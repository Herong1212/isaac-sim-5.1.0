from pathlib import Path

import omni.ui as ui
from omni.ui.tests.test_base import OmniUiTest
from omni.kit.viewport.utility import get_active_viewport_and_window
from omni.kit.ui_test.query import WidgetRef, WindowStub
import omni.kit.app

from .example_button import ButtonExample


CURRENT_PATH = Path(__file__).parent
TEST_DATA_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.parent.joinpath("data").joinpath("tests")
TEST_WIDTH, TEST_HEIGHT = 600, 400


class TestButtonItem(OmniUiTest):
    async def setUp(self):
        self._golden_img_dir = TEST_DATA_PATH.absolute().joinpath("golden_img").absolute()

        await self.create_test_area(width=TEST_WIDTH, height=TEST_HEIGHT, block_devices=False)

        _, viewport_window = get_active_viewport_and_window()
        await self.docked_test_window(viewport_window, width=TEST_WIDTH, height=TEST_HEIGHT, block_devices=False)

        self._btn_menu_1 = ButtonExample(btn_id=1, name="General", text="General")
        self._btn_menu_2 = ButtonExample(btn_id=2, name="has_triangle", text="has_triangle", has_triangle=True)
        self._btn_menu_3 = ButtonExample(btn_id=3, name="invisible", text="invisible")
        self._btn_menu_4 = ButtonExample(btn_id=4, name="disabled", text="disabled")
        self._btn_menu_5 = ButtonExample(btn_id=5, name="selected", text="selected")

        def _build_window():
            window = ui.Window("Button Menu Window", width=200, height=200)
            with window.frame:
                ui.Label("This is a test")

            return window

        self._btn_menu_6 = ButtonExample(btn_id=8, name="window left", text="window left", build_window_fn=_build_window, alignment=ui.Alignment.LEFT_BOTTOM)
        self._btn_menu_7 = ButtonExample(btn_id=6, name="window", text="window", build_window_fn=_build_window)
        self._btn_menu_8 = ButtonExample(btn_id=7, name="left alignment", text="left alignment", alignment=ui.Alignment.LEFT_BOTTOM)

        for _ in range(4):
            await omni.kit.app.get_app().next_update_async()

    # After running each test
    async def tearDown(self):
        self._btn_menu_3.visible = True
        self._btn_menu_1.destroy()
        self._btn_menu_1 = None
        self._btn_menu_2.destroy()
        self._btn_menu_2 = None
        self._btn_menu_3.destroy()
        self._btn_menu_3 = None
        self._btn_menu_4.destroy()
        self._btn_menu_4 = None
        self._btn_menu_5.destroy()
        self._btn_menu_5 = None
        self._btn_menu_6.destroy()
        self._btn_menu_6 = None
        self._btn_menu_7.destroy()
        self._btn_menu_7 = None
        self._btn_menu_8.destroy()
        self._btn_menu_8 = None

        await super().tearDown()

    async def test_item(self):
        self.assertEqual(self._btn_menu_1.name, "General")
        self.assertFalse(self._btn_menu_2.checked)
        self._btn_menu_2.checked = True
        self.assertTrue(self._btn_menu_3.visible)
        self._btn_menu_3.visible = False
        self.assertTrue(self._btn_menu_4.enabled)
        self._btn_menu_4.enabled = False
        self.assertFalse(self._btn_menu_5.selected)
        self._btn_menu_5.selected = True

        for _ in range(4):
            await omni.kit.app.get_app().next_update_async()

        widget_ref = WidgetRef(self._btn_menu_8.button, "", window=WindowStub())
        self.assertFalse(self._btn_menu_8.clicked)
        await widget_ref.click()
        self.assertTrue(self._btn_menu_8.clicked)

        await widget_ref.click(right_click=True)
        self.assertIsNotNone(self._btn_menu_8.menu_item)
        await self.finalize_test(
            golden_img_dir=self._golden_img_dir, golden_img_name="menubar_button_item_left_alignment.png"
        )

        widget_ref = WidgetRef(self._btn_menu_7.button, "", window=WindowStub())
        await widget_ref.click(right_click=True)
        self.assertIsNotNone(self._btn_menu_7.window)
        await self.finalize_test(
            golden_img_dir=self._golden_img_dir, golden_img_name="menubar_button_item_window.png"
        )

        widget_ref = WidgetRef(self._btn_menu_6.button, "", window=WindowStub())
        await widget_ref.click(right_click=True)
        await self.finalize_test(
            golden_img_dir=self._golden_img_dir, golden_img_name="menubar_button_item_window_left_alignment.png"
        )
