import carb
import omni.anim.navigation.core as nav
from .carb_util import CarbUtil
from omni.kit.scripting.scripts.script_manager import ScriptManager
import omni.usd
import numpy as np
from typing import List, Optional, Union, Tuple
from pxr import Sdf

"""
------------------------Utility for Simulation modules such as NavMesh------------------------
"""


class SimulationUtil:
    @staticmethod
    def is_the_same_point(
        point1: Union[carb.Float3, List[float], Tuple[float, float, float]],
        point2: Union[carb.Float3, List[float], Tuple[float, float, float]],
        tol: float = 0.01,
    ) -> bool:
        """Check if two 3D points are within a specified tolerance of each other.

        Accepts either `carb.Float3` or sequence-like (x, y, z) inputs.

        Args:
            point1: First point to compare
            point2: Second point to compare
            tol: Distance tolerance (default: 0.01)

        Returns:
            bool: True if points are within tolerance, False otherwise
        """

        def _to_xyz(p) -> Tuple[float, float, float]:
            try:
                return float(p[0]), float(p[1]), float(p[2])
            except Exception:
                return (
                    float(getattr(p, "x", 0.0)),
                    float(getattr(p, "y", 0.0)),
                    float(getattr(p, "z", 0.0)),
                )

        x1, y1, z1 = _to_xyz(point1)
        x2, y2, z2 = _to_xyz(point2)
        dx, dy, dz = x1 - x2, y1 - y2, z1 - z2
        return (dx * dx + dy * dy + dz * dz) ** 0.5 <= tol

    @staticmethod
    def is_the_same_point_2d(
        point1: Union[carb.Float3, List[float], Tuple[float, float]],
        point2: Union[carb.Float3, List[float], Tuple[float, float]],
        tol: float = 0.01,
    ) -> bool:
        """Calculate the 2D distance between two points, ignoring the z-axis.

        Accepts either `carb.Float3` or sequence-like (x, y) inputs.
        """

        def _to_xy(p) -> Tuple[float, float]:
            try:
                return float(p[0]), float(p[1])
            except Exception:
                return float(getattr(p, "x", 0.0)), float(getattr(p, "y", 0.0))

        x1, y1 = _to_xy(point1)
        x2, y2 = _to_xy(point2)
        dx, dy = x1 - x2, y1 - y2
        return (dx * dx + dy * dy) ** 0.5 <= tol

    @staticmethod
    def validate_navmesh_point(point: List[float], tol: Optional[float] = 0.01, agent_radius: Optional[float] = 0.0):
        """Validate if a 3D point is on the navmesh.

        Args:
            point: The 3D point to validate
            tol: Distance tolerance (default: 0.01)

        Returns:
            bool: True if the point is on the navmesh, False otherwise
        """
        point_carb = carb.Float3(point[0], point[1], point[2])
        navmesh = nav.acquire_interface().get_navmesh()
        if navmesh is None:
            carb.log_error("Trying to validate a NavMesh point without a valid NavMesh")
            return False
        closest_point = navmesh.query_closest_point(point_carb, agent_radius=agent_radius)[0]
        if closest_point is None or not SimulationUtil.is_the_same_point(point_carb, closest_point, tol):
            return False
        return True

    @staticmethod
    def validate_navmesh_point_2d(point: List[float], tol: Optional[float] = 0.01, agent_radius: Optional[float] = 0.0):
        """given a 3d point, check whether its 2d projection is on navmesh"""
        point_carb = carb.Float3(point[0], point[1], point[2])
        navmesh = nav.acquire_interface().get_navmesh()
        if navmesh is None:
            carb.log_error("Trying to validate a NavMesh point without a valid NavMesh")
            return False
        closest_point = navmesh.query_closest_point(point_carb, agent_radius=agent_radius)[0]
        if closest_point is None or not SimulationUtil.is_the_same_point_2d(point, closest_point, tol):
            return False
        return True

    @staticmethod
    def get_agent_script_instance_by_path(agent_prim_path: Union[str, Sdf.Path]):
        """Get the agent BehaviorScript instance by the agent prim path"""
        sm = ScriptManager.get_instance()
        for scripts in sm._prim_to_scripts.values():
            # Traverse the script inst list, find the target agent's inst
            for _, inst in scripts.items():
                if inst is not None:
                    if str(inst.prim_path) == str(agent_prim_path):
                        return inst
        return None

    @staticmethod
    def get_current_timecode() -> float:
        """
        get current simulation timecode
        note: the timecode value is bounded by the stage timecode range.
        """

        stage = omni.usd.get_context().get_stage()
        timeline_interface = omni.timeline.get_timeline_interface()
        current_time = timeline_interface.get_current_time()
        current_time_code = stage.GetTimeCodesPerSecond() * current_time
        return current_time_code

    @staticmethod
    def get_navmesh_scope() -> List[Tuple[float, float]]:
        """
        Compute axis-aligned bounds of the current NavMesh in world coordinates.

        Returns:
            List[Tuple[float, float]]: [(x_min, x_max), (y_min, y_max), (z_min, z_max)]

        Notes:
            - Callers commonly use only the first two pairs (XY). The Z range is
              provided for completeness and is currently unused by most callers.
            - Handles missing/empty navmesh gracefully with a minimal zero-sized scope.
        """

        inav = nav.acquire_interface()
        navmesh = inav.get_navmesh() if inav is not None else None
        if navmesh is None:
            carb.log_warn("NavMesh interface not available; returning zero scope around origin.")
            return [(0.0, 0.0), (0.0, 0.0), (0.0, 0.0)]

        try:
            vertices = navmesh.get_draw_triangles(0)
        except Exception as exc:
            carb.log_error(f"Failed to retrieve NavMesh triangles: {exc}")
            return [(0.0, 0.0), (0.0, 0.0), (0.0, 0.0)]

        if not vertices:
            carb.log_warn("NavMesh has no triangles; returning zero scope around origin.")
            return [(0.0, 0.0), (0.0, 0.0), (0.0, 0.0)]

        # Convert to a dense (N, 3) float array robustly (supports carb.Float3 or tuple-like)
        coords = np.empty((len(vertices), 3), dtype=float)
        for idx, v in enumerate(vertices):
            try:
                coords[idx, 0] = float(v[0])
                coords[idx, 1] = float(v[1])
                coords[idx, 2] = float(v[2])
            except Exception:
                coords[idx, 0] = float(getattr(v, "x", 0.0))
                coords[idx, 1] = float(getattr(v, "y", 0.0))
                coords[idx, 2] = float(getattr(v, "z", 0.0))

        x_min, x_max = float(np.min(coords[:, 0])), float(np.max(coords[:, 0]))
        y_min, y_max = float(np.min(coords[:, 1])), float(np.max(coords[:, 1]))
        z_min, z_max = float(np.min(coords[:, 2])), float(np.max(coords[:, 2]))

        # Validate finiteness
        if not np.all(np.isfinite([x_min, x_max, y_min, y_max, z_min, z_max])):
            carb.log_error("Computed non-finite NavMesh bounds; returning zero scope.")
            return [(0.0, 0.0), (0.0, 0.0), (0.0, 0.0)]

        return [(x_min, x_max), (y_min, y_max), (z_min, z_max)]

    # FIXME::more elegent way need to be added
    @staticmethod
    def get_capture_on_play() -> bool:
        """get capture on play setting"""
        result = carb.settings.get_settings().get("/omni/replicator/captureOnPlay")
        return result

    @staticmethod
    def update_xformOp_type(target_xform_type: str) -> str:
        """set the xform type to target value"""
        xformoptype_setting_path = "/persistent/app/primCreation/DefaultXformOpType"
        original_xform_order_setting = SimulationUtil.get_original_xformOp_type()
        carb.settings.get_settings().set(xformoptype_setting_path, target_xform_type)
        return original_xform_order_setting

    @staticmethod
    def get_original_xformOp_type() -> str:
        """get the original xform type"""
        xformoptype_setting_path = "/persistent/app/primCreation/DefaultXformOpType"
        original_xform_order_setting = carb.settings.get_settings().get(xformoptype_setting_path)
        return original_xform_order_setting
