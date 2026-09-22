import asyncio
from pathlib import Path
from typing import List, Tuple

import carb.input
import omni.kit.app
import omni.kit.ui_test as ui_test
from omni.kit.browser.core import DetailDelegate, DetailItem
from omni.kit.browser.core.models import DetailItem
from omni.ui.tests.test_base import OmniUiTest

from ..models import SingleLevelWrapper
from ..widgets.style import UI_STYLES
from ..widgets.thumbnail_view import ThumbnailView
from .common import SimpleBrowserModel

CURRENT_PATH = Path(__file__).parent
TEST_DATA_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.joinpath("data").joinpath("tests")


class TestDelegate(DetailDelegate):
    def on_drag(self, item: DetailItem) -> str:
        return item.name


class TestThumbnailView(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()

        self._golden_img_dir = TEST_DATA_PATH.absolute().joinpath("golden_img").absolute()
        self._browser_model = SimpleBrowserModel()
        self._detail_model = SingleLevelWrapper()
        colleciton_items = self._browser_model.get_item_children(None)
        category_items = self._browser_model.get_item_children(colleciton_items[0])
        self._detail_model.set_sources(self._browser_model, category_items[0])

        self._window = await self.create_test_window(width=500, height=600, block_devices=False)
        self._window.frame.set_style(UI_STYLES)
        self._delegate = TestDelegate(model=self._browser_model)
        with self._window.frame:
            self._view = ThumbnailView(self._detail_model, delegate=self._delegate)

        for _ in range(20):
            await omni.kit.app.get_app().next_update_async()

    # After running each test
    async def tearDown(self):
        self._view.destroy()
        await super().tearDown()

    async def test_general(self):
        """Testing general look of ThumbnailView"""
        # Wait for icons loaded
        await asyncio.sleep(5)

        self.assertEqual(self._view.model, self._detail_model)
        self.assertEqual(self._view.selection, [])

        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="thumbnailview_general.png")

    async def test_padding(self):
        self.assertEqual(self._view.thumbnail_padding_width, 1)
        self.assertEqual(self._view.thumbnail_padding_height, 1)

        self._view.thumbnail_padding_width = 10
        self._view.thumbnail_padding_height = 20

        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()
        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="thumbnailview_padding.png")

    async def test_selection(self):
        detail_items = self._detail_model.get_item_children()
        pos = self.__get_item_position(detail_items[0])
        await ui_test.emulate_mouse_move_and_click(pos)
        self.assertEqual(self._view.selection, [detail_items[0]])

        # CTRL + CLICK to additional selection
        await ui_test.input.emulate_keyboard(carb.input.KeyboardEventType.KEY_PRESS, carb.input.KeyboardInput.LEFT_CONTROL, carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL)
        await omni.kit.app.get_app().next_update_async()
        pos = self.__get_item_position(detail_items[3])
        await ui_test.emulate_mouse_move_and_click(pos)
        self.assertEqual(self._view.selection, [detail_items[0], detail_items[3]])

        # CTRL + CLICK again to remove additional selection
        await ui_test.emulate_mouse_move_and_click(pos)
        self.assertEqual(self._view.selection, [detail_items[0]])
        await ui_test.input.emulate_keyboard(carb.input.KeyboardEventType.KEY_RELEASE, carb.input.KeyboardInput.LEFT_CONTROL, carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL)

        # SHIFT + CLICK to multi selection
        await ui_test.input.emulate_keyboard(carb.input.KeyboardEventType.KEY_PRESS, carb.input.KeyboardInput.LEFT_SHIFT, carb.input.KEYBOARD_MODIFIER_FLAG_SHIFT)
        await omni.kit.app.get_app().next_update_async()
        pos = self.__get_item_position(detail_items[4])
        await ui_test.emulate_mouse_move_and_click(pos)
        self.assertEqual(self._view.selection, [detail_items[4], detail_items[3], detail_items[2], detail_items[1], detail_items[0]])
        await ui_test.input.emulate_keyboard(carb.input.KeyboardEventType.KEY_RELEASE, carb.input.KeyboardInput.LEFT_SHIFT, carb.input.KEYBOARD_MODIFIER_FLAG_SHIFT)

        # Right click on another item to change selection
        pos = self.__get_item_position(detail_items[5])
        await ui_test.emulate_mouse_move_and_click(pos, right_click=True)
        self.assertEqual(self._view.selection, [detail_items[5]])

        # Clear selection
        self._view.selection = []
        self.assertEqual(self._view.selection, [])

        await self.finalize_test_no_image()

    async def test_on_drag(self):

        def __on_selection_changed(selections: List[DetailItem]):
            self.__selections = selections


        self._view.set_selection_changed_fn(__on_selection_changed)
        detail_items = self._detail_model.get_item_children()

        self._view.selection = [detail_items[0], detail_items[3]]
        self.assertEqual(self.__selections, self._view.selection)

        # Drag item in selection
        drag_url = self._view.on_drag(detail_items[0])
        self.assertEqual(drag_url, "\n".join([item.name for item in self._view.selection]))

        # Drag item out of selection
        drag_url = self._view.on_drag(detail_items[1])
        self.assertEqual(drag_url, detail_items[1].name)

        self._view.set_selection_changed_fn(None)

        await self.finalize_test_no_image()

    async def test_item_execute(self):
        detail_items = self._detail_model.get_item_children()
        double_click_item = detail_items[2]
        pos = self.__get_item_position(double_click_item)
        await ui_test.emulate_mouse_move_and_click(pos, double=True)
        self.assertEqual(self._browser_model.execute_item, double_click_item)
        await self.finalize_test_no_image()

    async def test_item_changed(self):
        detail_items = self._detail_model.get_item_children()
        item = detail_items[2]
        item.name_model.set_value("NEW TEXT")
        self._delegate.item_changed(self._browser_model, item)
        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()
        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="thumbnailview_item_changed.png")

    def __get_item_position(self, item: DetailItem) -> ui_test.Vec2:
        frame = self._view._delegates[item]
        return ui_test.Vec2(frame.screen_position_x + frame.computed_content_width / 2, frame.screen_position_y + frame.computed_content_height / 2)