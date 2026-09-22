# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["BuiltinTools"]

import carb.dictionary
import carb.settings

from .select_button_group import SelectButtonGroup
from .snap_button_group import LegacySnapButtonGroup
from .transform_button_group import TransformButtonGroup
from .play_button_group import PlayButtonGroup
import typing
if typing.TYPE_CHECKING:
    from ..toolbar import Toolbar

SELECT_BUTTON_ENABLED_SETTING_PATH = "/exts/omni.kit.widget.toolbar/SelectionButton/enabled"
TRANSFORM_BUTTON_ENABLED_SETTING_PATH = "/exts/omni.kit.widget.toolbar/TransformButton/enabled"
PLAY_BUTTON_ENABLED_SETTING_PATH = "/exts/omni.kit.widget.toolbar/PlayButton/enabled"
LEGACY_SNAP_BUTTON_ENABLED_SETTING_PATH_WINDOW = "/exts/omni.kit.window.toolbar/legacySnapButton/enabled"
LEGACY_SNAP_BUTTON_ENABLED_SETTING_PATH_WIDGET = "/exts/omni.kit.widget.toolbar/legacySnapButton/enabled"


class BuiltinTools:
    def __init__(self, toolbar: "Toolbar"):
        self._dict = carb.dictionary.get_dictionary()
        self._settings = carb.settings.get_settings()

        self._sub_window = self._settings.subscribe_to_node_change_events(
            LEGACY_SNAP_BUTTON_ENABLED_SETTING_PATH_WINDOW, self._on_legacy_snap_setting_changed_window
        )

        self._toolbar = toolbar
        self._select_button_group = None
        if self._settings.get(SELECT_BUTTON_ENABLED_SETTING_PATH):
            self._select_button_group = SelectButtonGroup()
            toolbar.add_widget(self._select_button_group, 0)

        self._transform_button_group = None
        if self._settings.get(TRANSFORM_BUTTON_ENABLED_SETTING_PATH):
            self._transform_button_group = TransformButtonGroup()
            toolbar.add_widget(self._transform_button_group, 1)

        self._snap_button_group = None
        if self._settings.get(LEGACY_SNAP_BUTTON_ENABLED_SETTING_PATH_WIDGET):
            self._add_snap_button()

        self._play_button_group = None
        if self._settings.get(PLAY_BUTTON_ENABLED_SETTING_PATH):
            self._play_button_group = PlayButtonGroup()
            toolbar.add_widget(self._play_button_group, 21)

        self._sub_widget = self._settings.subscribe_to_node_change_events(
            LEGACY_SNAP_BUTTON_ENABLED_SETTING_PATH_WIDGET, self._on_legacy_snap_setting_changed
        )

    def destroy(self):
        if self._select_button_group:
            self._toolbar.remove_widget(self._select_button_group)
            self._select_button_group.clean()
            self._select_button_group = None

        if self._transform_button_group:
            self._toolbar.remove_widget(self._transform_button_group)
            self._transform_button_group.clean()
            self._transform_button_group = None

        if self._snap_button_group:
            self._remove_snap_button()

        if self._play_button_group:
            self._toolbar.remove_widget(self._play_button_group)
            self._play_button_group.clean()
            self._play_button_group = None

        if self._sub_window:
            self._settings.unsubscribe_to_change_events(self._sub_window)
            self._sub_window = None

        if self._sub_widget:
            self._settings.unsubscribe_to_change_events(self._sub_widget)
            self._sub_widget = None

    def __del__(self):
        self.destroy()

    def _add_snap_button(self):
        self._snap_button_group = LegacySnapButtonGroup()
        self._toolbar.add_widget(self._snap_button_group, 11)

    def _remove_snap_button(self):
        self._toolbar.remove_widget(self._snap_button_group)
        self._snap_button_group.clean()
        self._snap_button_group = None

    def _on_legacy_snap_setting_changed_window(self, *args, **kwargs):
        """
        If the old setting is set, we forward it into the new settings.
        """
        enabled_legacy_snap = self._settings.get(LEGACY_SNAP_BUTTON_ENABLED_SETTING_PATH_WINDOW)
        if enabled_legacy_snap is not None:
            carb.log_warn(
                'Deprecated, please use "/exts/omni.kit.widget.toolbar/legacySnapButton/enabled" setting'
            )
            self._settings.set(LEGACY_SNAP_BUTTON_ENABLED_SETTING_PATH_WIDGET, enabled_legacy_snap)

    def _on_legacy_snap_setting_changed(self, *args, **kwargs):
        enabled_legacy_snap = self._settings.get(LEGACY_SNAP_BUTTON_ENABLED_SETTING_PATH_WIDGET)
        if self._snap_button_group is None and enabled_legacy_snap:
            self._add_snap_button()
        elif self._snap_button_group is not None and not enabled_legacy_snap:
            self._remove_snap_button()

    def add_custom_select_type(self, entry_name: str, selection_types: list):
        self._select_button_group.add_custom_select_type(entry_name, selection_types)

    def remove_custom_select(self, entry_name):
        self._select_button_group.remove_custom_select(entry_name)

    def add_custom_move_type(self, entry_name: str, move_type: str):
        self._transform_button_group.add_custom_move_type(entry_name, move_type)

    def remove_custom_move(self, entry_name: str):
        self._transform_button_group.remove_custom_move_type(entry_name)
