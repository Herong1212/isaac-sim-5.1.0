"""This module provides a custom progress tracking model and a popup UI component for displaying progress within the Omniverse Kit."""

from omni import ui


class CustomProgressModel(ui.AbstractValueModel):
    """A model to track and manage progress information for UI components.

    This model is designed to work with progress bars or similar UI components in need of displaying progress. It maintains current progress value and total steps, allowing for the dynamic adjustment of the progress displayed. The model ensures that the progress value is always within the bounds of the total steps and provides functionalities to convert and retrieve the progress as both a float ratio and a formatted string.
    """

    def __init__(self):
        super().__init__()
        self._value = 0
        self._total_steps = 0

    def set_value(self, value):
        """Reimplemented set"""
        if value != self._value:
            # Tell the widget that the model is changed
            self._value = min(value, self._total_steps)
            self._value_changed()

    @property
    def total_steps(self):
        return self._total_steps

    @total_steps.setter
    def total_steps(self, value):
        if value != self._total_steps:
            self._total_steps = value
            self._value = min(self._value, self._total_steps)
            self._value_changed()

    @property
    def progress(self):
        return self._value

    def get_value_as_float(self):
        return self._value / self._total_steps if self._total_steps > 0 else 0.0

    def get_value_as_string(self):
        return f"{str(self._value)}/{str(self._total_steps)}"


class ProgressPopup:
    """Creates a modal window with a status label and a progress bar inside.

    Args:
        title (str): Title of the window.
        cancel_button_text (str): Text for the cancel button.
        cancel_button_fn (callable): Callback function for the cancel button.
        status_text (str): Initial text to display as status.
        modal (bool): Determines if the window is modal.
    """

    def __init__(self, title, cancel_button_text="Cancel", cancel_button_fn=None, status_text="", modal=False):
        self._status_text = status_text
        self._title = title
        self._cancel_button_text = cancel_button_text
        self._cancel_button_fn = cancel_button_fn
        self._progress_bar_model = None
        self._modal = modal
        self._popup = None
        self._buttons = []
        self._build_ui()

    def destroy(self):
        self._cancel_button_fn = None
        self._progress_bar_model = None
        for button in self._buttons:
            button.set_clicked_fn(None)
        self._popup = None

    def __enter__(self):
        self._popup.visible = True
        return self

    def __exit__(self, type, value, trace):
        self._popup.visible = False

    def set_cancel_fn(self, on_cancel_button_clicked):
        self._cancel_button_fn = on_cancel_button_clicked

    @property
    def progress(self):
        return self._progress_bar.model.progress

    @progress.setter
    def progress(self, value):
        self._progress_bar.model.set_value(value)

    @property
    def total_steps(self):
        return self._progress_bar.model.total_steps

    @total_steps.setter
    def total_steps(self, value):
        self._progress_bar.model.total_steps = value

    @property
    def status_text(self):
        return self._status_label.text

    @status_text.setter
    def status_text(self, value):
        self._status_label.text = value

    def show(self):
        self._popup.visible = True

    def hide(self):
        self._popup.visible = False

    def is_visible(self):
        return self._popup.visible

    def _on_cancel_button_fn(self):
        self.hide()
        if self._cancel_button_fn:
            self._cancel_button_fn()

    def _build_ui(self):
        self._popup = ui.Window(
            self._title, visible=False, auto_resize=True, height=0, dockPreference=ui.DockPreference.DISABLED
        )

        self._popup.flags = ui.WINDOW_FLAGS_NO_COLLAPSE | ui.WINDOW_FLAGS_NO_SCROLLBAR | ui.WINDOW_FLAGS_NO_RESIZE

        if self._modal:
            self._popup.flags = self._popup.flags | ui.WINDOW_FLAGS_MODAL

        with self._popup.frame:
            with ui.VStack(height=0, width=400):
                ui.Spacer(height=10)
                with ui.HStack(height=0):
                    ui.Spacer()
                    self._status_label = ui.Label(self._status_text, width=0, height=0)
                    ui.Spacer()
                ui.Spacer(height=10)
                with ui.HStack(height=0):
                    ui.Spacer(width=40)
                    self._progress_bar_model = CustomProgressModel()
                    self._progress_bar = ui.ProgressBar(
                        self._progress_bar_model, width=320, style={"color": 0xFFFF9E3D}
                    )
                    ui.Spacer(width=40)
                ui.Spacer(height=10)
                with ui.HStack(height=0):
                    ui.Spacer(height=0)
                    cancel_button = ui.Button(self._cancel_button_text, width=120, height=0)
                    cancel_button.set_clicked_fn(self._on_cancel_button_fn)
                    self._buttons.append(cancel_button)
                    ui.Spacer(height=0)
                ui.Spacer(width=0, height=10)
