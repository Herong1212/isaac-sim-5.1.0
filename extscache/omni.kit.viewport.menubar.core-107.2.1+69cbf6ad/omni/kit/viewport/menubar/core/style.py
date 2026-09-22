from pathlib import Path

import omni.ui as ui
from omni.ui import color as cl
from omni.ui import constant as fl

DEFAULT_MENUBAR_NAME: str = "__DEFAULT__MENUBAR__"
"""Name of default menubar"""

CURRENT_PATH = Path(__file__).parent
ICON_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.joinpath("data").joinpath("icons")

VIEWPORT_MENUBAR_STYLE: dict = {
    "Menu.Title": {"color": cl.viewport_menubar_title, "background_color": cl.viewport_menubar_title_background},
    "Menu.Title:hovered": {
        "background_color": cl.viewport_menubar_selection,
        "border_width": 1,
        "border_color": cl.viewport_menubar_selection_border,
    },
    "Menu.Title:pressed": {"background_color": cl.viewport_menubar_selection},
    "Menu.Item": {
        "color": cl.viewport_menubar_light,
        "margin_width": fl.viewport_menubar_item_margin,
        "margin_height": fl.viewport_menubar_item_margin_height,
    },
    "MenuBar.Window": {
        "background_color": cl.viewport_menubar_background,
        "border_width": 0,
        "border_radius": 0,
    },
    "MenuBar.Item": {
        "color": cl.viewport_menubar_light,
        "padding": 0,
        "margin_width": fl.viewport_menubar_item_margin,
        "margin_height": fl.viewport_menubar_item_margin,
    },
    "MenuBar.Item::menubar": {
        "color": cl.viewport_menubar_light,
        "padding": 0,
        "margin_width": 0,
        "margin_height": 0,
    },
    "MenuBar.Item.Background": {
        "background_color": cl.viewport_menubar_background,
        "border_radius": cl.viewport_menubar_border_radius,
        "padding": 1,
        "margin": 2,
    },

    "Menu.Item.Background": {
        "background_color": cl.viewport_menubar_background,
        "border_radius": cl.viewport_menubar_border_radius,
        "padding": 0,
        "margin_width": 0,
        "margin_height": 2,
    },
    "Menu.Item.CloseMark": {
        "color": 0x0,
    },
    "Menu.Item.CloseMark:checked": {
        "color": cl.viewport_menubar_light,
    },
    "MenuBar.Item.Triangle": {"background_color": cl.viewport_menubar_light},
    "Menu.Separator": {
        "color": cl.viewport_menubar_medium,
        "margin_height": fl.viewport_menubar_item_margin_height,
        "border_width": 1.5,
    },
    "Menu.Item.Separator": {
        "color": cl.viewport_menubar_medium,
        "margin_height": fl.viewport_menubar_item_margin_height,
        "border_width": 20,
    },
    "Menu.Window": {
        "background_color": cl.viewport_menubar_background,
        "border_width": 0,
        "border_radius": 0,
        "background_selected_color": cl.viewport_menubar_selection,
        "secondary_padding": 1,
        "secondary_selected_color": cl.viewport_menubar_selection_border,
        "margin": 2,
    },

    "MenuItem": {
        "background_selected_color": cl.viewport_menubar_selection,
        "secondary_padding": 1,
        "secondary_selected_color": cl.viewport_menubar_selection_border,
    },
    "Slider": {
        "border_radius": 100,
        "border_width": 1,
        "border_color": cl.viewport_menubar_medium,
        "background_color": cl(1, 1, 1, 0),
        "color": cl.viewport_menubar_light,
        "secondary_color": cl.viewport_menubar_medium,
        "draw_mode": ui.SliderDrawMode.FILLED,
        "padding": 0,
    },
    "Slider:disabled": {"color": cl.viewport_menubar_medium},
    "Menu.Item.Label": {"color": cl.viewport_menubar_light, "margin_width": fl.viewport_menubar_item_margin},
    "Menu.Item.Label:disabled": {"color": cl.viewport_menubar_medium},
    "Menu.Item.Text": {"color": cl.viewport_menubar_light},
    "Menu.Item.Text:disabled": {"color": cl.viewport_menubar_medium},
    "Menu.Item.Icon": {
        "image_url": f"{ICON_PATH}/none.svg",
        "color": 0xFFD6D6D6,
        "padding": 0,
        "margin_width": 2,
        "margin_height": 2,
    },
    "Menu.Item.Icon:selected": {"image_url": f"{ICON_PATH}/check_solid.svg"},
    "Menu.Item.RadioMark": {
        "image_url": f"{ICON_PATH}/radiomark.svg",
        "color": cl.viewport_menubar_selection_border,
        "margin_width": fl.viewport_menubar_item_margin,
    },
    "Menu.Item.Status": {
        "image_url": f"{ICON_PATH}/none.svg",
        "color": cl.viewport_menubar_selection_border,
        "margin_width": fl.viewport_menubar_item_margin,
    },
    "Menu.Item.Status:checked": {"image_url": f"{ICON_PATH}/radiomark.svg"},
    "Menu.Item.Status:selected": {"image_url": f"{ICON_PATH}/check_solid.svg"},
    "Menu.Item.Status::Category.None": {"image_url": f"{ICON_PATH}/none.svg"},
    "Menu.Item.Status::Category.All": {"image_url": f"{ICON_PATH}/check_solid.svg"},
    "Menu.Item.Status::Category.Mixed": {"image_url": f"{ICON_PATH}/mixed_checkbox.svg", "margin_width": 2},
    "ComboBox": {
        "background_color": 0x0,
        "secondary_color": 0x0,
        "color": cl.viewport_menubar_light,
        "secondary_selected_color": cl.viewport_menubar_light,
        "secondary_background_color": cl.viewport_menubar_background,
        "selected_color": cl.viewport_menubar_selection,
        "padding": 4,
        "font_size": 14,
    },
    "ComboBox:disabled": {"color": cl.viewport_menubar_medium},
    "CheckBox": {"border_radius": 1},
    "CheckBox:disabled": {"background_color": cl.viewport_menubar_medium},
    "Label": {"color": cl.viewport_menubar_light},
    "Menu.Button": {
        "color": cl.viewport_menubar_selection_border,
        "background_color": 0,
        "padding": 0,
        "margin_width": fl.viewport_menubar_item_margin,
        "margin_height": fl.viewport_menubar_item_margin_height,
        "stack_direction": ui.Direction.LEFT_TO_RIGHT,
    },
    "Menubar.Hover": {
        "background_color": 0,
        "padding": 1,
        "margin": 1,
    },
    "Menubar.Hover:hovered": {
        "background_color": cl.viewport_menubar_selection,
        "border_color": cl.viewport_menubar_selection_border_button,
        "border_width": 1.5
    },
    "Menubar.Hover:pressed": {
        "background_color": cl.viewport_menubar_selection,
        "border_color": cl.viewport_menubar_selection_border_button,
        "border_width": 1.5
    },

    "Rectangle::reset_invalid": {"background_color": 0xFF505050, "border_radius": 2},
    "Rectangle::reset": {"background_color": 0xFFA07D4F, "border_radius": 2},
}
"""Default style of menu bar"""


VIEWPORT_PREFERENCE_STYLE = {
    "TreeView.Frame": {"background_color": 0xFF343432, "padding": 10},
    "TreeView.Item.Label": {"color": 0xFF9E9E9E},
    "TreeView.Item.Line": {"color": 0x338A8777},
    "TreeView.Item.CheckBox": {"font_size": 10, "background_color": 0xFF9E9E9E, "color": 0xFF23211F, "border_radius": 0},
    "TreeView.Item.ComboBox": {"color": 0xFF9E9E9E, "secondary_color": 0xFF23211F, "border_radius": 0},
    "TreeView.Item.Alignment::left": {"image_url": f"{ICON_PATH}/align_left.svg"},
    "TreeView.Item.Alignment::left:checked": {"image_url": f"{ICON_PATH}/align_disabled_left.svg"},
    "TreeView.Item.Alignment::right": {"image_url": f"{ICON_PATH}/align_right.svg"},
    "TreeView.Item.Alignment::right:checked": {"image_url": f"{ICON_PATH}/align_disabled_right.svg"},
    "TreeView:drop": {"border_color": 0xFFC5911A, "background_selected_color": 0x0},
}
