## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import carb
import omni.kit.app
import omni.kit.test
import omni.usd
from omni.kit import ui_test
from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit.test_suite.helpers import arrange_windows

PERSISTENT_SETTINGS_PREFIX = "/persistent"


class TestUsdPreferences(AsyncTestCase):
    def set_defaults():
        carb.settings.get_settings().set(
            PERSISTENT_SETTINGS_PREFIX + "/exts/omni.kit.property.usd/large_selection", 100
        )
        carb.settings.get_settings().set(
            PERSISTENT_SETTINGS_PREFIX + "/exts/omni.kit.property.usd/raw_widget_multi_selection_limit", 1
        )

    # Before running each test
    async def setUp(self):
        await arrange_windows()
        TestUsdPreferences.set_defaults()

    # After running each test
    async def tearDown(self):
        TestUsdPreferences.set_defaults()
        omni.kit.window.preferences.hide_preferences_window()
        await ui_test.human_delay(50)

    async def test_usd_preferences_test(self, retry_count=0):
        try:
            omni.kit.window.preferences.show_preferences_window()
            await ui_test.human_delay(50)

            for page in omni.kit.window.preferences.get_page_list():
                if page.get_title() == "Property Widgets":
                    omni.kit.window.preferences.select_page(page)
                    await ui_test.human_delay(50)

                    frame = ui_test.find(
                        "Preferences//Frame/**/CollapsableFrame[*].identifier=='preferences_builder_Property Window'"
                    )

                    w = frame.find("**/IntDrag[*].identifier=='large_selection'")
                    await w.click(double=True)
                    await w.input("10")

                    w = frame.find("**/IntDrag[*].identifier=='raw_widget_multi_selection_limit'")
                    await w.click(double=True)
                    await w.input("20")

                    await ui_test.human_delay(50)

                    self.assertEqual(
                        carb.settings.get_settings().get(
                            PERSISTENT_SETTINGS_PREFIX + "/exts/omni.kit.property.usd/large_selection"
                        ),
                        10,
                    )
                    self.assertEqual(
                        carb.settings.get_settings().get(
                            PERSISTENT_SETTINGS_PREFIX + "/exts/omni.kit.property.usd/raw_widget_multi_selection_limit"
                        ),
                        20,
                    )
                    return None

            self.assertTrue(False, "Property Widgets preferences page not found")  # pragma: no cover
        except Exception as ex:
            if retry_count < 5:
                print("retrying test_usd_preferences_test...")
                return await self.test_usd_preferences_test(retry_count + 1)
            raise ex
