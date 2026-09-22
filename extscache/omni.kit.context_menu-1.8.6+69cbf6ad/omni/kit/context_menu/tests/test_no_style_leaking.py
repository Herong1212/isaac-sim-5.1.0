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
from omni.kit.test_suite.helpers import wait_stage_loading, arrange_windows
from pxr import Kind, Sdf, Gf
import pathlib


class TestContextMenuNoStyleLeakage(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        await arrange_windows()
        await omni.usd.get_context().new_stage_async()
        stage = omni.usd.get_context().get_stage()
        stage.SetDefaultPrim(stage.DefinePrim("/World"))

        from omni.kit.context_menu.scripts.context_menu import TEST_DATA_PATH
        self._golden_img_dir = TEST_DATA_PATH.absolute().joinpath("golden_img").absolute()
        self._usd_path = TEST_DATA_PATH.absolute().joinpath("usd").absolute()

    # After running each test
    async def tearDown(self):
        await super().tearDown()

    # Test(s)
    async def test_no_style_leaking(self):
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

        await wait_stage_loading()
        await ui_test.find("Stage").focus()
        viewport = ui_test.find("Viewport")
        await viewport.focus()

        # show viewport context menu
        await viewport.right_click()
        await ui_test.human_delay(10)

        # without closing context menu open new one & check for style leaking
        window = await self.create_test_window(width=200, height=330)
        context_menu = omni.kit.context_menu.get_instance()
        context_menu.show_context_menu("toolbar", {"menu_xpos": 4, "menu_ypos": 4}, menu_list)

        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="test_context_menu_style_leak_ui.png")
