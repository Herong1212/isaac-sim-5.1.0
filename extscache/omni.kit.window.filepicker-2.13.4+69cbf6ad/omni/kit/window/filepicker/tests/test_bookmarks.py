## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
import asyncio
import sys

from unittest.mock import patch
from ..api import FilePickerAPI
from ..model import FilePickerModel
from ..view import FilePickerView
from ..file_ops import add_bookmark, edit_bookmark, delete_bookmark
from .test_utils import time_logger
from unittest.mock import Mock
import omni.kit.ui_test as ui_test

import omni.client


@time_logger
class TestAddDeleteRenameBookmark(omni.kit.test.AsyncTestCase):
    """Testing FilePickerView.*bookmark* methods"""
    async def setUp(self):
        self.previous_retry_values = omni.client.set_retries(0, 0, 0)
        # OM-78933: Init_view mounts localhost, which emits a BOOKMARK_ADDED_GLOBAL_EVENT.  This corrupts the event stream
        # and subsequently adds unaccounted calls to mock_add_bookmark below.  The simple fix is to add a few frames
        # here in order to steer clear of the initialization step.
        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()

    async def tearDown(self):
        omni.client.set_retries(*self.previous_retry_values)

    async def _wait_for_window(self, title, updates=10):
        window = None
        for _ in range(updates):
            window = ui_test.find(title)
            if window is not None:
                break
            await omni.kit.app.get_app().next_update_async()
        self.assertIsNotNone(window)
        return window

    async def test_add_bookmark(self):
        """Testing FilePickerView.add_bookmark adds the bookmark and stores as persistent setting"""
        with patch("omni.client.add_bookmark") as mock_add_bookmark:
            test_name, test_path = "added", "omniverse://ov-added"
            under_test = FilePickerView("test-view")

            self.assertFalse(under_test.has_connection_with_name(test_name, collection="bookmarks"))
            mock_add_bookmark.reset_mock()
            under_test.add_bookmark(test_name, test_path)
            self.assertTrue(under_test.has_connection_with_name(test_name, collection="bookmarks"))

            await omni.kit.app.get_app().next_update_async()
            mock_add_bookmark.assert_called_once_with(test_name, test_path + "/")

            # test add bookmark for local path
            test_name = "local bookmark"
            test_path = "/usr/bar.pref" if sys.platform == "linux" else "C:/foo/bar.pref"
            under_test = FilePickerView("test-view")

            self.assertFalse(under_test.has_connection_with_name(test_name, collection="bookmarks"))
            # Add bookmark while testing dialogs
            item = Mock()
            item.name = test_name
            item.path = test_path
            add_bookmark(item, under_test)
            add_dialog = await self._wait_for_window("Add Bookmark")
            self.assertIsNotNone(add_dialog)
            ok_button = add_dialog.find("**/Button[*].text=='Ok'")
            await ok_button.click()
            self.assertTrue(under_test.has_connection_with_name(test_name, collection="bookmarks"))

            await omni.kit.app.get_app().next_update_async()
            mock_add_bookmark.assert_called_with(test_name, "file://" + test_path + "/")

    async def test_delete_bookmark_with_callback(self):
        """Testing FilePickerView.delete_bookmark deletes the bookmark and updates the persistent setting"""
        with patch("omni.client.remove_bookmark") as mock_remove_bookmark:
            test_name, test_path = "test", "omniverse://ov-test"
            under_test = FilePickerView("test-view")

            self.assertFalse(under_test.has_connection_with_name(test_name, collection="bookmarks"))
            bookmark = under_test.add_bookmark(test_name, test_path)
            self.assertTrue(under_test.has_connection_with_name(test_name, collection="bookmarks"))
            # Confirm that after being deleted, test_name is no longer in the bookmarks liset
            delete_bookmark(bookmark, under_test)
            delete_dialog = await self._wait_for_window("Delete Bookmark")
            yes_button = delete_dialog.find("**/Button[*].text=='Yes'")
            await yes_button.click()
            self.assertFalse(under_test.has_connection_with_name(test_name, collection="bookmarks"))

            await omni.kit.app.get_app().next_update_async()
            mock_remove_bookmark.assert_called_with(test_name)

    async def test_rename_bookmark_with_callback(self):
        """Testing FilePickerView.rename_bookmark renames the bookmark and updates the persistent setting"""
        with patch("omni.client.add_bookmark") as mock_add_bookmark,\
            patch("omni.client.remove_bookmark") as mock_remove_bookmark:
            test_name, test_path, test_rename = "ov-test", "omniverse://ov-test", "ov-renamed"
            under_test = FilePickerView("test-view")

            bookmark = under_test.add_bookmark(test_name, test_path, publish_event=False)
            self.assertTrue(under_test.has_connection_with_name(test_name, collection="bookmarks"))

            # test rename name
            await omni.kit.app.get_app().next_update_async()
            edit_bookmark(bookmark, under_test)
            edit_dialog = await self._wait_for_window("Edit Bookmark")
            self.assertIsNotNone(edit_dialog)
            field = edit_dialog.find(f"**/StringField[*].model.get_value_as_string() == '{test_name}'")
            field.widget.model.set_value(test_rename)
            ok_button = edit_dialog.find("**/Button[*].text=='Ok'")
            await ok_button.click()
            self.assertFalse(under_test.has_connection_with_name(test_name, collection="bookmarks"))
            self.assertTrue(under_test.has_connection_with_name(test_rename, collection="bookmarks"))

            # Confirm that previous name deleted, then new name added; delete bookmark is executed with delay so wait here
            for _ in range(8):
                await omni.kit.app.get_app().next_update_async()
            mock_remove_bookmark.assert_called_with(test_name)
            mock_add_bookmark.assert_called_with(test_rename, test_path + "/")

            # test rename only url
            await omni.kit.app.get_app().next_update_async()
            bookmark_collection = under_test.navigation_model.get_collection("bookmarks")
            bookmark_items = under_test.navigation_model.get_item_children(bookmark_collection)
            self.assertEqual(len(bookmark_items), 1)
            self.assertEqual(bookmark_items[0].name, test_rename)
            bookmark = bookmark_items[0]
            under_test.rename_bookmark(bookmark, test_rename, "omniverse://dummy")
            self.assertTrue(under_test.has_connection_with_name(test_rename, collection="bookmarks"))
            await omni.kit.app.get_app().next_update_async()
            mock_add_bookmark.assert_called_with(test_rename, "omniverse://dummy")



class TestUpdateBookmarksFromApi(omni.kit.test.AsyncTestCase):
    """Testing FilePickerAPI.*bookmarks* methods"""
    async def setUp(self):
        self.previous_retry_values = omni.client.set_retries(0, 0, 0)
        # OM-78933: Init_view mounts localhost, which emits a BOOKMARK_ADDED_GLOBAL_EVENT.  This corrupts the event stream
        # and subsequently adds unaccounted calls to mock_add_bookmark below.  The simple fix is to add a few frames
        # here in order to steer clear of the initialization step.
        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()

    async def tearDown(self):
        omni.client.set_retries(*self.previous_retry_values)

    async def test_add_delete_bookmark(self):
        """Testing FilePickerAPI.toggle_bookmark_from_path updates persistent settings"""
        with patch("omni.client.add_bookmark") as mock_add_bookmark,\
            patch("omni.client.remove_bookmark") as mock_remove_bookmark:
            test_name, test_path = "zXuo24Qjb", "omniverse://ov-zXuo24Qjb/bookmarked_dir"
            test_view = FilePickerView("test-view")
            under_test = FilePickerAPI(FilePickerModel(), test_view)
            await ui_test.human_delay(4)
            # Test adding new bookmark
            self.assertFalse(test_view.has_connection_with_name(test_name, collection="bookmarks"))
            under_test.toggle_bookmark_from_path(test_name, test_path, True)
            self.assertTrue(test_view.has_connection_with_name(test_name, collection="bookmarks"))
            await omni.kit.app.get_app().next_update_async()
            mock_add_bookmark.assert_called_with(test_name, test_path + "/")

            # Test deleting bookmark
            under_test.toggle_bookmark_from_path(test_name, test_path, False)
            self.assertFalse(test_view.has_connection_with_name(test_name, collection="bookmarks"))
            await omni.kit.app.get_app().next_update_async()
            mock_remove_bookmark.assert_called_with(test_name)

    async def test_update_bookmarks_when_settings_changed(self):
        """Testing FilePickerAPI.subscribe_client_bookmarks_changed updates bookmarks in view when settings changed"""
        test_view = FilePickerView("test-view")
        under_test = FilePickerAPI(FilePickerModel(), test_view)
        under_test.subscribe_client_bookmarks_changed()

        # Assert bookmark not initially in the view
        test_name, test_path = "b0azwuYvz", "omniverse://ov-b0azwuYvz/bookmarked_dir"
        self.assertFalse(test_view.has_connection_with_name(test_name, collection="bookmarks"))

        # Confirm that after adding bookmark to settings, the view updates appropriately
        omni.client.add_bookmark(test_name, test_path)
        # bookmark refreshing has a 1 second "debounce" time, so wait for longer than that
        await asyncio.sleep(1.5)
        self.assertTrue(test_view.has_connection_with_name(test_name, collection="bookmarks"))

        # Confirm that after deleting bookmark from settings, the view updates appropriately
        omni.client.remove_bookmark(test_name)
        # bookmark refreshing has a 1 second "debounce" time, so wait for longer than that
        await asyncio.sleep(1.5)
        self.assertFalse(test_view.has_connection_with_name(test_name, collection="bookmarks"))

        # Confirm that updating bookmarks manually, the view updates appropriately
        bookmarks = {"b0azwuYvz": "omniverse://ov-b0azwuYvz/bookmarked_dir"}
        under_test._update_bookmarks(bookmarks)
        under_test._update_nucleus_servers(bookmarks)
        await asyncio.sleep(1.5)
        self.assertTrue(test_view.has_connection_with_name(test_name, collection="bookmarks"))
