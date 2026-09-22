# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

# =================================== NOTE ====================================
# The APIs in this file are unfinished and may change in future releases
# Using these is at your own risk, and forward-compatability is not supported

import math
from typing import Optional

import carb
import omni.kit.commands
from omni.kit.xr.core import (
    XRCore,
    XREventGenerator,
    XRInputDeviceGeneratorEvent,
    XRSelectionBeam,
    XRSelectionEvent,
    XRToolComponentBase,
    XRTooltip,
    XRTransformType,
    XRUsdLayer,
)
from pxr import Gf

XR_USER_HAND_LEFT: str = "/user/hand/left"
XR_USER_HAND_RIGHT: str = "/user/hand/right"

XR_GUI_LAYER_GROUP: str = "move_tool"
XR_GUI_LAYER: str = "controllers"

XR_ROTATE_DEGREES: int = 30

XR_JOYSTICK_ACTIVE_THRESHOLD: float = 0.5
XR_JOYSTICK_INACTIVE_THRESHOLD: float = 0.4

MAX_MOVE_MULTIPLIER: float = 0.05


# The internal state of the move tool
class XRMoveToolState:

    def __init__(self):
        # When the remote grab (move) is activated, we need to capture a button/thumbstick/trackpad to allow
        # the user to make modifications. To temporarily override an input component of a controller we create
        # an event generator that overrides whatever button is specified in the actionmap
        # This field holds the subscription to that input eventgenerator
        self.manipulator_sub: Optional[XREventGenerator] = None

        # Last event from the manipulator button
        self.last_event: Optional[XRInputDeviceGeneratorEvent] = None

        # The application needs to record the location of the prim before the manipulation.
        self.pre_grab_transform: Optional[Gf.Matrix4d] = None

        # Which layer to make the final edit on (not the intermediate visual feedback)
        self.suggested_edit_layer: Optional[str] = None

        # Which prim is grabbed
        self.grabbed_prim: Optional[str] = None

        # Whether the prim is already on the suggested edit layer, if not undo will remove the prim spec from that layer
        self.prim_on_suggested_edit_layer: bool = False


class XRMoveTool(XRToolComponentBase):

    def __init__(self):
        # Initialize parent class
        super().__init__("move")

        # Define tooltips that show up when the move tool is active
        self.get_tooltip_manager().define_tooltip("move_manipulate_object_rotate", XRTooltip(text="Rotate object"))
        self.get_tooltip_manager().define_tooltip("move_manipulate_object_distance", XRTooltip(text="Adjust distance"))

        self.__state: dict[str, XRMoveToolState] = {}
        self.__state[XR_USER_HAND_LEFT] = XRMoveToolState()
        self.__state[XR_USER_HAND_RIGHT] = XRMoveToolState()

        # Check if the tool already needs to be enabled (hot reload)
        self.run_enable_if_enabled()

    def on_enable(self) -> None:
        """
        This function is called when the tool is enabled.
        """

        # The usd layer in which to insert the prims that
        # help moving prim
        self.__usd_layer: XRUsdLayer = self.get_usd_layer(XR_GUI_LAYER)

        # Define which events need to be listened to and which events
        # need to be generated.

        # The register_message_bus_event_handler functions are safe in regards to having a
        # reference to self and inspect the function signature to see how the callback
        # should be bound.
        # Event generators need to be bound that generate the events. In this case an
        # event generator is bound to the global stage scope, if it receives a press or
        # release call the callback can check the button pressed in conjunction with
        # the selection beam and filter out events.
        # When grab button is pressed, we allow the object to be moved (that is what
        # this tool does).

        # Note: this does not yet bind the event generators for xr_left_select_move and xr_right_select_move
        # those are created when the remote grab starts and are released when it ends.
        self.__subs = [
            self.register_message_bus_event_handler("xr_left_select_move.state", self.move),
            self.register_message_bus_event_handler("xr_right_select_move.state", self.move),
            self.register_message_bus_event_handler("xr_move.press", self.start_move),
            self.register_message_bus_event_handler("xr_move.release", self.end_move),
            self.bind_selection_event_generator("xr_move", ("press", "release"), "/", 5),
        ]

    def on_disable(self) -> None:
        """
        This function is called when the tool is disabled.
        """

        # remove all subscribe event handlers and event generators
        self.__usd_layer = None
        self.__subs = []

    def move(self, event: XRInputDeviceGeneratorEvent) -> None:
        """
        Callback called from the manipulator button
        """

        # Do the actual manipulation in preview (not as an action yet, but visible to the user)

        hand: str = event.input_device
        beam: Optional[XRSelectionBeam] = self.get_selection_manager().get_beam(hand)

        # Check if the beam is currently in remote grab mode
        if (beam is None) or (beam.is_active() is False) or (not beam.check_button_is_pressed("grab")):
            return

        # If this is the first in a series, record previous state and start manipulation on the
        # next frame.
        if self.__state[hand].last_event is None:
            self.__state[hand].last_event = event
            return

        # Record and retrieve last event
        last_event = self.__state[hand].last_event
        self.__state[hand].last_event = event

        # Try to figure out how the prim is manipulated
        if (
            math.fabs(last_event.x) > XR_JOYSTICK_ACTIVE_THRESHOLD
            and math.fabs(last_event.y) < XR_JOYSTICK_INACTIVE_THRESHOLD
        ):
            # Rotation

            turn_table_path: Optional[str] = beam.get_turn_table_path()
            if turn_table_path is None:
                return

            transform = self.__usd_layer.get_transform(turn_table_path)

            # If it is a trackpad the button must be pressed to left or right, for a thumbstick
            # it does not need to be pressed, just pushed left or right

            if event.input == "trackpad":
                # Version for trackpad
                if event.click == 0 and last_event.x < -XR_JOYSTICK_ACTIVE_THRESHOLD and last_event.click == 1.0:
                    # Rotate left
                    transform = Gf.Matrix4d().SetRotate(Gf.Rotation(Gf.Vec3d.YAxis(), -XR_ROTATE_DEGREES)) * transform
                    self.__usd_layer.set_transform(turn_table_path, transform)
                    return
                elif event.click == 0 and last_event.x > XR_JOYSTICK_ACTIVE_THRESHOLD and last_event.click == 1.0:
                    # Rotate right
                    transform = Gf.Matrix4d().SetRotate(Gf.Rotation(Gf.Vec3d.YAxis(), XR_ROTATE_DEGREES)) * transform
                    self.__usd_layer.set_transform(turn_table_path, transform)
                    return

            elif event.input == "thumbstick":
                # Version for thumbstick
                if event.x >= -XR_JOYSTICK_ACTIVE_THRESHOLD and last_event.x < -XR_JOYSTICK_ACTIVE_THRESHOLD:
                    # Rotate left
                    transform = Gf.Matrix4d().SetRotate(Gf.Rotation(Gf.Vec3d.YAxis(), -XR_ROTATE_DEGREES)) * transform
                    self.__usd_layer.set_transform(turn_table_path, transform)
                    return
                elif event.x <= XR_JOYSTICK_ACTIVE_THRESHOLD and last_event.x > XR_JOYSTICK_ACTIVE_THRESHOLD:
                    # Rotate right
                    transform = Gf.Matrix4d().SetRotate(Gf.Rotation(Gf.Vec3d.YAxis(), XR_ROTATE_DEGREES)) * transform
                    self.__usd_layer.set_transform(turn_table_path, transform)
                    return
            else:
                carb.log_error("move was bound to a button that is not a trackpad or a thumbstick")

        if math.fabs(event.y) > XR_JOYSTICK_ACTIVE_THRESHOLD and math.fabs(event.x) < XR_JOYSTICK_INACTIVE_THRESHOLD:
            # Up/down movement to get object closer/further
            change_factor = 1 + MAX_MOVE_MULTIPLIER * (
                (event.y + XR_JOYSTICK_ACTIVE_THRESHOLD) if event.y < 0 else (event.y - XR_JOYSTICK_ACTIVE_THRESHOLD)
            )

            # Need to change the length of the beam
            length = beam.get_length()
            beam.set_length(length * change_factor)
            return

    def start_move(self, ev: XRSelectionEvent) -> None:
        """
        This function is called when move through selection beam is started.
        """

        # This event handler is listening at global scope in the stage and hence
        # gets all events not handled by other event handlers.

        # Check if it is a grab event, i.e. the grab button is pressed
        if ev.button_changed != "grab":
            return

        # Retrieve the beam that triggered the event
        beam: Optional[XRSelectionBeam] = self.get_selection_manager().get_beam(ev.hand)

        if not beam.is_active():
            return

        target_usd_path: str = ev.enclosing_model

        # If the object is the entire stage or it is not grabbable, consume the event
        # but do not bind the manipulator tools
        if target_usd_path == "/" or not self.__usd_layer.is_grabbable(target_usd_path):
            ev.consume()
            return

        # If we are trying to move the object that we are bound to or a child of that
        # object, first detach the navigation from that object to avoid moving an object
        # we are indirectly tied to.
        anchor_path: Optional[str] = self.get_xr_core().get_stage_anchor_prim_path()
        if anchor_path is not None and anchor_path.startswith(target_usd_path):
            self.get_xr_core().detach_stage_anchor()

        self.grab_info_to_make_undo(ev.hand, target_usd_path)

        # Create a turn table at the end of the beam. The object will be bound to the
        # end of the beam and the turn_table allows for rotating the object.
        beam.create_turn_table_and_link(target_usd_path)

        # Get the length of the beam and explicitly set the length of beam
        # This ensures the object will stay at the given length (normally the beam length scales to the nearest object)
        length: float = beam.get_length()
        beam.set_length(length)

        # Create a new event generator that temporarily overrides the function
        # of the assigned button. This generator well stay until the subscription is cleared
        # resulting in reenabling of the originally bound event generator.
        self.__state[ev.hand].manipulator_sub = self.bind_input_event_generator(
            "xr_left_select_move" if beam.get_hand() == XR_USER_HAND_LEFT else "xr_right_select_move",
            ("state", "suspend"),
            {
                "tooltip_left_right": "move_manipulate_object_rotate",
                "tooltip_up_down": "move_manipulate_object_distance",
            },
        )

        self.get_selection_manager().set_selection(target_usd_path)

        # Consume the event so the lower priority bound functions are not executed
        ev.consume()

    def end_move(self, ev: XRSelectionEvent) -> None:
        """
        This function is called when the grab button is released.
        """

        # Filter out events that we need to handle
        if ev.button_changed != "grab":
            return

        if self.__state[ev.hand].grabbed_prim is None:
            return

        # Get the beam so we can uncouple it from the remotely grabbed object
        beam: Optional[XRSelectionBeam] = self.get_selection_manager().get_beam(ev.hand)

        # reset beam so it has no fixed length and points to nearest object
        beam.set_length(-1.0)

        if beam is not None and self.__state[ev.hand].grabbed_prim is not None:

            # Get the transform from the currently grabbed prim (preview)
            new_transform: Gf.Matrix4d = self.__usd_layer.get_transform(
                self.__state[ev.hand].grabbed_prim, XRTransformType.stage
            )

            # Execute the final edit in the suggested edit layer
            omni.kit.commands.execute(
                "XRTransformPrimCommand",
                prim_path=self.__state[ev.hand].grabbed_prim,
                layer_identifier=self.__state[ev.hand].suggested_edit_layer,
                new_transform=new_transform,
                old_transform=self.__state[ev.hand].pre_grab_transform,
                remove_from_layer=not self.__state[ev.hand].prim_on_suggested_edit_layer,
            )

            # Remove the link and let the object loose (it's new position was set by the execute of an action above)
            beam.remove_turn_table_and_link(commit=True)

        # Remove the event generator override and make sure that the previously assigned button is reassigned to the
        # previous task.
        self.__state[ev.hand].manipulator_sub = None

        # Clear out state for making an do/undo command
        self.clear_undo_info(ev.hand)

        # Consume the event so the lower priority bound functions are not executed
        ev.consume()

    def grab_info_to_make_undo(self, hand: str, grabbed_prim: str) -> None:

        xrcore: XRCore = self.get_xr_core()

        # In USDRT there are no layers and so the modifications we
        # make in moving the object can only be undone if we grab
        # the position before we start moving

        self.__state[hand].pre_grab_transform = xrcore.get_world_transform_matrix(grabbed_prim)
        self.__state[hand].grabbed_prim = grabbed_prim

        if xrcore.check_if_prim_transform_is_usdrt_only(grabbed_prim):
            self.__state[hand].suggested_edit_layer = None
        else:
            # This function will check if the prim is on the session layers, if so return that session layer
            # If it is in the main stage it will use what is in EditTarget, and if that is not a valid layer
            # it will default to the RootLayer of the stage for edits
            self.__state[hand].suggested_edit_layer = xrcore.suggest_edit_layer_for_prim(grabbed_prim)

        # Check if the prim is on the edit layer, if it is below that one, then undo will delete any edits on the
        # edit layer, otherwise it will revert to the original position on the edit layer
        self.__state[hand].prim_on_suggested_edit_layer = xrcore.check_if_prim_is_on_layer(
            grabbed_prim, self.__state[hand].suggested_edit_layer
        )

    def clear_undo_info(self, hand: str) -> None:
        """
        This function clears the state of do/undo
        """

        # Set them all back to None/False
        self.__state[hand].pre_grab_transform = None
        self.__state[hand].grabbed_prim = None
        self.__state[hand].suggested_edit_layer = None
        self.__state[hand].prim_on_suggested_edit_layer = False
