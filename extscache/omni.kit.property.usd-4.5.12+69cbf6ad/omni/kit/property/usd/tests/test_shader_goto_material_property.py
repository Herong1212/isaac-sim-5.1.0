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

from omni.kit.test.async_unittest import AsyncTestCase


class ShaderGotoMaterialProperty(AsyncTestCase):
    # Before running each test
    async def setUp(self):
        from omni.kit.test_suite.helpers import arrange_windows, get_test_data_path, open_stage, wait_stage_loading

        await arrange_windows("Stage", 128)
        await open_stage(get_test_data_path(__name__, "usd/locate_file_material.usda"))
        await wait_stage_loading()

    # After running each test
    async def tearDown(self):
        from omni.kit.test_suite.helpers import wait_stage_loading

        await wait_stage_loading()

    async def test_shader_goto_material_property(self):
        from omni.kit import ui_test
        from omni.kit.test_suite.helpers import get_test_data_path, select_prims, wait_stage_loading
        from omni.kit.window.content_browser import get_content_window

        await ui_test.find("Content").focus()
        await ui_test.find("Stage").focus()

        await select_prims(["/World/Looks/OmniPBR/Shader"])
        await wait_stage_loading()
        await ui_test.human_delay(10)

        test_data = {
            "sdf_locate_asset_inputs:ao_texture": (False, []),  # ""
            "sdf_locate_asset_inputs:diffuse_texture": (True, ["granite_a_mask.png"]),  # granite_a_mask.png
            "sdf_locate_asset_inputs:emissive_mask_texture": (True, ["granite_a_mask.png"]),  # granite_a_mask.png
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
