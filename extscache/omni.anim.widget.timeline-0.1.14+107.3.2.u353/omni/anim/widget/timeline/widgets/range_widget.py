import typing

import carb.settings
import omni.kit.app
import omni.ui as ui

from .. import models
from .range_slider_widget import FrameRangeSlider
from .time_item_value_field_widget import TimeItemValueFieldWidget


class RangeWidget:
    DEFAULT_HEIGHT = 22

    def __init__(self, range_model: models.StageRangeModel, time_display_model: ui.SimpleStringModel):
        self._range_model = range_model
        self._time_display_model = time_display_model

        self._start_frame_field: TimeItemValueFieldWidget = None
        self._end_frame_field: TimeItemValueFieldWidget = None
        self._frame_range_slider: FrameRangeSlider = None
        self._frame_range_slider_frame: ui.Frame = None
        self._range_slider_enabled = True
        self._snap_to_frame = True
        self._style = self.get_style()
        self._root_frame = ui.Frame(identifier="range_view", build_fn=self._build_ui)
        self._update_range_task = None

    @staticmethod
    def get_style():
        style = {
            "FrameRangeSlider.Label": {"color": 0xFFC6C6C6},
            "FrameRangeSlider.Gutter": {"background_color": 0xFFFFFFFF},
        }
        return style

    def __del__(self):
        self.destroy()

    def destroy(self):
        self._update_range_task = None

        self._range_model = None
        if self._start_frame_field:
            self._start_frame_field.destroy()
            self._start_frame_field = None
        if self._end_frame_field:
            self._end_frame_field.destroy()
            self._end_frame_field = None
        if self._root_frame:
            self._root_frame.clear()
            self._root_frame.destroy()
            self._root_frame = None
        if self._frame_range_slider_frame:
            self._frame_range_slider_frame.clear()
            self._frame_range_slider_frame.destroy()
            self._frame_range_slider_frame = None
        if self._frame_range_slider:
            self._frame_range_slider.destroy()
            self._frame_range_slider = None

    @property
    def snap_to_frame(self) -> bool:
        return self._snap_to_frame

    @snap_to_frame.setter
    def snap_to_frame(self, value: bool) -> None:
        self._snap_to_frame = value
        if self._frame_range_slider:
            self._frame_range_slider.snap_to_frame = value

    @property
    def range_slider_enabled(self):
        return self._range_slider_enabled

    @range_slider_enabled.setter
    def range_slider_enabled(self, value: bool):
        self._range_slider_enabled = value
        if self._frame_range_slider:
            self._frame_range_slider.enabled = value

    def on_width_changed(self, width: float):
        if self._root_frame.computed_content_width != width:
            self._root_frame.width = ui.Pixel(width)
            self.rebuild()

    def update_ui(self):
        if self._frame_range_slider:
            self._frame_range_slider.update_ui()

    def rebuild(self):
        if self._root_frame:
            self._root_frame.rebuild()

    def _build_ui(self):
        with ui.HStack(style=self._style):
            self._start_frame_field = TimeItemValueFieldWidget(
                value_model=self._range_model.max_range.start_model,
                time_display_model=self._time_display_model,
                fps_model=self._range_model.fps_model,
                item_model=self._range_model,
                item=self._range_model.max_range,
                tooltip="Scene Start",
                width=80,
            )
            ui.Spacer(width=4)
            self._frame_range_slider_frame = ui.Frame()
            with self._frame_range_slider_frame:
                self._frame_range_slider = FrameRangeSlider(
                    self._range_model, time_display_model=self._time_display_model
                )
                self._frame_range_slider.enabled = self._range_slider_enabled
                self._frame_range_slider.snap_to_frame = self._snap_to_frame
            ui.Spacer(width=4)
            self._end_frame_field = TimeItemValueFieldWidget(
                value_model=self._range_model.max_range.end_model,
                time_display_model=self._time_display_model,
                fps_model=self._range_model.fps_model,
                item_model=self._range_model,
                item=self._range_model.max_range,
                width=80,
                tooltip="Scene End",
            )
