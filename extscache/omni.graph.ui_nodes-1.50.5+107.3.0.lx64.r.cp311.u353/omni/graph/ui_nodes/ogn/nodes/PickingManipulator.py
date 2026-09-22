# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["PickingManipulatorFactory"]

from typing import Any, List, Optional

import carb
import omni.kit.app
import omni.kit.commands
from omni.ui import scene as sc

EVENT_NAME = "omni.graph.picking"
CLICK_GESTURE_NAMES = ["Left Mouse Click", "Right Mouse Click", "Middle Mouse Click"]
PRESS_GESTURE_NAMES = ["Left Mouse Press", "Right Mouse Press", "Middle Mouse Press"]
SEQ_LIMIT = 128


class DoNotPrevent(sc.GestureManager):
    def can_be_prevented(self, gesture):
        return False


# Custom gesture that triggers a picking query on mouse press, and sends the result on both mouse press and end of click
class PickingGesture(sc.DragGesture):
    def __init__(self, viewport_api: Any, viewport_window_name: str, mouse_button: int):
        super().__init__(mouse_button=mouse_button, manager=DoNotPrevent())
        self._viewport_api = viewport_api
        self._viewport_window_name = viewport_window_name
        self._click_gesture_name = CLICK_GESTURE_NAMES[mouse_button]
        self._press_gesture_name = PRESS_GESTURE_NAMES[mouse_button]

        self._event_type = carb.events.type_from_string(EVENT_NAME)
        self._message_bus = omni.kit.app.get_app().get_message_bus_event_stream()

        # Sequence number for associating picking queries with gestures
        self._seq = 0

        # Bool to track whether the mouse button was initially pressed over the 3D viewport or not
        # (does not need to be an array like the rest since _query_completed does not need to check it)
        self._began = False

        # Sequence number indexed bools to control the following execution order cases for mouse click:
        # 1: on_began -> _query_completed -> on_ended
        # 2: on_began -> _query_completed -> on_changed (cancelled) -> on_ended
        # 3: on_began -> on_ended -> _query_completed
        # 4: on_began -> on_changed (cancelled) -> _query_completed -> on_ended
        # 5: on_began -> on_changed (cancelled) -> on_ended -> _query_completed
        self._ended = [False] * SEQ_LIMIT  # True if the mouse button has been released without moving the mouse
        self._cancelled = [False] * SEQ_LIMIT  # True if the mouse was moved while pressed, cancelling the click
        self._result_stored = [False] * SEQ_LIMIT  # True if the picking query has completed and stored its result

        # Sequence number indexed temporary buffers to hold the picking result
        self._picked_prim_path = [None] * SEQ_LIMIT
        self._world_space_pos = [None] * SEQ_LIMIT

    # Callback to request_query called when the picking query completes
    def _query_completed(self, seq: int, picked_prim_path: str, world_space_pos: Optional[List[float]], *args):
        # Handle mouse press:
        # Send the picked prim path and picked world position in an event payload
        # Include the viewport window name and gesture name to filter on the receiving end
        press_payload = {
            "viewport": self._viewport_window_name,
            "gesture": self._press_gesture_name,
            "path": picked_prim_path,
            "pos_x": world_space_pos[0] if world_space_pos else 0.0,
            "pos_y": world_space_pos[1] if world_space_pos else 0.0,
            "pos_z": world_space_pos[2] if world_space_pos else 0.0,
        }
        self._message_bus.push(self._event_type, payload=press_payload)

        # Handle cases for mouse click
        if self._cancelled[seq]:
            return

        if self._ended[seq]:
            # Case 3: Click has already ended and we were waiting on the query to complete, so send the payload now
            click_payload = {
                "viewport": self._viewport_window_name,
                "gesture": self._click_gesture_name,
                "path": picked_prim_path,
                "pos_x": world_space_pos[0] if world_space_pos else 0.0,
                "pos_y": world_space_pos[1] if world_space_pos else 0.0,
                "pos_z": world_space_pos[2] if world_space_pos else 0.0,
            }
            self._message_bus.push(self._event_type, payload=click_payload)
        else:
            # Case 1 or 2: Click has not completed yet, so save the picking result and wait until mouse is released
            self._picked_prim_path[seq] = picked_prim_path
            self._world_space_pos[seq] = world_space_pos
            self._result_stored[seq] = True

    def _query_completed_seq(self, seq: int):
        return lambda *args: self._query_completed(seq, *args)

    # Called when the specified mouse button is pressed
    def on_began(self):
        # Get the next sequence number and reset the control bools
        self._seq = (self._seq + 1) % SEQ_LIMIT
        self._began = False
        self._ended[self._seq] = False
        self._cancelled[self._seq] = False
        self._result_stored[self._seq] = False
        self._picked_prim_path[self._seq] = None
        self._world_space_pos[self._seq] = None

        # Get the mouse position in normalized coords and check if the mouse is actually over the 3D viewport
        mouse = self.sender.gesture_payload.mouse
        resolution = self._viewport_api.resolution
        pos_norm, _ = self._viewport_api.map_ndc_to_texture(mouse)
        if pos_norm is None or not all(0.0 <= x <= 1.0 for x in pos_norm):
            return

        self._began = True

        # Get the mouse position in viewport resolution pixels and request a picking query
        pos_pixel = (int(pos_norm[0] * resolution[0]), int((1.0 - pos_norm[1]) * resolution[1]))
        self._viewport_api.request_query(
            pos_pixel,
            self._query_completed_seq(self._seq),
            query_name=f"omni.graph.ui_nodes.PickingManipulator.{id(self)}",
        )

    # Called when the mouse is moved while pressed, cancelling the click
    def on_changed(self):
        if not self._began:
            return

        self._cancelled[self._seq] = True

    # Called when the specified mouse button is released
    def on_ended(self):
        if not self._began or self._cancelled[self._seq]:
            return

        if self._result_stored[self._seq]:
            # Case 1: The picking query has already completed and we have the result saved, so send the payload now
            picked_prim_path = self._picked_prim_path[self._seq]
            world_space_pos = self._world_space_pos[self._seq]
            click_payload = {
                "viewport": self._viewport_window_name,
                "gesture": self._click_gesture_name,
                "path": picked_prim_path,
                "pos_x": world_space_pos[0] if world_space_pos else 0.0,
                "pos_y": world_space_pos[1] if world_space_pos else 0.0,
                "pos_z": world_space_pos[2] if world_space_pos else 0.0,
            }
            self._message_bus.push(self._event_type, payload=click_payload)
        else:
            # Case 3: The picking query has not completed yet, so wait until it completes to send the payload
            self._ended[self._seq] = True


# Custom manipulator containing a screen that contains the gestures
class PickingManipulator(sc.Manipulator):
    def __init__(self, viewport_api: Any, viewport_window_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._gestures = [
            PickingGesture(viewport_api, viewport_window_name, 0),  # left mouse click/press
            PickingGesture(viewport_api, viewport_window_name, 1),  # right mouse click/press
            PickingGesture(viewport_api, viewport_window_name, 2),  # middle mouse click/press
        ]
        self._screen = None
        self._transform = None
        self.name = None
        self.categories = ()

    def on_build(self):
        # Create a transform and put a screen in it (must hold a reference to keep the sc.Screen alive)
        self._transform = sc.Transform()
        with self._transform:
            # sc.Screen is an invisible rectangle that is always in front of and entirely covers the viewport camera
            # By attaching the gestures to this screen, the gestures can be triggered by clicking anywhere
            self._screen = sc.Screen(gesture=self._gestures)

    def destroy(self):
        self._gestures = []
        self._screen = None
        if self._transform:
            self._transform.clear()
            self._transform = None


# Factory creator
def PickingManipulatorFactory(desc: dict) -> PickingManipulator:  # noqa: N802
    manip = PickingManipulator(desc.get("viewport_api"), desc.get("viewport_window_name"))
    manip.categories = ()
    manip.name = f"PickingManipulator.{desc.get('viewport_window_name')}"
    return manip
