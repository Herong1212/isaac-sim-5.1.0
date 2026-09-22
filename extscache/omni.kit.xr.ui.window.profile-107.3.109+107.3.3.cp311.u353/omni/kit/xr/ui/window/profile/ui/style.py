# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

# =================================== NOTE ====================================
# The APIs in this file are unfinished and may change in future releases
# Using these is at your own risk, and forward-compatability is not supported

import omni.ui as ui

# TODO: This is a workaround for bug in omni.ui where
# style dictionaries are not applied correctly, hence
# we set colors using inline styles sourced from this
# function


def get_colors() -> dict:
    return {
        "panel": 0xFF333333,
        "panel_highlight": 0xFF393939,
        "advanced_panel": 0xFF222222,
        "advanced_panel_highlight": 0xFF282828,
        "info_panel": 0xFF222222,
        "info_panel_highlight": 0xFF282828,
    }


def get_style():

    KIT_GREEN = 0xFF8A8777
    BORDER_RADIUS = 1.5
    FONT_SIZE = 14.0
    LABEL_COLOR = 0xFF8F8E86
    FIELD_BACKGROUND = 0xFF23211F
    FIELD_TEXT_COLOR = 0xFFD5D5D5
    FIELD_TEXT_COLOR_READ_ONLY = 0xFF5C5C5C
    FRAME_TEXT_COLOR = 0xFFCCCCCC
    WINDOW_BACKGROUND_COLOR = 0xFF444444
    BUTTON_BACKGROUND_COLOR = 0xFF292929
    BUTTON_BACKGROUND_HOVERED_COLOR = 0xFF9E9E9E
    BUTTON_BACKGROUND_PRESSED_COLOR = 0xC22A8778
    BUTTON_LABEL_DISABLED_COLOR = 0xFF606060
    LABEL_LABEL_COLOR = 0xFF9E9E9E
    LABEL_TITLE_COLOR = 0xFFDDDDDD
    LABEL_VECTORLABEL_COLOR = 0xFFDDDDDD
    COMBOBOX_HOVERED_BACKGROUND_COLOR = 0xFF33312F
    XRFRAME_HOVERED_BACKGROUND_COLOR = 0xFF2E2E2B

    style = {
        "Window": {"background_color": WINDOW_BACKGROUND_COLOR},
        "Button": {"background_color": BUTTON_BACKGROUND_COLOR, "margin": 0, "padding": 3, "border_radius": 4},
        "RadioButton": {
            "margin": 2,
            "border_radius": 2,
            "font_size": 16,
            "background_color": 0xFF212121,
            "color": 0xFF444444,
        },
        "RadioButton.Label": {"font_size": 16, "color": 0xFF777777},
        "RadioButton:checked": {"background_color": 0xFF777777, "color": 0xFF222222},
        "RadioButton.Label:checked": {"color": 0xFFDDDDDD},
        "Button:hovered": {"background_color": BUTTON_BACKGROUND_HOVERED_COLOR},
        "Button:pressed": {"background_color": BUTTON_BACKGROUND_PRESSED_COLOR},
        "Button.Label:disabled": {"color": BUTTON_LABEL_DISABLED_COLOR},
        "Triangle::title": {"background_color": 0xFFCCCCCC},
        "Field::models": {
            "background_color": FIELD_BACKGROUND,
            "font_size": FONT_SIZE,
            "color": FIELD_TEXT_COLOR,
            "border_radius": BORDER_RADIUS,
        },
        "Field::models_readonly": {
            "background_color": FIELD_BACKGROUND,
            "font_size": FONT_SIZE,
            "color": FIELD_TEXT_COLOR_READ_ONLY,
            "border_radius": BORDER_RADIUS,
        },
        "Label": {"font_size": 14, "color": LABEL_COLOR},
        "Label::label": {"font_size": FONT_SIZE, "color": LABEL_LABEL_COLOR},
        "Label::title": {"font_size": FONT_SIZE, "color": LABEL_TITLE_COLOR},
        "ComboBox::renderer_choice": {"font_size": 16},
        "ComboBox::choices": {
            "font_size": FONT_SIZE,
            "color": FIELD_TEXT_COLOR,
            "background_color": FIELD_BACKGROUND,
            "secondary_color": FIELD_BACKGROUND,
            "border_radius": BORDER_RADIUS,
        },
        "ComboBox:hovered:choices": {
            "background_color": COMBOBOX_HOVERED_BACKGROUND_COLOR,
            "secondary_color": COMBOBOX_HOVERED_BACKGROUND_COLOR,
        },
        "Slider::value": {
            "font_size": FONT_SIZE,
            "color": FIELD_TEXT_COLOR,
            "border_radius": BORDER_RADIUS,
            "background_color": FIELD_BACKGROUND,
            "secondary_color": KIT_GREEN,
        },
        "Slider::multivalue": {
            "font_size": FONT_SIZE,
            "color": FIELD_TEXT_COLOR,
            "border_radius": BORDER_RADIUS,
            "background_color": FIELD_BACKGROUND,
            "secondary_color": KIT_GREEN,
            "draw_mode": ui.SliderDrawMode.HANDLE,
        },
        "CheckBox::greenCheck": {
            "font_size": 12,
            "background_color": LABEL_LABEL_COLOR,
            "color": FIELD_BACKGROUND,
            "border_radius": BORDER_RADIUS,
        },
        "Label::RenderLabel": {"font_size": 16, "color": FRAME_TEXT_COLOR},
        "Rectangle::TopBar": {
            "border_radius": BORDER_RADIUS * 2,
            "background_color": XRFRAME_HOVERED_BACKGROUND_COLOR,
        },
        "Label::vector_label": {"font_size": 16, "color": LABEL_VECTORLABEL_COLOR},
        "Rectangle::vector_label": {"border_radius": BORDER_RADIUS * 2, "corner_flag": ui.CornerFlag.LEFT},
        "Rectangle::reset_invalid": {"background_color": 0xFF505050, "border_radius": 2},
        "Rectangle::reset": {"background_color": 0xFFA07D4F, "border_radius": 2},
        "XRPanel": {
            "background_color": 0xFF333333,
            "secondary_color": 0xFF333333,
            "border_radius": 4,
        },
        "XRPanel:hovered": {"secondary_color": 0xFF393939},
        "XRPanel:pressed": {"secondary_color": 0xFF393939},
        "XRAdvancedPanel": {
            "background_color": 0xFF222222,
            "secondary_color": 0xFF222222,
            "border_radius": 4,
        },
        "XRAdvancedPanel:hovered": {"secondary_color": 0xFF282828},
        "XRAdvancedPanel:pressed": {"secondary_color": 0xFF282828},
        "XRInfoPanel": {
            "background_color": 0xFF222222,
            "secondary_color": 0xFF222222,
            "border_radius": 4,
        },
        "XRInfoPanel:hovered": {"secondary_color": 0xFF282828},
        "XRInfoPanel:pressed": {"secondary_color": 0xFF282828},
    }

    return style
