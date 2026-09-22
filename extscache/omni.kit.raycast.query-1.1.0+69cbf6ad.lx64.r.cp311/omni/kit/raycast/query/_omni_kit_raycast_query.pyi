"""pybind11 omni.kit.raycast.query.IRaycastQuery bindings"""
from __future__ import annotations
import omni.kit.raycast.query._omni_kit_raycast_query
import typing

__all__ = [
    "IRaycastQuery",
    "Ray",
    "RayQueryResult",
    "Result",
    "acquire_raycast_query_interface"
]


class IRaycastQuery():
    def add_raycast_sequence(self) -> int: 
        """
        Add a sequence of raycast queries that maintains last valid value
          and will execute raycast on current scene.

        Returns:
            int: Sequence id in raycast sequence for added.
        """
    def get_latest_result_from_raycast_sequence(self, arg0: int) -> typing.Tuple[Result, Ray, RayQueryResult]: 
        """
        Get latest result from a sequence of raycasts.

        Args:
            sequenceId (int): Sequence id returned by addRaycastSequence.

        Returns:
            Tuple(:obj:'Result', :obj:'Ray', :obj:'RayQueryResult'): Latest ray that was resolved and result of the ray request.
        """
    def get_latest_result_from_raycast_sequence_array(self, arg0: int) -> typing.Tuple[Result, typing.List[Ray], typing.List[RayQueryResult]]: 
        """
        Get latest result from a sequence of raycasts.

        Args:
            sequenceId (int): Sequence id returned by addRaycastSequence.

        Returns:
            Tuple(:obj:'Result', :obj:'Ray', :obj:'RayQueryResult'): Latest ray that was resolved and result of the ray request.
        """
    def get_raycast_sequence_array_size(self, arg0: int) -> typing.Tuple[Result, int]: 
        """
        Get the size of the raycast sequence.

        Args:
            sequenceId (int): Sequence id returned by addRaycastSequence.

        Returns:
            Tuple(:obj:'Result', int): Result and size.
        """
    def remove_raycast_sequence(self, arg0: int) -> Result: 
        """
        Remove a sequence of raycasts.

        Args:
            sequenceId (int): Sequence id to removed from RaycastSequence.

        Returns:
            :obj:'Result': Error code if function failed.
        """
    def set_raycast_sequence_array_size(self, arg0: int, arg1: int) -> Result: 
        """
        Set the size of the raycast sequence.

        Args:
            sequenceId (int): Sequence id returned by addRaycastSequence.
            size (int): Number of ray casts in sequence.

        Returns:
            :obj:'Result': Error code if function failed.
        """
    def submit_ray_to_raycast_sequence(self, arg0: int, arg1: Ray) -> Result: 
        """
        Submit a single ray request to a sequence of raycasts. The sequence must have a size of 1.

        Args:
            sequenceId (int): Sequence id returned by addRaycastSequence.
            ray (:obj:'Ray'): The ray to submit.

        Returns:
            :obj:'Result': Error code if function failed.
        """
    def submit_ray_to_raycast_sequence_array(self, arg0: int, arg1: typing.List[Ray]) -> Result: 
        """
        Submit an array of rays request to a sequence of raycasts.

        Args:
            sequenceId (int): Sequence id returned by addRaycastSequence.
            rays (List[:obj:'Ray']): The rays array to submit.

        Returns:
            :obj:'Result': Error code if function failed.
        """
    def submit_raycast_query(self, ray: Ray, callback: typing.Callable[[Ray, RayQueryResult], None]) -> None: 
        """
        This function adds a raycast query operation in the current scene.

        Args:
            ray (:obj:'Ray'): The ray to submit.
            callback (Callable): The callback lambda function to execute when resolved.
                function signature: void(Ray, RayQueryResult)
        """
    pass
class Ray():
    """
    Ray represents a ray in 3D space.
    """
    def __eq__(self, arg0: Ray) -> bool: ...
    def __init__(self, origin: object, direction: object, min_t: float = 0.0, max_t: float = inf, adjust_for_section: bool = True) -> None: 
        """
        A ray is defined by an origin point, a direction vector, and minimum and maximum distances along the ray.
        The ray can optionally be adjusted to fit within a specific section of space.

        Args:
            origin (Vec3): The origin point of the ray.
            direction (Vec3): The direction vector of the ray.
            min_t (float, optional): The minimum distance along the ray. Defaults to 0.0.
            max_t (float, optional): The maximum distance along the ray. Defaults to positive infinity.
            adjust_for_section (bool, optional): Whether to adjust the ray to fit within a specific section of space.
                Defaults to True.
        """
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    @property
    def forward(self) -> object:
        """
        direction of the ray

        :type: object
        """
    @forward.setter
    def forward(self, arg1: object) -> None:
        """
        direction of the ray
        """
    @property
    def max_t(self) -> float:
        """
        t value at end of ray

        :type: float
        """
    @max_t.setter
    def max_t(self, arg1: float) -> None:
        """
        t value at end of ray
        """
    @property
    def min_t(self) -> float:
        """
        t value of start of ray

        :type: float
        """
    @min_t.setter
    def min_t(self, arg1: float) -> None:
        """
        t value of start of ray
        """
    @property
    def origin(self) -> object:
        """
        origin of the ray

        :type: object
        """
    @origin.setter
    def origin(self, arg1: object) -> None:
        """
        origin of the ray
        """
    __hash__ = None
    pass
class RayQueryResult():
    def __init__(self) -> None: 
        """
        Create a new RayQueryResult
        """
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def get_target_usd_path(self) -> str: 
        """
        This function returns the usd path of geometry that was hit.

        Return:
            str: Usd path of object that is the target, or an empty string if nothing was hit
        """
    @property
    def hit_position(self) -> object:
        """
        position of hit

        :type: object
        """
    @property
    def hit_t(self) -> float:
        """
        t value of hit position

        :type: float
        """
    @property
    def instance_id(self) -> int:
        """
        instance id

        :type: int
        """
    @property
    def normal(self) -> object:
        """
        normal of geometry at hit point

        :type: object
        """
    @property
    def primitive_id(self) -> int:
        """
        primitive id

        :type: int
        """
    @property
    def valid(self) -> bool:
        """
        indicates whether result is valid

        :type: bool
        """
    pass
class Result():
    """
                Result stat code for raycast query.
            

    Members:

      SUCCESS : The operation was successful

      INVALID_PARAMETER : The parameter provided is invalid

      PARAMETER_IS_NULL : The parameter is a null value

      RAYCAST_SEQUENCE_DOES_NOT_EXIST : The raycast sequence does not exist

      RAYCAST_QUERY_MANAGER_DOES_NOT_EXIT : The raycast query manager does not exist

      RAYCAST_SEQUENCE_ADDITION_FAILED : The addition of the raycast sequence failed
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
    INVALID_PARAMETER: omni.kit.raycast.query._omni_kit_raycast_query.Result # value = <Result.INVALID_PARAMETER: 1>
    PARAMETER_IS_NULL: omni.kit.raycast.query._omni_kit_raycast_query.Result # value = <Result.PARAMETER_IS_NULL: 2>
    RAYCAST_QUERY_MANAGER_DOES_NOT_EXIT: omni.kit.raycast.query._omni_kit_raycast_query.Result # value = <Result.RAYCAST_QUERY_MANAGER_DOES_NOT_EXIT: 4>
    RAYCAST_SEQUENCE_ADDITION_FAILED: omni.kit.raycast.query._omni_kit_raycast_query.Result # value = <Result.RAYCAST_SEQUENCE_ADDITION_FAILED: 5>
    RAYCAST_SEQUENCE_DOES_NOT_EXIST: omni.kit.raycast.query._omni_kit_raycast_query.Result # value = <Result.RAYCAST_SEQUENCE_DOES_NOT_EXIST: 3>
    SUCCESS: omni.kit.raycast.query._omni_kit_raycast_query.Result # value = <Result.SUCCESS: 0>
    __members__: dict # value = {'SUCCESS': <Result.SUCCESS: 0>, 'INVALID_PARAMETER': <Result.INVALID_PARAMETER: 1>, 'PARAMETER_IS_NULL': <Result.PARAMETER_IS_NULL: 2>, 'RAYCAST_SEQUENCE_DOES_NOT_EXIST': <Result.RAYCAST_SEQUENCE_DOES_NOT_EXIST: 3>, 'RAYCAST_QUERY_MANAGER_DOES_NOT_EXIT': <Result.RAYCAST_QUERY_MANAGER_DOES_NOT_EXIT: 4>, 'RAYCAST_SEQUENCE_ADDITION_FAILED': <Result.RAYCAST_SEQUENCE_ADDITION_FAILED: 5>}
    pass
def acquire_raycast_query_interface(*args, **kwargs) -> typing.Any:
    """
    This function returns the RaycastQuery interface object to use.

    Return:
        :obj:'IRaycastQuery': RaycastQuery interface object.
    """
