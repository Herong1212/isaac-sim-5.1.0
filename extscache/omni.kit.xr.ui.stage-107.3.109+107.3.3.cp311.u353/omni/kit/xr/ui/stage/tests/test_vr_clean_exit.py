# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni
import omni.kit.xr.core.test_utils as test_utils
from omni.kit.viewport.utility import get_active_viewport
from omni.kit.xr.core.test_utils import TestVRProfile, XRTestVR


class TestCleanAtExit(XRTestVR):
    VR_PROFILE_SETTINGS: dict = {
        "render/resolutionMultiplier": 0.5  # overwrite default multiplier to avoid hitting DLSS enforcement
    }

    @test_utils.opened_usd_stage()
    async def test_unit_clean_at_exit(self):
        """Launch test profile and check if it exits cleanly"""

        # Create a test profile
        self.create_test_vr_profile("testvr")

        # Record names of layers and prims before
        pre_layer_names = test_utils.XRUsdStage.get_layer_names()
        self.assertFalse(test_utils.XRUsdStage.has_xr_gui_prims())

        # Request to enable a given profile
        profile_name = "testvr"

        async with test_utils.EnabledXRProfile(profile_name):
            # TODO: remove that wait, it is necessary because some of the Usd elements
            # of test profiles won't load (on time) without it.
            await self.wait_post_sync_async(50)
            # Check that profile was enabled
            self.assertEqual(test_utils.get_current_xr_profile_name(), profile_name)

        post_layer_names = test_utils.XRUsdStage.get_layer_names()

        self.assertEqual(test_utils.get_current_xr_profile_name(), "")

        self.assertSetEqual(pre_layer_names, post_layer_names)
        self.assertFalse(test_utils.XRUsdStage.has_xr_gui_prims())
