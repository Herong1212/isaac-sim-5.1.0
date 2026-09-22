import os
import os.path
import omni.kit.test
import carb
import carb.settings
import carb.tokens
from tempfile import TemporaryDirectory

from omni.kit.capture.viewport import CaptureOptions, CaptureExtension, CaptureRenderPreset
from omni.kit.viewport.utility import get_active_viewport, create_viewport_window, capture_viewport_to_file
from .test_helper import capture_async
from omni.ui.tests.test_base import OmniUiTest


class TestCaptureHdr(OmniUiTest):

    # Before running each test
    async def setUp(self):
        self._usd_context = ''
        settings = carb.settings.get_settings()
        self._frames_wait_for_capture_resource_ready = 6
        await omni.usd.get_context(self._usd_context).new_stage_async()
        self._capture_instance = CaptureExtension().get_instance()

    async def tearDown(self) -> None:
        self._capture_instance = None

    async def _make_sure_testcase_finishes(self):
        """ call this function at the end of a testcase to make sure the capture it starts will be terminated when
        there is anything goes wrong.
        """
        # the cancel call will cancel the capture if there is the capture is still running, otherwise do nothing
        while not self._capture_instance.done:
            await omni.kit.app.get_app().next_update_async()
        await self.wait_n_updates(20)

    async def test_hdr_capture(self):
        viewport_api = get_active_viewport(self._usd_context)
        # Wait until the viewport has valid resources
        await viewport_api.wait_for_rendered_frames()

        capture_filename = "capture_hdr_test"
        with TemporaryDirectory() as tmpdir:
            options = CaptureOptions()
            for render_preset in [CaptureRenderPreset.RAY_TRACE, CaptureRenderPreset.REAL_TIME_PATHTRACING, CaptureRenderPreset.PATH_TRACE]:
                filePath = tmpdir + "/" + capture_filename + "_" + str(render_preset)
                options.render_preset = render_preset
                options.file_type = ".exr"
                options.output_folder = str(filePath)
                exr_path = os.path.join(options._output_folder, "Capture1.exr")
                carb.log_warn(f"Capture image path: {exr_path}")
                options.hdr_output = True
                options.camera = viewport_api.camera_path.pathString
                # to reduce memory consumption and save time
                options.res_width = 600
                options.res_height = 337

                self._capture_instance.options = options
                output_files = await capture_async(self._capture_instance)
                print(f" - output_files: {output_files}")
                print(f" - exr_path: {exr_path}")
                self.assertTrue(exr_path in output_files)
                self.assertTrue(os.path.isfile(exr_path))
                await self._make_sure_testcase_finishes()

    async def _test_exr_compression_method(self, compression_method):
        viewport_api = get_active_viewport(self._usd_context)
        # Wait until the viewport has valid resources
        await viewport_api.wait_for_rendered_frames()

        with TemporaryDirectory() as tmpdir:
            capture_filename = "capture_exr_compression_method_test_" + compression_method
            filePath = tmpdir + "/" + capture_filename
            options = CaptureOptions()
            options.file_type = ".exr"
            options.exr_compression_method = compression_method
            options.output_folder = str(filePath)
            options.hdr_output = True
            options.camera = viewport_api.camera_path.pathString
            # to reduce memory consumption and save time
            options.res_width = 600
            options.res_height = 337

            self._capture_instance.options = options
            outputs = await capture_async(self._capture_instance)
            exr_path = os.path.join(options._output_folder, "Capture1.exr")
            self.assertEqual([exr_path], outputs)
            await self._make_sure_testcase_finishes()

    async def test_exr_compression_method_rle(self):
        await self._test_exr_compression_method("rle")

    async def test_exr_compression_method_zip(self):
        await self._test_exr_compression_method("zip")

    async def test_exr_compression_method_dwaa(self):
        await self._test_exr_compression_method("dwaa")

    async def test_exr_compression_method_dwab(self):
        await self._test_exr_compression_method("dwab")

    async def test_exr_compression_method_piz(self):
        await self._test_exr_compression_method("piz")

    async def test_exr_compression_method_b44(self):
        await self._test_exr_compression_method("b44")

    async def test_exr_compression_method_b44a(self):
        await self._test_exr_compression_method("b44a")

    # Notes: The following multiple viewport tests will fail now and should be revisited after we confirm the
    # multiple viewport capture support in new SRD.
    # # Make sure we do not crash in the unsupported multi-view case
    # async def test_hdr_multiview_capture(self):
    #     viewport_api = get_active_viewport(self._usd_context)
    #     # Wait until the viewport has valid resources
    #     await viewport_api.wait_for_rendered_frames()

    #     new_viewport = create_viewport_window("Viewport 2")

    #     capture_filename = "capture.hdr_test.multiview"
    #     filePath = pathlib.Path(OUTPUTS_DIR).joinpath(capture_filename)
    #     options = CaptureOptions()
    #     options.file_type = ".exr"
    #     options.output_folder = str(filePath)
    #     self._make_sure_directory_existed(options.output_folder)
    #     self._clean_files_in_directory(options.output_folder, ".exr")
    #     exr_path = os.path.join(options._output_folder, "Capture1.exr")
    #     carb.log_warn(f"Capture image path: {exr_path}")

    #     options.hdr_output = True
    #     options.camera = viewport_api.camera_path.pathString

    #     capture_instance = CaptureExtension().get_instance()
    #     capture_instance.options = options
    #     capture_instance.start()

    #     capture_viewport_to_file(new_viewport.viewport_api, file_path=exr_path)

    #     i = self._frames_wait_for_capture_resource_ready
    #     while i > 0:
    #         await omni.kit.app.get_app().next_update_async()
    #         i -= 1
    #     options = None
    #     capture_instance = None
    #     assert os.path.isfile(exr_path)

    #     if viewport_widget:
    #         viewport_widget.destroy()
    #         del viewport_widget

    # async def test_hdr_multiview_capture_legacy(self):
    #     await self.do_test_hdr_multiview_capture(True)

    # async def test_hdr_multiview_capture(self):
    #     await self.do_test_hdr_multiview_capture(False)
