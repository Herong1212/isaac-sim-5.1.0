"""pybind11 carb.physx.foundation bindings"""
from __future__ import annotations
import omni.physxfoundation.bindings._physxFoundation
import typing

__all__ = [
    "IPhysxFoundation",
    "acquire_physx_foundation_interface",
    "release_physx_foundation_interface"
]


class IPhysxFoundation():
    """
    This interface is the access point to the omni.physx foundation.
    """
    def cuda_device_check(self) -> bool: 
        """
        Check for the presence of at least one CUDA device
        """
    pass
def acquire_physx_foundation_interface(plugin_name: str = None, library_path: str = None) -> IPhysxFoundation:
    pass
def release_physx_foundation_interface(arg0: IPhysxFoundation) -> None:
    pass
