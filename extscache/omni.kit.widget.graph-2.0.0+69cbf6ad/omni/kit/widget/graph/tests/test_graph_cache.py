## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
from .test_graph import Model
from omni.ui.tests.test_base import OmniUiTest
from ..graph_node_index import GraphNodeIndex


class ModelPlus(Model):
    def __init__(self):
        super().__init__()
        self._inputs = ["First.color1", "First.color2", "Third.size"]
        self._outputs = ["First.result", "Second.out", "Third.outcome"]
        self._connections = {"First.color1": ["Second.out"], "First.color2": ["Third.outcome"]}

    def change(self):
        self._inputs = ["First.color1", "First.color2", "Fourth.size"]
        self._outputs = ["First.result", "Second.out", "Fourth.outcome"]
        self._connections = {"First.color1": ["Second.out"], "First.color2": ["Fourth.outcome"]}

    @property
    def nodes(self, item=None):
        if item:
            return

        return sorted(set([n.split(".")[0] for n in self._inputs + self._outputs]))

    @property
    def name(self, item=None):
        return item.split(".")[-1]

    @property
    def ports(self, item=None):
        if item in self._inputs:
            return

        if item in self._outputs:
            return

        return [n for n in self._inputs + self._outputs if n.startswith(item)]

    @property
    def inputs(self, item):
        if item in self._inputs:
            return self._connections.get(item, [])

    @property
    def outputs(self, item):
        if item in self._outputs:
            return []


class TestGraphCache(OmniUiTest):
    async def test_general(self):
        model = ModelPlus()
        cache1 = GraphNodeIndex(model, True)
        cache2 = GraphNodeIndex(model, True)

        diff = cache1.get_diff(cache2)
        self.assertTrue(diff.valid)
        self.assertTrue(not diff.nodes_to_add)
        self.assertTrue(not diff.connections_to_add)
        self.assertTrue(not diff.nodes_to_del)
        self.assertTrue(not diff.connections_to_del)

        model.change()
        cache2 = GraphNodeIndex(model, True)

        diff = cache1.get_diff(cache2)
        self.assertTrue(diff.valid)

        # Check the difference
        to_add = list(sorted([n.node for n in diff.nodes_to_add]))
        self.assertEqual(to_add, ["First", "Fourth"])
        to_add = list(sorted([(c.source_port, c.target_port) for c in diff.connections_to_add]))
        self.assertEqual(to_add, [("Fourth.outcome", "First.color2"), ("Second.out", "First.color1")])
        to_del = list(sorted([n.node for n in diff.nodes_to_del]))
        self.assertEqual(to_del, ["First", "Third"])
        to_del = list(sorted([(c.source_port, c.target_port) for c in diff.connections_to_del]))
        self.assertEqual(to_del, [("Second.out", "First.color1"), ("Third.outcome", "First.color2")])
