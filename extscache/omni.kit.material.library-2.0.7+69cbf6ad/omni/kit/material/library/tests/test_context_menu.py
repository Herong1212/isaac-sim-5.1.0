import unittest
import pathlib
import carb
import omni.kit.test
from pxr import UsdShade
from omni.ui.tests.test_base import OmniUiTest
from omni.kit import ui_test
from omni.kit.test_suite.helpers import wait_stage_loading
from .test_helper import TestMouseUIHelper


class TestMaterialContextMenu(TestMouseUIHelper):
    # Before running each test
    async def setUp(self):
        await super().setUp()

    # After running each test
    async def tearDown(self):
        await super().tearDown()

    async def test_material_context_menu(self, material_name="OmniPBR"):
        from omni.kit.window.content_browser.test_helper import ContentBrowserTestHelper

        usd_context = omni.usd.get_context()
        test_file_path = self._test_path.joinpath("usd/cube.usda").absolute()
        test_material_path = self._test_path.joinpath(f"mtl/{material_name}.mdl").absolute()

        await usd_context.open_stage_async(str(test_file_path))
        await wait_stage_loading()

        async with ContentBrowserTestHelper() as content_browser_helper:
            await content_browser_helper.toggle_grid_view_async(show_grid_view=False)
            await ui_test.human_delay(50)
            await content_browser_helper.navigate_to_async(str(test_material_path))
            mat_item = await content_browser_helper.get_treeview_item_async(material_name + ".mdl")
        await wait_stage_loading()

        # get subid's
        subid_list = []
        def have_subids(id_list):
            nonlocal subid_list
            subid_list = id_list

        await omni.kit.material.library.get_subidentifier_from_mdl(mdl_file=str(test_material_path), on_complete_fn=have_subids)

        # Select the prim.
        stage = omni.usd.get_context().get_stage()
        usd_context.get_selection().set_selected_prim_paths(["/World/Cube"], True)
        cube_prim = stage.GetPrimAtPath("/World/Cube")

        # check bound material
        bound_material, _ = UsdShade.MaterialBindingAPI(cube_prim).ComputeBoundMaterial()
        self.assertTrue(bound_material.GetPrim().IsValid() == False)

        # right click on material item and get context menu item
        await mat_item.right_click()
        await ui_test.human_delay(10)
        await ui_test.select_context_menu("Bind material to selected prim(s)")

        await wait_stage_loading()
        await ui_test.human_delay(10)
        usd_context.get_selection().set_selected_prim_paths(["/World/Cube"], True)
        await ui_test.human_delay(10)

        # check bound material
        bound_material, _ = UsdShade.MaterialBindingAPI(cube_prim).ComputeBoundMaterial()
        self.assertTrue(bound_material.GetPrim().IsValid() == True)
        self.assertTrue(bound_material.GetPrim().GetPrimPath().pathString == f"/World/Looks/{material_name}")


    async def test_material_context_menu_multi(self):
        await self.test_material_context_menu(material_name="OmniHair")
