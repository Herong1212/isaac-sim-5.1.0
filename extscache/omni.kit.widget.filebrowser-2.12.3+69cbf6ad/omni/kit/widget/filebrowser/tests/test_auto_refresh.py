## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
import omni.client
import omni.kit.app

from datetime import datetime
from typing import Callable
from unittest.mock import  patch
from ..model import FileBrowserModel, FileBrowserItemFactory
from ..nucleus_model import NucleusItemFactory
from ..filesystem_model import FileSystemItemFactory
from ..widget import FileBrowserWidget
from ..tree_view import FileBrowserTreeView
from ..grid_view import FileBrowserGridView, FileBrowserGridViewDelegate


class MockListEntry:
    def __init__(self, path, size=0, access=0, flags=omni.client.ItemFlags.CAN_HAVE_CHILDREN):
        self.relative_path = path
        self.size = size
        self.access = access
        self.flags = flags
        self.modified_time = datetime.now()
        self.deleted = False


class MockListSubscription:
    def __init__(self, url, list_cb, list_change_cb):
        self._url = url
        self._list_cb = list_cb
        self._list_change_cb = list_change_cb
        self._events = []
        self._cur_event = 0

    def queue_event(self, result: omni.client.Result, event: omni.client.ListEvent, entry: MockListEntry):
        self._events.append((result, event, entry))

    def next_event(self, url: str) -> omni.client.ListEvent:
        if url == self._url and self._cur_event < len(self._events):
            result, event, entry = self._events[self._cur_event]
            if self._list_change_cb:
                self._list_change_cb(result, event, entry)
            self._cur_event += 1
            return event
        else:
            return None


async def after_redraw_async(frames=1):
    for _ in range(frames + 1):
        await omni.kit.app.get_app().next_update_async()


class TestAutoRefresh(omni.kit.test.AsyncTestCase):
    """Testing FileSystemItem.content_changed_async"""
    async def setUp(self):
        self.test_list_subscription = None
        self._throttle_frames = 4

    async def tearDown(self):
        # Wait a few frames for delayed item changed events to clear the system
        await after_redraw_async(self._throttle_frames)

    def _mock_list_subscribe_impl(self, url: str, list_cb: Callable, list_change_cb: Callable):
        self.test_list_subscription = MockListSubscription(url, list_cb, list_change_cb)

    def _mock_list_writeable_change_impl(self, url: str):
        return (omni.client.Result.OK, [MockListEntry("foo.usd", access=omni.client.AccessFlags.READ | omni.client.AccessFlags.WRITE)])

    async def test_auto_refresh_nucleus_folder(self):
        """Testing FileBrowserModel.auto_refresh_item monitors Nucleus folder for changes"""
        with patch.object(omni.client, "list_subscribe_with_callback", side_effect=self._mock_list_subscribe_impl),\
            patch.object(FileBrowserModel, "_item_changed") as mock_item_changed:

            test_url = "omniverse://ov-test/watched"
            model = FileBrowserModel("ov-test", "omniverse://ov-test")
            watched = NucleusItemFactory.create_group_item("watched", test_url)
            model.root.add_child(watched)

            # Queue up events
            model.auto_refresh_item(watched, throttle_frames=self._throttle_frames)
            self.test_list_subscription.queue_event(omni.client.Result.OK, omni.client.ListEvent.CREATED, MockListEntry("foo.usd"))
            self.test_list_subscription.queue_event(omni.client.Result.OK, omni.client.ListEvent.CREATED, MockListEntry("bar.mdl"))
            self.test_list_subscription.queue_event(omni.client.Result.OK, omni.client.ListEvent.DELETED, MockListEntry("foo.usd"))
            self.test_list_subscription.queue_event(omni.client.Result.OK, omni.client.ListEvent.DELETED, MockListEntry("bar.mdl"))

            # Created foo.usd
            self.assertEqual(len(watched.children), 0)
            self.test_list_subscription.next_event(watched.path)
            self.assertEqual(len(watched.children), 1)
            self.assertTrue("foo.usd" in watched.children)

            # Created bar.mdl
            self.test_list_subscription.next_event(watched.path)
            self.assertEqual(len(watched.children), 2)
            self.assertTrue("bar.mdl" in watched.children)

            # Deleted foo.usd
            self.test_list_subscription.next_event(watched.path)
            self.assertEqual(len(watched.children), 2)
            # To implement soft deleted feature, we don't real delete the item, set it's delete flag instead
            self.assertTrue(watched.children["foo.usd"].is_deleted)
            self.assertTrue(not watched.children["bar.mdl"].is_deleted)

            # Deleted bar.mdl
            self.test_list_subscription.next_event(watched.path)
            self.assertEqual(len(watched.children), 2)
            self.assertTrue(watched.children["bar.mdl"].is_deleted)

            # Confirm item changes queued up and triggered only once after next frame
            await after_redraw_async(self._throttle_frames)
            mock_item_changed.assert_called_once_with(watched)

    async def test_auto_refresh_filesystem_folder(self):
        """Testing FileBrowserModel.auto_refresh_item monitors Filesystem folder for changes"""
        with patch("omni.client.list_subscribe_with_callback", side_effect=self._mock_list_subscribe_impl),\
            patch.object(FileBrowserModel, "_item_changed") as mock_item_changed:

            test_url = "C://watched"
            model = FileBrowserModel("C:", "C:")
            watched = FileSystemItemFactory.create_group_item("watched", test_url)
            model.root.add_child(watched)

            # Queue up events
            model.auto_refresh_item(watched, throttle_frames=self._throttle_frames)
            self.test_list_subscription.queue_event(omni.client.Result.OK, omni.client.ListEvent.CREATED, MockListEntry("foo.usd"))
            self.test_list_subscription.queue_event(omni.client.Result.OK, omni.client.ListEvent.CREATED, MockListEntry("bar.mdl"))
            self.test_list_subscription.queue_event(omni.client.Result.OK, omni.client.ListEvent.DELETED, MockListEntry("foo.usd"))
            self.test_list_subscription.queue_event(omni.client.Result.OK, omni.client.ListEvent.DELETED, MockListEntry("bar.mdl"))

            # Created foo.usd
            self.assertEqual(len(watched.children), 0)
            self.test_list_subscription.next_event(watched.path)
            self.assertEqual(len(watched.children), 1)
            self.assertTrue("foo.usd" in watched.children)

            # Created bar.mdl
            self.test_list_subscription.next_event(watched.path)
            self.assertEqual(len(watched.children), 2)
            self.assertTrue("bar.mdl" in watched.children)

            # Deleted foo.usd
            self.test_list_subscription.next_event(watched.path)
            self.assertEqual(len(watched.children), 1)
            # To implement soft deleted feature, we don't real delete the item, set it's delete flag instead
            self.assertTrue(not "foo.usd" in watched.children)
            self.assertTrue("bar.mdl" in watched.children)

            # Deleted bar.mdl
            self.test_list_subscription.next_event(watched.path)
            self.assertEqual(len(watched.children), 0)
            self.assertTrue(not "bar.mdl" in watched.children)

            # Confirm item changes queued up and triggered only once
            await after_redraw_async(self._throttle_frames)
            mock_item_changed.assert_called_once_with(watched)

    async def test_auto_refresh_ignores_update_events(self):
        """Testing FileBrowserModel.auto_refresh_item responds to CREATED and DELETED events (OM-29866)"""
        with patch("omni.client.list_subscribe_with_callback", side_effect=self._mock_list_subscribe_impl),\
            patch.object(FileBrowserModel, "_item_changed") as mock_item_changed:

            test_url = "omniverse://ov-test/watched"
            model = FileBrowserModel("ov-test", "omniverse://ov-test")
            watched = NucleusItemFactory.create_group_item("watched", test_url)
            model.root.add_child(watched)

            model.auto_refresh_item(watched, throttle_frames=self._throttle_frames)
            self.assertEqual(len(watched.children), 0)

            # CREATED event
            mock_item_changed.reset_mock()
            self.test_list_subscription.queue_event(omni.client.Result.OK, omni.client.ListEvent.CREATED, MockListEntry("foo.usd"))
            self.test_list_subscription.next_event(watched.path)
            self.assertEqual(len(watched.children), 1)
            self.assertTrue("foo.usd" in watched.children)

            await after_redraw_async(self._throttle_frames)
            mock_item_changed.assert_called_once_with(watched)

            # UPDATED, etc. events
            self.test_list_subscription.queue_event(omni.client.Result.OK, omni.client.ListEvent.UPDATED, MockListEntry("foo.usd"))
            self.test_list_subscription.queue_event(omni.client.Result.OK, omni.client.ListEvent.LOCKED, MockListEntry("foo.usd"))
            self.test_list_subscription.queue_event(omni.client.Result.OK, omni.client.ListEvent.UNLOCKED, MockListEntry("foo.usd"))
            self.test_list_subscription.queue_event(omni.client.Result.OK, omni.client.ListEvent.UNKNOWN, MockListEntry("foo.usd"))

            mock_item_changed.reset_mock()
            while True:
                # UPDATED event
                event = self.test_list_subscription.next_event(watched.path)
                if event:
                    await after_redraw_async(self._throttle_frames)
                    self.assertTrue(event not in [omni.client.ListEvent.CREATED, omni.client.ListEvent.DELETED])
                    mock_item_changed.assert_not_called()
                else:
                    break

            # DELETED event
            mock_item_changed.reset_mock()
            self.test_list_subscription.queue_event(omni.client.Result.OK, omni.client.ListEvent.DELETED, MockListEntry("foo.usd"))
            self.test_list_subscription.next_event(watched.path)
            # To implement soft deleted feature, we don't real delete the item, set it's delete flag instead
            for child_name in watched.children:
                item = watched.children[child_name]
                item.is_deleted = True
                self.assertEqual(item.is_deleted, True)

            # Confirm item changes queued up and triggered only once
            await after_redraw_async(self._throttle_frames)
            mock_item_changed.assert_called_once_with(watched)

    async def test_auto_refresh_on_permissions_change(self):
        """Testing FileBrowserModel.auto_refresh_item responds to METADATA events (OMPE-10272)"""
        with patch("omni.client.list_subscribe_with_callback", side_effect=self._mock_list_subscribe_impl),\
            patch.object(FileBrowserModel, "_item_changed") as mock_item_changed:

            test_url = "omniverse://ov-test/watched"
            model = FileBrowserModel("ov-test", "omniverse://ov-test")
            watched = NucleusItemFactory.create_group_item("watched", test_url)
            model.root.add_child(watched)

            model.auto_refresh_item(watched, throttle_frames=self._throttle_frames)
            self.assertEqual(len(watched.children), 0)

            # create a read only file
            mock_item_changed.reset_mock()
            self.test_list_subscription.queue_event(
                omni.client.Result.OK,
                omni.client.ListEvent.CREATED,
                MockListEntry("foo.usd", access=omni.client.AccessFlags.READ)
            )
            self.test_list_subscription.next_event(watched.path)
            self.assertEqual(len(watched.children), 1)
            self.assertTrue("foo.usd" in watched.children)

            await after_redraw_async(self._throttle_frames)
            mock_item_changed.assert_called_once_with(watched)
            self.assertTrue(watched.children["foo.usd"].readable)
            self.assertFalse(watched.children["foo.usd"].writeable)

            # change the file to write able
            mock_item_changed.reset_mock()
            self.test_list_subscription.queue_event(
                omni.client.Result.OK,
                omni.client.ListEvent.METADATA,
                MockListEntry("foo.usd", access=omni.client.AccessFlags.READ|omni.client.AccessFlags.WRITE)
            )
            self.test_list_subscription.next_event(watched.path)
            self.assertEqual(len(watched.children), 1)
            self.assertTrue("foo.usd" in watched.children)

            await after_redraw_async(self._throttle_frames)
            mock_item_changed.assert_called_once_with(watched)
            self.assertTrue(watched.children["foo.usd"].readable)
            self.assertTrue(watched.children["foo.usd"].writeable)

    async def test_widget_refreshes_views(self):
        """Testing FileBrowserWidget._auto_refresh_item updates views"""
        from .. import TREEVIEW_PANE

        with patch("omni.client.list_subscribe_with_callback", side_effect=self._mock_list_subscribe_impl),\
            patch.object(FileBrowserTreeView, "refresh_ui") as mock_refresh_tree_view,\
            patch.object(FileBrowserGridView, "refresh_ui") as mock_refresh_grid_view:

            test_url = "C://watched"
            model = FileBrowserModel("C:", "C:")
            watched = FileBrowserItemFactory.create_group_item("watched", test_url)
            model.root.add_child(watched)

            # Make watched directory the current one
            under_test = FileBrowserWidget("test")
            under_test.add_model_as_subtree(model)
            under_test._on_selection_changed(TREEVIEW_PANE, [watched])

            # Queue up events
            self.test_list_subscription.queue_event(omni.client.Result.OK, omni.client.ListEvent.CREATED, MockListEntry("foo.usd"))

            # Confirm change event triggers UI refresh
            mock_refresh_tree_view.reset_mock()
            mock_refresh_grid_view.reset_mock()

            self.test_list_subscription.next_event(watched.path)
            await after_redraw_async(self._throttle_frames)
            mock_refresh_tree_view.assert_called()
            mock_refresh_grid_view.assert_called()
            under_test.destroy()

    async def test_gridview_redraws_only_once(self):
        """Testing FileBrowserGridView.refresh_ui updates grid view only once when refreshed many times"""
        with patch.object(FileBrowserGridViewDelegate, "build_grid") as mock_delegate_build_grid,\
            patch.object(FileBrowserGridViewDelegate, "update_grid") as mock_delegate_update_grid:

            model = FileBrowserModel("ov-test", "omniverse://ov-test")
            under_test = FileBrowserGridView(model)
            mock_delegate_build_grid.assert_called_once_with(model)

            # OM-78400 Clear out all refreshes from setting up the view before testing for additional ones
            await after_redraw_async(self._throttle_frames)
            mock_delegate_update_grid.reset_mock()

            # Call refresh multiple times
            under_test.refresh_ui()
            under_test.refresh_ui()
            under_test.refresh_ui()

            # Confirm that refresh doesn't immediately rebuild the grid view. Instead, after some delay,
            # builds the view only once.
            mock_delegate_update_grid.assert_not_called()
            await after_redraw_async(self._throttle_frames)
            mock_delegate_update_grid.assert_called_once_with(model)
            under_test.destroy()

    # OMFP-3551: Item changed should Update when permission changed,then it could trigger the ui update.
    async def test_refresh_writeable_changed_item(self):
        """Testing refresh item could catch the writeable attribute change"""
        with patch.object(omni.client, "list_subscribe_with_callback", side_effect=self._mock_list_subscribe_impl),\
            patch.object(omni.client, "list_async", side_effect=self._mock_list_writeable_change_impl),\
            patch.object(FileBrowserModel, "_item_changed") as mock_item_changed:

            test_url = "omniverse://ov-test/watched"
            model = FileBrowserModel("ov-test", "omniverse://ov-test")
            under_test = FileBrowserGridView(model)
            watched = NucleusItemFactory.create_group_item("watched", test_url)
            model.root.add_child(watched)

            # Queue up events
            model.auto_refresh_item(watched, throttle_frames=self._throttle_frames)
            self.test_list_subscription.queue_event(omni.client.Result.OK, omni.client.ListEvent.CREATED, MockListEntry("foo.usd"))

            # Created foo.usd
            self.test_list_subscription.next_event(watched.path)
            self.assertEqual(len(watched.children), 1)
            self.assertTrue("foo.usd" in watched.children)

            await after_redraw_async(self._throttle_frames)
            # simulate refresh ui from filepicker, and it will trigger the item changed.
            self.assertFalse(watched.children["foo.usd"].item_changed)
            watched.populated = False
            await watched.populate_async()
            under_test.refresh_ui(watched,[watched])
            self.assertTrue(watched.children["foo.usd"].item_changed)
            under_test.destroy()

class TestSyncItemChanges(omni.kit.test.AsyncTestCase):
    """Testing omni.kit.widget.filebrowser.FileBrowserModel"""
    async def setUp(self):
        self.test_frame = 0
        self.test_listings_by_frame = [["A", "B", "C"], ["B", "C", "D"]]
        self._throttle_frames = 4

    async def tearDown(self):
        # Wait a few frames for delayed item changed events to clear the system
        await after_redraw_async(self._throttle_frames)

    async def _mock_list_async_impl(self, url: str, include_deleted_option=omni.client.ListIncludeOption.INCLUDE_DELETED_FILES):
        subdirs = []
        if self.test_frame < len(self.test_listings_by_frame):
            subdirs = self.test_listings_by_frame[self.test_frame]
            self.test_frame += 1
        entries = [MockListEntry(subdir) for subdir in subdirs]
        result = omni.client.Result.OK
        return result, entries

    async def test_syncing_item_changes_succeeds(self):
        """Testing FileBrowserModel.sync_up_item_changes updates given folder"""
        with patch("omni.client.list_async") as mock_list_async:
            mock_list_async.side_effect = self._mock_list_async_impl

            test_url = "C://watched"
            watched = FileSystemItemFactory.create_group_item("watched", test_url)
            under_test = FileBrowserModel("C:", "C:")
            under_test.root.add_child(watched)

            under_test.sync_up_item_changes(watched)
            await omni.kit.app.get_app().next_update_async()
            test_subdirs_0 = self.test_listings_by_frame[0]
            self.assertEqual(test_subdirs_0, [name for name in watched.children])

            under_test.sync_up_item_changes(watched)
            await omni.kit.app.get_app().next_update_async()
            test_subdirs_1 = self.test_listings_by_frame[1]
            self.assertEqual(test_subdirs_1, [name for name in watched.children])
