from pathlib import Path

import omni.kit.app
import omni.kit.test
from omni.kit.viewport.menubar.core import ViewportMenubar, ViewportMenuSpacer, get_instance as get_menubar_instance
from omni.kit.viewport.utility import get_active_viewport_and_window
import omni.ui as ui
from omni.ui.tests.test_base import OmniUiTest
import omni.usd

from .left_example_menu_container import LeftExampleMenuContainer
from .right_example_menu_container import RightExampleMenuContainer
from .example_button import ButtonExample

CURRENT_PATH = Path(__file__).parent
TEST_DATA_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.parent.joinpath("data").joinpath("tests")
TEST_WIDTH, TEST_HEIGHT = 600, 400


class ViewportBottomBar(ViewportMenubar):
    def __init__(self):
        super().__init__("BOTTOM_BAR")

    def build_fn(self, menu_items, factory):
        with ui.VStack():
            ui.Spacer()
            super().build_fn(menu_items, factory)


class TestMoreMenubars(OmniUiTest):
    async def setUp(self):
        self._golden_img_dir = TEST_DATA_PATH.absolute().joinpath("golden_img").absolute()

        _, viewport_window = get_active_viewport_and_window()
        await self.docked_test_window(viewport_window, width=TEST_WIDTH, height=TEST_HEIGHT)

        self._bottom_bar = None
        self._left_bar = None
        self._left_menu = None
        self._right_menu = None
        self._button_menu = None

    # After running each test
    async def tearDown(self):
        self._left_menu.destroy()
        self._left_menu = None

        self._right_menu.destroy()
        self._right_menu = None

        self._button_menu.destroy()
        self._button_menu = None

        if self._bottom_bar is not None:
            self._bottom_bar.destroy()
            self._bottom_bar = None

        if self._left_bar is not None:
            self._left_bar.destroy()
            self._left_bar = None

        await super().tearDown()

    async def test_bottom_bar(self):
        self._bottom_bar = ViewportBottomBar()
        with self._bottom_bar:
            self._left_menu = LeftExampleMenuContainer()
            self._right_menu = RightExampleMenuContainer()
            self._button_menu = ButtonExample()

        bottom_bar = get_menubar_instance().get_menubar("BOTTOM_BAR")
        with bottom_bar:
            ViewportMenuSpacer()

        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test(
            golden_img_dir=self._golden_img_dir, golden_img_name="viewport_bottombar.png"
        )

    async def test_left_bar(self):
        self._left_bar = ViewportMenubar(name="LEFT_BAR", direction=ui.Direction.TOP_TO_BOTTOM)
        with self._left_bar:
            self._left_menu = LeftExampleMenuContainer()
            self._right_menu = RightExampleMenuContainer()
            self._button_menu = ButtonExample()

        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test(
            golden_img_dir=self._golden_img_dir, golden_img_name="viewport_leftbar.png", threshold=.015
        )
