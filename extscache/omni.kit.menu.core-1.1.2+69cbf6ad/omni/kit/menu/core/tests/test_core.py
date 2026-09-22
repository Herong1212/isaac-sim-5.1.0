# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import carb
import omni.kit.app
import omni.kit.commands
import omni.kit.test
from omni.kit import ui_test
from omni.kit.menu.core import DictReadOnly, IconMenuBaseDelegate, uiMenu, uiMenuItem
from omni.ui.tests.test_base import OmniUiTest

# pylint: disable=broad-except


class TestCore(OmniUiTest):
    class DefaultMenuDelegate(IconMenuBaseDelegate):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.load_settings("omni.kit.menu.utils")

        def get_elided_length(self, menu_name):
            return 160

    # Before running each test
    async def setUp(self):
        await super().setUp()
        await omni.usd.get_context().new_stage_async()

    # After running each test
    async def tearDown(self):
        await super().tearDown()

    async def test_core(self):
        default_delegate = TestCore.DefaultMenuDelegate()
        self._menu_root = uiMenu(
            "Test Menu",
            enabled=True,
            delegate=default_delegate,
            tearable=False,
            glyph="menu_prim.svg",
            menu_checkable=True,
            menu_hotkey_text="Cheese",
            submenu=False,
        )
        self._menu_items = []
        with self._menu_root:
            self._menu_items.append(
                uiMenuItem("Test Menu Item 1", enabled=True, glyph="menu_prim.svg", menu_checkable=True)
            )
            self._menu_items.append(
                uiMenuItem("Test Menu Item 2", enabled=True, glyph="menu_prim.svg", menu_hotkey_text="Cheese")
            )
            self._menu_items.append(uiMenuItem("Test Menu Item 3", enabled=True, glyph="menu_prim.svg"))
            self._menu_items.append(uiMenuItem("Test Menu Item 4", enabled=True, glyph="menu_prim.svg"))

        self._menu_root.show_at(100, 100)

        await ui_test.human_delay(50)

    async def test_dict_read_only(self):
        master_dict = {"Window": {"background_color": 0xFF000000, "border_color": 0x0, "border_radius": 0}}
        test_dict = DictReadOnly({"Window": {"background_color": 0xFF000000, "border_color": 0x0, "border_radius": 0}})

        # add item
        try:
            test_dict["cheese"] = 1
        except Exception as exc:
            carb.log_warn(f"{exc}")
        self.assertEqual(test_dict, master_dict)

        # clear
        try:
            test_dict.clear()
        except Exception as exc:
            carb.log_warn(f"{exc}")
        self.assertEqual(test_dict, master_dict)

        # pop
        try:
            test_dict.pop()
        except Exception as exc:
            carb.log_warn(f"{exc}")
        self.assertEqual(test_dict, master_dict)

        # pop item
        try:
            test_dict.pop("test", None)
        except Exception as exc:
            carb.log_warn(f"{exc}")
        self.assertEqual(test_dict, master_dict)

        # update
        try:
            test_dict.update({"test": "cheese"})
        except Exception as exc:
            carb.log_warn(f"{exc}")
        self.assertEqual(test_dict, master_dict)

        # ior
        try:
            test_dict |= {"test": "cheese"}
        except Exception as exc:
            carb.log_warn(f"{exc}")
        self.assertEqual(test_dict, master_dict)

        # or
        new_dict = test_dict | {"more": 2}
        self.assertEqual(test_dict, master_dict)
        self.assertEqual(
            new_dict, {"Window": {"background_color": 4278190080, "border_color": 0, "border_radius": 0}, "more": 2}
        )

        # copy
        new_dict = test_dict.copy()
        self.assertEqual(new_dict, master_dict)
        new_dict = new_dict | {"more": 2}
        self.assertEqual(test_dict, master_dict)
        self.assertEqual(
            new_dict, {"Window": {"background_color": 4278190080, "border_color": 0, "border_radius": 0}, "more": 2}
        )

        # iter
        new_dict = {}
        for item in test_dict:
            new_dict[item] = test_dict[item]
        self.assertEqual(test_dict, master_dict)
        self.assertEqual(new_dict, master_dict)

        # keys
        new_dict = {}
        for item in test_dict.keys():
            new_dict[item] = test_dict[item]
        self.assertEqual(test_dict, master_dict)
        self.assertEqual(new_dict, master_dict)

        # len
        test_len = len(test_dict)
        self.assertEqual(test_len, 1)
        self.assertEqual(test_dict, master_dict)
