import os
import carb.settings
import omni.ui as ui
from omni.kit.window.preferences import PreferenceBuilder, PERSISTENT_SETTINGS_PREFIX, SettingType

CHARACTER_AUTHORING_FOLDER_SETTING =  "/exts/omni.anim.graph/character_authoring_folder"

class AnimGraphPreference(PreferenceBuilder):
    def __init__(self):
        super().__init__("Animation Graph")

        self._settings = carb.settings.get_settings()

    def build(self):
        """ Capture Screenshot """
        # The path widget. It's not standard because it has the button browse. Since the main layout has two columns,
        # we need to create another layout and put it to the main one.
        with ui.VStack(height=0):
            with self.add_frame("General"):
                with ui.VStack():
                    self._settings_widget = self.create_setting_widget(
                        "Output To Fabric",
                        "/animGraph/useFabric",
                        SettingType.BOOL,
                        tooltip="Enable - AnimGraph evaluation result output to Fabric Cache. Disable - to USD.",
                        enabled = False,
                    )

    def destroy(self):
        self._settings = None
