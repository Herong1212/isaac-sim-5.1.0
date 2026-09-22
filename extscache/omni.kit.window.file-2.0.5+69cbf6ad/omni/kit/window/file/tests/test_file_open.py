## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import os
import tempfile
import shutil
import omni.kit.app
import omni.kit.commands
import omni.kit.test
import omni.client

import unittest
from unittest.mock import Mock, patch
from carb.settings import ISettings
from omni.kit.window.file_exporter.test_helper import FileExporterTestHelper
from omni.kit.window.file_importer.test_helper import FileImporterTestHelper
from omni.kit.window.file_importer import get_file_importer
from omni.kit import ui_test
from pxr import Sdf
from ..file_window import get_file_utils_instance as get_window_file
from .test_base import TestFileBase


class TestFileOpen(TestFileBase):
    async def setUp(self):
        await super().setUp()

    # After running each test
    async def tearDown(self):
        await super().tearDown()

    def _mock_get_carb_setting(self, setting: str):
        from ..file_window import SHOW_UNSAVED_LAYERS_DIALOG, IGNORE_UNSAVED_STAGE
        if setting == SHOW_UNSAVED_LAYERS_DIALOG:
            return True
        elif setting == IGNORE_UNSAVED_STAGE:
            return True
        return False

    async def test_file_open(self):
        """Testing file open"""
        omni.usd.get_context().new_stage()
        omni.usd.get_context().set_pending_edit(False)
        omni.kit.window.file.open_stage(f"{self._usd_path}/test_file.usda")
        await self.wait_for_update()
        # check file is loaded
        stage = omni.usd.get_context().get_stage()
        prim_list = [prim.GetPath().pathString for prim in stage.TraverseAll() if not omni.usd.is_hidden_type(prim)]
        self.assertEqual(prim_list, ['/World', '/World/defaultLight'])

    async def test_open(self):
        """Test omni.kit.window.file.open"""
        async with FileImporterTestHelper() as file_importer_helper:
            omni.kit.window.file.open()

            from omni.kit.window.file_importer import get_file_importer
            file_importer = get_file_importer()

            self.assertTrue(file_importer.is_window_visible)

    async def test_file_open_with_new_edit_layer(self):
        """Testing that open with new edit layer executes the callback upon success"""
        omni.usd.get_context().new_stage()
        omni.usd.get_context().set_pending_edit(False)

        layer = Sdf.Layer.CreateNew(self._temp_path)
        self.assertTrue(layer, f"Failed to create temp layer {self._temp_path}.")
        layer.Save()
        layer = None

        mock_callback = Mock()
        async with FileExporterTestHelper() as file_export_helper:
            omni.kit.window.file.open_with_new_edit_layer(self._temp_path, callback=mock_callback)
            await self.wait_for_update()

            await file_export_helper.click_apply_async()
            await self.wait_for_update()

        mock_callback.assert_called_once()

        basename = os.path.basename(self._temp_path)

        # Test default edit layer path since file exporter should save it to the same dir as stage root.
        edit_layer_path = omni.client.make_absolute_url_if_possible(
            self._temp_path, f"{os.path.splitext(basename)[0]}_edit.usd"
        )
        result, _ = await omni.client.stat_async(edit_layer_path)
        self.assertEqual(result, omni.client.Result.OK)

    async def test_file_open_with_new_edit_layer_overwrites_existing_file(self):
        """Testing that open with new edit layer overwrites existing file"""
        layer = Sdf.Layer.CreateNew(self._temp_path)
        self.assertTrue(layer, f"Failed to create temp layer {self._temp_path}.")
        layer.Save()
        layer = None

        layer = Sdf.Layer.CreateNew(self._temp_edit_path)
        self.assertTrue(layer, f"Failed to create temp layer {self._temp_edit_path}.")
        layer.Save()
        layer = None

        async def open_with_new_edit_layer(path):
            async with FileExporterTestHelper() as file_export_helper:
                omni.kit.window.file.open_with_new_edit_layer(path)
                await self.wait_for_update()

                await file_export_helper.click_apply_async()
                await self.wait_for_update()
                await self.click_file_existed_prompt(accept=True)

            current_stage = omni.usd.get_context().get_stage()
            self.assertTrue(current_stage)

            name, _ = os.path.splitext(path)

            expected_layer_name = omni.client.make_file_url_if_possible(f"{name}_edit")
            self.assertTrue(current_stage.GetRootLayer().anonymous)
            self.assertEqual(len(current_stage.GetRootLayer().subLayerPaths), 2)

            sublayer0 = current_stage.GetRootLayer().subLayerPaths[0]
            sublayer1 = current_stage.GetRootLayer().subLayerPaths[1]
            file_name, _ = os.path.splitext(sublayer0)

            self.assertEqual(file_name, expected_layer_name)
            self.assertEqual(os.path.normpath(sublayer1), os.path.normpath(path))

        # First time, creates new edit layer
        await open_with_new_edit_layer(self._temp_path)

        # Second time, creates the same name to make sure it correctly overwrites.
        await omni.usd.get_context().close_stage_async()
        await open_with_new_edit_layer(self._temp_path)

    async def test_file_reopen(self):
        """Testing file reopen"""
        await omni.usd.get_context().new_stage_async()
        omni.usd.get_context().set_pending_edit(False)

        omni.kit.window.file.open_stage(f"{self._usd_path}/4Lights.usda")
        await self.wait_for_update()
        # verify its a unmodified stage
        self.assertFalse(omni.kit.undo.can_undo())

        ## create prim
        omni.kit.commands.execute("CreatePrimWithDefaultXform", prim_type="Sphere")
        # verify its a modified stage
        self.assertTrue(omni.kit.undo.can_undo())

        # Skip unsaved stage prompt
        with patch.object(ISettings, "get", side_effect=self._mock_get_carb_setting):
            omni.kit.window.file.reopen()
            await self.wait_for_update()

        # verify its a unmodified stage
        self.assertFalse(omni.kit.undo.can_undo())

    async def test_file_reopen_with_new_edit_layer(self):

        temp_dir = tempfile.mkdtemp()
        omni.usd.get_context().new_stage()
        omni.usd.get_context().set_pending_edit(False)
        omni.kit.window.file.open_stage(f"{self._usd_path}/4Lights.usda")
        await self.wait_for_update()

        async with FileExporterTestHelper() as file_export_helper:
            stage = omni.usd.get_context().get_stage()
            stage_url = stage.GetRootLayer().identifier

            # Re-open with edit layer
            omni.kit.window.file.open_with_new_edit_layer(stage_url)
            await self.wait_for_update()

            # Save edit layer to temp dir
            temp_url = f"{temp_dir}/4Lights_layer.usd".replace("\\", "/")
            await file_export_helper.click_apply_async(filename_url=temp_url)
            await self.wait_for_update()

        layer = omni.usd.get_context().get_stage().GetRootLayer()
        expected = [temp_url, stage_url.replace("\\", "/")]

        self.assertTrue(layer.anonymous)
        self.assertTrue(len(layer.subLayerPaths) == 2)
        self.assertEqual(layer.subLayerPaths[0], omni.client.make_file_url_if_possible(temp_url))
        self.assertTrue(layer.subLayerPaths[1].endswith("/data/tests/4Lights.usda"))

        # cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

    async def test_show_open_stage_failed_prompt(self):
        """Testing show_open_stage_failed_prompt"""
        omni.usd.get_context().new_stage()
        prompt = get_window_file().ui_handler.show_open_stage_failed_prompt("Test Window File Show Open Stage Failed Prompt")
        await self.wait_for_update()
        prompt.hide()

    async def test_connect_nucleus_when_opening_unreachable_file(self):
        """Testing that when opening an unreachable file, will try to auto-connect to Nucleus server"""
        omni.usd.get_context().new_stage()
        omni.usd.get_context().set_pending_edit(False)
        test_host = "ov-unconnected"
        test_url = f"omniverse://{test_host}/test_file.usda"
        async def mock_stat_async(url: str):
            return (omni.client.Result.ERROR_CONNECTION, None)
        with patch("omni.client.stat_async", side_effect=mock_stat_async),\
            patch.object(omni.kit.window.file.file_window, "connect") as mock_nucleus_connect:
            omni.kit.window.file.open_stage(test_url)
            await self.wait_for_update()
        # Confirm attempt to connect to Nucleus server
        self.assertEqual(mock_nucleus_connect.call_args[0], (test_host, f"omniverse://{test_host}"))

    async def test_file_close(self):
        """Testing try to close a file which has been modified"""
        await omni.usd.get_context().new_stage_async()
        omni.usd.get_context().set_pending_edit(False)

        omni.kit.window.file.open_stage(f"{self._usd_path}/4Lights.usda")
        await self.wait_for_update()

        # modify the stage
        omni.kit.commands.execute("CreatePrimWithDefaultXform", prim_type="Sphere")
        # try to close a modified stage
        mock_callback = Mock()

        with patch.object(ISettings, "get", side_effect=self._mock_get_carb_setting):
            omni.kit.window.file.close(mock_callback)
            await self.wait_for_update()

        mock_callback.assert_called_once()

    async def test_open_with_window_filename_field(self):
        omni.kit.window.file.open()
        await ui_test.human_delay()
        file_importer = get_file_importer()
        self.assertTrue(file_importer.is_window_visible)

        omni.kit.window.file.open()
        await ui_test.human_delay()
        omni.usd.get_context().new_stage()
        omni.usd.get_context().set_pending_edit(False)
        file_importer._dialog.set_current_directory(f"{self._usd_path}")
        file_importer._dialog.set_filename(f"{self._usd_path}/test_file.usda")
        file_importer._dialog._widget._file_bar._on_apply()
        await self.wait_for_update()
        # check file is loaded
        stage = omni.usd.get_context().get_stage()
        prim_list = [prim.GetPath().pathString for prim in stage.TraverseAll() if not omni.usd.is_hidden_type(prim)]
        self.assertEqual(prim_list, ['/World', '/World/defaultLight'])

        omni.kit.window.file.open()
        await ui_test.human_delay()
        omni.usd.get_context().new_stage()
        omni.usd.get_context().set_pending_edit(False)
        # OM-109022: test file name with "\\"
        file_importer._dialog.set_current_directory(f"{self._usd_path}")
        file_importer._dialog.set_filename(f"{self._usd_path}\\test_file.usda")
        file_importer._dialog._widget._file_bar._on_apply()
        await self.wait_for_update()
        # check file is loaded
        stage = omni.usd.get_context().get_stage()
        prim_list = [prim.GetPath().pathString for prim in stage.TraverseAll() if not omni.usd.is_hidden_type(prim)]
        self.assertEqual(prim_list, ['/World', '/World/defaultLight'])
        omni.usd.get_context().new_stage()
        await self.wait_for_update()
