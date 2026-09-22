# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["SelectModeModel"]

import omni.ui as ui
import carb
import carb.dictionary
import carb.settings


class SelectModeModel(ui.AbstractValueModel):
    """The value model that is reimplemented in Python to watch the prim select mode"""

    PICKING_MODE_SETTING = "/persistent/app/viewport/pickingMode"

    PICKING_MODE_MODELS = "kind:model.ALL"
    PICKING_MODE_PRIMS = "type:ALL"

    # new default
    PICKING_MODE_DEFAULT = PICKING_MODE_PRIMS


    def __init__(self):
        super().__init__()

        self._settings = carb.settings.get_settings()
        self._settings.set_default_string(self.PICKING_MODE_SETTING, self.PICKING_MODE_DEFAULT)

        self._dict = carb.dictionary.get_dictionary()
        self._subscription = self._settings.subscribe_to_node_change_events(self.PICKING_MODE_SETTING, self._on_change)
        self.set_value(self._settings.get(self.PICKING_MODE_SETTING))

    def clean(self):
        self._settings.unsubscribe_to_change_events(self._subscription)

    def _on_change(self, item, event_type):
        self._mode = self._dict.get(item)
        self._value_changed()

    def get_value_as_bool(self):
        return self._mode == self.PICKING_MODE_PRIMS

    def get_value_as_string(self):
        return self._mode

    def set_value(self, value):
        if isinstance(value, bool):
            if value:
                self._mode = self.PICKING_MODE_PRIMS
            else:
                self._mode = self.PICKING_MODE_MODELS
        else:
            self._mode = value
        self._settings.set(self.PICKING_MODE_SETTING, self._mode)
