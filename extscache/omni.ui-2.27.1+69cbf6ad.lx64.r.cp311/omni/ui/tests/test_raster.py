## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import math
from collections import deque
from functools import partial
from .test_base import OmniUiTest
import omni.ui as ui
from omni.ui import color as cl
import omni.kit.app


class TestRaster(OmniUiTest):
    """Testing ui.Frame"""

    async def test_general(self):
        import omni.kit.ui_test as ui_test
        from carb.input import MouseEventType

        window = await self.create_test_window(block_devices=False)

        with window.frame:
            with ui.HStack():
                left_frame = ui.Frame(raster_policy=ui.RasterPolicy.AUTO)
                right_frame = ui.Frame(raster_policy=ui.RasterPolicy.AUTO)

        with left_frame:
            ui.Rectangle(style={"background_color": ui.color.grey})

        with right_frame:
            ui.Rectangle(style={"background_color": ui.color.grey})

        left_frame_ref = ui_test.WidgetRef(left_frame, "")
        right_frame_ref = ui_test.WidgetRef(right_frame, "")

        await ui_test.input.wait_n_updates_internal()
        await ui_test.input.emulate_mouse_move(right_frame_ref.center)
        await ui_test.input.wait_n_updates_internal()
        await ui_test.input.emulate_mouse_move(left_frame_ref.center)
        await ui_test.input.wait_n_updates_internal()

        await self.finalize_test()

    async def test_edit(self):
        import omni.kit.ui_test as ui_test
        from carb.input import MouseEventType

        window = await self.create_test_window(block_devices=False)

        with window.frame:
            with ui.HStack():
                left_frame = ui.Frame(raster_policy=ui.RasterPolicy.AUTO)
                right_frame = ui.Frame(raster_policy=ui.RasterPolicy.AUTO)

        with left_frame:
            ui.Rectangle(style={"background_color": ui.color.grey})

        with right_frame:
            with ui.ZStack():
                ui.Rectangle(style={"background_color": ui.color.grey})
                with ui.VStack():
                    ui.Spacer()
                    field = ui.StringField(height=0)
                    ui.Spacer()

        left_frame_ref = ui_test.WidgetRef(left_frame, "")
        field_ref = ui_test.WidgetRef(field, "")

        await ui_test.input.wait_n_updates_internal()
        await ui_test.input.emulate_mouse_move_and_click(field_ref.center)
        await ui_test.input.wait_n_updates_internal()
        await ui_test.input.emulate_mouse_move(left_frame_ref.center)
        await ui_test.input.wait_n_updates_internal()

        await self.finalize_test()

    async def test_dnd(self):
        import omni.kit.ui_test as ui_test
        from carb.input import MouseEventType

        window = await self.create_test_window(
            block_devices=False,
            window_flags=ui.WINDOW_FLAGS_NO_SCROLLBAR
            | ui.WINDOW_FLAGS_NO_TITLE_BAR
            | ui.WINDOW_FLAGS_NO_RESIZE
            | ui.WINDOW_FLAGS_NO_MOVE,
        )

        with window.frame:
            with ui.HStack():
                left_frame = ui.Frame(raster_policy=ui.RasterPolicy.AUTO)
                right_frame = ui.Frame(raster_policy=ui.RasterPolicy.AUTO)

        with left_frame:
            ui.Rectangle(style={"background_color": ui.color.grey})

        with right_frame:
            ui.Rectangle(style={"background_color": ui.color.grey})

        left_frame_ref = ui_test.WidgetRef(left_frame, "")
        right_frame_ref = ui_test.WidgetRef(right_frame, "")

        await ui_test.input.wait_n_updates_internal()
        await ui_test.input.emulate_mouse(MouseEventType.MOVE, left_frame_ref.center)
        await ui_test.input.emulate_mouse(MouseEventType.LEFT_BUTTON_DOWN)
        await ui_test.input.wait_n_updates_internal()
        await ui_test.input.emulate_mouse_slow_move(left_frame_ref.center, right_frame_ref.center)

        await self.finalize_test()

        await ui_test.input.emulate_mouse(MouseEventType.LEFT_BUTTON_UP)

    async def test_update(self):
        import omni.kit.ui_test as ui_test
        from carb.input import MouseEventType

        window = await self.create_test_window(block_devices=False)

        with window.frame:
            with ui.HStack():
                left_frame = ui.Frame(raster_policy=ui.RasterPolicy.AUTO)
                right_frame = ui.Frame(raster_policy=ui.RasterPolicy.AUTO)

        with left_frame:
            ui.Rectangle(style={"background_color": ui.color.grey})

        with right_frame:
            ui.Rectangle(style={"background_color": ui.color.grey})

        await ui_test.input.wait_n_updates_internal()
        await ui_test.input.emulate_mouse_move(ui_test.input.Vec2(0, 0))

        with right_frame:
            ui.Rectangle(style={"background_color": ui.color.beige})

        await ui_test.input.wait_n_updates_internal(update_count=4)

        await self.finalize_test()

    async def test_model(self):
        import omni.kit.ui_test as ui_test
        from carb.input import MouseEventType

        window = await self.create_test_window(block_devices=False)

        with window.frame:
            with ui.HStack():
                left_frame = ui.Frame(raster_policy=ui.RasterPolicy.AUTO)
                right_frame = ui.Frame(raster_policy=ui.RasterPolicy.AUTO)

        with left_frame:
            ui.Rectangle(style={"background_color": ui.color.grey})

        with right_frame:
            with ui.ZStack():
                ui.Rectangle(style={"background_color": ui.color.grey})
                with ui.VStack():
                    ui.Spacer()
                    field = ui.StringField(height=0)
                    ui.Spacer()

        await ui_test.input.wait_n_updates_internal()
        await ui_test.input.emulate_mouse_move(ui_test.input.Vec2(0, 0))

        field.model.as_string = "NVIDIA"

        await ui_test.input.wait_n_updates_internal(update_count=4)

        await self.finalize_test()

    async def test_on_demand(self):
        import omni.kit.ui_test as ui_test
        from carb.input import MouseEventType

        window = await self.create_test_window(block_devices=False)

        with window.frame:
            with ui.HStack():
                right_frame = ui.Frame(raster_policy=ui.RasterPolicy.ON_DEMAND)

        with right_frame:
            with ui.ZStack():
                ui.Rectangle(style={"background_color": ui.color.grey})
                with ui.VStack():
                    ui.Spacer()
                    field = ui.StringField(height=0)
                    ui.Spacer()

        right_frame_ref = ui_test.WidgetRef(right_frame, "")

        await ui_test.input.wait_n_updates_internal()
        await ui_test.input.emulate_mouse_move(right_frame_ref.center)

        field.model.as_string = "NVIDIA"

        await ui_test.input.wait_n_updates_internal(update_count=4)

        await self.finalize_test()

    async def test_on_demand_invalidate(self):
        import omni.kit.ui_test as ui_test
        from carb.input import MouseEventType

        window = await self.create_test_window(block_devices=False)

        with window.frame:
            with ui.HStack():
                right_frame = ui.Frame(raster_policy=ui.RasterPolicy.ON_DEMAND)

        with right_frame:
            with ui.ZStack():
                ui.Rectangle(style={"background_color": ui.color.grey})
                with ui.VStack():
                    ui.Spacer()
                    field = ui.StringField(height=0)
                    ui.Spacer()

        right_frame_ref = ui_test.WidgetRef(right_frame, "")

        await ui_test.input.wait_n_updates_internal()
        await ui_test.input.emulate_mouse_move(right_frame_ref.center)

        field.model.as_string = "NVIDIA"

        await ui_test.input.wait_n_updates_internal(update_count=4)

        right_frame.invalidate_raster()

        await ui_test.input.wait_n_updates_internal(update_count=4)

        await self.finalize_test()

    async def test_child_window(self):
        """Testing rasterization when mouse hovers child window"""
        import omni.kit.ui_test as ui_test

        window = await self.create_test_window(block_devices=False)

        small_window = ui.Window("small", width=100, height=100, position_x=0, position_y=0)

        with small_window.frame:
            with ui.VStack():
                with ui.Frame(raster_policy=ui.RasterPolicy.AUTO):
                    with ui.VStack():
                        ui.Label("NVIDIA")
                with ui.Frame(raster_policy=ui.RasterPolicy.AUTO):
                    with ui.VStack():
                        ui.Spacer()
                        combo = ui.ComboBox(1, "one", "two", "three", "four", height=0)

        await ui_test.input.wait_n_updates_internal(update_count=2)

        # Clicking the combo box in the small window
        combo_ref = ui_test.WidgetRef(combo, "")
        await ui_test.input.emulate_mouse_move_and_click(combo_ref.center)

        await ui_test.input.wait_n_updates_internal(update_count=2)

        # Moving the mouse over the combo box and outside the window
        await ui_test.input.emulate_mouse_move(ui_test.input.Vec2(combo_ref.center.x, combo_ref.center.y + 80))

        await ui_test.input.wait_n_updates_internal(update_count=6)

        await self.finalize_test()

    async def test_label(self):
        import omni.kit.ui_test as ui_test

        window = await self.create_test_window()

        with window.frame:
            with ui.HStack():
                left_frame = ui.Frame(raster_policy=ui.RasterPolicy.AUTO)
                right_frame = ui.Frame(raster_policy=ui.RasterPolicy.AUTO)

        with left_frame:
            l = ui.Label("Left")

        with right_frame:
            r = ui.Label("Right")

        await ui_test.input.wait_n_updates_internal()

        l.text = "NVIDIA"
        r.text = "Omniverse"

        await ui_test.input.wait_n_updates_internal(update_count=4)

        await self.finalize_test()

    async def test_canvasframe_lod(self):
        import omni.kit.ui_test as ui_test

        window = await self.create_test_window()

        with window.frame:
            with ui.Frame(raster_policy=ui.RasterPolicy.AUTO):
                canvas = ui.CanvasFrame()
                with canvas:
                    with ui.ZStack():
                        p1 = ui.Placer(stable_size=1, draggable=1)
                        with p1:
                            with ui.Frame(raster_policy=ui.RasterPolicy.AUTO):
                                ui.Rectangle(style={"background_color": ui.color.blue}, visible_min=0.5)
                        p2 = ui.Placer(stable_size=1, draggable=1)
                        with p2:
                            with ui.Frame(raster_policy=ui.RasterPolicy.AUTO):
                                ui.Rectangle(style={"background_color": ui.color.green}, visible_max=0.5)

        await ui_test.input.wait_n_updates_internal(update_count=4)
        canvas.zoom = 0.25

        await ui_test.input.wait_n_updates_internal(update_count=4)
        canvas.zoom = 1.0

        await ui_test.input.wait_n_updates_internal(update_count=4)
        p2.offset_x = 300
        p2.offset_y = 300

        await ui_test.input.wait_n_updates_internal(update_count=4)
        canvas.zoom = 0.25

        await ui_test.input.wait_n_updates_internal(update_count=4)

        await self.finalize_test()

    async def test_plot(self):
        import omni.kit.ui_test as ui_test
        window = await self.create_test_window(block_devices=False)
        with window.frame:
            with ui.Frame(raster_policy=ui.RasterPolicy.AUTO):
                data = deque([i / 100 for i in range(-100, 101)])
                plot = ui.Plot(ui.Type.LINE, -1.0, 1.0, *data, width=360, height=100, style={"color": cl.red})

        await ui_test.input.wait_n_updates_internal(update_count=4)
        data.rotate(10)
        plot.set_data(*data)
        await ui_test.input.wait_n_updates_internal(update_count=4)
        await self.finalize_test()
