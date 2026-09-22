import carb.settings

import omni.ext
import omni.kit.renderer_capture


class Extension(omni.ext.IExt):
    """Renderer capture extension"""
    def on_startup(self):
        """Called when the extension is started up."""
        self._settings = carb.settings.get_settings()
        self._settings.set_default_bool("/exts/omni.kit.renderer.capture/autostartCapture", True)
        self._autostart = self._settings.get("/exts/omni.kit.renderer.capture/autostartCapture")
        if self._autostart:
            self._renderer_capture = omni.kit.renderer_capture.acquire_renderer_capture_interface()
            self._renderer_capture.startup()

    def on_shutdown(self):
        """Called when the extension is shut down."""
        if self._autostart:
            self._renderer_capture.shutdown()
            self._renderer_capture = None
