# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.ui as ui
from omni.kit.graph.delegate.modern import (
    GraphNodeDelegateFull,
    NODE_WIDTH_MARGIN, PORT_VISIBLE_MIN, HIGHLIGHT_THICKNESS, TEXT_VISIBLE_MIN, NODE_MIN_WIDTH,
    ICON, HEADER, STATE_TOGGER, PORT_HEIGHT, BACKGROUND_RADIUS
)
from omni.kit.graph.delegate.modern.delegate_closed import GraphNodeDelegateClosed
from omni.kit.widget.graph.abstract_graph_node_delegate import (
    AbstractGraphNodeDelegate,
    GraphNodeLayout,
    GraphNodeDescription,
    GraphPortDescription,
    GraphConnectionDescription
)
from omni.kit.widget.graph import GraphNodeLayout
from omni.kit.widget.graph.graph_model import GraphModel
from omni.kit.widget.graph.graph_node_delegate_router import GraphNodeDelegateRouter


# -------------------------------------------------------------------------------------------------
# Variable node router
class AnimationGraphNodeDelegateVariableRouter(GraphNodeDelegateRouter):
    def __init__(self):
        super().__init__()

        def is_closed(model, node):
            expansion_state = model[node].expansion_state
            return expansion_state == GraphModel.ExpansionState.CLOSED

        # Initial setup is the delegates for full and closed states.
        self.add_route(AnimationGraphNodeDelegateVariableFull())
        self.add_route(AnimationGraphNodeDelegateVariableClosed(), expression=is_closed)
        self.add_route(AnimationGraphNodeDelegateVariableRead(), type="ReadVariable")


# -------------------------------------------------------------------------------------------------
# Base class for variable node delegate
class AnimationGraphNodeDelegateVariableFull(GraphNodeDelegateFull):

    def get_node_layout(self, model, node_desc: GraphNodeDescription):
        """Called to determine the node layout"""
        return GraphNodeLayout.COLUMNS

    def _common_node_background(self, model, node, draw_icon: bool, node_min_width: int = None):
        """Called to create widgets of the node background"""
        node_type = str(model[node].type)
        port_type = None
        ports = model[node].ports
        if len(ports) > 0:
            port_type = str(model[ports[0]].type)

        HIGHLIGHT_THICKNESS_ZOOM_OUT_MORE = 4.0
        HIGHLIGHT_THICKNESS_ZOOM_OUT = 6.0

        NODE_HEADER = ICON["height"] + HEADER["margin_to_ports"]

        PORTS_HEIGHT = PORT_HEIGHT * len(model[node].ports)
        if model[node].expansion_state.value == 1:
            PORTS_HEIGHT = PORT_HEIGHT * len(model[node].connected_ports)

        # The node body
        background = ui.ZStack()
        with background:
            GraphNodeDelegateFull.build_tooltip([model[node].name, node_type], None, TEXT_VISIBLE_MIN)

            if node_min_width is None:
                node_min_width = NODE_MIN_WIDTH

            # This trick makes min width
            ui.Spacer(width=node_min_width)
            # highlight
            with ui.VStack(visible_max=PORT_VISIBLE_MIN):
                self._build_rectangle(BACKGROUND_RADIUS + HIGHLIGHT_THICKNESS, True, "Graph.Node.Border", node_type)

            # zoomed out highlight
            # this is shown during the zoom in between PORT_VISIBLE_MIN to TEXT_VISIBLE_MIN
            margin = NODE_WIDTH_MARGIN - HIGHLIGHT_THICKNESS_ZOOM_OUT
            with ui.HStack(visible_max=TEXT_VISIBLE_MIN, visible_min=PORT_VISIBLE_MIN):
                ui.Spacer(width=margin)
                with ui.VStack():
                    ui.Spacer(height=margin)
                    with ui.ZStack():
                        self._build_rectangle(BACKGROUND_RADIUS + HIGHLIGHT_THICKNESS_ZOOM_OUT, False, "Graph.Node.Border", node_type)
                    ui.Spacer(height=margin)
                ui.Spacer(width=margin)

            # zoomed out more hightlight
            # this is shown duing when the zoom is > TEXT_VISIBLE_MIN
            margin = NODE_WIDTH_MARGIN - HIGHLIGHT_THICKNESS_ZOOM_OUT_MORE
            with ui.HStack(visible_min=TEXT_VISIBLE_MIN):
                ui.Spacer(width=margin)
                with ui.VStack():
                    ui.Spacer(height=margin)
                    self._build_rectangle(BACKGROUND_RADIUS + HIGHLIGHT_THICKNESS_ZOOM_OUT_MORE, True, "Graph.Node.Border", node_type)
                    ui.Spacer(height=margin)
                ui.Spacer(width=margin)

            # node
            with ui.HStack():
                ui.Spacer(width=NODE_WIDTH_MARGIN)
                with ui.VStack():
                    ui.Spacer(height=NODE_WIDTH_MARGIN)
                    with ui.ZStack():
                        # background, this is shown across the whole zoom level
                        self._build_rectangle(
                            BACKGROUND_RADIUS,
                            True,
                            "Graph.Node.Background",
                            port_type if port_type is not None else node_type
                        )
                        if draw_icon:
                            with ui.VStack(visible_max=PORT_VISIBLE_MIN):
                                ui.Spacer()
                                # this icon_size is not accurate, since there is no way to find the actual width of the node
                                # we use node_min_width
                                icon_size = min(node_min_width, PORTS_HEIGHT + NODE_HEADER)
                                self._draw_icon(icon_size, node_type)
                                ui.Spacer()
                    ui.Spacer(height=NODE_WIDTH_MARGIN)
                ui.Spacer(width=NODE_WIDTH_MARGIN)

            if draw_icon:
                # zoom in icon in the middle
                # this is shown during the zoom in between PORT_VISIBLE_MIN to TEXT_VISIBLE_MIN
                icon_size = min(node_min_width, PORTS_HEIGHT)
                with ui.VStack(visible_max=TEXT_VISIBLE_MIN, visible_min=PORT_VISIBLE_MIN):
                    ui.Spacer(height=NODE_HEADER)
                    # this icon_size is not accurate, since there is no way to find the actual width of the node
                    # we use noe_min_width
                    self._draw_icon(icon_size, node_type)
        return background

    def _build_header(self, model, node_desc: GraphNodeDescription):
        ui.Spacer(height=NODE_WIDTH_MARGIN)
        header = ui.VStack()
        with header:
            node = node_desc.node
            node_name = "Write"
            node_category = str(model[node].type)
            port_type = None
            ports = model[node].ports
            if len(ports) > 0:
                port_type = str(model[ports[0]].type)

            widget_name = port_type if port_type is not None else node_category

            ui.Spacer(height=NODE_WIDTH_MARGIN)
            with ui.ZStack():
                GraphNodeDelegateFull.build_tooltip([node_name, node_category])
                with ui.HStack():
                    # label
                    with ui.VStack():
                        # the header text with background
                        with ui.ZStack(height=HEADER["sec_height"]):
                            ui.Label(
                                node_name,
                                visible_min=TEXT_VISIBLE_MIN,
                                style_type_name_override="Graph.Node.Label",
                                style={"margin_width": HEADER["margin_to_left"]},
                                alignment=ui.Alignment.CENTER
                            )

                        ui.Rectangle(
                            visible_min=PORT_VISIBLE_MIN,
                            height=HEADER["height"],
                            name=widget_name,
                            style_type_name_override="Graph.Node.Category"
                        )
                        # the expansion button
                        ui.Spacer(height=STATE_TOGGER["margin"])
                        with ui.HStack():
                            ui.Spacer()
                            self.build_expansion_widget(model, node, widget_name)
                            ui.Spacer(width=STATE_TOGGER["margin"])
                        ui.Spacer(height=STATE_TOGGER["margin"])
                ui.Label(
                    node_name,
                    height=HEADER["sec_height"],
                    visible_max=TEXT_VISIBLE_MIN,
                    visible_min=PORT_VISIBLE_MIN,
                    style_type_name_override="Graph.Node.Label.ZoomIn",
                    style={"margin_width": HEADER["margin_to_left_zoom_in"]},
                    alignment=ui.Alignment.CENTER
                )
            ui.Spacer(height=NODE_WIDTH_MARGIN)
        return header


# -------------------------------------------------------------------------------------------------
# Closed variable node delegate
class AnimationGraphNodeDelegateVariableClosed(GraphNodeDelegateClosed, AnimationGraphNodeDelegateVariableFull):
    def get_node_layout(self, model, node_desc: GraphNodeDescription):
        return AnimationGraphNodeDelegateVariableFull.get_node_layout(self, model, node_desc)

    def _common_node_background(self, model, node, draw_icon: bool, node_min_width: int = None):
        return AnimationGraphNodeDelegateVariableFull._common_node_background(
            self,
            model,
            node,
            draw_icon,
            node_min_width
        )

    def _build_header(self, model, node_desc: GraphNodeDescription):
        return AnimationGraphNodeDelegateVariableFull._build_header(self, model, node_desc)


# -------------------------------------------------------------------------------------------------
#  Specialization for read nodes, which contain no header
class AnimationGraphNodeDelegateVariableRead(AnimationGraphNodeDelegateVariableFull):

    def get_node_layout(self, model, node_desc: GraphNodeDescription):
        """Called to determine the node layout"""
        return GraphNodeLayout.LIST

    def node_background(self, model, node_desc: GraphNodeDescription):
        """Called to create widgets of the node background"""

        header = ui.ZStack()
        with header:
            ui.Spacer(height=PORT_HEIGHT * 3)
            self._common_node_background(model, node_desc.node, False, 80)

    def node_header_input(self, model, node_desc: GraphNodeDescription):
        """Called to create the left part of the header that will be used as input when the node is collapsed"""
        pass

    def node_header_output(self, model, node_desc: GraphNodeDescription):
        """Called to create the right part of the header that will be used as output when the node is collapsed"""
        pass

    def node_header(self, model, node_desc: GraphNodeDescription):
        """Called to create widgets of the top of the node"""
        with ui.ZStack():
            ui.Spacer(height=PORT_HEIGHT)

    def node_footer(self, model, node_desc: GraphNodeDescription):
        """Called to create widgets of the bottom of the node"""
        with ui.ZStack():
            ui.Spacer(height=PORT_HEIGHT)

    def port(self, model, node_desc: GraphNodeDescription, port_desc: GraphPortDescription):
        """Called to create the middle part of the port"""

        # make the port label match the header label, since there is no header
        style = {
            "Graph.Node.Port.Label": {
                "color": 0xFFD9D9D9,
                "margin_width": 4.0,
                "margin_height": 3.0,
                "font_size": 15.0,
            }
        }

        # add a margin to provide space from the left most side, as the node is smaller and no input port exists
        header = ui.HStack()
        with header:
            header.set_style(style)
            ui.Spacer(width=NODE_WIDTH_MARGIN)
            super().port(model, node_desc, port_desc)
