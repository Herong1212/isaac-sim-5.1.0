"""Accessor for objects associated with OmniGraph"""

import os
from contextlib import suppress
from typing import List, Optional, Tuple, Union

import omni.graph.core as og
import omni.usd
from carb import log_info, log_warn
from pxr import Sdf, Usd

from .type_aliases import (
    AttributeSpec_t,
    AttributeSpecs_t,
    AttributeType_t,
    GraphSpec_t,
    GraphSpecs_t,
    Node_t,
    NodeSpec_t,
    NodeSpecs_t,
    NodeType_t,
    NodeTypes_t,
    Prim_t,
    Prims_t,
    Variable_t,
    VariableName_t,
    Variables_t,
)

# Debugging variable that provides an efficient way of using the logging mechanism for persistent debugging.
# Use the pattern "DBG and log_info(f'Hello {world}')" to prevent the string formatting when debugging is off
DBG = os.getenv("OGN_DEBUG_OBJECTS") is not None


# =====================================================================
class ObjectLookup:
    """Helper to extract OmniGraph types from various types of descriptions for them.

    These functions take flexible spec types that identify attributes, nodes, or graphs. In most cases the spec types
    can be either one of or a list of the objects being used or found by the functions. The forms each spec type can
    take are as follows:

    **GraphSpec_t**
        - An omni.graph.core.Graph object
        - A string containing the path to an omni.graph.core.Graph object
        - An Sdf.Path containing the path to an omni.graph.core.Graph object
        - A list of any of the above

    **NodeSpec_t**
        - An omni.graph.core.Node object
        - A string containing the path to an omni.graph.core.Node object
        - An Sdf.Path containing the path to an omni.graph.core.Node object
        - A Usd.Prim or Usd.Typed that is the USD backing of an
          omni.graph.core.Node object
        - None, for situations in which the node itself is redundant information
        - A 2-tuple consisting of a string and a omni.graph.core.GraphSpec_t, where the string is a relative
          path to the omni.graph.core.Node object within the omni.graph.core.Graph
        - A list of any of the above

    **AttributeSpec_t**
        - An omni.graph.core.Attribute object
        - A string containing the full path to the omni.graph.core.Attribute object on the USD stage
        - An Sdf.Path containing the full path to the omni.graph.core.Attribute object on the USD stage
        - A Usd.Attribute or Usd.Relationship that is the USD backing of an omni.graph.core.Attribute object
        - A 2-tuple consisting of a string and a NodeSpec_t, where the string is the omni.graph.core.Attribute object's
          name within the omni.graph.core.Node
        - A list of any of the above

    **Prim_t**
        - A Usd.Prim or Usd.Typed object
        - A string containing the path to a Usd.Prim or Usd.Typed object
        - An Sdf.Path containing the path to a Usd.Prim or Usd.Typed object
        - A NodeSpec_t, identifying a node whose USD backing Usd.Prim or Usd.Typed object is
          to be returned
        - A list of any of the above

    **Variables_t**
        - An omni.graph.core.IVariable object
        - A 2-tuple consisting of a omni.graph.core.GraphSpec_t and a string, where the string is the name
          of the variable
        - A string containing the path of the attribute representing the variable
        - An Sdf.Path containing the path of the attribute representing the variable
        - A list of any of the above
    """

    # ----------------------------------------------------------------------
    @classmethod
    def graph(cls, graph_id: Optional[GraphSpecs_t]) -> Union[og.Graph, List[og.Graph]]:
        """Returns the OmniGraph graph(s) corresponding to the variable type parameter

        Args:
            graph_id: Information for the graph to find. If a list then iterate over the list

        Returns:
            omni.graph.core.Graph | list[omni.graph.core.Graph]: Graph(s) corresponding to the description(s) in the
                current scene, None where there is no match

        Raises:
            OmniGraphError: if a graph matching the identifier wasn't found
        """
        _ = DBG and log_info(f"Looking up graph with {graph_id}")

        def __find_graph(graph_info: GraphSpec_t) -> Optional[og.Graph]:
            """Find a graph matching the type hints, or None if no such graph exists"""
            graph = None
            if isinstance(graph_info, og.Graph):
                graph = graph_info
            elif isinstance(graph_info, str):
                graph = og.get_graph_by_path(graph_info)
            elif isinstance(graph_info, Sdf.Path):
                graph = og.get_graph_by_path(str(graph_info.GetPrimPath()))
            elif isinstance(graph_info, (Usd.Prim, Usd.Typed)):
                graph = og.get_graph_by_path(str(graph_info.GetPath()))

            # Invalid graph is an error
            if graph is not None and not graph.is_valid():
                raise og.OmniGraphError(f"Graph description not a string, path or og.Graph - {graph}")

            return graph

        if isinstance(graph_id, list):
            return [__find_graph(graph_in_list) for graph_in_list in graph_id]

        return __find_graph(graph_id)

    # ----------------------------------------------------------------------
    @classmethod
    def node(cls, node_id: NodeSpecs_t, graph_id: Optional[GraphSpec_t] = None) -> Union[og.Node, List[og.Node]]:
        """Returns the OmniGraph node(s) corresponding to the variable type parameter

        Args:
            node_id: Information for the node to find. If a list then iterate over the list
            graph_id: Identifier for graph to which the node belongs.

        Returns:
            omni.graph.core.Node | list[omni.graph.core.Node]: Node(s) corresponding to the description(s) in the
                current graph, None where there is no match

        Raises:
            OmniGraphError: node description wasn't a recognized type or if a mismatched graph was passed in
            og.OmniGraphValueError: If the node description did not match a node in the graph
        """
        _ = DBG and log_info(f"Looking up node with {node_id}, {graph_id}")

        graph_lookup = cls.graph(graph_id)

        def __verify_graph(nodes_graph: Optional[og.Graph], msg: str):
            """Raises og.OmniGraphError if the graph is invalid or not compatible with the one passed to the parent"""
            if nodes_graph is None:
                raise og.OmniGraphError(f"Node graph not found when looking up by {msg}")
            if graph_lookup is None:
                return
            if nodes_graph.get_handle() != graph_lookup.get_handle():
                # TODO: This is a bug in node/graph association where on load it is associated with the root graph but
                #       when created interactively it is associated with the nearest ancestor subgraph.
                # In the case of a compound node, the node graph will be a child of graph_lookup
                if graph_lookup.get_path_to_graph().startswith(nodes_graph.get_path_to_graph()) or (
                    nodes_graph.is_compound_graph()
                    and nodes_graph.get_path_to_graph().startswith(graph_lookup.get_path_to_graph())
                ):
                    return
                raise og.OmniGraphError(
                    f"Node graph {nodes_graph.get_path_to_graph()} did not match {graph_lookup.get_path_to_graph()}"
                )

        def __node_from_info(node: NodeSpec_t) -> og.Node:
            """Helper to extract a single node"""
            og_node = None
            error = None
            if isinstance(node, og.Node):
                og_node = node
                __verify_graph(og_node.get_graph(), "OmniGraph node")
            elif isinstance(node, tuple):
                if len(node) != 2:
                    error = "Node tuple description must be (node_id, graph_id)"
                else:
                    og_node = cls.node(node[0], node[1])
            elif isinstance(node, Usd.Prim):
                og_node = og.get_node_by_path(str(node.GetPrimPath()))
                if og_node is None:
                    error = f"Prim '{node.GetPrimPath()}' was not an OmniGraph node"
                else:
                    __verify_graph(og_node.get_graph(), f"Prim '{node.GetPrimPath()}'")
            elif isinstance(node, Usd.Typed):
                og_node = og.get_node_by_path(str(node.GetPath()))
                if og_node is None:
                    error = f"Schema prim '{node.GetPath()}' was not an OmniGraph node"
                else:
                    __verify_graph(og_node.get_graph(), f"Prim '{node.GetPrimPath()}'")
            elif isinstance(node, Sdf.Path):
                og_node = og.get_node_by_path(str(node.GetPrimPath()))
                if og_node is None:
                    error = f"Sdf path '{node.GetPrimPath()}' was not an OmniGraph node"
                else:
                    __verify_graph(og_node.get_graph(), f"Sdf path '{node.GetPrimPath()}'")
            elif isinstance(node, str):
                node_path = (
                    node
                    if node.startswith("/") or graph_lookup is None
                    else f"{graph_lookup.get_path_to_graph()}/{node}"
                )
                if node_path.find(".") >= 0:
                    log_warn(f"Finding a node_path using an attribute path {node_path} - ignoring the attribute part")
                    og_node = og.get_node_by_path(node_path.split(".")[0])
                else:
                    og_node = og.get_node_by_path(node_path)
                if og_node is None:
                    error = f"Node path '{node_path}' was not an OmniGraph node"
                else:
                    __verify_graph(og_node.get_graph(), f"String path '{node_path}'")
            else:
                error = "Unknown node specification type"

            if og_node is None:
                raise og.OmniGraphValueError(f"Could not find OmniGraph node from node description '{node}' - {error}")

            return og_node

        if isinstance(node_id, list):
            return [__node_from_info(node_in_list) for node_in_list in node_id]

        return __node_from_info(node_id)

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def node_path(cls, node_spec: NodeSpec_t) -> str:
        """Infers a node path from a spec where the node may or may not exist

        Args:
            node_spec: Description of a path to a node that may or may not exist

        Returns:
            str: The path inferred from the node spec. No assumption should be made about the validity of the path.

        Raises:
            OmniGraphError: If there was something inconsistent in the node spec or a path could not be inferred
        """
        if isinstance(node_spec, str):
            return node_spec
        if isinstance(node_spec, Sdf.Path):
            return str(node_spec)
        if isinstance(node_spec, Usd.Prim):
            return str(node_spec.GetPrimPath())
        if isinstance(node_spec, Usd.Typed):
            return str(node_spec.GetPath())
        if isinstance(node_spec, og.Node):
            return node_spec.get_prim_path()
        if isinstance(node_spec, tuple) and len(node_spec) == 2:
            (node_path, graph_spec) = node_spec
            if isinstance(graph_spec, str):
                return f"{graph_spec}/{node_path}"
            if isinstance(graph_spec, Sdf.Path):
                return f"{graph_spec}/{node_path}"
            if isinstance(graph_spec, og.Graph):
                return f"{graph_spec.get_path_to_graph()}/{node_path}"

        raise og.OmniGraphError(f"Could not infer node path from '{node_spec}'")

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def prim_path(cls, prim_ids: Prims_t) -> Union[str, List[str]]:
        """Infers a prim path from a spec where the prim may or may not exist

        Args:
            prim_ids: Identifier of a prim or list of prims that may or may not exist

        Returns:
            str | list[str]: Path(s) inferred from the prim spec(s). No assumption should be made about their validity.

        Raises:
            OmniGraphError: If there was something inconsistent in the prim spec or a path could not be inferred
        """
        _ = DBG and log_info(f"Looking up prim path with {prim_ids}")

        def __prim_path_from_info(prim_id: Prim_t) -> str:
            """Infer a single path from a prim specification"""
            if isinstance(prim_id, str):
                return prim_id
            if isinstance(prim_id, Sdf.Path):
                return str(prim_id)
            if isinstance(prim_id, Usd.Prim):
                if not prim_id.IsValid():
                    raise og.OmniGraphError("Could not infer prim path from invalid prim")
                return str(prim_id.GetPrimPath())
            if isinstance(prim_id, Usd.Typed):
                if not prim_id.IsValid():
                    raise og.OmniGraphError("Could not infer prim path from invalid schema")
                return str(prim_id.GetPath())
            if isinstance(prim_id, og.Node):
                if not prim_id.is_valid():
                    raise og.OmniGraphError("Could not infer prim path from invalid node")
                return prim_id.get_prim_path()
            if isinstance(prim_id, og.Graph):
                if not prim_id.is_valid():
                    raise og.OmniGraphError("Could not infer prim path from invalid graph")
                return prim_id.get_path_to_graph()
            if isinstance(prim_id, tuple):
                omg_node = cls.node(prim_id)
                return omg_node.get_prim_path() if omg_node.is_valid() else None

            raise og.OmniGraphError(f"Could not infer prim path from '{prim_id}'")

        if isinstance(prim_ids, list):
            return [__prim_path_from_info(node_in_list) for node_in_list in prim_ids]

        return __prim_path_from_info(prim_ids)

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def attribute(
        cls, attribute_id: AttributeSpecs_t, node_id: Optional[Node_t] = None, graph_id: Optional[GraphSpec_t] = None
    ) -> Union[og.Attribute, List[og.Attribute]]:
        """Returns the OmniGraph attribute(s) corresponding to the variable type parameter

        Args:
            attribute_id: Information on which attribute to look for. If a list then get all of them. The attribute_id
                          can take one of several forms, for maximum flexibility:

                          - a 2-tuple consisting of the attribute name as str and a node spec. The named attribute must
                            exist on the node - e.g. ("inputs:value", my_node) or ("inputs:value", "/Graph/MyNode").
                            This is equivalent to passing in the attribute and node spec as two different parameters.
                            You'd use this form when requesting several attributes from different nodes rather than
                            a bunch of attributes from the same node.
                          - a str or Sdf.Path pointing directly to the attribute - e.g. "/Graph/MyNode/inputs:value"
                          - a str that's an attribute name, iff the node_id is also specified
                          - a Usd.Attribute or Usd.Relationship pointing to the attribute's reference on the USD side

            node_id: Node to which the attribute belongs, when only the attribute's name is provided
            graph_id: Graph to which the node and attribute belong.

        Returns:
            Attribute(s) matching the description(s) - None where there is no match

        Raises:
            OmniGraphError: if the attribute description wasn't one of the recognized types, if
                any of the attributes could not be found, or if there was a mismatch in node or graph and attribute.
        """
        _ = DBG and log_info(f"Looking up attribute with {attribute_id}, {node_id}, {graph_id}")

        def __attribute_from_info(attribute_id: AttributeSpec_t) -> Optional[og.Attribute]:
            """Helper to extract a single attribute"""
            graph = cls.graph(graph_id)
            try:
                node = cls.node(node_id, graph)
            except og.OmniGraphValueError:
                node = None

            og_attribute = None
            try:
                if isinstance(attribute_id, og.Attribute):
                    if node is not None and attribute_id.get_node().get_handle() != node.get_handle():
                        raise og.OmniGraphError(
                            f"Attribute '{attribute_id.get_name()}' does not belong to node {node.get_prim_path()}"
                        )
                    return attribute_id

                if isinstance(attribute_id, tuple):
                    if len(attribute_id) != 2:
                        raise og.OmniGraphError("An attribute spec must be a (name, node) tuple")
                    return cls.attribute(attribute_id[0], attribute_id[1])
                if isinstance(attribute_id, Usd.Property):
                    prim_node = cls.node(attribute_id.GetPrim(), graph) if attribute_id.IsValid() else None
                    if prim_node is None:
                        raise og.OmniGraphError("USD attribute not valid")
                    if node is None:
                        node = prim_node
                    elif node.get_handle() != prim_node.get_handle():
                        raise og.OmniGraphError(
                            f"USD prim node `{prim_node.get_prim_path()}` does not match node '{node.get_prim_path()}'"
                        )
                    if not node.get_attribute_exists(attribute_id.GetName()):
                        raise og.OmniGraphError(
                            f"USD attribute '{attribute_id.GetName()}' does not refer to a legal og.Attribute"
                        )
                    og_attribute = node.get_attribute(attribute_id.GetName())
                    if og_attribute is None:
                        raise og.OmniGraphError(
                            f"USD attribute {attribute_id.get_name()} not found on node {node.get_prim_path()}"
                        )
                elif isinstance(attribute_id, (Sdf.Path, str)):
                    attribute_id = str(attribute_id)
                    if attribute_id.find(".") >= 0:
                        node_name, attribute_name = attribute_id.split(".")
                        specified_node = cls.node(node_name, graph)
                        if node is None:
                            node = specified_node
                        elif specified_node is None or node.get_handle() != specified_node.get_handle():
                            raise og.OmniGraphError("Attribute path is not a legal node/attribute combination")
                        if node is None:
                            raise og.OmniGraphError("Node of fully specified attribute path not found")
                    elif node is None:
                        # Bundle outputs do not have a "." separator so check to see if it's one of those
                        node_name, attribute_name = attribute_id.rsplit("/", 1)
                        node = cls.node(node_name, graph)
                        if node is None:
                            raise og.OmniGraphError("Node is required when only an attribute name is given")
                    else:
                        attribute_name = attribute_id
                    if not node.get_attribute_exists(attribute_name):
                        raise og.OmniGraphError(
                            f"Attribute named '{attribute_name}' does not refer to a legal og.Attribute"
                        )
                    og_attribute = node.get_attribute(attribute_name)
                    if og_attribute is None:
                        raise og.OmniGraphError(
                            f"Attribute named '{attribute_name}' not found on node '{node.get_prim_path()}'"
                        )
                    if og_attribute.get_node().get_handle() != node.get_handle():
                        raise og.OmniGraphError(
                            f"OmniGraph attribute {og_attribute.get_name()} does not belong to"
                            f" passed in node {node.get_prim_path()}"
                        )
                else:
                    raise og.OmniGraphError("Unrecognized specification used to try to look up an OmniGraph attribute")
            except og.OmniGraphError as error:
                raise og.OmniGraphError(
                    f"Failed trying to look up attribute with ({attribute_id}, node={node_id}, graph={graph_id})"
                ) from error

            return og_attribute

        if isinstance(attribute_id, list):
            return [__attribute_from_info(attribute_in_list) for attribute_in_list in attribute_id]

        return __attribute_from_info(attribute_id)

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def attribute_path(cls, attribute_spec: AttributeSpec_t) -> str:
        """Infers an attribute path from a spec where the attribute may or may not exist

        Args:
            attribute_spec: Location of where the attribute would be, if it exists

        Returns:
            str: Location of the attribute, if it exists

        Raises:
            OmniGraphError: If there was something inconsistent in the attribute spec or a path could not be inferred
        """
        # Deduce the path from the type information provided
        if isinstance(attribute_spec, Sdf.Path):
            return str(attribute_spec)
        if isinstance(attribute_spec, str):
            return attribute_spec
        if isinstance(attribute_spec, Usd.Property):
            return str(attribute_spec.GetPath())
        if isinstance(attribute_spec, og.Attribute):
            return cls.attribute_path((attribute_spec.get_name(), attribute_spec.get_node()))
        if isinstance(attribute_spec, tuple) and len(attribute_spec) == 2:
            # Assemble the two components of the path using strings instead of the Sdf.Path interface because
            # there is no guarantee or requirement that the path exist.
            (attribute_name, node_spec) = attribute_spec
            node_path = cls.node_path(node_spec)
            return f"{node_path}.{attribute_name}"

        raise og.OmniGraphError(f"Could not infer an attribute path from '{attribute_spec}'")

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def attribute_type(cls, type_id: str | AttributeType_t | og.Attribute | og.AttributeData) -> og.Type:
        """Returns the OmniGraph attribute type corresponding to the variable type parameter.

        All legal OGN types are recognized, as well as the UNKNOWN type.

        Args:
            type_id: Variable description of the attribute type object as one of:

                     - An omni.graph.core.Type object
                     - An OGN-style type description - e.g. "float[3]"
                     - An Sdf-style type description - e.g. "float3"
                     - An omni.graph.core.Attribute whose (resolved) type is to be retrieved
                     - An omni.graph.core.AttributeData whose (resolved) type is to be retrieved

        Returns:
            omni.graph.core.Type: Attribute type matching the description

        Raises:
            OmniGraphError: if the attribute type description wasn't one of the recognized types
        """
        _ = DBG and log_info(f"Looking up attribute type with {type_id}")

        if isinstance(type_id, og.Attribute):
            return type_id.get_resolved_type()

        if isinstance(type_id, og.AttributeData):
            return type_id.get_type()

        if isinstance(type_id, og.Type):
            if not og.AttributeType.is_legal_ogn_type(type_id) and type_id.base_type != og.BaseDataType.UNKNOWN:
                raise og.OmniGraphError(f"Attribute type {type_id} does not represent a legal OGN type")
            return type_id

        if isinstance(type_id, str):
            if type_id == "unknown":
                return og.Type(og.BaseDataType.UNKNOWN)
            attribute_type = og.AttributeType.type_from_ogn_type_name(type_id)
            if attribute_type.base_type == og.BaseDataType.UNKNOWN:
                attribute_type = og.AttributeType.type_from_sdf_type_name(type_id)
            if og.AttributeType.is_legal_ogn_type(attribute_type):
                return attribute_type

        raise og.OmniGraphError(f"Attribute type description '{type_id}' could not be parsed into a type")

    # ----------------------------------------------------------------------
    @classmethod
    def node_type(cls, type_id: NodeTypes_t) -> Union[og.NodeType, List[og.NodeType]]:
        """Returns the OmniGraph node type corresponding to the variable type parameter

        Args:
            type_id: Information used to identify the omni.graph.core.NodeType object; it will be one of:

            - an omni.graph.core.NodeType object
            - a string that is the unique identifier of the node type
            - an omni.graph.core.Node whose type is to be returned
            - a Usd.Prim or Usd.Typed that is the USD backing of an omni.graph.core.Node whose type is to be returned
            - a list of any combination of the above

        Returns:
            omni.graph.core.NodeType | list[omni.graph.core.NodeType]: Node type(s) matching the description

        Raises:
            OmniGraphError: if the node type description wasn't one of the recognized types or could not be found
        """
        _ = DBG and log_info(f"Looking up node type with {type_id}")

        def __node_type(node_type_id: NodeType_t) -> og.NodeType:
            """Look up a single node type from descriptive information"""
            node_type = None
            try:
                if isinstance(node_type_id, og.NodeType):
                    node_type = node_type_id
                elif isinstance(node_type_id, str):
                    node_type = og.get_node_type(node_type_id)
                elif isinstance(node_type_id, (og.Node, Usd.Prim, Usd.Typed)):
                    node_type = cls.node(node_type_id).get_node_type()
                else:
                    raise TypeError(
                        "ID type must be og.NodeType, str, og.Node, Usd.Prim, or Usd.Typed -"
                        f" {node_type_id} not recognized"
                    )
            except Exception as error:
                raise og.OmniGraphError(f"Failed to deduce node type from '{node_type_id}' - {error}")
            if node_type is None or not node_type.is_valid():
                raise og.OmniGraphError(f"'{node_type_id}' is not a recognized node type")
            return node_type

        if isinstance(type_id, list):
            return [__node_type(one_type_id) for one_type_id in type_id]
        return __node_type(type_id)

    # ----------------------------------------------------------------------
    @classmethod
    def prim(cls, prim_id: Prims_t) -> Union[Usd.Prim, List[Usd.Prim]]:
        """Returns the prim(s) corresponding to the node descriptions

        Args:
            prim_id: Information for the node to find. If a list then iterate over the list

        Returns:
            Usd.Prim | list[Usd.Prim]: Prim(s) corresponding to the description(s) in the current graph,
                None where there is no match

        Raises:
            OmniGraphError: if the node description(s) didn't correspond to a valid prim(s).
        """
        _ = DBG and log_info(f"Looking up prim with {prim_id}")

        stage = omni.usd.get_context().get_stage()
        if stage is None:  # pragma: no cover
            raise og.OmniGraphError(f"Cannot get prim on node '{prim_id}' - there is no USD stage")

        def __prim_from_info(item: Prim_t):
            """Helper to find a single prim"""
            prim_to_return = None
            if isinstance(item, Sdf.Path):
                prim_to_return = stage.GetPrimAtPath(item.GetPrimPath())
            elif isinstance(item, og.Node):
                prim_to_return = stage.GetPrimAtPath(item.get_prim_path()) if item.is_valid() else None
            elif isinstance(item, og.Graph):
                prim_to_return = stage.GetPrimAtPath(item.get_path_to_graph()) if item.is_valid() else None
            elif isinstance(item, Usd.Prim):
                prim_to_return = item
            elif isinstance(item, Usd.Typed):
                prim_to_return = item.GetPrim()
            elif isinstance(item, str):
                prim_path = cls.prim_path(item)
                if prim_path is not None:
                    prim_to_return = stage.GetPrimAtPath(prim_path)
            elif isinstance(item, tuple):
                omg_node = cls.node(item)
                prim_to_return = stage.GetPrimAtPath(omg_node.get_prim_path()) if omg_node.is_valid() else None
            if prim_to_return is None or not prim_to_return.IsValid():
                raise og.OmniGraphError(f"Failed to get prim on object '{prim_id}'")
            return prim_to_return

        if isinstance(prim_id, list):
            return [__prim_from_info(prim_id_in_list) for prim_id_in_list in prim_id]

        return __prim_from_info(prim_id)

    # ----------------------------------------------------------------------
    @classmethod
    def usd_attribute(cls, attribute_specs: AttributeSpecs_t) -> Union[Usd.Attribute, List[Usd.Attribute]]:
        """Returns the Usd.Attribute(s) corresponding to the attribute descriptions

        Args:
            attribute_specs: Location or list of locations from which to infer a matching Usd.Attribute

        Returns:
            Usd.Attribute | list[Usd.Attribute]: Usd.Attribute(s) corresponding to the description(s) in the USD stage

        Raises:
            OmniGraphError: if the attribute description didn't correspond to a valid Usd.Attribute.
        """
        _ = DBG and log_info(f"Looking up Usd.Attribute(s) with {attribute_specs}")

        stage = omni.usd.get_context().get_stage()
        if stage is None:  # pragma: no cover
            raise og.OmniGraphError(f"Cannot get Usd.Attributes from '{attribute_specs}' - there is no USD stage")

        def __usd_attribute_from_info(attribute_id: AttributeSpec_t):
            """Helper to find a single prim"""
            usd_attribute = stage.GetAttributeAtPath(cls.attribute_path(attribute_id))
            if usd_attribute.IsValid():
                return usd_attribute
            raise og.OmniGraphError(
                f"Attribute spec '{attribute_id}' did not correspond to a valid USD attribute"
                f" from {cls.attribute_path(attribute_id)}"
            )

        if isinstance(attribute_specs, list):
            return [__usd_attribute_from_info(attribute_spec) for attribute_spec in attribute_specs]

        return __usd_attribute_from_info(attribute_specs)

    # ----------------------------------------------------------------------
    @classmethod
    def usd_property(cls, attribute_specs: AttributeSpecs_t) -> Union[Usd.Property, List[Usd.Property]]:
        """Returns the Usd.Property(s) corresponding to the attribute descriptions

        Args:
            attribute_specs: Location or list of locations from which to infer a matching Usd.Property

        Returns:
            Usd.Property | list[Usd.Property]: Usd.Property(s) corresponding to the description(s) in the USD stage

        Raises:
            OmniGraphError: if the attribute description didn't correspond to a valid Usd.Property.
        """
        _ = DBG and log_info(f"Looking up Usd.Property(s) with {attribute_specs}")

        stage = omni.usd.get_context().get_stage()
        if stage is None:  # pragma: no cover
            raise og.OmniGraphError(f"Cannot get Usd.Property(s) from '{attribute_specs}' - there is no USD stage")

        def __usd_property_from_info(attribute_id: AttributeSpec_t):
            """Helper to find a single prim"""
            usd_property = stage.GetPropertyAtPath(cls.attribute_path(attribute_id))
            if usd_property.IsValid():

                return usd_property
            raise og.OmniGraphError(
                f"Attribute spec '{attribute_id}' did not correspond to a valid USD property"
                f" from {cls.attribute_path(attribute_id)}"
            )

        if isinstance(attribute_specs, list):
            return [__usd_property_from_info(attribute_spec) for attribute_spec in attribute_specs]

        return __usd_property_from_info(attribute_specs)

    # ----------------------------------------------------------------------
    @classmethod
    def usd_relationship(cls, attribute_specs: AttributeSpecs_t) -> Union[Usd.Relationship, List[Usd.Relationship]]:
        """Returns the Usd.Relationships(s) corresponding to the attribute descriptions

        Args:
            attribute_specs: Location or list of locations from which to infer a matching Usd.Attribute

        Returns:
            Usd.Relationship | list[Usd.Relationship]: Usd.Relationship(s) corresponding to the description(s) in the USD stage

        Raises:
            OmniGraphError: if the attribute description didn't correspond to a valid Usd.Relationship.
        """
        _ = DBG and log_info(f"Looking up Usd.Relationship(s) with {attribute_specs}")

        stage = omni.usd.get_context().get_stage()
        if stage is None:  # pragma: no cover
            raise og.OmniGraphError(f"Cannot get Usd.Relationships from '{attribute_specs}' - there is no USD stage")

        def __usd_relationship_from_info(attribute_id: AttributeSpec_t):
            """Helper to find a single prim"""
            usd_relationship = stage.GetRelationshipAtPath(cls.attribute_path(attribute_id))
            if usd_relationship.IsValid():
                return usd_relationship
            raise og.OmniGraphError(
                f"Attribute spec '{attribute_id}' did not correspond to a valid USD relationship"
                f" from {cls.attribute_path(attribute_id)}"
            )

        if isinstance(attribute_specs, list):
            return [__usd_relationship_from_info(attribute_spec) for attribute_spec in attribute_specs]

        return __usd_relationship_from_info(attribute_specs)

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def split_graph_from_node_path(cls, node_path: Union[str, Sdf.Path]) -> Tuple[og.Graph, str]:
        """Find the lowest level graph from a node path

        The path /World/Graph1/Graph2/Node1/Node2 would return the og.Graph at /World/Graph1/Graph2 and the
        relative node path "Node1/Node2".

        Args:
            node_path: Full path to the node from the root

        Returns:
            tuple[omni.graph.core.Graph, str]: where graph is the lowest graph in the tree and node_path is the
                relative path to the node from the graph
        """
        if isinstance(node_path, Sdf.Path):
            node_path = str(node_path)

        relative_path = []
        graph = None
        while (graph is None or not graph.is_valid()) and node_path:
            graph = og.get_graph_by_path(node_path)
            if graph is None or not graph.is_valid():
                try:
                    (node_path, base) = node_path.rsplit("/", maxsplit=1)
                except ValueError:
                    # No "/" in the string cannot be a legal node name - assume it's a graph name only
                    return (node_path, None)
                relative_path.append(base)

        return (graph, "/".join(reversed(relative_path)))

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def variable(cls, variable_id: Variables_t) -> Union[og.IVariable, List[og.IVariable]]:
        """Returns the variables(s) corresponding to the variable description

        Args:
            variable_id: Information for the variable to find. If a list then iterate over the list

        Returns:
            omni.graph.core.IVariable | list[omni.graph.core.IVariable]: Variables(s) corresponding to the
                description(s) in the current graph, None where there is no match

        Raises:
            OmniGraphError: if the variable description didn't correspond to a valid variable
        """
        _ = DBG and log_info(f"Looking up og.IVariable with {variable_id}")

        def var_from_info(var: Variable_t):
            var_to_return = None
            if isinstance(var, og.IVariable):
                var_to_return = var
            if isinstance(var, tuple) and len(var) == 2:
                (graph_spec, var_name) = var
                if isinstance(var_name, VariableName_t):
                    graph = cls.graph(graph_spec)
                    var_to_return = graph.find_variable(var_name)
            if isinstance(var, str):
                var = Sdf.Path(var)
            if isinstance(var, Sdf.Path):
                graph = cls.graph(var.GetPrimPath())
                if graph is None or not graph.is_valid():
                    raise og.OmniGraphError(f"Variable spec {var} does not reference a valid graph object")
                var_to_return = graph.find_variable(Sdf.Path.StripNamespace(var.name))
            if var_to_return is None:
                raise og.OmniGraphError(f"Failed to get variable {var}")
            return var_to_return

        if isinstance(variable_id, list):
            return [var_from_info(x) for x in variable_id]

        return var_from_info(variable_id)

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def compound_graph(cls, node_id: NodeSpecs_t) -> og.Graph | None | List[og.Graph | None]:
        """Returns the compound graph of a given node or nodes, or None if the node does not contain a compound graph

        Args:
             node_id: Information for the node to find. If a list then iterate over the list

         Returns:
             omni.graph.core.Graph | None | list[omni.graph.core.Graph | None]: The compound graph instances
                the contained by the given nodes. If node does not encapsulate a compound graph, the value None is returned.

         Raises:
             omni.graph.core.OmniGraphError: node_id description wasn't a recognized type
        """
        _ = DBG and log_info(f"Looking up Compound Graph with {node_id}")

        def _node_to_compound_graph(node: og.Node):
            compound_graph = node.get_compound_graph_instance()
            return compound_graph if compound_graph else None

        # Will raise if node_id is malformed.
        nodes = cls.node(node_id)
        if isinstance(nodes, list):
            return [_node_to_compound_graph(node) for node in nodes]
        return _node_to_compound_graph(nodes)

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def compound_node(
        cls, item_id: GraphSpec_t | NodeSpec_t | List[GraphSpec_t | NodeSpec_t]
    ) -> og.Node | None | List[og.Graph | None]:
        """Returns the owning compound node for a given graph, or node, or None if the graph or node is not encapsulated by a compound node

        Args:
            item_id: The graph, node, or list of graphs and nodes, to retrieve the owning compound node(s) for.

        Returns:
            omni.graph.core.Node | None | list[omni.graph.core.Node | None]: The compound node(s) that encapsulate the provided
            graph(s), or None if the graph(s) are not encapsulated by a compound node

        Raises:
            omni.graph.core.OmniGraphError: The provided graphs or nodes are invalid or unrecognized types.
        """

        _ = DBG and log_info(f"Looking up Owning Compound with {item_id}")

        def _graph_to_owner(graph: og.Graph):
            """Given a graph, return the compound node that owns the graph"""

            # We are making the assumption that the compound node is the prim parent of the compound
            parent_path = Sdf.Path(graph.get_path_to_graph()).GetParentPath()
            node = None
            with suppress(og.OmniGraphError):
                node = cls.node(parent_path)
            if not node:
                return None

            if node.get_compound_graph_instance() == graph:
                return node

            return None

        def _to_graph(item_id):
            """Given an item, graph or node spec, return the graph object"""
            graph = None
            with suppress(og.OmniGraphError):
                graph = cls.graph(item_id)
            if graph:
                return graph

            node = None
            with suppress(og.OmniGraphError):
                node = cls.node(item_id)
            if node:
                return node.get_graph()

            raise og.OmniGraphError(f"{item_id} is not a valid OmniGraph or OmniNode")

        if isinstance(item_id, list):
            return [_graph_to_owner(_to_graph(item)) for item in item_id]

        return _graph_to_owner(_to_graph(item_id))
