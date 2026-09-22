# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""This module provides the GraphNodeDelegateRouter class for routing graph node delegates based on defined conditions and the GraphNodeDelegateRoutingError exception for handling routing errors."""


__all__ = ["GraphNodeDelegateRoutingError", "GraphNodeDelegateRouter", "RoutingCondition"]

import omni.kit.app
from .abstract_graph_node_delegate import AbstractGraphNodeDelegate
from .abstract_graph_node_delegate import GraphConnectionDescription
from .abstract_graph_node_delegate import GraphNodeDescription
from .abstract_graph_node_delegate import GraphPortDescription
from collections import namedtuple


RoutingCondition = namedtuple("RoutingCondition", ["type", "expression", "delegate"])


class GraphNodeDelegateRoutingError(Exception):
    """Exception raised for errors in the graph node delegate routing process.

    This exception indicates that routing for a graph node delegate could not be resolved,
    typically because a default route is not available in the routing table."""

    pass


class GraphNodeDelegateRouter(AbstractGraphNodeDelegate):
    """
    The delegate that keeps multiple delegates and pick them depending on the
    routing conditions.

    It's possible to add the routing conditions with `add_route`, and
    conditions could be a type or a lambda expression.

    The latest added routing is stronger than previously added. Routing added
    without conditions is the default.

    We use type routing to make the specific kind of nodes unique, and also
    we can use the lambda function to make the particular state of nodes
    unique (ex. full/collapsed).

    It's possible to use type and lambda routing at the same time.

    Usage examples:

       delegate.add_route(TextureDelegate(), type="Texture2d")
       delegate.add_route(CollapsedDelegate(), expressipon=is_collapsed)
    """

    def __init__(self):
        """Initializes the GraphNodeDelegateRouter with an empty routing table."""
        super().__init__()
        self.__routing_table = []

    def add_route(self, delegate: AbstractGraphNodeDelegate, type=None, expression=None):
        """Adds a delegate with an optional type and/or expression to the routing table.

        Args:
            delegate (AbstractGraphNodeDelegate): The delegate to be added.
            type (str, optional): The type of the delegate. Defaults to None.
            expression (callable, optional): A lambda expression to evaluate for routing. Defaults to None."""
        if not delegate:
            return

        if type is None and expression is None:
            # It's a default delegate, we don't need what we had before
            self.__routing_table.clear()

        self.__routing_table.append(RoutingCondition(type, expression, delegate))

    def __route(self, model, node):
        """Return the delegate for the given node"""
        for c in reversed(self.__routing_table):
            if (c.type is None or model[node].type == c.type) and (c.expression is None or c.expression(model, node)):
                return c.delegate

        raise GraphNodeDelegateRoutingError("Can't route.")

    def get_node_layout(self, model, node_desc: GraphNodeDescription):
        """Determines the layout for a given node.

        Args:
            model: The data model associated with the graph.
            node_desc (GraphNodeDescription): The description of the node.

        Returns:
            The layout for the node."""
        return self.__route(model, node_desc.node).get_node_layout(model, node_desc)

    def node_background(self, model, node_desc: GraphNodeDescription):
        """Creates widgets for the background of a node.

        Args:
            model: The data model associated with the graph.
            node_desc (GraphNodeDescription): The description of the node.

        Returns:
            The widgets for the node's background."""
        return self.__route(model, node_desc.node).node_background(model, node_desc)

    def node_header_input(self, model, node_desc: GraphNodeDescription):
        """Creates the left part of the node header to be used as input when the node is collapsed.

        Args:
            model: The data model associated with the graph.
            node_desc (GraphNodeDescription): The description of the node.

        Returns:
            The widgets for the node's header input."""
        return self.__route(model, node_desc.node).node_header_input(model, node_desc)

    def node_header_output(self, model, node_desc: GraphNodeDescription):
        """Creates the right part of the node header to be used as output when the node is collapsed.

        Args:
            model: The data model associated with the graph.
            node_desc (GraphNodeDescription): The description of the node.

        Returns:
            The widgets for the node's header output."""
        return self.__route(model, node_desc.node).node_header_output(model, node_desc)

    def node_header(self, model, node_desc: GraphNodeDescription):
        """Creates widgets for the top of a node.

        Args:
            model: The data model associated with the graph.
            node_desc (GraphNodeDescription): The description of the node.

        Returns:
            The widgets for the node's header."""
        return self.__route(model, node_desc.node).node_header(model, node_desc)

    def node_footer(self, model, node_desc: GraphNodeDescription):
        """Creates widgets for the bottom of a node.

        Args:
            model: The data model associated with the graph.
            node_desc (GraphNodeDescription): The description of the node.

        Returns:
            The widgets for the node's footer."""
        return self.__route(model, node_desc.node).node_footer(model, node_desc)

    def port_input(self, model, node_desc: GraphNodeDescription, port_desc: GraphPortDescription):
        """Creates the left part of a port to be used as input.

        Args:
            model: The data model associated with the graph.
            node_desc (GraphNodeDescription): The description of the node.
            port_desc (GraphPortDescription): The description of the port.

        Returns:
            The widget for the port input."""
        return self.__route(model, node_desc.node).port_input(model, node_desc, port_desc)

    def port_output(self, model, node_desc: GraphNodeDescription, port_desc: GraphPortDescription):
        """Creates the right part of a port to be used as output.

        Args:
            model: The data model associated with the graph.
            node_desc (GraphNodeDescription): The description of the node.
            port_desc (GraphPortDescription): The description of the port.

        Returns:
            The widget for the port output."""
        return self.__route(model, node_desc.node).port_output(model, node_desc, port_desc)

    def port(self, model, node_desc: GraphNodeDescription, port_desc: GraphPortDescription):
        """Creates the middle part of a port.

        Args:
            model: The data model associated with the graph.
            node_desc (GraphNodeDescription): The description of the node.
            port_desc (GraphPortDescription): The description of the port.

        Returns:
            The widget for the port."""
        return self.__route(model, node_desc.node).port(model, node_desc, port_desc)

    def connection(
        self, model, source: GraphConnectionDescription, target: GraphConnectionDescription, foreground: bool = False
    ):
        """Creates a graphical connection between two ports.

        Args:
            model: The data model associated with the graph.
            source (GraphConnectionDescription): The source port description.
            target (GraphConnectionDescription): The target port description.
            foreground (bool, optional): If True, draw the connection in the foreground. Defaults to False.

        Returns:
            The created connection widget."""
        try:
            return self.__route(model, source.node).connection(model, source, target, foreground)
        except TypeError:
            # Use the old version of connection as a fallback
            return self.__route(model, source.node).connection(model, source, target)

    def destroy(self):
        """Destroys all delegates in the routing table."""
        while self.__routing_table:
            routing_condition = self.__routing_table.pop()
            routing_condition.delegate.destroy()
