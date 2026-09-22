import omni.ui as ui
from omni.kit import ui_test
from omni.kit.menu.utils import MenuHelperExtension
from omni.ui.tests.test_base import OmniUiTest


class TestMenuHelper(OmniUiTest, MenuHelperExtension):

    WINDOW_NAME = "My Window"
    MENU_GROUP = "Window"

    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def test_menu_helper(self):
        def visiblity_changed_fn(visible):
            self.menu_refresh()

        def show_window(visible: bool):
            if visible:
                self._window = ui.Window(TestMenuHelper.WINDOW_NAME, width=300, height=300)
                self._window.set_visibility_changed_fn(visiblity_changed_fn)
            elif self._window:
                self._window.visible = False

        try:
            self._window = None
            ui.Workspace.set_show_window_fn(TestMenuHelper.WINDOW_NAME, show_window)
            self.menu_startup(
                TestMenuHelper.WINDOW_NAME, TestMenuHelper.WINDOW_NAME, TestMenuHelper.MENU_GROUP, verbose=True
            )

            # verify window closed
            self.assertEqual(self._window, None)

            await ui_test.human_delay(10)
            await ui_test.menu_click(f"{TestMenuHelper.MENU_GROUP}/{TestMenuHelper.WINDOW_NAME}", human_delay_speed=4)
            await ui_test.human_delay(10)

            # verify window open
            self.assertEqual(self._window.visible, True)

            await ui_test.human_delay(10)
            await ui_test.menu_click(f"{TestMenuHelper.MENU_GROUP}/{TestMenuHelper.WINDOW_NAME}", human_delay_speed=4)
            await ui_test.human_delay(10)

            # verify window closed
            self.assertEqual(self._window.visible, False)

            await ui_test.human_delay(10)
            await ui_test.menu_click(f"{TestMenuHelper.MENU_GROUP}/{TestMenuHelper.WINDOW_NAME}", human_delay_speed=4)
            await ui_test.human_delay(10)

            # verify window open
            self.assertEqual(self._window.visible, True)
        finally:
            self.menu_shutdown()
            ui.Workspace.set_show_window_fn(TestMenuHelper.WINDOW_NAME, None)
            if self._window:
                self._window.destroy()
                self._window = None

            await ui_test.human_delay(10)

            # verify menus are removed
            import omni.kit.menu.utils

            self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

    async def test_menu_helper_double_add(self):
        try:
            self.assertEqual(
                self.menu_startup(TestMenuHelper.WINDOW_NAME, TestMenuHelper.WINDOW_NAME, TestMenuHelper.MENU_GROUP),
                True,
            )
            self.assertEqual(
                self.menu_startup(TestMenuHelper.WINDOW_NAME, TestMenuHelper.WINDOW_NAME, TestMenuHelper.MENU_GROUP),
                False,
            )
        finally:
            self.menu_shutdown()

    async def test_menu_helper_duplicate_registration(self):
        # check for window names getting released in shutdown
        ok = self.menu_startup(TestMenuHelper.WINDOW_NAME, TestMenuHelper.WINDOW_NAME, TestMenuHelper.MENU_GROUP)
        self.assertTrue(ok)
        self.menu_shutdown()

        ok = self.menu_startup(TestMenuHelper.WINDOW_NAME, TestMenuHelper.WINDOW_NAME, TestMenuHelper.MENU_GROUP)
        self.assertTrue(ok)
        self.menu_shutdown()

        # check for window names registers twice
        helper = MenuHelperExtension()
        ok = helper.menu_startup(TestMenuHelper.WINDOW_NAME, TestMenuHelper.WINDOW_NAME, TestMenuHelper.MENU_GROUP)
        self.assertTrue(ok)
        ok = helper.menu_startup(TestMenuHelper.WINDOW_NAME, TestMenuHelper.WINDOW_NAME, TestMenuHelper.MENU_GROUP)
        self.assertFalse(ok)
        helper.menu_shutdown()

    async def test_menu_helper_double_shutdown(self):
        helper = MenuHelperExtension()
        helper.menu_startup(TestMenuHelper.WINDOW_NAME, TestMenuHelper.WINDOW_NAME, TestMenuHelper.MENU_GROUP)
        helper.menu_shutdown()
        helper.menu_shutdown()
