## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
import carb
import omni.usd
import omni.kit.app
from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit import ui_test


class PreferencesTestPages(AsyncTestCase):
    # Before running each test
    async def setUp(self):
        omni.kit.window.preferences.show_preferences_window()

    async def tearDown(self):
        omni.kit.window.preferences.hide_preferences_window()

    async def test_show_pages(self):
        import omni.kit.material.library.material_config_utils as mc_utils

        pages = omni.kit.window.preferences.get_page_list()

        for page in pages:
            if page.get_title() in ["Material",  "Rendering"]:
                omni.kit.window.preferences.select_page(page)
                await ui_test.human_delay(50)

        mc_utils.save_carb_setting_to_config_file(
            "/app/mdl/nostdpath",
            "/options/noStandardPath"
        )
        mc_utils.save_live_config_to_file()
