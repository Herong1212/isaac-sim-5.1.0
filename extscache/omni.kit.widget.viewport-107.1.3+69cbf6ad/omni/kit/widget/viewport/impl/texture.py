# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["ViewportTexture"]

from typing import Callable, Optional, Sequence
import weakref

import omni.usd
from omni.kit.hydra_texture import create_hydra_texture
import omni.ui
import carb
from pxr import Usd, UsdGeom, Sdf

from ..capture import Capture
from .utility import _init_viewport_cameras, _report_error, _run_viewport_auto_frame


class ViewportTexture:
    __g_hd_texture_counter = 0

    """Backing texture for the Viewport Widget.
       Owner of this object is responsible for calling _on_stage_opened.
    """

    def __init__(self, usd_context_name: Optional[str], camera_path: Optional[str] = None,
                 resolution: Optional[Sequence] = None, hd_engine: Optional[str] = None,
                 hydra_engine_options: Optional[dict] = None,
                 update_api_texture: Optional[Callable] = None):

        # Generate a unique name for the C++ hydra_texture (we avoid . or / for carb dictionary usage)
        self.__hd_texture_name = f"omni_kit_widget_viewport_ViewportTexture_{ViewportTexture.__g_hd_texture_counter}"
        ViewportTexture.__g_hd_texture_counter += 1

        self.__settings = carb.settings.acquire_settings_interface()
        self.__hydra_texture = None

        # Default to color, either LdrColor or HdrColor
        self.__display_var = ""
        self.__render_settings_changed_sub = None
        self.__render_settings_changed_fns = set()
        self.__full_resolution = (0, 0)
        self.__render_resolution = (0, 0)
        self.__resolution_scale = 1.0
        self.__frame_info = {}
        self.__capture_delegates = None
        self.__drawable_changed_fn = None
        self.__drawable_change_sub = None
        self.__update_api_texture = update_api_texture
        self.__hydra_engine_options = hydra_engine_options
        self.__auto_attach: bool = self.__settings.get("/exts/omni.kit.widget.viewport/autoAttach/mode")
        self.__viewport_handle = None

        # UsdContext
        self.__usd_context_name = usd_context_name
        self.__camera_path = Sdf.Path(camera_path) if camera_path else Sdf.Path()

        self.__setup_resolution(resolution, "/app/renderer/resolution")
        self.__current_hd_engine = hd_engine or self.__resolve_default_renderer()

    def destroy(self):
        """
        Called by extension before destroying this object. It doesn't happen automatically.
        Without this hot reloading doesn't work.
        """
        # Remove all subscriptions early
        self.__capture_delegates = None
        self.__drawable_change_sub = None
        self.__render_settings_changed_sub = None
        # self.__hydra_engine_change_sub = None

        self.__set_hd_engine(None, None)
        self.__hydra_texture = None
        self.__settings = None
        self.__hd_texture_name = None
        self.__usd_context_name = None
        self.__render_settings_changed_fns = set()
        self.__frame_info = {}

    @property
    def camera_path(self):
        return self.__camera_path

    @camera_path.setter
    def camera_path(self, path):
        if path:
            path = Sdf.Path(path)
            if self.__camera_path != path:
                if self.__hydra_texture:
                    if self.__validate_camera(path):
                        self.__camera_path = path
                        self.__hydra_texture.set_camera_path(path.pathString)
                else:
                    self.__camera_path = path

    @property
    def resolution(self):
        """Return a tuple of (resolution_x, resolution_y) this Texture is rendering at, accounting for scale."""
        if self.__hydra_texture:
            return (self.__hydra_texture.width, self.__hydra_texture.height)

        return self.__render_resolution

    @resolution.setter
    def resolution(self, resolution):
        if len(resolution) != 2:
            raise ValueError("Resolution must be a sequence of two")

        # Record value requested as full_resolution
        resolution = (int(resolution[0]), int(resolution[1]))
        if self.__full_resolution != resolution:
            self.__full_resolution = resolution

        # Record value requested times factor as render_resolution, clamping to lowest possible 1x1 texture
        resolution = (
            int(max(1, resolution[0] * self.__resolution_scale)),
            int(max(1, resolution[1] * self.__resolution_scale))
        )
        if self.__render_resolution != resolution:
            self.__render_resolution = resolution
            # Set render_resolution to backing texture if it exists
            if self.__hydra_texture:
                self.__hydra_texture.set_width(resolution[0])
                self.__hydra_texture.set_height(resolution[1])

    @property
    def resolution_scale(self) -> float:
        """Get the scaling factor for the Texture's render resolution."""
        return self.__resolution_scale

    @resolution_scale.setter
    def resolution_scale(self, value: float):
        """Set the scaling factor for the Texture's render resolution."""
        # Convert to a float and check that is is above zero.
        value = float(value)
        if self.__resolution_scale == value:
            return
        if value <= 0:
            raise ValueError("Texture resolution scale must be greater than 0.")
        # Save the current full render resolution
        full_resolution = self.__full_resolution
        # Set the new render resolution scale
        self.__resolution_scale = value
        # And set full_resolution back into resolution which will account for new scaling factor.
        self.resolution = full_resolution

    @property
    def full_resolution(self):
        """Return a tuple of the full (full_resolution_x, full_resolution_y) this Texture is rendering at, not accounting for scale."""
        return self.__full_resolution

    @property
    def frame_info(self):
        return self.__frame_info

    @property
    def display_render_var(self):
        return self.__display_var

    @display_render_var.setter
    def display_render_var(self, name: str):
        self.__display_var = str(name)

    @property
    def hydra_engine(self):
        return self.__hydra_texture.get_hydra_engine() if self.__hydra_texture else self.__current_hd_engine

    @property
    def set_hd_engine(self):
        return self.__set_hd_engine

    @property
    def render_mode(self):
        hd_engine = self.hydra_engine
        if hd_engine is not None:
            return self.__settings.get(self.__render_mode_setting(hd_engine))
        return None

    @render_mode.setter
    def render_mode(self, render_mode: str):
        hd_engine = self.hydra_engine
        if hd_engine is not None:
            self.__settings.set_string(self.__render_mode_setting(hd_engine), str(render_mode))

    def _remove_render_settings_changed_fn(self, callback):
        try:
            self.__render_settings_changed_fns.remove(callback)
            if not self.__render_settings_changed_fns:
                self.__render_settings_changed_sub = None
        except KeyError:
            pass

    def _add_render_settings_changed_fn(self, callback=None) -> None:
        if callable(callback):
            self.__render_settings_changed_fns.add(callback)
        # Exit if the texture isn't even set up yet
        if not self.__hydra_texture:
            return
        # If the texture has been set up, we're likely already subscribed to the C++ event
        if self.__render_settings_changed_sub:
            # Already subscribed, call the callback now to sync our current state
            if callback:
                callback(self.__camera_path, self.__render_resolution)
            return

        def render_settings_changed(event: carb.events.IEvent):
            if event.type == omni.hydratexture.EVENT_TYPE_RENDER_SETTINGS_CHANGED:
                resolution = (event.payload["resolution_x"], event.payload["resolution_y"])
                camera_path = event.payload["camera_path"]
                camera_path = Sdf.Path(camera_path) if camera_path else Sdf.Path()
                self.__camera_path = camera_path
                self.__render_resolution = (int(resolution[0]), int(resolution[1]))
                # Update the "viewport_handle" now as it may have changed
                self.__set_viewport_handle(event.payload["viewport_handle"])
                self._render_settings_changed()
            else:
                carb.log_error("Wrong event captured for EVENT_TYPE_RENDER_SETTINGS_CHANGED!")

        self.__render_settings_changed_sub = self.__hydra_texture.get_event_stream().create_subscription_to_push_by_type(
            omni.hydratexture.EVENT_TYPE_RENDER_SETTINGS_CHANGED, render_settings_changed,
            name="Viewport Texture render changed",
        )
        # Call all registered callbacks now to sync the current state
        self._render_settings_changed()

    def _render_settings_changed(self):
        # Call the callbacks, making sure failure in one doesn't stop invocation of the others
        # Cache the current values locally, in case any callback modifies them.
        # This assures consistent mesagge across all callbacks, and any change should be
        # represetend by a subsequent invocation of EVENT_TYPE_RENDER_SETTINGS_CHANGED.
        camera_path, resolution = self.__camera_path, self.__render_resolution
        for callback in self.__render_settings_changed_fns:
            try:
                callback(camera_path, resolution)
            except Exception: # noqa PLW0718
                _report_error()

    def __validate_camera(self, cam_path: Sdf.Path, stage: Usd.Stage = None):
        stage = self.__ensure_usd_stage(stage=stage)
        prim = stage.GetPrimAtPath(cam_path)
        return prim and prim.IsA(UsdGeom.Camera)

    def __render_mode_setting(self, hd_engine: str) -> str:
        return f"/{hd_engine}/rendermode" if hd_engine != "iray" else "/rtx/iray/rendermode"

    def __setup_resolution(self, resolution: Sequence[int], setting_scope: str):
        # Otherwise, pull the resolution from settings
        width_key, height_key = "/width", "/height"
        for name, value in {
            width_key: 1280,
            height_key: 720
        }.items():
            self.__settings.set_default(setting_scope + name, value)

        if not resolution:
            resolution = (
                self.__settings.get(setting_scope + width_key),
                self.__settings.get(setting_scope + height_key)
            )
        self.__resolution_scale = self.__settings.get(setting_scope + "/multiplier") or 1.0
        self.resolution = resolution

    def schedule_capture(self, delegate: Capture) -> Capture:
        if self.__capture_delegates is None:
            self.__capture_delegates = []
        self.__capture_delegates.append(delegate)
        return delegate

    def _on_stage_opened(self, drawable_changed_fn, camera_path: str, first_init: bool):
        """Called when opening a new stage"""
        usd_context = self.__ensure_usd_context()

        prev_cam = self.__camera_path
        stage = usd_context.get_stage()
        if stage:
            # Init the viewport cameras
            implicit_cams, bound_camera = _init_viewport_cameras(stage, self.__settings,
                                                                 self.__usd_context_name, first_init)
            # See if owner has requested a specific Camera
            run_camera_validation = bool(implicit_cams)
            if camera_path:
                camera_path = Sdf.Path(camera_path)
                if camera_path and self.__validate_camera(camera_path):
                    self.__camera_path = camera_path
                    run_camera_validation = False

            if run_camera_validation:
                # If there was bound-camera, try to restore to that camera
                if bound_camera and self.__validate_camera(bound_camera):
                    self.__camera_path = bound_camera
                # Else, use the currently active camera if also valid in new stage
                # Otherwise take the first valid implicit camera found (most likely Perspective)
                elif not self.__validate_camera(prev_cam):
                    for cam_path in implicit_cams:
                        if self.__validate_camera(cam_path):
                            self.__camera_path = cam_path
                            break

            if first_init:
                try:
                    _run_viewport_auto_frame(stage, self.__settings, self.__usd_context_name,
                                             self.__camera_path, implicit_cams, bound_camera,
                                             self.resolution)
                except Exception: # noqa PLW0718
                    _report_error()

        if not self.__hydra_texture:
            self.__set_hd_engine(self.hydra_engine, None, first_init)
            if not self.__hydra_texture:
                # A stage was opened, but creation of the HydraTexture failed.
                # This can happen if the Viewport is created without a renderer, and then a stage was opened.
                # When a valid renderer is finally assigned, make sure to subscribe to its events
                self.__drawable_changed_fn = drawable_changed_fn if drawable_changed_fn else self.__drawable_changed_fn

                # If a renderer was selected then error, otherwise warn
                if self.hydra_engine:
                    carb.log_error(f"Setting hydra_engine to {self.hydra_engine} failed.")
                else:
                    carb.log_warn("Stage opened with no valid renderer selected.")
                return None
            self.__create_subscription_to_drawable_changed(drawable_changed_fn)
        elif prev_cam != self.__camera_path:
            self.__hydra_texture.set_camera_path(self.__camera_path.pathString)

        return weakref.proxy(self.__hydra_texture)

    def __create_subscription_to_drawable_changed(self, callback_fn: Callable = None):
        self.__drawable_changed_fn = callback_fn if callback_fn else self.__drawable_changed_fn

        # We need to react ASAP on the drawable change - so subscribing to PUSH to specific event type
        def on_drawable_changed(event: carb.events.IEvent):
            if event.type != omni.hydratexture.EVENT_TYPE_DRAWABLE_CHANGED:
                carb.log_error("Wrong event captured for DRAWABLE_CHANGED!")
                return

            result_handle = event.payload["result_handle"]
            self.__frame_info = self.__hydra_texture.get_frame_info(result_handle)
            # Store the "viewport_handle" into frame_info
            self.__set_viewport_handle(event.payload["viewport_handle"])
            aov_desc = self.__hydra_texture.get_aov_info(result_handle, aov_name=self.__display_var, include_texture=True)
            # Fallback to color if not found for now
            if not aov_desc and self.__display_var:
                aov_desc = self.__hydra_texture.get_aov_info(result_handle, aov_name="", include_texture=True)
            texture = aov_desc[0]["texture"]

            self.__drawable_changed_fn(texture["rp_resource"], event.payload.get("presentation_key", 0))

            if self.__capture_delegates:
                # Swap the list locally in case anybody tries to re-add durring iteration
                delegates, self.__capture_delegates = self.__capture_delegates, None
                all_aovs = self.__hydra_texture.get_aov_info(result_handle, include_texture=True)
                all_aovs = {aov["name"]: aov for aov in all_aovs}
                frame_info = self.__frame_info.copy()
                for delegate in delegates:
                    try:
                        delegate.capture(all_aovs, frame_info, weakref.proxy(self.__hydra_texture), result_handle)
                    except Exception: # noqa PLW0718
                        _report_error()

        self.__drawable_change_sub = None
        self.__drawable_change_sub = self.__hydra_texture.get_event_stream().create_subscription_to_push_by_type(
            omni.hydratexture.EVENT_TYPE_DRAWABLE_CHANGED,
            on_drawable_changed,
            name="Viewport Texture drawable change",
        )
        return True

    def __enable_hydra_engine(self, hd_engine_name, usd_context):
        if hd_engine_name in usd_context.get_attached_hydra_engine_names():
            return
        omni.usd.create_hydra_engine(hd_engine_name, usd_context)

    def __ensure_usd_context(self, usd_context: omni.usd.UsdContext = None):
        if not usd_context:
            usd_context = omni.usd.get_context(self.__usd_context_name)
            if not usd_context:
                raise RuntimeError(f"omni.usd.UsdContext '{self.__usd_context_name}' does not exist")
        return usd_context

    def __ensure_usd_stage(self, usd_context: omni.usd.UsdContext = None, stage: Usd.Stage = None):
        stage = stage if stage else self.__ensure_usd_context(usd_context).get_stage()
        if stage:
            return stage
        raise RuntimeError(f"omni.usd.UsdContext '{self.__usd_context_name}' has no stage")

    def __allow_hd_engine(self, hd_engine: str, hd_renderer: str | None = None):
        # Sanity check for pxr engine.  Can only have one of them active right now.
        pxr_in_use_key = "/app/viewport/omni_hydra_pxr_in_use"
        pxr_in_use_value = self.__settings.get(pxr_in_use_key) or []

        # If setting contains nothing, then can early exit if not requesting omni.hydra.pxr engine
        if not pxr_in_use_value and (hd_engine != "pxr"):
            return True

        # Need to iterate every value to understand if this is allowed, or the indivdual setting
        # should be cleared (due to a transtition from omni.hydra.pxr) on this instance
        #
        # Each entry in setting should be f'{usd_context_name}':hydra_texture_setting_path
        #
        single_ctx_entry = f"'{self.__usd_context_name}':"
        single_ctx_entry_len = len(single_ctx_entry)
        hd_texture_value = f"/exts/omni.kit.hydra_texture/{self.__hd_texture_name}/"
        full_value_len = single_ctx_entry_len + len(hd_texture_value)
        pxr_engine_requested = hd_engine == "pxr"

        idx = 0
        for in_use in pxr_in_use_value:
            idx = idx + 1
            if not in_use.startswith(single_ctx_entry):
                continue

            # This UsdContext is being used for omni.hydra.pxr
            # Figure out if it is refering to this instance, or transitioning away from omni.hydra.pxr
            # If neither, than this request is blocked
            #
            if (len(in_use) == full_value_len) and (in_use.find(hd_texture_value) == single_ctx_entry_len):
                if not pxr_engine_requested:
                    # index is pre-incremented above, so subtract one to pop this value
                    pxr_in_use_value.pop(idx - 1)
                    self.__settings.set(pxr_in_use_key, pxr_in_use_value)
                return True
            if pxr_engine_requested:
                return False

        # Tag omni.hydra.pxr engine in use for this UsdContext
        pxr_in_use_value.append(single_ctx_entry + hd_texture_value)
        self.__settings.set(pxr_in_use_key, pxr_in_use_value)
        return True

    def __set_hd_engine(self, hd_engine: str, hd_renderer: str | None = None, first_init: bool = False):
        usd_context = omni.usd.get_context(self.__usd_context_name)
        if first_init and (self.__hydra_texture is None):
            if self.__auto_attach:
                # Determine the renderer to auto-attch to (via setting or graceful fallback)
                probably_not_loaded = self.__current_hd_engine is None
                if not bool(hd_engine):
                    # There is a chance render extensions loading was delayed, so re-check if current_hd_engine is empty
                    if probably_not_loaded:
                        rndr_stg = self.__settings.get("/exts/omni.kit.widget.viewport/autoAttach/renderer")
                        self.__current_hd_engine = self.__resolve_default_renderer(rndr_stg, self.__auto_attach == 2)
                    hd_engine = self.__current_hd_engine

                if not bool(hd_engine):
                    (carb.log_warn if probably_not_loaded else carb.log_error)("Viewport is setup to auto-attach, but don't know what renderer to use")
                    return None

                self.__auto_attach = 0
                # Enforce an implicit default camera if user hasn't specified
                if not self.__camera_path:
                    self.__camera_path = Sdf.Path("/OmniverseKit_Persp")
            elif not bool(hd_engine):
                if self.__current_hd_engine is None:
                    self.__current_hd_engine = self.__resolve_default_renderer()
                hd_engine = self.__current_hd_engine

        # Setup the render-mode or query it when not provided (thats what it will be created as)
        if bool(hd_renderer) and bool(hd_engine):
            self.__settings.set_string(self.__render_mode_setting(hd_engine), str(hd_renderer))

        # Early exits for exiting texture that doesn't need a change
        if self.__hydra_texture:
            if not bool(hd_engine):
                # hd_engine might be "", move to None for no-renderer state
                hd_engine = None
                self.__hydra_texture = None
            elif hd_engine != self.__hydra_texture.get_hydra_engine():
                # Engine change, this case will be handled in the conditionals below
                pass
            else:
                # Nothing changed
                return self.__current_hd_engine

        # Check that this engine can be insytantiated properly for the HydraTexture / UsdContext targeted
        if not self.__allow_hd_engine(hd_engine, hd_renderer):
            carb.log_error(f"Additional texture for engine '{hd_engine}' is not currently supported")
            return self.__current_hd_engine

        cur_engine_name = None
        cam_path_str = self.__camera_path.pathString if self.__camera_path else ""
        if hd_engine:
            if not self.__hydra_texture:
                # Enables the engine on the UsdContext if neccessary
                self.__enable_hydra_engine(hd_engine, usd_context)

                hydra_engine_options = self.__hydra_engine_options
                if hydra_engine_options is None:
                    hydra_engine_options = {}
                # Fill in async_rendering and async_low_latency arguments from settings now if not specifed
                if hydra_engine_options.get("is_async") is None:
                    hydra_engine_options["is_async"] = bool(self.__settings.get("/app/asyncRendering"))
                if hydra_engine_options.get("is_async_low_latency") is None:
                    hydra_engine_options["is_async_low_latency"] = bool(self.__settings.get("/app/asyncRenderingLowLatency"))

                self.__hydra_texture = create_hydra_texture(
                    name=self.__hd_texture_name,
                    width=self.__render_resolution[0],
                    height=self.__render_resolution[1],
                    usd_context_name=self.__usd_context_name,
                    usd_camera_path=cam_path_str,
                    hydra_engine_name=hd_engine,
                    **hydra_engine_options
                )

                if self.__hydra_texture:
                    if self.__update_api_texture:
                        self.__update_api_texture(weakref.proxy(self), weakref.proxy(self.__hydra_texture))

                    self._add_render_settings_changed_fn()

                    # Make sure to subscribe to render-output if a stage has been opened, but this is the first
                    # valid renderer attached.
                    if not self.__drawable_change_sub and self.__drawable_changed_fn:
                        self.__create_subscription_to_drawable_changed()
            else:
                if cam_path_str and self.__hydra_texture.get_camera_path() != cam_path_str:
                    self.__hydra_texture.set_camera_path(cam_path_str)
                if self.__hydra_texture.get_hydra_engine() != hd_engine:
                    self.__enable_hydra_engine(hd_engine, usd_context)
                    self.__hydra_texture.set_hydra_engine(hd_engine)
            # We can't query via get_hydra_engine as the change hasn't been applied..assume success for now
            cur_engine_name = hd_engine  # self.__hydra_texture.get_hydra_engine()
        elif self.__hydra_texture:
            # self.__hydra_engine_change_sub = None
            self.__hydra_texture.set_hydra_engine(hd_engine)
            cur_engine_name = None

        if cur_engine_name == hd_engine:
            self.__current_hd_engine = hd_engine

        return self.__current_hd_engine

    def __resolve_default_renderer(self, active: str = None, auto_load: bool = False):
        import omni.kit.app
        ext_manager = omni.kit.app.get_app_interface().get_extension_manager()
        # Check the /renderer/active setting for the default renderer
        active = active or self.__settings.get("/renderer/active")
        enabled_list = self.__settings.get("/renderer/enabled")
        if enabled_list:
            enabled_list = enabled_list.split(",")

        def is_renderer_enabled(renderer: str):
            # If the extension is disabled, then it doesn't matter if it appears in the enabled setting
            renderer_ext = f"omni.hydra.{renderer}"
            ext_enabled = ext_manager.is_extension_enabled(renderer_ext)
            # Need to check self.__allow_hd_engine as /renderer/active may be set to an engine that doesn't support
            # a second Viewport on the same UsdContext and will need to fallback to one that will.
            # If /renderer/enabled is empty, then all enabled renderer extensions are enabled, otherwise must appear in the list
            rndr_enabled = self.__allow_hd_engine(renderer) and (renderer in enabled_list if enabled_list else True)
            # Return a tuple representing whether renderer is enabled in list and extention to enable if so and extension not yet loaded
            return (rndr_enabled, renderer_ext if not ext_enabled else None)

        # Itearate all known renderers, starting with active if set
        renderer_list = ["rtx", "iray", "pxr", "index"]
        if active:
            if active in renderer_list:
                renderer_list.remove(active)
            renderer_list.insert(0, active)

        for renderer in renderer_list:
            rndr_enabled, ext_to_enable = is_renderer_enabled(renderer)
            # Skip over any renderer that is marked as inactive
            if not rndr_enabled:
                continue
            # Check if totally valid (extension enabled and appears in /renderer/enabled)
            if ext_to_enable is None:
                return renderer
            # If auto-load requested, Check if renderer is only not-valid because extension has not yet been enabled
            if auto_load:
                ext_manager.set_extension_enabled_immediate(ext_to_enable, True)
                return renderer

        return None

    def __set_viewport_handle(self, viewport_handle: int):
        self.__frame_info["viewport_handle"] = viewport_handle
        if self.__viewport_handle != viewport_handle:
            self.__viewport_handle = viewport_handle
            if self.__update_api_texture:
                self.__update_api_texture(weakref.proxy(self), weakref.proxy(self.__hydra_texture))
