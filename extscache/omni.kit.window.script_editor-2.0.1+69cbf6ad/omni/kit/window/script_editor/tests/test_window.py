## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import os
import tempfile

import omni.kit.app
import omni.kit.ui_test as ui_test
import omni.ui as ui
from omni.kit.test import AsyncTestCase
from omni.kit.test_suite.helpers import get_test_data_path
from omni.kit.window.file_exporter.test_helper import FileExporterTestHelper
from omni.kit.window.file_importer.test_helper import FileImporterTestHelper


class TestScriptEditorWindow(AsyncTestCase):
    # Before running each test
    async def setUp(self):
        ui.Workspace.show_window("Script Editor", True)
        self._filename = get_test_data_path(__name__, "test_script.py").replace("\\", "/")
        self._txt_file = open(self._filename, "r").read()

    # After running each test
    async def tearDown(self):
        ui.Workspace.show_window("Script Editor", False)

    async def test_script_editor_window_load(self):
        window = ui.Workspace.get_window("Script Editor")
        menu = window._menu_option

        menu.menu_open()
        async with FileImporterTestHelper() as file_helper:
            await file_helper.wait_for_popup()
            await file_helper.click_apply_async(filename_url=self._filename)
        await ui_test.human_delay(10)

        # verify file list loaded
        self.assertEqual(
            window._script_editor_widget.get_script_path().lower().replace("\\", "/"), self._filename.lower()
        )

    async def test_script_editor_window_saveas(self):
        window = ui.Workspace.get_window("Script Editor")
        menu = window._menu_option

        await self.test_script_editor_window_load()

        with tempfile.TemporaryDirectory() as tempdir:
            filename = os.path.join(tempdir, "test.py").replace("\\", "/")
            menu.menu_save_as()
            async with FileExporterTestHelper() as file_helper:
                await file_helper.wait_for_popup()
                await file_helper.click_apply_async(filename_url=filename)
            await ui_test.human_delay(10)

            # verify file was saved
            self.assertEqual(
                window._script_editor_widget.get_script_path().lower().replace("\\", "/"), filename.lower()
            )

            txt_file = open(filename, "r").read()
            self.assertEqual(txt_file.replace("\n", ""), self._txt_file.replace("\n", ""))
