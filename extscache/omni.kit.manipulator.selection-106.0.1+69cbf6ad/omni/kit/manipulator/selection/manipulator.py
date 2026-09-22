# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["SelectionManipulator", "SelectionMode"]

import carb.input
from omni.ui import scene as sc
from .model import SelectionShapeModel
from typing import List
import weakref


class SelectionMode:
    """An enumeration for different selection modes in a manipulator."""

    REPLACE = 0
    """Mode to replace the current selection with the new selection."""
    APPEND = 1
    """Mode to add to the current selection."""
    REMOVE = 2
    """Mode to remove from the current selection."""


def _optional_bool(model: sc.AbstractManipulatorModel, item: str, default_value: bool = False):
    values = model.get_as_ints(item)
    return values[0] if values else default_value


class _ModifierDown:
    def __init__(self):
        self.__input = carb.input.acquire_input_interface()

    def test(self, modifiers: int):
        mods_down = self.__input.get_global_modifier_flags(modifiers)
        return bool(mods_down & modifiers)


class _SelectionPreventer(sc.GestureManager):
    """Class to explicitly block selection in favor of alt-orbit when alt-dragging"""

    @staticmethod
    def __check_alt_modifier(gesture):
        return _ModifierDown().test(carb.input.KEYBOARD_MODIFIER_FLAG_ALT)

    def can_be_prevented(self, gesture):
        if self.__check_alt_modifier(gesture):
            if getattr(gesture, "name", None) == "SelectionDrag":
                return True

        # Never prevent in the middle or at the end of drag
        return (
            gesture.state != sc.GestureState.CHANGED
            and gesture.state != sc.GestureState.ENDED
            and gesture.state != sc.GestureState.CANCELED
        )

    def should_prevent(self, gesture, preventer):
        if self.__check_alt_modifier(gesture):
            name = getattr(gesture, "name", None)
            if name == "TumbleGesture":
                return False
            if name == "SelectionDrag":
                return True
        return super().should_prevent(gesture, preventer)


class _SelectionGesture:
    @classmethod
    def __get_selection_mode(self):
        mods_down = _ModifierDown()
        if mods_down.test(carb.input.KEYBOARD_MODIFIER_FLAG_SHIFT):
            return SelectionMode.APPEND
        if mods_down.test(carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL):
            return SelectionMode.REMOVE
        # alt_down = mods_down.test(carb.input.KEYBOARD_MODIFIER_FLAG_ALT)
        return SelectionMode.REPLACE

    @classmethod
    def _set_mouse(self, model: sc.AbstractManipulatorModel, ndc_mouse: List[float], is_start: bool = False):
        if is_start:
            model.set_floats("ndc_start", ndc_mouse)
            model.set_ints("mode", [self.__get_selection_mode()])
        elif _optional_bool(model, "live_update"):
            model.set_ints("mode", [self.__get_selection_mode()])
        model.set_floats("ndc_current", ndc_mouse)

    @classmethod
    def _on_ended(self, manipulator: sc.Manipulator):
        # This is needed to not fight with alt+left-mouse camera orbit when not blocking alt explicitly
        # manipulator.invalidate()
        model = manipulator.model
        model.set_floats("ndc_start", [])
        model.set_floats("ndc_current", [])
        model.set_ints("mode", [])
        model._item_changed(model.get_item("ndc_rect"))


class _DragGesture(sc.DragGesture):
    def __init__(self, manipulator: sc.Manipulator, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__manipulator = manipulator

    def on_began(self):
        _SelectionGesture._set_mouse(self.__manipulator.model, self.sender.gesture_payload.mouse, True)

    def on_changed(self):
        model = self.__manipulator.model
        _SelectionGesture._set_mouse(model, self.sender.gesture_payload.mouse)
        model._item_changed(model.get_item("ndc_rect"))

    def on_ended(self):
        # Track whether on_changed has been called.
        # When it has: this drag is a drag.
        # When it hasn't: this drag is actually a click.
        if self.state != sc.GestureState.ENDED:
            return
        _SelectionGesture._on_ended(self.__manipulator)


class _ClickGesture(sc.ClickGesture):
    def __init__(self, manipulator: sc.Manipulator, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__manipulator = manipulator

    def on_ended(self):
        model = self.__manipulator.model
        _SelectionGesture._set_mouse(model, self.sender.gesture_payload.mouse, True)
        model._item_changed(model.get_item("ndc_rect"))
        _SelectionGesture._on_ended(self.__manipulator)


class SelectionManipulator(sc.Manipulator):
    """A manipulator for selecting objects within a scene.

    This manipulator allows users to select objects using various gestures, such as dragging for rectangle selection or clicking for single object selection. It can be styled with custom colors and thickness for the selection rectangle.

    Args:
        style (dict, optional): A dictionary with custom style attributes. Defaults to None.
        *args: Variable length argument list which will be forwarded to execute.
        **kwargs: Arbitrary keyword arguments that will be forwarded to execute.

    Attributes:
        model: SelectionShapeModel
            The model associated with the selection manipulator.
        gestures: list
            A list of gesture recognizers associated with the manipulator."""

    def __init__(self, style: dict = None, *args, **kwargs):
        """Initializes a selection manipulator with optional custom styling.

        Args:
            style (dict, optional): A dictionary with custom style attributes. Defaults to None.
            *args: Variable length argument list which will be forwarded to execute.
            **kwargs: Arbitrary keyword arguments that will be forwarded to execute.
        """
        applied_style = {
            "as_rect": True,
            "thickness": 2.0,
            "color": (1.0, 1.0, 1.0, 0.2),
            "inner_color": (1.0, 1.0, 1.0, 0.2),
        }
        if style:
            applied_style.update(style)
        super().__init__(*args, **kwargs)
        self.__as_rect = applied_style["as_rect"]
        self.__outline_color = applied_style["color"]
        self.__inner_color = applied_style["inner_color"]
        self.__thickness = applied_style["thickness"]
        self.__polygons, self.__transform = [], None
        # Provide some defaults
        if not self.model:
            self.model = SelectionShapeModel()
        self.gestures = []

    def on_build(self):
        """Builds the selection manipulator's UI elements."""
        if self.__transform:
            self.__transform.clear()
        self.__polygons = []

        sc.Screen(
            gestures=self.gestures
            or [
                _DragGesture(weakref.proxy(self), manager=_SelectionPreventer(), name="SelectionDrag"),
                _ClickGesture(weakref.proxy(self), name="SelectionClick"),
            ]
        )
        self.__transform = sc.Transform(look_at=sc.Transform.LookAt.CAMERA)

    def __draw_shape(self, start, end, as_rect):
        """Draws the selection shape on the screen.

        Args:
            start (Tuple[float, float, float]): The starting point of the selection shape in OBJECT space.
            end (Tuple[float, float, float]): The ending point of the selection shape in OBJECT space.
            as_rect (bool): Determines if the selection shape should be drawn as a rectangle or a polygon.
        """
        if as_rect:
            avg_z = (start[2] + end[2]) * 0.5
            points = (
                (start[0], start[1], avg_z),
                (end[0], start[1], avg_z),
                (end[0], end[1], avg_z),
                (start[0], end[1], avg_z),
            )
        else:
            if self.__polygons:
                points = self.__polygons[0].positions + [end]
            else:
                points = start, end
            # FIXME: scene.ui needs a full rebuild on this case
            self.__transform.clear()
            self.__polygons = []

        npoints = len(points)
        visible = npoints >= 3
        if not self.__polygons:
            with self.__transform:
                faces = [x for x in range(npoints)]
                # TODO: omni.ui.scene Shouldn't requires redundant color & thickness for constant color
                if self.__inner_color:
                    self.__polygons.append(
                        sc.PolygonMesh(
                            points, [self.__inner_color] * npoints, [npoints], faces, wireframe=False, visible=visible
                        )
                    )
                if self.__thickness and self.__outline_color:
                    self.__polygons.append(
                        sc.PolygonMesh(
                            points,
                            [self.__outline_color] * npoints,
                            [npoints],
                            faces,
                            wireframe=True,
                            thicknesses=[self.__thickness] * npoints,
                            visible=visible,
                        )
                    )
        else:
            for poly in self.__polygons:
                poly.positions = points
                poly.visible = visible

    def on_model_updated(self, item):
        """Updates the selection manipulator when the model changes.

        Args:
            item: The item in the model that was updated.
        """
        model = self.model
        if item != model.get_item("ndc_rect"):
            return

        ndc_rect = model.get_as_floats("ndc_rect")
        if ndc_rect:
            ndc_depth = 1
            start = self.__transform.transform_space(
                sc.Space.NDC, sc.Space.OBJECT, (ndc_rect[0], ndc_rect[1], ndc_depth)
            )
            end = self.__transform.transform_space(sc.Space.NDC, sc.Space.OBJECT, (ndc_rect[2], ndc_rect[3], ndc_depth))
            self.__draw_shape(start, end, self.__as_rect)
        else:
            self.__transform.clear()
            self.__polygons = []
