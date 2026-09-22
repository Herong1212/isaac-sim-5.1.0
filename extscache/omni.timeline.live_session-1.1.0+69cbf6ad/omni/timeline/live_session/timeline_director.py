import omni.usd
import omni.timeline
import carb.events

from .timeline_event import TimelineEvent
from .timeline_serializer import TimelineStateSerializer
from .timeline_session_role import TimelineSessionRole


class TimelineDirector(TimelineSessionRole):
    def __init__(self, usd_context_name: str, serializer: TimelineStateSerializer, session):
        super().__init__(usd_context_name, serializer, session)

        self._timeline = self._main_timeline
        self._timeline_sub = self._timeline.get_timeline_event_stream().create_subscription_to_pop(
            self._on_timeline_event
        )

    def start_session(self) -> bool:
        if not super().start_session():
            return False
        self._serializer.initialize(
            timeline=self._timeline,
            synced_stage=self._synced_stage,
            sending=True
        )
        return True

    def enable_sync(self, enabled: bool):
        if enabled == self._enable_sync:
            return
        super().enable_sync(enabled)
        if enabled:
            self._timeline_sub = self._timeline.get_timeline_event_stream().create_subscription_to_pop(
                self._on_timeline_event
            )
            self._update_timeline_state()
        else:
            self._timeline_sub = self._timeline.get_timeline_event_stream().create_subscription_to_pop(
                self._on_timeline_permanent_tick
            )

    def stop_session(self):
        super().stop_session()
        self._serializer.finalize()
        self._timeline_sub = None

    def _on_timeline_event(self, e: carb.events.IEvent):
        self._serializer.sendTimelineUpdate(TimelineEvent.from_carb_event(e))

    def _on_timeline_permanent_tick(self, e: carb.events.IEvent):
        if e.type == int(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED_PERMANENT):
            self._serializer.sendTimelineUpdate(TimelineEvent.from_carb_event(e))

    def _update_timeline_state(self):
        event = TimelineEvent(
            omni.timeline.TimelineEventType.CURRENT_TIME_TICKED,
            {'currentTime' : self._timeline.get_current_time()}
        )
        self._serializer.sendTimelineUpdate(event)

        event = TimelineEvent(
            omni.timeline.TimelineEventType.LOOP_MODE_CHANGED,
            {'looping' : self._timeline.is_looping()}
        )
        self._serializer.sendTimelineUpdate(event)

        event = TimelineEvent(
            omni.timeline.TimelineEventType.ZOOM_CHANGED,
            {
             'startTime' : self._timeline.get_zoom_start_time(),
             'endTime' : self._timeline.get_zoom_end_time(),
            }
        )
        self._serializer.sendTimelineUpdate(event)

        event = TimelineEvent(omni.timeline.TimelineEventType.STOP)
        if self._timeline.is_playing():
            event = TimelineEvent(omni.timeline.TimelineEventType.PLAY)
        elif not self._timeline.is_stopped():
            event = TimelineEvent(omni.timeline.TimelineEventType.PAUSE)
        self._serializer.sendTimelineUpdate(event)