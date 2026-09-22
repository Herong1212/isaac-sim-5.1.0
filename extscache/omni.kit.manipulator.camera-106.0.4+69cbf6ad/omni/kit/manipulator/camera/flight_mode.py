# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ['FlightModeKeyboard', 'get_keyboard_input']

from .model import CameraManipulatorModel, _accumulate_values, _optional_floats
from omni.ui import scene as sc
import omni.appwindow
from pxr import Gf
import carb
import carb.input


class FlightModeValues:
    def __init__(self):
        self.__xyz_values = (
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        )

    def update(self, i0, i1, value) -> bool:
        self.__xyz_values[i0][i1] = value
        total = 0
        for values in self.__xyz_values:
            values[2] = values[1] - values[0]
            total += values[2] != 0
        return total != 0

    @property
    def value(self):
        return (
            self.__xyz_values[0][2],
            self.__xyz_values[1][2],
            self.__xyz_values[2][2]
        )


class FlightModeKeyboard:
    __g_char_map = None

    @staticmethod
    def get_char_map():
        if not FlightModeKeyboard.__g_char_map:
            key_char_map = {
                'w': (2, 0),
                's': (2, 1),
                'a': (0, 0),
                'd': (0, 1),
                'q': (1, 0),
                'e': (1, 1),
            }
            carb_key_map = {eval(f'carb.input.KeyboardInput.{ascii_val.upper()}'): index for ascii_val, index in key_char_map.items()}
            FlightModeKeyboard.__g_char_map = carb_key_map

        for k, v in FlightModeKeyboard.__g_char_map.items():
            yield k, v

    def __init__(self):
        self.__input = None
        self.__model = None
        self.__stop_events = False
        self.__keyboard_sub = None
        self.__initial_speed = None
        self.__current_adjusted_speed = 1

    def init(self, model, iinput, mouse, mouse_button, app_window) -> None:
        self.__model = model
        if self.__input is None:
            self.__input = iinput
            self.__keyboard = app_window.get_keyboard()
            self.__keyboard_sub = iinput.subscribe_to_keyboard_events(self.__keyboard, self.__on_key)
            self.__mouse = mouse
            # XXX: This isn't working
            # self.__mouse_sub = iinput.subscribe_to_mouse_events(mouse, self.__on_mouse)
            # So just query the state on key-down
            self.__mouse_button = mouse_button
            self.__key_index = {k: v for k, v in FlightModeKeyboard.get_char_map()}
            self.__values = FlightModeValues()
            # Setup for modifier keys adjusting speed
            self.__settings = carb.settings.get_settings()
            # Shift or Control can modify flight speed, get the current state
            self.__setup_speed_modifiers()

        # Need to update all input key states on start
        for key, index in self.__key_index.items():
            # Read the key and update the value. Update has to occur whether key is down or not as numeric field
            # might have text focus; causing carbonite not to deliver __on_key messages
            key_val = self.__input.get_keyboard_value(self.__keyboard, key)
            self.__values.update(*index, 1 if key_val else 0)

        # Record whether a previous invocation had started external events
        prev_stop = self.__stop_events
        # Test if any interesting key-pair result in a value
        key_down = any(self.__values.value)
        # If a key is no longer down, it may have not gotten to __on_key subscription if a numeric entry id focused
        # In that case there is no more key down so kill any external trigger
        if prev_stop and not key_down:
            prev_stop = False
            self.__model._stop_external_events()
        self.__stop_events = key_down or prev_stop
        self.__model.set_floats('fly', self.__values.value)
        if self.__stop_events:
            self.__model._start_external_events(True)

    def _cancel(self) -> bool:
        return self.__input.get_mouse_value(self.__mouse, self.__mouse_button) == 0 if self.__input else True

    @property
    def active(self) -> bool:
        """Returns if Flight mode is active or not"""
        return bool(self.__stop_events)

    def __adjust_speed_modifiers(self, cur_speed_mod: float, prev_speed_mod: float):
        # Get the current state from
        initial_speed = self.__settings.get('/persistent/app/viewport/camMoveVelocity') or 1
        # Undo any previos speed modification based on key state
        if prev_speed_mod and prev_speed_mod != 1:
            initial_speed /= prev_speed_mod
        # Store the unadjusted values for restoration later (camMoveVelocity may change underneath modifiers)
        self.__initial_speed = initial_speed
        # Set the new speed if it is different
        cur_speed = initial_speed * cur_speed_mod
        self.__settings.set('/persistent/app/viewport/camMoveVelocity', cur_speed)

    def __setup_speed_modifiers(self):
        # Default to legacy value of modifying speed by doubling / halving
        self.__speed_modifier_amount = self.__settings.get('/exts/omni.kit.manipulator.camera/flightMode/keyModifierAmount')
        if not self.__speed_modifier_amount:
            return

        # Store the current_adjusted_speed as inital_speed
        prev_speed_mod = self.__current_adjusted_speed
        cur_speed_mod = prev_speed_mod
        # Scan the input keys that modify speed and adjust current_adjusted_speed
        if self.__input.get_keyboard_value(self.__keyboard, carb.input.KeyboardInput.LEFT_SHIFT):
            cur_speed_mod *= self.__speed_modifier_amount
        if self.__input.get_keyboard_value(self.__keyboard, carb.input.KeyboardInput.LEFT_CONTROL):
            if self.__speed_modifier_amount != 0:
                cur_speed_mod /= self.__speed_modifier_amount

        # Store new speed into proper place
        if prev_speed_mod != cur_speed_mod:
            self.__current_adjusted_speed = cur_speed_mod
            self.__adjust_speed_modifiers(cur_speed_mod, prev_speed_mod)

    def __process_speed_modifier(self, key: carb.input.KeyboardEventType, is_down: bool):
        if not self.__speed_modifier_amount:
            return

        def speed_adjustment(increase: bool):
            return self.__speed_modifier_amount if increase else (1 / self.__speed_modifier_amount)

        prev_speed_mod = self.__current_adjusted_speed
        cur_speed_mod = prev_speed_mod
        if key == carb.input.KeyboardInput.LEFT_SHIFT:
            cur_speed_mod *= speed_adjustment(is_down)
        if key == carb.input.KeyboardInput.LEFT_CONTROL:
            cur_speed_mod *= speed_adjustment(not is_down)

        if prev_speed_mod != cur_speed_mod:
            self.__current_adjusted_speed = cur_speed_mod
            self.__adjust_speed_modifiers(cur_speed_mod, prev_speed_mod)
            return True
        return False

    def __on_key(self, e) -> bool:
        index, value, speed_changed = None, None, False
        event_type = e.type
        KeyboardEventType = carb.input.KeyboardEventType
        if event_type == KeyboardEventType.KEY_PRESS or event_type == KeyboardEventType.KEY_REPEAT:
            index, value = self.__key_index.get(e.input), 1
            if event_type == KeyboardEventType.KEY_PRESS:
                speed_changed = self.__process_speed_modifier(e.input, True)
        elif event_type == KeyboardEventType.KEY_RELEASE:
            index, value = self.__key_index.get(e.input), 0
            speed_changed = self.__process_speed_modifier(e.input, False)

        # If not a navigation key, pass it on to another handler (unless it was a speed-moficiation key).
        if not index:
            return not speed_changed

        canceled = self._cancel()
        if canceled:
            value = 0

        has_data = self.__values.update(*index, value)
        if hasattr(self.__model, '_start_external_events'):
            if has_data:
                self.__stop_events = True
                self.__model._start_external_events(True)
            elif self.__stop_events:
                self.__stop_events = False
                self.__model._stop_external_events(True)

        self.__model.set_floats('fly', self.__values.value)
        # self.__model._item_changed(None)

        if canceled:
            self.destroy()

        return False

    def end(self):
        self.destroy()
        return None

    def __del__(self):
        self.destroy()

    def destroy(self) -> None:
        if self.__initial_speed is not None:
            self.__settings.set('/persistent/app/viewport/camMoveVelocity', self.__initial_speed)
            self.__initial_speed = None
        self.__current_adjusted_speed = 1

        if self.__model:
            self.__model.set_floats('fly', None)
            if self.__stop_events:
                self.__model._stop_external_events()
        if self.__keyboard_sub:
            self.__input.unsubscribe_to_keyboard_events(self.__keyboard, self.__keyboard_sub)
            self.__keyboard_sub = None
        self.__keyboard = None
        # if self.__mouse_sub:
        #     self.__input.unsubscribe_to_mouse_events(self.__mouse, self.__mouse_sub)
        #     self.__mouse_sub = None
        self.__mouse = None
        self.__input = None
        self.__values = None
        self.__key_index = None


def get_keyboard_input(model, walk_through: FlightModeKeyboard = None, end_with_mouse_ended: bool = False, mouse_button=carb.input.MouseInput.RIGHT_BUTTON):
    iinput = carb.input.acquire_input_interface()
    app_window = omni.appwindow.get_default_app_window()
    mouse = app_window.get_mouse()
    mouse_value = iinput.get_mouse_value(mouse, mouse_button)
    if mouse_value:
        if walk_through is None:
            walk_through = FlightModeKeyboard()
        walk_through.init(model, iinput, mouse, mouse_button, app_window)
    elif walk_through and end_with_mouse_ended:
        walk_through.destroy()
        walk_through = None
    return walk_through
