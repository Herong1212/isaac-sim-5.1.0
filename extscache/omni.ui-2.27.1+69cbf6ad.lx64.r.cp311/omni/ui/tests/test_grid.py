## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
from unittest import skip
import omni.kit.test
import omni.ui as ui
from .test_base import OmniUiTest
import omni.kit.app


class TestGrid(OmniUiTest):
    """Testing ui.HGrid and ui.VGrid"""

    async def test_v_size(self):
        """Testing fixed width of ui.VGrid"""
        window = await self.create_test_window()

        with window.frame:
            with ui.VGrid(column_width=20, row_height=20):
                for i in range(200):
                    ui.Label(f"{i}", style={"color": 0xFFFFFFFF})

        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_v_number(self):
        """Testing varying width of ui.VGrid"""
        window = await self.create_test_window()

        with window.frame:
            with ui.VGrid(column_count=10, row_height=20):
                for i in range(200):
                    ui.Label(f"{i}", style={"color": 0xFFFFFFFF})

        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_v_length(self):
        """Testing varying height of ui.VGrid"""
        window = await self.create_test_window()

        with window.frame:
            with ui.VGrid(column_width=30):
                for i in range(200):
                    if i == 50:
                        ui.Label(f"{i}", style={"color": 0xFF0033FF, "font_size": 22}, alignment=ui.Alignment.CENTER)
                    else:
                        ui.Label(f"{i}", style={"color": 0xFFFFFFFF}, alignment=ui.Alignment.CENTER)

        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_length_resize(self):
        """Testing varying height of ui.VGrid"""
        window = await self.create_test_window()
        frames = []

        with window.frame:
            grid = ui.VGrid(column_width=64, row_height=16)
            with grid:
                for i in range(300):
                    with ui.Frame() as frame:
                        frames.append(frame)
                        with ui.HStack():
                            with ui.VStack():
                                ui.Spacer()
                                ui.Rectangle(style={"background_color": ui.color.white})
                            with ui.VStack():
                                ui.Rectangle(style={"background_color": ui.color.white})
                                ui.Spacer()

        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        for _, frame in enumerate(frames):
            self.assertEqual(frame.computed_width, 64)
            self.assertEqual(frame.computed_height, 16)

        grid.column_width = 16
        grid.row_height = 48

        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        for _, frame in enumerate(frames):
            self.assertEqual(frame.computed_width, 16)
            self.assertEqual(frame.computed_height, 48)

        await self.finalize_test()

    async def test_h_size(self):
        """Testing fixed height of ui.HGrid"""
        window = await self.create_test_window()

        with window.frame:
            with ui.HGrid(column_width=20, row_height=20):
                for i in range(200):
                    ui.Label(f"{i}", style={"color": 0xFFFFFFFF})

        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_h_number(self):
        """Testing varying height of ui.VGrid"""
        window = await self.create_test_window()

        with window.frame:
            with ui.HGrid(row_count=10, column_width=20):
                for i in range(200):
                    ui.Label(f"{i}", style={"color": 0xFFFFFFFF})

        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_h_length(self):
        """Testing varying height of ui.VGrid"""
        window = await self.create_test_window()

        with window.frame:
            with ui.HGrid(row_height=30):
                for i in range(200):
                    if i == 50:
                        ui.Label(
                            f"{i}",
                            style={"color": 0xFF0033FF, "font_size": 22, "margin": 3},
                            alignment=ui.Alignment.CENTER,
                        )
                    else:
                        ui.Label(f"{i}", style={"color": 0xFFFFFFFF, "margin": 3}, alignment=ui.Alignment.CENTER)

        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_v_inspector(self):
        """Testing how inspector opens nested frames"""
        window = await self.create_test_window()

        with window.frame:
            with ui.VGrid(column_width=30):
                for i in range(200):
                    ui.Frame(
                        build_fn=lambda i=i: ui.Label(f"{i}", style={"color": 0xFFFFFFFF}, alignment=ui.Alignment.CENTER)
                    )

        grid = ui.Inspector.get_children(window.frame)[0]
        self.assertIsInstance(grid, ui.VGrid)

        counter = 0

        frames = ui.Inspector.get_children(grid)
        for frame in frames:
            self.assertIsInstance(frame, ui.Frame)

            label = ui.Inspector.get_children(frame)[0]
            self.assertIsInstance(label, ui.Label)
            self.assertEqual(label.text, f"{counter}")
            counter += 1

        self.assertEqual(counter, 200)

        await self.finalize_test()

    @skip("TC crash on this test in linux")
    async def test_nested_grid(self):
        """Testing nested grid without setting height and width and not crash (OM-70184)"""
        window = await self.create_test_window()
        with window.frame:
            with ui.VGrid():
                with ui.CollapsableFrame("Main Frame"):
                    with ui.VGrid():
                        ui.CollapsableFrame("Sub Frame")

        await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()
