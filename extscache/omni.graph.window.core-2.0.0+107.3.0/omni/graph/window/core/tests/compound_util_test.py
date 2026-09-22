import omni.graph.core as og
import omni.kit.test
import omni.usd

from ..compounds import CompoundUtils


class TestCompoundUtils(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()

    async def test_can_create_compound_from(self):
        """
        Tests the helper utility that determines whether a selection of nodes can be
        turned into a compound graph
        """
        stage = omni.usd.get_context().get_stage()

        # Test graph set up
        #   [G1In1]-->[G1M1]-->[G1M2]--->[G1M4]--->[G1Out1]
        #   [G1In2]---^    |---[G1M3]----|    |--->[G1Out2]
        #
        #   [G2In1]-->[G2M1]-->[G2Out1]
        #
        #   [G3In1]
        controller = og.Controller()
        keys = controller.Keys
        (_, nodes, _, _) = controller.edit(
            "/World/Testgraph",
            {
                keys.CREATE_NODES: [
                    ("G1In1", "omni.graph.nodes.ConstantFloat"),
                    ("G1In2", "omni.graph.nodes.ConstantFloat"),
                    ("G1M1", "omni.graph.nodes.Add"),
                    ("G1M2", "omni.graph.nodes.Add"),
                    ("G1M3", "omni.graph.nodes.Add"),
                    ("G1M4", "omni.graph.nodes.Add"),
                    ("G1Out1", "omni.graph.nodes.Magnitude"),
                    ("G1Out2", "omni.graph.nodes.Magnitude"),
                    ("G2In1", "omni.graph.nodes.ConstantFloat"),
                    ("G2M1", "omni.graph.nodes.Magnitude"),
                    ("G2Out1", "omni.graph.nodes.Magnitude"),
                    ("G3In1", "omni.graph.nodes.ConstantFloat"),
                ],
                keys.CONNECT: [
                    ("G1In1.inputs:value", "G1M1.inputs:a"),
                    ("G1In2.inputs:value", "G1M1.inputs:b"),
                    ("G1M1.outputs:sum", "G1M2.inputs:a"),
                    ("G1M1.outputs:sum", "G1M2.inputs:b"),
                    ("G1M1.outputs:sum", "G1M3.inputs:a"),
                    ("G1M1.outputs:sum", "G1M3.inputs:b"),
                    ("G1M2.outputs:sum", "G1M4.inputs:a"),
                    ("G1M3.outputs:sum", "G1M4.inputs:b"),
                    ("G1M4.outputs:sum", "G1Out1.inputs:input"),
                    ("G1M4.outputs:sum", "G1Out2.inputs:input"),
                    ("G2In1.inputs:value", "G2M1.inputs:input"),
                    ("G2M1.outputs:magnitude", "G2Out1.inputs:input"),
                ],
            },
        )

        prims = tuple(stage.GetPrimAtPath(n.get_prim_path()) for n in nodes)
        g1in1, g1in2, g1m1, g1m2, g1m3, g1m4, g1out1, g1out2, g2in1, g2m1, g2out1, g3in1 = prims

        # test individual nodes
        self.assertTrue(CompoundUtils.can_create_compound_from([g1in1]))
        self.assertTrue(CompoundUtils.can_create_compound_from([g1in2]))
        self.assertTrue(CompoundUtils.can_create_compound_from([g1m1]))
        self.assertTrue(CompoundUtils.can_create_compound_from([g2m1]))
        self.assertTrue(CompoundUtils.can_create_compound_from([g1out1]))

        # test unconnected nodes
        self.assertTrue(CompoundUtils.can_create_compound_from([g1in1, g2in1, g3in1]))
        self.assertTrue(CompoundUtils.can_create_compound_from([g1out1, g2out1, g3in1]))
        self.assertTrue(CompoundUtils.can_create_compound_from([g1in1, g2out1]))
        self.assertTrue(CompoundUtils.can_create_compound_from([g1m1, g2out1]))

        # test valid connected nodes
        self.assertTrue(CompoundUtils.can_create_compound_from([g1in1, g1in2, g1m1]))
        self.assertTrue(CompoundUtils.can_create_compound_from([g1in1, g1in2, g1m1, g1m2]))
        self.assertTrue(CompoundUtils.can_create_compound_from([g1in1, g1in2, g1m1, g1m2, g1m3]))
        self.assertTrue(CompoundUtils.can_create_compound_from([g1in1, g1in2, g1m1, g1m2, g1m3, g1m4]))
        self.assertTrue(CompoundUtils.can_create_compound_from([g1in1, g1in2, g1m1, g1m2, g1m3, g1m4, g1out1, g1out2]))
        self.assertTrue(CompoundUtils.can_create_compound_from([g1m1, g1m2, g1m3, g1m4, g1out1, g1out2]))

        # test multiple valid groups
        self.assertTrue(CompoundUtils.can_create_compound_from([g1in1, g1in2, g1m1, g2in1, g2m1, g2out1]))
        self.assertTrue(
            CompoundUtils.can_create_compound_from([g1m3, g1m4, g1out1, g1out2, g2in1, g2m1, g2out1, g3in1])
        )

        # test entire subgraphs/graph
        self.assertTrue(CompoundUtils.can_create_compound_from([g1in1, g1in2, g1m1, g1m2, g1m3, g1m4, g1out1]))
        self.assertTrue(CompoundUtils.can_create_compound_from([g2in1, g2m1, g2out1]))
        self.assertTrue(CompoundUtils.can_create_compound_from([g3in1]))
        self.assertTrue(CompoundUtils.can_create_compound_from(list(prims)))

        # test invalid setups
        self.assertFalse(CompoundUtils.can_create_compound_from([g1in1, g1m2]))
        self.assertFalse(CompoundUtils.can_create_compound_from([g1in1, g1out1]))
        self.assertFalse(CompoundUtils.can_create_compound_from([g1in1, g1m1, g1m2, g1m4, g1out1]))
        self.assertFalse(CompoundUtils.can_create_compound_from([g1m1, g1m3, g1m4]))
        self.assertFalse(CompoundUtils.can_create_compound_from([g2in1, g2out1]))

        # test mixing graphs
        (_, (node_a, _), _, _) = controller.edit(
            "/World/Testgraph2",
            {
                keys.CREATE_NODES: [
                    ("nodeA", "omni.graph.nodes.ConstantFloat"),
                    ("nodeB", "omni.graph.nodes.ConstantFloat"),
                ]
            },
        )

        self.assertFalse(CompoundUtils.can_create_compound_from([stage.GetPrimAtPath(node_a.get_prim_path()), g1in1]))

    async def test_sanitize_attribute_name(self):
        """Unit tests for the sanitize attribute name function"""
        controller = og.Controller(update_usd=True)
        keys = controller.Keys
        (_, (node,), _, _) = controller.edit(
            "/World/Testgraph",
            {
                keys.CREATE_NODES: [
                    (
                        "compound_node",
                        {
                            keys.CREATE_NODES: [("nodeA", "omni.graph.nodes.Add")],
                            keys.PROMOTE_ATTRIBUTES: [
                                ("nodeA.inputs:a", "a"),
                                ("nodeA.inputs:b", "b"),
                                ("nodeA.outputs:sum", "sum"),
                            ],
                        },
                    ),
                ]
            },
        )

        input_port = og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT
        output_port = og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT

        # existing names
        self.assertEqual(CompoundUtils.sanitize_attribute_name("a", node, input_port, False, None), "a_01")
        self.assertEqual(CompoundUtils.sanitize_attribute_name("b", node, input_port, False, None), "b_01")
        self.assertEqual(CompoundUtils.sanitize_attribute_name("sum", node, output_port, False, None), "sum_01")

        # standard conversion
        self.assertEqual(CompoundUtils.sanitize_attribute_name("a_b_c_d", node, input_port, False, "a"), "aBCD")
        self.assertEqual(CompoundUtils.sanitize_attribute_name("a", node, output_port, False, None), "a")
        self.assertEqual(CompoundUtils.sanitize_attribute_name("a_b_c_d", node, output_port, False, "a"), "aBCD")
        self.assertEqual(CompoundUtils.sanitize_attribute_name("a b c d", node, input_port, False, None), "aBCD")
        self.assertEqual(CompoundUtils.sanitize_attribute_name("123123", node, input_port, False, None), "_23123")
        self.assertEqual(CompoundUtils.sanitize_attribute_name("!@#$%", node, input_port, False, None), "_____")
        self.assertEqual(CompoundUtils.sanitize_attribute_name("blah[]", node, input_port, False, None), "blah")
        self.assertEqual(CompoundUtils.sanitize_attribute_name("ALL_CAPS", node, input_port, False, None), "allCaps")
        self.assertEqual(CompoundUtils.sanitize_attribute_name("____", node, input_port, False, None), "____")
        self.assertEqual(CompoundUtils.sanitize_attribute_name("-", node, input_port, False, None), "_")
        self.assertEqual(CompoundUtils.sanitize_attribute_name("a:b:c:d", node, input_port, False, None), "a_B_C_D")

        # Empty string
        self.assertEqual(CompoundUtils.sanitize_attribute_name("", node, input_port, False, None), "_")

        # add the default name
        og.Controller.create_attribute(
            node,
            "inputs:_",
            og.Type(og.BaseDataType.INT, 1, 0, og.AttributeRole.NONE),
            og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT,
        )
        self.assertEqual(CompoundUtils.sanitize_attribute_name("", node, input_port, False, None), "__01")
        self.assertEqual(CompoundUtils.sanitize_attribute_name("!", node, input_port, False, None), "__01")
        self.assertEqual(CompoundUtils.sanitize_attribute_name("_", node, input_port, False, None), "__01")
        self.assertEqual(CompoundUtils.sanitize_attribute_name("-", node, input_port, False, None), "__01")
        self.assertEqual(CompoundUtils.sanitize_attribute_name(":::::", node, input_port, False, None), "_____")
        self.assertEqual(CompoundUtils.sanitize_attribute_name(":", node, input_port, False, None), "__01")
        og.Controller.create_attribute(
            node,
            "inputs:__01",
            og.Type(og.BaseDataType.INT, 1, 0, og.AttributeRole.NONE),
            og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT,
        )
        self.assertEqual(CompoundUtils.sanitize_attribute_name(":", node, input_port, False, None), "__02")

        # keywords and types
        self.assertEqual(CompoundUtils.sanitize_attribute_name("double", node, input_port, False, None), "double_01")
        self.assertEqual(CompoundUtils.sanitize_attribute_name("double3", node, input_port, False, None), "double3")
        self.assertEqual(CompoundUtils.sanitize_attribute_name("double[3]", node, input_port, False, None), "double3")
        self.assertEqual(CompoundUtils.sanitize_attribute_name("do", node, input_port, False, None), "do_01")
        self.assertEqual(CompoundUtils.sanitize_attribute_name("while", node, input_port, False, None), "while_01")
