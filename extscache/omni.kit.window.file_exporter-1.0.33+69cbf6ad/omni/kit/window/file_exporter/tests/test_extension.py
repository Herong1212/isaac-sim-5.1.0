## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import os
import omni.kit.test
import omni.kit.ui_test as ui_test
import asyncio

import omni.appwindow
from unittest.mock import Mock, patch, ANY
from carb.settings import ISettings
from omni.kit.window.filepicker import FilePickerDialog
from omni.kit.test_suite.helpers import get_test_data_path
from .. import get_file_exporter
from ..test_helper import FileExporterTestHelper
from ..extension import on_export, file_filter_handler, DEFAULT_FILE_POSTFIX_OPTIONS


class TestFileExporter(omni.kit.test.AsyncTestCase):
    """
    Testing omni.kit.window.file_exporter extension.  NOTE that since the dialog is a singleton, we use an async
    lock to ensure that only one test runs at a time.  In practice, this is not a issue because only one extension
    is accessing the dialog at any given time.
    """
    __lock = asyncio.Lock()

    async def setUp(self):
        self._settings_path = "my_settings"
        self._test_settings = {
            "/exts/omni.kit.window.file_exporter/appSettings": self._settings_path,
            f"{self._settings_path}/directory": "C:/temp/folder" if os.name == "nt" else "/home/temp/folder",
            f"{self._settings_path}/filename": "my-file",
        }

    async def tearDown(self):
        pass

    def _mock_settings_get_string_impl(self, name: str) -> str:
        return self._test_settings.get(name)

    def _mock_settings_set_string_impl(self, name: str, value: str):
        self._test_settings[name] = value

    async def test_show_window_destroys_previous(self):
        """Testing show_window destroys previously allocated dialog"""
        async with self.__lock:
            under_test = get_file_exporter()
            with patch.object(FilePickerDialog, "destroy", autospec=True) as mock_destroy_dialog,\
                    patch("carb.windowing.IWindowing.hide_window"):
                under_test.show_window(title="first")
                under_test.show_window(title="second")
                mock_destroy_dialog.assert_called()
                dialog = mock_destroy_dialog.call_args[0][0]
                self.assertEqual(str(dialog._window), "first")

    async def test_hide_window_destroys_it(self):
        """Testing that hiding the window destroys it"""
        async with self.__lock:
            under_test = get_file_exporter()
            with patch.object(FilePickerDialog, "destroy", autospec=True) as mock_destroy_dialog:
                under_test.show_window(title="test")
                under_test._dialog.hide()
                # Dialog is destroyed after a couple frames
                await omni.kit.app.get_app().next_update_async()
                await omni.kit.app.get_app().next_update_async()
                mock_destroy_dialog.assert_called()
                dialog = mock_destroy_dialog.call_args[0][0]
                self.assertEqual(str(dialog._window), "test")

    async def test_hide_window_destroys_detached_window(self):
        """Testing that hiding the window destroys detached window."""
        async with self.__lock:
            under_test = get_file_exporter()
            with patch.object(FilePickerDialog, "destroy", autospec=True) as mock_destroy_dialog:
                under_test.show_window(title="test_detached")
                await omni.kit.app.get_app().next_update_async()
                under_test.detach_from_main_window()
                main_window = omni.appwindow.get_default_app_window().get_window()
                self.assertFalse(main_window is under_test._dialog._window.app_window.get_window())
                under_test.hide_window()
                # Dialog is destroyed after a couple frames
                await omni.kit.app.get_app().next_update_async()
                await omni.kit.app.get_app().next_update_async()
                mock_destroy_dialog.assert_called()
                dialog = mock_destroy_dialog.call_args[0][0]
                self.assertEqual(str(dialog._window), "test_detached")

    async def test_load_default_settings(self):
        """Testing that dialog applies saved settings"""
        async with self.__lock:
            under_test = get_file_exporter()
            with patch('omni.kit.window.file_exporter.extension.FilePickerDialog') as mock_dialog,\
                patch.object(ISettings, "get_as_string", side_effect=self._mock_settings_get_string_impl):
                under_test.show_window(title="test_dialog")

            # Retrieve keyword args for the constructor (first call), and confirm called with expected values
            constructor_kwargs = mock_dialog.call_args_list[0][1]
            self.assertEqual(constructor_kwargs['current_directory'], self._test_settings[f"{self._settings_path}/directory"])
            self.assertEqual(constructor_kwargs['current_filename'], "")

    async def test_override_default_settings(self):
        """Testing that user values override default settings"""
        async with self.__lock:
            test_url = "Omniverse://ov-test/my-folder/my-file.usd"
            under_test = get_file_exporter()
            with patch('omni.kit.window.file_exporter.extension.FilePickerDialog') as mock_dialog,\
                patch.object(ISettings, "get_as_string", side_effect=self._mock_settings_get_string_impl),\
                    patch("carb.windowing.IWindowing.hide_window"):
                under_test.show_window(title="test_dialog", filename_url=test_url)

            # Retrieve keyword args for the constructor (first call), and confirm called with expected values
            constructor_kwargs = mock_dialog.call_args_list[0][1]
            dirname, filename = os.path.split(test_url)
            self.assertEqual(constructor_kwargs['current_directory'], dirname)
            self.assertEqual(constructor_kwargs['current_filename'], filename)

    async def test_save_settings_on_export(self):
        """Testing that settings are saved on export"""
        my_settings = {
            'filename': "my-file",
            'directory': "Omniverse://ov-test/my-folder",
        }
        mock_dialog = Mock()
        with patch.object(ISettings, "get_as_string", side_effect=self._mock_settings_get_string_impl),\
            patch.object(ISettings, "set_string", side_effect=self._mock_settings_set_string_impl):

            on_export(None, mock_dialog, my_settings['filename'], my_settings['directory'])
            # Retrieve keyword args for the constructor (first call), and confirm called with expected values
            self.assertEqual(my_settings['filename'], self._test_settings[f"{self._settings_path}/filename"])
            self.assertEqual(my_settings['directory'], self._test_settings[f"{self._settings_path}/directory"])

    async def test_show_only_folders(self):
        """Testing show only folders option."""
        mock_handler = Mock()

        async with self.__lock:
            under_test = get_file_exporter()
            test_path = get_test_data_path(__name__).replace("\\", '/')

            async with FileExporterTestHelper() as helper:
                with patch("carb.windowing.IWindowing.hide_window"):
                    # under normal circumstance, files will be shown and could be selected.
                    # under_test.show_window(title="test", filename_url=test_path)
                    under_test.show_window(title="test", filename_url=test_path + "/")
                    await ui_test.human_delay(10)
                    item = await helper.get_item_async(None, "dummy.usd")
                    self.assertIsNotNone(item)
                    # apply button should be disabled
                    self.assertFalse(under_test._dialog._widget.file_bar._apply_button.enabled)
                    await helper.click_cancel_async()

                    # if shown with show_only_folders, files will not be shown
                    under_test.show_window(title="test", show_only_folders=True, export_handler=mock_handler)
                    await ui_test.human_delay(10)
                    item = await helper.get_item_async(None, "dummy.usd")
                    self.assertIsNone(item)

                    # try selecting a folder
                    selections = await under_test.select_items_async(test_path, filenames=['folder'])
                    self.assertEqual(len(selections), 1)
                    selected = selections[0]
                    # apply button should not be disabled
                    self.assertTrue(under_test._dialog._widget.file_bar._apply_button.enabled)
                    await ui_test.human_delay()
                    await helper.click_apply_async()
                    mock_handler.assert_called_once_with('', os.path.dirname(selected.path) + "/", extension=".usd", selections=[selected.path])

    async def test_invalid_export_filenames(self):
        """Testing invalid filename."""
        test_valid_filenames = ["test", "1test", "test1", "1_test", "anim.usdc"]
        test_invalid_filenames = [name + c for name in test_valid_filenames for c in '/\\:*?"<>|\t\n\r\x0b\x0c']

        async with self.__lock:
            under_test = get_file_exporter()
            test_path = get_test_data_path(__name__).replace("\\", '/')

            async with FileExporterTestHelper() as helper:
                with patch("carb.windowing.IWindowing.hide_window"):
                    under_test.show_window(title="test", filename_url=test_path + "/")
                    await ui_test.human_delay(10)
                    for name in test_valid_filenames:
                        under_test._dialog._widget.file_bar.filename = name
                        self.assertTrue(under_test._dialog._widget.file_bar._apply_button.enabled)
                    for name in test_invalid_filenames:
                        under_test._dialog._widget.file_bar.filename = name
                        self.assertFalse(under_test._dialog._widget.file_bar._apply_button.enabled)
                    await helper.click_cancel_async()

    async def test_cancel_handler(self):
        """Testing cancel handler."""
        mock_handler = Mock()

        async with self.__lock:
            under_test = get_file_exporter()
            test_path = get_test_data_path(__name__).replace("\\", '/')

            async with FileExporterTestHelper() as helper:
                under_test.show_window(
                    "test_cancel_handler", filename_url=test_path + "/",
                )
                await helper.wait_for_popup()
                await ui_test.human_delay(10)
                await helper.click_cancel_async(cancel_handler=mock_handler)
                await ui_test.human_delay(10)
                mock_handler.assert_called_once()


class TestFileFilterHandler(omni.kit.test.AsyncTestCase):
    """Testing default_file_filter_handler correctly shows/hides files."""

    async def setUp(self):
        ext_type = {
            'usd': "*.usd",
            'usda': "*.usda",
            'usdc': "*.usdc",
            'usdz': "*.usdz",
        }
        self.test_filenames = [
            ("test.anim.usd", "anim", ext_type['usd'], True),
            ("test.anim.usdz", "anim", ext_type['usdz'], True),
            ("test.anim.usdc", "anim", ext_type['usdz'], False),
            ("test.anim.usda", None, ext_type['usda'], True),
            ("test.material.", None, ext_type['usda'], False),
            ("test.materials.usd", "material", ext_type['usd'], False),
        ]

    async def tearDown(self):
        pass

    async def test_file_filter_handler(self):
        """Testing file filter handler"""
        for test_filename in self.test_filenames:
            filename, postfix, ext, expected = test_filename
            result = file_filter_handler(filename, postfix, ext)
            self.assertEqual(result, expected)


class TestOnExport(omni.kit.test.AsyncTestCase):
    """Testing on_export function correctly parses filename parts from dialog."""
    async def setUp(self):
        self.test_sets = [
            ("test", "anim", "*.usdc", "test", ".anim.usdc"),
            ("test.usd", "anim", "*.usdc", "test", ".anim.usdc"),
            ("test.cache.usdc", "geo", "*.usdz", "test", ".geo.usdz"),
            ("test.cache.any", "geo", "*.usd", "test.cache.any", ".geo.usd"),
            ("test.geo.usd", None, "*.usda", "test", ".usda"),
            ("test.png", "anim", "*.jpg", "test", ".anim.jpg"),
        ]

    async def tearDown(self):
        pass

    async def test_on_export(self):
        """Testing file filter handler"""
        mock_callback = Mock()
        mock_dialog = Mock()
        mock_extension_options = [
            ('*.usd', 'Can be Binary or Ascii'),
            ('*.usda', 'Human-readable text format'),
            ('*.usdc', 'Binary format'),
            ('*.png', 'test'),
            ('*.jpg', 'another test')
        ]

        for test_set in self.test_sets:
            filename = test_set[0]
            mock_dialog.get_file_postfix.return_value = test_set[1]
            mock_dialog.get_file_extension.return_value = test_set[2]
            mock_dialog.get_file_postfix_options.return_value = DEFAULT_FILE_POSTFIX_OPTIONS
            mock_dialog.get_file_extension_options.return_value = mock_extension_options
            mock_dialog.get_current_selections.return_value = []
            on_export(mock_callback, mock_dialog, filename, "C:/temp/test/")

            expected_basename = test_set[3]
            expected_extension = test_set[4]
            mock_callback.assert_called_with(expected_basename, "C:/temp/test/", extension=expected_extension, selections=ANY)

    async def test_export_filename_validation(self):
        """Test export with and without validation."""
        mock_callback = Mock()
        mock_dialog = Mock()
        mock_dialog.get_file_postfix.return_value = None
        mock_dialog.get_file_extension.return_value = ".usd"
        mock_dialog.get_file_extension_options.return_value = [('*.usd', 'Can be Binary or Ascii')]

        on_export(mock_callback, mock_dialog, "", "", should_validate=True)
        mock_callback.assert_not_called()

        on_export(mock_callback, mock_dialog, "", "C:/temp/test/", should_validate=False)
        mock_callback.assert_called_once()
