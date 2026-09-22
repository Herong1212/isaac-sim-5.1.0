# Copyright (c) 2022-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from collections import deque
from typing import Callable, List, Optional, Set, Tuple

import omni.graph.core as og
from pxr import Usd


def _filter_prims_to_nodes_and_graphs(prims: List[Usd.Prim]) -> Tuple[Set[og.Node], Optional[og.Graph], og.Graph]:
    """
    Splits the given list of prims in a list of node prims, an optional compound graph prims and the owning graph.

    The owning graph is the first valid graph found in the list of prims. If it's a node, it's the owning graph of the
    node, if it's a compound graph, it's the compound graph.

    Args:
        prims: The list of prims to split.

    Return:
        Tuple of a set of nodes, an optional compound graph and the owning graph.

    Raises:
        og.OmniGraphError if the list of prims contains an invalid prim, or the prims do not all belong to the same graph.
    """

    node_prims = set()
    compound_graph = None
    owning_graph = None

    def get_graph(node_item, graph_item) -> og.Graph:
        if node_item:
            return node_item.get_graph()
        return graph_item

    for prim in prims:
        if not prim.IsValid():
            raise og.OmniGraphError(f"Invalid prim {prim.GetPath()}")
        node = None
        graph = None

        try:
            node = og.Controller.node(prim)
        except og.OmniGraphError:
            node = None

        if not node:
            try:
                graph = og.Controller.graph(prim)
            except og.OmniGraphError:
                graph = None
            if not graph or not graph.is_compound_graph():
                raise og.OmniGraphError(f"Prim is not a node or a compound graph {prim.GetPath()}")

        owning_graph = owning_graph or get_graph(node, graph)
        if owning_graph != get_graph(node, graph):
            raise og.OmniGraphError("Prims are not part of the same graph")

        if node:
            node_prims.add(node)
        else:
            compound_graph = graph

    return (node_prims, compound_graph, owning_graph)


def traverse_downstream_graph(
    prims: List[Usd.Prim],
    attribute_predicate: Optional[Callable[[og.Attribute], bool]] = None,
    node_callback: Optional[Callable[[og.Node], None]] = None,
) -> Set[og.Node]:
    """
    Traverses the nodes downstream from the input nodes and apply the predicate on visited nodes.

    Args:
        prims: The list of starting point nodes for the traversal.
        attribute_predicate: Function taking an Attribute as parameter and returning bool.
                             If True, connections to this attribute are evaluated, otherwise they are skipped.
        node_callback: Function taking a Node as parameter.
                       Allows for custom logic to be applied to visited nodes.

    Return:
        Returns the set of visited nodes.

    Raises:
        og.OmniGraphError if the list of prims contains an invalid prim, or the prims do not all belong to the same graph.
    """

    def get_downstream_nodes(node: og.Node) -> Set[og.Node]:
        """
        Helper to get the downstream nodes.

        Filters selected attributes using the attribute_predicate.

        Args:
            node: The starting node for the traversal.

        Return:
            set[omni.graph.core.Node]: The set of visited nodes.
        """
        result = set()
        for attr in node.get_attributes():
            if attribute_predicate and not attribute_predicate(attr):
                continue

            for connection in attr.get_downstream_connections():
                if connection.is_valid() and connection.get_node().is_valid():
                    target_node = connection.get_node()
                    if target_node.get_graph() == node.get_graph():
                        result.add(connection.get_node())

        result.discard(node)
        return result

    def get_input_nodes(graph: og.Graph) -> Set[og.Node]:
        """
        Helper to get the input (i.e. downstream) nodes from a compound graph

        Filters selected attributes using the attribute_predicate.

        Args:
            graph: The starting graph for the traversal.

        Return:
            set[omni.graph.core.Node]: The set of visited nodes.
        """
        result = set()
        if not graph:
            return result

        compound_node = graph.get_owning_compound_node()
        if not compound_node:
            return result

        for attr in compound_node.get_attributes():
            for connection in attr.get_downstream_connections():
                if connection.is_valid() and connection.get_node().is_valid():
                    target_node = connection.get_node()
                    # the attribute is applied after the graph filter, to avoid the predicated being applied to
                    # compound output connections
                    if target_node.get_graph() == graph and (not attribute_predicate or attribute_predicate(attr)):
                        result.add(connection.get_node())
        return result

    visited_cache = set()

    # will raise an exception if there is an error with the prims
    (nodes, compound_graph, _) = _filter_prims_to_nodes_and_graphs(prims)

    # add in the input nodes of the compound graph
    nodes = nodes.union(get_input_nodes(compound_graph))

    for node in nodes:
        q = deque()
        q.append(node)
        while q:
            current_node = q.popleft()
            if current_node in visited_cache:
                continue

            if node_callback:
                node_callback(current_node)

            for connection in get_downstream_nodes(current_node):
                q.append(connection)

            visited_cache.add(current_node)

    return visited_cache


def traverse_upstream_graph(
    prims: List[Usd.Prim],
    attribute_predicate: Optional[Callable[[og.Attribute], bool]] = None,
    node_callback: Optional[Callable[[og.Node], None]] = None,
) -> Set[og.Node]:
    """
    Traverses the nodes upstream from the input nodes and apply the predicate on visited nodes.

    Args:
        prims: The list of starting point nodes for the traversal.
        attribute_predicate: Function taking an Attribute as parameter and returning bool.
                             If True, connections to this attribute are evaluated, otherwise they are skipped.
        node_callback: Function taking a Node as parameter.
                        Allows for custom logic to be applied to visited nodes.

    Return:
        set[omni.graph.core.Node]: The set of visited nodes.

    Raises:
        og.OmniGraphError if the list of prims contains an invalid prim, or the prims do not all belong to the same graph.
    """

    def get_upstream_nodes(node: og.Node) -> Set[og.Node]:
        """
        Helper to get the upstream nodes.

        Filters selected attributes using the attribute_predicate.

        Args:
            node: The starting node for the traversal.

        Return:
            Returns the set of visited nodes.
        """

        result = set()
        for attr in node.get_attributes():
            if attribute_predicate and not attribute_predicate(attr):
                continue

            for connection in attr.get_upstream_connections():
                if connection.is_valid() and connection.get_node().is_valid():
                    target_node = connection.get_node()
                    if target_node.get_graph() == node.get_graph():
                        result.add(connection.get_node())

        result.discard(node)
        return result

    def get_output_nodes(graph: og.Graph) -> Set[og.Node]:
        """
        Helper to get the output (i.e. upstream) nodes from a compound graph

        Filters selected attributes using the attribute_predicate.

        Args:
            graph: The starting graph for the traversal.

        Return:
            set[omni.graph.core.Node]: The set of visited nodes.
        """
        result = set()
        if not graph:
            return result

        compound_node = graph.get_owning_compound_node()
        if not compound_node:
            return result

        for attr in compound_node.get_attributes():
            for connection in attr.get_upstream_connections():
                if connection.is_valid() and connection.get_node().is_valid():
                    target_node = connection.get_node()
                    # the attribute is applied after the graph filter, to avoid the predicated being applied to
                    # compound input connections
                    if target_node.get_graph() == graph and (not attribute_predicate or attribute_predicate(attr)):
                        result.add(connection.get_node())

        return result

    visited_cache = set()

    # will raise an exception if there is an error with the prims
    (nodes, compound_graph, _) = _filter_prims_to_nodes_and_graphs(prims)

    # add in the output nodes of the compound graph
    nodes = nodes.union(get_output_nodes(compound_graph))

    for node in nodes:
        q = deque()
        q.append(node)
        while q:
            current_node = q.popleft()
            if current_node in visited_cache:
                continue

            if node_callback:
                node_callback(current_node)

            for connection in get_upstream_nodes(current_node):
                q.append(connection)

            visited_cache.add(current_node)

    return visited_cache
