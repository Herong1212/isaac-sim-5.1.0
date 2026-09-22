import carb
import omni.ext
import omni.kit.app
from .._resourceMonitor import *

class PublicExtension(omni.ext.IExt):
    def on_startup(self):
        self._resourceMonitor = acquire_resource_monitor_interface()

        self._preferences_page = None
        if carb.settings.get_settings().get("/exts/omni.kit.window.preferences/show_resource_monitor"):
            self._hooks = []
            manager = omni.kit.app.get_app().get_extension_manager()
            self._hooks.append(
                manager.subscribe_to_extension_enable(
                    on_enable_fn=lambda _: self._register_page(),
                    on_disable_fn=lambda _: self._unregister_page(),
                    ext_name="omni.kit.window.preferences",
                    hook_name="omni.resourcemonitor omni.kit.window.preferences listener",
                )
            )

    def on_shutdown(self):
        self._unregister_page()
        release_resource_monitor_interface(self._resourceMonitor)
        self._hooks = []

    def _register_page(self):
        try:
            from omni.kit.window.preferences import register_page
            from .resourcemonitor_page import ResourceMonitorPreferences

            self._preferences_page = register_page(ResourceMonitorPreferences())
        except ModuleNotFoundError:
            pass

    def _unregister_page(self):
        if self._preferences_page:
            try:
                import omni.kit.window.preferences

                omni.kit.window.preferences.unregister_page(self._preferences_page)
                self._preferences_page = None
            except ModuleNotFoundError:
                pass

