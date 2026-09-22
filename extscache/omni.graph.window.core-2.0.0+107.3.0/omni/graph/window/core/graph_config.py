# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import re
from functools import lru_cache
from pathlib import Path
from typing import List, Optional, Tuple

import carb
import carb.settings
import omni.graph.core as og
import omni.graph.tools.ogn as ogn
import OmniGraphSchema

from .extension import _is_kit_version_or_greater


class Paths:
    EXT_PATH = Path(__file__).parent.parent.parent.parent.parent
    ICON_PATH = EXT_PATH.joinpath("icons")


class Supports:
    @classmethod
    @lru_cache(maxsize=None)
    def compound_graphs(cls) -> bool:
        """Returns whether compound nodes and graphs are supported in the associated version of kit."""
        return _is_kit_version_or_greater((105, 1))

    @classmethod
    def compound_subgraphs(cls) -> bool:
        """Returns whether compound subgraphs are supported in the associated version of kit"""
        return hasattr(og, "_unstable") and callable(
            getattr(og._unstable.cmds, "CreateCompoundSubgraph", None)  # noqa: protected-access
        )

    @classmethod
    def compound_node_api(cls) -> bool:
        """Returns whether the omnigraph schema supports the compound node api"""
        return OmniGraphSchema.CompoundNodeAPI


class Settings:
    @staticmethod
    def set_default_settings():
        """Set up defaults for the settings that are owned by this extension"""
        settings = carb.settings.get_settings()
        settings.set_default_bool("/persistent/omnigraph/showNameAsType", True)

    @staticmethod
    def cull_legacy_prims() -> bool:
        """When True we will not add legacy prim OG nodes to the graph"""
        return True

    @staticmethod
    def is_legacy_prim_enabled(*args) -> bool:
        """Is the legacy prim creation drop menu enabled"""
        return carb.settings.get_settings().get("/persistent/omnigraph/createPrimNodes")

    @staticmethod
    def is_all_attributes_drop_enabled(*args) -> bool:
        """Is the ReadPrim/WritePrim prim drop menu enabled"""
        # FIXME: For now we will use the omni.graph.core createPrimNodes setting for this as well
        return carb.settings.get_settings().get("/persistent/omnigraph/createPrimNodes")

    @staticmethod
    def get_show_name_as_type():
        return carb.settings.get_settings().get_as_bool("/persistent/omnigraph/showNameAsType")

    @staticmethod
    def set_show_name_as_type(value: bool):
        carb.settings.get_settings().set("/persistent/omnigraph/showNameAsType", value)

    @staticmethod
    def is_schema_prims_enabled(*args) -> bool:
        """Are the OG schema prims (e.g. OmniGraphNode instead of ComputeNode) enabled"""
        try:
            return og.Settings()(og.Settings.USE_SCHEMA_PRIMS)
        except Exception:  # noqa: PLW0703
            # This setting has been removed in Kit 105 and the above call will generate an exception.
            # In this case there is no longer an option and schema prims are always enabled.
            return True

    @staticmethod
    def are_compounds_enabled(*args) -> bool:
        """Checks to see whether the compound feature is enabled"""
        return Supports.compound_graphs()

    @staticmethod
    def are_compound_node_types_enabled(*args) -> bool:
        """Checks to see whether the compound node types feature is enabled"""
        return carb.settings.get_settings().get_as_bool("/app/omnigraph/compoundNodeTypes")

    @staticmethod
    def is_target_mapping_enabled() -> bool:
        return carb.settings.get_settings().get_as_bool("/app/omnigraph/targetMapping")


# ------------------------------------------------------------------------------------
# Color utils


def rgb_to_abgr(rgb: int) -> int:
    """Convert RGB value to ABGR, which is what omni.ui wants"""
    a = 0xFF
    b = rgb & 0xFF
    g = (rgb >> 8) & 0xFF
    r = (rgb >> 16) & 0xFF
    return (a << 24) | (b << 16) | (g << 8) | r


def lerp_component(color: int, fixed_color: int) -> int:
    """Lerp a value to the fixed color"""
    return int(color + 0.5 * (fixed_color - color))


def lerp_color_to_secondary(rgb: int) -> int:
    """Calculate secondary from primary color
    This is defined as a desaturation of the primary color. One way to do this is to simply
    lerp the color towards grey. In our case half-way to #1F2123.
    """
    b = rgb & 0xFF
    g = (rgb >> 8) & 0xFF
    r = (rgb >> 16) & 0xFF
    return lerp_component(b, 0x23) | (lerp_component(g, 0x21) << 8) | (lerp_component(r, 0x1F) << 16)


def lerp_abgr_to_secondary(abgr: int, secondary: int = 0x23211F) -> int:
    """Calculate secondary from primary color, leaving the alpha as is
    This is defined as a desaturation of the primary color. One way to do this is to simply
    lerp the color towards grey. In our case half-way to #1F2123.
    """
    r = abgr & 0xFF
    g = (abgr >> 8) & 0xFF
    b = (abgr >> 16) & 0xFF
    a = (abgr >> 24) & 0xFF

    lr = (secondary) & 0xFF
    lg = (secondary >> 8) & 0xFF
    lb = (secondary >> 16) & 0xFF

    return (a << 24) | (lerp_component(b, lb) << 16) | (lerp_component(g, lg) << 8) | lerp_component(r, lr)


# ------------------------------------------------------------------------------------
# shared constants

ERROR_BACKGROUND_COLOR = rgb_to_abgr(0xCB6A6A)
ERROR_HIGHLIGHT_COLOR = rgb_to_abgr(0xAF4E4E)
WARNING_BACKGROUND_COLOR = rgb_to_abgr(0xDFCB4A)
WARNING_HIGHLIGHT_COLOR = rgb_to_abgr(0xA19337)
WARNING_LABEL_COLOR = rgb_to_abgr(0x292929)
EXPANSION_ON_COLOR_ABGR = 0xFFA8A8A8
EXPANSION_OFF_COLOR_ABGR = 0xFF23211F
COMPOUND_BACKGROUND_COLOR_ABGR = 0xFF5F5F5F

# ------------------------------------------------------------------------------------

DATA_TYPE_TO_COLOR = {
    og.BaseDataType.BOOL: 0xFF1C1CE2,
    og.BaseDataType.HALF: 0xFFADFB47,
    og.BaseDataType.DOUBLE: 0xFF67A515,
    og.BaseDataType.FLOAT: 0xFF88CF2A,
    og.BaseDataType.INT: 0xFF5F5FE5,
    og.BaseDataType.INT64: 0xFF4040D2,
    og.BaseDataType.UINT: 0xFF2525B5,
    og.BaseDataType.UINT64: 0xFF101081,
    og.BaseDataType.TOKEN: 0xFF9C3ACC,
    og.BaseDataType.RELATIONSHIP: 0xFFCD7A3A,  # Bundle
    og.BaseDataType.PRIM: 0xFFCD7A3A,  # Bundle
    og.BaseDataType.UCHAR: 0xFF781FA5,
    og.BaseDataType.UNKNOWN: 0xFFFFFFFF,
    og.BaseDataType.CONNECTION: 0xFFFFFFFF,
    og.BaseDataType.TAG: 0xFFFFFFFF,
}


def type_to_color(type_name: str, defaultColor: int = 0xFFFFFFFF) -> int:  # noqa: N803
    """Converts the data type as a string to a color"""
    tp = og.AttributeType.type_from_ogn_type_name(type_name)
    return DATA_TYPE_TO_COLOR.get(tp.base_type, defaultColor)


# ------------------------------------------------------------------------------------


class CategoryStyles:
    # The special prefix we treat as a filter by convention. For example "graph:action" is not the category of the node
    # as such, instead it is a flag that this node is specific to Action Graphs.
    graph_filter_category_prefix = "graph"

    # Special style for the help icon that appears when hovering - must be an illegal node type name
    HELP_TYPE = "__help__"

    """
    Hard coded category metadata. FIXME: This should be part of the category info ABI
    The data is: category name => (primary color, icon_path, secondary color)
    Note: color literals are RGB but data is stored as ABGR, secondary color is calculated from primary
    """
    STYLE_BY_CATEGORY = {
        k: (rgb_to_abgr(v[0]), v[1], rgb_to_abgr(lerp_color_to_secondary(v[0])))
        for k, v in {
            "animation": (0x56A6DB, f"{Paths.ICON_PATH}/node/type_animation_noBorder_dark.svg"),
            "bundle": (0xA29686, f"{Paths.ICON_PATH}/node/type_bundle_noBorder_dark.svg"),
            "character": (0x56A6DB, f"{Paths.ICON_PATH}/node/type_character_noBorder_dark.svg"),
            "Compounds": (0x00719A, f"{Paths.ICON_PATH}/node/type_compound_noBorder_dark.svg"),
            "constants": (0x80A18F, f"{Paths.ICON_PATH}/node/type_constant_noBorder_dark.svg"),
            "debug": (0x9F566C, f"{Paths.ICON_PATH}/node/type_debug_noBorder_dark.svg"),
            "event": (0x20BF7A, f"{Paths.ICON_PATH}/node/type_event_noBorder_dark.svg"),
            "flowControl": (0x747C57, f"{Paths.ICON_PATH}/node/type_flow_noBorder_dark.svg"),
            "function": (0x47FBAD, f"{Paths.ICON_PATH}/node/type_function_noBorder_dark.svg"),
            "generic": (0x9B9B9B, f"{Paths.ICON_PATH}/node/type_generic_noBorder_dark.svg"),
            "geometry": (0x536B57, f"{Paths.ICON_PATH}/node/type_geometry_noBorder_dark.svg"),
            "input": (0xE55FCE, f"{Paths.ICON_PATH}/node/type_input_noBorder_dark.svg"),
            "InputNode": (0xFF7C7457, f"{Paths.ICON_PATH}/node/type_scene_graph_noBorder_dark.svg"),
            "io": (0xEE874D, f"{Paths.ICON_PATH}/node/type_io_noBorder_dark.svg"),
            "material": (0x9C7EB9, f"{Paths.ICON_PATH}/node/type_material_noBorder_dark.svg"),
            "math": (0x4A8A53, f"{Paths.ICON_PATH}/node/type_math_noBorder_dark.svg"),
            "OutputNode": (0xFF7C7457, f"{Paths.ICON_PATH}/node/type_scene_graph_noBorder_dark.svg"),
            "rendering": (0x8D2DC5, f"{Paths.ICON_PATH}/node/type_rendering_noBorder_dark.svg"),
            "sceneGraph": (0x57747C, f"{Paths.ICON_PATH}/node/type_scene_graph_noBorder_dark.svg"),
            "script": (0x9F5B56, f"{Paths.ICON_PATH}/node/type_script_noBorder_dark.svg"),
            "texture": (0x9C7EB9, f"{Paths.ICON_PATH}/node/type_texture_noBorder_dark.svg"),
            "tutorials": (0xD9AC5E, f"{Paths.ICON_PATH}/node/type_tutorial_noBorder_dark.svg"),
            "time": (0x56A6DB, f"{Paths.ICON_PATH}/node/type_time_noBorder_dark.svg"),
            "ui": (0x9E8A58, f"{Paths.ICON_PATH}/node/type_ui_noBorder_dark.svg"),
            HELP_TYPE: (0xC9C9C9, f"{Paths.ICON_PATH}/node/type_help_noBorder_dark.svg"),
        }.items()
    }

    @staticmethod
    def _checked_get_graph_filter_from_category(category_tag: str) -> Optional[str]:
        """Returns the graph filter graph type if the given category is in fact a graph filter, otherwise
        return None
        Args:
            category_tag The category tag for example "graph:action" or "math:operator"
        Returns:
            None if the given tag is not a graph filter, or the graph type if it is ("action" in first example)
        """
        category_parts = category_tag.split(":")
        if (len(category_parts) > 1) and category_parts[0] == CategoryStyles.graph_filter_category_prefix:
            return category_parts[1]
        return None

    @staticmethod
    def get_style_for_node_type(node_type_name: str) -> Tuple[int, str, int]:
        """Return the style for the given node type, or fallback style if not found
        Returns (primary color, icon_path, secondary color)
        NOTE: Colors are in ABGR format
        """
        node_type = og.get_node_type(node_type_name)
        if not node_type:
            carb.log_warn(f"OmniGraph node type {node_type_name} not found")
            return None
        color, fallback_icon_path, second_color = CategoryStyles.STYLE_BY_CATEGORY["generic"]
        icon_path = node_type.get_metadata(ogn.MetadataKeys.ICON_PATH)
        if icon_path and (not Path(icon_path).is_file()):
            carb.log_warn(f"icon path {icon_path} not found for OmniGraph node type {node_type_name}")
            icon_path = None
        category_metadata = node_type.get_metadata(ogn.MetadataKeys.CATEGORIES)
        if category_metadata:
            categories = category_metadata.split(",")
            categories = [c for c in categories if CategoryStyles._checked_get_graph_filter_from_category(c) is None]
            if categories:
                # We only use the primary category
                prim_category = categories[0].split(":")[0]
                category_info = CategoryStyles.STYLE_BY_CATEGORY.get(prim_category, None)
                if category_info:
                    color, cat_icon_path, second_color = category_info
                    if (not icon_path) and Path(cat_icon_path).is_file():
                        icon_path = cat_icon_path
        if not icon_path:
            icon_path = fallback_icon_path

        return (color, icon_path, second_color)

    @staticmethod
    def modify_background_color_for_node_type(node_type_name, color: int) -> Optional[int]:
        """
        Returns a custom background color for a node type, given a desired foreground color.
        If the node type does not require a custom background color, None is returned.
        NOTE: Colors are in ABGR format
        """
        node_type = og.get_node_type(node_type_name)
        if not node_type:
            carb.log_warn(f"OmniGraph node type {node_type_name} not found")
            return None

        # compound nodes use a different blend for the secondary color
        background_color = None
        if hasattr(node_type, "is_compound_node_type") and node_type.is_compound_node_type():
            background_color = lerp_abgr_to_secondary(color, COMPOUND_BACKGROUND_COLOR_ABGR)

        return background_color


# ------------------------------------------------------------------------------------
# Naming utils


# Since the graph builds UI for nodes even when they're not visible we could be looking at hundreds of
# thousands of calls whenever the layout is rebuilt. So we'll cache the results to reduce overhead.
@lru_cache(maxsize=100000)
def make_nice_name(ugly_name: str, preserve_final_part: bool = False):
    """
    Takes a raw name and formats it for use as the corresponding nice name in the UI.

    o  (For attribute names) Standard namespaces ('inputs', 'outputs', 'state') are stripped off the front.
    o  (For attribute names) Any remaining namespaces are converted to words within the name.
    o  Underscores are converted to spaces.
    o  Mixed-case words are broken into separate words (e.g. 'primaryRGBColor' -> 'primary RGB Color').
    o  Words which are all lower-case are capitalized (e.g. 'primary' -> 'Primary').

    If 'preserve_final_part' is True then the portion of 'ugly_name' after the last namespace is left as-is.
    """

    def split_mixed_case(word: str) -> List[str]:
        # Lower-case followed by upper-case splits before first upper. E.g. 'usdPrim' -> 'usd Prim'
        # Upper-case followed by lower-case splits before last upper. E.g: 'USDPrim' -> 'USD Prim'
        # Combined example: abcDEFgHi -> abc DE Fg Hi
        result = []
        sub_word = ""
        uppers = ""
        for c in word:
            if c.isupper():
                if not uppers and sub_word:
                    result += [sub_word]
                    sub_word = ""
                uppers += c
            else:
                if len(uppers) > 1:
                    result += [uppers[:-1]]
                sub_word += uppers[-1:] + c
                uppers = ""

        if sub_word:
            result += [sub_word]
        elif uppers:
            result += [uppers]
        return result

    # Split out namespaces
    parts = ugly_name.split(":")
    # If the first namespace is one of our standard ones, get rid of it.
    if len(parts) > 1 and parts[0] in ("inputs", "outputs", "state"):
        parts = parts[1:]
    # If the user provided an explicit name then we shouldn't mess with that at all. Don't title case it or remove
    # namespace separators, just return it
    final_part = None
    if preserve_final_part:
        return ":".join(parts)
    parts_out = []
    for part in parts:
        words = part.replace("_", " ").split(" ")
        for word in words:
            if word.islower() or word.isupper():
                parts_out += [word]
            else:
                parts_out += split_mixed_case(word)
    # Title-case any words which are all lower case.
    parts_out = [part.title() if part.islower() else part for part in parts_out]

    if final_part:
        parts_out += [final_part]

    return " ".join(parts_out)


# Alternative method to make nice names:
_split_camel_reg = re.compile(r"[A-Z](?:[a-z0-9]+|[A-Z]*(?=[A-Z]|$))")


def camel_case_split(name: str) -> List[str]:
    """Return a list of camel-case delimited parts of the given name"""
    if not name:
        return []
    name_part = name[0].upper() + name[1:]
    return _split_camel_reg.findall(name_part)


def make_title_case(name: str) -> str:
    """Convert a camel-case name to a title-case equivalent"""
    return " ".join(camel_case_split(name))


# ------------------------------------------------------------------------------------
