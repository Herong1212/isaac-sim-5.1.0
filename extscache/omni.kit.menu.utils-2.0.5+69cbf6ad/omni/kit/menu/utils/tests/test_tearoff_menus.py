import omni.kit.test
from omni.kit import ui_test
from omni.kit.menu.utils import MenuItemDescription, MenuLayout
from omni.ui.tests.test_base import OmniUiTest

from .utils import refresh_menus


class TestTearOff(OmniUiTest):
    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def test_tearoff(self):
        menu_ticked = False

        def show_tick():
            nonlocal menu_ticked
            return menu_ticked

        submenu_list = [MenuItemDescription(name="Menu Item", ticked_fn=show_tick)]
        menu_list = [MenuItemDescription(name="Tear-off Menu Test", sub_menu=submenu_list)]
        omni.kit.menu.utils.add_menu_items(menu_list, "Tear-off-Test", 99)
        omni.kit.menu.utils.rebuild_menus()
        await ui_test.human_delay(50)

        # menu widgets
        menu_widget = None
        menu_item_widget = None
        for w in ui_test.get_menubar().find_all("**/"):
            if isinstance(w.widget, omni.kit.menu.core.uiMenu) and w.widget.text == "Tear-off Menu Test":
                menu_widget = w
            if isinstance(w.widget, omni.kit.menu.core.uiMenuItem) and w.widget.text == "Menu Item":
                menu_item_widget = w

        self.assertTrue(menu_widget)
        self.assertTrue(menu_item_widget)

        try:
            # tear off menu
            menu_widget.widget.tear_at(100, 200)

            # verify initial state
            await ui_test.human_delay(10)
            self.assertEqual(menu_item_widget.widget.checked, False)

            # verify new state
            menu_ticked = True
            # open menu as items are not refreshed on refresh_menu_items
            await refresh_menus("Tear-off-Test")

            self.assertEqual(menu_item_widget.widget.checked, True)
        finally:
            omni.kit.menu.utils.remove_menu_items(menu_list, "Tear-off-Test", 99)

        # verify menus removed
        self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

    async def test_tearoff_submenu(self):
        menu_placeholder = [MenuItemDescription(name="placeholder", show_fn=lambda: False)]

        example_window_is_ticked = False

        def get_example_window_is_ticked():
            nonlocal example_window_is_ticked
            return example_window_is_ticked

        def toggle_example_window_is_ticked():  # pragma: no cover
            pass

        menu_entry1 = [
            MenuItemDescription(
                name="Example Window",
                ticked=True,
                ticked_fn=get_example_window_is_ticked,
                onclick_fn=toggle_example_window_is_ticked,
            )
        ]
        menu_entry2 = [
            MenuItemDescription(
                name="Best Window Ever",
                ticked=True,
                ticked_fn=get_example_window_is_ticked,
                onclick_fn=toggle_example_window_is_ticked,
            )
        ]

        # add menu
        omni.kit.menu.utils.add_menu_items(menu_placeholder, "Developer")
        omni.kit.menu.utils.add_menu_items(menu_entry1, "Window")
        omni.kit.menu.utils.add_menu_items(menu_entry2, "Window")
        await ui_test.human_delay()

        # more the "Example Window" and "Best Window Ever" to different menus
        menu_layout = [
            MenuLayout.Menu(
                "Developer",
                [
                    MenuLayout.SubMenu(
                        "Utilities",
                        [
                            MenuLayout.Item("Stage Window", source="Window/Example Window"),
                            MenuLayout.Item("Another Stage Window", source="Window/Best Window Ever"),
                        ],
                    ),
                ],
            ),
        ]
        omni.kit.menu.utils.add_layout(menu_layout)
        await ui_test.human_delay(10)

        # get menu widgets
        # keep references to menu items for when tear-off is done as interacting with the menu directly would force a refresh and invalidate the test.
        menu_widget = None
        menu_item_widget = {}
        for w in ui_test.get_menubar().find_all("**/"):
            if isinstance(w.widget, omni.kit.menu.core.uiMenu) and w.widget.text == "Utilities":
                menu_widget = w
            if isinstance(w.widget, omni.kit.menu.core.uiMenuItem):
                menu_item_widget[w.widget.text] = w.widget

        self.assertTrue(menu_widget)
        self.assertTrue(menu_item_widget)

        # tear off menu
        menu_widget.widget.tear_at(100, 200)

        try:
            # update checked status (checked) - refreshing window should refresh "Developer/Utilities"
            example_window_is_ticked = True
            # open menu as items are not refreshed on refresh_menu_items
            await refresh_menus("Window", "Developer")

            # verify ticks are on
            self.assertTrue(menu_item_widget["Stage Window"].checked)
            self.assertTrue(menu_item_widget["Another Stage Window"].checked)

            # update checked status (unchecked) - refreshing window should refresh "Developer/Utilities"
            example_window_is_ticked = False
            # open menu as items are not refreshed on refresh_menu_items
            await refresh_menus("Window", "Developer")

            # verify ticks are off
            self.assertFalse(menu_item_widget["Stage Window"].checked)
            self.assertFalse(menu_item_widget["Another Stage Window"].checked)
        finally:
            # remove layout
            omni.kit.menu.utils.remove_layout(menu_layout)
            self.assertTrue(omni.kit.menu.utils.get_menu_layout() == [])

            # remove menu
            omni.kit.menu.utils.remove_menu_items(menu_entry2, "Window")
            omni.kit.menu.utils.remove_menu_items(menu_entry1, "Window")
            omni.kit.menu.utils.remove_menu_items(menu_placeholder, "Developer")
            self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})
