## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
from ..layer_watch import LayerWatch
from ..editor import close_all_editors
from omni.ui.tests.test_base import OmniUiTest
from pathlib import Path
from pxr import Usd
from pxr import UsdGeom
from pxr import Tf
import omni.client
import omni.kit
import omni.usd
import os
import time
import unittest
from omni.kit.window.content_browser.test_helper import ContentBrowserTestHelper
from omni.kit import ui_test
import tempfile
import string
import random

OMNI_SERVER = "omniverse://kit.nucleus.ov-ci.nvidia.com"
OMNI_USER = "omniverse"
OMNI_PASS = "omniverse"

class TestUsdaEdit(OmniUiTest):
    def tearDown(self):
        close_all_editors()

    def __set_omni_credentials(self):   # pragma: no cover
        # Save the environment to be able to restore it
        self.__OMNI_USER = os.environ.get("OMNI_USER", None)
        self.__OMNI_PASS = os.environ.get("OMNI_PASS", None)
        # Set the credentials
        os.environ["OMNI_USER"] = OMNI_USER
        os.environ["OMNI_PASS"] = OMNI_PASS

    def __restore_omni_credentials(self):   # pragma: no cover
        if self.__OMNI_USER is not None:
            os.environ["OMNI_USER"] = self.__OMNI_USER
        else:
            os.environ.pop("OMNI_USER")
        if self.__OMNI_PASS is not None:
            os.environ["OMNI_PASS"] = self.__OMNI_PASS
        else:
            os.environ.pop("OMNI_PASS")

    async def test_open_file(self):
        # New stage with a sphere
        await omni.usd.get_context().new_stage_async()
        omni.kit.commands.execute("CreatePrim", prim_path="/Sphere", prim_type="Sphere", select_new_prim=False)

        stage = omni.usd.get_context().get_stage()

        # Create USDA
        usda_filename = LayerWatch().start_watch(stage.GetRootLayer().identifier)

        # Check it's a valid stage
        duplicate = Usd.Stage.Open(usda_filename)
        self.assertTrue(duplicate)

        # Check it has the sphere
        sphere = duplicate.GetPrimAtPath("/Sphere")
        self.assertTrue(sphere)

        UsdGeom.Cylinder.Define(duplicate, '/Cylinder')
        duplicate.Save()

        await omni.kit.app.get_app().next_update_async()

        # Check cylinder is created
        cylinder = duplicate.GetPrimAtPath("/Cylinder")
        self.assertTrue(cylinder)

        # Remove USDA
        LayerWatch().stop_watch(stage.GetRootLayer().identifier)

        # Check the file is removed
        self.assertFalse(Path(usda_filename).exists())

        await omni.kit.app.get_app().next_update_async()

    async def test_edit_file_via_content_browser(self):
        # create a temporary folder/usd file
        await omni.usd.get_context().new_stage_async()
        stage = omni.usd.get_context().get_stage()
        root_layer = stage.GetRootLayer()

        while True:
            letters = string.ascii_lowercase
            dir_name = "kit_usda_" + "".join(random.choice(letters) for i in range(8))
            tmp_folder_path = Path(tempfile.gettempdir()).joinpath(dir_name)
            if not tmp_folder_path.exists():
                break
        tmp_folder_path.mkdir()

        tmp_file_path = tmp_folder_path.joinpath(omni.usd.make_valid_identifier(Path(root_layer.identifier).stem) + ".usda")
        root_layer.Export(tmp_file_path.resolve().__str__())

        async with ContentBrowserTestHelper() as content_browser_helper:
            await content_browser_helper.navigate_to_async(tmp_folder_path.__str__())
            await self.wait_n_updates(50)
            await content_browser_helper.refresh_current_directory()
            await self.wait_n_updates(50)
            await content_browser_helper.toggle_grid_view_async(True)
            await self.wait_n_updates(50)
            await content_browser_helper.refresh_current_directory()
            await self.wait_n_updates(50)
            item = await content_browser_helper.get_gridview_item_async(tmp_file_path.name)
            if item is None:
                return

            await item.right_click()
            await self.wait_n_updates(50)
            await ui_test.select_context_menu("Edit...")

        tmp_file_path = tmp_file_path.resolve().__str__().replace("\\", "/")
        usda_item = LayerWatch()._find_item(tmp_file_path)
        Path(usda_item.file_name).touch()
        await LayerWatch().wait_import_async(tmp_file_path)

        # Clean up
        for f in tmp_folder_path.iterdir():
            if f.is_file():
                f.unlink()
        tmp_folder_path.rmdir()

    async def test_edit_file_via_layer_window(self):
        await omni.usd.get_context().new_stage_async()

        root_item = ui_test.find("Layer//Frame/**/Label[*].text=='Root Layer (Authoring Layer)'")
        self.assertTrue(root_item)
        await root_item.right_click()
        await self.wait_n_updates(50)
        await ui_test.select_context_menu("Edit...")

        # TODO: edit the file to trigger import, and check if the modified value is correct
        stage = omni.usd.get_context().get_stage()
        layer_identifier = stage.GetRootLayer().identifier
        usda_item = LayerWatch()._find_item(layer_identifier)
        self.assertTrue(usda_item)

        duplicate = Usd.Stage.Open(usda_item.file_name)
        self.assertTrue(duplicate)

        # Check it has the sphere
        # sphere = duplicate.GetPrimAtPath("/Sphere")
        # self.assertTrue(sphere)

        UsdGeom.Cylinder.Define(duplicate, '/Cylinder')
        duplicate.Save()
        Path(usda_item.file_name).touch()

        # await omni.kit.app.get_app().next_update_async()
        await LayerWatch().wait_import_async(layer_identifier)

        # Check cylinder is created
        cylinder = stage.GetPrimAtPath("/Cylinder")
        self.assertTrue(cylinder)

    @unittest.skip("Works locally, but fails on TC for server connection in linux -> flaky")
    async def test_edit_file_on_nucleus(self): # pragma: no cover
        self.__set_omni_credentials()

        # Create a new stage on server
        temp_usd_folder = f"{OMNI_SERVER}/Users/test_usda_edit_{str(time.perf_counter_ns())}"
        temp_usd_file_path = f"{temp_usd_folder}/test_edit_file_on_nucleus.usd"

        # cleanup first
        await omni.client.delete_async(temp_usd_folder)
        # create the folder
        result = await omni.client.create_folder_async(temp_usd_folder)
        self.assertEqual(result, omni.client.Result.OK)

        stage = Usd.Stage.CreateNew(temp_usd_file_path)
        await omni.kit.app.get_app().next_update_async()
        UsdGeom.Xform.Define(stage, '/xform')
        UsdGeom.Sphere.Define(stage, '/xform/sphere')
        await omni.kit.app.get_app().next_update_async()
        stage.Save()

        # Start watching and edit the temp stage
        usda_filename = LayerWatch().start_watch(stage.GetRootLayer().identifier)
        temp_stage = Usd.Stage.Open(usda_filename)
        # Create another sphere
        UsdGeom.Sphere.Define(temp_stage, '/xform/sphere1')
        # Save the stage
        temp_stage.Save()

        # UsdStage saves the temorary file and renames it to usda, so we need
        # to touch it to let LayerWatch know it's changed.
        Path(usda_filename).touch()

        # Small delay because watchdog in LayerWatch doesn't call the callback
        # right away. So we need to give it some time.
        await LayerWatch().wait_import_async(stage.GetRootLayer().identifier)

        # Remove USDA
        LayerWatch().stop_watch(stage.GetRootLayer().identifier)

        stage.Reload()
        # Check the second sphere is there
        sphere = stage.GetPrimAtPath("/xform/sphere1")
        self.assertTrue(sphere)

        # Remove the temp folder
        result = await omni.client.delete_async(temp_usd_folder)
        self.assertEqual(result, omni.client.Result.OK)

        self.__restore_omni_credentials()
