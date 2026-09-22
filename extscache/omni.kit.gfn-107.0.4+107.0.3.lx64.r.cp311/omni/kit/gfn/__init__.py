"""Provides access to the GFN SDK interface"""

__all__ = [
    "get_geforcenow_interface",
    "IGeForceNow",
]

from ._kit_gfn import *

# Cached interface instance pointer
def get_geforcenow_interface() -> IGeForceNow:
    """Returns cached IGeForceNow interface"""

    if not hasattr(get_geforcenow_interface, "geforcenow"):
        get_geforcenow_interface.geforcenow = acquire_geforcenow_interface()
    return get_geforcenow_interface.geforcenow
