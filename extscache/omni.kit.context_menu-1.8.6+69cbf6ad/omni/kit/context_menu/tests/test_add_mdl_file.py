## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
import os
import omni.kit.app
import omni.usd
from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit import ui_test
from pxr import Sdf, UsdShade
from omni.kit.test_suite.helpers import get_test_data_path, wait_stage_loading, arrange_windows
from omni.kit.material.library.test_helper import MaterialLibraryTestHelper


class TestCreateMenuContextMenu(AsyncTestCase):
    # Before running each test
    async def setUp(self):
        # manually arrange windows as linux fails to auto-arrange
        await arrange_windows()

    # After running each test
    async def tearDown(self):
        await wait_stage_loading()

    async def test_viewport_menu_add_mdl_file(self):
        # new stage
        usd_context = omni.usd.get_context()
        await usd_context.new_stage_async()
        stage = usd_context.get_stage()

        # setup
        await ui_test.find("Stage").focus()
        viewport = ui_test.find("Viewport")
        await viewport.focus()

        # click on context menu item
        await viewport.right_click()
        await ui_test.human_delay(50)
        await ui_test.select_context_menu("Create/Material/Add MDL File")
        await ui_test.human_delay()

        # use add material dialog
        async with MaterialLibraryTestHelper() as material_test_helper:
            await material_test_helper.handle_add_material_dialog(get_test_data_path(__name__, "TESTEXPORT.mdl"))

        # wait for material to load & UI to refresh
        await wait_stage_loading()

        # verify
        # NOTE: TESTEXPORT.mdl material is named "Material" so that is the prim created
        shader = UsdShade.Shader(stage.GetPrimAtPath("/Looks/Material/Shader"))
        identifier = shader.GetSourceAssetSubIdentifier("mdl")
        self.assertTrue(identifier == "Material")
