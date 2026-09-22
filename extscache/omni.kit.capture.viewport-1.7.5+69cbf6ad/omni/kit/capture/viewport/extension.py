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
import time
import datetime
import asyncio
from typing import Callable, List, Set
import omni.ext
import carb
import carb.eventdispatcher
import omni.kit.app
import omni.timeline
import omni.usd
import omni.ui
from pxr import Gf, UsdRender, Sdf
from .capture_options import *
from .capture_progress import *
from .video_generation import VideoGenerationHelper
from .helper import (
    get_num_pattern_file_path,
    check_render_product_ext_availability,
    is_valid_render_product_prim_path,
    RenderProductCaptureHelper,
)
from omni.kit.viewport.utility import get_active_viewport, capture_viewport_to_file
import omni.appwindow


PERSISTENT_SETTINGS_PREFIX = "/persistent"
FILL_VIEWPORT_SETTING = PERSISTENT_SETTINGS_PREFIX + "/app/viewport/{viewport_api_id}/fillViewport"
FILL_VIEWPORT_DEFAULT = "/app/viewport/defaults/fillViewport"
SEQUENCE_CAPTURE_WAIT = "/app/captureSequence/waitFrames"
MP4_ENCODING_BITRATE_SETTING = "/exts/omni.videoencoding/bitrate"
MP4_ENCODING_IFRAME_INTERVAL_SETTING = "/exts/omni.videoencoding/iframeinterval"
MP4_ENCODING_PRESET_SETTING = "/exts/omni.videoencoding/preset"
MP4_ENCODING_PROFILE_SETTING = "/exts/omni.videoencoding/profile"
MP4_ENCODING_RC_MODE_SETTING = "/exts/omni.videoencoding/rcMode"
MP4_ENCODING_RC_TARGET_QUALITY_SETTING = "/exts/omni.videoencoding/rcTargetQuality"
MP4_ENCODING_VIDEO_FULL_RANGE_SETTING = "/exts/omni.videoencoding/videoFullRangeFlag"
VIDEO_FRAMES_DIR_NAME = "frames"
DEFAULT_IMAGE_FRAME_TYPE_FOR_VIDEO = ".png"
SEQUENCER_CAMERA = "[ Sequencer Camera ]"
capture_instance = None


class RenderStatus(IntEnum):
    # Note render status values from rtx/hydra/HydraRenderResults.h

    # Rendering was successful. A path tracer might not have reached a stopping criterion though.
    eSuccess = 0
    # Rendering was successful and the renderer has reached a stopping criterion on this iteration.
    eStopCriterionJustReached = 1
    # Rendering was successful and the renderer has reached a stopping criterion.
    eStopCriterionReached = 2
    # Rendering failed
    eFailed = 3


class CaptureExtension(omni.ext.IExt):
    """CaptureExtension provides a capture framework that manages the lifecycle of capturing viewport or application content. This extension is responsible for initializing capture options, preparing the capture environment, including folder structures and rendering configurations, and controlling the overall capture process from startup to shutdown. It supports various capture modes, such as single frame, sequence, and video capture, and it integrates with the rendering subsystem and timeline management to accurately record frame data. The extension can handle different rendering presets and dynamically adjust settings based on the capture configuration while ensuring that previous state settings are restored once the capture is complete.

    Example:
        .. code-block:: python

            capture_ext = CaptureExtension()
            if capture_ext.start():
                print('Capture started successfully')
    """

    def on_startup(self):
        """Initializes the capture extension on startup and sets up capture resources."""
        global capture_instance
        capture_instance = self

        self._options = CaptureOptions()
        self._progress = CaptureProgress()
        self._progress_window = CaptureProgressWindow()

        import omni.renderer_capture

        self._renderer = omni.renderer_capture.acquire_renderer_capture_interface()
        self._viewport_api = None

        self._app = omni.kit.app.get_app_interface()
        self._timeline = omni.timeline.get_timeline_interface()
        self._usd_context = omni.usd.get_context()
        self._selection = self._usd_context.get_selection()
        self._settings = carb.settings.get_settings()
        self._show_default_progress_window = True
        self._progress_update_fn = None
        self._forward_one_frame_fn = None
        self._capture_finished_fn = None
        self._to_capture_render_product = False
        self._render_product_path_for_capture = ""
        self._is_adaptivesampling_stop_criterion_reached = False
        # Variable to hold vis/invis state when toggled for capture
        self.__restore_visible = None
        self.__post_process_wait = 0

        self._frame_path: str = ""
        self._frame_paths: List[str] = []

    class ReshadeUpdateState:
        """Represents the state of the reshade update process during capture operations.

        This enumeration defines the internal stages used by the capture system to manage when and how reshade settings are applied. The states indicate whether reshade adjustments are to be applied before the capture (PRE_CAPTURE), immediately after the capture (POST_CAPTURE), or when post-capture processing is complete and the system is ready for further operations (POST_CAPTURE_READY).

        This enum is intended for internal use in coordinating reshade transitions during the capture workflow to ensure that reshade settings are synchronized with frame capture events and that image quality is maintained throughout the process.
        """

        PRE_CAPTURE = 0
        POST_CAPTURE = 1
        POST_CAPTURE_READY = 3

    def on_shutdown(self):
        """Handles shutdown for the capture extension and cleans up resources."""
        self._progress = None
        self._progress_window = None
        global capture_instance
        capture_instance = None

    @property
    def options(self):
        """Gets the current capture options.

        Returns:
            CaptureOptions: The current capture options.
        """
        return self._options

    @options.setter
    def options(self, value):
        """Sets the capture options.

        Args:
            value (CaptureOptions): Capture options instance to set.
        """
        self._options = value

    @property
    def progress(self):
        """Gets the current capture progress.

        Returns:
            CaptureProgress: Current capture progress.
        """
        return self._progress

    @property
    def show_default_progress_window(self):
        """Gets whether the default progress window is shown.

        Returns:
            bool: True if the default progress window is shown, otherwise False.
        """
        return self._show_default_progress_window

    @show_default_progress_window.setter
    def show_default_progress_window(self, value):
        """Sets the flag to show the default progress window.

        Args:
            value (bool): Boolean flag to display or hide the progress window.
        """
        self._show_default_progress_window = value

    @property
    def progress_update_fn(self):
        """Gets the progress update function.

        Returns:
            Callable: The callback function used for progress updates.
        """
        return self._progress_update_fn

    @progress_update_fn.setter
    def progress_update_fn(self, value):
        """Sets the progress update function.

        Args:
            value (Callable): Function to update capture progress.
        """
        self._progress_update_fn = value

    @property
    def forward_one_frame_fn(self):
        """Gets the function to forward one frame.

        Returns:
            Callable: The callback function used to forward one frame.
        """
        return self._forward_one_frame_fn

    @forward_one_frame_fn.setter
    def forward_one_frame_fn(self, value):
        """Sets the function to forward one frame.

        Args:
            value (Callable): Function to execute to forward one frame.
        """
        self._forward_one_frame_fn = value

    @property
    def capture_finished_fn(self):
        """Gets the capture finished callback function.

        Returns:
            Callable: The callback function executed upon capture completion.
        """
        return self._capture_finished_fn

    @capture_finished_fn.setter
    def capture_finished_fn(self, value):
        """Sets the function to be called when capture is finished.

        Args:
            value (Callable): Callback function to execute upon capture completion.
        """
        self._capture_finished_fn = value

    @property
    def done(self) -> bool:
        """Gets whether the capture has finished.

        Returns:
            bool: True if capture is finished, otherwise False.
        """
        return self._progress.done

    def start(self) -> bool:
        """Starts the capture process.

        Returns:
            bool: True if capture started successfully, False otherwise.
        """
        self._viewport_api = get_active_viewport()

        self._frame_path = ""
        self._frame_paths = []
        if not self._options.is_valid():
            carb.log_warn("Capture couldn't be started due to invalid capture options.")
            return False

        self._to_capture_render_product = self._check_if_to_capture_render_product()
        if self._to_capture_render_product:
            self._render_product_path_for_capture = RenderProductCaptureHelper.prepare_render_product_for_capture(
                self._options.render_product,
                self._get_camera_for_render_product_capture(),
                Gf.Vec2i(self._options.res_width, self._options.res_height),
            )
            if len(self._render_product_path_for_capture) == 0:
                carb.log_warn(
                    f"Capture will use render product {self._options.render_product}'s original camera and resolution because it failed to make a copy of it for processing."
                )
                self._render_product_path_for_capture = self._options.render_product

        # use usd time code for animation play during capture, caption option's fps setting for movie encoding
        if CaptureOptions.INVALID_ANIMATION_FPS == self._options.animation_fps:
            self._capture_fps = self._timeline.get_time_codes_per_seconds()
        else:
            self._capture_fps = self._options.animation_fps

        if not self._prepare_folder_and_counters():
            if self._render_product_path_for_capture != self._options.render_product:
                RenderProductCaptureHelper.remove_render_product_for_capture(self._render_product_path_for_capture)
                self._render_product_path_for_capture = ""
            carb.log_warn("Capture couldn't be started due to failed to prepare folders for capture.")
            return False

        # Viewport could be None in tests of omni.services.farm.agent.runner but requires output folders ready
        if self._viewport_api is None:
            carb.log_warn("Capture couldn't be started due to no active viewport.")
            return False

        if self._prepare_viewport():
            self._start_internal()
            return True
        else:
            carb.log_warn("Capture couldn't be started due to failed to prepare viewport for capture.")
            return False

    def pause(self):
        """Pauses the ongoing capture if it is currently capturing."""
        if self._progress.capture_status == CaptureStatus.CAPTURING and self._ui_pause_button.text == "Pause":
            self._progress.capture_status = CaptureStatus.PAUSED

    def resume(self):
        """Resumes the paused capture process."""
        if self._progress.capture_status == CaptureStatus.PAUSED:
            self._progress.capture_status = CaptureStatus.CAPTURING

    def cancel(self):
        """Cancels the ongoing capture process."""
        if (
            self._progress.capture_status == CaptureStatus.CAPTURING
            or self._progress.capture_status == CaptureStatus.PAUSED
        ):
            self._progress.capture_status = CaptureStatus.CANCELLED

    def _update_progress_hook(self):
        if self._progress_update_fn is not None:
            self._progress_update_fn(
                self._progress.capture_status,
                self._progress.progress,
                self._progress.elapsed_time,
                self._progress.estimated_time_remaining,
                self._progress.current_frame_time,
                self._progress.average_frame_time,
                self._progress.encoding_time,
                self._frame_counter,
                self._total_frame_count,
            )

    def _get_index_for_image(self, dir, file_name, image_suffix):
        def is_int(string_val):
            try:
                v = int(string_val)
                return True
            except:
                return False

        images = os.listdir(dir)
        name_len = len(file_name)
        suffix_len = len(image_suffix)
        max_index = 0
        for item in images:
            if item.startswith(file_name) and item.endswith(image_suffix):
                # If capture render product, there will be "_" + aov_name at the end of file name
                num_part = item[name_len : (len(item) - suffix_len)].split("_")[0]
                if is_int(num_part):
                    num = int(num_part)
                    if max_index < num:
                        max_index = num
        return max_index + 1

    def _float_to_time(self, ft):
        hour = int(ft)
        ft = (ft - hour) * 60
        minute = int(ft)
        ft = (ft - minute) * 60
        second = int(ft)
        ft = (ft - second) * 1000000
        microsecond = int(ft)
        return datetime.time(hour, minute, second, microsecond)

    def _check_if_to_capture_render_product(self):
        if len(self._options.render_product) == 0:
            return False

        omnigraph_exts_available = check_render_product_ext_availability()
        if not omnigraph_exts_available:
            carb.log_warn(
                f"Viewport Capture: unable to capture with render product {self._options.render_product} as it needs omni.graph.image.nodes enabled to work."
            )
            return False

        render_product_name = self._viewport_api.render_product_path if self._viewport_api else None
        if not render_product_name:
            carb.log_warn(
                f"Viewport Capture: unable to capture with render product {self._options.render_product} as Kit SDK needs updating to support viewport window render product APIs: {e}"
            )
            return False

        if is_valid_render_product_prim_path(self._options.render_product):
            return True
        else:
            carb.log_warn(
                f"Viewport Capture: unable to capture with render product {self._options.render_product} as it's not a valid Render Product prim path"
            )
            return False

    def _is_environment_sunstudy_player(self):
        if self._options.sunstudy_player is not None:
            return type(self._options.sunstudy_player).__module__ == "omni.kit.environment.core.sunstudy_player.player"
        else:
            carb.log_warn("Sunstudy player type check is valid only when the player is available.")
            return False

    def _update_sunstudy_player_time(self):
        if self._is_environment_sunstudy_player():
            self._options.sunstudy_player.current_time = self._sunstudy_current_time
        else:
            self._options.sunstudy_player.update_time(self._sunstudy_current_time)

    def _set_sunstudy_player_time(self, current_time):
        if self._is_environment_sunstudy_player():
            self._options.sunstudy_player.current_time = current_time
        else:
            date_time = self._options.sunstudy_player.get_date_time()
            time_to_set = self._float_to_time(current_time)
            new_date_time = datetime.datetime(
                date_time.year, date_time.month, date_time.day, time_to_set.hour, time_to_set.minute, time_to_set.second
            )
            self._options.sunstudy_player.set_date_time(new_date_time)

    def _prepare_sunstudy_counters(self):
        self._total_frame_count = self._options.fps * self._options.sunstudy_movie_length_in_seconds
        duration = self._options.sunstudy_end_time - self._options.sunstudy_start_time
        self._sunstudy_iterations_per_frame = self._options.ptmb_subframes_per_frame
        self._sunstudy_delta_time_per_iteration = duration / float(
            self._total_frame_count * self._sunstudy_iterations_per_frame
        )
        self._sunstudy_current_time = self._options.sunstudy_start_time
        self._set_sunstudy_player_time(self._sunstudy_current_time)

    def _prepare_folder_and_counters(self):
        self._workset_dir = self._options.output_folder
        if not self._make_sure_directory_writeable(self._workset_dir):
            carb.log_warn(
                f"Capture failed due to unable to create folder {self._workset_dir} or this folder is not writeable."
            )
            self._finish()
            return False

        if self._options.is_capturing_nth_frames():
            if self._options.capture_every_Nth_frames == 1:
                frames_folder = self._options.file_name + "_frames"
            else:
                frames_folder = (
                    self._options.file_name + "_" + str(self._options.capture_every_Nth_frames) + "th_frames"
                )
            self._nth_frames_dir = os.path.join(self._workset_dir, frames_folder)
            if not self._make_sure_directory_existed(self._nth_frames_dir):
                carb.log_warn(f"Capture failed due to unable to create folder {self._nth_frames_dir}")
                self._finish()
                return False

        if self._options.is_video():
            self._frames_dir = os.path.join(self._workset_dir, self._options.file_name + "_" + VIDEO_FRAMES_DIR_NAME)
            if not self._make_sure_directory_existed(self._frames_dir):
                carb.log_warn(
                    f"Capture failed due to unable to create folder {self._workset_dir} to save frames of the video."
                )
                self._finish()
                return False

            self._video_name = self._options.get_full_path()
            self._frame_pattern_prefix = os.path.join(self._frames_dir, self._options.file_name)

            if self._options.is_capturing_frame():
                self._start_time = float(self._options.start_frame) / self._capture_fps
                self._end_time = float(self._options.end_frame + 1) / self._capture_fps
                self._time = self._start_time
                self._frame = self._options.start_frame
                self._start_number = self._frame
                self._total_frame_count = round((self._end_time - self._start_time) * self._capture_fps)
            else:
                self._start_time = self._options.start_time
                self._end_time = self._options.end_time
                self._time = self._options.start_time
                self._frame = int(self._options.start_time * self._capture_fps)
                self._start_number = self._frame
                self._total_frame_count = math.ceil((self._end_time - self._start_time) * self._capture_fps)

            if self._options.movie_type == CaptureMovieType.SUNSTUDY:
                self._prepare_sunstudy_counters()
        else:
            if self._options.is_capturing_nth_frames():
                self._frame_pattern_prefix = self._nth_frames_dir
                if self._options.is_capturing_frame():
                    self._start_time = float(self._options.start_frame) / self._capture_fps
                    self._end_time = float(self._options.end_frame + 1) / self._capture_fps
                    self._time = self._start_time
                    self._frame = self._options.start_frame
                    self._start_number = self._frame
                    self._total_frame_count = round((self._end_time - self._start_time) * self._capture_fps)
                else:
                    self._start_time = self._options.start_time
                    self._end_time = self._options.end_time
                    self._time = self._options.start_time
                    self._frame = int(self._options.start_time * self._capture_fps)
                    self._start_number = self._frame
                    self._total_frame_count = math.ceil((self._end_time - self._start_time) * self._capture_fps)

                if self._options.movie_type == CaptureMovieType.SUNSTUDY:
                    self._prepare_sunstudy_counters()
            else:
                index = self._get_index_for_image(self._workset_dir, self._options.file_name, self._options.file_type)
                self._frame_pattern_prefix = os.path.join(self._workset_dir, self._options.file_name + str(index))
                self._start_time = self._timeline.get_current_time()
                self._end_time = self._timeline.get_current_time()
                self._time = self._timeline.get_current_time()
                self._frame = 1
                self._start_number = self._frame
                self._total_frame_count = 1
        self._subframe = 0
        self._sample_count = 0
        self._frame_counter = 0
        self._real_time_settle_latency_frames_done = 0
        self._settle_latency_frames = self._get_settle_latency_frames()
        self._last_skipped_frame_path = ""
        self._path_trace_iterations = 0

        self._time_rate = 1.0 / self._capture_fps
        self._time_subframe_rate = (
            self._time_rate * (self._options.ptmb_fsc - self._options.ptmb_fso) / self._options.ptmb_subframes_per_frame
        )
        return True

    def _get_active_camera(self) -> str:
        return self._viewport_api.camera_path if self._viewport_api else ""

    def _get_camera_for_render_product_capture(self) -> str:
        if SEQUENCER_CAMERA == self._options.camera:
            return self._get_active_camera()
        else:
            return self._options.camera

    def _is_to_use_sequencer_camera(self) -> bool:
        return SEQUENCER_CAMERA == self._options.camera

    def _prepare_viewport(self):
        if self._viewport_api is None:
            return False

        self._record_current_window_status(self._viewport_api)

        # if sequencer camera is given, we don't set the camera to start and let sequencer to control cameras
        if not self._is_to_use_sequencer_camera():
            capture_camera = Sdf.Path(self._options.camera)
            if capture_camera != self._saved_camera:
                self._viewport_api.camera_path = capture_camera

        self._viewport_api.updates_enabled = True
        if self._saved_fill_viewport_option:
            fv_setting_path = FILL_VIEWPORT_SETTING.format(viewport_api_id=self._viewport_api.id)
            # for application level capture, we want it to fill the viewport to make the viewport resolution the same to application window resolution
            # while for viewport capture, we can get images with the correct resolution so doesn't need it to fill viewport
            self._settings.set(fv_setting_path, self._options.app_level_capture)

        capture_resolution = (self._options.res_width, self._options.res_height)
        if capture_resolution != (self._saved_resolution_width, self._saved_resolution_height):
            self._viewport_api.resolution = capture_resolution

        self._settings.set_bool("/persistent/app/captureFrame/viewport", True)
        self._settings.set_bool("/app/captureFrame/setAlphaTo1", not self._options.save_alpha)
        if self._options.file_type == ".exr":
            self._settings.set_bool("/app/captureFrame/hdr", self._options.hdr_output)
            self._settings.set_bool("/rtx/post/backgroundZeroAlpha/premultiplyColorByAlpha", True)
        else:
            self._settings.set_bool("/app/captureFrame/hdr", False)
        if self._options.save_alpha:
            self._settings.set_bool("/rtx/post/backgroundZeroAlpha/enabled", True)
            self._settings.set_bool("/rtx/post/backgroundZeroAlpha/backgroundComposite", False)
            if self._options.hdr_output:
                self._settings.set_bool("/rtx/post/backgroundZeroAlpha/ApplyAlphaZeroPassFirst", True)

        if self._to_capture_render_product:
            self._viewport_api.render_product_path = self._render_product_path_for_capture

        # we only clear selection for non application level capture, other we will lose the ui.scene elemets during capture
        if not self._options.app_level_capture:
            self._selection.clear_selected_prim_paths()

        if self._options.render_preset == CaptureRenderPreset.RAY_TRACE:
            self._switch_renderer = self._saved_hd_engine != "rtx" or self._saved_render_mode != "RaytracedLighting"
            if self._switch_renderer:
                self._viewport_api.set_hd_engine("rtx", "RaytracedLighting")
                carb.log_info("Switching to RayTracing Mode")
        elif self._options.render_preset == CaptureRenderPreset.REAL_TIME_PATHTRACING:
            self._switch_renderer = self._saved_hd_engine != "rtx" or self._saved_render_mode != "RealTimePathTracing"
            if self._switch_renderer:
                self._viewport_api.set_hd_engine("rtx", "RealTimePathTracing")
                carb.log_info("Switching to RealTimePathTracing Mode")
        elif self._options.render_preset == CaptureRenderPreset.PATH_TRACE:
            self._switch_renderer = self._saved_hd_engine != "rtx" or self._saved_render_mode != "PathTracing"
            if self._switch_renderer:
                self._viewport_api.set_hd_engine("rtx", "PathTracing")
                carb.log_info("Switching to PathTracing Mode")
        elif self._options.render_preset == CaptureRenderPreset.IRAY:
            self._switch_renderer = self._saved_hd_engine != "iray" or self._saved_render_mode != "iray"
            if self._switch_renderer:
                self._viewport_api.set_hd_engine("iray", "iray")
                carb.log_info("Switching to IRay Mode")
            # now that Iray is not loaded automatically until renderer gets switched
            # we have to save and set the Iray settings after the renderer switch
            self._record_and_set_iray_settings()
        else:
            self._switch_renderer = False
            carb.log_warn("Keeping current Render Mode since render preset is not supported")

        if self._options.debug_material_type == CaptureDebugMaterialType.SHADED:
            self._settings.set_int("/rtx/debugMaterialType", -1)
        elif self._options.debug_material_type == CaptureDebugMaterialType.WHITE:
            self._settings.set_int("/rtx/debugMaterialType", 0)
        else:
            carb.log_info("Keeping current debug mateiral type")

        # tell timeline window to stop force checks of end time so that it won't affect capture range
        self._settings.set_bool("/exts/omni.anim.window.timeline/playinRange", False)

        self._set_totalspp_for_normal_capture()

        # don't show light and grid during capturing
        self._set_vp_object_settings(self._viewport_api, False)

        # disable async rendering for capture, otherwise it won't capture images correctly
        if self._saved_async_rendering:
            self._settings.set_bool("/app/asyncRendering", False)
        if self._saved_async_renderingLatency:
            self._settings.set_bool("/app/asyncRenderingLowLatency", False)

        # Rendering to some image buffers additionally require explicitly setting `set_capture_sync(True)`, on top of
        # disabling the `/app/asyncRendering` setting. This can otherwise cause images to hold corrupted buffer
        # information by erroneously assuming a complete image buffer is available when only a first partial subframe
        # has been renderer (as in the case of EXR):
        self._renderer.set_capture_sync(self._options.file_type == ".exr")
        # frames to wait for the async settings above to be ready, they will need to be detected by viewport, and
        # then viewport will notify the renderer not to do async rendering
        self._frames_to_disable_async_rendering = 2

        # Normally avoid using a high /rtx/pathtracing/spp setting since it causes GPU
        # timeouts for large sample counts. But a value larger than 1 can be useful in Multi-GPU setups
        self._settings.set_int(
            "/rtx/pathtracing/spp", min(self._options.spp_per_iteration, self._options.path_trace_spp)
        )

        # Setting resetPtAccumOnlyWhenExternalFrameCounterChanges ensures we control accumulation explicitly
        # by simpling changing the /rtx/externalFrameCounter value
        self._settings.set_bool("/rtx-transient/resetPtAccumOnlyWhenExternalFrameCounterChanges", True)

        # Enable syncLoads in materialDB and Hydra. This is needed to make sure texture updates finish before we start the rendering
        self._settings.set("/rtx/materialDb/syncLoads", True)
        self._settings.set("/rtx/hydra/materialSyncLoads", True)
        self._settings.set("/rtx-transient/resourcemanager/texturestreaming/async", False)
        self._settings.set("/rtx-transient/resourcemanager/texturestreaming/streamingBudgetMB", 0)
        self._settings.set("/rtx-transient/samplerFeedbackTileSize", 1)
        self._settings.set("/rtx-transient/resourcemanager/texturestreaming/evictionFrameLatency", 0)

        # for now, reshade needs to be turned off and on again to apply settings
        self._settings.set_bool("/rtx/reshade/enable", False)
        # need to skip several updates for reshade settings to apply:
        self._frames_to_apply_reshade = 2

        # these settings need to be True to ensure XR Output Alpha in composited image is right
        if not self._saved_output_alpha_in_composite:
            self._settings.set("/rtx/post/backgroundZeroAlpha/outputAlphaInComposite", True)

        # do not show the minibar of timeline window
        self._settings.set("/exts/omni.kit.timeline.minibar/stay_on_playing", False)

        # enable sequencer camera
        self._settings.set(
            "/persistent/exts/omni.kit.window.sequencer/useSequencerCamera", self._is_to_use_sequencer_camera()
        )

        # set timeline animation fps
        if self._capture_fps != self._saved_timeline_fps:
            self._timeline.set_time_codes_per_second(self._capture_fps)

        # return success
        return True

    def _show_progress_window(self):
        return (
            self._options.is_video()
            or self._options.is_capturing_nth_frames()
            or self._options.is_capturing_pathtracing_single_frame()
            or (
                self._options.is_capturing_single_frame()
                and self._options.is_capturing_rt_with_render_resolve_waiting()
            )
        ) and self.show_default_progress_window

    def _start_internal(self):
        # if we want preroll, then set timeline's current time back with the preroll frames' time,
        # and rely on timeline to do the preroll using the give timecode
        if self._options.preroll_frames > 0:
            self._timeline.set_current_time(self._start_time - self._options.preroll_frames / self._capture_fps)
        else:
            self._timeline.set_current_time(self._start_time)

        # initialize Reshade state for update loop
        self._reshade_switch_state = self.ReshadeUpdateState.PRE_CAPTURE

        # change timeline to be in play state
        self._timeline.play(
            start_timecode=self._start_time * self._capture_fps,
            end_timecode=self._end_time * self._capture_fps,
            looping=False,
        )

        # disable automatic time update in timeline so that movie capture tool can control time step
        self._timeline.set_auto_update(False)

        self._update_sub = carb.eventdispatcher.get_eventdispatcher().observe_event(
            event_name=omni.kit.app.GLOBAL_EVENT_UPDATE,
            on_event=self._on_update,
            order=1000000,
            observer_name="omni.kit.capture.viewport.extension.CaptureExtension",
        )

        self._is_adaptivesampling_stop_criterion_reached = False

        self._progress.start_capturing(
            self._total_frame_count, self._options.preroll_frames, self._options.capture_every_Nth_frames
        )

        if self._show_progress_window():
            self._progress_window.show(
                self._progress,
                self._options.is_capturing_single_frame(),
                show_pt_subframes=self._options.render_preset == CaptureRenderPreset.PATH_TRACE,
                show_pt_iterations=self._options.render_preset == CaptureRenderPreset.IRAY,
            )

        # prepare for application level capture
        if self._options.app_level_capture:
            # move the progress window to external window, and then hide application UI
            if self._show_progress_window():
                self._progress_window.move_to_external_window()
            self._settings.set("/app/window/hideUi", True)

        # timer for RT temporal effects to resolve
        self._time_waited_for_rt_render_resolve = 0.0

    def _record_and_set_iray_settings(self):
        if self._options.render_preset == CaptureRenderPreset.IRAY:
            self._saved_iray_sample_limit = self._settings.get_as_int("/rtx/iray/progressive_rendering_max_samples")
            self._settings.set("/rtx/iray/progressive_rendering_max_samples", self._options.path_trace_spp)

            self._saved_iray_render_sync_flag = self._settings.get_as_bool("/iray/render_synchronous")
            if not self._saved_iray_render_sync_flag:
                self._settings.set_bool("/iray/render_synchronous", True)

    def _restore_iray_settings(self):
        if self._options.render_preset == CaptureRenderPreset.IRAY:
            self._settings.set_bool("/iray/render_synchronous", self._saved_iray_render_sync_flag)
            self._settings.set("/rtx/iray/progressive_rendering_max_samples", self._saved_iray_sample_limit)

    def __save_mp4_encoding_settings(self):
        self._saved_mp4_encoding_bitrate = self._settings.get_as_int(MP4_ENCODING_BITRATE_SETTING)
        self._saved_mp4_encoding_iframe_interval = self._settings.get_as_int(MP4_ENCODING_IFRAME_INTERVAL_SETTING)
        self._saved_mp4_encoding_preset = self._settings.get(MP4_ENCODING_PRESET_SETTING)
        self._saved_mp4_encoding_profile = self._settings.get(MP4_ENCODING_PROFILE_SETTING)
        self._saved_mp4_encoding_rc_mode = self._settings.get(MP4_ENCODING_RC_MODE_SETTING)
        self._saved_mp4_encoding_rc_target_quality = self._settings.get(MP4_ENCODING_RC_TARGET_QUALITY_SETTING)
        self._saved_mp4_encoding_video_full_range_flag = self._settings.get(MP4_ENCODING_VIDEO_FULL_RANGE_SETTING)

    def __set_mp4_encoding_settings(self):
        self._settings.set(MP4_ENCODING_BITRATE_SETTING, self._options.mp4_encoding_bitrate)
        self._settings.set(MP4_ENCODING_IFRAME_INTERVAL_SETTING, self._options.mp4_encoding_iframe_interval)
        self._settings.set(MP4_ENCODING_PRESET_SETTING, self._options.mp4_encoding_preset)
        self._settings.set(MP4_ENCODING_PROFILE_SETTING, self._options.mp4_encoding_profile)
        self._settings.set(MP4_ENCODING_RC_MODE_SETTING, self._options.mp4_encoding_rc_mode)
        self._settings.set(MP4_ENCODING_RC_TARGET_QUALITY_SETTING, self._options.mp4_encoding_rc_target_quality)
        self._settings.set(MP4_ENCODING_VIDEO_FULL_RANGE_SETTING, self._options.mp4_encoding_video_full_range_flag)

    def _save_and_set_mp4_encoding_settings(self):
        if self._options.is_video():
            self.__save_mp4_encoding_settings()
            self.__set_mp4_encoding_settings()

    def _restore_mp4_encoding_settings(self):
        if self._options.is_video():
            self._settings.set(MP4_ENCODING_BITRATE_SETTING, self._saved_mp4_encoding_bitrate)
            self._settings.set(MP4_ENCODING_IFRAME_INTERVAL_SETTING, self._saved_mp4_encoding_iframe_interval)
            self._settings.set(MP4_ENCODING_PRESET_SETTING, self._saved_mp4_encoding_preset)
            self._settings.set(MP4_ENCODING_PROFILE_SETTING, self._saved_mp4_encoding_profile)
            self._settings.set(MP4_ENCODING_RC_MODE_SETTING, self._saved_mp4_encoding_rc_mode)
            self._settings.set(MP4_ENCODING_RC_TARGET_QUALITY_SETTING, self._saved_mp4_encoding_rc_target_quality)
            self._settings.set(MP4_ENCODING_VIDEO_FULL_RANGE_SETTING, self._saved_mp4_encoding_video_full_range_flag)

    def _save_and_set_application_capture_settings(self):
        # as in application capture mode, we actually capture the window size instead of the renderer output, thus we do this with two steps:
        # 1. set it to fill the viewport, and padding to (0, -1) to make viewport's size equals to application window size
        # 2. resize application window to the resolution that users set in movie capture, so that we can save the images with the desired resolution
        # this is not ideal because when we resize the application window, the size is actaully limited by the screen resolution so it's possible that
        # the resulting window size could be smaller than what we want.
        # also, it's more intuitive that padding should be (0, 0), but it has to be (0, -1) after tests as we still have 1 pixel left at top and bottom.
        if self._options.app_level_capture:
            vp_window = omni.ui.Workspace.get_window("Viewport")
            self._saved_viewport_padding_x = vp_window.padding_x
            self._saved_viewport_padding_y = vp_window.padding_y
            vp_window.padding_x = 0
            vp_window.padding_y = -1

            app_window_factory = omni.appwindow.acquire_app_window_factory_interface()
            app_window = app_window_factory.get_app_window()
            self._saved_app_window_size = app_window.get_size()
            app_window.resize(self._options.res_width, self._options._res_height)

    def _restore_application_capture_settings(self):
        if self._options.app_level_capture:
            vp_window = omni.ui.Workspace.get_window("Viewport")
            vp_window.padding_x = self._saved_viewport_padding_x
            vp_window.padding_y = self._saved_viewport_padding_y

            app_window_factory = omni.appwindow.acquire_app_window_factory_interface()
            app_window = app_window_factory.get_app_window()
            app_window.resize(self._saved_app_window_size[0], self._saved_app_window_size[1])

    def _set_vp_object_settings(self, viewport_api, restore: bool) -> None:
        action_module, action_key = "omni.kit.viewport.actions", "toggle_viewport_visibility"
        action_registry = omni.kit.actions.core.get_action_registry()
        action = action_registry.get_action(action_module, action_key)
        if not action:
            carb.log_error(f"Did not find {action_module}.{action_key}")
            return
        if restore == False:
            keys = (
                "guide/selection",
                "guide/grid",
                "guide/axis",  # Need to hide in legacy Viewport, but not in new one
                "scene/lights",
                "scene/audio",
                "scene/cameras",
                # "scene/skeletons" ?
            )
            # Run the action for all the types that must be hidden
            self.__restore_visible = action.execute(keys=keys, viewport_api=viewport_api, visible=False) or None
        elif self.__restore_visible:
            keys, self.__restore_visible = self.__restore_visible, None
            action.execute(keys=keys, viewport_api=viewport_api, visible=True)

    def _record_current_window_status(self, viewport_api):
        if self._viewport_api is None:
            carb.log_warn("No viewport, nothing to record")
            return

        self._saved_camera = viewport_api.camera_path
        self._saved_hydra_engine = viewport_api.hydra_engine
        self._saved_vp_updates_enabled = self._viewport_api.updates_enabled
        fv_setting_path = FILL_VIEWPORT_SETTING.format(viewport_api_id=self._viewport_api.id)
        self._saved_fill_viewport_option = self._settings.get(fv_setting_path)
        if self._saved_fill_viewport_option is None:
            self._saved_fill_viewport_option = self._settings.get_as_bool(FILL_VIEWPORT_DEFAULT)

        resolution = viewport_api.resolution
        self._saved_resolution_width = int(resolution[0])
        self._saved_resolution_height = int(resolution[1])
        self._saved_hd_engine = viewport_api.hydra_engine
        self._saved_render_mode = viewport_api.render_mode

        self._saved_capture_frame_viewport = self._settings.get("/persistent/app/captureFrame/viewport")
        self._saved_debug_material_type = self._settings.get_as_int("/rtx/debugMaterialType")
        self._saved_total_spp = self._settings.get_as_int("/rtx/pathtracing/totalSpp")
        self._saved_spp = self._settings.get_as_int("/rtx/pathtracing/spp")
        self._saved_reset_pt_accum_only = self._settings.get(
            "/rtx-transient/resetPtAccumOnlyWhenExternalFrameCounterChanges"
        )

        self._saved_async_rendering = self._settings.get("/app/asyncRendering")
        self._saved_async_renderingLatency = self._settings.get("/app/asyncRenderingLowLatency")
        self._saved_background_zero_alpha = self._settings.get("/rtx/post/backgroundZeroAlpha/enabled")
        self._saved_background_zero_alpha_comp = self._settings.get("/rtx/post/backgroundZeroAlpha/backgroundComposite")
        self._saved_background_zero_alpha_zp_first = self._settings.get(
            "/rtx/post/backgroundZeroAlpha/ApplyAlphaZeroPassFirst"
        )
        self._saved_background_zero_alpha_premultiply_color = self._settings.get(
            "/rtx/post/backgroundZeroAlpha/premultiplyColorByAlpha"
        )

        if self._options.movie_type == CaptureMovieType.SUNSTUDY:
            self._saved_sunstudy_current_time = self._options.sunstudy_current_time
        self._saved_timeline_current_time = self._timeline.get_current_time()
        self._saved_timeline_fps = self._timeline.get_time_codes_per_seconds()
        self._saved_rtx_sync_load_setting = self._settings.get("/rtx/materialDb/syncLoads")
        if self._to_capture_render_product:
            self._saved_render_product = viewport_api.render_product_path

        self._saved_hydra_sync_load_setting = self._settings.get("/rtx/hydra/materialSyncLoads")
        self._saved_async_texture_streaming = self._settings.get(
            "/rtx-transient/resourcemanager/texturestreaming/async"
        )
        self._saved_texture_streaming_budget = self._settings.get(
            "/rtx-transient/resourcemanager/texturestreaming/streamingBudgetMB"
        )
        self._saved_sampler_feedback_tile_size = self._settings.get_as_int("/rtx-transient/samplerFeedbackTileSize")
        self._saved_texture_streaming_eviction_frame_latency = self._settings.get_as_int(
            "/rtx-transient/resourcemanager/texturestreaming/evictionFrameLatency"
        )

        # save Reshade state in post process settings
        self._saved_reshade_state = bool(self._settings.get("/rtx/reshade/enable"))

        self._saved_output_alpha_in_composite = self._settings.get_as_bool(
            "/rtx/post/backgroundZeroAlpha/outputAlphaInComposite"
        )

        # save the visibility status of timeline window's minibar added in OM-92643
        self._saved_timeline_window_mimibar_visibility = self._settings.get_as_bool(
            "/exts/omni.kit.timeline.minibar/stay_on_playing"
        )

        # save the setting for sequencer camera, we want to enable it during capture
        self._saved_use_sequencer_camera = self._settings.get_as_bool(
            "/persistent/exts/omni.kit.window.sequencer/useSequencerCamera"
        )

        # if to capture mp4, save encoding settings
        self._save_and_set_mp4_encoding_settings()

        # if to capture in application mode, save viewport's padding values as we will reset it to make resolution of final image match what users set as possible as we can
        self._save_and_set_application_capture_settings()

    def _restore_window_status(self):
        if self._viewport_api is None:
            carb.log_warn("No viewport, nothing to restore")
            return
        if not self._saved_vp_updates_enabled:
            self._viewport_api.updates_enabled = self._saved_vp_updates_enabled

        if self._saved_fill_viewport_option:
            fv_setting_path = FILL_VIEWPORT_SETTING.format(viewport_api_id=self._viewport_api.id)
            self._settings.set(fv_setting_path, self._saved_fill_viewport_option)

        self._viewport_api.camera_path = self._saved_camera
        self._viewport_api.resolution = (self._saved_resolution_width, self._saved_resolution_height)
        if self._switch_renderer:
            self._viewport_api.set_hd_engine(self._saved_hydra_engine, self._saved_render_mode)

        self._settings.set_bool("/persistent/app/captureFrame/viewport", self._saved_capture_frame_viewport)
        self._settings.set_int("/rtx/debugMaterialType", self._saved_debug_material_type)
        self._settings.set_int("/rtx/pathtracing/totalSpp", self._saved_total_spp)
        self._settings.set_int("/rtx/pathtracing/spp", self._saved_spp)
        self._settings.set_bool(
            "/rtx-transient/resetPtAccumOnlyWhenExternalFrameCounterChanges", self._saved_reset_pt_accum_only
        )

        self._set_vp_object_settings(self._viewport_api, True)

        self._settings.set_bool("/app/asyncRendering", self._saved_async_rendering)
        self._settings.set_bool("/app/asyncRenderingLowLatency", self._saved_async_renderingLatency)
        self._renderer.set_capture_sync(not self._saved_async_rendering)
        self._settings.set_bool("/rtx/post/backgroundZeroAlpha/enabled", self._saved_background_zero_alpha)
        self._settings.set_bool(
            "/rtx/post/backgroundZeroAlpha/backgroundComposite", self._saved_background_zero_alpha_comp
        )
        self._settings.set_bool(
            "/rtx/post/backgroundZeroAlpha/ApplyAlphaZeroPassFirst", self._saved_background_zero_alpha_zp_first
        )
        self._settings.set_bool(
            "/rtx/post/backgroundZeroAlpha/premultiplyColorByAlpha", self._saved_background_zero_alpha_premultiply_color
        )

        self._restore_iray_settings()
        if self._options.movie_type == CaptureMovieType.SUNSTUDY:
            self._set_sunstudy_player_time(self._saved_sunstudy_current_time)
        self._settings.set("/rtx/materialDb/syncLoads", self._saved_rtx_sync_load_setting)
        self._settings.set("/rtx/hydra/materialSyncLoads", self._saved_hydra_sync_load_setting)
        self._settings.set("/rtx-transient/resourcemanager/texturestreaming/async", self._saved_async_texture_streaming)
        self._settings.set(
            "/rtx-transient/resourcemanager/texturestreaming/streamingBudgetMB", self._saved_texture_streaming_budget
        )
        self._settings.set("/rtx-transient/samplerFeedbackTileSize", self._saved_sampler_feedback_tile_size)
        self._settings.set(
            "/rtx-transient/resourcemanager/texturestreaming/evictionFrameLatency",
            self._saved_texture_streaming_eviction_frame_latency,
        )

        self._settings.set("/app/captureFrame/hdr", False)
        # tell timeline window it can restart force checks of end time
        self._settings.set_bool("/exts/omni.anim.window.timeline/playinRange", True)

        if self._to_capture_render_product:
            self._viewport_api.render_product_path = self._saved_render_product

        # set Reshade to its initial value it had before te capture:
        self._settings.set("/rtx/reshade/enable", self._saved_reshade_state)
        # set Reshade update loop state to initial value, so we're ready for the next run of the update loop:
        self._reshade_switch_state = self.ReshadeUpdateState.PRE_CAPTURE

        self._settings.set(
            "/rtx/post/backgroundZeroAlpha/outputAlphaInComposite", self._saved_output_alpha_in_composite
        )

        if self._saved_timeline_window_mimibar_visibility:
            self._setting.set(
                "/exts/omni.kit.timeline.minibar/stay_on_playing", self._saved_timeline_window_mimibar_visibility
            )

        self._settings.set(
            "/persistent/exts/omni.kit.window.sequencer/useSequencerCamera", self._saved_use_sequencer_camera
        )

        # if to capture mp4, restore encoding settings
        self._restore_mp4_encoding_settings()

        # if to capture in application mode, restore viewport's padding values
        self._restore_application_capture_settings()

    def _clean_pngs_in_directory(self, directory):
        self._clean_files_in_directory(directory, ".png")

    def _clean_files_in_directory(self, directory, suffix):
        images = os.listdir(directory)
        for item in images:
            if item.endswith(suffix):
                os.remove(os.path.join(directory, item))

    def _make_sure_directory_existed(self, directory):
        if not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
            except OSError as error:
                carb.log_warn(f"Directory cannot be created: {dir}")
                return False
        return True

    def _make_sure_directory_writeable(self, directory):
        if not self._make_sure_directory_existed(directory):
            return False

        # if the directory exists, try to create a test folder and then remove it to check if it's writeable
        # Normally this should be done using omni.client.stat api, unfortunately it won't work well if the
        # give folder is a read-only one mapped by O Drive.
        try:
            test_folder_name = "(@m#C$%^)((test^file$@@).testfile"
            full_test_path = os.path.join(directory, test_folder_name)
            f = open(full_test_path, "a")
            f.close()
            os.remove(full_test_path)
        except OSError as error:
            return False
        return True

    def _finish(self):
        if (
            self._progress.capture_status == CaptureStatus.FINISHING
            or self._progress.capture_status == CaptureStatus.CANCELLED
        ):
            if self.__post_process_wait > 0:
                self.__post_process_wait = self.__post_process_wait - 1
                return

            self._update_sub = None
            self._restore_window_status()
            self._sample_count = 0
            self._start_number = 0
            self._frame_counter = 0
            self._path_trace_iterations = 0

            # restore timeline settings
            # stop timeline, but re-enable auto update
            timeline = self._timeline
            timeline.set_auto_update(True)
            timeline.stop()

            self._timeline.set_current_time(self._saved_timeline_current_time)
            if self._capture_fps != self._saved_timeline_fps:
                self._timeline.set_time_codes_per_second(self._saved_timeline_fps)

            if self._to_capture_render_product and (
                self._render_product_path_for_capture != self._options.render_product
            ):
                RenderProductCaptureHelper.remove_render_product_for_capture(self._render_product_path_for_capture)

            # restore application ui if in application level capture mode
            if self._options.app_level_capture:
                self._settings.set("/app/window/hideUi", False)

            if self._show_progress_window():
                self._progress_window.close()

            if self._capture_finished_fn is not None:
                self._capture_finished_fn()

            self._progress.finish_capturing()

    def _wait_for_image_writing(self, seconds_to_wait: float = 5, seconds_to_sleep: float = 0.1):
        # wait for the last frame is written to disk
        # my tests of scenes of different complexity show a range of 0.2 to 1 seconds wait time
        # so 5 second max time should be enough and we can early quit by checking the last
        # frame every 0.1 seconds.
        seconds_tried = 0.0
        carb.log_info("Waiting for frames to be ready for encoding.")
        while seconds_tried < seconds_to_wait:
            if os.path.isfile(self._frame_path) and os.access(self._frame_path, os.R_OK):
                break
            else:
                time.sleep(seconds_to_sleep)
                seconds_tried += seconds_to_sleep

        if seconds_tried >= seconds_to_wait:
            carb.log_warn(f"Wait time out. To start encoding with images already have.")

    def _capture_image(self, frame_path: str):
        if self._options.app_level_capture:
            self._capture_application(frame_path)
        else:
            self._capture_viewport(frame_path)

    def _capture_application(self, frame_path: str):
        async def capture_frame(capture_filename: str):
            try:
                import omni.renderer_capture

                renderer_capture = omni.renderer_capture.acquire_renderer_capture_interface()
                renderer_capture.capture_next_frame_swapchain(capture_filename)
                carb.log_info(f"Capturing {capture_filename} in application level.")

            except ImportError:
                carb.log_error(f"Failed to capture {capture_filename} due to unable to import omni.renderer_capture.")

            await omni.kit.app.get_app().next_update_async()

        asyncio.ensure_future(capture_frame(frame_path))

    def _capture_viewport(self, frame_path: str):
        is_hdr = self.options._hdr_output
        render_product_path = self.options._render_product if self._to_capture_render_product else None
        format_desc = None
        if self._options.file_type == ".exr":
            format_desc = {}
            format_desc["format"] = "exr"
            format_desc["compression"] = self._options.exr_compression_method

        capture_viewport_to_file(
            self._viewport_api,
            file_path=frame_path,
            is_hdr=is_hdr,
            render_product_path=render_product_path,
            format_desc=format_desc,
        )
        carb.log_info(f"Capturing {frame_path}")

        # OMPE-24050: When scheduling a render-product capture, there needs to now
        # be an additional wait so that OmniGraph post-processing will be run
        #
        if render_product_path and (self._progress.capture_status == CaptureStatus.FINISHING):
            self.__post_process_wait = (
                self._settings.get("/exts/omni.kit.capture.viewport/renderProduct/waitFrames") or 0
            )

    def _get_current_frame_output_path(self):
        frame_path = ""
        if self._options.is_video():
            frame_path = get_num_pattern_file_path(
                self._frames_dir,
                self._options.file_name,
                self._options.file_name_num_pattern,
                self._frame,
                DEFAULT_IMAGE_FRAME_TYPE_FOR_VIDEO,
                self._options.renumber_negative_frame_number_from_0,
                abs(self._start_number),
            )
        else:
            if self._options.is_capturing_nth_frames():
                if self._frame_counter % self._options.capture_every_Nth_frames == 0:
                    frame_path = get_num_pattern_file_path(
                        self._frame_pattern_prefix,
                        self._options.file_name,
                        self._options.file_name_num_pattern,
                        self._frame,
                        self._options.file_type,
                        self._options.renumber_negative_frame_number_from_0,
                        abs(self._start_number),
                    )
            else:
                frame_path = self._frame_pattern_prefix + self._options.file_type
        return frame_path

    def _handle_skipping_frame(self, dt):
        if not self._options.overwrite_existing_frames:
            if os.path.exists(self._frame_path):
                carb.log_warn(f"Frame {self._frame_path} exists, skip it...")
                self._settings.set_int("/rtx/pathtracing/spp", 1)
                self._subframe = 0
                self._sample_count = 0
                self._path_trace_iterations = 0
                can_continue = True
                if self._forward_one_frame_fn is not None:
                    can_continue = self._forward_one_frame_fn(dt)
                elif self._options.movie_type == CaptureMovieType.SUNSTUDY and (
                    self._options.is_video() or self._options.is_capturing_nth_frames()
                ):
                    self._sunstudy_current_time += (
                        self._sunstudy_delta_time_per_iteration * self._sunstudy_iterations_per_frame
                    )
                    self._update_sunstudy_player_time()
                else:  # movie type is SEQUENCE
                    self._time = self._start_time + (self._frame - self._start_number) * self._time_rate
                    self._timeline.set_current_time(self._time)
                self._frame += 1
                self._frame_counter += 1

                # check if capture ends
                if self._forward_one_frame_fn is not None:
                    if can_continue is False:
                        if self._options.is_video():
                            self._progress.capture_status = CaptureStatus.TO_START_ENCODING
                        elif self._options.is_capturing_nth_frames():
                            self._progress.capture_status = CaptureStatus.FINISHING
                else:
                    if self._time >= self._end_time or self._frame_counter >= self._total_frame_count:
                        if self._options.is_video():
                            self._progress.capture_status = CaptureStatus.TO_START_ENCODING
                        elif self._options.is_capturing_nth_frames():
                            self._progress.capture_status = CaptureStatus.FINISHING

                return True
        else:
            if os.path.exists(self._frame_path) and self._last_skipped_frame_path != self._frame_path:
                carb.log_warn(f"Frame {self._frame_path} will be overwritten.")
                self._last_skipped_frame_path = self._frame_path
        return False

    def _get_default_settle_lateny_frames(self):
        # to workaround OM-40632, and OM-50514
        FRAMES_TO_DELAY_FOR_FRAME_SKIPPING_HACK = 5
        if self._options.render_preset in [CaptureRenderPreset.RAY_TRACE, CaptureRenderPreset.REAL_TIME_PATHTRACING]:
            return FRAMES_TO_DELAY_FOR_FRAME_SKIPPING_HACK
        elif (
            self._options.render_preset == CaptureRenderPreset.PATH_TRACE
            or self._options.render_preset == CaptureRenderPreset.IRAY
        ):
            pt_frames = self._options.ptmb_subframes_per_frame * self._options.path_trace_spp
            if pt_frames >= FRAMES_TO_DELAY_FOR_FRAME_SKIPPING_HACK:
                return 0
            else:
                return FRAMES_TO_DELAY_FOR_FRAME_SKIPPING_HACK - pt_frames
        else:
            return 0

    def _is_using_default_settle_latency_frames(self):
        return self._options.real_time_settle_latency_frames == 0 and self._settings.get(SEQUENCE_CAPTURE_WAIT) is None

    def _get_settle_latency_frames(self):
        settle_latency_frames = self._options.real_time_settle_latency_frames

        # Force a delay when capturing a range of frames
        if settle_latency_frames == 0 and (self._options.is_video() or self._options.is_capturing_nth_frames()):
            # Allow an explicit default to delay in SEQUENCE_CAPTURE_WAIT, when unset use logic below
            settle_latency_frames = self._settings.get(SEQUENCE_CAPTURE_WAIT)
            if settle_latency_frames is None:
                # Force a 4 frame delay when no sub-frames, otherwise account for sub-frames contributing to that 4
                settle_latency_frames = self._get_default_settle_lateny_frames()
                carb.log_info(f"Forcing {settle_latency_frames} frame delay per frame for sequence capture")

        return settle_latency_frames

    def _is_handling_settle_latency_frames(self):
        return (
            (self._options.is_video() or self._options.is_capturing_nth_frames())
            and self._settle_latency_frames > 0
            and self._real_time_settle_latency_frames_done < self._settle_latency_frames
        )

    def _handle_real_time_capture_settle_latency(self):
        # settle latency only works with sequence capture
        if not (self._options.is_video() or self._options.is_capturing_nth_frames()):
            return False

        # settle_latency_frames conflicts with the waiting time for RT's temporal effect resolve
        # so don't do it if option.rt_wait_for_render_resolve_in_seconds is specified.
        # Otherwise users will get the long waiting time for every settle latency frame, which is undesirable and a waste of perf
        if self._options.is_capturing_rt_with_render_resolve_waiting():
            # warn to notify users if they set the settle latency frames option delibrately
            if self._options.real_time_settle_latency_frames > 0:
                carb.log_warn(
                    "For Ray Trace capture, settle latency frames option will be ignored if the wait for render resolve option is set."
                )
            return False

        if self._settle_latency_frames > 0:
            self._real_time_settle_latency_frames_done += 1
            if self._real_time_settle_latency_frames_done >= self._settle_latency_frames:
                self._real_time_settle_latency_frames_done = 0
                return False
            else:
                self._subframe = 0
                self._sample_count = 0
                return True
        return False

    def _wait_for_rt_frame_to_resolve(self, dt):
        if self._options.render_preset != CaptureRenderPreset.RAY_TRACE:
            return False

        self._time_waited_for_rt_render_resolve += dt
        if self._time_waited_for_rt_render_resolve < self._options.rt_wait_for_render_resolve_in_seconds:
            return True
        else:
            self._time_waited_for_rt_render_resolve = 0.0
            return False

    def _is_capturing_pt_mb(self):
        return (
            CaptureRenderPreset.PATH_TRACE == self._options.render_preset and self._options.ptmb_subframes_per_frame > 1
        )

    def _is_capturing_pt_no_mb(self):
        return (
            CaptureRenderPreset.PATH_TRACE == self._options.render_preset
            and 1 == self._options.ptmb_subframes_per_frame
        )

    def _set_totalspp_for_normal_capture(self) -> None:
        # For motion blur, set totalSpp to 0 to ensure we accumulate as many samples as requested even across subframes
        # for non-motion blur path trace capture, we now rely on adaptive sampling's return status to decide if it's still
        # need to do more samples
        self._settings.set_int(
            "/rtx/pathtracing/totalSpp", 0 if self._is_capturing_pt_mb() else self._options.path_trace_spp
        )

    def _is_pt_adaptivesampling_stop_criterion_reached(self):
        if self._viewport_api is None:
            return False
        else:
            render_status = self._viewport_api.frame_info.get("status")
            return (
                render_status is not None
                and RenderStatus.eStopCriterionReached == render_status
                and self._is_capturing_pt_no_mb()
            )

    def _check_if_frame_time_limit_reached(self, dt: float):
        if self._options.early_quit_time_limit_per_frame_in_minutes <= 0:
            return

        current_frame_time_in_minutes = (self._progress._current_frame_time + dt) / 60
        if current_frame_time_in_minutes > self._options.early_quit_time_limit_per_frame_in_minutes:
            carb.log_warn(
                f"Current frame's capture time has reached its cap: \
                          {current_frame_time_in_minutes} > {self._options.early_quit_time_limit_per_frame_in_minutes} (minutes).\
                          \nMovie capture will force quit the application to allow it to be rerun."
            )
            self.cancel()
            self._settings.set("/app/file/ignoreUnsavedOnExit", True)
            self._settings.set("/app/file/ignoreUnsavedStage", True)
            self._settings.set("/app/fastShutdown", True)
            omni.kit.app.get_app().post_quit(1)

    def _on_update(self, e: carb.eventdispatcher.Event):
        dt = e["dt"]

        if self._progress.capture_status == CaptureStatus.FINISHING:
            # need to turn reshade off, update, and turn on again in _restore_window_status to apply pre-capture resolution
            if self._reshade_switch_state == self.ReshadeUpdateState.POST_CAPTURE:
                self._settings.set_bool("/rtx/reshade/enable", False)
                self._reshade_switch_state = self.ReshadeUpdateState.POST_CAPTURE_READY
                return
            self._finish()
            self._update_progress_hook()
        elif self._progress.capture_status == CaptureStatus.CANCELLED:
            # need to turn reshade off, update, and turn on again in _restore_window_status to apply pre-capture resolution
            if self._reshade_switch_state == self.ReshadeUpdateState.POST_CAPTURE:
                self._settings.set_bool("/rtx/reshade/enable", False)
                self._reshade_switch_state = self.ReshadeUpdateState.POST_CAPTURE_READY
                return
            carb.log_warn("video recording cancelled")
            self._update_progress_hook()
            self._finish()
        elif self._progress.capture_status == CaptureStatus.ENCODING:
            if VideoGenerationHelper().encoding_done:
                self._progress.capture_status = CaptureStatus.FINISHING
            self._update_progress_hook()
            self._progress.add_encoding_time(dt)
        elif self._progress.capture_status == CaptureStatus.TO_START_ENCODING:
            if VideoGenerationHelper().is_encoding is False:
                self._wait_for_image_writing()
                if self._options.renumber_negative_frame_number_from_0 is True and self._start_number < 0:
                    video_frame_start_num = 0
                else:
                    video_frame_start_num = self._start_number
                started = VideoGenerationHelper().generating_video(
                    self._video_name,
                    self._frames_dir,
                    self._options.file_name,
                    self._options.file_name_num_pattern,
                    video_frame_start_num,
                    self._total_frame_count,
                    self._options.fps,
                )
                if started:
                    self._progress.capture_status = CaptureStatus.ENCODING
                    self._update_progress_hook()
                    self._progress.add_encoding_time(dt)
                else:
                    carb.log_warn("Movie capture failed to encode the capture images.")
                    self._progress.capture_status = CaptureStatus.FINISHING
        elif self._progress.capture_status == CaptureStatus.CAPTURING:

            # Farm render jobs running excessive amount of time need to quit earlier and be rerun
            self._check_if_frame_time_limit_reached(dt)

            if self._frames_to_disable_async_rendering >= 0:
                self._frames_to_disable_async_rendering -= 1
                return

            # apply Reshade and skip frames to to pick up capturing resolution
            if self._reshade_switch_state == self.ReshadeUpdateState.PRE_CAPTURE:
                self._settings.set_bool("/rtx/reshade/enable", self._saved_reshade_state)
                # need to skip a couple of updates for Reshade settings to apply:
                if self._frames_to_apply_reshade >= 0:
                    self._frames_to_apply_reshade = self._frames_to_apply_reshade - 1
                    return
                self._reshade_switch_state = self.ReshadeUpdateState.POST_CAPTURE
                return

            if self._progress.is_prerolling():
                self._progress.prerolled_frames += 1
                self._settings.set_int("/rtx/pathtracing/spp", 1)
                left_preroll_frames = self._options.preroll_frames - self._progress.prerolled_frames
                self._timeline.set_current_time(self._start_time - left_preroll_frames / self._capture_fps)
                return

            self._frame_path = self._get_current_frame_output_path()
            if self._frame_path and self._frame_path not in self._frame_paths:
                self._frame_paths.append(self._frame_path)

            if self._handle_skipping_frame(dt):
                self._progress.add_frame_time(self._frame, dt)
                self._update_progress_hook()
                return

            # if it's capturing every nth frame, we want better performance by rendering the frames we don't want fast
            subframes_per_frame = self._options.ptmb_subframes_per_frame
            path_trace_spp = self._options.path_trace_spp
            if (
                self._options.is_capturing_nth_frames()
                and self._options.capture_every_Nth_frames > 1
                and self._frame_counter % self._options.capture_every_Nth_frames != 0
            ):
                path_trace_spp = 1
                self._settings.set_int("/rtx/pathtracing/totalSpp", path_trace_spp)
                subframes_per_frame = 1
            else:
                self._set_totalspp_for_normal_capture()

            self._settings.set_int("/rtx/pathtracing/spp", min(self._options.spp_per_iteration, path_trace_spp))

            if self._options.render_preset == CaptureRenderPreset.IRAY:
                iterations_done = int(self._settings.get("/iray/progression"))
                self._path_trace_iterations = iterations_done
                self._sample_count = iterations_done
            else:
                self._sample_count += self._options.spp_per_iteration
                self._path_trace_iterations = self._sample_count
            self._timeline.set_prerolling(False)
            self._settings.set_int("/rtx/externalFrameCounter", self._frame)

            # update progress timers
            if self._options.is_capturing_single_frame():
                if (
                    self._options.render_preset == CaptureRenderPreset.PATH_TRACE
                    or self._options.is_capturing_rt_with_render_resolve_waiting()
                ):
                    self._progress.add_single_frame_capture_time_for_pt(self._subframe, subframes_per_frame, dt)
                elif self._options.render_preset == CaptureRenderPreset.IRAY:
                    self._progress.add_single_frame_capture_time_for_iray(
                        self._subframe, subframes_per_frame, self._path_trace_iterations, path_trace_spp, dt
                    )
                else:
                    carb.log_info(
                        f"Movie capture: we don't support progress for {self._options.render_preset} in single frame capture mode."
                    )
            else:
                self._progress.add_frame_time(
                    self._frame,
                    dt,
                    self._subframe + 1,
                    subframes_per_frame,
                    self._path_trace_iterations,
                    path_trace_spp,
                    self._is_handling_settle_latency_frames() and not self._is_using_default_settle_latency_frames(),
                    self._real_time_settle_latency_frames_done,
                    self._settle_latency_frames,
                )
                self._update_progress_hook()

            # check if path trace and meet the samples per pixels stop criterion
            render_status = self._viewport_api.frame_info.get("status")
            if RenderStatus.eStopCriterionReached == render_status and self._is_adaptivesampling_stop_criterion_reached:
                carb.log_info(
                    "Got continuous path tracing adaptive sampling stop criterion reached event, skip this frame for it to finish."
                )
                # Doesn't apply the early stop of adaptive samples to settle latency frames
                if not self._is_handling_settle_latency_frames():
                    return
            self._is_adaptivesampling_stop_criterion_reached = self._is_pt_adaptivesampling_stop_criterion_reached()

            # capture frame when we reach the sample count for this frame and are rendering the last subframe
            # Note _sample_count can go over _samples_per_pixel when 'spp_per_iteration > 1'
            # also handle the case when we have adaptive sampling enabled and it returns stop criterion reached
            if (
                (self._sample_count >= path_trace_spp)
                and (self._subframe == subframes_per_frame - 1)
                or self._is_adaptivesampling_stop_criterion_reached
            ):
                if self._handle_real_time_capture_settle_latency():
                    return

                if self._wait_for_rt_frame_to_resolve(dt):
                    # # # carb.log_warn(f"Keep waiting for rt frame to resolve: {self._time_waited_for_rt_render_resolve}/{self._options.rt_wait_for_render_resolve_in_seconds}")
                    return

                if self._options.is_video():
                    self._capture_image(self._frame_path)
                else:
                    if self._options.is_capturing_nth_frames():
                        if self._frame_counter % self._options.capture_every_Nth_frames == 0:
                            self._capture_image(self._frame_path)
                    else:
                        self._progress.capture_status = CaptureStatus.FINISHING
                        self._capture_image(self._frame_path)

            # reset time the *next frame* (since otherwise we capture the first sample)
            if self._sample_count >= path_trace_spp or self._is_adaptivesampling_stop_criterion_reached:
                self._sample_count = 0
                self._path_trace_iterations = 0
                self._subframe += 1
                if self._subframe == subframes_per_frame:
                    self._subframe = 0
                    self._frame += 1
                    self._frame_counter += 1

                self._time = self._start_time + (self._frame - self._start_number) * self._time_rate

                can_continue = False
                if self._forward_one_frame_fn is not None:
                    can_continue = self._forward_one_frame_fn(dt)
                elif self._options.movie_type == CaptureMovieType.SUNSTUDY and (
                    self._options.is_video() or self._options.is_capturing_nth_frames()
                ):
                    self._sunstudy_current_time += self._sunstudy_delta_time_per_iteration
                    self._update_sunstudy_player_time()
                else:
                    if self._options.is_video() or self._options.is_capturing_nth_frames():
                        cur_time = (
                            self._time
                            + (self._options.ptmb_fso * self._time_rate)
                            + self._time_subframe_rate * self._subframe
                        )
                        self._timeline.set_current_time(cur_time)

                if self._forward_one_frame_fn is not None:
                    if can_continue == False:
                        if self._options.is_video():
                            self._progress.capture_status = CaptureStatus.TO_START_ENCODING
                        elif self._options.is_capturing_nth_frames():
                            self._progress.capture_status = CaptureStatus.FINISHING
                else:
                    if self._time >= self._end_time or self._frame_counter >= self._total_frame_count:
                        if self._options.is_video():
                            self._progress.capture_status = CaptureStatus.TO_START_ENCODING
                        elif self._options.is_capturing_nth_frames():
                            self._progress.capture_status = CaptureStatus.FINISHING

    def get_outputs(self) -> List[str]:
        """Gets output file names from the completed capture.

        Returns:
            List[str]: List of output file names generated during capture.
        """
        if not self.done:
            carb.log_warn("Capture not done, no output files")
            return []

        if self._options.is_video():
            return [self._options.get_full_path()]

        def _get_outputs_from_frame_path(frame_path, aovs) -> List[str]:
            if self.options._render_product:
                # For render product, not all aovs will generate capture file
                # Check one by one to get the real output files
                frame_output_files = []
                base_name = frame_path[: -len(self._options.file_type)]
                for aov in aovs:
                    file_name = f"{base_name}_{aov}{self._options.file_type}"
                    result, _ = omni.client.stat(file_name)
                    if result == omni.client.Result.OK:
                        frame_output_files.append(file_name)
                return frame_output_files
            else:
                return [frame_path]

        output_files = []

        aovs = []
        if self.options._render_product:
            stage = self._viewport_api.stage
            prim = stage.GetPrimAtPath(self._options.render_product)
            product = UsdRender.Product(prim)
            renderVars = product.GetOrderedVarsRel().GetForwardedTargets()
            for renderVar in renderVars:
                aovName = stage.GetPrimAtPath(renderVar).GetAttribute("sourceName").Get()
                aovs.append(aovName)

        for frame_path in self._frame_paths:
            output_files.extend(_get_outputs_from_frame_path(frame_path, aovs))
        return output_files

    @staticmethod
    def get_instance():
        """Gets the current instance of the capture extension.

        Returns:
            CaptureExtension: The current capture extension instance.
        """
        global capture_instance
        return capture_instance
