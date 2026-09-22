import omni.kit.test
import omni.ui as ui
from omni.kit import ui_test
from omni.kit.menu.utils import MenuItemDescription
from omni.ui.tests.test_base import OmniUiTest

from .utils import verify_menu_items


class TestReplace(OmniUiTest):
    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def test_replace_menus(self):
        omni.kit.menu.utils.set_default_menu_priority("Window", 99)

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
        new_menu_list = [
            MenuItemDescription(name="xTest 1", sub_menu=sub_menu),
            MenuItemDescription(name="xTest 2"),
            MenuItemDescription(name="xTest 3"),
            MenuItemDescription(name="xTest 4"),
        ]

        omni.kit.menu.utils.add_menu_items(menu_list, "Window")
        omni.kit.menu.utils.rebuild_menus()
        await ui_test.human_delay(10)

        # verify
        try:
            verify_menu_items(
                self,
                [
                    (ui.Menu, "Window", True),
                    (ui.Menu, "Test 1", True),
                    (ui.MenuItem, "Test 2", True),
                    (ui.MenuItem, "Test 3", True),
                    (ui.MenuItem, "Test 4", True),
                    (ui.MenuItem, "Sub Test 1", True),
                    (ui.MenuItem, "Sub Test 2", True),
                    (ui.MenuItem, "Sub Test 3", True),
                    (ui.MenuItem, "Sub Test 4", True),
                ],
            )
        finally:
            pass

        omni.kit.menu.utils.replace_menu_items(new_menu_list, menu_list, "Window")
        omni.kit.menu.utils.rebuild_menus()
        await ui_test.human_delay(10)

        # verify
        try:
            verify_menu_items(
                self,
                [
                    (ui.Menu, "Window", True),
                    (ui.Menu, "xTest 1", True),
                    (ui.MenuItem, "xTest 2", True),
                    (ui.MenuItem, "xTest 3", True),
                    (ui.MenuItem, "xTest 4", True),
                    (ui.MenuItem, "Sub Test 1", True),
                    (ui.MenuItem, "Sub Test 2", True),
                    (ui.MenuItem, "Sub Test 3", True),
                    (ui.MenuItem, "Sub Test 4", True),
                ],
            )
        finally:
            pass

        omni.kit.menu.utils.remove_menu_items(new_menu_list, "Window")
        self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})
