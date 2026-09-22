## Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
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
from omni.kit.test_suite.helpers import wait_stage_loading

# if this runs 1st on clean build opening filebrowser hangs
class zzPreferencesTestPages(AsyncTestCase):
    # Before running each test
    async def setUp(self):
        omni.kit.window.preferences.show_preferences_window()

    async def test_show_pages(self):
        await wait_stage_loading()
        pages = omni.kit.window.preferences.get_page_list()
        page_names = [page._title for page in pages]
        # as list alpha sorted. Don't compare with fixed list as members can change
        self.assertEqual(page_names, sorted(page_names))
        for page in pages:
            if page.get_title() == "Template Startup":
                omni.kit.window.preferences.select_page(page)
                await ui_test.human_delay(50)
                await ui_test.find("Preferences//Frame/**/Button[*].identifier=='stage_template_browse_0'").click()
                await ui_test.human_delay(50)
                await ui_test.find("Select Template Directory//Frame/**/Button[*].text=='Select'").click()
