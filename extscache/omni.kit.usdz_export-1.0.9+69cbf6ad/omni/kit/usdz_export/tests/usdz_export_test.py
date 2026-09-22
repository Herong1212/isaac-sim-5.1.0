## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import carb
import omni.kit
import omni.usd
import os
import tempfile
import omni.client
import omni.kit.app

from pathlib import Path
from omni.ui.tests.test_base import OmniUiTest
from omni.kit.usdz_export import usdz_export
from omni.kit.window.file_exporter.test_helper import FileExporterTestHelper

OMNI_SERVER = "omniverse://ov-test"

class TestUsdzExport(OmniUiTest):

    async def setUp(self):
        await super().setUp()
        await omni.usd.get_context().new_stage_async()

    def get_test_dir(self):
        token = carb.tokens.get_tokens_interface()
        data_dir = token.resolve("${data}")

        return f"{data_dir}"

    async def wait(self, frames=4):
        for _ in range(frames):
            await omni.kit.app.get_app().next_update_async()

    async def test_export_usdz_file(self):
        usdz_size = 2600000
        usdz_size_tc = 2675966

        current_path = Path(__file__)
        test_data_path = current_path.parent.parent.parent.parent.parent.joinpath("data")
        test_stage_path = str(test_data_path.joinpath("test_stage").joinpath("scene.usd"))
        test_dir = self.get_test_dir()
        export_file_path = Path(test_dir).joinpath("out.usdz").resolve()
        await usdz_export(test_stage_path, export_file_path.__str__())
        self.assertTrue(os.path.isfile(export_file_path.__str__()), 'out.usdz does not exist')
        size = os.stat(export_file_path).st_size
        self.assertTrue(size >= usdz_size and size <= usdz_size_tc, f'File size mismatch, expected {usdz_size} but got {size}')

    async def test_menu_option(self):
        import omni.kit.ui_test as ui_test
        await ui_test.find("Layer").focus()

        root_layer = ui_test.find(
            "Layer//Frame/**/Label[*].text=='Root Layer (Authoring Layer)'"
        )
        self.assertTrue(root_layer)

        await root_layer.right_click()
        await ui_test.select_context_menu("Export USDZ")

        with tempfile.TemporaryDirectory() as tmpdir:
            target_file = f"{tmpdir}/test.usdz"
            async with FileExporterTestHelper() as file_export_helper:
                await file_export_helper.click_apply_async(filename_url=target_file)
            await self.wait(100)

            result, _ = await omni.client.stat_async(target_file)
            self.assertTrue(result == omni.client.Result.OK)
