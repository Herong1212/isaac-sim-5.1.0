from __future__ import annotations
import omni.timeline._timeline
import typing
import carb.events._events

__all__ = [
    "ITimeline",
    "Timeline",
    "TimelineEventType",
    "acquire_timeline_interface",
    "release_timeline_interface"
]


class ITimeline():
    """
    Factory class for creating :class:`Timeline` instances.

    Timeline control, setter and getter methods are all deprecated and forwarded to the default :class:`Timeline`.
    These must be accessed through a :class:`Timeline` instance:

    .. highlight:: python
    .. code-block:: python

        import omni.timeline
        timeline = omni.timeline.get_timeline_interface()
        timeline.play()
    """
    def clear_tentative_time(self) -> None: 
        """
        Clear tentative time of animation in seconds.

        Clear/Invalidate the tentative time
        """
    def destroy_timeline(self, name: str) -> bool: 
        """
        Destroys the timeline with the given name if nothing references it. Does not release the default timeline.

        Args:
            name of the timeline.

        Returns:
            True if a timeline was deleted, False otherwise. The latter happens when the timeline does not exist, it is in use, or it is the default timeline.
        """
    def forward_one_frame(self) -> None: 
        """
        Forwards the timeline by one frame.
        """
    def get_current_tick(self) -> int: 
        """
        Gets the current tick index, starting from zero. Always returns zero when ticks per frame is one.

        Returns:
             The current tick index.
        """
    def get_current_time(self) -> float: 
        """
        Gets current time of animation in seconds.

        Returns:
            Current time of animation in seconds.
        """
    def get_end_time(self) -> float: 
        """
        Gets the end time of animation in seconds.

        Returns:
            End time of animation in seconds.
        """
    def get_fast_mode(self) -> bool: 
        """
        Checks if fast mode is on or off.

        Returns:
            true is fast mode is on.
        """
    def get_start_time(self) -> float: 
        """
        Gets the start time of animation in seconds.

        Returns:
            Start time of animation in seconds.
        """
    def get_target_framerate(self) -> float: 
        """
        Gets the target frame rate, which affects the derived FPS of the runloop in play mode.
        Exact runloop FPS is usually not the same as this value, as it is always a multiple of get_time_codes_per_seconds.

        Returns:
            The target frame rate.
        """
    def get_tentative_time(self) -> float: 
        """
        Gets tentative time of animation in seconds.

        Returns:
            Tentative time of animation if it is valid, otherwise return current time
        """
    def get_ticks_per_frame(self) -> int: 
        """
        Gets the tick count per frame, i.e. how many times update event is ticked per frame.

        Returns:
            The tick per frame count.
        """
    def get_ticks_per_second(self) -> float: 
        """
        Gets the tick count per seconds, i.e. how many times update event is ticked per second.

        Returns:
            The tick per second count.
        """
    def get_time_codes_per_second(self) -> float: 
        """
        Gets timeCodePerSecond metadata from currently opened stage.
        This is equivalent to calling GetTimeCodesPerSecond on UsdStage.

        Returns:
            timeCodePerSecond for current UsdStage.
        """
    def get_time_codes_per_seconds(self) -> float: 
        """
        Gets timeCodePerSecond metadata from currently opened stage.
        This is equivalent to calling GetTimeCodesPerSecond on UsdStage.

        This function is same as get_time_codes_per_second but incorrectly named. Kept for backwards compatibility.

        Returns:
            timeCodePerSecond for current UsdStage.
        """
    def get_timeline(self, name: str = '') -> Timeline: 
        """
        Returns the timeline with the given name or creates a new if it does not exist.

        Args:
            name: The name of the timeline.

        Returns:
            Timeline object.
        """
    def get_timeline_event_stream(self) -> carb.events._events.IEventStream: 
        """
        Gets TimelineEventStream, emitting TimelineEventType.

        Returns:
            TimelineEventStream.
        """
    def is_auto_updating(self) -> bool: 
        """
        Checks if timeline is auto updating.

        Returns:
            True if timeline is auto updating. False otherwise.
        """
    def is_looping(self) -> bool: 
        """
        Checks if animation is looping.

        Returns:
            True if animation is looping. False otherwise.
        """
    def is_playing(self) -> bool: 
        """
        Checks if animation is playing.

        Returns:
            True if animation is playing. False otherwise.
        """
    def is_prerolling(self) -> bool: 
        """
        Checks if timeline is prerolling.

        Returns:
            True if timeline is prerolling. False otherwise.
        """
    def is_stopped(self) -> bool: 
        """
        Checks if animation is stopped, as opposed to paused.

        Returns:
            True if animation is stopped. False otherwise.
        """
    def pause(self) -> None: 
        """
        Pauses animation.
        """
    def play(self, start_timecode: float = 0, end_timecode: float = 0, looping: bool = True) -> None: 
        """
        Plays animation with current timeCodePerSecond. If not set session start and end timecode, will play from
        global start time to end time in stage.

        Args:
            start_timecode: start timecode of session play, won't change the global StartTime.
            end_timecode: start timecode of session play, won't change the global EndTime.
            looping: true to enable session play looping, false to disable, won't change the global Looping.
        """
    def rewind_one_frame(self) -> None: 
        """
        Rewinds the timeline by one frame.
        """
    def set_auto_update(self, auto_update: bool) -> None: 
        """
        Turns on/off auto update.

        Args:
            auto_update: True to enable auto update, False to disable.
        """
    def set_current_time(self, time_in_seconds: float) -> None: 
        """
        Sets current time of animation in seconds.

        Args:
            time_in_seconds Current time of animation in seconds.
        """
    def set_end_time(self, end_time: float) -> None: 
        """
        Sets the end time of animation in seconds. This will write into current opened stage.

        Args:
            end_time: End time of animation in seconds.
        """
    def set_fast_mode(self, fast_mode: bool) -> None: 
        """
        Turns fast mode on or off.

        Args:
            fast_mode true to turn on fast mode, false to turn it off.
        """
    def set_looping(self, looping: bool) -> None: 
        """
        Sets animation looping mode.

        Args:
            looping: True to enable looping, False to disable.
        """
    def set_prerolling(self, preroll: bool) -> None: 
        """
        Turns on/off preroll status.

        Args:
            preroll: True to enable preroll, False to disable.
        """
    def set_start_time(self, start_time: float) -> None: 
        """
        Sets the begin time of animation in seconds. This will write into current opened stage.

        Args:
            start_time: Begin time of animation in seconds.
        """
    def set_target_framerate(self, target_framerate: float) -> None: 
        """
        Sets the target frame rate, which affects the derived FPS of the runloop in play mode.
        Exact runloop FPS is usually not the same as this value, as it is always a multiple of get_time_codes_per_seconds.

        Args:
            target_framerate The target frame rate.
        """
    def set_tentative_time(self, time_in_seconds: float) -> None: 
        """
        Sets tentative time of animation in seconds.

        Args:
            time_in_seconds Tentative time of animation in seconds.
        """
    def set_ticks_per_frame(self, ticks_per_frame: int) -> None: 
        """
        Sets the tick count per frame, i.e. how many times update event is ticked per frame.

        Args:
            ticks_per_frame: The tick per frame count.
        """
    def set_time_codes_per_second(self, time_codes_per_second: float) -> None: 
        """
        Sets timeCodePerSecond metadata to currently opened stage.
        This is equivalent to calling SetTimeCodesPerSecond on UsdStage.

        Args:
            time_codes_per_second: TimeCodePerSecond to set into current stage.
        """
    def stop(self) -> None: 
        """
        Stops animation.
        """
    pass
class Timeline():
    """
    Defines a timeline controller.
    """
    def clear_tentative_time(self) -> None: 
        """
        Clear tentative time of animation in seconds.

        Clear/Invalidate the tentative time
        """
    def clear_zoom(self) -> None: 
        """
        Clears the zoom state, i.e. sets the zoom range to [get_start_time(), get_end_time()].
        """
    def commit(self) -> None: 
        """
        Applies all pending state changes and invokes all callbacks.

        This method is not thread-safe, it should be called only from the main thread.
        """
    def commit_silently(self) -> None: 
        """
        Applies all pending state changes but does not invoke any callbacks.

        This method is thread-safe.
        """
    def forward_one_frame(self) -> None: 
        """
        Forwards the timeline by one frame.
        """
    def get_current_tick(self) -> int: 
        """
        Gets the current tick index, starting from zero. Always returns zero when ticks per frame is one.

        Returns:
             The current tick index.
        """
    def get_current_time(self) -> float: 
        """
        Gets current time of animation in seconds.

        Returns:
            Current time of animation in seconds.
        """
    def get_director(self) -> Timeline: 
        """
        Returns the current director Timeline.

        Returns:
             The director timeline object or None if none is set.
        """
    def get_end_time(self) -> float: 
        """
        Gets the end time of animation in seconds.

        End time means no frames can start strictly after this time point.
        When start and end time define an integer number of frames, end time is the end of the last animation frame.

        Returns:
            End time of animation in seconds.
        """
    def get_fast_mode(self) -> bool: 
        """
        Checks if fast mode is on or off. Deprecated, same as get_play_every_frame.

        Returns:
            true is fast mode is on.
        """
    def get_play_every_frame(self) -> bool: 
        """
        Checks if the timeline sends updates every frame. Same as get_fast_mode.

        Returns:
            true if the timeline does not skip frames.
        """
    def get_start_time(self) -> float: 
        """
        Gets the start time of animation in seconds.

        Start time is defined as the beginning of the first frame.

        Returns:
            Start time of animation in seconds.
        """
    def get_target_framerate(self) -> float: 
        """
        Gets the target frame rate, which affects the derived FPS of the runloop in play mode.
        Exact runloop FPS is usually not the same as this value, as it is always a multiple of get_time_codes_per_seconds.

        Returns:
            The target frame rate.
        """
    def get_tentative_time(self) -> float: 
        """
        Gets tentative time of animation in seconds.

        Returns:
            Tentative time of animation if it is valid, otherwise return current time
        """
    def get_ticks_per_frame(self) -> int: 
        """
        Gets the tick count per frame, i.e. how many times update event is ticked per frame.

        Returns:
            The tick per frame count.
        """
    def get_ticks_per_second(self) -> float: 
        """
        Gets the tick count per seconds, i.e. how many times update event is ticked per second.

        Returns:
            The tick per second count.
        """
    def get_time_codes_per_second(self) -> float: 
        """
        Gets timeCodePerSecond metadata from currently opened stage.
        This is equivalent to calling GetTimeCodesPerSecond on UsdStage.

        Returns:
            timeCodePerSecond for current UsdStage.
        """
    def get_time_codes_per_seconds(self) -> float: 
        """
        Gets timeCodePerSecond metadata from currently opened stage.
        This is equivalent to calling GetTimeCodesPerSecond on UsdStage.

        This function is same as get_time_codes_per_second but incorrectly named. Kept for backwards compatibility.

        Returns:
            timeCodePerSecond for current UsdStage.
        """
    def get_timeline_event_stream(self) -> carb.events._events.IEventStream: 
        """
        Gets TimelineEventStream, emitting TimelineEventType.

        Returns:
            TimelineEventStream.
        """
    def get_zoom_end_time(self) -> float: 
        """
        Gets the end time of zoomed animation in seconds.

        Returns:
            End time of zoomed animation in seconds. When no zoom is set, this function returns get_end_time().
        """
    def get_zoom_start_time(self) -> float: 
        """
        Gets the start time of zoomed animation in seconds.

        Returns:
            Start time of zoomed animation in seconds. When no zoom is set, this function returns get_start_time().
        """
    def is_auto_updating(self) -> bool: 
        """
        Checks if timeline is auto updating.

        Returns:
            True if timeline is auto updating. False otherwise.
        """
    def is_looping(self) -> bool: 
        """
        Checks if animation is looping.

        Returns:
            True if animation is looping. False otherwise.
        """
    def is_playing(self) -> bool: 
        """
        Checks if animation is playing.

        Returns:
            True if animation is playing. False otherwise.
        """
    def is_prerolling(self) -> bool: 
        """
        Checks if timeline is prerolling.

        Returns:
            True if timeline is prerolling. False otherwise.
        """
    def is_stopped(self) -> bool: 
        """
        Checks if animation is stopped, as opposed to paused.

        Returns:
            True if animation is stopped. False otherwise.
        """
    def is_zoomed(self) -> bool: 
        """
        Returns whether a zoom is set, i.e. whether the zoom range is not the entire
            [getStartTime(), getEndTime()] interval.

        Returns:
            True if get_start_time() < get_zoom_start_time() or get_zoom_end_time() < get_end_time() (note that "<=" always holds).
            False otherwise.
        """
    def pause(self) -> None: 
        """
        Pauses animation.
        """
    def play(self, start_timecode: float = 0, end_timecode: float = 0, looping: bool = True) -> None: 
        """
        Plays animation with current timeCodePerSecond. if not set session start and end timecode, will play from
        global start time to end time in stage.

        Args:
            start_timecode: start timecode of session play, won't change the global StartTime.
            end_timecode: start timecode of session play, won't change the global EndTime.
            looping: true to enable session play looping, false to disable, won't change the global Looping.
        """
    def rewind_one_frame(self) -> None: 
        """
        Rewinds the timeline by one frame.
        """
    def set_auto_update(self, auto_update: bool) -> None: 
        """
        Turns on/off auto update.

        Args:
            auto_update: True to enable auto update, False to disable.
        """
    def set_current_time(self, time_in_seconds: float) -> None: 
        """
        Sets current time of animation in seconds.

        Args:
            time_in_seconds Current time of animation in seconds.
        """
    def set_director(self, timeline: Timeline) -> None: 
        """
        Sets a director Timeline.

        When a director is set, the timeline mimics its behavior and any
            state changing call from all other sources are ignored.

        Args:
             timeline: The timeline object to be set as the director.
                      Pass None to clear the current director.
        """
    def set_end_time(self, end_time: float) -> None: 
        """
        Sets the end time of animation in seconds. This will write into current opened stage.

        The call enforces the time interval defined by start and end times to be at least one frame long.

        Args:
            end_time: End time of animation in seconds.
        """
    def set_fast_mode(self, fast_mode: bool) -> None: 
        """
        Turns fast mode on or off. Deprecated, same as set_play_every_frame.

        Args:
            fast_mode true to turn on fast mode, false to turn it off.
        """
    def set_looping(self, looping: bool) -> None: 
        """
        Sets animation looping mode.

        Args:
            looping: True to enable looping, False to disable.
        """
    def set_play_every_frame(self, play_every_frame: bool) -> None: 
        """
        Turns frame skipping off (true) or on (false). Same as set_fast_mode.

        Args:
            play_every_frame true to turn frame skipping off.
        """
    def set_prerolling(self, preroll: bool) -> None: 
        """
        Turns on/off preroll status.

        Args:
            preroll: True to enable preroll, False to disable.
        """
    def set_start_time(self, start_time: float) -> None: 
        """
        Sets the begin time of animation in seconds. This will write into current opened stage.

        The call enforces the time interval defined by start and end times to be at least one frame long.

        Args:
            start_time: Begin time of animation in seconds.
        """
    def set_target_framerate(self, target_framerate: float) -> None: 
        """
        Sets the target frame rate, which affects the derived FPS of the runloop in play mode.
        Exact runloop FPS is usually not the same as this value, as it is always a multiple of get_time_codes_per_seconds.

        Args:
            target_framerate The target frame rate.
        """
    def set_tentative_time(self, time_in_seconds: float) -> None: 
        """
        Sets tentative time of animation in seconds.

        Args:
            time_in_seconds Tentative time of animation in seconds.
        """
    def set_ticks_per_frame(self, ticks_per_frame: int) -> None: 
        """
        Sets the tick count per frame, i.e. how many times update event is ticked per frame.

        Args:
            ticks_per_frame: The tick per frame count.
        """
    def set_time_codes_per_second(self, time_codes_per_second: float) -> None: 
        """
        Sets timeCodePerSecond metadata to currently opened stage.
        This is equivalent to calling SetTimeCodesPerSecond on UsdStage.

        Args:
            time_codes_per_second: TimeCodePerSecond to set into current stage.
        """
    def set_zoom_range(self, start_time: float, end_time: float) -> None: 
        """
        Sets the zoom range, i.e. the playback interval.
        Values are truncated to the [get_start_time(), get_end_time()] interval, which is also the default range.
        A minimum of one frame long range is enforced.

        Args:
            start_time: Start time of zoom in seconds. Must be less or equal than end_time.
            end_time: End time of zoom in seconds. Must be greater or equal than start_time.
        """
    def stop(self) -> None: 
        """
        Stops animation.
        """
    def time_code_to_time(self, arg0: float) -> float: 
        """
        Converts time codes to seconds, w.r.t. the current timeCodesPerSecond setting of the timeline.

        Returns:
             The converted time code.
        """
    def time_to_time_code(self, arg0: float) -> float: 
        """
        Converts time in seconds to time codes, w.r.t. the current timeCodesPerSecond setting of the timeline.

        Returns:
             The converted time code.
        """
    pass
class TimelineEventType():
    """
            Timeline event types to be used by TimelineEventStream.
            

    Members:

      PLAY

      PAUSE

      STOP

      CURRENT_TIME_CHANGED

      CURRENT_TIME_TICKED_PERMANENT

      CURRENT_TIME_TICKED

      LOOP_MODE_CHANGED

      START_TIME_CHANGED

      END_TIME_CHANGED

      TIME_CODE_PER_SECOND_CHANGED

      AUTO_UPDATE_CHANGED

      PREROLLING_CHANGED

      TENTATIVE_TIME_CHANGED

      TICKS_PER_FRAME_CHANGED

      FAST_MODE_CHANGED

      PLAY_EVERY_FRAME_CHANGED

      TARGET_FRAMERATE_CHANGED

      DIRECTOR_CHANGED

      ZOOM_CHANGED
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    AUTO_UPDATE_CHANGED: omni.timeline._timeline.TimelineEventType # value = <TimelineEventType.AUTO_UPDATE_CHANGED: 10>
    CURRENT_TIME_CHANGED: omni.timeline._timeline.TimelineEventType # value = <TimelineEventType.CURRENT_TIME_CHANGED: 3>
    CURRENT_TIME_TICKED: omni.timeline._timeline.TimelineEventType # value = <TimelineEventType.CURRENT_TIME_TICKED: 5>
    CURRENT_TIME_TICKED_PERMANENT: omni.timeline._timeline.TimelineEventType # value = <TimelineEventType.CURRENT_TIME_TICKED_PERMANENT: 4>
    DIRECTOR_CHANGED: omni.timeline._timeline.TimelineEventType # value = <TimelineEventType.DIRECTOR_CHANGED: 16>
    END_TIME_CHANGED: omni.timeline._timeline.TimelineEventType # value = <TimelineEventType.END_TIME_CHANGED: 8>
    FAST_MODE_CHANGED: omni.timeline._timeline.TimelineEventType # value = <TimelineEventType.FAST_MODE_CHANGED: 14>
    LOOP_MODE_CHANGED: omni.timeline._timeline.TimelineEventType # value = <TimelineEventType.LOOP_MODE_CHANGED: 6>
    PAUSE: omni.timeline._timeline.TimelineEventType # value = <TimelineEventType.PAUSE: 1>
    PLAY: omni.timeline._timeline.TimelineEventType # value = <TimelineEventType.PLAY: 0>
    PLAY_EVERY_FRAME_CHANGED: omni.timeline._timeline.TimelineEventType # value = <TimelineEventType.FAST_MODE_CHANGED: 14>
    PREROLLING_CHANGED: omni.timeline._timeline.TimelineEventType # value = <TimelineEventType.PREROLLING_CHANGED: 11>
    START_TIME_CHANGED: omni.timeline._timeline.TimelineEventType # value = <TimelineEventType.START_TIME_CHANGED: 7>
    STOP: omni.timeline._timeline.TimelineEventType # value = <TimelineEventType.STOP: 2>
    TARGET_FRAMERATE_CHANGED: omni.timeline._timeline.TimelineEventType # value = <TimelineEventType.TARGET_FRAMERATE_CHANGED: 15>
    TENTATIVE_TIME_CHANGED: omni.timeline._timeline.TimelineEventType # value = <TimelineEventType.TENTATIVE_TIME_CHANGED: 12>
    TICKS_PER_FRAME_CHANGED: omni.timeline._timeline.TimelineEventType # value = <TimelineEventType.TICKS_PER_FRAME_CHANGED: 13>
    TIME_CODE_PER_SECOND_CHANGED: omni.timeline._timeline.TimelineEventType # value = <TimelineEventType.TIME_CODE_PER_SECOND_CHANGED: 9>
    ZOOM_CHANGED: omni.timeline._timeline.TimelineEventType # value = <TimelineEventType.ZOOM_CHANGED: 17>
    __members__: dict # value = {'PLAY': <TimelineEventType.PLAY: 0>, 'PAUSE': <TimelineEventType.PAUSE: 1>, 'STOP': <TimelineEventType.STOP: 2>, 'CURRENT_TIME_CHANGED': <TimelineEventType.CURRENT_TIME_CHANGED: 3>, 'CURRENT_TIME_TICKED_PERMANENT': <TimelineEventType.CURRENT_TIME_TICKED_PERMANENT: 4>, 'CURRENT_TIME_TICKED': <TimelineEventType.CURRENT_TIME_TICKED: 5>, 'LOOP_MODE_CHANGED': <TimelineEventType.LOOP_MODE_CHANGED: 6>, 'START_TIME_CHANGED': <TimelineEventType.START_TIME_CHANGED: 7>, 'END_TIME_CHANGED': <TimelineEventType.END_TIME_CHANGED: 8>, 'TIME_CODE_PER_SECOND_CHANGED': <TimelineEventType.TIME_CODE_PER_SECOND_CHANGED: 9>, 'AUTO_UPDATE_CHANGED': <TimelineEventType.AUTO_UPDATE_CHANGED: 10>, 'PREROLLING_CHANGED': <TimelineEventType.PREROLLING_CHANGED: 11>, 'TENTATIVE_TIME_CHANGED': <TimelineEventType.TENTATIVE_TIME_CHANGED: 12>, 'TICKS_PER_FRAME_CHANGED': <TimelineEventType.TICKS_PER_FRAME_CHANGED: 13>, 'FAST_MODE_CHANGED': <TimelineEventType.FAST_MODE_CHANGED: 14>, 'PLAY_EVERY_FRAME_CHANGED': <TimelineEventType.FAST_MODE_CHANGED: 14>, 'TARGET_FRAMERATE_CHANGED': <TimelineEventType.TARGET_FRAMERATE_CHANGED: 15>, 'DIRECTOR_CHANGED': <TimelineEventType.DIRECTOR_CHANGED: 16>, 'ZOOM_CHANGED': <TimelineEventType.ZOOM_CHANGED: 17>}
    pass
def acquire_timeline_interface(plugin_name: str = None, library_path: str = None) -> ITimeline:
    pass
def release_timeline_interface(arg0: ITimeline) -> None:
    pass
