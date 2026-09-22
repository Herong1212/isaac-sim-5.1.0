import omni.kit.test
import os
from pathlib import Path
from tempfile import TemporaryDirectory, NamedTemporaryFile, gettempdir
from unittest.mock import Mock
from unittest.mock import patch

import omni.ui as ui
import carb.settings
from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit import ui_test
from omni.kit.window.file_exporter import get_file_exporter
from ..test_helper import ContentBrowserTestHelper
from ..file_ops import download_items
from .. import get_content_window
from ..context_menu import ContextMenu


class TestDownload(AsyncTestCase):
    """Testing ContentBrowserWidget._download_items"""
    async def setUp(self):
        await ui_test.find("Content").focus()

    async def tearDown(self):
        # hide download window on test teardown
        window = ui.Workspace.get_window("Download Files")
        if window and window.visible:
            window.visible = False

    async def test_no_selection(self):
        """Testing when nothing is selected, don't open up file exporter."""
        # currently marking this as the first test to run since ui.Workspace.get_window result would not
        # be None if other tests had shown the window once
        download_items([])
        await ui_test.human_delay()
        window = ui.Workspace.get_window("Download Files")
        try:
            self.assertIsNone(window)
        except AssertionError:
            # in the case where the window is created, then the window should be invisible
            self.assertFalse(window.visible)

    async def test_single_selection(self):
        """Testing when downloading with a single item selected."""
        with TemporaryDirectory() as tmpdir_fd:
            # need to resolve to deal with the abbreviated user filename such as "LINE8~1"
            tmpdir = Path(tmpdir_fd).resolve()
            temp_fd = NamedTemporaryFile(dir=tmpdir, suffix=".mdl", delete=False)
            temp_fd.close()
            _, filename = os.path.split(temp_fd.name)
            async with ContentBrowserTestHelper() as content_browser_helper:
                await content_browser_helper.refresh_directory(gettempdir())
                await content_browser_helper.navigate_to_async(str(tmpdir))
                await ui_test.human_delay(100)
                items = await content_browser_helper.select_items_async(str(tmpdir), [filename])
                await ui_test.human_delay()

            with patch("omni.kit.notification_manager.post_notification") as mock_post_notification:
                self.assertEqual(len(items), 1)
                download_items(items)
                await ui_test.human_delay(10)

                file_exporter = get_file_exporter()
                self.assertIsNotNone(file_exporter)

                # the filename for file exporter should be pre-filled (same as the source filename)
                self.assertEqual(file_exporter._dialog.get_filename(), filename)
                # the filename field should enable input
                self.assertTrue(file_exporter._dialog._widget._enable_filename_input)
                file_exporter._dialog.set_current_directory(str(tmpdir))
                await ui_test.human_delay()
                window = ui.Workspace.get_window("Download Files")
                self.assertTrue(window.visible)

                file_exporter._dialog.set_filename("dummy")
                file_exporter.click_apply()
                await ui_test.human_delay(10)

                # should have created a downloaded file in the same directory, with the same extension
                self.assertTrue(tmpdir.joinpath("dummy.mdl").exists)

                mock_post_notification.assert_called_once()

    async def test_multi_selection(self):
        """Testing when downloading with multiple items selected."""
        with TemporaryDirectory() as tmpdir_fd:
            # need to resolve to deal with the abbreviated user filename such as "LINE8~1"
            tmpdir = Path(tmpdir_fd).resolve()
            temp_files = []

            for _ in range(2):
                temp_fd = NamedTemporaryFile(dir=tmpdir, suffix=".mdl", delete=False)
                temp_fd.close()
                _, filename = os.path.split(temp_fd.name)
                temp_files.append(filename)

            async with ContentBrowserTestHelper() as content_browser_helper:
                await content_browser_helper.refresh_directory(gettempdir())
                await content_browser_helper.navigate_to_async(str(tmpdir))
                await ui_test.human_delay(100)
                items = await content_browser_helper.select_items_async(str(tmpdir), temp_files)
                await ui_test.human_delay()

            with patch("omni.kit.notification_manager.post_notification") as mock_post_notification:
                self.assertEqual(len(items), len(temp_files))
                download_items(items)
                await ui_test.human_delay(10)

                file_exporter = get_file_exporter()
                self.assertIsNotNone(file_exporter)
                window = ui.Workspace.get_window("Download Files")
                self.assertTrue(window.visible)

                # the filename field should disable input
                self.assertFalse(file_exporter._dialog._widget._enable_filename_input)

                with TemporaryDirectory() as another_tmpdir_fd:
                    dst_tmpdir = Path(another_tmpdir_fd)
                    file_exporter._dialog.set_current_directory(str(dst_tmpdir))
                    await ui_test.human_delay()
                    # OM-99158: Check that the apply button is not disabled
                    self.assertTrue(file_exporter._dialog._widget.file_bar._apply_button.enabled)
                    file_exporter.click_apply()
                    await ui_test.human_delay(10)

                    # should have created downloaded files in the dst directory
                    downloaded_files = [file for file in os.listdir(dst_tmpdir)]
                    self.assertEqual(set(temp_files), set(downloaded_files))

                self.assertEqual(mock_post_notification.call_count, len(items))

    async def test_multi_results(self):
        """Testing when downloading with multiple results."""
        with TemporaryDirectory() as tmpdir_fd:
            # need to resolve to deal with the abbreviated user filename such as "LINE8~1"
            tmpdir = Path(tmpdir_fd).resolve()
            temp_files = []

            for _ in range(3):
                temp_fd = NamedTemporaryFile(dir=tmpdir, suffix=".mdl", delete=False)
                temp_fd.close()
                _, filename = os.path.split(temp_fd.name)
                temp_files.append(filename)

            async with ContentBrowserTestHelper() as content_browser_helper:
                await content_browser_helper.refresh_directory(gettempdir())
                await content_browser_helper.navigate_to_async(str(tmpdir))
                await ui_test.human_delay(100)
                items = await content_browser_helper.select_items_async(str(tmpdir), temp_files)
                await ui_test.human_delay()

            with patch.object(omni.kit.window.content_browser.file_ops, "copy_items_with_callback", side_effect=self._mock_copy_items_with_callback),\
                patch("omni.kit.notification_manager.post_notification") as mock_post_notification:
                self.assertEqual(len(items), len(temp_files))
                download_items(items)
                await ui_test.human_delay(10)

                file_exporter = get_file_exporter()
                self.assertIsNotNone(file_exporter)
                window = ui.Workspace.get_window("Download Files")
                self.assertTrue(window.visible)

                # the filename field should disable input
                self.assertFalse(file_exporter._dialog._widget._enable_filename_input)

                with TemporaryDirectory() as another_tmpdir_fd:
                    dst_tmpdir = Path(another_tmpdir_fd)
                    file_exporter._dialog.set_current_directory(str(dst_tmpdir))
                    await ui_test.human_delay()
                    # OM-99158: Check that the apply button is not disabled
                    self.assertTrue(file_exporter._dialog._widget.file_bar._apply_button.enabled)
                    file_exporter.click_apply()
                    await ui_test.human_delay(10)

                self.assertEqual(mock_post_notification.call_count, len(items))

    async def test_show_download_menuitem_setting(self):
        """Testing show download menuitem setting works as expect."""
        old_setting_value = carb.settings.get_settings().get("exts/omni.kit.window.content_browser/show_download_menuitem")

        item = Mock()
        item.path = "test"
        item.is_folder = False
        item.writeable = True

        carb.settings.get_settings().set("exts/omni.kit.window.content_browser/show_download_menuitem", True)
        menu_with_download = ContextMenu()

        menu_with_download.show(item, [item])
        await ui_test.human_delay(10)
        menu_dict = await ui_test.get_context_menu()
        has_download_menuitem = False
        for name in menu_dict["_"]:
            if name == "Download":
                has_download_menuitem = True
        self.assertTrue(has_download_menuitem)
        menu_with_download.destroy()

        carb.settings.get_settings().set("exts/omni.kit.window.content_browser/show_download_menuitem", False)
        menu_without_download = ContextMenu()
        await ui_test.human_delay(10)
        menu_without_download.show(item, [item])
        menu_dict = await ui_test.get_context_menu()
        has_download_menuitem = False
        for name in menu_dict["_"]:
            if name == "Download":
                has_download_menuitem = True
        self.assertFalse(has_download_menuitem)
        menu_without_download.destroy()

        carb.settings.get_settings().set("exts/omni.kit.window.content_browser/show_download_menuitem", old_setting_value)


    def _mock_copy_items_with_callback(self, src_paths, dst_paths, callback=None, copy_callback=None):
        # Fist one succeeded on copy
        # Second one failed on copy
        # Thrid has exception during copy
        copy_callback(src_paths[0], dst_paths[0], omni.client.Result.OK)
        copy_callback(src_paths[1], dst_paths[1], omni.client.Result.ERROR_NOT_SUPPORTED)
        expected_results = [dst_paths[0],dst_paths[1], Exception("Test Exception")]
        callback(expected_results)
