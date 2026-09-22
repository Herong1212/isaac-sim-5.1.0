# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
__all__ = ["PedestrianCapabilityChecker"]

import functools
import itertools
import math
from dataclasses import dataclass, field

from omni.asset_validator.core import BaseRuleChecker, is_omni_path
from pxr import Gf, Sdf, Usd, UsdGeom, UsdSkel

from ._pedestrian_rig_mapping_utils import JointsPreset, RigMapping, find_best_rig_mapping


@dataclass(frozen=True)
class SkeletonInfo:
    """Structure that saves a UsdSkelSkeleton and all of its skinnable meshes."""

    schema: UsdSkel.Skeleton
    skinning_meshes: list[Usd.Prim] = field(default_factory=list)


@dataclass(frozen=True)
class SkeletonRootInfo:
    """Structure that saves all skeletons and skinnable meshes under a UsdSkelRoot."""

    skeletons: list[SkeletonInfo]
    unbound_meshes: list[Usd.Prim] = field(default_factory=list)

    @functools.cached_property
    def bound_meshes(self):
        meshes = []
        for skeleton in itertools.chain(self.skeletons):
            meshes.extend(skeleton.skinning_meshes)

        return meshes


class PedestrianCapabilityChecker(BaseRuleChecker):
    """
    Validates the following pedestrian requirements in the **AV Sim Specification: Creators**:

    - **6.0.C0.02: People Skeleton Alignment Needs**

      The skeleton of a bipedal human character must be axis-aligned, centered at the origin, and feet must sit on the ground plane.

    - **6.0.C0.03: Skeleton Rig Binding Needs**

      Human character geometry prims must have a skeletal binding (skinning) to a ``UsdSkel`` skeleton rig.

    - **6.0.C0.04: Skeleton Rig Authoring**

      The skeleton should not be separately loadable from any mesh bound to it.

    - **6.0.C0.05: Skeleton Matching**

      The skeleton must match one of the following supported canonical template skeleton rigs:

      1. Reallusion Character Creator 4.x Skeleton
      2. Unreal Engine Mannequin Skeleton
      3. Omniverse Default Skeleton
    """

    def __init__(self, verbose, consumerLevelChecks, assetLevelChecks):
        super().__init__(verbose, consumerLevelChecks, assetLevelChecks)
        self.__stage = None

    def __find_joint_index_from_name(self, skeleton_query: UsdSkel.SkeletonQuery, joint_name: str) -> int:
        for index, joint in enumerate(skeleton_query.GetJointOrder()):
            if Sdf.Path(joint).name == joint_name:
                return index

        return -1

    def __find_best_rig_mapping(self, skeleton_query: UsdSkel.SkeletonQuery) -> RigMapping | None:
        return find_best_rig_mapping(skeleton_query.GetSkeleton())

    @staticmethod
    def __is_prim_under_skel_root(prim: Usd.Prim):
        parent = prim.GetParent()
        while not parent.GetPath().IsAbsoluteRootPath():
            if parent.IsA(UsdSkel.Root):
                return True

            parent = parent.GetParent()

        return not parent.GetPath().IsAbsoluteRootPath()

    @staticmethod
    def __find_loadable_ancestor(prim: Usd.Prim) -> Sdf.Path:
        parent = prim
        while not parent.GetPath().IsAbsoluteRootPath():
            if parent.HasAuthoredPayloads():
                return parent.GetPath()

            parent = parent.GetParent()

        return Sdf.Path.absoluteRootPath

    def __validate_skin_bound(self, skeleton: SkeletonInfo, up_axis, plane_axis_idxes, up_axis_idx):
        # Then, check the bounding box of mesh points for symmetry.
        skin_bound = Gf.BBox3d()
        for mesh in skeleton.skinning_meshes:
            skin_bound = Gf.BBox3d.Combine(
                skin_bound,
                UsdGeom.Boundable(mesh).ComputeWorldBound(
                    Usd.TimeCode.EarliestTime(), UsdGeom.Tokens.default_, UsdGeom.Tokens.render
                ),
            )

        center_point = skin_bound.ComputeCentroid()
        if not Gf.IsClose((center_point[plane_axis_idxes[0]], center_point[plane_axis_idxes[1]]), (0, 0), 0.1):
            self._AddWarning(
                message=f"The Bounding box of the pedestrian geometry prims is not symmetrical around the up-axis '{up_axis}'.",
                at=skeleton.schema,
            )

        # If it stands on the ground plane.
        bottom = skin_bound.ComputeAlignedBox().GetMin()
        if not Gf.IsClose(bottom[up_axis_idx], 0.0, 0.1):
            self._AddFailedCheck(message="Character must stand on the ground plane.", at=skeleton.schema)

    def __get_stage_up_axis(self):
        up_axis = UsdGeom.GetStageUpAxis(self.__stage)
        if up_axis == UsdGeom.Tokens.z:
            # Z up
            plane_axis_idxes = [0, 1]
            up_axis_idx = 2
        elif up_axis == UsdGeom.Tokens.y:
            # Y up
            plane_axis_idxes = [0, 2]
            up_axis_idx = 1
        else:
            raise ValueError(f"Stage up axis can only be '{UsdGeom.Tokens.y}' or '{UsdGeom.Tokens.z}'.")

        return up_axis, plane_axis_idxes, up_axis_idx

    def __validate_joint_world_transforms(self, skeleton: UsdSkel.Skeleton, skeleton_query: UsdSkel.SkeletonQuery):
        xform_cache = UsdGeom.XformCache()
        joint_world_transforms = skeleton_query.ComputeJointWorldTransforms(xform_cache)

        # Checking root joint to ensure it has no transforms.
        if joint_world_transforms:
            root_joint_transform: Gf.Matrix4d = joint_world_transforms[0]
            translation: Gf.Vec3d = root_joint_transform.ExtractTranslation()
            if not Gf.IsClose(translation, Gf.Vec3d(0.0, 0.0, 0.0), 1e-6):
                self._AddFailedCheck(
                    message="SimReady pedestrians require the transform of root joint has zero translation.",
                    at=skeleton.schema,
                )

        return joint_world_transforms

    def __validate_character_alignment_needs(
        self, skeleton: SkeletonInfo, skeleton_query: UsdSkel.SkeletonQuery, rig_mapping: RigMapping
    ):
        # Validate joint transforms.
        joint_world_transforms = self.__validate_joint_world_transforms(skeleton, skeleton_query)

        # Validate skin bound next.
        up_axis, plane_axis_idxes, up_axis_idx = self.__get_stage_up_axis()
        self.__validate_skin_bound(skeleton, up_axis, plane_axis_idxes, up_axis_idx)

        # Checks if the character is axis aligned and stands straight.
        # It uses the vector calculated between foot joints and see if it's aligned with the up axis.
        right_foot_joint_name = rig_mapping.mappings.get(JointsPreset.RIGHT_FOOT)
        left_foot_joint_name = rig_mapping.mappings.get(JointsPreset.LEFT_FOOT)
        if not left_foot_joint_name or not right_foot_joint_name:
            self._AddWarning("Cannot find foot joints to check if character is axis aligned.", at=skeleton.schema)
            return

        right_foot_joint_index = self.__find_joint_index_from_name(skeleton_query, right_foot_joint_name)
        left_foot_joint_index = self.__find_joint_index_from_name(skeleton_query, left_foot_joint_name)
        if right_foot_joint_index == -1 or left_foot_joint_index == -1:
            self._AddWarning("Cannot find foot joints to check if character is axis aligned.", at=skeleton.schema)
            return

        right_foot_transform: Gf.Matrix4d = joint_world_transforms[right_foot_joint_index]
        left_foot_transform: Gf.Matrix4d = joint_world_transforms[left_foot_joint_index]

        tolerance_degrees = 5.0
        aligned, offset_angle = self._is_feet_axis_aligned(
            left_foot_transform, right_foot_transform, up_axis_idx, tolerance_degrees
        )
        if not aligned:
            self._AddFailedCheck(
                f"Vector between foot joints should be nearly perpendicular to up axis '{up_axis}', "
                f"while it's off {round(offset_angle, 2)} degrees (tolerance is {tolerance_degrees} degrees).",
                at=skeleton.schema,
            )

    @staticmethod
    def _is_feet_axis_aligned(
        left_foot_transform: Gf.Matrix4d, right_foot_transform: Gf.Matrix4d, up_axis_idx: int, epsilon_in_degrees=5.0
    ):
        """Checks vector between left and right foot joints to see if they are perpendicular to up axis.

        Args:
            left_foot_transform (Gf.Matrix4d): World transform of left foot joint.
            right_foot_transform (Gf.Matrix4d): World transform of right foot joint.
            up_axis_dix (int): Index of up axis. 1 for y axis, 2 for z axis.
        """
        right_foot_translation: Gf.Vec3d = right_foot_transform.ExtractTranslation()
        left_foot_translation: Gf.Vec3d = left_foot_transform.ExtractTranslation()

        direction: Gf.Vec3d = Gf.GetNormalized(right_foot_translation - left_foot_translation)
        up_vector = Gf.Vec3d(0.0, 1.0, 0.0) if up_axis_idx == 1 else Gf.Vec3d(0.0, 0.0, 1.0)
        angle = math.degrees(math.acos(Gf.Dot(up_vector, direction)))
        offset_angle = 90.0 - angle

        return Gf.IsClose(offset_angle, 0.0, epsilon_in_degrees), offset_angle

    def __validate_skeleton(self, skeleton: SkeletonInfo):
        usd_skel_cache = UsdSkel.Cache()
        skeleton_query: UsdSkel.SkeletonQuery = usd_skel_cache.GetSkelQuery(skeleton.schema)

        # 6.0.C0.04: Skeleton Rig Authoring - The Skeleton should not be separately loadable from
        # any Mesh bound to it
        payload_parent: Sdf.Path = self.__find_loadable_ancestor(skeleton.schema.GetPrim())
        if not payload_parent.IsAbsoluteRootPath():
            for mesh in skeleton.skinning_meshes:
                if not mesh.GetPath().HasPrefix(payload_parent):
                    self._AddFailedCheck(
                        message="Mesh's skeleton is separably loadable and may be missing for deformation.",
                        at=skeleton.schema,
                    )

                    break

        # 6.0.C0.05: Skeleton must match one of the supported canonical template rigs.
        best_rig_mapping, missing_joints = self.__find_best_rig_mapping(skeleton_query)
        if best_rig_mapping is None:
            self._AddFailedCheck(
                "Skeleton must match one of the supported SimReady canonical template rigs. "
                "See specification documentation for more information.",
                at=skeleton.schema,
            )
            return

        if missing_joints:
            self._AddFailedCheck(
                f"Found matching {best_rig_mapping.name}-style skeleton rig, "
                f"but the skeleton is missing the following joints: {', '.join(missing_joints)}.",
                at=skeleton.schema,
            )

        # 6.0.C0.02: People Geometry Alignment Needs - A human character must be axis-aligned,
        # centered at the origin, and feet must sit on the ground plane.
        self.__validate_character_alignment_needs(skeleton, skeleton_query, best_rig_mapping)

    @staticmethod
    def __is_from_default_prim(prim: Usd.Prim):
        stage: Usd.Stage = prim.GetStage()
        default_prim = stage.GetDefaultPrim()
        if not default_prim:
            return False

        return prim.GetPath().HasPrefix(default_prim.GetPath())

    def CheckStage(self, stage: Usd.Stage):
        self.__stage = stage

        default_prim = stage.GetDefaultPrim()
        if not default_prim:
            self._AddFailedCheck("No default prim presented in this layer.", at=stage)

            return

        has_skelroot = False
        for child in Usd.PrimRange(default_prim, Usd.TraverseInstanceProxies()):
            if UsdSkel.Root(child):
                has_skelroot = True
                break

        if not has_skelroot:
            self._AddFailedCheck("No valid UsdSkelRoot presented under default prim in this layer.", at=stage)

    def CheckPrim(self, prim: Usd.Prim):
        if not self.__is_from_default_prim(prim):
            return

        if is_omni_path(prim.GetPath()):
            return

        if skel_root := UsdSkel.Root(prim):
            skel_root_info = self.__parse_skel_root_hierarchy(skel_root)
            if not skel_root_info.bound_meshes and not skel_root_info.unbound_meshes:
                self._AddFailedCheck(message="No skinnable mesh found.", at=prim)

            if not skel_root_info.skeletons:
                self._AddFailedCheck(message="No skeletons found.", at=prim)

            # 6.0.C0.03: Skeleton Rig Binding Needs Human character geometry prims must have a Skeletal
            # Binding (skinning) to a UsdSkel skeleton rig
            for unbound_mesh in skel_root_info.unbound_meshes:
                self._AddFailedCheck(message="No binding to a skeleton rig.", at=unbound_mesh)

            for skeleton in skel_root_info.skeletons:
                if not skeleton.skinning_meshes:
                    self._AddFailedCheck(message="No skinnable meshes found for skeleton.", at=skeleton.schema)
                    continue

                self.__validate_skeleton(skeleton)
        elif prim.IsA(UsdSkel.Skeleton) or UsdSkel.IsSkinnablePrim(prim):
            # It's possible that the skeleton or skinning mesh is out of the SkeletonRootInfo namespace.
            if not self.__is_prim_under_skel_root(prim):
                self._AddFailedCheck(
                    message="Skeleton or skinnable prim must be defined under SkelRoot.",
                    at=prim,
                )

    def __parse_skel_root_hierarchy(self, prim: UsdSkel.Root) -> SkeletonRootInfo:
        skeletons = {}
        unbound_meshes = []
        for child in Usd.PrimRange(prim.GetPrim(), Usd.TraverseInstanceProxies()):
            if usd_skeleton := UsdSkel.Skeleton(child):
                skeletons.setdefault(usd_skeleton.GetPath(), (usd_skeleton, []))
            elif UsdSkel.IsSkinnablePrim(child):
                if not child.HasAPI(UsdSkel.BindingAPI):
                    self._AddFailedCheck(message="Skinnable prim must have UsdSkelBindingAPI applied.", at=child)
                else:
                    binding_api: UsdSkel.BindingAPI = UsdSkel.BindingAPI(child)
                    skeleton = binding_api.GetSkeleton()
                    if not skeleton:
                        unbound_meshes.append(child)
                    else:
                        _, skining_meshes = skeletons.setdefault(skeleton.GetPath(), (skeleton, []))
                        skining_meshes.append(child)

        skeleton_infos = [SkeletonInfo(skeleton, meshes) for skeleton, meshes in skeletons.values()]

        return SkeletonRootInfo(skeletons=skeleton_infos, unbound_meshes=unbound_meshes)

    def ResetCaches(self):
        self.__stage = None
