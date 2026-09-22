## Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
__all__ = ["TestRayQuery"]

from pathlib import Path
import carb

import omni.kit.test
from omni.ui.tests.test_base import OmniUiTest
import omni.usd

from omni.kit.widget.viewport import ViewportWidget


CURRENT_PATH = Path(carb.tokens.get_tokens_interface().resolve("${omni.kit.widget.viewport}/data")).absolute().resolve()
TEST_FILES_DIR = CURRENT_PATH.joinpath('tests')
USD_FILES_DIR = TEST_FILES_DIR.joinpath('usd')

TEST_WIDTH, TEST_HEIGHT = 320, 180


class TestRayQuery(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()

    # After running each test
    async def tearDown(self):
        await super().tearDown()
        await self.linux_gpu_shutdown_workaround()

    async def linux_gpu_shutdown_workaround(self, usd_context_name : str = ''):
        await self.wait_n_updates(10)
        omni.usd.release_all_hydra_engines(omni.usd.get_context(usd_context_name))
        await self.wait_n_updates(10)

    async def open_usd_file(self, filename: str, resolved: bool = False):
        usd_context = omni.usd.get_context()
        usd_path = str(USD_FILES_DIR.joinpath(filename) if not resolved else filename)
        await usd_context.open_stage_async(usd_path)
        return usd_context

    async def __test_ray_query(self, camera_path: str):
        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT, block_devices=False)

        usd_context = await self.open_usd_file('ray_query.usda')
        self.assertIsNotNone(usd_context.get_stage())

        window_flags = omni.ui.WINDOW_FLAGS_NO_COLLAPSE
        window_flags |= omni.ui.WINDOW_FLAGS_NO_RESIZE
        window_flags |= omni.ui.WINDOW_FLAGS_NO_CLOSE
        window_flags |= omni.ui.WINDOW_FLAGS_NO_SCROLLBAR
        window_flags |= omni.ui.WINDOW_FLAGS_NO_TITLE_BAR

        vp_window, viewport_widget = None, None
        try:
            vp_window = omni.ui.Window("Viewport", width=TEST_WIDTH, height=TEST_HEIGHT, flags=window_flags)
            with vp_window.frame:
                viewport_widget = ViewportWidget(resolution=(TEST_WIDTH, TEST_HEIGHT))

            results = []

            def query_completed(*args):
                results.append(args)

            viewport_api = viewport_widget.viewport_api
            viewport_api.camera_path = camera_path

            # 1:1 conform of render and viewport
            await self.wait_n_updates(10)
            viewport_api.request_query((193, 123), query_completed)
            await self.wait_n_updates(15)

            # test with half height
            viewport_api.resolution = TEST_WIDTH, TEST_HEIGHT * 0.5
            await self.wait_n_updates(10)
            viewport_api.request_query((193, 78), query_completed)
            await self.wait_n_updates(15)

            # test with half width
            viewport_api.resolution = TEST_WIDTH * 0.5, TEST_HEIGHT
            await self.wait_n_updates(10)
            viewport_api.request_query((96, 106), query_completed)
            await self.wait_n_updates(15)

            self.assertEqual(len(results), 3)
            for args in results:
                self.assertEqual(args[0], "/World/Xform/FG")
                # Compare integer in a sane range that must be toward the lower-right corner of the object
                iworld_pos = [int(v) for v in args[1]]
                self.assertTrue(iworld_pos[0] >= 46 and iworld_pos[0] <= 50)
                self.assertTrue(iworld_pos[1] >= -50 and iworld_pos[1] <= -46)
                self.assertTrue(iworld_pos[2] == 0)
        finally:
            if viewport_widget:
                viewport_widget.destroy()
                viewport_widget = None
            if vp_window:
                vp_window.destroy()
                vp_window = None
            await self.finalize_test_no_image()

    async def test_perspective_ray_query(self):
        """Test request_query API with a perpective camera"""
        await self.__test_ray_query("/World/Xform/Camera")

    async def test_orthographic_ray_query(self):
        """Test request_query API with an orthographic camera"""
        await self.__test_ray_query("/OmniverseKit_Front")
