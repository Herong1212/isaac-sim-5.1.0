# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.graph.core as og
import omni.ui as ui
from omni.kit.graph.delegate.modern import (
    BACKGROUND_RADIUS,
    HEADER,
    HIGHLIGHT_THICKNESS,
    ICON,
    NODE_WIDTH_MARGIN,
    PORT_HEIGHT,
    PORT_VISIBLE_MIN,
    TEXT_VISIBLE_MIN,
    GraphNodeDelegateFull,
)
from omni.kit.graph.editor.core import GraphEditorCoreWidget
from omni.kit.widget.graph import GraphNodeLayout
from omni.kit.widget.graph.abstract_graph_node_delegate import GraphNodeDescription, GraphPortDescription

from . import graph_config
from .graph_delegate import OmniGraphNodeDelegate
from .graph_model import OmniGraphModel

_HIGHLIGHT_THICKNESS_ZOOM_OUT_MORE = 4.0
_HIGHLIGHT_THICKNESS_ZOOM_OUT = 6.0
_LABEL_COLOR = 0xFFD9D9D9
_NODE_MIN_WIDTH = 80


# -------------------------------------------------------------------------------------------------
# Base class for variable node delegate
class VariableNodeDelegate(OmniGraphNodeDelegate):

    # ---------------------------------------------------------------------------------------------
    def __init__(self, graph_widget: GraphEditorCoreWidget):
        super().__init__(graph_widget)
        self._node_label = "Write"
        self.show_header_icon = False
        self.show_header_background = False
        self.header_label_alignment = ui.Alignment.CENTER
        self._show_write_port_name = False

    # ---------------------------------------------------------------------------------------------
    def get_node_layout(self, model, node_desc: GraphNodeDescription):
        """Called to determine the node layout"""
        return GraphNodeLayout.COLUMNS

    # ---------------------------------------------------------------------------------------------
    def port(self, model: OmniGraphModel, node_desc: GraphNodeDescription, port_desc: GraphPortDescription):
        """Called to create the middle part of the port"""
        port = port_desc.port
        port_name = model[port].nice_name

        # no port names for execution pins
        if model[port].is_execution_pin:
            port_name = ""

        if port_name == "Value":
            # hides the output port on Write nodes only
            if (not self._show_write_port_name) and model.is_output(port):
                port_name = ""
            else:
                port_name = self._get_variable_name(model, node_desc)

        GraphNodeDelegateFull.build_port(model, node_desc, port_desc, port_name)

    # ---------------------------------------------------------------------------------------------
    def node_background(self, model: OmniGraphModel, node_desc: GraphNodeDescription):
        """Override the background drawing for variable nodes"""
        error_state = self.get_error_state(model, node_desc)
        type_colors = self._get_variable_node_colors(model, node_desc, 0xFFADFB47, error_state[0])
        header = ui.ZStack()

        # only draw the background
        self.show_header_background = error_state[0] != og.Severity.INFO
        with header:
            if error_state[0] == og.Severity.INFO:
                header.set_style(self.get_style(node_background=type_colors[3]))
            super().node_background(model, node_desc)

    # ---------------------------------------------------------------------------------------------
    def build_header(
        self, node_name: str, model: OmniGraphModel, node_desc: GraphNodeDescription, error_state: og.Severity
    ):
        """Overrides the build header specifically for variable nodes"""

        # draws with the variable node with customized colors
        var_color = self._get_variable_node_colors(model, node_desc, 0xFFADFB47, error_state)
        style = self.specialized_color_style(str(model[node_desc.node].type), var_color[1], "", var_color[2])
        style.update(self.specialized_expansion_style(str(model[node_desc.node].type), var_color[1], var_color[2]))

        if graph_config.Settings.get_show_name_as_type():
            node_name = self._node_label

        ui.Spacer(height=NODE_WIDTH_MARGIN)
        header = ui.ZStack()
        with header:
            # only override the style if there is no error
            if error_state == og.Severity.INFO:
                header.set_style(style)
            super().build_header(node_name, model, node_desc, error_state)

    # ---------------------------------------------------------------------------------------------
    def node_header(self, model: OmniGraphModel, node_desc: GraphNodeDescription):
        """Called to create widgets of the top of the node"""
        (error_state, error_name, message, error_icon) = self.get_error_state(model, node_desc)
        with ui.ZStack():
            self.build_header(model[node_desc.node].name, model, node_desc, error_state)

            # override the existing tooltip
            namespace, _, type_name = model[node_desc.node].node_type_name.rpartition(".")
            var_name = self._get_variable_name(model, node_desc)
            variable = model.get_graph(None).find_variable(var_name)
            variable_tooltip = variable.tooltip if variable else ""
            tips = [error_name, f"{type_name} ({namespace})", variable_tooltip]
            if message:
                tips = [message] + tips
            GraphNodeDelegateFull.build_tooltip(tips)
            # Apply an error/warning icon if needed.
            if error_state != og.Severity.INFO:
                with ui.HStack():
                    ui.Spacer()
                    with ui.VStack(alignment=ui.Alignment.RIGHT_CENTER, width=HEADER["sec_height"]):
                        ui.Spacer(height=NODE_WIDTH_MARGIN + ICON["border"])
                        with ui.HStack(width=HEADER["sec_height"] - ICON["border"]):
                            with ui.ZStack(
                                height=HEADER["sec_height"] - 2 * ICON["border"], alignment=ui.Alignment.RIGHT_CENTER
                            ):
                                ui.Rectangle(style_type_name_override="Graph.Node.Icon.Background")
                                ui.Image(
                                    error_icon,
                                    height=HEADER["sec_height"] - 3 * ICON["border"],
                                    fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT,
                                )

    # --------------------------------------------------------------------------
    def _get_variable_node_colors(
        self, model: OmniGraphModel, node_desc: GraphNodeDescription, default_color: int, error_state: og.Severity
    ) -> tuple:
        """
        Returns the specific colors for a variable node

        The tuple contains (basecolor, highlight, lowlight, midlight)
        """

        if error_state == og.Severity.ERROR:
            return (
                graph_config.ERROR_BACKGROUND_COLOR,
                graph_config.ERROR_HIGHLIGHT_COLOR,
                graph_config.lerp_abgr_to_secondary(graph_config.ERROR_BACKGROUND_COLOR, 0x121110),
                graph_config.ERROR_BACKGROUND_COLOR,
            )
        if error_state == og.Severity.WARNING:
            return (
                graph_config.WARNING_BACKGROUND_COLOR,
                graph_config.WARNING_HIGHLIGHT_COLOR,
                graph_config.lerp_abgr_to_secondary(graph_config.WARNING_BACKGROUND_COLOR, 0x121110),
                graph_config.WARNING_BACKGROUND_COLOR,
            )

        output_path = node_desc.node.GetPath().AppendProperty("outputs:value")
        input_path = node_desc.node.GetPath().AppendProperty("inputs:value")
        port_type = model[output_path].type or model[input_path].type

        base_color = default_color

        # if we can't find the node type, draw with the default color
        if port_type:
            base_color = graph_config.type_to_color(str(port_type), default_color)

        highlight_color = graph_config.lerp_abgr_to_secondary(base_color, 0xA8A8A8)
        lowlight_color = graph_config.lerp_abgr_to_secondary(base_color, 0x121110)
        midlight_color = graph_config.lerp_abgr_to_secondary(base_color)

        return (base_color, highlight_color, lowlight_color, midlight_color)

    # ---------------------------------------------------------------------------------------------
    def _get_variable_name(self, model: OmniGraphModel, node_desc: GraphNodeDescription):
        """Returns the name of the variable this node refers to"""
        attr = model.get_attribute_from_path(node_desc.node.GetPath().AppendProperty("inputs:variableName"))
        if attr:
            return attr.get()
        return None


# -------------------------------------------------------------------------------------------------
#  Specialization for read nodes, which contain no header
class ReadVariableNodeDelegate(VariableNodeDelegate):

    # ---------------------------------------------------------------------------------------------
    def __init__(self, graph_widget: GraphEditorCoreWidget):
        super().__init__(graph_widget)
        self._node_label = "Read"
        self._show_write_port_name = True

    # ---------------------------------------------------------------------------------------------
    def get_node_layout(self, model: OmniGraphModel, node_desc: GraphNodeDescription):
        """Called to determine the node layout"""
        return GraphNodeLayout.LIST

    # ---------------------------------------------------------------------------------------------
    def node_background(self, model: OmniGraphModel, node_desc: GraphNodeDescription):
        """Called to create widgets of the node background"""

        # draws with the variable node with customized colors
        var_color = self._get_variable_node_colors(
            model, node_desc, 0xFFADFB47, self.get_error_state(model, node_desc)[0]
        )
        node = node_desc.node
        style_name = str(model[node].node_type_name)

        style = {
            f"Graph.Node.Header.Background::{style_name}": {"background_color": var_color[3]},
            f"Graph.Node.Background::{style_name}": {"background_color": var_color[3]},
        }

        style.update(self.specialized_color_style(str(model[node_desc.node].type), var_color[1], "", var_color[2]))

        header = ui.ZStack()
        with header:
            header.set_style(style)
            ui.Spacer(height=PORT_HEIGHT * 3)
            self._draw_background(model, node_desc.node)

    # ---------------------------------------------------------------------------------------------
    def node_header_input(self, model: OmniGraphModel, node_desc: GraphNodeDescription):
        """Called to create the left part of the header that will be used as input when the node is collapsed"""

    # ---------------------------------------------------------------------------------------------
    def node_header_output(self, model: OmniGraphModel, node_desc: GraphNodeDescription):
        """Called to create the right part of the header that will be used as output when the node is collapsed"""

    # ---------------------------------------------------------------------------------------------
    def node_header(self, model: OmniGraphModel, node_desc: GraphNodeDescription):
        """Called to create widgets of the top of the node"""
        with ui.ZStack():
            ui.Spacer(height=PORT_HEIGHT)

    # ---------------------------------------------------------------------------------------------
    def node_footer(self, model: OmniGraphModel, node_desc: GraphNodeDescription):
        """Called to create widgets of the bottom of the node"""
        with ui.ZStack():
            ui.Spacer(height=PORT_HEIGHT)

    # ---------------------------------------------------------------------------------------------
    def port(self, model: OmniGraphModel, node_desc: GraphNodeDescription, port_desc: GraphPortDescription):
        """Called to create the middle part of the port"""

        # matches modern style
        color = (
            _LABEL_COLOR
            if self.get_error_state(model, node_desc)[0] != og.Severity.WARNING
            else graph_config.WARNING_LABEL_COLOR
        )

        # make the port label match the header label, since there is no header
        style = {
            "Graph.Node.Port.Label": {
                "color": color,
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
            self._draw_error_state(model, node_desc)
            super().port(model, node_desc, port_desc)

    # ---------------------------------------------------------------------------------------------
    def _draw_background(self, model: OmniGraphModel, node):
        """
        Called to create widgets of the node background,
        copied from _common_node_background
        """
        node_type = str(model[node].node_type_name)

        # The node body
        background = ui.ZStack()
        with background:
            GraphNodeDelegateFull.build_tooltip([model[node].name, node_type], None, TEXT_VISIBLE_MIN)

            # This trick makes min width
            ui.Spacer(width=_NODE_MIN_WIDTH)

            # highlight
            with ui.VStack(visible_max=PORT_VISIBLE_MIN):
                self._build_rectangle(BACKGROUND_RADIUS + HIGHLIGHT_THICKNESS, True, "Graph.Node.Border", node_type)

            # zoomed out highlight
            # this is shown during the zoom in between PORT_VISIBLE_MIN to TEXT_VISIBLE_MIN
            margin = NODE_WIDTH_MARGIN - _HIGHLIGHT_THICKNESS_ZOOM_OUT
            with ui.HStack(visible_max=TEXT_VISIBLE_MIN, visible_min=PORT_VISIBLE_MIN):
                ui.Spacer(width=margin)
                with ui.VStack():
                    ui.Spacer(height=margin)
                    with ui.ZStack():
                        self._build_rectangle(
                            BACKGROUND_RADIUS + _HIGHLIGHT_THICKNESS_ZOOM_OUT, False, "Graph.Node.Border", node_type
                        )
                    ui.Spacer(height=margin)
                ui.Spacer(width=margin)

            # zoomed out more hightlight
            # this is shown during when the zoom is > TEXT_VISIBLE_MIN
            margin = NODE_WIDTH_MARGIN - _HIGHLIGHT_THICKNESS_ZOOM_OUT_MORE
            with ui.HStack(visible_min=TEXT_VISIBLE_MIN):
                ui.Spacer(width=margin)
                with ui.VStack():
                    ui.Spacer(height=margin)
                    self._build_rectangle(
                        BACKGROUND_RADIUS + _HIGHLIGHT_THICKNESS_ZOOM_OUT_MORE, True, "Graph.Node.Border", node_type
                    )
                    ui.Spacer(height=margin)
                ui.Spacer(width=margin)

            # node
            with ui.HStack():
                ui.Spacer(width=NODE_WIDTH_MARGIN)
                with ui.VStack():
                    ui.Spacer(height=NODE_WIDTH_MARGIN)
                    # background, this is shown across the whole zoom level
                    self._build_rectangle(BACKGROUND_RADIUS, True, "Graph.Node.Background", node_type)
                    ui.Spacer(height=NODE_WIDTH_MARGIN)
                ui.Spacer(width=NODE_WIDTH_MARGIN)

        return background

    # -----------------------------------------------------------------------------------------
    def _draw_error_state(self, model: OmniGraphModel, node_desc: GraphNodeDescription):
        """Draws the error icon with tooltip"""
        (error_state, node_name, message, error_icon) = self.get_error_state(model, node_desc)

        if error_state == og.Severity.INFO:
            return

        # override the existing tooltip
        namespace, _, type_name = model[node_desc.node].node_type_name.rpartition(".")
        tips = [node_name, f"{type_name} ({namespace})"]
        if message:
            tips = [message] + tips

        # Apply an error/warning icon
        border = ICON["border"]
        with ui.HStack():
            ui.Spacer(width=border)
            with ui.ZStack(
                alignment=ui.Alignment.LEFT_CENTER, height=PORT_HEIGHT + border * 2, width=PORT_HEIGHT + border * 2
            ):
                GraphNodeDelegateFull.build_tooltip(tips)
                ui.Rectangle(style_type_name_override="Graph.Node.Icon.Background", width=PORT_HEIGHT + border * 2)
                with ui.HStack():
                    ui.Spacer(width=border)
                    ui.Image(error_icon, fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT, width=PORT_HEIGHT)
                    ui.Spacer(width=border)
            ui.Spacer(width=border)
