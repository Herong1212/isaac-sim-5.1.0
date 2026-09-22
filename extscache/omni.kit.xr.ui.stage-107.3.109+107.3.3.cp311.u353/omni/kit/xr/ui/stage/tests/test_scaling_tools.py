# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.kit.xr.core.test_utils as test_utils
from omni.kit.xr.core.test_utils import TestVRUIProfile, XRTestVR


class TestScalingVR(XRTestVR):

    VR_PROFILE_SETTINGS: dict = {"render/resolutionMultiplier": 0.5}

    async def test_unit_scaling_tools_vr_no_usdrt(self):
        """Launch VR at different units and test tools no usdrt"""

        self.set_setting("/xr/usdrt/enabled", False)
        await self.wait_post_sync_async(3)
        await self.test_unit_scaling_tools_vr()
        await self.wait_post_sync_async(3)
        self.set_setting("/xr/usdrt/enabled", True)

    async def test_unit_scaling_tools_vr(self):
        """Launch VR at different units and test tools"""

        golden_image_source = __name__

        # self.disable_comparison()

        # Create a test profile
        async with TestVRUIProfile(self):

            await self.wait_post_sync_async(10)

            # Test meter scale
            await self.load_stage_async(str(test_utils.get_usd_directory().joinpath("Scaling/meter_scale.usda")))

            self.set_param("testvrui", "/foveation/mode", "none")

            self.set_param(
                "testvrui", "/simulatedxr/controllers/leftType", "/interaction_profiles/meta/touch_controller_quest_2"
            )
            self.set_param(
                "testvrui", "/simulatedxr/controllers/rightType", "/interaction_profiles/meta/touch_controller_quest_2"
            )

            await self.wait_post_sync_async(15)

            await self.capture_and_compare_stereo_output_async("meter_scale", 0.0001, golden_image_source)

            await self.wait_post_sync_async(5)

            self.set_param("testvrui", "/simulatedxr/controllers/leftType", "/interaction_profiles/htc/vive_controller")
            self.set_param(
                "testvrui", "/simulatedxr/controllers/rightType", "/interaction_profiles/htc/vive_controller"
            )

            await self.wait_post_sync_async(10)

            await self.capture_and_compare_stereo_output_async("meter_scale_vive", 0.0001, golden_image_source)

            await self.wait_post_sync_async(5)

            self.set_param("testvrui", "/tooltips/visible", True)

            await self.wait_post_sync_async(10)

            await self.capture_and_compare_stereo_output_async("meter_scale_tooltips", 0.0001, golden_image_source)
            self.set_param("testvrui", "/tooltips/visible", False)

            await self.wait_post_sync_async(5)

            # Test centimeter meter scale
            await self.load_stage_async(str(test_utils.get_usd_directory().joinpath("Scaling/centimeter_scale.usda")))

            self.set_param(
                "testvrui", "/simulatedxr/controllers/leftType", "/interaction_profiles/meta/touch_controller_quest_2"
            )
            self.set_param(
                "testvrui", "/simulatedxr/controllers/rightType", "/interaction_profiles/meta/touch_controller_quest_2"
            )

            await self.wait_post_sync_async(15)

            await self.capture_and_compare_stereo_output_async("centimeter_scale", 0.0001, golden_image_source)

            await self.wait_post_sync_async(5)

            self.set_param("testvrui", "/simulatedxr/controllers/leftType", "/interaction_profiles/htc/vive_controller")
            self.set_param(
                "testvrui", "/simulatedxr/controllers/rightType", "/interaction_profiles/htc/vive_controller"
            )

            await self.wait_post_sync_async(10)

            await self.capture_and_compare_stereo_output_async("centimeter_scale_vive", 0.0001, golden_image_source)

            await self.wait_post_sync_async(5)

            self.set_param("testvrui", "/tooltips/visible", True)

            await self.wait_post_sync_async(10)

            await self.capture_and_compare_stereo_output_async("centimeter_scale_tooltips", 0.0001, golden_image_source)
            self.set_param("testvrui", "/tooltips/visible", False)

            await self.wait_post_sync_async(5)

            # Test millimeter meter scale
            await self.load_stage_async(str(test_utils.get_usd_directory().joinpath("Scaling/millimeter_scale.usda")))

            self.set_param(
                "testvrui", "/simulatedxr/controllers/leftType", "/interaction_profiles/meta/touch_controller_quest_2"
            )
            self.set_param(
                "testvrui", "/simulatedxr/controllers/rightType", "/interaction_profiles/meta/touch_controller_quest_2"
            )

            await self.wait_post_sync_async(15)

            await self.capture_and_compare_stereo_output_async("millimeter_scale", 0.0001, golden_image_source)

            await self.wait_post_sync_async(5)

            self.set_param("testvrui", "/simulatedxr/controllers/leftType", "/interaction_profiles/htc/vive_controller")
            self.set_param(
                "testvrui", "/simulatedxr/controllers/rightType", "/interaction_profiles/htc/vive_controller"
            )

            await self.capture_and_compare_stereo_output_async("millimeter_scale_vive", 0.0001, golden_image_source)

            await self.wait_post_sync_async(5)

            self.set_param("testvrui", "/tooltips/visible", True)

            await self.wait_post_sync_async(10)

            await self.capture_and_compare_stereo_output_async("millimeter_scale_tooltips", 0.0001, golden_image_source)
            self.set_param("testvrui", "/tooltips/visible", False)

            await self.wait_post_sync_async(5)

        # Ensure we run through at least a full cycle
        await self.wait_post_sync_async(3)
        self.assertEqual(test_utils.get_current_xr_profile_name(), "")
