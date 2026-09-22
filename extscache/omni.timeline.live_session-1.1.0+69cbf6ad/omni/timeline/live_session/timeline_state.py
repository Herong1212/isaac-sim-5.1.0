import enum
import omni.timeline
from typing import List, Union


# Consider moving these to the omni.timeline API


class PlayState(enum.Enum):
    PLAYING = 0
    PAUSED = 1
    STOPPED = 2


def get_timeline_state(timeline) -> PlayState:
    if timeline is None:
        return None
    if timeline.is_playing():
        return PlayState.PLAYING
    elif timeline.is_stopped():
        return PlayState.STOPPED
    return PlayState.PAUSED


def get_timeline_next_state(
    current_state: PlayState,
    event: Union[int, omni.timeline.TimelineEventType]
) -> PlayState:
    if isinstance(event, omni.timeline.TimelineEventType):
        event = int(event)

    if current_state == PlayState.PLAYING:
        if event == int(omni.timeline.TimelineEventType.STOP):
            return PlayState.STOPPED
        elif event == int(omni.timeline.TimelineEventType.PAUSE):
            return PlayState.PAUSED
        else:
            return current_state
    elif current_state == PlayState.PAUSED:
        if event == int(omni.timeline.TimelineEventType.STOP):
            return PlayState.STOPPED
        elif event == int(omni.timeline.TimelineEventType.PLAY):
            return PlayState.PLAYING
        else:
            return current_state
    elif current_state == PlayState.STOPPED:
        if event == int(omni.timeline.TimelineEventType.PLAY):
            return PlayState.PLAYING
        else:
            return current_state
    # Should not be called
    return current_state


def get_timeline_next_events(
    current_state: PlayState,
    next_state: PlayState
) -> List[omni.timeline.TimelineEventType]:
    if current_state == PlayState.PLAYING:
        if next_state == PlayState.PAUSED:
            return [omni.timeline.TimelineEventType.PAUSE]
        elif next_state == PlayState.STOPPED:
            return [omni.timeline.TimelineEventType.STOP]
    elif current_state == PlayState.PAUSED:
        if next_state == PlayState.PLAYING:
            return [omni.timeline.TimelineEventType.PLAY]
        elif next_state == PlayState.STOPPED:
            return [omni.timeline.TimelineEventType.STOP]
    elif current_state == PlayState.STOPPED:
        if next_state == PlayState.PLAYING:
            return [omni.timeline.TimelineEventType.PLAY]
        elif next_state == PlayState.PAUSED:
            return [omni.timeline.TimelineEventType.PLAY, omni.timeline.TimelineEventType.PAUSE]
    return []


class TimelineState:
    """
    All information that is required to cache timeline state.
    Usually it is better to cache the state instead of using the timeline itself
        because the timeline postpones state changes by one frame and we have no information
        about its state change queue.
    """
    def __init__(self, timeline = None):
        state = PlayState.STOPPED
        time = 0
        looping = True
        zoom_range = [0, 0]

        if timeline is not None:
            state = get_timeline_state(timeline)
            time = timeline.get_current_time()
            looping = timeline.is_looping()
            zoom_range = [timeline.get_zoom_start_time(), timeline.get_zoom_end_time()]

        self._state: PlayState = state
        self._current_time: float = time
        self._looping: bool = looping
        self._zoom_range = zoom_range

    @property
    def state(self) -> PlayState:
        return self._state

    @state.setter
    def state(self, state: PlayState):
        self._state = state

    @property
    def current_time(self) -> float:
        return self._current_time

    @current_time.setter
    def current_time(self, time: float):
        self._current_time = time

    @property
    def looping(self) -> bool:
        return self._looping

    @looping.setter
    def looping(self, value: bool):
        self._looping = value

    @property
    def zoom_range(self):
        return self._zoom_range

    def set_zoom_range(self, start_time: float, end_time: float):
        self._zoom_range = [start_time, end_time]
