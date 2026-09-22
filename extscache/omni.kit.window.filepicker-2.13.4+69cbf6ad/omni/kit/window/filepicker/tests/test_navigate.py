## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import os
import platform
import omni.kit.test
import asyncio
import omni.kit.app
import omni.client

from typing import Callable
from unittest.mock import Mock, patch, ANY, call
from ..api import FilePickerAPI
from ..collections.bookmark_collection import BookmarkCollectionItem
from ..collections.nucleus_collection import NucleusCollectionItem
from ..collections.filesystem_collection import FileSystemCollectionItem
from ..model import FilePickerModel
from ..view import FilePickerView
from .test_utils import time_logger
from omni.kit.widget.filebrowser import FileBrowserModel, FileBrowserItem, FileBrowserItemFactory


@time_logger
class TestSanitizePath(omni.kit.test.AsyncTestCase):
    """Testing FilePickerModel.sanitize_path"""
    async def setUp(self):
        self.previous_retry_values = omni.client.set_retries(0, 0, 0)
        self.test_paths = [
            ("my-computer://C:\\temp\\test\\file.mdl", "my-computer://c:/temp/test/file.mdl"),
            ("     /home/user/    ", "/home/user/"),
            (
                "http://content.ov.nvidia.com/omniverse://ov-content/Users/zbowman@nvidia.com/Bugs/OM21975/OM21975.usd",
                "omniverse://ov-content/Users/zbowman@nvidia.com/Bugs/OM21975/OM21975.usd",
            ),
            (
                "omniverse://content.ov.nvidia.com/Users/agrant@nvidia.com/assets/FREE_%C5%BBuk_3D_model.usdz",
                "omniverse://content.ov.nvidia.com/Users/agrant@nvidia.com/assets/FREE_Żuk_3D_model.usdz",
            )
        ]

    async def tearDown(self):
        omni.client.set_retries(*self.previous_retry_values)

    async def test_sanitize_path(self):
        """Testing FilePickerModel.sanitize_path returns expected path after normalization"""
        under_test = FilePickerModel()
        for test_path in self.test_paths:
            input, expected = test_path
            self.assertEqual(under_test.sanitize_path(input), expected)


@time_logger
class TestFindItemInSubTree(omni.kit.test.AsyncTestCase):
    """Testing FilePickerModel.find_item_in_subtree_async"""
    async def setUp(self):
        self.previous_retry_values = omni.client.set_retries(0, 0, 0)
        self.test_listings = {
            "omniverse://": ["omniverse://ov-sandbox", "omniverse://ov-test"],
            "omniverse://ov-test": ["Lib", "NVIDIA", "Projects", "Users"],
            "omniverse://ov-test/NVIDIA": ["Assets", "Materials", "Samples"],
            "omniverse://ov-test/NVIDIA/Samples": ["Astronaut", "Flight", "Marbles", "Attic"],
            "omniverse://ov-test/NVIDIA/Samples/Astronaut": ["Astronaut.usd", "Materials", "Props"],
            "my-computer://": ["/", "Desktop", "Documents", "Downloads"],
            "/": ["bin", "etc", "home", "lib", "tmp"],
            "/home": ["jack", "jill"],
            "/home/jack": ["Desktop", "Documents", "Downloads"],
            "/home/jack/Documents": ["test.usd"],
        }

    async def tearDown(self):
        omni.client.set_retries(*self.previous_retry_values)

    async def _mock_populate_async_impl(self, item: FileBrowserItem, callback_async: Callable):
        if not item.populated:
            if item.path in self.test_listings:
                subdirs = self.test_listings[item.path]
            else:
                subdirs = []
            for subdir in subdirs:
                if item.path.endswith("://"):
                    path = subdir
                elif item.path == "/":
                    path = f"/{subdir}"
                else:
                    path = f"{item.path}/{subdir}"
                item.add_child(FileBrowserItemFactory.create_group_item(subdir, path))
            item.populated = True
        return None

    async def _mock_populate_async_timeout(self, item: FileBrowserItem, callback_async: Callable):
        return asyncio.TimeoutError(1.0)

    async def test_find_nucleus_path_succeeds(self):
        """Testing FilePickerModel.find_item_in_subtree_async with Nucleus path should succeed"""
        with patch.object(FileBrowserItem, "populate_async", autospec=True) as mock_populate_async:
            mock_populate_async.side_effect = self._mock_populate_async_impl

            root_name = "ov-test"
            model = FileBrowserModel(root_name, f"omniverse://{root_name}")
            collection = FileBrowserItemFactory.create_group_item("Omniverse", "omniverse://")
            collection.add_child(model.root)

            test_path = f"{root_name}/NVIDIA/Samples/Astronaut/Astronaut.usd"
            under_test = FilePickerModel()
            item = await under_test.find_item_in_subtree_async(collection, test_path)

            assert item != None
            self.assertEqual(item.path, f"omniverse://{test_path}")

    async def test_find_linux_path_succeeds(self):
        """Testing FilePickerModel.find_item_in_subtree_async with Linux path should succeed"""
        with patch.object(FileBrowserItem, "populate_async", autospec=True) as mock_populate_async:
            mock_populate_async.side_effect = self._mock_populate_async_impl

            root_name = "/"
            model = FileBrowserModel(root_name, root_name)
            collection = FileBrowserItemFactory.create_group_item("My Computer", "my-computer://")
            collection.add_child(model.root)

            test_path = "/home/jack/Documents/test.usd"
            under_test = FilePickerModel()
            item = await under_test.find_item_in_subtree_async(collection, test_path)

            assert item != None
            self.assertEqual(item.path, test_path)

    async def test_find_invalid_path_fails(self):
        """Testing FilePickerModel.find_item_in_subtree_async from aliased Nucleus path should succeed"""
        with patch.object(FileBrowserItem, "populate_async", autospec=True) as mock_populate_async:
            mock_populate_async.side_effect = self._mock_populate_async_impl

            root_name = "ov-test"
            model = FileBrowserModel(root_name, f"omniverse://{root_name}")
            collection = FileBrowserItemFactory.create_group_item("Omniverse", "omniverse://")
            collection.add_child(model.root)

            # Expect exception.
            with self.assertRaises(RuntimeWarning) as e:
                test_path = f"{root_name}/invalid/path"
                under_test = FilePickerModel()
                await under_test.find_item_in_subtree_async(collection, test_path)

            assert str(e.exception).startswith("Path not found")

    async def test_populate_async_times_out(self):
        """Testing FileBrowserItem.populate_async times out"""
        with patch.object(FileBrowserItem, "populate_async", autospec=True) as mock_populate_async:
            mock_populate_async.side_effect = self._mock_populate_async_timeout

            root_name = "ov-test"
            model = FileBrowserModel(root_name, f"omniverse://{root_name}")
            collection = FileBrowserItemFactory.create_group_item("Omniverse", "omniverse://")
            collection.add_child(model.root)

            # Expect timeout exception.
            with self.assertRaises(asyncio.TimeoutError) as e:
                test_path = f"{root_name}/NVIDIA/Samples/Astronaut/Astronaut.usd"
                under_test = FilePickerModel()
                await under_test.find_item_in_subtree_async(collection, test_path)


@time_logger
class TestFindItem(omni.kit.test.AsyncTestCase):
    """Testing FilePickerModel.find_item_async"""
    async def setUp(self):
        self.previous_retry_values = omni.client.set_retries(0, 0, 0)
        self.collections = {
            "omniverse": NucleusCollectionItem(),
            "my-computer": FileSystemCollectionItem(),
            "bookmarks": BookmarkCollectionItem(),
        }
        self.test_listings = {
            self.collections["omniverse"]: [
                "omniverse://ov-test/NVIDIA/Samples/Astronaut/Astronaut.usd",
            ],
            self.collections["my-computer"]: [
                "/home/jack/Documents/foo.usd",
                "/Downloads/bar.usd",
            ],
            self.collections["bookmarks"]: [
                "omniverse://ov-test/NVIDIA/Samples/Astronaut/Astronaut.usd",
            ]
        }

    async def tearDown(self):
        omni.client.set_retries(*self.previous_retry_values)

    async def _mock_find_item_in_subtree_async_impl(self, root: FileBrowserItem, path: str):
        if root in self.test_listings:
            for fullpath in self.test_listings[root]:
                if fullpath.endswith(path):
                    return FileBrowserItemFactory.create_group_item(os.path.basename(path), fullpath)
        raise RuntimeWarning(f"Path not found: '{path}'")

    async def test_parse_collection_succeeds(self):
        """Testing FilePickerModel.find_item_async should search the appropriate collection"""
        with patch.object(FilePickerModel, "find_item_in_subtree_async") as mock_find_item_in_subtree:
            test_path = "path/to/my/file.usd"
            under_test = FilePickerModel()
            under_test.collections = self.collections

            # Path with explicit 'omniverse://' prefix should search the omniverse collection
            mock_find_item_in_subtree.reset_mock()
            await under_test.find_item_async(f"omniverse://{test_path}", None)
            mock_find_item_in_subtree.assert_called_once_with(self.collections.get("omniverse"), test_path)

            # Path with no 'omniverse://' prefix should search the local collection
            mock_find_item_in_subtree.reset_mock()
            await under_test.find_item_async(test_path, None)
            mock_find_item_in_subtree.assert_called_once_with(self.collections.get("my-computer"), test_path)

    async def test_collection_root_found(self):
        """Testing FilePickerModel.find_item_async finds url path if it belongs to a collection root."""
        under_test = FilePickerModel()
        under_test.collections = self.collections
        for url in ("omniverse", "my-computer", "bookmarks"):
            found = await under_test.find_item_async(url + "://")
            self.assertIs(found, self.collections[url])

    async def test_omniverse_url_found(self):
        """Testing FilePickerModel.find_item_async execs callback when omniverse path is found"""
        with patch.object(FilePickerModel, "find_item_in_subtree_async") as mock_find_item_in_subtree:
            mock_find_item_in_subtree.side_effect = self._mock_find_item_in_subtree_async_impl
            mock_callback = Mock()

            test_path = "omniverse://ov-test/NVIDIA/Samples/Astronaut/Astronaut.usd"
            under_test = FilePickerModel()
            under_test.collections = self.collections
            found = await under_test.find_item_async(test_path, mock_callback)
            self.assertEqual(found.path, test_path)

    async def test_filesystem_url_found(self):
        """Testing FilePickerModel.find_item_async execs callback when local path is found"""
        with patch.object(FilePickerModel, "find_item_in_subtree_async") as mock_find_item_in_subtree:
            mock_find_item_in_subtree.side_effect = self._mock_find_item_in_subtree_async_impl
            mock_callback = Mock()

            test_path = "/home/jack/Documents/foo.usd"
            under_test = FilePickerModel()
            under_test.collections = self.collections
            found = await under_test.find_item_async(test_path, mock_callback)
            self.assertEqual(found.path, test_path)

    async def test_path_not_found(self):
        """Testing FilePickerModel.find_item_async execs callback when path not found"""
        with patch.object(FilePickerModel, "find_item_in_subtree_async") as mock_find_item_in_subtree:
            mock_find_item_in_subtree.side_effect = self._mock_find_item_in_subtree_async_impl
            mock_callback = Mock()

            test_path = "invalid/path"
            under_test = FilePickerModel()
            under_test.collections = self.collections
            found = await under_test.find_item_async(test_path, mock_callback)

            # After searching all collections and not finding the path, exec callback with input set to None
            self.assertEqual(found, None)
            mock_callback.assert_called_once_with(None)

    async def test_aliased_omniverse_url_searched(self):
        """Testing FilePickerModel.find_item_async searches both the aliased and real server paths"""
        # Create a server connection with an aliased name
        root = self.collections["omniverse"]
        serv = FileBrowserItemFactory.create_group_item("ov-alias", "omniverse://ov-test")
        root.add_child(serv)

        with patch.object(FilePickerModel, "find_item_in_subtree_async") as mock_find_item_in_subtree:
            mock_find_item_in_subtree.side_effect = self._mock_find_item_in_subtree_async_impl
            test_path = "omniverse://ov-test/file/not/found.usd"
            under_test = FilePickerModel()
            under_test.collections = self.collections
            found = await under_test.find_item_async(test_path)

        # Even though Url is not found, confirm that it was searched for under both the aliased and real server names.
        self.assertEqual(found, None)
        self.assertEqual(mock_find_item_in_subtree.call_count, 2)
        expected_path = test_path.replace("omniverse://", "")
        # First, search all servers under root, but expect not find item in the server named "ov-alias"
        self.assertEqual(mock_find_item_in_subtree.call_args_list[0], call(root, expected_path))
        # Even though the server is named "ov-alias", it's real path is "ov-test". Expect to search this specific server.
        self.assertEqual(mock_find_item_in_subtree.call_args_list[1], call(serv, expected_path.replace("ov-test/", "")))


@time_logger
class TestApiNavigate(omni.kit.test.AsyncTestCase):
    """Testing FilePickerAPI.navigate_to"""
    async def setUp(self):
        self.previous_retry_values = omni.client.set_retries(0, 0, 0)
        self.test_listings = [
            "omniverse://ov-test/NVIDIA/Samples/Astronaut/Astronaut.usd",
        ]

    async def tearDown(self):
        omni.client.set_retries(*self.previous_retry_values)

    async def _mock_find_item_async_impl(self, url: str, callback: Callable = None):
        item = None
        if url in self.test_listings:
            item = FileBrowserItemFactory.create_group_item(os.path.basename(url), url)
        return item

    async def _mock_find_item_async_hangs(self, url: str, callback: Callable = None):
        while True:
            await asyncio.sleep(.1)

    def _mock_connect_server_impl(self, name: str, server_url: str, on_success_fn: Callable = None, on_failed_fn: Callable = None):
        if on_success_fn:
            on_success_fn(name, server_url)

    async def _mock_stat_async_succeeds(self, url: str):
        return omni.client.Result.OK, None

    async def _mock_long_time_stat_async_succeeds(self, url: str):
        await asyncio.sleep(10)
        return omni.client.Result.OK, None

    async def _mock_stat_async_fails(self, url: str):
        return omni.client.Result.ERROR, None

    async def test_local_path(self):
        """Testing FilePickerModel.is_local_path returns expected answer"""
        under_test = FilePickerModel()

        self.assertTrue(under_test.is_local_path("file:/home/usr/data/foo.usd"))
        if os.name == "nt":
            self.assertTrue(under_test.is_local_path("C:/temp/foo.usd"))
            self.assertTrue(under_test.is_local_path("z:/temp/foo.usd"))
        else:
            self.assertTrue(under_test.is_local_path("/home/user/data/foo.usd"))
        self.assertFalse(under_test.is_local_path("omniverse://ov-test/foo.usd"))
        self.assertFalse(under_test.is_local_path("ov-test/foo.usd"))

    async def test_path_found(self):
        """Testing FilePickerAPI.navigate_to execs callback when Omniverse path found"""
        with patch.object(FilePickerModel, "find_item_async", side_effect=self._mock_find_item_async_impl),\
            patch.object(FilePickerView, "has_connection_with_name", return_value=True),\
            patch.object(FilePickerView, "select_and_center") as mock_select_and_center,\
            patch("omni.client.stat_async", side_effect=self._mock_stat_async_succeeds):

            mock_callback = Mock()
            test_path = "omniverse://ov-test/NVIDIA/Samples/Astronaut/Astronaut.usd"
            under_test = FilePickerAPI(FilePickerModel(), FilePickerView("test-view"))
            await under_test.navigate_to_async(test_path, mock_callback)
            await omni.kit.app.get_app().next_update_async()

            # Confirm callback exec'd, and view centered on found item
            mock_callback.assert_called_once()
            self.assertEqual(mock_callback.call_args[0][0].path, test_path)

    async def test_path_with_spaces_found(self):
        """Testing that any spaces around url are stripped and navigating to it still succeeds"""
        with patch.object(FilePickerModel, "find_item_async", side_effect=self._mock_find_item_async_impl),\
            patch.object(FilePickerView, "has_connection_with_name", return_value=True),\
            patch.object(FilePickerView, "select_and_center") as mock_select_and_center,\
            patch("omni.client.stat_async", side_effect=self._mock_stat_async_succeeds):

            mock_callback = Mock()
            test_path = "    omniverse://ov-test/NVIDIA/Samples/Astronaut/Astronaut.usd    "
            under_test = FilePickerAPI(FilePickerModel(), FilePickerView("test-view"))
            await under_test.navigate_to_async(test_path, mock_callback)
            await omni.kit.app.get_app().next_update_async()

            # Confirm callback exec'd, and view centered on found item
            mock_callback.assert_called_once()
            self.assertEqual(mock_callback.call_args[0][0].path, test_path.strip())

            mock_select_and_center.assert_called_once()
            self.assertEqual(mock_select_and_center.call_args[0][0].path, test_path.strip())

    async def test_server_not_connected(self):
        """Testing FilePickerAPI.navigate_to connects server if not already connected"""
        with patch.object(FilePickerModel, "find_item_async", side_effect=self._mock_find_item_async_impl),\
            patch.object(FilePickerView, "has_connection_with_name", return_value=False),\
            patch.object(FilePickerView, "select_and_center") as mock_select_and_center,\
            patch.object(omni.kit.window.filepicker.api, "connect", side_effect=self._mock_connect_server_impl) as mock_connect_server,\
            patch("omni.client.stat_async", side_effect=self._mock_stat_async_succeeds):

            mock_callback = Mock()
            test_path = "omniverse://ov-test/NVIDIA/Samples/Astronaut/Astronaut.usd"
            under_test = FilePickerAPI(FilePickerModel(), FilePickerView("test-view"))
            await under_test.navigate_to_async(test_path, mock_callback)
            await omni.kit.app.get_app().next_update_async()

            # Confirm attempt to connect server
            broken_url = omni.client.break_url(test_path)
            mock_connect_server.assert_called_once_with(broken_url.host, f'{broken_url.scheme}://{broken_url.host}', on_success_fn=ANY)

            # Confirm callback exec'd, and view centered on found item
            mock_callback.assert_called_once()
            self.assertEqual(mock_callback.call_args[0][0].path, test_path)

            mock_select_and_center.assert_called_once()
            self.assertEqual(mock_select_and_center.call_args[0][0].path, test_path)

    async def test_local_path_not_found(self):
        """Testing FilePickerAPI.navigate_to does not try to connect to local path"""
        with patch.object(FilePickerModel, "find_item_async", side_effect=self._mock_find_item_async_impl),\
            patch.object(omni.kit.window.filepicker.api, "connect") as mock_connect_server,\
            patch("omni.client.stat_async", side_effect=self._mock_stat_async_fails):

            test_path = "C:/test/not_found.usd"
            under_test = FilePickerAPI(FilePickerModel(), FilePickerView("test-view"))
            await under_test.navigate_to_async(test_path, callback=None)
            await omni.kit.app.get_app().next_update_async()

            # Confirm did not attempt to connect the server
            mock_connect_server.assert_not_called()

    async def test_navigate_cancelled(self):
        """Testing FilePickerAPI.navigate_to gets cancelled when hung"""
        with patch.object(FilePickerModel, "find_item_async", side_effect=self._mock_find_item_async_hangs),\
            patch.object(FilePickerView, "has_connection_with_name", return_value=True),\
            patch("omni.client.stat_async", side_effect=self._mock_stat_async_succeeds):

            mock_callback = Mock()
            test_path = "omniverse://ov-test/slow/network/Astronaut/Astronaut.usd"
            under_test = FilePickerAPI(FilePickerModel(), FilePickerView("test-view"))

            # Cancel the task 2 seconds later
            # need to wrap the cancel call in a func because at init the loading pane would be None
            def delay_cancel():
                under_test._loading_pane.cancel_task()
            loop = asyncio.get_event_loop()
            loop.call_later(2, delay_cancel, *[])
            await under_test.navigate_to_async(test_path, mock_callback)

            # Confirm callback exec'd, and view centered on found item
            mock_callback.assert_not_called()

    # OMFP-3796: test Loading Spinner does not go away even when cancel is clicked
    # It caused by the long time stat async call
    async def test_navigate_long_time_stat_cancelled(self):
        """Testing FilePickerAPI.navigate_to gets cancelled when hung"""
        with patch.object(FilePickerModel, "find_item_async", side_effect=self._mock_find_item_async_hangs),\
            patch.object(FilePickerView, "has_connection_with_name", return_value=True),\
            patch("omni.client.stat_async", side_effect=self._mock_long_time_stat_async_succeeds):

            mock_callback = Mock()
            test_path = "omniverse://ov-test/slow/network/Astronaut/Astronaut.usd"
            under_test = FilePickerAPI(FilePickerModel(), FilePickerView("test-view"))

            # Cancel the task 2 seconds later
            # need to wrap the cancel call in a func because at init the loading pane would be None
            def delay_hide():
                under_test._loading_pane.hide()
            loop = asyncio.get_event_loop()
            loop.call_later(2, delay_hide, *[])
            await under_test.navigate_to_async(test_path, mock_callback)

            # Confirm callback exec'd, and view centered on found item
            mock_callback.assert_not_called()


@time_logger
class TestApiFindSubdirs(omni.kit.test.AsyncTestCase):
    """Testing FilePickerAPI.find_subdirs_async"""
    async def setUp(self):
        self.previous_retry_values = omni.client.set_retries(0, 0, 0)
        self.test_listings = {
            "omniverse://ov-test/NVIDIA": ["Assets", "Materials", "Samples"],
        }

    async def tearDown(self):
        omni.client.set_retries(*self.previous_retry_values)

    async def _mock_find_item_async_impl(self, path: str):
        item = None
        if path in self.test_listings:
            item = FileBrowserItemFactory.create_group_item(os.path.basename(path), path)
        return item

    async def _mock_populate_async_impl(self, item: FileBrowserItem, callback: Callable):
        if not item.populated:
            if item.path in self.test_listings:
                subdirs = self.test_listings[item.path]
            else:
                subdirs = []
            for subdir in subdirs:
                item.add_child(FileBrowserItemFactory.create_group_item(subdir, f"{item.path}/{subdir}"))
            item.populated = True
        return item.children

    async def test_path_found(self):
        """Testing FilePickerAPI.find_subdirs_async execs callback when subdirs found"""
        with patch.object(FilePickerModel, "find_item_async", side_effect=self._mock_find_item_async_impl),\
            patch.object(FileBrowserItem, "populate_async", side_effect=self._mock_populate_async_impl, autospec=True):
                mock_callback = Mock()
                test_path = "omniverse://ov-test/NVIDIA"
                under_test = FilePickerAPI(FilePickerModel(), FilePickerView("test-view"))
                await under_test.find_subdirs_async(test_path, mock_callback)

                # Confirm callback exec'd with list of subdirs
                mock_callback.assert_called_once_with(self.test_listings[test_path])

    async def test_path_not_found(self):
        """Testing FilePickerAPI.find_subdirs_async execs callback with empty list when path not found"""
        with patch.object(FilePickerModel, "find_item_async", side_effect=self._mock_find_item_async_impl),\
            patch.object(FileBrowserItem, "populate_async", side_effect=self._mock_populate_async_impl, autospec=True):
                mock_callback = Mock()
                test_path = "omniverse://unknown-path"
                under_test = FilePickerAPI(FilePickerModel(), FilePickerView("test-view"))
                await under_test.find_subdirs_async(test_path, mock_callback)

                # Confirm callback exec'd with list of subdirs
                mock_callback.assert_called_once_with([])

    async def test_empty_path(self):
        """Testing FilePickerAPI.find_subdirs_async execs callback with all connections when path is empty"""
        mock_callback = Mock()

        # Initialize view and ensure it has at least one connection.
        view = FilePickerView("test-view")
        view.add_server("ov-test", "omniverse://ov-test")

        under_test = FilePickerAPI(FilePickerModel(), view)
        await under_test.find_subdirs_async("", mock_callback)

        # Confirm callback exec'd with list of all connections
        expected = []
        for collection in ['omniverse', 'my-computer']:
            expected.extend([i.path for i in under_test.view.all_collection_items(collection)])

        mock_callback.assert_called_once_with(expected)

    async def test_local_path_windows_slashes(self):
        """Testing FilePickerDialog apply path doesn't contain any windows slashes"""
        from omni.kit.window.filepicker import FilePickerDialog

        extension_path = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
        filepicker_path = f"{extension_path}/icons/NvidiaDark/"
        filepicker_filename = "omniverse_logo_64.png"
        if platform.system().lower() == "windows":
            filepicker_path = filepicker_path.replace("/", "\\")

        mock_apply_fn = Mock()
        dialog = FilePickerDialog("Testing", click_apply_handler=mock_apply_fn)
        await omni.kit.app.get_app().next_update_async()
        dialog.set_current_directory(filepicker_path)
        dialog.set_filename(filepicker_filename)
        await omni.kit.app.get_app().next_update_async()
        dialog._click_apply_handler(dialog.get_filename(), dialog.get_current_directory())
        mock_apply_fn.assert_called_once_with(filepicker_filename, filepicker_path.replace("\\", "/"))
        dialog.destroy()
