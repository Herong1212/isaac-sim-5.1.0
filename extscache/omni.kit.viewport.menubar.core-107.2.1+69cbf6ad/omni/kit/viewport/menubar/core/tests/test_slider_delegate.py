from pathlib import Path

from omni.kit.viewport.menubar.core import SliderMenuDelegate
import omni.ui as ui
from omni.ui.tests.test_base import OmniUiTest
from omni.kit.viewport.utility import get_active_viewport_and_window
from omni.kit.ui_test.query import MenuRef
import omni.kit.app

from .abstract_test_container import AbstractTestContainer

CURRENT_PATH = Path(__file__).parent
TEST_DATA_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.parent.joinpath("data").joinpath("tests")
TEST_WIDTH, TEST_HEIGHT = 600, 400


class SliderMenuDelegateContainer(AbstractTestContainer):
    def __init__(self):
        self.drag_min = -100
        self.drag_max = 1000
        self._drag_step = 10
        self.drag_item = None
        self.int_drag_item = None
        self.checkbox_item_model = None
        self.checkbox_item = None

        super().__init__()

    def _build_menu_items(self):
        ui.MenuItem(
            "General",
            delegate=SliderMenuDelegate(),
        )
        ui.MenuItem(
            "Int Slider",
            delegate=SliderMenuDelegate(slider_class=ui.IntSlider),
        )

        self.checkbox_item_model = ui.SimpleIntModel(0)
        self.checkbox_item = ui.MenuItem(
            "Show checkbox with value is min",
            delegate=SliderMenuDelegate(model=self.checkbox_item_model, show_checkbox_if_min=True, min=0, max=10),
        )

        ui.MenuItem(
            "Hide Checkbox",
            delegate=SliderMenuDelegate(model=ui.SimpleIntModel(3), show_checkbox_if_min=True, min=0, max=10),
        )

        self.drag_item = ui.MenuItem(
            "Drag",
            delegate=SliderMenuDelegate(min=self.drag_min, max=self.drag_max, step=self._drag_step),
        )

        self.int_drag_item = ui.MenuItem(
            "Int Drag",
            delegate=SliderMenuDelegate(min=self.drag_min, max=self.drag_max, step=self._drag_step, slider_class=ui.IntSlider),
        )


class TestSliderDelegate(OmniUiTest):
    async def setUp(self):
        self._golden_img_dir = TEST_DATA_PATH.absolute().joinpath("golden_img").absolute()

        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT, block_devices=False)

        _, viewport_window = get_active_viewport_and_window()
        await self.docked_test_window(viewport_window, width=TEST_WIDTH, height=TEST_HEIGHT, block_devices=False)

        self._menu = SliderMenuDelegateContainer()

        await omni.kit.app.get_app().next_update_async()

    # After running each test
    async def tearDown(self):
        self._menu.destroy()
        self._menu = None

        await super().tearDown()

    async def test_delegate(self):
        menu_ref = MenuRef(self._menu.root_menu, "")
        await menu_ref.click()

        for _ in range(4):
            await omni.kit.app.get_app().next_update_async()

        slider_delegate = self._menu.drag_item.delegate
        self.assertEqual(slider_delegate.min, self._menu.drag_min)
        self.assertEqual(slider_delegate.max, self._menu.drag_max)

        self._menu.checkbox_item_model.set_value(5)
        checkbox_delegate = self._menu.checkbox_item.delegate
        checkbox_delegate.min = 5
        checkbox_delegate.max = 50
        self.assertEqual(checkbox_delegate.min, 5)
        self.assertEqual(checkbox_delegate.max, 50)
        checkbox_delegate.set_range(-10, 10)
        self.assertEqual(checkbox_delegate.min, -10)
        self.assertEqual(checkbox_delegate.max, 10)
        self._menu.checkbox_item_model.set_value(-10)

        await self.finalize_test(
            golden_img_dir=self._golden_img_dir, golden_img_name="menubar_slider_delegate.png"
        )
