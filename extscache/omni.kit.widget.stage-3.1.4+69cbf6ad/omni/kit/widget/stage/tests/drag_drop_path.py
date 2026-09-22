## Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
import os
import omni.kit.app
import omni.usd
import carb
from pxr import Usd, UsdGeom
from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit import ui_test
from omni.kit.test_suite.helpers import open_stage, get_test_data_path, wait_stage_loading, arrange_windows
from omni.kit.window.content_browser.test_helper import ContentBrowserTestHelper

PERSISTENT_SETTINGS_PREFIX = "/persistent"


class DragDropFileStagePath(AsyncTestCase):
    # Before running each test
    async def setUp(self):
        await arrange_windows(hide_viewport=True)
        await open_stage(get_test_data_path(__name__, "usd/empty.usda"))

    # After running each test
    async def tearDown(self):
        # ASSET_LOADED never gets sent during tearDown so ignore
        await wait_stage_loading(timeout=100, timeout_error=False)
        carb.settings.get_settings().set(PERSISTENT_SETTINGS_PREFIX + "/app/material/dragDropMaterialPath", "absolute")

    async def test_l1_drag_drop_path_usd_stage_absolute(self):
        carb.settings.get_settings().set(PERSISTENT_SETTINGS_PREFIX + "/app/material/dragDropMaterialPath", "absolute")

        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()

        stage_window = ui_test.find("Stage")
        await stage_window.focus()

        # drag/drop from content browser to stage window
        drag_target = stage_window.position + ui_test.Vec2(stage_window.size.x / 2, stage_window.size.y - 32)
        async with ContentBrowserTestHelper() as content_browser_helper:
            mdl_path = get_test_data_path(__name__, "mtl/badname.mdl")
            await content_browser_helper.drag_and_drop_tree_view(mdl_path, drag_target=drag_target)
        # verify prims
        shader = omni.usd.get_shader_from_material(stage.GetPrimAtPath('/World/Looks/Ue4basedMDL'), False)
        self.assertTrue(bool(shader), "/World/Looks/Ue4basedMDL not found")
        asset = shader.GetSourceAsset("mdl")
        self.assertTrue(os.path.isabs(asset.path))

    async def test_l1_drag_drop_path_usd_stage_relative(self):
        carb.settings.get_settings().set(PERSISTENT_SETTINGS_PREFIX + "/app/material/dragDropMaterialPath", "relative")

        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()

        stage_window = ui_test.find("Stage")
        await stage_window.focus()

        # drag/drop from content browser to stage window
        drag_target = stage_window.position + ui_test.Vec2(stage_window.size.x / 2, stage_window.size.y - 32)
        async with ContentBrowserTestHelper() as content_browser_helper:
            mdl_path = get_test_data_path(__name__, "mtl/badname.mdl")
            await content_browser_helper.drag_and_drop_tree_view(mdl_path, drag_target=drag_target)
        # verify prims
        shader = omni.usd.get_shader_from_material(stage.GetPrimAtPath('/World/Looks/Ue4basedMDL'), False)
        self.assertTrue(bool(shader), "/World/Looks/Ue4basedMDL not found")
        asset = shader.GetSourceAsset("mdl")
        self.assertFalse(os.path.isabs(asset.path))
