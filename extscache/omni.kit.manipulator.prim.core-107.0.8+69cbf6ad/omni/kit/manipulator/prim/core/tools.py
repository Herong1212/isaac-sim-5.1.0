# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""This module provides classes for creating and managing toolbar buttons and tools for primitive manipulation in the Omniverse Kit."""

__all__ = [
    "SelectionPivotTool",
    "LocalGlobalTool",
    "PrimManipTools",
]

import traceback
from pathlib import Path
from typing import List

import carb
import carb.dictionary
import carb.settings
import omni.kit.app
import omni.kit.context_menu
import omni.usd
from carb.eventdispatcher import get_eventdispatcher
from omni.kit.manipulator.tool.snap import SnapToolButton
from omni.kit.manipulator.transform import Operation, SimpleToolButton, TransformManipulator

from .settings_constants import Constants as prim_c
from .tool_models import LocalGlobalModeModel
from .toolbar_registry import get_toolbar_registry

TOOLS_ENABLED_SETTING_PATH = "/exts/omni.kit.manipulator.prim.core/tools/enabled"


class SelectionPivotTool(SimpleToolButton):
    """A class for a toolbar button that provides selection pivot placement functionality.

    This class extends SimpleToolButton and acts as a button in the user interface which, when clicked, allows users to change the pivot placement of selected primitives in the scene. It also listens to selection changes to update its visibility state and registers its menu entries upon initialization.

    Args:
        args: A variable-length argument list.

    Keyword Args:
        usd_context_name (str): The name of the USD context to be used. Defaults to an empty string if not provided.

    Note:
        This class assumes the context is "" for VP1 and manages its own menu items for pivot placement settings."""

    # menu entry only needs to register once
    __menu_entries = []

    @classmethod
    def register_menu(cls):
        """Registers the pivot tool's menu in the application.

        Args:
            cls (type): The class object representing the SelectionPivotTool.
        """

        def build_placement_setting_entry(setting: str):
            menu = {
                "name": setting,
                "checked_fn": lambda _: carb.settings.get_settings().get(prim_c.MANIPULATOR_PLACEMENT_SETTING)
                == setting,
                "onclick_fn": lambda _: carb.settings.get_settings().set(prim_c.MANIPULATOR_PLACEMENT_SETTING, setting),
            }
            return menu

        menu = [
            build_placement_setting_entry(s)
            for s in [
                prim_c.MANIPULATOR_PLACEMENT_LAST_PRIM_PIVOT,
                prim_c.MANIPULATOR_PLACEMENT_BBOX_BASE,
                prim_c.MANIPULATOR_PLACEMENT_BBOX_CENTER,
                prim_c.MANIPULATOR_PLACEMENT_SELECTION_CENTER,
                prim_c.MANIPULATOR_PLACEMENT_PICK_REF_PRIM,
            ]
        ]

        for item in menu:
            cls.__menu_entries.append(omni.kit.context_menu.add_menu(item, "sel_pivot", "omni.kit.manipulator.prim"))

    @classmethod
    def unregister_menu(cls):
        """Unregisters the pivot tool's menu from the application.

        Args:
            cls (type): The class object representing the SelectionPivotTool.
        """
        for sub in cls.__menu_entries:
            sub.release()
        cls.__menu_entries.clear()

    def __init__(self, *args, **kwargs):
        """Initializes a new instance of the SelectionPivotTool."""
        super().__init__(*args, **kwargs)

        # TODO assume the context is "" for VP1
        self._usd_context = omni.usd.get_context(self._toolbar_payload.get("usd_context_name", ""))
        self._selection = self._usd_context.get_selection()
        icon_folder_path = Path(
            f"{omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)}/data/icons"
        )
        enabled_img_url = f"{icon_folder_path}/pivot_location.svg"

        self._build_widget(
            button_name="sel_pivot",
            enabled_img_url=enabled_img_url,
            model=None,
            menu_index="sel_pivot",
            menu_extension_id="omni.kit.manipulator.prim",
            no_toggle=True,
            menu_on_left_click=True,
            tooltip="Selection Pivot Placement",
        )

        # order=1 to register after prim manipulator so _on_selection_changed gets updated len of xformable_prim_paths
        self._stage_event_sub = get_eventdispatcher().observe_event(
            observer_name="omni.kit.manipulator.prim.core:tools",
            event_name=self._usd_context.stage_event_name(omni.usd.StageEventType.SELECTION_CHANGED),
            order=1,
            on_event=lambda _: self._on_selection_changed(),
        )

        if self._usd_context.get_stage_state() == omni.usd.StageState.OPENED:
            self._on_selection_changed()

    def destroy(self):
        """Cleans up resources used by the tool, like event subscriptions."""
        super().destroy()
        self._stage_event_sub = None
        if self._model:
            self._model.destroy()
            self._model = None

    @classmethod
    def can_build(cls, manipulator: TransformManipulator, operation: Operation) -> bool:
        """Determines if the pivot tool can be built for the given manipulator and operation.

        Args:
            cls (type): The class object representing the SelectionPivotTool.
            manipulator (:obj:`TransformManipulator`): The manipulator for which the tool is being considered.
            operation (:obj:`Operation`): The operation type to check compatibility.

        Returns:
            bool: True if the tool can be built, False otherwise.
        """
        return operation == Operation.TRANSLATE or operation == Operation.ROTATE or operation == Operation.SCALE

    def _on_selection_changed(self):
        selected_xformable_paths_count = (
            len(self._manipulator.model.xformable_prim_paths) if self._manipulator.model else 0
        )

        if self._stack:
            visible = selected_xformable_paths_count > 0
            if self._stack.visible != visible:
                self._stack.visible = visible
                self._manipulator.refresh_toolbar()


class LocalGlobalTool(SimpleToolButton):
    """A toolbar button class for toggling between local and global transform spaces.

    This class is responsible for creating a toggle button in the UI that allows users to switch between local and global transform modes while performing translate or rotate operations. The button updates its appearance based on the current mode and provides tooltips to indicate the active transform space.

    Args:
        args: Variable length argument list.

    Keyword Args:
        operation (Operation): The type of operation (translate or rotate) the tool is used for.
        toolbar_payload (dict, optional): A dictionary containing additional parameters for toolbar customization.
    """

    def __init__(self, *args, **kwargs):
        """Initializes the LocalGlobalTool."""
        super().__init__(*args, **kwargs)

        if self._operation == Operation.TRANSLATE:
            setting_path = "/app/transform/moveMode"
        elif self._operation == Operation.ROTATE:
            setting_path = "/app/transform/rotateMode"
        else:
            raise RuntimeError("Invalid operation")

        self._model = LocalGlobalModeModel(setting_path)
        icon_folder_path = Path(
            f"{omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)}/data/icons"
        )
        enabled_img_url = f"{icon_folder_path}/transformspace_global_dark.svg"
        disabled_img_url = f"{icon_folder_path}/transformspace_local_dark.svg"

        self._build_widget(
            button_name="local_global",
            enabled_img_url=enabled_img_url,
            disabled_img_url=disabled_img_url,
            model=self._model,
            tooltip="Current Transform Space: World",
            disabled_tooltip="Current Transform Space: Local",
        )

    def destroy(self):
        """Cleans up the resources held by the tool. This should be called before deleting the tool."""
        super().destroy()
        if self._model:
            self._model.destroy()
            self._model = None

    @classmethod
    def can_build(cls, manipulator: TransformManipulator, operation: Operation) -> bool:
        """Determines if the tool can be built with the given manipulator and operation.

        Args:
            manipulator (:obj:`TransformManipulator`): The manipulator that will use the tool.
            operation (:obj:`Operation`): The operation for which the tool is being considered.

        Returns:
            bool: True if the tool can be built, False otherwise."""
        return operation == Operation.TRANSLATE or operation == Operation.ROTATE


class PrimManipTools:
    """A class responsible for managing the registration and lifecycle of primitive manipulation tools.

    The PrimManipTools class is responsible for handling the registration, enabling, disabling, and destruction of various primitive manipulation tools within an application. It includes tools such as LocalGlobalTool for toggling between local and global transform spaces, SnapToolButton for enabling snapping functionality, and SelectionPivotTool for defining selection pivot placement. This class also manages settings subscriptions for tool state changes and properly cleans up during destruction.
    """

    def __init__(self):
        """Initialize the PrimManipTools with default settings and register the necessary tools."""
        self._settings = carb.settings.get_settings()
        self._dict = carb.dictionary.get_dictionary()
        self._toolbar_reg = get_toolbar_registry()

        SelectionPivotTool.register_menu()  # one time startup
        self._builtin_tool_classes = {
            "prim:1space": LocalGlobalTool,
            "prim:2snap": SnapToolButton,
            "prim:3sel_pivot": SelectionPivotTool,
        }
        self._registered_tool_ids: List[str] = []

        self._sub = self._settings.subscribe_to_node_change_events(TOOLS_ENABLED_SETTING_PATH, self._on_setting_changed)
        if self._settings.get(TOOLS_ENABLED_SETTING_PATH) is True:
            self._register_tools()

        self._pivot_button_group = None

        # register pivot placement to "factory explorer" toolbar
        app_name = omni.kit.app.get_app().get_app_filename()
        if "omni.factory_explorer" in app_name:
            # add manu entry to factory explorer toolbar
            manager = omni.kit.app.get_app().get_extension_manager()
            self._hooks = manager.subscribe_to_extension_enable(
                lambda _: self._register_main_toolbar_button(),
                lambda _: self._unregister_main_toolbar_button(),
                ext_name="omni.explore.toolbar",
                hook_name="omni.kit.manipulator.prim.pivot_placement listener",
            )

    def __del__(self):
        self.destroy()

    def destroy(self):
        """Cleans up the resources and unregisters tools upon destruction of the PrimManipTools instance."""
        self._hooks = None
        if self._pivot_button_group is not None:
            self._unregister_main_toolbar_button()

        self._unregister_tools()
        if self._sub is not None:
            self._settings.unsubscribe_to_change_events(self._sub)
            self._sub = None

        SelectionPivotTool.unregister_menu()  # one time shutdown

    def _register_tools(self):
        for id, tool_class in self._builtin_tool_classes.items():
            self._toolbar_reg.register_tool(tool_class, id)
            self._registered_tool_ids.append(id)

    def _unregister_tools(self):
        for id in self._registered_tool_ids:
            self._toolbar_reg.unregister_tool(id)

        self._registered_tool_ids.clear()

    def _on_setting_changed(self, item, event_type):
        enabled = self._dict.get(item)
        if enabled and not self._registered_tool_ids:
            self._register_tools()
        elif not enabled:
            self._unregister_tools()

    def _register_main_toolbar_button(self):
        try:
            if not self._pivot_button_group:
                import omni.explore.toolbar

                from .pivot_button_group import PivotButtonGroup

                self._pivot_button_group = PivotButtonGroup()

                explorer_toolbar_ext = omni.explore.toolbar.get_toolbar_instance()
                explorer_toolbar_ext.toolbar.add_widget_group(self._pivot_button_group, 1)

                # also add to MODIFY_TOOLS list, when menu Modify is selected
                # all items in toolbar will be cleared and re-added from MODIFY_TOOLS list
                explorer_tools = omni.explore.toolbar.groups.MODIFY_TOOLS
                explorer_tools.append(self._pivot_button_group)
        except Exception:
            carb.log_warn(traceback.format_exc())

    def _unregister_main_toolbar_button(self):
        try:
            if self._pivot_button_group:
                import omni.explore.toolbar

                explorer_toolbar_ext = omni.explore.toolbar.get_toolbar_instance()
                explorer_toolbar_ext.toolbar.remove_widget_group(self._pivot_button_group)

                # remove from MODIFY_TOOLS list as well
                explorer_tools = omni.explore.toolbar.groups.MODIFY_TOOLS
                if self._pivot_button_group in explorer_tools:
                    explorer_tools.remove(self._pivot_button_group)

                self._pivot_button_group.clean()
                self._pivot_button_group = None

        except Exception:
            carb.log_warn(traceback.format_exc())
