import asyncio
from pathlib import Path

from carb.input import MouseEventType
import omni.kit.ui_test as ui_test
from omni.kit.ui_test.input import emulate_mouse
from omni.ui.tests.test_base import OmniUiTest
from omni.kit.widget.options_menu import OptionItem

from ..options_button import OptionsButton

CURRENT_PATH = Path(__file__).parent.absolute()
TEST_DATA_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.joinpath("data/tests")


class TestOptionsButton(OmniUiTest):
    # Before running each test
    async def setUp(self):
        self._items = [
            OptionItem("First Option"),
            OptionItem("Second Option"),
            OptionItem("Third Option"),
            OptionItem("More Options"),
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
            OptionsButton(self._items)

        await ui_test.human_delay()
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(20, 20))
        await ui_test.human_delay()
        await self.finalize_test("option_initial_ui.png")

    async def test_dirty(self):
        """Test options are dirty"""
        window = await self.create_test_window(block_devices=False)
        with window.frame:
            self._button = OptionsButton(self._items)

        try:
            await ui_test.human_delay()
            await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(20, 20))
            await ui_test.human_delay()
            await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(60, 72))
            await ui_test.human_delay()
            await self.finalize_test("option_dirty_ui.png")
        finally:
            self._button.model.reset()
