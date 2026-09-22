## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
from omni.kit import ui_test
from ..prompt import Prompt

class TestPrompt(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def test_prompt(self):
        """Testing Prompt window"""
        prompt = Prompt(
            "TestPrompt",
            "TestLabel",
            [
                ("test_button", "pencil.svg", None),
            ],
            modal=False
        )
        prompt.hide()
        self.assertFalse(prompt.is_visible())
        prompt.show()
        self.assertTrue(prompt.is_visible())
        button = ui_test.find("TestPrompt//Frame/**/Button[*].text=='  test_button'")
        await button.click()
        self.assertFalse(prompt.is_visible())
        del prompt