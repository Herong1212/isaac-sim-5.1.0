## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

__all__ = ["TestViewportEvents"]

from pathlib import Path
import math

import carb
from carb.input import MouseEventType

from omni.ui.tests.test_base import OmniUiTest
from omni.kit.viewport.window import ViewportWindow
from omni.kit.ui_test import emulate_mouse_move, emulate_mouse_move_and_click, emulate_mouse_scroll, Vec2
from omni.kit.ui_test.input import emulate_mouse


DATA_PATH = Path(carb.tokens.get_tokens_interface().resolve("${omni.kit.viewport.window}/data"))
TESTS_PATH = DATA_PATH.joinpath("tests").absolute().resolve()
USD_FILES = TESTS_PATH.joinpath("usd")

TEST_WIDTH, TEST_HEIGHT = 360, 240


class TestViewportEvents(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()

    # After running each test
    async def tearDown(self):
        await super().tearDown()

    async def __test_camera_scroll_wheel(self, initial_speed: float, scroll_y: float, vel_scale: float, test_op):
        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT, block_devices=False)

        settings = carb.settings.get_settings()
        settings.set('/persistent/app/viewport/camMoveVelocity', initial_speed)
        settings.set('/persistent/app/viewport/camVelocityScalerMultAmount', vel_scale)
        settings.set('/persistent/app/viewport/show/flySpeed', True)

        await self.wait_n_updates()

        vp_window = ViewportWindow('TestWindow', width=TEST_WIDTH, height=TEST_HEIGHT)

        # Odd, but need to scale scroll by window height ?
        y_scroll_scale = scroll_y * TEST_HEIGHT
        try:
            await emulate_mouse_move_and_click(Vec2(TEST_WIDTH - 40, TEST_HEIGHT - 40))
            settings.set('/exts/omni.kit.manipulator.camera/viewportMode', [vp_window.viewport_api.id, 'fly'])
            await self.wait_n_updates()

            await emulate_mouse(MouseEventType.RIGHT_BUTTON_DOWN)
            await self.wait_n_updates()
            for _ in range(15):
                await emulate_mouse_scroll(Vec2(0, y_scroll_scale))
                await self.wait_n_updates()
                test_op(settings.get('/persistent/app/viewport/camMoveVelocity'))

        finally:
            await emulate_mouse(MouseEventType.RIGHT_BUTTON_UP)
            await self.wait_n_updates()
            settings.set('/persistent/app/viewport/camMoveVelocity', 5)
            settings.set('/persistent/app/viewport/camVelocityScalerMultAmount', 1)
            settings.set('/persistent/app/viewport/show/flySpeed', False)
            settings.set('/exts/omni.kit.manipulator.camera/viewportMode', None)

            # Test no Window are reachable after destruction
            vp_window.destroy()
            del vp_window

            # Restore devices and window sizes again
            await self.finalize_test_no_image()

    async def test_camera_speed_scroll_wheel_down(self):
        """Test that the camera-speed scroll adjusts speed within proper ranges when adjusting speed down."""

        initial_speed = 0.001

        def test_range(value):
            self.assertTrue(value > 0, msg="Camera speed has become or fallen below zero")
            self.assertTrue(value < initial_speed, msg="Camera speed has wrapped around")

        await self.__test_camera_scroll_wheel(initial_speed, -1, 1.1, test_range)

    async def test_camera_speed_scroll_up(self):
        """Test that the camera-speed scroll adjusts speed within proper ranges when adjusting speed up."""

        initial_speed = 1.7976931348623157e+307

        def test_range(value):
            self.assertTrue(math.isfinite(value), msg="Camera speed has become infinite")
            self.assertTrue(value > initial_speed, msg="Camera speed has wrapped around")

        await self.__test_camera_scroll_wheel(initial_speed, 1, 1.4, test_range)

    async def test_camera_speed_buttons(self):
        """Test the camera speed buttonf affect UI properly"""

        settings = carb.settings.get_settings()

        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT, block_devices=False)

        settings.set("/persistent/app/viewport/TestWindow/Viewport0/hud/visible", True)
        settings.set("/persistent/app/viewport/TestWindow/Viewport0/hud/cameraSpeed/visible", True)
        settings.set("/persistent/app/viewport/TestWindow/Viewport0/hud/renderResolution/visible", False)
        settings.set("/persistent/exts/omni.kit.viewport.window/cameraSpeedMessage/showFlyViewLock", True)
        settings.set("/persistent/exts/omni.kit.viewport.window/cameraSpeedMessage/collapsed", False)
        settings.set("/persistent/exts/omni.kit.manipulator.camera/flyViewLock", False)
        settings.set("/app/viewport/forceHideFps", False)
        settings.set("/persistent/app/viewport/camMoveVelocity", 5.0)

        fade_in = settings.get("/exts/omni.kit.viewport.window/cameraSpeedMessage/fadeIn")
        fade_out = settings.get("/exts/omni.kit.viewport.window/cameraSpeedMessage/fadeOut")
        settings.set("/exts/omni.kit.viewport.window/cameraSpeedMessage/fadeIn", 0)
        settings.set("/exts/omni.kit.viewport.window/cameraSpeedMessage/fadeOut", 5.0)

        vp_window = None
        click_received = False
        await self.wait_n_updates(10)

        import omni.ui.scene as sc
        from omni.kit.viewport.registry import RegisterScene

        class ObjectClickGesture(sc.ClickGesture):
            def on_ended(self, *args):
                nonlocal click_received
                click_received = True

        class ViewportClickManipulator(sc.Manipulator):
            def __init__(self, viewport_desc):
                super().__init__()

            def on_build(self):
                # Need to hold a reference to this or the sc.Screen would be destroyed when out of scope
                self.__transform = sc.Transform()
                with self.__transform:
                    self.__screen = sc.Screen(gesture=ObjectClickGesture(mouse_button=0))

        scoped_factory = RegisterScene(ViewportClickManipulator, 'omni.kit.viewport.window.tests.test_camera_speed_buttons')  # noqa F841

        try:
            vp_window = ViewportWindow('TestWindow', width=TEST_WIDTH, height=TEST_HEIGHT)
            settings.set("/exts/omni.kit.manipulator.camera/viewportMode", [vp_window.viewport_api.id, "fly"])

            await emulate_mouse_move(Vec2(30, 80))
            await self.wait_n_updates()
            await self.capture_and_compare(golden_img_dir=TESTS_PATH, golden_img_name="test_camera_speed_buttons_start.png")

            await emulate_mouse_move_and_click(Vec2(30, 80))
            await self.wait_n_updates()
            await self.capture_and_compare(golden_img_dir=TESTS_PATH, golden_img_name="test_camera_speed_buttons_down.png")

            await emulate_mouse_move_and_click(Vec2(30, 80))
            await self.wait_n_updates()
            await self.capture_and_compare(golden_img_dir=TESTS_PATH, golden_img_name="test_camera_speed_buttons_up.png")

            await emulate_mouse_move_and_click(Vec2(275, 105))
            await self.wait_n_updates()
            await self.capture_and_compare(golden_img_dir=TESTS_PATH, golden_img_name="test_camera_speed_lock_down.png")

            self.assertFalse(click_received)
        finally:
            if vp_window:
                vp_window.destroy()
                del vp_window

            settings.set("/exts/omni.kit.viewport.window/cameraSpeedMessage/fadeIn", fade_in)
            settings.set("/exts/omni.kit.viewport.window/cameraSpeedMessage/fadeOut", fade_out)
            settings.destroy_item("/persistent/app/viewport/TestWindow/Viewport0/hud/visible")
            settings.destroy_item("/persistent/app/viewport/TestWindow/Viewport0/hud/cameraSpeed/visible")
            settings.destroy_item("/persistent/exts/omni.kit.viewport.window/cameraSpeedMessage/showFlyViewLock")
            settings.destroy_item("/persistent/exts/omni.kit.viewport.window/cameraSpeedMessage/collapsed")
            settings.destroy_item("/persistent/app/viewport/TestWindow/Viewport0/hud/renderResolution/visible")
            settings.destroy_item("/persistent/exts/omni.kit.manipulator.camera/flyViewLock")
            settings.destroy_item("/app/viewport/forceHideFps")

            await self.finalize_test_no_image()
