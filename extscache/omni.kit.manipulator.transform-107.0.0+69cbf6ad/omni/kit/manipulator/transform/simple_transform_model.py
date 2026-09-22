# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from __future__ import annotations

import math
from typing import List

import carb
from .gestures import (
    RotateChangedGesture,
    RotateDragGesturePayload,
    ScaleChangedGesture,
    ScaleDragGesturePayload,
    TransformDragGesturePayload,
    TranslateChangedGesture,
    TranslateDragGesturePayload,
)
from omni.ui import scene as sc

from .model import AbstractTransformManipulatorModel
from .types import Operation


class SimpleTranslateChangedGesture(TranslateChangedGesture):
    """A gesture that handles the change in translation during a translate operation.

    This class processes the translation changes when a TranslateDragGesturePayload is received. It updates the model's translation data based on the moved delta of the payload.
    """

    def on_changed(self):
        """Handles the update of the translation during a translate gesture.

        This method processes the translation changes when a TranslateDragGesturePayload is received. It updates the
        model's translation data by adding the moved delta of the payload to the current translation."""
        if (
            not self.gesture_payload
            or not self.sender
            or not isinstance(self.gesture_payload, TranslateDragGesturePayload)
        ):
            return

        model = self.sender.model
        item = self.gesture_payload.changing_item
        translated = self.gesture_payload.moved_delta
        translation = [a + b for a, b in zip(translated, model.get_as_floats(item))]

        model.set_floats(item, translation)


class SimpleRotateChangedGesture(RotateChangedGesture):
    """Handles the rotation changes for a transform manipulator gesture.

    This gesture class responds to changes in rotation during a rotation operation. It updates the rotation matrix of the manipulated object based on the axis and angle provided by the rotation gesture payload.
    """

    def on_began(self):
        """Called when the gesture begins.

        Initializes the rotation matrix of the manipulated object using the current rotation values."""
        if (
            not self.gesture_payload
            or not self.sender
            or not isinstance(self.gesture_payload, RotateDragGesturePayload)
        ):
            return

        model = self.sender.model
        item = self.gesture_payload.changing_item
        self._begin_rotation = model.get_as_floats(item).copy()
        self._begin_rotation_matrix = sc.Matrix44.get_rotation_matrix(
            self._begin_rotation[0], self._begin_rotation[1], self._begin_rotation[2], True
        )

    def on_changed(self):
        """Called when the rotation gesture is updated.

        Applies the rotation changes based on the axis and angle provided by the gesture payload. Updates the model's rotation data by applying the rotation to the starting rotation matrix. The rotation is computed by constructing a rotation matrix around the axis for the given angle in radians, then multiplying it by the initial rotation matrix. The result is decomposed back into Euler angles in degrees and set on the model.
        """
        if (
            not self.gesture_payload
            or not self.sender
            or not isinstance(self.gesture_payload, RotateDragGesturePayload)
        ):
            return

        model = self.sender.model
        item = self.gesture_payload.changing_item

        axis = self.gesture_payload.axis
        angle = self.gesture_payload.angle

        # always reset begin_rotation in local rotation mode
        if not model.global_mode:
            self._begin_rotation = model.get_as_floats(item).copy()
            self._begin_rotation_matrix = sc.Matrix44.get_rotation_matrix(
                self._begin_rotation[0], self._begin_rotation[1], self._begin_rotation[2], True
            )

        # convert to radian
        angle = angle / 180.0 * math.pi

        # calculate rotation matrix around axis for angle in radian
        matrix = [
            math.cos(angle) + axis[0] ** 2 * (1 - math.cos(angle)),
            axis[0] * axis[1] * (1 - math.cos(angle)) + axis[2] * math.sin(angle),
            axis[0] * axis[2] * (1 - math.cos(angle)) - axis[1] * math.sin(angle),
            0,
        ]
        matrix += [
            axis[0] * axis[1] * (1 - math.cos(angle)) - axis[2] * math.sin(angle),
            math.cos(angle) + axis[1] ** 2 * (1 - math.cos(angle)),
            axis[1] * axis[2] * (1 - math.cos(angle)) + axis[0] * math.sin(angle),
            0,
        ]
        matrix += [
            axis[0] * axis[2] * (1 - math.cos(angle)) + axis[1] * math.sin(angle),
            axis[1] * axis[2] * (1 - math.cos(angle)) - axis[0] * math.sin(angle),
            math.cos(angle) + axis[2] ** 2 * (1 - math.cos(angle)),
            0,
        ]

        matrix += [0, 0, 0, 1]
        matrix = sc.Matrix44(*matrix)  # each 4 elements in list is a COLUMN in a row-vector matrix!

        rotate = self._begin_rotation_matrix * matrix

        # decompose back to x y z euler angle
        sy = math.sqrt(rotate[0] ** 2 + rotate[1] ** 2)
        is_singular = sy < 10**-6
        if not is_singular:
            z = math.atan2(rotate[1], rotate[0])
            y = math.atan2(-rotate[2], sy)
            x = math.atan2(rotate[6], rotate[10])
        else:
            z = math.atan2(-rotate[9], rotate[5])
            y = math.atan2(-rotate[2], sy)
            x = 0

        x = x / math.pi * 180.0
        y = y / math.pi * 180.0
        z = z / math.pi * 180.0

        model.set_floats(item, [x, y, z])


class SimpleScaleChangedGesture(ScaleChangedGesture):
    """A gesture class that responds to scale changes during a transform manipulator operation.

    This class processes scale gestures and updates the model's scale data accordingly. It listens for scale gestures and applies the scale factor to the current scale of the object being manipulated.
    """

    def on_began(self):
        """Called when the scale gesture begins.

        Initializes the _begin_scale attribute with the current scale values of the item being manipulated."""
        if not self.gesture_payload or not self.sender or not isinstance(self.gesture_payload, ScaleDragGesturePayload):
            return

        model = self.sender.model
        item = self.gesture_payload.changing_item
        self._begin_scale = model.get_as_floats(item).copy()

    def on_changed(self):
        """Called when the scale gesture is updated.

        Applies a scale delta to the initial scale values and updates the model with the new scale. It multiplies the initial scale by the scale factor provided in the gesture payload for each axis.

        Args:
            gesture_payload (ScaleDragGesturePayload): The payload containing the scale factor and axis information.
            sender (AbstractTransformManipulatorModel): The model associated with the gesture."""
        if not self.gesture_payload or not self.sender or not isinstance(self.gesture_payload, ScaleDragGesturePayload):
            return

        model = self.sender.model
        item = self.gesture_payload.changing_item

        axis = self.gesture_payload.axis
        scale = self.gesture_payload.scale

        scale_delta = [scale * v for v in axis]
        scale_vec = [0, 0, 0]
        for i in range(3):
            scale_vec[i] = self._begin_scale[i] * scale_delta[i] if scale_delta[i] else self._scale[i]

        model.set_floats(item, [scale_vec[0], scale_vec[1], scale_vec[2]])


class SimpleTransformModel(AbstractTransformManipulatorModel):
    """A model for basic S/R/T (Scale/Rotate/Translate) transform manipulations in a 3D scene. It allows subscribing to callbacks for updates on manipulated data. Rotation operations are applied in XYZ order and values are in degrees.
    """

    def __init__(self):
        super().__init__()
        self._translation = [0, 0, 0]
        self._rotation = [0, 0, 0]
        self._scale = [1, 1, 1]
        self._transform = sc.Matrix44(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)
        self._op = Operation.TRANSLATE
        self._global_mode = True
        self._dirty = True

    @property
    def global_mode(self) -> bool:
        """
        Get whether it is global mode.

        Returns:
            bool: whether it is global mode.
        """
        return self._global_mode

    @global_mode.setter
    def global_mode(self, value: bool):
        """
        Set whether it is global mode.

        Args:
            value (bool): whether it is global mode.
        """
        if self._global_mode != value:
            self._global_mode = value
            self._dirty = True  # global vs local mode returns different Transform matrix
            self._item_changed(self._transform_item)

    def set_floats(self, item: AbstractTransformManipulatorModel.OperationItem, value: List[float]):
        """Updates the transformation values for a given transformation component (translation, rotation, or scale).

        Sets the corresponding transformation component values to the provided list of floats and marks the transformation as dirty.

        Args:
            item (AbstractTransformManipulatorModel.OperationItem): The component to update (translate_item, rotate_item, or scale_item).
            value (List[float]): The new values for the component."""
        if item == self._translate_item:
            self._translation[0] = value[0]
            self._translation[1] = value[1]
            self._translation[2] = value[2]
            self._dirty = True
            self._item_changed(self._translate_item)
        elif item == self._rotate_item:
            self._rotation[0] = value[0]
            self._rotation[1] = value[1]
            self._rotation[2] = value[2]
            self._dirty = True
            self._item_changed(self._rotate_item)
        elif item == self._scale_item:
            self._scale[0] = value[0]
            self._scale[1] = value[1]
            self._scale[2] = value[2]
            self._dirty = True
            self._item_changed(self._scale_item)
        else:
            carb.log_warn(f"Unsupported item {item}")

    def get_as_floats(self, item: AbstractTransformManipulatorModel.OperationItem) -> List[float]:
        """Retrieves the transformation values as a list of floats for a given component.

        If the transformation matrix is marked as dirty and the requested item is the transform_item, it recalculates the transformation matrix before returning it.

        Args:
            item (AbstractTransformManipulatorModel.OperationItem): The component to retrieve (translate_item, rotate_item, scale_item, transform_item).

        Returns:
            List[float]: The transformation values for the requested component or the transformation matrix if transform_item is requested.
        """
        if item == self._translate_item:
            return self._translation
        elif item == self._rotate_item:
            return self._rotation
        elif item == self._scale_item:
            return self._scale
        elif item is None or item == self._transform_item:
            if self._dirty:
                # Scale is not put into the Transform matrix because we don't want the TransformManipulator itself to scale
                # For a "global" style rotation gizmo (where the gizmo doesn't rotate), we don't want to put the rotation into Transform either.
                if self._global_mode:
                    self._transform = sc.Matrix44.get_translation_matrix(
                        self._translation[0], self._translation[1], self._translation[2]
                    )
                else:
                    self._transform = sc.Matrix44.get_translation_matrix(
                        self._translation[0], self._translation[1], self._translation[2]
                    ) * sc.Matrix44.get_rotation_matrix(self._rotation[0], self._rotation[1], self._rotation[2], True)
                self._dirty = False

            return self._transform
        else:
            carb.log_warn(f"Unsupported item {item}")
            return None

    def get_operation(self) -> Operation:
        """Retrieves the current operation mode of the transform manipulator.

        Returns:
            Operation: The current operation mode (Translate, Rotate, Scale)."""
        return self._op

    def set_operation(self, op: Operation):
        """Sets the current operation mode of the transform manipulator.

        If the operation mode is different from the current mode, it sets the new mode and notifies any subscribers that the transform item has changed.

        Args:
            op (Operation): The new operation mode to set."""
        if self._op != op:
            self._op = op
            self._item_changed(self._transform_item)
