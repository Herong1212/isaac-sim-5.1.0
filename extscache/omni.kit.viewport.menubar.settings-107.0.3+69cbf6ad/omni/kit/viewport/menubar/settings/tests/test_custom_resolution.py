from pathlib import Path

import carb.settings
import omni.kit.test
from omni.ui.tests.test_base import OmniUiTest
import omni.kit.ui_test as ui_test
from omni.kit.ui_test import Vec2, find
from ..menu_item.resolution_collection.model import ComboBoxResolutionModel, ResolutionComboBoxItem
from ..menu_item.custom_resolution.custom_resolution_delegate import CustomResolutionDelegate

CURRENT_PATH = Path(__file__).parent
TEST_DATA_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.parent.joinpath("data").joinpath("tests")
TEST_WIDTH, TEST_HEIGHT = 600, 600
SETTING_CUSTOM_RESOLUTION_LIST = "/persistent/app/renderer/resolution/custom/list"


class TestCustomResolution(OmniUiTest):
    async def setUp(self):
        self._golden_img_dir = TEST_DATA_PATH.absolute().joinpath("golden_img").absolute()
        self.__settings = carb.settings.get_settings()
        # Useles fake data that needs to go to ComboBoxResolutionModel
        resolution_settings = (("setting", (0, 0)), ("setting", (0, 0)))
        self.__model = ComboBoxResolutionModel(None, resolution_settings, self.__settings)

        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT, block_devices=False)
        await super().setUp()

    async def tearDown(self):
        self.__settings.set(SETTING_CUSTOM_RESOLUTION_LIST, [])
        await super().tearDown()

    async def test_custom_resolution_model(self):
        items = self.__model.get_item_children(None)
        num_items = len(items)

        self.__settings.set(SETTING_CUSTOM_RESOLUTION_LIST, [{"name": "test", "width": 100, "height": 200}])
        await self.wait_n_updates()

        items = self.__model.get_item_children(None)
        self.assertEqual(num_items + 2, len(items))
        new_item: ResolutionComboBoxItem = items[-1]
        self.assertEqual(new_item.name, "test")
        self.assertEqual(new_item.resolution, (100, 200))
        self.assertTrue(new_item.custom)

        self.__settings.set(SETTING_CUSTOM_RESOLUTION_LIST, [])
        await self.wait_n_updates()

        items = self.__model.get_item_children(None)
        self.assertEqual(num_items, len(items))

    async def test_custom_resolution_ui(self, human_delay_speed: float = 4):
        unlinked = False
        resolution = None
        try:
            from omni.kit.viewport.utility import get_active_viewport
            resolution = get_active_viewport().resolution

            await omni.usd.get_context().new_stage_async()
            await ui_test.emulate_mouse_move_and_click(Vec2(20, 46), human_delay_speed=human_delay_speed)
            await ui_test.emulate_mouse_move(Vec2(20, 166))

            # It is strange that could not emulate number input for width/height, use data model instead
            menu_ref = find("Viewport//Frame/**/SettingsRendererMenuItem[0]/MenuItem[0]")
            self.assertIsNotNone(menu_ref)
            delegate: CustomResolutionDelegate = menu_ref.widget.delegate

            # Change resolution width
            delegate.width_model.set_value(1200)
            await ui_test.emulate_mouse_move_and_click(Vec2(220, 190), human_delay_speed=human_delay_speed)
            await ui_test.emulate_keyboard_press(carb.input.KeyboardInput.ENTER, human_delay_speed=5)
            await self.capture_and_compare("menubar_setting_custom_resolutions_1200x675.png")

            # Unlink radio
            await ui_test.emulate_mouse_move_and_click(Vec2(265, 190), human_delay_speed=human_delay_speed)
            unlinked = True

            # Change resolution height
            delegate.height_model.set_value(800)
            await ui_test.emulate_mouse_move_and_click(Vec2(320, 190), human_delay_speed=human_delay_speed)
            await ui_test.emulate_keyboard_press(carb.input.KeyboardInput.ENTER)
            await self.capture_and_compare("menubar_setting_custom_resolutions_1200x800.png")

            # Save
            await ui_test.emulate_mouse_move_and_click(Vec2(460, 190))
            await ui_test.human_delay(human_delay_speed)
            await ui_test.emulate_char_press("Test")
            await self.wait_n_updates()
            await self.capture_and_compare("menubar_setting_custom_resolutions_save.png")

            await ui_test.emulate_mouse_move_and_click(Vec2(250, 340))
            await ui_test.human_delay(human_delay_speed)

            # Show resolution list
            await ui_test.emulate_mouse_move_and_click(Vec2(20, 46), human_delay_speed=human_delay_speed)
            await self.__show_resolution_list()
            await self.capture_and_compare("menubar_setting_custom_resolutions.png")

            # Delete custom resolution
            await ui_test.emulate_mouse_move_and_click(Vec2(582, 370), human_delay_speed=human_delay_speed)
            await self.__show_resolution_list()
            await self.capture_and_compare("menubar_setting_custom_resolutions_deleted.png")

        finally:
            # Hide menus
            await ui_test.emulate_mouse_move_and_click(Vec2(300, 26))

            # Revert link button
            if unlinked:
                await ui_test.emulate_mouse_move_and_click(Vec2(20, 46), human_delay_speed=human_delay_speed)
                await ui_test.emulate_mouse_move(Vec2(20, 166))
                await ui_test.human_delay(4)
                await ui_test.emulate_mouse_move_and_click(Vec2(265, 190), human_delay_speed=human_delay_speed)
                await ui_test.emulate_mouse_move_and_click(Vec2(300, 26))

            # Revert resolution
            get_active_viewport().resolution = resolution
            await self.wait_n_updates()
            await self.finalize_test_no_image()

    async def __show_resolution_list(self):
        await ui_test.emulate_mouse_move(Vec2(20, 166))
        await ui_test.emulate_mouse_move(Vec2(250, 166))
        await self.wait_n_updates()

    async def capture_and_compare(self, golden_img_name):
        await super().capture_and_compare(golden_img_dir=self._golden_img_dir, golden_img_name=golden_img_name)
        await self.wait_n_updates()
