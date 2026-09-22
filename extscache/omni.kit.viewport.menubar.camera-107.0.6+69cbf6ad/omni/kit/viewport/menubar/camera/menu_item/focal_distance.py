import asyncio
import weakref
import math
from typing import List


import carb
import omni.kit.app
import omni.kit.commands
import omni.kit.undo
from omni.kit.viewport.menubar.core import SpinnerMenuDelegate, IconMenuDelegate, USDAttributeModel
import omni.ui as ui
from omni.ui import scene as sc
import omni.usd
from pxr import Gf

from .camera_setting import AbstractCameraSetting

__all__ = ["CamFocalData", "FocusClickGesture", "FocusDragGesture", "PreventOthers", "ViewportClickManipulator", "FocalPickerScene", "CameraFocalDistance"]


class CamFocalData:
    def __init__(self, cam_focal: "CameraFocalDistance", viewport_api):
        self.__main_cursor = None
        self.__cam_focal = cam_focal
        self.viewport_api = viewport_api
        self.__undo = False
        self.__auto_destruct = False

        try:
            import omni.kit.window.cursor  # noqa: PLW0621
            self.__main_cursor = omni.kit.window.cursor.get_main_window_cursor()
            if self.__main_cursor:
                self.__main_cursor.override_cursor_shape(carb.windowing.CursorStandardShape.CROSSHAIR)
        except ImportError:
            pass

    def __del__(self):
        self.destroy()

    def destroy(self):
        if self.__undo:
            self.__undo = False
            omni.kit.undo.end_group()
        if self.__main_cursor:
            self.__main_cursor.clear_overridden_cursor_shape()
            self.__main_cursor = None
        if self.__cam_focal:
            self.__cam_focal._destroy_scene()  # noqa: PLW0212
            self.__cam_focal = False
        self.viewport_api = None

    def focus_query_completed(self, prim_path: str, world_space_pos, *args):
        try:
            viewport_api = self.viewport_api
            if prim_path and world_space_pos and viewport_api:
                cam_path = viewport_api.camera_path
                cam_prim = viewport_api.stage.GetPrimAtPath(cam_path)
                if not cam_prim:
                    carb.log_error(f'Could not get camera prim at "{cam_path}"')
                    return

                # Compute world-space camera position to get distance
                world_space_camera = viewport_api.transform.Transform(Gf.Vec3d(0, 0, 0))
                distance = (Gf.Vec3d(*world_space_pos) - world_space_camera).GetLength()
                if math.isfinite(distance):
                    # Set to the focusDistance attribute on the Camera
                    focus_attr = cam_prim.GetAttribute('focusDistance')
                    # Start an undo-group in case of a drag
                    if not self.__undo:
                        self.__undo = True
                        omni.kit.undo.begin_group()
                    omni.kit.commands.execute(
                        'ChangeProperty',
                        prop_path=focus_attr.GetPath(),
                        value=distance,
                        prev=focus_attr.Get() if focus_attr else None
                    )
                    # XXX: Setting to change center of interest TOO ?
        except Exception:  # noqa: PLW0718
            pass
        finally:
            if self.__auto_destruct:
                self.__auto_destruct = None
                self.destroy()

    def set_focus_position(self, ndc_mouse, auto_destruct: bool = True):
        mouse, viewport_api = self.viewport_api.map_ndc_to_texture_pixel(ndc_mouse)
        if mouse and viewport_api:
            self.__auto_destruct = auto_destruct
            viewport_api.request_query(mouse, self.focus_query_completed, query_name='omni.kit.viewport.menubar.camera.FocusQuery')
        elif auto_destruct:
            self.destroy()


class FocusClickGesture(sc.ClickGesture):
    def __init__(self, cam_focal_data: CamFocalData, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__cam_focal_data = cam_focal_data

    def on_ended(self, *args, **kwargs):
        if self.state != sc.GestureState.CANCELED:
            self.__cam_focal_data.set_focus_position(self.sender.gesture_payload.mouse)


class FocusDragGesture(sc.DragGesture):
    def __init__(self, cam_focal_data: CamFocalData, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__cam_focal_data = cam_focal_data

    def on_changed(self, *args, **kwargs):
        self.__cam_focal_data.set_focus_position(self.sender.gesture_payload.mouse, False)

    def on_ended(self, *args, **kwargs):
        if self.state != sc.GestureState.CANCELED:
            self.__cam_focal_data.set_focus_position(self.sender.gesture_payload.mouse)


class PreventOthers(sc.GestureManager):
    """Class to prevent any gestures (like selection) from interfering with the focus pick"""
    def can_be_prevented(self, gesture):
        # Never prevent in the middle of drag
        return gesture.state != sc.GestureState.CHANGED

    def should_prevent(self, gesture, preventer):
        if isinstance(gesture, FocusDragGesture):
            return False
        if isinstance(gesture, FocusClickGesture):
            return False
        return True


class ViewportClickManipulator(sc.Manipulator):
    def __init__(self, cam_focal_data: CamFocalData, *args, mouse_button: int = 0, **kwargs):
        super().__init__(*args, **kwargs)
        self.__gestures = [FocusDragGesture(cam_focal_data, mouse_button=mouse_button, manager=PreventOthers()),
                           FocusClickGesture(cam_focal_data, mouse_button=mouse_button, manager=PreventOthers())]
        self.__transform = None
        self.__screen = None  # noqa: PLW0238

    def __del__(self):
        self.destroy()

    def on_build(self):
        # Need to hold a reference to this or the sc.Screen would be destroyed when out of scope
        self.__transform = sc.Transform()
        with self.__transform:
            self.__screen = sc.Screen(gestures=self.__gestures)  # noqa: PLW0238

    def destroy(self):
        self.__gestures = None
        self.__screen = None  # noqa: PLW0238
        if self.__transform:
            self.__transform.clear()
            self.__transform = None


class FocalPickerScene:
    def __init__(self, cam_focal_data: CamFocalData, ui_frame):
        self.__ui_frame = ui_frame
        self.__manip = None
        self.__scene = None
        with ui_frame:
            # Need to insert a stack to get content_clipping and block events from going below us
            self.__container = ui.VStack(content_clipping=True)
            with self.__container:
                self.__scene = sc.SceneView()
                with self.__scene.scene:
                    self.__manip = ViewportClickManipulator(cam_focal_data)

    def __del__(self):
        self.destroy()

    def destroy(self):
        manip, self.__manip = self.__manip, None
        if manip:
            manip.destroy()
        scene, self.__scene = self.__scene, None
        if scene:
            scene.destroy()
        container, self.__container = self.__container, None
        if container:
            container.clear()
            container.destroy()
        # Clear ui.Frame, but kep it alive for next click
        ui_frame, self.__ui_frame = self.__ui_frame, None
        if ui_frame:
            ui_frame.clear()


class CameraFocalDistance(AbstractCameraSetting):
    def __init__(self, model: USDAttributeModel, viewport_context, enabled: bool = True):
        self.__registered_scene = None
        self.__viewport_api = viewport_context.get("viewport_api")
        self.__ui_get_frame = viewport_context.get("layer_provider")
        super().__init__(model, enabled=enabled)

    def destroy(self):
        self.__viewport_api = None
        self.__ui_get_frame = None
        self._destroy_scene()

    def _build_ui(self) -> List[ui.MenuDelegate]:
        self._focal_delegate = SpinnerMenuDelegate(
            model=self._property_model,
            height=26,
            enabled=self._enabled,
            text=False,
            icon_name="FocalDistance",
            tooltip="Camera Focal Distance",
            icon_height=26,
            use_in_menubar=True,
        )
        ui.MenuItem("Focal Distance", delegate=self._focal_delegate, identifier="viewport.camera.focal_distance")

        self._sample_delegate = IconMenuDelegate(name="Sample", height=26, has_triangle=False, enabled=self._enabled, tooltip="Sample Focal Distance")
        ui.MenuItem("Sample", delegate=self._sample_delegate, triggered_fn=self._sample, enabled=self._enabled, identifier="viewport.camera.sample")

        return [self._focal_delegate, self._sample_delegate]

    def _sample(self):
        if self.__registered_scene:
            # stop sample
            self._destroy_scene()
        elif self._enabled:
            # start sample
            asyncio.ensure_future(self.__create_focus_picker_scene())

    async def __create_focus_picker_scene(self):
        await omni.kit.app.get_app().next_update_async()
        self.__destroy_scene_sync()
        self.__registered_scene = FocalPickerScene(CamFocalData(weakref.proxy(self), self.__viewport_api),
                                                   self.__ui_get_frame.get_frame("omni.kit.viewport.menubar.camera.FocalPickerScene"))

    def __destroy_scene_sync(self):
        if self.__registered_scene:
            self.__registered_scene.destroy()
            self.__registered_scene = None

    def _destroy_scene(self):
        # Destroy on next event
        async def ui_async_destroy():
            await omni.kit.app.get_app().next_update_async()
            self.__destroy_scene_sync()
        asyncio.ensure_future(ui_async_destroy())
