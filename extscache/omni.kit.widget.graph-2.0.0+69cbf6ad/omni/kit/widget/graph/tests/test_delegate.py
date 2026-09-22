## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
from omni.kit.widget.graph.graph_node_delegate import GraphNodeDelegate
from omni.kit.widget.graph.graph_view import GraphView
from omni.ui.tests.test_base import OmniUiTest
from .test_graph import Model, connections
import omni.kit.app
import omni.kit.ui_test as ui_test
from omni.kit.ui_test.input import emulate_keyboard, human_delay, emulate_mouse_move, emulate_mouse, emulate_mouse_slow_move, emulate_mouse_drag_and_drop
import carb.input
from carb.input import KeyboardInput, KeyboardEventType, MouseEventType


style = GraphNodeDelegate.get_style()
# Don't use the image because the image scaling looks different in editor and kit-mini
style["Graph.Node.Footer.Image"]["image_url"] = ""
style["Graph.Node.Header.Collapse"]["image_url"] = ""
style["Graph.Node.Header.Collapse::Minimized"]["image_url"] = ""
style["Graph.Node.Header.Collapse::Closed"]["image_url"] = ""


class TestDelegate(OmniUiTest):
    async def test_general(self):
        """Testing general properties of the GraphView default delegate"""
        window = await self.create_test_window(768, 512)

        with window.frame:
            delegate = GraphNodeDelegate()
            model = Model()
            graph_view = GraphView(model=model, delegate=delegate, style=style, pan_x=600, pan_y=170)

        # Two frames because the first frame is to draw, the second frame is to auto-layout.
        for i in range(3):
            await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_zoom(self):
        """Testing zooming of the GraphView default delegate"""
        window = await self.create_test_window(384, 256)

        with window.frame:
            delegate = GraphNodeDelegate()
            model = Model()
            graph_view = GraphView(model=model, delegate=delegate, style=style, zoom=0.5, pan_x=300, pan_y=85)

        # Two frames because the first frame is to draw, the second frame is to auto-layout.
        for i in range(3):
            await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_focus(self):
        """Testing focusing of the GraphView default delegate"""
        window = await self.create_test_window(768, 512)

        with window.frame:
            delegate = GraphNodeDelegate()
            model = Model()
            graph_view = GraphView(model=model, delegate=delegate, style=style)

        # Two frames because the first frame is to draw, the second frame is to auto-layout.
        for i in range(3):
            await omni.kit.app.get_app().next_update_async()

        graph_view.focus_on_nodes()

        for i in range(2):
            await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_rewire(self):
        """Testing moving a wired connection from one port to another"""
        window = await self.create_test_window(768, 512, block_devices=False)

        global connections
        del connections["First.color2"]

        with window.frame:
            delegate = GraphNodeDelegate()
            model = Model()
            graph_view = GraphView(model=model, delegate=delegate, style=style)

        # Two frames because the first frame is to draw, the second frame is to auto-layout.
        for i in range(3):
            await omni.kit.app.get_app().next_update_async()

        graph_view.focus_on_nodes()
        await human_delay(2)

        human_delay_speed = 5
        # Move to the output port for a moment
        await ui_test.emulate_mouse_move(ui_test.Vec2(452, 235), human_delay_speed=5)
        await human_delay(human_delay_speed)
        await emulate_keyboard(KeyboardEventType.KEY_PRESS, KeyboardInput.LEFT_CONTROL, modifier=carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL)
        await human_delay(human_delay_speed)
        # Drag from output port to another output port to rewire
        await emulate_mouse_drag_and_drop(ui_test.Vec2(452, 235), ui_test.Vec2(145, 250), human_delay_speed=5)
        await human_delay(human_delay_speed)
        await ui_test.emulate_mouse_move(ui_test.Vec2(620, 235), human_delay_speed=5)
        await human_delay(human_delay_speed)
        # Drag from input port to another input port to rewire
        await emulate_mouse_drag_and_drop(ui_test.Vec2(620, 235), ui_test.Vec2(620, 250), human_delay_speed=5)
        await human_delay(human_delay_speed)
        # Note, using modifier=carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL on the release side was keeping CTRL on still, in some way
        await emulate_keyboard(KeyboardEventType.KEY_RELEASE, KeyboardInput.LEFT_CONTROL)

        await human_delay(10)

        # Restore connections for other tests
        connections["First.color1"] = ["Second.out"]
        connections["First.color2"] = ["Third.outcome"]
        await self.finalize_test()

    async def test_reverse_wire(self):
        """Testing wiring a connection from the input to output side"""
        window = await self.create_test_window(768, 512, block_devices=False)

        global connections
        del connections["First.color2"]

        with window.frame:
            delegate = GraphNodeDelegate()
            model = Model()
            graph_view = GraphView(model=model, delegate=delegate, style=style)

        # Two frames because the first frame is to draw, the second frame is to auto-layout.
        for i in range(3):
            await omni.kit.app.get_app().next_update_async()

        graph_view.focus_on_nodes()
        await human_delay(2)

        human_delay_speed = 5
        # Move to the output port for a moment
        await ui_test.emulate_mouse_move(ui_test.Vec2(620, 247), human_delay_speed=5)
        await human_delay(human_delay_speed)
        # Drag from input port to an output port
        await human_delay(human_delay_speed)
        await emulate_mouse_drag_and_drop(ui_test.Vec2(620, 247), ui_test.Vec2(145, 250), human_delay_speed=5)

        await human_delay(10)

        # No need to restore connections, as they end up the same as they started anyway
        await self.finalize_test()

    async def test_wire_in_progress(self):
        """Testing dragging a connection from one port towards another but not connecting yet."""
        window = await self.create_test_window(768, 512, block_devices=False)

        global connections
        del connections["First.color2"]

        with window.frame:
            delegate = GraphNodeDelegate()
            model = Model()
            graph_view = GraphView(model=model, delegate=delegate, style=style)

        # Two frames because the first frame is to draw, the second frame is to auto-layout.
        for i in range(10):
            await omni.kit.app.get_app().next_update_async()

        graph_view.focus_on_nodes()
        await human_delay(10)

        human_delay_speed = 10
        # Do most of a drag and drop manually (just delay the drop until after capturing golden img)
        start_pos = ui_test.Vec2(620, 249)
        end_pos = ui_test.Vec2(185, 250)
        await emulate_mouse_move(start_pos, human_delay_speed=human_delay_speed)
        await human_delay(human_delay_speed)
        await emulate_mouse(MouseEventType.LEFT_BUTTON_DOWN)
        await human_delay(human_delay_speed)
        await emulate_mouse_slow_move(start_pos, end_pos, human_delay_speed=human_delay_speed)
        await human_delay(human_delay_speed)

        await self.finalize_test()

        await emulate_mouse(MouseEventType.LEFT_BUTTON_UP)  # release the dangling wire to cancel the connection

        await human_delay(human_delay_speed)

        # Restore connections for other tests
        connections["First.color1"] = ["Second.out"]
        connections["First.color2"] = ["Third.outcome"]

    async def test_wire_in_progress_when_curve_drawn_top(self):
        """Testing dragging a connection from one port towards another but not connecting yet."""
        window = await self.create_test_window(768, 512, block_devices=False)

        global connections
        del connections["First.color2"]

        with window.frame:
            delegate = GraphNodeDelegate()
            model = Model()
            graph_view = GraphView(model=model, delegate=delegate, style=style, draw_curve_top_layer=True)

        for i in range(10):
            await omni.kit.app.get_app().next_update_async()

        graph_view.focus_on_nodes()
        await human_delay(10)

        human_delay_speed = 10
        # Do most of a drag and drop manually (just delay the drop until after capturing golden img)
        start_pos = ui_test.Vec2(620, 249)
        end_pos = ui_test.Vec2(185, 250)
        await emulate_mouse_move(start_pos, human_delay_speed=human_delay_speed)
        await human_delay(human_delay_speed)
        await emulate_mouse(MouseEventType.LEFT_BUTTON_DOWN)
        await human_delay(human_delay_speed)
        await emulate_mouse_slow_move(start_pos, end_pos, human_delay_speed=human_delay_speed)
        await human_delay(human_delay_speed)

        await self.finalize_test()

        await emulate_mouse(MouseEventType.LEFT_BUTTON_UP)  # release the dangling wire to cancel the connection

        await human_delay(human_delay_speed)

        # Restore connections for other tests
        connections["First.color1"] = ["Second.out"]
        connections["First.color2"] = ["Third.outcome"]

    async def test_connection_snapping(self):
        """Testing connection with the snapping effect on"""
        window = await self.create_test_window(768, 512, block_devices=False)

        global connections
        del connections["First.color2"]

        with window.frame:
            delegate = GraphNodeDelegate()
            model = Model()
            graph_view = GraphView(model=model, delegate=delegate, style=style, enable_snapping_for_connection=True)

        await ui_test.wait_n_updates(3)
        graph_view.focus_on_nodes()
        await ui_test.wait_n_updates(2)

        human_delay_speed = 5
        # Move to the Third.outcome port for a moment
        await ui_test.emulate_mouse_move(ui_test.Vec2(145, 250), human_delay_speed=5)
        await ui_test.human_delay(human_delay_speed)
        # Drag from Third.outcome output port to First.color2 label text instead of the exact port widget
        await ui_test.emulate_mouse_drag_and_drop(ui_test.Vec2(145, 250), ui_test.Vec2(640, 247), human_delay_speed=5)
        await ui_test.human_delay(human_delay_speed)
        # move the mouse away to check the connection
        await ui_test.emulate_mouse_move(ui_test.Vec2(300, 300), human_delay_speed=5)
        await ui_test.human_delay(human_delay_speed)

        # Restore connections for other tests
        connections["First.color1"] = ["Second.out"]
        connections["First.color2"] = ["Third.outcome"]
        await self.finalize_test()

    async def test_same_side_connection(self):
        window = await self.create_test_window(768, 512, block_devices=False)

        global connections
        del connections["First.color2"]
        del connections["First.color1"]

        with window.frame:
            delegate = GraphNodeDelegate()
            model = Model()
            graph_view = GraphView(model=model, delegate=delegate, style=style, allow_same_side_connections=True)

        await ui_test.wait_n_updates(3)
        graph_view.focus_on_nodes()
        await ui_test.wait_n_updates(2)

        human_delay_speed = 5
        # Move to the color1 input port for a moment
        await ui_test.emulate_mouse_move(ui_test.Vec2(292, 60), human_delay_speed=5)
        await human_delay(human_delay_speed)
        # Drag from color1 input port to color2 input port
        await human_delay(human_delay_speed)
        await emulate_mouse_drag_and_drop(ui_test.Vec2(292, 60), ui_test.Vec2(292, 80), human_delay_speed=5)
        await ui_test.human_delay(human_delay_speed)

        connections["First.color1"] = ["Second.out"]
        connections["First.color2"] = ["Third.outcome"]
        await self.finalize_test()
