# Copyright (c) 2018-2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import math
import os
import weakref
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union

import carb
import carb.profiler
import carb.settings
import omni.kit.commands
import omni.timeline
import omni.usd
import omni.client
from omni.kit.usd_undo import UsdEditTargetUndo

from pxr import Gf, Tf, Kind, Sdf, Sdr, Trace, Usd, UsdGeom, UsdLux, UsdShade
from .stage_helper import UsdStageHelper
import OmniAudioSchema

SETTING_NESTED_GPRIMS_AUTHORING = "/persistent/app/stage/nestedGprimsAuthoring"


def should_keep_children_order():
    """Internal. Whether it should keep children order after prim is renamed or removed."""

    SETTINGS_KEEP_CHILDREN_ORDER = "/persistent/ext/omni.usd/keep_children_order"
    return carb.settings.get_settings().get(SETTINGS_KEEP_CHILDREN_ORDER)


def move_prim_to_location(stage: Usd.Stage, prim_path: Sdf.Path, location: int, old_name: str = None):
    """Internal. Moves prim to specific location of its parent."""

    parent_path = prim_path.GetParentPath()
    parent_prim = stage.GetPrimAtPath(parent_path)
    if not parent_prim:
        return

    all_children = parent_prim.GetAllChildrenNames()
    total_children = len(all_children)
    name = prim_path.name
    if name in all_children:
        index = all_children.index(name)
        all_children.remove(name)
        if index == location:
            return
    else:
        if old_name and old_name in all_children:
            index = all_children.index(old_name)
            all_children.remove(old_name)
        else:
            index = -1

    if location < 0 or location > total_children:
        location = -1
    elif location > index and index != -1:
        # If it's to move from up to down.
        location -= 1

    all_children.insert(location, name)
    # Use Sdf API so it can be batched.
    parent_prim_spec = Sdf.CreatePrimInLayer(stage.GetRootLayer(), parent_path)
    parent_prim_spec.nameChildrenOrder = all_children


def get_child_position_in_the_parent(stage: Usd.Stage, prim_path: Sdf.Path):
    """Internal. Gets the index of the prim inside its parent."""

    parent_path = prim_path.GetParentPath()
    parent_prim = stage.GetPrimAtPath(parent_path)
    if parent_prim and stage.GetPrimAtPath(prim_path):
        all_children = parent_prim.GetAllChildrenNames()
        return all_children.index(prim_path.name)

    return -1


def get_context_and_stage(stage_or_context: Union[str, Usd.Stage, omni.usd.UsdContext]):
    """Internal. Returns instances of UsdContext and UsdStage based on the union argument."""

    if stage_or_context is None:
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
    elif isinstance(stage_or_context, Usd.Stage):
        usd_context = omni.usd.get_context_from_stage(stage_or_context)
        if not usd_context:
            raise ValueError(f"Invalid context given for `{stage_or_context}`.")
        stage = stage_or_context
    elif isinstance(stage_or_context, omni.usd.UsdContext):
        usd_context = stage_or_context
        stage = usd_context.get_stage()
    elif isinstance(stage_or_context, str):
        usd_context = omni.usd.get_context(stage_or_context)
        if not usd_context:
            raise ValueError(f"Invalid context given for `{stage_or_context}`.")
        stage = usd_context.get_stage()
    else:
        raise ValueError("Invalid param given for `stage_or_context`.")

    return usd_context, stage


def post_notification(message: str, info: bool = False, duration: int = 3):
    """Internal. Posts notification if omni.kit.notification_manager is enabled."""

    try:
        import omni.kit.notification_manager as nm

        if info:
            type = nm.NotificationStatus.INFO
        else:
            type = nm.NotificationStatus.WARNING

        return nm.post_notification(message, status=type, duration=duration)
    except Exception:
        pass

    return None


def active_edit_context(usd_context_or_stage):
    """Internal. Utility to return active edit context.
    By default, it will return the current edit target. When it's in auto-authoring mode,
    it will return the edit context of the default layer. You can refer to :mod:`omni.kit.usd.layers`
    for more details about auto-authoring.
    """

    if usd_context_or_stage is None:
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
    elif isinstance(usd_context_or_stage, omni.usd.UsdContext):
        usd_context = usd_context_or_stage
        stage = usd_context.get_stage()
    elif isinstance(usd_context_or_stage, Usd.Stage):
        usd_context = omni.usd.get_context_from_stage(usd_context_or_stage)
        stage = usd_context_or_stage
    else:
        raise ValueError("Invalid argument passed.")

    if usd_context:
        # It's possible that stage is in auto-authoring. When it's in auto-authoring,
        # the edit target will be pointed to the auto-authoring layer always. In order to
        # reduce the work to copy from auto-authoring layer to the target layer, this utility
        # will temporarily switch the edit target from auto-authoring layer to the target
        # layer so the changes will not be made firstly to auto-authoring layer, then copy.
        try:
            import omni.kit.usd.layers as layers

            return layers.active_authoring_layer_context(usd_context)
        except Exception:
            pass

    # Returns default edit context.
    edit_target = stage.GetEditTarget()
    return Usd.EditContext(stage, edit_target.GetLayer())


def remove_prim_spec(layer: Sdf.Layer, prim_spec_path: str):
    """Internal. Removes prim spec from layer."""

    prim_spec = layer.GetPrimAtPath(prim_spec_path)
    if not prim_spec:
        return False

    if prim_spec.nameParent:
        name_parent = prim_spec.nameParent
    else:
        name_parent = layer.pseudoRoot

    if not name_parent:
        return False

    name = prim_spec.name
    if name in name_parent.nameChildren:
        del name_parent.nameChildren[name]

    return True


def prim_can_be_removed_without_destruction(usd_context_or_stage, prim_path):
    """
    Internal. A destructive remove is one that will not only edit current edit target, \
    but also other non-anonymous layers. Why anonymous layers is not counted is because \
    anonymous layers are writable in Kit, and it's only existed when it's a new \
    stage or under session layer. Any deltas inside those anonymous layers can be safely \
    removed. Otherwise, this function will return false, which means it will not remove \
    prim specs in all layers, but deactivates them to avoid editing non-anonymous layers except \
    current edit target.
    """

    if isinstance(usd_context_or_stage, omni.usd.UsdContext):
        stage = usd_context_or_stage.get_stage()
    elif isinstance(usd_context_or_stage, Usd.Stage):
        stage = usd_context_or_stage
    else:
        raise ValueError("Invalid argument passed.")

    usd_prim = stage.GetPrimAtPath(prim_path)
    if not usd_prim:
        return True

    # If it's under reference, it cannot be removed non-destructively.
    if omni.usd.check_ancestral(usd_prim):
        return False

    with active_edit_context(stage):
        edit_target = stage.GetEditTarget()
        current_layer = edit_target.GetLayer()
        layer_stack = stage.GetLayerStack()

        has_delta_in_non_anonymous_layer = False
        for layer in layer_stack:
            prim_spec = layer.GetPrimAtPath(prim_path)
            if not prim_spec:
                continue

            if layer != current_layer and not layer.anonymous and not has_delta_in_non_anonymous_layer:
                has_delta_in_non_anonymous_layer = True

    return not has_delta_in_non_anonymous_layer


def write_refinement_override_enabled_hint(stage):
    """Internal. If the user authors refinementEnableOverride, drop a hint in customLayerData
    that we can use to enable/disable the checking for override attributes
    in the scene delegate (i.e., assuaging Pixar's concern that even assets
    that do not opt into per-mesh refinement must check for their presence at load
    time).

    The hint also gives us a numerical value that we can use to maintain
    backwards compatibility, as it is almost certain that the attributes and
    the value resolution logic governing this override behavior will be revisted,
    i.e., also encodable in a more high-level enum like Complexity setting in
    usdview, which could also be an attribute than lives on any prim, not just
    meshes, and whose behavior would inherit down namespace.
    """

    custom_data = stage.GetEditTarget().GetLayer().customLayerData
    custom_data["refinementOverrideImplVersion"] = 0
    stage.GetEditTarget().GetLayer().customLayerData = custom_data


def get_default_rotation_order_str():
    """Internal. Gets default rotation order from setting /persistent/app/primCreation/DefaultRotationOrder. """

    return carb.settings.get_settings().get("/persistent/app/primCreation/DefaultRotationOrder")


def get_default_camera_rotation_order_str():
    """Internal. Gets default camera rotation order from setting /persistent/app/primCreation/DefaultCameraRotationOrder. """

    return carb.settings.get_settings().get("/persistent/app/primCreation/DefaultCameraRotationOrder")


def get_default_rotation_order_type(is_camera: bool = False):
    """Internal. Gets default rotation order."""

    if is_camera:
        default_rotation_order = get_default_camera_rotation_order_str()
    else:
        default_rotation_order = get_default_rotation_order_str()
    type_dict = {
        "XYZ": UsdGeom.XformOp.TypeRotateXYZ,
        "XZY": UsdGeom.XformOp.TypeRotateXZY,
        "YXZ": UsdGeom.XformOp.TypeRotateYXZ,
        "YZX": UsdGeom.XformOp.TypeRotateYZX,
        "ZXY": UsdGeom.XformOp.TypeRotateZXY,
        "ZYX": UsdGeom.XformOp.TypeRotateZYX,
    }
    return type_dict.get(default_rotation_order, UsdGeom.XformOp.TypeRotateXYZ)


def ensure_parents_are_active(stage, path):
    """
    Internal. It will ensure parents are active. If they are not, it will change the active
    flag into active, and all of their children will be marked to inacitve.
    This is normally used when it's to create materials under /World/Looks, as it's
    possible /World/Looks is deactivated. While creating a prim under an inactive parent
    will throw exceptions by USD.
    """

    # OM-70901
    prim_path = Sdf.Path(path)
    prefixes = prim_path.GetParentPath().GetPrefixes()
    for prefix in prefixes:
        parent = stage.GetPrimAtPath(prefix)
        if not parent:
            return

        if parent.IsActive():
            continue

        parent.SetActive(True)
        with Sdf.ChangeBlock():
            for child in parent.GetAllChildren():
                child.SetActive(False)


def allow_prim_parenting(stage: Usd.Stage, path_from: str, path_to: str, action: str):
    """Internal. Checkes if parenting a prim to a target location is allowed."""

    prim = stage.GetPrimAtPath(path_from)
    if not prim:
        return None

    settings = carb.settings.get_settings()
    supported = settings.get(SETTING_NESTED_GPRIMS_AUTHORING)
    if supported:
        return prim

    # Check if a UsdGeom.Gprim exists in the desitionation hierarchy
    was_unparent = False
    path_to = Sdf.Path(path_to)
    if not omni.usd.is_ancestor_prim_type(stage, path_to, UsdGeom.Gprim):
        # Check if the src is -somehow- an ancestor of another Gprim, and if so do not allow it
        # This is to avoid Hydra issues that do not account for such removals
        if (action == "copy") or (not omni.usd.is_ancestor_prim_type(stage, Sdf.Path(path_from), UsdGeom.Gprim)):
            # There is still the case that illegaly nested Gprims exist underneath path_from, but the test
            # for that could be performance instensive and should be done on-open, not here.
            return prim

        was_unparent = True

    # Now check if the prim being moved (or any of its children are UsdGeom.Boundable)
    def _any_boundable_children(prim: Usd.Prim):
        # Check immediate children
        children = prim.GetChildren()
        if any((child.IsA(UsdGeom.Boundable) for child in children)):
            return True
        # Recurse
        if any((_any_boundable_children(child) for child in children)):
            return True
        return False

    if prim.IsA(UsdGeom.Boundable) or _any_boundable_children(prim):
        msg = f"Cannot {action} prim {path_from} to {path_to} as nested gprims are not supported."
        if was_unparent:
            msg += f"\n\nTo allow this in order to fix an existing scene set {SETTING_NESTED_GPRIMS_AUTHORING} to True"

        post_notification(msg)
        return None

    return prim


class GroupPrimsCommand(omni.kit.commands.Command, UsdStageHelper):
    """Group primitives to the same parent."""

    def __init__(
        self,
        prim_paths: List[Union[str, Sdf.Path]],
        stage: Optional[Usd.Stage] = None,
        context_name: Optional[str] = None,
        destructive=True,
    ):
        """
        Constructor.

        Args:
            prim_paths (List[str]): Prim paths that will be grouped.
            stage (Usd.Stage, optional): Stage to operate. Default is None, which means the stage in the default UsdContext is used.
            context_name (str, optional): The usd context to operate. Default is None, which means the default UsdContext is used.
                Param `stage`, to some extent, is duplicate to this param. They are both kept for back-compatibility.
            destructive (bool, optional): If it's true, it will group all prims and remove original prims, which
                                may edit other layers that are not edit target currently.
                                If it's false, all changes will be made only to the current edit target without
                                touching other layers. By default, it's true for back compatibility.
        """
        UsdStageHelper.__init__(self, stage, context_name)

        # Filter out empty and absolute root path
        self._prim_paths = []
        self._destructive = destructive
        stage = self._get_stage()
        self._all_path_prefix = Sdf.Path.emptyPath
        self._changed_layer_identifier = None
        for path in prim_paths:
            sdf_path = Sdf.Path(path)
            prim = stage.GetPrimAtPath(sdf_path)
            if not prim:
                continue

            if sdf_path and sdf_path != Sdf.Path.absoluteRootPath:
                parent_path = sdf_path.GetParentPath()
                if self._all_path_prefix == Sdf.Path.emptyPath:
                    self._all_path_prefix = parent_path
                else:
                    self._all_path_prefix = self._all_path_prefix.GetCommonPrefix(parent_path)
                self._prim_paths.append(sdf_path)

        if self._all_path_prefix == Sdf.Path.emptyPath:
            self._all_path_prefix = Sdf.Path.absoluteRootPath

        self._prim_paths = Sdf.Path.RemoveDescendentPaths(self._prim_paths)
        self._group_prim_path = None
        self._move_prims_command = None
        self._moved_paths = {}

    def do(self):
        if not self._prim_paths:
            return

        stage = self._get_stage()
        path = self._all_path_prefix.AppendElementString("Group")
        group_prim_path = omni.usd.get_stage_next_free_path(stage, path, False)
        self._group_prim_path = Sdf.Path(group_prim_path)
        group_prim = UsdGeom.Xform.Define(stage, self._group_prim_path)
        Usd.ModelAPI(group_prim).SetKind(Kind.Tokens.group)
        self._create_group_xform_impl(stage, group_prim, self._prim_paths)
        selection = self._get_context().get_selection()
        selection.set_prim_path_selected(group_prim_path, True, False, True, True)
        self._changed_layer_identifier = stage.GetEditTarget().GetLayer().identifier

    def undo(self):
        if self._changed_layer_identifier:
            changed_layer = Sdf.Find(self._changed_layer_identifier)
            if not changed_layer:
                carb.log_warn(f"Failed to ungroup prims as layer {self._changed_layer_identifier} is not found.")
                return

            stage = self._get_stage()
            with Usd.EditContext(stage, changed_layer):
                self._move_prims_command.undo()
                if self._group_prim_path:
                    delete_cmd = DeletePrimsCommand([self._group_prim_path], stage=stage)
                    delete_cmd.do()

    def _set_prim_pivot(self, prim, pivot):
        translation = Gf.Vec3d(0.0, 0.0, 0.0)
        rotation = Gf.Vec3f(0.0, 0.0, 0.0)
        scale = Gf.Vec3f(1.0, 1.0, 1.0)
        pivot = Gf.Vec3f(pivot[0], pivot[1], pivot[2])
        common_api = UsdGeom.XformCommonAPI(prim)
        common_api.SetTranslate(translation)
        common_api.SetRotate(rotation)
        common_api.SetScale(scale)
        common_api.SetPivot(pivot)

    @Trace.TraceFunction
    def _create_group_xform_impl(self, stage, group_prim, selected_prim_paths):
        old_world_matrices = {}
        new_paths = {}
        name_index = {}
        move_pending_prims = {}
        with Sdf.ChangeBlock():
            for prim_path in selected_prim_paths:
                prim = stage.GetPrimAtPath(prim_path)
                if not prim:
                    continue

                xformable = UsdGeom.Xformable(prim)
                if xformable:
                    old_world_matrices[prim_path] = omni.usd.get_world_transform_matrix(prim)
                move_to = group_prim.GetPath().AppendElementString(prim_path.name)
                index = name_index.get(move_to, -1)
                if index != -1:
                    name_index[move_to] += 1
                    move_to = group_prim.GetPath().AppendElementString(prim_path.name + "_" + str(index))
                else:
                    name_index[move_to] = 0

                move_pending_prims[prim_path] = move_to

            if len(move_pending_prims):
                self._move_prims_command = MovePrimsCommand(
                    paths_to_move = move_pending_prims,
                    keep_world_transform=False,
                    destructive=self._destructive,
                    stage_or_context=self._get_stage()
                )
                results = self._move_prims_command.do()

                # Need to check if it actually moved
                for index, (prim_path, move_to) in enumerate(move_pending_prims.items()):
                    if results[index]:
                        new_paths[prim_path] = move_to

        if len(old_world_matrices):
            for prim_path in selected_prim_paths:
                if prim_path not in new_paths:
                    continue

                new_path = new_paths[prim_path]
                new_prim = stage.GetPrimAtPath(new_path)
                new_parent = new_prim.GetParent()
                new_parent_world_mtx = omni.usd.get_world_transform_matrix(new_parent)
                new_parent_world_to_local_mtx = new_parent_world_mtx.GetInverse()
                old_world_matrix = old_world_matrices.get(prim_path, None)

                # It's possible that the prim is not xformable.
                if not old_world_matrix:
                    continue

                new_local_mtx = old_world_matrix * new_parent_world_to_local_mtx
                if not Gf.IsClose(new_local_mtx, omni.usd.get_local_transform_matrix(new_prim), 1e-2):
                    # It will author the new transform on CURRENT edit target. If an transfrom exists on a layer
                    # with stronger opinion, prim xfrom will NOT keep in place.
                    # Note that due to the limitation of our undo command, the prim spec will not be identical
                    # after undo. This will need to be addressed globally for all commands.
                    cmd = TransformPrimCommand(path=new_path, new_transform_matrix=new_local_mtx)
                    cmd.do()

            bound_box = Gf.BBox3d()
            for prim_path in selected_prim_paths:
                if prim_path not in new_paths:
                    continue

                new_path = new_paths[prim_path]
                new_prim = stage.GetPrimAtPath(new_path)
                xformable = UsdGeom.Xformable(new_prim)
                if not xformable:
                    continue

                local_bound_box = xformable.ComputeLocalBound(Usd.TimeCode.Default(), UsdGeom.Tokens.default_)
                bound_box = Gf.BBox3d.Combine(bound_box, local_bound_box)

            self._set_prim_pivot(group_prim, bound_box.ComputeCentroid())

    def _resolve_usd_references(self, is_undo=False):
        items = reversed(self._moved_paths.items()) if is_undo else self._moved_paths.items()
        for layer_identifier, paths in items:
            args = (paths["to"], paths["from"]) if is_undo else (paths["from"], paths["to"])
            omni.usd.resolve_prim_paths_references(layer_identifier, *args)


class UngroupPrimsCommand(omni.kit.commands.Command, UsdStageHelper):
    """Ungroup primitives from the parent."""

    class ExitCode(Enum):
        Success = auto()
        NoParent = auto()

    def __init__(
        self,
        prim_paths: List[Union[str, Sdf.Path]],
        stage: Optional[Usd.Stage] = None,
        context_name: Optional[str] = None,
        destructive=True,
    ):
        """
        Constructor.

        Args:
            prim_paths (List[str]): Prim paths that will be grouped.
            stage (Usd.Stage, optional): Stage to operate. Default is None, which means the stage in the default UsdContext is used.
            context_name (str, optional): The usd context to operate. Default is None, which means the default UsdContext is used.
                Param `stage`, to some extent, is duplicate to this param. They are both kept for back-compatibility.
            destructive (bool, optional): If it's true, it will group all prims and remove original prims, which
                                may edit other layers that are not edit target currently.
                                If it's false, all changes will be made only to the current edit target without
                                touching other layers. By default, it's true for back compatibility.
        """

        UsdStageHelper.__init__(self, stage, context_name)

        # Filter out empty and absolute root path
        self._destructive = destructive
        stage = self._get_stage()
        self._group_prim_path = None
        self._new_paths = []
        self._changed_layer_identifier = None

        for path in prim_paths:
            sdf_path = Sdf.Path(path)
            prim = stage.GetPrimAtPath(sdf_path)
            if not prim:
                continue

            group_prim = prim
            model_api = Usd.ModelAPI(group_prim)

            # find the parent of the group
            while group_prim.IsValid() and not Kind.Registry.IsA(model_api.GetKind(), "group"):
                if group_prim.GetParent().IsValid():
                    group_prim = group_prim.GetParent()
                    model_api = Usd.ModelAPI(group_prim)
                else:
                    break

            # if the group parent is valid add to list to be ungrouped
            if group_prim and group_prim.IsValid() and Kind.Registry.IsA(model_api.GetKind(), 'group'):
                if not self._group_prim_path:
                    self._group_prim_path = group_prim.GetPath()
                    break

    def do(self):
        if not self._group_prim_path:
            return self.ExitCode.NoParent

        self._prim_paths_in_group = []
        self._new_paths = []
        new_target_path = self._group_prim_path.GetParentPath()
        stage = self._get_stage()
        group_prim = stage.GetPrimAtPath(self._group_prim_path)

        for child in group_prim.GetChildren():
            prim_path = child.GetPath()
            move_to = new_target_path.AppendElementString(child.GetName())
            move_prim_command = MovePrimCommand(
                path_from=prim_path, path_to=move_to,
                keep_world_transform=False,
                destructive=self._destructive,
                stage_or_context=stage
            )
            move_prim_command.do()

            # Have to access internal state to make sure it's executed
            if move_prim_command._moved:
                self._new_paths.append(str(move_to))

        delete_command = DeletePrimsCommand(
            [self._group_prim_path], self._destructive, self._get_stage(),
        )
        delete_command.do()

        stage = self._get_stage()
        selection = self._get_context().get_selection()
        selection.set_selected_prim_paths(self._new_paths, True)
        self._changed_layer_identifier = stage.GetEditTarget().GetLayer().identifier

        return self.ExitCode.Success

    def undo(self):
        if self._changed_layer_identifier:
            changed_layer = Sdf.Find(self._changed_layer_identifier)
            if not changed_layer:
                carb.log_warn(f"Failed to group prims as layer {self._changed_layer_identifier} is not found.")
                return

            stage = self._get_stage()
            with Usd.EditContext(stage, changed_layer):
                group_command = GroupPrimsCommand(prim_paths=self._new_paths)
                group_command.do()

class CreatePrimWithDefaultXformCommand(omni.kit.commands.Command, UsdStageHelper):
    """Create a primitive to stage."""

    def __init__(
        self,
        prim_type: str,
        prim_path: str = None,
        select_new_prim: bool = True,
        attributes: Dict[str, Any] = {},
        create_default_xform=True,
        stage: Optional[Usd.Stage] = None,
        context_name: Optional[str] = None,
    ):
        """
        Constructor.

        Args:
            prim_type (str): Primitive type supported by USD, e.g. "Xform", "Camera", "Sphere", "Cube" etc.
            prim_path (str, optional): Path of the primitive to be created at. If None is provided,
                it will be placed at stage root or under default prim using Type name. Default is None.
            select_new_prim (bool, optional) : Whether to select the prim after it's created. Default is True.
            attributes (Dict[str, object], optional): Attributes dict to set after creation. Default is {}.
            create_default_xform (bool, optional): Whether to create default xform operators. Default is True.
            stage (Usd.Stage, optional): Stage to operate. Default is None, which means the stage in the default UsdContext is used.
            context_name (str, optional): The usd context to operate. Default is None, which means the default UsdContext is used.
                Param `stage`, to some extent, is duplicate to this param. They are both kept for back-compatibility.
        """

        UsdStageHelper.__init__(self, stage, context_name)
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
        self._selection = self._get_context().get_selection()
        self._select_new_prim = select_new_prim
        self._settings = carb.settings.get_settings()
        self._create_default_xform = create_default_xform
        self._context_name = context_name
        self._move_commands = []

    def do(self):
        stage = self._get_stage()
        path = self._prim_path or omni.usd.get_stage_next_free_path(stage, "/" + self._prim_type, True)

        ensure_parents_are_active(stage, path)

        prim = stage.DefinePrim(path, self._prim_type)
        with Sdf.ChangeBlock():
            for attr in self._attributes:
                prim.GetProperty(attr).Set(self._attributes[attr])

        with Sdf.ChangeBlock():
            self._prim_path = prim.GetPath().pathString
            # Select the created prim.
            if self._select_new_prim:
                self._selection.set_prim_path_selected(path, True, True, True, True)
            # Ensure axis influenced geometry prims are adjusted based on stage upAxis
            if prim.IsA(UsdGeom.Cylinder) or prim.IsA(UsdGeom.Capsule) or prim.IsA(UsdGeom.Cone):
                prim.GetAttribute(UsdGeom.Tokens.axis).Set(UsdGeom.GetStageUpAxis(stage))

            if prim.IsA(UsdGeom.Xformable) and self._create_default_xform:
                create_xform_cmd = CreateDefaultXformOnPrimCommand(prim_path=self._prim_path, stage=self._get_stage())
                create_xform_cmd.do()

            # Set extent if not already provided
            if UsdGeom.Tokens.extent not in self._attributes:
                attr = prim.GetAttribute(UsdGeom.Tokens.extent) if prim else None
                if prim and attr:
                    bounds = UsdGeom.Boundable.ComputeExtentFromPlugins(UsdGeom.Boundable(prim), Usd.TimeCode.Default())

                    # Bounds can be None if prim has empty points
                    if bounds is not None:
                        attr.Set(bounds)

            self._set_refinement_level(prim, stage)
            self._create_light_extra(prim, stage)

    def undo(self):
        delete_cmd = DeletePrimsCommand([self._prim_path], stage=self._get_stage())
        delete_cmd.do()

    def _create_light_extra(self, prim, stage):
        # https://github.com/PixarAnimationStudios/USD/commit/7540fdf3b2aa6b6faa0fce8e7b4c72b756286f51
        if (hasattr(UsdLux, 'LightAPI') and prim.HasAPI(UsdLux.LightAPI)) or (hasattr(UsdLux, 'Light') and prim.IsA(UsdLux.Light)):
            light_api = UsdLux.ShapingAPI.Apply(prim)
            light_api.CreateShapingConeAngleAttr(180)
            light_api.CreateShapingConeSoftnessAttr()
            light_api.CreateShapingFocusAttr()
            light_api.CreateShapingFocusTintAttr()
            light_api.CreateShapingIesFileAttr()

    def _set_refinement_level(self, prim, stage):
        if (
            prim.IsA(UsdGeom.Cylinder)
            or prim.IsA(UsdGeom.Capsule)
            or prim.IsA(UsdGeom.Cone)
            or prim.IsA(UsdGeom.Sphere)
        ) and self._settings.get(PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/highQuality"):
            prim.CreateAttribute("refinementEnableOverride", Sdf.ValueTypeNames.Bool, True).Set(True)
            prim.CreateAttribute("refinementLevel", Sdf.ValueTypeNames.Int, True).Set(2)
            write_refinement_override_enabled_hint(stage)


class CreatePrimCommand(CreatePrimWithDefaultXformCommand):
    """
    Create a primitive to stage. It is the same as :class:`.CreatePrimWithDefaultXformCommand` and kept for backward compatibility.
    """

    def __init__(
        self,
        prim_type: str,
        prim_path: str = None,
        select_new_prim: bool = True,
        attributes: Dict[str, Any] = {},
        create_default_xform=True,
        stage: Optional[Usd.Stage] = None,
        context_name: Optional[str] = None,
    ):
        """
        Constructor.

        Args:
            prim_type (str): Primitive type supported by USD, e.g. "Xform", "Camera", "Sphere", "Cube" etc.
            prim_path (str, optional): Path of the primitive to be created at. If None is provided,
                it will be placed at stage root or under default prim using Type name. Default is None.
            select_new_prim (bool, optional) : Whether to select the prim after it's created. Default is True.
            attributes (Dict[str, object], optional): Attributes dict to set after creation. Default is {}.
            create_default_xform (bool, optional): Whether to create default xform operators. Default is True.
            stage (Usd.Stage, optional): Stage to operate. Default is None, which means the stage in the default UsdContext is used.
            context_name (str, optional): The usd context to operate. Default is None, which means the default UsdContext is used.
                Param `stage`, to some extent, is duplicate to this param. They are both kept for back-compatibility.
        """

        super().__init__(prim_type, prim_path, select_new_prim, attributes, create_default_xform, stage, context_name)


class CopyPrimCommand(omni.kit.commands.Command):
    """Copy a primitive to a new path.

    Due to the complexity of the USD composition, this command provide several options to handle
    different scenarios:

    * A prim is defined and authored in single layer, this command will simply copy it.
    * A prim is defined and authored in multiple layers, this command will copy the prim according
      to options **duplicate_layers** and **combine_layers**. See :func:`omni.usd.commands.CopyPrimCommand.__init__` for reference.
    """

    def __init__(
        self,
        path_from: str,
        path_to: str = None,
        duplicate_layers: bool = False,
        combine_layers: bool = False,
        exclusive_select: bool = True,
        usd_context_name: str = "",
        flatten_references: bool = False,
        copy_to_introducing_layer: bool = False,
    ):
        """
        Constructor.

        Args:
            path_from (str): Path to copy from.
            path_to (str, optional): Path to copy to. If it's None, a path is auto-generated from stage. Default is None.
            duplicate_layers (bool, optional): Duplicate prim in all layers from the local layer stack. Default is False,
                which means it only copies the prim spec with **def** specifier to the target path, and ignores all
                **over** opinions in the other layers the local layer stack. This option can only be enabled when **combine_layers**
                and copy_to_introducing_layer are False. This option is full with assumption and does not work well when prim
                has multiple defs in different layers, which is mostly ok for now as most of the contents authored with Kit
                has only one **def** for the same prim.
            combine_layers (bool, optional): Combine layers on copy. When this option is enabled, it will combine all opinions
                authored to the source prim scattered in all the layers from the local layer stack. Default is False.
            exclusive_select (bool, optional): If to exclusively select (clear old selections) the newly create object. Default is True.
            flatten_references (bool, optional): Flatten references during copy. It's only valid when **combine_layers** is True, and **copy_to_introducing_layer** is False.
            copy_to_introducing_layer (bool, optional): If to copy it to the introducing layer, or the current edit target. Default is False,
                which means the current edit target.
        """

        self._usd_context = omni.usd.get_context(usd_context_name)
        self._selection = self._usd_context.get_selection()

        stage = self._usd_context.get_stage()
        if not path_to:
            path_to = omni.usd.get_stage_next_free_path(stage, path_from, False)
        else:
            path_to = omni.usd.get_stage_next_free_path(stage, path_to, False)
        self._path_from = path_from
        self._path_to = path_to
        self._duplicate_layers = duplicate_layers
        self._combine_layers = combine_layers
        self._exclusive_select = exclusive_select
        self._flatten_references = flatten_references
        self._copy_to_introducing_layer = copy_to_introducing_layer

    # Code ported from UsdUtils::copyPrim
    def do(self):
        self._copied = False
        stage = self._usd_context.get_stage()
        usd_prim = allow_prim_parenting(stage, self._path_from, self._path_to, "copy")
        if not usd_prim:
            return

        if not self._combine_layers and not self._copy_to_introducing_layer:
            omni.usd.duplicate_prim(stage, self._path_from, self._path_to, self._duplicate_layers)
        else:
            if not self._copy_to_introducing_layer:
                edit_target_layer = stage.GetEditTarget().GetLayer()
            else:
                edit_target_layer, _ = omni.usd.get_introducing_layer(usd_prim)

            # When combine_layers is True and it's to flatten references.
            if self._flatten_references and not self._copy_to_introducing_layer:
                if usd_prim.IsInstanceable():
                    carb.log_error("Duplicating instanceable prim with flattening is not supported.")
                    return

                # Make a temporary stage to hold the Prim to copy, and flatten it later
                flatten_stage = Usd.Stage.CreateInMemory()

                prim_stacks = []
                # If the prim is introduced by its ancestor, its primSpec might now exist in current stage (if no "over" is made to it)
                # we need to copy from its primStack
                if omni.usd.check_ancestral(usd_prim):
                    prim_stacks = usd_prim.GetPrimStack()
                else:
                    for layer in stage.GetLayerStack():
                        prim_spec = layer.GetPrimAtPath(self._path_from)
                        if prim_spec:
                            prim_stacks.append(prim_spec)

                for prim_spec in prim_stacks:
                    src_layer = prim_spec.layer
                    dst_layer = Sdf.Layer.CreateAnonymous()
                    Sdf.CreatePrimInLayer(dst_layer, self._path_from)
                    Sdf.CopySpec(src_layer, prim_spec.path, dst_layer, self._path_from)
                    # Convert all relative paths after copy to its real path.
                    omni.usd.resolve_paths(src_layer.identifier, dst_layer.identifier, False)
                    flatten_stage.GetRootLayer().subLayerPaths.append(dst_layer.identifier)

                flatten_layer = flatten_stage.Flatten()
                if flatten_layer.GetPrimAtPath(self._path_from):
                    omni.usd.resolve_paths(edit_target_layer.identifier, flatten_layer.identifier, True, True)
                    Sdf.CreatePrimInLayer(edit_target_layer, self._path_to)
                    Sdf.CopySpec(flatten_layer, self._path_from, edit_target_layer, self._path_to)
            else:
                Sdf.CreatePrimInLayer(edit_target_layer, self._path_to)
                omni.usd.stitch_prim_specs(stage, self._path_from, edit_target_layer, self._path_to, True)
        self._copied = True

        # Select the copied prim.
        self._selection.set_prim_path_selected(self._path_to, True, False, self._exclusive_select, True)

    def undo(self):
        if self._copied:
            delete_cmd = DeletePrimsCommand([self._path_to], stage=self._usd_context.get_stage())
            delete_cmd.do()

    def modify_callback_info(self, cb_type: str, cmd_args: Dict[str, Any]) -> Dict[str, Any]:
        # The command invocation may not have specified the 'path_to' so let the callback know what we ended up using.
        cmd_args["path_to"] = self._path_to
        return cmd_args


class CopyPrimsCommand(omni.kit.commands.Command):
    """
    Copy multiple primitives to new paths.

    This command is a batch version of command :class:`.CopyPrimCommand`.
    """

    def __init__(
        self,
        paths_from: List[str],
        paths_to: List[str] = None,
        duplicate_layers: bool = False,
        combine_layers: bool = False,
        flatten_references: bool = False,
        copy_to_introducing_layer: bool = False,
    ):
        """Constructor.

        See :func:`omni.usd.commands.CopyPrimCommand.__init__` for the details of all parameters except **paths_from**, which
        is a list of prim paths to be copied.
        """

        self._selection = omni.usd.get_context().get_selection()
        self._paths_from = paths_from.copy()
        self._paths_to = paths_to.copy() if paths_to is not None else None
        self._duplicate_layers = duplicate_layers
        self._combine_layers = combine_layers
        self._flatten_references = flatten_references
        self._copy_to_introducing_layer = copy_to_introducing_layer

    def do(self):
        self._previously_selected_paths = self._selection.get_selected_prim_paths()
        self._selection.clear_selected_prim_paths()
        for i in range(len(self._paths_from)):
            path_to = self._paths_to[i] if (self._paths_to is not None and i < len(self._paths_to)) else None
            omni.kit.commands.execute(
                "CopyPrim",
                path_from=self._paths_from[i],
                path_to=path_to,
                duplicate_layers=self._duplicate_layers,
                combine_layers=self._combine_layers,
                exclusive_select=False,
                flatten_references=self._flatten_references,
                copy_to_introducing_layer=self._copy_to_introducing_layer,
            )

    def undo(self):
        if self._previously_selected_paths:
            self._selection.set_selected_prim_paths(self._previously_selected_paths, False)


class CreateInstanceCommand(omni.kit.commands.Command):
    """Instance a primitive.

    It creates a new prim, adds the master object to references, and flags this prim as instanceable. It the prim is
    Xform, this command copies the transforms from the current frame. If the source prim is already instanceable, it
    tries to find master prim of this prim and uses it.
    """

    def __init__(self, path_from: str):
        """Constructor.

        Args:
            path_from (str): Path to instance from.
        """

        self._timeline = omni.timeline.get_timeline_interface()
        self._usd_context = omni.usd.get_context()
        self._selection = self._usd_context.get_selection()

        stage = self._usd_context.get_stage()
        path_to = omni.usd.get_stage_next_free_path(stage, path_from, False)
        self._path_from = path_from
        self._path_to = path_to

    def do(self):
        stage = self._usd_context.get_stage()
        timecode = self._timeline.get_current_time() * stage.GetTimeCodesPerSecond()
        prim_from = stage.GetPrimAtPath(self._path_from)

        # It only makes sence to instance Xforms
        allowed_types_for_instancing = ["Xform"]
        if not prim_from or prim_from.GetTypeName() not in allowed_types_for_instancing:
            message = f"Failed to instance prim {self._path_from} because it's not an Xform."
            carb.log_warn(message)
            post_notification(message)
            return False

        # By default the instance master is _path_from
        file_master = None
        path_master = self._path_from

        # Check if this prim already is an instance. If so, we don't want to produce instance of instance and we need to
        # find the master prim.
        references = []
        arcs = Usd.PrimCompositionQuery.GetDirectReferences(prim_from).GetCompositionArcs()
        for arc in arcs:
            arc_layer = arc.GetIntroducingLayer()
            arc_path = arc.GetIntroducingPrimPath()
            arc_prim = arc_layer.GetPrimAtPath(arc_path)
            reference_list = arc_prim.referenceList
            references += (
                reference_list.prependedItems[:] + reference_list.explicitItems[:] + reference_list.appendedItems[:]
            )

            if len(references) > 1:
                # ATM we don't consider complicated nested references. We are looking for a simple case when the user
                # presses Ctrl-I multiple times and wants to see multiple objects.
                continue

        if len(references) == 1:
            # It's a simple case, so we can use this reference as a master.
            file_master = references[0].assetPath
            path_master = references[0].primPath.pathString

        # Create a prim of the same type as _path_from
        prim_type = prim_from.GetTypeName()
        prim_to = stage.DefinePrim(self._path_to, prim_type)

        # If it's an Xform, we want the new prim to have the same position as the source
        xform_list = []
        xformable_to = None
        if prim_from.IsA(UsdGeom.Xformable):
            xformable_from = UsdGeom.Xformable(prim_from)
            xform_list = [(op, op.GetAttr().Get(timecode)) for op in xformable_from.GetOrderedXformOps()]
            xformable_to = UsdGeom.Xformable(prim_to)

        with Sdf.ChangeBlock():
            # Set inctanceable
            if file_master:
                prim_to.GetReferences().AddReference(file_master, path_master)
            else:
                prim_to.GetReferences().AddInternalReference(path_master)
            prim_to.SetInstanceable(True)

            # Copy all the Xforms from the source
            for op_from, val in xform_list:
                # to allow same typed transformable ops, we need to give the suffix as the original op
                names = op_from.GetName().split(":")
                # the name is e.g. xformOp:translate:pivot or xformOp:rotateXYZ. While HasSuffix is not
                # available in python, we filter the suffix by the number of the elements in names
                suffix = "" if len(names) < 3 else names[-1]
                op_to = xformable_to.AddXformOp(
                    op_from.GetOpType(), op_from.GetPrecision(), suffix, op_from.IsInverseOp()
                )
                op_to.GetAttr().Set(val)

        # OM-56752: If original prim has relationship that links to external paths of prim's namespace,
        # It needs to copy them so it will not lose information like material bindings.
        for relationship in prim_from.GetAuthoredRelationships():
            has_external_targets = False
            for path in relationship.GetTargets():
                if not path.HasPrefix(prim_from.GetPath()):
                    has_external_targets = True
                    break

            if has_external_targets:
                relationship.FlattenTo(prim_to)

        # Gets all external relationships under children
        external_relationships = {}
        total_relationships = 0
        for child in Usd.PrimRange(prim_from):
            if child == prim_from:
                continue

            relationships = external_relationships.get(child.GetPath(), None)
            for relationship in child.GetAuthoredRelationships():
                for path in relationship.GetTargets():
                    if not path.HasPrefix(prim_from.GetPath()):
                        if not relationships:
                            relationships = set()
                            external_relationships[child.GetPath()] = relationships
                        relationships.add(path)
                        total_relationships += 1

        # Shows 3 at most.
        if total_relationships > 0:
            relationship_list = ""
            count = 0
            for prim_path, relationships in external_relationships.items():
                if count >= 3:
                    break

                for relationship in relationships:
                    if count >= 3:
                        break

                    relationship_list += f"\n{prim_path} - {relationship}"
                    count += 1

            if total_relationships > 3:
                post_notification(
                    f"Instancing prim at {prim_from.GetPath()} includes at least the following relationships"
                    f" that are outside of its encapsulated namespace and will not take effect:\n{relationship_list}"
                )
            else:
                post_notification(
                    f"Instancing prim at {prim_from.GetPath()} includes the following relationships"
                    f" that are outside of its encapsulated namespace and will not take effect:\n{relationship_list}"
                )

        # Select the copied prim.
        self._selection.set_prim_path_selected(self._path_to, True, False, False, True)

    def undo(self):
        # Dereference this. Otherwise it fires error: Cannot remove ancestral prim
        stage = self._usd_context.get_stage()
        prim_to = stage.GetPrimAtPath(self._path_to)
        prim_to.GetReferences().ClearReferences()

        delete_cmd = DeletePrimsCommand([self._path_to], stage=stage)
        delete_cmd.do()


class CreateInstancesCommand(omni.kit.commands.Command):
    """Instance multiple primitives.

    This command is a batch version of :class:`.CreateInstanceCommand`.
    """

    def __init__(self, paths_from: List[str]):
        """Constructor.

        Args:
            paths_from List[str]: Prim paths to instance from.
        """
        self._selection = omni.usd.get_context().get_selection()
        self._paths_from = paths_from.copy()
        self._previously_selected_paths = []

        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()

        # It only makes sence to instance Xforms
        allowed_types_for_instancing = ["Xform"]

        for path in self._paths_from:
            prim = stage.GetPrimAtPath(path)
            if not prim or prim.GetTypeName() not in allowed_types_for_instancing:
                message = f"Failed to instance prim {path} because it's not an Xform."
                carb.log_warn(message)
                post_notification(message)
                self._paths_from = []
                break

    def do(self):
        if self._paths_from:
            self._previously_selected_paths = self._selection.get_selected_prim_paths()
            self._selection.clear_selected_prim_paths()
            for paths_from in self._paths_from:
                omni.kit.commands.execute("CreateInstance", path_from=paths_from)

    def undo(self):
        if self._previously_selected_paths:
            self._selection.set_selected_prim_paths(self._previously_selected_paths, False)


class DeletePrimsCommand(omni.kit.commands.Command, UsdStageHelper):
    """Delete primitives from stage."""

    def __init__(
        self,
        paths: List[Union[str, Sdf.Path]],
        destructive=True,
        stage: Optional[Usd.Stage] = None,
        context_name: Optional[str] = None,
    ):
        """
        Constructor.

        Args:
            paths (List[str]): Paths to prims to delete.

            destructive (bool, optional): If it's false, the delete will only happen in the current target, and follows:
                            1. If the prim spec is a def, it will remove the prim spec.
                            2. If the prim spec is a over, it will only deactivate this prim.
                            3. If the prim spec is not existed, it will create over prim and deactivate it.
                            4. If there is an overridden in a stronger layer, it will report errors.

                            If it's true, it will remove all prim specs in all local layers.

                            By default, it's True and means the delete operation is destructive for back-compatibility.

            stage (Usd.Stage, optional): Stage to operate. Default is None, which means to use the stage in the default UsdContext.
            context_name (str, optional): The usd context to operate. Default is None, which means to use the default UsdContext.
        """

        UsdStageHelper.__init__(self, stage, context_name)

        self._usd_context = self._get_context()
        self._selection = self._usd_context.get_selection()
        self._paths: List[Sdf.Path] = []
        self._destructive = destructive
        for path in paths:
            path = Sdf.Path(path)
            if path == Sdf.Path.absoluteRootPath:
                continue

            stage = self._get_stage()
            prim = stage.GetPrimAtPath(path)
            if prim:
                if omni.usd.editor.is_no_delete(prim):
                    carb.log_warn(f"{str(path)} is not deletable")
                else:
                    if self._destructive and omni.usd.check_ancestral(prim):
                        carb.log_warn(f"Cannot remove ancestral prim {str(path)}")
                    else:
                        self._paths.append(path)
            else:
                carb.log_error(f"{str(path)} does not exist")

        self._paths = Sdf.Path.RemoveDescendentPaths(self._paths)
        self._prev_selected_paths = list(self._selection.get_selected_prim_paths())
        self._temp_layers = {}
        self._default_prim_path = None
        self._active_state_changed_paths = {}
        self._changed_layer_identifier = None
        self._settings = carb.settings.get_settings()

    def _is_auto_authoring_layer(self, layer_identifier):
        try:
            import omni.kit.usd.layers as layers

            return layers.get_auto_authoring(self._usd_context).is_auto_authoring_layer(layer_identifier)
        except Exception:
            return False

    def _has_overridden_in_stronger_layer(self, stage, prim_path):
        edit_target = stage.GetEditTarget()
        edit_layer = edit_target.GetLayer()
        layer_stack = stage.GetLayerStack()
        for layer in layer_stack:
            if layer == edit_layer:
                break

            prim_spec = layer.GetPrimAtPath(prim_path)
            if not prim_spec:
                continue

            # If active flag is overridden in a stronger layer.
            if prim_spec.HasActive() and prim_spec.active:
                return True

        return False

    def _remove_prim_spec_in_auto_authoring_layer(self, stage, path):
        layer_stack = stage.GetLayerStack()
        for layer in layer_stack:
            if self._is_auto_authoring_layer(layer.identifier):
                remove_prim_spec(layer, path)
                break

    @Trace.TraceFunction
    def _remove_prim_specs(self, stage, paths):
        temp_layers = {}
        layer_stack = stage.GetLayerStack()
        for layer in layer_stack:
            temp_layer = Sdf.Layer.CreateAnonymous()
            edit = Sdf.BatchNamespaceEdit()
            for path in paths:
                prim_spec = layer.GetPrimAtPath(path)
                if prim_spec is None:
                    continue

                Sdf.CreatePrimInLayer(temp_layer, path)
                Sdf.CopySpec(layer, path, temp_layer, path)
                edit.Add(path, Sdf.Path.emptyPath)

            if layer.Apply(edit) and not self._is_auto_authoring_layer(layer.identifier):
                temp_layers[layer.identifier] = temp_layer

        return temp_layers

    def _has_prim_specs(self, stage, path):
        for layer in stage.GetLayerStack():
            prim_spec = layer.GetPrimAtPath(path)
            if prim_spec:
                return True

        return False

    def do(self):
        self._changed_layer_identifier = None
        self._active_state_changed_paths.clear()
        self._default_prim_path = None
        self._temp_layers.clear()

        stage = self._get_stage()
        clear_default_prim = False
        self._default_prim_path = stage.GetDefaultPrim().GetPath() if stage.HasDefaultPrim() else None
        if self._default_prim_path:
            clear_default_prim = self._default_prim_path in self._paths
        else:
            clear_default_prim = False

        with Sdf.ChangeBlock():
            if clear_default_prim:
                self._default_prim_path = stage.GetDefaultPrim().GetPath()
                stage.ClearDefaultPrim()

            to_be_removed_paths = []
            to_be_deactivated_paths = []
            if self._destructive:
                to_be_removed_paths = self._paths
            else:
                for path in self._paths:
                    usd_prim = stage.GetPrimAtPath(path)
                    if not usd_prim:
                        continue

                    if prim_can_be_removed_without_destruction(self._usd_context, path):
                        to_be_removed_paths.append(path)
                    else:
                        to_be_deactivated_paths.append(path)

            self._temp_layers = self._remove_prim_specs(stage, to_be_removed_paths)
            if to_be_deactivated_paths:
                # Working with current edit target, or default layer in auto_authoring mode.
                with active_edit_context(self._usd_context):
                    edit_target = stage.GetEditTarget()
                    current_layer = edit_target.GetLayer()
                    self._changed_layer_identifier = current_layer.identifier

                    temp_layer = self._temp_layers.get(current_layer.identifier, None)
                    if not temp_layer:
                        temp_layer = Sdf.Layer.CreateAnonymous()
                        self._temp_layers[current_layer.identifier] = temp_layer

                    for path in to_be_deactivated_paths:
                        # Removing auto-authoring copy always
                        self._remove_prim_spec_in_auto_authoring_layer(stage, path)

                        if self._has_overridden_in_stronger_layer(stage, path):
                            error = f"Failed to deactivate prim {path} because it is activated in a stronger layer."
                            carb.log_warn(error)
                            post_notification(error)
                            continue

                        created = False
                        prim_spec = current_layer.GetPrimAtPath(path)
                        # If it's def, removing it in current layer to save file size.
                        if prim_spec and prim_spec.specifier == Sdf.SpecifierDef:
                            Sdf.CreatePrimInLayer(temp_layer, path)
                            Sdf.CopySpec(current_layer, path, temp_layer, path)
                            remove_prim_spec(current_layer, path)
                            # Creates prim spec to set active meta as it has deltas in other layers.
                            prim_spec = Sdf.CreatePrimInLayer(current_layer, path)
                        else:
                            # Otherwise, we only deactivate it.
                            if not prim_spec:
                                prim_spec = Sdf.CreatePrimInLayer(current_layer, path)
                                # Record this so we can remove it in undo.
                                created = True

                        if prim_spec.HasActive():
                            if prim_spec.active != False:
                                self._active_state_changed_paths[path] = (prim_spec.active, created)
                        else:
                            self._active_state_changed_paths[path] = (None, created)
                        prim_spec.active = False

    def undo(self):
        stage = self._get_stage()
        with Sdf.ChangeBlock():
            for identifier, restore_from in self._temp_layers.items():
                restore_to = Sdf.Find(identifier)
                if not restore_to:
                    carb.log_warn(f"Failed to restore removed prims as target layer {identifier} cannot be found.")
                    continue

                for path in self._paths:
                    if restore_from.GetPrimAtPath(path):
                        Sdf.CreatePrimInLayer(restore_to, path)
                        Sdf.CopySpec(restore_from, path, restore_to, path)

            self._temp_layers = {}

            for path, value in self._active_state_changed_paths.items():
                restore_to = Sdf.Find(self._changed_layer_identifier)
                if not restore_to:
                    carb.log_warn(
                        f"Failed to restore removed prims as target layer {self._changed_layer_identifier} cannot be found."
                    )
                    continue

                prim_spec = restore_to.GetPrimAtPath(path)
                if not prim_spec:
                    carb.log_warn(
                        f"Failed to restore removed prim {path} to {self._changed_layer_identifier} as it cannot be found."
                    )
                    continue

                active, created = value
                if created:
                    parent_spec = prim_spec.realNameParent
                    if prim_spec.name in parent_spec.nameChildren:
                        del parent_spec.nameChildren[prim_spec.name]
                    continue

                if active is None or active == True:
                    prim_spec.ClearActive()
                else:
                    prim_spec.active = active

        stage = self._get_stage()
        if self._default_prim_path:
            stage.SetDefaultPrim(stage.GetPrimAtPath(self._default_prim_path))

        # Reselect restored objects
        self._selection.set_selected_prim_paths(self._prev_selected_paths, False)


class CreatePrimsCommand(omni.kit.commands.Command):
    """
    Create multiple primitives.

    This command is a batch version of command :class:`.CreatePrimCommand`.
    """

    def __init__(self, prim_types: List[str], usd_context_name: Optional[str] = None):
        """
        Constructor.

        Args:
            prim_types (List[str]): List of primitive types to create, e.g ["Sphere", "Cone"].
            usd_context_name (str, optional): The usd context to operate. Default is None, which means the default UsdContext.
        """

        self._prim_types = prim_types
        self._usd_context_name = usd_context_name

    def do(self):
        for p in self._prim_types:
            omni.kit.commands.execute("CreatePrim", prim_type=p, context_name=self._usd_context_name)

    def undo(self):
        pass


class CreateDefaultXformOnPrimCommand(omni.kit.commands.Command):
    """Create default xformOp on prim."""

    def __init__(self, prim_path: str, stage: Usd.Stage):
        """
        Constructor.

        Args:
            prim_path (str): Path of the primitive to be create xform attribtues
            stage (Usd.Stage): The USD stage to operate.
        """

        self._prim_path = prim_path
        self._stage = stage
        self._settings = carb.settings.get_settings()
        self._added_attributes = []
        self._type_changed_attributes = []
        self._old_xform_op_order = None

    def do(self):
        self._added_attributes = []
        self._type_changed_attributes = []
        self._old_xformOrder = None
        prim = self._stage.GetPrimAtPath(self._prim_path)
        if not prim or not prim.IsA(UsdGeom.Xformable):
            return
        with Sdf.ChangeBlock():
            is_prim_created_with_default_xform = self._settings.get(
                PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/PrimCreationWithDefaultXformOps"
            )
            if not is_prim_created_with_default_xform:
                return
            defaultXformOpType = self._settings.get(PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/DefaultXformOpType")
            if prim.IsA(UsdGeom.Camera):
                defaultRotationOrder = self._settings.get(
                    PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/DefaultCameraRotationOrder"
                )
            else:
                defaultRotationOrder = self._settings.get(
                    PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/DefaultRotationOrder"
                )
            defaultXformPrecision = self._settings.get(
                PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/DefaultXformOpPrecision"
            )
            vec3_type = Sdf.ValueTypeNames.Double3 if defaultXformPrecision == "Double" else Sdf.ValueTypeNames.Float3
            quat_type = Sdf.ValueTypeNames.Quatd if defaultXformPrecision == "Double" else Sdf.ValueTypeNames.Quatf
            mat4_type = Sdf.ValueTypeNames.Matrix4d  # there is no Matrix4f in SdfValueTypeNames
            default_translate = (
                Gf.Vec3d(0.0, 0.0, 0.0) if defaultXformPrecision == "Double" else Gf.Vec3f(0.0, 0.0, 0.0)
            )
            default_euler = self._get_default_euler_angle(
                prim, self._stage, Gf.Vec3d if defaultXformPrecision == "Double" else Gf.Vec3f
            )
            default_scale = Gf.Vec3d(1.0, 1.0, 1.0) if defaultXformPrecision == "Double" else Gf.Vec3f(1.0, 1.0, 1.0)
            rotation = (
                Gf.Rotation(Gf.Vec3d.XAxis(), default_euler[0])
                * Gf.Rotation(Gf.Vec3d.YAxis(), default_euler[1])
                * Gf.Rotation(Gf.Vec3d.ZAxis(), default_euler[2])
            )
            quat = rotation.GetQuat()
            default_orient = Gf.Quatd(quat) if defaultXformPrecision == "Double" else Gf.Quatf(quat)
            if defaultXformOpType == "Scale, Rotate, Translate":
                attr_translate = prim.GetAttribute("xformOp:translate")
                if not attr_translate:
                    attr_translate = prim.CreateAttribute("xformOp:translate", vec3_type, False)
                    attr_translate.Set(default_translate)
                    self._added_attributes.append(attr_translate)
                elif attr_translate.GetTypeName() != vec3_type:
                    attr_translate.SetTypeName(vec3_type)
                    self._type_changed_attributes.append([attr_translate, vec3_type])
                attr_rotate_name = "xformOp:rotate" + defaultRotationOrder
                attr_rotate = prim.GetAttribute(attr_rotate_name)
                if not attr_rotate:
                    attr_rotate = prim.CreateAttribute(attr_rotate_name, vec3_type, False)
                    euler = self._convert_default_euler_angle(rotation, default_euler, defaultRotationOrder)
                    attr_rotate.Set(euler)
                    self._added_attributes.append(attr_rotate)
                elif attr_rotate.GetTypeName() != vec3_type:
                    attr_rotate.SetTypeName(vec3_type)
                    self._type_changed_attributes.append([attr_rotate, vec3_type])
                attr_scale = prim.GetAttribute("xformOp:scale")
                if not attr_scale:
                    attr_scale = prim.CreateAttribute("xformOp:scale", vec3_type, False)
                    attr_scale.Set(default_scale)
                    self._added_attributes.append(attr_scale)
                elif attr_scale.GetTypeName() != vec3_type:
                    attr_scale.SetTypeName(vec3_type)
                    self._type_changed_attributes.append([attr_scale, vec3_type])
                attr_order = prim.GetAttribute("xformOpOrder")
                if not attr_order:
                    attr_order = prim.CreateAttribute("xformOpOrder", Sdf.ValueTypeNames.TokenArray, False)
                else:
                    self._old_xform_op_order = attr_order.Get()
                attr_order.Set(["xformOp:translate", attr_rotate_name, "xformOp:scale"])
            if defaultXformOpType == "Scale, Orient, Translate":
                attr_translate = prim.GetAttribute("xformOp:translate")
                if not attr_translate:
                    attr_translate = prim.CreateAttribute("xformOp:translate", vec3_type, False)
                    attr_translate.Set(default_translate)
                    self._added_attributes.append(attr_translate)
                elif attr_translate.GetTypeName() != vec3_type:
                    attr_translate.SetTypeName(vec3_type)
                    self._type_changed_attributes.append([attr_translate, vec3_type])
                attr_rotate = prim.GetAttribute("xformOp:orient")
                if not attr_rotate:
                    attr_rotate = prim.CreateAttribute("xformOp:orient", quat_type, False)
                    attr_rotate.Set(default_orient)
                    self._added_attributes.append(attr_rotate)
                elif attr_rotate.GetTypeName() != quat_type:
                    attr_rotate.SetTypeName(quat_type)
                    self._type_changed_attributes.append([attr_rotate, quat_type])
                attr_scale = prim.GetAttribute("xformOp:scale")
                if not attr_scale:
                    attr_scale = prim.CreateAttribute("xformOp:scale", vec3_type, False)
                    attr_scale.Set(default_scale)
                    self._added_attributes.append(attr_scale)
                elif attr_scale.GetTypeName() != vec3_type:
                    attr_scale.SetTypeName(vec3_type)
                    self._type_changed_attributes.append([attr_scale, vec3_type])
                attr_order = prim.GetAttribute("xformOpOrder")
                if not attr_order:
                    attr_order = prim.CreateAttribute("xformOpOrder", Sdf.ValueTypeNames.TokenArray, False)
                else:
                    self._old_xform_op_order = attr_order.Get()
                attr_order.Set(["xformOp:translate", "xformOp:orient", "xformOp:scale"])
            if defaultXformOpType == "Transform":
                attr_matrix = prim.GetAttribute("xformOp:transform")
                if not attr_matrix:
                    attr_matrix = prim.CreateAttribute("xformOp:transform", mat4_type, False)
                    attr_matrix.Set(
                        Gf.Matrix4d().SetScale(Gf.Vec3d(default_scale))
                        * Gf.Matrix4d().SetRotate(rotation)
                        * Gf.Matrix4d().SetTranslate(Gf.Vec3d(default_translate))
                    )
                    self._added_attributes.append(attr_matrix)
                attr_order = prim.GetAttribute("xformOpOrder")
                if not attr_order:
                    attr_order = prim.CreateAttribute("xformOpOrder", Sdf.ValueTypeNames.TokenArray, False)
                else:
                    self._old_xform_op_order = attr_order.Get()

                attr_order.Set(["xformOp:transform"])

    def undo(self):
        prim = self._stage.GetPrimAtPath(self._prim_path)
        with Sdf.ChangeBlock():
            if not prim:
                self._added_attributes.clear()
                self._type_changed_attributes.clear()
                self._old_xform_op_order = None
                return
            for attr in self._added_attributes:
                prim.RemoveProperty(attr.GetName())
            if len(self._type_changed_attributes) > 0:
                for [attr, attr_type] in self._type_changed_attributes:
                    attr.SetTypeName(attr_type)
            self._added_attributes.clear()
            self._type_changed_attributes.clear()

            if self._old_xform_op_order is not None:
                attr_order = prim.GetAttribute("xformOpOrder")
                if self._old_xform_op_order is not None:
                    attr_order.Set(self._old_xform_op_order)
                else:
                    attr_order.Set("[]")

    def _get_default_euler_angle(self, prim, stage, vector_type):
        """
        rotation specified as if applied in XYZ order
        """
        up_axis = UsdGeom.GetStageUpAxis(stage)
        if prim.IsA(UsdLux.DistantLight):
            if up_axis == "Y":
                return vector_type(315.0, 0.0, 0.0)
            else:
                return vector_type(45.0, 0.0, 90)
        elif prim.IsA(UsdLux.DomeLight):
            if up_axis == "Y":
                return vector_type(270.0, 0.0, 0.0)
        elif (
            prim.IsA(UsdLux.SphereLight)
            or prim.IsA(UsdLux.CylinderLight)
            or prim.IsA(UsdLux.DiskLight)
            or prim.IsA(UsdLux.RectLight)
            or prim.IsA(UsdGeom.Camera)
        ):
            if up_axis == "Z":
                return vector_type(90.0, 0.0, 90.0)

        return vector_type(0.0, 0.0, 0.0)

    def _convert_default_euler_angle(self, rotation, default_euler, default_rotation_order):
        # default_euler is specified in XYZ order. If the target xfromOp order is not XYZ, need to convert the value

        converted_euler = default_euler

        conv_order_table = {
            # Do not convert XYZ
            "XZY": [0, 2, 1],
            "YXZ": [1, 0, 2],
            "YZX": [1, 2, 0],
            "ZXY": [2, 0, 1],
            "ZYX": [2, 1, 0],
        }

        axis = [Gf.Vec3d.XAxis(), Gf.Vec3d.YAxis(), Gf.Vec3d.ZAxis()]

        conv_order = conv_order_table.get(default_rotation_order, None)
        if conv_order is not None:
            decomp_rot = rotation.Decompose(axis[conv_order[2]], axis[conv_order[1]], axis[conv_order[0]])

            index_order = Gf.Vec3i()
            for i in range(0, 3):
                index_order[conv_order[i]] = 2 - i

            converted_euler[0] = decomp_rot[index_order[0]]
            converted_euler[1] = decomp_rot[index_order[1]]
            converted_euler[2] = decomp_rot[index_order[2]]

        return converted_euler


PERSISTENT_SETTINGS_PREFIX = "/persistent"


class BindMaterialCommand(omni.kit.commands.Command, UsdStageHelper):
    """Bind material to a primitive."""

    def __init__(
        self,
        prim_path: Union[str, list],
        material_path: str,
        strength=None,
        stage: Optional[Usd.Stage] = None,
        context_name: Optional[str] = None,
        material_purpose: Optional[str]= UsdShade.Tokens.allPurpose
    ):
        """
        Constructor.

        Args:
            prim_path (str or list): Path(s) to prim or collection
            material_path (str): Path to material to bind.
            strength (float, optional): Strength. Default is None, which sets the strength value from setting
                **/persistent/app/stage/materialStrength**. If no setting is set, it's set to
                UsdShade.Tokens.weakerThanDescendants.
            stage (Usd.Stage, optional): Stage to operate. Default is None, which means the stage in the default UsdContext is used.
            context_name (str, optional): The usd context to operate. Default is None, which means the default UsdContext is used.
            material_purpose (str, optional): Material purpose. Default is UsdShade.Tokens.allPurpose.
        """

        UsdStageHelper.__init__(self, stage, context_name)

        self._path = prim_path
        self._material_path = material_path
        self._material_purpose = material_purpose
        self._prev_material = []
        self._prev_strength = []

        self._strength = strength
        if self._strength is None:
            self._strength = self._get_binding_strength()

    @staticmethod
    def _get_binding_strength():
        settings = carb.settings.get_settings()
        strength_setting = settings.get(PERSISTENT_SETTINGS_PREFIX + "/app/stage/materialStrength")
        if strength_setting == "strongerThanDescendants":
            return UsdShade.Tokens.strongerThanDescendants
        if strength_setting == "fallbackStrength":
            return UsdShade.Tokens.fallbackStrength
        return UsdShade.Tokens.weakerThanDescendants

    def _bind(self, binding_api, material_prim, strength=None, collection_api=None):
        # Passed in strength-list may have None as members, re-resolve default strength in that case
        if not bool(strength):
            strength = self._get_binding_strength()
        if material_prim:
            material = UsdShade.Material(material_prim)
            if collection_api:
                binding_api.Bind(collection_api, material, collection_api.GetName(), strength, self._material_purpose)
            else:
                binding_api.Bind(material, strength, self._material_purpose)
        else:
            if collection_api:
                binding_api.UnbindCollectionBinding(collection_api.GetName(), self._material_purpose)
            else:
                binding_api.UnbindDirectBinding(self._material_purpose)

    class PathType(Enum):
        Prim = auto()
        Collection = auto()
        Neither = auto()

    def _get_path_type(self, path: str, stage: Usd.Stage):
        sdf_path = Sdf.Path(path)
        if Usd.CollectionAPI.IsCollectionAPIPath(sdf_path):
            prim = stage.GetPrimAtPath(sdf_path.GetPrimPath())
            return self.PathType.Collection, prim, Usd.CollectionAPI.Get(stage, sdf_path)
        elif sdf_path.IsPrimPath():
            prim = stage.GetPrimAtPath(sdf_path)
            return self.PathType.Prim, prim, None
        return self.PathType.Neither, None, None

    # list of prims, so there could be parent problems due to material inheritance
    def _bind_material_list(self, prim_paths, material_path, material_strength):
        stage = self._get_stage()
        if stage:
            prev_mat_path = []
            prev_mat_strength = []

            if not isinstance(material_path, list):
                material_path = [material_path] * len(prim_paths)
            if not isinstance(material_strength, list):
                material_strength = [material_strength] * len(prim_paths)

            failed_to_bind_prim_paths = []
            can_apply_paths = []

            # get list of previous values
            for path in prim_paths:
                path_type, prim, _ = self._get_path_type(path, stage)
                if prim:
                    if prim.IsInstanceProxy():
                        failed_to_bind_prim_paths.append(path)
                        continue

                    can_apply_paths.append(path)
                    binding_api = UsdShade.MaterialBindingAPI(prim)

                    if path_type == self.PathType.Prim:
                        mat, rel = binding_api.ComputeBoundMaterial(self._material_purpose)
                        # ignore inherited materials
                        mat_path = mat.GetPath()
                        if rel and rel.GetPrim() != prim:
                            mat_path = None
                        prev_mat_path.append(mat_path)
                        prev_mat_strength.append(
                            UsdShade.MaterialBindingAPI.GetMaterialBindingStrength(rel) if rel else self._strength
                        )
                    elif path_type == self.PathType.Collection:
                        all_bindings = binding_api.GetCollectionBindings()
                        for b in all_bindings:
                            prev_mat_path.append(b.GetMaterialPath())
                            rel = b.GetBindingRel()
                            prev_mat_strength.append(
                                UsdShade.MaterialBindingAPI.GetMaterialBindingStrength(rel) if rel else self._strength
                            )

            # apply new material
            index = 0
            for path in can_apply_paths:
                _, prim, collection = self._get_path_type(path, stage)
                if prim:
                    material_prim = stage.GetPrimAtPath(material_path[index]) if material_path[index] else None
                    binding_api = UsdShade.MaterialBindingAPI.Apply(prim)
                    self._bind(binding_api, material_prim, material_strength[index], collection)
                    index = index + 1

            if failed_to_bind_prim_paths:
                message = "Failed to bind material to the following prims as they are instance proxies:\n"
                for path in failed_to_bind_prim_paths:
                    message += f"\n{str(path)}"

                post_notification(message)

            return prev_mat_path, prev_mat_strength
        return None

    def _bind_material(self, material_path, strength):
        if isinstance(self._path, list):
            return self._bind_material_list(self._path, material_path, strength)
        return self._bind_material_list([self._path], material_path, strength)

    def do(self):
        self._prev_material, self._prev_strength = self._bind_material(self._material_path, self._strength)

    def undo(self):
        self._bind_material(self._prev_material, self._prev_strength)


class SetMaterialStrengthCommand(omni.kit.commands.Command):
    """Set material binding strength."""

    def __init__(self, rel, strength):
        """
        Constructor.

        Args:
            rel: Material binding relationship.
            strength (float): Strength.
        """

        self._rel = rel
        self._strength = strength
        self._prev_strength = UsdShade.MaterialBindingAPI.GetMaterialBindingStrength(rel)

    def _set_strength(self, rel, strength):
        if rel:
            UsdShade.MaterialBindingAPI.SetMaterialBindingStrength(rel, strength)

    def do(self):
        self._set_strength(self._rel, self._strength)

    def undo(self):
        self._set_strength(self._rel, self._prev_strength)


class TransformPrimCommand(omni.kit.commands.Command):
    """Set primitive's local transform."""

    def __init__(
        self,
        path: str,
        new_transform_matrix: Gf.Matrix4d,
        old_transform_matrix: Gf.Matrix4d = None,
        time_code: Usd.TimeCode = Usd.TimeCode.Default(),
        had_transform_at_key: bool = False,
        usd_context_name: str = "",
    ):
        """
        Constructor.

        Args:
            path (str): Prim path.
            new_transform_matrix (Gf.Matrix4d): New local transform matrix.
            old_transform_matrix (Gf.Matrix4d, optional): Old local transform matrix that is used for undo. If it's not given,
                it's the current local transform matrix when this command is instantiated. Default is None.
            time_code (Usd.TimeCode): The timecode to change. Default is Usd.TimeCode.Default().
            had_transform_at_key (bool): If the local transform is set already before this command. This is used for undo to
                decide if it needs to clear the new value. Default is False.
            usd_context_name (str): The UsdContext to operate. Default is empty, which means the default UsdContext is used.
        """

        carb.log_verbose("init Transform Command")
        self._new_transform_matrix = new_transform_matrix
        self._path = path
        self._old_transform_matrix = old_transform_matrix
        self._time_code = time_code
        self._had_transform_at_key = had_transform_at_key
        self._usd_context_name = usd_context_name
        if self._old_transform_matrix == None:
            prim = self._stage().GetPrimAtPath(self._path)
            xformable = UsdGeom.Xformable(prim)
            self._old_transform_matrix = xformable.GetLocalTransformation(time_code)

    def _stage(self):
        return omni.usd.get_context(self._usd_context_name).get_stage()

    def _set_value_with_precision(
        self,
        xform_op,
        value,
        time_code: Usd.TimeCode = Usd.TimeCode.Default(),
        skip_equal_set_for_timesample: bool = False,
    ):
        attr = xform_op.GetAttr()
        stage = attr.GetStage()

        set_time_code = time_code
        old_value = xform_op.Get(set_time_code)

        if not self._xform_op_is_time_sampled(xform_op):
            set_time_code = Usd.TimeCode.Default()

        # If the xformOp is on session layer, auto target to session layer
        session_layer, property_spec = omni.usd.find_spec_on_session_or_its_sublayers(stage, attr.GetPath())
        if property_spec:
            edit_target_layer = session_layer
        else:
            edit_target_layer = stage.GetEditTarget().GetLayer()

        with Usd.EditContext(stage, stage.GetEditTargetForLocalLayer(edit_target_layer)):
            if old_value is None:
                if not set_time_code.IsDefault():
                    omni.usd.copy_timesamples_from_weaker_layer(stage, xform_op.GetAttr())
                return xform_op.Set(value, set_time_code)
            else:
                value_type = type(old_value)
                if skip_equal_set_for_timesample:
                    if not set_time_code.IsDefault() and not self._has_time_sample(xform_op, set_time_code):
                        if Gf.IsClose(value_type(value), old_value, 1e-6):
                            return False
                if not set_time_code.IsDefault():
                    omni.usd.copy_timesamples_from_weaker_layer(stage, xform_op.GetAttr())
                return xform_op.Set(value_type(value), set_time_code)

    def _xform_op_is_time_sampled(self, xform_op: UsdGeom.XformOp):
        return xform_op.GetNumTimeSamples() > 0

    def _has_time_sample(self, xform_op, time_code):
        if time_code.IsDefault():
            return False
        time_samples = xform_op.GetTimeSamples()
        time_code_value = time_code.GetValue()
        if round(time_code_value) != time_code_value:
            carb.log_warn(
                f"Error: try to identify attribute {str(xform_op.GetName())} has time sample on a non round key {time_code_value}"
            )
            return False
        if time_code_value in time_samples:
            return True
        return False

    def _xform_is_time_sampled(self, xform: UsdGeom.Xformable):
        xform_ops = xform.GetOrderedXformOps()
        for xform_op in xform_ops:
            if self._xform_op_is_time_sampled(xform_op):
                return True
        return False

    def _set_transform_matrix(
        self, matrix, time_code: Usd.TimeCode = Usd.TimeCode.Default(), skip_equal_set_for_timesample: bool = False
    ):
        # OM-70552
        # https://github.com/PixarAnimationStudios/USD/commit/5e38b2aac0693fcf441a607165346e42cd625b59
        # TODO: Rewrite this to create all xformOps as needed first
        # USD v22.03 removes the non-RAII API for change blocks
        if hasattr(Sdf, 'BeginChangeBlock'):
            Sdf.BeginChangeBlock()  # Use non-RAII style Sdf.ChangeBlock because it *may* need to be released in create_if_not_exist

        # re-fetch prim every time in case redoing on a deleted then restored prim
        stage = self._stage()
        prim = stage.GetPrimAtPath(self._path)
        if prim:
            xform = UsdGeom.Xformable(prim)
            xform_ops = xform.GetOrderedXformOps()

            # A.B.temp solution to unblock a showstopper for supporting unitsResolve suffix xformOp stacks
            pre_transform_stack = False;
            extra_xform_ops = []

            for xform_op in xform_ops:
                if xform_op.GetOpName().endswith(":unitsResolve"):
                    extra_xform_ops.append(xform_op)
                    if xform_op == xform_ops[0]:
                        pre_transform_stack = True

            # A.B.temp solution to unblock a showstopper for supporting unitsResolve suffix xformOp stacks
            # reconstruct the values back after modifying the incoming transform
            if len(extra_xform_ops) > 0:
                extra_transform = Gf.Matrix4d(1.0)
                for extra_op in extra_xform_ops:
                    extra_transform *= extra_op.GetOpTransform(time_code)

                extra_transform_inv = extra_transform.GetInverse()
                if pre_transform_stack:
                    matrix = matrix * extra_transform_inv
                else:
                    matrix = extra_transform_inv * matrix

            found_transfrom_op = False
            for xform_op in xform.GetOrderedXformOps():
                if xform_op.GetOpType() == UsdGeom.XformOp.TypeTransform:
                    found_transfrom_op = True
                    # This is here to prevent the TransformGizmo from writing a translation, rotation and scale on every
                    # key where it sets a value. At some point we should revisit the gizmo to simplify the logic, and
                    # start setting only the transform value the user intends.
                    self._set_value_with_precision(xform_op, matrix, time_code, skip_equal_set_for_timesample)
                    break
            if not found_transfrom_op:
                _, scale_orient_mat_unused, scale, rot_mat, translation, persp_mat_unused = matrix.Factor()
                rot_mat.Orthonormalize(False)
                rotation = rot_mat.ExtractRotation()

                # Don't use UsdGeomXformCommonAPI. It can only manipulate a very limited subset of xformOpOrder combinations
                # Do it manually as non-destructively as possible
                new_xform_ops = []

                if len(extra_xform_ops) > 0 and pre_transform_stack:
                    for xform_op in extra_xform_ops:
                        new_xform_ops.append(xform_op)

                def find_or_add(xform_op_type, create_if_not_exist, precision, op_suffix=""):
                    # Look up the xformOp directly. It is possible that the xformOp exists
                    # as prim attribute but not listed in xform_ops. AddXformOp will fail if called.

                    # basically UsdGeomXformOp::GetOpName but it has no python binding
                    type_token = UsdGeom.XformOp.GetOpTypeToken(xform_op_type)
                    attr_name = "xformOp:" + type_token
                    if op_suffix:
                        attr_name += f":{op_suffix}"

                    xform_op_attr = prim.GetAttribute(attr_name)
                    if xform_op_attr:
                        xform_op = UsdGeom.XformOp(xform_op_attr)
                        if xform_op:
                            return True, xform_op, xform_op.GetPrecision()

                    if create_if_not_exist:
                        # It is not safe to create new xformOps inside of SdfChangeBlocks, since
                        # new attribute creation via anything above Sdf API requires the PcpCache
                        # to be up to date. Flush the current change block before creating
                        # the new xformOp.
                        # OM-70552
                        # https://github.com/PixarAnimationStudios/USD/commit/5e38b2aac0693fcf441a607165346e42cd625b59
                        # TODO: Rewrite this to create all xformOps as needed first
                        # USD v22.03 removes the non-RAII API for change blocks
                        if hasattr(Sdf, 'EndChangeBlock'):
                            Sdf.EndChangeBlock()

                        xform_op = xform.AddXformOp(xform_op_type, precision, op_suffix)
                        precision = xform_op.GetPrecision()

                        # Create a new change block to batch the subsequent authoring operations
                        # where possible.
                        # OM-70552
                        # https://github.com/PixarAnimationStudios/USD/commit/5e38b2aac0693fcf441a607165346e42cd625b59
                        # TODO: Rewrite this to create all xformOps as needed first
                        # USD v22.03 removes the non-RAII API for change blocks
                        if hasattr(Sdf, 'BeginChangeBlock'):
                            Sdf.BeginChangeBlock()
                        return True, xform_op, precision
                    return False, None, precision

                def get_first_rotate_type():
                    for xform_op in xform_ops:
                        op_type = xform_op.GetOpType()
                        if op_type >= UsdGeom.XformOp.TypeRotateX and op_type <= UsdGeom.XformOp.TypeOrient and not xform_op.GetOpName().endswith(":unitsResolve"):
                            return op_type, xform_op.GetPrecision()
                    return UsdGeom.XformOp.TypeInvalid, UsdGeom.XformOp.PrecisionFloat

                def decompose_and_set_value(
                    rotation_type,
                    axis_0,
                    axis_1,
                    axis_2,
                    x_index,
                    y_index,
                    z_index,
                    precision,
                    timecode: Usd.TimeCode = Usd.TimeCode.Default(),
                    skip_equal_set_for_timesample: bool = False,
                ):
                    ret = False
                    angles = rotation.Decompose(axis_0, axis_1, axis_2)
                    rotate = Gf.Vec3f(angles[x_index], angles[y_index], angles[z_index])
                    found, xform_op, precision = find_or_add(rotation_type, True, precision)
                    if found:
                        ret = self._set_value_with_precision(xform_op, rotate, timecode, skip_equal_set_for_timesample)
                        new_xform_ops.append(xform_op)
                    return ret

                # Set translation
                precision = UsdGeom.XformOp.PrecisionDouble
                found, xform_op, precision = find_or_add(UsdGeom.XformOp.TypeTranslate, True, precision)
                if found:
                    self._set_value_with_precision(xform_op, translation, time_code, skip_equal_set_for_timesample)
                    new_xform_ops.append(xform_op)

                # Set pivot
                precision = UsdGeom.XformOp.PrecisionFloat
                has_pivot, pivot_op, precision = find_or_add(UsdGeom.XformOp.TypeTranslate, False, precision, "pivot")
                pivot_op_inv = None
                if has_pivot:
                    new_xform_ops.append(pivot_op)
                    for op in xform_ops:
                        if op.IsInverseOp() and op.GetOpName().endswith(":pivot"):
                            pivot_op_inv = op
                            break

                # Set rotation
                precision = UsdGeom.XformOp.PrecisionFloat
                first_rotate_op_type, precision = get_first_rotate_type()

                if first_rotate_op_type == UsdGeom.XformOp.TypeInvalid:
                    first_rotate_op_type = get_default_rotation_order_type(prim.IsA(UsdGeom.Camera))

                if (
                    first_rotate_op_type == UsdGeom.XformOp.TypeRotateX
                    or first_rotate_op_type == UsdGeom.XformOp.TypeRotateY
                    or first_rotate_op_type == UsdGeom.XformOp.TypeRotateZ
                ):
                    angles = rotation.Decompose(Gf.Vec3d.ZAxis(), Gf.Vec3d.YAxis(), Gf.Vec3d.XAxis())
                    rotateZYX = Gf.Vec3f(angles[2], angles[1], angles[0])
                    found, xform_op, precision = find_or_add(UsdGeom.XformOp.TypeRotateZ, True, precision)
                    if found:
                        self._set_value_with_precision(xform_op, rotateZYX[2], time_code, skip_equal_set_for_timesample)
                        new_xform_ops.append(xform_op)
                    found, xform_op, precision = find_or_add(UsdGeom.XformOp.TypeRotateY, True, precision)
                    if found:
                        self._set_value_with_precision(xform_op, rotateZYX[1], time_code, skip_equal_set_for_timesample)
                        new_xform_ops.append(xform_op)
                    found, xform_op, precision = find_or_add(UsdGeom.XformOp.TypeRotateX, True, precision)
                    if found:
                        self._set_value_with_precision(xform_op, rotateZYX[0], time_code, skip_equal_set_for_timesample)
                        new_xform_ops.append(xform_op)
                elif first_rotate_op_type == UsdGeom.XformOp.TypeRotateZYX:
                    decompose_and_set_value(
                        first_rotate_op_type,
                        Gf.Vec3d.XAxis(),
                        Gf.Vec3d.YAxis(),
                        Gf.Vec3d.ZAxis(),
                        0,
                        1,
                        2,
                        precision,
                        time_code,
                        skip_equal_set_for_timesample,
                    )
                elif first_rotate_op_type == UsdGeom.XformOp.TypeRotateXZY:
                    decompose_and_set_value(
                        first_rotate_op_type,
                        Gf.Vec3d.YAxis(),
                        Gf.Vec3d.ZAxis(),
                        Gf.Vec3d.XAxis(),
                        2,
                        0,
                        1,
                        precision,
                        time_code,
                        skip_equal_set_for_timesample,
                    )
                elif first_rotate_op_type == UsdGeom.XformOp.TypeRotateYXZ:
                    decompose_and_set_value(
                        first_rotate_op_type,
                        Gf.Vec3d.ZAxis(),
                        Gf.Vec3d.XAxis(),
                        Gf.Vec3d.YAxis(),
                        1,
                        2,
                        0,
                        precision,
                        time_code,
                        skip_equal_set_for_timesample,
                    )
                elif first_rotate_op_type == UsdGeom.XformOp.TypeRotateYZX:
                    decompose_and_set_value(
                        first_rotate_op_type,
                        Gf.Vec3d.XAxis(),
                        Gf.Vec3d.ZAxis(),
                        Gf.Vec3d.YAxis(),
                        0,
                        2,
                        1,
                        precision,
                        time_code,
                        skip_equal_set_for_timesample,
                    )
                elif first_rotate_op_type == UsdGeom.XformOp.TypeRotateZXY:
                    decompose_and_set_value(
                        first_rotate_op_type,
                        Gf.Vec3d.YAxis(),
                        Gf.Vec3d.XAxis(),
                        Gf.Vec3d.ZAxis(),
                        1,
                        0,
                        2,
                        precision,
                        time_code,
                        skip_equal_set_for_timesample,
                    )
                elif first_rotate_op_type == UsdGeom.XformOp.TypeOrient:
                    found, xform_op, precision = find_or_add(first_rotate_op_type, False, precision)
                    if found:
                        self._set_value_with_precision(
                            xform_op, rotation.GetQuat(), time_code, skip_equal_set_for_timesample
                        )
                        new_xform_ops.append(xform_op)
                else:  # first_rotate_op_type == UsdGeom.XformOp.TypeRotateXYZ and all else
                    decompose_and_set_value(
                        UsdGeom.XformOp.TypeRotateXYZ,
                        Gf.Vec3d.ZAxis(),
                        Gf.Vec3d.YAxis(),
                        Gf.Vec3d.XAxis(),
                        2,
                        1,
                        0,
                        precision,
                        time_code,
                        skip_equal_set_for_timesample,
                    )

                # Set scale
                precision = UsdGeom.XformOp.PrecisionFloat
                found, xform_op, precision = find_or_add(UsdGeom.XformOp.TypeScale, True, precision)
                if found:
                    self._set_value_with_precision(xform_op, Gf.Vec3f(scale), time_code, skip_equal_set_for_timesample)
                    new_xform_ops.append(xform_op)

                # Set extra ops from units resolve
                if len(extra_xform_ops) > 0 and not pre_transform_stack:
                    for xform_op in extra_xform_ops:
                        new_xform_ops.append(xform_op)

                # Set inverse pivot
                if has_pivot and pivot_op_inv:
                    new_xform_ops.append(pivot_op_inv)

                xform.SetXformOpOrder(new_xform_ops, xform.GetResetXformStack())

        # OM-70552
        # https://github.com/PixarAnimationStudios/USD/commit/5e38b2aac0693fcf441a607165346e42cd625b59
        # TODO: Rewrite this to create all xformOps as needed first
        # USD v22.03 removes the non-RAII API for change blocks
        if hasattr(Sdf, 'EndChangeBlock'):
            Sdf.EndChangeBlock()

    def _clear_transform_at_time(self, time_code: Usd.TimeCode):
        if time_code.IsDefault():
            return
        stage = self._stage()
        prim = stage.GetPrimAtPath(self._path)
        if prim:
            xform = UsdGeom.Xformable(prim)
            xform_ops = xform.GetOrderedXformOps()
            for xform_op in xform.GetOrderedXformOps():
                if self._has_time_sample(xform_op, time_code):
                    xform_op.GetAttr().ClearAtTime(time_code)

    def _switch_edit_tgt(self):
        stage = self._stage()
        def_layer, prim_spec = omni.usd.find_spec_on_session_or_its_sublayers(
            stage, self._path, lambda spec: spec.specifier == Sdf.SpecifierDef
        )
        if not prim_spec or not def_layer:
            return Usd.EditContext(stage)
        else:
            return Usd.EditContext(stage, Usd.EditTarget(def_layer))

    def do(self):
        with self._switch_edit_tgt() as context:
            self._set_transform_matrix(self._new_transform_matrix, self._time_code, True)

    def undo(self):
        # Note the undo will not restore the exact original state if in do() new xformOp is created or reordered
        # it only guarantees the resolved transform is the same.
        # The better way to do this is moving Transfrom Gizmo into python and save original primSpec out on do()
        with self._switch_edit_tgt() as context:
            prim_transform_is_time_sampled = False
            stage = self._stage()
            prim = stage.GetPrimAtPath(self._path)
            if prim:
                xform = UsdGeom.Xformable(prim)
                prim_transform_is_time_sampled = self._xform_is_time_sampled(xform)
            if self._time_code.IsDefault() or self._had_transform_at_key or (not prim_transform_is_time_sampled):
                self._set_transform_matrix(self._old_transform_matrix, self._time_code, True)
            else:
                self._clear_transform_at_time(self._time_code)


class TransformPrimSRTCommand(omni.kit.commands.Command):
    """Set primitive's local transform with scale, rotation and transform values."""

    def __init__(
        self,
        path: str,
        new_translation: Gf.Vec3d = None,
        new_rotation_euler: Gf.Vec3d = None,
        new_scale: Gf.Vec3d = None,
        new_rotation_order: Gf.Vec3i = None,
        old_translation: Gf.Vec3d = None,
        old_rotation_euler: Gf.Vec3d = None,
        old_rotation_order: Gf.Vec3i = None,
        old_scale: Gf.Vec3d = None,
        time_code: Usd.TimeCode = Usd.TimeCode.Default(),
        had_transform_at_key: bool = False,
        usd_context_name: str = "",
    ):
        """
        Constructor.

        Args:
            path (str): Prim path.
            new_translation (Gf.Vec3d, optional): New local translation. Leave to None to use current value.
                Default is None.
            new_rotation_euler (Gf.Vec3d, optional): New local rotation euler angles (in degree).
                Leave to None to use current value. Default is None.
            new_scale (Gf.Vec3d, optional): New scale. Leave to None to use current value. Default is None
            new_rotation_order (Gf.Vec3i, optional): New rotation order (e.g. (0, 1, 2) means XYZ).
                Leave to None to use current value. Default is None.
            old_translation (Gf.Vec3d, optional): Old local translation for undo. Leave to None to use current value.
                Default is None.
            old_rotation_euler (Gf.Vec3d, optional): Old local rotation euler angles for undo. Leave to None to use current value.
                Default is None.
            old_rotation_order (Gf.Vec3i, optional): Old local rotation order for undo. Leave to None to use current value.
                Default is None.
            old_scale (Gf.Vec3d, optional): Old scale for undo. Leave to None to use current value. Default is None.
            time_code (Usd.TimeCode, optional): TimeCode to set transform to. Default is Usd.TimeCode.Default().
            had_transform_at_key (bool): If the local transform is set already before this command. This is used for undo to
                decide if it needs to clear the new value. Default is False.
            usd_context_name (str): The UsdContext to operate. Default is empty, which means the default UsdContext is used.
        """

        carb.log_verbose("init Transform SRT Command")
        self._settings = carb.settings.get_settings()
        self._path = path
        self._new_translation = new_translation
        self._new_rotation_euler = new_rotation_euler
        self._new_rotation_order = new_rotation_order
        self._new_scale = new_scale
        self._old_translation = old_translation
        self._old_rotation_euler = old_rotation_euler
        self._old_rotation_order = old_rotation_order
        self._old_scale = old_scale
        self._time_code = time_code
        self._had_transform_at_key = had_transform_at_key
        self._usd_context = omni.usd.get_context(usd_context_name)
        if (
            self._old_translation is None
            or self._old_rotation_euler is None
            or self._old_rotation_order is None
            or self._old_scale is None
        ):
            stage = self._usd_context.get_stage()
            prim = stage.GetPrimAtPath(self._path)
            if prim:
                (
                    old_scale,
                    old_rotation_euler,
                    old_rotation_order,
                    old_translation,
                ) = omni.usd.get_local_transform_SRT(prim, self._time_code)
                if self._old_scale is None:
                    self._old_scale = old_scale
                if self._old_rotation_euler is None:
                    self._old_rotation_euler = old_rotation_euler
                if self._old_rotation_order is None:
                    self._old_rotation_order = old_rotation_order
                if self._old_translation is None:
                    self._old_translation = old_translation
            else:
                carb.log_error("Invalid prim path to transform")

            if self._new_translation is None:
                self._new_translation = self._old_translation
            if self._new_rotation_euler is None:
                self._new_rotation_euler = self._old_rotation_euler
            if self._new_rotation_order is None:
                self._new_rotation_order = self._old_rotation_order
            if self._new_scale is None:
                self._new_scale = self._old_scale

    @carb.profiler.profile
    def _set_value_with_precision(
        self,
        xform_op,
        value,
        time_code: Usd.TimeCode = Usd.TimeCode.Default(),
        skip_equal_set_for_timesample: bool = False,
    ):
        attr = xform_op.GetAttr()
        stage = attr.GetStage()

        set_time_code = time_code
        old_value = xform_op.Get(set_time_code)

        if not self._xform_op_is_time_sampled(xform_op):
            set_time_code = Usd.TimeCode.Default()

        # If the xformOp is on session layer, auto target to session layer
        session_layer, property_spec = omni.usd.find_spec_on_session_or_its_sublayers(stage, attr.GetPath())
        if property_spec:
            edit_target_layer = session_layer
        else:
            edit_target_layer = stage.GetEditTarget().GetLayer()

        with Usd.EditContext(stage, stage.GetEditTargetForLocalLayer(edit_target_layer)):
            if old_value is None:
                if not set_time_code.IsDefault():
                    omni.usd.copy_timesamples_from_weaker_layer(stage, attr)

                attr = xform_op.GetAttr()
                type_name = attr.GetTypeName()
                default_value = type_name.defaultValue

                return xform_op.Set(type(default_value)(value), set_time_code)
            else:
                value_type = type(old_value)
                if skip_equal_set_for_timesample:
                    if not set_time_code.IsDefault() and not self._has_time_sample(xform_op, set_time_code):
                        if Gf.IsClose(value_type(value), old_value, 1e-6):
                            return False
                if not set_time_code.IsDefault():
                    omni.usd.copy_timesamples_from_weaker_layer(stage, attr)
                return xform_op.Set(value_type(value), set_time_code)

    def _xform_op_is_time_sampled(self, xform_op: UsdGeom.XformOp):
        return xform_op.GetNumTimeSamples() > 0

    def _has_time_sample(self, xform_op, time_code):
        if time_code.IsDefault():
            return False
        time_samples = xform_op.GetTimeSamples()
        time_code_value = time_code.GetValue()
        if round(time_code_value) != time_code_value:
            carb.log_warn(
                f"Error: try to identify attribute {str(xform_op.GetName())} has time sample on a non round key {time_code_value}"
            )
            return False
        if time_code_value in time_samples:
            return True
        return False

    def _xform_is_time_sampled(self, xform: UsdGeom.Xformable):
        xform_ops = xform.GetOrderedXformOps()
        for xform_op in xform_ops:
            if self._xform_op_is_time_sampled(xform_op):
                return True
        return False

    def _construct_transfrom_matrix_from_SRT(
        self, translation: Gf.Vec3d, rotation_euler: Gf.Vec3d, rotation_order: Gf.Vec3i, scale: Gf.Vec3d
    ):
        trans_mtx = Gf.Matrix4d()
        rot_mtx = Gf.Matrix4d()
        scale_mtx = Gf.Matrix4d()

        trans_mtx.SetTranslate(translation)

        axes = [Gf.Vec3d.XAxis(), Gf.Vec3d.YAxis(), Gf.Vec3d.ZAxis()]
        rotation = (
            Gf.Rotation(axes[rotation_order[0]], rotation_euler[rotation_order[0]])
            * Gf.Rotation(axes[rotation_order[1]], rotation_euler[rotation_order[1]])
            * Gf.Rotation(axes[rotation_order[2]], rotation_euler[rotation_order[2]])
        )
        rot_mtx.SetRotate(rotation)
        scale_mtx.SetScale(scale)
        return scale_mtx * rot_mtx * trans_mtx

    @carb.profiler.profile
    def _set_transform_srt(
        self,
        translation_in: Gf.Vec3d,
        rotation_euler_in: Gf.Vec3d,
        rotation_order: Gf.Vec3i,
        scale_in: Gf.Vec3d,
        time_code: Usd.TimeCode = Usd.TimeCode.Default(),
        skip_equal_set_for_timesample: bool = False,
    ):
        # OM-70552
        # https://github.com/PixarAnimationStudios/USD/commit/5e38b2aac0693fcf441a607165346e42cd625b59
        # TODO: Rewrite this to create all xformOps as needed first
        # USD v22.03 removes the non-RAII API for change blocks
        if hasattr(Sdf, 'BeginChangeBlock'):
            Sdf.BeginChangeBlock()  # Use non-RAII style Sdf.ChangeBlock because it *may* need to be released in create_if_not_exist

        translation = Gf.Vec3d(translation_in)
        scale = Gf.Vec3d(scale_in)
        rotation_euler = Gf.Vec3d(rotation_euler_in)

        # re-fetch prim every time in case redoing on a deleted then restored prim
        stage = self._usd_context.get_stage()
        prim = stage.GetPrimAtPath(self._path)
        if prim:
            xform = UsdGeom.Xformable(prim)

            # A.B.temp solution to unblock a showstopper for supporting unitsResolve suffix xformOp stacks
            pre_transform_stack = False;
            extra_xform_ops = []

            xform_ops = xform.GetOrderedXformOps()
            for xform_op in xform_ops:
                if xform_op.GetOpName().endswith(":unitsResolve"):
                    extra_xform_ops.append(xform_op)
                    if xform_op == xform_ops[0]:
                        pre_transform_stack = True

            # A.B.temp solution to unblock a showstopper for supporting unitsResolve suffix xformOp stacks
            # reconstruct the values back after modifying the incoming transform
            if len(extra_xform_ops) > 0:
                if pre_transform_stack:
                    extra_transform = Gf.Matrix4d(1.0)
                    for extra_op in extra_xform_ops:
                        extra_transform *= extra_op.GetOpTransform(time_code)

                    extra_transform_inv = extra_transform.GetInverse()
                    matrix = self._construct_transfrom_matrix_from_SRT(
                            translation, rotation_euler, rotation_order, scale
                        )

                    matrix = matrix * extra_transform_inv

                    _, scale_orient_mat_unused, new_scale, new_rot_mat, new_translation, persp_mat_unused = matrix.Factor()

                    k_axis = [ Gf.Vec3d.XAxis(), Gf.Vec3d.YAxis(), Gf.Vec3d.ZAxis() ]

                    decomp_rot = new_rot_mat.ExtractRotation().Decompose(
                        k_axis[rotation_order[2]], k_axis[rotation_order[1]], k_axis[rotation_order[0]])

                    index_order = Gf.Vec3i()
                    for i in range(3):
                        index_order[rotation_order[i]] = 2 - i

                    rotation_new = Gf.Vec3d()
                    rotation_new[0] = decomp_rot[index_order[0]]
                    rotation_new[1] = decomp_rot[index_order[1]]
                    rotation_new[2] = decomp_rot[index_order[2]]
                    translation = new_translation
                    rotation_euler = rotation_new
                    scale = new_scale
                else:
                    # Post transform, we should know what to do
                    for extra_op in extra_xform_ops:
                        if extra_op.GetOpType() == UsdGeom.XformOp.TypeScale:
                            scale_value = extra_op.Get()
                            scale = Gf.CompDiv(Gf.Vec3d(scale), Gf.Vec3d(scale_value))
                        elif extra_op.GetOpType() == UsdGeom.XformOp.TypeRotateX:
                            rot_value = extra_op.Get()
                            if Gf.IsClose(abs(rot_value), 90.0, 0.01):
                                rotation_euler[0] = rotation_euler[0] - rot_value
                                scale[1], scale[2] = scale[2], scale[1]


            found_transfrom_op = False
            for xform_op in xform.GetOrderedXformOps():
                if xform_op.GetOpType() == UsdGeom.XformOp.TypeTransform:
                    found_transfrom_op = True
                    matrix = self._construct_transfrom_matrix_from_SRT(
                        translation, rotation_euler, rotation_order, scale
                    )
                    self._set_value_with_precision(xform_op, matrix, time_code, skip_equal_set_for_timesample)
                    break
            if not found_transfrom_op:
                # Don't use UsdGeomXformCommonAPI. It can only manipulate a very limited subset of xformOpOrder combinations
                # Do it manually as non-destructively as possible
                new_xform_ops = []

                if len(extra_xform_ops) > 0 and pre_transform_stack:
                    for xform_op in extra_xform_ops:
                        new_xform_ops.append(xform_op)

                @carb.profiler.profile
                def find_or_add(xform_op_type, create_if_not_exist, precision, op_suffix=""):
                    # Look up the xformOp directly. It is possible that the xformOp exists
                    # as prim attribute but not listed in xform_ops. AddXformOp will fail if called.

                    # basically UsdGeomXformOp::GetOpName but it has no python binding
                    type_token = UsdGeom.XformOp.GetOpTypeToken(xform_op_type)
                    attr_name = "xformOp:" + type_token
                    if op_suffix:
                        attr_name += f":{op_suffix}"

                    xform_op_attr = prim.GetAttribute(attr_name)
                    if xform_op_attr:
                        xform_op = UsdGeom.XformOp(xform_op_attr)
                        if xform_op:
                            return True, xform_op, xform_op.GetPrecision()

                    if create_if_not_exist:
                        # It is not safe to create new xformOps inside of SdfChangeBlocks, since
                        # new attribute creation via anything above Sdf API requires the PcpCache
                        # to be up to date. Flush the current change block before creating
                        # the new xformOp.
                        # OM-70552
                        # https://github.com/PixarAnimationStudios/USD/commit/5e38b2aac0693fcf441a607165346e42cd625b59
                        # TODO: Rewrite this to create all xformOps as needed first
                        # USD v22.03 removes the non-RAII API for change blocks
                        if hasattr(Sdf, 'EndChangeBlock'):
                            Sdf.EndChangeBlock()

                        xform_op = xform.AddXformOp(xform_op_type, precision, op_suffix)
                        precision = xform_op.GetPrecision()

                        # Create a new change block to batch the subsequent authoring operations
                        # where possible.
                        # OM-70552
                        # https://github.com/PixarAnimationStudios/USD/commit/5e38b2aac0693fcf441a607165346e42cd625b59
                        # TODO: Rewrite this to create all xformOps as needed first
                        # USD v22.03 removes the non-RAII API for change blocks
                        if hasattr(Sdf, 'BeginChangeBlock'):
                            Sdf.BeginChangeBlock()
                        return True, xform_op, precision
                    return False, None, precision

                @carb.profiler.profile
                def get_first_rotate_type():
                    for xform_op in xform_ops:
                        op_type = xform_op.GetOpType()
                        if op_type >= UsdGeom.XformOp.TypeRotateX and op_type <= UsdGeom.XformOp.TypeOrient and not xform_op.GetOpName().endswith(":unitsResolve"):
                            return op_type, xform_op.GetPrecision()
                    return UsdGeom.XformOp.TypeInvalid, UsdGeom.XformOp.PrecisionFloat

                @carb.profiler.profile
                def set_euler_value(
                    rotation_type,
                    precision,
                    timecode: Usd.TimeCode = Usd.TimeCode.Default(),
                    skip_equal_set_for_timesample: bool = False,
                ):
                    ret = False
                    found, xform_op, precision = find_or_add(rotation_type, True, precision)
                    if found:
                        ret = self._set_value_with_precision(
                            xform_op, rotation_euler, timecode, skip_equal_set_for_timesample
                        )
                        new_xform_ops.append(xform_op)
                    return ret

                # Set translation
                precision = UsdGeom.XformOp.PrecisionDouble
                found, xform_op, precision = find_or_add(UsdGeom.XformOp.TypeTranslate, True, precision)
                if found:
                    self._set_value_with_precision(xform_op, translation, time_code, skip_equal_set_for_timesample)
                    new_xform_ops.append(xform_op)

                # Set pivot
                precision = UsdGeom.XformOp.PrecisionFloat
                has_pivot, pivot_op, precision = find_or_add(UsdGeom.XformOp.TypeTranslate, False, precision, "pivot")
                pivot_op_inv = None
                if has_pivot:
                    new_xform_ops.append(pivot_op)
                    for op in xform_ops:
                        if op.IsInverseOp() and op.GetOpName().endswith(":pivot"):
                            pivot_op_inv = op
                            break

                # Set rotation
                precision = UsdGeom.XformOp.PrecisionFloat
                first_rotate_op_type, precision = get_first_rotate_type()
                rotation_order_to_type_map = {
                    Gf.Vec3i(0, 1, 2): UsdGeom.XformOp.TypeRotateXYZ,
                    Gf.Vec3i(0, 2, 1): UsdGeom.XformOp.TypeRotateXZY,
                    Gf.Vec3i(1, 0, 2): UsdGeom.XformOp.TypeRotateYXZ,
                    Gf.Vec3i(1, 2, 0): UsdGeom.XformOp.TypeRotateYZX,
                    Gf.Vec3i(2, 0, 1): UsdGeom.XformOp.TypeRotateZXY,
                    Gf.Vec3i(2, 1, 0): UsdGeom.XformOp.TypeRotateZYX,
                }

                if first_rotate_op_type == UsdGeom.XformOp.TypeInvalid:
                    default_xform_ops = self._settings.get_as_string(
                        PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/DefaultXformOpType"
                    )

                    if default_xform_ops == "Scale, Orient, Translate":
                        first_rotate_op_type = UsdGeom.XformOp.TypeOrient
                    else:
                        # TODO what if default_xform_ops == "Transform"?
                        first_rotate_op_type = rotation_order_to_type_map.get(
                            rotation_order, UsdGeom.XformOp.TypeInvalid
                        )
                if (
                    first_rotate_op_type == UsdGeom.XformOp.TypeRotateX
                    or first_rotate_op_type == UsdGeom.XformOp.TypeRotateY
                    or first_rotate_op_type == UsdGeom.XformOp.TypeRotateZ
                ):
                    # Add in reverse order
                    axis_type = [
                        UsdGeom.XformOp.TypeRotateX,
                        UsdGeom.XformOp.TypeRotateY,
                        UsdGeom.XformOp.TypeRotateZ,
                    ]
                    for i in range(2, -1, -1):
                        axis = rotation_order[i]
                        found, xform_op, precision = find_or_add(axis_type[axis], True, precision)
                        if found:
                            self._set_value_with_precision(
                                xform_op, rotation_euler[axis], time_code, skip_equal_set_for_timesample
                            )
                            new_xform_ops.append(xform_op)
                elif (
                    first_rotate_op_type == UsdGeom.XformOp.TypeRotateXYZ
                    or first_rotate_op_type == UsdGeom.XformOp.TypeRotateXZY
                    or first_rotate_op_type == UsdGeom.XformOp.TypeRotateYXZ
                    or first_rotate_op_type == UsdGeom.XformOp.TypeRotateYZX
                    or first_rotate_op_type == UsdGeom.XformOp.TypeRotateZXY
                    or first_rotate_op_type == UsdGeom.XformOp.TypeRotateZYX
                ):
                    provided_rotation_order = rotation_order_to_type_map.get(rotation_order, first_rotate_op_type)
                    if provided_rotation_order != first_rotate_op_type:
                        carb.log_warn(
                            f"Existing rotation order {first_rotate_op_type} on prim {self._path} is different than desired {provided_rotation_order}, overriding..."
                        )

                    set_euler_value(
                        provided_rotation_order,
                        precision,
                        time_code,
                        skip_equal_set_for_timesample,
                    )
                elif first_rotate_op_type == UsdGeom.XformOp.TypeOrient:
                    found, xform_op, precision = find_or_add(first_rotate_op_type, True, precision)
                    if found:
                        axes = [Gf.Vec3d.XAxis(), Gf.Vec3d.YAxis(), Gf.Vec3d.ZAxis()]
                        rotation = (
                            Gf.Rotation(axes[rotation_order[0]], rotation_euler[rotation_order[0]])
                            * Gf.Rotation(axes[rotation_order[1]], rotation_euler[rotation_order[1]])
                            * Gf.Rotation(axes[rotation_order[2]], rotation_euler[rotation_order[2]])
                        )
                        self._set_value_with_precision(
                            xform_op, rotation.GetQuat(), time_code, skip_equal_set_for_timesample
                        )
                        new_xform_ops.append(xform_op)
                    pass
                else:  # first_rotate_op_type == UsdGeom.XformOp.TypeRotateXYZ and all else
                    carb.log_error(f"Failed to determine rotation order {first_rotate_op_type}")

                # Set scale
                precision = UsdGeom.XformOp.PrecisionFloat
                found, xform_op, precision = find_or_add(UsdGeom.XformOp.TypeScale, True, precision)
                if found:
                    self._set_value_with_precision(xform_op, Gf.Vec3f(scale), time_code, skip_equal_set_for_timesample)
                    new_xform_ops.append(xform_op)

                # Set extra ops from units resolve
                if len(extra_xform_ops) > 0 and not pre_transform_stack:
                    for xform_op in extra_xform_ops:
                        new_xform_ops.append(xform_op)

                # Set inverse pivot
                if has_pivot and pivot_op_inv:
                    new_xform_ops.append(pivot_op_inv)

                xform.SetXformOpOrder(new_xform_ops, xform.GetResetXformStack())

        # OM-70552
        # https://github.com/PixarAnimationStudios/USD/commit/5e38b2aac0693fcf441a607165346e42cd625b59
        # TODO: Rewrite this to create all xformOps as needed first
        # USD v22.03 removes the non-RAII API for change blocks
        if hasattr(Sdf, 'EndChangeBlock'):
            carb.profiler.begin(1, "Sdf.EndChangeBlock()")
            # Calling EndChangeBlock will trigger pending USD notices to be sent out.
            # All USD notice handler will spend time in here.
            # In this case it takes half of the function time (~0.4ms at the time of this profiling)
            Sdf.EndChangeBlock()
            carb.profiler.end(1)

    def _clear_transform_at_time(self, time_code: Usd.TimeCode):
        if time_code.IsDefault():
            return
        stage = self._usd_context.get_stage()
        prim = stage.GetPrimAtPath(self._path)
        if prim:
            xform = UsdGeom.Xformable(prim)
            for xform_op in xform.GetOrderedXformOps():
                if self._has_time_sample(xform_op, time_code):
                    xform_op.GetAttr().ClearAtTime(time_code)

    def _switch_edit_tgt(self):
        stage = self._usd_context.get_stage()
        def_layer, prim_spec = omni.usd.find_spec_on_session_or_its_sublayers(
            stage, self._path, lambda spec: spec.specifier == Sdf.SpecifierDef
        )
        if not prim_spec or not def_layer:
            return Usd.EditContext(stage)
        else:
            return Usd.EditContext(stage, Usd.EditTarget(def_layer))

    def do(self):
        with self._switch_edit_tgt() as context:
            self._set_transform_srt(
                self._new_translation,
                self._new_rotation_euler,
                self._new_rotation_order,
                self._new_scale,
                self._time_code,
                True,
            )

    def undo(self):
        # Note the undo will not restore the exact original state if in do() new xformOp is created or reordered
        # it only guarantees the resolved transform is the same.
        # The better way to do this is moving Transfrom Gizmo into python and save original primSpec out on do()
        with self._switch_edit_tgt() as context:
            prim_transform_is_time_sampled = False
            stage = self._usd_context.get_stage()
            prim = stage.GetPrimAtPath(self._path)
            if prim:
                xform = UsdGeom.Xformable(prim)
                prim_transform_is_time_sampled = self._xform_is_time_sampled(xform)
            if self._time_code.IsDefault() or self._had_transform_at_key or (not prim_transform_is_time_sampled):
                self._set_transform_srt(
                    self._old_translation,
                    self._old_rotation_euler,
                    self._old_rotation_order,
                    self._old_scale,
                    self._time_code,
                    True,
                )
            else:
                self._clear_transform_at_time(self._time_code)


class TransformPrimsCommand(omni.kit.commands.Command):
    """Set local transforms for multiple primitives.

    This command is a batch version of :class:`.TransformPrimCommand`
    """

    def __init__(self, prims_to_transform: List[Tuple[str, Gf.Matrix4d, Gf.Matrix4d, Usd.TimeCode]]):
        """
        Constructor.

        Args:
            prims_to_transform (ListList[Tuple[str, Gf.Matrix4d, Gf.Matrix4d, Usd.TimeCode]]): List of primitives to transform
                in a tuple of (path, new_transform, old_transform).
        """

        self._prims_to_transform = prims_to_transform.copy()

    def do(self):
        for p in self._prims_to_transform:
            omni.kit.commands.execute(
                "TransformPrim",
                path=p[0],
                new_transform_matrix=p[1],
                old_transform_matrix=p[2],
                time_code=p[3],
                had_transform_at_key=p[4],
            )

    def undo(self):
        pass


class TransformPrimsSRTCommand(omni.kit.commands.Command):
    """Set local transforms of multiple primitives with scale, rotation and transform values.

    This command is a batch version of :class:`.TransformPrimSRTCommand`
    """

    def __init__(
        self,
        prims_to_transform: List[
            Tuple[
                str, Gf.Vec3d, Gf.Vec3d, Gf.Vec3i, Gf.Vec3d, Gf.Vec3d, Gf.Vec3d, Gf.Vec3i, Gf.Vec3d, Usd.TimeCode, bool
            ]
        ],
    ):
        """
        Constructor.

        Args:
            prims_to_transform: List of primitive to transform in a tuple of
                                (path,
                                new_translation,
                                new_rotation_euler,
                                new_rotation_order,
                                new_scale,
                                old_translation,
                                old_rotation_euler,
                                old_rotation_order,
                                old_scale,
                                time_code,
                                had_transform_at_key).
        """

        self._prims_to_transform = prims_to_transform.copy()

    def do(self):
        for p in self._prims_to_transform:
            omni.kit.commands.execute(
                "TransformPrimSRT",
                path=p[0],
                new_translation=p[1],
                new_rotation_euler=p[2],
                new_rotation_order=p[3],
                new_scale=p[4],
                old_translation=p[5],
                old_rotation_euler=p[6],
                old_rotation_order=p[7],
                old_scale=p[8],
                time_code=p[9],
                had_transform_at_key=p[10],
            )

    def undo(self):
        pass


class FramePrimsCommand(omni.kit.commands.Command):
    """Transform camera to encompass the bounds of a list of paths."""

    def __init__(
        self,
        prim_to_move: Union[str, Sdf.Path],
        prims_to_frame: Optional[Sequence[Union[str, Sdf.Path]]] = None,
        time_code: Usd.TimeCode = Usd.TimeCode.Default(),
        usd_context_name: str = "",
        aspect_ratio: float = 1,
        use_horizontal_fov: bool = None,
        zoom: float = 0.45,
        horizontal_fov: float = 0.20656116130367255,
    ):
        """
        Constructor.

        Args:
            prim_to_move(Union[str, Sdf.Path]): Path to the camera primitive that is being moved.
            prims_to_frame(Sequence[Union[str, Sdf.Path]], optional): Sequence of primitives to use to calculate the bounds to frame.
                If it's None, it means to calculate bound box for the whole stage. Default is None.
            time_code(Usd.TimeCode, optional): Timecode to set values at. Default is Usd.TimeCode.Default().
            usd_context_name(str, optional): Name of the usd context to work on. Default is None, which means the default UsdContext is used.
            aspect_ratio(float, optional): Width / Height of the final image. Default is 1.
            use_horizontal_fov(bool, optional): Whether to use a camera's horizontal or vertical field of view for framing.
            zoom(float, optional): Final zoom in or out of the framed box. Values above 0.5 move further away and below 0.5 go closer.
                Default is 0.45.
            horizontal_fov(float, optional): Default horizontal field-of-view to use for framing if one cannot be calculated.
                Default is 0.20656116130367255.
        """
        self.__usd_context_name = usd_context_name
        self.__prim_to_move = prim_to_move
        self.__time_code = time_code
        self.__prims_to_frame = prims_to_frame
        self.__created_property = False
        self.__aspect_ratio = abs(aspect_ratio) or 1.0
        self.__horizontal_fov = horizontal_fov
        self.__use_horizontal_fov = use_horizontal_fov
        self.__zoom = zoom

    def __compute_local_transform(self, stage: Usd.Stage):
        prim = stage.GetPrimAtPath(self.__prim_to_move)
        if not prim:
            carb.log_warn(f"Framing of UsdPrims failed, {self.__prim_to_move} doesn't exist")
            return None, None, None, None

        local_xform, world_xform = None, None
        xformable = UsdGeom.Xformable(prim)
        if xformable:
            local_xform = xformable.GetLocalTransformation(self.__time_code)

        imageable = UsdGeom.Imageable(prim)
        if imageable:
            parent_xform = imageable.ComputeParentToWorldTransform(self.__time_code)
            if not local_xform:
                world_xform = imageable.ComputeLocalToWorldTransform(self.__time_code)
                local_xform = world_xform * parent_xform.GetInverse()
            if not world_xform:
                world_xform = parent_xform * local_xform
            return local_xform, parent_xform, world_xform, prim

        carb.log_warn(f"Framing of UsdPrims failed, {self.__prim_to_move} isn't UsdGeom.Xformable or UsdGeom.Imageable")
        return None, None, None, None

    def __calculate_distance(self, radius, prim) -> Tuple[float, bool]:
        camera = UsdGeom.Camera(prim)
        h_fov_rad, v_fov_rad = self.__horizontal_fov, self.__horizontal_fov
        if camera:
            focalLength = camera.GetFocalLengthAttr()
            h_aperture = camera.GetHorizontalApertureAttr()
            v_aperture = camera.GetVerticalApertureAttr()
            if focalLength and (h_aperture or v_aperture):
                focalLength = focalLength.Get(self.__time_code)
                if h_aperture and not v_aperture:
                    v_aperture = h_aperture
                elif v_aperture and not h_aperture:
                    h_aperture = v_aperture
                h_aperture = h_aperture.Get(self.__time_code)
                v_aperture = v_aperture.Get(self.__time_code)

                if camera.GetProjectionAttr().Get(self.__time_code) == "orthographic":
                    new_horz_ap = (max(0.001, radius) / Gf.Camera.APERTURE_UNIT) * 3.5
                    if new_horz_ap != h_aperture:
                        new_vert_ap = v_aperture * ((new_horz_ap / h_aperture) if h_aperture else new_horz_ap)
                        return (new_horz_ap, new_vert_ap), (h_aperture, v_aperture)

                # Real fov's are 2x these, but only need the half for triangle calculation
                h_fov_rad = math.atan(
                    (h_aperture * Gf.Camera.APERTURE_UNIT) / (2.0 * focalLength * Gf.Camera.FOCAL_LENGTH_UNIT)
                )
                v_fov_rad = math.atan(
                    (v_aperture * Gf.Camera.APERTURE_UNIT) / (2.0 * focalLength * Gf.Camera.FOCAL_LENGTH_UNIT)
                )

        def fit_horizontal():
            if self.__use_horizontal_fov is not None:
                return self.__use_horizontal_fov
            conform = carb.settings.get_settings().get("/app/hydra/aperture/conform")
            if conform == 0 or conform == "vertical":
                return False

            is_fit = conform == 2 or conform == "fit"
            if is_fit or (conform == 3 or conform == "crop"):
                fov_aspect = h_fov_rad / v_fov_rad
                return not (is_fit ^ (fov_aspect > self.__aspect_ratio))
            return True

        if fit_horizontal():
            v_fov_rad = h_fov_rad / self.__aspect_ratio
        else:
            h_fov_rad = v_fov_rad * self.__aspect_ratio

        # Calculate the distance to encompass radius from the fovs
        dist = radius / math.tan(min(h_fov_rad, v_fov_rad))
        return (dist, dist), False

    def do(self):
        # Prims to frame bounds can be slightly more expensive than this, so validate we can move what was requested first
        usd_context = omni.usd.get_context(self.__usd_context_name)
        stage = usd_context.get_stage()
        local_xform, parent_xform, world_xform, prim = self.__compute_local_transform(stage)
        if not prim:
            return False

        aabbox = Gf.Range3d()

        def add_to_range(prim_path):
            aab_min, aab_max = usd_context.compute_path_world_bounding_box(prim_path)
            in_range = Gf.Range3d(Gf.Vec3d(*aab_min), Gf.Vec3d(*aab_max))
            if in_range.IsEmpty():
                aa_range = Gf.Range3d(Gf.Vec3d(-20, -20, -20), Gf.Vec3d(20, 20, 20))
                matrix = Gf.Matrix4d(*usd_context.compute_path_world_transform(prim_path))
                bbox = Gf.BBox3d(aa_range, matrix)
                in_range = bbox.ComputeAlignedRange()
                # Could still end up with an empty range (0 scale)
                if in_range.IsEmpty():
                    pos = matrix.ExtractTranslation()
                    in_range.SetMin(pos - aa_range.GetMin())
                    in_range.SetMax(pos + aa_range.GetMax())
            aabbox.UnionWith(in_range)

        prims_to_frame = self.__prims_to_frame
        if not prims_to_frame:
            prims_to_frame = [Sdf.Path.absoluteRootPath.pathString]
            if stage.HasDefaultPrim():
                dflt_prim = stage.GetDefaultPrim()
                if dflt_prim:
                    prims_to_frame = [dflt_prim.GetPath().pathString]

        # Calculate the bounds of the prims (excluding the prim we are moving if it was included)
        for prim_path in prims_to_frame:
            if prim_path != self.__prim_to_move:
                add_to_range(prim_path)

        if aabbox.IsEmpty():
            carb.log_warn(f"Framing of UsdPrims {prims_to_frame} resulted in an empty bounding-box")
            return

        if True:
            # Orient the aabox to the camera
            target = aabbox.GetMidpoint()
            tr0 = Gf.Matrix4d().SetTranslate(-target)
            local_rot = Gf.Matrix4d().SetRotate(local_xform.GetOrthonormalized().ExtractRotationQuat())
            tr1 = Gf.Matrix4d().SetTranslate(target)
            # And compute the new range
            aabbox = Gf.BBox3d(aabbox, tr0 * local_rot * tr1).ComputeAlignedRange()
        # Compute where to move in the parent space
        aabbox = Gf.BBox3d(aabbox, parent_xform.GetInverse()).ComputeAlignedRange()
        # Target is in parent-space (just like the camera / object we're moving)
        target = aabbox.GetMidpoint()
        # Frame against the aabox's bounding sphere
        radius = aabbox.GetSize().GetLength() * self.__zoom

        # TODO: Get rid of some of this complication due to Viewport-1
        values, ortho_props = self.__calculate_distance(radius, prim)
        prim_path = prim.GetPath()

        # For perspective, we really need the eye (it's translation)
        # For ortho, only needed to get coi (length to target)
        eye_dir = Gf.Vec3d(0, 0, values[0] if not ortho_props else 50000)
        eye = target + local_xform.TransformDir(eye_dir)

        # Mark center-of-interest accordingly (just length from target in local-space)
        coi_value = Gf.Vec3d(0, 0, -(eye - target).GetLength())
        coi_attr_name = "omni:kit:centerOfInterest"
        coi_attr = prim.GetAttribute(coi_attr_name)
        if not coi_attr:
            prev_coi = coi_value
            self.__created_property = True
        else:
            prev_coi = coi_attr.Get()

        omni.kit.commands.execute(
            "ChangePropertyCommand",
            prop_path=prim_path.AppendProperty(coi_attr_name),
            value=coi_value,
            prev=prev_coi,
            type_to_create_if_not_exist=Sdf.ValueTypeNames.Vector3d,
            usd_context_name=self.__usd_context_name,
            is_custom=True,
            variability=Sdf.VariabilityUniform,
        )

        if ortho_props:
            # Using time here causes issues with Viewport-1, so use default time for now
            time = self.__time_code if False else Usd.TimeCode.Default()
            omni.kit.commands.execute(
                "ChangePropertyCommand",
                prop_path=prim_path.AppendProperty("horizontalAperture"),
                value=values[0],
                prev=ortho_props[0],
                timecode=time,
                usd_context_name=self.__usd_context_name,
            )
            omni.kit.commands.execute(
                "ChangePropertyCommand",
                prop_path=prim_path.AppendProperty("verticalAperture"),
                value=values[1],
                prev=ortho_props[1],
                timecode=time,
                usd_context_name=self.__usd_context_name,
            )

        new_local_xform = Gf.Matrix4d(local_xform)
        new_local_xform.SetTranslateOnly(eye)

        had_transform_at_key = False
        had_matrix = False
        if not self.__time_code.IsDefault():
            xformable = UsdGeom.Xformable(prim)
            if xformable:
                for xform_op in xformable.GetOrderedXformOps():
                    had_matrix = xform_op.GetOpType() == UsdGeom.XformOp.TypeTransform
                    had_transform_at_key = had_transform_at_key or (xform_op.GetNumTimeSamples() > 0)

        if had_matrix:
            omni.kit.commands.execute(
                "TransformPrimCommand",
                path=self.__prim_to_move,
                new_transform_matrix=new_local_xform,
                old_transform_matrix=local_xform,
                time_code=self.__time_code,
                had_transform_at_key=had_transform_at_key,
                usd_context_name=self.__usd_context_name,
            )
        else:
            omni.kit.commands.execute(
                "TransformPrimSRTCommand",
                path=self.__prim_to_move,
                new_translation=new_local_xform.Transform(Gf.Vec3d(0, 0, 0)),
                time_code=self.__time_code,
                had_transform_at_key=had_transform_at_key,
                usd_context_name=self.__usd_context_name,
            )

    def undo(self):
        if not self.__created_property:
            return
        usd_context = omni.usd.get_context(self.__usd_context_name)
        stage = usd_context.get_stage()
        if not stage:
            return
        prim = stage.GetPrimAtPath(self.__prim_to_move)
        if not prim:
            return
        prim.RemoveProperty("omni:kit:centerOfInterest")
        self.__created_property = False


class SelectPrimsCommand(omni.kit.commands.Command):
    """Select primitives.

    See :mod:`omni.kit.selection` for more details about selection.
    """

    def __init__(
        self,
        old_selected_paths: List[str],
        new_selected_paths: List[str],
        expand_in_stage: bool = True,
        source: omni.usd.Selection.SourceType = omni.usd.Selection.SourceType.USD
    ):
        """
        Constructor.

        Args:
            old_selected_paths (List[str]): Old selected prim paths.
            new_selected_paths (List[str]): Prim paths to be selected.
            expand_in_stage (bool, DEPRECATED): Whether to expand the path in Stage Window on selection.
                This param is left for back compatibility.
            source (omni.usd.Selection.SourceType, optional): USD/FABRIC/ALL, indicates which stage selection should be set to
                Default is omni.usd.Selection.SourceType.USD.
        """

        self._selection = omni.usd.get_context().get_selection()
        self._old_selected_paths = old_selected_paths
        self._new_selected_paths = new_selected_paths
        self._expand_in_stage = expand_in_stage
        self._source = source

    def do(self):
        self._selection.set_selected_prim_paths(self._new_selected_paths, self._expand_in_stage, self._source)

    def undo(self):
        self._selection.set_selected_prim_paths(self._old_selected_paths, self._expand_in_stage, self._source)


class ToggleVisibilitySelectedPrimsCommand(omni.kit.commands.Command):
    """Toggles the visiblity of the selected primitives.

    This command will invert the visibilities for the specified list of primitives. Therefore,
    those visible primitives will be invisible after this command, and vice versa for
    invisible primitives.
    """

    def __init__(self, selected_paths: List[str], stage: Optional[Usd.Stage] = None, visible: Optional[bool] = None):
        """
        Constructor.

        Args:
            selected_paths (List[str]): A list of prim paths to toggle visibility.
            stage (Usd.Stage, optional): The stage to operate. Default is None,
                which means the stage in the default UsdContext is used.
            visible (Optional[bool]): By default, it's None that means to invert the visibility state for each prim.
                When it's set as a bool value, it will set all visibilities to the specified value instead of inverting them.
        """

        self._timeline = omni.timeline.get_timeline_interface()
        self._stage = stage or omni.usd.get_context().get_stage()
        self._selected_paths = [Sdf.Path(path) for path in selected_paths]
        self._old_invisible_parent_prims = set()
        self._changed_visibility_states = {}
        self._current_time = None
        if visible is not None:
            self._specified_visibility_value = UsdGeom.Tokens.inherited if visible else UsdGeom.Tokens.invisible
        else:
            self._specified_visibility_value = None

    def _get_prim_visibility(self, prim, time):
        imageable = UsdGeom.Imageable(prim)
        visibility_attr = imageable.GetVisibilityAttr()

        time_sampled = visibility_attr.GetNumTimeSamples() > 1
        if time_sampled:
            curr_time_code = time * self._stage.GetTimeCodesPerSecond()
        else:
            curr_time_code = Usd.TimeCode.Default()

        return imageable.ComputeVisibility(curr_time_code)

    def _toggle_visibility(self):
        self._current_time = self._timeline.get_current_time()

        for selected_path in self._selected_paths:
            selected_prim = self._stage.GetPrimAtPath(selected_path)
            if not selected_prim:
                carb.log_warn(f"Failed to toggle visibility for {selected_path} as it doesn't exist.")
                continue

            imageable = UsdGeom.Imageable(selected_prim)
            if not imageable:
                continue

            visibility = self._get_prim_visibility(selected_prim, self._current_time)
            if (
                self._specified_visibility_value is not None
                and visibility is not None
                and self._specified_visibility_value == visibility
            ):
                # Don't toggle visibility if it won't change.
                continue

            # It needs to save parent visibility as toggling visibility may influence parents.
            prefixes = selected_path.GetPrefixes()[:-1]
            for path in prefixes:
                parent = self._stage.GetPrimAtPath(path)
                if not parent:
                    break

                visibility = self._get_prim_visibility(parent, self._current_time)
                if visibility == UsdGeom.Tokens.invisible:
                    self._old_invisible_parent_prims.add(path)

            if self._specified_visibility_value is None:
                visibility = self._get_prim_visibility(selected_prim, self._current_time)
                # Invert the visibility state.
                if visibility == UsdGeom.Tokens.invisible:
                    imageable.MakeVisible()
                    self._changed_visibility_states[selected_path] = False
                else:
                    imageable.MakeInvisible()
                    self._changed_visibility_states[selected_path] = True
            elif self._specified_visibility_value == UsdGeom.Tokens.invisible:
                imageable.MakeInvisible()
                self._changed_visibility_states[selected_path] = True
            else:
                imageable.MakeVisible()
                self._changed_visibility_states[selected_path] = False

    def do(self):
        self._toggle_visibility()

    def undo(self):
        for prim_path, visible in self._changed_visibility_states.items():
            prim = self._stage.GetPrimAtPath(prim_path)
            if not prim:
                continue

            imageable = UsdGeom.Imageable(prim)
            if not imageable:
                continue

            if visible:
                imageable.MakeVisible()
            else:
                imageable.MakeInvisible()

        for path in self._old_invisible_parent_prims:
            prim = self._stage.GetPrimAtPath(path)
            if not prim:
                continue

            imageable = UsdGeom.Imageable(prim)
            imageable.MakeInvisible()


class UnhideAllPrimsCommand(omni.kit.commands.Command):
    """Unhide all primitives in the default UsdContext.

    This command will traverse the whole stage and unhides all primitives that are marked
    as invisible.
    """

    def do(self):
        self._invisible_imageables = []

        stage = omni.usd.get_context().get_stage()
        for prim in stage.Traverse():
            imageable = UsdGeom.Imageable(prim)
            if imageable:
                if imageable.ComputeVisibility() == UsdGeom.Tokens.invisible:
                    self._invisible_imageables.append(imageable)
                    imageable.MakeVisible()

    def undo(self):
        for imagleable in self._invisible_imageables:
            imagleable.MakeInvisible()


class MovePrimCommand(omni.kit.commands.Command):
    """Moves a primitive to a new path.

    This command moves a primitive from a old path to a new path. It can be used to
    re-organize the stage hierarchy. It supports two kinds of move: destructive and non-destructive.
    Destructive move means it will move opinions of the prim to the new path in all layers from the local layer stack
    instead of touching the current edit target only. Non-destructive move means it will not touch other layers instead
    of the current edit target only by merging all opinions from all local layers and moving them to the new path. It
    deactivates the old path instead of removing it depending on the condition if it will break the principle of non-destrutive
    authoring. Due to historical reason, this command is built with destuctive move so destructive move is enabled by
    default. It's recommended to use non-destructive move to ensure the command only influences the current edit target.
    REMINDER: Moving primitive to change stage's hierarchy in USD is a heavy operation that may trigger big composition cost.
    """

    def __init__(
        self,
        path_from: Union[str, Sdf.Path],
        path_to: Union[str, Sdf.Path],
        time_code: Usd.TimeCode = Usd.TimeCode.Default(),
        keep_world_transform: bool = True,
        on_move_fn: Callable[[Sdf.Path, Sdf.Path], None] = None,
        destructive=True,
        stage_or_context: Union[str, Usd.Stage, omni.usd.UsdContext] = None,
        resolve_reference: bool = True
    ):
        """
        Constructor.

        Args:
            path_from (str): Path to move prim from.
            path_to(str): Path to move prim to.
            time_code(Usd.TimeCode, optional): Current timecode of the stage. Default is Usd.TimeCode.Default().
            keep_world_transform(bool, optional): True to keep world transform after prim path is moved.
                False to keep local transfrom only. Default is True.
            on_move_fn(Callable[[Sdf.Path, Sdf.Path], None], optional): Function to call when prim is renamed, that
                the first param is the source path, and second one is the target path. Default is None.
            destructive(bool, optional): If it's false, it will not remove original prim but deactivate it. Default is True
                for back compatibility.
            stage_or_context: (Union[str, Usd.Stage, omni.usd.UsdContext]): Stage or UsdContext applies the changes to.
                It can be instance of Usd.Stage or omni.usd.UsdContext, or context name. By default, it will apply
                the changes to the stage in default UsdContext.
            resolve_reference (bool, optional): If to resolve primitive's references after prim is moved to new path.
        """
        self._path_from = Sdf.Path(path_from)
        usd_context, stage = get_context_and_stage(stage_or_context)
        self._usd_context = usd_context
        self._stage = stage
        # OMPE-28550: Initialize self._selection to avoid potential issue of accessing the attribute
        self._selection = None
        if self._usd_context:
            self._selection = self._usd_context.get_selection()
        self._path_to = Sdf.Path(omni.usd.get_stage_next_free_path(self._stage, path_to, False))
        self._time_code = time_code
        self._keep_world_transform = keep_world_transform
        self._moved = False
        self._prev_order = {}
        self._on_move_fn = on_move_fn
        self._destructive = destructive
        self._delete_command = None
        self._old_source_prim_location = None
        self._resolve_reference = resolve_reference
        self._changed_layer_identifiers = []

    def modify_callback_info(self, cb_type: str, cmd_args: Dict[str, Any]) -> Dict[str, Any]:
        # The command invocation may not have specified the 'path_to' so let the callback know what we ended up using.
        cmd_args["path_to"] = self._path_to
        return cmd_args

    @Trace.TraceFunction
    def _move_prim_spec(self, layer, path_from, path_to, is_undo):
        Sdf.CreatePrimInLayer(layer, path_to.GetParentPath())
        layer_path = layer.realPath

        if not is_undo:
            # keep the prim order when undo
            prim_spec = layer.GetPrimAtPath(path_from)
            if not prim_spec:
                return False
            parent_prim_spec = prim_spec.realNameParent

            # Each layer may have different children order. Store them separately.
            self._prev_order[layer_path] = parent_prim_spec.nameChildren.index(path_from.name)

        edit = Sdf.BatchNamespaceEdit()
        edit.Add(path_from, path_to, self._prev_order.get(layer_path, -1) if is_undo else -1)
        return layer.Apply(edit)

    def _is_auto_authoring_layer(self, layer_identifier):
        if not self._usd_context:
            return False

        try:
            import omni.kit.usd.layers as layers

            return layers.get_auto_authoring(self._usd_context).is_auto_authoring_layer(layer_identifier)
        except Exception:
            return False

    def _remove_prim_spec_in_auto_authoring_layer(self, stage, path):
        layer_stack = stage.GetLayerStack()
        for layer in layer_stack:
            if self._is_auto_authoring_layer(layer.identifier):
                remove_prim_spec(layer, path)
                break

    # Utility class to track live objects that should reflect the rename operation.
    # This is currenlty targeted at Viewports only, but a separate event/extension/registry might be better
    # to allow aribtrary extensions to handle a rename event.
    class RenameHandler:
        def __init__(self, old_path: Sdf.Path):
            """Cache all objects that reference the old_path, before any rename occurs"""
            self.__new_vp_apis = []
            self.__legacy_vp_windows = []

            # Try on new Viewport if loaded
            try:
                from omni.kit.widget.viewport import ViewportWidget

                for instance in ViewportWidget.get_instances():
                    viewport_api = instance.viewport_api
                    if viewport_api and viewport_api.camera_path.HasPrefix(old_path):
                        self.__new_vp_apis.append(viewport_api)
            except (ImportError, ModuleNotFoundError):
                pass

            # Try on legacy Viewport if loaded
            try:
                import omni.kit.viewport_legacy as vp_legacy

                vp_iface = vp_legacy.get_viewport_interface()
                # Convert to string for comparison once
                for viewport_handle in vp_iface.get_instance_list():
                    vp_window = vp_iface.get_viewport_window(viewport_handle)
                    if Sdf.Path(vp_window.get_active_camera() if vp_window else "").HasPrefix(old_path):
                        self.__legacy_vp_windows.append(vp_window)
            except (ImportError, ModuleNotFoundError):
                pass

        def apply_change(self, old_path: Sdf.Path, new_path: Sdf.Path):
            # New viewport takes the Sdf.Path natively
            for viewport_api in self.__new_vp_apis:
                try:
                    viewport_api.camera_path = viewport_api.camera_path.ReplacePrefix(old_path, new_path)
                except:
                    carb.log_warn("Failure in new Viewport camera_path")

            # Legacy Viewport takes a string
            for vp_window in self.__legacy_vp_windows:
                try:
                    vp_window_path = Sdf.Path(vp_window.get_active_camera()).ReplacePrefix(old_path, new_path)
                    vp_window.set_active_camera(vp_window_path.pathString)
                except:
                    carb.log_warn("Failure in legacy Viewport set_active_camera")

    @Trace.TraceFunction
    def _move(self, path_from, path_to, is_undo):
        if not Sdf.Path.IsValidPathString(path_to.pathString):
            carb.log_error(f"Invalid path: {str(path_to)}")
            return False

        stage = self._stage
        prim = allow_prim_parenting(stage, path_from, path_to, "move")
        if prim:
            if omni.usd.editor.is_no_delete(prim):
                error = f"{str(path_from)} is not deletable"
                carb.log_error(error)
                post_notification(error)
                return False

            if omni.usd.check_ancestral(prim):
                error = f"Cannot move/rename ancestral prim {str(path_from)}"
                carb.log_error(error)
                post_notification(error)
                return False

            prim_to_parent = stage.GetPrimAtPath(path_to.GetParentPath())
            if prim_to_parent and (prim_to_parent.IsInstance() or prim_to_parent.IsInstanceProxy()):
                error = f"{str(path_from)} cannot be moved under an instance or instance proxy."
                post_notification(error)
                return False

            # Get all of the objects that need to know about the path change
            rename_handler = MovePrimCommand.RenameHandler(path_from)

            old_world_matrices = {}
            if self._keep_world_transform and path_from.GetParentPath() != path_to.GetParentPath():
                # The moved prim might not be an Xformable (i.e. Scope), in this case, we need to find the
                # subtrees of this prim whose root are Xformable (handle nested Scope) and pin their transform.

                # Iterate all descendents in depth first order -> find first Xformable -> store its transform -> skip
                # all its children, find next subtree with Xformable root until visited the entire range.
                prim_range_it = iter(Usd.PrimRange(prim))
                for sub_prim in prim_range_it:
                    if sub_prim.IsA(UsdGeom.Xformable):
                        old_world_mtx = omni.usd.get_world_transform_matrix(sub_prim, self._time_code)
                        new_path = sub_prim.GetPath().ReplacePrefix(path_from, path_to)
                        old_world_matrices[new_path] = old_world_mtx

                        # Skip all its children
                        prim_range_it.PruneChildren()

            success = False
            was_default_prim = stage.GetDefaultPrim() == prim
            if self._selection:
                was_selected = self._selection.is_prim_path_selected(path_from.pathString)
            else:
                was_selected = False
            layer_stack = stage.GetLayerStack()
            prim_stack = prim.GetPrimStack()

            with Sdf.ChangeBlock():
                # Clean up copy inside auto-authoring firstly
                self._remove_prim_spec_in_auto_authoring_layer(stage, path_from)

                if self._destructive or (
                    not is_undo and prim_can_be_removed_without_destruction(stage, path_from)
                ):
                    self._destructive = True
                    for prim_spec in prim_stack:
                        layer = prim_spec.layer
                        # Only move from layers in the stage
                        if layer not in layer_stack:
                            continue
                        success = self._move_prim_spec(layer, path_from, path_to, is_undo) or success
                        self._changed_layer_identifiers.append(layer.identifier)
                        if success and self._resolve_reference:
                            omni.usd.resolve_prim_path_references(
                                layer.identifier, path_from.pathString, path_to.pathString
                            )
                else:
                    if is_undo:
                        if self._changed_layer_identifiers:
                            edit_target_layer = Sdf.Find(self._changed_layer_identifiers[0])
                            if not edit_target_layer:
                                carb.log_warn(
                                    f"Failed to activate {path_to} as target layer {self._changed_layer_identifier} cannot be found."
                                )
                                success = False
                            else:
                                DeletePrimsCommand([path_from], stage=stage).do()
                                if self._delete_command:
                                    with Usd.EditContext(stage, edit_target_layer):
                                        self._delete_command.undo()
                                success = True
                    else:
                        with active_edit_context(self._stage):
                            edit_target_layer = stage.GetEditTarget().GetLayer()
                            self._changed_layer_identifiers.append(edit_target_layer.identifier)
                            Sdf.CreatePrimInLayer(edit_target_layer, path_to)
                            omni.usd.stitch_prim_specs(stage, path_from, edit_target_layer, path_to)
                            self._delete_command = DeletePrimsCommand([path_from], stage=stage, destructive=False)
                            self._delete_command.do()
                            success = True

                    if success and self._resolve_reference:
                        omni.usd.resolve_prim_path_references(
                            edit_target_layer.identifier, path_from.pathString, path_to.pathString
                        )

                # Ensure prim will not be moved to the bottom.
                if success and self._old_source_prim_location is not None:
                    move_prim_to_location(stage, path_to, self._old_source_prim_location, path_from.name)

            self._moved = success
            if success:
                rename_handler.apply_change(path_from, path_to)

                if len(old_world_matrices):
                    new_prim = stage.GetPrimAtPath(path_to)
                    if not new_prim:
                        return False

                    new_parent = new_prim.GetParent()
                    new_parent_world_mtx = omni.usd.get_world_transform_matrix(new_parent, self._time_code)
                    new_parent_world_to_local_mtx = new_parent_world_mtx.GetInverse()

                    for path, mtx in old_world_matrices.items():
                        new_local_mtx = mtx * new_parent_world_to_local_mtx

                        if not Gf.IsClose(
                            new_local_mtx, omni.usd.get_local_transform_matrix(new_prim, self._time_code), 1e-2
                        ):
                            # It will author the new transform on CURRENT edit target. If an transfrom exists on a layer
                            # with stronger opinion, prim xfrom will NOT keep in place.
                            # Note that due to the limitation of our undo command, the prim spec will not be identical
                            # after undo. This will need to be addressed globally for all commands.
                            cmd = TransformPrimCommand(
                                path=path, new_transform_matrix=new_local_mtx, time_code=self._time_code
                            )
                            cmd.do()

                if was_selected and self._selection:
                    self._selection.set_prim_path_selected(path_to.pathString, True, False, False, True)
                if was_default_prim:
                    stage.SetDefaultPrim(stage.GetPrimAtPath(path_to))
                if self._on_move_fn:
                    try:
                        self._on_move_fn(path_from, path_to)
                    except:
                        carb.log_warn("error in MovePrimCommand on_move_fn")
            return success

    def do(self):
        carb.log_info(f"Moving prim from {self._path_from} to {self._path_to}")
        if (
            should_keep_children_order() and
            not self._old_source_prim_location and
            self._path_from.GetParentPath() == self._path_to.GetParentPath()
        ):
            index = get_child_position_in_the_parent(self._stage, self._path_from)
            if index != -1:
                self._old_source_prim_location = index

        return self._move(self._path_from, self._path_to, False)

    def undo(self):
        if self._moved:
            carb.log_info(f"Undo Move prim from {self._path_to} to {self._path_from}")
            self._move(self._path_to, self._path_from, True)


class MovePrimsCommand(omni.kit.commands.Command):
    """
    Move a list of primitives to new locations.

    This command is a batch version of command :class:`.MovePrimCommand`
    """

    def __init__(
        self,
        paths_to_move: Dict[str, str],
        time_code: Usd.TimeCode = Usd.TimeCode.Default(),
        keep_world_transform: bool = True,
        on_move_fn: Callable = None,
        destructive=True,
        stage_or_context: Union[str, Usd.Stage, omni.usd.UsdContext] = None
    ):
        """
        Constructor.

        Args:
            paths_to_move(Dict[str, str]): The dictionary contains entry of {path_from : path_to}.
            time_code(Usd.TimeCode, optional): Current timecode of the stage. Default is Usd.TimeCode.Default().
            keep_world_transform(bool, optional): True to keep world transform after prim path is moved.
                False to keep local transfrom only. Default is True.
            on_move_fn(Callable, optional): Function to call when prim is renamed. Default is None.
            destructive(bool, optional): If it's false, it will not remove original prim but deactivate it. Default is True
                for back compatibility.
            stage_or_context: (Union[str, Usd.Stage, omni.usd.UsdContext]): Stage or UsdContext applies the changes to.
                It can be instance of Usd.Stage or omni.usd.UsdContext, or context name. By default, it will apply
                the changes to the stage in default UsdContext.
        """

        self._paths_to_move = paths_to_move
        self._time_code = time_code
        self._keep_world_transform = keep_world_transform
        self._on_move_fn = on_move_fn
        self._destructive = destructive
        self._stage_or_context = stage_or_context
        self._move_commands = []
        self._moved_paths = {}

    def do(self):
        _results = []
        for prim_path, move_to in self._paths_to_move.items():
            move_prim_command = MovePrimCommand(
                    path_from=prim_path,
                    path_to=move_to,
                    time_code=self._time_code,
                    keep_world_transform=self._keep_world_transform,
                    on_move_fn=self._on_move_fn,
                    destructive=self._destructive,
                    stage_or_context=self._stage_or_context,
                    resolve_reference=False
                )
            move_prim_command.do()
            layer_identifiers = move_prim_command._changed_layer_identifiers

            # To check if there was an actual movement, we need to check the _moved variable
            _results.append(move_prim_command._moved)
            if move_prim_command._moved:
                self._move_commands.append(move_prim_command)
                self._add_resolve_path(layer_identifiers, prim_path, move_to)

        self._resolve_usd_references()
        return _results

    def undo(self):
        for command in reversed(self._move_commands):
            command.undo()
        self._resolve_usd_references(is_undo=True)

    def _add_resolve_path(self, layer_identifiers, path_from: Union[Sdf.Path, str], path_to: Union[Sdf.Path, str]):
        for layer_identifier in layer_identifiers:
            if layer_identifier not in self._moved_paths:
                self._moved_paths[layer_identifier] = {"from":[], "to":[]}
            self._moved_paths[layer_identifier]["from"].append(str(path_from))
            self._moved_paths[layer_identifier]["to"].append(str(path_to))

    def _resolve_usd_references(self, is_undo=False):
        items = reversed(self._moved_paths.items()) if is_undo else self._moved_paths.items()
        for layer_identifier, paths in items:
            args = (paths["to"], paths["from"]) if is_undo else (paths["from"], paths["to"])
            omni.usd.resolve_prim_paths_references(layer_identifier, *args)


class RenamePrimCommand(omni.kit.commands.Command):
    """
    Rename a primitive undoable **Command**.

    Args:
        prim_path (str): path of prim to be renamed.
        new_name (str): new name.
    """

    def __init__(
        self,
        prim_path: str,
        new_name: str
    ):
        self._prim_path = prim_path
        self._new_name = new_name
        self._move_prims_command = None

    def do(self):
        old_path = self._prim_path
        new_path = Sdf.Path(old_path).GetParentPath().AppendChild(self._new_name)
        self._move_prims_command = MovePrimsCommand(paths_to_move={old_path: new_path}, destructive=False)

        result = self._move_prims_command.do()

        return result and result[0]

    def undo(self):
        self._move_prims_command.undo()


class ReplaceReferencesCommand(omni.kit.commands.Command):  # pragma: no cover
    """Deprecated. Clears/Adds references.

    NOTE: THIS COMMAND HAS A LOT OF ISSUES AND IS DEPRECATED. PLEASE USE ReplaceReferenceCommand instead!

    Args:
        path (str): Prim path.
        old_url(str): Url to be replaced.
        new_url(str): Replacement url.
    """

    def __init__(self, path: str, old_url: str, new_url: str):
        self._usd_context = omni.usd.get_context()
        self._selection = self._usd_context.get_selection()
        self._path = None
        self._old_url = old_url
        self._new_url = new_url
        self._prev_selected_paths = list(self._selection.get_selected_prim_paths())
        self._selection.clear_selected_prim_paths()

        stage = self._usd_context.get_stage()
        prim = stage.GetPrimAtPath(path)
        if prim and not omni.usd.editor.is_no_delete(prim):
            self._path = path
        else:
            carb.log_error(f"{str(path)} does not exist or is not deletable")

    def do(self):
        stage = self._usd_context.get_stage()
        prim = stage.GetPrimAtPath(self._path)
        if prim:
            refs = prim.GetReferences()
            refs.ClearReferences()
            for url in self._new_url:
                refs.AddReference(url)

    def undo(self):
        stage = self._usd_context.get_stage()
        prim = stage.GetPrimAtPath(self._path)
        if prim:
            refs = prim.GetReferences()
            refs.ClearReferences()
            for url in self._old_url:
                refs.AddReference(url)

        # Reselect restored objects
        self._selection.clear_selected_prim_paths()
        if self._path in self._prev_selected_paths:
            self._selection.set_prim_path_selected(self._path, True, True, False, True)


class CreateUsdAttributeOnPathCommand(omni.kit.commands.Command):
    """Creates a USD Attribute with attribute path."""

    def __init__(
        self,
        attr_path: Union[Sdf.Path, str],
        attr_type: Sdf.ValueTypeName,
        custom: bool = True,
        variability: Sdf.Variability = Sdf.VariabilityVarying,
        attr_value: Any = None,
        usd_context_name: str = "",
    ):
        """Constructor.

        Args:
            attr_path (Union[Sdf.Path, str]): Path to the new attribute to be created. The prim of this path must already exist.
            attr_type (Sdf.ValueTypeName): New attribute's type.
            custom (bool, optional): If the attribute is custom. Default is True.
            variability (Sdf.Variability, optional): whether the attribute may vary over time and value coordinates,
                and if its value comes through authoring or from its owner. Default is Sdf.VariabilityVarying.
            attr_value (Any, optional): New attribute's value. Leave it as None to use default value.
            usd_context_name(str): Name of the usd context to execute the command on. Default is None, which uses the default UsdContext.
        """

        self._usd_context = omni.usd.get_context(usd_context_name)
        self._attr_path = Sdf.Path(attr_path)
        self._attr_type = attr_type
        self._custom = custom
        self._variability = variability
        self._attr_value = attr_value
        self._created = False

    def do(self):
        prim = self._usd_context.get_stage().GetPrimAtPath(self._attr_path.GetPrimPath())
        if prim:
            omni.kit.commands.execute(
                "CreateUsdAttributeCommand",
                prim=prim,
                attr_name=self._attr_path.name,
                attr_type=self._attr_type,
                custom=self._custom,
                variability=self._variability,
                attr_value=self._attr_value,
            )

    def undo(self):
        pass


class CreateUsdAttributeCommand(omni.kit.commands.Command):
    """Creates a USD Attribute for a primitive.

    Example of usage:
        omni.kit.commands.execute("CreateUsdAttribute",
                                   prim=prim,
                                   attr_name="custom",
                                   attr_type=Sdf.ValueTypeNames.Double3)
    """

    def __init__(
        self,
        prim: Usd.Prim,
        attr_name: str,
        attr_type: Sdf.ValueTypeName,
        custom: bool = True,
        variability: Sdf.Variability = Sdf.VariabilityVarying,
        attr_value: Any = None,
    ):
        """Constructor.

        Args:
            prim (Usd.Prim): USD primitive to create the attribute.
            attr_name (str): New attribute's name.
            attr_type (Sdf.ValueTypeName): New attribute's type.
            custom (bool, optional): If the attribute is custom. Default is True.
            variability (Sdf.Variability, optional): whether the attribute may vary over time and value coordinates,
                and if its value comes through authoring or from its owner. Default is Sdf.VariabilityVarying.
            attr_value (Any, optional): New attribute's value. Leave it as None to use default value.
        """

        self._stage = prim.GetStage()
        self._prim_path = prim.GetPath()
        self._attr_name = attr_name
        self._attr_type = attr_type
        self._custom = custom
        self._variability = variability
        self._attr_value = attr_value
        self._created = False

    def __get_prim(self):
        if not self._stage:
            carb.log_error(
                f"Unknown error. Failed to execute CreateUsdAttribute on prim {self._prim_path} since stage is invalid."
            )

            return None

        prim = self._stage.GetPrimAtPath(self._prim_path)
        if not prim:
            carb.log_error(
                f"Unknown error. Failed to execute CreateUsdAttribute on prim {self._prim_path} since prim is not found."
            )
            return None

        return prim

    def do(self):
        prim = self.__get_prim()
        if not prim:
            return

        attr = prim.CreateAttribute(
            name=self._attr_name, typeName=self._attr_type, custom=self._custom, variability=self._variability
        )
        if attr.IsValid():
            self._created = True
            if self._attr_value is not None:
                attr.Set(self._attr_value)

    def undo(self):
        if not self._created:
            return

        prim = self.__get_prim()
        if prim:
            prim.RemoveProperty(self._attr_name)

        self._created = False


class ChangePropertyCommand(omni.kit.commands.Command):
    """Change property value.

    By default, this command changes the value of the property when it exists.
    If the property doesn't exist, **type_to_create_if_not_exist** must be given to explicitly tell
    this command to create a new property with the new type and value.
    """

    # Saving the handle to throttle popups.
    overriden_notification = None

    def __init__(
        self,
        prop_path: str,
        value: Any,
        prev: Any,
        timecode=Usd.TimeCode.Default(),
        type_to_create_if_not_exist: Sdf.ValueTypeNames = None,
        target_layer: Sdf.Layer = None,
        usd_context_name: Union[str, omni.usd.UsdContext, Usd.Stage] = "",
        is_custom: bool = False,
        variability: Sdf.Variability = Sdf.VariabilityVarying
    ):
        """
        Constructor.

        Args:
            prop_path (str): Prim property path.
            value (Any): Value to change to. If it's None, current attribute value is cleared.
            prev (Any): Value to undo to.
            timecode (Usd.TimeCode, optional): The timecode to set property value to. Default is Usd.TimeCode.Default().
            type_to_create_if_not_exist (Sdf.ValueTypeName): If not None and property doesn't exist, a new property will
                be created with given type and value. Default is None.
            target_layer (sdf.Layer, optional): Target layer to write value to. Leave to None to use the current edit target.
            usd_context_name (Union[str, omni.usd.UsdContext, Usd.Stage], optional): Union that could be:
                            * Name of the usd context to work on. Leave to "" to use default USD context.
                            * Instance of UsdContext.
                            * Or stage instance.
                            Default is None, which means the default UsdContext is used.
            is_custom (bool, optional): If the property is created, specifiy if it is a 'custom' property (not part of the Schema).
                Default is False.
            variability (Sdf.Variability, optional): If the property is created, specify the variability. Default is Sdf.VariabilityVarying.
        """

        self._value = value
        self._prev = prev
        self._prop_path = Sdf.Path(prop_path)
        self._time_code = timecode
        self._type_to_create_if_not_exist = type_to_create_if_not_exist
        # Save identifier instead of layer handle to avoid holding it.
        self._target_layer_identifier = target_layer.identifier if target_layer else None

        if isinstance(usd_context_name, omni.usd.UsdContext):
            self._stage = usd_context_name.get_stage()
        elif isinstance(usd_context_name, Usd.Stage):
            self._stage = usd_context_name
        else:
            self._stage = omni.usd.get_context(usd_context_name).get_stage()

        self._do_executed = False
        self.__is_custom = is_custom
        self.__variability = variability
        self._usd_undo = None
        self._prop = None
        self._prim = None

    def _get_target_layer(self):
        # flag to store data to session layer only so it's not serialized
        prop = self._stage.GetPropertyAtPath(self._prop_path)
        if prop.HasCustomDataKey("nonpersistant") and prop.GetCustomDataByKey("nonpersistant"):
            return self._stage.GetSessionLayer()

        if self._target_layer_identifier:
            current_layer = Sdf.Layer.Find(self._target_layer_identifier)
        else:
            # If target layer is not specified, it firstly finds the prop from session layer.
            current_layer, _ = omni.usd.find_spec_on_session_or_its_sublayers(self._stage, self._prop_path)

            # If it's still not existed, using the current edit target layer.
            if not current_layer:
                current_layer = self._stage.GetEditTarget().GetLayer()

        return current_layer

    def _has_overrides_in_stronger_layer(self, current_layer):
        # FIXME: Don't why know it cannot use property.GetPropertyStack() to get the layer stack for this property.
        for layer in self._stage.GetLayerStack(True):
            # No stronger overrides above this layer.
            if layer == current_layer:
                break

            prop_spec = layer.GetPropertyAtPath(self._prop_path)
            if not prop_spec:
                continue

            return prop_spec.layer

        return None

    def _clear_notification_if_dismissed(self):
        if ChangePropertyCommand.overriden_notification and ChangePropertyCommand.overriden_notification.dismissed:
            ChangePropertyCommand.overriden_notification = None

    def _set_prop_value(self) -> bool:
        if self._value is None:
            self._prop.Clear()
        else:
            omni.usd.set_prop_val(self._prop, self._value, self._time_code, auto_target_layer=False)
        return True

    def do(self):
        self._clear_notification_if_dismissed()

        self._do_executed = False
        current_layer = self._get_target_layer()
        # If the target layer is destroyed or not existed, simply return.
        if not current_layer or not self._stage.HasLocalLayer(current_layer):
            carb.log_error(
                f"Failed to change property {self._prop_path} as target layer is not in the local stack of stage."
            )

            return False

        stronger_layer = self._has_overrides_in_stronger_layer(current_layer)

        self._do_executed = True

        # Updates target layer so it could be fixed for undo to make sure changes can be revert back
        # to correct layer.
        self._target_layer_identifier = current_layer.identifier

        prim_path = self._prop_path.GetAbsoluteRootOrPrimPath()
        self._prim = self._stage.GetPrimAtPath(prim_path)
        if not self._prim:
            carb.log_error(
                f"Failed to change property {self._prop_path} as prim does not exist."
            )
            return

        edit_target = self._stage.GetEditTargetForLocalLayer(current_layer)
        edit_target = edit_target.ComposeOver(self._stage.GetEditTarget())

        with Usd.EditContext(self._stage, edit_target):
            self._usd_undo = UsdEditTargetUndo(self._stage.GetEditTarget())
            self._usd_undo.reserve(self._prop_path)

            self._prop = omni.usd.get_prop_at_path(self._prop_path, self._stage)
            if not self._prop:
                if self._type_to_create_if_not_exist is not None:
                    self._prop = self._prim.CreateAttribute(
                        self._prop_path.name, self._type_to_create_if_not_exist, self.__is_custom, self.__variability
                    )

            if self._prop and (not self._set_prop_value()):
                return

        if self._prop and stronger_layer:
            if Sdf.Layer.IsAnonymousLayerIdentifier(stronger_layer.identifier):
                file_name = stronger_layer.identifier
            else:
                url = omni.client.break_url(stronger_layer.identifier)
                file_name = os.path.basename(url.path)

            if (
                not ChangePropertyCommand.overriden_notification or
                ChangePropertyCommand.overriden_notification.dismissed
            ):
                message = f"Overridden in a stronger layer ({file_name}):\n\n{str(self._prop_path)}"
                carb.log_warn(message)
                ChangePropertyCommand.overriden_notification = post_notification(message)

    def undo(self):
        if not self._do_executed or self._usd_undo is None:
            return

        self._usd_undo.undo()

        current_layer = self._get_target_layer()
        # If the target layer is destroyed or not existed, simply return.
        if not current_layer:
            return

        if self._prev is not None:
            prop = omni.usd.get_prop_at_path(self._prop_path)
            if prop:
                edit_target = self._stage.GetEditTargetForLocalLayer(current_layer)
                edit_target = edit_target.ComposeOver(self._stage.GetEditTarget())

                with Usd.EditContext(self._stage, edit_target):
                    omni.usd.set_prop_val(prop, self._prev, self._time_code, auto_target_layer=False)


class RemovePropertyCommand(omni.kit.commands.Command):
    """Remove property."""

    def __init__(self, prop_path: Union[Sdf.Path, str], usd_context_name: Union[str, Usd.Stage] = "",
            remove_from_layers: Optional[Union[List[Union[str, Sdf.Layer]], str, Sdf.Layer]] = None):
        """
        Constructor.

        Args:
            prop_path (str): Path of the property to be removed.
            usd_context_name (str, optional): Usd context name to run the command on. Default is None, which means the default UsdContext is used.
            remove_from_layers (Optional[Union[List[Union[str, Sdf.Layer]], str, Sdf.Layer]]): A list of layers to remove the
                property from. Default to None, which removes the property from all layers. Default is None.
        """

        self._prop_path = Sdf.Path(prop_path)
        self._prim_path = self._prop_path.GetAbsoluteRootOrPrimPath()

        if isinstance(usd_context_name, Usd.Stage):
            self._stage = usd_context_name
        else:
            self._stage = omni.usd.get_context(usd_context_name).get_stage()

        self._usd_undos = []
        # OM-67061: normalize remove_from_layers inputs to list of Sdf.Layer identifiers
        self._layers_to_remove_prop_from = []
        # Record the "remove all" status, in case the layers passed in are all invalid, in which case we should not
        # remove the property from any layer, instead of removing it from all layers
        self._remove_all = remove_from_layers is None
        remove_from_layers = remove_from_layers or []
        if isinstance(remove_from_layers, (str, Sdf.Layer)):
            remove_from_layers = [remove_from_layers]
        for layer in remove_from_layers:
            if isinstance(layer, Sdf.Layer):
                self._layers_to_remove_prop_from.append(layer.identifier)
                continue
            layer_to_remove = Sdf.Find(layer)
            if layer_to_remove is None:
                carb.log_warn(f"Failed to find layer [ {layer} ], ignoring for now.")
                continue
            self._layers_to_remove_prop_from.append(layer_to_remove.identifier)

    def do(self):
        if self._stage:
            layers_to_remove_from = [Sdf.Find(identifier) for identifier in self._layers_to_remove_prop_from]

            with Sdf.ChangeBlock():
                for layer in self._stage.GetLayerStack():
                    # OM-67061: Check if specific layers to remove property from is set, if so, ignore layers that are
                    #  not in specified layers
                    if not self._remove_all and layer not in layers_to_remove_from:
                        continue

                    edit_target = self._stage.GetEditTargetForLocalLayer(layer)
                    edit_target = edit_target.ComposeOver(self._stage.GetEditTarget())

                    prim_path = edit_target.MapToSpecPath(self._prim_path)
                    prop_path = prim_path.AppendProperty(self._prop_path.name)

                    prim_spec = layer.GetPrimAtPath(prim_path)
                    if prim_spec:
                        property_spec = layer.GetPropertyAtPath(prop_path)
                        if property_spec:
                            usd_undo = UsdEditTargetUndo(edit_target)
                            self._usd_undos.append(usd_undo)
                            usd_undo.reserve(self._prop_path)

                            prim_spec.RemoveProperty(property_spec)

    def undo(self):
        with Sdf.ChangeBlock():
            for usd_undo in self._usd_undos:
                usd_undo.undo()


class ChangeMetadataInPrimsCommand(omni.kit.commands.Command):
    """
    Deprecated. Modifies metadata of multiple primitives.

    See command :class:`.ChangeMetadataCommand`, which provides the same functionalities.
    """

    def __init__(self, prim_paths: List[str], key: Any, value: Any, usd_context_name: str = ""):
        """
        Constructor.

        Args:
            prim_paths (List[str]): Prim paths.
            key (Any): Key of metadata to change.
            value (Any): Value of metadata to change to.
            usd_context_name (str, optional): Name of the usd context to work on. Leave to "" to use default USD context.
        """

        self._prim_paths = prim_paths
        self._key = key
        self._value = value
        self._usd_context_name = usd_context_name

    def do(self):
        omni.kit.commands.execute(
            "ChangeMetadata",
            object_paths=self._prim_paths,
            key=self._key,
            value=self._value,
            usd_context_name=self._usd_context_name,
        )

    def undo(self):
        pass


class ChangeMetadataCommand(omni.kit.commands.Command):
    """Modify metadata of multiple objects."""

    def __init__(self, object_paths: List[str], key: Any, value: Any, usd_context_name: str = ""):
        """
        Constructor.

        Args:
            object_paths (List[str]): A list of object paths, which could be prims, attributes, etc.
            key (Any): Key of metadata to change.
            value (Any): Value of metadata to change to.
            usd_context_name (str, optional): Name of the usd context to work on. Leave to "" to use default USD context.
        """

        self._object_paths = object_paths
        self._key = key
        self._value = value
        self._old_values = {}
        self._usd_context_name = usd_context_name

    def do(self):
        stage = omni.usd.get_context(self._usd_context_name).get_stage()
        for path in self._object_paths:
            object = stage.GetObjectAtPath(path)
            if object:
                self._old_values[path] = object.GetMetadata(self._key) if object.HasMetadata(self._key) else None
                object.SetMetadata(self._key, self._value)

    def undo(self):
        stage = omni.usd.get_context(self._usd_context_name).get_stage()
        for path, old_value in self._old_values.items():
            object = stage.GetObjectAtPath(path)
            if object:
                if old_value is not None:
                    object.SetMetadata(self._key, old_value)
                else:
                    object.ClearMetadata(self._key)


class ChangeAttributesColorSpaceCommand(omni.kit.commands.Command):
    """Change attribute color space."""

    def __init__(self, attributes: List[Usd.Attribute], color_space: Any):
        """
        Constructor.

        Args:
            attributes (List[str]): attributes to set color space on.
            color_space: Value of metadata to change to.
        """

        self._attributes = attributes.copy()
        self._color_space = color_space
        self._old_values = {}

    def do(self):
        for attr in self._attributes:
            if attr:
                self._old_values[attr] = attr.GetColorSpace() if attr.HasColorSpace() else None
                attr.SetColorSpace(self._color_space)

    def undo(self):
        for attr, old_value in self._old_values.items():
            if attr:
                if old_value is not None:
                    attr.SetColorSpace(old_value)
                else:
                    attr.ClearColorSpace()


class CreateMdlMaterialPrimCommand(omni.kit.commands.Command, UsdStageHelper):
    """Create a MDL Material."""

    def __init__(
        self,
        mtl_url: str,
        mtl_name: str,
        mtl_path: str,
        select_new_prim: bool = False,
        stage: Optional[Usd.Stage] = None,
        context_name: Optional[str] = None,
    ):
        """
        Constructor.

        Args:
            mtl_url (str): MDL file path.
            mtl_name (str): MDL material name.
            mtl_path (str): Target prim path to create in the stage.
            select_new_prim (bool, optional): If to select the new created material after creation. Default is False.
            stage (Usd.Stage, optional): Stage to operate. Default is None, which means the stage in the default UsdContext is used.
            context_name (str, optional): The usd context to operate. Default is None, which means the default UsdContext is used.
        """

        UsdStageHelper.__init__(self, stage, context_name)

        self._mtl_url = omni.usd.make_path_relative_to_current_edit_target(mtl_url, stage=self._get_stage())
        self._mtl_name = mtl_name
        self._mtl_path = mtl_path
        self._select_new_prim = select_new_prim
        self._author_old_mdl_schema = carb.settings.get_settings().get("/omni.kit.plugin/authorOldMdlSchema")

    def do(self):
        stage = self._get_stage()

        ensure_parents_are_active(stage, self._mtl_path)

        # It's possible that parents of material are inactive so the material path is existed
        # already after it's activated. Regenerating the path to avoid conflicts.
        self._mtl_path = omni.usd.get_stage_next_free_path(stage, self._mtl_path, False)

        # create Looks folder
        parts = str(self._mtl_path).split("/")
        parts.pop()
        prim_path = ""
        for part in parts:
            prim_path = f"{prim_path}/{part}" if part else prim_path
            prim = stage.GetPrimAtPath(Sdf.Path(prim_path)) if prim_path else None
            if prim_path and not prim:
                omni.kit.commands.execute(
                    "CreatePrim",
                    prim_path=prim_path,
                    prim_type="Scope",
                    select_new_prim=False,
                    stage=stage
                )

        # create material
        mat_prim = stage.DefinePrim(self._mtl_path, "Material")
        material_prim = UsdShade.Material.Get(stage, mat_prim.GetPath())
        if material_prim:
            shader_mtl_path = stage.DefinePrim("{}/Shader".format(self._mtl_path), "Shader")
            shader_prim = UsdShade.Shader.Get(stage, shader_mtl_path.GetPath())
            if shader_prim:
                if self._author_old_mdl_schema:
                    shader_out = shader_prim.CreateOutput("out", Sdf.ValueTypeNames.Token)
                    shader_out.SetRenderType("material")
                    material_prim.GetSurfaceOutput().ConnectToSource(shader_out)
                    shader_prim.CreateIdAttr("mdlMaterial")
                    shader_prim.GetPrim().CreateAttribute("module", Sdf.ValueTypeNames.Asset).Set(self._mtl_url)
                    shader_prim.GetPrim().CreateAttribute("name", Sdf.ValueTypeNames.String).Set(self._mtl_name)
                else:
                    shader_out = shader_prim.CreateOutput("out", Sdf.ValueTypeNames.Token)
                    shader_out.SetRenderType("material")

                    material_prim.CreateSurfaceOutput("mdl").ConnectToSource(shader_out)
                    material_prim.CreateVolumeOutput("mdl").ConnectToSource(shader_out)
                    material_prim.CreateDisplacementOutput("mdl").ConnectToSource(shader_out)
                    shader_prim.GetImplementationSourceAttr().Set(UsdShade.Tokens.sourceAsset)
                    shader_prim.SetSourceAsset(Sdf.AssetPath(self._mtl_url.replace("\\", "/")), "mdl")
                    shader_prim.SetSourceAssetSubIdentifier(self._mtl_name, "mdl")
                if self._select_new_prim:
                    omni.usd.get_context().get_selection().set_prim_path_selected(
                        self._mtl_path, True, True, True, True
                    )
            else:
                DeletePrimsCommand([material_prim.GetPath().pathString], stage=stage).do()
                carb.log_warn(f"failed to create shader {shader_mtl_path}")
        else:
            carb.log_warn(f"failed to create prim {mat_prim.GetPath().pathString}")

    def undo(self):
        stage = self._get_stage()
        mat_prim = stage.GetPrimAtPath(self._mtl_path)
        if mat_prim:
            DeletePrimsCommand([mat_prim.GetPath().pathString], stage=stage).do()


class CreateMtlxMaterialPrimCommand(omni.kit.commands.Command, UsdStageHelper):
    """Create a MaterialX material."""

    def __init__(
        self,
        mtlx_url: str,
        base_path: str,
        select_new_prim: bool = False,
        stage: Optional[Usd.Stage] = None,
        context_name: Optional[str] = None
    ):
        """
        Constructor.

        Args:
            mtlx_url (str): Material file path.
            base_path (str): Target prim path to create the material under.
            select_new_prim (bool, optional): If to select new created prim. Default is False.
            stage (Usd.Stage, optional): Stage to operate. Default is None, which means the stage in the default UsdContext is used.
            context_name (str, optional): The usd context to operate. Default is None, which means the default UsdContext is used.
        """

        UsdStageHelper.__init__(self, stage, context_name)

        self._mtlx_url = omni.usd.make_path_relative_to_current_edit_target(mtlx_url, stage=self._get_stage())
        self._base_path = base_path
        self._select_new_prim = select_new_prim

    def do(self):
        stage = self._get_stage()

        ensure_parents_are_active(stage, self._base_path)

        # It's possible that parents of material are inactive so the material path is existed
        # already after it's activated. Regenerating the path to avoid conflicts.
        self._base_path = omni.usd.get_stage_next_free_path(stage, self._base_path, False)

        # create Looks folder
        parts = str(self._base_path).split("/")
        parts.pop()
        prim_path = ""
        for part in parts:
            prim_path = f"{prim_path}/{part}" if part else prim_path
            prim = stage.GetPrimAtPath(Sdf.Path(prim_path)) if prim_path else None
            if prim_path and not prim:
                omni.kit.commands.execute(
                    "CreatePrim",
                    prim_path=prim_path,
                    prim_type="Scope",
                    select_new_prim=False,
                    stage=stage
                )

        # create mtlx reference
        base_prim = stage.DefinePrim(self._base_path, "Scope")
        if base_prim:
            base_prim.GetReferences().AddReference(self._mtlx_url, "/MaterialX")

            if self._select_new_prim:
                omni.usd.get_context().get_selection().set_prim_path_selected(
                    self._base_path, True, True, True, True
                )
        else:
            DeletePrimsCommand([base_prim.GetPath().pathString], stage=stage).do()
            carb.log_warn(f"faild to create prim {self._base_path}")

    def undo(self):
        stage = self._get_stage()
        base_prim = stage.GetPrimAtPath(self._base_path)
        if base_prim:
            DeletePrimsCommand([base_prim.GetPath().pathString], stage=stage).do()


class CreateShaderPrimFromSdrCommand(omni.kit.commands.Command):
    """
    Load the shader specified by 'identifier' from the SDR registry and create a shader prim under
    the specified parent. The parent must be of type UsdShade.Material or UsdShade.NodeGraph.
    """

    def __init__(
        self,
        parent_path: str,
        identifier: str,
        name: str = None,
        select_new_prim: bool = False,
        stage_or_context: Union[str, Usd.Stage, omni.usd.UsdContext] = None,
        node_type = "mdl"
    ):
        """
        Constructor.

        Args:
            parent_path (str): The path of the parent UsdShade.Material or UsdShade.NodeGraph
            identifier (str): The identifer of the node Sdr registry which will be used to define the shader.
            name (str, optional): The name of the UsdShade.Shader prim to be created. If it's None, identifier will be used. Default is None.
            select_new_prim (bool, optional): If to select new created prim. Default is False.
            stage_or_context: (Union[str, Usd.Stage, omni.usd.UsdContext]): Stage or UsdContext applies the changes to.
                It can be instance of Usd.Stage or omni.usd.UsdContext, or context name. By default, it will apply
                the changes to the stage in default UsdContext.
        """

        self._parent_path = parent_path
        self._identifier = identifier
        self._name = name if name else identifier
        self._select_new_prim = select_new_prim
        self._prim_path = "{}/{}".format(self._parent_path, self._name)
        self._usd_context, self._stage = self.__get_context_and_stage(stage_or_context)
        self._node_type = node_type

    def __get_context_and_stage(self, stage_or_context):
        if stage_or_context is None:
            usd_context = omni.usd.get_context()
            stage = usd_context.get_stage()
        elif isinstance(stage_or_context, Usd.Stage):
            usd_context = omni.usd.get_context_from_stage(stage_or_context)
            stage = stage_or_context
        elif isinstance(stage_or_context, omni.usd.UsdContext):
            usd_context = stage_or_context
            stage = usd_context.get_stage()
        elif isinstance(stage_or_context, str):
            usd_context = omni.usd.get_context(stage_or_context)
            if not usd_context:
                raise ValueError(f"Invalid context given for `{stage_or_context}`.")
            stage = usd_context.get_stage()
        else:
            raise ValueError("Invalid param given for `stage_or_context`.")

        return usd_context, stage

    def do(self):
        stage = self._stage

        parent_prim = stage.GetPrimAtPath(self._parent_path)

        if not parent_prim or not parent_prim.IsA(UsdShade.NodeGraph):
            carb.log_warn(f"failed to create shader '{self._prim_path}', parent prim: '{self._parent_path}' does not exist or is not a 'UsdShade.NodeGraph'")
            return None

        node = Sdr.Registry().GetShaderNodeByIdentifierAndType(self._identifier, self._node_type)
        if not node:
            carb.log_warn(f"Failed to create shader for prim: '{self._prim_path}' identifier: '{self._identifier}' node type: '{self._node_type}'.")
            return None

        # It's possible that parents of material are inactive so the material path is existed
        # already after it's activated. Regenerating the path to avoid conflicts.
        self._prim_path = Sdf.Path(omni.usd.get_stage_next_free_path(stage, self._prim_path, False))
        ensure_parents_are_active(stage, self._prim_path)

        prim = stage.DefinePrim(self._prim_path, "Shader")
        shader_prim = UsdShade.Shader.Get(stage, prim.GetPath())

        if shader_prim:
            shader_prim.CreateIdAttr(self._identifier)

            for output_name in node.GetOutputNames():
                sdr_output = node.GetOutput(output_name)
                usdshade_output = None

                if sdr_output:
                    ndr_type_indicator = sdr_output.GetTypeAsSdfType()
                    type_name = ndr_type_indicator[1]

                    if type_name in ["terminal", "struct", "BSDF"]:
                        type_name = "token"

                    if type_name:
                        type_name = Sdf.ValueTypeNames.Find(type_name)
                        if not type_name:
                            carb.log_warn(f"Shader: '{self._prim_path}' output: '{output_name}' cannot find SdfValueTypeName for: '{ndr_type_indicator[1]}'")
                            self.undo()
                            return None
                    else:
                        type_name = ndr_type_indicator[0]

                    usdshade_output = shader_prim.CreateOutput(output_name, type_name)

                if not usdshade_output:
                    carb.log_warn(f"Shader: '{self._prim_path}' unable to create output port '{output_name}'")
                    self.undo()
                    return None

            if self._select_new_prim:
                omni.usd.get_context().get_selection().set_prim_path_selected(
                    self._prim_path.pathString, True, True, True, True
                )

            return shader_prim

        self.undo()
        return None

    def undo(self):
        carb.log_warn(f"failed to create shader: '{self._prim_path}'")

        stage = self._stage
        prim = stage.GetPrimAtPath(self._prim_path)

        if prim:
            DeletePrimsCommand([prim.GetPath().pathString], stage=stage).do()


class CreatePreviewSurfaceMaterialPrimCommand(omni.kit.commands.Command):
    """Create a USD Preview Surface Material."""

    def __init__(self, mtl_path: str, shader_prim_name="Shader", select_new_prim: bool = False):
        """
        Constructor.

        Args:
            mtl_path (str): The material path to create.
            shader_prim_name (str, optional): The name of the root shader prim. Default is "Shader".
            select_new_prim (bool, optional): If to select new created prim. Default is False.
        """

        self._mtl_path = mtl_path
        self._select_new_prim = select_new_prim
        self._shader_prim_name = shader_prim_name

    def do(self):
        stage = omni.usd.get_context().get_stage()

        # It's possible that parents of material are inactive so the material path is existed
        # already after it's activated. Regenerating the path to avoid conflicts.
        self._mtl_path = omni.usd.get_stage_next_free_path(stage, self._mtl_path, False)

        ensure_parents_are_active(stage, self._mtl_path)

        prim = stage.DefinePrim(self._mtl_path, "Material")
        material_prim = UsdShade.Material.Get(stage, prim.GetPath())
        shader_prim_path = None
        if material_prim:
            shader_prim = CreateShaderPrimFromSdrCommand(prim.GetPath().pathString, "UsdPreviewSurface", name=self._shader_prim_name).do()

            if shader_prim:
                shader_prim_path = shader_prim.GetPath().pathString

                surface_out = shader_prim.GetOutput("surface")
                if surface_out:
                    material_prim.CreateSurfaceOutput().ConnectToSource(surface_out)

                displacement_out = shader_prim.GetOutput("displacement")
                if displacement_out:
                    material_prim.CreateDisplacementOutput().ConnectToSource(displacement_out)

                if self._select_new_prim:
                    omni.usd.get_context().get_selection().set_prim_path_selected(self._mtl_path, True, True, True, True)

        else:
            self.undo()

        return (self._mtl_path, shader_prim_path)

    def undo(self):
        carb.log_warn(f"failed to create material: '{self._mtl_path}'")

        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath(self._mtl_path)
        if prim:
            DeletePrimsCommand([prim.GetPath().pathString], stage=stage).do()


class CreatePreviewSurfaceTextureMaterialPrimCommand(omni.kit.commands.Command):
    """Create a USD Preview Surface Texture Material."""

    def __init__(self, mtl_path: Union[str, Sdf.Path], select_new_prim: bool = False):
        """
        Constructor.

        Args:
            mtl_path (Union[str, Sdf.Path]): The material path to create.
            select_new_prim (bool, optional): If to select new created prim. Default is False.
        """

        self._mtl_path = Sdf.Path(mtl_path)
        self._select_new_prim = select_new_prim

    def _create_input(self, shader, input_name, value=None):
        api = UsdShade.NodeDefAPI(shader.GetPrim())
        if not api:
            carb.log_warn(f"Unable to apply UsdShade.NodeDefAP to: '{shader.GetPath().pathString}'")
            return None

        sdr_node = api.GetShaderNodeForSourceType("mdl")
        if not sdr_node:
            carb.log_warn(f"Unable to get shader node for: '{shader.GetPath().pathString}'")
            return None

        sdr_input = sdr_node.GetShaderInput(input_name)
        if not sdr_input:
            carb.log_warn(f"Unable to get input: '{input_name}' for: '{shader.GetPath().pathString}'")
            return None

        ndr_type_indicator = sdr_input.GetTypeAsSdfType()

        type_name = ndr_type_indicator[1]

        if type_name in ["terminal", "struct", "BSDF"]:
            type_name = "token"

        if type_name:
            type_name = Sdf.ValueTypeNames.Find(type_name)
            if not type_name:
                carb.log_warn(f"Shader: '{shader.GetPath().pathString}' input: '{input_name}' cannot find SdfValueTypeName for: '{ndr_type_indicator[1]}'")
                return None
        else:
            type_name = ndr_type_indicator[0]

        input_port = shader.CreateInput(input_name, type_name)
        if not input_port:
            carb.log_warn(f"Unable to create input port: '{input_name}' of type: '{input_type}' for shader: '{shader.GetPath().pathString}'")
            return None

        if value and not input_port.Set(value):
            carb.log_warn(f"Unable to set input port: '{input_name}' to: '{value}' for shader: '{shader.GetPath().pathString}'")
            return None

        return input_port

    def _get_output(self, shader, output_name):
        output_port = shader.GetOutput(output_name)

        if not output_port:
            carb.log_warn(f"unable to get output port '{output_name}' for shader: '{shader.GetPath().pathString}'")
            return None

        return output_port

    def _createAndConnectTexture(self, name, input_shader, input_port_name, output_port_name, params, primvar_reader_output_port):
        texture_shader = CreateShaderPrimFromSdrCommand(self._mtl_path, "UsdUVTexture", name=name).do()
        if not texture_shader:
            return False

        input_port = self._create_input(texture_shader, "st")
        if not input_port:
            return False

        if not input_port.ConnectToSource(primvar_reader_output_port):
            carb.log_warn(f"unable to connect 'st' to: '{primvar_reader_output_port.GetName()}' shader: '{shader.GetPath().pathString}'")
            return False

        input_port = self._create_input(input_shader, input_port_name)
        if not input_port:
            return False

        output_port = self._get_output(texture_shader, output_port_name)
        if not output_port:
            return False

        if not input_port.ConnectToSource(output_port):
            carb.log_warn(f"unable to connect 'st' to: '{output_port_name}' shader: '{shader.GetPath().pathString}'")
            return False

        for input_port_name, value in params.items():
            if not self._create_input(texture_shader, input_port_name, value):
                return False

        return True

    def do(self):
        (self._mtl_path, shader_prim_path) = CreatePreviewSurfaceMaterialPrimCommand(self._mtl_path, shader_prim_name="PreviewSurfaceTexture").do()

        if shader_prim_path:
            stage = omni.usd.get_context().get_stage()
            shader = UsdShade.Shader.Get(stage, shader_prim_path)

            if not shader:
                carb.log_warn(f"unable to get shader: {shader_prim_path}")
                return False

            primvar_reader_shader = CreateShaderPrimFromSdrCommand(self._mtl_path, "UsdPrimvarReader_float2", name="st").do()
            if not primvar_reader_shader:
                return False

            primvar_reader_output_port = self._get_output(primvar_reader_shader, "result")
            if not primvar_reader_output_port:
                return False

            usd_shade_input = self._create_input(primvar_reader_shader, "varname", "st")
            if not usd_shade_input:
                return False

            params = {}

            success = self._createAndConnectTexture("diffuseColorTex", shader, "diffuseColor", "rgb", params, primvar_reader_output_port)
            success |= self._createAndConnectTexture("metallicTex", shader, "metallic", "r", params, primvar_reader_output_port)
            success |= self._createAndConnectTexture("roughnessTex", shader, "roughness", "r", params, primvar_reader_output_port)

            params = {
                "sourceColorSpace": "raw",
                "fallback": Gf.Vec4f(0.0, 0.0, 1.0, 1.0)
            }

            success |= self._createAndConnectTexture("normalTex", shader, "normal", "rgb", params, primvar_reader_output_port)

            if success:
                if self._select_new_prim:
                    omni.usd.get_context().get_selection().set_prim_path_selected(self._mtl_path, True, True, True, True)

                return

        self.undo()

    def undo(self):
        carb.log_warn(f"failed to create material '{self._mtl_path}'")

        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath(self._mtl_path)
        if prim:
            DeletePrimsCommand([prim.GetPath().pathString], stage=stage).do()


class ClearCurvesSplitsOverridesCommand(omni.kit.commands.Command):
    """Clear Curves Splits Overrides."""

    def do(self):
        stage = omni.usd.get_context().get_stage()
        layer = stage.GetEditTarget().GetLayer()
        with Sdf.ChangeBlock():
            for prim in [x for x in stage.Traverse() if x.GetTypeName() in ["BasisCurves"]]:
                primSpec = layer.GetPrimAtPath(prim.GetPath())
                for attrName in ["primvars:numSplitsOverride", "primvars:numSplits"]:
                    propertySpec = layer.GetPropertyAtPath(prim.GetPath().AppendProperty(attrName))
                    if propertySpec:
                        primSpec.RemoveProperty(propertySpec)


class ClearRefinementOverridesCommand(omni.kit.commands.Command):
    """Clear Refinement Overrides."""

    def __init__(self):
        self._undo_data = {"refinementOverrideImplVersion": None, "prim_attrs": {}}

    def do(self):
        stage = omni.usd.get_context().get_stage()
        layer = stage.GetEditTarget().GetLayer()
        custom_data = layer.customLayerData
        with Sdf.ChangeBlock():
            if "refinementOverrideImplVersion" in custom_data:
                self._undo_data["refinementOverrideImplVersion"] = custom_data["refinementOverrideImplVersion"]
                del custom_data["refinementOverrideImplVersion"]
                layer.customLayerData = custom_data

            for prim in [
                x for x in stage.Traverse() if x.GetTypeName() in ["Mesh", "Sphere", "Cylinder", "Cone", "Capsule"]
            ]:
                primSpec = layer.GetPrimAtPath(prim.GetPath())
                for attrName in ["refinementEnableOverride", "refinementLevel"]:
                    propertySpec = layer.GetPropertyAtPath(prim.GetPath().AppendProperty(attrName))
                    if propertySpec:
                        # keep undo copy
                        if not prim.GetPath().pathString in self._undo_data["prim_attrs"]:
                            self._undo_data["prim_attrs"][prim.GetPath().pathString] = {}
                        attr = prim.GetAttribute(attrName)
                        self._undo_data["prim_attrs"][prim.GetPath().pathString][attrName] = attr.Get()
                        # remove property
                        primSpec.RemoveProperty(propertySpec)

    def undo(self):
        stage = omni.usd.get_context().get_stage()
        layer = stage.GetEditTarget().GetLayer()
        custom_data = layer.customLayerData
        with Sdf.ChangeBlock():
            if self._undo_data["refinementOverrideImplVersion"]:
                custom_data["refinementOverrideImplVersion"] = self._undo_data["refinementOverrideImplVersion"]
                self._undo_data["refinementOverrideImplVersion"] = None
                layer.customLayerData = custom_data

        # create attributes 1st as its problematic to CreateAttribute & Set inside a Sdf.ChangeBlock
        for prim_path in self._undo_data["prim_attrs"]:
            prim = stage.GetPrimAtPath(prim_path)
            prim.CreateAttribute("refinementEnableOverride", Sdf.ValueTypeNames.Bool)
            prim.CreateAttribute("refinementLevel", Sdf.ValueTypeNames.Int)

        # set attributes
        with Sdf.ChangeBlock():
            for prim_path in self._undo_data["prim_attrs"]:
                attr_data = self._undo_data["prim_attrs"][prim_path]
                prim = stage.GetPrimAtPath(prim_path)
                prim.GetAttribute("refinementEnableOverride").Set(attr_data["refinementEnableOverride"])
                prim.GetAttribute("refinementLevel").Set(attr_data["refinementLevel"])
            self._undo_data["prim_attrs"] = {}


class RelationshipTargetBase(omni.kit.commands.Command):
    """Base class of relationship related commands."""

    def __init__(self, relationship: Usd.Relationship, target: Sdf.Path):
        self._stage = weakref.ref(relationship.GetStage())
        self._rel_path = relationship.GetPath()
        self._target = target
        self._usd_undo = None

    def _get_relationship(self):
        stage = self._stage()
        if stage:
            rel = stage.GetRelationshipAtPath(self._rel_path)
            return rel
        return None

    def undo(self):
        if self._usd_undo is not None:
            self._usd_undo.undo()


class AddRelationshipTargetCommand(RelationshipTargetBase):
    """Add target to a relationship."""

    def __init__(self, relationship: Usd.Relationship, target: Sdf.Path, position: Usd.ListPosition = Usd.ListPositionBackOfPrependList):
        """Constructor.

        Args:
            relationship (Usd.Relationship): Relationship handle.
            target (Sdf.Path): The target path to add into the target list of relationship.
            position (Usd.ListPosition, optional): List position to add the target path to. Defaults to Usd.ListPositionBackOfPrependList.
        """

        super().__init__(relationship, target)
        self._position = position

    def do(self):
        rel = self._get_relationship()
        if rel:
            self._usd_undo = UsdEditTargetUndo(rel.GetPrim().GetStage().GetEditTarget())
            self._usd_undo.reserve(rel.GetPath())
            rel.AddTarget(self._target, self._position)


class RemoveRelationshipTargetCommand(RelationshipTargetBase):
    """Remove target from a relationship."""

    def __init__(self, relationship: Usd.Relationship, target: Sdf.Path):
        """Constructor.

        Args:
            relationship (Usd.Relationship): Relationship handle.
            target (Sdf.Path): Target path to remove from relationship list.
        """

        super().__init__(relationship, target)

    def do(self):
        rel = self._get_relationship()
        if rel:
            self._usd_undo = UsdEditTargetUndo(rel.GetPrim().GetStage().GetEditTarget())
            self._usd_undo.reserve(rel.GetPath())
            rel.RemoveTarget(self._target)


class SetRelationshipTargetsCommand(RelationshipTargetBase):
    """Set target(s) to a relationship."""

    def __init__(self, relationship: Usd.Relationship, targets: List[Sdf.Path]):
        """
        Constructor.

        Args:
            relationship (Usd.Relationship): Relationship handle.
            targets (List[Sdf.Path]): A list of target paths to set for the relationship.
        """

        super().__init__(relationship, None)
        self._targets = targets

    def do(self):
        rel = self._get_relationship()
        if rel:
            self._usd_undo = UsdEditTargetUndo(rel.GetPrim().GetStage().GetEditTarget())
            self._usd_undo.reserve(rel.GetPath())
            rel.SetTargets(self._targets)


class ReferenceCommandBase(omni.kit.commands.Command):
    """Base class for reference related commands."""

    def __init__(self, stage, prim_path: Sdf.Path, reference: Sdf.Reference):
        self._prim_path = prim_path
        self._reference = reference
        self._stage = weakref.ref(stage)
        self._reference_list = None
        self._had_prim_spec = False
        self._usd_undo = None

    def _get_references(self):
        stage = self._stage()
        if stage:
            prim = stage.GetPrimAtPath(self._prim_path)
            if prim:
                return prim.GetReferences()
        return None

    def _reserve_references(self):
        self._usd_undo = UsdEditTargetUndo(self._stage().GetEditTarget())
        self._usd_undo.reserve(self._prim_path, Sdf.PrimSpec.ReferencesKey)

    def _is_reference_valid(self):
        """Currently only checks for crate file version compatibility."""
        return omni.usd.is_usd_crate_file_version_supported(self._reference.assetPath)

    def undo(self):
        if self._usd_undo is not None:
            self._usd_undo.undo()

class AddReferenceCommand(ReferenceCommandBase):
    """Add reference to primitive."""

    def __init__(
        self, stage: Usd.Stage, prim_path: Sdf.Path, reference: Sdf.Reference, position: Usd.ListPosition = Usd.ListPositionBackOfPrependList
    ):
        """Constructor.

        Args:
            stage (Usd.Stage): The stage to operate.
            prim_path (Sdf.Path): The prim path to add reference.
            reference (Sdf.Reference): The reference to be added.
            position (Usd.ListPosition): The list position to add the reference. Defaults to Usd.ListPositionBackOfPrependList.
        """

        super().__init__(stage, prim_path, reference)
        self._position = position

    def do(self):
        if self._is_reference_valid() is False:
            return

        references = self._get_references()
        if references:
            try:
                self._reserve_references()
                references.AddReference(self._reference, self._position)
                return None
            except Tf.ErrorException as exc:
                return exc

class RemoveReferenceCommand(ReferenceCommandBase):
    """Remove specified reference from primitive."""

    def __init__(self, stage: Usd.Stage, prim_path: Sdf.Path, reference: Sdf.Reference):
        """Constructor.

        Args:
            stage (Usd.Stage): The stage to operate.
            prim_path (Sdf.Path): The prim path to remove the reference.
            reference (Sdf.Reference): The specified reference to be removed.
        """

        super().__init__(stage, prim_path, reference)

    def do(self):
        references = self._get_references()
        if references:
            self._reserve_references()
            references.RemoveReference(self._reference)

class ReplaceReferenceCommand(ReferenceCommandBase):
    """Replace the specified reference with a new one."""

    def __init__(self, stage: Usd.Stage, prim_path: Sdf.Path, old_reference: Sdf.Reference, new_reference: Sdf.Reference):
        """
        Constructor.

        Args:
            stage (Usd.Stage): The stage to operate.
            prim_path (Sdf.Path): The prim path to replace reference.
            old_reference (Sdf.Reference): The reference handle to be replaced.
            new_reference (Sdf.Reference): The new reference handle.
        """

        super().__init__(stage, prim_path, old_reference)
        self._new_reference = new_reference

    def do(self):
        stage = self._stage()
        if stage:
            if self._is_reference_valid() is False:
                return

            self._reserve_references()

            remove_cmd = RemoveReferenceCommand(stage, self._prim_path, self._reference)
            remove_cmd.do()

            add_cmd = AddReferenceCommand(stage, self._prim_path, self._new_reference)
            return add_cmd.do()

class PayloadCommandBase(omni.kit.commands.Command):
    """Base class for payload related commands."""

    def __init__(self, stage, prim_path: Sdf.Path, payload: Sdf.Payload):
        self._prim_path = prim_path
        self._payload = payload
        self._stage = weakref.ref(stage)
        self._usd_undo = None

    def _get_payloads(self):
        stage = self._stage()
        if stage:
            prim = stage.GetPrimAtPath(self._prim_path)
            if prim:
                return prim.GetPayloads()
        return None

    def _reserve_payloads(self):
        self._usd_undo = UsdEditTargetUndo(self._stage().GetEditTarget())
        self._usd_undo.reserve(self._prim_path, Sdf.PrimSpec.PayloadKey)

    def _is_payload_valid(self):
        """Currently only checks for crate file version compatibility."""
        return omni.usd.is_usd_crate_file_version_supported(self._payload.assetPath, stage=self._stage())

    def undo(self):
        if self._usd_undo is not None:
            self._usd_undo.undo()

class AddPayloadCommand(PayloadCommandBase):
    """Add a payload to primitive."""

    def __init__(self, stage: Usd.Stage, prim_path: Sdf.Path, payload: Sdf.Payload, position=Usd.ListPositionBackOfPrependList):
        """
        Constructor.

        Args:
            stage (Usd.Stage): The stage to operate.
            prim_path (Sdf.Path): The prim path to add payload.
            payload (Sdf.Payload): The payload to be added.
            position (Usd.ListPosition): The list position to add the payload. Defaults to Usd.ListPositionBackOfPrependList.
        """

        super().__init__(stage, prim_path, payload)
        self._position = position

    def do(self):
        if self._is_payload_valid() is False:
            return

        payloads = self._get_payloads()
        if payloads:
            try:
                self._reserve_payloads()
                payloads.AddPayload(self._payload, self._position)
                return None
            except Tf.ErrorException as exc:
                return exc

class RemovePayloadCommand(PayloadCommandBase):
    """Remove specified payload from primitive."""

    def __init__(self, stage, prim_path: Sdf.Path, payload: Sdf.Payload):
        """Constructor.

        Args:
            stage (Usd.Stage): The stage to operate.
            prim_path (Sdf.Path): The prim path to remove the payload.
            payload (Sdf.Payload): The specified payload to be removed.
        """

        super().__init__(stage, prim_path, payload)

    def do(self):
        payloads = self._get_payloads()
        if payloads:
            self._reserve_payloads()
            payloads.RemovePayload(self._payload)

class ReplacePayloadCommand(PayloadCommandBase):
    """Replace the specified reference with a new one."""

    def __init__(self, stage, prim_path: Sdf.Path, old_payload: Sdf.Payload, new_payload: Sdf.Payload):
        """
        Constructor.

        Args:
            stage (Usd.Stage): The stage to operate.
            prim_path (Sdf.Path): The prim path to replace payload.
            old_payload (Sdf.Payload): The payload to be replaced.
            new_payload (Sdf.Payload): The new payload handle.
        """

        super().__init__(stage, prim_path, old_payload)
        self._new_payload = new_payload

    def do(self):
        stage = self._stage()
        if stage:
            if self._is_payload_valid() is False:
                return

            self._reserve_payloads()

            remove_cmd = RemovePayloadCommand(stage, self._prim_path, self._payload)
            remove_cmd.do()

            add_cmd = AddPayloadCommand(stage, self._prim_path, self._new_payload)
            return add_cmd.do()

class CreatePrimCommandBase(omni.kit.commands.Command):
    """Base class to create a prim (and remove when undo)."""

    def __init__(self, usd_context: omni.usd.UsdContext, path_to: Sdf.Path, asset_path: str, select_prim: bool = True):
        """Constructor.

        Args:
            usd_context (omni.usd.UsdContext): UsdContext this command to run on.
            path_to (Sdf.Path): Path to create a new prim.
            asset_path (str): The asset it's necessary to add to references.
            select_prim (bool, optional):If to select the newly created UsdPrim. Defaults to True.
        """

        # TODO (105): Make these private and only cache UsdContext name
        self._usd_context = usd_context
        self._selection = self._usd_context.get_selection()

        stage = self._usd_context.get_stage()
        path_to = Sdf.Path(omni.usd.get_stage_next_free_path(stage, str(path_to), False))

        self._asset_path = asset_path
        self._path_to = path_to
        self._previous_selection = None
        self.__select_prim = select_prim

    def do(self):
        if not self.__select_prim:
            return

        # OMPE-37291: Check if crate file version is supported (this check ignores file if it's not USD crate file)
        if omni.usd.is_usd_crate_file_version_supported(self._asset_path) is False:
            return

        # Save the selection and select the created prim.
        self._previous_selection = self._selection.get_selected_prim_paths()
        async def select_prims(self: CreatePrimCommandBase):
            self._selection.set_selected_prim_paths([str(self._path_to)], False)

        import asyncio
        asyncio.ensure_future(select_prims(self))

    def undo(self):
        delete_cmd = DeletePrimsCommand([self._path_to], self._usd_context.get_stage())
        delete_cmd.do()

        # Restore selection
        if self._previous_selection is not None:
            self._selection.set_selected_prim_paths(self._previous_selection, False)


class CreateReferenceCommand(CreatePrimCommandBase):
    """Create a new prim with reference."""

    def __init__(
        self,
        usd_context: omni.usd.UsdContext,
        path_to: Sdf.Path,
        asset_path: str = None,
        prim_path: Sdf.Path = None,
        instanceable: bool = True,
        select_prim: bool = True,
    ):
        """Constructor.

        Args:
            usd_context (omni.usd.UsdContext): UsdContext this command to run on.
            path_to (Sdf.Path): Path to create a new prim.
            asset_path (str, optional): The asset path for reference. If not specified, it's a prim reference. Defaults to None.
            prim_path (Sdf.Path): The prim path to reference. Defaults to None.
            instanceable (bool, optional): If to set the prim instanceable. It works together with `/persistent/app/stage/instanceableOnCreatingReference` setting.
                Defaults to True.
            select_prim (bool): If to select the created primitive.
                Defaults to True.
        """

        super().__init__(usd_context, path_to, asset_path, select_prim)
        if prim_path:
            self._prim_path = Sdf.Path(prim_path)
        else:
            self._prim_path = Sdf.Path.emptyPath
        self._instanceable = instanceable
        self._settings = carb.settings.get_settings()

    def do(self):
        stage = self._usd_context.get_stage()

        ensure_parents_are_active(stage, self._path_to)

        prim_to = stage.DefinePrim(self._path_to)

        default_prim_is_xform = False
        if self._asset_path:
            # FIXME: OM-50609: WA to avoid crash if target_path includes format symbols.
            anonymous_layer = Sdf.Layer.CreateAnonymous()
            asset_layer = Sdf.Layer.FindOrOpen(self._asset_path)
            if asset_layer:
                ref_stage = Usd.Stage.Open(asset_layer, anonymous_layer)
                default_prim = ref_stage.GetDefaultPrim()
                if default_prim and default_prim.IsA(UsdGeom.Xform):
                    default_prim_is_xform = True
                elif not default_prim:
                    post_notification(
                        "The reference doesn't have a default prim set, which means that some prims may be missing."
                    )
        else:
            ref_stage = None

        with Sdf.ChangeBlock():
            edit_target = stage.GetEditTarget()
            current_layer = edit_target.GetLayer()
            prim_spec = Sdf.CreatePrimInLayer(current_layer, self._path_to)
            prim_spec.specifier = Sdf.SpecifierDef
            if self._asset_path:
                relative_url = omni.client.make_relative_url_if_possible(
                    current_layer.identifier, self._asset_path
                )
            else:
                relative_url = ""
            # OMPE-9290: If the current relative url is an absolute local path, and the layer is non-local, prepend
            #  the `file` scheme to the local path to make sure it resolves correctly; Currently on Linux, an abs
            #  local path may get recognized as relative without the explicit file scheme
            if omni.client.is_local_url(relative_url) and not omni.client.is_local_url(current_layer.identifier):
                relative_url = omni.client.normalize_url(omni.client.make_file_url_if_possible(relative_url))
            prim_spec.referenceList.Prepend(Sdf.Reference(relative_url, self._prim_path))

            # Set instanceable
            instanceable_on_create = self._settings.get(
                PERSISTENT_SETTINGS_PREFIX + "/app/stage/instanceableOnCreatingReference"
            )

            if default_prim_is_xform and instanceable_on_create:
                prim_to.SetInstanceable(
                    self._instanceable
                )

        rotate_ref = self._settings.get("/exts/omni.usd/commands/rotateOnCreatingReference")
        if default_prim_is_xform and rotate_ref and ref_stage:
            ref_up = UsdGeom.GetStageUpAxis(ref_stage)
            curr_up = UsdGeom.GetStageUpAxis(stage)

            if ref_up != curr_up:
                ref_xform_mat = UsdGeom.Xformable(prim_to).GetLocalTransformation()
                adj_mat = Gf.Matrix4d()
                if ref_up == "Y":
                    adj_mat = Gf.Matrix4d(
                        0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0
                    )
                elif ref_up == "Z":
                    adj_mat = Gf.Matrix4d(
                        0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0
                    )
                if adj_mat != Gf.Matrix4d():
                    ref_xform_mat = ref_xform_mat * adj_mat
                    omni.kit.commands.execute(
                        "TransformPrim", path=prim_to.GetPrimPath(), new_transform_matrix=ref_xform_mat
                    )

        super().do()

        return self._path_to

    def undo(self):
        # Dereference this. Otherwise it fires error: Cannot remove ancestral prim
        stage = self._usd_context.get_stage()
        prim_to = stage.GetPrimAtPath(self._path_to)
        prim_to.GetReferences().ClearReferences()

        super().undo()


class CreatePayloadCommand(CreatePrimCommandBase):
    """Create a new prim with payload."""

    def __init__(
        self,
        usd_context: omni.usd.UsdContext,
        path_to: Sdf.Path,
        asset_path: str = None,
        prim_path: Sdf.Path = None,
        instanceable: bool = True,
        select_prim: bool = True,
    ):
        """Constructor.

        Args:
            usd_context (omni.usd.UsdContext): UsdContext this command to run on.
            path_to (Sdf.Path): Path to create a new prim.
            asset_path (str, optional): The asset path to payload. Defaults to None.
            prim_path (Sdf.Path): The prim path to payload. Defaults to None.
            instanceable (bool, optional): If to set the prim instanceable. It works together with `/persistent/app/stage/instanceableOnCreatingReference` setting.
                Defaults to True.
            select_prim (bool): If to select the created primitive.
                Defaults to True.
        """

        super().__init__(usd_context, path_to, asset_path, select_prim)
        if prim_path:
            self._prim_path = Sdf.Path(prim_path)
        else:
            self._prim_path = Sdf.Path.emptyPath

        self._instanceable = instanceable
        self._settings = carb.settings.get_settings()

    def do(self):
        stage = self._usd_context.get_stage()

        ensure_parents_are_active(stage, self._path_to)

        default_prim_is_xform = False
        if self._asset_path:
            # FIXME: OM-50609: WA to avoid crash if target_path includes format symbols.
            anonymous_layer = Sdf.Layer.CreateAnonymous()
            asset_layer = Sdf.Layer.FindOrOpen(self._asset_path)
            if asset_layer:
                ref_stage = Usd.Stage.Open(asset_layer, anonymous_layer)
                default_prim = ref_stage.GetDefaultPrim()
                if default_prim and default_prim.IsA(UsdGeom.Xform):
                    default_prim_is_xform = True
                elif not default_prim:
                    post_notification(
                        "The payload doesn't have a default prim set, which means that some prims may be missing."
                    )
        else:
            ref_stage = None

        with Sdf.ChangeBlock():
            edit_target = stage.GetEditTarget()
            current_layer = edit_target.GetLayer()
            prim_spec = Sdf.CreatePrimInLayer(current_layer, self._path_to)
            prim_spec.specifier = Sdf.SpecifierDef
            if self._asset_path:
                relative_url = omni.client.make_relative_url_if_possible(
                    current_layer.identifier, self._asset_path
                )
            else:
                relative_url = ""
            # OMPE-9290: If the current relative url is an absolute local path, and the layer is non-local, prepend
            #  the `file` scheme to the local path to make sure it resolves correctly; Currently on Linux, an abs
            #  local path may get recognized as relative without the explicit file scheme
            if omni.client.is_local_url(relative_url) and not omni.client.is_local_url(current_layer.identifier):
                relative_url = omni.client.normalize_url(omni.client.make_file_url_if_possible(relative_url))
            prim_spec.payloadList.Prepend(Sdf.Payload(relative_url, self._prim_path))

            # Set instanceable
            instanceable_on_create = self._settings.get(
                PERSISTENT_SETTINGS_PREFIX + "/app/stage/instanceableOnCreatingReference"
            )

            if default_prim_is_xform and instanceable_on_create:
                prim_spec.SetInstanceable(
                    self._instanceable
                )

        rotate_ref = self._settings.get("/exts/omni.usd/commands/rotateOnCreatingReference")
        if default_prim_is_xform and rotate_ref and ref_stage:
            prim_to = stage.GetPrimAtPath(self._path_to)
            ref_up = UsdGeom.GetStageUpAxis(ref_stage)
            curr_up = UsdGeom.GetStageUpAxis(stage)

            if ref_up != curr_up:
                ref_xform_mat = UsdGeom.Xformable(prim_to).GetLocalTransformation()
                adj_mat = Gf.Matrix4d()
                if ref_up == "Y":
                    adj_mat = Gf.Matrix4d(
                        0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0
                    )
                elif ref_up == "Z":
                    adj_mat = Gf.Matrix4d(
                        0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0
                    )
                if adj_mat != Gf.Matrix4d():
                    ref_xform_mat = ref_xform_mat * adj_mat
                    omni.kit.commands.execute(
                        "TransformPrim", path=prim_to.GetPrimPath(), new_transform_matrix=ref_xform_mat
                    )

        super().do()

        return self._path_to

    def undo(self):
        # Dereference this. Otherwise it fires error: Cannot remove ancestral prim
        stage = self._usd_context.get_stage()
        prim_to = stage.GetPrimAtPath(self._path_to)
        prim_to.GetPayloads().ClearPayloads()

        super().undo()


class CreateAudioPrimFromAssetPathCommand(CreatePrimCommandBase):
    """Create a new Audio primitive from asset path."""

    def __init__(self, usd_context: omni.usd.UsdContext, path_to: Sdf.Path, asset_path: str, select_prim: bool = True):
        """Constructor.

        Args:
            usd_context (omni.usd.UsdContext): UsdContext this command to run on.
            path_to (Sdf.Path): Path to create a new prim.
            asset_path (str): The asset path of the audio file.
            select_prim (bool, optional): If to select the newly created UsdPrim or not. Defaults to True.
        """
        super().__init__(usd_context, path_to, asset_path, select_prim)

    def do(self):
        sound = OmniAudioSchema.OmniSound.Define(self._usd_context.get_stage(), self._path_to)
        if sound:
            sound.CreateFilePathAttr(self._asset_path)
            super().do()

        return self._path_to


class ToggleActivePrimsCommand(omni.kit.commands.Command):
    """Toggle the active state of prims."""

    def __init__(
        self, prim_paths: List[Sdf.Path], stage_or_context: Union[Usd.Stage, str, omni.usd.UsdContext] = None,
        active: Union[bool, None] = None
    ):
        """
        Constructor.

        Args:
            prim_paths (List[Sdf.Path]): A list of prim paths.
            stage_or_context (Union[str, Usd.Stage, omni.usd.UsdContext], optional): Stage or UsdContext applies the changes to.
                It can be instance of Usd.Stage or omni.usd.UsdContext, or context name. By default, it will apply
                the changes to the stage in default UsdContext.
            active (Union[bool, None], optional): If active flag is not None, it will set the active states to the value specified
                by it. Otherwise, it will revert the active states of prims. Defaults to None.
        """

        self.__usd_context, self.__stage = get_context_and_stage(stage_or_context)
        self.__prim_paths = [Sdf.Path(prim_path) for prim_path in prim_paths]
        self.__prim_paths = Sdf.Path.RemoveDescendentPaths(self.__prim_paths)
        self.__old_active_states = {}
        self.__influenced_layer_identifier = None
        self.__old_selected_prim_paths = None
        self.__active = active

    def do(self):
        if self.__usd_context:
            self.__old_selected_prim_paths = self.__usd_context.get_selection().get_selected_prim_paths()
        else:
            self.__old_selected_prim_paths = None

        valid_prim_paths = []

        edit_target_layer = self.__stage.GetEditTarget().GetLayer()
        self.__influenced_layer_identifier = edit_target_layer.identifier
        with Sdf.ChangeBlock():
            for prim_path in self.__prim_paths:
                prim = self.__stage.GetPrimAtPath(prim_path)
                if not prim:
                    continue

                if prim.IsInstanceProxy():
                    continue

                # Skips those prims that have no state change.
                if self.__active is not None and self.__active == prim.IsActive():
                    continue

                prim_spec = edit_target_layer.GetPrimAtPath(prim_path)

                valid_prim_paths.append(prim_path)
                if not prim_spec or not prim_spec.HasActive():
                    old_state = None
                else:
                    old_state = prim.IsActive()
                self.__old_active_states[prim_path] = old_state

                prim.SetActive(not prim.IsActive())

        self.__prim_paths = valid_prim_paths

    def undo(self):
        edit_layer = Sdf.Find(self.__influenced_layer_identifier)
        if not edit_layer:
            carb.log_error(
                f"Cannot undo active state as edit target {self.__influenced_layer_identifier} does not exist."
            )

            return

        with Usd.EditContext(self.__stage, edit_layer):
            with Sdf.ChangeBlock():
                for prim_path in self.__prim_paths:
                    prim = self.__stage.GetPrimAtPath(prim_path)
                    if not prim:
                        continue

                    old_state = self.__old_active_states.get(prim_path, None)
                    if old_state is None:
                        prim.ClearActive()
                    else:
                        prim.SetActive(old_state)

        if self.__usd_context and self.__old_selected_prim_paths:
            self.__usd_context.get_selection().set_selected_prim_paths(self.__old_selected_prim_paths, True)


class TogglePayLoadLoadSelectedPrimsCommand(omni.kit.commands.Command):
    """Toggles the loaded/unloaded payloads of the selected primitives."""

    def __init__(self, selected_paths: List[str], stage_or_context: Union[str, Usd.Stage, omni.usd.UsdContext] = None):
        """Constructor.

        Args:
            selected_paths (List[str]): Old selected prim paths.
            stage_or_context (Union[str, Usd.Stage, omni.usd.UsdContext], optional): Stage or UsdContext applies the changes to.
                It can be instance of Usd.Stage or omni.usd.UsdContext, or context name. By default, it will apply
                the changes to the stage in default UsdContext.
        """

        _, self._stage = get_context_and_stage(stage_or_context)
        self._selected_paths = selected_paths.copy()

    def _toggle_load(self):
        for selected_path in self._selected_paths:
            selected_prim = self._stage.GetPrimAtPath(selected_path)
            if selected_prim.IsLoaded():
                selected_prim.Unload()
            else:
                selected_prim.Load()

    def do(self):
        self._toggle_load()

    def undo(self):
        self._toggle_load()


class SetPayLoadLoadSelectedPrimsCommand(omni.kit.commands.Command):
    """Set the loaded/unloaded payloads of the selected primitives."""

    def __init__(self, selected_paths: List[str], value: bool, stage_or_context: Union[str, Usd.Stage, omni.usd.UsdContext] = None):
        """Constructor.

        Args:
            selected_paths (List[str]): Old selected prim paths.
            value (bool): True for load, and False for unload.
            stage_or_context (Union[str, Usd.Stage, omni.usd.UsdContext], optional): Stage or UsdContext applies the changes to.
                It can be instance of Usd.Stage or omni.usd.UsdContext, or context name. By default, it will apply
                the changes to the stage in default UsdContext.
        """
        _, self._stage = get_context_and_stage(stage_or_context)
        self._selected_paths = selected_paths.copy()
        self._processed_path = set()
        self._value = value
        self._is_undo = False

    def _set_load(self):
        if self._is_undo:
            paths = self._processed_path
        else:
            paths = self._selected_paths
        for selected_path in paths:
            selected_prim = self._stage.GetPrimAtPath(selected_path)
            if (selected_prim.IsLoaded() and self._value) or (not selected_prim.IsLoaded() and not self._value):
                if selected_path in self._processed_path:
                    self._processed_path.remove(selected_path)
                continue
            if self._value:
                selected_prim.Load()
            else:
                selected_prim.Unload()
            self._processed_path.add(selected_path)

    def do(self):
        self._set_load()

    def undo(self):
        self._is_undo = True
        self._value = not self._value
        self._set_load()
        self._value = not self._value
        self._processed_path = set()
        self._is_undo = False


class ParentPrimsCommand(omni.kit.commands.Command):
    """Moves prims into children of "parent" primitives."""

    def __init__(
        self,
        parent_path: str,
        child_paths: List[str],
        on_move_fn: callable = None,
        keep_world_transform: bool = True,
        stage_or_context: Union[str, Usd.Stage, omni.usd.UsdContext] = None
    ):
        """Constructor.

        Args:
            parent_path (str): prim path to become parent of child_paths
            child_paths (List[str]): prim paths to become children of parent_prim
            on_move_fn(Callable[[Sdf.Path, Sdf.Path], None], optional): Function to call when prim is re-parented, that
                the first param is the source path, and second one is the target path. Defaults to None.
            keep_world_transform (bool, optional): If it needs to keep the world transform after parenting. Defaults to True
            stage_or_context (Union[str, Usd.Stage, omni.usd.UsdContext], optional): Stage or UsdContext applies the changes to.
                It can be instance of Usd.Stage or omni.usd.UsdContext, or context name. By default, it will apply
                the changes to the stage in default UsdContext.
        """
        self._parent_path = parent_path
        self._child_paths = child_paths.copy()
        self._on_move_fn = on_move_fn
        self._keep_world_transform = keep_world_transform
        self._stage_or_context = stage_or_context

    def do(self):
        with omni.kit.undo.group():
            for path in self._child_paths:
                path_to = self._parent_path + "/" + Sdf.Path(path).name
                omni.kit.commands.execute(
                    "MovePrim",
                    path_from=path,
                    path_to=path_to,
                    on_move_fn=self._on_move_fn,
                    destructive=False,
                    keep_world_transform=self._keep_world_transform,
                    stage_or_context=self._stage_or_context
                )

    def undo(self):
        pass


class UnparentPrimsCommand(omni.kit.commands.Command):
    """Moves prims into root "/" primitive."""

    def __init__(
        self,
        paths: List[str],
        on_move_fn: callable = None,
        keep_world_transform: bool = True,
        stage_or_context: Union[str, Usd.Stage, omni.usd.UsdContext] = None
    ):
        """

        Args:
            paths: prim path to become parent of child_paths
            on_move_fn(Callable[[Sdf.Path, Sdf.Path], None], optional): Function to call when prim is re-parented, that
                the first param is the source path, and second one is the target path. Defaults to None.
            keep_world_transform (bool, optional): If it needs to keep the world transform after parenting. Defaults to True
            stage_or_context (Union[str, Usd.Stage, omni.usd.UsdContext], optional): Stage or UsdContext applies the changes to.
                It can be instance of Usd.Stage or omni.usd.UsdContext, or context name. By default, it will apply
                the changes to the stage in default UsdContext.
        """

        self._paths = paths.copy()
        self._on_move_fn = on_move_fn
        self._keep_world_transform = keep_world_transform
        self._stage_or_context = stage_or_context

    def do(self):
        with omni.kit.undo.group():
            for path in self._paths:
                path_to = "/" + Sdf.Path(path).name
                omni.kit.commands.execute(
                    "MovePrim",
                    path_from=path,
                    path_to=path_to,
                    on_move_fn=self._on_move_fn,
                    destructive=False,
                    keep_world_transform=self._keep_world_transform,
                    stage_or_context=self._stage_or_context
                )

    def undo(self):
        pass


class AppendAPIToPrimsCommand(omni.kit.commands.Command):
    """Appends API schema to prims."""

    def __init__(
        self,
        paths: List[str],
        api_schema: str,
        api_instance: str="",
        stage_or_context: Union[str, Usd.Stage, omni.usd.UsdContext] = None
    ):
        """
        Args:
            paths: prim path to become parent of child_paths
            api_schema (str): name of API to append to prim(s)
            api_instance (str): name of API instance to append to prim(s). Can be ""
            stage_or_context (Union[str, Usd.Stage, omni.usd.UsdContext], optional): Stage or UsdContext applies the changes to.
                It can be instance of Usd.Stage or omni.usd.UsdContext, or context name. By default, it will apply
                the changes to the stage in default UsdContext.
        """
        self._paths = paths.copy()
        self._api_schema = api_schema
        self._api_instance = api_instance
        self._stage_or_context = stage_or_context

    def do(self):
        usd_context, stage = get_context_and_stage(self._stage_or_context)
        if self._api_instance:
            for pp in self._paths:
                stage.GetPrimAtPath(pp).ApplyAPI(self._api_schema, self._api_instance)
        else:
            for pp in self._paths:
                stage.GetPrimAtPath(pp).ApplyAPI(self._api_schema)

    def undo(self):
        usd_context, stage = get_context_and_stage(self._stage_or_context)
        if self._api_instance:
            for pp in self._paths:
                stage.GetPrimAtPath(pp).RemoveAPI(self._api_schema, self._api_instance)
        else:
            for pp in self._paths:
                stage.GetPrimAtPath(pp).RemoveAPI(self._api_schema)


class RemoveAPIFromPrimsCommand(omni.kit.commands.Command):
    """Removes API schema from prims."""

    def __init__(
        self,
        paths: List[str],
        api_schema: str,
        api_instance: str="",
        stage_or_context: Union[str, Usd.Stage, omni.usd.UsdContext] = None
    ):
        """

        Args:
            paths: prim path to become parent of child_paths
            api_schema (str): name of API to append to prim(s)
            api_instance (str): name of API instance to append to prim(s). Can be ""
            stage_or_context (Union[str, Usd.Stage, omni.usd.UsdContext], optional): Stage or UsdContext applies the changes to.
                It can be instance of Usd.Stage or omni.usd.UsdContext, or context name. By default, it will apply
                the changes to the stage in default UsdContext.
        """
        self._paths = paths.copy()
        self._api_schema = api_schema
        self._api_instance = api_instance
        self._stage_or_context = stage_or_context

    def do(self):
        usd_context, stage = get_context_and_stage(self._stage_or_context)
        if self._api_instance:
            for pp in self._paths:
                stage.GetPrimAtPath(pp).RemoveAPI(self._api_schema, self._api_instance)
        else:
            for pp in self._paths:
                stage.GetPrimAtPath(pp).RemoveAPI(self._api_schema)

    def undo(self):
        usd_context, stage = get_context_and_stage(self._stage_or_context)
        if self._api_instance:
            for pp in self._paths:
                stage.GetPrimAtPath(pp).ApplyAPI(self._api_schema, self._api_instance)
        else:
            for pp in self._paths:
                stage.GetPrimAtPath(pp).ApplyAPI(self._api_schema)
