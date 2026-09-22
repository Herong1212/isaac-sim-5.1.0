from __future__ import annotations

import math
import re
from dataclasses import dataclass

SECONDS_PER_HOUR = 3600
SECONDS_PER_MINUTE = 60

# TODO: Drop frames
# For drop frame (29.97 or 59.94) we treat the fps as 30, or 60
# And then add 2 'drop frames' per minute except for minutes divisible by 10
# e.g. http://andrewduncan.net/timecodes/
DROP_FRAMES_PER_MINUTE = (60 * 30) - 2  # 1798
DROP_FRAMES_PER_10_MINUTES = (DROP_FRAMES_PER_MINUTE * 10) - 2  # 17978
DROP_FRAME_RATES = [29.97, 59.94]

# regular expression for smpte
smpte_pattern = re.compile(
    "^(?:(0?[0-9]|1[0-9]|2[0-3]):)?(?:(0?[0-9]|[0-5][0-9]):)(0?[0-9]|[0-5][0-9])(?:(\.|\;)([0-9]*))?$"
)
# test strings pass:
# .10
# 10.10
# 10:10.10
# 10:10:10.10


@dataclass
class SMPTE_Timecode:
    hours: int
    minutes: int
    seconds: int
    frames: int
    frames_fractional: float = None
    fps: float = 30

    def __str__(self) -> str:
        fractional_suffix = ""
        if self.frames_fractional:
            fractional_suffix = "*"

        return f"{self.hours:02.0f}:{self.minutes:02.0f}:{self.seconds:02.0f}.{self.frames:02.0f}{fractional_suffix}"

    @property
    def drop(self) -> bool:
        return self.fps in DROP_FRAME_RATES

    @property
    def as_frames(self) -> float:
        hour_frames = self.hours * 60 * 60 * self.fps
        minute_frames = self.minutes * 60 * self.fps
        seconds_frames = self.seconds * self.fps
        return hour_frames + minute_frames + seconds_frames + self.frames

    @property
    def as_seconds(self) -> float:
        hour_seconds = self.hours * 60 * 60
        minute_seconds = self.minutes * 60
        frame_seconds = self.frames / self.fps
        return hour_seconds + minute_seconds + self.seconds + frame_seconds

    @staticmethod
    def from_frames(frames: float, fps: float) -> SMPTE_Timecode:
        """
        Convert USD timecode value (float) to SMPTE timecode (dataclass).
        Returns math.nan if timecodes_per_second is zero
        """
        if fps == 0.0:
            return math.nan
        hours = int(frames / (SECONDS_PER_HOUR * fps))
        minutes = int(frames / (SECONDS_PER_MINUTE * fps) % SECONDS_PER_MINUTE)
        seconds = int(frames / fps % SECONDS_PER_MINUTE)
        frames_float = frames % fps
        frames_fractional, frames_int = math.modf(frames_float)
        return SMPTE_Timecode(hours, minutes, seconds, frames_int, frames_fractional, fps)

    @staticmethod
    def from_seconds(seconds: float, fps: float):
        if not fps:
            raise ValueError("FPS cannot be zero.")
        hours = int(seconds / (SECONDS_PER_HOUR))
        minutes = int(seconds / (SECONDS_PER_MINUTE) % SECONDS_PER_MINUTE)
        int_seconds = int(seconds)
        frames_float = (seconds - int_seconds) % fps
        frames_fractional, frames_int = math.modf(frames_float)
        return SMPTE_Timecode(hours, minutes, int_seconds, frames_int, frames_fractional, fps)

    @staticmethod
    def from_string(input: str, fps: str):
        match = re.match(smpte_pattern, input)
        if not match:
            return None
        hours_str, minutes_str, seconds_str, frame_separator, frames_str = match.groups()
        hours, minutes, seconds, frames = 0, 0, 0, 0
        if hours_str:
            hours = int(hours_str)
        if minutes_str:
            minutes = int(minutes_str)
        if seconds_str:
            seconds = int(seconds_str)
        if frames_str:
            frames = int(frames_str)
        return SMPTE_Timecode(hours=hours, minutes=minutes, seconds=seconds, frames=frames, fps=fps)
