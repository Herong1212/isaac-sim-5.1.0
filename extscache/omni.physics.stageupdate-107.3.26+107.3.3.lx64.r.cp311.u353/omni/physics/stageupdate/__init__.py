from .bindings._physicsStageUpdateNode import IPhysicsStageUpdateNode, acquire_physics_stage_update_node_interface


def _get_interface(func, acq):
    if not hasattr(func, "iface"):
        func.iface = acq()
    return func.iface


def get_physics_stage_update_node_interface() -> IPhysicsStageUpdateNode:
    return _get_interface(get_physics_stage_update_node_interface, acquire_physics_stage_update_node_interface)


from .scripts.extension import *
