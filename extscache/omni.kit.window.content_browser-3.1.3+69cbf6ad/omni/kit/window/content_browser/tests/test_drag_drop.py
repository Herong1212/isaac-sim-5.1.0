import omni.kit.test
import os
import random
import shutil
import tempfile
from unittest.mock import patch
from pathlib import Path

import omni.appwindow
from omni import ui
from carb.input import KeyboardInput

from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit import ui_test
from ..test_helper import ContentBrowserTestHelper
from ..extension import get_instance


class TestDragDrop(AsyncTestCase):
    """Testing ContentBrowser drag and drop behavior"""

    async def setUp(self):
        await ui_test.find("Content").focus()

    async def tearDown(self):
        pass

    def _prepare_test_dir(self, temp_dir):
        # make sure we start off clean
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
        os.mkdir(temp_dir)

        src_paths = []
        # create a file under test dir, and a folder containg a file;
        with open(os.path.join(temp_dir, "test.mdl"), "w") as _:
            pass
        src_paths.append("test.mdl")

        test_folder_path = os.path.join(temp_dir, "src_folder")
        os.mkdir(test_folder_path)
        with open(os.path.join(test_folder_path, "test_infolder.usd"), "w") as _:
            pass
        src_paths.extend(["src_folder", "src_folder/test_infolder.usd"])

        # create the destination folder
        dst_folder_path = os.path.join(temp_dir, "dst_folder")
        os.mkdir(dst_folder_path)

        return src_paths, dst_folder_path

    def _get_child_paths(self, root_dir):
        paths = []

        def _iter_listdir(root):
            for p in os.listdir(root):
                full_path = os.path.join(root, p)
                if os.path.isdir(full_path):
                    yield full_path
                    for child in _iter_listdir(full_path):
                        yield child
                else:
                    yield full_path

        for p in _iter_listdir(root_dir):
            paths.append(p.replace(root_dir, "").replace("\\", "/").lstrip("/"))

        return paths

    async def test_drop_to_move(self):
        """Testing drop items would move items inside the destination."""
        temp_dir = os.path.join(tempfile.gettempdir(), f"tmp{random.randint(0, int('0xffff', 16))}")
        temp_dir = str(Path(temp_dir).resolve())
        src_paths, dst_path = self._prepare_test_dir(temp_dir)

        async with ContentBrowserTestHelper() as content_browser_helper:
            await content_browser_helper.refresh_directory(tempfile.gettempdir())
            await content_browser_helper.toggle_grid_view_async(False)
            await ui_test.human_delay(50)
            await content_browser_helper.refresh_current_directory()
            await ui_test.human_delay(100)
            await content_browser_helper.navigate_to_async(dst_path)
            await ui_test.human_delay(100)
            await content_browser_helper.navigate_to_async(temp_dir)
            await ui_test.human_delay(100)
            await content_browser_helper.refresh_current_directory()
            await ui_test.human_delay(100)
            target_item = await content_browser_helper.get_treeview_item_async("dst_folder")
            if not target_item:
                return

            await content_browser_helper.drag_and_drop_tree_view(
                temp_dir, src_paths[:-1], drag_target=target_item.position, focus_treeview_items=False)
            await ui_test.human_delay(20)

            window = ui_test.find("MOVE")
            self.assertIsNotNone(window)
            await ui_test.emulate_keyboard_press(KeyboardInput.ENTER)
            await ui_test.human_delay(20)

            # files should be moved inside dst folder
            self.assertTrue(len(os.listdir(temp_dir)) == 1)
            self.assertTrue(os.path.exists(dst_path))
            results = self._get_child_paths(os.path.join(temp_dir, dst_path))
            self.assertEqual(set(results), set(src_paths))

        # Cleanup
        shutil.rmtree(temp_dir)

    async def test_drop_to_copy(self):
        """Testing drop with CTRL pressed copies items."""
        temp_dir = os.path.join(tempfile.gettempdir(), f"tmp{random.randint(0, int('0xffff', 16))}")
        temp_dir = str(Path(temp_dir).resolve())
        src_paths, dst_path = self._prepare_test_dir(temp_dir)

        async with ContentBrowserTestHelper() as content_browser_helper:
            await content_browser_helper.refresh_directory(tempfile.gettempdir())
            await content_browser_helper.toggle_grid_view_async(False)
            await ui_test.human_delay(50)
            await content_browser_helper.refresh_current_directory()
            await ui_test.human_delay(100)
            await content_browser_helper.navigate_to_async(dst_path)
            await ui_test.human_delay(100)
            await content_browser_helper.navigate_to_async(temp_dir)
            await ui_test.human_delay(100)
            await content_browser_helper.refresh_current_directory()
            await ui_test.human_delay(100)
            target_item = await content_browser_helper.get_treeview_item_async("dst_folder")
            if not target_item:
                return

            async with ui_test.KeyDownScope(KeyboardInput.LEFT_CONTROL):
                await content_browser_helper.drag_and_drop_tree_view(
                    temp_dir, src_paths[:-1], drag_target=target_item.position, focus_treeview_items=False)
                await ui_test.human_delay(10)

            # files should be copied inside dst folder
            self.assertTrue(len(os.listdir(temp_dir)) == 3)
            # source paths should still exist
            for src_path in src_paths:
                self.assertTrue(os.path.exists(os.path.join(temp_dir, src_path)))

            # source paths should also be copied in dst folder
            self.assertTrue(os.path.exists(dst_path))
            results = self._get_child_paths(os.path.join(temp_dir, dst_path))
            self.assertEqual(set(results), set(src_paths))

        # Cleanup
        shutil.rmtree(temp_dir)


class TestExternalDragDrop(AsyncTestCase):
    """Testing ContentBrowser external drag and drop behavior"""

    async def setUp(self):
        await ui_test.find("Content").focus()
        # hide viewport to avoid drop fn triggered for viewport
        ui.Workspace.show_window("Viewport", False)

        window = ui_test.find("Content")
        await ui_test.emulate_mouse_move(window.center)

        content_browser = get_instance()
        content_browser.set_current_directory("/test/target")

    async def tearDown(self):
        pass

    async def test_external_drop_copy(self):
        """Testing external drop triggers copy."""
        with patch.object(omni.client, "copy_async", return_value=omni.client.Result.OK) as mock_client_copy:
            # simulate drag/drop
            omni.appwindow.get_default_app_window().get_window_drop_event_stream().push(0, 0, {'paths': ["dummy"]})
            await ui_test.human_delay(20)
            mock_client_copy.assert_called_once()

    async def test_external_drop_existing_item(self):
        """Testing external drop with existing item prompts user for deletion."""
        with patch.object(omni.client, "stat_async", return_value=(omni.client.Result.OK, None)) as mock_client_stat:
            # simulate drag/drop
            omni.appwindow.get_default_app_window().get_window_drop_event_stream().push(0, 0, {'paths': ["dummy"]})
            await ui_test.human_delay(20)
            mock_client_stat.assert_called_once()
            confirm_deletion = ui_test.find("Confirm File Overwrite")
            self.assertTrue(confirm_deletion.window.visible)
