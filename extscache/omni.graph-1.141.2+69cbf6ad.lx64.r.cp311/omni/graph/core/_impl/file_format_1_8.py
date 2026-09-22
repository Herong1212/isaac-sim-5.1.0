"""Backwards compatibility support for version 1.8"""

from typing import List

import omni.graph.core as og
import omni.usd
import OmniGraphSchema
from pxr import Sdf, Usd

from . import file_format_helpers as helpers

LAST_FILE_FORMAT_WITH_BUNDLE_SEPARATOR = og.FileFormatVersion(1, 8)


# Output and state bundle separator coversion
#
# During the bundle asymmetry refactoring, changes were made too aggressively.
# The output and state bundle were put into the `outputs:` and `state:` namesapces.
# Unfortunately, this broke downstream respositories - some of them relied on `outputs_` prefix.
# Therefore, `outputs:` and `state:` prefix had to be reverted to `outputs_` and `state_`.
#
# In the meantime there were some Usd file formats that were accidentally converted:
# from:
#  `Node/outputs_bundle`
# to:
#  `Node.outputs:bundle`
#
# This file format upgrade provides ability to revert:
# From `Node.outputs:bundle` to `Node.outputs_bundle`


# ==============================================================================================================
def _is_omni_graph_node(prim: Usd.Prim):
    """Returns true if prim argument is OmniGraph node"""
    return prim.IsA(OmniGraphSchema.OmniGraphNode)


# ==============================================================================================================
def _is_bundle(relationship: Usd.Relationship, is_og_node: bool = False):
    if is_og_node and not _is_omni_graph_node(relationship.GetPrim()):
        return False
    return relationship.GetCustomDataByKey("omni:graph:relType") == "bundle"


# ==============================================================================================================
def _get_node_bundles(node: Usd.Prim):
    """Get all node's inputs that are bundle type."""

    input_bundles: List[Sdf.Path] = []
    output_bundles: List[Sdf.Path] = []
    state_bundles: List[Sdf.Path] = []

    for relationship in node.GetRelationships():
        is_bundle = _is_bundle(relationship)

        relationship_path = Sdf.Path(relationship.GetPath())
        if is_bundle and relationship.GetName().startswith("inputs:"):
            input_bundles.append(relationship_path)

        # Only get output bundles that require conversion to `outputs_`
        elif is_bundle and relationship.GetName().startswith("outputs:"):
            output_bundles.append(relationship_path)

        # Only get state bundles that require conversion to `state_`
        elif is_bundle and relationship.GetName().startswith("state:"):
            state_bundles.append(relationship_path)

    return input_bundles, output_bundles, state_bundles


# ==============================================================================================================
def _upgrade_bundle_relationship_values(bundle_relationship_path: Sdf.Path):
    """Iterate through bundle relationship target values and replace:

    from:
        [NodeA.outputs:bundle, NodeB.state:bundle, Node.inputs:value]
    to:
        [NodeA.outputs_bundle, NodeB.state_bundle, Node.inputs:value]
    """

    stage = omni.usd.get_context().get_stage()
    bundle_relationship = stage.GetRelationshipAtPath(bundle_relationship_path)

    upgraded_targets = []
    for target_path in bundle_relationship.GetTargets():
        relationship = stage.GetRelationshipAtPath(target_path)
        if relationship and _is_bundle(relationship, is_og_node=True):
            name = relationship.GetName()
            if name.startswith("outputs:"):
                name = target_path.name
                name = name.replace("outputs:", "outputs_", 1)
                upgraded_targets.append(target_path.GetParentPath().AppendProperty(name))
            elif name.startswith("state:"):
                name = target_path.name
                name = name.replace("state:", "state_", 1)
                upgraded_targets.append(target_path.GetParentPath().AppendProperty(name))
            else:
                upgraded_targets.append(target_path)
        else:
            upgraded_targets.append(target_path)
    bundle_relationship.SetTargets(upgraded_targets)


# ==============================================================================================================
def migrate_bundle_separator(old_format_version: og.FileFormatVersion, new_format_version: og.FileFormatVersion, _):
    if old_format_version > LAST_FILE_FORMAT_WITH_BUNDLE_SEPARATOR:
        return

    stage = omni.usd.get_context().get_stage()
    if stage is None:
        return

    input_bundles: List[Sdf.Path] = []
    output_bundles: List[Sdf.Path] = []
    state_bundles: List[Sdf.Path] = []

    # Collect input/output relationships
    for node_prim in helpers.get_prims_of_types(stage, ["OmniGraphNode"]):
        inputs, outputs, states = _get_node_bundles(node_prim)
        input_bundles += inputs
        output_bundles += outputs
        state_bundles += states

    # Upgrade input relationship target values:
    # Node.outputs:bundle -> Node.outputs_bundle
    for input_bundle in input_bundles:
        _upgrade_bundle_relationship_values(input_bundle)

    def remove_property(relationship_path: Sdf.Path):
        for prop_spec in stage.GetPropertyAtPath(relationship_path).GetPropertyStack(Usd.TimeCode.Default()):
            prim_spec = prop_spec.layer.GetPrimAtPath(prop_spec.path.GetPrimPath())
            prim_spec.RemoveProperty(prop_spec)

    def upgrade_bundle_relationships(bundle_relationship_paths: [Sdf.Path], str_form: str, str_to: str):
        for bundle_relationship_path in bundle_relationship_paths:
            bundle_relationship = stage.GetRelationshipAtPath(bundle_relationship_path)
            targets = bundle_relationship.GetTargets()
            prim = bundle_relationship.GetPrim()
            name = bundle_relationship.GetName()
            remove_property(bundle_relationship_path)

            # create new relationship
            name = name.replace(str_form, str_to, 1)
            relationship = prim.CreateRelationship(name, True)
            relationship.SetCustomDataByKey("omni:graph:relType", "bundle")
            relationship.SetTargets(targets)

    upgrade_bundle_relationships(output_bundles, "outputs:", "outputs_")
    upgrade_bundle_relationships(state_bundles, "state:", "state_")
