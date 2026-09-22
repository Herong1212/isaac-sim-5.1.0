# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from . import style, utils
from .settings import NavMeshSettings

import carb.input
import omni.kit.undo
import omni.ui as ui
import omni.usd
from omni.kit.widget.settings.settings_model import SettingModel
import omni.kit.notification_manager as nm

from pxr import Usd
import NavSchema

import copy
from typing import List

EXT_PATH = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
ICON_PATH = f"{EXT_PATH}/icons"


class NavMeshPrimPathListWidget(ui.AbstractItemModel):
    """Class that builds the NavMeshPrimPastList UI and encapsulates the tree view and model."""

    selection_change_in_progress = False

    class Item(ui.AbstractItem):
        """Class that represents a NavMeshPrimPath item in the tree view model."""

        def __init__(self):
            super().__init__()
            self.model = ui.SimpleStringModel()

    class ItemModel(ui.AbstractItemModel):
        """Class that contains a list of NavMeshPrimPath items for use with a tree view."""

        def __init__(self):
            super().__init__()
            self._items = []

        def get_item_children(self, item: ui.AbstractItem):
            """
            Returns the of children for a given item.

            @param item: The item for which to get the children.
            """
            if item is not None:
                return []
            return self._items

        def get_item_value_model(self, item: ui.AbstractItem, *_):
            """
            Returns the model for a given item.

            @param item: The item for which to get the model.
            """
            if item and isinstance(item, NavMeshPrimPathListWidget.Item):
                return item.model
            return None

        def get_item_value_model_count(self, *_):
            """Returns the number of columns in this model."""
            return 1

        def get_items(self, prim_paths: List[str]):
            """
            Given a list of prim paths, return a list of associated item models.

            @param prim_paths: The list of prim paths that should be used to get the items.
            """
            selected_items = []
            for item in self._items:
                if item.model.get_value_as_string() in prim_paths:
                    selected_items.append(item)
            return selected_items

        def get_prim_paths(self):
            """Returns a list of prim paths (one for each item)."""
            prim_paths = []
            for item in self._items:
                prim_paths.append(item.model.get_value_as_string())
            return prim_paths

        def set_prim_paths(self, prim_paths: List[str]):
            """
            Sets the prim paths for this model.  This will update the internal list of items accordingly.

            @param prim_paths: The list of prim paths.
            """
            do_update = False
            prim_path_count = len(prim_paths)
            sorted_prim_paths = copy.deepcopy(prim_paths)
            sorted_prim_paths.sort()
            while len(self._items) < prim_path_count:
                do_update = True
                self._items.append(NavMeshPrimPathListWidget.Item())
            while len(self._items) > prim_path_count:
                do_update = True
                self._items.pop()
            for prim_path_index in range(prim_path_count):
                item = self._items[prim_path_index]
                prim_path = sorted_prim_paths[prim_path_index]
                if item.model.get_value_as_string() != prim_path:
                    do_update = True
                    item.model.set_value(prim_path)
            if do_update:
                self._item_changed(None)

    def __init__(self):
        super().__init__()
        self._model = NavMeshPrimPathListWidget.ItemModel()
        self._usd_context = omni.usd.get_context()
        self._view = ui.TreeView(self._model, header_visible=False, root_visible=False)

    def __del__(self):
        self.destroy()

    def destroy(self):
        """Cleans up the data for the class."""

    def get_prim_paths(self):
        """This returns the list of prim paths shown in this widget."""
        return self._model.get_prim_paths()

    def get_selected_prim_paths(self):
        """This returns the list of prim paths in this widget that are in the selection."""
        prim_paths = self.get_prim_paths()
        selected_prim_paths = []
        for selected_item in self._view.selection:
            prim_path = selected_item.model.get_value_as_string()
            if prim_path in prim_paths:
                selected_prim_paths.append(prim_path)
        return selected_prim_paths

    def set_prim_paths(self, prim_paths: List[str]):
        """This sets the list of prim paths in this widget and refreshes the selection to make sure the state is valid."""
        self._model.set_prim_paths(prim_paths)


class NavMeshGeometryWidget:
    """
    This class builds the UI for the NavMeshExclusionsWidget.  It consists of two NavMeshPrimPathListWidgets (one
    for the included prim paths, one for the excluded prim paths) along with a few buttons for setting the
    exclusion state.  There is also a checkbox used to enable/disable rigid body prims being included in the
    NavMesh calculation.
    """
    RECURSIVELY_MODIFY_PRIMS = True
    SPACING = 8
    SCROLLBAR_WIDTH = 12

    def __init__(self):
        self._stage = omni.usd.get_context().get_stage()
        self._auto_exclude_physics_rigid_bodies = False
        self._exclusion_widget = None
        self._stage_event_sub = (
            omni.usd.get_context()
            .get_stage_event_stream()
            .create_subscription_to_pop(self._on_stage_event, name="NavMesh Exclusions Event")
        )

        with ui.ZStack(style=style.get_exclusions_window_style()):
            ui.Rectangle()
            with ui.VStack(style=style.get_exclusions_window_style()):
                ui.Spacer(height=5)
                with ui.HStack(height=0):
                    with ui.HStack(spacing=0):
                        with ui.VStack():
                            ui.Spacer()
                            with ui.HStack(spacing=0, alignment=ui.Alignment.RIGHT_CENTER):
                                ui.Spacer(width=10)
                                ui.CheckBox(model=SettingModel(NavMeshSettings.EXCLUDE_RIGID_BODIES_PATH), width=0)
                                ui.Spacer(width=NavMeshGeometryWidget.SPACING)
                                ui.Label("Auto-Exclude Rigid Bodies")
                            ui.Spacer(height=10)
                            with ui.HStack(spacing=0, alignment=ui.Alignment.RIGHT_CENTER):
                                ui.Spacer(width=5)
                                ui.Label("Excluded Geometry", width=100)
                                ui.Spacer(width=3)
                                ui.Button(
                                    "",
                                    clicked_fn=self._on_refresh_exclusion_list_clicked,
                                    identifier="refresh_exclusion_list",
                                    tooltip="Refresh the navmesh exclusion list based on the current stage.",
                                    width=60,
                                    height=14,
                                    image_url="resources/glyphs/menu_refresh.svg",
                                    image_width=14,
                                    image_height=14,
                                    style={"stack_direction": ui.Direction.LEFT_TO_RIGHT}
                                )
                                ui.Spacer(width=10)
                                ui.Label("Stage Selection:", width=50)
                                ui.Button(
                                    " Exclude",
                                    clicked_fn=self._on_exclude_stage_selection_clicked,
                                    identifier="exclude_stage_selection",
                                    tooltip="Remove the selected objects in the stage from the navmesh excluded geometry.",
                                    width=60,
                                    image_url="resources/glyphs/menu_plus.svg",
                                    image_width=14,
                                    image_height=14,
                                    style={"stack_direction": ui.Direction.LEFT_TO_RIGHT}
                                )
                                ui.Button(
                                    " Include",
                                    clicked_fn=self._on_include_stage_selection_clicked,
                                    identifier="include_stage_selection",
                                    tooltip="Includes back the selected objects in the stage from the navmesh excluded geometry.",
                                    width=60,
                                    image_url="resources/glyphs/menu_minus.svg",
                                    image_width=14,
                                    image_height=14,
                                    style={"stack_direction": ui.Direction.LEFT_TO_RIGHT}
                                )
                                ui.Spacer(width=0)
                                ui.Button(
                                    " Remove Selected",
                                    clicked_fn=self._on_remove_selected_clicked,
                                    identifier="remove_selected",
                                    tooltip="Remove the selected items from the navmesh excluded geometry list.",
                                    width=60,
                                    image_url=f"{ICON_PATH}/remove.svg",
                                    image_width=14,
                                    image_height=14,
                                    style={"stack_direction": ui.Direction.LEFT_TO_RIGHT}
                                )
                            ui.Spacer(height=4)
                            ui.Line()
                            ui.Spacer(height=4)
                with ui.ZStack(height=235):
                    with ui.VStack():
                        with ui.ScrollingFrame(
                            horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                            vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
                        ):
                            self._exclusion_widget = NavMeshPrimPathListWidget()
                        ui.Spacer(height=NavMeshGeometryWidget.SPACING)

    def _apply_or_remove_exclude_api(self, prim_paths: List[str], apply: bool):
        """
        This is a helper function that will either call ApplyAPI or RemoveAPI on each prim path, depending on if apply
        is set to true.

        @param prim_paths: The list of prim paths that should ahve the NavMeshExcludeAPI changed.
        @param apply: If true, apply NavMeshExcludeAPI; otherwise remove it.
        """
        modified = []
        if self._stage and len(prim_paths):
            with omni.kit.undo.group():
                for prim_path in prim_paths:
                    prim = self._stage.GetPrimAtPath(prim_path)
                    if apply and not prim.HasAPI(NavSchema.NavMeshExcludeAPI):
                        omni.kit.commands.execute(
                            "ApplyNavMeshAPICommand", prim_path=prim_path, api=NavSchema.NavMeshExcludeAPI
                        )
                        modified.append(prim_path)
                    elif not apply and prim.HasAPI(NavSchema.NavMeshExcludeAPI) and not str(prim_path).startswith("/__omni_nav_mesh_viz_1F21D921"):
                        omni.kit.commands.execute(
                            "RemoveNavMeshAPICommand", prim_path=prim_path, api=NavSchema.NavMeshExcludeAPI
                        )
                        modified.append(prim_path)
        return modified

    def _get_navmesh_supported_prim_paths_recursive(self, prim_paths_to_modify: List[str], prim: Usd.Prim):
        """
        This internal function checks if a prim is supported for navmesh and adds it to prim_paths_to_modify.  Then,
        it (recursively) processes all the prim's children.

        @param prim_paths_to_modify: This is the output list that will contain all the navmesh supported prim paths.
        @param prim: The prim to check for navmesh support (along with all its children, recursively)
        """
        if prim:
            if prim.IsInstance() and (prim.HasAuthoredPayloads() or prim.HasAuthoredReferences()):
                prim_paths_to_modify.append(prim.GetPath().pathString)
            if utils.is_supported_navmesh_prim(prim):
                prim_paths_to_modify.append(prim.GetPath().pathString)
            if NavMeshGeometryWidget.RECURSIVELY_MODIFY_PRIMS:
                for child_prim in prim.GetChildren():
                    self._get_navmesh_supported_prim_paths_recursive(prim_paths_to_modify, child_prim)

    def _get_selected_navmesh_supported_prim_paths(self):
        """This internal function returns the list of prim paths to modify when include/exclude is clicked."""
        prim_paths_to_modify = []
        if self._stage:
            selected_prim_paths = omni.usd.get_context().get_selection().get_selected_prim_paths()
            for prim_path in selected_prim_paths:
                prim = self._stage.GetPrimAtPath(prim_path)
                if prim.IsInstanceProxy():
                    nm.post_notification("Do not select instance proxies to exclude NavMesh.", status=nm.NotificationStatus.WARNING)
                else:
                    prim_paths_to_modify.append(prim.GetPath().pathString)
        return prim_paths_to_modify

    def _on_exclude_stage_selection_clicked(self):
        """This internal function will be called when the Add Stage Selection button is clicked."""
        prim_paths = self._exclusion_widget.get_prim_paths()
        applied = self._apply_or_remove_exclude_api(self._get_selected_navmesh_supported_prim_paths(), True)
        prim_paths.extend(applied)
        unique_paths = set(prim_paths)
        self._exclusion_widget.set_prim_paths(list(unique_paths))

    def _on_include_stage_selection_clicked(self):
        """This internal function will be called when the Remove Stage Selection button is clicked."""
        prim_paths = self._exclusion_widget.get_prim_paths()
        applied = self._apply_or_remove_exclude_api(self._get_selected_navmesh_supported_prim_paths(), False)
        prim_paths = set(prim_paths) - set(applied)
        self._exclusion_widget.set_prim_paths(list(prim_paths))

    def _on_remove_selected_clicked(self):
        """This internal function will be called when the Remove Selected button is clicked."""
        selected = self._exclusion_widget.get_selected_prim_paths()
        self._apply_or_remove_exclude_api(selected, False)
        self._exclusion_widget.set_prim_paths(
            list(set(self._exclusion_widget.get_prim_paths()) - set(selected)))

    def _on_refresh_exclusion_list_clicked(self):
        """This internal function will be called when the Refresh Exclusion List button is clicked."""
        self._refresh_exclusion_list()

    def _refresh_exclusion_list(self):
        """This internal function traverses the entire stage and updates the exclusion list widget accordingly."""
        def get_prim_paths_with_api(stage, api):
            prim_paths = []
            for prim in stage.TraverseAll():
                if prim.HasAPI(api):
                    prim_path = str(prim.GetPath())
                    if not str(prim_path).startswith("/__omni_nav_mesh_viz_1F21D921"):
                        prim_paths.append(prim_path)
            return prim_paths
        if self._stage is not None:
            self._exclusion_widget.set_prim_paths(
                get_prim_paths_with_api(self._stage, NavSchema.NavMeshExcludeAPI))
        else:
            self._exclusion_widget.set_prim_paths([])

    def add_to_exclusion_list(self, add_prim_paths: List[str]):
        prim_paths = self._exclusion_widget.get_prim_paths()
        prim_paths.extend(add_prim_paths)
        unique_paths = set(prim_paths)
        self._exclusion_widget.set_prim_paths(list(unique_paths))

    def remove_from_exclusion_list(self, remove_prim_paths: List[str]):
        prim_paths = self._exclusion_widget.get_prim_paths()
        prim_paths = set(prim_paths) - set(remove_prim_paths)
        self._exclusion_widget.set_prim_paths(list(prim_paths))

    def _on_stage_event(self, event: carb.events.IEvent):
        """
        This internal callback is called when a stage event happens.  If the stage is closed, clear the internal
        stage variable.  If the stage is opened, set it.  In all events, refresh the list of included an excluded paths
        in case a new stage was added/remove.

        @param: event: The stage event that occurred.
        """
        if event.type == int(omni.usd.StageEventType.CLOSING):
            self._stage = None
            self._refresh_exclusion_list()

        elif event.type == int(omni.usd.StageEventType.OPENED):
            self._stage = omni.usd.get_context().get_stage()
            self._refresh_exclusion_list()

    def destroy(self):
        """Cleans up the data for the class."""
        self._auto_exclude_physics_rigid_bodies = False
        self._exclusion_widget = None
        self._stage = None
