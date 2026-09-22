## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
import asyncio
from .test_base import OmniUiTest
import omni.kit.app
import omni.ui as ui
from functools import partial


class TestMenu(OmniUiTest):
    """Testing ui.Menu"""

    async def test_general(self):
        """Testing general properties of ui.Menu"""
        window = await self.create_test_window()

        with window.frame:
            ui.Spacer()

        shown = [False, False]

        def on_shown(index, s):
            shown[index] = s

        self.menu_h = ui.Menu("Test Hidden Context Menu", shown_changed_fn=partial(on_shown, 0))
        self.menu_v = ui.Menu("Test Visible Context Menu", shown_changed_fn=partial(on_shown, 1))

        with self.menu_h:
            ui.MenuItem("Hidden 1")
            ui.MenuItem("Hidden 2")
            ui.MenuItem("Hidden 3")

        with self.menu_v:
            ui.MenuItem("Test 1")
            ui.MenuItem("Test 2")
            ui.MenuItem("Test 3")

        # No menu is shown
        self.assertIsNone(ui.Menu.get_current())

        self.menu_h.show_at(0, 0)
        self.menu_v.show_at(0, 0)

        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        # Check the callback is called
        self.assertFalse(shown[0])
        self.assertTrue(shown[1])
        # Check the property
        self.assertFalse(self.menu_h.shown)
        self.assertTrue(self.menu_v.shown)
        # Check the current menu
        self.assertEqual(ui.Menu.get_current(), self.menu_v)

        await self.finalize_test()

        # Remove menus for later tests
        self.menu_h.destroy()
        self.menu_v.destroy()

    async def test_modern(self):
        """Testing general properties of ui.Menu"""
        window = await self.create_test_window()

        with window.frame:
            ui.Spacer()

        shown = [False, False]

        def on_shown(index, s):
            shown[index] = s

        self.menu_h = ui.Menu(
            "Test Hidden Context Menu Modern", shown_changed_fn=partial(on_shown, 0), menu_compatibility=0
        )
        self.menu_v = ui.Menu(
            "Test Visible Context Menu Modern", shown_changed_fn=partial(on_shown, 1), menu_compatibility=0
        )

        with self.menu_h:
            ui.MenuItem("Hidden 1")
            ui.MenuItem("Hidden 2")
            ui.MenuItem("Hidden 3")

        with self.menu_v:
            ui.MenuItem("Test 1")
            ui.MenuItem("Test 2")
            ui.MenuItem("Test 3")

        self.menu_h.show_at(0, 0)
        self.menu_v.show_at(0, 0)

        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        # Check the callback is called
        self.assertFalse(shown[0])
        self.assertTrue(shown[1])
        # Check the property
        self.assertFalse(self.menu_h.shown)
        self.assertTrue(self.menu_v.shown)
        # Check the current menu
        self.assertEqual(ui.Menu.get_current(), self.menu_v)

        await self.finalize_test()

        # Remove menus for later tests
        self.menu_h.destroy()
        self.menu_v.destroy()
        self.menu_h = None
        self.menu_v = None

    async def test_modern_visibility(self):
        import omni.kit.ui_test as ui_test

        triggered = []

        def on_triggered():
            triggered.append(True)

        window = await self.create_test_window(block_devices=False)

        with window.frame:
            ui.Spacer()

        menu = ui.Menu("Test Visibility Context Menu Modern", menu_compatibility=0)

        with menu:
            ui.MenuItem("Hidden 1")
            ui.MenuItem("Hidden 2")
            ui.MenuItem("Hidden 3")
            invis = ui.MenuItem("Invisible", triggered_fn=on_triggered)
            invis.visible = False
            ui.MenuItem("Another Invisible", visible=False)

        menu.show_at(0, 0)

        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        invis.visible = True

        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        ref_invis = ui_test.WidgetRef(invis, "")
        await ui_test.emulate_mouse_move_and_click(ref_invis.center)

        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        # Check the callback is called
        self.assertTrue(triggered)

        await self.finalize_test_no_image()

    async def test_modern_horizontal(self):
        """Testing general properties of ui.Menu"""
        window = await self.create_test_window()

        with window.frame:
            with ui.Menu(height=0, menu_compatibility=0, direction=ui.Direction.LEFT_TO_RIGHT):
                with ui.Menu("File"):
                    ui.MenuItem("Hidden 1")
                    ui.MenuItem("Hidden 2")
                    ui.MenuItem("Hidden 3")

                with ui.Menu("Edit"):
                    ui.MenuItem("Test 1")
                    ui.MenuItem("Test 2")
                    ui.MenuItem("Test 3")

        await self.finalize_test()

    async def test_modern_horizontal_right(self):
        """Testing general properties of ui.Menu"""
        window = await self.create_test_window()

        with window.frame:
            with ui.Menu(height=0, menu_compatibility=0, direction=ui.Direction.LEFT_TO_RIGHT):
                with ui.Menu("File"):
                    ui.MenuItem("Hidden 1")
                    ui.MenuItem("Hidden 2")
                    ui.MenuItem("Hidden 3")

                ui.Spacer()

                with ui.Menu("Edit"):
                    ui.MenuItem("Test 1")
                    ui.MenuItem("Test 2")
                    ui.MenuItem("Test 3")

        await self.finalize_test()

    async def test_modern_delegate(self):
        """Testing general properties of ui.Menu"""
        window = await self.create_test_window()

        with window.frame:
            ui.Spacer()

        class Delegate(ui.MenuDelegate):
            def build_item(self, item):
                if item.text[0] == "#":
                    ui.Rectangle(height=20, style={"background_color": ui.color(item.text)})

            def build_title(self, item):
                ui.Label(item.text)

            def build_status(self, item):
                ui.Label("Status is also here")

        self.menu = ui.Menu("Test Modern Delegate", menu_compatibility=0, delegate=Delegate())

        with self.menu:
            ui.MenuItem("#ff6600")
            ui.MenuItem("#00ff66")
            ui.MenuItem("#0066ff")
            ui.MenuItem("#66ff00")
            ui.MenuItem("#6600ff")
            ui.MenuItem("#ff0066")

        self.menu.show_at(0, 0)

        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

        # Remove menu for later tests
        self.menu.destroy()
        self.menu = None

    async def test_modern_checked(self):
        """Testing general properties of ui.Menu"""
        window = await self.create_test_window()

        with window.frame:
            ui.Spacer()

        called = [False, False]
        checked = [False, False]

        self.menu_v = ui.Menu("Test Visible Context Menu Modern", menu_compatibility=0)

        def checked_changed(i, c):
            called[i] = True
            checked[i] = c

        with self.menu_v:
            item1 = ui.MenuItem("Test 1", checked=False, checkable=True)
            item1.set_checked_changed_fn(partial(checked_changed, 0))
            item2 = ui.MenuItem("Test 2", checked=False, checkable=True, checked_changed_fn=partial(checked_changed, 1))
            ui.MenuItem("Test 3", checked=True, checkable=True)
            ui.MenuItem("Test 4", checked=False, checkable=True)
            ui.MenuItem("Test 5")

        item1.checked = True
        item2.checked = True

        self.menu_v.show_at(0, 0)

        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        # Check the callback is called
        self.assertTrue(called[0])
        self.assertTrue(checked[0])
        self.assertTrue(called[1])
        self.assertTrue(checked[1])

        await self.finalize_test()

        self.menu_v.destroy()
        self.menu_v = None

    async def test_radio(self):
        """Testing radio collections"""
        import omni.kit.ui_test as ui_test

        window = await self.create_test_window(block_devices=False)

        with window.frame:
            ui.Spacer()

        called = [False, False]
        checked = [False, False]

        self.menu = ui.Menu("Test Visible Context Menu Modern", menu_compatibility=0)

        def checked_changed(i, c):
            called[i] = True
            checked[i] = c

        with self.menu:
            collection = ui.MenuItemCollection("Collection")
            with collection:
                m1 = ui.MenuItem("Test 1", checked=False, checkable=True)
                m2 = ui.MenuItem("Test 2", checked=False, checkable=True)
                m3 = ui.MenuItem("Test 3", checked=False, checkable=True)
                m4 = ui.MenuItem("Test 4", checked=False, checkable=True)

        m2.checked = True
        m3.checked = True

        self.menu.show_at(0, 0)

        ref = ui_test.WidgetRef(collection, "")
        await omni.kit.app.get_app().next_update_async()
        await ui_test.emulate_mouse_move(ref.center)

        await omni.kit.app.get_app().next_update_async()

        # Check the checked states
        self.assertFalse(m1.checked)
        self.assertFalse(m2.checked)
        self.assertTrue(m3.checked)
        self.assertFalse(m4.checked)

        await self.finalize_test()

        self.menu.destroy()
        self.menu = None

    async def test_modern_click(self):
        """Click the menu bar"""
        import omni.kit.ui_test as ui_test

        window = await self.create_test_window(block_devices=False)

        with window.frame:
            with ui.Menu(height=0, menu_compatibility=0, direction=ui.Direction.LEFT_TO_RIGHT):
                file = ui.Menu("File")
                with file:
                    ui.MenuItem("File 1")
                    ui.MenuItem("File 2")
                    ui.MenuItem("File 3")

                with ui.Menu("Edit"):
                    ui.MenuItem("Edit 1")
                    ui.MenuItem("Edit 2")
                    ui.MenuItem("Edit 3")

        ref = ui_test.WidgetRef(file, "")

        # Click the File item
        await omni.kit.app.get_app().next_update_async()
        await ui_test.emulate_mouse_move_and_click(ref.center)

        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_modern_click_click(self):
        """Click the menu bar, wait, click again"""
        import omni.kit.ui_test as ui_test

        window = await self.create_test_window(block_devices=False)

        with window.frame:
            with ui.Menu(height=0, menu_compatibility=0, direction=ui.Direction.LEFT_TO_RIGHT):
                file = ui.Menu("File")
                with file:
                    ui.MenuItem("File 1")
                    ui.MenuItem("File 2")
                    ui.MenuItem("File 3")

                with ui.Menu("Edit"):
                    ui.MenuItem("Edit 1")
                    ui.MenuItem("Edit 2")
                    ui.MenuItem("Edit 3")

        ref = ui_test.WidgetRef(file, "")

        # Click the File item
        await omni.kit.app.get_app().next_update_async()
        await ui_test.emulate_mouse_move_and_click(ref.center)

        await asyncio.sleep(0.5)

        # Click the File item one more time
        await ui_test.emulate_mouse_move_and_click(ref.center)

        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_modern_click_move(self):
        """Click the menu bar, move to another item"""
        import omni.kit.ui_test as ui_test

        window = await self.create_test_window(block_devices=False)

        with window.frame:
            with ui.Menu(height=0, menu_compatibility=0, direction=ui.Direction.LEFT_TO_RIGHT):
                file = ui.Menu("File")
                with file:
                    ui.MenuItem("File 1")
                    ui.MenuItem("File 2")
                    ui.MenuItem("File 3")

                edit = ui.Menu("Edit")
                with edit:
                    ui.MenuItem("Edit 1")
                    ui.MenuItem("Edit 2")
                    ui.MenuItem("Edit 3")

        refFile = ui_test.WidgetRef(file, "")
        refEdit = ui_test.WidgetRef(edit, "")

        # Click the File item
        await omni.kit.app.get_app().next_update_async()
        await ui_test.emulate_mouse_move_and_click(refFile.center)

        await asyncio.sleep(0.5)

        # Hover the Edit item
        await ui_test.emulate_mouse_move(refEdit.center)

        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_modern_click_submenu(self):
        """Click the menu bar, wait, click again"""
        import omni.kit.ui_test as ui_test

        window = await self.create_test_window(block_devices=False)

        with window.frame:
            with ui.Menu(height=0, menu_compatibility=0, direction=ui.Direction.LEFT_TO_RIGHT):
                file = ui.Menu("File")
                with file:
                    ui.MenuItem("File 1")
                    sub = ui.Menu("Sub")
                    with sub:
                        ui.MenuItem("File 2")
                        mid = ui.MenuItem("Middle")
                        ui.MenuItem("File 4")

                    ui.MenuItem("File 5")

                with ui.Menu("Edit"):
                    ui.MenuItem("Edit 1")
                    ui.MenuItem("Edit 2")
                    ui.MenuItem("Edit 3")

        refFile = ui_test.WidgetRef(file, "")
        refSub = ui_test.WidgetRef(sub, "")
        refMid = ui_test.WidgetRef(mid, "")

        # Click the File item
        await omni.kit.app.get_app().next_update_async()
        await ui_test.emulate_mouse_move_and_click(refFile.center)

        # Hover the Sub item
        await omni.kit.app.get_app().next_update_async()
        await ui_test.emulate_mouse_move(refSub.center)

        # Hover the Middle item
        await omni.kit.app.get_app().next_update_async()
        await ui_test.emulate_mouse_move(refMid.center)

        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_modern_tearoff(self):
        """Click the menu bar, wait, click again"""
        import omni.kit.ui_test as ui_test

        shown_times = [0, 0]

        def on_shown(shown, shown_times=shown_times):
            """Called when the file menu is opened"""
            if shown:
                # It will show if it's opened or closed
                shown_times[0] += 1
            else:
                shown_times[0] -= 1
            # Could times it's called
            shown_times[1] += 1

        await self.create_test_area(block_devices=False)

        ui_main_window = ui.MainWindow()
        ui_main_window.main_menu_bar.visible = False
        window = ui.Window(
            "test_modern_tearoff",
            flags=ui.WINDOW_FLAGS_NO_SCROLLBAR | ui.WINDOW_FLAGS_NO_TITLE_BAR | ui.WINDOW_FLAGS_NO_RESIZE,
        )
        window.frame.set_style({"Window": {"background_color": 0xFF000000, "border_color": 0x0, "border_radius": 0}})

        await omni.kit.app.get_app().next_update_async()

        main_dockspace = ui.Workspace.get_window("DockSpace")
        window.dock_in(main_dockspace, ui.DockPosition.SAME)
        window.dock_tab_bar_visible = False

        with window.frame:
            with ui.Menu(height=0, menu_compatibility=0, direction=ui.Direction.LEFT_TO_RIGHT):
                file = ui.Menu("File", shown_changed_fn=on_shown)
                with file:
                    ui.MenuItem("File 1")
                    ui.MenuItem("File 2")
                    ui.MenuItem("File 5")

                with ui.Menu("Edit"):
                    ui.MenuItem("Edit 1")
                    ui.MenuItem("Edit 2")
                    ui.MenuItem("Edit 3")

        refFile = ui_test.WidgetRef(file, "")

        # Click the File item
        for _ in range(2):
            await omni.kit.app.get_app().next_update_async()
        await ui_test.emulate_mouse_move_and_click(refFile.center)

        # Move the menu window to the middle of the screen
        await omni.kit.app.get_app().next_update_async()
        await ui_test.emulate_mouse_drag_and_drop(
            ui_test.Vec2(refFile.center.x, refFile.center.y + 15), ui_test.Vec2(128, 128)
        )

        await omni.kit.app.get_app().next_update_async()
        # Menu should be torn off
        self.assertTrue(file.teared)
        # But the pull-down portion of the menu is not shown
        self.assertFalse(file.shown)

        # Click the File item
        for _ in range(2):
            await omni.kit.app.get_app().next_update_async()
        await ui_test.emulate_mouse_move_and_click(refFile.center)
        await omni.kit.app.get_app().next_update_async()

        # It should be 1 to indicate that the menu is opened
        self.assertEqual(shown_times[0], 1)
        # It was called three times:
        # - To open menu
        # - To tear off, the menu is closed
        # - Opened again to make a screenshot
        self.assertEqual(shown_times[1], 3)

        # Menu should be torn off
        self.assertTrue(file.teared)
        # But the pull-down portion of the menu is not shown
        self.assertTrue(file.shown)

        await self.finalize_test()

    async def test_modern_tearoff_submenu(self):
        """Click the menu bar, wait, click again"""
        import omni.kit.ui_test as ui_test

        await self.create_test_area(block_devices=False)

        ui_main_window = ui.MainWindow()
        ui_main_window.main_menu_bar.visible = False
        window = ui.Window(
            "test_modern_tearoff",
            flags=ui.WINDOW_FLAGS_NO_SCROLLBAR | ui.WINDOW_FLAGS_NO_TITLE_BAR | ui.WINDOW_FLAGS_NO_RESIZE,
        )
        window.frame.set_style({"Window": {"background_color": 0xFF000000, "border_color": 0x0, "border_radius": 0}})

        await omni.kit.app.get_app().next_update_async()

        main_dockspace = ui.Workspace.get_window("DockSpace")
        window.dock_in(main_dockspace, ui.DockPosition.SAME)
        window.dock_tab_bar_visible = False

        with window.frame:
            with ui.Menu(height=0, menu_compatibility=0, direction=ui.Direction.LEFT_TO_RIGHT):
                file = ui.Menu("File")
                with file:
                    ui.MenuItem("File 1")
                    sub = ui.Menu("Sub")
                    with sub:
                        ui.MenuItem("File 2")
                        ui.MenuItem("File 3")
                        ui.MenuItem("File 4")

                    ui.MenuItem("File 5")

                with ui.Menu("Edit"):
                    ui.MenuItem("Edit 1")
                    ui.MenuItem("Edit 2")
                    ui.MenuItem("Edit 3")

        refFile = ui_test.WidgetRef(file, "")
        refSub = ui_test.WidgetRef(sub, "")

        # Click the File item
        for _ in range(2):
            await omni.kit.app.get_app().next_update_async()
        await ui_test.emulate_mouse_move_and_click(refFile.center)

        # Hover the Sub item
        await omni.kit.app.get_app().next_update_async()
        await ui_test.emulate_mouse_move(refSub.center)

        # Move the menu window to the middle of the screen
        for _ in range(2):
            await omni.kit.app.get_app().next_update_async()

        await ui_test.emulate_mouse_drag_and_drop(
            ui_test.Vec2(refSub.position.x + refSub.size.x + 10, refSub.center.y - 10), ui_test.Vec2(128, 128)
        )

        # Click the File item
        for _ in range(2):
            await omni.kit.app.get_app().next_update_async()
        await ui_test.emulate_mouse_move_and_click(refFile.center)

        # Hover the Sub item
        await omni.kit.app.get_app().next_update_async()
        await ui_test.emulate_mouse_move(refSub.center)

        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_modern_button(self):
        """Click the menu bar"""
        import omni.kit.ui_test as ui_test

        clicked = []

        class Delegate(ui.MenuDelegate):
            def build_item(self, item):
                with ui.HStack(width=200):
                    ui.Label(item.text)
                    with ui.VStack(content_clipping=1, width=0):
                        ui.Button("Button", clicked_fn=lambda: clicked.append(True))

        delegate = Delegate()

        window = await self.create_test_window(block_devices=False)

        with window.frame:
            with ui.Menu(height=0, menu_compatibility=0, direction=ui.Direction.LEFT_TO_RIGHT):
                file = ui.Menu("File")
                with file:
                    child = ui.MenuItem("File 1", delegate=delegate)
                    ui.MenuItem("File 2", delegate=delegate)
                    ui.MenuItem("File 3", delegate=delegate)

                with ui.Menu("Edit"):
                    ui.MenuItem("Edit 1", delegate=delegate)
                    ui.MenuItem("Edit 2", delegate=delegate)
                    ui.MenuItem("Edit 3", delegate=delegate)

        ref_file = ui_test.WidgetRef(file, "")
        ref_child = ui_test.WidgetRef(child, "")

        # Click the File item
        await omni.kit.app.get_app().next_update_async()
        await ui_test.emulate_mouse_move_and_click(ref_file.center)

        await omni.kit.app.get_app().next_update_async()
        await ui_test.emulate_mouse_move_and_click(
            ui_test.Vec2(ref_child.position.x + ref_child.size.x - 10, ref_child.center.y)
        )

        await omni.kit.app.get_app().next_update_async()

        self.assertEqual(len(clicked), 1)

        await self.finalize_test()

    async def test_modern_enabled(self):
        """Click the menu bar"""
        import omni.kit.ui_test as ui_test

        window = await self.create_test_window(block_devices=False)

        with window.frame:
            with ui.Menu(height=0, menu_compatibility=0, direction=ui.Direction.LEFT_TO_RIGHT):
                file = ui.Menu("File")
                with file:
                    ui.MenuItem("File 1")
                    ui.MenuItem("File 2", enabled=False)
                    f3 = ui.MenuItem("File 3")
                    f4 = ui.MenuItem("File 4", enabled=False)

                with ui.Menu("Edit"):
                    ui.MenuItem("Edit 1")
                    ui.MenuItem("Edit 2")
                    ui.MenuItem("Edit 3")

        ref = ui_test.WidgetRef(file, "")

        # Click the File item
        await omni.kit.app.get_app().next_update_async()
        await ui_test.emulate_mouse_move_and_click(ref.center)
        await omni.kit.app.get_app().next_update_async()

        # Changed enabled runtime while the menu is open
        f3.enabled = False
        f4.enabled = True

        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_modern_submenu_disabled(self):
        """Test sub-menu items when parent si disabled"""
        import omni.kit.ui_test as ui_test

        window = await self.create_test_window(block_devices=False)

        with window.frame:
            with ui.Menu(height=0, menu_compatibility=0, direction=ui.Direction.LEFT_TO_RIGHT):
                file = ui.Menu("File")
                with file:
                    file_1 = ui.Menu("File 1", enabled=True)
                    with file_1:
                        ui.MenuItem("File 1a")
                        ui.MenuItem("File 1b")
                    file_2 = ui.Menu("File 2", enabled=False)
                    with file_2:
                        ui.MenuItem("File 2a")
                        ui.MenuItem("File 2b")

        ref = ui_test.WidgetRef(file, "")
        ref_1 = ui_test.WidgetRef(file_1, "")
        ref_2 = ui_test.WidgetRef(file_2, "")

        # Click the File item
        await omni.kit.app.get_app().next_update_async()
        await ui_test.emulate_mouse_move_and_click(ref.center)

        await omni.kit.app.get_app().next_update_async()
        await ui_test.emulate_mouse_move(ref_1.center)

        for _ in range(3):
            await omni.kit.app.get_app().next_update_async()
        await self.capture_and_compare(golden_img_name="omni.ui_scene.tests.TestMenu.test_modern_submenu_disabled_on.png")

        await omni.kit.app.get_app().next_update_async()
        await ui_test.emulate_mouse_move(ref_2.center)

        for _ in range(3):
            await omni.kit.app.get_app().next_update_async()
        await self.finalize_test(golden_img_name="omni.ui_scene.tests.TestMenu.test_modern_submenu_disabled_off.png")

    async def test_window(self):
        """Check we can create a window from menu"""
        import omni.kit.ui_test as ui_test

        menu = ui.Menu("menu", name="this")
        dialogs = []

        def _build_message_popup():
            dialogs.append(ui.Window("Message", width=100, height=50))

        def _show_context_menu(x, y, button, modifier):
            if button != 1:
                return
            menu.clear()
            with menu:
                ui.MenuItem("Create Pop-up", triggered_fn=_build_message_popup)
            menu.show()

        window = await self.create_test_window(block_devices=False)
        with window.frame:
            button = ui.Button("context menu", width=0, height=0, mouse_pressed_fn=_show_context_menu)

        await omni.kit.app.get_app().next_update_async()

        ref = ui_test.WidgetRef(button, "")
        await ui_test.emulate_mouse_move_and_click(ref.center, right_click=True)

        await omni.kit.app.get_app().next_update_async()

        await ui_test.emulate_mouse_move_and_click(
            ui_test.Vec2(ref.position.x + ref.size.x, ref.position.y + ref.size.y)
        )

        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_identifier(self):
        """Testing identifer and name properties of ui.Menu and ui.MenuItem"""
        window = await self.create_test_window()

        menu_a = ui.Menu("Test A")
        menu_b = ui.Menu("Test B", name="test b")
        menu_c = ui.Menu("Test C", name="Test c", identifier="test [c]")

        self.assertEqual(menu_a.identifier, "Test A")
        self.assertEqual(menu_b.identifier, "test b")
        self.assertEqual(menu_c.identifier, "test [c]")

        with menu_a:
            item_0 = ui.MenuItem("Item 0")
            item_1 = ui.MenuItem("Item 1", name="item 1")
            item_2 = ui.MenuItem("Item 2", name="Item 2", identifier="item [2]")

        self.assertEqual(item_0.identifier, "Item 0")
        self.assertEqual(item_1.identifier, "item 1")
        self.assertEqual(item_2.identifier, "item [2]")

        # Linux needs to wait a moment
        item_0, item_1, item_2 = None, None, None
        menu_a, menu_b, menu_c = None, None, None
        window = None
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test_no_image()
