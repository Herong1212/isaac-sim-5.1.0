## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
__all__ = ["TestTextEditor"]

import omni.kit.test
from omni.ui.tests.test_base import OmniUiTest
from pathlib import Path
import omni.kit.app
from .._text_editor import TextEditor

EXTENSION_PATH = Path(omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__))
GOLDEN_PATH = EXTENSION_PATH.joinpath("data/golden")


STYLE = {"Field": {"background_color": 0xFF24211F, "border_radius": 2}}


class TestTextEditor(OmniUiTest):
    async def test_general(self):
        """Testing general look of TextEditor"""
        window = await self.create_test_window()

        lines = ["The quick brown fox jumps over the lazy dog."] * 20

        with window.frame:
            TextEditor(text_lines=lines)

        for i in range(2):
            await omni.kit.app.get_app().next_update_async()

        await self.finalize_test(golden_img_dir=GOLDEN_PATH, golden_img_name=f"test_general.png")

    async def test_syntax(self):
        """Testing languages of TextEditor"""
        import inspect

        window = await self.create_test_window()

        with window.frame:
            TextEditor(text_lines=inspect.getsource(self.test_syntax).splitlines(), syntax=TextEditor.Syntax.PYTHON)

        for i in range(2):
            await omni.kit.app.get_app().next_update_async()

        await self.finalize_test(golden_img_dir=GOLDEN_PATH, golden_img_name=f"test_syntax.png")

    async def test_text_changed_flag(self):
        """Testing TextEditor text edited callback"""
        from omni.kit import ui_test

        window = await self.create_test_window(block_devices=False)
        window.focus()

        text = "Lorem ipsum"
        text_new = "dolor sit amet"

        with window.frame:
            text_editor = TextEditor(text=text)

        await ui_test.wait_n_updates(2)

        self.text_changed = False

        def on_text_changed(text_changed):
            self.text_changed = text_changed

        text_editor.set_edited_fn(on_text_changed)
        self.assertFalse(self.text_changed)

        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(100, 100))
        await ui_test.wait_n_updates(2)

        await ui_test.emulate_char_press("A")
        await ui_test.wait_n_updates(2)
        self.assertTrue(self.text_changed)

        await ui_test.emulate_key_combo("BACKSPACE")
        await ui_test.wait_n_updates(2)
        self.assertFalse(self.text_changed)

        text_editor.text = text_new
        await ui_test.wait_n_updates(2)
        # Only user input will trigger the callback
        self.assertFalse(self.text_changed)

        await ui_test.emulate_char_press("A")
        await ui_test.wait_n_updates(2)
        self.assertTrue(self.text_changed)

        text_editor.set_edited_fn(None)
