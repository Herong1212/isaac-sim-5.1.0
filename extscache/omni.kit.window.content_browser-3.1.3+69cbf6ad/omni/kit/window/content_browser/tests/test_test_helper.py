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
from omni.kit.test_suite.helpers import open_stage, get_test_data_path, get_prims, wait_stage_loading, arrange_windows
from ..test_helper import ContentBrowserTestHelper


class TestDragDropTreeView(AsyncTestCase):
    # Before running each test
    async def setUp(self):
        await arrange_windows("Stage", 512)

    # After running each test
    async def tearDown(self):
        await wait_stage_loading()

    async def test_config_menu_setting(self):
        await ui_test.find("Content").focus()

        async with ContentBrowserTestHelper() as content_browser_helper:
            old_setting = await content_browser_helper.get_config_menu_settings()
            # TODO: Why this not works as expect?
            await content_browser_helper.set_config_menu_settings({"test": "test"})
            test_dict = await content_browser_helper.get_config_menu_settings()
            standard_dict = {'hide_unknown': False, 'hide_thumbnails': True, 'show_details': False, 'show_udim_sequence': False}
            self.assertEqual(test_dict,standard_dict)
            await content_browser_helper.set_config_menu_settings(old_setting)

    async def test_select_single_item(self):
        await ui_test.find("Content").focus()

        # select file to show info
        usd_path = get_test_data_path(__name__)
        async with ContentBrowserTestHelper() as content_browser_helper:
            selections = await content_browser_helper.select_items_async(usd_path, names=["4Lights.usda"])
            await ui_test.human_delay(4)

        # Verify selections
        self.assertEqual([sel.name for sel in selections], ['4Lights.usda'])

    async def test_select_multiple_items(self):
        await ui_test.find("Content").focus()

        # select file to show info
        usd_path = get_test_data_path(__name__)
        filenames = ["4Lights.usda", "bound_shapes.usda", "quatCube.usda"]
        async with ContentBrowserTestHelper() as content_browser_helper:
            selections = await content_browser_helper.select_items_async(usd_path, names=filenames+["nonexistent.usda"])
            await ui_test.human_delay(4)

        # Verify selections
        self.assertEqual(sorted([sel.name for sel in selections]), sorted(filenames))

    async def test_drag_drop_single_item(self):
        await open_stage(get_test_data_path(__name__, "bound_shapes.usda"))
        await wait_stage_loading()

        await ui_test.find("Content").focus()
        await ui_test.find("Stage").focus()

        # verify prims
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        paths = [prim.GetPath().pathString for prim in get_prims(stage) if not omni.usd.is_hidden_type(prim)]
        self.assertEqual(paths, ['/World', '/World/defaultLight', '/World/Cone', '/World/Cube', '/World/Sphere', '/World/Cylinder', '/World/Looks', '/World/Looks/OmniPBR', '/World/Looks/OmniPBR/Shader', '/World/Looks/OmniGlass', '/World/Looks/OmniGlass/Shader', '/World/Looks/OmniSurface_Plastic', '/World/Looks/OmniSurface_Plastic/Shader'])

        # drag/drop files to stage window
        stage_window = ui_test.find("Stage")
        drag_target = stage_window.position + ui_test.Vec2(stage_window.size.x / 2, stage_window.size.y - 32)

        async with ContentBrowserTestHelper() as content_browser_helper:
            for file_path in ["4Lights.usda", "quatCube.usda"]:
                await content_browser_helper.drag_and_drop_tree_view(get_test_data_path(__name__, file_path), drag_target=drag_target)

        # verify prims
        paths = [prim.GetPath().pathString for prim in get_prims(stage) if not omni.usd.is_hidden_type(prim)]
        self.assertEqual(paths, ['/World', '/World/defaultLight', '/World/Cone', '/World/Cube', '/World/Sphere', '/World/Cylinder', '/World/Looks', '/World/Looks/OmniPBR', '/World/Looks/OmniPBR/Shader', '/World/Looks/OmniGlass', '/World/Looks/OmniGlass/Shader', '/World/Looks/OmniSurface_Plastic', '/World/Looks/OmniSurface_Plastic/Shader', '/World/_Lights', '/World/_Lights/SphereLight_01', '/World/_Lights/SphereLight_02', '/World/_Lights/SphereLight_03', '/World/_Lights/SphereLight_00', '/World/_Lights/Cube', '/World/quatCube', '/World/quatCube/Cube'])

    async def test_drag_drop_multiple_items(self):
        await open_stage(get_test_data_path(__name__, "bound_shapes.usda"))
        await wait_stage_loading()

        await ui_test.find("Content").focus()
        await ui_test.find("Stage").focus()

        # verify prims
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        paths = [prim.GetPath().pathString for prim in get_prims(stage) if not omni.usd.is_hidden_type(prim)]
        self.assertEqual(paths, ['/World', '/World/defaultLight', '/World/Cone', '/World/Cube', '/World/Sphere', '/World/Cylinder', '/World/Looks', '/World/Looks/OmniPBR', '/World/Looks/OmniPBR/Shader', '/World/Looks/OmniGlass', '/World/Looks/OmniGlass/Shader', '/World/Looks/OmniSurface_Plastic', '/World/Looks/OmniSurface_Plastic/Shader'])

        # drag/drop files to stage window
        stage_window = ui_test.find("Stage")
        drag_target = stage_window.position + ui_test.Vec2(stage_window.size.x / 2, stage_window.size.y - 96)

        async with ContentBrowserTestHelper() as content_browser_helper:
            usd_path = get_test_data_path(__name__)
            await content_browser_helper.drag_and_drop_tree_view(usd_path, names=["4Lights.usda", "quatCube.usda"], drag_target=drag_target, focus_treeview_items=False)

        # verify prims
        paths = [prim.GetPath().pathString for prim in get_prims(stage) if not omni.usd.is_hidden_type(prim)]
        self.assertEqual(paths, ['/World', '/World/defaultLight', '/World/Cone', '/World/Cube', '/World/Sphere', '/World/Cylinder', '/World/Looks', '/World/Looks/OmniPBR', '/World/Looks/OmniPBR/Shader', '/World/Looks/OmniGlass', '/World/Looks/OmniGlass/Shader', '/World/Looks/OmniSurface_Plastic', '/World/Looks/OmniSurface_Plastic/Shader', '/World/_Lights', '/World/_Lights/SphereLight_01', '/World/_Lights/SphereLight_02', '/World/_Lights/SphereLight_03', '/World/_Lights/SphereLight_00', '/World/_Lights/Cube', '/World/quatCube', '/World/quatCube/Cube'])
