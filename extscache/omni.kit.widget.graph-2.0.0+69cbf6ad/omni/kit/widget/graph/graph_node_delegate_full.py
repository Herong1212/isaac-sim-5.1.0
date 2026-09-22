# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""This module provides the GraphNodeDelegateFull class for creating styled graph node UI elements in NVIDIA Omniverse applications."""


__all__ = ["color_to_hex", "GraphNodeDelegateFull"]

from .abstract_graph_node_delegate import AbstractGraphNodeDelegate
from .abstract_graph_node_delegate import GraphConnectionDescription
from .abstract_graph_node_delegate import GraphNodeDescription
from .abstract_graph_node_delegate import GraphPortDescription
from .graph_model import GraphModel
from functools import partial
import colorsys
import math
import omni.ui as ui


# Zoom level when the text disappears and the replacement line appears
TEXT_VISIBLE_MIN = 0.6
# Zoom level when the line disappears
LINE_VISIBLE_MIN = 0.15

CONNECTION_CURVE = 60
MARGIN_WIDTH = 7.5


def color_to_hex(color: tuple) -> int:
    """Converts a color from floating-point RGB(A) format to a hexadecimal integer.

    Args:
        color (tuple): A tuple representing the color in RGB(A) format. Each component is a
                       float in the range [0.0, 1.0], where the optional fourth element is the alpha
                       value. If the alpha value is not provided, it defaults to 1.0 (fully opaque).

    Returns:
        int: The color encoded as a hexadecimal integer in the form 0xAARRGGBB, where AA is
             the alpha component, RR is the red component, GG is the green component, and BB
             is the blue component.
    """

    def to_int(f: float) -> int:
        return int(255 * max(0.0, min(1.0, f)))

    red = to_int(color[0])
    green = to_int(color[1])
    blue = to_int(color[2])
    alpha = to_int(color[3]) if len(color) > 3 else 255
    return (alpha << 8 * 3) + (blue << 8 * 2) + (green << 8 * 1) + red


class GraphNodeDelegateFull(AbstractGraphNodeDelegate):
    """A delegate class for graph node UI elements with Omniverse design.

    This class provides methods for creating and styling various parts of a graph node interface, such as headers, footers, ports, and connections. It extends AbstractGraphNodeDelegate and follows the design conventions of NVIDIA Omniverse applications.

    Args:
        scale_factor (float): A multiplier for scaling the UI elements of the graph node."""

    def __init__(self, scale_factor=1.0):
        """Initializes the GraphNodeDelegateFull with an optional scale factor."""
        self._scale_factor = scale_factor

    def __scale(self, value):
        """Return the value multiplied by global scale multiplier"""
        return value * self._scale_factor

    def __build_rectangle(self, radius, width, height, draw_top, style_name, name, style_override=None):
        """
        Build rectangle of the specific design.

        Args:
            radius: The radius of round corers. The corners are top-left and
                    bottom-right.
            width: The width of triangle to cut. The top-right and
                   bottom-left trialgles are cut.
            height: The height of triangle to cut. The top-right and
                    bottom-left trialgles are cut.
            draw_top: When false the top corners are straight.
            style_name: style_type_name_override of each widget
            name: name of each widget
            style_override: the style to apply to the top level node
        """
        stack = ui.VStack()
        if style_override:
            stack.set_style(style_override)

        with stack:
            # Top of the rectangle
            if draw_top:
                with ui.HStack(height=0):
                    with ui.VStack(width=0):
                        ui.Circle(
                            radius=radius,
                            width=0,
                            height=0,
                            size_policy=ui.CircleSizePolicy.FIXED,
                            alignment=ui.Alignment.RIGHT_BOTTOM,
                            style_type_name_override=style_name,
                            name=name,
                        )
                        ui.Rectangle(style_type_name_override=style_name, name=name)
                    ui.Rectangle(style_type_name_override=style_name, name=name)
                    ui.Triangle(
                        width=width,
                        height=height,
                        alignment=ui.Alignment.LEFT_TOP,
                        style_type_name_override=style_name,
                        name=name,
                    )

            # Middle of the rectangle
            ui.Rectangle(style_type_name_override=style_name, name=name)

            # Bottom of the rectangle
            with ui.HStack(height=0):
                ui.Triangle(
                    width=width,
                    height=height,
                    alignment=ui.Alignment.RIGHT_BOTTOM,
                    style_type_name_override=style_name,
                    name=name,
                )
                ui.Rectangle(style_type_name_override=style_name, name=name)
                with ui.VStack(width=0):
                    ui.Rectangle(style_type_name_override=style_name, name=name)
                    ui.Circle(
                        radius=radius,
                        width=0,
                        height=0,
                        size_policy=ui.CircleSizePolicy.FIXED,
                        alignment=ui.Alignment.LEFT_TOP,
                        style_type_name_override=style_name,
                        name=name,
                    )

    # TODO: build_node_footer_input/build_node_footer_output
    def node_background(self, model, node_desc: GraphNodeDescription):
        """Called to create widgets of the node background.

        Args:
            model: The graph model containing the node data.
            node_desc (GraphNodeDescription): Description of the node to create background for."""
        node = node_desc.node

        # Constants
        MARGIN_TOP = 20.0
        MARGIN_BOTTOM = 25.0

        BORDER_THICKNESS = 3.0
        BORDER_RADIUS = 3.5
        HEADER_HEIGHT = 25.0
        MIN_WIDTH = 180.0
        TRIANGLE = 20.0

        # Computed values
        left_right_offset = MARGIN_WIDTH - BORDER_THICKNESS * 0.5
        outer_radius = BORDER_RADIUS + BORDER_THICKNESS * 0.5
        inner_radius = BORDER_RADIUS - BORDER_THICKNESS * 0.5

        # The size of the triangle
        outer_triangle = TRIANGLE
        # The size of the triangle to make the thickness of the diagonal line
        # the same as horizontal and vertial thickness. Works only with 45
        # degrees diagonals
        inner_triangle = outer_triangle - BORDER_THICKNESS / (
            math.sqrt(2) * math.tan(math.radians((180.0 - 45.0) / 2.0))
        )

        style_name = str(model[node].type)

        # Draw a rectangle and a top line
        with ui.HStack():
            # Left offset
            ui.Spacer(width=self.__scale(left_right_offset))

            with ui.VStack():
                ui.Spacer(height=self.__scale(MARGIN_TOP))

                # The node body
                with ui.ZStack():
                    # This trick makes min width
                    ui.Spacer(width=self.__scale(MIN_WIDTH))

                    # The color override for the border
                    border_color = model[node].display_color
                    if border_color:
                        style = {"Graph.Node.Border": {"background_color": color_to_hex(border_color)}}
                    else:
                        style = None

                    # Build outer rectangle
                    self.__build_rectangle(
                        self.__scale(outer_radius),
                        self.__scale(outer_triangle),
                        self.__scale(outer_triangle),
                        True,
                        "Graph.Node.Border",
                        style_name,
                        style,
                    )

                    # Build inner rectangle
                    with ui.VStack():
                        ui.Spacer(height=self.__scale(HEADER_HEIGHT))
                        with ui.HStack():
                            ui.Spacer(width=self.__scale(BORDER_THICKNESS))

                            if border_color:
                                # 140% lightness from the border color
                                # 50% saturation from the border color
                                L_MULT = 1.4
                                S_MULT = 0.5
                                hls = colorsys.rgb_to_hls(border_color[0], border_color[1], border_color[2])
                                rgb = colorsys.hls_to_rgb(hls[0], min(1.0, (hls[1] * L_MULT)), hls[2] * S_MULT)
                                if len(border_color) > 3:  # alpha
                                    rgb = rgb + (border_color[3],)
                                style = {"background_color": color_to_hex(rgb)}
                            else:
                                style = None

                            self.__build_rectangle(
                                self.__scale(inner_radius),
                                self.__scale(inner_triangle),
                                self.__scale(inner_triangle),
                                False,
                                "Graph.Node.Background",
                                style_name,
                                style,
                            )
                            ui.Spacer(width=self.__scale(BORDER_THICKNESS))
                        ui.Spacer(height=self.__scale(BORDER_THICKNESS))

                ui.Spacer(height=self.__scale(MARGIN_BOTTOM))

            # Right offset
            ui.Spacer(width=self.__scale(left_right_offset))

    def node_header_input(self, model, node_desc: GraphNodeDescription):
        """Called to create the left part of the header that will be used as input when the node is collapsed.

        Args:
            model: The graph model containing the node data.
            node_desc (GraphNodeDescription): Description of the node to create header input for."""
        ui.Spacer(width=self.__scale(8))

    def node_header_output(self, model, node_desc: GraphNodeDescription):
        """Called to create the right part of the header that will be used as output when the node is collapsed.

        Args:
            model: The graph model containing the node data.
            node_desc (GraphNodeDescription): Description of the node to create header output for."""
        ui.Spacer(width=self.__scale(8))

    def _common_node_header_top(self, model, node):
        """Node header part that is used in both full and closed states"""

        def switch_expansion(model, node):
            current = model[node].expansion_state
            model[node].expansion_state = GraphModel.ExpansionState((current.value + 1) % 3)

        # Draw the node name and a bit of space
        with ui.ZStack(width=0):
            ui.Label(model[node].name, style_type_name_override="Graph.Node.Header.Label", visible_min=TEXT_VISIBLE_MIN)
            with ui.Placer(stable_size=True, visible_min=LINE_VISIBLE_MIN, visible_max=TEXT_VISIBLE_MIN, offset_y=-8):
                ui.Label(model[node].name, name="Degenerated", style_type_name_override="Graph.Node.Header.Label")
        with ui.HStack():
            # Collapse button
            collapse = ui.ImageWithProvider(
                width=self.__scale(18), height=self.__scale(18), style_type_name_override="Graph.Node.Header.Collapse"
            )

            expansion_state = model[node].expansion_state
            if expansion_state == GraphModel.ExpansionState.CLOSED:
                collapse.name = "Closed"
            elif expansion_state == GraphModel.ExpansionState.MINIMIZED:
                collapse.name = "Minimized"
            else:
                collapse.name = "Open"

            collapse.set_mouse_pressed_fn(lambda x, y, b, m, model=model, node=node: switch_expansion(model, node))

    def node_header(self, model, node_desc: GraphNodeDescription):
        """Called to create widgets of the top of the node.

        Args:
            model: The graph model containing the node data.
            node_desc (GraphNodeDescription): Description of the node to create header for."""
        with ui.VStack(skip_draw_when_clipped=True):
            self._common_node_header_top(model, node_desc.node)
            ui.Spacer(height=self.__scale(8))

    def node_footer(self, model, node_desc: GraphNodeDescription):
        """Called to create widgets of the bottom of the node.

        Args:
            model: The graph model containing the node data.
            node_desc (GraphNodeDescription): Description of the node to create footer for."""
        node = node_desc.node

        style_name = str(model[node].type)

        # Draw the circle and the image on the top of it
        with ui.VStack(visible_min=LINE_VISIBLE_MIN, skip_draw_when_clipped=True):
            ui.Spacer(height=self.__scale(10))
            with ui.HStack(height=0):
                ui.Spacer()
                with ui.ZStack(width=self.__scale(50), height=self.__scale(50)):
                    ui.Rectangle(
                        style_type_name_override="Graph.Node.Footer", name=style_name, visible_min=TEXT_VISIBLE_MIN
                    )
                    ui.ImageWithProvider(
                        style_type_name_override="Graph.Node.Footer.Image",
                        name=style_name,
                        visible_min=TEXT_VISIBLE_MIN,
                    )
                    # Scale up the icon when zooming out
                    with ui.Placer(
                        stable_size=True,
                        visible_min=LINE_VISIBLE_MIN,
                        visible_max=TEXT_VISIBLE_MIN,
                        offset_x=self.__scale(-15),
                        offset_y=self.__scale(-30),
                    ):
                        with ui.ZStack(width=0, height=0):
                            ui.Rectangle(style_type_name_override="Graph.Node.Footer", name=style_name)
                            ui.ImageWithProvider(
                                style_type_name_override="Graph.Node.Footer.Image",
                                name=style_name,
                                width=self.__scale(80),
                                height=self.__scale(80),
                            )
                ui.Spacer()
            ui.Spacer(height=self.__scale(2))

    def port_input(self, model, node_desc: GraphNodeDescription, port_desc: GraphPortDescription):
        """Called to create the left part of the port that will be used as input.

        Args:
            model: The graph model containing the node data.
            node_desc (GraphNodeDescription): Description of the node containing the port.
            port_desc (GraphPortDescription): Description of the port."""
        node = node_desc.node
        port = port_desc.port
        connected_source = port_desc.connected_source
        connected_target = port_desc.connected_target

        if port is None:
            ui.Spacer(width=self.__scale(7.5))
            return

        outputs = model[port].outputs
        is_output = outputs is not None
        if is_output:
            ui.Spacer(width=self.__scale(7.5))
            return

        style_type_name = "Graph.Node.Port.Input"
        customcolor_style_type_name = "Graph.Node.Port.Input.CustomColor"
        inputs = model[port].inputs

        node_type = str(model[node].type)
        port_type = str(model[port].type)

        with ui.HStack(skip_draw_when_clipped=True):
            ui.Spacer(width=self.__scale(6))
            with ui.ZStack(width=self.__scale(8)):
                if inputs is not None:
                    # Half-circle that shows the port is able to have input connection
                    # Background of the node color
                    ui.Circle(
                        radius=self.__scale(6),
                        name=node_type,
                        style_type_name_override=style_type_name,
                        size_policy=ui.CircleSizePolicy.FIXED,
                        style={"border_color": 0x0, "border_width": 0},
                        alignment=ui.Alignment.LEFT_CENTER,
                        arc=ui.Alignment.RIGHT,
                        visible_min=TEXT_VISIBLE_MIN,
                    )
                    # Port has unique color
                    ui.Circle(
                        radius=self.__scale(6),
                        name=port_type,
                        style_type_name_override=customcolor_style_type_name,
                        size_policy=ui.CircleSizePolicy.FIXED,
                        alignment=ui.Alignment.LEFT_CENTER,
                        arc=ui.Alignment.RIGHT,
                        visible_min=TEXT_VISIBLE_MIN,
                    )
                    # Border of the node color
                    ui.Circle(
                        radius=self.__scale(6),
                        name=node_type,
                        style_type_name_override=style_type_name,
                        size_policy=ui.CircleSizePolicy.FIXED,
                        style={"background_color": 0x0},
                        alignment=ui.Alignment.LEFT_CENTER,
                        arc=ui.Alignment.RIGHT,
                        visible_min=TEXT_VISIBLE_MIN,
                    )
                if connected_source:
                    # Circle that shows that the port is a source for the connection
                    ui.Circle(
                        radius=self.__scale(7),
                        name=port_type,
                        size_policy=ui.CircleSizePolicy.FIXED,
                        style_type_name_override="Graph.Connection",
                        alignment=ui.Alignment.LEFT_CENTER,
                        visible_min=TEXT_VISIBLE_MIN,
                    )
                if connected_target:
                    # Circle that shows that the port is a target for the connection
                    ui.Circle(
                        radius=self.__scale(5),
                        name=port_type,
                        size_policy=ui.CircleSizePolicy.FIXED,
                        style_type_name_override="Graph.Connection",
                        alignment=ui.Alignment.LEFT_CENTER,
                        visible_min=TEXT_VISIBLE_MIN,
                    )

    def port_output(self, model, node_desc: GraphNodeDescription, port_desc: GraphPortDescription):
        """Called to create the right part of the port that will be used as output.

        Args:
            model: The graph model containing the node data.
            node_desc (GraphNodeDescription): Description of the node containing the port.
            port_desc (GraphPortDescription): Description of the port."""
        node = node_desc.node
        port = port_desc.port
        connected_source = port_desc.connected_source
        connected_target = port_desc.connected_target

        if port is None:
            ui.Spacer(width=self.__scale(7.5))
            return

        style_type_name = "Graph.Node.Port.Output"
        customcolor_style_type_name = "Graph.Node.Port.Output.CustomColor"
        outputs = model[port].outputs
        inputs = model[port].inputs

        node_type = str(model[node].type)
        port_type = str(model[port].type)

        with ui.ZStack(width=self.__scale(16), skip_draw_when_clipped=True):
            if outputs is not None:
                # Circle that shows the port is able to be an output connection
                # Background of the node color
                ui.Circle(
                    name=node_type,
                    style_type_name_override=style_type_name,
                    alignment=ui.Alignment.CENTER,
                    radius=self.__scale(6),
                    size_policy=ui.CircleSizePolicy.FIXED,
                    visible_min=TEXT_VISIBLE_MIN,
                )
                # Port has unique color
                ui.Circle(
                    name=port_type,
                    style_type_name_override=customcolor_style_type_name,
                    style={"background_color": 0x0},
                    alignment=ui.Alignment.CENTER,
                    radius=self.__scale(6),
                    size_policy=ui.CircleSizePolicy.FIXED,
                    visible_min=TEXT_VISIBLE_MIN,
                )
            if connected_source and inputs is None:
                # Circle that shows that the port is a source for the connection
                ui.Circle(
                    radius=self.__scale(7),
                    name=port_type,
                    size_policy=ui.CircleSizePolicy.FIXED,
                    style_type_name_override="Graph.Connection",
                    alignment=ui.Alignment.CENTER,
                    visible_min=TEXT_VISIBLE_MIN,
                )
            if connected_target or (outputs == [] and inputs):
                # Circle that shows that the port is a target for the connection
                ui.Circle(
                    radius=self.__scale(5),
                    name=port_type,
                    size_policy=ui.CircleSizePolicy.FIXED,
                    style_type_name_override="Graph.Connection",
                    alignment=ui.Alignment.CENTER,
                    visible_min=TEXT_VISIBLE_MIN,
                )

    def port(self, model, node_desc: GraphNodeDescription, port_desc: GraphPortDescription):
        """Called to create the middle part of the port.

        Args:
            model: The graph model containing the node data.
            node_desc (GraphNodeDescription): Description of the node containing the port.
            port_desc (GraphPortDescription): Description of the port."""

        def set_expansion_state(model, port, state: GraphModel.ExpansionState, *args):
            model[port].expansion_state = state

        port = port_desc.port
        level = port_desc.level

        if port is None:
            return

        sub_ports = model[port].ports
        is_group = sub_ports is not None

        inputs = model[port].inputs
        outputs = model[port].outputs
        is_input = inputs is not None
        is_output = outputs is not None
        style_name = "input" if is_input and not is_output else "output"
        with ui.HStack(skip_draw_when_clipped=True):
            if level > 0:
                style_type_name_override = "Graph.Node.Port.Branch"
                if port_desc.relative_position == port_desc.parent_child_count - 1:
                    ui.Line(
                        width=4,
                        height=ui.Percent(50),
                        style_type_name_override=style_type_name_override,
                        alignment=ui.Alignment.RIGHT,
                        visible_min=TEXT_VISIBLE_MIN,
                    )
                else:
                    ui.Line(
                        width=4,
                        style_type_name_override=style_type_name_override,
                        alignment=ui.Alignment.RIGHT,
                        visible_min=TEXT_VISIBLE_MIN,
                    )
                ui.Line(
                    width=8,
                    style_type_name_override=style_type_name_override,
                    visible_min=TEXT_VISIBLE_MIN,
                )

            if is_group:
                # +/- button
                state = model[port].expansion_state
                if state == GraphModel.ExpansionState.CLOSED:
                    image_name = "Plus"
                    next_state = GraphModel.ExpansionState.OPEN
                else:
                    image_name = "Minus"
                    next_state = GraphModel.ExpansionState.CLOSED
                ui.ImageWithProvider(
                    width=10,
                    style_type_name_override="Graph.Node.Port.Group",
                    name=image_name,
                    visible_min=TEXT_VISIBLE_MIN,
                    mouse_pressed_fn=partial(set_expansion_state, model, port, next_state),
                )

            with ui.ZStack():
                ui.Label(
                    model[port].name,
                    style_type_name_override="Graph.Node.Port.Label",
                    name=style_name,
                    visible_min=TEXT_VISIBLE_MIN,
                )
                ui.Line(
                    style_type_name_override="Graph.Node.Port.Label",
                    visible_min=LINE_VISIBLE_MIN,
                    visible_max=TEXT_VISIBLE_MIN,
                )

    def connection(
        self, model, source: GraphConnectionDescription, target: GraphConnectionDescription, foreground: bool = False
    ):
        """Called to create the connection between ports.

        Args:
            model: The graph model containing the connection data.
            source (GraphConnectionDescription): Description of the source port of the connection.
            target (GraphConnectionDescription): Description of the target port of the connection.
            foreground (bool): Optional flag to draw the connection in the foreground."""
        port_type = str(model[source.port].type)

        if target.is_tangent_reversed != source.is_tangent_reversed:
            # It's the same node connection. Set tangent in pixels.
            if source.is_tangent_reversed:
                start_tangent_width = ui.Pixel(-20)
                end_tangent_width = ui.Pixel(-20)
            else:
                start_tangent_width = ui.Pixel(20)
                end_tangent_width = ui.Pixel(20)
        else:
            # If the connection is reversed, we need to mirror tangents
            source_reverced_tangent = -1.0 if target.is_tangent_reversed else 1.0
            target_reverced_gangent = -1.0 if source.is_tangent_reversed else 1.0
            start_tangent_width = ui.Percent(-CONNECTION_CURVE * source_reverced_tangent)
            end_tangent_width = ui.Percent(CONNECTION_CURVE * target_reverced_gangent)

        ui.FreeBezierCurve(
            target.widget,
            source.widget,
            start_tangent_width=start_tangent_width,
            end_tangent_width=end_tangent_width,
            name=port_type,
            style_type_name_override="Graph.Connection",
        )
