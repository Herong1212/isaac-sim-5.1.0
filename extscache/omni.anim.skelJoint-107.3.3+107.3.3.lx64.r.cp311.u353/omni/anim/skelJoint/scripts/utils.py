# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import carb

import omni.usd
from pxr import Sdf, Usd, UsdSkel, UsdGeom, Gf, Vt, Tf
import OmniSkelSchema

from typing import Tuple, List
from enum import Enum


def __rotation_degree_normalize(degree: float) -> float:
    while(degree < 0.0):
        degree += 360.0
    while (degree > 360.0):
        degree -= 360.0
    return degree


def __gf_vec3f_fast_compare(vec0: Gf.Vec3f, vec1: Gf.Vec3f, eps: float) -> bool:
    if not Gf.IsClose(vec0[0], vec1[0], eps):
        return False
    if not Gf.IsClose(vec0[1], vec1[1], eps):
        return False
    if not Gf.IsClose(vec0[2], vec1[2], eps):
        return False
    return True


def __gf_rotation_vec3f_fast_compare(vec0: Gf.Vec3f, vec1: Gf.Vec3f, eps: float) -> bool:
    delta0 = vec0[0] - vec1[0]
    if not Gf.IsClose(__rotation_degree_normalize(delta0), 0.0, eps) and not Gf.IsClose(__rotation_degree_normalize(delta0), 360.0, eps):
        return False
    delta1 = vec0[1] - vec1[1]
    if not Gf.IsClose(__rotation_degree_normalize(delta1), 0.0, eps) and not Gf.IsClose(__rotation_degree_normalize(delta1), 360.0, eps):
        return False
    delta2 = vec0[2] - vec1[2]
    if not Gf.IsClose(__rotation_degree_normalize(delta2), 0.0, eps) and not Gf.IsClose(__rotation_degree_normalize(delta2), 360.0, eps):
        return False
    return True


def find_skeleton(prim: Usd.Prim):
    while True:
        if not prim or prim.IsPseudoRoot():
            return Usd.Prim()
        if prim.IsA(UsdSkel.Skeleton) and prim.HasAPI(OmniSkelSchema.OmniSkeletonAPI):
            return prim
        if not prim.IsA(OmniSkelSchema.OmniJoint) and not prim.IsA(UsdGeom.Scope):
            return Usd.Prim()

        prim = prim.GetParent()


def get_joint_rotation_order_and_attrname(omniJoint: OmniSkelSchema.OmniJoint) -> [str, str]:
    if not omniJoint or not OmniSkelSchema.OmniJoint(omniJoint):
        return ["", ""]
    for op in OmniSkelSchema.OmniJoint(omniJoint).GetOrderedXformOps():
        op_type = op.GetOpType()
        if op_type in [UsdGeom.XformOp.TypeRotateXYZ, UsdGeom.XformOp.TypeRotateXZY, UsdGeom.XformOp.TypeRotateYXZ, UsdGeom.XformOp.TypeRotateYZX, UsdGeom.XformOp.TypeRotateZXY, UsdGeom.XformOp.TypeRotateZYX]:
            return [UsdGeom.XformOp.GetOpTypeToken(op_type), op.GetName()]
    return ["", ""]


def get_bind_poses(skeleton: UsdSkel.Skeleton) -> [Vt.Vec3fArray, Vt.Vec3fArray, Vt.Vec3fArray, Vt.TokenArray]:
    if not skeleton:
        return [Vt.Vec3fArray(), Vt.Vec3fArray(), Vt.Vec3fArray(), Vt.TokenArray()]
    stage = skeleton.GetPrim().GetStage()
    if stage is None:
        return [Vt.Vec3fArray(), Vt.Vec3fArray(), Vt.Vec3fArray(), Vt.TokenArray()]

    skel_path = skeleton.GetPrim().GetPath()
    joints = skeleton.GetJointsAttr().Get()
    joint_counts = len(joints)

    bindTranslations = Vt.Vec3fArray(joint_counts, Gf.Vec3f(0.0))
    bindRotations = Vt.Vec3fArray(joint_counts, Gf.Vec3f(0.0))
    bindScales = Vt.Vec3fArray(joint_counts, Gf.Vec3f(1.0))
    rotationOrders = Vt.TokenArray(joint_counts)

    for i in range(joint_counts):
        joint = joints[i]
        joint_path = skel_path.AppendPath(joint)
        joint_prim = stage.GetPrimAtPath(joint_path)
        omniJoint = OmniSkelSchema.OmniJoint(joint_prim)
        if not omniJoint:
            continue
        bindTranslations[i] = omniJoint.GetBindTranslationAttr().Get()
        bindRotations[i] = omniJoint.GetBindRotationAttr().Get()
        bindScales[i] = omniJoint.GetBindScaleAttr().Get()
        rotationOrders[i] = omniJoint.GetBindRotationAttr().GetCustomDataByKey("RotationOrder")

    return [bindTranslations, bindRotations, bindScales, rotationOrders]


def get_rest_poses(skeleton: UsdSkel.Skeleton) -> [Vt.Vec3fArray, Vt.Vec3fArray, Vt.Vec3fArray, Vt.TokenArray]:
    if not skeleton:
        return [Vt.Vec3fArray(), Vt.Vec3fArray(), Vt.Vec3fArray(), Vt.TokenArray()]
    stage = skeleton.GetPrim().GetStage()
    if stage is None:
        return [Vt.Vec3fArray(), Vt.Vec3fArray(), Vt.Vec3fArray(), Vt.TokenArray()]

    skel_path = skeleton.GetPrim().GetPath()
    joints = skeleton.GetJointsAttr().Get()
    joint_counts = len(joints)

    restTranslations = Vt.Vec3fArray(joint_counts, Gf.Vec3f(0.0))
    restRotations = Vt.Vec3fArray(joint_counts, Gf.Vec3f(0.0))
    restScales = Vt.Vec3fArray(joint_counts, Gf.Vec3f(1.0))
    rotationOrders = Vt.TokenArray(joint_counts)

    for i in range(joint_counts):
        joint = joints[i]
        joint_path = skel_path.AppendPath(joint)
        joint_prim = stage.GetPrimAtPath(joint_path)
        omniJoint = OmniSkelSchema.OmniJoint(joint_prim)
        if not omniJoint:
            continue
        restTranslations[i] = omniJoint.GetRestTranslationAttr().Get()
        restRotations[i] = omniJoint.GetRestRotationAttr().Get()
        restScales[i] = omniJoint.GetRestScaleAttr().Get()
        rotationOrders[i] = omniJoint.GetRestRotationAttr().GetCustomDataByKey("RotationOrder")

    return [restTranslations, restRotations, restScales, rotationOrders]


def get_retarget_poses(skeleton: UsdSkel.Skeleton) -> [Vt.Vec3fArray, Vt.Vec3fArray, Vt.Vec3fArray, Vt.TokenArray]:
    if not skeleton:
        return [Vt.Vec3fArray(), Vt.Vec3fArray(), Vt.Vec3fArray(), Vt.TokenArray()]
    stage = skeleton.GetPrim().GetStage()
    if stage is None:
        return [Vt.Vec3fArray(), Vt.Vec3fArray(), Vt.Vec3fArray(), Vt.TokenArray()]

    skel_path = skeleton.GetPrim().GetPath()
    joints = skeleton.GetJointsAttr().Get()
    joint_counts = len(joints)

    retargetTranslations = Vt.Vec3fArray(joint_counts, Gf.Vec3f(0.0))
    retargetRotations = Vt.Vec3fArray(joint_counts, Gf.Vec3f(0.0))
    retargetScales = Vt.Vec3fArray(joint_counts, Gf.Vec3f(1.0))
    rotationOrders = Vt.TokenArray(joint_counts)

    for i in range(joint_counts):
        joint = joints[i]
        joint_path = skel_path.AppendPath(joint)
        joint_prim = stage.GetPrimAtPath(joint_path)
        omniJoint = OmniSkelSchema.OmniJoint(joint_prim)
        if not omniJoint:
            continue
        retargetTranslations[i] = omniJoint.GetRetargetTranslationAttr().Get()
        retargetRotations[i] = omniJoint.GetRetargetRotationAttr().Get()
        retargetScales[i] = omniJoint.GetRetargetScaleAttr().Get()
        rotationOrders[i] = omniJoint.GetRetargetRotationAttr().GetCustomDataByKey("RotationOrder")

    return [retargetTranslations, retargetRotations, retargetScales, rotationOrders]


def get_joint_poses(skeleton: UsdSkel.Skeleton) -> [Vt.Vec3fArray, Vt.Vec3fArray, Vt.Vec3fArray, Vt.TokenArray]:
    if not skeleton:
        return [Vt.Vec3fArray(), Vt.Vec3fArray(), Vt.Vec3fArray(), Vt.TokenArray()]
    stage = skeleton.GetPrim().GetStage()
    if stage is None:
        return [Vt.Vec3fArray(), Vt.Vec3fArray(), Vt.Vec3fArray(), Vt.TokenArray()]

    skel_path = skeleton.GetPrim().GetPath()
    joints = skeleton.GetJointsAttr().Get()
    joint_counts = len(joints)

    jointTranslations = Vt.Vec3fArray(joint_counts, Gf.Vec3f(0.0))
    jointRotations = Vt.Vec3fArray(joint_counts, Gf.Vec3f(0.0))
    jointScales = Vt.Vec3fArray(joint_counts, Gf.Vec3f(1.0))
    rotationOrders = Vt.TokenArray(joint_counts)

    for i in range(joint_counts):
        joint = joints[i]
        joint_path = skel_path.AppendPath(joint)
        joint_prim = stage.GetPrimAtPath(joint_path)
        omniJoint = OmniSkelSchema.OmniJoint(joint_prim)
        if not omniJoint:
            continue
        jointTranslations[i] = Gf.Vec3f(omniJoint.GetPrim().GetAttribute("xformOp:translate").Get())
        rot_order, rot_attrname = get_joint_rotation_order_and_attrname(omniJoint)
        jointRotations[i] = Gf.Vec3f(omniJoint.GetPrim().GetAttribute(rot_attrname).Get())
        jointScales[i] = Gf.Vec3f(omniJoint.GetPrim().GetAttribute("xformOp:scale").Get())
        rotationOrders[i] = rot_order

    return [jointTranslations, jointRotations, jointScales, rotationOrders]


def set_joint_poses(skeleton: UsdSkel.Skeleton, translations: Vt.Vec3fArray, rotations: Vt.Vec3fArray, scales: Vt.Vec3fArray, rotationOrders: Vt.TokenArray) -> bool:
    if not skeleton:
        return False
    stage = skeleton.GetPrim().GetStage()
    if stage is None:
        return False

    skel_path = skeleton.GetPrim().GetPath()
    joints = skeleton.GetJointsAttr().Get()
    joint_counts = len(joints)

    joint_rotation_orders = Vt.TokenArray(joint_counts)
    joint_rotation_attrname = Vt.TokenArray(joint_counts)
    omniJoints = []
    for i in range(joint_counts):
        joint = joints[i]
        joint_path = skel_path.AppendPath(joint)
        joint_prim = stage.GetPrimAtPath(joint_path)
        omniJoint = OmniSkelSchema.OmniJoint(joint_prim)
        if not omniJoint:
            return False

        rot_order, rot_attrname = get_joint_rotation_order_and_attrname(omniJoint)
        joint_rotation_orders[i] = rot_order
        if joint_rotation_orders[i] != rotationOrders[i]:
            carb.log_warn(f"set_joint_poses joint {joint} rotation order {joint_rotation_orders[i]} mismatch desired rotation order {rotationOrders[i]}")
            return False
        joint_rotation_attrname[i] = rot_attrname
        omniJoints.append(omniJoint)
    session_layer = stage.GetSessionLayer()
    with Usd.EditContext(stage, stage.GetEditTargetForLocalLayer(session_layer)):
        with Sdf.ChangeBlock():
            for i in range(joint_counts):
                omniJoints[i].GetPrim().GetAttribute("xformOp:translate").Set(Gf.Vec3d(translations[i]))
                omniJoints[i].GetPrim().GetAttribute(joint_rotation_attrname[i]).Set(Gf.Vec3d(rotations[i]))
                omniJoints[i].GetPrim().GetAttribute("xformOp:scale").Set(Gf.Vec3d(scales[i]))

    return True


def is_joint_poses_matching_bind_poses(skeleton: UsdSkel.Skeleton) -> bool:
    if not skeleton:
        return False
    stage = skeleton.GetPrim().GetStage()
    if stage is None:
        return False

    skel_path = skeleton.GetPrim().GetPath()
    joints = skeleton.GetJointsAttr().Get()
    joint_counts = len(joints)

    for i in range(joint_counts):
        joint = joints[i]
        joint_path = skel_path.AppendPath(joint)
        joint_prim = stage.GetPrimAtPath(joint_path)
        omniJoint = OmniSkelSchema.OmniJoint(joint_prim)
        if not omniJoint:
            return False

        bindTranslation = omniJoint.GetBindTranslationAttr().Get()
        bindRotation = omniJoint.GetBindRotationAttr().Get()
        bindScale = omniJoint.GetBindScaleAttr().Get()
        bindRotationOrder = omniJoint.GetBindRotationAttr().GetCustomDataByKey("RotationOrder")

        jointTranslation = Gf.Vec3f(omniJoint.GetPrim().GetAttribute("xformOp:translate").Get())
        rot_order, rot_attrname = get_joint_rotation_order_and_attrname(omniJoint)
        jointRotation = Gf.Vec3f(omniJoint.GetPrim().GetAttribute(rot_attrname).Get())
        jointScale = Gf.Vec3f(omniJoint.GetPrim().GetAttribute("xformOp:scale").Get())
        jointRotationOrder = rot_order
        if not __gf_vec3f_fast_compare(bindTranslation, jointTranslation, 1e-3):
            return False
        if not __gf_rotation_vec3f_fast_compare(bindRotation, jointRotation, 1e-3):
            return False
        if not __gf_vec3f_fast_compare(bindScale, jointScale, 1e-3):
            return False
        if bindRotationOrder != jointRotationOrder:
            return False

    return True


def is_joint_poses_matching_rest_poses(skeleton: UsdSkel.Skeleton) -> bool:
    if not skeleton:
        return False
    stage = skeleton.GetPrim().GetStage()
    if stage is None:
        return False

    skel_path = skeleton.GetPrim().GetPath()
    joints = skeleton.GetJointsAttr().Get()
    joint_counts = len(joints)

    for i in range(joint_counts):
        joint = joints[i]
        joint_path = skel_path.AppendPath(joint)
        joint_prim = stage.GetPrimAtPath(joint_path)
        omniJoint = OmniSkelSchema.OmniJoint(joint_prim)
        if not omniJoint:
            return False

        restTranslation = omniJoint.GetRestTranslationAttr().Get()
        restRotation = omniJoint.GetRestRotationAttr().Get()
        restScale = omniJoint.GetRestScaleAttr().Get()
        restRotationOrder = omniJoint.GetRestRotationAttr().GetCustomDataByKey("RotationOrder")

        jointTranslation = Gf.Vec3f(omniJoint.GetPrim().GetAttribute("xformOp:translate").Get())
        rot_order, rot_attrname = get_joint_rotation_order_and_attrname(omniJoint)
        jointRotation = Gf.Vec3f(omniJoint.GetPrim().GetAttribute(rot_attrname).Get())
        jointScale = Gf.Vec3f(omniJoint.GetPrim().GetAttribute("xformOp:scale").Get())
        jointRotationOrder = rot_order
        if not __gf_vec3f_fast_compare(restTranslation, jointTranslation, 1e-3):
            return False
        if not __gf_rotation_vec3f_fast_compare(restRotation, jointRotation, 1e-3):
            return False
        if not __gf_vec3f_fast_compare(restScale, jointScale, 1e-3):
            return False
        if restRotationOrder != jointRotationOrder:
            return False

    return True


def is_joint_poses_matching_retarget_poses(skeleton: UsdSkel.Skeleton) -> bool:
    if not skeleton:
        return False
    stage = skeleton.GetPrim().GetStage()
    if stage is None:
        return False

    skel_path = skeleton.GetPrim().GetPath()
    joints = skeleton.GetJointsAttr().Get()
    joint_counts = len(joints)

    for i in range(joint_counts):
        joint = joints[i]
        joint_path = skel_path.AppendPath(joint)
        joint_prim = stage.GetPrimAtPath(joint_path)
        omniJoint = OmniSkelSchema.OmniJoint(joint_prim)
        if not omniJoint:
            return False

        retargetTranslation = omniJoint.GetRetargetTranslationAttr().Get()
        retargetRotation = omniJoint.GetRetargetRotationAttr().Get()
        retargetScale = omniJoint.GetRetargetScaleAttr().Get()
        retargetRotationOrder = omniJoint.GetRetargetRotationAttr().GetCustomDataByKey("RotationOrder")

        jointTranslation = Gf.Vec3f(omniJoint.GetPrim().GetAttribute("xformOp:translate").Get())
        rot_order, rot_attrname = get_joint_rotation_order_and_attrname(omniJoint)
        jointRotation = Gf.Vec3f(omniJoint.GetPrim().GetAttribute(rot_attrname).Get())
        jointScale = Gf.Vec3f(omniJoint.GetPrim().GetAttribute("xformOp:scale").Get())
        jointRotationOrder = rot_order
        if not __gf_vec3f_fast_compare(retargetTranslation, jointTranslation, 1e-3):
            return False
        if not __gf_rotation_vec3f_fast_compare(retargetRotation, jointRotation, 1e-3):
            return False
        if not __gf_vec3f_fast_compare(retargetScale, jointScale, 1e-3):
            return False
        if retargetRotationOrder != jointRotationOrder:
            return False

    return True


def is_retarget_poses_matching_bind_poses(skeleton: UsdSkel.Skeleton) -> bool:
    if not skeleton:
        return False
    stage = skeleton.GetPrim().GetStage()
    if stage is None:
        return False

    skel_path = skeleton.GetPrim().GetPath()
    joints = skeleton.GetJointsAttr().Get()
    joint_counts = len(joints)

    for i in range(joint_counts):
        joint = joints[i]
        joint_path = skel_path.AppendPath(joint)
        joint_prim = stage.GetPrimAtPath(joint_path)
        omniJoint = OmniSkelSchema.OmniJoint(joint_prim)
        if not omniJoint:
            return False

        bindTranslation = omniJoint.GetBindTranslationAttr().Get()
        bindRotation = omniJoint.GetBindRotationAttr().Get()
        bindScale = omniJoint.GetBindScaleAttr().Get()
        bindRotationOrder = omniJoint.GetBindRotationAttr().GetCustomDataByKey("RotationOrder")

        retargetTranslation = omniJoint.GetRetargetTranslationAttr().Get()
        retargetRotation = omniJoint.GetRetargetRotationAttr().Get()
        retargetScale = omniJoint.GetRetargetScaleAttr().Get()
        retargetRotationOrder = omniJoint.GetRetargetRotationAttr().GetCustomDataByKey("RotationOrder")

        if not __gf_vec3f_fast_compare(bindTranslation, retargetTranslation, 1e-3):
            return False
        if not __gf_rotation_vec3f_fast_compare(bindRotation, retargetRotation, 1e-3):
            return False
        if not __gf_vec3f_fast_compare(bindScale, retargetScale, 1e-3):
            return False
        if bindRotationOrder != retargetRotationOrder:
            return False

    return True


def is_rest_poses_matching_bind_poses(skeleton: UsdSkel.Skeleton) -> bool:
    if not skeleton:
        return False
    stage = skeleton.GetPrim().GetStage()
    if stage is None:
        return False

    skel_path = skeleton.GetPrim().GetPath()
    joints = skeleton.GetJointsAttr().Get()
    joint_counts = len(joints)

    for i in range(joint_counts):
        joint = joints[i]
        joint_path = skel_path.AppendPath(joint)
        joint_prim = stage.GetPrimAtPath(joint_path)
        omniJoint = OmniSkelSchema.OmniJoint(joint_prim)
        if not omniJoint:
            return False

        bindTranslation = omniJoint.GetBindTranslationAttr().Get()
        bindRotation = omniJoint.GetBindRotationAttr().Get()
        bindScale = omniJoint.GetBindScaleAttr().Get()
        bindRotationOrder = omniJoint.GetBindRotationAttr().GetCustomDataByKey("RotationOrder")

        restTranslation = omniJoint.GetRestTranslationAttr().Get()
        restRotation = omniJoint.GetRestRotationAttr().Get()
        restScale = omniJoint.GetRestScaleAttr().Get()
        restRotationOrder = omniJoint.GetRestRotationAttr().GetCustomDataByKey("RotationOrder")

        if not __gf_vec3f_fast_compare(bindTranslation, restTranslation, 1e-3):
            return False
        if not __gf_rotation_vec3f_fast_compare(bindRotation, restRotation, 1e-3):
            return False
        if not __gf_vec3f_fast_compare(bindScale, restScale, 1e-3):
            return False
        if bindRotationOrder != restRotationOrder:
            return False

    return True
