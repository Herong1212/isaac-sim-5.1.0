"""File format upgrade utilities"""

from typing import Any, Dict, List, Optional, Tuple

import carb
import omni.graph.core as og
import omni.usd
import OmniGraphSchema
from omni.kit.commands import execute
from pxr import Gf, Usd

from . import file_format_helpers as helpers

EXTENDED_ATTRIBUTE_SCOPED_CUSTOM_DATA_VERSION = og.FileFormatVersion(1, 5)

LAST_FILE_FORMAT_VERSION_WITHOUT_SCHEMA = og.FileFormatVersion(1, 5)
"""This is the last file format version where it is possible to have OmniGraph prims that do not use the schema"""


# ==============================================================================================================
def _get_og_node_prims(stage: Usd.Stage) -> list[Usd.Prim]:
    """Gets the OmniGraphNode and ComputeNode prims found in the scene."""
    return helpers.get_prims_of_types(stage, ["ComputeNode", "OmniGraphNode"])


# ==============================================================================================================
def check_for_bare_connections(stage: Usd.Stage) -> List[str]:
    """Check for any of the old unsupported connections from nodes to prims that cannot exist in schema-based world

    Return:
        List of strings describing the forbidden connections found
    """
    allowed_attributes = {"node:type"}

    bad_connections = []

    og_prims = _get_og_node_prims(stage)

    for prim in og_prims:
        for attribute in prim.GetAttributes():
            if attribute.GetName() in allowed_attributes:
                continue
            for connected_path in attribute.GetConnections():
                connected_prim = stage.GetPrimAtPath(connected_path.GetPrimPath())
                if not connected_prim.IsValid():
                    carb.log_warn(
                        f"Invalid connection found at {attribute.GetPath()}:"
                        f" {connected_path.GetPrimPath()} while migrating to new schema"
                    )
                elif connected_prim.GetTypeName() not in ["ComputeNode", "OmniGraphNode"]:
                    bad_connections.append(f"{prim.GetPrimPath()} - {connected_path}")
    return bad_connections


# ==============================================================================================================
def migrate_attribute_custom_data(
    old_format_version: og.FileFormatVersion, new_format_version: og.FileFormatVersion, _
):
    """Add scoped customData to attributes which have the old format"""
    if old_format_version < EXTENDED_ATTRIBUTE_SCOPED_CUSTOM_DATA_VERSION:
        stage = omni.usd.get_context().get_stage()
        if stage is None:
            return

        og_prims = _get_og_node_prims(stage)
        for prim in og_prims:
            if prim:
                for attribute in prim.GetAttributes():
                    custom_data = attribute.GetCustomData()
                    extended_type = custom_data.get("ExtendedAttributeType", None)
                    if extended_type:
                        attribute.SetCustomDataByKey("omni:graph:attrType", extended_type)


# ==============================================================================================================
class OmniGraphSchemaMigrator:
    """Collection of methods to manage all of the steps involved in migrating an arbitrary graph to use schema prims"""

    def __init__(self):
        """Set up initial values"""
        self.__command_count = 0

    # --------------------------------------------------------------------------------------------------------------
    @property
    def stage(self) -> Usd.Stage:
        """Returns the stage in use - set as a property so that the latest version is always used as it changes"""
        return omni.usd.get_context().get_stage()

    # --------------------------------------------------------------------------------------------------------------
    def __check_for_old_prim_nodes(self) -> List[str]:
        """Delete any of the old unsupported prim nodes that cannot exist in schema-based world

        Return:
            List of prim paths deleted
        """
        prims_to_remove = []
        og_prims = _get_og_node_prims(self.stage)
        for prim in og_prims:
            node_type_attr = prim.GetAttribute("node:type")
            if node_type_attr.IsValid() and node_type_attr.Get() == "omni.graph.core.Prim":
                prim.SetActive(False)
                prims_to_remove.append(prim.GetPrimPath())
                carb.log_error(
                    "Nodes of type omni.graph.core.Prim no longer function. "
                    f"{prim.GetPrimPath()} has been disabled and should be deleted."
                )
        return prims_to_remove

    # --------------------------------------------------------------------------------------------------------------
    def __change_prim_types_to_match_schema(self) -> List[Tuple[str, str, str]]:
        """Modify any old prim names to match the ones used by the schema

        Return:
            List of (path, old_type, new_type) for prims whose type was changed
        """
        retyped = []
        compute_graph_prims = helpers.get_prims_of_types(self.stage, ["GlobalComputeGraph", "ComputeGraph"])
        for prim in compute_graph_prims:
            retyped.append((str(prim.GetPrimPath()), prim.GetTypeName(), "OmniGraph"))
            prim.SetTypeName("OmniGraph")

        compute_node_prims = helpers.get_prims_of_types(self.stage, ["ComputeNode"])
        for prim in compute_node_prims:
            retyped.append((str(prim.GetPrimPath()), prim.GetTypeName(), "OmniGraphNode"))
            prim.SetTypeName("OmniGraphNode")
            # Ensure that the schema-defined attributes on the node are no longer custom
            node_prim = OmniGraphSchema.OmniGraphNode(prim)
            if node_prim:
                node_type_attr = node_prim.GetNodeTypeAttr()
                if node_type_attr.IsValid():
                    if not node_type_attr.SetCustom(False):
                        carb.log_warn(f"Failed to set node:type attribute to non-custom on {prim.GetPrimPath()}")
                else:
                    carb.log_warn(f"OmniGraph prim node {prim.GetPrimPath()} has no node:type attribute")
                node_type_version_attr = node_prim.GetNodeTypeVersionAttr()
                if node_type_version_attr.IsValid():
                    if not node_type_version_attr.SetCustom(False):
                        carb.log_warn(f"Failed to set node:typeVersion attribute to non-custom on {prim.GetPrimPath()}")
                else:
                    carb.log_warn(f"OmniGraph prim node {prim.GetPrimPath()} has no node:type attribute")
            else:
                # This might be an error or it might just be the fact that the USD notification to change the type
                # hasn't been processed yet. As this is only temporary compatibility code and we know that when
                # reading a file the prims are immediately valid there is no need to add the complexity here to
                # tie into an event loop and await the USD notification propagation.
                pass
        return retyped

    # --------------------------------------------------------------------------------------------------------------
    def __create_top_level_graph(self) -> List[Tuple[str, str]]:
        """If there are any nodes or settings not in a graph then create a graph for them and move them into it.

        Assumes that before calling this all of the old prim type names have been replaced with the schema prim
        type names.

        Args:
            stage: USD stage on which to replace settings

        Return:
            List of (old_path, new_path) for prims that were moved from the root level to a new graph

        Raises:
            og.OmniGraphError if the required prim changes failed
        """
        # Collect this map of settings prim path onto the path at which the parent graph must be created
        prims_to_move = []
        prims = helpers.get_prims_of_types(self.stage, ["ComputeGraphSettings", "OmniGraphNode"])
        for prim in prims:
            parent = prim.GetParent()
            if not parent.IsValid() or parent.GetTypeName() != "OmniGraph":
                prims_to_move.append(prim)

        prim_paths_moved = []
        if prims_to_move:
            for prim in prims_to_move:
                parent_path = str(prim.GetParent().GetPrimPath())
                if parent_path[-1] != "/":
                    parent_path += "/"
                default_global_graph_path = f"{parent_path}__graphUsingSchemas"
                global_graph_prim = self.stage.GetPrimAtPath(default_global_graph_path)
                if not global_graph_prim:
                    (status, result) = execute("CreatePrim", prim_path=default_global_graph_path, prim_type="OmniGraph")
                    if not status:
                        raise og.OmniGraphError(
                            f"Error creating OmniGraph prim at {default_global_graph_path} - {result}"
                        )
                new_prim_path = f"{default_global_graph_path}/{prim.GetName()}"
                prim_paths_moved.append((str(prim.GetPrimPath()), new_prim_path))
                (status, result) = execute("MovePrim", path_from=prim.GetPrimPath(), path_to=new_prim_path)
                if not status:
                    raise og.OmniGraphError(
                        f"Error moving OmniGraph prim from {prim.GetPrimPath()} to {new_prim_path} - {result}"
                    )
        return prim_paths_moved

    # --------------------------------------------------------------------------------------------------------------
    def __replace_settings_with_properties(self, new_file_format_version: Tuple[int, int]) -> List[str]:
        """If there are any of the old settings prims move their property values into their containing graph.

        Args:
            new_file_format_version: The file format version that should be used for the graph setting

        Return:
            List of prim paths with settings that were transferred to the containing graph and then deleted
        """
        prims_disabled = []
        prims = helpers.get_prims_of_types(self.stage, ["ComputeGraphSettings"])
        for prim in prims:
            prim.SetActive(False)
            carb.log_warn(
                "Prims of type ComputeGraphSettings no longer function. "
                f"{prim.GetPrimPath()} has been disabled and should be deleted."
            )
            graph_prim = prim.GetParent()
            # Need to check against the old types as well as the USD change notices may not have percolated
            if graph_prim.IsValid() and graph_prim.GetTypeName() in [
                "GlobalComputeGraph",
                "ComputeGraph",
                "OmniGraph",
            ]:
                for attr in prim.GetAttributes():
                    setting_name = attr.GetName()
                    setting_value = attr.Get()
                    if setting_name == "flatCacheBacking":
                        setting_name = "fabricCacheBacking"
                        if setting_value == "StagedWithHistory":
                            setting_value = "StageWithHistory"
                    graph_attr = graph_prim.GetAttribute(setting_name)
                    if not graph_attr.IsValid():
                        graph_attr = graph_prim.CreateAttribute(
                            setting_name, attr.GetTypeName(), custom=False, variability=attr.GetVariability()
                        )
                    if graph_attr.IsValid():
                        graph_attr.Set(setting_value)
                    else:
                        carb.log_warn(
                            f"Could not create settings attribute {attr.GetName()}"
                            f" on graph {graph_prim.GetPrimPath()}"
                        )
                prims_disabled.append(str(prim.GetPrimPath()))
                schema_prim = OmniGraphSchema.OmniGraph(graph_prim)
                if bool(schema_prim):
                    file_format_version_attr = schema_prim.GetFileFormatVersionAttr()
                    file_format_version_attr.Set(Gf.Vec2i(new_file_format_version))
                else:
                    carb.log_warn(f"Could not cast graph prim {graph_prim.GetPrimPath()} to OmniGraph schema")
            else:
                carb.log_warn(f"Could not find graph above {prim.GetPrimPath()} to receive settings")

        prims = helpers.get_prims_of_types(self.stage, ["ComputeNodeMetadata"])
        for prim in prims:
            # Also get rid of the obsolete metadata children
            prims_disabled.append(str(prim.GetPrimPath()))
            prim.SetActive(False)
            carb.log_warn(
                "Prims of type ComputeNodeMetadata no longer function. "
                f"{prim.GetPrimPath()} has been disabled and should be deleted."
            )
        return prims_disabled

    # --------------------------------------------------------------------------------------------------------------
    # Handling for old files that did not use the OmniGraph schema (earlier than 1.3)
    def update(self, new_file_format_version: Optional[Tuple[int, int]] = None) -> Dict[str, Any]:
        """Update the current file to use the new schema; run when a new stage is being attached.

        Conversion of old scenes entails:
            - Changing any ComputeGraph or GlobalComputeGraph prims to be OmniGraph types
            - If a ComputeGraphSettings prim exists, migrating its attribute values to the OmniGraph prim
            - Changing any ComputeNode prims to be OmniGraphNode types
            - If any ComputeNode prims appear without a parent ComputeGraph then create a default graph
              and move them into it

        Args:
            new_file_format_version: The file format version that should be used for the graph setting. If None then
                                     it will force the version immediately following the schema conversion (1, 4)

        Return:
            A dictionary of operations that were performed as part of the migration (key describes the operation, value
            is the objects to which it was applied)
        """
        stage = omni.usd.get_context().get_stage()
        if stage is None:
            return {"message": "No stage to convert"}

        try:
            self.__command_count = 0
            return_values = {}  # noqa: SIM904

            # Verify that the old prim nodes don't exist
            return_values["Prim Nodes Removed"] = self.__check_for_old_prim_nodes()

            # Verify that bare connections from OmniGraph nodes to non-OmniGraph prims do not exist
            bare_connections = check_for_bare_connections(self.stage)
            if bare_connections:
                raise og.OmniGraphError(
                    "Deprecated connections from an OmniGraph node to a USD Prim not allowed with schema"
                    f" - {bare_connections}"
                )

            # First pass - change ComputeGraph/GlobalComputeGraph -> OmniGraph and ComputeNode -> OmniGraphNode
            return_values["Prim Types Changed"] = self.__change_prim_types_to_match_schema()

            # Second pass - if there are any OmniGraphNode or ComputeGraphSettings prims not in a graph,
            # create one and move them into it
            return_values["Root Prims Moved To Graph"] = self.__create_top_level_graph()

            # Third pass - move settings from their own prim to the parent graph prim
            if new_file_format_version is None:
                new_file_format_version = (1, 4)
            return_values["Settings Removed"] = self.__replace_settings_with_properties(new_file_format_version)

            # Now that the scene has been migrated the schema setting has to be enabled or bad things will happen.
            # Don't bother doing it if nothing changed though.
            if any(return_values.values()):
                carb.log_warn(
                    "Scene has migrated to use OmniGraph Schema - please save and reload. These changes were made:\n"
                    f"{return_values}"
                )

            return return_values
        except og.OmniGraphError as error:
            # If anything failed it would leave the graph in a hybrid state so try to restore it back to its original
            # state so that it remains stable.
            carb.log_error(str(error))
            for _i in range(self.__command_count):
                omni.kit.undo()
            return_values = {}

        return return_values


# ==============================================================================================================
# Handling for old files that did not use the OmniGraph schema (earlier than 1.3)
def update_to_include_schema(new_file_format_version: Optional[Tuple[int, int]] = None) -> Dict[str, Any]:
    """Update the current file to use the new schema.  See OmniGraphSchemaMigrator.update() for details

    Conversion of old scenes entails:
        - Changing any ComputeGraph or GlobalComputeGraph prims to be OmniGraph types
        - If a ComputeGraphSettings prim exists, migrating its attribute values to the OmniGraph prim
        - Changing any ComputeNode prims to be OmniGraphNode types
        - If any ComputeNode prims appear without a parent ComputeGraph create a default graph and move them into it

    Args:
        new_file_format_version: The file format version that should be used for the graph setting. If None then it will
                                 force the version immediately following the schema conversion (1, 4)

    Return:
        A dictionary of operations that were performed as part of the migration (key describes the operation, value
        is the objects to which it was applied)

    Raises:
        og.OmniGraphError if any of the attempted changes failed - will attempt to restore graph to original state
    """
    return OmniGraphSchemaMigrator().update()


# ==============================================================================================================
# Handling for old files that did not use the OmniGraph schema (earlier than 1.3)
def cb_update_to_include_schema(
    old_version: Optional[og.FileFormatVersion], new_version: Optional[og.FileFormatVersion], graph: Optional[og.Graph]
) -> Dict[str, Any]:
    """Callback invoked when a file is loaded to update old files to use the new schema.

    This will be called anytime a file is loaded with a non-current version. The old version and new version are
    checked to confirm that the values cross over the boundary when schemas were created, and if so then the schema
    information is applied to the file.

    Args:
        old_version: Version the file to upgrade uses
        new_version: Current file version expected
        graph: Graph to convert (only present for historical reasons - the entire stage is updated)

    Return:
        A dictionary of operations that were performed as part of the migration (key describes the operation, value
        is the objects to which it was applied)
    """
    # If the file format version is one of the ones that must contain schema prims no migration is needed
    if old_version is not None and (
        old_version.majorVersion > LAST_FILE_FORMAT_VERSION_WITHOUT_SCHEMA.majorVersion
        or (
            old_version.majorVersion == LAST_FILE_FORMAT_VERSION_WITHOUT_SCHEMA.majorVersion
            and old_version.minorVersion > LAST_FILE_FORMAT_VERSION_WITHOUT_SCHEMA.minorVersion
        )
    ):
        return {"message": f"File format version {old_version} already uses the schema"}

    return update_to_include_schema((new_version.majorVersion, new_version.minorVersion))
