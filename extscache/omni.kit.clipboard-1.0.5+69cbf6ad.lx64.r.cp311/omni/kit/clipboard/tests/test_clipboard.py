## Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

import omni.kit.test
from omni.ui.tests.test_base import OmniUiTest
from omni.kit import ui_test

from .. import copy, paste

class ClipboardTest(OmniUiTest):

    # Before running each test
    # async def setUp(self):
    #     pass

    # After running each test
    # async def tearDown(self):
    #     pass

    async def test_clipboard(self):

        await self.create_test_window(width=400, height=40)
        human_delay_speed = 2
        await ui_test.wait_n_updates(human_delay_speed)

        str_to_copy = "Testing, testing, 1, 2, 3."
        copy(str_to_copy)
        pasted_str = paste()

        self.assertEqual(str_to_copy, pasted_str)
