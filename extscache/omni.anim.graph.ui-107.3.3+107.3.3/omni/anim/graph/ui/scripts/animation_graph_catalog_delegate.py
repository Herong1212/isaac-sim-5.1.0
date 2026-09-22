# Copyright (c) 2018-2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["AnimationGraphCatalogTreeDelegate"]

from functools import partial
from omni.ui import color as cl
from pathlib import Path
import omni.ui as ui
from omni.kit.graph.editor.core.graph_editor_core_tree_delegate import GraphEditorCoreTreeDelegate

CURRENT_PATH = Path(__file__).parent
ICON_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.joinpath("icons")


class AnimationGraphCatalogTreeDelegate(GraphEditorCoreTreeDelegate):
    """The delegate for TreeView of OmniGraph"""

    def __init__(self, flat=False):
        super().__init__()
        self._flat = flat
        self._filter_by_text = ""
        self._item_size = 48
        self._icon_size = 40
        self._section_height = 40

    def destroy(self):
        pass

    def build_section_icon(self, model, item, column_id, level, expanded):
        """override the build_section_icon in the graph_editor_core_tree_delegate"""
        icon_model = model.get_item_value_model(item, 2)
        category_model = model.get_item_value_model(item, 4)
        if icon_model and category_model:
            thumbnail = icon_model.as_string
            category = category_model.as_string
            icon_image = self._build_icon(thumbnail, 1, self._icon_size, 9, category)
        ui.Spacer(width=10)

    def _build_rectangle(self, radius, type_name, name, style_override=None):
        """
        Build rectangle of the specific design.

        Args:
            radius: The radius of round corners. The corners are top-left and
                    bottom-right.
            type_name: style_type_name_override of each widget
            name: name of each widget
            style_override: the style to apply to the top level node
        """
        stack = ui.VStack(alignment=ui.Alignment.CENTER)
        if style_override:
            stack.set_style(style_override)

        with stack:
            # Top of the rectangle
            with ui.HStack(height=0):
                ui.Circle(
                    radius=radius,
                    width=0,
                    height=0,
                    size_policy=ui.CircleSizePolicy.FIXED,
                    alignment=ui.Alignment.RIGHT_BOTTOM,
                    style_type_name_override=type_name,
                    name=name
                )
                ui.Rectangle(style_type_name_override=type_name, name=name)

            # Middle of the rectangle
            ui.Rectangle(style_type_name_override=type_name, name=name)

            # Bottom of the rectangle
            with ui.HStack(height=0):
                ui.Rectangle(style_type_name_override=type_name, name=name)
                ui.Circle(
                    radius=radius,
                    width=0,
                    height=0,
                    size_policy=ui.CircleSizePolicy.FIXED,
                    alignment=ui.Alignment.LEFT_TOP,
                    style_type_name_override=type_name,
                    name=name
                )

    def _build_icon(self, thumbnail: str, border, icon_size, radius, category):
        with ui.VStack(width=icon_size):
            ui.Spacer()
            with ui.ZStack(height=icon_size):
                self._build_rectangle(radius, "Graph.Node.Category", category)
                with ui.VStack(width=icon_size, height=icon_size):
                    ui.Spacer(height=border)
                    with ui.HStack():
                        ui.Spacer(width=border)
                        self._build_rectangle(radius - border, "Graph.Node.Icon.Background", category)
                        ui.Spacer(width=border)
                    ui.Spacer(height=border)
                with ui.HStack():
                    ui.Spacer()
                    icon_image = ui.Image(
                        f"{thumbnail}",
                        width=icon_size - border * 2,
                        style_type_name_override="TreeView.Section.Icon",
                        name="Icon")
                    ui.Spacer()
                ui.Spacer()
            ui.Spacer()
        return icon_image

    def build_icon_with_tooltip(self, model, item, column_id, level, expanded):
        """override the build_icon_with_tooltip in the graph_editor_core_tree_delegate"""
        ui.Spacer(width=5)
        icon_model = model.get_item_value_model(item, 2)
        category_model = model.get_item_value_model(item, 4)
        if icon_model and category_model:
            thumbnail = icon_model.as_string
            category = category_model.as_string
            icon_image = self._build_icon(thumbnail, 1, self._icon_size, 9, category)
            icon_image.set_tooltip_fn(lambda: self._build_icon(thumbnail, 2, self._item_size * 2, 20, category))
            tooltip_style = {"Tooltip": {"background_color": cl(0, 0, 0, 0), "border_width": 0, "border_color": cl(0, 0, 0, 0)}}
            icon_image.set_style(tooltip_style)
        ui.Spacer(width=10)
