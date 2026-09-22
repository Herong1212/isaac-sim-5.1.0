from pathlib import Path

from omni import ui
from omni.ui import color as cl

CURRENT_PATH = Path(__file__).parent.absolute()
ICON_PATH = CURRENT_PATH.parent.parent.parent.parent.joinpath(f"data/icons")

UI_STYLE = {
    "OptionsButton": {"background_color": 0, "margin_width": 0, "padding": 4, "border_radius": 2},
    "OptionsButton:selected": {"background_color": cl.shade(cl('#23211F'))},
    "OptionsButton.Image": {
        "background_color": 0x0,
        "color": cl.shade(cl('#A8A8A8')),
        "image_url": f"{ICON_PATH}/settings.svg",
        "alignment": ui.Alignment.CENTER,
    },
    "OptionsButton.Image:selected": {
        "color": cl.shade(cl('#34C7FF')),
    },
    "OptionsButton:hovered": {"background_color": 0xFF6E6E6E},
}
