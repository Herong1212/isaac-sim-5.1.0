from omni import ui

from .time_units import TimeUnits


class TimeValueModel(ui.SimpleFloatModel):
    def __init__(
        self,
        value: float,
        time_units: str = TimeUnits.SECONDS,
        read_only: bool = False,
        *args,
        **kwargs,
    ) -> None:
        """A simple float value model for time with a specified time unit.
        Note: Read only flag is a hint for views and item models - it is not enforced in the value model."""
        self._time_units = time_units
        self._read_only = read_only
        super().__init__(value, *args, **kwargs)

    def __repr__(self):
        return f"<{self.__class__.__name__}(value={self.as_float}, time_units={self._time_units})>"

    @property
    def time_units(self):
        return self._time_units

    @property
    def read_only(self):
        return self._read_only

    @read_only.setter
    def read_only(self, value):
        if value == self._read_only:
            return
        self._read_only = value
        # value change to trigger field widget update
        self._value_changed()
