# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#


import asyncio
import carb
import carb.events
import omni.kit.app
import omni.kit.context_menu
import omni.timeline
import omni.ui as ui
from functools import partial
from typing import Callable, Optional
from .annotation_model import Annotation, AnnotationSet
from .annotation_clip_widget import AnnotationClipWidget, WidgetSide, DRAG_HANDLER_WIDTH
from .timeline_context_menu import timeline_menu_list
from omni.anim.widget.timeline import TimelineContentDelegate, TimelineGridModel
from .utils import time_to_timecode, timecode_to_time


DEFAULT_COLOR = 0xFFAA5500
DEFAULT_COLOR_CURRENT_TIME = 0xFF008800
DEFAULT_COLOR_READONLY = 0xFF656565
DEFAULT_COLOR_CURRENT_TIME_READONLY = 0xFF8D8D90


class DragHandler():
    def __init__(
        self,
        x: float,
        y: float,
        widget_placer: ui.Placer,
        track_clips: list,
        widget: AnnotationClipWidget,
        timeline_grid_model: TimelineGridModel,
        timeline_name: str,
    ):
        assert(widget_placer is not None)
        assert(widget is not None)
        assert(timeline_grid_model is not None)
        assert(track_clips is not None)
        self._origin_x = x
        self._origin_y = y
        self._widget = widget
        self._widget_placer = widget_placer
        self._track_clips = track_clips
        self._track_clips.sort(key=lambda data: data[0].offset_x.value)
        self._timeline_grid_model = timeline_grid_model
        self._on_drag_fn = None
        self._neighbor_placer = None
        self._placer_origin_x = widget_placer.offset_x.value
        self._placer_origin_w = widget_placer.width.value
        two_drag_handler_width = DRAG_HANDLER_WIDTH * 2
        view_width = int(self._timeline_grid_model.range_length_inclusive) * self._timeline_grid_model.frame_width
        widget_side = widget.contain_type()
        if widget_side == WidgetSide.Center:
            self._value_min = 0
            self._value_max = view_width
            for placer, annotation in self._track_clips:
                if self._placer_origin_x > placer.offset_x.value:
                    if placer.offset_x.value >= 0:
                       self._value_min += placer.width.value
                else:
                    if placer.offset_x.value + placer.width.value <= view_width:
                       self._value_max -= placer.width.value
            self._on_drag_fn = self._handle_move

        elif widget_side == WidgetSide.Left:
            self._value_min = 0
            self._value_max = min(view_width, self._placer_origin_x + self._placer_origin_w - two_drag_handler_width)
            for placer, annotation in self._track_clips:
                if placer.offset_x.value < self._placer_origin_x:
                    self._value_min = max(self._value_min, placer.offset_x.value + two_drag_handler_width)
                    self._neighbor_placer = placer
            self._on_drag_fn = self._handle_left_drag

        elif widget_side == WidgetSide.Right:
            self._value_min = max(two_drag_handler_width, 0 - self._placer_origin_x)
            self._value_max = view_width - self._placer_origin_x
            for placer, annotation in self._track_clips:
                if placer.offset_x.value > self._placer_origin_x:
                    neighbor_end = placer.offset_x.value + placer.width.value - two_drag_handler_width
                    self._value_max = min(self._value_max, neighbor_end - self._placer_origin_x)
                    self._neighbor_placer = placer
                    break
            self._on_drag_fn = self._handle_right_drag

        # save state
        self._timeline: omni.timeline.Timeline = omni.timeline.get_timeline_interface(timeline_name)
        self._timeline.pause()
        self._original_time = self._timeline.get_current_time()
        self._timeline_playing = self._timeline.is_playing()
        self._widget.selected = True

    def _handle_move(self, x: float, y: float, modifiers: int, is_pressed: bool):
        dx = x - self._origin_x
        self._widget_placer.offset_x =min(self._value_max, max(self._value_min, self._placer_origin_x + dx))
        if len(self._track_clips) > 1:
            if dx > 0: # move to right
                for i in range(1, len(self._track_clips)):
                    left_placer = self._track_clips[i-1][0]
                    min_left_offset = left_placer.offset_x + left_placer.width
                    cur_placer = self._track_clips[i][0]
                    cur_placer.offset_x = max(min_left_offset, cur_placer.offset_x.value)
            else:
                for i in range(len(self._track_clips)-1, 0, -1):
                    cur_placer = self._track_clips[i-1][0]
                    right_placer = self._track_clips[i][0]
                    max_right_offset = right_placer.offset_x - cur_placer.width
                    cur_placer.offset_x = min(max_right_offset, cur_placer.offset_x.value)

        start_time = int(self._timeline_grid_model.transform_position_to_timeline(self._widget_placer.offset_x))
        self._timeline.set_current_time(timecode_to_time(start_time, self._timeline))

    def _handle_left_drag(self, x: float, y: float, modifiers: int, is_pressed: bool):
        dx = x - self._origin_x
        self._widget_placer.offset_x = min(self._value_max, max(self._value_min, self._placer_origin_x + dx))
        self._widget_placer.width = ui.Length(self._placer_origin_x + self._placer_origin_w - self._widget_placer.offset_x.value)

        if self._neighbor_placer is not None and dx < 0:
            if self._widget_placer.offset_x.value < self._neighbor_placer.offset_x.value + self._neighbor_placer.width.value:
                self._neighbor_placer.width = ui.Length(self._widget_placer.offset_x.value - self._neighbor_placer.offset_x.value)

        start_time = int(self._timeline_grid_model.transform_position_to_timeline(self._widget_placer.offset_x))
        self._timeline.set_current_time(timecode_to_time(start_time, self._timeline))

    def _handle_right_drag(self, x: float, y: float, modifiers: int, is_pressed: bool):
        dx = x - self._origin_x
        width =  min(self._value_max, max(self._value_min, self._placer_origin_w + dx))
        self._widget_placer.width = ui.Length(width)

        if self._neighbor_placer is not None:
            if self._widget_placer.offset_x.value + self._widget_placer.width.value > self._neighbor_placer.offset_x.value:
                end = self._neighbor_placer.offset_x.value + self._neighbor_placer.width.value
                self._neighbor_placer.offset_x = self._widget_placer.offset_x.value + self._widget_placer.width.value
                self._neighbor_placer.width = ui.Length(end - self._neighbor_placer.offset_x.value)

        end_pos = self._placer_origin_x + width
        end_time = int(self._timeline_grid_model.transform_position_to_timeline(end_pos))
        self._timeline.set_current_time(timecode_to_time(end_time, self._timeline))

    def restore(self):
        self._timeline.set_current_time(self._original_time)
        if self._timeline_playing:
            self._timeline.play()
        self._widget.selected = False

    def update_models(self, scale: float):
        for placer, clip in self._track_clips:
            start_time = self._timeline_grid_model.transform_position_to_timeline(placer.offset_x) / scale
            end_pos = placer.offset_x + placer.width
            end_time = self._timeline_grid_model.transform_position_to_timeline(end_pos) / scale
            end_time = max(start_time + 1, end_time)
            tag = clip.tag
            clip.set_values(tag, start_time, end_time)

    def __del__(self):
        self.destroy()

    def destroy(self):
        self._timeline_grid_model = None
        self._widget_placer = None
        self._timeline = None
        self._track_clips.clear()


class AnnotationDelegate(TimelineContentDelegate):
    """ Rendering delegate for an AnnotationSet to be used in TimelineView
    """
    def __init__(
        self,
        model: AnnotationSet = None,
        track_height: int = 32,
        recolor_current_time=True,
        timeline_name: Optional[str] = None
    ):
        self._clip_placers = {}
        self._clip_widgets = {}
        if model is None:
            self._model = AnnotationSet()
        else:
            self._model = model
        self.track_height = track_height
        if timeline_name is None:
            timeline_name = ''
        self._timeline_name = timeline_name
        self._timeline = omni.timeline.get_timeline_interface(timeline_name)
        self._timeline_sub = None
        if recolor_current_time:
            self._timeline_sub = self._timeline.get_timeline_event_stream().create_subscription_to_pop(
                self._on_timeline_event
            )
        self._timeline_fps_sub = omni.timeline.get_timeline_interface().get_timeline_event_stream().create_subscription_to_pop_by_type(
            event_type=omni.timeline.TimelineEventType.TIME_CODE_PER_SECOND_CHANGED,
            fn=self._on_timeline_fps_changed,
        )

        self._model_changed_sub = self._model.add_value_changed_fn(self._on_model_changed)
        main_context = omni.usd.get_context()
        self._stage_event_sub: carb.Subscription = main_context.get_stage_event_stream().create_subscription_to_pop(
            self._on_stage_event
        )
        self._selection: omni.usd.Selection = main_context.get_selection()
        self._clip_double_clicked_fn = None
        self._drag_handler: DragHandler = None
        stage = omni.usd.get_context().get_stage()
        self._fps_scale = stage.GetTimeCodesPerSecond() / model.time_codes_per_second
        super().__init__()

    def destroy(self):
        self._clip_placers = {}
        self._clip_widgets = {}
        # TODO: do not destroy model?
        # if self._model() is not None:
        #    self._model.destroy()
        if self._stage_event_sub:
            self._stage_event_sub.unsubscribe()
        self._stage_event_sub = None
        if self._timeline_sub:
            self._timeline_sub.unsubscribe()
        self._timeline_name = None
        self._timeline_sub = None
        if self._timeline_fps_sub:
            self._timeline_fps_sub.unsubscribe()
        self._timeline_fps_sub = None
        self._timeline = None
        if self._model_changed_sub is not None and self._model is not None:
            self._model.remove_value_changed_fn(self._model_changed_sub)
        self._model = None
        self._clip_double_clicked_fn = None
        self._drag_handler = None
        return super().destroy()

    @property
    def model(self):
        return self._model

    def set_clip_double_clicked_fn(self, fn: Callable[[Annotation, float, float, int, int], None]) -> None:
        """ Sets callback mouse double click callback function for all clips
        Args:
            fn: function to be called when a clip is double clicked
        """
        self._clip_double_clicked_fn = fn

    def show_context_menu(self):
        context_menu: omni.kit.context_menu.ContextMenuExtension = omni.kit.context_menu.get_instance()
        if context_menu is None:
            carb.log_warn("Context menu is disabled.")
            return

        menu_name = 'timeline_delegate_context_menu'
        objects = {'annotations': self._model, 'timeline_name': self._timeline_name}
        context_menu.show_context_menu(menu_name, objects, timeline_menu_list)

    def select_annotations(self, selected: bool = True):
        for _, widget in self._clip_widgets.items():
            widget.selected = selected
            if not selected:
                widget.end_edit()

    def _build_clip(self, clip_width: float, clip_data: Annotation, track_name: str):
        with ui.ZStack():
            clip_widget = self._clip_widgets.get(clip_data.name)
            if clip_widget is None:
                clip_widget = AnnotationClipWidget(
                    model=clip_data,
                    all_models=self._model,
                    timeline_name=self._timeline_name,
                    track_name=track_name,
                    on_clip_double_clicked=self._on_clip_double_clicked
                )
                self._clip_widgets[clip_data.name] = clip_widget
            else:
                clip_widget.set_track(track_name)
                clip_widget.rebuild()

    def _on_clip_double_clicked(self, annotation: Annotation, x: float, y: float, b: int, s: int):
        if self._drag_handler is not None:
            self._drag_handler.destroy()
            self._drag_handler = None

        if self._clip_double_clicked_fn:
            self._clip_double_clicked_fn(annotation, x, y, b, s)

    def _build_track(self, track_name: str, track_data: dict):
        with ui.ZStack():
            for clip in track_data:
                clip_placer = ui.Placer()
                self._update_clip(clip_placer, clip)
                self._clip_placers[clip.name] = clip_placer
                with clip_placer:
                    ui.Frame(
                        build_fn=partial(
                            self._build_clip,
                            clip_width=clip_placer.width.value,
                            clip_data=clip,
                            track_name=track_name)
                    )

    def _build_content(self):
        with ui.VStack(spacing=2):
            if len(self._model.tracks) == 0:
                ui.Frame(width=1, height=1)
            for track_name, track_data in self._model.tracks.items():
                ui.Frame(
                    build_fn=partial(self._build_track, track_name=track_name, track_data=track_data),
                    height=self.track_height,
                )
        self._grid_frame.set_mouse_pressed_fn(self._on_mouse_pressed_frame)
        self._grid_frame.set_mouse_released_fn(self._on_mouse_released_frame)
        self._grid_frame.set_mouse_moved_fn(self._on_mouse_move)

    def _update_clip(self, clip_placer: ui.Placer, clip: Annotation):
        if self._timeline_grid_model is not None:
            clip_offset_x = self._timeline_grid_model.transform_timeline_to_position(clip.start * self._fps_scale)
            clip_width = clip.length * self._timeline_grid_model.frame_width * self._fps_scale
            clip_placer.offset_x = ui.Pixel(clip_offset_x)
            clip_placer.width = ui.Pixel(clip_width)

    async def _update_clips(self, clips):
        # Async update must be done async for drawing to update
        for clip_placer, clip_data in clips:
            self._update_clip(clip_placer, clip_data)
        self._content_frame.rebuild()

    def _update_content(self):
        _update_clips = []
        for _, clips in self._model.tracks.items():
            for clip in clips:
                clip_placer = self._clip_placers.get(clip.name)
                if clip_placer:
                    _update_clips.append((clip_placer, clip))
        asyncio.ensure_future(self._update_clips(_update_clips))

    def _update_colors(self):
        for _, widget in self._clip_widgets.items():
            widget.update_color()

    def _on_timeline_event(self, e: carb.events.IEvent):
        if e.type == int(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED):
            time = int(time_to_timecode(e.payload["currentTime"], self._timeline) / self._fps_scale)
            if self._model.parent_anim.is_read_only():
                self._model.set_color(DEFAULT_COLOR_CURRENT_TIME_READONLY, DEFAULT_COLOR_READONLY, time)
            else:
                self._model.set_color(DEFAULT_COLOR_CURRENT_TIME, DEFAULT_COLOR, time)
            self._update_colors()

    def _on_timeline_fps_changed(self, *args):
        self._update_content()

    def _on_stage_event(self, e: carb.events.IEvent):
        if e.type == int(omni.usd.StageEventType.SELECTION_CHANGED):
            selected_prims = self._selection.get_selected_prim_paths()
            for _, widget in self._clip_widgets.items():
                widget: AnnotationClipWidget
                source = widget.model.source
                if source is not None and not source.is_external and source.source_path_in_stage in selected_prims:
                    widget.selected = True
                else:
                    widget.selected = False
                    widget.end_edit()

    def _update_clip_placers(self):
        self._clip_placers = {}
        for _, track_data in self._model.tracks.items():
            for clip in track_data:
                clip_placer = ui.Placer()
                self._update_clip(clip_placer, clip)
                self._clip_placers[clip.name] = clip_placer

    def _update_clip_widgets(self):
        names = []
        for annotation in self._model.annotations:
            names.append(annotation.name)

        # clear widgets for which a model no longer exists
        new_widgets = {}
        for name, widget in self._clip_widgets.items():
            if name in names:
                new_widgets[name] = widget
        self._clip_widgets = new_widgets

    def _on_model_changed(self, model: AnnotationSet):
        stage = omni.usd.get_context().get_stage()
        self._fps_scale = stage.GetTimeCodesPerSecond() / model.time_codes_per_second
        self._update_clip_placers()
        self._update_clip_widgets()
        self.update()

    def _on_mouse_pressed_frame(self, x: float, y: float, button: int, modifier: int):
        # Clicking on a clip also triggers mouse_pressed event here
        # If any widget covers the click we let widget handle it.
        accept_click = True
        for name, widget in self._clip_widgets.items():
            widget: AnnotationClipWidget
            if not widget.contain_type() == WidgetSide.Outside:
                accept_click = False
                if not widget.is_editing:
                    if button == 0:
                        self.select_annotations(False)
                        annotation = widget.model
                        source = annotation.source
                        if source is not None and not source.is_read_only():
                            placers = self._get_track_clip_placers(widget._track_name)
                            self._drag_handler = DragHandler(x, y, self._clip_placers[name], placers, widget,
                                                        self._timeline_grid_model, self._timeline_name)
                break

        if accept_click:
            if button == 0:
                self.select_annotations(False)
            elif button == 1:
                self.show_context_menu()

    def _on_mouse_released_frame(self, x: float, y: float, button: int, modifier: int):
        if self._drag_handler:
            self._drag_handler.update_models(self._fps_scale)
            self._drag_handler.restore()
            self._drag_handler.destroy()
            self._drag_handler = None

    def _on_mouse_move(self, x: float, y: float, modifiers: int, is_pressed: bool):
        if self._drag_handler and self._drag_handler._on_drag_fn is not None:
            self._drag_handler._on_drag_fn(x, y, modifiers, is_pressed)

    def _get_track_clip_placers(self, track_name):
        placers = []
        clips = self.model.tracks.get(track_name, [])
        for clip in clips:
            placers.append((self._clip_placers[clip.name], clip))
        return placers
