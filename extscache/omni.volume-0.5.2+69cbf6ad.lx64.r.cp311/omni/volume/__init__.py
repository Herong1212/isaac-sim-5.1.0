"""This module contains bindings to C++ carb::volume::IVolume interface.

All the function are in omni.volume.IVolume class, to get it use get_editor_interface method, which caches
acquire interface call:

    >>> import omni.volume
    >>> e = omni.volume.get_volume_interface()
    >>> print(f"Is UI hidden: {e.is_ui_hidden()}")
"""

from ._volume import *
from functools import lru_cache

@lru_cache()
def get_volume_interface() -> IVolume:
    """Returns cached :class:` omni.volume.IVolume` interface"""
    return acquire_volume_interface()
