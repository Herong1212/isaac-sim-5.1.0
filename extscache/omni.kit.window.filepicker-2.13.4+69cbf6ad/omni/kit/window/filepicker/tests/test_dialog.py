## Copyright (c) 2018-2023, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
from unittest.mock import Mock, patch
import asyncio
from typing import Callable

import carb.input
import omni.kit.test
from omni.kit import ui_test
from omni.kit.widget.filebrowser import TREEVIEW_PANE, FileBrowserItem, FileBrowserItemFactory

from ..dialog import FilePickerDialog
from ..api import FilePickerAPI
from ..test_helper import FilePickerTestHelper
from .test_utils import time_logger

import omni.client
from tempfile import TemporaryDirectory, NamedTemporaryFile
from pathlib import Path
import os
import random


@time_logger
class TestDialog(omni.kit.test.AsyncTestCase):
    """Testing the Filepicker Dialog."""
    async def setUp(self):
        self.previous_retry_values = omni.client.set_retries(0, 0, 0)
        self.test_listings = {
            "omniverse://": ["omniverse://ov-sandbox", "omniverse://ov-test"],
            "omniverse://ov-test": ["Lib", "NVIDIA", "Projects", "Users"],
            "omniverse://ov-test/NVIDIA": ["Assets", "Materials", "Samples"],
            "omniverse://ov-test/NVIDIA/Samples": ["Astronaut", "Flight", "Marbles", "Attic"],
            "omniverse://ov-test/NVIDIA/Samples/Astronaut": ["Astronaut.usd", "Materials", "Props"],
            "my-computer://": ["/", "Desktop", "Documents", "Downloads"],
            "/": ["bin", "etc", "home", "lib", "tmp"],
            "/home": ["jack", "jill"],
            "/home/jack": ["Desktop", "Documents", "Downloads"],
            "/home/jack/Documents": ["test.usd"],
        }

    async def tearDown(self):
        omni.client.set_retries(*self.previous_retry_values)

    @staticmethod
    async def _mock_stat_async_succeeds(url: str):
        return omni.client.Result.OK, None

    async def _mock_populate_async_impl(self, item: FileBrowserItem, callback_async: Callable, timeout: float = 10.0):
        if not item.populated:
            if item.path in self.test_listings:
                subdirs = self.test_listings[item.path]
            else:
                subdirs = []
            for subdir in subdirs:
                if item.path.endswith("://"):
                    path = subdir
                elif item.path == "/":
                    path = f"/{subdir}"
                else:
                    path = f"{item.path}/{subdir}"
                item.add_child(FileBrowserItemFactory.create_group_item(subdir, path))
            item.populated = True
        return None

    async def test_key_funcs(self):
        """Testing key functions"""

        mock_apply = Mock()
        mock_cancel = Mock()

        dialog = FilePickerDialog("test_apply", click_cancel_handler=mock_cancel, click_apply_handler=mock_apply,
                                treeview_identifier="FilePicker")
        await ui_test.human_delay(10)

        dialog.show()

        # OM-117841 Temporarily revert the changes when enter key press.
        # await ui_test.emulate_keyboard_press(carb.input.KeyboardInput.ENTER)
        # await ui_test.human_delay()
        # mock_apply.assert_called_once()

        await ui_test.emulate_keyboard_press(carb.input.KeyboardInput.ESCAPE)
        await ui_test.human_delay()
        mock_cancel.assert_called_once()

        # OM-117841 Temporarily revert the changes when enter key press.
        # test update apply handler updates key press func
        # mock_apply.reset_mock()
        # another_mock_apply = Mock()
        # dialog.set_click_apply_handler(another_mock_apply)
        # await ui_test.emulate_keyboard_press(carb.input.KeyboardInput.ENTER)
        # await ui_test.human_delay()
        # another_mock_apply.assert_called_once()
        # mock_apply.assert_not_called()
        dialog.hide()
        dialog.destroy()

    async def test_initial_navigation(self):
        """Testing that the initial navigation executed."""
        self.initial_navigation_finished = False

        async def _mock_navigation(*args, **kwargs):
            self.initial_navigation_finished = True

        with patch.object(FilePickerAPI, "navigate_to_async", side_effect=_mock_navigation), \
            patch("omni.client.stat_async", side_effect=self._mock_stat_async_succeeds):
            # make sure that when no interaction happens, initial navigation happens correctly
            dialog = FilePickerDialog(
                "test_cancel_initial_navigation", current_directory="omniverse://foo", current_filename="bar.usd",
                treeview_identifier="FilePicker")
            await ui_test.human_delay(10)
            dialog.show()
            await ui_test.human_delay(10)
            self.assertTrue(self.initial_navigation_finished)
            self.assertEqual(dialog.get_current_directory(), "omniverse://foo/")
            self.assertEqual(dialog.get_filename(), "bar.usd")
            dialog.hide()
            dialog.destroy()

        # OMPE-11887: make sure when current directory is "omniverse://", navigate_to_async is not invoked.
        self.initial_navigation_finished = False
        with patch.object(FilePickerAPI, "navigate_to_async", side_effect=_mock_navigation):
            dialog = FilePickerDialog(
                "test_cancel_initial_navigation", current_directory="omniverse://", current_filename="bar.usd",
                treeview_identifier="FilePicker")
            await ui_test.human_delay(10)
            dialog.show()
            await ui_test.human_delay(10)
            self.assertFalse(self.initial_navigation_finished)
            self.assertEqual(dialog.get_current_directory(), "omniverse://")
            self.assertEqual(dialog.get_filename(), "bar.usd")
            dialog.hide()
            dialog.destroy()

    async def test_selection_cancels_initial_navigation(self):
        """Testing that the initial navigation is cancelled by user selection."""
        self.initial_navigation_finished = False
        async def _mock_navigation(*args, **kwargs):
            await asyncio.sleep(2)
            self.initial_navigation_finished = True

        with patch.object(FilePickerAPI, "navigate_to_async", side_effect=_mock_navigation), \
                patch("omni.client.stat_async", side_effect=self._mock_stat_async_succeeds), \
                patch.object(FileBrowserItem, "populate_async", side_effect=self._mock_populate_async_impl, autospec=True):
            # check that user selection of an item cancels initial navigation
            dialog = FilePickerDialog(
                "test_cancel_by_selection", current_directory="omniverse://foo", current_filename="bar.usd",
                treeview_identifier="FilePicker")
            await ui_test.human_delay(10)
            dialog.add_connections({"ov-test": "omniverse://ov-test"})
            await ui_test.human_delay(10)
            dialog.show()
            await ui_test.human_delay()
            async with FilePickerTestHelper(dialog._widget) as filepicker_helper:
                item = await filepicker_helper.get_item_async("FilePicker", "ov-test", pane=TREEVIEW_PANE)
                self.assertTrue(bool(item))
                await item.click()
            # this should have cancelled the initial navigation
            await asyncio.sleep(2)
            self.assertFalse(self.initial_navigation_finished)
            dialog.hide()
            dialog.destroy()

    async def test_typing_in_pathfield_cancels_initial_navigation(self):
        """Testing that the initial navigation is cancelled by typing in pathfield."""
        self.initial_navigation_finished = False
        async def _mock_navigation(*args, **kwargs):
            await asyncio.sleep(2)
            self.initial_navigation_finished = True

        with patch.object(FilePickerAPI, "navigate_to_async", side_effect=_mock_navigation), \
                patch("omni.client.stat_async", side_effect=self._mock_stat_async_succeeds):
            # check that user typing in path field cancels initial navigation
            dialog = FilePickerDialog(
                "test_cancel_by_typing", current_directory="omniverse://foo", current_filename="bar.usd",
                treeview_identifier="FilePicker")
            await ui_test.human_delay(10)
            dialog.show()
            await ui_test.human_delay()
            # clicking in will trigger begin edit for path field, thus cancel the initial navigation
            path_field = ui_test.find_all("test_cancel_by_typing//Frame/**/ComboBox[*]")[0]
            await path_field.click()
            await asyncio.sleep(2)
            self.assertFalse(self.initial_navigation_finished)
            dialog.hide()
            dialog.destroy()

    async def test_file_bar(self):
        extension_options = [
                    ('*.usd', 'Can be Binary or Ascii'),
                    ('*.usda', 'Human-readable text format'),
                    ('*.usdc', 'Binary format'),
                    ('*.png', 'test'),
                    ('*.jpg', 'another test')
                ]
        postfix_options = [
            "anim",
            "cache",
            "curveanim",
            "geo",
            "material",
            "project",
            "seq",
            "skel",
            "skelanim"
        ]

        mock_handler = Mock()

        dialog = FilePickerDialog("test_file_bar",
                    treeview_identifier="FilePicker",
                    file_extension_options=extension_options,
                    file_postfix_options=postfix_options,
                    click_apply_handler=mock_handler,
                    click_cancel_handler=mock_handler
                )

        # basic checks, for an actual use case check file picker use cases such as importer and exporter
        dialog.set_filebar_label_name('Temp file name')
        self.assertEqual('Temp file name:', dialog.get_filebar_label_name())

        (choice, _) = random.choice(extension_options)
        dialog.set_file_extension(choice)
        self.assertEqual(choice, dialog.get_file_extension())

        choice_index = random.randint(0, len(extension_options) - 1)
        combo_box_button = ui_test.WidgetRef(dialog._widget._file_bar._file_extension_menu._button, "", dialog._window)
        await combo_box_button.click()
        combo_box_menu = None
        for _ in range(10):
            combo_box_menu = ui_test.find("ComboBoxMenu")
            if combo_box_menu is not None:
                break
            await omni.kit.app.get_app().next_update_async()
        self.assertIsNotNone(combo_box_menu)
        extension_button = combo_box_menu.find(f"**/ZStack[{choice_index}]/Button[0]")
        await extension_button.click()
        self.assertEqual(extension_options[choice_index][0], dialog.get_file_extension())

        choice = random.choice(postfix_options)
        dialog.set_file_postfix(choice)
        self.assertEqual(choice, dialog.get_file_postfix())

        with TemporaryDirectory() as tmpdir_fd:
            tmpdir = Path(tmpdir_fd).resolve()

            temp_fd = NamedTemporaryFile(dir=tmpdir, suffix=".mdl", delete=False)
            temp_fd.close()
            _, filename = os.path.split(temp_fd.name)
            async with FilePickerTestHelper(dialog._widget) as filepicker_helper:
                await filepicker_helper.toggle_grid_view_async(True)
                await filepicker_helper.select_items_async(str(tmpdir), [filename])
                await ui_test.human_delay()

                apply_button = ui_test.WidgetRef(dialog._widget._file_bar._apply_button, "", dialog._window)
                await apply_button.click()
                mock_handler.assert_called_with(filename, os.path.dirname(temp_fd.name).replace("\\", "/") + "/")

                cancel_button = ui_test.WidgetRef(dialog._widget._file_bar._cancel_button, "", dialog._window)
                await cancel_button.click()
                mock_handler.assert_called_with(filename, os.path.dirname(temp_fd.name).replace("\\", "/") + "/")

        dialog.destroy()

    async def test_double_click(self):
        mock_handler = Mock()

        dialog = FilePickerDialog("test_double_click",
                    treeview_identifier="FilePicker",
                    click_apply_handler=mock_handler,
                    click_cancel_handler=mock_handler
                )

        with TemporaryDirectory() as tmpdir_fd:
            tmpdir = Path(tmpdir_fd).resolve()

            temp_fd = NamedTemporaryFile(dir=tmpdir, suffix=".mdl", delete=False)
            temp_fd.close()
            _, filename = os.path.split(temp_fd.name)
            async with FilePickerTestHelper(dialog._widget) as filepicker_helper:
                await filepicker_helper.toggle_grid_view_async(True)
                items = await filepicker_helper.select_items_async(str(tmpdir), [filename])
                await ui_test.human_delay()

                rect = ui_test.find_first(f"test_double_click//Frame/**/Rectangle[*].identifier=='{items[0].name}'")
                await rect.double_click()
                mock_handler.assert_called_with(filename, os.path.dirname(temp_fd.name).replace("\\", "/") + "/")

        dialog.destroy()