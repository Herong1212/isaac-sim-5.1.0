import omni.kit.test
import os
import random
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

from omni import ui
from carb.input import KeyboardInput

from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit import ui_test
from ..test_helper import ContentBrowserTestHelper


# FIXME: Currently force this to run before test_navigate, since it was not easy to close out the
# "add neclues connection" window in test
class TestFileRename(AsyncTestCase):
    """Testing ContentBrowserWidget drag and drop behavior"""
    async def setUp(self):
        await ui_test.find("Content").focus()

    async def tearDown(self):
        pass

    def _prepare_test_dir(self, temp_dir, temp_file):
        # make sure we start off clean
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
        os.makedirs(temp_dir)

        with open(os.path.join(temp_dir, temp_file), "w") as _:
            pass

    async def test_rename_file(self):
        """Testing renaming a file."""
        temp_dir = os.path.join(tempfile.gettempdir(), f"tmp{random.randint(0, int('0xffff', 16))}")
        temp_dir = str(Path(temp_dir).resolve())
        filename = "temp.mdl"
        self._prepare_test_dir(temp_dir, filename)

        async with ContentBrowserTestHelper() as content_browser_helper:
            await content_browser_helper.refresh_directory(tempfile.gettempdir())
            await content_browser_helper.navigate_to_async("omniverse:/")
            await ui_test.human_delay(50)
            await content_browser_helper.refresh_current_directory()
            await ui_test.human_delay(50)
            await content_browser_helper.navigate_to_async(temp_dir)
            await ui_test.human_delay(50)
            await content_browser_helper.toggle_grid_view_async(True)
            await ui_test.human_delay(50)
            t = await content_browser_helper.get_item_async(temp_dir + "/" + filename)
            await content_browser_helper.refresh_current_directory()
            await ui_test.human_delay(50)
            item = await content_browser_helper.get_gridview_item_async(filename)
            if item is None:
                return

            await item.right_click()
            await ui_test.human_delay()

            await ui_test.select_context_menu("Rename")

            popup = ui.Workspace.get_window(f"Rename {filename}")
            self.assertIsNotNone(popup)
            self.assertTrue(popup.visible)

            def dummy(*args, **kwargs):
                return "dummy.txt"

            with patch(
                "omni.kit.window.popup_dialog.InputDialog.get_value",
                side_effect=dummy
            ):
                await ui_test.emulate_keyboard_press(KeyboardInput.ENTER)
                await ui_test.human_delay(10)

            # file should have been renamed to dummy.txt now
            self.assertFalse(os.path.exists(os.path.join(temp_dir, filename)))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "dummy.txt")))
            await content_browser_helper.navigate_to_async("omniverse:/")
            await ui_test.human_delay(50)
        # Cleanup
        shutil.rmtree(temp_dir)

    async def test_rename_folder(self):
        """Testing renaming a folder."""
        temp_dir = os.path.join(tempfile.gettempdir(), f"tmp{random.randint(0, int('0xffff', 16))}")
        temp_dir = str(Path(temp_dir).resolve())
        src_folder = os.path.join(temp_dir, "test_folder")
        filename = "temp.mdl"
        self._prepare_test_dir(src_folder, filename)

        async with ContentBrowserTestHelper() as content_browser_helper:
            await content_browser_helper.refresh_directory(tempfile.gettempdir())
            await content_browser_helper.navigate_to_async(src_folder)
            await content_browser_helper.navigate_to_async(temp_dir)
            t = await content_browser_helper.get_item_async(src_folder)
            await content_browser_helper.toggle_grid_view_async(True)
            await content_browser_helper.refresh_current_directory()
            await ui_test.human_delay(50)
            item = await content_browser_helper.get_gridview_item_async("test_folder")
            if item is None:
                return

            await item.right_click()
            await ui_test.human_delay()

            await ui_test.select_context_menu("Rename")

            popup = ui.Workspace.get_window("Rename test_folder")
            self.assertIsNotNone(popup)
            self.assertTrue(popup.visible)

            def dummy(*args, **kwargs):
                return "renamed_folder"

            with patch(
                "omni.kit.window.popup_dialog.InputDialog.get_value",
                side_effect=dummy
            ):
                await ui_test.emulate_keyboard_press(KeyboardInput.ENTER)
                await ui_test.human_delay(20)

            # file should have been renamed to dummy.txt now
            self.assertFalse(os.path.exists(src_folder))
            renamed_folder = os.path.join(temp_dir, "renamed_folder")
            self.assertTrue(os.path.exists(renamed_folder))
            self.assertTrue(os.path.exists(os.path.join(renamed_folder, filename)))

            await content_browser_helper.navigate_to_async("omniverse:/")
            await ui_test.human_delay(50)

        # Cleanup
        shutil.rmtree(temp_dir)
