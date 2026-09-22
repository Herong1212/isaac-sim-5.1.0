# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#


import omni.timeline
from typing import Optional
from .singleton import singleton
from .annotation.utils import timecode_to_time, time_to_timecode


class Range:
    '''
    Range represents a time frame interval.
    '''
    def __init__(self, start: int, end: int) -> None:
        self._start = start
        self._end = end

    @property
    def start(self) -> int:
        return self._start

    @property
    def end(self) -> int:
        return self._end

    def apply_on_timeline(self, timeline: omni.timeline.Timeline):
        '''
        Sets the start and end time of a timeline object.
        '''
        timeline.set_start_time(timecode_to_time(self.start, timeline))
        timeline.set_end_time(timecode_to_time(self.end, timeline))


class ZoomState:
    '''
    ZoomState can be used to change the start and end times of the timeline in an undoable way.

    ZoomState does not react to changes of timelines' start and end times, instead, the desired normal (full) range
        needs to be set manually via normal_range.
    - Call "zoom" to set a new start and end time on a timeline which is always contained by the normal range.
    - Call "reset_zoom" to restore the normal range.
    '''
    def __init__(self, timeline_name: str):
        self._zoomed: bool = False
        self._normal_range: Range = Range(0, 0)
        self._zoom_range: Range = Range(0, 0)
        self._timeline: omni.timeline.Timeline = omni.timeline.get_timeline_interface(timeline_name)
        self._timeline_name: str = timeline_name

    @property
    def zoomed(self) -> bool:
        '''
        Returns True if we are zooming on the timeline.
        '''
        return self._zoomed

    @property
    def normal_range(self) -> Range:
        '''
        The timeline's "normal" (full) range, which can be restored with reset_zoom.
        '''
        return self._normal_range

    @normal_range.setter
    def normal_range(self, value: Range):
        self._normal_range = value

    @property
    def zoom_range(self) -> Range:
        '''
        Returns the last used zoom range.
        '''
        return self._zoom_range

    @property
    def timeline(self) -> omni.timeline.Timeline:
        '''
        The timeline object this object operates on.
        '''
        return self._timeline

    @property
    def timeline_name(self) -> str:
        '''
        The name of the timeline this object operates on.
        '''
        return self._timeline_name

    def zoom(self, range: Range):
        '''
        Sets timeline's start and end times to range. The new range is culled to the timeline's normal range.
        Args:
            - range (Range): the desired zoom range, i.e. start and end times in time frames.
        '''
        self._zoomed = True
        timeline_start = int(time_to_timecode(self._timeline.get_start_time(), self.timeline))
        timeline_end = int(time_to_timecode(self._timeline.get_end_time(), self.timeline))
        adjusted_range = Range(max(range.start, timeline_start), min(range.end, timeline_end))
        self._zoom_range = adjusted_range
        self._zoom_range.apply_on_timeline(self._timeline)

    def reset_zoom(self):
        '''
        Resets the timeline's zoom to its full range
        '''
        if self._zoomed:
            self._zoomed = False
            self._normal_range.apply_on_timeline(self._timeline)

    def clear_zoom(self):
        '''
        Clears the current zoom state (the "zoomed" flag)
        '''
        self._zoomed = False


@singleton
class ZoomHandler:
    '''
    ZoomHandler is a singleton that is used to access ZoomState objects.
    '''
    def __init__(self) -> None:
        self._zoom_data: dict = {}

    def get_zoom(self, timeline_name: Optional[str] = None) -> ZoomState:
        '''
        Returns the ZoomState of a timeline.
        Args:
            - timeline_name (str): optional name of the timeline. If no value is passed the default timeline is used.
        '''
        if timeline_name is None:
            timeline_name = ''

        state = self._zoom_data.get(timeline_name)
        if state is None:
            state = ZoomState(timeline_name)
            self._zoom_data[timeline_name] = state
        return state

    def __del__(self):
        self.destroy()

    def destroy(self):
        self._zoom_data = {}
