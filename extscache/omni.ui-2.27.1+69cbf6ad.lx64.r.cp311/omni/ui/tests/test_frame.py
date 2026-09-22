## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import carb
import omni.kit.test
from functools import partial
from .test_base import OmniUiTest
import omni.ui as ui
import omni.kit.app


class TestFrame(OmniUiTest):
    """Testing ui.Frame"""

    async def test_general(self):
        """Testing general properties of ui.Frame"""
        window = await self.create_test_window()

        with window.frame:
            with ui.VStack():
                with ui.Frame(width=0, height=0):
                    ui.Label("Label in Frame")
                with ui.Frame(width=0, height=0):
                    ui.Label("First label, should not be displayed")
                    ui.Label("Second label, should be displayed")
                with ui.Frame(height=0):
                    ui.Label("Long Label in Frame. " * 10, word_wrap=True)
                with ui.Frame(horizontal_clipping=True, width=ui.Percent(50), height=0):
                    ui.Label("This should be clipped horizontally. " * 10)
                with ui.Frame(vertical_clipping=True, height=20):
                    ui.Label("This should be clipped vertically. " * 10, word_wrap=True)

        await self.finalize_test()

    async def test_deferred(self):
        """Testing deferred population of ui.Frame"""
        window = await self.create_test_window()

        def two_labels():
            ui.Label("First label, should not be displayed")
            ui.Label("Second label, should be displayed")

        with window.frame:
            with ui.VStack():
                ui.Frame(height=0, build_fn=lambda: ui.Label("Label in Frame"))
                ui.Frame(height=0, build_fn=two_labels)
                ui.Frame(height=0, build_fn=lambda: ui.Label("Long text " * 15, word_wrap=True))
                ui.Frame(
                    horizontal_clipping=True,
                    width=ui.Percent(50),
                    height=0,
                    build_fn=lambda: ui.Label("horizontal clipping " * 15),
                )

                frame = ui.Frame(height=0)
                with frame:
                    ui.Label("A deferred function will override this widget")
                frame.set_build_fn(lambda: ui.Label("This widget should be displayed"))

        # Wait two frames to let Frame create deferred children. The first
        # frame the window is Appearing.
        await omni.kit.app.get_app().next_update_async()
        # The second frame build_fn is called
        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_deferred_first_frame(self):
        """Testing the first frame of deferred population of ui.Frame"""
        window = await self.create_test_window()

        # The first frame the window is initializing its size.
        await omni.kit.app.get_app().next_update_async()

        with window.frame:
            with ui.VStack():
                ui.Frame(height=0, build_fn=lambda: ui.Label("Label in the first frame"))

        await self.finalize_test()

    async def test_deferred_rebuild(self):
        """Testing deferred rebuild of ui.Frame"""
        window = await self.create_test_window()

        self._rebuild_counter = 0

        def label_counter(self):
            self._rebuild_counter += 1
            ui.Label(f"Rebuild was called {self._rebuild_counter} times")

        window.frame.set_build_fn(lambda s=self: label_counter(s))

        # Wait two frames to let Frame create deferred children. The first
        # frame the window is Appearing.
        await omni.kit.app.get_app().next_update_async()
        # The second frame build_fn is called
        await omni.kit.app.get_app().next_update_async()

        # Rebuild everything so build_fn should be called
        window.frame.rebuild()
        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_scroll(self):
        import omni.kit.ui_test as ui_test

        first = []
        second = []

        def scroll(flag, x, y, mod):
            flag.append(x)

        window = await self.create_test_window(block_devices=False)

        # Empty window
        window1 = ui.Window("Test1", width=100, height=100, position_x=10, position_y=10)
        with window1.frame:
            with ui.ZStack():
                spacer = ui.Spacer(
                    mouse_wheel_fn=partial(scroll, first), scroll_only_window_hovered=1, mouse_pressed_fn=None
                )
                with ui.ZStack(content_clipping=1):
                    ui.Spacer()

        await omni.kit.app.get_app().next_update_async()

        ref = ui_test.WidgetRef(spacer, "")

        await ui_test.emulate_mouse_move(ref.center)
        await ui_test.emulate_mouse_scroll(ui_test.Vec2(1, 0))

        await omni.kit.app.get_app().next_update_async()

        self.assertTrue(len(first) == 0)

        await self.finalize_test_no_image()

    async def test_scroll_only_window_hovered(self):
        import omni.kit.ui_test as ui_test

        first = []
        second = []

        def scroll(flag, x, y, mod):
            flag.append(x)

        window = await self.create_test_window(block_devices=False)

        # Empty window
        window1 = ui.Window("Test1", width=100, height=100, position_x=10, position_y=10)
        with window1.frame:
            with ui.ZStack():
                spacer = ui.Spacer(
                    mouse_wheel_fn=partial(scroll, first), scroll_only_window_hovered=0, mouse_pressed_fn=None
                )
                with ui.ZStack(content_clipping=1):
                    ui.Spacer()

        await omni.kit.app.get_app().next_update_async()

        ref = ui_test.WidgetRef(spacer, "")

        await ui_test.emulate_mouse_move(ref.center)
        await ui_test.emulate_mouse_scroll(ui_test.Vec2(1, 0))

        await omni.kit.app.get_app().next_update_async()

        self.assertTrue(len(first) == 1)

        await self.finalize_test_no_image()

    async def test_clear_frame_no_crash(self):
        import omni.kit.ui_test as ui_test
        win = await self.create_test_window(block_devices=False)

        with win.frame:
            with ui.ZStack():
                with ui.VStack():
                    for i in range(3):
                        ui.Rectangle()
                with ui.HStack():
                    for i in range(3):
                        circle = ui.Circle(mouse_pressed_fn=lambda *x: win.frame.clear())

        await omni.kit.app.get_app().next_update_async()
        # click the last circle
        ref = ui_test.WidgetRef(circle, "")
        await ui_test.emulate_mouse_move(ref.center)
        # this will hit the error of `Container::clear was called during an event or draw, this is not supported`
        # It is expected. This it to test with the click of clear parent frame, the system doesn't crash
        await ui_test.emulate_mouse_click()
        await omni.kit.app.get_app().next_update_async()
        await self.finalize_test_no_image()
