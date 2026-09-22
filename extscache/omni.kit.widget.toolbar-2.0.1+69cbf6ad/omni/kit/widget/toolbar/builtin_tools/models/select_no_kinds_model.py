# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["SelectNoKindsModel"]

import omni.ui as ui
import carb
import carb.dictionary
import carb.settings


class SelectNoKindsModel(ui.AbstractValueModel):
    """The value model that is reimplemented in Python to watch the prim select mode"""

    PICKING_MODE_NO_KINDS_SETTING = "/persistent/app/viewport/pickingModeNoKinds"

    # new default
    PICKING_MODE_NO_KINDS_DEFAULT = True


    def __init__(self):
        super().__init__()

        self._settings = carb.settings.get_settings()
        self._settings.set_default_bool(self.PICKING_MODE_NO_KINDS_SETTING, self.PICKING_MODE_NO_KINDS_DEFAULT)

        self._dict = carb.dictionary.get_dictionary()
        self._subscription = self._settings.subscribe_to_node_change_events(self.PICKING_MODE_NO_KINDS_SETTING, self._on_change)
        self.set_value(self._settings.get(self.PICKING_MODE_NO_KINDS_SETTING))

    def clean(self):
        self._settings.unsubscribe_to_change_events(self._subscription)

    def _on_change(self, item, event_type):
        self._mode = self._dict.get(item)
        self._value_changed()

    def get_value_as_bool(self):
        return self._mode

    def set_value(self, value):
        self._mode = value
        self._settings.set(self.PICKING_MODE_NO_KINDS_SETTING, self._mode)
