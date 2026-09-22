# pylint: disable=missing-function-docstring, missing-class-docstring, invalid-overridden-method
import json

import omni.kit.test
from omni.kit import ui_test


class TestUsdAPI(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        from omni.kit.test_suite.helpers import arrange_windows

        from .create_prims import create_test_stage

        await arrange_windows("Stage", 200)
        await omni.usd.get_context().new_stage_async()
        self._prim_path = create_test_stage()

    async def tearDown(self):
        pass

    async def test_usd_api(self):
        from omni.kit.property.usd import PrimPathWidget

        # test PrimPathWidget.*_button_menu_entry
        button_menu_entry = PrimPathWidget.add_button_menu_entry(
            path="TestUsdAPI/Test Entry", glyph=None, name_fn=None, show_fn=None, enabled_fn=None, onclick_fn=None
        )
        self.assertTrue(button_menu_entry is not None)
        button_menu_entries = PrimPathWidget.get_button_menu_entries()
        self.assertTrue(button_menu_entry in button_menu_entries)
        PrimPathWidget.remove_button_menu_entry(button_menu_entry)
        button_menu_entries = PrimPathWidget.get_button_menu_entries()
        self.assertFalse(button_menu_entry in button_menu_entries)

        # test PrimPathWidget.*_path_item
        path_func_updates = 0

        def my_path_func():
            nonlocal path_func_updates
            path_func_updates += 1

        # select prim so prim path widget is drawn
        usd_context = omni.usd.get_context()
        usd_context.get_selection().set_selected_prim_paths([self._prim_path], True)

        PrimPathWidget.add_path_item(my_path_func)
        path_items = PrimPathWidget.get_path_items()
        self.assertTrue(my_path_func in path_items)
        await ui_test.human_delay(10)
        self.assertTrue(path_func_updates == 1)
        PrimPathWidget.rebuild()
        await ui_test.human_delay(10)
        self.assertTrue(path_func_updates == 2)
        PrimPathWidget.remove_path_item(my_path_func)
        self.assertFalse(my_path_func in path_items)
        PrimPathWidget.rebuild()
        await ui_test.human_delay(10)
        self.assertTrue(path_func_updates == 2)

        usd_context.get_selection().set_selected_prim_paths([], True)

    async def test_dictonary_merge(self):
        from omni.kit.property.usd import PrimPathWidget

        def json_serialize(obj):  # pragma: no cover
            if hasattr(obj, "json_enc"):
                return obj.json_enc()
            if hasattr(obj, "__dict__"):
                return obj.__dict__

            return {"unknown": f"{obj}"}

        # remove None values or "_fn" keys from dictionary
        def purge_list(to_purge):
            if isinstance(to_purge, list):
                return [purge_list(x) for x in to_purge if x is not None]
            if isinstance(to_purge, dict):
                return {key: purge_list(val) for key, val in to_purge.items() if val is not None and "_fn" not in key}
            return to_purge

        button_menu_entry = []
        button_menu_entry.append(PrimPathWidget.add_button_menu_entry("test/Toggle Wireframe Mode"))
        button_menu_entry.append(PrimPathWidget.add_button_menu_entry("test/Toggle Do Not Cast Shadows"))
        button_menu_entry.append(PrimPathWidget.add_button_menu_entry("test/Toggle Enable Shadow Terminator Fix"))
        button_menu_entry.append(PrimPathWidget.add_button_menu_entry("test/Toggle Enable Fast Refraction Shadow"))
        button_menu_entry.append(PrimPathWidget.add_button_menu_entry("test/Toggle Disable RT SSS Transmission"))
        button_menu_entry.append(PrimPathWidget.add_button_menu_entry("test/Toggle Enable Holdout Object"))
        button_menu_entry.append(PrimPathWidget.add_button_menu_entry("test/Toggle Invisible To Secondary Rays"))
        button_menu_entry.append(PrimPathWidget.add_button_menu_entry("test/Toggle Is Procedural Volume"))
        button_menu_entry.append(PrimPathWidget.add_button_menu_entry("test/Toggle Matte Object"))
        button_menu_entry.append(PrimPathWidget.add_button_menu_entry("test/Toggle Invisible to Primary Ray"))
        button_menu_entry.append(PrimPathWidget.add_button_menu_entry("test/Toggle Is Light"))
        button_menu_entry.append(PrimPathWidget.add_button_menu_entry("test/xx/yy/zz/Prototype Variations/All"))
        button_menu_entry.append(
            PrimPathWidget.add_button_menu_entry("test/xx/yy/zz/Prototype Variations/Scale Variation")
        )
        button_menu_entry.append(
            PrimPathWidget.add_button_menu_entry("test/xx/yy/zz/Prototype Variations/Rotation Variation")
        )
        button_menu_entry.append(
            PrimPathWidget.add_button_menu_entry("test/xx/yy/zz/Prototype Variations/Vertical Offset Variation")
        )
        button_menu_entry.append(
            PrimPathWidget.add_button_menu_entry("test/xx/yy/zz/Prototype Variations/Vertical Alignment Variation")
        )
        button_menu_entry.append(
            PrimPathWidget.add_button_menu_entry("test/xx/yy/zz/Prototype Variations/Distribution Probability")
        )
        button_menu_entry.append(PrimPathWidget.add_button_menu_entry("test/Target Surfaces/Surface Area"))

        menu_list = omni.kit.widget.context_menu.get_menu_dict("ADD", "")
        json_expected = "{'name': {'test': [{'name': 'Toggle Wireframe Mode'}, {'name': 'Toggle Do Not Cast Shadows'}, {'name': 'Toggle Enable Shadow Terminator Fix'}, {'name': 'Toggle Enable Fast Refraction Shadow'}, {'name': 'Toggle Disable RT SSS Transmission'}, {'name': 'Toggle Enable Holdout Object'}, {'name': 'Toggle Invisible To Secondary Rays'}, {'name': 'Toggle Is Procedural Volume'}, {'name': 'Toggle Matte Object'}, {'name': 'Toggle Invisible to Primary Ray'}, {'name': 'Toggle Is Light'}, {'name': {'xx': [{'name': {'yy': [{'name': {'zz': [{'name': {'Prototype Variations': [{'name': 'All'}, {'name': 'Scale Variation'}, {'name': 'Rotation Variation'}, {'name': 'Vertical Offset Variation'}, {'name': 'Vertical Alignment Variation'}, {'name': 'Distribution Probability'}]}}]}}]}}]}}, {'name': {'Target Surfaces': [{'name': 'Surface Area'}]}}]}}"
        json_data = ""
        for item in menu_list.copy():
            if isinstance(item["name"], dict) and "test" in item["name"]:
                json_data = json.dumps(purge_list(item), default=lambda obj: json_serialize(obj)).replace('"', "'")

        self.assertEqual(json_data, json_expected)
