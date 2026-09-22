# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import os
from enum import Enum, IntEnum
import carb


class CaptureMovieType(IntEnum):
    """An enumeration for movie capture types.

    This enum defines the modes available for capturing movies. Use SEQUENCE to capture a series of individual frames and SUNSTUDY to capture a movie based on sun study settings.

    Constants:
        SEQUENCE (int): Captures a sequence of frames as still images.
        SUNSTUDY (int): Captures a movie that incorporates sun study parameters.

    Example:
    .. code-block:: python

        movie_type = CaptureMovieType.SEQUENCE
    """

    SEQUENCE = 0
    SUNSTUDY = 1


class CaptureRangeType(IntEnum):
    """An enumeration that defines the method for specifying a capture range. Use FRAMES when the capture range is determined by frame numbers, and use SECONDS when it is determined by time in seconds."""

    FRAMES = 0
    SECONDS = 1


class CaptureRenderPreset(IntEnum):
    """A set of render presets for capture operations.

    This enumeration defines the rendering methods available during capture sessions in Omni UI. Each preset controls a different rendering approach, allowing users to select the method best suited for quality and performance requirements.

    Members:
        PATH_TRACE: Use a full path-tracing method for high-quality output.
        RAY_TRACE: Use ray tracing to produce realistic lighting and shadow effects.
        IRAY: Use the IRay rendering technique for interactive quality and efficiency.
        REAL_TIME_PATHTRACING: Use real-time path tracing to balance performance with visual fidelity.

    Example:
    .. code-block:: python

        preset = CaptureRenderPreset.PATH_TRACE
    """

    PATH_TRACE = 0
    RAY_TRACE = 1
    IRAY = 2
    REAL_TIME_PATHTRACING = 3


class CaptureDebugMaterialType(IntEnum):
    """Enum representing the debug material type for capture workflows.

    This enum defines two options that determine how materials are rendered when capturing debug images. The SHADED option uses the normal shading of the scene, providing a realistic look. The WHITE option renders the material in white, which can help emphasize object shapes and structures.

    Use this enum within capture settings to select the desired debug material representation.
    """

    SHADED = 0
    WHITE = 1


OUTPUT_FILE_TYPES = {".png", ".tga", ".exr", ".mp4"}


EXR_COMPRESSION_METHODS = {"zip", "zips", "dwaa", "dwab", "piz", "rle", "b44", "b44a"}
MP4_ENCODING_PRESETS = {
    "PRESET_DEFAULT",
    "PRESET_HP",
    "PRESET_HQ",
    "PRESET_BD",
    "PRESET_LOW_LATENCY_DEFAULT",
    "PRESET_LOW_LATENCY_HQ",
    "PRESET_LOW_LATENCY_HP",
    "PRESET_LOSSLESS_DEFAULT",
    "PRESET_LOSSLESS_HP",
}
MP4_ENCODING_PROFILES = {
    "H264_PROFILE_BASELINE",
    "H264_PROFILE_MAIN",
    "H264_PROFILE_HIGH",
    "H264_PROFILE_HIGH_444",
    "H264_PROFILE_STEREO",
    "H264_PROFILE_SVC_TEMPORAL_SCALABILITY",
    "H264_PROFILE_PROGRESSIVE_HIGH",
    "H264_PROFILE_CONSTRAINED_HIGH",
    "HEVC_PROFILE_MAIN",
    "HEVC_PROFILE_MAIN10",
    "HEVC_PROFILE_FREXT",
}
MP4_ENCODING_RC_MODES = {"RC_CONSTQP", "RC_VBR", "RC_CBR", "RC_CBR_LOWDELAY_HQ", "RC_CBR_HQ", "RC_VBR_HQ"}


class CaptureOptions:
    """All Capture options that will be used when capturing.

    Note: When adding an attribute, make sure it is exposed via the constructor.
    Not doing so will cause errors when serializing and deserializing this object.

    Args:
        camera (str): The camera used for capture. Default goes to "camera".
        range_type (CaptureRangeType): The capture range type. Default goes to CaptureRangeType.FRAMES.
        capture_every_nth_frames (int): The number of frames to capture every nth frame. Default goes to -1.
        fps (int): The frames per second to capture. Default goes to 24.
        start_frame (int): The start frame number, only available with CaptureRangeType.FRAMES. Default goes to 1.
        end_frame (int): The end frame number, only available with CaptureRangeType.FRAMES. Default goes to 48.
        start_time (float): The start time, only available with CaptureRangeType.SECONDS. Default goes to 0.
        end_time (float): The end time, only available with CaptureRangeType.SECONDS. Default goes to 2.
        res_width (int): The width of the capture resolution. Default goes to 1920.
        res_height (int): The height of the capture resolution. Default goes to 1080.
        render_preset (CaptureRenderPreset): The render preset to use. Default goes to CaptureRenderPreset.PATH_TRACE.
        debug_material_type (CaptureDebugMaterialType): The debug material type to use. Default goes to CaptureDebugMaterialType.SHADED.
        spp_per_iteration (int): The number of samples per pixel per iteration. Default goes to 1.
        path_trace_spp (int): The number of Path Tracing samples per pixel. Default goes to 1.
        ptmb_subframes_per_frame (int): The number of Path Tracing motion blur subframes per frame. Default goes to 1.
        ptmb_fso (float): The Path Tracing motion blur frame shutter open. Default goes to 0.0.
        ptmb_fsc (float): The Path Tracing motion blur frame shutter close. Default goes to 1.0.
        output_folder (str): The output folder. Default goes to "".
        file_name (str): The file name. Default goes to "Capture".
        file_name_num_pattern (str): The file name number pattern. Default goes to ".####".
        file_type (str): The file type. Default goes to ".png".
        save_alpha (bool): Whether to save the alpha channel. Default goes to False.
        hdr_output (bool): Whether to output an HDR image. Default goes to False.
        show_pathtracing_single_frame_progress (bool): Whether to show the Path Tracing single frame progress. Default goes to False.
        preroll_frames (int): The number of preroll frames. Default goes to 0.
        overwrite_existing_frames (bool): Whether to overwrite existing frame images. Default goes to False.
        movie_type (CaptureMovieType): The movie type. Default goes to CaptureMovieType.SEQUENCE.
        sunstudy_start_time (float): The start time of the sun study. Default goes to 0.0.
        sunstudy_current_time (float): The current time of the sun study. Default goes to 0.0.
        sunstudy_end_time (float): The end time of the sun study. Default goes to 0.0.
        sunstudy_movie_length_in_seconds (float): The length of the sun study movie. Default goes to 2.0.
        sunstudy_player: The sun study player. Default goes to None.
        real_time_settle_latency_frames (int): The number of real time settle latency frames. Default goes to 0.
        renumber_negative_frame_number_from_0 (bool): Whether to renumber negative frame numbers from 0. Default goes to False.
        render_product (str): The render product used for capture. Default goes to "".
        exr_compression_method (str): The compression method for EXR files. Default goes to "zips".
        mp4_encoding_bitrate (int): The bitrate for MP4 encoding. Default goes to 16777216.
        mp4_encoding_iframe_interval (int): The interval for MP4 encoding. Default goes to 60.
        mp4_encoding_preset (str): The preset for MP4 encoding. Default goes to "PRESET_DEFAULT".
        mp4_encoding_profile (str): The profile for MP4 encoding. Default goes to "H264_PROFILE_HIGH".
        mp4_encoding_rc_mode (str): The rate control mode for MP4 encoding. Default goes to "RC_VBR".
        mp4_encoding_rc_target_quality (int): The target quality for MP4 encoding. Default goes to 0.
        mp4_encoding_video_full_range_flag (bool): Whether to use full range video. Default goes to False.
        app_level_capture (bool): Whether to capture all scene elements. Default goes to False.
        animation_fps (float): The animation frames per second. Default goes to -1.
        rt_wait_for_render_resolve_in_seconds (int): The number of seconds to wait for the render resolve. Default goes to -1.
        early_quit_time_limit_per_frame_in_minutes (int): Capture time limitation for a single frame. Quit application if reached. Default goes to -1.
    """

    INVALID_ANIMATION_FPS = -1

    def __init__(
        self,
        camera="camera",
        range_type=CaptureRangeType.FRAMES,
        capture_every_nth_frames=-1,
        fps=24,
        start_frame=1,
        end_frame=48,
        start_time=0,
        end_time=2,
        res_width=1920,
        res_height=1080,
        render_preset=CaptureRenderPreset.PATH_TRACE,
        debug_material_type=CaptureDebugMaterialType.SHADED,
        spp_per_iteration=1,
        path_trace_spp=1,
        ptmb_subframes_per_frame=1,
        ptmb_fso=0.0,
        ptmb_fsc=1.0,
        output_folder="",
        file_name="Capture",
        file_name_num_pattern=".####",
        file_type=".png",
        save_alpha=False,
        hdr_output=False,
        show_pathtracing_single_frame_progress=False,
        preroll_frames=0,
        overwrite_existing_frames=False,
        movie_type=CaptureMovieType.SEQUENCE,
        sunstudy_start_time=0.0,
        sunstudy_current_time=0.0,
        sunstudy_end_time=0.0,
        sunstudy_movie_length_in_seconds=2,
        sunstudy_player=None,
        real_time_settle_latency_frames=0,
        renumber_negative_frame_number_from_0=False,
        render_product="",
        exr_compression_method="zips",
        mp4_encoding_bitrate=16777216,
        mp4_encoding_iframe_interval=60,
        mp4_encoding_preset="PRESET_DEFAULT",
        mp4_encoding_profile="H264_PROFILE_HIGH",
        mp4_encoding_rc_mode="RC_VBR",
        mp4_encoding_rc_target_quality=0,
        mp4_encoding_video_full_range_flag=False,
        app_level_capture=False,
        animation_fps=INVALID_ANIMATION_FPS,
        rt_wait_for_render_resolve_in_seconds=-1,
        early_quit_time_limit_per_frame_in_minutes=-1,
    ):
        """Initializes a new CaptureOptions instance with default capture properties."""
        self._camera = camera
        self._range_type = range_type
        self._capture_every_nth_frames = capture_every_nth_frames
        self._fps = fps
        self._start_frame = start_frame
        self._end_frame = end_frame
        self._start_time = start_time
        self._end_time = end_time
        self._res_width = res_width
        self._res_height = res_height
        self._render_preset = render_preset
        self._debug_material_type = debug_material_type
        self._spp_per_iteration = spp_per_iteration
        self._path_trace_spp = path_trace_spp
        self._ptmb_subframes_per_frame = ptmb_subframes_per_frame
        self._ptmb_fso = ptmb_fso
        self._ptmb_fsc = ptmb_fsc
        self._output_folder = output_folder
        self._file_name = file_name
        self._file_name_num_pattern = file_name_num_pattern
        self._file_type = file_type
        self._save_alpha = save_alpha
        self._hdr_output = hdr_output
        self._show_pathtracing_single_frame_progress = show_pathtracing_single_frame_progress
        self._preroll_frames = preroll_frames
        self._overwrite_existing_frames = overwrite_existing_frames
        self._movie_type = movie_type
        self._sunstudy_start_time = sunstudy_start_time
        self._sunstudy_current_time = sunstudy_current_time
        self._sunstudy_end_time = sunstudy_end_time
        self._sunstudy_movie_length_in_seconds = sunstudy_movie_length_in_seconds
        self._sunstudy_player = sunstudy_player
        self._real_time_settle_latency_frames = real_time_settle_latency_frames
        self._renumber_negative_frame_number_from_0 = renumber_negative_frame_number_from_0
        self._render_product = render_product
        self.exr_compression_method = exr_compression_method
        self.mp4_encoding_bitrate = mp4_encoding_bitrate
        self.mp4_encoding_iframe_interval = mp4_encoding_iframe_interval
        self.mp4_encoding_preset = mp4_encoding_preset
        self.mp4_encoding_profile = mp4_encoding_profile
        self.mp4_encoding_rc_mode = mp4_encoding_rc_mode
        self.mp4_encoding_rc_target_quality = mp4_encoding_rc_target_quality
        self.mp4_encoding_video_full_range_flag = mp4_encoding_video_full_range_flag
        self._app_level_capture = app_level_capture
        self._animation_fps = animation_fps
        self._rt_wait_for_render_resolve_in_seconds = rt_wait_for_render_resolve_in_seconds
        self._early_quit_time_limit_per_frame_in_minutes = early_quit_time_limit_per_frame_in_minutes

    def to_dict(self):
        """Converts the CaptureOptions to a dictionary of attribute names and values.

        Returns:
            dict: Dictionary representation of capture options.
        """
        data = vars(self)
        return {key.lstrip("_"): value for key, value in data.items()}

    @classmethod
    def from_dict(cls, options):
        """Creates a CaptureOptions instance from a dictionary.

        Args:
            cls (type): Reference to the CaptureOptions class.
            options (dict): Dictionary containing capture option attributes.

        Returns:
            CaptureOptions: New capture options instance.
        """
        return cls(**options)

    @property
    def camera(self) -> str:
        """Gets the camera used for capture.

        Returns:
            str: The camera value.
        """
        return self._camera

    @camera.setter
    def camera(self, value: str):
        """Sets the camera used for capture.

        Args:
            value (str): Camera value to set.
        """
        self._camera = value

    @property
    def range_type(self) -> CaptureRangeType:
        """Gets the range_type property.

        Returns:
            CaptureRangeType: The range type.
        """
        return self._range_type

    @range_type.setter
    def range_type(self, value: int):
        """Sets the range_type property.

        Args:
            value (int): New range type.
        """
        if value in list(CaptureRangeType):
            self._range_type = value
        else:
            carb.log_warn(
                f"Failed to set range type to {value} as it is not supported. Supported values are {list(CaptureRangeType)}"
            )

    @property
    def capture_every_Nth_frames(self) -> int:
        """Gets the capture_every_Nth_frames property.

        Returns:
            int: The capture every nth frames value.
        """
        return self._capture_every_nth_frames

    @capture_every_Nth_frames.setter
    def capture_every_Nth_frames(self, value: int):
        """Sets the capture_every_Nth_frames property.

        Args:
            value (int): New capture every nth frames value.
        """
        self._capture_every_nth_frames = value

    @property
    def fps(self) -> float:
        """Gets the fps property.

        Returns:
            float: The fps value.
        """
        return self._fps

    @fps.setter
    def fps(self, value: float):
        """Sets the fps property.

        Args:
            value (float): New fps value.
        """
        if value <= 0:
            carb.log_warn(f"Failed to set FPS to {value} as it needs to be a positive number.")
        else:
            self._fps = value

    @property
    def start_frame(self) -> int:
        """Capture start frame number, only available with CaptureRangeType.FRAMES.

        Returns:
            int: Capture start frame number.
        """
        return self._start_frame

    @start_frame.setter
    def start_frame(self, value: int):
        """Sets the start_frame property.

        Args:
            value (int): Capture start frame number.
        """
        self._start_frame = value

    @property
    def end_frame(self) -> int:
        """Capture end frame number, only available with CaptureRangeType.FRAMES.

        Returns:
            int: Capture end frame number.
        """
        return self._end_frame

    @end_frame.setter
    def end_frame(self, value: int):
        """Sets the end_frame property.

        Args:
            value (int): Capture end frame number.
        """
        self._end_frame = value

    @property
    def start_time(self) -> float:
        """Capture start time, only available with CaptureRangeType.SECONDS.

        Returns:
            float: Capture start time.
        """
        return self._start_time

    @start_time.setter
    def start_time(self, value: float):
        """Sets the start_time property.

        Args:
            value (float): New start time value.
        """
        self._start_time = value

    @property
    def end_time(self) -> float:
        """Capture end time, only available with CaptureRangeType.SECONDS.

        Returns:
            float: Capture end time.
        """
        return self._end_time

    @end_time.setter
    def end_time(self, value: float):
        """Sets the end_time property.

        Args:
            value (float): New end time value.
        """
        self._end_time = value

    @property
    def res_width(self) -> int:
        """Gets resolution width.

        Returns:

            int: The resolution width.
        """
        return self._res_width

    @res_width.setter
    def res_width(self, value: int):
        """Sets the res_width property.

        Args:
            value (int): New resolution width value.
        """
        if value <= 0:
            carb.log_warn(f"Failed to set resolution width to {value} as it needs to be a positive number.")
        else:
            self._res_width = value

    @property
    def res_height(self) -> int:
        """Gets resolution height.

        Returns:

            int: The resolution height.
        """
        return self._res_height

    @res_height.setter
    def res_height(self, value: int):
        """Sets resolution height.

        Args:

            value (int): The resolution height to set.
        """
        if value <= 0:
            carb.log_warn(f"Failed to set resolution height to {value} as it needs to be a positive number.")
        else:
            self._res_height = value

    @property
    def render_preset(self) -> CaptureRenderPreset:
        """Gets render preset.

        Returns:

            CaptureRenderPreset: The current render preset.
        """
        return self._render_preset

    @render_preset.setter
    def render_preset(self, value: CaptureRenderPreset):
        """Sets render preset.

        Args:

            value (CaptureRenderPreset): The render preset value to set.
        """
        if value in list(CaptureRenderPreset):
            self._render_preset = value
        else:
            carb.log_warn(
                f"Failed to set render preset as {value} is not supported. Supported values are {list(CaptureRenderPreset)}."
            )

    @property
    def debug_material_type(self) -> CaptureDebugMaterialType:
        """Gets debug material type.

        Returns:

            CaptureDebugMaterialType: The current debug material type.
        """
        return self._debug_material_type

    @debug_material_type.setter
    def debug_material_type(self, value: CaptureDebugMaterialType):
        """Sets debug material type.

        Args:

            value (CaptureDebugMaterialType): The debug material type value to set.
        """
        if value in list(CaptureDebugMaterialType):
            self._debug_material_type = value
        else:
            carb.log_warn(
                f"Failed to set debug material type as {value} is not supported. Supported values are {list(CaptureDebugMaterialType)}."
            )

    @property
    def spp_per_iteration(self) -> int:
        """Gets the number of samples per pixel per iteration.

        Returns:

            int: The current samples per iteration.
        """
        return self._spp_per_iteration

    @spp_per_iteration.setter
    def spp_per_iteration(self, value: int):
        """Sets the number of samples per pixel per iteration.

        Args:

            value (int): The samples per iteration value to set.
        """
        if value > 0:
            self._spp_per_iteration = value
        else:
            carb.log_warn(
                f"Failed to set samples per pixel per iteration to {value} as it needs to be a positive number."
            )

    @property
    def path_trace_spp(self) -> int:
        """Gets the number of Path Tracing samples per pixel.

        Returns:

            int: The current path trace samples per pixel.
        """
        return self._path_trace_spp

    @path_trace_spp.setter
    def path_trace_spp(self, value: int):
        """Sets the number of Path Tracing samples per pixel.

        Args:

            value (int): The path trace samples per pixel to set.
        """
        if value > 0:
            self._path_trace_spp = value
        else:
            carb.log_warn(f"Failed to set path trace samples per pixel to {value} as it needs to be a positive number.")

    @property
    def ptmb_subframes_per_frame(self) -> int:
        """Gets the number of Path Tracing motion blur subframes per frame.

        Returns:

            int: The number of Path Tracing motion blur subframes per frame.
        """
        return self._ptmb_subframes_per_frame

    @ptmb_subframes_per_frame.setter
    def ptmb_subframes_per_frame(self, value: int):
        """Sets the number of Path Tracing motion blur subframes per frame.

        Args:

            value (int): The number of Path Tracing motion blur subframes per frame to set.
        """
        if value > 0:
            self._ptmb_subframes_per_frame = value
        else:
            carb.log_warn(
                f"Failed to set path trace motion blur subframe number to {value} as it needs to be a positive number."
            )

    @property
    def ptmb_fso(self) -> float:
        """Gets the Path Tracing motion blur frame shutter open.

        Returns:

            float: The current Path Tracing motion blur frame shutter open.
        """
        return self._ptmb_fso

    @ptmb_fso.setter
    def ptmb_fso(self, value: float):
        """Sets the Path Tracing motion blur frame shutter open.

        Args:

            value (float): The Path Tracing motion blur frame shutter open to set.
        """
        self._ptmb_fso = value

    @property
    def ptmb_fsc(self) -> float:
        """Gets the Path Tracing motion blur frame shutter close.

        Returns:

            float: The current Path Tracing motion blur frame shutter close.
        """
        return self._ptmb_fsc

    @ptmb_fsc.setter
    def ptmb_fsc(self, value: float):
        """Sets the Path Tracing motion blur frame shutter close.

        Args:

            value (float): The Path Tracing motion blur frame shutter close to set.
        """
        self._ptmb_fsc = value

    @property
    def output_folder(self) -> str:
        """Gets output folder.

        Returns:

            str: The current output folder.
        """
        return self._output_folder

    @output_folder.setter
    def output_folder(self, value: str):
        """Sets output folder.

        Args:

            value (str): The output folder to set.
        """
        self._output_folder = value

    @property
    def file_name(self) -> str:
        """Gets the file name.

        Returns:
            str: The file name.
        """
        return self._file_name

    @file_name.setter
    def file_name(self, value: str):
        """Sets file name.

        Args:

            value (str): The file name to set.
        """
        self._file_name = value

    @property
    def file_name_num_pattern(self) -> str:
        """Gets the file name number pattern.

        Returns:
            str: The file name number pattern.
        """
        return self._file_name_num_pattern

    @file_name_num_pattern.setter
    def file_name_num_pattern(self, value: str):
        """Sets the file name number pattern.

        Args:
            value (str): File name number pattern to set.
        """
        self._file_name_num_pattern = value

    @property
    def file_type(self) -> str:
        """Gets the file type.

        Returns:
            str: The file type.
        """
        return self._file_type

    @file_type.setter
    def file_type(self, value: str):
        """Sets the file type.

        Args:
            value (str): File type to set.
        """
        if value in OUTPUT_FILE_TYPES:
            self._file_type = value
        else:
            carb.log_warn(
                f"Failed to set output file type as {value} is not supported. Supported values are {OUTPUT_FILE_TYPES}."
            )

    @property
    def save_alpha(self) -> bool:
        """Gets the save alpha flag.

        Returns:
            bool: The current save alpha flag.
        """
        return self._save_alpha

    @save_alpha.setter
    def save_alpha(self, value: bool):
        """Sets the save alpha flag.

        Args:
            value (bool): Save alpha flag value to set.
        """
        self._save_alpha = value

    @property
    def hdr_output(self) -> bool:
        """Gets the hdr output flag.

        Returns:
            bool: The current hdr output flag.
        """
        return self._hdr_output

    @hdr_output.setter
    def hdr_output(self, value: bool):
        """Sets the hdr output flag.

        Args:
            value (bool): HDR output flag value to set.
        """
        self._hdr_output = value

    @property
    def show_pathtracing_single_frame_progress(self) -> bool:
        """Gets the show Path Tracing single frame progress flag.

        Returns:
            bool: The current state of Path Tracing single frame progress flag.
        """
        return self._show_pathtracing_single_frame_progress

    @show_pathtracing_single_frame_progress.setter
    def show_pathtracing_single_frame_progress(self, value: bool):
        """Sets the show Path Tracing single frame progress flag.

        Args:
            value (bool): Flag value for showing Path Tracing single frame progress.
        """
        self._show_pathtracing_single_frame_progress = value

    @property
    def preroll_frames(self) -> int:
        """Gets the number of preroll frames.

        Returns:
            int: The number of preroll frames.
        """
        return self._preroll_frames

    @preroll_frames.setter
    def preroll_frames(self, value: int):
        """Sets the number of preroll frames.

        Args:
            value (int): The number of preroll frames to set.
        """
        if value >= 0:
            self._preroll_frames = value
        else:
            carb.log_warn(f"Failed to set preroll frames number to {value} as it couldn't be negative.")

    @property
    def overwrite_existing_frames(self) -> bool:
        """Gets the overwrite existing frame images flag.

        Returns:
            bool: The current state of overwrite existing frame images flag.
        """
        return self._overwrite_existing_frames

    @overwrite_existing_frames.setter
    def overwrite_existing_frames(self, value: bool):
        """Sets the overwrite existing frame images flag.

        Args:
            value (bool): Flag indicating whether to overwrite existing frame images.
        """
        self._overwrite_existing_frames = value

    @property
    def movie_type(self) -> CaptureMovieType:
        """Gets the movie type.

        Returns:
            CaptureMovieType: The current movie type.
        """
        return self._movie_type

    @movie_type.setter
    def movie_type(self, value: CaptureMovieType):
        """Sets the movie type.

        Args:
            value (CaptureMovieType): The movie type value to set.
        """
        if value in list(CaptureMovieType):
            self._movie_type = value
        else:
            carb.log_warn(
                f"Failed to set movie type as {value} is not supported. Supported values are {list(CaptureMovieType)}."
            )

    @property
    def sunstudy_start_time(self) -> float:
        """Gets the sunstudy start time.

        Returns:
            float: The current sunstudy start time.
        """
        return self._sunstudy_start_time

    @sunstudy_start_time.setter
    def sunstudy_start_time(self, value: float):
        """Sets the sunstudy start time.

        Args:
            value (float): The sunstudy start time to set.
        """
        self._sunstudy_start_time = value

    @property
    def sunstudy_current_time(self) -> float:
        """Gets the current time of the sunstudy.

        Returns:
            float: The current current time of the sunstudy.
        """
        return self._sunstudy_current_time

    @sunstudy_current_time.setter
    def sunstudy_current_time(self, value: float):
        """Sets the sunstudy current time.

        Args:
            value (float): The sunstudy current time to set.
        """
        self._sunstudy_current_time = value

    @property
    def sunstudy_end_time(self) -> float:
        """Gets the end time of the sunstudy.

        Returns:
            float: The current end time of the sunstudy.
        """
        return self._sunstudy_end_time

    @sunstudy_end_time.setter
    def sunstudy_end_time(self, value: float):
        """Sets the end time of the sunstudy.

        Args:
            value (float): Value to set the end time of the sunstudy.
        """
        self._sunstudy_end_time = value

    @property
    def sunstudy_movie_length_in_seconds(self) -> float:
        """Gets the length of the sunstudy movie in seconds.

        Returns:
            float: The current length of the sunstudy movie in seconds.
        """
        return self._sunstudy_movie_length_in_seconds

    @sunstudy_movie_length_in_seconds.setter
    def sunstudy_movie_length_in_seconds(self, value: float):
        """Sets the length of the sunstudy movie in seconds.

        Args:
            value (float): Value to set the length of the sunstudy movie in seconds.
        """
        if value > 0:
            self._sunstudy_movie_length_in_seconds = value
        else:
            carb.log_warn(f"Failed to set sunstuey movie length to {value} as it needs to be a positive number.")

    @property
    def sunstudy_player(self):
        """Gets the sunstudy player object.

        Returns:
            any: The current sunstudy player object.
        """
        return self._sunstudy_player

    @sunstudy_player.setter
    def sunstudy_player(self, value):
        """Sets the sunstudy player object.

        Args:
            value (any): Value to set sunstudy_player.
        """
        self._sunstudy_player = value

    @property
    def real_time_settle_latency_frames(self) -> int:
        """Gets the number of real time settle latency frames.

        Returns:
            int: The current number of real time settle latency frames.
        """
        return self._real_time_settle_latency_frames

    @real_time_settle_latency_frames.setter
    def real_time_settle_latency_frames(self, value: int):
        """Sets the number of real time settle latency frames.

        Args:
            value (int): Value to set the number of real time settle latency frames.
        """
        self._real_time_settle_latency_frames = value

    @property
    def renumber_negative_frame_number_from_0(self) -> bool:
        """Gets the flag to renumber negative frame numbers from 0.

        Returns:
            bool: The current flag to renumber negative frame numbers from 0.
        """
        return self._renumber_negative_frame_number_from_0

    @renumber_negative_frame_number_from_0.setter
    def renumber_negative_frame_number_from_0(self, value: bool):
        """Sets the flag to renumber negative frame numbers from 0.

        Args:
            value (bool): Value to set the flag to renumber negative frame numbers from 0.
        """
        self._renumber_negative_frame_number_from_0 = value

    @property
    def render_product(self) -> str:
        """Gets the render product used for capture.

        Returns:
            str: The current render product used for capture.
        """
        return self._render_product

    @render_product.setter
    def render_product(self, value: str):
        """Sets the render product used for capture.

        Args:
            value (str): Value to set render product used for capture.
        """
        self._render_product = value

    @property
    def exr_compression_method(self) -> str:
        """Gets the compression method for EXR files.

        Returns:
            str: The current exr_compression_method.
        """
        return self._exr_compression_method

    @exr_compression_method.setter
    def exr_compression_method(self, value: str):
        """Sets exr_compression_method.

        Args:
            value (str): Value to set exr_compression_method.
        """
        global EXR_COMPRESSION_METHODS
        if value in EXR_COMPRESSION_METHODS:
            self._exr_compression_method = value
        else:
            self._exr_compression_method = "zips"
            carb.log_warn(
                f"Can't set unsupported compression method {value} for exr format, set to default zip16. Supported values are: {EXR_COMPRESSION_METHODS}"
            )

    @property
    def mp4_encoding_bitrate(self) -> int:
        """Gets mp4_encoding_bitrate.

        Returns:
            int: The current mp4_encoding_bitrate.
        """
        return self._mp4_encoding_bitrate

    @mp4_encoding_bitrate.setter
    def mp4_encoding_bitrate(self, value: int):
        """Sets mp4_encoding_bitrate.

        Args:
            value (int): Value to set mp4_encoding_bitrate.
        """
        self._mp4_encoding_bitrate = value

    @property
    def mp4_encoding_iframe_interval(self) -> int:
        """Gets mp4_encoding_iframe_interval.

        Returns:
            int: The current mp4_encoding_iframe_interval.
        """
        return self._mp4_encoding_iframe_interval

    @mp4_encoding_iframe_interval.setter
    def mp4_encoding_iframe_interval(self, value: int):
        """Sets mp4_encoding_iframe_interval.

        Args:
            value (int): Value to set mp4_encoding_iframe_interval.
        """
        if value > 0:
            self._mp4_encoding_iframe_interval = value
        else:
            carb.log_warn(f"Failed to mp4 encoding iframe interval to {value} as it needs to be a positive number.")

    @property
    def mp4_encoding_preset(self) -> str:
        """Gets the mp4 encoding preset.

        Returns:
            str: The current mp4 encoding preset.
        """
        return self._mp4_encoding_preset

    @mp4_encoding_preset.setter
    def mp4_encoding_preset(self, value: str):
        """Sets the mp4 encoding preset.

        Args:
            value (str): Value to set the mp4 encoding preset.
        """
        global MP4_ENCODING_PRESETS
        if value in MP4_ENCODING_PRESETS:
            self._mp4_encoding_preset = value
        else:
            self._mp4_encoding_preset = "PRESET_DEFAULT"
            carb.log_warn(
                f"Can't set unsupported mp4 encoding preset {value}, set to default {self._mp4_encoding_preset}. Supported values are: {MP4_ENCODING_PRESETS}"
            )

    @property
    def mp4_encoding_profile(self) -> str:
        """Gets the mp4 encoding profile.

        Returns:
            str: The current mp4 encoding profile.
        """
        return self._mp4_encoding_profile

    @mp4_encoding_profile.setter
    def mp4_encoding_profile(self, value: str):
        """Sets the mp4 encoding profile.

        Args:
            value (str): The value to set for the mp4 encoding profile.
        """
        global MP4_ENCODING_PROFILES
        if value in MP4_ENCODING_PROFILES:
            self._mp4_encoding_profile = value
        else:
            self._mp4_encoding_profile = "H264_PROFILE_HIGH"
            carb.log_warn(
                f"Can't set unsupported mp4 encoding profile {value}, set to default {self._mp4_encoding_profile}. Supported values are: {MP4_ENCODING_PROFILES}"
            )

    @property
    def mp4_encoding_rc_mode(self) -> str:
        """Gets the mp4 encoding rate control mode.

        Returns:
            str: The current mp4 encoding rate control mode.
        """
        return self._mp4_encoding_rc_mode

    @mp4_encoding_rc_mode.setter
    def mp4_encoding_rc_mode(self, value: str):
        """Sets the mp4 encoding rate control mode.

        Args:
            value (str): The value to set for the mp4 encoding rate control mode.
        """
        global MP4_ENCODING_RC_MODES
        if value in MP4_ENCODING_RC_MODES:
            self._mp4_encoding_rc_mode = value
        else:
            self._mp4_encoding_rc_mode = "RC_VBR"
            carb.log_warn(
                f"Can't set unsupported mp4 encoding rate control mode {value}, set to default {self._mp4_encoding_rc_mode}. Supported values are: {MP4_ENCODING_RC_MODES}"
            )

    @property
    def mp4_encoding_rc_target_quality(self) -> int:
        """Gets the mp4 encoding rate control target quality.

        Returns:
            int: The current mp4 encoding rate control target quality.
        """
        return self._mp4_encoding_rc_target_quality

    @mp4_encoding_rc_target_quality.setter
    def mp4_encoding_rc_target_quality(self, value: int):
        """Sets the mp4 encoding rate control target quality.

        Args:
            value (int): The value to set for the mp4 encoding rate control target quality.
        """
        if 0 <= value and value <= 51:
            self._mp4_encoding_rc_target_quality = value
        else:
            self._mp4_encoding_rc_target_quality = 0
            carb.log_warn(
                f"Can't set unsupported mp4 encoding rate control target quality {value}, set to default {self._mp4_encoding_rc_target_quality}. Supported range is [0, 51]"
            )

    @property
    def mp4_encoding_video_full_range_flag(self) -> bool:
        """Gets the mp4 encoding video full range flag.

        Returns:
            bool: The current state of the full range flag.
        """
        return self._mp4_encoding_video_full_range_flag

    @mp4_encoding_video_full_range_flag.setter
    def mp4_encoding_video_full_range_flag(self, value: bool):
        """Sets the mp4 encoding video full range flag.

        Args:
            value (bool): The value to set for the full range flag.
        """
        self._mp4_encoding_video_full_range_flag = value

    @property
    def app_level_capture(self) -> bool:
        """Gets the flag to capture all scene elements.

        Returns:
            bool: The current flag to capture all scene elements.
        """
        return self._app_level_capture

    @app_level_capture.setter
    def app_level_capture(self, value: bool):
        """Sets the flag to capture all scene elements.

        Args:
            value (bool): The value to set for the flag to capture all scene elements.
        """
        self._app_level_capture = value

    @property
    def animation_fps(self) -> float:
        """Gets the animation frames per second.

        Returns:
            float: The current animation frames per second.
        """
        return self._animation_fps

    @animation_fps.setter
    def animation_fps(self, value: float):
        """Sets the animation frames per second.

        Args:
            value (float): The value to set for the animation frames per second.
        """
        if value <= 0 and value != CaptureOptions.INVALID_ANIMATION_FPS:
            carb.log_warn(f"Failed to set animation FPS to {value} as it needs to be a positive number.")
        else:
            self._animation_fps = value

    @property
    def rt_wait_for_render_resolve_in_seconds(self) -> int:
        """Gets the number of seconds to wait for render resolve.

        Returns:
            int: The current number of seconds to wait for render resolve.
        """
        return self._rt_wait_for_render_resolve_in_seconds

    @rt_wait_for_render_resolve_in_seconds.setter
    def rt_wait_for_render_resolve_in_seconds(self, seconds_to_wait: int):
        """Sets the number of seconds to wait for render resolve.

        Args:
            seconds_to_wait (int): The number of seconds to wait for render resolve.
        """
        self._rt_wait_for_render_resolve_in_seconds = seconds_to_wait

    @property
    def early_quit_time_limit_per_frame_in_minutes(self) -> int:
        """Gets the capture time limitation for a single frame.

        Returns:
            int: The current capture time limitation for a single frame.
        """
        return self._early_quit_time_limit_per_frame_in_minutes

    @early_quit_time_limit_per_frame_in_minutes.setter
    def early_quit_time_limit_per_frame_in_minutes(self, time_limit_per_frame: int):
        """Sets the capture time limitation for a single frame.

        Args:
            time_limit_per_frame (int): The current capture time limitation for a single frame.
        """
        # warn if it's set to above 0, which means it will quit the kit app when the time spending in capturing a frame reaches it,
        # in case users set it by mistake
        if time_limit_per_frame > 0:
            carb.log_warn(
                f"Capture option early_quit_time_limit_per_frame_in_minutes will be set to {time_limit_per_frame} minutes. \
                          \nPlease be noted that Movie capture will force quit the application if the capture time of a frame reaches it."
            )

        self._early_quit_time_limit_per_frame_in_minutes = time_limit_per_frame

    def is_video(self) -> bool:
        """Determines if the capture option is set to video mode.

        Returns:
            bool: True if file type is ".mp4", False otherwise.
        """
        return self.file_type == ".mp4"

    def is_capturing_nth_frames(self) -> bool:
        """Determines if capturing every nth frame is enabled.

        Returns:
            bool: True if capturing every nth frame is enabled, False otherwise.
        """
        return self._capture_every_nth_frames > 0

    def is_capturing_pathtracing_single_frame(self) -> bool:
        """Determines if capturing a single frame in Path Tracing mode.

        Returns:
            bool: True if capturing a single frame in Path Tracing mode, False otherwise.
        """
        return (
            self.is_video() is False
            and self.is_capturing_nth_frames() is False
            and (self.render_preset == CaptureRenderPreset.PATH_TRACE or self.render_preset == CaptureRenderPreset.IRAY)
        )

    def is_capturing_single_frame(self) -> bool:
        """Determines if capturing a single frame is active, meaning video mode is off and nth frame capture is disabled.

        Returns:

            bool: True if capturing a single frame is active, False otherwise.
        """
        return self.is_video() is False and self.is_capturing_nth_frames() is False

    def is_capturing_rt_with_render_resolve_waiting(self) -> bool:
        """Checks if capturing real time with render resolve waiting is enabled. It confirms that render preset is RAY_TRACE and waiting seconds is greater than 0.

        Returns:

            bool: True if render resolve waiting is active with real time capture, False otherwise.
        """
        return self.render_preset == CaptureRenderPreset.RAY_TRACE and self.rt_wait_for_render_resolve_in_seconds > 0

    def is_capturing_frame(self) -> bool:
        """Determines if capture is based on frame range.

        Returns:

            bool: True if the range type is FRAMES, False otherwise.
        """
        return self._range_type == CaptureRangeType.FRAMES

    def get_full_path(self) -> str:
        """Get full output path for video mode only.

        Returns:

            str: Full output path if in video mode, or an empty string if not.
        """
        if self.is_video():
            return os.path.join(self._output_folder, self._file_name + self._file_type)
        else:
            carb.log_warn("'get_full_path' only works for video mode.")
            return ""

    def is_valid(self) -> bool:
        """Check if the capture options are valid to start a capture.
        * output folder and file name will NOT be fully checked here, as its hard to check things like permission at this time, thus we defer the check to them when we prepare folders for the capture and report errors for failures.

        Returns:

            bool: True if the capture options are valid, False otherwise.
        """
        invalid_options_msg = ""

        def check_positive_number(option, option_name):
            if option <= 0:
                return f"{option_name} should be a positive number \r\n"
            return ""

        def check_required_string(option, option_name):
            if len(option) == 0:
                return f"no {option_name} is specified \r\n"
            return ""

        def check_enum_type_in_range(option, option_name, enum_type):
            if option in list(enum_type):
                return ""
            else:
                return f"{option_name} is not supported. Supported values are {list(enum_type)} \r\n"

        if self.range_type == CaptureRangeType.FRAMES:
            if self.start_frame > self.end_frame:
                invalid_options_msg += "start frame should not be greater than end frame \r\n"
        else:
            if self.start_time > self.end_time:
                invalid_options_msg += "start time should not be greater than end time \r\n"

        invalid_options_msg += check_required_string(self.camera, "camera name")
        invalid_options_msg += check_required_string(self.file_name, "file name")

        invalid_options_msg += check_enum_type_in_range(self.movie_type, "movie type", CaptureMovieType)
        invalid_options_msg += check_enum_type_in_range(self.range_type, "range type", CaptureRangeType)
        invalid_options_msg += check_enum_type_in_range(self.render_preset, "render preset", CaptureRenderPreset)
        invalid_options_msg += check_enum_type_in_range(
            self.debug_material_type, "debug material type", CaptureDebugMaterialType
        )

        invalid_options_msg += check_positive_number(self.fps, "FPS")
        invalid_options_msg += check_positive_number(self.res_width, "resolution width")
        invalid_options_msg += check_positive_number(self.res_height, "resolution height")
        invalid_options_msg += check_positive_number(self.spp_per_iteration, "samples per pixel per iteration")
        invalid_options_msg += check_positive_number(self.path_trace_spp, "path trace samples per pixel")

        if self.preroll_frames < 0:
            invalid_options_msg += "preroll frames number should be equal to or greater than 0 \r\n"

        if self.sunstudy_start_time > self.sunstudy_end_time:
            invalid_options_msg += "sunstudy start time should not be greater than end time \r\n"

        if self.ptmb_fso < -1.0:
            invalid_options_msg += "Path trace motion blur frame shutter open should not be smaller than -1.0 \r\n"
        if self.ptmb_fso > self.ptmb_fsc:
            invalid_options_msg += (
                "Path trace motion blur frame shutter open should not be greater than frame shutter close \r\n"
            )
        if self.ptmb_fsc > 1.0:
            invalid_options_msg += "Path trace motion blur frame shutter close should not be greater than 1.0 \r\n"

        if len(invalid_options_msg) > 0:
            carb.log_warn(f"Invalid capture options:\r\n{invalid_options_msg}")
            return False
        return True
