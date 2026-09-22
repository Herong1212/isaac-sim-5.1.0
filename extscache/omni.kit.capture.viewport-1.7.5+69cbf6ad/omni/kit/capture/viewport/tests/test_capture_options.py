import omni.kit.test
import omni.kit.capture.viewport.capture_options as _capture_options
from omni.kit.capture.viewport import CaptureExtension, CaptureRangeType, CaptureRenderPreset, CaptureDebugMaterialType, CaptureMovieType


class TestCaptureOptions(omni.kit.test.AsyncTestCase):

    async def setUp(self):
        self._capture_instance = CaptureExtension().get_instance()

    async def tearDown(self) -> None:
        self._capture_instance = None

    async def test_capture_options_serialisation(self):
        options = _capture_options.CaptureOptions()
        data_dict = options.to_dict()

        self.assertIsInstance(data_dict, dict)

    async def test_capture_options_deserialisation(self):
        options = _capture_options.CaptureOptions()
        data_dict = options.to_dict()
        regenerated_options = _capture_options.CaptureOptions.from_dict(data_dict)

        self.assertIsInstance(regenerated_options, _capture_options.CaptureOptions)

    async def test_capture_options_values_persisted(self):
        options = _capture_options.CaptureOptions(camera="my_camera")
        data_dict = options.to_dict()
        regenerated_options = _capture_options.CaptureOptions.from_dict(data_dict)

        self.assertEqual(regenerated_options.camera, "my_camera")

    async def test_adding_random_attribute_fails(self):
        """ Test that adding new attributes without making them configurable via the __init__ will raise an exception
        """
        options = _capture_options.CaptureOptions()
        options._my_new_value = "foo"
        data_dict = options.to_dict()
        with self.assertRaises(TypeError, msg="__init__() got an unexpected keyword argument 'my_new_value'"):
            regnerated = _capture_options.CaptureOptions.from_dict(data_dict)

    async def test_capture_options_set_invalid_attributes(self):
        options = _capture_options.CaptureOptions()
        options.range_type = CaptureRangeType.SECONDS
        self.assertEqual(options.range_type, CaptureRangeType.SECONDS)
        options.range_type = 5
        self.assertEqual(options.range_type, CaptureRangeType.SECONDS)

        options.movie_type = CaptureMovieType.SUNSTUDY
        self.assertEqual(options.movie_type, CaptureMovieType.SUNSTUDY)
        options.movie_type = 4
        self.assertEqual(options.movie_type, CaptureMovieType.SUNSTUDY)

        options.render_preset = CaptureRenderPreset.IRAY
        self.assertEqual(options.render_preset, CaptureRenderPreset.IRAY)
        options.render_preset = 6
        self.assertEqual(options.render_preset, CaptureRenderPreset.IRAY)

        options.debug_material_type = CaptureDebugMaterialType.WHITE
        self.assertEqual(options.debug_material_type, CaptureDebugMaterialType.WHITE)
        options.debug_material_type = 3
        self.assertEqual(options.debug_material_type, CaptureDebugMaterialType.WHITE)

        options.res_width = 1024
        self.assertEqual(options.res_width, 1024)
        options.res_width = 0
        self.assertEqual(options.res_width, 1024)

        options.res_height = 1024
        self.assertEqual(options.res_height, 1024)
        options.res_height = 0
        self.assertEqual(options.res_height, 1024)
        options.res_height = -1
        self.assertEqual(options.res_height, 1024)

        options.fps = 30
        self.assertEqual(options.fps, 30)
        options.fps = 0
        self.assertEqual(options.fps, 30)
        options.fps = -1
        self.assertEqual(options.fps, 30)

        options.spp_per_iteration = 256
        self.assertEqual(options.spp_per_iteration, 256)
        options.spp_per_iteration = 0
        self.assertEqual(options.spp_per_iteration, 256)
        options.spp_per_iteration = -1
        self.assertEqual(options.spp_per_iteration, 256)

        options.path_trace_spp = 256
        self.assertEqual(options.path_trace_spp, 256)
        options.path_trace_spp = 0
        self.assertEqual(options.path_trace_spp, 256)
        options.path_trace_spp = -1
        self.assertEqual(options.path_trace_spp, 256)

        options.ptmb_subframes_per_frame = 64
        self.assertEqual(options.ptmb_subframes_per_frame, 64)
        options.ptmb_subframes_per_frame = 0
        self.assertEqual(options.ptmb_subframes_per_frame, 64)
        options.ptmb_subframes_per_frame = -1
        self.assertEqual(options.ptmb_subframes_per_frame, 64)

        options.preroll_frames = 8
        self.assertEqual(options.preroll_frames, 8)
        options.preroll_frames = -1
        self.assertEqual(options.preroll_frames, 8)

        options.sunstudy_movie_length_in_seconds = 10
        self.assertEqual(options.sunstudy_movie_length_in_seconds, 10)
        options.sunstudy_movie_length_in_seconds = 0
        self.assertEqual(options.sunstudy_movie_length_in_seconds, 10)
        options.sunstudy_movie_length_in_seconds = -1
        self.assertEqual(options.sunstudy_movie_length_in_seconds, 10)

    async def test_capture_options_validation(self):
        options_default = _capture_options.CaptureOptions()
        self.assertTrue(options_default.is_valid(), "default options should be valid")

        options_invalid_numbers = _capture_options.CaptureOptions(fps=-1, res_height=-1, res_width=-1, spp_per_iteration=-1, path_trace_spp=-1)
        self.assertFalse(options_invalid_numbers.is_valid(), "invalid number options should fail the validation test")
        self._capture_instance.options = options_invalid_numbers
        self.assertFalse(self._capture_instance.start(), "invalid options should fail to start capture")
        await self.wait_n_updates()

        options_invalid_strs = _capture_options.CaptureOptions(camera="", file_name="")
        self.assertFalse(options_invalid_strs.is_valid(), "invalid string options should fail the validation test")
        self._capture_instance.options = options_invalid_strs
        self.assertFalse(self._capture_instance.start(), "invalid options should fail to start capture")
        await self.wait_n_updates()

        options_invalid_enums = _capture_options.CaptureOptions(movie_type=3, range_type=5, render_preset=6, debug_material_type=4)
        self.assertFalse(options_invalid_enums.is_valid(), "invalid enum options should fail the validation test")
        self._capture_instance.options = options_invalid_enums
        self.assertFalse(self._capture_instance.start(), "invalid options should fail to start capture")
        await self.wait_n_updates()

    async def test_capture_options_unsupported_exr_compression_method(self):
        options = _capture_options.CaptureOptions(exr_compression_method="sth_wrong")
        self.assertEqual(options.exr_compression_method, "zips")

    async def test_capture_options_mp4_encoding_settings(self):
        options = _capture_options.CaptureOptions(
            mp4_encoding_bitrate=4194304,
            mp4_encoding_iframe_interval=10,
            mp4_encoding_preset="PRESET_LOSSLESS_HP",
            mp4_encoding_profile="H264_PROFILE_PROGRESSIVE_HIGH",
            mp4_encoding_rc_mode="RC_VBR_HQ",
            mp4_encoding_rc_target_quality=51,
            mp4_encoding_video_full_range_flag=True,
        )
        self.assertEqual(options.mp4_encoding_bitrate, 4194304)
        self.assertEqual(options.mp4_encoding_iframe_interval, 10)
        self.assertEqual(options.mp4_encoding_preset, "PRESET_LOSSLESS_HP")
        self.assertEqual(options.mp4_encoding_profile, "H264_PROFILE_PROGRESSIVE_HIGH")
        self.assertEqual(options._mp4_encoding_rc_mode, "RC_VBR_HQ")
        self.assertEqual(options._mp4_encoding_rc_target_quality, 51)
        self.assertEqual(options.mp4_encoding_video_full_range_flag, True)

    async def test_capture_options_unsupported_mp4_encoding_settings(self):
        options = _capture_options.CaptureOptions(
            mp4_encoding_bitrate=4194304,
            mp4_encoding_iframe_interval=10,
            mp4_encoding_preset="PRESET_NOT_EXISTING",
            mp4_encoding_profile="PROFILE_NOT_EXISTING",
            mp4_encoding_rc_mode="RC_NOT_EXISTING",
            mp4_encoding_rc_target_quality=52,
            mp4_encoding_video_full_range_flag=True,
        )
        self.assertEqual(options.mp4_encoding_bitrate, 4194304)
        self.assertEqual(options.mp4_encoding_iframe_interval, 10)
        self.assertEqual(options.mp4_encoding_preset, "PRESET_DEFAULT")
        self.assertEqual(options.mp4_encoding_profile, "H264_PROFILE_HIGH")
        self.assertEqual(options._mp4_encoding_rc_mode, "RC_VBR")
        self.assertEqual(options._mp4_encoding_rc_target_quality, 0)
        self.assertEqual(options.mp4_encoding_video_full_range_flag, True)
