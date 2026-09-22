## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
__all__ = ["TestGraph"]

from omni.kit.widget.graph import GraphNodeDescription
from omni.kit.widget.graph import GraphNodeLayout
from omni.kit.widget.graph import GraphPortDescription
from omni.kit.widget.graph.abstract_graph_node_delegate import AbstractGraphNodeDelegate
from omni.kit.widget.graph.graph_model import GraphModel
from omni.kit.widget.graph.graph_view import GraphView
from omni.ui import color as cl
from omni.ui.tests.test_base import OmniUiTest
import omni.kit.app
import omni.ui as ui

inputs = ["First.color1", "First.color2", "Third.size"]
outputs = ["First.result", "Second.out", "Third.outcome"]
connections = {"First.color1": ["Second.out"], "First.color2": ["Third.outcome"]}
style = {
    "Graph": {"background_color": 0xFF000000},
    "Graph.Connection": {"color": 0xFFDBA656, "background_color": 0xFFDBA656, "border_width": 2.0},
}

BORDER_WIDTH = 16


class Model(GraphModel):
    def __init__(self):
        super().__init__()
        self.__positions = {}

    @property
    def nodes(self, item=None):
        if item:
            return

        return sorted(set([n.split(".")[0] for n in inputs + outputs]))

    @property
    def name(self, item=None):
        return item.split(".")[-1]

    @property
    def ports(self, item=None):
        if item in inputs:
            return

        if item in outputs:
            return

        return [n for n in inputs + outputs if n.startswith(item)]

    @property
    def inputs(self, item):
        if item in inputs:
            return connections.get(item, [])

    @inputs.setter
    def inputs(self, value, item=None):
        if item is None:
            return

        for v in value:
            if item:
                if item not in connections:
                    connections[item] = []

                if v not in connections:
                    connections[item].append(v)
                    if item in inputs and v in inputs: # same side connection
                        connections[v]= [item]
        if not value:
            connections.pop(item)

        self._item_changed(None)

    @property
    def outputs(self, item):
        if item in outputs:
            return []

    @property
    def position(self, item=None):
        """Returns the position of the node"""
        return self.__positions.get(item, None)

    @position.setter
    def position(self, value, item=None):
        """The node position setter"""
        self.__positions[item] = value


class Delegate(AbstractGraphNodeDelegate):
    def node_background(self, model, node_desc: GraphNodeDescription):
        ui.Rectangle(style={"background_color": 0xFF015C3A})

    def node_header(self, model, node_desc: GraphNodeDescription):
        ui.Label(model[node_desc.node].name, style={"font_size": 12, "margin": 6, "color": 0xFFDBA656})

    def port_input(self, model, node_desc: GraphNodeDescription, port_desc: GraphPortDescription):
        color = 0xFFDBA656 if port_desc.connected_target else 0x0
        ui.Circle(width=10, style={"background_color": color})

    def port_output(self, model, node_desc: GraphNodeDescription, port_desc: GraphPortDescription):
        color = 0xFFDBA656 if port_desc.connected_source else 0x0
        ui.Circle(width=10, style={"background_color": color})

    def port(self, model, node_desc: GraphNodeDescription, port_desc: GraphPortDescription):
        ui.Label(model[port_desc.port].name, style={"font_size": 10, "margin": 2})

    def connection(self, model, source, target, foreground: bool = False):
        """Called to create the connection between ports"""
        # If the connection is reversed, we need to mirror tangents
        ui.FreeBezierCurve(target.widget, source.widget, style={"color": 0xFFFFFFFF})


class DelegateHeap(AbstractGraphNodeDelegate):
    def get_node_layout(self, model, node_desc: GraphNodeDescription):
        return GraphNodeLayout.HEAP

    def port_input(self, model, node_desc: GraphNodeDescription, port_desc: GraphPortDescription):
        return ui.Rectangle(style={"background_color": cl(1.0, 0.0, 0.0, 1.0)})

    def port_output(self, model, node_desc: GraphNodeDescription, port_desc: GraphPortDescription):
        return ui.Rectangle(style={"background_color": cl(0.0, 1.0, 1.0, 0.5)})

    def port(self, model, node_desc: GraphNodeDescription, port_desc: GraphPortDescription):
        with ui.HStack():
            ui.Spacer(width=BORDER_WIDTH)
            with ui.VStack():
                ui.Spacer(height=BORDER_WIDTH)
                frame = ui.Frame(separate_window=True)
                with frame:
                    with ui.ZStack():
                        ui.Rectangle(width=32, height=32, style={"background_color": cl(0.75)})
                ui.Spacer(height=BORDER_WIDTH)
            ui.Spacer(width=BORDER_WIDTH)
        return frame

    def connection(self, model, source, target, foreground: bool=False):
        """Called to create the connection between ports"""
        ui.OffsetLine(
            target.widget,
            source.widget,
            alignment=ui.Alignment.UNDEFINED,
            begin_arrow_type=ui.ArrowType.ARROW,
            bound_offset=20,
            style_type_name_override="Graph.Connection",
            style={"color": cl.white, "border_width": 1.0},
        )


class TestGraph(OmniUiTest):
    """Testing GraphView"""

    async def test_general(self):
        """Testing general properties of GraphView"""
        window = await self.create_test_window(512, 256)

        with window.frame:
            delegate = Delegate()
            model = Model()
            graph_view = GraphView(model=model, delegate=delegate, style=style, pan_x=400, pan_y=100)

        # Two frames because the first frame is to draw, the second frame is to auto-layout.
        for i in range(10):
            await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_zoom(self):
        """Testing zooming of GraphView"""
        window = await self.create_test_window(256, 128)

        with window.frame:
            delegate = Delegate()
            model = Model()
            graph_view = GraphView(model=model, delegate=delegate, style=style, zoom=0.5, pan_x=200, pan_y=50)

        # Two frames because the first frame is to draw, the second frame is to auto-layout.
        for i in range(10):
            await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_focus(self):
        """Testing focusing of GraphView"""
        window = await self.create_test_window(512, 256)

        with window.frame:
            delegate = Delegate()
            model = Model()
            graph_view = GraphView(model=model, delegate=delegate, style=style)

        # Wait several frames to draw and auto-layout.
        for i in range(10):
            await omni.kit.app.get_app().next_update_async()

        graph_view.focus_on_nodes()

        for i in range(10):
            await omni.kit.app.get_app().next_update_async()

        self.assertAlmostEqual(graph_view.zoom, 1.6606260538101196)
        await self.finalize_test()

    async def test_focus_with_zoom_limits(self):
        """Testing focusing of GraphView"""
        window = ui.Window("test", width=512, height=256)

        with window.frame:
            delegate = Delegate()
            model = Model()
            graph_view = GraphView(model=model, delegate=delegate, style=style, zoom_max=1.5)

        # Wait several frames to draw and auto-layout.
        for i in range(10):
            await omni.kit.app.get_app().next_update_async()

        graph_view.focus_on_nodes()

        for i in range(10):
            await omni.kit.app.get_app().next_update_async()

        self.assertAlmostEqual(graph_view.zoom, 1.5, places=4)

    async def test_heap(self):
        """Testing general properties of GraphView"""
        import omni.kit.ui_test as ui_test
        window = await self.create_test_window(512, 256, block_devices=False)

        with window.frame:
            delegate = DelegateHeap()
            model = Model()
            graph_view = GraphView(model=model, delegate=delegate, style=style, pan_x=400, pan_y=100)

        # Two frames because the first frame is to draw, the second frame is to auto-layout.
        for i in range(10):
            await omni.kit.app.get_app().next_update_async()

        human_delay_speed = 5
        await ui_test.human_delay(human_delay_speed)

        # translate the heap node
        await ui_test.emulate_mouse_move(ui_test.Vec2(140, 90), human_delay_speed=5)
        await ui_test.human_delay(human_delay_speed)
        await ui_test.emulate_mouse_drag_and_drop(ui_test.Vec2(140, 90), ui_test.Vec2(250, 100), human_delay_speed=5)

        await self.finalize_test()

    async def test_not_force_regenerate(self):
        """Testing general properties of GraphView"""
        import omni.kit.ui_test as ui_test
        window = await self.create_test_window(512, 256, block_devices=False)

        with window.frame:
            delegate = Delegate()
            model = Model()
            graph_view = GraphView(model=model, delegate=delegate, style=style, pan_x=400, pan_y=100, always_force_regenerate=False)

        # remove connection of "First.color2"--"Third.outcome"
        human_delay_speed = 5
        await ui_test.human_delay(human_delay_speed)
        await ui_test.emulate_mouse_move(ui_test.Vec2(382, 151), human_delay_speed=5)
        await ui_test.human_delay(human_delay_speed)
        await ui_test.emulate_mouse_click(right_click=True)
        await ui_test.human_delay(human_delay_speed)
        await ui_test.emulate_mouse_move(ui_test.Vec2(400, 170), human_delay_speed=5)
        await ui_test.human_delay(human_delay_speed)
        await ui_test.emulate_mouse_click()
        await ui_test.human_delay(human_delay_speed)

        # rebuild node "Third", since when connection is removed, the port widget needs to be removed
        node = model.nodes[2]
        model._rebuild_node(node, True)
        await ui_test.human_delay(human_delay_speed)

        global connections
        self.assertEqual(connections, {"First.color1": ["Second.out"]})

        # restore the test
        connections = {"First.color1": ["Second.out"], "First.color2": ["Third.outcome"]}
        await self.finalize_test()