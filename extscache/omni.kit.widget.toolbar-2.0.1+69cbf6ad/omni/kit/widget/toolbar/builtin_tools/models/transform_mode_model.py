# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["TransformModeModel"]

import omni.ui as ui
import carb
import carb.dictionary
import carb.settings


class TransformModeModel(ui.AbstractValueModel):
    """The value model that is reimplemented in Python to watch the prim select mode"""

    TRANSFORM_OP_SETTING = "/app/transform/operation"
    TRANSFORM_OP_SELECT = "select"
    TRANSFORM_OP_MOVE = "move"
    TRANSFORM_OP_ROTATE = "rotate"
    TRANSFORM_OP_SCALE = "scale"

    def __init__(self, op):
        super().__init__()

        self._op = op
        self._settings = carb.settings.get_settings()
        self._settings.set_default_string(self.TRANSFORM_OP_SETTING, self.TRANSFORM_OP_MOVE)

        self._dict = carb.dictionary.get_dictionary()
        self._op_sub = self._settings.subscribe_to_node_change_events(self.TRANSFORM_OP_SETTING, self._on_op_change)
        self._selected_op = self._settings.get(self.TRANSFORM_OP_SETTING)

    def clean(self):
        self._settings.unsubscribe_to_change_events(self._op_sub)

    def _on_op_change(self, item, event_type):
        self._selected_op = self._dict.get(item)
        self._value_changed()

    def _on_op_space_changed(self, item, event_type):
        self._op_space = self._dict.get(item)
        self._value_changed()

    def get_value_as_bool(self):
        return self._selected_op == self._op

    def set_value(self, value):
        """Reimplemented set bool"""
        if value:
            self._settings.set(self.TRANSFORM_OP_SETTING, self._op)


class LocalGlobalTransformModeModel(TransformModeModel):
    TRANSFORM_MODE_GLOBAL = "global"
    TRANSFORM_MODE_LOCAL = "local"

    def __init__(self, op, op_space_setting_path):
        super().__init__(op=op)

        self._setting_path = op_space_setting_path

        self._op_space_sub = self._settings.subscribe_to_node_change_events(
            self._setting_path, self._on_op_space_changed
        )
        self._op_space = self._settings.get(self._setting_path)

    def clean(self):
        self._settings.unsubscribe_to_change_events(self._op_space_sub)
        super().clean()

    def _on_op_space_changed(self, item, event_type):
        self._op_space = self._dict.get(item)
        self._value_changed()

    def get_op_space_mode(self):
        return self._op_space
    
    def get_value_as_string(self):
        return self._op_space

    def set_value(self, value):
        if isinstance(value, bool):
            if not value:
                self._settings.set(
                    self._setting_path,
                    self.TRANSFORM_MODE_LOCAL
                    if self._op_space == self.TRANSFORM_MODE_GLOBAL
                    else self.TRANSFORM_MODE_GLOBAL,
                )
        elif isinstance(value, str):
            if value in [self.TRANSFORM_MODE_LOCAL, self.TRANSFORM_MODE_GLOBAL]:
                self._settings.set(self._setting_path, value)
            else:
                carb.log_warn(f"Unknown value '{value}' for '{self._setting_path}'")
        else:
            carb.log_warn(f"Unknown value type of '{value}' for '{self._setting_path}'")

        super().set_value(value)
