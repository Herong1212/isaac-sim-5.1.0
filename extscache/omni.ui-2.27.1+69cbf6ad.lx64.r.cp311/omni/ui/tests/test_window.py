## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
from .test_base import OmniUiTest
import omni.ui as ui
import omni.kit.app
from functools import partial
import omni.kit.test


WINDOW_STYLE = {"Window": {"background_color": 0xFF303030, "border_color": 0x0, "border_width": 0, "border_radius": 0}}
MODAL_WINDOW_STYLE = {
    "Window": {
        "background_color": 0xFFFF0000,
        "border_color": 0x0,
        "border_width": 0,
        "border_radius": 0,
        "secondary_background_color": 0,
    }
}


class TestWindow(OmniUiTest):
    """Testing ui.Window"""

    async def test_general(self):
        """Testing general properties of ui.Windows"""
        window = await self.create_test_window()

        # Empty window
        window1 = ui.Window(
            "Test1", width=100, height=100, position_x=10, position_y=10, flags=ui.WINDOW_FLAGS_NO_SCROLLBAR
        )
        window1.frame.set_style(WINDOW_STYLE)

        # Window with Label
        window2 = ui.Window(
            "Test2", width=100, height=100, position_x=120, position_y=10, flags=ui.WINDOW_FLAGS_NO_SCROLLBAR
        )
        window2.frame.set_style(WINDOW_STYLE)
        with window2.frame:
            ui.Label("Hello world")

        # Window with layout
        window3 = ui.Window(
            "Test3", width=100, height=100, position_x=10, position_y=120, flags=ui.WINDOW_FLAGS_NO_SCROLLBAR
        )
        window3.frame.set_style(WINDOW_STYLE)
        with window3.frame:
            with ui.VStack():
                ui.Spacer()
                with ui.HStack(height=0):
                    ui.Spacer()
                    ui.Label("Hello world", width=0)

        await self.finalize_test()

    async def test_imgui_visibility(self):
        """Testing general properties of ui.Windows"""
        window = await self.create_test_window()

        # Empty window
        window1 = ui.Window("Test1", width=100, height=100, position_x=10, position_y=10)
        window1.frame.set_style(WINDOW_STYLE)

        await omni.kit.app.get_app().next_update_async()

        # Remove window
        window1 = None

        await omni.kit.app.get_app().next_update_async()

        # It's still at ImGui cache, but we cant change the visibility of it.
        window1 = ui.Workspace.get_window("Test1")
        self.assertIsNotNone(window1)
        self.assertIsNone(window1.visible)

        await omni.kit.app.get_app().next_update_async()

        # Create another one
        window1 = ui.Window("Test1", width=100, height=100, position_x=10, position_y=10)
        window1.frame.set_style(WINDOW_STYLE)
        with window1.frame:
            ui.Label("Hello world")

        await omni.kit.app.get_app().next_update_async()

        # It should be visible
        await self.finalize_test()

    async def test_overlay(self):
        """Testing the ability to overlay of ui.Windows"""
        window = await self.create_test_window()

        # Creating to windows with the same title. It should be displayed as
        # one window with the elements of both windows.
        window1 = ui.Window("Test", width=100, height=100, position_x=10, position_y=10)
        window1.frame.set_style(WINDOW_STYLE)
        with window1.frame:
            with ui.VStack():
                ui.Label("Hello world", height=0)

        window3 = ui.Window("Test")
        window3.frame.set_style(WINDOW_STYLE)
        with window3.frame:
            with ui.VStack():
                ui.Spacer()
                ui.Label("Hello world", height=0)

        await self.finalize_test()

    async def test_popup1(self):
        """Testing WINDOW_FLAGS_POPUP"""
        window = await self.create_test_window()

        # General popup
        window1 = ui.Window(
            "test_popup1",
            width=100,
            height=100,
            position_x=10,
            position_y=10,
            flags=ui.WINDOW_FLAGS_POPUP | ui.WINDOW_FLAGS_NO_TITLE_BAR,
        )
        window1.frame.set_style(WINDOW_STYLE)
        with window1.frame:
            with ui.VStack():
                ui.Label("Hello world", height=0)

        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_popup2(self):
        """Testing WINDOW_FLAGS_POPUP"""
        window = await self.create_test_window()

        # Two popups
        window1 = ui.Window(
            "test_popup2_0",
            width=100,
            height=100,
            position_x=10,
            position_y=10,
            flags=ui.WINDOW_FLAGS_POPUP | ui.WINDOW_FLAGS_NO_TITLE_BAR,
        )
        window1.frame.set_style(WINDOW_STYLE)
        with window1.frame:
            with ui.VStack():
                ui.Label("Hello world", height=0)

        # Wait one frame and create second window.
        await omni.kit.app.get_app().next_update_async()

        window2 = ui.Window(
            "test_popup2_1",
            position_x=10,
            position_y=10,
            auto_resize=True,
            flags=ui.WINDOW_FLAGS_POPUP | ui.WINDOW_FLAGS_NO_TITLE_BAR,
        )
        window2.frame.set_style(WINDOW_STYLE)
        with window2.frame:
            with ui.VStack():
                ui.Label("Second popup", height=0)

        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_popup3(self):
        """Testing WINDOW_FLAGS_POPUP"""
        window = await self.create_test_window()
        with window.frame:
            with ui.VStack():
                field = ui.StringField(style={"background_color": 0x0})

        field.model.set_value("This is StringField")

        # General popup
        window1 = ui.Window(
            "test_popup3",
            width=100,
            height=100,
            position_x=10,
            position_y=10,
            flags=ui.WINDOW_FLAGS_POPUP | ui.WINDOW_FLAGS_NO_TITLE_BAR,
        )
        window1.frame.set_style(WINDOW_STYLE)
        with window1.frame:
            with ui.VStack():
                ui.Label("Hello world", height=0)

        # Wait one frame and focus field
        await omni.kit.app.get_app().next_update_async()
        field.focus_keyboard()

        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_modal1(self):
        """Testing WINDOW_FLAGS_MODAL"""
        window = await self.create_test_window()

        # General popup
        window1 = ui.Window(
            "test_modal1",
            width=100,
            height=100,
            position_x=10,
            position_y=10,
            flags=ui.WINDOW_FLAGS_MODAL | ui.WINDOW_FLAGS_NO_TITLE_BAR,
        )
        window1.frame.set_style(WINDOW_STYLE)
        with window1.frame:
            with ui.VStack():
                ui.Label("Hello world", height=0)

        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_modal2(self):
        """Testing WINDOW_FLAGS_MODAL with transparent dim background"""
        window = await self.create_test_window()

        # General popup
        window1 = ui.Window(
            "test_modal2",
            width=100,
            height=100,
            position_x=10,
            position_y=10,
            flags=ui.WINDOW_FLAGS_MODAL | ui.WINDOW_FLAGS_NO_TITLE_BAR,
        )
        window1.frame.set_style(MODAL_WINDOW_STYLE)
        with window1.frame:
            with ui.VStack():
                ui.Label("Hello world", height=0)

        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_menubar(self):
        """Testing general properties of ui.MenuBar"""
        window = await self.create_test_window()

        # Empty window
        window1 = ui.Window(
            "Test1",
            width=100,
            height=100,
            position_x=10,
            position_y=10,
            flags=ui.WINDOW_FLAGS_MENU_BAR | ui.WINDOW_FLAGS_NO_SCROLLBAR,
        )
        window1.frame.set_style(WINDOW_STYLE)
        with window1.menu_bar:
            with ui.Menu("File"):
                ui.MenuItem("Open")
        with window1.frame:
            ui.Label("Hello world")

        # Window with Label
        window2 = ui.Window(
            "Test2",
            width=100,
            height=100,
            position_x=120,
            position_y=10,
            flags=ui.WINDOW_FLAGS_MENU_BAR | ui.WINDOW_FLAGS_NO_SCROLLBAR,
        )
        window2.frame.set_style(WINDOW_STYLE)
        window2.menu_bar.style = {"MenuBar": {"background_color": 0xFFEDB51A}}
        with window2.menu_bar:
            with ui.Menu("File"):
                ui.MenuItem("Open")
        with window2.frame:
            ui.Label("Hello world")

        # Window with layout
        window3 = ui.Window(
            "Test3",
            width=100,
            height=100,
            position_x=10,
            position_y=120,
            flags=ui.WINDOW_FLAGS_MENU_BAR | ui.WINDOW_FLAGS_NO_SCROLLBAR,
        )
        window3.frame.style = {**WINDOW_STYLE, **{"Window": {"background_color": 0xFFEDB51A}}}
        with window3.menu_bar:
            with ui.Menu("File"):
                ui.MenuItem("Open")
        with window3.frame:
            ui.Label("Hello world")

        await self.finalize_test()

    async def test_docked(self):
        ui_main_window = ui.MainWindow()
        win = ui.Window("first", width=100, height=100)
        await omni.kit.app.get_app().next_update_async()
        self.assertFalse(win.docked)
        main_dockspace = ui.Workspace.get_window("DockSpace")
        win.dock_in(main_dockspace, ui.DockPosition.SAME)
        await omni.kit.app.get_app().next_update_async()
        self.assertTrue(win.docked)

    async def test_is_selected_in_dock(self):
        ui_main_window = ui.MainWindow()
        window1 = ui.Window("First", width=100, height=100)
        window2 = ui.Window("Second", width=100, height=100)
        window3 = ui.Window("Thrid", width=100, height=100)
        await omni.kit.app.get_app().next_update_async()
        main_dockspace = ui.Workspace.get_window("DockSpace")
        window1.dock_in(main_dockspace, ui.DockPosition.SAME)
        window2.dock_in(main_dockspace, ui.DockPosition.SAME)
        window3.dock_in(main_dockspace, ui.DockPosition.SAME)
        await omni.kit.app.get_app().next_update_async()
        window2.focus()
        await omni.kit.app.get_app().next_update_async()
        self.assertFalse(window1.is_selected_in_dock())
        self.assertTrue(window2.is_selected_in_dock())
        self.assertFalse(window3.is_selected_in_dock())

    async def test_mainwindow_resize(self):
        """Testing resizing of mainwindow"""
        await self.create_test_area(128, 128)

        main_window = ui.MainWindow()
        main_window.main_menu_bar.clear()
        main_window.main_menu_bar.visible = True
        main_window.main_menu_bar.menu_compatibility = False

        with main_window.main_menu_bar:
            with ui.Menu("NVIDIA"):
                ui.MenuItem("Item 1")
                ui.MenuItem("Item 2")
                ui.MenuItem("Item 3")
            ui.Spacer()
            with ui.Menu("Omniverse"):
                ui.MenuItem("Item 1")
                ui.MenuItem("Item 2")
                ui.MenuItem("Item 3")

        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        main_dockspace = ui.Workspace.get_window("DockSpace")
        window1 = ui.Window("Viewport")
        with window1.frame:
            ui.Label("Window", alignment=ui.Alignment.CENTER)

        await omni.kit.app.get_app().next_update_async()

        window1.dock_in(main_dockspace, ui.DockPosition.SAME)

        await omni.kit.app.get_app().next_update_async()

        window1.dock_tab_bar_enabled = False

        app_window = omni.appwindow.get_default_app_window()
        app_window.resize(256, 128)

        for i in range(2):
            await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

        main_window = None
        window1.dock_tab_bar_enabled = True  # Turn back on for other tests

        for i in range(2):
            await omni.kit.app.get_app().next_update_async()

    async def test_window_tooltip(self):
        ui.Workspace.clear()
        await self.create_test_area(block_devices=False)
        ui_main_window = ui.MainWindow()
        ui_main_window.main_menu_bar.visible = False
        win1 = ui.Window("first", width=100, height=100)
        win1.tabBar_tooltip="hello world"
        win2 = ui.Window("second", width=100, height=100)
        await omni.kit.app.get_app().next_update_async()

        main_dockspace = ui.Workspace.get_window("DockSpace")
        win1.dock_in(main_dockspace, ui.DockPosition.SAME)
        win2.dock_in(win1, ui.DockPosition.SAME)
        await omni.kit.app.get_app().next_update_async()

        import omni.kit.ui_test as ui_test
        await ui_test.emulate_mouse_move(ui_test.Vec2(22, 12))
        for i in range(2):
            await omni.kit.app.get_app().next_update_async()
        await self.finalize_test()
        ui.Workspace.clear()

    async def test_window_no_tooltip(self):
        ui.Workspace.clear()
        await self.create_test_area(block_devices=False)
        ui_main_window = ui.MainWindow()
        ui_main_window.main_menu_bar.visible = False
        win1 = ui.Window("first", width=100, height=100)
        win1.tabBar_tooltip="hello world"
        win2 = ui.Window("second", width=100, height=100)
        await omni.kit.app.get_app().next_update_async()

        main_dockspace = ui.Workspace.get_window("DockSpace")
        win1.dock_in(main_dockspace, ui.DockPosition.SAME)
        win2.dock_in(win1, ui.DockPosition.SAME)
        await omni.kit.app.get_app().next_update_async()

        import omni.kit.ui_test as ui_test
        await ui_test.emulate_mouse_move(ui_test.Vec2(80, 12))
        for i in range(2):
            await omni.kit.app.get_app().next_update_async()
        await self.finalize_test()
        ui.Workspace.clear()


class WindowCallbacks(OmniUiTest):

    def _focus_callback(self, state_dict, name, focus_state: bool) -> None:
        state_dict[name] = focus_state

    async def test_window_focus_callback(self):
        """test window focus callback"""
        focus_values = {}
        window1 = ui.Window("First", width=100, height=100)
        window1.set_focused_changed_fn(partial(self._focus_callback, focus_values, "window1"))
        window2 = ui.Window("Second", width=100, height=100)
        window1.set_focused_changed_fn(partial(self._focus_callback, focus_values, "window2"))
        await omni.kit.app.get_app().next_update_async()
        #Looks like setting focus on 1 window doesn't set if off on the others?
        window1.focus()
        self.assertTrue(focus_values['window1']==True)
        await omni.kit.app.get_app().next_update_async()
        window2.focus()
        self.assertTrue(focus_values['window2']==True)

    async def __test_window_focus_policy(self, focus_policy: ui.FocusPolicy, mouse_event: str, focus_changes: bool = True):
        import omni.kit.ui_test as ui_test
        from carb.input import MouseEventType

        width, height = 100, 100
        start_pos = ui_test.Vec2(width, height)
        window0_center = ui_test.Vec2(width/2, height/2)
        window1_center = window0_center + ui_test.Vec2(width, 0)

        mouse_types = {
            "left": (MouseEventType.LEFT_BUTTON_DOWN, MouseEventType.LEFT_BUTTON_UP),
            "middle": (MouseEventType.MIDDLE_BUTTON_DOWN, MouseEventType.MIDDLE_BUTTON_UP),
            "right": (MouseEventType.RIGHT_BUTTON_DOWN, MouseEventType.RIGHT_BUTTON_UP),
        }.get(mouse_event)

        # Get the list of expected eulsts based on FocusPolicy
        if focus_changes:
            if focus_policy != ui.FocusPolicy.FOCUS_ON_HOVER:
                focus_tests = [
                    (False, True),  # Initial state
                    (False, True),  # After mouse move to window 0
                    (False, True),  # After mouse move to window 1
                    (True, False),  # After mouse click in window 0
                    (False, True),  # After mouse click in window 1
                ]
            else:
                focus_tests = [
                    (False, True),  # Initial state
                    (True, False),  # After mouse move to window 0
                    (False, True),  # After mouse move to window 1
                    (True, False),  # After mouse click in window 0
                    (False, True),  # After mouse click in window 1
                ]
        else:
            # Default focus test that never changes focus
            focus_tests = [
                (False, True),  # Initial state
                (False, True),  # After mouse move to window 0
                (False, True),  # After mouse move to window 1
                (False, True),  # After mouse click in window 0
                (False, True),  # After mouse click in window 1
            ]

        await self.create_test_area(width*2, height, block_devices=False)

        window0 = ui.Window("0", width=width, height=height, position_y=0, position_x=0)
        window1 = ui.Window("1", width=width, height=height, position_y=0, position_x=width)

        # Test initial focus state
        if focus_policy != ui.FocusPolicy.DEFAULT:
            self.assertNotEqual(window0.focus_policy, focus_policy)
            window0.focus_policy = focus_policy
            self.assertNotEqual(window1.focus_policy, focus_policy)
            window1.focus_policy = focus_policy

        self.assertEqual(window0.focus_policy, focus_policy)
        self.assertEqual(window1.focus_policy, focus_policy)

        # Test  the individual focus state and move to next state test
        focus_test_idx = 0
        async def test_focused_windows():
            nonlocal focus_test_idx
            expected_focus_state = focus_tests[focus_test_idx]
            focus_test_idx = focus_test_idx + 1

            window0_focused, window1_focused = window0.focused, window1.focused
            expected_window0_focus, expected_window1_focus = expected_focus_state[0], expected_focus_state[1]

            # Build a more specifc failure message
            fail_msg = f"Testing {focus_policy} with mouse '{mouse_event}' (focus_test_idx: {focus_test_idx-1})"
            fail_msg_0 = f"{fail_msg}: Window 0 expected focus: {expected_window0_focus}, had focus {window0_focused}."
            fail_msg_1 = f"{fail_msg}: Window 1 expected focus: {expected_window1_focus}, had focus {window1_focused}."

            self.assertEqual(expected_window0_focus, window0_focused, msg=fail_msg_0)
            self.assertEqual(expected_window1_focus, window1_focused, msg=fail_msg_1)


        # Move mouse
        await ui_test.input.emulate_mouse_move(start_pos)
        # Test the current focus state
        await test_focused_windows()

        # Move mouse
        await ui_test.input.emulate_mouse_move(window0_center)
        # Test the current focus state on both windows
        await test_focused_windows()

        # Move mouse
        await ui_test.input.emulate_mouse_move(window1_center)
        # Test the current focus state on both windows
        await test_focused_windows()

        # Move mouse to Window 0
        await ui_test.emulate_mouse_move(window0_center)
        # Do mouse click: down and up event
        await ui_test.input.emulate_mouse(mouse_types[0])
        await ui_test.input.wait_n_updates_internal()
        await ui_test.input.emulate_mouse(mouse_types[1])
        await ui_test.input.wait_n_updates_internal()
        # Test the current focus state on both windows
        await test_focused_windows()

        # Move mouse to Window 1
        await ui_test.emulate_mouse_move(window1_center)
        # Do mouse click: down and up event
        await ui_test.input.emulate_mouse(mouse_types[0])
        await ui_test.input.wait_n_updates_internal()
        await ui_test.input.emulate_mouse(mouse_types[1])
        await ui_test.input.wait_n_updates_internal()
        # Test the current focus state on both windows
        await test_focused_windows()

    async def test_window_focus_policy_left_mouse(self):
        """test Window focus policy based on mouse events on left click"""
        # Left click should change focus
        await self.__test_window_focus_policy(ui.FocusPolicy.FOCUS_ON_LEFT_MOUSE_DOWN, "left")

        # Middle click should not change focus
        await self.__test_window_focus_policy(ui.FocusPolicy.FOCUS_ON_LEFT_MOUSE_DOWN, "middle", False)

        # Right click should not change focus
        await self.__test_window_focus_policy(ui.FocusPolicy.FOCUS_ON_LEFT_MOUSE_DOWN, "right", False)

    async def test_window_focus_policy_any_mouse(self):
        """test Window focus policy based on mouse events on any click"""
        # Left click should change focus
        await self.__test_window_focus_policy(ui.FocusPolicy.FOCUS_ON_ANY_MOUSE_DOWN, "left")

        # Middle click should change focus
        await self.__test_window_focus_policy(ui.FocusPolicy.FOCUS_ON_ANY_MOUSE_DOWN, "middle")

        # Right click should change focus
        await self.__test_window_focus_policy(ui.FocusPolicy.FOCUS_ON_ANY_MOUSE_DOWN, "right")

    async def test_window_focus_policy_hover_mouse(self):
        """test Window focus policy based on mouse events hover"""
        # Left click should change focus
        await self.__test_window_focus_policy(ui.FocusPolicy.FOCUS_ON_HOVER, "left")

        # Middle click should not change focus
        await self.__test_window_focus_policy(ui.FocusPolicy.FOCUS_ON_HOVER, "middle")

        # Right click should not change focus
        await self.__test_window_focus_policy(ui.FocusPolicy.FOCUS_ON_HOVER, "right")

    async def test_callback_remove(self):
        self.called = 0
        def callback():
            self.called += 1
        window = ui.Window("test callback")
        callback1 = window.set_visibility_changed_fn(lambda v: callback())
        callback2 = window.set_visibility_changed_fn(lambda v: callback())

        self.assertEqual(self.called , 2)

        window.set_visibility_changed_fn(None)
        window.visible = True
        # check that the callback was removed
        self.assertEqual(self.called , 2)
