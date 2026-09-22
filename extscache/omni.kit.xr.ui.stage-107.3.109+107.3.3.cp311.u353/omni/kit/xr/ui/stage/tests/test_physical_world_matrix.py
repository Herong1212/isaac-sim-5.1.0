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
from pxr import Gf


class TestPhysicalWorldMatrix(XRTestVR):

    async def test_unit_physical_world_matrix(self):
        """Test that opens test scene and changes the physical world matrix"""

        async with TestVRProfile(self):

            # Load scene
            await self.load_stage_async(str(test_utils.get_usd_directory().joinpath("Scaling/centimeter_scale.usda")))

            # Capture the Viewport
            await self.capture_and_compare_viewport_output_async("scene_xrenabled_xrpose_1", 0.001, __name__)

            # Wait a bit
            await self.wait_post_sync_async(50)

            # Set the camera, should force
            self.set_xr_camera(Gf.Vec3d(300, 70, 80), Gf.Vec3d(200, 70, 150))

            await self.wait_post_sync_async(2)

            # Capture the Viewport
            await self.capture_and_compare_viewport_output_async("scene_xrenabled_xrpose_2", 0.001, __name__)

            # Wait a bit
            await self.wait_post_sync_async(5)
