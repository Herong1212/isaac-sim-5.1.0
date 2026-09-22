__all__ = ["ActionsWindowStyle"]
from omni.ui import color as cl
from pathlib import Path

CURRENT_PATH = Path(__file__).parent
ICON_PATH = CURRENT_PATH.parent.parent.parent.parent.joinpath("data").joinpath("icons")

VIEW_ROW_HEIGHT = 28

"""Style colors"""
# https://confluence.nvidia.com/pages/viewpage.action?pageId=1218553472&preview=/1218553472/1359943485/image2022-6-7_13-20-4.png
cl.actions_column_header_background = cl.shade(cl("#323434"))
cl.actions_text = cl.shade(cl("#848484"))
cl.actions_background = cl.shade(cl("#1F2123"))
cl.actions_background_hovered = cl.shade(cl("#2A2B2C"))
cl.actions_background_selected = cl.shade(cl("#77878A"))
cl.actions_item_icon_expand_background = cl.shade(cl('#9E9E9E'))
cl.actions_row_background = cl.shade(cl('#444444'))

ACTIONS_WINDOW_STYLE = {
    "ActionsView": {
        "background_color": cl.actions_background,
        "scrollbar_size": 10,
        "background_selected_color": 0x109D905C, # Same in stage window
        "secondary_selected_color": 0xFFB0703B, # column resize
        "secondary_color": cl.actions_text, # column splitter
    },
    "ActionsView:selected": {
        "background_color": cl.actions_background_selected,
    },
    "ActionsView.Row.Background": {"background_color": cl.actions_row_background},
    "ActionsView.Header.Background": {"background_color": cl.actions_column_header_background},
    "ActionsView.Header.Text": {"color": cl.actions_text, "margin": 4},
    "ActionsView.Item.Text": {"color": cl.actions_text, "margin": 4},
    "ActionsView.Item.Text:selected": {"color": cl.actions_background},
    "ActionsView.Item.Icon.Background": {"background_color": cl.actions_item_icon_expand_background, "border_radius": 2},
    "ActionsView.Item.Icon.Background:selected": {"background_color": cl.actions_background},
    "ActionsView.Item.Icon.Text": {"color": cl.actions_background},
    "ActionsView.Item.Icon.Text:selected": {"color": cl.actions_text},
}

HIGHLIGHT_LABEL_STYLE = {
    "HStack": {"margin": 4},
    "Label": {"color": cl.actions_text},
    "Label:selected": {"color": cl.actions_background},
}
