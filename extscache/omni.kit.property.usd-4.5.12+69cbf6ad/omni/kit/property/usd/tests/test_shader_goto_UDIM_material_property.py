## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
# pylint: disable=missing-function-docstring, missing-class-docstring
import os

import omni.kit.app
import omni.kit.test
import omni.usd
from omni.kit import ui_test
from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit.test_suite.helpers import (
    arrange_windows,
    get_test_data_path,
    open_stage,
    select_prims,
    wait_stage_loading,
)
from omni.kit.window.content_browser import get_content_window
from omni.kit.window.content_browser.test_helper import ContentBrowserTestHelper
from omni.kit.window.file_importer.test_helper import FileImporterTestHelper


class ShaderGotoUDIMMaterialProperty(AsyncTestCase):
    # Before running each test
    async def setUp(self):
        async with ContentBrowserTestHelper() as content_browser_helper:
            await content_browser_helper.set_config_menu_settings(
                {"hide_unknown": True, "hide_thumbnails": True, "show_details": False, "show_udim_sequence": True}
            )

        await arrange_windows("Stage", 128)
        await open_stage(get_test_data_path(__name__, "usd/locate_file_UDIM_material.usda"))

    # After running each test
    async def tearDown(self):
        from omni.kit.test_suite.helpers import wait_stage_loading

        await wait_stage_loading()

    async def test_shader_goto_UDIM_material_property(self):
        await ui_test.find("Content").focus()

        stage_window = ui_test.find("Stage")
        await stage_window.focus()

        await select_prims(["/World/Looks/OmniPBR/Shader"])
        await wait_stage_loading()

        test_data = {
            "sdf_locate_asset_inputs:ao_texture": (False, []),  # ""
            "sdf_locate_asset_inputs:diffuse_texture": (
                True,
                ["T_Hood_A1_Albedo.<UDIM>.png"],
            ),  # T_Hood_A1_1001_Albedo.png
            "sdf_locate_asset_inputs:emissive_mask_texture": (
                True,
                ["T_Hood_A1_Emissive.<UDIM>.png"],
            ),  # granite_a_mask.png
            "sdf_locate_asset_inputs:opacity_texture": (False, []),  # http
            "sdf_locate_asset_inputs:reflectionroughness_texture": (False, []),  # test
        }

        content_browser = get_content_window()

        tests_completed = 0

        for widget_ref in ui_test.find_all("Property//Frame/**/CollapsableFrame[*]"):
            widget_ref.widget.collapsed = widget_ref.widget.title not in ["Shader", "Inputs"]

            if widget_ref.widget.title == "Inputs":
                for sub_widget_ref in widget_ref.find_all("**/CollapsableFrame[*]"):
                    sub_widget_ref.widget.collapsed = False

                    for button_widget_ref in sub_widget_ref.find_all("**/Button[*]"):
                        identifier = button_widget_ref.widget.identifier
                        if identifier in test_data:
                            tests_completed += 1
                            enabled, expected = test_data[identifier]
                            self.assertEqual(button_widget_ref.widget.enabled, enabled)
                            if enabled:
                                content_browser.navigate_to(get_test_data_path(__name__, ""))

                                button_widget_ref.widget.scroll_here_y(0.0)
                                await ui_test.human_delay(10)
                                await button_widget_ref.click()
                                await ui_test.human_delay(10)
                                selected = [os.path.basename(path) for path in content_browser.get_current_selections()]
                                self.assertEqual(selected, expected)

        self.assertTrue(tests_completed == len(test_data))

    async def test_shader_change_UDIM_material_property(self):
        await ui_test.find("Content").focus()

        stage_window = ui_test.find("Stage")
        await stage_window.focus()

        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()

        await select_prims(["/World/Looks/OmniPBR/Shader"])
        await wait_stage_loading()
        await ui_test.human_delay(50)

        # verfiy prim asset
        prim = stage.GetPrimAtPath("/World/Looks/OmniPBR/Shader")
        attr = prim.GetAttribute("inputs:diffuse_texture")
        self.assertTrue(
            attr.Get()
            .resolvedPath.replace("\\", "/")
            .endswith("omni.kit.property.usd/data/tests/usd/textures/T_Hood_A1_Albedo.<UDIM>.png")
        )

        success = False

        for widget_ref in ui_test.find_all("Property//Frame/**/CollapsableFrame[*]"):
            widget_ref.widget.collapsed = widget_ref.widget.title not in ["Shader", "Inputs"]

            if widget_ref.widget.title == "Inputs":
                for sub_widget_ref in widget_ref.find_all("**/CollapsableFrame[*]"):
                    sub_widget_ref.widget.collapsed = False
                    button_widget_ref = sub_widget_ref.find(
                        "**/Button[*].identifier=='sdf_browse_asset_inputs:diffuse_texture'"
                    )
                    if button_widget_ref:
                        # change prim asset
                        await button_widget_ref.click()
                        await ui_test.human_delay(10)

                        url = omni.usd.correct_filename_case(
                            get_test_data_path(__name__, "usd/textures/").replace("\\", "/")
                        )
                        async with FileImporterTestHelper() as file_import_helper:
                            await file_import_helper.select_items_async(url, names=["granite_a_mask2.png"])
                            await file_import_helper.click_apply_async()

                        # verfiy prim asset
                        await ui_test.human_delay(10)
                        self.assertTrue(
                            attr.Get()
                            .resolvedPath.replace("\\", "/")
                            .endswith("omni.kit.property.usd/data/tests/usd/textures/granite_a_mask2.png")
                        )
                        success = True
                        break

        self.assertTrue(success)
