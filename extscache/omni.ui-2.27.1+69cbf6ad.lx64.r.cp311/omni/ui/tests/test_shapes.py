## Copyright (c) 2018-2023, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
__all__ = ["TestShapes"]

import asyncio
from functools import partial

import omni.kit.test
from .test_base import OmniUiTest
import omni.ui as ui
from omni.ui import color as cl


class TestShapes(OmniUiTest):
    """Testing ui.Shape"""

    async def test_offsetline(self):
        """Testing general properties of ui.OffsetLine"""
        window = await self.create_test_window()

        with window.frame:
            with ui.ZStack(
                style={
                    "Rectangle": {"background_color": cl(0, 0, 0, 0), "border_color": cl.white, "border_width": 1},
                    "OffsetLine": {"color": cl.white, "border_width": 1},
                }
            ):
                with ui.VStack():
                    with ui.HStack(height=32):
                        rect1 = ui.Rectangle(width=32)
                        ui.Spacer()
                    ui.Spacer()
                    with ui.HStack(height=32):
                        ui.Spacer()
                        rect2 = ui.Rectangle(width=32)

                ui.OffsetLine(
                    rect1,
                    rect2,
                    alignment=ui.Alignment.UNDEFINED,
                    begin_arrow_type=ui.ArrowType.ARROW,
                    offset=7,
                    bound_offset=20,
                )
                ui.OffsetLine(
                    rect2,
                    rect1,
                    alignment=ui.Alignment.UNDEFINED,
                    begin_arrow_type=ui.ArrowType.ARROW,
                    offset=7,
                    bound_offset=20,
                )

        await self.finalize_test()

    async def test_bezier(self):
        import omni.kit.ui_test as ui_test
        from omni.kit.ui_test import Vec2

        window = await self.create_test_window(width=300, height=200, block_devices=False)
        with window.frame:
            with ui.VStack():
                style = {"color": cl.red, "border_width": 2}
                ui.Spacer()
                with ui.Frame(height=150, style=style):
                    curve = ui.BezierCurve()
                ui.Spacer()

        def _on_curve_clicked(c):
            style = {"color": cl.blue, "border_width": 2}
            c.style= style

        curve.set_mouse_released_fn(lambda x, y, button, modifier, c=curve: _on_curve_clicked(c))

        await omni.kit.app.get_app().next_update_async()
        await ui_test.emulate_mouse_move_and_click(Vec2(150, 100))
        await omni.kit.app.get_app().next_update_async()
        await self.finalize_test()

    async def test_freebezier(self):
        """Testing general properties of ui.OffsetLine"""
        window = await self.create_test_window()

        with window.frame:
            with ui.ZStack(
                style={
                    "Rectangle": {"background_color": cl(0, 0, 0, 0), "border_color": cl.white, "border_width": 1},
                    "FreeBezierCurve": {"color": cl.white, "border_width": 1},
                }
            ):
                with ui.VStack():
                    with ui.HStack(height=32):
                        rect1 = ui.Rectangle(width=32)
                        ui.Spacer()
                    ui.Spacer()
                    with ui.HStack(height=32):
                        ui.Spacer()
                        rect2 = ui.Rectangle(width=32)

                # Default tangents
                ui.FreeBezierCurve(rect1, rect2, style={"color": cl.chartreuse})

                # 0 tangents
                ui.FreeBezierCurve(
                    rect1,
                    rect2,
                    start_tangent_width=0,
                    start_tangent_height=0,
                    end_tangent_width=0,
                    end_tangent_height=0,
                    style={"color": cl.darkslategrey},
                )

                # Fraction tangents
                ui.FreeBezierCurve(
                    rect1,
                    rect2,
                    start_tangent_width=0,
                    start_tangent_height=ui.Fraction(2),
                    end_tangent_width=0,
                    end_tangent_height=ui.Fraction(-2),
                    style={"color": cl.dodgerblue},
                )

                # Percent tangents
                ui.FreeBezierCurve(
                    rect1,
                    rect2,
                    start_tangent_width=0,
                    start_tangent_height=ui.Percent(100),
                    end_tangent_width=0,
                    end_tangent_height=ui.Percent(-100),
                    style={"color": cl.peru},
                )

                # Super big tangents
                ui.FreeBezierCurve(
                    rect1,
                    rect2,
                    start_tangent_width=0,
                    start_tangent_height=1e8,
                    end_tangent_width=0,
                    end_tangent_height=-1e8,
                    style={"color": cl.indianred},
                )

        await self.finalize_test()

    async def test_freebezier_anchors(self):
        """Testing general properties of Anchors on BezierCurves"""
        import omni.kit.ui_test as ui_test
        from omni.kit.ui_test import Vec2

        window = await self.create_test_window(block_devices=False, window_flags=ui.WINDOW_FLAGS_NO_MOVE | ui.WINDOW_FLAGS_NO_SCROLLBAR)

        ANCHOR_ALIGNMENT = ui.Alignment.CENTER

        def drag_anchor(curve, x: float, y: float, button, mod):
            if curve:
                t = curve.get_closest_parametric_position(x, y)
                curve.anchor_position = t

        def remove_anchor(curve, x: float, y: float, button, mod):
            async def wait_and_turn_off_anchor_frame():
                await omni.kit.app.get_app().next_update_async()
                curve.set_anchor_fn(None)

            # rt-click to remove
            if button == 1:
                asyncio.ensure_future(wait_and_turn_off_anchor_frame())

        def bound_anchor(curve=None):

            with ui.VStack(content_clipping=1,
                           style={"margin": 0}):
                with ui.VStack(style={"margin_height": 50}):
                    dot = ui.Circle(
                        # Make sure this alignment is the same as the anchor_alignment
                        # or this circle won't stick to the curve correctly.
                        alignment=ANCHOR_ALIGNMENT,
                        radius=6,
                        style_type_name_override="Anchor",
                        size_policy=ui.CircleSizePolicy.FIXED,
                    )
                    dot.set_mouse_pressed_fn(partial(remove_anchor, curve))
                    dot.set_mouse_moved_fn(partial(drag_anchor, curve))

        with window.frame:
            with ui.ZStack(
                style={
                    "Rectangle": {"background_color": cl(0, 0, 0, 0), "border_color": cl.white, "border_width": 1},
                    "FreeBezierCurve": {"color": cl.white, "border_width": 1},
                    "Anchor": {"background_color": cl.orange},
                }
            ):
                with ui.VStack():
                    with ui.HStack(height=32):
                        rect1 = ui.Rectangle(width=32)
                        ui.Spacer()
                    ui.Spacer()
                    with ui.HStack(height=32):
                        ui.Spacer()
                        rect2 = ui.Rectangle(width=32)

                ref = ui_test.WidgetRef(window.frame, "")

                # Default tangents
                curve1 = ui.FreeBezierCurve(rect1, rect2, style={"color": cl.chartreuse},
                                            anchor_alignment=ANCHOR_ALIGNMENT)
                curve1.set_anchor_fn(partial(bound_anchor, curve1))

                for _ in range(10):
                    await omni.kit.app.get_app().next_update_async()

                # drag the anchor decoration
                await ui_test.emulate_mouse_move(ref.center)
                await ui_test.emulate_mouse_drag_and_drop(ref.center, ref.center * 0.6, human_delay_speed=1)

                # 0 tangents
                curve2 = ui.FreeBezierCurve(
                    rect1,
                    rect2,
                    start_tangent_width=0,
                    start_tangent_height=0,
                    end_tangent_width=0,
                    end_tangent_height=0,
                    style={"color": cl.darkslategrey},
                    anchor_alignment=ANCHOR_ALIGNMENT,
                    anchor_position=0.25,
                )
                curve2.set_anchor_fn(partial(bound_anchor, curve2))

                for _ in range(10):
                    await omni.kit.app.get_app().next_update_async()

                # remove the anchor decoration
                await ui_test.emulate_mouse_move_and_click(Vec2(50, 67), right_click=True)

                # Fraction tangents
                curve3 = ui.FreeBezierCurve(
                    rect1,
                    rect2,
                    start_tangent_width=0,
                    start_tangent_height=ui.Fraction(2),
                    end_tangent_width=0,
                    end_tangent_height=ui.Fraction(-2),
                    style={"color": cl.dodgerblue},
                    anchor_alignment=ANCHOR_ALIGNMENT,
                    anchor_position=0.75,
                )
                curve3.set_anchor_fn(partial(bound_anchor, curve3))

                for _ in range(10):
                    await omni.kit.app.get_app().next_update_async()

                # Percent tangents without an anchor_fn
                curve4 = ui.FreeBezierCurve(
                    rect1,
                    rect2,
                    start_tangent_width=0,
                    start_tangent_height=ui.Percent(100),
                    end_tangent_width=0,
                    end_tangent_height=ui.Percent(-100),
                    style={"color": cl.peru},
                )

                for _ in range(50):
                    await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_freeline_anchors(self):
        """Testing general properties of Anchors on Lines"""
        import omni.kit.ui_test as ui_test
        from omni.kit.ui_test import Vec2

        window = await self.create_test_window(block_devices=False, window_flags=ui.WINDOW_FLAGS_NO_MOVE | ui.WINDOW_FLAGS_NO_SCROLLBAR)

        ANCHOR_ALIGNMENT = ui.Alignment.CENTER

        def drag_anchor(curve, x: float, y: float, button, mod):
            if curve:
                t = curve.get_closest_parametric_position(x, y)
                curve.anchor_position = t

        def remove_anchor(curve, x: float, y: float, button, mod):
            async def wait_and_turn_off_anchor_frame():
                await omni.kit.app.get_app().next_update_async()
                curve.set_anchor_fn(None)

            # rt-click to remove
            if button == 1:
                asyncio.ensure_future(wait_and_turn_off_anchor_frame())

        def bound_anchor(curve=None):

            with ui.VStack(content_clipping=1,
                           style={"margin": 0}):
                with ui.VStack(style={"margin_height": 50}):
                    dot = ui.Circle(
                        # Make sure this alignment is the same as the anchor_alignment
                        # or this circle won't stick to the curve correctly.
                        alignment=ANCHOR_ALIGNMENT,
                        radius=6,
                        style_type_name_override="Anchor",
                        size_policy=ui.CircleSizePolicy.FIXED,
                    )
                    dot.set_mouse_pressed_fn(partial(remove_anchor, curve))
                    dot.set_mouse_moved_fn(partial(drag_anchor, curve))

        with window.frame:
            with ui.ZStack(
                style={
                    "Rectangle": {"background_color": cl(0, 0, 0, 0), "border_color": cl.white, "border_width": 1},
                    "FreeLine": {"color": cl.white, "border_width": 1},
                    "Anchor": {"background_color": cl.orange},
                }
            ):
                with ui.VStack():
                    with ui.HStack(height=32):
                        rect1 = ui.Rectangle(width=32)
                        ui.Spacer()
                    ui.Spacer()
                    with ui.HStack(height=32):
                        ui.Spacer()
                        rect2 = ui.Rectangle(width=32)

                ref = ui_test.WidgetRef(window.frame, "")

                line1 = ui.FreeLine(
                    rect1,
                    rect2,
                    alignment=ui.Alignment.UNDEFINED,
                    style={"color": cl.chartreuse},
                    anchor_alignment=ANCHOR_ALIGNMENT,
                    anchor_position=.5,
                )
                line1.set_anchor_fn(partial(bound_anchor, line1))

                for _ in range(10):
                    await omni.kit.app.get_app().next_update_async()

                await ui_test.emulate_mouse_move(ref.center)
                await ui_test.emulate_mouse_drag_and_drop(ref.center, Vec2(100, 30), human_delay_speed=1)

                line2 = ui.Line(alignment=ui.Alignment.V_CENTER,
                        width=100,
                        anchor_alignment=ANCHOR_ALIGNMENT,
                        anchor_position=.25,
                        style={"color": cl.blue},)
                line2.set_anchor_fn(partial(bound_anchor, line2))

                for _ in range(10):
                    await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_lines_no_anchors(self):
        """Testing general properties of Anchors on Lines"""
        import omni.kit.ui_test as ui_test
        window = await self.create_test_window(block_devices=False, window_flags=ui.WINDOW_FLAGS_NO_MOVE | ui.WINDOW_FLAGS_NO_SCROLLBAR)

        with window.frame:
            with ui.ZStack(
                style={
                    "Rectangle": {"background_color": cl(0, 0, 1, 0)},
                    "Circle": {"background_color": cl(0, 0, 0, 0), "border_color": cl.white, "border_width": 1},
                    "Line": {"color": cl.white, "border_width": 1},
                }
            ):
                ui.Rectangle()
                with ui.VStack():
                    with ui.HStack(height=32):
                        rect1 = ui.Circle(width=32)
                        ui.Spacer()
                    ui.Spacer()
                    with ui.HStack(height=32):
                        ui.Spacer()
                        rect2 = ui.Circle(width=32)

                ui.FreeLine(
                    rect1,
                    rect2,
                    alignment=ui.Alignment.UNDEFINED,
                    style={"color": cl.chartreuse},
                )

                ui.Line(style={"color": cl.blue},)

                for _ in range(5):
                    await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_freeshape_hover(self):
        """Testing freeshape mouse hover"""

        import omni.kit.ui_test as ui_test

        is_hovered = False

        def mouse_hover(hovered):
            nonlocal is_hovered
            is_hovered = hovered

        min = ui_test.Vec2(50, 50)
        max = ui_test.Vec2(150, 150)
        window = await self.create_test_window(block_devices=False)
        with window.frame:
            with ui.ZStack():
                # Four draggable rectangles that represent the control points
                with ui.Placer(draggable=True, offset_x=min.x, offset_y=min.y):
                    control1 = ui.Circle(width=10, height=10)
                with ui.Placer(draggable=True, offset_x=max.x, offset_y=max.y):
                    control2 = ui.Circle(width=10, height=10)

                # The rectangle that fits to the control points
                shape = ui.FreeRectangle(
                    control1,
                    control2,
                    mouse_hovered_fn=mouse_hover,
                )

        try:
            await ui_test.human_delay()
            self.assertFalse(is_hovered)
            shape_ref = ui_test.WidgetRef(shape, "")
            await ui_test.emulate_mouse_move(shape_ref.position + min / 2)
            await ui_test.human_delay()
            self.assertFalse(is_hovered) # top-left outside shape offset
            await ui_test.emulate_mouse_move(shape_ref.position + min + (max-min) / 2)
            await ui_test.human_delay()
            self.assertTrue(is_hovered) # center of shape
            await ui_test.emulate_mouse_move(shape_ref.position + max + min / 2)
            await ui_test.human_delay()
            self.assertFalse(is_hovered) # bottom-right outside shape max

        finally:
            await self.finalize_test_no_image()
