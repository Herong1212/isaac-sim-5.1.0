# Copyright (c) 2022-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import os
from typing import List, Tuple

import omni.kit.commands
from omni.kit.widget.layers.path_utils import PathUtils

from ..bindings._omni_kit_stagerecorder_core import *


class StartRecording(omni.kit.commands.Command):
    # TODO: reorg parameters and consider default values
    # TODO: Specify types throughout!
    def __init__(
        self,
        target_paths: List[Tuple[str, bool]],
        live_mode: bool,
        use_frame_range: bool,
        start_frame: int,
        end_frame: int,
        use_preroll: bool,
        preroll_frame: int,
        record_to: str,
        take_name: str,
        record_folder: str,
        increment_name: bool,
        apply_root_anim: bool,
        fps: float,
    ):
        """
        Start recording using the specified arguments.

        Args:
            target_paths: list of tuples, each specifying the path and whether to include children
            live_mode: whether to record live or lockstep
            use_frame_range: whether to use the specified arguments for start and end frame
            start_frame: starting frame
            end_frame: ending frame
            use_preroll: whether to use the specified argument for preroll frame
            preroll_frame: starting frame after pre-roll (to allow sim to "warm-up")
            record_to: "FILE" or "NEW_LAYER"
            take_name: base name for takes
            record_folder: folder path for takes
            increment_name: whether to increment name for each take or overwrite
            apply_root_anim: whether to bake root motion (UsdSkel only)
            fps: frame rate in Live Mode, otherwise just for setting timeCodesPerSecond (0=stage fps)
        """
        super().__init__()
        self._target_paths = target_paths
        self._live_mode = live_mode
        self._use_frame_range = use_frame_range
        self._start_frame = start_frame
        self._end_frame = end_frame
        self._use_preroll = use_preroll
        self._preroll_frame = preroll_frame
        self._record_to = record_to
        self._take_name = take_name
        self._record_folder = record_folder
        self._increment_name = increment_name
        self._apply_root_anim = apply_root_anim
        self._fps = fps

        self._plugin = acquire_interface()  # released in extension
        self._recording_started_by_me = False

    def do(self):
        if not self._target_paths:
            raise ValueError(f"StartRecording command: Missing target path(s)")

        try:
            record_to = self._get_record_to()
        except KeyError:
            raise ValueError(f"StartRecording command: Unrecognized record_to value {self._record_to}")

        if not self._plugin.try_start_progress():
            raise RuntimeError(f"StartRecording command: Attempt failed - recording already in progress")
        else:
            time_mode = TimeMode.LIVE if self._live_mode else TimeMode.WORLD_TIME
            if not self._plugin.validate_recording_frame_range(
                time_mode, self._use_frame_range, self._start_frame, self._end_frame
            ):
                return {"error": "Recording range exceeds maximum"}
            if not self._plugin.validate_recording_preroll(self._use_preroll, self._preroll_frame):
                return {"error": "Recording pre-roll exceeds maximum"}

            self._recording_started_by_me = True
            self._plugin.clear_recording_targets()
            for target_path in self._target_paths:
                self._plugin.add_recording_target(target_path[0], target_path[1])
            self._plugin.set_recording_time_mode(time_mode)
            self._plugin.set_recording_frame_range(self._use_frame_range, self._start_frame, self._end_frame)
            self._plugin.set_recording_preroll(self._use_preroll, self._preroll_frame)
            take_name, prim_name = self._get_take_name()
            # TODO: Remove dead code since animOnly is always true
            self._plugin.set_recording_config(
                record_to,
                self._increment_name,
                True,
                self._fps,
            )
            for target_path in self._target_paths:
                self._plugin.set_skel_recording_option(
                    target_path[0],
                    take_name,
                    "",
                    self._apply_root_anim,
                )
            self._plugin.start_recording()
            return {"error": None}

    def undo(self):
        if self._recording_started_by_me:
            self._plugin.stop_recording(True)

    def _get_take_name(self):
        layer_path = ""
        record_to = self._get_record_to()
        if record_to == RecordTo.FILE or record_to == RecordTo.NEW_LAYER:
            file_ext = ".usd"
            layer_path = self._take_name
            if layer_path != "" and self._record_folder != "":
                layer_path = os.path.join(self._record_folder, layer_path)
            if layer_path != "":
                layer_path = f"{layer_path}{file_ext}"
        prim_name = self._take_name
        if prim_name != "" and PathUtils.is_omni_path(prim_name):
            prim_name, ext = os.path.splitext(os.path.basename(prim_name))

        return layer_path, prim_name

    def _get_record_to(self):
        return RecordTo.__members__[self._record_to]


class StopRecording(omni.kit.commands.Command):
    def __init__(self):
        super().__init__()
        self._plugin = acquire_interface()  # released in extension

    def do(self):
        return self._plugin.stop_recording(False)
