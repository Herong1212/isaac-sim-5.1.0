# pylint: disable=too-many-lines
# =============================================================================================================================
# This submodule is work-in-progress and subject to change without notice
#  _    _  _____ ______         _______  __     ______  _    _ _____     ______          ___   _   _____  _____  _____ _  __
# | |  | |/ ____|  ____|     /\|__   __| \ \   / / __ \| |  | |  __ \   / __ \ \        / / \ | | |  __ \|_   _|/ ____| |/ /
# | |  | | (___ | |__       /  \  | |     \ \_/ / |  | | |  | | |__) | | |  | \ \  /\  / /|  \| | | |__) | | | | (___ | ' /
# | |  | |\___ \|  __|     / /\ \ | |      \   /| |  | | |  | |  _  /  | |  | |\ \/  \/ / | . ` | |  _  /  | |  \___ \|  <
# | |__| |____) | |____   / ____ \| |       | | | |__| | |__| | | \ \  | |__| | \  /\  /  | |\  | | | \ \ _| |_ ____) | . \
#  \____/|_____/|______| /_/    \_\_|       |_|  \____/ \____/|_|  \_\  \____/   \/  \/   |_| \_| |_|  \_\_____|_____/|_|\_|

from typing import List, Optional, Set, Tuple, Union

import carb
import omni.graph.core as og
import omni.graph.tools.ogn as ogn
import omni.kit
import omni.kit.commands
import omni.usd
from pxr import Sdf

from ..commands.command_type_wrappers import CommandGraphWrapper
from ..commands.topology_commands import CreateNodeCommand, DeleteNodeCommand
from ..type_aliases import AttributeSpec_t, GraphSpec_t, NodeSpec_t

_DEFAULT_NODE_INSTANCE_NAME = "SubgraphNode"
_DEFAULT_SUBGRAPH_NAME = "Subgraph"
_COMPOUND_SUBGRAPH_NODE_TYPE = "omni.graph.nodes.CompoundSubgraph"
_ATTRIBUTE_INPUT_PREFIX = "inputs:"
_ATTRIBUTE_OUTPUT_PREFIX = "outputs:"
_ALT_ATTRIBUTE_OUTPUT_PREFIX = "outputs_"


# ------------------------------------------------------------------------------
def validate_attribute_for_promotion_from_compound_subgraph(attr_spec: AttributeSpec_t) -> Optional[str]:
    """Validates that an attribute can be promoted from a compound subgraph

    Args:
        attr_spec - The attribute to test.

    Returns:
        str - An error message with the reason it cannot be promoted, or None if it can be promoted.
    """
    try:
        attr = og.ObjectLookup.attribute(attr_spec)
    except og.OmniGraphError:
        return f"Attribute {attr_spec} is not a valid attribute"

    port_type = attr.get_port_type()
    if port_type not in (
        og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT,
        og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT,
    ):
        return "Only input and output attributes can be promoted"

    if attr.get_metadata(ogn.MetadataKeys.LITERAL_ONLY) == "1":
        return "Literal attributes cannot be promoted"

    return None


# ------------------------------------------------------------------------------
def validate_nodes_for_compound_subgraph(nodes: List[NodeSpec_t]) -> Optional[str]:
    """Validates that the set of nodes can be moved into a compound subgraph

    Args:
        nodes - a list of Nodes representing the node candidates for exporting to a subgraph

    Returns:
        Optional[str] - None if the nodes are valid, otherwise a string describing the error
    """
    node_path_set = set()
    graph = None
    for node_spec in nodes:
        try:
            node = og.ObjectLookup.node(node_spec)
        except og.OmniGraphError:
            return f"Node {node_spec} does not exist"

        graph = graph or node.get_graph()
        if graph != node.get_graph():
            return "Nodes must all belong to the same graph"

        node_path_set.add(node)

    return None


# -------------------------------------------------------------------------
def _get_nodes_parent_graph(nodes: List[Union[str, Sdf.Path]]) -> og.Graph:
    """
    Validates that the nodes, from Sdf.Paths, all belong to the same graph, and return the graph
    """
    if len(nodes) == 0:
        return None

    graph = None
    for node in nodes:
        node_obj = og.get_node_by_path(str(node))
        if not node_obj:
            raise og.OmniGraphError(f"{str(node)} is not an OmniGraphNode")
        graph = graph or node_obj.get_graph()
        if graph != node_obj.get_graph():
            raise og.OmniGraphError("Not all nodes belong to the same graph")

    return graph


# ------------------------------------------------------------------------------
def _get_fixed_relationship_data(relationship: Sdf.Path) -> List[Sdf.Path]:
    """
    Returns a list of Sdf.Paths that are connected to the relationship, stripping out
    target and bundle connections
    """
    stage = omni.usd.get_context().get_stage()
    rel = stage.GetRelationshipAtPath(relationship)
    if not rel:
        return []

    targets = rel.GetTargets()
    new_targets = []

    for target in targets:
        # target path
        if target.IsPropertyPath() and target.name.startswith(_ATTRIBUTE_OUTPUT_PREFIX):
            continue

        # bundle path
        if target.IsPropertyPath() and target.name.startswith(_ALT_ATTRIBUTE_OUTPUT_PREFIX):
            continue

        new_targets.append(target)

    return new_targets


# ------------------------------------------------------------------------------
def _set_relationship_data(attr: og.Attribute, data: List[Sdf.Path]):
    """Sets the data where the attribute is a relationship"""

    stage = omni.usd.get_context().get_stage()
    rel = stage.GetRelationshipAtPath(Sdf.Path(attr.get_path()))
    if rel:
        rel.SetTargets(data)


# ------------------------------------------------------------------------------
def _reload_top_level_graph(graph_id: GraphSpec_t) -> og.Graph:
    """
    Given a graph path, walks the hierarchy to the top level graph node and forces a reload from USD

    Returns:
        The reloaded graph
    """

    graph = og.Controller.graph(graph_id)
    if not graph:
        raise og.OmniGraphError(f"Graph {graph_id} does not exist")

    graph_path = graph.get_path_to_graph()

    # find the top level graph
    while graph.get_owning_compound_node():
        graph = graph.get_owning_compound_node().get_graph()

    graph.reload_from_stage()

    # once the graph is reloaded, the original may become invalid, so reload it from the given path
    return og.Controller.graph(graph_path)


# ------------------------------------------------------------------------------
def _copy_nodes_to_graph(nodes: List[Sdf.Path], graph: og.Graph):
    """
    Copies nodes to a subgraph, including links between nodes
    """
    if not nodes:
        return

    stage = omni.usd.get_context().get_stage()
    graph_path = graph.get_path_to_graph()
    new_node_paths = set()

    with Sdf.ChangeBlock():
        for node in nodes:
            old_graph_path = node.GetParentPath()
            old_node_path = node
            new_node_path = old_node_path.MakeRelativePath(old_graph_path).MakeAbsolutePath(graph_path)
            omni.kit.commands.execute(
                "CopyPrim", path_from=old_node_path, path_to=new_node_path, exclusive_select=False
            )
            new_node_paths.add(new_node_path)

    # remove existing connections and replace with new connections, if they exist
    with Sdf.ChangeBlock():
        for node_path in new_node_paths:
            prim = stage.GetPrimAtPath(node_path)
            for attr in prim.GetAttributes():
                name = str(attr.GetName())
                if name.startswith(_ATTRIBUTE_INPUT_PREFIX) or name.startswith(_ATTRIBUTE_OUTPUT_PREFIX):
                    attr.ClearConnections()
            for rel in prim.GetRelationships():
                name = str(rel.GetName())
                if (
                    name.startswith(_ATTRIBUTE_INPUT_PREFIX)
                    or name.startswith(_ATTRIBUTE_OUTPUT_PREFIX)
                    or name.startswith(_ALT_ATTRIBUTE_OUTPUT_PREFIX)
                ):
                    # Strip out any targets that are connections to other targets or bundles
                    rel.SetTargets(_get_fixed_relationship_data(rel.GetPath()))

    # reload the parent graph so the subgraph nodes get created
    _reload_top_level_graph(nodes[0].GetParentPath())

    # reattach the connections
    with Sdf.ChangeBlock():
        # walk the old node list, and create inter connections where needed
        for node in nodes:
            old_graph_path = node.GetParentPath()
            old_node_path = node
            new_node_path = old_node_path.MakeRelativePath(old_graph_path).MakeAbsolutePath(graph_path)

            for attr in og.Controller.node(node).get_attributes():
                port_type = attr.get_port_type()
                if port_type in [
                    og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT,
                    og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT,
                ]:
                    for con_info in attr.get_upstream_connections_info():
                        (up, con_type) = (con_info.attr, con_info.connection_type)
                        up_path = Sdf.Path(up.get_path()).MakeRelativePath(old_graph_path).MakeAbsolutePath(graph_path)
                        up_node = up_path.GetPrimPath()

                        # Either it's connected to the new node, or connected to something in the nodes subgraph
                        if up_node in new_node_paths or up_node.HasPrefix(new_node_path):
                            output_path = up_path
                            input_path = (
                                Sdf.Path(attr.get_path()).MakeRelativePath(old_graph_path).MakeAbsolutePath(graph_path)
                            )
                            og.cmds.ConnectAttrs(
                                src_attr=str(output_path),
                                dest_attr=str(input_path),
                                modify_usd=True,
                                connection_type=con_type,
                            )


# -------------------------------------------------------------------------
def _exposed_inputs(attr: og.Attribute, node_path_set: Set[Sdf.Path]) -> Optional[Tuple[List[Sdf.Path], Sdf.Path]]:
    """Given an input, returns a tuple containing a list of connections and the port
    If the port is not to be exposed, returns None
    """

    port_type = attr.get_port_type()
    if port_type != og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT:
        return None

    if validate_attribute_for_promotion_from_compound_subgraph(attr):
        return None

    if attr.get_metadata(ogn.MetadataKeys.OUTPUT_ONLY) == "1":
        return None

    # ignore execution pins if the graph is not an execution graph, unless connected
    if (
        attr.get_resolved_type().role == og.AttributeRole.EXECUTION
        and attr.get_node().get_graph().get_evaluator_name() != "execution"
        and attr.get_upstream_connection_count() == 0
    ):
        return None

    inputs = []
    dest_path = Sdf.Path(attr.get_path())
    for up in attr.get_upstream_connections():
        src_path = Sdf.Path(up.get_path())
        # use the node to get the prim path or bundles will return an incorrect attribute
        src_prim_path = Sdf.Path(up.get_node().get_prim_path())
        if src_prim_path not in node_path_set:
            inputs.append(src_path)

    # If the input is unconnected run through special cases
    if attr.get_upstream_connection_count() == 0:
        # the type is unresolved, in which case we should exposed it as a attribute.
        if (not attr.is_optional_for_compute) and (attr.get_resolved_type() == og.Type(og.BaseDataType.UNKNOWN)):
            inputs.append(Sdf.Path())
        # special case for unconnected execution types
        if attr.get_resolved_type().role == og.AttributeRole.EXECUTION:
            inputs.append(Sdf.Path())

    if len(inputs) == 0:
        return None

    return (inputs, dest_path)


# -------------------------------------------------------------------------
def _exposed_outputs(
    attr: og.Attribute, node_path_set: Set[Sdf.Path], has_downstream_nodes: bool
) -> Tuple[Sdf.Path, List[Sdf.Path]]:
    """Given an output, returns a tuple of the output and connections, or None if the output should not be exposed"""
    port_type = attr.get_port_type()
    is_output_port = port_type == og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT
    is_output_port |= (
        port_type == og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT
        and attr.get_metadata(ogn.MetadataKeys.OUTPUT_ONLY) == "1"
    )
    if not is_output_port:
        return None

    # ignore attributes that are not valid for promotion
    if validate_attribute_for_promotion_from_compound_subgraph(attr):
        return None

    # ignore execution pins if the graph is not an execution graph, unless it is connected
    if (
        attr.get_resolved_type().role == og.AttributeRole.EXECUTION
        and attr.get_node().get_graph().get_evaluator_name() != "execution"
        and attr.get_downstream_connection_count() == 0
    ):
        return None

    outputs = []
    src_path = Sdf.Path(attr.get_path())

    for down in attr.get_downstream_connections():
        dest_path = Sdf.Path(down.get_path())
        if dest_path.GetPrimPath() not in node_path_set:
            outputs.append(dest_path)

    # If the node has outputs, but none are connected, expose the output
    if attr.get_downstream_connection_count() == 0 and not has_downstream_nodes:
        outputs.append(Sdf.Path())

    if len(outputs) == 0:
        return None

    return (src_path, outputs)


# -------------------------------------------------------------------------
def _find_connections(
    nodes: List[og.Node],
) -> Tuple[List[Tuple[List[Sdf.Path], Sdf.Path]], List[Tuple[Sdf.Path, List[Sdf.Path]]]]:
    """Finds the input and output connections from a subset of nodes that are connected externally to the list"""

    node_path_set = {Sdf.Path(node.get_prim_path()) for node in nodes}
    inputs = []
    outputs = []

    for node in nodes:  # noqa: PLR1702
        has_downstream_nodes = any(a.get_downstream_connection_count() > 0 for a in node.get_attributes())
        for attr in node.get_attributes():
            input_tuple = _exposed_inputs(attr, node_path_set)
            if input_tuple:
                inputs.append(input_tuple)
            output_tuple = _exposed_outputs(attr, node_path_set, has_downstream_nodes)
            if output_tuple:
                outputs.append(output_tuple)

    return (inputs, outputs)


# -------------------------------------------------------------------------------------------------------------
def _make_unique(name: str, names: Set[str]) -> str:
    """Given a name, returns a unique name, using the provided set to find duplicates"""
    orig_name = name
    count = 0
    while name in names:
        count = count + 1
        name = f"{orig_name}_{count:02d}"
    names.add(name)
    return name


# -------------------------------------------------------------------------------------------------------------
def _get_attribute_type(attr: og.Attribute) -> og.Type:
    """Helper to retreive the attribute type for use with create_attribute"""
    if attr.get_extended_type() == og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_REGULAR:
        return attr.get_resolved_type()
    return og.AttributeType.type_from_sdf_type_name(attr.get_type_name())


# -------------------------------------------------------------------------------------------------------------
def _get_connections(attribute: og.Attribute) -> Tuple[List[str], List[str]]:

    if not attribute.is_valid():
        return ([], [])

    upstream = attribute.get_upstream_connections()
    downstream = attribute.get_downstream_connections()
    upstream = [og.ObjectLookup.attribute_path(a) for a in upstream]
    downstream = [og.ObjectLookup.attribute_path(a) for a in downstream]
    return (upstream, downstream)


# -------------------------------------------------------------------------
def _disconnect_and_remove_attribute(node: og.Node, attribute_name: str) -> bool:
    """Disconnects and removes an attribute from a node"""
    attr = og.ObjectLookup.attribute((attribute_name, node))
    upstream_connections = attr.get_upstream_connections()
    downstream_connections = attr.get_downstream_connections()
    for up in upstream_connections:
        og.cmds.imm.DisconnectAttrs(src_attr=up, dest_attr=attr, modify_usd=True)
    for down in downstream_connections:
        og.cmds.imm.DisconnectAttrs(src_attr=attr, dest_attr=down, modify_usd=True)
    return node.remove_attribute(attribute_name)


# -------------------------------------------------------------------------
def _strip_prefix(attribute_name: str):
    """Helper function to strip the input/output prefixes from an attribute name"""
    ret = (
        attribute_name.removeprefix(f"{_ATTRIBUTE_OUTPUT_PREFIX}")
        .removeprefix(f"{_ATTRIBUTE_INPUT_PREFIX}")
        .removeprefix(f"{_ALT_ATTRIBUTE_OUTPUT_PREFIX}")
    )
    return ret


# -------------------------------------------------------------------------
def _get_attribute_prefix(attr: og.Attribute) -> str:
    """Helper function to get the prefix of an attribute for its port type"""
    if attr.get_resolved_type().role == og.AttributeRole.BUNDLE:
        return (
            _ATTRIBUTE_INPUT_PREFIX
            if attr.get_port_type() == og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT
            else _ALT_ATTRIBUTE_OUTPUT_PREFIX
        )

    return (
        _ATTRIBUTE_INPUT_PREFIX
        if attr.get_port_type() == og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT
        else _ATTRIBUTE_OUTPUT_PREFIX
    )


# -------------------------------------------------------------------------
def _rename_attribute(
    compound_node: og.Node, attr: og.Attribute, new_name: str, connections: Tuple[List[str], List[str]]
):
    """
    Renames the attribute on the node with new name.
    new_name is the new attribute name without prefix
    connections is a tuple with a list of upstream and downstream connections
    """
    name = attr.get_name()

    # create attribute with new name
    compound_node.create_attribute(
        attributeName=new_name,
        attributeType=_get_attribute_type(attr),
        portType=attr.get_port_type(),
        extendedType=attr.get_extended_type(),
        unionTypes=",".join(attr.get_union_types() or []),
    )

    new_attr = compound_node.get_attribute(f"{_get_attribute_prefix(attr)}{new_name}")

    # rewire to the new attribute
    for up in connections[0]:
        og.cmds.imm.DisconnectAttrs(src_attr=og.ObjectLookup.attribute(up), dest_attr=attr, modify_usd=True)
        og.cmds.imm.ConnectAttrs(src_attr=up, dest_attr=new_attr, modify_usd=True)
    for down in connections[1]:
        og.cmds.imm.DisconnectAttrs(src_attr=attr, dest_attr=og.ObjectLookup.attribute(down), modify_usd=True)
        og.cmds.imm.ConnectAttrs(src_attr=new_attr, dest_attr=down, modify_usd=True)

    # delete the old attribute
    return compound_node.remove_attribute(name)


# -----------------------------------------------------------------------------
def _attribute_in_subgraph(node: og.Node, attr: og.Attribute) -> bool:
    """Returns whether an attribute is in the subgraph of a node"""
    return node.get_compound_graph_instance() == attr.get_node().get_graph()


# -----------------------------------------------------------------------------
def _get_resolved_value(attr: og.Attribute):
    """Returns the resolved value of an attribute, or None if it is a relationship"""

    # for relationships return the data that does not refer to a connection
    if attr.get_resolved_type().base_type == og.BaseDataType.RELATIONSHIP:
        return _get_fixed_relationship_data(Sdf.Path(attr.get_path()))

    # regular type
    if attr.get_extended_type() == og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_REGULAR:
        return og.DataView.get(attr)

    if attr.get_resolved_type().base_type != og.BaseDataType.UNKNOWN:
        return og.DataView.get(attr)

    return None


# ------------------------------------------------------------------------------
class CreateCompoundSubgraphCommand(omni.kit.commands.Command):
    """
    Creates a new compound subgraph on a graph and attaches it to a Compound Node Instance

    Args:
        graph: The graph to create the node on
        node_name: The name of the Compound Node instances, or None to use the default name
        subgraph_name: The name of the subgraph to be generated, or None to use the default

    Returns:
        og.Node: The newly created node, or None if the command fails

    Raises:
        omni.graph.core.OmniGraphError: If the node creation fails in immediate mode
    """

    # -------------------------------------------------------------------------
    def __init__(self, graph, node_name: Optional[str] = None, subgraph_name: Optional[str] = None):
        self._graph = CommandGraphWrapper(graph)
        self._node_name = node_name or _DEFAULT_NODE_INSTANCE_NAME
        self._subgraph_name = subgraph_name or _DEFAULT_SUBGRAPH_NAME
        self._node_path = None

    # -------------------------------------------------------------------------
    @staticmethod
    def do_immediate(graph: og.Graph, node_path: str, subgraph_name: str):

        # create the compound node, which will create a default graph object
        node = CreateNodeCommand.do_immediate(graph, node_path, _COMPOUND_SUBGRAPH_NODE_TYPE, True)

        # moves the created subgraph if necessary
        if subgraph_name != _DEFAULT_SUBGRAPH_NAME:
            RenameCompoundSubgraphCommand.do_immediate(
                f"{node_path}/{_DEFAULT_SUBGRAPH_NAME}", f"{node_path}/{subgraph_name}"
            )

        return node

    # --------------------------------------------------------------------------
    def do(self):
        node = None
        self._node_path = None
        try:
            node = CreateCompoundSubgraphCommand.do_immediate(
                self._graph.object, f"{self._graph.object.get_path_to_graph()}/{self._node_name}", self._subgraph_name
            )
            self._node_path = node.get_prim_path()

        except og.OmniGraphError as error:
            carb.log_warn(f"Creation of {self._node_path} failed with {error}")
            self._node_path = None

        return node

    # --------------------------------------------------------------------------
    def undo(self):
        if self._node_path:
            DeleteNodeCommand.do_immediate(self._graph.object, self._node_path, True)
            self._node_path = None


# -----------------------------------------------------------------------------
class CreateCompoundSubgraphInputCommand(omni.kit.commands.Command):
    """
    Creates a new input on a Subgraph Compound Node.
    Arg:
        compound_node: The compound node that represents the subgraph container
        input_name: The name of the input, without a namespace prefix
        connect_to: The attribute to connect the input to. This cannot be None, and must
        exist on the subgraph of the compound_node
    Returns:
        (og.Attribute) The created attribute, or None if a failure occurs

    Raises:
        omni.graph.core.OmniGraphError: If the attribute cannot be created in immediate mode.


    """

    def __init__(self, compound_node: NodeSpec_t, input_name: str, connect_to: AttributeSpec_t):
        self._compound_node_path = og.ObjectLookup.node_path(compound_node)
        self._input_name = input_name
        self._connection = og.ObjectLookup.attribute_path(connect_to)
        self._applied = False

    @staticmethod
    def do_immediate(compound_node: NodeSpec_t, input_name: str, connect_to: AttributeSpec_t) -> og.Attribute:

        # these calls will raise if not valid
        compound_node = og.ObjectLookup.node(compound_node)
        connect_to = og.ObjectLookup.attribute(connect_to)
        input_name = input_name.removeprefix(_ATTRIBUTE_INPUT_PREFIX)

        error_str = validate_attribute_for_promotion_from_compound_subgraph(connect_to)
        if error_str:
            raise og.OmniGraphError(error_str)

        if connect_to.get_port_type() != og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT:
            raise og.OmniGraphError(f"{connect_to.get_path()} is not an input port")

        if compound_node.get_attribute_exists(f"{_ATTRIBUTE_INPUT_PREFIX}{input_name}"):
            raise og.OmniGraphError(f"{compound_node.get_prim_path()} already has a connection named {input_name}")

        if connect_to.get_upstream_connection_count() != 0:
            allow_multi_input = (
                connect_to.get_metadata(ogn.MetadataKeys.ALLOW_MULTI_INPUTS) == "1"
                or connect_to.get_resolved_type().role == og.AttributeRole.EXECUTION
            )
            if not allow_multi_input:
                raise og.OmniGraphError(
                    f"{connect_to.get_path()} is already connected to {connect_to.get_upstream_connections()[0].get_path()}."
                )

        if not compound_node.is_compound_node():
            raise og.OmniGraphError(f"{compound_node.get_prim_path()} is not a Compound Node")

        if not _attribute_in_subgraph(compound_node, connect_to):
            raise og.OmniGraphError(
                f"{compound_node.get_prim_path()} can only connect to a node in its compound graph instance"
            )

        created = compound_node.create_attribute(
            attributeName=input_name,
            attributeType=_get_attribute_type(connect_to),
            portType=og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT,
            extendedType=connect_to.get_extended_type(),
            unionTypes=",".join(connect_to.get_union_types() or []),
        )

        if not created:
            raise og.OmniGraphError(f"Could not create attribute {input_name} on {compound_node.get_prim_path()}")

        attr = og.ObjectLookup.attribute((f"{_ATTRIBUTE_INPUT_PREFIX}{input_name}", compound_node))

        # prior to connecting, if the connected attribute has a USD value, that needs to be set on the new attribute
        attr_value = _get_resolved_value(connect_to)
        if attr_value is not None:
            # if the connect attribute was manually resolved
            if attr.get_extended_type() != og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_REGULAR:
                attr.set_resolved_type(connect_to.get_resolved_type())

            if attr.get_resolved_type().base_type == og.BaseDataType.RELATIONSHIP:
                _set_relationship_data(attr, attr_value)
            else:
                og.Controller.set(attr, attr_value, update_usd=True)

        # connect the attribute
        og.cmds.imm.ConnectAttrs(
            src_attr=attr,
            dest_attr=connect_to,
            modify_usd=True,
        )

        return attr

    def do(self):
        self._applied = False
        attribute_created = None
        try:
            attribute_created = self.do_immediate(self._compound_node_path, self._input_name, self._connection)
            self._applied = True
        except og.OmniGraphError as error:
            carb.log_warn(
                f"Creation of subgraph compound input {self._input_name} on {self._compound_node_path} failed with {error}"
            )
            attribute_created = None
        return attribute_created

    def undo(self):
        if self._applied:
            node = og.ObjectLookup.node(self._compound_node_path)
            _disconnect_and_remove_attribute(node, f"{_ATTRIBUTE_INPUT_PREFIX}{self._input_name}")
            self._applied = False


# -----------------------------------------------------------------------------
class CreateCompoundSubgraphOutputCommand(omni.kit.commands.Command):
    """
    Creates a new output on a Subgraph Compound Node.
    Arg:
        compound_node: The compound node that represents the subgraph container
        output_name: The name of the output without a namespace prefix
        connect_from: The attribute to connect the output from. This cannot be None, and must
        exist on the subgraph of the compound_node
    Returns:
        (og.Attribute) The created attribute, or None if a failure occurs

    Raises:
        omni.graph.core.OmniGraphError: If the attribute cannot be created in immediate mode.

    """

    def __init__(self, compound_node: NodeSpec_t, output_name: str, connect_from: AttributeSpec_t):
        self._compound_node_path = og.ObjectLookup.node_path(compound_node)
        self._output_name = output_name
        self._connection = og.ObjectLookup.attribute_path(connect_from)
        self._applied = False

    @staticmethod
    def do_immediate(compound_node: NodeSpec_t, output_name: str, connect_from: AttributeSpec_t) -> og.Attribute:

        # these calls will raise if not valid
        compound_node = og.ObjectLookup.node(compound_node)
        connect_from = og.ObjectLookup.attribute(connect_from)
        prefix_name = _ATTRIBUTE_OUTPUT_PREFIX
        if connect_from.is_valid() and connect_from.get_resolved_type().role == og.AttributeRole.BUNDLE:
            prefix_name = _ALT_ATTRIBUTE_OUTPUT_PREFIX
        output_name = output_name.removeprefix(prefix_name)

        error_str = validate_attribute_for_promotion_from_compound_subgraph(connect_from)
        if error_str:
            raise og.OmniGraphError(error_str)

        # outputs can be connected to inputs or outputs
        if (
            connect_from.get_port_type() != og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT
            and connect_from.get_port_type() != og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT
        ):
            raise og.OmniGraphError(f"{connect_from.get_path()} is not an input port")

        if not compound_node.is_compound_node():
            raise og.OmniGraphError(f"{compound_node.get_prim_path()} is not a Compound Node")

        if compound_node.get_attribute_exists(f"{prefix_name}{output_name}"):
            raise og.OmniGraphError(f"{compound_node.get_prim_path()} already has a connection named {output_name}")

        if not _attribute_in_subgraph(compound_node, connect_from):
            raise og.OmniGraphError(
                f"{compound_node.get_prim_path()} can only connect to a node in its compound graph instance"
            )

        created = compound_node.create_attribute(
            attributeName=output_name,
            attributeType=_get_attribute_type(connect_from),
            portType=og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT,
            extendedType=connect_from.get_extended_type(),
            unionTypes=",".join(connect_from.get_union_types() or []),
        )

        if not created:
            raise og.OmniGraphError(f"Could not create attribute {output_name} on {compound_node.get_prim_path()}")

        dest_attr = compound_node.get_attribute(f"{prefix_name}{output_name}")

        # connect the attribute
        og.cmds.imm.ConnectAttrs(
            src_attr=connect_from,
            dest_attr=dest_attr,
            modify_usd=True,
        )

        return dest_attr

    def do(self):
        self._applied = False
        attribute_created = None
        try:
            attribute_created = self.do_immediate(self._compound_node_path, self._output_name, self._connection)
            self._applied = True
        except og.OmniGraphError as error:
            carb.log_warn(
                f"Creation of subgraph compound output {self._output_name} on {self._compound_node_path} failed with {error}"
            )
            attribute_created = None
        return attribute_created

    def undo(self):
        if self._applied:
            node = og.ObjectLookup.node(self._compound_node_path)
            _disconnect_and_remove_attribute(node, f"{_ATTRIBUTE_OUTPUT_PREFIX}{self._output_name}")
            self._applied = False


# -----------------------------------------------------------------------------
class RemoveCompoundSubgraphAttributeCommand(omni.kit.commands.Command):
    """Command that removes an input or output attribute from a Subgraph Compound Node

        Args:
        attribute: The attribute to remove.

    Return:
        (bool) : True if the attribute was successfully removed

    Raises:
        omni.graph.core.OmniGraphError: If the attribute cannot be created in immediate mode.
    """

    def __init__(self, attribute: AttributeSpec_t):
        self._attribute_path = og.ObjectLookup.attribute_path(attribute)
        self._upstream_connections = []
        self._downstream_connections = []
        self._applied = False
        self._attribute_kwargs = {}
        self._node_path = None
        self._attribute_name_with_namespace = None

    @staticmethod
    def do_immediate(attribute: AttributeSpec_t):
        attribute = og.ObjectLookup.attribute(attribute)
        node = attribute.get_node()

        if not node.is_compound_node():
            raise og.OmniGraphError(f"{node.get_prim_path()} is not a Compound Node")

        if not _disconnect_and_remove_attribute(node, attribute.get_name()):
            raise og.OmniGraphError(f"Attribute removal failed for {attribute.get_name()}")

    def do(self):
        self._applied = False
        try:
            attr = og.ObjectLookup.attribute(self._attribute_path)
            self._node_path = og.ObjectLookup.node_path(attr.get_node())
            self._attribute_name_with_namespace = attr.get_name()
            name_no_prefix = _strip_prefix(attr.get_name())

            self._attribute_kwargs = {
                "attributeName": name_no_prefix,
                "portType": attr.get_port_type(),
                "attributeType": _get_attribute_type(attr),
                "extendedType": attr.get_extended_type(),
                "unionTypes": ",".join(attr.get_union_types() or []),
            }
            (self._upstream_connections, self._downstream_connections) = _get_connections(attr)
            self.do_immediate(attribute=self._attribute_path)
            self._applied = True
        except og.OmniGraphError as error:
            carb.log_warn(f"Removal of attribute {self._attribute_path} failed with {error}")

        return self._applied

    def undo(self):
        if self._applied:
            node = og.ObjectLookup.node(self._node_path)
            node.create_attribute(**self._attribute_kwargs)
            attr = node.get_attribute(self._attribute_name_with_namespace)
            # reconnect the previous connections
            for upstream in self._upstream_connections:
                og.cmds.imm.ConnectAttrs(src_attr=upstream, dest_attr=attr, modify_usd=True)
            for downstream in self._downstream_connections:
                og.cmds.imm.ConnectAttrs(src_attr=attr, dest_attr=downstream, modify_usd=True)
            self._applied = False


# -----------------------------------------------------------------------------
class RenameCompoundSubgraphAttributeCommand(omni.kit.commands.Command):
    """
    Command that renames a compound subgraph input/output port and preserves existing connections.

    Args:
        attribute: The input/output port to rename
        new_name: The new name for the input/output port without a prefix

    Returns:
        attribute (og.Attribute): The new input/output port attribute or None if the rename failed

    Raises:
        og.OmniGraphError: If the rename fails in immediate mode.
    """

    def __init__(self, attribute: AttributeSpec_t, new_name: str):
        self._attribute_path = og.ObjectLookup.attribute_path(attribute)
        self._new_name = _strip_prefix(new_name)
        self._attribute_name_no_prefix = None
        self._prefix = None
        self._node_path = None
        self._connections = None
        self._applied = False

    @staticmethod
    def do_immediate(attribute: AttributeSpec_t, new_name: str, connections: Tuple[List[str], List[str]]):
        attribute = og.ObjectLookup.attribute(attribute)
        node = attribute.get_node()
        prefix = _get_attribute_prefix(attribute)

        # these calls will raise if not valid
        if not node.is_compound_node():
            raise og.OmniGraphError(f"{node.get_prim_path()} is not a Compound Node")

        if node.get_attribute_exists(f"{prefix}{new_name}"):
            raise og.OmniGraphError(f"{node.get_prim_path()} already has a port named {new_name}")

        if not _rename_attribute(node, attribute, new_name, connections):
            raise og.OmniGraphError(f"Attribute rename failed for {attribute.get_name()} to {new_name}")

        return og.ObjectLookup.attribute(f"{prefix}{new_name}", node)

    def do(self):
        self._applied = False
        new_attr = None

        # If anything fails here, we want to raise so that undo will be called properly
        attr = og.ObjectLookup.attribute(self._attribute_path)
        self._prefix = _get_attribute_prefix(attr)
        self._attribute_name_no_prefix = _strip_prefix(attr.get_name())
        self._node_path = og.ObjectLookup.node_path(attr.get_node())
        self._connections = _get_connections(attr)

        self.do_immediate(self._attribute_path, self._new_name, self._connections)

        new_attr = og.ObjectLookup.attribute(f"{self._node_path}.{self._prefix}{self._new_name}")
        self._applied = True

        return new_attr

    def undo(self):
        # Restore the old attr and its connections
        if self._applied:
            node = og.ObjectLookup.node(self._node_path)
            new_attr = node.get_attribute(f"{self._prefix}{self._new_name}")
            self._applied = not _rename_attribute(
                node, new_attr, f"{self._attribute_name_no_prefix}", self._connections
            )


# -----------------------------------------------------------------------------
class ReplaceWithCompoundSubgraphCommand(omni.kit.commands.Command):
    """
    Command that replaces a set of nodes in a graph with a new compound subgraph and compound node

    Args:
        nodes: A list of nodes (Sdf.Path, og.Node, str) to nodes that will be moved into the subgraph.
        compound_name: The name of the compound node instance to create.
        graph_name: The name of the compound subgraph to create.

    Returns:
        node (og.Node): The compound node, or None if the command fails

    Raises:
        og.OmniGraphError: If the node creation fails in immediate mode.
    """

    # -------------------------------------------------------------------------
    def __init__(
        self,
        nodes: List[NodeSpec_t],
        compound_name: str = "compound",
        graph_name: str = "Subgraph",
    ):
        self._nodes = nodes
        self._node_type = None
        self._compound_name = compound_name
        self._graph_name = graph_name
        self._applied = False
        self._compound_node_path = None

    # -------------------------------------------------------------------------
    @staticmethod
    def do_immediate(nodes: List[NodeSpec_t], compound_name: str, subgraph_name: str):

        # make sure the nodes are all Sdf.Paths
        nodes = [Sdf.Path(og.ObjectLookup.node_path(node)) for node in nodes]

        # apply special validation rules
        error_string = validate_nodes_for_compound_subgraph(nodes)
        if error_string:
            raise og.OmniGraphError(error_string)

        # get the parent graph
        graph = _get_nodes_parent_graph(nodes)
        if not graph:
            raise og.OmniGraphError("Node list is empty")
        graph_path = graph.get_path_to_graph()

        # make sure the name is unique
        graph_nodes = {str(Sdf.Path(node.get_prim_path()).GetPrimPath().name) for node in graph.get_nodes()}
        compound_name = _make_unique(compound_name, graph_nodes)

        # create the compound node
        (success, node) = omni.kit.commands.execute(
            "CreateCompoundSubgraph", graph=graph, node_name=compound_name, subgraph_name=subgraph_name
        )

        if not success or node is None:
            raise og.OmniGraphError("Could not create a compound subgraph")

        # get the subgraph
        subgraph = og.get_graph_by_path(f"{node.get_prim_path()}/{subgraph_name}")

        # get the existing nodes
        og_nodes = [og.get_node_by_path(str(path)) for path in nodes]

        # store the existing connections to the nodes on the graph
        (input_connections, output_connections) = _find_connections(og_nodes)

        # copy the nodes to the subgraph graph
        _copy_nodes_to_graph(nodes, subgraph)

        # refresh the OG objects - _copy_nodes reloads the graph
        graph = og.Controller.graph(graph_path)
        node = og.Controller.node(f"{graph.get_path_to_graph()}/{compound_name}")
        subgraph = og.get_graph_by_path(f"{node.get_prim_path()}/{subgraph_name}")

        # create the inputs and outputs
        input_names = set()
        input_tuples = [
            (src, dst, _make_unique(_strip_prefix(dst.name), input_names)) for (src, dst) in input_connections
        ]
        for _, dst, port_name in input_tuples:
            dst_port = f"{node.get_prim_path()}/{subgraph_name}/{dst.GetPrimPath().name}.{dst.name}"
            CreateCompoundSubgraphInputCommand.do_immediate(
                compound_node=node, input_name=port_name, connect_to=dst_port
            )

        output_names = set()
        output_tuples = [
            (src, dst, _make_unique(_strip_prefix(src.name), output_names)) for (src, dst) in output_connections
        ]
        for src, _, port_name in output_tuples:
            src_port = f"{node.get_prim_path()}/{subgraph_name}/{src.GetPrimPath().name}.{src.name}"
            CreateCompoundSubgraphOutputCommand.do_immediate(
                compound_node=node, output_name=port_name, connect_from=src_port
            )

        # delete the previous nodes
        for node_path in nodes:
            og.cmds.DeleteNode(graph=graph, node_path=str(node_path), modify_usd=True)

        # now connect the to the newly created nodes
        for src_list, _, port_name in input_tuples:
            # the intermediate port
            inter_port = f"{node.get_prim_path()}.{_ATTRIBUTE_INPUT_PREFIX}{port_name}"

            # connect the inputs
            for src in src_list:
                # src to intermediate, if it's valid
                if src != Sdf.Path():
                    og.cmds.ConnectAttrs(
                        src_attr=str(src),
                        dest_attr=str(inter_port),
                        modify_usd=True,
                    )

        # connect the new outputs
        for _, dst_list, port_name in output_tuples:
            inter_port = f"{node.get_prim_path()}.{_ATTRIBUTE_OUTPUT_PREFIX}{port_name}"

            # adjust for bundles where the 'outputs_' prefix is used instead of 'outputs:'
            try:
                og.Controller.attribute(inter_port)
            except og.OmniGraphError:
                inter_port = f"{node.get_prim_path()}.{_ALT_ATTRIBUTE_OUTPUT_PREFIX}{port_name}"

            # intermediate to dest
            for dst in dst_list:
                if dst != Sdf.Path():
                    og.cmds.ConnectAttrs(
                        src_attr=str(inter_port),
                        dest_attr=str(dst),
                        modify_usd=True,
                    )

        # reload the graph again to process the new connections
        graph = _reload_top_level_graph(graph)

        return og.Controller.node(f"{graph.get_path_to_graph()}/{compound_name}")

    # -------------------------------------------------------------------------
    def do(self):
        """
        Applies the command.

        Returns the path to the new compound node, or an empty path if an error occurs
        """

        if self._compound_node_path:
            return og.get_node_by_path(self._compound_node_path)

        node = None
        self._compound_node_path = None
        try:
            with omni.kit.undo.group():
                node = ReplaceWithCompoundSubgraphCommand.do_immediate(
                    self._nodes, self._compound_name, self._graph_name
                )
            self._compound_node_path = node.get_prim_path()
        except og.OmniGraphError as error:
            carb.log_warn(f"Creation of compound {self._compound_name} failed with {error}")
            self._compound_node_path = None
            node = None
            # This needs to re-raise, or if the command fails in editor it isn't completely undone with undo
            raise error

        return node

    # ---------------------------------------------------------------------------
    def undo(self):
        if self._compound_node_path:
            self._compound_node_path = None


# ------------------------------------------------------------------------------
class RenameCompoundSubgraphCommand(omni.kit.commands.Command):
    """
    Command that performs a rename on existing compound subgraphs. This is an explcit command as Subgraphs are typically
    not able to be deleted.

    Note that changes to omnigraph from this command are deferred. The USD will change immediately,
    but omnigraph changes may not be applied until the next frame.

    Args:
        subgraph (GraphSpec_t): The subgraph, specified by graph or path, to rename
        new_name (str): The new name of the subgraph. Note that the new path must be still be a child of the
        compound node

    Returns:
        The path of the new subgraph. None is returned in immediate mode on failure.

    Raises:
        og.OmniGraphError if the rename fails
    """

    # -------------------------------------------------------------------------
    def __init__(self, subgraph: GraphSpec_t, new_path: Union[str, Sdf.Path]):
        self._subgraph = subgraph
        self._new_path = new_path
        self._old_path = None

    # -------------------------------------------------------------------------
    @staticmethod
    def do_immediate(subgraph: GraphSpec_t, new_path: Union[str, Sdf.Path]):
        """Applies the command without undo"""
        graph = og.Controller.graph(subgraph)
        if not graph or not graph.is_valid() or not graph.is_compound_graph():
            return None

        new_path = str(new_path)
        path = graph.get_path_to_graph()
        prim = omni.usd.get_context().get_stage().GetPrimAtPath(path)
        if not prim:
            return None

        if Sdf.Path(new_path).GetParentPath() != Sdf.Path(path).GetParentPath():
            carb.log_warn(f"RenameCompoundSubgraphCommand: '{new_path}' must remain a child of the compound node")
            return None

        metadata = prim.GetMetadata("no_delete")
        prim.SetMetadata("no_delete", False)
        # don't use execute or it will try to apply two move undos
        omni.kit.commands.create("MovePrim", path_from=path, path_to=new_path).do()
        new_prim = omni.usd.get_context().get_stage().GetPrimAtPath(new_path)
        if not new_prim:
            if prim:
                prim.SetMetadata("no_delete", metadata)
            return None

        new_prim.SetMetadata("no_delete", metadata)
        return str(new_prim.GetPath())

    # -------------------------------------------------------------------------
    def do(self):
        """Overrides the do operation and performs graph renaming"""
        self._old_path = og.Controller.prim_path(self._subgraph)
        new_prim = RenameCompoundSubgraphCommand.do_immediate(self._subgraph, self._new_path)
        if not new_prim:
            self._old_path = None
            raise og.OmniGraphError(f"Failed to rename subgraph {self._subgraph} to self._new_path")

        return new_prim

    # -------------------------------------------------------------------------
    def undo(self):
        """Applies the undo operation. Reverts the graph to its previous path."""
        if self._old_path:
            RenameCompoundSubgraphCommand.do_immediate(self._new_path, self._old_path)
            self._old_path = None


# -----------------------------------------------------------------------------
class PromoteUnconnectedToCompoundSubgraphCommand(omni.kit.commands.Command):
    """
    Command that promotes unconnected inputs/outputs on a node to its compound subgraph

    Args:
        node: The node (Sdf.Path, og.Node, str) whose unconnected inputs/outputs will be promoted
        inputs: If unconnected inputs should be promoted
        outputs: If unconnected outputs should be promoted

    Returns:
        List[og.Attribute]: The attributes created on the compound subgraph

    Raises:
        og.OmniGraphError: If attribute promotion fails in immediate mode.
    """

    # -------------------------------------------------------------------------
    def __init__(self, node: NodeSpec_t, inputs: bool, outputs: bool):
        self._node = node
        self._inputs = inputs
        self._outputs = outputs
        self._ports = None
        self._applied = False

    # -------------------------------------------------------------------------
    @staticmethod
    def do_immediate(node: NodeSpec_t, inputs: bool, outputs: bool):

        node = og.ObjectLookup.node(node)

        # get the owning compound and existing inputs/outputs
        owning_compound = node.get_graph().get_owning_compound_node()
        if not owning_compound:
            raise og.OmniGraphError("Node not in a compound")

        # output-only inputs should be promoted as outputs
        def is_output(port_type, attr):
            return port_type == og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT or (
                port_type == og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT
                and attr.get_metadata(ogn.MetadataKeys.OUTPUT_ONLY) == "1"
            )

        input_names = set()
        output_names = set()
        for attr in owning_compound.get_attributes():
            port_type = attr.get_port_type()
            if inputs and port_type == og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT:
                input_names.add(_strip_prefix(attr.get_name()))
            elif outputs and port_type == og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT:
                output_names.add(_strip_prefix(attr.get_name()))

        # Find all unconnected inputs/outputs
        inputs_to_promote = []
        outputs_to_promote = []
        for attr in node.get_attributes():
            port_type = attr.get_port_type()
            if (
                port_type == og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT
                and inputs
                and attr.get_upstream_connection_count() == 0
                and validate_attribute_for_promotion_from_compound_subgraph(attr) is None
            ):
                inputs_to_promote.append(attr)
            elif (
                is_output(port_type, attr)
                and outputs
                and attr.get_downstream_connection_count() == 0
                and validate_attribute_for_promotion_from_compound_subgraph(attr) is None
            ):
                outputs_to_promote.append(attr)

        ports = []
        for i in inputs_to_promote:
            port_name = _make_unique(_strip_prefix(i.get_name()), input_names)
            port = CreateCompoundSubgraphInputCommand.do_immediate(
                compound_node=owning_compound, input_name=port_name, connect_to=i
            )
            ports.append(port)

        for o in outputs_to_promote:
            port_name = _make_unique(_strip_prefix(o.get_name()), output_names)
            port = CreateCompoundSubgraphOutputCommand.do_immediate(
                compound_node=owning_compound, output_name=port_name, connect_from=o
            )
            ports.append(port)
        return ports

    # -------------------------------------------------------------------------
    def do(self):
        self._applied = False
        try:
            with omni.kit.undo.group():
                ports = PromoteUnconnectedToCompoundSubgraphCommand.do_immediate(
                    node=self._node, inputs=self._inputs, outputs=self._outputs
                )
            self._ports = ports
            self._applied = True
            return ports
        except og.OmniGraphError as error:
            # This needs to re-raise, or if the command fails in editor it isn't completely undone with undo
            carb.log_warn(f"Failed to promote unconnected inputs/outputs on {self._node}")
            raise error

    # ---------------------------------------------------------------------------
    def undo(self):
        if self._applied:
            for p in self._ports:
                RemoveCompoundSubgraphAttributeCommand.do_immediate(attribute=p)
            self._applied = False
