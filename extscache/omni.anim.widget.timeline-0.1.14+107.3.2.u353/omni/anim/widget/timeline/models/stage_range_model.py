import typing

import carb.events
import omni.timeline
import omni.usd

from .range_model import RangeModel
from .time_range_controller import TimeRangeController
from .time_units import TimeUnits


class StageRangeModel(RangeModel):
    def __init__(
        self,
        context: typing.Optional[omni.usd.UsdContext] = None,
        use_range_controller: bool = True,
        max_range_read_only: bool = False,
    ):
        self._context = context or omni.usd.get_context()
        self._timeline_interface = self._context.get_timeline()

        time_codes_per_second = self._timeline_interface.get_time_codes_per_seconds()
        current_time = self._timeline_interface.get_current_time() * time_codes_per_second
        start_time = self._timeline_interface.get_start_time() * time_codes_per_second
        end_time = self._timeline_interface.get_end_time() * time_codes_per_second

        super().__init__(
            time_units=TimeUnits.USD_TIMECODE,
            current_time=current_time,
            start=start_time,
            end=end_time,
            min=start_time,
            max=end_time,
            fps=time_codes_per_second,
            max_range_read_only=max_range_read_only,
        )

        # Keeps view range within full range when editing.
        self._time_range_controller = TimeRangeController(self) if use_range_controller else None

        self._timeline_event_sub = self._timeline_interface.get_timeline_event_stream().create_subscription_to_pop(
            self._on_timeline_event
        )

        self._stage_sub = self._context.get_stage_event_stream().create_subscription_to_pop(self._on_stage_event)

    def destroy(self):
        self._time_range_controller = None
        if self._timeline_event_sub:
            self._timeline_event_sub.unsubscribe()
            self._timeline_event_sub = None
        if self._stage_sub:
            self._stage_sub.unsubscribe()
            self._stage_sub = None
        self._context = None
        self._timeline_interface = None

    @property
    def current_time(self):
        return self.current_time_model.as_float

    @current_time.setter
    def current_time(self, value) -> None:
        self._set_current_time(value, False)

    @property
    def tentative_time(self) -> typing.Optional[float]:
        if self._timeline_interface.get_tentative_time() == self._timeline_interface.get_current_time():
            return None
        return self._timeline_interface.get_tentative_time() * self._timeline_interface.get_time_codes_per_seconds()

    @tentative_time.setter
    def tentative_time(self, value):
        self._set_current_time(value, True)

    def _set_current_time(self, frame: float, tentative=False):
        self.current_time_model.as_float = frame

        if self._timeline_interface.is_playing():
            self._timeline_interface.pause()

        frames_per_second = self._timeline_interface.get_time_codes_per_seconds()
        if frames_per_second == 0:
            seconds_value = 0
        else:
            seconds_value = frame / frames_per_second

        if tentative:
            self._timeline_interface.set_tentative_time(seconds_value)
        else:
            self._timeline_interface.set_current_time(seconds_value)

    def _on_timeline_event(self, event: carb.events.IEvent):
        if event.type == int(omni.timeline.TimelineEventType.TIME_CODE_PER_SECOND_CHANGED):
            time_codes_per_second = self._timeline_interface.get_time_codes_per_seconds()
            self.fps_model.as_float = time_codes_per_second
            self._item_changed(None)

        if event.type == int(omni.timeline.TimelineEventType.START_TIME_CHANGED):
            new_start = (
                self._timeline_interface.get_start_time() * self._timeline_interface.get_time_codes_per_seconds()
            )
            zoomed = self.zoomed  # check zoom state before changes
            if self.max_range:
                self.max_range.start_model.as_float = new_start
                if not zoomed:
                    self.view_range.start_model.as_float = new_start
            else:
                self.view_range.start_model.as_float = new_start
            self._item_changed(None)

        elif event.type == int(omni.timeline.TimelineEventType.END_TIME_CHANGED):
            new_end = self._timeline_interface.get_end_time() * self._timeline_interface.get_time_codes_per_seconds()
            zoomed = self.zoomed  # check zoom state before changes

            if self.max_range:
                self.max_range.end_model.as_float = new_end
                if not zoomed:
                    self.view_range.end_model.as_float = new_end
            else:
                self.view_range.end_model.as_float = new_end
            self._item_changed(None)

        elif event.type in (
            int(omni.timeline.TimelineEventType.CURRENT_TIME_CHANGED),
            int(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED),
            int(omni.timeline.TimelineEventType.STOP),
        ):
            frames_per_second = self._timeline_interface.get_time_codes_per_seconds()
            current_time = self._timeline_interface.get_current_time()
            current_time_frame = current_time * frames_per_second
            if self.current_time_model.as_float != current_time_frame:
                self.current_time_model.set_value(current_time_frame)

        elif event.type in (int(omni.timeline.TimelineEventType.TENTATIVE_TIME_CHANGED),):
            frames_per_second = self._timeline_interface.get_time_codes_per_seconds()
            tentative_time = self._timeline_interface.get_tentative_time()
            tentative_time_frame = tentative_time * frames_per_second
            if self.current_time_model.as_float != tentative_time_frame:
                self.current_time_model.set_value(tentative_time_frame)

    def end_edit(self, item=None):
        super().end_edit(item)
        self.push_to_stage()

    def push_to_stage(self):
        if not self.max_range:
            return
        frames_per_second = self._timeline_interface.get_time_codes_per_seconds()
        start_time = self._timeline_interface.get_start_time() * frames_per_second  # get start time is in seconds
        end_time = self._timeline_interface.get_end_time() * frames_per_second  # get end time is in seconds
        new_start_time = self.max_range.start_model.as_float / frames_per_second
        new_end_time = self.max_range.end_model.as_float / frames_per_second
        if start_time != new_start_time:
            self._timeline_interface.set_start_time(new_start_time)
        if end_time != new_end_time:
            self._timeline_interface.set_end_time(new_end_time)

    def _on_stage_event(self, stage_event: carb.events.IEvent):
        if stage_event.type == int(omni.usd.StageEventType.OPENED):
            frames_per_second = self._timeline_interface.get_time_codes_per_seconds()
            start = self._timeline_interface.get_start_time() * frames_per_second
            end = self._timeline_interface.get_end_time() * frames_per_second
            if self.max_range:
                self.max_range.start_model.set_value(start)
                self.max_range.end_model.set_value(end)
            self.view_range.start_model.set_value(start)
            self.view_range.end_model.set_value(end)
            self._item_changed(None)
