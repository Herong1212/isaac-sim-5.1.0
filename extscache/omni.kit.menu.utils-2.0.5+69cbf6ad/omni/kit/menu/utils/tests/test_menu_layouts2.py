# pylint: disable=too-many-lines
import omni.kit.test
import omni.ui as ui
from omni.kit import ui_test
from omni.kit.menu.utils import MenuItemDescription, MenuLayout

from .utils import refresh_menus, verify_menu_items


class TestMenuLayoutUtils2(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def test_submenu_layout_item_move_and_refresh(self):
        show_state = True

        def get_menu_test_state():
            nonlocal show_state
            return show_state

        menu_window1 = [
            MenuItemDescription(name="Blast", sub_menu=[MenuItemDescription(name="Settings")]),
        ]
        menu_window2 = [
            MenuItemDescription(
                name="Blast",
                sub_menu=[
                    MenuItemDescription(
                        name="Documentation",
                        sub_menu=[
                            MenuItemDescription(
                                name="Things",
                                sub_menu=[MenuItemDescription(name="Kit UI", show_fn=get_menu_test_state)],
                            )
                        ],
                    )
                ],
            )
        ]

        menu_window3 = [
            MenuItemDescription(
                name="Blast",
                sub_menu=[
                    MenuItemDescription(
                        name="Documentation",
                        sub_menu=[MenuItemDescription(name="Programming", show_fn=get_menu_test_state)],
                    )
                ],
            )
        ]
        menu_window4 = [
            MenuItemDescription(
                name="Blast",
                sub_menu=[
                    MenuItemDescription(
                        name="Documentation",
                        sub_menu=[MenuItemDescription(name="USD Schemas", show_fn=get_menu_test_state)],
                    )
                ],
            )
        ]

        # add menu
        omni.kit.menu.utils.add_menu_items(menu_window1, "Window", 99)
        omni.kit.menu.utils.add_menu_items(menu_window2, "Window")
        omni.kit.menu.utils.add_menu_items(menu_window3, "Window")
        omni.kit.menu.utils.add_menu_items(menu_window4, "Window")
        await ui_test.human_delay()

        menu_placeholder = [MenuItemDescription(name="placeholder", show_fn=lambda: False)]
        omni.kit.menu.utils.add_menu_items(menu_placeholder, "TestTest")

        # ----------------------------------------------------
        # simple layout test
        # ----------------------------------------------------
        menu_layout = [
            MenuLayout.Menu(
                "TestTest",
                [
                    MenuLayout.Item("Move1", source="Window/Blast/Documentation"),
                    MenuLayout.Item("Move2", source="Window/Blast"),
                ],
            ),
        ]
        omni.kit.menu.utils.add_layout(menu_layout)

        try:
            # verify layout
            verify_menu_items(
                self,
                [
                    (ui.Menu, "TestTest", True),
                    (ui.Menu, "Window", False),
                    (ui.Menu, "Move1", True),
                    (ui.Menu, "Move2", True),
                    (ui.MenuItem, "placeholder", False),
                    (ui.Menu, "Things", True),
                    (ui.MenuItem, "Programming", True),
                    (ui.MenuItem, "USD Schemas", True),
                    (ui.MenuItem, "Kit UI", True),
                    (ui.Menu, "Documentation", False),
                    (ui.MenuItem, "Settings", True),
                    (ui.Menu, "Blast", False),
                    (ui.Menu, "Documentation", False),
                    (ui.Menu, "Things", False),
                ],
            )

            show_state = False
            # open menu as items are not refreshed on refresh_menu_items
            await refresh_menus("TestTest")
            await ui_test.human_delay()

            # verify layout
            verify_menu_items(
                self,
                [
                    (ui.Menu, "TestTest", True),
                    (ui.Menu, "Window", False),
                    (ui.Menu, "Move1", False),
                    (ui.Menu, "Move2", True),
                    (ui.MenuItem, "placeholder", False),
                    (ui.Menu, "Things", False),
                    (ui.MenuItem, "Programming", False),
                    (ui.MenuItem, "USD Schemas", False),
                    (ui.MenuItem, "Kit UI", False),
                    (ui.Menu, "Documentation", False),
                    (ui.MenuItem, "Settings", True),
                    (ui.Menu, "Blast", False),
                    (ui.Menu, "Documentation", False),
                    (ui.Menu, "Things", False),
                ],
            )
        finally:
            # remove layout
            omni.kit.menu.utils.remove_layout(menu_layout)
            self.assertTrue(omni.kit.menu.utils.get_menu_layout() == [])

            # remove menu
            omni.kit.menu.utils.remove_menu_items(menu_window4, "Window")
            omni.kit.menu.utils.remove_menu_items(menu_window3, "Window")
            omni.kit.menu.utils.remove_menu_items(menu_window2, "Window")
            omni.kit.menu.utils.remove_menu_items(menu_window1, "Window")
            omni.kit.menu.utils.remove_menu_items(menu_placeholder, "TestTest")
            self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

    async def test_submenu_layout_item_duplicate(self):
        show_state = True

        def get_menu_test_state():
            nonlocal show_state
            return show_state

        menu_window1 = [
            MenuItemDescription(name="Blast", sub_menu=[MenuItemDescription(name="Settings")]),
        ]
        menu_window2 = [
            MenuItemDescription(
                name="Blast",
                sub_menu=[
                    MenuItemDescription(
                        name="Documentation",
                        sub_menu=[
                            MenuItemDescription(
                                name="Things",
                                sub_menu=[MenuItemDescription(name="Kit UI", show_fn=get_menu_test_state)],
                            )
                        ],
                    )
                ],
            )
        ]

        menu_window3 = [
            MenuItemDescription(
                name="Blast",
                sub_menu=[
                    MenuItemDescription(
                        name="Documentation",
                        sub_menu=[MenuItemDescription(name="Programming", show_fn=get_menu_test_state)],
                    )
                ],
            )
        ]
        menu_window4 = [
            MenuItemDescription(
                name="Blast",
                sub_menu=[
                    MenuItemDescription(
                        name="Documentation",
                        sub_menu=[MenuItemDescription(name="USD Schemas", show_fn=get_menu_test_state)],
                    )
                ],
            )
        ]

        # add menu
        omni.kit.menu.utils.add_menu_items(menu_window1, "Window", 99)
        omni.kit.menu.utils.add_menu_items(menu_window2, "Window")
        omni.kit.menu.utils.add_menu_items(menu_window3, "Window")
        omni.kit.menu.utils.add_menu_items(menu_window4, "Window")
        await ui_test.human_delay()

        menu_placeholder = [MenuItemDescription(name="placeholder", show_fn=lambda: False)]
        omni.kit.menu.utils.add_menu_items(menu_placeholder, "One")
        omni.kit.menu.utils.add_menu_items(menu_placeholder, "Two")

        # ----------------------------------------------------
        # simple layout test
        # ----------------------------------------------------
        menu_layout = [
            MenuLayout.Menu(
                "One",
                [
                    MenuLayout.Item("Move1", source="Window/Blast/Documentation"),
                    MenuLayout.Item("Move2", source="Window/Blast"),
                ],
            ),
            MenuLayout.Menu(
                "Two",
                [
                    MenuLayout.Item("Move2", source="Window/Blast", duplicate=True),
                    MenuLayout.Item("Duplicate 1", source="Window/Blast/Documentation", duplicate=True),
                    MenuLayout.Item("Duplicate 2", source="Window/Blast/Documentation", duplicate=True),
                    MenuLayout.Item("Duplicate 3", source="Window/Blast/Documentation", duplicate=True),
                    MenuLayout.Item("Duplicate 4", source="Window/Blast/Documentation", duplicate=True),
                ],
            ),
        ]
        omni.kit.menu.utils.add_layout(menu_layout)

        try:
            # verify layout
            verify_menu_items(
                self,
                [
                    (ui.Menu, "One", True),
                    (ui.Menu, "Two", True),
                    (ui.Menu, "Window", False),
                    (ui.Menu, "Move1", True),
                    (ui.Menu, "Move2", True),
                    (ui.MenuItem, "placeholder", False),
                    (ui.Menu, "Things", True),
                    (ui.MenuItem, "Programming", True),
                    (ui.MenuItem, "USD Schemas", True),
                    (ui.MenuItem, "Kit UI", True),
                    (ui.Menu, "Documentation", False),
                    (ui.MenuItem, "Settings", True),
                    (ui.Menu, "Duplicate 1", True),
                    (ui.Menu, "Duplicate 2", True),
                    (ui.Menu, "Duplicate 3", True),
                    (ui.Menu, "Duplicate 4", True),
                    (ui.MenuItem, "placeholder", False),
                    (ui.Menu, "Move2", False),
                    (ui.MenuItem, "Programming", True),
                    (ui.MenuItem, "USD Schemas", True),
                    (ui.Menu, "Things", True),
                    (ui.MenuItem, "Kit UI", True),
                    (ui.MenuItem, "Programming", True),
                    (ui.MenuItem, "USD Schemas", True),
                    (ui.Menu, "Things", True),
                    (ui.MenuItem, "Kit UI", True),
                    (ui.MenuItem, "Programming", True),
                    (ui.MenuItem, "USD Schemas", True),
                    (ui.Menu, "Things", True),
                    (ui.MenuItem, "Kit UI", True),
                    (ui.MenuItem, "Programming", True),
                    (ui.MenuItem, "USD Schemas", True),
                    (ui.Menu, "Things", True),
                    (ui.MenuItem, "Kit UI", True),
                    (ui.Menu, "Blast", False),
                    (ui.Menu, "Documentation", False),
                    (ui.Menu, "Things", False),
                ],
            )

            show_state = False
            # open menu as items are not refreshed on refresh_menu_items
            await refresh_menus("Window", "One")
            await refresh_menus("Window", "Two")
            await ui_test.human_delay()

            # verify layout
            verify_menu_items(
                self,
                [
                    (ui.Menu, "One", True),
                    (ui.Menu, "Two", True),
                    (ui.Menu, "Window", False),
                    (ui.Menu, "Move1", False),
                    (ui.Menu, "Move2", True),
                    (ui.MenuItem, "placeholder", False),
                    (ui.Menu, "Things", False),
                    (ui.MenuItem, "Programming", False),
                    (ui.MenuItem, "USD Schemas", False),
                    (ui.MenuItem, "Kit UI", False),
                    (ui.Menu, "Documentation", False),
                    (ui.MenuItem, "Settings", True),
                    (ui.Menu, "Duplicate 1", False),
                    (ui.Menu, "Duplicate 2", False),
                    (ui.Menu, "Duplicate 3", False),
                    (ui.Menu, "Duplicate 4", False),
                    (ui.MenuItem, "placeholder", False),
                    (ui.Menu, "Move2", False),
                    (ui.MenuItem, "Programming", False),
                    (ui.MenuItem, "USD Schemas", False),
                    (ui.Menu, "Things", False),
                    (ui.MenuItem, "Kit UI", False),
                    (ui.MenuItem, "Programming", False),
                    (ui.MenuItem, "USD Schemas", False),
                    (ui.Menu, "Things", False),
                    (ui.MenuItem, "Kit UI", False),
                    (ui.MenuItem, "Programming", False),
                    (ui.MenuItem, "USD Schemas", False),
                    (ui.Menu, "Things", False),
                    (ui.MenuItem, "Kit UI", False),
                    (ui.MenuItem, "Programming", False),
                    (ui.MenuItem, "USD Schemas", False),
                    (ui.Menu, "Things", False),
                    (ui.MenuItem, "Kit UI", False),
                    (ui.Menu, "Blast", False),
                    (ui.Menu, "Documentation", False),
                    (ui.Menu, "Things", False),
                ],
            )
        finally:
            # remove layout
            omni.kit.menu.utils.remove_layout(menu_layout)
            self.assertTrue(omni.kit.menu.utils.get_menu_layout() == [])

            # remove menu
            omni.kit.menu.utils.remove_menu_items(menu_window4, "Window")
            omni.kit.menu.utils.remove_menu_items(menu_window3, "Window")
            omni.kit.menu.utils.remove_menu_items(menu_window2, "Window")
            omni.kit.menu.utils.remove_menu_items(menu_window1, "Window")
            omni.kit.menu.utils.remove_menu_items(menu_placeholder, "One")
            omni.kit.menu.utils.remove_menu_items(menu_placeholder, "Two")
            self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

    async def test_submenu_layout_item_move_with_seperator(self):
        show_state = True

        def get_menu_test_state():
            nonlocal show_state
            return show_state

        menu_window1 = [
            MenuItemDescription(name="Blast", sub_menu=[MenuItemDescription(name="Settings")]),
        ]
        menu_window2 = [
            MenuItemDescription(
                name="Blast",
                sub_menu=[
                    MenuItemDescription(
                        name="Documentation",
                        sub_menu=[
                            MenuItemDescription(
                                name="Things",
                                sub_menu=[MenuItemDescription(name="Kit UI", show_fn=get_menu_test_state)],
                            )
                        ],
                    )
                ],
            )
        ]

        menu_window3 = [
            MenuItemDescription(
                name="Blast",
                sub_menu=[
                    MenuItemDescription(name="", header="Hot Docs 1"),
                    MenuItemDescription(
                        name="Documentation",
                        sub_menu=[MenuItemDescription(name="Programming", show_fn=get_menu_test_state)],
                    ),
                    MenuItemDescription(name="", header="Hot Docs 2"),
                ],
            )
        ]
        menu_window4 = [
            MenuItemDescription(
                name="Blast",
                sub_menu=[
                    MenuItemDescription(name="", header="Hot Docs 3"),
                    MenuItemDescription(
                        name="Documentation",
                        sub_menu=[MenuItemDescription(name="USD Schemas", show_fn=get_menu_test_state)],
                    ),
                    MenuItemDescription(name="", header="Hot Docs 4"),
                ],
            )
        ]

        # add menu
        omni.kit.menu.utils.add_menu_items(menu_window1, "Window", 99)
        omni.kit.menu.utils.add_menu_items(menu_window2, "Window")
        omni.kit.menu.utils.add_menu_items(menu_window3, "Window")
        omni.kit.menu.utils.add_menu_items(menu_window4, "Window")
        await ui_test.human_delay()

        menu_placeholder = [MenuItemDescription(name="placeholder", show_fn=lambda: False)]
        omni.kit.menu.utils.add_menu_items(menu_placeholder, "TestTest")

        # ----------------------------------------------------
        # simple layout test
        # ----------------------------------------------------
        menu_layout = [
            MenuLayout.Menu(
                "TestTest",
                [
                    MenuLayout.SubMenu(
                        "Blast Assets",
                        [
                            MenuLayout.Item("Move1", source="Window/Blast/Documentation"),
                            MenuLayout.Item("Move2", source="Window/Blast"),
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
                    (ui.Menu, "TestTest", True),
                    (ui.Menu, "Window", True),
                    (ui.Menu, "Blast Assets", True),
                    (ui.MenuItem, "placeholder", False),
                    (ui.Menu, "Move1", True),
                    (ui.Menu, "Move2", True),
                    (ui.Menu, "Things", True),
                    (ui.MenuItem, "Programming", True),
                    (ui.MenuItem, "USD Schemas", True),
                    (ui.MenuItem, "Kit UI", True),
                    (ui.Menu, "Documentation", False),
                    (ui.MenuItem, "Settings", True),
                    (ui.Separator, "Hot Docs 4", False),
                    (ui.Menu, "Blast", False),
                    (ui.Menu, "Documentation", False),
                    (ui.Separator, "Hot Docs 4", False),
                    (ui.Menu, "Things", False),
                ],
            )

            show_state = False
            # open menu as items are not refreshed on refresh_menu_items
            await refresh_menus("Window")
            await ui_test.human_delay()

            # verify layout
            verify_menu_items(
                self,
                [
                    (ui.Menu, "TestTest", True),
                    (ui.Menu, "Window", True),
                    (ui.Menu, "Blast Assets", True),
                    (ui.MenuItem, "placeholder", False),
                    (ui.Menu, "Move1", False),
                    (ui.Menu, "Move2", True),
                    (ui.Menu, "Things", False),
                    (ui.MenuItem, "Programming", False),
                    (ui.MenuItem, "USD Schemas", False),
                    (ui.MenuItem, "Kit UI", False),
                    (ui.Menu, "Documentation", False),
                    (ui.MenuItem, "Settings", True),
                    (ui.Separator, "Hot Docs 4", False),
                    (ui.Menu, "Blast", False),
                    (ui.Menu, "Documentation", False),
                    (ui.Separator, "Hot Docs 4", False),
                    (ui.Menu, "Things", False),
                ],
            )
        finally:
            # remove layout
            omni.kit.menu.utils.remove_layout(menu_layout)
            self.assertTrue(omni.kit.menu.utils.get_menu_layout() == [])

            # remove menu
            omni.kit.menu.utils.remove_menu_items(menu_window4, "Window")
            omni.kit.menu.utils.remove_menu_items(menu_window3, "Window")
            omni.kit.menu.utils.remove_menu_items(menu_window2, "Window")
            omni.kit.menu.utils.remove_menu_items(menu_window1, "Window")
            omni.kit.menu.utils.remove_menu_items(menu_placeholder, "TestTest")
            self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})
