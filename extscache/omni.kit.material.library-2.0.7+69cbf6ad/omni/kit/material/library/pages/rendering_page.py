import carb
import carb.settings
import omni.kit.app
import omni.ui as ui
from omni.kit.window.preferences import PreferenceBuilder, SettingType, PERSISTENT_SETTINGS_PREFIX
from typing import Any
from typing import Dict
from typing import Optional


class RenderingPreferences(PreferenceBuilder):
    def __init__(self):
        super().__init__("Rendering")

    def build(self):
        with ui.VStack(height=0):
            """ White Mode """
            with self.add_frame("White Mode"):
                with ui.VStack():
                    widget = self.create_setting_widget("Material", "/rtx/debugMaterialWhite", SettingType.STRING)
                    widget.enabled = False
                    self.create_setting_widget(
                        "Exceptions (Requires Scene Reload)",
                        PERSISTENT_SETTINGS_PREFIX + "/app/rendering/whiteModeExceptions",
                        SettingType.STRING,
                    )
