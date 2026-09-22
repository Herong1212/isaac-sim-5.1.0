import carb

import omni.graph.core as og
from omni.kit.hydra_texture import create_hydra_texture
import omni.kit.test
from omni.syntheticdata import SyntheticData, SyntheticDataStage


# Test the instance mapping pipeline
class TestGraphManipulation(omni.kit.test.AsyncTestCase):

    def __init__(self, methodName: str) -> None:
        super().__init__(methodName=methodName)
        if "rtx" not in omni.usd.get_context().get_attached_hydra_engine_names():
            omni.usd.create_hydra_engine("rtx", omni.usd.get_context())

    def render_product_path(self, hydra_texture) -> str:
        '''Return a string to the UsdRender.Product used by the texture'''
        render_product = hydra_texture.get_render_product_path()
        if render_product and (not render_product.startswith('/')):
            render_product = '/Render/RenderProduct_' + render_product
        return render_product

    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        self._stage = omni.usd.get_context().get_stage()
        self._hydra_texture_0 = create_hydra_texture(
            "TEX0",
            512,
            512,
            omni.usd.get_context().get_name(),
            is_async=carb.settings.acquire_settings_interface().get("/app/asyncRendering")
        )
        self._render_product_path_0 = self.render_product_path(self._hydra_texture_0)

    async def tearDown(self):
        self._hydra_texture_0 = None

    async def test_rendervar_enable(self):
        isdg = SyntheticData.Get()
        render_var = "BoundingBox3DSD"
        assert(not isdg.is_rendervar_enabled(self._render_product_path_0, render_var, False, self._stage))
        assert(not isdg.is_rendervar_used(self._render_product_path_0, render_var))
        isdg.enable_rendervar(self._render_product_path_0, render_var, self._stage)
        assert(isdg.is_rendervar_enabled(self._render_product_path_0, render_var, False, self._stage))
        assert(not isdg.is_rendervar_used(self._render_product_path_0, render_var))
        isdg.disable_rendervar(self._render_product_path_0, render_var, self._stage)
        assert(not isdg.is_rendervar_enabled(self._render_product_path_0, render_var, False, self._stage))
        assert(not isdg.is_rendervar_used(self._render_product_path_0, render_var))

    async def test_rendervar_auto_activation(self):
        isdg = SyntheticData.Get()
        render_var = "BoundingBox3DSD"
        assert(not isdg.is_rendervar_enabled(self._render_product_path_0, render_var, True, self._stage))
        assert(not isdg.is_rendervar_used(self._render_product_path_0, render_var))
        isdg.activate_node_template("BoundingBox3DReduction",0, [self._render_product_path_0], {}, self._stage, True)
        assert(isdg.is_rendervar_enabled(self._render_product_path_0, render_var, False, self._stage))
        assert(isdg.is_rendervar_used(self._render_product_path_0, render_var))
        assert(isdg.is_rendervar_enabled(self._render_product_path_0, render_var, True, self._stage))
        isdg.deactivate_node_template("BoundingBox3DReduction",0, [self._render_product_path_0], self._stage, True)
        assert(not isdg.is_rendervar_enabled(self._render_product_path_0, render_var, False, self._stage))
        assert(not isdg.is_rendervar_used(self._render_product_path_0, render_var))

    async def test_rendervar_manual_activation(self):
        isdg = SyntheticData.Get()
        render_var = "BoundingBox3DSD"
        assert(not isdg.is_rendervar_enabled(self._render_product_path_0, render_var, False, self._stage))
        assert(not isdg.is_rendervar_used(self._render_product_path_0, render_var))
        assert(not isdg.is_node_template_activated("BoundingBox3DReduction",self._render_product_path_0,False))
        isdg.activate_node_template("BoundingBox3DReduction",0, [self._render_product_path_0], {}, self._stage, False)
        assert(isdg.is_node_template_activated("BoundingBox3DReduction",self._render_product_path_0,False))
        assert(isdg.is_node_template_activated("BoundingBox3DReduction",self._render_product_path_0,True))
        assert(not isdg.is_rendervar_enabled(self._render_product_path_0, render_var, False, self._stage))
        assert(isdg.is_rendervar_used(self._render_product_path_0, render_var))
        isdg.enable_rendervar(self._render_product_path_0, render_var, self._stage)
        assert(isdg.is_rendervar_enabled(self._render_product_path_0, render_var, False, self._stage))
        assert(isdg.is_rendervar_used(self._render_product_path_0, render_var))
        assert(not isdg.is_rendervar_enabled(self._render_product_path_0, render_var, True, self._stage))
        isdg.deactivate_node_template("BoundingBox3DReduction",0, [self._render_product_path_0], self._stage, False)
        assert(not isdg.is_node_template_activated("BoundingBox3DReduction",self._render_product_path_0,True))
        assert(isdg.is_rendervar_enabled(self._render_product_path_0, render_var, False, self._stage))
        assert(not isdg.is_rendervar_used(self._render_product_path_0, render_var))
        isdg.disable_rendervar(self._render_product_path_0, render_var, self._stage)
        assert(not isdg.is_rendervar_enabled(self._render_product_path_0, render_var, False, self._stage))
        assert(not isdg.is_rendervar_used(self._render_product_path_0, render_var))

    async def test_rendervar_hybrid_activation(self):
        isdg = SyntheticData.Get()
        render_var = "BoundingBox3DSD"
        assert(not isdg.is_rendervar_enabled(self._render_product_path_0, render_var, False, self._stage))
        assert(not isdg.is_rendervar_used(self._render_product_path_0, render_var))
        isdg.activate_node_template("BoundingBox3DReduction",0, [self._render_product_path_0], {}, self._stage, False)
        assert(not isdg.is_rendervar_enabled(self._render_product_path_0, render_var, False, self._stage))
        assert(isdg.is_rendervar_used(self._render_product_path_0, render_var))
        isdg.enable_rendervar(self._render_product_path_0, render_var, self._stage)
        assert(isdg.is_rendervar_enabled(self._render_product_path_0, render_var, False, self._stage))
        assert(isdg.is_rendervar_used(self._render_product_path_0, render_var))
        isdg.deactivate_node_template("BoundingBox3DReduction",0, [self._render_product_path_0], self._stage, True)
        assert(isdg.is_rendervar_enabled(self._render_product_path_0, render_var, False, self._stage))
        assert(not isdg.is_rendervar_used(self._render_product_path_0, render_var))
        assert(not isdg.is_rendervar_enabled(self._render_product_path_0, render_var, True, self._stage))
        isdg.disable_rendervar(self._render_product_path_0, render_var, self._stage)
        assert(not isdg.is_rendervar_enabled(self._render_product_path_0, render_var, False, self._stage))

    async def test_rendervar_initially_activated(self):
        isdg = SyntheticData.Get()
        render_var = "BoundingBox3DSD"
        assert(not isdg.is_rendervar_enabled(self._render_product_path_0, render_var, False, self._stage))
        assert(not isdg.is_rendervar_used(self._render_product_path_0, render_var))
        isdg.enable_rendervar(self._render_product_path_0, render_var, self._stage)
        assert(isdg.is_rendervar_enabled(self._render_product_path_0, render_var, False, self._stage))
        assert(not isdg.is_rendervar_used(self._render_product_path_0, render_var))
        isdg.activate_node_template("BoundingBox3DReduction",0, [self._render_product_path_0], {}, self._stage, True)
        assert(isdg.is_rendervar_enabled(self._render_product_path_0, render_var, False, self._stage))
        assert(isdg.is_rendervar_used(self._render_product_path_0, render_var))
        assert(not isdg.is_rendervar_enabled(self._render_product_path_0, render_var, True, self._stage))
        isdg.deactivate_node_template("BoundingBox3DReduction",0, [self._render_product_path_0], self._stage, True)
        assert(isdg.is_rendervar_enabled(self._render_product_path_0, render_var, False, self._stage))
        assert(not isdg.is_rendervar_used(self._render_product_path_0, render_var))
        isdg.disable_rendervar(self._render_product_path_0, render_var, self._stage)
        assert(not isdg.is_rendervar_enabled(self._render_product_path_0, render_var, False, self._stage))

    async def test_rendervar_multiple_activation(self):
        isdg = SyntheticData.Get()
        render_var = "BoundingBox3DSD"
        if not isdg.is_node_template_registered("BoundingBox3DDisplayPostDuplicate"):
            isdg.register_node_template(
                SyntheticData.NodeTemplate(
                    SyntheticDataStage.POST_RENDER,
                    "omni.syntheticdata.SdPostRenderVarDisplayTexture",
                    [
                        SyntheticData.NodeConnectionTemplate("LdrColorSD"),
                        SyntheticData.NodeConnectionTemplate("Camera3dPositionSD"),
                        SyntheticData.NodeConnectionTemplate("PostRenderProductCamera"),
                        SyntheticData.NodeConnectionTemplate("InstanceMappingPost"),
                        SyntheticData.NodeConnectionTemplate("BoundingBox3DReduction")
                    ],
                    {
                        "inputs:renderVar": "LdrColorSD",
                        "inputs:renderVarDisplay": "BoundingBox3DSDDisplay",
                        "inputs:mode": "semanticBoundingBox3dMode",
                        "inputs:parameters": [0.0, 5.0, 0.027, 0.27]
                    }
                ), # node template default attribute values (when differs from the default value specified in the .ogn)
                template_name="BoundingBox3DDisplayPostDuplicate" # node template name
            )
        assert(not isdg.is_rendervar_enabled(self._render_product_path_0, render_var, False, self._stage))
        assert(not isdg.is_rendervar_used(self._render_product_path_0, render_var))
        isdg.activate_node_template("BoundingBox3DDisplayPost",0, [self._render_product_path_0], {}, self._stage, True)
        assert(not isdg.is_node_template_activated("BoundingBox3DReduction",self._render_product_path_0,True))
        assert(isdg.is_node_template_activated("BoundingBox3DReduction",self._render_product_path_0,False))
        assert(isdg.is_rendervar_enabled(self._render_product_path_0, render_var, True, self._stage))
        assert(isdg.is_rendervar_used(self._render_product_path_0, render_var))
        isdg.activate_node_template("BoundingBox3DDisplayPostDuplicate",0, [self._render_product_path_0], {}, self._stage, True)
        isdg.deactivate_node_template("BoundingBox3DDisplayPost",0, [self._render_product_path_0], self._stage, True)
        assert(isdg.is_rendervar_enabled(self._render_product_path_0, render_var, True, self._stage))
        assert(isdg.is_rendervar_used(self._render_product_path_0, render_var))
        assert(not isdg.is_node_template_activated("BoundingBox3DReduction",self._render_product_path_0,True))
        assert(isdg.is_node_template_activated("BoundingBox3DReduction",self._render_product_path_0,False))
        isdg.deactivate_node_template("BoundingBox3DDisplayPostDuplicate",0, [self._render_product_path_0], self._stage, True)
        assert(not isdg.is_node_template_activated("BoundingBox3DReduction",self._render_product_path_0,False))
        assert(not isdg.is_rendervar_enabled(self._render_product_path_0, render_var, True, self._stage))
        assert(not isdg.is_rendervar_used(self._render_product_path_0, render_var))

    async def test_rendervar_intergraph_activation(self):
        isdg = SyntheticData.Get()
        render_var = "BoundingBox3DSD"
        assert(not isdg.is_rendervar_enabled(self._render_product_path_0, render_var, False, self._stage))
        assert(not isdg.is_rendervar_used(self._render_product_path_0, render_var))
        isdg.activate_node_template("BoundingBox3DSDhostPtr",0, [self._render_product_path_0], {}, self._stage, True)
        assert(isdg.is_rendervar_enabled(self._render_product_path_0, render_var, False, self._stage))
        assert(isdg.is_rendervar_used(self._render_product_path_0, render_var))
        isdg.deactivate_node_template("BoundingBox3DSDhostPtr",0, [self._render_product_path_0], self._stage, True)
        assert(not isdg.is_rendervar_enabled(self._render_product_path_0, render_var, False, self._stage))
        assert(not isdg.is_rendervar_used(self._render_product_path_0, render_var))

    async def test_rendervar_intergraph_deactivation(self):
        isdg = SyntheticData.Get()
        if not isdg.is_node_template_registered("SemanticBoundingBox3DInfosSDhostPtrDuplicate"):
             isdg.register_node_template(
                    SyntheticData.NodeTemplate(
                        SyntheticDataStage.ON_DEMAND,
                        "omni.syntheticdata.SdRenderVarPtr",
                        [
                            SyntheticData.NodeConnectionTemplate("SemanticBoundingBox3DInfosSDhost"),
                            SyntheticData.NodeConnectionTemplate("PostProcessDispatch")
                        ],
                        {"inputs:renderVar": "SemanticBoundingBox3DInfosSDhost"}
                    ),
                    template_name="SemanticBoundingBox3DInfosSDhostPtrDuplicate",
                )
        assert(not isdg.is_node_template_activated("BoundingBox3DReduction",self._render_product_path_0,False))
        assert(not isdg.is_node_template_activated("SemanticBoundingBox3DInfosSDPostCopyToHost",self._render_product_path_0,False))
        isdg.activate_node_template("SemanticBoundingBox3DExtentSDhostPtr",0, [self._render_product_path_0], {}, self._stage, True)
        isdg.activate_node_template("SemanticBoundingBox3DInfosSDhostPtrDuplicate",0, [self._render_product_path_0], {}, self._stage, True)
        assert(isdg.is_node_template_activated("BoundingBox3DReduction",self._render_product_path_0,False))
        assert(isdg.is_node_template_activated("SemanticBoundingBox3DInfosSDPostCopyToHost",self._render_product_path_0,False))
        isdg.activate_node_template("SemanticBoundingBox3DInfosSDhostPtr",0, [self._render_product_path_0], {}, self._stage, True)
        assert(isdg.is_node_template_activated("BoundingBox3DReduction",self._render_product_path_0,False))
        assert(isdg.is_node_template_activated("SemanticBoundingBox3DInfosSDPostCopyToHost",self._render_product_path_0,False))
        isdg.deactivate_node_template("SemanticBoundingBox3DExtentSDhostPtr",0, [self._render_product_path_0], self._stage, True)
        assert(isdg.is_node_template_activated("BoundingBox3DReduction",self._render_product_path_0,False))
        assert(isdg.is_node_template_activated("SemanticBoundingBox3DInfosSDPostCopyToHost",self._render_product_path_0,False))
        isdg.deactivate_node_template("SemanticBoundingBox3DInfosSDhostPtrDuplicate",0, [self._render_product_path_0], self._stage, True)
        assert(isdg.is_node_template_activated("BoundingBox3DReduction",self._render_product_path_0,False))
        assert(isdg.is_node_template_activated("SemanticBoundingBox3DInfosSDPostCopyToHost",self._render_product_path_0,False))
        isdg.deactivate_node_template("SemanticBoundingBox3DInfosSDhostPtr",0, [self._render_product_path_0], self._stage, True)
        assert(not isdg.is_node_template_activated("BoundingBox3DReduction",self._render_product_path_0,False))
        assert(not isdg.is_node_template_activated("SemanticBoundingBox3DInfosSDPostCopyToHost",self._render_product_path_0,False))

    # Define an inline node type that is to be used only in this test.
    class InlineCounterPy:
        """Helper inline-defined Python node that simply increments a counter variable"""

        @staticmethod
        def compute(context: og.GraphContext, node: og.Node):
            """Compute method"""
            node.get_attribute("outputs:count").set(node.get_attribute("outputs:count").get() + 1)
            return True

        @staticmethod
        def get_node_type() -> str:
            """Get node type"""
            return "omni.syntheticdata.test.InlineCounterPy"

        @staticmethod
        def initialize_type(node_type: og.NodeType):
            """Initialize node attributes"""
            node_type.add_output("outputs:count", "int", 0)
            return True

    async def _test_direct_graph_manipulation(self, back_graph_by_usd: bool, back_node_by_usd: bool):
        """Wrapper function that contains the main testing logic"""

        isdg = SyntheticData.Get()

        # Create a new (push) graph using the SyntheticData singleton.
        wrapped_graph = None
        with og.Settings.temporary("/exts/omni.syntheticdata/graphBackedByUsd", back_graph_by_usd):
            node_wrapping_graph = isdg._get_or_create_graph(path="/MyGraph", stage=SyntheticDataStage.SIMULATION, renderProductPath=None)
            wrapped_graph = node_wrapping_graph.get_wrapped_graph()

        # Graphs that are created by the SyntheticData singleton with USD backing should have USD notice
        # handling enabled (which allows the graphs to be edited directly via USD, the node editor, etc.).
        self.assertTrue(wrapped_graph.usd_notice_handling_enabled())
        self.assertTrue(wrapped_graph.is_valid())

        # Populate the graph with a simple counter node that will increment its output every time the (push)
        # graph is evaluated.
        counter_node = wrapped_graph.create_node(path="/MyGraph/Counter", node_type=self.InlineCounterPy.get_node_type(), use_usd=back_node_by_usd)
        out_cnt_attr = counter_node.get_attribute("outputs:count")
        self.assertEqual(out_cnt_attr.get(), 0)
        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(out_cnt_attr.get(), 1)

        # Next, delete the USD prim associated with the entire graph.
        self._stage.RemovePrim(wrapped_graph.get_path_to_graph())
        isdg._nodeGraphs = {}  # Manually clear out the nodeGraphs since we explicitly deleted the graph prim earlier.
        await omni.kit.app.get_app().next_update_async()

        # When either the graph and/or its contained node are backed by USD, the OmniGraphUsdListener will pick up on
        # the USD prim deletion and process the destruction of the corresponding OmniGraph, resulting in those objects
        # becoming invalid. Otherwise (i.e. when both the graph and node do not have USD backing) the USD change will
        # not get propagated to OmniGraph, meaning that the push graph and contained node will remain valid and useable.
        # Note that OmniGraphUsdListener will always get triggered and execute its full code-path because (a) we invoked
        # a USD-side change by deleting the graph prim, and (b) the push graph was created as a global graph (which are
        # always handled by OmniGraphUsdListener, regardless of whether or not the USD backing option has been selected).
        if not (not back_graph_by_usd and not back_node_by_usd):
            self.assertFalse(wrapped_graph.is_valid())
            self.assertFalse(counter_node.is_valid())
            self.assertFalse(out_cnt_attr.is_valid())
        else:
            self.assertTrue(wrapped_graph.is_valid())
            self.assertTrue(counter_node.is_valid())
            self.assertTrue(out_cnt_attr.is_valid())
            self.assertEqual(out_cnt_attr.get(), 2)

    async def test_direct_graph_manipulation(self):
        """
        Verify that SyntheticData-generated OmniGraphs respond to USD authoring changes
        when said graphs have USD backing
        """

        # Register the inlined node type.
        og.register_node_type(self.InlineCounterPy, 1)

        # Run the actual test logic with different USD backing options. Make sure to deregister the inlined node type
        # at the end, even if the actual test fails at runtime.
        try:
            await self._test_direct_graph_manipulation(True, True)
            await self._test_direct_graph_manipulation(True, False)
            await self._test_direct_graph_manipulation(False, True)
            await self._test_direct_graph_manipulation(False, False)
        finally:
            self.assertTrue(og.deregister_node_type(self.InlineCounterPy.get_node_type()))

    async def test_direct_graph_manipulation_with_usd_backing_disabled_globally(self):
        """
        Verify that SyntheticData-generated OmniGraphs continue to work as expected when
        OmniGraph USD backing is disabled globally.
        """

        # Register the inlined node type.
        og.register_node_type(self.InlineCounterPy, 1)

        try:
            # Validate that the synthetic data graphs continue to work
            # when the OmniGraphUsdListener is disabled globally
            with og.Settings.temporary("/app/omnigraph/disableUsdBacking", True):
                await self._test_direct_graph_manipulation(False, False)
        finally:
            self.assertTrue(og.deregister_node_type(self.InlineCounterPy.get_node_type()))
