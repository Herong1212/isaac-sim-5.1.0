import omni.kit.app
import carb

class UIPreferencesExtension(omni.ext.IExt):
    def on_startup(self, ext_id):
        self._preferences_page = None
        self._hooks = []

        manager = omni.kit.app.get_app().get_extension_manager()
        self._hooks.append(
            manager.subscribe_to_extension_enable(
                on_enable_fn=lambda _: self._register_page(),
                on_disable_fn=lambda _: self._unregister_page(),
                ext_name="omni.kit.window.preferences",
                hook_name="omni.ui omni.kit.window.preferences listener",
            )
        )

    def on_shutdown(self):
        self._unregister_page()
        self._preferences_page = None
        self._hooks = []

    def _register_page(self):
        from omni.kit.window.preferences import register_page
        from .pages_developer import DeveloperPreferences

        self._preferences_page = register_page(DeveloperPreferences())

    def _unregister_page(self):
        if self._preferences_page:
            import omni.kit.window.preferences

            omni.kit.window.preferences.unregister_page(self._preferences_page)
            self._preferences_page = None
