## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

from pathlib import Path
from tempfile import TemporaryDirectory

from omni.kit.widget.text_editor import TextEditor
import omni.kit.ui_test as ui_test
import omni.ui as ui
from omni.kit.test import AsyncTestCase

CURRENT_PATH = Path(__file__).parent.joinpath("../../../../../data")

# Use it to receive extraterrestrial messages from executing script
public_mailbox = ""


class TestScriptEditor(AsyncTestCase):
    # Before running each test
    async def setUp(self):
        global public_mailbox
        public_mailbox = ""

        ui.Workspace.show_window("Script Editor")
        await ui_test.wait_n_updates(2)
        self._editor_window_ref = ui_test.find("Script Editor")
        await self._editor_window_ref.focus()
        self._editor_window = self._editor_window_ref._widget
        self._editor_widget = self._editor_window._script_editor_widget
        self._btn_run = ui_test.find("Script Editor//Frame/**/Button[*].identifier=='execute_script'")
        self._editor = ui_test.find("Script Editor//Frame/**/script_editor_0")

        # Clear script
        self._editor_widget.current_editor.text = ""

        # Focus on text field
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(700, 500))

    async def tearDown(self):
        self._editor.text = ""

    async def test_script_run(self):
        await ui_test.emulate_char_press("import omni.kit.window.script_editor.tests.test_script_editor as editor\n")
        await ui_test.emulate_char_press("editor.public_mailbox = 'who is there?'\n")
        await ui_test.wait_n_updates(2)
        await self._execute()
        self.assertEqual(public_mailbox, "who is there?")

        # Add another line
        await ui_test.emulate_char_press("editor.public_mailbox = 123\n")
        await ui_test.wait_n_updates(2)
        await self._execute()
        self.assertEqual(public_mailbox, 123)

        # New tab
        await ui_test.emulate_key_combo("CTRL+N")
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(700, 500))
        await ui_test.emulate_char_press("import omni.kit.window.script_editor.tests.test_script_editor as editor\n")
        await ui_test.emulate_char_press("editor.public_mailbox = 'yellow'\n")
        await ui_test.wait_n_updates(2)
        await self._execute()
        self.assertEqual(public_mailbox, "yellow")

    async def test_script_fail(self):
        await ui_test.emulate_char_press("import omni.kit.window.script_editor.tests.test_script_editor as editor\n")
        await ui_test.emulate_char_press("editor.public_mailbox = 555\n")
        await ui_test.emulate_char_press("x = \n")  # typo
        await ui_test.wait_n_updates(2)
        await self._execute()
        self.assertEqual(public_mailbox, "")

        # fix it
        await ui_test.emulate_key_combo("BACKSPACE")
        await ui_test.emulate_key_combo("BACKSPACE")
        await ui_test.emulate_char_press("3")
        await ui_test.wait_n_updates(2)
        await self._execute()
        self.assertEqual(public_mailbox, 555)

    async def test_script_get_source(self):
        # That tests: exts."omni.kit.window.script_editor".executeInTempFile = true
        # If we are not writing to a temp file ast/inspect doesn't work and throws error that it can't find source.
        await ui_test.emulate_char_press(
            """
import ast
import inspect
import omni.kit.window.script_editor.tests.test_script_editor as editor

foo = lambda y: y
lines = inspect.getsource(foo)
r = ast.parse(lines)
editor.public_mailbox = r is not None
"""
        )
        await ui_test.wait_n_updates(2)
        await self._execute()
        self.assertEqual(public_mailbox, True)

    async def test_close_and_reopen_window(self):
        """Tests to make sure that content remains in the window even after it has been closed and reopened."""
        global public_mailbox

        await ui_test.emulate_char_press("import omni.kit.window.script_editor.tests.test_script_editor as editor\n")
        await ui_test.emulate_char_press("editor.public_mailbox = 'Hello World'\n")
        await ui_test.wait_n_updates(2)
        await self._execute()

        self.assertEqual(public_mailbox, "Hello World")
        await ui_test.wait_n_updates(2)

        self._editor_window.visible = False
        await ui_test.wait_n_updates(20)
        public_mailbox = ""

        self._editor_window.visible = True
        await ui_test.wait_n_updates(2)
        await self._execute()
        self.assertEqual(public_mailbox, "Hello World")

    async def test_script_print_log(self):
        """Test to prevent log output from missing."""
        await ui_test.emulate_char_press("print(\"test print log\")\n")
        await ui_test.wait_n_updates(2)
        await self._execute()
        self.assertEqual(self._editor_window._script_editor_widget.get_last_log_text(), "test print log")

    async def test_add_close_tab(self):
        """Test to add a new tab and close it."""
        self.assertEqual(len(self._editor_window._script_editor_widget._tabs._tabs), 1)

        # Add by hotkey
        # Without test window show, must short human_delay_speed to make sure the key combo is triggered only once
        await ui_test.emulate_key_combo("CTRL+N", human_delay_speed=1)
        self.assertEqual(len(self._editor_widget._tabs._tabs), 2)
        self.assertEqual(self._editor_widget._tabs._tabs[0].index, 0)
        self.assertEqual(self._editor_widget._tabs._tabs[1].index, 1)

        # Add by function (menu item)
        self._editor_widget.add_tab()
        self.assertEqual(len(self._editor_widget._tabs._tabs), 3)
        self.assertEqual(self._editor_widget._tabs._tabs[0].index, 0)
        self.assertEqual(self._editor_widget._tabs._tabs[1].index, 1)
        self.assertEqual(self._editor_widget._tabs._tabs[2].index, 2)

        # Close by hotkey
        self._editor_widget.close_tab()
        self.assertEqual(len(self._editor_widget._tabs._tabs), 2)
        self.assertEqual(self._editor_widget._tabs._tabs[0].index, 0)
        self.assertEqual(self._editor_widget._tabs._tabs[1].index, 1)

        # Close by function (menu item)
        self._editor_widget.close_tab()
        self.assertEqual(len(self._editor_widget._tabs._tabs), 1)
        self.assertEqual(self._editor_widget._tabs._tabs[0].index, 0)

        # Close last tab will close it immediately and create new tab moment later
        self._editor_widget.close_tab()
        self.assertEqual(len(self._editor_widget._tabs._tabs), 0)
        await ui_test.wait_n_updates(2)
        self.assertEqual(len(self._editor_widget._tabs._tabs), 1)
        self.assertEqual(self._editor_widget._tabs._tabs[0].index, 0)

    async def test_set_palette(self):
        """Test to set palette."""
        default_palette = "Dark"
        self._editor_window._set_editor_palette("Light")
        self.assertEqual(self._editor_widget.current_editor.palette, TextEditor.Palette.Light)
        self._editor_window._set_editor_palette(default_palette)

    async def test_editor_functions(self):
        """Test to check editor functions."""
        text = "test"
        await ui_test.emulate_char_press(text)
        await ui_test.wait_n_updates(2)
        self._editor_widget.undo()
        self.assertEqual(self._editor_widget.current_editor.text, text[:len(text) - 1] + "\n")
        self._editor_widget.redo()
        self.assertEqual(self._editor_widget.current_editor.text, text + "\n")

        self._editor_widget.select_all()
        await ui_test.wait_n_updates(2)
        self.assertEqual(self._btn_run._widget.text, "Run Selected (Ctrl + Enter)")
        self._editor_widget.cut()
        await ui_test.wait_n_updates(2)
        self.assertEqual(self._editor_widget.current_editor.text, "\n")
        self._editor_widget.paste()
        await ui_test.wait_n_updates(2)
        self.assertEqual(self._editor_widget.current_editor.text, text + "\n")

        self._editor_widget.select_all()
        await ui_test.wait_n_updates(2)
        self._editor_widget.copy()
        self._editor_widget.delete()
        await ui_test.wait_n_updates(2)
        self.assertEqual(self._editor_widget.current_editor.text, "\n")
        self._editor_widget.paste()
        await ui_test.wait_n_updates(2)
        self.assertEqual(self._editor_widget.current_editor.text, text + "\n")

    async def test_font_size(self):
        """Test to check font size."""
        old_size = self._editor_window._get_font_size()
        self._editor_window._set_font_size(18)
        self.assertEqual(self._editor_window._get_font_size(), 18)
        self._editor_window._set_font_size(old_size)

    async def test_execute_on_reload(self):
        """Test to check execute on reload."""
        self.assertFalse(self._editor_window._is_execute_file_on_reload())
        self._editor_window._toggle_execute_file_on_reload()
        self.assertTrue(self._editor_window._is_execute_file_on_reload())
        try:
            with TemporaryDirectory() as tmpdir:
                # tmp_dir = Path(tmpdir).resolve()
                tmp_file = tmpdir + "/test.py"
                with open(tmp_file, "w", encoding="utf-8") as tmp_fd:
                    tmp_fd.write(
"""
import omni.kit.window.script_editor.tests.test_script_editor as editor
editor.public_mailbox = "test"
"""
                    )
                self._editor_widget.load_script(tmp_file)

                with open(tmp_file, "w", encoding="utf-8") as tmp_fd:
                    tmp_fd.write(
"""
import omni.kit.window.script_editor.tests.test_script_editor as editor
editor.public_mailbox = "reload"
"""
                    )
                await ui_test.wait_n_updates(2)
                self.assertEqual(public_mailbox, "reload")
        finally:
            self._editor_widget.close_tab()
            self._editor_window._toggle_execute_file_on_reload()
            self.assertFalse(self._editor_window._is_execute_file_on_reload())

    async def _execute(self):
        # Click on Run button and focus on editor again
        await self._btn_run.click()
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(700, 500))
