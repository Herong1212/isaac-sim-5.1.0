# Base on ConnectorDialog in omni.kit.widget.nucleus_connector

import omni.ui as ui
import omni.client
import asyncio
import carb
from typing import Coroutine, Any
from omni.kit.window.popup_dialog import FormDialog, FormWidget, PopupDialog

from ..style import ICON_PATH

class Colors:
    """A class that defines a palette of colors for UI components.

    This class contains static attributes representing various colors used in the UI design, each defined as a shade with optional light variations. The colors include backgrounds, borders, button states, text, warnings, URLs, images, progress elements, and alert panes. They are meant to ensure consistency and theme coherence across the user interface.
    """

    Background = ui.color.shade(0xFF23211F, light=0xFF535354)
    Border = ui.color.shade(0xFFA1A1A1, light=0xFFE0E0E0)
    ButtonHovered = ui.color.shade(0xFF9A9A9A, light=0xFF9A9A9A)
    ButtonSelected = ui.color.shade(0xFF9A9A9A, light=0xFF9A9A9A)
    Text = ui.color.shade(0xFFA1A1A1, light=0xFFE0E0E0)
    TextWarn = ui.color.shade(0xFF3333A1, light=0xFF3333E0)
    Url = ui.color.shade(0xFFE8AD4B, light=0xFFE00000)
    Image = ui.color.shade(0xFFA8A8A8, light=0xFFA8A8A8)
    ProgressBackground = ui.color.shade(0xFF24211F, light=0xFF24211F)
    ProgressBorder = ui.color.shade(0xFF323434, light=0xFF323434)
    ProgressBar = ui.color.shade(0xFFC9974C, light=0xFFC9974C)
    AlertPaneBackground = ui.color.shade(0xFF3A3A3A, light=0xFF323434)
    InfoPaneBorder = ui.color.shade(0xFFC9974C, light=0xFFC9974C)
    WarningPaneBorder = ui.color.shade(0xFF318693, light=0xFF318693)

UI_STYLES = {
    "Dialog": {
        "background_color": Colors.Background,
        "margin_width": 8,
        "margin_height": 8,
    },
    "Image": {
        "background_color": 0x0,
        "margin": 0,
        "padding": 0,
        "color": Colors.Image,
        "alignment": ui.Alignment.CENTER,
    },
    "QrCode": {
        "background_color": 0x0,
        "margin": 10,
        "padding": 0,
        "alignment": ui.Alignment.CENTER,
    },
    "Image.Label": {"color": Colors.Text, "alignment": ui.Alignment.CENTER},
    "ProgressBar": {
        "background_color": Colors.ProgressBackground,
        "border_width": 2,
        "border_radius": 0,
        "border_color": Colors.ProgressBorder,
        "color": Colors.ProgressBar,
        "margin": 0,
        "padding": 0,
        "alignment": ui.Alignment.LEFT_CENTER,
    },
    "ProgressBar.Frame": {
        "background_color": 0xFF23211F,
        "margin": 0,
        "padding": 0,
    },
    "ProgressBar.Puck": {
        "background_color": Colors.ProgressBar,
        "margin": 2,
    },
    "StringField.Url": {
        "color": Colors.Url,
        "background_color": 0x0,
    },
    "Label": {"color": Colors.Text},
    "Label.Code": {
        "color": Colors.Text,
        "alignment": ui.Alignment.CENTER,
        "font_size": 40,
    },
    "Label.TimeRemaining": {"color": Colors.Url},
    "Label.Expired": {"color": Colors.TextWarn, "alignment": ui.Alignment.CENTER},
    "AlertPane": {
        "background_color": Colors.AlertPaneBackground,
        "color": Colors.Text,
        "margin": 0,
        "border_radius": 0.0,
    },
    "AlertPane::info": {
        "border_color": Colors.InfoPaneBorder,
        "border_width": 2,
    },
    "AlertPane::warn": {
        "border_color": Colors.WarningPaneBorder,
        "border_width": 2,
    },
    "AlertPane.Content": {"background_color": 0x0, "margin_width": 8, "margin_height": 12},
    "AlertPanePane.Clear": {
        "background_color": 0x0,
        "border_radius": 0.0,
        "border_color": Colors.Text,
        "border_width": 1,
        "margin": 0,
        "padding": 2,
    },
    "AlertPane.Clear:hovered": {"background_color": Colors.ButtonHovered},
    "AlertPane.Clear.Image": {"image_url": f"{ICON_PATH}/close.svg", "color": Colors.Text},
}

class AlertPane:
    """A class representing an alert pane within an application dialog.

    This pane can be used to display informational messages or warnings to the user in a stylized format.

    Args:
        width: int
            The width of the alert pane in pixels."""

    Info = 0
    Warn = 1

    def __init__(self, width: int = 400):
        self._widget: ui.Frame = None
        self._frame: ui.Frame = None
        self._icon_frame: ui.Frame = None
        self._label: ui.Label = None
        self._build_ui(width=width)

    def destroy(self):
        self._label = None
        self._frame = None
        self._widget = None

    def _build_ui(self, width: int = 400):
        self._widget = ui.Frame(visible=False, height=0)
        with self._widget:
            with ui.ZStack(width=width, style=UI_STYLES):
                self._frame = ui.Frame()
                with ui.HStack(spacing=4, style_type_name_override="AlertPane.Content"):
                    self._icon_frame = ui.Frame()
                    self._label = ui.Label("", height=20, word_wrap=True, style_type_name_override="Label")

    def show(self, msg: str = "", alert_type: int = 0):
        if self._widget:
            with self._frame:
                style_name = "warn" if alert_type == AlertPane.Warn else "info"
                ui.Rectangle(style_type_name_override="AlertPane", name=style_name)
            with self._icon_frame:
                icon = f"{ICON_PATH}/warn.svg" if alert_type == AlertPane.Warn else f"{ICON_PATH}/info.svg"
                ui.ImageWithProvider(
                    icon,
                    width=16,
                    height=16,
                    fill_policy=ui.IwpFillPolicy.IWP_PRESERVE_ASPECT_FIT,
                    style_type_name_override="Image",
                )
            if self._label:
                self._label.text = msg
            self._widget.visible = True

    def hide(self):
        if self._widget:
            self._widget.visible = False


class S3ConnectorDialog(PopupDialog):
    """The main connection dialog for establishing Nucleus connections.

    This dialog provides a user interface to add new Omniverse connections with an optional name. It manages the UI elements and tasks associated with the connection process, such as displaying progress, handling cancellations, and showing alerts.
    """

    def __init__(self):
        super().__init__(width=400, title="Add S3 connection", ok_label="Ok", cancel_label="Cancel", modal=True)
        self._form_widget = None
        self._progress_bar = None
        self._alert_pane = None
        self._task = None
        self._build_ui()

    def _build_ui(self):
        field_defs = [
            FormDialog.FieldDef("url", "https://  ", ui.StringField, "", True),
            FormDialog.FieldDef("name", "Optional Name:  ", ui.StringField, ""),
        ]
        with self._window.frame:
            with ui.VStack(style=UI_STYLES, style_type_name_override="Dialog"):
                # OM-81873: This is a temporary solution for the authentication dialog; add the form widget in a frame
                #  so that it could be easily hidden/shown
                self._form_frame = ui.Frame()
                with self._form_frame:
                    self._form_widget = FormWidget("Add a new connection with optional name.", field_defs)
                self._alert_pane = AlertPane(width=self._window.width - 24)
                self._build_ok_cancel_buttons()
        self.hide()
        self.set_cancel_clicked_fn(lambda _: self._on_cancel_fn())

    def _on_cancel_fn(self):
        self.cancel_task()
        self.hide()

    def get_value(self, name: str) -> str:
        if self._form_widget:
            return self._form_widget.get_value(name)
        return None

    def set_value(self, name: str, value: str):
        if self._form_widget:
            field = self._form_widget.get_field(name)
            if field:
                field.model.set_value(value or "")

    def destroy(self):
        self.cancel_task()
        if self._form_widget:
            self._form_widget.destroy()
            self._form_widget = None
        if self._form_frame:
            self._form_frame = None
        self._progress_bar = None
        if self._alert_pane:
            self._alert_pane.destroy()
            self._alert_pane = None
        super().destroy()

    def __del__(self):
        self.destroy()

    async def run_cancellable_task(self, task: Coroutine) -> Any:
        """Manages running and cancelling the given task"""
        if self._task:
            self.cancel_task()
        self._task = asyncio.create_task(task)

        try:
            return await self._task
        except asyncio.CancelledError:
            carb.log_info(f"Cancelling task ... {self._task}")
            raise
        except Exception as e:
            raise
        finally:
            self._task = None

    def cancel_task(self):
        """Cancels the managed task"""
        if self._task is not None:
            self._task.cancel()
        self._task = None

    @property
    def frame(self):
        return self._window.frame

    @property
    def visible(self) -> bool:
        if self._window:
            return self._window.visible
        return False

    def show(self, name: str = None, url: str = None):
        """Shows the dialog after resetting to a default state"""
        broken_url = omni.client.break_url(url or "")
        # TODO: does this could easy to expand to other kind of url?
        # it's not make sense to write connection dialog for every different kind of url
        host = broken_url.host if broken_url.scheme == "https" else None
        self.set_value("url", host)
        self.set_value("name", name)
        if self._alert_pane:
            self._alert_pane.hide()
        if not self._okay_button:
            self._build_ok_cancel_buttons()
        self._okay_button.enabled = True
        self._cancel_button.enabled = True
        self._okay_button.visible = True
        if self._form_frame:
            self._form_frame.visible = True

        self._window.visible = True

        # focus fields on show
        if self._form_widget:
            self._form_widget.focus()

    def hide(self):
        self._window.visible = False
        # reset window title on hide; authentication mode might have reset the window title.
        self._window.title = self._title

    def show_alert(self, msg: str = "", alert_type: int = 0):
        # hide form widget and OK button
        if self._okay_button:
            self._okay_button.visible = False
            # Disable apply button
            self._okay_button.enabled = False
        if self._form_frame:
            self._form_frame.visible = False

        if self._alert_pane:
            self._alert_pane.show(msg, alert_type=alert_type)
        if self._progress_bar:
            self._progress_bar.hide()
        self._window.visible = True
