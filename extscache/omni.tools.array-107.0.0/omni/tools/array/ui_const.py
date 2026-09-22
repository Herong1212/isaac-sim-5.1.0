# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.kit.app
import omni.ui as ui

# Paths
PATH_EXTENSION = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
PATH_MENU_ENTRY = "Tools/Array"
PATH_ICON_LINKED_ON = "/data/link_tint.svg"
PATH_ICON_LINKED_OFF = "/data/link_tint_off.svg"
PATH_ICON_RADIO_ON = "/data/radio_on.svg"
PATH_ICON_RADIO_OFF = "/data/radio_off.svg"
PATH_ICON_TOTAL_BUTTON = "/data/total.svg"
PATH_ICON_PREVIEW_BUTTON_ON = "/data/switch_on_dark.svg"
PATH_ICON_PREVIEW_BUTTON_OFF = "/data/switch_off_dark.svg"
PATH_ICON_RANDOM = "/data/refresh_icon.svg"
PATH_ICON_WARNING = "/data/warning.svg"

# UI Variable Defaults
REMEMBER_LAST_DEFAULT = True

# Names
NAME_TOOL = "Array Tool"

# Tooltips
TOOLTIP_PREVIEW = """Toggle live array preview
"""
TOOLTIP_LABEL_COUNT = """Total array element count
"""
TOOLTIP_LABEL_OFFSET_2D = """Replicates array in additional second dimension with incremental offset.
In total mode: Total offset at additional second array dimension endpoint.
"""
TOOLTIP_LABEL_OFFSET_3D = """Replicates array in additional third dimension with incremental offset.
In total mode: Total offset at additional third array dimension endpoint.
"""
TOOLTIP_LABEL_TRANSLATE = """Translation increment for each array element.
In total mode: Total translation increment at array endpoint.
Note: Translations are applied in local space.
"""
TOOLTIP_LABEL_ROTATE = """Rotation increment for each array element.
In total mode: Total rotation increment at array endpoint.
Note: Rotations are applied in local space.
"""
TOOLTIP_LABEL_SCALE = """Scale increment for each array element.
In total mode: Total scale increment at array endpoint.
Note: Scaling is applied in local space.
"""
TOOLTIP_BUTTON_RESET = """Click to reset value
"""
TOOLTIP_BUTTON_TOTAL = """Toggle Total Mode for this row.
In Total Mode, values represent the total amount of increments at the array endpoint.
"""
TOOLTIP_FIELD_COUNT_2D = """Total second dimension replication count
"""
TOOLTIP_FIELD_COUNT_3D = """Total third dimension replication count
"""
TOOLTIP_BUTTON_LINKED_SCALE = """Toggle linked scale
"""
TOOLTIP_LABEL_CREATE_INSTANCES = """Create array elements as instances
"""
TOOLTIP_LABEL_CREATE_COPIES = """Create array elements as copies
"""
TOOLTIP_LABEL_ARRAY_TYPE = """Determines how to build array from current selection.\n
Single Stamp: Arrays entire selection as single array stamp element
Ordered Sequence: Arrays selection objects individually in selection order
Random Sequence: Arrays selection objects individually in random order
"""
TOOLTIP_LABEL_GROUP_RESULT = """Determines if array output should be grouped
"""
TOOLTIP_LABEL_REORIENT = """Determines if array element translation should follow rotation changes
"""
TOOLTIP_LABEL_REMEMBER_LAST = """Determines if Array Tool should retain edited values after applying
"""
TOOLTIP_LABEL_AUTO_SELECT_CREATED = """Determines if array elements should be auto-selected after applying
"""
TOOLTIP_BUTTON_CANCEL = """Closes Array Tool without applying any changes. Resets values to defaults.
"""
TOOLTIP_BUTTON_RESET_ALL = """Resets all values and settings to their respective defaults
"""
TOOLTIP_BUTTON_APPLY = """Creates editable array based on current values and settings
"""
TOOLTIP_RANDOM_ORDER_SEED = """Determines the Seed value used when arraying selection as 'Random Sequence'
"""
TOOLTIP_RANDOM = """Generate a random seed value
"""

# Styles
STYLE_LABEL = {"": {"color": 0xCCFFFFFF}, ":disabled": {"color": 0x33FFFFFF}}
STYLE_TOOLTIP = {
    "color": 0xCC000000,
    "background_color": 0xFFAADDDD,
    "border_width": 0,
    "margin": -1,
    "border_width": 0,
}
STYLE_TOOLTIP_TEXT = {"margin": 3}
STYLE_LINKED_BUTTON_ON = {
    "": {
        "image_url": f"{PATH_EXTENSION}{PATH_ICON_LINKED_ON}",
        "padding": 0,
        "color": 0xFFFFC734,
        "background_color": 0x0,
    },
    ":hovered": {
        "color": 0xFFFFFFFF,
        "padding": 0,
        "background_color": 0x0,
    },
}
STYLE_LINKED_BUTTON_OFF = {
    "": {
        "image_url": f"{PATH_EXTENSION}{PATH_ICON_LINKED_OFF}",
        "padding": 0,
        "color": 0x66FFFFFF,
        "background_color": 0x0,
    },
    ":hovered": {
        "background_color": 0x0,
        "color": 0xFFFFFFFF,
        "padding": 0,
    },
}
STYLE_SEPARATOR = {"color": 0x66FFFFFF}
STYLE_COLLAPSABLE_FRAME = {"border_radius": 4, "margin": 3}
STYLE_RECT_CREATE_TYPE = {
    "border_width": 1,
    "border_color": 0xFF666666,
    "border_radius": 4,
    "background_color": 0x0,
}
STYLE_RADIO_BUTTON = {
    "": {
        "background_color": 0x0,
        "image_url": f"{PATH_EXTENSION}{PATH_ICON_RADIO_OFF}",
    },
    ":checked": {"image_url": f"{PATH_EXTENSION}{PATH_ICON_RADIO_ON}"},
    ":disabled": {"color": 0x33FFFFFF},
}
STYLE_LINE = {"color": 0x22FFFFFF}
STYLE_BUTTON_RESET_OFF = {"background_color": 0x33FFFFFF}
STYLE_BUTTON_RESET_ON = {"background_color": 0xFFA07D4F, "border_radius": 2, "color": 0xFFFFFFFF}
STYLE_PREVIEW_BUTTON_TOGGLE = {"background_color": 0xFF999999, "border_width": 1, "border_color": 0xFFAAAAAA}
STYLE_BUTTON_PREVIEW_ON = {
    "": {"background_color": 0x0, "image_url": f"{PATH_EXTENSION}{PATH_ICON_PREVIEW_BUTTON_ON}"},
    ":hovered": {"color": 0x99FFFFFF},
}
STYLE_BUTTON_PREVIEW_OFF = {
    "": {"background_color": 0x0, "image_url": f"{PATH_EXTENSION}{PATH_ICON_PREVIEW_BUTTON_OFF}"},
    ":hovered": {"color": 0x99FFFFFF},
}
STYLE_VECTOR_DISABLED = {"color": 0x22FFFFFF}
STYLE_VECTOR_ENABLED = {"color": 0xCCFFFFFF}
STYLE_VECTOR_ENABLED_TOTAL_MODE = {"color": 0xFFFFC734}
STYLE_BUTTON_APPLY = {"": {"color": 0xCCFFFFFF}, ":disabled": {"color": 0x33FFFFFF}}
STYLE_BUTTON_TOTAL_OFF = {
    "": {
        "image_url": f"{PATH_EXTENSION}{PATH_ICON_TOTAL_BUTTON}",
        "padding": 0,
        "background_color": 0x0,
        "border_width": 1,
        "border_color": 0x22FFFFFF,
        "color": 0x66FFFFFF,
    },
    ":hovered": {"background_color": 0xFFFFFFFF, "color": 0xFF000000, "padding": 0, "border_width": 0},
}
STYLE_BUTTON_TOTAL_ON = {
    "": {
        "image_url": f"{PATH_EXTENSION}{PATH_ICON_TOTAL_BUTTON}",
        "background_color": 0x33FFC734,
        "padding": 0,
        "color": 0xFFFFC734,
        "border_width": 2,
        "border_color": 0xFFFFC734,
    },
    ":hovered": {"background_color": 0xFFFFFFFF, "color": 0xFF000000, "padding": 0},
}
STYLE_COMBOBOX_ARRAY_TYPE = {"border_radius": 6, "margin": 0}
STYLE_LABEL_SCALE = {"color": 0xCCFFFFFF}
STYLE_LABEL_SCALE_TOTAL = {"color": 0xFFFFC734}
STYLE_RANDOM_SEED_FIELD = {"margin": 0, "align": "left", "color": 0xCCFFFFFF, ":disabled": {"color": 0x33FFFFFF}}
STYLE_RANDOM_BUTTON = {
    "margin": 0,
    "image_url": f"{PATH_EXTENSION}{PATH_ICON_RANDOM}",
    "background_color": 0x22FFFFFF,
    "color": 0xCCFFFFFF,
    "padding": 2,
    # "border_radius": 3,
    # "border_width": 1,
    "border_color": 0x99FFFFFF,
    ":hovered": {"color": 0xCC000000, "background_color": 0xFFFFFFFF},
    ":disabled": {"color": 0x33FFFFFF, "background_color": 0x0, "border_color": 0x22FFFFFF},
}
STYLE_VECTOR_LABEL = {
    "border_radius": 5,
    "corner_flag": ui.CornerFlag.LEFT,
    "Rectangle::vector_label_x": {"background_color": 0xFF5555AA},
    "Rectangle::vector_label_y": {"background_color": 0xFF76A371},
    "Rectangle::vector_label_z": {"background_color": 0xFFA07D4F},
}

STYLE_WARNING_ICON = {"image_url": f"{PATH_EXTENSION}{PATH_ICON_WARNING}", "color": 0xFF06E2F9, "background_color": 0x0}
