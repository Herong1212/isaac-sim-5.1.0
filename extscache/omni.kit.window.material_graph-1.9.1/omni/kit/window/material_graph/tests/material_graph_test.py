## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
from pathlib import Path
from typing import Optional

import carb
import omni.kit
import omni.kit.app
import omni.ui as ui
import omni.usd
from omni.ui.tests.test_base import OmniUiTest
from pxr import Sdf, UsdShade

from ..graph_window import GraphWindow
from ..usdshade_graph_model import UsdShadeGraphModel

CURRENT_PATH = Path(carb.tokens.get_tokens_interface().resolve("${omni.kit.window.material_graph}/data"))


class TestMaterialGraph(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        app = omni.kit.app.acquire_app_interface()

        self._golden_img_dir = CURRENT_PATH.absolute().resolve().joinpath("tests")

        if float(app.get_kit_version_short()) < 105:
            self._golden_img_dir = self._golden_img_dir.joinpath("kit_lt__105")

    # After running each test
    async def tearDown(self):
        self._golden_img_dir = None
        await super().tearDown()

    async def test_general(self):
        await omni.usd.get_context().new_stage_async()
        stage = omni.usd.get_context().get_stage()

        material = UsdShade.Material.Define(stage, "/material")
        pbrShader = UsdShade.Shader.Define(stage, "/material/PBRShader")
        pbrShader.CreateIdAttr("UsdPreviewSurface")
        pbrShader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.4)
        surface_out = pbrShader.CreateOutput("surface", Sdf.ValueTypeNames.Token)
        material.CreateSurfaceOutput().ConnectToSource(surface_out)

        # ToDo: figure out why we need to add and clear these
        #  ports in order to pass extension test in Usd 22.22
        dsp = material.CreateDisplacementOutput()
        dsp.ClearSource()

        vol = material.CreateVolumeOutput()
        vol.ClearSource()

        window = await self.create_test_window(width=512, height=256)

        graph_window = GraphWindow("Material Graph Test")
        graph_window.flags = ui.WINDOW_FLAGS_NO_SCROLLBAR | ui.WINDOW_FLAGS_NO_TITLE_BAR | ui.WINDOW_FLAGS_NO_RESIZE
        graph_window.position_x = 0
        graph_window.position_y = 0
        graph_window.width = 512
        graph_window.height = 256

        graph_window._import_prims(UsdShadeGraphModel, [material.GetPrim()])

        for _ in range(4):
            await omni.kit.app.get_app().next_update_async()

        # Close the catalog
        graph_window._main_widget._splitter_left._button.call_clicked_fn()

        for _ in range(20):
            await omni.kit.app.get_app().next_update_async()

        await self.finalize_test(golden_img_dir=self._golden_img_dir)

        window = None
        graph_window.destroy()
        graph_window = None
