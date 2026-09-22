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
import omni.ui as ui
import omni.kit.ui_test as ui_test
from omni.ui.tests.test_base import OmniUiTest
from pathlib import Path
from ..settings_widget import create_setting_widget, create_setting_widget_combo, SettingType, SettingWidgetType, SettingsWidgetBuilder, SettingsSearchableCombo
from ..style import get_ui_style_name, get_style

PERSISTENT_SETTINGS_PREFIX = "/persistent"


class TestSettings(OmniUiTest):
    pass

    # Before running each test
    async def setUp(self):
        await super().setUp()

        extension_path = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
        self._golden_img_dir = Path(extension_path).joinpath("data").joinpath("tests").joinpath("golden_img").absolute()

        # create settings
        carb.settings.get_settings().set_bool(PERSISTENT_SETTINGS_PREFIX + "/test/test/test_bool", True)
        carb.settings.get_settings().set_float(PERSISTENT_SETTINGS_PREFIX + "/test/test/test_float", 1.0)
        carb.settings.get_settings().set_int(PERSISTENT_SETTINGS_PREFIX + "/test/test/test_int", 27)
        carb.settings.get_settings().set_string(PERSISTENT_SETTINGS_PREFIX + "/test/test/test_str", "test-test")
        carb.settings.get_settings().set_float_array(PERSISTENT_SETTINGS_PREFIX + "/test/test/test_color3", [1, 2, 3])
        carb.settings.get_settings().set_float_array(PERSISTENT_SETTINGS_PREFIX + "/test/test/test_double2", [1.5, 2.7])
        carb.settings.get_settings().set_float_array(
            PERSISTENT_SETTINGS_PREFIX + "/test/test/test_double3", [2.7, 1.5, 9.2]
        )
        carb.settings.get_settings().set_int_array(PERSISTENT_SETTINGS_PREFIX + "/test/test/test_int2", [10, 13])
        carb.settings.get_settings().set_string(PERSISTENT_SETTINGS_PREFIX + "/test/test/test_combo1", "AAAAAA")
        carb.settings.get_settings().set_string(PERSISTENT_SETTINGS_PREFIX + "/test/test/test_combo2", "BBBBBB")
        carb.settings.get_settings().set_string(PERSISTENT_SETTINGS_PREFIX + "/test/test/test_combo3", "CCCCCC")
        carb.settings.get_settings().set_string(PERSISTENT_SETTINGS_PREFIX + "/test/test/test_combo4", "DDDDDD")
        carb.settings.get_settings().set_string(PERSISTENT_SETTINGS_PREFIX + "/test/test/test_combo5", "")
        carb.settings.get_settings().set_string(PERSISTENT_SETTINGS_PREFIX + "/test/test/test_combo7", "cccccc")
        carb.settings.get_settings().set_string(PERSISTENT_SETTINGS_PREFIX + "/test/test/test_combo8", "BBBBBB")
        carb.settings.get_settings().set_string(PERSISTENT_SETTINGS_PREFIX + "/test/test/test_combo9", "DDDDDD")
        carb.settings.get_settings().set_int(PERSISTENT_SETTINGS_PREFIX + "/test/test/test_combo10", 2)
        carb.settings.get_settings().set_int(PERSISTENT_SETTINGS_PREFIX + "/test/test/test_combo11", 2)
        carb.settings.get_settings().set_int(PERSISTENT_SETTINGS_PREFIX + "/test/test/test_combo12", 3)
        carb.settings.get_settings().set_string(PERSISTENT_SETTINGS_PREFIX + "/test/test/test_combo13", "EEEEEE")
        carb.settings.get_settings().set_int(PERSISTENT_SETTINGS_PREFIX + "/test/test/test_combo14", 1)
        carb.settings.get_settings().set_bool(PERSISTENT_SETTINGS_PREFIX + "/test/test/test_combo15", False)

        carb.settings.get_settings().set_string("/rtx/test_asset", "/home/")
        carb.settings.get_settings().set_string("/rtx-defaults/test_asset", "/home/")

        carb.settings.get_settings().set_string(
            PERSISTENT_SETTINGS_PREFIX + "/test/test/test_radiobutton/value",
            "A"
        )
        carb.settings.get_settings().set_string_array(
            PERSISTENT_SETTINGS_PREFIX + "/test/test/test_radiobutton/items",
            ["A", "B", "C", "D"]
        )

        # FIXME: Test fails when using set_string
        carb.settings.get_settings().set_default_string(PERSISTENT_SETTINGS_PREFIX + "/test/test/test_combo6", "cheese")

    # After running each test
    async def tearDown(self):
        await super().tearDown()
        omni.kit.window.preferences.hide_preferences_window()

    # Test(s)
    def _build_window(self, window):
        with window.frame:
            with ui.VStack(height=-0, style=get_style()):
                with ui.CollapsableFrame(title="create_setting_widget"):
                    with ui.VStack():
                        with ui.HStack(height=24):
                            omni.ui.Label("bool", word_wrap=True, width=ui.Percent(35))
                            create_setting_widget(PERSISTENT_SETTINGS_PREFIX + "/test/test/test_bool", SettingType.BOOL)
                        with ui.HStack(height=24):
                            omni.ui.Label("float", word_wrap=True, width=ui.Percent(35))
                            create_setting_widget(
                                PERSISTENT_SETTINGS_PREFIX + "/test/test/test_float", SettingType.FLOAT
                            )
                        with ui.HStack(height=24):
                            omni.ui.Label("int", word_wrap=True, width=ui.Percent(35))
                            create_setting_widget(PERSISTENT_SETTINGS_PREFIX + "/test/test/test_int", SettingType.FLOAT)
                        with ui.HStack(height=24):
                            omni.ui.Label("string", word_wrap=True, width=ui.Percent(35))
                            create_setting_widget(
                                PERSISTENT_SETTINGS_PREFIX + "/test/test/test_str", SettingType.STRING
                            )
                        with ui.HStack(height=24):
                            omni.ui.Label("color3", word_wrap=True, width=ui.Percent(35))
                            create_setting_widget(
                                PERSISTENT_SETTINGS_PREFIX + "/test/test/test_color3", SettingType.COLOR3
                            )
                        with ui.HStack(height=24):
                            omni.ui.Label("double2", word_wrap=True, width=ui.Percent(35))
                            create_setting_widget(
                                PERSISTENT_SETTINGS_PREFIX + "/test/test/test_double2", SettingType.DOUBLE2
                            )
                        with ui.HStack(height=24):
                            omni.ui.Label("double3", word_wrap=True, width=ui.Percent(35))
                            create_setting_widget(
                                PERSISTENT_SETTINGS_PREFIX + "/test/test/test_double3", SettingType.DOUBLE3
                            )
                        with ui.HStack(height=24):
                            omni.ui.Label("int2", word_wrap=True, width=ui.Percent(35))
                            create_setting_widget(PERSISTENT_SETTINGS_PREFIX + "/test/test/test_int2", SettingType.INT2)

                        with ui.HStack(height=24):
                            omni.ui.Label("radiobutton", word_wrap=True, width=ui.Percent(35))
                            create_setting_widget(
                                PERSISTENT_SETTINGS_PREFIX + "/test/test/test_radiobutton/value",
                                SettingWidgetType.RADIOBUTTON
                            )

                ui.Spacer(height=20)

                with ui.CollapsableFrame(title="create_setting_widget_combo"):
                    with ui.VStack():
                        with ui.HStack(height=24):
                            omni.ui.Label("combo1", word_wrap=True, width=ui.Percent(35))
                            create_setting_widget_combo(
                                PERSISTENT_SETTINGS_PREFIX + "/test/test/test_combo1",
                                ["AAAAAA", "BBBBBB", "CCCCCC", "DDDDDD"],
                            )
                        with ui.HStack(height=24):
                            omni.ui.Label("combo2", word_wrap=True, width=ui.Percent(35))
                            create_setting_widget_combo(
                                PERSISTENT_SETTINGS_PREFIX + "/test/test/test_combo2",
                                ["AAAAAA", "BBBBBB", "CCCCCC", "DDDDDD"],
                            )
                        with ui.HStack(height=24):
                            omni.ui.Label("combo3", word_wrap=True, width=ui.Percent(35))
                            create_setting_widget_combo(
                                PERSISTENT_SETTINGS_PREFIX + "/test/test/test_combo3",
                                ["AAAAAA", "BBBBBB", "CCCCCC", "DDDDDD"],
                            )
                        with ui.HStack(height=24):
                            omni.ui.Label("combo4", word_wrap=True, width=ui.Percent(35))
                            create_setting_widget_combo(
                                PERSISTENT_SETTINGS_PREFIX + "/test/test/test_combo4",
                                ["AAAAAA", "BBBBBB", "CCCCCC", "DDDDDD"],
                            )
                        with ui.HStack(height=24):
                            omni.ui.Label("combo5", word_wrap=True, width=ui.Percent(35))
                            create_setting_widget_combo(
                                PERSISTENT_SETTINGS_PREFIX + "/test/test/test_combo5",
                                ["AAAAAA", "BBBBBB", "CCCCCC", "DDDDDD"],
                            )
                        # Test setting_is_index=False and items as dictionary - jira OM-117775
                        with ui.HStack(height=24):
                            omni.ui.Label("combo7", word_wrap=True, width=ui.Percent(35))
                            create_setting_widget_combo(
                                PERSISTENT_SETTINGS_PREFIX + "/test/test/test_combo7",
                                {
                                    "AAAAAA": "aaaaaa",
                                    "BBBBBB": "bbbbbb",
                                    "CCCCCC": "cccccc",
                                    "DDDDDD": "dddddd",
                                    "EEEEEE": "eeeeee",
                                },
                                setting_is_index=False
                            )
                        # Test setting_is_index=False and items as list
                        with ui.HStack(height=24):
                            omni.ui.Label("combo8", word_wrap=True, width=ui.Percent(35))
                            create_setting_widget_combo(
                                PERSISTENT_SETTINGS_PREFIX + "/test/test/test_combo8",
                                ["AAAAAA", "BBBBBB", "CCCCCC", "DDDDDD", "EEEEEE"],
                                setting_is_index=False
                            )
                        # Test setting_is_index=True and items as dictionary - no matched value, match label
                        with ui.HStack(height=24):
                            omni.ui.Label("combo9", word_wrap=True, width=ui.Percent(35))
                            create_setting_widget_combo(
                                PERSISTENT_SETTINGS_PREFIX + "/test/test/test_combo9",
                                {
                                    "AAAAAA": "aaaaaa",
                                    "BBBBBB": "bbbbbb",
                                    "CCCCCC": "cccccc",
                                    "DDDDDD": "dddddd",
                                    "EEEEEE": "eeeeee",
                                },
                                setting_is_index=True
                            )
                        # Test setting_is_index=True and items as dictionary, values as int
                        with ui.HStack(height=24):
                            omni.ui.Label("combo10", word_wrap=True, width=ui.Percent(35))
                            create_setting_widget_combo(
                                PERSISTENT_SETTINGS_PREFIX + "/test/test/test_combo10",
                                {
                                    "AAAAAA": 1,
                                    "BBBBBB": 2,
                                    "CCCCCC": 3,
                                    "DDDDDD": 4,
                                    "EEEEEE": 5,
                                },
                                setting_is_index=True
                            )
                        # Test setting_is_index=True and items as list, values as index int
                        with ui.HStack(height=24):
                            omni.ui.Label("combo11", word_wrap=True, width=ui.Percent(35))
                            create_setting_widget_combo(
                                PERSISTENT_SETTINGS_PREFIX + "/test/test/test_combo11",
                                ["AAAAAA", "BBBBBB", "CCCCCC", "DDDDDD", "EEEEEE"],
                                setting_is_index=True
                            )
                        # Test setting_is_index not given and items as list, values as index int
                        with ui.HStack(height=24):
                            omni.ui.Label("combo12", word_wrap=True, width=ui.Percent(35))
                            create_setting_widget_combo(
                                PERSISTENT_SETTINGS_PREFIX + "/test/test/test_combo12",
                                ["AAAAAA", "BBBBBB", "CCCCCC", "DDDDDD", "EEEEEE"]
                            )
                        # Test setting_is_index not given and items as list, values as string
                        with ui.HStack(height=24):
                            omni.ui.Label("combo13", word_wrap=True, width=ui.Percent(35))
                            create_setting_widget_combo(
                                PERSISTENT_SETTINGS_PREFIX + "/test/test/test_combo13",
                                ["AAAAAA", "BBBBBB", "CCCCCC", "DDDDDD", "EEEEEE"],
                            )
                        # Test setting_is_index not given and items as list, values bool
                        with ui.HStack(height=24):
                            omni.ui.Label("combo14", word_wrap=True, width=ui.Percent(35))
                            create_setting_widget_combo(
                                PERSISTENT_SETTINGS_PREFIX + "/test/test/test_combo14",
                                [True, False],
                            )
                        # Test setting_is_index not given and items as dict
                        with ui.HStack(height=24):
                            omni.ui.Label("combo15", word_wrap=True, width=ui.Percent(35))
                            create_setting_widget_combo(
                                PERSISTENT_SETTINGS_PREFIX + "/test/test/test_combo15",
                                {"Yes": True, "No": False}
                            )

                ui.Spacer(height=20)

                with ui.CollapsableFrame(title="create_setting_widget_asset"):
                    with ui.VStack():
                        with ui.HStack(height=24):
                            path = "/rtx/test_asset"
                            omni.ui.Label("asset", word_wrap=True, width=ui.Percent(35))
                            widget, model = create_setting_widget(path, "ASSET")
                            ui.Spacer(width=4)
                            button = SettingsWidgetBuilder._build_reset_button(path)
                            model.set_reset_button(button)

                ui.Spacer(height=20)

                with ui.CollapsableFrame(title="create_searchable_widget_combo"):
                    with ui.VStack():
                        with ui.HStack(height=24):
                            path = PERSISTENT_SETTINGS_PREFIX + "/test/test/test_combo6"
                            SettingsWidgetBuilder._create_label("Searchable", path, "Search Me...")
                            widget = SettingsSearchableCombo(path, {"Whiskey": "whiskey", "Wine": "Wine", "plain": "Plain", "cheese": "Cheese", "juice": "Juice"}, "cheese")

    # Test(s)
    async def test_widgets_golden(self):
        window = await self.create_test_window(width=300, height=800)
        self._build_window(window)
        await ui_test.human_delay(50)
        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="test_widgets.png")


    async def test_widget_ui(self):
        window = ui.Window("Test Window", width=600, height=800)
        self._build_window(window)
        await ui_test.human_delay(10)

        widget = ui_test.find("Test Window//Frame/**/StringField[*].identifier=='AssetPicker_path'")
        widget.model.set_value("/cheese/")
        await ui_test.human_delay(10)
        await ui_test.find("Test Window//Frame/**/Rectangle[*].identifier=='/rtx/test_asset_reset'").click()
        await ui_test.human_delay(10)
        await ui_test.find("Test Window//Frame/**/Button[*].identifier=='AssetPicker_locate'").click()
        await ui_test.human_delay(10)
        await widget.input("my hovercraft is full of eels")
        await ui_test.human_delay(10)
        await ui_test.find("Test Window//Frame/**/Rectangle[*].identifier=='/rtx/test_asset_reset'").click()
        await ui_test.human_delay(10)

#        await ui_test.human_delay(1000)

    async def test_show_pages(self):
        omni.kit.window.preferences.show_preferences_window()
        pages = omni.kit.window.preferences.get_page_list()
        for page in pages:
            omni.kit.window.preferences.select_page(page)
            await ui_test.human_delay(50)

    async def test_unsupported_widget_type(self):
        path = PERSISTENT_SETTINGS_PREFIX + "/test/test/test_unsupported"
        # Test unsupported types
        widget, model = create_setting_widget(path, 1)
        self.assertEqual((widget, model), (None, None))
