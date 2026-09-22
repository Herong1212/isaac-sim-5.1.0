## Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
import omni.kit.app
import omni.usd

from pxr import UsdGeom
from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit import ui_test
from omni.kit.test_suite.helpers import (
    open_stage,
    get_test_data_path,
    get_prims,
    wait_stage_loading,
    arrange_windows
    )
from omni.kit.window.content_browser.test_helper import ContentBrowserTestHelper



class DragDropFileStageSingle(AsyncTestCase):
    # Before running each test
    async def setUp(self):
        await arrange_windows(hide_viewport=True)
        await open_stage(get_test_data_path(__name__, "usd/test_export_simple.usda"))

    # After running each test
    async def tearDown(self):
        await wait_stage_loading()

    async def test_l1_drag_drop_single_usd_stage(self):
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()

        await wait_stage_loading()

        await ui_test.find("Content").focus()
        await ui_test.find("Stage").focus()

        # verify prims
        paths = [prim.GetPath().pathString for prim in get_prims(stage) if not omni.usd.is_hidden_type(prim)]
        self.assertEqual(paths, ['/World', '/World/Cone', '/World/Cube', '/World/Looks', '/World/Looks/OmniPBR', '/World/Looks/OmniPBR/Shader', '/World/Looks/OmniGlass', '/World/Looks/OmniGlass/Shader'])

        # drag/drop files to stage window
        async with ContentBrowserTestHelper() as content_browser_helper:
            stage_window = ui_test.find("Stage")
            drag_target = stage_window.position + ui_test.Vec2(stage_window.size.x / 2, stage_window.size.y - 32)
            await content_browser_helper.drag_and_drop_tree_view(get_test_data_path(__name__, "quatCube.usda"), drag_target=drag_target)

        for i in range(5):
            await omni.kit.app.get_app().next_update_async()
        # verify prims
        paths = [prim.GetPath().pathString for prim in get_prims(stage) if not omni.usd.is_hidden_type(prim)]
        self.assertEqual(paths, ['/World', '/World/Cone', '/World/Cube', '/World/Looks', '/World/Looks/OmniPBR', '/World/Looks/OmniPBR/Shader', '/World/Looks/OmniGlass', '/World/Looks/OmniGlass/Shader', '/World/quatCube', '/World/quatCube/Cube'])

    async def test_drag_drop_to_default_prim(self):
        usd_context = omni.usd.get_context()
        await usd_context.new_stage_async()

        await ui_test.find("Content").focus()
        await ui_test.find("Stage").focus()

        stage = usd_context.get_stage()
        prim = stage.DefinePrim("/test", "Xform")
        prim2 = stage.DefinePrim("/test2", "Xform")
        prim3 = UsdGeom.Mesh.Define(stage, "/test3").GetPrim()

        total_root_prims = 3
        """
        OM-66707

        Rules:
        1. When it has no default prim, it will create pseudo root prim reference.
        2. When it has default prim, it will create reference under default prim.
        3. When the default prim is a gprim, it will create reference under pseudo root prim too as gprims
        cannot have children.
        """
        for default_prim in [None, prim, prim2, prim3]:
            if default_prim:
                stage.SetDefaultPrim(default_prim)
            else:
                stage.ClearDefaultPrim()

            # drag/drop files to stage window
            async with ContentBrowserTestHelper() as content_browser_helper:
                stage_window = ui_test.find("Stage")
                drag_target = stage_window.position + ui_test.Vec2(stage_window.size.x / 2, stage_window.size.y - 32)
                url = get_test_data_path(__name__, 'usd')
                await content_browser_helper.drag_and_drop_tree_view(url, names=["empty.usda", "cube.usda"], drag_target=drag_target, focus_treeview_items=False)
            if default_prim and default_prim != prim3:
                self.assertEqual(len(prim.GetChildren()), 2)
            else:
                total_root_prims += 2

            all_root_prims = [prim for prim in stage.GetPseudoRoot().GetChildren() if not omni.usd.is_hidden_type(prim)]
            self.assertEqual(len(all_root_prims), total_root_prims)
