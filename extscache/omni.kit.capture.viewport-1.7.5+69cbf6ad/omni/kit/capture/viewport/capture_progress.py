# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import os
import math
import asyncio
from enum import Enum, IntEnum
import datetime
import subprocess
import carb
import omni.ui as ui
import omni.kit.app


class CaptureStatus(IntEnum):
    """An enumeration that defines the possible statuses of a capture process in an Omni UI application.

    This enumeration provides a clear indication of the current state of a capture operation. The integer values correspond to the following states:

        NONE (0): No capture operation is active or has been started.
        CAPTURING (1): The capture process is currently running.
        PAUSED (2): The capture process is temporarily suspended.
        FINISHING (3): The capture is in the process of finalizing its operations.
        TO_START_ENCODING (4): The system is ready to begin encoding the captured data.
        ENCODING (5): The captured data is undergoing encoding.
        CANCELLED (6): The capture process has been cancelled.
        DONE (7): The capture process has completed successfully.
    """

    NONE = 0
    CAPTURING = 1
    PAUSED = 2
    FINISHING = 3
    TO_START_ENCODING = 4
    ENCODING = 5
    CANCELLED = 6
    DONE = 7


class CaptureProgress:
    def __init__(self):
        self._init_internal()

    def _init_internal(self, total_frames=1):
        self._total_frames = total_frames
        # at least to capture 1 frame
        if self._total_frames < 1:
            self._total_frames = 1
        self._capture_status = CaptureStatus.NONE
        self._elapsed_time = 0.0
        self._estimated_time_remaining = 0.0
        self._current_frame_time = 0.0
        self._average_time_per_frame = 0.0
        self._encoding_time = 0.0
        self._current_frame = 0
        self._first_frame_num = 0
        self._got_first_frame = False
        self._progress = 0.0
        self._current_subframe = -1
        self._total_subframes = 1
        self._subframe_time = 0.0
        self._total_frame_time = 0.0
        self._average_time_per_subframe = 0.0
        self._total_preroll_frames = 0
        self._prerolled_frames = 0
        self._path_trace_iteration_num = 0
        self._path_trace_subframe_num = 0
        self._total_iterations = 0
        self._average_time_per_iteration = 0.0
        self._is_handling_settle_latency_frames = False
        self._settle_latency_frames_done = 0
        self._total_settle_latency_frames = 0
        self._capture_nth_frame = 1
        self._nth_frames_captured = 0
        self._time_per_frame_for_uncaptured_frames = 0.0

    @property
    def capture_status(self):
        return self._capture_status

    @capture_status.setter
    def capture_status(self, value):
        self._capture_status = value

    @property
    def elapsed_time(self):
        return self._get_time_string(self._elapsed_time)

    @property
    def estimated_time_remaining(self):
        return self._get_time_string(self._estimated_time_remaining)

    @property
    def current_frame_time(self):
        return self._get_time_string(self._current_frame_time)

    @property
    def average_frame_time(self):
        return self._get_time_string(self._average_time_per_frame)

    @property
    def encoding_time(self):
        return self._get_time_string(self._encoding_time)

    @property
    def progress(self):
        return self._progress

    @property
    def current_subframe(self):
        return self._current_subframe if self._current_subframe >= 0 else 0

    @property
    def total_subframes(self):
        return self._total_subframes

    @property
    def subframe_time(self):
        return self._get_time_string(self._subframe_time)

    @property
    def average_time_per_subframe(self):
        return self._get_time_string(self._average_time_per_subframe)

    @property
    def total_preroll_frames(self):
        return self._total_preroll_frames

    @total_preroll_frames.setter
    def total_preroll_frames(self, value):
        self._total_preroll_frames = value

    @property
    def prerolled_frames(self):
        return self._prerolled_frames

    @prerolled_frames.setter
    def prerolled_frames(self, value):
        self._prerolled_frames = value

    @property
    def path_trace_iteration_num(self):
        return self._path_trace_iteration_num

    @path_trace_iteration_num.setter
    def path_trace_iteration_num(self, value):
        self._path_trace_iteration_num = value

    @property
    def path_trace_subframe_num(self):
        return self._path_trace_subframe_num

    @path_trace_subframe_num.setter
    def path_trace_subframe_num(self, value):
        self._path_trace_subframe_num = value

    @property
    def total_iterations(self):
        return self._total_iterations

    @property
    def average_time_per_iteration(self):
        return self._get_time_string(self._average_time_per_iteration)

    @property
    def current_frame_count(self):
        return self._current_frame - self._first_frame_num

    @property
    def total_frames(self):
        return self._total_frames

    @property
    def is_handling_settle_latency_frames(self):
        return self._is_handling_settle_latency_frames

    @property
    def settle_latency_frames_done(self):
        return self._settle_latency_frames_done

    @property
    def total_settle_latency_frames(self):
        return self._total_settle_latency_frames

    @property
    def capture_every_nth_frame(self):
        return self._capture_nth_frame

    @property
    def done(self) -> bool:
        return self._capture_status == CaptureStatus.DONE

    def start_capturing(self, total_frames, preroll_frames=0, capture_nth_frame=1):
        self._init_internal(total_frames)
        self._total_preroll_frames = preroll_frames
        self._capture_status = CaptureStatus.CAPTURING
        self._capture_nth_frame = capture_nth_frame

    def finish_capturing(self):
        self._capture_status = CaptureStatus.DONE

    def is_prerolling(self):
        return (
            (self._capture_status == CaptureStatus.CAPTURING or self._capture_status == CaptureStatus.PAUSED)
            and self._total_preroll_frames > 0
            and self._total_preroll_frames > self._prerolled_frames
        )

    def add_encoding_time(self, delta_time):
        if self._estimated_time_remaining > 0.0:
            self._elapsed_time += self._estimated_time_remaining
            self._estimated_time_remaining = 0.0
        self._encoding_time += delta_time

    def add_frame_time(
        self,
        frame,
        delta_time,
        pt_subframe_num=0,
        pt_total_subframes=0,
        pt_iteration_num=0,
        pt_iteration_per_subframe=0,
        handling_settle_latency_frames=False,
        settle_latency_frames_done=0,
        total_settle_latency_frames=0,
    ):
        if not self._got_first_frame:
            self._got_first_frame = True
            self._first_frame_num = frame
            self._current_frame = frame

        self._path_trace_subframe_num = pt_subframe_num
        self._path_trace_iteration_num = pt_iteration_num
        self._total_subframes = pt_total_subframes
        self._total_iterations = pt_iteration_per_subframe

        self._elapsed_time += delta_time
        if self._current_frame != frame:
            frames_captured = self._current_frame - self._first_frame_num + 1
            if self.is_capturing_every_nth_frame():
                if self.is_capturing_the_nth_frame():
                    if self._nth_frames_captured == 0:
                        self._average_time_per_frame = self._current_frame_time
                    else:
                        self._average_time_per_frame = (
                            self._nth_frames_captured * self._average_time_per_frame + self._current_frame_time
                        ) / (self._nth_frames_captured + 1)
                    self._nth_frames_captured += 1
                else:
                    self._time_per_frame_for_uncaptured_frames = self._current_frame_time
            else:
                self._average_time_per_frame = self._elapsed_time / frames_captured

            self._current_frame = frame
            self._current_frame_time = delta_time
        else:
            self._current_frame_time += delta_time

        if frame == self._first_frame_num:
            self._estimated_time_remaining = 0.0
            self._progress = 0.0
        else:
            if self.is_capturing_every_nth_frame():
                frames_wanted_ahead = (
                    math.ceil(self._total_frames / self._capture_nth_frame) - self._nth_frames_captured
                )
                frames_unwanted_ahead = (
                    self._total_frames - (self._current_frame - self._first_frame_num) - frames_wanted_ahead
                )
                # when capturing every nth frame, if there is no frames wanted, we estimate the remaining time by calculating the time for the unwanted frames only,
                # otherwise we might result in negative estimated time
                if frames_wanted_ahead > 1:
                    self._estimated_time_remaining = (
                        self._average_time_per_frame * frames_wanted_ahead
                        + self._time_per_frame_for_uncaptured_frames * frames_unwanted_ahead
                        - self._current_frame_time
                    )
                elif frames_wanted_ahead == 1 and self._average_time_per_frame > self._current_frame_time:
                    self._estimated_time_remaining = (
                        self._average_time_per_frame
                        - self._current_frame_time
                        + self._time_per_frame_for_uncaptured_frames * frames_unwanted_ahead
                    )
                else:
                    self._estimated_time_remaining = self._time_per_frame_for_uncaptured_frames * frames_unwanted_ahead
                total_frame_time = self._elapsed_time + self._estimated_time_remaining
            else:
                total_frame_time = self._average_time_per_frame * self._total_frames
                # if users pause for long times, or there are skipped frames, it's possible that elapsed time will be greater than estimated total time
                # if this happens, estimate it again
                if self._elapsed_time >= total_frame_time:
                    if self._elapsed_time < delta_time + self._average_time_per_frame:
                        total_frame_time += delta_time + self._average_time_per_frame
                    else:
                        total_frame_time = self._elapsed_time + self._average_time_per_frame * (
                            self._total_frames - self._current_frame + 1
                        )

                self._estimated_time_remaining = total_frame_time - self._elapsed_time

            # In case the new progress becomes less than the current progress,
            # do not update the progress to get a better experience rather than make the progresser cursor jitter
            new_progress = self._elapsed_time / total_frame_time
            if new_progress > self._progress:
                self._progress = new_progress

        self._is_handling_settle_latency_frames = handling_settle_latency_frames
        self._settle_latency_frames_done = settle_latency_frames_done
        self._total_settle_latency_frames = total_settle_latency_frames

    def add_single_frame_capture_time_for_pt(self, subframe, total_subframes, delta_time):
        self._total_subframes = total_subframes
        self._elapsed_time += delta_time
        self._current_frame_time += delta_time

        if self._current_subframe != subframe:
            self._subframe_time = delta_time
            if self._current_subframe == -1:
                self._average_time_per_subframe = self._elapsed_time
            else:
                self._average_time_per_subframe = self._elapsed_time / subframe
                self._total_frame_time = self._average_time_per_subframe * total_subframes
        else:
            self._subframe_time += delta_time

        self._current_subframe = subframe
        if self._current_subframe == 0:
            self._estimated_time_remaining = 0.0
            self._progress = 0.0
        else:
            if self._elapsed_time >= self._total_frame_time:
                self._total_frame_time += delta_time + self._average_time_per_subframe
            self._estimated_time_remaining = self._total_frame_time - self._elapsed_time
            self._progress = self._elapsed_time / self._total_frame_time

    def add_single_frame_capture_time_for_iray(
        self, subframe, total_subframes, iterations_done, iterations_per_subframe, delta_time
    ):
        self._total_subframes = total_subframes
        self._total_iterations = iterations_per_subframe
        self._elapsed_time += delta_time
        self._path_trace_iteration_num = iterations_done
        self._current_frame_time += delta_time

        if self._current_subframe != subframe:
            self._subframe_time = delta_time
            if self._current_subframe == -1:
                self._average_time_per_subframe = self._elapsed_time
            else:
                self._average_time_per_subframe = self._elapsed_time / subframe
                self._total_frame_time = self._average_time_per_subframe * total_subframes
        else:
            self._subframe_time += delta_time

        self._current_subframe = subframe
        if self._current_subframe == 0:
            self._estimated_time_remaining = 0.0
            self._progress = 0.0
        else:
            if self._elapsed_time >= self._total_frame_time:
                self._total_frame_time += delta_time + self._average_time_per_subframe
            self._estimated_time_remaining = self._total_frame_time - self._elapsed_time
            self._progress = self._elapsed_time / self._total_frame_time

    def _get_time_string(self, time_seconds):
        hours = int(time_seconds / 3600)
        minutes = int((time_seconds - hours * 3600) / 60)
        seconds = time_seconds - hours * 3600 - minutes * 60
        time_string = ""
        if hours > 0:
            time_string += "{:d}h ".format(hours)
        if minutes > 0:
            time_string += "{:d}m ".format(minutes)
        else:
            if hours > 0:
                time_string += "0m "
        time_string += "{:.2f}s".format(seconds)
        return time_string

    def is_capturing_every_nth_frame(self) -> bool:
        return self._capture_nth_frame > 1

    def is_capturing_the_nth_frame(self) -> bool:
        return (
            self.is_capturing_every_nth_frame()
            and (self._current_frame - self._first_frame_num) % self._capture_nth_frame == 0
        )

    def get_every_nth_frame_text(self) -> str:
        if self._capture_nth_frame == 2:
            return "2nd"
        elif self._capture_nth_frame == 3:
            return "3rd"
        else:
            return f"{self._capture_nth_frame}th"


PROGRESS_WINDOW_WIDTH = 360
PROGRESS_WINDOW_HEIGHT = 280
PROGRESS_BAR_WIDTH = 216
PROGRESS_BAR_HEIGHT = 20
PROGRESS_BAR_HALF_HEIGHT = PROGRESS_BAR_HEIGHT / 2
TRIANGLE_WIDTH = 6
TRIANGLE_HEIGHT = 10
TRIANGLE_OFFSET_Y = 10

PROGRESS_WIN_DARK_STYLE = {
    "Triangle::progress_marker": {"background_color": 0xFFD1981D},
    "Rectangle::progress_bar_background": {
        "border_width": 0.5,
        "border_radius": PROGRESS_BAR_HALF_HEIGHT,
        "background_color": 0xFF888888,
    },
    "Rectangle::progress_bar_full": {
        "border_width": 0.5,
        "border_radius": PROGRESS_BAR_HALF_HEIGHT,
        "background_color": 0xFFD1981D,
    },
    "Rectangle::progress_bar": {
        "background_color": 0xFFD1981D,
        "border_radius": PROGRESS_BAR_HALF_HEIGHT,
        "corner_flag": ui.CornerFlag.LEFT,
        "alignment": ui.Alignment.LEFT,
    },
}

PAUSE_BUTTON_STYLE = {
    "Button.Label::pause": {"color": 0xFFCCCCCC},
    "Button.Label::pause:disabled": {"color": 0xFF666666},
}


class CaptureProgressWindow:
    def __init__(self):
        self._app = omni.kit.app.get_app_interface()
        self._update_sub = None
        self._window_caption = "Capture Progress"
        self._window = None
        self._progress = None
        self._progress_bar_len = PROGRESS_BAR_HALF_HEIGHT
        self._progress_step = 0.5
        self._is_single_frame_mode = False
        self._show_pt_subframes = False
        self._show_pt_iterations = False
        self._support_pausing = True
        self._is_external_window = False

    def show(
        self,
        progress,
        single_frame_mode: bool = False,
        show_pt_subframes: bool = False,
        show_pt_iterations: bool = False,
        support_pausing: bool = True,
    ) -> None:
        self._progress = progress
        self._is_single_frame_mode = single_frame_mode
        self._show_pt_subframes = show_pt_subframes
        self._show_pt_iterations = show_pt_iterations
        self._support_pausing = support_pausing
        self._build_ui()
        from carb.eventdispatcher import get_eventdispatcher

        self._update_sub = get_eventdispatcher().observe_event(
            event_name=omni.kit.app.GLOBAL_EVENT_UPDATE,
            on_event=self._on_update,
            observer_name="omni.kit.capture.viewport.capture_progress",
        )

    def close(self):
        if self._is_external_window:
            asyncio.ensure_future(self._move_back_to_main_window())
        else:
            self._window.destroy()
            self._window = None
        self._update_sub = None

    def move_to_external_window(self):
        self._window.move_to_new_os_window()
        self._is_external_window = True

    def move_to_main_window(self):
        if self._is_external_window:
            asyncio.ensure_future(self._move_back_to_main_window())

    def is_external_window(self):
        return self._is_external_window

    async def _move_back_to_main_window(self):
        was_external, self._is_external_window = self._is_external_window, False
        if was_external:
            self._window.move_to_main_os_window()
            app = omni.kit.app.get_app()
            for _ in range(2):
                await app.next_update_async()
            self._window.destroy()
            self._window = None

    def _build_progress_bar(self):
        self._progress_bar_area.clear()
        self._progress_bar_area.set_style(PROGRESS_WIN_DARK_STYLE)
        with self._progress_bar_area:
            with ui.Placer(offset_x=self._progress_bar_len - TRIANGLE_WIDTH / 2, offset_y=TRIANGLE_OFFSET_Y):
                ui.Triangle(
                    name="progress_marker",
                    width=TRIANGLE_WIDTH,
                    height=TRIANGLE_HEIGHT,
                    alignment=ui.Alignment.CENTER_BOTTOM,
                )
            with ui.ZStack():
                ui.Rectangle(name="progress_bar_background", width=PROGRESS_BAR_WIDTH, height=PROGRESS_BAR_HEIGHT)
                ui.Rectangle(name="progress_bar", width=self._progress_bar_len, height=PROGRESS_BAR_HEIGHT)

    def _build_ui_timer(self, text, init_value):
        with ui.HStack():
            with ui.HStack(width=ui.Percent(50)):
                ui.Spacer()
                ui.Label(text, width=0)
            with ui.HStack(width=ui.Percent(50)):
                ui.Spacer(width=15)
                timer_label = ui.Label(init_value)
                ui.Spacer()
                return timer_label

    def _build_multi_frames_capture_timers(self):
        self._ui_elapsed_time = self._build_ui_timer("Elapsed time", self._progress.elapsed_time)
        self._ui_remaining_time = self._build_ui_timer(
            "Estimated time remaining", self._progress.estimated_time_remaining
        )
        frame_count_str = f"{self._progress.current_frame_count}/{self._progress.total_frames}"
        self._ui_frame_count = self._build_ui_timer("Current/Total frames", frame_count_str)
        self._ui_current_frame_time = self._build_ui_timer("Current frame time", self._progress.current_frame_time)
        if self._show_pt_subframes:
            subframes_str = f"{self._progress.path_trace_subframe_num}/{self._progress.total_subframes}"
            self._ui_pt_subframes = self._build_ui_timer("Subframe/Total subframes", subframes_str)
        if self._show_pt_iterations:
            subframes_str = f"{self._progress.path_trace_subframe_num}/{self._progress.total_subframes}"
            self._ui_pt_subframes = self._build_ui_timer("Subframe/Total subframes", subframes_str)
            iter_str = f"{self._progress.path_trace_iteration_num}/{self._progress.total_iterations}"
            self._ui_pt_iterations = self._build_ui_timer("Iterations done/Total", iter_str)
        self._ui_ave_frame_time = self._build_ui_timer("Average time per frame", self._progress.average_frame_time)
        self._ui_encoding_time = self._build_ui_timer("Encoding", self._progress.encoding_time)

    def _build_single_frame_capture_timers(self):
        self._ui_elapsed_time = self._build_ui_timer("Elapsed time", self._progress.elapsed_time)
        self._ui_remaining_time = self._build_ui_timer(
            "Estimated time remaining", self._progress.estimated_time_remaining
        )
        if self._show_pt_subframes:
            subframe_count = f"{self._progress.current_subframe}/{self._progress.total_subframes}"
            self._ui_subframe_count = self._build_ui_timer("Subframe/Total subframes", subframe_count)
            self._ui_current_frame_time = self._build_ui_timer("Current subframe time", self._progress.subframe_time)
            self._ui_ave_frame_time = self._build_ui_timer(
                "Average time per subframe", self._progress.average_time_per_subframe
            )
        if self._show_pt_iterations:
            subframe_count = f"{self._progress.current_subframe}/{self._progress.total_subframes}"
            self._ui_subframe_count = self._build_ui_timer("Subframe/Total subframes", subframe_count)
            iteration_count = f"{self._progress.path_trace_iteration_num}/{self._progress.total_iterations}"
            self._ui_iteration_count = self._build_ui_timer("Iterations done/Per subframe", iteration_count)
            # self._ui_ave_iteration_time = self._build_ui_timer("Average time per iteration", self._progress.average_time_per_iteration)
            self._ui_ave_frame_time = self._build_ui_timer(
                "Average time per subframe", self._progress.average_time_per_subframe
            )

    def _build_notification_area(self):
        with ui.HStack():
            ui.Spacer(width=ui.Percent(20))
            self._notification = ui.Label("")
            ui.Spacer(width=ui.Percent(10))

    def _build_ui(self):
        if self._window is None:
            self._window = ui.Window(
                self._window_caption,
                width=PROGRESS_WINDOW_WIDTH,
                height=PROGRESS_WINDOW_HEIGHT,
                style=PROGRESS_WIN_DARK_STYLE,
            )
            with self._window.frame:
                with ui.VStack():
                    with ui.HStack():
                        ui.Spacer(width=ui.Percent(20))
                        self._progress_bar_area = ui.VStack()
                        self._build_progress_bar()
                        ui.Spacer(width=ui.Percent(20))
                    ui.Spacer(height=5)

                    if self._is_single_frame_mode:
                        self._build_single_frame_capture_timers()
                    else:
                        self._build_multi_frames_capture_timers()

                    self._build_notification_area()

                    with ui.HStack():
                        with ui.HStack(width=ui.Percent(50)):
                            ui.Spacer()
                            self._ui_pause_button = ui.Button(
                                "Pause",
                                height=0,
                                clicked_fn=self._on_pause_clicked,
                                enabled=self._support_pausing,
                                style=PAUSE_BUTTON_STYLE,
                                name="pause",
                            )
                        with ui.HStack(width=ui.Percent(50)):
                            ui.Spacer(width=15)
                            ui.Button("Cancel", height=0, clicked_fn=self._on_cancel_clicked)
                            ui.Spacer()
                    ui.Spacer()

        self._window.visible = True
        self._update_timers()

    def _on_pause_clicked(self):
        if self._progress.capture_status == CaptureStatus.CAPTURING and self._ui_pause_button.text == "Pause":
            self._progress.capture_status = CaptureStatus.PAUSED
            self._ui_pause_button.text = "Resume"
        elif self._progress.capture_status == CaptureStatus.PAUSED:
            self._progress.capture_status = CaptureStatus.CAPTURING
            self._ui_pause_button.text = "Pause"

    def _on_cancel_clicked(self):
        if (
            self._progress.capture_status == CaptureStatus.CAPTURING
            or self._progress.capture_status == CaptureStatus.PAUSED
        ):
            self._progress.capture_status = CaptureStatus.CANCELLED

    def _update_timers(self):
        if self._is_single_frame_mode:
            self._ui_elapsed_time.text = self._progress.elapsed_time
            self._ui_remaining_time.text = self._progress.estimated_time_remaining
            if self._show_pt_subframes:
                subframe_count = f"{self._progress.current_subframe}/{self._progress.total_subframes}"
                self._ui_subframe_count.text = subframe_count
                self._ui_current_frame_time.text = self._progress.subframe_time
                self._ui_ave_frame_time.text = self._progress.average_time_per_subframe
            if self._show_pt_iterations:
                subframe_count = f"{self._progress.current_subframe}/{self._progress.total_subframes}"
                self._ui_subframe_count.text = subframe_count
                iteration_count = f"{self._progress.path_trace_iteration_num}/{self._progress.total_iterations}"
                self._ui_iteration_count.text = iteration_count
                self._ui_ave_frame_time.text = self._progress.average_time_per_subframe
        else:
            self._ui_elapsed_time.text = self._progress.elapsed_time
            self._ui_remaining_time.text = self._progress.estimated_time_remaining
            frame_count_str = f"{self._progress.current_frame_count}/{self._progress.total_frames}"
            self._ui_frame_count.text = frame_count_str
            self._ui_current_frame_time.text = self._progress.current_frame_time
            if self._show_pt_subframes:
                subframes_str = f"{self._progress.path_trace_subframe_num}/{self._progress.total_subframes}"
                self._ui_pt_subframes.text = subframes_str
            if self._show_pt_iterations:
                subframes_str = f"{self._progress.path_trace_subframe_num}/{self._progress.total_subframes}"
                self._ui_pt_subframes.text = subframes_str
                iter_str = f"{self._progress.path_trace_iteration_num}/{self._progress.total_iterations}"
                self._ui_pt_iterations.text = iter_str
            self._ui_ave_frame_time.text = self._progress.average_frame_time
            self._ui_encoding_time.text = self._progress.encoding_time

    def _update_notification(self):
        if self._progress.capture_status == CaptureStatus.CAPTURING:
            if self._progress.is_prerolling():
                msg = "Running preroll frames {}/{}, please wait...".format(
                    self._progress.prerolled_frames, self._progress.total_preroll_frames
                )
                self._notification.text = msg
            elif not self._is_single_frame_mode:
                if self._progress.is_handling_settle_latency_frames:
                    msg = "Running settle latency frames {}/{}...".format(
                        self._progress.settle_latency_frames_done, self._progress.total_settle_latency_frames
                    )
                    self._notification.text = msg
                else:
                    info_for_nth_frame = ""
                    if self._progress.is_capturing_every_nth_frame():
                        if self._progress.is_capturing_the_nth_frame():
                            info_for_nth_frame = "rendering"
                        else:
                            info_for_nth_frame = "skipping"
                        self._notification.text = f"Capturing every {self._progress.get_every_nth_frame_text()} frame at {self._progress.current_frame_count}, {info_for_nth_frame}"
                    else:
                        self._notification.text = f"Capturing frame {self._progress.current_frame_count}..."
            elif self._is_single_frame_mode and not self._show_pt_iterations and not self._show_pt_subframes:
                self._notification.text = "Waiting for rendering to resolve..."
        elif self._progress.capture_status == CaptureStatus.ENCODING:
            self._notification.text = "Encoding..."
        else:
            self._notification.text = ""

    def _on_update(self, _):
        self._update_notification()
        self._update_timers()
        self._progress_bar_len = (
            PROGRESS_BAR_WIDTH - PROGRESS_BAR_HEIGHT
        ) * self._progress.progress + PROGRESS_BAR_HALF_HEIGHT
        self._build_progress_bar()
