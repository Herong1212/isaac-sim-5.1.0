# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from typing import List

import carb
import omni.ext
import omni.usd
from pxr import Usd

from .action_window import ActionWindow
from .array_const import ALLOWED_INSTANCE_TYPES, CREATE_TYPE, CreateType
from .array_core import ArrayCore
from .array_params import ArrayParams


class Extension(omni.ext.IExt):
    # Set up
    def on_startup(self, ext_id):
        carb.log_verbose("Array Tool startup")
        self._array_core = ArrayCore()
        self._action_window = ActionWindow()

    # Clean up
    def on_shutdown(self):
        carb.log_verbose("Array Tool shutdown")
        self._array_core.clean()
        self._array_core = None
        self._action_window.clean()
        self._action_window = None

    # Can be used to easily construct a new dictionary of default array values
    @staticmethod
    def construct_new_array() -> dict:
        return ArrayParams().get_defaults()


# Call to create an array from scratch
class CreateArrayCommand(omni.kit.commands.Command):
    """
    Creates an Array of prims - undoable/redoable **Command**.

    Can be used outside of the Array Tool extension.

    Required Args:
        target_prims (list): The list of prims to array. Expects prims, not prim paths.
        array_values (dict): The values to use to construct the array. Expects a dictionary matching the one seen in ArrayParams().

    Optional Args:
        usd_context_name (str): The USD context where this command should be used - allows for this command to be used by multiple USD contexts simultaneously.

    Returns:
        Do() (tuple): (Created prim paths: list, Grouped prims path: list, Seleced prims path: list)
    """

    def __init__(self, target_prims: List[Usd.Prim], array_values: dict, usd_context_name: str = ""):
        super().__init__()
        self._target_prim_paths = self.extract_paths(target_prims)
        self._target_prims = None
        self._array_values = array_values
        self._creation_results = None
        self._array_core = ArrayCore.get_instance()
        self._usd_context = omni.usd.get_context(usd_context_name)
        self._stage = self._usd_context.get_stage()

    def do(self):
        self._target_prims = self.extract_prims(self._target_prim_paths)
        # Check valid values are provided
        if self.check_valid_args_supplied(self._target_prims, self._array_values):
            # Check valid prims are being provided
            valid_prim_results = self.check_has_valid_instanceable_prims(
                self._target_prims, self._array_values[CREATE_TYPE]
            )
            if valid_prim_results[0]:
                self._creation_results = self._array_core.create_array(valid_prim_results[1], self._array_values)
        return self._creation_results

    def undo(self):
        # Prevent undo from happening if nothing was created
        if self._creation_results is not None:
            self._array_core.delete_prims(self._creation_results[0].copy())

    def extract_paths(self, prims: list):
        paths = []
        for prim in prims:
            paths.append(prim.GetPath())
        return paths

    def extract_prims(self, paths: list):
        prims = []
        for path in paths:
            prims.append(self._stage.GetPrimAtPath(path))
        return prims

    def check_valid_args_supplied(self, target_prims: list, array_values: dict):
        if not target_prims:
            carb.log_warn("No prims provided. Please provide at least one valid prim.")
            return False
        elif not array_values:
            carb.log_warn("No array values provided. Please provide a dictionary of array values.")
            return False
        elif array_values:
            # Create a reference dictionary of expected values
            ref_values = ArrayParams().get_defaults()
            for key in ref_values.keys():
                if key not in array_values:
                    carb.log_warn(
                        "Missing expected array values. See ArrayParams for dictionary of expected array values."
                    )
                    return False
        return True

    def check_has_valid_instanceable_prims(self, target_prims: list, creation_type: CreateType):
        # If the creation type is set to copies, return True
        if creation_type is CreateType.COPIES:
            return True, target_prims

        # Only instance the allowed instanceable types
        allowed_types_for_instancing = ALLOWED_INSTANCE_TYPES
        unallowed_prims = []
        allowed_prims = []
        for prim in target_prims:
            if not prim or prim.GetTypeName() not in allowed_types_for_instancing:
                unallowed_prims.append(prim)
            else:
                allowed_prims.append(prim)

        has_unallowed_prims = len(unallowed_prims) > 0
        has_mixed_prims = has_unallowed_prims and target_prims != unallowed_prims

        if has_mixed_prims:
            message = f"Skipping invalid prims. Only Xforms are allowed to be instanced. Failed to instance the following prims: {unallowed_prims}."
            carb.log_warn(message)
            return True, allowed_prims

        if has_unallowed_prims:
            message = (
                f"Only Xforms are allowed to be instanced. Failed to instance the following prims: {unallowed_prims}."
            )
            carb.log_warn(message)
            return False, []

        return True, target_prims


# Called from the UI to Apply the current array tool values
class ApplyArrayCommand(omni.kit.commands.Command):
    """
    Used by the Array Tool UI to 'Apply' the array - undoable/redoable **Command**.

    Should NOT be used outside of the Array Tool extension.

    Optional Args:
        usd_context_name (str): The USD context where this command should be used - allows for this command to be used by multiple USD contexts simultaneously.
    """

    def __init__(self, usd_context_name: str = "") -> None:
        super().__init__()
        self._last_prim_paths = None
        self._last_prims = None
        self._last_values = None
        self._creation_results = None
        self._array_core = ArrayCore.get_instance()
        self._usd_context = omni.usd.get_context(usd_context_name)
        self._stage = self._usd_context.get_stage()

    def do(self):
        if self._last_prim_paths:
            self._last_prims = self.extract_prims(self._last_prim_paths)
            self._creation_results = self._array_core.create_array(self._last_prims, self._last_values)
        else:
            self._last_prims, self._last_values = self._array_core.get_current_prims_and_values()
            self._last_prim_paths = self.extract_paths(self._last_prims)
            self._creation_results = self._array_core.apply_array()

    def undo(self):
        self._array_core.delete_prims(self._creation_results[0].copy())

    def extract_paths(self, prims: list):
        paths = []
        for prim in prims:
            paths.append(prim.GetPath())
        return paths

    def extract_prims(self, paths: list):
        prims = []
        for path in paths:
            prims.append(self._stage.GetPrimAtPath(path))
        return prims


omni.kit.commands.register_all_commands_in_module(__name__)
