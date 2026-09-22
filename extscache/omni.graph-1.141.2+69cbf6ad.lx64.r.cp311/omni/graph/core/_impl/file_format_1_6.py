"""Backwards compatibility support for version 1.6"""

import carb
import omni.graph.core as og
import omni.usd
import OmniGraphSchema

from . import file_format_helpers as helpers

LAST_FILE_FORMAT_WITHOUT_COMPOUND_SCHEMA_API = og.FileFormatVersion(1, 6)


# ==============================================================================================================
def migrate_compound_node_schema_data(
    old_format_version: og.FileFormatVersion, new_format_version: og.FileFormatVersion, _
):
    """If there are any prims that represent compound node instances, upgrade them to use a schema API
    instead of a custom relationship attribute.
    """
    if old_format_version > LAST_FILE_FORMAT_WITHOUT_COMPOUND_SCHEMA_API:
        return

    stage = omni.usd.get_context().get_stage()
    if stage is None:
        return

    prims = helpers.get_prims_of_types(stage, ["OmniGraphNode"])
    prim_paths_changed = []
    for prim in prims:
        # if the old relationship was found, apply the schema and update the new relationship
        compound_rel = prim.GetRelationship("omni:graph:compound")
        if compound_rel.IsValid():
            schema_api = OmniGraphSchema.CompoundNodeAPI.Apply(prim)
            # At the introduction of the schema, there were only node type compounds
            # so, if this format is found assume the compound is of that type
            schema_api.GetCompoundTypeAttr().Set(OmniGraphSchema.Tokens.nodetype)
            schema_api.GetCompoundGraphRel().SetTargets(compound_rel.GetTargets())
            prim_paths_changed = [str(prim.GetPath())]
            prim.RemoveProperty(compound_rel.GetName())

    if prim_paths_changed:
        carb.log_warn(
            "Scene has migrated to use CompoundNodeAPI Schema - please save and reload. These changes were made:\n"
            f"{prim_paths_changed}"
        )
