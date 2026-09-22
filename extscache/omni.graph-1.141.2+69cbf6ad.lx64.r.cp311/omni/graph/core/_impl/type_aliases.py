"""Houses all of the type definitions for the various interface argument types.

For clarity these types are stored in a structure that gives them a unified naming:

.. code-block:: python

    from omni.graph.core.typing import NodeSpec_t
    def get_node(node_spec: NodeSpec_t):
        pass

The convention used is that X_t is a singular item and Xs_t is a union of the singular item and a list of them.
"""

import omni.graph.core as og
from pxr import Sdf, Usd

# ==============================================================================================================
# Values for type hints on methods that take a variety of convertible types as parameters

# --------------------------------------------------------------------------------------------------------------
# Simple types
Path_t = str | Sdf.Path
"""Typing for a path in the USD stage"""

# --------------------------------------------------------------------------------------------------------------
# Graph types (requires a Union because the new "|" syntax does not allow mixing of pybind and tuple types)
Graph_t = Path_t | og.Graph | Usd.Prim | Usd.Typed
"""Typing that identifies an existing omni.graph.core.Graph object
1a. "/MyGraph"
1b. Sdf.Path("/MyGraph")
2. og.get_current_graph()
3. stage.GetPrimAtPath("/MyGraph")
4. OmniGraphSchema.OmniGraph(prim)
"""
Graphs_t = Graph_t | list[Graph_t]
"""Typing that identifies a list of existing omni.graph.core.Graph objects"""
# Added specs for consistency, though for graphs no extra information is currently needed to identify them
GraphSpec_t = Graph_t
"""Typing that identifies an existing omni.graph.core.Graph object"""
GraphSpecs_t = Graphs_t
"""Typing that identifies a list of existing omni.graph.core.Graph objects"""

# --------------------------------------------------------------------------------------------------------------
# Node types
NewNode_t = Path_t | tuple[str | Graph_t]
"""Typing for information required to create a new node
1a. "/MyGraph/MyNode"
1b. Sdf.Path("/MyGraph/MyNode")
2. ("MyNode", og.Controller.graph("/MyGraph"))
"""

Node_t = str | og.Node | Sdf.Path | Usd.Prim | Usd.Typed
"""Typing that identifies an existing omni.graph.core.Node object
1. "/MyGraph/MyNode"
2. og.Controller.node("/MyGraph/MyNode")
3. Sdf.Path("/MyGraph/MyNode")
4. stage.GetPrimAtPath("/MyGraph/MyNode")
5. OmniGraphSchema.OmniGraphNode(my_prim)
"""
Nodes_t = Node_t | list[Node_t]
"""Typing that identifies a list of existing omni.graph.core.Node objects"""

NodeSpec_t = Node_t | tuple[str | GraphSpec_t]
"""Typing that identifies an existing omni.graph.core.Node object, with optional graph for disambiguation
1. As per Node_t
2. ("MyNode", As per GraphSpec_t)
"""
NodeSpecs_t = NodeSpec_t | list[NodeSpec_t]
"""Typing that identifies a list of existing omni.graph.core.Node objects, with optional graph for disambiguation"""

# --------------------------------------------------------------------------------------------------------------
# NodeType types
NodeType_t = str | og.NodeType | og.Node | Usd.Prim | Usd.Typed
"""Typing that identifies an existing omni.graph.core.NodeType object
1. "omni.graph.nodes.Add"
2. og.Controller.node_type("omni.graph.nodes.Add")
3. og.Controller.node("/MyGraph/MyAddNode")
4. stage.GetPrimAtPath("/MyGraph/MyAddNode")
5. OmniGraphSchema.OmniGraphNode(my_add_prim)
"""
NodeTypes_t = NodeType_t | list[NodeType_t]
"""Typing that identifies a list of existing omni.graph.core.NodeType objects"""

# --------------------------------------------------------------------------------------------------------------
# Attribute Types
ExtendedAttribute_t = og.ExtendedAttributeType | tuple[og.ExtendedAttributeType, str | list[str]]
"""Typing for an extended attribute type description
1. og.ExtendedAttributeType.ANY
2. (og.ExtendedAttributeType.UNION, "numerics")
3. (og.ExtendedAttributeType.UNION, ["float", "double"])
"""

AttributeName_t = str | tuple[str, og.AttributePortType]
"""Typing for an attribute name
1. "inputs:foo"
2. ("foo", og.AttributePortType.INPUT)
"""

NewAttribute_t = Path_t | tuple[AttributeName_t, Node_t] | tuple[AttributeName_t, str, Graph_t]
"""Typing for the information required to uniquely identify an attribute that does not yet exist
1a. "/MyGraph/MyNode/inputs:new_attr"
1b. Sdf.Path("/MyGraph/MyNode/inputs:new_attr")
2a. ("inputs:new_attr", og.Controller.node("/MyGraph/MyNode"))
2b. (("new_attr", og.AttributePortType.INPUT), og.Controller.node("/MyGraph/MyNode"))
3a. ("inputs:new_attr", "MyNode", og.Controller.graph("/MyGraph"))
3b. (("new_attr", og.AttributePortType.INPUT), "MyNode", og.Controller.graph("/MyGraph"))
"""

Attribute_t = Path_t | og.Attribute | Usd.Property
"""Typing that identifies an existing omni.graph.core.Attribute object
1a. "/MyGraph/MyNode/inputs:new_attr"
1b. Sdf.Path("/MyGraph/MyNode/inputs:new_attr")
2. og.Controller.attribute("/MyGraph/MyNode/inputs:new_attr")
3a. stage.GetPrimAtPath("/MyGraph/MyNode").GetAttribute("inputs:new_attr")
3b. stage.GetPrimAtPath("/MyGraph/MyNode").GetProperty("inputs:new_attr")
3c. stage.GetPrimAtPath("/MyGraph/MyNode").GetRelationship("inputs:new_attr")
"""
Attributes_t = Attribute_t | list[Attribute_t]
"""Typing that identifies a list of existing omni.graph.core.Attribute objects"""

AttributeWithValue_t = Attribute_t | og.AttributeData
"""Typing for an attribute-like object that references a value in Fabric"""
AttributesWithValues_t = AttributeWithValue_t | list[AttributeWithValue_t]
"""Typing for a list of attribute-like objects that reference values in Fabric"""

AttributeType_t = str | og.Type
"""Typing that identifies an existing omni.graph.core.Type definition
1. "float"
2. og.Type(og.BaseDataType.FLOAT, 1, 0, og.AttributeRole.NONE)
"""

AttributeTypeSpec_t = str | og.Type | list[str]
"""Typing that identifies a regular or extended type definition
1. "any"
2. og.Type(og.BaseDataType.FLOAT, 3, 1, og.AttributeRole.VECTOR)
3. ["float", "integral_scalers"]
"""

# An attribute that is either unique by itself or which has optional node and graph parts to help look it up.
# This would be passed in as arguments to a function that needs to uniquely identify an existing attribute.
# It differs from a regular attribute in allowing a relative path to the attribute within the node/graph
AttributeSpec_t = og.Attribute | NewAttribute_t
"""Typing for information required to identify an existing og.Attribute"""
AttributeSpecs_t = AttributeSpec_t | list[AttributeSpec_t]
"""Typing for information required to identify a list of existing og.Attributes"""

# --------------------------------------------------------------------------------------------------------------
# Prim types
Prim_t = Path_t | og.Node | Usd.Prim | Usd.Typed | og.Graph
"""Typing for an existing USD prim
1a. "/World"
1b. Sdf.Path("/World")
2. og.Controller.node("/World/MyGraph/MyNode")
3. stage.GetPrimAtPath("/World")
4. OmniGraphSchema.OmniGraph(my_prim)
5. og.Controller.graph("/World/MyGraph")
"""
Prims_t = Prim_t | list[Prim_t]
"""Typing for a list of existing USD prims"""

PrimAttrs_t = dict[str | tuple[AttributeType_t, any]]
"""Typing for a description of attribute values for a prim
1. {"inputs:fvalue", ("float", 1.0)}
2. {"inputs:dvalue", (og.Type(og.BaseDataType.DOUBLE, 1, 0), 1.0)}
"""

NewPrim_t = tuple[Path_t, PrimAttrs_t]
"""Typing for information required to create a prim with a predefined set of values
1. ("/World/NewPrim", {"inputs:fvalue", ("float", 1.0)})
"""
NewPrims_t = NewPrim_t, list[NewPrim_t]
"""Typing for information required to create a list of prims with a predefined set of values"""

# --------------------------------------------------------------------------------------------------------------
# Variable types
VariableName_t = str
"""Typing information required to specify a variable name
1. "Variable1"
"""
VariableType_t = str | og.Type
"""Typing information required to specify a variable type
1. "float[3]"
2. og.Type(og.BaseDataType.FLOAT, 3, 0)
"""
Variable_t = Path_t | og.IVariable | tuple[GraphSpec_t, VariableName_t]
"""Typing information required to specify a variable
1a. "/TestGraph.graph:variable:Variable_1"
1b. Sdf.Path("/TestGraph.graph:variable:Variable_1")
2. og.Controller.variable("/TestGraph.graph:variable:Variable_1")
3a. ("/MyGraph", "Variable1")
3b. (Sdf.Path("/MyGraph"), "Variable1")
3c. (og.get_current_graph(), "Variable1")
3d. (stage.GetPrimAtPath("/MyGraph"), "Variable1")
3e. (OmniGraphSchema.OmniGraph(prim), "Variable1")

"""
Variables_t = Variable_t | list[Variable_t]
"""Typing information required to specify a list of variable"""

CompoundSubgraphCmd_t = dict[str, any]
"""Typing information required when specifying an inline compound subgraph"""
