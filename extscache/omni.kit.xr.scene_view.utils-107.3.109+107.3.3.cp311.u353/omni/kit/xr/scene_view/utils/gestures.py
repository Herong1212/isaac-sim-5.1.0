# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = [
    "TranslationGestureHandler",
    "RotationGestureHandler",
    "ScaleGestureHandler",
    "Resize2DGestureHandler",
]

import math
from typing import Literal, TypeAlias, cast
from weakref import ProxyType, proxy

import carb
import numpy as np
from omni.ui import scene as sc

from .manipulator_components.area_2d_component import Area2DComponent
from .transformable_manipulator import TransformableManipulatorModel

# Typing numpy types gets complex, so here's a local alias to use instead
NPVec3: TypeAlias = np.ndarray[tuple[Literal[3]], np.dtype[np.float_]]
NPVec4: TypeAlias = np.ndarray[tuple[Literal[4]], np.dtype[np.float_]]

NP_ZERO_VEC: NPVec4 = np.array([0, 0, 0, 1])
NP_X_VEC: NPVec4 = np.array([1, 0, 0, 1])
NP_Y_VEC: NPVec4 = np.array([0, 1, 0, 1])
NP_Z_VEC: NPVec4 = np.array([0, 0, 1, 1])


class _ParallelRayResult:
    """
    This error is returned internally-only when the dot product of a raycast is zero.
    It's used to avoid dividing by zero.
    """

    ...


class TranslationGestureHandler(sc.DragGesture):
    """
    A gesture handler for dragging a Scene item which moves it around in 3D inside the Scene
    """

    def __init__(self, model: TransformableManipulatorModel, **kwargs):
        super().__init__(**kwargs)

        # ProxyType works like its base, so linting as base is fine
        self.__model: TransformableManipulatorModel = cast(TransformableManipulatorModel, proxy(model))

        self._initial_translation: NPVec3 | None = None
        self._initial_distance: float | None = None
        self._initial_offset: NPVec3 | None = None

    def on_began(self):
        self._initial_translation = np.array(self.__model.translation.floats)
        payload: sc.AbstractGesture.GesturePayload = self.sender.gesture_payload  # type: ignore
        self._initial_distance = payload.ray_distance

        mo = self.raw_input.mouse_origin
        md = self.raw_input.mouse_direction
        origin = np.array([mo.x, mo.y, mo.z])
        direction = np.array([md.x, md.y, md.z])
        direction = direction / np.linalg.norm(direction)
        point = origin + direction * self._initial_distance

        self._initial_offset = self._initial_translation - point

    def on_changed(self):
        assert self._initial_distance is not None
        assert self._initial_offset is not None

        mo = self.raw_input.mouse_origin
        md = self.raw_input.mouse_direction
        new_origin = np.array([mo.x, mo.y, mo.z])
        new_direction = np.array([md.x, md.y, md.z])
        new_direction = new_direction / np.linalg.norm(new_direction)

        translation = new_origin + new_direction * self._initial_distance + self._initial_offset

        self.__model.set_floats(self.__model.translation, list(translation[:]))

    def on_ended(self):
        pass


class RotationGestureHandler(sc.DragGesture):
    """
    A gesture handler for dragging a Scene item which moves it around in 3D inside the Scene
    """

    def __init__(self, model: TransformableManipulatorModel, **kwargs):
        super().__init__(**kwargs)

        # ProxyType works like its base, so linting as base is fine
        self.__model: TransformableManipulatorModel = cast(TransformableManipulatorModel, proxy(model))

        self.__initial_rotation: NPVec3 | None = None
        self.__initial_direction: NPVec3 | None = None
        self.__initial_origin: NPVec3 | None = None

    def on_began(self):
        self.__initial_rotation = np.array(self.__model.rotation.floats)
        md = self.raw_input.mouse_direction
        mo = self.raw_input.mouse_origin

        self.__initial_origin = np.array([mo.x, 0.0, mo.z])

        # TODO: Use "scene up" instead of assuming Y
        direction = np.array([md.x, 0.0, md.z])
        direction = direction / np.linalg.norm(direction)
        self.__initial_direction = direction

    def on_changed(self):
        assert self.__initial_origin is not None
        assert self.__initial_direction is not None
        assert self.__initial_rotation is not None

        md = self.raw_input.mouse_direction
        mo = self.raw_input.mouse_origin
        target_direction = np.array([md.x, 0.0, md.z])
        target_origin = np.array([mo.x, 0.0, mo.z])

        # Use a made-up "target" point to allow rotation to account for movement AND angle changes
        new_target = target_origin + target_direction / np.linalg.norm(target_direction)
        new_direction = new_target - self.__initial_origin
        new_direction = new_direction / np.linalg.norm(new_direction)

        cp = np.cross(new_direction, self.__initial_direction)
        cp_multiplier = cp[1]

        orig_diff = math.radians(np.linalg.norm(target_origin - self.__initial_origin))

        # Copy initial rotation and add the new angle to it
        dampening = 0.5
        rotation = list(self.__initial_rotation[:3])
        rotation[1] += orig_diff * cp_multiplier * dampening

        self.__model.set_floats(self.__model.rotation, rotation[:])


class ScaleGestureHandler(sc.DragGesture):
    """
    A gesture handler for dragging a Scene item which moves it around in 3D inside the Scene
    """

    def __init__(self, model: TransformableManipulatorModel, **kwargs):
        super().__init__(**kwargs)

        # ProxyType works like its base, so linting as base is fine
        self.__model: TransformableManipulatorModel = cast(TransformableManipulatorModel, proxy(model))

        self.__initial_direction: NPVec3 | None = None
        self.__last_direction: NPVec3 | None = None

    def on_began(self):
        md = self.raw_input.mouse_direction

        self.__initial_direction = np.array([md.x, md.y, md.z])
        self.__last_direction = self.__initial_direction

        assert self.__last_direction is not None
        self.__last_direction = self.__last_direction / np.linalg.norm(self.__last_direction)

    def on_changed(self):
        assert self.__initial_direction is not None
        assert self.__last_direction is not None

        md = self.raw_input.mouse_direction
        current_direction = np.array([md.x, md.y, md.z])
        current_direction = current_direction / np.linalg.norm(current_direction)
        delta_direction = current_direction - self.__last_direction

        # determines counter/clockwise
        cp = np.cross(current_direction, delta_direction)
        dp = np.dot(-self.__initial_direction, cp)
        norm = np.linalg.norm(current_direction - self.__last_direction)

        # scale up if clockwise, down if counter-clockwise
        up_down = 1.0 if dp < 0 else -1.0

        # NOTE: Numpy's `floating[float_]` type ends up being compatible with float, just type checkers aren't really
        # big fans of seeing it as such.
        scale = cast(float, self.__model.scale.floats[0] + norm * up_down)

        # Keep the scale sane, as this algorithm currently goes a bit crazy sometimes
        if scale < 0.5:
            scale = 0.5
        elif scale > 3.0:
            scale = 3.0

        self.__last_direction = current_direction
        self.__model.set_floats(self.__model.scale, [scale, scale, scale])

    def on_ended(self):
        self.__initial_direction = None
        self.__last_direction = None


class Resize2DGestureHandler(sc.DragGesture):
    def __init__(
        self,
        model: TransformableManipulatorModel,
        target: "ProxyType[Area2DComponent]",
        **kwargs,
    ):
        super().__init__(**kwargs)

        # ProxyType works like its base, so linting as base is fine
        self.__model: TransformableManipulatorModel = cast(TransformableManipulatorModel, proxy(model))
        self.__target: ProxyType[Area2DComponent] = target

        self._surface_normal: NPVec3 | None = None
        self._origin_point: NPVec3 | None = None
        self._origin_x_positive: NPVec3 | None = None
        self._origin_y_positive: NPVec3 | None = None
        self._original_width: float | None = None
        self._original_height: float | None = None

        self._hit_offset_x: float = 0
        self._hit_offset_y: float = 0

    def on_began(self):
        original_matrix = np.reshape(self.__model.matrix_item.floats, (4, 4))

        self._origin_point = (NP_ZERO_VEC @ original_matrix)[:3]
        self._origin_x_positive = (NP_X_VEC @ original_matrix)[:3] - self._origin_point
        self._origin_y_positive = (NP_Y_VEC @ original_matrix)[:3] - self._origin_point
        self._surface_normal = (NP_Z_VEC @ original_matrix)[:3] - self._origin_point

        self._original_width = self.__target.width
        self._original_height = self.__target.height

        uv_offset_result = self._calc_uv_offset()
        match uv_offset_result:
            case (offset_x, offset_y):
                self._hit_offset_x = offset_x
                self._hit_offset_y = offset_y
            case _ParallelRayResult():
                carb.log_error("Initial gesture direction was perpendicular")

    def _calc_uv_offset(self) -> tuple[float, float] | _ParallelRayResult:
        assert self._surface_normal is not None
        assert self._origin_x_positive is not None
        assert self._origin_y_positive is not None
        assert self._origin_point is not None

        mo = self.raw_input.mouse_origin
        input_origin: NPVec3 = np.array([mo.x, mo.y, mo.z])

        md = self.raw_input.mouse_direction
        input_direction: NPVec3 = np.array([md.x, md.y, md.z])
        input_direction /= np.linalg.norm(input_direction)

        # Check that the ray isn't parallel to the plane
        if np.dot(input_direction, self._surface_normal) == 0:
            return _ParallelRayResult()

        # Calculate the distance along the pointing ray to where it intersects the manipulators forward plane
        dist: float = np.dot(self._origin_point - input_origin, self._surface_normal) / np.dot(
            input_direction, self._surface_normal
        )

        # This is the point where the input ray intersects the forward plane
        point: NPVec3 = input_origin + dist * input_direction

        # Calculate the relative X/Y distance in the forward plane's coordinate space
        v: NPVec3 = point - self._origin_point
        projected: NPVec3 = v - np.dot(v, self._surface_normal) * self._surface_normal / np.dot(
            self._surface_normal, self._surface_normal
        )

        x_delta: float = np.dot(projected, self._origin_x_positive)
        y_delta: float = np.dot(projected, self._origin_y_positive)

        return x_delta, y_delta

    def on_changed(self) -> None:
        offset: tuple[float, float]
        uv_offset_result = self._calc_uv_offset()
        match uv_offset_result:
            case tuple():
                offset = uv_offset_result
            case _ParallelRayResult():
                # In change updates, it should be safe to just ignore parallel input rays
                return

        assert self._original_width is not None
        assert self._original_height is not None

        x_delta, y_delta = offset
        x_delta -= self._hit_offset_x
        y_delta -= self._hit_offset_y

        size_offset_x = x_delta * 2
        size_offset_y = y_delta * 2

        # NOTE: linters apparently have problems with proxy types and property setters. The following "ignore" comments
        # prevent those problems from erroneously triggering lint warnings.
        if self._original_width + size_offset_x > 0:
            self.__target.width = self._original_width + size_offset_x  # type: ignore
        if self._original_height + size_offset_y > 0:
            self.__target.height = self._original_height + size_offset_y  # type: ignore
