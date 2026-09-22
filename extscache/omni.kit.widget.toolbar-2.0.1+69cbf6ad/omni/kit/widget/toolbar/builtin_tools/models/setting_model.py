# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["BoolSettingModel"]

import omni.ui as ui
import carb
import carb.dictionary
import carb.settings


class BoolSettingModel(ui.AbstractValueModel):
    """The value model that is reimplemented in Python to watch a bool setting path"""

    def __init__(self, setting_path, inverted: bool=False):
        super().__init__()

        self._setting_path = setting_path
        self._inverted = inverted
        self._settings = carb.settings.get_settings()
        self._dict = carb.dictionary.get_dictionary()
        self._subscription = self._settings.subscribe_to_node_change_events(self._setting_path, self._on_change)
        self._value = self._settings.get(self._setting_path)
        if self._inverted:
            self._value = not self._value

    def clean(self):
        self._settings.unsubscribe_to_change_events(self._subscription)

    def _on_change(self, item, event_type):
        self._value = self._dict.get(item)
        if self._inverted:
            self._value = not self._value
        self._value_changed()

    def get_value_as_bool(self):
        return self._value

    def set_value(self, value):
        """Reimplemented set bool"""
        if self._inverted:
            value = not value
        self._settings.set(self._setting_path, value)


class FloatSettingModel(ui.AbstractValueModel):
    """The value model that is reimplemented in Python to watch a float setting path"""

    def __init__(self, setting_path):
        super().__init__()

        self._setting_path = setting_path
        self._settings = carb.settings.get_settings()
        self._dict = carb.dictionary.get_dictionary()
        self._subscription = self._settings.subscribe_to_node_change_events(self._setting_path, self._on_change)
        self._value = self._settings.get(self._setting_path)

    def clean(self):
        self._settings.unsubscribe_to_change_events(self._subscription)

    def _on_change(self, item, event_type):
        self._value = self._dict.get(item)
        self._value_changed()

    def get_value_as_float(self):
        return self._value

    def set_value(self, value):
        """Reimplemented set float"""
        self._settings.set(self._setting_path, value)
