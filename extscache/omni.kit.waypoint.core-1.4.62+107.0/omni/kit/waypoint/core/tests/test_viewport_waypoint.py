from pathlib import Path

import carb
import omni.kit.app
import omni.kit.test
from omni.kit.test_suite.helpers import wait_stage_loading
from omni.kit.waypoint.core import get_instance
from omni.kit.waypoint.core.common import WAYPOINT_ROOT_PRIM_PATH
from omni.kit.waypoint.core.viewport_waypoint import ViewportWaypoint

CURRENT_PATH = Path(__file__).parent
TEST_DATA_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.joinpath("data").joinpath("tests")


class TestViewportWaypoint(omni.kit.test.AsyncTestCase):
    # Before running each test
    async def setUp(self):
        self._ext = get_instance()
        self._context = omni.usd.get_context()
        await self._context.new_stage_async()

    # After running each test
    async def tearDown(self):
        # There are async functions that require a delay.
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        pass

    async def test_1_properties(self):
        waypoint = ViewportWaypoint("Test_Waypoint")
        self.assertEqual(waypoint.name, "Test_Waypoint")
        self.assertEqual(str(waypoint), '"Test_Waypoint"')
        self.assertEqual(repr(waypoint), '"Test_Waypoint"')
        self.assertEqual(waypoint.path, "/Viewport_Waypoints/Test_Waypoint")
        self.assertIsNone(waypoint.thumbnail)
        self.assertIsNone(waypoint.thumbnail_data)
        self.assertIsNone(waypoint.create_time)
        self.assertIsNone(waypoint.created_by)
        self.assertEqual(waypoint.comment, "")

        # This will fail (and give a warning because of missing prim), but should otherwise cause no issue.
        waypoint.recall()

        # NOTE: Using the setter on the name doesn't check the prim or anything, just updates the name and resulting path.
        waypoint.name = "Setter_Name_Waypoint"
        self.assertEqual(str(waypoint), '"Setter_Name_Waypoint"')
        self.assertEqual(waypoint.path, "/Viewport_Waypoints/Setter_Name_Waypoint")

        # Invalid name.
        ret = waypoint.rename("Gar\\bage")
        self.assertFalse(ret)

        # Valid name (but the prim doesn't exist)
        ret = waypoint.rename("Renamed_Waypoint")
        self.assertFalse(ret)
