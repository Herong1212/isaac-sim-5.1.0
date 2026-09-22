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
                'outputs': [
                    ['outputs:count', 0, False],
                    ['outputs:names', [], False],
                    ['outputs:types', [], False],
                    ['outputs:roles', [], False],
                    ['outputs:arrayDepths', [], False],
                    ['outputs:tupleCounts', [], False],
                    ['outputs:values', [], False],
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
            test_info = await _test_setup_scene(self, controller, f"/TestGraph{i}", "TestNode_omni_graph_nodes_BundleInspector", "omni.graph.nodes.BundleInspector", test_run, _TestGraphAndNode())
            await controller.evaluate(test_info.graph)
            _test_verify_scene(self, controller, test_run, test_info, f"omni.graph.nodes.BundleInspector User test case #{i+1}")

    async def test_vectorized_generated(self):
        for i, test_run in enumerate(self.TEST_DATA):
            # Skip test runs that specified a test scene.
            controller = og.Controller()
            await _test_clear_scene(self, test_run, reset_stage=False)
            test_info = await _test_setup_scene(self, controller, f"/TestGraph{i}", "TestNode_omni_graph_nodes_BundleInspector","omni.graph.nodes.BundleInspector", test_run, _TestGraphAndNode(), 16)
            await controller.evaluate(test_info.graph)
            _test_verify_scene(self, controller, test_run, test_info, f"omni.graph.nodes.BundleInspector User test case #{i+1}", 16)

    async def test_data_access(self):
        test_file_name = "OgnBundleInspectorTemplate.usda"
        usd_path = os.path.join(os.path.dirname(__file__), "usd", test_file_name)
        if not os.path.exists(usd_path):  # pragma: no cover
            self.assertTrue(False, f"{usd_path} not found for loading test")
        (result, error) = await ogts.load_test_file(usd_path)
        self.assertTrue(result, f'{error} on {usd_path}')
        test_node = og.Controller.node("/TestGraph/Template_omni_graph_nodes_BundleInspector")
        self.assertTrue(test_node.is_valid())
        node_type_name = test_node.get_type_name()
        self.assertEqual(og.GraphRegistry().get_node_type_version(node_type_name), 4)

        def _attr_error(attribute: og.Attribute, usd_test: bool) -> str:  # pragma no cover
            test_type = "USD Load" if usd_test else "Database Access"
            return f"{node_type_name} {test_type} Test - {attribute.get_name()} value error"


        self.assertTrue(test_node.get_attribute_exists("inputs:bundle"))
        attribute = test_node.get_attribute("inputs:bundle")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("inputs:execIn"))
        attribute = test_node.get_attribute("inputs:execIn")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("inputs:inspectDepth"))
        attribute = test_node.get_attribute("inputs:inspectDepth")
        self.assertTrue(attribute.is_valid())
        expected_value = 1
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:print"))
        attribute = test_node.get_attribute("inputs:print")
        self.assertTrue(attribute.is_valid())
        expected_value = False
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("outputs:arrayDepths"))
        attribute = test_node.get_attribute("outputs:arrayDepths")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:attributeCount"))
        attribute = test_node.get_attribute("outputs:attributeCount")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs_bundle"))
        attribute = test_node.get_attribute("outputs_bundle")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:childCount"))
        attribute = test_node.get_attribute("outputs:childCount")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:count"))
        attribute = test_node.get_attribute("outputs:count")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:names"))
        attribute = test_node.get_attribute("outputs:names")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:roles"))
        attribute = test_node.get_attribute("outputs:roles")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:tupleCounts"))
        attribute = test_node.get_attribute("outputs:tupleCounts")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:types"))
        attribute = test_node.get_attribute("outputs:types")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:values"))
        attribute = test_node.get_attribute("outputs:values")
        self.assertTrue(attribute.is_valid())
