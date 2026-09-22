# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import os
import carb
import omni.ext
from typing import List, Optional
from pxr import Sdf, UsdSkel, Gf, UsdUtils, Usd
import RetargetingSchema
from .rig_automap_manager import RetargetAutoMapManager
from .rig import Rig, RetargetRig
from .utils import convert_trans_rots_to_pxr_matrices, get_stage_id, set_forward_axis, set_up_axis, rest_pose_exist
from ..bindings._omni_anim_retarget_core import *

ext_path = ""


class PublicExtension(omni.ext.IExt):
    def on_startup(self, ext_id):
        global ext_path
        ext_path = omni.kit.app.get_app().get_extension_manager().get_extension_path(ext_id)
        RetargetRig.set_extension_path(ext_path)
        rig_path = RetargetRig.get_system_rig_folder("Human")
        load_auto_map(rig_path, True)

    def on_shutdown(self):
        RetargetAutoMapManager.del_instance()


def load_auto_map(rig_path: str, reset_before_load: bool):
    RetargetAutoMapManager.get_instance().load_automaps(rig_path, reset_before_load)


def has_retarget_setup(skel_prim, min_tag_count=1):
    if skel_prim.HasAPI(RetargetingSchema.ControlRigAPI):
        control_rig_api = RetargetingSchema.ControlRigAPI(skel_prim)
        attr = control_rig_api.GetRetargetTagsAttr()
        if attr is not None:
            tags = attr.Get()
            if tags:
                count = 0
                for tag in tags:
                    if tag != "":
                        count += 1
                return count >= min_tag_count

    return False

def auto_setup(rigname: str, skel_prim_path: Sdf.Path, use_mapping=True, auto_facing=True, auto_tagging=True, auto_posing=True):
    """
        Attempt to automatically create retarget pose for the incoming UsdSkel Skeleton prim (source_skel_prim_path)

        Args:
            Sdf Path to UsdSkel Skeleton Prim

        Returns:
            return True if successful
            return False if not
    """
    stage = omni.usd.get_context().get_stage()
    skel_prim = stage.GetPrimAtPath(skel_prim_path)
    skeleton = None
    if skel_prim:
        skeleton = UsdSkel.Skeleton(skel_prim)
    else:
        # failed
        return False

    # first get the keyword from rig file
    # we need keywords - we can move keywords to RetargetAutoMapManager
    rig = RetargetRig(rigname)
    rig.set_skeleton(skeleton)
    return rig.auto_setup(use_mapping, auto_facing, auto_tagging, auto_posing)

def auto_setup_by_prim(rigname: str, skel_prim, use_mapping=True, auto_facing=True, auto_tagging=True, auto_posing=True):

    rig = RetargetRig(rigname)

    # we don't care about the name of the file
    success, _, template_file = rig.get_reference_skeleton()
    if not success:
        carb.log_error("Reference Template File is Missing.")
        return False

    if not skel_prim:
        carb.log_error("Invalid SkelPrim.")
        return False

    skel_prim_path = skel_prim.GetPath().pathString
    do_auto_facing = auto_facing
    do_auto_tagging = auto_tagging
    do_auto_posing = auto_posing

    skeleton = UsdSkel.Skeleton(skel_prim)
    rig.set_skeleton(skeleton)
    stage = skel_prim.GetStage()
    cache = UsdUtils.StageCache.Get()
    stage_id = cache.GetId(stage)
    if not Usd.StageCache.Id.IsValid(stage_id):
        carb.log_error(f"Stage Cache is invalid. Insert the stage to stage cache if this is not currently open stage {skel_prim.GetPath().pathString}.")
        carb.log_error(">>> UsdUtils.StageCache.Get().Insert(stage)/UsdUtils.StageCache.Get().Erase(stage)")

    # now create retarget controller
    retarget_controller = omni.anim.retarget.core.RetargetController(str(template_file), None, Usd.StageCache.Id.ToLongInt(stage_id), skel_prim_path)
    if retarget_controller:
        if use_mapping:
            _, success, facing_setup = RetargetAutoMapManager.get_instance().apply_best_automap(rig)
            # if we succeed, turn off auto face/auto tag
            if success:
                if facing_setup:
                    do_auto_facing = False
                    do_auto_tagging = False
                else:
                    # we have tagging, but not facing
                    do_auto_tagging = False

        keywords = rig.keywords

        # add keyword
        for tag in keywords.keys():
            retarget_controller.add_auto_setup_keywords(tag, keywords[tag])

        if do_auto_facing:
            # first do auto facing
            up_axis, forward_axis = retarget_controller.auto_facing()

            def get_axis_label(axis):
                if axis[0] == 1.0:
                    return "X"
                if axis[0] == -1.0:
                    return "MINUS X"
                if axis[1] == 1.0:
                    return "Y"
                if axis[1] == -1.0:
                    return "MINUS Y"
                if axis[2] == 1.0:
                    return "Z"
                if axis[2] == -1.0:
                    return "MINUS Z"
            # set the information
            set_up_axis(skeleton, get_axis_label(up_axis))
            set_forward_axis(skeleton, get_axis_label(forward_axis))

        if do_auto_tagging:
            # now auto tag
            tag_to_joint_map = retarget_controller.auto_tag()
            if len(tag_to_joint_map) == 0:
                return False
            tag_mapping = {}
            for tag_to_joint in tag_to_joint_map:
                tag_mapping[tag_to_joint[0]] = tag_to_joint[1]
            rig.set_joint_mappings(tag_mapping)

        if do_auto_posing:
            # if no bind pose or no rest pose, fail it
            if not rest_pose_exist(skeleton):
                carb.log_error(f"Could not automatically set animation retarget pose for {skel_prim.GetPath().pathString}. The character's bind pose is missing or invalid. To set the retarget pose, go to the Animation Retargeting window and hit \"Apply\" in the Retarget Pose section when character is in desired pose.")
                return False

            # third, auto pose
            target_translations: List[carb.Float3] = []
            target_rotations: List[carb.Float4] = []
            target_translations, target_rotations = retarget_controller.auto_pose()
            # now update to usd skeleton
            if len(target_translations) == 0:
                carb.log_error(f"Could not automatically set animation retarget pose for {skel_prim.GetPath().pathString}. The character's bind pose is missing or invalid. To set the retarget pose, go to the Animation Retargeting window and hit \"Apply\" in the Retarget Pose section when character is in desired pose.")
                return False

            transforms = convert_trans_rots_to_pxr_matrices(target_translations, target_rotations)
            control_rig_api = RetargetingSchema.ControlRigAPI(skel_prim)
            retarget_transforms_attr = control_rig_api.GetRetargetTransformsAttr()
            retarget_transforms_attr.Set(transforms)
        return True

    return False

def auto_pose(source_skel_prim_path: Sdf.Path, target_skel_prim_path: Sdf.Path):
    """
        Attempt to automatically create retarget pose for the incoming UsdSkel Skeleton prim (source_skel_prim_path)

        Args:
            Sdf Path to UsdSkel Skeleton Prim

        Returns:
            return True if successful
            return False if not
    """
    retarget_controller = omni.anim.retarget.core.RetargetController(None, str(source_skel_prim_path), -1, str(target_skel_prim_path))
    if retarget_controller:
        target_translations: List[carb.Float3] = []
        target_rotations: List[carb.Float4] = []
        target_translations, target_rotations = retarget_controller.auto_pose()
        # now update to usd skeleton
        if len(target_translations) == 0:
            return
        stage = omni.usd.get_context().get_stage()
        skel_prim = stage.GetPrimAtPath(target_skel_prim_path)
        if skel_prim:
            transforms = convert_trans_rots_to_pxr_matrices(target_translations, target_rotations)
            if not skel_prim.HasAPI(RetargetingSchema.ControlRigAPI):
                RetargetingSchema.ControlRigAPI.Apply(skel_prim)
            control_rig_api = RetargetingSchema.ControlRigAPI(skel_prim)
            retarget_transforms_attr = control_rig_api.GetRetargetTransformsAttr()
            retarget_transforms_attr.Set(transforms)
        else:
            carb.log_error("Invalid prim \"{}\" : requires Skeleton prim.".format(target_skel_prim_path))
