# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import math
from typing import Optional, Tuple, Union

import omni.graph.core as og
import omni.usd
import OmniGraphSchema
from omni.kit.widget.graph import IsolationGraphModel
from pxr import Gf, Sdf, Usd, UsdUI

from . import graph_config

_INPUT_POSITION_ATTR = "ui:nodegraph:input:pos"
_OUTPUT_POSITION_ATTR = "ui:nodegraph:output:pos"

_INPUT_NAMESPACE = og.get_port_type_namespace(og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT)
_NODE_OFFSET = 400


# ----------------------------------------------------------------------------------------------
class VirtualNodeHelper:
    """Helper class for virtual nodes - inputs and outputs - in the isolation graph model

    The isolation graph model uses virtual nodes to represent the inputs and outputs of compounds, and passes Sdf.Paths
    does to represent nodes. These methods are to aid in handling these virtual nodes representions.

    """

    # ----------------------------------------------------------------------------------------------
    @classmethod
    def is_virtual_node(cls, node_obj: Union[Sdf.Path, Usd.Prim, str]) -> bool:
        """Given a node object, determines whether the node object represents a virtual node"""
        if isinstance(node_obj, (IsolationGraphModel.InputNode, IsolationGraphModel.OutputNode)):
            return True

        if isinstance(node_obj, Usd.Prim):
            node_obj = node_obj.GetPath()

        try:
            graph = og.Controller.graph(node_obj)
            return bool(graph) and graph_config.Supports.compound_graphs() and graph.is_compound_graph()
        except og.OmniGraphError:
            pass

        return False

    # ----------------------------------------------------------------------------------------------
    @classmethod
    def is_virtual_node_port(cls, property_path: Sdf.Path) -> bool:
        """Given a property path, determines whether the property path represents a virtual node port"""
        return property_path.IsPropertyPath() and cls.is_virtual_node(property_path.GetPrimPath())

    # ----------------------------------------------------------------------------------------------
    @classmethod
    def _get_position_attribute_path(cls, property_path: Sdf.Path) -> Sdf.Path:
        """Gets the path of the virtual node attribute"""
        if not property_path.IsPropertyPath():
            raise og.OmniGraphError("Expected a property path for the virtual node position attribute")

        is_input = property_path.name.startswith(_INPUT_NAMESPACE)
        attr_name = _INPUT_POSITION_ATTR if is_input else _OUTPUT_POSITION_ATTR
        return property_path.GetPrimPath().AppendProperty(attr_name)

    # ----------------------------------------------------------------------------------------------
    @classmethod
    def get_virtual_node_position(
        cls, property_path: Sdf.Path, default_pos: Optional[Tuple[float, float]]
    ) -> Optional[Tuple[float, float]]:
        """
        Gets the position of the virtual node - input or output - corresponding to the given property path.
        If the underlying attribute does not exist, the default position is returned.

        The isolation graph model will pass an Sdf.Path of the first input or output.

        Args:
            property_path: Sdf.Path - the property path representing the virtual node.
            default_pos: Tuple[float, float] - the default position to use if the attribute does not have an authored value. Can be None.

        Returns:
            Tuple[float, float] - the position of the virtual node, or the default position if the attribute does not exist.

        Raises:
            og.OmniGraphError: if the backing prim does not exist
        """
        attr_path = cls._get_position_attribute_path(property_path)
        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath(attr_path.GetPrimPath())
        if not prim or not prim.IsA(OmniGraphSchema.OmniGraph):
            raise og.OmniGraphError(f"Invalid prim for virtual node property path: {property_path}")

        attr = prim.GetAttribute(attr_path.name)
        return default_pos if not attr else attr.Get()

    # ----------------------------------------------------------------------------------------------
    @classmethod
    def set_virtual_node_position(cls, property_path: Sdf.Path, position: Optional[Tuple[float, float]]):
        """
        Sets the position of the associated virtual node - input or output - corresponding to the given property path.

        The command will be added to the undo stack, and will create the property if necessary

        Args:
            property_path: Sdf.Path - the property path representing the node
            position: - the value to set

        """
        if position is None:
            return

        attr_path = cls._get_position_attribute_path(property_path)
        prev_pos = cls.get_virtual_node_position(property_path, position)
        omni.kit.commands.execute(
            "ChangePropertyCommand",
            prop_path=str(attr_path),
            value=Gf.Vec2f(position[0], position[1]),
            prev=Gf.Vec2f(prev_pos[0], prev_pos[1]),
            type_to_create_if_not_exist=Sdf.ValueTypeNames.Float2,
            variability=Sdf.VariabilityUniform,
        )

    # ----------------------------------------------------------------------------------------------
    @classmethod
    def compute_initial_position(cls, property_path: Sdf.Path) -> Optional[Gf.Vec2f]:
        """
        Given the virtual node property path representing the input or output node for the compound, computes the initial position

        Args:
            property_path: Sdf.Path - the property path representing the node. This is typically the first input or output on the node

        Returns:
            Gf.Vec2f - the initial position of the virtual node, or None if the property path is invalid, or there are no nodes in the subgraph

        """
        is_input = property_path.name.startswith(_INPUT_NAMESPACE)
        try:
            graph = og.Controller.graph(property_path.GetPrimPath())
        except og.OmniGraphError:
            return None

        stage = omni.usd.get_context().get_stage()
        min_pos = Gf.Vec2f(math.inf, math.inf)
        max_pos = Gf.Vec2f(-math.inf, -math.inf)
        for node in graph.get_nodes():
            node_prim = stage.GetPrimAtPath(node.get_prim_path())
            if not node_prim:
                continue
            if node_prim.HasAPI(UsdUI.NodeGraphNodeAPI):
                pos = UsdUI.NodeGraphNodeAPI(node_prim).GetPosAttr().Get() or (0, 0)
                min_pos[0] = min(min_pos[0], pos[0])
                min_pos[1] = min(min_pos[1], pos[1])
                max_pos[0] = max(max_pos[0], pos[0])
                max_pos[1] = max(max_pos[1], pos[1])

        if math.isinf(min_pos[0]):
            return None

        # have the input node be on the left, output node on the right
        if is_input:
            return Gf.Vec2f(min_pos[0] - _NODE_OFFSET, min_pos[1])

        return Gf.Vec2f(max_pos[0] + _NODE_OFFSET, min_pos[1])

    # ----------------------------------------------------------------------------------------------
    @classmethod
    def convert_from(cls, property_path: Sdf.Path) -> Sdf.Path:
        """
        Given a path, if it's a virtual node path, convert it to a path to the owning compound node.

        Args:
            (Sdf.Path) A property path representing an attribute

        Returns:
            (Sdf.Path) The converted property path, or the original if it's not a virtual node path
        """

        if not property_path.IsPropertyPath():
            return property_path

        try:
            graph = og.Controller.graph(property_path.GetPrimPath())
        except og.OmniGraphError:
            return property_path

        if not graph:
            return property_path

        node = graph.get_owning_compound_node()
        if not node:
            return property_path

        if node.is_compound_node():
            return Sdf.Path(node.get_prim_path()).AppendProperty(property_path.name)

        return property_path

    # ----------------------------------------------------------------------------------------------
    @classmethod
    def convert_to(cls, property_path: Sdf.Path) -> Sdf.Path:
        """Given a property path, if it's a path to a compound node, convert it to a virtual node path.

        Args:
            (Sdf.Path) A property path representing an attribute

        Returns:
            (Sdf.Path) The converted property path, or the original if it's not a compound node path

        """

        if not property_path.IsPropertyPath():
            return property_path

        try:
            node = og.Controller.node(property_path.GetPrimPath())
        except og.OmniGraphError:
            return property_path

        if node.is_compound_node() and node.get_compound_graph_instance():
            return Sdf.Path(node.get_compound_graph_instance().get_path_to_graph()).AppendProperty(property_path.name)

        return property_path

    # ----------------------------------------------------------------------------------------------
    @classmethod
    def convert_to_destination(cls, property_path: Sdf.Path) -> Sdf.Path:
        """Given a property path thats assumed to be a destination port of a connection, return the most
        appropriate representation.

        Args:
            (Sdf.Path) A property path representing an attribute

        Returns:
            (Sdf.Path) The converted path for a destination port
        """
        compound_node_path = cls.convert_from(property_path)
        compound_graph_path = cls.convert_to(property_path)

        if compound_node_path == compound_graph_path:
            return property_path

        # for input ports, the connection is from the compound node, so return the port from there
        if compound_node_path.name.startswith(_INPUT_NAMESPACE):
            return compound_node_path

        # otherwise, it's an output port, and the destination is the virtual (i.e. compound graph) port
        return compound_graph_path

    # ----------------------------------------------------------------------------------------------
    @classmethod
    def convert_connection(cls, src_path: Sdf.Path, dest_path: Sdf.Path) -> Tuple[Sdf.Path]:
        """
        Given a connection, convert the paths to the appropriate virtual node paths.
        No conversion is done if they are nodes in the same graph

        Args:
            src_path: Sdf.Path - the source path
            dest_path: Sdf.Path - the destination path

        Returns:
            Tuple[Sdf.Path] - the converted paths
        """
        subgraph_src_path = cls.convert_to(src_path)
        compound_src_path = cls.convert_from(src_path)

        subgraph_dest_path = cls.convert_to(dest_path)
        compound_dest_path = cls.convert_from(dest_path)

        # no conversion necessary
        if subgraph_src_path == compound_src_path and subgraph_dest_path == compound_dest_path:
            return src_path, dest_path

        # grab the actual nodes
        src_node = og.Controller.node(compound_src_path.GetPrimPath())
        dst_node = og.Controller.node(compound_dest_path.GetPrimPath())

        # A connection from Compound to Compound looks like the following
        # Cs/Cd -> the attribute path as part of the compound node
        # Ss/Sd -> the attribute path as part of the subgraph node (virtual node)

        # A) [Cs]                       B)         [Cd]
        #    [Ss] -> [Cd]                  [Cs] -> [Ss]
        #            [Sd]                  [Ss]
        #
        # The other cases are not when one isn't a compound. In that case Cs = Ss and/or Cs = Ss
        # C) [Cs/Ss] -> [Cd]    or    D)  [Cs]               or  E) [Cs/Ss] -> [Cd/Sd]
        #               [Sd]              [Ss]  -> [Cd/Sd]

        # Case E)
        if src_node.get_graph() == dst_node.get_graph():
            return src_path, dest_path

        # Case A) or C)
        if src_node.is_compound_node() and (src_node.get_compound_graph_instance() == dst_node.get_graph()):
            return subgraph_src_path, compound_dest_path

        # Case B) or D)
        return compound_src_path, subgraph_dest_path
