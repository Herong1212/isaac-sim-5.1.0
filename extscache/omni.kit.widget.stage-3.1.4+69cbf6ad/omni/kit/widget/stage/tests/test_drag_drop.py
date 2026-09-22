import pathlib
import omni.kit.test
import carb
import omni.kit.undo

from pxr import UsdShade, Sdf, Gf
from omni.ui.tests.test_base import OmniUiTest
from omni.kit import ui_test
from omni.kit.test_suite.helpers import arrange_windows, open_stage, wait_stage_loading, get_test_data_path
from omni.kit.window.content_browser.test_helper import ContentBrowserTestHelper


class TestStageDragDrop(OmniUiTest):
    async def setUp(self):
        await super().setUp()
        await arrange_windows()
        extension_path = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
        self._test_path = pathlib.Path(extension_path).joinpath("data").joinpath("tests")

    # After running each test
    async def tearDown(self):
        await super().tearDown()
        carb.settings.get_settings().set( "/persistent/app/stage/movePrimInPlace", 1)

    async def test_prim_reparent(self):
        usd_context = omni.usd.get_context()
        await usd_context.new_stage_async()
        stage = usd_context.get_stage()
        stage.DefinePrim("/World2", "Xform")
        stage.DefinePrim("/cube", "Cube")

        await ui_test.human_delay()

        stage_window = ui_test.find("Stage")
        await stage_window.focus()
        stage_window.window._stage_widget._tree_view.root_visible=True

        await ui_test.human_delay()

        stage_tree = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
        absolute_prim_item = stage_tree.find("**/Label[*].text=='Root:'")
        world_prim_item = stage_tree.find("**/Label[*].text=='World2'")
        cube_prim_item = stage_tree.find("**/Label[*].text=='cube'")
        self.assertTrue(absolute_prim_item)
        self.assertTrue(cube_prim_item)
        self.assertTrue(world_prim_item)

        await cube_prim_item.drag_and_drop(world_prim_item.center)
        await ui_test.human_delay()
        self.assertTrue(stage.GetPrimAtPath("/World2/cube"))
        self.assertFalse(stage.GetPrimAtPath("/cube"))

        cube_prim_item = stage_tree.find("**/Label[*].text=='cube'")
        self.assertTrue(cube_prim_item)
        await cube_prim_item.drag_and_drop(absolute_prim_item.center)
        await ui_test.human_delay()
        self.assertFalse(stage.GetPrimAtPath("/World2/cube"))
        self.assertTrue(stage.GetPrimAtPath("/cube"))

    async def test_material_drag_drop_preview(self):
        await arrange_windows(hide_viewport=True)

        usd_context = omni.usd.get_context()
        test_file_path = self._test_path.joinpath("usd/cube.usda").absolute()
        test_material_path = self._test_path.joinpath("mtl/mahogany_floorboards.mdl").absolute()
        await usd_context.open_stage_async(str(test_file_path))
        await ui_test.human_delay()

        # get cube prim
        stage = omni.usd.get_context().get_stage()
        world_prim = stage.GetPrimAtPath("/World")
        cube_prim = stage.GetPrimAtPath("/World/Cube")

        # select cube prim to expand the stage list...
        usd_context.get_selection().set_selected_prim_paths(["/World/Cube"], True)
        await ui_test.human_delay()
        usd_context.get_selection().clear_selected_prim_paths()
        await ui_test.human_delay()

        # check bound material
        bound_material, _ = UsdShade.MaterialBindingAPI(cube_prim).ComputeBoundMaterial()
        self.assertFalse(bound_material.GetPrim().IsValid())

        # drag/drop
        async with ContentBrowserTestHelper() as content_browser_helper:
            stage_window = ui_test.find("Stage")
            drag_target = stage_window.position + ui_test.Vec2(stage_window.size.x / 2, stage_window.size.y - 32)
            await content_browser_helper.drag_and_drop_tree_view(str(test_material_path), drag_target=drag_target)
        # select new material prim
        mahogany_prim = stage.GetPrimAtPath("/World/Looks/mahogany_floorboards")
        self.assertTrue(mahogany_prim.GetPrim().IsValid())
        await ui_test.human_delay()

        # check /World isn't bound
        bound_material, _ = UsdShade.MaterialBindingAPI(world_prim).ComputeBoundMaterial()
        self.assertFalse(bound_material.GetPrim().IsValid())

        # check /World/Cube isn't bound
        bound_material, _ = UsdShade.MaterialBindingAPI(cube_prim).ComputeBoundMaterial()
        self.assertFalse(bound_material.GetPrim().IsValid())

        # drag/drop
        async with ContentBrowserTestHelper() as content_browser_helper:
            stage_tree = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
            for widget in stage_tree.find_all("**/Label[*].text=='Cube'"):
                await content_browser_helper.drag_and_drop_tree_view(str(test_material_path), drag_target=widget.center)
                break
        # select cube prim
        usd_context.get_selection().set_selected_prim_paths(["/World/Cube"], True)
        await ui_test.human_delay()

        # check bound material
        bound_material, _ = UsdShade.MaterialBindingAPI(cube_prim).ComputeBoundMaterial()

        self.assertTrue(bound_material.GetPrim().IsValid())
        self.assertTrue(bound_material.GetPrim().GetPrimPath().pathString == "/World/Looks/mahogany_floorboards_01")

        # check /World isn't bound
        bound_material, _ = UsdShade.MaterialBindingAPI(world_prim).ComputeBoundMaterial()
        self.assertFalse(bound_material.GetPrim().IsValid())

    async def test_prim_parent_keep_transform(self):
        settings = carb.settings.get_settings()
        settings.set( "/persistent/app/stage/movePrimInPlace", 0)

        await open_stage(get_test_data_path(__name__, "4Lights.usda"))
        await wait_stage_loading()

        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()

        stage_window = ui_test.find("Stage")
        await stage_window.focus()
        stage_window.window._stage_widget._tree_view.root_visible=True

        await ui_test.human_delay()

        stage_tree = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
        target_prim_item = stage_tree.find("**/Label[*].text=='SphereLight_00'")
        cube_prim_item = stage_tree.find("**/Label[*].text=='Cube'")
        self.assertTrue(cube_prim_item)
        self.assertTrue(target_prim_item)

        await cube_prim_item.drag_and_drop(target_prim_item.center)
        await ui_test.human_delay()
        self.assertTrue(stage.GetPrimAtPath("/Stage/SphereLight_00/Cube"))

        self.assertAlmostEqual(Gf.Vec3d(stage.GetPrimAtPath('/Stage/SphereLight_00').GetAttribute('xformOp:translate').Get()), Gf.Vec3d(-107.755989, 13.481207, 94.274811))
        self.assertAlmostEqual(Gf.Vec3d(stage.GetPrimAtPath('/Stage/SphereLight_00/Cube').GetAttribute('xformOp:translate').Get()), Gf.Vec3d(0.0, 0.0, 0.0))

    async def test_prim_parent_inherit_transform(self):
        settings = carb.settings.get_settings()
        settings.set( "/persistent/app/stage/movePrimInPlace", 1)

        await open_stage(get_test_data_path(__name__, "4Lights.usda"))
        await wait_stage_loading()

        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()

        stage_window = ui_test.find("Stage")
        await stage_window.focus()
        stage_window.window._stage_widget._tree_view.root_visible=True

        await ui_test.human_delay()

        stage_tree = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
        target_prim_item = stage_tree.find("**/Label[*].text=='SphereLight_00'")
        cube_prim_item = stage_tree.find("**/Label[*].text=='Cube'")
        self.assertTrue(cube_prim_item)
        self.assertTrue(target_prim_item)

        await cube_prim_item.drag_and_drop(target_prim_item.center)
        await ui_test.human_delay()
        self.assertTrue(stage.GetPrimAtPath("/Stage/SphereLight_00/Cube"))

        self.assertAlmostEqual(Gf.Vec3d(stage.GetPrimAtPath('/Stage/SphereLight_00').GetAttribute('xformOp:translate').Get()), Gf.Vec3d(-107.755989, 13.481207, 94.274811))
        self.assertAlmostEqual(Gf.Vec3d(stage.GetPrimAtPath('/Stage/SphereLight_00/Cube').GetAttribute('xformOp:translate').Get()), Gf.Vec3d(107.755989, -13.481207, -94.274811))

    async def test_prim_parent_ask(self):
        settings = carb.settings.get_settings()
        settings.set( "/persistent/app/stage/movePrimInPlace", 2)

        await open_stage(get_test_data_path(__name__, "4Lights.usda"))
        await wait_stage_loading()

        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()

        stage_window = ui_test.find("Stage")
        await stage_window.focus()
        stage_window.window._stage_widget._tree_view.root_visible=True

        await ui_test.human_delay()

        stage_tree = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
        target_prim_item = stage_tree.find("**/Label[*].text=='SphereLight_00'")
        cube_prim_item = stage_tree.find("**/Label[*].text=='Cube'")
        self.assertTrue(cube_prim_item)
        self.assertTrue(target_prim_item)

        # select "Keep Prim Transform"
        await cube_prim_item.drag_and_drop(target_prim_item.center)
        await ui_test.human_delay(10)
        await ui_test.select_context_menu("Keep Prim Transform", offset=ui_test.Vec2(10, 10))
        await ui_test.human_delay()
        self.assertTrue(stage.GetPrimAtPath("/Stage/SphereLight_00/Cube"))

        self.assertAlmostEqual(Gf.Vec3d(stage.GetPrimAtPath('/Stage/SphereLight_00').GetAttribute('xformOp:translate').Get()), Gf.Vec3d(-107.755989, 13.481207, 94.274811))
        self.assertAlmostEqual(Gf.Vec3d(stage.GetPrimAtPath('/Stage/SphereLight_00/Cube').GetAttribute('xformOp:translate').Get()), Gf.Vec3d(0.0, 0.0, 0.0))

        omni.kit.undo.undo()

        # select "Inherit Parent Transform"
        await cube_prim_item.drag_and_drop(target_prim_item.center)
        await ui_test.human_delay(10)
        await ui_test.select_context_menu("Inherit Parent Transform", offset=ui_test.Vec2(10, 10))
        await ui_test.human_delay()
        self.assertTrue(stage.GetPrimAtPath("/Stage/SphereLight_00/Cube"))

        self.assertAlmostEqual(Gf.Vec3d(stage.GetPrimAtPath('/Stage/SphereLight_00').GetAttribute('xformOp:translate').Get()), Gf.Vec3d(-107.755989, 13.481207, 94.274811))
        self.assertAlmostEqual(Gf.Vec3d(stage.GetPrimAtPath('/Stage/SphereLight_00/Cube').GetAttribute('xformOp:translate').Get()), Gf.Vec3d(107.755989, -13.481207, -94.274811))
