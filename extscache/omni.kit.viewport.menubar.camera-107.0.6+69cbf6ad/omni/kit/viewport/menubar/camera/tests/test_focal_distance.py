# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#


import carb.input
from omni.kit.ui_test import Vec2
import omni.kit.ui_test as ui_test
from omni.kit.viewport.utility import get_active_viewport_window
from omni.ui.tests.test_base import OmniUiTest
import omni.usd
from pxr import Gf, UsdGeom


TEST_WIDTH, TEST_HEIGHT = 850, 300


class TestFocalDistance(OmniUiTest):
    async def setUp(self):
        self.usd_context_name = ''
        self.usd_context = omni.usd.get_context(self.usd_context_name)
        await self.usd_context.new_stage_async()
        self.stage = self.usd_context.get_stage()

        self.stage.SetDefaultPrim(UsdGeom.Xform.Define(self.stage, '/World').GetPrim())

        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT)

        await self.wait_n_updates()

        self._viewport_window = get_active_viewport_window()
        self._viewport_window.position_x = 0
        self._viewport_window.position_y = 0

    async def tearDown(self):
        self.usd_context = None
        self.stage = None

    async def test_cam_sample_focal_distance(self):
        # create a test camera
        cam_path = '/World/TestCamera'
        cam_prim = UsdGeom.Camera.Define(self.stage, cam_path).GetPrim()
        omni.kit.commands.execute("TransformPrimSRTCommand", path=cam_path, new_translation=Gf.Vec3d(0, 0, 15))
        focus_dist_attr = cam_prim.GetAttribute('focusDistance')
        focus_dist_attr.Set(400)

        # create a cube as the sample
        sample_path = '/World/Cube'
        UsdGeom.Cube.Define(self.stage, sample_path)
        await self.wait_n_updates(300)

        # set the test cam to be the viewport cam
        app_window = omni.appwindow.get_default_app_window()
        app_window.set_input_blocking_state(carb.input.DeviceType.MOUSE, None)
        # open camera list
        await ui_test.emulate_mouse_move(Vec2(40, 40))
        await ui_test.emulate_mouse_click()
        await self.wait_n_updates()
        # cameras
        await ui_test.emulate_mouse_move(Vec2(40, 75))
        await ui_test.emulate_mouse_click()
        await self.wait_n_updates()
        # choose test camera
        await ui_test.emulate_mouse_move(Vec2(200, 75))
        await ui_test.emulate_mouse_click()
        await self.wait_n_updates()

        # decrease the focal distance by 3
        await ui_test.emulate_mouse_move(Vec2(340, 50))
        for _ in range(3):
            await self.wait_n_updates()
            await ui_test.emulate_mouse_click()
        await self.wait_n_updates()
        self.assertEqual(focus_dist_attr.Get(), 397)

        # click focal sample button to enable sample picker
        await ui_test.emulate_mouse_move(Vec2(370, 40))
        await self.wait_n_updates()
        await ui_test.emulate_mouse_click()
        await self.wait_n_updates()

        # click the sample object (cube) to reset the focal distance
        await ui_test.emulate_mouse_move(Vec2(420, 150))
        await self.wait_n_updates()
        await ui_test.emulate_mouse_click()
        await self.wait_n_updates(10)
        self.assertAlmostEqual(focus_dist_attr.Get(), 14, places=2)
