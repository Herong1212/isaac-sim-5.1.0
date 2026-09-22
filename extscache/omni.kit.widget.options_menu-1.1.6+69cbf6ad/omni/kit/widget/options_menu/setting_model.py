"""This module defines a custom UI value model for observing and interacting with application settings."""

import carb
import omni.ui as ui


class SettingModel(ui.AbstractValueModel):
    """A value model that is reimplemented in Python to watch a setting path.

    This model is responsible for observing a specific setting and notifying subscribers about any changes to the setting's value.

        Args:
            setting_path (str): The path of the setting to be monitored."""

    def __init__(self, setting_path: str):
        """Initializes the SettingModel."""
        super().__init__()

        self._setting_path = setting_path
        self._settings = carb.settings.get_settings()
        self._dict = carb.dictionary.get_dictionary()
        self._subscription = self._settings.subscribe_to_node_change_events(self._setting_path, self._on_change)
        self._value = self._settings.get(self._setting_path)

    def destroy(self):
        """Cleans up resources and subscriptions."""
        if self._subscription:
            self._settings.unsubscribe_to_change_events(self._subscription)
            self._subscription = None

    def _on_change(self, item, event_type):
        self._value = self._dict.get(item)
        self._value_changed()

    def get_value_as_bool(self):
        """Returns the setting value as a boolean."""
        return self._value

    def get_value_as_string(self):
        """Returns the setting value as a string."""
        return self._value

    def get_value_as_float(self):
        """Returns the setting value as a float."""
        return self._value

    def get_value_as_int(self):
        """Returns the setting value as an integer."""
        return self._value

    def set_value(self, value):
        """Updates the setting with a new value.

        Args:
            value: The new value to set."""
        if value != self._value:
            self._settings.set(self._setting_path, value)
