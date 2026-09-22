# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import os
import json
import carb
import omni.kit.commands
from .utils import get_joint_list, get_skeleton_tag_joint_dict, get_stage_id, uniform_absolute_path, convert_to_simple_joints, get_stage_id, convert_trans_rots_to_pxr_matrices, rest_pose_exist, set_forward_axis, set_up_axis, unload_retarget_pose
from typing import Dict, Optional, List
from .rig_automap_manager import RetargetAutoMapManager
import RetargetingSchema

ext_path = ""


AXIS_BLUE  = 0xFFFABD2D
AXIS_GREEN = 0xFF00B976
AXIS_RED   = 0xFFAA5555


class RigJsonException(Exception):
    pass

class TagData:
    def __init__(self, joint):
        self.joint = joint
        self.selected = False

class Rig:
    def __init__(self, rig_path):
        self._json_data = None
        self._path = rig_path
        self._tags: Dict[str, TagData] = {}
        rig_file_path = uniform_absolute_path(f"{rig_path}/rig.json")
        try:
            with open(rig_file_path, mode="r") as json_file:
                self._json_data = json.load(json_file)
        except IOError:
            carb.log_error(f"Failed to access {rig_file_path}.")
            raise RigJsonException()
        except ValueError:
            carb.log_error(f"Failed to open json file: {rig_file_path}.")
            raise RigJsonException()

        self._groups = dict()
        for tag in self._json_data["tags"]:
            group_name = tag.get("group", "Body")
            if group_name not in self._groups.keys():
                self._groups[group_name] = list()
            self._groups[group_name].append(tag)
        self._current_group = self._json_data["current_group"]
        self._secondary_groups = set(self._json_data.get("secondary_groups", []))
        self._match_score = self._json_data["match_score"]
        self._skeleton = None
        # declare broadcast for listeners
        self._tag_changed_callbacks = []
        self._joint_changed_callbacks = []
        self._tag_added_callbacks = []
        self._tag_removed_callbacks = []
        self._tags_cleared_callbacks = []
        self._tag_selected_callbacks = []
        self._skeleton_changed_callbacks = []
        self.clear()
        self.executing = False

    def __del__(self):
        self._tag_changed_callbacks = []
        self._joint_changed_callbacks = []
        self._tag_added_callbacks = []
        self._tag_removed_callbacks = []
        self._tags_cleared_callbacks = []
        self._tag_selected_callbacks = []
        self._skeleton_changed_callbacks = []

    @property
    def path(self):
        return self._path

    @property
    def name(self):
        return self._json_data["name"]

    @property
    def version(self):
        return self._json_data["version"]

    @property
    def read_only(self):
        return self._json_data["read_only"]

    @property
    def selection_size(self):
        return self._json_data["selection_size"]

    @property
    def pin_size(self):
        return self._json_data["pin_size"]

    @property
    def pin_color(self):
        return int(self._json_data["pin_color"], 16)

    @property
    def pin_background_color(self):
        return int(self._json_data["pin_background_color"], 16)

    @property
    def pin_invalid_color(self):
        return int(self._json_data["pin_invalid_color"], 16)

    @property
    def pin_selected_color(self):
        return int(self._json_data["pin_selected_color"], 16)

    @property
    def current_group(self):
        return self._current_group

    @current_group.setter
    def current_group(self, value):
        self._current_group = value

    @property
    def group_names(self):
        return list(self._groups.keys())

    @property
    def tag_names(self):
        return list(self._tags.keys())

    @property
    def keywords(self):
        tags = self._json_data["tags"]
        keymap = {}
        for tag in tags:
            # if it has keywords
            if "keywords" in tag.keys():
                keymap[tag["name"]] = tag["keywords"]

        return keymap

    @property
    def skeleton(self):
        return self._skeleton

    def get_reference_skeleton(self):
        if "reference_skeleton" in self._json_data.keys():
            reference_skeleton = self._json_data["reference_skeleton"]
            rig_folder_path = uniform_absolute_path(f"{self._path}/assets/{reference_skeleton}")
            return True, reference_skeleton, rig_folder_path

        return False, None, None

    def get_reference_animations(self):
        if "reference_animations" in self._json_data.keys():
            reference_animations = self._json_data["reference_animations"]
            out_animations = {}
            for anim in reference_animations:
                out_animations[anim] = uniform_absolute_path(f"{self._path}/assets/{anim}")
            return True, out_animations
        return False, None

    def does_match(self, score):
        return score >= self._match_score

    def get_unassigned_tags(self, group):
        unassigned_tags = []
        tags = self._json_data["tags"]
        used_tags = self._tags.keys()
        for tag in tags:
            if tag["group"] == group and tag["name"] not in used_tags:
                unassigned_tags.append(tag["name"])
        return unassigned_tags

    def get_selected(self, tag_name):
        if tag_name in self._tags:
            return self._tags[tag_name].selected

    # for now only allow single selection
    def clear_select(self):
        tag_name = ""
        # turn off all tags
        for tag in self._tags:
            if self._tags[tag].selected:
                self._tags[tag].selected = False
                tag_name = tag
                break

        if tag_name != "":
            for tag_selected in self._tag_selected_callbacks:
                tag_selected(tag_name, False)

    # for now only allow single selection
    def set_selected(self, tag_name, selected):
        # if we're to select something, clear selection first
        if selected:
            self.clear_select()

        # only trigger if modified
        if tag_name in self._tags and self._tags[tag_name].selected != selected:
            self._tags[tag_name].selected = selected

            for tag_selected in self._tag_selected_callbacks:
                tag_selected(tag_name, selected)

    def get_tags_by_group(self, group_name):
        names = [x["name"] for x in self._groups[group_name]]
        tags = [self._tags[x] for x in names]
        return tags

    def get_active_tags(self):
        result = []
        # check to be sure the group is correct before returning anything
        if self._current_group in self._groups:
            result += self._groups[self._current_group]
        for group in self._secondary_groups:
            result += self._groups.get(group, [])
        return result

    def run_change_callbacks(self):
        for skeleton_changed in self._skeleton_changed_callbacks:
            skeleton_changed(self._skeleton)

    def set_skeleton(self, skeleton):
        if self._skeleton != skeleton:
            self._skeleton = skeleton
            # clear current assigned tags
            self.clear()

            # assign new tags
            if skeleton:
                tag_joint_dict = self.get_tag_joint_mapping()
                for tag, joint in tag_joint_dict.items():
                    self.set_joint(tag, joint, False)

            self.run_change_callbacks()

    def get_skeleton(self):
        return self._skeleton

    def get_joint(self, tag_name):
        if tag_name in self._tags:
            return self._tags[tag_name].joint
        return ""

    def set_joint(self, tag_name, joint_name, savechange):
        #first clear any other tag that is using the same joint name
        for t in self._tags:
            if t != tag_name and self._tags[t].joint == joint_name:
                self._tags[t].joint = ""

        new_item = (tag_name not in self._tags)
        if new_item:
            self._tags[tag_name] = TagData(joint_name)
        elif self._tags[tag_name] != joint_name:
            self._tags[tag_name].joint = joint_name
        else:
            return

        if savechange:
            self.update_skeleton_tags()
            if new_item:
                for tag_added in self._tag_added_callbacks:
                    tag_added(tag_name)
            else:
                for joint_changed in self._joint_changed_callbacks:
                    joint_changed(tag_name, joint_name)

    def set_joint_mappings(self, mappings: dict):
        if self.skeleton:
            joints = get_joint_list(self.skeleton)
            for tag in mappings:
                #if joint exists, then add
                if mappings[tag] in joints:
                    self.set_joint(tag, mappings[tag], False)

        self.update_skeleton_tags()

    def is_tag_mapped(self, tag_name):
        joint = self.get_joint(tag_name)
        return joint != ""

    def is_default_tag_mapped(self):
        default_tags = self.get_default_tags()

        for tag in default_tags:
            if not self.is_tag_mapped(tag):
                return False
        return True

    def is_default_tag(self, tag_name):
        tags = self._json_data["tags"]
        for i in range(len(tags)):
            tag = tags[i]
            optional = False
            if tag["name"] == tag_name:
                if "optional" in tag:
                    optional = tag["optional"]
                if not optional:
                    return True
                break
        return False

    def get_default_tags(self):
        default_tags = []
        tags = self._json_data["tags"]
        for i in range(len(tags)):
            tag = tags[i]
            optional = False
            if "optional" in tag:
                optional = tag["optional"]
            if not optional:
                default_tags.append(tag["name"])
        return default_tags

    def clear(self):
        self.clear_select()
        self._tags.clear()
        # add necessary data
        for tag in self._json_data["tags"]:
            self._tags[tag["name"]] = TagData("")

        for tags_cleared in self._tags_cleared_callbacks:
            tags_cleared()

    def update_skeleton_tags(self):
        pass

    def reset_tags(self):
        pass

    def remove_tag(self, tag_name):
        if (tag_name in self._tags):
            self._tags.pop(tag_name)

            for tag_removed in self._tag_removed_callbacks:
                tag_removed(tag_name)

            self.update_skeleton_tags()

    def rename_tag(self, old_tag_name, new_tag_name):
        if (new_tag_name in self._tags):
            return
        if (old_tag_name not in self._tags):
            return

        self._tags[new_tag_name] = self._tags[old_tag_name]
        self._tags.pop(old_tag_name)

        for tag_changed in self._tag_changed_callbacks:
            tag_changed(old_tag_name, new_tag_name)

        self.update_skeleton_tags()

    def get_tags(self):
        # makes it easier to iterate dict
        return self._tags

    def refresh_tags(self):
        if self._skeleton:
            # clear current assigned tags
            self.clear()
            # assign new tags
            tag_joint_dict = self.get_tag_joint_mapping()
            for tag, joint in tag_joint_dict.items():
                self.set_joint(tag, joint, False)

    def valid_default_tag_setup(self):
        return self.is_default_tag_mapped()

    def should_run_auto_setup(self, min_count=1):
        # Bugfix: If a retarget attribute exist, return false
        #         This fixes the overwriting of the retarget pose
        #         on NV Human generated assets.
        skel_prim = self._skeleton.GetPrim()
        if skel_prim.HasAttribute("controlRig:retargetTransforms"):
            retarget_attr = skel_prim.GetAttribute("controlRig:retargetTransforms")
            if not bool(retarget_attr):
                return False

            values = retarget_attr.Get() or []
            if not len(values):
                return False

        tags = self.get_tags()

        mapped = 0
        for tag in tags:
            if self.is_tag_mapped(tag):
                mapped += 1
                if mapped >= min_count:
                    return False

        return True

    def get_tag_joint_mapping(self):
        pass

    def auto_setup(self, use_mapping=True, auto_facing=True, auto_tagging=True, auto_posing=True):
        pass

    def register_tag_changed(self, callback):
        if (callback not in self._tag_changed_callbacks):
            self._tag_changed_callbacks.append(callback)

    def unregister_tag_changed(self, callback):
        if (callback in self._tag_changed_callbacks):
            self._tag_changed_callbacks.remove(callback)

    def register_joint_changed(self, callback):
        if (callback not in self._joint_changed_callbacks):
            self._joint_changed_callbacks.append(callback)

    def unregister_joint_changed(self, callback):
        if (callback in self._joint_changed_callbacks):
            self._joint_changed_callbacks.remove(callback)

    def register_tag_added(self, callback):
        if (callback not in self._tag_added_callbacks):
            self._tag_added_callbacks.append(callback)

    def unregister_tag_added(self, callback):
        if (callback in self._tag_added_callbacks):
            self._tag_added_callbacks.remove(callback)

    def register_tag_removed(self, callback):
        if (callback not in self._tag_removed_callbacks):
            self._tag_removed_callbacks.append(callback)

    def unregister_tag_removed(self, callback):
        if (callback in self._tag_removed_callbacks):
            self._tag_removed_callbacks.remove(callback)

    def register_tags_cleared(self, callback):
        if (callback not in self._tags_cleared_callbacks):
            self._tags_cleared_callbacks.append(callback)

    def unregister_tags_cleared(self, callback):
        if (callback in self._tags_cleared_callbacks):
            self._tags_cleared_callbacks.remove(callback)

    def register_tag_selected(self, callback):
        if (callback not in self._tag_selected_callbacks):
            self._tag_selected_callbacks.append(callback)

    def unregister_tag_selected(self, callback):
        if (callback in self._tag_selected_callbacks):
            self._tag_selected_callbacks.remove(callback)

    def register_skeleton_changed(self, callback):
        if (callback not in self._skeleton_changed_callbacks):
            self._skeleton_changed_callbacks.append(callback)

    def unregister_skeleton_changed(self, callback):
        if (callback in self._skeleton_changed_callbacks):
            self._skeleton_changed_callbacks.remove(callback)

    def enable_secondary_group(self, group:str):
        if not group in self._secondary_groups:
            self._secondary_groups.add(group)
            self.run_change_callbacks()

    def is_group_enabled(self, group:str) -> bool:
        return (self._current_group == group) or (group in self._secondary_groups)

    def disable_secondary_group(self, group:str):
        if group in self._secondary_groups:
            self._secondary_groups.remove(group)
            self.run_change_callbacks()

    def get_active_groups(self) -> List[str]:
        result = []
        if self._current_group:
            result.append(self._current_group)
        result += self._secondary_groups
        return result

#TODO: should we support stage here?


class RetargetRig(Rig):
    def __init__(self, rig_name):
        self._rig_name = rig_name
        rig_path = RetargetRig.get_system_rig_folder(rig_name)
        self.automap = None
        super().__init__(rig_path)

    def __del__(self):
        super().__del__()

    def reset_tags(self):
        """ when tag set up has been modified update skeleton """
        self.automap = None
        if self._skeleton:
            self.executing = True
            stage_id = get_stage_id(self._skeleton.GetPrim().GetStage())
            omni.kit.commands.execute(
                "ClearRetargetTagsCommand",
                stage_id = stage_id,
                skel_paths=[self._skeleton.GetPrim().GetPath()]
            )
            self.executing = False

    def update_skeleton_tags(self):
        """ when tag set up has been modified update skeleton """
        if self._skeleton:
            self.executing = True

            tag_joint_dict : Dict[str, str] = {}

            for tag in self._tags:
                tag_joint_dict[tag] = self._tags[tag].joint

            stage_id = get_stage_id(self._skeleton.GetPrim().GetStage())
            omni.kit.commands.execute(
                "SetSkeletonJointTagPairCommand",
                stage_id = stage_id,
                skel_paths=[self._skeleton.GetPrim().GetPath()],
                tag_joint_dict=tag_joint_dict
            )
            self.executing = False

    def save_retarget_pose(self):
        if self._skeleton:
            self.executing = True
            stage_id = get_stage_id(self._skeleton.GetPrim().GetStage())
            omni.kit.commands.execute(
                "SaveRetargetPoseCommand",
                stage_id = stage_id,
                skel_paths=[self._skeleton.GetPrim().GetPath()]
            )
            self.executing = False

    def load_retarget_pose(self):
        if self._skeleton:
            self.executing = True
            stage_id = get_stage_id(self._skeleton.GetPrim().GetStage())
            omni.kit.commands.execute(
                "LoadRetargetPoseCommand",
                stage_id = stage_id,
                skel_paths=[self._skeleton.GetPrim().GetPath()]
            )
            self.executing = False

    def unload_retarget_pose(self):
        if self._skeleton:
            self.executing = True
            unload_retarget_pose(self._skeleton.GetPrim().GetPath().pathString)
            self.executing = False


    def reset_retarget_pose(self):
        if self._skeleton:
            self.executing = True
            stage_id = get_stage_id(self._skeleton.GetPrim().GetStage())
            omni.kit.commands.execute(
                "ResetRetargetPoseCommand",
                stage_id = stage_id,
                skel_paths=[self._skeleton.GetPrim().GetPath()]
            )
            self.executing = False

    def set_up_axis(self, up_axis):
        if self._skeleton:
            self.executing = True
            stage_id = get_stage_id(self._skeleton.GetPrim().GetStage())
            omni.kit.commands.execute(
                "SetSkeletonUpForwardAxis",
                stage_id = stage_id,
                skel_paths=[self._skeleton.GetPrim().GetPath()],
                is_up_axis=True,
                axis=up_axis
            )
            self.executing = False

    def set_forward_axis(self, forward_axis):
        if self._skeleton:
            self.executing = True
            stage_id = get_stage_id(self._skeleton.GetPrim().GetStage())
            omni.kit.commands.execute(
                "SetSkeletonUpForwardAxis",
                stage_id = stage_id,
                skel_paths=[self._skeleton.GetPrim().GetPath()],
                is_up_axis=False,
                axis=forward_axis
            )
            self.executing = False

    def get_tag_joint_mapping(self):
        tag_joint_dict: Dict[str, str] = {}
        if self._skeleton:
            skel_prim = self._skeleton.GetPrim()
            tags = []

            if skel_prim.HasAPI(RetargetingSchema.ControlRigAPI):
                control_rig_api = RetargetingSchema.ControlRigAPI(skel_prim)
                retarget_attr = control_rig_api.GetRetargetTagsAttr()
                if retarget_attr:
                    tags = retarget_attr.Get()
                    if tags and len(tags) > 0:
                        joint_attr = self._skeleton.GetJointsAttr()
                        if joint_attr:
                            joints = convert_to_simple_joints(joint_attr.Get())
                            for i, joint in enumerate(joints):
                                if tags[i] != "":
                                    tag_joint_dict[tags[i]] = joint
        return tag_joint_dict

    def auto_setup(self, use_mapping=True, auto_facing=True, auto_tagging=True, auto_posing=True):
        # we don't care about the name of the file
        success, _, template_file = self.get_reference_skeleton()
        if not success:
            carb.log_error("Reference Template File is Missing.")
            return False

        skeleton = self._skeleton
        skel_prim = skeleton.GetPrim()
        stage_id = get_stage_id(skel_prim.GetStage())

        do_auto_facing = auto_facing
        do_auto_tagging = auto_tagging
        do_auto_posing = auto_posing

        # now create retarget controller
        retarget_controller = omni.anim.retarget.core.RetargetController(str(template_file), None, stage_id, str(skel_prim.GetPath()))
        if retarget_controller:
            if use_mapping:
                _, success, facing_setup = RetargetAutoMapManager.get_instance().apply_best_automap(self)
                # if we succeed, turn off auto face/auto tag
                if success:
                    if facing_setup:
                        do_auto_facing = False
                        do_auto_tagging = False
                    else:
                        # we have tagging, but not facing
                        do_auto_tagging = False

            keywords = self.keywords

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

                    return "X"

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
                self.set_joint_mappings(tag_mapping)

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

    @property
    def rig_name(self) -> str:
        return self._rig_name

    @staticmethod
    def get_system_rig_folder(rig_name: Optional[str] = ""):
        folder_path = "data/rigs/"
        if rig_name:
            folder_path += rig_name + "/"
        global ext_path
        if ext_path == "":
            carb.log_error("extension path is not set yet. Ensure that's set by extension startup.")
            return

        rig_path = os.path.join(ext_path, folder_path)
        return rig_path

    @staticmethod
    def set_extension_path(extension_path: str):
        global ext_path
        ext_path = extension_path
