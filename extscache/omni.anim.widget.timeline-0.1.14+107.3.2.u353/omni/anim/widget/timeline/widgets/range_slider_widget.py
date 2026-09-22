import asyncio
import typing
from functools import partial

import carb
import carb.settings
from omni import ui

from .. import models
from .time_item_value_field_widget import TimeItemValueFieldWidget


class EditScope:
    """The class to avoid circular event calling"""

    def __init__(self):
        self.active = False

    def __enter__(self):
        self.active = True

    def __exit__(self, type, value, traceback):
        self.active = False

    def __bool__(self):
        return not self.active


class FrameRangeSlider:
    LABEL_WIDTH = 80
    BOX_WIDTH = 14
    HANDLE_WIDTH = LABEL_WIDTH + BOX_WIDTH
    BORDER_WIDTH = 2

    @staticmethod
    def get_style():
        return {
            "FrameRangeSlider.Body": {"border_radius": 0, "background_color": 0xFF222222},
            "FrameRangeSlider.Body:hovered": {"border_radius": 0, "background_color": 0xFF626262},
            "FrameRangeSlider.Body:selected": {"background_color": 0xFF626262},
            "FrameRangeSlider.LeftHandle": {"border_radius": 2, "background_color": 0xFF999999},
            "FrameRangeSlider.LeftHandle:hovered": {"border_radius": 2, "background_color": 0xFF666666},
            "FrameRangeSlider.RightHandle": {"border_radius": 2, "background_color": 0xFF999999},
            "FrameRangeSlider.RightHandle:hovered": {"border_radius": 2, "background_color": 0xFF666666},
            "FrameRangeSlider.Label": {"color": 0xFFC6C6C6, "border_color": 0xFFFFFFFF},
            "FrameRangeSlider.Background": {"background_color": 0xFF2A2825},
            "FrameRangeSlider.Gutter": {"background_color": 0xFF333333},
        }

    def __init__(self, range_model: models.StageRangeModel, time_display_model: ui.SimpleStringModel):
        self._settings = carb.settings.get_settings()
        self._range_model = range_model
        self._time_display_model = time_display_model
        self._view_start_model = range_model.view_range.start_model
        self._view_end_model = range_model.view_range.end_model
        self._range_slider_stack: ui.Stack = None
        self._style = self.get_style()
        self._body_placer: ui.Placer = None
        self._body_rectangle: ui.Rectangle = None
        self._left_handle: ui.Rectangle = None
        self._right_handle: ui.Rectangle = None
        self._start_placer: ui.Placer = None
        self._start_field: TimeItemValueFieldWidget = None
        self._end_placer: ui.Placer = None
        self._end_field: TimeItemValueFieldWidget = None
        self._handle_editing = False
        self._body_editing = False
        self._slider_editing = False
        self._slider_width = 1
        self._edit_scope = EditScope()
        self._start_pos: float = None
        self._delta_offset: float = 0
        self._snap = True
        self._built = False
        self._previous_view_start: float = None
        self._previous_view_end: float = None
        self._update_range_task: asyncio.Task = None
        self._start_drag_x = None

        self._range_slider_frame = ui.Frame(build_fn=self._range_slider_build_fn)
        self._range_item_change_sub = self._range_model.subscribe_item_changed_fn(self._on_frame_range_item_changed)

    def _on_frame_range_item_changed(self, model, item):
        if not self._edit_scope:
            return
        if self._update_range_task is None or self._update_range_task.done():
            self._update_range_task = asyncio.ensure_future(self.async_update_range_view())

    async def async_update_range_view(self):
        self.update_ui()

    @property
    def zoomed(self):
        """Return whether or not we are zoomed in. If view range is equal to scene range we are not zoomed."""
        if self._range_model.min == self._range_model.start and self._range_model.max == self._range_model.end:
            return False
        return True

    def on_body_double_click(self, x: float, y: float, button: int, modifier: int):
        self.toggle_zoom()

    def toggle_zoom(self):
        if self.zoomed:
            self._previous_view_start = self._range_model.start
            self._previous_view_end = self._range_model.end
            self._range_model.set_range(self._range_model.min, self._range_model.max)
        elif self._previous_view_start is not None and self._previous_view_end is not None:
            self._range_model.start = self._previous_view_start
            self._range_model.end = self._previous_view_end
            self._range_model.set_range(self._previous_view_start, self._previous_view_end)

    @property
    def snap_to_frame(self) -> bool:
        return self._snap

    @snap_to_frame.setter
    def snap_to_frame(self, value: bool) -> None:
        self._snap = value

    def __del__(self):
        self.destroy()

    def destroy(self):
        self._view_start_end_edit_sub = None
        self._view_end_end_edit_sub = None
        self._range_item_change_sub = None

        if self._body_placer:
            self._body_placer.destroy()
            self._body_placer = None
        if self._start_placer:
            self._start_placer.destroy()
            self._start_placer = None
        if self._end_placer:
            self._end_placer.destroy()
            self._end_placer = None
        if self._body_rectangle:
            self._body_rectangle.destroy()
            self._body_rectangle = None
        if self._range_slider_frame:
            self._range_slider_frame.destroy()
            self._range_slider_frame = None
        self._edit_scope = None
        self._range_model = None
        self._settings = None

    def rebuild(self):
        self._range_slider_frame.rebuild()

    @property
    def enabled(self):
        return self._range_slider_frame.visible

    @enabled.setter
    def enabled(self, value: bool):
        self._range_slider_frame.visible = value

    def get_slider_width(self):
        return self._slider_width - (self.HANDLE_WIDTH * 2)

    def on_width_changed(self, width):
        if not self._edit_scope:
            return
        if not self.enabled:
            return

        if not self._range_slider_frame:
            # not built yet
            return
        with self._edit_scope:
            self._slider_width = width
            self._range_slider_frame.width = ui.Pixel(self._slider_width)
            self._update_ui()

    def update_ui(self):
        """Update UI to reflect current frame range model values."""
        if not self._edit_scope or not self._built:
            return
        with self._edit_scope:
            self._update_ui()

    def _update_ui(self):
        """Note: This should be called within an edit context."""
        start_position = self.frame_to_slider_pos(self._range_model.start)
        end_position = self.frame_to_slider_pos(self._range_model.end)

        if self._range_model.max_range.length == 0.0:
            # special case when range is 0
            end_position = self.max_x_end_placer

        clamped_start_pos = self.clamp(start_position, 0, self.max_x_end_placer)
        clamped_end_position = self.clamp(end_position, clamped_start_pos, self.max_x_end_placer - self.HANDLE_WIDTH)

        # carb.log_warn(f"Update ui placers: start pos: {clamped_start_pos}, end pos: {clamped_end_position + self.HANDLE_WIDTH}, body width: {clamped_end_position - clamped_start_pos}")
        self._body_placer.width = ui.Pixel(clamped_end_position - clamped_start_pos)
        self._start_placer.offset_x = ui.Pixel(clamped_start_pos)
        self._end_placer.offset_x = ui.Pixel(clamped_end_position + self.HANDLE_WIDTH)
        self._body_placer.offset_x = ui.Pixel(clamped_start_pos + self.HANDLE_WIDTH)

    def _range_slider_build_fn(self):
        self._view_start_model.set_value(self._range_model.start)
        self._view_end_model.set_value(self._range_model.end)

        self._range_slider_stack = ui.ZStack()
        with self._range_slider_stack:
            ui.Rectangle(style=self._style, style_type_name_override="FrameRangeSlider.Gutter")
            self._body_placer = ui.Placer(draggable=False, drag_axis=ui.Axis.X)
            self._body_placer.set_offset_x_changed_fn(self.on_body_offset_changed)
            with self._body_placer:
                self._body_rectangle = ui.Rectangle(style=self._style, style_type_name_override="FrameRangeSlider.Body")
                self._body_rectangle.set_mouse_pressed_fn(partial(self.on_mouse_pressed, placer=self._body_placer))
                self._body_rectangle.set_mouse_released_fn(partial(self.on_mouse_released, placer=self._body_placer))
                self._body_rectangle.set_mouse_moved_fn(partial(self.on_mouse_moved, placer=self._body_placer))
                self._body_rectangle.set_mouse_double_clicked_fn(self.on_body_double_click)

            self._start_placer = ui.Placer(draggable=False, drag_axis=ui.Axis.X)
            self._start_placer.set_offset_x_changed_fn(self.on_start_placer_offset_changed)
            with self._start_placer:
                with ui.HStack(width=self.HANDLE_WIDTH):
                    with ui.ZStack():
                        with ui.HStack():
                            self._start_field = TimeItemValueFieldWidget(
                                value_model=self._range_model.view_range.start_model,
                                time_display_model=self._time_display_model,
                                fps_model=self._range_model.fps_model,
                                item_model=self._range_model,
                                item=self._range_model.view_range,
                                width=80,
                                tooltip="View Start",
                            )
                    self._left_handle = ui.Rectangle(
                        width=self.BOX_WIDTH, style=self._style, style_type_name_override="FrameRangeSlider.LeftHandle"
                    )
                    self._left_handle.set_mouse_pressed_fn(partial(self.on_mouse_pressed, placer=self._start_placer))
                    self._left_handle.set_mouse_released_fn(partial(self.on_mouse_released, placer=self._start_placer))
                    self._left_handle.set_mouse_moved_fn(partial(self.on_mouse_moved, placer=self._start_placer))

            self._end_placer = ui.Placer(draggable=False, drag_axis=ui.Axis.X)
            self._end_placer.set_offset_x_changed_fn(self.on_end_placer_offset_changed)
            with self._end_placer:
                with ui.HStack():
                    self._right_handle = ui.Rectangle(
                        width=self.BOX_WIDTH, style=self._style, style_type_name_override="FrameRangeSlider.RightHandle"
                    )
                    self._right_handle.set_mouse_pressed_fn(partial(self.on_mouse_pressed, placer=self._end_placer))
                    self._right_handle.set_mouse_released_fn(partial(self.on_mouse_released, placer=self._end_placer))
                    self._right_handle.set_mouse_moved_fn(partial(self.on_mouse_moved, placer=self._end_placer))

                    self._end_field = TimeItemValueFieldWidget(
                        value_model=self._range_model.view_range.end_model,
                        time_display_model=self._time_display_model,
                        fps_model=self._range_model.fps_model,
                        item_model=self._range_model,
                        item=self._range_model.view_range,
                        width=80,
                        tooltip="View End",
                    )

        self.on_width_changed(self._range_slider_frame.computed_width)
        self._built = True

    def on_mouse_moved(self, x: float, y: float, key_mod: int, pressed: bool, placer: ui.Placer = None):
        if not placer.selected:
            return
        delta_offset = x - self._start_drag_x
        placer.offset_x = self._start_pos + delta_offset

    def on_mouse_pressed(self, x: float, y: float, button: int, modifier: int, placer: ui.Placer = None):
        placer.selected = True
        self._start_drag_x = x
        self._start_pos = placer.offset_x.value

    def on_mouse_released(self, *args, placer: ui.Placer = None):
        placer.selected = False
        if self._range_model.is_editing:
            self._range_model.end_edit(self._range_model.view_range)
        self._start_pos = None

    def _snap_to_frame(self, offset: float) -> typing.Tuple[int, float]:
        snap_time = round(self.slider_pos_to_time(offset))
        snap_offset = self.frame_to_slider_pos(snap_time)
        return snap_offset, snap_time

    @staticmethod
    def clamp(value: float, _min: float, _max: float) -> float:
        if _min is not None and value < _min:
            return _min
        if _max is not None and value > _max:
            return _max
        return value

    @property
    def max_x_end_placer(self):
        return self.get_slider_width() + self.HANDLE_WIDTH

    def on_body_offset_changed(self, offset_x: ui.Pixel):
        if not self._edit_scope:
            return

        with self._edit_scope:
            if self._body_placer.selected and not self._range_model.is_editing:
                self._range_model.begin_edit(self._range_model.view_range)

            body_width = self._body_placer.width
            view_range_length = self._range_model.view_range.length
            new_offset = offset_x

            if self._snap:
                snap_offset, new_start_time = self._snap_to_frame(new_offset - self.HANDLE_WIDTH)
                new_offset = snap_offset + self.HANDLE_WIDTH
                new_end_time = round(new_start_time + view_range_length)
                view_range_length = new_end_time - new_start_time
            else:
                new_start_time = self.slider_pos_to_time(new_offset - self.HANDLE_WIDTH)
                new_end_time = new_start_time + view_range_length

            clamp_time = self.clamp(
                new_start_time, _min=self._range_model.min, _max=self._range_model.max - view_range_length
            )
            if new_start_time != clamp_time:
                new_start_time = clamp_time
                new_offset = self.frame_to_slider_pos(clamp_time) + self.HANDLE_WIDTH
                new_end_time = new_start_time + view_range_length

            self._body_placer.offset_x = ui.Pixel(new_offset)
            self._start_placer.offset_x = ui.Pixel(new_offset - self.HANDLE_WIDTH)
            self._end_placer.offset_x = ui.Pixel(new_offset + body_width)

            if self._range_model.start == new_start_time and self._range_model.end == new_end_time:
                return

            self._range_model.set_range(new_start_time, new_end_time)

    def on_start_placer_offset_changed(self, offset_x: ui.Pixel):
        if not self._edit_scope:
            return

        with self._edit_scope:
            if self._start_placer.selected and not self._range_model.is_editing:
                self._range_model.begin_edit(self._range_model.view_range)

            view_start_time = self._view_start_model.as_float
            new_offset = offset_x

            if self._snap:
                new_offset, new_time = self._snap_to_frame(new_offset)
            else:
                new_time = self.slider_pos_to_time(new_offset)

            clamp_time = self.clamp(new_time, self._range_model.min, self._range_model.end)
            if new_time != clamp_time:
                new_time = clamp_time
                new_offset = self.frame_to_slider_pos(clamp_time)

            self._start_placer.offset_x = ui.Pixel(new_offset)
            if new_time == view_start_time:
                return

            self._range_model.set_range(new_time, self._range_model.end)
            self.update_slider_body(start_pos=new_offset)

    def on_end_placer_offset_changed(self, offset_x: ui.Pixel):
        if not self._edit_scope:
            return

        with self._edit_scope:
            if self._end_placer.selected and not self._range_model.is_editing:
                self._range_model.begin_edit(self._range_model.view_range)

            view_end_time = self._view_end_model.as_float
            self._delta_offset = offset_x.value - self._start_pos
            new_offset = self._start_pos + self._delta_offset

            if self._snap:
                snap_offset, new_time = self._snap_to_frame(new_offset - self.HANDLE_WIDTH)
                new_offset = snap_offset + self.HANDLE_WIDTH
            else:
                new_time = self.slider_pos_to_time(self._end_placer.offset_x - self.HANDLE_WIDTH)

            clamp_time = self.clamp(new_time, self._range_model.start, self._range_model.max)
            if new_time != clamp_time:
                new_time = clamp_time
                new_offset = self.frame_to_slider_pos(clamp_time) + self.HANDLE_WIDTH

            self._end_placer.offset_x = ui.Pixel(new_offset)
            if new_time == view_end_time:
                return

            self._range_model.set_range(self._range_model.start, new_time)
            self.update_slider_body(end_pos=new_offset)

    def slider_pos_to_time(self, pos):
        frame_range_length = self._range_model.max_range.length
        slider_width = self.get_slider_width()
        return frame_range_length * (pos / slider_width) + self._range_model.min

    def frame_to_slider_pos(self, frame):
        frame_range_length = max((self._range_model.max_range.length), 0.000001)
        return self.get_slider_width() * (frame - self._range_model.min) / frame_range_length

    def update_slider_body(self, start_pos=None, end_pos=None):
        if start_pos is None:
            start_pos = self._start_placer.offset_x.value
        if end_pos is None:
            end_pos = self._end_placer.offset_x.value
        new_width = end_pos - start_pos - self.HANDLE_WIDTH

        self._body_placer.width = ui.Pixel(new_width)
        self._body_placer.offset_x = ui.Pixel(start_pos + self.HANDLE_WIDTH)
