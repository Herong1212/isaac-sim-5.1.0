## Copyright (c) 2024, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

import omni.kit.test
from omni.ui.tests.test_base import OmniUiTest
from dataclasses import dataclass
from pathlib import Path
from typing import List
import omni.kit.app
import omni.ui as ui
import omni.kit.window.console
import omni.kit.ui_test as ui_test
from omni.kit.test_suite.helpers import wait_stage_loading
import carb.settings

OPEN_LOG_BUTTONS_PATH = "/exts/omni.kit.window.console/showOpenLogButtons"

class TestConsoleWindow(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        extension_path = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
        self._golden_img_dir = Path(extension_path).joinpath("data").joinpath("tests").absolute()

        ui.Workspace.show_window("Console")
        self._window = omni.kit.window.console.get_instance()._window
        await self.docked_test_window(window=self._window, width=1000, height=600, block_devices=False)

    # After running each test
    async def tearDown(self):
        await super().tearDown()

    async def test_console(self):
        self._window._command_manager.execute_command("clear")
        settings = carb.settings.get_settings()
        image = "test_console.png" if settings.get(OPEN_LOG_BUTTONS_PATH) else "test_console_no_log_buttons.png"
        
        self._window._command_manager.execute_command("clear")
        await omni.kit.app.get_app().next_update_async()

        await self.capture_and_compare(golden_img_dir=self._golden_img_dir, golden_img_name=image, use_log=False)

        await self.finalize_test_no_image()

    async def test_commands(self):

        async def __input_command(command: str):
            await ui_test.emulate_char_press(command)
            await ui_test.emulate_keyboard_press(carb.input.KeyboardInput.ENTER)
            await omni.kit.app.get_app().next_update_async()

        @dataclass
        class Log:
            level: str
            source: str
            message: str

        def __get_all_logs(log_view) -> List[str]:
            log_view.select_all_logs()
            logs = log_view.get_selected_log_string().split("\n")
            results = []
            for log in logs:
                fields = log.split(" ")
                if len(fields) <= 5:
                    continue
                results.append(Log(fields[3], fields[4], " ".join(fields[5:])))
            return results


        await self._set_log_level("info")
        await self._trigger_command_input()
        
        try:
            
            # Verify console is cleared
            await __input_command("clear")
            log_view = self._window._log_view._console_log_view
            log_view.select_all_logs()
            selected_count = log_view.get_selected_log_count()
            self.assertEqual(selected_count, 0)

            # Verify all commands are listed
            await __input_command("help")
            results = __get_all_logs(log_view)
            expected_messages = [f"{cmd.name} - {cmd.description}" for cmd in self._window._command_manager._commands]
            count = len(expected_messages)
            self.assertEqual([i.message for i in results[-count:]], expected_messages)

            # Verify history command
            await __input_command("history")
            results = __get_all_logs(log_view)
            expected_messages = [f"{index}: {cmd}" for index, cmd in enumerate(["clear", "help", "history"])]
            self.assertEqual([i.message for i in results[-3:]], expected_messages)

            # Verify open command
            open_stage_url = f"{self._golden_img_dir}/empty.usd"
            open_stage_url = open_stage_url.replace("\\", "/")
            await __input_command(f"open {open_stage_url}")
            await wait_stage_loading()
            context = omni.usd.get_context()
            stage_url = context.get_stage_url()
            # The driver letter may be different on case
            self.assertEqual(stage_url.lower(), open_stage_url.lower())

            # Verify close command
            await __input_command("close")
            for _ in range(4):
                await omni.kit.app.get_app().next_update_async()
            context = omni.usd.get_context()
            stage_url = context.get_stage_url()
            self.assertEqual(stage_url, '')

            # Verify script file
            # Here \t means tab to trigger auto-complete
            await __input_command("test_s\t")
            await omni.kit.app.get_app().next_update_async()
            results = __get_all_logs(log_view)
            self.assertEqual(results[-1].message, "Sample script")

            await __input_command("test_list")
            await omni.kit.app.get_app().next_update_async()
            results = __get_all_logs(log_view)
            self.assertEqual(results[-1].message, "list_test")
        finally:
            await self._set_log_level("warning")
            await self._trigger_command_input()
            await ui_test.emulate_mouse_move(ui_test.Vec2(0, 0))
            await omni.kit.app.get_app().next_update_async()
            await self.finalize_test_no_image()

    async def test_command_input_field(self):
        await self._trigger_command_input()
        input_field_ref = ui_test.find("Console//Frame/**/StringField[*].name=='commands'")
        input_field = input_field_ref.widget
        try:
            input_field.focus_keyboard()
            copy_string = "string to copy"
            await ui_test.emulate_char_press(copy_string)
            await input_field_ref.click(right_click=True)
            command_input = self._window._command_input
            context_menu = command_input._context_menu
            self.assertIsNotNone(context_menu)
            await ui_test.select_context_menu("Copy", context_menu, offset=ui_test.Vec2(5, 5))
            input_field.model.set_value("")
            await input_field_ref.click(right_click=True)
            await ui_test.select_context_menu("Paste", context_menu, offset=ui_test.Vec2(5, 5))
            await omni.kit.app.get_app().next_update_async()
            self.assertEqual(input_field.model.as_string, copy_string)
        finally:
            input_field.model.set_value("")
            await self._trigger_command_input()
            await self.finalize_test_no_image()

    async def test_log_view_context_menu(self):
        self._window._command_manager.execute_command("clear")
        carb.log_warn("a")
        carb.log_warn("b")
        carb.log_warn("c")

        log_view_ref = ui_test.find("Console//Frame/**/ConsoleLogView[*].name=='log'")
        await log_view_ref.click(right_click=True)
        context_menu = self._window._log_view._context_menu
        console_log_view = self._window._log_view._console_log_view
        self.assertEqual(console_log_view.get_selected_log_count(), 0)
        self.assertIsNotNone(context_menu)
        await ui_test.select_context_menu("Select All", context_menu, offset=ui_test.Vec2(5, 5))

        self.assertEqual(console_log_view.get_selected_log_count(), 3)
        await log_view_ref.click(right_click=True)
        await ui_test.select_context_menu("Copy 3 Messages", context_menu, offset=ui_test.Vec2(5, 5))
        messages = omni.kit.clipboard.paste().split("\n")
        self.assertEqual([m.split(" ")[-1] for m in messages[:3]], ["a", "b", "c"])

        await self.finalize_test_no_image()

    async def _trigger_command_input(self):
        commands_button = ui_test.find("Console//Frame/**/ToolbarButton[*].name=='command'")
        await commands_button.click()
        await omni.kit.app.get_app().next_update_async()

    async def _set_log_level(self, level: str):
        log_level_button = ui_test.find(f"Console//Frame/**/ToolbarButton[*].name=='{level}'")
        await log_level_button.click()
        await omni.kit.app.get_app().next_update_async()
