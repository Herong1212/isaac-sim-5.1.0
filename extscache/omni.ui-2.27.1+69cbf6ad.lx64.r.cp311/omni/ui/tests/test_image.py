## Copyright (c) 2019-2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
from .test_base import OmniUiTest
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from functools import partial
from pathlib import Path
import asyncio
import carb
import omni.kit.app
import omni.ui as ui
import os
import unittest

CURRENT_PATH = Path(__file__).parent
DATA_PATH = CURRENT_PATH.parent.parent.parent.joinpath("data")


class TestImage(OmniUiTest):
    """Testing ui.Image"""

    async def setUp(self):
        carb.settings.get_settings().set_bool("/persistent/exts/omni.ui/Image/generateMips", True)

    async def tearDown(self):
        # make sure persistant settting doesn't leak to other tests
        carb.settings.get_settings().set_bool("/persistent/exts/omni.ui/Image/generateMips", False)

    async def test_general(self):
        """Testing general properties of ui.Image"""
        window = await self.create_test_window()

        f = asyncio.Future()

        def on_image_progress(future: asyncio.Future, progress):
            if progress >= 1:
                if not future.done():
                    future.set_result(None)

        with window.frame:
            ui.Image(f"{DATA_PATH}/tests/red.png", progress_changed_fn=partial(on_image_progress, f))

        # Wait the image to be loaded
        await f

        await self.finalize_test()

    async def test_broken_svg(self):
        """Testing ui.Image doesn't crash when the image is broken."""
        window = await self.create_test_window()

        def build():
            ui.Image(f"{DATA_PATH}/tests/broken.svg")

        window.frame.set_build_fn(build)

        # Call build
        await omni.kit.app.get_app().next_update_async()

        # Attempts to load the broken file. The error message is "Failed to load the texture:"
        await omni.kit.app.get_app().next_update_async()

        # Recall build
        window.frame.rebuild()
        await omni.kit.app.get_app().next_update_async()

        # Second attempt to load the broken file. Second error message is expected.
        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_imagewithprovider(self):
        # Because PIL works differently in Windows and Liniux.
        # TODO: Use something else for the rasterization of the text
        return

        """Testing ui.Image doesn't crash when the image is broken."""
        window = await self.create_test_window()

        image_width = 256
        image_height = 256
        upscale = 2

        black = (0, 0, 0, 255)
        white = (255, 255, 255, 255)
        font_path = os.path.normpath(
            carb.tokens.get_tokens_interface().resolve("${kit}/resources/fonts/roboto_medium.ttf")
        )
        font_size = 25
        font = ImageFont.truetype(font_path, font_size)

        image = Image.new("RGBA", (image_width * upscale, image_height * upscale), white)
        draw = ImageDraw.Draw(image)
        # draw.fontmode = "RGB"
        draw.text(
            (0, image_height),
            "The quick brown fox jumps over the lazy dog",
            fill=black,
            font=font,
        )

        # Convert image to Image Provider
        pixels = [int(c) for p in image.getdata() for c in p]
        image_provider = ui.ByteImageProvider()
        image_provider.set_bytes_data(pixels, [image_width * upscale, image_height * upscale])

        with window.frame:
            with ui.HStack():
                ui.Spacer(width=0.5)
                ui.ImageWithProvider(
                    image_provider,
                    fill_policy=ui.IwpFillPolicy.IWP_STRETCH,
                    width=image_width,
                    height=image_height,
                    pixel_aligned=True,
                )

        # Second attempt to load the broken file. Second error message is expected.
        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_imagewithprovider_with_no_valid_style(self):
        """This is to test ImageWithProvider is not crash when style is not defined and image_url is not defined"""
        window = await self.create_test_window()
        with window.frame:
            ui.ImageWithProvider(
                height=200,
                width=200,
                fill_policy=ui.IwpFillPolicy.IWP_PRESERVE_ASPECT_FIT,
                style_type_name_override="Graph.Node.Port")

        for _ in range(2):
            await omni.kit.app.get_app().next_update_async()
        await self.finalize_test_no_image()

    async def test_destroy(self):
        """Testing creating and destroying ui.Image"""
        window = await self.create_test_window()

        with window.frame:
            ui.Image(f"{DATA_PATH}/tests/red.png")

            # It will immediately kill ui.Image
            ui.Spacer()

        # Several frames to make sure it doesn't crash
        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()

        # Another way to destroy it
        with window.frame:
            # The image is destroyed, but we hold it to make sure it doesn't
            # crash
            ui.Image(f"{DATA_PATH}/tests/red.png").destroy()

        # Several frames to make sure it doesn't crash
        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()

        await self.finalize_test_no_image()

    async def test_byteimageprovider(self):
        """Testing creating ui.ByteImageProvider"""
        window = await self.create_test_window()

        bytes = [0, 0, 0, 255, 255, 0, 0, 255, 0, 255, 0, 255, 0, 0, 255, 255]
        resolution = [2, 2]

        with window.frame:
            ui.ImageWithProvider(
                ui.ByteImageProvider(bytes, resolution),
                fill_policy=ui.IwpFillPolicy.IWP_STRETCH,
            )

        await self.finalize_test()

    async def test_dynamictextureprovider(self):
        """Testing creating ui.DynamicTextureProvider"""
        window = await self.create_test_window()

        bytes = [0, 0, 0, 255, 255, 0, 0, 255, 0, 255, 0, 255, 0, 0, 255, 255]
        resolution = [2, 2]
        textureprovider = ui.DynamicTextureProvider("textureX")
        textureprovider.set_bytes_data(bytes, resolution)
        with window.frame:
            ui.ImageWithProvider(
                textureprovider,
                fill_policy=ui.IwpFillPolicy.IWP_STRETCH,
            )

        resource = textureprovider.get_managed_resource()
        self.assertIsNotNone(resource)

        await self.finalize_test()

    def _warpAvailable():
        try:
            import warp as wp
            return True
        except ModuleNotFoundError:
            return False

    @unittest.skipIf(not _warpAvailable(), "warp module not found")
    async def test_byteimageprovider_from_warp(self):
        """Testing creating ui.ByteImageProvider with bytes from gpu"""
        window = await self.create_test_window()

        import warp as wp

        @wp.kernel
        def checkerboard(pixels: wp.array(dtype=wp.uint8, ndim=3), size_x: wp.int32, size_y: wp.int32, num_channels: wp.int32):
            x, y, c = wp.tid()
            value = wp.uint8(0)
            if (x / 4) % 2 == (y / 4) % 2:
                value = wp.uint8(255)
            pixels[x, y, c] = value

        size_x = 256
        size_y = 256
        num_channels = 4

        texture_array = wp.zeros(shape=(size_x, size_y, num_channels), dtype=wp.uint8)

        wp.launch(kernel=checkerboard, dim=(size_x, size_y, num_channels), inputs=[texture_array, size_x, size_y, num_channels])

        provider = ui.ByteImageProvider()
        # Test switching between host and gpu source data
        provider.set_bytes_data([128 for _ in range(size_x * size_y * num_channels)], [size_x, size_y])
        provider.set_bytes_data_from_gpu(texture_array.ptr, [size_x, size_y])

        with window.frame:
            ui.ImageWithProvider(
                provider,
                fill_policy=ui.IwpFillPolicy.IWP_STRETCH,
            )

        await self.finalize_test()

    async def test_imageprovider_single_channel(self):
        """Test single channel image with attempt to use unsupported mipmapping"""
        window = await self.create_test_window()
        provider = ui.RasterImageProvider()
        provider.source_url = DATA_PATH.joinpath("tests", "single_channel.jpg").as_posix()
        provider.max_mip_levels = 2

        with window.frame:
            ui.ImageWithProvider(
                provider,
                fill_policy=ui.IwpFillPolicy.IWP_STRETCH,
            )

        # wait for image to load
        await asyncio.sleep(2)

        await self.finalize_test()

    async def test_image_mipmapping(self):
        import omni.kit.ui_test as ui_test
        from omni.kit.test_suite.helpers import wait_stage_loading

        window = await self.create_test_window(block_devices=False, width=522, height=800)
        with window.frame:
            with ui.VStack(style={"margin": 1}):
                image_source = "resources/desktop-icons/omniverse_512.png"
                ui.Image(image_source, width=512, height=512)
                with ui.HStack():
                    ui.Image(image_source, width=256, height=256)

                    with ui.VStack():
                        for i in range(0, 2):
                            ui.Image(image_source, width=128, height=128)

                    with ui.VStack():
                        for i in range(0, 4):
                            ui.Image(image_source, width=64, height=64)

                    with ui.VStack():
                        for i in range(0, 8):
                            ui.Image(image_source, width=32, height=32)

                    with ui.VStack():
                        for i in range(0, 16):
                            ui.Image(image_source, width=16, height=16)

                    with ui.VStack():
                        for i in range(0, 32):
                            ui.Image(image_source, width=8, height=8)

                    with ui.VStack():
                        for i in range(0, 64):
                            ui.Image(image_source, width=4, height=4)

        await wait_stage_loading()
        await self.finalize_test(golden_img_name="omni.ui.tests.TestImage.test_image_mipmapping.png")
