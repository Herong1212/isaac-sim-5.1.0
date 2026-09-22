import asyncio
from functools import partial

from omni import ui
from omni.anim.widget.timeline import (
    RangeModel,
    StageRangeModel,
    TimelineContentDelegate,
    TimelineGridModel,
    TimelineView,
    TimelineViewDelegate,
    TimeUnits,
)
from omni.kit.preferences.animation import TimeDisplay

_window_kwargs = {"width": 600, "height": 100}
TRACK_HEIGHT = 32
TRACKS = {
    "Track1": {"Clip1": (0, 100), "Clip2": (100, 200)},
    "Track2": {"Clip3": (50, 150)},
    "Track3": {"Clip4": (150, 300)},
}
KEYS = [0, 50, 100, 150, 200, 300]
STYLE = {
    "KeyframeTriangle": {"background_color": 0xFFFFAA00, "border_color": 0xFFEE9900},
    "KeyframeTriangle:hovered": {"background_color": 0xFFFFAAFF, "border_color": 0xFFFFFFFF},
    "KeyframeTriangle:selected": {"background_color": 0xFFFFAAFF, "border_color": 0xFFFFFFFF},
    "KeyframeTriangle:pressed": {"background_color": 0xFFFFAAFF, "border_color": 0xFFFFFFFF},
    "ClipRectangle": {"background_color": 0xFFFFAA00, "border_color": 0xFFEE9900, "border_radius": 4},
    "ClipRectangle:hovered": {"background_color": 0xFFFFAAFF, "border_color": 0xFFFFFFFF, "border_radius": 4},
    "ClipRectangle:selected": {"background_color": 0xFFFFAAFF, "border_color": 0xFFFFFFFF, "border_radius": 4},
    "ClipRectangle:pressed": {"background_color": 0xFFFFAAFF, "border_color": 0xFFFFFFFF, "border_radius": 4},
}


class GutterDelegate(TimelineContentDelegate):
    def _build_background(self):
        pass

    def _build_grid(self):
        pass

    def _build_key(self):
        ui.Triangle(
            width=4,
            style=STYLE,
            style_type_name_override="KeyframeTriangle",
            alignment=ui.Alignment.CENTER_BOTTOM,
        )

    def _build_content(self):
        width_offset = self._timeline_grid_model.frame_width / 2
        with ui.ZStack():
            for key_time in KEYS:
                offset_x = self._timeline_grid_model.transform_timeline_to_position(key_time) - width_offset
                with ui.Placer(offset_x=offset_x):
                    self._build_key()

    def _update_content(self):
        self._content_frame.rebuild()


class ContentDelegate(TimelineContentDelegate):
    def __init__(self):
        self._clip_placers = {}
        super().__init__()

    def destroy(self):
        self._clip_placers = {}
        return super().destroy()

    def _build_clip(self, clip_name: str, clip_data: tuple):
        with ui.ZStack():
            ui.Rectangle(style_type_name_override="ClipRectangle", style=STYLE)
            ui.Label(clip_name)

    def _build_track(self, track_name: str, track_data: dict):
        with ui.ZStack():
            for clip_name, clip_data in track_data.items():
                clip_offset_x = self._timeline_grid_model.transform_timeline_to_position(clip_data[0])
                clip_length = clip_data[1] - clip_data[0]
                clip_width = clip_length * self._timeline_grid_model.frame_width
                clip = ui.Placer(offset_x=clip_offset_x, width=clip_width)
                self._clip_placers[clip_name] = clip
                with clip:
                    ui.Frame(build_fn=partial(self._build_clip, clip_name=clip_name, clip_data=clip_data))

    def _build_content(self):
        with ui.VStack(spacing=2):
            for track_name, track_data in TRACKS.items():
                ui.Frame(
                    build_fn=partial(self._build_track, track_name=track_name, track_data=track_data),
                    height=TRACK_HEIGHT,
                )

    def _update_clip(self, clip_placer: ui.Placer, clip_data):
        clip_offset_x = self._timeline_grid_model.transform_timeline_to_position(clip_data[0])
        clip_length = clip_data[1] - clip_data[0]
        clip_width = clip_length * self._timeline_grid_model.frame_width
        clip_placer.offset_x = ui.Pixel(clip_offset_x)
        clip_placer.width = ui.Pixel(clip_width)

    async def _update_clips(self, clips):
        # Async update must be done async for drawing to update
        for clip_placer, clip_data in clips:
            self._update_clip(clip_placer, clip_data)

    def _update_content(self):
        _update_clips = []
        for track in TRACKS.values():
            for clip_name, clip_data in track.items():
                clip = self._clip_placers.get(clip_name)
                if clip:
                    _update_clips.append((clip, clip_data))
        if _update_clips:
            asyncio.ensure_future(self._update_clips(_update_clips))


# default timeline (frames) - by default this uses StageRange model.
default_window = ui.Window("Default Timeline", **_window_kwargs)
with default_window.frame:
    with ui.VStack():
        ui.Spacer(height=10)
        with ui.HStack():
            ui.Spacer(width=10)
            TimelineView()
            ui.Spacer(width=10)
        ui.Spacer(height=10)

# default timeline with seconds display
default_window_seconds = ui.Window("Default Timeline: Seconds", **_window_kwargs)
with default_window_seconds.frame:
    TimelineView(time_display=TimeDisplay.SECONDS)


# # Timeline with content
content_window = ui.Window("Timeline with Content", **_window_kwargs)
content_delegate = ContentDelegate()
gutter_delegate = GutterDelegate()
with content_window.frame:
    TimelineView(
        build_content=True,
        build_range=True,
        timeline_content_delegate=content_delegate,
        timeline_gutter_delegate=gutter_delegate,
    )

# Timeline with custom range and range slider
frame_range = RangeModel()
range_window = ui.Window("Timeline with unbound Range Model: Seconds", **_window_kwargs)
with range_window.frame:
    TimelineView(build_range=False, range_model=frame_range, time_display=TimeDisplay.SECONDS)

# No scrubber - use a custom model so that we don't change stage time when clicking.
frame_range_2 = RangeModel(min=None, max=None)
no_scrubber_window = ui.Window("Timeline No Scrubber", **_window_kwargs)
with no_scrubber_window.frame:
    TimelineView(build_scrubber=False, range_model=frame_range_2)

# No scrubber - use a custom model so that we don't change stage time when clicking.
timeline_seconds_window = ui.Window("Stage Timeline: read only max range", **_window_kwargs)
stage_range = StageRangeModel(max_range_read_only=True)
with timeline_seconds_window.frame:
    TimelineView(range_model=stage_range, build_range=True)
