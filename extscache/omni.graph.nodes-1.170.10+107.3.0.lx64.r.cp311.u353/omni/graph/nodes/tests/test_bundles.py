import omni.graph.core as ogc
import omni.kit.test


class TestNodeInputAndOutputBundles(ogc.tests.OmniGraphTestCase):
    """Test to validate access to input/output bundles"""

    TEST_GRAPH_PATH = "/TestGraph"

    async def setUp(self):
        """Set up  test environment, to be torn down when done"""
        await super().setUp()

        self.graph = ogc.Controller.create_graph(self.TEST_GRAPH_PATH)
        self.context = self.graph.get_default_graph_context()

        self.prim_cube = ogc.Controller.create_prim("/cube", {}, "Cube")

        (
            self.graph,
            [self.read_prim, self.extract_prim, self.extract_bundle],
            _,
            _,
        ) = ogc.Controller.edit(
            self.TEST_GRAPH_PATH,
            {
                ogc.Controller.Keys.CREATE_NODES: [
                    ("read_prims", "omni.graph.nodes.ReadPrims"),
                    ("extract_prim", "omni.graph.nodes.ExtractPrim"),
                    ("extract_bundle", "omni.graph.nodes.ExtractBundle"),
                ],
                ogc.Controller.Keys.CONNECT: [
                    ("read_prims.outputs_primsBundle", "extract_prim.inputs:prims"),
                    ("extract_prim.outputs_primBundle", "extract_bundle.inputs:bundle"),
                ],
                ogc.Controller.Keys.SET_VALUES: [
                    ("extract_prim.inputs:primPath", str(self.prim_cube.GetPath())),
                ],
            },
        )

        stage = omni.usd.get_context().get_stage()

        omni.kit.commands.execute(
            "AddRelationshipTarget",
            relationship=stage.GetPropertyAtPath(self.TEST_GRAPH_PATH + "/read_prims.inputs:prims"),
            target=self.prim_cube.GetPath(),
        )

    async def test_pass_through_output(self):
        """Test if data from pass through output is accessible through bundles"""
        await ogc.Controller.evaluate(self.graph)

        factory = ogc.IBundleFactory.create()

        # Accessing bundle through get_output_bundle constructs IBundle interface
        output_bundle = self.context.get_output_bundle(self.extract_bundle, "outputs_passThrough")
        output_bundle2 = factory.get_bundle(self.context, output_bundle)
        self.assertTrue(output_bundle2.valid)
        self.assertTrue(output_bundle2.get_attribute_by_name("extent").is_valid())
