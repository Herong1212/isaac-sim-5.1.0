import omni.usd
from .utils import *
from pathlib import Path
import omni.kit.ui_test as ui_test
import inspect

from .base_ui_test import BaseUiTest


CAPTURE_SETTINGS = [
    ("/app/window/scaleToMonitor", False, True),
    ("/app/window/dpiScaleOverride", 1.0, -1.0),
    ("/app/window/hideUi", True, False),
    ("/app/viewport/forceHideFps", True, False),
    ("/persistent/app/viewport/displayOptions", 0, 0),
    ("/app/runLoops/main/rateLimitFrequency", 60, 60),
    ("/persistent/simulation/minFrameRate", 60, 60),
    ("/app/viewport/grid/enabled", False, True),
    ("/app/docks/disabled", True, False),
    ("/app/asyncRendering", False, True),
    ("/app/hydraEngine/waitIdle", True, False),
    ("/app/renderer/waitIdle", True, False),
    ("/rtx/materialDb/syncLoads", True, False),
    ("/omni.kit.plugin/syncUsdLoads", True, False),
    ("/rtx/hydra/materialSyncLoads", True, False),
    ("/exts/omni.usd/updatePriority", 1, 0),
    ("/renderer/multiGpu/autoEnable", False, True),
    ("/app/captureFrame/setAlphaTo1", True, False),
    ("/rtx/post/aa/op", 0, 0),
    ("/rtx/shadows/enabled", False, True),
    ("/rtx/reflections/enabled", False, True),
    ("/rtx/ambientOcclusion/enabled", False, True),
    ("/rtx/post/tonemap/op", 1, 6),
    ("/rtx/pathtracing/lightcache/cached/enabled", False, True),
    ("/rtx/raytracing/lightcache/spatialCache/enabled", False, True),
    ("/rtx/materialDb/syncLoads", True, True),
    ("/omni.kit.plugin/syncUsdLoads", True, True),
    ("/rtx/hydra/materialSyncLoads", True, True)
]

WINDOW_WIDTH = 1440
WINDOW_HEIGHT = 900


class SamplesTest(BaseUiTest):
    async def setUp(self):
        await super().setUp()
        await self.setup_window(WINDOW_WIDTH, WINDOW_HEIGHT)
        await self.setup_settings(CAPTURE_SETTINGS)

    async def tearDown(self):
        await super().tearDown()
        await self.restore_window()
        self.restore_settings(CAPTURE_SETTINGS)

    # async def test_blend(self):
    #     await self.load_stage(self.usd_data_dir, "TestBlend.usda")
    #     await self.play()
    #     await self.step_frame(24)
    #     await self.snapshot_compare("TestBlend")

    # async def test_filter(self):
    #     await self.load_stage(self.usd_data_dir, "TestFilter.usda")
    #     await self.play()
    #     await self.step_frame(24)
    #     await self.snapshot_compare("TestFilter")
