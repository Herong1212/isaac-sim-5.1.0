# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from omni.ui import color as cl

from typing import Dict


def abgr_to_color(abgr: int) -> cl:
    # cl in rgba order
    return cl((abgr & 0xFF) / 255, (abgr >> 8 & 0xFF) / 255, (abgr >> 16 & 0xFF) / 255, (abgr >> 24 & 0xFF) / 255)


# style is nested dict, can't simply call to_style.update(from_style)
def update_style(to_style: Dict, from_style: Dict):
    if from_style:
        for k, v in from_style.items():
            if isinstance(v, dict):
                to_style[k] = update_style(to_style.get(k, {}), v)
            else:
                to_style[k] = v
    return to_style


def get_navpath_default_style():
    COLOR_X = 0xFF6060AA
    COLOR_Y = 0xFF76A371
    COLOR_Z = 0xFFA07D4F
    COLOR_SCREEN = 0x8AFEF68E
    COLOR_FREE = 0x40404040

    return {
        "Translate.Axis::x": {"color": COLOR_X},
        "Translate.Axis::y": {"color": COLOR_Y},
        "Translate.Axis::z": {"color": COLOR_Z},
        "Translate.Plane::x_y": {"color": COLOR_Z},
        "Translate.Plane::y_z": {"color": COLOR_X},
        "Translate.Plane::z_x": {"color": COLOR_Y},
        "Translate.Point": {"color": COLOR_SCREEN, "type": "point"},
        "Rotate.Arc::x": {"color": COLOR_X},
        "Rotate.Arc::y": {"color": COLOR_Y},
        "Rotate.Arc::z": {"color": COLOR_Z},
        "Rotate.Arc::screen": {"color": COLOR_SCREEN},
        "Rotate.Arc::free": {"color": COLOR_FREE},
        "Scale.Axis::x": {"color": COLOR_X},
        "Scale.Axis::y": {"color": COLOR_Y},
        "Scale.Axis::z": {"color": COLOR_Z},
        "Scale.Plane::x_y": {"color": COLOR_Z},
        "Scale.Plane::y_z": {"color": COLOR_X},
        "Scale.Plane::z_x": {"color": COLOR_Y},
        "Scale.Point": {"color": COLOR_SCREEN},
    }


def get_button_style():
    return {
        "Button": {
            "background_color": 0xFF212121,
        },
        "Button:hovered": {"background_color": 0xFF9E9E9E},
        "Button:selected": {
            "background_color": 0xFF777777,
        },
        "Button:pressed": {"background_color": 0xFF79776C},
        "Button.Label": {"color": 0xFF777777},
        "Button.Label:selected": {"color": 0xFFDDDDDD},
    }


def get_disabled_style():
    return {
        "Label": {"color": 0xFF777777},
    }


def get_exclusions_window_style():
    return {
        "ListBackground": {"background_color": 0xFF24211F, "border_radius": 4},
        "FrameBackground": {"background_color": 0xFF35312E, "border_radius": 4},
        "ScrollingFrame": {"background_color": 0},
        "TreeView.Item": {"margin": 3},
    }
