# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""
A menu to set datetime format.
"""
__all__ = ["DatetimeFormatMenu"]

import omni.ui as ui
import carb.settings
import omni.kit.app

from typing import Callable
from functools import partial


DATETIME_FORMAT_SETTING = "/persistent/app/datetime/format"
DATETIME_FORMATS = [
            "MM/DD/YYYY",
            "DD.MM.YYYY",
            "DD-MM-YYYY",
            "YYYY-MM-DD",
            "YYYY/MM/DD",
            "YYYY.MM.DD"
            ]


class DatetimeFormatMenu:
    """
    Menu to set datetime format.

    Args:
        value_changed_fn(Callable): function to call when datetime format changed. Function Signature:
            void value_changed_fn()
    """
    def __init__(
        self,
        value_changed_fn: Callable[[], None]=None,
    ):
        self._menu = ui.Menu()
        self._menu_items = {}
        self._value_changed_fn = value_changed_fn
        self._update_setting = omni.kit.app.SettingChangeSubscription(
            DATETIME_FORMAT_SETTING,
            self._on_datetime_format_changed,
        )
        with self._menu:
            self._build_dateformat_items()

    def _on_datetime_format_changed(self, item, event_type):
        if event_type == carb.settings.ChangeEventType.CHANGED:
            format = carb.settings.get_settings().get(DATETIME_FORMAT_SETTING)
            menu_item = self._menu_items.get(format, None)
            if menu_item:
                for item in self._menu_items.values():
                    item.checked = False
                menu_item.checked = True
                if self._value_changed_fn:
                    self._value_changed_fn()

    def _build_dateformat_items(self):

        def set_datetime_format(owner, format, menu_item):
            for item in owner._menu_items.values():
                if item != menu_item:
                    item.checked = False
            if menu_item.checked:
                if format != carb.settings.get_settings().get(DATETIME_FORMAT_SETTING):
                    carb.settings.get_settings().set(DATETIME_FORMAT_SETTING, format)

        for format in DATETIME_FORMATS:
            menu_item = ui.MenuItem(
                        format,
                        checkable=True,
                        checked=False,
                        direction=ui.Direction.RIGHT_TO_LEFT
                    )
            menu_item.set_triggered_fn(partial(set_datetime_format, self, format, menu_item))
            if format == carb.settings.get_settings().get(DATETIME_FORMAT_SETTING):
                menu_item.checked = True
            self._menu_items[format] = menu_item

    @property
    def visible(self):
        """ Return True if the menu is visible. """
        return self._menu.visible

    @visible.setter
    def visible(self, value: bool):
        """ Set visibility of the menu. """
        self._menu.visible = value

    def show_at(self, x: float, y: float):
        """ Show the menu at the given position. """
        self._menu.show_at(x, y)

    def destroy(self):
        """Destructor"""
        self._menu = None
        self._menu_items = None
        self._update_setting = None
        self._value_changed_fn = None

def get_datetime_format():
    """ Get datetime from settings. """
    format = carb.settings.get_settings().get(DATETIME_FORMAT_SETTING)
    if format not in DATETIME_FORMATS:
        # if not valid format, using current system format
        return "%x"
    return format.replace("MM", "%m").replace("DD", "%d").replace("YYYY", "%Y")
