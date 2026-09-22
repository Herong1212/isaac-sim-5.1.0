# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from typing import Dict

from omni.ui import color as cl

COLOR_X = 0xFF6060AA
COLOR_Y = 0xFF76A371
COLOR_Z = 0xFFA07D4F
COLOR_SCREEN = 0x8AFEF68E
COLOR_FREE = 0x40404040
COLOR_FOCAL = 0xE6CCCCCC


def get_default_style():
    """Returns the default style settings for the manipulator's visual elements.

    These settings include predefined colors for the axes (X, Y, Z), planes, and other components used in
    the manipulator in the context of translation, rotation, and scaling operations. It provides a consistent
    look and feel for the manipulator's visual elements and can be overridden by custom styles.

    Returns:
        Dict[str, Dict[str, Union[int, bool]]]: A dictionary with style settings for each manipulator component,
        with keys representing the component names and values containing style information such as color and visibility.
    """
    return {
        "Translate.Axis::x": {"color": COLOR_X},
        "Translate.Axis::y": {"color": COLOR_Y},
        "Translate.Axis::z": {"color": COLOR_Z},
        "Translate.Plane::x_y": {"color": COLOR_Z},
        "Translate.Plane::y_z": {"color": COLOR_X},
        "Translate.Plane::z_x": {"color": COLOR_Y},
        "Translate.Point": {"color": COLOR_SCREEN, "type": "point"},
        "Translate.Focal": {"color": COLOR_FOCAL, "visible": False},
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


def get_default_toolbar_style():
    """
    Returns the default style settings for the manipulator's toolbar.

    The function provides a set of default style properties for the manipulator's toolbar elements. Each element
    such as collapsable frames, lines, and rectangles has a set of attributes including background color,
    border color, padding, and margins. These default styles can be used to maintain a consistent look and feel
    across the toolbar or be overridden by custom styles.

    Returns:
        Dict[str, Dict[str, int]]: A dictionary containing styles for the toolbar elements. Each key represents
        an element type, and the corresponding value is another dictionary with style attributes as keys and
        their values as integers representing colors, widths, and sizes.
    """
    return {
        "CollapsableFrame": {
            "background_color": 0x00,
            "secondary_color": 0x00,
            "border_color": 0x0,
            "border_width": 0,
            "padding": 0,
            "margin_height": 5,
            "margin_width": 0,
        },
        "CollapsableFrame:hovered": {"secondary_color": 0x00},
        "CollapsableFrame:pressed": {"secondary_color": 0x00},
        "Line": {"color": 0xFFA1A1A1, "border_width": 2},
        "Rectangle": {"background_color": 0x8F000000},
    }


def abgr_to_color(abgr: int) -> cl:
    """Converts an ABGR integer value to a color object.

    The function takes an integer that represents a color in ABGR format (alpha, blue, green, red)
    and converts it into a color object with RGBA channels normalized to the range [0, 1].

    Args:
        abgr (int): The color value in ABGR format to be converted.

    Returns:
        omni.ui.color: The color object with RGBA channels."""
    # cl in rgba order
    return cl((abgr & 0xFF) / 255, (abgr >> 8 & 0xFF) / 255, (abgr >> 16 & 0xFF) / 255, (abgr >> 24 & 0xFF) / 255)


# style is nested dict, can't simply call to_style.update(from_style)
def update_style(to_style: Dict, from_style: Dict):
    """Updates the style dictionary with values from another dictionary.

    This function takes two dictionaries: `to_style`, the target dictionary to be updated, and `from_style`, the source dictionary containing new values. It recursively merges the `from_style` into `to_style`, ensuring that nested dictionaries are properly updated. This allows for deep customization of style properties in a structured manner.

    Args:
        to_style (Dict): The target style dictionary to update.
        from_style (Dict): The source style dictionary from which to update values.

    Returns:
        Dict: The updated target style dictionary with merged values from the source dictionary."""
    if from_style:
        for k, v in from_style.items():
            if isinstance(v, dict):
                to_style[k] = update_style(to_style.get(k, {}), v)
            else:
                to_style[k] = v
    return to_style
