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

from math import acos, cos, pi, sin
from typing import Iterable, Optional

import omni.kit.commands
from omni.kit.xr.core import (
    XRCore,
    XRInputDeviceGeneratorEvent,
    XRRay,
    XRRayQueryResult,
    XRSelectionManager,
    XRToolComponentBase,
    XRTooltip,
    XRTransformType,
    XRUsdLayer,
)
from pxr import Gf, Usd

XR_USER_HAND_LEFT: str = "/user/hand/left"
XR_USER_HAND_RIGHT: str = "/user/hand/right"
XR_GRAB_RANGE: float = 0.20  # meter
XR_GRAB_SAMPLE_DIRECTIONS: int = 64
XR_GRAB_TOOL_GROUP: str = "grab_tool"


# State of the tool per hand
class XRGrabToolState:

    def __init__(self):
        # Whether grab is active
        self.active: bool = False

        # Whether remote grab is active
        self.remote_grab_active: bool = False

        # The transform of the prim before grabbing
        self.pre_grab_transform: Optional[Gf.Matrix4d] = None

        # The layer to use for editing a grabbed object
        self.suggested_edit_layer: Optional[str] = None

        # The path to the object that is grabbed
        self.grabbed_prim: Optional[str] = None

        # Whether the prim has an opinion on the edit layer (for undo)
        self.prim_on_suggested_edit_layer: bool = False


class XRGrabTool(XRToolComponentBase):

    def __init__(self):
        # Initialize parent class with tool name
        super().__init__("grab")

        # Setup uniformly sampling directions for grabbing
        # This defines a spiral over a sphere and uses that to
        # compute a relatively uniform set of sampling directions
        # over a sphere

        golden_ratio: float = (1.0 + 5.0**0.5) / 2.0
        self.__sample_directions: list[float] = []

        # For more accuracy add more sample directions: this runs on the
        # GPU and should be fast. The sampling is on the RTCores
        for idx in range(0, XR_GRAB_SAMPLE_DIRECTIONS):
            phi = acos(1.0 - 2.0 * (idx + 0.5) / XR_GRAB_SAMPLE_DIRECTIONS)
            theta = 2.0 * pi * idx / golden_ratio
            self.__sample_directions.append((cos(theta) * sin(phi), sin(theta) * sin(phi), cos(phi)))

        # Keep track of whether grab is being used
        self.__state: dict[str, XRGrabToolState] = {}
        self.__state[XR_USER_HAND_LEFT] = XRGrabToolState()
        self.__state[XR_USER_HAND_RIGHT] = XRGrabToolState()

        # Define tooltips to be used
        self.get_tooltip_manager().define_tooltip("grab_object", XRTooltip(text="Grab object"))

        # If grab is already enabled, run enable
        # This function checks what is enabled (dynamic reloading) and triggers an enable if needed
        self.run_enable_if_enabled()

    def on_enable(self) -> None:
        """
        This function is called when the tool is enabled.
        """

        # We need a link to the controller model so grabbed objects are moved
        # when the controller moves. This looks up the managed usd layer
        # that we use for controllers.

        # A usd layer will be valid for the entirety of the tools life.
        # If a new stage gets loaded, all tools will disable and will be
        # enabled on the next stage, ensuring a new usd layer will be
        # made.
        self.__usd_layer: XRUsdLayer = self.get_usd_layer("controllers")

        # Register callback points and event generators
        # All event generators will post messages on the message bus and the
        # message bus callbacks will execute code.

        # The first set of subscriptions is to register what actions to perform
        # when an action is on the message bus.
        # The second set is to define how to map event generators to the controllers:
        # this defines the event that needs to be bound. The actual button it binds to
        # is in the action map.

        # As tools can temporarily overwrite buttons/joysticks we define event generators
        # that let is know what the current configuration is. A new event generator
        # can temporarily grab input until its subscription is released and it will default
        # back to the original subscription.

        # Each button can make multiple gestures like press, release, suspend and the
        # event generator decides which gestures to send. Each gesture is separately bound.

        self.__subs = [
            self.register_message_bus_event_handler("xr_left_grab.press", self.grab_press),
            self.register_message_bus_event_handler("xr_left_grab.release", self.grab_release),
            self.register_message_bus_event_handler("xr_left_grab.suspend", self.grab_suspend),
            self.register_message_bus_event_handler("xr_right_grab.press", self.grab_press),
            self.register_message_bus_event_handler("xr_right_grab.release", self.grab_release),
            self.register_message_bus_event_handler("xr_right_grab.suspend", self.grab_suspend),
            self.bind_input_event_generator(
                "xr_left_grab", ("press", "release", "suspend"), {"tooltip_button": "grab_object"}
            ),
            self.bind_input_event_generator(
                "xr_right_grab", ("press", "release", "suspend"), {"tooltip_button": "grab_object"}
            ),
        ]

        # Make UI not grabbable by default
        stage = omni.usd.get_context().get_stage()
        if stage is not None:
            with Usd.EditContext(stage, Usd.EditTarget(stage.GetSessionLayer())):
                self.__usd_layer.set_grabbable("/_xr", False)

    def on_disable(self) -> None:
        """
        This function is called when the tool is disabled.
        """

        # Remove all subscriptions
        self.__subs = []

        # Remove layer so we don't have a hold on it any more
        self.__usd_layer = None

    # Callback functions can bind predefined Event templates, which allows
    # the linter and autocomplete to see which fields are available

    def grab_press(self, event: XRInputDeviceGeneratorEvent) -> None:
        """
        This function is called when the grab button is pressed.
        """

        if self.__usd_layer and self.__usd_layer.is_valid():

            # The input device refers to the hand (input_device) initiating the callback
            hand: str = event.input_device

            # We send rays from the grip attachment point
            attachment_point_path: Optional[str] = self.__usd_layer.get_meta_data(hand + "/attachments/grip")
            if attachment_point_path is None:
                return

            # Get the location of the grip location in stage space
            attachment_point: Gf.Matrix4d = self.__usd_layer.get_transform(attachment_point_path, XRTransformType.stage)

            # Get the origin of the transform in world coordinates
            origin: Gf.Vec3d = attachment_point.ExtractTranslation()

            # define a series of rays to see which objects we hit
            rays: list[XRRay] = []
            tmax: float = XR_GRAB_RANGE / self.get_xr_core().get_coordinate_system().meters_per_unit

            # Deal with problems in the renderer and add a little offset
            origin[2] = origin[2] + 0.01

            for direction in self.__sample_directions:
                # add sample ray
                rays.append(XRRay(origin, direction, 0.0, tmax))

            def callback(rays: Iterable[XRRay], results: Iterable[XRRayQueryResult]):
                """
                Function called when ray cast completes
                """

                # If button was released before we could process the samples taken
                if not self.__state[hand].active:
                    return

                # Find closest hit and select that object
                closest = results[0]
                for result in results:
                    if result.valid and result.hit_t < closest.hit_t:
                        closest = result

                # find the closest enclosing model (one that we can move)
                usd_target_path: Optional[str] = closest.get_target_enclosing_model_usd_path()

                if usd_target_path is not None:
                    # Try again but now with slower version that also checks whether object can be grabbed
                    # if we hit a none grabbable object
                    if not self.__usd_layer.is_grabbable(usd_target_path):
                        usd_target_path = None
                        closest = XRRayQueryResult()
                        for result in results:
                            if result.valid and result.hit_t < closest.hit_t:
                                usd_target_path = result.get_target_enclosing_model_usd_path()
                                if usd_target_path is not None and self.__usd_layer.is_grabbable(usd_target_path):
                                    closest = result

                # Grab object if one was found
                if usd_target_path is not None and closest.valid:

                    # Check if we are trying to grab our own anchor or a prim below it
                    # if so detach the anchor and freeze anchor in the given location.s
                    # Grabbing an anchor that you are connected to would give you a weird feedback loop
                    anchor_path: Optional[str] = self.get_xr_core().get_stage_anchor_prim_path()
                    if anchor_path is not None and anchor_path.startswith(usd_target_path):
                        self.get_xr_core().detach_stage_anchor()

                    # Create link to object and link it under controller in its current location
                    link_path: str = self.__usd_layer.ensure_device_prim_path(hand) + "/link"

                    # Make grabbed object the selected object
                    self.get_selection_manager().set_selection(usd_target_path)

                    # Store information to make an undo
                    self.grab_info_to_make_undo(hand, usd_target_path)

                    # Link grabbed object to the controller
                    self.__usd_layer.add_link(link_path, link_path=usd_target_path, group=XR_GRAB_TOOL_GROUP)
                else:
                    # Dispatch a message to the selection manager that is
                    # is used by the move tool to do a remote manipulation

                    selection_manager = self.get_selection_manager()
                    selection_manager.dispatch_press(hand, "grab")
                    self.__state[hand].remote_grab_active = True

            # Submit sample rays to see what is being grabbed
            # The callback returns within 1 or 2 frames, as the ray casts use the rendering engine

            self.get_xr_core().submit_multi_raycast_query(rays, callback)
            self.__state[hand].active = True

    def grab_release(self, event: XRInputDeviceGeneratorEvent, commit: bool = True) -> None:
        """
        This function is called when the object is released.
        """

        hand: str = event.input_device
        self.__state[hand].active = False

        # Deal with remote grab
        if self.__state[hand].remote_grab_active:
            selection_manager: XRSelectionManager = self.get_selection_manager()
            selection_manager.dispatch_release(hand, "grab")
            self.__state[hand].remote_grab_active = False

        # Get path to linked object
        link_path = self.__usd_layer.ensure_device_prim_path(hand) + "/link"

        # Check if there is a managed object
        if self.__usd_layer.is_managed_prim(link_path):

            if commit and self.__state[hand].grabbed_prim is not None:
                new_transform: Gf.Matrix4d = self.__usd_layer.get_transform(
                    self.__state[hand].grabbed_prim, XRTransformType.stage
                )

                # Execute final undoable command
                omni.kit.commands.execute(
                    "XRTransformPrimCommand",
                    prim_path=self.__state[hand].grabbed_prim,
                    layer_identifier=self.__state[hand].suggested_edit_layer,
                    new_transform=new_transform,
                    old_transform=self.__state[hand].pre_grab_transform,
                    remove_from_layer=not self.__state[hand].prim_on_suggested_edit_layer,
                )

            # Remove linked object that hooked the object
            self.__usd_layer.remove(link_path)

        # Reset the undo information, so the state is cleared for the next grab
        self.clear_undo_info(hand)

    def grab_suspend(self, event: XRInputDeviceGeneratorEvent) -> None:
        """
        This function is called when the button gets overridden by another tool.
        Anything that is grabbed is released, to ensure it is not stuck in someone's
        hand.
        """
        self.grab_release(event, False)

    def grab_info_to_make_undo(self, hand: str, grabbed_prim: str) -> None:
        """
        This function collects information for do/undo in an xr grab.
        """
        xrcore: XRCore = self.get_xr_core()

        # In USDRT there are no layers and so the modifications we
        # make in moving the object can only be undone if we grab
        # the position before we start moving

        self.__state[hand].pre_grab_transform = xrcore.get_world_transform_matrix(grabbed_prim)
        self.__state[hand].grabbed_prim = grabbed_prim

        # Figure out which layer for editing the usd to use
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
