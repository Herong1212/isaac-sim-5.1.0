import math
from functools import lru_cache
from typing import List, Optional

from omni import ui
from omni.kit.preferences.animation import TimeDisplay, g_time_display_model

from .range_model import RangeModel
from .time_display_value_model import TimeDisplayValueModel
from .time_units import TimeUnits
from .time_value_model import TimeValueModel


class TimelineGridModel:
    """Contains the logic for computing timeline grid steps and spacing."""

    FONT_SIZE = 14
    FRAME_NUMBER_PADDING = 32
    MIN_SMALL_TICK_WIDTH = 4
    SECONDS_STEPS = (0.01, 0.1, 0.5, 1, 2, 5, 10, 20, 30, 60, 90, 120, 240, 480, 960)
    FRAME_STEPS = (
        1,
        5,
        10,
        20,
        30,
        50,
        60,
        100,
        200,
        300,
        500,
        600,
        1000,
        3000,
        5000,
        6000,
        10000,
        20000,
        30000,
        50000,
        60000,
        100000,
    )

    def __init__(
        self, range_model: RangeModel, time_display_model: Optional[ui.SimpleStringModel] = None, font_size=FONT_SIZE
    ):
        self._range_model = range_model
        self._font_size = font_size
        self._container_width = 0
        self._frac_big_tick_size = 0

        self.pixels_per_time_unit_model = ui.SimpleFloatModel(0)  # scale time unit to pixels
        self.pixels_per_frame_model = ui.SimpleFloatModel(0)  # UI width per frame
        self.large_tick_width_model = ui.SimpleFloatModel(0)  # UI width per large step
        self.large_tick_step_model = ui.SimpleFloatModel(0)  # Timevalues per large tick
        self._time_display_model = time_display_model or g_time_display_model
        # These models are for determining the size of display strings. They are initialized here to avoid doing it often (on update)
        self._time_model = TimeValueModel(0, time_units=self._range_model.time_units)
        self._time_display_value_model = TimeDisplayValueModel(
            self._time_model, self._time_display_model, self._range_model.fps_model
        )

    def __repr__(self):
        return f"TimelineGridModel(frame_width:{self.pixels_per_frame_model.as_string}, large_tick_width:{self.large_tick_width_model.as_string}, large_tick_step:{self.large_tick_step_model.as_string})"

    @property
    def time_display_model(self):
        return self._time_display_model

    @property
    def range_model(self):
        return self._range_model

    def transform_position_to_timeline(self, offset: float):
        if self.pixels_per_time_unit == 0:
            return 0
        time_offset = offset / self.pixels_per_time_unit
        return time_offset + self._range_model.start

    def transform_timeline_to_position(self, timeline_val: float) -> float:
        start = self._range_model.start
        relative_time = timeline_val - start
        return self.pixels_per_time_unit * relative_time

    @property
    def small_tick_width(self) -> float:
        """UI width per small tick."""
        return max(self.MIN_SMALL_TICK_WIDTH, self.frame_width)

    @property
    def small_tick_count(self) -> int:
        if self.small_tick_width == 0:
            return 0
        return math.ceil(self._container_width / self.small_tick_width) + 1

    @property
    def frame_width(self) -> float:
        "UI Width per frame"
        return self.pixels_per_frame_model.as_float

    @property
    def large_tick_width(self) -> float:
        """UI Width per large tick step"""
        return self.large_tick_width_model.as_float

    @property
    def large_tick_step(self) -> float:
        """Timecodes per large tick"""
        return self.large_tick_step_model.as_float

    @property
    def large_tick_count(self) -> int:
        if self.large_tick_step == 0:
            return 0
        return math.ceil(self.range_length_inclusive / self.large_tick_step)

    @property
    def range_length_inclusive(self) -> float:
        if self._range_model.time_units == TimeUnits.FRAMES:
            return self._range_model.view_range.length + 1
        if self._range_model.time_units == TimeUnits.SECONDS:
            if self._range_model.fps == 0:
                return 0
            return self._range_model.view_range.length + (1 / self._range_model.fps)

    @property
    def frame_time_value(self):
        if self._range_model.time_units == TimeUnits.FRAMES:
            return 1
        if self._range_model.time_units == TimeUnits.SECONDS:
            return 1 / self._range_model.fps

    @property
    def frac_big_tick_size(self):
        if self.large_tick_step == 0:
            return 0
        begin_mod_big_tick = self._range_model.start % self.large_tick_step
        if begin_mod_big_tick:
            return self.large_tick_width * (1.0 - begin_mod_big_tick / self.large_tick_step)
        return 0

    @property
    def frame_label_offset(self):
        begin_mod_big_tick = self._range_model.start % self.large_tick_step
        if begin_mod_big_tick:
            return self.large_tick_step - begin_mod_big_tick
        return 0

    @property
    def frac_small_tick_size(self):
        mod_small_tick = self._range_model.start % 1
        if mod_small_tick:
            return (1 - mod_small_tick) * self.small_tick_width
        return 0

    @property
    def pixels_per_time_unit(self):
        if self.range_length_inclusive == 0:
            return 0
        return self._container_width / self.range_length_inclusive

    def _get_min_large_tick_width(self) -> float:
        """Get minimum large tick width for the current label size."""
        return (
            self.get_frame_numbers_label_size(self._range_model.start, self._range_model.end)
            + TimelineGridModel.FRAME_NUMBER_PADDING
        )

    def _step_sizes_for_time_display(self) -> List[float]:
        if self._range_model.time_units == TimeUnits.USD_TIMECODE and self._time_display_model.as_string in (
            TimeDisplay.SECONDS,
            TimeDisplay.SMPTE,
        ):
            timecodes_per_second = self._range_model.fps
            return [step * timecodes_per_second for step in self.SECONDS_STEPS]
        return sorted(TimelineGridModel.FRAME_STEPS)

    def _compute_large_tick_step(self, width: float) -> float:
        """Compute the smallest large tick step for the given container width."""
        # Get the smallest tick width that will fit the labels
        min_large_tick_width = self._get_min_large_tick_width()
        if min_large_tick_width <= 1:
            return 0

        step_sizes = self._step_sizes_for_time_display()

        for step_size in step_sizes:
            if step_size == 0:
                # This shouldn't happen - but we can ignore any 0 step size.
                continue
            step_count = int(self.range_length_inclusive / step_size)
            if step_count == 0:
                break
            step_width = width / step_count
            if step_width >= min_large_tick_width:
                return step_size
        return step_sizes[-1]

    def on_container_width_changed(self, container_width: float):
        def _early_out():
            self.pixels_per_frame_model.set_value(0)
            self.large_tick_width_model.set_value(0)
            self.large_tick_step_model.set_value(0)

        self._container_width = container_width

        if container_width == 0:
            return _early_out()

        range_length_inclusive = self.range_length_inclusive
        if range_length_inclusive == 0:
            return _early_out()

        # Update unit min width
        large_tick_step = self._compute_large_tick_step(container_width)
        if not large_tick_step:
            return _early_out()

        # Frame width - ui width per frame
        frame_width = self.frame_time_value * self.pixels_per_time_unit

        # update models
        large_tick_count = range_length_inclusive / large_tick_step
        large_tick_width = container_width / large_tick_count

        # Offsets for fractional stat time and when not starting from 0
        self.pixels_per_frame_model.set_value(frame_width)
        self.large_tick_width_model.set_value(large_tick_width)
        self.large_tick_step_model.set_value(large_tick_step)

    @lru_cache(maxsize=32)
    def get_frame_numbers_label_size(self, start: float, end: float):
        self._time_display_value_model.set_value(start)
        start_value_string = self._time_display_value_model.as_string
        self._time_display_value_model.set_value(end)
        end_value_string = self._time_display_value_model.as_string

        number_of_digits = max(
            len(start_value_string),
            len(end_value_string),
        )
        return number_of_digits * self._font_size * 0.6
