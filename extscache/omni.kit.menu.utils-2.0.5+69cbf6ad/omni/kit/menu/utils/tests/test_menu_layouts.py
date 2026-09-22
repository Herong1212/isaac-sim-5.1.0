import omni.kit.test
import omni.ui as ui
from omni.kit import ui_test
from omni.kit.menu.utils import LayoutSourceSearch, MenuItemDescription, MenuLayout

from .utils import refresh_menus, verify_menu_checked_items, verify_menu_items


class TestMenuLayoutUtils(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        omni.kit.menu.utils.get_instance().clear_menu_data()

    async def tearDown(self):
        pass

    async def test_nested_submenu_layout(self):
        menu_placeholder = [MenuItemDescription(name="placeholder", show_fn=lambda: False)]

        menu_physics = [
            MenuItemDescription(
                name="Physics",
                sub_menu=[
                    MenuItemDescription(name="Debug"),
                    MenuItemDescription(name="Settings"),
                    MenuItemDescription(name="Demo Scenes"),
                    MenuItemDescription(name="Test Runner"),
                    MenuItemDescription(name="Character Controller"),
                ],
            )
        ]

        menu_blast = [
            MenuItemDescription(
                name="Blast",
                sub_menu=[
                    MenuItemDescription(name="Settings"),
                    MenuItemDescription(
                        name="Documentation",
                        sub_menu=[
                            MenuItemDescription(name="Kit UI"),
                            MenuItemDescription(name="Programming"),
                            MenuItemDescription(name="USD Schemas"),
                        ],
                    ),
                ],
            )
        ]

        menu_flow = [
            MenuItemDescription(
                name="Flow", sub_menu=[MenuItemDescription(name="Presets"), MenuItemDescription(name="Monitor")]
            )
        ]

        # add menu
        omni.kit.menu.utils.add_menu_items(menu_placeholder, "Window", 90)
        omni.kit.menu.utils.add_menu_items(menu_physics, "Window")
        omni.kit.menu.utils.add_menu_items(menu_blast, "Window")
        omni.kit.menu.utils.add_menu_items(menu_flow, "Window")
        await ui_test.human_delay()

        # ----------------------------------------------------
        # nested layout test
        # ----------------------------------------------------
        menu_layout = [
            MenuLayout.Menu(
                "Window",
                [
                    MenuLayout.SubMenu(
                        "Simulation",
                        [
                            MenuLayout.Group(
                                "Flow",
                                [
                                    MenuLayout.Item("Presets", source="Window/Flow/Presets"),
                                    MenuLayout.Item("Monitor", source="Window/Flow/Monitor"),
                                ],
                            ),
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
                            MenuLayout.Group(
                                "Physics",
                                [
                                    MenuLayout.Item("Demo Scenes"),
                                    MenuLayout.Item("Settings", source="Window/Physics/Settings"),
                                    MenuLayout.Item("Debug"),
                                    MenuLayout.Item("Test Runner"),
                                    MenuLayout.Item("Character Controller"),
                                ],
                            ),
                        ],
                    ),
                ],
            )
        ]
        omni.kit.menu.utils.add_layout(menu_layout)
        await ui_test.human_delay(10)

        try:
            # verify layout
            verify_menu_items(
                self,
                [
                    (ui.Menu, "Window", True),
                    (ui.Menu, "Simulation", True),
                    (ui.MenuItem, "placeholder", False),
                    (ui.Menu, "Physics", False),
                    (ui.Menu, "Blast", False),
                    (ui.Menu, "Flow", False),
                    (ui.Menu, "Documentation", True),
                    (ui.Separator, "Flow", True),
                    (ui.MenuItem, "Presets", True),
                    (ui.MenuItem, "Monitor", True),
                    (ui.Separator, "Blast", True),
                    (ui.MenuItem, "Settings", True),
                    (ui.Separator, "Physics", True),
                    (ui.MenuItem, "Demo Scenes", True),
                    (ui.MenuItem, "Settings", True),
                    (ui.MenuItem, "Debug", True),
                    (ui.MenuItem, "Test Runner", True),
                    (ui.MenuItem, "Character Controller", True),
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
            omni.kit.menu.utils.remove_menu_items(menu_physics, "Window")
            omni.kit.menu.utils.remove_menu_items(menu_blast, "Window")
            omni.kit.menu.utils.remove_menu_items(menu_flow, "Window")
            omni.kit.menu.utils.remove_menu_items(menu_placeholder, "Window")
            self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

    async def test_remapped_layout_checkbox(self):
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
        omni.kit.menu.utils.add_menu_items(menu_placeholder, "Tools")
        omni.kit.menu.utils.add_menu_items(menu_placeholder, "More Tools")
        omni.kit.menu.utils.add_menu_items(menu_entry1, "Window")
        omni.kit.menu.utils.add_menu_items(menu_entry2, "Window")
        await ui_test.human_delay()

        # more the "Example Window" and "Best Window Ever" to different menus
        menu_layout = [
            MenuLayout.Menu("Tools", [MenuLayout.Item("Stage Window", source="Window/Example Window")]),
            MenuLayout.Menu("More Tools", [MenuLayout.Item("Another Stage Window", source="Window/Best Window Ever")]),
            MenuLayout.Menu("More Cheese", [MenuLayout.Item("Not A Menu Item", source="No Menu/Worst Window Ever")]),
        ]
        omni.kit.menu.utils.add_layout(menu_layout)
        await ui_test.human_delay(10)

        # update checked status (checked) - refreshing window should refresh "Tools" and "More Tools"
        example_window_is_ticked = True
        omni.kit.menu.utils.refresh_menu_items("Window")
        # open menu as items are not refreshed on refresh_menu_items
        for menu_name in ["Tools", "More Tools", "Stage Window", "Another Stage Window"]:
            await refresh_menus(menu_name)

        try:
            # verify
            verify_menu_checked_items(
                self,
                [
                    (ui.Menu, "Tools", True, False, False),
                    (ui.Menu, "More Tools", True, False, False),
                    (ui.Menu, "Window", False, False, False),
                    (ui.MenuItem, "Stage Window", True, True, True),
                    (ui.MenuItem, "Another Stage Window", True, True, True),
                ],
            )

            # update checked status (unchecked) - refreshing window should refresh "Tools" and "More Tools"
            example_window_is_ticked = False
            omni.kit.menu.utils.refresh_menu_items("Window")
            # open menu as items are not refreshed on refresh_menu_items
            for menu_name in ["Tools", "More Tools", "Stage Window", "Another Stage Window"]:
                await refresh_menus(menu_name)

            # verify
            verify_menu_checked_items(
                self,
                [
                    (ui.Menu, "Tools", True, False, False),
                    (ui.Menu, "More Tools", True, False, False),
                    (ui.Menu, "Window", False, False, False),
                    (ui.MenuItem, "Stage Window", True, True, False),
                    (ui.MenuItem, "Another Stage Window", True, True, False),
                ],
            )
        finally:
            # remove layout
            omni.kit.menu.utils.remove_layout(menu_layout)
            self.assertTrue(omni.kit.menu.utils.get_menu_layout() == [])

            # remove menu
            omni.kit.menu.utils.remove_menu_items(menu_entry2, "Window")
            omni.kit.menu.utils.remove_menu_items(menu_entry1, "Window")
            omni.kit.menu.utils.remove_menu_items(menu_placeholder, "Tools")
            omni.kit.menu.utils.remove_menu_items(menu_placeholder, "More Tools")
            self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

    async def test_remapped_layout_checkbox_submenu(self):
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

        # update checked status (checked) - refreshing window should refresh "Developer/Utilities"
        example_window_is_ticked = True
        await refresh_menus("Window", "Developer")

        try:
            # verify ticks are on
            verify_menu_checked_items(
                self,
                [
                    (ui.Menu, "Developer", True, False, False),
                    (ui.Menu, "Window", False, False, False),
                    (ui.Menu, "Utilities", True, False, False),
                    (ui.MenuItem, "Stage Window", True, True, True),
                    (ui.MenuItem, "Another Stage Window", True, True, True),
                ],
            )

            # update checked status (unchecked) - refreshing window should refresh "Developer/Utilities"
            example_window_is_ticked = False
            await refresh_menus("Window", "Developer")

            # verify ticks are off
            verify_menu_checked_items(
                self,
                [
                    (ui.Menu, "Developer", True, False, False),
                    (ui.Menu, "Window", False, False, False),
                    (ui.Menu, "Utilities", True, False, False),
                    (ui.MenuItem, "Stage Window", True, True, False),
                    (ui.MenuItem, "Another Stage Window", True, True, False),
                ],
            )
        finally:
            # remove layout
            omni.kit.menu.utils.remove_layout(menu_layout)
            self.assertTrue(omni.kit.menu.utils.get_menu_layout() == [])

            # remove menu
            omni.kit.menu.utils.remove_menu_items(menu_entry2, "Window")
            omni.kit.menu.utils.remove_menu_items(menu_entry1, "Window")
            omni.kit.menu.utils.remove_menu_items(menu_placeholder, "Developer")
            self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

    async def test_layout_local_source(self):
        menu_placeholder = [MenuItemDescription(name="placeholder", show_fn=lambda: False)]

        menu_physics = [
            MenuItemDescription(
                name="Physics",
                sub_menu=[
                    MenuItemDescription(name="Debug"),
                    MenuItemDescription(name="Settings"),
                    MenuItemDescription(name="Demo Scenes"),
                    MenuItemDescription(name="Test Runner"),
                    MenuItemDescription(name="Character Controller"),
                ],
            )
        ]

        menu_blast = [
            MenuItemDescription(
                name="Blast",
                sub_menu=[
                    MenuItemDescription(name="Settings"),
                    MenuItemDescription(
                        name="Documentation",
                        sub_menu=[
                            MenuItemDescription(name="Kit UI"),
                            MenuItemDescription(name="Programming"),
                            MenuItemDescription(name="USD Schemas"),
                        ],
                    ),
                ],
            )
        ]

        menu_flow = [
            MenuItemDescription(
                name="Flow", sub_menu=[MenuItemDescription(name="Presets"), MenuItemDescription(name="Monitor")]
            )
        ]

        # add menu
        omni.kit.menu.utils.add_menu_items(menu_placeholder, "Window", 90)
        omni.kit.menu.utils.add_menu_items(menu_physics, "Window")
        omni.kit.menu.utils.add_menu_items(menu_blast, "Window")
        omni.kit.menu.utils.add_menu_items(menu_flow, "Window")
        await ui_test.human_delay()

        # ----------------------------------------------------
        # nested layout test
        # ----------------------------------------------------
        menu_layout = [
            MenuLayout.Menu(
                "Window",
                [
                    MenuLayout.SubMenu(
                        "Simulation",
                        [
                            MenuLayout.Group(
                                "Flow",
                                [
                                    MenuLayout.Item("Presets", source="Window/Flow/Presets"),
                                    MenuLayout.Item("Monitor", source="Window/Flow/Monitor"),
                                ],
                            ),
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
                            MenuLayout.Group(
                                "Physics",
                                [
                                    MenuLayout.Item("Demo Scenes"),
                                    MenuLayout.Item("Settings", source="Window/Physics/Settings"),
                                    MenuLayout.Item("Debug"),
                                    MenuLayout.Item("Test Runner"),
                                    MenuLayout.Item("Character Controller"),
                                ],
                            ),
                        ],
                    ),
                    # these should not be moved as they are local only
                    MenuLayout.Item("Demo Scenes", source_search=LayoutSourceSearch.LOCAL_ONLY),
                    MenuLayout.Item("Settings", source_search=LayoutSourceSearch.LOCAL_ONLY),
                    MenuLayout.Item("Debug", source_search=LayoutSourceSearch.LOCAL_ONLY),
                    MenuLayout.Item("Test Runner", source_search=LayoutSourceSearch.LOCAL_ONLY),
                    MenuLayout.Item("Character Controller", source_search=LayoutSourceSearch.LOCAL_ONLY),
                ],
            )
        ]
        omni.kit.menu.utils.add_layout(menu_layout)

        try:
            # verify layout
            verify_menu_items(
                self,
                [
                    (ui.Menu, "Window", True),
                    (ui.Menu, "Simulation", True),
                    (ui.MenuItem, "placeholder", False),
                    (ui.Menu, "Physics", False),
                    (ui.Menu, "Blast", False),
                    (ui.Menu, "Flow", False),
                    (ui.Menu, "Documentation", True),
                    (ui.Separator, "Flow", True),
                    (ui.MenuItem, "Presets", True),
                    (ui.MenuItem, "Monitor", True),
                    (ui.Separator, "Blast", True),
                    (ui.MenuItem, "Settings", True),
                    (ui.Separator, "Physics", True),
                    (ui.MenuItem, "Demo Scenes", True),
                    (ui.MenuItem, "Settings", True),
                    (ui.MenuItem, "Debug", True),
                    (ui.MenuItem, "Test Runner", True),
                    (ui.MenuItem, "Character Controller", True),
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
            omni.kit.menu.utils.remove_menu_items(menu_physics, "Window")
            omni.kit.menu.utils.remove_menu_items(menu_blast, "Window")
            omni.kit.menu.utils.remove_menu_items(menu_flow, "Window")
            omni.kit.menu.utils.remove_menu_items(menu_placeholder, "Window")
            self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

    async def test_layout_slashes(self):
        menu_profiler = [
            MenuItemDescription(
                name="Profiler",
                sub_menu=[
                    MenuItemDescription(name="Start\\Stop"),
                ],
            )
        ]

        # add menu
        omni.kit.menu.utils.add_menu_items(menu_profiler, "Window", 90)
        await ui_test.human_delay()

        # ----------------------------------------------------
        # nested layout test
        # ----------------------------------------------------
        menu_layout = [
            MenuLayout.Menu(
                "Window",
                [
                    MenuLayout.SubMenu(
                        "FixMe",
                        [
                            MenuLayout.Item("Start\\Stop", source="Window/Profiler/Start\\Stop"),
                        ],
                    ),
                ],
            )
        ]
        omni.kit.menu.utils.add_layout(menu_layout)

        try:
            # verify layout
            verify_menu_items(
                self,
                [
                    (ui.Menu, "Window", True),
                    (ui.Menu, "FixMe", True),
                    (ui.Menu, "Profiler", False),
                    (ui.MenuItem, "Start\\Stop", True),
                ],
            )
        finally:
            # remove layout
            omni.kit.menu.utils.remove_layout(menu_layout)
            self.assertTrue(omni.kit.menu.utils.get_menu_layout() == [])

            # remove menu
            omni.kit.menu.utils.remove_menu_items(menu_profiler, "Window")
            self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

    async def test_layout_duplicate_item_name(self):
        menu_profiler = [
            MenuItemDescription(
                name="Cheese",
                sub_menu=[
                    MenuItemDescription(name="Cheese"),
                    MenuItemDescription(name="More Cheese"),
                ],
            )
        ]

        # add menu
        omni.kit.menu.utils.add_menu_items(menu_profiler, "Window", 90)
        await ui_test.human_delay()

        # ----------------------------------------------------
        # nested layout test
        # ----------------------------------------------------
        menu_layout = [
            MenuLayout.Menu(
                "Window",
                [
                    MenuLayout.SubMenu(
                        "Profiler",
                        [
                            MenuLayout.Item("Profiler Window", source="Window/Cheese/Cheese"),
                            MenuLayout.Item("Profiler Test", source="Window/Cheese/More Cheese"),
                        ],
                    ),
                ],
            )
        ]
        omni.kit.menu.utils.add_layout(menu_layout)

        try:
            # verify layout
            verify_menu_items(
                self,
                [
                    (ui.Menu, "Window", True),
                    (ui.Menu, "Profiler", True),
                    (ui.Menu, "Cheese", False),
                    (ui.MenuItem, "Profiler Window", True),
                    (ui.MenuItem, "Profiler Test", True),
                ],
            )
        finally:
            # remove layout
            omni.kit.menu.utils.remove_layout(menu_layout)
            self.assertTrue(omni.kit.menu.utils.get_menu_layout() == [])

            # remove menu
            omni.kit.menu.utils.remove_menu_items(menu_profiler, "Window")
            self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

    async def test_layout_header_move(self):
        menu_profiler = [
            MenuItemDescription(
                name="Cheese",
                sub_menu=[
                    MenuItemDescription(name="Item", header="Cheese"),
                ],
            )
        ]

        # add menu
        omni.kit.menu.utils.add_menu_items(menu_profiler, "Window", 90)
        await ui_test.human_delay()

        # ----------------------------------------------------
        # nested layout test
        # ----------------------------------------------------
        menu_layout = [
            MenuLayout.Menu(
                "Window",
                [
                    MenuLayout.SubMenu(
                        "FixMe",
                        [
                            MenuLayout.Item("Start\\Stop", source="Window/Cheese/Item"),
                        ],
                    ),
                ],
            )
        ]
        omni.kit.menu.utils.add_layout(menu_layout)

        try:
            # verify layout
            verify_menu_items(
                self,
                [
                    (ui.Menu, "Window", True),
                    (ui.Menu, "FixMe", True),
                    (ui.Menu, "Cheese", False),
                    (ui.MenuItem, "Start\\Stop", True),
                ],
            )
        finally:
            # remove layout
            omni.kit.menu.utils.remove_layout(menu_layout)
            self.assertTrue(omni.kit.menu.utils.get_menu_layout() == [])

            # remove menu
            omni.kit.menu.utils.remove_menu_items(menu_profiler, "Window")
            self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

    async def test_empty_root_menu(self):
        menu_replicator = [
            MenuItemDescription(name="Start"),
            MenuItemDescription(name="Resume"),
            MenuItemDescription(name="Preview"),
            MenuItemDescription(name=""),
            MenuItemDescription(name="Capture On Play"),
            MenuItemDescription(name="Synthetic Data Recorder"),
            MenuItemDescription(name=""),
            MenuItemDescription(name="Replicator YAML"),
            MenuItemDescription(name=""),
            MenuItemDescription(name="Semantics Schema Editor"),
        ]

        # add menu
        menu_placeholder1 = omni.kit.menu.utils.add_menu_items(
            [MenuItemDescription(name="placeholder", show_fn=lambda: False)], name="Window", menu_index=90
        )
        menu_placeholder2 = omni.kit.menu.utils.add_menu_items(
            [MenuItemDescription(name="placeholder", show_fn=lambda: False)], name="FixMe", menu_index=91
        )
        omni.kit.menu.utils.add_menu_items(menu_replicator, "Replicator", 90)
        await ui_test.human_delay()

        # move everything but separator test
        menu_layout1 = [
            MenuLayout.Menu(
                "Window",
                [
                    MenuLayout.Item(name="Semantics Schema Editor", source="Replicator/Semantics Schema Editor"),
                    MenuLayout.Item(name="Replicator YAML", source="Replicator/Replicator YAML"),
                    MenuLayout.Seperator(),
                    MenuLayout.Item(name="Synthetic Data Recorder", source="Replicator/Synthetic Data Recorder"),
                    MenuLayout.Item(name="Preview", source="Replicator/Preview"),
                    MenuLayout.Item(name="Start", source="Replicator/Start"),
                    MenuLayout.Item(name="Resume", source="Replicator/Resume"),
                ],
            ),
        ]
        omni.kit.menu.utils.add_layout(menu_layout1)

        menu_layout2 = [
            MenuLayout.Menu(
                "FixMe",
                [
                    MenuLayout.Item(name="Capture On Play", source="Replicator/Capture On Play"),
                ],
            ),
        ]
        omni.kit.menu.utils.add_layout(menu_layout2)

        try:
            # verify layout
            verify_menu_items(
                self,
                [
                    (ui.Menu, "Window", True),
                    (ui.Menu, "Replicator", False),
                    (ui.Menu, "FixMe", True),
                    (ui.MenuItem, "Semantics Schema Editor", True),
                    (ui.MenuItem, "Replicator YAML", True),
                    (ui.Separator, "", True),
                    (ui.MenuItem, "Synthetic Data Recorder", True),
                    (ui.MenuItem, "Preview", True),
                    (ui.MenuItem, "Start", True),
                    (ui.MenuItem, "Resume", True),
                    (ui.MenuItem, "placeholder", False),
                    (ui.Separator, "", False),
                    (ui.MenuItem, "Capture On Play", True),
                    (ui.MenuItem, "placeholder", False),
                ],
            )
        finally:
            # remove layout
            omni.kit.menu.utils.remove_layout(menu_layout1)
            omni.kit.menu.utils.remove_layout(menu_layout2)
            self.assertTrue(omni.kit.menu.utils.get_menu_layout() == [])

            # remove menu
            omni.kit.menu.utils.remove_menu_items(menu_replicator, "Replicator")
            omni.kit.menu.utils.remove_menu_items(menu_placeholder1, "Window")
            omni.kit.menu.utils.remove_menu_items(menu_placeholder2, "FixMe")
            self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})
