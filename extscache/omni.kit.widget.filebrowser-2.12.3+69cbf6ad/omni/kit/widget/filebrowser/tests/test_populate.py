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
import omni.client
import omni.kit.app

from typing import List, Callable
from functools import partial
from datetime import datetime
from unittest.mock import Mock, patch, ANY
import os

from carb.eventdispatcher import get_eventdispatcher
from ..model import FileBrowserModel, FileBrowserItemFactory, FileBrowserItem
from ..nucleus_model import NucleusItemFactory, NucleusItem
from ..filesystem_model import FileSystemItemFactory, FileSystemItem
from .. import CONNECTION_ERROR_GLOBAL_EVENT
from . import AsyncMock


class TestNucleusPopulate(omni.kit.test.AsyncTestCase):
    """Testing omni.kit.widget.filebrowser.NucleusItem"""
    async def setUp(self):
        self.test_listings = {"omniverse://ov-test": ["Lib", "NVIDIA", "Projects", "Users"]}

    async def tearDown(self):
        pass

    class MockListEntry:
        def __init__(self, path, size=0, access=0, flags=omni.client.ItemFlags.CAN_HAVE_CHILDREN):
            self.relative_path = path
            self.size = size
            self.access = access
            self.flags = flags
            self.modified_time = datetime.now()

    async def _mock_list_async_impl(self, url: str):
        if url in self.test_listings:
            entries = [self.MockListEntry(subdir) for subdir in self.test_listings[url]]
            result = omni.client.Result.OK
        else:
            entries, result = [], omni.client.Result.ERROR_NOT_FOUND
        return result, entries

    async def _mock_list_async_exception(self, url: str):
        raise RuntimeError("Runtime error")

    async def _mock_list_async_error(self, url: str):
        return omni.client.Result.ERROR, []

    async def _mock_list_async_timeout(self, url: str, timeout = 1.0):
        await asyncio.sleep(timeout+1)

    async def test_listing_succeeds(self):
        """Testing NucleusItem.populate_async should succeed"""
        with patch("omni.client.list_async") as mock_list_async:
            mock_list_async.side_effect = self._mock_list_async_impl
            mock_callback = AsyncMock(return_value=123)

            test_path = "omniverse://ov-test"
            item = NucleusItemFactory.create_group_item(test_path, test_path)
            return_value = await item.populate_async(mock_callback)

            # Check that item has been populated
            self.assertTrue(item.populated)

            # Check that the callback was invoked and that we received its return value
            mock_callback.assert_called_once_with(omni.client.Result.OK, item.children)
            self.assertEqual(return_value, 123)

    async def test_listing_raises_exception(self):
        """Testing NucleusItem.populate_async should catch Exception"""
        with patch("omni.client.list_async") as mock_list_async:
            mock_list_async.side_effect = self._mock_list_async_exception
            mock_callback = AsyncMock()
            mock_sub_callback = Mock()

            test_path = "omniverse://ov-test"
            item = NucleusItemFactory.create_group_item(test_path, test_path)

            # Listen for connection error events
            event_stream_sub = get_eventdispatcher().observe_event(event_name=CONNECTION_ERROR_GLOBAL_EVENT, on_event=mock_sub_callback)
            await item.populate_async(mock_callback)

            # Check that the callback was invoked with Exception result.
            result, _ = mock_callback.call_args[0]
            assert isinstance(result, Exception)

            # Check that item is nevertheless marked as populated
            self.assertFalse(bool(item.children))
            self.assertTrue(item.populated)

            # Confirm that an error event was sent to the subscribed callback
            await omni.kit.app.get_app().next_update_async()
            mock_sub_callback.assert_called_once()
            event = mock_sub_callback.call_args[0][0]
            self.assertTrue(event["url"] == test_path)

    async def test_listing_returns_error(self):
        """Testing NucleusItem.populate_async should return error"""
        with patch("omni.client.list_async") as mock_list_async:
            mock_list_async.side_effect = self._mock_list_async_error
            mock_callback = AsyncMock()
            mock_sub_callback = Mock()

            test_path = "omniverse://ov-test"
            item = NucleusItemFactory.create_group_item(test_path, test_path)

            # Listen for connection error events
            event_stream_sub = get_eventdispatcher().observe_event(event_name=CONNECTION_ERROR_GLOBAL_EVENT, on_event=mock_sub_callback)
            await item.populate_async(mock_callback)

            # Check that the callback was invoked with Exception result.
            result, _ = mock_callback.call_args[0]
            assert isinstance(result, RuntimeWarning)

            # Check that item is nevertheless marked as populated
            self.assertFalse(bool(item.children))
            self.assertTrue(item.populated)

            # Check that an error event was sent to the subscribed callback
            await omni.kit.app.get_app().next_update_async()
            mock_sub_callback.assert_called_once()
            event = mock_sub_callback.call_args[0][0]
            self.assertTrue(event["url"] == test_path)

    async def test_listing_times_out(self):
        """Testing NucleusItem.populate_async times out"""
        with patch("omni.client.list_async") as mock_list_async:
            timeout = 1.0
            mock_list_async.side_effect = self._mock_list_async_timeout
            mock_callback = AsyncMock()
            mock_sub_callback = Mock()

            test_path = "omniverse://ov-test"
            item = NucleusItemFactory.create_group_item(test_path, test_path)

            # Listen for connection error events
            event_stream_sub = get_eventdispatcher().observe_event(event_name=CONNECTION_ERROR_GLOBAL_EVENT, on_event=mock_sub_callback)
            await item.populate_async(mock_callback, timeout=timeout)

            # Check that the callback was invoked with Exception result.
            result, _ = mock_callback.call_args[0]
            assert isinstance(result, RuntimeWarning)

            # Check that item is nevertheless marked as populated
            self.assertFalse(bool(item.children))
            self.assertTrue(item.populated)

            # Check that an error event was sent to the subscribed callback
            await omni.kit.app.get_app().next_update_async()
            mock_sub_callback.assert_called_once()
            event = mock_sub_callback.call_args[0][0]
            self.assertTrue(event["url"] == test_path)

    async def test_listing_called_just_once(self):
        """Testing NucleusItem.populate_async should not populate item if already populated"""
        with patch("omni.client.list_async") as mock_list_async:
            mock_list_async.side_effect = self._mock_list_async_impl

            test_path = "omniverse://ov-test"
            item = NucleusItemFactory.create_group_item(test_path, test_path)
            await item.populate_async(None)

            # Check that item has been populated
            self.assertTrue(bool(item.children) and item.populated)

            # Populate again and again
            await item.populate_async(None)
            await item.populate_async(None)

            # Check that the call to list_async ran only the first time
            self.assertEqual(mock_list_async.call_count, 1)


class TestFileSystemPopulate(omni.kit.test.AsyncTestCase):
    """Testing omni.kit.widget.filebrowser.FileSystemItem"""
    async def setUp(self):
        self.test_listings = {"C:": ["Program Files", "ProgramData", "temp", "Users", "Windows"]}

    async def tearDown(self):
        pass

    class MockDirEntry:
        def __init__(self, path: str, file_attrs: int = 0, symlink: bool = False):
            self.name = path
            self.path = path
            self._file_attrs = file_attrs
            self._symlink = symlink

        def stat(self):
            from collections import namedtuple
            MockStat = namedtuple("MockStat", "st_file_attributes st_size, st_mode, st_mtime")
            return MockStat(self._file_attrs, 0, 0, 0)

        def is_dir(self):
            True

        def is_symlink(self):
            return self._symlink

    class MockDirEntryIterator:
        def __init__(self, subdirs = List[str]):
            self._subdirs = subdirs
            self._current = 0

        def __iter__(self):
            return self

        def __next__(self):
            if self._current < len(self._subdirs):
                entry = TestFileSystemPopulate.MockDirEntry(self._subdirs[self._current])
                self._current += 1
                return entry
            else:
                raise StopIteration

        def __enter__(self):
            return self.__iter__()

        def __exit__(self, e_type, e_val, e_traceback):
            return False


    class MockFileSystemItem:
        def __init__(self, path: str, name: str):
            self.populated = False
            self.is_folder = True
            self.writeable = True
            self.item_changed = False
            self.name = name
            self.path = path


    def _mock_os_scandir_impl(self, path: str):
        if path in self.test_listings:
            subdirs = self.test_listings[path]
        else:
            subdirs = []
        return self.MockDirEntryIterator(subdirs)

    def _mock_create_entry_item_impl(self, entry: os.DirEntry):
        if entry.name == "temp":
            raise PermissionError("No permission testing")
        return self.MockFileSystemItem(entry.path, entry.name)

    async def test_listing_succeeds(self):
        """Testing FileSystemItem.populate_async should succeed"""
        with patch("os.scandir") as mock_os_scandir:
            with patch("omni.kit.widget.filebrowser.FileSystemItem.keep_entry") as mock_keep_entry:
                mock_os_scandir.side_effect = self._mock_os_scandir_impl
                mock_keep_entry.return_value = True
                mock_callback = AsyncMock(return_value=123)

                test_path = "C:"
                item = FileSystemItemFactory.create_group_item(test_path, test_path)
                return_value = await item.populate_async(mock_callback)

                # Check that item has been populated
                self.assertTrue(item.populated)

                # Check that the callback was invoked and that we received its return value
                mock_callback.assert_called_once_with(None, item.children)
                self.assertEqual(return_value, 123)

    async def test_listing_with_no_child_permission(self):
        """Testing FileSystemItem.populate_async should succeed even if there are children without permission to visit."""
        with patch("os.scandir") as mock_os_scandir:
            with patch("omni.kit.widget.filebrowser.FileSystemItem.keep_entry") as mock_keep_entry:
                with patch.object(FileSystemItemFactory, 'create_entry_item', Mock(side_effect=self._mock_create_entry_item_impl)):
                    mock_os_scandir.side_effect = self._mock_os_scandir_impl
                    mock_keep_entry.return_value = True
                    mock_callback = AsyncMock(return_value=123)

                    test_path = "C:"
                    item = FileSystemItemFactory.create_group_item(test_path, test_path)
                    return_value = await item.populate_async(mock_callback)

                    # Check that item has been populated
                    self.assertTrue(item.populated)

                    # Check all children populated except "temp" due to expected PermissionError
                    self.assertEqual(set(item.children.keys()), {"Program Files", "ProgramData", "Users", "Windows"})

                    # Check that the callback was invoked and that we received its return value
                    mock_callback.assert_called_once_with(None, item.children)
                    self.assertEqual(return_value, 123)

    async def test_listing_returns_empty(self):
        """Testing FileSystemItem.populate_async returns empty"""
        with patch("os.scandir") as mock_os_scandir:
            with patch("omni.kit.widget.filebrowser.FileSystemItem.keep_entry") as mock_keep_entry:
                mock_os_scandir.side_effect = self._mock_os_scandir_impl
                mock_keep_entry.return_value = True
                mock_callback = AsyncMock(return_value=123)

                test_path = "O:"
                item = FileSystemItemFactory.create_group_item(test_path, test_path)
                return_value = await item.populate_async(mock_callback)

                # Check that item has not been populated
                self.assertFalse(bool(item.children) and item.populated)

                # Check that the callback was invoked and that we received its return value
                mock_callback.assert_called_once_with(None, ANY)
                self.assertEqual(return_value, 123)

    async def test_keep_entry(self):
        """Testing FileSystemItem.keep_entry returns True for valid entries"""
        import stat

        with patch("os.name", "nt"):
            self.assertTrue(
                FileSystemItem.keep_entry(self.MockDirEntry("Desktop")))
            self.assertTrue(
                FileSystemItem.keep_entry(self.MockDirEntry(".thumbs", file_attrs=stat.FILE_ATTRIBUTE_HIDDEN)))
            self.assertFalse(
                FileSystemItem.keep_entry(self.MockDirEntry("System", file_attrs=stat.FILE_ATTRIBUTE_SYSTEM)))

        with patch("os.name", "posix"):
            self.assertTrue(
                FileSystemItem.keep_entry(self.MockDirEntry("home")))
            self.assertTrue(
                FileSystemItem.keep_entry(self.MockDirEntry("link@", symlink=True)))

    async def test_error_in_item_creation(self):
        """
        Testing that when there's error in item creation, directory listing is not affected, but will only omit the
        item with error.
        """
        from omni import ui

        with patch("os.scandir") as mock_os_scandir:
            with patch("omni.kit.widget.filebrowser.FileSystemItem.keep_entry") as mock_keep_entry, \
                    patch.object(ui.SimpleStringModel, "__init__") as mock_raise:
                mock_os_scandir.side_effect = self._mock_os_scandir_impl
                mock_keep_entry.return_value = True
                mock_raise.side_effect = RuntimeError("dummy")

                test_path = "C:"
                item = FileSystemItemFactory.create_group_item(test_path, test_path)
                self.assertIsNone(item)


class TestFileBrowserPopulate(omni.kit.test.AsyncTestCase):
    """Testing omni.kit.widget.filebrowser.FileBrowserItem"""
    async def setUp(self):
        self.test_listings = {"omniverse://ov-test": ["Lib", "NVIDIA", "Projects", "Users"]}
        self._timeout = 1.0

    async def tearDown(self):
        pass

    async def _mock_populate_async_impl(self, item: FileBrowserItem, callback_async: Callable, timeout: float = 1.0):
        if not item.populated:
            if item.path in self.test_listings:
                subdirs = self.test_listings[item.path]
            else:
                subdirs = []
            for subdir in subdirs:
                item.add_child(FileBrowserItemFactory.create_group_item(subdir, f"{item.path}/{subdir}"))
            item.populated = True
        return await callback_async(None, item.children)

    async def _mock_populate_async_timeout(self, item: FileBrowserItem, callback_async: Callable, timeout: float = 1.0):
        return await callback_async(asyncio.TimeoutError(), None)

    async def test_populate_with_callback_succeeds(self):
        """Testing FileBrowserItem.populate_with_callback should invoke callback"""
        with patch.object(FileBrowserItem, "populate_async", autospec=True) as mock_populate_async:
            mock_populate_async.side_effect = self._mock_populate_async_impl
            mock_callback = Mock()

            test_path = "omniverse://ov-test"
            item = FileBrowserItemFactory.create_group_item(test_path, test_path)
            item.populate_with_callback(mock_callback, timeout=self._timeout)

            # Wait for the thread to finish, then check that callback was invoked
            await omni.kit.app.get_app().next_update_async()

            mock_callback.assert_called_once_with(item.children)

    async def test_populate_with_callback_times_out(self):
        """Testing FileBrowserItem.populate_with_callback times out"""
        with patch.object(FileBrowserItem, "populate_async", autospec=True) as mock_populate_async:
            mock_populate_async.side_effect = self._mock_populate_async_timeout
            mock_callback = Mock()

            test_path = "omniverse://ov-test"
            item = FileBrowserItemFactory.create_group_item(test_path, test_path)
            item.populate_with_callback(mock_callback, timeout=self._timeout)

            # Wait for the thread to finish, then check that callback was not invoked
            await omni.kit.app.get_app().next_update_async()

            mock_callback.assert_not_called()

    async def test_get_item_children_succeeds(self):
        """Testing FileBrowserModel.get_item_children should populate asynchronously"""
        with patch.object(FileBrowserItem, "populate_async", autospec=True) as mock_populate_async:
            mock_populate_async.side_effect = self._mock_populate_async_impl
            mock_item_changed_callback = Mock()

            test_path = "omniverse://ov-test"
            model = FileBrowserModel(test_path, test_path, timeout=self._timeout)
            model.add_item_changed_fn(mock_item_changed_callback)

            item = model.root
            self.assertFalse(item.populated)
            # Check that the call immediately returns but with initially empty children list
            children = model.get_item_children(item)
            self.assertEqual(children, [])

            # Wait til populate_async fulfills its task
            await omni.kit.app.get_app().next_update_async()

            # Check again and confirm item is now populated with expected children
            self.assertTrue(item.populated)
            children = model.get_item_children(item)
            self.assertEqual([c.name for c in children], self.test_listings.get(test_path))

            # Confirm item changed was called
            await omni.kit.app.get_app().next_update_async()
            mock_item_changed_callback.assert_called_once_with(model, item)
