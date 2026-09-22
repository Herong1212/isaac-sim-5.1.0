# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""This module defines classes for managing gestures and manipulators related to reference primitive markers in USD stages within the Omniverse Kit."""


from __future__ import annotations

import asyncio
import colorsys
import concurrent.futures
import weakref
from collections import defaultdict
from typing import DefaultDict, Dict, Set, Union
from weakref import ProxyType

import carb
import carb.dictionary
import carb.events
import carb.profiler
import carb.settings
import omni.timeline
import omni.usd
from carb.eventdispatcher import get_eventdispatcher
from omni.kit.async_engine import run_coroutine
from omni.kit.manipulator.transform import COLOR_X, COLOR_Y, COLOR_Z
from omni.kit.manipulator.transform import Constants as TrCon
from omni.kit.manipulator.transform import abgr_to_color
from omni.kit.viewport.manipulator.transform import Viewport1WindowState
from omni.ui import color as cl
from omni.ui import scene as sc
from pxr import Sdf, Tf, Usd, UsdGeom

from .model import PrimTransformModel
from .settings_constants import Constants
from .utils import flatten  # , get_local_transform_pivot_inv

LARGE_SELECTION_CAP = 20


class PreventViewportOthers(sc.GestureManager):
    """A class that provides gesture management capabilities to prevent viewport interactions from being blocked by other gestures.

    This class is designed to work within a viewport context, determining if certain gestures should be prevented based on the state and type of other gestures that are currently active. It primarily focuses on enhancing user interaction with the viewport by ensuring that more critical gestures take precedence and are not hindered by others. The class achieves this through its methods `can_be_prevented` and `should_prevent`, which assess and decide whether a gesture should be allowed to continue or be prevented in favor of another.

    The class inherits from `sc.GestureManager`, leveraging its capabilities to manage and prioritize gestures within the viewport.
    """

    def can_be_prevented(self, gesture):
        """Determines if the gesture can be prevented.

        Args:
            gesture (:obj:`sc.Gesture`): The gesture to be evaluated for prevention.

        Returns:
            bool: True if the gesture can be prevented, otherwise False."""
        return True

    def should_prevent(self, gesture, preventer):
        """Decides if an ongoing gesture should be prevented by another gesture.

        Args:
            gesture (:obj:`sc.Gesture`): The ongoing gesture to be evaluated.
            preventer (:obj:`sc.Gesture`): The gesture that might prevent the ongoing one.

        Returns:
            bool: True if the ongoing gesture should be prevented, otherwise False."""
        if preventer.state == sc.GestureState.BEGAN or preventer.state == sc.GestureState.CHANGED:
            if issubclass(type(preventer), ClickMarkerGesture):
                if issubclass(type(gesture), ClickMarkerGesture):
                    return gesture.gesture_payload.ray_distance > preventer.gesture_payload.ray_distance
                elif isinstance(gesture, ClickMarkerGesture):
                    return False
                else:
                    return True
            else:
                return True

        return super().should_prevent(gesture, preventer)


class ClickMarkerGesture(sc.DragGesture):
    """A gesture class for handling click-to-mark operations on 3D markers in a viewport.

    This class extends the sc.DragGesture class to implement specific behavior for clicking on 3D markers that represent points of interest in a scene. It is typically used in the context of a 3D editing application to allow users to select or manipulate reference points on 3D primitives.

    Args:
        prim_path (:obj:`Sdf.Path`): The USD path to the primitive associated with the marker.
        marker (ProxyType[:obj:`ReferencePrimMarker`]): A weak proxy reference to the associated ReferencePrimMarker instance.
    """

    def __init__(
        self,
        prim_path: Sdf.Path,
        marker: ProxyType[ReferencePrimMarker],
    ):
        """Initializes a ClickMarkerGesture instance."""
        super().__init__(manager=PreventViewportOthers())
        self._prim_path = prim_path
        self._marker = marker
        self._vp1_window_state = None

    def on_began(self):
        """Called when the gesture begins."""
        self._viewport_on_began()

    def on_canceled(self):
        """Called when the gesture is canceled."""
        self._viewport_on_ended()

    def on_ended(self):
        """Called when the gesture ends."""
        self._viewport_on_ended()
        self._marker.on_pivot_marker_picked(self._prim_path)

    def _viewport_on_began(self):
        self._viewport_on_ended()
        if self._marker.legacy:
            self._vp1_window_state = Viewport1WindowState()

    def _viewport_on_ended(self):
        if self._vp1_window_state:
            self._vp1_window_state.destroy()
            self._vp1_window_state = None


class MarkerHoverGesture(sc.HoverGesture):
    """A class representing a hover gesture over markers in a 3D viewport.

    This class manages hover interactions with visual markers, such as lines and arcs, making them brighter when hovered over. It tracks the beginning and ending of hover gestures, adjusting the visual representation of items to indicate active hover states.

    Args:
        args: Variable length argument list.

    Keyword Args:
        Any additional keyword arguments."""

    def __init__(self, *args, **kwargs):
        """Constructor method for MarkerHoverGesture.

        This method does not need a detailed description."""
        super().__init__(*args, **kwargs)
        self.items = []
        self._began_count = 0
        self._original_colors = []
        self._original_ends = []

    def on_began(self):
        """Callback for when the hover gesture begins with no additional interactions."""
        self._began_count += 1
        if self._began_count == 1:
            self._original_colors = [None] * len(self.items)
            self._original_ends = [None] * len(self.items)
            for i, item in enumerate(self.items):
                self._original_colors[i] = item.color
                item.color = self._make_brighter(item.color)

                if isinstance(item, sc.Line):
                    self._original_ends[i] = item.end
                    end = [dim * 1.2 for dim in item.end]
                    item.end = end

                if isinstance(item, sc.Arc):
                    ...  # TODO change color to white, blocked by OM-56044

    def on_ended(self):
        """Callback for when the hover gesture ends with no additional interactions."""
        self._began_count -= 1
        if self._began_count <= 0:
            self._began_count = 0
            for i, item in enumerate(self.items):
                item.color = self._original_colors[i]

                if isinstance(item, sc.Line):
                    item.end = self._original_ends[i]

                if isinstance(item, sc.Arc):
                    ...  # TODO change color back, blocked by OM-56044

    def _make_brighter(self, color):
        hsv = colorsys.rgb_to_hsv(color[0], color[1], color[2])
        rgb = colorsys.hsv_to_rgb(hsv[0], hsv[1], hsv[2] * 1.2)
        return cl(rgb[0], rgb[1], rgb[2], color[3])


class ReferencePrimMarker(sc.Manipulator):
    """A class representing a manipulator for reference primitive markers in USD stages.

    This manipulator visually represents selectable primitives in a 3D scene and allows users to pick a reference primitive as a pivot for transformations using a custom gesture. It is a subclass of `sc.Manipulator` and provides a custom user interface in the viewport.

    Args:
        usd_context_name (str): The name of the USD context to operate within. An empty string will use the default context.
        manipulator_model (Optional[:obj:`ProxyType[PrimTransformModel]`]): The data model used by the manipulator for transformations. If `None`, no model is used.
        legacy (bool): A flag indicating whether to use legacy behavior. Defaults to `False`.

    The manipulator listens to USD stage events, timeline changes, and selection changes to update its state and appearance in the viewport. It also handles custom gestures for user interaction with the viewport markers.
    """

    def __init__(
        self, usd_context_name: str = "", manipulator_model: ProxyType[PrimTransformModel] = None, legacy: bool = False
    ):
        """Initializes a new instance of the ReferencePrimMarker."""
        super().__init__()
        self._settings = carb.settings.get_settings()
        self._dict = carb.dictionary.get_dictionary()
        self._usd_context_name = usd_context_name
        self._usd_context = omni.usd.get_context(self._usd_context_name)
        self._manipulator_model = manipulator_model
        if manipulator_model != None:
            self._data_accessor_selector = self._manipulator_model.get_da()
        else:
            self._data_accessor_selector = None
        self._legacy = legacy
        self._selection = self._usd_context.get_selection()
        self._timeline = omni.timeline.get_timeline_interface()
        self._current_time = self._timeline.get_current_time()

        # dict from prefixes -> dict of affected markers.
        self._markers: DefaultDict[Dict] = defaultdict(dict)
        self._stage_listener = None
        self._pending_changed_paths: Set[Sdf.Path] = set()
        self._process_pending_change_task_or_future: Union[asyncio.Task, concurrent.futures.Future, None] = None

        # order=1 to ensure the event handler is called after prim manipulator
        self._stage_event_sub = get_eventdispatcher().observe_event(
            observer_name="omni.kit.manipulator.prim.core:reference_prim_marker",
            event_name=self._usd_context.stage_event_name(omni.usd.StageEventType.SELECTION_CHANGED),
            on_event=lambda _: self._on_selection_changed(),
            order=1,
        )

        self._placement_sub = self._settings.subscribe_to_node_change_events(
            Constants.MANIPULATOR_PLACEMENT_SETTING, self._on_placement_changed
        )
        self._placement = self._settings.get(Constants.MANIPULATOR_PLACEMENT_SETTING)

        self._op_sub = self._settings.subscribe_to_node_change_events(TrCon.TRANSFORM_OP_SETTING, self._on_op_changed)
        self._selected_op = self._settings.get(TrCon.TRANSFORM_OP_SETTING)

    def destroy(self):
        """Cleans up resources and subscriptions."""
        self._stage_event_sub = None
        if self._placement_sub:
            self._settings.unsubscribe_to_change_events(self._placement_sub)
            self._placement_sub = None

        if self._op_sub:
            self._settings.unsubscribe_to_change_events(self._op_sub)
            self._op_sub = None

        if self._stage_listener:
            self._data_accessor_selector.remove_update_callback_ref_prim_maker(self._stage_listener)
            # self._stage_listener.Revoke()
            self._stage_listener = None

        if self._process_pending_change_task_or_future and not self._process_pending_change_task_or_future.done():
            self._process_pending_change_task_or_future.cancel()
            self._process_pending_change_task_or_future = None

        self._timeline_sub = None

    @property
    def usd_context_name(self) -> str:
        """Gets the USD context name.

        Returns:
            str: The current USD context name."""
        return self._usd_context_name

    @usd_context_name.setter
    def usd_context_name(self, value: str):
        """Sets the USD context name.

        Args:
            value (str): The name of the USD context."""
        if value != self._usd_context_name:
            new_usd_context = omni.usd.get_context(value)

            if not new_usd_context:
                carb.log_error(f"Invalid usd context name {value}")
                return

            if self._stage_listener:
                # self._stage_listener.Revoke()
                self._data_accessor_selector.remove_update_callback_ref_prim_maker(self._stage_listener)
                self._stage_listener = None
            self._usd_context_name = value
            self._usd_context = new_usd_context

            # order=1 to ensure the event handler is called after prim manipulator
            self._stage_event_sub = get_eventdispatcher().observe_event(
                observer_name="omni.kit.manipulator.prim.core:reference_prim_marker",
                event_name=self._usd_context.stage_event_name(omni.usd.StageEventType.SELECTION_CHANGED),
                on_event=lambda _: self._on_selection_changed(),
                order=1,
            )
            self.invalidate()

    @property
    def manipulator_model(self) -> ProxyType[PrimTransformModel]:
        """Gets the manipulator model.

        Returns:
            :obj:`ProxyType[PrimTransformModel]`: The current manipulator model."""
        return self._manipulator_model

    @manipulator_model.setter
    def manipulator_model(self, value):
        """Sets the manipulator model.

        Args:
            value (:obj:`ProxyType[PrimTransformModel]`): The manipulator model."""
        if value != self._manipulator_model:
            self._manipulator_model = value
            self._data_accessor_selector = self._manipulator_model.get_da()
            self.invalidate()

    @property
    def legacy(self) -> bool:
        """Gets the legacy mode state.

        Returns:
            bool: True if legacy mode is enabled, false otherwise."""
        return self._legacy

    @legacy.setter
    def legacy(self, value):
        """Sets the legacy mode.

        Args:
            value (bool): If true, enables legacy mode."""
        self._legacy = value

    def on_pivot_marker_picked(self, path: Sdf.Path):
        """Handles the event when a pivot marker is picked.

        Args:
            path (:obj:`Sdf.Path`): The path of the picked pivot marker."""
        if self._manipulator_model.set_pivot_prim_path(path):
            # Hide marker on the new pivot prim and show marker on old pivot prim
            old_pivot_marker = self._markers.get(self._pivot_prim_path, {}).get(self._pivot_prim_path, None)
            if old_pivot_marker:
                old_pivot_marker.visible = True

            self._pivot_prim_path = self._manipulator_model.get_pivot_prim_path()

            new_pivot_marker = self._markers.get(self._pivot_prim_path, {}).get(self._pivot_prim_path, None)
            if new_pivot_marker:
                new_pivot_marker.visible = False

    def on_build(self):
        """Builds or rebuilds the ReferencePrimMarker."""
        if self._stage_listener:
            if self._data_accessor_selector != None:
                self._data_accessor_selector.remove_update_callback_ref_prim_maker(self._stage_listener)
            # self._stage_listener.Revoke()
            self._stage_listener = None

        self._timeline_sub = None
        self._markers.clear()

        if self._placement != Constants.MANIPULATOR_PLACEMENT_PICK_REF_PRIM:
            return

        # don't build marker on "select" mode
        if self._selected_op == TrCon.TRANSFORM_OP_SELECT:
            return

        # selected_xformable_paths = [p if isinstance(p, Sdf.Path) else Sdf.Path(p.GetString()) for p in self._manipulator_model.xformable_prim_paths]
        selected_xformable_paths = [p for p in self._manipulator_model.xformable_prim_paths]
        stage = self._usd_context.get_stage()
        self._current_time = self._timeline.get_current_time()

        selection_count = len(selected_xformable_paths)

        # skip if there's only one xformable
        if selection_count <= 1:
            return

        if selection_count > LARGE_SELECTION_CAP:
            carb.log_warn(
                f"{selection_count} is greater than the maximum selection cap {LARGE_SELECTION_CAP}, "
                f"{Constants.MANIPULATOR_PLACEMENT_PICK_REF_PRIM} mode will be disabled and fallback to "
                f"{Constants.MANIPULATOR_PLACEMENT_LAST_PRIM_PIVOT} due to performance concern."
            )
            return

        # timecode = self._get_current_time_code()
        self._pivot_prim_path = self._manipulator_model.get_pivot_prim_path()
        # xform_cache = UsdGeom.XformCache(timecode)

        for path in selected_xformable_paths:
            prim = self._data_accessor_selector.get_prim_at_path(path)
            # TODO: add timecode
            pivot_inv = self._data_accessor_selector.get_local_transform_pivot_inv(
                prim, self._manipulator_model._current_time
            )
            transform = pivot_inv.GetInverse() * self._data_accessor_selector.get_local_to_world_transform(prim)
            transform.Orthonormalize()  # in case of a none uniform scale

            marker_transform = sc.Transform(transform=flatten(transform), visible=self._pivot_prim_path != path)
            with marker_transform:
                with sc.Transform(scale_to=sc.Space.SCREEN):
                    gesture = ClickMarkerGesture(path, marker=weakref.proxy(self))
                    hover_gesture = MarkerHoverGesture()
                    x_line = sc.Line(
                        (0, 0, 0),
                        (50, 0, 0),
                        color=abgr_to_color(COLOR_X),
                        thickness=2,
                        intersection_thickness=8,
                        gestures=[gesture, hover_gesture],
                    )
                    y_line = sc.Line(
                        (0, 0, 0),
                        (0, 50, 0),
                        color=abgr_to_color(COLOR_Y),
                        thickness=2,
                        intersection_thickness=8,
                        gestures=[gesture, hover_gesture],
                    )
                    z_line = sc.Line(
                        (0, 0, 0),
                        (0, 0, 50),
                        color=abgr_to_color(COLOR_Z),
                        thickness=2,
                        intersection_thickness=8,
                        gestures=[gesture, hover_gesture],
                    )
                    with sc.Transform(look_at=sc.Transform.LookAt.CAMERA):
                        point = sc.Arc(
                            radius=6,
                            wireframe=False,
                            tesselation=8,
                            color=cl.white,  # TODO default color grey, blocked by OM-56044
                        )
                    hover_gesture.items = [x_line, y_line, z_line, point]

            prefixes = path.GetPrefixes()
            for prefix in prefixes:
                self._markers[prefix][path] = marker_transform

        if self._markers:
            # self._stage_listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._on_objects_changed, stage)
            self._stage_listener = self._data_accessor_selector.setup_update_callback_ref_prim_maker(
                self._on_objects_changed
            )

            self._timeline_sub = self._timeline.get_timeline_event_stream().create_subscription_to_pop(
                self._on_timeline_event
            )

    def _on_selection_changed(self):
        if self._placement == Constants.MANIPULATOR_PLACEMENT_PICK_REF_PRIM:
            self.invalidate()

    def _on_placement_changed(self, item, event_type):
        placement = self._dict.get(item)
        if placement != self._placement:
            self._placement = placement
            self.invalidate()

    def _on_op_changed(self, item, event_type):
        selected_op = self._dict.get(item)
        if selected_op != self._selected_op:
            if selected_op == TrCon.TRANSFORM_OP_SELECT or self._selected_op == TrCon.TRANSFORM_OP_SELECT:
                self.invalidate()
            self._selected_op = selected_op

    def _on_timeline_event(self, e: carb.events.IEvent):
        if e.type == int(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED):
            current_time = e.payload["currentTime"]
            if current_time != self._current_time:
                self._current_time = current_time
                if self._placement != Constants.MANIPULATOR_PLACEMENT_PICK_REF_PRIM:
                    # TODO only invalidate transform if this prim or ancestors transforms are time varying?
                    self.invalidate()

    @carb.profiler.profile
    async def _process_pending_change(self):
        processed_transforms = set()
        # xform_cache = UsdGeom.XformCache(timecode)
        stage = self._usd_context.get_stage()

        for path in self._pending_changed_paths:
            prim_path = path.GetPrimPath()
            affected_transforms = self._markers.get(prim_path, {})
            if affected_transforms:
                # if not UsdGeom.Xformable.is_transformation_affected_by_attr_named(path.name):
                # TODO: wait for iFabricHierarchy
                # return back for USD
                if not self._data_accessor_selector.is_transformation_affected_by_attr_named(path):
                    continue

                for path0, transform in affected_transforms.items():
                    if transform in processed_transforms:
                        continue
                    prim = self._data_accessor_selector.get_prim_at_path(path0)
                    if not prim:
                        continue
                    pivot_inv = self._data_accessor_selector.get_local_transform_pivot_inv(
                        prim, self._manipulator_model._current_time
                    )
                    xform = pivot_inv.GetInverse() * self._data_accessor_selector.get_local_to_world_transform(prim)
                    xform.Orthonormalize()  # in case of a none uniform scale

                    transform_value = flatten(xform)
                    transform.transform = transform_value
                    processed_transforms.add(transform)

        self._pending_changed_paths.clear()

    @carb.profiler.profile
    def _on_objects_changed(self, resynced_paths, changed_info_only_paths, data_source=None):
        changed_info_only_paths_valid = []
        for path in changed_info_only_paths:  # notice.GetChangedInfoOnlyPaths():
            prim_path = path.GetPrimPath()
            if self._data_accessor_selector.get_data_accessor(data_source).is_valid_path(prim_path):
                changed_info_only_paths_valid.append(path)
        self._pending_changed_paths.update(changed_info_only_paths_valid)

        if self._process_pending_change_task_or_future is None or self._process_pending_change_task_or_future.done():
            self._process_pending_change_task_or_future = run_coroutine(self._process_pending_change())

    def _get_current_time_code(self):
        return Usd.TimeCode(
            omni.usd.get_frame_time_code(self._current_time, self._usd_context.get_stage().GetTimeCodesPerSecond())
        )
