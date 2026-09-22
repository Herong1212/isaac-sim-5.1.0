import asyncio
from pathlib import Path
from typing import List

import omni.kit.app
import omni.kit.ui_test as ui_test
from omni.kit.browser.core import (
    AbstractBrowserModel,
    CategoryItem,
    CollectionItem,
    DetailItem,
    TreeBrowserWidget,
    TreeCategoryDelegate,
)
from omni.ui.tests.test_base import OmniUiTest

from .common import TreeBrowserModel

CURRENT_PATH = Path(__file__).parent
TEST_DATA_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.joinpath("data").joinpath("tests")


class TestTreeCategoryDelegate(TreeCategoryDelegate):
    def _on_item_right_click(self, item: CategoryItem):
        self._right_click_item = item


class TestTreeBrowserWidget(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()

        self._golden_img_dir = TEST_DATA_PATH.absolute().joinpath("golden_img").absolute()
        self._browser_model = TreeBrowserModel(show_all=True)
        self._window = await self.create_test_window(width=500, height=600, block_devices=False)
        self._delegate = TestTreeCategoryDelegate(hide_zero_count=True)
        with self._window.frame:
            self._browser_widget = TreeBrowserWidget(self._browser_model, category_delegate=self._delegate)

        self._browser_widget.collection_index = 0
        await omni.kit.app.get_app().next_update_async()

    # After running each test
    async def tearDown(self):
        self._window = None
        await super().tearDown()

    async def test_general(self):
        """Testing general look of TreeBrowserWidget"""

        # Wait for icon loaded
        await asyncio.sleep(5)

        # Expand first item
        collections = self._browser_model.get_item_children(None)
        category = self._browser_model.get_item_children(collections[0])[1]
        self._browser_widget._category_view.set_expanded(category, True, True)
        self._browser_model._item_changed(category)
        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="tree_general.png")

    async def test_item_loading(self):
        collections = self._browser_model.get_item_children(None)
        category = self._browser_model.get_item_children(collections[0])[1]

        try:
            category.loading = True
            #self._browser_widget._category_view.set_expanded(category, True, True)
            self._browser_model._item_changed(category)
            await omni.kit.app.get_app().next_update_async()

            await self.capture_and_compare(golden_img_dir=self._golden_img_dir, golden_img_name="tree_loading.png")

            category.loading = False
            self._browser_model._item_changed(category)
            await omni.kit.app.get_app().next_update_async()
            await self.capture_and_compare(golden_img_dir=self._golden_img_dir, golden_img_name="tree_loading_done.png")
        finally:
            await self.finalize_test_no_image()

    async def test_right_click(self):
        collections = self._browser_model.get_item_children(None)
        category = self._browser_model.get_item_children(collections[0])[1]
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(52, 43), right_click=True)
        self.assertEqual(self._delegate._right_click_item, category)
        await self.finalize_test_no_image()
