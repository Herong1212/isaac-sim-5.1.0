# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""Provides a collection of commands for managing and manipulating prims within a Fabric stage."""

__all__ = [
    "DeleteFabricPrimsCommand",
    "MoveFabricPrimCommand",
    "MoveFabricPrimsCommand",
    "ToggleVisibilitySelectedFabricPrimsCommand",
    "CreateFabricPrimWithDefaultXformCommand",
    "CreateDefaultXformOnFabricPrimCommand",
    "CreateFabricPrimCommand",
    "GroupFabricPrimsCommand",
    "UngroupFabricPrimsCommand",
    "TransformFabricPrimCommand",
    "CopyFabricPrimCommand",
    "CopyFabricPrimsCommand",
    "ChangeFabricPropertyCommand",
    "ChangeFabricAttributeCommand",
]

from typing import Union, List, Optional, Callable, Dict, Any

import carb
import carb.settings
import omni.kit.commands
import omni.usd
import usdrt.Sdf
import usdrt.Usd
import usdrt.UsdGeom
import usdrt.Gf
import usdrt.Rt
import usdrt.UsdLux
import usdrt.Vt
import usdrt.hierarchy
from pxr import Sdf, UsdGeom, Usd
from omni.kit.primitive.mesh.evaluators import _get_all_evaluators
from . import utils
from .fabric_stage_helper import FabricStageHelper


PERSISTENT_SETTINGS_PREFIX = "/persistent"
SETTING_NESTED_GPRIMS_AUTHORING = "/persistent/app/stage/nestedGprimsAuthoring"


def post_notification(message: str, info: bool = False, duration: int = 3):
    """Posts a notification to the user interface.

    Args:
        message (str): The message to display in the notification.
        info (bool, optional): Set to True if the notification is informational; False for a warning. Defaults to False.
        duration (int, optional): The duration in seconds to show the notification. Defaults to 3."""
    try:
        import omni.kit.notification_manager as nm

        if info:
            type = nm.NotificationStatus.INFO
        else:
            type = nm.NotificationStatus.WARNING

        nm.post_notification(message, status=type, duration=duration)
    except Exception:
        pass


def allow_prim_parenting(stage: usdrt.Usd.Stage, path_from: str, path_to: str, action: str):
    """Checks if a prim can be parented under a given path and performs actions based on the stage settings.

    This function is used internally by commands that require parenting prims within the stage.

    Args:
        stage (usdrt.Usd.Stage): The Fabric stage where the parenting operation is to be performed.
        path_from (str): The path of the source prim that is being parented.
        path_to (str): The path under which the source prim will be parented.
        action (str): The action being performed, e.g., 'copy' or 'move'.

    Returns:
        usdrt.Usd.Prim or None: The source prim if parenting is allowed, otherwise None.
    """
    prim = stage.GetPrimAtPath(usdrt.Sdf.Path(path_from))
    if not prim or not prim.IsValid():
        return None

    settings = carb.settings.get_settings()
    supported = settings.get(SETTING_NESTED_GPRIMS_AUTHORING)
    if supported:
        return prim

    # Check if a usdrt.UsdGeom.Gprim exists in the desitionation hierarchy
    was_unparent = False
    path_to = usdrt.Sdf.Path(path_to)
    if not utils.is_ancestor_prim_type(stage, path_to, usdrt.UsdGeom.Gprim):
        # Check if the src is -somehow- an ancestor of another Gprim, and if so do not allow it
        if (action == "copy") or (
            not utils.is_ancestor_prim_type(stage, usdrt.Sdf.Path(path_from), usdrt.UsdGeom.Gprim)
        ):
            return prim

        was_unparent = True

    # Now check if the prim being moved (or any of its children are UsdGeom.Boundable)
    def _any_boundable_children(prim: usdrt.Usd.Prim):
        # Check immediate children
        children = prim.GetChildren()
        if any((child.IsA(usdrt.UsdGeom.Boundable) for child in children)):
            return True
        # Recurse
        if any((_any_boundable_children(child) for child in children)):
            return True
        return False

    if prim.IsA(usdrt.UsdGeom.Boundable) or _any_boundable_children(prim):
        msg = f"Cannot {action} fabric prim {path_from} to {path_to} as nested gprims are not supported."
        if was_unparent:
            msg += f"\n\nTo allow this in order to fix an existing scene set {SETTING_NESTED_GPRIMS_AUTHORING} to True"

        post_notification(msg)
        return None

    return prim


def get_all_descendent_prims(prim: usdrt.Usd.Prim):
    """Recursively finds all descendant prims of a given prim.

    Args:
        prim (usdrt.Usd.Prim): The prim to start the search from.

    Returns:
        List[usdrt.Usd.Prim]: A list of all descendant prims of the input prim.
    """
    # Recursively find all the children / grandchildren, etc. of given prim
    descendents = []
    children_prims: list[usdrt.Usd.Prim] = prim.GetChildren()

    if children_prims:
        descendents.extend(children_prims)
        for child in children_prims:
            child_children = get_all_descendent_prims(child)
            descendents.extend(child_children)

    return descendents


def get_all_properties_from_prim(prim: usdrt.Usd.Prim):
    """Collects information about a prim and its properties, including attributes and relationships.

    Args:
        prim (usdrt.Usd.Prim): The prim to collect information from.

    Returns:
        dict: A dictionary containing detailed information about the prim's path, type, schemas, attributes, and relationships.
    """
    prim_info = {}
    prim_info["path"] = prim.GetPath()
    prim_info["type"] = prim.GetTypeName()
    prim_info["schemas"] = prim.GetAppliedSchemas()

    # Collect attributes
    prim_info["attrs"] = []
    prim_attrs = prim.GetAttributes()
    for attr in prim_attrs:
        attr_info = {}
        attr_info["name"] = attr.GetName()
        attr_info["type"] = attr.GetTypeName()
        attr_info["value"] = attr.Get()

        if type(attr_info["value"]).__module__ == "usdrt.Vt._Vt":
            attr_info["value"] = list(attr_info["value"])
        prim_info["attrs"].append(attr_info)

    # Collect relationship
    prim_info["relationships"] = []
    relationships = prim.GetRelationships()
    for rel in relationships:
        rel_info = {}
        rel_info["name"] = rel.GetName()
        rel_info["targets"] = rel.GetTargets()

        prim_info["relationships"].append(rel_info)

    return prim_info


def create_prims_with_properties(stage: usdrt.Usd.Stage, prim_properties: dict, new_path: usdrt.Sdf.Path = None):
    """Creates one or more prims on the stage with specified properties.

    Args:
        stage (usdrt.Usd.Stage): The stage where the prims will be created.
        prim_properties (dict): A dictionary containing properties for the prim(s) to be created.
            This includes the prim path, type, schemas, attributes, and relationships.
        new_path (usdrt.Sdf.Path, optional): If provided, the new prim will be created at this path.
            Defaults to None, which means the prim path from prim_properties will be used.
    """
    if new_path:
        prim_path = new_path
    else:
        prim_path = prim_properties["path"]
    prim_type = prim_properties["type"]
    new_prim = stage.DefinePrim(prim_path, prim_type)

    if new_prim:
        for schema in prim_properties["schemas"]:
            existing_schemas = new_prim.GetAppliedSchemas()
            if schema not in existing_schemas:
                new_prim.AddAppliedSchema(schema)

        # Re-create attributes
        for attr_info in prim_properties["attrs"]:
            attr_name = attr_info["name"]
            attr_type = attr_info["type"]
            attr_value = attr_info["value"]

            if not new_prim.HasAttribute(attr_name):
                new_attr = new_prim.CreateAttribute(attr_name, attr_type, False)
            else:
                new_attr = new_prim.GetAttribute(attr_name)

            new_attr.Set(attr_value)

        # Re-create relationships
        for rel_info in prim_properties["relationships"]:
            rel_name = rel_info["name"]
            rel_targets = rel_info["targets"]

            if not new_prim.HasRelationship(rel_name):
                new_rel = new_prim.CreateRelationship(rel_name)
            else:
                new_rel = new_prim.GetRelationship(rel_name)

            new_rel.SetTargets(rel_targets)


class DeleteFabricPrimsCommand(omni.kit.commands.Command, FabricStageHelper):
    """A command for deleting prims from a Fabric stage.

    The command removes the specified prims and their descendants from the stage, if allowed by the current stage settings. It supports undo and redo operations.

    Args:
        paths: List[Union[str, usdrt.Sdf.Path]]
            The Fabric paths of the prims to be deleted.
        delete_descendents: bool
            Whether to delete descendants of the specified prims.
        stage: Optional[usdrt.Usd.Stage]
            The stage from which the prims will be deleted.
        context_name: Optional[str]
            The name of the context to use for the operation."""

    def __init__(
        self,
        paths: list[Union[str, usdrt.Sdf.Path]],
        delete_descendents: bool = True,
        stage: Optional[usdrt.Usd.Stage] = None,
        context_name: Optional[str] = None,
    ):
        """Creates a command to delete the specified Fabric prims."""
        FabricStageHelper.__init__(self, stage, context_name)

        self._delete_descendents = delete_descendents
        self._usd_context = self._get_context()
        self._selection = self._usd_context.get_selection()
        self._paths: list[usdrt.Sdf.Path] = []
        self._stage = self._get_stage()

        for path in paths:
            path = usdrt.Sdf.Path(path)
            if path == usdrt.Sdf.Path.absoluteRootPath:
                continue

            prim = self._stage.GetPrimAtPath(path)
            if prim:
                self._paths.append(path)
            else:
                carb.log_error(f"{str(path)} does not exist")

        if self._delete_descendents:
            # Paths in self._paths do not have parent/child relationship with each other
            self._paths = utils.remove_descendent_paths(self._paths)

        self._prev_selected_paths = list(self._selection.get_selected_prim_paths(omni.usd.Selection.SourceType.FABRIC))

    def do(self):
        """Executes the deletion of the specified Fabric prims."""
        # Remove paths that are about to be deleted from prev selected paths
        new_selected_paths = self._prev_selected_paths.copy()

        # Collect all the descendents of selected prims
        prims_to_delete = []
        for path in self._paths:
            prim = self._stage.GetPrimAtPath(path)
            prims_to_delete.append(prim)
            if self._delete_descendents:
                prims_to_delete.extend(get_all_descendent_prims(prim))

        # Store all the info and attributes of these prims
        self._descendent_properties = []
        for prim in prims_to_delete:
            prim_path_string = prim.GetPath().pathString
            if prim_path_string in new_selected_paths:
                new_selected_paths.remove(prim_path_string)

            self._descendent_properties.append(get_all_properties_from_prim(prim))

        self._selection.set_selected_prim_paths(new_selected_paths, False, omni.usd.Selection.SourceType.FABRIC)

        for props in self._descendent_properties:
            self._stage.RemovePrim(props["path"])

    def undo(self):
        """Undoes the deletion of the specified Fabric prims, restoring them to the stage."""
        # Rebuild all the prims and restore their attributes
        for prim_properties in self._descendent_properties:
            create_prims_with_properties(self._stage, prim_properties)

        # Reselect restored objects
        self._selection.set_selected_prim_paths(self._prev_selected_paths, False, omni.usd.Selection.SourceType.FABRIC)


class MoveFabricPrimCommand(omni.kit.commands.Command):
    """A command for moving a single prim from one path to another within the Fabric stage.

    This command updates the scene graph to reflect the new location of the prim and maintains its world transform if specified. The command supports undo and redo operations.

    Args:
        path_from: Union[str, usdrt.Sdf.Path]
            The source path from which the prim is to be moved.
        path_to: Union[str, usdrt.Sdf.Path]
            The target path to which the prim is to be moved to.
        time_code: usdrt.Usd.TimeCode
            The timecode at which the move operation is performed. Defaults to usdrt.Usd.TimeCode.Default().
        keep_world_transform: bool
            Whether to maintain the world transform of the prim after moving. Defaults to True.
        on_move_fn: Callable
            An optional callback function to be called after the move operation. Defaults to None
        stage_or_context: Union[str, usdrt.Usd.Stage, omni.usd.UsdContext]
            The stage or context where the prim is moved. Can be a stage instance, context instance, or context name. Defaults to None"""

    def __init__(
        self,
        path_from: Union[str, usdrt.Sdf.Path],
        path_to: Union[str, usdrt.Sdf.Path],
        time_code: usdrt.Usd.TimeCode = usdrt.Usd.TimeCode.Default(),
        keep_world_transform: bool = True,
        on_move_fn: Callable = None,
        stage_or_context: Union[str, usdrt.Usd.Stage, omni.usd.UsdContext] = None,
    ):
        """Creates a command to move a Fabric prim from one path to another."""
        self._path_from = usdrt.Sdf.Path(path_from)
        usd_context, stage = self.__get_context_and_stage(stage_or_context)
        self._usd_context = usd_context
        self._stage = stage
        if self._usd_context:
            self._selection = self._usd_context.get_selection()

        self._path_to = usdrt.Sdf.Path(utils.get_stage_next_free_path(self._stage, path_to, False))
        self._time_code = time_code
        self._keep_world_transform = keep_world_transform
        self._moved = False
        self._on_move_fn = on_move_fn
        self._delete_command = None

    def __get_context_and_stage(self, stage_or_context):
        def get_fabric_stage_from_usd_context(context):
            stage_id = context.get_stage_id()
            return usdrt.Usd.Stage.Attach(stage_id)

        if stage_or_context is None:
            usd_context = omni.usd.get_context()
            stage = get_fabric_stage_from_usd_context(usd_context)
        elif isinstance(stage_or_context, usdrt.Usd.Stage):
            stage = stage_or_context
            stage_id = stage.GetStageId()
            usd_context = omni.usd.get_context_from_stage_id(stage_id)
        elif isinstance(stage_or_context, omni.usd.UsdContext):
            usd_context = stage_or_context
            stage = get_fabric_stage_from_usd_context(stage_or_context)
        elif isinstance(stage_or_context, str):
            usd_context = omni.usd.get_context(stage_or_context)
            if not usd_context:
                raise ValueError(f"Invalid context given for `{stage_or_context}`.")
            stage = get_fabric_stage_from_usd_context(usd_context)
        else:
            raise ValueError("Invalid param given for `stage_or_context`.")

        return usd_context, stage

    def _move(self, path_from: usdrt.Sdf.Path, path_to: usdrt.Sdf.Path, is_undo: bool):
        # TODO: replace with usdrt.Sdf.Path.IsValidPathString when OM-105470 is done.
        if not Sdf.Path.IsValidPathString(path_to.pathString):
            carb.log_error(f"Invalid path: {str(path_to)}")
            return

        stage = self._stage
        stage_id = stage.GetStageIdAsStageId()
        fabric_id = stage.GetFabricId()
        hier = usdrt.hierarchy.IFabricHierarchy().get_fabric_hierarchy(fabric_id, stage_id)

        prim = allow_prim_parenting(stage, path_from.GetString(), path_to.GetString(), "move")
        if prim:
            # NOTE: skip checking prim deletable, fabric prim has no metadata
            old_world_matrices = {}
            if self._keep_world_transform and path_from.GetParentPath() != path_to.GetParentPath():
                # NOTE: usdrt.Usd.PrimRange currenly does not support Fabric only prims
                prim_range_it = iter(usdrt.Usd.PrimRange(prim))
                pruned_paths: list[usdrt.Sdf.Path] = []

                for sub_prim in prim_range_it:
                    is_pruned = False
                    for pruned_path in pruned_paths:
                        common_prefix = pruned_path.GetCommonPrefix(sub_prim.GetPath())
                        if common_prefix == pruned_path:
                            is_pruned = True
                            break

                    if is_pruned:
                        continue

                    if sub_prim.IsA(usdrt.UsdGeom.Xformable):
                        old_world_mtx = hier.get_world_xform(sub_prim.GetPath())
                        new_path = sub_prim.GetPath().ReplacePrefix(path_from, path_to)
                        old_world_matrices[new_path] = old_world_mtx

                        # Skip all its children
                        pruned_paths.append(sub_prim.GetPath())

            was_default_prim = stage.GetDefaultPrim() == prim
            if self._selection:
                was_selected = self._selection.is_prim_path_selected(
                    path_from.GetString(), omni.usd.Selection.SourceType.FABRIC
                )
            else:
                was_selected = False

            if was_selected:
                # Remove from selection
                self._selection.set_prim_path_selected(
                    path_to.GetString(), False, False, False, True, omni.usd.Selection.SourceType.FABRIC
                )

            # Store all properties of this prim and its descendants
            descendant_prims = [prim]
            descendant_prims.extend(get_all_descendent_prims(prim))

            prim_properties = [get_all_properties_from_prim(descendant_prim) for descendant_prim in descendant_prims]

            # Rebuild prim with new paths
            for prim_property in prim_properties:
                new_path = prim_property["path"].ReplacePrefix(path_from, path_to)
                create_prims_with_properties(stage, prim_property, new_path)

            self._moved = True

            if len(old_world_matrices):
                # Maintain world xform
                new_prim = stage.GetPrimAtPath(path_to)
                if not new_prim:
                    return

                for path, mtx in old_world_matrices.items():
                    if not usdrt.Gf.IsClose(mtx, hier.get_world_xform(new_prim.GetPath()), 1e-2):
                        cmd = TransformFabricPrimCommand(path=path, new_transform_matrix=mtx, time_code=self._time_code)
                        cmd.do()

            # Remove original prim and its decendents, deleting parent won't delete its children in Fabric
            for prim in descendant_prims:
                stage.RemovePrim(prim.GetPath())

            if was_selected and self._selection:
                self._selection.set_prim_path_selected(
                    path_to.GetString(), True, False, False, True, omni.usd.Selection.SourceType.FABRIC
                )

            # NOTE: skip setting default prim if "was_default_prim" is True as metadata is not supported in Fabric

            if self._on_move_fn:
                try:
                    self._on_move_fn(path_from, path_to)
                except:
                    carb.log_warn("error in MoveFabricPrimCommand on_move_fn")

    def do(self):
        """Executes the command to move the specified Fabric prim to the new location."""
        carb.log_info(f"Moving fabric prim from {self._path_from} to {self._path_to}")
        self._move(self._path_from, self._path_to, False)

    def undo(self):
        """Undoes the move of the specified Fabric prims, restoring them to the previous location"""
        if self._moved:
            carb.log_info(f"Undo Move fabric prim from {self._path_to} to {self._path_from}")
            self._move(self._path_to, self._path_from, True)


class MoveFabricPrimsCommand(omni.kit.commands.Command):
    """A command for moving multiple prims within a Fabric stage.

    This command allows multiple prims to be moved to new locations, updating the scene graph accordingly. Supports undo and redo.

    Args:
        paths_to_move: (Dict[str, str])
            A dictionary containing path mappings from source to destination.
        time_code: (usdrt.Usd.TimeCode, optional)
            The timecode at which the move operation is performed. Defaults to usdrt.Usd.TimeCode.Default().
        keep_world_transform: (bool, optional)
            If set to True, the world transform of the prims is maintained after moving. Defaults to True.
        on_move_fn: (Callable, optional)
            An optional callback function to be called after the move operation. Defaults to None.
        stage_or_context (Union[str, usdrt.Usd.Stage, omni.usd.UsdContext], optional)
            The stage or context to which the changes are applied. It can be a stage instance, context instance, or context name. By default, it will apply the changes to the stage in the default context."""

    def __init__(
        self,
        paths_to_move: Dict[str, str],
        time_code: usdrt.Usd.TimeCode = usdrt.Usd.TimeCode.Default(),
        keep_world_transform: bool = True,
        on_move_fn: Callable = None,
        stage_or_context: Union[str, usdrt.Usd.Stage, omni.usd.UsdContext] = None,
    ):
        """Creates a command for moving multiple Fabric prims to new locations."""
        self._paths_to_move = paths_to_move
        self._time_code = time_code
        self._keep_world_transform = keep_world_transform
        self._on_move_fn = on_move_fn
        self._stage_or_context = stage_or_context

    def do(self):
        """Executes the move of multiple prims."""
        for src, dst in self._paths_to_move.items():
            omni.kit.commands.execute(
                "MoveFabricPrim",
                path_from=src,
                path_to=dst,
                time_code=self._time_code,
                keep_world_transform=self._keep_world_transform,
                on_move_fn=self._on_move_fn,
                stage_or_context=self._stage_or_context,
            )

    def undo(self):
        """Undoes the move of multiple prims."""
        pass


class ToggleVisibilitySelectedFabricPrimsCommand(omni.kit.commands.Command):
    """Toggles the visibility of the selected Fabric prims.

    Args:
        selected_paths (List[str]): The Fabric paths of the selected prims.
        stage (Optional[usdrt.Usd.Stage]): The stage where the prims exist. If not provided, the default stage is used.
    """

    def __init__(self, selected_paths: List[str], stage: Optional[usdrt.Usd.Stage] = None):
        """Toggles the visibility of the selected prims."""
        stage_id = omni.usd.get_context().get_stage_id()
        self._stage = stage or usdrt.Usd.Stage.Attach(stage_id)
        self._selected_paths = [usdrt.Sdf.Path(path) for path in selected_paths]

    def _toggle_visibility(self):
        """Internal method to toggle the visibility attribute of the selected prims."""
        for selected_path in self._selected_paths:
            selected_prim = self._stage.GetPrimAtPath(selected_path)
            if not selected_prim:
                continue

            vis_attr = selected_prim.GetAttribute("_worldVisibility")
            if not vis_attr:
                vis_attr = selected_prim.CreateAttribute("_worldVisibility", usdrt.Sdf.ValueTypeNames.Bool, False)
                vis_attr.Set(True)

            visibility = vis_attr.Get()

            if visibility:
                vis_attr.Set(False)
            else:
                vis_attr.Set(True)

    def do(self):
        """Executes the toggle visibility command on the selected prims."""
        self._toggle_visibility()

    def undo(self):
        """Undoes the toggle visibility command, restoring the original visibility states of the selected prims."""
        self._toggle_visibility()


class CreateFabricPrimWithDefaultXformCommand(omni.kit.commands.Command, FabricStageHelper):
    """A command to create a Fabric prim with a default transform.

    This command creates a new prim of the specified type, at the given path, and applies a default transform to it. The newly created prim can be automatically selected.

    Args:
        prim_type: str
            The type of prim to create (e.g., 'Sphere', 'Cube').
        prim_path: str
            The path where the prim will be created. If None, it will be placed at the stage root or under default prim using the type name.
        select_new_prim: bool
            Indicates whether to select the prim after creation.
        attributes: Dict[str, Any]
            Optional dictionary of attributes to set after creation.
        create_default_xform: bool
            Determines whether to create default transform attributes for the prim.
        stage: Optional[usdrt.Usd.Stage]
            The stage where the prim will be created. If not provided, the default stage is used.
        context_name: Optional[str]
            The name of the context to use for the operation. If not provided, the default context is used."""

    attr_type_table = {
        "radius": usdrt.Sdf.ValueTypeNames.Double,
        "height": usdrt.Sdf.ValueTypeNames.Double,
        "size": usdrt.Sdf.ValueTypeNames.Double,
        "extent": usdrt.Sdf.ValueTypeNames.Range3d,
        "focalLength": usdrt.Sdf.ValueTypeNames.Float,
        "focusDistance": usdrt.Sdf.ValueTypeNames.Float,
        "clippingRange": usdrt.Sdf.ValueTypeNames.Float2,
        "inputs:intensity": usdrt.Sdf.ValueTypeNames.Float,
        "inputs:length": usdrt.Sdf.ValueTypeNames.Float,
        "inputs:radius": usdrt.Sdf.ValueTypeNames.Float,
        "inputs:angle": usdrt.Sdf.ValueTypeNames.Float,
        "inputs:width": usdrt.Sdf.ValueTypeNames.Float,
        "inputs:height": usdrt.Sdf.ValueTypeNames.Float,
        "inputs:texture:format": usdrt.Sdf.ValueTypeNames.Token,
        "auralMode": usdrt.Sdf.ValueTypeNames.Token,
    }

    default_size_attr_table = {
        "Capsule": {
            "height": 50.0,
            "radius": 25.0,
            "extent": usdrt.Gf.Range3d(usdrt.Gf.Vec3d(-25, -50, -25), usdrt.Gf.Vec3d(25, 50, 25)),
        },
        "Cone": {
            "height": 100.0,
            "radius": 50.0,
            "extent": usdrt.Gf.Range3d(usdrt.Gf.Vec3d(-50, -50, -50), usdrt.Gf.Vec3d(50, 50, 50)),
        },
        "Cube": {"size": 100.0, "extent": usdrt.Gf.Range3d(usdrt.Gf.Vec3d(-50, -50, -50), usdrt.Gf.Vec3d(50, 50, 50))},
        "Cylinder": {
            "height": 100.0,
            "radius": 50.0,
            "extent": usdrt.Gf.Range3d(usdrt.Gf.Vec3d(-50, -50, -50), usdrt.Gf.Vec3d(50, 50, 50)),
        },
        "Sphere": {"radius": 50, "extent": usdrt.Gf.Range3d(usdrt.Gf.Vec3d(-50, -50, -50), usdrt.Gf.Vec3d(50, 50, 50))},
        "Default": {"extent": usdrt.Gf.Range3d(usdrt.Gf.Vec3d(), usdrt.Gf.Vec3d())},
    }

    def __init__(
        self,
        prim_type: str,
        prim_path: str = None,
        select_new_prim: bool = True,
        attributes: Dict[str, Any] = {},
        create_default_xform=True,
        stage: Optional[usdrt.Usd.Stage] = None,
        context_name: Optional[str] = None,
    ):
        """A command to create a Fabric prim with a default transform."""
        FabricStageHelper.__init__(self, stage, context_name)
        self._prim_type = prim_type
        self._prim_path = prim_path
        if attributes is None:
            self._attributes = {}
        else:
            self._attributes = omni.usd.gather_default_attributes(prim_type.lower())
            # Handle divergent setting for "Camera" created as "orthographic"
            if prim_type == "Camera" and attributes.get("projection") == "orthographic":
                self._attributes.update(omni.usd.gather_default_attributes("orthoCamera"))
            self._attributes.update(attributes)

        if prim_type in CreateFabricPrimWithDefaultXformCommand.default_size_attr_table:
            self._attributes.update(CreateFabricPrimWithDefaultXformCommand.default_size_attr_table[prim_type])
        else:
            self._attributes.update(CreateFabricPrimWithDefaultXformCommand.default_size_attr_table["Default"])
        self._selection = self._get_context().get_selection()
        self._select_new_prim = select_new_prim
        self._settings = carb.settings.get_settings()
        self._create_default_xform = create_default_xform
        self._move_commands = []

    def do(self):
        """Executes the command to create a new Fabric prim with default transform.

        If the prim already exists at the specified path, the command will fail and log an error."""
        stage = self._get_stage()
        path = self._prim_path or utils.get_stage_next_free_path(stage, "/" + self._prim_type, True)

        prim = stage.DefinePrim(path, self._prim_type)

        self._set_refinement_level(prim, stage)
        self._create_light_extra(prim, stage)
        self._create_camera_extra(prim, stage)

        # Set properties
        for attr_name in self._attributes:
            if attr_name == "extent":
                # "_worldExtent" attribute is required for FSD
                boundable = usdrt.Rt.Boundable(prim)
                extent_attr = boundable.CreateWorldExtentAttr()
                extent_attr.Set(self._attributes["extent"])

            else:
                attr = prim.GetAttribute(attr_name)
                if not attr:
                    attr_type = CreateFabricPrimWithDefaultXformCommand.attr_type_table.get(attr_name, None)
                    attr = prim.CreateAttribute(attr_name, attr_type, False)

                attr.Set(self._attributes[attr_name])

        self._prim_path = prim.GetPath().GetString()
        # Select the created prim.
        if self._select_new_prim:
            self._selection.set_prim_path_selected(path, True, True, True, True, omni.usd.Selection.SourceType.FABRIC)

        # Ensure axis influenced geometry prims are adjusted based on stage upAxis
        if prim.IsA(usdrt.UsdGeom.Cylinder) or prim.IsA(usdrt.UsdGeom.Capsule) or prim.IsA(usdrt.UsdGeom.Cone):
            axis_attr = prim.GetAttribute(usdrt.UsdGeom.Tokens.axis)
            if not axis_attr:
                axis_attr = prim.CreateAttribute(usdrt.UsdGeom.Tokens.axis, usdrt.Sdf.ValueTypeNames.Token, True)
            usd_stage = self._get_usd_stage()
            axis_attr.Set(UsdGeom.GetStageUpAxis(usd_stage))

        if prim.IsA(usdrt.UsdGeom.Xformable) and self._create_default_xform:
            create_xform_cmd = CreateDefaultXformOnFabricPrimCommand(prim_path=self._prim_path, stage=stage)
            create_xform_cmd.do()

    def undo(self):
        """Undoes the creation of the new Fabric prim, effectively deleting it from the stage."""
        delete_cmd = DeleteFabricPrimsCommand([self._prim_path], stage=self._get_stage())
        delete_cmd.do()

    def _create_light_extra(self, prim: usdrt.Usd.Prim, stage: usdrt.Usd.Stage):
        if (
            prim.IsA(usdrt.UsdLux.CylinderLight)
            or prim.IsA(usdrt.UsdLux.DiskLight)
            or prim.IsA(usdrt.UsdLux.DistantLight)
            or prim.IsA(usdrt.UsdLux.DomeLight)
            or prim.IsA(usdrt.UsdLux.GeometryLight)
            or prim.IsA(usdrt.UsdLux.RectLight)
            or prim.IsA(usdrt.UsdLux.SphereLight)
        ):
            light_api = usdrt.UsdLux.LightAPI(prim)
            light_api.CreateCollectionLightLinkIncludeRootAttr()
            light_api.CreateCollectionShadowLinkIncludeRootAttr()
            # TODO: This doesn't work color_attr = light_api.CreateColorAttr()
            color_attr = prim.CreateAttribute("inputs:color", usdrt.Sdf.ValueTypeNames.Vector3f, False)
            color_attr.Set(usdrt.Gf.Vec3f(1, 1, 1))
            color_temp_attr = light_api.CreateColorTemperatureAttr()
            color_temp_attr.Set(6500)
            diff_attr = light_api.CreateDiffuseAttr()
            diff_attr.Set(1.0)
            light_api.CreateEnableColorTemperatureAttr()
            light_api.CreateExposureAttr()
            light_api.CreateFiltersRel()
            light_api.CreateIntensityAttr()
            light_api.CreateNormalizeAttr()
            spec_attr = light_api.CreateSpecularAttr()
            spec_attr.Set(1.0)

            if prim.IsA(usdrt.UsdLux.CylinderLight):
                treat_as_line_attr = prim.CreateAttribute("treatAsLine", usdrt.Sdf.ValueTypeNames.Bool, False)
                treat_as_line_attr.Set(False)

            shaping_api = usdrt.UsdLux.ShapingAPI(prim)
            cone_angle_attr = shaping_api.CreateShapingConeAngleAttr()
            cone_angle_attr.Set(180)
            shaping_api.CreateShapingConeSoftnessAttr()
            shaping_api.CreateShapingFocusAttr()
            shaping_api.CreateShapingFocusTintAttr()
            shaping_api.CreateShapingIesAngleScaleAttr()
            shaping_api.CreateShapingIesFileAttr()
            shaping_api.CreateShapingIesNormalizeAttr()

    def _create_camera_extra(self, prim: usdrt.Usd.Prim, stage: usdrt.Usd.Stage):
        if prim.IsA(usdrt.UsdGeom.Camera):
            cam = usdrt.UsdGeom.Camera(prim)
            clip_range_attr = prim.GetAttribute("clippingRange")
            if not clip_range_attr:
                clip_range_attr = cam.CreateClippingRangeAttr()

            clip_range_attr.Set((1, 1e07))
            horizontal_aperture_attr = cam.CreateHorizontalApertureAttr()
            horizontal_aperture_attr.Set(20.954999923706055)

            cam.CreateHorizontalApertureOffsetAttr()
            cam.CreateExposureAttr()
            cam.CreateFStopAttr()

            vertical_aperture_attr = cam.CreateVerticalApertureAttr()
            vertical_aperture_attr.Set(15.290800094604492)

            cam.CreateVerticalApertureOffsetAttr()
            cam.CreateShutterCloseAttr()
            cam.CreateShutterOpenAttr()

            stereo_attr = cam.CreateStereoRoleAttr()
            stereo_attr.Set("mono")

            projection_attr = cam.CreateProjectionAttr()
            projection_attr.Set("perspective")

            cam.CreateClippingPlanesAttr()

    def _set_refinement_level(self, prim, stage):
        if (
            prim.IsA(usdrt.UsdGeom.Cylinder)
            or prim.IsA(usdrt.UsdGeom.Capsule)
            or prim.IsA(usdrt.UsdGeom.Cone)
            or prim.IsA(usdrt.UsdGeom.Sphere)
        ) and self._settings.get(PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/highQuality"):
            prim.CreateAttribute("refinementEnableOverride", usdrt.Sdf.ValueTypeNames.Bool, True).Set(True)
            prim.CreateAttribute("refinementLevel", usdrt.Sdf.ValueTypeNames.Int, True).Set(2)


class CreateFabricPrimCommand(CreateFabricPrimWithDefaultXformCommand):
    """A command to create a Fabric prim with a default transform.

    This command creates a new prim of the specified type, at the given path, and applies a default transform to it. The newly created prim can be automatically selected.

    Args:
        prim_type: str
            The type of prim to create (e.g., 'Sphere', 'Cube').
        prim_path: Optional[str]
            The path where the prim will be created. If None, it will be placed at the stage root or under default prim using the type name.
        select_new_prim: bool
            Indicates whether to select the prim after creation.
        attributes: Optional[Dict[str, Any]]
            Optional dictionary of attributes to set after creation.
        create_default_xform: bool
            Determines whether to create default transform attributes for the prim.
        stage: Optional[usdrt.Usd.Stage]
            The stage where the prim will be created. If not provided, the default stage is used.
        context_name: Optional[str]
            The name of the context to use for the operation. If not provided, the default context is used."""

    def __init__(
        self,
        prim_type: str,
        prim_path: str = None,
        select_new_prim: bool = True,
        attributes: Dict[str, Any] = {},
        create_default_xform=True,
        stage: Optional[usdrt.Usd.Stage] = None,
        context_name: Optional[str] = None,
    ):
        """Initializes a command to create a Fabric prim with a default transform."""
        super().__init__(prim_type, prim_path, select_new_prim, attributes, create_default_xform, stage, context_name)


class CreateFabricPrimsCommand(omni.kit.commands.Command):
    """A command for creating Fabric prims.

    This command takes a list of prim types and creates corresponding prims on the Fabric stage.

    Args:
        prim_types: List[str]
            List of prim types to create, e.g., ['Sphere', 'Cone'].
        usd_context_name: Optional[str]
            Name of the USD context to operate in. Defaults to None, which uses the default context."""

    def __init__(self, prim_types: List[str], usd_context_name: Optional[str] = None):
        """Initializes a command to create multiple Fabric prim."""
        self._prim_types = prim_types
        self._usd_context_name = usd_context_name

    def do(self):
        """Executes the command to create a list of Fabric prims from corresponding prim types"""
        for p in self._prim_types:
            omni.kit.commands.execute("CreateFabricPrim", prim_type=p, context_name=self._usd_context_name)

    def undo(self):
        """Undoes the creation of the list of Fabric prims."""
        pass


class CreateFabricMeshPrimWithDefaultXform(omni.kit.commands.Command):
    """A command to create a Fabric mesh prim with a default transform.

    This command supports creating various mesh shapes with default transformations and additional
    parameters to fine-tune the mesh's appearance and placement in the scene."""

    def __init__(self, prim_type: str, **kwargs):
        """Creates a Fabric mesh prim with a default transform.

        Args:
            prim_type (str): The type of prim to create. Supports 'Plane', 'Sphere', 'Cone', 'Cylinder', 'Disk', 'Torus', and 'Cube'.
            **kwargs: Additional keyword arguments for prim creation, including:
                object_origin (usdrt.Gf.Vec3f): The position of the mesh center.
                u_patches (int): The number of patches to tessellate in the U direction.
                v_patches (int): The number of patches to tessellate in the V direction.
                w_patches (int): The number of patches to tessellate in the W direction, applicable to 'Cone', 'Cylinder', and 'Cube'.
                half_scale (float): Half the size of the mesh. Defaults to None.
                u_verts_scale (int): Tessellation level multiplier for the U direction.
                v_verts_scale (int): Tessellation level multiplier for the V direction.
                w_verts_scale (int): Tessellation level multiplier for the W direction, affects caps tessellation for 'Cone' and 'Cylinder', and Z-axis tessellation for 'Cube'.
                above_ground (bool): If True, offsets the mesh center above the ground plane if 'object_origin' is not provided. Defaults to False.
        """

        self._prim_type = prim_type[0:1].upper() + prim_type[1:].lower()
        self._usd_context = omni.usd.get_context(kwargs.get("context_name", ""))
        stage_id = self._usd_context.get_stage_id()
        self._selection = self._usd_context.get_selection()
        self._usd_stage = self._usd_context.get_stage()
        self._stage = usdrt.Usd.Stage.Attach(stage_id)
        self._settings = carb.settings.get_settings()
        self._default_path = kwargs.get("prim_path", None)
        self._select_new_prim = kwargs.get("select_new_prim", True)
        self._prepend_default_prim = kwargs.get("prepend_default_prim", True)
        self._above_ground = kwargs.get("above_ground", False)

        self._attributes = {**kwargs}
        # Supported mesh types should have an associated evaluator class
        self._evaluator_class = _get_all_evaluators()[prim_type]
        assert isinstance(self._evaluator_class, type)

    def do(self):
        """Execute the command to create a Fabric mesh prim with a default transform."""
        self._prim_path = None
        if self._default_path:
            path = utils.get_stage_next_free_path(self._stage, self._default_path, self._prepend_default_prim)
        else:
            path = utils.get_stage_next_free_path(self._stage, "/" + self._prim_type, self._prepend_default_prim)

        mesh = usdrt.UsdGeom.Mesh.Define(self._stage, usdrt.Sdf.Path(path))

        prim = mesh.GetPrim()
        up_axis = UsdGeom.GetStageUpAxis(self._usd_stage)
        self._attributes["up_axis"] = up_axis

        half_scale = self._attributes.get("half_scale", None)
        if half_scale is None or half_scale <= 0.0:
            half_scale = self._evaluator_class.get_default_half_scale()

        object_origin = self._attributes.get("object_origin", None)
        if object_origin is None and self._above_ground:
            # To move the mesh above the ground.
            if self._prim_type != "Disk" and self._prim_type != "Plane":
                if self._prim_type != "Torus":
                    offset = half_scale
                else:
                    # The tube of torus is half of the half_scale.
                    offset = half_scale / 2.0

                if up_axis == "Y":
                    object_origin = usdrt.Gf.Vec3d(0.0, offset, 0.0)
                else:
                    object_origin = usdrt.Gf.Vec3d(0.0, 0.0, offset)
            else:
                object_origin = usdrt.Gf.Vec3d(0.0)
        elif isinstance(object_origin, list):
            object_origin = usdrt.Gf.Vec3d(*object_origin)
        else:
            object_origin = usdrt.Gf.Vec3d(0.0)

        default_translate = usdrt.Gf.Vec3d(object_origin)
        default_scale = usdrt.Gf.Vec3d(1.0, 1.0, 1.0)
        default_orient = usdrt.Gf.Quatd(1.0, usdrt.Gf.Vec3d(0.0, 0.0, 0.0))

        translate_mtx = usdrt.Gf.Matrix4d().SetTranslate(default_translate)
        scale_mtx = usdrt.Gf.Matrix4d().SetScale(default_scale)
        rot_mtx = usdrt.Gf.Matrix4d().SetRotate(default_orient)

        world_mtx = scale_mtx * rot_mtx * translate_mtx

        if not prim.HasAttribute("omni:fabric:localMatrix"):
            local_matrix_attr = prim.CreateAttribute(
                "omni:fabric:localMatrix", usdrt.Sdf.ValueTypeNames.Matrix4d, False
            )
            local_matrix_attr.Set(usdrt.Gf.Matrix4d(1))

        if not prim.HasAttribute("omni:fabric:worldMatrix"):
            world_matrix_attr = prim.CreateAttribute(
                "omni:fabric:worldMatrix", usdrt.Sdf.ValueTypeNames.Matrix4d, False
            )
            world_matrix_attr.Set(usdrt.Gf.Matrix4d(1))

        stage_id = self._stage.GetStageIdAsStageId()
        fabric_id = self._stage.GetFabricId()
        hier = usdrt.hierarchy.IFabricHierarchy().get_fabric_hierarchy(fabric_id, stage_id)
        hier.set_world_xform(usdrt.Sdf.Path(path), world_mtx)

        self._prim_path = path
        if self._select_new_prim:
            self._selection.set_prim_path_selected(path, True, False, True, True, omni.usd.Selection.SourceType.FABRIC)

        self._define_mesh(mesh)
        return self._prim_path

    def undo(self):
        """Undoes the creation of the new Fabric mesh prim, effectively deleting it from the stage"""
        if self._prim_path:
            self._stage.RemovePrim(self._prim_path)

    def _define_mesh(self, mesh):
        evaluator = self._evaluator_class(self._attributes)
        prim = mesh.GetPrim()

        points = []
        normals = []
        sts = []
        point_indices = []
        face_vertex_counts = []

        points, normals, sts, point_indices, face_vertex_counts = evaluator.eval(**self._attributes)

        units = UsdGeom.GetStageMetersPerUnit(self._usd_stage)
        if usdrt.Gf.IsClose(units, 0.0, 1e-6):
            units = 0.01

        # Scale points to make sure it's already in centimeters
        scale = 0.01 / units
        points = [point * scale for point in points]

        # Set points
        points_attr = mesh.CreatePointsAttr()
        points_attr.Set(usdrt.Vt.Vec3fArray(points))

        # Set normals and interpolation
        normal_attr = prim.CreateAttribute("primvars:normals", usdrt.Sdf.ValueTypeNames.Float3Array, False)
        normal_attr.Set(usdrt.Vt.Vec3fArray(normals))

        normal_interpo_attr = prim.CreateAttribute(
            "primvars:normals:interpolation", usdrt.Sdf.ValueTypeNames.Token, False
        )
        normal_interpo_attr.Set("faceVarying")

        # Set face vertex indices
        face_vertex_indices_attr = mesh.CreateFaceVertexIndicesAttr()
        face_vertex_indices_attr.Set(point_indices)

        # Set face vertex counts
        face_vertex_counts_attr = mesh.CreateFaceVertexCountsAttr()
        face_vertex_counts_attr.Set(face_vertex_counts)

        face_varying_interpo_attr = mesh.CreateFaceVaryingLinearInterpolationAttr()
        face_varying_interpo_attr.Set("cornersPlus1")

        interpo_boundary_attr = mesh.CreateInterpolateBoundaryAttr()
        interpo_boundary_attr.Set("edgeAndCorner")

        sts_primvar = prim.CreateAttribute("primvars:st", usdrt.Sdf.ValueTypeNames.TexCoord2fArray, False)
        sts_primvar.Set(usdrt.Vt.Vec2fArray(sts))

        subd_attr = mesh.CreateSubdivisionSchemeAttr()
        subd_attr.Set("none")

        boundable = usdrt.Rt.Boundable(prim)
        extent_attr = boundable.CreateWorldExtentAttr()
        bounds = utils.compute_extent_from_points(prim)
        extent_attr.Set(bounds)

        # set the new prim as the active selection
        if self._select_new_prim:
            self._selection.set_selected_prim_paths(
                [prim.GetPath().pathString], False, omni.usd.Selection.SourceType.FABRIC
            )


class CreateDefaultXformOnFabricPrimCommand(omni.kit.commands.Command):
    """A command to create and apply a default transform to a Fabric prim at a specified path.

    Args:
        prim_path: str
            The Fabric path where the prim is located.
        stage: usdrt.Usd.Stage
            The stage where the prim resides."""

    def __init__(self, prim_path: str, stage: usdrt.Usd.Stage):
        """Creates and applies a default transform to a Fabric prim."""
        self._prim_path = prim_path
        self._stage = stage
        self._usd_context = omni.usd.get_context()
        self._settings = carb.settings.get_settings()
        self._added_attributes = []
        self._old_world_mtx_value = None

        stage_id = self._stage.GetStageIdAsStageId()
        fabric_id = self._stage.GetFabricId()
        self._hier = usdrt.hierarchy.IFabricHierarchy().get_fabric_hierarchy(fabric_id, stage_id)

    def do(self):
        """Executes the command to create and apply a default transform to a Fabric prim at a specified path."""
        self._added_attributes.clear()

        usd_stage = self._usd_context.get_stage()
        prim = self._stage.GetPrimAtPath(self._prim_path)
        if not prim or not prim.IsA(usdrt.UsdGeom.Xformable):
            return

        is_prim_created_with_default_xform = self._settings.get(
            PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/PrimCreationWithDefaultXformOps"
        )
        if not is_prim_created_with_default_xform:
            return

        default_translate = usdrt.Gf.Vec3d(0.0, 0.0, 0.0)
        default_translate_mtx = usdrt.Gf.Matrix4d().SetTranslate(default_translate)

        default_scale = usdrt.Gf.Vec3d(1.0, 1.0, 1.0)
        default_scale_mtx = usdrt.Gf.Matrix4d().SetScale(default_scale)

        default_euler = self._get_default_euler_angle(prim, usd_stage, usdrt.Gf.Vec3d)
        rotation = (
            usdrt.Gf.Rotation(usdrt.Gf.Vec3d.XAxis(), default_euler[0])
            * usdrt.Gf.Rotation(usdrt.Gf.Vec3d.YAxis(), default_euler[1])
            * usdrt.Gf.Rotation(usdrt.Gf.Vec3d.ZAxis(), default_euler[2])
        )
        quat = rotation.GetQuat()
        default_rot_mtx = usdrt.Gf.Matrix4d().SetRotate(quat)

        default_world_mtx = default_scale_mtx * default_rot_mtx * default_translate_mtx

        if not prim.HasAttribute("omni:fabric:worldMatrix"):
            world_matrix_attr = prim.CreateAttribute(
                "omni:fabric:worldMatrix", usdrt.Sdf.ValueTypeNames.Matrix4d, False
            )
            world_matrix_attr.Set(usdrt.Gf.Matrix4d(1))
            self._added_attributes.append("omni:fabric:worldMatrix")
        else:
            self._old_world_mtx_value = self._hier.get_world_xform(prim.GetPath())

        if not prim.HasAttribute("omni:fabric:localMatrix"):
            local_matrix_attr = prim.CreateAttribute(
                "omni:fabric:localMatrix", usdrt.Sdf.ValueTypeNames.Matrix4d, False
            )
            local_matrix_attr.Set(usdrt.Gf.Matrix4d(1))
            self._added_attributes.append("omni:fabric:localMatrix")

        self._hier.set_world_xform(prim.GetPath(), default_world_mtx)

    def undo(self):
        """Undoes the default transform to the Fabric prim."""
        prim = self._stage.GetPrimAtPath(self._prim_path)
        if not prim:
            self._added_attributes.clear()
            self._old_world_mtx_value = None
            return

        if self._old_world_mtx_value is not None:
            self._hier.set_world_xform(prim.GetPath(), self._old_world_mtx_value)

        for attr_name in self._added_attributes:
            prim.RemoveProperty(attr_name)

    def _get_default_euler_angle(self, prim, usd_stage, vector_type):
        """
        rotation specified as if applied in XYZ order
        """
        up_axis = UsdGeom.GetStageUpAxis(usd_stage)
        if prim.IsA(usdrt.UsdLux.DistantLight):
            if up_axis == "Y":
                return vector_type(315.0, 0.0, 0.0)
            else:
                return vector_type(45.0, 0.0, 90)
        elif prim.IsA(usdrt.UsdLux.DomeLight):
            if up_axis == "Y":
                return vector_type(270.0, 0.0, 0.0)
        elif (
            prim.IsA(usdrt.UsdLux.SphereLight)
            or prim.IsA(usdrt.UsdLux.CylinderLight)
            or prim.IsA(usdrt.UsdLux.DiskLight)
            or prim.IsA(usdrt.UsdLux.RectLight)
            or prim.IsA(usdrt.UsdGeom.Camera)
        ):
            if up_axis == "Z":
                return vector_type(90.0, 0.0, 90.0)

        return vector_type(0.0, 0.0, 0.0)


class CopyFabricPrimCommand(omni.kit.commands.Command):
    """A command to copy a Fabric prim to a new location.

    This command is used to duplicate a specified Fabric prim and place it under a new path within the same stage. It supports undo and redo operations.

    Args:
        path_from: str
            The source path of the Fabric prim to copy.
        path_to: Optional[str]
            The destination path for the copied prim. If None, a new unique path is generated.
        exclusive_select: bool
            If True, the copied prim will be exclusively selected; otherwise, it won't affect the selection.
        usd_context_name: str
            The name of the USD context. Defaults to an empty string, which uses the default context."""

    def __init__(self, path_from: str, path_to: str = None, exclusive_select: bool = True, usd_context_name: str = ""):
        """Creates a CopyFabricPrimCommand to copy a Fabric prim to a new location."""
        self._usd_context = omni.usd.get_context(usd_context_name)
        self._selection = self._usd_context.get_selection()
        stage = self._get_stage()
        if not path_to:
            path_to = utils.get_stage_next_free_path(stage, path_from, False)
        else:
            path_to = utils.get_stage_next_free_path(stage, path_to, False)

        self._path_from = path_from
        self._path_to = path_to
        self._exclusive_select = exclusive_select

    def _get_stage(self):
        stage_id = self._usd_context.get_stage_id()
        return usdrt.Usd.Stage.Attach(stage_id)

    def do(self):
        """Executes the command to copy a Fabric prim to a new location."""
        self._copied = False
        stage = self._get_stage()
        usd_prim = allow_prim_parenting(stage, self._path_from, self._path_to, "copy")
        if not usd_prim:
            return

        # collect prim properties
        prim_descendants = [usd_prim]
        prim_descendants.extend(get_all_descendent_prims(usd_prim))

        prim_props = [get_all_properties_from_prim(prim) for prim in prim_descendants]

        for prim_prop in prim_props:
            prim_path = prim_prop["path"]
            new_prim_path = prim_path.ReplacePrefix(self._path_from, self._path_to)
            create_prims_with_properties(stage, prim_prop, new_prim_path)

        self._copied = True

        # Select the copied prim
        self._selection.set_prim_path_selected(
            self._path_to, True, False, self._exclusive_select, True, omni.usd.Selection.SourceType.FABRIC
        )

    def undo(self):
        """Undoes the copy a Fabric prim to a new location, effectively deleting it from the stage. """
        if self._copied:
            delete_cmd = DeleteFabricPrimsCommand([self._path_to], stage=self._get_stage())
            delete_cmd.do()


class CopyFabricPrimsCommand(omni.kit.commands.Command):
    """A command for copying and pasting Fabric prims within a stage.

    This command duplicates one or more Fabric prims to new locations within the same Fabric stage, preserving their properties and relationships. It supports undo and redo capabilities.

    Args:
        paths_from (list[str]): The source paths of the prims to copy.
        paths_to (list[str], optional): The destination paths for the copied prims. If `None` or length smaller than paths_from, then the next free path is generated for missing paths.
    """

    def __init__(self, paths_from: list[str], paths_to: list[str] = None):
        """Creates a command for copying multiple Fabric prims to new locations."""
        self._selection = omni.usd.get_context().get_selection()
        self._paths_from = paths_from.copy()
        self._paths_to = paths_to.copy() if paths_to is not None else None

    def do(self):
        """Executes the command to copy multiple Fabric prims to the specified new locations."""
        self._previously_selected_paths = self._selection.get_selected_prim_paths(omni.usd.Selection.SourceType.FABRIC)
        self._selection.clear_selected_prim_paths(omni.usd.Selection.SourceType.FABRIC)
        for i in range(len(self._paths_from)):
            path_to = self._prim_to[i] if (self._paths_to is not None and i < len(self._paths_to)) else None
            omni.kit.commands.execute(
                "CopyFabricPrim", path_from=self._paths_from[i], path_to=path_to, exclusive_select=False
            )

    def undo(self):
        """Undoes the copy operation, effectively removing the copied prims."""
        if self._previously_selected_paths:
            self._selection.set_selected_prim_paths(
                self._previously_selected_paths, False, omni.usd.Selection.SourceType.FABRIC
            )


class GroupFabricPrimsCommand(omni.kit.commands.Command, FabricStageHelper):
    """A command to group multiple Fabric prims under a new Xform prim.

    This command creates a new 'group' Xform prim at the common parent path of the specified prims and moves the prims under this new parent. It is useful for organizing prims in the scene hierarchy. Supports undo and redo operations.

    Args:
        prim_paths (List[str]): Prim paths that will be grouped.
        stage (usdrt.Usd.Stage): Stage to operate. Optional.
        context_name (str): The usd context to operate. Optional.
    """

    def __init__(
        self,
        prim_paths: List[Union[str, Sdf.Path]],
        stage: Optional[usdrt.Usd.Stage] = None,
        context_name: Optional[str] = None,
    ):
        """Create a command to group multiple Fabric prims under a new Xform prim."""
        FabricStageHelper.__init__(self, stage, context_name)

        # Filter out empty and absolute root path
        self._prim_paths = []
        self._stage = self._get_stage()
        self._all_path_prefix = usdrt.Sdf.Path.emptyPath

        for path in prim_paths:
            sdf_path = usdrt.Sdf.Path(path)
            prim = self._stage.GetPrimAtPath(sdf_path)
            if not prim:
                continue

            if sdf_path and sdf_path != usdrt.Sdf.Path.absoluteRootPath:
                parent_path = sdf_path.GetParentPath()
                if self._all_path_prefix == usdrt.Sdf.Path.emptyPath:
                    self._all_path_prefix = parent_path
                else:
                    self._all_path_prefix = self._all_path_prefix.GetCommonPrefix(parent_path)
                self._prim_paths.append(sdf_path)

        if self._all_path_prefix == usdrt.Sdf.Path.emptyPath:
            self._all_path_prefix = usdrt.Sdf.Path.absoluteRootPath

        self._prim_paths = utils.remove_descendent_paths(self._prim_paths)
        self._move_commands = []
        self._group_prim_path = None

    def do(self):
        """Groups a set of prims under a new Xform prim.

        Parameters:
            prim_paths (List[Union[str, Sdf.Path]]): Prim paths that will be grouped.
            stage (Optional[usdrt.Usd.Stage], optional): Stage to operate. Defaults to None, which uses the default stage.
            context_name (Optional[str], optional): The USD context to operate. Defaults to None, which uses the default context.
        """
        self._move_commands = []
        if not self._prim_paths:
            return

        path = self._all_path_prefix.AppendChild("Group")
        group_prim_path = utils.get_stage_next_free_path(self._stage, path.GetString(), False)
        self._group_prim_path = usdrt.Sdf.Path(group_prim_path)
        group_xform = usdrt.UsdGeom.Xform.Define(self._stage, self._group_prim_path)

        # NOTE: skipped setting Kind.Tokens.group here, which is not supported by usdrt

        self._create_group_xform_impl(self._stage, group_xform, self._prim_paths)
        selection = self._get_context().get_selection()
        selection.set_prim_path_selected(group_prim_path, True, False, True, True, omni.usd.Selection.SourceType.FABRIC)

    def undo(self):
        """Undoes the grouping operation, effectively ungrouping the prims."""
        for command in reversed(self._move_commands):
            command.undo()

        if self._group_prim_path:
            delete_cmd = DeleteFabricPrimsCommand([self._group_prim_path], stage=self._stage)
            delete_cmd.do()

    def _set_group_xform(self, prim, world_extent):
        centroid = world_extent.GetMidpoint()
        world_mtx = usdrt.Gf.Matrix4d().SetTranslate(centroid)

        if not prim.HasAttribute("omni:fabric:localMatrix"):
            local_mtx_attr = prim.CreateAttribute("omni:fabric:localMatrix", usdrt.Sdf.ValueTypeNames.Matrix4d, False)
            local_mtx_attr.Set(usdrt.Gf.Matrix4d(1))

        if not prim.HasAttribute("omni:fabric:worldMatrix"):
            world_mtx_attr = prim.CreateAttribute("omni:fabric:worldMatrix", usdrt.Sdf.ValueTypeNames.Matrix4d, False)
            world_mtx_attr.Set(usdrt.Gf.Matrix4d(1))

        stage_id = self._stage.GetStageIdAsStageId()
        fabric_id = self._stage.GetFabricId()
        hier = usdrt.hierarchy.IFabricHierarchy().get_fabric_hierarchy(fabric_id, stage_id)
        hier.set_world_xform(prim.GetPath(), world_mtx)

    def _create_group_xform_impl(self, stage, group_prim, selected_prim_paths):
        new_paths = {}
        name_index = {}
        xform_extent = usdrt.Gf.Range3d()

        for prim_path in selected_prim_paths:
            prim = stage.GetPrimAtPath(prim_path)
            if not prim:
                continue

            boundable = usdrt.Rt.Boundable(prim)
            world_extent_attr = boundable.GetWorldExtentAttr()
            if world_extent_attr:
                world_extent = world_extent_attr.Get()
                xform_extent.UnionWith(world_extent)

            move_to = group_prim.GetPrimPath().AppendChild(prim_path.name)
            index = name_index.get(move_to, -1)
            if index != -1:
                name_index[move_to] += 1
                move_to = group_prim.GetPrimPath().AppendChild(prim_path.name + "_" + str(index))
            else:
                name_index[move_to] = 0

            move_prim_command = MoveFabricPrimCommand(
                path_from=prim_path, path_to=move_to, keep_world_transform=False, stage_or_context=self._get_stage()
            )
            move_prim_command.do()

            if move_prim_command._moved:
                self._move_commands.append(move_prim_command)
                new_paths[prim_path] = move_to

        self._set_group_xform(group_prim.GetPrim(), xform_extent)


class UngroupFabricPrimsCommand(omni.kit.commands.Command, FabricStageHelper):
    """A command to ungroup Fabric prims from their common parent group.

    This command moves the specified prims from under their group parent prim to the parent path of the group prim. It is useful for flattening the scene hierarchy as needed.

    Args:
        prim_paths (List[str]): Prim paths that will be grouped.
        stage (usdrt.Usd.Stage): Stage to operate. Optional.
        context_name (str): The usd context to operate. Optional.
    """

    def __init__(
        self,
        prim_paths: List[Union[str, usdrt.Sdf.Path]],
        stage: Optional[usdrt.Usd.Stage] = None,
        context_name: Optional[str] = None,
    ):
        """Initializes a command to ungroup Fabric prims from their common parent group"""
        FabricStageHelper.__init__(self, stage, context_name)

        # Filter out empty and absolute root path
        stage = self._get_stage()
        self._group_prim_path = None
        self._new_paths = []

        for path in prim_paths:
            sdf_path = usdrt.Sdf.Path(path)
            prim = stage.GetPrimAtPath(sdf_path)
            if not prim:
                continue

            group_prim = prim
            # NOTE: Skipped checking if prim is group Kind here as Fabric doesn't support it

            if group_prim and group_prim.IsValid():
                if not self._group_prim_path:
                    self._group_prim_path = group_prim.GetPath()
                    break

    def do(self):
        """Ungroups the specified Fabric prims from their parent group prim.

        The prims will be moved to the parent path of the group prim.

        If there are no prims specified or the group prim is not valid, the command does nothing."""
        if not self._group_prim_path:
            return

        self._prim_paths_in_group = []
        self._new_paths = []
        new_target_path = self._group_prim_path.GetParentPath()
        stage = self._get_stage()
        group_prim = stage.GetPrimAtPath(self._group_prim_path)

        for child in group_prim.GetChildren():
            prim_path = child.GetPath()
            move_to = new_target_path.AppendChild(child.GetName())
            move_prim_command = MoveFabricPrimCommand(
                path_from=prim_path, path_to=move_to, keep_world_transform=False, stage_or_context=stage
            )
            move_prim_command.do()

            # Have to access internal state to make sure it's executed
            if move_prim_command._moved:
                self._new_paths.append(move_to.GetString())

        delete_command = DeleteFabricPrimsCommand([self._group_prim_path], self._get_stage())
        delete_command.do()

        selection = self._get_context().get_selection()
        selection.set_selected_prim_paths(self._new_paths, True, omni.usd.Selection.SourceType.FABRIC)

    def undo(self):
        """Restores the original group structure by regrouping the previously ungrouped prims.

        Recreates the group prim that was deleted during the do() action and moves the prims back under it."""
        group_command = GroupFabricPrimsCommand(prim_paths=self._new_paths)
        group_command.do()


class TransformFabricPrimCommand(omni.kit.commands.Command):
    """A command to transform a Fabric prim.

    This command applies a specified transformation matrix to a Fabric prim at a given path. It can operate in either world or local space and supports undo/redo operations.

    Args:
        path: str
            Prim path.
        new_transform_matrix: usdrt.Gf.Matrix4d
            New local/world transform matrix.
        old_transform_matrix: usdrt.Gf.Matrix4d
            Optional old local/world transform matrix to undo to. If `None` use current transform.
        is_world_xform: bool
            Whether the transformation is applied in world space (True) or local space (False). Defaults to False.
        time_code: usdrt.Usd.TimeCode
            The timecode at which the transformation is applied. Defaults to usdrt.Usd.TimeCode.Default().
        usd_context_name: str
            The name of the USD context the command operates within. Defaults to an empty string, which uses the default context."""

    def __init__(
        self,
        path: str,
        new_transform_matrix: usdrt.Gf.Matrix4d,
        old_transform_matrix: usdrt.Gf.Matrix4d = None,
        is_world_xform: bool = False,
        time_code: usdrt.Usd.TimeCode = usdrt.Usd.TimeCode.Default(),
        usd_context_name: str = "",
    ):
        """Creates a TransformFabricPrimCommand to perform transformations on a Fabric prim.

        Args:
            path (str): The path to the Fabric prim to transform.
            new_transform_matrix (usdrt.Gf.Matrix4d): A 4x4 transformation matrix specifying the new transformation.
            old_transform_matrix (usdrt.Gf.Matrix4d, optional): The original transformation matrix before the transformation.
        """
        carb.log_verbose("init Fabric Transform Command")
        self._new_transform_matrix = new_transform_matrix
        self._path = usdrt.Sdf.Path(path)
        self._old_transform_matrix = old_transform_matrix
        self._is_world_xform = is_world_xform
        self._time_code = time_code
        self._usd_context_name = usd_context_name
        self._stage = self._get_stage()

        stage_id = self._stage.GetStageIdAsStageId()
        fabric_id = self._stage.GetFabricId()
        self._hier = usdrt.hierarchy.IFabricHierarchy().get_fabric_hierarchy(fabric_id, stage_id)

        if self._old_transform_matrix is None:
            if self._is_world_xform:
                self._old_transform_matrix = self._hier.get_world_xform(self._path)
            else:
                self._old_transform_matrix = self._hier.get_local_xform(self._path)

    def _get_stage(self):
        usd_stage_id = omni.usd.get_context(self._usd_context_name).get_stage_id()
        return usdrt.Usd.Stage.Attach(usd_stage_id)

    def _set_transform_matrix(self, xform_mtx: usdrt.Gf.Matrix4d, time_code):
        if self._is_world_xform:
            self._hier.set_world_xform(self._path, xform_mtx)
        else:
            self._hier.set_local_xform(self._path, xform_mtx)

    def do(self):
        """Executes the command to transform a Fabric prim."""
        self._set_transform_matrix(self._new_transform_matrix, self._time_code)

    def undo(self):
        """Undoes the transformation of the Fabric prim, effectively reset the prim to the old transformation"""
        self._set_transform_matrix(self._old_transform_matrix, self._time_code)


class ChangeFabricPropertyCommand(omni.kit.commands.Command):
    """
    Change prim property undoable **Command**.

    Args:
        prop_path (str): Prim property path.
        value (Any): Value to change to.
        prev (Any): Value to undo to.
        timecode (usdrt.Usd.TimeCode): The timecode to set property value to.
        type_to_create_if_not_exist (usdrt.Sdf.ValueTypeName): If not None AND property does not already exist, a new property will be created with given type and value.
        usd_context_name (Union[str, Usd.Stage]): Union that could be:
                        * Name of the usd context to work on. Leave to "" to use default USD context.
                        * Instance of UsdContext.
                        * Or stage instance.
        is_custom (bool): If the property is created, specifiy if it is a 'custom' property (not part of the Schema).
    """

    def __init__(
        self,
        prop_path: str,
        value: Any,
        prev: Any,
        timecode=usdrt.Usd.TimeCode.Default(),
        type_to_create_if_not_exist: usdrt.Sdf.ValueTypeNames = None,
        usd_context_name: Union[str, omni.usd.UsdContext, Usd.Stage, usdrt.Usd.Stage] = "",
        is_custom: bool = False,
    ):
        "Create a command to change prim property."
        self._value = value
        self._prev = prev
        self._prop_path = usdrt.Sdf.Path(prop_path)
        self._time_code = timecode
        self._type_to_create_if_not_exist = type_to_create_if_not_exist

        if isinstance(usd_context_name, omni.usd.UsdContext):
            stage_id = usd_context_name.get_stage_id()
            self._stage = usdrt.Usd.Stage.Attach(stage_id)
        elif isinstance(usd_context_name, usdrt.Usd.Stage):
            self._stage = usd_context_name
        elif isinstance(usd_context_name, Usd.Stage):
            stage_id = omni.usd.get_context_from_stage(usd_context_name).get_stage_id()
            self._stage = usdrt.Usd.Stage.Attach(stage_id)
        else:
            stage_id = omni.usd.get_context(usd_context_name).get_stage_id()
            self._stage = usdrt.Usd.Stage.Attach(stage_id)

        self._new_property = False
        self._new_time_code = False
        self._do_executed = False
        self.__is_custom = is_custom

    def do(self):
        """Executes the command to change the specified Fabric property to a new value.

        This method updates the property value and can create a new property if it does not exist and a type is specified.
        """
        self._do_executed = False

        prim_path = self._prop_path.GetAbsoluteRootOrPrimPath()
        prim = self._stage.GetPrimAtPath(prim_path)
        if not prim:
            carb.log_error(f"Failed to change property {self._prop_path} as fabric prim does not exist.")
            return

        # TODO: usdrt.Usd.Stage.GetAttributeAtPath() does not work with fabric only prim
        prop_name = self._prop_path.GetNameToken()
        prop = prim.GetAttribute(prop_name)

        if not prop:
            if self._type_to_create_if_not_exist is not None:
                prop = prim.CreateAttribute(self._prop_path.name, self._type_to_create_if_not_exist, self.__is_custom)
                if prop:
                    self._new_property = True

        if prop:
            if self._prev is None:
                self._prev = prop.Get(self._time_code)

            self._new_time_code = self._time_code != usdrt.Usd.TimeCode.Default()
            prop.Set(self._value, self._time_code)

            self._do_executed = True

    def undo(self):
        """Undoes the property change, reverting the property value to its previous state.

        If the property was created during the execution of the `do` method, this method will remove the property."""
        if not self._do_executed:
            return

        prop_name = self._prop_path.GetNameToken()
        prim_path = self._prop_path.GetAbsoluteRootOrPrimPath()
        prim = self._stage.GetPrimAtPath(prim_path)
        prop = prim.GetAttribute(prop_name)
        if self._new_property:
            prim.RemoveProperty(prop_name)

        else:
            if prop:
                # NOTE: skipped clearing attr at time because it't not supported
                prop.Set(self._prev, self._time_code)


class ChangeFabricAttributeCommand(omni.kit.commands.Command):
    """
    Change fabric prim attribute undoable **Command**.

    Args:
        attr_path (usdrt.Sdf.Path): Prim attribute path.
        value (Any): Value to change to.
        prev (Any): Value to undo to.
        timecode (usdrt.Usd.TimeCode): The timecode to set attribute value to.
        type_to_create_if_not_exist (usdrt.Sdf.ValueTypeName): If not None AND attribute does not already exist, a new attribute will be created with given type and value.
        stage (usdrt.Usd.Stage): The current Fabric stage.
        is_custom (bool): If the attribute is created, specify if it is a 'custom' attribute (not part of the Schema).
    """

    def __init__(
        self,
        attr_path: str,
        value: Any,
        prev: Any,
        timecode=usdrt.Usd.TimeCode.Default(),
        type_to_create_if_not_exist: usdrt.Sdf.ValueTypeNames = None,
        stage: usdrt.Usd.Stage = None,
        is_custom: bool = False,
    ):
        "Create a command to change prim attribute."
        self._value = value
        self._prev = prev
        self._attr_path = attr_path
        self._time_code = timecode
        self._type_to_create_if_not_exist = type_to_create_if_not_exist
        self._stage = stage

        self._new_attribute = False
        self._do_executed = False
        self.__is_custom = is_custom

    def _set_attr_val(self, attr: usdrt.Usd.Attribute, val: Any, time_code=usdrt.Usd.TimeCode.Default()):
        # Add support to set Gf.Matrix4X, Gf.QuatX using python tuple
        attr_type = attr.GetTypeName()
        if attr_type == usdrt.Sdf.ValueTypeNames.Matrix4d and isinstance(val, tuple):
            attr.Set(usdrt.Gf.Matrix4d(*val), time_code)
        elif attr_type == usdrt.Sdf.ValueTypeNames.Quath and isinstance(val, tuple):
            attr.Set(usdrt.Gf.Quath(*val), time_code)
        elif attr_type == usdrt.Sdf.ValueTypeNames.Quatf and isinstance(val, tuple):
            attr.Set(usdrt.Gf.Quatf(*val), time_code)
        elif attr_type == usdrt.Sdf.ValueTypeNames.Quatd and isinstance(val, tuple):
            attr.Set(usdrt.Gf.Quatd(*val), time_code)
        elif attr_type == usdrt.Sdf.ValueTypeNames.Int2 and isinstance(val, tuple):
            attr.Set(usdrt.Gf.Vec2i(int(val[0]), int(val[1])), time_code)
        else:
            attr.Set(val, time_code)

    def do(self):
        """Executes the command to change the specified Fabric attribute to a new value.\n\nThis method updates the attribute value and can create a new attribute if it does not exist and a type is specified."""
        self._do_executed = False
        # Get attribute
        attr = self._stage.GetAttributeAtPath(self._attr_path)
        if not attr:
            if self._type_to_create_if_not_exist is not None:
                prim_path = self._attr_path.GetAbsoluteRootOrPrimPath()
                prim = self._stage.GetPrimAtPath(prim_path)
                attr = prim.CreateAttribute(self._attr_path.name, self._type_to_create_if_not_exist, self.__is_custom)
                if attr:
                    self._new_attribute = True

        if attr:
            if self._prev is None:
                self._prev = attr.Get(self._time_code)

            self._set_attr_val(attr, self._value, self._time_code)
            self._do_executed = True

    def undo(self):
        """Undoes the attribute change, reverting the attribute value to its previous state.\n\nIf the attribute was created during the execution of the `do` method, this method will remove the attribute."""
        if not self._do_executed:
            return

        if self._new_attribute:
            attribute_spec = self._stage.GetAttributeAtPath(self._attr_path)
            if attribute_spec:
                prim_path = self._attr_path.GetAbsoluteRootOrPrimPath()
                prim_spec = self._stage.GetPrimAtPath(prim_path)
                prim_spec.Removeattribute(attribute_spec)
        else:
            attr = self._stage.GetAttributeAtPath(self._attr_path)
            if attr:
                self._set_attr_val(attr, self._prev, self._time_code)
