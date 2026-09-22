from pathlib import Path
from pxr import Gf

from carb import settings
import omni.kit.app
import omni.kit.commands
import omni.kit.test
import omni.usd
import omni.kit.ui_test as ui_test

from omni.kit.window.content_browser.test_helper import ContentBrowserTestHelper
from ..content_browser_options import ContentBrowserOptions

EXTENSION_FOLDER_PATH = Path(omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__))
TEST_DATA_PATH = EXTENSION_FOLDER_PATH.joinpath("data/tests")


class TestAddFromContent(omni.kit.test.AsyncTestCase):
    """
    Test the functionality of adding a reference to a stage at the average position of the selected prims,
    with and without deleting the selected prims.
    """
    async def setUp(self):
        self.usd_context = omni.usd.get_context()
        await self.usd_context.new_stage_async()

        self.stage = self.usd_context.get_stage()
        self.assertIsNotNone(self.stage)

        self.prim_paths = [self.stage.DefinePrim(f"{self.stage.GetDefaultPrim().GetPath()}/xform{i}", "Xform").GetPath().pathString for i in range(3)]
        positions = [Gf.Vec3d(100, 0, 0), Gf.Vec3d(0, 100, 0), Gf.Vec3d(0, 0, 100)]
        for i in range(3):
            omni.kit.commands.execute("TransformPrimCommand",
                                      path=self.prim_paths[i],
                                      new_transform_matrix=Gf.Matrix4d().SetTranslate(positions[i]))
        self.usd_context.get_selection().set_selected_prim_paths(self.prim_paths, False)

        self.test_file_path = str(TEST_DATA_PATH.joinpath("tests.usda").absolute())
        self.avg_position = (positions[0] + positions[1] + positions[2]) / 3
        self.small_number = 0.00001

    async def tearDown(self):
        pass

    async def test_replace_from_content(self):
        async with ContentBrowserTestHelper() as content_browser_helper:
            await content_browser_helper.navigate_to_async(self.test_file_path)
            await content_browser_helper.select_items_async(str(TEST_DATA_PATH), ["tests.usda"])

            usd_item = await content_browser_helper.get_gridview_item_async("tests.usda")
            self.assertTrue(usd_item)

            self.usd_context.get_selection().set_selected_prim_paths(self.prim_paths, True)
            await usd_item.right_click()
            await ui_test.select_context_menu("Replace Current Selection")

            cube = self.stage.GetPrimAtPath("/tests/Cube")
            self.assertTrue(cube.IsValid(), "Prim from file to be added is invalid")
            for path in self.prim_paths:
                self.assertFalse(self.stage.GetPrimAtPath(path).IsValid(), "Prim that should have been replaced is still valid")
            prim_position = omni.usd.get_world_transform_matrix(cube).ExtractTranslation()
            self.assertTrue(Gf.IsClose(self.avg_position, prim_position, self.small_number), f"New prim is located at {prim_position} when it should be at {self.avg_position}")

    async def test_add_from_content(self):
        async with ContentBrowserTestHelper() as content_browser_helper:
            await content_browser_helper.navigate_to_async(self.test_file_path)
            await content_browser_helper.select_items_async(str(TEST_DATA_PATH), ["tests.usda"])

            usd_item = await content_browser_helper.get_gridview_item_async("tests.usda")
            self.assertTrue(usd_item)

            self.usd_context.get_selection().set_selected_prim_paths(self.prim_paths, True)
            await usd_item.right_click()
            await ui_test.select_context_menu("Add at Current Selection")

            cube = self.stage.GetPrimAtPath("/tests/Cube")
            self.assertTrue(cube.IsValid(), "Prim from file to be added is invalid")
            for path in self.prim_paths:
                self.assertTrue(self.stage.GetPrimAtPath(path).IsValid(), "Prim that should still exist is now invalid")
            prim_position = omni.usd.get_world_transform_matrix(cube).ExtractTranslation()
            self.assertTrue(Gf.IsClose(self.avg_position, prim_position, self.small_number), f"New prim is located at {prim_position} when it should be at {self.avg_position}")

            # Clear selection
            self.usd_context.get_selection().set_selected_prim_paths([], True)
            await ui_test.emulate_mouse_click()
            await usd_item.right_click()
            await ui_test.select_context_menu("Add at Current Selection")

            # FIXME: Calls it directly without simulating ray query.
            self.assertFalse(self.stage.GetPrimAtPath("/tests_01"))
            ContentBrowserOptions._add_to_stage_using_vp2_helper(
                self.usd_context,
                self.stage,
                self.test_file_path,
                settings.get_settings(),
                "/OmniverseKit_Persp",
                None
            )
            self.assertTrue(self.stage.GetPrimAtPath("/tests_01"))
