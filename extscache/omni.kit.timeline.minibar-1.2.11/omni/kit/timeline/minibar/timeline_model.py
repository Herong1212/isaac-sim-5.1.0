import math

import omni.ext
import omni.kit.app
import omni.timeline
import omni.ui as ui
from omni.timeline import TimelineEventType


class TimelineLoopModel(ui.AbstractValueModel):
    def __init__(self):
        super().__init__()
        self._timeline = omni.timeline.get_timeline_interface()
        self._timeline_sub = self._timeline.get_timeline_event_stream().create_subscription_to_pop_by_type(
            TimelineEventType.LOOP_MODE_CHANGED, self._on_timeline_event
        )

    def __del__(self):  # pragma: no cover
        self.destroy()

    def destroy(self):  # pragma: no cover
        self._timeline_sub = None
        self._timeline = None

    def _on_timeline_event(self, evt):
        self._value_changed()

    def get_value_as_bool(self):
        return self._timeline.is_looping()

    def set_value(self, value: bool):
        self._timeline.set_looping(value)


class TimelinePlayModel(ui.AbstractValueModel):
    def __init__(self):
        super().__init__()
        self._timeline = omni.timeline.get_timeline_interface()
        self._timeline_sub = self._timeline.get_timeline_event_stream().create_subscription_to_pop(
            self._on_timeline_event, name="Timeline Minibar TimelinePlayModel"
        )

    def __del__(self):  # pragma: no cover
        self.destroy()

    def destroy(self):  # pragma: no cover
        self._timeline_sub = None
        self._timeline = None

    def _on_timeline_event(self, evt):
        value = int(evt.type)
        if value in [int(TimelineEventType.PLAY), int(TimelineEventType.STOP), int(TimelineEventType.PAUSE)]:
            self._value_changed()

    def get_value_as_bool(self):
        return self._timeline.is_playing()

    def set_value(self, value: bool):
        if value:
            self._timeline.play()
        else:
            self._timeline.pause()


class TimelineStartModel(ui.AbstractValueModel):
    def __init__(self):
        super().__init__()
        self._timeline = omni.timeline.get_timeline_interface()
        self._timeline_sub = self._timeline.get_timeline_event_stream().create_subscription_to_pop(
            self._on_timeline_event, name="Timeline Minibar TimelineStartModel"
        )
        self._on_editing = False
        self._edit_value = 0

    def __del__(self):  # pragma: no cover
        self.destroy()

    def destroy(self):  # pragma: no cover
        self._timeline_sub = None
        self._timeline = None

    def _on_timeline_event(self, evt):
        value = int(evt.type)
        if value in [int(TimelineEventType.START_TIME_CHANGED), int(TimelineEventType.TIME_CODE_PER_SECOND_CHANGED)]:
            self._value_changed()

    def get_value_as_int(self):
        tps = self._timeline.get_time_codes_per_seconds()
        return round(self._timeline.get_start_time() * tps)

    def set_value(self, value: int):
        if self._on_editing:
            self._edit_value = value
            return

        try:
            v = int(value)
        except ValueError:
            return

        tps = self._timeline.get_time_codes_per_seconds()
        if math.isclose(tps, 0):
            return

        v = min(self._timeline.get_end_time() * tps - 1, v)
        self._timeline.set_start_time(v / tps)

    def begin_edit(self) -> None:
        self._on_editing = True

    def end_edit(self) -> None:
        super().end_edit()
        self._on_editing = False
        self.set_value(self._edit_value)


class TimelineEndModel(ui.AbstractValueModel):
    def __init__(self):
        super().__init__()
        self._timeline = omni.timeline.get_timeline_interface()
        self._timeline_sub = self._timeline.get_timeline_event_stream().create_subscription_to_pop(
            self._on_timeline_event, name="Timeline Minibar TimelineEndModel"
        )
        self._on_editing = False
        self._edit_value = 0

    def __del__(self):  # pragma: no cover
        self.destroy()

    def destroy(self):  # pragma: no cover
        self._timeline_sub = None
        self._timeline = None

    def _on_timeline_event(self, evt):
        value = int(evt.type)
        if value in [int(TimelineEventType.END_TIME_CHANGED), int(TimelineEventType.TIME_CODE_PER_SECOND_CHANGED)]:
            self._value_changed()

    def get_value_as_int(self):
        tps = self._timeline.get_time_codes_per_seconds()
        return round(self._timeline.get_end_time() * tps)

    def set_value(self, value):
        if self._on_editing:
            self._edit_value = value
            return

        try:
            v = int(value)
        except ValueError:
            return

        tps = self._timeline.get_time_codes_per_seconds()
        if math.isclose(tps, 0):
            return
        v = max(self._timeline.get_start_time() * tps + 1, v)

        self._timeline.set_end_time(v / tps)

    def begin_edit(self) -> None:
        self._on_editing = True

    def end_edit(self) -> None:
        super().end_edit()
        self._on_editing = False
        self.set_value(self._edit_value)


class TimelineCurrentModel(ui.AbstractValueModel):
    def __init__(self):
        super().__init__()
        self._timeline = omni.timeline.get_timeline_interface()
        self._timeline_sub = self._timeline.get_timeline_event_stream().create_subscription_to_pop(
            self._on_timeline_event, name="Timeline Minibar TimelinePlayModel"
        )

    def __del__(self):  # pragma: no cover
        self.destroy()

    def destroy(self):  # pragma: no cover
        self._timeline_sub = None
        self._timeline = None

    def _on_timeline_event(self, evt):
        value = int(evt.type)
        if value in [
            int(TimelineEventType.STOP),
            int(TimelineEventType.CURRENT_TIME_CHANGED),
            int(TimelineEventType.CURRENT_TIME_TICKED),
            int(TimelineEventType.TIME_CODE_PER_SECOND_CHANGED),
        ]:
            self._value_changed()

    def get_value_as_int(self):
        tps = self._timeline.get_time_codes_per_seconds()
        return round(self._timeline.get_current_time() * tps)

    def set_value(self, value: int):
        try:
            v = int(value)
        except ValueError:
            return

        tps = self._timeline.get_time_codes_per_seconds()
        if math.isclose(tps, 0):
            return

        self._timeline.set_current_time(v / tps)

    def begin_edit(self) -> None:
        pass
