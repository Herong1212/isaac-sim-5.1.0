## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
import inspect
import omni.kit.window.content_browser_registry as registry

from unittest.mock import Mock
from omni.kit.test.async_unittest import AsyncTestCase


class TestRegistry(AsyncTestCase):
    """Testing Content Browser Registry"""
    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def test_custom_menus(self):
        """Test registering and de-registering custom menus"""
        test_menus = [
            {
                "register_fn": registry.register_context_menu,
                "deregister_fn": registry.deregister_context_menu,
                "context": "context",
                "name": "my context menu",
                "glyph": "my glyph",
                "click_fn": Mock(),
                "show_fn": Mock(),
            },
            {
                "register_fn": registry.register_listview_menu,
                "deregister_fn": registry.deregister_listview_menu,
                "context": "listview",
                "name": "my listview menu",
                "glyph": "my glyph",
                "click_fn": Mock(),
                "show_fn": Mock(),
            },
            {
                "register_fn": registry.register_import_menu,
                "deregister_fn": registry.deregister_import_menu,
                "context": "import",
                "name": "my import menu",
                "glyph": None,
                "click_fn": Mock(),
                "show_fn": Mock(),
            },
            {
                "register_fn": registry.register_file_open_handler,
                "deregister_fn": registry.deregister_file_open_handler,
                "context": "file_open",
                "name": "my file_open handler",
                "glyph": None,
                "click_fn": Mock(),
                "show_fn": Mock(),
            }
        ]
        # Register menus
        for test_menu in test_menus:
            register_fn = test_menu["register_fn"]
            if 'glyph' in inspect.getfullargspec(register_fn).args:
                register_fn(test_menu["name"], test_menu["glyph"], test_menu["click_fn"], test_menu["show_fn"])
            else:
                register_fn(test_menu["name"], test_menu["click_fn"], test_menu["show_fn"])

        # Confirm menus stored to registry
        for test_menu in test_menus:
            self.assertTrue(f'{test_menu["context"]}::{test_menu["name"]}' in registry.custom_menus())

        # De-register all menus
        for test_menu in test_menus:
            test_menu["deregister_fn"](test_menu["name"])

        # Confirm all menus removed from registry
        self.assertEqual(len(registry.custom_menus()), 0)

    async def test_selection_handlers(self):
        """Test registering selection handlers"""
        test_handler_1 = Mock()
        test_handler_2 = Mock()
        test_handlers = [test_handler_1, test_handler_2, test_handler_1]

        self.assertEqual(len(registry.selection_handlers()), 0)
        for test_handler in test_handlers:
            registry.register_selection_handler(test_handler)
        # Confirm each unique handler is stored only once in registry
        self.assertEqual(len(registry.selection_handlers()), 2)

    async def test_search_delegate(self):
        """Test registering search delegate"""
        test_search_delegate = Mock()

        self.assertEqual(registry.search_delegate(), None)
        registry.register_search_delegate(test_search_delegate)
        # Confirm search delegate stored in registry
        self.assertEqual(registry.search_delegate(), test_search_delegate)
