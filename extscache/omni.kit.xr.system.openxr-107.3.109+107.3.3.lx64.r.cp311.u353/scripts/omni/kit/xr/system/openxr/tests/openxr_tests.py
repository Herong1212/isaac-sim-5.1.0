# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni.kit.test
import omni.kit.xr.core.test_utils as test_utils


class TestOpenXRSystemConfiguration(omni.kit.test.AsyncTestCase):
    async def test_unit_activate_openxr(self):
        # Test whether OpenXR can be activated
        await test_utils.run_system_test(self, "OpenXR", "activate_openxr")
