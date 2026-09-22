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
from omni.kit.xr.core import XRCore, XRRay, XRRayQueryResult


class TestProfileFunctionality(test_utils.XRTest):
    async def test_unit_async_xr_raycast(self):
        """
        Test async XR raycast works and returns a valid result
        """

        settings = carb.settings.get_settings()
        settings.set("/xr/profile/vr/system/display", "SimulatedXR")
        settings.set("/xr/profile/vr/tools/layout", "")
        settings.set("/xr/profile/vr/gui/layers", [])
        settings.set("/xr/profile/vr/adjustForUserHeight", False)

        # Ensure we run through at least a full cycle
        await self.wait_post_sync_async(50)

        usd_path = str(test_utils.get_usd_directory().joinpath("SimpleGeometry/center_sphere.usda"))

        # Load sample scene
        async with test_utils.XRUsdStage(usd_path, keep_stage=True):

            # Request to enable a given profile
            profile_name = "vr"
            async with test_utils.EnabledXRProfile(profile_name):

                # Ensure we run through at least a full cycle
                await self.wait_post_sync_async(5)

                origin = (0, 0, 0)
                direction = (0, 1, 0)
                ray = XRRay(origin, direction, 0, 10000)
                ray_query_result: XRRayQueryResult = await XRCore.get_singleton().execute_raycast_query_async(ray)

                self.assertTrue(ray_query_result.valid)
                self.assertAlmostEqual(ray_query_result.hit_t, 46.27, delta=0.5)
