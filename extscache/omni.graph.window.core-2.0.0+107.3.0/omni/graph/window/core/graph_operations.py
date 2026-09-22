# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import webbrowser
from typing import List, Optional, Tuple, Union

import carb
import omni.graph.core as og
import omni.graph.core._unstable as ogu
import omni.graph.tools.ogn as ogn
import omni.kit
import omni.usd
from pxr import Sdf, Usd

from .compounds import CompoundUtils
from .graph_model import OmniGraphModel
from .virtual_node_helper import VirtualNodeHelper

# Priority ordered list of supported types to their corresponding constants
# Ordered to prioritize simple types before tuples, and generic types over
# attribute types
TYPE_TO_CONSTANT_NODE = (
    ("any", "omni.graph.nodes.ConstantDouble"),
    ("double", "omni.graph.nodes.ConstantDouble"),
    ("timecode", "omni.graph.nodes.ConstantTimecode"),
    ("float", "omni.graph.nodes.ConstantFloat"),
    ("int", "omni.graph.nodes.ConstantInt"),
    ("int64", "omni.graph.nodes.ConstantInt64"),
    ("uint", "omni.graph.nodes.ConstantUInt"),
    ("half", "omni.graph.nodes.ConstantHalf"),
    ("uchar", "omni.graph.nodes.ConstantUChar"),
    ("uint64", "omni.graph.nodes.ConstantUInt64"),
    ("token", "omni.graph.nodes.ConstantToken"),
    ("string", "omni.graph.nodes.ConstantString"),
    ("path", "omni.graph.nodes.ConstantPath"),
    ("bool", "omni.graph.nodes.ConstantBool"),
    ("target", "omni.graph.nodes.ConstantTarget"),
    ("double[3]", "omni.graph.nodes.ConstantDouble3"),
    ("double[4]", "omni.graph.nodes.ConstantDouble4"),
    ("double[2]", "omni.graph.nodes.ConstantDouble2"),
    ("float[3]", "omni.graph.nodes.ConstantFloat3"),
    ("float[4]", "omni.graph.nodes.ConstantFloat4"),
    ("float[2]", "omni.graph.nodes.ConstantFloat2"),
    ("frame[4]", "omni.graph.nodes.ConstantFrame"),
    ("int[3]", "omni.graph.nodes.ConstantInt3"),
    ("int[4]", "omni.graph.nodes.ConstantInt4"),
    ("int[2]", "omni.graph.nodes.ConstantInt2"),
    ("half[3]", "omni.graph.nodes.ConstantHalf3"),
    ("half[4]", "omni.graph.nodes.ConstantHalf4"),
    ("half[2]", "omni.graph.nodes.ConstantHalf2"),
    ("colord[3]", "omni.graph.nodes.ConstantColor3d"),
    ("colorf[3]", "omni.graph.nodes.ConstantColor3f"),
    ("colorh[3]", "omni.graph.nodes.ConstantColor3h"),
    ("colord[4]", "omni.graph.nodes.ConstantColor4d"),
    ("colorf[4]", "omni.graph.nodes.ConstantColor4f"),
    ("colorh[4]", "omni.graph.nodes.ConstantColor4h"),
    ("matrixd[2]", "omni.graph.nodes.ConstantMatrix2d"),
    ("matrixd[3]", "omni.graph.nodes.ConstantMatrix3d"),
    ("matrixd[4]", "omni.graph.nodes.ConstantMatrix4d"),
    ("normald[3]", "omni.graph.nodes.ConstantNormal3d"),
    ("normalf[3]", "omni.graph.nodes.ConstantNormal3f"),
    ("normalh[3]", "omni.graph.nodes.ConstantNormal3h"),
    ("pointd[3]", "omni.graph.nodes.ConstantPoint3d"),
    ("pointf[3]", "omni.graph.nodes.ConstantPoint3f"),
    ("pointh[3]", "omni.graph.nodes.ConstantPoint3h"),
    ("quatd[4]", "omni.graph.nodes.ConstantQuatd"),
    ("quatf[4]", "omni.graph.nodes.ConstantQuatf"),
    ("quath[4]", "omni.graph.nodes.ConstantQuath"),
    ("texcoordd[3]", "omni.graph.nodes.ConstantTexCoord3d"),
    ("texcoordf[3]", "omni.graph.nodes.ConstantTexCoord3f"),
    ("texcoordh[3]", "omni.graph.nodes.ConstantTexCoord3h"),
    ("texcoordd[2]", "omni.graph.nodes.ConstantTexCoord2d"),
    ("texcoordf[2]", "omni.graph.nodes.ConstantTexCoord2f"),
    ("texcoordh[2]", "omni.graph.nodes.ConstantTexCoord2h"),
    ("vectord[3]", "omni.graph.nodes.ConstantVector3d"),
    ("vectorf[3]", "omni.graph.nodes.ConstantVector3f"),
    ("vectorh[3]", "omni.graph.nodes.ConstantVector3h"),
)


# -----------------------------------------------------------------------------
def _graph_from_port(port: Sdf.Path) -> Optional[Sdf.Path]:
    """Given an attribute port, returns the owning graph"""
    try:
        attr = og.Controller.attribute(str(port))
    except og.OmniGraphError:
        return None

    return Sdf.Path(attr.get_node().get_graph().get_path_to_graph())


# -----------------------------------------------------------------------------


def _get_potential_types(port: Sdf.Path) -> List[str]:
    """
    Given a port, returns the list of potential types that could be accepted on
    a connected port.
    This does not guarantee matching types, as nodes may have custom resolution
    logic that is not validated.
    """

    # bundles will return as invalid ports
    try:
        attr = og.Controller.attribute(str(port))
    except og.OmniGraphError:
        return []

    if not attr:
        return []
    attr_type = attr.get_resolved_type()
    if attr_type.base_type == og.BaseDataType.UNKNOWN:
        extended_type = attr.get_extended_type()
        if extended_type == og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_ANY:
            return ["any"]
        if extended_type == og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_UNION:
            union_types = attr.get_union_types()
            return union_types
    if attr_type.base_type == og.BaseDataType.PRIM:
        return ["bundle"]
    return [attr_type.get_ogn_type_name()]


# -----------------------------------------------------------------------------


def _get_matching_constant_node(types: List[str]) -> Optional[str]:
    """
    Given a list of types, returns the best matching constant node
    Returns:
        The qualified name of the constant node, or None, if there are no matches
    """
    # searches the list in priority order
    for type_name, node_name in TYPE_TO_CONSTANT_NODE:
        if type_name in types:
            return node_name
    return None


# -----------------------------------------------------------------------------


def _try_find_matching_input_type(types: List[str], port: Sdf.Path, require_constant: bool) -> Optional[str]:
    """
    Given a port, search the inputs for another input with a resolved type
    Note: this will only match types that have a constant node type
    """
    node = og.Controller.node(port.GetPrimPath())
    if node:
        for attr in node.get_attributes():
            if (
                Sdf.Path(attr.get_path()) == port
                or attr.get_port_type() != og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT
            ):
                continue
            attr_type = attr.get_resolved_type()
            if (
                attr_type.base_type != og.BaseDataType.UNKNOWN
                and attr_type.get_ogn_type_name() in types
                and
                # only consider it, if there is a matching constant node
                (not require_constant or _get_matching_constant_node([attr_type.get_ogn_type_name()]) is not None)
            ):
                return attr_type.get_ogn_type_name()

    return None


# -----------------------------------------------------------------------------


def _find_matching_variable_type(port: Sdf.Path) -> Tuple[og.Type, bool]:
    """
    Find a matching variable type for a port
    Returns the best matching type, and a boolean indicating whether
    the port can have a value retrieved
    """
    attr = og.Controller.attribute(str(port))
    attr_type = attr.get_resolved_type()
    if attr_type.base_type != og.BaseDataType.UNKNOWN:
        return (attr_type, True)

    potential_types = _get_potential_types(port)
    matching_type = _try_find_matching_input_type(potential_types, port, False)
    if matching_type is not None:
        return (og.AttributeType.type_from_ogn_type_name(matching_type), False)

    # try a priority list of types first
    # scalars take priority over vectors.
    # 3 component takes highest priority of vectors
    for prefix in ["", "[3]", "[4]", "[2]"]:
        for x in ["double", "float", "half", "int", "token", "string"]:
            type_str = x + prefix
            if type_str in potential_types:
                return (og.AttributeType.type_from_ogn_type_name(type_str), False)

    if potential_types:
        return (og.AttributeType.type_from_ogn_type_name(potential_types[0]), False)

    return (None, False)


# -----------------------------------------------------------------------------


def _create_read_variable_node(
    model: OmniGraphModel, port: Sdf.Path, name: str, pos: Tuple[float], graph_path: Union[Sdf.Path, str]
):
    """
    Create a read variable node from an existing variable and connect it to the given port
    """
    stage = omni.usd.get_context().get_stage()
    (_, node) = model.create_node("omni.graph.core.ReadVariable", str(graph_path), pos)
    if node:
        og.Controller.set(node.get_attribute("inputs:variableName"), name, update_usd=True, undoable=True)
        relationship_path = Sdf.Path(node.get_prim_path()).AppendProperty("inputs:graph")
        omni.kit.commands.execute(
            "AddRelationshipTarget",
            relationship=stage.GetRelationshipAtPath(relationship_path),
            target=model.get_graph(None).get_path_to_graph(),  # relationship is to the parent graph
        )
        og.Controller.connect(node.get_attribute("outputs:value"), port, update_usd=True, undoable=True)


# -----------------------------------------------------------------------------


def _create_write_variable_node(
    model: OmniGraphModel, port: Sdf.Path, name: str, pos: Tuple[float], graph_path: Union[Sdf.Path, str]
):
    """
    Create a read variable node from an existing variable and connect it to the given port
    """
    stage = omni.usd.get_context().get_stage()
    (_, node) = model.create_node("omni.graph.core.WriteVariable", str(graph_path), pos)
    if node:
        og.Controller.set(node.get_attribute("inputs:variableName"), name, update_usd=True, undoable=True)
        relationship_path = Sdf.Path(node.get_prim_path()).AppendProperty("inputs:graph")
        omni.kit.commands.execute(
            "AddRelationshipTarget",
            relationship=stage.GetRelationshipAtPath(relationship_path),
            target=model.get_graph(None).get_path_to_graph(),  # relationship is to the parent graph
        )
        og.Controller.connect(port, node.get_attribute("inputs:value"), update_usd=True, undoable=True)


# -----------------------------------------------------------------------------


def get_compatible_variables(model: OmniGraphModel, port: Sdf.Path) -> List[og.IVariable]:
    """Get a list of compatible variables with the given port"""

    types = _get_potential_types(port)
    if not types:
        return []

    result = []
    for var in model._graph.get_variables():  # noqa: protected-access
        if types[0] == "any" or var.type.get_ogn_type_name() in types:
            result.append(var)

    return result


# ------------------------------------------------------------------------------


def promote_to_existing_variable(model: OmniGraphModel, port: Sdf.Path, name: str, pos: Tuple[float]):
    """
    Promote an empty port to use an existing variable given by the name.
    An input port will promote to a read variable, and an output port will promote to a write variable node.
    """

    if not get_compatible_variables(model, port):
        carb.log_error("Promote to Existing Variable: No matching variables match the given port")
        return

    attr = og.Controller.attribute(str(port))
    if not attr:
        carb.log_error("Promote to Existing Variable: Port is not a valid node port")
        return

    port_type = attr.get_port_type()
    is_input = port_type == og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT
    is_output = port_type == og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT
    output_only = attr.get_metadata(ogn.MetadataKeys.OUTPUT_ONLY) == "1"
    graph_path = _graph_from_port(port)
    if not graph_path:
        carb.log_error(f"Promote To Existing Variable: Could not find graph for port {port}")
        return

    if is_output or (is_input and output_only):
        with omni.kit.undo.group():
            _create_write_variable_node(model, port, name, pos, graph_path)
    elif is_input:
        with omni.kit.undo.group():
            _create_read_variable_node(model, port, name, pos, graph_path)


# -----------------------------------------------------------------------------


def can_promote_to_variable(model: OmniGraphModel, port: Sdf.Path) -> bool:
    """
    Determines whether the given port can be promoted to be a constant
    """

    # get the connections. None is returned if the port is not an input/output,
    # [] otherwise
    outputs = model.get_output_connections(port)
    inputs = model[port].inputs
    connections = outputs if inputs is None else inputs

    invalid_types = {
        og.BaseDataType.ASSET,
        og.BaseDataType.RELATIONSHIP,
        og.BaseDataType.CONNECTION,
        og.BaseDataType.PRIM,
        og.BaseDataType.TAG,
    }

    invalid_roles = {
        og.AttributeRole.OBJECT_ID,
        og.AttributeRole.EXECUTION,
        og.AttributeRole.APPLIED_SCHEMA,
        og.AttributeRole.BUNDLE,
        og.AttributeRole.PATH,  # Path included, as it isn't explicitly supported by variables
    }

    # TARGET role not available prior to Kit 105.
    if hasattr(og.AttributeRole, "TARGET"):
        invalid_roles.add(og.AttributeRole.TARGET)

    if connections is not None and len(connections) == 0:
        attr = model.get_attribute_from_path(port)
        if (not attr) or attr.get_metadata(ogn.MetadataKeys.LITERAL_ONLY):
            return False
        attr_type = attr.get_resolved_type()
        return attr_type.base_type not in invalid_types and attr_type.role not in invalid_roles

    return False


# -----------------------------------------------------------------------------


def promote_to_variable(model: OmniGraphModel, port: Sdf.Path, pos: Tuple[float]):
    """
    Promotes the given empty port to a variable in the graph
    """
    if not can_promote_to_variable(model, port):
        return

    graph = model.get_graph(None)
    stage = omni.usd.get_context().get_stage()

    name = Sdf.Path.StripNamespace(port.name)
    base_name = name
    incr = 1
    while graph.find_variable(name):
        name = f"{base_name}_{incr:02d}"
        incr = incr + 1

    # determine the variable type
    (var_type, set_value) = _find_matching_variable_type(port)
    if var_type is None:
        carb.log_error(f"Promote to Variable: Could not find a matching type for {port}")
        return

    # use the USD value if possible
    value = None
    if set_value:
        value = stage.GetAttributeAtPath(port).Get()

    inputs = model[port].inputs
    graph_path = _graph_from_port(port)
    if not graph_path:
        carb.log_error(f"Promote To Variable: Could not find graph for port {port}")
        return

    with omni.kit.undo.group():
        og.cmds.CreateVariable(graph=graph, variable_name=name, variable_type=var_type, variable_value=value)
        if inputs == []:
            _create_read_variable_node(model, port, name, pos, graph_path)
        else:
            _create_write_variable_node(model, port, name, pos, graph_path)


# -----------------------------------------------------------------------------


def can_promote_to_constant(model: OmniGraphModel, port: Sdf.Path) -> bool:
    """
    Determines whether the given port can be promoted to be a variable
    """
    connections = model[port].inputs
    if connections is not None and len(connections) == 0 and not model.is_execution(port):
        attr = model.get_attribute_from_path(port)
        if (not attr) or attr.get_metadata(ogn.MetadataKeys.LITERAL_ONLY):
            return False

        potentials = _get_potential_types(port)
        return _get_matching_constant_node(potentials) is not None

    return False


# -----------------------------------------------------------------------------


def promote_to_constant(model: OmniGraphModel, port: Sdf.Path, pos: Tuple[float]):
    """Promotes the given empty port to a constant"""

    potentials = _get_potential_types(port)
    # only set the value, if the type is valid
    set_value = len(potentials) == 1 and potentials[0] != "any"

    # there is more than one type, try to match to other inputs
    if not set_value:
        matching_input = _try_find_matching_input_type(potentials, port, True)
        if matching_input:
            potentials = [matching_input]

    constant_node = _get_matching_constant_node(potentials)
    if not constant_node:
        carb.log_error(f"Promote To Constant: Could not find constant node for type{port}")
        return

    graph_path = _graph_from_port(port)
    if not graph_path:
        carb.log_error(f"Promote To Constant: Could not find graph for port {port}")
        return

    with omni.kit.undo.group():
        (_, node) = model.create_node(constant_node, str(graph_path), pos)
        if node:
            if set_value:
                stage = omni.usd.get_context().get_stage()
                prop = stage.GetPropertyAtPath(port)
                if isinstance(prop, Usd.Attribute):
                    value = prop.Get()
                elif isinstance(prop, Usd.Relationship):
                    value = prop.GetTargets()
                if value is not None:
                    og.Controller.set(node.get_attribute("inputs:value"), value, update_usd=True, undoable=True)
            og.Controller.connect(node.get_attribute("inputs:value"), port, update_usd=True, undoable=True)


# -----------------------------------------------------------------------------


def is_help_available_for_node_type(node_type: Union[str, og.NodeType]) -> bool:
    """Determines if there is help available for a given node type"""
    if node_type is None:
        return False

    if isinstance(node_type, str):
        node_type = og.get_node_type(node_type)
        if not node_type:
            return False
    elif not isinstance(node_type, og.NodeType):
        # In case anyone is not passing in the node, where no help can be provided
        return False

    # if there is no extension information, it's likely a compound node
    extension = node_type.get_metadata(ogn.MetadataKeys.EXTENSION)
    if not extension:
        return False

    return True


# -----------------------------------------------------------------------------


def show_help_for_node_type(node_type: Union[str, og.NodeType]):
    """Open up the help page for the node type passed in. Assume that the documentation exists"""

    if isinstance(node_type, str):
        node_type_name = node_type
        node_type = og.get_node_type(node_type_name)
    elif isinstance(node_type, og.NodeType):
        node_type_name = node_type.get_node_type()
    else:
        # In case anyone is not passing in the node, where no help can be provided
        return

    # Build up the URL to point to the docs. The extension and node type name use "-" as
    # separators and the node type name has the extension name stripped from it.
    # Node Type="omni.graph.nodes.BundleInspector", Extension="omni.graph.nodes", Version=1
    # -> URL = .../omni-graph-nodes/BundleInspector-1.html
    # Node Type="omni.deform.mesh", Extension="omni.anim.deformers", Version=2
    # -> URL = .../omni-anim-deformers/omni-deform-mesh-2.html
    url_pattern = "https://docs.omniverse.nvidia.com/prod_extensions/prod_extensions/ext_omnigraph/node-library/nodes/{}/{}-{}.html"
    # When the documentation is built but not yet publicly available uncomment this next
    # line so that you can test before it goes live.
    # url_pattern = "https://omniverse.gitlab-master-pages.nvidia.com/omni-docs/prod_extensions/prod_extensions/ext_omnigraph/node-library/nodes/{}/{}-{}.html"

    version = og.GraphRegistry().get_node_type_version(node_type_name)
    extension = node_type.get_metadata(ogn.MetadataKeys.EXTENSION)
    extension = extension.replace(".", "-").lower()
    node_type_name = node_type_name.replace(".", "-").replace(extension, "").lower()
    if node_type_name[0] == "-":
        node_type_name = node_type_name[1:]
    url = url_pattern.format(extension, node_type_name, version)
    webbrowser.open(url)


# -----------------------------------------------------------------------------


def can_convert_type(model: OmniGraphModel, port: Sdf.Path) -> bool:
    """
    Determines whether the given input port can be (re)resolved
    """
    connections = model[port].inputs
    if connections is not None and len(connections) == 0 and not model.is_execution(port):
        attr = model.get_attribute_from_path(port)
        if attr is not None:
            extended_type = attr.get_extended_type()
            if extended_type in (
                og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_ANY,
                og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_UNION,
            ):
                return True
    return False


# -------------------------------------------------------------------------------


def remove_subgraph_port(model: OmniGraphModel, port: Sdf.Path):
    """Given a port on a compound node instance for a subgraph, removes the port from the node"""
    ogu.cmds.RemoveCompoundSubgraphAttribute(attribute=port)
    # remove the ui with both to/from versions to handle the owner and compound editing cases
    model.remove_port_ui(VirtualNodeHelper.convert_to(port))
    model.remove_port_ui(VirtualNodeHelper.convert_from(port))
    model._item_changed(None)  # noqa: protected-access


# -------------------------------------------------------------------------------


def promote_attribute_to_compound(model: OmniGraphModel, port: Sdf.Path):
    """Promotes an attribute to the compound node above it"""

    compound_node = CompoundUtils.get_compound_node(port.GetPrimPath())
    if not compound_node:
        return

    graph_path = compound_node.get_compound_graph_instance().get_path_to_graph()
    prim = omni.usd.get_context().get_stage().GetPrimAtPath(graph_path)
    if not prim:
        carb.log_warning(f"Could not find USD Prim {graph_path} for promotion: {port}")
        return

    try:
        attribute = og.Controller.attribute(str(port))
    except og.OmniGraphError:
        carb.log_warning(f"Expected attribute to exist for promotion: {port}")
        return

    model.create_new_subgraph_port(attribute, prim, model.is_output(attribute), True)
    model._item_changed(None)  # noqa: protected-access


# -------------------------------------------------------------------------------


def can_rename_port(port: Sdf.Path):
    """Can we rename the given port? For compound subgraphs, all ports can be renamed"""
    # Check if it's an sdf path as we could also get an IsolationModel.EmptyPort, which should not be renamable
    return isinstance(port, Sdf.Path) and (
        CompoundUtils.is_compound_subgraph_node(port) or CompoundUtils.is_compound_graph(port.GetPrimPath())
    )


# -------------------------------------------------------------------------------


def promote_unconnected_to_compound(model: OmniGraphModel, node: Usd.Prim, inputs: bool, outputs: bool):
    """Promote unconnected inputs/outputs on a node to its owning compound"""
    (_, ports) = ogu.cmds.PromoteUnconnectedToCompoundSubgraph(
        node=og.Controller.node(node), inputs=inputs, outputs=outputs
    )
    for p in ports:
        src_attr = CompoundUtils.get_connected_port_in_subgraph(p)
        if src_attr:
            is_attr_output = model.is_output(src_attr)
            is_attr_output_only = src_attr.get_metadata(ogn.MetadataKeys.OUTPUT_ONLY) == "1"
            model._create_subgraph_port_ui(  # noqa: protected-access
                Sdf.Path(p), src_attr, is_attr_output, is_attr_output_only
            )
    model._item_changed(None)  # noqa: protected-access
