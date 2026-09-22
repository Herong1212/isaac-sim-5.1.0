"""
Source for get_ui_style_name, get_style.
"""
__all__ = ['get_ui_style_name', 'get_style']

import carb.settings
import omni.ui as ui


def get_ui_style_name():
    """
    Gets which light/dark theme kit is using. Not wildly supported.
    """
    return carb.settings.get_settings().get_as_string("/persistent/app/window/uiStyle") or "NvidiaDark"


def get_style():
    """
    Get default style.
    """
    KIT_GREEN = 0xFF8A8777
    BORDER_RADIUS = 1.5
    FONT_SIZE = 14.0

    ui_style = get_ui_style_name()

    if ui_style == "NvidiaLight": # pragma: no cover
        WINDOW_BACKGROUND_COLOR = 0xFF444444
        BUTTON_BACKGROUND_COLOR = 0xFF545454
        BUTTON_BACKGROUND_HOVERED_COLOR = 0xFF9E9E9E
        BUTTON_BACKGROUND_PRESSED_COLOR = 0xC22A8778
        BUTTON_LABEL_DISABLED_COLOR = 0xFF606060
        BUTTON_LABEL_COLOR = 0x7FD6D6D6

        FRAME_TEXT_COLOR = 0xFF545454
        FIELD_BACKGROUND = 0xFF545454
        FIELD_SECONDARY = 0xFFABABAB
        FIELD_TEXT_COLOR = 0xFFD6D6D6
        FIELD_TEXT_COLOR_READ_ONLY = 0xFF9C9C9C
        FIELD_TEXT_COLOR_HIDDEN = 0x01000000
        COLLAPSABLEFRAME_BORDER_COLOR = 0x0
        COLLAPSABLEFRAME_BACKGROUND_COLOR = 0x7FD6D6D6
        COLLAPSABLEFRAME_TEXT_COLOR = 0xFF545454

        COLLAPSABLEFRAME_GROUPFRAME_BACKGROUND_COLOR = 0xFFC9C9C9
        COLLAPSABLEFRAME_SUBFRAME_BACKGROUND_COLOR = 0xFFD6D6D6
        COLLAPSABLEFRAME_HOVERED_BACKGROUND_COLOR = 0xFFCCCFBF
        COLLAPSABLEFRAME_PRESSED_BACKGROUND_COLOR = 0xFF2E2E2B
        COLLAPSABLEFRAME_HOVERED_SECONDARY_COLOR = 0xFFD6D6D6
        COLLAPSABLEFRAME_PRESSED_SECONDARY_COLOR = 0xFFE6E6E6
        LABEL_VECTORLABEL_COLOR = 0xFFDDDDDD
        LABEL_MIXED_COLOR = 0xFFD6D6D6
        LIGHT_FONT_SIZE = 14.0
        LIGHT_BORDER_RADIUS = 3
        style = {
            "Window": {"background_color": 0xFFE0E0E0},
            "Button": {"background_color": 0xFFE0E0E0, "margin": 0, "padding": 3, "border_radius": 2},
            "Button:hovered": {"background_color": BUTTON_BACKGROUND_HOVERED_COLOR},
            "Button:pressed": {"background_color": BUTTON_BACKGROUND_PRESSED_COLOR},
            "Button.Label:disabled": {"color": BUTTON_LABEL_DISABLED_COLOR},
            "Button.Label": {"color": BUTTON_LABEL_COLOR},
            "RadioButton": {
                "margin": 2,
                "border_radius": 2,
                "font_size": 16,
                "background_color": BUTTON_BACKGROUND_COLOR,
                "color": 0xFFFF0000,
            },
            "RadioButton.Label": {"font_size": 16, "color": 0xFFC8C8C8},
            "RadioButton:checked": {"background_color": BUTTON_BACKGROUND_HOVERED_COLOR, "color": 0xFF00FF00},
            "RadioButton:pressed": {"background_color": BUTTON_BACKGROUND_HOVERED_COLOR, "color": 0xFF00FF00},
            "RadioButton.Label:checked": {"color": 0xFFE8E8E8},
            "Triangle::title": {"background_color": BUTTON_BACKGROUND_COLOR},
            "ComboBox": {
                "font_size": LIGHT_FONT_SIZE,
                "color": 0xFFE6E6E6,
                "background_color": 0xFF545454,
                "secondary_color": 0xFF545454,
                "selected_color": 0xFFACACAF,
                "border_radius": LIGHT_BORDER_RADIUS * 2,
            },
            "ComboBox:hovered": {"background_color": 0xFF545454},
            "ComboBox:selected": {"background_color": 0xFF545454},
            "Field::models": {
                "background_color": FIELD_BACKGROUND,
                "font_size": LIGHT_FONT_SIZE,
                "color": FIELD_TEXT_COLOR,
                "border_radius": LIGHT_BORDER_RADIUS,
                "secondary_color": FIELD_SECONDARY,
            },
            "Field::models_readonly": {
                "background_color": FIELD_BACKGROUND,
                "font_size": LIGHT_FONT_SIZE,
                "color": FIELD_TEXT_COLOR_READ_ONLY,
                "border_radius": LIGHT_BORDER_RADIUS,
                "secondary_color": FIELD_SECONDARY,
            },
            "Field::models:pressed": {"background_color": 0xFFCECECE},
            "Field": {"background_color": 0xFF535354, "color": 0xFFCCCCCC},
            "Label": {"font_size": 12, "color": FRAME_TEXT_COLOR},
            "Label::RenderLabel": {"font_size": LIGHT_FONT_SIZE, "color": FRAME_TEXT_COLOR},
            "Label::label": {
                "font_size": LIGHT_FONT_SIZE,
                "background_color": FIELD_BACKGROUND,
                "color": FRAME_TEXT_COLOR,
            },
            "Label::title": {
                "font_size": LIGHT_FONT_SIZE,
                "background_color": FIELD_BACKGROUND,
                "color": FRAME_TEXT_COLOR,
            },
            "Slider::value": {
                "font_size": LIGHT_FONT_SIZE,
                "color": FIELD_TEXT_COLOR,
                "border_radius": LIGHT_BORDER_RADIUS,
                "background_color": BUTTON_BACKGROUND_HOVERED_COLOR,
                "secondary_color": KIT_GREEN,
            },
            "CheckBox::greenCheck": {"font_size": 10, "background_color": KIT_GREEN, "color": 0xFF23211F},
            "CollapsableFrame": {
                "background_color": COLLAPSABLEFRAME_BACKGROUND_COLOR,
                "secondary_color": COLLAPSABLEFRAME_BACKGROUND_COLOR,
                "color": COLLAPSABLEFRAME_TEXT_COLOR,
                "border_radius": LIGHT_BORDER_RADIUS,
                "border_color": 0x0,
                "border_width": 1,
                "font_size": LIGHT_FONT_SIZE,
                "padding": 6,
            },
            "CollapsableFrame.Header": {
                "font_size": LIGHT_FONT_SIZE,
                "background_color": FRAME_TEXT_COLOR,
                "color": FRAME_TEXT_COLOR,
            },
            "CollapsableFrame:hovered": {"secondary_color": COLLAPSABLEFRAME_HOVERED_SECONDARY_COLOR},
            "CollapsableFrame:pressed": {"secondary_color": COLLAPSABLEFRAME_PRESSED_SECONDARY_COLOR},
            "Label::vector_label": {"font_size": 14, "color": LABEL_VECTORLABEL_COLOR},
            "Rectangle::reset_invalid": {"background_color": 0xFF505050, "border_radius": 2},
            "Rectangle::reset": {"background_color": 0xFFA07D4F, "border_radius": 2},
            "Rectangle::vector_label": {"border_radius": BORDER_RADIUS * 2, "corner_flag": ui.CornerFlag.LEFT},
            "Rectangle": {"border_radius": LIGHT_BORDER_RADIUS, "background_color": FIELD_BACKGROUND},
            "Line::check_line": {"color": KIT_GREEN},
        }
    else:
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
        LABEL_TITLE_COLOR = 0xFFAAAAAA
        LABEL_VECTORLABEL_COLOR = 0xFFDDDDDD
        COLORWIDGET_BORDER_COLOR = 0xFF1E1E1E
        COMBOBOX_HOVERED_BACKGROUND_COLOR = 0xFF33312F
        COLLAPSABLEFRAME_BORDER_COLOR = 0x0
        COLLAPSABLEFRAME_BACKGROUND_COLOR = 0xFF343432
        COLLAPSABLEFRAME_GROUPFRAME_BACKGROUND_COLOR = 0xFF23211F
        COLLAPSABLEFRAME_SUBFRAME_BACKGROUND_COLOR = 0xFF343432
        COLLAPSABLEFRAME_HOVERED_BACKGROUND_COLOR = 0xFF2E2E2B
        COLLAPSABLEFRAME_PRESSED_BACKGROUND_COLOR = 0xFF2E2E2B

        style = {
            "Window": {"background_color": WINDOW_BACKGROUND_COLOR},
            "Button": {"background_color": WINDOW_BACKGROUND_COLOR, "margin": 0, "padding": 3, "border_radius": 4},
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
            "CollapsableFrame": {
                "background_color": COLLAPSABLEFRAME_BACKGROUND_COLOR,
                "secondary_color": COLLAPSABLEFRAME_BACKGROUND_COLOR,
                "border_radius": BORDER_RADIUS * 2,
                "padding": 4,
                "color": FRAME_TEXT_COLOR,
            },
            "CollapsableFrame::groupFrame": {
                "background_color": COLLAPSABLEFRAME_GROUPFRAME_BACKGROUND_COLOR,
                "secondary_color": COLLAPSABLEFRAME_GROUPFRAME_BACKGROUND_COLOR,
                "border_radius": BORDER_RADIUS * 2,
                "padding": 2,
            },
            "CollapsableFrame::groupFrame:hovered": {
                "background_color": COLLAPSABLEFRAME_GROUPFRAME_BACKGROUND_COLOR,
                "secondary_color": COLLAPSABLEFRAME_GROUPFRAME_BACKGROUND_COLOR,
            },
            "CollapsableFrame::groupFrame:pressed": {
                "background_color": COLLAPSABLEFRAME_GROUPFRAME_BACKGROUND_COLOR,
                "secondary_color": COLLAPSABLEFRAME_GROUPFRAME_BACKGROUND_COLOR,
            },
            "CollapsableFrame::subFrame": {
                "background_color": COLLAPSABLEFRAME_SUBFRAME_BACKGROUND_COLOR,
                "secondary_color": COLLAPSABLEFRAME_SUBFRAME_BACKGROUND_COLOR,
            },
            "CollapsableFrame::subFrame:hovered": {
                "background_color": COLLAPSABLEFRAME_SUBFRAME_BACKGROUND_COLOR,
                "secondary_color": COLLAPSABLEFRAME_HOVERED_BACKGROUND_COLOR,
            },
            "CollapsableFrame::subFrame:pressed": {
                "background_color": COLLAPSABLEFRAME_SUBFRAME_BACKGROUND_COLOR,
                "secondary_color": COLLAPSABLEFRAME_PRESSED_BACKGROUND_COLOR,
            },
            "CollapsableFrame.Header": {
                "font_size": FONT_SIZE,
                "background_color": FRAME_TEXT_COLOR,
                "color": FRAME_TEXT_COLOR,
            },
            "CollapsableFrame:hovered": {"secondary_color": COLLAPSABLEFRAME_HOVERED_BACKGROUND_COLOR},
            "CollapsableFrame:pressed": {"secondary_color": COLLAPSABLEFRAME_PRESSED_BACKGROUND_COLOR},
            "ColorWidget": {
                "border_radius": BORDER_RADIUS,
                "border_color": COLORWIDGET_BORDER_COLOR,
                "border_width": 0.5,
            },
            "Label::RenderLabel": {"font_size": 16, "color": FRAME_TEXT_COLOR},
            "Rectangle::TopBar": {
                "border_radius": BORDER_RADIUS * 2,
                "background_color": COLLAPSABLEFRAME_HOVERED_BACKGROUND_COLOR,
            },
            "Label::vector_label": {"font_size": 16, "color": LABEL_VECTORLABEL_COLOR},
            "Rectangle::vector_label": {"border_radius": BORDER_RADIUS * 2, "corner_flag": ui.CornerFlag.LEFT},
            "Rectangle::reset_invalid": {"background_color": 0xFF505050, "border_radius": 2},
            "Rectangle::reset": {"background_color": 0xFFA07D4F, "border_radius": 2},
        }

    return style
