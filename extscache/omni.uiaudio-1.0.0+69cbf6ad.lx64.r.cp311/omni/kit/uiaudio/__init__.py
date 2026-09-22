"""
        This module contains bindings for the omni::kit::uiaudio module.
        This provides functionality for playing and managing sound prims in
        USD scenes.

        Sound files may be in RIFF/WAV, Ogg, or FLAC format.
        Data in the sound files may use 8, 16, 24, or 32 bit integer samples,
        or 32 bit floating point samples.  Channel counts may be from 1 to 64
        If more channels of data are provided than the audio device can play,
        some channels will be blended together automatically.
"""


from ._uiaudio import *


# Cached UI audio instance pointer
def get_ui_audio_interface() -> IUiAudio:
    """
    helper method to retrieve a cached version of the IUiAudio interface.

    Returns:
        The cached :class:`omni.kit.uiaudio.IUiAudio` interface.  This will only be
        retrieved on the first call.  All subsequent calls will return the cached interface
        object.
    """

    if not hasattr(get_ui_audio_interface, "ui_audio"):
        get_ui_audio_interface.ui_audio = acquire_ui_audio_interface()
    return get_ui_audio_interface.ui_audio
