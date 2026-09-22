from pathlib import Path

CURRENT_PATH = Path(__file__).parent
ICON_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.joinpath("data").joinpath("icons")

UI_STYLE = {"Menu.Item.Icon::Display": {"image_url": f"{ICON_PATH}/viewport_visibility.svg"}}
