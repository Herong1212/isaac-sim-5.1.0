import carb
import omni.ext
import omni.kit.app
import asyncio

class _AudioExtension(omni.ext.IExt):
    """
    Extension startup and shutdown event handler.  This handles installing and removing the audio
    preferences page from the app's main preferences window when this extension loads and unloads.
    """

    def __init__(self):
        super().__init__()
        self._preferences_page = None
        self._hooks = []

    def on_startup(self, ext_id):
        """
        Extension startup callback function.  This is called automatically when the Python side of
        this extension loads.  If enabled, the audio preferences page will be installed when this
        extension is later enabled (usually happens automatically after extension load).  The audio
        preferences page will be removed when this extension is unloaded or disabled.

        Args:
            ext_id: The ID of this extension.  This will be a string containing the extension's name
                    and version.
        """

        if carb.settings.get_settings().get("/exts/omni.kit.window.preferences/show_audio"):
            manager = omni.kit.app.get_app().get_extension_manager()
            self._hooks.append(
                manager.subscribe_to_extension_enable(
                    on_enable_fn=lambda _: self._register_page(),
                    on_disable_fn=lambda _: self._unregister_page(),
                    ext_name="omni.kit.window.preferences",
                    hook_name="omni.kit.audiodeviceenum omni.kit.window.preferences listener",
                )
            )

    def on_shutdown(self):
        """
        Extension shutdown callback function.  This is called automatically when the Python side of
        this extension unloads.  This will always attempt to remove the audio preferences page.  This
        operation will be ignored if the page was not originally installed.
        """

        self._unregister_page()
        self._hooks = []


    def _register_page(self):
        try:
            from omni.kit.window.preferences import register_page
            from .audio_page import AudioPreferences

            self._preferences_page = register_page(AudioPreferences())
        except ModuleNotFoundError: # pragma: no cover
            pass

    def _unregister_page(self):
        if self._preferences_page:
            try:
                import omni.kit.window.preferences

                omni.kit.window.preferences.unregister_page(self._preferences_page)
                self._preferences_page = None
            except ModuleNotFoundError: # pragma: no cover
                pass

