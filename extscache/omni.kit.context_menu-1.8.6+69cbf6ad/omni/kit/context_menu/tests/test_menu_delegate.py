## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.app
import omni.kit.commands
import omni.kit.test
from omni.ui.tests.test_base import OmniUiTest
import omni.ui as ui
from omni.kit import ui_test
from pxr import Kind, Sdf, Gf
import pathlib


class TestContextMenuDelegate(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()

    # After running each test
    async def tearDown(self):
        await super().tearDown()

    # Test(s)
    async def test_delegate_context_menu(self):
        from omni.kit.context_menu import ContextMenuExtension

        def stub_fn():
            pass

        def show_stub_false(objects):
            return False

        # setup menu
        menu_list = [
            {
                "name": "Set Authoring Layer",
                "glyph": "menu_rename.svg",
                "onclick_fn": stub_fn,
            },
            {"name": ""},
            {
                "name": "Create Sublayer",
                "glyph": "menu_create_sublayer.svg",
                "onclick_fn": stub_fn,
            },
            {
                "name": "Insert Sublayer",
                "glyph": "menu_insert_sublayer.svg",
                "onclick_fn": stub_fn,
            },
            {
                "name": "Merge Down One",
                "glyph": "menu_merge_down.svg",
                "onclick_fn": stub_fn,
            },
            {
                "name": "Flatten Sublayers",
                "glyph": "menu_flatten_layers.svg",
                "onclick_fn": stub_fn,
            },
            {"name": ""},
            {
                "name": "Save",
                "glyph": "menu_save.svg",
                "onclick_fn": stub_fn,
            },
            {
                "name": "Save As",
                "glyph": "menu_save_as.svg",
                "onclick_fn": stub_fn,
            },
            {
                "name": "Save As And Replace",
                "glyph": "menu_save_as.svg",
                "onclick_fn": stub_fn,
            },
            {"name": ""},
            {
                "name": "Reload Layer",
                "glyph": "menu_refresh.svg",
                "onclick_fn": stub_fn,
            },
            {
                "name": "Remove Layer",
                "glyph": "menu_remove_layer.svg",
                "onclick_fn": stub_fn,
            },
            {
                "name": "Delete Prim",
                "glyph": "menu_delete.svg",
                "onclick_fn": stub_fn,
            },
            {"name": ""},
            {
                "name": "Select Bound Objects",
                "glyph": "menu_search.svg",
                "onclick_fn": stub_fn,
            },
            {"name": ""},
            {"glyph": "menu_link.svg", "name": {
                  'SubMenu':
                    [
                        {'name': 'Set up axis +Y', 'onclick_fn': stub_fn},
                        {'name': 'Set up axis +Z', 'onclick_fn': stub_fn}
                    ]
                },
            },
            {"glyph": "none.svg", "name": {
                  'SubMenu Hidden':
                    [
                        {'name': 'Set up axis +Y', "show_fn": show_stub_false, 'onclick_fn': stub_fn},
                        {'name': 'Set up axis +Z', "show_fn": show_stub_false, 'onclick_fn': stub_fn}
                    ]
              }
            },
        ]

        delegate_calls = {"init": 0, "build_item": 0, "build_status": 0, "build_title": 0, "get_style": 0, "get_parameters": 0}

        class MenuDelegate(ContextMenuExtension.DefaultMenuDelegate):
            def __init__(self, **kwargs):
                nonlocal delegate_calls
                super().__init__(**kwargs)
                delegate_calls["init"] += 1

            def build_item(self, item: ui.MenuHelper):
                nonlocal delegate_calls
                super().build_item(item)
                delegate_calls["build_item"] += 1

            def build_status(self, item: ui.MenuHelper):
                nonlocal delegate_calls
                super().build_status(item)
                delegate_calls["build_status"] += 1

            def build_title(self, item: ui.MenuHelper):
                nonlocal delegate_calls
                super().build_title(item)
                delegate_calls["build_title"] += 1

            def get_style(self):
                nonlocal delegate_calls
                delegate_calls["get_style"] += 1
                return {}

            def get_parameters(self, name, kwargs):
                nonlocal delegate_calls
                delegate_calls["get_parameters"] += 1

        await ui_test.human_delay(50)

        menu_delegate = MenuDelegate()
        window = await self.create_test_window(width=200, height=330)
        context_menu = omni.kit.context_menu.get_instance()
        context_menu.show_context_menu("delegate", {"menu_xpos": 4, "menu_ypos": 4}, menu_list, delegate=menu_delegate)

        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test_no_image()
        await ui_test.human_delay(50)

        self.assertEqual(delegate_calls, {'init': 1, 'build_item': 21, 'build_status': 2, 'build_title': 2, 'get_style': 17, 'get_parameters': 17})
