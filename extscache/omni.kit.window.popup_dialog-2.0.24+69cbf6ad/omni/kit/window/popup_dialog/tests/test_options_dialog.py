## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
import unittest
import asyncio
import omni.kit.app

from pathlib import Path
from omni.ui.tests.test_base import OmniUiTest
from unittest.mock import Mock
from ..options_dialog import OptionsDialog, OptionsWidget

CURRENT_PATH = Path(__file__).parent.absolute()
TEST_DATA_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.joinpath("data/tests")


class TestOptionsDialog(OmniUiTest):
    """Testing FormDialog"""
    async def setUp(self):
        self._field_defs = [
            OptionsDialog.FieldDef("hard", "Hard place", False),
            OptionsDialog.FieldDef("harder", "Harder place", True),
            OptionsDialog.FieldDef("hardest", "Hardest place", False),
        ]
        self._golden_img_dir = TEST_DATA_PATH.absolute().joinpath("images")

    async def tearDown(self):
        pass

    async def test_ui_layout(self):
        """Testing that the UI layout looks consistent"""
        window = await self.create_test_window()
        with window.frame:
            OptionsWidget(
                message="Please make your choice:",
                field_defs=self._field_defs,
                radio_group=False,
            )
        await omni.kit.app.get_app().next_update_async()
        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="options_dialog.png")
        window.destroy()
        # wait one frame so that widget is destroyed
        await omni.kit.app.get_app().next_update_async()

    async def test_okay_handler(self):
        """Test clicking okay button triggers the callback"""
        mock_okay_handler = Mock()
        under_test = OptionsDialog(
            message="Please make your choice:",
            field_defs=self._field_defs,
            width=300,
            radio_group=False,
            ok_handler=mock_okay_handler,
        )
        under_test.show()
        await asyncio.sleep(1)
        under_test._on_okay()
        mock_okay_handler.assert_called_once()
        # TODO:
        # self.assertEqual(under_test.get_choice(), 'harder')
        under_test.destroy()
