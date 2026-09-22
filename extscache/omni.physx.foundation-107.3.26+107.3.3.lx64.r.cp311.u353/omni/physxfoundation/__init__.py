from .bindings._physxFoundation import acquire_physx_foundation_interface, IPhysxFoundation

def get_physx_foundation_interface() -> IPhysxFoundation:
    if not hasattr(get_physx_foundation_interface, "iface"):
        get_physx_foundation_interface.iface = acquire_physx_foundation_interface()
    return get_physx_foundation_interface.iface

from .scripts.extension import *
