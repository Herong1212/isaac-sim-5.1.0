__all__ = ["HOTKEYS_WINDOW_STYLE", "FILTER_WINDOW_STYLE", "WARNING_WINDOW_STYLE", "WINDOW_PICK_STYLE", "CONTEXT_MENU_STYLE"]
from pathlib import Path
import omni.ui as ui
from omni.ui import color as cl

# OM-63810: Happens in Create only which has different font from Kit.
# Must set height to big enough for Add Actions button
VIEW_ROW_HEIGHT = 28

CURRENT_PATH = Path(__file__).parent.absolute()
ICON_PATH = CURRENT_PATH.parent.parent.parent.parent.joinpath("data").joinpath("icons")

"""Style colors"""
# https://confluence.nvidia.com/pages/viewpage.action?pageId=1218553472&preview=/1218553472/1359943485/image2022-6-7_13-20-4.png
cl.hotkey_edit_icon = cl.shade(cl('#9E9E9E'))
cl.hotkey_hint = cl.shade(cl('#5A5A5A'))
cl.hotkey_warning = cl.shade(cl('#DFCB4A'))
cl.hotkey_text_active = cl.shade(cl('#CCCCCC'))
cl.hotkey_text_user = cl.shade(cl('#F2F2F2'))

HOTKEYS_WINDOW_STYLE = {
    "TreeView.Item:selected": {"color": 0xFF8A8777},
    "ActionsView.Window.Text": {"color": cl.actions_text, "margin": 4},
    "ActionsView.Item.Text::warning": {"color": cl.hotkey_warning},
    "Button.Background": {"background_color": 0x0},
    "Button::add": {"background_color": cl.actions_background, "stack_direction": ui.Direction.LEFT_TO_RIGHT, "border_radius": 4},
    "Button::add:hovered": {"background_color": cl.actions_background_hovered},
    "Button.Label::add": {"alignment": ui.Alignment.LEFT, "color": cl.actions_text},
    "Button.Image::add": {"image_url": f"{ICON_PATH}/add.svg", "color": 0xFF5E6C5F, "alignment": ui.Alignment.LEFT},

    "ComboBox": {
        "color": cl.actions_text,
        "secondary_color": cl.actions_background,
        "border_radius": 4,
        "margin": 1
    },

    "Image": {"border_radius": 4},
    "Field": {"border_radius": 4, "margin": 1},
    "Image::delete": {"image_url": f"{ICON_PATH}/delete.svg", "color": cl.hotkey_edit_icon},
    "Image::edit": {"image_url": f"{ICON_PATH}/edit.svg", "color": cl.hotkey_edit_icon},
    "Image::cancel": {"image_url": f"{ICON_PATH}/cancel.svg", "color": cl.hotkey_edit_icon},
    "Image::save": {"image_url": f"{ICON_PATH}/save.svg", "color": cl.hotkey_edit_icon},
    "Image::remove": {"image_url": f"{ICON_PATH}/remove.svg", "margin": 4},
    "Image::remove:hovered": {"image_url": f"{ICON_PATH}/remove-hovered.svg"},
    "DropDownArrow.background": {"border_radius": 4, "background_color": cl.actions_background, "margin_height": 1.5},
    "DropDownArrow": {"background_color": cl.hotkey_edit_icon, "margin": 4, "border_radius": 4},
    "Action.Input": {"color": cl.actions_text, "margin": 4},
    "Action.Input::hint": {"color": cl.hotkey_hint},

    "TriggerPressOption": {
        "background_color": 0x0,
        "margin_width": 2,
        "padding": 1,
        "stack_direction": ui.Direction.LEFT_TO_RIGHT,
        "spacing": 10
    },
    "TriggerPressOption.Label": {
        "alignment": ui.Alignment.LEFT,
    },
    "TriggerPressOption.Image": {
        "image_url": f"{ICON_PATH}/radio_off.svg",
    },
    "TriggerPressOption.Image:checked": {
        "image_url": f"{ICON_PATH}/radio_on.svg"
    },
    "TriggerPressOption.Background": {"background_color": 0x0},
    "TriggerPressOption.Background:hovered": {"background_color": cl.hotkey_background_hovered},

    "ResetButton.Invalid": {"background_color": 0xFF505050, "border_radius": 2},
    "ResetButton": {"background_color": 0xFFA07D4F, "border_radius": 2},

    "SearchBar.Filter": {
        "image_url": f"{ICON_PATH}/filter.svg",
        "margin": 4,
    },
    "SearchBar.Options": {
        "image_url": f"{ICON_PATH}/settings.svg",
        "color": cl.hotkey_edit_icon,
        "margin": 5,
    },
}

FILTER_WINDOW_STYLE = {
    "Window": {"padding": 0, "margin": 0},
    "Titlebar.Background": {"background_color": cl.actions_background},
    "Titlebar.Title": {"color": cl.actions_text},
    "Titlebar.Reset": {"background_color": 0},
    "Titlebar.Reset.Label": {"color": 0xFFB0703B},
    "CheckBox": {"background_color": cl.actions_text, "color": cl.actions_background},
    "FilterFlag.Text": {"color": cl.actions_text},
}

WARNING_WINDOW_STYLE = {
    "Window": {"secondary_background_color": 0x0},
    "Titlebar.Background": {"background_color": cl.actions_background},
    "Titlebar.Title": {"color": cl.actions_text},
    "Titlebar.Image": {"image_url": f"{ICON_PATH}/warning.svg"},
    "Warning.Text": {"color": cl.actions_text},
    "Warning.Text::highlight": {"color": cl.hotkey_text_active},
    "Warning.Button": {"background_color": cl.actions_background},
    "Warning.Button.Label": {"color": cl.hotkey_text_active},
}

WINDOW_PICK_STYLE = {
    "TreeView.Item": {
        "color": cl.actions_text, "margin": 4
    },
    "TreeView.Item:selected": {
        "color": cl.actions_background
    },
}

CONTEXT_MENU_STYLE = {
    "MenuItem": {"color": cl.actions_text},
}

HIGHLIGHT_LABEL_STYLE = {
    "HStack": {"margin": 4},
    "Label": {"color": cl.actions_text},
    "Label:selected": {"color": cl.actions_background},
}

HIGHLIGHT_LABEL_STYLE_USER = {
    "HStack": {"margin": 4},
    "Label": {"color": cl.hotkey_text_user},
    "Label:selected": {"color": cl.actions_background},
}
