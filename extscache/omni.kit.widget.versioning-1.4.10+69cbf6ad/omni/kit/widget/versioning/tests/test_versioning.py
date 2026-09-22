## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
import omni.kit.app
import omni.client

from datetime import datetime
from unittest.mock import patch, Mock
from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit.test_suite.helpers import get_test_data_path
from omni.kit.window.content_browser import get_content_window
import omni.ui as ui
import omni.kit.ui_test as ui_test

from omni.kit.widget.versioning import CheckpointWidget, CheckpointCombobox, LAYOUT_TABLE_VIEW, LAYOUT_SLIM_VIEW
from ..checkpoint_helper import CheckpointHelper
from ..checkpoints_model import CheckpointModel


class MockServer:
    def __init__(self, cache_enabled=False, checkpoints_enabled=False, omniojects_enabled=False, username="", version=""):
        self.cache_enabled = cache_enabled
        self.checkpoints_enabled = checkpoints_enabled
        self.omniojects_enabled = omniojects_enabled
        self.username = username
        self.version = version


class MockFileEntry:
    def __init__(self, relative_path="", access="", flags="", size=0, modified_time="", created_time="", modified_by="", created_by="", version="", comment="<Test Node>"):
        self.relative_path = relative_path
        self.access = access
        self.flags = flags
        self.size = size
        self.modified_time = modified_time
        self.created_time = created_time
        self.modified_by = modified_by
        self.created_by = created_by
        self.version = version
        self.comment = comment


class _TestBase(AsyncTestCase):
    # Before running each test
    async def setUp(self):
        self._mock_server = MockServer(
            cache_enabled=False,
            checkpoints_enabled=True,
            omniojects_enabled=True,
            username="versioning_test@nvidia.com",
            version="TestServer"
        )
        self._mock_file_entries = [
            MockFileEntry(
                access=1,
                created_by="git@nvidia.com",
                created_time=datetime.min.time(),
                flags=513,
                modified_by="versioning_test@nvidia.com",
                modified_time=datetime.min.time(),
                relative_path="&1",
                size=160,
                version=12023408,
                comment="<1>"
            ),
            MockFileEntry(
                access=1,
                created_by="git@nvidia.com",
                created_time=datetime.min.time(),
                flags=513,
                modified_by="versioning_test@nvidia.com",
                modified_time=datetime.min.time(),
                relative_path="&2",
                size=260,
                version=12023408,
                comment="<2>"
            )
        ]

    # After running each test
    async def tearDown(self):
        pass

    async def _mock_get_server_info_async(self, url: str):
        return omni.client.Result.OK, self._mock_server

    async def _mock_list_checkpoints_async(self, query: str):
        return omni.client.Result.OK, self._mock_file_entries

    def _mock_checkpoint_query(self, query: str):
        return (None, 1)

    def _mock_copy_async(self, path, filepath, message=""):
        return omni.client.Result.OK
    
    def _mock_on_file_change(self, result):
        pass
    
    def _mock_resolve_subscribe(self, url, urls, cb1, cb2):
        cb2(omni.client.Result.OK, None, self._mock_file_entries[0], None)


class TestVersioningWindow(_TestBase):

    async def test_versioning_widget(self):
        with patch("omni.client.get_server_info_async", side_effect=self._mock_get_server_info_async),\
            patch("omni.client.list_checkpoints_async", side_effect=self._mock_list_checkpoints_async),\
            patch("omni.client.copy_async", side_effect=self._mock_copy_async) as _mock,\
            patch("omni.client.resolve_subscribe_with_callback",  side_effect=self._mock_resolve_subscribe),\
            patch.object(CheckpointModel, "_on_file_change_event", side_effect=self._mock_on_file_change) as _mock_file_change:

            under_test = get_content_window()
            # TODO: Filebrowser file selection not working for grid_view
            under_test.toggle_grid_view(False)
            test_path = get_test_data_path(__name__, "4Lights.usda")
            await under_test.select_items_async(test_path)
            await ui_test.wait_n_updates(2)

            # Confirm that checkpoint widget displays the expected checkpoint entry
            cp_widget = under_test.get_checkpoint_widget()
            cp_model = cp_widget._model
            cp_items = cp_model.get_item_children(None)

            self.assertTrue(len(cp_items))
            # Last item is the latest
            self.assertEqual(cp_items[-1].entry, self._mock_file_entries[0])

            # test restore
            cp_model.restore_checkpoint("omniverse://dummy.usd", "omniverse://dummy.usd?&2")
            await ui_test.wait_n_updates(5)
            _mock.assert_called_once_with("omniverse://dummy.usd?&2", "omniverse://dummy.usd",
                message="Restored checkpoint #2")

            # OMFP-3807: restore should trigger file change,check here
            _mock_file_change.assert_called()

    async def test_versioning_widget_table_view(self):
        mock_double_click = Mock()
        with patch("omni.client.get_server_info_async", side_effect=self._mock_get_server_info_async),\
            patch("omni.client.list_checkpoints_async", side_effect=self._mock_list_checkpoints_async):
            url = get_test_data_path(__name__, "4Lights.usda")
            window_flags = ui.WINDOW_FLAGS_NO_SCROLLBAR
            window = ui.Window("TestTableView", width=800, height=500, flags=window_flags)
            with window.frame:
                with ui.VStack():
                    widget = CheckpointWidget(url, layout=LAYOUT_TABLE_VIEW)
                    widget.set_url(url)
                    widget.add_context_menu(
                        "Foo",
                        "pencil.svg",
                        Mock(),
                        None,
                    )
                    widget.add_context_menu(
                        "Bar",
                        "pencil.svg",
                        Mock(),
                        None,
                    )
                    widget.set_mouse_double_clicked_fn(lambda b, k, cp: mock_double_click(cp))
            window.focus()
            await ui_test.wait_n_updates(5)
            cp_items = widget._model.get_item_children(None)

            # test that table view displays our test file entry correctly
            self.assertFalse(widget.empty())
            item = cp_items[-1]
            # Last item is the latest
            self.assertEqual(item.entry, self._mock_file_entries[0])
            self.assertEqual(item.comment, "<1>")
            self.assertTrue(item.get_full_url().endswith(f"4Lights.usda?&1"))
            self.assertEqual(item.get_relative_path(), "&1")

            # test search filtering
            treeview_item = ui_test.find("TestTableView//Frame/**/Label[*].text=='1'")
            self.assertIsNotNone(treeview_item)
            widget.set_search("2")
            await ui_test.human_delay()
            treeview_item = ui_test.find("TestTableView//Frame/**/Label[*].text=='1'")
            self.assertIsNone(treeview_item)
            # restore keywords back
            widget.set_search("")

            # test double click
            treeview_item = ui_test.find("TestTableView//Frame/**/Label[*].text=='1'")
            self.assertIsNotNone(treeview_item)
            await treeview_item.double_click()
            mock_double_click.assert_called_once_with(item)

            # test context menu
            await treeview_item.right_click()
            await ui_test.human_delay()
            await ui_test.select_context_menu("Foo")

            # test delete context menu
            widget.delete_context_menu("Foo")
            await ui_test.human_delay()
            await treeview_item.right_click()
            menu = await ui_test.get_context_menu()
            self.assertEqual(menu['_'], ['Bar'])

    async def test_checkpoint_combo_box(self):
        with patch("omni.client.get_server_info_async", side_effect=self._mock_get_server_info_async),\
            patch("omni.client.list_checkpoints_async", side_effect=self._mock_list_checkpoints_async),\
            patch("omni.client.get_branch_and_checkpoint_from_query", side_effect=self._mock_checkpoint_query):
            url = "omniverse://dummy.usd"
            window_flags = ui.WINDOW_FLAGS_NO_SCROLLBAR
            window = ui.Window("TestComboBox", width=800, height=500, flags=window_flags)
            with window.frame:
                with ui.VStack():
                    combo_box = CheckpointCombobox(url, lambda sel: print(f"Selected: {sel.get_full_url()}"))
            window.focus()
            await ui_test.wait_n_updates(5)

            # test visible
            self.assertTrue(combo_box.visible)
            combo_box.visible = False
            self.assertFalse(combo_box.visible)
            combo_box.visible = True

            # test url
            self.assertEqual(url, combo_box.url)
            url = "omniverse://dummy.usd?1"
            combo_box.url = url
            self.assertEqual(url, combo_box.url)

            # test show checkpoints
            field = ui_test.find_all("TestComboBox//Frame/**/StringField[*]")[0]
            self.assertIsNotNone(field)
            await field.click()

            await ui_test.human_delay()
            self.assertTrue(combo_box._checkpoint_list_popup.visible)


class TestCheckpointHelper(_TestBase):

    async def test_extract_server_from_url(self):
        self.assertFalse(CheckpointHelper.extract_server_from_url(""))
        self.assertEqual(CheckpointHelper.extract_server_from_url("omniverse://dummy/foo.bar"), "omniverse://dummy")

    async def test_is_checkpoint_enabled(self):
        enabled = await CheckpointHelper.is_checkpoint_enabled_async("")
        self.assertFalse(enabled)

        with patch("omni.client.get_server_info_async", side_effect=self._mock_get_server_info_async) as _mock:
            enabled = await CheckpointHelper.is_checkpoint_enabled_async("omniverse://dummy/foo.bar")
            self.assertTrue(enabled)
            _mock.assert_called_once()
            _mock.reset_mock()

            # test that server result is cached
            self.assertTrue("omniverse://dummy" in CheckpointHelper.server_cache)
            enabled = await CheckpointHelper.is_checkpoint_enabled_async("omniverse://dummy/baz.abc")
            self.assertTrue(enabled)
            _mock.assert_not_called()

    async def test_is_checkpoint_enabled_with_callback(self):
        callback = Mock()
        with patch("omni.client.get_server_info_async", side_effect=self._mock_get_server_info_async):
            CheckpointHelper.is_checkpoint_enabled_with_callback("omniverse://dummy/foo.bar", callback)
            await ui_test.wait_n_updates(2)
            callback.assert_called_once_with("omniverse://dummy", True)
