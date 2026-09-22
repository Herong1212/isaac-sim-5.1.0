# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""This module provides the `GraphNodeDelegateClosed` class, a specialized delegate for representing closed state graph nodes with the Omniverse design."""


__all__ = ["GraphNodeDelegateClosed"]

from .abstract_graph_node_delegate import GraphNodeDescription
from .graph_node_delegate_full import GraphNodeDelegateFull
from .graph_node_delegate_full import LINE_VISIBLE_MIN
from .graph_node_delegate_full import TEXT_VISIBLE_MIN
import omni.ui as ui


class GraphNodeDelegateClosed(GraphNodeDelegateFull):
    """A specialized delegate for representing closed state graph nodes in Omniverse design.

    Args:
        scale_factor (float): The factor by which the node's UI is scaled."""

    def __init__(self, scale_factor=1.0):
        """Initializes the closed graph node delegate with a scaling factor."""
        super().__init__(scale_factor)

    def node_header_input(self, model, node_desc: GraphNodeDescription):
        """Creates the left part of the header to be used as input when the node is collapsed.

        Args:
            model: The data model for the graph.
            node_desc (GraphNodeDescription): The description of the graph node."""
        node = node_desc.node
        connected_source = node_desc.connected_source
        connected_target = node_desc.connected_target

        with ui.ZStack(width=8, skip_draw_when_clipped=True):
            ui.Circle(
                radius=6,
                name=str(model[node].type),
                style_type_name_override="Graph.Node.Input",
                size_policy=ui.CircleSizePolicy.FIXED,
                alignment=ui.Alignment.RIGHT_CENTER,
                arc=ui.Alignment.RIGHT,
                visible_min=TEXT_VISIBLE_MIN,
            )

            if connected_source:
                # Circle that shows that the port is a source for the connection
                ui.Circle(
                    radius=7,
                    size_policy=ui.CircleSizePolicy.FIXED,
                    style_type_name_override="Graph.Connection",
                    alignment=ui.Alignment.RIGHT_CENTER,
                    visible_min=TEXT_VISIBLE_MIN,
                )
            if connected_target:
                # Circle that shows that the port is a target for the connection
                ui.Circle(
                    radius=5,
                    size_policy=ui.CircleSizePolicy.FIXED,
                    style_type_name_override="Graph.Connection",
                    alignment=ui.Alignment.RIGHT_CENTER,
                    visible_min=TEXT_VISIBLE_MIN,
                )

    def node_header_output(self, model, node_desc: GraphNodeDescription):
        """Creates the right part of the header to be used as output when the node is collapsed.

        Args:
            model: The data model for the graph.
            node_desc (GraphNodeDescription): The description of the graph node."""
        node = node_desc.node
        connected_source = node_desc.connected_source
        connected_target = node_desc.connected_target

        with ui.ZStack(width=8, skip_draw_when_clipped=True):
            ui.Circle(
                radius=6,
                name=str(model[node].type),
                style_type_name_override="Graph.Node.Output",
                size_policy=ui.CircleSizePolicy.FIXED,
                alignment=ui.Alignment.LEFT_CENTER,
                visible_min=TEXT_VISIBLE_MIN,
            )

            if connected_source:
                # Circle that shows that the port is a source for the connection
                ui.Circle(
                    radius=7,
                    size_policy=ui.CircleSizePolicy.FIXED,
                    style_type_name_override="Graph.Connection",
                    alignment=ui.Alignment.LEFT_CENTER,
                    visible_min=TEXT_VISIBLE_MIN,
                )
            if connected_target:
                # Circle that shows that the port is a target for the connection
                ui.Circle(
                    radius=5,
                    size_policy=ui.CircleSizePolicy.FIXED,
                    style_type_name_override="Graph.Connection",
                    alignment=ui.Alignment.LEFT_CENTER,
                    visible_min=TEXT_VISIBLE_MIN,
                )

    def node_header(self, model, node_desc: GraphNodeDescription):
        """Creates widgets at the top of the node.

        Args:
            model: The data model for the graph.
            node_desc (GraphNodeDescription): The description of the graph node."""
        node = node_desc.node

        with ui.VStack(skip_draw_when_clipped=True):
            self._common_node_header_top(model, node)

            style_name = str(model[node].type)

            # Draw the circle and the image on the top of it
            with ui.HStack(height=0):
                with ui.VStack():
                    ui.Label(
                        "Inputs",
                        alignment=ui.Alignment.CENTER,
                        style_type_name_override="Graph.Node.Port.Label",
                        visible_min=TEXT_VISIBLE_MIN,
                    )
                    ui.Spacer(height=15)

                with ui.ZStack(width=50, height=50):
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
                        offset_x=-15,
                        offset_y=-20,
                    ):
                        with ui.ZStack(width=0, height=0):
                            ui.Rectangle(
                                style_type_name_override="Graph.Node.Footer", name=style_name, width=80, height=80
                            )
                            ui.ImageWithProvider(
                                style_type_name_override="Graph.Node.Footer.Image", name=style_name, width=80, height=80
                            )

                with ui.VStack():
                    ui.Label(
                        "Outputs",
                        alignment=ui.Alignment.CENTER,
                        style_type_name_override="Graph.Node.Port.Label",
                        visible_min=TEXT_VISIBLE_MIN,
                    )
                    ui.Spacer(height=15)

            ui.Spacer(height=18)

    def node_footer(self, model, node_desc: GraphNodeDescription):
        """Creates widgets at the bottom of the node. This method intentionally does nothing for closed nodes."""
        # Don't draw footer
        pass
