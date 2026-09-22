import os
import os.path
import omni.kit.test
import omni.usd
import carb
import carb.settings
import carb.tokens
import pathlib
from tempfile import mkdtemp

from omni.kit.capture.viewport import CaptureOptions, CaptureExtension
from omni.kit.viewport.utility import get_active_viewport
from omni.kit.test_suite.helpers import wait_stage_loading
from omni.ui.tests.test_base import OmniUiTest
from pxr import UsdRender
from .test_helper import capture_async


TEST_DIR = str(pathlib.Path(__file__).parent.parent.parent.parent.parent.parent)
EXPECTED_AOVS = [
    "LdrColor",
    "HdrColor",
    "PtDirectIllumation",
    "PtGlobalIllumination",
    "PtReflections",
    "PtRefractions",
    "PtSelfIllumination",
    "PtBackground",
    "PtWorldNormal",
    "PtWorldPos",
    "PtZDepth",
    "PtVolumes",
]


class TestCaptureRenderProduct(OmniUiTest):

    # Before running each test
    async def setUp(self):
        self._usd_context = ''
        self._frames_per_sec_to_wait_for_capture_resource_ready = 60
        test_usd = TEST_DIR + "/data/tests/usd/PTAccumulateTest.usd"
        carb.log_warn(f"testing capture with usd {test_usd}")
        self._context = omni.usd.get_context()
        self._capture_instance = CaptureExtension().get_instance()
        self._file_size_1spp = None
        await self._context.open_stage_async(test_usd)
        await wait_stage_loading()
        await self.wait_n_updates()

    async def tearDown(self) -> None:
        self._capture_instance = None
        await omni.usd.get_context().close_stage_async()
        await self.wait_n_updates()

    async def wait_for_capture_resource_ready(self, n_frames: int = 1):
        await self.wait_n_updates(self._frames_per_sec_to_wait_for_capture_resource_ready * 10 * n_frames)

    async def _make_sure_capture_finishes(self):
        """ call this function at the end of a testcase to make sure the capture it starts will be terminated when
        there is anything goes wrong.
        """
        # the cancel call will cancel the capture if there is the capture is still running, otherwise do nothing
        self._capture_instance.cancel()
        await self.wait_n_updates(20)

    async def _test_render_product_capture(self, filePath, render_product_name, spp, enable_hdr=False, sequence_capture=False, start_frame=0, end_frame=0, expect_outputs=[]):
        viewport_api = get_active_viewport(self._usd_context)
        # Wait until the viewport has valid resources
        await viewport_api.wait_for_rendered_frames()

        # wait for PT to resolve after loading, otherwise it's easy to crash
        await self.wait_for_capture_resource_ready(5)

        # assert True
        options = CaptureOptions()
        options.file_type = ".exr"
        options.output_folder = str(filePath)
        options.hdr_output = enable_hdr
        options.camera = viewport_api.camera_path.pathString
        options.render_preset = omni.kit.capture.viewport.CaptureRenderPreset.PATH_TRACE
        options.render_product = render_product_name
        options.path_trace_spp = spp
        # to reduce memory consumption and save time
        options.res_width = 600
        options.res_height = 337

        if sequence_capture:
            options.capture_every_Nth_frames = 1
            options.start_frame = start_frame
            options.end_frame = end_frame

        self._capture_instance.options = options
        outputs = []
        try:
            outputs = await capture_async(self._capture_instance, expect_outputs=expect_outputs)
        finally:
            self._capture_instance.options = None
            await self._make_sure_capture_finishes()

        return outputs

    def _get_exr_path(self, capture_folder_name, aov_channel, index=1):
        exr_path = os.path.join(str(capture_folder_name), f"Capture{index}_" + aov_channel + ".exr")
        return exr_path

    def _get_captured_image_size(self, image_folder, aov_channel):
        exr_path = os.path.join(str(image_folder), f"Capture1_" + aov_channel + ".exr")
        if os.path.isfile(exr_path):
            return os.path.getsize(exr_path)
        else:
            return 0

    def __get_temp_directoy(self, suffix):
        class NoDeleteTempDir():
            def __init__(self, tmpdir):
                carb.log_info(f"Temporary directory created: {tmpdir}")
                self.name = tmpdir
            def __enter__(self, *args, **kwargs):
                return self.name
            def __exit__(self, *args, **kwargs):
                return
        
        return NoDeleteTempDir(mkdtemp(suffix=f"_{suffix}", dir=omni.kit.test.get_test_output_path()))

    async def test_capture_rp_1_default_rp(self):
        context = omni.usd.get_context()
        stage = context.get_stage()
        rps = []
        for prim in stage.Traverse():
            if prim.IsA(UsdRender.Product):
                prim_path = prim.GetPath().pathString
                if not prim_path.endswith("_MovieRecord_Script"):
                    rps.append(prim_path)
        default_rp_name = rps[1]
        carb.log_info("Test with default render product: {default_rp_name}")

        with self.__get_temp_directoy("vp2_default_rp_0") as image_folder:
            expect_outputs = [self._get_exr_path(image_folder, aov) for aov in ["LdrColor"]]
            outputs = await self._test_render_product_capture(image_folder, default_rp_name, 16, expect_outputs=expect_outputs)
            self.assertEqual(expect_outputs, outputs)

        with self.__get_temp_directoy("vp2_default_rp_1") as image_folder:
            expect_outputs = [self._get_exr_path(image_folder, aov) for aov in ["LdrColor"]]
            outputs = await self._test_render_product_capture(image_folder, default_rp_name, 16, expect_outputs=expect_outputs)
            self.assertEqual(expect_outputs, outputs)

    async def __capture_1spp_render_product(self, image_folder, expect_outputs = []):
        outputs = await self._test_render_product_capture(image_folder, "/Render/RenderView", 1, expect_outputs=expect_outputs)
        self._file_size_1spp = self._get_captured_image_size(image_folder, "HdrColor")
        return outputs

    async def test_capture_rp_2_user_created_rp(self):
        with self.__get_temp_directoy("rp_1spp") as image_folder:
            expect_outputs = [self._get_exr_path(image_folder, aov) for aov in EXPECTED_AOVS]
            outputs = await self.__capture_1spp_render_product(image_folder, expect_outputs)

            # TODO: It is strange that outputs will be different between run this test only and run this test after test_capture_rp_1_default_rp
            # So here only check basic aov outputs
            for expect in expect_outputs:
                self.assertTrue(expect in outputs, f"Output missed: {expect} not found in {outputs}")

            # Capture again to test index increase
            expect_outputs = [self._get_exr_path(image_folder, aov, index=2) for aov in EXPECTED_AOVS]
            outputs = await self._test_render_product_capture(image_folder, "/Render/RenderView", 1, expect_outputs=expect_outputs)
            for expect in expect_outputs:
                self.assertTrue(expect in outputs, f'{expect} not found in {outputs}')

    async def test_capture_rp_3_rp_accumulation(self):
        with self.__get_temp_directoy("rp_48spp") as image_folder:
            expect_outputs = [self._get_exr_path(image_folder, aov) for aov in EXPECTED_AOVS]
            outputs = await self._test_render_product_capture(image_folder, "/Render/RenderView", 48, expect_outputs=expect_outputs)
            for expect in expect_outputs:
                self.assertTrue(expect in outputs, f'{expect} not found in {outputs}')

            # compare result of test_capture_2_user_created_rp images to check accumulation works or not
            # if it works, more spp will result in smaller file size
            file_size_48spp = self._get_captured_image_size(image_folder, "LdrColor")

            if self._file_size_1spp is None:
                with self.__get_temp_directoy("rp_1spp") as image_folder_1spp:
                    await self.__capture_1spp_render_product(image_folder_1spp)

            carb.log_warn(f"File size of 1spp capture is {self._file_size_1spp} bytes, and file size of 48spp capture is {file_size_48spp}")
            self.assertNotEqual(file_size_48spp, self._file_size_1spp)

    async def test_capture_rp_4_rp_sequence(self):
        with self.__get_temp_directoy("rp_seq") as image_folder:
            start_frame = 0
            end_frame = 10
            expect_outputs = []
            for index in range(start_frame, end_frame + 1):
                for aov in EXPECTED_AOVS:
                    expect_outputs.append(os.path.join(str(image_folder), "Capture_frames", f"Capture.{index:04d}_{aov}.exr"))
            outputs = await self._test_render_product_capture(image_folder, "/Render/RenderView", 1, sequence_capture=True, start_frame=start_frame, end_frame=end_frame, expect_outputs=expect_outputs)
            for expect in expect_outputs:
                self.assertTrue(expect in outputs, f"Output missed: {expect} not found in {outputs}")
