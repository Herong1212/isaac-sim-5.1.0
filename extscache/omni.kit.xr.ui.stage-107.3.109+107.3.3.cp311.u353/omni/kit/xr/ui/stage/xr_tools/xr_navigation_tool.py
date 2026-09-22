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

from omni.kit.xr.core import (
    XRCoordinateSystem,
    XRInputDevice,
    XRInputDeviceGeneratorEvent,
    XRToken,
    XRToolComponentBase,
    XRTooltip,
)
from pxr import Gf

XR_TOKEN_AIM = XRToken("aim")
XR_TOKEN_GRIP = XRToken("grip")

XR_NAVIGATION_VERT_MOVEMENT_ENABLED = "/xr/navigation/vertMovement/enabled"


class XRNavigationTool(XRToolComponentBase):

    def __init__(self):
        # Initialize parent class
        super().__init__("navigation")

        # Define the tooltips that describe what buttons do
        # Tooltips are defined in the tooltip manager and the tooltip display looks up the actual
        # description for each tooltip key.
        self.get_tooltip_manager().define_tooltip("navigate_rotate_left", XRTooltip(text="Rotate left"))
        self.get_tooltip_manager().define_tooltip("navigate_rotate_right", XRTooltip(text="Rotate right"))
        self.get_tooltip_manager().define_tooltip(
            "navigate_fly_up_down", XRTooltip(text=["Move Fwd/Back", "Move Up/Down (Hold Vertical)"])
        )
        self.get_tooltip_manager().define_tooltip("navigate_fly_left_right", XRTooltip(text="Move Left/Right"))
        self.get_tooltip_manager().define_tooltip("navigate_accelerate_fly", XRTooltip(text="Accelerate Fly"))

        # If tool is already enabled, trigger the enable function
        self.run_enable_if_enabled()

    def on_enable(self) -> None:
        """
        This function is called when the tool is enabled.
        """

        # Register callback points for events from input system
        # This list has two pieces:
        # event handlers: which functions to call when an event is generated
        # event generators: which components need to generate which events

        # To ensure we only generate events that we need the event generators need to
        # be bound explicitly.
        self.__subs = [
            self.register_message_bus_event_handler("xr_navigation_rotate_left.release", self.rotate_left),
            self.register_message_bus_event_handler("xr_navigation_rotate_right.release", self.rotate_right),
            self.register_message_bus_event_handler("xr_navigation_fly.state", self.fly),
            self.register_message_bus_event_handler("xr_navigation_fly_accelerate.update", self.fly_accelerate),
            self.register_message_bus_event_handler(
                "xr_navigation_fly_accelerate.suspend", self.fly_accelerate_suspend
            ),
            self.bind_input_event_generator(
                "xr_navigation_rotate_left", ("release"), {"tooltip_button": "navigate_rotate_left"}
            ),
            self.bind_input_event_generator(
                "xr_navigation_rotate_right", ("release"), {"tooltip_button": "navigate_rotate_right"}
            ),
            self.bind_input_event_generator(
                "xr_navigation_fly_accelerate", ("state", "suspend"), {"tooltip_button": "navigate_accelerate_fly"}
            ),
        ]

        # We need to inspect the fly_event_generator to see which controller it is bound to
        # hence add that one separately to the list
        fly_event_generator = self.bind_input_event_generator(
            "xr_navigation_fly",
            ("state"),
            {"tooltip_left_right": "navigate_fly_left_right", "tooltip_up_down": "navigate_fly_up_down"},
        )

        self.__subs.append(fly_event_generator)

        # Get the name of the controller that is connected to fly
        if fly_event_generator is not None:
            self.__fly_input_device_name = fly_event_generator.get_input_device_name()
        else:
            self.__fly_input_device_name = None

        # Find the navigation speed and ensure a default value is set
        self._navigation_speed_settings_path = (
            self.get_xr_core().get_current_profile().get_persistent_path() + "navigation/speed"
        )
        self.get_settings().set_default(self._navigation_speed_settings_path, 3.0)

        self._navigation_vert_movement_enabled_path = "/xr/navigation/vertMovement/enabled"
        self.get_settings().set_default(self._navigation_vert_movement_enabled_path, True)

        self.__accelerate: float = 1.0

    def on_disable(self) -> None:
        """
        This function is called when the tool is disabled.
        """

        # Remove all subscriptions:
        # This removes event handler/generators
        self.__subs = []
        self.__fly_input_device_name = None

    def rotate(self, amount: float) -> None:
        """
        This function is called to rotate the user by a certain amount

        Args:
            amount: rotation in degrees
        """

        # Convert to radians
        amount = amount * math.pi / 180.0

        # Between the anchor and the origin of the physical space is a transform
        # This function adjusts that transform to rotate the user by a certain amount
        self.get_xr_core().schedule_rotate_space_origin_relative_to_camera(yaw=amount, pitch=0)

    def rotate_left(self) -> None:
        """
        This function is called to rotate the user left.
        """
        self.rotate(30.0)

    def rotate_right(self) -> None:
        """
        This function is called to rotate the user right.
        """
        self.rotate(-30.0)

    def fly_accelerate(self, event) -> None:
        """
        This function is called when accelerate button is pressed.
        """

        # Currently disabled
        self.__accelerate = 1.0 + 2.0 * event.value

    def fly_accelerate_suspend(self) -> None:
        """
        This function is called when accelerate button is no longer assigned.
        In that case return to original speed, so user is not stuck with
        a high speed.
        """

        self.__accelerate = 1.0

    def fly(self, event: XRInputDeviceGeneratorEvent) -> None:
        """
        This function is called when the fly button is operated.
        """

        # Get the movement of the buttons
        move_horiz: float = event.dt * event.x
        move_vert: float = event.dt * event.y

        # Only do something if there is any motion
        if move_horiz != 0.0 or move_vert != 0.0:

            # Get the device the button is connected to
            input_device: Optional[XRInputDevice] = self.get_xr_core().get_input_device(self.__fly_input_device_name)

            # If there is no device, ignore flying for now
            if input_device is None:
                return

            # Get the aim pose if possible (this should have a level pose)
            if input_device.has_pose(XR_TOKEN_AIM):
                device_pose: Gf.Matrix4d = input_device.get_pose(XR_TOKEN_AIM)
            else:
                device_pose: Gf.Matrix4d = input_device.get_pose(XR_TOKEN_GRIP)

            # figure out how the controller is oriented as we use orientation
            # as another input

            # figure out what the forward vector is of the controller
            forward: Gf.Vec3d = device_pose.GetRow3(2)
            forward.Normalize()
            forward_up: float = forward[1]

            # Track which mode the controller up/down movement is
            move_up_down: bool = False
            move_down_up: bool = False
            move_back_forward: bool = False

            # Check if we assign button up_down/down_up or back/forward
            vert_move_limit: float = 0.8
            horiz_move_limit: float = 0.6

            vert_movement_enabled = self.get_settings().get_as_bool(self._navigation_vert_movement_enabled_path)

            if vert_movement_enabled:
                if forward_up < -vert_move_limit:
                    move_up_down = True
                elif forward_up > -horiz_move_limit and forward_up < horiz_move_limit:
                    move_back_forward = True
                elif forward_up > vert_move_limit:
                    move_down_up = True
            else:
                move_back_forward = True

            if move_up_down:
                velocity = Gf.Vec3d(move_horiz, move_vert, 0.0) * self.__accelerate
            elif move_back_forward:
                velocity = Gf.Vec3d(move_horiz, 0.0, -move_vert) * self.__accelerate
            elif move_down_up:
                velocity = Gf.Vec3d(move_horiz, -move_vert, 0.0) * self.__accelerate
            else:
                velocity = Gf.Vec3d(move_horiz, 0.0, 0.0) * self.__accelerate

            # We need the coordinate system to make speed stage scale invariant
            coordinate_system: XRCoordinateSystem = self.get_xr_core().get_coordinate_system()

            # Calculate current speed
            speed: float = (
                self.get_settings().get(self._navigation_speed_settings_path) / coordinate_system.meters_per_unit
            )

            # Update the transform between physical reference frame and the anchor.
            # So the anchor stays put and we move the user's reference frame relative
            # to the anchor. The speed is applied in the user's local sense of
            # left/right, up/down and forward/backward
            self.get_xr_core().schedule_move_space_origin_relative_to_camera(
                velocity[0] * speed, velocity[1] * speed, velocity[2] * speed
            )
