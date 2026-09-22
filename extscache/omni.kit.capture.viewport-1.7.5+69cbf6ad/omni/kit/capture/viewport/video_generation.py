# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import os
import threading
import carb

try:
    from video_encoding import get_video_encoding_interface
except ImportError:
    get_video_encoding_interface = lambda: None

from .singleton import Singleton
from .helper import get_num_pattern_file_path

g_video_encoding_api = get_video_encoding_interface()


@Singleton
class VideoGenerationHelper:
    def __init__(self):
        self._init_internal()

    @property
    def is_encoding(self):
        return self._is_encoding

    @property
    def encoding_done(self):
        return self._is_encoding == False and self._encoding_done == True

    def generating_video(
        self, video_name, frames_dir, filename_prefix, filename_num_pattern,
        start_number, total_frames, frame_rate, image_type=".png"
    ):
        carb.log_warn(f"Using videoencoding plugin to encode video ({video_name})")
        global g_video_encoding_api
        self._encoding_finished = False
        if g_video_encoding_api is None:
            carb.log_warn("Video encoding api not available; cannot encode video.")
            return False

        # acquire list of available frame image files, based on start_number and filename_pattern
        next_frame = start_number
        frame_count = 0
        self._frame_filenames = []
        while True:
            frame_path = get_num_pattern_file_path(
                frames_dir,
                filename_prefix,
                filename_num_pattern,
                next_frame,
                image_type
            )
            if os.path.isfile(frame_path) and os.access(frame_path, os.R_OK):
                self._frame_filenames.append(frame_path)
                next_frame += 1
                frame_count += 1
                if frame_count == total_frames:
                    break
            else:
                break

        carb.log_warn(f"Found {len(self._frame_filenames)} frames to encode.")
        if len(self._frame_filenames) == 0:
            carb.log_warn(f"No frames to encode.")
            return False

        if not g_video_encoding_api.start_encoding(video_name, frame_rate, len(self._frame_filenames), True):
            carb.log_warn(f"videoencoding plug failed to start encoding.")
            return False

        if self._encoding_thread == None:
            self._encoding_thread = threading.Thread(target=self._encode_image_file_sequence, args=())
            self._is_encoding = True
            self._encoding_thread.start()
        return True

    def _init_internal(self):
        self._video_generation_done_fn = None
        self._frame_filenames = []
        self._encoding_thread = None
        self._is_encoding = False
        self._encoding_done = False

    def _encode_image_file_sequence(self):
        global g_video_encoding_api
        try:
            for frame_filename in self._frame_filenames:
                g_video_encoding_api.encode_next_frame_from_file(frame_filename)
        except:
            import traceback

            carb.log_warn(traceback.format_exc())
        finally:
            g_video_encoding_api.finalize_encoding()
            self._init_internal()
            self._encoding_done = True
