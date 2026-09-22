import os
import pathlib
import shutil
from typing import Callable
from datetime import datetime, timezone

import carb
import carb.imaging
import carb.settings
import omni.kit.commands
import omni.kit.test
import omni.usd
import omni.rtx.tests.test_common

from omni.kit.test_suite.helpers import open_stage, wait_stage_loading
from pxr import UsdShade, Sdf

EXTENSION_DIR = pathlib.Path(omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__))
TESTS_DIR = EXTENSION_DIR.joinpath('data', 'tests')
USD_DIR = TESTS_DIR.joinpath('usd')

def get_usd_scene_path(usdSubpath: pathlib.Path):
    path = USD_DIR.joinpath(usdSubpath)
    return str(path)

def make_uri_with_scheme(absolute_path_or_uri: str):
    url_parts = omni.client.break_url(absolute_path_or_uri)
    uri = omni.client.make_url(
        scheme=(url_parts.scheme if url_parts.scheme else 'file'),
        host=url_parts.host,
        path=url_parts.path
    )
    return uri

def log_info(message: str):
    R"""Print log message in both streams to see them while developing tests"""
    carb.log_info(message)
    print(message)

class ExpectedBakingResult(object):
    texture: str = "" # filepath to a baked texture
    # TODO constants
    def __init__(self, texture: str = "") -> None:
        self.texture = texture

class RenderTest(omni.rtx.tests.test_common.RtxTest):

    WINDOW_SIZE = (1280, 768)

    EXTENSION_FOLDER_PATH = pathlib.Path(omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__))
    GOLDEN_DIR = EXTENSION_FOLDER_PATH.joinpath("data/golden")
    USD_DIR = EXTENSION_FOLDER_PATH.joinpath("data/usd")
    OUTPUTS_DIR = pathlib.Path(omni.kit.test.get_test_output_path())

    test_name: str = ""
    test_config_suffix: str = ""

    def __init__(self, test_name: str, tests=...):
        self.test_name = test_name
        super().__init__(tests)

    def clearTestOutputs(self):
        output_dir: str = f"{self.OUTPUTS_DIR}/{self.test_name}"
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir)

    async def setUp(self):
        await super().setUp()
        # apply pre load settings
        self.set_settings(omni.rtx.tests.test_common.testSettings)
        additional_settings: dict = {
            "/app/captureFrame/setAlphaTo1": True,
            "/app/renderer/resolution/height": -1,
            "/app/renderer/resolution/width": -1,
            "/app/window/dpiScaleOverride": 1.0,
            "/app/window/scaleToMonitor": False,
            "/app/asyncRendering": False,
            "/renderer/multiGpu/enabled": False,
            "/renderer/multiGpu/autoEnable": False,
            "/omni.kit.plugin/syncUsdLoads": True,
            "/rtx/hydra/materialSyncLoads": True,
            "/rtx/materialDb/syncLoads": True,
            # "/rtx/pathtracing/spp": 4,                                # needs to be set in the `config/extension.toml`
            # "/rtx/pathtracing/totalSpp": 128,                         # needs to be set in the `config/extension.toml`
            "/rtx-transient/resourcemanager/texturestreaming/async": False,
            "/rtx-transient/resourcemanager/genMipsForNormalMaps": False,
            "/renderer/debug/aftermath/enabled": True,
            "/renderer/debug/aftermath/useLightMode": True,
            "/rtx-defaults/post/aa/op": 0,
            # "/rtx/iray/min_samples_per_update": 4,                    # needs to be set in the `config/extension.toml`
            # "/rtx/iray/progressive_rendering_max_samples": 128        # needs to be set in the `config/extension.toml`
            "/rtx/iray/optixDenoiser/enabled": False,
            "/iray/render_synchronous": True,
            "/iray/device/forceCPU": True,                              # drivers to old in CI
            # "/iray/device/cpuEnabled": True,
            "/iray/verifyDriverVersion/enabled": True,
            "/rtx/iray/guided_sampling": False,
        }
        self.set_settings(additional_settings)
        # get the active renderer set in the extension.toml
        self.test_config_suffix: str = carb.settings.get_settings().get("/renderer/active")
        await self.openNewStage() # seems to be required for correctly handling multiple tests in one test class

    async def tearDown(self):
        await self.closeStage()
        # await super().tearDown() this is doing some failed image stuff we don't need

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    async def applyPostLoadSettings(self):
        await omni.kit.app.get_app().next_update_async()
        self.set_settings(omni.rtx.tests.test_common.postLoadTestSettings)
        additional_settings: dict = {
            "/rtx/sceneDb/ambientLightIntensity": 0.0,
            "/rtx/indirectDiffuse/enabled": True,
            "/rtx/directLighting/sampledLighting/enabled": True,
            "/rtx/post/aa/op": 0,
            "/rtx-transient/post/aa/limitedOps": False,
            "/rtx-transient/resourcemanager/texturestreaming/async": False,
            "/rtx-transient/resourcemanager/genMipsForNormalMaps": False,
        }
        self.set_settings(additional_settings)
        await omni.kit.app.get_app().next_update_async()


    async def openNewStage(self):
        await omni.usd.get_context().new_stage_async()
        stage = omni.usd.get_context().get_stage()
        stage.SetDefaultPrim(stage.DefinePrim("/World"))
        await wait_stage_loading()
        await self.applyPostLoadSettings()
        return stage

    async def closeStage(self):
        await omni.kit.app.get_app().next_update_async()
        await omni.usd.get_context().close_stage_async()
        await omni.kit.app.get_app().next_update_async()

    async def openTestStage(self, usdSceneFilepath: str):
        await open_stage(usdSceneFilepath)
        await wait_stage_loading()
        await self.applyPostLoadSettings()
        return omni.usd.get_context().get_stage()

    async def saveStageAs(self, usdSceneFilepath: str):
        await wait_stage_loading()
        await omni.usd.get_context().save_as_stage_async(usdSceneFilepath)
        await wait_stage_loading()

        return omni.usd.get_context().get_stage()

    async def wait_for_update(self, wait_frames:int=10):
        await omni.rtx.tests.test_common.wait_for_update(wait_frames=wait_frames)

    async def capture_and_compare(self, img_subdir: pathlib.Path, golden_img_name, threshold=omni.rtx.tests.test_common.RtxTest.THRESHOLD, metric: carb.imaging.ComparisonMetric = carb.imaging.ComparisonMetric.MEAN_ERROR_SQUARED) -> bool:
        """
        Capture current frame and compare it with the golden image. Assert if the diff is more than given threshold.
        """

        # wait until we have computed the iterations
        if carb.settings.get_settings().get("/renderer/active") == "rtx":
            total_spp: int = carb.settings.get_settings().get_as_int("/rtx/pathtracing/totalSpp")
            carb.log_info(f"Waiting for {total_spp} samples per pixel.")
        elif carb.settings.get_settings().get("/renderer/active") == "iray":
            total_spp: int = carb.settings.get_settings().get_as_int("/rtx/iray/progressive_rendering_max_samples")
            carb.log_info(f"Waiting for {total_spp} samples per pixel.")
        await self.wait_for_update()

        try:
            golden_img_dir = self.GOLDEN_DIR.joinpath(img_subdir)
            output_img_dir = self.OUTPUTS_DIR.joinpath(img_subdir)

            if not golden_img_name:
                golden_img_name = f"{self.__test_name}.png"

            if not pathlib.Path(golden_img_dir).joinpath(golden_img_name).exists():
                carb.log_error(f"Golden image '{golden_img_name}' is missing!")

            return threshold > await self._capture_and_compare(golden_img_name, threshold, output_img_dir, golden_img_dir, metric)
        except:
            carb.log_error(f"Image comparision for '{golden_img_name}' failed.")
            return False
