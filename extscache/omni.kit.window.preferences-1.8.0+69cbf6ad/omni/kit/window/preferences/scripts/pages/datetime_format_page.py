import carb.settings
import omni.kit.app
from functools import partial
from ..preferences_window import PreferenceBuilder, PERSISTENT_SETTINGS_PREFIX


class DatetimeFormatPreferences(PreferenceBuilder):
    def __init__(self):
        super().__init__("Datetime Format")

        settings = carb.settings.get_settings()

        if settings.get(PERSISTENT_SETTINGS_PREFIX + "/app/datetime/format") is None:
            settings.set_default_string(PERSISTENT_SETTINGS_PREFIX + "/app/datetime/format", "MM/DD/YYYY")

    def build(self):
        import omni.ui as ui

        # OM-38343: allow user to  switching between different date formats
        with ui.VStack(height=0):
            with self.add_frame("Datetime Format"):
                self.create_setting_widget_combo(
                    "Display Date As", 
                    PERSISTENT_SETTINGS_PREFIX + "/app/datetime/format", 
                    [
                        "MM/DD/YYYY",
                        "DD.MM.YYYY",
                        "DD-MM-YYYY",
                        "YYYY-MM-DD",
                        "YYYY/MM/DD",
                        "YYYY.MM.DD"
                    ]
                )

    def __del__(self): # pragma: no cover
        super().__del__()
