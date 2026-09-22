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
import omni.client
import tempfile

from unittest.mock import Mock, patch, ANY
from ..dialog import FilePickerDialog
from ..view import FilePickerView
from ..model import FilePickerModel
from ..collections.collection_data import CollectionData
from .test_utils import time_logger


@time_logger
class TestFilePickerDialog(omni.kit.test.AsyncTestCase):
    """Testing FilePickerDialog properly executes API endpoints."""
    async def setUp(self):
        pass

    async def wait_for_update(self, wait_frames=20):
        for _ in range(wait_frames):
            await omni.kit.app.get_app().next_update_async()

    async def tearDown(self):
        pass

    async def test_add_connections_succeeds(self):
        """Testing happy path for adding connections"""
        with patch.object(FilePickerView, "add_server") as mock_add_server:
            # Create the widget and add multiple connections
            under_test = FilePickerDialog("test")
            connections = {"C:": "C:"}

            mock_add_server.reset_mock()
            under_test.add_connections(connections)

            # Check that all specified connections were attempted
            assert mock_add_server.call_count == len(connections.items())
            for name, path in connections.items():
                mock_add_server.assert_any_call(name, path, auto_select=False)
            under_test.destroy()

    async def test_set_search_delegate(self):
        """Testing that hiding the window destroys it"""
        mock_search_delegate = Mock()
        under_test = FilePickerDialog("test")
        await self.wait_for_update()
        under_test.set_search_delegate(mock_search_delegate)
        mock_search_delegate.build_ui.assert_called_once()
        under_test.destroy()

    async def test_set_filename(self):
        with tempfile.TemporaryDirectory() as tmp_dirname:
            under_test = FilePickerDialog("test", current_directory=tmp_dirname)
            for _ in range(6):
                await omni.kit.app.get_app().next_update_async()

            # Confirm current directory
            self.assertEqual(under_test.get_current_directory().rstrip('/'), tmp_dirname.replace('\\', '/'))

            # Set simple filename
            test_filename = "file.usd"
            under_test.set_filename(f"{tmp_dirname}/{test_filename}")
            self.assertEqual(under_test.get_filename(), test_filename)

            # Set filename to full path that descends from current directory
            test_filename = "path/to/test/file.usd"
            under_test.set_filename(f"{tmp_dirname}/{test_filename}")
            self.assertEqual(under_test.get_filename(), test_filename)

            # Set filename to full path that doesn't relate to current directory
            test_filename = "C:/unrelated/path/to/test/file.usd"
            under_test.set_filename(test_filename)
            self.assertEqual(under_test.get_filename(), test_filename)
            under_test.destroy()

    async def test_resilience_to_fast_destruction(self):
        """Testing that the extension is resilient to fast destruction."""
        async def side_effect(*args, **kwargs):
            # fake a long find item period to have the loading pane present on destruction
            import asyncio
            await asyncio.sleep(1)

        async def mock_stat(*args, **kwargs):
            return omni.client.Result.OK, None

        with patch.object(FilePickerModel, "find_item_async", side_effect=side_effect), patch("omni.client.stat_async", side_effect=mock_stat):
            for i in range(5):
                under_test = FilePickerDialog("test")
                under_test.show()
                under_test.navigate_to("dummy/file/path.usd")
                await self.wait_for_update(wait_frames=i)
                under_test.hide()
                await self.wait_for_update(wait_frames=i)
                under_test.destroy()
