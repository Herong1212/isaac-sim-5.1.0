## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
from omni.kit.widget.graph import GraphView, IsolationGraphModel, GraphNodeDelegate
from omni.ui.tests.test_base import OmniUiTest
import omni.kit.ui_test as ui_test
from .test_graph import Model


inputs = ["First.color1", "First.color2", "sub1.in", "sub2.in"]
outputs = ["First.result", "sub1.out", "sub2.out"]
connections = {}


class MyModel(Model):
    def __init__(self):
        super().__init__()

    @property
    def nodes(self, item=None):
        if item:
            return ["sub1", "sub2"]
        return ["First"]

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
            return list(connections.get(item, set()))

    @inputs.setter
    def inputs(self, value, item=None):
        if item is None:
            return

        for v in value:
            if item:
                if item not in connections:
                    connections[item] = set()

                if v not in connections:
                    connections[item].add(v)

        if not value:
            connections.pop(item)

        self._item_changed(None)

    @property
    def outputs(self, item):
        if item in outputs:
            return list(connections.get(item, set()))

class TestIsolationModel(OmniUiTest):
    async def test_general(self):
        """Testing isolation model for compound, input and output node"""
        window = await self.create_test_window(768, 512, block_devices=False)

        style = GraphNodeDelegate.get_style()
        # Don't use the image because the image scaling looks different in editor and kit-mini
        style["Graph.Node.Footer.Image"]["image_url"] = ""
        style["Graph.Node.Header.Collapse"]["image_url"] = ""
        style["Graph.Node.Header.Collapse::Minimized"]["image_url"] = ""
        style["Graph.Node.Header.Collapse::Closed"]["image_url"] = ""

        with window.frame:
            delegate = GraphNodeDelegate()
            model = MyModel()
            graph_view = GraphView(model=model, delegate=delegate, style=style, pan_x=600, pan_y=170)

        # get node first and dive in
        item = model.nodes[0]
        isolation_model = IsolationGraphModel(model, item)
        graph_view.model = isolation_model

        # Wait several frames to draw and auto-layout.
        human_delay_speed = 5
        await ui_test.human_delay(human_delay_speed)

        graph_view.focus_on_nodes()

        await ui_test.human_delay(human_delay_speed)

        # select input nodes
        await ui_test.emulate_mouse_move(ui_test.Vec2(380, 320), human_delay_speed=5)
        # move input nodes
        await ui_test.emulate_mouse_drag_and_drop(ui_test.Vec2(380, 320), ui_test.Vec2(100, 60), human_delay_speed=5)

        # select output nodes
        await ui_test.emulate_mouse_move(ui_test.Vec2(380, 450), human_delay_speed=5)
        # move output nodes
        await ui_test.emulate_mouse_drag_and_drop(ui_test.Vec2(380, 450), ui_test.Vec2(650, 180), human_delay_speed=5)

        # Move to the First.color1 port
        await ui_test.emulate_mouse_move(ui_test.Vec2(168, 45), human_delay_speed=5)
        # Connnect the First.color1 port to sub1.in
        await ui_test.emulate_mouse_drag_and_drop(ui_test.Vec2(168, 45), ui_test.Vec2(320, 45), human_delay_speed=5)
        await ui_test.human_delay(human_delay_speed)

        # Move to the sub2.out port
        await ui_test.emulate_mouse_move(ui_test.Vec2(448, 185), human_delay_speed=5)
        # Connnect the sub2.out port to First.result
        await ui_test.emulate_mouse_drag_and_drop(ui_test.Vec2(448, 185), ui_test.Vec2(590, 170), human_delay_speed=5)
        await ui_test.human_delay(human_delay_speed)

        global connections
        self.assertEqual(connections["sub1.in"], {"First.color1"})
        self.assertEqual(connections["First.result"], {"sub2.out"})

        # Restore connections for other tests
        connections = {}
        await self.finalize_test()
        graph_view.destroy()
        window.destroy()
