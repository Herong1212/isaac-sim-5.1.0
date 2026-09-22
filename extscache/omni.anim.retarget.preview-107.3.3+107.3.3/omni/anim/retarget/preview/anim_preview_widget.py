# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import asyncio
import enum
import carb.events
import omni.ui as ui
import omni.kit.app
import omni.timeline
from functools import partial
from omni.ui import scene as sc
from omni.ui import color as cl
from omni.kit.widget.viewport import ViewportWidget
from pxr import Gf, Usd, UsdGeom, UsdSkel
from typing import *

from .anim_preview_model import AnimPreviewModel
from .annotation.annotation_delegate import AnnotationDelegate
from .annotation.annotation_model import Annotation, AnnotationSet
from .widget.context_menu import show_camera_context_menu, show_visibility_context_menu
from .joint_compare_window import JointCompareWindow
from .orbit_camera import AnimatedOrbitViewportCameraManipulator, ViewSide
from .compatibility_utils import get_joint_list
from .utils import WeakMethod
from omni.anim.widget.timeline import StageRangeModel, TimelineView
from omni.kit.helper.file_utils.asset_types import get_icon

from .prim_search_widget import PrimSearchWidget
from .model.source_model import SourceModel


__all__ = ['AnimPreviewWidget']

MODULE_PATH = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
MIN_TRACKS_TO_SHOW = 1
MAX_TRACKS_TO_SHOW = 5

SKELANIM_ICON = get_icon("a.skelanim.usd")
SKEL_ICON = get_icon("a.skel.usd")

BASE_BUTTON_STYLE = {
    "Button": {
        "margin": 2,
        "background_color": cl.shade(cl("#25282ACC"))
    },
    "Button:pressed": {
        "background_color": cl.shade(cl("#34C7FF3B"))
    },
    "Button:hovered": {
        "background_color": cl.shade(cl("#34C7FF3B")),
        "border_width": 1,
        "border_color": cl.shade(cl("#34C7FF"))
    },
    "Button:checked": {
        "background_color": cl.shade(cl("#6E6E6E"))
    },
}
PAUSE_BUTTON_STYLE = {"image_url": f"{MODULE_PATH}/icons/pause.svg"}
PAUSE_BUTTON_STYLE.update(BASE_BUTTON_STYLE)
PLAY_BUTTON_STYLE = {"image_url": f"{MODULE_PATH}/icons/play.svg"}
PLAY_BUTTON_STYLE.update(BASE_BUTTON_STYLE)
NEXT_FRAME_BUTTON_STYLE = {"image_url": f"{MODULE_PATH}/icons/next_frame.svg"}
NEXT_FRAME_BUTTON_STYLE.update(BASE_BUTTON_STYLE)
PREVIOUS_FRAME_BUTTON_STYLE = {"image_url": f"{MODULE_PATH}/icons/previous_frame.svg"}
PREVIOUS_FRAME_BUTTON_STYLE.update(BASE_BUTTON_STYLE)
START_BUTTON_STYLE = {"image_url": f"{MODULE_PATH}/icons/first_frame.svg"}
START_BUTTON_STYLE.update(BASE_BUTTON_STYLE)
END_BUTTON_STYLE = {"image_url": f"{MODULE_PATH}/icons/last_frame.svg"}
END_BUTTON_STYLE.update(BASE_BUTTON_STYLE)
LOOP_BUTTON_STYLE = {"image_url": f"{MODULE_PATH}/icons/loop.svg"}
LOOP_BUTTON_STYLE.update(BASE_BUTTON_STYLE)

VISIBILITY_BUTTON_STYLE = {"image_url": f"{MODULE_PATH}/icons/visibility.svg"}
VISIBILITY_BUTTON_STYLE.update(BASE_BUTTON_STYLE)

CAMERA_BUTTON_STYLE = {"image_url": f"{MODULE_PATH}/icons/camera.svg"}
CAMERA_BUTTON_STYLE.update(BASE_BUTTON_STYLE)

PLAY_BUTTON_SIZE = 36

class PlayMode(enum.Enum):
    STOP = 1
    PLAY = 2
    PAUSE = 3


class ForwardUpAxesManipulator(sc.Manipulator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_build(
        self,
        forward_color: int = ui.color("#0076b9"),
        text_background_color: int = ui.color("#cdcdcd"),
        text_border_color: int = ui.color.black,
        text_border_thickness: int = 3,
        text_padding: int = 5,
        text_size: int = 15,
        up_color: int = ui.color("#b92323"),
    ):
        if self.model:
            draw_text = self.model.get_as_value(self.model.get_item("draw_text"))
            position = self.model.get_as_vector(self.model.get_item("position"))
            rotation = self.model.get_as_vector(self.model.get_item("rotation"))
            skel_rot = sc.Matrix44.get_rotation_matrix(rotation[0], rotation[1], rotation[2])
            skel_pos = sc.Matrix44.get_translation_matrix(position[0], position[1], position[2])
            transform = skel_pos * skel_rot
            if self.model.get_as_value(self.model.get_item("draw_forward_axis")):
                self.__build_axis(
                    axis_color=forward_color,
                    draw_text=draw_text,
                    end_id="forward_end",
                    start_id="forward_start",
                    text="Forward",
                    text_background_color=text_background_color,
                    text_border_color=text_border_color,
                    text_border_thickness=text_border_thickness,
                    text_padding=text_padding,
                    text_pos_id="forward_text_pos",
                    text_size=text_size,
                    transform=transform,
                )
            if self.model.get_as_value(self.model.get_item("draw_up_axis")):
                self.__build_axis(
                    axis_color=up_color,
                    draw_text=draw_text,
                    end_id="up_end",
                    start_id="up_start",
                    text="Up",
                    text_background_color=text_background_color,
                    text_border_color=text_border_color,
                    text_border_thickness=text_border_thickness,
                    text_padding=text_padding,
                    text_pos_id="up_text_pos",
                    text_size=text_size,
                    transform=transform,
                )

    def on_model_updated(self, item):
        self.invalidate()

    def __build_axis(
        self,
        axis_color: int,
        draw_text: bool,
        end_id: str,
        start_id: str,
        text_pos_id: str,
        transform: sc.Matrix44,
        text: str,
        text_background_color: int,
        text_border_color: int,
        text_border_thickness: int,
        text_padding: int,
        text_size: int,
):
        if draw_text:
            height = 2 * text_size + text_padding
            width = len(text) * text_size + 2 * text_padding
            text_pos = self.model.get_as_vector(self.model.get_item(text_pos_id))
            translate = transform * sc.Matrix44.get_translation_matrix(text_pos[0], text_pos[1], text_pos[2])
            with sc.Transform(transform=translate):
                with sc.Transform(look_at=sc.Transform.LookAt.CAMERA, scale_to=sc.Space.SCREEN):
                    sc.Rectangle(width, height, color=text_background_color)
                    sc.Rectangle(width, height, color=text_border_color, thickness=text_border_thickness, wireframe=True)
                sc.Label(text, alignment=ui.Alignment.CENTER, color=axis_color, size=text_size)
        end = self.model.get_as_vector(self.model.get_item(end_id))
        start = self.model.get_as_vector(self.model.get_item(start_id))
        with sc.Transform(transform=transform):
            sc.Line([start[0], start[1], start[2]], [end[0], end[1], end[2]], color=axis_color, thickness=5)


class ForwardUpAxesModel(sc.AbstractManipulatorModel):
    class ValueItem(sc.AbstractManipulatorItem):
        def __init__(self, value: float = 0):
            super().__init__()
            self.value = value

    class VectorItem(sc.AbstractManipulatorItem):
        def __init__(self, value: List = [0, 0, 0]):
            super().__init__()
            self.value = value

    def __init__(self, usd_context_name: str = ''):
        super().__init__()
        self.__current_path = None
        self.__has_control_rig = False
        self.__items = {
            "draw_forward_axis": ForwardUpAxesModel.ValueItem(0),
            "draw_text": ForwardUpAxesModel.ValueItem(1),
            "draw_up_axis": ForwardUpAxesModel.ValueItem(0),
            "forward_end": ForwardUpAxesModel.VectorItem(),
            "forward_start": ForwardUpAxesModel.VectorItem(),
            "forward_text_pos": ForwardUpAxesModel.VectorItem(),
            "position": ForwardUpAxesModel.VectorItem(),
            "rotation": ForwardUpAxesModel.VectorItem(),
            "up_end": ForwardUpAxesModel.VectorItem(),
            "up_start": ForwardUpAxesModel.VectorItem(),
            "up_text_pos": ForwardUpAxesModel.VectorItem(),
        }
        self.__usd_context_name = usd_context_name
        self.update_transform()

    def get_as_value(self, item: sc.AbstractManipulatorItem):
        if self.__has_control_rig and isinstance(item, ForwardUpAxesModel.ValueItem):
            return item.value
        return 0

    def get_as_vector(self, item: sc.AbstractManipulatorItem):
        if isinstance(item, ForwardUpAxesModel.VectorItem):
            return item.value
        return []

    def get_item(self, id: str):
        if id in self.__items:
            return self.__items[id]
        return None

    def set_draw(self, id: str, value: bool):
        if id in self.__items:
            item = self.__items[id]
            if isinstance(item, ForwardUpAxesModel.ValueItem):
                item.value = 1 if value else 0
                self._item_changed(None)

    def set_skeleton(self, skeleton: UsdSkel.Skeleton):
        prim_path = None
        if skeleton:
            prim = skeleton.GetPrim()
            if prim and prim.IsA(UsdSkel.Skeleton):
                prim_path = prim.GetPrimPath()
        if self.__current_path != prim_path:
            self.__current_path = prim_path
            self.update_transform()

    def update_transform(self):
        forward_axis = 'Z'
        prim = None
        up_axis = 'Y'
        self.__has_control_rig = False
        if self.__current_path:
            stage = omni.usd.get_context(self.__usd_context_name).get_stage()
            prim = stage.GetPrimAtPath(self.__current_path)
        if prim:
            if prim.HasAttribute("controlRig:forwardAxis") and prim.HasAttribute("controlRig:upAxis"):
                self.__has_control_rig = True
                forward_value = prim.GetAttribute("controlRig:forwardAxis").Get()
                up_value = prim.GetAttribute("controlRig:upAxis").Get()
                if forward_value:
                    forward_axis = forward_value
                if up_value:
                    up_axis = up_value

            curr_time = omni.timeline.get_timeline_interface().get_current_time()
            world_transform = UsdGeom.XformCache(curr_time).GetLocalToWorldTransform(prim)
            ret, scale_orient_mat, scale, rotation_mat, translation, _ = world_transform.Factor()
            rotation_mat.Orthonormalize(False)
            abs_rotation = Gf.Rotation.DecomposeRotation3(
                        rotation_mat, Gf.Vec3d.XAxis(), Gf.Vec3d.YAxis(), Gf.Vec3d.ZAxis(), 1.0
                    )

            self.__items['position'].value = translation
            self.__items['rotation'].value = abs_rotation
        else:
            self.__items['position'].value = [0, 0, 0]
            self.__items['rotation'].value = [0, 0, 0]
        self.__set_drawing_transform('forward_start', 'forward_end', 'forward_text_pos', forward_axis)
        self.__set_drawing_transform('up_start', 'up_end', 'up_text_pos', up_axis)
        self._item_changed(None)

    def __set_drawing_transform(
        self, start_id: str,
        end_id: str,
        text_pos_id: str,
        axis: str,
        line_length: int = 50,
        text_offset: int = 60
    ):
        dir = [0.0, 0.0, 0.0]
        if axis in ["X", "x"]:
            dir = [1.0, 0.0, 0.0]
        if axis in ["Y", "y"]:
            dir = [0.0, 1.0, 0.0]
        if axis in ["Z", "z"]:
            dir = [0.0, 0.0, 1.0]
        if axis in ["-X", "-x", "MINUS X"]:
            dir = [-1.0, 0.0, 0.0]
        if axis in ["-Y", "-y", "MINUS Y"]:
            dir = [0.0, -1.0, 0.0]
        if axis in ["-Z", "-z", "MINUS Z"]:
            dir = [0.0, 0.0, -1.0]
        self.__items[end_id].value = [line_length * dir[0], line_length * dir[1], line_length * dir[2]]
        self.__items[start_id].value = [0.0, 0.0, 0.0]
        self.__items[text_pos_id].value = [text_offset * dir[0], text_offset * dir[1], text_offset * dir[2]]


class AnimPreviewWidget:
    def __init__(self, parent, preview_model: AnimPreviewModel, show_source_widgets=True, *ui_args, **ui_kw_args):
        """AnimPreviewWidget constructor
        Args:
            preview_model (AnimPreviewModel): The model that interfaces with the UsdContext and Timeline.
            *ui_args, **ui_kw_args: Additional arguments to pass to the ViewportWidget's parent frame
        """

        self.__parent = parent

        self.__playbutton = None
        self.__camera_manip = None
        self.__follow_skeleton = True
        self.__cam_distance = 500
        self.__forward_up_axes_model = ForwardUpAxesModel(preview_model.context_name)
        self.__scene_view = None
        self.__vp_widget = None
        self.__ui_container = None
        self.__camera_button = None
        self.__loading_text = None
        self.__anim_source = None
        self.__skel_source = None
        self.__timeline_view = None
        self.__joint_compare_window = None
        self.__loop_button = None
        self.__track_count = 0
        self.__annotation_count = 0

        self.__model:AnimPreviewModel = preview_model
        self.__show_source_widgets = show_source_widgets

        self.__show_axes = True

        self.__preview_mode = PlayMode.STOP

        self.__build_ui_args = ui_args
        self.__build_ui_kw_args = ui_kw_args
        self.__annotation_delegate = None

        self.__ui_container = ui.Frame(name="AnimPreviewWidgetFrame", build_fn=self.build_ui)
        # self.__ui_container.rebuild()

        self.__model.register_animation_loaded(self._on_animation_loaded)
        self.__model.register_animation_changed(self._on_animation_changed)
        self.__model.register_skeleton_loaded(self._on_skeleton_loaded)
        self.__model.register_skeleton_changed(self._on_skeleton_changed)
        self.__model.register_stage_loaded(self._on_preview_stage_loaded)

        self.__model._skel_source_model.add_prim_delete_callback_fn(self._delete_skel_source_cb)
        self.__model._anim_source_model.add_prim_delete_callback_fn(self._delete_anim_source_cb)

        self.__timeline_event_sub = self.__model.timeline.get_timeline_event_stream().create_subscription_to_pop(
            self.__on_timeline_event
        )

        self._skeleton_prim_selector:PrimSearchWidget = None
        self._clip_prim_selector:PrimSearchWidget = None
        self._skeleton_prim_paths = []
        self._clip_prim_paths = []

    def __del__(self):
        self.destroy()

    def destroy(self):
        self.__model.unregister_animation_loaded(self._on_animation_loaded)
        self.__model.unregister_animation_changed(self._on_animation_changed)
        self.__model.unregister_skeleton_loaded(self._on_skeleton_loaded)
        self.__model.unregister_skeleton_changed(self._on_skeleton_changed)
        self.__model.unregister_stage_loaded(self._on_preview_stage_loaded)
        self.__model._skel_source_model.remove_prim_delete_callback_fn(self._delete_skel_source_cb)
        self.__model._anim_source_model.remove_prim_delete_callback_fn(self._delete_anim_source_cb)
        self.__track_count = 0
        self.__annotation_count = 0

        self.__timeline_event_sub = None
        if self.__playbutton:
            self.__playbutton.destroy()
            self.__playbutton = None
        if self.__camera_manip:
            self.__camera_manip.destroy()
            self.__camera_manip = None
        if self.__scene_view:
            self.__scene_view.destroy()
            self.__scene_view = None
        if self.__vp_widget:
            self.__vp_widget.destroy()
            self.__vp_widget = None
        if self.__ui_container:
            self.__ui_container.destroy()
            self.__ui_container = None
        if self.__camera_button:
            self.__camera_button.destroy()
            self.__camera_button = None
        if self.__loading_text:
            self.__loading_text.destroy()
            self.__loading_text = None
        if self.__anim_source:
            self.__anim_source.destroy()
            self.__anim_source = None
        if self.__skel_source:
            self.__skel_source.destroy()
            self.__skel_source = None
        if self.__joint_compare_window:
            self.__joint_compare_window.clean()
            self.__joint_compare_window = None
        if self.__timeline_view:
            self.__timeline_view.destroy()
            self.__timeline_view = None
        if self.__loop_button:
            self.__loop_button.destroy()
            self.__loop_button = None

        if self._skeleton_prim_selector:
            self._skeleton_prim_selector.destroy()
            self._skeleton_prim_selector = None

        if self._clip_prim_selector:
            self._clip_prim_selector.destroy()
            self._clip_prim_selector = None

    def _clear_camera_manip(self):
        if self.__camera_manip is not None:
            self.__camera_manip.destroy()
            self.__camera_manip = None

    def _delete_skel_source_cb(self, source:SourceModel):
        current = self.__model.skel_source_model.get_current_source()
        if current.source_path_in_stage == source.source_path_in_stage:
            if self.__model.timeline.is_playing():
                self.__model.pause()
            self._skeleton_prim_selector.set_value("", run_callbacks=False)
            self._clip_prim_selector.set_value("")
            self.reset_scene()
            asyncio.ensure_future(self.__parent._delete_skel_source_cb())

    def _delete_anim_source_cb(self, source:SourceModel):
        current = self.__model.anim_source_model.get_current_source()
        if current.source_path_in_stage == source.source_path_in_stage:
            # Stop animation playback and disconnect the animation
            # relationship from the current skeleton
            if self.__model.timeline.is_playing():
                self.__model.pause()
            self._clear_camera_manip()
            self.update_from_stage()
            self._clip_prim_selector.set_value("")

            self.__parent._restore_after_drag()

    def __on_timeline_play(self):
        """ Called when the timeline enters play mode
        """
        self.__preview_mode = PlayMode.PLAY
        if self.__playbutton is not None:
            self.__playbutton.style = PAUSE_BUTTON_STYLE

    def __on_timeline_pause(self):
        """ Called when the timeline is paused
        """
        self.__preview_mode = PlayMode.PAUSE
        if self.__playbutton is not None:
            self.__playbutton.style = PLAY_BUTTON_STYLE

    def __on_timeline_stop(self):
        """ Called when the timeline is stopped
        """
        self.__preview_mode = PlayMode.STOP
        if self.__playbutton is not None:
            self.__playbutton.style = PLAY_BUTTON_STYLE

    def __on_playpause_pressed(self):
        """ Called when the play/pause button is clicked
        """
        if self.__model.timeline.is_playing():
            self.__model.pause()
        else:
            self.__model.play()

    def __on_step_pressed(self):
        """ Called when the step forward button is clicked
        """
        self.__model.pause()
        self.__model.timeline.forward_one_frame()

    def __on_step_back_pressed(self):
        """ Called when the step back button is clicked
        """
        self.__model.pause()
        self.__model.timeline.rewind_one_frame()

    def __on_start_pressed(self):
        """ Called when the start button is clicked
        """
        self.__model.pause()
        self.__model.timeline.set_current_time(self.__model.timeline.get_start_time())

    def __on_end_pressed(self):
        """ Called when the end button is clicked
        """
        self.__model.pause()
        self.__model.timeline.set_current_time(self.__model.timeline.get_end_time())

    def __on_loop_pressed(self):
        """ Called when the loop button is clicked"""
        looping = not self.__model.timeline.is_looping()
        self.__model.timeline.set_looping(looping)
        if self.__loop_button:
            self.__loop_button.checked = looping

    def __on_timeline_event(self, event: carb.events.IEvent):
        """ Callback for timeline events, refreshes button states.
        """
        if event.type == int(omni.timeline.TimelineEventType.PAUSE):
            self.__on_timeline_pause()
        elif event.type == int(omni.timeline.TimelineEventType.PLAY):
            self.__on_timeline_play()
        elif event.type == int(omni.timeline.TimelineEventType.STOP):
            self.__on_timeline_stop()
        elif event.type == int(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED):
            if self.__follow_skeleton and self.__camera_manip and self.__model.skel_geometry:
                from .annotation.utils import time_to_timecode
                current_time = time_to_timecode(self.__model.timeline.get_current_time(), self.__model.timeline)
                orbit_center = self.__model.skel_geometry.get_center(current_time)
                dpos = orbit_center - self.__camera_manip.world_orbit_center
                self.__camera_manip.world_orbit_center = orbit_center
                self.__camera_manip.refresh(self.__camera_manip.position + dpos)

    @property
    def viewport_api(self):
        """ Access to the underying ViewportAPI object to control renderer, resolution
        """
        if self.__vp_widget is None:
            return None

        return self.__vp_widget.viewport_api

    @property
    def scene_view(self):
        """ Access to the omni.ui.scene.SceneView
        """
        return self.__scene_view

    @property
    def camera_manipulator(self):
        """ Access to the camera manipulator that can be used to control the preview camera
        """
        return self.__camera_manip

    @property
    def follow_skeleton(self):
        return self.__follow_skeleton

    @property
    def play_mode(self):
        return self.__preview_mode

    def set_style(self, *args, **kwargs):
        """ Sets the style of the main container
        """
        self.__ui_container.set_style(*args, **kwargs)

    def show_loading(self, visible: bool = True):
        """ Toggles loading text
         Args:
            visible: loading text is visible or not
        """
        if self.__loading_text is not None:
            self.__loading_text.visible = visible

    def _screen_to_ndc(self, screen_x: float, screen_y: float):
        """ Converts screen coordinates (in the app windows's space) to viewport NDC
        """
        x = screen_x - self.scene_view.screen_position_x
        y = screen_y - self.scene_view.screen_position_y
        x = x / float(self.scene_view.computed_content_width) * 2.0 - 1.0
        y = (1.0 - y / float(self.scene_view.computed_content_height)) * 2.0 - 1.0
        return x, y

    def is_mouse_over_skeleton(self, mouse_x: float, mouse_y: float) -> bool:
        """ Returns whether the mouse is over the skeleton
        Args:
            mouse_x: horizontal mouse position in the app window's space
            mouse_y: vertical mouse position in the app window's space
        """
        if not self.viewport_api:
            return True

        world_bbox = self.__model.get_skeleton_bbox()

        # Instead of computing the projection of the AABB we compute its bounding box in NDC
        ndc_min = self.viewport_api.world_to_ndc.Transform(world_bbox.GetCorner(0))
        ndc_max = Gf.Vec3d(ndc_min)
        for i_corner in range(1, 8):
            p = self.viewport_api.world_to_ndc.Transform(world_bbox.GetCorner(i_corner))
            for i_coord in range(3):
                ndc_min[i_coord] = min(p[i_coord], ndc_min[i_coord])
                ndc_max[i_coord] = max(p[i_coord], ndc_max[i_coord])
        mouse_ndc_x, mouse_ndc_y = self._screen_to_ndc(mouse_x, mouse_y)

        return ndc_min[0] <= mouse_ndc_x <= ndc_max[0] and ndc_min[1] <= mouse_ndc_y <= ndc_max[1]

    def _refresh_compatibility_ui(self):
        # TODO: set icon
        pass

    def _on_annotations_changed(self, model: AnnotationSet):
        if model is not None:
            track_count = len(model.tracks.keys())
            annotation_count = len(model.annotations)
            # We don't refresh when the annotation count is the same but the track count isn't
            # This is a limitation, but it is necessary to avoid the loss of the delegate during annotation
            #    start/end editing.
            # One solution would be to refresh the UI when the dragging is finished.
            needs_rebuild = track_count != self.__track_count and annotation_count != self.__annotation_count
            self.__track_count = track_count
            self.__annotation_count = annotation_count
            if needs_rebuild:
                self.__ui_container.rebuild()

    def _on_animation_changed(
        self,
        source_path: str,
        target_path: str,
        external_url: str,
        annotations: AnnotationSet
    ):
        """ Called when the current animation was changed
        """
        if self.__joint_compare_window and self.__joint_compare_window.visible:
            self._on_joint_match_clicked(True)
        self.__model.set_show_active_bones(True)

        # TODO: rebuild is actually needed when the size of widgets (e.g. height of the TimelineView) changes
        self.__ui_container.rebuild()
        # self._refresh_compatibility_ui()  # this is needed if we don't rebuild

        if annotations is not None:
            annotations.add_value_changed_fn(self._on_annotations_changed)
            self._on_annotations_changed(annotations)

    def _on_animation_loaded(
        self,
        source_path: str,
        target_path: str,
        source_stage: Usd.Stage,
        external_url: str,
        annotations: AnnotationSet
    ):
        """ Called when a new animation was loaded.
        """
        # Changed callback is also called in this case, no further action is needed
        pass

    def _on_skeleton_changed(self, source_path: str, target_path: str):
        """ Called when the current skeleton was changed
        """
        self._refresh_compatibility_ui()

        if self.__joint_compare_window and self.__joint_compare_window.visible:
            self._on_joint_match_clicked(True)
        self.__model.set_show_active_bones(True)

        self.set_show_axes(self.__show_axes)
        self.__forward_up_axes_model.set_skeleton(self.__model.get_skeleton())

        # OM-85112: no need to place camera until correct geometry center is calculate using compute_geo_center() in animation_preview_model
        if self.__model.skel_geometry is not None:
            self.__cam_distance = self.__model.skel_geometry.height * 3.0
            if self.__camera_manip:
                self.__camera_manip.set_distance(self.__cam_distance, self.__model.skel_geometry.center)
            self.__forward_up_axes_model.update_transform()

    def _on_skeleton_loaded(self, source_path: str, target_path: str, source_stage: Usd.Stage):
        """ Called when a new skeleton was loaded.
        """
        # Changed callback is also called in this case, no further action is needed
        pass

    def _on_preview_stage_loaded(self):
        self.__ui_container.rebuild()

    def _on_clear_anims(self):
        """ Called when the clear animations button was clicked
        """
        if self.__joint_compare_window and self.__joint_compare_window.visible:
            self._on_joint_match_clicked(False)
        self.__model.set_show_active_bones(False)
        self.__model.stop()
        self.__model.remove_animations()
        self.__ui_container.rebuild()

    def _on_clear_skels(self):
        """ Called when the clear skeletons button was clicked
        """
        if self.__joint_compare_window and self.__joint_compare_window.visible:
            self._on_joint_match_clicked(False)
        self.__model.set_show_active_bones(False)
        self.__model.remove_skeletons()
        source = self.__model.skel_source_model.get_current_source()
        self._on_skeleton_loaded(source.source_path_in_stage, source.target_path_in_stage, None)

    def reset_scene(self):
        """ Resets the scene and the UI to its default.
        """
        self._clear_camera_manip()
        self.__model.reset_scene()
        self.__ui_container.rebuild()

    def sync_up_axis_with_current_stage(self):
        self.__model.sync_up_axis_with_current_stage()

    def _on_clip_double_clicked(self, annotation: Annotation, x: float, y: float, b: int, s: int):
        """ Called when a clip (annotation) was clicked in the TimelineView
        """
        context = omni.usd.get_context()
        if annotation is not None and annotation.source is not None and not annotation.source.is_external:
            path = str(annotation.source.source_path_in_stage)
            if path is not None:
                context.get_selection().set_selected_prim_paths([path], True)

    def _on_switch_view(self, side: ViewSide):
        if self.__camera_manip:
            # reset rotation so when we animate again, it starts from zero rotation
            if not self.__follow_skeleton and self.__model.skel_geometry:
                # the orbit center could be anywhere now, let's move it back so the camera looks at the T-pose skeleton
                self.__camera_manip.world_orbit_center = self.__model.skel_geometry.center
            self.__camera_manip.set_rotation(0)
            self.__camera_manip.switch_view(side, self.__cam_distance)

    def _on_animate_cam_changed(self, value: bool):
        self.__camera_manip.rotating = value

    def _on_follow_skeleton_changed(self, value: bool):
        self.__follow_skeleton = value
        if self.__follow_skeleton:
            from .annotation.utils import time_to_timecode
            current_time = time_to_timecode(self.__model.timeline.get_current_time(), self.__model.timeline)
            orbit_center = self.__model.skel_geometry.get_center(current_time)
        else:
            orbit_center = self.__model.skel_geometry.center
        dpos = orbit_center - self.__camera_manip.world_orbit_center
        self.__camera_manip.world_orbit_center = orbit_center
        self.__camera_manip.refresh(self.__camera_manip.position + dpos)

    def get_show_axes(self):
        return self.__show_axes

    def set_show_axes(self, show):
        self.__show_axes = show
        self.__forward_up_axes_model.set_draw("draw_forward_axis", show)
        self.__forward_up_axes_model.set_draw("draw_up_axis", show)

    def _show_camera_context_menu(self):
        show_camera_context_menu(
            self,
            ViewSide.DIAGONAL,  # TODO
            self.camera_manipulator.rotating,
            self.__follow_skeleton,
            module_path=MODULE_PATH,
            position=(self.__camera_button.screen_position_x, self.__camera_button.screen_position_y + self.__camera_button.height)
        )

    def _show_visibility_context_menu(self):
        show_visibility_context_menu(
            self,
            self.__model,
            self.__model.get_show_skeleton(),
            self.__model.get_show_mesh(),
            self.__show_axes,
            position=(self.__visibility_button.screen_position_x, self.__visibility_button.screen_position_y + self.__visibility_button.height)
        )

    def _on_joint_match_clicked(self, keep_window: bool = False):
        if not keep_window and self.__joint_compare_window and self.__joint_compare_window.visible:
            self.__joint_compare_window.hide()
            self.__joint_compare_window.clean()
            self.__joint_compare_window = None
            return
        compatibility = self.__model.get_compatibility()
        if compatibility is not None:
            skel_joints = get_joint_list(self.__model.skeleton_prim)
            skel_joints = [str(j) for j in skel_joints]
            anim_joints = get_joint_list(self.__model.animation_prim)
            anim_joints = [str(j) for j in anim_joints]
            common_joints = compatibility[1]
            anim_only_joints = compatibility[2]
            skel_only_joints = compatibility[3]
            if self.__joint_compare_window:
                self.__joint_compare_window.clean()
            joint_prim_paths = [str(p) for p in self.__model.get_joint_prim_paths()]
            self.__joint_compare_window = JointCompareWindow(
                context=self.__model.context,
                joint_prim_paths=joint_prim_paths,
                joint_lists=[anim_joints, skel_joints],
                captions=[
                    f'Animation joint count: {len(anim_joints)} (non-matching: {len(anim_only_joints)})',
                    f'Skeleton joint count: {len(skel_joints)} (not animated: {len(skel_only_joints)})'
                ],
                title='Joint comparison',
                intersections=common_joints,
                uniques=[anim_only_joints, skel_only_joints]
            )

    def __should_build_camera_manipulator(self):
        return self.viewport_api is not None \
            and self.viewport_api.camera_path is not None \
            and not self.viewport_api.camera_path.isEmpty

    def __build_viewport_widget(self):
        if not self.__model.stage_active or self.__parent.is_hint_stack_visible:
            return None

        # Create the ViewportWidget, forwarding all of the arguments to this constructor
        context_name = self.__model.context_name
        # GPU Crash Workaround: Use a constant resolution, rather than fill frame.
        # Notice: change to fill frame, not found crash yet. should revert this if unstable.
        with ui.ZStack(name="zs_ViewPortWidget", height=ui.Fraction(1), style={"margin": 0, "padding": 0,}):
            self.__vp_widget = ViewportWidget(usd_context_name=context_name, resolution='fill_frame', #(640,340),
                                              *self.__build_ui_args, **self.__build_ui_kw_args)

    def update_from_stage(self, stage:Optional[Usd.Stage]=None):
        skeleton_prim_paths = []
        clip_prim_paths = []

        stage = stage or omni.usd.get_context().get_stage()

        if stage:
            for prim in stage.Traverse():
                if prim.IsA(UsdSkel.Root):
                    skeleton_prim_paths.append(prim)
                elif prim.IsA(UsdSkel.Animation):
                    clip_prim_paths.append(prim)

        self._skeleton_prim_paths = skeleton_prim_paths
        self._clip_prim_paths = clip_prim_paths

    def rebuild(self):
        self.__ui_container.rebuild()

    def _get_model_active_skel_path(self) -> str:
        if not self.__model.skel_source_model.get_current_source():
            return ""

        stage = omni.usd.get_context().get_stage()
        if not stage:
            return ""

        skel_path = self.__model.skel_source_model.get_current_source().source_path_in_stage
        skel_prim = stage.GetPrimAtPath(skel_path)

        if bool(skel_prim) and skel_prim.IsA(UsdSkel.Skeleton):
            skel_prim = skel_prim.GetParent()
            if not bool(skel_prim) or not skel_prim.IsA(UsdSkel.Root):
                return ""

        skel_name = skel_prim.GetPath() if bool(skel_prim) else ""
        return str(skel_name)

    def _get_model_active_anim_path(self) -> str:
        if not self.__model.anim_source_model.get_current_source():
            return ""

        anim_path = self.__model.anim_source_model.get_current_source().source_path_in_stage
        anim_prim = omni.usd.get_context().get_stage().GetPrimAtPath(anim_path)
        anim_name = anim_prim.GetPath() if bool(anim_prim) else ""
        return str(anim_name)

    def update_selectors(self):
        if self._skeleton_prim_selector:
            self._skeleton_prim_selector.set_value(self._get_model_active_skel_path(), run_callbacks=False)
        if self._clip_prim_selector:
            self._clip_prim_selector.set_value(self._get_model_active_anim_path(), run_callbacks=False)

    def build_ui(self):
        enable_skeleton_picker = bool(self.__model._skeleton)
        enable_buttons = self.__model.stage_active and self.__model.has_animation()
        if self.__vp_widget:
            self.__vp_widget.destroy()

        self.update_from_stage()

        with ui.VStack(name="vs_preview_main", height=ui.Percent(100)):
            ## buttons at top
            with ui.HStack(name="hs_target_buttons", height=40):
                self.__camera_button = ui.Button(
                    name="button_camera",
                    width=32,
                    height=32,
                    style=CAMERA_BUTTON_STYLE,
                    clicked_fn=self._show_camera_context_menu,
                    enabled=enable_buttons
                )

                self.__visibility_button = ui.Button(
                    name="button_visibility",
                    width=32,
                    height=32,
                    style=VISIBILITY_BUTTON_STYLE,
                    clicked_fn=self._show_visibility_context_menu,
                    enabled=self.__model.stage_active
                )

                if self.__show_source_widgets:
                    ui.Spacer(width=6)

                    self._skeleton_prim_selector = PrimSearchWidget(self._skeleton_prim_paths,
                                                                    value=self._get_model_active_skel_path() or "",
                                                                    enabled=enable_skeleton_picker,
                                                                    full_prim_name=True,
                                                                    icon=SKEL_ICON)

                    self._skeleton_prim_selector.add_changed_callback(self.__parent._skeleton_prim_selector_on_changed_cb)

            ## viewport
            viewport_zstack = ui.ZStack(name="zs_viewport_main", content_clipping=1,
                                        width=ui.Fraction(1))
            with viewport_zstack:
                ui.Spacer(name="spacer_zs_viewport", height=ui.Percent(100))
                # Add a background Rectangle that is black by default, but can change with a set_style
                ui.Rectangle(style_type_name_override='ViewportBackgroundColor',
                             height=ui.Percent(100),
                             style={'ViewportBackgroundColor': {'background_color': 0xff000000}})

                self.__build_viewport_widget()

                # Add the omni.ui.scene.SceneView that is going to host the camera-manipulator
                self.__scene_view = sc.SceneView(aspect_ratio_policy=sc.AspectRatioPolicy.STRETCH)

                # And finally add the camera-manipulator into that view
                if self.__should_build_camera_manipulator():
                    with self.__scene_view.scene:
                        ForwardUpAxesManipulator(model=self.__forward_up_axes_model)

                        skelgeom = self.__model.skel_geometry
                        if skelgeom is None:
                            world_orbit_center = [0, 90, 0]  # for the default skeleton
                        else:
                            world_orbit_center = skelgeom.center

                        if self.__camera_manip is not None:
                            self.__camera_manip.destroy()

                        self.__camera_manip = AnimatedOrbitViewportCameraManipulator(
                            self.viewport_api,
                            world_orbit_center=world_orbit_center,
                            distance=self.__cam_distance
                        )
                        model = self.__camera_manip.model

                        # Let's disable any undo for these movements as we're a preview-window
                        model.set_ints('disable_undo', [1])

                        # We'll also let the Viewport automatically push view and projection changes into our scene-view
                        self.viewport_api.add_scene_view(self.__scene_view)
                        self.__camera_manip.switch_view(ViewSide.DIAGONAL, self.__cam_distance)

                self.__loading_text = ui.Label(
                    'Loading stage...',
                    alignment=ui.Alignment.CENTER,
                    style={'font_size': 30}
                )
                self.__loading_text.visible = False

            ## playback buttons
            with ui.VStack(name="vs_playback_main", direction=ui.Direction.BOTTOM_TO_TOP, height=40):
                with ui.HStack(height=PLAY_BUTTON_SIZE+8):
                    # ui.Spacer()
                    with ui.ZStack(width=PLAY_BUTTON_SIZE*6):  # 6 buttons
                        ui.Rectangle(name="rect_playback_buttons", width=PLAY_BUTTON_SIZE*6, height=PLAY_BUTTON_SIZE, alignment=ui.Alignment.CENTER_TOP)
                        with ui.HStack(name="vs_playback_buttons", alignment=ui.Alignment.CENTER):
                            ui.Button(
                                name="button_start",
                                width=PLAY_BUTTON_SIZE,
                                height=PLAY_BUTTON_SIZE,
                                clicked_fn=WeakMethod(self.__on_start_pressed),
                                style=START_BUTTON_STYLE,
                                enabled=enable_buttons
                            )

                            ui.Button(
                                name="button_back",
                                width=PLAY_BUTTON_SIZE,
                                height=PLAY_BUTTON_SIZE,
                                clicked_fn=WeakMethod(self.__on_step_back_pressed),
                                style=PREVIOUS_FRAME_BUTTON_STYLE,
                                enabled=enable_buttons
                            )

                            playpause_style = PLAY_BUTTON_STYLE
                            if self.__preview_mode == PlayMode.PLAY:
                                playpause_style = PAUSE_BUTTON_STYLE
                            self.__playbutton = ui.Button(
                                name="button_playpausev",
                                width=PLAY_BUTTON_SIZE,
                                height=PLAY_BUTTON_SIZE,
                                clicked_fn=WeakMethod(self.__on_playpause_pressed),
                                style=playpause_style,
                                enabled=enable_buttons
                            )

                            ui.Button(
                                name="button_step",
                                width=PLAY_BUTTON_SIZE,
                                height=PLAY_BUTTON_SIZE,
                                clicked_fn=WeakMethod(self.__on_step_pressed),
                                style=NEXT_FRAME_BUTTON_STYLE,
                                enabled=enable_buttons
                            )

                            ui.Button(
                                name="button_end",
                                width=PLAY_BUTTON_SIZE,
                                height=PLAY_BUTTON_SIZE,
                                clicked_fn=WeakMethod(self.__on_end_pressed),
                                style=END_BUTTON_STYLE,
                                enabled=enable_buttons
                            )

                            self.__loop_button = ui.Button(
                                name="button_loop",
                                width=PLAY_BUTTON_SIZE,
                                height=PLAY_BUTTON_SIZE,
                                clicked_fn=WeakMethod(self.__on_loop_pressed),
                                style=LOOP_BUTTON_STYLE,
                                enabled=enable_buttons,
                                checked=self.__model.timeline.is_looping()
                            )

                    if self.__anim_source:
                        self.__anim_source.destroy()

                    self._clip_prim_selector = PrimSearchWidget(self._clip_prim_paths,
                                                                value=self._get_model_active_anim_path() or "",
                                                                enabled=enable_skeleton_picker,
                                                                opens_up=True,
                                                                full_prim_name=False,
                                                                icon=SKELANIM_ICON)

                    self._clip_prim_selector.add_changed_callback(self.__parent._clip_prim_selector_on_changed_cb)

            annotation_model = self.__model.annotation_model
            timeline = self.__model.context.get_timeline()
            if timeline.get_time_codes_per_seconds() < 1e-3 or \
                    timeline.get_end_time() - timeline.get_start_time() < 1e-3:
                # this timeline is not properly initialized, i. e., the time codes per second is 0 or
                # start_time is bigger than end time
                timeline.set_start_time(0)
                timeline.set_end_time(10)
                timeline.set_time_codes_per_second(30)

            self.__stage_range_model = StageRangeModel(self.__model.context, max_range_read_only=True)
            self.__stage_range_model.add_item_changed_fn(self._on_range_changed)
            if annotation_model is None:
                with ui.HStack(height=40, name="timeline_view_hstack",
                               style={"HStack::timeline_view_hstack": {"margin_width": 5}}):
                    self.__timeline_view = TimelineView(
                        build_range=False,
                        range_model=self.__stage_range_model,
                    )
            else:
                track_count = min(MAX_TRACKS_TO_SHOW, self.__track_count + 1)
                track_count = max(MIN_TRACKS_TO_SHOW, track_count)
                track_height = 30
                # TODO: destroy old one?
                self.__annotation_delegate = AnnotationDelegate(
                    model=annotation_model,
                    track_height=track_height,
                    timeline_name=self.__model.context_name
                )
                self.__annotation_delegate.set_clip_double_clicked_fn(self._on_clip_double_clicked)
                height = 65 + self.__annotation_delegate.track_height * track_count
                with ui.HStack(height=height, name="timeline_view_hstack",
                               style={"HStack::timeline_view_hstack": {"margin_width": 5}}):
                    self.__timeline_view = TimelineView(
                        build_content=True,
                        build_range=True,
                        range_model=self.__stage_range_model,
                        timeline_content_delegate=self.__annotation_delegate,
                    )

    def _on_range_changed(self, model, item):
        if item is not None and item.name_model.as_string == 'View Range':
            fps = self.__stage_range_model.fps
            new_start = item.start / fps
            new_end = item.end / fps
            self.__model.timeline.set_zoom_range(new_start, new_end)
            self.__model.timeline.set_current_time(new_start)
