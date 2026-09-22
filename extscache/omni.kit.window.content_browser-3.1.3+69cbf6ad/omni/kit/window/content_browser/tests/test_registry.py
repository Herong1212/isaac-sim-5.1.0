## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
from unittest.mock import patch, Mock
from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit import ui_test
from ..api import ContentBrowserAPI
from .. import get_instance


class TestRegistry(AsyncTestCase):
    """Testing Content Browser Registry"""
    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def test_custom_menus(self):
        """Test persisting custom menus"""
        test_menus = {
            "context": {
                "name": "my context menu",
                "glyph": "my glyph",
                "click_fn": Mock(),
                "show_fn": Mock(),
            },
            "listview": {
                "name": "my listview menu",
                "glyph": "my glyph",
                "click_fn": Mock(),
                "show_fn": Mock(),
            },
            "import": {
                "name": "my import menu",
                "glyph": None,
                "click_fn": Mock(),
                "show_fn": Mock(),
            },
            "file_open": {
                "context": "file_open",
                "name": "my file_open handler",
                "glyph": None,
                "click_fn": Mock(),
                "show_fn": Mock(),
            }
        }
        # Register menus
        under_test = get_instance()
        for context, test_menu in test_menus.items():
            if context == "context":
                under_test.add_context_menu(test_menu["name"], test_menu["glyph"], test_menu["click_fn"], test_menu["show_fn"])
            elif context == "listview":
                under_test.add_listview_menu(test_menu["name"], test_menu["glyph"], test_menu["click_fn"], test_menu["show_fn"])
            elif context == "import":
                under_test.add_import_menu(test_menu["name"], test_menu["glyph"], test_menu["click_fn"], test_menu["show_fn"])
            elif context == "file_open":
                under_test.add_file_open_handler(test_menu["name"], test_menu["click_fn"], test_menu["show_fn"])
            elif context == "checkpoint":
                under_test.add_file_open_handler(test_menu["name"], test_menu["click_fn"], test_menu["show_fn"])
            else:
                pass

        with patch.object(ContentBrowserAPI, "add_context_menu") as mock_add_context_menu,\
            patch.object(ContentBrowserAPI, "add_listview_menu") as mock_add_listview_menu,\
            patch.object(ContentBrowserAPI, "add_import_menu") as mock_add_import_menu,\
            patch.object(ContentBrowserAPI, "add_checkpoint_menu") as mock_add_checkpoint_menu,\
            patch.object(ContentBrowserAPI, "add_file_open_handler") as mock_add_file_open_handler:
            # Hide then show window again
            under_test.show_window(None, False)
            await ui_test.human_delay(4)
            under_test.show_window(None, True)
            await ui_test.human_delay(4)

        # Confirm all mocks got called with appropriate inputs
        for context, test_menu in test_menus.items():
            if context == "context":
                mock_add_context_menu.assert_called_with(test_menu["name"], test_menu["glyph"], test_menu["click_fn"], test_menu["show_fn"], 0)
            elif context == "listview":
                mock_add_listview_menu.assert_called_with(test_menu["name"], test_menu["glyph"], test_menu["click_fn"], test_menu["show_fn"], -1)
            elif context == "import":
                mock_add_import_menu.assert_called_with(test_menu["name"], test_menu["glyph"], test_menu["click_fn"], test_menu["show_fn"])
            elif context == "file_open":
                mock_add_file_open_handler.assert_called_with(test_menu["name"], test_menu["click_fn"], test_menu["show_fn"])
            elif context == "checkpoint":
                mock_add_checkpoint_menu.assert_called_with(test_menu["name"], test_menu["click_fn"], test_menu["show_fn"])
            else:
                pass

    async def test_selection_handlers(self):
        """Test persisting selection handlers"""
        test_handler_1 = Mock()
        test_handler_2 = Mock()
        test_handlers = [test_handler_1, test_handler_2, test_handler_1]

        under_test = get_instance()
        for test_handler in test_handlers:
            under_test.subscribe_selection_changed(test_handler)

        with patch.object(ContentBrowserAPI, "subscribe_selection_changed") as mock_subscribe_selection_changed:
            # Hide then show window again
            under_test.show_window(None, False)
            await ui_test.human_delay(4)
            under_test.show_window(None, True)
            await ui_test.human_delay(4)

        self.assertEqual(mock_subscribe_selection_changed.call_count, 2)

    async def test_search_delegate(self):
        """Test persisting search delegate"""
        test_search_delegate = Mock()

        under_test = get_instance()
        under_test.set_search_delegate(test_search_delegate)

        # Confirm search delegate restored from registry
        with patch.object(ContentBrowserAPI, "set_search_delegate") as mock_set_search_delegate:
            # Hide then show window again
            under_test.show_window(None, False)
            await ui_test.human_delay(4)
            under_test.show_window(None, True)
            await ui_test.human_delay(4)

        mock_set_search_delegate.assert_called_with(test_search_delegate)
