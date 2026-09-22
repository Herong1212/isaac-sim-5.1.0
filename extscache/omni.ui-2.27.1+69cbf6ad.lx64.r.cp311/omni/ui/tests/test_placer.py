## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
from .test_base import OmniUiTest
import omni.ui as ui
import omni.kit.app


RECT_SIZE = 10
RECT_STYLE = {"background_color": 0xFFFFFFFF}
RECT_TRANSPARENT_STYLE = {"background_color": 0x66FFFFFF, "border_color": 0xFFFFFFFF, "border_width": 1}


class TestPlacer(OmniUiTest):
    """Testing ui.Placer"""

    async def test_general(self):
        """Testing general properties of ui.Placer"""
        window = await self.create_test_window()

        with window.frame:
            with ui.ZStack():
                with ui.Placer(offset_x=10, offset_y=10):
                    ui.Rectangle(width=RECT_SIZE, height=RECT_SIZE, style=RECT_STYLE)
                with ui.Placer(offset_x=90, offset_y=10):
                    ui.Rectangle(width=RECT_SIZE, height=RECT_SIZE, style=RECT_STYLE)
                with ui.Placer(offset_x=90, offset_y=90):
                    ui.Rectangle(width=RECT_SIZE, height=RECT_SIZE, style=RECT_STYLE)
                with ui.Placer(offset_x=10, offset_y=90):
                    ui.Rectangle(width=RECT_SIZE, height=RECT_SIZE, style=RECT_STYLE)

        await self.finalize_test()

    async def test_percents(self):
        """Testing ability to offset in percents of ui.Placer"""
        window = await self.create_test_window()

        with window.frame:
            with ui.ZStack():
                with ui.Placer(offset_x=ui.Percent(10), offset_y=ui.Percent(10)):
                    ui.Rectangle(width=RECT_SIZE, height=RECT_SIZE, style=RECT_STYLE)
                with ui.Placer(offset_x=ui.Percent(90), offset_y=ui.Percent(10)):
                    ui.Rectangle(width=RECT_SIZE, height=RECT_SIZE, style=RECT_STYLE)
                with ui.Placer(offset_x=ui.Percent(90), offset_y=ui.Percent(90)):
                    ui.Rectangle(width=RECT_SIZE, height=RECT_SIZE, style=RECT_STYLE)
                with ui.Placer(offset_x=ui.Percent(10), offset_y=ui.Percent(90)):
                    ui.Rectangle(width=RECT_SIZE, height=RECT_SIZE, style=RECT_STYLE)

        await self.finalize_test()

    async def test_child_percents(self):
        """Testing ability to offset in percents of ui.Placer"""
        window = await self.create_test_window()

        with window.frame:
            with ui.ZStack():
                with ui.Placer(offset_x=ui.Percent(10), offset_y=ui.Percent(10)):
                    ui.Rectangle(width=ui.Percent(80), height=ui.Percent(80), style=RECT_TRANSPARENT_STYLE)
                with ui.Placer(offset_x=ui.Percent(50), offset_y=ui.Percent(50)):
                    ui.Rectangle(width=ui.Percent(50), height=ui.Percent(50), style=RECT_TRANSPARENT_STYLE)

        await self.finalize_test()

    async def test_resize(self):
        window = await self.create_test_window()

        with window.frame:
            placer = ui.Placer(width=200)
            with placer:
                ui.Rectangle(height=100, style={"background_color": omni.ui.color.red})

        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        placer.width = ui.Percent(5)

        await self.finalize_test()

    async def test_splitter_resize_cursor(self):
        window = await self.create_test_window()
        window.focus()

        from carb.input import DeviceType, MouseEventType
        omni.appwindow.get_default_app_window().set_input_blocking_state(DeviceType.MOUSE, False)

        with window.frame:
            with ui.HStack():
                left_frame = ui.Frame()
                with left_frame:
                    ui.Button("Foo")
                placer = ui.Placer(draggable=True, drag_axis=ui.Axis.X)
                with placer:
                    rect = ui.Rectangle(width=10, style={"background_color": omni.ui.color.red})
                with ui.VStack():
                    right_frame = ui.Frame()
                    with right_frame:
                        ui.Label("Bar")

        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        import omni.kit.ui_test as ui_test
        from omni.kit.ui_test.input import emulate_mouse
        # Test hover
        ref = ui_test.WidgetRef(rect, "")
        start_pos = ref.center
        end_pos = ref.position
        await ui_test.emulate_mouse_move(start_pos)
        await ui_test.human_delay(10)

        import omni.kit.imgui as imgui
        imgui_inst = imgui.acquire_imgui()
        self.assertEqual(imgui_inst.get_mouse_cursor(), imgui.MouseCursor.RESIZE_EW)

        # Test dragging
        await emulate_mouse(MouseEventType.MOVE, start_pos)
        await emulate_mouse(MouseEventType.LEFT_BUTTON_DOWN)
        await ui_test.human_delay(4)
        step = (end_pos - start_pos) / 8
        for i in range(0, 9):
            await emulate_mouse(MouseEventType.MOVE, start_pos + step * i)
            await ui_test.human_delay(4)
            self.assertEqual(imgui_inst.get_mouse_cursor(), imgui.MouseCursor.RESIZE_EW)
        await ui_test.human_delay(4)
        await emulate_mouse(MouseEventType.LEFT_BUTTON_UP)
        await ui_test.human_delay(4)

        await self.finalize_test_no_image() 