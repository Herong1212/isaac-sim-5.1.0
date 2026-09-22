## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.app

from unittest.mock import Mock
from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit.helper.file_utils import asset_types
from .. import (
    FILE_OPENED_EVENT, FILE_OPENED_GLOBAL_EVENT, FILE_SAVED_EVENT, FILE_SAVED_GLOBAL_EVENT, FileEventModel,
    get_instance, get_latest_urls_from_event_queue, get_last_url_opened, get_last_url_saved
)


class TestOpenedQueue(AsyncTestCase):
    """Testing Opened Queue"""
    async def setUp(self):
        pass

    async def tearDown(self):
        get_instance().clear_event_queue()

    async def test_get_latest_urls_opened_succeeds(self):
        """Test saving and retrieving url's from the saved queue"""
        test_events = [
            (FILE_OPENED_GLOBAL_EVENT, "omniverse://ov-test/stage.usd", "tag-1"),
            (FILE_OPENED_GLOBAL_EVENT, "omniverse://ov-test/image.jpg", None),
            (FILE_SAVED_GLOBAL_EVENT, "omniverse://ov-baz/folder/", "tag-1"),
            (FILE_SAVED_GLOBAL_EVENT, "omniverse://ov-foo/last_image.png", None),
            (FILE_OPENED_GLOBAL_EVENT, "omniverse://ov-bar/last_material.mdl", "tag-1"),
            (FILE_OPENED_GLOBAL_EVENT, "omniverse://ov-baz/last_url.usd", "tag-2"),
        ]

        under_test = get_instance()
        under_test.clear_event_queue()

        # Add test urls to queue via event stream
        for event_type, url, tag in test_events:
            file_event = FileEventModel(url=url, is_folder=url.endswith('/'), tag=tag)
            omni.kit.app.queue_event(event_type, file_event.dict())

        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()

        self.assertEqual(len(test_events), len(under_test._event_queue))
        self.assertEqual(4, len(get_latest_urls_from_event_queue(num_latest=10, event_type=FILE_OPENED_EVENT)))
        self.assertEqual(4, len(get_latest_urls_from_event_queue(num_latest=10, event_name=FILE_OPENED_GLOBAL_EVENT)))
        self.assertEqual(2, len(get_latest_urls_from_event_queue(num_latest=10, event_type=FILE_SAVED_EVENT)))
        self.assertEqual(2, len(get_latest_urls_from_event_queue(num_latest=10, event_name=FILE_SAVED_GLOBAL_EVENT)))
        self.assertEqual(3, len(get_latest_urls_from_event_queue(num_latest=10, tag="tag-1")))
        self.assertEqual(1, len(get_latest_urls_from_event_queue(num_latest=10, asset_type=asset_types.ASSET_TYPE_USD, tag="tag-1")))

        self.assertTrue("last_url" in get_last_url_opened())
        self.assertTrue("last_material" in get_last_url_opened(asset_type=asset_types.ASSET_TYPE_MATERIAL))
        self.assertTrue("last_image" in get_last_url_saved(asset_type=asset_types.ASSET_TYPE_IMAGE))

        # Confirm queue was properly saved into user settings
        expected = test_events[::-1] # LIFO list matches the order of the event queue
        self._event_queue = under_test._load_queue_from_settings() # Reload queue from settings
        self.assertEqual(len(under_test.event_queue), len(expected))
        for i, entry in enumerate(under_test.event_queue.items()):
            file_event = entry[1]
            test_url = expected[i]
            self.assertEqual(file_event.url, test_url[1])
            self.assertEqual(file_event.tag, test_url[2])
            self.assertEqual(file_event.is_folder, test_url[1].endswith('/'))

