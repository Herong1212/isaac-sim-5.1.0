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

def get_style():
    if THEME == "NvidiaLight":
        style = {
            "Button": {"background_color": 0xFFC9C9C9, "selected_color": 0xFFACACAF},
            "Button.Label": {"color": 0xFF535354},
            "Dialog": {"background_color": 0xFFC9C9C9, "color": 0xFF535354, "margin_width": 6},
            "Label": {"background_color": 0xFFC9C9C9, "color": 0xFF535354},
            "Input": {
                "background_color": 0xFFC9C9C9,
                "selected_color": 0xFFACACAF,
                "color": 0xFF535354,
                "alignment": ui.Alignment.LEFT_CENTER,
            },
            "Rectangle": {"background_color": 0xFFC9C9C9, "border_radius": 3},
            "Background": {"background_color": 0xFFE0E0E0, "border_radius": 2, "border_width": 0.5, "border_color": 0x55ADAC9F},
            "Background::header": {"background_color": 0xFF535354, "corner_flag": ui.CornerFlag.TOP, "margin": 0},
            "Dialog": {"background_color": 0xFFC9C9C9, "color": 0xFF535354, "margin": 10},
            "Message": {
                "background_color": 0xFFC9C9C9,
                "color": 0xFF535354,
                "margin": 0,
                "alignment": ui.Alignment.LEFT_CENTER,
                "margin": 0,
            },
            "Button": {"background_color": 0xFFC9C9C9, "selected_color": 0xFFACACAF, "margin": 0},
            "Button.Label": {"color": 0xFF535354},
            "Field": {"background_color": 0xFF535354, "color": 0xFFD6D6D6},
            "Field:pressed": {"background_color": 0xFF535354, "color": 0xFFD6D6D6},
            "Field:selected": {"background_color": 0xFFBEBBAE, "color": 0xFFD6D6D6},
            "Field.Label": {"background_color": 0xFFC9C9C9, "color": 0xFF535354, "margin": 0},
            "Field.Label::title": {"color": 0xFFD6D6D6},
            "Field.Label::prefix": {"alignment": ui.Alignment.RIGHT_CENTER},
            "Field.Label::postfix": {"alignment": ui.Alignment.LEFT_CENTER},
            "Field.Label::reset_all": {"color": 0xFFB0703B, "alignment": ui.Alignment.RIGHT_CENTER},
            "Input": {
                "background_color": 0xFF535354,
                "color": 0xFFD6D6D6,
                "alignment": ui.Alignment.LEFT_CENTER,
                "margin_height": 0,
            },
            "Menu.Item": {"margin_width": 6, "margin_height": 2},
            "Menu.Header": {"margin": 6},
            "Menu.CheckBox": {"background_color": 0xFF535354, "color": 0xFFD6D6D6},
            "Menu.Separator": {"color": 0x889E9E9E},
            "Options.Item": {"margin_width": 6, "margin_height": 0},
            "Options.CheckBox": {"background_color": 0x0, "color": 0xFF23211F},
            "Options.RadioButton": {"background_color": 0x0, "color": 0xFF9E9E9E},
            "Rectangle.Warning": {"background_color": 0x440000FF, "border_radius": 3, "margin": 10},
        }
    else:
        style = {
            "BorderedBackground": {"background_color": 0x0,  "border_width": .5, "border_color": 0x55ADAC9F},
            "Background": {"background_color": 0x0},
            "Background::header": {"background_color": 0xFF23211F, "corner_flag": ui.CornerFlag.TOP, "margin": 0},
            "Dialog": {"background_color": 0x0, "color": 0xFF9E9E9E, "margin": 10},
            "Message": {
                "background_color": 0x0,
                "color": 0xFF9E9E9E,
                "margin": 0,
                "alignment": ui.Alignment.LEFT_CENTER,
                "margin": 0,
            },
            "Button": {"background_color": 0xFF23211F, "selected_color": 0xFF8A8777, "margin": 0},
            "Button.Label": {"color": 0xFF9E9E9E},
            "Field.Label": {"background_color": 0x0, "color": 0xFF9E9E9E, "margin": 0},
            "Field.Label::prefix": {"alignment": ui.Alignment.RIGHT_CENTER},
            "Field.Label::postfix": {"alignment": ui.Alignment.LEFT_CENTER},
            "Field.Label::reset_all": {"color": 0xFFB0703B, "alignment": ui.Alignment.RIGHT_CENTER},
            "Input": {
                "background_color": 0xCC23211F,
                "color": 0xFF9E9E9E,
                "alignment": ui.Alignment.LEFT_CENTER,
                "margin_height": 0,
            },
            "Menu.Item": {"margin_width": 6, "margin_height": 2},
            "Menu.Header": {"margin": 6},
            "Menu.CheckBox": {"background_color": 0xDD9E9E9E, "color": 0xFF23211F},
            "Menu.Separator": {"color": 0x889E9E9E},
            "Options.Item": {"margin_width": 6, "margin_height": 0},
            "Options.CheckBox": {"background_color": 0xDD9E9E9E, "color": 0xFF23211F},
            "Options.RadioButton": {"background_color": 0x0, "color": 0xFF9E9E9E},
            "Rectangle.Warning": {"background_color": 0x440000FF, "border_radius": 3, "margin": 10},
        }

    return style
