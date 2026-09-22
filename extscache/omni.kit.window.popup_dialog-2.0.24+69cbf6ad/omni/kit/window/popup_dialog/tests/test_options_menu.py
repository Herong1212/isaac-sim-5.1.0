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
from ..options_menu import OptionsMenu, OptionsMenuWidget

CURRENT_PATH = Path(__file__).parent.absolute()
TEST_DATA_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.joinpath("data/tests")


class TestOptionsMenu(OmniUiTest):
    """Testing FormDialog"""
    async def setUp(self):
        self._field_defs = [
            OptionsMenu.FieldDef("audio", "Audio", None, False),
            OptionsMenu.FieldDef("materials", "Materials", None, True),
            OptionsMenu.FieldDef("scripts", "Scripts", None, False),
            OptionsMenu.FieldDef("textures", "Textures", None, False),
            OptionsMenu.FieldDef("usd", "USD", None, True),
        ]
        self._golden_img_dir = TEST_DATA_PATH.absolute().joinpath("images")

    async def tearDown(self):
        pass

    async def test_ui_layout(self):
        """Testing that the UI layout looks consistent"""
        window = await self.create_test_window()
        with window.frame:
            OptionsMenuWidget(
                title="Options",
                field_defs=self._field_defs,
            )
        await omni.kit.app.get_app().next_update_async()
        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="options_menu.png")
        window.destroy()
        # wait one frame so that widget is destroyed
        await omni.kit.app.get_app().next_update_async()

    async def test_okay_handler(self):
        """Test clicking okay button triggers the callback"""
        mock_value_changed_fn = Mock()
        under_test = OptionsMenu(
            title="Options",
            field_defs=self._field_defs,
            value_changed_fn=mock_value_changed_fn,
        )
        under_test.show()
        self.assertEqual(under_test.get_value('usd'), True)
        under_test.destroy()
