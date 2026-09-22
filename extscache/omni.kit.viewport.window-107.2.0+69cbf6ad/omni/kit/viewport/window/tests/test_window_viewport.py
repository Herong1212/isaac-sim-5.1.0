## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

__all__ = ["TestWindowViewport"]

from pathlib import Path
from pxr import Gf

import carb
import omni.kit.test
from omni.ui.tests.test_base import OmniUiTest
import omni.usd
import omni.timeline
from omni.kit.viewport.window import ViewportWindow

DATA_PATH = Path(carb.tokens.get_tokens_interface().resolve("${omni.kit.viewport.window}/data")).absolute().resolve()
TEST_FILES = DATA_PATH.joinpath("tests")
USD_FILES = TEST_FILES.joinpath("usd")

TEST_WIDTH, TEST_HEIGHT = 360, 240


class TestWindowViewport(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()

    # After running each test
    async def tearDown(self):
        await super().tearDown()

    async def test_timeline_time_projection(self):
        """Test that changing attribute that affect projection work when time-sampled."""
        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT)

        vp_window = ViewportWindow('TestWindow', width=TEST_WIDTH, height=TEST_HEIGHT)
        usd_context = vp_window.viewport_api.usd_context
        # L1 test without a render, so cannot lock to reults as there are none
        vp_window.viewport_api.lock_to_render_result = False

        await usd_context.open_stage_async(str(USD_FILES.joinpath("timesampled_camera.usda")))

        timeline = omni.timeline.get_timeline_interface()
        timeline.set_current_time(2)
        timeline.commit()

        expected_proj = Gf.Matrix4d(2.542591218004352, 0, 0, 0, 0, 4.261867184464438, 0, 0, 0, 0, -1.000002000002, -1, 0, 0, -2.000002000002, 0)
        self.assertTrue(Gf.IsClose(expected_proj, vp_window.viewport_api.projection, 1e-07))

        # Test no Window are reachable after destruction
        vp_window.destroy()
        del vp_window

        # Unblocks devices again
        await self.finalize_test_no_image()

    async def test_viewport_instance_resolution_serialization(self):
        """Test that restoring a Viewport instance resolution works from persistent data."""
        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT)

        vp_window = None
        settings = carb.settings.get_settings()
        try:
            vp_window = ViewportWindow('TestWindow', width=TEST_WIDTH, height=TEST_HEIGHT)
            self.assertEqual(vp_window.viewport_api.resolution, (1280, 720))
            self.assertEqual(vp_window.viewport_api.resolution_scale, 1.0)
        finally:
            if vp_window:
                vp_window.destroy()
                del vp_window

        try:
            settings.set('/persistent/app/viewport/TestWindow/Viewport0/resolution', [512, 512])
            settings.set('/persistent/app/viewport/TestWindow/Viewport0/resolutionScale', 0.25)
            vp_window = ViewportWindow('TestWindow', width=TEST_WIDTH, height=TEST_HEIGHT)
            self.assertEqual(vp_window.viewport_api.full_resolution, (512, 512))
            self.assertEqual(vp_window.viewport_api.resolution, (128, 128))
            self.assertEqual(vp_window.viewport_api.resolution_scale, 0.25)
        finally:
            settings.destroy_item('/persistent/app/viewport/TestWindow/Viewport0/resolution')
            settings.destroy_item('/persistent/app/viewport/TestWindow/Viewport0/resolutionScale')
            if vp_window:
                vp_window.destroy()
                del vp_window

        # Unblocks devices again
        await self.finalize_test_no_image()

    async def test_viewport_startup_resolution_serialization(self):
        """Test that restoring a Viewport instance resolution works from startup data."""
        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT)

        vp_window = None
        settings = carb.settings.get_settings()
        try:
            vp_window = ViewportWindow('TestWindow', width=TEST_WIDTH, height=TEST_HEIGHT)
            self.assertEqual(vp_window.viewport_api.resolution, (1280, 720))
            self.assertEqual(vp_window.viewport_api.resolution_scale, 1.0)
        finally:
            if vp_window:
                vp_window.destroy()
                del vp_window

        try:
            settings.set('/app/viewport/TestWindow/Viewport0/resolution', [1024, 1024])
            settings.set('/app/viewport/TestWindow/Viewport0/resolutionScale', 0.125)
            vp_window = ViewportWindow('TestWindow', width=TEST_WIDTH, height=TEST_HEIGHT)
            self.assertEqual(vp_window.viewport_api.full_resolution, (1024, 1024))
            self.assertEqual(vp_window.viewport_api.resolution, (128, 128))
            self.assertEqual(vp_window.viewport_api.resolution_scale, 0.125)
        finally:
            settings.destroy_item('/app/viewport/TestWindow/Viewport0/resolution')
            settings.destroy_item('/app/viewport/TestWindow/Viewport0/resolutionScale')
            if vp_window:
                vp_window.destroy()
                del vp_window

        # Unblocks devices again
        await self.finalize_test_no_image()

    async def test_viewport_globals_resolution_serialization(self):
        """Test that restoring a Viewport instance resolution works from startup global data."""
        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT)

        vp_window = None
        settings = carb.settings.get_settings()
        try:
            vp_window = ViewportWindow('TestWindow', width=TEST_WIDTH, height=TEST_HEIGHT)
            self.assertEqual(vp_window.viewport_api.resolution, (1280, 720))
            self.assertEqual(vp_window.viewport_api.resolution_scale, 1.0)
        finally:
            if vp_window:
                vp_window.destroy()
                del vp_window

        try:
            settings.set('/app/viewport/defaults/resolution', [512, 512])
            settings.set('/app/viewport/defaults/resolutionScale', 0.5)
            vp_window = ViewportWindow('TestWindow', width=TEST_WIDTH, height=TEST_HEIGHT)
            self.assertEqual(vp_window.viewport_api.full_resolution, (512, 512))
            self.assertEqual(vp_window.viewport_api.resolution, (256, 256))
            self.assertEqual(vp_window.viewport_api.resolution_scale, 0.5)
        finally:
            settings.destroy_item('/app/viewport/defaults/resolution')
            settings.destroy_item('/app/viewport/defaults/resolutionScale')
            if vp_window:
                vp_window.destroy()
                del vp_window

        # Unblocks devices again
        await self.finalize_test_no_image()

    async def __test_viewport_hud_visibility(self, golden_img_name: str, visible: bool, bg_alpha: float = None):
        """Test that toggling Viewport HUD visibility."""

        vp_window = None
        settings = carb.settings.get_settings()
        hud_setting_prefix = "/persistent/app/viewport/TestWindow/Viewport0/hud"
        hud_setting_keys = ("visible", "renderResolution/visible")
        golden_img_names = [f"{golden_img_name}_off.png", f"{golden_img_name}_on.png"]

        try:
            settings.destroy_item("/persistent/app/viewport/TestWindow/Viewport0")
            settings.destroy_item("/app/viewport/forceHideFps")
            settings.destroy_item("/app/viewport/showLayerMenu")

            for hk in hud_setting_keys:
                settings.set(f"{hud_setting_prefix}/{hk}", True)
            if bg_alpha is not None:
                settings.set("/persistent/app/viewport/ui/background/opacity", bg_alpha)
            settings.set(f"{hud_setting_prefix}/renderFPS/visible", False)
            settings.set(f"{hud_setting_prefix}/hostMemory/visible", False)

            await self.wait_n_updates()
            await self.create_test_area(width=320, height=240)
            vp_window = ViewportWindow('TestWindow', width=320, height=240)

            settings.set(f"{hud_setting_prefix}/visible", visible)
            await self.wait_n_updates()

            await self.capture_and_compare(golden_img_name=golden_img_names[visible], golden_img_dir=TEST_FILES)
            await self.wait_n_updates()

            settings.set(f"{hud_setting_prefix}/visible", not visible)
            await self.wait_n_updates()
            await self.finalize_test(golden_img_name=golden_img_names[not visible], golden_img_dir=TEST_FILES)

        finally:
            settings.destroy_item("/persistent/app/viewport/ui/background/opacity")

            if vp_window:
                vp_window.destroy()
                del vp_window

    async def test_viewport_hud_visibility(self):
        """Test that toggling Viewport HUD visibility works forward."""
        await self.__test_viewport_hud_visibility("test_viewport_hud_visibility", True)

    async def test_viewport_hud_visibility_with_bg(self):
        """Test that toggling Viewport HUD visibility works and is affected by UI background color."""
        await self.__test_viewport_hud_visibility("test_viewport_hud_visibility_no_bg", False, 0.0)

    async def test_camera_axis_resize(self):
        """Test that camera axis overlay properly sizes as requested."""
        from omni.kit.viewport.window.scene.scenes import CameraAxisLayer

        async def test_size(camera_axis_layer, size, golden_img_name):
            """test custom sizes"""
            # one way to set the size
            settings.set(CameraAxisLayer.CAMERA_AXIS_SIZE_SETTING, size)
            # another way to set the size
            settings.set(f"{CameraAxisLayer.CAMERA_AXIS_SIZE_SETTING}/0", size[0])
            settings.set(f"{CameraAxisLayer.CAMERA_AXIS_SIZE_SETTING}/1", size[1])

            # wait for UI refresh
            await self.wait_n_updates()

            # read back the actual layer extents and check if the values are as expected
            self.assertEqual(camera_axis_layer._CameraAxisLayer__scene_view.width.value, float(size[0]))
            self.assertEqual(camera_axis_layer._CameraAxisLayer__scene_view.height.value, float(size[1]))

            # finally, the image test
            await self.capture_and_compare(golden_img_name=golden_img_name, golden_img_dir=TEST_FILES)
            await self.wait_n_updates()

        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT)

        settings = carb.settings.get_settings()
        vp_window = ViewportWindow('TestWindow', width=TEST_WIDTH, height=TEST_HEIGHT)
        viewport_api = vp_window.viewport_api
        # Test requires a USD context so that the implicit cameras are actually created
        await viewport_api.usd_context.new_stage_async()

        # turn the CameraAxisLayer on
        axis_visibility_key = f"/persistent/app/viewport/{viewport_api.id}/guide/axis/visible"
        axis_vis_restore = settings.get(axis_visibility_key)

        try:
            settings.set(axis_visibility_key, True)

            # get CameraAxis layer
            cam_axis_layer = vp_window._find_viewport_layer(layer_id="Axis", category="guide")
            self.assertTrue(cam_axis_layer is not None, "Axis widget is not available!")

            def_size = CameraAxisLayer.CAMERA_AXIS_DEFAULT_SIZE
            await test_size(cam_axis_layer, (def_size[0] + 20, def_size[1] + 30), "test_camera_axis_resize_enlarge.png")
            await test_size(cam_axis_layer, (def_size[0] - 20, def_size[1] - 30), "test_camera_axis_resize_shrink.png")

        finally:
            settings.set(axis_visibility_key, axis_vis_restore)

            if vp_window:
                vp_window.destroy()
                del vp_window

            await self.finalize_test_no_image()

    async def __test_engine_creation_arguments(self, hydra_engine_options, verify_engine):
        vp_window = None
        try:
            await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT)

            vp_window = ViewportWindow('TestWindow', width=TEST_WIDTH, height=TEST_HEIGHT,
                                       hydra_engine_options=hydra_engine_options)

            await self.wait_n_updates()
            self.assertIsNotNone(vp_window)

            await verify_engine(vp_window.viewport_widget.viewport_api._hydra_texture)
        finally:
            if vp_window:
                vp_window.destroy()
                del vp_window

            await self.finalize_test_no_image()

    async def test_engine_creation_default_arguments(self):
        """Test default engine creation arguments"""

        async def verify_engine(hydra_texture):
            settings = carb.settings.get_settings()
            tick_rate = settings.get(f"{hydra_texture.get_settings_path()}hydraTickRate")
            is_async = settings.get(f"{hydra_texture.get_settings_path()}async")
            is_async_ll = settings.get(f"{hydra_texture.get_settings_path()}asyncLowLatency")

            self.assertEqual(is_async, bool(settings.get("/app/asyncRendering")))
            self.assertEqual(is_async_ll, bool(settings.get("/app/asyncRenderingLowLatency")))
            self.assertEqual(tick_rate, int(settings.get("/persistent/app/viewport/defaults/tickRate")))

        hydra_engine_options = {}
        await self.__test_engine_creation_arguments(hydra_engine_options, verify_engine)

    async def test_engine_creation_forward_arguments(self):
        """Test forwarding of engine creation arguments"""

        settings = carb.settings.get_settings()

        # Make sure the defaults are in a state that overrides from hydra_engine_options can be tested
        self.assertFalse(bool(settings.get("/app/asyncRendering")))
        self.assertFalse(bool(settings.get("/app/asyncRenderingLowLatency")))
        self.assertNotEqual(30, int(settings.get("/persistent/app/viewport/defaults/tickRate")))

        try:
            hydra_engine_options = {
                "is_async": True,
                "is_async_low_latency": True,
                "hydra_tick_rate": 30

            }

            async def verify_engine(hydra_texture):
                tick_rate = settings.get(f"{hydra_texture.get_settings_path()}hydraTickRate")
                is_async = settings.get(f"{hydra_texture.get_settings_path()}async")
                is_async_ll = settings.get(f"{hydra_texture.get_settings_path()}asyncLowLatency")

                self.assertEqual(is_async, hydra_engine_options.get("is_async"))
                self.assertEqual(is_async_ll, hydra_engine_options.get("is_async_low_latency"))
                self.assertEqual(tick_rate, hydra_engine_options.get("hydra_tick_rate"))

            await self.__test_engine_creation_arguments(hydra_engine_options, verify_engine)
        finally:
            settings.set("/app/asyncRendering", False)
            settings.destroy_item("/app/asyncRenderingLowLatency")
