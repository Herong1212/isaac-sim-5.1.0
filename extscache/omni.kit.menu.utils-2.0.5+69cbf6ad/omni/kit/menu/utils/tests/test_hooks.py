import omni.kit.test
import omni.ui as ui
from omni.kit import ui_test
from omni.kit.menu.utils import MenuItemDescription
from omni.ui.tests.test_base import OmniUiTest

from .utils import verify_menu_items


class TestHooks(OmniUiTest):
    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def test_hooks(self):
        def hook_func(merged_menu):
            for i in merged_menu["Window"]:
                i.name = i.name.replace("Test ", "xxText ")

        omni.kit.menu.utils.add_hook(hook_func)
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

        omni.kit.menu.utils.add_menu_items(menu_list, "Window")
        omni.kit.menu.utils.rebuild_menus()
        await ui_test.human_delay(10)

        # verify changes have been make via hook
        try:
            verify_menu_items(
                self,
                [
                    (ui.Menu, "Window", True),
                    (ui.Menu, "xxText 1", True),
                    (ui.MenuItem, "xxText 2", True),
                    (ui.MenuItem, "xxText 3", True),
                    (ui.MenuItem, "xxText 4", True),
                    (ui.MenuItem, "Sub Test 1", True),
                    (ui.MenuItem, "Sub Test 2", True),
                    (ui.MenuItem, "Sub Test 3", True),
                    (ui.MenuItem, "Sub Test 4", True),
                ],
            )
        finally:
            pass

        omni.kit.menu.utils.remove_hook(hook_func)
        omni.kit.menu.utils.remove_menu_items(menu_list, "Window")
        self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})
