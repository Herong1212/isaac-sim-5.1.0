"""pybind11 omni.meshraycast bindings"""
from __future__ import annotations
import omni.kit.mesh.raycast._meshraycast
import typing
import carb._carb
import carb.events._events

__all__ = [
    "BoundResult",
    "BvhRefreshRate",
    "CurveTessellateResult",
    "HitResult",
    "IMeshRaycast",
    "OverlapVerticesEntry",
    "RaycastContext",
    "RaycastEventType",
    "acquire_mesh_raycast_interface",
    "release_mesh_raycast_interface"
]


class BoundResult():
    @property
    def distance(self) -> float:
        """
        :type: float
        """
    @property
    def meshIndex(self) -> int:
        """
        :type: int
        """
    pass
class BvhRefreshRate():
    """
            BVH Refresh Interval.
            

    Members:

      SLOW

      FAST
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
    FAST: omni.kit.mesh.raycast._meshraycast.BvhRefreshRate # value = <BvhRefreshRate.FAST: 1>
    SLOW: omni.kit.mesh.raycast._meshraycast.BvhRefreshRate # value = <BvhRefreshRate.SLOW: 0>
    __members__: dict # value = {'SLOW': <BvhRefreshRate.SLOW: 0>, 'FAST': <BvhRefreshRate.FAST: 1>}
    pass
class CurveTessellateResult():
    @property
    def positions(self) -> typing.Any:
        """
        :type: typing.Any
        """
    @property
    def tangents(self) -> typing.Any:
        """
        :type: typing.Any
        """
    pass
class HitResult():
    @property
    def face_index(self) -> int:
        """
        :type: int
        """
    @property
    def meshIndex(self) -> int:
        """
        :type: int
        """
    @property
    def mesh_index(self) -> int:
        """
        :type: int
        """
    @property
    def normal(self) -> carb._carb.Float3:
        """
        :type: carb._carb.Float3
        """
    @property
    def position(self) -> carb._carb.Float3:
        """
        :type: carb._carb.Float3
        """
    pass
class IMeshRaycast():
    def closestRaycast(self, origin: carb._carb.Float3, dir: carb._carb.Float3, dist: float, context: RaycastContext = None) -> HitResult: ...
    def closestRaycastBound(self, origin: carb._carb.Float3, dir: carb._carb.Float3, dist: float, context: RaycastContext = None) -> BoundResult: ...
    def closestRaycastMesh(self, arg0: str, arg1: carb._carb.Float3, arg2: carb._carb.Float3, arg3: float, arg4: bool) -> HitResult: ...
    def create_context(self) -> RaycastContext: ...
    def destroy_context(self, arg0: RaycastContext) -> None: ...
    def getFloodPoints(self, arg0: str, arg1: float, arg2: bool) -> dict: ...
    def get_bvh_refresh_rate(self) -> BvhRefreshRate: ...
    def get_mesh_path_from_index(self, arg0: int) -> str: ...
    def get_mesh_paths(self) -> typing.List[str]: ...
    def get_mesh_raycast_event_stream(self) -> carb.events._events.IEventStream: ...
    def get_vertex_local_positions(self, arg0: str, arg1: typing.List[int]) -> typing.List[carb._carb.Float3]: ...
    def overlap_vertices(self, origin: carb._carb.Float3, radius: float, context: RaycastContext = None) -> typing.List[OverlapVerticesEntry]: ...
    @staticmethod
    def sample_curve_segment_at_t(*args, **kwargs) -> typing.Any: ...
    def set_allowed_mesh_paths(self, paths: typing.List[str], context: RaycastContext = None) -> None: ...
    def set_bvh_refresh_rate(self, arg0: BvhRefreshRate, arg1: bool) -> None: ...
    def set_disallowed_mesh_paths(self, paths: typing.List[str], include_descendents: bool, context: RaycastContext = None) -> None: ...
    def set_hit_filter_fn(self, fn: typing.Callable[[str], bool], context: RaycastContext = None) -> None: ...
    def spherecast(self, origin: carb._carb.Float3, dir: carb._carb.Float3, radius: float, dist: float, context: RaycastContext = None) -> typing.List[int]: ...
    def tessellate_curve(self, arg0: str, arg1: int, arg2: bool) -> typing.List[CurveTessellateResult]: ...
    pass
class OverlapVerticesEntry():
    @property
    def faceIndices(self) -> typing.List[int]:
        """
        :type: typing.List[int]
        """
    @property
    def meshIndex(self) -> int:
        """
        :type: int
        """
    @property
    def vertexIndices(self) -> typing.List[int]:
        """
        :type: typing.List[int]
        """
    pass
class RaycastContext():
    pass
class RaycastEventType():
    """
            Raycast Event Type.
            

    Members:

      BVH_REBUILT
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
    BVH_REBUILT: omni.kit.mesh.raycast._meshraycast.RaycastEventType # value = <RaycastEventType.BVH_REBUILT: 0>
    __members__: dict # value = {'BVH_REBUILT': <RaycastEventType.BVH_REBUILT: 0>}
    pass
def acquire_mesh_raycast_interface(plugin_name: str = None, library_path: str = None) -> IMeshRaycast:
    pass
def release_mesh_raycast_interface(arg0: IMeshRaycast) -> None:
    pass
