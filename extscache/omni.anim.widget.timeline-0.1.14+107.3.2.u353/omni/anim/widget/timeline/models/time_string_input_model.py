import typing

import carb
from omni import ui
from omni.kit.preferences.animation import TimeDisplay

from .smpte import SMPTE_Timecode
from .time_display_value_model import TimeDisplayValueModel
from .time_units import TimeUnits


class TimeStringInputModel(ui.SimpleStringModel):
    """Wraps a parent time model for string input validation and coercion."""

    def __init__(self, parent_model=TimeDisplayValueModel) -> None:
        super().__init__(parent_model.as_string)
        self._parent_model = parent_model

        # Sub is only to trick field to use this model and not parent.
        self._sub = self._parent_model.subscribe_value_changed_fn(self._parent_value_changed)

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.as_string})>"

    def _parent_value_changed(self, model: ui.AbstractValueModel):
        self._value_changed()

    def begin_edit(self) -> None:
        self._parent_model.begin_edit()
        return super().begin_edit()

    def end_edit(self) -> None:
        self._parent_model.end_edit()
        return super().end_edit()

    @property
    def is_valid(self) -> bool:
        value, _ = self.string_to_value(self.as_string)
        return value is not None

    def string_to_value(self, input: str) -> typing.Tuple[typing.Optional[float], str]:
        """
        Coerce the input string to a time unit float.
        Use the parent model time display to infer the input type.
        An input ending with `s` will be treated as seconds.
        Valid timecode string will be treated coverted to seconds or frames depending on parent.
        """
        # default our input assumption to seconds
        input_unit = TimeUnits.SECONDS
        # but if the parent display unit is frames, override that assumption
        if self._parent_model.time_display == TimeUnits.FRAMES:
            input_unit = TimeUnits.FRAMES

        # Try to interpret simple float value as seconds or frames
        input = input.strip()
        if input.endswith("s"):
            # but user can force to seconds by adding s
            input_unit = TimeDisplay.SECONDS
            input = input[:-1]
        try:
            float_value = float(input)
            return (float_value, input_unit)
        except ValueError:
            pass

        # if not a simple float value, see if smpte is input
        smpte = SMPTE_Timecode.from_string(input=input, fps=self._parent_model.fps)
        if smpte:
            if self._parent_model.time_units == TimeUnits.SECONDS:
                input_unit = TimeDisplay.SECONDS
                return (smpte.as_seconds, input_unit)
            elif self._parent_model.time_units == TimeUnits.FRAMES:
                input_unit = TimeDisplay.FRAMES
                return (smpte.as_frames, input_unit)

        return (None, f"Invalid time value: {input}")

    def commit(self):
        """Commit value to parent model."""
        value, unit_type = self.string_to_value(self.as_string)
        if value is None:
            carb.log_error(f"Cannot commit: {self.as_string}")
            return
        self._parent_model.set_value_as_unit(value, unit_type)
