## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
__all__ = ["TestCaptureAPI"]

import contextlib
from pathlib import Path
import os

import omni.client
import omni.kit.test
from omni.ui.tests.test_base import OmniUiTest

import omni.usd
import omni.ui as ui
from omni.kit.widget.viewport import ViewportWidget
from omni.kit.widget.viewport.capture import ByteCapture, FileCapture
from omni.kit.test_helpers_gfx.compare_utils import compare as gfx_compare
from omni.kit.test import get_test_output_path

import carb
from pxr import Usd, UsdRender


OUTPUTS_DIR = Path(get_test_output_path())
CURRENT_PATH = Path(carb.tokens.get_tokens_interface().resolve("${omni.kit.widget.viewport}/data")).absolute().resolve()
TEST_FILES_DIR = CURRENT_PATH.joinpath("tests")
USD_FILES_DIR = TEST_FILES_DIR.joinpath("usd")

TEST_WIDTH, TEST_HEIGHT = 360, 240


# XXX: Make this more accessible in compare_utils
#
def compare_images(image_name):
    gfx_compare(OUTPUTS_DIR.joinpath(image_name),
                TEST_FILES_DIR.joinpath(image_name),
                OUTPUTS_DIR.joinpath(f"{Path(image_name).stem}.diffmap.png"))


class TestByteCapture(ByteCapture):
    def __init__(self, test, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__test = test
        self.__complete = False

    def on_capture_completed(self, buffer, buffer_size, width, height, byte_format):
        self.__test.assertEqual(width, TEST_WIDTH)
        self.__test.assertEqual(height, TEST_HEIGHT)
        self.__test.assertEqual(byte_format, ui.TextureFormat.RGBA8_UNORM)


class TestCaptureAPI(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()

    # After running each test
    async def tearDown(self):
        await super().tearDown()

    async def wait_for_capture_file(self, image_path):
        while True:
            result, entry = omni.client.stat(image_path)
            if result == omni.client.Result.OK and entry.size > 0:
                break
            await self.wait_n_updates()
        self.assertTrue(os.path.exists(image_path))

    async def merged_test_capture_file(self):
        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT)

        usd_path = str(TEST_FILES_DIR.joinpath("usd/sphere.usda"))
        image_name = "sphere.png"
        image_path = str(OUTPUTS_DIR.joinpath(image_name))

        usd_context = omni.usd.get_context()
        await usd_context.open_stage_async(usd_path)
        self.assertIsNotNone(usd_context.get_stage())

        vp_window = ui.Window("test_capture_file", width=TEST_WIDTH, height=TEST_HEIGHT, flags=ui.WINDOW_FLAGS_NO_SCROLLBAR)
        self.assertIsNotNone(vp_window)
        with vp_window.frame:
            vp_widget = ViewportWidget(resolution=(TEST_WIDTH, TEST_HEIGHT))
            self.assertIsNotNone(vp_widget)

            capture = vp_widget.viewport_api.schedule_capture(FileCapture(image_path))
            captured_aovs = await capture.wait_for_result()
            await self.wait_for_capture_file(image_path)
            self.assertEqual(captured_aovs, ["LdrColor"])
            # Test the frame's metadata is available
            self.assertIsNotNone(capture.view)
            self.assertIsNotNone(capture.projection)
            self.assertEqual(capture.resolution, (TEST_WIDTH, TEST_HEIGHT))
            # Test the viewport_handle is also available for usets that
            self.assertIsNotNone(capture.viewport_handle)

            compare_images(image_name)

        vp_widget.destroy()
        vp_window.destroy()
        del vp_window

    async def merged_test_capture_file_with_format(self):
        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT)

        usd_path = str(TEST_FILES_DIR.joinpath("usd/sphere.usda"))
        image_name = "sphere_rle.exr"
        image_path = str(OUTPUTS_DIR.joinpath(image_name))

        usd_context = omni.usd.get_context()
        await usd_context.open_stage_async(usd_path)
        self.assertIsNotNone(usd_context.get_stage())

        vp_window = ui.Window("test_capture_file_with_format", width=TEST_WIDTH, height=TEST_HEIGHT, flags=ui.WINDOW_FLAGS_NO_SCROLLBAR)
        self.assertIsNotNone(vp_window)
        with vp_window.frame:
            vp_widget = ViewportWidget(resolution=(TEST_WIDTH, TEST_HEIGHT))
            self.assertIsNotNone(vp_widget)

            capture = vp_widget.viewport_api.schedule_capture(FileCapture(image_path,
                                                                          format_desc={"format": "exr",
                                                                                       "compression": "rle"}))
            captured_aovs = await capture.wait_for_result()
            await self.wait_for_capture_file(image_path)
            self.assertEqual(captured_aovs, ["LdrColor"])
            # Test the frame's metadata is available
            self.assertIsNotNone(capture.view)
            self.assertIsNotNone(capture.projection)
            self.assertEqual(capture.resolution, (TEST_WIDTH, TEST_HEIGHT))
            # Test the viewport_handle is also available for usets that
            self.assertIsNotNone(capture.viewport_handle)

            compare_images(image_name)

        vp_widget.destroy()
        vp_window.destroy()
        del vp_window

    async def merged_test_capture_bytes_free_func_hdr(self):
        # 1030: Doesn't have the ability to set render_product_path and this test will fail
        import omni.hydratexture
        if not hasattr(omni.hydratexture.IHydraTexture, "set_render_product_path"):
            return

        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT)

        aov_name = "HdrColor"
        image_name = f"cube_{aov_name}.exr"
        image_path = str(OUTPUTS_DIR.joinpath(image_name))
        usd_path = str(TEST_FILES_DIR.joinpath("usd/cube.usda"))

        with contextlib.suppress(FileNotFoundError):
            os.remove(image_path)

        usd_context = omni.usd.get_context()
        await usd_context.open_stage_async(usd_path)
        self.assertIsNotNone(usd_context.get_stage())

        num_calls = 0

        def on_capture_completed(buffer, buffer_size, width, height, byte_format):
            nonlocal num_calls
            num_calls = num_calls + 1
            self.assertEqual(width, TEST_WIDTH)
            self.assertEqual(height, TEST_HEIGHT)
            # Note the RGBA16_SFLOAT format!
            self.assertEqual(byte_format, ui.TextureFormat.RGBA16_SFLOAT)

        vp_window = ui.Window("test_capture_bytes_free_func", width=TEST_WIDTH, height=TEST_HEIGHT, flags=ui.WINDOW_FLAGS_NO_SCROLLBAR)
        self.assertIsNotNone(vp_window)
        with vp_window.frame:
            vp_widget = ViewportWidget(resolution=(TEST_WIDTH, TEST_HEIGHT))
            self.assertIsNotNone(vp_widget)

            # Edit the RenderProduct to output HdrColor
            render_product_path = vp_widget.viewport_api.render_product_path
            if render_product_path[0] != "/":
                render_product_path = f"/Render/RenderProduct_{render_product_path}"

            stage = usd_context.get_stage()
            with Usd.EditContext(stage, stage.GetSessionLayer()):
                prim = usd_context.get_stage().GetPrimAtPath(render_product_path)
                self.assertTrue(prim.IsValid())
                self.assertTrue(prim.IsA(UsdRender.Product))
                product = UsdRender.Product(prim)
                targets = product.GetOrderedVarsRel().GetForwardedTargets()
                self.assertEqual(1, len(targets))

                prim = usd_context.get_stage().GetPrimAtPath(targets[0])
                self.assertTrue(prim.IsValid())
                self.assertTrue(prim.IsA(UsdRender.Var))
                render_var = UsdRender.Var(prim)
                value_set = render_var.GetSourceNameAttr().Set(aov_name)
                self.assertTrue(value_set)

            # Trigger the texture to update the render, and wait for the change to funnel back to us
            vp_widget.viewport_api.render_product_path = render_product_path
            settings_changed = await vp_widget.viewport_api.wait_for_render_settings_change()
            self.assertTrue(settings_changed)

            # Now that the settings have changed, so the capture of "HdrColor"
            captured_aovs = await vp_widget.viewport_api.schedule_capture(ByteCapture(on_capture_completed, aov_name=aov_name)).wait_for_result()
            self.assertTrue(aov_name in captured_aovs)

            # Since we requested one AOV, test that on_capture_completed was only called once
            # Currently RTX will deliver "HdrColor" and "LdrColor" when "HdrColor" is requested
            # If that changes these two don't neccessarily need to be tested.
            self.assertEqual(len(captured_aovs), 1)
            self.assertEqual(num_calls, 1)

            captured_aovs = await vp_widget.viewport_api.schedule_capture(FileCapture(image_path, aov_name=aov_name)).wait_for_result()
            self.assertTrue(aov_name in captured_aovs)
            await self.wait_for_capture_file(image_path)
            compare_images(image_name)

        vp_widget.destroy()
        vp_window.destroy()
        del vp_window

    async def merged_test_capture_bytes_subclass(self):
        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT)

        usd_path = str(TEST_FILES_DIR.joinpath("usd/cube.usda"))
        usd_context = omni.usd.get_context()
        await usd_context.open_stage_async(usd_path)
        self.assertIsNotNone(usd_context.get_stage())

        capture = TestByteCapture(self)

        vp_window = ui.Window("test_capture_bytes_subclass", width=TEST_WIDTH, height=TEST_HEIGHT, flags=ui.WINDOW_FLAGS_NO_SCROLLBAR)
        self.assertIsNotNone(vp_window)
        with vp_window.frame:
            vp_widget = ViewportWidget(resolution=(TEST_WIDTH, TEST_HEIGHT))
            self.assertIsNotNone(vp_widget)
            vp_widget.viewport_api.schedule_capture(capture)

        captured_aovs = await capture.wait_for_result()
        self.assertEqual(captured_aovs, ["LdrColor"])

        vp_widget.destroy()
        vp_window.destroy()
        del vp_window

    async def test_3_capture_tests_merged_for_linux(self):
        try:
            await self.merged_test_capture_file()
            await self.wait_n_updates(10)

            await self.merged_test_capture_bytes_free_func_hdr()
            await self.wait_n_updates(10)

            await self.merged_test_capture_bytes_subclass()
            await self.wait_n_updates(10)

            await self.merged_test_capture_file_with_format()
            await self.wait_n_updates(10)
        finally:
            await self.finalize_test_no_image()
