import omni.graph.core as og
import omni.graph.core.tests as ogts
import omni.kit.test
from pxr import Usd, UsdGeom


class TestReadPrimsDirtyPush(ogts.OmniGraphTestCase):
    """Unit tests for dirty push behavior of the ReadPrimsV2 node in this extension"""

    async def test_read_prims_dirty_push(self):
        usd_context = omni.usd.get_context()
        stage: Usd.Stage = usd_context.get_stage()
        test_graph_path = "/World/TestGraph"

        controller = og.Controller()
        keys = og.Controller.Keys

        tree = UsdGeom.Xform.Define(stage, "/tree")
        branch = UsdGeom.Xform.Define(stage, "/tree/branch")
        leaf = ogts.create_cube(stage, "tree/branch/leaf", (1, 0, 0))

        # Set initial values
        UsdGeom.XformCommonAPI(branch).SetTranslate((0, 0, 0))
        leaf.GetAttribute("size").Set(1)

        (graph, [read_prims_node, _], _, _) = controller.edit(
            {"graph_path": test_graph_path, "evaluator_name": "dirty_push"},
            {
                keys.CREATE_NODES: [
                    ("Read", "omni.graph.nodes.ReadPrimsV2"),
                    ("Inspector", "omni.graph.nodes.BundleInspector"),
                ],
                keys.CONNECT: [
                    ("Read.outputs_primsBundle", "Inspector.inputs:bundle"),
                ],
                keys.SET_VALUES: [
                    ("Read.inputs:computeBoundingBox", True),
                    ("Inspector.inputs:print", False),
                ],
            },
        )

        graph_context = graph.get_default_graph_context()

        bundle = None

        async def update_bundle(expected_child_count=1):
            nonlocal bundle
            await controller.evaluate()
            container = graph_context.get_output_bundle(read_prims_node, "outputs_primsBundle")
            self.assertTrue(container.valid)
            child_bundles = container.get_child_bundles()
            self.assertEqual(len(child_bundles), expected_child_count)
            bundle = child_bundles[0] if len(child_bundles) == 1 else None

        # Helpers
        def assert_bundle_attr(name, expected_value):
            attr = bundle.get_attribute_by_name(name)
            if expected_value is None:
                self.assertFalse(attr.is_valid())
            else:
                actual_value = attr.get()
                if isinstance(expected_value, list):
                    actual_value = actual_value.tolist()
                self.assertEqual(actual_value, expected_value)

        # Observe the branch
        omni.kit.commands.execute(
            "SetRelationshipTargets",
            relationship=stage.GetPropertyAtPath(f"{test_graph_path}/Read.inputs:prims"),
            targets=[branch.GetPath()],
        )

        # Initial update
        await update_bundle()

        assert_bundle_attr("xformOp:translate", [0, 0, 0])
        assert_bundle_attr("bboxMaxCorner", [0.5, 0.5, 0.5])
        assert_bundle_attr("worldMatrix", [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1])

        # Change the USD stage on the branch (a tracked prim)
        UsdGeom.XformCommonAPI(branch).SetTranslate((1, 2, 3))

        # The lazy node should compute
        await update_bundle()

        # Check the output bundle
        assert_bundle_attr("xformOp:translate", [1, 2, 3])
        assert_bundle_attr("bboxMaxCorner", [1.5, 2.5, 3.5])
        assert_bundle_attr("worldMatrix", [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 2, 3, 1])

        # Change the leaf cube (a descendant of the tracked prim)
        leaf.GetAttribute("size").Set(2)

        # The lazy node should compute
        await update_bundle()

        assert_bundle_attr("xformOp:translate", [1, 2, 3])
        assert_bundle_attr("bboxMaxCorner", [2.0, 3.0, 4.0])
        assert_bundle_attr("worldMatrix", [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 2, 3, 1])

        # Change the tree (an ancestor of the tracked prim)
        UsdGeom.XformCommonAPI(tree).SetTranslate((-1, -2, -3))

        # The lazy node should compute
        await update_bundle()

        assert_bundle_attr("xformOp:translate", [1, 2, 3])
        assert_bundle_attr("bboxMaxCorner", [1.0, 1.0, 1.0])
        assert_bundle_attr("worldMatrix", [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1])

        # Create a new attribute on the tracked prim
        UsdGeom.XformCommonAPI(branch).SetScale((10, 10, 10))

        # The lazy node should compute
        await update_bundle()

        assert_bundle_attr("xformOp:translate", [1, 2, 3])
        assert_bundle_attr("xformOp:scale", [10, 10, 10])
        assert_bundle_attr("bboxMaxCorner", [10.0, 10.0, 10.0])
        assert_bundle_attr("worldMatrix", [10, 0, 0, 0, 0, 10, 0, 0, 0, 0, 10, 0, 0, 0, 0, 1])

        # Delete the branch
        stage.RemovePrim(branch.GetPath())

        # The lazy node should compute
        await update_bundle(0)
        self.assertEqual(bundle, None)
