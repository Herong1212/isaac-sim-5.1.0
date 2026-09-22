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
from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit import ui_test
from pxr import Sdf, UsdShade
from omni.kit.test_suite.helpers import (
    open_stage,
    get_test_data_path,
    get_prims,
    wait_stage_loading,
    arrange_windows
    )
from omni.kit.window.content_browser.test_helper import ContentBrowserTestHelper


class DragDropFileStageMulti(AsyncTestCase):
    # Before running each test
    async def setUp(self):
        await arrange_windows()
        await open_stage(get_test_data_path(__name__, "usd/test_export_simple.usda"))

    # After running each test
    async def tearDown(self):
        await wait_stage_loading()

    async def test_l1_drag_drop_multi_usd_stage(self):
        await ui_test.find("Content").focus()

        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()

        stage_window = ui_test.find("Stage")
        await stage_window.focus()

        # verify prims
        paths = [prim.GetPath().pathString for prim in get_prims(stage) if not omni.usd.is_hidden_type(prim)]
        self.assertEqual(paths, ['/World', '/World/Cone', '/World/Cube', '/World/Looks', '/World/Looks/OmniPBR', '/World/Looks/OmniPBR/Shader', '/World/Looks/OmniGlass', '/World/Looks/OmniGlass/Shader'])

        # drag/drop files to stage window
        drag_target = stage_window.position + ui_test.Vec2(stage_window.size.x / 2, stage_window.size.y - 96)

        async with ContentBrowserTestHelper() as content_browser_helper:
            usd_path = get_test_data_path(__name__)
            await content_browser_helper.drag_and_drop_tree_view(
                usd_path, names=["4Lights.usda", "quatCube.usda"], drag_target=drag_target, focus_treeview_items=False)
        # verify prims
        paths = [prim.GetPath().pathString for prim in get_prims(stage) if not omni.usd.is_hidden_type(prim)]
        self.assertEqual(paths, ['/World', '/World/Cone', '/World/Cube', '/World/Looks', '/World/Looks/OmniPBR', '/World/Looks/OmniPBR/Shader', '/World/Looks/OmniGlass', '/World/Looks/OmniGlass/Shader', '/World/_Lights', '/World/_Lights/SphereLight_01', '/World/_Lights/SphereLight_02', '/World/_Lights/SphereLight_03', '/World/_Lights/SphereLight_00', '/World/_Lights/Cube', '/World/quatCube', '/World/quatCube/Cube'])
