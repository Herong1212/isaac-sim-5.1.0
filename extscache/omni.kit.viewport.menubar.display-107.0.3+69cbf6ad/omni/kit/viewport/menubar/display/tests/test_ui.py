from pathlib import Path

import carb.input
import omni.kit.app
import omni.kit.test
import omni.kit.ui_test as ui_test
from omni.kit.ui_test import Vec2
from omni.kit.viewport.menubar.core import CategoryCollectionItem, CategoryStateItem, CategoryCustomItem, ViewportMenuDelegate, SelectableMenuItem
from omni.ui.tests.test_base import OmniUiTest
import omni.ui as ui
import omni.usd

CURRENT_PATH = Path(__file__).parent
TEST_DATA_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.parent.joinpath("data").joinpath("tests")
TEST_WIDTH, TEST_HEIGHT = 600, 400
TEST_SETTING_TRUE = "/exts/test/setting/true"
TEST_SETTING_FALSE = "/exts/test/setting/false"


class TestSettingMenuWindow(OmniUiTest):
    async def setUp(self):
        self._golden_img_dir = TEST_DATA_PATH.absolute().joinpath("golden_img").absolute()

        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT)

        await omni.kit.app.get_app().next_update_async()

    async def test_general(self):
        await self._show_display_menu("menubar_display.png", None)

    async def test_heads_up(self):
        settings = carb.settings.get_settings()
        prev_value = settings.get("/exts/omni.kit.viewport.window/hud/memoryTypes")
        try:
            await self._show_display_menu("menubar_display_headsup.png", 86)
            # Try custom memory types and ordering
            custom_types = ["host", "device"]
            self.assertTrue(prev_value != custom_types)
            settings.set("/exts/omni.kit.viewport.window/hud/memoryTypes", custom_types)
            await self.wait_n_updates()
            await self._show_display_menu("menubar_display_headsup_custom.png", 86)
        finally:
            settings.set("/exts/omni.kit.viewport.window/hud/memoryTypes", prev_value)

    async def test_show_by_type(self):
        await self._show_display_menu("menubar_display_show_type.png", 106)
        settings = carb.settings.get_settings()
        path_excludes = "/exts/omni.kit.viewport.menubar.display/showByType/exclude_list"
        default = settings.get(path_excludes)
        settings.set(path_excludes, [])
        try:
            await self._show_display_menu("menubar_display_show_type_with_skeletons.png", 106)
        finally:
            settings.set(path_excludes, default)

    async def test_show_by_purpose(self):
        await self._show_display_menu("menubar_display_show_purpose.png", 126)

    async def test_show_custom_menu_item(self):

        inst = omni.kit.viewport.menubar.display.get_instance()
        custom_collection_item = CategoryCollectionItem(
            "Custom catetory",
            [
                CategoryStateItem("Custom Item", ui.SimpleBoolModel(True)),
            ]
        )
        inst.register_custom_category_item("Show By Type", custom_collection_item)

        def _build_menu():
            with ui.Menu("Physics", delegate=ViewportMenuDelegate()):
                SelectableMenuItem("Joints", ui.SimpleBoolModel(True))
                with ui.Menu("Colliders", delegate=ViewportMenuDelegate()):
                    SelectableMenuItem("None", ui.SimpleBoolModel(True))
                    SelectableMenuItem("Selected", ui.SimpleBoolModel(False))
                    SelectableMenuItem("All", ui.SimpleBoolModel(False))
                    ui.Separator()
                    SelectableMenuItem("Normals", ui.SimpleBoolModel(False))

        physics_item = CategoryCustomItem("Physics", _build_menu)
        inst.register_custom_category_item("Show By Type", physics_item)

        settings = carb.settings.get_settings()
        settings.set(TEST_SETTING_FALSE, False)
        settings.set(TEST_SETTING_TRUE, True)
        inst.register_custom_setting("test new setting (True)", TEST_SETTING_TRUE)
        inst.register_custom_setting("test new setting (False)", TEST_SETTING_FALSE)
        await omni.kit.app.get_app().next_update_async()
        await self._show_display_menu("menubar_display_custom.png", 106)

        inst.deregister_custom_category_item("Show By Type", custom_collection_item)
        inst.deregister_custom_category_item("Show By Type", physics_item)
        inst.deregister_custom_setting("test new setting (True)")
        inst.deregister_custom_setting("test new setting (False)")
        await omni.kit.app.get_app().next_update_async()

    async def test_show_custom_category_and_section(self):
        inst = omni.kit.viewport.menubar.display.get_instance()

        category = "Draw Overlay"
        section = "Selection Display"

        did_shown_changed_callback = False

        def on_shown(s):
            nonlocal did_shown_changed_callback
            did_shown_changed_callback = True

        overlay_item = CategoryCollectionItem(
            category,
            [
                CategoryCustomItem("Points", lambda: SelectableMenuItem("Points", model=ui.SimpleBoolModel())),
                CategoryCustomItem("Normals", lambda: SelectableMenuItem("Normals", model=ui.SimpleBoolModel()))
            ],
            shown_changed_fn=on_shown
        )

        inst.register_custom_category_item(category, overlay_item, section)

        await omni.kit.app.get_app().next_update_async()
        await self._show_display_menu("menubar_display_custom_category_and_section.png", 166)

        self.assertTrue(did_shown_changed_callback)

        inst.deregister_custom_category_item(category, overlay_item)
        await omni.kit.app.get_app().next_update_async()

    async def _show_display_menu(self, golden_img_name: str, y: int = None) -> None:
        # Enable mouse input
        app_window = omni.appwindow.get_default_app_window()
        for device in [carb.input.DeviceType.MOUSE]:
            app_window.set_input_blocking_state(device, None)

        try:
            await ui_test.emulate_mouse_move(Vec2(20, 46), human_delay_speed=4)
            await ui_test.emulate_mouse_click()

            if y is not None:
                await ui_test.emulate_mouse_move(Vec2(20, y))

            await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name=golden_img_name)
        finally:
            for _ in range(3):
                await omni.kit.app.get_app().next_update_async()

            await ui_test.emulate_mouse_move(Vec2(300, 26))
            await ui_test.emulate_mouse_click()

            for _ in range(3):
                await omni.kit.app.get_app().next_update_async()
