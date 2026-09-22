# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.kit.app
import omni.kit.test
import omni.kit.xr.core

from ..._xrtests import *


class TestCPPTests(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def test_unit_xr_math(self):
        """
        Test XRMath classes
        """
        self.assertEqual(xrtests_test_xr_math(), True)

    async def test_unit_xr_version(self):
        """
        Test XRVersion
        """
        self.assertEqual(xrtests_test_xr_version(), True)

    async def test_unit_versioned_usage(self):
        xrtests_test_versioned_usage()

    async def test_unit_unversioned_usage(self):
        xrtests_test_unversioned_usage()

    async def test_unit_library_approaches(self):
        xrtests_test_library_approaches()
