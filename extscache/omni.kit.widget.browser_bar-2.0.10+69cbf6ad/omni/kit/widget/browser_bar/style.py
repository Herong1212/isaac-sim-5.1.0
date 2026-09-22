# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""This module defines the style configurations for the omni.kit.widget.browser_bar, specifying UI styles for both light and dark themes."""


import omni.ui as ui
from pathlib import Path

CURRENT_PATH = Path(__file__).parent
ICON_PATH = CURRENT_PATH.parent.parent.parent.parent.joinpath("icons")

UI_STYLES = {}

UI_STYLES["NvidiaLight"] = {
    "Rectangle": {"background_color": 0xFF535354},
    "Button": {"background_color": 0xFFE0E0E0, "margin": 4, "padding": 0, "border_width": 0},
    "Button:hovered": {"background_color": 0xFFACACAF},
    "Button:selected": {"background_color": 0xFFACACAF},
    "Button:disabled": {"background_color": 0xFFE0E0E0},
    "Button.Image": {"color": 0xFF6E6E6E},
    "Button.Image:disabled": {"color": 0x0},
    "ComboBox": {"background_color": 0xFF535354, "selected_color": 0xFFACACAF, "color": 0xFFD6D6D6},
    "ComboBox:hovered": {"background_color": 0xFFACACAF},
    "ComboBox:selected": {"background_color": 0xFFACACAF},
}

UI_STYLES["NvidiaDark"] = {
    "Rectangle": {"background_color": 0xFF23211F},
    "Button": {"background_color": 0x0, "margin": 4, "padding": 0},
    "Button:disabled": {"background_color": 0x0},
    "Button.Image": {"color": 0xFFFFFFFF},
    "Button.Image:disabled": {"color": 0xFF888888},
    "ComboBox": {
        "background_color": 0xFF23211F,
        "selected_color": 0x0,
        "color": 0xFF4A4A4A,
        "border_radius": 0,
        "margin": 0,
        "padding": 4,
        "secondary_color": 0xFF23211F,
    },
    "ComboBox.Active": {
        "background_color": 0xFF23211F,
        "selected_color": 0xFF3A3A3A,
        "color": 0xFF9E9E9E,
        "border_radius": 0,
        "margin": 0,
        "padding": 4,
        "secondary_selected_color": 0xFF9E9E9E,
        "secondary_color": 0xFF23211F,
    },
    "ComboBox.Active:hovered": {
        "color": 0xFF4A4A4A,
        "secondary_color": 0x0,
    },
    "ComboBox.Active:pressed": {
        "color": 0xFF4A4A4A,
        "secondary_color": 0x0,
    },
    "ComboBox.Bg": {
        "background_color": 0x0,
        "margin": 0,
        "padding": 2,
    },
    "ComboBox.Bg.Active": {
        "background_color": 0x0,
        "margin": 0,
        "padding": 2,
    },
    "ComboBox.Bg.Active:hovered": {
        "background_color": 0xFF6E6E6E,
    },
    "ComboBox.Bg.Active:pressed": {
        "background_color": 0xFF6E6E6E,
    },
}
