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
import asyncio
import omni.kit.ui_test as ui_test

import omni.appwindow
from functools import lru_cache
from unittest.mock import Mock, patch, ANY
from carb.settings import ISettings
from omni.kit.window.filepicker import FilePickerDialog
from omni.kit.test_suite.helpers import get_test_data_path
from .. import get_file_importer
from ..extension import FileImporterExtension
from ..test_helper import FileImporterTestHelper
from tempfile import TemporaryDirectory
import shutil
from carb.input import KeyboardInput



@lru_cache()
def _get_default_window():
    app_window = omni.appwindow.get_default_app_window()
    if app_window:
        return app_window.get_window()
    return None


class TestFileImporter(omni.kit.test.AsyncTestCase):
    """
    Testing omni.kit.window.file_importer extension.  NOTE that since the dialog is a singleton, we use an async
    lock to ensure that only one test runs at a time.  In practice, this is not a issue because only one extension
    is accessing the dialog at any given time.
    """
    __lock = asyncio.Lock()

    async def setUp(self):
        self._settings_path = "my_settings"
        self._test_settings = {
            "/exts/omni.kit.window.file_importer/appSettings": self._settings_path,
            f"{self._settings_path}/directory": "C:/temp/folder" if os.name == "nt" else "/home/temp/folder",
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
            under_test = get_file_importer()
            original_destroy = FilePickerDialog.destroy
            with patch.object(FilePickerDialog, "destroy", autospec=True) as mock_destroy_dialog,\
                    patch("carb.windowing.IWindowing.hide_window"):
                under_test.show_window(title="first")
                under_test.show_window(title="second")
                mock_destroy_dialog.assert_called()
                dialog = mock_destroy_dialog.call_args[0][0]
                self.assertEqual(str(dialog._window), "first")
                original_destroy(dialog)

    async def test_hide_window_destroys_it(self):
        """Testing that hiding the window destroys it"""
        async with self.__lock:
            under_test = get_file_importer()
            original_destroy = FilePickerDialog.destroy
            with patch.object(FilePickerDialog, "destroy", autospec=True) as mock_destroy_dialog:
                under_test.show_window(title="test")
                under_test._dialog.hide()
                # Dialog is destroyed after a couple frames
                await omni.kit.app.get_app().next_update_async()
                await omni.kit.app.get_app().next_update_async()
                mock_destroy_dialog.assert_called()
                dialog = mock_destroy_dialog.call_args[0][0]
                self.assertEqual(str(dialog._window), "test")
                original_destroy(dialog)

    async def test_hide_window_destroys_detached_window(self):
        """Testing that hiding the window destroys detached window."""
        async with self.__lock:
            under_test = get_file_importer()
            original_destroy = FilePickerDialog.destroy
            with patch.object(FilePickerDialog, "destroy", autospec=True) as mock_destroy_dialog:
                under_test.show_window(title="test_detached")
                await omni.kit.app.get_app().next_update_async()
                under_test.detach_from_main_window()
                main_window = _get_default_window()
                if main_window:
                    self.assertFalse(main_window is under_test._dialog._window.app_window.get_window())
                under_test.hide_window()
                # Dialog is destroyed after a couple frames
                await omni.kit.app.get_app().next_update_async()
                await omni.kit.app.get_app().next_update_async()
                mock_destroy_dialog.assert_called()
                dialog = mock_destroy_dialog.call_args[0][0]
                self.assertEqual(str(dialog._window), "test_detached")
                original_destroy(dialog)

    async def test_load_default_settings(self):
        """Testing that dialog applies saved settings"""
        async with self.__lock:
            under_test = get_file_importer()
            with patch('omni.kit.window.file_importer.extension.FilePickerDialog') as mock_dialog,\
                patch.object(ISettings, "get_as_string", side_effect=self._mock_settings_get_string_impl):
                under_test.show_window(title="test_dialog")

            # Retrieve keyword args for the constructor (first call), and confirm called with expected values
            constructor_kwargs = mock_dialog.call_args_list[0][1]
            self.assertEqual(constructor_kwargs['current_directory'], self._test_settings[f"{self._settings_path}/directory"])

    async def test_override_default_settings(self):
        """Testing that user values override default settings"""
        async with self.__lock:
            test_url = "Omniverse://ov-test/my-folder/my-file.usd"
            under_test = get_file_importer()
            with patch('omni.kit.window.file_importer.extension.FilePickerDialog') as mock_dialog,\
                patch.object(ISettings, "get_as_string", side_effect=self._mock_settings_get_string_impl),\
                    patch("carb.windowing.IWindowing.hide_window"):
                under_test.show_window(title="test_dialog", filename_url=test_url)

            # Retrieve keyword args for the constructor (first call), and confirm called with expected values
            constructor_kwargs = mock_dialog.call_args_list[0][1]
            dirname, filename = os.path.split(test_url)
            self.assertEqual(constructor_kwargs['current_directory'], dirname)
            self.assertEqual(constructor_kwargs['current_filename'], filename)

    async def test_save_settings_on_import(self):
        """Testing that settings are saved on import"""
        from ..extension import on_import

        my_settings = {
            'filename': "my-file.anim.usd",
            'directory': "Omniverse://ov-test/my-folder",
        }
        mock_dialog = Mock()
        with patch.object(ISettings, "get_as_string", side_effect=self._mock_settings_get_string_impl),\
            patch.object(ISettings, "set_string", side_effect=self._mock_settings_set_string_impl):

            on_import(None, mock_dialog, my_settings['filename'], my_settings['directory'])
            # Retrieve keyword args for the constructor (first call), and confirm called with expected values
            self.assertEqual(my_settings['directory'], self._test_settings[f"{self._settings_path}/directory"])

    async def test_multi_selections(self):
        """Tests for multi-selections support."""

        mock_handler = Mock()
        async with self.__lock:
            under_test = get_file_importer()
            test_path = get_test_data_path(__name__).replace("\\", '/')

            async with FileImporterTestHelper() as helper:
                with patch("carb.windowing.IWindowing.hide_window"):
                    under_test.show_window(
                        title="test", filename_url=test_path + "/", allow_multi_files_selection=True,
                        import_handler=mock_handler
                    )
                    await ui_test.human_delay(10)
                    item = await helper.get_item_async(None, "dummy.usd")
                    self.assertIsNotNone(item)

                    item2 = await helper.get_item_async(None, "cone.usda")
                    self.assertIsNotNone(item2)
                    # apply button should be disabled
                    self.assertFalse(under_test._dialog._widget.file_bar._apply_button.enabled)

                    # try selecting two files
                    selections = await under_test.select_items_async(test_path, filenames=["dummy.usd", "cone.usda"])
                    self.assertEqual(len(selections), 2)
                    # apply button should not be disabled
                    self.assertTrue(under_test._dialog._widget.file_bar._apply_button.enabled)

                    await ui_test.human_delay()
                    await helper.click_apply_async()
                    mock_handler.assert_called_once_with(
                        'dummy.usd', test_path + "/",
                        selections=[selections[0].path, selections[1].path]
                    )

    async def test_show_only_folders(self):
        """Testing show only folders option."""
        mock_handler = Mock()

        async with self.__lock:
            under_test = get_file_importer()
            test_path = get_test_data_path(__name__).replace("\\", '/')

            async with FileImporterTestHelper() as helper:
                with patch("carb.windowing.IWindowing.hide_window"):
                    # under normal circumstance, files will be shown and could be selected.
                    under_test.show_window(title="test", filename_url=test_path + "/")
                    await ui_test.human_delay(10)
                    item = await helper.get_item_async(None, "dummy.usd")
                    self.assertIsNotNone(item)
                    # apply button should be disabled
                    self.assertFalse(under_test._dialog._widget.file_bar._apply_button.enabled)
                    await helper.click_cancel_async()

                    # if shown with show_only_folders, files will not be shown
                    under_test.show_window(title="test", show_only_folders=True, import_handler=mock_handler)
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
                    mock_handler.assert_called_once_with('', test_path + "/", selections=[selected.path])

    async def test_cancel_handler(self):
        """Testing cancel handler."""
        mock_handler = Mock()

        async with self.__lock:
            under_test = get_file_importer()

            async with FileImporterTestHelper() as helper:
                under_test.show_window("test_cancel_handler")
                await helper.wait_for_popup()
                await omni.kit.app.get_app().next_update_async()
                await omni.kit.app.get_app().next_update_async()
                await helper.click_cancel_async(cancel_handler=mock_handler)
                await omni.kit.app.get_app().next_update_async()
                await omni.kit.app.get_app().next_update_async()
                mock_handler.assert_called_once()
                under_test.hide_window()

    async def test_validation_of_invalid_import_path(self):
        """Testing invalid import path is going through validation correctly."""
        mock_handler = Mock()

        async with self.__lock:
            under_test = get_file_importer()
            test_path = get_test_data_path(__name__).replace("\\", '/')

            async with FileImporterTestHelper() as helper:
                with patch("carb.windowing.IWindowing.hide_window"):
                    # under normal circumstance, files will be shown and could be selected.
                    under_test.show_window(title="test", filename_url=test_path + "/", should_validate=True,
                        import_handler=mock_handler)
                    await ui_test.human_delay(10)
                    item = await helper.get_item_async(None, "dummy.usd")
                    self.assertIsNotNone(item)
                    # try to hit accept with a non-existent path
                    await helper.click_apply_async(filename_url = test_path + "/non-existent")
                    await ui_test.human_delay()
                    # accept handler should not be called
                    mock_handler.assert_not_called()
                    await helper.click_cancel_async()

                    # test that when validation is turned off, this would go through
                    under_test.show_window(title="test", filename_url=test_path + "/", should_validate=False,
                        import_handler=mock_handler)
                    await ui_test.human_delay(10)
                    item = await helper.get_item_async(None, "dummy.usd")
                    self.assertIsNotNone(item)
                    # try to hit accept with a non-existent path
                    await helper.click_apply_async(filename_url = test_path + "/non-existent")
                    await ui_test.human_delay()
                    # accept handler should not be called
                    mock_handler.assert_called_once_with('non-existent', test_path + "/", selections=[])

    async def test_invalid_import_filename(self):
        """Testing invalid file name."""
        test_valid_filenames = ["test", "1test", "test1", "1_test/file", "c:\\anim.usdc", "2.usdc?&25"]
        test_invalid_filenames = [c + name + c for name in test_valid_filenames for c in '*\t\n\r\x0b\x0c']

        async with self.__lock:
            under_test = get_file_importer()
            test_path = get_test_data_path(__name__).replace("\\", '/')

            async with FileImporterTestHelper() as helper:
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

    async def test_apply_path(self):
        async with self.__lock:
            under_test = get_file_importer()
            test_path = get_test_data_path(__name__).replace("\\", '/')

            with TemporaryDirectory() as _tmpdir:
                tmpdir = _tmpdir.replace("\\", "/")
                mock_handler = Mock()
                under_test.show_window(title="test", filename_url=test_path + "/", import_handler=mock_handler)
                shutil.copyfile(test_path + "/cone.usda", tmpdir + "/cone.usda")

                path_field = under_test._dialog._widget._tool_bar._browser_bar._path_field
                path_field._path_model.begin_edit()
                path_field._path_model._field.model.set_value(tmpdir + "/cone.usda")
                # wait for tooltip update
                for _ in range(10):
                    await omni.kit.app.get_app().next_update_async()
                path_field._path_model._apply_path_handler(path_field._path_model._field.model.get_value_as_string())
                path_field._path_model.end_edit()
                # Apply handler is excecuted asynchronously now so wait for one frame before asserting
                await omni.kit.app.get_app().next_update_async()
                mock_handler.assert_called_once_with("cone.usda", tmpdir, selections=[])

                # OMPRW-733 & OMPRW-734: we should make sure navigate to the folder is work.
                under_test.show_window(title="test", filename_url=test_path + "/", import_handler=mock_handler)
                path_field = under_test._dialog._widget._tool_bar._browser_bar._path_field
                with patch.object(under_test._dialog, "navigate_to") as mock_navigate_to:
                    path_field._path_model._apply_path_handler(tmpdir)
                    # wait for update
                    for _ in range(10):
                        await omni.kit.app.get_app().next_update_async()
                    mock_navigate_to.assert_called_once_with(tmpdir)

class TestFileFilterHandler(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        ext_type = {
            'usd': "*.usd",
            'usda': "*.usda",
            'usdc': "*.usdc",
            'usdz': "*.usdz",
            'multiusd': "*.usd, *.usda, *.usdc, *.usdz",
            'all': "*.*",
            'bad_formatting_type': "*.usd, .usda, *.usdc,*.usdz, ,  ,"
        }
        self.test_filenames = [
            ("test.anim.usd", "anim", ext_type['all'], True),
            ("test.anim.usd", "anim", ext_type['usd'], True),
            ("test.anim.usdz", "anim", ext_type['usdz'], True),
            ("test.anim.usdc", "anim", ext_type['usdz'], False),
            ("test.anim.usda", None, ext_type['usda'], True),
            ("test.material.", None, ext_type['usda'], False),
            ("test.materials.usd", "material", ext_type['usd'], False),
            ("test.material.", None, ext_type['all'], True),
            ("test.material.", "anim", ext_type['all'], False),
            ("test.material.", "material", ext_type['all'], True),
        ]
        for t in ["multiusd", 'bad_formatting_type']:
            self.test_filenames.extend([
                ("test.anim.usd", "anim", ext_type[t], True),
                ("test.anim.usdz", "anim", ext_type[t], True),
                ("test.anim.usdc", "anim", ext_type[t], True),
                ("test.anim.usda", None, ext_type[t], True),
                ("test.anim.bbb", None, ext_type[t], False),
                ("test.material.", None, ext_type[t], False),
                ("test.anim.usdc", "cache", ext_type[t], False),
                ("test.anim.usdc", None, ext_type[t], True),
            ])

    async def tearDown(self):
        pass

    async def test_file_filter_handler(self):
        """Testing default file filter handler"""
        from ..extension import default_filter_handler

        for test_filename in self.test_filenames:
            filename, postfix, ext, expected = test_filename
            result = default_filter_handler(filename, postfix, ext)
            self.assertEqual(result, expected)
