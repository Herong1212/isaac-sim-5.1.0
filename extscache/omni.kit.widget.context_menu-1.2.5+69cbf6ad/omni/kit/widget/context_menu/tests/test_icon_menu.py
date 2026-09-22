## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.app
import omni.kit.test
import omni.ui as ui
from omni.ui.tests.test_base import OmniUiTest
from omni.kit import ui_test
from pathlib import Path


class TestIconMenu(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()

        extension_path = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
        test_data_path = Path(extension_path).joinpath("data").joinpath("tests")

        self._golden_img_dir = test_data_path.absolute().joinpath("golden_img").absolute()

    # After running each test
    async def tearDown(self):
        await super().tearDown()

    # Test(s)
    async def test_icon_menu(self):
        def stub_fn():
            pass # pragma: no cover

        def show_stub_false(objects):
            return False # pragma: no cover

        # setup menu
        icon_path = str(Path(omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)).joinpath("data/tests/icons/button.svg"))
        menu_list = [
            {
                "name": "Set Authoring Layer",
                "glyph": icon_path,
                "onclick_fn": stub_fn,
            },
            {"name": ""},
            {
                "name": "Create Sublayer",
                "glyph": icon_path,
                "onclick_fn": stub_fn,
            },
            {
                "name": "Insert Sublayer",
                "glyph": icon_path,
                "onclick_fn": stub_fn,
            },
            {
                "name": "Merge Down One",
                "glyph": icon_path,
                "onclick_fn": stub_fn,
            },
            {
                "name": "Flatten Sublayers",
                "glyph": icon_path,
                "onclick_fn": stub_fn,
            },
            {"name": ""},
            {
                "name": "Save",
                "glyph": icon_path,
                "onclick_fn": stub_fn,
            },
            {
                "name": "Save As",
                "glyph": icon_path,
                "onclick_fn": stub_fn,
            },
            {
                "name": "Save As And Replace",
                "glyph": icon_path,
                "onclick_fn": stub_fn,
            },
            {"name": ""},
            {
                "name": "Reload Layer",
                "glyph": icon_path,
                "onclick_fn": stub_fn,
            },
            {
                "name": "Remove Layer",
                "glyph": icon_path,
                "onclick_fn": stub_fn,
            },
            {
                "name": "Delete Prim",
                "glyph": icon_path,
                "onclick_fn": stub_fn,
            },
            {"name": ""},
            {
                "name": "Select Bound Objects",
                "glyph": icon_path,
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

        window = await self.create_test_window(width=200, height=330)
        await ui_test.human_delay(10)
        context_menu = omni.kit.widget.context_menu.get_instance()
        context_menu.show_context_menu("toolbar", {"menu_xpos": 4, "menu_ypos": 4}, menu_list)
        await ui_test.human_delay(10)
        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="test_icon_menu_ui.png")
