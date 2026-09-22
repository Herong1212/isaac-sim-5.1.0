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


class TestControllerModelsVR(XRTestVR):
    VR_PROFILE_SETTINGS: dict = {
        "render/resolutionMultiplier": 1.0  # overwrite default multiplier to avoid hitting DLSS enforcement
    }

    async def test_unit_controller_models_vr(self):
        """Launch VR at different units and test tools"""

        # self.disable_comparison()

        golden_image_source = __name__

        await self.load_stage_async(str(test_utils.get_usd_directory().joinpath("boxes/boxes.usd")))

        # Create a test profile
        async with TestVRUIProfile(self):

            self.set_param("testvrui", "/foveation/mode", "none")

            await self.wait_post_sync_async(15)

            self.set_param(
                "testvrui", "/simulatedxr/controllers/leftType", "/interaction_profiles/meta/touch_controller_quest_2"
            )
            self.set_param(
                "testvrui", "/simulatedxr/controllers/rightType", "/interaction_profiles/meta/touch_controller_quest_2"
            )

            await self.wait_post_sync_async(10)

            await self.capture_and_compare_stereo_output_async(
                "dual_meta_touch_controller_quest2", 0.001, golden_image_source
            )

            await self.wait_post_sync_async(5)

            self.set_param(
                "testvrui", "/simulatedxr/controllers/leftType", "/interaction_profiles/bytedance/pico4_controller"
            )
            self.set_param(
                "testvrui", "/simulatedxr/controllers/rightType", "/interaction_profiles/bytedance/pico4_controller"
            )

            await self.wait_post_sync_async(10)

            await self.capture_and_compare_stereo_output_async("dual_pico4_controller", 0.001, golden_image_source)

            await self.wait_post_sync_async(5)

            self.set_param("testvrui", "/simulatedxr/controllers/leftType", "/interaction_profiles/htc/vive_controller")
            self.set_param(
                "testvrui", "/simulatedxr/controllers/rightType", "/interaction_profiles/htc/vive_controller"
            )

            await self.wait_post_sync_async(10)

            await self.capture_and_compare_stereo_output_async("dual_vive_controller", 0.001, golden_image_source)

            await self.wait_post_sync_async(5)

            self.set_param(
                "testvrui", "/simulatedxr/controllers/leftType", "/interaction_profiles/htc/vive_cosmos_controller"
            )
            self.set_param(
                "testvrui", "/simulatedxr/controllers/rightType", "/interaction_profiles/htc/vive_cosmos_controller"
            )

            await self.wait_post_sync_async(10)

            await self.capture_and_compare_stereo_output_async(
                "dual_vive_cosmos_controller", 0.001, golden_image_source
            )

            await self.wait_post_sync_async(5)

            self.set_param(
                "testvrui", "/simulatedxr/controllers/leftType", "/interaction_profiles/htc/vive_focus3_controller"
            )
            self.set_param(
                "testvrui", "/simulatedxr/controllers/rightType", "/interaction_profiles/htc/vive_focus3_controller"
            )

            await self.wait_post_sync_async(5)

            await self.capture_and_compare_stereo_output_async(
                "dual_vive_focus3_controller", 0.001, golden_image_source
            )

            await self.wait_post_sync_async(10)

            self.set_param(
                "testvrui", "/simulatedxr/controllers/leftType", "/interaction_profiles/khr/simple_controller"
            )
            self.set_param(
                "testvrui", "/simulatedxr/controllers/rightType", "/interaction_profiles/khr/simple_controller"
            )

            await self.capture_and_compare_stereo_output_async("dual_simple_controller", 0.001, golden_image_source)

            await self.wait_post_sync_async(5)

            self.set_param(
                "testvrui", "/simulatedxr/controllers/leftType", "/interaction_profiles/valve/index_controller"
            )
            self.set_param(
                "testvrui", "/simulatedxr/controllers/rightType", "/interaction_profiles/valve/index_controller"
            )

            await self.wait_post_sync_async(10)

            await self.capture_and_compare_stereo_output_async(
                "dual_valve_index_controller", 0.001, golden_image_source
            )

            await self.wait_post_sync_async(5)

            await self.load_stage_async(str(test_utils.get_usd_directory().joinpath("boxes/boxesZUp.usd")))

            await self.wait_post_sync_async(15)

            self.set_param(
                "testvrui", "/simulatedxr/controllers/leftType", "/interaction_profiles/meta/touch_controller_quest_2"
            )
            self.set_param(
                "testvrui", "/simulatedxr/controllers/rightType", "/interaction_profiles/meta/touch_controller_quest_2"
            )

            await self.wait_post_sync_async(10)

            await self.capture_and_compare_stereo_output_async(
                "dual_meta_touch_controller_quest2_z_up", 0.001, golden_image_source
            )

            await self.wait_post_sync_async(5)

            self.set_param(
                "testvrui", "/simulatedxr/controllers/leftType", "/interaction_profiles/htc/vive_focus3_controller"
            )
            self.set_param(
                "testvrui", "/simulatedxr/controllers/rightType", "/interaction_profiles/htc/vive_focus3_controller"
            )

            await self.wait_post_sync_async(5)

            await self.capture_and_compare_stereo_output_async(
                "dual_vive_focus3_controller_z_up", 0.001, golden_image_source
            )

        # Ensure we run through at least a full cycle
        await self.wait_post_sync_async(3)
        self.assertEqual(test_utils.get_current_xr_profile_name(), "")
