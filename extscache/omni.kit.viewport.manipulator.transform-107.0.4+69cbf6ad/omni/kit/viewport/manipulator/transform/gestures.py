# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from __future__ import annotations

__all__ = [
    "ViewportTransformChangedGestureBase",
    "ViewportTranslateChangedGesture",
    "ViewportRotateChangedGesture",
    "ViewportScaleChangedGesture",
]

import asyncio
import math
import traceback
from enum import Enum, Flag, IntEnum, auto
from typing import Dict, List, Sequence, Set, Tuple, Union
import concurrent.futures

import carb
import carb.dictionary
import carb.events
import carb.profiler
import carb.settings
import omni.kit.app
from omni.kit.async_engine import run_coroutine
import omni.kit.commands
import omni.kit.undo
import omni.timeline


from omni.kit.manipulator.tool.snap import SnapProviderManager

# from omni.kit.manipulator.tool.snap import settings_constants as snap_c
from omni.kit.manipulator.transform import (
    RotateChangedGesture,
    RotateDragGesturePayload,
    ScaleChangedGesture,
    ScaleDragGesturePayload,
    TransformDragGesturePayload,
    TranslateChangedGesture,
    TranslateDragGesturePayload,
    Operation,
)
from omni.kit.manipulator.transform import Constants as transform_c
from omni.ui import scene as sc

from .model import ViewportTransformModel, ManipulationMode, Viewport1WindowState
from .utils import flatten

from usdrt import Gf


class ViewportTransformChangedGestureBase:
    """A base class for viewport transform changed gestures.

    This class provides the foundational functionality for handling changes in viewport transforms, including translating, rotating, and scaling gestures. It interacts with the USD context and viewport API to manage transformation operations and update the viewport accordingly.

    Args:
        usd_context_name (str): The name of the USD context to be used for the transformations.
        viewport_api: The API of the viewport to be manipulated.
    """

    def __init__(self, usd_context_name: str = "", viewport_api=None):
        """Initializes the ViewportTransformChangedGestureBase class."""
        self._settings = carb.settings.get_settings()
        self._usd_context_name = usd_context_name
        self._usd_context = omni.usd.get_context(self._usd_context_name)
        self._viewport_api = viewport_api  # VP2
        self._vp1_window_state = None
        self._stage_id = None

    def on_began(self, payload_type=TransformDragGesturePayload):
        """Handles the beginning of a gesture.

        Args:
            payload_type (type): Type of the payload for the gesture.
        """
        self._viewport_on_began()

        if not self.gesture_payload or not self.sender or not isinstance(self.gesture_payload, payload_type):
            return

        model = self.sender.model
        if not model:
            return

        item = self.gesture_payload.changing_item
        self._current_editing_op = item.operation

        # NOTE! self._begin_xform has no scale. To get the full matrix, do self._begin_scale_mtx * self._begin_xform
        self._begin_xform = Gf.Matrix4d(*model.get_as_floats(model.get_item("no_scale_transform_manipulator")))

        manip_scale = Gf.Vec3d(*model.get_as_floats(model.get_item("scale_manipulator")))
        self._begin_scale_mtx = Gf.Matrix4d(1.0)
        self._begin_scale_mtx.SetScale(manip_scale)

        model.set_floats(model.get_item("viewport_fps"), [0.0])

        model.on_began(self.gesture_payload)

    def on_changed(self, payload_type=TransformDragGesturePayload):
        """Handles changes during a gesture.

        Args:
            payload_type (type): Type of the payload for the gesture.
        """
        if not self.gesture_payload or not self.sender or not isinstance(self.gesture_payload, payload_type):
            return

        model = self.sender.model
        if not model:
            return

        if self._viewport_api:
            fps = self._viewport_api.frame_info.get("fps")
            model.set_floats(model.get_item("viewport_fps"), [fps])

        model.on_changed(self.gesture_payload)

    def on_ended(self, payload_type=TransformDragGesturePayload):
        """Handles the end of a gesture.

        Args:
            payload_type (type): Type of the payload for the gesture.
        """
        self._viewport_on_ended()
        if not self.gesture_payload or not self.sender or not isinstance(self.gesture_payload, payload_type):
            return

        model = self.sender.model
        if not model:
            return

        item = self.gesture_payload.changing_item
        if item.operation != self._current_editing_op:
            return

        model.set_floats(model.get_item("viewport_fps"), [0.0])

        model.on_ended(self.gesture_payload)

        self._current_editing_op = None

    def on_canceled(self, payload_type=TransformDragGesturePayload):
        """Handles the cancellation of a gesture.

        Args:
            payload_type (type): Type of the payload for the gesture.
        """
        self._viewport_on_ended()
        if not self.gesture_payload or not self.sender or not isinstance(self.gesture_payload, payload_type):
            return

        model = self.sender.model
        if not model:
            return

        item = self.gesture_payload.changing_item
        if item.operation != self._current_editing_op:
            return

        model.on_canceled(self.gesture_payload)

        self._current_editing_op = None

    def _publish_delta(self, operation: Operation, delta: List[float]):
        if operation == Operation.TRANSLATE:
            self._settings.set_float_array(TRANSFORM_GIZMO_TRANSLATE_DELTA_XYZ, delta)
        elif operation == Operation.ROTATE:
            self._settings.set_float_array(TRANSFORM_GIZMO_ROTATE_DELTA_XYZW, delta)
        elif operation == Operation.SCALE:
            self._settings.set_float_array(TRANSFORM_GIZMO_SCALE_DELTA_XYZ, delta)

    def __set_viewport_manipulating(self, value: int):
        # Signal that user-manipulation has started for this stage
        if self._stage_id is None:
            # self._stage_id = UsdUtils.StageCache.Get().GetId(self._usd_context.get_stage()).ToLongInt()
            self._stage_id = self._usd_context.get_stage_id()
        key = f"/app/viewport/{self._stage_id}/manipulating"
        cur_value = self._settings.get(key) or 0
        self._settings.set(key, cur_value + value)

    def _viewport_on_began(self):
        self._viewport_on_ended()
        if self._viewport_api is None:
            self._vp1_window_state = Viewport1WindowState()
        self.__set_viewport_manipulating(1)

    def _viewport_on_ended(self):
        if self._vp1_window_state:
            self._vp1_window_state.destroy()
            self._vp1_window_state = None
        if self._stage_id:
            self.__set_viewport_manipulating(-1)
            self._stage_id = None


class ViewportTranslateChangedGesture(TranslateChangedGesture, ViewportTransformChangedGestureBase):
    """A class for handling translation gestures in a viewport.

    This class extends the TranslateChangedGesture and ViewportTransformChangedGestureBase classes to provide
    functionality for handling translation gestures within a viewport environment. It supports snapping and
    delta publications for translation operations.

    Args:
        snap_manager (SnapProviderManager): Manages snapping behavior during translation.

    Keyword Args:
        usd_context_name (str): Name of the USD context.
        viewport_api: API for interacting with the viewport.
    """

    def __init__(self, snap_manager: SnapProviderManager, **kwargs):
        """Initializes the ViewportTranslateChangedGesture class."""
        ViewportTransformChangedGestureBase.__init__(self, **kwargs)
        TranslateChangedGesture.__init__(self)
        self._accumulated_translate = Gf.Vec3d(0)
        self._snap_manager = snap_manager

    def on_began(self):
        """Handles the beginning of a translate gesture."""
        ViewportTransformChangedGestureBase.on_began(self, TranslateDragGesturePayload)
        self._accumulated_translate = Gf.Vec3d(0)

        model = self._get_model(TranslateDragGesturePayload)
        if model and self._can_snap(model):
            # TODO No need for gesture=self when VP1 has viewport_api
            self._snap_manager.on_began(model.consolidated_xformable_prim_data_curr.keys(), gesture=self)

        if model:
            model.set_floats(model.get_item("translate_delta"), [0, 0, 0])

    def on_ended(self):
        """Handles the end of a translate gesture."""
        ViewportTransformChangedGestureBase.on_ended(self, TranslateDragGesturePayload)

        model = self._get_model(TranslateDragGesturePayload)
        if model and self._can_snap(model):
            self._snap_manager.on_ended()

    def on_canceled(self):
        """Handles the cancellation of a translate gesture."""
        ViewportTransformChangedGestureBase.on_canceled(self, TranslateDragGesturePayload)

        model = self._get_model(TranslateDragGesturePayload)
        if model and self._can_snap(model):
            self._snap_manager.on_ended()

    @carb.profiler.profile
    def on_changed(self):
        """Handles changes during a translate gesture.

        Args:
            args: Arguments for the gesture change event.

        Keyword Args:
            key1 (type): Description of key1.
            key2 (type): Description of key2.
        """
        ViewportTransformChangedGestureBase.on_changed(self, TranslateDragGesturePayload)

        model = self._get_model(TranslateDragGesturePayload)
        if not model:
            return

        manip_xform = Gf.Matrix4d(*model.get_as_floats(model.get_item("no_scale_transform_manipulator")))
        new_manip_xform = Gf.Matrix4d(manip_xform)
        rotation_mtx = manip_xform.ExtractRotationMatrix()
        rotation_mtx.Orthonormalize()

        translate_delta = self.gesture_payload.moved_delta
        translate = self.gesture_payload.moved
        axis = self.gesture_payload.axis

        # slow Gf.Vec3d(*translate_delta)
        translate_delta = Gf.Vec3d(translate_delta[0], translate_delta[1], translate_delta[2])
        if model.op_settings_listener.translation_mode == transform_c.TRANSFORM_MODE_LOCAL:
            translate_delta = translate_delta * rotation_mtx

        self._accumulated_translate += translate_delta

        def apply_position(snap_world_pos=None, snap_world_orient=None, keep_spacing: bool = True):
            nonlocal new_manip_xform
            if self.state != sc.GestureState.CHANGED:
                return

            # only set translate if no snap or only snap to position
            item_name = "translate"

            if snap_world_pos and (
                math.isfinite(snap_world_pos[0])
                and math.isfinite(snap_world_pos[1])
                and math.isfinite(snap_world_pos[2])
            ):
                if snap_world_orient is None:
                    new_manip_xform.SetTranslateOnly(Gf.Vec3d(snap_world_pos[0], snap_world_pos[1], snap_world_pos[2]))
                    new_manip_xform = self._begin_scale_mtx * new_manip_xform
                else:
                    new_manip_xform.SetTranslateOnly(Gf.Vec3d(snap_world_pos[0], snap_world_pos[1], snap_world_pos[2]))
                    new_manip_xform.SetRotateOnly(snap_world_orient)

                    # set transform if snap both position and orientation
                    item_name = "no_scale_transform_manipulator"
            else:
                new_manip_xform.SetTranslateOnly(self._begin_xform.ExtractTranslation() + self._accumulated_translate)
                new_manip_xform = self._begin_scale_mtx * new_manip_xform

            model.set_floats(model.get_item("translate_delta"), translate_delta)

            if model.custom_manipulator_enabled:
                self._publish_delta(Operation.TRANSLATE, translate_delta)

            if keep_spacing is False:
                mode_item = model.get_item("manipulator_mode")
                prev_mode = model.get_as_ints(mode_item)
                model.set_ints(mode_item, [int(ManipulationMode.UNIFORM)])

            model.set_floats(model.get_item(item_name), flatten(new_manip_xform))

            if keep_spacing is False:
                model.set_ints(mode_item, prev_mode)

        # only do snap to surface if drag the center point
        if (
            model.snap_settings_listener.snap_enabled
            and model.snap_settings_listener.snap_provider
            and axis == [1, 1, 1]
        ):
            ndc_location = None
            if self._viewport_api:
                # No mouse location is available, have to convert back to NDC space
                ndc_location = self.sender.transform_space(
                    sc.Space.WORLD, sc.Space.NDC, self.gesture_payload.ray_closest_point
                )

            if self._snap_manager.get_snap_pos(
                new_manip_xform,
                ndc_location,
                self.sender.scene_view,
                lambda **kwargs: apply_position(
                    kwargs.get("position", None), kwargs.get("orient", None), kwargs.get("keep_spacing", True)
                ),
            ):
                return

        apply_position()

    def _get_model(self, payload_type) -> ViewportTransformModel:
        if not self.gesture_payload or not self.sender or not isinstance(self.gesture_payload, payload_type):
            return None

        return self.sender.model

    def _can_snap(self, model: ViewportTransformModel):
        axis = self.gesture_payload.axis
        if (
            model.snap_settings_listener.snap_enabled
            and model.snap_settings_listener.snap_provider
            and axis == [1, 1, 1]
        ):
            return True

        return False


class ViewportRotateChangedGesture(RotateChangedGesture, ViewportTransformChangedGestureBase):
    """A class for handling rotation change gestures within a viewport.

    This class is responsible for managing the beginning, ongoing changes, and ending of rotation gestures applied to objects in the viewport. It extends the functionality of RotateChangedGesture and ViewportTransformChangedGestureBase.

    Keyword Args:
        usd_context_name (str): The name of the USD context.
        viewport_api: The API for the viewport.
    """

    def __init__(self, **kwargs):
        """Initialize the ViewportRotateChangedGesture instance."""
        ViewportTransformChangedGestureBase.__init__(self, **kwargs)
        RotateChangedGesture.__init__(self)

    def on_began(self):
        """Handle the beginning of the rotation gesture."""
        ViewportTransformChangedGestureBase.on_began(self, RotateDragGesturePayload)

        model = self.sender.model
        if model:
            model.set_floats(model.get_item("rotate_delta"), [0, 0, 0, 0])

    def on_ended(self):
        """Handle the end of the rotation gesture."""
        ViewportTransformChangedGestureBase.on_ended(self, RotateDragGesturePayload)

    def on_canceled(self):
        """Handle the cancellation of the rotation gesture."""
        ViewportTransformChangedGestureBase.on_canceled(self, RotateDragGesturePayload)

    @carb.profiler.profile
    def on_changed(self):
        """Handle changes during the rotation gesture.

        Args:
            args: Arguments for the rotation gesture.

        Keyword Args:
            payload_type (type): The type of the payload for the gesture.
            axis (list): The axis of rotation.
            angle (float): The angle of rotation.
            angle_delta (float): The change in angle.
            screen_space (bool): Whether the rotation is in screen space.
            free_rotation (bool): Whether the rotation is free-form.
        """
        ViewportTransformChangedGestureBase.on_changed(self, RotateDragGesturePayload)

        if (
            not self.gesture_payload
            or not self.sender
            or not isinstance(self.gesture_payload, RotateDragGesturePayload)
        ):
            return

        model = self.sender.model
        if not model:
            return

        axis = self.gesture_payload.axis
        angle = self.gesture_payload.angle
        angle_delta = self.gesture_payload.angle_delta
        screen_space = self.gesture_payload.screen_space
        free_rotation = self.gesture_payload.free_rotation

        axis = Gf.Vec3d(*axis[:3])
        rotate = Gf.Rotation(axis, angle)
        delta_axis = Gf.Vec4d(*axis, 0.0)

        rot_matrix = Gf.Matrix4d(1)
        rot_matrix.SetRotate(rotate)
        rot_matrix = Gf.Matrix4d(rot_matrix)

        if free_rotation:
            rotate = Gf.Rotation(axis, angle_delta)

            rot_matrix = Gf.Matrix4d(1)
            rot_matrix.SetRotate(rotate)
            rot_matrix = Gf.Matrix4d(rot_matrix)

            xform = Gf.Matrix4d(*model.get_as_floats(model.get_item("no_scale_transform_manipulator")))
            full_xform = self._begin_scale_mtx * xform
            translate = full_xform.ExtractTranslation()
            no_translate_mtx = Gf.Matrix4d(full_xform)
            no_translate_mtx.SetTranslateOnly(Gf.Vec3d(0))
            no_translate_mtx = no_translate_mtx * rot_matrix
            new_transform_matrix = no_translate_mtx.SetTranslateOnly(translate)
            delta_axis = no_translate_mtx * delta_axis
        elif model.op_settings_listener.rotation_mode == transform_c.TRANSFORM_MODE_GLOBAL or screen_space:
            begin_full_xform = self._begin_scale_mtx * self._begin_xform
            translate = begin_full_xform.ExtractTranslation()
            no_translate_mtx = Gf.Matrix4d(begin_full_xform)
            no_translate_mtx.SetTranslateOnly(Gf.Vec3d(0))
            no_translate_mtx = no_translate_mtx * rot_matrix
            new_transform_matrix = no_translate_mtx.SetTranslateOnly(translate)
            delta_axis = no_translate_mtx * delta_axis
        else:
            self._begin_xform = Gf.Matrix4d(*model.get_as_floats(model.get_item("no_scale_transform_manipulator")))
            new_transform_matrix = self._begin_scale_mtx * rot_matrix * self._begin_xform

        delta_axis.Normalize()
        delta_rotate = Gf.Rotation(delta_axis[:3], angle_delta)
        quat = delta_rotate.GetQuat()
        real = quat.GetReal()
        imaginary = quat.GetImaginary()
        rd = [imaginary[0], imaginary[1], imaginary[2], real]
        model.set_floats(model.get_item("rotate_delta"), rd)

        if model.custom_manipulator_enabled:
            self._publish_delta(Operation.ROTATE, rd)

        model.set_floats(model.get_item("rotate"), flatten(new_transform_matrix))


class ViewportScaleChangedGesture(ScaleChangedGesture, ViewportTransformChangedGestureBase):
    """A class for handling viewport scale change gestures.

    This class manages the initiation, updates, and termination of scale change gestures in the viewport. It integrates with the ViewportTransformChangedGestureBase class and the ScaleChangedGesture class to provide comprehensive gesture handling for scaling operations.

    Keyword Args:
        usd_context_name (str): The name of the USD context.
        viewport_api (object): The viewport API instance.
    """

    def __init__(self, **kwargs):
        """Initializes the ViewportScaleChangedGesture."""
        ViewportTransformChangedGestureBase.__init__(self, **kwargs)
        ScaleChangedGesture.__init__(self)

    def on_began(self):
        """Handles the beginning of the scale change gesture."""
        ViewportTransformChangedGestureBase.on_began(self, ScaleDragGesturePayload)

        model = self.sender.model
        if model:
            model.set_floats(model.get_item("scale_delta"), [0, 0, 0])

    def on_ended(self):
        """Handles the ending of the scale change gesture."""
        ViewportTransformChangedGestureBase.on_ended(self, ScaleDragGesturePayload)

    def on_canceled(self):
        """Handles the cancellation of the scale change gesture."""
        ViewportTransformChangedGestureBase.on_canceled(self, ScaleDragGesturePayload)

    @carb.profiler.profile
    def on_changed(self):
        """Handles changes during the scale change gesture.

        Args:
            args (list): List of arguments.

        Keyword Args:
            payload_type (type): The type of the gesture payload.
        """
        ViewportTransformChangedGestureBase.on_changed(self, ScaleDragGesturePayload)

        if not self.gesture_payload or not self.sender or not isinstance(self.gesture_payload, ScaleDragGesturePayload):
            return

        model = self.sender.model
        if not model:
            return

        axis = self.gesture_payload.axis
        scale = self.gesture_payload.scale

        axis = Gf.Vec3d(*axis[:3])

        scale_delta = scale * axis
        scale_vec = Gf.Vec3d()
        for i in range(3):
            scale_vec[i] = scale_delta[i] if scale_delta[i] else 1

        scale_matrix = Gf.Matrix4d(1.0)
        scale_matrix.SetScale(scale_vec)
        scale_matrix *= self._begin_scale_mtx
        new_transform_matrix = scale_matrix * self._begin_xform

        s = Gf.Vec3d(*model.get_as_floats(model.get_item("scale_manipulator")))
        sd = [s_n / s_o for s_n, s_o in zip([scale_matrix[0][0], scale_matrix[1][1], scale_matrix[2][2]], s)]
        model.set_floats(model.get_item("scale_delta"), sd)

        if model.custom_manipulator_enabled:
            self._publish_delta(Operation.SCALE, sd)

        model.set_floats(model.get_item("scale"), flatten(new_transform_matrix))
