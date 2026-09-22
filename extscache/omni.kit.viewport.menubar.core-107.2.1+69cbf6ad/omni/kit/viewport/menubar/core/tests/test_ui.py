from pathlib import Path

import carb.input
import omni.kit.app
import omni.kit.test
from omni.kit.viewport.utility import get_active_viewport_and_window
import omni.kit.ui_test as ui_test
from omni.kit.ui_test import Vec2
from omni.ui.tests.test_base import OmniUiTest
import omni.usd

from .left_example_menu_container import LeftExampleMenuContainer
from .right_example_menu_container import RightExampleMenuContainer
from .example_button import ButtonExample

CURRENT_PATH = Path(__file__).parent
TEST_DATA_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.parent.joinpath("data").joinpath("tests")
TEST_WIDTH, TEST_HEIGHT = 600, 400


class TestExampleMenuWindow(OmniUiTest):
    async def setUp(self):
        self._golden_img_dir = TEST_DATA_PATH.absolute().joinpath("golden_img").absolute()

        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT)

        _, viewport_window = get_active_viewport_and_window()
        await self.docked_test_window(viewport_window, width=TEST_WIDTH, height=TEST_HEIGHT, block_devices=False)

        self._left_menu = LeftExampleMenuContainer()
        self._right_menu = RightExampleMenuContainer()
        self._button_menu = ButtonExample()

        await omni.kit.app.get_app().next_update_async()

    # After running each test
    async def tearDown(self):
        self._left_menu.destroy()
        self._left_menu = None

        self._right_menu.destroy()
        self._right_menu = None

        self._button_menu.destroy()
        self._button_menu = None

        await super().tearDown()

    async def test_left(self):
        await self._show_popup_menu()

        self.assertEqual(self._left_menu.float_slider_delegate.min, 0.0)
        self.assertEqual(self._left_menu.float_slider_delegate.max, 1.0)

        golden_img_name = "menubar_example_left"
        try:
            import omni.kit.widget.spinner  # noqa: PLW0621, F401
        except ImportError:
            golden_img_name += "-no_spinner"
        await self.finalize_test(
            golden_img_dir=self._golden_img_dir, golden_img_name=f"{golden_img_name}.png"
        )

    async def test_right(self):
        await self._show_popup_menu(pos=Vec2(540, 20))
        await self.finalize_test(
            golden_img_dir=self._golden_img_dir, golden_img_name="menubar_example_right.png"
        )

    async def test_button(self):
        await self._show_popup_menu(pos=Vec2(60, 20), right_click=True)
        await self.finalize_test(
            golden_img_dir=self._golden_img_dir, golden_img_name="menubar_example_button.png"
        )

    async def _show_popup_menu(self, pos=Vec2(20, 20), right_click=False):  # noqa: B008
        # Enable mouse input
        app_window = omni.appwindow.get_default_app_window()
        for device in [carb.input.DeviceType.MOUSE]:
            app_window.set_input_blocking_state(device, None)

        await ui_test.emulate_mouse_move(pos)
        await ui_test.emulate_mouse_click(right_click=right_click)
        await omni.kit.app.get_app().next_update_async()
