from tempfile import TemporaryDirectory, gettempdir
import shutil
import os
import stat
import omni.kit.test
from unittest.mock import patch, Mock

import omni.client
from omni import ui
from carb.input import KeyboardInput

from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit import ui_test
from omni.kit.test_suite.helpers import get_test_data_path
from omni.kit.widget.filebrowser import is_clipboard_cut, get_clipboard_items, clear_clipboard
from ..test_helper import ContentBrowserTestHelper
from ..file_ops import copy_items
from tempfile import TemporaryDirectory
import os

class TestCutPaste(AsyncTestCase):
    """Testing ContentBrowserWidget cut and paste behavior"""
    async def setUp(self):
        test_dir = get_test_data_path(__name__)
        # Use temp directory for cut test
        self._temp_dir = TemporaryDirectory()
        self._test_dir = f"{self._temp_dir.name}/tests"
        self._copy_tree(test_dir, self._test_dir)
        result, _ = omni.client.stat(self._test_dir)
        self.assertEqual(result, omni.client.Result.OK)
        await ui_test.find("Content").focus()

        # Since new test directory created under temp directory, need to refresh the temp directory in content browser
        async with ContentBrowserTestHelper() as content_browser_helper:
            await content_browser_helper.refresh_directory(gettempdir())

    async def tearDown(self):
        self._temp_dir.cleanup()

    async def test_paste_availability(self):
        """Testing paste context menu shows up correctly."""
        test_file = "4Lights.usda"
        test_folder = "folder.usda"

        async with ContentBrowserTestHelper() as content_browser_helper:
            result, _ = omni.client.stat(self._test_dir)
            self.assertEqual(result, omni.client.Result.OK)
            await content_browser_helper.navigate_to_async(self._test_dir)
            await content_browser_helper.toggle_grid_view_async(True)
            await ui_test.human_delay(100)
            item = await content_browser_helper.get_gridview_item_async(test_file)
            folder_item = await content_browser_helper.get_gridview_item_async(test_folder)
            if not item:
                return
            await item.right_click()
            await ui_test.human_delay()

            context_menu = await ui_test.get_context_menu()
            context_options = context_menu["_"]
            self.assertIn("Cut", context_options)
            self.assertNotIn("Paste", context_options)

            await ui_test.select_context_menu("Cut")

            # now paste should be available
            await ui_test.human_delay()
            await folder_item.right_click()
            await ui_test.human_delay()
            context_menu = await ui_test.get_context_menu()
            context_options = context_menu["_"]
            self.assertIn("Paste", context_options)

            # paste will not be available if more than one item is selected, but Cut should
            await content_browser_helper.select_items_async(self._test_dir, [test_file, test_folder])
            await item.right_click()
            await ui_test.human_delay()
            context_menu = await ui_test.get_context_menu()
            context_options = context_menu["_"]
            self.assertNotIn("Paste", context_options)
            self.assertIn("Cut", context_options)

        clear_clipboard()


    async def test_cut_and_paste(self):
        """Testing cut and paste."""
        test_file = "4Lights.usda"
        test_folder = "folder.usda"

        async with ContentBrowserTestHelper() as content_browser_helper:
            await content_browser_helper.navigate_to_async(self._test_dir)
            await content_browser_helper.toggle_grid_view_async(True)
            await ui_test.human_delay(100)
            item = await content_browser_helper.get_gridview_item_async(test_file)
            folder_item = await content_browser_helper.get_gridview_item_async(test_folder)
            if not item:
                return
            if not folder_item:
                return

            await folder_item.right_click()
            await ui_test.human_delay()
            await ui_test.select_context_menu("Cut")

            # cut clipboard should have one item in it
            self.assertTrue(is_clipboard_cut())
            self.assertEqual(1, len(get_clipboard_items()))
            self.assertEqual(get_clipboard_items()[0].path.replace("\\", "/").lower(),
                f"{self._test_dir}/{test_folder}".replace("\\", "/").lower())

            # cut clipboard should still have one item in it, but updated
            await item.right_click()
            await ui_test.human_delay()
            await ui_test.select_context_menu("Cut")
            self.assertTrue(is_clipboard_cut())
            self.assertEqual(1, len(get_clipboard_items()))
            cut_path = get_clipboard_items()[0].path
            self.assertEqual(cut_path.replace("\\", "/").lower(), f"{self._test_dir}/{test_file}".replace("\\", "/").lower())

            with patch.object(omni.client, "move_async", return_value=(omni.client.Result.OK, None)) as mock_move:
                await folder_item.right_click()
                await ui_test.human_delay()
                await ui_test.select_context_menu("Paste")

                await ui_test.human_delay(10)
                window = ui_test.find("MOVE")
                self.assertIsNotNone(window)
                await ui_test.emulate_keyboard_press(KeyboardInput.ENTER)
                await ui_test.human_delay()

            mock_move.assert_called_once()
            # clipboard should be cleared now
            self.assertEqual(get_clipboard_items(), [])
            self.assertFalse(is_clipboard_cut())

    async def test_copy_parent_to_child(self):
        with TemporaryDirectory() as tmpdir:
            with TemporaryDirectory(dir=tmpdir) as child_tmpdir:
                dst_item = Mock()
                dst_item.path = child_tmpdir
                copy_items(dst_item, [tmpdir])
                await ui_test.human_delay(10)
                self.assertEqual(len(os.listdir(child_tmpdir)), 0)

    def _copy_tree(self, src: str, dst: str):
        shutil.copytree(src, dst)
        os.chmod(dst, stat.S_IRWXU + stat.S_IRWXG + stat.S_IRWXO)
        for root, dirs, files in os.walk(dst):
            for dir in dirs:
                os.chmod(os.path.join(root, dir), stat.S_IRWXU + stat.S_IRWXG + stat.S_IRWXO)
            for file in files:
                os.chmod(os.path.join(root, file), stat.S_IRWXU + stat.S_IRWXG + stat.S_IRWXO)
