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


class TestVRDuringKitStalls(XRTestVR):

    VR_PROFILE_SETTINGS: dict = {
        "render/resolutionMultiplier": 1.0  # overwrite default multiplier to avoid hitting DLSS enforcement
    }

    async def test_unit_vr_during_kit_stalls(self):
        """Launch VR and load a scene"""

        # Force kit to stall at different locations:
        # Current version of kit often does this with compiles, extension loads etc
        # In this case simulate it to check the condition variable timeouts
        # Due to lockstep enforcement between render and simulation thread there are
        # locks and condition variables between two, to ensure no deadlock occurs
        # they release automatically after a few seconds, this test checks if the
        # app is not crashing if those timeouts are hit.
        # We need those timeouts to keep the app responsive.

        async with TestVRProfile(self) as test_profile:
            self.profile = test_profile

            self.set_setting("/xr/debug/forceSimThreadStall", True)

            await self.load_stage_async(str(test_utils.get_usd_directory().joinpath("Scaling/centimeter_scale.usda")))

            await self.wait_post_sync_async(20)

            self.set_setting("/xr/debug/forceRenderThreadStall", True)

            await self.capture_and_compare_stereo_output_async("vr_kit_stall", 0.001, __name__)
            await self.capture_and_compare_viewport_output_async("vr_kit_stall", 0.001, __name__)

            await self.wait_post_sync_async(20)

            self.set_setting("/xr/debug/forceRenderThreadStall", True)

            await self.wait_post_sync_async(5)

            self.set_setting("/xr/debug/forceSimThreadStall", True)

            await self.wait_post_sync_async(5)

            await self.capture_and_compare_viewport_output_async("vr_kit_stall2", 0.001, __name__)

            await self.wait_post_sync_async(5)

            self.set_setting("/xr/debug/forceSimThreadStall", True)

            self.request_disable_profile()
            self.set_setting("/xr/debug/forceRenderThreadStall", True)

            # Ensure we run through at least a full cycle
            await self.wait_post_sync_async(3)
            self.assertEqual(test_utils.get_current_xr_profile_name(), "")

            self.profile = None
