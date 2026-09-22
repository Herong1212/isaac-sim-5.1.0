"""This module contains bindings to C++ carb::stats::IStats interface.

All the function are in omni.stats.IStats class, to get it use get_editor_interface method, which caches
acquire interface call:

    >>> import omni.stats
    >>> e = omni.stats.get_stats_interface()
    >>> print(f"Is UI hidden: {e.is_ui_hidden()}")
"""

from ._stats import *

# Cached stats instance pointer
def get_stats_interface() -> IStats:
    """Returns cached :class:` omni.stats.IStats` interface"""

    if not hasattr(get_stats_interface, "stats"):
        get_stats_interface.stats = acquire_stats_interface()
    return get_stats_interface.stats
