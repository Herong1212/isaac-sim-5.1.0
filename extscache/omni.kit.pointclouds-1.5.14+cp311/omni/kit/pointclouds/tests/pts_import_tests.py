# Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto. Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
# NOTE:
#   omni.kit.test - std python's unittest module with additional wrapping to add suport for async/await tests
#   For most things refer to unittest docs: https://docs.python.org/3/library/unittest.html
import os
from pathlib import Path

import carb
import omni.kit.commands
import omni.kit.test
import omni.kit.tool.asset_importer as ai

# Import extension python module we are testing with absolute import path, as if we are external user (other extension)
from omni.kit.pointclouds.pts_importer import PTSImporter


# Having a test class dervived from omni.kit.test.AsyncTestCase declared on the root of module will make it auto-discoverable by omni.kit.test
class PTSImportTest(omni.kit.test.AsyncTestCase):
    importer = None
    flowusd_iface = None

    # Before running each test
    async def setUp(self):
        if not ai.is_supported_format(".pts"):
            carb.log_info("Registering pts")
            extension_path = Path(__file__).parent.parent
            PTSImportTest.importer = PTSImporter(extension_path)
            ai.register_importer(PTSImportTest.importer)

    # After running each test
    async def tearDown(self):
        ai.remove_importer(PTSImportTest.importer)
        PTSImportTest.importer = None

    async def test_registration_pts(self):
        ai_instance = ai.AssetImporterExtension.get_instance()

        # Verify the importer was registered
        pts_importers = list(filter(lambda x: isinstance(x, PTSImporter), ai_instance._importers_manager._importers))

        self.assertTrue(len(pts_importers) == 1)

    async def test_supported_format_pts(self):
        self.assertTrue(ai.is_supported_format(".pts"))

    async def test_import_pts(self):
        # extension_path = Path(__file__).parent.parent
        current_path = Path(__file__).parent
        data_path = current_path.parent.parent.parent.parent.joinpath("data")
        test_data_path = str(data_path.joinpath("bunnyData.pts"))

        self.assertTrue(os.path.exists(test_data_path))

        ai_instance = ai.AssetImporterExtension.get_instance()

        # Verify the importer was registered
        pts_importers = list(filter(lambda x: isinstance(x, PTSImporter), ai_instance._importers_manager._importers))

        self.assertTrue(len(pts_importers) == 1)
        importer = pts_importers[0]

        stage = omni.usd.get_context().get_stage()
        if stage is None:
            await omni.kit.stage_templates.new_stage_async()
            stage = omni.usd.get_context().get_stage()

        for importer in ai_instance._importers_manager._importers:
            if isinstance(importer, PTSImporter):
                importer._create_renderer = False

        stage = omni.usd.get_context().get_stage()

        await ai_instance._importers_manager.convert_assets([test_data_path])

        await omni.kit.app.get_app().next_update_async()

        prim = stage.GetPrimAtPath("/World/bunnyData")
        self.assertTrue(prim)

        ai.remove_importer(importer)

        delete_cmd = omni.usd.commands.DeletePrimsCommand(["/World/bunnyData"])
        delete_cmd.do()
