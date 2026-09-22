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
                    ['inputs:curveVertexStarts', [0], False],
                    ['inputs:curveVertexCounts', [3], False],
                    ['inputs:tubeSTStarts', [0], False],
                    ['inputs:tubeQuadStarts', [0], False],
                    ['inputs:cols', [3], False],
                    ['inputs:t', [0.1, 0.2, 0.3], False],
                    ['inputs:width', [2.0], False],
                    ['inputs:scaleTLikeS', False, False],
                ],
                'outputs': [
                    ['outputs:primvars:st', [], False],
                    ['outputs:primvars:st:indices', [], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:curveVertexStarts', [0], False],
                    ['inputs:curveVertexCounts', [3], False],
                    ['inputs:tubeSTStarts', [0, 12], False],
                    ['inputs:tubeQuadStarts', [0, 12], False],
                    ['inputs:cols', [3], False],
                    ['inputs:t', [0.1, 0.2, 0.3], False],
                    ['inputs:width', [2.0], False],
                    ['inputs:scaleTLikeS', False, False],
                ],
                'outputs': [
                    ['outputs:primvars:st', [[0.0, 0.1], [0.33333334, 0.1], [0.6666667, 0.1], [1, 0.1], [0, 0.2], [0.33333334, 0.2], [0.6666667, 0.2], [1, 0.2], [0, 0.3], [0.33333334, 0.3], [0.6666667, 0.3], [1, 0.3]], False],
                    ['outputs:primvars:st:indices', [0, 1, 5, 4, 1, 2, 6, 5, 2, 3, 7, 6, 4, 5, 9, 8, 5, 6, 10, 9, 6, 7, 11, 10, 8, 9, 13, 12, 9, 10, 14, 13, 10, 11, 15, 14, 12, 13, 17, 16, 13, 14, 18, 17, 14, 15, 19, 18], False],
                ],
            },
        },
        {
            '': {
                'inputs': [
                    ['inputs:curveVertexStarts', [0], False],
                    ['inputs:curveVertexCounts', [3], False],
                    ['inputs:tubeSTStarts', [0, 12], False],
                    ['inputs:tubeQuadStarts', [0, 12], False],
                    ['inputs:cols', [3], False],
                    ['inputs:t', [0.1, 0.2, 0.3], False],
                    ['inputs:width', [2.0, 2.0, 2.0], False],
                    ['inputs:scaleTLikeS', True, False],
                ],
                'outputs': [
                    ['outputs:primvars:st', [[0.0, 0.01924501], [0.33333334, 0.01924501], [0.6666667, 0.01924501], [1, 0.01924501], [0, 0.03849002], [0.33333334, 0.03849002], [0.6666667, 0.03849002], [1, 0.03849002], [0, 0.05773503], [0.33333334, 0.05773503], [0.6666667, 0.05773503], [1, 0.05773503]], False],
                    ['outputs:primvars:st:indices', [0, 1, 5, 4, 1, 2, 6, 5, 2, 3, 7, 6, 4, 5, 9, 8, 5, 6, 10, 9, 6, 7, 11, 10, 8, 9, 13, 12, 9, 10, 14, 13, 10, 11, 15, 14, 12, 13, 17, 16, 13, 14, 18, 17, 14, 15, 19, 18], False],
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
            test_info = await _test_setup_scene(self, controller, f"/TestGraph{i}", "TestNode_omni_graph_nodes_CurveTubeST", "omni.graph.nodes.CurveTubeST", test_run, _TestGraphAndNode())
            await controller.evaluate(test_info.graph)
            _test_verify_scene(self, controller, test_run, test_info, f"omni.graph.nodes.CurveTubeST User test case #{i+1}")

    async def test_vectorized_generated(self):
        for i, test_run in enumerate(self.TEST_DATA):
            # Skip test runs that specified a test scene.
            controller = og.Controller()
            await _test_clear_scene(self, test_run, reset_stage=False)
            test_info = await _test_setup_scene(self, controller, f"/TestGraph{i}", "TestNode_omni_graph_nodes_CurveTubeST","omni.graph.nodes.CurveTubeST", test_run, _TestGraphAndNode(), 16)
            await controller.evaluate(test_info.graph)
            _test_verify_scene(self, controller, test_run, test_info, f"omni.graph.nodes.CurveTubeST User test case #{i+1}", 16)

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
            instance_setup[key] = await _test_setup_scene(self, og.Controller(allow_exists_prim=True), key, "TestNode_omni_graph_nodes_CurveTubeST", "omni.graph.nodes.CurveTubeST", test_data_setup[key], test_info)
        self.assertEqual(len(og.get_all_graphs()), 24)

        # We want to evaluate all graphs concurrently. Kick them all.
        # Evaluate multiple times to skip 2 serial frames and increase chances for a race condition.
        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()

        for (key, test_info) in instance_setup.items():
            _test_verify_scene(self, og.Controller(), test_data_setup[key], test_info, f"omni.graph.nodes.CurveTubeST User test case instance{key}")

    async def test_data_access(self):
        test_file_name = "OgnCurveTubeSTTemplate.usda"
        usd_path = os.path.join(os.path.dirname(__file__), "usd", test_file_name)
        if not os.path.exists(usd_path):  # pragma: no cover
            self.assertTrue(False, f"{usd_path} not found for loading test")
        (result, error) = await ogts.load_test_file(usd_path)
        self.assertTrue(result, f'{error} on {usd_path}')
        test_node = og.Controller.node("/TestGraph/Template_omni_graph_nodes_CurveTubeST")
        self.assertTrue(test_node.is_valid())
        node_type_name = test_node.get_type_name()
        self.assertEqual(og.GraphRegistry().get_node_type_version(node_type_name), 1)

        def _attr_error(attribute: og.Attribute, usd_test: bool) -> str:  # pragma no cover
            test_type = "USD Load" if usd_test else "Database Access"
            return f"{node_type_name} {test_type} Test - {attribute.get_name()} value error"


        self.assertTrue(test_node.get_attribute_exists("inputs:cols"))
        attribute = test_node.get_attribute("inputs:cols")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:curveVertexCounts"))
        attribute = test_node.get_attribute("inputs:curveVertexCounts")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:curveVertexStarts"))
        attribute = test_node.get_attribute("inputs:curveVertexStarts")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:scaleTLikeS"))
        attribute = test_node.get_attribute("inputs:scaleTLikeS")
        self.assertTrue(attribute.is_valid())
        expected_value = False
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:t"))
        attribute = test_node.get_attribute("inputs:t")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:tubeQuadStarts"))
        attribute = test_node.get_attribute("inputs:tubeQuadStarts")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:tubeSTStarts"))
        attribute = test_node.get_attribute("inputs:tubeSTStarts")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:width"))
        attribute = test_node.get_attribute("inputs:width")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("outputs:primvars:st"))
        attribute = test_node.get_attribute("outputs:primvars:st")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:primvars:st:indices"))
        attribute = test_node.get_attribute("outputs:primvars:st:indices")
        self.assertTrue(attribute.is_valid())
