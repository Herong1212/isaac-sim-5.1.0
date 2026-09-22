import typing

import omni.timeline
from omni import ui

from .time_units import TimeUnits
from .time_value_model import TimeValueModel

g_timeline_interface = omni.timeline.get_timeline_interface()


class RangeItem(ui.AbstractItem):
    """Simple range item, values are floats representing seconds."""

    def __init__(
        self,
        name: str = "range",
        start: float = 0,
        end: float = 100,
        time_units: str = TimeUnits.SECONDS,
        fps: typing.Optional[typing.Union[float, ui.SimpleFloatModel]] = None,
        read_only=False,
    ):
        super().__init__()
        self._time_units = time_units
        self._read_only = read_only
        self._name_model = ui.SimpleStringModel(name)
        self._start_model = TimeValueModel(start, time_units=self._time_units, read_only=read_only)
        self._end_model = TimeValueModel(end, time_units=self._time_units, read_only=read_only)

        if fps and isinstance(fps, float):
            self._fps_model = ui.SimpleFloatModel(fps)
        elif fps and isinstance(fps, ui.SimpleFloatModel):
            self._fps_model = fps
        else:
            self._fps_model = None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self._name_model.as_string}', start={self._start_model.as_float}, end={self._end_model.as_float}, time_units={self.time_units}, fps={self.fps})>"

    @property
    def fps(self) -> float:
        if self._fps_model:
            return self._fps_model.as_float
        else:
            return g_timeline_interface.get_time_codes_per_seconds()

    @property
    def time_units(self):
        return self._time_units

    @property
    def start_model(self) -> TimeValueModel:
        return self._start_model

    @property
    def end_model(self) -> TimeValueModel:
        return self._end_model

    @property
    def name_model(self) -> ui.SimpleStringModel:
        return self._name_model

    @property
    def fps_model(self) -> typing.Optional[ui.SimpleFloatModel]:
        return self._fps_model

    @property
    def start(self) -> float:
        return self._start_model.as_float

    @property
    def end(self) -> float:
        return self._end_model.as_float

    @property
    def is_valid(self) -> bool:
        return self._start_model.as_float <= self._end_model.as_float

    @property
    def value_model_count(self) -> int:
        return 3

    @property
    def length(self) -> float:
        return self._end_model.as_float - self._start_model.as_float

    @property
    def length_inclusive(self) -> float:
        return (self._end_model.as_float - self._start_model.as_float) + 1

    @property
    def read_only(self) -> bool:
        return self._read_only
