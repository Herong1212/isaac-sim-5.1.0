__all__ = ["ResetHelper", "ResetButton"]
import abc
from typing import Callable, List
import carb.settings
import omni.ui as ui


class ResetHelper:
    def __init__(self, reset_button=None):
        self._reset_button = None

    @abc.abstractmethod
    def can_reset(self) -> bool:
        return False

    @abc.abstractmethod
    def reset(self) -> bool:
        return True

    def set_reset_button(self, button: "ResetButton"):
        self._reset_button = button
        self._update_reset_button()

    def _update_reset_button(self):
        if self._reset_button is None:
            return

        self._reset_button.refresh()


class ResetButton:
    def __init__(self, helpers: List[ResetHelper] = None, on_reset_fn: Callable[[None], None] = None):
        self._helpers = helpers if helpers else []
        self._settings = carb.settings.get_settings()
        self._on_reset_fn = on_reset_fn
        self._build_ui()

    def add_setting_model(self, helper: ResetHelper):
        if helper not in self._helpers:
            self._helpers.append(helper)
            self.refresh()

    def refresh(self):
        visible = False
        for helper in self._helpers:
            if helper.can_reset():
                visible = True
                break
        self._reset_button.visible = visible

    def _build_ui(self):
        with ui.HStack(width=0):
            ui.Spacer()
            with ui.VStack(width=0):
                ui.Spacer()
                with ui.ZStack(width=15, height=12):
                    with ui.HStack(style={"margin_width": 0}):
                        ui.Spacer()
                        with ui.VStack(width=0):
                            ui.Spacer()
                            ui.Rectangle(width=5, height=5, style_type_name_override="ResetButton.Invalid")
                            ui.Spacer()
                        ui.Spacer()
                    with ui.HStack():
                        ui.Spacer()
                        self._reset_button = ui.Rectangle(width=12, height=12, style_type_name_override="ResetButton", tooltip="Click to reset value")
                        ui.Spacer()
                self._reset_button.set_mouse_pressed_fn(lambda x, y, m, w: self._restore_defaults())
                ui.Spacer()
            ui.Spacer()

    def _restore_defaults(self):
        for helper in self._helpers:
            if helper.can_reset() and not helper.reset():
                return
        self._reset_button.visible = False
        if self._on_reset_fn:
            self._on_reset_fn()
