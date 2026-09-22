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

from unittest.mock import Mock, patch
from omni.usd import UsdContext
from carb.settings import ISettings
from .test_base import TestFileBase
from ..file_window import FileUtils

# run tests last as it doesn't cleanup modela dialogs
class zzTestPromptIfUnsavedStage(TestFileBase):
    async def setUp(self):
        await super().setUp()
        self._show_unsaved_layers_dialog = False
        self._ignore_unsaved_stage = False

    # After running each test
    async def tearDown(self):
        await super().tearDown()

    def _mock_get_carb_setting(self, setting: str):
        from ..file_window import SHOW_UNSAVED_LAYERS_DIALOG, IGNORE_UNSAVED_STAGE
        if setting == SHOW_UNSAVED_LAYERS_DIALOG:
            return self._show_unsaved_layers_dialog
        elif setting == IGNORE_UNSAVED_STAGE:
            return self._ignore_unsaved_stage
        return False

    async def test_save_unsaved_stage(self):
        """Testing click save when prompted to save unsaved stage"""
        self._ignore_unsaved_stage = False
        self._show_unsaved_layers_dialog = True

        mock_callback = Mock()
        with patch.object(ISettings, "get", side_effect=self._mock_get_carb_setting),\
            patch.object(UsdContext, "has_pending_edit", return_value=True),\
            patch.object(UsdContext, "is_new_stage", return_value=True),\
            patch.object(FileUtils, "save") as mock_file_save:
            # Show prompt and click Save
            omni.kit.window.file.prompt_if_unsaved_stage(mock_callback)
            await self.click_unsaved_stage_prompt(button=0)

        mock_file_save.assert_called_once_with(mock_callback, allow_skip_sublayers=True)

    async def test_dont_save_unsaved_stage(self):
        """Testing click don't save when prompted to save unsaved stage"""
        self._ignore_unsaved_stage = False
        self._show_unsaved_layers_dialog = True

        mock_callback = Mock()
        with patch.object(ISettings, "get", side_effect=self._mock_get_carb_setting),\
            patch.object(UsdContext, "has_pending_edit", return_value=True),\
            patch.object(UsdContext, "is_new_stage", return_value=True),\
            patch.object(FileUtils, "save") as mock_file_save:
            # Show prompt and click Don't Save
            omni.kit.window.file.prompt_if_unsaved_stage(mock_callback)
            await self.click_unsaved_stage_prompt(button=1)

        mock_file_save.assert_not_called()
        mock_callback.assert_called_once()

    async def test_cancel_unsaved_stage(self):
        """Testing click cancel when prompted to save unsaved stage"""
        self._ignore_unsaved_stage = False
        self._show_unsaved_layers_dialog = True

        mock_callback = Mock()
        with patch.object(ISettings, "get", side_effect=self._mock_get_carb_setting),\
            patch.object(UsdContext, "has_pending_edit", return_value=True),\
            patch.object(UsdContext, "is_new_stage", return_value=True),\
            patch.object(FileUtils, "save") as mock_file_save:
            # Show prompt and click Don't Save
            omni.kit.window.file.prompt_if_unsaved_stage(mock_callback)
            await self.click_unsaved_stage_prompt(button=2)

        mock_file_save.assert_not_called()
        mock_callback.assert_not_called()

    async def test_no_prompt(self):
        """Testing unsaved stage prompt not shown"""
        self._ignore_unsaved_stage = False
        self._show_unsaved_layers_dialog = False

        mock_callback = Mock()
        with patch.object(ISettings, "get", side_effect=self._mock_get_carb_setting),\
            patch.object(UsdContext, "has_pending_edit", return_value=True),\
            patch.object(UsdContext, "is_new_stage", return_value=False),\
            patch.object(FileUtils, "save") as mock_file_save:
            omni.kit.window.file.prompt_if_unsaved_stage(mock_callback)

        mock_file_save.assert_called_once_with(mock_callback, allow_skip_sublayers=True)

    async def test_ignore_unsaved(self):
        """Testing ignore unsaved setting set to True"""
        self._ignore_unsaved_stage = True

        mock_callback = Mock()
        with patch.object(ISettings, "get", side_effect=self._mock_get_carb_setting),\
            patch.object(UsdContext, "has_pending_edit", return_value=True),\
            patch.object(FileUtils, "save") as mock_file_save:
            omni.kit.window.file.prompt_if_unsaved_stage(mock_callback)

        mock_file_save.assert_not_called()
        mock_callback.assert_called_once()

    async def test_no_pending_edit(self):
        """Testing stage with no pending edit"""
        self._ignore_unsaved_stage = False

        mock_callback = Mock()
        with patch.object(ISettings, "get", side_effect=self._mock_get_carb_setting),\
            patch.object(UsdContext, "has_pending_edit", return_value=False),\
            patch.object(FileUtils, "save") as mock_file_save:
            omni.kit.window.file.prompt_if_unsaved_stage(mock_callback)

        mock_file_save.assert_not_called()
        mock_callback.assert_called_once()
