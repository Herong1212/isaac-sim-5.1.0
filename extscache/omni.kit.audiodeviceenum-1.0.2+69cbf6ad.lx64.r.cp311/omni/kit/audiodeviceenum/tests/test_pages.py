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

    # After running each test
    async def tearDown(self):
        omni.kit.window.preferences.hide_preferences_window()
        carb.settings.get_settings().set("/app/show_developer_preference_section", False)

    async def test_show_pages(self):
        # NOTE: Cannot test changing values in page as causes errors on TC
        for page in omni.kit.window.preferences.get_page_list():
            if page.get_title() == "Audio":
                omni.kit.window.preferences.select_page(page)
                await ui_test.human_delay(10)

        widgets = ui_test.find_all("Preferences//Frame/**/Button[*]")
        for w in widgets:
            if w.widget.text in ["Refresh", "Apply"]:
                await w.click()
                await ui_test.human_delay(10)
