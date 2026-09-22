import copy
from pathlib import Path
from typing import Dict

from omni.kit.viewport.menubar.core import ViewportMenuContainer, IconMenuDelegate
import omni.ui as ui
from omni.ui.tests.test_base import OmniUiTest
from omni.kit.viewport.utility import get_active_viewport_and_window
from omni.kit.ui_test.query import MenuRef
import omni.kit.app
import carb.settings

from ..style import VIEWPORT_MENUBAR_STYLE
from .style import UI_STYLE

CURRENT_PATH = Path(__file__).parent
TEST_DATA_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.parent.joinpath("data").joinpath("tests")
TEST_WIDTH, TEST_HEIGHT = 600, 400


class IconMenuDelegateContainer(ViewportMenuContainer):
    def __init__(self):
        self._settings = carb.settings.get_settings()
        self._settings.set("/exts/omni.kit.viewport.menubar.delegate/visible", True)
        self._settings.set("/exts/omni.kit.viewport.menubar.delegate/order", -100)

        self.triggered = 0
        self.right_clicked = 0
        self.root_menu = None

        test_ui_style = copy.copy(VIEWPORT_MENUBAR_STYLE)
        test_ui_style.update(UI_STYLE)
        super().__init__(
            name="Icon",
            delegate=IconMenuDelegate("Sample", triggered_fn=self._on_trigger, right_clicked_fn=self._on_right_click),
            visible_setting_path="/exts/omni.kit.viewport.menubar.delegate/visible",
            order_setting_path="/exts/omni.kit.viewport.menubar.delegate/order",
            style=test_ui_style
        )

        self._settings = carb.settings.get_settings()

    def destroy(self):
        self._delegate.destroy()
        super().destroy()

    def _on_trigger(self) -> None:
        self.triggered += 1

    def _on_right_click(self) -> None:
        self.right_clicked += 1

    def build_fn(self, factory: Dict):
        self.root_menu = ui.Menu(
            self.name, delegate=self._delegate, on_build_fn=self._build_menu_items, style=self._style
        )

    def _build_menu_items(self):
        ui.MenuItem(
            "Icon",
            delegate=IconMenuDelegate("Sample", text=True, build_custom_widgets=self._build_custom_widgets, has_triangle=False),
        )

    def _build_custom_widgets(self, item: ui.MenuItem):
        ui.Label("custom widget")


class TestIconDelegate(OmniUiTest):
    async def setUp(self):
        self._golden_img_dir = TEST_DATA_PATH.absolute().joinpath("golden_img").absolute()

        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT, block_devices=False)

        _, viewport_window = get_active_viewport_and_window()
        await self.docked_test_window(viewport_window, width=TEST_WIDTH, height=TEST_HEIGHT, block_devices=False)

        self._menu = IconMenuDelegateContainer()

        await omni.kit.app.get_app().next_update_async()

    # After running each test
    async def tearDown(self):
        self._menu.destroy()
        self._menu = None

        await super().tearDown()

    async def test_delegate(self):
        root_delegate = self._menu.root_menu.delegate
        self.assertFalse(root_delegate.text_visible)
        self.assertFalse(root_delegate.checked)
        self.assertTrue(root_delegate.enabled)
        self.assertEqual(root_delegate.text, "")

        menu_ref = MenuRef(self._menu.root_menu, "")
        await menu_ref.click()

        await self.finalize_test(
            golden_img_dir=self._golden_img_dir, golden_img_name="menubar_icon_delegate.png"
        )

        self.assertEqual(self._menu.triggered, 1)
        self.assertEqual(self._menu.right_clicked, 0)

        await menu_ref.click(right_click=True)
        self.assertEqual(self._menu.triggered, 1)
        self.assertEqual(self._menu.right_clicked, 1)

        root_delegate.text = "Test"
        root_delegate.text_visible = True
        root_delegate.checked = True
        root_delegate.enabled = False

        await self.finalize_test_no_image()
