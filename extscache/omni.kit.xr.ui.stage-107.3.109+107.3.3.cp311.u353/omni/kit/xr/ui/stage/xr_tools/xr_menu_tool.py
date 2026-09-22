# Copyright (c) 2021-2025, NVIDIA CORPORATION.  All rights reserved.
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

from typing import Optional

import carb
from omni.kit.xr.core import (
    XRCoordinateSystem,
    XRCore,
    XRInputDevice,
    XRToolComponentBase,
    XRTooltip,
    XRTransformType,
    XRUsdLayer,
)
from omni.kit.xr.scene_view.utils import UiContainer, WidgetComponent
from omni.kit.xr.scene_view.utils.manipulator_components.widget_component import UpdatePolicy
from omni.kit.xr.scene_view.utils.spatial_source import SpatialSource
from pxr import Gf

from .scene_ui_widgets import XRMenuWidget

XR_GUI_LAYER_GROUP: str = "menu_tool"

XR_MENU_DISTANCE: int = 1
XR_MENU_WIDTH: float = 3.5
XR_MENU_HEIGHT: float = 3.0
XR_MENU_RESOLUTION_SCALE: int = 10
XR_MENU_UNIT_TO_PIXEL_SCALE: float = 100.0
XR_DISTANCE_TO_DEACTIVATE_METERS: int = 3

XR_USD_LAYER_KEY = "controllers"


class XRMenuTool(XRToolComponentBase):

    def __init__(self):
        # Initialize parent class
        super().__init__("menu")

        # Track whether the menu is placed
        self.__placed: bool = False

        self.__usd_layer: Optional[XRUsdLayer] = None

        # The widget of the menu
        self.__settings_menu_widget = None

        # The location of the widget
        self.__settings_menu_location: Optional[Gf.Vec3d] = None

        # The distance in stage units for the menu to disappear
        self.__settings_menu_distance_for_hide: Optional[float] = None

        # Define a tooltip
        self.get_tooltip_manager().define_tooltip("settings_menu", XRTooltip(text="Settings menu"))

        # This function enables the tool if it was enabled before the tool had been loaded (hot reload)
        self.run_enable_if_enabled()

    def on_enable(self) -> None:
        """
        This function is called when the tool is enabled.
        """

        # Get the usd layer, this one creates the layer if needed
        self.__usd_layer = self.get_usd_layer(XR_USD_LAYER_KEY)

        # Register a callback to an event of when menu needs to be toggled and
        # an event generator that connects that event to the assigned button

        # Bind the xr_menu.release callback and call toggle_menu.
        # Bind the xr_menu (look up in the action map the assigned button) and on release of that button generate an event
        self.__subs = [
            self.register_message_bus_event_handler("xr_menu.release", self.toggle_menu),
            self.bind_input_event_generator("xr_menu", ("release"), {"tooltip_button": "settings_menu"}),
        ]

    def on_disable(self) -> None:
        """
        This function is called when the tool is disabled.
        """

        # Remove all subscriptions
        self.__subs = []
        self.hide_settings_menu()
        self.__usd_layer = None

    def toggle_menu(self) -> None:
        """
        This function is called when the settings menu toggle button is hit.
        """

        # Determine if we need to place or hide the menu
        if self.__placed:
            self.hide_settings_menu()
        else:
            self.place_settings_menu()

    def hide_settings_menu(self):
        """
        This function removes the menu.
        """

        if self.__settings_menu_widget:
            # Remove the widget
            self.__settings_menu_widget.root.clear()
            self.__settings_menu_widget = None

        self.__placed = False

        self.__usd_layer.remove_group(XR_GUI_LAYER_GROUP)

    def place_settings_menu(self) -> None:
        """
        This function places the tool menu in the scene.
        """

        # Find the location of the hmd/tablet
        input_device: Optional[XRInputDevice] = self.get_xr_core().get_input_device("displayDevice")
        if input_device is None:
            return

        # Get the pose in stage space
        device_pose: Gf.Matrix4d = input_device.get_virtual_world_pose()

        # Get the current coordinate system
        coordinate_system: XRCoordinateSystem = self.get_xr_core().get_coordinate_system()
        usd_layer_coordinate_system: XRCoordinateSystem = self.__usd_layer.get_coordinate_system()

        carb.log_info("[XR] PLACING XR MENU:")
        carb.log_info(f"  coordinate_system meters-per-unit: {coordinate_system.meters_per_unit}")
        carb.log_info(f"  usd_layer_coordinate_system meters-per-unit: {usd_layer_coordinate_system.meters_per_unit}")

        # Compute scale forward vector (corrected for unit size of stage)
        forward_vector: tuple[float] = tuple(
            (XR_MENU_DISTANCE / coordinate_system.meters_per_unit) * x
            for x in usd_layer_coordinate_system.get_forward_vector()
        )

        # Ensure the pose is upright in the current coordinate system

        device_pose: Gf.Matrix4d = XRCore.get_singleton().reorient_transform_matrix_up_right(
            device_pose, coordinate_system.up_axis == "y"
        )

        # Move the location by the forward vector so it is right in the user's view
        menu_location: Gf.Matrix4d = Gf.Matrix4d().SetTranslate(forward_vector) * device_pose

        usd_path = self.__usd_layer.get_top_level_prim_path() + "/menu/settings"

        self.__usd_layer.add_transform(
            path=usd_path,
            group=XR_GUI_LAYER_GROUP,
            transform=menu_location,
            transform_type=XRTransformType.stage,
        )

        # Create the widget
        widget_component = WidgetComponent(
            XRMenuWidget,
            XR_MENU_WIDTH / coordinate_system.meters_per_unit,
            XR_MENU_HEIGHT / coordinate_system.meters_per_unit,
            XR_MENU_RESOLUTION_SCALE,
            XR_MENU_UNIT_TO_PIXEL_SCALE * coordinate_system.meters_per_unit,
            update_policy=UpdatePolicy.ON_MOUSE_HOVERED,
            widget_kwargs={"profile": self.get_xr_core().get_current_profile()},
        )
        self.__settings_menu_widget = UiContainer(
            widget_component,
            space_stack=[
                SpatialSource.new_prim_path_source(usd_path),
                SpatialSource.new_scale_source(Gf.Vec3d(0.25)),
            ],
        )

        # Store the location of where we placed the menu
        self.__settings_menu_location = menu_location.ExtractTranslation()
        carb.log_info(f"[XR] menu location for distance check: {self.__settings_menu_location}")

        # Store the distance in stage units of when to hide the menu
        self.__settings_menu_distance_for_hide: float = (
            XR_DISTANCE_TO_DEACTIVATE_METERS / coordinate_system.meters_per_unit
        )

        self.__placed = True

    def on_update(self) -> None:
        """
        Called every tick while this tool is enabled
        """

        # Check if user is still close to the menu

        if self.__placed:

            # Find the primary display device (tablet, hmd)
            input_device: Optional[XRInputDevice] = self.get_xr_core().get_input_device("displayDevice")

            # Check if device exists
            if input_device is None:
                return

            # Get the current pose of the device
            pose: Gf.Matrix4d = input_device.get_virtual_world_pose()
            # All we need is the location in stage space
            location = pose.ExtractTranslation()

            # Compute distance to where the menu is. If it is too far away, then
            # hide the menu
            distance = Gf.GetLength(location - self.__settings_menu_location)
            if distance > self.__settings_menu_distance_for_hide:
                carb.log_info(
                    f"[XR] Disabling XR menu (too far away: {distance} > {self.__settings_menu_distance_for_hide})"
                )
                self.hide_settings_menu()
