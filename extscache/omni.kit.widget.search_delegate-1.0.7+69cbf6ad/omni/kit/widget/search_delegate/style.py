# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import carb
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
THUMBNAIL_PATH = CURRENT_PATH.parent.parent.parent.parent.joinpath("data").joinpath("thumbnails")


def get_style():
    if THEME == "NvidiaLight":
        BACKGROUND_COLOR = 0xFF535354
        BACKGROUND_SELECTED_COLOR = 0xFF6E6E6E
        BACKGROUND_HOVERED_COLOR = 0xFF6E6E6E
        BACKGROUND_DISABLED_COLOR = 0xFF666666
        TEXT_COLOR = 0xFF8D760D
        TEXT_HINT_COLOR = 0xFFD6D6D6
        SEARCH_BORDER_COLOR = 0xFFC9974C
        SEARCH_HOVER_COLOR = 0xFFB8B8B8
        SEARCH_CLOSE_COLOR = 0xFF858585
        SEARCH_TEXT_BACKGROUND_COLOR = 0xFFD9D4BC
    else:
        BACKGROUND_COLOR = 0xFF23211F
        BACKGROUND_SELECTED_COLOR = 0xFF8A8777
        BACKGROUND_HOVERED_COLOR = 0xFF3A3A3A
        BACKGROUND_DISABLED_COLOR = 0xFF666666
        TEXT_COLOR = 0xFF9E9E9E
        TEXT_HINT_COLOR = 0xFF4A4A4A
        SEARCH_BORDER_COLOR = 0xFFC9974C
        SEARCH_HOVER_COLOR = 0xFF3A3A3A
        SEARCH_CLOSE_COLOR = 0xFF858585
        SEARCH_TEXT_BACKGROUND_COLOR = 0xFFD9D4BC

    style = {
        "Button": {
            "background_color": BACKGROUND_COLOR,
            "selected_color": BACKGROUND_SELECTED_COLOR,
            "color": TEXT_COLOR,
            "margin": 0,
            "padding": 0
        },
        "Button:hovered": {"background_color": BACKGROUND_HOVERED_COLOR},
        "Button.Label": {"color": TEXT_COLOR},
        "Field": {"background_color": 0x0, "selected_color": BACKGROUND_SELECTED_COLOR, "color": TEXT_COLOR, "alignment": ui.Alignment.LEFT_CENTER},
        "Label": {"background_color": 0x0, "color": TEXT_COLOR},
        "Rectangle": {"background_color": 0x0},
        "SearchField": {
            "background_color": 0,
            "border_radius": 0,
            "border_width": 0,
            "background_selected_color": BACKGROUND_COLOR,
            "margin": 0,
            "padding": 4,
            "alignment": ui.Alignment.LEFT_CENTER,
        },
        "SearchField.Frame": {
            "background_color": BACKGROUND_COLOR,
            "border_radius": 0.0,
            "border_color": 0,
            "border_width": 2,
        },
        "SearchField.Frame:selected": {
            "background_color": BACKGROUND_COLOR,
            "border_radius": 0,
            "border_color": SEARCH_BORDER_COLOR,
            "border_width": 2,
        },
        "SearchField.Frame:disabled": {
            "background_color": BACKGROUND_DISABLED_COLOR,
        },
        "SearchField.Hint": {"color": TEXT_HINT_COLOR},
        "SearchField.Button": {"background_color": 0x0, "margin_width": 2, "padding": 4},
        "SearchField.Button.Image": {"color": TEXT_HINT_COLOR},
        "SearchField.Clear": {"background_color": 0x0, "padding": 4},
        "SearchField.Clear:hovered": {"background_color": SEARCH_HOVER_COLOR},
        "SearchField.Clear.Image": {"image_url": f"{ICON_PATH}/close.svg", "color": SEARCH_CLOSE_COLOR},
        "SearchField.Word": {"background_color": SEARCH_TEXT_BACKGROUND_COLOR},
        "SearchField.Word.Label": {"color": TEXT_COLOR},
        "SearchField.Word.Button": {"background_color": 0, "padding": 2},
        "SearchField.Word.Button.Image": {"image_url": f"{ICON_PATH}/close.svg", "color": TEXT_COLOR},
    }
    return style
