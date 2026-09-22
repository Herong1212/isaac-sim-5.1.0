__all__ = ["PropertyUsdPreferences"]

import omni.ui as ui
from omni.kit.window.preferences import PERSISTENT_SETTINGS_PREFIX, PreferenceBuilder, SettingType


class PropertyUsdPreferences(PreferenceBuilder):
    """A class to build the property preferences page."""

    def __init__(self):
        super().__init__("Property Widgets")

    def build(self):
        """Builds the property preferences page."""
        with ui.VStack(height=0):
            with self.add_frame("Property Window"):
                with ui.VStack():
                    w = self.create_setting_widget(
                        "Large selections threshold. This prevents slowdown/stalls on large selections, after this number of prims is selected most of the property window will be hidden.\n\nSet to zero to disable this feature\n\n",
                        PERSISTENT_SETTINGS_PREFIX + "/exts/omni.kit.property.usd/large_selection",
                        SettingType.INT,
                        height=20,
                    )
                    w.identifier = "large_selection"

                    self.spacer()

                    w = self.create_setting_widget(
                        "Raw Usd Properties Widget multi-selection limit. This prevents slowdown/stalls on large selections, after this number of prims is selected content of Raw Usd Properties Widget will be hidden.\n\nSet to zero to disable this feature\n\n",
                        PERSISTENT_SETTINGS_PREFIX + "/exts/omni.kit.property.usd/raw_widget_multi_selection_limit",
                        SettingType.INT,
                        height=20,
                    )
                    w.identifier = "raw_widget_multi_selection_limit"

                    self.spacer()

                    w = self.create_setting_widget(
                        "Update when Enter is pressed.  When Enabled, only update property changes when Enter or Tab is pressed, and not on every keystroke.\n\n",
                        PERSISTENT_SETTINGS_PREFIX + "/exts/omni.kit.property.usd/update_on_press_enter",
                        SettingType.BOOL,
                        height=20,
                    )
                    w.identifier = "update_on_press_enter"

                    ui.Separator()
                    ui.Spacer(height=10)

                    w = self.create_setting_widget(
                        "Large reference threshold. Limit when references frame will start collapsed, this prevents slowdown/stalls on selecting prims with large number of references\n\nSet to zero to disable this feature\n\n",
                        PERSISTENT_SETTINGS_PREFIX + "/exts/omni.kit.property.usd/references_hide_max",
                        SettingType.INT,
                        height=20,
                    )
                    w.identifier = "large_reference_selection"

                    w = self.create_setting_widget(
                        "References check missing paths. When enabled this can cause additional slowdown/stalls on prims with large number of references\n\n",
                        PERSISTENT_SETTINGS_PREFIX + "/exts/omni.kit.property.usd/references_check_missing",
                        SettingType.BOOL,
                        height=20,
                    )
                    w.identifier = "references_widget_check_missing"
