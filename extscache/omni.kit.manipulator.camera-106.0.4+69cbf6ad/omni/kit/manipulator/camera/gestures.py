# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ['build_gestures', 'PanGesture', 'TumbleGesture', 'LookGesture', 'ZoomGesture']

from omni.ui import scene as sc
from .gesturebase import CameraGestureBase
from pxr import Gf
import carb
from typing import Callable

kDefaultKeyBindings = {
    'PanGesture': 'Any MiddleButton',
    'TumbleGesture': 'Alt LeftButton',
    'ZoomGesture': 'Alt RightButton',
    'LookGesture': 'RightButton'
}


def build_gestures(model: sc.AbstractManipulatorModel,
                   bindings: dict = None,
                   manager: sc.GestureManager = None,
                   configure_model: Callable = None):
    def _parse_binding(binding_str: str):
        keys = binding_str.split(' ')
        button = {
            'LeftButton': 0,
            'RightButton': 1,
            'MiddleButton': 2
        }.get(keys.pop())

        modifiers = 0
        for mod_str in keys:
            mod_bit = {
                'Shift': carb.input.KEYBOARD_MODIFIER_FLAG_SHIFT,
                'Ctrl': carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL,
                'Alt': carb.input.KEYBOARD_MODIFIER_FLAG_ALT,
                'Super': carb.input.KEYBOARD_MODIFIER_FLAG_SUPER,
                'Any': 0xffffffff,
            }.get(mod_str)
            if not mod_bit:
                raise RuntimeError(f'Unparseable binding: {binding_str}')
            modifiers = modifiers | mod_bit

        return (button, modifiers)

    if not bindings:
        bindings = kDefaultKeyBindings
    gestures = []
    for gesture, binding in bindings.items():
        instantiator = globals().get(gesture)
        if not instantiator:
            carb.log_warn(f'Gesture "{gesture}" was not found for key-binding: "{binding}"')
            continue
        button, modifers = _parse_binding(binding)
        gestures.append(instantiator(model, configure_model, mouse_button=button, modifiers=modifers, manager=manager))
    return gestures


class PanGesture(CameraGestureBase):
    def on_mouse_move(self, mouse_moved):
        if self.disable_pan:
            return

        world_speed = self.world_speed
        move_speed = self.move_speed
        self._accumulate_values('move', mouse_moved[0] * 0.5 * world_speed[0] * move_speed[0],
                                        mouse_moved[1] * 0.5 * world_speed[1] * move_speed[1],
                                        0)


class TumbleGesture(CameraGestureBase):
    def on_mouse_move(self, mouse_moved):
        if self.disable_tumble:
            return

        # Mouse moved is [-1,1], so make a full drag scross the viewport a 180 tumble
        speed = self.tumble_speed
        self._accumulate_values('tumble', mouse_moved[0] * speed[0] * -90,
                                          mouse_moved[1] * speed[1] * 90,
                                          0)

class LookGesture(CameraGestureBase):
    def on_mouse_move(self, mouse_moved):
        if self.disable_look:
            return

        # Mouse moved is [-1,1], so make a full drag scross the viewport a 180 look
        speed = self.look_speed
        self._accumulate_values('look', mouse_moved[0] * speed[0] * -90,
                                        mouse_moved[1] * speed[1] * 90,
                                        0)



class OrthoZoomAperture():
    def __init__(self, model: sc.AbstractManipulatorModel, apertures):
        self.__values = apertures.copy()

    def apply(self, model: sc.AbstractManipulatorModel, distance: float):
        # TODO ortho-speed
        for i in range(2):
            self.__values[i] -= distance * 2
        model.set_floats('current_aperture', self.__values)
        model._item_changed(model.get_item('current_aperture'))

    def dirty_items(self, model: sc.AbstractManipulatorModel):
        cur_ap = model.get_item('current_aperture')
        if model.get_as_floats('initial_aperture') != model.get_as_floats(cur_ap):
            return [cur_ap]


class OrthoZoomProjection():
    def __init__(self, model: sc.AbstractManipulatorModel, projection):
        self.__projection = projection.copy()

    def apply(self, model: sc.AbstractManipulatorModel, distance: float):
        # TODO ortho-speed
        distance /= 3.0
        rml = (2.0 / self.__projection[0])
        tmb = (2.0 / self.__projection[5])
        aspect = tmb / rml
        rpl = rml * -self.__projection[12]
        tpb = tmb * self.__projection[13]
        rml -= distance
        tmb -= distance * aspect
        rpl += distance
        tpb += distance
        self.__projection[0] = 2.0 / rml
        self.__projection[5] = 2.0 / tmb
        #self.__projection[12] = -rpl / rml
        #self.__projection[13] = tpb / tmb
        model.set_floats('projection', self.__projection)
        # Trigger recomputation of ndc_speed
        model._item_changed(model.get_item('projection'))

    def dirty_items(self, model: sc.AbstractManipulatorModel):
        proj = model.get_item('projection')
        return [proj]
        if model.get_as_floats('projection') != model.get_as_floats(proj):
            return [proj]


class ZoomGesture(CameraGestureBase):
    def dirty_items(self, model: sc.AbstractManipulatorModel):
        return super().dirty_items(model) if not self.__orth_zoom else self.__orth_zoom.dirty_items(model)

    def __setup_ortho_zoom(self):
        apertures = self.model.get_as_floats('initial_aperture')
        if apertures:
            self.__orth_zoom = OrthoZoomAperture(self.model, apertures)
            return True
        projection = self.model.get_as_floats('projection')
        if projection:
            self.__orth_zoom = OrthoZoomProjection(self.model, projection)
            return True

        carb.log_warn("Orthographic zoom needs a projection or aperture")
        return False

    def on_began(self, *args, **kwargs):
        super().on_began(*args, **kwargs)

        # Setup an orthographic movement (aperture adjustment) if needed
        self.__orth_zoom = False
        if self.orthographic:
            self.__setup_ortho_zoom()
        # self.model.set_ints('adjust_center_of_interest', [1])

        # Zoom into center of view or mouse interest
        self.__direction = Gf.Vec3d(self.center_of_interest.GetNormalized()) if False else None

    def on_mouse_move(self, mouse_moved):
        if self.disable_zoom:
            return

        # Compute length/radius from gesture start
        distance = (mouse_moved[0] + mouse_moved[1]) * self.world_speed.GetLength() * 1.41421356
        distance *= self.move_speed[2]

        if self.__orth_zoom:
            self.__orth_zoom.apply(self.model, distance)
            return

        # Zoom into view-enter or current mouse/world interest
        direction = self.__direction if self.__direction else Gf.Vec3d(self.center_of_interest.GetNormalized())

        amount = direction * distance
        self._accumulate_values('move', amount[0], amount[1], amount[2])
