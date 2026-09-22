from pathlib import Path

CURRENT_PATH = Path(__file__).parent
ICON_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.parent.joinpath("data").joinpath("tests")

UI_STYLE = {
    "Menu.Item.Icon::Sample": {"image_url": f"{ICON_PATH}/preferences_dark.svg"},
    "Menu.Button.Image::Sample": {"image_url": f"{ICON_PATH}/preferences_dark.svg"},
}
