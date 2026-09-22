# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
""" Style of widgets used in the extension."""

import carb
import omni.ui as ui

try:
    THEME = carb.settings.get_settings().get_as_string("/persistent/app/window/uiStyle")
except Exception:
    THEME = None
finally:
    THEME = THEME or "NvidiaDark"

def get_style():
    """
    Return:
        Dict[str, Any]: Get style of widgets used in the extension.
    """
    if THEME == "NvidiaLight": # pragma: no cover
        BACKGROUND_COLOR = 0xFF535354
        BACKGROUND_SELECTED_COLOR = 0xFF6E6E6E
        BACKGROUND_HOVERED_COLOR = 0xFF6E6E6E
        FIELD_BACKGROUND_COLOR = 0xFF1F2124
        SECONDARY_COLOR = 0xFFE0E0E0
        BORDER_COLOR = 0xFF707070
        TITLE_COLOR = 0xFF707070
        TEXT_COLOR = 0xFF8D760D
        TEXT_HINT_COLOR = 0xFFD6D6D6
    else:
        BACKGROUND_COLOR = 0xFF23211F
        BACKGROUND_SELECTED_COLOR = 0xFF8A8777
        BACKGROUND_HOVERED_COLOR = 0xFF3A3A3A
        SECONDARY_COLOR = 0xFF9E9E9E
        BORDER_COLOR = 0xFF8A8777
        TITLE_COLOR = 0xFFCECECE
        TEXT_COLOR = 0xFF9E9E9E
        TEXT_HINT_COLOR = 0xFF7A7A7A

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
        "Field": {"background_color": BACKGROUND_COLOR, "selected_color": BACKGROUND_SELECTED_COLOR, "color": TEXT_COLOR, "alignment": ui.Alignment.LEFT_CENTER},
        "Field.Hint": {"background_color": 0x0, "color": TEXT_HINT_COLOR, "margin_width": 4},
        "Label": {"background_color": 0x0, "color": TEXT_COLOR},
        "CheckBox": {"alignment": ui.Alignment.CENTER},
    }
    return style
