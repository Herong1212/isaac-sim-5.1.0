import omni.graph.core as og
import omni.graph.core.tests as ogts

_CONSTANT_TUPLES = [
    ("omni.graph.nodes.ConstantColor3d", (1.0, 1.0, 1.0)),
    ("omni.graph.nodes.ConstantColor3f", (1.0, 1.0, 1.0)),
    ("omni.graph.nodes.ConstantColor3h", (1.0, 1.0, 1.0)),
    ("omni.graph.nodes.ConstantColor4d", (1.0, 1.0, 1.0, 1.0)),
    ("omni.graph.nodes.ConstantColor4f", (1.0, 1.0, 1.0, 1.0)),
    ("omni.graph.nodes.ConstantColor4h", (1.0, 1.0, 1.0, 1.0)),
    ("omni.graph.nodes.ConstantDouble", 1.0),
    ("omni.graph.nodes.ConstantDouble2", (1.0, 1.0)),
    ("omni.graph.nodes.ConstantDouble3", (1.0, 1.0, 1.0)),
    ("omni.graph.nodes.ConstantDouble4", (1.0, 1.0, 1.0, 1.0)),
    ("omni.graph.nodes.ConstantFloat", 1.0),
    ("omni.graph.nodes.ConstantFloat2", (1.0, 1.0)),
    ("omni.graph.nodes.ConstantFloat3", (1.0, 1.0, 1.0)),
    ("omni.graph.nodes.ConstantFloat4", (1.0, 1.0, 1.0, 1.0)),
    ("omni.graph.nodes.ConstantFrame", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]),
    ("omni.graph.nodes.ConstantFrame", ((1, 2, 3, 4), (5, 6, 7, 8), (9, 10, 11, 12), (13, 14, 15, 16))),
    ("omni.graph.nodes.ConstantHalf", 1.0),
    ("omni.graph.nodes.ConstantHalf2", (1.0, 1.0)),
    ("omni.graph.nodes.ConstantHalf3", (1.0, 1.0, 1.0)),
    ("omni.graph.nodes.ConstantHalf4", (1.0, 1.0, 1.0, 1.0)),
    ("omni.graph.nodes.ConstantInt", 1),
    ("omni.graph.nodes.ConstantInt2", (1, 1)),
    ("omni.graph.nodes.ConstantInt3", (1, 1, 1)),
    ("omni.graph.nodes.ConstantInt4", (1, 1, 1, 1)),
    ("omni.graph.nodes.ConstantInt64", 1000000000000),
    ("omni.graph.nodes.ConstantMatrix2d", (1.0, 1.0, 1.0, 1.0)),
    ("omni.graph.nodes.ConstantMatrix2d", ((1.0, 1.0), (1.0, 1.0))),
    ("omni.graph.nodes.ConstantMatrix3d", (1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0)),
    ("omni.graph.nodes.ConstantMatrix3d", ((1.0, 1.0, 1.0), (1.0, 1.0, 1.0), (1.0, 1.0, 1.0))),
    (
        "omni.graph.nodes.ConstantMatrix4d",
        (1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0),
    ),
    (
        "omni.graph.nodes.ConstantMatrix4d",
        ((1.0, 1.0, 1.0, 1.0), (1.0, 1.0, 1.0, 1.0), (1.0, 1.0, 1.0, 1.0), (1.0, 1.0, 1.0, 1.0)),
    ),
    ("omni.graph.nodes.ConstantNormal3d", (1.0, 0, 0)),
    ("omni.graph.nodes.ConstantNormal3f", (1.0, 0, 0)),
    ("omni.graph.nodes.ConstantNormal3h", (1.0, 0, 0)),
    ("omni.graph.nodes.ConstantPath", "/World/A/Path"),
    ("omni.graph.nodes.ConstantPoint3d", (1.0, 1.0, 1.0)),
    ("omni.graph.nodes.ConstantPoint3f", (1.0, 1.0, 1.0)),
    ("omni.graph.nodes.ConstantPoint3h", (1.0, 1.0, 1.0)),
    ("omni.graph.nodes.ConstantQuatd", (0, 0, 0, 1.0)),
    ("omni.graph.nodes.ConstantQuatf", (0, 0, 0, 1.0)),
    ("omni.graph.nodes.ConstantQuath", (0, 0, 0, 1.0)),
    ("omni.graph.nodes.ConstantString", "a string"),
    ("omni.graph.nodes.ConstantTexCoord2d", (1.0, 1.0)),
    ("omni.graph.nodes.ConstantTexCoord2f", (1.0, 1.0)),
    ("omni.graph.nodes.ConstantTexCoord2h", (1.0, 1.0)),
    ("omni.graph.nodes.ConstantTexCoord3d", (1.0, 1.0, 1.0)),
    ("omni.graph.nodes.ConstantTexCoord3f", (1.0, 1.0, 1.0)),
    ("omni.graph.nodes.ConstantTexCoord3h", (1.0, 1.0, 1.0)),
    ("omni.graph.nodes.ConstantTimecode", 1.0),
    ("omni.graph.nodes.ConstantToken", "a token"),
    ("omni.graph.nodes.ConstantUChar", 1),
    ("omni.graph.nodes.ConstantUInt", 1),
    ("omni.graph.nodes.ConstantUInt64", 10000000000000),
    ("omni.graph.nodes.ConstantVector3d", (1.0, 1.0, 1.0)),
    ("omni.graph.nodes.ConstantVector3f", (1.0, 1.0, 1.0)),
    ("omni.graph.nodes.ConstantVector3h", (1.0, 1.0, 1.0)),
]


class TestConstantNodes(ogts.OmniGraphTestCase):
    """Class for testing constant nodes"""

    async def test_constant_nodes(self):
        def flatten_to_list(t):
            """Helper to flatten nested lists and tuples"""
            res = []

            def flatten(item, result_list):
                if isinstance(item, (list, tuple)):
                    for x in item:
                        flatten(x, result_list)
                else:
                    result_list.append(item)

            flatten(t, res)
            return res

        # walk through the graph, testing each constant
        graph_count = 0
        for node, value in _CONSTANT_TUPLES:
            with self.subTest(f"{node}-{graph_count}"):
                graph_count = graph_count + 1
                controller = og.Controller()
                keys = controller.Keys
                (graph, (const, to_string), _, _) = controller.edit(
                    f"/World/MyGraph{graph_count}",
                    {
                        keys.CREATE_NODES: [
                            ("Constant", node),
                            ("ToString", "omni.graph.nodes.ToString"),
                        ],
                        keys.SET_VALUES: [("Constant.inputs:value", value)],
                        keys.CONNECT: [("Constant.inputs:value", "ToString.inputs:value")],
                    },
                )
                await controller.evaluate(graph)
                a = const.get_attribute("inputs:value").get()
                b = flatten_to_list(value) if isinstance(value, tuple) else value
                c = to_string.get_attribute("inputs:value").get()
                if isinstance(b, list):
                    self.assertListEqual(list(a), b)  # handle values being numpy arrays
                    self.assertListEqual(list(c), b)
                else:
                    self.assertEquals(a, b)
                    self.assertEquals(c, b)

        # custom case for target constants
        with self.subTest("omni.graph.nodes.ConstantTarget"):
            value = "/World/A/Target"
            controller = og.Controller()
            keys = controller.Keys
            (graph, (const, get_prim), _, _) = controller.edit(
                "/World/MyGraphTarget",
                {
                    keys.CREATE_NODES: [
                        ("Constant", "omni.graph.nodes.ConstantTarget"),
                        ("GetPrimPaths", "omni.graph.nodes.GetPrimPaths"),
                    ],
                    keys.SET_VALUES: [("Constant.inputs:value", value)],
                    keys.CONNECT: [("Constant.inputs:value", "GetPrimPaths.inputs:prims")],
                },
            )

            await controller.evaluate(graph)
            a = const.get_attribute("inputs:value").get()
            c = get_prim.get_attribute("inputs:prims").get()
            self.assertEquals(1, len(a))
            self.assertEquals(1, len(c))
            self.assertEquals(str(a[0]), str(value))
            self.assertEquals(str(c[0]), str(value))
