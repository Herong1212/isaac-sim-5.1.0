# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ['ViewportWidget']

import asyncio
import concurrent.futures
import contextlib
from typing import Optional, Tuple, Union
import weakref

from omni.kit.async_engine import run_coroutine
import omni.ui as ui
import omni.usd
import carb.eventdispatcher
import carb.settings
from pxr import Usd, UsdGeom, Sdf, Tf

from .api import ViewportAPI
from .impl.texture import ViewportTexture
from .impl.utility import init_settings, save_implicit_cameras, StageAxis
from .display_delegate import ViewportDisplayDelegate


class ViewportWidget:
    """
    A low level omni.ui.Widget for displaying rendered output.
    """
    __g_instances = []

    @staticmethod
    def get_instances():
        """Return an iterable object to enumerate all known ViewportWidget instances"""
        yield from ViewportWidget.__g_instances

    @staticmethod
    def __clean_instances(dead, self=None):
        active = []
        for p in ViewportWidget.__g_instances:
            with contextlib.suppress(ReferenceError):
                if p and p != self:
                    active.append(p)
        ViewportWidget.__g_instances = active

    @property
    def viewport_api(self):
        """Return the active omni.kit.widget.viewport.ViewportAPI for the ViewportWidget"""
        return self.__proxy_api

    @property
    def name(self):
        """Return the name of the ViewportWidget"""
        return self.__ui_frame.name

    @property
    def visible(self):
        """Set the visibility of this ViewportWidget"""
        return self.__ui_frame.visible

    @visible.setter
    def visible(self, value) -> bool:
        """Get the visibility of this ViewportWidget"""
        self.__ui_frame.visible = bool(value)

    def __init__(self,
                 usd_context_name: str = '',
                 camera_path: Optional[str] = None,
                 resolution: Optional[tuple] = None,
                 hd_engine: Optional[str] = None,
                 viewport_api: Union[ViewportAPI, str, None] = None,
                 hydra_engine_options: Optional[dict] = None,
                 **ui_kwargs):
        """
        ViewportWidget constructor

        Args:
            usd_context_name (str): The name of a UsdContext this Viewport will be viewing.
            camera_path (str): The path to a UsdGeom.Camera to render with.
            resolution: (x,y): The size of the backing texture that is rendered into (or 'fill_frame' to lock to UI size).
            viewport_api: (ViewportAPI, str) A ViewportAPI instance that users have access to via .viewport_api property
                                             or a unique string id used to create a default ViewportAPI instance.
        """
        self.__ui_frame: ui.Frame = ui.Frame(**ui_kwargs)
        self.__viewport_texture: Optional[ViewportTexture] = None
        self.__display_delegate: Optional[ViewportDisplayDelegate] = None
        self.__g_instances.append(weakref.proxy(self, ViewportWidget.__clean_instances))
        self.__stage_listener = None
        self.__rsettings_changed = None
        if not viewport_api or not isinstance(viewport_api, ViewportAPI):
            viewport_id = viewport_api if viewport_api else str(id(self))
            self.__vp_api: ViewportAPI = ViewportAPI(usd_context_name, viewport_id, self._viewport_changed)
        else:
            self.__vp_api: ViewportAPI = viewport_api

        # This object or it's parent-scope instantiator own the API, so hand out a weak-ref proxy
        self.__proxy_api = weakref.proxy(self.__vp_api)
        self.__update_api_texture = self.__vp_api._ViewportAPI__set_hydra_texture
        self.__stage_up: Optional[StageAxis] = None
        self.__size_changed: bool = False
        self.__resize_future: Optional[asyncio.Future] = None
        self.__resize_task_or_future: Union[asyncio.Task, concurrent.futures.Future, None] = None
        self.__changed_objects = set()
        self.__scene_changed_task_or_future: Union[asyncio.Task, concurrent.futures.Future, None] = None
        self.__push_ui_to_viewport: bool = False
        self.__expand_viewport_to_ui: bool = False
        self.__full_resolution: Tuple[float, float] = (0.0, 0.0)
        # Whether to account for DPI when driving the Viewport resolution
        self.__resolution_uses_dpi: bool = True

        resolution = self.__resolve_resolution(resolution)

        # Save any arguments to send to HydraTexture in a local kwargs dict
        self.__hydra_engine_options = hydra_engine_options

        # TODO: Defer ui creation until stage open
        self.__build_ui(usd_context_name, camera_path, resolution, hd_engine)

        def on_usd_settings_saving(_):
            # XXX: This might be better handled at a higher level or allow opt into implicit camera saving
            if carb.settings.get_settings().get("/app/omni.usd/storeCameraSettingsToUsdStage"):
                if self.__vp_api:
                    time, camera = self.__vp_api.time, str(self.__vp_api.camera_path)
                else:
                    time, camera = None, None
                save_implicit_cameras(self.__ensure_usd_stage(), time, camera)

        usd_context = self.__ensure_usd_context()
        self.__stage_subscription = [
            carb.eventdispatcher.get_eventdispatcher().observe_event(
                observer_name="omni.kit.widget.viewport",
                event_name=usd_context.stage_event_name(event),
                on_event=func
            )
            for event, func in (
                (omni.usd.StageEventType.OPENED, lambda _: self.__on_stage_opened(self.__ensure_usd_stage(), camera_path, resolution, hd_engine)),
                (omni.usd.StageEventType.CLOSING, lambda _: self.__remove_notifications()),
                (omni.usd.StageEventType.SETTINGS_SAVING, on_usd_settings_saving)
            )
        ]

        stage = usd_context.get_stage()
        if stage:
            self.__on_stage_opened(stage, camera_path, resolution, hd_engine)
        elif usd_context and carb.settings.get_settings().get("/exts/omni.kit.widget.viewport/autoAttach/mode") == 2:
            # Initialize the auto-attach now, but watch for all excpetions so that constructor returns properly and this
            # ViewportWidget is valid and fully constructed in order to try and re-setup on next stage open
            try:
                resolution, tx_resolution = self.__get_texture_resolution(resolution)
                self.__viewport_texture = ViewportTexture(usd_context_name, camera_path, tx_resolution, hd_engine,
                                                          hydra_engine_options=self.__hydra_engine_options,
                                                          update_api_texture=self.__update_api_texture)
                self.__update_api_texture(self.__viewport_texture, None)
                self.__viewport_texture._on_stage_opened(self.__set_image_data, camera_path, self.__is_first_instance())
            except Exception:  # noqa PLW0718
                from .impl.utility import _report_error
                _report_error()

    def destroy(self):
        """
        Called by extension before destroying this object. It doesn't happen automatically.
        Without this hot reloading doesn't work.
        """
        # Clean ourself from the instance list
        ViewportWidget.__clean_instances(None, self)
        self.__stage_subscription = None
        self.__remove_notifications()
        if self.__vp_api:
            clear_engine = self.__vp_api.set_hd_engine
            if clear_engine:
                clear_engine(None)
        self.__update_api_texture(None, None)
        self.__destroy_ui()
        self.__vp_api = None
        self.__proxy_api = None
        self.__resize_task_or_future = None
        self.__scene_changed_task_or_future = None

    @property
    def usd_context_name(self) -> str:
        """Return the name of the USdContext this instance is attached to"""
        return self.__vp_api.usd_context_name

    @property
    def display_delegate(self):
        return self.__display_delegate

    @display_delegate.setter
    def display_delegate(self, display_delegate: ViewportDisplayDelegate):
        if not isinstance(display_delegate, ViewportDisplayDelegate):
            raise RuntimeError('display_delegate must be a ViewportDisplayDelegate, {display_delegate} is not')

        # Store the previous delegate for return value and comparison wtether anything is actually changing
        prev_delegate = self.__display_delegate
        # If the delegate is different, call the create method and change this instance's value if succesful
        if prev_delegate != display_delegate:
            self.__ui_frame.clear()
            display_delegate.create(self.__ui_frame, prev_delegate)
            self.__display_delegate = display_delegate
        # Return the previous delegate so callers can swap and restore
        return prev_delegate

    def _viewport_changed(self, camera_path: Sdf.Path, stage: Usd.Stage, time: Usd.TimeCode | None = None):
        # During re-open camera_path can wind up in an empty state, so be careful around getting the UsdGeom.Camera
        prim = stage.GetPrimAtPath(camera_path) if (camera_path and stage) else None
        camera = UsdGeom.Camera(prim) if prim else None
        if not camera:
            return None, None, None
        if time is None:
            time = Usd.TimeCode.Default()

        canvas_size = self.__display_delegate.size
        force_update = self.__size_changed
        self.__vp_api._sync_viewport_api(camera, canvas_size, time, force_update=force_update)  # noqa PLW0212
        return camera, canvas_size, time

    def __ensure_usd_context(self, usd_context: omni.usd.UsdContext = None):
        if not usd_context:
            usd_context = self.__vp_api.usd_context
            if not usd_context:
                raise RuntimeError(f'omni.usd.UsdContext "{self.usd_context_name}" does not exist')
        return usd_context

    def __ensure_usd_stage(self, usd_context: omni.usd.UsdContext = None):
        stage = self.__ensure_usd_context(usd_context).get_stage()
        if stage:
            return stage
        raise RuntimeError(f'omni.usd.UsdContext "{self.usd_context_name}" has no stage')

    def __remove_notifications(self):
        # Remove notifications that are -transient- or related to a stage and can be easily setup
        if self.__stage_listener:
            self.__stage_listener.Revoke()
            self.__stage_listener = None
        if self.__rsettings_changed and self.__viewport_texture:
            self.__viewport_texture._remove_render_settings_changed_fn(self.__rsettings_changed)  # noqa PLW0212
            self.__rsettings_changed = None
        if self.__ui_frame:
            self.__ui_frame.set_computed_content_size_changed_fn(None)
        # Discard any pending changes to inspect
        if self.__scene_changed_task_or_future:
            self.__scene_changed_task_or_future.cancel()
            self.__scene_changed_task_or_future = None
        self.__changed_objects = set()
        # self.set_build_fn(None)

    def __setup_notifications(self, stage: Usd.Stage, hydra_texture):
        # Remove previous -soft- notifications
        self.__remove_notifications()

        # Proxy these two object so as not to extend their lifetime the API object
        if hydra_texture and not isinstance(hydra_texture, weakref.ProxyType):
            hydra_texture = weakref.proxy(hydra_texture)

        assert hydra_texture is None or isinstance(hydra_texture, weakref.ProxyType), "Not sending a proxied object"

        self.__update_api_texture(weakref.proxy(self.__viewport_texture), hydra_texture)

        async def scene_changed():
            _, self.__scene_changed_task_or_future = self.__scene_changed_task_or_future, None
            changed_paths, self.__changed_objects = self.__changed_objects, set()
            camera_path = self.__vp_api.camera_path
            if not camera_path:
                return

            # This may be invoked asynchronously after
            stage = self.__ensure_usd_context().get_stage()
            if not stage:
                return

            root_changed, cam_changed = False, False
            for p in changed_paths:
                if not root_changed and (p == Sdf.Path.absoluteRootPath):  # noqa SIM102
                    root_changed = True
                if not cam_changed:
                    prim_path = p.GetPrimPath()
                    # If it is the camera path, assume any property change can affect view/projection
                    cam_changed = prim_path == camera_path
                    if not cam_changed:
                        # Not the camera path, but any transform change to any parent also affects view
                        is_child = camera_path.HasPrefix(prim_path)
                        cam_changed = is_child and UsdGeom.Xformable.IsTransformationAffectedByAttrNamed(p.name)

                if root_changed and cam_changed:
                    break

            if root_changed:
                cam_changed = self.__stage_up.update(stage, self.__vp_api.time, self.usd_context_name, self.__is_first_instance()) or cam_changed
            if cam_changed:
                self.__vp_api.viewport_changed(camera_path, stage)

        # Stage changed notification (Tf.Notice)
        def stage_changed_notice(notice, sender):
            # assert self.__vp_api.stage == sender
            if self.__vp_api.camera_path:
                self.__changed_objects.update(notice.GetChangedInfoOnlyPaths())
                if not self.__scene_changed_task_or_future:
                    self.__scene_changed_task_or_future = run_coroutine(scene_changed())

        # omni.ui notification that the widget size has changed
        def update_size():
            try:
                self.__size_changed = True
                self.__root_size_changed()
                self.__vp_api.viewport_changed(self.__vp_api.camera_path, self.__ensure_usd_stage())
            finally:
                self.__size_changed = False

        # async version to ellide intermediate resize event
        async def resize_future(n_frames: int, mouse_wait: int, mouse_up: bool, update_projection: bool = False):
            import omni.appwindow
            import omni.kit.app
            import carb.input

            if update_projection:
                prim = stage.GetPrimAtPath(self.__vp_api.camera_path)
                camera = UsdGeom.Camera(prim) if prim else None
                if not camera:
                    update_projection = False

            app = omni.kit.app.get_app()

            async def skip_frame():
                await app.next_update_async()
                if update_projection:
                    self.__vp_api._sync_viewport_api(camera, self.__display_delegate.size, force_update=True)  # noqa PLW0212

            if mouse_wait or mouse_up:
                iinput = carb.input.acquire_input_interface()
                app_window = omni.appwindow.get_default_app_window()
                mouse = app_window.get_mouse()
                mouse_value = iinput.get_mouse_value(mouse, carb.input.MouseInput.LEFT_BUTTON)
                frames_waited, mouse_static, prev_mouse = 0, 0, None
                while mouse_value:
                    await skip_frame()
                    frames_waited = frames_waited + 1
                    # Check mouse up no matter what, up cancels even if waiting for mouse paused
                    mouse_value = iinput.get_mouse_value(mouse, carb.input.MouseInput.LEFT_BUTTON)
                    if mouse_wait and mouse_value:
                        if mouse_static > mouse_wait:
                            # Else if the mouse has been on same pixel for more than required time, done
                            break

                        # Compare current and previous mouse locations
                        cur_mouse = iinput.get_mouse_coords_pixel(mouse)
                        if prev_mouse is not None:
                            if (cur_mouse[0] == prev_mouse[0]) and (cur_mouse[1] == prev_mouse[1]):
                                mouse_static = mouse_static + 1
                            else:
                                mouse_static = 0
                        prev_mouse = cur_mouse
                # Make sure to wait the miniumum nuber of frames as well
                if n_frames:
                    n_frames = max(0, n_frames - frames_waited)

            for _ in range(n_frames):
                await skip_frame()

            # Check it hasn't been handled already once more
            if self.__resize_future.done():
                return
            # Finally flag it as handled and push the size change
            self.__resize_future.set_result(True)
            update_size()

        def size_changed_notification(*args, **kwargs):
            # Elide intermediate resize events when pushing ui size to Viewport
            if self.__push_ui_to_viewport or self.__expand_viewport_to_ui or self.__vp_api.fill_frame:
                if self.__resize_future and not self.__resize_future.done():
                    return

                # Setting that controls the number of ui-frame delay
                settings = carb.settings.get_settings()
                f_delay = settings.get("/exts/omni.kit.widget.viewport/resize/textureFrameDelay")
                mouse_pause = settings.get("/exts/omni.kit.widget.viewport/resize/waitForMousePaused")
                mouse_up = settings.get("/exts/omni.kit.widget.viewport/resize/waitForMouseUp")
                update_proj = settings.get("/exts/omni.kit.widget.viewport/resize/updateProjection")
                if f_delay or mouse_pause or mouse_up:
                    self.__resize_future = asyncio.Future()
                    self.__resize_task_or_future = run_coroutine(resize_future(f_delay, mouse_pause, mouse_up, update_proj))
                    return

            update_size()

        # hydra_texture notification that the render-settings have changed (we only care about camera and resolution)
        def render_settings_changed(camera_path, resolution):
            # Notify everything else in the chain
            stage = self.__ensure_usd_context().get_stage()
            if stage:
                self.__vp_api.viewport_changed(camera_path, stage)
                self.__vp_api._notify_render_settings_change()  # noqa PLW0212
            else:
                # This callback should be removed on omni.usd.StageEventType.CLOSING so it genrally should not be reachable
                # for a UsdContext without a stage.
                carb.log_warn(f'render_settings_changed called when omni.usd.UsdContext "{self.usd_context_name}" had no stage')

        self.__stage_listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, lambda n, s: stage_changed_notice(n, s), stage)
        self.__rsettings_changed = self.__viewport_texture._add_render_settings_changed_fn(render_settings_changed)  # noqa PLE1128
        self.__ui_frame.set_computed_content_size_changed_fn(size_changed_notification)
        # self.set_build_fn(update_size)

        # Update now if the widget is layed out
        if self.__ui_frame.computed_height:
            update_size()

    def __resolve_resolution(self, resolution):
        # XXX: ViewportWindow handles the de-serialization of saved Viewport resolution.
        #      This means clients of ViewportWidget only must handle startup resolution themselves.
        if resolution is None:
            # Support legacy settings to force fit-viewport
            settings = carb.settings.get_settings()
            width, height = settings.get('/app/renderer/resolution/width'), settings.get('/app/renderer/resolution/height')
            # If both are set to values above 0, that is the default resolution for a Viewport
            # If either of these being zero or below causes autmoatic resolution to fill the UI frame
            if ((width is not None) and (width > 0)) and ((height is not None) and (height > 0)):
                resolution = (width, height)
            elif ((width is not None) and (width <= 0)) or ((height is not None) and (height <= 0)):
                resolution = 'fill_frame'

        # Allow a 'fill_frame' constant to be used for resolution
        # Any constant zero or below also fills frame (support legacy behavior)
        if (resolution is not None) and ((isinstance(resolution, str) and resolution == 'fill_frame') or int(resolution[0]) <= 0 or int(resolution[1]) <= 0):
            resolution = 'fill_frame'
            self.__vp_api.fill_frame = True

        # Allow a 'fill_frame' constant to be used for resolution
        # Any constant zero or below also fills frame (support legacy behavior)
        if resolution is not None:
            if (isinstance(resolution, str) and resolution == 'fill_frame') or int(resolution[0]) <= 0 or int(resolution[1]) <= 0:
                resolution = 'fill_frame'
                self.__push_ui_to_viewport = True
                self.__vp_api.fill_frame = True
            else:
                self.__full_resolution = resolution

        return resolution

    def __get_texture_resolution(self, resolution: Union[str, tuple]):
        # Don't pass 'fill_frame' to ViewportTexture if it was requested, that will be done during layout anyway
        if resolution == 'fill_frame':
            return ((0, 0), None)
        return resolution, resolution

    def __build_ui(self, usd_context_name: str, camera_path: str, resolution: Union[str, tuple], hd_engine: str):
        # Required for a lot of things (like selection-color) to work!
        init_settings()

        resolution, tx_resolution = self.__get_texture_resolution(resolution)

        # the viewport texture is the base background inmage that is drive by the Hydra_Texture object
        self.__viewport_texture = ViewportTexture(usd_context_name, camera_path, tx_resolution, hd_engine,
                                                  hydra_engine_options=self.__hydra_engine_options,
                                                  update_api_texture=self.__update_api_texture)
        self.__update_api_texture(self.__viewport_texture, None)

        self.display_delegate = ViewportDisplayDelegate(self.__proxy_api)
        # Pull the current Viewport full resolution now (will call __root_size_changed)
        self.set_resolution(resolution)

    def __destroy_ui(self):
        self.__display_delegate.destroy()
        if self.__viewport_texture:
            self.__viewport_texture.destroy()
            self.__viewport_texture = None
        if self.__ui_frame:
            self.__ui_frame.destroy()
            self.__ui_frame = None

    def __is_first_instance(self) -> bool:
        for vp_instance in self.__g_instances:
            if vp_instance == self:
                # vpinstance is this object, and no other instances attached to named UsdContext has been seen
                return True
            if vp_instance.usd_context_name == self.usd_context_name:
                # vpinstance is NOT this object, but vpinstance is attached to same UsdContext
                return False
        # Should be unreachable, but would be True in the event neither case above was triggered
        return True

    def __set_image_data(self, texture, presentation_key=0):
        vp_api = self.__vp_api

        prim = self.__ensure_usd_stage().GetPrimAtPath(vp_api.camera_path)
        camera = UsdGeom.Camera(prim) if prim else None

        frame_info = vp_api.frame_info
        lock_to_render = vp_api.lock_to_render_result
        metadata = frame_info.get('metadata', None)

        view = frame_info.get('view', None) if lock_to_render else None
        # omni.ui.scene may not handle RTX projection yet, so calculate from USD camera
        projection = None  # frame_info.get('projection', None) if lock_to_render else None

        canvas_size = self.__display_delegate.update(viewport_api=vp_api, texture=texture, view=view, projection=projection, presentation_key=presentation_key, metadata=metadata)
        vp_api._sync_viewport_api(camera, canvas_size, vp_api.time, view, projection, force_update=True)  # noqa PLW0212
        vp_api._notify_frame_change()  # noqa PLW0212

    def __on_stage_opened(self, stage: Usd.Stage, camera_path: str, resolution: tuple, hd_engine: str):
        """Called when opening a new stage"""

        # We support creation of ViewportWidget with an explicit path.
        # If that path was not given or does not exists, fall-back to ov-metadata
        if camera_path:
            cam_prim = stage.GetPrimAtPath(camera_path)
            if not cam_prim or not UsdGeom.Camera(cam_prim):
                camera_path = False
        if not camera_path:
            # TODO: 104 Put in proper namespace and per viewport
            # camera_path = stage.GetMetadataByDictKey("customLayerData", f"cameraSettings:{self.__vp_api.id}:boundCamera") or
            # Fallback to < 103.1 boundCamera
            try:
                # Wrap in a try-catch so failure reading metadata does not cascade to caller.
                camera_path = stage.GetMetadataByDictKey("customLayerData", "cameraSettings:boundCamera")
            except Tf.ErrorException as e:
                carb.log_error(f"Error reading Usd.Stage's boundCamera metadata {e}")

        # Cache the known up-axis to watch for changes
        self.__stage_up = StageAxis(stage)

        if self.__viewport_texture is None:
            self.__build_ui(self.usd_context_name, camera_path, resolution, hd_engine)
        else:
            self.__viewport_texture.camera_path = camera_path

        hydra_texture = self.__viewport_texture._on_stage_opened(self.__set_image_data, camera_path, self.__is_first_instance())  # noqa PLW0212
        self.__setup_notifications(stage, hydra_texture)

    # XXX: Temporary API for driving Viewport resolution based on UI.  These may be removed.
    @property
    def resolution_uses_dpi(self) -> bool:
        """Whether to account for DPI when driving the Viewport texture resolution"""
        return self.__resolution_uses_dpi

    @property
    def fill_frame(self) -> bool:
        """Whether the ui object containing the Viewport texture expands both dimensions of resolution based on the ui size"""
        return self.__push_ui_to_viewport

    @property
    def expand_viewport(self) -> bool:
        """Whether the ui object containing the Viewport texture expands one dimension of resolution to cover the full ui size"""
        return self.__expand_viewport_to_ui

    @resolution_uses_dpi.setter
    def resolution_uses_dpi(self, value: bool) -> None:
        """Tell the ui object whether to use DPI scale when driving the Viewport texture resolution"""
        value = bool(value)
        if self.__resolution_uses_dpi != value:
            self.__resolution_uses_dpi = value
            self.__root_size_changed()

    @fill_frame.setter
    def fill_frame(self, value: bool) -> None:
        """Tell the ui object containing the Viewport texture to expand both dimensions of resolution based on the ui size"""
        value = bool(value)
        if self.__push_ui_to_viewport != value:
            self.__push_ui_to_viewport = value
            if not self.__root_size_changed():
                self.__vp_api.resolution = self.__full_resolution

    @expand_viewport.setter
    def expand_viewport(self, value: bool) -> None:
        """Tell the ui object containing the Viewport texture to expand one dimension of resolution to cover the full ui size"""
        value = bool(value)
        if self.__expand_viewport_to_ui != value:
            self.__expand_viewport_to_ui = value
            if not self.__root_size_changed():
                self.__vp_api.resolution = self.__full_resolution

    def set_resolution(self, resolution: Tuple[float, float]) -> None:
        self.__full_resolution = resolution
        # When resolution is <= 0, that means ui.Frame drives Viewport resolution
        self.__push_ui_to_viewport = (resolution is None) or (resolution[0] <= 0) or (resolution[1] <= 0)
        if not self.__root_size_changed():
            # If neither option is enabled, then just set the resolution directly
            self.__vp_api.resolution = resolution

    @property
    def resolution(self) -> Tuple[float, float]:
        """Return the resolution that the renderer is providing images at."""
        return self.__vp_api.resolution

    @resolution.setter
    def resolution(self, resolution: Tuple[float, float]):
        """Set the resolution that the renderer is providing images at."""
        self.set_resolution(resolution)

    @property
    def full_resolution(self):
        """Return the resolution being requested (not accounting for any % down-scaling"""
        return self.__full_resolution

    def __root_size_changed(self, *args, **kwargs):
        # If neither options are enabled, then do nothing to the Viewport's resolution
        if not self.__push_ui_to_viewport and not self.__expand_viewport_to_ui:
            return False

        # Match the legacy Viewport resolution and fit
        # XXX: Note for a down-sampled constant resolution, that is expanded to the Viewport dimensions
        # the order of operation is off if one expects 512 x 512 @ 1 to 1024 x 1024 @ 0.5 to expand to the same result

        # Get the omni.ui.Widget computed size
        ui_frame = self.__ui_frame
        res_x, res_y = int(ui_frame.computed_width), int(ui_frame.computed_height)
        # Scale by DPI as legacy Viewport (to match legacy Viewport calculations)
        dpi_scale = ui.Workspace.get_dpi_scale() if self.__resolution_uses_dpi else 1.0
        res_x, res_y = res_x * dpi_scale, res_y * dpi_scale
        # Full resolution width and hight
        fres_x, fres_y = self.__full_resolution if self.__full_resolution else (res_x, res_y)
        if self.__expand_viewport_to_ui and (fres_y > 0) and (res_y > 0):
            tex_ratio = fres_x / fres_y
            ui_ratio = res_x / res_y
            if tex_ratio < ui_ratio:
                fres_x = fres_x * (ui_ratio / tex_ratio)
            else:
                fres_y = fres_y * (tex_ratio / ui_ratio)

            # Limit the resolution to not grow too large
            res_x, res_y = min(res_x, fres_x), min(res_y, fres_y)

        self.__vp_api.resolution = res_x, res_y
        return True
