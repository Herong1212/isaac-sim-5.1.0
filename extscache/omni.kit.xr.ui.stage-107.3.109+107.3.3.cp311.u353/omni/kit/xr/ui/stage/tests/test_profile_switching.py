# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.kit.xr.core.test_utils as test_utils
from omni.kit.xr.core.test_utils import EnabledXRProfile, XRTestVR, get_current_xr_profile_name


class TestProfileSwitching(XRTestVR):
    VR_PROFILE_SETTINGS: dict = {
        "render/resolutionMultiplier": 0.5  # overwrite default multiplier to avoid hitting DLSS enforcement
    }

    @test_utils.opened_usd_stage()
    async def test_unit_profile_switching(self):
        """Test switching between different profiles"""

        profile_name1 = "testvr"
        profile_name2 = "testvr2"

        # Create a test profile
        self.create_test_vr_profile(profile_name1)
        self.create_test_vr_profile(profile_name2)

        self.assertEqual(get_current_xr_profile_name(), "")

        # Request to enable a given profile
        async with EnabledXRProfile(profile_name1):
            # TODO: remove that wait, it is necessary because some of the Usd elements
            # of test profiles won't load (on time) without it.
            await self.wait_post_sync_async(50)
            # Check that profile was enabled
            self.assertEqual(get_current_xr_profile_name(), profile_name1)

        self.assertEqual(get_current_xr_profile_name(), "")

        # Request to enable a given profile
        async with EnabledXRProfile(profile_name2):
            # TODO: remove that wait, it is necessary because some of the Usd elements
            # of test profiles won't load (on time) without it.
            await self.wait_post_sync_async(50)
            # Check that profile was enabled
            self.assertEqual(get_current_xr_profile_name(), profile_name2)

        self.assertEqual(get_current_xr_profile_name(), "")
