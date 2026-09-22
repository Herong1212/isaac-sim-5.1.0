import os
import os.path
import omni.kit.test
import carb
import carb.settings
import carb.tokens
from tempfile import TemporaryDirectory

from omni.ui.tests.test_base import OmniUiTest
from omni.kit.capture.viewport import CaptureOptions, CaptureExtension, CaptureRangeType, CaptureRenderPreset
from omni.kit.viewport.utility import get_active_viewport
from .test_helper import capture_async, wait_for_capture_done


class TestCapturePng(OmniUiTest):

    # Before running each test
    async def setUp(self):
        self._usd_context = ''
        settings = carb.settings.get_settings()
        self._frames_wait_for_capture_resource_ready = 6
        await omni.usd.get_context(self._usd_context).new_stage_async()
        self._capture_instance = CaptureExtension().get_instance()
        await self.wait_n_updates()

    async def tearDown(self) -> None:
        await omni.usd.get_context().close_stage_async()
        await self.wait_n_updates()
        self._capture_instance = None

    async def _make_sure_testcase_finishes(self):
        """ call this function at the end of a testcase to make sure the capture it starts will be terminated when
        there is anything goes wrong.
        """
        # the cancel call will cancel the capture if there is the capture is still running, otherwise do nothing
        self._capture_instance.cancel()
        await self.wait_n_updates(20)

    async def test_png_capture_general(self):
        viewport_api = get_active_viewport(self._usd_context)
        # Wait until the viewport has valid resources
        await viewport_api.wait_for_rendered_frames()

        with TemporaryDirectory() as tmpdir:
            capture_filename = "capture_png_test"
            filePath = tmpdir + "/" + capture_filename
            options = CaptureOptions()
            options.file_type = ".png"
            options.output_folder = str(filePath)
            png_path = os.path.join(options._output_folder, "Capture1.png")
            options.hdr_output = False
            options.camera = viewport_api.camera_path.pathString

            self._capture_instance.options = options
            output_files = await capture_async(self._capture_instance)
            self.assertEqual([png_path], output_files)
            await self._make_sure_testcase_finishes()

    async def test_png_capture_sequence(self):
        viewport_api = get_active_viewport(self._usd_context)
        # Wait until the viewport has valid resources
        await viewport_api.wait_for_rendered_frames()

        with TemporaryDirectory() as tmpdir:
            capture_filename = "capture_png_test_seq"
            filePath = tmpdir + "/" + capture_filename
            options = CaptureOptions()
            options.file_type = ".png"
            options.start_frame = 1
            options.end_frame = 10
            options.render_preset = 1
            options.capture_every_Nth_frames = 1
            options.output_folder = str(filePath)
            options.file_name = "capture_png_seq"
            options.overwrite_existing_frames = True
            results_folder = os.path.join(options.output_folder, options.file_name + "_frames")
            options.hdr_output = False
            options.camera = viewport_api.camera_path.pathString

            self._capture_instance.options = options
            output_files = await capture_async(self._capture_instance)
            expected_output_files = [os.path.join(results_folder, options.file_name + f".{index:04d}.png") for index in range(options.start_frame, options.end_frame + 1)]
            self.assertEqual(expected_output_files, output_files)

            # test skipping files
            first_png_path = expected_output_files[0]
            first_png_time = os.path.getmtime(first_png_path)
            options.overwrite_existing_frames = False
            options.end_frame = 11
            the_11th_png_path = os.path.join(results_folder, options.file_name + ".0011.png")
            self._capture_instance.options = options
            await capture_async(self._capture_instance)
            first_png_time_skipping = os.path.getmtime(first_png_path)
            self.assertEqual(first_png_time, first_png_time_skipping)

            # test overwrite existing files
            options.overwrite_existing_frames = True
            self._capture_instance.options = options
            await capture_async(self._capture_instance)
            first_png_time_overwrite = os.path.getmtime(first_png_path)
            self.assertNotEqual(first_png_time, first_png_time_overwrite)

            options = None
            await self._make_sure_testcase_finishes()

    async def test_png_capture_sequence_low_spp_with_settle_latency_frames(self):
        """Testcase to make sure the OM-112018 is fixed and won't happen again
        """
        viewport_api = get_active_viewport(self._usd_context)
        # Wait until the viewport has valid resources
        await viewport_api.wait_for_rendered_frames()

        with TemporaryDirectory() as tmpdir:
            capture_filename = "capture_png_test_seq_low_spp_with_slf"
            filePath = tmpdir + "/" + capture_filename
            options = CaptureOptions()
            options.file_type = ".png"
            options.start_frame = 1
            options.end_frame = 10
            # OM-112018 happens in PT captures
            options.render_preset = CaptureRenderPreset.PATH_TRACE
            options.capture_every_Nth_frames = 1
            options.real_time_settle_latency_frames = 0
            options.path_trace_spp = 1
            options.output_folder = str(filePath)
            options.file_name = "capture_png_seq"
            options.overwrite_existing_frames = True
            results_folder = os.path.join(options.output_folder, options.file_name + "_frames")
            first_png_path = os.path.join(results_folder, options.file_name + ".0001.png")
            last_png_path = os.path.join(results_folder, options.file_name + ".0010.png")
            options.hdr_output = False
            options.camera = viewport_api.camera_path.pathString

            self._capture_instance.options = options
            await capture_async(self._capture_instance)

            self.assertTrue(os.path.isfile(first_png_path), f'File "{first_png_path}" could not be found.')
            self.assertTrue(os.path.isfile(last_png_path), f'File "{last_png_path}" could not be found.')
            await self._make_sure_testcase_finishes()

    async def test_png_capture_sequence_in_time(self):
        viewport_api = get_active_viewport(self._usd_context)
        # Wait until the viewport has valid resources
        await viewport_api.wait_for_rendered_frames()

        with TemporaryDirectory() as tmpdir:
            capture_filename = "capture_png_test_seq_in_time"
            filePath = tmpdir + "/" + capture_filename
            options = CaptureOptions()
            options.file_type = ".png"
            options.range_type = CaptureRangeType.SECONDS
            options.fps = 24
            options.animation_fps = 24
            options.start_time = 0.0
            options.end_time = 1.0
            options.render_preset = 1
            options.capture_every_Nth_frames = 1
            options.real_time_settle_latency_frames = -1
            options.output_folder = str(filePath)
            options.file_name = "capture_png_seq"
            options.overwrite_existing_frames = True
            results_folder = os.path.join(options.output_folder, options.file_name + "_frames")
            options.hdr_output = False
            options.camera = viewport_api.camera_path.pathString

            self._capture_instance.options = options
            outputs = await capture_async(self._capture_instance)

            total_frame_count = round((options.end_time - options.start_time) * options.animation_fps)
            expected_output_files = [os.path.join(results_folder, options.file_name + f".{index:04d}.png") for index in range(total_frame_count)]
            self.assertEqual(expected_output_files, outputs)

            nonexist_png_path = os.path.join(results_folder, options.file_name + ".00" + str(total_frame_count) + ".png")
            self.assertFalse(os.path.isfile(nonexist_png_path), f'File "{nonexist_png_path}" was found, which is unexpected.')

            options = None
            await self._make_sure_testcase_finishes()

    async def test_png_capture_sequence_nth_frame(self):
        viewport_api = get_active_viewport(self._usd_context)
        # Wait until the viewport has valid resources
        await viewport_api.wait_for_rendered_frames()

        with TemporaryDirectory() as tmpdir:
            capture_filename = "capture_png_test_seq_5th_frame"
            filePath = tmpdir + "/" + capture_filename
            options = CaptureOptions()
            options.file_type = ".png"
            options.start_frame = 0
            options.end_frame = 20
            options.render_preset = 1
            options.capture_every_Nth_frames = 5
            options.output_folder = str(filePath)
            options.file_name = "capture_png_seq"
            options.overwrite_existing_frames = True
            results_folder = os.path.join(options.output_folder, options.file_name + "_5th_frames")
            options.hdr_output = False
            options.camera = viewport_api.camera_path.pathString
            
            self._capture_instance.options = options
            outputs = await capture_async(self._capture_instance)
            expected_output_files = [os.path.join(results_folder, options.file_name + f".{index:04d}.png") for index in range(options.start_frame, options.end_frame + 1) if index % options.capture_every_Nth_frames == 0]
            self.assertEqual(expected_output_files, outputs)

            unexpected_output_files = [os.path.join(results_folder, options.file_name + f".{index:04d}.png") for index in range(options.start_frame, options.end_frame + 1) if index % options.capture_every_Nth_frames != 0]
            for output in unexpected_output_files:
                self.assertFalse(os.path.isfile(output), f'File "{output}" was found, which is not expected.')
            await self._make_sure_testcase_finishes()

    async def test_png_capture_mp4(self):
        viewport_api = get_active_viewport(self._usd_context)
        # Wait until the viewport has valid resources
        await viewport_api.wait_for_rendered_frames()

        with TemporaryDirectory() as tmpdir:
            capture_filename = "capture_png_test_mp4"
            filePath = tmpdir + "/" + capture_filename
            options = CaptureOptions()
            options.file_type = ".mp4"
            options.start_frame = 1
            options.end_frame = 100
            options.render_preset = 0
            options.capture_every_Nth_frames = 1
            options.output_folder = str(filePath)
            options.file_name = "capture_png_mp4"
            options.overwrite_existing_frames = True
            options.hdr_output = False
            options.camera = viewport_api.camera_path.pathString

            mp4_path = os.path.join(options._output_folder, options.file_name + ".mp4")
            self._capture_instance.options = options
            outputs = await capture_async(self._capture_instance)
            self.assertEqual([mp4_path], outputs)

            frame_pngs = [os.path.join(options._output_folder, options.file_name + "_frames", options.file_name + f".{index:04d}.png") for index in range(options.start_frame, options.end_frame + 1)]
            for png in frame_pngs:
                self.assertTrue(os.path.isfile(png), f'File "{png}" could not be found.')
            
            await self._make_sure_testcase_finishes()

    async def test_png_capture_rt_render_resolve_wait(self):
        viewport_api = get_active_viewport(self._usd_context)
        # Wait until the viewport has valid resources
        await viewport_api.wait_for_rendered_frames()

        with TemporaryDirectory() as tmpdir:
            capture_filename = "capture_png_rt_render_resolve_wait"
            filePath = tmpdir + "/" + capture_filename
            options = CaptureOptions()
            options.file_type = ".png"
            options.output_folder = str(filePath)
            png_path = os.path.join(options._output_folder, "Capture1.png")
            carb.log_warn(f"Capture image path: {png_path}")
            options.hdr_output = False
            options.camera = viewport_api.camera_path.pathString
            options.render_preset = CaptureRenderPreset.RAY_TRACE
            options.rt_wait_for_render_resolve_in_seconds = 10

            self._capture_instance.options = options
            self._capture_instance.start()

            # wait for progress window to show up and verify the ui elements
            await self.wait_n_updates(100)
            self.assertEqual(options.rt_wait_for_render_resolve_in_seconds, 10)
            self.assertTrue(self._capture_instance._progress_window._window.visible, "Progress window should show up when doing single frame capture in RT with render resolve wait")
            self.assertFalse(self._capture_instance._progress_window._show_pt_iterations, "Progress window should not show PT iteration info when doing single frame capture in RT with render resolve wait")
            self.assertFalse(self._capture_instance._progress_window._show_pt_subframes, "Progress window should not show PT subframe info when doing single frame capture in RT with render resolve wait")
            self.assertEqual(self._capture_instance._progress_window._notification.text, "Waiting for rendering to resolve...")

            # wait for capture to finish and verify image captured
            await wait_for_capture_done(self._capture_instance)
            options = None
            self.assertTrue(os.path.isfile(png_path), f'File "{png_path}" could not be found.')
            await self._make_sure_testcase_finishes()
