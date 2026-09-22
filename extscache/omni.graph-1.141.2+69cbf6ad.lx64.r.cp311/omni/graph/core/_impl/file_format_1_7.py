"""Backwards compatibility support for version 1.7"""

import omni.graph.core as og
import omni.usd
import OmniGraphSchema
from pxr import Sdf

from . import attribute_types
from . import file_format_helpers as helpers

LAST_FILE_FORMAT_WITH_BUNDLE_IO_ASYMMETRY = og.FileFormatVersion(1, 7)

# Input-Output Bundle Asymmetry:
#
# Prior to version 1.8 input bundles were represented as relationships, but
# output and state bundles were represented as a primitive nested under a node.
#
# This file is responsible for unifying input, output and state bundles.
# It converts state and output bundles into relationship type.
#
# The upgrade involves:
# 1. Inactivating output and state bundles.
# 2. Creating new relationships representing output and state bundles.
# 3. Upgrading graph topology connections for output -> input bundles
#    to respect created relationships in 2.
#
# Connections prior to version 1.8:
# NodeA/outputs_bundle -> NodeB.inputs:bundle[NodeA/outputs_bundle]
#
# New 1.8 upgraded connections:
# NodeA.outputs_bundle -> NodeB.inputs:bundle[NodeA.outputs:bundle]


INPUT_NS = attribute_types.get_port_type_namespace(og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT)
OUTPUT_NS = attribute_types.get_port_type_namespace(og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT)
STATE_NS = attribute_types.get_port_type_namespace(og.AttributePortType.ATTRIBUTE_PORT_TYPE_STATE)

NS_DELIMITER = "_"
OUTPUT_PREFIX = OUTPUT_NS + NS_DELIMITER
STATE_PREFIX = STATE_NS + NS_DELIMITER
LEGACY_BUNDLE_PRIM_NAME = "Output"


# ==============================================================================================================
def is_omni_graph_node(prim):
    """Returns true if prim argument is OmniGraph node"""
    return prim.IsA(OmniGraphSchema.OmniGraphNode)


# ==============================================================================================================
def is_node_bundle_primitive(prim_or_path):
    """Prior to version 1.8 `outputs` and `state` bundles were represented as
    a child primitives nested under a node.
    This function confirms if given primitive or a path is a primitive
    representing bundle nested under a node primitive.
    """
    prim = prim_or_path
    if isinstance(prim_or_path, Sdf.Path):
        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath(prim_or_path)

    if not prim.IsValid():
        return False
    if prim.GetTypeName() != LEGACY_BUNDLE_PRIM_NAME:
        return False
    if not is_omni_graph_node(prim.GetParent()):
        return False

    name = prim.GetPath().name
    return name.startswith(OUTPUT_PREFIX) or name.startswith(STATE_PREFIX)


# ==============================================================================================================
def get_node_bundle_primitives(node):
    """Prior to version 1.8 `outputs` and `state` bundles were represented as
    a child primitives nested under a node.
    This function returns all primitives nested under a node that are
    primitives represetning bundles.
    """
    bundle_prims = []
    for child in node.GetChildren():
        if is_node_bundle_primitive(child):
            bundle_prims.append(child)
    return bundle_prims


# ==============================================================================================================
def get_node_input_bundles(node):
    """Get all node's inputs that are bundle type."""
    rels = []
    for relationship in node.GetRelationships():
        if not relationship.GetName().startswith(INPUT_NS):
            continue
        if relationship.GetCustomDataByKey("omni:graph:relType") == "target":
            continue
        rels.append(relationship)
    return rels


# ==============================================================================================================
def get_node_input_targets(node):
    """Get all node's inputs that are target type."""
    rels = []
    for relationship in node.GetRelationships():
        if not relationship.GetName().startswith(INPUT_NS):
            continue
        if relationship.GetCustomDataByKey("omni:graph:relType") != "target":
            continue
        rels.append(relationship)
    return rels


# ==============================================================================================================
def upgrade_relationship_values(relationship):
    """Iterate through relationship values and upgrade bundle primitives
    from primitive format to bundle relationship. Upgrade happens only
    if target value is a bundle primitive, non bundle prim values remain
    unchanged:

    from:
        [NodeA/outputs_bundle, NodeB/state_bundle, Node.inputs:value]
    to:
        [NodeA.outputs_bundle, NodeB.state:bundle, Node.inputs:value]
    """
    upgraded_targets = []
    for target_path in relationship.GetTargets():
        if is_node_bundle_primitive(target_path):
            path = target_path.GetParentPath()
            name = target_path.name
            upgraded_targets.append(path.AppendProperty(name))
        else:
            upgraded_targets.append(target_path)
    relationship.SetTargets(upgraded_targets)


# ==============================================================================================================
def migrate_bundle_io_asymmetry(old_format_version: og.FileFormatVersion, new_format_version: og.FileFormatVersion, _):
    if old_format_version > LAST_FILE_FORMAT_WITH_BUNDLE_IO_ASYMMETRY:
        return

    stage = omni.usd.get_context().get_stage()
    if stage is None:
        return

    input_bundles = []
    input_targets = []
    bundle_prims = []

    for prim in helpers.get_prims_of_types(stage, ["OmniGraphNode"]):
        bundle_prims += get_node_bundle_primitives(prim)
        input_bundles += get_node_input_bundles(prim)
        input_targets += get_node_input_targets(prim)

    # Upgrade input bundles relationship values
    for input_bundle in input_bundles:
        upgrade_relationship_values(input_bundle)
        input_bundle.SetCustomDataByKey("omni:graph:relType", "bundle")

    # Backwards compatibility mode.
    # Upgrade input targets relationship values
    for input_target in input_targets:
        upgrade_relationship_values(input_target)

    # Inactivate bundle primitives and create new relationships for
    # output and state bundles.
    for bundle_prim in bundle_prims:
        name = bundle_prim.GetPath().name

        # replace Output prim with an attribute that is relationship
        bundle_relationship = bundle_prim.GetParent().CreateRelationship(name, True)
        bundle_relationship.SetCustomDataByKey("omni:graph:relType", "bundle")

        # Do not remove old bundle primitives:
        # https://openusd.org/release/api/class_usd_stage.html#ac605faad8fc2673263775b1eecad2955
        bundle_prim.SetActive(False)
