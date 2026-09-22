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
from ..input_dialog import InputDialog, InputWidget

CURRENT_PATH = Path(__file__).parent.absolute()
TEST_DATA_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.joinpath("data/tests")


class TestInputDialog(OmniUiTest):
    """Testing FormDialog"""
    async def setUp(self):
        self._golden_img_dir = TEST_DATA_PATH.absolute().joinpath("images")

    async def tearDown(self):
        pass

    async def test_ui_layout(self):
        """Testing that the UI layout looks consistent"""
        window = await self.create_test_window()
        with window.frame:
            InputWidget(
                message="Please enter a username:",
                pre_label="LDAP Name:  ",
                post_label="@nvidia.com",
                default_value="user",
            )

        await omni.kit.app.get_app().next_update_async()
        # Add a threshold for the focused field is not stable.
        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="input_dialog.png", threshold=25)

    async def test_okay_handler(self):
        """Test clicking okay button triggers the callback"""
        mock_okay_handler = Mock()
        under_test =  InputDialog(
            message="Please enter a string value:",
            pre_label="LDAP Name:  ",
            post_label="@nvidia.com",
            ok_handler=mock_okay_handler,
        )
        under_test.show()
        under_test._on_okay()
        await omni.kit.app.get_app().next_update_async()
        mock_okay_handler.assert_called_once()

    async def test_get_field_value(self):
        """Test that get_value returns the value of the input field"""
        under_test =  InputDialog(
            message="Please enter a string value:",
            pre_label="LDAP Name:  ",
            post_label="@nvidia.com",
            default_value="user",
        )
        self.assertEqual("user", under_test.get_value())
