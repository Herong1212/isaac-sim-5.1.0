from pathlib import Path
from omni import ui
from omni.ui import color as cl

CURRENT_PATH = Path(__file__).parent.absolute()
ICON_PATH = CURRENT_PATH.parent.parent.parent.parent.joinpath("icons")


class Colors:
    Background = ui.color.shade(0xFF23211F, light=0xFF535354)
    Border = ui.color.shade(0xFFC9974C)
    Hint = ui.color.shade(0xFF4A4A4A, light=0xFFD6D6D6)
    Hover = ui.color.shade(0xFF3A3A3A, light=0xFFB8B8B8)
    Close = ui.color.shade(0xFF858585)
    WordText = ui.color.shade(0xFF8D760D)
    WordBackground = ui.color.shade(0xFFD9D4BC)


UI_STYLE = {
    "SearchField": {
        "background_color": 0,
        "border_radius": 0,
        "border_width": 0,
        "background_selected_color": 0xFF535354,
    },
    "SearchField.Frame": {
        "background_color": Colors.Background,
        "border_radius": 0.0,
        "border_color": 0,
        "border_width": 2,
    },
    "SearchField.Frame:selected": {
        "background_color": Colors.Background,
        "border_radius": 0,
        "border_color": Colors.Border,
        "border_width": 2,
    },
    "SearchField.Hint": {"color": Colors.Hint},
    "SearchField.Search": {"image_url": f"{ICON_PATH}/search.svg", "color": Colors.Hint},
    "SearchField.Clear": {"background_color": 0x0, "padding": 4},
    "SearchField.Clear:hovered": {"background_color": Colors.Hover},
    "SearchField.Clear.Image": {"image_url": f"{ICON_PATH}/close.svg", "color": Colors.Close},
    "SearchField.Word": {"background_color": Colors.WordBackground},
    "SearchField.Word.Label": {"color": Colors.WordText},
    "SearchField.Word.Button": {"background_color": 0, "padding": 2},
    "SearchField.Word.Button.Image": {"image_url": f"{ICON_PATH}/close.svg", "color": Colors.WordText},

    "TreeView.Frame": {"background_color": 0xDD23211F, "border_color": 0xAA8A8777, "border_width": 0.5},
    "Tooltips.Spacer": {
        "background_color": 0x0,
        "color": 0x0,
        "alignment": ui.Alignment.LEFT,
        "padding": 0,
        "margin": 0,
    },
    "Tooltips.Item": {"background_color": 0, "padding": 4},
    "Tooltips.Item:hovered": {"background_color": cl("#77878A")},
    "Tooltips.Item:checked": {"background_color": cl("#77878A")},
    "Tooltips.Item.Label": {"color": cl("#9E9E9E"), "alignment": ui.Alignment.LEFT},
}
