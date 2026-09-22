import omni.ui as ui
from omni.kit import ui_test
from omni.kit.menu.utils import MenuHelperExtensionFull, MenuHelperWindow
from omni.ui.tests.test_base import OmniUiTest


class TestMenuHelperFull(OmniUiTest, MenuHelperExtensionFull):

    WINDOW_NAME = "My Full Window"
    MENU_GROUP = "Window"
    MENU_GROUP2 = "Window/Debug"

    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def test_menu_helper_full1(self):
        self.menu_startup(
            lambda: MenuHelperWindow(TestMenuHelperFull.WINDOW_NAME, width=300, height=300, verbose=True),
            TestMenuHelperFull.WINDOW_NAME,
            TestMenuHelperFull.WINDOW_NAME,
            TestMenuHelperFull.MENU_GROUP,
            verbose=True,
        )

        try:
            # verify window closed
            self.assertEqual(self._window, None)

            await ui_test.human_delay(10)
            await ui_test.menu_click(
                f"{TestMenuHelperFull.MENU_GROUP}/{TestMenuHelperFull.WINDOW_NAME}", human_delay_speed=4
            )
            await ui_test.human_delay(10)

            # verify window open
            self.assertEqual(self._window.visible, True)

            await ui_test.human_delay(10)
            await ui_test.menu_click(
                f"{TestMenuHelperFull.MENU_GROUP}/{TestMenuHelperFull.WINDOW_NAME}", human_delay_speed=4
            )
            await ui_test.human_delay(10)

            # verify window closed
            self.assertEqual(self._window, None)

            await ui_test.human_delay(10)
            await ui_test.menu_click(
                f"{TestMenuHelperFull.MENU_GROUP}/{TestMenuHelperFull.WINDOW_NAME}", human_delay_speed=4
            )
            await ui_test.human_delay(10)

            # verify window open
            self.assertEqual(self._window.visible, True)
        finally:
            self.menu_shutdown()

            # verify menus are removed
            import omni.kit.menu.utils

            self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

    async def test_menu_helper_full2(self):
        class MyWindow:
            def __init__(self):
                self._class_window = ui.Window(TestMenuHelperFull.WINDOW_NAME, width=300, height=300)

            def __del__(self):
                self._class_window.destroy()
                self._class_window = None

        self.menu_startup(
            lambda: MyWindow(),
            TestMenuHelperFull.WINDOW_NAME,
            TestMenuHelperFull.WINDOW_NAME,
            TestMenuHelperFull.MENU_GROUP,
            window_attr_name="_class_window",
            verbose=True,
        )

        try:
            # verify window closed
            self.assertEqual(self._window, None)

            await ui_test.human_delay(10)
            await ui_test.menu_click(
                f"{TestMenuHelperFull.MENU_GROUP}/{TestMenuHelperFull.WINDOW_NAME}", human_delay_speed=4
            )
            await ui_test.human_delay(10)

            # verify window open
            self.assertEqual(self._window.visible, True)

            await ui_test.human_delay(10)
            await ui_test.menu_click(
                f"{TestMenuHelperFull.MENU_GROUP}/{TestMenuHelperFull.WINDOW_NAME}", human_delay_speed=4
            )
            await ui_test.human_delay(10)

            # verify window closed
            self.assertEqual(self._window, None)

            await ui_test.human_delay(10)
            await ui_test.menu_click(
                f"{TestMenuHelperFull.MENU_GROUP}/{TestMenuHelperFull.WINDOW_NAME}", human_delay_speed=4
            )
            await ui_test.human_delay(10)

            # verify window open
            self.assertEqual(self._window.visible, True)
        finally:
            self.menu_shutdown()

            # verify menus are removed
            import omni.kit.menu.utils

            self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

    async def test_menu_helper_full3(self):
        for index in range(0, 10):
            self.menu_startup(
                lambda i=index: ui.Window(TestMenuHelperFull.WINDOW_NAME + str(i), width=300, height=150),
                TestMenuHelperFull.WINDOW_NAME + str(index),
                TestMenuHelperFull.WINDOW_NAME + str(index),
                TestMenuHelperFull.MENU_GROUP2,
                verbose=True,
            )

        try:
            # verify all windows are closed
            open_state = [self._window_list[index] is not None for index in range(0, 10)]
            self.assertEqual(open_state, [False] * 10)

            for index in range(0, 10):
                expected = [False] * 10
                expected[index] = True

                await ui_test.human_delay()
                await ui_test.menu_click(f"{TestMenuHelperFull.MENU_GROUP2}/{TestMenuHelperFull.WINDOW_NAME}{index}")
                await ui_test.human_delay()

                # verify only index window is open
                open_state = [self._window_list[index] is not None for index in range(0, 10)]
                self.assertEqual(open_state, expected)

                await ui_test.human_delay()
                await ui_test.menu_click(f"{TestMenuHelperFull.MENU_GROUP2}/{TestMenuHelperFull.WINDOW_NAME}{index}")
                await ui_test.human_delay()

                # verify window closed
                self.assertEqual(self._window_list[index], None)

                # verify all windows are closed
                open_state = [self._window_list[index] is not None for index in range(0, 10)]
                self.assertEqual(open_state, [False] * 10)

        finally:
            self.menu_shutdown()

            # verify menus are removed
            import omni.kit.menu.utils

            self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

    async def test_menu_helper_full4(self):
        for index in range(0, 10):
            self.menu_startup(
                lambda i=index: ui.Window(TestMenuHelperFull.WINDOW_NAME + str(i), width=300, height=150),
                TestMenuHelperFull.WINDOW_NAME + str(index),
                TestMenuHelperFull.WINDOW_NAME + str(index),
                TestMenuHelperFull.MENU_GROUP2,
                verbose=True,
            )

        try:
            # verify all windows are closed
            for index in range(0, 10):
                self.assertEqual(self._window_list[index], None)

            for index in range(0, 10):
                await ui_test.human_delay()
                await ui_test.menu_click(f"{TestMenuHelperFull.MENU_GROUP2}/{TestMenuHelperFull.WINDOW_NAME}{index}")
                await ui_test.human_delay()

                # verify index window open
                self.assertEqual(self._window_list[index].visible, True)

            for index in range(0, 10):
                await ui_test.human_delay()
                await ui_test.menu_click(f"{TestMenuHelperFull.MENU_GROUP2}/{TestMenuHelperFull.WINDOW_NAME}{index}")
                await ui_test.human_delay()

                # verify index window closed
                self.assertEqual(self._window_list[index], None)

        finally:
            for index in range(0, 10):
                self.menu_shutdown(index)

            # verify menus are removed
            import omni.kit.menu.utils

            self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

    async def test_menu_helper_full_duplicate_registration(self):
        # check for window names getting released in shutdown
        value = self.menu_startup(
            lambda: MenuHelperWindow(TestMenuHelperFull.WINDOW_NAME, width=300, height=300, verbose=True),
            TestMenuHelperFull.WINDOW_NAME,
            TestMenuHelperFull.WINDOW_NAME,
            TestMenuHelperFull.MENU_GROUP,
        )
        self.assertNotEqual(value, None)
        self.menu_shutdown()

        value = self.menu_startup(
            lambda: MenuHelperWindow(TestMenuHelperFull.WINDOW_NAME, width=300, height=300, verbose=True),
            TestMenuHelperFull.WINDOW_NAME,
            TestMenuHelperFull.WINDOW_NAME,
            TestMenuHelperFull.MENU_GROUP,
        )
        self.assertNotEqual(value, None)
        self.menu_shutdown()

        # check for window names registers twice
        helper = MenuHelperExtensionFull()
        value = helper.menu_startup(
            lambda: MenuHelperWindow(TestMenuHelperFull.WINDOW_NAME, width=300, height=300, verbose=True),
            TestMenuHelperFull.WINDOW_NAME,
            TestMenuHelperFull.WINDOW_NAME,
            TestMenuHelperFull.MENU_GROUP,
        )
        self.assertNotEqual(value, None)

        value = helper.menu_startup(
            lambda: MenuHelperWindow(TestMenuHelperFull.WINDOW_NAME, width=300, height=300, verbose=True),
            TestMenuHelperFull.WINDOW_NAME,
            TestMenuHelperFull.WINDOW_NAME,
            TestMenuHelperFull.MENU_GROUP,
        )
        self.assertEqual(value, None)

        helper.menu_shutdown()

    async def test_menu_helper_full_double_shutdown(self):
        helper = MenuHelperExtensionFull()
        helper.menu_startup(
            lambda: MenuHelperWindow(TestMenuHelperFull.WINDOW_NAME, width=300, height=300, verbose=True),
            TestMenuHelperFull.WINDOW_NAME,
            TestMenuHelperFull.WINDOW_NAME,
            TestMenuHelperFull.MENU_GROUP,
        )
        helper.menu_shutdown()
        helper.menu_shutdown()
