# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from pxr import Usd, UsdSkel
from .usd_helper import traverse_prim


def get_joint_list(prim: Usd.Prim):
    """
    Returns the list of joints for a SkelAnim or a Skeleton prim
    """
    if prim and prim.IsValid():
        if prim.IsA(UsdSkel.Animation):
            anim_joints_attr = UsdSkel.Animation(prim).GetJointsAttr()
            anim_joints = anim_joints_attr.Get()
            if anim_joints:
                return anim_joints
        elif prim.IsA(UsdSkel.Skeleton):
            skel_cache = UsdSkel.Cache()
            skel_query = skel_cache.GetSkelQuery(UsdSkel.Skeleton(prim))
            skel_joints = skel_query.GetJointOrder()
            if skel_joints:
                return skel_joints
    return []


def check_compatibility(skel_prim: Usd.Prim, anim_prim: Usd.Prim):
    matching_joints = []
    missing_anim_joints = []
    not_animated_joints = []

    if skel_prim and skel_prim.IsValid() and anim_prim and anim_prim.IsValid() and\
       skel_prim.IsA(UsdSkel.Skeleton) and anim_prim.IsA(UsdSkel.Animation):

        anim_joints_attr = UsdSkel.Animation(anim_prim).GetJointsAttr()
        anim_joints = anim_joints_attr.Get()
        skel_cache = UsdSkel.Cache()
        skel_query = skel_cache.GetSkelQuery(UsdSkel.Skeleton(skel_prim))
        skel_joints = skel_query.GetJointOrder()

        if anim_joints and skel_joints:
            for j in anim_joints:
                if j in skel_joints:
                    matching_joints.append(j)
                else:
                    missing_anim_joints.append(j)
            for j in skel_joints:
                if j not in matching_joints:
                    not_animated_joints.append(j)

    return matching_joints, missing_anim_joints, not_animated_joints


def is_anim_bound_to_usd_skel(skel_prim: Usd.Prim, anim_prim: Usd.Prim) -> bool:
    """
    Checks if the skeleton binding of anim_prim matches skel_prim

    Args:
        - skel_prim (Usd.Prim): a Skeleton prim
        - anim_prim (Usd.Prim): a SkelAnim prim
    Returns:
        True if skel_prim is set as source skeleton to anim_prim
    """
    if anim_prim and anim_prim.IsValid() and anim_prim.IsA(UsdSkel.Animation) and\
            skel_prim and skel_prim.IsValid() and skel_prim.IsA(UsdSkel.Skeleton):
        skel_binding_rel = anim_prim.GetRelationship("animationSkelBinding:sourceSkeleton")
        if skel_binding_rel.IsValid():
            targets = skel_binding_rel.GetTargets()
            if skel_prim.GetPrimPath() in targets:
                return True
    return False


def is_anim_bound_to_skel(skel_prim: Usd.Prim, anim_prim: Usd.Prim) -> bool:
    """
    Checks if the skeleton binding of anim_prim matches skel_prim

    Args:
        - skel_prim (Usd.Prim): a Skeleton or SkelRoot prim
        - anim_prim (Usd.Prim): a SkelAnim prim
    Returns:
        True if skel_prim of any of its descendent Skeletons is set as source skeleton to anim_prim
    """
    if skel_prim and skel_prim.IsA(UsdSkel.Skeleton):
        return is_anim_bound_to_usd_skel(skel_prim, anim_prim)
    if anim_prim and anim_prim.IsValid() and anim_prim.IsA(UsdSkel.Animation) and\
            skel_prim and skel_prim.IsValid() and skel_prim.IsA(UsdSkel.Root):
        skel_binding_rel = anim_prim.GetRelationship("animationSkelBinding:sourceSkeleton")
        if skel_binding_rel.IsValid():
            targets = skel_binding_rel.GetTargets()

            def is_skel(prim: Usd.Prim, _) -> bool:
                return prim and prim.IsA(UsdSkel.Skeleton)

            skel_paths = traverse_prim(skel_prim.GetStage(), skel_prim.GetPath(), is_skel)
            for skel_path in skel_paths:
                if skel_path in targets:
                    return True
    return False


def is_anim_compatible_with_usd_skel(skel_prim: Usd.Prim, anim_prim: Usd.Prim) -> bool:
    """
    Checks if the skeleton is compatible with the animation,
        i.e. all joints of the animation are present in the Skeleton

    Args:
        - skel_prim (Usd.Prim): a Skeleton prim
        - anim_prim (Usd.Prim): a SkelAnim prim
    Returns:
        True if skel_prim is compatible to the animation
    """
    # check_compabitiliy will do the validation checks for us
    matching_joints, missing_anim_joints, _ = check_compatibility(skel_prim, anim_prim)
    if len(matching_joints) > 0 and len(missing_anim_joints) == 0:
        return True

    return False


def is_anim_compatible_with_skel(skel_prim: Usd.Prim, anim_prim: Usd.Prim) -> bool:
    """
    Checks if the skeleton is compatible with the animation,
        i.e. all joints of the animation are present in the Skeleton

    Args:
        - skel_prim (Usd.Prim): a Skeleton or SkelRoot prim
        - anim_prim (Usd.Prim): a SkelAnim prim
    Returns:
        True if skel_prim or any of its descendant Skeleton prims is compatible to the animation
    """
    if skel_prim and skel_prim.IsA(UsdSkel.Skeleton):
        return is_anim_compatible_with_usd_skel(skel_prim, anim_prim)
    if anim_prim and anim_prim.IsValid() and anim_prim.IsA(UsdSkel.Animation) and\
            skel_prim and skel_prim.IsValid() and skel_prim.IsA(UsdSkel.Root):

        def is_skel(prim: Usd.Prim, _) -> bool:
            return prim and prim.IsA(UsdSkel.Skeleton)

        stage = skel_prim.GetStage()
        skel_paths = traverse_prim(stage, skel_prim.GetPath(), is_skel)
        for skel_path in skel_paths:
            usd_skel_prim = stage.GetPrimAtPath(skel_path)
            if is_anim_compatible_with_usd_skel(usd_skel_prim, anim_prim):
                return True

    return False
