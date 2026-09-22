# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from __future__ import annotations

__all__ = ["FabricDataAccessor"]

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
import pxr.Tf
import pxr.Usd
import usdrt.Gf
import usdrt.hierarchy
import usdrt.Sdf
import usdrt.Usd
import usdrt.UsdGeom
from carb.eventdispatcher import get_eventdispatcher
from omni.kit.manipulator.prim.core import DataAccessorConstants as da_c

# from omni.kit.viewport.manipulator.transform import DataAccessor
from omni.ui import scene as sc


class FabricDataAccessor:  # (DataAccessor):
    """A class for accessing and manipulating USD (Universal Scene Description) data in a fabric.

    This class handles the retrieval and alteration of scene graph information, including transformation matrices, stage access, and USD prim manipulation. It is designed to work within a fabric-based USD runtime and provides a range of methods to interact with USD stages and prims.

    Args:
        usd_context_name (str): The name of the USD context to associate with this data accessor. An empty string indicates no specific context.
        model: The model associated with the data accessor. The exact type of the model is not specified.

    This class also handles update callbacks for changes in the USD stage and provides utility functions for converting between different path and transform representations.
    """

    from usdrt import Rt, Sdf, Usd, UsdGeom, Vt

    def __init__(self, usd_context_name: str = "", model=None):
        """Constructor for FabricDataAccessor.

        Initializes a new instance of the FabricDataAccessor with optional USD context and model."""
        super().__init__()
        self._settings = carb.settings.get_settings()
        self._xform_cache = None
        self._stage: self.Usd.Stage = None
        self._stage_id = None
        self._stageUSD: pxr.Usd.Stage = None
        self._hier = None
        self._change_tracker = None
        self._change_tracker_ref_prim_maker = None
        self._change_tracker_ref_prim_maker_func = None
        self._usd_context = None
        self._property_listener = get_eventdispatcher().observe_event(
            event_name=omni.kit.app.GLOBAL_EVENT_UPDATE,
            on_event=self._on_tick,
            observer_name="omni.kit.manipulator.prim data_accessor Fabric update",
        )
        self._model = model
        self._usd_context_name = usd_context_name
        self._usd_context = omni.usd.get_context(self._usd_context_name)
        self._priority = 1
        self._priority_write = 2
        if self._settings.get(da_c.DATA_ACCESSOR_PRIORITY_FABRIC) != None:
            self._priority = int(self._settings.get(da_c.DATA_ACCESSOR_PRIORITY_FABRIC))
        if self._settings.get(da_c.DATA_ACCESSOR_PRIORITY_WRITE_FABRIC) != None:
            self._priority_write = int(self._settings.get(da_c.DATA_ACCESSOR_PRIORITY_WRITE_FABRIC))

        self.set_stage()

    def destroy(self):
        """Cleans up resources and references held by the FabricDataAccessor instance."""
        self._model = None
        self._usd_context_name = None
        self._usd_context = None
        self._inited = False
        if self._change_tracker != None:
            self.remove_update_callback()
        if self._change_tracker_ref_prim_maker != None:
            self.remove_update_callback_ref_prim_maker()
        self._priority = -1
        self._priority_write = -1
        self._property_listener = None
        # self._settings.destroy_item(da_c.DATA_ACCESSOR_PRIORITY_FABRIC)

    def get_sdf_path_type(self) -> type:
        """Returns the type associated with Sdf paths used in FabricDataAccessor.

        Returns:
            type: The Sdf path type used by FabricDataAccessor."""
        return usdrt.Sdf.Path

    def get_data_tag(self) -> str:
        """Gets the data tag that identifies FabricDataAccessor.

        Returns:
            str: The data tag for FabricDataAccessor."""
        return "FABRIC"

    @property
    def priority(self) -> int:
        """Gets the priority value of the FabricDataAccessor.

        Returns:
            int: The priority value."""
        return self._priority

    @property
    def priority_write(self) -> int:
        """Gets the write priority value of the FabricDataAccessor.

        Returns:
            int: The write priority value."""
        return self._priority_write

    @property
    def is_inited(self):
        """Gets the initialization status of the FabricDataAccessor.

        Returns:
            bool: The initialization status."""
        return self._inited

    @property
    def usd_context(self):
        """Gets the USD context associated with the FabricDataAccessor.

        Returns:
            omni.usd.UsdContext: The USD context."""
        return self._usd_context

    def is_transformation_affected_by_attr_named(self, sdf_path: usdrt.Sdf.Path) -> bool:
        """Checks if transformation is affected by a specific attribute.

        Args:
            sdf_path (:obj:`usdrt.Sdf.Path`): The Sdf path to check.

        Returns:
            bool: True if transformation is affected, False otherwise."""
        return True  # pxr.UsdGeom.Xformable.IsTransformationAffectedByAttrNamed(name)

    def is_instance_proxy(self, prim: usdrt.Usd.Prim) -> bool:
        """Determines if the provided prim is an instance proxy.

        Args:
            prim (:obj:`usdrt.Usd.Prim`): The prim to check.

        Returns:
            bool: True if it is an instance proxy, False otherwise."""
        return False

    def get_stage_up_axis(self) -> str:
        """Retrieves the up-axis of the stage.

        Returns:
            str: The up-axis of the stage."""
        return pxr.UsdGeom.GetStageUpAxis(self._stageUSD)

    def remove_descendent_paths(self, paths: List[usdrt.Sdf.Path]) -> List[usdrt.Sdf.Path]:
        """Removes descendent paths from a list of paths.

        Args:
            paths (List[:obj:`usdrt.Sdf.Path`]): The list of paths to process.

        Returns:
            List[:obj:`usdrt.Sdf.Path`]: The list of paths without descendents."""
        pxrPaths = [self.to_pxr_path(path) for path in paths]
        fixedPaths = pxr.Sdf.Path.RemoveDescendentPaths(pxrPaths)
        usdrtPaths = [self._to_usdrt_path(path) for path in fixedPaths]
        return usdrtPaths

    def is_prim_active(self, prim: usdrt.Usd.Prim) -> bool:
        """Determines if the provided prim is active.

        Args:
            prim (:obj:`usdrt.Usd.Prim`): The prim to check.

        Returns:
            bool: True if the prim is active, False otherwise."""
        return True

    def get_sdf_path(self, path: usdrt.Sdf.Path) -> usdrt.Sdf.Path:
        """Returns the Sdf path for the given path.

        Args:
            path (:obj:`usdrt.Sdf.Path`): The path to resolve.

        Returns:
            :obj:`usdrt.Sdf.Path`: The resolved Sdf path."""
        res = self._to_usdrt_path(path)
        return res

    def get_string_path(self, path: Union[usdrt.Sdf.Path, str]) -> str:
        """Converts an Sdf path to its string representation.

        Args:
            path (Union[:obj:`usdrt.Sdf.Path`, str]): The path to convert.

        Returns:
            str: The string representation of the path."""
        return str(path)

    def is_valid_path(self, path: Any) -> bool:
        """Determines if the given path is a valid Sdf path.

        Args:
            path (Any): The path to validate.

        Returns:
            bool: True if the path is valid, False otherwise."""
        if isinstance(path, usdrt.Sdf._Sdf.Path):
            return True
        else:
            return False

    def path_to_int(self, path: usdrt.Sdf.Path) -> int:
        """Converts an Sdf path to an integer representation.

        Args:
            path (:obj:`usdrt.Sdf.Path`): The path to convert.

        Returns:
            int: The integer representation of the path."""
        return path.pathC.path

    def to_pxr_path(self, path: Union[usdrt.Sdf.Path, pxr.Sdf.Path]) -> pxr.Sdf.Path:
        """Converts a path to a pxr.Sdf.Path type.

        Args:
            path (Union[:obj:`usdrt.Sdf.Path`, pxr.Sdf.Path]): The path to convert.

        Returns:
            pxr.Sdf.Path: The converted pxr path."""
        if isinstance(path, pxr.Sdf.Path):
            return path
        else:
            return pxr.Sdf.Path(str(path))

    def _to_usdrt_path(self, path: Union[usdrt.Sdf.Path, pxr.Sdf.Path]) -> usdrt.Sdf.Path:
        if isinstance(path, usdrt.Sdf._Sdf.Path):
            return path
        else:
            return usdrt.Sdf.Path(str(path))

    def is_a_xformable(self, prim: usdrt.Usd.Prim) -> bool:
        """Determines if the provided prim is a xformable prim.

        Args:
            prim (:obj:`usdrt.Usd.Prim`): The prim to check.

        Returns:
            bool: True if it's a xformable prim, False otherwise."""
        return prim.IsA(usdrt.UsdGeom.Xformable) and prim.HasAttribute("omni:fabric:localMatrix")

    def has_prim_at_path(self, path: usdrt.Sdf.Path) -> bool:
        """Checks if a prim exists at the given path.

        Args:
            path (:obj:`usdrt.Sdf.Path`): The path to check.

        Returns:
            bool: True if a prim exists at the path, False otherwise."""
        # Warning: when FSD = false, HasPrimAtPath may return false in certain cases
        res = self._stage.HasPrimAtPath(path)
        return res

    def get_prim_at_path(self, path: usdrt.Sdf.Path) -> usdrt.Usd.Prim:
        """Returns the USD Prim at the specified path.

        Args:
            path (:obj:`usdrt.Sdf.Path`): The path to the USD Prim.

        Returns:
            usdrt.Usd.Prim: The USD Prim at the given path."""
        return self._stage.GetPrimAtPath(path)

    def prim_has_prefix(self, path: usdrt.Sdf.Path, prim_path: usdrt.Sdf.Path) -> bool:
        """Checks if the given path has the specified prefix.

        Args:
            path (:obj:`usdrt.Sdf.Path`): The path to check for the prefix.
            prim_path (:obj:`usdrt.Sdf.Path`): The prefix to check against the path.

        Returns:
            bool: True if the path has the prefix, False otherwise."""
        path0 = self._to_usdrt_path(path)
        prim_path0 = self._to_usdrt_path(prim_path)
        return path0.HasPrefix(prim_path0)

    def get_current_time_code(self, currentTime: float) -> usdrt.Usd.TimeCode:
        """Gets the current time code.

        Args:
            currentTime (float): The current time to get the time code for.

        Returns:
            usdrt.Usd.TimeCode: The current time code."""
        if currentTime is None:
            return usdrt.Usd.TimeCode.Default()

        return usdrt.Usd.TimeCode(omni.usd.get_frame_time_code(currentTime, self._stageUSD.GetTimeCodesPerSecond()))

    def _euler_from_quaternion(self, q: usdrt.Gf.Quatd, axes: List[usdrt.Gf.Vec3d]) -> List[float]:
        # TODO: add rotation order when/if USDRT supports it
        rot = usdrt.Gf.Rotation(q)
        eulers = rot.Decompose(*axes)
        # round epsilons from decompose
        eulers = [round(angle + 1e-4, 3) for angle in eulers]
        return eulers

    def get_local_transform_SRT(
        self, prim: usdrt.Usd.Prim, time: float = None
    ) -> Tuple[usdrt.Gf.Vec3d, usdrt.Gf.Vec3d, usdrt.Gf.Vec3i, usdrt.Gf.Vec3d]:
        """Gets the local transform SRT (scale, rotation, translation) of the USD Prim.

        Args:
            prim (:obj:`usdrt.Usd.Prim`): The USD Prim to get the transform for.
            time (float): The time at which to evaluate the transform.

        Returns:
            Tuple[usdrt.Gf.Vec3d, usdrt.Gf.Vec3d, usdrt.Gf.Vec3i, usdrt.Gf.Vec3d]: The SRT components of the transform.
        """
        if self._hier:
            local_mtx = self._hier.get_local_xform(prim.GetPath())
        else:
            local_mtx = usdrt.Gf.Matrix4d(1)

        _, _, s, rot_mat, t, _ = local_mtx.Factor()
        rot = rot_mat.ExtractRotation()

        r = rot.Decompose(usdrt.Gf.Vec3d.XAxis(), usdrt.Gf.Vec3d.YAxis(), usdrt.Gf.Vec3d.ZAxis())
        ro = usdrt.Gf.Vec3i(2, 1, 0)
        return (s, r, ro, t)

    def _get_local_transform_matrix(self, prim: usdrt.Usd.Prim, time: float = None) -> usdrt.Gf.Matrix4d:
        if self._hier:
            local_mtx = self._hier.get_local_xform(prim.GetPath())
        else:
            local_mtx = usdrt.Gf.Matrix4d(1)

        return local_mtx

    def _construct_transfrom_matrix_from_SQT(
        self, t: usdrt.Gf.Vec3d, q: usdrt.Gf.Quatd, scale: usdrt.Gf.Vec3d
    ) -> usdrt.Gf.Matrix4d:
        trans_mtx = usdrt.Gf.Matrix4d()
        rot_mtx = usdrt.Gf.Matrix4d()
        scale_mtx = usdrt.Gf.Matrix4d()
        trans_mtx.SetTranslate(t)
        rot_mtx.SetRotate(q)
        scale_mtx.SetScale(scale)
        return scale_mtx * rot_mtx * trans_mtx

    def get_local_to_world_transform(self, prim: usdrt.Usd.Prim) -> usdrt.Gf.Matrix4d:
        """Gets the local-to-world transform matrix of the USD Prim.

        Args:
            prim (:obj:`usdrt.Usd.Prim`): The USD Prim to get the transform for.

        Returns:
            usdrt.Gf.Matrix4d: The local-to-world transform matrix."""
        if self._hier:
            return self._hier.get_world_xform(prim.GetPath())
        else:
            return usdrt.Gf.Matrix4d(1)

    def get_parent_to_world_transform(self, prim: usdrt.Usd.Prim) -> usdrt.Gf.Matrix4d:
        """Gets the parent-to-world transform matrix of the USD Prim.

        Args:
            prim (:obj:`usdrt.Usd.Prim`): The USD Prim to get the transform for.

        Returns:
            usdrt.Gf.Matrix4d: The parent-to-world transform matrix."""
        parent = prim.GetParent()
        if parent and self._hier:
            return self._hier.get_world_xform(parent.GetPath())
        else:
            return usdrt.Gf.Matrix4d(1)

    # TODO: wait for iFabricHierarchy
    def clear_xform_cache(self):
        """Clears the transform cache."""
        pass

    # TODO: wait for iFabricHierarchy
    def free_xform_cache(self):
        """Frees the transform cache."""
        self._xform_cache = None

    # TODO: wait for iFabricHierarchy
    def xform_set_time(self):
        """Sets the time for the transform cache."""
        pass

    # TODO: wait for iFabricHierarchy
    def update_xform_cache(self):
        """Updates the transform cache."""
        pass

    # stage
    def free_stage(self):
        """Frees the USD stage."""
        self._stage = None

    def get_stage(self) -> usdrt.Usd.Stage:
        """Gets the USD stage.

        Returns:
            usdrt.Usd.Stage: The USD stage."""
        return self._stage

    def set_stage(self):
        """Sets the USD stage."""
        self._stage_id = self._usd_context.get_stage_id()
        if self._stage_id > 0:
            self._stage = usdrt.Usd.Stage.Attach(self._stage_id)
            fabric_id = self._stage.GetFabricId()
            stage_id = self._stage.GetStageIdAsStageId()
            self._hier = usdrt.hierarchy.IFabricHierarchy().get_fabric_hierarchy(fabric_id, stage_id)

        self._stageUSD = self._usd_context.get_stage()

    # callbacks
    def setup_update_callback(self) -> usdrt.Rt.ChangeTracker:
        """Sets up the update callback for changes.

        Returns:
            usdrt.Rt.ChangeTracker: The change tracker instance."""
        carb.log_info("usdrt.Rt.ChangeTracker in omni.kit.manipulator.prim data accessor Fabric")
        self._change_tracker = usdrt.Rt.ChangeTracker(self._stage)
        self._change_tracker.TrackAttribute("omni:fabric:localMatrix")
        return self._change_tracker

    def remove_update_callback(self, listener: pxr.Tf.Listener = None) -> usdrt.Rt.ChangeTracker:
        """Removes the update callback for changes.

        Args:
            listener (Optional[:obj:`pxr.Tf.Listener`]): The listener to remove.

        Returns:
            usdrt.Rt.ChangeTracker: None, indicating the callback has been removed."""
        if self._change_tracker != None:
            carb.log_info("usdrt.Rt.ChangeTracker in omni.kit.manipulator.prim data accessor Fabric remove")
            self._change_tracker.StopTrackingAttribute("omni:fabric:localMatrix")
            self._change_tracker = None
        return None

    def setup_update_callback_ref_prim_maker(
        self,
        func: Callable[
            [List, List[Union[usdrt.Sdf.Path, pxr.Sdf.Path]], List[Union[usdrt.Sdf.Path, pxr.Sdf.Path]], str], None
        ],
    ) -> usdrt.Rt.ChangeTracker:
        """Sets up the update callback with a reference to the prim maker function.

        Args:
            func (Callable): The function to call when changes occur.

        Returns:
            usdrt.Rt.ChangeTracker: The change tracker instance."""
        carb.log_info("usdrt.Rt.ChangeTracker in omni.kit.manipulator.prim data accessor Fabric for ref prim maker")
        self._change_tracker_ref_prim_maker = usdrt.Rt.ChangeTracker(self._stage)
        self._change_tracker_ref_prim_maker.TrackAttribute("omni:fabric:localMatrix")
        self._change_tracker_ref_prim_maker_func = func
        return self._change_tracker_ref_prim_maker

    def remove_update_callback_ref_prim_maker(self, listener: pxr.Tf.Listener = None) -> usdrt.Rt.ChangeTracker:
        """Removes the update callback reference to the prim maker.

        Args:
            listener (Optional[:obj:`pxr.Tf.Listener`]): The listener to remove.

        Returns:
            usdrt.Rt.ChangeTracker: None, indicating the callback has been removed."""
        if self._change_tracker_ref_prim_maker != None:
            carb.log_info(
                "usdrt.Rt.ChangeTracker in omni.kit.manipulator.prim data accessor Fabric remove for ref prim maker"
            )
            self._change_tracker_ref_prim_maker.StopTrackingAttribute("omni:fabric:localMatrix")
            self._change_tracker_ref_prim_maker = None
            self._change_tracker_ref_prim_maker_func = None
        return None

    def _on_tick(self, _):
        self.update_changes()

    def update_changes(self):
        """Updates changes in the USD stage."""
        if self._change_tracker:
            if self._change_tracker.HasChanges():
                prim_paths_tmp = self._change_tracker.GetAllChangedPrims()
                self._change_tracker.ClearChanges()
                if prim_paths_tmp:
                    self._model.on_objects_changed([], prim_paths_tmp, data_source="FABRIC")

        if self._change_tracker_ref_prim_maker:
            if self._change_tracker_ref_prim_maker.HasChanges():
                prim_paths_tmp = self._change_tracker_ref_prim_maker.GetAllChangedPrims()
                self._change_tracker_ref_prim_maker.ClearChanges()
                if prim_paths_tmp:
                    self._change_tracker_ref_prim_maker_func([], prim_paths_tmp, data_source="FABRIC")

    # Fabric specific commands
    def do_transform_all_selected_prims_to_manipulator_pivot(
        self,
        paths: List[str],
        paths_c: List[int],
        new_translations: List[float],
        new_rotation_eulers: List[float],
        new_rotation_orders: List[int],
        new_scales: List[float],
    ):
        """Transforms all selected prims to manipulator pivot.

        Args:
            paths (List[str]): List of path strings for selected prims.
            paths_c (List[int]): List of path hashes for selected prims.
            new_translations (List[float]): List of new translation values for prims.
            new_rotation_eulers (List[float]): List of new rotation euler angles for prims.
            new_rotation_orders (List[int]): List of new rotation orders for prims.
            new_scales (List[float]): List of new scale values for prims."""
        # path_str = [str(path) for path in paths]

        omni.kit.commands.create(
            "TransformMultiPrimsSRTFabricCpp",
            count=len(paths_c),
            fabric_stage_id=self._stage_id,
            no_undo=True,
            paths=paths_c,
            new_translations=new_translations,
            new_rotation_eulers=new_rotation_eulers,
            new_rotation_orders=new_rotation_orders,
            new_scales=new_scales,
        ).do()
        # self.update_changes()

    def do_transform_selected_prims(
        self,
        paths: List[str],
        paths_c: List[int],
        new_translations: List[float],
        new_rotation_eulers: List[float],
        new_rotation_orders: List[int],
        new_scales: List[float],
    ):
        """Transforms selected prims with the given transformations.

        Args:
            paths (List[str]): List of path strings for selected prims.
            paths_c (List[int]): List of path hashes for selected prims.
            new_translations (List[float]): List of new translation values for prims.
            new_rotation_eulers (List[float]): List of new rotation euler angles for prims.
            new_rotation_orders (List[int]): List of new rotation orders for prims.
            new_scales (List[float]): List of new scale values for prims."""
        omni.kit.commands.create(
            "TransformMultiPrimsSRTFabricCpp",
            count=len(paths_c),
            fabric_stage_id=self._stage_id,
            no_undo=True,
            paths=paths_c,
            new_translations=new_translations,
            new_rotation_eulers=new_rotation_eulers,
            new_rotation_orders=new_rotation_orders,
            new_scales=new_scales,
        ).do()
        self.update_changes()

    def on_ended_transform(
        self,
        paths: List[str],
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
        """Applies transformations to multiple prims.

        Args:
            paths (List[str]): Paths of prims to transform.
            paths_c (List[int]): C++ compatible path representation.
            new_translations (List[float]): New translations for the prims.
            new_rotation_eulers (List[float]): New rotation angles in Euler form.
            new_rotation_orders (List[int]): New rotation orders for the prims.
            new_scales (List[float]): New scale values for the prims.
            old_translations (List[float]): Previous translations for undo functionality.
            old_rotation_eulers (List[float]): Previous rotations in Euler form for undo.
            old_rotation_orders (List[int]): Previous rotation orders for undo functionality.
            old_scales (List[float]): Previous scale values for undo functionality."""
        # path_str = [str(path) for path in paths]
        omni.kit.commands.execute(
            "TransformMultiPrimsSRTFabricCpp",
            count=len(paths_c),
            fabric_stage_id=self._stage_id,
            paths=paths_c,
            new_translations=new_translations,
            new_rotation_eulers=new_rotation_eulers,
            new_rotation_orders=new_rotation_orders,
            new_scales=new_scales,
            old_translations=old_translations,
            old_rotation_eulers=old_rotation_eulers,
            old_rotation_orders=old_rotation_orders,
            old_scales=old_scales,
        )
        # self.update_changes()

    def get_local_transform_pivot_inv(self, prim: usdrt.Usd.Prim, time: float = None) -> usdrt.Gf.Matrix4d:
        """Returns the inverse of the local transformation pivot for a given prim.

        Args:
            prim (:obj:`Usd.Prim`): The prim to calculate the inverse transform for.
            time (float, optional): The time at which to evaluate the transformation.

        Returns:
            :obj:`Gf.Matrix4d`: The inverse of the local transformation matrix."""
        return usdrt.Gf.Matrix4d(1.0)
