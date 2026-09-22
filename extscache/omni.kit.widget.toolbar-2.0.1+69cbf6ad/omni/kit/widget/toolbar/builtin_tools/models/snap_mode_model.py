# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni.ui as ui
import carb
import carb.dictionary
import carb.settings


class SnapModeModel(ui.AbstractValueModel):
    """The value model that is reimplemented in Python to watch the prim select mode"""

    SNAP_MODE_SETTING = "/persistent/app/viewport/snapToSurface"
    SNAP_MODE_INCREMENT = "Snap to Increment"
    SNAP_MODE_FACE = "Snap to Face"

    def __init__(self):
        super().__init__()

        self._dict = carb.dictionary.get_dictionary()
        self._settings = carb.settings.get_settings()
        self._sub = self._settings.subscribe_to_node_change_events(self.SNAP_MODE_SETTING, self._on_snap_change)
        self._selected_mode = self._settings.get(self.SNAP_MODE_SETTING)

    def clean(self):
        self._settings.unsubscribe_to_change_events(self._sub)

    def _on_snap_change(self, item, event_type):
        self._selected_mode = self._dict.get(item)
        self._value_changed()

    def get_value_as_bool(self):
        return self._selected_mode
    
    def get_value_as_string(self):
        return self.SNAP_MODE_FACE if self._selected_mode else self.SNAP_MODE_INCREMENT

    def set_value(self, value):
        if isinstance(value, bool):
            self._settings.set(self.SNAP_MODE_SETTING, value)
        elif isinstance(value, str):
            if value in [self.SNAP_MODE_INCREMENT, self.SNAP_MODE_FACE]:
                self._settings.set(self.SNAP_MODE_SETTING, value==self.SNAP_MODE_FACE)
            else:
                carb.log_warn(f"Unknown value '{value}' for '{self.SNAP_MODE_SETTING}'")
        else:
            carb.log_warn(f"Unknown value type of '{value}' for '{self.SNAP_MODE_SETTING}'")
