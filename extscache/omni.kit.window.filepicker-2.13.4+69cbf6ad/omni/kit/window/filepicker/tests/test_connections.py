## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
import omni.kit.app
import carb.settings

from unittest.mock import patch, Mock
from omni.kit import ui_test
from omni.kit.widget.filebrowser import TREEVIEW_PANE, LISTVIEW_PANE, FileBrowserModel, FileBrowserItem
from ..dialog import FilePickerDialog
from ..widget import FilePickerWidget
from ..api import FilePickerAPI
from ..view import FilePickerView
from ..model import FilePickerModel
from ..test_helper import FilePickerTestHelper
from ..collections.collection_data import CollectionData
from ..collections.collection_item import CollectionItem
from ..collections.s3_collection import AddS3ConnectionItem
from ..collections.s3_connector_dialog import S3ConnectorDialog
from .test_utils import time_logger
import omni.client


@time_logger
class TestAddDeleteRenameServer(omni.kit.test.AsyncTestCase):
    """Testing FilePickerView.*server* methods"""
    async def setUp(self):
        self.previous_retry_values = omni.client.set_retries(0, 0, 0)
        # OM-78933: Init_view mounts localhost, which emits a BOOKMARK_ADDED_GLOBAL_EVENT.  This corrupts the event stream
        # and subsequently adds unaccounted calls to mock_add_bookmark below.  The simple fix is to add a few frames
        # here in order to steer clear of the initialization step.
        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()

    async def tearDown(self):
        omni.client.set_retries(*self.previous_retry_values)

    async def test_file_system_collections(self):
        """Testing FilePickerView.file_system_collections"""
        view = FilePickerView("test-view", show_only_collections=["my-computer"])
        model = view.navigation_model
        collection_item = model.get_item_children(None)[0]
        children = model.get_item_children(collection_item)
        count = len(children)
        while not collection_item.populated:
            await ui_test.human_delay(10)
        children = model.get_item_children(collection_item)
        self.assertGreater(len(children), count)

    async def test_add_server(self):
        """Testing FilePickerView.add_server adds the server"""
        with patch("omni.client.add_bookmark") as mock_add_bookmark:
            test_name, test_path = "ov-added", "omniverse://ov-added"
            under_test = FilePickerView("test-view")

            self.assertFalse(under_test.has_connection_with_name(test_name, collection="omniverse"))
            under_test.add_server(test_name, test_path)
            self.assertTrue(under_test.has_connection_with_name(test_name, collection="omniverse"))

            await omni.kit.app.get_app().next_update_async()
            mock_add_bookmark.assert_called_with(test_name, test_path)

            # OMPE-27824: make sure destroy after add server not trigger error
            under_test.destroy()

    async def test_delete_server(self):
        """Testing FilePickerView.delete_server deletes the server"""
        with patch("omni.client.remove_bookmark") as mock_remove_bookmark,\
             patch('omni.client.sign_out') as mock_disconnect:
            test_name, test_path = "ov-test", "omniverse://ov-test"
            under_test = FilePickerView("test-view")

            self.assertFalse(under_test.has_connection_with_name(test_name, collection="omniverse"))
            item = under_test.add_server(test_name, test_path)
            self.assertTrue(under_test.has_connection_with_name(test_name, collection="omniverse"))
            # Confirm that after being deleted, test_path is no longer in the connections liset
            under_test.delete_server(item)
            self.assertFalse(under_test.has_connection_with_name(test_name, collection="omniverse"))

            await omni.kit.app.get_app().next_update_async()
            mock_remove_bookmark.assert_called_with(test_name)
            mock_disconnect.assert_called_with(test_path)

    async def test_rename_server(self):
        """Testing FilePickerView.rename_server renames the server"""
        with patch("omni.client.add_bookmark") as mock_add_bookmark,\
            patch("omni.client.remove_bookmark") as mock_remove_bookmark,\
            patch.object(FilePickerView, "delete_server") as mock_delete_server:
            test_name, test_path, test_rename = "ov-test", "omniverse://ov-test", "ov-renamed"
            under_test = FilePickerView("test-view")

            item = under_test.add_server(test_name, test_path)
            self.assertTrue(under_test.has_connection_with_name(test_name, collection="omniverse"))

            await omni.kit.app.get_app().next_update_async()
            under_test.rename_server(item, test_rename)
            self.assertFalse(under_test.has_connection_with_name(test_name, collection="omniverse"))
            self.assertTrue(under_test.has_connection_with_name(test_rename, collection="omniverse"))
            # OMFP-4028: make sure rename server not trigger delete server
            mock_delete_server.assert_not_called()
            # Confirm that previous name deleted, then new name added
            for _ in range(8):
                await omni.kit.app.get_app().next_update_async()
            mock_remove_bookmark.assert_called_with(test_name)
            mock_add_bookmark.assert_called_with(test_rename, test_path)

    async def test_log_out_server(self):
        """Testing FilePickerView.log_out_server logs out the server"""
        with patch("omni.client.sign_out") as mock_sign_out:
            test_name, test_path = "ov-test", "omniverse://ov-test"
            under_test = FilePickerView("test-view")

            self.assertFalse(under_test.has_connection_with_name(test_name, collection="omniverse"))
            under_test.add_server(test_name, test_path)
            self.assertTrue(under_test.has_connection_with_name(test_name, collection="omniverse"))

            # Confirm that sign out is correctly called
            model = under_test.get_connection_with_url(test_path)
            under_test.log_out_server(model)
            await omni.kit.app.get_app().next_update_async()
            mock_sign_out.assert_called_with(test_path)


class TestUpdateConnectionsFromApi(omni.kit.test.AsyncTestCase):
    """Testing FilePickerAPI.*connections* methods"""
    async def setUp(self):
        self.previous_retry_values = omni.client.set_retries(0, 0, 0)
        # OM-78933: Init_view mounts localhost, which emits a BOOKMARK_ADDED_GLOBAL_EVENT.  This corrupts the event stream
        # and subsequently adds unaccounted calls to mock_add_bookmark below.  The simple fix is to add a few frames
        # here in order to steer clear of the initialization step.
        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()

    async def tearDown(self):
        omni.client.set_retries(*self.previous_retry_values)

    async def test_add_connections(self):
        """Testing FilePickerAPI.add_connections writes new connection to persistent settings"""
        with patch("omni.client.add_bookmark") as mock_add_bookmark:
            test_name, test_path = "ov-test", "omniverse://ov-test"
            test_view = FilePickerView("test-view")
            under_test = FilePickerAPI(FilePickerModel(), test_view)

            self.assertFalse(test_view.has_connection_with_name(test_name, collection="omniverse"))
            under_test.add_connections({test_name: test_path})
            self.assertTrue(test_view.has_connection_with_name(test_name, collection="omniverse"))

            await omni.kit.app.get_app().next_update_async()
            mock_add_bookmark.assert_called_with(test_name, test_path)

    async def test_update_connections_when_settings_changed(self):
        """Testing FilePickerAPI.subscribe_client_bookmarks_changed updates connections in view when bookmarks changed"""
        test_view = FilePickerView("test-view")
        under_test = FilePickerAPI(FilePickerModel(), test_view)
        under_test.subscribe_client_bookmarks_changed()

        self._sub_count = 0
        def _on_bookmark_changed(bookmarks):
            self._sub_count += 1

        self._bookmark_sub = omni.client.list_bookmarks_with_callback(_on_bookmark_changed)
        # First bookmark change event by default if subscribed
        while self._sub_count != 1:
            await ui_test.human_delay(10)
        
        try:
            # Assert connection not initially in the view
            test_name, test_path = "ov-ax98zjbm", "omniverse://ov-ax98zjbm"
            self.assertFalse(test_view.has_connection_with_name(test_name, collection="omniverse"))

            # Confirm that when an external source adds a bookmark, the view updates appropriately
            omni.client.add_bookmark(test_name, test_path)
            while self._sub_count != 2:
                await ui_test.human_delay(10)
            await ui_test.human_delay(10)
            self.assertTrue(test_view.has_connection_with_name(test_name, collection="omniverse"))

            # Confirm that after deleting connection from settings, the view updates appropriately
            omni.client.remove_bookmark(test_name)
            while self._sub_count != 3:
                await ui_test.human_delay(10)
            await ui_test.human_delay(10)
            self.assertFalse(test_view.has_connection_with_name(test_name, collection="omniverse"))
        finally:
            self._bookmark_sub = None

    async def test_collection_data(self):
        """Testing FilePickerAPI.add_collection/remove_collection adds/removes a collection to/from the view"""
        test_view = FilePickerView("test-view")
        api = FilePickerAPI(FilePickerModel(), test_view)
        model = test_view.navigation_model
        collections = model.collections

        connection_model = FileBrowserModel("custom colleciton", "test://collection")
        custom_file = FileBrowserItem("custom file", None)
        def __populate():
            connection_model.root.add_child(custom_file)

        collection_data = CollectionData(
            identifier="test",
            title="Test",
            path_to_icon="",
            model=connection_model,
            populate_fn=__populate
        )
        self.assertFalse(collections.get("test"))
        collection_item = api.add_collection(collection_data)
        collections = model.collections
        self.assertTrue(collections.get("test") == collection_item)

        collection_items = model.get_item_children(None)
        self.assertTrue(collection_item in collection_items)
        connection_items = model.get_item_children(collection_item)
        self.assertEqual(len(connection_items), 1)
        self.assertEqual(connection_items[0], connection_model.root)
        items = model.get_item_children(connection_items[0])
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0], custom_file)
    
        api.remove_collection("test")
        collections = model.collections
        self.assertFalse(collections.get("test"))

    async def test_register_collection(self):
        """Testing FilePickerAPI.register_collection_item/deregister_collection_item adds/removes a collection to/from the view"""
        class TestCollection(CollectionItem):
            def __init__(self):
                super().__init__("test", "Test", None, access = omni.client.AccessFlags.READ, populated=False, order=5)

        test_view = FilePickerView("test-view")
        api = FilePickerAPI(FilePickerModel(), test_view)
        model = test_view.navigation_model
        collections = model.collections

        connection_model = FileBrowserModel("custom colleciton", "test://collection")
        custom_file = FileBrowserItem("custom file", None)
        def __populate():
            connection_model.root.add_child(custom_file)

        self.assertFalse(collections.get("test"))
        collection_item = TestCollection()
        success = api.register_collection_item(collection_item)
        self.assertTrue(success)    
        collections = model.collections
        self.assertTrue(collections.get("test") == collection_item)

        collection_items = model.get_item_children(None)
        self.assertTrue(collection_item in collection_items)
        connection_items = model.get_item_children(collection_item)
        self.assertEqual(len(connection_items), 0)
    
        success = api.deregister_collection_item(collection_item)
        self.assertTrue(success)
        collections = model.collections
        self.assertFalse(collections.get("test"))

    async def test_show_only_collections(self):
        """Testing FilePickerAPI.add_show_only_collection/remove_show_only_collection adds/removes a collection to/from the view"""
        test_view = FilePickerView("test-view", show_only_collections=["bookmarks", "omniverse"])
        api = FilePickerAPI(FilePickerModel(), test_view)
        model = test_view.navigation_model
        current_values = test_view.show_only_collections
        # Default is empty that all collections are shown
        self.assertTrue(len(current_values) == 2)
        collection_items = model.get_item_children(None)
        self.assertEqual(len(collection_items), 2)
        self.assertEqual(collection_items[0].identifier, "bookmarks")
        self.assertEqual(collection_items[1].identifier, "omniverse")

        # Already in the list, nothing changed
        api.add_show_only_collection("bookmarks")
        collection_items = model.get_item_children(None)
        self.assertEqual(len(collection_items), 2)

        api.add_show_only_collection("https")
        collection_items = model.get_item_children(None)
        self.assertEqual(len(collection_items), 3)
        self.assertEqual(collection_items[2].identifier, "https")

        api.remove_show_only_collection("bookmarks")
        collection_items = model.get_item_children(None)
        self.assertEqual(len(collection_items), 2)
        self.assertEqual(collection_items[0].identifier, "omniverse")
        self.assertEqual(collection_items[1].identifier, "https")

class TestAddNewConnectionUI(omni.kit.test.AsyncTestCase):
    """Testing UX fr adding new connections"""
    async def setUp(self):
        self.previous_retry_values = omni.client.set_retries(0, 0, 0)

    async def tearDown(self):
        omni.client.set_retries(*self.previous_retry_values)

    async def test_treeview_add_new_connection_clicked(self):
        """Testing that when 'Add New Connection ...' item in treeview is clicked, launches connection flow"""
        dialog = FilePickerDialog("test_treeview_add_new_connection_clicked", treeview_identifier="FilePicker")
        await ui_test.human_delay(10)

        async with FilePickerTestHelper(dialog._widget) as filepicker_helper:
            with patch.object(omni.kit.widget.nucleus_connector, "connect_with_dialog") as mock_connector:
                item = await filepicker_helper.get_item_async("FilePicker", "Add New Connection ...", pane=TREEVIEW_PANE)
                await item.click()
                await ui_test.human_delay(10)
                mock_connector.assert_called_once()

        dialog.destroy()

    async def test_treeview_add_new_s3_connection_clicked(self):
        """Testing that when 'Add New Connection ...' item in treeview is clicked, launches connection flow"""
        dialog = FilePickerDialog("test_treeview_add_new_s3_connection_clicked", treeview_identifier="FilePicker", show_only_collections=["https"])
        await ui_test.human_delay(10)
        test_view = dialog._widget._view
        test_name = "s3_test"
        if test_view.has_connection_with_name(test_name, collection="https"):
            items = [i for i in test_view.all_collection_items("https") if i.name == test_name]
            if items:
                test_view.delete_server(items[0])
                await ui_test.human_delay(10)
        self.assertFalse(test_view.has_connection_with_name(test_name, collection="https"))
        async with FilePickerTestHelper(dialog._widget) as filepicker_helper:
            with patch.object(omni.client, "stat") as mock_stat:
                with patch.object(omni.client, "add_bookmark") as mock_add_bookmark:
                    mock_stat.return_value = (omni.client.Result.OK, None)
                    item = await filepicker_helper.get_item_async("FilePicker", "Add New Connection ...", pane=TREEVIEW_PANE)
                    await item.click()
                    await ui_test.human_delay(10)
                    window_ref = ui_test.find("Add S3 connection")
                    url_field = window_ref.find("**/HStack[0]/StringField[0]")
                    url_field.widget.model.set_value(test_name)
                    await ui_test.human_delay(10)
                    ok_button = window_ref.find("**/Button[*].text=='Ok'")
                    await ok_button.click()
                    mock_stat.assert_called_once()
                    await ui_test.human_delay(10)
                    self.assertTrue(test_view.has_connection_with_name(test_name, collection="https"))

        dialog.destroy()

    async def test_add_s3_connection_dialog(self):
        dialog = S3ConnectorDialog()
        dialog.show()
        dialog.set_value("url", "https://s3_test")
        await ui_test.human_delay(10)
        dialog.destroy()

    async def test_gridview_add_new_connection_clicked(self):
        """Testing that when 'Add New Connection ...' item in gridview is clicked, launches connection flow"""
        dialog = FilePickerDialog("test_gridview_add_new_connection_clicked", treeview_identifier="FilePicker")
        await ui_test.human_delay(10)

        async with FilePickerTestHelper(dialog._widget) as filepicker_helper:
            with patch.object(omni.kit.widget.nucleus_connector, "connect_with_dialog") as mock_connector:
                item = await filepicker_helper.get_item_async("FilePicker", "Omniverse", pane=TREEVIEW_PANE)
                await item.click()
                await ui_test.human_delay(10)

                item = await filepicker_helper.get_item_async("FilePicker", "Add New Connection ...", pane=LISTVIEW_PANE)
                await item.click()
                await ui_test.human_delay(10)
                mock_connector.assert_called_once()

        dialog.destroy()

    async def test_not_has_default_localhost(self):
        """Testing that there is no default localhost server in filepicker dialog"""
        # TODO: some test machine has the localhost bookmark stored in omniverse.toml
        # and the omni client's remove_bookmark is not time stable, so it cause flaky failed
        # comment his until find a better test solution
        return
        omni.client.remove_bookmark("localhost")
        await ui_test.human_delay(100)

        dialog = FilePickerDialog("test_not_has_default_localhost", treeview_identifier="FilePicker")
        await ui_test.human_delay(10)

        test_view = dialog._widget._view
        self.assertFalse(test_view.has_connection_with_name("localhost", collection="omniverse"))
        dialog.destroy()

    async def test_default_connection_setting(self):
        """Testing that default connection setting is working as expect"""
        test_connections = {
            "ov-test": "omniverse://ov-test",
            "test": "omniverse://ov-test",
        }
        old_setting_value = carb.settings.get_settings().get("exts/omni.kit.window.filepicker/mounted_servers")

        self._sub_count = 0
        self._bookmarks = {}
        def _on_bookmark_changed(bookmarks):
            self._sub_count += 1
            self._bookmarks = bookmarks
    
        self._bookmark_sub = omni.client.list_bookmarks_with_callback(_on_bookmark_changed)
        # First bookmark change event by default if subscribed
        while self._sub_count != 1:
            await ui_test.human_delay(10)

        # Make sure test connections not in default bookmarks
        if "ov-test" in self._bookmarks.keys():
            count = self._sub_count
            omni.client.remove_bookmark("ov-test")
            while self._sub_count != count + 1:
                await ui_test.human_delay(10)

        if "test" in self._bookmarks.keys():
            omni.client.remove_bookmark("test")
            count = self._sub_count
            while self._sub_count != count + 1:
                await ui_test.human_delay(10)

        try:
            carb.settings.get_settings().set("exts/omni.kit.window.filepicker/mounted_servers", test_connections)
            count = self._sub_count
            widget = FilePickerWidget("test_default_connection_setting")

            # Here a server added which will trigger a bookmark change event
            while self._sub_count != count + 1:
                await ui_test.human_delay(10)
            await ui_test.human_delay(10)

            test_view = widget._view
            self.assertTrue(test_view.has_connection_with_name("ov-test", collection="omniverse"))
            # The second one has duplicate server url with first one, so it should not be added
            self.assertFalse(test_view.has_connection_with_name("test", collection="omniverse"))

            await ui_test.human_delay(10)
            
            # Confirm that after deleting connection from settings, the view updates appropriately
            count = self._sub_count
            omni.client.remove_bookmark("ov-test")
            # remove_bookmark will trigger a bookmark change event
            while self._sub_count != count + 1:
                await ui_test.human_delay(10)
            self.assertFalse(test_view.has_connection_with_name("test", collection="omniverse"))
            widget.destroy()
        finally:
            carb.settings.get_settings().set("exts/omni.kit.window.filepicker/mounted_servers", old_setting_value)
            self._bookmark_sub = None

    async def test_show_add_new_connection_setting(self):
        """Testing that show add new connection setting is working as expect"""
        old_setting_value = carb.settings.get_settings().get("exts/omni.kit.window.filepicker/show_add_new_connection")
        carb.settings.get_settings().set("exts/omni.kit.window.filepicker/show_add_new_connection", True)
        await ui_test.human_delay(30)
        widget = FilePickerWidget("test_show_add_new_connection_setting")
        await ui_test.human_delay(30)

        test_view = widget._view
        mock_handle = Mock()
        collections = test_view.navigation_model.collections.values()
        for coll in collections:
            if coll and coll.children:
                for name, conn in coll.children.items():
                    if test_view._is_placeholder(conn):
                        self.assertEqual(name, "Add New Connection ...")
                        mock_handle()
        mock_handle.assert_called_once()
        widget.destroy()
        mock_handle.reset_mock()
        await ui_test.human_delay(10)
        carb.settings.get_settings().set("exts/omni.kit.window.filepicker/show_add_new_connection", False)
        widget = FilePickerWidget("test_not_show_add_new_connection_setting")
        await ui_test.human_delay(30)
        test_view = widget._view
        mock_handle = Mock()
        collections = test_view.navigation_model.collections.values()
        for coll in collections:
            if coll and coll.children:
                for name, conn in coll.children.items():
                    if test_view._is_placeholder(conn):
                        mock_handle()
        mock_handle.assert_not_called()
        widget.destroy()
        carb.settings.get_settings().set("exts/omni.kit.window.filepicker/show_add_new_connection", old_setting_value)
        await ui_test.human_delay(30)
