# pylint: disable=missing-function-docstring, missing-class-docstring
import unittest

import carb
import omni.kit.test
import omni.usd
from carb.input import KeyboardInput
from omni.kit import ui_test
from omni.kit.test_suite.helpers import (
    arrange_windows,
    get_test_data_path,
    open_stage,
    select_prims,
    wait_stage_loading,
)
from omni.ui.tests.test_base import OmniUiTest


class TestRename(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await arrange_windows("Stage", 200)
        await open_stage(get_test_data_path(__name__, "usd/cube.usda"))
        await wait_stage_loading()
        carb.settings.get_settings().set("/exts/omni.kit.property.usd/allow_rename_prims", True)
        self._original_setting_value = carb.settings.get_settings().get_as_string(
            "/persistent/app/stage/unicodeNormalizationMethod"
        )

    # After running each test
    async def tearDown(self):
        carb.settings.get_settings().set(
            "/persistent/app/stage/unicodeNormalizationMethod", self._original_setting_value
        )
        await wait_stage_loading()

    async def test_rename_prim(self):
        from omni.kit.ui_test import emulate_char_press, emulate_keyboard_press

        stage = omni.usd.get_context().get_stage()

        await select_prims(["/Xform/Cube"])
        await ui_test.human_delay(10)
        await ui_test.find("Property//Frame/**/StringField[*].identifier=='prim_name'").click()
        await ui_test.human_delay(10)
        await emulate_char_press("1MyHövercräftISFullOfEels")
        await emulate_keyboard_press(KeyboardInput.ENTER)
        await ui_test.human_delay(10)

        # verify rename
        prim = stage.GetPrimAtPath("/Xform/_MyHövercräftISFullOfEels")
        self.assertTrue(prim.IsValid())

        # undo
        omni.kit.undo.undo()
        await ui_test.human_delay(10)

        # verify rename
        prim = stage.GetPrimAtPath("/Xform/Cube")
        self.assertTrue(prim.IsValid())

    async def test_rename_prim_with_unicode_NFC_normalization(self):
        import unicodedata

        from omni.kit.ui_test import emulate_keyboard_press

        stage = omni.usd.get_context().get_stage()

        # Test NFC normalization
        # These 2 prim names are unique in NFD but same in NFC
        two_codepoints = "가"  # ᄀ + ᅡ
        single_codepoint = "가"  # 가
        prim0 = stage.DefinePrim(f"/prim_{two_codepoints}", "Xform")
        prim1 = stage.DefinePrim(f"/prim_{single_codepoint}", "Xform")

        # Turn on NFC normalization option
        settings = carb.settings.get_settings()
        settings.set("/persistent/app/stage/unicodeNormalizationMethod", "NFC")

        self.assertNotEqual(prim0.GetName(), prim1.GetName())
        self.assertEqual(unicodedata.normalize("NFC", prim0.GetName()), unicodedata.normalize("NFC", prim1.GetName()))

        await select_prims([f"/prim_{two_codepoints}"])
        await ui_test.human_delay(10)
        string_field = ui_test.find("Property//Frame/**/StringField[*].identifier=='prim_name'")
        await string_field.click()
        await ui_test.human_delay(5)
        # If we don't do any edit, the prim name should automatically be applied NFC normalization, and since
        # there's already a prim with the same name, it will be renamed to prim_가_01
        await emulate_keyboard_press(KeyboardInput.ENTER)
        await ui_test.human_delay(5)
        self.assertFalse(prim0.IsValid())
        renamed_prim = stage.GetPrimAtPath(f"/prim_{single_codepoint}_01")
        self.assertTrue(renamed_prim.IsValid())
        self.assertEqual(renamed_prim.GetName(), "prim_가_01")

    @unittest.skipUnless(omni.kit.test.gitlab.is_running_in_gitlab(), "Can fail locally")
    async def test_copy_to_clipboard(self):
        await select_prims(["/Xform/Cube"])
        await ui_test.human_delay(10)

        # open context menu
        await ui_test.find("Property//Frame/**/StringField[*].identifier=='prim_name'").click(right_click=True)
        await ui_test.human_delay(10)

        # select context menu
        await ui_test.select_context_menu("Copy to clipboard", offset=ui_test.Vec2(10, 10))
        await ui_test.human_delay(10)

        # verify
        paste = omni.kit.clipboard.paste()
        self.assertEqual(paste, "Cube\n")

    @unittest.skipUnless(omni.kit.test.gitlab.is_running_in_gitlab(), "Can fail locally")
    async def test_copypath_to_clipboard(self):
        await select_prims(["/Xform/Cube"])
        await ui_test.human_delay(10)

        # open context menu
        await ui_test.find("Property//Frame/**/StringField[*].identifier=='prim_path'").click(right_click=True)
        await ui_test.human_delay(10)

        # select context menu
        await ui_test.select_context_menu("Copy to clipboard", offset=ui_test.Vec2(10, 10))
        await ui_test.human_delay(10)

        # verify
        paste = omni.kit.clipboard.paste()
        self.assertEqual(paste, "/Xform/Cube\n")

    async def test_rename_prim_disabled(self):
        from omni.kit.ui_test import emulate_char_press, emulate_keyboard_press

        carb.settings.get_settings().set("/exts/omni.kit.property.usd/allow_rename_prims", False)
        stage = omni.usd.get_context().get_stage()

        await select_prims(["/Xform/Cube"])
        await ui_test.human_delay(10)
        await ui_test.find("Property//Frame/**/StringField[*].identifier=='prim_name'").click()
        await ui_test.human_delay(10)
        await emulate_char_press("MyHovercraftIsFullOfEels")
        await emulate_keyboard_press(KeyboardInput.ENTER)
        await ui_test.human_delay(10)

        # verify prim wasn't renamed
        prim = stage.GetPrimAtPath("/Xform/MyHovercraftIsFullOfEels")
        self.assertFalse(prim.IsValid())
        prim = stage.GetPrimAtPath("/Xform/Cube")
        self.assertTrue(prim.IsValid())
