"""This module defines the style options for the options menu widget in the Omni Kit UI, including colors, margins, and icons."""

from pathlib import Path
import omni.ui as ui
from omni.ui import color as cl

CURRENT_PATH = Path(__file__).parent.absolute()
ICON_PATH = CURRENT_PATH.parent.parent.parent.parent.joinpath(f"data/icons")

OPTIONS_MENU_STYLE = {
    "Title.Background": {"background_color": 0xFF23211F, "corner_flag": ui.CornerFlag.TOP, "margin": 0},
    "Title.Header": {"margin_width": 3, "margin_height": 0},
    "Title.Label": {"background_color": 0x0, "color": cl.shade(cl("#A1A1A1")), "margin_width": 5},
    "ResetButton": {"background_color": 0},
    "ResetButton:hovered": {"background_color": cl.shade(cl("323434"))},
    "ResetButton.Label": {"color": cl.shade(cl("#34C7FF"))},
    "ResetButton.Label:disabled": {"color": cl.shade(cl("#6E6E6E"))},
    "ResetButton.Label:hovered": {"color": cl.shade(cl("#1A91C5"))},
    "MenuItem.Icon": {"image_url": f"{ICON_PATH}/check_solid.svg", "color": 0, "margin": 7},
    "MenuItem.Icon:checked": {"color": cl.shade(cl("#34C7FF"))},
    "MenuItem.Icon:selected": {"color": cl.shade(cl("#1F2123"))},
    "MenuItem.Icon::disabled:disabled": {"color": cl.shade(cl("#6E6E6E")), "margin": 7},
    "MenuItem.Radio": {"image_url": f"{ICON_PATH}/radiomark.svg", "color": 0, "margin": 7},
    "MenuItem.Radio:checked": {"color": cl.shade(cl("#34C7FF"))},
    "MenuItem.Radio:selected": {"color": cl.shade(cl("#1F2123"))},
    "MenuItem.Label::title": {"color": cl.shade(cl("#A1A1A1")), "margin_width": 5},
    "MenuItem.Label:disabled": {"color": cl.shade(cl("#6E6E6E"))},
    "MenuItem.Separator": {"color": cl.shade(cl("#626363")), "border_width": 1.5},
}
