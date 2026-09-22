import omni.ext
import omni.kit.app
import omni.timeline
from omni import ui

from .ui_helpers import WeakMethod

_timeline = omni.timeline.get_timeline_interface()
_setters = {
    omni.timeline.TimelineEventType.START_TIME_CHANGED: _timeline.set_start_time,
    omni.timeline.TimelineEventType.END_TIME_CHANGED: _timeline.set_end_time,
    omni.timeline.TimelineEventType.CURRENT_TIME_CHANGED: _timeline.set_current_time,
}
_getters = {
    omni.timeline.TimelineEventType.START_TIME_CHANGED: _timeline.get_start_time,
    omni.timeline.TimelineEventType.END_TIME_CHANGED: _timeline.get_end_time,
    omni.timeline.TimelineEventType.CURRENT_TIME_CHANGED: _timeline.get_current_time,
}


class TimelineValueModel(ui.AbstractValueModel):
    def __init__(self, event_type=omni.timeline.TimelineEventType.END_TIME_CHANGED):
        super().__init__()
        self._event_type = event_type

        # relam -- Finding a better home for this would remove another dependency
        self._timeline_event_sub = _timeline.get_timeline_event_stream().create_subscription_to_pop(
            WeakMethod(self._on_timeline_event)
        )
        self._time_codes = _timeline.get_time_codes_per_seconds()
        self._getter = _getters.get(self._event_type)
        self._setter = _setters.get(self._event_type)
        self._time_value = self._getter()
        self._new_time_value = None

    def __del__(self):
        self._timeline_event_sub = None
        self._timeline = None

    def _on_timeline_event(self, evt):
        this_type = int(self._event_type)
        if evt.type == this_type:
            self._time_value = self._getter()
            self._value_changed()
        elif evt.type == int(omni.timeline.TimelineEventType.TIME_CODE_PER_SECOND_CHANGED):
            self._time_codes = _timeline.get_time_codes_per_seconds()
            self._value_changed()
        elif self._event_type == omni.timeline.TimelineEventType.CURRENT_TIME_CHANGED:
            if (
                (evt.type == int(omni.timeline.TimelineEventType.CURRENT_TIME_CHANGED))
                or (evt.type == int(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED))
                or (evt.type == int(omni.timeline.TimelineEventType.STOP))
            ):
                self._value_changed()

    def get_value_as_string(self):
        if self._time_value is None:
            return
        return str("{:.0f}".format(self._time_value * self._time_codes))

    def get_value_as_float(self):
        if self._time_value is None:
            return
        return self._time_value * self._time_codes

    def begin_edit(self):
        pass

    def set_value(self, value):
        try:
            v = float(value)
            self._new_time_value = v
        except ValueError:
            self._new_time_value = None

    def end_edit(self):
        if self._new_time_value is None:
            return
        if self._new_time_value == self._time_value:
            return
        if not self._setter:
            return

        clamped_value = min(max(self._new_time_value, 0), 999999)
        self._time_value = clamped_value / self._time_codes

        # set time in kit
        self._setter(self._time_value)
        # tell listeners value has changed
        self._value_changed()
        self._new_time_value = None
