# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import carb
import omni.kit.xr.core.test_utils as test_utils
from omni.kit.xr.advertise import XRAdvertizer
from omni.kit.xr.core.test_utils import XRTest


class TestAdvertise(XRTest):
    @test_utils.opened_usd_stage()
    async def test_advertise(self):
        """Test zeroconf advertisement"""

        settings = carb.settings.get_settings()
        settings.set("/xr/profile/tabletar/system/display", "SimulatedXR")

        # Request to enable a given profile
        profile_name = "tabletar"
        async with test_utils.EnabledXRProfile(profile_name):
            # Check that profile was enabled
            self.assertEqual(test_utils.get_current_xr_profile_name(), profile_name)

            await self.wait_pre_sync_async(2)

            # now check XRAdvertizer
            zero_conf = XRAdvertizer()
            zero_conf.set_profile_name(profile_name)

            self.assertEqual(profile_name, zero_conf.get_profile_name())
            self.assertEqual(zero_conf.serviceType, "_xrstream-001._udp")
            self.assertEqual(zero_conf.servicePort, 8001)
            self.assertFalse(zero_conf.is_enabled())
            zero_conf.startZeroconf(None)
            self.assertTrue(zero_conf.is_enabled())
            zero_conf.stopZeroconf(None)
            self.assertFalse(zero_conf.is_enabled())
