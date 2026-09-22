# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from omni.kit.stage.mdl_converter import *
from pxr import UsdGeom
from pxr import UsdShade
import omni.kit.test
import omni.kit.ui_test as ui_test
from omni.kit.test_suite.helpers import arrange_windows, open_stage, wait_stage_loading
from pathlib import Path
from omni.mdl.pymdlsdk.tests.render_test import RenderTest

class Test(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        await omni.kit.test_suite.helpers.arrange_windows("Stage", 800, 600)
        await omni.usd.get_context().new_stage_async()
        self.stage = omni.usd.get_context().get_stage()
        self.assertIsNotNone(self.stage)

    async def tearDown(self):
        await omni.usd.get_context().close_stage_async()

    def _find_mtl_item(self, text):
        # TODO: not sure why there's two items with the same realpath in the stage window, for now pick the first one
        item = ui_test.find_all(f"Stage//Frame/**/Label[*].text=='{text}'")[0]
        self.assertTrue(item)
        return item

    async def test_mdl_converter(self):
        """Testing omni.kit.stage.mdl_converter"""
        sphere = UsdGeom.Sphere.Define(self.stage, "/Sphere01")
        await ui_test.human_delay(20)

        material = UsdShade.Material.Define(self.stage, "/Material01")
        await ui_test.human_delay(20)

        UsdShade.MaterialBindingAPI(sphere.GetPrim()).Bind(material)

        material = self._find_mtl_item("Material01")
        self.assertIsNotNone(material)
        await material.right_click()

        context_menu = await ui_test.get_context_menu()
        self.assertIsNotNone(context_menu)
        context_options = context_menu["_"]

        self.assertTrue("Export to MDL" in context_options)
        self.assertTrue("Expand Graph" in context_options)

    async def test_mdl_converter_ui(self):
        EXTENSION_FOLDER_PATH = Path(omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__))
        USD_DIR = EXTENSION_FOLDER_PATH.joinpath("data/usd")
        test_content_root = USD_DIR  # for local tests
        scene_uri=f"{test_content_root}/basics/composition_basics.usda"

        usd_context = omni.usd.get_context()
        await open_stage(scene_uri, usd_context)
        await wait_stage_loading()
        stage = usd_context.get_stage()
        self.assertIsNotNone(stage)
        await ui_test.human_delay(20)

        # Expand TreeView
        stage_tree = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
        stage_tree.widget.set_expanded(None, True, True)
        await ui_test.human_delay(20)

        material = self._find_mtl_item("ShaderKnobMaterial")
        self.assertIsNotNone(material)
        await material.right_click()

        await ui_test.select_context_menu("Expand Graph")
        await ui_test.human_delay(20)

        dialog = ui_test.find("Expand Material")
        self.assertIsNotNone(dialog)
        button = dialog.find("**/Button[*].text=='Yes'")
        self.assertIsNotNone(button)
        await button.click()

        material = self._find_mtl_item("ShaderKnobMaterial")
        self.assertIsNotNone(material)
        await material.right_click()

        await ui_test.select_context_menu("Export to MDL")

        # dialog = ui_test.find("Convert Material to MDL and Export As...")
        # self.assertIsNotNone(dialog)
        # All the attempts below are failing
        # buttons = dialog.find_all("**/Button[*]")
        # labels = dialog.find_all("**/Label[*]")
        # button = dialog.find("**/Button[*].text=='Export'")
        # button = dialog.find("**/Button[*].text=='Cancel'")
        # self.assertIsNotNone(button)
        # await button.click()

        material = self._find_mtl_item("Invalid")
        self.assertIsNotNone(material)
        await material.right_click()

        await ui_test.select_context_menu("Export to MDL")

        dialog = ui_test.find("Convert Material to MDL")
        self.assertIsNotNone(dialog)
        button = dialog.find("**/Button[*].text=='Ok'")
        self.assertIsNotNone(button)
        await button.click()

        material = self._find_mtl_item("Invalid")
        self.assertIsNotNone(material)
        await material.right_click()

        await ui_test.select_context_menu("Expand Graph")
