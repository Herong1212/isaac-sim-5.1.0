# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import carb
import omni
from pxr import Vt, UsdSkel, Gf, Usd, UsdUtils
import RetargetingSchema, OmniSkelSchema
from typing import Dict, List
import omni.kit.commands

def convert_to_simple_joints(joints):
    simple_joints = []
    for joint in joints:
        simple_joints.append(joint.split("/")[-1])
    return simple_joints


def get_joint_token_from_simple_joint(skeleton, simple_joint):
    """ get full path name from the skeleton """
    if skeleton:
        joint_attr = skeleton.GetJointsAttr()
        if joint_attr:
            joints = convert_to_simple_joints(joint_attr.Get())
            for i, joint in enumerate(joints):
                if joint == simple_joint:
                    return joint_attr.Get()[i]
    return ""


def get_joint_list(skeleton):
    """ get full path name from the skeleton """
    if skeleton:
        joint_attr = skeleton.GetJointsAttr()
        if joint_attr:
            joints = convert_to_simple_joints(joint_attr.Get())
            return joints
    return []


def get_skeleton_tag_joint_dict(skeleton):
    tag_joint_dict: Dict[str, str] = {}
    if skeleton:
        skel_prim = skeleton.GetPrim()
        tags = []

        if skeleton and skel_prim.HasAPI(RetargetingSchema.ControlRigAPI):
            control_rig_api = RetargetingSchema.ControlRigAPI(skel_prim)
            retarget_attr = control_rig_api.GetRetargetTagsAttr()
            if (retarget_attr):
                tags = retarget_attr.Get()
                if tags and len(tags) > 0:
                    joint_attr = skeleton.GetJointsAttr()
                    if joint_attr:
                        joints = convert_to_simple_joints(joint_attr.Get())
                        for i, joint in enumerate(joints):
                            if tags[i] != "":
                                tag_joint_dict[tags[i]] = joint
    return tag_joint_dict


def get_joint_list_from_dict(key_list, tag_data_dict):
    joint_list = []
    for key in key_list:
        joint_list.append(tag_data_dict[key])

    return joint_list


def get_tags_token_from_dict(skeleton, tag_joint_dict):
    """ Convert tag_joint_dict to token array of tags """
    if skeleton:
        joint_attr = skeleton.GetJointsAttr()
        if joint_attr:
            joints = convert_to_simple_joints(joint_attr.Get())
            tags = Vt.TokenArray(len(joints))
            # flip the dict
            tag_keys = list(tag_joint_dict.keys())
            joint_values = get_joint_list_from_dict(tag_keys, tag_joint_dict)
            joint_tag_dict: Dict[str, str] = {}
            # this will override if there is duplicated value - i.e. multiple joints
            for i, joint in enumerate(joint_values):
                # ensure this joint exists in the joints
                if joint in joints:
                    joint_tag_dict[joint] = tag_keys[i]
            for i, joint in enumerate(joints):
                if (joint in joint_values):
                    tags[i] = joint_tag_dict[joint]
                else:
                    tags[i] = ""
    return tags


def find_skel_prims(stage, skel_paths: list):
    skel_prims = set()
    for skel_path in skel_paths:
        prim = stage.GetPrimAtPath(skel_path)
        if not prim:
            continue
        if UsdSkel.Skeleton(prim):
            skel_prims.add(prim)
        else:
            carb.log_error("Path \"{}\" is not a skeleton!  Skipping.".format(skel_path))
    return skel_prims


def get_retarget_pose(skeleton):
    if not bool(skeleton):
        return []
    # if we don't have retarget transform, we go through rest transform and bind transform
    transforms_attr = skeleton.GetPrim().GetAttribute("controlRig:retargetTransforms")
    if transforms_attr:
        transforms = transforms_attr.Get()
        if transforms:
            return transforms
    transforms_attr = skeleton.GetRestTransformsAttr()
    if transforms_attr:
        transforms = transforms_attr.Get()
        if transforms:
            return transforms

    transforms_attr = skeleton.GetBindTransformsAttr()
    if transforms_attr:
        transforms = transforms_attr.Get()
    return transforms


def have_retarget_tag(skeleton):
    return skeleton.GetPrim().HasAttribute("controlRig:retargetTags")


def have_retarget_pose(skeleton):
    return skeleton.GetPrim().HasAttribute("controlRig:retargetTransforms")


def get_forward_up_axis(skeleton):
    forward_axis = 'Z'
    up_axis = 'Y'
    if skeleton:
        skel_prim = skeleton.GetPrim()
        if skel_prim:
            if skel_prim.HasAttribute("controlRig:upAxis"):
                up_axis = skel_prim.GetAttribute("controlRig:upAxis").Get()
                if not up_axis:
                    up_axis = 'Y'
            if skel_prim.HasAttribute("controlRig:forwardAxis"):
                forward_axis = skel_prim.GetAttribute("controlRig:forwardAxis").Get()
                if not forward_axis:
                    forward_axis = 'Z'
    return forward_axis, up_axis


def convert_matrix_to_trans_rots(transforms):
    translations: List[carb.Float3] = []
    rotations: List[carb.Float4] = []

    for transform in transforms:
        trans = transform.ExtractTranslation()
        quat = transform.ExtractRotationQuat()
        translations.append(carb.Float3(trans[0], trans[1], trans[2]))
        rotations.append(carb.Float4(quat.imaginary[0], quat.imaginary[1], quat.imaginary[2], quat.real))

    return translations, rotations


def convert_trans_rots_to_pxr(translations, rotations):
    vt_translations = []
    vt_rotations = []
    vt_scales = []
    for i, translation in enumerate(translations):
        vt_translations.append(Gf.Vec3f(translation[0], translation[1], translation[2]))
        vt_rotations.append(Gf.Quatf(rotations[i][3], rotations[i][0], rotations[i][1], rotations[i][2]))
        vt_scales.append(Gf.Vec3h(1.0, 1.0, 1.0))
    return vt_translations, vt_rotations, vt_scales


def convert_trans_rots_to_pxr_matrices(translations, rotations):
    gf_matrices = []
    for i, translation in enumerate(translations):
        transform = Gf.Matrix4d(1)
        transform.SetTranslateOnly(Gf.Vec3d(translation[0], translation[1], translation[2]))
        transform.SetRotateOnly(Gf.Rotation(Gf.Quatd(rotations[i][3], rotations[i][0], rotations[i][1], rotations[i][2])))
        gf_matrices.append(transform)
    return gf_matrices


def is_same_skeleton(a, b):
    return (a == b or a.GetPrim().GetPath() == b.GetPrim().GetPath())

def get_joint_skeleton_token(prim):
    if prim.IsA(OmniSkelSchema.OmniJoint):
        parent = prim.GetParent()
        while parent and not parent.IsA(UsdSkel.Skeleton):
            parent = parent.GetParent()
        if parent and parent.IsA(UsdSkel.Skeleton):
            parent.GetPath().MakeRelativePath(prim.GetPath())
            return UsdSkel.Skeleton(parent), prim.GetPath().pathString
    return UsdSkel.Skeleton(), ""

def get_selected_joint(skeleton):
    import omni.usd
    # find currently seleced joint
    usd_context = omni.usd.get_context()
    stage = usd_context.get_stage()
    selection = usd_context.get_selection()
    selected_prims = selection.get_selected_prim_paths()
    if len(selected_prims) > 0:
        prim = stage.GetPrimAtPath(selected_prims[0])
        if OmniSkelSchema.OmniJoint(prim):
            #selected_skeleton, joint_token = OmniSkelSchema.OmniJoint(prim).GetJoint()
            selected_skeleton, joint_token = get_joint_skeleton_token(prim)
            if is_same_skeleton(selected_skeleton, skeleton):
                simple_joint = joint_token.split("/")[-1]
                return simple_joint
    return None


def apply_control_rig_api(skeleton):
    """ we still need this version, when undo is not possible because
    some of the actions will require it to apply right away """
    skel_prim = skeleton.GetPrim()
    if not skel_prim.HasAPI(RetargetingSchema.ControlRigAPI):
        RetargetingSchema.ControlRigAPI.Apply(skel_prim)


def set_up_axis(skeleton, up_axis):
    apply_control_rig_api(skeleton)
    skel_prim = skeleton.GetPrim()
    if skel_prim.HasAttribute("controlRig:upAxis"):
        skel_prim.GetAttribute("controlRig:upAxis").Set(up_axis)
    else:
        skel_prim.CreateAttribute("controlRig:upAxis", up_axis, False)


def set_forward_axis(skeleton, forward_axis):
    apply_control_rig_api(skeleton)
    skel_prim = skeleton.GetPrim()
    if skel_prim.HasAttribute("controlRig:forwardAxis"):
        skeleton.GetPrim().GetAttribute("controlRig:forwardAxis").Set(forward_axis)
    else:
        skel_prim.CreateAttribute("controlRig:forwardAxis", forward_axis, False)


def uniform_absolute_path(path):
    if len(path) == 1:
        return path[0].lower()

    # Windows path
    if len(path) > 1 and path[1] == ":":
        # Here use upper drive letter, otherwise content_browser.navigate_to does not work
        path = path[0].upper() + path[1:]
    path = path.replace("\\", "/")
    path = path.replace("\\\\", "/")

    if path.startswith("omniverse://"):
        path = path[0:12] + path[12:].replace("//", "/")
    else:
        path = path.replace("//", "/")
    path = path.replace("\\/", "/")
    path = path.replace("/\\", "/")

    if path.startswith("omniverse://"):  # omni path
        path_prefix = "omniverse://"
        asset_path = path[12:]
        if "/" in path[12:]:
            index = asset_path.index("/")
            path_prefix += asset_path[0:index]
            asset_path = asset_path[index:]
    elif path[1] == ":":  # windows path
        path_prefix = path[0:2]
        asset_path = path[2:]
    else:  # linux path
        path_prefix = ""
        asset_path = path

    parts = asset_path.split("/")
    results = []
    for part in parts:
        if part == "..":
            if results:
                results.pop(-1)
            if not results:
                break
        elif part != ".":
            results.append(part)

    return path_prefix + "/".join(results)

def get_stage(stage_id):
    if stage_id == -1:
        return omni.usd.get_context().get_stage()
    else:
        return UsdUtils.StageCache.Get().Find(Usd.StageCache.Id.FromLongInt(stage_id))

def get_stage_id(stage):
    return Usd.StageCache.Id.ToLongInt(UsdUtils.StageCache.Get().GetId(stage))

def rest_pose_exist(skeleton):
    # if we don't have retarget transform, we go through rest transform and bind transform
    transforms_attr = skeleton.GetRestTransformsAttr()
    if transforms_attr:
        transforms = transforms_attr.Get()
        if transforms == None or len(transforms) == 0:
            return False

        identity_only = True
        for transform in transforms:
            if transform != Gf.Matrix4d(1.0):
                identity_only = False

        if identity_only:
            #carb.log_error("All rest transform is identity.")
            return False

        return True

    transforms_attr = skeleton.GetBindTransformsAttr()
    if transforms_attr:
        transforms = transforms_attr.Get()
        if transforms == None or len(transforms) == 0:
            return False

        identity_only = True
        for transform in transforms:
            if transform != Gf.Matrix4d(1.0):
                identity_only = False

        if identity_only:
            #carb.log_error("All rest transform is identity.")
            return False

        return True

    return False

def load_retarget_pose(skel_path):
    omni.kit.commands.execute(
        "SwitchSkeletonTransformMode",
        skeleton_path=skel_path,
        #retarget pose is mode 1
        transform_mode=1
    )

def unload_retarget_pose(skel_path):
    omni.kit.commands.execute(
        "SwitchSkeletonTransformMode",
        skeleton_path=skel_path,
        #retarget pose is mode 1
        transform_mode=0
    )
