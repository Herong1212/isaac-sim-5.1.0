from pathlib import Path

from omni import ui
from omni.ui import color as cl

CURRENT_PATH = Path(__file__).parent
ICON_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.joinpath("icons")


class Colors:
    Background = ui.color.shade(0xFF23211F, light=0xFF535354)
    Scrollbar = ui.color.shade(0xFF808080, light=0xFF9E9E9E)
    Selected = ui.color.shade(0xFFFFC734, light=0xFFC5911A)
    Text = ui.color.shade(0xFFA1A1A1, light=0xFFE0E0E0)
    DarkText = ui.color.shade(0xFF504F50, light=0xFFA1A1A1)
    Image = ui.color.shade(0xFFA8A8A8)
    Branch = ui.color.shade(cl(.36, .36, .36, 1.0))
    Expand = ui.color.shade(cl(.65, .65, .65, 1.0))



UI_STYLES = {
    # Collection combobox
    "CollectionList": {
        "background_color": Colors.Background,
        "selected_color": ui.color.shade(0xFF4C4A43, light=0xFF484848),
        "color": Colors.Text,
        "border_radius": 1,
    },
    # Category view
    "TreeView": {"background_color": 0, "background_selected_color": 0xFF6E6E6E},
    "TreeView:selected": {"background_color": 0, "secondary_color": 0},
    "TreeView.Frame": {
        "background_color": Colors.Background,
        "secondary_color": Colors.Scrollbar,
        "border_radius": 0,
        "scrollbar_size": 10,
    },
    "TreeView.Branch.Line": {
        "color": Colors.Branch,
        "background_color": Colors.Branch,
        "margin": 0,
    },
    # + and - signs
    "TreeView.Item": {
        "color": Colors.Expand,
        "border_width": 1.5,
        "border_color": Colors.Expand,
    },
    "TreeView.Item:selected": {"color": Colors.Expand},
    "TreeView.Item.Name": {"background_color": 0, "color": Colors.Text},
    "TreeView.Item.Name:selected": {"color": Colors.Selected},
    "TreeView.Item.Count": {"background_color": 0, "color": Colors.DarkText},
    "TreeView.Item.Count:selected": {"color": Colors.Text},
    "TreeView.Mark": {"color": 0, "border_width": 4},
    "TreeView.Mark:selected": {"color": Colors.Selected, "border_width": 4},

    # Detail view
    "GridView.Frame": {
        "background_color": Colors.Background,
        "secondary_color": Colors.Scrollbar,
        "border_radius": 0,
        "scrollbar_size": 10,
    },
    "GridView.Grid": {"background_color": 0},
    "GridView.Item": {"background_color": 0, "color": Colors.Text},
    "GridView.Image": {"border_width": 0},
    "GridView.Image:selected": {"border_width": 2, "border_color": Colors.Selected, "border_radius": 3.0},
    "GridView.Image.Placeholder": {"image_url": f"{ICON_PATH}/cloud_download.svg", "color": Colors.Image},
    # Overview view
    "CollapsableFrame": {"background_color": 0, "secondary_color": 0, "padding": 0, "margin": 0},
    "Overview.Frame": {"background_color": 0},
    "Overview.Header.Arrow": {"background_color": 0xFF929292},
    "Overview.Header.Label": {"color": 0xFF929292},
    "Overview.Header.Line": {"color": 0xFF707070},
    # Search bar
    "SearchBar.Button": {
        "background_color": 0,
        "padding": 3,
        "margin": 0,
        "stack_direction": ui.Direction.LEFT_TO_RIGHT,
    },
    "SearchBar.Button:hovered": {"background_color": 0xFF3A3A3A},
    "SearchBar.Button:pressed": {"background_color": Colors.Background},
    "SearchBar.Button:selected": {"background_color": Colors.Background},
    "SearchBar.Button.Image::navigation": {"image_url": f"{ICON_PATH}/navtree.svg", "color": Colors.Image},
    "SearchBar.Button.Image::options": {"image_url": f"{ICON_PATH}/options.svg", "color": Colors.Image},
    "SearchBar.Button.Label": {"color": 0xFFACACAC},
    "Splitter": {"background_color": 0, "margin_width": 0},
    "Splitter:hovered": {"background_color": 0xFFB0703B},
    "Splitter:pressed": {"background_color": 0xFFB0703B},
}
