#!/usr/bin/env python3

import carb
from pathlib import Path
import os

import omni.kit.commands
import omni.kit.test
import omni.usd
from omni.mdl.pymdlsdk.tests.render_test import RenderTest

# Try/Cacth import error as test-running for setup can have reduced dependencies
# but run of "setup" tests is a filter after all tests have loaded!
try:
    from omni.rtx.tests import RtxTest, testSettings, postLoadTestSettings
    from omni.rtx.tests.test_common import wait_for_update
    from omni.kit.test_helpers_gfx.compare_utils import ComparisonMetric
except ImportError:
    class RtxTest:
        pass
    pass


# This class is auto-discoverable by omni.kit.test
class MtlxRenderTest(RenderTest):
    EXTENSION_FOLDER_PATH = Path(omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__))
    GOLDEN_DIR = EXTENSION_FOLDER_PATH.joinpath("data/tests/golden")
    USD_DIR = EXTENSION_FOLDER_PATH.joinpath("data/tests/usd")
    WINDOW_SIZE = (1280, 768)
    THRESHOLD: float = 5e-5

    def __init__(self, tests=...):
        super().__init__("mtlx_render", tests)
        self.clearTestOutputs()  # useful for manual test runs

    # Before running each test
    async def setUp(self):
        await super().setUp()

    # After running each test
    async def tearDown(self):
        await super().tearDown()

    # do string replacements and save a new file
    def prepare_temp_file(self, srcFilename, destFilename, replacementMap):
        with open(srcFilename, 'r') as srcFile, \
             open(destFilename, 'w') as destFile:

            src = srcFile.read()
            for key, value in replacementMap.items():
                src = src.replace(key, value)
            destFile.write(src)

    # base test script
    async def run_image_test(self,
                             scene_uri: str,
                             test_case_name: str,
                             threshold = THRESHOLD,
                             metric: carb.imaging.ComparisonMetric = carb.imaging.ComparisonMetric.MEAN_ERROR_SQUARED):
        # open the stage and make it's opened
        full_stage_uri: str = str(self.USD_DIR.joinpath(scene_uri))
        carb.log_info(f"Loading: {full_stage_uri}")
        stage = await self.openTestStage(full_stage_uri)
        self.assertIsNotNone(stage)
        carb.log_info("Rendering image for comparison started.")
        success: bool = await self.capture_and_compare(self.test_name, f"{test_case_name}_{self.test_config_suffix}.png", threshold, metric)
        carb.log_info("Image comparison finished.")
        self.assertTrue(success, "rendered image does not match the reference")
