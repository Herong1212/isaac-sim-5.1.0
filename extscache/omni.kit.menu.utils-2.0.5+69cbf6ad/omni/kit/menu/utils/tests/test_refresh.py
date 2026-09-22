import omni.kit.test
import omni.ui as ui
from omni.kit import ui_test
from omni.kit.menu.utils import MenuItemDescription
from omni.ui.tests.test_base import OmniUiTest

from .utils import verify_menu_items


class TestRefresh(OmniUiTest):
    async def setUp(self):
        omni.kit.menu.utils.get_debug_stats()["refreshed_menu_items"] = {}
        self.assertEqual(omni.kit.menu.utils.get_debug_stats()["refreshed_menu_items"], {})

    async def tearDown(self):
        omni.kit.menu.utils.get_debug_stats()["refreshed_menu_items"] = {}

    async def test_refresh_windows(self):
        sub_menu = [
            MenuItemDescription(name="Sub Test 1"),
            MenuItemDescription(name="Sub Test 2"),
            MenuItemDescription(name="Sub Test 3"),
            MenuItemDescription(name="Sub Test 4"),
        ]
        menu_list = [
            MenuItemDescription(name="Test 1", sub_menu=sub_menu),
            MenuItemDescription(name="Test 2"),
            MenuItemDescription(name="Test 3"),
            MenuItemDescription(name="Test 4"),
        ]

        omni.kit.menu.utils.add_menu_items(menu_list, "Window", 99)
        omni.kit.menu.utils.rebuild_menus()
        await ui_test.human_delay(50)

        await ui_test.menu_click("Window", show=True)
        await ui_test.human_delay(10)
        await ui_test.menu_click("Window", show=False)
        await ui_test.human_delay(10)

        try:
            # dict should be empty as nothing has refreshed yet
            self.assertEqual(omni.kit.menu.utils.get_debug_stats()["refreshed_menu_items"], {})

            # refresh
            omni.kit.menu.utils.refresh_menu_items("Window")

            await ui_test.menu_click("Window", show=True)
            await ui_test.human_delay(10)
            await ui_test.menu_click("Window", show=False)
            await ui_test.human_delay(10)
            # all items should be 1
            self.assertEqual(
                omni.kit.menu.utils.get_debug_stats()["refreshed_menu_items"],
                {
                    "Window_Test_1_Sub_Test_1": 1,
                    "Window_Test_1_Sub_Test_2": 1,
                    "Window_Test_1_Sub_Test_3": 1,
                    "Window_Test_1_Sub_Test_4": 1,
                    "Window_Test_2": 1,
                    "Window_Test_3": 1,
                    "Window_Test_4": 1,
                },
            )

            # refresh
            omni.kit.menu.utils.refresh_menu_items("Window/Test 2")
            omni.kit.menu.utils.refresh_menu_items("Window/Test 3")

            await ui_test.menu_click("Window", show=True)
            await ui_test.human_delay(10)
            await ui_test.menu_click("Window", show=False)
            await ui_test.human_delay(10)
            # all items should be 1 except Window_Test_2 & Window_Test_3 which are 2
            self.assertEqual(
                omni.kit.menu.utils.get_debug_stats()["refreshed_menu_items"],
                {
                    "Window_Test_1_Sub_Test_1": 1,
                    "Window_Test_1_Sub_Test_2": 1,
                    "Window_Test_1_Sub_Test_3": 1,
                    "Window_Test_1_Sub_Test_4": 1,
                    "Window_Test_2": 2,
                    "Window_Test_3": 2,
                    "Window_Test_4": 1,
                },
            )

            # refresh
            omni.kit.menu.utils.refresh_menu_items("Window/Test 1/Sub Test 1")
            omni.kit.menu.utils.refresh_menu_items("Window/Test 1/Sub Test 2")

            await ui_test.menu_click("Window", show=True)
            await ui_test.human_delay(10)
            await ui_test.menu_click("Window", show=False)
            await ui_test.human_delay(10)
            self.assertEqual(
                omni.kit.menu.utils.get_debug_stats()["refreshed_menu_items"],
                {
                    "Window_Test_1_Sub_Test_1": 2,
                    "Window_Test_1_Sub_Test_2": 2,
                    "Window_Test_1_Sub_Test_3": 1,
                    "Window_Test_1_Sub_Test_4": 1,
                    "Window_Test_2": 2,
                    "Window_Test_3": 2,
                    "Window_Test_4": 1,
                },
            )
        finally:
            omni.kit.menu.utils.remove_menu_items(menu_list, "Window")
            self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

    async def test_refresh_windows_with_separator(self):
        sub_menu = [
            MenuItemDescription(name=""),
            MenuItemDescription(name=""),
            MenuItemDescription(name=""),
            MenuItemDescription(name=""),
        ]
        menu_list = [
            MenuItemDescription(name="Test", sub_menu=sub_menu),
            MenuItemDescription(name=""),
            MenuItemDescription(name=""),
            MenuItemDescription(name=""),
        ]

        omni.kit.menu.utils.add_menu_items(menu_list, "Window", 99)
        omni.kit.menu.utils.rebuild_menus()
        await ui_test.human_delay(50)

        await ui_test.menu_click("Window", show=True)
        await ui_test.human_delay(10)
        await ui_test.menu_click("Window", show=False)
        await ui_test.human_delay(10)

        try:
            # verify menus are initially correct
            verify_menu_items(
                self,
                [
                    (ui.Menu, "Window", True),
                    (ui.Menu, "Test", False),
                    (ui.Separator, "", False),
                    (ui.Separator, "", False),
                ],
            )

            # refresh
            omni.kit.menu.utils.refresh_menu_items("Window")
            await ui_test.menu_click("Window", show=True)
            await ui_test.human_delay(10)
            await ui_test.menu_click("Window", show=False)
            await ui_test.human_delay(10)

            # verify menus have not changed during refresh
            verify_menu_items(
                self,
                [
                    (ui.Menu, "Window", True),
                    (ui.Menu, "Test", False),
                    (ui.Separator, "", False),
                    (ui.Separator, "", False),
                ],
            )

            # refresh
            omni.kit.menu.utils.refresh_menu_items("Window/Test 2")
            omni.kit.menu.utils.refresh_menu_items("Window/Test 3")

            await ui_test.menu_click("Window", show=True)
            await ui_test.human_delay(10)
            await ui_test.menu_click("Window", show=False)
            await ui_test.human_delay(10)

            # verify menus have not changed during refresh
            verify_menu_items(
                self,
                [
                    (ui.Menu, "Window", True),
                    (ui.Menu, "Test", False),
                    (ui.Separator, "", False),
                    (ui.Separator, "", False),
                ],
            )
        finally:
            omni.kit.menu.utils.remove_menu_items(menu_list, "Window")
            self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})
