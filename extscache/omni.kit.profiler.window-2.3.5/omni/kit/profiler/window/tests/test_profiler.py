## Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import pathlib

import omni.kit.app
import omni.kit.commands
import omni.kit.test
import omni.ui as ui
from omni.ui.tests.test_base import OmniUiTest
from pxr import Gf, Kind, Sdf
from ..capture_browser import is_external_build


class TestProfiler(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()

        ext_path = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
        self._golden_img_dir = pathlib.Path(ext_path).joinpath("data/tests/golden_img")

    # After running each test
    async def tearDown(self):
        await super().tearDown()

    # Test(s)
    async def test_profiler_ui(self):
        window = omni.kit.profiler.window.get_window()
        window.visible = True

        await omni.kit.app.get_app().next_update_async()

        window = omni.ui.Workspace.get_window("Profiler")
        await self.docked_test_window(window=window, width=window.width, height=window.height)

        if is_external_build():
            await self.finalize_test(
                golden_img_dir=self._golden_img_dir, golden_img_name="test_profiler_external_build.png", use_log=False
            )
        else:
            await self.finalize_test(
                golden_img_dir=self._golden_img_dir, golden_img_name="test_profiler.png", use_log=False
            )
