# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

# =================================== NOTE ====================================
# The APIs in this file are unfinished and may change in future releases
# Using these is at your own risk, and forward-compatability is not supported

__all__ = ["XRViewportController"]

import math
from typing import Optional, Tuple

import carb
import carb.events
import carb.profiler
import omni.kit.app
import omni.kit.viewport.utility as viewport_utils
import omni.usd
from omni.kit.manipulator.camera import ViewportCameraManipulator
from omni.kit.manipulator.camera.model import CameraManipulatorModel, ModelState
from omni.kit.viewport.window import ViewportWindow
from omni.kit.xr.core import (
    XRCore,
    XRCoreEventType,
    XRRay,
    XRRayQueryResult,
    XRSingleton,
    XRSingletonType,
    XRWeakMethod,
)
from pxr import Gf, Sdf, Usd, UsdGeom

XR_VIEWPORT_BOUND_CAMERA_SETTING = "/xr/viewport/boundCamera"
XR_ANCHOR_RESET_SETTING = "/xr/anchor/reset"

# Predefined paths for the xrCamera prim and the xrAnchor prim
XR_STAGE_CAMERA = "/_xr/stage/xrCamera"
XR_STAGE_ANCHOR = "/_xr/stage/xrAnchor"
XR_STAGE_SPACE_ORIGIN = "/_xr/stage/xrSpaceOrigin"


@XRSingleton()
class XRViewportController(XRSingletonType):
    def __init__(self):
        # Get the active viewport, we use that for mirroring XR
        self.__viewport_api, self.__viewport_window = viewport_utils.get_active_viewport_and_window()

        # If there is no viewport exit out
        if self.__viewport_api is None:
            carb.log_error("ViewportAPI is unexpectedly None")
            return

        if self.__viewport_window is None:
            carb.log_error("ViewportWindow is unexpectedly None")
            return

        # Prim paths representing camera and anchor during XR session
        self.__xr_camera_path: str = XR_STAGE_CAMERA
        self.__xr_anchor_path: str = XR_STAGE_ANCHOR
        self.__xr_space_origin_path: str = XR_STAGE_SPACE_ORIGIN

        # Prims representing camera and anchor during XR session
        self.__xr_camera_prim: Optional[UsdGeom.Camera] = None
        self.__xr_anchor_prim: Optional[UsdGeom.XForm] = None
        self.__xr_space_origin_prim: Optional[UsdGeom.XForm] = None

        # Cache useful pieces of carb
        self.__settings = carb.settings.get_settings()
        self.__xrcore: XRCore = XRCore.get_singleton()

        self.__enable_reset_anchor: bool = True
        self.__xr_viewport_enabled: bool = False

        # Get events from XRCore
        xr_message_bus: carb.events.IEventStream = XRCore.get_singleton().get_message_bus()

        # We need to wrap lambda functions in weak methods to assure
        # that this class is destroyed. Since carb events run through
        # C++ the reference counting on python objects is lost.
        # This works around that problem.

        on_update_fcn = XRWeakMethod(self._on_update)
        xr_profile_changed_fcn = XRWeakMethod(self._xr_profile_changed)

        xr_viewport_enabled_fcn = XRWeakMethod(self._xr_viewport_enabled)
        xr_viewport_disabled_fcn = XRWeakMethod(self._xr_viewport_disabled)
        xr_system_changed_fcn = XRWeakMethod(self._xr_system_changed)

        xr_enabled_fcn = XRWeakMethod(self._xr_enabled)
        xr_disabled_fcn = XRWeakMethod(self._xr_disabled)

        xr_anchor_reset_fcn = XRWeakMethod(self._xr_anchor_reset)

        xr_stage_open_fcn = XRWeakMethod(self._stage_open)
        xr_stage_close_fcn = XRWeakMethod(self._stage_close)

        usd_context: omni.usd.UsdContext = omni.usd.get_context()
        usd_context_stream: carb.events.IEventStream = usd_context.get_stage_event_stream()

        self.__subs = [
            xr_message_bus.create_subscription_to_pop_by_type(
                XRCoreEventType.system_changed,
                lambda _: xr_system_changed_fcn(),
                name="XR System changed",
            ),
            xr_message_bus.create_subscription_to_pop_by_type(
                XRCoreEventType.pre_sync_update,
                lambda _: on_update_fcn(),
                name="XR PreSync Update",
            ),
            xr_message_bus.create_subscription_to_pop_by_type(
                XRCoreEventType.profile_changed,
                lambda _: xr_profile_changed_fcn(),
                name="XR Profile Updated",
            ),
            xr_message_bus.create_subscription_to_pop_by_type(
                XRCoreEventType.xr_viewport_enabled,
                lambda _: xr_viewport_enabled_fcn(),
                name="XR Viewport Enabled",
            ),
            xr_message_bus.create_subscription_to_pop_by_type(
                XRCoreEventType.xr_viewport_disabled,
                lambda _: xr_viewport_disabled_fcn(),
                name="XR Viewport Disabled",
            ),
            xr_message_bus.create_subscription_to_pop_by_type(
                XRCoreEventType.xr_enabled,
                lambda _: xr_enabled_fcn(),
                name="XR Enabled",
            ),
            xr_message_bus.create_subscription_to_pop_by_type(
                XRCoreEventType.xr_disabled,
                lambda _: xr_disabled_fcn(),
                name="XR Disabled",
            ),
            usd_context_stream.create_subscription_to_pop_by_type(
                omni.usd.StageEventType.OPENED, lambda _: xr_stage_open_fcn()
            ),
            usd_context_stream.create_subscription_to_pop_by_type(
                omni.usd.StageEventType.CLOSING, lambda _: xr_stage_close_fcn()
            ),
            omni.kit.app.SettingChangeSubscription(XR_ANCHOR_RESET_SETTING, lambda *_: xr_anchor_reset_fcn()),
        ]

        self.__stage_open = False

        self.__xr_profile_subs = []
        self.__xr_profile_name = ""

        self.__anchor_mode = ""
        self.__custom_anchor = ""
        self.__adjust_for_user_height = True

        self.__current_anchor_mode = ""
        self.__current_custom_anchor = ""

        self.__viewport_bound_camera_path = ""

        self.__need_anchor_reset = False

        # resolve what camera is bound at the start of this class
        viewport_bound_camera = self._get_bound_camera_path()
        if viewport_bound_camera != self.__xr_camera_path and len(viewport_bound_camera) > 0:
            self.__viewport_bound_camera_path = str(viewport_bound_camera)
        else:
            self.__viewport_bound_camera_path = "/OmniverseKit_Persp"

        if usd_context.get_stage_state() == omni.usd.StageState.OPENED:
            self._stage_open()

    def _xr_profile_changed(self) -> None:
        """
        When XR profile is changed
        """

        carb.log_info("[XR] Viewport controller detected profile change")
        self._update_xr_profile_monitor()

    def _xr_enabled(self) -> None:
        """
        When XR mode gets enabled
        """

        carb.log_info("[XR] Viewport controller detected xr was enabled")
        self._update_xr_profile_monitor()

    def _xr_disabled(self) -> None:
        """
        When XR mode gets disabled
        """

        carb.log_info("[XR] Viewport controller detected xr was disabled")

        self._remove_xr_profile_monitor()
        self.__enable_reset_anchor = True

    def _stage_open(self) -> None:
        """
        When stage gets opened
        """

        carb.log_info("[XR] Viewport controller detected stage was opened")
        self.__stage_open = True

        self._update_xr_profile_monitor()

        viewport_bound_camera = self._get_bound_camera_path()
        if viewport_bound_camera != self.__xr_camera_path and len(viewport_bound_camera) > 0:
            self.__viewport_bound_camera_path = str(viewport_bound_camera)
        else:
            self.__viewport_bound_camera_path = "/OmniverseKit_Persp"

        if self.__xr_viewport_enabled:
            self._ensure_xr_camera_and_anchor()
            self._force_xr_camera()
            self.__enable_reset_anchor = True

    def _stage_close(self) -> None:
        """
        When stage gets opened
        """

        carb.log_info("[XR] Viewport controller detected stage was closed")
        self.__stage_open = False

        self.__xr_camera_prim = None
        self.__xr_anchor_prim = None
        self.__xr_space_origin_prim = None

        self.__viewport_bound_camera_path = ""

    def _xr_viewport_enabled(self) -> None:
        """
        Called when XR starts displaying
        """

        carb.log_info("[XR] Viewport controller detected xr viewport enabled")
        self.__xr_viewport_enabled = True
        self._disable_scene_ui()
        self._ensure_xr_camera_and_anchor()
        self._force_xr_camera()
        self.__enable_reset_anchor = True

        if self.__need_anchor_reset:
            self._reset_anchor()
            self.__need_anchor_reset = False

    def _xr_viewport_disabled(self) -> None:
        """
        Called when XR stops displaying
        """

        carb.log_info("[XR] Viewport controller detected xr viewport disabled")
        self.__xr_viewport_enabled = False
        self._restore_viewport_camera()
        self._enable_scene_ui()
        self.__enable_reset_anchor = False

    def _xr_system_changed(self) -> None:

        carb.log_info("[XR] Viewport controller detected system change")

        if self.__xr_viewport_enabled is True:
            self._reset_anchor()
        else:
            self.__need_anchor_reset = True

    def _update_xr_profile_monitor(self) -> None:
        """
        For each profile we need to monitor settings
        that tell what the current anchor settings
        are.

        This function registers new callbacks
        """
        if self.__stage_open is False:
            return

        current_xr_profile = self.__xrcore.get_current_xr_profile()

        if current_xr_profile.get_name() != self.__xr_profile_name:
            # We need to register new callbacks
            self.__xr_profile_name = current_xr_profile.get_name()

            if len(self.__xr_profile_name):
                # If profile is an XR profile register callback function
                update_navigation_settings_fcn = XRWeakMethod(self._update_xr_navigation_settings)

                self.__xr_profile_subs = [
                    omni.kit.app.SettingChangeSubscription(
                        current_xr_profile.get_persistent_path() + "anchorMode",
                        lambda *_: update_navigation_settings_fcn(),
                    ),
                    omni.kit.app.SettingChangeSubscription(
                        current_xr_profile.get_scene_persistent_path() + "customAnchor",
                        lambda *_: update_navigation_settings_fcn(),
                    ),
                ]
            else:
                # Clear previous callbacks
                self.__xr_profile_subs = []

        # reset initial state of cached settings
        self._update_xr_navigation_settings()

    def _remove_xr_profile_monitor(self) -> None:
        """
        Stop monitoring settings in the profile
        """
        self.__xr_profile_subs = []

    def _xr_anchor_reset(self) -> None:
        """
        Function called when the requests a reset on the current
        anchor.
        """

        # Check if the user requested a reset
        reset = self.__settings.get(XR_ANCHOR_RESET_SETTING)
        if reset is True:
            # Reset the request
            self.__settings.set(XR_ANCHOR_RESET_SETTING, False)
            # Reset the anchor
            self._reset_anchor()

    def _update_xr_navigation_settings(self):
        """
        Read out settings from settings database.
        """
        self.__anchor_mode = "active camera"
        self.__custom_anchor = ""
        self.__adjust_for_user_height = True

        current_xr_profile = self.__xrcore.get_current_xr_profile()
        if len(current_xr_profile.get_name()):
            # Ensure that there is a default setting
            self.__settings.set_default(current_xr_profile.get_persistent_path() + "anchorMode", "active camera")
            self.__settings.set_default(current_xr_profile.get_scene_persistent_path() + "customAnchor", "")
            self.__settings.set_default(current_xr_profile.get_persistent_path() + "adjustForUserHeight", False)

            # Get latest values
            self.__anchor_mode = self.__settings.get(current_xr_profile.get_persistent_path() + "anchorMode")
            if (
                self.__anchor_mode != "active camera"
                and self.__anchor_mode != "custom anchor"
                and self.__anchor_mode != "scene origin"
            ):
                self.__anchor_mode = "active camera"

            self.__custom_anchor = self.__settings.get(current_xr_profile.get_scene_persistent_path() + "customAnchor")
            self.__adjust_for_user_height = self.__settings.get(
                current_xr_profile.get_persistent_path() + "adjustForUserHeight"
            )

        if self.__anchor_mode != self.__current_anchor_mode or self.__custom_anchor != self.__current_custom_anchor:
            # Only reset the anchor if mode or custom anchor setting was actually changed.
            self.__current_anchor_mode = self.__anchor_mode
            self.__current_custom_anchor = self.__custom_anchor
            self._reset_anchor()

    def _reset_anchor(self):
        """
        Update the anchor -> this should force a reset of the anchor space.
        This function does the following:

            - Determine the new anchor
            - Determine the type of the prim
            - If Camera teleport into scene by casting a ray down to find floor and then updating
                the hit point with the distance from the floor. Then use floor as anchor
                and new pose as camera look at
            - If XForm reset the anchor that links real world with virtual world
        """

        # Figure out the name of the new anchor
        new_anchor = ""
        if self.__anchor_mode == "active camera":
            # Get the cached name of the last active viewport camera
            new_anchor = self._get_viewport_bound_camera()

        elif self.__anchor_mode == "custom anchor":
            # Get the anchor from the cached value of the las t custom anchor that
            # was set for the stage
            new_anchor = self.__custom_anchor

        if new_anchor != "":

            # Grab the prim from usd
            stage = omni.usd.get_context().get_stage()
            if stage is None:
                return

            new_anchor_path = Sdf.Path(new_anchor)
            new_anchor_prim = stage.GetPrimAtPath(new_anchor_path)
            if new_anchor_prim.IsValid():

                # Figure out what to do base on type of prim
                if new_anchor_prim.IsA(UsdGeom.Camera):
                    # It's a camera: we want to use this as a teleport operation

                    # We need to know where to teleport to, this code does a quick teleport
                    # computation

                    # Find the location of the new anchor
                    view_pose = XRCore.get_singleton().get_world_transform_matrix(new_anchor)

                    # We need to know what is up and down. This can change per stage
                    # Get the coordinate system information
                    coordinate_system = self.__xrcore.get_coordinate_system()

                    # find out what the up vector is, is we can cast a ray down to the floor
                    up_vector = coordinate_system.get_up_vector()
                    up_vector = (-up_vector[0], -up_vector[1], -up_vector[2])

                    # define ray pointing to the floor
                    # Ray is no more than 2.5 meters long, beyond that we do not do a teleport
                    ray = XRRay(view_pose.GetRow3(3), up_vector, 0.0, 2.5 / coordinate_system.meters_per_unit)

                    def callback(ray: XRRay, result: XRRayQueryResult):

                        nonlocal new_anchor

                        # On next frame when ray cast is complete
                        if result.valid:

                            # if we hit something

                            # get the prim that should be the new anchor
                            connected_anchor_path = result.get_target_enclosing_model_usd_path()

                            # resolve current height
                            # get the input device of the primary display
                            input_device = self.__xrcore.get_input_device("displayDevice")

                            if input_device is not None:
                                # get pose in physical space
                                pose = input_device.get_pose()

                                # calculate height in stage units
                                height = pose.GetRow3(3)[1] / coordinate_system.meters_per_unit

                                # compute an up vector that has the length of height
                                up_vector = tuple(height * x for x in coordinate_system.get_up_vector())

                                # move the view_pose such that it matched the height of current user
                                # The idea here is that camera is an approximate location and view direction
                                # that we still need to update so your height of the floor is realistic
                                view_pose.SetRow3(3, view_pose.GetRow3(3) + up_vector)

                            # Teleport to the new anchor and ensure that the camera matches view_pose
                            carb.log_info(
                                "[XR] Schedule teleport and match height anchor: "
                                + str(connected_anchor_path)
                                + " pose: "
                                + str(view_pose)
                            )

                            self.__xrcore.schedule_teleport_to_view(connected_anchor_path, view_pose)
                        else:
                            # if there is no floor or camera is floating in space far above the ground,
                            # use the prim that was set

                            if self.__anchor_mode == "active camera":
                                # do not attach to active camera
                                new_anchor = ""

                            carb.log_info(
                                "[XR] Schedule teleport anchor: " + str(new_anchor) + " pose: " + str(view_pose)
                            )

                            self.__xrcore.schedule_teleport_to_view(new_anchor, view_pose)

                    if self.__adjust_for_user_height:
                        self.__xrcore.submit_raycast_query(ray, callback)
                        return
                    else:

                        carb.log_info("[XR] Schedule teleport anchor: " + str(new_anchor) + " pose: " + str(view_pose))
                        self.__xrcore.schedule_teleport_to_view(new_anchor, view_pose)
                        return

        # In any other case:
        #  - prim is not valid
        #  - prim is not a camera
        # We use the chosen prim as the new anchor point and reset the transfrom between
        # anchor and where the camera is
        self.__xrcore.schedule_set_stage_anchor(new_anchor)

    def _on_update(self) -> None:
        """
        Run every frame to force camera to be XR camera if it was changed.
        We also record the selected camera
        """

        if self.__xrcore.is_xr_viewport_enabled() and self.__stage_open is True:

            # Make sure we are using XRCamera and record if was changed
            # in which case we assume that the user wants to reset the anchor
            # to that camera if they are in active camera mode
            self._force_xr_camera()

            # Grab navigation keyboard changes so we can apply them in xr
            keyboard_translation, mouse_yaw_pitch = self._get_keyboard_mouse_inputs()

            # Apply the changes
            self.__xrcore.schedule_apply_viewport_navigation(
                keyboard_translation[0],
                keyboard_translation[1],
                keyboard_translation[2],
                mouse_yaw_pitch[0],
                mouse_yaw_pitch[1],
            )

    def _ensure_xr_camera_and_anchor(self) -> None:
        """
        Ensure xrCamera and xrAnchor are created.
        Normally these are made by the C++ code, in
        case that fails they are generated here
        """

        carb.log_info("[XR] Ensure xr_camera and xr_anchor are present")

        # Get the current stage
        stage = self.__viewport_api.stage
        if not stage:
            return

        # XR prims are all on the session layer
        session_layer = stage.GetSessionLayer()
        if not session_layer:
            return

        # Check if the camera prim is non existant or invalid
        if self.__xr_camera_prim is None or not self.__xr_camera_prim.GetPrim().IsValid():
            camera_prim = stage.GetPrimAtPath(self.__xr_camera_path)
            if not camera_prim.IsValid():
                # Create the prim
                with Usd.EditContext(stage, Usd.EditTarget(session_layer)):
                    self.__xr_camera_prim = UsdGeom.Camera.Define(stage, self.__xr_camera_path)
                    # We assume it just needs a transform
                    self.__xr_camera_prim.AddTransformOp()

                    # Initialize to identity matrix
                    transform_stack = self.__xr_camera_prim.GetOrderedXformOps()
                    transform_stack[0].Set(Gf.Matrix4d().SetIdentity())

        # Check if the anchor prim is non existant or invalid
        if self.__xr_anchor_prim is None or not self.__xr_anchor_prim.GetPrim().IsValid():
            anchor_prim = stage.GetPrimAtPath(self.__xr_anchor_path)
            if not anchor_prim.IsValid():
                with Usd.EditContext(stage, Usd.EditTarget(session_layer)):
                    self.__xr_anchor_prim = UsdGeom.Xform.Define(stage, self.__xr_anchor_path)
                    self.__xr_anchor_prim.AddTransformOp()

                    transform_stack = self.__xr_anchor_prim.GetOrderedXformOps()
                    transform_stack[0].Set(Gf.Matrix4d().SetIdentity())

        # Check if the anchor prim is non existant or invalid
        if self.__xr_space_origin_prim is None or not self.__xr_space_origin_prim.GetPrim().IsValid():
            space_origin_prim = stage.GetPrimAtPath(self.__xr_space_origin_path)
            if not space_origin_prim.IsValid():
                with Usd.EditContext(stage, Usd.EditTarget(session_layer)):
                    self.__xr_space_origin_prim = UsdGeom.Xform.Define(stage, self.__xr_space_origin_path)
                    self.__xr_space_origin_prim.AddTransformOp()

                    transform_stack = self.__xr_space_origin_prim.GetOrderedXformOps()
                    transform_stack[0].Set(Gf.Matrix4d().SetIdentity())

    def _get_bound_camera_path(self) -> str:
        """
        Get the path of the bound camera
        """

        # Currently most up to date camera must be grabbed from the viewport_api
        return str(self.__viewport_api.camera_path)

    def _set_bound_camera_path(self, bound_camera_path: str) -> None:
        """
        Set which camera is bound
        """

        # Note: Ideally we do this with the kit command
        # But kit command saves edits on the root layer instead of the session layer
        # Storing xrCamera path in root layer seems wrong as the xrCamera does
        # not exist in the usd file itself
        # Hence this code below just does the same as the command.
        #
        # This seems an issue in kit that needs to be fixed. The logic should be that
        # cameras that only exist on the session layer, only override stage metadata
        # on the session layer and not in the root layer.
        #
        # Note: Once the code in the kit gets updated to run multiple viewports
        # (currently broken) this code needs to be updated too

        carb.log_info("[XR] Set bound camera path " + str(bound_camera_path))

        stage = self.__viewport_api.stage
        if not stage:
            return

        session_layer = stage.GetSessionLayer()
        if not session_layer:
            return

        # Set current camera in the viewport api

        self.__viewport_api.camera_path = bound_camera_path

        # Set current camera in the usd metadata of the session layer
        with Usd.EditContext(stage, Usd.EditTarget(session_layer)):
            stage.SetMetadataByDictKey("customLayerData", "cameraSettings:boundCamera", bound_camera_path)

    def _clear_bound_camera_path(self, prev_bound_camera_path: str) -> None:
        """
        Clear the override in the usd session layer and restore usd property
        to old value. Also restore the previous bound camera in the
        viewport class.
        """

        # Exiting XR mode will delete the XRCamera, and we need to set the boundCamera again
        # However last time we did the edits it was on the session layer and not on the
        # root layer. Hence we delete the property on the session layer and then rewrite
        # the right value on the root layer, to get back in the old mode

        stage = self.__viewport_api.stage
        if not stage:
            return

        session_layer = stage.GetSessionLayer()
        if not session_layer:
            return

        # Our camera edits in usd are only on the session layer, so other user are not
        # affected
        with Usd.EditContext(stage, Usd.EditTarget(session_layer)):
            stage.ClearMetadataByDictKey("customLayerData", "cameraSettings:boundCamera")

        root_layer = stage.GetRootLayer()
        if not root_layer:
            return

        # Default camera is set on the root layer, so reset it there
        # TODO: This is what current viewport code seems to do, which is odd
        # as one would expect it on the session layer, so shared stages can have
        # different cameras.
        # Maybe use session_layer here to do the right thing
        with Usd.EditContext(stage, Usd.EditTarget(root_layer)):
            stage.SetMetadataByDictKey("customLayerData", "cameraSettings:boundCamera", prev_bound_camera_path)

        self.__viewport_api.camera_path = prev_bound_camera_path

    def _set_viewport_bound_camera(self, viewport_bound_camera: str) -> None:
        """
        Whenever the viewport camera is set we want to track it. As we can use it to update the
        XRCamera
        """

        # NOTE: There is no comparison to see if that camera is already bound
        # This ensures that when you change the camera in the menu to the same one
        # as before it will do a reset of the anchor

        carb.log_info("[XR] Set viewport bound camera " + str(viewport_bound_camera))

        self.__viewport_bound_camera_path = str(viewport_bound_camera)
        if XRCore.get_singleton().is_xr_viewport_enabled():
            if self.__anchor_mode == "active camera" and self.__enable_reset_anchor is True:
                # If anchor is tracking active camera, reset the anchor
                self._reset_anchor()

    def _get_viewport_bound_camera(self) -> str:
        """
        Get the last camera set in the viewport
        """

        if self.__viewport_bound_camera_path == self.__xr_camera_path:
            return "/OmniverseKit_Persp"
        return self.__viewport_bound_camera_path

    def _force_xr_camera(self) -> None:
        """
        On every frame that we run XR, we make sure camera is forced to be XRCamera
        """

        # Get the current camera
        current_bound_camera_path = self._get_bound_camera_path()

        # Check if camera is the xrCamera
        if current_bound_camera_path != self.__xr_camera_path:
            # Force camera back into xrCamera, we don't want to
            # edit any of the none xrCameras
            self._set_bound_camera_path(self.__xr_camera_path)

            # Record the camera the user selected
            self._set_viewport_bound_camera(current_bound_camera_path)

    def _restore_viewport_camera(self) -> None:
        """
        Restore the camera after exiting XR mode
        """

        viewport_bound_camera = self._get_viewport_bound_camera()
        self._clear_bound_camera_path(viewport_bound_camera)

    def _disable_scene_ui(self) -> None:
        """
        Disable all viewport manipulators and scene ui elements that are incompatible with XR

        Currently, these ui elements include:
        - The prim transform manipulator that appears on prim selection
        - The grid ui
        - The prim bounding box that appears on prim selection
        """
        # TODO: enabling external camera updates doesn't really work as I expected.
        # The expectation is that calling this should ensure that the new viewport scene ui manipulators
        # all render correctly as the _on_update code path updates the USD camera transform.
        # camera_manipulation_model = get_camera_manipulation_model(self.viewport_window)
        # enable_external_camera_updates(camera_manipulation_model)
        # Disable the prim transform manipulator and the grid ui
        #
        # NOTE: How did I discover these magical string values?
        # With the `print_all_viewport_layers` function defined below!
        self._disabled_layers = [
            viewport_utils._DisableViewportWindowLayer(self.__viewport_window, [("Prim Transform", "manipulator")])
        ]

    def _enable_scene_ui(self) -> None:
        """
        Reenable all viewport manipulators and scene ui
        """
        self._disabled_layers = []

    def _get_camera_manipulation_model(self) -> CameraManipulatorModel:
        """
        Returns the ViewportCameraManipulator CameraManipulationModel for `viewport_window`.
        """
        # TODO: Determine a better way to access the CameraManipulatorModel or consider filing an MR against Kit
        # to add an actual API. The below code was copied directly from
        # https://gitlab-master.nvidia.com/omniverse/kit/-/blob/307e18a97dbee4540ff3cbafb8671f5ce036cb4a/kit/source/extensions/omni.kit.viewport.window/omni/kit/viewport/window/window.py#L328-337
        viewport_window_name = self.__viewport_window.name
        cam_manipulator_item = self.__viewport_window._find_viewport_layer("Camera", "manipulator")
        if cam_manipulator_item is None:
            carb.log_warn(f"cam_manipulator_item for {viewport_window_name} is unexpectedly None")
        cam_manipulator_layer = getattr(cam_manipulator_item, "layer", None)
        if cam_manipulator_layer is None:
            carb.log_warn(f"cam_manipulator_layer for {viewport_window_name} is unexpectedly None")
        cam_manipulator: ViewportCameraManipulator = getattr(cam_manipulator_layer, "manipulator", None)
        if cam_manipulator is None:
            carb.log_warn(f"cam_manipulator for {viewport_window_name} is unexpectedly None")
        model: CameraManipulatorModel = cam_manipulator.model
        return model

    def _get_keyboard_mouse_inputs(self) -> Tuple[Gf.Vec3d, Gf.Vec3d]:
        """
        Extracts the keyboard and mouse navigation values from the last frame from `model`

        Returns the tuple (translation, rotation), where:

        - The translation vector is in world space, units in cm
        - The rotation vector corresponds to (yaw, pitch, 0), units in radians, where yaw is rotation about the up axis and pitch is rotation about the over axis
        """
        # NOTE: LATENCY WARNING. Using the last_applied value likely introduces at least one frame of latency
        # for keyboard + mouse navigation inputs.
        #
        # NOTE: Why does the below code use __last_applied rather than model._CameraManipulatorModel__{fly/look/move} directly?
        # In practice, I found that the direct values aren't set reliably (look for example is always None or an empty array)
        # or aren't scaled by the correct speed values (fly).
        #
        # TODO: Determine a better way to access keyboard + mouse navigational inputs.
        # This may require an MR to Kit to add the necessary API. See https://nvidia-omniverse.atlassian.net/browse/OM-85010

        model: CameraManipulatorModel = self._get_camera_manipulation_model()
        last: ModelState = model._CameraManipulatorModel__last_applied
        translation = Gf.Vec3d(0, 0, 0)
        yawPitch = Gf.Vec3d(0, 0, 0)
        if last is not None:
            # Only apply lastFly if the current fly value is populated
            # Temporary work around for https://nvidia-omniverse.atlassian.net/browse/OM-90140
            lastFly = None
            fly = model.get_as_floats(model._CameraManipulatorModel__fly)
            isFlyPopulated = fly and not (fly[0] == 0 and fly[1] == 0 and fly[2] == 0)
            if isFlyPopulated:
                lastFly = last.fly or last.move
            # Translate the on both keyboard fly and mouse move events
            translation = lastFly or translation
            yawPitch = last.look or yawPitch

        yawPitch[0] = math.radians(yawPitch[0])
        yawPitch[1] = -math.radians(yawPitch[1])
        return (translation, yawPitch)

    def print_all_viewport_layers(viewport_window: ViewportWindow):
        """
        Utility function to recursively print all viewport layers of a `viewport_window`
        Useful to discover name + category pairs for use in viewport_window._find_viewport_layer
        """
        layers = viewport_window._ViewportWindow__viewport_layers

        def print_recursive(viewport_layers):
            for layer in viewport_layers:
                print(layer)
                if hasattr(layer, "name"):
                    print(f" - name: {layer.name}")
                if hasattr(layer, "categories"):
                    print(f" - categories: {layer.categories}")
                if hasattr(layer, "layers"):
                    print_recursive(layer.layers)

        print_recursive(layers.layers)
