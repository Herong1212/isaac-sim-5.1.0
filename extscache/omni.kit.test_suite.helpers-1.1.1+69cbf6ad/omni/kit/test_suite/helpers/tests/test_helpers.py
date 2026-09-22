## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import os

import carb
import omni.kit.material.library
import omni.usd
import omni.kit.commands
from omni.kit import ui_test
from omni.kit.material.library.test_helper import MaterialLibraryTestHelper
from omni.kit.test_suite.helpers import (
    StageEventHandler,
    TestSuiteHelpers,
    arrange_windows,
    build_sdf_asset_frame_dictonary,
    delete_prim_path_children,
    get_prims,
    get_random_material_list,
    get_test_data_path,
    handle_multiple_descendents_dialog,
    open_stage,
    select_prims,
    wait_for_viewport_ready,
    wait_stage_loading,
)
from omni.kit.ui_test import Vec2
from omni.kit.viewport.utility import get_ui_position_for_prim
from omni.kit.window.content_browser.test_helper import ContentBrowserTestHelper
from omni.ui.tests.test_base import OmniUiTest
from pxr import Tf, UsdShade

__all__ = [
    "TestHelpers",
]


class TestHelpers(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        await arrange_windows("Stage", 256)

    # After running each test
    async def tearDown(self):
        await super().tearDown()
        TestSuiteHelpers.stage_event_debug = False
        TestSuiteHelpers.stage_loading_debug = False

    # Test(s)
    async def test_helpers_stageloading(self):
        TestSuiteHelpers.stage_event_debug = True
        TestSuiteHelpers.stage_loading_debug = True

        await open_stage(get_test_data_path(__name__, "bound_shapes.usda"))

        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        to_select = "/World/Cylinder"

        # wait for material to load & UI to refresh
        await wait_stage_loading()

        # select prim
        await select_prims([to_select])
        await ui_test.human_delay()

        # wait for material to load & UI to refresh
        await wait_stage_loading()

    async def test_helpers_stageevent(self):
        stage_event_handler = StageEventHandler("omni.kit.test_suite.helpers.tests")

        await stage_event_handler.reset_stage_event(omni.usd.StageEventType.OPENED)

        menu_widget = ui_test.get_menubar()
        await open_stage(get_test_data_path(__name__, "bound_shapes.usda"))

        await stage_event_handler.wait_for_stage_event()
        del stage_event_handler

    async def test_helpers_multiple_descendents_dialog(self, retries=0):
        viewport_window = await arrange_windows(topleft_width=0)

        ui_test_window = ui_test.find("Viewport")
        await ui_test_window.focus()

        # get single and multi-subid materials
        single_material = None
        multi_material = None
        mdl_list = await omni.kit.material.library.get_mdl_list_async()
        if not mdl_list:
            await ui_test.human_delay(50)
            if retries < 5:
                return await test_helpers_multiple_descendents_dialog(retries+1)
            print(f">> test_helpers_multiple_descendents_dialog: No materials found, skipping test.")
            return

        for mtl_name, mdl_path, submenu in mdl_list:
            if "Presets" in mdl_path or "Base" in mdl_path:
                continue
            if not single_material and not submenu:
                single_material = (mtl_name, mdl_path)
            if not multi_material and submenu:
                multi_material = (mtl_name, mdl_path)

        if not single_material or not multi_material:
            print(f">> test_helpers_multiple_descendents_dialog: failed to find single_material ({single_material}) and/or multi_material ({multi_material})")
            print(f">> test_helpers_multiple_descendents_dialog: mdl_list:{mdl_list}")
            await ui_test.human_delay(50)
            if retries < 5:
                return await test_helpers_multiple_descendents_dialog(retries+1)

        # verify both tests have run
        self.assertTrue(single_material != None)
        self.assertTrue(multi_material != None)

        async def verify_prims(stage, mtl_name, verify_prim_list):
            # verify material
            prim_paths = [p.GetPrimPath().pathString for p in stage.Traverse()]
            self.assertTrue(f"/World/Looks/{mtl_name}" in prim_paths)
            self.assertTrue(f"/World/Looks/{mtl_name}/Shader" in prim_paths)

            # verify bound material
            if verify_prim_list:
                for prim_path in verify_prim_list:
                    prim = stage.GetPrimAtPath(prim_path)
                    bound_material, _ = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()
                    self.assertTrue(bound_material.GetPrim().IsValid() == True)
                    self.assertTrue(bound_material.GetPrim().GetPrimPath().pathString == f"/World/Looks/{mtl_name}")

            # undo
            omni.kit.undo.undo()

            # verify material was removed
            prim_paths = [p.GetPrimPath().pathString for p in stage.Traverse()]
            self.assertFalse(f"/World/Looks/{mtl_name}" in prim_paths)


        async def test_multiple_descendents_mtl(stage, material, multiple_descendents_prim, target_prim, drag_target):
            mtl_name, mdl_path = material

            # drag and drop items from the tree view of content browser
            async with ContentBrowserTestHelper() as content_browser_helper:
                await content_browser_helper.drag_and_drop_tree_view(mdl_path, drag_target=drag_target)

            # use multiple descendents dialog
            await handle_multiple_descendents_dialog(stage, multiple_descendents_prim, target_prim)

            # handle create material dialog
            async with MaterialLibraryTestHelper() as material_library_helper:
                await material_library_helper.handle_create_material_dialog(mdl_path, mtl_name)

            # wait for material to load & UI to refresh
            await wait_stage_loading()

            # verify created/bound prims
            await verify_prims(stage, mtl_name, [target_prim])


        # load stage with multi-descendent prim
        await open_stage(get_test_data_path(__name__, "multi-material-object-cube-component.usda"))
        await wait_stage_loading()

        # test DnD single & multi subid material from Content window to /World/pCube1 targeting each descendant - Create material & Binding
        stage = omni.usd.get_context().get_stage()
        multiple_descendents_prim = "/World/pCube1"
        drag_target, valid = get_ui_position_for_prim(viewport_window, multiple_descendents_prim)
        drag_target = Vec2(drag_target[0], drag_target[1])
        target_prim = "/World/pCube1/front1"
        await test_multiple_descendents_mtl(stage, single_material, multiple_descendents_prim, target_prim, drag_target)
        await test_multiple_descendents_mtl(stage, multi_material, multiple_descendents_prim, target_prim, drag_target)

        # verify delete_prim_path_children and get_prims too...
        stage = omni.usd.get_context().get_stage()
        prim_list = [prim.GetPath().pathString for prim in get_prims(stage) if not omni.usd.is_hidden_type(prim)]
        self.assertTrue("/World/Looks" in prim_list)
        await delete_prim_path_children("/World/Looks/")
        prim_list = [prim.GetPath().pathString for prim in get_prims(stage) if not omni.usd.is_hidden_type(prim)]
        self.assertFalse("/World/Looks/" in prim_list)

    async def test_helpers_assign_material(self):
        # new stage
        usd_context = omni.usd.get_context()
        await usd_context.new_stage_async()
        stage = usd_context.get_stage()

        # setup
        await ui_test.find("Stage").focus()

        # create root prim
        rootname = "/World"
        stage.SetDefaultPrim(stage.DefinePrim(rootname))

        # create Looks folder
        omni.kit.commands.execute("CreatePrim", prim_path="{}/Looks".format(rootname), prim_type="Scope", select_new_prim=True)

        # create material
        kit_folder = carb.tokens.get_tokens_interface().resolve("${kit}")
        omni_pbr_mtl = os.path.normpath(kit_folder + "/mdl/core/Base/OmniPBR.mdl")
        mtl_path = omni.usd.get_stage_next_free_path(stage, "{}/Looks/{}".format(rootname, omni.usd.make_valid_identifier("OmniPBR")), False)
        omni.kit.commands.execute("CreateMdlMaterialPrim", mtl_url=omni_pbr_mtl, mtl_name="OmniPBR", mtl_path=mtl_path)

        # create sphere
        omni.kit.commands.execute("CreatePrimWithDefaultXform", prim_type="Sphere", select_new_prim=True)

        # wait for material to load & UI to refresh
        await wait_stage_loading()

        # select prim
        await select_prims(["/World/Sphere"])

        # expand stage window...
        stage_widget = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True").widget.set_expanded(None, True, True)

        # get prim
        prim = stage.GetPrimAtPath("/World/Sphere")

        # click on context menu item & assign ma
        viewport = ui_test.find("Viewport")
        await viewport.focus()
        await viewport.right_click()
        await ui_test.human_delay(10)
        await ui_test.select_context_menu("Assign Material")

        # assign material
        await ui_test.human_delay()
        async with MaterialLibraryTestHelper() as material_test_helper:
            await material_test_helper.handle_assign_material_dialog(1, 0)

        bound_material, relationship = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()
        strength = UsdShade.MaterialBindingAPI.GetMaterialBindingStrength(relationship)
        self.assertEqual(bound_material.GetPrim().GetPrimPath().pathString, mtl_path)
        self.assertEqual(strength, UsdShade.Tokens.weakerThanDescendants)

        # click on context menu item
        viewport = ui_test.find("Viewport")
        await viewport.focus()
        await viewport.right_click()
        await ui_test.human_delay(10)
        await ui_test.select_context_menu("Assign Material")

        # assign material with different strength
        await ui_test.human_delay()
        async with MaterialLibraryTestHelper() as material_test_helper:
            await material_test_helper.handle_assign_material_dialog(1, 1)

        bound_material, relationship = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()
        strength = UsdShade.MaterialBindingAPI.GetMaterialBindingStrength(relationship)
        self.assertEqual(bound_material.GetPrim().GetPrimPath().pathString, mtl_path)
        self.assertEqual(strength, UsdShade.Tokens.strongerThanDescendants)

    async def test_helpers_random_material_list(self):
        mdl_list = await get_random_material_list()
        self.assertGreater(len(mdl_list), 2)

    async def test_helpers_wait_for_viewport_ready(self):
        await wait_for_viewport_ready()

    async def test_helpers_build_sdf_asset_frame_dictonary(self):
        await arrange_windows("Stage", 64)
        await open_stage(get_test_data_path(__name__, "bound_shapes.usda"))

        # select prim
        await select_prims(["/World/Looks/OmniPBR"])

        # wait for material to load & UI to refresh
        await wait_stage_loading()

        # open all CollapsableFrames
        for frame in ui_test.find_all("Property//Frame/**/CollapsableFrame[*]"):
            if frame.widget.title != "Raw USD Properties":
                frame.widget.scroll_here_y(0.5)
                frame.widget.collapsed = False
                await ui_test.human_delay()

        widget_table = await build_sdf_asset_frame_dictonary()
        self.assertGreater(len(widget_table), 5)
