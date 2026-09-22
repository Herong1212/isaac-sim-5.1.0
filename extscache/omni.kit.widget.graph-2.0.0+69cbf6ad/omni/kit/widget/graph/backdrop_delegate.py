# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""This module provides a `BackdropDelegate` class for implementing node backdrop UI elements in the Omniverse graph widget."""


__all__ = ["BackdropDelegate"]

from .abstract_graph_node_delegate import GraphNodeDescription
from .graph_node_delegate_full import GraphNodeDelegateFull
from .graph_node_delegate_full import LINE_VISIBLE_MIN
from .graph_node_delegate_full import TEXT_VISIBLE_MIN
import omni.ui as ui


class BackdropDelegate(GraphNodeDelegateFull):
    """A class for implementing node backdrop UI elements in the Omniverse graph widget.

    This delegate class extends the functionality of GraphNodeDelegateFull to provide a custom backdrop UI for graph nodes.

    Args:
        scale_factor (float): The factor by which the UI elements are scaled.
    """

    def node_header(self, model, node_desc: GraphNodeDescription):
        """Creates widgets to display at the top of the node.

        Args:
            model: The graph model that contains the node data.
            node_desc (GraphNodeDescription): The graphical description of the node."""
        node = node_desc.node

        def set_color(model, node, item_model):
            sub_models = item_model.get_item_children()
            rgb = (
                item_model.get_item_value_model(sub_models[0]).as_float,
                item_model.get_item_value_model(sub_models[1]).as_float,
                item_model.get_item_value_model(sub_models[2]).as_float,
            )
            model[node].display_color = rgb

        with ui.ZStack(skip_draw_when_clipped=True):
            with ui.VStack():
                self._common_node_header_top(model, node)
            with ui.VStack():
                ui.Spacer(height=23)
                color_widget = ui.ColorWidget(width=20, height=20, style={"margin": 1})
                sub_models = color_widget.model.get_item_children()

                # This constant is BORDER_DEFAULT = 0xFFDBA656
                border_color = model[node].display_color or (0.337, 0.651, 0.859)

                color_widget.model.get_item_value_model(sub_models[0]).as_float = border_color[0]
                color_widget.model.get_item_value_model(sub_models[1]).as_float = border_color[1]
                color_widget.model.get_item_value_model(sub_models[2]).as_float = border_color[2]
                color_widget.model.add_end_edit_fn(lambda m, i: set_color(model, node, m))

    def node_background(self, model, node_desc: GraphNodeDescription):
        """Creates widgets that make up the node background.

        Args:
            model: The graph model that contains the node data.
            node_desc (GraphNodeDescription): The graphical description of the node.

        Raises:
            Exception: If an error occurs in the underlying UI toolkit."""
        node = node_desc.node

        # Constants from GraphNodeDelegateFull.node_background
        MARGIN_WIDTH = 7.5
        MARGIN_TOP = 20.0
        MARGIN_BOTTOM = 25.0

        BORDER_THICKNESS = 3.0
        BORDER_RADIUS = 3.5
        HEADER_HEIGHT = 25.0
        MIN_WIDTH = 180.0
        TRIANGLE = 20.0

        MIN_HEIGHT = 50.0

        def on_size_changed(placer, model, node):
            offset_x = placer.offset_x
            offset_y = placer.offset_y

            model[node].size = (offset_x.value, offset_y.value)

            if offset_x.value < MIN_WIDTH:
                placer.offset_x = MIN_WIDTH
            if offset_y.value < MIN_HEIGHT:
                placer.offset_y = MIN_HEIGHT

        def set_description(field: ui.StringField, model: "GraphModel", node: any, description: str):
            """Called to set the description on the model and  remove the field with the description"""
            model[node].description = description
            field.visible = False

        def on_description(model: "GraphModel", node: any, frame: ui.Frame, description: str):
            """Called to create a field on the node to edit description"""
            with frame:
                field = ui.StringField(multiline=True, style_type_name_override="Graph.Node.Description.Edit")
                if description:
                    field.model.as_string = description
                field.model.add_end_edit_fn(lambda m: set_description(field, model, node, m.as_string))
                field.focus_keyboard()

        width, height = model[node].size or (MIN_WIDTH, MIN_HEIGHT)
        with ui.ZStack(width=0, height=0):
            super().node_background(model, node_desc)

            # Properly alighned description
            with ui.VStack():
                ui.Spacer(height=HEADER_HEIGHT + MARGIN_TOP)
                with ui.HStack():
                    ui.Spacer(width=MARGIN_WIDTH + BORDER_THICKNESS)
                    with ui.ZStack():
                        description = model[node].description
                        if description:
                            ui.Label(
                                description,
                                alignment=ui.Alignment.LEFT_TOP,
                                style_type_name_override="Graph.Node.Description",
                            )

                        # Frame with description field
                        frame = ui.Frame()
                        frame.set_mouse_double_clicked_fn(
                            lambda x, y, b, m, f=frame, d=description: on_description(model, node, f, d)
                        )
                    ui.Spacer(width=MARGIN_WIDTH + BORDER_THICKNESS)
                ui.Spacer(height=MARGIN_BOTTOM + BORDER_THICKNESS)

            # The triangle that resizes the node
            with ui.VStack():
                with ui.HStack():
                    placer = ui.Placer(draggable=True)
                    placer.offset_x = width
                    placer.offset_y = height
                    placer.set_offset_x_changed_fn(lambda _, p=placer, m=model, n=node: on_size_changed(p, m, n))
                    placer.set_offset_y_changed_fn(lambda _, p=placer, m=model, n=node: on_size_changed(p, m, n))
                    with placer:
                        triangle = ui.Triangle(
                            width=TRIANGLE,
                            height=TRIANGLE,
                            alignment=ui.Alignment.RIGHT_TOP,
                            style_type_name_override="Graph.Node.Resize",
                        )
                        triangle.set_mouse_pressed_fn(lambda x, y, b, m: b == 0 and model.size_begin_edit(node))
                        triangle.set_mouse_released_fn(lambda x, y, b, m: b == 0 and model.size_end_edit(node))
                    ui.Spacer(width=MARGIN_WIDTH + 0.5 * BORDER_THICKNESS)
                ui.Spacer(height=MARGIN_BOTTOM + BORDER_THICKNESS)

    def node_footer(self, model, node_desc: GraphNodeDescription):
        """A placeholder for creating widgets at the bottom of the node.

        Args:
            model: The graph model that contains the node data.
            node_desc (GraphNodeDescription): The graphical description of the node."""
        pass
