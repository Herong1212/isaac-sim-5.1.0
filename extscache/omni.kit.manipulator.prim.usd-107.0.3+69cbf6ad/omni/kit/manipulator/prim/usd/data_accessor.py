# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from __future__ import annotations

__all__ = ["UsdDataAccessor"]

import asyncio
import concurrent.futures
import math
import traceback
from enum import Enum, Flag, IntEnum, auto
from typing import Any, Callable, Dict, List, Sequence, Set, Tuple, Union

import carb
import carb.dictionary
import carb.events
import carb.profiler
import carb.settings
import omni.kit.app
import omni.kit.commands
import omni.kit.undo
import omni.timeline
import pxr.Sdf
import pxr.Usd
import pxr.UsdGeom
import usdrt.Gf
from omni.kit.async_engine import run_coroutine
from omni.kit.manipulator.prim.core import DataAccessorConstants as da_c
from omni.kit.viewport.manipulator.transform import DataAccessor
from omni.ui import scene as sc


# to be moved to omni.kit.manipulator.prim.usd
class UsdDataAccessor(DataAccessor):
    """A class for handling data access in USD contexts.

    This class extends the DataAccessor to provide specific functionalities for working with
    Universal Scene Description (USD) stages and primitives. It encapsulates operations such
    as obtaining USD stage references, transforming USD primitives, and managing USD-specific
    callbacks and cache mechanisms.

    Args:
        usd_context_name (str): An optional name identifier for the USD context.
        model: An optional reference to the model associated with the USD context."""

    from pxr import Gf, Sdf, Tf, Usd, UsdGeom, UsdUtils

    def __init__(self, usd_context_name: str = "", model=None):
        """Initializes the USD data accessor with optional context name and model."""
        super().__init__()
        self._settings = carb.settings.get_settings()
        self._xform_cache = None
        self._stage: self.Usd.Stage = None
        self._func_ref_prim_maker = None
        self._property_listener = None
        self._model = model
        self._usd_context_name = usd_context_name
        self._usd_context = omni.usd.get_context(self._usd_context_name)
        self._priority = 2
        self._priority_write = 1
        if self._settings.get(da_c.DATA_ACCESSOR_PRIORITY_USD) != None:
            self._priority = int(self._settings.get(da_c.DATA_ACCESSOR_PRIORITY_USD))
        if self._settings.get(da_c.DATA_ACCESSOR_PRIORITY_WRITE_USD) != None:
            self._priority_write = int(self._settings.get(da_c.DATA_ACCESSOR_PRIORITY_WRITE_USD))
        self.set_stage()

    def destroy(self):
        """Cleans up the data accessor, clearing all references and settings."""
        self._model = None
        self._usd_context_name = None
        self._usd_context = None
        self._priority = -1
        self._priority_write = -1
        self._property_listener = None

    def get_sdf_path_type(self) -> type:
        """Returns the type used for SDF paths.

        Returns:
            type: The SDF path type."""
        return pxr.Sdf.Path

    def get_data_tag(self) -> str:
        """Gets the data tag associated with USD.

        Returns:
            str: The data tag for USD."""
        return "USD"

    @property
    def priority(self) -> int:
        """Gets the priority level for the data accessor.

        Returns:
            int: The priority level."""
        return self._priority

    @property
    def priority_write(self) -> int:
        """Gets the write priority level for the data accessor.

        Returns:
            int: The write priority level."""
        return self._priority_write

    @property
    def is_inited(self):
        """Gets the initialization state of the data accessor.

        Returns:
            bool: True if the data accessor is initialized, False otherwise."""
        return self._inited

    @property
    def usd_context(self):
        """Gets the USD context used by the data accessor.

        Returns:
            :obj:`Usd.Context`: The USD context."""
        return self._usd_context

    def is_transformation_affected_by_attr_named(self, name: str) -> bool:
        """Checks if transformation is affected by the specified attribute name.

        Args:
            name (str): The name of the attribute.

        Returns:
            bool: True if affected, False otherwise."""
        return pxr.UsdGeom.Xformable.IsTransformationAffectedByAttrNamed(name)

    def is_instance_proxy(self, prim: pxr.Usd.Prim) -> bool:
        """Determines if the given prim is an instance proxy.

        Args:
            prim (:obj:`Usd.Prim`): The prim to check.

        Returns:
            bool: True if it is an instance proxy, False otherwise."""
        return prim.IsInstanceProxy()

    def get_stage_up_axis(self) -> str:
        """Gets the up axis of the current stage.

        Returns:
            str: The up axis ('Y' or 'Z')."""
        return pxr.UsdGeom.GetStageUpAxis(self._stage)

    # TODO: check paths types
    def remove_descendent_paths(self, paths: List[pxr.Sdf.Path]) -> List[pxr.Sdf.Path]:
        """Removes descendent paths from the given list of paths.

        Args:
            paths (List[:obj:`Sdf.Path`]): The list of paths to process.

        Returns:
            List[:obj:`Sdf.Path`]: The list of paths without descendants."""
        pxrPaths = [self.to_pxr_path(path) for path in paths]
        return pxr.Sdf.Path.RemoveDescendentPaths(pxrPaths)

    def is_prim_active(self, prim: pxr.Usd.Prim) -> bool:
        """Checks if the specified prim is active.

        Args:
            prim (:obj:`Usd.Prim`): The prim to check.

        Returns:
            bool: True if the prim is active, False otherwise."""
        return prim.IsActive()

    def get_sdf_path(self, path: pxr.Sdf.Path) -> pxr.Sdf.Path:
        """Converts the given path to an SDF path.

        Args:
            path (:obj:`Sdf.Path`): The path to convert.

        Returns:
            :obj:`Sdf.Path`: The converted SDF path."""
        return self.to_pxr_path(path)

    def get_string_path(self, path: Union[pxr.Sdf.Path, str]) -> str:
        """Converts the given path to a string representation.

        Args:
            path (Union[:obj:`Sdf.Path`, str]): The path to convert.

        Returns:
            str: The string representation of the path."""
        return str(path)

    def is_valid_path(self, path: Any) -> bool:
        """Checks if the given path is a valid SDF path.

        Args:
            path (Any): The path to check.

        Returns:
            bool: True if the path is valid, False otherwise."""
        if isinstance(path, pxr.Sdf.Path):
            return True
        else:
            return False

    def path_to_int(self, path: pxr.Sdf.Path) -> int:
        """Converts the given SDF path to an integer representation.

        Args:
            path (:obj:`Sdf.Path`): The SDF path to convert.

        Returns:
            int: The integer representation of the path."""
        return -1

    def is_a_xformable(self, prim: pxr.Usd.Prim) -> bool:
        """Checks if the given prim is a Xformable type.

        Args:
            prim (:obj:`Usd.Prim`): The prim to check.

        Returns:
            bool: True if the prim is a Xformable, False otherwise."""
        return prim.IsA(pxr.UsdGeom.Xformable)

    def has_prim_at_path(self, path: pxr.Sdf.Path) -> bool:
        """Checks if there is a prim at the specified path.

        Args:
            path (:obj:`Sdf.Path`): The path to check.

        Returns:
            bool: True if there is a prim, False otherwise."""
        prim = self._stage.GetPrimAtPath(path)
        if prim is not None and prim.IsValid():
            return True
        else:
            return False

    def get_prim_at_path(self, path: pxr.Sdf.Path) -> pxr.Usd.Prim:
        """Retrieves the prim at the specified path.

        Args:
            path (:obj:`Sdf.Path`): The path where the prim is located.

        Returns:
            :obj:`Usd.Prim`: The prim at the given path."""
        return self._stage.GetPrimAtPath(path)

    def to_pxr_path(self, path: Union[usdrt.Sdf.Path, pxr.Sdf.Path]) -> pxr.Sdf.Path:
        """Converts given path to pxr.Sdf.Path format.

        Args:
            path (Union[usdrt.Sdf.Path, pxr.Sdf.Path]): The path to convert.

        Returns:
            pxr.Sdf.Path: The converted path in pxr.Sdf.Path format."""
        if isinstance(path, pxr.Sdf.Path):
            return path
        else:
            return pxr.Sdf.Path(str(path))

    def prim_has_prefix(self, path: pxr.Sdf.Path, prim_path: pxr.Sdf.Path) -> bool:
        """Checks if the given path has the specified prefix.

        Args:
            path (pxr.Sdf.Path): The path to check.
            prim_path (pxr.Sdf.Path): The prefix to look for.

        Returns:
            bool: True if path has the prefix, False otherwise."""
        path0 = self.to_pxr_path(path)
        return path0.HasPrefix(self.to_pxr_path(prim_path))

    def get_current_time_code(self, currentTime: float) -> pxr.Usd.TimeCode:
        """Gets the current time code based on given currentTime.

        Args:
            currentTime (float): The current time to convert to time code.

        Returns:
            pxr.Usd.TimeCode: The time code corresponding to the given currentTime."""
        return self.Usd.TimeCode(omni.usd.get_frame_time_code(currentTime, self._stage.GetTimeCodesPerSecond()))

    def get_local_transform_SRT(
        self, prim: pxr.Usd.Prim, time: float = None
    ) -> Tuple[usdrt.Gf.Vec3d, usdrt.Gf.Vec3d, usdrt.Gf.Vec3i, usdrt.Gf.Vec3d]:
        """Gets the local transform SRT (scale, rotate, translate) of a prim at a given time.

        Args:
            prim (pxr.Usd.Prim): The prim to get the transform of.
            time (float): The time at which to get the transform.

        Returns:
            Tuple[usdrt.Gf.Vec3d, usdrt.Gf.Vec3d, usdrt.Gf.Vec3i, usdrt.Gf.Vec3d]: The SRT values."""
        time_code = self.get_current_time_code(time)
        (s, r, ro, t) = omni.usd.get_local_transform_SRT(prim, time_code)
        return (usdrt.Gf.Vec3d(s), usdrt.Gf.Vec3d(r), usdrt.Gf.Vec3i(ro), usdrt.Gf.Vec3d(t))

    # xform cache
    def get_local_to_world_transform(self, prim: pxr.Usd.Prim) -> usdrt.Gf.Matrix4d:
        """Gets the local to world transform matrix of a prim.

        Args:
            prim (pxr.Usd.Prim): The prim to get the transform of.

        Returns:
            usdrt.Gf.Matrix4d: The local to world transform matrix."""
        return usdrt.Gf.Matrix4d(self._xform_cache.GetLocalToWorldTransform(prim))

    def get_parent_to_world_transform(self, prim: pxr.Usd.Prim) -> usdrt.Gf.Matrix4d:
        """Gets the parent to world transform matrix of a prim.

        Args:
            prim (pxr.Usd.Prim): The prim to get the transform of.

        Returns:
            usdrt.Gf.Matrix4d: The parent to world transform matrix."""
        return usdrt.Gf.Matrix4d(self._xform_cache.GetParentToWorldTransform(prim))

    def clear_xform_cache(self):
        """Clears the transform cache."""
        self._xform_cache.Clear()

    def free_xform_cache(self):
        """Frees the transform cache."""
        self._xform_cache = None

    def xform_set_time(self):
        """Updates the transform cache to the current time."""
        self._xform_cache.SetTime(self.get_current_time_code(self._model._current_time))

    def update_xform_cache(self):
        """Updates the transform cache with the current time and stage."""
        if hasattr(self._model, "_current_time") and self._stage:
            self._xform_cache = pxr.UsdGeom.XformCache(self.get_current_time_code(self._model._current_time))

    # stage
    def free_stage(self):
        """Frees the current Usd.Stage."""
        self._stage = None

    def get_stage(self):
        """Returns the current Usd.Stage.

        Returns:
            The current Usd.Stage."""
        return self._stage

    def set_stage(self) -> pxr.Usd.Stage:
        """Sets the current stage to the USD context's stage."""
        self._stage = self._usd_context.get_stage()

    # callbacks
    def setup_update_callback(self) -> pxr.Tf.Listener:
        """Sets up a callback for USD object changes."""
        res = self.Tf.Notice.Register(self.Usd.Notice.ObjectsChanged, self._on_objects_changed, self._stage)
        carb.log_info("Tf.Notice.Register in PrimTransformModel USD")
        return res

    def remove_update_callback(self, listener: pxr.Tf.Listener) -> pxr.Tf.Listener:
        """Removes the update callback.

        Args:
            listener (pxr.Tf.Listener): The listener to remove."""
        listener.Revoke()
        carb.log_info("Tf.Notice.Revoke in PrimTransformModel")
        return None

    def _on_objects_changed(self, notice, sender):
        resynced_paths = notice.GetResyncedPaths()
        changed_info_only_paths = notice.GetChangedInfoOnlyPaths()
        self._model.on_objects_changed(resynced_paths, changed_info_only_paths, data_source="USD")

    def setup_update_callback_ref_prim_maker(
        self,
        func: Callable[
            [List, List[Union[usdrt.Sdf.Path, pxr.Sdf.Path]], List[Union[usdrt.Sdf.Path, pxr.Sdf.Path]], str], None
        ],
    ) -> pxr.Tf.Listener:
        """Sets up a callback for reference prim maker.

        Args:
            func (Callable): The function to call on update."""
        res = self.Tf.Notice.Register(
            self.Usd.Notice.ObjectsChanged, self._on_objects_changed_ref_prim_maker, self._stage
        )
        self._func_ref_prim_maker = func
        carb.log_info("Tf.Notice.Register in PrimTransformModel USD for ref prim maker")
        return res

    def remove_update_callback_ref_prim_maker(self, listener: pxr.Tf.Listener):
        """Removes the update callback for reference prim maker.

        Args:
            listener (pxr.Tf.Listener): The listener to remove."""
        listener.Revoke()
        self._func_ref_prim_maker = None
        carb.log_info("Tf.Notice.Revoke in PrimTransformModel for ref prim maker")
        return None

    def _on_objects_changed_ref_prim_maker(self, notice, sender):
        resynced_paths = notice.GetResyncedPaths()
        changed_info_only_paths = notice.GetChangedInfoOnlyPaths()
        self._func_ref_prim_maker(resynced_paths, changed_info_only_paths, data_source="USD")

    # USD specific commands
    def do_transform_all_selected_prims_to_manipulator_pivot(
        self,
        paths: List[str],
        paths_c: List[int],
        new_translations: List[float],
        new_rotation_eulers: List[float],
        new_rotation_orders: List[int],
        new_scales: List[float],
    ):
        """Transforms all selected prims to the manipulator pivot.

        Args:
            paths (List[str]): Paths to the prims to transform.
            paths_c (List[int]): Component counts of the paths.
            new_translations (List[float]): New translations for the prims.
            new_rotation_eulers (List[float]): New rotation Eulers for the prims.
            new_rotation_orders (List[int]): New rotation orders for the prims.
            new_scales (List[float]): New scales for the prims."""
        paths_str = []
        for path in paths:
            paths_str.append(str(path))
        omni.kit.commands.create(
            "TransformMultiPrimsSRTCpp",
            count=len(paths_str),
            no_undo=True,
            paths=paths_str,
            new_translations=new_translations,
            new_rotation_eulers=new_rotation_eulers,
            new_rotation_orders=new_rotation_orders,
            new_scales=new_scales,
            usd_context_name=self._usd_context_name,
            time_code=self.get_current_time_code(self._model._current_time).GetValue(),
        ).do()

    def do_transform_selected_prims(
        self,
        paths: List[str],
        paths_c: List[int],
        new_translations: List[float],
        new_rotation_eulers: List[float],
        new_rotation_orders: List[int],
        new_scales: List[float],
    ):
        """Transforms selected prims.

        Args:
            paths (List[str]): Paths to the prims to transform.
            paths_c (List[int]): Component counts of the paths.
            new_translations (List[float]): New translations for the prims.
            new_rotation_eulers (List[float]): New rotation Eulers for the prims.
            new_rotation_orders (List[int]): New rotation orders for the prims.
            new_scales (List[float]): New scales for the prims."""
        # paths_str = []
        # for path in paths:
        #     paths_str.append(str(path))
        omni.kit.commands.create(
            "TransformMultiPrimsSRTCpp",
            count=len(paths),
            no_undo=True,
            paths=paths,
            new_translations=new_translations,
            new_rotation_eulers=new_rotation_eulers,
            new_rotation_orders=new_rotation_orders,
            new_scales=new_scales,
            usd_context_name=self._usd_context_name,
            time_code=self.get_current_time_code(self._model._current_time).GetValue(),
        ).do()

    def on_ended_transform(
        self,
        paths: List[pxr.Sdf.Path],
        paths_c: List[int],
        new_translations: List[float],
        new_rotation_eulers: List[float],
        new_rotation_orders: List[int],
        new_scales: List[float],
        old_translations: List[float],
        old_rotation_eulers: List[float],
        old_rotation_orders: List[int],
        old_scales: List[float],
    ):
        """Handles the end of a transformation operation.

        Args:
            paths (List[pxr.Sdf.Path]): Paths to the prims that were transformed.
            paths_c (List[int]): Component counts of the paths.
            new_translations (List[float]): New translations for the prims.
            new_rotation_eulers (List[float]): New rotation Eulers for the prims.
            new_rotation_orders (List[int]): New rotation orders for the prims.
            new_scales (List[float]): New scales for the prims.
            old_translations (List[float]): Previous translations for the prims.
            old_rotation_eulers (List[float]): Previous rotation Eulers for the prims.
            old_rotation_orders (List[int]): Previous rotation orders for the prims.
            old_scales (List[float]): Previous scales for the prims."""
        paths_str = []
        for path in paths:
            paths_str.append(str(path))
        omni.kit.commands.execute(
            "TransformMultiPrimsSRTCpp",
            count=len(paths_str),
            paths=paths_str,
            new_translations=new_translations,
            new_rotation_eulers=new_rotation_eulers,
            new_rotation_orders=new_rotation_orders,
            new_scales=new_scales,
            old_translations=old_translations,
            old_rotation_eulers=old_rotation_eulers,
            old_rotation_orders=old_rotation_orders,
            old_scales=old_scales,
            usd_context_name=self._usd_context_name,
            time_code=self.get_current_time_code(self._model._current_time).GetValue(),
        )

    def get_local_transform_pivot_inv(self, prim: pxr.Usd.Prim, time: float = None) -> usdrt.Gf.Matrix4d:
        """Computes the inverse of the local transformation pivot matrix.

        Args:
            prim (:obj:`pxr.Usd.Prim`): The primitive to compute the local transformation pivot for.
            time (float, optional): The time at which to compute the pivot.

        Returns:
            :obj:`usdrt.Gf.Matrix4d`: The inverse of the local transformation pivot matrix."""
        if time == None:
            time_code = pxr.Usd.TimeCode
        else:
            time_code = self.get_current_time_code(time)
        xform = pxr.UsdGeom.Xformable(prim)
        xform_ops = xform.GetOrderedXformOps()
        if len(xform_ops):
            pivot_op_inv = xform_ops[-1]
            if (
                pivot_op_inv.GetOpType() == pxr.UsdGeom.XformOp.TypeTranslate
                and pivot_op_inv.IsInverseOp()
                and pivot_op_inv.GetName().endswith("pivot")
            ):
                return usdrt.Gf.Matrix4d(pivot_op_inv.GetOpTransform(time_code))
        return usdrt.Gf.Matrix4d(1.0)
