import asyncio
import math
import typing
from dataclasses import dataclass

import carb
import carb.input
import carb.windowing
import omni.appwindow
import omni.ext
import omni.kit.app
import omni.kit.ui
from carb.input import KEYBOARD_MODIFIER_FLAG_CONTROL
from omni import ui
from omni.kit.preferences.animation import g_time_display_model

from ..delegates import TimelineContentDelegate, TimelineViewDelegate
from ..models import RangeModel, StageRangeModel, TimelineGridModel
from ..widgets import TimelineWidget, TimelineWidgetStyle

try:
    import omni.kit.window.cursor as window_cursor

    g_main_window_cursor: typing.Optional[window_cursor.WindowCursor] = window_cursor.get_main_window_cursor()
except ImportError:
    carb.log_warn("Could not import omni.kit.window.cursor")
    g_main_window_cursor = None


g_input_interface: carb.input.IInput = carb.input.acquire_input_interface()

WINDOW_NAME = "New Timeline View"
SNAP_DISTANCE = 10


@dataclass
class PanStartState:
    x: float
    y: float
    key_mod: int
    range_start: float
    range_end: float
    pixels_per_timecode: float
    scroll_y: float


class TimelineView:
    DEFAULT_HEIGHT = 35

    def __init__(
        self,
        range_model: typing.Optional[RangeModel] = None,
        timeline_grid_model: typing.Optional[TimelineGridModel] = None,
        scroll_y_changed_fn: typing.Optional[typing.Callable] = None,
        timeline_view_delegate: typing.Optional[TimelineViewDelegate] = None,
        timeline_content_delegate: typing.Optional[TimelineContentDelegate] = None,
        timeline_gutter_delegate: typing.Optional[TimelineContentDelegate] = None,
        build_scrubber: bool = True,
        build_range: bool = False,
        build_content: bool = False,
        time_display: typing.Optional[typing.Union[str, ui.SimpleStringModel]] = None,
        spacing: int = 2,
    ):
        if not time_display:
            self._time_display_model = g_time_display_model
        elif isinstance(time_display, str):
            self._time_display_model = ui.SimpleStringModel(time_display)
        elif isinstance(time_display, ui.SimpleStringModel):
            self._time_display_model = time_display

        self._time_setting_sub = self._time_display_model.subscribe_value_changed_fn(
            self._on_time_display_settings_change
        )

        self._range_model: typing.Union[RangeModel, StageRangeModel] = range_model or StageRangeModel()
        self._timeline_grid_model: TimelineGridModel = timeline_grid_model or TimelineGridModel(
            self._range_model, self._time_display_model
        )

        # build flags
        self._should_build_scrubber = build_scrubber
        self._should_build_range = build_range
        self._should_build_content = build_content

        self._spacing = spacing

        self._style = TimelineWidgetStyle.get_style()

        self._delegate = timeline_view_delegate or TimelineViewDelegate(
            timeline_content_delegate=timeline_content_delegate, timeline_gutter_delegate=timeline_gutter_delegate
        )
        self._timeline_widget_frame: typing.Optional[ui.Frame] = None
        self._timeline_content_frame: typing.Optional[ui.ScrollingFrame] = None
        self._scrubber_frame: typing.Optional[ui.Frame] = None

        self._frame_range_sub = self._range_model.subscribe_item_changed_fn(self._on_frame_range_item_changed)
        self._ui_frame = ui.Frame(
            style=self._style,
            build_fn=self._build_ui,
            identifier="timeline_view",
            horizontal_clipping=True,
            vertical_clipping=True,
            computed_content_size_changed_fn=self._on_size_changed,
        )
        self._panning = False
        self._zooming = False
        self._pan_start_state = None
        self._scroll_y = 0
        self._scroll_y_changed_fn = scroll_y_changed_fn
        self._set_mouse_callbacks()

    def _on_time_display_settings_change(self, value_model: ui.SimpleStringModel):
        self.rebuild()

    def _on_size_changed(self):
        self.on_resize()

    @property
    def width(self):
        if self._ui_frame:
            return self._ui_frame.width
        return 0

    @property
    def scrolling_frame(self) -> typing.Optional[ui.ScrollingFrame]:
        return self._timeline_content_frame

    @property
    def scroll_y(self) -> float:
        if self._timeline_content_frame:
            return self._timeline_content_frame.scroll_y
        return 0

    @scroll_y.setter
    def scroll_y(self, value: float) -> None:
        if self._timeline_content_frame:
            self._timeline_content_frame.scroll_y = value

    def _on_scroll_y_changed(self, value):
        if self._scroll_y_changed_fn:
            self._scroll_y_changed_fn(value)

    def get_timeline_height(self):
        if not self._timeline_widget_frame:
            return TimelineWidget.DEFAULT_HEIGHT
        return self._timeline_widget_frame.computed_height

    def destroy(self):
        self._time_setting_sub = None
        self._scroll_y_changed_fn = None
        self._frame_range_sub = None

        if self._delegate:
            self._delegate.destroy()
            self._delegate = None

        if self._ui_frame:
            self._ui_frame.destroy()

        self._range_model = None
        self._timeline_grid_model = None

    def get_style(self):
        return self._style

    def _on_frame_range_item_changed(self, model, item):
        asyncio.ensure_future(self.async_update())

    def rebuild(self):
        if not self._ui_frame:
            return
        self._ui_frame.rebuild()

    def rebuild_content(self):
        if self._timeline_content_frame:
            self._timeline_content_frame.rebuild()

    def get_frame_range_model(self):
        return self._range_model

    def get_grid_model(self):
        return self._timeline_grid_model

    async def async_update(self):
        # Async resize for first build.
        self.on_resize()

    def on_resize(self):
        if not self._ui_frame:
            return

        self._timeline_grid_model.on_container_width_changed(container_width=self._ui_frame.computed_width)
        if self._timeline_grid_model.frame_width == 0:
            return
        if self._delegate:
            self._delegate.resize(self._ui_frame.computed_width)

    def update(self):
        if self._delegate:
            self._delegate.update()

    def _build_ui(self):
        with ui.VStack(spacing=self._spacing, content_clipping=True):
            with ui.ZStack(direction=ui.Direction.BACK_TO_FRONT, content_clipping=True):
                with ui.VStack(content_clipping=True):
                    self._timeline_widget_frame = ui.Frame(
                        build_fn=self._build_timeline_widget, horizontal_clipping=True, vertical_clipping=True
                    )
                    if self._should_build_content:
                        self._timeline_widget_frame.height = ui.Pixel(TimelineWidget.DEFAULT_HEIGHT)
                        self._timeline_content_frame = ui.ScrollingFrame(
                            build_fn=self._build_timeline_content,
                            horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                            vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                            scroll_y_changed_fn=self._on_scroll_y_changed,
                            horizontal_clipping=True,
                        )
                if self._should_build_scrubber:
                    self._scrubber_frame = ui.Frame(
                        build_fn=self._build_scrubber,
                        separate_window=True,
                        horizontal_clipping=True,
                        vertical_clipping=True,
                    )
            if self._should_build_range:
                self._range_frame = ui.Frame(build_fn=self._build_frame_range, height=22, content_clipping=True)

        asyncio.ensure_future(self.async_update())

    def _set_mouse_callbacks(self):
        self._ui_frame.set_mouse_pressed_fn(self._tracks_timeline_frame_mouse_pressed)
        self._ui_frame.set_mouse_moved_fn(self._tracks_timeline_frame_mouse_moved)
        self._ui_frame.set_mouse_released_fn(self._tracks_timeline_frame_mouse_released)
        self._ui_frame.set_mouse_wheel_fn(self._tracks_timeline_mouse_wheel)
        self._ui_frame.set_key_pressed_fn(self._tracks_timeline_key_pressed)

    def _on_pan_start(self, x: float, y: float, key_mod: int):
        view_start = self._range_model.start
        view_end = self._range_model.end
        pixels_per_timecode = self._timeline_grid_model.pixels_per_time_unit
        if pixels_per_timecode == 0:
            return
        self._panning = True
        self._pan_start_state = PanStartState(x, y, key_mod, view_start, view_end, pixels_per_timecode, self.scroll_y)
        self._range_model.begin_edit(self._range_model.view_range)
        if g_main_window_cursor:
            g_main_window_cursor.override_cursor_shape(carb.windowing.CursorStandardShape.HAND)

    def _on_pan(self, x: float, y: float, key_mod: int):
        """Each drag delta change."""
        delta_x = x - self._pan_start_state.x
        delta_y = y - self._pan_start_state.y

        delta_timecodes = (delta_x * -1) / self._timeline_grid_model.pixels_per_time_unit

        if self._range_model.max is not None and self._range_model.min is not None:
            max_timecodes_delta = self._range_model.max - self._pan_start_state.range_end
            min_timecodes_delta = self._range_model.min - self._pan_start_state.range_start
            delta_timecodes = max(min(delta_timecodes, max_timecodes_delta), min_timecodes_delta)

        new_range_begin = round(self._pan_start_state.range_start + delta_timecodes)
        new_range_end = round(self._pan_start_state.range_end + delta_timecodes)

        if self._range_model.start != new_range_begin and self._range_model.end != new_range_end:
            self._range_model.set_range(new_range_begin, new_range_end)

        if not self._timeline_content_frame:
            return

        new_scroll_y = self._pan_start_state.scroll_y - delta_y
        new_scroll_y = max(min(new_scroll_y, self._timeline_content_frame.scroll_y_max), 0)
        if self.scroll_y != new_scroll_y:
            self.scroll_y = new_scroll_y

    def _on_pan_end(self, x: float, y: float, key_mod: int):
        if g_main_window_cursor:
            g_main_window_cursor.clear_overridden_cursor_shape()

        self._range_model.end_edit(self._range_model.view_range)
        self._pan_start_state = None
        self._panning = False

    def _on_zoom(self, x: float, y: float, wheel_x: float, wheel_y: float, key_mod: int):
        # percentage by which to zoom
        zoom_speed = 10
        zoom_direction = wheel_y

        if not self._zooming:
            self._range_model.begin_edit(self._range_model.view_range)
        self._zooming = True

        # TODO: Too easy to break - if mouse is outside frame then we don't get key-up
        # if g_main_window_cursor:
        #     g_main_window_cursor.override_cursor_shape(carb.windowing.CursorStandardShape.HORIZONTAL_RESIZE)

        view_start = self._range_model.start
        view_end = self._range_model.end
        range_length = self._range_model.view_range.length

        if range_length <= 0 and zoom_direction < 0:
            # Zooming out while frame range is 0 or less, just fix the range
            self._range_model.set_range(view_start, view_start + 1)
            return

        if zoom_direction > 0 and range_length == 0:
            # already at max zoom.
            return

        timeline_pos = self.transform_window_to_view_pos(x)
        time = self.transform_position_to_timeline(timeline_pos)

        # ratio to apply delta to keep relative to mouse pos
        view_start_ratio = abs(self._range_model.start - time) / range_length
        view_end_ratio = abs(self._range_model.end - time) / range_length

        # desired new range length
        new_range_delta = range_length / zoom_speed  # * zoom_direction

        start_delta = math.ceil(new_range_delta * view_start_ratio)
        end_delta = math.ceil(new_range_delta * view_end_ratio)
        new_start = view_start + (start_delta * zoom_direction)
        new_end = view_end - (end_delta * zoom_direction)

        if self._range_model.min is not None:
            new_start = max(new_start, self._range_model.min)
        if self._range_model.max is not None:
            new_end = max(new_start, min(new_end, self._range_model.max))

        if new_start > new_end:
            # hit max zoom, do nothing.
            return

        self._range_model.set_range(new_start, new_end)

    def _on_zoom_end(self):
        self._zooming = False
        self._range_model.end_edit(self._range_model.view_range)
        # if g_main_window_cursor:
        #     g_main_window_cursor.clear_overridden_cursor_shape()

    def _get_current_mouse_coords(self):
        app_window: omni.appwindow.IAppWindow = omni.appwindow.get_default_app_window()
        dpi_scale = ui.Workspace.get_dpi_scale()
        pos_x, pos_y = g_input_interface.get_mouse_coords_pixel(app_window.get_mouse())
        return pos_x / dpi_scale, pos_y / dpi_scale

    def _tracks_timeline_key_pressed(self, key: int, key_mod: int, pressed: bool):
        if self._zooming and key_mod == 0 and pressed is False:
            self._on_zoom_end()

    def _tracks_timeline_mouse_wheel(self, wheel_x: float, wheel_y: float, key_mod: int):
        if key_mod == KEYBOARD_MODIFIER_FLAG_CONTROL:
            x, y = self._get_current_mouse_coords()
            self._on_zoom(x, y, wheel_x, wheel_y, key_mod)

    def _tracks_timeline_frame_mouse_pressed(self, x: float, y: float, button: int, key_mod: int):
        if button == 2:
            self._on_pan_start(x, y, key_mod)

    def _tracks_timeline_frame_mouse_released(self, x: float, y: float, button: int, key_mod: int):
        if self._panning and button == 2:
            self._on_pan_end(x, y, key_mod)

    def _tracks_timeline_frame_mouse_moved(self, x: float, y: float, key_mod: int, pressed: bool):
        if self._panning:
            self._on_pan(x, y, key_mod)

    def _build_scrubber(self):
        self._delegate.build_scrubber(
            range_model=self._range_model,
            timeline_grid_model=self._timeline_grid_model,
            time_display_model=self._time_display_model,
        )

    def _build_timeline_content(self):
        self._delegate.build_timeline_content(
            range_model=self._range_model,
            timeline_grid_model=self._timeline_grid_model,
            time_display_model=self._time_display_model,
        )

    def _build_timeline_widget(self):
        self._delegate.build_timeline_widget(
            self._range_model, self._timeline_grid_model, time_display_model=self._time_display_model
        )

    def _build_frame_range(self):
        self._delegate.build_frame_range_widget(
            self._range_model, self._timeline_grid_model, time_display_model=self._time_display_model
        )

    def transform_window_to_view_pos(self, screen_x: float) -> float:
        return 0 - (self._ui_frame.screen_position_x - screen_x)

    def transform_window_to_timeline(self, screen_x: float) -> float:
        return self.transform_position_to_timeline(self.transform_window_to_view_pos(screen_x))

    def transform_timeline_to_position(self, timeline_val) -> float:
        return self._timeline_grid_model.transform_timeline_to_position(timeline_val)

    def transform_position_to_timeline(self, offset: float):
        return self._timeline_grid_model.transform_position_to_timeline(offset)
