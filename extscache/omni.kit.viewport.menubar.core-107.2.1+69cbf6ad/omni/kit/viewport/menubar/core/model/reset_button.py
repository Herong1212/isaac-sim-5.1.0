import abc
from typing import Callable, Optional, List
import carb.settings
import omni.ui as ui


class ResetHelper:
    """
    A helper class for reset button.
    """
    def __init__(self, reset_button: Optional["ResetButton"] = None):
        """
        Constructor.

        Keyword Args:
            reset_button (Optional["ResetButton"]): Reset button to attach, defaults to None.
        """
        self._reset_button = reset_button

    @abc.abstractmethod
    def get_default(self):
        """Get default value"""
        return  # pragma: no cover

    @abc.abstractmethod
    def restore_default(self):
        """Restore default value"""
        return  # pragma: no cover

    @abc.abstractmethod
    def get_value(self):
        """Get current value"""
        return  # pragma: no cover

    def set_reset_button(self, button: "ResetButton"):
        """
        Attach to a reset button.

        Args:
            button ("ResetButton"): Reset button to attach.
        """
        self._reset_button = button
        self._update_reset_button()

    def _update_reset_button(self):
        if self._reset_button is None:
            return

        self._reset_button.refresh()


class ResetButton:
    """A button to reset value"""
    def __init__(self, helpers: Optional[List[ResetHelper]] = None, on_reset_fn: Callable[[None], None] = None):
        """
        Constructor.

        Keyword Args:
            helpers (Optional[List[ResetHelper]]): List for reset helper attached to this button, defaults to None.
            on_reset_fn (Callable[[None], None]): Callback when button clicked, defaults to None.
        """
        self._helpers = helpers
        self._settings = carb.settings.get_settings()
        self._on_reset_fn = on_reset_fn
        self._build_ui()

    def add_setting_model(self, helper: ResetHelper) -> None:
        """
        Add reset helper.

        Args:
            helper (ResetHelper): Reset helper.
        """
        if self._helpers and helper not in self._helpers:
            self._helpers.append(helper)
            self.refresh()

    def refresh(self):
        """Refresh button status"""
        visible = False
        if self._helpers:
            for helper in self._helpers:
                default = helper.get_default()
                current = helper.get_value()
                if default != current:
                    visible = True
                    break
        self._reset_button.visible = visible

    def _build_ui(self):
        with ui.VStack(width=0, height=0):
            ui.Spacer()
            with ui.ZStack(width=15, height=15):
                with ui.HStack(style={"margin_width": 0}):
                    ui.Spacer()
                    with ui.VStack(width=0):
                        ui.Spacer()
                        ui.Rectangle(width=5, height=5, name="reset_invalid")
                        ui.Spacer()
                    ui.Spacer()
                self._reset_button = ui.Rectangle(width=12, height=12, name="reset", tooltip="Click to reset value")

            self._reset_button.set_mouse_pressed_fn(lambda x, y, m, w: self._restore_defaults())
            ui.Spacer()

        self.refresh()

    def _restore_defaults(self):
        if self._helpers:
            for helper in self._helpers:
                default_value = helper.get_default()
                current_value = helper.get_value()
                if default_value != current_value:
                    helper.restore_default()
        self._reset_button.visible = False
        if self._on_reset_fn:
            self._on_reset_fn()
