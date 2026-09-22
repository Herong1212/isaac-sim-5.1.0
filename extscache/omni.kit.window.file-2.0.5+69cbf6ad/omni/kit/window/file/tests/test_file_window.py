## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##


import omni.kit.window.file
from .test_base import TestFileBase
from unittest.mock import Mock
from omni.kit import ui_test
from omni.kit.window.file import ReadOnlyOptionsWindow
from omni.kit.window.file import register_open_stage_addon, register_open_stage_complete
from omni.kit.window.file_importer import get_file_importer

class TestFileWindow(TestFileBase):
    async def setUp(self):
        await super().setUp()

    # After running each test
    async def tearDown(self):
        await super().tearDown()

    async def test_read_only_options_window(self):
        """Testing read only options window"""
        self._readonly_window = ReadOnlyOptionsWindow(None, None, True)

        self._readonly_window.show()
        self.assertTrue(self._readonly_window.is_visible)

        self._readonly_window.destroy()

    async def test_stage_register(self):
        """Testing register_open_stage_addon and register_open_stage_complete subscription"""
        mock_callback1 = Mock()
        mock_callback2 = Mock()
        self._addon_subscription = register_open_stage_addon(mock_callback1)
        self._complete_subscription = register_open_stage_complete(mock_callback2)

        omni.kit.window.file.open_stage(f"{self._usd_path}/test_file.usda")
        await self.wait_for_update()

        mock_callback1.assert_called_once()
        mock_callback2.assert_called_once()

    async def test_add_reference(self):
        omni.kit.window.file.add_reference(is_payload=False)
        await ui_test.human_delay()

        file_importer = get_file_importer()
        self.assertTrue(file_importer.is_window_visible)
        file_importer.click_cancel()
