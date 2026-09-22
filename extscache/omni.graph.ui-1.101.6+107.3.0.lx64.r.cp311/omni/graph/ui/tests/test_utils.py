"""Test utility functions that don't require a golden image."""

import omni.graph.core as og
import omni.graph.core.tests as ogts
import omni.kit.app
import omni.ui as ui

from .._impl.standalone_attribute_builder import StandaloneAttributeBuilder


class TestOmniGraphUiUtils(ogts.OmniGraphTestCase):
    TEST_GRAPH_PATH = "/World/TestGraph"

    # Before running each test
    async def setUp(self):
        await super().setUp()

        self.graph, *_ = og.Controller.edit({"graph_path": self.TEST_GRAPH_PATH, "evaluator_name": "execution"})

    # After running each test
    async def tearDown(self):
        await super().tearDown()

    async def test_standalone_builder(self):
        # Test is_attribute_supported()
        node = og.Controller.create_node(self.TEST_GRAPH_PATH + "/bundle", "omni.graph.nodes.BundleConstructor")
        bundle_attr = node.get_attribute("outputs_bundle")
        self.assertFalse(StandaloneAttributeBuilder.is_attribute_supported(bundle_attr), "bundle attr support")

        node = og.Controller.create_node(self.TEST_GRAPH_PATH + "/target", "omni.graph.nodes.ConstantTarget")
        target_attr = node.get_attribute("inputs:value")
        self.assertFalse(StandaloneAttributeBuilder.is_attribute_supported(target_attr), "target attr support")

        node = og.Controller.create_node(self.TEST_GRAPH_PATH + "/color", "omni.graph.nodes.ConstantColor3f")
        color_attr = node.get_attribute("inputs:value")
        color_attr.set((0.5, 0.2, 0.1))
        self.assertTrue(StandaloneAttributeBuilder.is_attribute_supported(color_attr), "color attr support")

        # Test get_value_as_string()
        w = ui.Window("OG UI Test", width=100, height=100)
        with w.frame:
            _, model = StandaloneAttributeBuilder.build_ui(color_attr)

        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(
            StandaloneAttributeBuilder.get_value_as_string(model), "(0.5, 0.2, 0.1)", "get color value as string"
        )
