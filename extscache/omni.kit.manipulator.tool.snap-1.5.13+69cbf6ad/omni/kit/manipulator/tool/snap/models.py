# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import carb
import carb.dictionary
import carb.settings
import omni.ui as ui


class SettingModel(ui.AbstractValueModel):
    """A UI model for synchronizing with application settings.

    This model tracks a specific setting within the application and updates its value based on changes to that setting. It allows for the setting's value to be updated both in the UI and the application settings, ensuring synchronization between the two.

    Args:
        setting_path: str
            The path to the setting which this model will represent."""

    def __init__(self, setting_path: str):
        """Initializes the SettingModel object.

        Args:
            setting_path (str): The path to the setting which this model will represent."""
        super().__init__()

        self._setting_path = setting_path
        self._settings = carb.settings.get_settings()
        self._dict = carb.dictionary.get_dictionary()
        self._subscription = self._settings.subscribe_to_node_change_events(self._setting_path, self._on_change)
        self._value = self._settings.get(self._setting_path)

    def __del__(self):
        """Automatic destructor that calls the destroy method upon deletion."""
        self.destroy()

    def destroy(self):
        """Unsubscribes from setting change events and cleans up resources."""
        if self._subscription is not None:
            self._settings.unsubscribe_to_change_events(self._subscription)
            self._subscription = None

    def _on_change(self, item, event_type):
        """Internal callback for when the subscribed setting changes.

        Args:
            item: The item that has changed.
            event_type: The type of change event that has occurred."""
        self._value = self._dict.get(item)
        self._value_changed()

    def get_value_as_bool(self) -> bool:
        """Returns the current value of the setting as a boolean.

        Returns:
            bool: The boolean representation of the setting value."""
        return bool(self._value)

    def get_value_as_float(self) -> float:
        """Returns the current value of the setting as a float.

        Returns:
            float: The float representation of the setting value."""
        return float(self._value)

    def set_value(self, value):
        """Sets the value of the setting.

        Args:
            value: The new value to set for the setting."""
        self._settings.set(self._setting_path, value)
