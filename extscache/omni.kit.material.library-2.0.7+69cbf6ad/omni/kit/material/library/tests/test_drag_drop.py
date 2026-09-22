import os
import unittest
import pathlib
import shutil
import tempfile
import carb
import omni.kit.test
from pxr import UsdShade
from omni.kit import ui_test
from omni.kit.test_suite.helpers import wait_stage_loading
from omni.kit.ui_test import Vec2
from .test_helper import TestMouseUIHelper


PRIM_PATH = "/World/Cube"

class TestMaterialDragDrop(TestMouseUIHelper):
    # Before running each test
    async def setUp(self):
        await super().setUp()

    # After running each test
    async def tearDown(self):
        await super().tearDown()

    async def test_material_drag_drop_preview(self, index=1, material_name="OmniPBR"):
        from omni.kit.window.content_browser.test_helper import ContentBrowserTestHelper

        usd_context = omni.usd.get_context()
        test_file_path = self._test_path.joinpath("usd/cube.usda").absolute()
        test_material_path = self._test_path.joinpath(f"mtl/{material_name}.mdl").absolute()
        await usd_context.open_stage_async(str(test_file_path))
        await wait_stage_loading()

        # get cube prim
        stage = omni.usd.get_context().get_stage()
        cube_prim = stage.GetPrimAtPath(PRIM_PATH)

        # content_browser to "test_material_path" path
        async with ContentBrowserTestHelper() as content_browser_helper:
            await content_browser_helper.toggle_grid_view_async(False)
            await content_browser_helper.navigate_to_async(str(test_material_path))
            mat_item = await content_browser_helper.get_treeview_item_async(material_name + ".mdl")
        await ui_test.human_delay(50)

        # select cube prim
        usd_context.get_selection().set_selected_prim_paths([PRIM_PATH], True)
        await ui_test.human_delay(10)

        # check bound material
        bound_material, _ = UsdShade.MaterialBindingAPI(cube_prim).ComputeBoundMaterial()
        self.assertTrue(bound_material.GetPrim().IsValid() == False)

        # get subid's
        subid_list = []
        def have_subids(id_list):
            nonlocal subid_list
            subid_list = id_list

        await omni.kit.material.library.get_subidentifier_from_mdl(mdl_file=str(test_material_path), on_complete_fn=have_subids)

        # get UI widgets
        preview_widget = ui_test.find("Property//Frame/**/Button[*].identifier=='preview_drop_target'").widget

        # do drag/drop
        # fixme - as TreeView cannot get items position, use magic number for 1st icon position
        source_pos = (mat_item.position.x, mat_item.position.y)
        dest_pos = (preview_widget.screen_position_x+20, preview_widget.screen_position_y+20)
        await self._simulate_mouse([(carb.input.MouseEventType.MOVE, source_pos[0], source_pos[1]),
                                   (carb.input.MouseEventType.LEFT_BUTTON_DOWN, 0, 0)])
        await self._simulate_mouse_steps(source_pos, dest_pos)
        await self._simulate_mouse([(carb.input.MouseEventType.LEFT_BUTTON_UP, 0, 0)])
        await ui_test.human_delay()

        # select cube prim
        usd_context.get_selection().set_selected_prim_paths([PRIM_PATH], True)
        await ui_test.human_delay(10)

        # check bound material
        bound_material, _ = UsdShade.MaterialBindingAPI(cube_prim).ComputeBoundMaterial()
        self.assertTrue(bound_material.GetPrim().IsValid() == True)
        self.assertTrue(bound_material.GetPrim().GetPrimPath().pathString == f"/World/Looks/{material_name}")


    async def test_material_drag_drop_preview_multi(self):
        await self.test_material_drag_drop_preview(0, "OmniHair")


    async def test_material_drag_drop_combo(self, index=1, material_name="OmniPBR"):
        from omni.kit.window.content_browser.test_helper import ContentBrowserTestHelper

        usd_context = omni.usd.get_context()
        test_file_path = self._test_path.joinpath("usd/cube.usda").absolute()
        test_material_path = self._test_path.joinpath(f"mtl/{material_name}.mdl").absolute()
        await usd_context.open_stage_async(str(test_file_path))
        await wait_stage_loading()

        # get cube prim
        stage = omni.usd.get_context().get_stage()
        cube_prim = stage.GetPrimAtPath(PRIM_PATH)

        # content_browser to "test_material_path" path
        async with ContentBrowserTestHelper() as content_browser_helper:
            await content_browser_helper.toggle_grid_view_async(False)
            await content_browser_helper.navigate_to_async(str(test_material_path))
            mat_item = await content_browser_helper.get_treeview_item_async(material_name + ".mdl")
        await ui_test.human_delay(50)

        # select cube prim
        usd_context.get_selection().set_selected_prim_paths([PRIM_PATH], True)
        await ui_test.human_delay(10)

        # check bound material
        bound_material, _ = UsdShade.MaterialBindingAPI(cube_prim).ComputeBoundMaterial()
        self.assertTrue(bound_material.GetPrim().IsValid() == False)

        # get subid's
        subid_list = []
        def have_subids(id_list):
            nonlocal subid_list
            subid_list = id_list

        await omni.kit.material.library.get_subidentifier_from_mdl(mdl_file=str(test_material_path), on_complete_fn=have_subids)

        # get UI widgets
        string_widget = ui_test.find("Property//Frame/**/StringField[*].identifier=='bound_prim_field'").widget

        # do drag/drop
        # fixme - string_widget.screen_position_y is wrong?
        source_pos = (mat_item.position.x, mat_item.position.y)
        dest_pos = (string_widget.screen_position_x + (string_widget.computed_content_width/2), string_widget.screen_position_y + 46)
        await self._simulate_mouse([(carb.input.MouseEventType.MOVE, source_pos[0], source_pos[1]),
                                   (carb.input.MouseEventType.LEFT_BUTTON_DOWN, 0, 0)])
        await self._simulate_mouse_steps(source_pos, dest_pos)
        await self._simulate_mouse([(carb.input.MouseEventType.LEFT_BUTTON_UP, 0, 0)])
        await ui_test.human_delay()

        if len(subid_list)> 1:
            # material has subid and dialog is shown
            create_widget = self._inspector_query.find_widget("Create Material/Frame[0]/VStack[5]/HStack[1]/Button")
            await self._simulate_mouse([(carb.input.MouseEventType.MOVE,
                                        create_widget.screen_position_x+create_widget.computed_content_width/2,
                                        create_widget.screen_position_y+create_widget.computed_content_height/2),
                                       (carb.input.MouseEventType.LEFT_BUTTON_DOWN, 0, 0),
                                       (carb.input.MouseEventType.LEFT_BUTTON_UP, 0, 0)])
            await ui_test.human_delay()

        # select cube prim
        usd_context.get_selection().set_selected_prim_paths([PRIM_PATH], True)
        await ui_test.human_delay(10)

        # check bound material
        bound_material, _ = UsdShade.MaterialBindingAPI(cube_prim).ComputeBoundMaterial()
        self.assertTrue(bound_material.GetPrim().IsValid() == True)
        self.assertTrue(bound_material.GetPrim().GetPrimPath().pathString == f"/World/Looks/{material_name}")


    async def test_material_drag_drop_combo_multi(self):
        await self.test_material_drag_drop_combo(0, "OmniHair")


    async def test_material_drag_drop_prim(self, index=1, material_name="OmniPBR"):
        from omni.kit.window.content_browser.test_helper import ContentBrowserTestHelper
        from omni.kit.viewport.utility import get_active_viewport_window, get_ui_position_for_prim

        viewport_window = get_active_viewport_window()

        usd_context = viewport_window.viewport_api.usd_context
        test_file_path = self._test_path.joinpath("usd/cube.usda").absolute()
        test_material_path = self._test_path.joinpath(f"mtl/{material_name}.mdl").absolute()
        await usd_context.open_stage_async(str(test_file_path))
        await wait_stage_loading()

        # Make sure the layout and any resizes have processed
        for _ in range(2):
            await omni.kit.app.get_app().next_update_async()

        # get cube prim
        stage = usd_context.get_stage()
        cube_prim = stage.GetPrimAtPath(PRIM_PATH)

        # content_browser to "test_material_path" path
        async with ContentBrowserTestHelper() as content_browser_helper:
            await content_browser_helper.toggle_grid_view_async(False)
            await content_browser_helper.navigate_to_async(str(test_material_path))
            mat_item = await content_browser_helper.get_treeview_item_async(material_name + ".mdl")
        await ui_test.human_delay(50)

        # select cube prim
        usd_context.get_selection().set_selected_prim_paths([PRIM_PATH], True)
        await ui_test.human_delay(10)

        # check bound material
        bound_material, _ = UsdShade.MaterialBindingAPI(cube_prim).ComputeBoundMaterial()
        self.assertTrue(bound_material.GetPrim().IsValid() == False)

        # get subid's
        subid_list = []
        def have_subids(id_list):
            nonlocal subid_list
            subid_list = id_list

        await omni.kit.material.library.get_subidentifier_from_mdl(mdl_file=str(test_material_path), on_complete_fn=have_subids)

        # get prim x,y
        prim_ui_pos, valid = get_ui_position_for_prim(viewport_window, PRIM_PATH)
        self.assertTrue(bool(valid))

        # do drag/drop
        # fixme - as TreeView cannot get items position, use magic number for 1st icon position
        source_pos = (mat_item.position.x, mat_item.position.y)
        await self._simulate_mouse([(carb.input.MouseEventType.MOVE, source_pos[0], source_pos[1]),
                                   (carb.input.MouseEventType.LEFT_BUTTON_DOWN, 0, 0)])
        await self._simulate_mouse_steps(source_pos, prim_ui_pos)
        await self._simulate_mouse([(carb.input.MouseEventType.LEFT_BUTTON_UP, 0, 0)])
        await ui_test.human_delay(10)

        # select cube prim
        usd_context.get_selection().set_selected_prim_paths([PRIM_PATH], True)
        await ui_test.human_delay(10)

        # check bound material
        bound_material, _ = UsdShade.MaterialBindingAPI(cube_prim).ComputeBoundMaterial()
        self.assertTrue(bound_material.GetPrim().IsValid() == True)
        self.assertTrue(bound_material.GetPrim().GetPrimPath().pathString == f"/World/Looks/{material_name}")


    async def test_material_drag_drop_prim_multi(self):
        await self.test_material_drag_drop_prim(0, "OmniHair")

    def _write_mdl(self, output_path, good_file):
        with open(output_path, mode='w') as f:
            f.write("mdl 1.6;\n")
            f.write("\n")
            f.write("import ::df::*;\n")
            f.write("import ::tex::*;\n")
            f.write("import ::math::*;\n")
            f.write("import ::state::*;\n")
            f.write("import ::anno::*;\n")
            f.write("\n")
            f.write("\n")
            f.write("export material BadMaterial(\n")
            f.write("    float scale = 1.0\n")
            f.write(")\n")
            f.write("= material(\n")
            f.write("    surface: material_surface(\n")
            f.write("        scattering: df::diffuse_reflection_bsdf(\n")
            f.write("            tint: color(0.25, 0.5, 0.75)")
            if good_file:
                f.write(",")
            f.write("\n")
            f.write("            roughness: 1.0\n")
            f.write("        )\n")
            f.write("    )\n")
            f.write(");\n")
            f.close()

    async def test_material_drag_drop_bad_mdl(self):
        from omni.kit.window.content_browser.test_helper import ContentBrowserTestHelper
        from omni.kit.viewport.utility import get_active_viewport_window, get_ui_position_for_prim

        viewport_window = get_active_viewport_window()

        usd_context = viewport_window.viewport_api.usd_context
        test_file_path = self._test_path.joinpath("usd/cube.usda").absolute()
        await usd_context.open_stage_async(str(test_file_path))
        await wait_stage_loading()

        # Make sure the layout and any resizes have processed
        for _ in range(2):
            await omni.kit.app.get_app().next_update_async()

        # get cube prim
        stage = usd_context.get_stage()
        cube_prim = stage.GetPrimAtPath(PRIM_PATH)

        tmpdir = tempfile.mkdtemp()
        try:
            # material file path
            test_material_path = str(tmpdir).replace('\\', '/') + "/badfile.mdl"

            # write mdl with errors
            self._write_mdl(test_material_path, good_file=False)

            # content_browser to "tmpdir" path
            async with ContentBrowserTestHelper() as content_browser_helper:
                await content_browser_helper.toggle_grid_view_async(False)
                await content_browser_helper.navigate_to_async(tmpdir)
                await ui_test.human_delay(10)

            # select cube prim
            usd_context.get_selection().set_selected_prim_paths([PRIM_PATH], True)
            await ui_test.human_delay(10)

            # verify no bound material
            bound_material, _ = UsdShade.MaterialBindingAPI(cube_prim).ComputeBoundMaterial()
            self.assertTrue(bound_material.GetPrim().IsValid() == False)

            # get prim x,y from viewport
            prim_ui_pos, valid = get_ui_position_for_prim(viewport_window, PRIM_PATH)
            self.assertTrue(bool(valid))

            # do drag/drop
            async with ContentBrowserTestHelper() as content_browser_helper:
                await content_browser_helper.drag_and_drop_tree_view(test_material_path, drag_target=Vec2(prim_ui_pos[0], prim_ui_pos[1]))
                await ui_test.human_delay(10)

            # verify no bound material, as mdl is bad
            bound_material, _ = UsdShade.MaterialBindingAPI(cube_prim).ComputeBoundMaterial()
            self.assertTrue(bound_material.GetPrim().IsValid() == False)

            # write mdl without errors
            self._write_mdl(test_material_path, good_file=True)

            # do drag/drop
            async with ContentBrowserTestHelper() as content_browser_helper:
                await content_browser_helper.drag_and_drop_tree_view(test_material_path, drag_target=Vec2(prim_ui_pos[0], prim_ui_pos[1]))
                await ui_test.human_delay(10)

            # verify bound material as mdl is error free
            bound_material, _ = UsdShade.MaterialBindingAPI(cube_prim).ComputeBoundMaterial()
            self.assertTrue(bound_material.GetPrim().IsValid() == True)
            self.assertTrue(bound_material.GetPrim().GetPrimPath().pathString == f"/World/Looks/BadMaterial")

            await ui_test.human_delay(10)

        finally:
            # cleanup
            shutil.rmtree(tmpdir, ignore_errors=True)

