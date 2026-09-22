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
# Use these at your own risk, and forward-compatability is not supported

__all__ = ["XRCore", "XRUtils"]

import asyncio
from functools import partial
from typing import Callable, Iterable, List, Optional, Tuple, Union

import carb
import omni.kit.notification_manager as nm
from omni.kit.viewport.utility import get_active_viewport
from pxr import Gf, Sdf, Usd

from ..._xrcore import XRCoordinateSystem, XRCore_Internal, XRRay, XRRayQueryResult, XRToken
from .xractionmap_class_wrapper import XRActionMap
from .xreventgenerator_class_wrapper import XREventGenerator
from .xrinputdevice_class_wrapper import XRInputDevice
from .xrprofile_class_wrapper import XRProfile
from .xrsystem_class_wrapper import XRSystem
from .xrusdlayer_class_wrapper import XRUsdLayer

# =================================================
# This file constructs a shim for the C++
# functionality exposed into python and adds
# types, type conversions, documentation, and
# improved python integration for these functions.
# =================================================

# ================================================
# XRCore class extensions
# ================================================


# pylint: disable=protected-access
# noinspection PyProtectedMember


class XRCore:
    _singleton: "XRCore"
    _singleton_deleted: bool

    def __init__(self):
        if hasattr(XRCore, "_singleton"):
            carb.log_error("Do not instantiate XRCore directly -- instead, use XRCore.get_singleton()")

        self.__internal = XRCore_Internal()

    def __eq__(self, other):
        if isinstance(other, XRCore):
            return self.__internal == other.__internal
        return False

    def __hash__(self):
        return self.__internal.__hash__()

    def _get_internal(self) -> XRCore_Internal:
        return self.__internal

    @staticmethod
    # NOTE: if we move to Python 3.11, this should return Self instead of "XRCore"
    def _start_singleton() -> "XRCore":
        # In case it is started for a second time, remove the flag
        if hasattr(XRCore, "_singleton_deleted"):
            del XRCore._singleton_deleted

        if not hasattr(XRCore, "_singleton"):
            carb.log_info("creating XRCore singleton")
            XRCore._singleton = XRCore()

        return XRCore._singleton

    @staticmethod
    # NOTE: if we move to Python 3.11, this should return Self instead of "XRCore"
    def get_singleton() -> "XRCore":
        if hasattr(XRCore, "_singleton_deleted"):
            raise RuntimeError("XRCore has been deleted")

        if not hasattr(XRCore, "_singleton"):
            carb.log_info("creating XRCore singleton")
            XRCore._singleton = XRCore()

        return XRCore._singleton

    @staticmethod
    def _delete_singleton() -> None:
        if hasattr(XRCore, "_singleton"):
            carb.log_info("deleting XRCore singleton")
            del XRCore._singleton
            XRCore._singleton_deleted = True

    def get_message_bus(self) -> carb.events.IEventStream:
        """
        This function returns the message bus for xr.

        Return:
            IEventStream
        """
        return self.__internal.get_message_bus()

    def dispatch_message_bus_and_check_consume(self, event_type, event_dict) -> bool:
        """
        This function dispatches a message on the message bus and adds consumed as a parameter in the
        payload and checks whether propagation should be stopped.
        Args:
            event_type:     type of the event
            event_dict:     dictionary of the event

        Return:
            whether propagation should be stopped
        """

        return self.__internal.dispatch_message_bus_and_check_consume(event_type, event_dict)

    def get_profile(self, name: str) -> XRProfile:
        """
        This function gets an XR profile. A profile has its own set of configuration.
        If the profile does not exist, a new one will be created.

        Args:
            name: Name of the profile

        Return:
            The requested XRProfile
        """
        return XRProfile(self.__internal.get_profile(name))

    def ensure_profile(self, name: str) -> XRProfile:
        """
        This function gets an XR profile. A profile has its own set of configuration.
        If the profile does not exist, a new one will be created.

        Args:
            name: Name of the profile

        Return:
            The requested XRProfile
        """
        return XRProfile(self.__internal.get_profile(name))

    def get_coordinate_system(self) -> XRCoordinateSystem:
        """
        This function returns the coordinate system used by XR.
        This is derived from the stage coordinate system, but maybe
        scaled if some scale is applied to the overall world

        Return:
            XR coordinate system
        """
        return self.__internal.get_coordinate_system()

    def get_stage_coordinate_system(self) -> XRCoordinateSystem:
        """
        This function returns the coordinate system used by the stage.

        Return:
            Stage coordinate system
        """
        return self.__internal.get_stage_coordinate_system()

    def get_profile_list(self) -> list[XRProfile]:
        """
        This function returns the list of profiles currently defined in the application.

        Return:
            A list of XRProfiles
        """
        return [XRProfile(x) for x in self.__internal.get_profile_list()]

    def get_profile_name_list(self) -> list[str]:
        """
        This function returns the list of the names of the profiles that are currently defined.

        Return:
            A list of profile names
        """
        return self.__internal.get_profile_name_list()

    def get_system(self, name: str) -> Optional[XRSystem]:
        """
        Return a system for a given name.

        Args:
            name:    name of the system

        Return:
            System
        """

        return XRSystem(self.__internal.get_system(name))

    def get_systems(self, modes: Union[list[str], str, None] = None) -> list[XRSystem]:
        """
        Return the list of available xr systems.
        This function allows for specifying which features and
        which operating modes need to supported.

        Args:
            modes:       list of modes required

        Return:
            A list of systems
        """

        if modes is None:
            modes = list()
        if isinstance(modes, str):
            modes = [modes]

        return [XRSystem(x) for x in self.__internal.get_systems(modes)]

    def get_system_names(self, modes: Union[list[str], str, None] = None) -> list[str]:
        """
        Return the list with names of available xr systems.
        This function allows for specifying which features and
        which operating modes need to supported.

        Args:
            modes:       list of modes required

        Return:
            A list of systems
        """

        if modes is None:
            modes = list()
        if isinstance(modes, str):
            modes = [modes]

        return [x.get_name() for x in self.__internal.get_systems(modes)]

    def is_xr_enabled(self) -> bool:
        """
        This function checks if XR is currently running.

        Return:
            True if XR is running, else False
        """
        return self.__internal.is_xr_enabled()

    def is_xr_display_enabled(self) -> bool:
        """
        This function checks if XR display is currently displaying.

        Return:
            True if XR is currently displaying output, else False
        """
        return self.__internal.is_xr_display_enabled()

    def is_xr_viewport_enabled(self) -> bool:
        """
        This function checks if XR viewport is currently displaying.

        Return:
            True if XR is currently displaying into viewport, else False
        """
        return self.__internal.is_xr_viewport_enabled()

    def get_current_profile(self) -> XRProfile:
        """
        This function gets the active XRProfile. Only one profile can be
        active at the same time.

        Return:
            active XRProfile
        """
        # TODO: One of these two functions should be deprecated/removed, right?
        return XRProfile(self.get_current_xr_profile())

    def get_current_xr_profile(self) -> XRProfile:
        """
        This function gets the active XRProfile. Only one profile can be
        active at the same time.

        Return:
            active XRProfile
        """
        return XRProfile(self.__internal.get_current_xr_profile())

    def get_current_profile_name(self) -> str:
        """
        This function returns the name of active XRProfile.

        Return:
            string with name of the active XRProfile
        """
        # TODO: One of these two functions should be deprecated/removed, right?
        return self.get_current_xr_profile_name()

    def get_current_xr_profile_name(self) -> str:
        """
        This function returns the name of active XRProfile.

        Return:
            string with name of the active XRProfile
        """
        return self.__internal.get_current_xr_profile().get_name()

    def create_xr_usd_layer(
        self,
        usd_path: str,
        meters_per_unit: float = 0.01,
        up_axis: str = "y",
        ui_layer_name: str = "",
        component_layer_name: str = "",
    ) -> XRUsdLayer:
        """
        This function creates a new session layer for the profile.

        Args:
            usd_path:               the usd path prefix used for all object in this session layer
            meters_per_unit:        number of meters per unit to use for this session layer
            up_axis:                string with name of the axis pointing up
            ui_layer_name:          name of layer to put xr session ui on
            component_layer_name:   name of layer to put xr ui components on

        Return:
            Session layer object
        """
        return XRUsdLayer(
            self.__internal.create_xr_usd_layer(usd_path, meters_per_unit, up_axis, ui_layer_name, component_layer_name)
        )

    @staticmethod
    def request_enable_profile(name: str) -> None:
        """
        Request a profile to be enabled.

        Args:
            name:   name of profile
        """

        carb.settings.get_settings().set_bool("/xr/profile/" + name + "/enabled", True)

    def request_disable_profile(self) -> None:
        """
        Request current profile to be disabled.
        """

        if self.get_current_xr_profile_name() != "":
            carb.settings.get_settings().set_bool(
                "/xr/profile/" + self.get_current_xr_profile_name() + "/enabled", False
            )

    def schedule_capture_viewport_frame(self, file_name: str, viewport_id: int = 0) -> None:
        """
        Capture xr viewport and save to file.

        Args:
            file_name:        name of the file in which to save the image
            viewport_id:      number of the viewport
        """

        return self.__internal.schedule_capture_viewport_frame(file_name, viewport_id)

    def schedule_capture_display_frame(
        self,
        file_name: str,
        display_name: Optional[str] = None,
        capture_source: Optional[str] = None,
        capture_output: Optional[str] = "color",
        capture_depth_range: Tuple[float, float] = (0.1, 10.0),
    ) -> None:
        """
        Capture xr display and save to file.

        Args:
            file_name:              Name of the image file (without extension)
            display_name:           Name of the display (default = None)
            capture_source:         Which rendered image to capture (display maybe composited of multiple images)
            capture_output:         Which type of output to capture
            capture_depth_range:    Near/far plane to use for depth visualization (default (0.1m, 10.0m))
        """

        return self.__internal.schedule_capture_display_frame(
            file_name, display_name, capture_source, capture_output, capture_depth_range
        )

    # TODO: This should be moved to a documentation plugin
    @staticmethod
    def show_ovxr_app_docs(page: Optional[str] = None) -> None:
        import webbrowser

        if page == "rendering_optimization":
            webbrowser.open(
                "https://docs.omniverse.nvidia.com/app_omniverse-xr/app_omniverse-xr/performance-optimization.html"
            )
        else:
            webbrowser.open("https://docs.omniverse.nvidia.com/app_omniverse-xr/app_omniverse-xr/overview.html")

    def test_system(self, system_name: str, test_name: str) -> None:
        return self.__internal.test_system(system_name, test_name)

    def submit_raycast_query(self, ray: XRRay, callback: Callable[[XRRay, XRRayQueryResult], None]) -> None:
        """
        This function submits a ray query to be resolved through a callback.

        Args:
            ray:      struct describing the ray (origin, orientation, length)
            callback: function that takes as first input the ray and as second input rayresult and is executed
                      once the query has completed (executes on main thread)
        """
        return self.__internal.submit_raycast_query(ray, callback)

    def submit_multi_raycast_query(
        self, rays: list[XRRay], callback: Callable[[list[XRRay], list[XRRayQueryResult]], None]
    ) -> None:
        """
        This function submits multiple ray queries at once to be resolved through a callback.

        Args:
            rays:     struct describing the ray (origin, orientation, length)
            callback: function that takes as first input a vector of rays (input) and as second input a vector of ray
                      results (result).
                      the function is executed once the query has completed (executes on main thread)
        """
        return self.__internal.submit_multi_raycast_query(rays, callback)

    def get_stage_anchor_prim_path(self) -> Optional[str]:
        """
        Get the currently bound stage anchor prim path.

        Return:
            string with path to stage anchor if any is set
        """
        return self.__internal.get_stage_anchor_prim_path()

    def detach_stage_anchor(self) -> None:
        """
        Detach the currently bound stage anchor prim path.
        """
        return self.__internal.detach_stage_anchor()

    def schedule_apply_viewport_navigation(
        self,
        dx: float,
        dy: float,
        dz: float,
        yaw: float,
        pitch: float,
    ) -> None:
        """
        Updates the view transform of the USD camera specified by cameraPrimPath and takes
        into account keyboard and mouse navigation value: translation, yaw, and pitch.

        Args:
            dx:                 The keyboard navigation x translation component
            dy:                 The keyboard navigation y translation component
            dy:                 The keyboard navigation z translation component
            yaw:                The mouse navigation yaw value in radians
            pitch:              The mouse navigation pitch value in radians
        """
        return self.__internal.schedule_apply_viewport_navigation(dx, dy, dz, yaw, pitch)

    def schedule_set_stage_anchor(self, stage_anchor: str) -> None:
        """
        Schedule setting the stage anchor and reset all the adjoining transforms. So that after
        this operation is executed the anchor is the space origin of the physical world.

        Args:
            stage_anchor:       Name of the usdPrim in the stage that functions as an anchor.
        """

        self.__internal.schedule_set_stage_anchor(stage_anchor)

    def schedule_teleport_to_view(
        self, stage_anchor: str, view_pose: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]]]
    ) -> None:
        """
        Schedule setting the stage anchor and the initial view pose of the camera. After this operation
        is executed the users camera pose is the viewpose and the stage_anchor is the anchor.

        Args:
            stage_anchor:       Name of the usdPrim in the stage that functions as an anchor.
            view_pose:          Pose of the camera that is the initial view.
        """

        self.__internal.schedule_teleport_to_view(stage_anchor, view_pose)

    def schedule_set_space_origin(
        self, space_origin_pose: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]]]
    ) -> None:
        """
        Schedule setting the stage origin

        Args:
            space_origin_pose:          Pose of the space origin.
        """

        self.__internal.schedule_set_space_origin(space_origin_pose)

    def schedule_set_camera(self, view_pose: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]]]) -> None:
        """
        Schedule camera so what is looked at matches the view_pose.

        Args:
            view_pose:          Pose of the camera that is the initial view.
        """

        self.__internal.schedule_set_camera(view_pose)

    def schedule_move_space_origin_relative_to_camera(self, dx: float, dy: float, dz: float) -> None:
        """
        Schedule rotating the space origin.

        Args:
            dx, dy, dz:     motion in the different directions
        """

        self.__internal.schedule_move_space_origin_relative_to_camera(dx, dy, dz)

    def schedule_rotate_space_origin_relative_to_camera(self, yaw: float, pitch: float) -> None:
        """
        Schedule rotating the space origin.

        Args:
            yaw, pitch:    rotation around camera
        """

        self.__internal.schedule_rotate_space_origin_relative_to_camera(yaw, pitch)

    def get_input_device(self, handle: Union[str, XRToken]) -> Optional[XRInputDevice]:
        """
        Get input device from current frame.

        Args:
            handle: type or name of input device component

        Return:
            XRInputDevice or None
        """
        input_device = self.__internal.get_input_device(handle)
        if input_device is None:
            return None
        return XRInputDevice(input_device)

    def has_input_device(self, handle: Union[str, XRToken]) -> bool:
        """
        Check if input device is available in current frame.

        Args:
            handle: type or name of input device component

        Return:
            whether the input device exists
        """
        return self.__internal.has_input_device(handle)

    def get_input_devices(self, handle: Union[str, XRToken]) -> list[XRInputDevice]:
        """
        Get list of input devices filtered by type or name.

        Args:
            handle: type or name of input device component

        Return:
            List with input devices
        """
        return [XRInputDevice(input_device) for input_device in self.__internal.get_input_devices(handle)]

    def get_all_input_devices(self) -> list[XRInputDevice]:
        """
        Get list of all input devices.

        Return:
            List of all input devices
        """
        return [XRInputDevice(input_device) for input_device in self.__internal.get_all_input_devices()]

    def get_action_map(self) -> Optional[XRActionMap]:
        """
        Get action map from current frame.

        Return:
            XRActionMap or None
        """
        action_map = self.__internal.get_action_map()
        if action_map is None:
            return None
        return XRActionMap(action_map)

    def is_gui_enabled(self) -> bool:
        """
        Check if the XR Gui is enabled.

        Return:
            True if enabled
        """
        return self.__internal.is_gui_enabled()

    def is_tool_enabled(self, tool: Union[str, XRToken]) -> bool:
        """
        Check if a tool is enabled.

        Args:
            tool:  name of the tool

        Return:
            True if enabled
        """
        return self.__internal.is_tool_enabled(tool)

    def is_gui_layer_enabled(self, gui_layer: Union[str, XRToken]) -> bool:
        """
        Check if a gui layer is enabled.

        Args:
            gui_layer:  name of the gui layer

        Return:
            True if enabled
        """
        return self.__internal.is_gui_layer_enabled(gui_layer)

    def bind_input_event_generator(
        self, event_name: str, event_list: Iterable[str], tooltips: Union[dict[str, str], str] = {}
    ) -> Optional[XREventGenerator]:
        """
        Bind an event generator.

        Args:
            event_name: name of the event that needs to be generated
            event_list: tuple with names of events that need to be generated (e.g press, release, etc)
            tooltips:   dictionary with tooltips

        Return:
            XREventGenerator or None
        """

        if isinstance(tooltips, str):
            tooltips = {"click": tooltips}

        event_generator = self.__internal.bind_input_event_generator(event_name, event_list, tooltips)
        if event_generator is None:
            return None
        return XREventGenerator(event_generator)

    def unbind_input_event_generator(self, event_name: str) -> None:
        """
        Unbind an event generator. If the event generator does not exist this function does nothing.

        Args:
            event_name: name of the event that needs to be ubound
        """
        self.__internal.unbind_input_event_generator(event_name)

    @staticmethod
    def check_current_renderer_supported(profile_display_name: str, notify: bool = True) -> bool:
        """
        Checks that the current renderer is supported in XR mode and gives a warning if not.

        Args:
            profile_display_name:           The display name of the XR profile trying to be enabled

        Return:
            Whether XR can be enabled with the current renderer
        """

        settings = carb.settings.get_settings()
        renderer = settings.get("/renderer/active")
        render_mode = settings.get("/rtx/rendermode")

        if str(renderer) == "rtx" and str(render_mode) == "PathTracing":
            # RTX Path Tracing is experimentally supported, allow but warn
            if notify:
                nm.post_notification(
                    "Current Render Mode may not achieve a comfortable frame rate.\nSwitch to RTX - Realtime for smoother playback.",
                    duration=3,
                    status=nm.NotificationStatus.WARNING,
                )
            return True
        elif renderer == "rtx":
            # RTX (not path traced) is supported, allow
            return True
        else:
            # Others are not supported, warn and block
            if notify:
                nm.post_notification(
                    f"Current Render Mode Not Supported.\nSwitch to RTX - Realtime and Start {profile_display_name} again.",
                    duration=3,
                    status=nm.NotificationStatus.WARNING,
                )
            return False

    def set_pickable_path(self, usd_path: str, pickable: bool) -> None:
        """
        This function sets a usd path to be pickable and updates that setting every time the usd is updated.

        Args:
            usd_path:      usd path of tree that needs to be pickable/not pickable
            pickable:      whether prims need to be pickable
        """
        return self.__internal.set_pickable_path(usd_path, pickable)

    def unset_pickable_path(self, usd_path: str) -> None:
        """
        This function unsets a usd path to be pickable and removes the automated update.

        Args:
            usd_path:      usd path of tree that needs to be unset
        """
        return self.__internal.unset_pickable_path(usd_path)

    # TODO: OMPE-16574 -- Remove FSD checks once FSD replaces OmniHydra completely
    def is_fsd_enabled(self) -> bool:
        """
        This function checks if the Fabric Scene Delegate is enabled.

        Return:
            True if FSD is enabled, else False
        """
        return self.__internal.is_fsd_enabled()

    def suggest_edit_layer_for_prim(self, prim: Union[Usd.Prim, Sdf.Path, str]) -> str:
        """
        Suggest on which layer to make an edit when using XR tooling. This function will return the name of a session
        layer if the prim has edits on the session layer, otherwise it will return the root layer.

        Args:
            prim_path:  path of the prim

        Return:
            name of the layer
        """

        prim_path: str = ""
        if isinstance(prim, Usd.Prim):
            prim_path = prim.GetPath().pathString
        else:
            prim_path = str(prim)

        return self.__internal.suggest_edit_layer_for_prim(prim_path)

    def check_if_prim_transform_is_usdrt_only(self, prim: Union[Usd.Prim, Sdf.Path, str]) -> bool:
        """
        Check if the transform in usdrt is different from usd. If that is the case, it is likely only
        usdrt is updated for that prim and so any edits we do should be in usdrt as well
        Args:
            prim_path:  path of the prim

        Return:
            true if usdrt transform is significantly different
        """

        prim_path: str = ""
        if isinstance(prim, Usd.Prim):
            prim_path = prim.GetPath().pathString
        else:
            prim_path = str(prim)

        return self.__internal.check_if_prim_transform_is_usdrt_only(prim_path)

    def check_if_prim_is_on_layer(
        self, prim: Union[Usd.Prim, Sdf.Path, str], layer: Union[str, None, Sdf.Layer]
    ) -> bool:
        """
        Check if a prim has opinions on a given layer.

        Args:
            prim_path:         path of the prim
            layer_identifier:  identifier of the layer

        Return:
            True if it has opinions on given layer
        """

        prim_path: str = ""
        if isinstance(prim, Usd.Prim):
            prim_path = prim.GetPath().pathString
        else:
            prim_path = str(prim)

        layer_identifier: str = ""
        if isinstance(layer, Sdf.Layer):
            layer_identifier = layer.identifier
        elif layer is not None:
            layer_identifier = str(layer)

        return self.__internal.check_if_prim_is_on_layer(prim_path, layer_identifier)

    def remove_prim_from_layer(self, prim: Union[Usd.Prim, Sdf.Path, str], layer: Union[str, None, Sdf.Layer]) -> None:
        """
        Remove a prim from a given layer.

        Args:
            prim_path:         path of the prim
            layer_identifier:  identifier of the layer
        """

        prim_path: str = ""
        if isinstance(prim, Usd.Prim):
            prim_path = prim.GetPath().pathString
        else:
            prim_path = str(prim)

        layer_identifier: str = ""
        if isinstance(layer, Sdf.Layer):
            layer_identifier = layer.identifier
        elif layer is not None:
            layer_identifier = str(layer)

        self.__internal.remove_prim_from_layer(prim_path, layer_identifier)

    def set_local_transform_matrix(
        self,
        prim: Union[Usd.Prim, Sdf.Path, str],
        matrix: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]]],
        layer_identifier: Union[str, None] = None,
    ) -> None:
        """
        This function sets the local transform matrix of a usd prim. By default if
        no layer name is given the function writes to usdrt otherwise it will write
        to usd.

        Args:
            prim:             usd prim
            matrix:           local transform matrix
            layer_identifier: option layer name. If not provided current edit target is used.
        """

        prim_path: str = ""
        if isinstance(prim, Usd.Prim):
            prim_path = prim.GetPath().pathString
        else:
            prim_path = str(prim)

        if layer_identifier is not None:
            self.__internal.set_local_transform_matrix_usd(prim_path, matrix, layer_identifier)
        else:
            self.__internal.set_local_transform_matrix(prim_path, matrix)

    def set_world_transform_matrix(
        self,
        prim: Union[Usd.Prim, Sdf.Path, str],
        matrix: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]]],
        layer_identifier: Union[str, None] = None,
    ) -> None:
        """
        This function sets the world transform matrix of a usd prim. By default if
        no layer name is given the function writes to usdrt otherwise it will write
        to usd.

        Args:
            prim:             usd prim
            matrix:           local transform matrix
            layer_identifier: option layer name. If not provided current edit target is used.
        """

        prim_path: str = ""
        if isinstance(prim, Usd.Prim):
            prim_path = prim.GetPath().pathString
        else:
            prim_path = str(prim)

        if layer_identifier is not None:
            self.__internal.set_world_transform_matrix_usd(prim_path, matrix, layer_identifier)
        else:
            self.__internal.set_world_transform_matrix(prim_path, matrix)

    def get_local_transform_matrix(self, prim: Union[Usd.Prim, Sdf.Path, str]) -> Gf.Matrix4d:
        """
        This function gets the local transform matrix of a usd prim.

        Args:
            prim: usd prim

        Return:
            Local transform matrix of prim
        """

        prim_path: str = ""
        if isinstance(prim, Usd.Prim):
            prim_path = prim.GetPath().pathString
        else:
            prim_path = str(prim)

        return Gf.Matrix4d(*self.__internal.get_local_transform_matrix(prim_path))

    def get_world_transform_matrix(self, prim: Union[Usd.Prim, Sdf.Path, str]) -> Gf.Matrix4d:
        """
        This function gets the world transform matrix of a usd prim.

        Args:
            prim: usd prim

        Return:
            World transform matrix of prim
        """

        prim_path: str = ""
        if isinstance(prim, Usd.Prim):
            prim_path = prim.GetPath().pathString
        else:
            prim_path = str(prim)

        return Gf.Matrix4d(*self.__internal.get_world_transform_matrix(prim_path))

    def get_enclosing_model(self, usd_path: str) -> str:
        """
        This function resolves the enclosing model based on a usd path. It gets the closest parent
        that has been marked as a model.

        Args:
            usd_path:      a usd path inside the enclosing model
        """
        return self.__internal.get_enclosing_model(usd_path)

    def reorient_transform_matrix_up_right(
        self, matrix: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]]], y_up: bool = True
    ) -> Gf.Matrix4d:
        """
        This function reorients a transform so up points up

        Args:
            matrix: transform matrix to modify
            y_up: whether y is up (otherwise z is up)

        Return:
            Transformed matrix
        """

        return Gf.Matrix4d(*self.__internal.reorient_transform_up_right(matrix, y_up))

    def reorient_transform_matrix_no_roll(
        self, matrix: Union[Gf.Matrix4d, Iterable[float], Iterable[Iterable[float]]], y_up: bool = True
    ) -> Gf.Matrix4d:
        """
        This function reorients a transform so right vector is parallel to the
        ground plane.

        Args:
            matrix: transform matrix to modify
            y_up: whether y is up (otherwise z is up)

        Return:
            Transformed matrix
        """

        return Gf.Matrix4d(*self.__internal.reorient_transform_no_roll(matrix, y_up))

    @staticmethod
    def on_raycast_query_result(_ray: XRRay, result: XRRayQueryResult, future: asyncio.Future) -> None:
        """
        Internal callback-to-future conversion.
        """
        future.set_result(result)

    async def execute_raycast_query_async(self, ray: XRRay) -> XRRayQueryResult:
        """
        This function is the asynchronous version of function submit_raycast_query.

        Args:
            ray:     struct describing the ray (origin, orientation, length)

        Return:
            future with raycast query result
        """
        f: asyncio.Future = asyncio.Future()
        self.submit_raycast_query(ray, partial(XRCore.on_raycast_query_result, future=f))
        return await f

    @staticmethod
    def on_multi_raycast_query_result(
        _rays: List[XRRay], results: List[XRRayQueryResult], future: asyncio.Future
    ) -> None:
        """
        Internal callback-to-future conversion.
        """
        future.set_result(results)

    async def execute_multi_raycast_query_async(self, rays: List[XRRay]) -> List[XRRayQueryResult]:
        """
        Asynchronous version of function submit_multi_raycast_query.

        Args:
            rays:     list describing many rays (origin, orientation, length)

        Return:
            future with raycast query results
        """
        f: asyncio.Future = asyncio.Future()
        self.submit_multi_raycast_query(rays, partial(XRCore.on_multi_raycast_query_result, future=f))
        return await f


XRUtils = XRCore
