# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["StageWindow"]

from .selection_watch import SelectionWatch
from .external_drag_drop_helper import setup_external_drag_drop, destroy_external_drag_drop
from .stage_settings import StageSettings
from omni.kit.widget.stage import StageWidget
from typing import List
from typing import Optional
from typing import Tuple
from pxr import Usd

import carb.eventdispatcher
import carb.settings
import omni.ui as ui
import omni.usd


class CustomizedStageWidget(StageWidget):

    @StageWidget.show_prim_display_name.setter
    def show_prim_display_name(self, value):
        StageWidget.show_prim_display_name.fset(self, value)
        StageSettings().show_prim_displayname = value

    @StageWidget.children_reorder_supported.setter
    def children_reorder_supported(self, value):
        StageWidget.children_reorder_supported.fset(self, value)
        StageSettings().should_keep_children_order = value

    @StageWidget.auto_reload_prims.setter
    def auto_reload_prims(self, value):
        StageWidget.auto_reload_prims.fset(self, value)
        StageSettings().auto_reload_prims = value

    @StageWidget.show_undefined_prims.setter
    def show_undefined_prims(self, value):
        StageWidget.show_undefined_prims.fset(self, value)
        StageSettings().show_undefined_prims = value

    @StageWidget.show_abstract_prims.setter
    def show_abstract_prims(self, value):
        StageWidget.show_abstract_prims.fset(self, value)
        StageSettings().show_abstract_prims = value

    @StageWidget.show_inactive_prims.setter
    def show_inactive_prims(self, value):
        StageWidget.show_inactive_prims.fset(self, value)
        StageSettings().show_inactive_prims = value

    def get_treeview(self):
        return self._tree_view

    def get_delegate(self):
        return self._delegate


class StageWindow(ui.Window):
    """The Stage window"""

    def __init__(self, usd_context_name: str = ""):
        self._usd_context = omni.usd.get_context(usd_context_name)
        self._visiblity_changed_listener = None
        self._selection = None

        super().__init__(
            "Stage",
            width=600,
            height=800,
            flags=ui.WINDOW_FLAGS_NO_SCROLLBAR,
            dockPreference=ui.DockPreference.RIGHT_TOP,
        )
        self.set_visibility_changed_fn(self._visibility_changed_fn)

        # Dock it to the same space where Layers is docked, make it the first tab and the active tab.
        self.deferred_dock_in("Layers", ui.DockPolicy.CURRENT_WINDOW_IS_ACTIVE)
        self.dock_order = 0

        # Get list of columns from settings
        self._settings = carb.settings.get_settings()
        self._columns_settings_path = "/persistent/exts/omni.kit.window.stage/columns"
        columns: Optional[str] = self._settings.get(self._columns_settings_path)
        if columns is None:
            # By default Visibility and Type are enabled columns
            self._columns = ["Visibility","Type"]
        else:
            self._columns = columns.split("|")

        with self.frame:
            self._stage_widget = CustomizedStageWidget(
                None, columns_enabled=self._columns,
                children_reorder_supported=StageSettings().should_keep_children_order,
                show_prim_display_name=StageSettings().show_prim_displayname,
                auto_reload_prims=StageSettings().auto_reload_prims,
                show_undefined_prims=StageSettings().show_undefined_prims,
                show_abstract_prims=StageSettings().show_abstract_prims,
                show_inactive_prims=StageSettings().show_inactive_prims,
            )

        # The Open/Close Stage logic
        self._stage_subscription = [
            carb.eventdispatcher.get_eventdispatcher().observe_event(
                observer_name="omni.kit.window.stage",
                event_name=self._usd_context.stage_event_name(event),
                on_event=func
            )
            for event, func in (
                (omni.usd.StageEventType.OPENED, lambda _: self._on_stage_opened()),
                (omni.usd.StageEventType.CLOSING, lambda _: self._on_stage_closing())
            )
        ]

        self._on_stage_opened()

        # The selection logic
        self._selection = SelectionWatch(usd_context=self._usd_context)
        self._stage_widget.set_selection_watch(self._selection)

        # Callback when columns are changed or toggled
        self._columns_changed_sub = self._stage_widget.subscribe_columns_changed(self._columns_changed)

    def _columns_changed(self, columns: List[Tuple[str, bool]]):
        """
        Called by StageWidget when columns are changed or toggled.
        """
        enabled_columns = [c[0] for c in columns if c[1]]
        self._settings.set_string(self._columns_settings_path, "|".join(enabled_columns))

    def _visibility_changed_fn(self, visible):
        if self._visiblity_changed_listener:
            self._visiblity_changed_listener(visible)

        if not visible:
            if self._selection:
                self._selection.destroy()
                self._selection = None
        else:
            self._selection = SelectionWatch(usd_context=self._usd_context)

        if self._stage_widget:
            self._stage_widget.set_selection_watch(self._selection)

    def set_visibility_changed_listener(self, listener):
        self._visiblity_changed_listener = listener

    def destroy(self):
        """
        Called by extension before destroying this object. It doesn't happen automatically.
        Without this hot reloading doesn't work.
        """
        self._visiblity_changed_listener = None
        if self._selection:
            self._selection._tree_view = None
            self._selection._events = None
            self._selection._stage_event_sub = None
            self._selection = None
        self._stage_widget.destroy()
        self._stage_widget = None
        self._stage_subscription = None
        self._settings = None
        self._columns_changed_sub = None
        super().destroy()
        destroy_external_drag_drop()

    def _on_stage_opened(self):
        """Called when opening a new stage"""
        stage = self._usd_context.get_stage()
        if not stage:
            return

        self._stage_widget.open_stage(stage)
        setup_external_drag_drop("Stage", self._stage_widget)

    def _on_stage_closing(self):
        """Called when close the stage"""
        self._stage_widget.open_stage(None)
        setup_external_drag_drop("Stage", self._stage_widget)

    def get_widget(self) -> CustomizedStageWidget:
        return self._stage_widget
