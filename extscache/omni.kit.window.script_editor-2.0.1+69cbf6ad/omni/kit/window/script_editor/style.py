from pathlib import Path

import omni.ui as ui
from omni.ui import color as cl
from omni.ui import constant as fl

CURRENT_PATH = Path(__file__).parent
ICON_PATH = CURRENT_PATH.parent.parent.parent.parent.joinpath("data").joinpath("icons")

WINDOW_STYLE = {
    "Menu.Title": {"color": 0xFFFF0000, "background_color": 0xFF00FF00},
    "LogView": {
        "background_color": cl.shade(0xFF2E2B28),
    },
    "LogView.Item.Text": {"font_size": fl.script_editor_font_size},
    "LogView.Item.Text::command": {"color": cl.shade(0xB2FFFFFF)},
    "LogView.Item.Text::information": {"color": cl.shade(0xFFFFFFFF)},
    "LogView.Item.Text::error": {"color": cl.shade(0xFFAAB1F6)},
    "Separator": {"color": 0xFF000000},
    "Tab.Header.Background": {"background_color": 0xFF333333, "border_radius": 1},
    "Tab.Header.Background:selected": {"background_color": 0xFF000000},
    "Tab.Header.Label": {"margin_height": 4, "font_size": fl.script_editor_font_size},
    "Tab.Header.Label::transparent": {"color": 0},
    "Tab.Header.Circle": {"background_color": 0xFF9B9B9B},
    "Tab.Header.Image::close": {"image_url": f"{ICON_PATH}/close.svg"},
    "Button": {"border_radius": 4, "padding": 5},
    "TextEditor": {"font_size": fl.script_editor_font_size},
}

MENU_STYLE = {
    "Menu.Window": {"background_color": 0xFF3D3B38, "padding": 0, "border_radius": 4},
    "MenuBar.Item": {
        "margin_width": 6,
        "margin_height": 4,
    },
    "Menu.Title": {"background_color": 0xFF2A2825, "border_radius": 4, "corner_flag": ui.CornerFlag.TOP},
    "Menu.Title.Line": {"color": 0xFF373635},
    "Menu.Separator": {"color": 0xFF707070, "margin_width": 6},
    "Menu.Item": {"color": 0xFFCCCCCC, "margin_height": 2, "margin_width": 4},
    "Menu.Item:disabled": {"color": 0xFF6F6F6F},
    "Menu.Item.CheckMark": {
        "color": 0xFFCCCCCC,
        "margin_width": 5,
        "image_url": "${kit}/resources/icons/RenderCheckMark.svg",
    },
    "Menu.Item.CheckMark:disabled": {"color": 0xFF6F6F6F},
    "Menu.Item.ExpandMark": {
        "color": 0xFFCCCCCC,
        "margin_width": 5,
        "image_url": "${kit}/resources/icons/ExpandMark.svg",
    },
    "Menu.Item.ExpandMark:disabled": {"color": 0xFF6F6F6F},
    "Menu.Item.CloseMark": {"color": 0, "margin": 3, "image_url": "${kit}/resources/icons/CloseMark.svg"},
    "Menu.Item.CloseMark:checked": {"color": 0xFFCCCCCC},
}
