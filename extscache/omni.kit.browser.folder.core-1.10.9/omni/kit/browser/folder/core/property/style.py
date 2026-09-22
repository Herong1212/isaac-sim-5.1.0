from pathlib import Path

import omni.ui as ui

CURRENT_PATH = Path(__file__).parent
ICON_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.parent.joinpath("data/icons")

PROPERTY_STYLES = {
    "PropertyToolBar.Button": {"background_color": 0x0, "padding": 3, "margin": 0},
    "PropertyToolBar.Button:selected": {"background_color": ui.color.shade(0xFF23211F, light=0xFF535354)},
    "Splitter": {"background_color": 0x0, "margin_width": 0},
    "Splitter:hovered": {"background_color": 0xFFB0703B},
    "Splitter:pressed": {"background_color": 0xFFB0703B},
}