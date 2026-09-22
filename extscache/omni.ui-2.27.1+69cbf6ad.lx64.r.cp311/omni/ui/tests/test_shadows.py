## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
__all__ = ["TestShadows"]

import omni.kit.test
from .test_base import OmniUiTest
import omni.ui as ui
from omni.ui import color as cl


class TestShadows(OmniUiTest):
    """Testing shadow for ui.Shape"""

    async def test_rectangle(self):
        """Testing rectangle shadow"""
        window = await self.create_test_window()

        with window.frame:
            with ui.HStack():
                ui.Spacer()
                with ui.VStack():
                    ui.Spacer()
                    ui.Rectangle(
                        width=100,
                        height=100,
                        style={
                            "background_color": cl.transparent,
                            "shadow_flag": 1, "shadow_color": cl.blue,
                            "shadow_thickness": 20,
                            "shadow_offset_x": 3,
                            "shadow_offset_y": 3,
                            "border_width": 0,
                            "border_color": 0x22FFFF00,
                            "border_radius": 20,
                            "corner_flag": ui.CornerFlag.RIGHT})
                    ui.Spacer()
                ui.Spacer()

        await self.finalize_test()

    async def test_circle(self):
        """Testing circle shadow"""
        window = await self.create_test_window()

        with window.frame:
            with ui.HStack():
                ui.Spacer()
                with ui.VStack():
                    ui.Spacer()
                    ui.Circle(
                        width=60,
                        height=70,
                        alignment=ui.Alignment.RIGHT_BOTTOM,
                        style={
                            "background_color": cl.yellow,
                            "shadow_color": cl.blue,
                            "shadow_thickness": 20,
                            "shadow_offset_x": 6,
                            "shadow_offset_y": -6,
                            "border_width": 20,
                            "border_color": cl.blue})
                    ui.Spacer()
                ui.Spacer()

        await self.finalize_test()

    async def test_triangle(self):
        """Testing triangle shadow"""
        window = await self.create_test_window()

        with window.frame:
            with ui.HStack():
                ui.Spacer()
                with ui.VStack():
                    ui.Spacer()
                    ui.Triangle(
                        width=100,
                        height=80,
                        alignment=ui.Alignment.RIGHT_TOP,
                        style={
                            "background_color": cl.red,
                            "shadow_color": cl.blue,
                            "shadow_thickness": 10,
                            "shadow_offset_x": -8,
                            "shadow_offset_y": 5})
                    ui.Spacer()
                ui.Spacer()

        await self.finalize_test()

    async def test_line(self):
        """Testing line shadow"""
        window = await self.create_test_window()

        with window.frame:
            with ui.HStack():
                ui.Spacer()
                with ui.VStack():
                    ui.Spacer()
                    ui.Line(
                        alignment=ui.Alignment.LEFT,
                        style={
                            "color": cl.red,
                            "shadow_color": cl.green,
                            "shadow_thickness": 15,
                            "shadow_offset_x": 3,
                            "shadow_offset_y": 3,
                            "border_width": 10})
                    ui.Spacer()
                ui.Spacer()

        await self.finalize_test()

    async def test_ellipse(self):
        """Testing ellipse shadow"""
        window = await self.create_test_window()

        with window.frame:
            with ui.HStack():
                ui.Spacer(width=15)
                with ui.VStack():
                    ui.Spacer(height=35)
                    ui.Ellipse(
                        style={
                            "background_color": cl.green,
                            "shadow_color": cl.red,
                            "shadow_thickness": 20,
                            "shadow_offset_x": 5,
                            "shadow_offset_y": -5,
                            "border_width": 5,
                            "border_color": cl.blue})
                    ui.Spacer(height=35)
                ui.Spacer(width=15)

        await self.finalize_test()

    async def test_freeshape(self):
        """Testing freeshap with shadow"""
        window = await self.create_test_window()
        with window.frame:
            with ui.ZStack():
                # Four draggable rectangles that represent the control points
                with ui.Placer(draggable=True, offset_x=0, offset_y=0):
                    control1 = ui.Circle(width=10, height=10)
                with ui.Placer(draggable=True, offset_x=150, offset_y=150):
                    control2 = ui.Circle(width=10, height=10)

                # The rectangle that fits to the control points
                ui.FreeRectangle(
                    control1,
                    control2,
                    style={
                        "background_color": cl(0.6),
                        "border_color": cl(0.1),
                        "border_width": 1.0,
                        "border_radius": 8.0,
                        "shadow_color": cl.red,
                        "shadow_thickness": 20,
                        "shadow_offset_x": 5,
                        "shadow_offset_y": 5})
        await self.finalize_test()

    async def test_buttons(self):
        """Testing button with shadow"""
        window = await self.create_test_window()
        with window.frame:
            with ui.VStack(spacing=10):
                ui.Button(
                    "One",
                    height=30,
                    style={
                        "shadow_flag": 1,
                        "shadow_color": cl.blue,
                        "shadow_thickness": 13,
                        "shadow_offset_x": 3,
                        "shadow_offset_y": 3,
                        "border_width": 3,
                        "border_color": cl.green,
                        "border_radius": 3})
                ui.Button(
                    "Two",
                    height=30,
                    style={
                        "shadow_flag": 1,
                        "shadow_color": cl.red,
                        "shadow_thickness": 10,
                        "shadow_offset_x": 2,
                        "shadow_offset_y": 2,
                        "border_radius": 3})
                ui.Button(
                    "Three",
                    height=30,
                    style={
                        "shadow_flag": 1,
                        "shadow_color": cl.green,
                        "shadow_thickness": 5,
                        "shadow_offset_x": 4,
                        "shadow_offset_y": 4})
        await self.finalize_test()
