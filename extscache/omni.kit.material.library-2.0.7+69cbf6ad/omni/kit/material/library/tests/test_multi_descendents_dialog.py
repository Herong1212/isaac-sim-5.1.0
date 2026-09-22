## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

import omni.kit.app
import omni.kit.test
import omni.usd
from omni.kit import ui_test
from omni.kit.material.library.test_helper import MaterialLibraryTestHelper
from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit.test_suite.helpers import (
    arrange_windows,
    get_test_data_path,
    handle_multiple_descendents_dialog,
    open_stage,
    wait_stage_loading,
)
from omni.kit.ui_test import Vec2
from omni.kit.viewport.utility import get_ui_position_for_prim
from omni.kit.window.content_browser.test_helper import ContentBrowserTestHelper
from pxr import UsdShade


class MultipleDescendentsDragDropTest(AsyncTestCase):
    # Before running each test
    async def setUp(self):
        await open_stage(get_test_data_path(__name__, "usd/empty_stage.usda"))

    # After running each test
    async def tearDown(self):
        await wait_stage_loading()

    async def test_drag_drop_material_viewport(self, retries=0):
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
                return await self.test_drag_drop_material_viewport(retries+1)
            print(f">> test_drag_drop_material_viewport: No materials found, skipping test.")
            return

        for mtl_name, mdl_path, submenu in mdl_list:
            if "Presets" in mdl_path or "Base" in mdl_path:
                continue
            if not single_material and not submenu :
                single_material = (mtl_name, mdl_path)
            if not multi_material and submenu:
                multi_material = (mtl_name, mdl_path)

        if not single_material or not multi_material:
            print(f">> test_drag_drop_material_viewport: failed to find single_material ({single_material}) and/or multi_material ({multi_material})")
            print(f">> test_drag_drop_material_viewport: mdl_list:{mdl_list}")
            await ui_test.human_delay(50)
            if retries < 5:
                return await self.test_drag_drop_material_viewport(retries+1)

        # verify both tests have run
        self.assertTrue(single_material != None)
        self.assertTrue(multi_material != None)

        async def verify_prims(stage, mtl_name, verify_prim_list):
            # verify material
            await ui_test.human_delay(10)
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


        async def test_mtl(stage, material, verify_prim_list, drag_target):
            mtl_name, mdl_path = material

            # drag and drop items from the tree view of content browser
            async with ContentBrowserTestHelper() as content_browser_helper:
                await content_browser_helper.drag_and_drop_tree_view(mdl_path, drag_target=drag_target)

            await ui_test.human_delay(10)

            # handle create material dialog
            async with MaterialLibraryTestHelper() as material_library_helper:
                await material_library_helper.handle_create_material_dialog(mdl_path, mtl_name)

            # wait for material to load & UI to refresh
            await wait_stage_loading()
            await ui_test.human_delay(10)

            # verify created/bound prims
            await verify_prims(stage, mtl_name, verify_prim_list)


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


        # test DnD single & multi subid material from Content window to center of viewport - Create material
        stage = omni.usd.get_context().get_stage()
        drag_target = ui_test_window.center

        await test_mtl(stage, single_material, [], drag_target)
        await test_mtl(stage, multi_material, [], drag_target)

        # load stage with multi-descendant prim
        await open_stage(get_test_data_path(__name__, "usd/multi-material-object-cube-component.usda"))
        await wait_stage_loading()

        # test DnD single & multi subid material from Content window to /World/Sphere - Create material & Binding
        stage = omni.usd.get_context().get_stage()
        verify_prim_list = ["/World/Sphere"]
        drag_target, valid = get_ui_position_for_prim(viewport_window, verify_prim_list[0])
        drag_target = Vec2(drag_target[0], drag_target[1])
        await test_mtl(stage, single_material, verify_prim_list, drag_target)
        await test_mtl(stage, multi_material, verify_prim_list, drag_target)

        # test DnD single & multi subid material from Content window to /World/pCube1 targeting each descendant - Create material & Binding
        stage = omni.usd.get_context().get_stage()
        multiple_descendents_prim = "/World/pCube1"
        descendents = ["/World/pCube1", "/World/pCube1/front1", "/World/pCube1/side1", "/World/pCube1/back", "/World/pCube1/side2", "/World/pCube1/top1", "/World/pCube1/bottom"]
        drag_target, valid = get_ui_position_for_prim(viewport_window, multiple_descendents_prim)
        drag_target = Vec2(drag_target[0], drag_target[1])
        for target_prim in descendents:
            await test_multiple_descendents_mtl(stage, single_material, multiple_descendents_prim, target_prim, drag_target)
            await test_multiple_descendents_mtl(stage, multi_material, multiple_descendents_prim, target_prim, drag_target)
