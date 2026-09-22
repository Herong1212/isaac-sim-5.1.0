# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ['CameraGestureBase']

from omni.ui import scene as sc
from .model import _accumulate_values, _optional_bool, _optional_floats, _flatten_matrix
from .flight_mode import get_keyboard_input

import carb.settings

from pxr import Gf
from typing import Callable, Sequence

# Base class for camera transform manipulation/gesture
#
class CameraGestureBase(sc.DragGesture):
    def __init__(self, model: sc.AbstractManipulatorModel, configure_model: Callable = None, name: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name if name else self.__class__.__name__
        self.model = model
        # XXX: Need a manipulator on_began method
        self.__configure_model = configure_model
        self.__prev_mouse = None
        self.__prev_mouse_time = None
        self.__keyboard = None
        self.__fly_active = None

    def destroy(self):
        self.model = None
        self._disable_flight()
        super().destroy()

    @property
    def center_of_interest(self):
        return Gf.Vec3d(self.model.get_as_floats('center_of_interest'))

    @property
    def initial_transform(self):
        return Gf.Matrix4d(*self.model.get_as_floats('initial_transform'))

    @property
    def last_transform(self):
        return Gf.Matrix4d(*self.model.get_as_floats('transform'))

    @property
    def projection(self):
        return Gf.Matrix4d(*self.model.get_as_floats('projection'))

    @property
    def orthographic(self):
        return _optional_bool(self.model, 'orthographic')

    @property
    def disable_pan(self):
        return _optional_bool(self.model, 'disable_pan')

    @property
    def disable_tumble(self):
        return _optional_bool(self.model, 'disable_tumble')

    @property
    def disable_look(self):
        return _optional_bool(self.model, 'disable_look')

    @property
    def disable_zoom(self):
        return _optional_bool(self.model, 'disable_zoom')

    @property
    def intertia(self):
        inertia = _optional_bool(self.model, 'inertia_enabled')
        if not inertia:
            return 0
        inertia = _optional_floats(self.model, 'inertia_seconds')
        return inertia[0] if inertia else 0

    @property
    def up_axis(self):
        # Assume Y-up if not specified
        return _optional_bool(self.model, 'up_axis', 1)

    @staticmethod
    def __conform_speed(values):
        if values:
            vlen = len(values)
            if vlen == 1:
                return (values[0], values[0], values[0])
            if vlen == 2:
                return (values[0], values[1], 0)
            return values
        return (1, 1, 1)

    def get_rotation_speed(self, secondary):
        model = self.model
        rotation_speed = self.__conform_speed(_optional_floats(model, 'rotation_speed'))
        secondary_speed = self.__conform_speed(_optional_floats(model, secondary))

        return (rotation_speed[0] * secondary_speed[0],
                rotation_speed[1] * secondary_speed[1],
                rotation_speed[2] * secondary_speed[2])

    @property
    def tumble_speed(self):
        return self.get_rotation_speed('tumble_speed')

    @property
    def look_speed(self):
        return self.get_rotation_speed('look_speed')

    @property
    def move_speed(self):
        return self.__conform_speed(_optional_floats(self.model, 'move_speed'))

    @property
    def world_speed(self):
        model = self.model
        ndc_scale = self.__conform_speed(_optional_floats(model, 'ndc_scale'))
        world_speed = self.__conform_speed(_optional_floats(model, 'world_speed'))
        return Gf.CompMult(world_speed, ndc_scale)

    def _disable_flight(self):
        if self.__keyboard:
            self.__keyboard.destroy()

    def _setup_keyboard(self, model, exit_mode: bool) -> bool:
        """Setup keyboard and return whether the manipualtor mode (fly) was broadcast to consumers"""
        self.__keyboard = get_keyboard_input(model, self.__keyboard)
        if self.__keyboard:
            # If the keyboard is active, broadcast that fly mode has been entered
            if self.__keyboard.active:
                self.__fly_active = True
                model._broadcast_mode("fly")
                return True
            # Check if fly mode was exited
            if self.__fly_active:
                exit_mode = self.name.replace('Gesture', '').lower() if exit_mode else ""
                model._broadcast_mode(exit_mode)
                return True
        return False

    # omni.ui.scene Gesture interface
    # We abstract on top of this due to asynchronous picking, in that we
    # don't want a gesture to begin until the object/world-space query has completed
    # This 'delay' could be a setting, but will wind up 'snapping' from the transition
    # from a Camera's centerOfInterest to the new world-space position
    def on_began(self, mouse: Sequence[float] = None):
        model = self.model

        # Setup flight mode and possibly broadcast that mode to any consumers
        was_brodcast = self._setup_keyboard(model, False)
        # If fly mode was not broadcast, then brodcast this gesture's mode
        if not was_brodcast:
            # LookGesture => look
            manip_mode = self.name.replace('Gesture', '').lower()
            model._broadcast_mode(manip_mode)

        mouse = mouse if mouse else self.sender.gesture_payload.mouse
        if self.__configure_model:
            self.__configure_model(model, mouse)
        self.__prev_mouse = mouse

        xf = model.get_as_floats('transform')
        if xf:
            # Save an imutable copy of transform for undoable end-event
            model.set_floats('initial_transform', xf.copy())

        coi = model.get_as_floats('center_of_interest')
        if coi:
            # Save an imutable copy of center_of_interest for end adjustment if desired (avoiding space conversions)
            model.set_floats('center_of_interest_start', coi.copy())
            model._item_changed('center_of_interest')

        model.set_ints('interaction_active', [1])

    def on_changed(self, mouse: Sequence[float] = None):
        self._setup_keyboard(self.model, True)
        cur_mouse = mouse if mouse else self.sender.gesture_payload.mouse
        mouse_moved = (cur_mouse[0] - self.__prev_mouse[0], cur_mouse[1] - self.__prev_mouse[1])
        # if (mouse_moved[0] != 0) or (mouse_moved[1] != 0):
        self.__prev_mouse = cur_mouse
        self.on_mouse_move(mouse_moved)

    def on_ended(self):
        model = self.model
        final_position = True

        # Brodcast that the camera manipulationmode is now none
        model._broadcast_mode("")

        if self.__keyboard:
            self.__keyboard = self.__keyboard.end()
            final_position = self.__keyboard is None

        self.__prev_mouse = None
        self.__prev_mouse_time = None

        if final_position:
            if model._start_external_events(False):
                model._stop_external_events(False)
            self.__apply_as_undoable()

        model.set_ints('adjust_center_of_interest', [])
        model.set_floats('current_aperture', [])
        model.set_ints('interaction_active', [0])
        # model.set_floats('center_of_interest_start', [])
        # model.set_floats('center_of_interest_picked', [])

    def dirty_items(self, model: sc.AbstractManipulatorModel):
        model = self.model
        cur_item = model.get_item('transform')
        if model.get_as_floats('initial_transform') != model.get_as_floats(cur_item):
            return [cur_item]

    def __apply_as_undoable(self):
        model = self.model
        dirty_items = self.dirty_items(model)
        if dirty_items:
            model.set_ints('interaction_ended', [1])
            try:
                for item in dirty_items:
                    model._item_changed(item)
            except:
                raise
            finally:
                model.set_ints('interaction_ended', [0])

    def _accumulate_values(self, key: str, x: float, y: float, z: float):
        item = _accumulate_values(self.model, key, x, y, z)
        if item:
            self.model._item_changed(None if self.__keyboard else item)
