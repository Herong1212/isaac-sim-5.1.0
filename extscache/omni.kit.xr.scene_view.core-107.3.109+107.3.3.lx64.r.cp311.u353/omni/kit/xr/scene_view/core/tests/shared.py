# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["XRSceneViewTest", "EXT_ROOT", "IMG_ROOT"]

from pathlib import Path

import carb
import omni.ui as ui
from omni.kit.xr.core.test_utils import XRTestVR, XRUsdStage
from omni.kit.xr.scene_view.core import XRSceneView
from pxr.Gf import Vec3d

EXT_ROOT = Path(carb.tokens.get_tokens_interface().resolve("${omni.kit.xr.scene_view.core}"))  # type: ignore
IMG_ROOT = EXT_ROOT.joinpath("data/tests/images")


class XRSceneViewTest(XRTestVR):
    ACCEPTABLE_GOLDEN_THRESHOLD: float = 6e-4
    TEX_SYNC_FRAMES = 80
    UI_APPEARANCE_DELAY = 7
    WINDOW_SIZE = (1024, 1024)

    async def setUp(self):  # type: ignore
        await super().setUp()

        from omni.kit.viewport.utility import get_active_viewport_window

        self._viewport_window = get_active_viewport_window()  # type: ignore

        assert self._viewport_window
        if self._viewport_window:
            self._viewport_window.position_x = 0  # type: ignore
            self._viewport_window.position_y = 0  # type: ignore
            self._viewport_window.width = self.WINDOW_SIZE[0]  # type: ignore
            self._viewport_window.height = self.WINDOW_SIZE[1]  # type: ignore
            self._viewport_window.viewport_api.resolution = (self.WINDOW_SIZE[0], self.WINDOW_SIZE[1])

        await self.wait_post_sync_async()

        async with XRUsdStage(keep_stage=True):
            # Set up the UI viewport junk
            self._frame: ui.Frame = self._viewport_window.get_frame("test xr scene view")
            with self._frame:
                self._xr_scene_view = XRSceneView()

            if self._viewport_window.viewport_api is not None:
                self._viewport_window.viewport_api.add_scene_view(self._xr_scene_view)

            self._has_scene_view = True
            self.set_viewport_camera(Vec3d(25, 25, 150), Vec3d(0, 0, 0))
            await self.wait_post_sync_async()

    async def tear_down_scene_view(self):
        if not self._has_scene_view:
            return

        if self._xr_scene_view is not None:
            self._xr_scene_view.scene.clear()
            self._xr_scene_view.destroy()

        self._frame.clear()

        if self._viewport_window is not None:
            if self._viewport_window.viewport_api is not None:
                self._viewport_window.viewport_api.remove_scene_view(self._xr_scene_view)

        self._xr_scene_view = None

        await self.wait_post_sync_async()

        self._has_scene_view = False

    async def tearDown(self):
        await self.tear_down_scene_view()

        del self._frame
        del self._xr_scene_view
        del self._viewport_window

        await super().tearDown()
