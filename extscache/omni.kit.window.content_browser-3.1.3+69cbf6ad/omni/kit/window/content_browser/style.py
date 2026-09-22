# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni.ui as ui
from pathlib import Path

try:
    THEME = carb.settings.get_settings().get_as_string("/persistent/app/window/uiStyle")
except Exception:
    THEME = None
finally:
    THEME = THEME or "NvidiaDark"

CURRENT_PATH = Path(__file__).parent.absolute()
ICON_PATH = CURRENT_PATH.parent.parent.parent.parent.joinpath(f"icons/{THEME}")
ICON_COMMON_PATH = CURRENT_PATH.parent.parent.parent.parent.joinpath(f"icons/common")


def get_style():
    if THEME == "NvidiaLight":
        style = {
            "Rectangle": {"background_color": 0xFF535354},
            "Splitter": {"background_color": 0x0, "margin_width": 0},
            "Splitter:hovered": {"background_color": 0xFFB0703B},
            "Splitter:pressed": {"background_color": 0xFFB0703B},
            "ToolBar": {"alignment": ui.Alignment.CENTER, "margin_height": 2},
            "ToolBar.Button": {"background_color": 0xFF535354, "color": 0xFF9E9E9E},
            "ToolBar.Button::filter": {"background_color": 0x0, "color": 0xFF9E9E9E},
            "ToolBar.Button::import": {
                "background_color": 0xFFD6D6D6,
                "color": 0xFF535354,
                "stack_direction": ui.Direction.LEFT_TO_RIGHT,
                "border_radius": 3,
            },
            "ToolBar.Button.Label": {"color": 0xFF535354, "alignment": ui.Alignment.LEFT_CENTER},
            "ToolBar.Button.Image": {"background_color": 0x0, "color": 0xFFFFFFFF, "alignment": ui.Alignment.CENTER},
            "ToolBar.Button:hovered": {"background_color": 0xFFB8B8B8},
            
            "Recycle.Button.Label": {"color": 0xFF9E9E9E, "alignment": ui.Alignment.LEFT_CENTER},
            "Recycle.Button.Image": {"image_url": "resources/glyphs/trash.svg", "background_color": 0x0, "color": 0xFFFFFFFF, "alignment": ui.Alignment.CENTER},
            "Recycle.Button:hovered": {"background_color": 0xFF3A3A3A},
        }
    else:
        style = {
            "Splitter": {"background_color": 0x0, "margin_width": 0},
            "Splitter:hovered": {"background_color": 0xFFB0703B},
            "Splitter:pressed": {"background_color": 0xFFB0703B},
            "ToolBar": {"alignment": ui.Alignment.CENTER, "margin_height": 2},
            "ToolBar.Button": {"background_color": 0x0, "color": 0xFF9E9E9E},
            "ToolBar.Button::import": {
                "background_color": 0xFF23211F,
                "color": 0xFF9E9E9E,
                "stack_direction": ui.Direction.LEFT_TO_RIGHT,
                "border_radius": 3,
            },
            "ToolBar.Button.Label": {"color": 0xFF9E9E9E, "alignment": ui.Alignment.LEFT_CENTER},
            "ToolBar.Button.Image": {"background_color": 0x0, "color": 0xFFFFFFFF, "alignment": ui.Alignment.CENTER},
            "ToolBar.Button:hovered": {"background_color": 0xFF3A3A3A},
            
            "Recycle.Button.Label": {"color": 0xFF9E9E9E, "alignment": ui.Alignment.LEFT_CENTER},
            "Recycle.Button.Image": {"image_url": "resources/glyphs/trash.svg", "background_color": 0x0, "color": 0xFFFFFFFF, "alignment": ui.Alignment.CENTER},
            "Recycle.Button:hovered": {"background_color": 0xFF3A3A3A},
        }

    return style
