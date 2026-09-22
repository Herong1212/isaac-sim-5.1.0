## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
from ..imageview import ImageView
from omni.ui.tests.test_base import OmniUiTest
from functools import partial
from pathlib import Path
import omni.kit.app

import asyncio

class TestImageview(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        extension_path = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
        self._golden_img_dir = Path(extension_path).joinpath("data").joinpath("tests").absolute()

    # After running each test
    async def tearDown(self):
        self._golden_img_dir = None
        await super().tearDown()

    async def test_general(self):
        window = await self.create_test_window()
        f = asyncio.Future()

        def on_image_progress(future: asyncio.Future, progress):
            if progress >= 1:
                if not future.done():
                    future.set_result(None)

        with window.frame:
            image_view = ImageView(f"{self._golden_img_dir.joinpath('lenna.png')}")
            image_view.set_progress_changed_fn(partial(on_image_progress, f))

        # Wait the image to be loaded
        await f

        await self.finalize_test(golden_img_dir=self._golden_img_dir)
