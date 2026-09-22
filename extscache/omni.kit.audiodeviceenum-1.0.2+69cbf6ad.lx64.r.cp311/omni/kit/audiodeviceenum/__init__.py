"""
        This module contains bindings to the C++ omni::audio::IAudioDeviceEnum
        interface.  This provides functionality for enumerating available audio devices
        and collecting some basic information on each one.

        Sound devices attached to the system may change at any point due to user
        activity (ie: connecting or unplugging a USB audio device).  When enumerating
        devices, it is important to collect all device information directly instead
        of caching it.

        The device information is suitable to be used to display to a user in a menu
        to allow them to choose a device to use by name.
"""


from ._audiodeviceenum import *
from .extension import _AudioExtension


# Cached audio device enumerator instance pointer
def get_audio_device_enum_interface() -> IAudioDeviceEnum:
    """
    helper method to retrieve a cached version of the IAudioDeviceEnum interface.

    Returns:
        The cached :class:`omni.kit.audiodeviceenum.IAudioDeviceEnum` interface.  This will
        only be retrieved on the first call.  All subsequent calls will return the cached
        interface object.
    """

    if not hasattr(get_audio_device_enum_interface, "audio_device_enum"):
        get_audio_device_enum_interface.audio_device_enum = acquire_audio_device_enum_interface()
    return get_audio_device_enum_interface.audio_device_enum
