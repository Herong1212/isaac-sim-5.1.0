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
import omni.kit.app

from unittest.mock import Mock, patch, ANY
from .. import get_content_window
from omni.kit import ui_test
from omni.kit.test_suite.helpers import open_stage, get_test_data_path
from omni.kit.helper.file_utils import FILE_OPENED_GLOBAL_EVENT
from omni.kit.widget.filebrowser import is_clipboard_cut, get_clipboard_items, clear_clipboard


class MockItem:
    def __init__(self, path: str):
        self.name = path
        self.path = path
        self.writeable = True
        self.is_folder = True
        self.is_deleted = False

class TestContentBrowser(omni.kit.test.AsyncTestCase):
    """
    Testing omni.kit.window.content_browser extension.  NOTE that since the dialog is a singleton, we use an async
    lock to ensure that only one test runs at a time.  In practice, this is not a issue since there's only one instance
    in the app.
    """
    __lock = asyncio.Lock()

    async def setUp(self):
        pass

    async def wait_for_update(self, wait_frames=20):
        for _ in range(wait_frames):
            await omni.kit.app.get_app().next_update_async()

    async def tearDown(self):
        pass

    async def test_set_search_delegate(self):
        """Testing that hiding the window destroys it"""
        mock_search_delegate = Mock()
        async with self.__lock:
            under_test = get_content_window()
            await self.wait_for_update()
            under_test.set_search_delegate(mock_search_delegate)
            under_test.unset_search_delegate(mock_search_delegate)
        mock_search_delegate.build_ui.assert_called_once()

    async def test_open_event(self):
        """Testing that on open event should auto navigate"""
        under_test = get_content_window()
        omni.kit.app.queue_event(FILE_OPENED_GLOBAL_EVENT, {"url": get_test_data_path(__name__, "bound_shapes.usda")})
        with patch.object(under_test, "navigate_to") as mock:
            await ui_test.human_delay(50)
            mock.assert_called_once()
        omni.kit.app.queue_event(FILE_OPENED_GLOBAL_EVENT, {"url": get_test_data_path(__name__, "bound_shapes.usda")})

    async def test_interface(self):
        """Testing all simple interface"""
        under_test = get_content_window()
        under_test.set_current_directory("omniverse:/")
        self.assertEqual(under_test.get_current_directory(), "omniverse:/")
        self.assertEqual(under_test.get_current_selections(), [])
        under_test.show_model(None)
        def dummy(*args, **kwargs):
            pass

        under_test.subscribe_selection_changed(dummy)
        under_test.unsubscribe_selection_changed(dummy)
        under_test.delete_context_menu("test")
        under_test.toggle_bookmark_from_path("", "omniverse:/", False)
        under_test.add_checkpoint_menu("test", "", None, None)
        under_test.delete_checkpoint_menu("test")
        under_test.add_listview_menu("test", "", None, None)
        under_test.delete_listview_menu("test")
        under_test.add_import_menu("test", "", None, None)
        under_test.delete_import_menu("test")
        self.assertEqual(under_test.get_file_open_handler("test"), None)
        under_test.add_file_open_handler("test", dummy, None)
        under_test.delete_file_open_handler("test")
        self.assertIsNotNone(under_test.api)
        self.assertIsNotNone(under_test.get_checkpoint_widget())
        self.assertIsNone(under_test.get_timestamp_widget())

    async def test_api(self):
        """Testing rest api interface"""
        api = get_content_window().api
        self.assertIsNotNone(api)
        api._post_warning("test")
        def dummy(*args, **kwargs):
            pass
        api.subscribe_selection_changed(dummy)
        api._notify_selection_subs(2, [])
        mock_item_list = [MockItem(str(i)) for i in range(10)]
        with patch.object(api.view, "get_selections", return_value=mock_item_list) as mock:
            api.copy_selected_items()
            mock.assert_called_once()
            self.assertFalse(is_clipboard_cut())
            mock.reset_mock()
            api.cut_selected_items()
            self.assertEqual(get_clipboard_items(), mock_item_list)
            mock.assert_called_once()

        with patch.object(api.view, "get_selections", return_value=mock_item_list) as mock:
            api.delete_selected_items()
            mock.assert_called_once()

        mock_item_list1 = [MockItem("test")]
        with patch("omni.kit.widget.filebrowser.get_clipboard_items", return_value=mock_item_list) as mock, \
                patch.object(api.view, "get_selections", return_value=mock_item_list1) as mock2:
            api.paste_items()
            api.clear_clipboard()
            mock2.assert_called_once()
