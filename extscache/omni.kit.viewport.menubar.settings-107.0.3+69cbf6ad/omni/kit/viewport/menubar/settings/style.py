from pathlib import Path
from omni.ui import color as cl

CURRENT_PATH = Path(__file__).parent
ICON_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.joinpath("data").joinpath("icons")

UI_STYLE = {
    "Menu.Item.Icon::Settings": {"image_url": f"{ICON_PATH}/viewport_settings.svg"},
    "ResolutionLink": {"background_color": 0, "margin": 0, "padding": 2},
    "ResolutionLink.Image": {"image_url": f"{ICON_PATH}/link_dark.svg", "margin": 0},
    "ResolutionLink.Image:checked": {"image_url": f"{ICON_PATH}/link.svg"},
    "ComboBox::ratio": {"background_color": 0x0, "padding": 4, "margin": 0},
    "Menu.Item.Button::save": {"padding": 0, "margin": 0, "background_color": 0},
    "Menu.Item.Button.Image::save": {"image_url": f"{ICON_PATH}/save.svg", "color": cl.viewport_menubar_light},
    "Menu.Item.Button.Image::save:checked": {"color": cl.shade(cl("#0697cd"))},

    "Ratio.Background": {"background_color": 0xFF444444, "border_color": 0xFFA1701B, "border_width": 1},
    "Resolution.Text": {"color": cl.input_hint},
    "Resolution.Name": {"color": cl.viewport_menubar_light},
    "Resolution.Del": {"image_url": f"{ICON_PATH}/delete.svg"},
}


cl.save_background = cl.shade(cl("#1F2123"))
cl.input_hint = cl.shade(cl('#5A5A5A'))
SAVE_WINDOW_STYLE = {
    "Window": {"secondary_background_color": 0x0},
    "Titlebar.Background": {"background_color": cl.save_background},
    "Input.Hint": {"color": cl.input_hint},
    "Image::close": {"image_url": f"{ICON_PATH}/close.svg"},
    "Button": {"background_color": cl.save_background},
}
