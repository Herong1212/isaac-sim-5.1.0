## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
from pathlib import Path
import omni.kit.app
import omni.kit.test
from omni.ui.tests.test_base import OmniUiTest
from omni.kit import ui_test
from omni.kit.test_suite.helpers import wait_stage_loading, arrange_windows

class TestContextMenuDelegateStyle(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        await arrange_windows()

        extension_path = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
        test_data_path = Path(extension_path).joinpath("data").joinpath("tests")
        self._golden_img_dir = test_data_path.absolute().joinpath("golden_img").absolute()

    async def test_context_menu_style_leaks(self):
        from omni.kit.widget.context_menu import ContextMenuWidgetExtension
        from omni.ui.tests.compare_utils import CompareMetric

        def stub_fn():
            pass # pragma: no cover

        def show_stub_false(objects):
            return False # pragma: no cover

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
                "appear_after": "Save",
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

        class MenuDelegate(ContextMenuWidgetExtension.DefaultMenuDelegate):
            TEXT_SIZE = 14
            ICON_SIZE = 14
            MARGIN_SIZE = [3, 3]

            def get_style(self):
                from omni.kit.widget.context_menu import style

                vp_style = style.MENU_STYLE.copy()
                vp_style["Label::Enabled"] = {"margin_width": self.MARGIN_SIZE[0],"margin_height": self.MARGIN_SIZE[1],"color": self.COLOR_LABEL_ENABLED}
                vp_style["Label::Disabled"] = {"margin_width": self.MARGIN_SIZE[0], "margin_height": self.MARGIN_SIZE[1], "color": self.COLOR_LABEL_DISABLED}

                return vp_style

            def get_parameters(self, name, kwargs):
                kwargs["tearable"] = False

        window = await self.create_test_window(width=200, height=320)
        await ui_test.human_delay(10)
        context_menu = omni.kit.widget.context_menu.get_instance()
        omni.kit.widget.context_menu.reorder_menu_dict(menu_list)
        context_menu.show_context_menu("viewport", {"menu_xpos": 4, "menu_ypos": 4}, menu_list, delegate=MenuDelegate())

        await ui_test.human_delay(10)
        await wait_stage_loading()

        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="test_context_menu_style_ui.png", cmp_metric=CompareMetric.MEAN_ERROR_SQUARED)
        await ui_test.human_delay(50)

    async def test_context_menu_close_menu(self):
        from omni.kit.widget.context_menu import ContextMenuWidgetExtension
        from omni.ui.tests.compare_utils import CompareMetric

        def stub_fn():
            pass # pragma: no cover

        def show_stub_false(objects):
            return False # pragma: no cover

        def populate_stub(objects: dict):
            pass # pragma: no cover

        async def async_stub(objects: dict, menu_item):
            pass # pragma: no cover

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
                "appear_after": "Save",
            },
            {
                "name": "Delete Prim",
                "glyph": "menu_delete.svg",
                "onclick_fn": stub_fn,
                "appear_after": "Save",
            },
            {"name": ""},
            {
                "name": "Select Bound Objects",
                "glyph": "menu_search.svg",
                "onclick_action": ("omni.kit.widget.stage", "my_hovercraft_is_full_of_eels"),
            },
            {"name": ""},
            {"name": ""},
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
            {"populate_fn": populate_stub},
            {"name": "Test async", "show_fn_async": async_stub},
            {"name": ""},
            {"name": ""},
            {"name": ""},
        ]

        context_menu = omni.kit.widget.context_menu.get_instance()
        context_menu.show_context_menu("viewport", {"menu_xpos": 4, "menu_ypos": 4}, menu_list)
        await ui_test.human_delay(10)

        self.assertTrue(context_menu.get_context_menu())
        self.assertEqual(context_menu.name, "Context menu viewport")
        omni.kit.widget.context_menu.close_menu()
        self.assertFalse(context_menu.get_context_menu())
        self.assertEqual(context_menu.name, None)

        event_stream = omni.kit.widget.context_menu.get_menu_event_stream()
