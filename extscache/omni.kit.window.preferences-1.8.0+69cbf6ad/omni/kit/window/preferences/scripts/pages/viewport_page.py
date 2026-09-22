
import carb
from ..preferences_window import PreferenceBuilder, SettingType

class ViewportPreferences(PreferenceBuilder):
    def __init__(self):
        super().__init__("Viewport")
        settings = carb.settings.get_settings()
        settings.set_default_string("/persistent/app/viewport/autoFrame/mode", "")
        settings.set_default_bool("/persistent/app/viewport/autoFrame/singleCamera", True)
        settings.set_default_bool("/persistent/app/viewport/autoFrame/implicitOnly", True)

        self.__subscription = None
        if settings.get_as_bool("/exts/omni.kit.window.preferences/show_occluded_objects"):
            settings.set_default_bool("/persistent/app/viewport/pickOccluded", settings.get_as_bool("/rtx/raytracing/picking/occluded/enabled"))
            self.__subscription = settings.subscribe_to_node_change_events("/persistent/app/viewport/pickOccluded", self.__on_change_picking_occluded)

    def __del__(self):

        super().__del__()
        if self.__subscription:
            settings = carb.settings.get_settings()
            settings.unsubscribe_to_change_events(self.__subscription)

    def __on_change_picking_occluded(self, item, event_type):
        settings = carb.settings.get_settings()
        settings.set("/rtx/raytracing/picking/occluded/enabled", settings.get_as_bool("/persistent/app/viewport/pickOccluded"))

    def show_page(self) -> bool:
        import omni.kit
        return omni.kit.app.get_app().get_extension_manager().is_extension_enabled("omni.kit.widget.viewport")

    def build(self):
        import omni.ui as ui

        with self.add_frame("Stage Open"):
            with self.add_frame("Auto Frame"):
                with ui.VStack():
                    self.create_setting_widget_combo("Auto Frame",
                                                    "/persistent/app/viewport/autoFrame/mode",
                                                    {
                                                        "Off" : "",
                                                        "First Open": "first_open",
                                                        "Always": "always"
                                                    },
                                                    setting_is_index = False,
                                                    tooltip = "Auto framing mode")

                    self.create_setting_widget("Single Camera Only",
                                               "/persistent/app/viewport/autoFrame/singleCamera",
                                               SettingType.BOOL,
                                               tooltip = "Whether to auto-frame single or multiple cameras")

                    self.create_setting_widget("Implicit Cameras Only",
                                               "/persistent/app/viewport/autoFrame/implicitOnly",
                                               SettingType.BOOL,
                                               tooltip = "Whether to auto-frame any or implicit cameras only")

        if self.__subscription:
            with self.add_frame("Selection"):
                with ui.VStack():
                    self.create_setting_widget("Area Select Occluded Objects",
                                                "/persistent/app/viewport/pickOccluded",
                                                SettingType.BOOL,
                                                tooltip = "Does viewport selection select occluded objects")
