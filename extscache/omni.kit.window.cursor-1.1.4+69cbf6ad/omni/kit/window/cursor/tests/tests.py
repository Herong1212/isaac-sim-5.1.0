# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import carb.input
import carb.windowing
import omni.appwindow
import omni.kit.app
import omni.kit.test
import omni.kit.imgui
import omni.kit.window.cursor
import omni.kit.imgui_renderer
import omni.ui as ui


class TestCursorShape(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        app_window = omni.appwindow.get_default_app_window()
        self._mouse = app_window.get_mouse()
        self._app = omni.kit.app.get_app()
        self._cursor = omni.kit.window.cursor.get_main_window_cursor()
        self._input_provider = carb.input.acquire_input_provider()
        self._imgui = omni.kit.imgui.acquire_imgui()
        self._windowing = carb.windowing.acquire_windowing_interface()
        self._os_window = app_window.get_window()
        self._imgui_renderer = omni.kit.imgui_renderer.acquire_imgui_renderer_interface()
        await self._build_test_windows()

    async def tearDown(self):
        self._os_window = None
        self._windowing = None
        self._imgui = None
        self._window = None
        self._dock_window_1 = None
        self._dock_window_2 = None
        self._imgui_renderer = None

    async def test_cursor_shape(self):
        main_dockspace = ui.Workspace.get_window("DockSpace")

        width = main_dockspace.width
        height = main_dockspace.height
        await self._wait()
        
        await self._move_and_test_cursor_shape((width / 2, 1), omni.kit.imgui.MouseCursor.ARROW)

        # Put on StringField and test IBeam shape
        await self._move_and_test_cursor_shape((width / 2, height / 4), omni.kit.imgui.MouseCursor.TEXT_INPUT)

        # Put on vertical split and test HORIZONTAL_RESIZE
        await self._move_and_test_cursor_shape(
            (width / 2 + 1, height * 3 / 4),
            omni.kit.imgui.MouseCursor.RESIZE_EW,
        )

        # Put on horizontal split and test VERTICAL_RESIZE
        await self._move_and_test_cursor_shape(
            (width * 3 / 4, height / 2 + 1),
            omni.kit.imgui.MouseCursor.RESIZE_NS,
        )

        await self._wait()

        # test override_cursor_shape_extend and get_cursor_shape_override_extend
        test_extend_shapes = [
            "IBeam",
            "Grab_close",
            "Crosshair",
            "Grab_open",
        ]

        for cursor_shape in test_extend_shapes:
            self._cursor.override_cursor_shape_extend(cursor_shape)
            await self._wait(100)
            cur_cursor = self._cursor.get_cursor_shape_override_extend()
            self.assertEqual(cur_cursor, cursor_shape)

        # test override_cursor_shape and get_cursor_shape_override
        test_shapes = [
            carb.windowing.CursorStandardShape.CROSSHAIR,
            carb.windowing.CursorStandardShape.IBEAM,
        ]

        for cursor_shape in test_shapes:
            self._cursor.override_cursor_shape(cursor_shape)
            await self._wait(100)
            cur_cursor = self._cursor.get_cursor_shape_override()
            self.assertEqual(cur_cursor, cursor_shape)

        all_shapes = self._imgui_renderer.get_all_cursor_shape_names()
        print(all_shapes)

        self._cursor.clear_overridden_cursor_shape()
        await self._wait()

    async def _move_and_test_cursor_shape(self, pos, cursor: omni.kit.imgui.MouseCursor):
        # Available options:
        # omni.kit.imgui.MouseCursor.ARROW: carb.windowing.CursorStandardShape.ARROW,
        # omni.kit.imgui.MouseCursor.TEXT_INPUT: carb.windowing.CursorStandardShape.IBEAM,
        # omni.kit.imgui.MouseCursor.RESIZE_NS: carb.windowing.CursorStandardShape.VERTICAL_RESIZE,
        # omni.kit.imgui.MouseCursor.RESIZE_EW: carb.windowing.CursorStandardShape.HORIZONTAL_RESIZE,
        # omni.kit.imgui.MouseCursor.HAND: carb.windowing.CursorStandardShape.HAND,
        # omni.kit.imgui.MouseCursor.CROSSHAIR: carb.windowing.CursorStandardShape.CROSSHAIR,

        self._input_provider.buffer_mouse_event(self._mouse, carb.input.MouseEventType.MOVE, pos, 0, pos)
        self._windowing.set_cursor_position(self._os_window, carb.Int2(*[int(p) for p in pos]))

        await self._wait()
        imgui_cursor = self._imgui.get_mouse_cursor()
        self.assertEqual(cursor, imgui_cursor, f"Expect {cursor} but got {imgui_cursor}")




    # build a dockspace with windows/widgets to test various cursor shape from imgui
    async def _build_test_windows(self):
        import omni.ui as ui

        self._window = ui.Window("CursorShapeTest")
        with self._window.frame:
            with ui.ZStack():
                with ui.Placer(offset_x=0, offset_y=10):
                    ui.StringField()

        self._dock_window_1 = ui.Window("DockWindow1")
        self._dock_window_2 = ui.Window("DockWindow2")

        await self._app.next_update_async()

        main_dockspace = ui.Workspace.get_window("DockSpace")
        window_handle = ui.Workspace.get_window("CursorShapeTest")
        dock_window_handle1 = ui.Workspace.get_window("DockWindow1")
        dock_window_handle2 = ui.Workspace.get_window("DockWindow2")

        window_handle.dock_in(main_dockspace, ui.DockPosition.SAME)
        dock_window_handle1.dock_in(window_handle, ui.DockPosition.BOTTOM, 0.5)
        dock_window_handle2.dock_in(dock_window_handle1, ui.DockPosition.RIGHT, 0.5)

    async def _wait(self, num=8):
        for i in range(num):
            await self._app.next_update_async()