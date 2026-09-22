# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""This module provides classes and functionality for managing data accessors and transforming USD prims within the Omniverse Kit."""


from __future__ import annotations

from typing import Callable, Dict, List, Sequence, Set, Tuple, Union

import carb.events
import carb.profiler
import carb.settings
import omni.kit
import omni.kit.app
import pxr.Sdf
import usdrt.Gf
import usdrt.Sdf

from .global_registry import get_prim_data_accessor_registry
from .settings_constants import DataAccessorConstants as da_c
from .settings_constants import DataRegistryEventTypes as da_ev_c


class TransformData:
    """A class for storing transformation data for USD prims.

    This class holds lists of transformation-related data such as paths, translations, rotations, scales, and their old values before the transformation. It is intended to be used by higher-level classes or functions performing transformations on USD prims to keep track of the initial and resulting state of each transformed prim.
    """

    def __init__(self):
        """Initializes the TransformData instance."""
        self.paths = []
        self.paths_c = []
        self.new_translations = []
        self.new_rotation_eulers = []
        self.new_rotation_orders = []
        self.new_scales = []
        self.old_translations = []
        self.old_rotation_eulers = []
        self.old_rotation_orders = []
        self.old_scales = []


class PrimDataAccessorSelector:
    """A class to select and manage data accessors for USD prims.

    This class is responsible for storing and managing different data accessors for prims in a USD scene. It allows for
    the retrieval and modification of prim data based on the type of data accessor. The class also handles
    registration for data accessor changes and updates the transformations of selected prims.

    Args:
        model: The model associated with the data accessors.
        usd_context_name (str): The name of the USD context to be used. Defaults to an empty string.
        dataTypes (List[str]): A list of data types that the data accessor should handle. Defaults to ['FABRIC', 'USD'].
    """

    def __init__(self, model, usd_context_name="", dataTypes=["FABRIC", "USD"]):
        """Constructor for PrimDataAccessorSelector."""
        self._model = model
        self._usd_context_name = usd_context_name
        self._usd_context = omni.usd.get_context(self._usd_context_name)
        self.prim_data_accessor_registry = get_prim_data_accessor_registry()
        self._defType = None  # dataTypes[0]
        self._data_accessors = {}
        self._data_accessors_sorted = []
        self._data_accessors_sorted_w = []
        self._data_types = {}
        self._process()
        self._app = omni.kit.app.get_app()

        self._da_registry_event_stream = self.prim_data_accessor_registry.get_event_stream()
        self._da_change_listener = self._da_registry_event_stream.create_subscription_to_pop(
            self._on_data_accessor_changed
        )

        self._transform_data_map: dict[str, TransformData] = {}
        self._prim_paths_cache = {}
        self._da_prim_cache = {}

    def destroy(self):
        """Destroy the PrimDataAccessorSelector and its resources."""
        self._da_registry_event_stream = None
        self._da_change_listener = None
        self._data_accessor_change_listener = None
        for da in self.get_data_accessors():
            da.destroy()
        self._data_accessors = None
        self._data_accessors_sorted = None

    def _on_data_accessor_changed(self, event: carb.events.IEvent):
        if event.type == da_ev_c.DATA_ACCESSOR_ADDED:
            data_tag = event.payload.get_dict().get("data_tag")
            self._add_data_accessor(data_tag)
            carb.log_info(f"PrimTransformModel._on_data_accessor_changed add: {str(data_tag)}")
        elif event.type == da_ev_c.DATA_ACCESSOR_REMOVED:
            data_tag = event.payload.get_dict().get("data_tag")
            self._remove_data_accessor(data_tag)
            carb.log_info(f"PrimTransformModel._on_data_accessor_changed remove: {str(data_tag)}")

    def _process(self):
        for data_tag in self.prim_data_accessor_registry.get_data_accessors_func():
            data_accessor = self.prim_data_accessor_registry.get_data_accessors_func()[data_tag](
                usd_context_name=self._usd_context_name, model=self._model
            )
            self._data_accessors[data_tag] = data_accessor
            self._data_types[data_accessor.get_sdf_path_type()] = data_tag
        self._upd_data_accessors()

    def _add_data_accessor(self, data_tag: str):
        if data_tag not in self._data_accessors:
            data_accessor = self.prim_data_accessor_registry.get_data_accessors_func()[data_tag](
                usd_context_name=self._usd_context_name, model=self._model
            )
            self._data_accessors[data_tag] = data_accessor
            self._data_types[data_accessor.get_sdf_path_type()] = data_tag
            self._upd_data_accessors()
            self._model.update_selection()

    def _remove_data_accessor(self, data_tag: str):
        if data_tag in self._data_accessors:
            data_accessor = self._data_accessors[data_tag]
            del self._data_types[data_accessor.get_sdf_path_type()]
            data_accessor.destroy()
            del self._data_accessors[data_tag]
            self._upd_data_accessors()
            self._model.update_selection()

    def _upd_data_accessors(self):
        def by_prio(da):
            return da.priority

        def by_prio_w(da):
            return da.priority_write

        self._data_accessors_sorted = list(self._data_accessors.values())
        self._data_accessors_sorted.sort(key=by_prio)
        self._data_accessors_sorted_w = list(self._data_accessors.values())
        self._data_accessors_sorted_w.sort(key=by_prio_w)
        self._set_def_type()
        self.update_xform_cache()

    def _set_def_type(self):
        if len(self.get_data_accessors()) > 0:
            da = self.get_data_accessors()[0]
            self._defType = da.get_data_tag()

    # if omni.kit.manipulator.prim.core is not dependent on prim2.usd/fabric, I can't set type hint of returning value here
    def get_data_accessors(self):
        """Retrieve sorted list of data accessors based on priority."""
        return self._data_accessors_sorted

    def get_data_accessors_write_priority(self):
        """Retrieve list of data accessors sorted by write priority."""
        return self._data_accessors_sorted_w

    def get_data_types(self):
        """Get a mapping of SDF path types to data accessor tags."""
        return self._data_types

    def is_ready(self) -> bool:
        """Check if the data accessor selector is ready for operation."""
        if len(self.get_data_accessors()) > 0:
            return True
        else:
            return False

    def get_sdf_path_by_priority(
        self, sdf_path: Union[usdrt.Sdf.Path, pxr.Sdf.Path]
    ) -> Union[usdrt.Sdf.Path, pxr.Sdf.Path]:
        """Get the SDF path by priority.

        Args:
            sdf_path (Union[usdrt.Sdf.Path, pxr.Sdf.Path]): The SDF path to prioritize."""
        for da in self.get_data_accessors():
            sdf_path_tst = da.get_sdf_path(sdf_path)
            has_prim = da.has_prim_at_path(sdf_path_tst)
            if has_prim:
                return sdf_path_tst

    # if omni.kit.manipulator.prim.core is not dependent on prim2.usd/fabric, I can't set type hint of returning value here
    # def get_data_accessor(self, data_type: str):
    #     if data_type not in self._data_accessors:
    #         carb.log_error(f"PrimDataAccessorSelector get_data_accessor: no {data_type} data accessor")
    #         return None
    #     else:
    #         return self._data_accessors[data_type]

    def get_data_accessor(self, data_type: str):
        """Get the data accessor for a given data type.

        Args:
            data_type (str): The data type to retrieve the accessor for."""
        da = self._data_accessors.get(data_type, None)
        if da is None:
            carb.log_error(f"PrimDataAccessorSelector get_data_accessor: no {data_type} data ")
        return da

    def _prim_data_type(self, prim: Union[usdrt.Usd.Prim, pxr.Usd.Prim]) -> type:
        return self._data_types[type(prim.GetPath())]

    def _sdf_path_data_type(self, path) -> type:
        return self._data_types[type(path)]  # return self.get_data_types()[type(path)]

    def _str_path_data_type(self, path) -> type:
        return self._data_types[type(path)]  # return self.get_data_types()[type(path)]

    def is_sdf_path_in_set(
        self, path: Union[usdrt.Sdf.Path, pxr.Sdf.Path], array=Union[Set, List]
    ) -> Union[usdrt.Usd.Prim, pxr.Usd.Prim]:
        """Check if the SDF path is in a given set or list.

        Args:
            path (Union[usdrt.Sdf.Path, pxr.Sdf.Path]): The path to check.
            array (Union[Set, List]): The set or list to check against."""
        for da in self.get_data_accessors():
            path0 = da.get_sdf_path(path)
            if path0 in array:
                return path0
        return None

    def remove_descendent_paths(self, paths) -> Union[usdrt.Sdf.Path, pxr.Sdf.Path]:
        """Remove descendant paths from a list.

        Args:
            paths (List[Union[usdrt.Sdf.Path, pxr.Sdf.Path]]): The list of paths to process."""
        # Currently selection does not return ordered fabric/all prims
        # workaround to pass tests:
        # return self.get_data_accessor(self._sdf_path_data_type(sdf_path)).remove_descendent_paths(paths)
        # when iFabricHierarchy is done:
        paths_tmp = self.get_data_accessor(self._defType).remove_descendent_paths(paths)
        res = []
        for path in paths_tmp:
            res.append(self.get_sdf_path_by_priority(path))
        return res

    def get_sdf_path(self, sdf_path: Union[usdrt.Sdf.Path, pxr.Sdf.Path]) -> Union[usdrt.Sdf.Path, pxr.Sdf.Path]:
        """Get the SDF path.

        Args:
            sdf_path (Union[usdrt.Sdf.Path, pxr.Sdf.Path]): The SDF path."""
        return self.get_data_accessor(self._defType).get_sdf_path(sdf_path)

    def _get_sdf_path_data_tag(self, sdf_path: Union[usdrt.Sdf.Path, pxr.Sdf.Path]) -> str:
        return self.get_data_accessor(self._sdf_path_data_type(sdf_path)).get_data_tag()

    def get_string_path(self, sdf_path: Union[usdrt.Sdf.Path, pxr.Sdf.Path]) -> str:
        """Get the string representation of an SDF path.

        Args:
            sdf_path (Union[usdrt.Sdf.Path, pxr.Sdf.Path]): The SDF path."""
        return self.get_data_accessor(self._sdf_path_data_type(sdf_path)).get_string_path(sdf_path)

    def has_prim_at_path(self, sdf_path: Union[usdrt.Sdf.Path, pxr.Sdf.Path]) -> bool:
        """Check if a prim exists at the given SDF path.

        Args:
            sdf_path (Union[usdrt.Sdf.Path, pxr.Sdf.Path]): The SDF path to check."""
        return self.get_data_accessor(self._sdf_path_data_type(sdf_path)).has_prim_at_path(sdf_path)

    def cache_prim_data(self, paths):
        """Cache the prim data for the given paths.

        Args:
            paths (List[Union[usdrt.Sdf.Path, pxr.Sdf.Path]]): The list of paths to cache."""
        self._prim_paths_cache = {}
        self._da_prim_cache = {}
        for path in paths:
            prim = self.get_prim_at_path(path)
            self._prim_paths_cache[path] = prim
            self._da_prim_cache[prim] = self.get_data_accessor(self._sdf_path_data_type(path))

    def get_prim_at_path(
        self, sdf_path: Union[usdrt.Sdf.Path, pxr.Sdf.Path], use_cache: bool = False
    ) -> Union[usdrt.Usd.Prim, pxr.Usd.Prim]:
        """Get the prim at the specified SDF path, with optional caching.

        Args:
            sdf_path (Union[usdrt.Sdf.Path, pxr.Sdf.Path]): The SDF path where the prim is located.
            use_cache (bool): Flag to indicate whether to use cached data."""
        # return self.get_data_accessor(self._sdf_path_data_type(sdf_path)).get_prim_at_path(sdf_path)
        if use_cache and sdf_path in self._prim_paths_cache:
            return self._prim_paths_cache[sdf_path]
        else:
            return self._data_accessors[self._data_types[type(sdf_path)]].get_prim_at_path(sdf_path)

    def get_local_transform_SRT(
        self, prim: Union[usdrt.Usd.Prim, pxr.Usd.Prim], time: float
    ) -> Tuple[usdrt.Gf.Vec3d, usdrt.Gf.Vec3d, usdrt.Gf.Vec3i, usdrt.Gf.Vec3d]:
        """Get the local transform SRT (Scale, Rotate, Translate) for a prim at a given time.

        Args:
            prim (Union[usdrt.Usd.Prim, pxr.Usd.Prim]): The prim to get the transform for.
            time (float): The time at which to get the transform."""
        return self.get_data_accessor(self._prim_data_type(prim)).get_local_transform_SRT(prim, time)

    def get_local_to_world_transform(
        self, prim: Union[usdrt.Usd.Prim, pxr.Usd.Prim], use_cache: bool = False
    ) -> usdrt.Gf.Matrix4d:
        """Get the local to world transform matrix for a prim, with optional caching.

        Args:
            prim (Union[usdrt.Usd.Prim, pxr.Usd.Prim]): The prim to get the transform for.
            use_cache (bool): Flag to indicate whether to use cached data."""
        # return self.get_data_accessor( self._prim_data_type(prim) ).get_local_to_world_transform(prim)
        if use_cache and prim in self._da_prim_cache:
            return self._da_prim_cache[prim].get_local_to_world_transform(prim)
        else:
            return self.get_data_accessor(self._data_types[type(prim.GetPath())]).get_local_to_world_transform(prim)

    def get_parent_to_world_transform(
        self, prim: Union[usdrt.Usd.Prim, pxr.Usd.Prim], use_cache: bool = False
    ) -> usdrt.Gf.Matrix4d:
        """Get the parent to world transform matrix for a prim, with optional caching.

        Args:
            prim (Union[usdrt.Usd.Prim, pxr.Usd.Prim]): The prim to get the transform for.
            use_cache (bool): Flag to indicate whether to use cached data."""
        # return self.get_data_accessor(self._prim_data_type(prim)).get_parent_to_world_transform(prim)
        if use_cache and prim in self._da_prim_cache:
            return self._da_prim_cache[prim].get_parent_to_world_transform(prim)
        else:
            return self.get_data_accessor(self._data_types[type(prim.GetPath())]).get_parent_to_world_transform(prim)

    def get_local_transform_pivot_inv(
        self, prim: Union[usdrt.Usd.Prim, pxr.Usd.Prim], time=pxr.Usd.TimeCode
    ) -> usdrt.Gf.Matrix4d:
        """Get the inverse of the local transform pivot for a prim at a given time.

        Args:
            prim (Union[usdrt.Usd.Prim, pxr.Usd.Prim]): The prim to get the pivot for.
            time (pxr.Usd.TimeCode): The time at which to get the pivot."""
        return self.get_data_accessor(self._prim_data_type(prim)).get_local_transform_pivot_inv(prim, time)

    def prim_has_prefix(
        self, sdf_path0: Union[usdrt.Sdf.Path, pxr.Sdf.Path], sdf_path: Union[usdrt.Sdf.Path, pxr.Sdf.Path]
    ) -> bool:
        """Check if the given SDF path has the specified prefix.

        Args:
            sdf_path0 (Union[usdrt.Sdf.Path, pxr.Sdf.Path]): The prefix path.
            sdf_path (Union[usdrt.Sdf.Path, pxr.Sdf.Path]): The SDF path to check."""
        return self.get_data_accessor(self._sdf_path_data_type(sdf_path0)).prim_has_prefix(sdf_path0, sdf_path)

    def reset_data(self):
        """Resets the transform data map."""
        self._transform_data_map: dict[str, TransformData] = {}

    def add_data(
        self,
        path: Union[usdrt.Sdf.Path, pxr.Sdf.Path],
        translation: usdrt.Gf.Vec3d,
        rotation: usdrt.Gf.Vec3d,
        ro: usdrt.Gf.Vec3i,
        scale: usdrt.Gf.Vec3d,
    ):
        """Adds transformation data for a given path.

        Args:
            path (Union[usdrt.Sdf.Path, pxr.Sdf.Path]): The path of the USD prim.
            translation (usdrt.Gf.Vec3d): The translation vector.
            rotation (usdrt.Gf.Vec3d): The rotation vector (euler angles).
            ro (usdrt.Gf.Vec3i): The rotation order.
            scale (usdrt.Gf.Vec3d): The scaling vector."""
        for da in self.get_data_accessors():
            if da.is_valid_path(path):
                tag = da.get_data_tag()
                if tag not in self._transform_data_map:
                    self._transform_data_map[tag] = TransformData()
                tr = self._transform_data_map[tag]
                tr.paths.append(str(path))
                tr.paths_c.append(da.path_to_int(path))
                tr.new_translations += [translation[0], translation[1], translation[2]]
                tr.new_rotation_eulers += [rotation[0], rotation[1], rotation[2]]
                tr.new_rotation_orders += [ro[0], ro[1], ro[2]]
                tr.new_scales += [scale[0], scale[1], scale[2]]
                break

    def add_data_full(
        self,
        path: Union[usdrt.Sdf.Path, pxr.Sdf.Path],
        translation: usdrt.Gf.Vec3d,
        rotation: usdrt.Gf.Vec3d,
        ro: usdrt.Gf.Vec3i,
        scale: usdrt.Gf.Vec3d,
        translation_old: usdrt.Gf.Vec3d,
        rotation_old: usdrt.Gf.Vec3d,
        ro_old: usdrt.Gf.Vec3i,
        scale_old: usdrt.Gf.Vec3d,
    ):
        """Adds full transformation data including old and new values for a given path.

        Args:
            path (Union[usdrt.Sdf.Path, pxr.Sdf.Path]): The path of the USD prim.
            translation (usdrt.Gf.Vec3d): The new translation vector.
            rotation (usdrt.Gf.Vec3d): The new rotation vector (euler angles).
            ro (usdrt.Gf.Vec3i): The new rotation order.
            scale (usdrt.Gf.Vec3d): The new scaling vector.
            translation_old (usdrt.Gf.Vec3d): The old translation vector.
            rotation_old (usdrt.Gf.Vec3d): The old rotation vector (euler angles).
            ro_old (usdrt.Gf.Vec3i): The old rotation order.
            scale_old (usdrt.Gf.Vec3d): The old scaling vector."""
        for da in self.get_data_accessors_write_priority():
            if da.has_prim_at_path(da.get_sdf_path(path)):
                tag = da.get_data_tag()
                if tag not in self._transform_data_map:
                    self._transform_data_map[tag] = TransformData()
                tr = self._transform_data_map[tag]
                tr.paths.append(str(path))
                tr.paths_c.append(da.path_to_int(path))
                tr.new_translations += [translation[0], translation[1], translation[2]]
                tr.new_scales += [scale[0], scale[1], scale[2]]

                tr.old_translations += [translation_old[0], translation_old[1], translation_old[2]]
                tr.old_scales += [scale_old[0], scale_old[1], scale_old[2]]

                if self._get_sdf_path_data_tag(path) == tag:
                    tr.new_rotation_eulers += [rotation[0], rotation[1], rotation[2]]
                    tr.new_rotation_orders += [ro[0], ro[1], ro[2]]

                    tr.old_rotation_eulers += [rotation_old[0], rotation_old[1], rotation_old[2]]
                    tr.old_rotation_orders += [ro_old[0], ro_old[1], ro_old[2]]

                else:
                    usd_prim = da.get_prim_at_path(da.get_sdf_path(path))
                    _, _, hi_prio_rot_orders, _ = da.get_local_transform_SRT(usd_prim, self._model._current_time)
                    lo_prio_eulers = (rotation[0], rotation[1], rotation[2])
                    lo_prio_rot_orders = [ro[0], ro[1], ro[2]]
                    lo_prio_q = self._quaternion_from_euler(lo_prio_eulers, lo_prio_rot_orders)
                    hi_prio_eulers = self._euler_from_quaternion_ro(lo_prio_q, hi_prio_rot_orders)

                    tr.new_rotation_eulers += [hi_prio_eulers[0], hi_prio_eulers[1], hi_prio_eulers[2]]
                    tr.new_rotation_orders += [hi_prio_rot_orders[0], hi_prio_rot_orders[1], hi_prio_rot_orders[2]]

                    old_lo_prio_eulers = (rotation_old[0], rotation_old[1], rotation_old[2])
                    old_lo_prio_q = self._quaternion_from_euler(old_lo_prio_eulers, lo_prio_rot_orders)
                    old_hi_prio_eulers = self._euler_from_quaternion_ro(old_lo_prio_q, hi_prio_rot_orders)

                    tr.old_rotation_eulers += [old_hi_prio_eulers[0], old_hi_prio_eulers[1], old_hi_prio_eulers[2]]
                    tr.old_rotation_orders += [hi_prio_rot_orders[0], hi_prio_rot_orders[1], hi_prio_rot_orders[2]]
                break

    @carb.profiler.profile
    def do_transform_selected_prims(self):
        """Transforms the selected prims.

        Args:
            args (List): The arguments for the transformation.

        Keyword Args:
            paths (List): The paths of the prims to transform.
            paths_c (List): The compact paths of the prims to transform.
            new_translations (List): The new translation values.
            new_rotation_eulers (List): The new rotation euler angles.
            new_rotation_orders (List): The new rotation orders.
            new_scales (List): The new scale values."""
        carb.profiler.begin(1, "DataAccessorSelector.tr")
        for tag, data in self._transform_data_map.items():
            self.get_data_accessor(tag).do_transform_selected_prims(
                data.paths,
                data.paths_c,
                data.new_translations,
                data.new_rotation_eulers,
                data.new_rotation_orders,
                data.new_scales,
            )
        carb.profiler.end(1)

    def do_transform_all_selected_prims_to_manipulator_pivot(
        self,
        paths: List[Union[usdrt.Sdf.Path, pxr.Sdf.Path]],
        new_translations: List[float],
        new_rotation_eulers: List[float],
        new_rotation_orders: List[int],
        new_scales: List[float],
    ):
        """Transforms all selected prims to the manipulator pivot.

        Args:
            paths (List[Union[usdrt.Sdf.Path, pxr.Sdf.Path]]): The paths of prims to transform.
            new_translations (List[float]): The new translation values.
            new_rotation_eulers (List[float]): The new rotation euler angles.
            new_rotation_orders (List[int]): The new rotation orders.
            new_scales (List[float]): The new scale values."""
        transform_data_map: dict[str, TransformData] = {}
        for i, path in enumerate(paths):
            for da in self.get_data_accessors():
                if da.is_valid_path(path):
                    tag = da.get_data_tag()
                    if tag not in transform_data_map:
                        transform_data_map[tag] = TransformData()
                    tr = transform_data_map[tag]
                    # tr.paths.append(path)
                    tr.paths_c.append(da.path_to_int(path))
                    tr.new_translations += [
                        new_translations[i * 3],
                        new_translations[i * 3 + 1],
                        new_translations[i * 3 + 2],
                    ]
                    tr.new_rotation_eulers += [
                        new_rotation_eulers[i * 3],
                        new_rotation_eulers[i * 3 + 1],
                        new_rotation_eulers[i * 3 + 2],
                    ]
                    tr.new_rotation_orders += [
                        new_rotation_orders[i * 3],
                        new_rotation_orders[i * 3 + 1],
                        new_rotation_orders[i * 3 + 2],
                    ]
                    tr.new_scales += [new_scales[i * 3], new_scales[i * 3 + 1], new_scales[i * 3 + 2]]
                    break
        for tag in transform_data_map:
            data = transform_data_map[tag]
            self.get_data_accessor(tag).do_transform_all_selected_prims_to_manipulator_pivot(
                data.paths,
                data.paths_c,
                data.new_translations,
                data.new_rotation_eulers,
                data.new_rotation_orders,
                data.new_scales,
            )

    def on_ended_transform(self):
        """Ends the transform operation."""
        with omni.kit.undo.group():
            for tag, data in self._transform_data_map.items():
                self.get_data_accessor(tag).on_ended_transform(
                    data.paths,
                    data.paths_c,
                    data.new_translations,
                    data.new_rotation_eulers,
                    data.new_rotation_orders,
                    data.new_scales,
                    data.old_translations,
                    data.old_rotation_eulers,
                    data.old_rotation_orders,
                    data.old_scales,
                )

    def _euler_from_quaternion_ro(self, q, conv_order):
        converted_euler = [0, 0, 0]
        rotation = usdrt.Gf.Rotation(q)
        axis = [usdrt.Gf.Vec3d.XAxis(), usdrt.Gf.Vec3d.YAxis(), usdrt.Gf.Vec3d.ZAxis()]
        decomp_rot = rotation.Decompose(axis[conv_order[2]], axis[conv_order[1]], axis[conv_order[0]])
        index_order = usdrt.Gf.Vec3i()
        for i in range(0, 3):
            index_order[conv_order[i]] = 2 - i
        converted_euler[0] = decomp_rot[index_order[0]]
        converted_euler[1] = decomp_rot[index_order[1]]
        converted_euler[2] = decomp_rot[index_order[2]]
        return converted_euler

    def _quaternion_from_euler(self, eulers: Tuple[float, ...], ro: usdrt.Gf.Vec3i):
        axes = [usdrt.Gf.Vec3d(1, 0, 0), usdrt.Gf.Vec3d(0, 1, 0), usdrt.Gf.Vec3d(0, 0, 1)]
        nrs = [usdrt.Gf.Rotation(axes[i], eulers[i]) for i in [ro[0], ro[1], ro[2]]]
        nr = nrs[0] * nrs[1] * nrs[2]
        result = nr.GetQuat()
        return result

    def is_a_xformable(self, prim: Union[usdrt.Usd.Prim, pxr.Usd.Prim]) -> bool:
        """Checks if the prim can be transformed.

        Args:
            prim (Union[usdrt.Usd.Prim, pxr.Usd.Prim]): The USD prim to check."""
        return self.get_data_accessor(self._prim_data_type(prim)).is_a_xformable(prim)

    def is_instance_proxy(self, prim: Union[usdrt.Usd.Prim, pxr.Usd.Prim]) -> bool:
        """Checks if the prim is an instance proxy.

        Args:
            prim (Union[usdrt.Usd.Prim, pxr.Usd.Prim]): The USD prim to check."""
        return self.get_data_accessor(self._prim_data_type(prim)).is_instance_proxy(prim)

    def is_prim_active(self, prim: Union[usdrt.Usd.Prim, pxr.Usd.Prim]) -> bool:
        """Checks if the prim is active.

        Args:
            prim (Union[usdrt.Usd.Prim, pxr.Usd.Prim]): The USD prim to check."""
        return self.get_data_accessor(self._prim_data_type(prim)).is_prim_active(prim)

    # use pxr until implemented in usdrt
    def is_transformation_affected_by_attr_named(self, sdf_path: Union[usdrt.Usd.Prim, pxr.Usd.Prim]) -> bool:
        """Checks if the prim's transformation is affected by an attribute.

        Args:
            sdf_path (Union[usdrt.Usd.Prim, pxr.Usd.Prim]): The USD prim to check."""
        return self.get_data_accessor(self._sdf_path_data_type(sdf_path)).is_transformation_affected_by_attr_named(
            sdf_path.name
        )

    # use pxr until implemented in usdrt
    def get_stage_up_axis(self) -> str:
        """Retrieves the up axis of the stage."""
        da = self.get_data_accessor("USD")
        if da == None:
            carb.log_error("PrimDataAccessorSelector get_stage_up_axis: no USD data accessor")
        else:
            return da.get_stage_up_axis()

    # use pxr until implemented in usdrt
    def get_current_time_code(self, currentTime: float) -> pxr.Usd.TimeCode:
        """Gets the current time code.

        Args:
            currentTime (float): The current time to retrieve the time code for."""
        da = self.get_data_accessor("USD")
        if da == None:
            carb.log_error("PrimDataAccessorSelector get_current_time_code: no USD data accessor")
            return None
        else:
            return da.get_current_time_code(currentTime)

    def clear_xform_cache(self):
        """Clears the transformation cache."""
        for da in self.get_data_accessors():
            da.clear_xform_cache()

    def free_xform_cache(self):
        """Frees the transformation cache."""
        for da in self.get_data_accessors():
            da.free_xform_cache()

    def xform_set_time(self):
        """Sets the time for the transform."""
        for da in self.get_data_accessors():
            da.xform_set_time()

    def update_xform_cache(self):
        """Updates the transformation cache."""
        for da in self.get_data_accessors():
            da.update_xform_cache()

    def free_stage(self):
        """Frees the USD stage."""
        for da in self.get_data_accessors():
            da.free_stage()

    def get_stage(self) -> Union[usdrt.Usd.Stage, pxr.Usd.Stage]:
        """Retrieves the USD stage."""
        return self.get_data_accessor(self._defType).get_stage()

    def set_stage(self):
        """Sets the USD stage."""
        for da in self.get_data_accessors():
            da.set_stage()

    def setup_update_callback(self):
        """Sets up the update callback."""
        res = None
        for da in self.get_data_accessors():
            cb = da.setup_update_callback()
            if da.get_data_tag() == "USD":
                res = cb
        return res

    def remove_update_callback(
        self, listener: pxr.Tf.Listener = None
    ) -> Union[usdrt.Rt.ChangeTracker, pxr.Tf.Listener]:
        """Removes an update callback.

        Args:
            listener (:obj:`pxr.Tf.Listener`): The listener to be removed."""
        for da in self.get_data_accessors():
            da.remove_update_callback(listener)
        return None

    def setup_update_callback_ref_prim_maker(
        self,
        func: Callable[
            [List, List[Union[usdrt.Sdf.Path, pxr.Sdf.Path]], List[Union[usdrt.Sdf.Path, pxr.Sdf.Path]], str], None
        ],
    ) -> Union[usdrt.Rt.ChangeTracker, pxr.Tf.Listener]:
        """Sets up an update callback for reference prim maker.

        Args:
            func (:obj:`Callable`): The function to call when the update occurs."""
        res = None
        for da in self.get_data_accessors():
            cb = da.setup_update_callback_ref_prim_maker(func)
            if da.get_data_tag() == "USD":
                res = cb
        return res

    def remove_update_callback_ref_prim_maker(
        self, listener: pxr.Tf.Listener = None
    ) -> Union[usdrt.Rt.ChangeTracker, pxr.Tf.Listener]:
        """Removes an update callback for reference prim maker.

        Args:
            listener (:obj:`pxr.Tf.Listener`): The listener to be removed."""
        for da in self.get_data_accessors():
            da.remove_update_callback_ref_prim_maker(listener)
        return None

    # #template functions
    # @property
    # def Gf(self):
    #     # return self.get_data_accessor(self._defType).Gf
    #     return usdrt.Gf

    @property
    def Sdf(self):
        """Gets the Sdf module.

        Returns:
            The Sdf module."""
        return self.get_data_accessor(self._defType).Sdf

    @property
    def Tf(self):
        """Gets the Tf module.

        Returns:
            The Tf module."""
        return self.get_data_accessor(self._defType).Tf

    @property
    def Usd(self):
        """Gets the Usd module.

        Returns:
            The Usd module."""
        return self.get_data_accessor(self._defType).Usd

    @property
    def UsdGeom(self):
        """Gets the UsdGeom module.

        Returns:
            The UsdGeom module."""
        return self.get_data_accessor(self._defType).UsdGeom

    @property
    def usd_context(self):
        """Gets the USD context.

        Returns:
            The USD context."""
        return self._usd_context
        # return self.get_data_accessor(self._defType)._usd_context
