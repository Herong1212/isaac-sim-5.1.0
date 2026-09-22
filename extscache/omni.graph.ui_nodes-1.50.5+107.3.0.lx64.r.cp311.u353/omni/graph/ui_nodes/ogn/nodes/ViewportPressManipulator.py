# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["ViewportPressManipulatorFactory"]

from typing import Any

import carb
import omni.kit.app
import omni.kit.commands
from omni.ui import scene as sc

EVENT_NAME_BEGAN = "omni.graph.viewport.press.began"
EVENT_NAME_ENDED = "omni.graph.viewport.press.ended"
GESTURE_NAMES = ["Left Mouse Press", "Right Mouse Press", "Middle Mouse Press"]


class DoNotPrevent(sc.GestureManager):
    def can_be_prevented(self, gesture):
        return False


class ViewportPressGesture(sc.DragGesture):
    def __init__(self, viewport_api: Any, viewport_window_name: str, mouse_button: int):
        super().__init__(mouse_button=mouse_button, manager=DoNotPrevent())
        self._viewport_api = viewport_api
        self._viewport_window_name = viewport_window_name
        self._gesture_name = GESTURE_NAMES[mouse_button]

        self._event_type_began = carb.events.type_from_string(EVENT_NAME_BEGAN)
        self._event_type_ended = carb.events.type_from_string(EVENT_NAME_ENDED)
        self._message_bus = omni.kit.app.get_app().get_message_bus_event_stream()

        self._start_pos_valid = False

    def on_began(self):
        mouse = self.sender.gesture_payload.mouse
        resolution = self._viewport_api.resolution

        # Position in normalized coords
        pos_norm = self._viewport_api.map_ndc_to_texture(mouse)[0]
        pos_norm = (pos_norm[0], 1.0 - pos_norm[1])
        if not all(0.0 <= x <= 1.0 for x in pos_norm):
            self._start_pos_valid = False
            return

        # Position in viewport resolution pixels
        pos_pixel = (pos_norm[0] * resolution[0], pos_norm[1] * resolution[1])

        payload = {
            "viewport": self._viewport_window_name,
            "gesture": self._gesture_name,
            "pos_norm_x": pos_norm[0],
            "pos_norm_y": pos_norm[1],
            "pos_pixel_x": pos_pixel[0],
            "pos_pixel_y": pos_pixel[1],
        }
        self._message_bus.push(self._event_type_began, payload=payload)

        self._start_pos_valid = True

    def on_ended(self):
        if not self._start_pos_valid:
            return

        mouse = self.sender.gesture_payload.mouse
        resolution = self._viewport_api.resolution

        # Position in normalized coords
        pos_norm = self._viewport_api.map_ndc_to_texture(mouse)[0]
        pos_norm = (pos_norm[0], 1.0 - pos_norm[1])
        pos_valid = True
        if not all(0.0 <= x <= 1.0 for x in pos_norm):
            pos_valid = False
            pos_norm = [0.0, 0.0]

        # Position in viewport resolution pixels
        pos_pixel = (pos_norm[0] * resolution[0], pos_norm[1] * resolution[1])

        payload = {
            "viewport": self._viewport_window_name,
            "gesture": self._gesture_name,
            "pos_norm_x": pos_norm[0],
            "pos_norm_y": pos_norm[1],
            "pos_pixel_x": pos_pixel[0],
            "pos_pixel_y": pos_pixel[1],
            "pos_valid": pos_valid,
        }
        self._message_bus.push(self._event_type_ended, payload=payload)

        self._start_pos_valid = False


# Custom manipulator containing a Screen that contains the gestures
class ViewportPressManipulator(sc.Manipulator):
    def __init__(self, viewport_api: Any, viewport_window_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._gestures = [
            ViewportPressGesture(viewport_api, viewport_window_name, 0),  # left mouse press
            ViewportPressGesture(viewport_api, viewport_window_name, 1),  # right mouse press
            ViewportPressGesture(viewport_api, viewport_window_name, 2),  # middle mouse press
        ]
        self._screen = None
        self._transform = None
        self.name = None
        self.categories = ()

    def on_build(self):
        self._transform = sc.Transform()
        with self._transform:
            self._screen = sc.Screen(gesture=self._gestures)

    def destroy(self):
        self._gestures = []
        self._screen = None
        if self._transform:
            self._transform.clear()
            self._transform = None


# Factory creator
def ViewportPressManipulatorFactory(desc: dict) -> ViewportPressManipulator:  # noqa: N802
    manip = ViewportPressManipulator(desc.get("viewport_api"), desc.get("viewport_window_name"))
    manip.categories = ()
    manip.name = f"ViewportPressManipulator.{desc.get('viewport_window_name')}"
    return manip
