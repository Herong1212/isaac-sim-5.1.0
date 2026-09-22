from pathlib import Path

CURRENT_PATH = Path(__file__).parent
ICON_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.joinpath("data").joinpath("icons")

UI_STYLE = {
    "Menu.Item.Icon::Renderer": {
        "image_url": f"{ICON_PATH}/viewport_renderer.svg"
    },
    "Menu.Item.Button": {
        "background_color": 0,
        "margin": 0,
        "padding": 0,
    },
    "Menu.Item.Button.Image::OptionBox": {
        "image_url": f"{ICON_PATH}/settings_submenu.svg"
    },
}
