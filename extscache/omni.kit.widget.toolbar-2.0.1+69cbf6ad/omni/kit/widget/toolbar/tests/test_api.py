# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.appwindow
import omni.kit.app
import omni.kit.test
import omni.kit.ui_test as ui_test
import omni.kit.widget.toolbar
import omni.ui as ui
from carb.input import KeyboardInput as Key
from omni.kit.ui_test import Vec2
from omni.kit.widget.toolbar import Hotkey, SimpleToolButton, Toolbar, WidgetGroup, get_instance

from .helpers import reset_toolbar_settings
from ..extension import get_data_path_internal

test_message_queue = []


class TestSimpleToolButton(SimpleToolButton):
    """
    Test of how to use SimpleToolButton
    """

    def __init__(self, icon_path):
        def on_toggled(c):
            test_message_queue.append(f"Test button toggled {c}")

        super().__init__(
            name="test_simple",
            tooltip="Test Simple ToolButton",
            icon_path=f"{icon_path}/plus.svg",
            icon_checked_path=f"{icon_path}/plus.svg",
            hotkey=Key.L,
            toggled_fn=on_toggled,
        )


class TestToolButtonGroup(WidgetGroup):
    """
    Test of how to create two ToolButton in one WidgetGroup
    """

    def __init__(self, icon_path):
        super().__init__()
        self._icon_path = icon_path

    def clean(self):
        self._sub1 = None
        self._sub2 = None
        self._hotkey.clean()
        self._hotkey = None
        super().clean()

    def get_style(self):
        style = {
            "Button.Image::test1": {"image_url": f"{self._icon_path}/plus.svg"},
            "Button.Image::test1:checked": {"image_url": f"{self._icon_path}/minus.svg"},
            "Button.Image::test2": {"image_url": f"{self._icon_path}/minus.svg"},
            "Button.Image::test2:checked": {"image_url": f"{self._icon_path}/plus.svg"},
        }
        return style

    def create(self, default_size):
        def on_value_changed(index, model):
            if model.get_value_as_bool():
                self._acquire_toolbar_context()
            else:
                self._release_toolbar_context()
            test_message_queue.append(f"Group button {index} clicked")

        button1 = ui.ToolButton(
            name="test1",
            width=default_size,
            height=default_size,
        )
        self._sub1 = button1.model.subscribe_value_changed_fn(lambda model, index=1: on_value_changed(index, model))

        button2 = ui.ToolButton(
            name="test2",
            width=default_size,
            height=default_size,
        )
        self._sub2 = button2.model.subscribe_value_changed_fn(lambda model, index=2: on_value_changed(index, model))

        self._hotkey = Hotkey(
            "toolbar::test2",
            Key.K,
            lambda: button2.model.set_value(not button2.model.get_value_as_bool()),
            lambda: self._is_in_context(),
        )

        # return a dictionary of name -> widget if you want to expose it to other widget_group
        return {"test1": button1, "test2": button2}


_MAIN_WINDOW_INSTANCE = None


class ToolbarApiTest(omni.kit.test.AsyncTestCase):
    WINDOW_NAME = "Main Toolbar Test"

    async def setUp(self):
        reset_toolbar_settings()

        self._icon_path = get_data_path_internal().absolute().joinpath("icon").absolute()
        self._app = omni.kit.app.get_app()
        test_message_queue.clear()

        # If the instance doesn't exist, we need to create it for the test
        # Create a tmp window with the widget inside, Y axis because the tests are in the Y axis
        global _MAIN_WINDOW_INSTANCE
        if _MAIN_WINDOW_INSTANCE is None:
            _MAIN_WINDOW_INSTANCE = ui.ToolBar(
                self.WINDOW_NAME, noTabBar=False, padding_x=3, padding_y=3, margin=5, axis=ui.ToolBarAxis.Y
            )
            self._widget = get_instance()
            self._widget.set_axis(ui.ToolBarAxis.Y)
            self._widget.rebuild_toolbar(root_frame=_MAIN_WINDOW_INSTANCE.frame)
            await self._app.next_update_async()
            await self._app.next_update_async()

        self._main_dockspace = ui.Workspace.get_window("DockSpace")
        self._toolbar_handle = ui.Workspace.get_window(self.WINDOW_NAME)
        self._toolbar_handle.undock()
        await self._app.next_update_async()

        self._toolbar_handle.dock_in(self._main_dockspace, ui.DockPosition.LEFT)
        await self._app.next_update_async()

    async def test_api(self):
        toolbar = omni.kit.widget.toolbar.get_instance()
        widget_simple = TestSimpleToolButton(self._icon_path)
        widget = TestToolButtonGroup(self._icon_path)

        toolbar.add_widget(widget, -100)
        toolbar.add_widget(widget_simple, -200)

        for i in range(2):
            await self._app.next_update_async()

        # Check widgets are added and can be fetched
        self.assertIsNotNone(toolbar.get_widget("test_simple"))
        self.assertIsNotNone(toolbar.get_widget("test1"))
        self.assertIsNotNone(toolbar.get_widget("test2"))

        for i in range(5):
            await self._app.next_update_async()

        tool_test_simple_pos = self._get_widget_center(toolbar, "test_simple")
        tool_test1_pos = self._get_widget_center(toolbar, "test1")
        tool_test2_pos = self._get_widget_center(toolbar, "test2")

        # Test click on first simple button
        await self._emulate_click(tool_test_simple_pos)
        await self._app.next_update_async()

        # Test hot key on first simple button
        await self._emulate_keyboard_press(Key.L)
        await self._app.next_update_async()

        # Test click on 1/2 group button
        await self._emulate_click(tool_test1_pos)
        await self._app.next_update_async()

        # Test click on 2/2 group button
        await self._emulate_click(tool_test2_pos)
        await self._app.next_update_async()

        # Making sure all button are triggered by checking the message queue
        expected_messages = [
            "Test button toggled True",
            "Test button toggled False",
            "Group button 1 clicked",
            "Group button 2 clicked",
        ]

        self.assertEqual(expected_messages, test_message_queue)
        test_message_queue.clear()

        toolbar.remove_widget(widget)
        toolbar.remove_widget(widget_simple)

        widget.clean()
        widget_simple.clean()

        for i in range(2):
            await self._app.next_update_async()

        # Check widgets are cleared
        self.assertIsNone(toolbar.get_widget("test_simple"))
        self.assertIsNone(toolbar.get_widget("test1"))
        self.assertIsNone(toolbar.get_widget("test2"))

    async def test_context(self):
        toolbar = omni.kit.widget.toolbar.get_instance()
        widget_simple = TestSimpleToolButton(self._icon_path)
        widget = TestToolButtonGroup(self._icon_path)

        test_context = "test_context"

        toolbar.add_widget(widget, -100)
        toolbar.add_widget(widget_simple, -200, test_context)

        await self._app.next_update_async()
        await self._app.next_update_async()
        await self._app.next_update_async()
        await self._app.next_update_async()
        await self._app.next_update_async()

        tool_test_simple_pos = self._get_widget_center(toolbar, "test_simple")
        tool_test1_pos = self._get_widget_center(toolbar, "test1")

        # Test click on first simple button
        # Add "Test button toggled True" to queue
        await self._emulate_click(tool_test_simple_pos)
        await self._app.next_update_async()

        self.assertEqual(toolbar.get_context(), test_context)

        # Test hot key on 2/2 group button
        # It should have no effect since it's not "in context"
        # Add nothing to queue
        await self._emulate_keyboard_press(Key.K)
        await self._app.next_update_async()

        # Test click on first simple button again, should exit context
        # Add "Test button toggled False" to queue
        await self._emulate_click(tool_test_simple_pos)
        await self._app.next_update_async()

        self.assertEqual(toolbar.get_context(), Toolbar.DEFAULT_CONTEXT)

        # Test hot key on 2/2 group button again
        # It should have effect because it's in default context
        # Add "Group button 2 clicked" to queue
        await self._emulate_keyboard_press(Key.K)
        await self._app.next_update_async()

        # Test click on first simple button again
        # Add "Test button toggled True" to queue
        await self._emulate_click(tool_test_simple_pos)
        await self._app.next_update_async()

        self.assertEqual(toolbar.get_context(), test_context)

        # Test click on 1/2 group button so it takes context by force.
        # Add "Group button 1 clicked" to queue
        await self._emulate_click(tool_test1_pos)
        await self._app.next_update_async()

        self.assertEqual(toolbar.get_context(), Toolbar.DEFAULT_CONTEXT)

        # Test hot key on first simple button, it should still work on default context.
        # Releasing an expired context.
        # Add "Test button toggled False" to queue
        await self._emulate_keyboard_press(Key.L)
        await self._app.next_update_async()

        self.assertEqual(toolbar.get_context(), Toolbar.DEFAULT_CONTEXT)

        # Test hot key on first simple button, it should still work on default context.
        # Add "Test button toggled True" to queue
        await self._emulate_keyboard_press(Key.L)
        await self._app.next_update_async()

        self.assertEqual(toolbar.get_context(), test_context)

        expected_messages = [
            "Test button toggled True",
            "Test button toggled False",
            "Group button 2 clicked",
            "Test button toggled True",
            "Group button 1 clicked",
            "Test button toggled False",
            "Test button toggled True",
        ]

        self.assertEqual(expected_messages, test_message_queue)
        toolbar.remove_widget(widget)
        toolbar.remove_widget(widget_simple)

        widget.clean()
        widget_simple.clean()

        await self._app.next_update_async()

    async def test_options_menu(self):
        widget = get_instance()
        builtin_tools = widget._builtin_tools

        play_group = builtin_tools._play_button_group
        if play_group:
            play_group._invoke_context_menu("")
            self.assertIsNotNone(play_group._options_menu)

        select_group = builtin_tools._select_button_group
        if select_group:
            select_group._invoke_context_menu("select_mode")
            self.assertIsNotNone(select_group._options_menu)

        snap_group = builtin_tools._snap_button_group
        if snap_group:
            snap_group._invoke_context_menu("")
            self.assertIsNotNone(snap_group._options_menu)

        transform_group = builtin_tools._transform_button_group
        if transform_group:
            transform_group._invoke_context_menu("move_op")
            self.assertIsNotNone(transform_group._move_options_menu)
            transform_group._invoke_context_menu("rotate_op")
            self.assertIsNotNone(transform_group._rotate_options_menu)

    def _get_widget_center(self, toolbar, id: str):
        return (
            toolbar.get_widget(id).screen_position_x + toolbar.get_widget(id).width / 2,
            toolbar.get_widget(id).screen_position_y + toolbar.get_widget(id).height / 2,
        )

    async def _emulate_click(self, pos):
        await ui_test.emulate_mouse_move_and_click(Vec2(*pos))

    async def _emulate_keyboard_press(self, key: Key):
        await ui_test.emulate_keyboard_press(key)
