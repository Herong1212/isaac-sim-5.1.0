from pathlib import Path

from omni.ui import color as cl

AGENT_SDG_STYLE = {
    "ActionsView": {
        "background_color": cl.actions_background,
        "scrollbar_size": 10,
        "background_selected_color": 0x109D905C,  # Same in stage window
        "secondary_selected_color": 0xFFB0703B,  # column resize
        "secondary_color": cl.actions_text,  # column splitter
    },
    "ActionsView:selected": {
        "background_color": cl.actions_background_selected,
    },
    "ActionsView.Row.Background": {"background_color": cl.actions_row_background},
    "ActionsView.Header.Background": {"background_color": cl.actions_column_header_background},
    "ActionsView.Header.Text": {"color": cl.actions_text, "margin": 4},
    "ActionsView.Item.Text": {"color": cl.actions_text, "margin": 4},
    "ActionsView.Item.Text:selected": {"color": cl.actions_background},
    "ActionsView.Item.Icon.Background": {
        "background_color": cl.actions_item_icon_expand_background,
        "border_radius": 2,
    },
    "ActionsView.Item.Icon.Background:selected": {"background_color": cl.actions_background},
    "ActionsView.Item.Icon.Text": {"color": cl.actions_background},
    "ActionsView.Item.Icon.Text:selected": {"color": cl.actions_text},
}
