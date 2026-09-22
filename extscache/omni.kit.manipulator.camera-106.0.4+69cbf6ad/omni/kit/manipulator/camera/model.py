# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ['CameraManipulatorModel']

from omni.ui import scene as sc
from pxr import Gf
from typing import Any, Callable, List, Sequence, Union
from .math import TransformAccumulator
from .animation import AnimationEventStream
import time
import carb.profiler
import carb.settings

ALMOST_ZERO = 1.e-4

def _flatten_matrix(matrix: Gf.Matrix4d):
    return [matrix[0][0], matrix[0][1], matrix[0][2], matrix[0][3],
            matrix[1][0], matrix[1][1], matrix[1][2], matrix[1][3],
            matrix[2][0], matrix[2][1], matrix[2][2], matrix[2][3],
            matrix[3][0], matrix[3][1], matrix[3][2], matrix[3][3]]


def _optional_floats(model: sc.AbstractManipulatorModel, item: str, default_value: Sequence[float] = None):
    item = model.get_item(item)
    if item:
        values = model.get_as_floats(item)
        if values:
            return values
    return default_value

def _optional_float(model: sc.AbstractManipulatorModel, item: str, default_value: float = 0):
    item = model.get_item(item)
    if item:
        values = model.get_as_floats(item)
        if values:
            return values[0]
    return default_value

def _optional_int(model: sc.AbstractManipulatorModel, item: str, default_value: int = 0):
    item = model.get_item(item)
    if item:
        values = model.get_as_ints(item)
        if values:
            return values[0]
    return default_value

def _optional_bool(model: sc.AbstractManipulatorModel, item: str, default_value: bool = False):
    return _optional_int(model, item, default_value)


def _accumulate_values(model: sc.AbstractManipulatorModel, name: str, x: float, y: float, z: float):
    item = model.get_item(name)
    if item:
        values = model.get_as_floats(item)
        model.set_floats(item, [values[0] + x, values[1] + y, values[2] + z] if values else [x, y, z])
    return item


def _scalar_or_vector(value: Sequence[float]):
    acceleration_len = len(value)
    if acceleration_len == 1:
        return Gf.Vec3d(value[0], value[0], value[0])
    if acceleration_len == 2:
        return Gf.Vec3d(value[0], value[1], 1)
    return Gf.Vec3d(value[0], value[1], value[2])


class ModelState:
    def __reduce_value(self, vec: Gf.Vec3d):
        if vec and (vec[0] == 0 and vec[1] == 0 and vec[2] == 0):
            return None
        return vec

    def __expand_value(self, vec: Gf.Vec3d, alpha: float):
        if vec:
            vec = tuple(v * alpha for v in vec)
            if vec[0] != 0 or vec[1] != 0 or vec[2] != 0:
                return vec
        return None

    def __init__(self, tumble: Gf.Vec3d = None, look: Gf.Vec3d = None, move: Gf.Vec3d = None, fly: Gf.Vec3d = None):
        self.__tumble = self.__reduce_value(tumble)
        self.__look = self.__reduce_value(look)
        self.__move = self.__reduce_value(move)
        self.__fly = self.__reduce_value(fly)

    def any_values(self):
        return self.__tumble or self.__look or self.__move or self.__fly

    def apply_alpha(self, alpha: float):
        return (self.__expand_value(self.__tumble, alpha),
                self.__expand_value(self.__look, alpha),
                self.__expand_value(self.__move, alpha),
                self.__expand_value(self.__fly, alpha))

    @property
    def tumble(self):
        return self.__tumble

    @property
    def look(self):
        return self.__look

    @property
    def move(self):
        return self.__move

    @property
    def fly(self):
        return self.__fly


class Velocity:
    def __init__(self, acceleration: Sequence[float], dampening: Sequence[float] = (10,), clamp_dt: float = 0.15):
        self.__velocity = Gf.Vec3d(0, 0, 0)
        self.__acceleration_rate = _scalar_or_vector(acceleration)
        self.__dampening = _scalar_or_vector(dampening)
        self.__clamp_dt = clamp_dt

    def apply(self, value: Gf.Vec3d, dt: float, alpha: float = 1):
        ### XXX: We're not locked to anything and event can come in spuriously
        ### So clamp the max delta-time to a value (if this is to high, it can introduces lag)
        if (dt > 0) and (dt > self.__clamp_dt):
            dt = self.__clamp_dt
        if value:
            acceleration = Gf.CompMult(value, self.__acceleration_rate) * alpha
            self.__velocity += acceleration * dt

        damp_factor = tuple(max(min(v * dt, 0.75), 0) for v in self.__dampening)
        self.__velocity += Gf.CompMult(-self.__velocity, Gf.Vec3d(*damp_factor))

        if Gf.Dot(self.__velocity, self.__velocity) < ALMOST_ZERO:
            self.__velocity = Gf.Vec3d(0, 0, 0)

        return self.__velocity * dt

    @staticmethod
    def create(model: sc.AbstractManipulatorModel, mode: str, clamp_dt: float = 0.15):
        acceleration = _optional_floats(model, f'{mode}_acceleration')
        if acceleration is None:
            return None
        dampening = _optional_floats(model, f'{mode}_dampening')
        return Velocity(acceleration, dampening or (10, 10, 10), clamp_dt)


class Decay:
    def __init__(self):
        pass

    def apply(self, value: Gf.Vec3d, dt: float, alpha: float = 1):
        return value * alpha if value else None


class CameraManipulatorModel(sc.AbstractManipulatorModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__settings = carb.settings.get_settings()

        self.__items = {
            # 'view': (sc.AbstractManipulatorItem(), 16),
            'projection': (sc.AbstractManipulatorItem(), 16),
            'transform': (sc.AbstractManipulatorItem(), 16),
            'orthographic': (sc.AbstractManipulatorItem(), 1),
            'center_of_interest': (sc.AbstractManipulatorItem(), 3),
            # Accumulated movement
            'move': (sc.AbstractManipulatorItem(), 3),
            'tumble': (sc.AbstractManipulatorItem(), 3),
            'look': (sc.AbstractManipulatorItem(), 3),
            'fly': (sc.AbstractManipulatorItem(), 3),
            # Optional speed for world (pan, truck) and rotation (tumble, look) operation
            # Can be set individually for x, y, z or as a scalar
            'world_speed': (sc.AbstractManipulatorItem(), (3, 1)),
            'move_speed': (sc.AbstractManipulatorItem(), (3, 1)),
            'rotation_speed': (sc.AbstractManipulatorItem(), (3, 1)),
            'tumble_speed': (sc.AbstractManipulatorItem(), (3, 1)),
            'look_speed': (sc.AbstractManipulatorItem(), (3, 1)),
            'fly_speed': (sc.AbstractManipulatorItem(), (3, 1)),
            # Inertia enabled, and amoint of second to apply it for
            'inertia_enabled': (sc.AbstractManipulatorItem(), 1),
            'inertia_seconds': (sc.AbstractManipulatorItem(), 1),
            # Power of ineratia decay (for an ease-out) 0 and 1 are linear
            'inertia_decay': (sc.AbstractManipulatorItem(), 1),
            # Acceleration and dampening values
            'tumble_acceleration': (sc.AbstractManipulatorItem(), (3, 1)),
            'look_acceleration': (sc.AbstractManipulatorItem(), (3, 1)),
            'move_acceleration': (sc.AbstractManipulatorItem(), (3, 1)),
            'fly_acceleration': (sc.AbstractManipulatorItem(), (3, 1)),
            'tumble_dampening': (sc.AbstractManipulatorItem(), (3, 1)),
            'look_dampening': (sc.AbstractManipulatorItem(), (3, 1)),
            'move_dampening': (sc.AbstractManipulatorItem(), (3, 1)),
            'fly_dampening': (sc.AbstractManipulatorItem(), (3, 1)),
            'fly_mode_lock_view': (sc.AbstractManipulatorItem(), 1),
            # Decimal precision of rotation operations
            'rotation_precision': (sc.AbstractManipulatorItem(), 1),
            # Mapping of units from input to world
            'ndc_scale': (sc.AbstractManipulatorItem(), 3),
            # Optional int-as-bool items
            'disable_pan': (sc.AbstractManipulatorItem(), 1),
            'disable_tumble': (sc.AbstractManipulatorItem(), 1),
            'disable_look': (sc.AbstractManipulatorItem(), 1),
            'disable_zoom': (sc.AbstractManipulatorItem(), 1),
            'disable_fly': (sc.AbstractManipulatorItem(), 1),
            'disable_undo': (sc.AbstractManipulatorItem(), 1),
            'object_centric_movement': (sc.AbstractManipulatorItem(), 1),
            'viewport_id': (sc.AbstractManipulatorItem(), 1),
            # USD specific concepts
            'up_axis': (sc.AbstractManipulatorItem(), 3),
            'current_aperture': (sc.AbstractManipulatorItem(), 2),
            'initial_aperture': (sc.AbstractManipulatorItem(), 2),
            'had_transform_at_key': (sc.AbstractManipulatorItem(), 1),
            'time': (sc.AbstractManipulatorItem(), 1),
            # Internal signal for final application of the changes, use disable_undo for user-control
            'interaction_ended': (sc.AbstractManipulatorItem(), 1), # Signal that undo should be applied
            'interaction_active': (sc.AbstractManipulatorItem(), 1), # Signal that a gesture is manipualting camera
            'interaction_animating': (sc.AbstractManipulatorItem(), 1), # Signal that an animation is manipulating camera
            'center_of_interest_start': (sc.AbstractManipulatorItem(), 3),
            'center_of_interest_picked': (sc.AbstractManipulatorItem(), 3),
            'adjust_center_of_interest': (sc.AbstractManipulatorItem(), 1),
            'initial_transform': (sc.AbstractManipulatorItem(), 16),
        }
        self.__values = {item: [] for item, _ in self.__items.values()}

        self.__values[self.__items.get('look_speed')[0]] = [1, 0.5]
        self.__values[self.__items.get('fly_speed')[0]] = [1]
        self.__values[self.__items.get('inertia_seconds')[0]] = [0.5]
        self.__values[self.__items.get('inertia_enabled')[0]] = [0]
        # self.__values[self.__items.get('interaction_active')[0]] = [0]
        # self.__values[self.__items.get('interaction_animating')[0]] = [0]
        self.__settings_changed_subs = []

        def read_inertia_setting(mode: str, setting_scale: float):
            global_speed_key = f'/persistent/exts/omni.kit.manipulator.camera/{mode}Speed'
            subscribe = self.__settings.subscribe_to_tree_change_events
            self.__settings_changed_subs.append(
                subscribe(global_speed_key,
                          lambda *args, **kwargs: self.__speed_setting_changed(*args, **kwargs,
                                                                               mode=mode, setting_scale=setting_scale)),
            )
            self.__speed_setting_changed(None, None, carb.settings.ChangeEventType.CHANGED, mode, setting_scale)

            accel = self.__settings.get(f'/exts/omni.kit.manipulator.camera/{mode}Acceleration')
            damp = self.__settings.get(f'/exts/omni.kit.manipulator.camera/{mode}Dampening')
            if accel is None or damp is None:
                if accel is None and damp is not None:
                    pass
                elif damp is None and accel is not None:
                    pass
                return

            self.__values[self.__items.get(f'{mode}_acceleration')[0]] = [accel]
            self.__values[self.__items.get(f'{mode}_dampening')[0]] = [damp]

        read_inertia_setting('fly', 1)
        read_inertia_setting('look', 180)
        read_inertia_setting('move', 1)
        read_inertia_setting('tumble', 360)

        self.__settings_changed_subs.append(
            self.__settings.subscribe_to_node_change_events('/persistent/exts/omni.kit.manipulator.camera/flyViewLock',
                                                            self.__fly_mode_lock_view_changed)
        )
        self.__fly_mode_lock_view_changed(None, carb.settings.ChangeEventType.CHANGED)

        self.__animation_key = id(self)
        self.__flight_inertia_active = False
        self.__last_applied = None

        # Faster access for key-values looked up during animation
        self.__move = self.__items.get('move')[0]
        self.__tumble = self.__items.get('tumble')[0]
        self.__look = self.__items.get('look')[0]
        self.__fly = self.__items.get('fly')[0]
        self.__transform = self.__items.get('transform')[0]
        self.__projection = self.__items.get('projection')[0]
        self.__center_of_interest = self.__items.get('center_of_interest')[0]
        self.__adjust_center_of_interest = self.__items.get('adjust_center_of_interest')[0]
        self.__inertia_enabled = self.__items.get('inertia_enabled')[0]
        self.__inertia_seconds = self.__items.get('inertia_seconds')[0]

        self.__tumble_velocity = None
        self.__look_velocity = None
        self.__move_velocity = None
        self.__fly_velocity = None
        self.__intertia_state = None
        self.__anim_stream = None
        self.__anim_stopped = 0
        self.__mode = None

    def __speed_setting_changed(self, tree_item: carb.dictionary.Item, changed_item: carb.dictionary.Item,
                                event_type: carb.settings.ChangeEventType, mode: str, setting_scale: float = 1):
        if tree_item is None:
            speed = self.__settings.get(f'/persistent/exts/omni.kit.manipulator.camera/{mode}Speed')
        else:
            speed = tree_item.get_dict()

        if speed:
            if (not isinstance(speed, tuple)) and (not isinstance(speed, list)):
                speed = [speed]
            self.__values[self.__items.get(f'{mode}_speed')[0]] = [float(x) / setting_scale for x in speed]

    def __fly_mode_lock_view_changed(self, changed_item: carb.dictionary.Item, event_type: carb.settings.ChangeEventType):
        model_key = self.__items.get('fly_mode_lock_view')[0]
        setting_key = '/persistent/exts/omni.kit.manipulator.camera/flyViewLock'
        self.__values[model_key] = [self.__settings.get(setting_key)]

    def __del__(self):
        self.destroy()

    def destroy(self):
        self.__destroy_animation()
        if self.__settings and self.__settings_changed_subs:
            for subscription in self.__settings_changed_subs:
                self.__settings.unsubscribe_to_change_events(subscription)
            self.__settings_changed_subs = None
        self.__settings = None

    def __destroy_animation(self):
        if self.__anim_stream:
            self.__anim_stream.destroy()
            self.__anim_stream = None
            self.__mark_animating(0)

    def __validate_arguments(self, name: Union[str, sc.AbstractManipulatorItem],
                             values: Sequence[Union[int, float]] = None) -> sc.AbstractManipulatorItem:
        if isinstance(name, sc.AbstractManipulatorItem):
            return name
        item, expected_len = self.__items.get(name, (None, None))
        if item is None:
            raise KeyError(f"CameraManipulatorModel doesn't understand values of {name}")
        if values and (len(values) != expected_len):
            if (not isinstance(expected_len, tuple)) or (not len(values) in expected_len):
                raise ValueError(f"CameraManipulatorModel {name} takes {expected_len} values, got {len(values)}")
        return item

    def get_item(self, name: str) -> sc.AbstractManipulatorItem():
        return self.__items.get(name, (None, None))[0]

    def set_ints(self, item: Union[str, sc.AbstractManipulatorItem], values: Sequence[int]):
        item = self.__validate_arguments(item, values)
        self.__values[item] = values

    def set_floats(self, item: Union[str, sc.AbstractManipulatorItem], values: Sequence[int]):
        item = self.__validate_arguments(item, values)
        self.__values[item] = values

    def get_as_ints(self, item: Union[str, sc.AbstractManipulatorItem]) -> List[int]:
        item = self.__validate_arguments(item)
        return self.__values[item]

    def get_as_floats(self, item: Union[str, sc.AbstractManipulatorItem]) -> List[float]:
        item = self.__validate_arguments(item)
        return self.__values[item]

    @carb.profiler.profile
    def _item_changed(self, item: Union[str, sc.AbstractManipulatorItem], delta_time: float = None, alpha: float = None):
        # item == None is the signal to push all model values into a final matrix at 'transform'
        if item is not None:
            if not isinstance(item, sc.AbstractManipulatorItem):
                item = self.__items.get(item)
                item = item[0] if item else None
            # Either of these adjust the pixel-to-world mapping
            if item == self.__center_of_interest or item == self.__projection:
                self.calculate_pixel_to_world(Gf.Vec3d(self.get_as_floats(self.__center_of_interest)))
                super()._item_changed(item)
                return

        if self.__anim_stream and delta_time is None:
            # If this is the end of an interaction (mouse up), return and let animation/inertia continue as is.
            if _optional_int(self, 'interaction_ended', 0) or (self.__intertia_state is None):
                return
            # If inertia is active, look values should be passed through; so as camera is drifting the look-rotation
            # is still applied.  If there is no look applied, then inertia is killed for any other movement.
            look = self.get_as_floats(self.__look) if self.__flight_inertia_active else None
            if look:
                # Destroy the look-velocity correction; otherwise look wil lag as camera drifts through inertia
                self.__look_velocity = None
            else:
                self._kill_external_animation(False)
            return

        tumble, look, move, fly = None, None, None, None

        if item is None or item == self.__tumble:
            tumble = self.get_as_floats(self.__tumble)
            if tumble:
                tumble = Gf.Vec3d(*tumble)
                self.set_floats(self.__tumble, None)

        if item is None or item == self.__look:
            look = self.get_as_floats(self.__look)
            if look:
                look = Gf.Vec3d(*look)
                self.set_floats(self.__look, None)

        if item is None or item == self.__move:
            move = self.get_as_floats(self.__move)
            if move:
                move = Gf.Vec3d(*move)
                self.set_floats(self.__move, None)

        if item is None or item == self.__fly:
            fly = self.get_as_floats(self.__fly)
            if fly:
                fly = Gf.Vec3d(*fly)
                fly_speed = _optional_floats(self, 'fly_speed')
                if fly_speed:
                    if len(fly_speed) == 1:
                        fly_speed = Gf.Vec3d(fly_speed[0], fly_speed[0], fly_speed[0])
                    else:
                        fly_speed = Gf.Vec3d(*fly_speed)
                    # Flight speed is multiplied by 5 for VP-1 compatibility
                    fly = Gf.CompMult(fly, fly_speed * 5)

        self.__last_applied = ModelState(tumble, look, move, fly)
        if (delta_time is not None) or self.__last_applied.any_values():
            self._apply_state(self.__last_applied, delta_time, alpha)
        else:
            super()._item_changed(item)

    def calculate_pixel_to_world(self, pos):
        projection = Gf.Matrix4d(*self.get_as_floats(self.__projection))
        top_left, bot_right = self._calculate_pixel_to_world(pos, projection, projection.GetInverse())
        x = top_left[0] - bot_right[0]
        y = top_left[1] - bot_right[1]
        # For NDC-z we don't want to use the clip range which could be huge
        # So avergae the X-Y scales instead
        self.set_floats('ndc_scale', [x, y, (x + y) * 0.5])

    def _calculate_pixel_to_world(self, pos, projection, inv_projection):
        ndc = projection.Transform(pos)
        top_left = inv_projection.Transform(Gf.Vec3d(-1, -1, ndc[2]))
        bot_right = inv_projection.Transform(Gf.Vec3d(1, 1, ndc[2]))
        return (top_left, bot_right)

    def _set_animation_key(self, key: str):
        self.__animation_key = key

    def _start_external_events(self, flight_mode: bool = False):
        # If flight mode is already doing inertia, do nothing.
        # This is for the case where right-click for WASD navigation end with a mouse up and global inertia is enabled.
        if self.__flight_inertia_active and not flight_mode:
            return False

        # Quick check that inertia is enabled for any mode other than flight

        if not flight_mode:
            inertia_modes = self.__settings.get('/exts/omni.kit.manipulator.camera/inertiaModesEnabled')
            len_inertia_enabled = len(inertia_modes) if inertia_modes else 0
            if len_inertia_enabled == 0:
                return
            if len_inertia_enabled == 1:
                self.__inertia_modes = [inertia_modes[0], 0, 0, 0]
            elif len_inertia_enabled == 2:
                self.__inertia_modes = [inertia_modes[0], inertia_modes[1], 0, 0]
            elif len_inertia_enabled == 3:
                self.__inertia_modes = [inertia_modes[0], inertia_modes[1], inertia_modes[2], 0]
            else:
                self.__inertia_modes = inertia_modes
        else:
            self.__inertia_modes = [1, 0, 1, 0]

        # Setup the animation state
        self.__anim_stopped = 0
        self.__intertia_state = None
        self.__flight_inertia_active = flight_mode
        # Pull more infor from inertai settings fro what is to be created
        create_tumble = self.__inertia_modes[1]
        create_look = flight_mode or self.__inertia_modes[2]
        create_move = self.__inertia_modes[3]
        create_fly = flight_mode
        if self.__anim_stream:
            # Handle case where key was down, then lifted, then pushed again by recreating look_velocity / flight correction.
            create_tumble = create_tumble and not self.__tumble_velocity
            create_look = create_look and not self.__look_velocity
            create_move = create_move and not self.__move_velocity
            create_fly = False

        clamp_dt = self.__settings.get('/ext/omni.kit.manipulator.camera/clampUpdates') or 0.15
        if create_look:
            self.__look_velocity = Velocity.create(self, 'look', clamp_dt)
        if create_tumble:
            self.__tumble_velocity = Velocity.create(self, 'tumble', clamp_dt)
        if create_move:
            self.__move_velocity = Velocity.create(self, 'move', clamp_dt)
        if create_fly:
            self.__fly_velocity = Velocity.create(self, 'fly', clamp_dt)

        # If any velocities are valid, then setup an animation to apply it.
        if self.__tumble_velocity or self.__look_velocity or self.__move_velocity or self.__fly_velocity:
            # Only set up the animation in flight-mode, let _stop_external_events set it up otherwise
            if flight_mode and not self.__anim_stream:
                self.__anim_stream = AnimationEventStream.get_instance()
                self.__anim_stream.add_animation(self._apply_state_tick, self.__animation_key)
            return True

        if self.__anim_stream:
            anim_stream, self.__anim_stream = self.__anim_stream, None
            anim_stream.destroy()
        return False

    def _stop_external_events(self, flight_mode: bool = False):
        # Setup animation for inertia in non-flight mode
        if not flight_mode and not self.__anim_stream:
            tumble, look, move = None, None, None
            if self.__last_applied and (self.__tumble_velocity or self.__look_velocity or self.__move_velocity or self.__fly_velocity):
                if self.__tumble_velocity and self.__inertia_modes[1]:
                    tumble = self.__last_applied.tumble
                if self.__look_velocity and self.__inertia_modes[2]:
                    look = self.__last_applied.look
                if self.__move_velocity and self.__inertia_modes[3]:
                    move = self.__last_applied.move
            if tumble or look or move:
                self.__last_applied = ModelState(tumble, look, move, self.__last_applied.fly)
                self.__anim_stream = AnimationEventStream.get_instance()
                self.__anim_stream.add_animation(self._apply_state_tick, self.__animation_key)
            else:
                self.__tumble_velocity = None
                self.__look_velocity = None
                self.__move_velocity = None
                self.__fly_velocity = None
                self.__intertia_state = None
                return

        self.__anim_stopped = time.monotonic()
        self.__intertia_state = self.__last_applied
        self.__mark_animating(1)

    def __mark_animating(self, interaction_animating: int):
        item, _ = self.__items.get('interaction_animating', (None, None))
        self.set_ints(item, [interaction_animating])
        super()._item_changed(item)

    def _apply_state_time(self, dt: float, apply_fn: Callable):
        alpha = 1
        if self.__anim_stopped:
            now = time.monotonic()
            inertia_enabled = _optional_int(self, 'inertia_enabled', 0)
            inertia_seconds = _optional_float(self, 'inertia_seconds', 0)
            if inertia_enabled and inertia_seconds > 0:
                alpha = 1.0 - ((now - self.__anim_stopped) / inertia_seconds)
                if alpha > ALMOST_ZERO:
                    decay = self.__settings.get('/exts/omni.kit.manipulator.camera/inertiaDecay')
                    decay = _optional_int(self, 'inertia_decay', decay)
                    alpha = pow(alpha, decay) if decay else 1
                else:
                    alpha = 0
            else:
                alpha = 0

        if alpha == 0:
            if self.__anim_stream:
                anim_stream, self.__anim_stream = self.__anim_stream, None
                anim_stream.destroy()
            self.set_ints('interaction_ended', [1])

        apply_fn(dt * alpha, 1)

        if alpha == 0:
            self.set_ints('interaction_ended', [0])
            self.__mark_animating(0)
            self.__tumble_velocity = None
            self.__look_velocity = None
            self.__move_velocity = None
            self.__fly_velocity = None
            self.__intertia_state = None
            self.__flight_inertia_active = False
            return False
        return True

    def _apply_state_tick(self, dt: float = None):
        keep_anim = True
        istate = self.__intertia_state
        if istate:
            if self.__flight_inertia_active:
                # See _item_changed, but during an inertia move, look should still be applied (but without any velocity)
                look = self.get_as_floats(self.__look)
                if look:
                    self.set_floats(self.__look, None)
                state = ModelState(None, look, None, istate.fly)
            else:
                tumble = (self.get_as_floats(self.__tumble) or istate.tumble) if self.__inertia_modes[1] else None
                look = (self.get_as_floats(self.__look) or istate.look) if self.__inertia_modes[2] else None
                move = (self.get_as_floats(self.__move) or istate.move) if self.__inertia_modes[3] else None
                state = ModelState(tumble, look, move)
            keep_anim = self._apply_state_time(dt, lambda dt, alpha: self._apply_state(state, dt, alpha))
        else:
            keep_anim = self._apply_state_time(dt, lambda dt, alpha: self._item_changed(None, dt, alpha))

        if not keep_anim and self.__anim_stream:
            self.__destroy_animation()

    def _kill_external_animation(self, kill_stream: bool = True, initial_transform = None):
        if kill_stream:
            self.__destroy_animation()
            # self._stop_external_events()
        self.__tumble_velocity = None
        self.__look_velocity = None
        self.__move_velocity = None
        self.__fly_velocity = None
        self.__intertia_state = None
        self.__flight_inertia_active = False
        # Reset internal transform if provided
        if initial_transform:
            self.set_floats('transform', initial_transform)
            self.set_floats('initial_transform', initial_transform)

    @carb.profiler.profile
    def _apply_state(self, state: ModelState, dt: float = None, alpha: float = None):
        up_axis = _optional_floats(self, 'up_axis')
        rotation_precision = _optional_int(self, 'rotation_precision', 5)
        last_transform = Gf.Matrix4d(*self.get_as_floats(self.__transform))
        xforms = TransformAccumulator(last_transform)
        center_of_interest = None

        tumble = state.tumble
        if self.__tumble_velocity:
            tumble = self.__tumble_velocity.apply(tumble, dt, alpha)
        if tumble:
            center_of_interest = Gf.Vec3d(*self.get_as_floats(self.__center_of_interest))
            tumble = Gf.Vec3d(round(tumble[0], rotation_precision), round(tumble[1], rotation_precision), round(tumble[2], rotation_precision))
            final_xf = xforms.get_tumble(tumble, center_of_interest, up_axis)
        else:
            final_xf = Gf.Matrix4d(1)

        look = state.look
        if self.__look_velocity:
            look = self.__look_velocity.apply(look, dt, alpha)
        if look:
            look = Gf.Vec3d(round(look[0], rotation_precision), round(look[1], rotation_precision), round(look[2], rotation_precision))
            final_xf = final_xf * xforms.get_look(look, up_axis)

        move = state.move
        if self.__move_velocity:
            move = self.__move_velocity.apply(move, dt, alpha)
        if move:
            final_xf = xforms.get_translation(move) * final_xf
            adjust_coi = move[2] != 0
        else:
            adjust_coi = False

        fly = None if _optional_int(self, 'disable_fly', 0) else state.fly
        if self.__fly_velocity:
            fly = self.__fly_velocity.apply(fly, dt, alpha)
        if fly:
            if _optional_bool(self, 'fly_mode_lock_view', False):
                decomp_rot = last_transform.ExtractRotation().Decompose(Gf.Vec3d.ZAxis(), Gf.Vec3d.YAxis(), Gf.Vec3d.XAxis())
                rot_z = Gf.Rotation(Gf.Vec3d.ZAxis(), decomp_rot[0])
                rot_y = Gf.Rotation(Gf.Vec3d.YAxis(), decomp_rot[1])
                rot_x = Gf.Rotation(Gf.Vec3d.XAxis(), decomp_rot[2])

                last_transform_tr = Gf.Matrix4d().SetTranslate(last_transform.ExtractTranslation())
                last_transform_rt_0 = Gf.Matrix4d().SetRotate(rot_x)
                last_transform_rt_1 = Gf.Matrix4d().SetRotate(rot_y * rot_z)

                if up_axis[2]:
                    fly[1], fly[2] = -fly[2], fly[1]
                elif Gf.Dot(Gf.Vec3d.ZAxis(), last_transform.TransformDir((0, 0, 1))) < 0:
                    fly[1], fly[2] = -fly[1], -fly[2]

                flight_xf = xforms.get_translation(fly)
                last_transform = last_transform_rt_0 * flight_xf * last_transform_rt_1 * last_transform_tr
            else:
                final_xf = xforms.get_translation(fly) * final_xf

        transform = final_xf * last_transform

        # If zooming out in Z, adjust the center-of-interest and pixel-to-world in 'ndc_scale'
        self.set_ints(self.__adjust_center_of_interest, [adjust_coi])
        if adjust_coi:
            center_of_interest = center_of_interest or Gf.Vec3d(*self.get_as_floats(self.__center_of_interest))
            coi = Gf.Matrix4d(*self.get_as_floats('initial_transform')).Transform(center_of_interest)
            coi = transform.GetInverse().Transform(coi)
            self.calculate_pixel_to_world(coi)

        self.set_floats(self.__transform, _flatten_matrix(transform))
        super()._item_changed(self.__transform)

    def _broadcast_mode(self, mode: str):
        if mode == self.__mode:
            return
        viewport_id = _optional_int(self, 'viewport_id', None)
        if viewport_id is None:
            return

        # Send a signal that contains the viewport_id and mode (carb requires a homogenous array, so as strings)
        self.__settings.set("/exts/omni.kit.manipulator.camera/viewportMode", [str(viewport_id), mode])
        self.__mode = mode
