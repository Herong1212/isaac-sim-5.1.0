# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from .model import _accumulate_values

import omni.kit.app
from omni.ui import scene as sc
import carb

import asyncio
from typing import Dict, List, Sequence, Set

# Setting per action mode (i.e):
# /exts/omni.kit.manipulator.camera/gamePad/fly/deadZone
# /exts/omni.kit.manipulator.camera/gamePad/look/deadZone
ACTION_MODE_SETTING_KEYS = {"scale", "deadZone"}
ACTION_MODE_SETTING_ROOT = "/exts/omni.kit.manipulator.camera/gamePad"
# Setting per action trigger (i.e):
# /exts/omni.kit.manipulator.camera/gamePad/button/a/scale
ACTION_TRIGGER_SETTING_KEYS = {"scale"}

__all__ = ['GamePadController']


class ValueMapper:
    def __init__(self, mode: str, trigger: str, index: int, sub_index: int):
        self.__mode: str = mode
        self.__trigger: str = trigger
        self.__index: int = index
        self.__sub_index = sub_index

    @property
    def mode(self) -> str:
        return self.__mode

    @property
    def trigger(self) -> str:
        return self.__trigger

    @property
    def index(self) -> int:
        return self.__index

    @property
    def sub_index(self) -> int:
        return self.__sub_index


class ModeSettings:
    def __init__(self, action_mode: str, settings: carb.settings.ISettings):
        self.__scale: float = 1.0
        self.__dead_zone: float = 1e-04
        self.__action_mode = action_mode
        self.__setting_subs: Sequence[carb.settings.SubscriptionId] = []
        for setting_key in ACTION_MODE_SETTING_KEYS:
            sp = self.__get_setting_path(setting_key)
            self.__setting_subs.append(
                settings.subscribe_to_node_change_events(sp, lambda *args, k=setting_key: self.__setting_changed(*args, setting_key=k))
            )
            self.__setting_changed(None, carb.settings.ChangeEventType.CHANGED, setting_key=setting_key)

    def __del__(self):
        self.destroy()

    def __get_setting_path(self, setting_key: str):
        return f"{ACTION_MODE_SETTING_ROOT}/{self.__action_mode}/{setting_key}"

    def __setting_changed(self, item: carb.dictionary.Item, event_type: carb.settings.ChangeEventType, setting_key: str):
        if event_type == carb.settings.ChangeEventType.CHANGED:
            setting_path = self.__get_setting_path(setting_key)
            if setting_key == "scale":
                self.__scale = carb.settings.get_settings().get(setting_path)
                if self.__scale is None:
                    self.__scale = 1.0
            elif setting_key == "deadZone":
                # Use absolute value, no negative dead-zones and clamp to 1.0
                dead_zone = carb.settings.get_settings().get(setting_path)
                self.__dead_zone = min(abs(dead_zone) or 1e-04, 1.0) if (dead_zone is not None) else 0.0

    def destroy(self, settings: carb.settings.ISettings = None):
        settings = settings or carb.settings.get_settings()
        for setting_sub in self.__setting_subs:
            settings.unsubscribe_to_change_events(setting_sub)
        self.__setting_subs = tuple()

    def get_value(self, value: float, axis_idx: int) -> float:
        # Legacy implementation, which scales input value into new range fitted by dead_zone
        value = (value - self.__dead_zone) / (1.0 - self.__dead_zone)
        value = max(0, min(1, value))
        scale = self.__scale
        return value * scale
        # Somewhat simpler version that doesn't scale input by dead-zone
        if abs(value) > self.__dead_zone:
            return value * scale
        return 0


def _limit_camera_velocity(value: float, settings: carb.settings.ISettings, context_name: str):
    cam_limit = settings.get('/exts/omni.kit.viewport.window/cameraSpeedLimit')
    if context_name in cam_limit:
        vel_min = settings.get('/persistent/app/viewport/camVelocityMin')
        if vel_min is not None:
            value = max(vel_min, value)
        vel_max = settings.get('/persistent/app/viewport/camVelocityMax')
        if vel_max is not None:
            value = min(vel_max, value)
    return value


def _adjust_flight_speed(xyz_value: Sequence[float]):
    y = xyz_value[1]
    if y == 0.0:
        return

    import math
    settings = carb.settings.get_settings()
    value = settings.get('/persistent/app/viewport/camMoveVelocity') or 1
    scaler = settings.get('/persistent/app/viewport/camVelocityScalerMultAmount') or 1.1
    scaler = 1.0 + (max(scaler, 1.0 + 1e-8) - 1.0) * abs(y)
    if y < 0:
        value = value / scaler
    elif y > 0:
        value = value * scaler
    if math.isfinite(value) and (value > 1e-8):
        value = _limit_camera_velocity(value, settings, 'gamepad')
        settings.set('/persistent/app/viewport/camMoveVelocity', value)


class GamePadController:
    def __init__(self, manipulator: sc.Manipulator):
        self.__manipulator: sc.Manipulator = manipulator
        self.__gp_event_sub: Dict[carb.input.Gamepad, int] = {}
        self.__compressed_events: Dict[int, float] = {}
        self.__action_modes: Dict[str, List[float]] = {}
        self.__app_event_sub: carb.events.ISubscription = None
        self.__mode_settings: Dict[str, ModeSettings] = {}
        self.__value_actions: Dict[carb.input.GamepadInput, ValueMapper] = {}
        self.__setting_subs: Sequence[carb.settings.SubscriptionId] = []
        self.__focus_sub: carb.events.ISubscription = None
        self.__pause_events: bool = False
        carb.settings.get_settings().set_default(f"{ACTION_MODE_SETTING_ROOT}/mustBeFocused", True)
        self.__must_be_focused = carb.settings.get_settings().get(f"{ACTION_MODE_SETTING_ROOT}/mustBeFocused")

        # Some button presses need synthetic events because unlike keyboard input, carb gamepad doesn't repeat.
        # event 1 left pressed: value = 0.5
        # event 2 right pressed: value = 0.5
        # these should cancel, but there is no notification of left event until it changes from 0.5
        # This is all handled in __gamepad_event
        trigger_synth = {carb.input.GamepadInput.RIGHT_TRIGGER, carb.input.GamepadInput.LEFT_TRIGGER}
        shoulder_synth = {carb.input.GamepadInput.RIGHT_SHOULDER, carb.input.GamepadInput.LEFT_SHOULDER}
        self.__synthetic_state_init = {
            carb.input.GamepadInput.RIGHT_TRIGGER: trigger_synth,
            carb.input.GamepadInput.LEFT_TRIGGER: trigger_synth,
            carb.input.GamepadInput.RIGHT_SHOULDER: shoulder_synth,
            carb.input.GamepadInput.LEFT_SHOULDER: shoulder_synth,
        }
        self.__synthetic_state = self.__synthetic_state_init.copy()

        self.__init_gamepad_action(None, carb.settings.ChangeEventType.CHANGED)

        self.__gp_connect_sub = self._iinput.subscribe_to_gamepad_connection_events(self.__gamepad_connection)

    def __init_gamepad_action(self, item: carb.dictionary.Item, event_type: carb.settings.ChangeEventType):
        if event_type != carb.settings.ChangeEventType.CHANGED:
            return

        self.__value_actions: Dict[carb.input.GamepadInput, ValueMapper] = {}

        settings = carb.settings.get_settings()
        create_subs = not bool(self.__setting_subs)

        gamepad_action_paths = []
        gamepad_input_names = ["rightStick", "leftStick", "dPad", "trigger", "shoulder", "button/a", "button/b", "button/x", "button/y"]
        for gamepad_input in gamepad_input_names:
            action_setting_path = f"{ACTION_MODE_SETTING_ROOT}/{gamepad_input}/action"
            gamepad_action_paths.append(action_setting_path)
            if create_subs:
                self.__setting_subs.append(
                    settings.subscribe_to_node_change_events(action_setting_path, self.__init_gamepad_action)
                )

        # TODO: Maybe need more configuable/robust action mapping
        def action_mapping_4(action_mode: str):
            action_modes = action_mode.split(".")
            if len(action_modes) != 1:
                carb.log_error(f"Action mapping '{action_mode}' for quad input is invalid, using '{action_modes[0]}'")
            action_mode = action_modes[0]
            if action_mode == "look":
                return action_mode, (0, 1), (0, 1, 0, 1)
            return action_mode, (0, 2), (1, 0, 1, 0)

        def action_mapping_2(action_mode: str):
            action_modes = action_mode.split(".")
            if len(action_modes) != 2:
                action_modes = (action_modes[0], "x")
                carb.log_error(f"Action mapping '{action_mode}' for dual input is invalid, using '{action_modes[0]}.x'")
            axis = {'x': 0, 'y': 1, 'z': 2}.get(action_modes[1], 0)
            return action_modes[0], axis, (0, 1)

        def action_mapping_1(action_mode: str):
            action_modes = action_mode.split(".")
            if len(action_modes) != 2:
                action_modes = (action_modes[0], "x")
                carb.log_error(f"Action mapping '{action_mode}' for dual input is invalid, using '{action_modes[0]}.x'")
            axis = {'x': 0, 'y': 1, 'z': 2}.get(action_modes[1], 0)
            return action_modes[0], axis, 0

        # Go through the list of named events and setup the action based on it's value
        right_stick_action = settings.get(gamepad_action_paths[0])
        if right_stick_action:
            right_stick_action, axis, sub_idx = action_mapping_4(right_stick_action)
            self.__value_actions[carb.input.GamepadInput.RIGHT_STICK_LEFT] = ValueMapper(right_stick_action, gamepad_input_names[0], axis[0], sub_idx[0])
            self.__value_actions[carb.input.GamepadInput.RIGHT_STICK_RIGHT] = ValueMapper(right_stick_action, gamepad_input_names[0], axis[0], sub_idx[1])
            self.__value_actions[carb.input.GamepadInput.RIGHT_STICK_UP] = ValueMapper(right_stick_action, gamepad_input_names[0], axis[1], sub_idx[2])
            self.__value_actions[carb.input.GamepadInput.RIGHT_STICK_DOWN] = ValueMapper(right_stick_action, gamepad_input_names[0], axis[1], sub_idx[3])

        left_stick_action = settings.get(gamepad_action_paths[1])
        if left_stick_action:
            left_stick_action, axis, sub_idx = action_mapping_4(left_stick_action)
            self.__value_actions[carb.input.GamepadInput.LEFT_STICK_LEFT] = ValueMapper(left_stick_action, gamepad_input_names[1], axis[0], sub_idx[0])
            self.__value_actions[carb.input.GamepadInput.LEFT_STICK_RIGHT] = ValueMapper(left_stick_action, gamepad_input_names[1], axis[0], sub_idx[1])
            self.__value_actions[carb.input.GamepadInput.LEFT_STICK_UP] = ValueMapper(left_stick_action, gamepad_input_names[1], axis[1], sub_idx[2])
            self.__value_actions[carb.input.GamepadInput.LEFT_STICK_DOWN] = ValueMapper(left_stick_action, gamepad_input_names[1], axis[1], sub_idx[3])

        dpad_action = settings.get(gamepad_action_paths[2])
        if dpad_action:
            dpad_action, axis, sub_idx = action_mapping_4(dpad_action)
            self.__value_actions[carb.input.GamepadInput.DPAD_LEFT] = ValueMapper(dpad_action, gamepad_input_names[2], axis[0], sub_idx[0])
            self.__value_actions[carb.input.GamepadInput.DPAD_RIGHT] = ValueMapper(dpad_action, gamepad_input_names[2], axis[0], sub_idx[1])
            self.__value_actions[carb.input.GamepadInput.DPAD_UP] = ValueMapper(dpad_action, gamepad_input_names[2], axis[1], sub_idx[2])
            self.__value_actions[carb.input.GamepadInput.DPAD_DOWN] = ValueMapper(dpad_action, gamepad_input_names[2], axis[1], sub_idx[3])

        trigger_action = settings.get(gamepad_action_paths[3])
        if trigger_action:
            trigger_action, axis, sub_idx = action_mapping_2(trigger_action)
            self.__value_actions[carb.input.GamepadInput.RIGHT_TRIGGER] = ValueMapper(trigger_action, gamepad_input_names[3], axis, sub_idx[0])
            self.__value_actions[carb.input.GamepadInput.LEFT_TRIGGER] = ValueMapper(trigger_action, gamepad_input_names[3], axis, sub_idx[1])

        shoulder_action = settings.get(gamepad_action_paths[4])
        if shoulder_action:
            shoulder_action, axis, sub_idx = action_mapping_2(shoulder_action)
            self.__value_actions[carb.input.GamepadInput.RIGHT_SHOULDER] = ValueMapper(shoulder_action, gamepad_input_names[4],  axis, sub_idx[0])
            self.__value_actions[carb.input.GamepadInput.LEFT_SHOULDER] = ValueMapper(shoulder_action, gamepad_input_names[4], axis, sub_idx[1])

        button_action = settings.get(gamepad_action_paths[5])
        if button_action:
            button_action, axis, sub_idx = action_mapping_1(button_action)
            self.__value_actions[carb.input.GamepadInput.A] = ValueMapper(button_action, gamepad_input_names[5], axis, sub_idx)

        button_action = settings.get(gamepad_action_paths[6])
        if button_action:
            button_action, axis, sub_idx = action_mapping_1(button_action)
            self.__value_actions[carb.input.GamepadInput.B] = ValueMapper(button_action, gamepad_input_names[6], axis, sub_idx)

        button_action = settings.get(gamepad_action_paths[7])
        if button_action:
            button_action, axis, sub_idx = action_mapping_1(button_action)
            self.__value_actions[carb.input.GamepadInput.X] = ValueMapper(button_action, gamepad_input_names[7], axis, sub_idx)

        button_action = settings.get(gamepad_action_paths[8])
        if button_action:
            button_action, axis, sub_idx = action_mapping_1(button_action)
            self.__value_actions[carb.input.GamepadInput.Y] = ValueMapper(button_action, gamepad_input_names[8], axis, sub_idx)

        for value_mapper in self.__value_actions.values():
            action_mode = value_mapper.mode
            if self.__mode_settings.get(action_mode) is None:
                self.__mode_settings[action_mode] = ModeSettings(action_mode, settings)
            action_trigger = value_mapper.trigger
            if self.__mode_settings.get(action_trigger) is None:
                self.__mode_settings[action_trigger] = ModeSettings(action_trigger, settings)

    def __del__(self):
        self.destroy()

    @property
    def _iinput(self):
        return carb.input.acquire_input_interface()

    async def __apply_events(self):
        # Grab the events to apply and reset the state to empty
        events, self.__compressed_events = self.__compressed_events, {}
        # Reset the synthetic state
        self.__synthetic_state = self.__synthetic_state_init.copy()
        if not events:
            return

        manipulator = self.__manipulator
        if not manipulator:
            return

        model = manipulator.model
        try:
            manipulator._on_began(model, None)
        except RuntimeError as e:
            carb.log_warn(f"manipulator._on_began raised RuntimeError({str(e)})")

        # Map the action to +/- values per x, y, z components
        action_modes: Dict[str, Dict[int, List[float]]] = {}
        for input, value in events.items():
            action = self.__value_actions.get(input)
            if not action:
                continue
            # Must exists, KeyError otherwise
            mode_setting = self.__mode_settings[action.mode]
            trigger_setting = self.__mode_settings[action.trigger]

            # Get the dict for this action storing +/- values per x, y, z
            pos_neg_value_dict = action_modes.get(action.mode) or {}
            # Get the +/- values for the x, y, z component
            pos_neg_values = pos_neg_value_dict.get(action.index) or [0, 0]
            # Scale the value by the action's scaling factor
            value = mode_setting.get_value(value, action.index)
            # Scale the value by the trigger's scaling factor
            value = trigger_setting.get_value(value, action.index)
            # Store the +/- value into the proper slot '+' into 0, '-' into 1
            pos_neg_values[action.sub_index] += value
            # Store back into the dict mapping x, y, z to +/- values
            pos_neg_value_dict[action.index] = pos_neg_values
            # Store back into the dict storing the +/- values per x, y, z into the action
            action_modes[action.mode] = pos_neg_value_dict

        # Collapse the +/- values per individual action and x, y, z into a single total
        for action_mode, pos_neg_value_dict in action_modes.items():
            # Some components may not have been touched but need to preserve last value
            xyz_value = self.__action_modes.get(action_mode) or [0, 0, 0]
            for xyz_index, pos_neg_value in pos_neg_value_dict.items():
                xyz_value[xyz_index] = pos_neg_value[0] - pos_neg_value[1]
            # Apply model speed to anything but fly (that is handled by model itself)
            if action_mode != "fly":
                model_speed = model.get_item(f"{action_mode}_speed")
                if model_speed is not None:
                    model_speed = model.get_as_floats(model_speed)
                    if model_speed is not None:
                        for i in range(len(model_speed)):
                            xyz_value[i] *= model_speed[i]
            # Store the final values
            self.__action_modes[action_mode] = xyz_value

        # Prune any actions that now do nothing (has 0 for x, y, and z)
        self.__action_modes = {
            action_mode: xyz_value for action_mode, xyz_value in self.__action_modes.items() if (xyz_value[0] or xyz_value[1] or xyz_value[2])
        }

        has_data: bool = bool(self.__action_modes)
        if has_data:
            self.__apply_gamepad_state()

        if hasattr(model, '_start_external_events'):
            if has_data:
                self.___start_external_events(model)
            else:
                self.__stop_external_events(model)

    def ___on_focus_event(self, e: carb.events.IEvent):
        if not self.__must_be_focused:
            return

        self.__pause_events = not e.payload["isFocused"]
        if not self.__pause_events:
            for gamepad in self.__gp_event_sub.keys():
                # If we're unpausing, read the current state
                for i in range(carb.input.GamepadInput.COUNT):
                    gi = carb.input.GamepadInput(i)
                    self.__compressed_events[gi] = self._iinput.get_gamepad_value(gamepad, gi)
        else:
            # Set everything to zero when pausing
            for i in range(carb.input.GamepadInput.COUNT):
                self.__compressed_events[carb.input.GamepadInput(i)] = 0.0

        # whether events are being paused or not, make sure that we apply the current state
        asyncio.ensure_future(self.__apply_events())

    def ___start_external_events(self, model):
        if self.__app_event_sub:
            return

        _broadcast_mode = getattr(model, '_broadcast_mode', None)
        if _broadcast_mode:
            _broadcast_mode("gamepad")

        from carb.eventdispatcher import get_eventdispatcher
        self.__app_event_sub = get_eventdispatcher().observe_event(
            event_name=omni.kit.app.GLOBAL_EVENT_UPDATE,
            on_event=self.__apply_gamepad_state,
            observer_name=f"omni.kit.manipulator.camera.GamePadController.{id(self)}",
            # order=omni.kit.app.UPDATE_ORDER_PYTHON_ASYNC_FUTURE_END_UPDATE
        )
        model._start_external_events(True)

    def __stop_external_events(self, model):
        if self.__app_event_sub:
            _broadcast_mode = getattr(model, '_broadcast_mode', None)
            if _broadcast_mode:
                _broadcast_mode("")

            self.__app_event_sub = None
            self.__action_modes = {}
            model._stop_external_events(True)

    def __apply_gamepad_state(self, *_):
        manipulator = self.__manipulator
        model = manipulator.model
        # manipulator._on_began(model, None)
        for action_mode, xyz_value in self.__action_modes.items():
            if action_mode == "fly":
                model.set_floats("fly", xyz_value)
                continue
            elif action_mode == "speed":
                _adjust_flight_speed(xyz_value)
                continue
            item = _accumulate_values(model, action_mode, xyz_value[0], xyz_value[1], xyz_value[2])
            if item:
                model._item_changed(item)

    def __gamepad_event(self, event: carb.input.GamepadEvent):
        # Ignore if paused
        if self.__pause_events:
            return

        event_input = event.input
        self.__compressed_events[event_input] = event.value

        # Gamepad does not get repeat events, so on certain button presses there needs to be a 'synthetic' event
        # that represents the inverse-key (left/right) based on its last/current state.
        synth_state = self.__synthetic_state.get(event.input)
        if synth_state:
            for synth_input in synth_state:
                del self.__synthetic_state[synth_input]
                if synth_input != event_input:
                    self.__compressed_events[synth_input] = self._iinput.get_gamepad_value(event.gamepad, synth_input)

        asyncio.ensure_future(self.__apply_events())

    def __gamepad_connection(self, event: carb.input.GamepadConnectionEvent):
        e_type = event.type
        e_gamepad = event.gamepad
        if e_type == carb.input.GamepadConnectionEventType.DISCONNECTED:
            e_gamepad_sub = self.__gp_event_sub.get(e_gamepad)
            if e_gamepad_sub:
                self._iinput.unsubscribe_to_gamepad_events(e_gamepad, e_gamepad_sub)
                del self.__gp_event_sub[e_gamepad]
                if not self.__gp_event_sub:
                    # No more gamepads, so remove focus subscription
                    self.__focus_sub = None

        elif e_type == carb.input.GamepadConnectionEventType.CONNECTED:
            if self.__gp_event_sub.get(e_gamepad):
                carb.log_error("Gamepad connected event, but already subscribed")
                return

            if not self.__focus_sub and self.__must_be_focused:
                app_window = omni.appwindow.acquire_app_window_factory_interface().get_app_window()
                self.__pause_events = not app_window.is_focused()

                self.__focus_sub = app_window.get_window_focus_event_stream().create_subscription_to_pop(
                    self.___on_focus_event
                )

            gp_event_sub = self._iinput.subscribe_to_gamepad_events(e_gamepad, self.__gamepad_event)
            if gp_event_sub:
                self.__gp_event_sub[e_gamepad] = gp_event_sub

    def destroy(self):
        iinput = self._iinput
        settings = carb.settings.get_settings()

        # Remove gamepad connected subscriptions
        if self.__gp_connect_sub:
            iinput.unsubscribe_to_gamepad_connection_events(self.__gp_connect_sub)
            self.__gp_connect_sub = None

        # Remove gamepad event subscriptions
        for gamepad, gamepad_sub in self.__gp_event_sub.items():
            iinput.unsubscribe_to_gamepad_events(gamepad, gamepad_sub)
        self.__gp_event_sub = {}

        # Remove any pending state on the model
        model = self.__manipulator.model if self.__manipulator else None
        if model:
            self.__stop_external_events(model)
            self.__manipulator = None

        # Remove any settings subscriptions
        for setting_sub in self.__setting_subs:
            settings.unsubscribe_to_change_events(setting_sub)
        self.__setting_subs = []

        # Destroy any mode/action specific settings
        for action_mode, mode_settings in self.__mode_settings.items():
            mode_settings.destroy(settings)
        self.__mode_settings = {}
