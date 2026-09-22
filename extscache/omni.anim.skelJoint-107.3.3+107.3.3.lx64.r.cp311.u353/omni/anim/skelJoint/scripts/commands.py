# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni
import omni.timeline
import carb
from pxr import Sdf, Vt, Usd, UsdGeom, UsdSkel
import OmniSkelSchema
from omni.kit.usd_undo import UsdLayerUndo
from typing import List, Optional

from .utils import *

import omni.anim.skelJoint as sj


def get_all_descendents_joint(prim, output=[]):
    if prim and prim.IsA(OmniSkelSchema.OmniJoint):
        output.append(prim)
    for child in prim.GetChildren():
        get_all_descendents_joint(child, output)


class ApplyOmniSkelJointLimitsAPICommand(omni.kit.commands.Command):
    """
    Apply OmniSkel Joint Limits API **Command**.

    Adds an OmniJointLimitsAPI to the specified joint(s). This
    contains joint angle limit information.

    Args:
        paths: Joint paths to add api to
        select_prim: Bool weather to select the prim(s) after execution
        stage: Stage containing the skeleton
    """
    def __init__(
            self,
            paths: List[Sdf.Path] = [],
            select_prim: bool = True,
            stage: Optional[Usd.Stage] = None
    ):
        self._usd_undo = None
        self._paths = paths
        self._select_prim = select_prim
        self._stage = stage

    def do(self):
        stage = self._stage
        if not stage:
            stage = omni.usd.get_context().get_stage()
        self._usd_undo = UsdLayerUndo(stage.GetEditTarget().GetLayer())
        added_path = []
        for path in self._paths:
            prim = stage.GetPrimAtPath(path)
            if not prim or not prim.IsA(OmniSkelSchema.OmniJoint) or prim.HasAPI(OmniSkelSchema.OmniJointLimitsAPI):
                carb.log_warn(f"failed create OmniSkel JointLimits: {path} is taken")
            else:
                self._usd_undo.reserve(path)
                # OMNI_SKEL_USD_WRITE
                prim.ApplyAPI(OmniSkelSchema.OmniJointLimitsAPI)
                added_path.append(str(path))

        if self._select_prim and len(added_path) > 0:
            context = omni.usd.get_context_from_stage(stage)
            if context:
                selection = context.get_selection()
                selection.set_selected_prim_paths(list(set(added_path)), True)

    def undo(self):
        if self._usd_undo is not None:
            self._usd_undo.undo()


class RemoveOmniSkelJointLimitsAPICommand(omni.kit.commands.Command):
    """
    Remove OmniSkel Joint Limits API **Command**.

    Removes OmniJointLimitsAPI from the specified joint(s).

    Args:
        paths: Joint paths to remove api from
        stage: Stage containing the skeleton
    """
    def __init__(
        self,
        paths: List[Sdf.Path] = [],
        stage: Optional[Usd.Stage] = None
    ):
        self._usd_undo = None
        self._paths = paths
        self._stage = stage

    def do(self):
        stage = self._stage
        if not stage:
            stage = omni.usd.get_context().get_stage()
        self._usd_undo = UsdLayerUndo(stage.GetEditTarget().GetLayer())
        for path in self._paths:
            prim = stage.GetPrimAtPath(path)
            if prim and prim.IsA(OmniSkelSchema.OmniJoint) and prim.HasAPI(OmniSkelSchema.OmniJointLimitsAPI):
                self._usd_undo.reserve(path)
                # OMNI_SKEL_USD_WRITE
                jointLimit = OmniSkelSchema.OmniJointLimitsAPI(prim)
                with Sdf.ChangeBlock():
                    prim.RemoveProperty("swingHorizontalAngle")
                    prim.RemoveProperty("swingVerticalAngle")
                    prim.RemoveProperty("twistMinimumAngle")
                    prim.RemoveProperty("twistMaximumAngle")
                    prim.RemoveProperty("offsetRotation")
                    prim.RemoveProperty("enabled")
                    prim.RemoveAPI(OmniSkelSchema.OmniJointLimitsAPI)

    def undo(self):
        if self._usd_undo is not None:
            self._usd_undo.undo()


class CreateOmniSkelJointBoxShapeCommand(omni.kit.commands.Command):
    """
    Create OmniSkel Joint Box Shape **Command**.

    Creates a box shape on the specified joint(s) for visualization.

    Args:
        paths: Joint paths to create prims on
        select_prim: Bool weather to select the prim(s) after execution
        stage: Stage containing the skeleton
    """
    def __init__(
            self,
            paths: List[Sdf.Path] = [],
            select_prim: bool = True,
            stage: Optional[Usd.Stage] = None
    ):
        self._usd_undo = None
        self._paths = paths
        self._select_prim = select_prim
        self._stage = stage

    def do(self):
        stage = self._stage
        if not stage:
            stage = omni.usd.get_context().get_stage()
        self._usd_undo = UsdLayerUndo(stage.GetEditTarget().GetLayer())
        added_shape_path = []
        for path in self._paths:
            prim = stage.GetPrimAtPath(path)
            if prim:
                carb.log_warn(f"failed create OmniSkel JointBoxShape: {path} is taken")
            else:
                self._usd_undo.reserve(path)
                # OMNI_SKEL_USD_WRITE
                cube = UsdGeom.Cube.Define(stage, path)
                cube.GetPrim().ApplyAPI(OmniSkelSchema.OmniJointBoxShapeAPI)
                cube.GetPurposeAttr().Set("guide")
                added_shape_path.append(path)

        if self._select_prim and len(added_shape_path) > 0:
            context = omni.usd.get_context_from_stage(stage)
            if context:
                selection = context.get_selection()
                selection.set_selected_prim_paths(list(set(added_shape_path)), True)

    def undo(self):
        if self._usd_undo is not None:
            self._usd_undo.undo()


class CreateOmniSkelJointSphereShapeCommand(omni.kit.commands.Command):
    """
    Create OmniSkel Joint Sphere Shape **Command**.

    Creates a sphere shape on the specified joint(s) for visualization.

    Args:
        paths: Joint paths to create prims on
        select_prim: Bool weather to select the prim(s) after execution
        stage: Stage containing the skeleton
    """
    def __init__(
            self,
            paths: List[Sdf.Path] = [],
            select_prim: bool = True,
            stage: Optional[Usd.Stage] = None
    ):
        self._usd_undo = None
        self._paths = paths
        self._select_prim = select_prim
        self._stage = stage

    def do(self):
        stage = self._stage
        if not stage:
            stage = omni.usd.get_context().get_stage()
        context = omni.usd.get_context_from_stage(stage)
        if context:
            selection = context.get_selection()
        else:
            selection = None
        self._usd_undo = UsdLayerUndo(stage.GetEditTarget().GetLayer())
        added_shape_path = []
        for path in self._paths:
            prim = stage.GetPrimAtPath(path)
            if prim:
                carb.log_warn(f"failed create OmniSkel JointSphereShape: {path} is taken")
            else:
                self._usd_undo.reserve(path)
                # OMNI_SKEL_USD_WRITE
                sphere = UsdGeom.Sphere.Define(stage, path)
                sphere.GetPrim().ApplyAPI(OmniSkelSchema.OmniJointSphereShapeAPI)
                sphere.GetPurposeAttr().Set("guide")
                added_shape_path.append(path)
        if selection and self._select_prim and len(added_shape_path) > 0:
            selection.set_selected_prim_paths(list(set(added_shape_path)), True)

    def undo(self):
        if self._usd_undo is not None:
            self._usd_undo.undo()


class CreateOmniSkelJointCapsuleShapeCommand(omni.kit.commands.Command):
    """
    Create OmniSkel Joint Capsule Shape **Command**.

    Creates a capsule shape on the specified joint(s) for visualization.

    Args:
        paths: Joint paths to create prims on
        select_prim: Bool weather to select the prim(s) after execution
        stage: Stage containing the skeleton
    """
    def __init__(
            self,
            paths: List[Sdf.Path] = [],
            select_prim: bool = True,
            stage: Optional[Usd.Stage] = None
    ):
        self._usd_undo = None
        self._paths = paths
        self._select_prim = select_prim
        self._stage = stage

    def do(self):
        stage = self._stage
        if not stage:
            stage = omni.usd.get_context().get_stage()
        context = omni.usd.get_context_from_stage(stage)
        if context:
            selection = context.get_selection()
        else:
            selection = None
        self._usd_undo = UsdLayerUndo(stage.GetEditTarget().GetLayer())
        added_shape_path = []
        for path in self._paths:
            prim = stage.GetPrimAtPath(path)
            if prim:
                carb.log_warn(f"failed create OmniSkel JointCapsuleShape: {path} is taken")
            else:
                self._usd_undo.reserve(path)
                # OMNI_SKEL_USD_WRITE
                capsule = UsdGeom.Capsule.Define(stage, path)
                capsule.GetPrim().ApplyAPI(OmniSkelSchema.OmniJointCapsuleShapeAPI)
                capsule.GetPurposeAttr().Set("guide")
                added_shape_path.append(path)
        if selection and self._select_prim and len(added_shape_path) > 0:
            selection.set_selected_prim_paths(list(set(added_shape_path)), True)

    def undo(self):
        if self._usd_undo is not None:
            self._usd_undo.undo()


class SwitchSkeletonTransformMode(omni.kit.commands.Command):
    """
    Switch Skeleton Transform Mode **Command**.

    Sets a skeleton's current transform mode, ie what pose it
    displays with in the viewport.

    Args:
        skeleton_path: Path to the skeleton
        transform_mode: Mode to switch to. 0 = animation, 1 = retargeting, 2 = rest, 3 = binding
        stage: Stage containing the skeleton
    """
    def __init__(
            self,
            skeleton_path: Sdf.Path = None,
            transform_mode: int = -1,
            stage: Optional[Usd.Stage] = None
    ):
        self._skeleton_path = skeleton_path
        self._transform_mode = transform_mode
        self._usd_undo = None
        self._stage = stage

    def __switch_mode(context, skel_prim, mode):
        path = str(skel_prim.GetPath())
        if mode == 0:
            sj.acquire_interface().switch_to_animation_transform_mode(path, "")
        elif mode == 1:
            context.get_timeline().stop()
            sj.acquire_interface().switch_to_retargeting_transform_mode(path, "")
        elif mode == 2:
            context.get_timeline().stop()
            sj.acquire_interface().switch_to_rest_transform_mode(path, "")
        elif mode == 3:
            context.get_timeline().stop()
            sj.acquire_interface().reset_to_binding(path, "")

    def do(self):
        stage = self._stage
        if not stage:
            stage = omni.usd.get_context().get_stage()
        context = omni.usd.get_context_from_stage(stage)
        if not context:
            class_name = self.__class__.__name__
            carb.log_error(f'{class_name}: stages that are not attached to a USD context are not supported')
            return
        self._usd_undo = UsdLayerUndo(stage.GetSessionLayer())
        skel_prim = stage.GetPrimAtPath(self._skeleton_path)
        if skel_prim.IsA(UsdSkel.Skeleton) and skel_prim.HasAPI(OmniSkelSchema.OmniSkeletonAPI):
            # TODO: switch_mode doesn't support "swith to BIND" for now, to trigger BIND
            has_value = skel_prim.HasAuthoredCustomDataKey("TransformMode")
            need_update = not has_value
            if has_value:
                prev_transform_mode = skel_prim.GetCustomDataByKey("TransformMode")
                need_update = prev_transform_mode != self._transform_mode

            if need_update:
                self._usd_undo.reserve(self._skeleton_path)
                # OMNI_SKEL_USD_WRITE
                SwitchSkeletonTransformMode.__switch_mode(context, skel_prim, self._transform_mode)

    def undo(self):
        if self._usd_undo is not None:
            self._usd_undo.undo()


class ResetToBindingCommand(omni.kit.commands.Command):
    """
    Apply Joint Binding Pose To Skeleton **Command**.

    Sets a skeleton's current pose to its binding pose

    Args:
        skeleton_path: Path to the skeleton
        stage: Stage containing the skeleton
    """
    def __init__(
            self,
            skeleton_path: Sdf.Path = None,
            stage: Optional[Usd.Stage] = None
    ):
        self._skeleton_path = skeleton_path
        self._usd_undo = None
        self._stage = stage

    def do(self):
        stage = self._stage
        if not stage:
            stage = omni.usd.get_context().get_stage()
        context = omni.usd.get_context_from_stage(stage)
        if not context:
            class_name = self.__class__.__name__
            carb.log_error(f'{class_name}: stages that are not attached to a USD context are not supported')
            return
        self._usd_undo = UsdLayerUndo(stage.GetSessionLayer())
        skel_prim = stage.GetPrimAtPath(self._skeleton_path)
        if skel_prim.IsA(UsdSkel.Skeleton) and skel_prim.HasAPI(OmniSkelSchema.OmniSkeletonAPI):
            timeline = context.get_timeline()
            timeline.stop()

            joints = []
            get_all_descendents_joint(skel_prim, joints)
            for joint in joints:
                self._usd_undo.reserve(joint.GetPath())

            # OMNI_SKEL_USD_WRITE
            path = str(skel_prim.GetPath())
            sj.acquire_interface().reset_to_binding(path, "")

    def undo(self):
        if self._usd_undo is not None:
            self._usd_undo.undo()


class ApplyJointRestPoseToSkeletonCommand(omni.kit.commands.Command):
    """
    Apply Joint Rest Pose To Skeleton **Command**.

    Sets a skeleton's current pose to its rest pose

    Args:
        skeleton_path: Path to the skeleton
        stage: Stage containing the skeleton
    """
    def __init__(
            self,
            skeleton_path: Sdf.Path = None,
            stage: Optional[Usd.Stage] = None
    ):
        self._skeleton_path = skeleton_path
        self._usd_undos = []
        self._stage = stage

    def do(self):
        stage = self._stage
        if not stage:
            stage = omni.usd.get_context().get_stage()
        context = omni.usd.get_context_from_stage(stage)
        if not context:
            class_name = self.__class__.__name__
            carb.log_error(f'{class_name}: stages that are not attached to a USD context are not supported')
            return
        self._usd_undos = [UsdLayerUndo(layer) for layer in [stage.GetSessionLayer(), stage.GetEditTarget().GetLayer()]]
        skel_prim = stage.GetPrimAtPath(self._skeleton_path)
        for u in self._usd_undos:
            u.reserve(skel_prim.GetPath())

        if skel_prim.IsA(UsdSkel.Skeleton) and skel_prim.HasAPI(OmniSkelSchema.OmniSkeletonAPI):
            timeline = context.get_timeline()
            timeline.stop()

            joints = []
            get_all_descendents_joint(skel_prim, joints)
            for joint in joints:
                for u in self._usd_undos:
                    u.reserve(joint.GetPath())

            # OMNI_SKEL_USD_WRITE
            path = str(skel_prim.GetPath())
            sj.acquire_interface().apply_joint_rest_pose_to_skeleton(path, "")

    def undo(self):
        for u in self._usd_undos:
            u.undo()


class ApplyJointRetargetPoseToSkeletonCommand(omni.kit.commands.Command):
    """
    Apply Joint Retarget Pose To Skeleton **Command**.

    Sets a skeleton's current pose to its retarget pose

    Args:
        skeleton_path: Path to the skeleton
        stage: Stage containing the skeleton
    """
    def __init__(
            self,
            skeleton_path: Sdf.Path = None,
            stage: Optional[Usd.Stage] = None
    ):
        self._skeleton_path = skeleton_path
        self._usd_undos = []
        self._stage = stage

    def do(self):
        stage = self._stage
        if not stage:
            stage = omni.usd.get_context().get_stage()
        context = omni.usd.get_context_from_stage(stage)
        if not context:
            class_name = self.__class__.__name__
            carb.log_error(f'{class_name}: stages that are not attached to a USD context are not supported')
            return
        self._usd_undos = [UsdLayerUndo(layer) for layer in [stage.GetSessionLayer(), stage.GetEditTarget().GetLayer()]]
        skel_prim = stage.GetPrimAtPath(self._skeleton_path)
        for u in self._usd_undos:
            u.reserve(skel_prim.GetPath())
        if skel_prim.IsA(UsdSkel.Skeleton) and skel_prim.HasAPI(OmniSkelSchema.OmniSkeletonAPI):
            timeline = context.get_timeline()
            timeline.stop()

            joints = []
            get_all_descendents_joint(skel_prim, joints)
            for joint in joints:
                for u in self._usd_undos:
                    u.reserve(joint.GetPath())

            # OMNI_SKEL_USD_WRITE
            path = str(skel_prim.GetPath())
            sj.acquire_interface().apply_joint_retarget_pose_to_skeleton(path, "")

    def undo(self):
        for u in self._usd_undos:
            u.undo()


class ClearOmniSkelOldDataCommand(omni.kit.commands.Command):
    """
    ClearOmniSkelOldData **Command**.

    Removes OmniSkel prims/data from the scene
    """
    def __init__(
            self
    ):
        self._usd_undo = None

    def do(self):
        stage = omni.usd.get_context().get_stage()
        context = omni.usd.get_context_from_stage(stage)
        if not context:
            class_name = self.__class__.__name__
            carb.log_error(f'{class_name}: stages that are not attached to a USD context are not supported')
            return
        self._usd_undo = UsdLayerUndo(stage.GetEditTarget().GetLayer())
        clearList = []
        for prim in stage.Traverse():
            if prim.IsA(UsdSkel.Skeleton) and prim.HasAPI(OmniSkelSchema.OmniSkeletonAPI):
                for child in prim.GetChildren():
                    if child.IsA(UsdGeom.Scope) and child.GetName() == "OmniSkel":
                        clearList.append(child)
                        prim.RemoveAPI(OmniSkelSchema.OmniSkeletonAPI)

        clearList.reverse()
        for clearPrim in clearList:
            if clearPrim:
                stage.RemovePrim(clearPrim.GetPath())

    def undo(self):
        if self._usd_undo is not None:
            self._usd_undo.undo()


class SetJointPosesCommand(omni.kit.commands.Command):
    """
    Set Joint Poses **Command**.

    Sets the poses of all the joints in a skeleton hierarchy. The
    utils.get_joint_poses() function can be used to query data in
    the same format.

    Args:
        skeleton_path: The usd path of the UsdSkel.Skeleton to set joint poses on
        stage: The stage containing the skeleton
        translations: Translation vectors, x,y,z for each bone.
        rotations: Rotation euler angles, x,y,z for each bone.
        scales: Per axis scales, x,y,z for each bone.
        rotation_orders: Rotation order string (eg "rotateXYZ") for each bone.
    """
    def __init__(
            self,
            skeleton_path: Sdf.Path,
            stage: Usd.Stage,
            translations: Vt.Vec3fArray,
            rotations: Vt.Vec3fArray,
            scales: Vt.Vec3fArray,
            rotation_orders: Vt.TokenArray
    ):
        self._skeleton_path = skeleton_path
        self._usd_undos = []
        self._stage = stage
        self._translations = translations
        self._rotations = rotations
        self._scales = scales
        self._rotation_orders = rotation_orders

    def do(self):
        stage = self._stage
        if not stage:
            stage = omni.usd.get_context().get_stage()
        context = omni.usd.get_context_from_stage(stage)
        if not context:
            class_name = self.__class__.__name__
            carb.log_error(f'{class_name}: stages that are not attached to a USD context are not supported')
            return
        self._usd_undos = [UsdLayerUndo(layer) for layer in [stage.GetSessionLayer(), stage.GetEditTarget().GetLayer()]]
        skel_prim = stage.GetPrimAtPath(self._skeleton_path)
        for u in self._usd_undos:
            u.reserve(skel_prim.GetPath())
        if skel_prim.IsA(UsdSkel.Skeleton) and skel_prim.HasAPI(OmniSkelSchema.OmniSkeletonAPI):
            timeline = context.get_timeline()
            timeline.stop()

            joints = []
            get_all_descendents_joint(skel_prim, joints)
            for joint in joints:
                for u in self._usd_undos:
                    u.reserve(joint.GetPath())

            # OMNI_SKEL_USD_WRITE
            path = str(skel_prim.GetPath())
            set_joint_poses(UsdSkel.Skeleton(skel_prim), self._translations, self._rotations, self._scales, self._rotation_orders)

    def undo(self):
        for u in self._usd_undos:
            u.undo()


omni.kit.commands.register(ApplyOmniSkelJointLimitsAPICommand)
omni.kit.commands.register(RemoveOmniSkelJointLimitsAPICommand)
omni.kit.commands.register(CreateOmniSkelJointBoxShapeCommand)
omni.kit.commands.register(CreateOmniSkelJointSphereShapeCommand)
omni.kit.commands.register(CreateOmniSkelJointCapsuleShapeCommand)
omni.kit.commands.register(SwitchSkeletonTransformMode)
omni.kit.commands.register(ResetToBindingCommand)
omni.kit.commands.register(ApplyJointRetargetPoseToSkeletonCommand)
omni.kit.commands.register(ApplyJointRestPoseToSkeletonCommand)
omni.kit.commands.register(ClearOmniSkelOldDataCommand)
omni.kit.commands.register(SetJointPosesCommand)
