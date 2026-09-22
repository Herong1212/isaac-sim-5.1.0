# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Sequence, Tuple

if TYPE_CHECKING:
    from .manipulator import TransformManipulator

import copy
import math
from functools import lru_cache

import carb.input
import carb.settings
import numpy as np
from omni.ui import color as cl
from omni.ui import scene as sc

from .settings_constants import c as CONSTANTS


@lru_cache()
def __get_input() -> carb.input.IInput:
    return carb.input.acquire_input_interface()


def _is_alt_down() -> bool:
    input = __get_input()
    return (
        input.get_keyboard_value(None, carb.input.KeyboardInput.LEFT_ALT)
        + input.get_keyboard_value(None, carb.input.KeyboardInput.RIGHT_ALT)
        > 0
    )


class PreventOthers(sc.GestureManager):
    """A gesture manager that makes TransformGesture the priority gesture over others.

    This manager ensures that TransformGesture takes precedence, preventing other gestures
    from being recognized when TransformGesture is active and certain conditions are met."""

    def can_be_prevented(self, gesture):
        """Determines if a gesture can be prevented.

        Args:
            gesture (sc.AbstractGesture): The gesture to be evaluated.

        Returns:
            bool: True if the gesture can be prevented, otherwise False."""
        # Never prevent in the middle or at the end of drag
        return (
            gesture.state != sc.GestureState.CHANGED
            and gesture.state != sc.GestureState.ENDED
            and gesture.state != sc.GestureState.CANCELED
        )

    def should_prevent(self, gesture, preventer):
        """Decides if a gesture should be prevented based on its state and type.

        Args:
            gesture (sc.AbstractGesture): The gesture that may be prevented.
            preventer (sc.AbstractGesture): The gesture attempting to prevent the other gesture.

        Returns:
            bool: True if the gesture should be prevented, otherwise False."""
        if (
            (isinstance(preventer, TransformGesture) or isinstance(preventer, DummyClickGesture))
            and (preventer.state == sc.GestureState.BEGAN or preventer.state == sc.GestureState.CHANGED)
            and not _is_alt_down()  # don't prevent other gesture if alt (camera manip) is down
        ):
            if isinstance(gesture, TransformGesture):
                if gesture.order > preventer.order:
                    return True

                elif gesture.order == preventer.order:
                    # Transform vs Transform depth test
                    return gesture.gesture_payload.ray_distance > preventer.gesture_payload.ray_distance
            else:
                # Transform is the priority when it's against any other gesture
                return True
        return super().should_prevent(gesture, preventer)


class HoverDepthTest(sc.GestureManager):
    """A manager that performs a depth test for hover gestures.

    The hover gesture with the smaller order is given priority. If they have same order, gesture with smaller ray distance (closer to the camera) is given priority.
    """

    def can_be_prevented(self, gesture):
        """Determines if a hover gesture can be prevented based on its type.

        Args:
            gesture (sc.AbstractGesture): The gesture to be evaluated.

        Returns:
            bool: True if the gesture is an instance of HighlightGesture, otherwise False."""
        return isinstance(gesture, HighlightGesture)

    def should_prevent(self, gesture, preventer):
        """Decides if a hover gesture should be prevented based on its state, type, and depth.

        Args:
            gesture (sc.AbstractGesture): The gesture that may be prevented.
            preventer (sc.AbstractGesture): The gesture attempting to prevent the other gesture.

        Returns:
            bool: True if the gesture should be prevented, otherwise False."""
        if (
            isinstance(gesture, HighlightGesture) and not _is_alt_down()
        ):  # don't prevent other gesture if alt (camera manip) is down
            if isinstance(preventer, HighlightGesture):
                if preventer.state == sc.GestureState.BEGAN or preventer.state == sc.GestureState.CHANGED:
                    if gesture.order > preventer.order:
                        return True

                    elif gesture.order == preventer.order:
                        # Hover vs Hover depth test
                        return gesture.gesture_payload.ray_distance > preventer.gesture_payload.ray_distance
        return False


class TransformDragGesturePayload(sc.AbstractGesture.GesturePayload):
    """A payload class used for drag gestures related to transformation operations.

    This class contains information about the items being manipulated during transform drag gestures.

    Args:
        base: sc.AbstractGesture.GesturePayload
            The base gesture payload.
        changing_item: sc.AbstractManipulatorItem
            The manipulator item that is being changed during the drag operation.
    Attributes:
        changing_item: sc.AbstractManipulatorItem
            The manipulator item that is being changed during the drag operation.
    """

    def __init__(self, base: sc.AbstractGesture.GesturePayload, changing_item: sc.AbstractManipulatorItem):
        """Initializes a new instance of the TransformDragGesturePayload."""
        super().__init__(base.item_closest_point, base.ray_closest_point, base.ray_distance)
        self.changing_item = changing_item


@dataclass(init=False)
class TranslateDragGesturePayload(TransformDragGesturePayload):
    """A payload for drag gestures used during translation operations.

    This class holds details about the translation operation such as the axis of translation, the delta movement since the last change, and the total movement since the drag started.
    """

    axis: Sequence[float]
    """The axis along which the translation is occurring."""
    moved_delta: Sequence[float]
    """The change in position since the last update."""
    moved: Sequence[float]
    """The total change in position since the drag began."""


@dataclass(init=False)
class RotateDragGesturePayload(TransformDragGesturePayload):
    """A payload class used for rotation drag gestures within the Transform manipulator.

    This class encapsulates the properties of a rotation operation as it is being performed, such as the rotation axis, the incremental angle change, and the total angle rotated.
    """

    axis: Sequence[float]
    """The axis around which the object is being rotated."""
    angle_delta: float
    """The change in rotation angle since the last update."""
    angle: float
    """The total rotation angle since the beginning of the drag gesture."""
    screen_space: bool
    """Indicates if the rotation is happening in screen space."""
    free_rotation: bool
    """Indicates if the rotation is free (not constrained to an axis)."""


@dataclass(init=False)
class ScaleDragGesturePayload(TransformDragGesturePayload):
    """A payload class used for drag gestures related to scaling operations.

    This class contains information about the scaling factors and the axis along which objects are being scaled during drag gestures.
    """

    axis: Sequence[float]
    """The axis along which the scaling is performed."""
    scale: Sequence[float]
    """The scaling values on each axis."""


class TransformChangedGesture(sc.ManipulatorGesture):
    """A gesture representing a change in a transformation, such as translation, rotation, or scaling.

    This gesture is part of the mechanism for handling transformation manipulations in a omni.ui.scene.SceneView. It is triggered when a transformation action begins, changes, ends, or is canceled. It is responsible for updating the transformation state and potentially preventing other omni.ui.scene.SceneView interactions while a transformation is active.

    Args:
        **kwargs: Variable length keyword arguments.
    """

    def __init__(self, **kwargs):
        """Initializes the TransformChangedGesture."""
        super().__init__(**kwargs)

    def process(self):
        """Processes the gesture and determines the appropriate action based on its state."""
        if not self.gesture_payload:
            return

        # Redirection to methods
        if self.state == sc.GestureState.BEGAN:
            self.on_began()
        elif self.state == sc.GestureState.CHANGED:
            self.on_changed()
        elif self.state == sc.GestureState.ENDED:
            self.on_ended()
        elif self.state == sc.GestureState.CANCELED:
            self.on_canceled()

    # Public API:
    def on_began(self):
        """Handler for the beginning state of the gesture."""
        ...

    def on_changed(self):
        """Handler for the changed state of the gesture."""
        ...

    def on_ended(self):
        """Handler for the ended state of the gesture."""
        ...

    def on_canceled(self):
        """Handler for the canceled state of the gesture."""
        ...


class TranslateChangedGesture(TransformChangedGesture):
    """A gesture representing a change in a translation during an interaction with a manipulator.

    This gesture is used internally to handle manipulator interactions in a omni.ui.scene.SceneView for translation operations. It is part of the gesture system that responds to the beginning, modification, ending, or canceling of a translation action and is responsible for updating the state of the transformation and optionally blocking other omni.ui.scene.SceneView interactions while active.
    """

    ...


class RotateChangedGesture(TransformChangedGesture):
    """A gesture representing a change in rotation during an interaction with a manipulator.

    This gesture is used internally to handle manipulator interactions in a omni.ui.scene.SceneView for rotation operations. It is part of the gesture system that responds to the beginning, modification, ending, or canceling of a rotation action and is responsible for updating the state of the transformation and optionally blocking other omni.ui.scene.SceneView interactions while active.
    """

    ...


class ScaleChangedGesture(TransformChangedGesture):
    """A gesture representing a change in scaling during an interaction with a manipulator.

    This gesture is used internally to handle manipulator interactions in a omni.ui.scene.SceneView for scaling operations. It is part of the gesture system that responds to the beginning, modification, ending, or canceling of a scaling action and is responsible for updating the state of the transformation and optionally blocking other omni.ui.scene.SceneView interactions while active.
    """

    ...


####################
# Internal gestures
####################


class HighlightControl:
    """A control for highlighting manipulator widgets during interaction.

    When an interaction with a manipulator widget begins, the HighlightControl is responsible for changing the color of the widget to indicate its highlighted state. Once the interaction ends, the original color is restored. This class supports highlighting the same widget from multiple triggers simultaneously.

    Args:
        items: List[sc.AbstractManipulatorItem], optional
            A list of manipulator items to track highlighting for.
        color: cl.Color, optional
            The color used for highlighting."""

    # Use static member to track across ALL HighlightControl instances,
    # because more than one HighlightControl can highlight the same widget (e.g. translate center and plane quads)
    __status_tracker = defaultdict(int)
    __original_colors = {}

    def __init__(self, items=None, color=None):
        """Initializes a HighlightControl instance. """
        self._items = items
        # From rendering\source\plugins\carb.imguizmo\ImGuizmo.cpp
        # static const ImU32 selectionColor = 0x8A1CE6E6;
        self._selection_color = color if color else cl("#e6e61c8a")

    def highlight(self, sender):
        """Highlights the given sender or all items managed by this control.

        Args:
            sender (sc.AbstractManipulatorItem): The item to highlight."""
        if self._items is None:
            HighlightControl.__status_tracker[sender] += 1
            if HighlightControl.__status_tracker[sender] == 1:
                self._highlight(sender)
        else:
            for item in self._items:
                HighlightControl.__status_tracker[item] += 1
                if HighlightControl.__status_tracker[item] == 1:
                    self._highlight(item)

    def dehighlight(self, sender):
        """Removes the highlight from the given sender or all items managed by this control.

        Args:
            sender (sc.AbstractManipulatorItem): The item to dehighlight."""
        if self._items is None:
            HighlightControl.__status_tracker[sender] -= 1
            if HighlightControl.__status_tracker[sender] <= 0:
                self._dehighlight(sender)
                HighlightControl.__status_tracker.pop(sender)
        else:
            for item in self._items:
                HighlightControl.__status_tracker[item] -= 1
                if HighlightControl.__status_tracker[item] <= 0:
                    self._dehighlight(item)
                    HighlightControl.__status_tracker.pop(item)

    def _highlight(self, item):
        """Applies the highlight color to the specified item.

        Args:
            item (sc.AbstractManipulatorItem): The item to apply the highlight color to."""
        if hasattr(item, "color"):
            HighlightControl.__original_colors[item] = item.color
            item.color = self._selection_color

        if hasattr(item, "colors"):
            HighlightControl.__original_colors[item] = item.colors.copy()
            colors = item.colors.copy()
            for i in range(len(colors)):
                colors[i] = self._selection_color
            item.colors = colors

    def _dehighlight(self, item):
        """Restores the original color of the specified item.

        Args:
            item (sc.AbstractManipulatorItem): The item to restore the original color to."""
        if hasattr(item, "color"):
            item.color = HighlightControl.__original_colors[item]

        if hasattr(item, "colors"):
            item.colors = HighlightControl.__original_colors[item]


class HighlightGesture(sc.HoverGesture):
    """A gesture for highlighting UI elements during interaction.

    This gesture is responsible for changing the appearance of UI elements, such as manipulator widgets,
    to visually signify that they are being interacted with. It uses a HighlightControl instance to manage
    the highlight state and ensures the correct visual feedback is provided to the user based on the gesture's life cycle.

    Args:
        HighlightControl: HighlightControl
            The control responsible for managing highlights.
        order: int
            The priority order of the gesture, used for conflict resolution. Defaults to 0.
    """

    def __init__(self, highlight_ctrl: HighlightControl, order: int = 0):
        """Initializes the HighlightGesture with a given HighlightControl and optional order. """
        super().__init__(manager=HoverDepthTest())
        self._highlight_ctrl = highlight_ctrl
        self._begun = False
        self._order = order

    @property
    def order(self) -> int:
        """The order property of the HighlightGesture.

        Returns:
            int: The priority order of the gesture."""
        return self._order

    def process(self):
        """Processes the gesture, updating its state and handling highlighting based on interaction."""
        if isinstance(self.sender, sc.Arc) and self.sender.gesture_payload.culled:
            # Turn down the gesture if it on the wrong side of the arc
            if self.state == sc.GestureState.BEGAN:
                self.state = sc.GestureState.POSSIBLE
            if self.state == sc.GestureState.CHANGED:
                self.state = sc.GestureState.ENDED

        if _is_alt_down():
            # Turn down the gesture if manipulating camera
            # If gesture already began, don't turn it down as ALT won't trigger camera manipulation at this point
            if self.state == sc.GestureState.BEGAN:
                self.state = sc.GestureState.POSSIBLE

        if self.state == sc.GestureState.BEGAN:
            self._on_began()
        elif self.state == sc.GestureState.ENDED:
            self._on_ended()
        elif self.state == sc.GestureState.CANCELED:
            self._on_canceled()
        elif self.state == sc.GestureState.CHANGED:
            self._on_changed()
        elif self.state == sc.GestureState.PREVENTED:
            self._on_prevented()
        super().process()

    def _on_began(self):
        """Handles the initiation of the gesture, causing the associated manipulator widget to be highlighted."""
        self._begun = True
        self._highlight_ctrl.highlight(self.sender)

    def _on_ended(self):
        """Handles the end of the gesture, removing the highlight from the associated manipulator widget."""
        if self._begun:
            self._begun = False
            self._highlight_ctrl.dehighlight(self.sender)

    def _on_changed(self):
        """Handles changes to the gesture state."""
        ...

    def _on_canceled(self):
        """Handles the cancellation of the gesture, removing the highlight if it had been applied."""
        self._on_ended()

    def _on_prevented(self):
        """Handles the gesture being prevented, removing the highlight if it had been applied."""
        self._on_ended()


class TransformGesture(sc.DragGesture):
    """A gesture class used to manage transformation operations within a 3D scene. It is the base class to inherit from if you want to register custom gestures to manipulator.

    This class is responsible for processing gesture inputs related to translating, rotating, and scaling objects in the scene. It works in conjunction with a manipulator and a highlight control to provide visual feedback and ensure correct interaction behavior.
    Args:
        manipulator (TransformManipulator): The manipulator associated with the gesture.
        highlight_ctrl (HighlightControl): The highlight control used to manage highlighting of manipulator widgets.
        order (int): The priority order of the gesture.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
    """

    def __init__(
        self, manipulator: TransformManipulator, highlight_ctrl: HighlightControl, order: int = 0, *args, **kwargs
    ):
        """Initializes the TransformGesture with a given manipulator, highlight control, order, and additional arguments."""
        super().__init__(*args, **kwargs)
        self._manipulator = manipulator
        self._highlight_ctrl = highlight_ctrl
        self._order = order
        self._toolbar_was_visible = None
        self._began = False

    @property
    def order(self) -> int:
        return self._order

    def process(self):
        """Processes the gesture, handling its state changes and invoking the appropriate methods based on the current state."""
        if _is_alt_down():
            # Turn down the gesture if manipulating camera
            # If gesture already began, don't turn it down as ALT won't trigger camera manipulation at this point
            if self.state == sc.GestureState.BEGAN:
                self.state = sc.GestureState.POSSIBLE

        if self.state == sc.GestureState.BEGAN:
            self._on_began()
        elif self.state == sc.GestureState.ENDED:
            self._on_ended()
        elif self.state == sc.GestureState.CANCELED:
            self._on_canceled()
        elif self.state == sc.GestureState.CHANGED:
            self._on_changed()
        elif self.state == sc.GestureState.PREVENTED:
            self._on_prevented()
        super().process()

    def _on_began(self):
        """Handler called when the gesture begins. Sets up necessary state for the transformation."""
        self._began = True

        self._toolbar_was_visible = self._manipulator.toolbar_visible
        self._manipulator.toolbar_visible = False

    def _on_ended(self):
        """Handler called when the gesture ends. Performs cleanup and state restoration."""
        if self._began and self._toolbar_was_visible is not None:
            self._manipulator.toolbar_visible = self._toolbar_was_visible
            self._toolbar_was_visible = None
        self._began = False

    def _on_changed(self):
        """Handler called when the gesture state changes. Typically used to perform the transformation."""
        ...

    def _on_canceled(self):
        """Handler called when the gesture is canceled. Rolls back any changes if necessary."""
        if self._began:
            self._on_ended()

            if self._toolbar_was_visible is not None:
                self._manipulator.toolbar_visible = self._toolbar_was_visible
                self._toolbar_was_visible = None

    def _on_prevented(self):
        """Handler called when the gesture is prevented from continuing, often due to other gestures taking precedence."""
        if self._began:
            self._on_ended()


class TranslateGesture(TransformGesture):
    """A gesture class used for translating objects in a 3D scene.

    This class processes input related to moving objects along specific axes in the scene. It integrates with a manipulator and a highlight control to provide interactive feedback and manage the transformation.

    Args:
        manipulator (TransformManipulator): The manipulator associated with the gesture.
        axis (Sequence[int]): The axis along which translation occurs.
        highlight_ctrl (HighlightControl): The highlight control used to manage highlighting of manipulator widgets.
        order (int): The priority order of the gesture."""

    def __init__(
        self, manipulator: TransformManipulator, axis: Sequence[int], highlight_ctrl: HighlightControl, order: int = 0
    ):
        """Initializes the TranslateGesture with a given manipulator, translation axis, highlight control, and order."""
        super().__init__(manipulator=manipulator, highlight_ctrl=highlight_ctrl, order=order, manager=PreventOthers())
        self._axis = axis

    def _on_began(self):
        """Handler called when the translation gesture begins. Sets up the necessary state for the translation operation."""
        super()._on_began()

        self._moved = [0, 0, 0]  # moved since begin edit, non-snapped
        self._moved_snap = [0, 0, 0]
        self._changing_item = self._manipulator.model.get_item("translate")

        payload = TranslateDragGesturePayload(self.gesture_payload, self._changing_item)
        payload.axis = self._axis
        self._manipulator._process_gesture(TranslateChangedGesture, self.state, payload)
        if self._highlight_ctrl:
            self._highlight_ctrl.highlight(self.sender)

    def _on_changed(self):
        """Handler called when the translation gesture state changes. Computes and applies the translation delta."""
        super()._on_changed()

        moved_delta = self.sender.gesture_payload.moved
        moved_delta = self._manipulator._transform.transform_space(
            sc.Space.WORLD, sc.Space.OBJECT, [moved_delta[0], moved_delta[1], moved_delta[2], 0]
        )
        moved_delta = moved_delta[0:3]
        moved_prev = self._moved_snap[:]
        self._moved = [sum(x) for x in zip(self._moved, moved_delta)]

        self._moved_snap = self._moved.copy()
        snap = self._manipulator.model.get_snap(self._changing_item)
        if snap is not None:
            for i, snap_axis in enumerate(snap):
                if snap_axis:
                    self._moved_snap[i] = math.copysign(abs(self._moved[i]) // snap_axis * snap_axis, self._moved[i])
            moved_delta = [m - mp for m, mp in zip(self._moved_snap, moved_prev)]

        if moved_delta != [0, 0, 0]:
            new_gesture_payload = TranslateDragGesturePayload(self.gesture_payload, self._changing_item)
            new_gesture_payload.axis = self._axis
            new_gesture_payload.moved_delta = moved_delta
            new_gesture_payload.moved = self._moved_snap

            self._manipulator._process_gesture(TranslateChangedGesture, self.state, new_gesture_payload)

    def _on_ended(self):
        """Handler called when the translation gesture ends. Finalizes the translation and restores states."""
        super()._on_ended()

        payload = TranslateDragGesturePayload(self.gesture_payload, self._changing_item)
        payload.axis = self._axis
        self._manipulator._process_gesture(TranslateChangedGesture, self.state, payload)
        if self._highlight_ctrl:
            self._highlight_ctrl.dehighlight(self.sender)

    def _on_canceled(self):
        """Handler called when the translation gesture is canceled. Reverts any changes made during the translation."""
        self._on_ended()


class RotationGesture(TransformGesture):
    """A gesture class used for rotating objects in a 3D scene around a specified axis or freely without constraints.

    This class handles input related to object rotation and interacts with a manipulator and highlight control to provide visual feedback and manage the rotation behavior.

    Attributes:
        manipulator: TransformManipulator
            The manipulator associated with this gesture.
        axis: Sequence[int] | None
            The axis around which the object is rotated, or None for free rotation.
        viz_arc: sc.Arc
            The visual representation of the rotation arc.
        highlight_ctrl: HighlightControl
            The control responsible for managing highlights.
        order: int
            The priority order of the gesture, used for conflict resolution."""

    def __init__(
        self,
        manipulator: TransformManipulator,
        axis: Sequence[int] | None,
        viz_arc: sc.Arc,
        highlight_ctrl: HighlightControl,
        order: int = 0,
    ):
        """Initializes the RotationGesture with a given manipulator, rotation axis, visualization arc, highlight control, order, and additional arguments."""
        super().__init__(manipulator=manipulator, highlight_ctrl=highlight_ctrl, order=order, manager=PreventOthers())
        self._viz_arc = viz_arc
        self._axis = axis
        self._angle = 0
        self._last_free_intersect = None
        self._settings = carb.settings.get_settings()

    def process(self):
        """Processes the rotation gesture, taking into account the state of the arc and whether it's culled based on its orientation."""
        if isinstance(self.sender, sc.Arc) and self.sender.gesture_payload.culled:
            # Turn down the gesture if it on the wrong side of the arc
            if self.state == sc.GestureState.BEGAN:
                self.state = sc.GestureState.POSSIBLE

        super().process()

    def _on_began(self):
        """Handler called when the rotation gesture begins. Sets up the necessary state for the rotation operation."""
        super()._on_began()

        self._original_tickness = self.sender.thickness
        self.sender.thickness = self._original_tickness + 1
        self._begin_angle = self.sender.gesture_payload.angle

        if self._viz_arc:
            self._viz_arc.begin = self._begin_angle

        if self._axis is None:
            self._last_free_intersect, _ = self._sphere_intersect()

        self._changing_item = self._manipulator.model.get_item("rotate")
        self._manipulator._process_gesture(
            RotateChangedGesture, self.state, RotateDragGesturePayload(self.gesture_payload, self._changing_item)
        )
        if self._highlight_ctrl:
            self._highlight_ctrl.highlight(self.sender)

    def _on_changed(self):
        """Handler called when the rotation gesture state changes. Computes and applies the rotation delta."""
        super()._on_changed()

        prev_angle = self._angle
        self._angle = self.sender.gesture_payload.angle - self._begin_angle
        self._angle = self._angle / math.pi * 180  # convert to degree

        snap = self._manipulator.model.get_snap(self._changing_item)
        if snap:  # Not None and not zero
            self._angle = self._angle // snap * snap
            angle_delta = self._angle - prev_angle
        else:
            angle_delta = self.sender.gesture_payload.moved_angle
            angle_delta = angle_delta / math.pi * 180  # convert to degree

        screen_space = False
        free_rotation = False

        # handle the free rotation mode when grabbing the center of rotation manipulator
        if self._axis is None:
            axis, angle_delta = self._handle_free_rotation()
            if axis is not None and angle_delta is not None:
                free_rotation = True
            else:
                # early return, no gesture is generated for invalid free rotation
                return
        elif self._axis == [0, 0, 0]:
            axis = self.sender.transform_space(sc.Space.OBJECT, sc.Space.WORLD, [0, 0, 1, 0])
            screen_space = True
        else:
            axis = self._axis

        # normalize
        axis_len = math.sqrt(axis[0] ** 2 + axis[1] ** 2 + axis[2] ** 2)
        axis = [v / axis_len for v in axis]

        if not free_rotation:
            # confine angle in [-180, 180) range so the overlay doesn't block manipulated object too much
            angle = (self._angle - 360.0 * math.floor(self._angle / 360.0 + 0.5)) / 180.0 * math.pi
            self._viz_arc.end = angle + self._viz_arc.begin
            self._viz_arc.visible = True

        if angle_delta:
            new_gesture_payload = RotateDragGesturePayload(self.gesture_payload, self._changing_item)
            new_gesture_payload.axis = axis
            new_gesture_payload.angle = self._angle
            new_gesture_payload.angle_delta = angle_delta
            new_gesture_payload.screen_space = screen_space
            new_gesture_payload.free_rotation = free_rotation

            self._manipulator._process_gesture(RotateChangedGesture, self.state, new_gesture_payload)

    def _on_ended(self):
        """Handler called when the rotation gesture ends. Finalizes the rotation and restores states."""
        super()._on_ended()

        self.sender.thickness = self._original_tickness

        if self._viz_arc:
            self._viz_arc.visible = False

        self._manipulator._process_gesture(
            RotateChangedGesture, self.state, RotateDragGesturePayload(self.gesture_payload, self._changing_item)
        )
        if self._highlight_ctrl:
            self._highlight_ctrl.dehighlight(self.sender)

        if self._axis is None:
            self._last_free_intersect = None

    def _on_canceled(self):
        """Handler called when the rotation gesture is canceled. Reverts any changes made during the rotation."""
        self._on_ended()

    def _sphere_intersect(self) -> Tuple[List[float], bool]:
        """Computes the intersection point of a ray with a sphere representing the rotation manipulator, or the nearest point on the ray to the sphere if no intersection occurs.

        Returns:
            Tuple[List[float], bool]: A tuple containing the intersection or nearest point in world coordinates, and a boolean indicating whether the ray intersected the sphere.
        """
        intersect = self.sender.gesture_payload.ray_closest_point
        ndc_location = self.sender.transform_space(sc.Space.WORLD, sc.Space.NDC, intersect)
        ndc_ray_origin = copy.copy(ndc_location)
        ndc_ray_origin[2] = 0.0

        object_ray_origin = np.array(self.sender.transform_space(sc.Space.NDC, sc.Space.OBJECT, ndc_ray_origin))
        object_ray_end = np.array(self.sender.transform_space(sc.Space.NDC, sc.Space.OBJECT, ndc_location))

        dir = object_ray_end - object_ray_origin
        dir = dir / np.linalg.norm(dir)

        a = np.dot(dir, dir)
        b = 2.0 * np.dot(object_ray_origin, dir)
        c = np.dot(object_ray_origin, object_ray_origin) - self.sender.radius * self.sender.radius

        discriminant = b * b - 4 * a * c
        if discriminant >= 0.0:
            sqrt_discriminant = math.sqrt(discriminant)
            t = (-b - sqrt_discriminant) / (2.0 * a)
            if t >= 0:
                point = object_ray_origin + t * dir
                world = self.sender.transform_space(sc.Space.OBJECT, sc.Space.WORLD, point.tolist())
                return world, True

        # If no intersection, get the neareast point on the ray to the sphere
        nearest_dist = np.dot(-object_ray_origin, dir)
        point = object_ray_origin + dir * nearest_dist
        world = self.sender.transform_space(sc.Space.OBJECT, sc.Space.WORLD, point.tolist())
        return world, False

    def _handle_free_rotation(self) -> Tuple[List[float], float]:
        """Handles the free rotation mode when the user interacts with the center of the rotation manipulator. Computes the axis and angle of rotation based on the current mouse position and manipulator orientation.

        Returns:
            Tuple[List[float], float]: A tuple containing the rotation axis and the angle delta for the rotation gesture.
        """
        with np.errstate(all="raise"):
            try:
                axis = None
                angle_delta = None

                nearest_ray_point, intersected = self._sphere_intersect()
                last_intersect = copy.copy(self._last_free_intersect)
                self._last_free_intersect = nearest_ray_point

                mode = self._settings.get(CONSTANTS.FREE_ROTATION_TYPE_SETTING)
                if intersected or mode == CONSTANTS.FREE_ROTATION_TYPE_CLAMPED:
                    # Use clamped mode as long as ray intersects with sphere to maintain consistent behavior when dragging within the sphere
                    # clamped at the edge of free rotation sphere
                    if nearest_ray_point is not None and last_intersect is not None:
                        # calculate everything in world space
                        origin = np.array(self.sender.transform_space(sc.Space.OBJECT, sc.Space.WORLD, [0, 0, 0]))
                        vec1 = last_intersect - origin
                        vec1 = vec1 / np.linalg.norm(vec1)
                        vec2 = nearest_ray_point - origin
                        vec2 = vec2 / np.linalg.norm(vec2)

                        axis = np.cross(vec1, vec2)
                        mag = np.linalg.norm(axis)
                        if mag > 0:
                            axis = axis / mag
                            dot = np.dot(vec1, vec2)
                            if dot >= -1 and dot <= 1:
                                angle_delta = np.arccos(dot) / math.pi * 180
                                if not math.isfinite(angle_delta):
                                    raise FloatingPointError()

                elif mode == CONSTANTS.FREE_ROTATION_TYPE_CONTINUOUS:
                    # Continuous mode. Only fallback to it if not intersected and continuous_mode is on.
                    # extend beyond sphere edge for free rotation based on moved distance
                    moved = np.array(self.sender.gesture_payload.moved)
                    forward = self.sender.transform_space(sc.Space.OBJECT, sc.Space.WORLD, [0, 0, 1, 0])
                    forward = np.array([forward[0], forward[1], forward[2]])

                    moved_len = math.sqrt(np.dot(moved, moved))
                    if moved_len > 0:
                        moved_dir = moved / moved_len
                        forward = forward / np.linalg.norm(forward)
                        axis = np.cross(forward, moved_dir).tolist()
                        angle_delta = moved_len
            except Exception:
                axis = None
                angle_delta = None
            finally:
                return axis, angle_delta


class ScaleGesture(TransformGesture):
    """A gesture class used for scaling objects in a 3D scene.

    This class handles input related to resizing objects along specific axes or uniformly from the center in the scene. It integrates with a manipulator and a highlight control to provide interactive feedback and manage the scaling transformation.

    Attributes:
        manipulator: TransformManipulator
            The manipulator associated with this gesture.
        axis: Sequence[int]
            The axis along which the object is being scaled.
        highlight_ctrl: HighlightControl
            The control responsible for managing highlights.
        handle_lines: List[sc.Line], optional
            Lines representing the scaling handles.
        handle_dots: List[sc.Arc], optional
            Dots representing the scaling points.
        order: int
            The priority order of the gesture, used for conflict resolution."""

    def __init__(
        self,
        manipulator: TransformManipulator,
        axis: Sequence[int],
        highlight_ctrl: HighlightControl,
        handle_lines: List[sc.Line] = None,
        handle_dots: List[sc.Arc] = None,
        order: int = 0,
    ):
        """Initializes the ScaleGesture with a given manipulator, scaling axis, highlight control, optional handle lines, optional handle dots, and order. """
        super().__init__(manipulator=manipulator, highlight_ctrl=highlight_ctrl, order=order, manager=PreventOthers())
        self._settings = carb.settings.get_settings()
        self._axis = axis
        self._handle_lines = handle_lines or []
        self._handle_dots = handle_dots or []
        self._omni_scale = self._axis == [1, 1, 1]  # scale from the center dot

    def _get_dir_and_length_from_origin(self, point):
        point = self.sender.transform_space(
            sc.Space.WORLD, sc.Space.OBJECT, self.sender.gesture_payload.item_closest_point
        )
        transform = self._manipulator.model.get_as_floats(self._manipulator.model.get_item("transform"))
        origin_in_local = self.sender.transform_space(
            sc.Space.WORLD, sc.Space.OBJECT, [transform[12], transform[13], transform[14]]
        )
        diff = [s - o for s, o in zip(point, origin_in_local)]
        length = math.sqrt(diff[0] ** 2 + diff[1] ** 2 + diff[2] ** 2)
        dir = [x / length for x in diff]

        return point, dir, length

    def _on_began(self):
        """Handler called when the scaling gesture begins. Sets up the necessary state for the scaling operation."""
        super()._on_began()

        self._original_ends = [line.end.copy() for line in self._handle_lines]
        self._original_dot_transform = [
            [dot.transform[12], dot.transform[13], dot.transform[14]] for dot in self._handle_dots
        ]

        if self._omni_scale:
            self._omni_scale_direction = self._settings.get(CONSTANTS.OMNI_SCALE_DIR_SETTING)
            # scale is based on the screen space distance.
            intersect = self.sender.gesture_payload.ray_closest_point
            self._start_screen_location = self.sender.transform_space(sc.Space.WORLD, sc.Space.NDC, intersect)
        else:
            # scale is based world space distance
            self._start_point, self._direction, self._start_length = self._get_dir_and_length_from_origin(
                self.sender.gesture_payload.item_closest_point
            )
            self._accumulated_distance = self._start_length
        self._changing_item = self._manipulator.model.get_item("scale")
        self._scale_prev = None
        self._manipulator._process_gesture(
            ScaleChangedGesture, self.state, ScaleDragGesturePayload(self.gesture_payload, self._changing_item)
        )
        if self._highlight_ctrl:
            self._highlight_ctrl.highlight(self.sender)

    def _on_changed(self):
        """Handler called when the scaling gesture state changes. Computes and applies the scaling factor."""
        super()._on_changed()

        if self._omni_scale:
            SCALE_SPEED_FACTOR = 0.01
            # scale is based on the screen space movement. up or right is scaling up, down or left is scaling down
            intersect = self.sender.gesture_payload.ray_closest_point
            screen_location = self.sender.transform_space(sc.Space.WORLD, sc.Space.NDC, intersect)
            diff = 0
            if "X" in self._omni_scale_direction:
                scene_width = self.sender.scene_view.computed_content_width
                diff += (screen_location[0] - self._start_screen_location[0]) * scene_width
            if "Y" in self._omni_scale_direction:
                scene_height = self.sender.scene_view.computed_content_height
                diff += (screen_location[1] - self._start_screen_location[1]) * scene_height
            scale = diff * SCALE_SPEED_FACTOR + 1
        else:
            # scale is based how much distance has been dragged from starting length
            # use object space delta
            moved = self.sender.gesture_payload.moved
            moved = self.sender.transform_space(sc.Space.WORLD, sc.Space.OBJECT, [moved[0], moved[1], moved[2], 0])
            distance = moved[0] * self._direction[0] + moved[1] * self._direction[1] + moved[2] * self._direction[2]
            self._accumulated_distance += distance
            scale = self._accumulated_distance / self._start_length
        if scale == 0:
            scale = 0.001
        snap = self._manipulator.model.get_snap(self._changing_item)
        if snap:  # Not None and not zero
            if abs(scale) < snap:
                scale = math.copysign(1, scale)
            else:
                snap_scale = (abs(scale) - 1) // snap * snap + 1
                scale = math.copysign(snap_scale, scale)

        for i, line in enumerate(self._handle_lines):
            line.end = [
                self._original_ends[i][0] * scale,
                self._original_ends[i][1] * scale,
                self._original_ends[i][2] * scale,
            ]

        for i, dot in enumerate(self._handle_dots):
            t = dot.transform
            t[12] = self._original_dot_transform[i][0] * scale
            t[13] = self._original_dot_transform[i][1] * scale
            t[14] = self._original_dot_transform[i][2] * scale

            dot.transform = t

        if scale != self._scale_prev:
            self._scale_prev = scale
            new_gesture_payload = ScaleDragGesturePayload(self.gesture_payload, self._changing_item)
            new_gesture_payload.axis = self._axis
            new_gesture_payload.scale = scale
            self._manipulator._process_gesture(ScaleChangedGesture, self.state, new_gesture_payload)

    def _on_ended(self):
        """Handler called when the scaling gesture ends. Finalizes the scaling and restores states."""
        super()._on_ended()

        for i, line in enumerate(self._handle_lines):
            line.end = self._original_ends[i]

        for i, dot in enumerate(self._handle_dots):
            dot.transform[12] = self._original_dot_transform[i][0]
            dot.transform[13] = self._original_dot_transform[i][1]
            dot.transform[14] = self._original_dot_transform[i][2]

        self._manipulator._process_gesture(
            ScaleChangedGesture, self.state, ScaleDragGesturePayload(self.gesture_payload, self._changing_item)
        )
        if self._highlight_ctrl:
            self._highlight_ctrl.dehighlight(self.sender)

    def _on_canceled(self):
        """Handler called when the scaling gesture is canceled. Reverts any changes made during the scaling."""
        self._on_ended()


# The sole purpose of this dummy gesture is to prevent further viewport drag interaction by emitting a TransformChangedGesture,
# which:
#    Turns of selection rect in VP1
#    Prevents other gestures in VP2
class DummyGesture(TransformGesture):
    """A gesture used internally to prevent viewport interactions.

    This gesture is not associated with any visual manipulator elements; its primary function is to emit TransformChangedGesture events to disable selection rectangles in the viewport and prevent other gestures from being recognized when certain manipulator-related conditions are met.

    Args:
        manipulator (TransformManipulator): The manipulator associated with the gesture.
    """

    def __init__(self, manipulator: TransformManipulator):
        """Initializes the DummyGesture with a given manipulator."""
        # toolbar always has smaller order value to take precedence over manipulator handles.
        super().__init__(manipulator, None, order=-999, manager=PreventOthers())

    def _on_began(self):
        """Handler called when the dummy gesture begins. Processes a TransformChangedGesture to prevent viewport interaction."""
        self._manipulator._process_gesture(
            TransformChangedGesture, self.state, TransformDragGesturePayload(self.gesture_payload, None)
        )

    def _on_changed(self):
        """Handler for when the dummy gesture state changes. No implementation required."""
        ...

    def _on_ended(self):
        """Handler called when the dummy gesture ends. Processes a TransformChangedGesture to resume viewport interaction."""
        self._manipulator._process_gesture(
            TransformChangedGesture, self.state, TransformDragGesturePayload(self.gesture_payload, None)
        )

    def _on_canceled(self):
        """Handler called when the dummy gesture is canceled. Behaves like the end handler."""
        self._on_ended()


# The sole purpose of this dummy gesture is to prevent further viewport click interaction which:
#    Prevents other gestures in VP2 (e.g. right click on manipulator toolbar won't further trigger viewport context menu)
#    (no VP1 support for this!)
class DummyClickGesture(sc.ClickGesture):
    """A gesture used to prevent viewport click interactions.

    This gesture is used to block other gestures in the viewport, such as right-clicking on a manipulator toolbar to prevent triggering the viewport context menu.

    Args:
        mouse_button: int
            The mouse button associated with the click gesture."""

    def __init__(self, mouse_button: int):
        """Initializes the DummyClickGesture with a specified mouse button."""
        super().__init__(mouse_button=mouse_button, manager=PreventOthers())

    @property
    def order(self):
        """The order property of the DummyClickGesture.

        Returns:
            int: The priority order of the gesture."""
        return -1000
