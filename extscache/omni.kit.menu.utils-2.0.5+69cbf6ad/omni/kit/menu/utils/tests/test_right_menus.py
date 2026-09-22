# pylint: disable=useless-parent-delegation
from typing import Union

import omni.kit.test
import omni.ui as ui
from omni.kit import ui_test
from omni.kit.menu.utils import MenuAlignment, MenuItemDescription

from .utils import refresh_menus, verify_menu_items


class TestMenuRightAlignedUtils(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def test_right_menu(self):
        class MenuDelegate(ui.MenuDelegate):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)

            def build_item(self, item: ui.MenuHelper):
                super().build_item(item)

            def build_status(self, item: ui.MenuHelper):
                super().build_status(item)

            def build_title(self, item: ui.MenuHelper):
                super().build_title(item)

            def get_menu_alignment(self):
                return MenuAlignment.RIGHT

        class MenuDelegateHidden(MenuDelegate):
            def update_menu_item(self, menu_item: Union[ui.Menu, ui.MenuItem], menu_refresh: bool):
                if isinstance(menu_item, ui.MenuItem):
                    menu_item.visible = False
                elif isinstance(menu_item, ui.Menu):
                    menu_item.visible = True

        class MenuDelegateButton(MenuDelegate):
            def build_item(self, item: ui.MenuHelper):
                with ui.HStack(width=0):
                    with ui.VStack(content_clipping=1, width=0):
                        ui.Button("Button", style={"margin": 0}, clicked_fn=lambda: print("clicked"))

        # ----------------------------------------------------
        # left aligned menu
        # ----------------------------------------------------
        submenu_list3 = [MenuItemDescription(name="SubMenu Item")]
        submenu_list2 = [MenuItemDescription(name="SubMenu 2", sub_menu=submenu_list3)]
        submenu_list1 = [MenuItemDescription(name="SubMenu 1", sub_menu=submenu_list2)]
        left_menu_list = [MenuItemDescription(name="Root Item", sub_menu=submenu_list1)]
        right_menu1 = None
        right_menu2 = None
        right_menu3 = None
        right_menu4 = None

        # add menu
        omni.kit.menu.utils.add_menu_items(left_menu_list, "SubMenu Test", 99)

        try:
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.Menu, "Root Item", True),
                    (ui.Menu, "SubMenu 1", True),
                    (ui.Menu, "SubMenu 2", True),
                    (ui.MenuItem, "SubMenu Item", True),
                ],
            )
            # refresh and verify
            # open menu as items are not refreshed on refresh_menu_items
            await refresh_menus("SubMenu Test")

            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.Menu, "Root Item", True),
                    (ui.Menu, "SubMenu 1", True),
                    (ui.Menu, "SubMenu 2", True),
                    (ui.MenuItem, "SubMenu Item", True),
                ],
            )

            # ----------------------------------------------------
            # right aligned menu
            # ----------------------------------------------------
            right_menu_list = [MenuItemDescription(name="SubMenu Item 1"), MenuItemDescription(name="SubMenu Item 2")]
            right_menu1 = omni.kit.menu.utils.add_menu_items(
                right_menu_list, "Right Menu Test 1", delegate=MenuDelegate()
            )
            right_menu2 = omni.kit.menu.utils.add_menu_items(
                right_menu_list, "Right Menu Test 2", delegate=MenuDelegate()
            )
            right_menu3 = omni.kit.menu.utils.add_menu_items([], name="Empty Menu", delegate=MenuDelegateHidden())
            right_menu4 = omni.kit.menu.utils.add_menu_items([], name="Button Menu", delegate=MenuDelegateButton())

            # wait for menus to redraw
            await ui_test.human_delay(10)

            # verify
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.Spacer, True),
                    (ui.Menu, "Right Menu Test 1", True),
                    (ui.Menu, "Right Menu Test 2", True),
                    (ui.Menu, "Empty Menu", True),
                    (ui.Menu, "Button Menu", True),
                    (ui.Spacer, True),
                    (ui.Menu, "Root Item", True),
                    (ui.Menu, "SubMenu 1", True),
                    (ui.Menu, "SubMenu 2", True),
                    (ui.MenuItem, "SubMenu Item", True),
                    (ui.MenuItem, "SubMenu Item 1", True),
                    (ui.MenuItem, "SubMenu Item 2", True),
                    (ui.MenuItem, "SubMenu Item 1", True),
                    (ui.MenuItem, "SubMenu Item 2", True),
                    (ui.MenuItem, "placeholder", False),
                    (ui.MenuItem, "placeholder", False),
                ],
                True,
            )

            # refresh and verify
            # open menu as items are not refreshed on refresh_menu_items
            await refresh_menus("Right Menu Test 1")

            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.Spacer, True),
                    (ui.Menu, "Right Menu Test 1", True),
                    (ui.Menu, "Right Menu Test 2", True),
                    (ui.Menu, "Empty Menu", True),
                    (ui.Menu, "Button Menu", True),
                    (ui.Spacer, True),
                    (ui.Menu, "Root Item", True),
                    (ui.Menu, "SubMenu 1", True),
                    (ui.Menu, "SubMenu 2", True),
                    (ui.MenuItem, "SubMenu Item", True),
                    (ui.MenuItem, "SubMenu Item 1", True),
                    (ui.MenuItem, "SubMenu Item 2", True),
                    (ui.MenuItem, "SubMenu Item 1", True),
                    (ui.MenuItem, "SubMenu Item 2", True),
                    (ui.MenuItem, "placeholder", False),
                    (ui.MenuItem, "placeholder", False),
                ],
                True,
            )
        finally:
            # remove menus
            omni.kit.menu.utils.remove_menu_items(left_menu_list, "SubMenu Test")
            omni.kit.menu.utils.remove_menu_items(right_menu1, "Right Menu Test 1")
            omni.kit.menu.utils.remove_menu_items(right_menu2, "Right Menu Test 2")
            omni.kit.menu.utils.remove_menu_items(right_menu3, "Empty Menu")
            omni.kit.menu.utils.remove_menu_items(right_menu4, "Button Menu")
            # verify menus removed
            self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

    async def test_multi_delegate_menu(self):
        class MenuDelegate(ui.MenuDelegate):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)

            def build_item(self, item: ui.MenuHelper):
                super().build_item(item)

            def build_status(self, item: ui.MenuHelper):
                super().build_status(item)

            def build_title(self, item: ui.MenuHelper):
                super().build_title(item)

            def get_menu_alignment(self):
                return MenuAlignment.RIGHT

        class MenuDelegateHidden(MenuDelegate):
            pass

        class MenuDelegateButton(MenuDelegate):
            pass

        # ----------------------------------------------------
        # left aligned menu
        # ----------------------------------------------------
        submenu_list3 = [MenuItemDescription(name="SubMenu Item")]
        submenu_list2 = [MenuItemDescription(name="SubMenu 2", sub_menu=submenu_list3)]
        submenu_list1 = [MenuItemDescription(name="SubMenu 1", sub_menu=submenu_list2)]
        left_menu_list = [MenuItemDescription(name="Root Item", sub_menu=submenu_list1)]
        right_menu1 = None
        right_menu2 = None
        right_menu3 = None
        right_menu4 = None

        # add menu
        omni.kit.menu.utils.add_menu_items(left_menu_list, "SubMenu Test", 99)
        try:
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.Menu, "Root Item", True),
                    (ui.Menu, "SubMenu 1", True),
                    (ui.Menu, "SubMenu 2", True),
                    (ui.MenuItem, "SubMenu Item", True),
                ],
            )
            # refresh and verify
            # open menu as items are not refreshed on refresh_menu_items
            await refresh_menus("SubMenu Test")

            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.Menu, "Root Item", True),
                    (ui.Menu, "SubMenu 1", True),
                    (ui.Menu, "SubMenu 2", True),
                    (ui.MenuItem, "SubMenu Item", True),
                ],
            )

            # ----------------------------------------------------
            # right aligned menu
            # ----------------------------------------------------
            md = MenuDelegate()
            right_menu_list = [MenuItemDescription(name="SubMenu Item 1"), MenuItemDescription(name="SubMenu Item 2")]
            right_menu1 = omni.kit.menu.utils.add_menu_items(right_menu_list, "Right Menu Test", delegate=md)
            right_menu2 = omni.kit.menu.utils.add_menu_items(right_menu_list, "Right Menu Test", delegate=md)
            right_menu3 = omni.kit.menu.utils.add_menu_items([], name="Right Menu Test", delegate=MenuDelegateHidden())
            right_menu4 = omni.kit.menu.utils.add_menu_items([], name="Right Menu Test", delegate=MenuDelegateButton())

            # wait for menus to redraw
            await ui_test.human_delay(10)

            # verify
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.Spacer, True),
                    (ui.Menu, "Right Menu Test", True),
                    (ui.Spacer, True),
                    (ui.Menu, "Root Item", True),
                    (ui.Menu, "SubMenu 1", True),
                    (ui.Menu, "SubMenu 2", True),
                    (ui.MenuItem, "SubMenu Item", True),
                    (ui.MenuItem, "SubMenu Item 1", True),
                    (ui.MenuItem, "SubMenu Item 2", True),
                    (ui.MenuItem, "placeholder", False),
                ],
                True,
            )

            # refresh and verify
            # open menu as items are not refreshed on refresh_menu_items
            await refresh_menus("Right Menu Test")

            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.Spacer, True),
                    (ui.Menu, "Right Menu Test", True),
                    (ui.Spacer, True),
                    (ui.Menu, "Root Item", True),
                    (ui.Menu, "SubMenu 1", True),
                    (ui.Menu, "SubMenu 2", True),
                    (ui.MenuItem, "SubMenu Item", True),
                    (ui.MenuItem, "SubMenu Item 1", True),
                    (ui.MenuItem, "SubMenu Item 2", True),
                    (ui.MenuItem, "placeholder", False),
                ],
                True,
            )
        finally:
            # remove menus
            omni.kit.menu.utils.remove_menu_items(left_menu_list, "SubMenu Test")
            omni.kit.menu.utils.remove_menu_items(right_menu1, "Right Menu Test")
            omni.kit.menu.utils.remove_menu_items(right_menu2, "Right Menu Test")
            omni.kit.menu.utils.remove_menu_items(right_menu3, "Right Menu Test")
            omni.kit.menu.utils.remove_menu_items(right_menu4, "Right Menu Test")
            # verify menus removed
            self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})
