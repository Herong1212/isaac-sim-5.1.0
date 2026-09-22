import omni.kit.test
import carb
from pxr import Gf

from isaacsim.anim.robot.path_planner import PathPlanner, NavMeshPathPlanner


class TestNavigation:
    def __init__(self, path_points=None):
        self._path_points = path_points or []

    def get_navmesh(self):
        return TestNavMesh(self._path_points)


class TestNavMesh:
    def __init__(self, path_points):
        self._path_points = path_points

    def query_shortest_path(self, start, end, agent_radius=0.0):
        if not self._path_points:
            return None
        return TestPath(self._path_points)


class TestPath:
    def __init__(self, points):
        self._points = points

    def get_points(self):
        return self._points


class TestPathPlanner(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self.start = Gf.Vec3d(0, 0, 0)
        self.end = Gf.Vec3d(1, 1, 0)

    async def test_base_planner(self):
        """Test basic path planner returns direct path."""
        planner = PathPlanner()
        path = planner.get_path_points(self.start, self.end)

        self.assertEqual(len(path), 2)
        self.assertEqual(path[0], self.start)
        self.assertEqual(path[1], self.end)

    async def test_navmesh_planner_path_simplification(self):
        """Test path simplification with collinear points."""
        # Create path with unnecessary intermediate points
        test_points = [
            carb.Float3(0, 0, 0),
            carb.Float3(0.25, 0.25, 0),  # Collinear point
            carb.Float3(0.5, 0.5, 0),  # Collinear point
            carb.Float3(0.75, 0.75, 0),  # Collinear point
            carb.Float3(1, 1, 0),
        ]

        planner = NavMeshPathPlanner()
        planner._inavigation = TestNavigation(test_points)

        path = planner.get_path_points(self.start, self.end)

        # Should be simplified to just start and end points
        self.assertEqual(len(path), 2)
        self.assertEqual(path[0], self.start)
        self.assertEqual(path[-1], self.end)
