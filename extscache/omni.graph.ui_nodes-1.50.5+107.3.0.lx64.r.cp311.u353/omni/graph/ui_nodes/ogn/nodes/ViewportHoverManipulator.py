# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["ViewportHoverManipulatorFactory"]

from typing import Any

import carb
import omni.kit.app
import omni.kit.commands
from omni.ui import scene as sc

EVENT_NAME_BEGAN = "omni.graph.viewport.hover.began"
EVENT_NAME_CHANGED = "omni.graph.viewport.hover.changed"
EVENT_NAME_ENDED = "omni.graph.viewport.hover.ended"


class DoNotPrevent(sc.GestureManager):
    def can_be_prevented(self, gesture):
        return False


class ViewportHoverGesture(sc.HoverGesture):
    def __init__(self, viewport_api: Any, viewport_window_name: str):
        super().__init__(manager=DoNotPrevent())
        self._viewport_api = viewport_api
        self._viewport_window_name = viewport_window_name

        self._event_type_began = carb.events.type_from_string(EVENT_NAME_BEGAN)
        self._event_type_changed = carb.events.type_from_string(EVENT_NAME_CHANGED)
        self._event_type_ended = carb.events.type_from_string(EVENT_NAME_ENDED)
        self._message_bus = omni.kit.app.get_app().get_message_bus_event_stream()

        self._viewport_hovered = False

    def on_began(self):
        self._viewport_hovered = False

    def on_changed(self):
        mouse = self.sender.gesture_payload.mouse
        pos_norm = self._viewport_api.map_ndc_to_texture(mouse)[0]
        pos_norm = (pos_norm[0], 1.0 - pos_norm[1])

        viewport_hovered = all(0.0 <= x <= 1.0 for x in pos_norm)

        if not self._viewport_hovered and viewport_hovered:
            # hover began
            resolution = self._viewport_api.resolution
            pos_pixel = (pos_norm[0] * resolution[0], pos_norm[1] * resolution[1])
            payload = {
                "viewport": self._viewport_window_name,
                "pos_norm_x": pos_norm[0],
                "pos_norm_y": pos_norm[1],
                "pos_pixel_x": pos_pixel[0],
                "pos_pixel_y": pos_pixel[1],
            }
            self._message_bus.push(self._event_type_began, payload=payload)

        elif self._viewport_hovered and viewport_hovered:
            # hover changed
            resolution = self._viewport_api.resolution
            pos_pixel = (pos_norm[0] * resolution[0], pos_norm[1] * resolution[1])
            mouse_moved = self.sender.gesture_payload.mouse_moved
            vel_norm = self._viewport_api.map_ndc_to_texture(mouse_moved)[0]
            origin_norm = self._viewport_api.map_ndc_to_texture((0, 0))[0]
            vel_norm = (vel_norm[0] - origin_norm[0], origin_norm[1] - vel_norm[1])
            vel_pixel = (vel_norm[0] * resolution[0], vel_norm[1] * resolution[1])

            payload = {
                "viewport": self._viewport_window_name,
                "pos_norm_x": pos_norm[0],
                "pos_norm_y": pos_norm[1],
                "pos_pixel_x": pos_pixel[0],
                "pos_pixel_y": pos_pixel[1],
                "vel_norm_x": vel_norm[0],
                "vel_norm_y": vel_norm[1],
                "vel_pixel_x": vel_pixel[0],
                "vel_pixel_y": vel_pixel[1],
            }
            self._message_bus.push(self._event_type_changed, payload=payload)

        elif self._viewport_hovered and not viewport_hovered:
            # hover ended
            payload = {
                "viewport": self._viewport_window_name,
            }
            self._message_bus.push(self._event_type_ended, payload=payload)

        self._viewport_hovered = viewport_hovered

    def on_ended(self):
        if self._viewport_hovered:
            # hover ended
            payload = {
                "viewport": self._viewport_window_name,
            }
            self._message_bus.push(self._event_type_ended, payload=payload)

            self._viewport_hovered = False


# Custom manipulator containing a Screen that contains the gestures
class ViewportHoverManipulator(sc.Manipulator):
    def __init__(self, viewport_api: Any, viewport_window_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._gestures = [ViewportHoverGesture(viewport_api, viewport_window_name)]
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
def ViewportHoverManipulatorFactory(desc: dict) -> ViewportHoverManipulator:  # noqa: N802
    manip = ViewportHoverManipulator(desc.get("viewport_api"), desc.get("viewport_window_name"))
    manip.categories = ()
    manip.name = f"ViewportHoverManipulator.{desc.get('viewport_window_name')}"
    return manip
