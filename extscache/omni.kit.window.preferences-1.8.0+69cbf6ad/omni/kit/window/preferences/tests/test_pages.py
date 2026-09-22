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
from omni.kit.window.preferences import PreferenceBuilder, SettingType, PERSISTENT_SETTINGS_PREFIX


class ShowPagePreferences(PreferenceBuilder):
    def __init__(self):
        super().__init__("test_show_page_func")
        self.set_show_page(False)

    def set_show_page(self, state):
        self.__show_page = state

    def show_page(self) -> bool:
        return self.__show_page

    def build(self):
        pass


class PreferencesTestPages(AsyncTestCase):
    # Before running each test
    async def setUp(self):
        omni.kit.window.preferences.show_preferences_window()

    # After running each test
    async def tearDown(self):
        omni.kit.window.preferences.hide_preferences_window()
        carb.settings.get_settings().set("/app/show_developer_preference_section", False)

    async def _change_values(self):
        # toggle checkboxes
        widgets = ui_test.find_all("Preferences//Frame/**/CheckBox[*]")
        if widgets:
            for w in widgets:
                # don't change audio as it causes exceptions on TC
                if isinstance(w.model, omni.kit.widget.settings.settings_model.SettingModel) and not "audio" in w.model._path:
                    ov = w.model.get_value_as_bool()
                    w.model.set_value(not ov)
                    await ui_test.human_delay(10)
                    w.model.set_value(ov)

    async def test_show_pages(self):
        pages = omni.kit.window.preferences.get_page_list()
        page_names = [page._title for page in pages]
        # is list alpha sorted. Don't compare with fixed list as members can change
        self.assertEqual(page_names, sorted(page_names))
        for page in pages:
            omni.kit.window.preferences.select_page(page)
            await ui_test.human_delay(10)
            await self._change_values()

    async def test_developer_page(self):
        carb.settings.get_settings().set("/app/show_developer_preference_section", True)
        await ui_test.human_delay(10)
        omni.kit.window.preferences.select_page(omni.kit.window.preferences.get_instance()._developer_preferences)
        await ui_test.human_delay(10)
        await self._change_values()

    async def test_show_page_func(self):
        page = omni.kit.window.preferences.register_page(ShowPagePreferences())

        page.set_show_page(False)
        omni.kit.window.preferences.select_page(page)
        omni.kit.window.preferences.rebuild_pages()
        await ui_test.human_delay(50)

        pages = [p.name for p in omni.kit.window.preferences.get_shown_page_list()]
        self.assertFalse("test_show_page_func" in pages)

        page.set_show_page(True)
        omni.kit.window.preferences.select_page(page)
        omni.kit.window.preferences.rebuild_pages()
        await ui_test.human_delay(50)

        pages = [p.name for p in omni.kit.window.preferences.get_shown_page_list()]
        self.assertTrue("test_show_page_func" in pages)

        omni.kit.window.preferences.unregister_page(page)
        del page
