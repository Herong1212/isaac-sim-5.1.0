# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from functools import lru_cache

from omni.ui import color as cl
from omni.ui import constant as fl


MENU_TITLE = cl.shade(cl("#25282A"))
MENU_BACKGROUND = cl.shade(cl("#25282ACC"))
MENU_MEDIUM = cl.shade(cl("#6E6E6E"))
MENU_LIGHT = cl.shade(cl("#D6D6D6"))
MENU_SELECTION = cl.shade(cl("#34C7FF3B"))
MENU_SELECTION_BORDER = cl.shade(cl("#34C7FF"))
MENU_ITEM_CHECKMARK_COLOR = cl.shade(cl("#34C7FF"))
MENU_ITEM_MARGIN = fl.shade(5)
MENU_ITEM_MARGIN_HEIGHT = fl.shade(3)

MENU_STYLE = {
    "Menu.Title": {"color": MENU_TITLE, "background_color": 0x0},
    "Menu.Title:hovered": {
        "background_color": MENU_SELECTION,
        "border_width": 1,
        "border_color": MENU_SELECTION_BORDER,
    },
    "Menu.Title:pressed": {"background_color": MENU_SELECTION},
    "Menu.Item": {
        "color": MENU_LIGHT,
        "margin_width": MENU_ITEM_MARGIN,
        "margin_HEIGHT": MENU_ITEM_MARGIN_HEIGHT,
    },
    "Menu.Item.CheckMark": {"color": MENU_ITEM_CHECKMARK_COLOR},
    "Menu.Separator": {
        "color": MENU_MEDIUM,
        "margin_HEIGHT": MENU_ITEM_MARGIN_HEIGHT,
        "border_width": 1.5,
    },
    "Menu.Window": {
        "background_color": MENU_BACKGROUND,
        "border_width": 0,
        "border_radius": 0,
        "background_selected_color": MENU_SELECTION,
        "secondary_padding": 1,
        "secondary_selected_color": MENU_SELECTION_BORDER,
        "margin": 2,
    },
    "MenuItem": {
        "background_selected_color": MENU_SELECTION,
        "secondary_padding": 1,
        "secondary_selected_color": MENU_SELECTION_BORDER,
    },
}
