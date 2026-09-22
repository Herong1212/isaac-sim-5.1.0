## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
import unittest
from .test_base import OmniUiTest
from functools import partial
import omni.kit.app
import omni.ui as ui

WINDOW_STYLE = {"Window": {"background_color": 0xFF303030, "border_color": 0x0, "border_width": 0, "border_radius": 0}}

TEXT = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut "
    "labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco "
    "laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in "
    "voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat "
    "non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
)


class TestCanvasFrame(OmniUiTest):
    """Testing ui.CanvasFrame"""

    async def test_general(self):
        """Testing general properties of ui.CanvasFrame"""
        window = await self.create_test_window()

        with window.frame:
            with ui.CanvasFrame():
                with ui.VStack(height=0):
                    # Simple text
                    ui.Label("Hello world")

                    # Word wrap
                    ui.Label(TEXT, word_wrap=True)

                    # Gray button
                    ui.Button(
                        "Button",
                        style={
                            "Button": {"background_color": 0xFF666666, "margin": 0, "padding": 4, "border_radius": 0}
                        },
                    )

        await self.finalize_test()

    @unittest.skip("Disabling temporarily to avoid failure due to bold 'l' on linux font")
    async def test_zoom(self):
        """Testing zoom of ui.CanvasFrame"""
        window = await self.create_test_window()

        with window.frame:
            with ui.CanvasFrame(zoom=0.5):
                with ui.VStack(height=0):
                    # Simple text
                    ui.Label("Hello world")

                    # Word wrap
                    ui.Label(TEXT, word_wrap=True)

                    # Gray button
                    ui.Button(
                        "Button",
                        style={
                            "Button": {"background_color": 0xFF666666, "margin": 0, "padding": 8, "border_radius": 0}
                        },
                    )

        await self.finalize_test()

    async def test_pan(self):
        """Testing zoom of ui.CanvasFrame"""
        window = await self.create_test_window()

        with window.frame:
            with ui.CanvasFrame(pan_x=64, pan_y=128):
                with ui.VStack(height=0):
                    # Simple text
                    ui.Label("Hello world")

                    # Word wrap
                    ui.Label(TEXT, word_wrap=True)

                    # Gray button
                    ui.Button(
                        "Button",
                        style={
                            "Button": {"background_color": 0xFF666666, "margin": 0, "padding": 4, "border_radius": 0}
                        },
                    )

        await self.finalize_test()

    async def test_space(self):
        """Testing transforming screen space to canvas space of ui.CanvasFrame"""
        window = await self.create_test_window()

        with window.frame:
            frame = ui.CanvasFrame(pan_x=512, pan_y=1024)
            with frame:
                placer = ui.Placer()
                with placer:
                    # Gray button
                    ui.Button(
                        "Button",
                        width=0,
                        height=0,
                        style={
                            "Button": {"background_color": 0xFF666666, "margin": 0, "padding": 4, "border_radius": 0}
                        },
                    )

        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        placer.offset_x = frame.screen_to_canvas_x(frame.screen_position_x + 128)
        placer.offset_y = frame.screen_to_canvas_y(frame.screen_position_y + 128)

        await self.finalize_test()

    async def test_navigation_pan(self):
        """Test how CanvasFrame interacts with mouse"""
        import omni.kit.ui_test as ui_test

        pan = [0, 0]

        def pan_changed(axis, value):
            pan[axis] = value

        window = await self.create_test_window(block_devices=False)

        with window.frame:
            canvas = ui.CanvasFrame(smooth_zoom=False)
            canvas.set_pan_key_shortcut(0, 0)
            canvas.set_pan_x_changed_fn(partial(pan_changed, 0))
            canvas.set_pan_y_changed_fn(partial(pan_changed, 1))
            with canvas:
                with ui.VStack(height=0):
                    # Simple text
                    ui.Label("Hello world")

                    # Word wrap
                    ui.Label(TEXT, word_wrap=True)

                    # Button
                    ui.Button("Button")

        ref = ui_test.WidgetRef(window.frame, "")

        for i in range(2):
            await omni.kit.app.get_app().next_update_async()

        await ui_test.emulate_mouse_move(ref.center)
        await ui_test.emulate_mouse_drag_and_drop(ref.center, ref.center * 0.8, human_delay_speed=1)

        for i in range(2):
            await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

        self.assertEqual(pan[0], -26)
        self.assertEqual(pan[1], -26)

    async def test_navigation_zoom(self):
        """Test how CanvasFrame interacts with mouse zoom"""
        import omni.kit.ui_test as ui_test

        window = await self.create_test_window(block_devices=False)
        with window.frame:
            canvas = ui.CanvasFrame(smooth_zoom=False)
            canvas.set_zoom_key_shortcut(1, 0)

        self.assertEqual(canvas.zoom, 1.0)
        ref = ui_test.WidgetRef(window.frame, "")

        for i in range(2):
            await omni.kit.app.get_app().next_update_async()

        await ui_test.emulate_mouse_move(ref.center)
        await ui_test.emulate_mouse_drag_and_drop(ref.center, ref.center * 0.5, right_click=True, human_delay_speed=1)

        for i in range(2):
            await omni.kit.app.get_app().next_update_async()

        # check the zoom is changed with the key_index press and right click
        self.assertAlmostEqual(canvas.zoom, 0.8950250148773193, 1)

        await self.finalize_test_no_image()

    async def test_zoom_with_limits(self):
        """Testing zoom is limited by the zoom_min and zoom_max"""
        window = await self.create_test_window()

        with window.frame:
            frame = ui.CanvasFrame(zoom=2.5, zoom_max=2.0, zoom_min=0.5)
            with frame:
                with ui.HStack():
                    ui.Spacer()
                    with ui.VStack():
                        ui.Spacer()
                        ui.Rectangle(width=50, height=50, style={"background_color": 0xFF000066})
                        ui.Spacer()
                    ui.Spacer()

        await omni.kit.app.get_app().next_update_async()
        await self.finalize_test()

        # check the zoom is limited by zoom_max = 2.0
        self.assertEqual(frame.screen_position_x, 2.0)
        self.assertEqual(frame.screen_position_y, 2.0)

    async def test_compatibility(self):
        """Testing zoom of ui.CanvasFrame"""
        window = await self.create_test_window()

        with window.frame:
            with ui.CanvasFrame(zoom=0.5, pan_x=64, pan_y=64, compatibility=False):
                with ui.VStack(height=0):
                    # Simple text
                    ui.Label("NVIDIA")

                    # Word wrap
                    ui.Label(TEXT, word_wrap=True)

                    # Gray button
                    ui.Button(
                        "Button",
                        style={
                            "Button": {"background_color": 0xFF666666, "margin": 0, "padding": 8, "border_radius": 0}
                        },
                    )

        await self.finalize_test()

    async def test_compatibility_text(self):
        """Testing zoom of ui.CanvasFrame"""
        window = await self.create_test_window()

        with window.frame:
            with ui.CanvasFrame(zoom=4.0, compatibility=False):
                with ui.VStack(height=0):
                    # Simple text
                    ui.Label("NVIDIA")

                    # Word wrap
                    ui.Label(TEXT, word_wrap=True)

                    # Gray button
                    ui.Button(
                        "Button",
                        style={
                            "Button": {"background_color": 0xFF666666, "margin": 0, "padding": 8, "border_radius": 0}
                        },
                    )

        # Make sure we only have one font cached
        for _ in range(2):
            await omni.kit.app.get_app().next_update_async()
        self.assertEqual(len(ui.Inspector.get_stored_font_atlases()), 1)

        await self.finalize_test()

    async def test_compatibility_clipping(self):
        window = await self.create_test_window()

        with window.frame:
            with ui.CanvasFrame(compatibility=0):
                with ui.Placer(draggable=1, width=50, height=50, offset_x=5, offset_y=50):
                    ui.Circle(
                        width=50,
                        height=50,
                        style={"background_color": ui.color.white},
                        arc=ui.Alignment.RIGHT_BOTTOM,
                    )

        await self.finalize_test()

    async def test_compatibility_clipping_2(self):
        # Create a backgroud window
        window = await self.create_test_window()

        # Create a new UI window
        window1 = ui.Window("clip 2", width=100, height=100, position_x=10, position_y=10)

        # Begin drawing contents inside window1
        with window1.frame:
            # Create a canvas frame with compatibility mode off
            canvas_frame = ui.CanvasFrame(compatibility=0, name="my")

            with canvas_frame:
                with ui.Frame():
                    with ui.ZStack(content_clipping=1):
                        # Add a blue rectangle inside the ZStack
                        ui.Rectangle(width=50, height=50, style={"background_color": ui.color.blue})
                        with ui.Placer(draggable=True, width=10, height=10):
                            ui.Rectangle(style={"background_color": 0xff123456})

        # Wait for the next update cycle of the application
        await omni.kit.app.get_app().next_update_async()

        # Pan the canvas frame to the specified coordinates
        canvas_frame.pan_x = 100
        canvas_frame.pan_y = 80

        # Finalize and clean up the test
        await self.finalize_test()

    async def test_compatibility_pan(self):
        """test pan is working when compatibility=0"""
        import omni.kit.ui_test as ui_test
        window = await self.create_test_window(block_devices=False)

        with window.frame:
            canvas = ui.CanvasFrame(compatibility=0)
            canvas.set_pan_key_shortcut(0, 0)
            with canvas:
                with ui.VStack(height=0):
                    # Simple text
                    ui.Label("Hello world")

                    # Word wrap
                    ui.Label(TEXT, word_wrap=True)

                    # Button
                    ui.Button("Button")

        ref = ui_test.WidgetRef(window.frame, "")
        await ui_test.wait_n_updates(2)
        await ui_test.emulate_mouse_move(ref.center)
        await ui_test.emulate_mouse_drag_and_drop(ref.center, ref.center * 0.8, human_delay_speed=1)
        await ui_test.wait_n_updates(2)
        await self.finalize_test()

    async def test_pan_no_leak(self):
        """test pan from one canvasFrame is not leaking to another canvasFrame """
        import omni.kit.ui_test as ui_test
        window = await self.create_test_window(block_devices=False, height=600)
        with window.frame:
            with ui.VStack():
                with ui.Frame(height=300):
                    canvas1 = ui.CanvasFrame(style={"background_color": omni.ui.color.red})
                    canvas1.set_pan_key_shortcut(1, 0)
                    with canvas1:
                        ui.Label("HELLO WORLD")
                with ui.Frame(height=300):
                    canvas2 = ui.CanvasFrame(style={"background_color": omni.ui.color.blue})
                    canvas2.set_pan_key_shortcut(1, 0)
                    with canvas2:
                        ui.Label("NVIDIA")

        ref1 = ui_test.WidgetRef(canvas1, "")
        ref2 = ui_test.WidgetRef(canvas2, "")
        await ui_test.wait_n_updates(2)
        # pan from the first canvas to second canvas, we should only see first canvas panned, but not the second one
        await ui_test.emulate_mouse_move(ref1.center)
        await ui_test.emulate_mouse_drag_and_drop(ref1.center, ref2.center, right_click=True, human_delay_speed=1)
        await ui_test.wait_n_updates(2)
        await self.finalize_test()

    async def test_zoom_no_leak(self):
        """test zoom from one canvasFrame is not leaking to another canvasFrame """
        import omni.kit.ui_test as ui_test
        from omni.kit.ui_test.vec2 import Vec2

        window = await self.create_test_window(block_devices=False, height=600)
        with window.frame:
            with ui.VStack():
                with ui.Frame(height=300):
                    canvas1 = ui.CanvasFrame(compatibility=0, style={"background_color": omni.ui.color.red})
                    canvas1.set_zoom_key_shortcut(1, 0)
                    with canvas1:
                        ui.Label("HELLO WORLD")
                with ui.Frame(height=300):
                    canvas2 = ui.CanvasFrame(compatibility=0, style={"background_color": omni.ui.color.blue})
                    canvas2.set_zoom_key_shortcut(1, 0)
                    with canvas2:
                        ui.Label("NVIDIA")

        ref1 = ui_test.WidgetRef(canvas1, "")
        ref2 = ui_test.WidgetRef(canvas2, "")

        await ui_test.wait_n_updates(2)
        # zoom from the second canvas to first canvas, we should only see second canvas zoomed, but not the first one
        await ui_test.emulate_mouse_move(ref2.center)
        await ui_test.emulate_mouse_drag_and_drop(ref2.center, ref1.center * 0.5, right_click=True, human_delay_speed=1)

        self.assertEqual(canvas1.zoom, 1.0)
        self.assertNotEqual(canvas2.zoom, 1.0)
        await self.finalize_test_no_image()

    async def __test_colorwidget(self, golden_img_name: str, compatibility: bool, delay: int = 3):
        import omni.kit.ui_test as ui_test
        from omni.kit.ui_test.vec2 import Vec2

        await self.create_test_area(width=600, height=500, block_devices=False)

        window = ui.Window("Example Window", width=250, height=250)
        with window.frame:
            with ui.CanvasFrame(compatibility=compatibility):
                with (color_frame := ui.Frame(width=30, height=30)):
                    ui.ColorWidget()

        app = omni.kit.app.get_app()
        for _ in range(delay):
            await app.next_update_async()

        ref_win = ui_test.WidgetRef(window.frame, "")
        ref = ui_test.WidgetRef(color_frame, "")

        if compatibility:
            positions = [
                ref.center,
                Vec2(370, 250),
                Vec2(10, 10)
            ]
        else:
            positions = [
                ref.center + ref_win.position,
                Vec2(370, 370),
                ref.center
            ]

        await ui_test.emulate_mouse_move_and_click(positions[0], human_delay_speed=delay)
        for _ in range(delay):
            await app.next_update_async()

        await ui_test.emulate_mouse_move_and_click(positions[1], human_delay_speed=delay)

        for _ in range(delay):
            await app.next_update_async()

        await self.finalize_test(golden_img_name=f"omni.ui.tests.test_canvasframe.TestCanvasFrame.{golden_img_name}")

        # Click off of the popup to make it disappear for the next test
        await ui_test.emulate_mouse_move_and_click(positions[2], human_delay_speed=delay)

    async def test_colorwidget_compatibility_off(self):
        """Test how CanvasFrame interacts with a colorwidget popup with compatibility off."""
        await self.__test_colorwidget(
            "test_colorwidget_compatibility_off.png",
            False
        )

    async def test_colorwidget_compatibility_on(self):
        """Test how CanvasFrame interacts with a colorwidget popup in compatibility mode."""
        await self.__test_colorwidget(
            "test_colorwidget_compatibility_on.png",
            True
        )

    async def test_callback_remove(self):
        self.called = 0
        def callback():
            self.called += 1
        window = ui.Window("tesst callback")
        with window.frame:
            canvas = ui.CanvasFrame()
            canvas.set_pan_x_changed_fn(lambda v: callback())
            canvas.set_pan_x_changed_fn(lambda v: callback())

            canvas.pan_x = 10
            canvas.pan_x = 20

        self.assertEqual(self.called , 4)

        # remove the callbacks
        canvas.set_pan_x_changed_fn(None)
        canvas.pan_x = 30
        # check the callback is not called, so it is still 4
        self.assertEqual(self.called , 4)