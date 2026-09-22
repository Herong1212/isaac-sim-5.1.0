import enum
import omni.timeline
from carb import log_error
from typing import List
from .global_time import get_global_time_s
from .timeline_event import TimelineEvent

class SyncStrategyType(enum.Enum):
    STRICT = 0
    """
    Moves the time only when a new time update is received.
    No difference is allowed from the last known current time.
    """

    DIFFERENCE_LIMITED = 1
    """
    When the timeline is not playing, no difference is allowed from the last 
    known current time.

    When the timeline is playing, the listener's current time may differ from
    that of the presenter. The maximum difference in seconds can be set in the
    "max_time_diff_sec" parameter of the SyncStrategyDescriptor.

    If the allowed difference is zero, this strategy falls back to "STRICT" mode.
    Otherwise, 
    - the listener may run freely even if no new time update is received 
      until it reaches the maximum allowed difference, then it pauses to wait
      for the presenter, 
    - when the listener is behind the presenter more than the maximum allowed 
      difference, it will speed up its playback speed for a short time to catch up 
      with the presenter instead of jumping directly to the last known current time.
    """

    LOOSE = 2
    """
    Synchronizes current time only when the timeline is not playing.
    Useful when all we care about is whether the presented started playing and what
        the current was before that.
    Time difference can be unlimited if played for long.
    """


class SyncStrategyDescriptor:
    def __init__(
        self, 
        strategy_type: SyncStrategyType,
        max_time_diff_sec: float = 1
    ) -> None:
        self.strategy_type = strategy_type
        self.max_time_diff_sec = max_time_diff_sec


class TimeInterpolator:
    # wc_: wall clock time, sim_: simulation time
    def __init__(self, sim_start = 0.0, sim_target = 0.0, wc_duration = 1.0):
        self.start = sim_start
        self.target = sim_target
        self.wc_duration = min((sim_target - sim_start) / 4,  wc_duration)
        self.wc_start = get_global_time_s()
    
    def get_interpolated(self, wc_time):
        t = (wc_time - self.wc_start) / self.wc_duration  # to [0,1]
        t = min(max(0, t), 1)
        t_sq = t * t
        t = 3 * t_sq - 2 * t_sq * t  # smoothstep

        return (1 - t) * self.start + t * self.target  # [0,1] to sim time


# TODO: find a better name...
class TimelineSyncStrategyExecutor:
    def __init__(self, desc: SyncStrategyDescriptor, timeline):
        self._strategy_desc = desc
        self._timeline = timeline

        self._is_presenter_playing = False
        self.reset()

    @property
    def strategy_desc(self) -> SyncStrategyDescriptor:
        return self._strategy_desc

    @strategy_desc.setter
    def strategy_desc(self, desc: SyncStrategyDescriptor):
        # one of them is zero, reset status of diff limited
        # (otherwise we do not need to)
        if desc.max_time_diff_sec * self._strategy_desc.max_time_diff_sec < 0.00001:
            self.reset()
        self._strategy_desc = desc

    def process_events(self, events: List[TimelineEvent]) -> List[TimelineEvent]:
        """
        Processes the incoming timeline update events and decides what to do.
        Returns a new list of timeline events that may not contain any of the input events.
        """
        if self._strategy_desc.strategy_type == SyncStrategyType.STRICT:
            return self._process_strict(events)
        elif self._strategy_desc.strategy_type == SyncStrategyType.LOOSE:
            return self._process_loose(events)
        elif self.strategy_desc.strategy_type == SyncStrategyType.DIFFERENCE_LIMITED:
            if self.strategy_desc.max_time_diff_sec < 0.0001:
                return self._process_strict(events)
            else:
                return self._process_diff_limited(events)
        else:
            log_error(f'Sync strategy not implemented: {self._strategy_desc.strategy_type}')

    def reset(self):
        self._is_suspended = False  # True: extrapolated too much, waiting
        self._interpolating = False
        self._time_interpolator = TimeInterpolator()
        self._last_known_sim_time = None

    # event processing shared between all strategy types
    def _process_event_common(self, event: TimelineEvent, out_events: List[TimelineEvent]):
        if event.type == int(omni.timeline.TimelineEventType.PLAY):
            self._is_presenter_playing = True
        elif event.type == int(omni.timeline.TimelineEventType.PAUSE):
            self._is_presenter_playing = False
            self.reset()
        elif event.type == int(omni.timeline.TimelineEventType.STOP):
            self._is_presenter_playing = False
            self.reset()
        elif event.type == int(omni.timeline.TimelineEventType.LOOP_MODE_CHANGED):
            out_events.append(event)
        elif event.type == int(omni.timeline.TimelineEventType.ZOOM_CHANGED):
            out_events.append(event)

    def _process_strict(self, events: List[TimelineEvent]) -> List[TimelineEvent]:
        out_events = []
        for event in events:
            self._process_event_common(event, out_events)
            if event.type == int(omni.timeline.TimelineEventType.PLAY):
                # Play but then pause immediately
                out_events.append(TimelineEvent(omni.timeline.TimelineEventType.PLAY, {}))
                out_events.append(TimelineEvent(omni.timeline.TimelineEventType.PAUSE, {}))
            elif event.type == int(omni.timeline.TimelineEventType.PAUSE):
                out_events.append(event)
            elif event.type == int(omni.timeline.TimelineEventType.STOP):
                out_events.append(event)
            elif event.type == int(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED):
                self._last_known_sim_time = event.payload['currentTime']
                # Play if needed, Sync the time then pause
                if not self._timeline.is_playing():
                    out_events.append(TimelineEvent(omni.timeline.TimelineEventType.PLAY, {}))
                out_events.append(event)
                out_events.append(TimelineEvent(omni.timeline.TimelineEventType.PAUSE, {}))
        return out_events

    def _process_loose(self, events: List[TimelineEvent]) -> List[TimelineEvent]:
        out_events = []
        for event in events:
            self._process_event_common(event, out_events)
            if event.type == int(omni.timeline.TimelineEventType.PLAY):
                out_events.append(event)
            elif event.type == int(omni.timeline.TimelineEventType.PAUSE):
                out_events.append(event)
            elif event.type == int(omni.timeline.TimelineEventType.STOP):
                out_events.append(event)
            elif event.type == int(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED):
                self._last_known_sim_time = event.payload['currentTime']
                # Care about the time only when the not playing
                if not self._timeline.is_playing():
                    out_events.append(event)
        return out_events
    
    def _start_interpolation(self, t0: float, t: float):
        dt_max = self.strategy_desc.max_time_diff_sec
        if not self._interpolating and t0 + dt_max < t:
            self._interpolating = True
            self._time_interpolator = TimeInterpolator(t0, t)
    
    def _handle_time_difference(self, current_time: float, out_events: List[TimelineEvent]):
        end_wait_scale_factor = 0.2
        end_interpolation_scale_factor = 0.2
        # Rules. Note that their order of application differs from this enumeration.
        # Notation: 
        #   current_time (new update from the presenter) -> t
        #   end_wait_scale_factor -> s
        #   end_interpolation_scale_factor -> si
        #   self._timeline.get_current_time() -> t0
        #   self.strategy_desc.max_time_diff_sec -> dt_max
        #   self._timeline.get_end_time() -> end
        #
        # 0. Looping is on and close to the end. end - K < t0  =>  set time and pause
        #    See below for K.
        # 
        # 1. Suspend. t < t0 - dt_max  =>  ahead of the presenter, pause and wait
        # 
        # 2. Restart after suspend. is_suspended and t0 - s*dt_max < t  =>  play
        #   The role of scale factor s is to avoid alternating pause/play when the presenter
        #   is slow/lagging. Instead, we let the listener run for a bit, then pause for longer.
        #   Thus, "s" basically controls the length of wait and extrapolation periods when
        #   the presenter is lagging behind.
        #
        # 3.1. Slightly behind, do nothing. Not interpolating and t0 < t < t0 + dt_max  =>  ok
        # 3.2. Got close enough, stop interpolation. t < t0 + si
        # 
        # 4. Start interpolation (faster playback). t0 + dt_max < t  =>  increase playback speed.

        t = current_time
        dt_max = self.strategy_desc.max_time_diff_sec
        s = end_wait_scale_factor
        si = end_interpolation_scale_factor
        t0 = self._timeline.get_current_time()
        K = max(0.5, dt_max)
        end = self._timeline.get_end_time()

        # 0. Close to the end: set and pause
        if self._timeline.is_looping() and end - K < t0:
            self._is_suspended = True
            if t0 < t:
                out_events.append(TimelineEvent(
                    omni.timeline.TimelineEventType.CURRENT_TIME_TICKED,
                    {'currentTime': t},
                ))
            out_events.append(TimelineEvent(omni.timeline.TimelineEventType.PAUSE, {}))
            self._interpolating = False
            self._time_interpolator = TimeInterpolator()
            return

        # 1. time difference is too high, pause
        if not self._is_suspended and t < t0 - dt_max:
            out_events.append(TimelineEvent(omni.timeline.TimelineEventType.PAUSE, {}))
            self._is_suspended = True
            self._interpolating = False
            return
        # 2. end waiting
        elif self._is_suspended and t0 - s * dt_max < t:
            out_events.append(TimelineEvent(omni.timeline.TimelineEventType.PLAY, {}))
            self._is_suspended = False

        # 3.2
        if self._interpolating and t < t0 + si:
            self._interpolating = False
            return
        
        if self._interpolating:
            self._time_interpolator.target = t

        # 4. start interpolation
        self._start_interpolation(t0, t)
    
    def _process_diff_limited(self, events: List[TimelineEvent]) -> List[TimelineEvent]:
        out_events = []
        time_received = False
        for event in events:
            self._process_event_common(event, out_events)
            if event.type == int(omni.timeline.TimelineEventType.PLAY):
                out_events.append(TimelineEvent(omni.timeline.TimelineEventType.PLAY, {}))
            elif event.type == int(omni.timeline.TimelineEventType.PAUSE):
                out_events.append(event)
                if 'currentTime' in event.payload.keys():
                    out_events.append(TimelineEvent(
                        omni.timeline.TimelineEventType.CURRENT_TIME_TICKED,
                        {'currentTime' : event.payload['currentTime']}
                    ))
            elif event.type == int(omni.timeline.TimelineEventType.STOP):
                out_events.append(event)
            elif event.type == int(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED):
                time_received = True
                presenter_rewind = False
                # presenter's time restart because of looping
                if self._last_known_sim_time is not None and \
                    event.payload['currentTime'] < self._last_known_sim_time:
                    presenter_rewind = True
                is_previous_time_known = self._last_known_sim_time is not None
                self._last_known_sim_time = event.payload['currentTime']
                # not is_previous_time_known: avoid rule 1. of _handle_time_difference when
                #   the listener re-enabled sync. 
                #   in this case we should always jump to the new time
                if is_previous_time_known and not presenter_rewind and self._is_presenter_playing:
                    self._handle_time_difference(event.payload['currentTime'], out_events)
                else:
                    # just set the new time, restart playback if necessary
                    out_events.append(event)
                    self._interpolating = False
                    if self._is_presenter_playing:
                        out_events.append(TimelineEvent(omni.timeline.TimelineEventType.PLAY, {}))
                        self._is_suspended = False
                        # still apply rule 4. (interpolation). 
                        # this case happens when sync was re-enabled. this can be removed if we 
                        #   don't want interpolation when sync was re-enabled,
                        #   jumping instantly to the new time might be better.
                        self._start_interpolation(
                            self._timeline.get_current_time(),
                            self._last_known_sim_time
                        )
        
        # no new information, use the last known time
        if self._is_presenter_playing and not time_received and \
            self._last_known_sim_time is not None:
            self._handle_time_difference(self._last_known_sim_time, out_events)

        # interpolation
        if self._interpolating and self._time_interpolator is not None:
            # avoid being stuck when a different strategy was set during interpolation
            #   and it pauses the timeline
            if not self._timeline.is_playing():
                out_events.append(TimelineEvent(omni.timeline.TimelineEventType.PLAY, {}))
            t_interpolated = self._time_interpolator.get_interpolated(get_global_time_s())
            out_events.append(TimelineEvent(
                omni.timeline.TimelineEventType.CURRENT_TIME_TICKED,
                {'currentTime' : t_interpolated}
            ))

        return out_events