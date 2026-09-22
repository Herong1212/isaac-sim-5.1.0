import os
import omni.kit.test
from pathlib import Path
from omni.kit import ui_test
from ..dialog import FilePickerDialog
from ..view import FilePickerView
from tempfile import TemporaryDirectory, NamedTemporaryFile, gettempprefix
from ..test_helper import FilePickerTestHelper
from ..file_ops import move_items, obliterate_items, restore_items, about_connection, checkpoint_items
from omni.kit.widget.filebrowser import LISTVIEW_PANE, TREEVIEW_PANE
from omni.kit.widget.filebrowser.tree_view import FileBrowserTreeView
import omni.ui as ui
from unittest.mock import patch, Mock
import omni.client
from..versioning_helper import VersioningHelper
from .test_utils import time_logger


@time_logger
class TestFileOps(omni.kit.test.AsyncTestCase):
    """Testing omni.kit.window.filepicker.file_ops"""
    async def setUp(self):
        # Because tests are run in async, queries could have access the wrong window
        # using the same name
        self._dialog = FilePickerDialog(
            "test_file_ops",
            treeview_identifier="FilePicker"
        )
        await ui_test.human_delay(4)
        # OMPE-5058: it could save test time if we are not sorting the item
        self._dialog._widget.api.view.filebrowser.navigation_model.sort_by_field = ""
        self._tmpdir_fd = TemporaryDirectory()
        self._tmpdir = Path(self._tmpdir_fd.name).resolve()

        self._temp_fd = NamedTemporaryFile(dir=self._tmpdir, suffix=".mdl", delete=False)
        self._temp_fd.close()
        self._folder, self._filename = os.path.split(self._temp_fd.name)
        self._filepicker_helper = FilePickerTestHelper(self._dialog._widget)
        self._delete_refrsh_order = []
        self._refresh_count = 0

    async def tearDown(self):
        self._dialog.destroy()
        self._tmpdir_fd.cleanup()

    async def _select_item_and_menu(self, item_filename, menu_name):
        await self._filepicker_helper.select_items_async(str(self._tmpdir), [item_filename])
        await ui_test.human_delay(2)
        item = await self._filepicker_helper.get_item_async("FilePicker", item_filename, pane=LISTVIEW_PANE)
        await item.right_click(human_delay_speed=5)
        menu = ui_test.WidgetRef(ui.Menu.get_current(), "")
        menu_item = menu.find(f"uiMenuItem[*].text=='{menu_name}'")
        await ui_test.emulate_mouse_move_and_click(menu_item.center)

    async def _wait_for_window(self, title, updates=10):
        window = None
        for _ in range(updates):
            window = ui_test.find(title)
            if window is not None:
                break
            await omni.kit.app.get_app().next_update_async()
        self.assertIsNotNone(window)
        return window

    async def test_rename(self):
        # rename
        await self._select_item_and_menu(self._filename, "Rename")
        rename_dialog = await self._wait_for_window(f"Rename {self._filename}")
        field = rename_dialog.find("**/StringField[*]")
        self.assertEqual(field.widget.model.get_value_as_string(), self._filename)
        new_filename = gettempprefix() + ".mdl"
        field.widget.model.set_value(new_filename)
        ok_button = rename_dialog.find("**/Button[*].text=='Confirm'")
        await ok_button.click()
        self._filename = os.path.join(self._tmpdir, new_filename)
        self.assertTrue(os.path.exists(self._filename))

    async def _mock_delete_async(self, path):
        omni.client.delete(path)
        await ui_test.human_delay(1)
        self._refresh_count = 0
        self._delete_refrsh_order.append("delete")
        return omni.client.Result.OK

    def _mock_select_and_center(self, item):
        self._filepicker_helper.filepicker.api.view.filebrowser.select_and_center(item, TREEVIEW_PANE)
        if len(self._delete_refrsh_order) > 0:
            self._delete_refrsh_order.append("select_and_center")

    def _mock_refresh_ui(self, *args, **kwargs):
        if len(self._delete_refrsh_order) > 1:
            self._refresh_count += 1

    async def test_delete(self):
        self._refresh_count = 0
        with patch("omni.client.delete_async") as mock_delete_async,\
            patch.object(FilePickerView, "select_and_center") as mock_select_and_center,\
            patch.object(FileBrowserTreeView, "refresh_ui", side_effect=self._mock_refresh_ui):
            mock_delete_async.side_effect = self._mock_delete_async
            mock_select_and_center.side_effect = self._mock_select_and_center
            # delete
            await self._select_item_and_menu(self._filename, "Delete")
            delete_dialog = None

            for _ in range(10):
                for window in ui.Workspace.get_windows():
                    if window.title == "Confirm File Deletion" and\
                        ui_test.WindowRef(window, "").find("**/Label[*].text.find('delete') >= 0"):
                        delete_dialog = ui_test.WindowRef(window, "")
                        break
                if delete_dialog is not None:
                    break
                await omni.kit.app.get_app().next_update_async()

            self.assertIsNotNone(delete_dialog)
            yes_button = delete_dialog.find("**/Button[*].text=='Yes'")
            await yes_button.click()
            self.assertFalse(os.path.exists(self._filename))
            await ui_test.human_delay(10)
            if self._filepicker_helper.filepicker:
                # OM-65585: It should auto select the parent folder
                selected_items = self._filepicker_helper.filepicker.api.get_current_selections(TREEVIEW_PANE)
                self.assertEqual(len(selected_items), 1)
                self.assertEqual(selected_items[0], self._tmpdir.as_posix())
            # OMPE-28290: make sure the  is select_and_center called after delete
            self.assertEqual(self._delete_refrsh_order, ["delete", "select_and_center"])
            # OMPE-28290: make sure only refresh once after select_and_center
            self.assertEqual(self._refresh_count, 1)

    async def test_new_folder(self):
        with TemporaryDirectory(dir=self._tmpdir) as tmpdir_fd:
            tmpdir = Path(tmpdir_fd).resolve()
            await self._select_item_and_menu(os.path.basename(tmpdir), "New Folder")
            new_dialog = await self._wait_for_window("Create folder")
            self.assertIsNotNone(new_dialog)
            field = new_dialog.find("**/StringField[*]")
            new_folder_name = gettempprefix()
            field.widget.model.set_value(new_folder_name)
            ok_button = new_dialog.find("**/Button[*].text=='Ok'")
            await ok_button.click()
            self.assertTrue(os.path.exists(os.path.join(tmpdir, new_folder_name)))

    async def test_move_items(self):
        with TemporaryDirectory(dir=self._tmpdir) as tmpdir_fd:
            tmpdir = Path(tmpdir_fd).resolve()
            item = Mock()
            item.path = tmpdir
            item.parent = None
            item.is_folder = True
            move_items(item, [self._temp_fd.name])
            await ui_test.human_delay(10)
            self.assertTrue(os.path.exists(os.path.join(tmpdir, self._filename)))

    async def test_obliterate(self):
        with patch("omni.client.get_server_info_async") as mock_get_server_info_async,\
            patch(f"omni.client.obliterate_async") as mock_obliterate_async:
            mock_server_info = Mock()
            mock_server_info.checkpoints_enabled = True
            mock_get_server_info_async.return_value = (True, mock_server_info)

            item = Mock()
            item.path = self._temp_fd.name
            item.parent = None
            item.is_folder = False
            obliterate_items([item], self._dialog._widget._view)

            await ui_test.human_delay(10)
            delete_dialog = None

            for _ in range(10):
                for window in ui.Workspace.get_windows():
                    if window.title == "Confirm File Deletion" and\
                        ui_test.WindowRef(window, "").find("**/Label[*].text.find('obliterate') >= 0"):
                        delete_dialog = ui_test.WindowRef(window, "")
                        break
                if delete_dialog is not None:
                    break
                await omni.kit.app.get_app().next_update_async()

            self.assertIsNotNone(delete_dialog)
            yes_button = delete_dialog.find("**/Button[*].text=='Yes'")
            await yes_button.click()
            await ui_test.human_delay(10)
            mock_obliterate_async.assert_awaited_once_with(item.path.replace("\\", "/"), True)

    async def test_restore(self):
        with patch("omni.client.undelete_async") as mock_undelete_async:
            item = Mock()
            item.path = self._temp_fd.name
            item.parent = None
            item.is_folder = False
            item.is_deleted = True
            restore_items([item], self._dialog._widget._view)
            await ui_test.human_delay(10)
            mock_undelete_async.assert_awaited_once_with(item.path.replace("\\", "/"))

    async def test_checkpoint(self):
        with patch.object(VersioningHelper, "check_server_checkpoint_support_async") as mock_check_server,\
            patch(f"omni.client.create_checkpoint_async") as mock_create_checkpoint:
            item = Mock()
            item.path = self._temp_fd.name
            item.parent = None
            item.is_folder = False

            mock_check_server.return_value = True
            mock_create_checkpoint.return_value = (omni.client.Result.OK, None)

            checkpoint_items([item], self._dialog._widget._checkpoint_widget)
            checkpoint_dialog = await self._wait_for_window("Checkpoint Name")
            field = checkpoint_dialog.find("**/StringField[*].multiline==True")
            field.widget.model.set_value("new_checkpoint")
            ok_button = checkpoint_dialog.find("**/Button[*].text=='Ok'")
            await ok_button.click()
            await ui_test.human_delay(10)

            mock_check_server.assert_awaited_once()
            mock_create_checkpoint.assert_awaited_once_with(item.path, "new_checkpoint", True)

    async def test_new_usd_file(self):
        with TemporaryDirectory(dir=self._tmpdir) as tmpdir_fd:
            tmpdir = Path(tmpdir_fd).resolve()
            await self._select_item_and_menu(os.path.basename(tmpdir), "New USD File")
            new_dialog = await self._wait_for_window("New USD")
            field = new_dialog.find("**/StringField[*]")
            new_filename = gettempprefix()
            field.widget.model.set_value(new_filename)
            create_button = new_dialog.find("**/Button[*].text=='Create'")
            await create_button.click()
            self.assertTrue(os.path.exists(os.path.join(tmpdir, new_filename + '.usd')))

    async def test_about_connection(self):
        with patch("omni.client.get_server_info_async") as mock_get_server_info_async:
            mock_server_info = Mock()
            mock_server_info.version = "1.0"
            mock_server_info.auth_token = "xxxxxxxx"
            mock_server_info.checkpoints_enabled =True
            mock_server_info.omniojects_enabled = True

            mock_get_server_info_async.return_value = (True, mock_server_info)

            item = Mock()
            item.path = self._temp_fd.name
            item.parent = None
            item.is_folder = False

            about_connection(item)
            await ui_test.human_delay(10)
            about_dialog = await self._wait_for_window("About")
            close_button = about_dialog.find("**/Button[*].text=='Close'")
            await close_button.click()
            await ui_test.human_delay(10)
            self.assertFalse(about_dialog._window.visible)
