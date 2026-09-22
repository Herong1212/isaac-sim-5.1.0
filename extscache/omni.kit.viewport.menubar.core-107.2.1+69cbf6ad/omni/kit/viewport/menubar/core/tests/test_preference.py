from pathlib import Path

import omni.kit.test
from omni.ui.tests.test_base import OmniUiTest
import omni.kit.app
import omni.kit.window.preferences
from omni.kit.viewport.window import ViewportWindow
import omni.ui as ui

from omni.kit.viewport.menubar.core import get_instance, ViewportMenuSpacer
from .left_example_menu_container import LeftExampleMenuContainer
from .right_example_menu_container import RightExampleMenuContainer
from .example_button import ButtonExample


CURRENT_PATH = Path(__file__).parent
TEST_DATA_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.parent.joinpath("data").joinpath("tests")
TEST_WIDTH, TEST_HEIGHT = 1280, 600


class TestPreference(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()

        self._golden_img_dir = TEST_DATA_PATH.absolute().joinpath("golden_img").absolute()

        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT, block_devices=False)
        self._vw = ViewportWindow('TestWindow', width=TEST_WIDTH, height=TEST_HEIGHT)

        self._left_menu = LeftExampleMenuContainer()
        self._right_menu = RightExampleMenuContainer()
        self._button_menu = ButtonExample()

    # After running each test
    async def tearDown(self):
        self._left_menu.destroy()
        self._left_menu = None

        self._right_menu.destroy()
        self._right_menu = None

        self._button_menu.destroy()
        self._button_menu = None

        self._vw.destroy()
        self._vw = None

        await super().tearDown()

    async def test_viewport_preference(self):
        await self._test_preference_page("Viewport")

    async def _test_preference_page(self, title: str):
        for page in omni.kit.window.preferences.get_page_list():
            if page.get_title() == title:
                omni.kit.window.preferences.select_page(page)
        omni.kit.window.preferences.rebuild_pages()
        omni.kit.window.preferences.show_preferences_window()
        await omni.kit.app.get_app().next_update_async()

        w = ui.Workspace.get_window("Preferences")

        await self.docked_test_window(
            window=w,
            width=1280,
            height=600,
        )

        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name=f"{title}.png")

    async def test_preference_model(self):
        inst = get_instance()
        page = inst._page # noqa PLW0212
        model = page._model # noqa PLW0212

        items = model.get_item_children(None)
        self.assertEqual(len(items), 4)
        self.assertEqual(items[0].name, self._left_menu.name)
        self.assertEqual(items[1].name, self._button_menu.name)
        self.assertTrue(isinstance(items[2], ViewportMenuSpacer))
        self.assertEqual(items[3].name, self._right_menu.name)

        left_item = items[0]
        button_item = items[1]

        self.assertEqual(model.get_drag_mime_data(left_item), self._left_menu.name)

        drop_accepted = model.drop_accepted(button_item, left_item)
        self.assertTrue(drop_accepted)

        drop_accepted = model.drop_accepted(None, left_item)
        self.assertFalse(drop_accepted)

        # Drop left to behind button
        model.drop(button_item, left_item)
        items = model.get_item_children(None)
        self.assertEqual(items[0], button_item)
        self.assertEqual(items[1], left_item)

        # Drop left to in front of button
        model.drop(left_item, button_item)
        items = model.get_item_children(None)
        self.assertEqual(items[0], left_item)
        self.assertEqual(items[1], button_item)

        await self.finalize_test_no_image()
