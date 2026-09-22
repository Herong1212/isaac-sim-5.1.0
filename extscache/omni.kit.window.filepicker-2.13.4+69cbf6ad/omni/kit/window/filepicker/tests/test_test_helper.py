## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import os
from pathlib import Path
from tempfile import TemporaryDirectory, NamedTemporaryFile

import omni.kit.test
from omni.kit import ui_test
from omni.kit.widget.filebrowser import TREEVIEW_PANE, LISTVIEW_PANE

from ..dialog import FilePickerDialog
from ..test_helper import FilePickerTestHelper
from .test_utils import time_logger

import omni.client


@time_logger
class TestTestHelper(omni.kit.test.AsyncTestCase):
    """Testing the test helper functions"""
    async def setUp(self):
        self.previous_retry_values = omni.client.set_retries(0, 0, 0)

    async def tearDown(self):
        omni.client.set_retries(*self.previous_retry_values)

    async def test_get_item_from_tree_view(self):
        """Testing getting item from the tree view"""
        dialog = FilePickerDialog("test_get_item_from_treeview", treeview_identifier="FilePicker")
        await ui_test.human_delay(10)
        dialog.add_connections({"ov-test": "omniverse://ov-test"})
        await ui_test.human_delay(10)

        async with FilePickerTestHelper(dialog._widget) as filepicker_helper:
            item = await filepicker_helper.get_item_async("FilePicker", "ov-test", pane=TREEVIEW_PANE)
            self.assertTrue(bool(item))

        dialog.destroy()

    async def test_get_item_from_table_view(self):
        """Testing getting item from the list view table"""
        dialog = FilePickerDialog("test_get_item_from_table_view", treeview_identifier="FilePicker")
        await ui_test.human_delay(10)
        dialog.add_connections({"ov-test": "omniverse://ov-test"})
        await ui_test.human_delay(10)

        async with FilePickerTestHelper(dialog._widget) as filepicker_helper:
            await filepicker_helper.toggle_grid_view_async(False)
            item = await filepicker_helper.get_item_async("FilePicker", "Omniverse", pane=TREEVIEW_PANE)
            await item.click()
            await ui_test.human_delay(10)
            item = await filepicker_helper.get_item_async("FilePicker", "ov-test", pane=LISTVIEW_PANE)
            self.assertTrue(bool(item))

        dialog.destroy()

    async def test_get_item_from_grid_view(self):
        """Testing getting item from the list view grid"""
        dialog = FilePickerDialog("test_get_item_from_grid_view", treeview_identifier="FilePicker")
        await ui_test.human_delay(10)
        dialog.add_connections({"ov-test": "omniverse://ov-test"})
        await ui_test.human_delay(10)

        async with FilePickerTestHelper(dialog._widget) as filepicker_helper:
            await filepicker_helper.toggle_grid_view_async(True)
            item = await filepicker_helper.get_item_async("FilePicker", "Omniverse", pane=TREEVIEW_PANE)
            await item.click()
            await ui_test.human_delay(10)
            item = await filepicker_helper.get_item_async("FilePicker", "ov-test", pane=LISTVIEW_PANE)
            self.assertTrue(bool(item))

        dialog.destroy()

    async def test_select_single_item(self):
        dialog = FilePickerDialog("test_select_single_item", treeview_identifier="FilePicker")

        with TemporaryDirectory() as tmpdir_fd:
            tmpdir = Path(tmpdir_fd).resolve()
            temp_fd = NamedTemporaryFile(dir=tmpdir, suffix=".mdl", delete=False)
            temp_fd.close()
            _, filename = os.path.split(temp_fd.name)

            async with FilePickerTestHelper(dialog._widget) as filepicker_helper:
                await filepicker_helper.toggle_grid_view_async(True)
                selections = await filepicker_helper.select_items_async(str(tmpdir), [filename])
                await ui_test.human_delay()

            self.assertEqual(1, len(selections))
            self.assertEqual(selections[0].name, filename)

        dialog.destroy()

    async def test_select_multiple_items(self):
        dialog = FilePickerDialog("test_select_multiple_items", treeview_identifier="FilePicker")

        with TemporaryDirectory() as tmpdir_fd:
            tmpdir = Path(tmpdir_fd).resolve()
            temp_files = []
            temp_file_path_names = []

            for _ in range(2):
                temp_fd = NamedTemporaryFile(dir=tmpdir, suffix=".mdl", delete=False)
                temp_fd.close()
                temp_file_path_names.append(temp_fd.name.replace('\\', '/'))
                _, filename = os.path.split(temp_fd.name)
                temp_files.append(filename)
            async with FilePickerTestHelper(dialog._widget) as filepicker_helper:
                await filepicker_helper.toggle_grid_view_async(True)
                selections = await filepicker_helper.select_items_async(str(tmpdir), temp_files)
                await ui_test.human_delay()

                self.assertEqual(len(selections), len(temp_files))
                self.assertEqual(set([sel.name for sel in selections]), set(temp_files))
                self.assertEqual(set(dialog.get_current_selections()), set(temp_file_path_names))

                current_directory = filepicker_helper.filepicker.api.get_current_directory()
                await filepicker_helper.select_items_async(str(tmpdir), [temp_files[0]])
                current_directory_after_select = filepicker_helper.filepicker.api.get_current_directory()
                # OMREQ-923: Should not set the current directory for selection change in list pane.
                self.assertEqual(current_directory, current_directory_after_select)

        dialog.destroy()