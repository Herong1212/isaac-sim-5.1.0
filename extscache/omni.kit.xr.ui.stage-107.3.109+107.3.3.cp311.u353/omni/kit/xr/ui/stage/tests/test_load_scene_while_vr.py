# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.kit.xr.core.test_utils as test_utils
from omni.kit.xr.core.test_utils import TestVRProfile, XRTestVR


class TestLoadSceneWhileVR(XRTestVR):
    VR_PROFILE_SETTINGS: dict = {
        "render/resolutionMultiplier": 1.0  # overwrite default multiplier to avoid hitting DLSS enforcement
    }

    async def test_unit_load_scene_while_vr(self):
        """Launch VR and load a scene"""

        # self.disable_comparison()

        async with TestVRProfile(self) as test_profile:
            self.profile = test_profile

            await self.load_stage_async(str(test_utils.get_usd_directory().joinpath("Scaling/centimeter_scale.usda")))

            await self.capture_and_compare_stereo_output_async("load_while_vr", 0.001, __name__)
            await self.capture_and_compare_warped_output_async("load_while_vr", 0.001, __name__)
            await self.capture_and_compare_viewport_output_async("load_while_vr", 0.001, __name__)

            await self.wait_post_sync_async(20)

            self.request_disable_profile()

            # Ensure we run through at least a full cycle
            await self.wait_post_sync_async(3)
            self.assertEqual(test_utils.get_current_xr_profile_name(), "")

            self.profile = None
