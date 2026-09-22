## Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
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
from unittest.mock import patch
from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit.test_suite.helpers import get_test_data_path
from ..dialog import FilePickerDialog
from .test_utils import time_logger


class MockServer:
    def __init__(self, cache_enabled=False, checkpoints_enabled=False, omniojects_enabled=False, username="", version=""):
        self.cache_enabled = cache_enabled
        self.checkpoints_enabled = checkpoints_enabled
        self.omniojects_enabled = omniojects_enabled
        self.username = username
        self.version = version


class MockFileEntry:
    def __init__(self, relative_path="", access="", flags="", size=0, modified_time="", created_time="", modified_by="", created_by="", version=""):
        self.relative_path = relative_path
        self.access = access
        self.flags = flags
        self.size = size
        self.modified_time = modified_time
        self.created_time = created_time
        self.modified_by = modified_by
        self.created_by = created_by
        self.version = version
        self.comment = "<Test Node>"


@time_logger
class TestTimestamp(AsyncTestCase):
    # Before running each test
    async def setUp(self):
        self._mock_server = MockServer(
            cache_enabled=False,
            checkpoints_enabled=True,
            omniojects_enabled=True,
            username="timestamp_test@nvidia.com",
            version="TestServer"
        )
        self._mock_file_entry_0 = MockFileEntry(
            access=1,
            created_by="git@nvidia.com",
            created_time=datetime.now(),
            flags=513,
            modified_by="timestamp_test@nvidia.com",
            modified_time=datetime.now(),
            relative_path="&FakeCheckpoint",
            size=16070,
            version=12023408
        )
        self._mock_file_entry_1 = MockFileEntry(
            access=2,
            created_by="git@nvidia.com",
            created_time=datetime(2020,1,1,12,30,30),
            flags=513,
            modified_by="timestamp_test@nvidia.com",
            modified_time=datetime(2020,1,1,12,30,30),
            relative_path="&FakeCheckpoint",
            size=5070,
            version=12023409
        )

    # After running each test
    async def tearDown(self):
        pass

    async def _mock_get_server_info_async(self, url: str):
        return omni.client.Result.OK, self._mock_server

    async def _mock_list_checkpoints_async(self, query: str):
        return omni.client.Result.OK, [self._mock_file_entry_1, self._mock_file_entry_0]

    async def test_resolve_timestamp(self):
        with patch("omni.client.get_server_info_async", side_effect=self._mock_get_server_info_async),\
            patch("omni.client.list_checkpoints_async", side_effect=self._mock_list_checkpoints_async):

            test_path = get_test_data_path(__name__, "../icon.png")
            under_test = FilePickerDialog(
                "test_resolve_timestamp",
                current_directory=test_path,
                enable_checkpoints=True,
                enable_timestamp=True,
                show_grid_view=True,
            )

            for _ in range(10):
                await omni.kit.app.get_app().next_update_async()

            # enable the timestamp resolve
            ts_widget = under_test._widget._timestamp_widget
            ts_widget.check = True
            full_path = ts_widget.get_timestamp_url(None)
            self.assertTrue(full_path.find('timestamp'))

            under_test.destroy()
