# pylint: disable=relative-beyond-top-level, attribute-defined-outside-init
__all__ = ["WarningMessage", "WarningWindow"]
from dataclasses import dataclass
from typing import List, Tuple, Callable, Union, Optional
import omni.ui as ui
from ..style import WARNING_WINDOW_STYLE


@dataclass
class WarningMessage:
    message: str
    highlight: bool = False


class WarningWindow(ui.Window):
    r"""
    Window Show warning message.

    Args:
        title (str): Warning title.
        messages (List[Union[str, WarningMessage]]): Message list. Use a single '\n' for a new line.
        buttons (List[Tuple[str, Callable[[None], None]]): Button list. Default 'OK' to close.
        width (ui.Length): Window width. Default 360 pixels.
        button_width (ui.Length): Width of a single button. Default 60 pixels.
        visible (bool): Visible after created. Default True.
    """

    PADDING = 4

    def __init__(
        self,
        title: str,
        messages: Optional[List[Union[str, WarningMessage]]] = None,
        buttons: Optional[List[Tuple[str, Callable[[None], None]]]] = None,
        width: ui.Length = 360,
        button_width=60,
        visible=True
    ):
        self.__title = title
        self.__messages = messages if messages else []
        self.__buttons = buttons if buttons else []
        self.__button_width = button_width
        self.__width = width

        flags = ui.WINDOW_FLAGS_NO_TITLE_BAR | ui.WINDOW_FLAGS_NO_RESIZE | ui.WINDOW_FLAGS_NO_MOVE | ui.WINDOW_FLAGS_MODAL
        super().__init__(f"###Hotkey_WARNING_{title}", width=width, visible=visible, flags=flags, auto_resize=True, padding_x=0, padding_y=0)

        self.frame.set_style(WARNING_WINDOW_STYLE)
        self.frame.set_build_fn(self.__build_ui)

    def __del__(self):
        self.destroy()

    def __build_ui(self):
        with self.frame:
            with ui.VStack(width=self.__width, height=0):
                self._build_titlebar()
                ui.Spacer(height=15)
                self._build_message()
                ui.Spacer(height=15)
                self._build_buttons()
                ui.Spacer(height=15)

    def _build_titlebar(self):
        with ui.ZStack(height=0):
            ui.Rectangle(style_tyle_name_override="Titlebar.Background")
            with ui.VStack():
                ui.Spacer(height=self.PADDING)
                with ui.HStack():
                    ui.Spacer(width=self.PADDING)
                    ui.Image(width=16, style_type_name_override="Titlebar.Image")
                    ui.Spacer(width=8)
                    ui.Label(self.__title, width=0, style_tyle_name_override="Titlebar.Title")
                    ui.Spacer(width=self.PADDING)
                ui.Spacer(height=self.PADDING)

    def _build_message(self):
        message_lines = []
        message_lines.append([])
        for message in self.__messages:
            if isinstance(message, str):
                if message == "\n":
                    message_lines.append([])
                message_lines[len(message_lines) - 1].append(WarningMessage(message))
            elif isinstance(message, WarningMessage):
                message_lines[len(message_lines) - 1].append(message)
        with ui.VStack(spacing=6, height=0):
            for messages in message_lines:
                with ui.HStack():
                    ui.Spacer(width=self.PADDING)
                    ui.Spacer()
                    for message in messages:
                        ui.Label(
                            message.message,
                            width=0,
                            alignment=ui.Alignment.CENTER,
                            style_type_name_override="Warning.Text",
                            name="highlight" if message.highlight else ""
                        )
                    ui.Spacer()
                    ui.Spacer(width=self.PADDING)

    def _build_buttons(self):
        if self.__buttons:
            with ui.HStack():
                ui.Spacer()
                for index, button in enumerate(self.__buttons):
                    if index > 0:
                        ui.Spacer(width=20)
                    ui.Button(button[0], width=self.__button_width, clicked_fn=lambda fn=button[1]: self.__on_button_click(fn), style_type_name_override="Warning.Button")
                ui.Spacer(width=self.PADDING)
        else:
            with ui.HStack():
                ui.Spacer()
                ui.Button("OK", width=self.__button_width, clicked_fn=self.__on_button_click, style_type_name_override="Warning.Button")
                ui.Spacer(width=self.PADDING)

    def __on_button_click(self, clicked_fn: Callable[[None], bool] = None) -> None:
        keep_open = False
        if clicked_fn:
            keep_open = clicked_fn()

        if not keep_open:
            self.visible = False
