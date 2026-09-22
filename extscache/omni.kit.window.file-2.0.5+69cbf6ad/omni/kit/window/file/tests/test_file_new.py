## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
import omni.usd
import omni.kit.window

from unittest.mock import patch
from .test_base import TestFileBase


class TestFileNew(TestFileBase):
    async def setUp(self):
        await super().setUp()

    # After running each test
    async def tearDown(self):
        await super().tearDown()

    async def test_file_new(self):
        """Testing file new"""
        omni.kit.window.file.new()
        await self.wait_for_update()
        # verify new layer has non-Null identifier
        self.assertTrue(omni.usd.get_context().get_stage().GetRootLayer().anonymous)
