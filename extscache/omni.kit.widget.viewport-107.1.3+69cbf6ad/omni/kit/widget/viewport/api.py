# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["ViewportAPI"]

import asyncio
import contextlib
from typing import Callable, Optional, Sequence, Tuple, Union
import weakref

import carb
import omni.usd
from pxr import Usd, UsdGeom, Sdf, Gf, CameraUtil

from .impl.utility import _report_error
from .capture import Capture


class ViewportAPI():
    class __ViewportSubscription:
        def __init__(self, fn: Callable, callback_container: set):
            self.__callback_container = callback_container
            self.__callback = fn
            self.__callback_container.add(self.__callback)

        def destroy(self):
            if not self.__callback_container:
                return
            # Clear out self of references early, and then operate on the re-scoped objects
            scoped_container = self.__callback_container
            scoped_callback = self.__callback
            self.__callback_container, self.__callback = None, None
            with contextlib.suppress(KeyError):
                scoped_container.remove(scoped_callback)

        def __del__(self):
            self.destroy()

    def __init__(self, usd_context_name: str, viewport_id: str, viewport_changed_fn: Optional[Callable]):
        self.__usd_context_name = usd_context_name
        self.__viewport_id = viewport_id
        self.__viewport_changed = viewport_changed_fn
        self.__viewport_texture, self.__hydra_texture = None, None
        self.__aspect_ratios = (1, 1)
        self.__projection = Gf.Matrix4d(1)
        self.__flat_rendered_projection = self.__flatten_matrix(self.__projection)
        self.__transform = Gf.Matrix4d(1)
        self.__view = Gf.Matrix4d(1)
        self.__ndc_to_world = None
        self.__world_to_ndc = None
        self.__time = Usd.TimeCode.Default()
        self.__view_changed = set()
        self.__frame_changed = set()
        self.__render_settings_changed = set()
        self.__fill_frame = False
        self.__lock_to_render_result = True
        self.__first_synch = True
        self.__updates_enabled = True
        self.__freeze_frame = False
        self.__scene_views = []

        # This stores the instance of SceneCameraModel if it's required and successfully imported.
        # We initialize it to None as we don't need it immediately at initialization time.
        self.__scene_camera_model = None

        settings = carb.settings.get_settings()
        self.__accelerate_rtx_picking = bool(settings.get("/exts/omni.kit.widget.viewport/picking/rtx/accelerate"))
        self.__accelerate_rtx_picking_sub = settings.subscribe_to_node_change_events(
            "/exts/omni.kit.widget.viewport/picking/rtx/accelerate", self.__accelerate_rtx_changed
        )

    def __del__(self):
        sub, self.__accelerate_rtx_picking_sub = self.__accelerate_rtx_picking_sub, None
        if sub:
            carb.settings.get_settings().unsubscribe_to_change_events(sub)

    def add_scene_view(self, scene_view):
        """
        Add an omni.ui.scene.SceneView to push view and projection changes to.
        The provided scene_view will be saved as a weak-ref.

        Args:
            scene_view (omni.ui.scene.SceneView): The scene_view to add into this Viewport
        """
        if not scene_view:  # pragma: no cover
            raise RuntimeError('Provided scene_view is invalid')
        self.__clean_weak_views()
        self.__scene_views.append(weakref.ref(scene_view, self.__clean_weak_views))

        # Only ever try this once, for now extension musg be loaded before first scene added
        if self.__scene_camera_model is None:
            self.__scene_camera_model = False
            # Check if setting is enabled (if enabled it is assumed the extension is loaded as well)
            if carb.settings.get_settings().get("/exts/omni.kit.widget.viewport/sceneView/singleCameraModel/enabled"):
                try:
                    from omni.kit.viewport.scene_camera_model import SceneCameraModel
                    self.__scene_camera_model = SceneCameraModel(self.__usd_context_name, self.frame_info.get("viewport_handle", -1))
                except ImportError:
                    carb.log_error("omni.kit.viewport.scene_camera_model must be enabled for singleCameraModel")

        # Assign the SceneCameraModel if it exists
        sc_cam_model = self.__scene_camera_model
        if sc_cam_model:
            scene_view.model = sc_cam_model

        # Sync the model immediately
        model = scene_view.model
        model.set_floats('view', self.__flatten_matrix(self.__view))
        model.set_floats('projection', self.__flatten_matrix(self.__projection))

    def remove_scene_view(self, scene_view):
        """
        Remove an omni.ui.scene.SceneView that was receiving view and projection changes.

        Args:
            scene_view (omni.ui.scene.SceneView): The scene_view to add into this Viewport
        """
        if not scene_view:
            raise RuntimeError('Provided scene_view is invalid')
        for sv in self.__scene_views:
            if sv() == scene_view:
                self.__scene_views.remove(sv)
                break
        self.__clean_weak_views()

    def subscribe_to_view_change(self, callback: Callable):
        """
        Add a function to be called when the camera-view changes.

        Args:
            callback (Callable): The object to invoke when the camera-view changes.
        """
        return self.__subscribe_to_change(callback, self.__view_changed, 'subscribe_to_view_change')

    def subscribe_to_frame_change(self, callback: Callable):
        """
        Add a function to be called when the renderer has delivered a new frame.

        Args:
            callback (Callable): The object to invoke when the renderer has delivered a new frame.
        """
        return self.__subscribe_to_change(callback, self.__frame_changed, 'subscribe_to_frame_change')

    def subscribe_to_render_settings_change(self, callback: Callable):
        """
        Add a function to be called when the renderer's setting have changed (such as resolution, renderer in use)

        Args:
            callback (Callable): The object to invoke when the renderer's setting have changed.
        """
        return self.__subscribe_to_change(callback, self.__render_settings_changed, 'subscribe_to_render_settings_change')

    def request_pick(self, *args, **kwargs):
        """
        Request a pick in the Viewport.

        Args:
            top_left (Tuple[int, int]): Top left corner for the pick (in pixel coordinates).
            bottom_right (Tuple[int, int]): Bottom right corner for the pick (in pixel coordinates).
            mode (omni.usd.PickingMode): The mode that wil effect the selection when the pick completes.
        """
        return self.__hydra_texture.request_pick(*args, **kwargs) if self.__hydra_texture else None

    def request_query(self, *args, **kwargs):
        """
        Request a query into the world the Viewport is rendering.

        Args:
            pixel (Tuple[int, int]): The pixel to query the scene from
            callback (Callable): Object to invoke when the query completes.
                def on_query_complete(prim_path: str, world_pos: Tuple[float, float, float], viewport_api)
            query_name (str): Give the name a query so it can be replaced/updated with a new one before completed.
        """
        if self.__accelerate_rtx_picking and kwargs.get("view") is None:
            # If using scene_camera_model, pull view and projection from that and
            # avoid the flattening stage as well.
            if False:  # self.__scene_camera_model:  # noqa PLW0125
                kwargs["view"] = self.__scene_camera_model.view
                kwargs["projection"] = self.__scene_camera_model.projection
            else:
                kwargs["view"] = self.__flatten_matrix(self.__view)
                kwargs["projection"] = self.__flat_rendered_projection

        return self.__hydra_texture.request_query(*args, **kwargs) if self.__hydra_texture else None

    def schedule_capture(self, delegate: Capture) -> Capture:
        """
        Schedule a capture of the rendered output

        Args:
            delegate (Capture): The object to invoke when the capture has completed.
        """
        return self.__viewport_texture.schedule_capture(delegate) if self.__viewport_texture else None

    async def wait_for_render_settings_change(self):
        future = asyncio.Future()

        def rs_changed(*args):
            nonlocal scoped_sub
            scoped_sub = None
            if not future.done():
                future.set_result(True)

        scoped_sub = self.subscribe_to_render_settings_change(rs_changed)
        return await future

    async def wait_for_rendered_frames(self, additional_frames: int = 0):
        future = asyncio.Future()

        def frame_changed(*args):
            nonlocal additional_frames, scoped_sub
            additional_frames = additional_frames - 1
            if (additional_frames <= 0) and (not future.done()):
                future.set_result(True)
                scoped_sub = None

        scoped_sub = self.subscribe_to_frame_change(frame_changed)
        return await future

    # Deprecated
    def pick(self, *args, **kwargs):  # pragma: no cover
        carb.log_warn('ViewportAPI.pick is deprecated, use request_pick')
        return self.__hydra_texture.pick(*args, **kwargs) if self.__hydra_texture else None

    def query(self, mouse, *args, **kwargs):  # pragma: no cover
        carb.log_warn('ViewportAPI.query is deprecated, use request_query')
        return self.__hydra_texture.query(mouse, *args, **kwargs) if self.__hydra_texture else None

    def set_updates_enabled(self, enabled: bool = True):  # pragma: no cover
        carb.log_warn('ViewportAPI.set_updates_enabled is deprecated, use updates_enabled')
        self.updates_enabled = enabled

    @property
    def hydra_engine(self):
        """Get the name of the active omni.hydra.engine for this Viewport"""
        return self.__viewport_texture.hydra_engine if self.__viewport_texture else None

    @hydra_engine.setter
    def hydra_engine(self, hd_engine: str):
        """Set the name of the active omni.hydra.engine for this Viewport"""
        if self.__viewport_texture:
            self.__viewport_texture.hydra_engine = hd_engine

    @property
    def render_mode(self):
        """Get the render-mode for the active omni.hydra.engine used in this Viewport"""
        return self.__viewport_texture.render_mode if self.__viewport_texture else None

    @render_mode.setter
    def render_mode(self, render_mode: str):
        """Set the render-mode for the active omni.hydra.engine used in this Viewport"""
        if self.__viewport_texture:
            self.__viewport_texture.render_mode = render_mode

    @property
    def set_hd_engine(self):
        """Set the active omni.hydra.engine for this Viewport, and optionally its render-mode"""
        return self.__viewport_texture.set_hd_engine if self.__viewport_texture else None

    @property
    def camera_path(self) -> Sdf.Path:
        """Return an Sdf.Path to the active rendering camera"""
        return self.__viewport_texture.camera_path if self.__viewport_texture else None

    @camera_path.setter
    def camera_path(self, camera_path: Union[Sdf.Path, str]):
        """Set the active rendering camera from an Sdf.Path"""
        if self.__viewport_texture:
            self.__viewport_texture.camera_path = camera_path

    @property
    def resolution(self) -> Tuple[float, float]:
        """Return a tuple of (resolution_x, resolution_y) this Viewport is rendering at, accounting for scale."""
        return self.__viewport_texture.resolution if self.__viewport_texture else None

    @resolution.setter
    def resolution(self, value: Tuple[float, float]):
        """Set the resolution to render with (resolution_x, resolution_y).
        The provided resolution should be full resolution, as any texture scaling will be applied to it."""
        if self.__viewport_texture:
            self.__viewport_texture.resolution = value

    @property
    def resolution_scale(self) -> float:
        """Get the scaling factor for the Viewport's render resolution."""
        return self.__viewport_texture.resolution_scale if self.__viewport_texture else None

    @resolution_scale.setter
    def resolution_scale(self, value: float):
        """Set the scaling factor for the Viewport's render resolution."""
        if self.__viewport_texture:
            self.__viewport_texture.resolution_scale = value

    @property
    def full_resolution(self) -> Tuple[float, float]:
        """Return a tuple of the full (full_resolution_x, full_resolution_y) this Viewport is rendering at, not accounting for scale."""
        return self.__viewport_texture.full_resolution if self.__viewport_texture else None

    @property
    def render_product_path(self) -> str:
        """Return a string to the UsdRender.Product used by the Viewport"""
        return self.__hydra_texture.get_render_product_path() if self.__hydra_texture else None

    @render_product_path.setter
    def render_product_path(self, prim_path: str):
        """Set the UsdRender.Product used by the Viewport with a string"""
        return self.__hydra_texture.set_render_product_path(prim_path) if self.__hydra_texture else None

    def set_render_product_path(self, *args, **kwargs):
        """Set the UsdRender.Product used by the Viewport with a string and optional arguments"""
        return self.__hydra_texture.set_render_product_path(*args, **kwargs) if self.__hydra_texture else None

    @property
    def fps(self) -> float:
        """Return the frames-per-second this Viewport is running at"""
        return self.frame_info.get("fps", 0)

    @property
    def frame_info(self) -> dict:
        return self.__viewport_texture.frame_info if self.__viewport_texture else {}

    @property
    def fill_frame(self) -> bool:
        return self.__fill_frame

    @fill_frame.setter
    def fill_frame(self, value: bool):
        value = bool(value)
        if self.__fill_frame != value:
            self.__fill_frame = value
            stage = self.stage
            if stage:
                self.viewport_changed(self.camera_path, stage)

    @property
    def lock_to_render_result(self) -> bool:
        return self.__lock_to_render_result

    @lock_to_render_result.setter
    def lock_to_render_result(self, value: bool):
        value = bool(value)
        if self.__lock_to_render_result != value:
            self.__lock_to_render_result = value
            if self.__viewport_texture:
                self.__viewport_texture._render_settings_changed() # noqa PLW0212

    @property
    def freeze_frame(self) -> bool:
        return self.__freeze_frame

    @freeze_frame.setter
    def freeze_frame(self, value: bool):
        self.__freeze_frame = bool(value)

    @property
    def updates_enabled(self) -> bool:
        return self.__updates_enabled

    @updates_enabled.setter
    def updates_enabled(self, value: bool):
        value = bool(value)
        if self.__updates_enabled != value:
            self.__updates_enabled = value
            if self.__hydra_texture:
                self.__hydra_texture.set_updates_enabled(value)

    @property
    def viewport_changed(self):
        return self.__viewport_changed if self.__viewport_changed else lambda c, s: None

    @property
    def id(self) -> str: # noqa A003
        return self.__viewport_id

    @property
    def usd_context_name(self) -> str:
        """Return the name of the omni.usd.UsdContext this Viewport is attached to"""
        return self.__usd_context_name

    @property
    def usd_context(self):
        """Return the omni.usd.UsdContext this Viewport is attached to"""
        return omni.usd.get_context(self.__usd_context_name)

    @property
    def stage(self) -> Usd.Stage:
        """Return the Usd.Stage of the omni.usd.UsdContext this Viewport is attached to"""
        return self.usd_context.get_stage()

    @property
    def projection(self) -> Gf.Matrix4d:
        """Return the projection of the UsdCamera in terms of the ui element it sits in."""
        return Gf.Matrix4d(self.__projection)

    @property
    def transform(self) -> Gf.Matrix4d:
        """Return the world-space transform of the UsdGeom.Camera being used to render"""
        return Gf.Matrix4d(self.__transform)

    @property
    def view(self) -> Gf.Matrix4d:
        """Return the inverse of the world-space transform of the UsdGeom.Camera being used to render"""
        return Gf.Matrix4d(self.__view)

    @property
    def time(self) -> Usd.TimeCode:
        """Return the Usd.TimeCode this Viewport is using"""
        return self.__time

    @property
    def world_to_ndc(self) -> Gf.Matrix4d:
        if not self.__world_to_ndc:
            self.__world_to_ndc = self.view * self.projection
        return Gf.Matrix4d(self.__world_to_ndc)

    @property
    def ndc_to_world(self) -> Gf.Matrix4d:
        if not self.__ndc_to_world:
            self.__ndc_to_world = self.world_to_ndc.GetInverse()
        return Gf.Matrix4d(self.__ndc_to_world)

    def map_ndc_to_texture(self, mouse: Sequence[float]) -> Tuple[Tuple[float, float], "ViewportAPI"]:
        ratios = self.__aspect_ratios
        # Move into viewport's NDC-space: [-1, 1] bound by viewport
        mouse = (mouse[0] / ratios[0], mouse[1] / ratios[1])
        # Move from NDC space to texture-space [-1, 1] to [0, 1]

        def check_bounds(idx):
            coord = mouse[idx]
            return coord >= -1 and coord <= 1

        return tuple((x + 1.0) * 0.5 for x in mouse), self if (check_bounds(0) and check_bounds(1)) else None

    def map_ndc_to_texture_pixel(self, mouse: Sequence[float]) -> Tuple[Tuple[float, float], "ViewportAPI"]:
        # Move into viewport's uv-space: [0, 1]
        mouse, viewport = self.map_ndc_to_texture(mouse)
        # Then scale by resolution flipping-y
        resolution = self.resolution
        return (int(mouse[0] * resolution[0]), int((1.0 - mouse[1]) * resolution[1])), viewport

    def __get_conform_policy(self):
        """
        TODO: Need python exposure via UsdContext or HydraTexture
        import carb
        conform_setting = carb.settings.get_settings().get("/app/hydra/aperture/conform")
        if (conform_setting is None) or (conform_setting == 1) or (conform_setting == "horizontal"):
            return CameraUtil.MatchHorizontally
        if (conform_setting == 0) or (conform_setting == "vertical"):
            return CameraUtil.MatchVertically
        if (conform_setting == 2) or (conform_setting == "fit"):
            return CameraUtil.Fit
        if (conform_setting == 3) or (conform_setting == "crop"):
            return CameraUtil.Crop
        if (conform_setting == 4) or (conform_setting == "stretch"):
            return CameraUtil.DontConform
        """
        return CameraUtil.MatchHorizontally

    def _conform_projection(self, policy, camera: UsdGeom.Camera, image_aspect: float, canvas_aspect: float, projection: Sequence[float] = None):
        """
        For the given camera (or possible incoming projection) return a projection matrix that matches the rendered image
        but keeps NDC co-ordinates for the texture bound to [-1, 1]
        """
        if projection is None:
            # If no projection is provided, conform the camera based on settings
            # This wil adjust apertures on the gf_camera
            gf_camera = camera.GetCamera(self.__time)
            if policy == CameraUtil.DontConform:
                # For DontConform, still have to conform for the final canvas
                if image_aspect < canvas_aspect:
                    gf_camera.horizontalAperture = gf_camera.horizontalAperture * (canvas_aspect / image_aspect)
                else:
                    gf_camera.verticalAperture = gf_camera.verticalAperture * (image_aspect / canvas_aspect)
            else:
                CameraUtil.ConformWindow(gf_camera, policy, image_aspect)

            projection = gf_camera.frustum.ComputeProjectionMatrix()
            self.__flat_rendered_projection = self.__flatten_matrix(projection)
        else:
            self.__flat_rendered_projection = projection
            projection = Gf.Matrix4d(*projection)

        # projection now has the rendered image projection
        # Conform again based on canvas size so projection extends with the Viewport sits in the UI
        if image_aspect < canvas_aspect:
            self.__aspect_ratios = (image_aspect / canvas_aspect, 1)
            policy2 = CameraUtil.MatchVertically
        else:
            self.__aspect_ratios = (1, canvas_aspect / image_aspect)
            policy2 = CameraUtil.MatchHorizontally

        if policy != CameraUtil.DontConform:
            projection = CameraUtil.ConformedWindow(projection, policy2, canvas_aspect)

        return projection

    def _sync_viewport_api(self, camera: UsdGeom.Camera, canvas_size: Sequence[int],
                           time: Usd.TimeCode | None = None,
                           view: Sequence[float] = None, projection: Sequence[float] = None,
                           force_update: bool = False):
        """Sync the ui and viewport state, and inform any view-scubscribers if a change occured"""

        # Early exit if the Viewport is locked to a rendered image, not updates to SceneViews or internal state
        if not self.__updates_enabled or self.__freeze_frame:
            return False
        # Store the current time
        self.__time = time if time is not None else Usd.TimeCode.Default()
        # When locking to render, allow one update to push initial USD state into Viewport
        # Otherwise, if locking to render results and no View provided, wait for next frame to deliver it.
        if self.__first_synch:
            self.__first_synch = False
        elif not force_update and (self.__lock_to_render_result and not view):
            return False

        # If forcing UI resolution to match Viewport, set the resolution now if it needs to be updated.
        # Early exit in this case as it will trigger a subsequent UI -> Viewport sync.
        resolution = self.full_resolution or (0, 0)
        canvas_size = (int(canvas_size[0]), int(canvas_size[1]))
        # We want to be careful not to resize to 0, 0 in the case the canvas is 0, 0
        if self.__fill_frame and (canvas_size[0] and canvas_size[1]): # noqa SIM102
            if (resolution[0] != canvas_size[0]) or (resolution[1] != canvas_size[1]):
                self.resolution = canvas_size
                return False

        prev_xform, prev_proj = self.__transform, self.__projection
        if view:
            self.__view = Gf.Matrix4d(*view)
            self.__transform = self.__view.GetInverse()
        else:
            self.__transform = camera.ComputeLocalToWorldTransform(self.__time)
            self.__view = self.__transform.GetInverse()

        image_aspect = resolution[0] / resolution[1] if resolution[1] else 1
        canvas_aspect = canvas_size[0] / canvas_size[1] if canvas_size[1] else 1
        policy = self.__get_conform_policy()

        self.__projection = self._conform_projection(policy, camera, image_aspect, canvas_aspect, projection)

        view_changed = self.__transform != prev_xform
        proj_changed = self.__projection != prev_proj
        if view_changed or proj_changed:
            self.__ndc_to_world = None
            self.__world_to_ndc = None
            self.__notify_scene_views(view_changed, proj_changed)
            self.__notify_objects(self.__view_changed)
            return True
        return False

    # Legacy methods that we also support
    def get_active_camera(self) -> Sdf.Path:
        """Deprecated method to return an Sdf.Path to the active rendering camera"""
        return self.camera_path

    def set_active_camera(self, camera_path: Sdf.Path):
        """Deprecated method to set the active rendering camera from an Sdf.Path"""
        self.camera_path = camera_path

    def get_render_product_path(self) -> str:
        """Deprecated method to return a string to the UsdRender.Product used by the Viewport"""
        return self.render_product_path

    def get_texture_resolution(self) -> Tuple[float, float]:
        """Deprecated method to return a tuple of (resolution_x, resolution_y)"""
        return self.resolution

    def set_texture_resolution(self, value: Tuple[float, float]):
        """Deprecated method to set the resolution to render with (resolution_x, resolution_y)"""
        self.resolution = value

    def get_texture_resolution_scale(self) -> float:
        """Get the scaling factor for the Viewport's render resolution."""
        return self.resolution_scale

    def set_texture_resolution_scale(self, value: float):
        """Set the scaling factor for the Viewport's render resolution."""
        self.resolution_scale = value

    def get_full_texture_resolution(self) -> Tuple[float, float]:
        """Return a tuple of (full_resolution_x, full_resolution_y)"""
        return self.full_resolution

    # Semi Private access, do not assume these will always be available by guarding usage and access.
    @property
    def display_render_var(self) -> str | None:
        return self.__viewport_texture.display_render_var if self.__viewport_texture else None

    @display_render_var.setter
    def display_render_var(self, name: str):
        if self.__viewport_texture:
            self.__viewport_texture.display_render_var = str(name)

    @property
    def _settings_path(self) -> str:
        return self.__hydra_texture.get_settings_path() if self.__hydra_texture else None

    @property
    def _hydra_texture(self):
        return self.__hydra_texture

    @property
    def _viewport_texture(self):
        return self.__viewport_texture

    def _notify_frame_change(self):
        self.__notify_objects(self.__frame_changed)

    def _notify_render_settings_change(self):
        self.__notify_objects(self.__render_settings_changed)

    # Very Private methods
    def __set_hydra_texture(self, viewport_texture, hydra_texture):
        # Transfer any local state this instance is carying
        if hydra_texture:
            hydra_texture.set_updates_enabled(self.__updates_enabled)

        sc_cam_model = self.__scene_camera_model
        if sc_cam_model:
            sc_cam_model.set_viewport_handle(self.frame_info.get("viewport_handle", -1))

        # Replace the references this instance has
        self.__viewport_texture = viewport_texture
        self.__hydra_texture = hydra_texture

    def __callback_args(self, fn_container: Sequence):
        # Send a proxy so nobody can retain the instance directly
        vp_api = weakref.proxy(self)
        if id(fn_container) == id(self.__render_settings_changed):
            return (self.camera_path, self.resolution, vp_api)
        return (vp_api,)

    def __subscribe_to_change(self, callback: Callable, container: set, name: str):
        if not callable(callback):
            raise ValueError(f"ViewportAPI {name} requires a callable object")
        # If we're in a valid state, invoke the callback now.
        # If it throws we leave it up to the caller to figure out why and re-subscribe
        if self.__viewport_texture and self.__hydra_texture:
            callback(*self.__callback_args(container))
        return ViewportAPI.__ViewportSubscription(callback, container)

    def __notify_objects(self, fn_container: Sequence):
        if fn_container:
            args = self.__callback_args(fn_container)
            for fn in fn_container.copy():
                try:
                    fn(*args)
                except Exception:  # noqa PLW0718; pragma: no cover
                    _report_error()

    def __notify_scene_views(self, view: bool, proj: bool):
        if not self.__scene_views:
            return
        # Since these are weak-refs, prune any objects that may have gone out of date
        active_views = []
        # Flatten these once for the loop below
        if view:
            view = [self.__view[0][0], self.__view[0][1], self.__view[0][2], self.__view[0][3], self.__view[1][0], self.__view[1][1], self.__view[1][2], self.__view[1][3], self.__view[2][0], self.__view[2][1], self.__view[2][2], self.__view[2][3], self.__view[3][0], self.__view[3][1], self.__view[3][2], self.__view[3][3]]
        if proj:
            proj = [self.__projection[0][0], self.__projection[0][1], self.__projection[0][2], self.__projection[0][3], self.__projection[1][0], self.__projection[1][1], self.__projection[1][2], self.__projection[1][3], self.__projection[2][0], self.__projection[2][1], self.__projection[2][2], self.__projection[2][3], self.__projection[3][0], self.__projection[3][1], self.__projection[3][2], self.__projection[3][3]]

        def update_model(sv_model, view, proj):
            view_item, proj_item = None, None
            if view:
                view_item = sv_model.get_item("view")
                sv_model.set_floats(view_item, view)
            if proj:
                proj_item = sv_model.get_item("projection")
                sv_model.set_floats(proj_item, proj)
            # Update both or just a single item
            sv_model._item_changed(None if (view_item and proj_item) else (view_item or proj_item)) # noqa PLW0212

        # Update the SceneCameraModel once if it exists
        sc_cam_model = self.__scene_camera_model
        if sc_cam_model:
            update_model(sc_cam_model, None, proj)

        for sv_ref in self.__scene_views:
            scene_view = sv_ref()
            if scene_view:
                active_views.append(sv_ref)
                try:
                    sv_model = scene_view.model
                    if sv_model != sc_cam_model:
                        update_model(sv_model, view, proj)
                except Exception:  # noqa PLW0718; pragma: no cover
                    _report_error()
        self.__scene_views = active_views

    def __clean_weak_views(self, *args):
        self.__scene_views = [sv for sv in self.__scene_views if sv()]

    def __accelerate_rtx_changed(self, *args, **kwargs):
        settings = carb.settings.get_settings()
        self.__accelerate_rtx_picking = bool(settings.get("/exts/omni.kit.widget.viewport/picking/rtx/accelerate"))

    @staticmethod
    def __flatten_matrix(m):
        # Pull individual Gf.Vec4 for each row, then index each component of those individually.
        m0, m1, m2, m3 = m[0], m[1], m[2], m[3]
        return [m0[0], m0[1], m0[2], m0[3], m1[0], m1[1], m1[2], m1[3], m2[0], m2[1], m2[2], m2[3], m3[0], m3[1], m3[2], m3[3]]
