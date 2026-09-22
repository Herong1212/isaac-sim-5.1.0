# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""This module defines the LocalGlobalModeModel class for managing and interacting with local and global operation space settings in a UI context."""


import carb
import carb.dictionary
import carb.settings
import omni.ui as ui


class LocalGlobalModeModel(ui.AbstractValueModel):
    """A model for managing local and global operation space settings.

    This class extends `omni.ui.AbstractValueModel` and provides mechanisms to interact with
    operation space settings, allowing the user to switch between local and global transform modes.
    It subscribes to changes in operation space settings and updates the internal state accordingly.

    Args:
        op_space_setting_path (str): The path to the operation space setting in the application settings.
    """

    TRANSFORM_MODE_GLOBAL = "global"
    """str: Indicates global transformation mode."""
    TRANSFORM_MODE_LOCAL = "local"
    """str: Indicates local transformation mode."""

    def __init__(self, op_space_setting_path):
        """Initializes the LocalGlobalModeModel with operational space setting path."""
        super().__init__()

        self._settings = carb.settings.get_settings()
        self._dict = carb.dictionary.get_dictionary()
        self._setting_path = op_space_setting_path
        self._op_space_sub = self._settings.subscribe_to_node_change_events(
            self._setting_path, self._on_op_space_changed
        )
        self._op_space = self._settings.get(self._setting_path)

    def __del__(self):
        self.destroy()

    def destroy(self):
        """Cleans up resources and subscriptions."""
        if self._op_space_sub is not None:
            self._settings.unsubscribe_to_change_events(self._op_space_sub)
            self._op_space_sub = None

    def _on_op_space_changed(self, item, event_type):
        self._op_space = self._dict.get(item)
        self._value_changed()

    def get_value_as_bool(self):
        """Determines if the operational space is set to global mode.

        Returns:
            bool: True if the operational space is global, False if local."""
        return self._op_space != self.TRANSFORM_MODE_LOCAL

    def set_value(self, value):
        """Sets the operational space mode based on a boolean value.

        Args:
            value (bool): True to set global mode, False for local mode."""
        self._settings.set(
            self._setting_path,
            self.TRANSFORM_MODE_LOCAL if value == False else self.TRANSFORM_MODE_GLOBAL,
        )
