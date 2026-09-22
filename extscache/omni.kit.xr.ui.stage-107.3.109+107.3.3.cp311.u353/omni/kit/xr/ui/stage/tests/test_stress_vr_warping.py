# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import carb.settings
import omni.kit.xr.core.test_utils as test_utils
from omni.kit.xr.core.test_utils import TestVRProfile, XRTestVR


class TestProfileStressTestWarping(XRTestVR):
    VR_PROFILE_SETTINGS: dict = {
        "render/resolutionMultiplier": 1.0  # overwrite default multiplier to avoid hitting DLSS enforcement
    }

    async def test_unit_stress_test_warping(self):
        """Stress test warping with different render settings"""

        # self.disable_comparison()

        golden_image_source = __name__

        await self.load_stage_async(str(test_utils.get_usd_directory().joinpath("Scaling/centimeter_scale.usda")))

        # Wait a bit
        await self.wait_post_sync_async(10)

        # Create a test profile
        async with TestVRProfile(self):

            settings = carb.settings.get_settings()

            # Test Default

            await self.capture_and_compare_warped_output_async("stress_vr_warping_1", 0.001, golden_image_source)

            # Test GI

            settings.set("rtx/indirectDiffuse/enabled", True)
            await self.wait_post_sync_async(20)
            await self.capture_and_compare_warped_output_async("stress_vr_warping_2", 0.001, golden_image_source)
