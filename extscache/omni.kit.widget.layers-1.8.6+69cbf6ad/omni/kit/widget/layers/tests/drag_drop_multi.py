## Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
import omni.usd
import omni.kit.ui_test as ui_test

from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit.test_suite.helpers import open_stage, wait_stage_loading, get_test_data_path, get_prims, arrange_windows
from omni.kit.window.content_browser.test_helper import ContentBrowserTestHelper


class DragDropFileStageMulti(AsyncTestCase):
    # Before running each test
    async def setUp(self):
        await arrange_windows("Layer", 800, 600)
        await open_stage(get_test_data_path(__name__, "bound_shapes.usda"))
        await wait_stage_loading()

    # After running each test
    async def tearDown(self):
        await wait_stage_loading()

    async def test_l1_drag_drop_multi_usd_stage(self):
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()

        await ui_test.find("Content").focus()
        stage_window = ui_test.find("Layer")
        await stage_window.focus()

        # verify prims
        paths = [prim.GetPath().pathString for prim in get_prims(stage) if not omni.usd.is_hidden_type(prim)]
        self.assertEqual(paths, ['/World', '/World/defaultLight', '/World/Cone', '/World/Cube', '/World/Sphere', '/World/Cylinder', '/World/Looks', '/World/Looks/OmniPBR', '/World/Looks/OmniPBR/Shader', '/World/Looks/OmniGlass', '/World/Looks/OmniGlass/Shader', '/World/Looks/OmniSurface_Plastic', '/World/Looks/OmniSurface_Plastic/Shader'])

        # drag/drop files to stage window
        drag_target = stage_window.position + ui_test.Vec2(stage_window.size.x / 2, stage_window.size.y / 2)

        # get file from content window
        async with ContentBrowserTestHelper() as content_browser_helper:
            usd_path = get_test_data_path(__name__)
            await content_browser_helper.drag_and_drop_tree_view(
                usd_path, names=["4Lights.usda", "quatCube.usda"], drag_target=drag_target, focus_treeview_items=False)

        # verify prims
        paths = [prim.GetPath().pathString for prim in get_prims(stage) if not omni.usd.is_hidden_type(prim)]
        self.assertEqual(paths, ['/Stage', '/Stage/Cube', '/Stage/SphereLight_01', '/Stage/SphereLight_02', '/Stage/SphereLight_03', '/Stage/SphereLight_00', '/World', '/World/defaultLight', '/World/Cone', '/World/Cube', '/World/Sphere', '/World/Cylinder', '/World/Looks', '/World/Looks/OmniPBR', '/World/Looks/OmniPBR/Shader', '/World/Looks/OmniGlass', '/World/Looks/OmniGlass/Shader', '/World/Looks/OmniSurface_Plastic', '/World/Looks/OmniSurface_Plastic/Shader'])
