"""Test the node that inspects attribute bundles"""

import omni.graph.core as og
import omni.graph.core.tests as ogts

from .bundle_test_utils import (
    bundle_inspector_results,
    get_bundle_with_all_results,
    prim_with_everything_definition,
    verify_bundles_are_equal,
)


# ======================================================================
class TestBundleInspector(ogts.test_case_class()):
    """Run a simple unit test that exercises graph functionality"""

    # ----------------------------------------------------------------------
    async def test_node_with_contents(self):
        """Test the node with some pre-made input bundle contents"""
        prim_definition = prim_with_everything_definition()
        keys = og.Controller.Keys
        (_, [inspector_node, _], [prim], _) = og.Controller.edit(
            "/TestGraph",
            {
                keys.CREATE_NODES: [
                    ("Inspector", "omni.graph.nodes.BundleInspector"),
                ],
                keys.CREATE_PRIMS: ("TestPrim", prim_definition),
                keys.EXPOSE_PRIMS: (og.Controller.PrimExposureType.AS_BUNDLE, "/TestPrim", "TestPrimExtract"),
                keys.CONNECT: [
                    ("TestPrimExtract.outputs_primBundle", "Inspector.inputs:bundle"),
                ],
            },
        )
        await og.Controller.evaluate()
        results = bundle_inspector_results(inspector_node)
        expected_values = get_bundle_with_all_results(str(prim.GetPrimPath()), prim_source_type=str(prim.GetTypeName()))

        try:
            verify_bundles_are_equal(results, expected_values)
        except ValueError as error:
            self.assertTrue(False, error)

    async def test_bundle_inspector_node_v2(self):
        """Validate backward compatibility for legacy versions of BundleInspector node."""
        # load the test scene which contains a ReadPrim V1 node
        (result, error) = await ogts.load_test_file("TestBundleInspectorNode_v2.usda", use_caller_subdirectory=True)
        self.assertTrue(result, error)

        test_graph_path = "/TestGraph"
        test_graph = og.get_graph_by_path(test_graph_path)
        read_prim_node = test_graph.get_node(test_graph_path + "/Inspector")
        self.assertTrue(read_prim_node.is_valid())

        # validate new attributes can be automatically created with their default value set.
        attr_names_and_values = [
            ("inputs:inspectDepth", 1),
        ]

        for attr_name, attr_value in attr_names_and_values:
            self.assertTrue(read_prim_node.get_attribute_exists(attr_name))
            self.assertTrue(read_prim_node.get_attribute(attr_name).get() == attr_value)
