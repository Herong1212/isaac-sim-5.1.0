import carb
import omni.ext
import omni.kit.app
import omni.client
from omni.metropolis.utils.ui_util import UIUtil

class ActionAndEventDataGenerationSetupExtension(omni.ext.IExt):
    def on_startup(self, ext_id):
        from omni.kit.window.title import get_main_window_title
        self._settings = carb.settings.get_settings()
        self._set_defaults()

        window_title = get_main_window_title()
        window_title.set_app_version(None)

        UIUtil.open_action_and_event_data_generation_layout()
        omni.kit.app.get_app().print_and_log(f"Action and Event Data Generation App is loaded.")

        omni.client.set_hang_detection_time_ms(10000)


    def on_shutdown(self):
        pass

    def _set_defaults(self):
        self._settings.set_default("/persistent/exts/omni.kit.property.tagging/showAdvancedTagView", False)
        self._settings.set_default("/persistent/exts/omni.kit.property.tagging/showHiddenTags", False)
        self._settings.set_default("/persistent/exts/omni.kit.property.tagging/modifyHiddenTags", False)
        self._settings.set_default("/rtx/raytracing/fractionalCutoutOpacity", True)
