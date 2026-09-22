# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import carb.settings
import omni.kit.app
import omni.kit.ui
import omni.ui as ui
from omni.kit.viewport.menubar.core import SelectableMenuItem
from omni.kit.viewport.menubar.core.model.category_model import CategoryCustomItem, CategoryStateItem
import omni.kit.commands
import omni.kit.viewport.menubar.display


SETTING_DISPLAY_RETARGET_AXES = "/persistent/exts/omni.anim.retarget.ui/displayRetargetAxes"


class RetargetViewportMenu:
    MENU_NAME = "Animation"
    CATEGORY = "Show By Type"

    def __init__(self):
        self._display_instance = omni.kit.viewport.menubar.display.get_instance()
        self._settings = carb.settings.acquire_settings_interface()
        self._subscriptions = {}
        self._viewport_menu = CategoryCustomItem(RetargetViewportMenu.MENU_NAME, lambda: self._build_menu())
        self._display_instance.register_custom_category_item(RetargetViewportMenu.CATEGORY, self._viewport_menu)

    def destroy(self):  # pragma: no cover
        if self._display_instance:
            try:
                self._display_instance.deregister_custom_category_item(
                    RetargetViewportMenu.CATEGORY,
                    self._viewport_menu
                )
            except Exception:
                # TODO: This fails the repo test
                # AttributeError: 'DisplayMenuContainer' object has no attribute '_category_models''
                pass
        for setting_path in self._subscriptions:
            if self._settings:
                self._settings.unsubscribe_to_change_events(self._subscriptions[setting_path])
        self._display_instance = None
        self._viewport_menu = None
        self._subscriptions = {}

    def _build_menu(self):
        retarget_axes_item = self._create_menu_simple_bool_item("Retarget Axes", SETTING_DISPLAY_RETARGET_AXES)
        self._subscribe_to_setting_change(None, [retarget_axes_item], SETTING_DISPLAY_RETARGET_AXES)

    def _create_menu_simple_bool_item(self, text, setting) -> CategoryStateItem:
        # also set default value with whatever we have in the settings
        new_item = SelectableMenuItem(text, ui.SimpleBoolModel(self._settings.get_as_bool(setting)))
        new_item.model.add_value_changed_fn(
            lambda model, item=new_item: self._settings.set(setting, model.get_value_as_bool())
        )
        return new_item

    def _subscribe_to_setting_change(self, sub, items, setting):
        if sub is not None:
            self._settings.unsubscribe_to_change_events(sub)
            if len(items) == 1:
                value = self._settings.get_as_bool(setting)
                items[0].model.set_value(value)
            else:
                items[self._settings.get_as_int(setting)].model.set_value(True)
        sub = self._settings.subscribe_to_node_change_events(
            setting,
            lambda item,
            event_type: self._subscribe_to_setting_change(sub, items, setting)
        )
