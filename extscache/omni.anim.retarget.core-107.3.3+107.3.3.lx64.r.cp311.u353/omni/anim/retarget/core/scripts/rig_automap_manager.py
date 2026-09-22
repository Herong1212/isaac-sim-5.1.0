# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import json
import os

import carb
from .utils import get_joint_list, set_forward_axis, set_up_axis, uniform_absolute_path


class RigAutoMapJsonException(Exception):
    pass


class RigAutoMap:
    def __init__(self, automap_file_path):
        self._automap_file_path = automap_file_path
        self._json_data = None
        self._mappings = dict()
        try:
            with open(automap_file_path, mode="r") as json_file:
                self._json_data = json.load(json_file)
                json_file.close()
        except IOError:
            carb.log_error(f"Failed to access {automap_file_path}.")
            raise RigAutoMapJsonException()
        except ValueError:
            carb.log_error(f"Failed to open json file: {automap_file_path}.")
            raise RigAutoMapJsonException()

        mappings = self._json_data["mappings"]
        for mapping in mappings:
            tag = mapping[0]
            joint = mapping[1]
            if tag is not None and tag != "" and joint != "":
                self._mappings[tag] = joint
        if "up_axis" in self._json_data:
            self.up_axis = self.get_axis_name(self._json_data["up_axis"])
        else:
            self.up_axis = None

        if "forward_axis" in self._json_data:
            self.forward_axis = self.get_axis_name(self._json_data["forward_axis"])
        else:
            self.forward_axis = None

    def __del__(self):
        self.destroy()

    def destroy(self):
        del self._json_data
        self._mappings = None
        self._json_data = None

    def get_axis_name(self, axis):
        if axis in ["X", "x"]:
            return "X"
        if axis in ["Y", "y"]:
            return "Y"
        if axis in ["Z", "z"]:
            return "Z"
        if axis in ["-X", "-x", "MINUS X"]:
            return "MINUS X"
        if axis in ["-Y", "-y", "MINUS Y"]:
            return "MINUS Y"
        if axis in ["-Z", "-z", "MINUS Z"]:
            return "MINUS Z"

        return None

    @property
    def name(self):
        return self._json_data["name"]

    @property
    def mappings(self):
        return self._mappings

    def get_rig_match_score(self, rig):
        score = 0
        # get list of joint
        joints = get_joint_list(rig.skeleton)
        for rig_tag in rig.tag_names:
            if rig_tag in self._mappings and self._mappings[rig_tag] in joints:
                score += 1
        return score


class RigAutoMapManager:
    def __init__(self):
        self._automaps = []

    def __del__(self):
        for automap in self._automaps:
            del automap

        self._automaps = []

    def load_automaps(self, rig_path, reset_before_load):
        automap_dir_path = f"{rig_path}/automap"
        if reset_before_load:
            self._automaps = list()
        file_names = [f for f in os.listdir(automap_dir_path) if os.path.isfile(os.path.join(automap_dir_path, f))]
        for file_name in file_names:
            automap_file_path = uniform_absolute_path(f"{automap_dir_path}/{file_name}")
            self._automaps.append(RigAutoMap(automap_file_path))

class RetargetAutoMapManager(RigAutoMapManager):
    __instance = None

    def __init__(self):
        if RetargetAutoMapManager.__instance is not None:
            raise Exception("Use RetargetAutoMapManager.get_instance() instead")
        else:
            RetargetAutoMapManager.__instance = self

        super().__init__()

    def __del__(self):
        super().__del__()

    @staticmethod
    def get_instance():
        if RetargetAutoMapManager.__instance is None:
            RetargetAutoMapManager()
        return RetargetAutoMapManager.__instance

    @staticmethod
    def del_instance():
        del RetargetAutoMapManager.__instance
        RetargetAutoMapManager.__instance = None

    def apply_best_automap(self, rig):
        best_rig_match_score = 0
        best_automap = None
        success = False
        # search from back
        # if users add another auto map files later, we want that to be prioritized
        for i in range(len(self._automaps) - 1, -1, -1):
            automap = self._automaps[i]
            score = automap.get_rig_match_score(rig)
            if score > best_rig_match_score:
                best_automap = automap
                rig.automap = best_automap
                best_rig_match_score = score
        if best_rig_match_score > 0:
            rig.set_joint_mappings(best_automap.mappings)
            # only apply axis if the auto mapping works
            success = rig.does_match(best_rig_match_score)
            if success:
                if best_automap.up_axis is not None and best_automap.forward_axis is not None:
                    set_up_axis(rig.skeleton, best_automap.up_axis)
                    set_forward_axis(rig.skeleton, best_automap.forward_axis)
                    return best_rig_match_score, True, True

                # return False for auto map
                return best_rig_match_score, True, False

        return 0, False, False
