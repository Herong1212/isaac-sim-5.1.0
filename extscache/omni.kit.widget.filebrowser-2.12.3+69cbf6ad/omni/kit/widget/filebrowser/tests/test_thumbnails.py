## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import os
import asyncio
import omni.kit.test
import omni.kit.app
import omni.client
import omni.ui as ui

from unittest.mock import patch, Mock
from carb import eventdispatcher
from typing import List, Dict
from functools import partial
from ..grid_view import FileBrowserGridViewDelegate
from ..card import FileBrowserItemCard
from ..model import FileBrowserModel, FileBrowserItem, FileBrowserItemFactory
from ..thumbnails import find_thumbnails_for_files_async, list_thumbnails_for_folder_async
from .. import MISSING_IMAGE_THUMBNAILS_GLOBAL_EVENT, THUMBNAILS_GENERATED_GLOBAL_EVENT
from . import AsyncMock


class TestRefreshThumbnails(omni.kit.test.AsyncTestCase):
    """Testing FileBrowserGridViewDelegate rendering thumbnails"""
    async def setUp(self):
        self.test_dir = "omniverse://ov-test"
        self.test_thumbnail_dict = {
            f"{self.test_dir}/foo.tif": f"{self.test_dir}/.thumbs/foo.tif.png",
            f"{self.test_dir}/bar.png": f"{self.test_dir}/.thumbs/bar.png.png",
        }

    async def tearDown(self):
        pass

    def _build_test_model(self, paths: List[str]) -> FileBrowserModel:
        model = FileBrowserModel("ov-test", self.test_dir)
        for path in paths:
            model.root.add_child(
                FileBrowserItemFactory.create_dummy_item(os.path.basename(path), path))
        return model

    async def _mock_get_folder_thumbnails_impl(self) -> Dict:
        return self.test_thumbnail_dict

    async def _mock_get_folder_thumbnails_empty(self) -> Dict:
        return {}

    async def _mock_find_thumbnails_impl(self, paths: str, generate_missing: bool = False) -> Dict:
        return {path: self.test_thumbnail_dict.get(path) for path in paths}

    async def test_update_grid_succeeds(self):
        """Testing FileBrowserGridViewDelegate.update_grid successfully renders custom thumbnails"""
        with patch.object(FileBrowserItem, "get_custom_thumbnails_for_folder_async", side_effect=self._mock_get_folder_thumbnails_impl),\
            patch.object(FileBrowserItemCard, "refresh_thumbnail_async", new_callable=AsyncMock) as mock_refresh_thumbnail:

            paths = list(self.test_thumbnail_dict)
            model = self._build_test_model(paths)
            under_test = FileBrowserGridViewDelegate(ui.Frame(), "NvidiaDark", testing=True)
            under_test.build_grid(model)
            under_test.update_grid(model)
            await omni.kit.app.get_app().next_update_async()

            # Confirm that cards with existing thumbnails redraw themselves
            self.assertEqual(mock_refresh_thumbnail.call_count, len(paths))
            under_test.destroy()

    async def test_thumbnails_not_found(self):
        """Testing FileBrowserGridViewDelegate.update_grid correctly handles no thumbnails"""
        with patch.object(FileBrowserItem, "get_custom_thumbnails_for_folder_async", side_effect=self._mock_get_folder_thumbnails_empty),\
            patch.object(FileBrowserItemCard, "refresh_thumbnail_async", new_callable=AsyncMock) as mock_refresh_thumbnail:

            paths = list(self.test_thumbnail_dict)
            model = self._build_test_model(paths)
            under_test = FileBrowserGridViewDelegate(ui.Frame(), "NvidiaDark", testing=True)
            under_test.build_grid(model)
            under_test.update_grid(model)
            await omni.kit.app.get_app().next_update_async()

            # Confirm that no matching thumbnails were found
            mock_refresh_thumbnail.assert_not_called()
            under_test.destroy()

    async def test_update_cards_on_thumbnails_generated(self):
        """Testing FileBrowserGridViewDelegate.update_cards_on_thumbnails_generated correctly handles new thumbnails"""
        with patch.object(FileBrowserItem, "get_custom_thumbnails_for_folder_async", side_effect=self._mock_get_folder_thumbnails_empty),\
            patch.object(FileBrowserItemCard, "refresh_thumbnail_async", new_callable=AsyncMock) as mock_refresh_thumbnail,\
            patch("omni.kit.widget.filebrowser.grid_view.find_thumbnails_for_files_async", side_effect=self._mock_find_thumbnails_impl):

            paths = list(self.test_thumbnail_dict)
            model = self._build_test_model(paths)
            under_test = FileBrowserGridViewDelegate(ui.Frame(), "NvidiaDark", testing=True)
            under_test.build_grid(model)
            under_test.update_grid(model)
            await omni.kit.app.get_app().next_update_async()

            # Listen for connection error events
            omni.kit.app.queue_event(THUMBNAILS_GENERATED_GLOBAL_EVENT, {"paths": [paths[0]]})
            for _ in range(2):
                await omni.kit.app.get_app().next_update_async()
            mock_refresh_thumbnail.assert_called_with(self.test_thumbnail_dict.get(paths[0]))

            omni.kit.app.queue_event(THUMBNAILS_GENERATED_GLOBAL_EVENT, {"paths": [paths[1]]})
            for _ in range(2):
                await omni.kit.app.get_app().next_update_async()
            mock_refresh_thumbnail.assert_called_with(self.test_thumbnail_dict.get(paths[1]))
            under_test.destroy()

class TestFindThumbnailsForFiles(omni.kit.test.AsyncTestCase):
    """Testing find_thumbnails_for_files_async api func"""
    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def test_find_thumbnails_succeeds(self):
        """Testing find_thumbnails_for_files_async returns expected thumbnails in dict"""
        async def mock_stat_async_impl(path: str):
            return omni.client.Result.OK, None

        with patch("omni.client.stat_async", side_effect=mock_stat_async_impl):
            test_urls = ["omniverse://ov-foo/foo.usd", "omniverse://ov-bar/bar.usd", "omniverse://ov-baz/baz.usd" ]
            results = await find_thumbnails_for_files_async(test_urls)

            # Confirm thumbnail files found
            self.assertEqual(len(test_urls), len(results))
            for url, thumbnail_url in results.items():
                parent_dir = os.path.dirname(url)
                filename = os.path.basename(url)
                expected = f"{parent_dir}/.thumbs/256x256/{filename}.png"
                self.assertEqual(thumbnail_url, expected)

    async def test_find_thumbnails_returns_auto_files(self):
        """Testing find_thumbnails_for_files_async returns auto thumbnails when those are available"""
        async def mock_stat_async_auto(path: str):
            return (omni.client.Result.OK, None) if ".auto." in path else (omni.client.Result.ERROR_NOT_FOUND, None)

        with patch("omni.client.stat_async", side_effect=mock_stat_async_auto):
            test_urls = ["omniverse://ov-foo/foo.usd", "omniverse://ov-bar/bar.usd", "omniverse://ov-baz/baz.usd" ]
            results = await find_thumbnails_for_files_async(test_urls)
            # Confirm thumbnail files found
            self.assertEqual(len(test_urls), len(results))
            for url, thumbnail_url in results.items():
                parent_dir = os.path.dirname(url)
                filename = os.path.basename(url)
                expected = f"{parent_dir}/.thumbs/256x256/{filename}.auto.png"
                self.assertEqual(thumbnail_url, expected)

    async def test_find_thumbnails_generates_missing_when_not_found(self):
        """Testing find_thumbnails_for_files_async submits missing thumbnails for generation"""
        async def mock_stat_async_not_found(path: str):
            return omni.client.Result.ERROR_NOT_FOUND, None

        with patch("omni.client.stat_async", side_effect=mock_stat_async_not_found):
            test_image_urls = ["omniverse://ov-foo/foo.png", "omniverse://ov-baz/baz.jpg"]
            test_urls = test_image_urls + ["omniverse://ov-bar/bar.usd"]

            mock_sub_callback = Mock()
            event_stream_sub = eventdispatcher.get_eventdispatcher().observe_event(event_name=MISSING_IMAGE_THUMBNAILS_GLOBAL_EVENT, on_event=mock_sub_callback)
            results = await find_thumbnails_for_files_async(test_urls)

            # Check that subscription callback was triggered, and that only image files are submitted for
            # thumbnail generation.
            self.assertEqual(len(results), 0)
            await omni.kit.app.get_app().next_update_async()
            mock_sub_callback.assert_called_once()
            event = mock_sub_callback.call_args[0][0]
            self.assertTrue(event["urls"] == test_image_urls)

            # Call again with additional inputs
            test_more_image_urls = ["omniverse://ov-cow/cow.tif"]
            test_urls += test_more_image_urls
            mock_sub_callback.reset_mock()
            results = await find_thumbnails_for_files_async(test_urls)

            # This time, assert that only the new files are submitted for thumbnail generation.  I.e. we don't
            # want the same files to be submitted more than once.
            self.assertEqual(len(results), 0)
            await omni.kit.app.get_app().next_update_async()
            mock_sub_callback.assert_called_once()
            event = mock_sub_callback.call_args[0][0]
            self.assertTrue(event["urls"] == test_more_image_urls)


class TestListThumbnailsForFolder(omni.kit.test.AsyncTestCase):
    """Testing list_thumbnails_for_folder_async api func"""
    async def setUp(self):
        self.test_folder = "omniverse://ov-test/folder"
        self.test_files = ["foo.usd", "bar.jpg", "baz.png" ]
        self.test_urls = [f"{self.test_folder}/{f}" for f in self.test_files]
        self.test_thumbnails = [f"{self.test_folder}/.thumbs/256x256/{f}.png" for f in self.test_files]
        self.test_auto_thumbnails = [f"{self.test_folder}/.thumbs/256x256/{f}.auto.png" for f in self.test_files]

    async def tearDown(self):
        pass

    class MockStats:
        def __init__(self, is_folder: bool = False):
            self.flags = 0
            if is_folder:
                self.flags |= omni.client.ItemFlags.CAN_HAVE_CHILDREN

    class MockListEntry:
        def __init__(self, url: str):
            self.relative_path = os.path.basename(url)

    async def _mock_stat_async_impl(self, url: str):
        if os.path.basename(url) == "folder":
            return omni.client.Result.OK, self.MockStats(is_folder=True)
        return omni.client.Result.OK, self.MockStats(is_folder=False)

    async def _mock_list_async_impl(self, url: str):
        if url.endswith(".thumbs/256x256"):
                return omni.client.Result.OK, [self.MockListEntry(url) for url in self.test_thumbnails]
        else:
            return omni.client.Result.OK, [self.MockListEntry(url) for url in self.test_urls]

    async def _mock_list_async_impl_auto(self, url: str):
        if url.endswith(".thumbs/256x256"):
                return omni.client.Result.OK, [self.MockListEntry(url) for url in self.test_auto_thumbnails]
        else:
            return omni.client.Result.OK, [self.MockListEntry(url) for url in self.test_urls]

    async def _mock_list_async_timeout(self, url: str):
        raise asyncio.TimeoutError

    async def test_list_thumbnails_succeeds(self):
        """Testing list_thumbnails_for_folder_async returns expected thumbnails in dict"""
        with patch("omni.client.stat_async", side_effect=self._mock_stat_async_impl),\
            patch("omni.client.list_async", side_effect=self._mock_list_async_impl):
            results = await list_thumbnails_for_folder_async(self.test_folder)
            # Confirm thumbnail files found
            self.assertEqual(len(self.test_urls), len(results))
            for url, thumbnail_url in results.items():
                parent_dir = os.path.dirname(url)
                filename = os.path.basename(url)
                expected = f"{parent_dir}/.thumbs/256x256/{filename}.png"
                self.assertEqual(thumbnail_url, expected)

    async def test_list_thumbnails_auto(self):
        """Testing list_thumbnails_for_folder_async returns auto thumbnails in dict"""
        with patch("omni.client.stat_async", side_effect=self._mock_stat_async_impl),\
            patch("omni.client.list_async", side_effect=self._mock_list_async_impl_auto):
            results = await list_thumbnails_for_folder_async(self.test_folder)
            # Confirm auto thumbnail files found
            self.assertEqual(len(self.test_urls), len(results))
            for url, thumbnail_url in results.items():
                parent_dir = os.path.dirname(url)
                filename = os.path.basename(url)
                expected = f"{parent_dir}/.thumbs/256x256/{filename}.auto.png"
                self.assertEqual(thumbnail_url, expected)

    async def test_list_thumbnails_auto_precedence(self):
        """Testing that when list_thumbnails_for_folder_async returns multiple thumbnails, the non-auto one takes precedence"""
        test_file = "foo.usd"
        test_url = f"{self.test_folder}/{test_file}"

        async def mock_list_async_impl(url: str):
            if url.endswith(".thumbs/256x256"):
                thumbnail_folder = f"{self.test_folder}/.thumbs/256x256"
                # Return both auto and non-auto thumbnails
                return omni.client.Result.OK, [self.MockListEntry(f"{thumbnail_folder}/{test_file}.auto.png"), self.MockListEntry(f"{thumbnail_folder}/{test_file}.png")]
            else:
                return omni.client.Result.OK, [self.MockListEntry(test_url)]

        with patch("omni.client.stat_async", side_effect=self._mock_stat_async_impl),\
            patch("omni.client.list_async", side_effect=mock_list_async_impl):
            results = await list_thumbnails_for_folder_async(self.test_folder)
            # Confirm non-auto thumbnail precedes auto thumbnail
            expected = f"{self.test_folder}/.thumbs/256x256/{test_file}.png"
            self.assertEqual(results.get(test_url), expected)

    async def test_get_thumbnails_timeout(self):
        """Testing list_thumbnails_for_folder_async times out"""
        with patch("omni.client.stat_async", side_effect=self._mock_stat_async_impl),\
            patch("omni.client.list_async", side_effect=self._mock_list_async_timeout):
            results = await list_thumbnails_for_folder_async(self.test_folder)
            self.assertEqual(results, {})

    async def test_get_thumbnails_generates_missing_when_not_found(self):
        """Testing list_thumbnails_for_folder_async submits missing thumbnails for generation"""
        test_image_files = ["bar.jpg", "baz.png" ]
        test_image_urls = [f"{self.test_folder}/{f}" for f in test_image_files]
        test_urls = test_image_urls + [f"{self.test_folder}/foo.usd"]

        async def mock_list_async_impl(url: str):
            if url.endswith(".thumbs/256x256"):
                # Thumbnails not found
                return omni.client.Result.OK, []
            else:
                return omni.client.Result.OK, [self.MockListEntry(url) for url in test_urls]

        with patch("omni.client.stat_async", side_effect=self._mock_stat_async_impl),\
            patch("omni.client.list_async", side_effect=mock_list_async_impl):

            mock_sub_callback = Mock()
            event_stream_sub = eventdispatcher.get_eventdispatcher().observe_event(event_name=MISSING_IMAGE_THUMBNAILS_GLOBAL_EVENT, on_event=mock_sub_callback)
            results = await list_thumbnails_for_folder_async(self.test_folder)

            # Check that subscription callback was triggered, and that only image files are submitted for
            # thumbnail generation.
            self.assertEqual(len(results), 0)
            await omni.kit.app.get_app().next_update_async()
            mock_sub_callback.assert_called_once()
            event = mock_sub_callback.call_args[0][0]
            self.assertEqual(event["urls"], test_image_urls)

            # Call again with additional inputs
            test_more_image_urls = [f"{self.test_folder}/cow.tif"]
            test_urls += test_more_image_urls
            mock_sub_callback.reset_mock()
            results = await list_thumbnails_for_folder_async(self.test_folder)

            # This time, assert that only the new files are submitted for thumbnail generation.  I.e. we don't
            # want the same files to be submitted more than once.
            self.assertEqual(len(results), 0)
            await omni.kit.app.get_app().next_update_async()
            mock_sub_callback.assert_called_once()
            event = mock_sub_callback.call_args[0][0]
            self.assertTrue(event["urls"] == test_more_image_urls)
