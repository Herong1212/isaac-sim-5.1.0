"""This module defines a set of UI styles and color palettes for components in the omni.kit.widget.nucleus_connector package, providing consistency and theming across the user interface."""

from omni import ui
from pathlib import Path

CURRENT_PATH = Path(__file__).parent
DATA_PATH = CURRENT_PATH.parent.parent.parent.parent.joinpath("data")
ICON_PATH = DATA_PATH.joinpath("icons")


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
