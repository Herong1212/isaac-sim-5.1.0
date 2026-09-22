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

from dataclasses import dataclass
from typing import Optional

from omni.kit.xr.core import (
    XRAssetManager,
    XRCoordinateSystem,
    XRInputDevice,
    XRInputDeviceGeneratorEvent,
    XROrientationAlignment,
    XRSelectionBeam,
    XRToolComponentBase,
    XRTooltip,
    XRTransformType,
    XRUsdLayer,
)
from pxr import Gf

XR_USER_HAND_LEFT = "/user/hand/left"
XR_USER_HAND_RIGHT = "/user/hand/right"

XR_TELEPORT_FORWARD = "teleport_forward"
XR_TELEPORT_BACKWARD = "teleport_backward"

XR_TELEPORT_GUI_LAYER_GROUP = "teleport_tool"
XR_TELEPORT_GUI_LAYER = "controllers"

TELEPORT_COLINEAR_THRESHOLD = 0.85


@dataclass
class XRTeleporterBeam:
    beam_path: str = ""
    reorient_path: str = ""
    target_path: str = ""
    active: bool = False
    target_shown: bool = False
    vis_update: int = 0
    direction: str = ""


class XRTeleportTool(XRToolComponentBase):

    def __init__(self):

        # Initialize parent class with the name of the tool
        super().__init__("teleport")

        self.__marker_scale_offset_shown_backward = Gf.Matrix4d().SetTranslate(
            Gf.Vec3d(0, 10.0, 0)
        ) * Gf.Matrix4d().SetDiagonal(Gf.Vec4d(-0.3, 0.3, -0.3, 1))
        self.__marker_scale_offset_shown_forward = Gf.Matrix4d().SetTranslate(
            Gf.Vec3d(0, 10.0, 0)
        ) * Gf.Matrix4d().SetDiagonal(Gf.Vec4d(0.3, 0.3, 0.3, 1))

        # Define tool tips for the two possible teleport operations
        self.get_tooltip_manager().define_tooltip("teleport_forward", XRTooltip(text="Teleport forward"))
        self.get_tooltip_manager().define_tooltip("teleport_backward", XRTooltip(text="Teleport backward"))

        self.__usd_layer: Optional[XRUsdLayer] = None

        # To construct teleporters we need to have a controller model loaded
        # TODO: In the future just depend on positions coming from OpenXR
        self.__controller_subs = [
            self.register_message_bus_event_handler("xr_gui.controllers.enable", self.update_teleport, 10),
            self.register_message_bus_event_handler("xr_gui.controllers.disable", self.on_disable, -10),
            self.register_message_bus_event_handler("xr_input.user_hand_left.attachments_change", self.update_teleport),
            self.register_message_bus_event_handler(
                "xr_input.user_hand_right.attachments_change", self.update_teleport
            ),
        ]

        self.left_bound = False
        self.right_bound = False

        # This function checks if the tool was already enabled when the tool class
        # got initialized. If so it will enable the tool.
        self.run_enable_if_enabled()

    def on_enable(self) -> None:
        """
        This function is called when tool is enabled.
        """

        self.update_teleport()

    def update_teleport(self) -> None:
        """
        This function is called when the tool is enabled.
        """

        if not self.is_enabled():
            return

        if self.has_usd_layer(XR_TELEPORT_GUI_LAYER):
            self.__usd_layer = self.get_usd_layer(XR_TELEPORT_GUI_LAYER)

        if self.__usd_layer is None:
            return

        if (self.__usd_layer.get_meta_data(XR_USER_HAND_LEFT + "/attachments/aim") is None) and (
            self.__usd_layer.get_meta_data(XR_USER_HAND_RIGHT + "/attachments/aim") is None
        ):
            return

        # Path where max height setting can be found
        self.__arc_max_height_settings_path = (
            self.get_xr_core().get_current_profile().get_persistent_path() + "teleport/arc_max_height"
        )
        self.get_settings().set_default(self.__arc_max_height_settings_path, 5.0)
        self.__arc_max_height: float = self.get_settings().get(self.__arc_max_height_settings_path)

        # List with event handlers and event generators

        # Clear all previous subscriptions
        self.__subs = []

        self.__subs = [
            # Functions to call when teleporter is started and ended
            self.register_message_bus_event_handler("xr_left_teleport_forward.press", self.teleport_forward_press),
            self.register_message_bus_event_handler("xr_left_teleport_forward.release", self.teleport_release),
            self.register_message_bus_event_handler("xr_left_teleport_forward.update", self.teleport_update),
            self.register_message_bus_event_handler("xr_left_teleport_forward.suspend", self.teleport_suspend),
            self.register_message_bus_event_handler("xr_left_teleport_backward.press", self.teleport_backward_press),
            self.register_message_bus_event_handler("xr_left_teleport_backward.release", self.teleport_release),
            self.register_message_bus_event_handler("xr_left_teleport_backward.update", self.teleport_update),
            self.register_message_bus_event_handler("xr_left_teleport_backward.suspend", self.teleport_suspend),
            self.register_message_bus_event_handler("xr_right_teleport_forward.press", self.teleport_forward_press),
            self.register_message_bus_event_handler("xr_right_teleport_forward.release", self.teleport_release),
            self.register_message_bus_event_handler("xr_right_teleport_forward.update", self.teleport_update),
            self.register_message_bus_event_handler("xr_right_teleport_forward.suspend", self.teleport_suspend),
            self.register_message_bus_event_handler("xr_right_teleport_backward.press", self.teleport_backward_press),
            self.register_message_bus_event_handler("xr_right_teleport_backward.release", self.teleport_release),
            self.register_message_bus_event_handler("xr_right_teleport_backward.update", self.teleport_update),
            self.register_message_bus_event_handler("xr_right_teleport_backward.suspend", self.teleport_suspend),
            # Callback to track when arc height is changed
            self.register_setting_event_handler(self.__arc_max_height_settings_path, self.arc_height_change),
        ]

        left_forward = self.bind_input_event_generator(
            "xr_left_teleport_forward",
            ("press", "release", "update", "suspend"),
            {"tooltip_button": "teleport_forward"},
        )

        left_backward = self.bind_input_event_generator(
            "xr_left_teleport_backward",
            ("press", "release", "update", "suspend"),
            {"tooltip_button": "teleport_forward"},
        )

        if left_forward is not None or left_backward is not None:
            self.left_bound = True

        right_forward = self.bind_input_event_generator(
            "xr_right_teleport_forward",
            ("press", "release", "update", "suspend"),
            {"tooltip_button": "teleport_forward"},
        )

        right_backward = self.bind_input_event_generator(
            "xr_right_teleport_backward",
            ("press", "release", "update", "suspend"),
            {"tooltip_button": "teleport_forward"},
        )

        if right_forward is not None or right_backward is not None:
            self.right_bound = True

        self.__subs.append([left_forward, left_backward, right_forward, right_backward])

        # load material model
        self.load_models()

        # build the beams that lay dormant until needed to teleport around
        # USD is slow when adding and deleting prims, hence we have them around
        # in case we need them

        self.remove_teleporters()
        self.build_teleporters()

    def on_disable(self) -> None:
        """
        This function is called when the tool is disabled.
        """

        # remove event handlers and event generators
        self.__subs = []

        # Remove the prims inside usd
        self.remove_teleporters()

        # Clear local reference to usd layer and teleporter information
        self.__usd_layer = None
        self.__teleport_beams = {}

    def remove_teleporters(self) -> None:
        """
        Function called to remove the teleporters from usd.
        """

        if self.__usd_layer is not None:
            self.__usd_layer.remove_group(XR_TELEPORT_GUI_LAYER_GROUP)

    def build_teleporters(self) -> None:
        """
        Function to build teleporters.
        """

        self.__teleport_beams = {}
        if self.left_bound:
            self.__teleport_beams[XR_USER_HAND_LEFT] = self.setup_teleport(XR_USER_HAND_LEFT)

        if self.right_bound:
            self.__teleport_beams[XR_USER_HAND_RIGHT] = self.setup_teleport(XR_USER_HAND_RIGHT)

    def arc_height_change(self, *args) -> None:
        """
        This function is called when the arc height is changed.
        """

        # Get the new height
        self.__arc_max_height = self.get_settings().get(self.__arc_max_height_settings_path)

        if self.__usd_layer is not None:

            # If there is a managed prim object, update the height
            if XR_USER_HAND_LEFT in self.__teleport_beams:
                self.__usd_layer.set_max_height(
                    self.__teleport_beams[XR_USER_HAND_LEFT].beam_path, self.__arc_max_height
                )
            if XR_USER_HAND_RIGHT in self.__teleport_beams:
                self.__usd_layer.set_max_height(
                    self.__teleport_beams[XR_USER_HAND_RIGHT].beam_path, self.__arc_max_height
                )

    def load_models(self) -> None:
        """
        This function loads asset in a hidden spot in the managed usd layer.
        The assets are then referenced into the locations where the data is needed.
        This allows us to cache assets at the start of the XR session.
        """

        if self.__usd_layer is not None:
            # Ensure that the beam materials are loaded into the scene
            # We record the usd path where the material can be found
            self.__beam_material: str = (
                self.__usd_layer.load_asset("{generic.materials}/selection_emissive_material.usd")
                + "/Looks/selection_emissive_material"
            )

    def setup_teleport(self, hand: str) -> Optional[XRTeleporterBeam]:
        """
        This function creates the teleport beam in the managed usd layer.
        """

        if self.__usd_layer is not None:

            teleport_beam: XRTeleporterBeam = XRTeleporterBeam()
            attachment_point_path: Optional[str] = self.__usd_layer.get_meta_data(hand + "/attachments/aim")

            # create a teleport beam object
            if attachment_point_path is None:
                return None

            teleport_beam.beam_path = attachment_point_path + "/teleporter"

            # This adds the entire arc.
            # Right now all logic to deal with arc is done in c++ for performance reasons
            # The arc has a series of segments that are placed along the arc and it automatically
            # ends at the first object it hits
            self.__usd_layer.add_teleport_arc(
                teleport_beam.beam_path,
                material_reference=self.__beam_material,
                tube_radius=2,
                max_height=self.__arc_max_height * 100,
                num_segments=32,
                group=XR_TELEPORT_GUI_LAYER_GROUP,
                visible=True,
            )

            # Get usd path for the teleporter tip, to link object to the tip (tip is always generated)
            beam_tip: str = self.__usd_layer.get_end_prim_path(teleport_beam.beam_path)

            # Build a reorientation to ensure model placed on tip faces the same way as the device
            # defined usd path
            teleport_beam.reorient_path = beam_tip + "/reorient"

            # At the end of the teleport beam we reorient the pose upward, so the marker
            # will be vertically aligned
            self.__usd_layer.add_reorient(
                path=teleport_beam.reorient_path,
                alignment=XROrientationAlignment.device_up_right,
                group=XR_TELEPORT_GUI_LAYER_GROUP,
                visible=True,
            )

            # Define marker for forward and backward teleport
            teleport_beam.target_path = teleport_beam.reorient_path + "/target"

            # Teleport marker, by default the marker is very tiny hidden inside the beam
            asset_path = XRAssetManager.get_singleton().resolve_asset_path("{generic.markers}/teleport_gizmo.usd")
            self.__usd_layer.add_asset(
                teleport_beam.target_path,
                visible=False,
                group=XR_TELEPORT_GUI_LAYER_GROUP,
                pickable=False,
                file_path=asset_path,
            )

            # hide teleport beam object beam by default
            self.__usd_layer.hide(teleport_beam.beam_path)

            return teleport_beam

    def teleport_forward_press(self, event: XRInputDeviceGeneratorEvent) -> None:
        """
        This function is called to start forward teleport
        """

        if self.__usd_layer is not None:
            self.teleport_press(event, XR_TELEPORT_FORWARD)

    def teleport_backward_press(self, event: XRInputDeviceGeneratorEvent) -> None:
        """
        This function is called to start backward teleport
        """

        if self.__usd_layer is not None:
            self.teleport_press(event, XR_TELEPORT_BACKWARD)

    def teleport_press(self, event: XRInputDeviceGeneratorEvent, direction: str) -> None:
        """
        This function is called for teleport
        """

        if self.__usd_layer is not None:
            # Get hand the teleport is coming from
            hand: str = event.input_device

            # Check if beam is active, in which case we do not allow for teleport beam
            beam: Optional[XRSelectionBeam] = self.get_selection_manager().get_beam(hand)
            if beam is not None and beam.is_active():
                return

            # Get teleport beam information
            teleport_beam: Optional[XRTeleporterBeam] = self.__teleport_beams.get(hand)
            if teleport_beam is None:
                return

            # Show the teleport beam
            self.__usd_layer.show(teleport_beam.beam_path)

            # Tell which direction to use
            teleport_beam.active = True
            teleport_beam.direction = direction

            # show marker, by default it is very tiny and will be updated to a big
            # marker in case the beam hits a colinear surface
            self.__usd_layer.show(teleport_beam.target_path)

    def teleport_update(self, event: XRInputDeviceGeneratorEvent) -> None:
        """
        This function is called during teleport and resolves whether user can
        teleport to that location.
        """

        if self.__usd_layer is not None:
            hand: str = event.input_device
            teleport_beam: Optional[XRTeleporterBeam] = self.__teleport_beams.get(hand)

            if teleport_beam is not None and teleport_beam.active is True:

                # Retrieve latest target the teleport beam is pointing at
                target_info = self.__usd_layer.get_target_info(teleport_beam.beam_path)
                target_usd_path: Optional[str] = target_info.get_target_usd_path()

                if target_usd_path is not None and target_usd_path.startswith(teleport_beam.beam_path):
                    # As a precaution, ignore a self-hit even though pickable is set to False
                    return

                # TODO: Check if usdrt finally supports setting visibility fast
                # Right now we hide things by making them really small

                # We need the coordinate system to resolve what the up index in stage coordinates is
                coordinate_system: XRCoordinateSystem = self.get_xr_core().get_coordinate_system()

                # Check if we don't hit ourselves and that we hit a surface that is relatively level
                if (
                    target_info.valid
                    and target_info.normal[coordinate_system.up_axis_index] > TELEPORT_COLINEAR_THRESHOLD
                ):
                    # We hit a proper surface

                    # Update the target if it is not shown currently
                    if not teleport_beam.target_shown:
                        self.__usd_layer.show(teleport_beam.target_path)
                        if teleport_beam.direction == XR_TELEPORT_FORWARD:
                            # Set the forward transform
                            self.__usd_layer.set_transform(
                                teleport_beam.target_path, transform=self.__marker_scale_offset_shown_forward
                            )
                        else:
                            # Set the backward transform
                            self.__usd_layer.set_transform(
                                teleport_beam.target_path, transform=self.__marker_scale_offset_shown_backward
                            )

                        # record that state of marker is shown
                        teleport_beam.target_shown = True
                else:
                    # no surface is hit, disable the marker

                    if teleport_beam.target_shown:

                        self.__usd_layer.hide(teleport_beam.target_path)
                        teleport_beam.target_shown = False

    def teleport_release(self, event: XRInputDeviceGeneratorEvent) -> None:
        """
        This function is called when teleporter button is released.
        """

        if self.__usd_layer is not None:
            hand: str = event.input_device
            teleport_beam: Optional[XRTeleporterBeam] = self.__teleport_beams.get(hand)

            if teleport_beam is None:
                return

            # Hide the teleporter, no longer needed
            self.__usd_layer.hide(teleport_beam.beam_path)
            self.__usd_layer.hide(teleport_beam.target_path)

            # Teleport beam is no longer active
            teleport_beam.active = False

            # if result is valid and normal is pointing up
            target_info = self.__usd_layer.get_target_info(teleport_beam.beam_path)

            # Get the stage coordinate system definition
            coordinate_system: XRCoordinateSystem = self.get_xr_core().get_coordinate_system()

            if target_info.valid and target_info.normal[coordinate_system.up_axis_index] > TELEPORT_COLINEAR_THRESHOLD:

                # set a default player height
                player_height: float = 1.7

                hmd_input_device: XRInputDevice = self.get_xr_core().get_input_device("displayDevice")

                # if there is a display device, check it's z value as that is a good indicator of player height
                if hmd_input_device is not None:
                    # We get display device in physical coordinates, which means
                    # y is up and the units are in meters
                    phys_trans = hmd_input_device.get_pose()
                    hmd_location = phys_trans.ExtractTranslation()

                    # Set better player height estimate
                    player_height = hmd_location[1]

                # Get player height in stage coordinates
                player_height = player_height / coordinate_system.meters_per_unit
                # Create up vector with length of player
                up_vector = tuple(player_height * x for x in coordinate_system.get_up_vector())

                # Get the surface's enclosing model.
                # This is the prim the user will be connected to
                # So if it is a moving car, the user will move with the car
                anchor: Optional[str] = target_info.get_target_enclosing_model_usd_path()
                if anchor is None:
                    return

                # Get the transform of the marker, this is where we are teleporting to.
                mat: Gf.Matrix4d = self.__usd_layer.get_transform(teleport_beam.target_path, XRTransformType.stage)

                # Add player height offset to that location
                mat.SetRow3(3, mat.GetRow3(3) + up_vector)

                # Teleport function: this will set the new anchor,
                # it will make your current hmd pose in the physical space match
                # with what is in 'mat' and calculate the intermediate transform
                # to set the reference of the local hmd
                self.get_xr_core().schedule_teleport_to_view(anchor, mat)

    def teleport_suspend(self, event: XRInputDeviceGeneratorEvent) -> None:
        """
        This function is called if the teleport button is replaced.
        This is to ensure a user is not stuck in teleporting mode.
        """

        if self.__usd_layer is not None:
            hand: str = event.input_device
            teleport_beam: Optional[XRTeleporterBeam] = self.__teleport_beams.get(hand)
            if teleport_beam is None:
                return

            # Just hide the beam and the target
            self.__usd_layer.hide(teleport_beam.beam_path)
            self.__usd_layer.hide(teleport_beam.target_path)

            # Set the beam inactive
            teleport_beam.active = False
