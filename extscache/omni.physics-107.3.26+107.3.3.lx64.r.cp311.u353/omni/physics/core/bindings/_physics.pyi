"""pybind11 omni.physics bindings"""
from __future__ import annotations
import omni.physics.core.bindings._physics
import typing
import carb._carb

__all__ = [
    "ACCELERATION",
    "BenchmarkFns",
    "CONTACT_FOUND",
    "CONTACT_LOST",
    "CONTACT_PERSIST",
    "ContactData",
    "ContactDataVector",
    "ContactEventHeader",
    "ContactEventHeaderVector",
    "ContactEventType",
    "FORCE",
    "ForceMode",
    "FrictionAnchor",
    "FrictionAnchorsDataVector",
    "IMPULSE",
    "IPhysics",
    "IPhysicsBenchmarks",
    "IPhysicsInteraction",
    "IPhysicsSceneQuery",
    "IPhysicsSimulation",
    "IPhysicsStageUpdate",
    "InteractionFns",
    "OverlapHit",
    "PhysicsProfileStats",
    "PhysicsStepContext",
    "RaycastHit",
    "SceneQueryFns",
    "SceneQueryHitLocation",
    "SceneQueryHitObject",
    "Simulation",
    "SimulationFns",
    "SimulationId",
    "StageUpdateFns",
    "SweepHit",
    "VELOCITY_CHANGE",
    "acquire_physics_benchmarks_interface",
    "acquire_physics_interaction_interface",
    "acquire_physics_interface",
    "acquire_physics_scene_query_interface",
    "acquire_physics_simulation_interface",
    "acquire_physics_stage_update_interface",
    "k_invalid_simulation_id",
    "k_invalid_subscription_id",
    "release_physics_benchmarks_interface",
    "release_physics_interaction_interface",
    "release_physics_interface",
    "release_physics_scene_query_interface",
    "release_physics_simulation_interface",
    "release_physics_stage_update_interface"
]


class BenchmarkFns():
    """
    Collection of functions for managing benchmarks.
    Handles benchmark control and statistics.
    """
    def __init__(self) -> None: 
        """
        Create a new benchmark functions object
        """
    @property
    def subscribe_profile_stats_events(self) -> typing.Any:
        """
        Subscribe to profile stats events

        :type: typing.Any
        """
    @subscribe_profile_stats_events.setter
    def subscribe_profile_stats_events(*args, **kwargs) -> None:
        """
        Subscribe to profile stats events
        """
    @property
    def unsubscribe_profile_stats_events(self) -> typing.Callable[[int], None]:
        """
        Unsubscribe from profile stats events

        :type: typing.Callable[[int], None]
        """
    @unsubscribe_profile_stats_events.setter
    def unsubscribe_profile_stats_events(self, arg0: typing.Callable[[int], None]) -> None:
        """
        Unsubscribe from profile stats events
        """
    pass
class ContactData():
    def __init__(self) -> None: ...
    @property
    def impulse(self) -> carb._carb.Float3:
        """
        :type: carb._carb.Float3
        """
    @impulse.setter
    def impulse(self, arg0: carb._carb.Float3) -> None:
        pass
    @property
    def normal(self) -> carb._carb.Float3:
        """
        :type: carb._carb.Float3
        """
    @normal.setter
    def normal(self, arg0: carb._carb.Float3) -> None:
        pass
    @property
    def position(self) -> carb._carb.Float3:
        """
        :type: carb._carb.Float3
        """
    @position.setter
    def position(self, arg0: carb._carb.Float3) -> None:
        pass
    @property
    def separation(self) -> float:
        """
        :type: float
        """
    @separation.setter
    def separation(self, arg0: float) -> None:
        pass
    pass
class ContactDataVector():
    def __bool__(self) -> bool: 
        """
        Check whether the list is nonempty
        """
    @typing.overload
    def __delitem__(self, arg0: int) -> None: 
        """
        Delete the list elements at index ``i``

        Delete list elements using a slice object
        """
    @typing.overload
    def __delitem__(self, arg0: slice) -> None: ...
    @typing.overload
    def __getitem__(self, s: slice) -> ContactDataVector: 
        """
        Retrieve list elements using a slice object
        """
    @typing.overload
    def __getitem__(self, arg0: int) -> ContactData: ...
    @typing.overload
    def __init__(self) -> None: 
        """
        Copy constructor
        """
    @typing.overload
    def __init__(self, arg0: ContactDataVector) -> None: ...
    @typing.overload
    def __init__(self, arg0: typing.Iterable) -> None: ...
    def __iter__(self) -> typing.Iterator: ...
    def __len__(self) -> int: ...
    @typing.overload
    def __setitem__(self, arg0: int, arg1: ContactData) -> None: 
        """
        Assign list elements using a slice object
        """
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: ContactDataVector) -> None: ...
    def append(self, x: ContactData) -> None: 
        """
        Add an item to the end of the list
        """
    def clear(self) -> None: 
        """
        Clear the contents
        """
    @typing.overload
    def extend(self, L: ContactDataVector) -> None: 
        """
        Extend the list by appending all the items in the given list

        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def extend(self, L: typing.Iterable) -> None: ...
    def insert(self, i: int, x: ContactData) -> None: 
        """
        Insert an item at a given position.
        """
    @typing.overload
    def pop(self) -> ContactData: 
        """
        Remove and return the last item

        Remove and return the item at index ``i``
        """
    @typing.overload
    def pop(self, i: int) -> ContactData: ...
    pass
class ContactEventHeader():
    """
    Contact event header, issued for contact pair.
    Contains information about the pair and the number of contact data.
    """
    def __init__(self) -> None: ...
    @property
    def actor0(self) -> int:
        """
        Actor0 of the contact pair, can be retyped to SdfPath.

        :type: int
        """
    @actor0.setter
    def actor0(self, arg0: int) -> None:
        """
        Actor0 of the contact pair, can be retyped to SdfPath.
        """
    @property
    def actor1(self) -> int:
        """
        Actor1 of the contact pair, can be retyped to SdfPath.

        :type: int
        """
    @actor1.setter
    def actor1(self, arg0: int) -> None:
        """
        Actor1 of the contact pair, can be retyped to SdfPath.
        """
    @property
    def collider0(self) -> int:
        """
        Collider0 of the contact pair, can be retyped to SdfPath.

        :type: int
        """
    @collider0.setter
    def collider0(self, arg0: int) -> None:
        """
        Collider0 of the contact pair, can be retyped to SdfPath.
        """
    @property
    def collider1(self) -> int:
        """
        Collider1 of the contact pair, can be retyped to SdfPath.

        :type: int
        """
    @collider1.setter
    def collider1(self, arg0: int) -> None:
        """
        Collider1 of the contact pair, can be retyped to SdfPath.
        """
    @property
    def contact_data_offset(self) -> int:
        """
        Contact data offset index to the contact data array.

        :type: int
        """
    @contact_data_offset.setter
    def contact_data_offset(self, arg0: int) -> None:
        """
        Contact data offset index to the contact data array.
        """
    @property
    def friction_anchors_data_offset(self) -> int:
        """
        Friction anchors offset index to the friction anchors data array.

        :type: int
        """
    @friction_anchors_data_offset.setter
    def friction_anchors_data_offset(self, arg0: int) -> None:
        """
        Friction anchors offset index to the friction anchors data array.
        """
    @property
    def num_contact_data(self) -> int:
        """
        Number of contact data in the contact data array for given pair.

        :type: int
        """
    @num_contact_data.setter
    def num_contact_data(self, arg0: int) -> None:
        """
        Number of contact data in the contact data array for given pair.
        """
    @property
    def num_friction_anchors_data(self) -> int:
        """
        Number of friction anchors data in the friction anchors data array for given pair.

        :type: int
        """
    @num_friction_anchors_data.setter
    def num_friction_anchors_data(self, arg0: int) -> None:
        """
        Number of friction anchors data in the friction anchors data array for given pair.
        """
    @property
    def proto_index0(self) -> int:
        """
        Point instancer prototypeIndex for collider0, used only for point instancers otherwise 0xFFFFFFFF.

        :type: int
        """
    @proto_index0.setter
    def proto_index0(self, arg0: int) -> None:
        """
        Point instancer prototypeIndex for collider0, used only for point instancers otherwise 0xFFFFFFFF.
        """
    @property
    def proto_index1(self) -> int:
        """
        Point instancer prototypeIndex for collider1, used only for point instancers otherwise 0xFFFFFFFF.

        :type: int
        """
    @proto_index1.setter
    def proto_index1(self, arg0: int) -> None:
        """
        Point instancer prototypeIndex for collider1, used only for point instancers otherwise 0xFFFFFFFF.
        """
    @property
    def stage_id(self) -> int:
        """
        Stage id of the simulated USD stage.

        :type: int
        """
    @stage_id.setter
    def stage_id(self, arg0: int) -> None:
        """
        Stage id of the simulated USD stage.
        """
    @property
    def type(self) -> ContactEventType:
        """
        Contact event header type.

        :type: ContactEventType
        """
    @type.setter
    def type(self, arg0: ContactEventType) -> None:
        """
        Contact event header type.
        """
    pass
class ContactEventHeaderVector():
    def __bool__(self) -> bool: 
        """
        Check whether the list is nonempty
        """
    @typing.overload
    def __delitem__(self, arg0: int) -> None: 
        """
        Delete the list elements at index ``i``

        Delete list elements using a slice object
        """
    @typing.overload
    def __delitem__(self, arg0: slice) -> None: ...
    @typing.overload
    def __getitem__(self, s: slice) -> ContactEventHeaderVector: 
        """
        Retrieve list elements using a slice object
        """
    @typing.overload
    def __getitem__(self, arg0: int) -> ContactEventHeader: ...
    @typing.overload
    def __init__(self) -> None: 
        """
        Copy constructor
        """
    @typing.overload
    def __init__(self, arg0: ContactEventHeaderVector) -> None: ...
    @typing.overload
    def __init__(self, arg0: typing.Iterable) -> None: ...
    def __iter__(self) -> typing.Iterator: ...
    def __len__(self) -> int: ...
    @typing.overload
    def __setitem__(self, arg0: int, arg1: ContactEventHeader) -> None: 
        """
        Assign list elements using a slice object
        """
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: ContactEventHeaderVector) -> None: ...
    def append(self, x: ContactEventHeader) -> None: 
        """
        Add an item to the end of the list
        """
    def clear(self) -> None: 
        """
        Clear the contents
        """
    @typing.overload
    def extend(self, L: ContactEventHeaderVector) -> None: 
        """
        Extend the list by appending all the items in the given list

        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def extend(self, L: typing.Iterable) -> None: ...
    def insert(self, i: int, x: ContactEventHeader) -> None: 
        """
        Insert an item at a given position.
        """
    @typing.overload
    def pop(self) -> ContactEventHeader: 
        """
        Remove and return the last item

        Remove and return the item at index ``i``
        """
    @typing.overload
    def pop(self, i: int) -> ContactEventHeader: ...
    pass
class ContactEventType():
    """
            Enumeration of different types of contact events.
            Determines the type of contact event.
        

    Members:

      CONTACT_FOUND : Contact issued for newly found contact pairs

      CONTACT_LOST : Contact issued for contact pair lost

      CONTACT_PERSIST : Contact issued for persistent contact pairs
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    CONTACT_FOUND: omni.physics.core.bindings._physics.ContactEventType # value = <ContactEventType.CONTACT_FOUND: 0>
    CONTACT_LOST: omni.physics.core.bindings._physics.ContactEventType # value = <ContactEventType.CONTACT_LOST: 1>
    CONTACT_PERSIST: omni.physics.core.bindings._physics.ContactEventType # value = <ContactEventType.CONTACT_PERSIST: 2>
    __members__: dict # value = {'CONTACT_FOUND': <ContactEventType.CONTACT_FOUND: 0>, 'CONTACT_LOST': <ContactEventType.CONTACT_LOST: 1>, 'CONTACT_PERSIST': <ContactEventType.CONTACT_PERSIST: 2>}
    pass
class ForceMode():
    """
            Enumeration of different ways to apply forces in physics simulation.
            Determines how forces are interpreted and applied to objects.
        

    Members:

      FORCE : Apply a continuous force

      IMPULSE : Apply an instantaneous impulse

      VELOCITY_CHANGE : Directly change the velocity

      ACCELERATION : Apply an acceleration
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    ACCELERATION: omni.physics.core.bindings._physics.ForceMode # value = <ForceMode.ACCELERATION: 3>
    FORCE: omni.physics.core.bindings._physics.ForceMode # value = <ForceMode.FORCE: 0>
    IMPULSE: omni.physics.core.bindings._physics.ForceMode # value = <ForceMode.IMPULSE: 1>
    VELOCITY_CHANGE: omni.physics.core.bindings._physics.ForceMode # value = <ForceMode.VELOCITY_CHANGE: 2>
    __members__: dict # value = {'FORCE': <ForceMode.FORCE: 0>, 'IMPULSE': <ForceMode.IMPULSE: 1>, 'VELOCITY_CHANGE': <ForceMode.VELOCITY_CHANGE: 2>, 'ACCELERATION': <ForceMode.ACCELERATION: 3>}
    pass
class FrictionAnchor():
    def __init__(self) -> None: ...
    @property
    def impulse(self) -> carb._carb.Float3:
        """
        :type: carb._carb.Float3
        """
    @impulse.setter
    def impulse(self, arg0: carb._carb.Float3) -> None:
        pass
    @property
    def position(self) -> carb._carb.Float3:
        """
        :type: carb._carb.Float3
        """
    @position.setter
    def position(self, arg0: carb._carb.Float3) -> None:
        pass
    pass
class FrictionAnchorsDataVector():
    def __bool__(self) -> bool: 
        """
        Check whether the list is nonempty
        """
    @typing.overload
    def __delitem__(self, arg0: int) -> None: 
        """
        Delete the list elements at index ``i``

        Delete list elements using a slice object
        """
    @typing.overload
    def __delitem__(self, arg0: slice) -> None: ...
    @typing.overload
    def __getitem__(self, s: slice) -> FrictionAnchorsDataVector: 
        """
        Retrieve list elements using a slice object
        """
    @typing.overload
    def __getitem__(self, arg0: int) -> FrictionAnchor: ...
    @typing.overload
    def __init__(self) -> None: 
        """
        Copy constructor
        """
    @typing.overload
    def __init__(self, arg0: FrictionAnchorsDataVector) -> None: ...
    @typing.overload
    def __init__(self, arg0: typing.Iterable) -> None: ...
    def __iter__(self) -> typing.Iterator: ...
    def __len__(self) -> int: ...
    @typing.overload
    def __setitem__(self, arg0: int, arg1: FrictionAnchor) -> None: 
        """
        Assign list elements using a slice object
        """
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: FrictionAnchorsDataVector) -> None: ...
    def append(self, x: FrictionAnchor) -> None: 
        """
        Add an item to the end of the list
        """
    def clear(self) -> None: 
        """
        Clear the contents
        """
    @typing.overload
    def extend(self, L: FrictionAnchorsDataVector) -> None: 
        """
        Extend the list by appending all the items in the given list

        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def extend(self, L: typing.Iterable) -> None: ...
    def insert(self, i: int, x: FrictionAnchor) -> None: 
        """
        Insert an item at a given position.
        """
    @typing.overload
    def pop(self) -> FrictionAnchor: 
        """
        Remove and return the last item

        Remove and return the item at index ``i``
        """
    @typing.overload
    def pop(self, i: int) -> FrictionAnchor: ...
    pass
class IPhysics():
    """
    Main physics interface for managing simulations.
    Provides functionality to register, unregister, and control physics simulations.
    """
    def activate_simulation(self, id: SimulationId) -> None: 
        """
        Activate a simulation by ID
        """
    def deactivate_simulation(self, id: SimulationId) -> None: 
        """
        Deactivate a simulation by ID
        """
    def get_num_simulations(self) -> int: 
        """
        Get the total number of registered simulations
        """
    def get_simulation(self, id: SimulationId) -> object: 
        """
        Get a simulation by ID
        """
    def get_simulation_ids(self) -> typing.List[SimulationId]: 
        """
        Get all registered simulation IDs
        """
    def get_simulation_name(self, id: SimulationId) -> str: 
        """
        Get the name of a simulation by ID
        """
    def is_simulation_active(self, id: SimulationId) -> bool: 
        """
        Check if a simulation is active
        """
    def register_simulation(self, simulation: Simulation, name: str) -> SimulationId: 
        """
        Register a new physics simulation with the given name
        """
    def unregister_simulation(self, id: SimulationId) -> None: 
        """
        Unregister a physics simulation by ID
        """
    pass
class IPhysicsBenchmarks():
    def subscribe_profile_stats_events(self, callback: typing.Callable[[typing.List[PhysicsProfileStats]], None]) -> carb._carb.Subscription: 
        """
        Subscribe to physics simulation profile stats events.

        Note: Subscription cannot be changed in the callback.
        If subscription is used, getProfileStats will not return any results
        as the results are cleared after the subscription sends them.

        Args:
            callback: The callback function to be called with the profile data.

        Returns:
            SubscriptionId for release, kInvalidSubscriptionId if the operation failed
        """
    pass
class IPhysicsInteraction():
    """
    Interface for controlling physics interaction behavior.
    Provides functionality for managing physics reset behavior and raycast handling.
    """
    def disable_reset_on_stop(self, disable: bool) -> None: 
        """
        Controls the behavior of the ResetOnStop setting.

        Args:
            disable (bool): Disable/enable the reset on stop override.
        """
    def handle_raycast(self, orig: object, dir: object, input: bool) -> None: 
        """
        Called when a raycast request is executed - used for picking.

        Args:
            orig (Optional[carb.Float3]): Start position of the raycast, can be None
            dir (Optional[carb.Float3]): Direction of the raycast, can be None
            input (bool): Whether the input control is set or reset (e.g. mouse down)
        """
    def is_disabled_reset_on_stop(self) -> bool: 
        """
        Returns the current state of the ResetOnStop setting.

        Returns:
            bool: Disable/enable for the reset on stop.
        """
    pass
class IPhysicsSceneQuery():
    def overlap_box(self, half_extent: carb._carb.Float3, position: carb._carb.Float3, rotation: carb._carb.Float4, report_fn: function) -> int: 
        """
        Overlap test of a box against objects in the physics scene.

        Args:
            half_extent: Box half extent
            position: Box position
            rotation: Box rotation (quaternion x, y, z, w)
            report_fn: Scene query hit report function, return True to continue traversal, False to stop traversal

        Returns:
            int: Number of overlaps found
        """
    def overlap_box_any(self, half_extent: carb._carb.Float3, position: carb._carb.Float3, rotation: carb._carb.Float4) -> bool: 
        """
        Overlap test of a box against objects in the physics scene, reports only boolean.

        Args:
            half_extent: Box half extent
            position: Box position
            rotation: Box rotation (quaternion x, y, z, w)

        Returns:
            bool: True if overlap found
        """
    def overlap_shape(self, g_prim_path: int, report_fn: function) -> int: 
        """
        Overlap test of a UsdGeomGPrim against objects in the physics scene.

        Note: A convex mesh approximation will be used for meshes, the first query will compute the convex mesh
        approximation and store the result in a local cache

        Args:
            g_prim_path: UsdGeomGPrim path encoded in uint64_t
            report_fn: Scene query hit report function, return True to continue traversal, False to stop traversal

        Returns:
            int: Number of overlaps found
        """
    def overlap_shape_any(self, g_prim_path: int) -> bool: 
        """
        Overlap test of a mesh against objects in the physics scene, reports only boolean.

        Note: A convex mesh approximation will be used for the test, the first query will compute the convex mesh
        approximation and store the result in a local cache

        Args:
            g_prim_path: UsdGeomGPrim path encoded in uint64_t

        Returns:
            bool: True if overlap found
        """
    def overlap_sphere(self, radius: float, position: carb._carb.Float3, report_fn: function) -> int: 
        """
        Overlap test of a sphere against objects in the physics scene.

        Args:
            radius: Sphere radius
            position: Sphere position
            report_fn: Scene query hit report function, return True to continue traversal, False to stop traversal

        Returns:
            int: Number of overlaps found
        """
    def overlap_sphere_any(self, radius: float, position: carb._carb.Float3) -> bool: 
        """
        Overlap test of a sphere against objects in the physics scene, reports only boolean.

        Args:
            radius: Sphere radius
            position: Sphere position

        Returns:
            bool: True if overlap found
        """
    def raycast_all(self, origin: carb._carb.Float3, unit_dir: carb._carb.Float3, distance: float, report_fn: function, both_sides: bool) -> None: 
        """
        Raycast physics scene, returns all hits found in a raycast callback.

        Args:
            origin: Origin of the ray
            unit_dir: Normalized direction of the ray
            distance: Length of the ray. Has to be in the [0, inf) range
            report_fn: Scene query hit report function, return True to continue traversal, False to stop traversal
            both_sides: If mesh both triangle sides should be checked
        """
    def raycast_any(self, origin: carb._carb.Float3, unit_dir: carb._carb.Float3, distance: float, both_sides: bool) -> bool: 
        """
        Raycast any physics scene, returns only boolean if hit was found or not.

        Args:
            origin: Origin of the ray
            unit_dir: Normalized direction of the ray
            distance: Length of the ray. Has to be in the [0, inf) range
            both_sides: If mesh both triangle sides should be checked

        Returns:
            bool: True if hit was found
        """
    def raycast_closest(self, origin: carb._carb.Float3, unit_dir: carb._carb.Float3, distance: float, both_sides: bool) -> typing.Tuple[bool, RaycastHit]: 
        """
        Raycast physics scene, return the closest hit found.

        Args:
            origin: Origin of the ray
            unit_dir: Normalized direction of the ray
            distance: Length of the ray. Has to be in the [0, inf) range
            both_sides: If mesh both triangle sides should be checked

        Returns:
            Tuple of (bool, RaycastHit): True if hit was found and the hit information
        """
    def sweep_box_all(self, half_extent: carb._carb.Float3, position: carb._carb.Float3, rotation: carb._carb.Float4, unit_dir: carb._carb.Float3, distance: float, report_fn: function, both_sides: bool) -> None: 
        """
        Sweep test of a box against all objects in the physics scene, returning all the hits found.

        Args:
            half_extent: Box half extent
            position: Box position. This is the origin of the sweep
            rotation: Box rotation (quaternion x, y, z, w)
            unit_dir: Normalized direction of the sweep
            distance: Length of the ray. Has to be in the [0, inf) range
            report_fn: Scene query hit report function, return True to continue traversal, False to stop traversal
            both_sides: If mesh both triangle sides should be checked
        """
    def sweep_box_any(self, half_extent: carb._carb.Float3, position: carb._carb.Float3, rotation: carb._carb.Float4, unit_dir: carb._carb.Float3, distance: float, both_sides: bool) -> bool: 
        """
        Sweep test of a box against all objects in the physics scene, returning whether any hit was found.

        Args:
            half_extent: Box half extent
            position: Box position. This is the origin of the sweep
            rotation: Box rotation (quaternion x, y, z, w)
            unit_dir: Normalized direction of the sweep
            distance: Length of the ray. Has to be in the [0, inf) range
            both_sides: If mesh both triangle sides should be checked

        Returns:
            bool: True if hit was found
        """
    def sweep_box_closest(self, half_extent: carb._carb.Float3, position: carb._carb.Float3, rotation: carb._carb.Float4, unit_dir: carb._carb.Float3, distance: float, both_sides: bool) -> typing.Tuple[bool, SweepHit]: 
        """
        Sweep test of a box against all objects in the physics scene, returning the closest hit found.

        Args:
            half_extent: Box half extent
            position: Box position. This is the origin of the sweep
            rotation: Box rotation (quaternion x, y, z, w)
            unit_dir: Normalized direction of the sweep
            distance: Length of the ray. Has to be in the [0, inf) range
            both_sides: If mesh both triangle sides should be checked

        Returns:
            Tuple of (bool, SweepHit): True if hit was found and the hit information
        """
    def sweep_shape_all(self, g_prim_path: int, unit_dir: carb._carb.Float3, distance: float, report_fn: function, both_sides: bool) -> None: 
        """
        Sweep test of a UsdGeomGPrim against all objects in the physics scene, returning all the hits found.

        Note: A convex mesh approximation will be used for the test, the first query will compute the convex mesh
        approximation and store the result in a local cache

        Args:
            g_prim_path: UsdGeomGPrim path encoded in uint64_t
            unit_dir: Normalized direction of the sweep
            distance: Length of the ray. Has to be in the [0, inf) range
            report_fn: Scene query hit report function, return True to continue traversal, False to stop traversal
            both_sides: If mesh both triangle sides should be checked
        """
    def sweep_shape_any(self, g_prim_path: int, unit_dir: carb._carb.Float3, distance: float, both_sides: bool) -> bool: 
        """
        Sweep test of a UsdGeomGPrim against all objects in the physics scene, returning whether any hit was found.

        Note: A convex mesh approximation will be used for meshes, the first query will compute the convex mesh
        approximation and store the result in a local cache

        Args:
            g_prim_path: UsdGeomGPrim path encoded in uint64_t
            unit_dir: Normalized direction of the sweep
            distance: Length of the ray. Has to be in the [0, inf) range
            both_sides: If mesh both triangle sides should be checked

        Returns:
            bool: True if hit was found
        """
    def sweep_shape_closest(self, g_prim_path: int, unit_dir: carb._carb.Float3, distance: float, both_sides: bool) -> typing.Tuple[bool, SweepHit]: 
        """
        Sweep test of a UsdGeomGPrim against all objects in the physics scene, returning the closest hit found.

        Note: A convex mesh approximation will be used for meshes, the first query will compute the convex mesh
        approximation and store the result in a local cache

        Args:
            g_prim_path: UsdGeomGPrim path encoded in uint64_t
            unit_dir: Normalized direction of the sweep
            distance: Length of the ray. Has to be in the [0, inf) range
            both_sides: If mesh both triangle sides should be checked

        Returns:
            Tuple of (bool, SweepHit): True if hit was found and the hit information
        """
    def sweep_sphere_all(self, radius: float, origin: carb._carb.Float3, unit_dir: carb._carb.Float3, distance: float, report_fn: function, both_sides: bool) -> None: 
        """
        Sweep test of a sphere against all objects in the physics scene, returning all the hits found.

        Args:
            radius: Sphere radius
            origin: Origin of the sweep
            unit_dir: Normalized direction of the sweep
            distance: Length of the ray. Has to be in the [0, inf) range
            report_fn: Scene query hit report function, return True to continue traversal, False to stop traversal
            both_sides: If mesh both triangle sides should be checked
        """
    def sweep_sphere_any(self, radius: float, origin: carb._carb.Float3, unit_dir: carb._carb.Float3, distance: float, both_sides: bool) -> bool: 
        """
        Sweep test of a sphere against all objects in the physics scene, returning whether any hit was found.

        Args:
            radius: Sphere radius
            origin: Origin of the sweep
            unit_dir: Normalized direction of the sweep
            distance: Length of the ray. Has to be in the [0, inf) range
            both_sides: If mesh both triangle sides should be checked

        Returns:
            bool: True if hit was found
        """
    def sweep_sphere_closest(self, radius: float, origin: carb._carb.Float3, unit_dir: carb._carb.Float3, distance: float, both_sides: bool) -> typing.Tuple[bool, SweepHit]: 
        """
        Sweep test of a sphere against all objects in the physics scene, returning the closest hit found.

        Args:
            radius: Sphere radius
            origin: Origin of the sweep
            unit_dir: Normalized direction of the sweep
            distance: Length of the ray. Has to be in the [0, inf) range
            both_sides: If mesh both triangle sides should be checked

        Returns:
            Tuple of (bool, SweepHit): True if hit was found and the hit information
        """
    pass
class IPhysicsSimulation():
    def add_force_at_pos(self, stage_id: int, path: int, force: carb._carb.Float3, pos: carb._carb.Float3, mode: ForceMode) -> None: 
        """
        Applies a force (or impulse) defined in the global coordinate frame, acting at a particular
        point in global coordinates, to the actor.

        Args:
            stage_id (int): USD stageId
            path (int): Body USD path encoded to uint64_t
            force (tuple): Force / impulse to add, defined in the global frame
            pos (tuple): Position in the global frame to add the force at
            mode (int): The mode to use when applying the force/impulse
        """
    def add_torque(self, stage_id: int, path: int, torque: carb._carb.Float3) -> None: 
        """
        Applies a torque (or impulse) at the center of mass

        Args:
            stage_id (int): USD stageId
            path (int): Body USD path encoded to uint64_t
            torque (tuple): Torque to add to the body center of mass
        """
    def attach_stage(self, id: int) -> bool: 
        """
        Attach USD stage. This will run the physics parser and will populate the simulation with the corresponding simulation objects.

        Note: previous stage will be detached.

        Args:
            id (int): USD stageId (can be retrieved from a stagePtr - pxr::UsdUtilsStageCache::Get().GetId(stagePtr).ToLongInt())

        Returns:
            bool: True if stage was successfully attached.
        """
    def check_results(self) -> bool: 
        """
        Check if simulation finished.

        Returns:
            bool: True if simulation finished.
        """
    def detach_stage(self) -> None: 
        """
        Detach USD stage, this will remove all objects from the simulation
        """
    def fetch_results(self) -> None: 
        """
        Fetch simulation results.
        Writing out simulation results based on physics settings.

        Note: This is a blocking call. The function will wait until the simulation is finished.
        """
    def flush_changes(self) -> None: 
        """
        Flush changes will force physics to process buffered changes

        Changes to physics gets buffered, in some cases flushing changes is required if order is required.

        Example - prim A gets added. Existing prim B has a relationship that gets switched to use A. Currently,
        the relationship change gets processed immediately and fails because prim A only gets added at the
        start of the next sim step.
        """
    def get_attached_stage(self) -> int: 
        """
        Gets the currently attached USD stage.

        Returns:
            int: USD stageId, 0 means no stage is attached.
        """
    def get_simulation_step_count(self, simulation_id: SimulationId) -> int: 
        """
        Get the number of physics steps performed in the active simulation.

        The step count resets to 0 when a new simulation starts.

        Args:
            simulation_id: Simulation ID

        Returns:
            int: Number of steps since the currently active simulation started or 0 if there is no active simulation
        """
    def get_simulation_time_steps_per_second(self, simulation_id: SimulationId, stage_id: int, scene_path: int) -> int: 
        """
        Get physics simulation time steps per second.

        Args:
            simulation_id: Simulation ID
            stage_id (int): Stage id
            scene_path (int): Returns the time steps for given scene if 0 is passed returns the first found scene stepping

        Returns:
            int: Current time steps per second
        """
    def get_simulation_timestamp(self, simulation_id: SimulationId) -> int: 
        """
        Get physics simulation timestamp.

        Timestamp will increase with every simulation step.

        Args:
            simulation_id: Simulation ID

        Returns:
            int: Current timestamp
        """
    def is_change_tracking_paused(self) -> bool: 
        """
        Check if fabric change tracking for physics listener is paused or not

        Returns:
            bool: True if change tracking is paused
        """
    def is_sleeping(self, stage_id: int, path: int) -> bool: 
        """
        Checks whether a body sleeps

        Args:
            stage_id (int): USD stageId
            path (int): Body USD path encoded to uint64_t

        Returns:
            bool: True if body is asleep
        """
    def pause_change_tracking(self, pause: bool) -> None: 
        """
        Pause change tracking for physics listener

        Args:
            pause (bool): Pause or resume the change tracking
        """
    def put_to_sleep(self, stage_id: int, path: int) -> None: 
        """
        Puts to sleep body on given path

        Args:
            stage_id (int): USD stageId
            path (int): Body USD path encoded to uint64_t
        """
    def simulate(self, elapsed_time: float, current_time: float) -> None: 
        """
        Execute physics simulation

        The simulation will simulate the exact elapsedTime passed. No substepping will happen.
        It is the caller's responsibility to provide reasonable elapsedTime.
        In general it is recommended to use fixed size time steps with a maximum of 1/60 of a second

        Args:
            elapsedTime (float): Simulation time in seconds.
            currentTime (float): Current time, might be used for time sampled transformations to apply.
        """
    def subscribe_physics_contact_report_events(self, contact_report_fn: typing.Callable[[ContactEventHeaderVector, ContactDataVector, FrictionAnchorsDataVector], None]) -> carb._carb.Subscription: 
        """
        Subscribe to physics simulation contact report events.

        Note: The contact buffer data are available for one simulation step.

        Args:
            contact_report_fn: The callback function to be called on contact report.
            userData: Optional user data to be passed back in the callback function.

        Returns:
            int: Subscription Id for release
        """
    def subscribe_physics_on_step_events(self, pre_step: bool, order: int, on_update: typing.Callable[[float, PhysicsStepContext], None]) -> carb._carb.Subscription: 
        """
        Subscribe to physics pre/post step events.

        Note: Subscriptions cannot be changed in the onUpdate callback

        Args:
            preStep (bool): Whether to execute this callback right *before* the physics step event. If this is false, the
                           callback will be executed right *after* the physics step event.
            order (int): An integer value used to order the callbacks: 0 means "highest priority", 1 is "less priority" and so on.
            onUpdate: The callback function to be called on update.
            userData: The userData to be passed back in the callback function.

        Returns:
            int: Subscription Id for release, returns kInvalidSubscriptionId if failed
        """
    def wake_up(self, stage_id: int, path: int) -> None: 
        """
        Wakes up body on given path

        Args:
            stage_id (int): USD stageId
            path (int): Body USD path encoded to uint64_t
        """
    pass
class IPhysicsStageUpdate():
    """
    Interface to mimic the requirements of current stage update nodes.
    Currently only one stage can be attached, multiple stages are not yet supported.
    """
    def force_load_physics_from_usd(self) -> None: 
        """
        Called when a force load from USD is requested.
        This will make sure that the physics engine creates internal objects for the stage that is attached.
        """
    def handle_raycast(self, orig: object, dir: object, input: bool) -> None: 
        """
        Called when a raycast request is executed - used for picking.

        Args:
            orig (Optional[carb.Float3]): Start position of the raycast, can be None
            dir (Optional[carb.Float3]): Direction of the raycast, can be None
            input (bool): Whether the input control is set or reset (e.g. mouse down)
        """
    def on_attach(self, stage_id: int) -> None: 
        """
        Called when a stage gets attached, does not load physics. Does just set internally stage.

        Args:
            stage_id (int): Stage Id that should be attached
        """
    def on_detach(self) -> None: 
        """
        Called when stage gets detached.
        """
    def on_pause(self) -> None: 
        """
        Called when timeline gets paused.
        """
    def on_reset(self) -> None: 
        """
        Called when timeline is stopped.
        """
    def on_resume(self, current_time: float) -> None: 
        """
        Called when timeline play is requested.

        Args:
            current_time (float): Current time in seconds
        """
    def on_update(self, current_time: float, elapsed_secs: float, enable_update: bool) -> None: 
        """
        Called when on stage update.

        Args:
            current_time (float): Current time in seconds
            elapsed_secs (float): Elapsed time from previous update in seconds
            enable_update (bool): Enable physics update, physics can be disabled, but we still need to update other subsystems
        """
    def release_physics_objects(self) -> None: 
        """
        Called when a release of physics objects is requested.
        """
    def reset_simulation(self) -> None: 
        """
        Called when a reset of physics simulation is requested.
        This will release all physics objects and reset the simulation, while keeping the stage attached.
        """
    pass
class InteractionFns():
    """
    Collection of functions for managing physics interactions.
    Handles raycast queries and interaction control.
    """
    def __init__(self) -> None: 
        """
        Create a new interaction functions object
        """
    @property
    def disable_reset_on_stop(self) -> typing.Callable[[bool], None]:
        """
        Disable reset on stop

        :type: typing.Callable[[bool], None]
        """
    @disable_reset_on_stop.setter
    def disable_reset_on_stop(self, arg0: typing.Callable[[bool], None]) -> None:
        """
        Disable reset on stop
        """
    @property
    def handle_raycast(self) -> typing.Callable[[float, float, bool], None]:
        """
        Handle raycast queries

        :type: typing.Callable[[float, float, bool], None]
        """
    @handle_raycast.setter
    def handle_raycast(self, arg0: typing.Callable[[float, float, bool], None]) -> None:
        """
        Handle raycast queries
        """
    @property
    def is_disabled_reset_on_stop(self) -> typing.Callable[[], bool]:
        """
        Check if reset on stop is disabled

        :type: typing.Callable[[], bool]
        """
    @is_disabled_reset_on_stop.setter
    def is_disabled_reset_on_stop(self, arg0: typing.Callable[[], bool]) -> None:
        """
        Check if reset on stop is disabled
        """
    pass
class OverlapHit(SceneQueryHitObject):
    def __init__(self) -> None: ...
    pass
class PhysicsProfileStats():
    def __init__(self) -> None: ...
    @property
    def ms(self) -> float:
        """
        Time in milliseconds for this zone

        :type: float
        """
    @ms.setter
    def ms(self, arg0: float) -> None:
        """
        Time in milliseconds for this zone
        """
    @property
    def zone_name(self) -> str:
        """
        Name of the profiling zone

        :type: str
        """
    @zone_name.setter
    def zone_name(self, arg0: str) -> None:
        """
        Name of the profiling zone
        """
    pass
class PhysicsStepContext():
    """
    Context information for a physics simulation step.
    Contains data needed during physics simulation updates.
    """
    def __init__(self) -> None: 
        """
        Create an empty physics step context
        """
    @property
    def scene_path(self) -> int:
        """
        Path to the scene being simulated

        :type: int
        """
    @scene_path.setter
    def scene_path(self, arg0: int) -> None:
        """
        Path to the scene being simulated
        """
    @property
    def simulation_id(self) -> SimulationId:
        """
        ID of the simulation being stepped

        :type: SimulationId
        """
    @simulation_id.setter
    def simulation_id(self, arg0: SimulationId) -> None:
        """
        ID of the simulation being stepped
        """
    pass
class RaycastHit(SceneQueryHitLocation, SceneQueryHitObject):
    def __init__(self) -> None: ...
    pass
class SceneQueryFns():
    """
    Collection of functions for managing scene queries.
    Handles raycast queries and scene query control.
    """
    def __init__(self) -> None: 
        """
        Create a new scene query functions object
        """
    @property
    def overlap_box(self) -> typing.Any:
        """
        Overlap box

        :type: typing.Any
        """
    @overlap_box.setter
    def overlap_box(*args, **kwargs) -> None:
        """
        Overlap box
        """
    @property
    def overlap_box_any(self) -> typing.Callable[[carb._carb.Float3, carb._carb.Float3, carb._carb.Float4], bool]:
        """
        Overlap box any

        :type: typing.Callable[[carb._carb.Float3, carb._carb.Float3, carb._carb.Float4], bool]
        """
    @overlap_box_any.setter
    def overlap_box_any(self, arg0: typing.Callable[[carb._carb.Float3, carb._carb.Float3, carb._carb.Float4], bool]) -> None:
        """
        Overlap box any
        """
    @property
    def overlap_shape(self) -> typing.Any:
        """
        Overlap shape

        :type: typing.Any
        """
    @overlap_shape.setter
    def overlap_shape(*args, **kwargs) -> None:
        """
        Overlap shape
        """
    @property
    def overlap_shape_any(self) -> typing.Callable[[int], bool]:
        """
        Overlap shape any

        :type: typing.Callable[[int], bool]
        """
    @overlap_shape_any.setter
    def overlap_shape_any(self, arg0: typing.Callable[[int], bool]) -> None:
        """
        Overlap shape any
        """
    @property
    def overlap_sphere(self) -> typing.Any:
        """
        Overlap sphere

        :type: typing.Any
        """
    @overlap_sphere.setter
    def overlap_sphere(*args, **kwargs) -> None:
        """
        Overlap sphere
        """
    @property
    def overlap_sphere_any(self) -> typing.Callable[[float, carb._carb.Float3], bool]:
        """
        Overlap sphere any

        :type: typing.Callable[[float, carb._carb.Float3], bool]
        """
    @overlap_sphere_any.setter
    def overlap_sphere_any(self, arg0: typing.Callable[[float, carb._carb.Float3], bool]) -> None:
        """
        Overlap sphere any
        """
    @property
    def raycast_all(self) -> typing.Any:
        """
        Raycast all objects

        :type: typing.Any
        """
    @raycast_all.setter
    def raycast_all(*args, **kwargs) -> None:
        """
        Raycast all objects
        """
    @property
    def raycast_any(self) -> typing.Callable[[carb._carb.Float3, carb._carb.Float3, float, bool], bool]:
        """
        Raycast any object

        :type: typing.Callable[[carb._carb.Float3, carb._carb.Float3, float, bool], bool]
        """
    @raycast_any.setter
    def raycast_any(self, arg0: typing.Callable[[carb._carb.Float3, carb._carb.Float3, float, bool], bool]) -> None:
        """
        Raycast any object
        """
    @property
    def raycast_closest(self) -> typing.Any:
        """
        Raycast the closest object

        :type: typing.Any
        """
    @raycast_closest.setter
    def raycast_closest(*args, **kwargs) -> None:
        """
        Raycast the closest object
        """
    @property
    def sweep_box_all(self) -> typing.Any:
        """
        Sweep box all objects

        :type: typing.Any
        """
    @sweep_box_all.setter
    def sweep_box_all(*args, **kwargs) -> None:
        """
        Sweep box all objects
        """
    @property
    def sweep_box_any(self) -> typing.Callable[[carb._carb.Float3, carb._carb.Float3, carb._carb.Float4, carb._carb.Float3, float, bool], bool]:
        """
        Sweep box any object

        :type: typing.Callable[[carb._carb.Float3, carb._carb.Float3, carb._carb.Float4, carb._carb.Float3, float, bool], bool]
        """
    @sweep_box_any.setter
    def sweep_box_any(self, arg0: typing.Callable[[carb._carb.Float3, carb._carb.Float3, carb._carb.Float4, carb._carb.Float3, float, bool], bool]) -> None:
        """
        Sweep box any object
        """
    @property
    def sweep_box_closest(self) -> typing.Any:
        """
        Sweep box the closest object

        :type: typing.Any
        """
    @sweep_box_closest.setter
    def sweep_box_closest(*args, **kwargs) -> None:
        """
        Sweep box the closest object
        """
    @property
    def sweep_shape_all(self) -> typing.Any:
        """
        Sweep shape all objects

        :type: typing.Any
        """
    @sweep_shape_all.setter
    def sweep_shape_all(*args, **kwargs) -> None:
        """
        Sweep shape all objects
        """
    @property
    def sweep_shape_any(self) -> typing.Callable[[int, carb._carb.Float3, float, bool], bool]:
        """
        Sweep shape any object

        :type: typing.Callable[[int, carb._carb.Float3, float, bool], bool]
        """
    @sweep_shape_any.setter
    def sweep_shape_any(self, arg0: typing.Callable[[int, carb._carb.Float3, float, bool], bool]) -> None:
        """
        Sweep shape any object
        """
    @property
    def sweep_shape_closest(self) -> typing.Any:
        """
        Sweep shape the closest object

        :type: typing.Any
        """
    @sweep_shape_closest.setter
    def sweep_shape_closest(*args, **kwargs) -> None:
        """
        Sweep shape the closest object
        """
    @property
    def sweep_sphere_all(self) -> typing.Any:
        """
        Sweep sphere all objects

        :type: typing.Any
        """
    @sweep_sphere_all.setter
    def sweep_sphere_all(*args, **kwargs) -> None:
        """
        Sweep sphere all objects
        """
    @property
    def sweep_sphere_any(self) -> typing.Callable[[float, carb._carb.Float3, carb._carb.Float3, float, bool], bool]:
        """
        Sweep sphere any object

        :type: typing.Callable[[float, carb._carb.Float3, carb._carb.Float3, float, bool], bool]
        """
    @sweep_sphere_any.setter
    def sweep_sphere_any(self, arg0: typing.Callable[[float, carb._carb.Float3, carb._carb.Float3, float, bool], bool]) -> None:
        """
        Sweep sphere any object
        """
    @property
    def sweep_sphere_closest(self) -> typing.Any:
        """
        Sweep sphere the closest object

        :type: typing.Any
        """
    @sweep_sphere_closest.setter
    def sweep_sphere_closest(*args, **kwargs) -> None:
        """
        Sweep sphere the closest object
        """
    pass
class SceneQueryHitLocation(SceneQueryHitObject):
    def __init__(self) -> None: ...
    @property
    def distance(self) -> float:
        """
        :type: float
        """
    @distance.setter
    def distance(self, arg0: float) -> None:
        pass
    @property
    def face_index(self) -> int:
        """
        :type: int
        """
    @face_index.setter
    def face_index(self, arg0: int) -> None:
        pass
    @property
    def material(self) -> int:
        """
        :type: int
        """
    @material.setter
    def material(self, arg0: int) -> None:
        pass
    @property
    def normal(self) -> carb._carb.Float3:
        """
        :type: carb._carb.Float3
        """
    @normal.setter
    def normal(self, arg0: carb._carb.Float3) -> None:
        pass
    @property
    def position(self) -> carb._carb.Float3:
        """
        :type: carb._carb.Float3
        """
    @position.setter
    def position(self, arg0: carb._carb.Float3) -> None:
        pass
    pass
class SceneQueryHitObject():
    def __init__(self) -> None: ...
    @property
    def collision(self) -> int:
        """
        :type: int
        """
    @collision.setter
    def collision(self, arg0: int) -> None:
        pass
    @property
    def proto_index(self) -> int:
        """
        :type: int
        """
    @proto_index.setter
    def proto_index(self, arg0: int) -> None:
        pass
    @property
    def rigid_body(self) -> int:
        """
        :type: int
        """
    @rigid_body.setter
    def rigid_body(self, arg0: int) -> None:
        pass
    pass
class Simulation():
    """
    Main physics simulation class that combines all simulation functionality.
    Provides access to simulation, scene query, interaction, and stage update functions.
    """
    def __init__(self) -> None: 
        """
        Create a new simulation instance
        """
    @property
    def benchmark_fns(self) -> BenchmarkFns:
        """
        Benchmark functions

        :type: BenchmarkFns
        """
    @benchmark_fns.setter
    def benchmark_fns(self, arg0: BenchmarkFns) -> None:
        """
        Benchmark functions
        """
    @property
    def interaction_fns(self) -> InteractionFns:
        """
        Interaction functions

        :type: InteractionFns
        """
    @interaction_fns.setter
    def interaction_fns(self, arg0: InteractionFns) -> None:
        """
        Interaction functions
        """
    @property
    def scene_query_fns(self) -> SceneQueryFns:
        """
        Scene query functions

        :type: SceneQueryFns
        """
    @scene_query_fns.setter
    def scene_query_fns(self, arg0: SceneQueryFns) -> None:
        """
        Scene query functions
        """
    @property
    def simulation_fns(self) -> SimulationFns:
        """
        Core simulation functions

        :type: SimulationFns
        """
    @simulation_fns.setter
    def simulation_fns(self, arg0: SimulationFns) -> None:
        """
        Core simulation functions
        """
    @property
    def stage_update_fns(self) -> StageUpdateFns:
        """
        Stage update functions

        :type: StageUpdateFns
        """
    @stage_update_fns.setter
    def stage_update_fns(self, arg0: StageUpdateFns) -> None:
        """
        Stage update functions
        """
    pass
class SimulationFns():
    """
    Collection of functions for managing physics simulation.
    Provides core functionality for physics simulation control and interaction.
    """
    def __init__(self) -> None: 
        """
        Create a new simulation functions object
        """
    @property
    def add_force_at_pos(self) -> typing.Callable[[int, int, carb._carb.Float3, carb._carb.Float3, ForceMode], None]:
        """
        Add a force at a specific position

        :type: typing.Callable[[int, int, carb._carb.Float3, carb._carb.Float3, ForceMode], None]
        """
    @add_force_at_pos.setter
    def add_force_at_pos(self, arg0: typing.Callable[[int, int, carb._carb.Float3, carb._carb.Float3, ForceMode], None]) -> None:
        """
        Add a force at a specific position
        """
    @property
    def add_torque(self) -> typing.Callable[[int, int, carb._carb.Float3], None]:
        """
        Add torque to an object

        :type: typing.Callable[[int, int, carb._carb.Float3], None]
        """
    @add_torque.setter
    def add_torque(self, arg0: typing.Callable[[int, int, carb._carb.Float3], None]) -> None:
        """
        Add torque to an object
        """
    @property
    def attach_stage(self) -> typing.Callable[[int], bool]:
        """
        Function to attach a stage to the simulation

        :type: typing.Callable[[int], bool]
        """
    @attach_stage.setter
    def attach_stage(self, arg0: typing.Callable[[int], bool]) -> None:
        """
        Function to attach a stage to the simulation
        """
    @property
    def check_results(self) -> typing.Callable[[], bool]:
        """
        Check if simulation results are available

        :type: typing.Callable[[], bool]
        """
    @check_results.setter
    def check_results(self, arg0: typing.Callable[[], bool]) -> None:
        """
        Check if simulation results are available
        """
    @property
    def detach_stage(self) -> typing.Callable[[], None]:
        """
        Function to detach a stage from the simulation

        :type: typing.Callable[[], None]
        """
    @detach_stage.setter
    def detach_stage(self, arg0: typing.Callable[[], None]) -> None:
        """
        Function to detach a stage from the simulation
        """
    @property
    def fetch_results(self) -> typing.Callable[[], None]:
        """
        Retrieve simulation results

        :type: typing.Callable[[], None]
        """
    @fetch_results.setter
    def fetch_results(self, arg0: typing.Callable[[], None]) -> None:
        """
        Retrieve simulation results
        """
    @property
    def flush_changes(self) -> typing.Callable[[], None]:
        """
        Apply pending changes to the simulation

        :type: typing.Callable[[], None]
        """
    @flush_changes.setter
    def flush_changes(self, arg0: typing.Callable[[], None]) -> None:
        """
        Apply pending changes to the simulation
        """
    @property
    def get_attached_stage(self) -> typing.Callable[[], int]:
        """
        Get the currently attached stage

        :type: typing.Callable[[], int]
        """
    @get_attached_stage.setter
    def get_attached_stage(self, arg0: typing.Callable[[], int]) -> None:
        """
        Get the currently attached stage
        """
    @property
    def get_simulation_step_count(self) -> typing.Callable[[], int]:
        """
        Get the number of simulation steps executed

        :type: typing.Callable[[], int]
        """
    @get_simulation_step_count.setter
    def get_simulation_step_count(self, arg0: typing.Callable[[], int]) -> None:
        """
        Get the number of simulation steps executed
        """
    @property
    def get_simulation_time_steps_per_second(self) -> typing.Callable[[int, int], int]:
        """
        Get the simulation time steps per second

        :type: typing.Callable[[int, int], int]
        """
    @get_simulation_time_steps_per_second.setter
    def get_simulation_time_steps_per_second(self, arg0: typing.Callable[[int, int], int]) -> None:
        """
        Get the simulation time steps per second
        """
    @property
    def get_simulation_timestamp(self) -> typing.Callable[[], int]:
        """
        Get the current simulation timestamp

        :type: typing.Callable[[], int]
        """
    @get_simulation_timestamp.setter
    def get_simulation_timestamp(self, arg0: typing.Callable[[], int]) -> None:
        """
        Get the current simulation timestamp
        """
    @property
    def is_change_tracking_paused(self) -> typing.Callable[[], bool]:
        """
        Check if change tracking is paused

        :type: typing.Callable[[], bool]
        """
    @is_change_tracking_paused.setter
    def is_change_tracking_paused(self, arg0: typing.Callable[[], bool]) -> None:
        """
        Check if change tracking is paused
        """
    @property
    def is_sleeping(self) -> typing.Callable[[int, int], bool]:
        """
        Check if a physics object is sleeping

        :type: typing.Callable[[int, int], bool]
        """
    @is_sleeping.setter
    def is_sleeping(self, arg0: typing.Callable[[int, int], bool]) -> None:
        """
        Check if a physics object is sleeping
        """
    @property
    def pause_change_tracking(self) -> typing.Callable[[bool], None]:
        """
        Pause tracking of simulation changes

        :type: typing.Callable[[bool], None]
        """
    @pause_change_tracking.setter
    def pause_change_tracking(self, arg0: typing.Callable[[bool], None]) -> None:
        """
        Pause tracking of simulation changes
        """
    @property
    def put_to_sleep(self) -> typing.Callable[[int, int], None]:
        """
        Put a physics object to sleep

        :type: typing.Callable[[int, int], None]
        """
    @put_to_sleep.setter
    def put_to_sleep(self, arg0: typing.Callable[[int, int], None]) -> None:
        """
        Put a physics object to sleep
        """
    @property
    def simulate(self) -> typing.Callable[[float, float], None]:
        """
        Run the physics simulation

        :type: typing.Callable[[float, float], None]
        """
    @simulate.setter
    def simulate(self, arg0: typing.Callable[[float, float], None]) -> None:
        """
        Run the physics simulation
        """
    @property
    def subscribe_physics_contact_report_events(self) -> typing.Callable[[typing.Callable[[ContactEventHeaderVector, ContactDataVector, FrictionAnchorsDataVector], None]], int]:
        """
        Subscribe to physics contact events

        :type: typing.Callable[[typing.Callable[[ContactEventHeaderVector, ContactDataVector, FrictionAnchorsDataVector], None]], int]
        """
    @subscribe_physics_contact_report_events.setter
    def subscribe_physics_contact_report_events(self, arg0: typing.Callable[[typing.Callable[[ContactEventHeaderVector, ContactDataVector, FrictionAnchorsDataVector], None]], int]) -> None:
        """
        Subscribe to physics contact events
        """
    @property
    def subscribe_physics_on_step_events(self) -> typing.Callable[[bool, int, typing.Callable[[float, PhysicsStepContext], None]], int]:
        """
        Subscribe to physics step events

        :type: typing.Callable[[bool, int, typing.Callable[[float, PhysicsStepContext], None]], int]
        """
    @subscribe_physics_on_step_events.setter
    def subscribe_physics_on_step_events(self, arg0: typing.Callable[[bool, int, typing.Callable[[float, PhysicsStepContext], None]], int]) -> None:
        """
        Subscribe to physics step events
        """
    @property
    def unsubscribe_physics_contact_report_events(self) -> typing.Callable[[int], None]:
        """
        Unsubscribe from physics contact events

        :type: typing.Callable[[int], None]
        """
    @unsubscribe_physics_contact_report_events.setter
    def unsubscribe_physics_contact_report_events(self, arg0: typing.Callable[[int], None]) -> None:
        """
        Unsubscribe from physics contact events
        """
    @property
    def unsubscribe_physics_on_step_events(self) -> typing.Callable[[int], None]:
        """
        Unsubscribe from physics step events

        :type: typing.Callable[[int], None]
        """
    @unsubscribe_physics_on_step_events.setter
    def unsubscribe_physics_on_step_events(self, arg0: typing.Callable[[int], None]) -> None:
        """
        Unsubscribe from physics step events
        """
    @property
    def wake_up(self) -> typing.Callable[[int, int], None]:
        """
        Wake up a sleeping physics object

        :type: typing.Callable[[int, int], None]
        """
    @wake_up.setter
    def wake_up(self, arg0: typing.Callable[[int, int], None]) -> None:
        """
        Wake up a sleeping physics object
        """
    pass
class SimulationId():
    """
    A unique identifier for a physics simulation instance.
    Used to reference and manage different physics simulations in the system.
    """
    def __eq__(self, arg0: SimulationId) -> bool: 
        """
        Compare two simulation IDs for equality
        """
    def __hash__(self) -> int: 
        """
        Get the hash value of the simulation ID
        """
    @typing.overload
    def __init__(self) -> None: 
        """
        Create an invalid simulation ID

        Create a simulation ID with the given value
        """
    @typing.overload
    def __init__(self, arg0: int) -> None: ...
    def __ne__(self, arg0: SimulationId) -> bool: 
        """
        Compare two simulation IDs for inequality
        """
    @property
    def id(self) -> int:
        """
        The underlying ID value

        :type: int
        """
    pass
class StageUpdateFns():
    """
    Collection of functions for managing stage updates in physics simulation.
    Handles stage lifecycle and update events.
    """
    def __init__(self) -> None: 
        """
        Create a new stage update functions object
        """
    @property
    def force_load_physics_from_usd(self) -> typing.Callable[[], None]:
        """
        Force load physics data from USD

        :type: typing.Callable[[], None]
        """
    @force_load_physics_from_usd.setter
    def force_load_physics_from_usd(self, arg0: typing.Callable[[], None]) -> None:
        """
        Force load physics data from USD
        """
    @property
    def handle_raycast(self) -> typing.Callable[[float, float, bool], None]:
        """
        Handle raycast queries

        :type: typing.Callable[[float, float, bool], None]
        """
    @handle_raycast.setter
    def handle_raycast(self, arg0: typing.Callable[[float, float, bool], None]) -> None:
        """
        Handle raycast queries
        """
    @property
    def on_attach(self) -> typing.Callable[[int], None]:
        """
        Callback when a stage is attached

        :type: typing.Callable[[int], None]
        """
    @on_attach.setter
    def on_attach(self, arg0: typing.Callable[[int], None]) -> None:
        """
        Callback when a stage is attached
        """
    @property
    def on_detach(self) -> typing.Callable[[], None]:
        """
        Callback when a stage is detached

        :type: typing.Callable[[], None]
        """
    @on_detach.setter
    def on_detach(self, arg0: typing.Callable[[], None]) -> None:
        """
        Callback when a stage is detached
        """
    @property
    def on_pause(self) -> typing.Callable[[], None]:
        """
        Callback when simulation pauses

        :type: typing.Callable[[], None]
        """
    @on_pause.setter
    def on_pause(self, arg0: typing.Callable[[], None]) -> None:
        """
        Callback when simulation pauses
        """
    @property
    def on_reset(self) -> typing.Callable[[], None]:
        """
        Callback when simulation resets

        :type: typing.Callable[[], None]
        """
    @on_reset.setter
    def on_reset(self, arg0: typing.Callable[[], None]) -> None:
        """
        Callback when simulation resets
        """
    @property
    def on_resume(self) -> typing.Callable[[float], None]:
        """
        Callback when simulation resumes

        :type: typing.Callable[[float], None]
        """
    @on_resume.setter
    def on_resume(self, arg0: typing.Callable[[float], None]) -> None:
        """
        Callback when simulation resumes
        """
    @property
    def on_update(self) -> typing.Callable[[float, float, bool], None]:
        """
        Callback for stage updates

        :type: typing.Callable[[float, float, bool], None]
        """
    @on_update.setter
    def on_update(self, arg0: typing.Callable[[float, float, bool], None]) -> None:
        """
        Callback for stage updates
        """
    @property
    def release_physics_objects(self) -> typing.Callable[[], None]:
        """
        Release physics objects

        :type: typing.Callable[[], None]
        """
    @release_physics_objects.setter
    def release_physics_objects(self, arg0: typing.Callable[[], None]) -> None:
        """
        Release physics objects
        """
    @property
    def reset_simulation(self) -> typing.Callable[[], None]:
        """
        Reset simulation

        :type: typing.Callable[[], None]
        """
    @reset_simulation.setter
    def reset_simulation(self, arg0: typing.Callable[[], None]) -> None:
        """
        Reset simulation
        """
    pass
class SweepHit(SceneQueryHitLocation, SceneQueryHitObject):
    def __init__(self) -> None: ...
    pass
def acquire_physics_benchmarks_interface(plugin_name: str = None, library_path: str = None) -> IPhysicsBenchmarks:
    pass
def acquire_physics_interaction_interface(plugin_name: str = None, library_path: str = None) -> IPhysicsInteraction:
    pass
def acquire_physics_interface(plugin_name: str = None, library_path: str = None) -> IPhysics:
    pass
def acquire_physics_scene_query_interface(plugin_name: str = None, library_path: str = None) -> IPhysicsSceneQuery:
    pass
def acquire_physics_simulation_interface(plugin_name: str = None, library_path: str = None) -> IPhysicsSimulation:
    pass
def acquire_physics_stage_update_interface(plugin_name: str = None, library_path: str = None) -> IPhysicsStageUpdate:
    pass
def release_physics_benchmarks_interface(arg0: IPhysicsBenchmarks) -> None:
    pass
def release_physics_interaction_interface(arg0: IPhysicsInteraction) -> None:
    pass
def release_physics_interface(arg0: IPhysics) -> None:
    pass
def release_physics_scene_query_interface(arg0: IPhysicsSceneQuery) -> None:
    pass
def release_physics_simulation_interface(arg0: IPhysicsSimulation) -> None:
    pass
def release_physics_stage_update_interface(arg0: IPhysicsStageUpdate) -> None:
    pass
ACCELERATION: omni.physics.core.bindings._physics.ForceMode # value = <ForceMode.ACCELERATION: 3>
CONTACT_FOUND: omni.physics.core.bindings._physics.ContactEventType # value = <ContactEventType.CONTACT_FOUND: 0>
CONTACT_LOST: omni.physics.core.bindings._physics.ContactEventType # value = <ContactEventType.CONTACT_LOST: 1>
CONTACT_PERSIST: omni.physics.core.bindings._physics.ContactEventType # value = <ContactEventType.CONTACT_PERSIST: 2>
FORCE: omni.physics.core.bindings._physics.ForceMode # value = <ForceMode.FORCE: 0>
IMPULSE: omni.physics.core.bindings._physics.ForceMode # value = <ForceMode.IMPULSE: 1>
VELOCITY_CHANGE: omni.physics.core.bindings._physics.ForceMode # value = <ForceMode.VELOCITY_CHANGE: 2>
k_invalid_simulation_id: omni.physics.core.bindings._physics.SimulationId
k_invalid_subscription_id = 1099511627775
