"""Tests for python wrapper object robustness"""

import os
from tempfile import TemporaryDirectory

import omni.graph.core as og
import omni.graph.core.tests as ogts
import omni.kit.app
import omni.usd


# ==============================================================================================================
class TestWrapperLifetime(ogts.OmniGraphTestCase):
    async def setUp(self):
        """Set up  test environment, to be torn down when done"""
        await super().setUp()
        self.TEST_GRAPH_PATH = "/Graph"

    async def test_survive_on_save(self):
        """Tests that saving the stage does not invalidate wrapper objects"""

        class OgnDummyPy:
            @staticmethod
            def compute(context: og.GraphContext, node: og.Node):
                return True

            @staticmethod
            def get_node_type() -> str:
                return "omni.graph.OgnDummyPy"

            @staticmethod
            def initialize_type(node_type: og.NodeType):
                """Initialize node attributes"""
                node_type.add_input("inputs:a", "int", False)
                node_type.add_output("outputs:a", "int", True)
                return True

        og.register_node_type(OgnDummyPy, 1)
        controller = og.Controller()
        keys = og.Controller.Keys
        graph_path = self.TEST_GRAPH_PATH
        (graph, nodes, _, _) = controller.edit(
            graph_path,
            {
                keys.CREATE_NODES: [
                    ("Dummy1", "omni.graph.OgnDummyPy"),
                    ("Dummy2", "omni.graph.OgnDummyPy"),
                ],
                keys.CONNECT: [
                    ("Dummy1.outputs:a", "Dummy2.inputs:a"),
                ],
            },
        )
        await controller.evaluate(graph)

        graph_context = graph.get_default_graph_context()
        attributes = nodes[0].get_attributes() + nodes[1].get_attributes()

        def _verify_handles():
            self.assertTrue(bool(graph_context))
            self.assertTrue(bool(graph))
            self.assertEqual(graph.get_default_graph_context(), graph_context)
            for n in nodes:
                self.assertTrue(bool(n))
                self.assertEqual(n.get_graph(), graph)
            for a in attributes:
                self.assertTrue(bool(a))
                self.assertTrue(a.get_node() in nodes)

        _verify_handles()
        # Now save the stage and re-verify, this will trigger a resync on the root path
        # which OG will have to handle in a way that preserves object handles for paths
        # that can be salvaged
        usd_context = omni.usd.get_context()
        with TemporaryDirectory() as temp_dir_name:
            tmp_file_path = os.path.join(temp_dir_name, "tmp.usda")
            await usd_context.save_as_stage_async(tmp_file_path)
            # make sure new stage event is handled by OG
            await omni.kit.app.get_app().next_update_async()
            _verify_handles()
        # Now clear the stage and re-create it
        await omni.usd.get_context().new_stage_async()
        controller = og.Controller()
        (graph, nodes, _, _) = controller.edit(
            graph_path,
            {
                keys.CREATE_NODES: [
                    ("Dummy1", "omni.graph.OgnDummyPy"),
                    ("Dummy2", "omni.graph.OgnDummyPy"),
                ],
                keys.CONNECT: [
                    ("Dummy1.outputs:a", "Dummy2.inputs:a"),
                ],
            },
        )
        await controller.evaluate(graph)
        _verify_handles()

        # Now trigger a resync by setting metadata on the stage root
        stage = usd_context.get_stage()
        stage.SetTimeCodesPerSecond(stage.GetTimeCodesPerSecond() + 1)
