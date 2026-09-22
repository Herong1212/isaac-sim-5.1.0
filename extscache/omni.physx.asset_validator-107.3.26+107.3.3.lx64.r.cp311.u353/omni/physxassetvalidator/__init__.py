from .bindings._physxAssetValidator import IPhysxAssetValidator
from .bindings._physxAssetValidator import acquire_physx_asset_validator_interface

def _get_interface(func, acq):
    if not hasattr(func, "iface"):
        func.iface = acq()
    return func.iface

def get_physx_asset_validator_interface() -> IPhysxAssetValidator:
    return _get_interface(get_physx_asset_validator_interface, acquire_physx_asset_validator_interface)

from .scripts.extension import *
