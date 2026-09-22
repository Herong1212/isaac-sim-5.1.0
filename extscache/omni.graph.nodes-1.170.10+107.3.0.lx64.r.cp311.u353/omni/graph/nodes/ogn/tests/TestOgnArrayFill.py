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
                    ['inputs:array', {'type': 'bool[]', 'value': [True, True]}, False],
                    ['inputs:fillValue', {'type': 'bool', 'value': False}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'bool[]', 'value': [False, False]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:array', {'type': 'double[]', 'value': [1.0, 2.0, 3.0]}, False],
                    ['inputs:fillValue', {'type': 'double', 'value': 5.0}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'double[]', 'value': [5.0, 5.0, 5.0]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:array', {'type': 'float[]', 'value': [1.0, 2.0, 3.0]}, False],
                    ['inputs:fillValue', {'type': 'float', 'value': 5.0}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'float[]', 'value': [5.0, 5.0, 5.0]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:array', {'type': 'half[]', 'value': [1.0, 2.0, 3.0]}, False],
                    ['inputs:fillValue', {'type': 'half', 'value': 5.0}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'half[]', 'value': [5.0, 5.0, 5.0]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:array', {'type': 'int[]', 'value': [41, 42]}, False],
                    ['inputs:fillValue', {'type': 'int', 'value': 0}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'int[]', 'value': [0, 0]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:array', {'type': 'int64[]', 'value': [41, 42]}, False],
                    ['inputs:fillValue', {'type': 'int64', 'value': 0}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'int64[]', 'value': [0, 0]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:array', {'type': 'string', 'value': 'TestString'}, False],
                    ['inputs:fillValue', {'type': 'uchar', 'value': 65}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'string', 'value': 'AAAAAAAAAA'}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:array', {'type': 'token[]', 'value': ['Foo', 'Bar']}, False],
                    ['inputs:fillValue', {'type': 'token', 'value': ''}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'token[]', 'value': ['', '']}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:array', {'type': 'uchar[]', 'value': [41, 42]}, False],
                    ['inputs:fillValue', {'type': 'uchar', 'value': 0}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'uchar[]', 'value': [0, 0]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:array', {'type': 'uint[]', 'value': [41, 42]}, False],
                    ['inputs:fillValue', {'type': 'uint', 'value': 0}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'uint[]', 'value': [0, 0]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:array', {'type': 'uint64[]', 'value': [41, 42]}, False],
                    ['inputs:fillValue', {'type': 'uint64', 'value': 0}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'uint64[]', 'value': [0, 0]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:array', {'type': 'double[2][]', 'value': [[1.0, 2.0], [3.0, 4.0]]}, False],
                    ['inputs:fillValue', {'type': 'double[2]', 'value': [5.0, 6.0]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'double[2][]', 'value': [[5.0, 6.0], [5.0, 6.0]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:array', {'type': 'double[3][]', 'value': [[1.0, 2.0, 3.0], [3.0, 4.0, 5.0]]}, False],
                    ['inputs:fillValue', {'type': 'double[3]', 'value': [5.0, 6.0, 7.0]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'double[3][]', 'value': [[5.0, 6.0, 7.0], [5.0, 6.0, 7.0]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:array', {'type': 'double[4][]', 'value': [[1.0, 2.0, 3.0, 4.0], [3.0, 4.0, 5.0, 6.0]]}, False],
                    ['inputs:fillValue', {'type': 'double[4]', 'value': [5.0, 6.0, 7.0, 8.0]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'double[4][]', 'value': [[5.0, 6.0, 7.0, 8.0], [5.0, 6.0, 7.0, 8.0]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:array', {'type': 'matrixd[2][]', 'value': [[1.0, 2.0, 3.0, 4.0], [3.0, 4.0, 5.0, 6.0]]}, False],
                    ['inputs:fillValue', {'type': 'matrixd[2]', 'value': [5.0, 6.0, 7.0, 8.0]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'matrixd[2][]', 'value': [[5.0, 6.0, 7.0, 8.0], [5.0, 6.0, 7.0, 8.0]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:array', {'type': 'matrixd[3][]', 'value': [[1, 2, 3, 4, 5, 6, 7, 8, 9], [3, 4, 5, 6, 7, 8, 9, 10, 11]]}, False],
                    ['inputs:fillValue', {'type': 'matrixd[3]', 'value': [5, 6, 7, 8, 9, 10, 11, 12, 13]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'matrixd[3][]', 'value': [[5, 6, 7, 8, 9, 10, 11, 12, 13], [5, 6, 7, 8, 9, 10, 11, 12, 13]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:array', {'type': 'matrixd[4][]', 'value': [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16], [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]]}, False],
                    ['inputs:fillValue', {'type': 'matrixd[4]', 'value': [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'matrixd[4][]', 'value': [[5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:array', {'type': 'float[2][]', 'value': [[1.0, 2.0], [3.0, 4.0]]}, False],
                    ['inputs:fillValue', {'type': 'float[2]', 'value': [5.0, 6.0]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'float[2][]', 'value': [[5.0, 6.0], [5.0, 6.0]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:array', {'type': 'float[3][]', 'value': [[1.0, 2.0, 3.0], [3.0, 4.0, 5.0]]}, False],
                    ['inputs:fillValue', {'type': 'float[3]', 'value': [5.0, 6.0, 7.0]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'float[3][]', 'value': [[5.0, 6.0, 7.0], [5.0, 6.0, 7.0]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:array', {'type': 'float[4][]', 'value': [[1.0, 2.0, 3.0, 4.0], [3.0, 4.0, 5.0, 6.0]]}, False],
                    ['inputs:fillValue', {'type': 'float[4]', 'value': [5.0, 6.0, 7.0, 8.0]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'float[4][]', 'value': [[5.0, 6.0, 7.0, 8.0], [5.0, 6.0, 7.0, 8.0]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:array', {'type': 'half[2][]', 'value': [[1.0, 2.0], [3.0, 4.0]]}, False],
                    ['inputs:fillValue', {'type': 'half[2]', 'value': [5.0, 6.0]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'half[2][]', 'value': [[5.0, 6.0], [5.0, 6.0]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:array', {'type': 'half[3][]', 'value': [[1.0, 2.0, 3.0], [3.0, 4.0, 5.0]]}, False],
                    ['inputs:fillValue', {'type': 'half[3]', 'value': [5.0, 6.0, 7.0]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'half[3][]', 'value': [[5.0, 6.0, 7.0], [5.0, 6.0, 7.0]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:array', {'type': 'half[4][]', 'value': [[1.0, 2.0, 3.0, 4.0], [3.0, 4.0, 5.0, 6.0]]}, False],
                    ['inputs:fillValue', {'type': 'half[4]', 'value': [5.0, 6.0, 7.0, 8.0]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'half[4][]', 'value': [[5.0, 6.0, 7.0, 8.0], [5.0, 6.0, 7.0, 8.0]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:array', {'type': 'int[2][]', 'value': [[41, 42], [43, 44]]}, False],
                    ['inputs:fillValue', {'type': 'int[2]', 'value': [1, 2]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'int[2][]', 'value': [[1, 2], [1, 2]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:array', {'type': 'int[3][]', 'value': [[1, 2, 3], [3, 4, 5]]}, False],
                    ['inputs:fillValue', {'type': 'int[3]', 'value': [5, 6, 7]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'int[3][]', 'value': [[5, 6, 7], [5, 6, 7]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:array', {'type': 'int[4][]', 'value': [[1, 2, 3, 4], [3, 4, 5, 6]]}, False],
                    ['inputs:fillValue', {'type': 'int[4]', 'value': [5, 6, 7, 8]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'int[4][]', 'value': [[5, 6, 7, 8], [5, 6, 7, 8]]}, False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:array', {'type': 'pointd[3][]', 'value': [[1.0, 2.0, 3.0], [3.0, 4.0, 5.0]]}, False],
                    ['inputs:fillValue', {'type': 'pointd[3]', 'value': [5.0, 6.0, 7.0]}, False],
                ],
                'outputs': [
                    ['outputs:array', {'type': 'pointd[3][]', 'value': [[5.0, 6.0, 7.0], [5.0, 6.0, 7.0]]}, False],
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
            test_info = await _test_setup_scene(self, controller, f"/TestGraph{i}", "TestNode_omni_graph_nodes_ArrayFill", "omni.graph.nodes.ArrayFill", test_run, _TestGraphAndNode())
            await controller.evaluate(test_info.graph)
            _test_verify_scene(self, controller, test_run, test_info, f"omni.graph.nodes.ArrayFill User test case #{i+1}")

    async def test_vectorized_generated(self):
        for i, test_run in enumerate(self.TEST_DATA):
            # Skip test runs that specified a test scene.
            controller = og.Controller()
            await _test_clear_scene(self, test_run, reset_stage=False)
            test_info = await _test_setup_scene(self, controller, f"/TestGraph{i}", "TestNode_omni_graph_nodes_ArrayFill","omni.graph.nodes.ArrayFill", test_run, _TestGraphAndNode(), 16)
            await controller.evaluate(test_info.graph)
            _test_verify_scene(self, controller, test_run, test_info, f"omni.graph.nodes.ArrayFill User test case #{i+1}", 16)

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
            instance_setup[key] = await _test_setup_scene(self, og.Controller(allow_exists_prim=True), key, "TestNode_omni_graph_nodes_ArrayFill", "omni.graph.nodes.ArrayFill", test_data_setup[key], test_info)
        self.assertEqual(len(og.get_all_graphs()), 24)

        # We want to evaluate all graphs concurrently. Kick them all.
        # Evaluate multiple times to skip 2 serial frames and increase chances for a race condition.
        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()

        for (key, test_info) in instance_setup.items():
            _test_verify_scene(self, og.Controller(), test_data_setup[key], test_info, f"omni.graph.nodes.ArrayFill User test case instance{key}")

    async def test_data_access(self):
        test_file_name = "OgnArrayFillTemplate.usda"
        usd_path = os.path.join(os.path.dirname(__file__), "usd", test_file_name)
        if not os.path.exists(usd_path):  # pragma: no cover
            self.assertTrue(False, f"{usd_path} not found for loading test")
        (result, error) = await ogts.load_test_file(usd_path)
        self.assertTrue(result, f'{error} on {usd_path}')
        test_node = og.Controller.node("/TestGraph/Template_omni_graph_nodes_ArrayFill")
        self.assertTrue(test_node.is_valid())
        node_type_name = test_node.get_type_name()
        self.assertEqual(og.GraphRegistry().get_node_type_version(node_type_name), 1)

        def _attr_error(attribute: og.Attribute, usd_test: bool) -> str:  # pragma no cover
            test_type = "USD Load" if usd_test else "Database Access"
            return f"{node_type_name} {test_type} Test - {attribute.get_name()} value error"

