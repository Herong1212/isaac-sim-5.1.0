# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["ViewportScrollManipulatorFactory"]

from typing import Any

import carb
import omni.kit.app
import omni.kit.commands
from omni.ui import scene as sc

EVENT_NAME = "omni.graph.viewport.scroll"


class DoNotPrevent(sc.GestureManager):
    def can_be_prevented(self, gesture):
        return False


class ViewportScrollGesture(sc.ScrollGesture):
    def __init__(self, viewport_api: Any, viewport_window_name: str):
        super().__init__(manager=DoNotPrevent())
        self._viewport_api = viewport_api
        self._viewport_window_name = viewport_window_name

        self._event_type = carb.events.type_from_string(EVENT_NAME)
        self._message_bus = omni.kit.app.get_app().get_message_bus_event_stream()

    def on_ended(self, *args):
        mouse = self.sender.gesture_payload.mouse
        resolution = self._viewport_api.resolution

        # Position in normalized coords
        pos_norm = self._viewport_api.map_ndc_to_texture(mouse)[0]
        pos_norm = (pos_norm[0], 1.0 - pos_norm[1])
        if not all(0.0 <= x <= 1.0 for x in pos_norm):
            return

        # Position in viewport resolution pixels
        pos_pixel = (pos_norm[0] * resolution[0], pos_norm[1] * resolution[1])

        payload = {
            "viewport": self._viewport_window_name,
            "pos_norm_x": pos_norm[0],
            "pos_norm_y": pos_norm[1],
            "pos_pixel_x": pos_pixel[0],
            "pos_pixel_y": pos_pixel[1],
            "scroll": self.scroll[0],
        }
        self._message_bus.push(self._event_type, payload=payload)


class ViewportScrollManipulator(sc.Manipulator):
    def __init__(self, viewport_api: Any, viewport_window_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._gestures = [ViewportScrollGesture(viewport_api, viewport_window_name)]
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
def ViewportScrollManipulatorFactory(desc: dict) -> ViewportScrollManipulator:  # noqa: N802
    manip = ViewportScrollManipulator(desc.get("viewport_api"), desc.get("viewport_window_name"))
    manip.categories = ()
    manip.name = f"ViewportScrollManipulator.{desc.get('viewport_window_name')}"
    return manip
