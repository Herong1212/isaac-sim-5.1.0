import os
import os.path
import omni.kit.test
from tempfile import TemporaryDirectory

import omni.ui as ui
from omni.kit.capture.viewport import CaptureOptions, CaptureExtension
from omni.kit.viewport.utility import get_active_viewport_and_window
from omni.ui.tests.test_base import OmniUiTest
from .test_helper import capture_async


class TestCaptureSceneElement(OmniUiTest):

    # Before running each test
    async def setUp(self):
        self._usd_context = ''
        self._frames_wait_for_capture_resource_ready = 6
        await omni.usd.get_context(self._usd_context).new_stage_async()
        self._capture_instance = CaptureExtension().get_instance()

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

    async def test_capture_scene_element(self):
        # create some scene elements
        viewport_api, vp_window = get_active_viewport_and_window()

        from omni.ui_scene import scene as sc
        vp_window.width = 1920
        vp_window.height = 1080
        with vp_window.frame:
            scene_view = sc.SceneView(aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT)
            with scene_view.scene:
                with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0.25, 0.25, -0.1)):
                    sc.Rectangle(1, 1, color=ui.color(1.0, 1.0, 0.0, 0.5))
                with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0, 0, 0)):
                    sc.Rectangle(1, 1, color=ui.color(1.0, 1.0, 1.0, 0.5))
                with sc.Transform(transform=sc.Matrix44.get_translation_matrix(-0.25, -0.25, 0.1)):
                    sc.Rectangle(1, 1, color=ui.color(1.0, 0.0, 1.0, 0.5))

        await self.wait_n_updates(2)

        # capture the scene elements and compare images
        capture_filename = "capture_png_test_sceen_element"
        with TemporaryDirectory() as tmpdir:
            filePath = tmpdir + "/" + capture_filename
            options = CaptureOptions()
            options.file_type = ".png"
            options.render_preset = 1
            options.start_frame = 0
            options.end_frame = 10
            options.res_width = 1920
            options.res_height = 1080
            options.capture_every_Nth_frames = 1
            options.output_folder = str(filePath)
            options.file_name = "capture_png_scene_element"
            options.overwrite_existing_frames = True
            results_folder = os.path.join(options.output_folder, options.file_name + "_frames")
            se_png_path = os.path.join(results_folder, options.file_name + ".0001.png")
            options.hdr_output = False
            options.app_level_capture = True
            options.camera = viewport_api.camera_path.pathString

            self._capture_instance.options = options
            await capture_async(self._capture_instance)

            self.assertTrue(os.path.isfile(se_png_path), f'File "{se_png_path}" could not be found.')
            scene_element_image_size = os.path.getsize(se_png_path) if os.path.isfile(se_png_path) else 0

            # capture the same scene without capturing scene elements, and compare images
            options.app_level_capture = False
            options.file_name = "capture_png_dont_capture_scene_element"
            results_folder = os.path.join(options.output_folder, options.file_name + "_frames")
            se_png_path = os.path.join(results_folder, options.file_name + ".0001.png")
            self._capture_instance.options = options
            await capture_async(self._capture_instance)
            
            self.assertTrue(os.path.isfile(se_png_path), f'File "{se_png_path}" could not be found.')
            non_scene_element_image_size = os.path.getsize(se_png_path) if os.path.isfile(se_png_path) else 0
            # the image comparison result is not reliable on TC now so switch to compare file size.
            self.assertNotEqual(scene_element_image_size, non_scene_element_image_size)

            await self._make_sure_testcase_finishes()
            options = None
