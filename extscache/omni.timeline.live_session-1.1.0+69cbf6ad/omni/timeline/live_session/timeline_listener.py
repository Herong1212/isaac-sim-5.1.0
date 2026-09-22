import asyncio
import carb
import omni.kit.app
import omni.timeline
import omni.usd

from typing import List
from .global_time import get_global_time_s
from .timeline_serializer import TimelineStateSerializer
from .sync_strategy import SyncStrategyDescriptor, SyncStrategyType, TimelineSyncStrategyExecutor
from .timeline_event import TimelineEvent
from .timeline_session_role import TimelineSessionRole


TIMESTAMP_SYNC_EPS = 1e-3  # 1 ms


class TimelineListener(TimelineSessionRole):
    def __init__(
        self,
        usd_context_name: str,
        serializer: TimelineStateSerializer,
        session,
        sync_strategy: SyncStrategyDescriptor = None
    ):
        super().__init__(usd_context_name, serializer, session)
        self._app_sub = None
        self._is_director_timeline_supported = hasattr(self._main_timeline, 'set_director')
        self._timeline_name = 'timeline_director'
        if not self._is_director_timeline_supported:
            carb.log_warn("Timeline sync: use a newer Kit version to support all features.")
            self._director_timeline = self._main_timeline
            self._controlled_timeline = None
        else:
            self._controlled_timeline = self._main_timeline
            self._initialize_director_timeline()

        if sync_strategy is None:
            sync_strategy = SyncStrategyDescriptor(SyncStrategyType.DIFFERENCE_LIMITED)
        self._timeline_sync_executor = TimelineSyncStrategyExecutor(sync_strategy, self._director_timeline)

    def start_session(self, catch_up: bool = True) -> bool:
        if not super().start_session():
            return False
        self._initialize_director_timeline()

        self._serializer.initialize(
            timeline=self._director_timeline,
            synced_stage=self._synced_stage,
            sending=False
        )
        asyncio.ensure_future(self._start_session(catch_up))
        return True

    @property
    def sync_strategy(self):
        return self._timeline_sync_executor

    async def _start_session(self, catch_up):
        # make sure the director is set before it recieves the updates
        await omni.kit.app.get_app().next_update_async()

        # catch up with the current state
        if catch_up:
            self._check_time(None)

        self._app_sub = self._ed.observe_event(
            event_name=omni.kit.app.GLOBAL_EVENT_UPDATE,
            on_event=self._check_time,
            observer_name="omni.timeline.live_session.timeline_listener"
        )

    def stop_session(self):
        super().stop_session()
        self._serializer.finalize()
        if self._controlled_timeline is not None:
            self._controlled_timeline.set_director(None)
            omni.timeline.destroy_timeline(self._timeline_name)
        self._app_sub = None

    def enable_sync(self, enabled: bool):
        if enabled == self._enable_sync:
            return
        super().enable_sync(enabled)
        if enabled:
            if self._synced_stage is None:
                carb.log_error(f"{self.__class__}: could not find presence layer")
                return
            self._initialize_director_timeline()
            self._serializer.initialize(
                timeline=self._director_timeline,
                synced_stage=self._synced_stage,
                sending=False
            )
            self._timeline_sync_executor.reset()
            asyncio.ensure_future(self._start_session(True))
        else:
            if self._controlled_timeline:
                self._controlled_timeline.set_director(None)
            self._app_sub = None

    def get_latency_estimate(self) -> float:
        return max(get_global_time_s() - self._last_update_timestamp, 0)

    def _warn_once(self, tag: str, msg: str):
        attr_name = "__logged_" + tag
        if not hasattr(self, attr_name):
            setattr(self, attr_name, False)
        if not getattr(self, attr_name):
            carb.log_warn(msg)
            setattr(self, attr_name, True)

    def _save_timestamp(self, timestamp: float):
        if get_global_time_s() + TIMESTAMP_SYNC_EPS < timestamp:
            self._warn_once(
                "global_time_sync",
                "Future timestamp received. Global time is inaccurate, latency estimates are unreliable."
            )
        self._last_update_timestamp = max(self._last_update_timestamp, timestamp)

    def _update_latency_timestamp(self, events: List[TimelineEvent]):
        if len(events) == 0:
            self._save_timestamp(self._serializer.receiveTimestamp())
        for event in events:
            self._save_timestamp(event.timestamp)

    def _check_time(self, _):
        events = self._serializer.receiveTimelineUpdate()
        actions_to_execute = events
        self._update_latency_timestamp(events)
        if self._timeline_sync_executor is not None:
            actions_to_execute = self._timeline_sync_executor.process_events(events)
        for event in actions_to_execute:
            self._apply_time_event(event)

    def _apply_time_event(self, event: TimelineEvent):
        type_id = int(event.type)
        if type_id == int(omni.timeline.TimelineEventType.PLAY):
            self._director_timeline.play()
        elif type_id == int(omni.timeline.TimelineEventType.PAUSE):
            self._director_timeline.pause()
        elif type_id == int(omni.timeline.TimelineEventType.STOP):
            self._director_timeline.stop()
        elif type_id == int(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED):
            time = event.payload['currentTime']
            self._director_timeline.set_current_time(time)
        elif type_id == int(omni.timeline.TimelineEventType.LOOP_MODE_CHANGED):
            looping = event.payload['looping']
            self._director_timeline.set_looping(looping)
        elif type_id == int(omni.timeline.TimelineEventType.ZOOM_CHANGED):
            start_time, end_time = event.payload['startTime'], event.payload['endTime']
            self._director_timeline.set_zoom_range(start_time, end_time)

    def _initialize_director_timeline(self):
        if self._controlled_timeline is None:
            return

        time = self._controlled_timeline.get_current_time()
        playing = self._controlled_timeline.is_playing()
        stopped = self._controlled_timeline.is_stopped()

        self._director_timeline = omni.timeline.get_timeline_interface(self._timeline_name)
        self._director_timeline.set_end_time(self._controlled_timeline.get_end_time())
        self._director_timeline.set_start_time(self._controlled_timeline.get_start_time())
        self._director_timeline.set_time_codes_per_second(self._controlled_timeline.get_time_codes_per_seconds())

        self._director_timeline.set_current_time(time)
        if not playing:
            if stopped:
                self._director_timeline.stop()
            else:
                self._director_timeline.pause()

        self._director_timeline.commit()

        self._controlled_timeline.set_director(self._director_timeline)
