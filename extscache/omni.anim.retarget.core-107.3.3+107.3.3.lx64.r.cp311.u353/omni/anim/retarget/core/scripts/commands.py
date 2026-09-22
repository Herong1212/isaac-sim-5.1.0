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
import omni.usd
from pxr import Vt, Sdf, UsdSkel, Gf, UsdUtils, Usd
import RetargetingSchema
from .utils import find_skel_prims, get_tags_token_from_dict, get_retarget_pose, convert_matrix_to_trans_rots, convert_trans_rots_to_pxr_matrices, get_stage, load_retarget_pose, unload_retarget_pose
from typing import Dict, List

# feet IK settings
SETTING_RETARGET_ENABLE_FEET_IK = "/persistent/exts/omni.anim.retarget.core/enableFeetIK"
SETTING_RETARGET_FEET_IK_ACTIVATION = "/persistent/exts/omni.anim.retarget.core/feetIKActivation"
SETTING_RETARGET_FEET_IK_TAGS = "/persistent/exts/omni.anim.retarget.core/feetIKTags"

class SetSkeletonJointTagPairCommand(omni.kit.commands.Command):
    def __init__(self, stage_id, skel_paths: list, tag_joint_dict: Dict[str, str]):
        self._usd_undo = None
        self._stage_id = stage_id
        self._skel_paths = skel_paths
        self._tag_joint_dict = tag_joint_dict

    def do(self):
        stage = get_stage(self._stage_id)
        skel_prims = find_skel_prims(stage, self._skel_paths)

        if len(skel_prims) == 0:
            return

        self._usd_undo = omni.kit.usd_undo.UsdEditTargetUndo(stage.GetEditTarget())
        for skel_prim in skel_prims:
            self._usd_undo.reserve(skel_prim.GetPath())
            tags = get_tags_token_from_dict(UsdSkel.Skeleton(skel_prim), self._tag_joint_dict)
            if not skel_prim.HasAPI(RetargetingSchema.ControlRigAPI):
                RetargetingSchema.ControlRigAPI.Apply(skel_prim)
            control_rig_api = RetargetingSchema.ControlRigAPI(skel_prim)
            control_rig_api.GetRetargetTagsAttr().Set(tags)

    def undo(self):
        if self._usd_undo is not None:
            self._usd_undo.undo()


class ClearRetargetTagsCommand(omni.kit.commands.Command):
    def __init__(self, stage_id, skel_paths: list):
        self._usd_undo = None
        self._stage_id = stage_id
        self._skel_paths = skel_paths

    def do(self):
        stage = get_stage(self._stage_id)
        skel_prims = find_skel_prims(stage, self._skel_paths)

        if len(skel_prims) == 0:
            return

        self._usd_undo = omni.kit.usd_undo.UsdEditTargetUndo(stage.GetEditTarget())
        for skel_prim in skel_prims:
            self._usd_undo.reserve(skel_prim.GetPath())
            if not skel_prim.HasAPI(RetargetingSchema.ControlRigAPI):
                RetargetingSchema.ControlRigAPI.Apply(skel_prim)
            control_rig_api = RetargetingSchema.ControlRigAPI(skel_prim)
            control_rig_api.GetRetargetTagsAttr().Clear()

    def undo(self):
        if self._usd_undo is not None:
            self._usd_undo.undo()


class SetSkeletonTagsCommand(omni.kit.commands.Command):
    def __init__(self, stage_id, skel_paths: list, tags: Vt.TokenArray):
        self._usd_undo = None
        self._stage_id = stage_id
        self._skel_paths = skel_paths
        self._tags = tags

    def do(self):
        stage = get_stage(self._stage_id)
        skel_prims = find_skel_prims(stage, self._skel_paths)

        if len(skel_prims) == 0:
            return
        self._usd_undo = omni.kit.usd_undo.UsdEditTargetUndo(stage.GetEditTarget())
        for skel_prim in skel_prims:
            self._usd_undo.reserve(skel_prim.GetPath())
            if not skel_prim.HasAPI(RetargetingSchema.ControlRigAPI):
                RetargetingSchema.ControlRigAPI.Apply(skel_prim)
            control_rig_api = RetargetingSchema.ControlRigAPI(skel_prim)
            control_rig_api.GetRetargetTagsAttr().Set(self._tags)

    def undo(self):
        if self._usd_undo is not None:
            self._usd_undo.undo()


class SaveRetargetPoseCommand(omni.kit.commands.Command):
    def __init__(self, stage_id, skel_paths: list):
        self._usd_undo = None
        self._stage_id = stage_id
        self._skel_paths = skel_paths

    def do(self):
        stage = get_stage(self._stage_id)
        skel_prims = set()
        for skel_path in self._skel_paths:
            prim = stage.GetPrimAtPath(skel_path)
            if not prim:
                continue

            if UsdSkel.Skeleton(prim):
                skel_prims.add(prim)
            else:
                carb.log_error("Path \"{}\" is not a skeleton!  Skipping.".format(skel_path))

        if len(skel_prims) == 0:
            return

        skel_cache = UsdSkel.Cache()
        self._save_operation(skel_prims, skel_cache, stage)

    def _save_operation(self, skel_prims, skel_cache, stage):
        import omni.timeline
        time_code = omni.timeline.get_timeline_interface().get_current_time() * stage.GetTimeCodesPerSecond()
        self._usd_undo = omni.kit.usd_undo.UsdEditTargetUndo(stage.GetEditTarget())

        for skel_prim in skel_prims:
            skel_query = skel_cache.GetSkelQuery(UsdSkel.Skeleton(skel_prim))

            self._usd_undo.reserve(skel_prim.GetPath())
            if not skel_prim.HasAPI(RetargetingSchema.ControlRigAPI):
                RetargetingSchema.ControlRigAPI.Apply(skel_prim)
            control_rig_api = RetargetingSchema.ControlRigAPI(skel_prim)
            retarget_transforms_attr = control_rig_api.GetRetargetTransformsAttr()

            transforms = skel_query.ComputeJointLocalTransforms(time_code)
            retarget_transforms_attr.Set(transforms)

    def undo(self):
        if self._usd_undo is not None:
            self._usd_undo.undo()


class LoadRetargetPoseCommand(omni.kit.commands.Command):
    def __init__(self, stage_id, skel_paths: list):
        self._stage_id = stage_id
        self._skel_paths = skel_paths

    def do(self):
        stage = get_stage(self._stage_id)
        skel_prims = set()
        for skel_path in self._skel_paths:
            prim = stage.GetPrimAtPath(skel_path)
            if not prim:
                continue

            if UsdSkel.Skeleton(prim):
                skel_prims.add(prim)
            else:
                carb.log_error("Path \"{}\" is not a skeleton!  Skipping.".format(skel_path))

        if len(skel_prims) == 0:
            return

        for skel_prim in skel_prims:
            skeleton = UsdSkel.Skeleton(skel_prim)

            if not skel_prim.HasAPI(RetargetingSchema.ControlRigAPI):
                carb.log_error("Retarget Transform \"{}\" doesn't exist.".format(skel_path))
                continue

            load_retarget_pose(skel_path)

    def undo(self):
        pass


class ResetRetargetPoseCommand(omni.kit.commands.Command):
    def __init__(self, stage_id, skel_paths: list):
        self._usd_undo = None
        self._stage_id = stage_id
        self._skel_paths = skel_paths

    def do(self):
        stage = get_stage(self._stage_id)
        skel_prims = set()
        for skel_path in self._skel_paths:
            prim = stage.GetPrimAtPath(skel_path)
            if not prim:
                continue

            if UsdSkel.Skeleton(prim):
                skel_prims.add(prim)
            else:
                carb.log_error("Path \"{}\" is not a skeleton!  Skipping.".format(skel_path))

        if len(skel_prims) == 0:
            return

        self._remove_operation(skel_prims, stage)

    def _remove_operation(self, skel_prims, stage):
        self._usd_undo = omni.kit.usd_undo.UsdEditTargetUndo(stage.GetEditTarget())
        for skel_prim in skel_prims:
            if not skel_prim.HasAPI(RetargetingSchema.ControlRigAPI):
                continue

            self._usd_undo.reserve(skel_prim.GetPath().AppendProperty("controlRig:retargetTransforms"))
            attr = skel_prim.GetAttribute("controlRig:retargetTransforms")
            if attr:
                attr.Clear()

            pose = get_retarget_pose(UsdSkel.Skeleton(skel_prim))
            attr.Set(pose)

            #I have to unload and load to refresh
            unload_retarget_pose(skel_prim.GetPath().pathString)
            load_retarget_pose(skel_prim.GetPath().pathString)

    def undo(self):
        if self._usd_undo is not None:
            self._usd_undo.undo()


class SetSkeletonUpForwardAxis(omni.kit.commands.Command):
    def __init__(self, stage_id, skel_paths: list, is_up_axis: bool, axis: str):
        self._usd_undo = None
        self._stage_id = stage_id
        self._skel_paths = skel_paths
        self._is_up_axis = is_up_axis
        self._axis = axis

    def do(self):
        stage = get_stage(self._stage_id)
        skel_prims = find_skel_prims(stage, self._skel_paths)
        if len(skel_prims) == 0:
            return

        self._usd_undo = omni.kit.usd_undo.UsdEditTargetUndo(stage.GetEditTarget())
        for skel_prim in skel_prims:
            self._usd_undo.reserve(skel_prim.GetPath())
            if not skel_prim.HasAPI(RetargetingSchema.ControlRigAPI):
                RetargetingSchema.ControlRigAPI.Apply(skel_prim)
            if self._is_up_axis:
                attribute = "controlRig:upAxis"
            else:
                attribute = "controlRig:forwardAxis"

            if skel_prim.HasAttribute(attribute):
                skel_prim.GetAttribute(attribute).Set(self._axis)
            else:
                skel_prim.CreateAttribute(attribute, self._axis, False)

    def undo(self):
        if self._usd_undo is not None:
            self._usd_undo.undo()


class SaveRetargetPoseTransformCommand(omni.kit.commands.Command):
    def __init__(self, stage_id, skel_paths: list, transforms: list):
        self._usd_undo = None
        self._stage_id = stage_id
        self._skel_paths = skel_paths
        self._transforms = transforms

    def do(self):
        stage = get_stage(self._stage_id)
        skel_prims = set()
        for skel_path in self._skel_paths:
            prim = stage.GetPrimAtPath(skel_path)
            if not prim:
                continue

            if UsdSkel.Skeleton(prim):
                skel_prims.add(prim)
            else:
                carb.log_error("Path \"{}\" is not a skeleton!  Skipping.".format(skel_path))

        if len(skel_prims) == 0:
            return

        self._usd_undo = omni.kit.usd_undo.UsdEditTargetUndo(stage.GetEditTarget())

        for skel_prim in skel_prims:
            self._usd_undo.reserve(skel_prim.GetPath())
            if not skel_prim.HasAPI(RetargetingSchema.ControlRigAPI):
                RetargetingSchema.ControlRigAPI.Apply(skel_prim)
            control_rig_api = RetargetingSchema.ControlRigAPI(skel_prim)
            retarget_transforms_attr = control_rig_api.GetRetargetTransformsAttr()
            retarget_transforms_attr.Set(self._transforms)

    def undo(self):
        if self._usd_undo is not None:
            self._usd_undo.undo()

class EnableRetargetFeetIK(omni.kit.commands.Command):
    # enable = whether to enable feet IK or not
    # feetTags = [left_foot_root_tag, left_feet_end_tag, right_foot_root_tag, right_feet_end_tag]
    def __init__(self, enable=True, feetTags=["LeftLeg", "LeftFoot", "RightLeg", "RightFoot"], feetActivation=0.2):
        self._enable = enable
        self._feetTags = feetTags
        self._feetActivation = feetActivation

    def do(self):
        settings = carb.settings.get_settings()
        self._old_enable = settings.get(SETTING_RETARGET_ENABLE_FEET_IK)
        self._old_feetTags = settings.get(SETTING_RETARGET_FEET_IK_TAGS)
        self._old_feeetActivation = settings.get(SETTING_RETARGET_FEET_IK_ACTIVATION)

        settings.set(SETTING_RETARGET_ENABLE_FEET_IK, self._enable)
        settings.set(SETTING_RETARGET_FEET_IK_ACTIVATION, self._feetActivation)
        settings.set(SETTING_RETARGET_FEET_IK_TAGS, self._feetTags)


    def undo(self):
        if self._old_enable is not None:
            settings = carb.settings.get_settings()
            settings.set(SETTING_RETARGET_ENABLE_FEET_IK, self._old_enable)
            settings.set(SETTING_RETARGET_FEET_IK_ACTIVATION, self._old_feetActivation)
            settings.set(SETTING_RETARGET_FEET_IK_TAGS, self._old_feetTags)

class CreateRetargetAnimationsCommand(omni.kit.commands.Command):
    """
    Create Retarget Animations **Command**.

    Args:
        source_skeleton_path: path string of source skeleton prim
        target_skeleton_path: path string of target skeleton prim
        source_animation_paths: path strings of source animation prims
        target_animation_parent_path: path string of parent prim of target animation
        set_root_identity: If True, clear the root transforms after retargeting
        allow_default_transforms: If True and no joints need mapping, use the source transforms as the default
                                  (useful if the source animation has possibly already been retargeted)
    """
    def __init__(
        self,
        source_skeleton_path: str,
        target_skeleton_path: str,
        source_animation_paths: List[str],
        target_animation_parent_path: str,
        set_root_identity: bool,
        allow_default_transforms: bool = False
    ):
        self._usd_undo = None
        self._source_skeleton_path = source_skeleton_path
        self._target_skeleton_path = target_skeleton_path

        self._source_animation_paths = source_animation_paths
        self._target_animation_parent_path = target_animation_parent_path
        self._set_root_identity = set_root_identity
        self._allow_default_transforms = allow_default_transforms

    def do(self):
        stage = omni.usd.get_context().get_stage()

        source_skel_prim = stage.GetPrimAtPath(self._source_skeleton_path)
        source_skeleton = None
        if not source_skel_prim:
            carb.log_error("Path \"{}\" is not a valid prim! Aborting...".format(self._source_skeleton_path))
            return

        source_skeleton = UsdSkel.Skeleton(source_skel_prim)
        if not source_skeleton:
            carb.log_error("Path \"{}\" is not a skeleton! Aborting...".format(self._source_skeleton_path))
            return

        # if exists, we create as a child with same name
        target_anim_parent_prim = stage.GetPrimAtPath(self._target_animation_parent_path)
        if not target_anim_parent_prim:
            carb.log_error("Target Path \"{}\" is not valid! Aborting...".format(self._target_animation_parent_path))
            return

        target_skeleton_path = self._target_skeleton_path
        target_skel_prim = stage.GetPrimAtPath(target_skeleton_path)
        target_skeleton = None
        if not target_skel_prim:
            carb.log_error("Path \"{}\" is not a valid prim! Aborting...".format(target_skeleton_path))
            return

        target_skeleton = UsdSkel.Skeleton(target_skel_prim)
        if not target_skeleton:
            carb.log_error("Path \"{}\" is not a skeleton! Aborting...".format(target_skeleton_path))
            return

        # create retarget controller
        retarget_controller = omni.anim.retarget.core.RetargetController(
            None,
            self._source_skeleton_path,
            -1,
            target_skeleton_path
        )

        self._usd_undo = omni.kit.usd_undo.UsdEditTargetUndo(stage.GetEditTarget())

        # it's better to reverse, so we can remove from back
        source_rest_transforms = get_retarget_pose(source_skeleton)

        def convert_vtarray_to_list(array):
            ret_list = []
            for a in array:
                ret_list.append(a)
            return ret_list

        def get_target_transforms(mapping_table, source_transforms):
            if self._allow_default_transforms and not mapping_table:
                return convert_matrix_to_trans_rots(source_transforms)
            else:
                source_mod_transforms = source_rest_transforms
                for i in mapping_table:
                    source_mod_transforms[i] = source_transforms[mapping_table[i]]

                source_translations, source_rotations = convert_matrix_to_trans_rots(source_mod_transforms)
                # retarget
                target_translations: List[carb.Float3] = []
                target_rotations: List[carb.Float4] = []
                return retarget_controller.retarget(source_translations, source_rotations)

        for source_anim_path in self._source_animation_paths:

            source_skel_anim = UsdSkel.Animation(stage.GetPrimAtPath(source_anim_path))
            if not source_skel_anim:
                carb.log_error("Path \"{}\" is not a valid prim! Aborting...".format(source_anim_path))
                continue

            source_skel_anim_name = source_anim_path.split("/")[-1]

            target_anim_full_path = Sdf.Path(self._target_animation_parent_path + "/" + source_skel_anim_name)
            target_skel_anim = stage.GetPrimAtPath(target_anim_full_path)
            if target_skel_anim:
                carb.log_error("Target Animation \"{}\" exists! Aborting...".format(target_anim_full_path))
                continue

            skelCache = UsdSkel.Cache()
            animQuery = skelCache.GetAnimQuery(source_skel_anim)
            times = animQuery.GetJointTransformTimeSamples()
            # if joint_tokens don't match with skeleton joint tokesn,
            # we want to create mapping table
            anim_joint_tokens = convert_vtarray_to_list(animQuery.GetJointOrder())
            skel_joint_tokens = source_skeleton.GetJointsAttr().Get()
            # the order is all different
            # so I have to create mapping table
            # source skeleton to source animation buffer
            mapping_table = {}
            for i, token in enumerate(skel_joint_tokens):
                if token in anim_joint_tokens:
                    mapping_table[i] = anim_joint_tokens.index(token)

            target_skel_anim = UsdSkel.Animation(stage.DefinePrim(target_anim_full_path, "SkelAnimation"))
            target_skel_anim.GetJointsAttr().Set(target_skeleton.GetJointsAttr().Get())

            for time in times:
                # get source transform
                source_transforms = source_skel_anim.GetTransforms(time)

                target_translations, target_rotations = get_target_transforms(mapping_table, source_transforms)
                if len(target_translations) == 0:
                    carb.log_warn("Retarget has failed. Make sure retarget has been set up. ")
                    return

                # update target skeleton
                vt_transforms = convert_trans_rots_to_pxr_matrices(target_translations, target_rotations)

                # clear root - this has to happen after retarget if set_root_identity is set
                if self._set_root_identity:
                    vt_transforms[1] = vt_transforms[1] * vt_transforms[0]
                    vt_transforms[0] = Gf.Matrix4d(1.0)

                target_skel_anim.SetTransforms(Vt.Matrix4dArray(vt_transforms), time)

            carb.log_info("Animation \"{0}\" has been generated with time range of [{1},{2}]...".format(target_skel_anim, str(times[0]), str(times[-1])))

    def undo(self):
        if self._usd_undo is not None:
            self._usd_undo.undo()


omni.kit.commands.register_all_commands_in_module(__name__)
