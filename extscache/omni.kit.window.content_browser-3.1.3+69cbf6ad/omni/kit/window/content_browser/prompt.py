import omni
import omni.ui as ui
from .style import ICON_PATH


class Prompt:
    def __init__(
        self,
        title,
        text,
        content_buttons,
        modal=False,
    ):
        self._title = title
        self._text = text
        self._content_buttons = content_buttons
        self._modal = modal
        self._buttons = []
        self._build_ui()

    def __del__(self):
        for button in self._buttons:
            button.set_clicked_fn(None)
        self._buttons.clear()

    def show(self):
        self._window.visible = True

    def hide(self):
        self._window.visible = False

    def is_visible(self):
        return self._window.visible

    def _build_ui(self):
        import carb.settings

        self._window = ui.Window(
            self._title, visible=False, height=0, dockPreference=ui.DockPreference.DISABLED
        )
        self._window.flags = (
            ui.WINDOW_FLAGS_NO_COLLAPSE
            | ui.WINDOW_FLAGS_NO_RESIZE
            | ui.WINDOW_FLAGS_NO_SCROLLBAR
            | ui.WINDOW_FLAGS_NO_RESIZE
            | ui.WINDOW_FLAGS_NO_MOVE
        )

        if self._modal:
            self._window.flags = self._window.flags | ui.WINDOW_FLAGS_MODAL

        theme = carb.settings.get_settings().get_as_string("/persistent/app/window/uiStyle") or "NvidiaDark"
        button_style = {
            "Button": {"stack_direction": ui.Direction.LEFT_TO_RIGHT},
            "Button.Image": {"alignment": ui.Alignment.CENTER},
            "Button.Label": {"alignment": ui.Alignment.LEFT_CENTER}
        }

        def button_cliked_fn(button_fn):
            if button_fn:
                button_fn()
            self.hide()

        with self._window.frame:
            with ui.VStack(height=0):
                ui.Spacer(width=0, height=10)
                if self._text:
                    with ui.HStack(height=0):
                        ui.Spacer()
                        self._text_label = ui.Label(self._text, word_wrap=True, width=self._window.width - 80, height=0)
                        ui.Spacer()
                    ui.Spacer(width=0, height=10)
                with ui.VStack(height=0):
                    ui.Spacer(height=0)
                    for button in self._content_buttons:
                        (button_text, button_icon, button_fn) = button
                        with ui.HStack():
                            ui.Spacer(width=40)
                            ui_button = ui.Button(
                                "  " + button_text,
                                image_url=f"{ICON_PATH}/{button_icon}",
                                image_width=24,
                                height=40,
                                clicked_fn=lambda a=button_fn: button_cliked_fn(a),
                                style=button_style
                            )
                            ui.Spacer(width=40)
                        ui.Spacer(height=5)
                        self._buttons.append(ui_button)
                    ui.Spacer(height=5)
                    with ui.HStack():
                        ui.Spacer()
                        cancel_button = ui.Button("Cancel", width=80, height=0)
                        cancel_button.set_clicked_fn(lambda: self.hide())
                        self._buttons.append(cancel_button)
                        ui.Spacer(width=40)
                    ui.Spacer(height=0)
                ui.Spacer(width=0, height=10)
