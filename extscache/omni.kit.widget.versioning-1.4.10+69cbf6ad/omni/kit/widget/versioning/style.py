# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import carb
import omni.ui as ui

from .extension import get_icons_path


def get_style():
    style = carb.settings.get_settings().get("/persistent/app/window/uiStyle")
    if not style:
        style = "NvidiaDark"

    FONT_SIZE = 14.0

    if style == "NvidiaLight":  # pragma: no cover -- unused style
        WIDGET_BACKGROUND_COLOR = 0xFF454545
        BUTTON_BACKGROUND_COLOR = 0xFF545454
        BUTTON_FONT_COLOR = 0xFFD6D6D6
        INPUT_BACKGROUND_COLOR = 0xFF454545
        INPUT_FONT_COLOR = 0xFFD6D6D6
        INPUT_HINT_COLOR = 0xFF9E9E9E
        CARD_BACKGROUND_COLOR = 0xFF545454
        CARD_HOVERED_COLOR = 0xFF6E6E6E
        CARD_SELECTED_COLOR = 0xFFBEBBAE
        CARD_FONT_COLOR = 0xFFD6D6D6
        CARD_SEPARATOR_COLOR = 0x44D6D6D6
        MENU_BACKGROUND_COLOR = 0xFF454545
        MENU_FONT_COLOR = 0xFFD6D6D6
        MENU_SEPARATOR_COLOR = 0x44D6D6D6
        NOTIFICATION_BACKGROUND_COLOR = 0xFF545454
        NOTIFICATION_FONT_COLOR = 0xFFD6D6D6
        TREEVIEW_BACKGROUND_COLOR = 0xFF545454
        TREEVIEW_ITEM_COLOR = 0xFFD6D6D6
        TREEVIEW_HEADER_BACKGROUND_COLOR = 0xFF545454
        TREEVIEW_HEADER_COLOR = 0xFFD6D6D6
        TREEVIEW_SELECTED_COLOR = 0x109D905C
    else:
        WIDGET_BACKGROUND_COLOR = 0xFF343432
        BUTTON_BACKGROUND_COLOR = 0xFF23211F
        BUTTON_FONT_COLOR = 0xFF9E9E9E
        INPUT_BACKGROUND_COLOR = 0xFF23211F
        INPUT_FONT_COLOR = 0xFF9E9E9E
        INPUT_HINT_COLOR = 0xFF4A4A4A
        CARD_BACKGROUND_COLOR = 0xFF23211F
        CARD_HOVERED_COLOR = 0xFF3A3A3A
        CARD_SELECTED_COLOR = 0xFF8A8777
        CARD_FONT_COLOR = 0xFF9E9E9E
        CARD_SEPARATOR_COLOR = 0x449E9E9E
        MENU_BACKGROUND_COLOR = 0xFF343432
        MENU_FONT_COLOR = 0xFF9E9E9E
        MENU_SEPARATOR_COLOR = 0x449E9E9E
        NOTIFICATION_BACKGROUND_COLOR = 0xFF343432
        NOTIFICATION_FONT_COLOR = 0xFF9E9E9E
        TREEVIEW_BACKGROUND_COLOR = 0xFF23211F
        TREEVIEW_ITEM_COLOR = 0xFF9E9E9E
        TREEVIEW_HEADER_BACKGROUND_COLOR = 0xFF343432
        TREEVIEW_HEADER_COLOR = 0xFF9E9E9E
        TREEVIEW_SELECTED_COLOR = 0x664F4D43

    style = {
        "Window": {"secondary_background_color": 0},
        "ScrollingFrame": {"background_color": WIDGET_BACKGROUND_COLOR, "margin_width": 0},
        "ComboBox": {"background_color": BUTTON_BACKGROUND_COLOR, "color": BUTTON_FONT_COLOR},
        "ComboBox.Field": {"background_color": INPUT_BACKGROUND_COLOR, "color": INPUT_FONT_COLOR},
        "ComboBox.Field::hint": {"background_color": 0x0, "color": INPUT_HINT_COLOR},
        "Card": {"background_color": CARD_BACKGROUND_COLOR, "color": CARD_FONT_COLOR, "margin_height": 1, "border_width": 2},
        "Card:hovered": {"background_color": CARD_HOVERED_COLOR, "border_color": CARD_HOVERED_COLOR, "border_width": 2},
        "Card:pressed": {"background_color": CARD_HOVERED_COLOR, "border_color": CARD_HOVERED_COLOR, "border_width": 2},
        "Card:selected": {"background_color": CARD_SELECTED_COLOR, "border_color": CARD_SELECTED_COLOR, "border_width": 2},
        "Card.Label": {"background_color": 0x0, "color": CARD_FONT_COLOR, "margin_width": 4},
        "Card.Label:selected": {"background_color": 0x0, "color": CARD_BACKGROUND_COLOR, "margin_width": 4},
        "Card.Separator": {"background_color": 0x0, "color": CARD_SEPARATOR_COLOR},
        "Menu": {"background_color": MENU_BACKGROUND_COLOR, "color": MENU_FONT_COLOR, "border_radius": 2},
        "Menu.Item": {"background_color": 0x0, "margin": 0},
        "Menu.Separator": {"background_color": 0x0, "color": MENU_SEPARATOR_COLOR, "alignment": ui.Alignment.CENTER},
        "Notification": {"background_color": NOTIFICATION_BACKGROUND_COLOR, "margin_width": 0},
        "Notification.Label": {"background_color": 0x0, "color": NOTIFICATION_FONT_COLOR, "alignment": ui.Alignment.CENTER_TOP},
        "TreeView": {"background_color": 0x0},
        "TreeView.Background": {"background_color": TREEVIEW_BACKGROUND_COLOR},
        "TreeView.Header": {"background_color": TREEVIEW_HEADER_BACKGROUND_COLOR, "color": TREEVIEW_HEADER_COLOR},
        "TreeView.Header::label": {"margin": 4},
        "TreeView.Item": {"margin":4, "background_color": 0x0, "color": TREEVIEW_ITEM_COLOR},
        "TreeView.Item:selected": {"margin":4, "color": TREEVIEW_SELECTED_COLOR},

    }
    return style
