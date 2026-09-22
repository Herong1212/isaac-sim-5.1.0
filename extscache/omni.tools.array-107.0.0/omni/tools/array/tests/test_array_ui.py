# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import pathlib

import omni.kit.app
import omni.kit.commands
import omni.kit.test
from omni.ui.tests.test_base import OmniUiTest

from ..action_window import ActionWindow

EXTENSION_FOLDER_PATH = pathlib.Path(
    omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
)
DATA_DIR = EXTENSION_FOLDER_PATH.joinpath("omni/tools/array/tests/data")


class TestArrayUIWindow(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        self._golden_img_dir = DATA_DIR.absolute().joinpath("golden_img").absolute()
        self._action_window = ActionWindow()

    # After running each test
    async def tearDown(self):
        await super().tearDown()
        self._action_window.clean()
        self._action_window = None

    async def capture_golden_image(self, filename):
        import omni.renderer_capture

        capture_next_frame = omni.renderer_capture.acquire_renderer_capture_interface().capture_next_frame_swapchain
        wait_async_capture = omni.renderer_capture.acquire_renderer_capture_interface().wait_async_capture

        capture_next_frame(str(self._golden_img_dir.joinpath(filename)))

        await omni.kit.app.get_app().next_update_async()

        wait_async_capture()

    # Test the array tool UI with options collapsed
    async def test_window_options_collapsed(self):
        self._action_window.show()
        self._action_window._options.collapsed = True
        window = self._action_window._window

        await self.docked_test_window(window=window, width=400, height=570)

        # This is here to update the golden image.  NEVER CHECK IN WITH THE FOLLOWING LINE UNCOMMENTED
        # await self.capture_golden_image("test_window_collapsed.png")

        await self.finalize_test(
            use_log=True, golden_img_dir=self._golden_img_dir, golden_img_name="test_window_collapsed.png"
        )

        self._action_window.hide()

    # Test the array tool UI with options expanded
    async def test_window_options_expanded(self):
        self._action_window.show()
        self._action_window._options.collapsed = False
        window = self._action_window._window

        await self.docked_test_window(window=window, width=400, height=570)

        # This is here to update the golden image.  NEVER CHECK IN WITH THE FOLLOWING LINE UNCOMMENTED
        # await self.capture_golden_image("test_window_expanded.png")

        await self.finalize_test(
            use_log=True, golden_img_dir=self._golden_img_dir, golden_img_name="test_window_expanded.png"
        )

        self._action_window.hide()
