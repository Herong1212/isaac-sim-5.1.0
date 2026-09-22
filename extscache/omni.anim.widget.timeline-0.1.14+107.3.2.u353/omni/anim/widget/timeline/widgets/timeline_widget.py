import math
import typing

import carb
import carb.settings
from omni import ui

from .. import delegates
from ..models import RangeModel, TimeDisplayValueModel, TimelineGridModel, TimeValueModel
from .timeline_widget_style import TimelineWidgetStyle

g_settings = carb.settings.get_settings()

TICK_LINE_PADDING = 2
SCRUBBER_HEIGHT = 20
SNAP_TO_WHOLE_FRAME = True
CLAMP_TO_RANGE = True
INITIAL_SMALL_TICK_COUNT = 900  # a largish number to avoid rebuilding


def nearest_square(x) -> int:
    # Calculate square root
    sr = math.floor(math.sqrt(x))
    # Calculate perfect square
    a = sr * sr
    b = (sr + 1) * (sr + 1)

    # Find the nearest
    if (x - a) < (b - x):
        return a
    return b


class TimelineWidget:
    DEFAULT_HEIGHT = 35

    def __init__(
        self,
        range_model: RangeModel,
        timeline_grid_model: TimelineGridModel,
        time_display_model: ui.SimpleStringModel,
        timeline_gutter_delegate: typing.Optional[delegates.TimelineContentDelegate] = None,
        snap_to_whole_frame: bool = SNAP_TO_WHOLE_FRAME,
        clamp_to_range: bool = CLAMP_TO_RANGE,
    ):
        self._style = TimelineWidgetStyle.get_style()
        self._range_model = range_model
        self._timeline_grid_model = timeline_grid_model
        self._timeline_ticks_frame: ui.Frame = None
        self._timeline_keyframes_delegate = timeline_gutter_delegate
        self._large_ticks_frame: ui.Frame = None
        self._small_ticks_frame: ui.Frame = None
        self._large_ticks_grid: ui.HGrid = None
        self._small_ticks_grid: ui.HGrid = None
        self._large_ticks_offset_spacer: ui.Spacer = None
        self._small_ticks_offset_spacer: ui.Spacer = None
        self._last_large_tick_step = self._timeline_grid_model.large_tick_step
        self._time_display_model = time_display_model

        self._dragging_frame = False
        self._press_on_slider = False
        self._small_tick_frame_count = 0

        # Scrubber behavior options
        self.snap_to_whole_frame = snap_to_whole_frame
        self.clamp_to_range = clamp_to_range

        self._ui_frame = ui.Frame(
            style=self._style, build_fn=self._build_ui, horizontal_clipping=True, vertical_clipping=True
        )
        self._frame_range_sub = self._range_model.subscribe_item_changed_fn(self._on_frame_range_item_changed)

    def destroy(self):
        self._frame_range_sub = None
        self._ui_frame.clear()
        self._ui_frame = None
        self._timeline_grid_model = None

    def rebuild(self):
        if self._ui_frame:
            self._ui_frame.rebuild()

    def _on_frame_range_item_changed(self, model, item):
        self._last_large_tick_step = self._timeline_grid_model.large_tick_step
        if self._large_ticks_frame:
            self._large_ticks_frame.rebuild()
        self._update_small_ticks_grid()

    def _update_small_ticks_grid(self):
        if not self._small_ticks_grid:
            return

        new_small_tick_count = nearest_square(self._timeline_grid_model.small_tick_count)
        if new_small_tick_count > self._small_tick_frame_count:
            with self._small_ticks_grid:
                for _ in range(0, new_small_tick_count):
                    ui.Frame(build_fn=self._build_small_tick)
            self._small_tick_frame_count = new_small_tick_count
        self._small_ticks_grid.column_width = ui.Pixel(self._timeline_grid_model.small_tick_width)
        self._small_ticks_offset_spacer.width = ui.Pixel(self._timeline_grid_model.frac_small_tick_size)

    def get_frame_range(self) -> RangeModel:
        return self._range_model

    def grid_needs_rebuild(self):
        return self._last_large_tick_step != self._timeline_grid_model.large_tick_step

    def update(self):
        self._update_small_ticks_grid()
        self._update_large_ticks_grid()

    def _update_large_ticks_grid(self):
        if not self._large_ticks_grid or self.grid_needs_rebuild():
            self._last_large_tick_step = self._timeline_grid_model.large_tick_step
            if self._large_ticks_frame:
                self._large_ticks_frame.rebuild()
        elif self._large_ticks_grid:
            self._large_ticks_grid.column_width = ui.Pixel(self._timeline_grid_model.large_tick_width)
            self._large_ticks_offset_spacer.width = ui.Pixel(self._timeline_grid_model.frac_big_tick_size)

    def _build_ui(self):
        with ui.ZStack(content_clipping=True):
            ui.Rectangle(style_type_name_override="TimelineWidget.BackgroundRectangle")
            with ui.VStack(content_clipping=True):
                ui.Spacer(  # Scrubber play-head spacer
                    height=SCRUBBER_HEIGHT,
                    mouse_pressed_fn=self._on_mouse_pressed,
                    mouse_moved_fn=self._on_mouse_moved,
                    mouse_released_fn=self._on_mouse_released,
                )
                with ui.ZStack(content_clipping=True):
                    ui.Rectangle(
                        style_type_name_override="TimelineWidget.HorizontalRectangle",
                    )
                    ui.Frame(build_fn=self._build_gutter_frame, horizontal_clipping=True, vertical_clipping=True)
            self._timeline_ticks_frame = ui.Frame(
                build_fn=self._build_timeline_ticks, horizontal_clipping=True, vertical_clipping=True
            )

    def _build_gutter_frame(self):
        if self._timeline_keyframes_delegate:
            self._timeline_keyframes_delegate.build(
                self._range_model, self._timeline_grid_model, self._time_display_model
            )

    def _build_timeline_ticks(self):
        frame_width = self._timeline_grid_model.frame_width
        if frame_width == 0:
            ui.Spacer()
            return

        # init timecode value model - avoid init in loop.
        with ui.VStack(content_clipping=True):
            self._large_ticks_frame = ui.Frame(build_fn=self._build_large_ticks_frame, content_clipping=True)
            ui.Spacer(height=ui.Percent(15))
            self._small_ticks_frame = ui.Frame(
                build_fn=self._build_small_ticks_frame, height=ui.Percent(20), content_clipping=True
            )

    def _build_small_ticks_frame(self):
        with ui.HStack(content_clipping=True):
            self._small_ticks_offset_spacer = ui.Spacer(width=self._timeline_grid_model.frac_small_tick_size)
            self._small_ticks_grid = ui.HGrid(
                column_width=ui.Pixel(self._timeline_grid_model.small_tick_width), content_clipping=True
            )

        self._small_tick_frame_count = 900
        with self._small_ticks_grid:
            for _ in range(0, self._small_tick_frame_count):
                ui.Frame(build_fn=self._build_small_tick, content_clipping=True)

    def _build_large_ticks_frame(self):
        # init timecode value model - avoid init in loop.
        with ui.HStack():
            # Space for partial frame/partial unit width start
            self._large_ticks_offset_spacer = ui.Spacer(width=self._timeline_grid_model.frac_big_tick_size)
            self._large_ticks_grid = ui.HGrid(
                column_width=self._timeline_grid_model.large_tick_width, content_clipping=True
            )

        time_model = TimeValueModel(0, time_units=self._range_model.time_units)
        time_display_model = TimeDisplayValueModel(
            parent_model=time_model, time_display_model=self._time_display_model, fps_model=self._range_model.fps_model
        )

        if time_display_model is None:
            carb.log_error(
                f"No display model: range units={self._range_model.time_units}, time_display={self._time_display_model}"
            )
            return

        range_length_inclusive = math.ceil(self._range_model.view_range.length_inclusive)
        if self._timeline_grid_model.large_tick_step == 0:
            return
        with self._large_ticks_grid:
            for i in range(0, range_length_inclusive, math.ceil(self._timeline_grid_model.large_tick_step)):
                time_model.set_value(self._range_model.start + i + self._timeline_grid_model.frame_label_offset)
                self._build_large_tick(time_display_model.as_string)

    def _build_large_tick(self, label_string: str):
        with ui.HStack():
            ui.Line(
                width=TICK_LINE_PADDING,
                style_type_name_override="TimelineWidget.Tick.Line",
                alignment=ui.Alignment.LEFT,
            )
            ui.Label(
                label_string,
                height=0,
                style_type_name_override="TimelineWidget.Tick.FrameNumberLabel",
                alignment=ui.Alignment.LEFT_TOP,
            )

    def _build_small_tick(self):
        ui.Line(
            alignment=ui.Alignment.LEFT,
            style_type_name_override="TimelineWidget.Tick.Line",
        )

    def get_frame_width(self):
        return self._timeline_grid_model.frame_width

    def transform_window_to_timeline(self, screen_x: float) -> float:
        return 0 - (self._ui_frame.screen_position_x - screen_x)

    def _set_time_from_mouse_pos(self, x: float, tentative: bool = False):
        transform_window_to_timeline = self.transform_window_to_timeline(x)
        frame_number = self._timeline_grid_model.transform_position_to_timeline(transform_window_to_timeline)

        # Clamp to view range
        if self.clamp_to_range:
            frame_number = min(max(frame_number, self._range_model.view_range.start), self._range_model.view_range.end)

        if self.snap_to_whole_frame:
            frame_number = round(frame_number)

        self._range_model.current_time = frame_number

    def _on_mouse_pressed(self, x, y, button_index, mod):
        if button_index == 0:
            self._set_time_from_mouse_pos(x, button_index == 2)
            self._dragging_frame = True

    def _on_mouse_moved(self, x: float, y: float, m: int, pressed: bool):
        if self._dragging_frame:
            frame_width = self._timeline_grid_model.frame_width
            if frame_width == 0:
                return
            self._set_time_from_mouse_pos(x)

    def _on_mouse_released(self, x, y, button_index, mod):
        self._dragging_frame = False

    def get_content_width(self):
        return self._ui_frame.computed_width
