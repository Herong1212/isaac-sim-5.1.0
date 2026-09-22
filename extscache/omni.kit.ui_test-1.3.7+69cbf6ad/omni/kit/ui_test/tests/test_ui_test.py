## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
import unittest
import omni.kit.app
from omni.kit.test import AsyncTestCase

import omni.ui as ui
import omni.kit.ui_test as ui_test
import carb.input
import omni.appwindow

from carb.input import KeyboardInput, KeyboardEventType

from contextlib import asynccontextmanager


@asynccontextmanager
async def capture_keyboard():
    input = carb.input.acquire_input_interface()
    keyboard = omni.appwindow.get_default_app_window().get_keyboard()

    events = []

    def on_input(e):
        events.append((e.input, e.type, e.modifiers))

    sub = input.subscribe_to_keyboard_events(keyboard, on_input)

    try:
        yield events
    finally:
        input.unsubscribe_to_keyboard_events(keyboard, sub)


@asynccontextmanager
async def capture_mouse():
    input = carb.input.acquire_input_interface()
    mouse = omni.appwindow.get_default_app_window().get_mouse()

    events = []

    def on_input(e):
        events.append((e.input, e.type))

    sub = input.subscribe_to_mouse_events(mouse, on_input)

    try:
        yield events
    finally:
        input.unsubscribe_to_mouse_events(mouse, sub)


class TestUITest(AsyncTestCase):
    async def setUp(self):
        self._clicks = 0

        self._window = ui.Window("Cool Window")
        with self._window.frame:  # the frame can only have 1 widget under it
            with ui.HStack():
                with ui.VStack():
                    ui.Label("Test2")
                with ui.VStack(width=150):
                    with ui.HStack(height=30):
                        ui.Label("Test1")
                        ui.StringField()

                        def on_click(*_):
                            self._clicks += 1

                        ui.Button("TestButton", clicked_fn=on_click)

        await ui_test.wait_n_updates(2)

    async def tearDown(self):
        self._window = None

    async def test_find(self):
        # Click a button
        button = ui_test.find("Cool Window//Frame/**/Button[*]")
        self.assertEqual(button.realpath, "Cool Window//Frame/HStack[0]/VStack[1]/HStack[0]/Button[0]")
        await button.click()
        self.assertEqual(self._clicks, 1)

        # Move mouse away, click and then click button again, that should be +1 click:
        await ui_test.emulate_mouse_move(ui_test.Vec2(0, 0))
        await ui_test.emulate_mouse_click()
        await ui_test.find("Cool Window//Frame/**/Button[*]").click()
        self.assertEqual(self._clicks, 2)

    async def test_nested_find(self):
        # Multiple nested finds
        h_stack = ui_test.find("Cool Window//Frame/HStack[0]")
        self.assertEqual(h_stack.realpath, "Cool Window//Frame/HStack[0]")
        await h_stack.find("**/Button[0]").click()
        self.assertEqual(self._clicks, 1)

        window = ui_test.find("Cool Window")
        h_stack = window.find("HStack[0]")
        self.assertEqual(h_stack.realpath, "Cool Window//Frame/HStack[0]")
        await h_stack.find("**/Button[0]").click()
        self.assertEqual(self._clicks, 2)

    async def test_find_all(self):
        labels = ui_test.find_all("Cool Window//Frame/**/Label[*]")
        self.assertSetEqual({s.widget.text for s in labels}, {"Test1", "Test2"})

        h_stack = ui_test.find("Cool Window//Frame/HStack[0]")
        labels = h_stack.find_all("**/Label[*]")
        self.assertSetEqual({s.widget.text for s in labels}, {"Test1", "Test2"})

    async def test_find_first(self):
        label = ui_test.find_first("Cool Window//Frame/**/Label[*]")
        self.assertSetEqual({label.widget.text}, {"Test2"})


class TestInput(AsyncTestCase):
    async def test_emulate_keyboard(self):
        async with capture_keyboard() as events:
            await ui_test.emulate_keyboard_press(carb.input.KeyboardInput.X, carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL)

            self.assertListEqual(
                events,
                [
                    (KeyboardInput.LEFT_CONTROL, KeyboardEventType.KEY_PRESS, carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL),
                    (KeyboardInput.X, KeyboardEventType.KEY_PRESS, carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL),
                    (KeyboardInput.X, KeyboardEventType.KEY_RELEASE, carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL),
                    (KeyboardInput.LEFT_CONTROL, KeyboardEventType.KEY_RELEASE, 0),
                ],
            )

    async def test_emulate_key_combo(self):
        async with capture_keyboard() as events:
            await ui_test.emulate_key_combo("SHIFT+ctrl+w")
            self.assertListEqual(
                events,
                [
                    (KeyboardInput.LEFT_SHIFT, KeyboardEventType.KEY_PRESS, carb.input.KEYBOARD_MODIFIER_FLAG_SHIFT),
                    (KeyboardInput.LEFT_CONTROL, KeyboardEventType.KEY_PRESS, carb.input.KEYBOARD_MODIFIER_FLAG_SHIFT | carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL),
                    (KeyboardInput.W, KeyboardEventType.KEY_PRESS, carb.input.KEYBOARD_MODIFIER_FLAG_SHIFT | carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL),
                    (KeyboardInput.W, KeyboardEventType.KEY_RELEASE, carb.input.KEYBOARD_MODIFIER_FLAG_SHIFT | carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL),
                    (KeyboardInput.LEFT_CONTROL, KeyboardEventType.KEY_RELEASE, carb.input.KEYBOARD_MODIFIER_FLAG_SHIFT),
                    (KeyboardInput.LEFT_SHIFT, KeyboardEventType.KEY_RELEASE, 0),
                ],
            )
            events.clear()
            await ui_test.emulate_key_combo("Y")
            self.assertListEqual(
                events,
                [(KeyboardInput.Y, KeyboardEventType.KEY_PRESS, 0), (KeyboardInput.Y, KeyboardEventType.KEY_RELEASE, 0)],
            )

    @unittest.skip("Subscribe to mouse in carbonite doesn't seem to work")
    async def test_emulate_mouse_scroll(self):
        async with capture_mouse() as events:
            await ui_test.emulate_mouse_scroll(ui_test.Vec2(5.5, 6.5))
            print(events)
            self.assertListEqual(
                events,
                [] # TODO
            )
