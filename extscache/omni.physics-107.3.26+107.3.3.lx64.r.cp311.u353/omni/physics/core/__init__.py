from .bindings._physics import *


def _get_interface(func, acq):
    if not hasattr(func, "iface"):
        func.iface = acq()
    return func.iface


def get_physics_interface() -> IPhysics:
    return _get_interface(get_physics_interface, acquire_physics_interface)


def get_physics_stage_update_interface() -> IPhysicsStageUpdate:
    return _get_interface(get_physics_stage_update_interface, acquire_physics_stage_update_interface)


def get_physics_simulation_interface() -> IPhysicsSimulation:
    return _get_interface(get_physics_simulation_interface, acquire_physics_simulation_interface)


def get_physics_scene_query_interface() -> IPhysicsSceneQuery:
    return _get_interface(get_physics_scene_query_interface, acquire_physics_scene_query_interface)


def get_physics_interaction_interface() -> IPhysicsInteraction:
    return _get_interface(get_physics_interaction_interface, acquire_physics_interaction_interface)


def get_physics_benchmarks_interface() -> IPhysicsBenchmarks:
    return _get_interface(get_physics_benchmarks_interface, acquire_physics_benchmarks_interface)


from .scripts.extension import PhysicsExtension
