# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import carb
import omni.kit.xr.core.test_utils as test_utils
import omni.usd
from omni.kit.xr.core.test_utils import TestVRProfile, XRTestVR


class TestSelectionOutline(XRTestVR):

    golden_image_threshold = 0.00019

    async def setUp(self):
        """
        Setup: Ensure we have a clean scene and wait
        a number of frames to clear buffers.
        """
        await super().setUp()
        await self.new_stage_async()
        await self.wait_post_sync_async(40)

    async def test_no_selection_outline_if_nothing_selected_as_default(self) -> None:
        async with TestVRProfile(self) as test_vr_profile:
            settings = carb.settings.get_settings()
            settings.set("/xr/profile/" + test_vr_profile.get_name() + "/render/resolutionMultiplier", 1.0)
            await self.load_stage_and_compare_images(
                "selection_outline_off_as_default", False, test_vr_profile.get_name(), False
            )

    async def test_selection_outline_when_prims_selected_as_default(self) -> None:
        async with TestVRProfile(self) as test_vr_profile:
            settings = carb.settings.get_settings()
            settings.set("/xr/profile/" + test_vr_profile.get_name() + "/render/resolutionMultiplier", 1.0)
            await self.load_stage_and_compare_images(
                "selection_outline_on_as_default", True, test_vr_profile.get_name(), False
            )

    async def test_no_selection_outline_when_prims_selected_with_hidden_outline_setting(self) -> None:
        async with TestVRProfile(self) as test_vr_profile:
            settings = carb.settings.get_settings()
            settings.set("/xr/profile/" + test_vr_profile.get_name() + "/render/resolutionMultiplier", 1.0)
            await self.load_stage_and_compare_images(
                "selection_outline_off_because_hidden_outline", True, test_vr_profile.get_name(), True
            )

    async def load_stage_and_compare_images(
        self, golden_image_name: str, select_prims: bool, profile_name: str, hide_prims: bool
    ) -> None:
        await self.wait_post_sync_async(20)
        await self.load_stage_async(
            str(test_utils.get_usd_directory("omni.kit.xr.profile.common").joinpath("prims.usd"))
        )
        await self.wait_post_sync_async(20)

        if select_prims:
            omni.usd.get_context().get_selection().set_selected_prim_paths(
                ["/World/Cube", "/World/Cylinder", "/World/Cone", "/World/Capsule", "/World/Disk"], True
            )

        settings = carb.settings.get_settings()
        settings.set(f"/xr/profile/{profile_name}/viewport/outline/hidden", hide_prims)

        hideGrid: bool = settings.get(f"/xr/profile/{profile_name}/viewport/grid/hidden")
        settings.set("/app/viewport/grid/enabled", not hideGrid)

        hideOutline: bool = settings.get(f"/xr/profile/{profile_name}/viewport/outline/hidden")
        settings.set("/app/viewport/outline/enabled", not hideOutline)

        await self.capture_and_compare_warped_output_async(golden_image_name, self.golden_image_threshold, __name__)
        await self.wait_post_sync_async(20)
