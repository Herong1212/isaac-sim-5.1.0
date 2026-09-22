# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import re
from collections import deque
from typing import List, Set, Tuple, Union

import carb
import omni.graph.core as og
import omni.graph.tools.ogn as ogn
import omni.usd
import OmniGraphSchema
from pxr import Sdf, Tf, Usd, UsdUI

from . import graph_config

SCOPE_FOLDER = Sdf.Path("/World/Compounds")


class CompoundUtils:
    """
    Utilities for working with compounds.

    Compound Node               The OmniGraphNode that graph(s) will be parented under
    Compound Graph              The OmniGraph encapsulated by a compound node

                                In the case of compound subgraphs, this is also the graph that will be evaluated. But in
                                the case of functions/published compounds, this will be the source of the USD reference,
                                and will not be evaluated directly

    Compound Graph Instance     The OmniGraph that will be evaluated.

                                For compound subgraphs, this is the same as the Compound Graph
                                For functions/published compounds, this is the USD reference to the Compound Graph

    Owning Compound Node        The OmniGraphNode that owns a given node.

                                If node is an OmniGraph, this is the compound node that owns it
                                If node is an OmniGraphNode in a graph, this is compound node that owns the OmniGraph
                                If node is a Compound Node itself, this is the compound node that this compound node is
                                nested under
    """

    # -------------------------------------------------------------------------------
    @staticmethod
    def sanitize_compound_name_and_namespace(name: str, namespace: str) -> Tuple[str, str]:
        """Sanitizes the proposed compound name and namespace to make sure they are valid and unique"""

        # sanitize the namespace
        # replace special characters with _
        namespace = re.sub("[^a-zA-Z0-9.]", "_", namespace)
        # remove prefix, postfix and consecutive '.' characters
        namespace = ".".join(list(filter(None, namespace.split("."))))
        # remove special characters from the name
        name = re.sub("[^a-zA-Z0-9]", "_", name)

        base_name = name
        count = 0
        stage = omni.usd.get_context().get_stage()

        # find the next name that does not have an existing prim, or registered type
        while True:
            prim_path = SCOPE_FOLDER.AppendChild(name)
            qualified_name = f"{namespace}.{name}"
            if not stage.GetPrimAtPath(prim_path) and not og.get_node_type(qualified_name).is_valid():
                break
            count = count + 1
            name = f"{base_name}_{count:02}"

        return (name, namespace)

    # -------------------------------------------------------------------------------
    @staticmethod
    def sanitize_attribute_name(
        name: str, node: og.Node, port_type: og.AttributePortType, is_bundle: bool, prev_name: str | None = None
    ) -> str:
        """
        Sanitizes the proposed attribute name on a compound and returns a valid and unique attr name
        Args:
            name:           Base name to be validated without the input/output prefix
            node:           Node that the new attribute will be created on
            port_type:      The type of port for the attribute
            is_bundle:      Whether the attribute is a bundle
            prev_name:      The previous name of the port, with or without a namespace. If the new name matches the
                            previous name, it is considered valid. Pass None if there is no previous name.
        Returns: The sanitized name of the attribute, without a namespace prefix, or None if it could not be converted
                 to a valid, unique attribute name
        """

        # convert to camel case first and remove any array brackets
        new_name = re.sub(r"(_|-)+", " ", name).title().replace(" ", "") or Tf.MakeValidIdentifier(name)
        new_name = "".join([new_name[0].lower(), new_name[1:]])
        new_name = re.sub(r"\[(.*)\]", r"\1", new_name)
        new_name = Tf.MakeValidIdentifier(new_name)

        # in the case of a rename, where the new name matches the old name, it is valid
        namespaced_name = og.Attribute.ensure_port_type_in_name(new_name, port_type, is_bundle)
        if prev_name in (namespaced_name, new_name):
            return new_name

        def is_name_valid(full_name, base_name):
            if node.get_attribute_exists(full_name):
                return False
            if not Tf.IsValidIdentifier(base_name):
                return False
            try:
                ogn.check_attribute_name(full_name, ogn.LanguageTypeValues.PYTHON)
                ogn.check_attribute_name(full_name, ogn.LanguageTypeValues.CPP)
            except ogn.ParseError:
                return False

            return True

        # make sure the name is unique among attributes
        base_name = new_name
        postfix = 0
        attr_count = len(node.get_attributes())
        while not is_name_valid(namespaced_name, new_name):
            postfix = postfix + 1
            new_name = f"{base_name}_{postfix:02}"
            namespaced_name = og.Attribute.ensure_port_type_in_name(new_name, port_type, is_bundle)
            if postfix > attr_count:
                return None

        return new_name

    # -------------------------------------------------------------------------------
    @staticmethod
    def compute_compound_node_position(nodes: List[Usd.Prim]) -> Tuple[float, float]:
        pos = (0.0, 0.0)
        num = 0
        for node in nodes:
            attr = node.GetAttribute(UsdUI.Tokens.uiNodegraphNodePos)
            if attr and attr.HasValue():
                (x, y) = attr.Get()
                pos = (pos[0] + x, pos[1] + y)
                num = num + 1
        if num > 0:
            pos = (pos[0] / num, pos[1] / num)
        return pos

    # -------------------------------------------------------------------------------
    @classmethod
    def can_create_compound_from(cls, prims: List[Usd.Prim]) -> bool:
        """
        Determines whether a list of prims, representing USD nodes, can be converted into a compound graph

        To avoid having nodes creating cycles, we validate there are no intermediate nodes between candidates

            [A]->[B]->[C]->[D]

            In this scenario, [A] and [D] cannot be made into a compound node because the resulting graph
            would have [B]->[C] groups as both an input and output of the resulting compound.

            We validate by looking at each candidate, and traversing the graph looking for the pattern of
            a non-candidate node to a candidate node.

        """

        def get_downstream_nodes(node: og.Node) -> Set[og.Node]:
            """Helper to get the downstream nodes"""
            result = set()
            for attr in node.get_attributes():
                for connection in attr.get_downstream_connections():
                    if connection.is_valid() and connection.get_node().is_valid():
                        target_node = connection.get_node()
                        if target_node.get_graph() == node.get_graph():
                            result.add(connection.get_node())

            result.discard(node)
            return result

        # convert to nodes
        nodes = [og.get_node_by_path(str(prim.GetPath())) for prim in prims]
        if not nodes:
            return False

        # check for invalid nodes and that all nodes are part of the same graph
        if any(not bool(node) or (node.get_graph() != nodes[0].get_graph()) for node in nodes):
            return False

        # keep track of visited nodes to avoid loops, avoid recomputation
        visited_cache = set()

        for node in nodes:
            q = deque()
            q.append((node, True))
            while q:
                current_node, current_is_candidate = q.popleft()
                if current_node in visited_cache:
                    continue

                for connection in get_downstream_nodes(current_node):
                    next_is_candidate = connection in nodes
                    if next_is_candidate and not current_is_candidate:
                        return False
                    q.append((connection, next_is_candidate))

                visited_cache.add(current_node)

        return True

    # -------------------------------------------------------------------------------
    @staticmethod
    def is_compound_graph(item: Union[og.Graph, Usd.Prim, str, Sdf.Path]) -> bool:
        """
        Returns true if the given item is a compound graph
        """
        try:
            graph = og.Controller.graph(item)
        except og.OmniGraphError:
            return False

        return bool(graph) and graph.is_compound_graph()

    # -------------------------------------------------------------------------------
    @staticmethod
    def is_compound_node(item: Union[og.Node, Usd.Prim, str, Sdf.Path]) -> bool:
        """
        Returns true if the given item is a compound_node
        """
        try:
            node = og.Controller.node(item)
        except og.OmniGraphError:
            return False

        return graph_config.Settings.are_compounds_enabled() and node.is_compound_node()

    # -------------------------------------------------------------------------------
    @staticmethod
    def is_compound_subgraph_node(node_or_port: Sdf.Path) -> bool:
        """
        Checks whether a node or port path is part of a subgraph compound node instance
        A compound subgraph node is a compound node whose underlying graph is simply a subgraph
        and not a more complex node type
        """
        # handle the case where EmptyPort is passed in
        if not isinstance(node_or_port, Sdf.Path):
            return False

        # the imported schema may not have the compound node API
        if not graph_config.Supports.compound_node_api():
            return False

        # is there a better way to get the prim from the port?
        prim = omni.usd.get_context().get_stage().GetPrimAtPath(node_or_port.GetPrimPath())
        if not prim:
            return False

        return (
            prim.HasAPI(OmniGraphSchema.CompoundNodeAPI)
            and OmniGraphSchema.CompoundNodeAPI(prim).GetCompoundTypeAttr().Get() == "subgraph"
        )

    # -------------------------------------------------------------------------------
    @staticmethod
    def is_node_in_a_compound(node_or_port: Sdf.Path) -> bool:
        """Check whether a node or port path is part of a node within a compound graph"""

        # handle the case where EmptyPort is passed in
        if not isinstance(node_or_port, Sdf.Path):
            return False

        try:
            node = og.Controller.node(node_or_port.GetPrimPath())
        except og.OmniGraphError:
            return False

        return node.is_valid() and node.get_graph().is_compound_graph()

    # -------------------------------------------------------------------------------
    @staticmethod
    def get_compound_node(node: Sdf.Path) -> og.Node:
        """Given a node, get the the compound node that parents it"""

        try:
            node = og.Controller.node(node.GetPrimPath())
            compound_node = node.get_graph().get_owning_compound_node()
        except og.OmniGraphError:
            return None
        return compound_node

    # -------------------------------------------------------------------------------
    @staticmethod
    def can_promote_attribute_to_compound_subgraph(port: Sdf.Path) -> bool:
        """Checks whether an attribute can be promoted to the parent compound node"""

        if not CompoundUtils.is_node_in_a_compound(port):
            return False
        try:
            attribute = og.Controller.attribute(str(port))
        except og.OmniGraphError:
            return False

        # check if the attribute is already promoted and fan in is not allowed
        is_input = (
            attribute.get_port_type() == og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT
            and attribute.get_metadata(ogn.MetadataKeys.OUTPUT_ONLY) != "1"
        )
        if is_input:
            allow_multi_input = (
                attribute.get_metadata(ogn.MetadataKeys.ALLOW_MULTI_INPUTS) == "1"
                or attribute.get_resolved_type().role == og.AttributeRole.EXECUTION
            )
            upstream_connections = attribute.get_upstream_connections()
            already_promoted_input = any(
                a.get_node().get_graph() != attribute.get_node().get_graph() for a in upstream_connections
            )
            if not allow_multi_input and already_promoted_input:
                return False

        # check that the port is on a valid node for promotion
        return og._unstable.validate_attribute_for_promotion_from_compound_subgraph(attribute) is None  # noqa: PLW0212

    # -------------------------------------------------------------------------------
    @classmethod
    def owning_compound_node(cls, prim: Usd.Prim) -> Usd.Prim:
        """
        Return the owning compound node prim given a compound graph.
        TODO: accept more than just prims and handle nodes in compound graphs as well as nested compounds
        """
        # If this is a compound subgraph, the parent will be a compound node
        parent = prim.GetParent()
        return parent if prim.IsA(OmniGraphSchema.OmniGraph) and cls.is_compound_node(parent) else None

    # ----------------------------------------------------------------------------------------------
    @classmethod
    def get_compound_graphs(cls, graph) -> List[og.Graph]:
        """
        Returns a list of all the immediate compound graphs in an OmniGraph.

        Args:
            graph (GraphSpec_t): The OmniGraph to search for compound graphs

        Returns:
            List[og.Graph]: A list, possible empty, of all the immediate compound graphs in an OmniGraph

        """
        try:
            graph = og.Controller.graph(graph)
        except og.OmniGraphError:
            carb.log_warning(f"Invalid graph passed to get_compound_graphs {graph}")
            return []

        if not graph:
            return []

        graphs = []
        for node in graph.get_nodes():
            if node.is_compound_node():
                sub_graph = node.get_compound_graph_instance()
                if sub_graph:
                    graphs.append(sub_graph)
        return graphs

    # ----------------------------------------------------------------------------------------------
    @classmethod
    def get_connected_port_in_subgraph(cls, port: Sdf.Path):
        """
        Given a port on a compound subgraph, get the attribute in the compound subgraph that drives it.
        If there is more than one driving attr, return the one with a matching name, otherwise None.

        Args:
            port:       Port on the compound node

        Return: og.Attribute or None
        """
        try:
            attr = og.Controller.attribute(str(port))
        except og.OmniGraphError:
            return None

        is_input = attr.get_port_type() == og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT
        connections = attr.get_downstream_connections() if is_input else attr.get_upstream_connections()

        # Only one attr driving the input/output on the compound? Then just return it, otherwise ensure the name
        # matches
        if len(connections) == 1:
            return connections[0]
        for c in connections:
            if attr.get_name() == c.get_name():
                return c
        return None

    @classmethod
    def get_root_graph_prim(cls, graph_id: Union[og.Graph, Usd.Prim, Sdf.Path, str]) -> Usd.Prim:
        """
        Given an object representing a graph (either as a graph, a prim or a path) returns the Usd.Prim of the root
        graph.

        Returns:
            The prim of the object passed in if it's a root graph, the prim of the root graph if the object is a graph
            or None if the graph_id does not have a valid graph or root graph.

        """
        try:
            graph = og.Controller.graph(graph_id)
        except og.OmniGraphError:
            return None

        if not graph:
            return None

        root_graph = graph
        while root_graph.is_compound_graph():
            root_graph = root_graph.get_owning_compound_node().get_graph()

        try:
            return og.Controller.prim(root_graph)
        except og.OmniGraphError:
            return None
