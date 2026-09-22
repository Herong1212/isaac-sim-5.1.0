import os
import omni.kit.test
import omni.graph.core as og
import omni.graph.core.tests as ogts
from omni.graph.core.tests.omnigraph_test_utils import _TestGraphAndNode
from omni.graph.core.tests.omnigraph_test_utils import _test_clear_scene
from omni.graph.core.tests.omnigraph_test_utils import _test_setup_scene
from omni.graph.core.tests.omnigraph_test_utils import _test_verify_scene


class TestOgn(ogts.OmniGraphTestCase):

    TEST_DATA = [
        {
            '': {
                'inputs': [
                    ['inputs:matrix', {'type': 'matrixd[4]', 'value': [1, 0, 0, 0, 0, 1, 0, 0, 10, 10, 1, 0, 50, 0, 0, 1]}, False],
                    ['inputs:translation', {'type': 'vectord[3]', 'value': [1, 2, 3]}, False],
                ],
                'outputs': [
                    ['outputs:matrix', {'type': 'matrixd[4]', 'value': [1, 0, 0, 0, 0, 1, 0, 0, 10, 10, 1, 0, 1, 2, 3, 1]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:matrix', {'type': 'matrixd[4]', 'value': [1, 0, 0, 0, 0, 1, 0, 0, 10, 10, 1, 0, 50, 0, 0, 1]}, False],
                    ['inputs:translation', {'type': 'vectord[3][]', 'value': [[45, 10, 10], [3, 2, 1]]}, False],
                ],
                'outputs': [
                    ['outputs:matrix', {'type': 'matrixd[4][]', 'value': [[1, 0, 0, 0, 0, 1, 0, 0, 10, 10, 1, 0, 45, 10, 10, 1], [1, 0, 0, 0, 0, 1, 0, 0, 10, 10, 1, 0, 3, 2, 1, 1]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:matrix', {'type': 'matrixd[4][]', 'value': [[1, 10, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 50, 0, 0, 1], [1, 15, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 100, 0, 0, 1]]}, False],
                    ['inputs:translation', {'type': 'vectord[3]', 'value': [1, 2, 3]}, False],
                ],
                'outputs': [
                    ['outputs:matrix', {'type': 'matrixd[4][]', 'value': [[1, 10, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 2, 3, 1], [1, 15, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 2, 3, 1]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:matrix', {'type': 'matrixd[4][]', 'value': [[1, 10, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 50, 0, 0, 1], [1, 15, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 100, 0, 0, 1]]}, False],
                    ['inputs:translation', {'type': 'vectord[3][]', 'value': [[45, 10, 10], [3, 2, 1]]}, False],
                ],
                'outputs': [
                    ['outputs:matrix', {'type': 'matrixd[4][]', 'value': [[1, 10, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 45, 10, 10, 1], [1, 15, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 3, 2, 1, 1]]}, False],
                ],
            },
        },
    ]

    test_cap = os.getenv("OGN_GENERATED_TEST_LIMIT")
    if test_cap is not None:  # pragma: no cover
        TEST_DATA = TEST_DATA[0: int(test_cap)]

    async def test_generated(self):
        for i, test_run in enumerate(self.TEST_DATA):
            # Skip test runs that specified a test scene.
            controller = og.Controller()
            await _test_clear_scene(self, test_run, reset_stage=False)
            test_info = await _test_setup_scene(self, controller, f"/TestGraph{i}", "TestNode_omni_graph_nodes_SetMatrix4Translation", "omni.graph.nodes.SetMatrix4Translation", test_run, _TestGraphAndNode())
            await controller.evaluate(test_info.graph)
            _test_verify_scene(self, controller, test_run, test_info, f"omni.graph.nodes.SetMatrix4Translation User test case #{i+1}")

    async def test_vectorized_generated(self):
        for i, test_run in enumerate(self.TEST_DATA):
            # Skip test runs that specified a test scene.
            controller = og.Controller()
            await _test_clear_scene(self, test_run, reset_stage=False)
            test_info = await _test_setup_scene(self, controller, f"/TestGraph{i}", "TestNode_omni_graph_nodes_SetMatrix4Translation","omni.graph.nodes.SetMatrix4Translation", test_run, _TestGraphAndNode(), 16)
            await controller.evaluate(test_info.graph)
            _test_verify_scene(self, controller, test_run, test_info, f"omni.graph.nodes.SetMatrix4Translation User test case #{i+1}", 16)

    async def test_thread_safety(self):
        import omni.kit
        # Generate multiple instances of the test setup to run them concurrently
        instance_setup = dict()
        for n in range(24):
            instance_setup[f"/TestGraph_{n}"] = _TestGraphAndNode()

        valid_test_runs = self.TEST_DATA

        # Build a map of test graph to setup data
        test_data_setup = {}
        idx = 0
        for n in range(24):
            test_data_setup[f"/TestGraph_{n}"] = valid_test_runs[idx]
            idx = (idx + 1) % len(valid_test_runs)

        await omni.usd.get_context().new_stage_async()
        for (key, test_info) in instance_setup.copy().items():
            instance_setup[key] = await _test_setup_scene(self, og.Controller(allow_exists_prim=True), key, "TestNode_omni_graph_nodes_SetMatrix4Translation", "omni.graph.nodes.SetMatrix4Translation", test_data_setup[key], test_info)
        self.assertEqual(len(og.get_all_graphs()), 24)

        # We want to evaluate all graphs concurrently. Kick them all.
        # Evaluate multiple times to skip 2 serial frames and increase chances for a race condition.
        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()

        for (key, test_info) in instance_setup.items():
            _test_verify_scene(self, og.Controller(), test_data_setup[key], test_info, f"omni.graph.nodes.SetMatrix4Translation User test case instance{key}")

    async def test_data_access(self):
        test_file_name = "OgnSetMatrix4TranslationTemplate.usda"
        usd_path = os.path.join(os.path.dirname(__file__), "usd", test_file_name)
        if not os.path.exists(usd_path):  # pragma: no cover
            self.assertTrue(False, f"{usd_path} not found for loading test")
        (result, error) = await ogts.load_test_file(usd_path)
        self.assertTrue(result, f'{error} on {usd_path}')
        test_node = og.Controller.node("/TestGraph/Template_omni_graph_nodes_SetMatrix4Translation")
        self.assertTrue(test_node.is_valid())
        node_type_name = test_node.get_type_name()
        self.assertEqual(og.GraphRegistry().get_node_type_version(node_type_name), 1)

        def _attr_error(attribute: og.Attribute, usd_test: bool) -> str:  # pragma no cover
            test_type = "USD Load" if usd_test else "Database Access"
            return f"{node_type_name} {test_type} Test - {attribute.get_name()} value error"

