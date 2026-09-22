"""This module provides an extension for adding audio property functionalities to Omniverse Kit applications."""

import omni.ext
import omni.kit.app
from pxr import UsdMedia

from .audio_settings_widget import AudioSettingsWidget


class AudioPropertyExtension(omni.ext.IExt):
    """A class designed to extend Omniverse Kit applications with audio property functionalities.

    This extension class manages the registration and unregistration of custom widgets related to audio properties within the Omniverse Kit property window. It extends the 'omni.ext.IExt' interface, which allows it to integrate seamlessly into the Omniverse extension system. Upon startup, it registers widgets for handling media, sound, and audio listener properties, and provides a dedicated audio settings layer. It cleans up by unregistering these widgets upon shutdown.
    """

    def __init__(self):
        """Constructor for AudioPropertyExtension."""
        self._registered = False
        super().__init__()

    def on_startup(self, ext_id):
        """Initializes extension and sets up necessary paths.

        Args:
            ext_id (str): The ID of the extension being started."""
        self._register_widget()

    def on_shutdown(self):
        """Cleans up resources and unregisters widgets when the extension is shutting down."""
        if self._registered:
            self._unregister_widget()

    def _register_widget(self):
        import omni.kit.window.property as p
        from omni.kit.property.usd.usd_property_widget import SchemaPropertiesWidget

        w = p.get_window()
        if w:
            w.register_widget("prim", "media", SchemaPropertiesWidget("Media", UsdMedia.SpatialAudio, False))

            try:
                import OmniAudioSchema

                w.register_widget(
                    "prim", "audio_sound", SchemaPropertiesWidget("Sound", OmniAudioSchema.OmniSound, False)
                )
                w.register_widget(
                    "prim", "audio_listener", SchemaPropertiesWidget("Listener", OmniAudioSchema.OmniListener, False)
                )
            except ModuleNotFoundError:
                pass

            w.register_widget("layers", "audio_settings", AudioSettingsWidget())
            self._registered = True

    def _unregister_widget(self):
        import omni.kit.window.property as p

        w = p.get_window()
        if w:
            w.unregister_widget("prim", "media")
            w.unregister_widget("prim", "audio_sound")
            w.unregister_widget("prim", "audio_listener")
            w.unregister_widget("layers", "audio_settings")
            self._registered = False
