import omni.graph.core as og
import omni.graph.core.tests as ogts
import omni.kit.test


class TestFindPrimsNode(ogts.OmniGraphTestCase):
    """Unit tests for Find Prims node in this extension"""

    # ----------------------------------------------------------------------
    async def test_find_prims_node_type_attribute_v1(self):
        """First version of Find Prims node did not use pattern matching. Attribute 'type' needs to be automatically
        updated to support pattern matching.
        """
        # load the test scene which contains a ReadPrim V1 node
        (result, error) = await ogts.load_test_file("TestFindPrimsNode_v1.usda", use_caller_subdirectory=True)
        self.assertTrue(result, error)

        test_graph_path = "/World/TestGraph"
        test_graph = og.get_graph_by_path(test_graph_path)
        find_prims_empty = test_graph.get_node(test_graph_path + "/find_prims_empty")
        self.assertTrue(find_prims_empty.is_valid())

        find_prims_types = test_graph.get_node(test_graph_path + "/find_prims_types")
        self.assertTrue(find_prims_types.is_valid())

        self.assertEqual(find_prims_empty.get_attribute("inputs:type").get(), "*")
        self.assertEqual(find_prims_types.get_attribute("inputs:type").get(), "Mesh")

    # ----------------------------------------------------------------------
    async def test_add_target_input(self):
        """
        Test target input type and that path input is still used if target prim has not been selected
        """

        keys = og.Controller.Keys
        controller = og.Controller()
        (graph, (node,), _, _) = controller.edit(
            "/TestGraph",
            {
                keys.CREATE_NODES: [("FindPrims", "omni.graph.nodes.FindPrims")],
                keys.CREATE_PRIMS: [
                    ("/World/A", "Xform"),
                    ("/World/B", "Xform"),
                    ("/World/A/Cone", "Cone"),
                    ("/World/B/Cone", "Cone"),
                    ("/World/B/Cube", "Cube"),
                    ("/World/B/Sphere", "Sphere"),
                ],
                keys.SET_VALUES: [("FindPrims.inputs:rootPrimPath", "/World/A")],
            },
        )

        # If no target input is specified, fallback to path input
        await controller.evaluate(graph)
        out = node.get_attribute("outputs:primPaths")
        self.assertEqual(out.get(), ["/World/A/Cone"])

        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        rel = stage.GetRelationshipAtPath("/TestGraph/FindPrims.inputs:rootPrim")
        omni.kit.commands.execute("AddRelationshipTarget", relationship=rel, target="/World/B")

        await controller.evaluate(graph)
        out = node.get_attribute("outputs:primPaths")
        self.assertEqual(out.get(), ["/World/B/Cone", "/World/B/Cube", "/World/B/Sphere"])

        # Test with a required relationship
        cone = stage.GetPrimAtPath("/World/B/Cone")
        cube = stage.GetPrimAtPath("/World/B/Cube")
        omni.kit.commands.execute(
            "AddRelationshipTarget", relationship=cone.CreateRelationship("test_rel"), target="/World/A"
        )
        omni.kit.commands.execute(
            "AddRelationshipTarget", relationship=cube.CreateRelationship("test_rel"), target="/World/B"
        )
        rel_attr = node.get_attribute("inputs:requiredRelationship")
        rel_attr.set("test_rel")
        rel = stage.GetRelationshipAtPath("/TestGraph/FindPrims.inputs:requiredTarget")
        omni.kit.commands.execute("AddRelationshipTarget", relationship=rel, target="/World/B")
        await controller.evaluate(graph)
        self.assertEqual(out.get(), ["/World/B/Cube"])
