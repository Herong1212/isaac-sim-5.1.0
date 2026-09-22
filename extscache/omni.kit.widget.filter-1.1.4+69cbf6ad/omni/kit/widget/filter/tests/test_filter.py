import asyncio
from pathlib import Path

from carb.input import MouseEventType
import omni.kit.ui_test as ui_test
from omni.kit.ui_test.input import emulate_mouse, emulate_mouse_click
from omni.ui.tests.test_base import OmniUiTest
from omni.kit.widget.options_menu import OptionItem

from ..filter import FilterButton, FilterModel

CURRENT_PATH = Path(__file__).parent.absolute()
TEST_DATA_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.joinpath("data/tests")


class TestFilter(OmniUiTest):
    # Before running each test
    async def setUp(self):
        self._items = [
            OptionItem("audio", text="Audio"),
            OptionItem("materials", text="Materials"),
            OptionItem("scripts", text="Scripts"),
            OptionItem("textures", text="Textures"),
            OptionItem("usd", text="USD"),
        ]

        self._golden_img_dir = TEST_DATA_PATH.absolute().joinpath("golden")

        await super().setUp()

    # After running each test
    async def tearDown(self):
        await super().tearDown()

    async def finalize_test(self, golden_img_name: str):
        await self.wait_n_updates()
        await super().finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name=golden_img_name)
        await self.wait_n_updates()

    async def test_ui(self):
        """Test initial UI"""
        window = await self.create_test_window(block_devices=False)
        with window.frame:
            FilterButton(self._items)

        await ui_test.human_delay()
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(20, 20), right_click=False)
        await asyncio.sleep(0.5)
        await ui_test.human_delay()
        await self.finalize_test("filter_initial_ui.png")

    async def test_dirty_toggle(self):
        """Test filter settings are dirty"""
        window = await self.create_test_window(block_devices=False)
        with window.frame:
            self._button = FilterButton(self._items)

        try:
            # click on first item
            await ui_test.human_delay()
            await self.__show_menu(right_click=True)
            await ui_test.human_delay()
            await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(60, 72))
            await ui_test.human_delay()
            await self.finalize_test("filter_dirty_ui.png")

            # hide menu
            await self.__hide_menu()

            # Double click to toggle
            await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(20, 20), double=True)
            await ui_test.human_delay()
            items = self._button.model.get_item_children()
            for item in items:
                self.assertFalse(item.value)

            # Middle click to toggle again
            await ui_test.emulate_mouse_move(ui_test.Vec2(20, 20))
            await emulate_mouse(MouseEventType.MIDDLE_BUTTON_DOWN)
            await ui_test.human_delay()
            await emulate_mouse(MouseEventType.MIDDLE_BUTTON_UP)
            await ui_test.human_delay()
            items = self._button.model.get_item_children()
            for index, item in enumerate(items):
                if index == 0:
                    self.assertTrue(item.value)
                else:
                    self.assertFalse(item.value)

        finally:
            await self.__hide_menu()
            self._button.model.reset()

    async def __show_menu(self, right_click: bool=False):
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(20, 20), right_click=right_click)
        await asyncio.sleep(0.1)

    async def __hide_menu(self):
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(0, 0))
        await ui_test.human_delay()
        await asyncio.sleep(1)
