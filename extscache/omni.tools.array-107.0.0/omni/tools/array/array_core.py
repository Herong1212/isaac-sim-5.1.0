# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import random
from dataclasses import dataclass
from enum import Enum

import carb
import numpy as np
import omni.kit
import omni.usd
from omni.usd.commands import (
    CopyPrimCommand,
    CreateInstanceCommand,
    DeletePrimsCommand,
    GroupPrimsCommand,
    TransformPrimSRTCommand,
)
from pxr import Gf, Sdf, Usd, UsdGeom

from . import array_const
from .array_params import ArrayParams


@dataclass
class CountChanges:
    has_changed = False
    diff_one_d = 0
    diff_two_d = 0
    diff_three_d = 0


@dataclass
class TransformChanges:
    one_d_changed = False
    two_d_changed = False
    three_d_changed = False
    diff_inc_translate = Gf.Vec3d(0)
    diff_inc_rotate = Gf.Vec3d(0)
    diff_inc_scale = Gf.Vec3d(0)
    diff_pivot = Gf.Vec3d(0)
    diff_offset_two_d = Gf.Vec3d(0)
    diff_offset_three_d = Gf.Vec3d(0)


@dataclass
class CreatedPrim:
    path = ""
    prim = None
    source_prim = None
    is_original_prim = False

    def set_values(self, path, prim, source_prim, is_original_prim):
        self.path = path
        self.prim = prim
        self.source_prim = source_prim
        self.is_original_prim = is_original_prim


class MatchResults(Enum):
    EXACT_MATCH = 1
    ORDER_MISMATCH = 2
    MISMATCH = 3


class Dimension(Enum):
    ONE = 1
    TWO = 2
    THREE = 3


# Core array class
class ArrayCore:
    _array_core_instance = None

    def __init__(self):
        super().__init__()
        # Array core variables
        self._ignore_preview = False
        self._target_prims = []
        self._valid_prims = []
        self._valid_prim_transforms = {}
        self._one_d_result_prims = []
        self._two_d_result_prims = []
        self._three_d_result_prims = []
        self._array_params = ArrayParams()
        self._array_values = self._array_params.get_defaults()
        self._prev_array_values = self._array_values.copy()

        ArrayCore._array_core_instance = self

        self._refresh()

    @staticmethod
    def get_instance():
        if ArrayCore._array_core_instance is None:
            ArrayCore._array_core_instance = ArrayCore()
        return ArrayCore._array_core_instance

    def clean(self):
        self._clear_resulting_prims()

    # Update only a single array value
    def update_value(self, value_name: str, new_value):
        if self._check_value_exists(value_name):
            self._array_values[value_name] = new_value
            self._check_value_changed()

    # Update all array values at once
    def update_all_values(self, new_values: dict):
        self._array_values = new_values.copy()
        self._check_value_changed()

    # Update only the target prims. Expecting a list of prims, not prim paths
    def update_target_prims(self, target_prims: list):
        # Check to see if the target prims changed
        match_results = self._check_prims_match(self._target_prims, target_prims)
        # If no change, check for transformation changes...
        if match_results == MatchResults.EXACT_MATCH:
            # Check to see if transforms changed
            changes = self._check_selected_prim_transforms_changed(self._target_prims, target_prims)
            self._update_valid_prim_transforms()
            if changes["Changed"]:
                self._update_selected_transformations(changes)
        # If there was a change in the target prims, rebuild
        elif match_results == MatchResults.ORDER_MISMATCH or match_results == MatchResults.MISMATCH:
            # Update target prims, valid prims, store current valid prim transforms, and rebuild
            self._target_prims = target_prims.copy()
            self._valid_prims = self._get_valid_target_prims(self._target_prims, True)
            self._update_valid_prim_transforms()
            self._rebuild()

    # Called by the CreateArrayCommand - creates and applies in one go based on the values supplied
    # Expecting a list of prims, not prim paths
    def create_array(self, target_prims: list, array_values: dict):
        self._target_prims = target_prims.copy()
        self._valid_prims = self._get_valid_target_prims(self._target_prims, True)
        self._update_valid_prim_transforms()
        self._array_values = array_values.copy()
        self._rebuild()
        return self.apply_array()  # Returns a tuple of applied prim paths, grouped path, and selected prim paths

    # ================== START - COPY, TRANSFORM, INTERACTIONS, DELETE =======================

    # Called by all methods to create/copy a prim
    # Returns the result
    def _copy_prim(self, source_path: str, source_prim: Usd.Prim, is_original_prim: bool):
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()

        # COPY/INSTANCE
        if self._array_values[array_const.CREATE_TYPE] == array_const.CreateType.COPIES:
            cmd = CopyPrimSelectCommand(path_from=str(source_path), path_to=str(source_path))
            copied_prim = cmd.do()
        elif self._array_values[array_const.CREATE_TYPE] == array_const.CreateType.INSTANCES:
            cmd = CreateInstanceSelectCommand(path_from=str(source_path))
            copied_prim = cmd.do()
        copied_prim_path = copied_prim
        created_prim = CreatedPrim()
        created_prim.set_values(copied_prim_path, stage.GetPrimAtPath(copied_prim_path), source_prim, is_original_prim)

        return created_prim

    # Called by all methods to apply transformations
    # More prims to move = slower performance due to the transform command - will be faster later with API update
    def _transform_prim(
        self,
        path: str,
        prim: Usd.Prim,
        action_index: int,
        trans_dif: Gf.Vec3d() = Gf.Vec3d(0),
        rot_dif: Gf.Vec3d() = Gf.Vec3d(0),
        scale_dif: Gf.Vec3d() = Gf.Vec3d(0),
    ):
        trans_op = self._check_attribute_exists(prim, "Translate")
        rot_op = self._check_attribute_exists(prim, "Rotate")
        scale_op = self._check_attribute_exists(prim, "Scale")

        cur_pos = trans_op[1]
        cur_rot = rot_op[1]
        cur_scale = scale_op[1]
        new_pos = cur_pos + trans_dif * action_index
        new_rot = cur_rot + rot_dif * action_index
        new_scale = cur_scale + scale_dif * action_index
        cmd = TransformPrimSRTCommand(
            path=path, new_translation=new_pos, new_rotation_euler=new_rot, new_scale=new_scale
        )
        cmd.do()

    # Called by all methods to apply "follow rotation" transformations
    # More prims to move = slower performance due to the transform command - will be faster later with API update
    def _transform_prim_reorient(
        self,
        path: str,
        prim: Usd.Prim,
        source_prim: Usd.Prim,
        action_index: int,
        trans_dif: Gf.Vec3d() = Gf.Vec3d(0),
        rot_dif: Gf.Vec3d() = Gf.Vec3d(0),
        scale_dif: Gf.Vec3d() = Gf.Vec3d(0),
        selection: bool = False,
    ):
        if selection:
            self._transform_prim(path, prim, action_index, trans_dif, rot_dif, scale_dif)
            return

        def rot_from_euler(angles: Gf.Vec3d, order: Gf.Vec3i):
            sin = np.sin(np.radians(angles))
            cos = np.cos(np.radians(angles))

            R = [
                Gf.Matrix3d(1, 0, 0, 0, cos[0], sin[0], 0, -sin[0], cos[0]),
                Gf.Matrix3d(cos[1], 0, -sin[1], 0, 1, 0, sin[1], 0, cos[1]),
                Gf.Matrix3d(cos[2], sin[2], 0, -sin[2], cos[2], 0, 0, 0, 1),
            ]

            rot = Gf.Matrix3d(R[order[0]] * R[order[1]] * R[order[2]]).ExtractRotation()
            return rot

        source_prim_pos = self._check_attribute_exists(source_prim, "Translate")[1]
        order = self._get_valid_rotation_attribute(prim)[2]  # Get the correct rotation order
        rot = rot_from_euler(rot_dif, order) * action_index
        trans = trans_dif * action_index
        new_pos = (rot.TransformDir(trans)) + source_prim_pos

        source_prim_rot = self._check_attribute_exists(source_prim, "Rotate")[1]
        new_rot = source_prim_rot + rot_dif * action_index

        source_prim_scale = self._check_attribute_exists(source_prim, "Scale")[1]
        new_scale = source_prim_scale + scale_dif * action_index

        cmd = TransformPrimSRTCommand(
            path=path, new_translation=new_pos, new_rotation_euler=new_rot, new_scale=new_scale
        )
        cmd.do()

    # Called by all methods to manage the interactability of a prim, and if it appears in the stage window
    def _update_prim_interactions(self, prim_to_update: CreatedPrim, is_interactable: bool):
        usd_context = omni.usd.get_context()
        usd_context.set_pickable(prim_to_update.path, is_interactable)
        omni.usd.editor.set_hide_in_stage_window(prim_to_update.prim, not is_interactable)

    # Called by all methods to delete prims
    def delete_prims(self, prim_paths_to_delete: list):
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        valid_prim_paths = [prim_path for prim_path in prim_paths_to_delete if stage.GetPrimAtPath(prim_path).IsValid()]
        if len(valid_prim_paths) > 0:
            cmd = DeletePrimsCommand(paths=valid_prim_paths)
            cmd.do()

    # ================== END - COPY, TRANSFORM, INTERACTIONS, DELETE =======================

    # Stores the current transforms of valid selected prims
    def _update_valid_prim_transforms(self):
        self._valid_prim_transforms.clear()
        if self._valid_prims:
            for prim in self._valid_prims:
                self._valid_prim_transforms[prim] = {
                    "Translate": self._check_attribute_exists(prim, "Translate"),
                    "Rotate": self._check_attribute_exists(prim, "Rotate"),
                    "Scale": self._check_attribute_exists(prim, "Scale"),
                    "Pivot": self._check_attribute_exists(prim, "Pivot"),
                }

    # Checks if two lists of prims are the same, returns how they differ
    def _check_prims_match(self, primsA: list, primsB: list):
        if primsA == primsB:
            return MatchResults.EXACT_MATCH
        else:
            if len(primsA) == len(primsB):
                matches = 0
                for p in primsA:
                    if p in primsB:
                        matches += 1
                if matches == len(primsA):
                    return MatchResults.ORDER_MISMATCH

        return MatchResults.MISMATCH

    # Checks for transform changes on selected prims, returns changes if any
    def _check_selected_prim_transforms_changed(self, original_prims: list, changed_prims: list):
        changes = {}
        changes["Changed"] = False
        # Only continue if there are saved prim transforms
        if self._valid_prim_transforms:
            # Only check the first changed prim
            # In Omniverse if you have one or multiple objects selected, the first will always move
            for prim in changed_prims:
                transform_changes = TransformChanges()

                diffs = []

                trans_op = self._check_attribute_exists(prim, "Translate")
                rot_op = self._check_attribute_exists(prim, "Rotate")
                scale_op = self._check_attribute_exists(prim, "Scale")
                pivot_op = self._check_attribute_exists(prim, "Pivot")
                diff_trans = Gf.Vec3d(0)
                diff_rot = Gf.Vec3d(0)
                diff_scale = Gf.Vec3d(0)
                diff_pivot = Gf.Vec3d(0)

                if trans_op[0]:
                    curr_trans = trans_op[1]
                    diff_trans = curr_trans - self._valid_prim_transforms[prim]["Translate"][1]
                    diffs.append(diff_trans)
                if rot_op[0]:
                    curr_rot = rot_op[1]
                    diff_rot = curr_rot - self._valid_prim_transforms[prim]["Rotate"][1]
                    diffs.append(diff_rot)
                if scale_op[0]:
                    curr_scale = scale_op[1]
                    diff_scale = curr_scale - self._valid_prim_transforms[prim]["Scale"][1]
                    diffs.append(diff_scale)
                if pivot_op[0]:
                    curr_pivot = pivot_op[1]
                    diff_pivot = curr_pivot - self._valid_prim_transforms[prim]["Pivot"][1]
                    diffs.append(diff_pivot)

                for diff in diffs:
                    if diff != Gf.Vec3d(0):
                        changes["Changed"] = True
                        break

                transform_changes.diff_inc_translate = diff_trans
                transform_changes.diff_inc_rotate = diff_rot
                transform_changes.diff_inc_scale = diff_scale
                transform_changes.diff_pivot = diff_pivot
                changes[prim] = transform_changes

        return changes

    # Checks for changes between two dictionaries
    # Returns a dictionary of a dictionary of changes
    def _check_dict_changes(self, dictA: dict, dictB: dict):
        changes = {}
        for key, value in dictA.items():
            if dictB[key] != value:
                changes[key] = {"New Value": value, "Old Value": dictB[key]}
        return changes

    # Determine which value changed and make the appropriate change
    def _check_value_changed(self):
        # Store the changes between previous and current array values
        changed_values = self._check_dict_changes(self._array_values, self._prev_array_values)
        # Update previous to match
        self._prev_array_values = self._array_values.copy()
        need_count_update = False
        need_transform_update = False
        if changed_values:
            # If any of the following change, rebuild and ignore any other changes (rebuild takes care of them)
            if (
                array_const.PREVIEW in changed_values
                or array_const.REORIENT_ROTATION in changed_values
                or array_const.CREATE_TYPE in changed_values
                or array_const.RANDOM_ORDER_SEED in changed_values
            ):
                self._rebuild()
                return

            # If the user changes the array type (group, ordered, random)...
            # If they have more than one valid selection, rebuild
            if array_const.ARRAY_TYPE in changed_values:
                if len(self._valid_prims) > 1:
                    self._rebuild()
                    return

            # COUNTS
            count_changes = CountChanges()
            if array_const.COUNT in changed_values:
                count_changes.diff_one_d = (
                    changed_values[array_const.COUNT]["New Value"] - changed_values[array_const.COUNT]["Old Value"]
                )
                need_count_update = True
            if array_const.TWO_D_COUNT in changed_values:
                count_changes.diff_two_d = (
                    changed_values[array_const.TWO_D_COUNT]["New Value"]
                    - changed_values[array_const.TWO_D_COUNT]["Old Value"]
                )
                need_count_update = True
            if array_const.THREE_D_COUNT in changed_values:
                count_changes.diff_three_d = (
                    changed_values[array_const.THREE_D_COUNT]["New Value"]
                    - changed_values[array_const.THREE_D_COUNT]["Old Value"]
                )
                need_count_update = True

            # TRANSFORMS
            transform_changes = TransformChanges()
            if array_const.INC_TRANSLATE in changed_values:
                transform_changes.diff_inc_translate = (
                    changed_values[array_const.INC_TRANSLATE]["New Value"]
                    - changed_values[array_const.INC_TRANSLATE]["Old Value"]
                )
                need_transform_update = True
                transform_changes.one_d_changed = True
            if array_const.INC_ROTATE in changed_values:
                transform_changes.diff_inc_rotate = (
                    changed_values[array_const.INC_ROTATE]["New Value"]
                    - changed_values[array_const.INC_ROTATE]["Old Value"]
                )
                need_transform_update = True
                transform_changes.one_d_changed = True
            if array_const.INC_SCALE in changed_values:
                transform_changes.diff_inc_scale = (
                    changed_values[array_const.INC_SCALE]["New Value"]
                    - changed_values[array_const.INC_SCALE]["Old Value"]
                )
                need_transform_update = True
                transform_changes.one_d_changed = True
            if array_const.TWO_D_OFFSET in changed_values:
                transform_changes.diff_offset_two_d = (
                    changed_values[array_const.TWO_D_OFFSET]["New Value"]
                    - changed_values[array_const.TWO_D_OFFSET]["Old Value"]
                )
                need_transform_update = True
                transform_changes.two_d_changed = True
            if array_const.THREE_D_OFFSET in changed_values:
                transform_changes.diff_offset_three_d = (
                    changed_values[array_const.THREE_D_OFFSET]["New Value"]
                    - changed_values[array_const.THREE_D_OFFSET]["Old Value"]
                )
                need_transform_update = True
                transform_changes.three_d_changed = True

            if need_count_update:
                self._update_counts(count_changes)
            elif need_transform_update:
                self._update_value_transformations(transform_changes)
            else:
                # Nothing changed that requires a rebuild or update
                pass
        else:
            # Nothing changed
            pass

    # Call when any of the counts are changed
    # Adds/Removes appropriately
    def _update_counts(self, count_changes: CountChanges):
        # No selection or preview is off - kick out
        if self._check_preview_off_or_no_valid_prims():
            return

        old_one_d_count = self._array_values[array_const.COUNT] - count_changes.diff_one_d
        old_two_d_count = self._array_values[array_const.TWO_D_COUNT] - count_changes.diff_two_d
        old_three_d_count = self._array_values[array_const.THREE_D_COUNT] - count_changes.diff_three_d

        # 1D changed, update 2D and 3D
        if count_changes.diff_one_d > 0:
            self._create_1d(count_changes.diff_one_d, self._one_d_result_prims, False, old_one_d_count, old_one_d_count)
            if self._array_values[array_const.TWO_D_COUNT] > 1:
                self._update_2d(count_changes.diff_one_d)
                if self._array_values[array_const.THREE_D_COUNT] > 1:
                    self._update_3d(count_changes.diff_one_d, Dimension.ONE)
            return
        # 2D changed, update 3D
        if count_changes.diff_two_d > 0:
            self._create_2d(
                count_changes.diff_two_d, self._two_d_result_prims, self._one_d_result_prims, True, old_two_d_count
            )
            if self._array_values[array_const.THREE_D_COUNT] > 1:
                self._update_3d(count_changes.diff_two_d, Dimension.TWO)
            return
        # 3D changed
        if count_changes.diff_three_d > 0:
            self._create_3d(
                count_changes.diff_three_d,
                self._three_d_result_prims,
                self._two_d_result_prims,
                True,
                old_three_d_count,
            )
        else:
            prim_paths_to_delete = []
            if count_changes.diff_one_d < 0:
                # 1D
                prim_paths_to_delete.extend(self._get_remove_1d(count_changes))
                if self._array_values[array_const.TWO_D_COUNT] > 1:
                    # 2D
                    prim_paths_to_delete.extend(self._get_remove_2d(count_changes))
                    if self._array_values[array_const.THREE_D_COUNT] > 1:
                        # 3D
                        prim_paths_to_delete.extend(self._get_remove_3d(count_changes))
                self.delete_prims(prim_paths_to_delete)
                return
            if count_changes.diff_two_d < 0:
                # 2D
                prim_paths_to_delete.extend(self._get_remove_2d(count_changes))
                if self._array_values[array_const.THREE_D_COUNT] > 1:
                    # 3D
                    prim_paths_to_delete.extend(self._get_remove_3d(count_changes))
                self.delete_prims(prim_paths_to_delete)
                return
            if count_changes.diff_three_d < 0:
                # 3D
                prim_paths_to_delete.extend(self._get_remove_3d(count_changes))
                self.delete_prims(prim_paths_to_delete)

    # Returns 1D prims to remove
    def _get_remove_1d(self, count_changes: CountChanges):
        prims_to_remove = []
        for i in range(int(Gf.Abs(count_changes.diff_one_d))):
            end_of_list = self._one_d_result_prims[-1].copy()
            prims_to_remove.append(end_of_list)
            self._one_d_result_prims.pop()

        prim_paths_to_remove = []
        for prim_list in prims_to_remove:
            for created_prim in prim_list:
                prim_paths_to_remove.append(created_prim.path)

        return prim_paths_to_remove

    # Returns 2D prims to remove
    def _get_remove_2d(self, count_changes: CountChanges):
        num_entry_to_remove = int(Gf.Abs(count_changes.diff_one_d))
        num_list_to_remove = int(Gf.Abs(count_changes.diff_two_d))

        prim_paths_to_remove = []

        # Remove end lists (2D count change)
        if num_list_to_remove > 0:
            for i in range(num_list_to_remove):
                removed = self._two_d_result_prims.pop()
                for entry in removed:
                    for cp in entry:
                        prim_paths_to_remove.append(cp.path)

        # Remove list end entries (1D count change)
        if num_entry_to_remove > 0:
            for index, list in enumerate(self._two_d_result_prims):
                if index == 0:
                    continue
                for i in range(num_entry_to_remove):
                    removed = list.pop()
                    for cp in removed:
                        prim_paths_to_remove.append(cp.path)

        return prim_paths_to_remove

    # Returns 3D prims to remove
    def _get_remove_3d(self, count_changes: CountChanges):
        num_entry_to_remove = int(Gf.Abs(count_changes.diff_one_d))
        num_list_to_remove = int(Gf.Abs(count_changes.diff_two_d))
        num_list_of_lists_to_remove = int(Gf.Abs(count_changes.diff_three_d))

        prim_paths_to_remove = []

        # Remove lists of lists(3D count change)
        if num_list_of_lists_to_remove > 0:
            for i in range(num_list_of_lists_to_remove):
                removed = self._three_d_result_prims.pop()
                for list in removed:
                    for entry in list:
                        for cp in entry:
                            prim_paths_to_remove.append(cp.path)

        # Remove lists (2D count change)
        if num_list_to_remove > 0:
            for index, list_of_lists in enumerate(self._three_d_result_prims):
                if index == 0:
                    continue
                for i in range(num_list_to_remove):
                    removed = list_of_lists.pop()
                    for entry in removed:
                        for cp in entry:
                            prim_paths_to_remove.append(cp.path)

        # Remove list end entries (1D count change)
        if num_entry_to_remove > 0:
            for index, list_of_lists in enumerate(self._three_d_result_prims):
                if index == 0:
                    continue
                for list in list_of_lists:
                    for i in range(num_entry_to_remove):
                        removed = list.pop()
                        for cp in removed:
                            prim_paths_to_remove.append(cp.path)

        return prim_paths_to_remove

    def _update_value_transformations(self, transform_changes: TransformChanges, reset: bool = False):
        # No selection or preview is off - kick out
        if self._check_preview_off_or_no_valid_prims():
            return

        inc_trans = self._array_values[array_const.INC_TRANSLATE]
        inc_rot = self._array_values[array_const.INC_ROTATE]
        inc_scale = self._array_values[array_const.INC_SCALE]
        two_d_offset = self._array_values[array_const.TWO_D_OFFSET]
        three_d_offset = self._array_values[array_const.THREE_D_OFFSET]

        # Reset all prim transforms before continuing
        if reset:
            self._reset_prim_transforms_to_source()

        # Here we are working backwards - if the 3D list exists, all other lists exist inside, so we can do everything in one go
        # 3D
        if self._three_d_result_prims:
            for list_of_lists_index, index_list_of_lists in enumerate(self._three_d_result_prims):
                for list_index, list in enumerate(index_list_of_lists):
                    for entry_index, entry in enumerate(list):
                        for created_prim in entry:
                            path = created_prim.path
                            prim = created_prim.prim
                            source_prim = created_prim.source_prim
                            is_original_prim = created_prim.is_original_prim

                            if not is_original_prim:
                                # If one D changed...
                                if transform_changes.one_d_changed:
                                    # If follow rotations...
                                    if self._get_reorient_mode_on():
                                        # If 1D (list 0, 0 in 3D list) - do reorient
                                        if list_of_lists_index == 0:
                                            if list_index == 0:
                                                action_index = entry_index
                                                source_transform_prim = self._get_source_transform_prim(source_prim)
                                                self._transform_prim_reorient(
                                                    path,
                                                    prim,
                                                    source_transform_prim,
                                                    action_index,
                                                    inc_trans,
                                                    inc_rot,
                                                    inc_scale,
                                                )
                                            # If list 0, index 1+ (2D entries), reposition 2D
                                            else:
                                                action_index = list_index
                                                source_transform_prim = source_prim
                                                self._transform_prim(
                                                    path, source_transform_prim, action_index, two_d_offset
                                                )
                                        # Otherwise reposition 3D
                                        else:
                                            action_index = list_of_lists_index
                                            source_transform_prim = source_prim
                                            self._transform_prim(
                                                path, source_transform_prim, action_index, three_d_offset
                                            )
                                    # Modify based on one d changes + any diff offset for two D and three D
                                    else:
                                        # If resetting, essentially do the same logic as follow rotation.
                                        if reset:
                                            if list_of_lists_index == 0:
                                                if list_index == 0:
                                                    action_index = entry_index
                                                    self._transform_prim(
                                                        path,
                                                        prim,
                                                        action_index,
                                                        transform_changes.diff_inc_translate,
                                                        transform_changes.diff_inc_rotate,
                                                        transform_changes.diff_inc_scale,
                                                    )
                                                # If list 0, index 1+ (2D entries), reposition 2D
                                                else:
                                                    action_index = list_index
                                                    source_transform_prim = source_prim
                                                    self._transform_prim(
                                                        path, source_transform_prim, action_index, two_d_offset
                                                    )
                                            # Otherwise reposition 3D
                                            else:
                                                action_index = list_of_lists_index
                                                source_transform_prim = source_prim
                                                self._transform_prim(
                                                    path, source_transform_prim, action_index, three_d_offset
                                                )
                                        else:
                                            dif_pos = (
                                                transform_changes.diff_inc_translate * (entry_index)
                                                + transform_changes.diff_offset_two_d
                                                + transform_changes.diff_offset_three_d
                                            )
                                            dif_rot = transform_changes.diff_inc_rotate * (entry_index)
                                            dif_scale = transform_changes.diff_inc_scale * (entry_index)
                                            action_index = 1
                                            self._transform_prim(path, prim, action_index, dif_pos, dif_rot, dif_scale)
                                elif transform_changes.two_d_changed:
                                    dif_pos = (
                                        transform_changes.diff_offset_two_d + transform_changes.diff_offset_three_d
                                    )
                                    action_index = list_index
                                    self._transform_prim(path, prim, action_index, dif_pos)
                                else:
                                    action_index = list_of_lists_index
                                    self._transform_prim(
                                        path, prim, action_index, transform_changes.diff_offset_three_d
                                    )
            return

        # 2D
        if self._two_d_result_prims:
            for list_index, index_list in enumerate(self._two_d_result_prims):
                for entry_index, entry in enumerate(index_list):
                    for created_prim in entry:
                        path = created_prim.path
                        prim = created_prim.prim
                        source_prim = created_prim.source_prim
                        is_original_prim = created_prim.is_original_prim

                        if not is_original_prim:
                            # If one D changed...
                            if transform_changes.one_d_changed:
                                # If follow rotations...
                                if self._get_reorient_mode_on():
                                    # If 1D (list 0 in 2D list) - do reorient
                                    if list_index == 0:
                                        action_index = entry_index
                                        source_transform_prim = self._get_source_transform_prim(source_prim)
                                        self._transform_prim_reorient(
                                            path,
                                            prim,
                                            source_transform_prim,
                                            action_index,
                                            inc_trans,
                                            inc_rot,
                                            inc_scale,
                                        )
                                    # If index 1+ (2D), reposition
                                    else:
                                        action_index = list_index
                                        source_transform_prim = source_prim
                                        self._transform_prim(path, source_transform_prim, action_index, two_d_offset)
                                # Modify based on one d changes + any diff offset for two D
                                else:
                                    # If resetting, essentially do the same logic as follow rotation.
                                    if reset:
                                        if list_index == 0:
                                            action_index = entry_index
                                            self._transform_prim(
                                                path,
                                                prim,
                                                action_index,
                                                transform_changes.diff_inc_translate,
                                                transform_changes.diff_inc_rotate,
                                                transform_changes.diff_inc_scale,
                                            )
                                        else:
                                            action_index = list_index
                                            source_transform_prim = source_prim
                                            self._transform_prim(
                                                path, source_transform_prim, action_index, two_d_offset
                                            )
                                    else:
                                        dif_pos = (
                                            transform_changes.diff_inc_translate * (entry_index)
                                            + transform_changes.diff_offset_two_d
                                        )
                                        dif_rot = transform_changes.diff_inc_rotate * (entry_index)
                                        dif_scale = transform_changes.diff_inc_scale * (entry_index)
                                        action_index = 1
                                        self._transform_prim(path, prim, action_index, dif_pos, dif_rot, dif_scale)
                            # Otherwise just update 2D offsets
                            else:
                                action_index = list_index
                                self._transform_prim(path, prim, action_index, transform_changes.diff_offset_two_d)
            return

        # 1D
        if self._one_d_result_prims:
            for entry_index, entry in enumerate(self._one_d_result_prims):
                for created_prim in entry:
                    path = created_prim.path
                    prim = created_prim.prim
                    source_prim = created_prim.source_prim
                    is_original_prim = created_prim.is_original_prim

                    if not is_original_prim:
                        if transform_changes.one_d_changed:
                            action_index = entry_index
                            if self._get_reorient_mode_on():
                                source_transform_prim = self._get_source_transform_prim(source_prim)
                                self._transform_prim_reorient(
                                    path, prim, source_transform_prim, action_index, inc_trans, inc_rot, inc_scale
                                )
                            else:
                                self._transform_prim(
                                    path,
                                    prim,
                                    action_index,
                                    transform_changes.diff_inc_translate,
                                    transform_changes.diff_inc_rotate,
                                    transform_changes.diff_inc_scale,
                                )

    # Call when selected prims are moved and propagate transform updates to arrayed prims
    def _update_selected_transformations(self, changes: dict):
        # No selection or preview is off - kick out
        if self._check_preview_off_or_no_valid_prims():
            return

        # Check to see if a valid prim's pivot changed
        # If so, rebuild transformations on all prims and kick out
        for prim in self._valid_prims:
            if changes[prim].diff_pivot != Gf.Vec3d(0):
                inc_trans = self._array_values[array_const.INC_TRANSLATE]
                inc_rot = self._array_values[array_const.INC_ROTATE]
                inc_scale = self._array_values[array_const.INC_SCALE]
                two_d_offset = self._array_values[array_const.TWO_D_OFFSET]
                three_d_offset = self._array_values[array_const.THREE_D_OFFSET]
                tcs = TransformChanges()
                tcs.one_d_changed = True
                tcs.diff_inc_translate = inc_trans
                tcs.diff_inc_rotate = inc_rot
                tcs.diff_inc_scale = inc_scale
                tcs.diff_offset_two_d = two_d_offset
                tcs.diff_offset_three_d = three_d_offset
                self._update_value_transformations(tcs, True)
                return

        # Index to use for transformation multiplications
        action_index = 1  # 1 = uniform

        # Does transformations - consolidated into func since all 3 dimensions use the same logic for this
        # Local utility
        def do_transform(path, prim, source_prim):
            # Get the appropriate prim to use for transformations
            source_transform_prim = self._get_source_transform_prim(source_prim)

            if source_transform_prim in changes:
                inc_trans = changes[source_transform_prim].diff_inc_translate
                inc_rot = changes[source_transform_prim].diff_inc_rotate
                inc_scale = changes[source_transform_prim].diff_inc_scale

                if self._get_reorient_mode_on():
                    self._transform_prim_reorient(
                        path, prim, source_prim, action_index, inc_trans, inc_rot, inc_scale, True
                    )
                else:
                    self._transform_prim(path, prim, action_index, inc_trans, inc_rot, inc_scale)

        # Here we are working backwards - if the 3D list exists, all other lists exist inside, so we can do everything in one go
        # 3D
        if self._three_d_result_prims:
            for index_list_of_lists in self._three_d_result_prims:
                for list in index_list_of_lists:
                    for entry_index, entry in enumerate(list):
                        for prim_index, created_prim in enumerate(entry):
                            path = created_prim.path
                            prim = created_prim.prim
                            is_original_prim = created_prim.is_original_prim

                            # Get the source source prim from 1D
                            source_prim = self._one_d_result_prims[entry_index][prim_index].source_prim

                            if not is_original_prim:
                                do_transform(path, prim, source_prim)
            return

        # 2D
        if self._two_d_result_prims:
            for index_list in self._two_d_result_prims:
                for entry_index, entry in enumerate(index_list):
                    for prim_index, created_prim in enumerate(entry):
                        path = created_prim.path
                        prim = created_prim.prim
                        is_original_prim = created_prim.is_original_prim

                        # Get the source source prim from 1D
                        source_prim = self._one_d_result_prims[entry_index][prim_index].source_prim

                        if not is_original_prim:
                            do_transform(path, prim, source_prim)
            return

        # 1D
        if self._one_d_result_prims:
            for prim_list in self._one_d_result_prims:
                for created_prim in prim_list:
                    path = created_prim.path
                    prim = created_prim.prim
                    source_prim = created_prim.source_prim
                    is_original_prim = created_prim.is_original_prim

                    if not is_original_prim:
                        do_transform(path, prim, source_prim)

    # Call when a major change is made that would require a rebuild, eg:
    # Selection change, instance/copy change, or source selection change
    def _rebuild(self):
        self._clear_resulting_prims()
        self._refresh()

    # REFRESH
    def _refresh(self):
        # Make sure to set the system seed for random generation
        random.seed(self._array_values[array_const.RANDOM_ORDER_SEED])

        # If there's no prims selected or preview is off, clear
        if self._check_preview_off_or_no_valid_prims():
            self._clear_resulting_prims()
            return

        # Construct the 1D array
        if self._array_values[array_const.COUNT] > 1:
            self._create_1d(
                amount=self._array_values[array_const.COUNT],
                results=self._one_d_result_prims,
                add_source_prims=True,
                prim_to_use_start_index=0,
                transform_modifier_start_index=0,
            )
            # 1D Required to make 2D
            if self._array_values[array_const.TWO_D_COUNT] > 1:
                # Construct the 2D array
                self._create_2d(
                    amount=self._array_values[array_const.TWO_D_COUNT],
                    results=self._two_d_result_prims,
                    source_prims=self._one_d_result_prims,
                    add_to_end=False,
                    start_index=0,
                )
                # 2D Required to make 3D
                if self._array_values[array_const.THREE_D_COUNT] > 1:
                    # Construct the 2D array
                    self._create_3d(
                        amount=self._array_values[array_const.THREE_D_COUNT],
                        results=self._three_d_result_prims,
                        source_prims=self._two_d_result_prims,
                        add_to_end=False,
                        start_index=0,
                    )

    # Clears all temporarily created prims - usually when the user hits cancel or refreshes the extension
    def _clear_resulting_prims(self):
        valid_prim_paths = []

        # Local utility method
        def try_add_to_valid_prim_paths(created_prim):
            path = created_prim.path
            is_original_prim = created_prim.is_original_prim
            if path and not is_original_prim:
                valid_prim_paths.append(path)

        if len(self._three_d_result_prims) > 0:
            for list_of_list in self._three_d_result_prims:
                for list in list_of_list:
                    for entry in list:
                        for created_prim in entry:
                            try_add_to_valid_prim_paths(created_prim)
        elif len(self._two_d_result_prims) > 0:
            for list in self._two_d_result_prims:
                for entry in list:
                    for created_prim in entry:
                        try_add_to_valid_prim_paths(created_prim)
        else:
            for entry in self._one_d_result_prims:
                for created_prim in entry:
                    try_add_to_valid_prim_paths(created_prim)

        # Clear lists
        self._one_d_result_prims.clear()
        self._two_d_result_prims.clear()
        self._three_d_result_prims.clear()

        # Delete all valid existing resulting prims
        self.delete_prims(valid_prim_paths)

    # Create 1D
    def _create_1d(
        self,
        amount: int,
        results: list,
        add_source_prims: bool,
        prim_to_use_start_index: int = 0,
        transform_modifier_start_index: int = 0,
    ):
        source_prims = []
        inc_trans = self._array_values[array_const.INC_TRANSLATE]
        inc_rot = self._array_values[array_const.INC_ROTATE]
        inc_scale = self._array_values[array_const.INC_SCALE]

        for i in range(amount):
            source_prims.append(self._get_prim_to_use(prim_to_use_start_index + i))

        for index, prim_list in enumerate(source_prims):
            prims_at_index = []
            for prim in prim_list:
                path = prim.GetPath()
                if add_source_prims:
                    if index == 0:
                        created_prim = CreatedPrim()
                        created_prim.set_values(path, prim, prim, True)
                        prims_at_index.append(created_prim)
                        continue

                # COPY/INSTANCE
                resulting_prim = self._copy_prim(path, prim, False)
                prims_at_index.append(resulting_prim)

                # Get the prim to use for transformations based on source selection mode
                source_transform_prim = self._get_source_transform_prim(prim)

                # TRANSFORMS
                action_index = transform_modifier_start_index + index  # value to use for calculations.
                if self._get_reorient_mode_on():
                    self._transform_prim_reorient(
                        resulting_prim.path,
                        source_transform_prim,
                        self._get_source_transform_prim(resulting_prim.source_prim),
                        action_index,
                        inc_trans,
                        inc_rot,
                        inc_scale,
                    )
                else:
                    self._transform_prim(
                        resulting_prim.path, source_transform_prim, action_index, inc_trans, inc_rot, inc_scale
                    )

                # DISABLE INTERACTIONS
                self._update_prim_interactions(resulting_prim, False)

            # Add all prims created this index/loop to the one supplied results list
            # List of list of CreatedPrims()
            results.append(prims_at_index)

    # Create 2D
    def _create_2d(
        self, amount: int, results: list, source_prims: list, add_to_end: bool = False, start_index: int = 0
    ):
        two_d_offset = self._array_values[array_const.TWO_D_OFFSET]

        # If the user updated the 2D count but the 2D list has not been constructed yet...
        # Add the one D list to index 0
        if add_to_end and len(self._two_d_result_prims) == 0:
            self._two_d_result_prims.append(self._one_d_result_prims)

        # How many 2D sections to add
        for iter in range(amount):
            # Copy the whole first entry from 1D into 0 index in 2D, then continue to the next 2D index
            if not add_to_end:
                if iter == 0:
                    self._two_d_result_prims.append(self._one_d_result_prims)
                    continue

            # The whole list at the previous index [[a,b],[a,b],[a,b]]
            # previous_index_list = self._two_d_result_prims[iter - 1]
            base_list = self._two_d_result_prims[0]
            # Loop through each entry in the previous index list [a,b]
            new_list = []
            for entry in base_list:
                # Each prim in this entry a,b...
                new_entry = []
                for created_prim in entry:
                    path = created_prim.path
                    prim = created_prim.prim

                    # COPY/INSTANCE
                    resulting_prim = self._copy_prim(path, prim, False)
                    new_entry.append(resulting_prim)

                    # Get the prim to use for transformations
                    source_transform_prim = prim

                    # TRANSFORMS
                    action_index = start_index + iter
                    self._transform_prim(resulting_prim.path, source_transform_prim, action_index, two_d_offset)

                    # DISABLE INTERACTIONS
                    self._update_prim_interactions(resulting_prim, False)

                new_list.append(new_entry)
            self._two_d_result_prims.append(new_list)

    # Called when 1D updates
    def _update_2d(self, amount: int):

        two_d_offset = self._array_values[array_const.TWO_D_OFFSET]

        diff_list = []
        for i in range(amount):
            diff_list.append(self._one_d_result_prims[i - amount])

        # How many 2D sections to add
        for iter in range(self._array_values[array_const.TWO_D_COUNT]):
            if iter == 0:
                continue

            base_list = diff_list
            # Loop through each entry in the diff list
            for entry in base_list:
                # Each prim in this entry a,b...
                new_entry = []
                for created_prim in entry:
                    path = created_prim.path
                    prim = created_prim.prim

                    # COPY/INSTANCE
                    resulting_prim = self._copy_prim(path, prim, False)
                    new_entry.append(resulting_prim)

                    # Get the prim to use for transformations
                    source_transform_prim = prim

                    # TRANSFORMS
                    action_index = iter
                    self._transform_prim(resulting_prim.path, source_transform_prim, action_index, two_d_offset)

                    # DISABLE INTERACTIONS
                    self._update_prim_interactions(resulting_prim, False)

                # Add each new entry to the end of the list at the current index
                self._two_d_result_prims[iter].append(new_entry)

    # Create 3D
    def _create_3d(
        self, amount: int, results: list, source_prims: list, add_to_end: bool = False, start_index: int = 0
    ):

        three_d_offset = self._array_values[array_const.THREE_D_OFFSET]

        # If the user updated the 3D count but the 3D list has not been constructed yet...
        # Add the two D list to index 0
        if add_to_end and len(self._three_d_result_prims) == 0:
            self._three_d_result_prims.append(self._two_d_result_prims)

        # How many 3D sections to add
        for iter in range(amount):
            # Copy all of 2D into the 0 index in 3D, then continue to the next 3D index
            if not add_to_end:
                if iter == 0:
                    self._three_d_result_prims.append(self._two_d_result_prims)
                    continue

            # The whole list at the previous index [[[a,b],[a,b],[a,b]], [[a,b],[a,b],[a,b]]]
            base_list = self._three_d_result_prims[0]
            # Loop through each list in the previous index lists [[a,b],[a,b],[a,b]]
            new_list_of_lists = []
            for list in base_list:
                # Loop through each entry in this list [a,b]
                new_list = []
                for entry in list:
                    # Each prim in this entry a,b...
                    new_entry = []
                    for created_prim in entry:
                        path = created_prim.path
                        prim = created_prim.prim

                        # COPY/INSTANCE
                        resulting_prim = self._copy_prim(path, prim, False)
                        new_entry.append(resulting_prim)

                        # Get the prim to use for transformations
                        source_transform_prim = prim

                        # TRANSFORMS
                        action_index = start_index + iter
                        self._transform_prim(resulting_prim.path, source_transform_prim, action_index, three_d_offset)

                        # DISABLE INTERACTIONS
                        self._update_prim_interactions(resulting_prim, False)

                    new_list.append(new_entry)
                new_list_of_lists.append(new_list)
            self._three_d_result_prims.append(new_list_of_lists)

    # Called when 1D or 2D updates
    def _update_3d(self, amount: int, source_dimension_change: Dimension):

        three_d_offset = self._array_values[array_const.THREE_D_OFFSET]

        index_zero_lists = self._three_d_result_prims[0]

        diff_list = []
        if source_dimension_change == Dimension.ONE:
            for list in index_zero_lists:
                curr_list_new_entries = []
                for i in range(amount):
                    curr_list_new_entries.append(list[i - amount])
                diff_list.append(curr_list_new_entries)
        elif source_dimension_change == Dimension.TWO:
            new_lists = []
            for i in range(amount):
                new_lists.append(index_zero_lists[i - amount])
            diff_list.append(new_lists)

        # How many 3D sections to add
        for iter in range(self._array_values[array_const.THREE_D_COUNT]):
            if iter == 0:
                continue

            base_list = diff_list
            # Loop through each entry in the diff list
            for index, list in enumerate(base_list):
                if source_dimension_change == Dimension.ONE:
                    for entry in list:
                        new_entry = []
                        for created_prim in entry:
                            path = created_prim.path
                            prim = created_prim.prim

                            # COPY/INSTANCE
                            resulting_prim = self._copy_prim(path, prim, False)
                            new_entry.append(resulting_prim)

                            # Get the prim to use for transformations
                            source_transform_prim = prim

                            # TRANSFORMS
                            action_index = iter
                            self._transform_prim(
                                resulting_prim.path, source_transform_prim, action_index, three_d_offset
                            )

                            # DISABLE INTERACTIONS
                            self._update_prim_interactions(resulting_prim, False)
                        self._three_d_result_prims[iter][index].append(new_entry)

                elif source_dimension_change == Dimension.TWO:
                    for list_of_entries in list:
                        new_list = []
                        for entry in list_of_entries:
                            new_entry = []
                            for created_prim in entry:
                                path = created_prim.path
                                prim = created_prim.prim

                                # COPY/INSTANCE
                                resulting_prim = self._copy_prim(path, prim, False)
                                new_entry.append(resulting_prim)

                                # Get the prim to use for transformations
                                source_transform_prim = prim

                                # TRANSFORMS
                                action_index = iter
                                self._transform_prim(
                                    resulting_prim.path, source_transform_prim, action_index, three_d_offset
                                )

                                # DISABLE INTERACTIONS
                                self._update_prim_interactions(resulting_prim, False)
                            new_list.append(new_entry)
                        self._three_d_result_prims[iter].append(new_list)

    # Returns the appropriate prims to use from the valid prims based on the selected array type
    def _get_prim_to_use(self, index: int):
        prim_to_use = []  # List of prim paths
        if self._array_values["array_type"] is array_const.ARRAY_TYPE_DEFAULT.GROUP:
            prim_to_use = self._valid_prims
            return prim_to_use
        if self._array_values["array_type"] is array_const.ARRAY_TYPE_DEFAULT.ORDERED_SEQUENCE:
            index_to_use = (index) % len(self._valid_prims)
            prim_to_use.append(self._valid_prims[index_to_use])
            return prim_to_use
        if self._array_values["array_type"] is array_const.ARRAY_TYPE_DEFAULT.RANDOM_SEQUENCE:
            if index == 0:
                prim_to_use.append(self._valid_prims[0])  # Make sure the first selected prim is the first retunred
            else:
                index_to_use = random.randrange(0, len(self._valid_prims))
                prim_to_use.append(self._valid_prims[index_to_use])
            return prim_to_use

    # Returns the correct prim to use for transformations based on the source selection mode selected
    # Both sequences use the first selected prim as the array start point
    def _get_source_transform_prim(self, current_prim):
        if self._array_values["array_type"] is array_const.ARRAY_TYPE_DEFAULT.GROUP:
            return current_prim
        elif self._array_values["array_type"] is array_const.ARRAY_TYPE_DEFAULT.ORDERED_SEQUENCE:
            return self._valid_prims[0]  # From first selected
            # return self._valid_prims[len(self._valid_prims)-1] # From last selected
        elif self._array_values["array_type"] is array_const.ARRAY_TYPE_DEFAULT.RANDOM_SEQUENCE:
            return self._valid_prims[0]  # From first selected
            # return self._valid_prims[len(self._valid_prims)-1] # From last selected

    # Applies the array settings
    def apply_array(self) -> tuple:
        """
        Returns a tuple of (Applied prim paths, grouped prim path, selected prim paths(from creation))
        """
        usd_context = omni.usd.get_context()
        selection = usd_context.get_selection()

        # Nothing has been created
        if (
            len(self._one_d_result_prims) == 0
            and len(self._two_d_result_prims) == 0
            and len(self._three_d_result_prims) == 0
        ):
            # Is preview off?
            if not self._array_values[array_const.PREVIEW]:
                # Ignore preview and rebuild
                self._ignore_preview = True
                self._rebuild()
                self._ignore_preview = False

        applied_prim_paths = []
        grouped_prim_path = []
        selected_prim_paths = []

        def try_enable_prim(created_prim):
            path = created_prim.path
            is_original_prim = created_prim.is_original_prim
            if path and not is_original_prim:
                applied_prim_paths.append(path)
                self._update_prim_interactions(created_prim, True)

        if len(self._three_d_result_prims) > 0:
            for list_of_list in self._three_d_result_prims:
                for list in list_of_list:
                    for entry in list:
                        for created_prim in entry:
                            try_enable_prim(created_prim)
        elif len(self._two_d_result_prims) > 0:
            for list in self._two_d_result_prims:
                for entry in list:
                    for created_prim in entry:
                        try_enable_prim(created_prim)
        elif len(self._one_d_result_prims) > 0:
            for entry in self._one_d_result_prims:
                for created_prim in entry:
                    try_enable_prim(created_prim)

        self._one_d_result_prims.clear()
        self._two_d_result_prims.clear()
        self._three_d_result_prims.clear()

        # Only try to group or auto-select created if anything was actually made.
        if len(applied_prim_paths) > 0:
            # Group results
            if self._array_values[array_const.ARRAY_GROUP_RESULT]:
                grouped_prim_path = omni.kit.commands.execute("GroupPrimsSelectCommand", prim_paths=applied_prim_paths)
                # Auto select created (with grouping)
                if self._array_values[array_const.AUTO_SELECT_CREATED]:
                    selection.set_prim_path_selected(grouped_prim_path[1], True, False, True, True)
                    selected_prim_paths = selection.get_selected_prim_paths()
            else:
                # Auto select created
                if self._array_values[array_const.AUTO_SELECT_CREATED]:
                    selection.set_selected_prim_paths(applied_prim_paths, True)
                    selected_prim_paths = selection.get_selected_prim_paths()

        self._array_params.reset_to_defaults()
        self._array_values = self._array_params.get_defaults()
        self._prev_array_values = self._array_values.copy()

        self._target_prims.clear()
        self._valid_prims.clear()

        return applied_prim_paths, grouped_prim_path, selected_prim_paths

    # Reset the array values
    def reset_array_values(self):
        self._array_params.reset_to_defaults()
        self._array_values = self._array_params.get_defaults()
        self._prev_array_values = self._array_values.copy()
        print(f"Values reset: {self._array_values}")

        self._rebuild()

    # Cancel the array and reset values
    def cancel_array(self):
        self._array_params.reset_to_defaults()
        self._array_values = self._array_params.get_defaults()
        self._prev_array_values = self._array_values.copy()

        self._target_prims.clear()
        self._valid_prims.clear()

        self._refresh()

    # ============== PUBLIC UTILITY METHODS ===============

    # Returns all current array values
    def get_all_array_values(self) -> dict:
        return self._array_values.copy()

    # Returns a single array value
    def get_array_value(self, value_name: str):
        if self._check_value_exists(value_name):
            return self._array_values[value_name]

    # Returns a tuple containing the current target prims and current array values
    def get_current_prims_and_values(self) -> tuple:
        return self._target_prims.copy(), self._array_values.copy()

    # ============== LOCAL UTILITY METHODS ===============

    # Given a list of prims, returns their prim paths
    def _extract_paths(self, prims: list):
        paths = []
        for prim in prims:
            paths.append(prim.GetPath())
        return paths

    # Given a list of prim paths, returns their prims
    def _extract_prims(self, paths: list):
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        prims = []
        for path in paths:
            prims.append(stage.GetPrimAtPath(path))
        return prims

    # Returns the bool for reorient
    def _get_reorient_mode_on(self):
        return self._array_values[array_const.REORIENT_ROTATION]

    # Quick check to see if preview is off and there's no valid prims selected
    # Returns True if there's no valid prims or preview is disabled
    def _check_preview_off_or_no_valid_prims(self):
        if self._ignore_preview:
            return False
        return not self._valid_prims or not self._array_values[array_const.PREVIEW]

    # Checks whether a provided value exists in the _array_values dict
    # If the provided value_name does not exist, a warning is thrown
    def _check_value_exists(self, value_name: str) -> bool:
        if value_name in self._array_values:
            return True
        else:
            carb.log_warn(f"{value_name} is not an array property.")
            return False

    # Return a list of valid target prims given a list of prim paths
    def _get_valid_target_prims(self, target_prims: list, xformables_only: bool) -> list:
        valid_prims = []
        if len(target_prims) == 0:
            return valid_prims

        # Remove any non-xformables
        xformable_prims = []
        for prim in target_prims:
            # Exclude all instance proxies from valid lists
            # Instance proxy = greyed out child(ren) of instanced objects
            if prim.IsInstanceProxy():
                carb.log_warn(f"{prim} is an instance proxy and is invalid for manipulation.")
                continue
            # Check to see if the prim has time varied attributes, if True, exclude it.
            if self._check_has_time_varied_attributes(prim):
                carb.log_warn(
                    f"{prim} has at least one time varied xform op. Prims with time varied xform ops are not allowed. "
                    + "Try providing a parent xform without time varied ops, instead."
                )
                continue
            if xformables_only:
                if prim.IsA(UsdGeom.Xformable):
                    xformable_prims.append(prim)
                else:
                    carb.log_warn(f"{prim} is not a valid prim and will be ignored. Only Xformable prims are allowed.")
            else:
                xformable_prims.append(prim)

        # Remove children prims of provided parent prims, if applicable
        # We don't support making copies of a parent containing children, where the parent and children are both provided.
        # In this case, we'll only take the parent and copy that.
        sort_order = xformable_prims.copy()
        result = Sdf.Path.RemoveDescendentPaths(self._extract_paths(xformable_prims))
        valid_prims = self._extract_prims(result)
        valid_prims.sort(key=sort_order.index)

        # If there was a change in the resulting prims, check the difference and spit out a warning with the excluded prims
        if valid_prims != xformable_prims:
            difference = []
            for prim in target_prims:
                if prim not in valid_prims:
                    difference.append(prim)
            if difference:
                carb.log_warn(
                    "Providing child prims along with their parent prim(s) is not allowed. The following provided prims have been excluded:\n"
                    + f"{difference}"
                )

        return valid_prims

    # Returns the rotation attribute and rotation order used by the supplied prim
    def _get_valid_rotation_attribute(self, prim) -> tuple:
        """
        Returns a tuple of (Attribute (Usd.Attribute), Value (Vec3d), Rotation Order (Vec3i)).

        If no attribute exists, the value is calculated (usually identity).
        """
        local_transform = omni.usd.get_local_transform_SRT(prim)
        XYZ = prim.GetAttribute("xformOp:rotateXYZ")
        XZY = prim.GetAttribute("xformOp:rotateXZY")
        YXZ = prim.GetAttribute("xformOp:rotateYXZ")
        YZX = prim.GetAttribute("xformOp:rotateYZX")
        ZXY = prim.GetAttribute("xformOp:rotateZXY")
        ZYX = prim.GetAttribute("xformOp:rotateZYX")
        ORIENT = prim.GetAttribute("xformOp:orient")
        # Returns the attribute, the value, and the order
        if XYZ:
            return XYZ, local_transform[1], local_transform[2]
        if XZY:
            return XZY, local_transform[1], local_transform[2]
        if YXZ:
            return YXZ, local_transform[1], local_transform[2]
        if YZX:
            return YZX, local_transform[1], local_transform[2]
        if ZXY:
            return ZXY, local_transform[1], local_transform[2]
        if ZYX:
            return ZYX, local_transform[1], local_transform[2]
        if ORIENT:
            return ORIENT, local_transform[1], local_transform[2]
        return None, local_transform[1], local_transform[2]

    # Checks if a prim has time varied xform ops or not. Returns result
    def _check_has_time_varied_attributes(self, prim: Usd.Prim) -> bool:
        xform = UsdGeom.Xformable(prim)
        xform_ops = xform.GetOrderedXformOps()
        for op in xform_ops:
            if op.MightBeTimeVarying():
                return True
        return False

    # Checks if a translate, rotate, scale, or pivot op exists, and if so, returns True/False and the value of the op
    def _check_attribute_exists(self, prim: Usd.Prim, op: str) -> tuple:
        """
        Returns a tuple of (Attribute Exists (bool), Value (Vec3d), Attribute (Usd.Attribute)).

        If no attribute exists, the value is calculated (usually identity).
        """
        local_transform = omni.usd.get_local_transform_SRT(prim)
        if op == "Translate":
            attr = prim.GetAttribute("xformOp:translate")
            return bool(attr), Gf.Vec3d(local_transform[3]), attr if bool(attr) else None
        elif op == "Rotate":
            attr = self._get_valid_rotation_attribute(prim)
            return attr[0] is not None, Gf.Vec3d(attr[1]), attr[0]
        elif op == "Scale":
            attr = prim.GetAttribute("xformOp:scale")
            return bool(attr), Gf.Vec3d(local_transform[0]), attr if bool(attr) else None
        elif op == "Pivot":
            attr = prim.GetAttribute("xformOp:translate:pivot")
            if attr:
                return True, Gf.Vec3d(attr.Get()), attr
            else:
                return False, Gf.Vec3d(0), None

    # Resets all created prim transforms to their source prim's values
    # Called when the pivot is modified on a source prim that has a pivot op
    def _reset_prim_transforms_to_source(self):
        def reset_prim_transforms(created_prim: CreatedPrim):
            # Skip original prims
            if created_prim.is_original_prim:
                return

            prim = created_prim.prim
            path = created_prim.path
            source_prim = created_prim.source_prim

            pivot_op = self._check_attribute_exists(prim, "Pivot")

            source_trans_op = self._check_attribute_exists(source_prim, "Translate")
            source_rot_op = self._check_attribute_exists(source_prim, "Rotate")
            source_scale_op = self._check_attribute_exists(source_prim, "Scale")
            source_pivot_op = self._check_attribute_exists(source_prim, "Pivot")

            if pivot_op[0] and source_pivot_op[0]:
                pivot_op[2].Set(source_pivot_op[1])

            cmd = TransformPrimSRTCommand(
                path=path,
                new_translation=source_trans_op[1],
                new_rotation_euler=source_rot_op[1],
                new_scale=source_scale_op[1],
            )
            cmd.do()

        if self._three_d_result_prims:
            for index_list_of_lists in self._three_d_result_prims:
                for list in index_list_of_lists:
                    for entry in list:
                        for created_prim in entry:
                            reset_prim_transforms(created_prim)
        elif self._two_d_result_prims:
            for index_list in self._two_d_result_prims:
                for entry in index_list:
                    for created_prim in entry:
                        reset_prim_transforms(created_prim)
        elif self._one_d_result_prims:
            for entry in self._one_d_result_prims:
                for created_prim in entry:
                    reset_prim_transforms(created_prim)


# ============== CUSTOM COMMANDS ================


# Custom version of CopyPrimCommand which does NOT auto-select copied prim on completion
class CopyPrimSelectCommand(CopyPrimCommand):
    def do(self):
        stage = self._usd_context.get_stage()
        usd_prim = stage.GetPrimAtPath(self._path_from)
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

        return self._path_to


# Custom version of GroupPrimsCommand which does NOT auto-select group parent on completion
class GroupPrimsSelectCommand(GroupPrimsCommand):
    def do(self):
        self._move_commands = []
        if not self._prim_paths:
            return

        stage = self._get_stage()
        path = self._all_path_prefix.AppendElementString("Group")
        group_prim_path = omni.usd.get_stage_next_free_path(stage, path, False)
        self._group_prim_path = Sdf.Path(group_prim_path)
        group_prim = UsdGeom.Xform.Define(stage, self._group_prim_path)
        self._create_group_xform_impl(stage, group_prim, self._prim_paths)

        return group_prim_path


# Custom version of CreateInstanceCommand which does NOT auto-select created prim on completion
class CreateInstanceSelectCommand(CreateInstanceCommand):
    def do(self):
        stage = self._usd_context.get_stage()
        timecode = self._timeline.get_current_time() * stage.GetTimeCodesPerSecond()
        prim_from = stage.GetPrimAtPath(self._path_from)

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

        return self._path_to


omni.kit.commands.register_all_commands_in_module(__name__)
