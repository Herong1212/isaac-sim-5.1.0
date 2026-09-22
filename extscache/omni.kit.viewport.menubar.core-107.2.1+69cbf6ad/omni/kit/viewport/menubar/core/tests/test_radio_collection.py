from pathlib import Path

from omni.kit.viewport.menubar.core import RadioMenuCollection, ComboBoxModel
from omni.ui.tests.test_base import OmniUiTest
from omni.kit.viewport.utility import get_active_viewport_and_window
from omni.kit.ui_test.query import MenuRef
import omni.kit.app

from .abstract_test_container import AbstractTestContainer

CURRENT_PATH = Path(__file__).parent
TEST_DATA_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.parent.joinpath("data").joinpath("tests")
TEST_WIDTH, TEST_HEIGHT = 600, 400


class RadioContainer(AbstractTestContainer):
    def __init__(self):
        self.radio_menu = None
        super().__init__()

    def _build_menu_items(self):
        self.radio_menu = RadioMenuCollection(
            "Radio Collection",
            ComboBoxModel(["First", "Second", "Third"], current_value="Second"),
        )

    def destroy(self):
        if self.radio_menu:
            self.radio_menu.destroy()
        super().destroy()


class TestRadioContainer(OmniUiTest):
    async def setUp(self):
        self._golden_img_dir = TEST_DATA_PATH.absolute().joinpath("golden_img").absolute()

        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT, block_devices=False)

        _, viewport_window = get_active_viewport_and_window()
        await self.docked_test_window(viewport_window, width=TEST_WIDTH, height=TEST_HEIGHT, block_devices=False)

        self._menu = RadioContainer()

        await omni.kit.app.get_app().next_update_async()

    # After running each test
    async def tearDown(self):
        self._menu.destroy()
        self._menu = None

        await super().tearDown()

    async def test_delegate(self):
        menu_ref = MenuRef(self._menu.root_menu, "")
        await menu_ref.click()

        menu_ref = MenuRef(self._menu.radio_menu, "")
        await menu_ref.click()

        for _ in range(4):
            await omni.kit.app.get_app().next_update_async()

        await self.finalize_test(
            golden_img_dir=self._golden_img_dir, golden_img_name="menubar_radio_collection.png"
        )

        self.assertEqual(self._menu.radio_menu._model.current_index.as_int, 1)  # noqa: PLW0212
        first_ref = menu_ref.find_menu("First")
        await first_ref.click()
        self.assertEqual(self._menu.radio_menu._model.current_index.as_int, 0)  # noqa: PLW0212

        await self.finalize_test_no_image()
