## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import carb
from carb.eventdispatcher import get_eventdispatcher, Event
from pathlib import Path
from omni.kit.actions.core import get_action_registry
import omni.kit.app
import omni.kit.test
import omni.ui as ui
from omni.ui.tests.test_base import OmniUiTest
from omni.kit import ui_test

class TestContextMenu(OmniUiTest):
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
    async def test_basic_context_menu(self):

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

        window = await self.create_test_window(width=200, height=330)
        await ui_test.human_delay(10)
        context_menu = omni.kit.widget.context_menu.get_instance()
        omni.kit.widget.context_menu.reorder_menu_dict(menu_list)
        context_menu.show_context_menu("toolbar", {"menu_xpos": 4, "menu_ypos": 4}, menu_list)
        await ui_test.human_delay(10)
        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="test_context_menu_ui.png")

    async def test_add_menu(self):
        def is_stub(objects: dict):
            return False # pragma: no cover

        def menu_stub(objects: dict):
            pass # pragma: no cover

        menu = {
            "name": "Export to MDL",
            "glyph": "menu_save.svg",
            "show_fn": [is_stub],
            "onclick_fn": menu_stub,
            "appear_after": "Save Selected",
        }
        menu_expand = {
            "name": "Expand Graph",
            "glyph": "menu_save.svg",
            "show_fn": [is_stub],
            "onclick_fn": menu_stub,
            "appear_after": "Export to MDL",
        }

        # verify no menus
        self.assertEqual(omni.kit.widget.context_menu.get_menu_dict(), [])

        # add menus
        stage_context_menu_export = omni.kit.widget.context_menu.add_menu(menu)
        stage_context_menu_expand = omni.kit.widget.context_menu.add_menu(menu_expand)

        #verify menus
        self.assertNotEqual(omni.kit.widget.context_menu.get_menu_dict(), [])

        # cleanup
        del stage_context_menu_export
        del stage_context_menu_expand

        # verify no menus
        self.assertEqual(omni.kit.widget.context_menu.get_menu_dict(), [])

    async def test_complex_get_menu_dict(self):
        menus = [ {'name': 'Attribute'},
                  {'name': 'Reference'},
                  {'name': 'Payload'},
                  {'name': {'TransformOp': [{'name': 'Translate, Rotate, Scale'}]}},
                  {'name': {'TransformOp': [{'name': 'Translate, Orient, Scale'}]}},
                  {'name': {'TransformOp': [{'name': 'Transform'}]}},
                  {'name': {'TransformOp': [{'name': 'Pivot'}]}},
                  {'name': {'TransformOp': [{'name': 'Translate'}]}},
                  {'name': {'TransformOp': [{'name': 'Rotate'}]}},
                  {'name': {'TransformOp': [{'name': 'Orient'}]}},
                  {'name': {'TransformOp': [{'name': 'Scale'}]}},
                  {'name': 'Instanceable'},
                  {'name': {'Rendering': [{'name': 'Toggle Wireframe Mode'}]}},
                  {'name': {'Rendering': [{'name': 'Toggle Do Not Cast Shadows'}]}},
                  {'name': {'Rendering': [{'name': 'Toggle Enable Shadow Terminator Fix'}]}},
                  {'name': {'Rendering': [{'name': 'Toggle Enable Fast Refraction Shadow'}]}},
                  {'name': {'Rendering': [{'name': 'Toggle Disable RT SSS Transmission'}]}},
                  {'name': {'Rendering': [{'name': 'Toggle Enable Holdout Object'}]}},
                  {'name': {'Rendering': [{'name': 'Toggle Invisible To Secondary Rays'}]}},
                  {'name': {'Rendering': [{'name': 'Toggle Is Procedural Volume'}]}},
                  {'name': {'Rendering': [{'name': 'Toggle Matte Object'}]}},
                  {'name': {'Rendering': [{'name': 'Toggle Invisible to Primary Ray'}]}},
                  {'name': {'Rendering': [{'name': 'Toggle Is Light'}]}},
                  {'name': {'Rendering': [{'name': 'Toggle Disable Auto Lod'}]}},
                ]
        menu_list = omni.kit.widget.context_menu.merge_menus(menus)
        self.assertEqual(menu_list, [{'name': 'Attribute'}, {'name': 'Reference'}, {'name': 'Payload'}, {'name': {'TransformOp': [{'name': 'Translate, Rotate, Scale'}, {'name': 'Translate, Orient, Scale'}, {'name': 'Transform'}, {'name': 'Pivot'}, {'name': 'Translate'}, {'name': 'Rotate'}, {'name': 'Orient'}, {'name': 'Scale'}]}}, {'name': 'Instanceable'}, {'name': {'Rendering': [{'name': 'Toggle Wireframe Mode'}, {'name': 'Toggle Do Not Cast Shadows'}, {'name': 'Toggle Enable Shadow Terminator Fix'}, {'name': 'Toggle Enable Fast Refraction Shadow'}, {'name': 'Toggle Disable RT SSS Transmission'}, {'name': 'Toggle Enable Holdout Object'}, {'name': 'Toggle Invisible To Secondary Rays'}, {'name': 'Toggle Is Procedural Volume'}, {'name': 'Toggle Matte Object'}, {'name': 'Toggle Invisible to Primary Ray'}, {'name': 'Toggle Is Light'}, {'name': 'Toggle Disable Auto Lod'}]}}])

    async def test_nested_menu_no_warnings(self):
        def add_menu(path):
            parts = path.split("/")
            if len(parts) > 1:
                last_name = parts.pop()
                first_name = parts.pop(0)
                context_root = {"name": {first_name: []}}
                context_item = context_root["name"][first_name]

                while parts:
                    name = parts.pop(0)
                    context_item.append({"name": {name: []}})
                    context_item = context_item[0]["name"][name]

                context_item.append(
                    {
                        "name": last_name
                    }
                )
            else:
                context_root = {"name": path}
            return omni.kit.widget.context_menu.add_menu(context_root)

        a = add_menu("A/B/C/D/E")
        b = add_menu("A/B/C/D/F")

        omni.kit.widget.context_menu.get_menu_dict()

        warning_count = 0

        def on_log_event(e: Event):
            if e["level"] == carb.logging.LEVEL_WARN:
                nonlocal warning_count
                warning_count += 1

        # log event, count number of warnings outputted
        log_sub = get_eventdispatcher().observe_event(
            event_name=omni.kit.app.GLOBAL_EVENT_ERROR_LOG,
            on_event=on_log_event, observer_name="test_nested_menu_no_warnings")

        omni.kit.widget.context_menu.get_menu_dict()
        await omni.kit.app.get_app().next_update_async()

        # ensure there are no merge warnings
        self.assertEqual(warning_count, 0)

        del log_sub
        del a, b

async def test_menu_action(self):
        action_ext_id = "omni.kit.widget.context_menu.test"
        self._menu_actions_called = 0
        menu_list = [
            {
                "name": "Menu Action without parameters",
                "onclick_action": (action_ext_id, "action_without_parameter"),
            },
            {
                "name": "Menu Action with a parameter",
                "onclick_action": (action_ext_id, "action_with_a_parameter"),
            },
        ]

        def _run_menu_action():
            self._menu_actions_called += 1

        action_registry = get_action_registry()
        action_registry.register_action(action_ext_id, "action_without_parameter", lambda: _run_menu_action())
        action_registry.register_action(action_ext_id, "action_with_a_parameter", lambda menu_xpos: _run_menu_action())

        try:
            await self.create_test_window(width=200, height=330, block_devices=False)
            await ui_test.human_delay(10)
            context_menu = omni.kit.widget.context_menu.get_instance()
            omni.kit.widget.context_menu.reorder_menu_dict(menu_list)
            context_menu.show_context_menu("toolbar", {"menu_xpos": 4, "menu_ypos": 4}, menu_list)
            await ui_test.human_delay(10)
            await ui_test.select_context_menu("Menu Action without parameters")
            await ui_test.human_delay(20)
            self.assertEqual(self._menu_actions_called, 1)
            context_menu.show_context_menu("toolbar", {"menu_xpos": 4, "menu_ypos": 4}, menu_list)
            await ui_test.human_delay(10)
            await ui_test.select_context_menu("Menu Action with a parameter")
            await ui_test.human_delay(20)
            self.assertEqual(self._menu_actions_called, 2)
        finally:
            action_registry.deregister_all_actions_for_extension(action_ext_id)
            await self.finalize_test_no_image()
