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
ICON_ROOT = CURRENT_PATH.parent.parent.parent.parent.joinpath("icons/")
ICON_PATH = ICON_ROOT.joinpath(THEME)
ICON_COMMON_PATH = ICON_ROOT.joinpath("common")
THUMBNAIL_PATH = CURRENT_PATH.parent.parent.parent.parent.joinpath("data").joinpath("thumbnails")


def get_style():
    if THEME == "NvidiaLight":
        BACKGROUND_COLOR = 0xFF535354
        BACKGROUND_SELECTED_COLOR = 0xFF6E6E6E
        BACKGROUND_HOVERED_COLOR = 0xFF6E6E6E
        SECONDARY_COLOR = 0xFFE0E0E0
        BORDER_COLOR = 0xFF707070
        MENU_BACKGROUND_COLOR = 0xFF343432
        MENU_SEPARATOR_COLOR = 0x449E9E9E
        PROGRESS_BACKGROUND = 0xFF606060
        PROGRESS_BORDER = 0xFF323434
        PROGRESS_BAR = 0xFFC9974C
        PROGRESS_TEXT_COLOR = 0xFFD8D8D8
        TITLE_COLOR = 0xFF707070
        TEXT_COLOR = 0xFF8D760D
        TEXT_HINT_COLOR = 0xFFD6D6D6
        SPLITTER_HOVER_COLOR = 0xFFB0703B
    else:
        BACKGROUND_COLOR = 0xFF23211F
        BACKGROUND_SELECTED_COLOR = 0xFF8A8777
        BACKGROUND_HOVERED_COLOR = 0xFF3A3A3A
        SECONDARY_COLOR = 0xFF9E9E9E
        BORDER_COLOR = 0xFF8A8777
        MENU_BACKGROUND_COLOR = 0xFF343432
        MENU_SEPARATOR_COLOR = 0x449E9E9E
        PROGRESS_BACKGROUND = 0xFF606060
        PROGRESS_BORDER = 0xFF323434
        PROGRESS_BAR = 0xFFC9974C
        PROGRESS_TEXT_COLOR = 0xFFD8D8D8
        TITLE_COLOR = 0xFFCECECE
        TEXT_COLOR = 0xFF9E9E9E
        TEXT_HINT_COLOR = 0xFF4A4A4A
        SPLITTER_HOVER_COLOR = 0xFFB0703B

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
        "Button.Label:disabled": {"color": BACKGROUND_HOVERED_COLOR},
        "ComboBox": {
            "background_color": BACKGROUND_COLOR,
            "selected_color": BACKGROUND_SELECTED_COLOR,
            "color": TEXT_COLOR,
        },
        "ComboBox:hovered": {"background_color": BACKGROUND_HOVERED_COLOR},
        "ComboBox:selected": {"background_color": BACKGROUND_SELECTED_COLOR},
        "ComboBox.Button": {
            "background_color": BACKGROUND_COLOR,
            "selected_color": BACKGROUND_SELECTED_COLOR,
            "color": TEXT_COLOR,
            "margin_width": 0,
            "padding": 0,
        },
        "ComboBox.Button:hovered": {"background_color": BACKGROUND_HOVERED_COLOR},
        "ComboBox.Button.Label": {"color": TEXT_COLOR, "alignment": ui.Alignment.LEFT_CENTER},
        "ComboBox.Button.Glyph": {"color": 0xFFFFFFFF},
        "ComboBox.Menu": {
            "background_color": 0x0,
            "margin": 0,
            "padding": 0,
        },
        "ComboBox.Menu.Frame": {
            "background_color": 0xFF343432,
            "border_color": BORDER_COLOR,
            "border_width": 0,
            "border_radius": 4,
            "margin": 2,
            "padding": 0,
        },
        "ComboBox.Menu.Background": {
            "background_color": 0xFF343432,
            "border_color": BORDER_COLOR,
            "border_width": 0,
            "border_radius": 4,
            "margin": 0,
            "padding": 0,
        },
        "ComboBox.Menu.Item": {"background_color": 0x0, "color": TEXT_COLOR},
        "ComboBox.Menu.Item:hovered": {"background_color": BACKGROUND_SELECTED_COLOR},
        "ComboBox.Menu.Item:selected": {"background_color": BACKGROUND_SELECTED_COLOR},
        "ComboBox.Menu.Item::left": {"color": TEXT_COLOR, "alignment": ui.Alignment.LEFT_CENTER},
        "ComboBox.Menu.Item::right": {"color": TEXT_COLOR, "alignment": ui.Alignment.RIGHT_CENTER},
        "Field": {"background_color": 0x0, "selected_color": BACKGROUND_SELECTED_COLOR, "color": TEXT_COLOR, "alignment": ui.Alignment.LEFT_CENTER},
        "Label": {"background_color": 0x0, "color": TEXT_COLOR},
        "Menu": {"background_color": MENU_BACKGROUND_COLOR, "color": TEXT_COLOR, "border_radius": 2},
        "Menu.Item": {"background_color": 0x0, "margin": 0},
        "Menu.Separator": {"background_color": 0x0, "color": MENU_SEPARATOR_COLOR},
        "Rectangle": {"background_color": 0x0},
        "FileBar": {"background_color": BACKGROUND_COLOR, "color": TEXT_COLOR},
        "FileBar.Label": {"background_color": 0x0, "color": TEXT_COLOR, "alignment": ui.Alignment.LEFT_CENTER, "margin_width": 4, "margin_height": 0},
        "FileBar.Label:disabled": {"color": TEXT_HINT_COLOR},
        "DetailView": {"background_color": BACKGROUND_COLOR, "color": TEXT_COLOR, "margin": 0, "padding": 0},
        "DetailView.ScrollingFrame": {"background_color": BACKGROUND_COLOR, "secondary_color": SECONDARY_COLOR},
        "DetailFrame": {
            "background_color": BACKGROUND_COLOR,
            "secondary_color": 0xFF0000FF,
            "color": TEXT_COLOR,
            "border_radius": 1,
            "border_color": 0xFF535354,
            "margin_width": 4,
            "margin_height": 1.5,
            "padding": 0
        },
        "DetailFrame.Header.Label": {"color": TITLE_COLOR},
        "DetailFrame.Header.Icon": {"color": 0xFFFFFFFF, "padding": 0, "alignment": ui.Alignment.LEFT_CENTER},
        "DetailFrame.Body": {"margin_height": 2, "padding": 0},
        "DetailFrame.Separator": {"background_color": TEXT_HINT_COLOR},
        "DetailFrame.LineItem::left_aligned": {"alignment": ui.Alignment.LEFT_CENTER},
        "DetailFrame.LineItem::right_aligned": {"alignment": ui.Alignment.RIGHT_CENTER},
        "ProgressBar": {
            "background_color": PROGRESS_BACKGROUND,
            "border_width": 2,
            "border_radius": 0,
            "border_color": PROGRESS_BORDER,
            "color": PROGRESS_BAR,
            "secondary_color": PROGRESS_TEXT_COLOR,
            "margin": 0,
            "padding": 0,
            "alignment": ui.Alignment.LEFT_CENTER,
        },
        "ProgressBar.Frame": {"background_color": BACKGROUND_COLOR, "margin": 0, "padding": 0},
        "ProgressBar.Puck": {"background_color": PROGRESS_BAR, "margin": 2},
        "ToolBar": {"alignment": ui.Alignment.CENTER, "margin_height": 2},
        "ToolBar.Button": {"background_color": 0x0, "color": TEXT_COLOR, "margin_width": 2, "padding": 2},
        "ToolBar.Button.Label": {"color": TEXT_COLOR, "alignment": ui.Alignment.LEFT_CENTER},
        "ToolBar.Button.Image": {"background_color": 0x0, "color": 0xFFFFFFFF, "alignment": ui.Alignment.CENTER},
        "ToolBar.Button:hovered": {"background_color": 0xFF6E6E6E},
        "ToolBar.Field": {"background_color": BACKGROUND_COLOR, "color": TEXT_COLOR, "margin": 0, "padding": 0},
        "Splitter": {"background_color": 0x0, "margin_width": 0},
        "Splitter:hovered": {"background_color": SPLITTER_HOVER_COLOR},
        "Splitter:pressed": {"background_color": SPLITTER_HOVER_COLOR},
        "LoadingPane.Bg": {"background_color": BACKGROUND_COLOR},
        "LoadingPane.Button": {
            "background_color": BACKGROUND_HOVERED_COLOR,
            "selected_color": BACKGROUND_SELECTED_COLOR,
            "color": TEXT_COLOR,
        },
        "LoadingPane.Button:hovered": {"background_color": BACKGROUND_SELECTED_COLOR},
    }
    return style
