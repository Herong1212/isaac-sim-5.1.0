# pylint: disable=too-many-lines
import omni.kit.test
import omni.ui as ui
from omni.kit import ui_test
from omni.kit.menu.utils import MenuItemDescription, MenuLayout

from .utils import refresh_menus, verify_menu_items


class TestMenuUtils(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def test_menus(self):
        menu_list = [MenuItemDescription(name="Exit")]
        layout_list = [MenuLayout.Menu("Test", [])]

        show_state = False

        def get_menu_test_state():
            nonlocal show_state
            return show_state

        # ----------------------------------------------------
        # verify add_menu_items
        # ----------------------------------------------------
        self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})
        omni.kit.menu.utils.add_menu_items(menu_list, "Test", 99)
        self.assertFalse(omni.kit.menu.utils.get_merged_menus() == {})

        # ----------------------------------------------------
        # verify add_layout
        # ----------------------------------------------------
        self.assertTrue(omni.kit.menu.utils.get_menu_layout() == [])
        omni.kit.menu.utils.add_layout(layout_list)
        self.assertFalse(omni.kit.menu.utils.get_menu_layout() == [])

        # ----------------------------------------------------
        # verify remove_layout & clean up
        # ----------------------------------------------------
        omni.kit.menu.utils.remove_layout(layout_list)
        self.assertTrue(omni.kit.menu.utils.get_menu_layout() == [])

        # ----------------------------------------------------
        # verify remove_menu_items & clean up
        # ----------------------------------------------------
        omni.kit.menu.utils.remove_menu_items(menu_list, "Test")
        self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

        # ----------------------------------------------------
        # check for recursive bugs - linked lists
        # ----------------------------------------------------
        submenu_list2 = [MenuItemDescription(name="Test2", sub_menu=None)]
        submenu_list1 = [MenuItemDescription(name="Test1", sub_menu=submenu_list2)]
        submenu_list2[0].sub_menu = submenu_list1
        menu_list = [MenuItemDescription(name="SubMenu Test", sub_menu=submenu_list1)]
        omni.kit.menu.utils.add_menu_items(menu_list, "SubMenu Test", 99)
        omni.kit.menu.utils.rebuild_menus()
        # open menu as items are not refreshed on refresh_menu_items
        await refresh_menus("SubMenu Test")
        omni.kit.menu.utils.remove_menu_items(menu_list, "SubMenu Test")
        self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

        # ----------------------------------------------------
        # check for recursive bugs - separator with sub_menus
        # ----------------------------------------------------
        submenu_list3 = [MenuItemDescription(name="SubMenu Item")]
        submenu_list2 = [MenuItemDescription(name="", sub_menu=submenu_list3)]
        submenu_list1 = [MenuItemDescription(name="", sub_menu=submenu_list2)]
        menu_list = [MenuItemDescription(name="SubMenu Test", sub_menu=submenu_list1)]
        omni.kit.menu.utils.add_menu_items(menu_list, "SubMenu Test", 99)
        omni.kit.menu.utils.rebuild_menus()
        # open menu as items are not refreshed on refresh_menu_items
        await refresh_menus("SubMenu Test")
        omni.kit.menu.utils.remove_menu_items(menu_list, "SubMenu Test")
        self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

        # ----------------------------------------------------
        # verify simple submenu
        # ----------------------------------------------------
        submenu_list3 = [MenuItemDescription(name="SubMenu Item")]
        submenu_list2 = [MenuItemDescription(name="SubMenu 2", sub_menu=submenu_list3)]
        submenu_list1 = [MenuItemDescription(name="SubMenu 1", sub_menu=submenu_list2)]
        menu_list = [MenuItemDescription(name="Root Item", sub_menu=submenu_list1)]
        # add menu
        omni.kit.menu.utils.add_menu_items(menu_list, "SubMenu Test", 99)
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
        finally:
            # remove menu
            omni.kit.menu.utils.remove_menu_items(menu_list, "SubMenu Test")
            self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

        # ----------------------------------------------------
        # verify submenu visibility - use show_fn to hide last item
        # ----------------------------------------------------
        submenu_list3 = [MenuItemDescription(name="SubMenu Item", show_fn=lambda: False)]
        submenu_list2 = [MenuItemDescription(name="SubMenu 2", sub_menu=submenu_list3)]
        submenu_list1 = [MenuItemDescription(name="SubMenu 1", sub_menu=submenu_list2)]
        menu_list = [
            MenuItemDescription(name="Root Item", sub_menu=submenu_list1),
            MenuItemDescription(name="Test Item"),
        ]
        # add menu
        omni.kit.menu.utils.add_menu_items(menu_list, "SubMenu Test", 99)
        try:
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.Menu, "Root Item", False),
                    (ui.MenuItem, "Test Item", True),
                    (ui.Menu, "SubMenu 1", False),
                    (ui.Menu, "SubMenu 2", False),
                    (ui.MenuItem, "SubMenu Item", False),
                ],
            )
            # rebuild and verify
            omni.kit.menu.utils.rebuild_menus()
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.Menu, "Root Item", False),
                    (ui.MenuItem, "Test Item", True),
                    (ui.Menu, "SubMenu 1", False),
                    (ui.Menu, "SubMenu 2", False),
                    (ui.MenuItem, "SubMenu Item", False),
                ],
            )
            # refresh and verify
            # open menu as items are not refreshed on refresh_menu_items
            await refresh_menus("SubMenu Test")
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.Menu, "Root Item", False),
                    (ui.MenuItem, "Test Item", True),
                    (ui.Menu, "SubMenu 1", False),
                    (ui.Menu, "SubMenu 2", False),
                    (ui.MenuItem, "SubMenu Item", False),
                ],
            )
        finally:
            # remove menu
            omni.kit.menu.utils.remove_menu_items(menu_list, "SubMenu Test")
            self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

        # ----------------------------------------------------
        # verify submenu visibility - use show_fn to control last item
        # ----------------------------------------------------
        submenu_list3 = [MenuItemDescription(name="SubMenu Item", show_fn=get_menu_test_state)]
        submenu_list2 = [MenuItemDescription(name="SubMenu 2", sub_menu=submenu_list3)]
        submenu_list1 = [MenuItemDescription(name="SubMenu 1", sub_menu=submenu_list2)]
        menu_list = [
            MenuItemDescription(name="Root Item", sub_menu=submenu_list1),
            MenuItemDescription(name="Test Item"),
        ]
        show_state = False
        # add menu
        omni.kit.menu.utils.add_menu_items(menu_list, "SubMenu Test", 99)
        try:
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.Menu, "Root Item", False),
                    (ui.MenuItem, "Test Item", True),
                    (ui.Menu, "SubMenu 1", False),
                    (ui.Menu, "SubMenu 2", False),
                    (ui.MenuItem, "SubMenu Item", False),
                ],
            )
            # refresh and verify
            show_state = True
            # open menu as items are not refreshed on refresh_menu_items
            await refresh_menus("SubMenu Test")
            await ui_test.human_delay()
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.Menu, "Root Item", True),
                    (ui.MenuItem, "Test Item", True),
                    (ui.Menu, "SubMenu 1", True),
                    (ui.Menu, "SubMenu 2", True),
                    (ui.MenuItem, "SubMenu Item", True),
                ],
            )
            # refresh and verify
            show_state = False
            # open menu as items are not refreshed on refresh_menu_items
            await refresh_menus("SubMenu Test")
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.Menu, "Root Item", False),
                    (ui.MenuItem, "Test Item", True),
                    (ui.Menu, "SubMenu 1", False),
                    (ui.Menu, "SubMenu 2", False),
                    (ui.MenuItem, "SubMenu Item", False),
                ],
            )
            # rebuild and verify
            show_state = True
            omni.kit.menu.utils.rebuild_menus()
            await ui_test.human_delay()
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.Menu, "Root Item", True),
                    (ui.MenuItem, "Test Item", True),
                    (ui.Menu, "SubMenu 1", True),
                    (ui.Menu, "SubMenu 2", True),
                    (ui.MenuItem, "SubMenu Item", True),
                ],
            )
            # rebuild and verify
            show_state = False
            omni.kit.menu.utils.rebuild_menus()
            await ui_test.human_delay()
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.Menu, "Root Item", False),
                    (ui.MenuItem, "Test Item", True),
                    (ui.Menu, "SubMenu 1", False),
                    (ui.Menu, "SubMenu 2", False),
                    (ui.MenuItem, "SubMenu Item", False),
                ],
            )
        finally:
            # remove menu
            omni.kit.menu.utils.remove_menu_items(menu_list, "SubMenu Test")
            self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

        # ----------------------------------------------------
        # verify show_fn on submenu
        # ----------------------------------------------------
        submenu_list3 = [MenuItemDescription(name="SubMenu Item")]
        submenu_list2 = [MenuItemDescription(name="SubMenu 2", sub_menu=submenu_list3)]
        submenu_list1 = [MenuItemDescription(name="SubMenu 1", show_fn=get_menu_test_state, sub_menu=submenu_list2)]
        menu_list = [
            MenuItemDescription(name="Root Item", sub_menu=submenu_list1),
            MenuItemDescription(name="Test Item"),
        ]
        show_state = False
        # add menu
        omni.kit.menu.utils.add_menu_items(menu_list, "SubMenu Test", 99)
        try:
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.Menu, "Root Item", False),
                    (ui.MenuItem, "Test Item", True),
                    (ui.Menu, "SubMenu 1", False),
                    (ui.Menu, "SubMenu 2", False),
                    (ui.MenuItem, "SubMenu Item", True),
                ],
            )
            # open menu as items are not refreshed on refresh_menu_items
            await refresh_menus("SubMenu Test")
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.Menu, "Root Item", False),
                    (ui.MenuItem, "Test Item", True),
                    (ui.Menu, "SubMenu 1", False),
                    (ui.Menu, "SubMenu 2", False),
                    (ui.MenuItem, "SubMenu Item", True),
                ],
            )
            # refresh and verify
            show_state = True
            # open menu as items are not refreshed on refresh_menu_items
            await refresh_menus("SubMenu Test")
            await ui_test.human_delay()
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.Menu, "Root Item", True),
                    (ui.MenuItem, "Test Item", True),
                    (ui.Menu, "SubMenu 1", True),
                    (ui.Menu, "SubMenu 2", True),
                    (ui.MenuItem, "SubMenu Item", True),
                ],
            )
            # rebuild and verify
            show_state = True
            omni.kit.menu.utils.rebuild_menus()
            await ui_test.human_delay()
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.Menu, "Root Item", True),
                    (ui.MenuItem, "Test Item", True),
                    (ui.Menu, "SubMenu 1", True),
                    (ui.Menu, "SubMenu 2", True),
                    (ui.MenuItem, "SubMenu Item", True),
                ],
            )
            # refresh and verify
            show_state = False
            # open menu as items are not refreshed on refresh_menu_items
            await refresh_menus("SubMenu Test")
            await ui_test.human_delay()
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.Menu, "Root Item", False),
                    (ui.MenuItem, "Test Item", True),
                    (ui.Menu, "SubMenu 1", False),
                    (ui.Menu, "SubMenu 2", False),
                    (ui.MenuItem, "SubMenu Item", True),
                ],
            )
            # rebuild and verify
            show_state = False
            omni.kit.menu.utils.rebuild_menus()
            await ui_test.human_delay()
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.Menu, "Root Item", False),
                    (ui.MenuItem, "Test Item", True),
                    (ui.Menu, "SubMenu 1", False),
                    (ui.Menu, "SubMenu 2", False),
                    (ui.MenuItem, "SubMenu Item", True),
                ],
            )
        finally:
            # remove menu
            omni.kit.menu.utils.remove_menu_items(menu_list, "SubMenu Test")
            self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

        # ----------------------------------------------------
        # verify show_fn on item
        # ----------------------------------------------------
        submenu_list3 = [MenuItemDescription(name="SubMenu Item", show_fn=get_menu_test_state)]
        submenu_list2 = [MenuItemDescription(name="SubMenu 2", sub_menu=submenu_list3)]
        submenu_list1 = [MenuItemDescription(name="SubMenu 1", sub_menu=submenu_list2)]
        menu_list = [
            MenuItemDescription(name="Root Item", sub_menu=submenu_list1),
            MenuItemDescription(name="Test Item"),
        ]
        show_state = False
        # add menu
        omni.kit.menu.utils.add_menu_items(menu_list, "SubMenu Test", 99)
        try:
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.Menu, "Root Item", False),
                    (ui.MenuItem, "Test Item", True),
                    (ui.Menu, "SubMenu 1", False),
                    (ui.Menu, "SubMenu 2", False),
                    (ui.MenuItem, "SubMenu Item", False),
                ],
            )
            # refresh and verify
            show_state = True
            # open menu as items are not refreshed on refresh_menu_items
            await refresh_menus("SubMenu Test")
            await ui_test.human_delay()
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.Menu, "Root Item", True),
                    (ui.MenuItem, "Test Item", True),
                    (ui.Menu, "SubMenu 1", True),
                    (ui.Menu, "SubMenu 2", True),
                    (ui.MenuItem, "SubMenu Item", True),
                ],
            )
            # rebuild and verify
            show_state = True
            omni.kit.menu.utils.rebuild_menus()
            await ui_test.human_delay()
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.Menu, "Root Item", True),
                    (ui.MenuItem, "Test Item", True),
                    (ui.Menu, "SubMenu 1", True),
                    (ui.Menu, "SubMenu 2", True),
                    (ui.MenuItem, "SubMenu Item", True),
                ],
            )
            # refresh and verify
            show_state = False
            # open menu as items are not refreshed on refresh_menu_items
            await refresh_menus("SubMenu Test")
            await ui_test.human_delay()
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.Menu, "Root Item", False),
                    (ui.MenuItem, "Test Item", True),
                    (ui.Menu, "SubMenu 1", False),
                    (ui.Menu, "SubMenu 2", False),
                    (ui.MenuItem, "SubMenu Item", False),
                ],
            )
            # rebuild and verify
            show_state = False
            omni.kit.menu.utils.rebuild_menus()
            await ui_test.human_delay()
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.Menu, "Root Item", False),
                    (ui.MenuItem, "Test Item", True),
                    (ui.Menu, "SubMenu 1", False),
                    (ui.Menu, "SubMenu 2", False),
                    (ui.MenuItem, "SubMenu Item", False),
                ],
            )
        finally:
            # remove menu
            omni.kit.menu.utils.remove_menu_items(menu_list, "SubMenu Test")
            self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

        # ----------------------------------------------------
        # verify sub_menu
        # ----------------------------------------------------
        submenu_list3 = [MenuItemDescription(name="SubMenu Item 1"), MenuItemDescription(name="SubMenu Item 2")]
        submenu_list2 = [MenuItemDescription(name="SubMenu 2", sub_menu=submenu_list3)]
        submenu_list1 = [MenuItemDescription(name="SubMenu 1", sub_menu=submenu_list2)]
        menu_list = [MenuItemDescription(name="Root Item", sub_menu=submenu_list1)]
        # add menu
        omni.kit.menu.utils.add_menu_items(menu_list, "SubMenu Test", 99)
        try:
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.Menu, "Root Item", True),
                    (ui.Menu, "SubMenu 1", True),
                    (ui.Menu, "SubMenu 2", True),
                    (ui.MenuItem, "SubMenu Item 1", True),
                    (ui.MenuItem, "SubMenu Item 2", True),
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
                    (ui.MenuItem, "SubMenu Item 1", True),
                    (ui.MenuItem, "SubMenu Item 2", True),
                ],
            )
        finally:
            # remove menu
            omni.kit.menu.utils.remove_menu_items(menu_list, "SubMenu Test")
            self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

        # ----------------------------------------------------
        # verify show_fn on item with two items one item hidden
        # ----------------------------------------------------
        submenu_list3 = [
            MenuItemDescription(name="SubMenu Item 1", show_fn=get_menu_test_state),
            MenuItemDescription(name="SubMenu Item 2"),
        ]
        submenu_list2 = [MenuItemDescription(name="SubMenu 2", sub_menu=submenu_list3)]
        submenu_list1 = [MenuItemDescription(name="SubMenu 1", sub_menu=submenu_list2)]
        menu_list = [
            MenuItemDescription(name="Root Item", sub_menu=submenu_list1),
            MenuItemDescription(name="Test Item"),
        ]
        show_state = False
        # add menu
        omni.kit.menu.utils.add_menu_items(menu_list, "SubMenu Test", 99)
        try:
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.Menu, "Root Item", True),
                    (ui.MenuItem, "Test Item", True),
                    (ui.Menu, "SubMenu 1", True),
                    (ui.Menu, "SubMenu 2", True),
                    (ui.MenuItem, "SubMenu Item 1", False),
                    (ui.MenuItem, "SubMenu Item 2", True),
                ],
            )
            # refresh and verify
            show_state = True
            # open menu as items are not refreshed on refresh_menu_items
            await refresh_menus("SubMenu Test")
            await ui_test.human_delay()
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.Menu, "Root Item", True),
                    (ui.MenuItem, "Test Item", True),
                    (ui.Menu, "SubMenu 1", True),
                    (ui.Menu, "SubMenu 2", True),
                    (ui.MenuItem, "SubMenu Item 1", True),
                    (ui.MenuItem, "SubMenu Item 2", True),
                ],
            )
            # rebuild and verify
            show_state = True
            omni.kit.menu.utils.rebuild_menus()
            await ui_test.human_delay()
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.Menu, "Root Item", True),
                    (ui.MenuItem, "Test Item", True),
                    (ui.Menu, "SubMenu 1", True),
                    (ui.Menu, "SubMenu 2", True),
                    (ui.MenuItem, "SubMenu Item 1", True),
                    (ui.MenuItem, "SubMenu Item 2", True),
                ],
            )
            # refresh and verify
            show_state = False
            # open menu as items are not refreshed on refresh_menu_items
            await refresh_menus("SubMenu Test")
            await ui_test.human_delay()
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.Menu, "Root Item", True),
                    (ui.MenuItem, "Test Item", True),
                    (ui.Menu, "SubMenu 1", True),
                    (ui.Menu, "SubMenu 2", True),
                    (ui.MenuItem, "SubMenu Item 1", False),
                    (ui.MenuItem, "SubMenu Item 2", True),
                ],
            )
            # rebuild and verify
            show_state = False
            omni.kit.menu.utils.rebuild_menus()
            await ui_test.human_delay()
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.Menu, "Root Item", True),
                    (ui.MenuItem, "Test Item", True),
                    (ui.Menu, "SubMenu 1", True),
                    (ui.Menu, "SubMenu 2", True),
                    (ui.MenuItem, "SubMenu Item 1", False),
                    (ui.MenuItem, "SubMenu Item 2", True),
                ],
            )
        finally:
            # remove menu
            omni.kit.menu.utils.remove_menu_items(menu_list, "SubMenu Test")
            self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

        # ----------------------------------------------------
        # verify show_fn on item with two items 1st one hidden
        # ----------------------------------------------------
        menu_list = [
            MenuItemDescription(name="SubMenu Item 1", show_fn=get_menu_test_state),
            MenuItemDescription(name="SubMenu Item 2"),
        ]
        show_state = False
        # add menu
        omni.kit.menu.utils.add_menu_items(menu_list, "SubMenu Test", 99)
        try:
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.MenuItem, "SubMenu Item 1", False),
                    (ui.MenuItem, "SubMenu Item 2", True),
                ],
            )
            # refresh and verify
            show_state = True
            # open menu as items are not refreshed on refresh_menu_items
            await refresh_menus("SubMenu Test")
            await ui_test.human_delay()
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.MenuItem, "SubMenu Item 1", True),
                    (ui.MenuItem, "SubMenu Item 2", True),
                ],
            )
            # rebuild and verify
            show_state = True
            omni.kit.menu.utils.rebuild_menus()
            await ui_test.human_delay()
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.MenuItem, "SubMenu Item 1", True),
                    (ui.MenuItem, "SubMenu Item 2", True),
                ],
            )
            # refresh and verify
            show_state = False
            # open menu as items are not refreshed on refresh_menu_items
            await refresh_menus("SubMenu Test")
            await ui_test.human_delay()
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.MenuItem, "SubMenu Item 1", False),
                    (ui.MenuItem, "SubMenu Item 2", True),
                ],
            )
            # rebuild and verify
            show_state = False
            omni.kit.menu.utils.rebuild_menus()
            await ui_test.human_delay()
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.MenuItem, "SubMenu Item 1", False),
                    (ui.MenuItem, "SubMenu Item 2", True),
                ],
            )
        finally:
            # remove menu
            omni.kit.menu.utils.remove_menu_items(menu_list, "SubMenu Test")
            self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

        # ----------------------------------------------------
        # verify show_fn on item with two items 2nd one hidden
        # ----------------------------------------------------
        menu_list = [
            MenuItemDescription(name="SubMenu Item 1"),
            MenuItemDescription(name="SubMenu Item 2", show_fn=get_menu_test_state),
        ]
        show_state = False
        # add menu
        omni.kit.menu.utils.add_menu_items(menu_list, "SubMenu Test", 99)
        try:
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.MenuItem, "SubMenu Item 1", True),
                    (ui.MenuItem, "SubMenu Item 2", False),
                ],
            )
            # refresh and verify
            show_state = True
            # open menu as items are not refreshed on refresh_menu_items
            await refresh_menus("SubMenu Test")
            await ui_test.human_delay()
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.MenuItem, "SubMenu Item 1", True),
                    (ui.MenuItem, "SubMenu Item 2", True),
                ],
            )
            # rebuild and verify
            show_state = True
            omni.kit.menu.utils.rebuild_menus()
            await ui_test.human_delay()
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.MenuItem, "SubMenu Item 1", True),
                    (ui.MenuItem, "SubMenu Item 2", True),
                ],
            )
            # refresh and verify
            show_state = False
            # open menu as items are not refreshed on refresh_menu_items
            await refresh_menus("SubMenu Test")
            await ui_test.human_delay()
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.MenuItem, "SubMenu Item 1", True),
                    (ui.MenuItem, "SubMenu Item 2", False),
                ],
            )
            # rebuild and verify
            show_state = False
            omni.kit.menu.utils.rebuild_menus()
            await ui_test.human_delay()
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", True),
                    (ui.MenuItem, "SubMenu Item 1", True),
                    (ui.MenuItem, "SubMenu Item 2", False),
                ],
            )
        finally:
            # remove menu
            omni.kit.menu.utils.remove_menu_items(menu_list, "SubMenu Test")
            self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

        # ----------------------------------------------------
        # add menu/remove menu - menu should disapear
        # ----------------------------------------------------
        menu_list = [MenuItemDescription(name="Item 1"), MenuItemDescription(name="Item 2")]
        # add menu
        omni.kit.menu.utils.add_menu_items(menu_list, "SubMenu Test 1", 99)
        omni.kit.menu.utils.add_menu_items(menu_list, "SubMenu Test 2", 99)
        # remove menu
        omni.kit.menu.utils.remove_menu_items(menu_list, "SubMenu Test 1")
        try:
            # verify "SubMenu Test 1" is not 1st
            verify_menu_items(
                self, [(ui.Menu, "SubMenu Test 2", True), (ui.MenuItem, "Item 1", True), (ui.MenuItem, "Item 2", True)]
            )
        finally:
            # remove menu
            omni.kit.menu.utils.remove_menu_items(menu_list, "SubMenu Test 2")
            self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

        # ----------------------------------------------------
        # add empty menu test
        # ----------------------------------------------------
        menu_list = []
        # add menu
        omni.kit.menu.utils.add_menu_items(menu_list, "Menu Test", 99)
        try:
            # verify "SubMenu Test 1" is not 1st
            verify_menu_items(self, [])
        finally:
            # remove menu
            omni.kit.menu.utils.remove_menu_items(menu_list, "Menu Test")
            self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

    async def test_menu_layout(self):
        submenu_list3 = [MenuItemDescription(name="SubMenu Item 1"), MenuItemDescription(name="SubMenu Item 2")]
        submenu_list2 = [MenuItemDescription(name="SubMenu 2", sub_menu=submenu_list3)]
        submenu_list1 = [MenuItemDescription(name="SubMenu 1", sub_menu=submenu_list2)]
        menu_list = [
            MenuItemDescription(name="Root Item", sub_menu=submenu_list1),
            MenuItemDescription(name="Test Item"),
        ]
        menu_placeholder = [MenuItemDescription(name="placeholder", show_fn=lambda: False)]

        # add menu
        omni.kit.menu.utils.add_menu_items(menu_placeholder, "Layout Test", 190)
        omni.kit.menu.utils.add_menu_items(menu_list, "SubMenu Test", 99)
        await ui_test.human_delay()

        # ----------------------------------------------------
        # simple layout test
        # ----------------------------------------------------
        menu_layout = [
            MenuLayout.Menu(
                "Layout Test",
                [
                    MenuLayout.Item("Test Item"),
                    MenuLayout.Seperator(),
                    MenuLayout.Item("SubMenu Item 1"),
                    MenuLayout.Item("SubMenu Item 2"),
                ],
            ),
            MenuLayout.Menu("SubMenu Test", remove=True),
        ]
        omni.kit.menu.utils.add_layout(menu_layout)
        try:
            # verify layout
            verify_menu_items(
                self,
                [
                    (ui.Menu, "Layout Test", True),
                    (ui.MenuItem, "Test Item", True),
                    (ui.Separator, "", True),
                    (ui.MenuItem, "SubMenu Item 1", True),
                    (ui.MenuItem, "SubMenu Item 2", True),
                    (ui.MenuItem, "placeholder", False),
                ],
            )
        finally:
            # remove layout
            omni.kit.menu.utils.remove_layout(menu_layout)
            self.assertTrue(omni.kit.menu.utils.get_menu_layout() == [])

        # ----------------------------------------------------
        # simple layout test with named seperator
        # ----------------------------------------------------
        menu_layout = [
            MenuLayout.Menu(
                "Layout Test",
                [
                    MenuLayout.Item("Test Item"),
                    MenuLayout.Seperator("Header"),
                    MenuLayout.Item("SubMenu Item 1"),
                    MenuLayout.Item("SubMenu Item 2"),
                ],
            ),
            MenuLayout.Menu("SubMenu Test", remove=True),
        ]
        omni.kit.menu.utils.add_layout(menu_layout)
        try:
            # verify layout
            verify_menu_items(
                self,
                [
                    (ui.Menu, "Layout Test", True),
                    (ui.MenuItem, "Test Item", True),
                    (ui.Separator, "Header", True),
                    (ui.MenuItem, "SubMenu Item 1", True),
                    (ui.MenuItem, "SubMenu Item 2", True),
                    (ui.MenuItem, "placeholder", False),
                ],
            )
        finally:
            # remove layout
            omni.kit.menu.utils.remove_layout(menu_layout)
            self.assertTrue(omni.kit.menu.utils.get_menu_layout() == [])

        # ----------------------------------------------------
        # simple layout test with group
        # ----------------------------------------------------
        menu_layout = [
            MenuLayout.Menu(
                "Layout Test",
                [
                    MenuLayout.Item("Test Item"),
                    MenuLayout.Group(
                        "Items",
                        [
                            MenuLayout.Item("SubMenu Item 1"),
                            MenuLayout.Item("SubMenu Item 2"),
                        ],
                    ),
                ],
            ),
        ]
        omni.kit.menu.utils.add_layout(menu_layout)

        try:
            # verify layout
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", False),
                    (ui.Menu, "Layout Test", True),
                    (ui.Menu, "Root Item", False),
                    (ui.Menu, "SubMenu 1", False),
                    (ui.Menu, "SubMenu 2", False),
                    (ui.MenuItem, "Test Item", True),
                    (ui.Separator, "Items", True),
                    (ui.MenuItem, "SubMenu Item 1", True),
                    (ui.MenuItem, "SubMenu Item 2", True),
                    (ui.MenuItem, "placeholder", False),
                ],
            )
        finally:
            # remove layout
            omni.kit.menu.utils.remove_layout(menu_layout)
            self.assertTrue(omni.kit.menu.utils.get_menu_layout() == [])

        # ----------------------------------------------------
        # simple layout test with renamed items
        # ----------------------------------------------------
        menu_layout = [
            MenuLayout.Menu(
                "Layout Test",
                [
                    MenuLayout.Item("Test Item"),
                    MenuLayout.Seperator(),
                    MenuLayout.Item("Item 1", source="SubMenu Test/Root Item/SubMenu 1/SubMenu 2/SubMenu Item 1"),
                    MenuLayout.Item("Item 2", source="SubMenu Test/Root Item/SubMenu 1/SubMenu 2/SubMenu Item 2"),
                ],
            ),
        ]
        omni.kit.menu.utils.add_layout(menu_layout)
        try:
            # verify layout
            verify_menu_items(
                self,
                [
                    (ui.Menu, "SubMenu Test", False),
                    (ui.Menu, "Layout Test", True),
                    (ui.Menu, "Root Item", False),
                    (ui.Menu, "SubMenu 1", False),
                    (ui.Menu, "SubMenu 2", False),
                    (ui.MenuItem, "Test Item", True),
                    (ui.Separator, "", True),
                    (ui.MenuItem, "Item 1", True),
                    (ui.MenuItem, "Item 2", True),
                    (ui.MenuItem, "placeholder", False),
                ],
            )
        finally:
            # remove layout
            omni.kit.menu.utils.remove_layout(menu_layout)
            self.assertTrue(omni.kit.menu.utils.get_menu_layout() == [])

        # ----------------------------------------------------
        # simple layout test with submenu and renamed items in subdir - submenu doesn't exist
        # ----------------------------------------------------
        menu_layout = [
            MenuLayout.Menu(
                "Layout Test",
                [
                    MenuLayout.Item("Test Item"),
                    MenuLayout.SubMenu(
                        "Items",
                        [
                            MenuLayout.Item(
                                "Item 1", source="SubMenu Test/Root Item/SubMenu 1/SubMenu 2/SubMenu Item 1"
                            ),
                            MenuLayout.Item(
                                "Item 2", source="SubMenu Test/Root Item/SubMenu 1/SubMenu 2/SubMenu Item 2"
                            ),
                        ],
                    ),
                    MenuLayout.Menu("SubMenu Test", remove=True),
                ],
            ),
        ]
        omni.kit.menu.utils.add_layout(menu_layout)
        try:
            # verify layout
            verify_menu_items(
                self,
                [
                    (ui.Menu, "Layout Test", True),
                    (ui.MenuItem, "Test Item", True),
                    (ui.Menu, "Items", True),
                    (ui.MenuItem, "placeholder", False),
                    (ui.MenuItem, "Item 1", True),
                    (ui.MenuItem, "Item 2", True),
                ],
            )
        finally:
            # remove layout
            omni.kit.menu.utils.remove_layout(menu_layout)
            self.assertTrue(omni.kit.menu.utils.get_menu_layout() == [])

        # ----------------------------------------------------
        # simple layout test with submenu and renamed items in subdir - submenu exists
        # ----------------------------------------------------
        menu_layout = [
            MenuLayout.Menu(
                "Layout Test",
                [
                    MenuLayout.Item("Test Item"),
                    MenuLayout.SubMenu(
                        "Items",
                        [
                            MenuLayout.Item(
                                "Item 1", source="SubMenu Test/Root Item/SubMenu 1/SubMenu 2/SubMenu Item 1"
                            ),
                            MenuLayout.Item(
                                "Item 2", source="SubMenu Test/Root Item/SubMenu 1/SubMenu 2/SubMenu Item 2"
                            ),
                        ],
                    ),
                    MenuLayout.Menu("SubMenu Test", remove=True),
                ],
            ),
        ]
        items_menu_list = [MenuItemDescription(name="Items", sub_menu=[MenuItemDescription(name="Item 3")])]
        omni.kit.menu.utils.add_menu_items(items_menu_list, "Layout Test", 99)
        omni.kit.menu.utils.add_layout(menu_layout)
        try:
            # verify layout
            verify_menu_items(
                self,
                [
                    (ui.Menu, "Layout Test", True),
                    (ui.MenuItem, "Test Item", True),
                    (ui.Menu, "Items", True),
                    (ui.MenuItem, "placeholder", False),
                    (ui.MenuItem, "Item 1", True),
                    (ui.MenuItem, "Item 2", True),
                    (ui.MenuItem, "Item 3", True),
                ],
            )
        finally:
            # remove layout
            omni.kit.menu.utils.remove_menu_items(items_menu_list, "Layout Test")
            omni.kit.menu.utils.remove_layout(menu_layout)
            self.assertTrue(omni.kit.menu.utils.get_menu_layout() == [])

        # ----------------------------------------------------
        # simple layout test with submenu and renamed items in subdir - submenu exists non-sorted
        # ----------------------------------------------------
        word_list = [
            "Scribble",
            "Aftermath",
            "Spy",
            "Imminent",
            "Direct",
            "Berserk",
            "Parsimonious",
            "Flashy",
            "Flawless",
            "Print",
            "Plate",
            "Smell",
            "Divergent",
            "Perpetual",
            "Complain",
            "Abrasive",
            "House",
            "Macabre",
            "Carry",
            "Itch",
            "Penitent",
            "Stain",
            "Mother",
            "Fork",
        ]

        submenu_list = []
        for word in word_list:
            submenu_list.append(MenuItemDescription(name=word))
        items_menu_list = [MenuItemDescription(name="Items", sub_menu=submenu_list)]
        menu_layout = [
            MenuLayout.Menu(
                "Layout Test",
                [
                    MenuLayout.Item("Test Item"),
                    MenuLayout.SubMenu(
                        "Items",
                        [
                            MenuLayout.Item(
                                "Item 1", source="SubMenu Test/Root Item/SubMenu 1/SubMenu 2/SubMenu Item 1"
                            ),
                            MenuLayout.Item(
                                "Item 2", source="SubMenu Test/Root Item/SubMenu 1/SubMenu 2/SubMenu Item 2"
                            ),
                        ],
                    ),
                    MenuLayout.Menu("SubMenu Test", remove=True),
                ],
            ),
        ]
        omni.kit.menu.utils.add_menu_items(items_menu_list, "Layout Test", 99)
        omni.kit.menu.utils.add_layout(menu_layout)
        try:
            # verify layout
            verify_menu_items(
                self,
                [
                    (ui.Menu, "Layout Test", True),
                    (ui.MenuItem, "Test Item", True),
                    (ui.Menu, "Items", True),
                    (ui.MenuItem, "placeholder", False),
                    (ui.MenuItem, "Item 1", True),
                    (ui.MenuItem, "Item 2", True),
                    (ui.MenuItem, "Scribble", True),
                    (ui.MenuItem, "Aftermath", True),
                    (ui.MenuItem, "Spy", True),
                    (ui.MenuItem, "Imminent", True),
                    (ui.MenuItem, "Direct", True),
                    (ui.MenuItem, "Berserk", True),
                    (ui.MenuItem, "Parsimonious", True),
                    (ui.MenuItem, "Flashy", True),
                    (ui.MenuItem, "Flawless", True),
                    (ui.MenuItem, "Print", True),
                    (ui.MenuItem, "Plate", True),
                    (ui.MenuItem, "Smell", True),
                    (ui.MenuItem, "Divergent", True),
                    (ui.MenuItem, "Perpetual", True),
                    (ui.MenuItem, "Complain", True),
                    (ui.MenuItem, "Abrasive", True),
                    (ui.MenuItem, "House", True),
                    (ui.MenuItem, "Macabre", True),
                    (ui.MenuItem, "Carry", True),
                    (ui.MenuItem, "Itch", True),
                    (ui.MenuItem, "Penitent", True),
                    (ui.MenuItem, "Stain", True),
                    (ui.MenuItem, "Mother", True),
                    (ui.MenuItem, "Fork", True),
                ],
            )
            # verify items
            for _ in word_list:
                verify_menu_items(
                    self,
                    [
                        (ui.Menu, "Layout Test", True),
                        (ui.MenuItem, "Test Item", True),
                        (ui.Menu, "Items", True),
                        (ui.MenuItem, "placeholder", False),
                        (ui.MenuItem, "Item 1", True),
                        (ui.MenuItem, "Item 2", True),
                        (ui.MenuItem, "Scribble", True),
                        (ui.MenuItem, "Aftermath", True),
                        (ui.MenuItem, "Spy", True),
                        (ui.MenuItem, "Imminent", True),
                        (ui.MenuItem, "Direct", True),
                        (ui.MenuItem, "Berserk", True),
                        (ui.MenuItem, "Parsimonious", True),
                        (ui.MenuItem, "Flashy", True),
                        (ui.MenuItem, "Flawless", True),
                        (ui.MenuItem, "Print", True),
                        (ui.MenuItem, "Plate", True),
                        (ui.MenuItem, "Smell", True),
                        (ui.MenuItem, "Divergent", True),
                        (ui.MenuItem, "Perpetual", True),
                        (ui.MenuItem, "Complain", True),
                        (ui.MenuItem, "Abrasive", True),
                        (ui.MenuItem, "House", True),
                        (ui.MenuItem, "Macabre", True),
                        (ui.MenuItem, "Carry", True),
                        (ui.MenuItem, "Itch", True),
                        (ui.MenuItem, "Penitent", True),
                        (ui.MenuItem, "Stain", True),
                        (ui.MenuItem, "Mother", True),
                        (ui.MenuItem, "Fork", True),
                    ],
                )
        finally:
            # remove layout
            omni.kit.menu.utils.remove_menu_items(items_menu_list, "Layout Test")
            omni.kit.menu.utils.remove_layout(menu_layout)
            self.assertTrue(omni.kit.menu.utils.get_menu_layout() == [])

        # ----------------------------------------------------
        # simple layout test with submenu and renamed items in subdir - submenu exists sorted
        # ----------------------------------------------------
        menu_layout = [
            MenuLayout.Menu(
                "Layout Test",
                [
                    MenuLayout.Item("Test Item"),
                    MenuLayout.SubMenu(
                        "Items",
                        [
                            MenuLayout.Item(
                                "Item 1", source="SubMenu Test/Root Item/SubMenu 1/SubMenu 2/SubMenu Item 1"
                            ),
                            MenuLayout.Item(
                                "Item 2", source="SubMenu Test/Root Item/SubMenu 1/SubMenu 2/SubMenu Item 2"
                            ),
                            MenuLayout.Sort(exclude_items=[]),
                        ],
                    ),
                    MenuLayout.Menu("SubMenu Test", remove=True),
                ],
            ),
        ]
        omni.kit.menu.utils.add_menu_items(items_menu_list, "Layout Test", 99)
        omni.kit.menu.utils.add_layout(menu_layout)
        try:
            # verify layout
            verify_menu_items(
                self,
                [
                    (ui.Menu, "Layout Test", True),
                    (ui.MenuItem, "Test Item", True),
                    (ui.Menu, "Items", True),
                    (ui.MenuItem, "placeholder", False),
                    (ui.MenuItem, "Abrasive", True),
                    (ui.MenuItem, "Aftermath", True),
                    (ui.MenuItem, "Berserk", True),
                    (ui.MenuItem, "Carry", True),
                    (ui.MenuItem, "Complain", True),
                    (ui.MenuItem, "Direct", True),
                    (ui.MenuItem, "Divergent", True),
                    (ui.MenuItem, "Flashy", True),
                    (ui.MenuItem, "Flawless", True),
                    (ui.MenuItem, "Fork", True),
                    (ui.MenuItem, "House", True),
                    (ui.MenuItem, "Imminent", True),
                    (ui.MenuItem, "Itch", True),
                    (ui.MenuItem, "Item 1", True),
                    (ui.MenuItem, "Item 2", True),
                    (ui.MenuItem, "Macabre", True),
                    (ui.MenuItem, "Mother", True),
                    (ui.MenuItem, "Parsimonious", True),
                    (ui.MenuItem, "Penitent", True),
                    (ui.MenuItem, "Perpetual", True),
                    (ui.MenuItem, "Plate", True),
                    (ui.MenuItem, "Print", True),
                    (ui.MenuItem, "Scribble", True),
                    (ui.MenuItem, "Smell", True),
                    (ui.MenuItem, "Spy", True),
                    (ui.MenuItem, "Stain", True),
                ],
            )
        finally:
            # remove layout
            omni.kit.menu.utils.remove_menu_items(items_menu_list, "Layout Test")
            omni.kit.menu.utils.remove_layout(menu_layout)
            self.assertTrue(omni.kit.menu.utils.get_menu_layout() == [])

        # ----------------------------------------------------
        # simple layout test with submenu and renamed items in subdir - submenu exists sorted & all menus sorted
        # ----------------------------------------------------
        menu_layout = [
            MenuLayout.Menu(
                "Layout Test",
                [
                    MenuLayout.Item("Test Item"),
                    MenuLayout.SubMenu(
                        "Items",
                        [
                            MenuLayout.Item(
                                "Zombieland", source="SubMenu Test/Root Item/SubMenu 1/SubMenu 2/SubMenu Item 1"
                            ),
                            MenuLayout.Item(
                                "Banana", source="SubMenu Test/Root Item/SubMenu 1/SubMenu 2/SubMenu Item 2"
                            ),
                        ],
                    ),
                    MenuLayout.Menu("SubMenu Test", remove=True),
                    MenuLayout.Sort(exclude_items=[], sort_submenus=True),
                ],
            ),
        ]
        omni.kit.menu.utils.add_menu_items(items_menu_list, "Layout Test", 99)
        omni.kit.menu.utils.add_layout(menu_layout)

        try:
            # verify layout
            verify_menu_items(
                self,
                [
                    (ui.Menu, "Layout Test", True),
                    (ui.Menu, "Items", True),
                    (ui.MenuItem, "Test Item", True),
                    (ui.MenuItem, "placeholder", False),
                    (ui.MenuItem, "Abrasive", True),
                    (ui.MenuItem, "Aftermath", True),
                    (ui.MenuItem, "Banana", True),
                    (ui.MenuItem, "Berserk", True),
                    (ui.MenuItem, "Carry", True),
                    (ui.MenuItem, "Complain", True),
                    (ui.MenuItem, "Direct", True),
                    (ui.MenuItem, "Divergent", True),
                    (ui.MenuItem, "Flashy", True),
                    (ui.MenuItem, "Flawless", True),
                    (ui.MenuItem, "Fork", True),
                    (ui.MenuItem, "House", True),
                    (ui.MenuItem, "Imminent", True),
                    (ui.MenuItem, "Itch", True),
                    (ui.MenuItem, "Macabre", True),
                    (ui.MenuItem, "Mother", True),
                    (ui.MenuItem, "Parsimonious", True),
                    (ui.MenuItem, "Penitent", True),
                    (ui.MenuItem, "Perpetual", True),
                    (ui.MenuItem, "Plate", True),
                    (ui.MenuItem, "Print", True),
                    (ui.MenuItem, "Scribble", True),
                    (ui.MenuItem, "Smell", True),
                    (ui.MenuItem, "Spy", True),
                    (ui.MenuItem, "Stain", True),
                    (ui.MenuItem, "Zombieland", True),
                ],
            )
        finally:
            # remove layout
            omni.kit.menu.utils.remove_menu_items(items_menu_list, "Layout Test")
            omni.kit.menu.utils.remove_layout(menu_layout)
            self.assertTrue(omni.kit.menu.utils.get_menu_layout() == [])

        # ----------------------------------------------------
        # simple layout test with submenu and renamed items in subdir - submenu exists sorted & exclude
        # ----------------------------------------------------
        submenu_list = []
        special_words = ["Parsimonious", "Perpetual", "Mother"]
        menu_layout = [
            MenuLayout.Menu(
                "Layout Test",
                [
                    MenuLayout.Item("Test Item"),
                    MenuLayout.SubMenu(
                        "Items",
                        [
                            MenuLayout.Item(
                                "Item 1", source="SubMenu Test/Root Item/SubMenu 1/SubMenu 2/SubMenu Item 1"
                            ),
                            MenuLayout.Item(
                                "Item 2", source="SubMenu Test/Root Item/SubMenu 1/SubMenu 2/SubMenu Item 2"
                            ),
                            MenuLayout.Sort(exclude_items=special_words),
                        ],
                    ),
                    MenuLayout.Menu("SubMenu Test", remove=True),
                ],
            ),
        ]
        omni.kit.menu.utils.add_menu_items(items_menu_list, "Layout Test", 99)
        omni.kit.menu.utils.add_layout(menu_layout)
        try:
            # verify layout
            verify_menu_items(
                self,
                [
                    (ui.Menu, "Layout Test", True),
                    (ui.MenuItem, "Test Item", True),
                    (ui.Menu, "Items", True),
                    (ui.MenuItem, "placeholder", False),
                    (ui.MenuItem, "Abrasive", True),
                    (ui.MenuItem, "Aftermath", True),
                    (ui.MenuItem, "Berserk", True),
                    (ui.MenuItem, "Carry", True),
                    (ui.MenuItem, "Complain", True),
                    (ui.MenuItem, "Direct", True),
                    (ui.MenuItem, "Divergent", True),
                    (ui.MenuItem, "Flashy", True),
                    (ui.MenuItem, "Flawless", True),
                    (ui.MenuItem, "Fork", True),
                    (ui.MenuItem, "House", True),
                    (ui.MenuItem, "Imminent", True),
                    (ui.MenuItem, "Itch", True),
                    (ui.MenuItem, "Item 1", True),
                    (ui.MenuItem, "Item 2", True),
                    (ui.MenuItem, "Macabre", True),
                    (ui.MenuItem, "Penitent", True),
                    (ui.MenuItem, "Plate", True),
                    (ui.MenuItem, "Print", True),
                    (ui.MenuItem, "Scribble", True),
                    (ui.MenuItem, "Smell", True),
                    (ui.MenuItem, "Spy", True),
                    (ui.MenuItem, "Stain", True),
                    (ui.MenuItem, "Parsimonious", True),
                    (ui.MenuItem, "Perpetual", True),
                    (ui.MenuItem, "Mother", True),
                ],
            )
        finally:
            # remove layout
            omni.kit.menu.utils.remove_menu_items(items_menu_list, "Layout Test")
            omni.kit.menu.utils.remove_layout(menu_layout)
            self.assertTrue(omni.kit.menu.utils.get_menu_layout() == [])

        # ----------------------------------------------------
        # simple layout test with submenu and renamed items in subdir - submenu exists sorted & exclude & all menus sorted
        # ----------------------------------------------------
        submenu_list = []
        special_words = ["Parsimonious", "Perpetual", "Mother"]
        menu_layout = [
            MenuLayout.Menu(
                "Layout Test",
                [
                    MenuLayout.Item("Test Item"),
                    MenuLayout.SubMenu(
                        "Items",
                        [
                            MenuLayout.Item(
                                "Item 1", source="SubMenu Test/Root Item/SubMenu 1/SubMenu 2/SubMenu Item 1"
                            ),
                            MenuLayout.Item(
                                "Item 2", source="SubMenu Test/Root Item/SubMenu 1/SubMenu 2/SubMenu Item 2"
                            ),
                        ],
                    ),
                    MenuLayout.Menu("SubMenu Test", remove=True),
                    MenuLayout.Sort(exclude_items=special_words, sort_submenus=True),
                ],
            ),
        ]
        omni.kit.menu.utils.add_menu_items(items_menu_list, "Layout Test", 99)
        omni.kit.menu.utils.add_layout(menu_layout)

        try:
            # verify layout
            verify_menu_items(
                self,
                [
                    (ui.Menu, "Layout Test", True),
                    (ui.Menu, "Items", True),
                    (ui.MenuItem, "Test Item", True),
                    (ui.MenuItem, "placeholder", False),
                    (ui.MenuItem, "Abrasive", True),
                    (ui.MenuItem, "Aftermath", True),
                    (ui.MenuItem, "Berserk", True),
                    (ui.MenuItem, "Carry", True),
                    (ui.MenuItem, "Complain", True),
                    (ui.MenuItem, "Direct", True),
                    (ui.MenuItem, "Divergent", True),
                    (ui.MenuItem, "Flashy", True),
                    (ui.MenuItem, "Flawless", True),
                    (ui.MenuItem, "Fork", True),
                    (ui.MenuItem, "House", True),
                    (ui.MenuItem, "Imminent", True),
                    (ui.MenuItem, "Itch", True),
                    (ui.MenuItem, "Item 1", True),
                    (ui.MenuItem, "Item 2", True),
                    (ui.MenuItem, "Macabre", True),
                    (ui.MenuItem, "Penitent", True),
                    (ui.MenuItem, "Plate", True),
                    (ui.MenuItem, "Print", True),
                    (ui.MenuItem, "Scribble", True),
                    (ui.MenuItem, "Smell", True),
                    (ui.MenuItem, "Spy", True),
                    (ui.MenuItem, "Stain", True),
                    (ui.MenuItem, "Parsimonious", True),
                    (ui.MenuItem, "Perpetual", True),
                    (ui.MenuItem, "Mother", True),
                ],
            )
        finally:
            # remove layout
            omni.kit.menu.utils.remove_menu_items(items_menu_list, "Layout Test")
            omni.kit.menu.utils.remove_layout(menu_layout)
            self.assertTrue(omni.kit.menu.utils.get_menu_layout() == [])

        # ----------------------------------------------------
        # simple layout test with submenu and renamed items in subdir - submenu exists sorted with directories 1st
        # ----------------------------------------------------
        submenu_list = []
        special_words = ["Parsimonious", "Perpetual", "Mother"]
        for word in word_list:
            if word in special_words:
                submenu_list.append(MenuItemDescription(name=word, sub_menu=[MenuItemDescription(name="Folder")]))
            else:
                submenu_list.append(MenuItemDescription(name=word))
        items_menu_list = [MenuItemDescription(name="Items", sub_menu=submenu_list)]

        menu_layout = [
            MenuLayout.Menu(
                "Layout Test",
                [
                    MenuLayout.Item("Test Item"),
                    MenuLayout.SubMenu(
                        "Items",
                        [
                            MenuLayout.Item(
                                "Item 1", source="SubMenu Test/Root Item/SubMenu 1/SubMenu 2/SubMenu Item 1"
                            ),
                            MenuLayout.Item(
                                "Item 2", source="SubMenu Test/Root Item/SubMenu 1/SubMenu 2/SubMenu Item 2"
                            ),
                            MenuLayout.Sort(exclude_items=[]),
                        ],
                    ),
                    MenuLayout.Menu("SubMenu Test", remove=True),
                ],
            ),
        ]
        omni.kit.menu.utils.add_menu_items(items_menu_list, "Layout Test", 99)
        omni.kit.menu.utils.add_layout(menu_layout)

        try:
            # verify layout
            verify_menu_items(
                self,
                [
                    (ui.Menu, "Layout Test", True),
                    (ui.MenuItem, "Test Item", True),
                    (ui.Menu, "Items", True),
                    (ui.MenuItem, "placeholder", False),
                    (ui.MenuItem, "Abrasive", True),
                    (ui.MenuItem, "Aftermath", True),
                    (ui.MenuItem, "Berserk", True),
                    (ui.MenuItem, "Carry", True),
                    (ui.MenuItem, "Complain", True),
                    (ui.MenuItem, "Direct", True),
                    (ui.MenuItem, "Divergent", True),
                    (ui.MenuItem, "Flashy", True),
                    (ui.MenuItem, "Flawless", True),
                    (ui.MenuItem, "Fork", True),
                    (ui.MenuItem, "House", True),
                    (ui.MenuItem, "Imminent", True),
                    (ui.MenuItem, "Itch", True),
                    (ui.MenuItem, "Item 1", True),
                    (ui.MenuItem, "Item 2", True),
                    (ui.MenuItem, "Macabre", True),
                    (ui.Menu, "Mother", True),
                    (ui.Menu, "Parsimonious", True),
                    (ui.MenuItem, "Penitent", True),
                    (ui.Menu, "Perpetual", True),
                    (ui.MenuItem, "Plate", True),
                    (ui.MenuItem, "Print", True),
                    (ui.MenuItem, "Scribble", True),
                    (ui.MenuItem, "Smell", True),
                    (ui.MenuItem, "Spy", True),
                    (ui.MenuItem, "Stain", True),
                    (ui.MenuItem, "Folder", True),
                    (ui.MenuItem, "Folder", True),
                    (ui.MenuItem, "Folder", True),
                ],
            )
        finally:
            # remove layout
            omni.kit.menu.utils.remove_menu_items(items_menu_list, "Layout Test")
            omni.kit.menu.utils.remove_layout(menu_layout)
            self.assertTrue(omni.kit.menu.utils.get_menu_layout() == [])

            # remove menu
            omni.kit.menu.utils.remove_menu_items(menu_list, "SubMenu Test")
            omni.kit.menu.utils.remove_menu_items(menu_placeholder, "Layout Test")
            self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

    async def test_submenu_layout(self):
        menu_rendering = [MenuItemDescription(name="Render Settings"), MenuItemDescription(name="Movie Capture")]
        blast_menu2 = [
            MenuItemDescription(name="Kit UI"),
            MenuItemDescription(name="Programming"),
            MenuItemDescription(name="USD Schemas"),
        ]
        blast_menu1 = [
            MenuItemDescription(name="Settings"),
            MenuItemDescription(name="Documentation", sub_menu=blast_menu2),
        ]
        menu_window = [
            MenuItemDescription(name="MDL Material Graph"),
            MenuItemDescription(name="Blast", sub_menu=blast_menu1),
        ]

        # add menu
        omni.kit.menu.utils.add_menu_items(menu_rendering, "Rendering", 190)
        omni.kit.menu.utils.add_menu_items(menu_window, "Window", 99)
        await ui_test.human_delay()

        # ----------------------------------------------------
        # simple layout test
        # ----------------------------------------------------
        menu_layout = [
            MenuLayout.Menu(
                "Window",
                [
                    MenuLayout.SubMenu(
                        "Rendering",
                        [
                            MenuLayout.Item("Render Settings"),
                            MenuLayout.Item("Movie Capture"),
                            MenuLayout.Item("MDL Material Graph"),
                        ],
                    ),
                    MenuLayout.SubMenu(
                        "Simulation",
                        [
                            MenuLayout.Group(
                                "Blast",
                                [
                                    MenuLayout.Item("Settings", source="Window/Blast/Settings"),
                                    MenuLayout.SubMenu(
                                        "Documentation",
                                        [
                                            MenuLayout.Item("Kit UI", source="Window/Blast/Documentation/Kit UI"),
                                            MenuLayout.Item(
                                                "Programming", source="Window/Blast/Documentation/Programming"
                                            ),
                                            MenuLayout.Item(
                                                "USD Schemas", source="Window/Blast/Documentation/USD Schemas"
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ]
        omni.kit.menu.utils.add_layout(menu_layout)

        try:
            # verify layout
            verify_menu_items(
                self,
                [
                    (ui.Menu, "Window", True),
                    (ui.Menu, "Rendering", False),
                    (ui.Menu, "Rendering", True),
                    (ui.Menu, "Simulation", True),
                    (ui.Menu, "Blast", False),
                    (ui.MenuItem, "Render Settings", True),
                    (ui.MenuItem, "Movie Capture", True),
                    (ui.MenuItem, "MDL Material Graph", True),
                    (ui.Menu, "Documentation", True),
                    (ui.Separator, "Blast", True),
                    (ui.MenuItem, "Settings", True),
                    (ui.MenuItem, "Kit UI", True),
                    (ui.MenuItem, "Programming", True),
                    (ui.MenuItem, "USD Schemas", True),
                    (ui.Menu, "Documentation", False),
                ],
            )
        finally:
            # remove layout
            omni.kit.menu.utils.remove_layout(menu_layout)
            self.assertTrue(omni.kit.menu.utils.get_menu_layout() == [])

            # remove menu
            omni.kit.menu.utils.remove_menu_items(menu_window, "Window")
            omni.kit.menu.utils.remove_menu_items(menu_rendering, "Rendering")
            self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

    async def test_submenu_layout_oldreference(self):
        menu_rendering = [MenuItemDescription(name="Render Settings"), MenuItemDescription(name="Movie Capture")]
        menu_window1 = [
            MenuItemDescription(name="MDL Material Graph"),
            MenuItemDescription(name="Blast", sub_menu=[MenuItemDescription(name="Settings")]),
        ]
        menu_window2 = [
            MenuItemDescription(
                name="Blast",
                sub_menu=[MenuItemDescription(name="Documentation", sub_menu=[MenuItemDescription(name="Kit UI")])],
            )
        ]
        menu_window3 = [
            MenuItemDescription(
                name="Blast",
                sub_menu=[
                    MenuItemDescription(name="Documentation", sub_menu=[MenuItemDescription(name="Programming")])
                ],
            )
        ]
        menu_window4 = [
            MenuItemDescription(
                name="Blast",
                sub_menu=[
                    MenuItemDescription(name="Documentation", sub_menu=[MenuItemDescription(name="USD Schemas")])
                ],
            )
        ]

        # add menu
        omni.kit.menu.utils.add_menu_items(menu_rendering, "Rendering", 190)
        omni.kit.menu.utils.add_menu_items(menu_window1, "Window", 99)
        omni.kit.menu.utils.add_menu_items(menu_window2, "Window")
        omni.kit.menu.utils.add_menu_items(menu_window3, "Window")
        omni.kit.menu.utils.add_menu_items(menu_window4, "Window")
        await ui_test.human_delay()

        # ----------------------------------------------------
        # simple layout test
        # ----------------------------------------------------
        menu_layout = [
            MenuLayout.Menu(
                "Window",
                [
                    MenuLayout.SubMenu(
                        "Rendering",
                        [
                            MenuLayout.Item("Render Settings"),
                            MenuLayout.Item("Movie Capture"),
                            MenuLayout.Item("MDL Material Graph"),
                        ],
                    ),
                    MenuLayout.SubMenu(
                        "Simulation",
                        [
                            MenuLayout.Group(
                                "Blast",
                                [
                                    MenuLayout.Item("Settings", source="Window/Blast/Settings"),
                                    MenuLayout.SubMenu(
                                        "Documentation",
                                        [
                                            MenuLayout.Item("Kit UI", source="Window/Blast/Documentation/Kit UI"),
                                            MenuLayout.Item(
                                                "Programming", source="Window/Blast/Documentation/Programming"
                                            ),
                                            MenuLayout.Item(
                                                "USD Schemas", source="Window/Blast/Documentation/USD Schemas"
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ]
        omni.kit.menu.utils.add_layout(menu_layout)

        try:
            # verify layout
            verify_menu_items(
                self,
                [
                    (ui.Menu, "Window", True),
                    (ui.Menu, "Rendering", False),
                    (ui.Menu, "Rendering", True),
                    (ui.Menu, "Simulation", True),
                    (ui.Menu, "Blast", False),
                    (ui.MenuItem, "Render Settings", True),
                    (ui.MenuItem, "Movie Capture", True),
                    (ui.MenuItem, "MDL Material Graph", True),
                    (ui.Menu, "Documentation", True),
                    (ui.Separator, "Blast", True),
                    (ui.MenuItem, "Settings", True),
                    (ui.MenuItem, "Kit UI", True),
                    (ui.MenuItem, "Programming", True),
                    (ui.MenuItem, "USD Schemas", True),
                    (ui.Menu, "Documentation", False),
                ],
            )
        finally:
            # remove menu
            omni.kit.menu.utils.remove_menu_items(menu_window4, "Window")
            omni.kit.menu.utils.remove_menu_items(menu_window3, "Window")
            omni.kit.menu.utils.remove_menu_items(menu_window2, "Window")

        try:
            # verify layout
            verify_menu_items(
                self,
                [
                    (ui.Menu, "Window", True),
                    (ui.Menu, "Rendering", False),
                    (ui.Menu, "Rendering", True),
                    (ui.Menu, "Simulation", True),
                    (ui.Menu, "Blast", False),
                    (ui.MenuItem, "Render Settings", True),
                    (ui.MenuItem, "Movie Capture", True),
                    (ui.MenuItem, "MDL Material Graph", True),
                    (ui.Separator, "Blast", True),
                    (ui.MenuItem, "Settings", True),
                    (ui.Menu, "Documentation", False),
                ],
            )
        finally:
            omni.kit.menu.utils.remove_menu_items(menu_window1, "Window")
            omni.kit.menu.utils.remove_menu_items(menu_rendering, "Rendering")
            self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

            # remove layout
            omni.kit.menu.utils.remove_layout(menu_layout)
            self.assertTrue(omni.kit.menu.utils.get_menu_layout() == [])

    async def test_submenu_layout_oldreference_source(self):
        menu_rendering = [MenuItemDescription(name="Render Settings"), MenuItemDescription(name="Movie Capture")]
        menu_window1 = [
            MenuItemDescription(name="MDL Material Graph"),
            MenuItemDescription(name="Blast", sub_menu=[MenuItemDescription(name="Settings")]),
        ]
        menu_window2 = [
            MenuItemDescription(
                name="Blast",
                sub_menu=[MenuItemDescription(name="Documentation", sub_menu=[MenuItemDescription(name="Kit UI")])],
            )
        ]
        menu_window3 = [
            MenuItemDescription(
                name="Blast",
                sub_menu=[
                    MenuItemDescription(name="Documentation", sub_menu=[MenuItemDescription(name="Programming")])
                ],
            )
        ]
        menu_window4 = [
            MenuItemDescription(
                name="Blast",
                sub_menu=[
                    MenuItemDescription(name="Documentation", sub_menu=[MenuItemDescription(name="USD Schemas")])
                ],
            )
        ]

        # add menu
        omni.kit.menu.utils.add_menu_items(menu_rendering, "Rendering", 190)
        omni.kit.menu.utils.add_menu_items(menu_window1, "Window", 99)
        omni.kit.menu.utils.add_menu_items(menu_window2, "Window")
        omni.kit.menu.utils.add_menu_items(menu_window3, "Window")
        omni.kit.menu.utils.add_menu_items(menu_window4, "Window")
        await ui_test.human_delay()

        # ----------------------------------------------------
        # simple layout test
        # ----------------------------------------------------
        menu_layout = [
            MenuLayout.Menu(
                "Window",
                [
                    MenuLayout.SubMenu(
                        "Rendering",
                        [
                            MenuLayout.Item("Render Settings"),
                            MenuLayout.Item("Movie Capture"),
                            MenuLayout.Item("MDL Material Graph"),
                        ],
                    ),
                    MenuLayout.SubMenu("Simulation", [MenuLayout.Group("Blast", source="Window/Blast")]),
                ],
            ),
        ]
        omni.kit.menu.utils.add_layout(menu_layout)

        try:
            # verify layout
            verify_menu_items(
                self,
                [
                    (ui.Menu, "Window", True),
                    (ui.Menu, "Rendering", False),
                    (ui.Menu, "Rendering", True),
                    (ui.Menu, "Simulation", True),
                    (ui.MenuItem, "Render Settings", True),
                    (ui.MenuItem, "Movie Capture", True),
                    (ui.MenuItem, "MDL Material Graph", True),
                    (ui.Separator, "Blast", True),
                    (ui.MenuItem, "Settings", True),
                    (ui.Menu, "Documentation", True),
                    (ui.MenuItem, "Kit UI", True),
                    (ui.MenuItem, "Programming", True),
                    (ui.MenuItem, "USD Schemas", True),
                ],
            )
        finally:
            # remove menu
            omni.kit.menu.utils.remove_menu_items(menu_window4, "Window")
            omni.kit.menu.utils.remove_menu_items(menu_window3, "Window")
            omni.kit.menu.utils.remove_menu_items(menu_window2, "Window")

        try:
            # verify layout
            verify_menu_items(
                self,
                [
                    (ui.Menu, "Window", True),
                    (ui.Menu, "Rendering", False),
                    (ui.Menu, "Rendering", True),
                    (ui.Menu, "Simulation", True),
                    (ui.MenuItem, "Render Settings", True),
                    (ui.MenuItem, "Movie Capture", True),
                    (ui.MenuItem, "MDL Material Graph", True),
                    (ui.Separator, "Blast", True),
                    (ui.MenuItem, "Settings", True),
                ],
            )
        finally:
            omni.kit.menu.utils.remove_menu_items(menu_window1, "Window")
            omni.kit.menu.utils.remove_menu_items(menu_rendering, "Rendering")
            self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

            # remove layout
            omni.kit.menu.utils.remove_layout(menu_layout)
            self.assertTrue(omni.kit.menu.utils.get_menu_layout() == [])

    async def test_menus_buildsm_1(self):
        # test build_submenu_dict
        menu_dict = omni.kit.menu.utils.build_submenu_dict(
            [
                MenuItemDescription(name="Test/Root Item/SubMenu 1/SubMenu 2/SubMenu Item 1"),
                MenuItemDescription(name="Test/Root Item/SubMenu 1/SubMenu 2/SubMenu Item 2"),
                MenuItemDescription(name="Test/Root Item/SubMenu 1/SubMenu Item 3"),
                MenuItemDescription(name="Test/Root Item/Item 4"),
            ]
        )

        # add menu
        for group in menu_dict:
            omni.kit.menu.utils.add_menu_items(menu_dict[group], group)
            verify_menu_items(
                self,
                [
                    (ui.Menu, "Test", True),
                    (ui.Menu, "Root Item", True),
                    (ui.MenuItem, "Item 4", True),
                    (ui.Menu, "SubMenu 1", True),
                    (ui.MenuItem, "SubMenu Item 3", True),
                    (ui.Menu, "SubMenu 2", True),
                    (ui.MenuItem, "SubMenu Item 1", True),
                    (ui.MenuItem, "SubMenu Item 2", True),
                ],
            )

        for group in menu_dict:
            omni.kit.menu.utils.remove_menu_items(menu_dict[group], group)

        # verify menus are removed
        self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

    async def test_menus_buildsm_2(self):
        # test build_submenu_dict
        menu_dict = omni.kit.menu.utils.build_submenu_dict(
            [
                MenuItemDescription(name="Test1/Root Item/SubMenu 1/SubMenu 2/SubMenu Item 1"),
                MenuItemDescription(name="Test2/Root Item/SubMenu 1/SubMenu 2/SubMenu Item 2"),
                MenuItemDescription(name="Test1/Root Item/SubMenu 1/SubMenu Item 3"),
                MenuItemDescription(name="Test2/Root Item/Item 4"),
            ]
        )
        self.assertEqual(
            str(menu_dict),
            "{'Test1': [<MenuItemDescription name:'Root Item' sub_menu:[<MenuItemDescription name:'SubMenu 1' sub_menu:[<MenuItemDescription name:'SubMenu Item 3'>]>, <MenuItemDescription name:'SubMenu 1' sub_menu:[<MenuItemDescription name:'SubMenu 2' sub_menu:[<MenuItemDescription name:'SubMenu Item 1'>]>, <MenuItemDescription name:'SubMenu 2'>]>]>], 'Test2': [<MenuItemDescription name:'Root Item' sub_menu:[<MenuItemDescription name:'Item 4'>]>, <MenuItemDescription name:'Root Item' sub_menu:[<MenuItemDescription name:'SubMenu 1' sub_menu:[<MenuItemDescription name:'SubMenu 2' sub_menu:[<MenuItemDescription name:'SubMenu Item 2'>]>, <MenuItemDescription name:'SubMenu 2'>]>]>]}",
        )

        # add menu
        for group in menu_dict:
            omni.kit.menu.utils.add_menu_items(menu_dict[group], group)

        # verify
        try:
            verify_menu_items(
                self,
                [
                    (ui.Menu, "Test1", True),
                    (ui.Menu, "Test2", True),
                    (ui.Menu, "Root Item", True),
                    (ui.Menu, "SubMenu 1", True),
                    (ui.MenuItem, "SubMenu Item 3", True),
                    (ui.Menu, "SubMenu 2", True),
                    (ui.MenuItem, "SubMenu Item 1", True),
                    (ui.Menu, "Root Item", True),
                    (ui.MenuItem, "Item 4", True),
                    (ui.Menu, "SubMenu 1", True),
                    (ui.Menu, "SubMenu 2", True),
                    (ui.MenuItem, "SubMenu Item 2", True),
                ],
            )
        finally:
            for group in menu_dict:
                omni.kit.menu.utils.remove_menu_items(menu_dict[group], group)

        # verify menus are removed
        self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})
