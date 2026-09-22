from enum import Enum
from dataclasses import dataclass
import math
import sys
from pxr import Usd

try:
    import omni.anim.curve.core as anim_curve
except ImportError:
    anim_curve = None


class AnimSection(Enum):
    SOURCE_BODY = 0
    PRE_INFINITY = -1
    POST_INFINITY = 1


@dataclass
class SourceTime:
    """Represents time in source animation.
    time: Timecode value in the source animation.
    infinity: Represents section of the source animation we exist: body (0), pre-infinity(-1), or post-infinity.(1)
    epsilon: If source time is within 1 timecodes of infinity section borders, this value will be set to the distance.
    """

    time: float
    infinity: AnimSection
    epsilon: float = 0


def get_anim_data_range(prim):
    startTime = sys.float_info.max
    endTime = -sys.float_info.max

    if anim_curve is not None:
        curves = anim_curve.get_curve_plugin().get_curves(str(prim.GetPath()))
        for curve in curves.values():
            if not curve.keys:
                continue

            start = (
                prim.GetStage().GetTimeCodesPerSecond()
                * curve.keys[0].time
                / anim_curve.get_curve_plugin().get_ticks_per_second()
            )
            end = (
                prim.GetStage().GetTimeCodesPerSecond()
                * curve.keys[-1].time
                / anim_curve.get_curve_plugin().get_ticks_per_second()
            )

            if start < startTime:
                startTime = start
            if end > endTime:
                endTime = end
    if startTime <= endTime:
        return (startTime, endTime)
    else:
        return None


def offset_from_play_offset(play_offset: float, play_start: float, play_end: float) -> float:
    # Play offset must be between play start and play end, otherwise it is ignored.
    if play_offset and not math.isnan(play_offset):
        if play_offset < play_start or play_offset > play_end:
            return 0
        else:
            # Play offset is set as an absolute time value
            # Calculate offset as delta
            return -(play_offset - play_start)
    # no play offset, offset is 0
    return 0


def get_source_time_from_parent_time(
    parent_time: Usd.TimeCode,
    start_time: float,
    play_rate: float,
    play_start: float,
    play_end: float,
    play_offset: float = 0,
    looping=False,
) -> SourceTime:
    # Play offset must be between play start and play end, otherwise it is ignored.
    offset = offset_from_play_offset(play_offset, play_start, play_end)

    # get overall clipped length of play range
    clipped_length = play_end - play_start
    # get the relative time within the clip
    time_in_clip_time_frame = parent_time - start_time
    # get the media source time from the clip time before clipping (trim/loop)
    relative_time_in_source_time_frame = play_start + (time_in_clip_time_frame * play_rate) - offset

    # consider looping and holding
    time_in_source_time_frame = relative_time_in_source_time_frame
    section = AnimSection.SOURCE_BODY

    if relative_time_in_source_time_frame > play_end:
        section = AnimSection.POST_INFINITY

        if looping:
            # we are in post-infinity loop space
            loop_fractional = float(relative_time_in_source_time_frame) % float(clipped_length)
            time_in_source_time_frame = play_start + (loop_fractional / play_rate)
        else:
            # we are in post-infinity hold
            time_in_source_time_frame = play_start + clipped_length
    elif relative_time_in_source_time_frame < play_start:
        section = AnimSection.PRE_INFINITY

        if looping:
            loop_fractional = relative_time_in_source_time_frame % clipped_length
            time_in_source_time_frame = play_start - (loop_fractional / play_rate)
        else:
            time_in_source_time_frame = play_start - clipped_length

    epsilon = 0
    distance_to_preinfinity = abs(relative_time_in_source_time_frame - play_start)
    distance_to_postinfinity = abs(relative_time_in_source_time_frame - play_end)
    closest_infinity = min(distance_to_preinfinity, distance_to_postinfinity)
    if closest_infinity < 1:
        epsilon = closest_infinity

    return SourceTime(time_in_source_time_frame, section, epsilon=epsilon)


def is_curve_node(prim: Usd.Prim) -> bool:
    if prim.GetTypeName() != "OmniGraphNode":
        return False

    return prim.GetAttribute("node:type").Get() == "omni.anim.curve.core.AnimCurve"
