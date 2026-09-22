from pxr import Gf
import carb
import omni.anim.navigation.core as nav
from isaacsim.anim.robot.utils import simplify_3d_points


class PathPlanner:
    """
    Base class for all path planners.
    Default implementation returns a straight line path between the start and end points.
    """

    def get_path_points(self, start: Gf.Vec3d, end: Gf.Vec3d, agent_radius=0.5) -> list[Gf.Vec3d]:
        return [start, end]


class NavMeshPathPlanner(PathPlanner):
    """
    Path planner that uses the navmesh
    It finds the shortest path between the start and end points while avoiding static obstacles.
    """

    def __init__(self):
        self._inavigation = nav.acquire_interface()

    def get_path_points(self, start: Gf.Vec3d, end: Gf.Vec3d, agent_radius=0.5) -> list[Gf.Vec3d] | None:
        navmesh = self._inavigation.get_navmesh()
        if navmesh is None:
            carb.log_error("Navmesh does NOT exist")
            return None
        path = navmesh.query_shortest_path(start, end, agent_radius=agent_radius)
        if path is None:
            carb.log_error("A valid path between " + str(start) + " and " + str(end) + " does not exist.")
            return None
        # Simplify the path to reduce the number of points if they are on the same line
        return simplify_3d_points(path.get_points(), 0.01)
