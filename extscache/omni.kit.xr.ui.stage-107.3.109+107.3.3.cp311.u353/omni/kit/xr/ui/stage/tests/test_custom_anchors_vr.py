# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import carb
import omni
import omni.kit.xr.core.test_utils as test_utils
from omni.kit.xr.core import XRCore
from omni.kit.xr.core.test_utils import TestVRProfile, XRTestVR
from pxr import Usd, UsdGeom


class TestCustomAnchorsVR(XRTestVR):
    ACCEPTABLE_GOLDEN_THRESHOLD: float = 6e-4
    VR_PROFILE_SETTINGS: dict = {
        "render/resolutionMultiplier": 1.0  # overwrite default multiplier to avoid hitting DLSS enforcement
    }

    async def test_unit_custom_anchors(self):
        """Launch VR and load a scene"""

        # self.disable_comparison()

        await self.load_stage_async(str(test_utils.get_usd_directory().joinpath("Scaling/centimeter_scale.usda")))

        # Wait a bit
        await self.wait_post_sync_async(10)

        # Create a test profile
        async with TestVRProfile(self) as test_profile:

            await self.wait_post_sync_async(10)

            anchor_mode_settings_path = f"/xr/profile/{test_profile.get_name()}/anchorMode"
            anchor_name_settings_path = f"/xrstage/profile/{test_profile.get_name()}/customAnchor"

            stage = omni.usd.get_context().get_stage()

            with Usd.EditContext(stage, stage.GetSessionLayer()):
                # Setup first anchor prim
                anchor_prim = UsdGeom.Xform.Define(stage, "/World/Anchor1")
                translate_op = anchor_prim.AddTranslateOp()
                rotate_op = anchor_prim.AddRotateXYZOp()
                translate_op.Set((45, -25, 200))
                rotate_op.Set((-180, 90, -180))

                # Setup second anchor prim
                anchor_prim2 = UsdGeom.Xform.Define(stage, "/World/Anchor2")
                translate_op2 = anchor_prim2.AddTranslateOp()
                rotate_op2 = anchor_prim2.AddRotateXYZOp()
                translate_op2.Set((400, -55, -1200))
                rotate_op2.Set((180, 35, -180))

                # Enable first custom anchors.
                carb.settings.get_settings().set(anchor_mode_settings_path, "custom anchor")
                carb.settings.get_settings().set(anchor_name_settings_path, "/World/Anchor1")

            await self.wait_post_sync_async(10)
            await self.capture_and_compare_viewport_output_async(
                "custom_anchor_01_set_first_anchor", self.ACCEPTABLE_GOLDEN_THRESHOLD, __name__
            )

            with Usd.EditContext(stage, stage.GetSessionLayer()):
                # Move the first anchor xform.
                translate_op.Set((-750, -25, 300))
                rotate_op.Set((0, 0, 0))

            await self.wait_post_sync_async(10)
            await self.capture_and_compare_viewport_output_async(
                "custom_anchor_02_move_first_anchor", self.ACCEPTABLE_GOLDEN_THRESHOLD, __name__
            )

            # Switch to the second anchor.
            carb.settings.get_settings().set(anchor_name_settings_path, "/World/Anchor2")

            await self.wait_post_sync_async(10)
            await self.capture_and_compare_viewport_output_async(
                "custom_anchor_03_set_second_anchor", self.ACCEPTABLE_GOLDEN_THRESHOLD, __name__
            )

            # Ensure simulating keyboard/mouse will be additive to the custom anchor.
            keyboard_translation = (-250, 100, -1000)
            XRCore.get_singleton().schedule_move_space_origin_relative_to_camera(*keyboard_translation)

            await self.wait_post_sync_async(10)
            await self.capture_and_compare_viewport_output_async(
                "custom_anchor_04_move_keyboard_mouse", self.ACCEPTABLE_GOLDEN_THRESHOLD, __name__
            )

            with Usd.EditContext(stage, stage.GetSessionLayer()):
                # Now move the second anchor's transform and ensure the keyboard deltas are additive.
                translate_op2.Set((0, -55, -900))

            await self.wait_post_sync_async(10)
            await self.capture_and_compare_viewport_output_async(
                "custom_anchor_05_move_second_anchor", self.ACCEPTABLE_GOLDEN_THRESHOLD, __name__
            )

            # Set to empty anchor.
            carb.settings.get_settings().set(anchor_name_settings_path, "")

            keyboard_translation = (0, 100, 0)
            XRCore.get_singleton().schedule_move_space_origin_relative_to_camera(*keyboard_translation)

            await self.wait_post_sync_async(10)
            await self.capture_and_compare_viewport_output_async(
                "custom_anchor_06_set_empty_anchor", self.ACCEPTABLE_GOLDEN_THRESHOLD, __name__
            )

            # Disable anchors.
            carb.settings.get_settings().set(anchor_mode_settings_path, "")

            await self.wait_post_sync_async(10)
            await self.capture_and_compare_viewport_output_async(
                "custom_anchor_07_disable_custom_anchor_mode", self.ACCEPTABLE_GOLDEN_THRESHOLD, __name__
            )

        # Wait a bit
        await self.wait_post_sync_async(90)
