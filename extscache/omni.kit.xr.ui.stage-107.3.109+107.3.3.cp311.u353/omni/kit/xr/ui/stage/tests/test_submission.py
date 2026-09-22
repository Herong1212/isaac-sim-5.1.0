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
from pxr import Gf


class XRPipelineEvents(XRTestVR):

    VR_PROFILE_SETTINGS: dict = {
        "render/resolutionMultiplier": 1.0  # overwrite default multiplier to avoid hitting DLSS enforcement
    }

    @test_utils.opened_usd_stage()
    async def test_unit_xr_submission(self):
        """Test if XR submission of frames is executed"""

        async with TestVRProfile(self):

            await self.load_stage_async(str(test_utils.get_usd_directory().joinpath("Scaling/centimeter_scale.usda")))

            # Wait a bit
            await self.wait_post_sync_async(10)

            settings = carb.settings.get_settings()

            begin_frame = settings.get("/xr/simulatedxr/runBeginFrame/framenumber")
            sync_devices = settings.get("/xr/simulatedxr/runSyncSystem/framenumber")
            scaling_override = settings.get("/xr/simulatedxr/runOverrideScaling/framenumber")
            update_device_tracking = settings.get("/xr/simulatedxr/runUpdateTracking/framenumber")
            setup_displays = settings.get("/xr/simulatedxr/runUpdateDisplays/framenumber")
            setup_mirrors = settings.get("/xr/simulatedxr/runUpdateViewportMirrors/framenumber")
            pre_composition = settings.get("/xr/simulatedxr/runPreCompositionStage/framenumber")
            post_composition = settings.get("/xr/simulatedxr/runPostCompositionStage/framenumber")
            post_queue_submit = settings.get("/xr/simulatedxr/runPostQueueSubmitStage/framenumber")

            # Set the camera, should force
            self.set_xr_camera(Gf.Vec3d(100, 370, 35), Gf.Vec3d(200, -70, 150))

            await self.wait_post_sync_async(2)

            next_begin_frame = settings.get("/xr/simulatedxr/runBeginFrame/framenumber")
            next_sync_devices = settings.get("/xr/simulatedxr/runSyncSystem/framenumber")
            next_scaling_override = settings.get("/xr/simulatedxr/runOverrideScaling/framenumber")
            next_update_device_tracking = settings.get("/xr/simulatedxr/runUpdateTracking/framenumber")
            next_setup_displays = settings.get("/xr/simulatedxr/runUpdateDisplays/framenumber")
            next_setup_mirrors = settings.get("/xr/simulatedxr/runUpdateViewportMirrors/framenumber")
            next_pre_composition = settings.get("/xr/simulatedxr/runPreCompositionStage/framenumber")
            next_post_composition = settings.get("/xr/simulatedxr/runPostCompositionStage/framenumber")
            next_post_queue_submit = settings.get("/xr/simulatedxr/runPostQueueSubmitStage/framenumber")

            self.assertTrue(next_begin_frame > begin_frame)
            self.assertTrue(next_sync_devices > sync_devices)
            self.assertTrue(next_scaling_override > scaling_override)
            self.assertTrue(next_update_device_tracking > update_device_tracking)
            self.assertTrue(next_setup_displays > setup_displays)
            self.assertTrue(next_setup_mirrors > setup_mirrors)
            self.assertTrue(next_pre_composition > pre_composition)
            self.assertTrue(next_post_composition > post_composition)
            self.assertTrue(next_post_queue_submit > post_queue_submit)

            await self.wait_post_sync_async(5)

        # Ensure we run through at least a full cycle
        await self.wait_post_sync_async(3)
        self.assertEqual(test_utils.get_current_xr_profile_name(), "")
