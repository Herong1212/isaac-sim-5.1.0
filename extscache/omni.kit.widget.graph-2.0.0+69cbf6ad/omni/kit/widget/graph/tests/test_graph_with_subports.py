## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
__all__ = ["TestGraphWithSubports"]

from omni.kit.widget.graph import GraphNodeDescription
from omni.kit.widget.graph import GraphPortDescription
from omni.kit.widget.graph.abstract_graph_node_delegate import AbstractGraphNodeDelegate
from omni.kit.widget.graph.graph_model import GraphModel
from omni.kit.widget.graph.graph_view import GraphView
from omni.ui.tests.test_base import OmniUiTest
import omni.kit.app
import omni.ui as ui
from functools import partial

inputs = ["First.color1", "First.color1.tex", "First.color1.shader", "First.color2", "Third.size", "Fourth.color1", "Fourth.color1.tex", "Fourth.color1.shader",]
outputs = ["First.result", "Second.out", "Third.outcome", "Third.outcome.out1", "Third.outcome.out2"]
connections = {"First.color1.tex": ["Second.out"], "First.color2": ["Third.outcome.out2"], "Fourth.color1.tex": ["Third.outcome.out1"]}
style = {
    "Graph": {"background_color": 0xFF000000},
    "Graph.Connection": {"color": 0xFFDBA656, "background_color": 0xFFDBA656, "border_width": 2.0},
}

BORDER_WIDTH = 16


class Model(GraphModel):
    def __init__(self):
        super().__init__()

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
        item_len = len(item.split("."))
        if item_len == 1 or item_len == 2:
            result = [n for n in inputs + outputs if n.startswith(item) and len(n.split(".")) == item_len + 1]
            return result
        return []

    @property
    def expansion_state(self, item=None):
        """the expansion state of a node or a port"""
        item_len = len(item.split("."))
        if item_len == 2:
            return GraphModel.ExpansionState.CLOSED
        return GraphModel.ExpansionState.OPEN

    @property
    def inputs(self, item):
        if item in inputs:
            return connections.get(item, [])
        return None

    @property
    def outputs(self, item):
        if item in outputs:
            return []
        return None


class ExpandModel(Model):
    def __init__(self):
        super().__init__()

    @property
    def expansion_state(self, item=None):
        """the expansion state of a node or a port"""
        return GraphModel.ExpansionState.OPEN


class Delegate(AbstractGraphNodeDelegate):
    def node_background(self, model, node_desc: GraphNodeDescription):
        ui.Rectangle(style={"background_color": 0xFF015C3A})

    def node_header(self, model, node_desc: GraphNodeDescription):
        ui.Label(model[node_desc.node].name, style={"font_size": 12, "margin": 6, "color": 0xFFDBA656})

    def port_input(self, model, node_desc: GraphNodeDescription, port_desc: GraphPortDescription):
        # this is output port
        if model[port_desc.port].inputs is None:
            color = 0x0
        elif port_desc.connected_target:
            color = 0xFFDBA6FF
        else:
            color = 0xFFDBA656
        ui.Circle(width=10, style={"background_color": color})

    def port_output(self, model, node_desc: GraphNodeDescription, port_desc: GraphPortDescription):
        # this is output port
        if model[port_desc.port].outputs is None:
            color = 0x0
        elif port_desc.connected_source:
            color = 0xFFDBA6FF
        else:
            color = 0xFFDBA656
        ui.Circle(width=10, style={"background_color": color})

    def port(self, model, node_desc: GraphNodeDescription, port_desc: GraphPortDescription):
        def set_expansion_state(model, port, state: GraphModel.ExpansionState, *args):
            model[port].expansion_state = state

        port = port_desc.port
        level = port_desc.level
        sub_ports = model[port].ports
        is_group = len(sub_ports) > 0

        def draw_collapse_button():
            if is_group:
                state = model[port].expansion_state
                if state == GraphModel.ExpansionState.CLOSED:
                    button_name = "+"
                    next_state = GraphModel.ExpansionState.OPEN
                else:
                    button_name = "-"
                    next_state = GraphModel.ExpansionState.CLOSED
                ui.Label(button_name,
                         width=10,
                         style={"font_size": 10, "margin": 2},
                         mouse_pressed_fn=partial(set_expansion_state, model, port, next_state))
            else:
                ui.Spacer(width=10)

        def draw_branch():
            if level > 0:
                ui.Line(width=8, style={"color": 0xFFFFFFFF})

        alignment = ui.Alignment.LEFT if model[port].inputs is not None else ui.Alignment.RIGHT
        with ui.HStack():
            if alignment == ui.Alignment.RIGHT:
                ui.Spacer(width=40)
            else:
                draw_collapse_button()
                draw_branch()
            ui.Label(model[port].name, style={"font_size": 10, "margin": 2}, alignment=alignment)
            if alignment == ui.Alignment.RIGHT:
                draw_branch()
                draw_collapse_button()
            else:
                ui.Spacer(width=40)

    def connection(self, model, source, target, foreground: bool = False):
        """Called to create the connection between ports"""
        # If the connection is reversed, we need to mirror tangents
        ui.FreeBezierCurve(target.widget, source.widget, style={"color": 0xFFFFFFFF})


class TestGraphWithSubports(OmniUiTest):
    """Testing GraphView"""

    async def test_general(self):
        """Testing general properties of GraphView with port_grouping is True"""
        window = await self.create_test_window(512, 256)

        with window.frame:
            delegate = Delegate()
            model = Model()
            graph_view = GraphView(model=model, delegate=delegate, style=style, pan_x=400, pan_y=100, port_grouping=True)

        # Two frames because the first frame is to draw, the second frame is to auto-layout.
        for i in range(3):
            await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()

    async def test_expansion(self):
        """Testing subport expansion"""
        window = await self.create_test_window(512, 256)

        with window.frame:
            delegate = Delegate()
            model = ExpandModel()
            graph_view = GraphView(model=model, delegate=delegate, style=style, pan_x=400, pan_y=100, port_grouping=True)

        # Two frames because the first frame is to draw, the second frame is to auto-layout.
        for i in range(3):
            await omni.kit.app.get_app().next_update_async()

        await self.finalize_test()