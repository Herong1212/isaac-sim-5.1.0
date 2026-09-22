import copy
from pathlib import Path
from typing import Dict

import carb.settings
import omni.kit.app
from omni.kit.viewport.menubar.core import ViewportMenuContainer, AbstractWidgetMenuDelegate, IconMenuDelegate
import omni.ui as ui
from omni.kit.ui_test.query import MenuRef
from omni.kit.viewport.utility import get_active_viewport_and_window
from omni.ui.tests.test_base import OmniUiTest

from .style import UI_STYLE

from ..style import VIEWPORT_MENUBAR_STYLE
from ..model.reset_button import ResetHelper

CURRENT_PATH = Path(__file__).parent
TEST_DATA_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.parent.joinpath("data").joinpath("tests")
TEST_WIDTH, TEST_HEIGHT = 600, 400


class SimpleTextDelegate(AbstractWidgetMenuDelegate):
    def build_widget(self, item: ui.MenuHelper):
        ui.Label(item.text)


class SimpleResetHelper(ResetHelper):
    def __init__(self, value: bool) -> None:
        self._value = value
        super().__init__()

    def get_default(self):
        return True

    def restore_default(self):
        self._value = self.get_default()

    def get_value(self):
        return self._value


class AbstractMenuDelegateContainer(ViewportMenuContainer):
    def __init__(self):
        self._settings = carb.settings.get_settings()
        self._settings.set("/exts/omni.kit.viewport.menubar.delegate/visible", True)
        self._settings.set("/exts/omni.kit.viewport.menubar.delegate/order", -100)

        self.invisible_menuitem = None
        self.disabled_menuitem = None
        self.root_menu = None

        test_ui_style = copy.copy(VIEWPORT_MENUBAR_STYLE)
        test_ui_style.update(UI_STYLE)
        super().__init__(
            name="",
            delegate=IconMenuDelegate("Sample"),
            visible_setting_path="/exts/omni.kit.viewport.menubar.delegate/visible",
            order_setting_path="/exts/omni.kit.viewport.menubar.delegate/order",
            style=test_ui_style
        )

        self._settings = carb.settings.get_settings()

    def build_fn(self, factory: Dict):
        self.root_menu = ui.Menu(
            self.name, delegate=self._delegate, on_build_fn=self._build_menu_items, style=self._style
        )

    def _build_menu_items(self):
        ui.MenuItem(
            "General",
            delegate=SimpleTextDelegate(),
        )
        ui.MenuItem(
            "Reserve Status",
            delegate=SimpleTextDelegate(reserve_status=True),
        )
        ui.MenuItem(
            "Reset Button (True)",
            delegate=SimpleTextDelegate(model=SimpleResetHelper(True), has_reset=True),
        )
        ui.MenuItem(
            "Reset Button (False)",
            delegate=SimpleTextDelegate(model=SimpleResetHelper(False), has_reset=True),
        )
        ui.Menu(
            "Menu",
            delegate=SimpleTextDelegate(),
        )
        self.invisible_menuitem = ui.MenuItem(
            "Invisible",
            delegate=SimpleTextDelegate(visible=False),
        )

        self.disabled_menuitem = ui.MenuItem(
            "Disabled",
            delegate=SimpleTextDelegate(enabled=False),
        )


class TestAbstractDelegate(OmniUiTest):
    async def setUp(self):
        self._golden_img_dir = TEST_DATA_PATH.absolute().joinpath("golden_img").absolute()

        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT, block_devices=False)

        _, viewport_window = get_active_viewport_and_window()
        await self.docked_test_window(viewport_window, width=TEST_WIDTH, height=TEST_HEIGHT, block_devices=False)

        self._menu = AbstractMenuDelegateContainer()

        await omni.kit.app.get_app().next_update_async()

    # After running each test
    async def tearDown(self):
        self._menu.destroy()
        self._menu = None

        await super().tearDown()

    async def test_delegate(self):
        menu_ref = MenuRef(self._menu.root_menu, "")
        await menu_ref.click()
        self.assertFalse(self._menu.invisible_menuitem.delegate.visible)
        self.assertFalse(self._menu.disabled_menuitem.delegate.enabled)
        await self.finalize_test(
            golden_img_dir=self._golden_img_dir, golden_img_name="menubar_abstract_delegate.png"
        )
