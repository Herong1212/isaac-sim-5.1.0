# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""This module defines the PrimTransformModel for transforming USD prims in a viewport and handling related manipulations and gestures."""


from __future__ import annotations

import asyncio
import concurrent.futures
import math
import traceback
from enum import Enum, Flag, IntEnum, auto
from typing import Dict, List, Sequence, Set, Tuple, Union

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
import usdrt.Gf
import usdrt.Sdf
from carb.eventdispatcher import get_eventdispatcher
from omni.kit.async_engine import run_coroutine
from omni.kit.manipulator.tool.snap import SnapProviderManager
from omni.kit.manipulator.tool.snap import settings_constants as snap_c
from omni.kit.manipulator.transform import AbstractTransformManipulatorModel
from omni.kit.manipulator.transform import Constants as transform_c
from omni.kit.manipulator.transform import Operation, OpSettingsListener, SnapSettingsListener
from omni.kit.viewport.manipulator.transform import (
    ManipulationMode,
    ViewportRotateChangedGesture,
    ViewportScaleChangedGesture,
    ViewportTransformModel,
    ViewportTranslateChangedGesture,
)
from omni.ui import scene as sc

from .prim_data_accessor_selector import PrimDataAccessorSelector
from .settings_constants import Constants as prim_c
from .utils import *

# Settings needed for zero-gravity
TRANSFORM_GIZMO_CUSTOM_MANIPULATOR_ENABLED = "/app/transform/gizmoCustomManipulatorEnabled"
TRANSFORM_GIZMO_CUSTOM_MANIPULATOR_PRIMS = "/app/transform/gizmoCustomManipulatorPrims"
TRANSFORM_GIZMO_IS_USING = "/app/transform/gizmoIsUsing"
TRANSFORM_GIZMO_TRANSLATE_DELTA_XYZ = "/app/transform/gizmoTranslateDeltaXYZ"
TRANSFORM_GIZMO_PIVOT_WORLD_POSITION = "/app/transform/tempPivotWorldPosition"
TRANSFORM_GIZMO_ROTATE_DELTA_XYZW = "/app/transform/gizmoRotateDeltaXYZW"
TRANSFORM_GIZMO_SCALE_DELTA_XYZ = "/app/transform/gizmoScaleDeltaXYZ"
TRANSLATE_DELAY_FRAME_SETTING = "/exts/omni.kit.manipulator.prim.core/visual/delayFrame"

PRINT_PERF_DATA = True


class OpFlag(Flag):
    """An enumeration defining operation flags for transformation.

    This enumeration subclass represents different types of transformation operations that can be applied to objects in a scene, such as translation, rotation, and scaling. Each member of this enumeration represents a distinct operation and can be combined using bitwise operations to represent multiple transformations simultaneously.
    """

    TRANSLATE = auto()
    """Flag
Indicates a translation operation."""
    ROTATE = auto()
    """Flag
Indicates a rotation operation."""
    SCALE = auto()
    """Flag
Indicates a scaling operation."""


class Placement(Enum):
    """An enumeration representing the various placement options for the transform manipulator.

    This enum defines where the pivot of the transform manipulator will be placed in relation to the selected primitives.

    Attributes:
        LAST_PRIM_PIVOT: The pivot is at the last selected primitive.
        SELECTION_CENTER: The pivot is centered among all selected primitives.
        BBOX_CENTER: The pivot is at the bounding box center of the selection.
        REF_PRIM: The pivot is at a referenced primitive.
        BBOX_BASE: The pivot is at the base of the bounding box of the selection."""

    LAST_PRIM_PIVOT = auto()
    """Enum: Represents last selected primitive's pivot."""
    SELECTION_CENTER = auto()
    """Enum: Represents center of the selection."""
    BBOX_CENTER = auto()
    """Enum: Represents bounding box center of the selection."""
    REF_PRIM = auto()
    """Enum: Represents a reference primitive."""
    BBOX_BASE = auto()
    """Enum: Represents base of the selection's bounding box."""


class PrimTranslateChangedGesture(ViewportTranslateChangedGesture):
    """A class that represents the gesture of translation change for a primitive in the viewport.

    This class extends the `ViewportTranslateChangedGesture` and is responsible for handling the translation change events
    when a primitive is manipulated in the viewport. It ensures the translation changes are properly reflected in the
    model representing the primitive's transform."""

    def _get_model(self, payload_type) -> PrimTransformModel:
        if not self.gesture_payload or not self.sender or not isinstance(self.gesture_payload, payload_type):
            return None
        return self.sender.model


class PrimRotateChangedGesture(ViewportRotateChangedGesture):
    """A derived gesture class to handle rotation changes for prims.

    This class extends the functionality of ViewportRotateChangedGesture by providing additional
    handling specific to rotation changes in the context of prims within a scene. It captures
    the changes in rotation initiated through the viewport manipulators and applies them to the
    relevant prims."""

    ...


class PrimScaleChangedGesture(ViewportScaleChangedGesture):
    """A gesture class that handles scaling changes for primitive objects in a viewport.

    This class responds to scaling manipulation gestures performed on USD primitive objects within a viewport. It extends the default viewport scaling gesture functionality with additional logic specific to primitive object scaling. The class is designed to work in conjunction with tools that manipulate the scale of USD prims visually, providing a means to capture and respond to user input related to scaling operations.
    """

    ...


class PrimTransformModel(ViewportTransformModel):
    """A model for transforming USD prims in a viewport.

    This model extends the functionality of the ViewportTransformModel to specifically handle the transformation
    of USD prims. It supports various operations such as translation, rotation, and scaling of prims
    within the USD scene. The model is capable of handling selections of multiple prims, applying
    transformations in different modes (e.g., global, local), and integrates with snapping and
    other viewport manipulation tools.

    The model also manages a selection of prims and updates their transformations based on user
    interactions in the viewport. It supports custom manipulators and can be extended to handle
    specific use cases in USD scene manipulation.

    Args:
        usd_context_name (str): The name of the USD context to operate within.
        viewport_api: The viewport API instance to interact with for viewport transformations."""

    def __init__(self, usd_context_name: str = "", viewport_api=None):
        """Initializes a new instance of PrimTransformModel, setting up the necessary properties and subscriptions for transforming USD prims in a viewport."""
        ViewportTransformModel.__init__(self, usd_context_name=usd_context_name, viewport_api=viewport_api)
        self._data_accessor_selector = PrimDataAccessorSelector(
            model=self, usd_context_name=usd_context_name, dataTypes=["USD", "FABRIC"]
        )

        self._transform = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]  # visual transform of manipulator
        self._no_scale_transform_manipulator = usdrt.Gf.Matrix4d(1.0)  # transform of manipulator without scale
        self._scale_manipulator = usdrt.Gf.Vec3d(1.0)  # scale of manipulator
        self._settings = carb.settings.get_settings()
        self._dict = carb.dictionary.get_dictionary()
        self._timeline = omni.timeline.get_timeline_interface()
        self._app = omni.kit.app.get_app()
        self._usd_context_name = usd_context_name
        # self._usd_context = omni.usd.get_context(usd_context_name)

        self._selection = []
        self._enabled_hosting_widget_count: int = 0
        self._stage_listener = None
        self._xformable_prim_paths: List[self._data_accessor_selector.Sdf.Path] = []
        self._xformable_prim_paths_sorted: List[self._data_accessor_selector.Sdf.Path] = []
        self._xformable_prim_paths_set: Set[self._data_accessor_selector.Sdf.Path] = set()
        self._xformable_prim_paths_prefix_set: Set[self._data_accessor_selector.Sdf.Path] = set()
        self._consolidated_xformable_prim_paths: List[self._data_accessor_selector.Sdf.Path] = []
        self._pending_changed_paths_for_xform_data: Set[self._data_accessor_selector.Sdf.Path] = set()
        self._pivot_prim: self._data_accessor_selector.Usd.Prim = None
        self._update_prim_xform_from_prim_task_or_future: Union[asyncio.Task, concurrent.futures.Future, None] = None
        self._current_editing_op: Operation = None
        self._ignore_xform_data_change = False
        self._timeline_sub = None
        self._pending_changed_paths: Dict[self._data_accessor_selector.Sdf.Path, bool] = {}

        self._mode = ManipulationMode.PIVOT
        self._viewport_fps: float = (
            0.0  # needed this as heuristic for delaying the visual update of manipulator to match rendering
        )
        self._viewport_api = viewport_api
        self._delay_dirty_tasks_or_futures: Dict[int, Union[asyncio.Task, concurrent.futures.Future]] = {}

        self._no_scale_transform_manipulator_item = sc.AbstractManipulatorItem()
        self._items["no_scale_transform_manipulator"] = self._no_scale_transform_manipulator_item

        self._scale_manipulator_item = sc.AbstractManipulatorItem()
        self._items["scale_manipulator"] = self._scale_manipulator_item

        self._transform_manipulator_item = sc.AbstractManipulatorItem()
        self._items["transform_manipulator"] = self._transform_manipulator_item

        self._manipulator_mode_item = sc.AbstractManipulatorItem()
        self._items["manipulator_mode"] = self._manipulator_mode_item

        self._viewport_fps_item = sc.AbstractManipulatorItem()
        self._items["viewport_fps"] = self._viewport_fps_item

        self._set_default_settings()

        # subscribe to snap events
        self._snap_settings_listener = SnapSettingsListener(
            enabled_setting_path=None,
            move_x_setting_path=snap_c.SNAP_TRANSLATE_SETTING_PATH,
            move_y_setting_path=snap_c.SNAP_TRANSLATE_SETTING_PATH,
            move_z_setting_path=snap_c.SNAP_TRANSLATE_SETTING_PATH,
            rotate_setting_path=snap_c.SNAP_ROTATE_SETTING_PATH,
            scale_setting_path=snap_c.SNAP_SCALE_SETTING_PATH,
            provider_setting_path=snap_c.SNAP_PROVIDER_NAME_SETTING_PATH,
        )

        # subscribe to operation/mode events
        self._op_settings_listener = OpSettingsListener()
        self._op_settings_listener_sub = self._op_settings_listener.subscribe_listener(self._on_op_listener_changed)

        self._placement_sub = self._settings.subscribe_to_node_change_events(
            prim_c.MANIPULATOR_PLACEMENT_SETTING, self._on_placement_setting_changed
        )
        self._placement = Placement.LAST_PRIM_PIVOT
        placement = self._settings.get(prim_c.MANIPULATOR_PLACEMENT_SETTING)
        self._update_placement(placement)

        # cache unique setting path for selection pivot position
        # vp1 default
        self._selection_pivot_position_path = TRANSFORM_GIZMO_PIVOT_WORLD_POSITION + "/Viewport"
        # vp2
        if self._viewport_api:
            self._selection_pivot_position_path = (
                TRANSFORM_GIZMO_PIVOT_WORLD_POSITION + "/" + self._viewport_api.id.split("/")[0]
            )
        # update setting with pivot placement position on init
        self._update_temp_pivot_world_position()

        def subscribe_to_value_and_get_current(setting_val_name: str, setting_path: str):
            sub = self._settings.subscribe_to_node_change_events(
                setting_path, lambda item, type: setattr(self, setting_val_name, self._dict.get(item))
            )
            setattr(self, setting_val_name, self._settings.get(setting_path))
            return sub

        # subscribe to zero-gravity settings
        self._custom_manipulator_enabled_sub = subscribe_to_value_and_get_current(
            "_custom_manipulator_enabled", TRANSFORM_GIZMO_CUSTOM_MANIPULATOR_ENABLED
        )

        self._warning_notification = None
        self._selected_instance_proxy_paths = set()

        # subscribe to USD related events
        self._stage_event_sub = [
            get_eventdispatcher().observe_event(
                observer_name="omni.kit.manipulator.prim.core:model",
                event_name=self._data_accessor_selector.usd_context.stage_event_name(event),
                on_event=func,
            )
            for event, func in (
                (omni.usd.StageEventType.OPENED, lambda _: self._on_stage_opened()),
                (omni.usd.StageEventType.CLOSING, lambda _: self._on_stage_closing()),
            )
        ]

        if self._data_accessor_selector.usd_context.get_stage_state() == omni.usd.StageState.OPENED:
            self._on_stage_opened()

    def update_selection(self):
        """Updates the selection state of the model."""
        if not self._data_accessor_selector.is_ready() or not self._data_accessor_selector.get_stage():
            return

        selection_prioterized = []
        for sdf_path in self._selection:
            sdf_path_prioritized = self.get_da().get_sdf_path_by_priority(sdf_path)
            selection_prioterized.append(sdf_path_prioritized)
        self.on_selection_changed(selection_prioterized)

    def on_selection_changed(self, selection: List[pxr.Sdf.Path]):
        """Handles updates to the selection of prims within the model.

        Args:
            selection (List[:obj:`pxr.Sdf.Path`]): The new selection of Sdf Paths."""
        if self._data_accessor_selector.is_ready():
            self._selection = selection

            def by_str(path):
                return self._data_accessor_selector.get_string_path(path)

            if self._update_prim_xform_from_prim_task_or_future is not None:
                self._update_prim_xform_from_prim_task_or_future.cancel()
                self._update_prim_xform_from_prim_task_or_future = None

            self._selected_instance_proxy_paths.clear()
            self._xformable_prim_paths.clear()
            self._xformable_prim_paths_set.clear()
            self._xformable_prim_paths_prefix_set.clear()
            self._consolidated_xformable_prim_paths.clear()
            self._pivot_prim = None

            for sdf_path in selection:
                # sdf_path_prioritized = self._data_accessor_selector.get_sdf_path_by_priority(sdf_path)
                # if sdf_path_prioritized != None:
                prim = self._data_accessor_selector.get_prim_at_path(sdf_path)
                if (
                    prim
                    and self._data_accessor_selector.is_a_xformable(prim)
                    and self._data_accessor_selector.is_prim_active(prim)
                ):
                    self._xformable_prim_paths.append(prim.GetPath())

            if self._xformable_prim_paths:
                # Make a sorted list so parents always appears before child
                self._xformable_prim_paths_sorted = self._xformable_prim_paths.copy()
                self._xformable_prim_paths_sorted.sort(key=by_str)
                # self._xformable_prim_paths_sorted.sort()

                # Find the most recently selected valid xformable prim as the pivot prim where the transform gizmo is located at.
                self._pivot_prim = self._data_accessor_selector.get_prim_at_path(self._xformable_prim_paths[-1])

                # Get least common prims ancestors.
                # We do this so that if one selected prim is a descendant of other selected prim, the descendant prim won't be
                # transformed twice.
                self._consolidated_xformable_prim_paths = self._data_accessor_selector.remove_descendent_paths(
                    self._xformable_prim_paths
                )

                # Filter all instance proxy paths.
                for path in self._consolidated_xformable_prim_paths:
                    prim = self._data_accessor_selector.get_prim_at_path(path)
                    if self._data_accessor_selector.is_instance_proxy(prim):
                        self._selected_instance_proxy_paths.add(sdf_path)

                self._data_accessor_selector.cache_prim_data(self._consolidated_xformable_prim_paths)

            self._xformable_prim_paths_set.update(self._xformable_prim_paths)
            for path in self._xformable_prim_paths_set:
                self._xformable_prim_paths_prefix_set.update(path.GetPrefixes())

            if self._update_transform_from_prims():
                self._item_changed(self._transform_item)

            # Happens when host widget is already enabled and first selection in a new stage
            if self._enabled_hosting_widget_count > 0 and self._stage_listener is None:
                self._stage_listener = self._data_accessor_selector.setup_update_callback()

    def get_da(self):
        """Retrieves the data accessor selector associated with the model.

        Returns:
            :obj:`PrimDataAccessorSelector`: The data accessor selector."""
        return self._data_accessor_selector

    def _on_timeline_event(self, e: carb.events.IEvent):
        if e.type == int(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED):
            current_time = e.payload["currentTime"]
            if current_time != self._current_time:
                self._current_time = current_time
                self._data_accessor_selector.xform_set_time()
                # TODO only update transform if this prim or ancestors transforms are time varying?
                if self._update_transform_from_prims():
                    self._item_changed(self._transform_item)

    def _on_stage_opened(self):
        self._timeline_sub = self._timeline.get_timeline_event_stream().create_subscription_to_pop(
            self._on_timeline_event
        )
        self._current_time = self._timeline.get_current_time()
        if self._data_accessor_selector.is_ready():
            self._data_accessor_selector.set_stage()
            self._data_accessor_selector.update_xform_cache()

    # #commands
    # def _on_ended_transform(
    #     self,
    #     paths: List,
    #     new_translations: List[float],
    #     new_rotation_eulers: List[float],
    #     new_rotation_orders: List[int],
    #     new_scales: List[float],
    #     old_translations: List[float],
    #     old_rotation_eulers: List[float],
    #     old_rotation_orders: List[int],
    #     old_scales: List[float],
    # ):
    #     self._alert_if_selection_has_instance_proxies()
    #     self._data_accessor_selector.on_ended_transform(
    #         paths,
    #         new_translations,
    #         new_rotation_eulers,
    #         new_rotation_orders,
    #         new_scales,
    #         old_translations,
    #         old_rotation_eulers,
    #         old_rotation_orders,
    #         old_scales,
    #     )

    def __del__(self):
        self.destroy()

    def destroy(self):
        """Cleans up resources and subscriptions when the model is destroyed."""
        if self._warning_notification:
            self._warning_notification.dismiss()
            self._warning_notification = None

        self._op_settings_listener_sub = None
        if self._op_settings_listener:
            self._op_settings_listener.destroy()
            self._op_settings_listener = None

        self._stage_event_sub = None
        if self._stage_listener:
            self._stage_listener = self._data_accessor_selector.remove_update_callback(self._stage_listener)

        # if self._data_accessor_selector.usd_context.get_stage_state() == omni.usd.StageState.OPENED:
        self._on_stage_closing()

        self._timeline_sub = None

        if self._snap_settings_listener:
            self._snap_settings_listener.destroy()
            self._snap_settings_listener = None

        if self._custom_manipulator_enabled_sub:
            self._settings.unsubscribe_to_change_events(self._custom_manipulator_enabled_sub)
            self._custom_manipulator_enabled_sub = None

        if self._placement_sub:
            self._settings.unsubscribe_to_change_events(self._placement_sub)
            self._placement_sub = None

        for task_or_future in self._delay_dirty_tasks_or_futures.values():
            task_or_future.cancel()
        self._delay_dirty_tasks_or_futures.clear()

        if self._data_accessor_selector != None:
            self._data_accessor_selector.destroy()
        self._data_accessor_selector = None

    def set_pivot_prim_path(self, path0: self._data_accessor_selector.Sdf.Path) -> bool:
        """Sets the pivot prim path based on the provided path.

        Args:
            path0 (:obj:`pxr.Sdf.Path`): The new pivot prim path.

        Returns:
            bool: True if the pivot prim path was successfully set."""
        path = self._data_accessor_selector.is_sdf_path_in_set(path0, self._xformable_prim_paths_set)
        if path == None:
            carb.log_warn(f"Cannot set pivot prim path to {path0}")
            return False

        if not self._pivot_prim or self._pivot_prim.GetPath() != path:
            self._pivot_prim = self._data_accessor_selector.get_prim_at_path(path)
        else:
            return False

        if self._update_transform_from_prims():
            self._item_changed(self._transform_item)

        return True

    def get_pivot_prim_path(self) -> self._data_accessor_selector.Sdf.Path:
        """Gets the current pivot prim path.

        Returns:
            :obj:`pxr.Sdf.Path`: The current pivot prim path."""
        if self._pivot_prim:
            return self._pivot_prim.GetPath()
        return None

    @carb.profiler.profile
    def _update_xform_data_from_dirty_paths(self):
        for p in self._pending_changed_paths_for_xform_data:
            prim_path = p.GetPrimPath()
            if prim_path in self.all_xformable_prim_data_curr and self._path_may_affect_transform(p):
                prim = self._data_accessor_selector.get_prim_at_path(prim_path)
                xform_tuple = self._data_accessor_selector.get_local_transform_SRT(prim, self._current_time)
                pivot = self._data_accessor_selector.get_local_transform_pivot_inv(
                    prim, self._current_time
                ).GetInverse()
                self.all_xformable_prim_data_curr[prim_path] = xform_tuple + (pivot,)

                if prim_path in self._consolidated_xformable_prim_paths:
                    self.consolidated_xformable_prim_data_curr[prim_path] = xform_tuple + (pivot,)

        self._pending_changed_paths_for_xform_data.clear()

    def on_began(self, payload):
        """Handles the beginning of a transformation event.

        Args:
            payload (Dict): The payload associated with the transform event."""
        item = payload.changing_item
        self._current_editing_op = item.operation

        # All selected xformable prims' transforms. Store this for when `Keep Spacing` option is off during snapping,
        # because it can modify parent's and child're transform differently.
        self._all_xformable_prim_data_prev: Dict[
            self._data_accessor_selector.Sdf.Path,
            Tuple[usdrt.Gf.Vec3d, usdrt.Gf.Vec3d, usdrt.Gf.Vec3i, usdrt.Gf.Vec3d, usdrt.Gf.Vec3d],
        ] = {}

        # consolidated xformable prims' transforms. If parent is in the dict, child will be excluded.
        self._consolidated_xformable_prim_data_prev: Dict[
            self._data_accessor_selector.Sdf.Path, Tuple[usdrt.Gf.Vec3d, usdrt.Gf.Vec3d, usdrt.Gf.Vec3i, usdrt.Gf.Vec3d]
        ] = {}

        for path in self._xformable_prim_paths:
            prim = self._data_accessor_selector.get_prim_at_path(path)
            xform_tuple = self._data_accessor_selector.get_local_transform_SRT(prim, self._current_time)
            pivot = self._data_accessor_selector.get_local_transform_pivot_inv(prim, self._current_time).GetInverse()
            self._all_xformable_prim_data_prev[path] = xform_tuple + (pivot,)

            if path in self._consolidated_xformable_prim_paths:
                self._consolidated_xformable_prim_data_prev[path] = xform_tuple + (pivot,)

        self.all_xformable_prim_data_curr = self._all_xformable_prim_data_prev.copy()
        self.consolidated_xformable_prim_data_curr = self._consolidated_xformable_prim_data_prev.copy()

        self._pending_changed_paths_for_xform_data.clear()

        if self.custom_manipulator_enabled:
            self._settings.set(TRANSFORM_GIZMO_IS_USING, True)

    def on_changed(self, payload):
        """Handles changes during a transformation event.

        Args:
            payload (Dict): The payload associated with the transform event."""
        # Always re-fetch the changed transform on_changed. Although it might not be manipulated by manipulator,
        # prim's transform can be modified by other runtime (e.g. omnigraph), and we always want the latest.
        self._update_xform_data_from_dirty_paths()

    def on_ended(self, payload):
        """Handles the end of a transformation event.

        Args:
            payload (Dict): The payload associated with the transform event."""
        # Always re-fetch the changed transform on_changed. Although it might not be manipulated by manipulator,
        # prim's transform can be modified by other runtime (e.g. omnigraph), and we always want the latest.
        self._update_xform_data_from_dirty_paths()
        self._data_accessor_selector.reset_data()
        carb.profiler.begin(1, "PrimTransformChangedGestureBase.TransformPrimSRT.all")
        for path, (s, r, ro, t, pivot) in self.all_xformable_prim_data_curr.items():
            # Data didn't change
            if self._all_xformable_prim_data_prev[path] == self.all_xformable_prim_data_curr[path]:
                # carb.log_info(f"Skip {path}")
                continue
            (old_s, old_r, old_ro, old_t, old_pivot) = self._all_xformable_prim_data_prev[path]
            self._data_accessor_selector.add_data_full(path, t, r, ro, s, old_t, old_r, old_ro, old_s)

        self._ignore_xform_data_change = True
        self._alert_if_selection_has_instance_proxies()
        self._data_accessor_selector.on_ended_transform()
        self._ignore_xform_data_change = False

        carb.profiler.end(1)

        if self.custom_manipulator_enabled:
            self._settings.set(TRANSFORM_GIZMO_IS_USING, False)

        # if the manipulator was locked to orientation or translation,
        # refresh it on_ended so the transform is up to date
        mode = self._get_transform_mode_for_current_op()
        if self._should_keep_manipulator_orientation_unchanged(
            mode
        ) or self._should_keep_manipulator_translation_unchanged(mode):
            # set editing op to None AFTER _should_keep_manipulator_*_unchanged but
            # BEFORE self._update_transform_from_prims
            self._current_editing_op = None
            if self._update_transform_from_prims():
                self._item_changed(self._transform_item)

        self._current_editing_op = None

    def on_canceled(self, payload):
        """Handles the cancellation of a transformation event.

        Args:
            payload (Dict): The payload associated with the transform event."""
        # gc.enable()
        if self.custom_manipulator_enabled:
            self._settings.set(TRANSFORM_GIZMO_IS_USING, False)

        self._current_editing_op = None

    def widget_enabled(self):
        """Notifies the model that a widget has been enabled."""
        self._enabled_hosting_widget_count += 1

        # just changed from no active widget to 1 active widget
        if self._enabled_hosting_widget_count == 1:
            # listener only needs to be activated if manipulator is visible
            if self._consolidated_xformable_prim_paths:
                assert self._stage_listener is None
                self._stage_listener = self._data_accessor_selector.setup_update_callback()

    def _clear_temp_pivot_position_setting(self):
        if self._settings.get(self._selection_pivot_position_path):
            self._settings.destroy_item(self._selection_pivot_position_path)

    def widget_disabled(self):
        """Notifies the model that a widget has been disabled."""
        self._enabled_hosting_widget_count -= 1
        self._clear_temp_pivot_position_setting()
        assert self._enabled_hosting_widget_count >= 0
        if self._enabled_hosting_widget_count < 0:
            carb.log_error(f"manipulator enabled widget tracker out of sync: {self._enabled_hosting_widget_count}")
            self._enabled_hosting_widget_count = 0

        # If no hosting manipulator is active, revoke the listener since there's no need to sync Transform
        if self._enabled_hosting_widget_count == 0:
            if self._stage_listener:
                self._stage_listener = self._data_accessor_selector.remove_update_callback(self._stage_listener)

            for task_or_future in self._delay_dirty_tasks_or_futures.values():
                task_or_future.cancel()
            self._delay_dirty_tasks_or_futures.clear()

    def set_floats(self, item: sc.AbstractManipulatorItem, value: Sequence[float]):
        """Sets the float values for a given manipulator item.

        Args:
            item (:obj:`sc.AbstractManipulatorItem`): The manipulator item to be updated.
            value (Sequence[float]): The new float values to be set for the item."""
        if item == self._viewport_fps_item:
            self._viewport_fps = value[0]
            return

        flag = None
        if issubclass(type(item), AbstractTransformManipulatorModel.OperationItem):
            if (
                item.operation == Operation.TRANSLATE_DELTA
                or item.operation == Operation.ROTATE_DELTA
                or item.operation == Operation.SCALE_DELTA
            ):
                return
            if item.operation == Operation.TRANSLATE:
                flag = OpFlag.TRANSLATE
            elif item.operation == Operation.ROTATE:
                flag = OpFlag.ROTATE
            elif item.operation == Operation.SCALE:
                flag = OpFlag.SCALE
            transform = usdrt.Gf.Matrix4d(*value)
        elif item == self._transform_manipulator_item:
            flag = OpFlag.TRANSLATE | OpFlag.ROTATE | OpFlag.SCALE
            transform = usdrt.Gf.Matrix4d(*value)
        elif item == self._no_scale_transform_manipulator_item:
            flag = OpFlag.TRANSLATE | OpFlag.ROTATE
            old_manipulator_scale_mtx = usdrt.Gf.Matrix4d(1.0)
            old_manipulator_scale_mtx.SetScale(self._scale_manipulator)
            transform = old_manipulator_scale_mtx * usdrt.Gf.Matrix4d(*value)

        if flag is not None:
            if self._mode == ManipulationMode.PIVOT:
                self._transform_selected_prims(
                    transform, self._no_scale_transform_manipulator, self._scale_manipulator, flag
                )
            elif self._mode == ManipulationMode.UNIFORM:
                self._transform_all_selected_prims_to_manipulator_pivot(transform, flag)
        else:
            carb.log_warn(f"Unsupported item {item}")

    def set_ints(self, item: sc.AbstractManipulatorItem, value: Sequence[int]):
        """Sets the integer values for a given manipulator item.

        Args:
            item (:obj:`sc.AbstractManipulatorItem`): The manipulator item to be updated.
            value (Sequence[int]): The new integer values to be set for the item."""
        if item == self._manipulator_mode_item:
            try:
                self._mode = ManipulationMode(value[0])
            except:
                carb.log_error(traceback.format_exc())
        else:
            carb.log_warn(f"unsupported item {item}")
            return None

    def get_as_floats(self, item: sc.AbstractManipulatorItem):
        """Gets the float values associated with a manipulator item.

        Args:
            item (:obj:`sc.AbstractManipulatorItem`): The manipulator item whose values are to be retrieved.

        Returns:
            Sequence[float]: The float values associated with the item."""
        if item == self._transform_item:
            return self._transform
        elif item == self._no_scale_transform_manipulator_item:
            return flatten(self._no_scale_transform_manipulator)
        elif item == self._scale_manipulator_item:
            return [self._scale_manipulator[0], self._scale_manipulator[1], self._scale_manipulator[2]]
        elif item == self._transform_manipulator_item:
            scale_mtx = usdrt.Gf.Matrix4d(1)
            scale_mtx.SetScale(self._scale_manipulator)
            return flatten(scale_mtx * self._no_scale_transform_manipulator)
        else:
            carb.log_warn(f"unsupported item {item}")
            return None

    def get_as_ints(self, item: sc.AbstractManipulatorItem):
        """Gets the integer values associated with a manipulator item.

        Args:
            item (:obj:`sc.AbstractManipulatorItem`): The manipulator item whose values are to be retrieved.

        Returns:
            Sequence[int]: The integer values associated with the item."""
        if item == self._manipulator_mode_item:
            return [int(self._mode)]
        else:
            carb.log_warn(f"unsupported item {item}")
            return None

    def get_operation(self) -> Operation:
        """Gets the current operation of the model.

        Returns:
            Operation: The current operation."""
        if self._op_settings_listener.selected_op == transform_c.TRANSFORM_OP_MOVE:
            return Operation.TRANSLATE
        elif self._op_settings_listener.selected_op == transform_c.TRANSFORM_OP_ROTATE:
            return Operation.ROTATE
        elif self._op_settings_listener.selected_op == transform_c.TRANSFORM_OP_SCALE:
            return Operation.SCALE
        return Operation.NONE

    def get_snap(self, item: AbstractTransformManipulatorModel.OperationItem):
        """Gets the snap settings for a manipulator item.

        Args:
            item (:obj:`AbstractTransformManipulatorModel.OperationItem`): The manipulator item to get snap settings for.

        Returns:
            Union[None, Sequence[float]]: The snap settings for the item."""
        if not self._snap_settings_listener.snap_enabled:
            return None

        if item.operation == Operation.TRANSLATE:
            if self._snap_settings_listener.snap_provider:
                return None

            return (
                self._snap_settings_listener.snap_move_x,
                self._snap_settings_listener.snap_move_y,
                self._snap_settings_listener.snap_move_z,
            )
        elif item.operation == Operation.ROTATE:
            return self._snap_settings_listener.snap_rotate
        elif item.operation == Operation.SCALE:
            return self._snap_settings_listener.snap_scale

        return None

    @carb.profiler.profile
    def _transform_selected_prims(
        self,
        new_manipulator_transform: usdrt.Gf.Matrix4d,
        old_manipulator_transform_no_scale: usdrt.Gf.Matrix4d,
        old_manipulator_scale: usdrt.Gf.Vec3d,
        dirty_ops: OpFlag,
    ):
        carb.profiler.begin(1, "omni.kit.manipulator.prim.core.model._transform_selected_prims.prepare_data")
        use_cache = True
        self._data_accessor_selector.clear_xform_cache()

        # any op may trigger a translation change if multi-manipulating
        should_update_translate = (
            dirty_ops & OpFlag.TRANSLATE
            or len(self._xformable_prim_paths) > 1
            or self._placement != Placement.LAST_PRIM_PIVOT
        )
        should_update_rotate = dirty_ops & OpFlag.ROTATE
        should_update_scale = dirty_ops & OpFlag.SCALE

        old_manipulator_scale_mtx = usdrt.Gf.Matrix4d(1.0)
        old_manipulator_scale_mtx.SetScale(old_manipulator_scale)
        old_manipulator_transform_inv = (old_manipulator_scale_mtx * old_manipulator_transform_no_scale).GetInverse()

        # selected_parent_to_world_mtx = usdrt.Gf.Matrix4d(1)
        # selected_local_to_world_mtx = usdrt.Gf.Matrix4d(1)
        self._data_accessor_selector.reset_data()

        for path in self._consolidated_xformable_prim_paths:
            if self._custom_manipulator_enabled and self._should_skip_custom_manipulator_path(str(path)):
                continue
            selected_prim = self._data_accessor_selector.get_prim_at_path(sdf_path=path, use_cache=use_cache)

            # We check whether path is in consolidated_xformable_prim_data_curr because it may have not made it the dictionary if an error occured
            if not selected_prim or path not in self.consolidated_xformable_prim_data_curr:
                continue

            (s, r, ro, t, selected_pivot) = self.consolidated_xformable_prim_data_curr[path]
            selected_pivot_inv = selected_pivot.GetInverse()
            selected_local_to_world_mtx = self._data_accessor_selector.get_local_to_world_transform(
                selected_prim, use_cache=use_cache
            )
            selected_parent_to_world_mtx = self._data_accessor_selector.get_parent_to_world_transform(
                selected_prim, use_cache=use_cache
            )

            # Transform the prim from world space to pivot's space
            # Then apply the new pivotPrim-to-world-space transform matrix
            selected_local_to_world_pivot_mtx = (
                selected_pivot * selected_local_to_world_mtx * old_manipulator_transform_inv * new_manipulator_transform
            )

            world_to_parent_mtx = selected_parent_to_world_mtx.GetInverse()
            selected_local_mtx_new = selected_local_to_world_pivot_mtx * world_to_parent_mtx * selected_pivot_inv

            if should_update_translate:
                translation = selected_local_mtx_new.ExtractTranslation()

            if should_update_rotate:
                # Construct the new rotation from old scale and translation.
                # Don't use Factor because it won't be able to tell if scale is positive or negative and can result in flipped rotation
                old_s_mtx = usdrt.Gf.Matrix4d(1.0)
                old_s_mtx.SetScale(usdrt.Gf.Vec3d(s))
                old_t_mtx = usdrt.Gf.Matrix4d(1.0)
                old_t_mtx.SetTranslate(usdrt.Gf.Vec3d(t))
                rot_new = (old_s_mtx.GetInverse() * selected_local_mtx_new * old_t_mtx.GetInverse()).ExtractRotation()

                decomp_rot = self.decompose_to_eulers(rot_new, ro)
                index_order = usdrt.Gf.Vec3i()
                for i in range(3):
                    index_order[ro[i]] = 2 - i

                rotation = usdrt.Gf.Vec3d(
                    decomp_rot[index_order[0]], decomp_rot[index_order[1]], decomp_rot[index_order[2]]
                )
                rotation = find_best_euler_angles(usdrt.Gf.Vec3d(r), rotation, ro)

            if should_update_scale:
                # Construct the new scale from old rotation and translation.
                # Don't use Factor because it won't be able to tell if scale is positive or negative and can result in flipped rotation
                old_rt_mtx = compose_transform_ops_to_matrix(t, r, ro, usdrt.Gf.Vec3d(1))
                new_s_mtx = selected_local_mtx_new * old_rt_mtx.GetInverse()
                scale = usdrt.Gf.Vec3d(new_s_mtx[0][0], new_s_mtx[1][1], new_s_mtx[2][2])

            translation = translation if should_update_translate else t
            rotation = rotation if should_update_rotate else r
            scale = scale if should_update_scale else s

            self._data_accessor_selector.add_data(path, translation, rotation, ro, scale)
            xform_tuple = (scale, rotation, ro, translation, selected_pivot)
            self.consolidated_xformable_prim_data_curr[path] = xform_tuple
            self.all_xformable_prim_data_curr[path] = xform_tuple
        carb.profiler.end(1)

        self._ignore_xform_data_change = True
        self._alert_if_selection_has_instance_proxies()
        self._data_accessor_selector.do_transform_selected_prims()
        self._ignore_xform_data_change = False

    @carb.profiler.profile
    def _transform_all_selected_prims_to_manipulator_pivot(
        self,
        new_manipulator_transform: usdrt.Gf.Matrix4d,
        dirty_ops: OpFlag,
    ):
        self._data_accessor_selector.clear_xform_cache()

        # any op may trigger a translation change if multi-manipulating
        should_update_translate = dirty_ops & OpFlag.TRANSLATE or len(self._xformable_prim_paths) > 1
        should_update_rotate = dirty_ops & OpFlag.ROTATE
        should_update_scale = dirty_ops & OpFlag.SCALE
        self._data_accessor_selector.reset_data()

        for path in self._xformable_prim_paths_sorted:
            if self._custom_manipulator_enabled and self._should_skip_custom_manipulator_path(
                self._data_accessor_selector.get_string_path(path)
            ):
                continue

            selected_prim = self._data_accessor_selector.get_prim_at_path(path)
            # We check whether path is in all_xformable_prim_data_curr because it may have not made it the dictionary if an error occured
            if not selected_prim or path not in self.all_xformable_prim_data_curr:
                continue

            (s, r, ro, t, selected_pivot) = self.all_xformable_prim_data_curr[path]

            selected_parent_to_world_mtx = self._data_accessor_selector.get_parent_to_world_transform(selected_prim)
            world_to_parent_mtx = selected_parent_to_world_mtx.GetInverse()

            selected_local_mtx_new = new_manipulator_transform * world_to_parent_mtx * selected_pivot.GetInverse()

            if should_update_translate:
                translation = selected_local_mtx_new.ExtractTranslation()

            if should_update_rotate:
                # Construct the new rotation from old scale and translation.
                # Don't use Factor because it won't be able to tell if scale is positive or negative and can result in flipped rotation
                old_s_mtx = usdrt.Gf.Matrix4d(1.0)
                old_s_mtx.SetScale(usdrt.Gf.Vec3d(s))
                old_t_mtx = usdrt.Gf.Matrix4d(1.0)
                old_t_mtx.SetTranslate(usdrt.Gf.Vec3d(t))
                rot_new = (old_s_mtx.GetInverse() * selected_local_mtx_new * old_t_mtx.GetInverse()).ExtractRotation()

                # axes = [usdrt.Gf.Vec3d.XAxis(), usdrt.Gf.Vec3d.YAxis(), usdrt.Gf.Vec3d.ZAxis()]
                decomp_rot = self.decompose_to_eulers(
                    rot_new, ro
                )  # decomp_rot = rot_new.Decompose(axes[ro[2]], axes[ro[1]], axes[ro[0]])
                index_order = usdrt.Gf.Vec3i()
                for i in range(3):
                    index_order[ro[i]] = 2 - i

                rotation = usdrt.Gf.Vec3d(
                    decomp_rot[index_order[0]], decomp_rot[index_order[1]], decomp_rot[index_order[2]]
                )
                rotation = find_best_euler_angles(usdrt.Gf.Vec3d(r), rotation, ro)

            if should_update_scale:
                # Construct the new scale from old rotation and translation.
                # Don't use Factor because it won't be able to tell if scale is positive or negative and can result in flipped rotation
                old_rt_mtx = compose_transform_ops_to_matrix(t, r, ro, usdrt.Gf.Vec3d(1))
                new_s_mtx = selected_local_mtx_new * old_rt_mtx.GetInverse()
                scale = usdrt.Gf.Vec3d(new_s_mtx[0][0], new_s_mtx[1][1], new_s_mtx[2][2])

            # any op may trigger a translation change if multi-manipulating
            translation = translation if should_update_translate else t
            rotation = rotation if should_update_rotate else r
            scale = scale if should_update_scale else s

            self._data_accessor_selector.add_data(path, translation, rotation, ro, scale)
            xform_tuple = (scale, rotation, ro, translation, selected_pivot)
            self.all_xformable_prim_data_curr[path] = xform_tuple
            if path in self.consolidated_xformable_prim_data_curr:
                self.consolidated_xformable_prim_data_curr[path] = xform_tuple

        self._ignore_xform_data_change = True
        self._alert_if_selection_has_instance_proxies()
        self._data_accessor_selector.do_transform_selected_prims()
        self._ignore_xform_data_change = False

    def _alert_if_selection_has_instance_proxies(self):
        if self._selected_instance_proxy_paths and (
            not self._warning_notification or self._warning_notification.dismissed
        ):
            try:
                import omni.kit.notification_manager as nm

                self._warning_notification = nm.post_notification(
                    "Children of an instanced prim cannot be modified, uncheck Instanceable on the instanced prim to modify child prims.",
                    status=nm.NotificationStatus.WARNING,
                )
            except ImportError:
                pass

    def _on_stage_closing(self):
        if self._data_accessor_selector != None:
            self._data_accessor_selector.free_stage()
            self._data_accessor_selector.free_xform_cache()
        self._xformable_prim_paths.clear()
        self._xformable_prim_paths_sorted.clear()
        self._xformable_prim_paths_set.clear()
        self._xformable_prim_paths_prefix_set.clear()
        self._consolidated_xformable_prim_paths.clear()
        self._pivot_prim = None
        self._timeline_sub = None
        if self._stage_listener:
            self._stage_listener = self._data_accessor_selector.remove_update_callback(self._stage_listener)
        self._pending_changed_paths.clear()
        if self._update_prim_xform_from_prim_task_or_future is not None:
            self._update_prim_xform_from_prim_task_or_future.cancel()
            self._update_prim_xform_from_prim_task_or_future = None

    def _should_keep_manipulator_orientation_unchanged(self, mode: str) -> bool:
        # Exclude snap_to_face. During snap_to_face operation, it may modify the orientation of object to confrom to surface
        # normal and the `new_manipulator_transform` param for `_transform_selected_prims` is set to the final transform
        # of the manipulated prim. However, if we use old rotation in the condition below, _no_scale_transform_manipulator
        # will not confrom to the new orientation, and _transform_selected_prims would double rotate the prims because it
        # sees the rotation diff between the old prim orientation (captured at on_began) vs new normal orient, instead of
        # current prim orientation vs new normal orientation.
        # Plus, it is nice to see the normal of the object changing while snapping.
        snap_provider_enabled = self.snap_settings_listener.snap_enabled and self.snap_settings_listener.snap_provider

        # When the manipulator is being manipulated as local translate or scale, we do not want to change the rotation of
        # the manipulator even if it's rotated, otherwise the direction of moving or scaling will change and can be very hard to control.
        # It can happen when you move a prim that has a constraint on it (e.g. lookAt)
        # In this case keep the rotation the same as on_began
        return (
            mode == transform_c.TRANSFORM_MODE_LOCAL
            and (self._current_editing_op == Operation.TRANSLATE or self._current_editing_op == Operation.SCALE)
            and not snap_provider_enabled
        )

    def _should_keep_manipulator_translation_unchanged(self, mode: str) -> bool:
        # When the pivot placement is BBOX_CENTER and multiple prims being rotated, the bbox center may shifts, and the
        # rotation center will shift with them. This causes weird user experience. So we pin the rotation center until
        # mouse is released.
        return self._current_editing_op == Operation.ROTATE and (
            self._placement == Placement.BBOX_CENTER or self._placement == Placement.BBOX_BASE
        )

    def _get_transform_mode_for_current_op(self) -> str:
        mode = transform_c.TRANSFORM_MODE_LOCAL
        if self._op_settings_listener.selected_op == transform_c.TRANSFORM_OP_ROTATE:
            mode = self._op_settings_listener.rotation_mode
        elif self._op_settings_listener.selected_op == transform_c.TRANSFORM_OP_MOVE:
            mode = self._op_settings_listener.translation_mode

        return mode

    # Adds a delay to the visual update during translate (only) manipulation
    # It's due to the renderer having a delay of rendering the mesh and the manipulator appears to drift apart.
    # It's only an estimation and may varying from scene/renderer setup.
    async def _delay_dirty(self, transform, id):
        if self._viewport_fps:
            render_frame_time = 1.0 / self._viewport_fps * self._settings.get(TRANSLATE_DELAY_FRAME_SETTING)
            while True:
                dt = await self._app.next_update_async()
                render_frame_time -= dt
                # break a frame early
                if render_frame_time < dt:
                    break

        # cancel earlier job if a later one catches up (fps suddenly changed?)
        earlier_tasks_or_futures = []
        for key, task_or_future in self._delay_dirty_tasks_or_futures.items():
            if key < id:
                earlier_tasks_or_futures.append(key)
                task_or_future.cancel()
            else:
                break
        for key in earlier_tasks_or_futures:
            self._delay_dirty_tasks_or_futures.pop(key)

        self._transform = transform
        self._item_changed(self._transform_item)
        self._delay_dirty_tasks_or_futures.pop(id)

    def _update_temp_pivot_world_position(self):
        if type(self._transform) is not list:
            return
        new_world_position = self._transform[12:15]
        self._settings.set_float_array(self._selection_pivot_position_path, new_world_position)

    @carb.profiler.profile
    def _update_transform_from_prims(self):
        xform_flattened = self._calculate_transform_from_prim()
        if self._transform != xform_flattened:
            self._transform = xform_flattened
            # update setting with new pivot placement position
            self._update_temp_pivot_world_position()
            return True
        return False

    # def _calculate_transform_from_obj(self):
    def _calculate_transform_from_prim(self):
        if not self._data_accessor_selector.is_ready():
            return False
        if not self._data_accessor_selector.get_stage():
            return False
        if not self._pivot_prim:
            return False
        self._data_accessor_selector.clear_xform_cache()
        # cur_time = self._data_accessor_selector.get_current_time_code(self._current_time)
        mode = self._get_transform_mode_for_current_op()

        pivot_inv = self._data_accessor_selector.get_local_transform_pivot_inv(self._pivot_prim, self._current_time)
        if self._should_keep_manipulator_orientation_unchanged(mode):
            pivot_prim_path = self._pivot_prim.GetPath()

            (s, r, ro, t) = self._data_accessor_selector.get_local_transform_SRT(self._pivot_prim, self._current_time)
            pivot = self._data_accessor_selector.get_local_transform_pivot_inv(
                self._pivot_prim, self._current_time
            ).GetInverse()
            self.all_xformable_prim_data_curr[pivot_prim_path] = (s, r, ro, t) + (pivot,)

            # This method may be called from _on_op_listener_changed, before any gesture has started
            # in which case _all_xformable_prim_data_prev would be empty
            piv_xf_tuple = self._all_xformable_prim_data_prev.get(pivot_prim_path, False)
            if not piv_xf_tuple:
                piv_xf_tuple = self._data_accessor_selector.get_local_transform_SRT(
                    self._pivot_prim, self._current_time
                )
                pv_xf_pivot = self._data_accessor_selector.get_local_transform_pivot_inv(
                    self._pivot_prim, self._current_time
                ).GetInverse()
                self._all_xformable_prim_data_prev[self._pivot_prim.GetPath()] = piv_xf_tuple + (pv_xf_pivot,)
            (s_p, r_p, ro_p, t_p, t_piv) = piv_xf_tuple

            xform = construct_transform_matrix_from_SRT(t, r_p, ro_p, s, pivot_inv)
            parent = self._data_accessor_selector.get_local_to_world_transform(self._pivot_prim.GetParent())
            xform *= parent
        else:
            # *
            xform = self._data_accessor_selector.get_local_to_world_transform(self._pivot_prim)
        xform = pivot_inv.GetInverse() * xform

        if self._should_keep_manipulator_translation_unchanged(mode):
            xform.SetTranslateOnly((self._transform[12], self._transform[13], self._transform[14]))
        else:
            # if there's only one selection, we always use LAST_PRIM_PIVOT though
            if self._placement != Placement.LAST_PRIM_PIVOT and self._placement != Placement.REF_PRIM:
                average_translation = usdrt.Gf.Vec3d(0.0)
                if self._placement == Placement.BBOX_CENTER or self._placement == Placement.BBOX_BASE:
                    world_bound = usdrt.Gf.Range3d(
                        usdrt.Gf.Vec3d(3.4028234663852886e38, 3.4028234663852886e38, 3.4028234663852886e38),
                        usdrt.Gf.Vec3d(-3.4028234663852886e38, -3.4028234663852886e38, -3.4028234663852886e38),
                    )  # usdrt.Gf.Range3d()

                def get_prim_translation(xformable):
                    xformable_world_mtx = self._data_accessor_selector.get_local_to_world_transform(xformable)
                    xformable_pivot_inv = self._data_accessor_selector.get_local_transform_pivot_inv(
                        xformable, self._current_time
                    )
                    xformable_world_mtx = xformable_pivot_inv.GetInverse() * xformable_world_mtx
                    return xformable_world_mtx.ExtractTranslation()

                for path in self._xformable_prim_paths:
                    xformable = self._data_accessor_selector.get_prim_at_path(path)
                    if self._placement == Placement.SELECTION_CENTER:
                        average_translation += get_prim_translation(xformable)
                    elif self._placement == Placement.BBOX_CENTER or Placement.BBOX_BASE:
                        # *
                        # TODO: wait for iFabricHierarchy
                        bound_range = self._data_accessor_selector.usd_context.compute_path_world_bounding_box(
                            self._data_accessor_selector.get_string_path(path)
                        )
                        bound_range = usdrt.Gf.Range3d(usdrt.Gf.Vec3d(*bound_range[0]), usdrt.Gf.Vec3d(*bound_range[1]))
                        if not bound_range.IsEmpty():
                            world_bound = usdrt.Gf.Range3d.GetUnion(world_bound, bound_range)
                        else:
                            # extend world bound with tranlation for prims with zero bbox, e.g. Xform, Camera
                            # *
                            prim_translation = get_prim_translation(xformable)
                            world_bound.UnionWith(prim_translation)

                if self._placement == Placement.SELECTION_CENTER:
                    average_translation /= len(self._xformable_prim_paths)
                elif self._placement == Placement.BBOX_CENTER:
                    # *
                    average_translation = world_bound.GetMidpoint()
                elif self._placement == Placement.BBOX_BASE:
                    # xform may not have bbox but its descendants may have, exclude cases that only xform are selected
                    if not world_bound.IsEmpty():
                        bbox_center = world_bound.GetMidpoint()
                        bbox_size = world_bound.GetSize()

                        if (
                            self._data_accessor_selector.get_stage_up_axis()
                            == self._data_accessor_selector.get_data_accessor("USD").UsdGeom.Tokens.y
                        ):
                            # Y-up world
                            average_translation = bbox_center - usdrt.Gf.Vec3d(0.0, bbox_size[1] / 2.0, 0.0)
                        else:
                            # Z-up world
                            average_translation = bbox_center - usdrt.Gf.Vec3d(0.0, 0.0, bbox_size[2] / 2.0)
                    else:
                        # fallback to SELECTION_CENTER
                        average_translation /= len(self._xformable_prim_paths)

                # Only take the translate from selected prim average.
                # The rotation and scale still comes from pivot prim
                xform.SetTranslateOnly(average_translation)

        # instead of using RemoveScaleShear, additional steps made to handle negative scale properly
        scale, _, _, _ = self._data_accessor_selector.get_local_transform_SRT(self._pivot_prim, self._current_time)

        scale_epsilon = 1e-6
        for i in range(3):
            if usdrt.Gf.IsClose(scale[i], 0.0, scale_epsilon):
                scale[i] = -scale_epsilon if scale[i] < 0 else scale_epsilon

        inverse_scale = usdrt.Gf.Matrix4d().SetScale(usdrt.Gf.Vec3d(1.0 / scale[0], 1.0 / scale[1], 1.0 / scale[2]))
        xform = inverse_scale * xform
        # this is the average xform without scale
        self._no_scale_transform_manipulator = usdrt.Gf.Matrix4d(xform)
        # store the scale separately
        self._scale_manipulator = usdrt.Gf.Vec3d(scale)

        xform = xform.RemoveScaleShear()

        if mode == transform_c.TRANSFORM_MODE_GLOBAL:
            xform = xform.SetTranslate(xform.ExtractTranslation())

        return flatten(xform)

    def _on_op_listener_changed(self, type: OpSettingsListener.CallbackType, value: str):
        if type == OpSettingsListener.CallbackType.OP_CHANGED:
            # cancel all delayed tasks
            for task_or_future in self._delay_dirty_tasks_or_futures.values():
                task_or_future.cancel()
            self._delay_dirty_tasks_or_futures.clear()

            self._update_transform_from_prims()
            self._item_changed(self._transform_item)
        elif type == OpSettingsListener.CallbackType.TRANSLATION_MODE_CHANGED:
            if self._op_settings_listener.selected_op == transform_c.TRANSFORM_OP_MOVE:
                if self._update_transform_from_prims():
                    self._item_changed(self._transform_item)
        elif type == OpSettingsListener.CallbackType.ROTATION_MODE_CHANGED:
            if self._op_settings_listener.selected_op == transform_c.TRANSFORM_OP_ROTATE:
                if self._update_transform_from_prims():
                    self._item_changed(self._transform_item)

    def _update_placement(self, placement_str: str):
        if placement_str == prim_c.MANIPULATOR_PLACEMENT_SELECTION_CENTER:
            placement = Placement.SELECTION_CENTER
        elif placement_str == prim_c.MANIPULATOR_PLACEMENT_BBOX_CENTER:
            placement = Placement.BBOX_CENTER
        elif placement_str == prim_c.MANIPULATOR_PLACEMENT_PICK_REF_PRIM:
            placement = Placement.REF_PRIM
        elif placement_str == prim_c.MANIPULATOR_PLACEMENT_BBOX_BASE:
            placement = Placement.BBOX_BASE
        else:  # placement == prim_c.MANIPULATOR_PLACEMENT_LAST_PRIM_PIVOT or bad values
            placement = Placement.LAST_PRIM_PIVOT

        if placement != self._placement:
            if placement == Placement.LAST_PRIM_PIVOT and self._placement == Placement.REF_PRIM:
                # reset the pivot prim in case it was changed by MANIPULATOR_PLACEMENT_PICK_REF_PRIM
                if self._xformable_prim_paths:
                    self._pivot_prim = self._data_accessor_selector.get_prim_at_path(self._xformable_prim_paths[-1])

            self._placement = placement
            if self._update_transform_from_prims():
                self._item_changed(self._transform_item)

    def _on_placement_setting_changed(self, item, event_type):
        placement_str = self._dict.get(item)
        self._update_placement(placement_str)

    def _check_update_selected_instance_proxy_list(self, path: self._data_accessor_selector.Sdf.Path, resynced):
        def track_or_remove_from_instance_proxy_list(prim):
            valid_proxy = (
                prim
                and self._data_accessor_selector.is_prim_active(prim)
                and self._data_accessor_selector.is_instance_proxy(prim)
            )
            if valid_proxy:
                self._selected_instance_proxy_paths.add(prim.GetPath())
            else:
                self._selected_instance_proxy_paths.discard(prim.GetPath())

        prim_path = path
        changed_prim = self._data_accessor_selector.get_prim_at_path(prim_path)

        # Update list of instance proxy paths.
        if resynced and path.IsPrimPath():
            if prim_path in self._consolidated_xformable_prim_paths:
                # Quick path if it's selected already.
                track_or_remove_from_instance_proxy_list(changed_prim)
            else:
                # Slow path to verify if any of its ancestors are changed.
                for path in self._consolidated_xformable_prim_paths:
                    if not self._data_accessor_selector.prim_has_prefix(path, prim_path):
                        continue

                    prim = self._data_accessor_selector.get_prim_at_path(path)
                    track_or_remove_from_instance_proxy_list(prim)

    @carb.profiler.profile
    async def _update_transform_from_prims_async(self):
        try:
            check_all_prims = (
                self._placement != Placement.LAST_PRIM_PIVOT
                and self._placement != Placement.REF_PRIM
                and len(self._xformable_prim_paths) > 1
            )
            pivot_prim_path = self._pivot_prim.GetPath()

            for p, resynced in self._pending_changed_paths.items():
                self._check_update_selected_instance_proxy_list(p, resynced)

                prim_path = p.GetPrimPath()
                # Update either check_all_prims
                #        or prim_path is a prefix of pivot_prim_path (pivot prim's parent affect pivot prim transform)
                # Note: If you move the manipulator and the prim flies away while manipulator stays in place, check this
                #       condition!
                if (
                    # check _xformable_prim_paths_prefix_set so that if the parent path of selected prim(s) changed, it
                    # can still update manipulator transform
                    prim_path in self._xformable_prim_paths_prefix_set
                    if check_all_prims
                    else self._data_accessor_selector.prim_has_prefix(pivot_prim_path, prim_path)
                ):
                    if self._path_may_affect_transform(p):
                        # only delay the visual update in translate mode.
                        should_delay_frame = self._settings.get(TRANSLATE_DELAY_FRAME_SETTING) > 0
                        if (
                            self._op_settings_listener.selected_op == transform_c.TRANSFORM_OP_MOVE
                            and should_delay_frame
                        ):
                            xform = self._calculate_transform_from_prim()
                            id = self._app.get_update_number()
                            self._delay_dirty_tasks_or_futures[id] = run_coroutine(self._delay_dirty(xform, id))
                        else:
                            if self._update_transform_from_prims():
                                self._item_changed(self._transform_item)
                        break
        except Exception as e:
            carb.log_error(traceback.format_exc())
        finally:
            self._pending_changed_paths.clear()
            self._update_prim_xform_from_prim_task_or_future = None

    @carb.profiler.profile
    def on_objects_changed(self, resynced_paths, changed_info_only_paths, data_source=None):
        """Called when objects in the stage have changed.

        Args:
            args (List): A list of changed objects.

        Keyword Args:
            kwds (Dict): Additional keyword arguments with details about the changes."""
        if not self._pivot_prim:
            return
        # collect resynced paths so that removed/added xformOps triggers refresh
        for path in resynced_paths:  # notice.GetResyncedPaths():
            prim_path = path.GetPrimPath()
            # to avoid double call from Fabric and USD, TEMPORARY
            if prim_path in self._xformable_prim_paths_prefix_set:
                if self._data_accessor_selector.get_data_accessor(data_source).is_valid_path(prim_path):
                    self._pending_changed_paths[path] = True
        # collect changed only paths
        changed_info_only_paths_valid = []
        for path in changed_info_only_paths:  # notice.GetChangedInfoOnlyPaths():
            prim_path = path.GetPrimPath()
            # to avoid double call from Fabric and USD, TEMPORARY
            if prim_path in self._xformable_prim_paths_prefix_set:
                if self._data_accessor_selector.get_data_accessor(data_source).is_valid_path(prim_path):
                    self._pending_changed_paths[path] = False
                    changed_info_only_paths_valid.append(path)
        # if an operation is in progess, record all dirty xform path
        if self._current_editing_op is not None and not self._ignore_xform_data_change:
            # self._pending_changed_paths_for_xform_data.update(changedInfoOnlyPaths)
            self._pending_changed_paths_for_xform_data.update(changed_info_only_paths_valid)
        if (
            self._update_prim_xform_from_prim_task_or_future is None
            or self._update_prim_xform_from_prim_task_or_future.done()
        ):
            self._update_prim_xform_from_prim_task_or_future = run_coroutine(self._update_transform_from_prims_async())

    def _set_default_settings(self):
        self._settings.set_default(TRANSFORM_GIZMO_CUSTOM_MANIPULATOR_ENABLED, False)
        self._settings.set_default(TRANSFORM_GIZMO_IS_USING, False)
        self._settings.set_default(TRANSFORM_GIZMO_TRANSLATE_DELTA_XYZ, [0, 0, 0])
        self._settings.set_default(TRANSFORM_GIZMO_ROTATE_DELTA_XYZW, [0, 0, 0, 1])
        self._settings.set_default(TRANSFORM_GIZMO_SCALE_DELTA_XYZ, [0, 0, 0])

    def _should_skip_custom_manipulator_path(self, path: str) -> bool:
        custom_manipulator_path_prims_settings_path = TRANSFORM_GIZMO_CUSTOM_MANIPULATOR_PRIMS + path
        return self._settings.get(custom_manipulator_path_prims_settings_path)

    @carb.profiler.profile
    def _path_may_affect_transform(self, path: self._data_accessor_selector.Sdf.Path) -> bool:
        # Batched changes sent in a SdfChangeBlock may not have property name but only the prim path
        return (
            not path.ContainsPropertyElements()
            or self._data_accessor_selector.is_transformation_affected_by_attr_named(path)
        )

    def decompose_to_eulers(self, q: usdrt.Gf.Quatd, ro: usdrt.Gf.Vec3i) -> usdrt.Gf.Vec3d:
        """Decomposes a quaternion into Euler angles based on a rotation order.

        Args:
            q (:obj:`usdrt.Gf.Quatd`): The quaternion to decompose.
            ro (:obj:`usdrt.Gf.Vec3i`): The rotation order as a vector of 3 integers.

        Returns:
            :obj:`usdrt.Gf.Vec3d`: The decomposed Euler angles."""
        axes = [usdrt.Gf.Vec3d.XAxis(), usdrt.Gf.Vec3d.YAxis(), usdrt.Gf.Vec3d.ZAxis()]
        return q.Decompose(axes[ro[2]], axes[ro[1]], axes[ro[0]])

    @property
    def custom_manipulator_enabled(self):
        """Gets whether a custom manipulator is enabled.

        Returns:
            bool: True if a custom manipulator is enabled, False otherwise."""
        return self._custom_manipulator_enabled

    @property
    def snap_settings_listener(self):
        """Gets the snap settings listener instance.

        Returns:
            :obj:`SnapSettingsListener`: The snap settings listener object."""
        return self._snap_settings_listener

    @property
    def op_settings_listener(self):
        """Gets the operation settings listener instance.

        Returns:
            :obj:`OpSettingsListener`: The operation settings listener object."""
        return self._op_settings_listener

    @property
    def usd_context(self) -> omni.usd.UsdContext:
        """Gets the USD context for the prim transform model.

        Returns:
            :obj:`UsdContext`: The USD context associated with the model."""
        return self._data_accessor_selector.usd_context

    @property
    def xformable_prim_paths(self) -> List[self._data_accessor_selector.Sdf.Path]:
        """Gets the list of transformable prim paths.

        Returns:
            List[:obj:`Sdf.Path`]: The list of xformable prim paths."""
        return self._xformable_prim_paths
