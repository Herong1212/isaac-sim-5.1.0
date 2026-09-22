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
import asyncio
import os
import shutil
import tempfile
import unittest
from pathlib import Path

import carb
import omni.kit.commands
import omni.kit.test
import omni.kit.tool.asset_importer as ai

# Import extension python module we are testing with absolute import path, as if we are external user (other extension)
from omni.kit.pointclouds.e57_importer import CacheMethod, E57_Renderer, E57Importer, ImportMethod
from pxr import UsdGeom

TEST_SERVER = "omniverse://kit-test-content.ov.nvidia.com/Projects/omni.kit.pointclouds/sources/"


# Having a test class dervived from omni.kit.test.AsyncTestCase declared on the root of module will make it auto-discoverable by omni.kit.test
class ImportTest(omni.kit.test.AsyncTestCase):
    importer = None

    # Before running each test
    async def setUp(self):
        if not ai.is_supported_format(".e57"):
            carb.log_info("Registering e57")
            extension_path = Path(__file__).parent.parent
            ImportTest.importer = E57Importer(extension_path)
            ai.register_importer(ImportTest.importer)

    # After running each test
    async def tearDown(self):
        ai.remove_importer(ImportTest.importer)
        ImportTest.importer = None

    async def test_registration(self):
        ai_instance = ai.AssetImporterExtension.get_instance()

        # Verify the importer was registered
        e57importers = list(filter(lambda x: isinstance(x, E57Importer), ai_instance._importers_manager._importers))

        self.assertTrue(len(e57importers) == 1)

    async def test_supported_format(self):
        self.assertTrue(ai.is_supported_format(".e57"))

    async def test_import_copy(self):
        # extension_path = Path(__file__).parent.parent
        current_path = Path(__file__).parent
        data_path = current_path.parent.parent.parent.parent.joinpath("data")
        test_data_path = str(data_path.joinpath("bunnyDouble.e57"))

        self.assertTrue(os.path.exists(test_data_path))

        ai_instance = ai.AssetImporterExtension.get_instance()

        # Verify the importer was registered
        e57importers = list(filter(lambda x: isinstance(x, E57Importer), ai_instance._importers_manager._importers))

        self.assertTrue(len(e57importers) >= 1)
        importer = e57importers[0]

        stage = omni.usd.get_context().get_stage()
        if stage is None:
            await omni.kit.stage_templates.new_stage_async()
            stage = omni.usd.get_context().get_stage()

        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            for importer in ai_instance._importers_manager._importers:
                if isinstance(importer, E57Importer):
                    importer._copy_data = True
                    importer._renderer = E57_Renderer.NONE
                    importer._export_folder = str(tmpdir)
                    importer._import_method = ImportMethod.LOAD

            await ai_instance._importers_manager.convert_assets([test_data_path])

            await omni.kit.app.get_app().next_update_async()
            await asyncio.sleep(0.5)
            await omni.kit.app.get_app().next_update_async()

            prim = stage.GetPrimAtPath("/World/bunnyDouble")
            self.assertTrue(prim)

            # Interpolation should be set as vertex OM-72158
            points = prim.GetChild("scan")
            if not points:
                points_xform = prim.GetChild("combined_scan")
                self.assertTrue(points_xform)
                points = points_xform.GetChild("scan")
            self.assertTrue(points)
            attr = UsdGeom.Points(points).GetDisplayColorAttr()
            self.assertTrue(attr)
            self.assertTrue(attr.HasValue())
            self.assertTrue(attr.HasMetadata("interpolation"))
            self.assertEqual(attr.GetMetadata("interpolation"), "vertex")

            ai.remove_importer(importer)

            delete_cmd = omni.usd.commands.DeletePrimsCommand(["/World/bunnyDouble"])
            delete_cmd.do()

    async def test_import_to_usd(self):
        # extension_path = Path(__file__).parent.parent
        current_path = Path(__file__).parent
        data_path = current_path.parent.parent.parent.parent.joinpath("data")
        test_data_path = str(data_path.joinpath("bunnyDouble.e57"))

        self.assertTrue(os.path.exists(test_data_path))

        ai_instance = ai.AssetImporterExtension.get_instance()

        # Verify the importer was registered
        e57importers = list(filter(lambda x: isinstance(x, E57Importer), ai_instance._importers_manager._importers))

        self.assertTrue(len(e57importers) >= 1)
        importer = e57importers[0]

        await omni.kit.stage_templates.new_stage_async()
        stage = omni.usd.get_context().get_stage()

        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            for importer in ai_instance._importers_manager._importers:
                if isinstance(importer, E57Importer):
                    importer._renderer = E57_Renderer.NONE
                    importer._export_folder = str(tmpdir)
                    importer._import_method = ImportMethod.LOAD
                    # Those are read from settings in the import dialog, overwrite
                    importer._convert_potree = False
                    importer._generate_local_cache = False

            await ai_instance._importers_manager.convert_assets([test_data_path])

            await omni.kit.app.get_app().next_update_async()
            await asyncio.sleep(10)
            await omni.kit.app.get_app().next_update_async()

            # Create new stage and expect converting the file again because it is now missing
            # (regression test for nvbug 5278369)
            await omni.kit.stage_templates.new_stage_async()

            out_files = os.listdir(tmpdir)
            self.assertTrue("bunnyDouble.usd" in out_files)

            os.remove(os.path.join(tmpdir, "bunnyDouble.usd"))
            out_files = os.listdir(tmpdir)
            self.assertFalse("bunnyDouble.usd" in out_files)

            for importer in ai_instance._importers_manager._importers:
                if isinstance(importer, E57Importer):
                    importer._renderer = E57_Renderer.NONE
                    importer._export_folder = str(tmpdir)
                    importer._cache_method = CacheMethod.LOAD_USD
                    # Those are read from settings in the import dialog, overwrite
                    importer._convert_potree = False
                    importer._generate_local_cache = False

            await ai_instance._importers_manager.convert_assets([test_data_path])

            await omni.kit.app.get_app().next_update_async()
            await asyncio.sleep(10)
            await omni.kit.app.get_app().next_update_async()

            out_files = os.listdir(tmpdir)
            self.assertTrue("bunnyDouble.usd" in out_files)

            ai.remove_importer(importer)

    async def test_import_to_potree(self):
        current_path = Path(__file__).parent
        data_path = current_path.parent.parent.parent.parent.joinpath("data")
        test_data_path = str(data_path.joinpath("bunnyDouble.e57"))

        self.assertTrue(os.path.exists(test_data_path))

        ai_instance = ai.AssetImporterExtension.get_instance()

        # Verify the importer was registered
        e57importers = list(filter(lambda x: isinstance(x, E57Importer), ai_instance._importers_manager._importers))

        self.assertTrue(len(e57importers) >= 1)
        importer = e57importers[0]

        await omni.kit.stage_templates.new_stage_async()

        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            temp_data_path = str(Path(tmpdir).joinpath("bunnyDouble.e57"))
            shutil.copyfile(test_data_path, temp_data_path)
            out_path = Path(tmpdir).joinpath("bunnyDouble.potree")

            for importer in ai_instance._importers_manager._importers:
                if isinstance(importer, E57Importer):
                    importer._renderer = E57_Renderer.NONE
                    importer._import_method = ImportMethod.STREAM
                    # Those are read from settings in the import dialog, overwrite
                    importer._convert_potree = True
                    importer._generate_local_cache = True

            await ai_instance._importers_manager.convert_assets([temp_data_path])

            await omni.kit.app.get_app().next_update_async()
            await asyncio.sleep(10)
            await omni.kit.app.get_app().next_update_async()

            self.assertTrue(os.path.exists(out_path))

            out_files = [f for f in os.listdir(out_path) if os.path.isfile(os.path.join(out_path, f))]

            self.assertTrue("sources.json" in out_files)
            self.assertTrue("cloud.js" in out_files)

            ai.remove_importer(importer)
