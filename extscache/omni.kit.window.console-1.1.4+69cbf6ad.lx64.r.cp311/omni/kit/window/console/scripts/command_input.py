import asyncio
from typing import Optional

import carb
import omni.kit.app
import omni.kit.clipboard
import omni.ui as ui

from .console_command import console_log_info, CommandManager


class CommandInput:
    def __init__(self, command_manager: CommandManager, cmd_input_visible_model: ui.SimpleBoolModel) -> None:
        """
        Input field for command.

        Args:
            command_manager (CommandManager): Manager to execute commands.
            cmd_input_visible_model (ui.SimpleBoolModel): Model to show/hide command input.
        """
        self.__command_manager = command_manager
        self.__cmd_input_visible_model = cmd_input_visible_model

        self._context_menu: Optional[ui.Menu] = None

        self._build_ui()

    def destroy(self):
        self.__sub_command = None
        self.__sub_input_end = None

    def _build_ui(self) -> None:
        self._command_frame = ui.VStack(visible=self.__cmd_input_visible_model.as_bool, spacing=6, height=0, mouse_released_fn=lambda x, y, btn, m: self.__on_mouse_released(btn))
        with self._command_frame:
            ui.Separator(height=0)

            # Allow tab input so we can handle TAB key to list commands per input
            # TODO: How to handle UP/DOWN to list history command
            with ui.ZStack():
                self._command_input = ui.StringField(height=26, allow_tab_input=True, name="commands")
                self._hint_container = ui.HStack(spacing=5)
                with self._hint_container:
                    ui.Spacer(width=4)
                    ui.Label("Type 'HELP' to show help information.", style_type_name_override="CommandField.Hint")
            self.__sub_input_end = self._command_input.model.subscribe_end_edit_fn(self.__on_command_input_end)
            self.__sub_input_changed = self._command_input.model.subscribe_value_changed_fn(self.__on_command_input_changed)

            def __on_command_model_changed(_):
                self._command_frame.visible = self.__cmd_input_visible_model.as_bool
                if self._command_frame.visible:
                    self._focus()

            self.__sub_command = self.__cmd_input_visible_model.subscribe_value_changed_fn(__on_command_model_changed)
        
    def _focus(self):

        async def __focus_async():
            await omni.kit.app.get_app().next_update_async()
            self._command_input.focus_keyboard()

        asyncio.ensure_future(__focus_async())

    def __on_command_input_end(self, model) -> None:
        async def __execute_command():
            await omni.kit.app.get_app().next_update_async()
            if self._context_menu and self._context_menu.shown:
                return

            command = self._command_input.model.as_string.strip()
            if command:
                self.__command_manager.execute_command(command)
                self._command_input.model.set_value("")
                self._command_input.focus_keyboard()

        asyncio.ensure_future(__execute_command())

    def __on_command_input_changed(self, model) -> None:
        value = model.as_string
        self._hint_container.visible = value == ""
        if value and value[-1] == "\t":
            prefix = value[:-1]
            async def __list_commands(prefix):
                await omni.kit.app.get_app().next_update_async()

                commands = self.__command_manager.list_commands(prefix)
                if len(commands) == 0:
                    console_log_info(f'No match for "{prefix}"\n')
                    model.set_value(prefix)
                elif len(commands) == 1:
                    model.set_value(commands[0])
                else:
                    model.set_value(prefix)
                    console_log_info("Possible matches:\n")
                    for command in commands:
                        console_log_info(f"- {command}\n")

            asyncio.ensure_future(__list_commands(prefix))

    def __on_mouse_released(self, btn: int) -> None:
        if btn == 1:
            if self._context_menu is None:
                self._context_menu = ui.Menu("###ConsoleInputContextMenu", menu_compatibility=False)
                with self._context_menu:

                    def __copy():
                        omni.kit.clipboard.copy(self._command_input.model.as_string)

                    def __paste():
                        self._command_input.model.set_value(omni.kit.clipboard.paste())
                        self._focus()

                    ui.MenuItem("Copy", triggered_fn=__copy)
                    ui.MenuItem("Paste", triggered_fn=__paste)

            self._context_menu.show()