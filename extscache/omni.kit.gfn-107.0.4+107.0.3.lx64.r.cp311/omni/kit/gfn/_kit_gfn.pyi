"""pybind11 omni.kit.gfn bindings"""
from __future__ import annotations
import omni.kit.gfn._kit_gfn
import typing

__all__ = [
    "IGeForceNow",
    "acquire_geforcenow_interface",
    "release_geforcenow_interface"
]


class IGeForceNow():
    """
    Interface class to GFN SDK
    """
    def deregister_on_session_init_callback(self, arg0: int) -> bool: 
        """
        Deregister a session initialization callback
        """
    def get_partner_secure_data(self) -> str: 
        """
        Get partner secure data from GFN SDK
        """
    def register_on_session_init_callback(self, arg0: typing.Callable[[str], None]) -> int: 
        """
        Registers a callback to be called on session initialization.
        """
    def shutdown(self) -> None: 
        """
        Shutdown the GFN SDK
        """
    def startup(self, sdk_library_path: str = '') -> None: 
        """
        Initialize the GFN SDK
        """
    pass
def acquire_geforcenow_interface(plugin_name: str = None, library_path: str = None) -> IGeForceNow:
    pass
def release_geforcenow_interface(arg0: IGeForceNow) -> None:
    pass
