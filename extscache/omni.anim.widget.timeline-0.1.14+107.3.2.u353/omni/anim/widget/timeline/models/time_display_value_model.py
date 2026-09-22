import carb
from omni import ui
from omni.kit.preferences.animation import TimeDisplay

from .helpers import _pretty_print_float
from .smpte import SMPTE_Timecode
from .time_units import TimeUnits
from .time_value_model import TimeValueModel


class TimeDisplayValueModel(ui.SimpleFloatModel):
    def __init__(
        self,
        parent_model: TimeValueModel,
        time_display_model: ui.SimpleStringModel,
        fps_model: ui.SimpleFloatModel,
        *args,
        **kwargs,
    ) -> None:
        """Wraps a parent TimeValueModel, interpreted as seconds and displayed as seconds."""
        super().__init__(*args, **kwargs)
        self._parent_model = parent_model
        self._time_display_model = time_display_model
        self._fps_model = fps_model
        self._sub = self._parent_model.subscribe_value_changed_fn(self._parent_value_changed)

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.as_string})>"

    def set_value(self, value) -> None:
        self._parent_model.set_value(value)

    def _parent_value_changed(self, value_model: ui.AbstractValueModel):
        self.set_value(self._parent_model.as_float)
        self._value_changed()

    @property
    def as_float(self):
        return self._parent_model.as_float

    @property
    def time_units(self):
        return self._parent_model.time_units

    @property
    def time_display(self) -> str:
        return self._time_display_model.as_string

    @property
    def fps(self) -> float:
        return self._fps_model.as_float

    @property
    def as_frames(self) -> float:
        if self._parent_model.time_units == TimeUnits.SECONDS:
            return self._parent_model.as_float * self.fps
        if self._parent_model.time_units == TimeUnits.FRAMES:
            return self._parent_model.as_float

    @as_frames.setter
    def as_frames(self, value: float):
        if self.fps == 0:
            self._parent_model.as_float = 0.0
            return

        if self._parent_model.time_units == TimeUnits.SECONDS:
            self._parent_model.as_float = value / self.fps
        if self._parent_model.time_units == TimeUnits.FRAMES:
            self._parent_model.as_float = value

    @property
    def as_seconds(self) -> float:
        if self._parent_model.time_units == TimeUnits.SECONDS:
            return self._parent_model.as_float
        if self._parent_model.time_units == TimeUnits.FRAMES:
            if self.fps == 0:
                return 0
            return self._parent_model.as_float / self.fps

    @as_seconds.setter
    def as_seconds(self, value: float):
        if self._parent_model.time_units == TimeUnits.SECONDS:
            self._parent_model.as_float = value
        if self._parent_model.time_units == TimeUnits.FRAMES:
            self._parent_model.as_float = value * self.fps

    @property
    def as_smpte(self):
        if self._parent_model.time_units == TimeUnits.SECONDS:
            return SMPTE_Timecode.from_seconds(self.as_seconds, self.fps)
        if self._parent_model.time_units == TimeUnits.FRAMES:
            return SMPTE_Timecode.from_frames(self.as_frames, self.fps)
        raise ValueError(f"Invalid time units for smpte display: {self.time_units}")

    def set_value_as_unit(self, value: float, time_unit: str):
        if time_unit == TimeUnits.SECONDS:
            self.as_seconds = value
            return
        if time_unit == TimeUnits.FRAMES:
            self.as_frames = value
            return
        raise ValueError(f"Invalid time unit: {time_unit}")

    def get_value_as_string(self) -> str:
        if self.time_display == TimeDisplay.SECONDS:
            return f"{_pretty_print_float(self.as_seconds, rounding_digits=2)}s"
        if self.time_display == TimeDisplay.FRAMES:
            return f"{_pretty_print_float(self.as_frames, precision=2)}"
        if self.time_display in (TimeDisplay.SMPTE, TimeDisplay.TIMECODE):
            return f"{self.as_smpte}"
        raise ValueError("Invalid time display")

    @property
    def read_only(self):
        return self._parent_model.read_only
