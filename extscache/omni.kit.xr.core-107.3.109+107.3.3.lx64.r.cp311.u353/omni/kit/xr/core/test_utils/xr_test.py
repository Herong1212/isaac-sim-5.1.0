# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

# =================================== NOTE ====================================
# The APIs in this file are unfinished and may change in future releases
# Using these is at your own risk, and forward-compatability is not supported

import asyncio
import pathlib
from typing import Any, Optional, Sequence, Set, Union

import carb
import omni.kit.app
import omni.kit.test
import omni.kit.xr.core.imagecomparison
import omni.usd
from omni.kit.viewport.utility import get_active_viewport
from omni.kit.viewport.utility.camera_state import ViewportCameraState
from omni.kit.xr.core import XRCore, XRCoreEventType
from pxr import Gf

from .golden_image import (
    GoldenImageTest,
    QuadviewImageTest,
    StereoGoldenImageTest,
    TabletGoldenImageTest,
    ViewportGoldenImageTest,
    WarpedGoldenImageTest,
)
from .tests_directories import get_data_directory


class XRTest(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        """
        Setup: Ensure we have a clean scene and wait
        a number of frames to clear buffers.
        """

        carb.log_info("[XR] Setup test " + str(self.__class__.__name__))

        self._disable_comparison = False

        if carb.settings.get_settings().get("/xr/tests/disableComparison"):
            self._disable_comparison = True

        self._compare_success = True

        self._module = self.__class__.__module__

    async def tearDown(self):
        """
        Disable any outstanding profile and wait
        some more cycles to clear on going processes
        """

        carb.log_info("[XR] Teardown test " + str(self.__class__.__name__))

        self.request_disable_profile()
        await self.wait_post_sync_async(4)

        # Always check the image comparisons at the end of the test.  This
        # avoids needing to do the comparison in the tests itself which has
        # sometimes been missed in making new tests.
        if not self._disable_comparison:
            self.assertTrue(self._compare_success)

    def set_module(self, module: str) -> None:
        """
        Set module where to lookup files
        """
        self._module = module

    def is_linux(self) -> bool:
        """
        Check if platform is linux
        """

        import platform

        return platform.system() == "Linux"

    def disable_comparison(self):
        """
        Disable comparison for recording test images first time

        Use this function when building the test to generate outputs
        but no fail in the process
        """

        self._disable_comparison = True

    def is_comparison_disabled(self):
        """
        Returns whether comparison of golden images is disabled or not
        """

        return self._disable_comparison

    def compare_result(self, new_result: bool):
        """
        Compare new result with current XRTest success status.
        """

        self._compare_success = self._compare_success and new_result

    def get_recording_directory(self, module: Union[str, None] = None) -> pathlib.Path:
        """
        Get directory with xr recordings inside extension
        """

        return get_data_directory(module).joinpath("tests/playback_recording")

    async def wait_post_sync_async(self, count: int = 1) -> None:
        """
        Wait for the post_sync callback in XRCore

        Args:
            count: number of frames to wait
        """

        future: asyncio.Future = asyncio.Future()
        cur_count = 0
        target_count = count

        def on_post_sync(ev: carb.events.IEvent):
            nonlocal cur_count
            cur_count = cur_count + 1
            if cur_count == target_count:
                future.set_result(True)

        sub_post_sync = (
            XRCore.get_singleton()
            .get_message_bus()
            .create_subscription_to_pop_by_type(
                XRCoreEventType.post_sync_update, on_post_sync, name="Post Sync", order=-1
            )
        )

        await future
        sub_post_sync = None  # noqa: F841

        return

    async def wait_materials_loaded_async(self) -> None:
        """
        Wait until materials have been loaded
        """

        while True:
            await self.wait_post_sync_async()
            ctx = omni.usd.get_context()
            _, files_loaded, total_files = ctx.get_stage_loading_status()
            if files_loaded or total_files:
                continue
            else:
                break
            carb.log_info("[XR] Detected that all materials have been loaded")

    async def wait_pre_sync_async(self, count: int = 1) -> None:
        """
        Wait for the pre_sync callback in XRCore

        Args:
            count: number of frames to wait
        """

        future: asyncio.Future = asyncio.Future()
        cur_count = 0
        target_count = count

        def on_pre_sync(ev: carb.events.IEvent):
            nonlocal cur_count
            cur_count = cur_count + 1
            if cur_count == target_count:
                future.set_result(True)

        sub_pre_Sync = (
            XRCore.get_singleton()
            .get_message_bus()
            .create_subscription_to_pop_by_type(XRCoreEventType.pre_sync_update, on_pre_sync, name="Pre Sync", order=-1)
        )

        await future
        sub_pre_Sync = None  # noqa: F841

        return

    async def capture_and_compare_stereo_output_async(
        self,
        golden_image_name: str,
        threshold: float,
        module_name: str,
        capture_source: Optional[str] = None,
        capture_output: str = "color",
        capture_depth_range: tuple[float, float] = (0.1, 10.0),
    ) -> None:
        """
        Capture stereo image and compare against golden images
        """
        golden_image_test = StereoGoldenImageTest(
            self._disable_comparison,
            capture_source=capture_source,
            capture_output=capture_output,
            capture_depth_range=capture_depth_range,
        )
        await self.wait_post_sync_async(golden_image_test.get_frames_to_wait())
        result = await golden_image_test.capture_and_compare_output_async(golden_image_name, threshold, module_name)
        self._compare_success = self._compare_success and result

    async def capture_and_compare_tablet_output_async(
        self,
        golden_image_name: str,
        threshold: float,
        module_name: str,
        capture_source: Optional[str] = None,
        capture_output: str = "color",
        capture_depth_range: tuple[float, float] = (0.1, 10.0),
    ) -> None:
        """
        Capture tablet image and compare against golden image
        """
        golden_image_test = TabletGoldenImageTest(
            self._disable_comparison,
            capture_source=capture_source,
            capture_output=capture_output,
            capture_depth_range=capture_depth_range,
        )
        await self.wait_post_sync_async(golden_image_test.get_frames_to_wait())
        result = await golden_image_test.capture_and_compare_output_async(golden_image_name, threshold, module_name)
        self._compare_success = self._compare_success and result

    async def capture_and_compare_quadview_output_async(
        self,
        golden_image_name: str,
        threshold: float,
        module_name: str,
        capture_source: Optional[str] = None,
        capture_output: str = "color",
        capture_depth_range: tuple[float, float] = (0.1, 10.0),
    ) -> None:
        """
        Capture quadview image and compare against golden images
        """
        golden_image_test = QuadviewImageTest(
            self._disable_comparison,
            capture_source=capture_source,
            capture_output=capture_output,
            capture_depth_range=capture_depth_range,
        )
        await self.wait_post_sync_async(golden_image_test.get_frames_to_wait())
        result = await golden_image_test.capture_and_compare_output_async(golden_image_name, threshold, module_name)
        self._compare_success = self._compare_success and result

    async def capture_and_compare_warped_output_async(
        self,
        golden_image_name: str,
        threshold: float,
        module_name: str,
        capture_output: str = "color",
        capture_depth_range: tuple[float, float] = (0.1, 10.0),
    ) -> None:
        """
        Capture warped image and compare against golden images
        """
        golden_image_test = WarpedGoldenImageTest(
            self._disable_comparison, capture_output=capture_output, capture_depth_range=capture_depth_range
        )
        await self.wait_post_sync_async(golden_image_test.get_frames_to_wait())
        result = await golden_image_test.capture_and_compare_output_async(golden_image_name, threshold, module_name)
        self._compare_success = self._compare_success and result

    async def capture_and_compare_viewport_output_async(
        self,
        golden_image_name: str,
        threshold: float,
        module_name: str,
    ) -> None:
        """
        Capture stereo image and compare against golden images
        """

        golden_image_test = ViewportGoldenImageTest(self._disable_comparison)
        await self.wait_post_sync_async(golden_image_test.get_frames_to_wait())
        result = await golden_image_test.capture_and_compare_output_async(golden_image_name, threshold, module_name)
        self._compare_success = self._compare_success and result

    async def new_stage_async(self) -> None:
        """
        Create new stage in the app and wait until it is opened
        """

        ctx = omni.usd.get_context()
        await ctx.new_stage_async()

    async def load_stage_async(self, file_path: str) -> None:
        """
        Load a stage asynchronously
        """

        # make sure there are no pending material loads
        await self.wait_post_sync_async()

        await self.wait_materials_loaded_async()

        ctx = omni.usd.get_context()
        await ctx.open_stage_async(file_path)

        # ensure material loads have started
        await self.wait_post_sync_async(3)

        # ensure materials are present
        await self.wait_materials_loaded_async()

        await self.wait_post_sync_async(100)

    def request_enable_profile(self, name: str) -> None:
        """
        Request to enable a profile

        Args:
            name:      name of the profile
        """

        XRCore.get_singleton().request_enable_profile(name)

    def request_disable_profile(self) -> None:
        """
        Disable any XR profile
        """

        XRCore.get_singleton().request_disable_profile()

    def set_xr_camera(self, position: Gf.Vec3d, target: Gf.Vec3d):
        """
        Set the camera location
        """

        coordinate_system = XRCore.get_singleton().get_coordinate_system()
        pose = Gf.Matrix4d().SetLookAt(position, target, coordinate_system.get_up_vector()).GetInverse()
        XRCore.get_singleton().schedule_set_camera(pose)

    def set_viewport_camera(self, position: Gf.Vec3d, target: Gf.Vec3d):
        """
        Set the camera location
        """
        viewport = get_active_viewport()
        viewport_cam_state = ViewportCameraState(camera_path=viewport.camera_path, viewport=viewport)
        viewport_cam_state.set_position_world(position, True)
        viewport_cam_state.set_target_world(target, True)

        return viewport

    # Helper function to set the physical world Matrix with a XRPose
    async def set_physical_world_matrix(self, pymatrix):
        """
        Set the physical world Matrix with a XRPose
        """

        core = XRCore.get_singleton()
        profile = core.get_profile("vr")
        device = profile.get_device("xrdisplaydevice0")
        profile.set_physical_world_to_world_anchor_transform_to_match_xr_device(pymatrix, device)

    async def wait_until_event_set(self, event: asyncio.Event):
        await event.wait()  # TODO - why do we have a 1-liner function used once that's in the library?

    def set_param(self, profile: str, path: str, value: Any):
        settings = carb.settings.get_settings()

        full_path = "/xr/profile/" + profile + path
        settings.set(full_path, value)

    def set_setting(self, path: str, value: Any):
        settings = carb.settings.get_settings()
        settings.set(path, value)
