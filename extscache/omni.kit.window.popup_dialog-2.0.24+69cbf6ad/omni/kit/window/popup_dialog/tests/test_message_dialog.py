## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
import omni.kit.app

from pathlib import Path
from omni.ui.tests.test_base import OmniUiTest
from unittest.mock import Mock
from ..message_dialog import MessageWidget, MessageDialog

CURRENT_PATH = Path(__file__).parent.absolute()
TEST_DATA_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.joinpath("data/tests")


class TestMessageDialog(OmniUiTest):
    """Testing FormDialog"""
    async def setUp(self):
        self._message = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
        self._golden_img_dir = TEST_DATA_PATH.absolute().joinpath("images")

    async def tearDown(self):
        pass

    async def test_message_widget(self):
        """Testing the look of message widget"""
        window = await self.create_test_window()
        with window.frame:
            under_test = MessageWidget()
        under_test.set_message(self._message)
        await omni.kit.app.get_app().next_update_async()
        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="message_dialog.png")
        window.destroy()
        # wait one frame so that widget is destroyed
        await omni.kit.app.get_app().next_update_async()

    async def test_messgae_dialog(self):
        """Testing the look of message dialog"""
        mock_cancel_handler = Mock()
        under_test = MessageDialog(title="Message", cancel_handler=mock_cancel_handler,)
        under_test.set_message("Hello World")
        under_test.show()
        await omni.kit.app.get_app().next_update_async()
        under_test._on_cancel()
        mock_cancel_handler.assert_called_once()
        under_test.destroy()