import carb
import omni.graph.core as og
import omni.graph.core.tests as ogt
import omni.usd


# -------------------------------------------------------------------------
class CarbLogSuppressor:
    def __init__(self):
        self.logging = carb.logging.acquire_logging()
        self.log_was_enabled = self.logging.is_log_enabled()

    def __enter__(self):
        # turn off carb logging so the error does not trigger test failure
        # og logging still works and logs node error message.
        self.logging.set_log_enabled(False)
        return self

    def __exit__(self, *_):
        # restore carb logging
        self.logging.set_log_enabled(self.log_was_enabled)


# -------------------------------------------------------------------------
class TestValueCommands(ogt.OmniGraphTestCase):
    """Unit tests for value OmniGraph commands"""

    _node_type_name = None

    # -------------------------------------------------------------------------
    def _register_node_type(self):
        """Helper to register, a preloaded node type with a couple of inputs"""

        class OgnSimpleNode:
            @staticmethod
            def compute(_context: og.GraphContext, _node: og.Node):
                return True

            @staticmethod
            def initialize_type(node_type: og.NodeType):
                node_type.add_extended_input(
                    "inputs:any_input", "", True, og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_ANY
                )
                node_type.add_input("inputs:int_input", "int", True)

            @staticmethod
            def get_node_type() -> str:
                return "omni.graph.OgnSimpleNode"

        og.register_node_type(OgnSimpleNode, 1)
        self._node_type_name = OgnSimpleNode.get_node_type()

    # -------------------------------------------------------------------------
    def _deregister_node_type(self):
        """Deregister the preloaded node type"""
        if self._node_type_name:
            og.deregister_node_type(self._node_type_name)
        self._node_type_name = None

    # -------------------------------------------------------------------------
    def _create_graph_with_node(self, graph_path="/World/TestGraph"):
        """Helper to set up a graph with a single node"""
        (graph, (node,), _, _) = og.Controller.edit(
            graph_path, {og.Controller.Keys.CREATE_NODES: [("Node", self._node_type_name)]}
        )
        return (graph, node)

    # -------------------------------------------------------------------------
    async def setUp(self):
        await super().setUp()
        self._register_node_type()

    # -------------------------------------------------------------------------
    async def tearDown(self):
        self._deregister_node_type()
        await super().tearDown()

    # -------------------------------------------------------------------------
    async def test_disable_node_command(self):
        """Test the DisableNode OmniGraph command"""
        (_, node) = self._create_graph_with_node()

        self.assertFalse(node.is_disabled())
        og.cmds.DisableNode(node=node)
        self.assertTrue(node.is_disabled())
        omni.kit.undo.undo()
        self.assertFalse(node.is_disabled())
        omni.kit.undo.redo()
        self.assertTrue(node.is_disabled())

    # -------------------------------------------------------------------------
    async def test_enable_node_command(self):
        """Test the EnableNode OmniGraph command"""
        (_, node) = self._create_graph_with_node()
        node.set_disabled(True)
        og.cmds.EnableNode(node=node)
        self.assertFalse(node.is_disabled())
        omni.kit.undo.undo()
        self.assertTrue(node.is_disabled())
        omni.kit.undo.redo()
        self.assertFalse(node.is_disabled())

    # -------------------------------------------------------------------------
    async def test_disable_graph_command(self):
        """Test the DisableGraph OmniGraph command"""
        (graph, _) = self._create_graph_with_node()
        self.assertFalse(graph.is_disabled())
        og.cmds.DisableGraph(graph=graph)
        self.assertTrue(graph.is_disabled())
        omni.kit.undo.undo()
        self.assertFalse(graph.is_disabled())
        omni.kit.undo.redo()
        self.assertTrue(graph.is_disabled())

        # validate it works pathing a graph path
        graph.set_disabled(False)
        og.cmds.DisableGraph(graph=graph.get_path_to_graph())
        self.assertTrue(graph.is_disabled())

    # -------------------------------------------------------------------------
    async def test_enable_graph_command(self):
        """Test the EnableGraph OmniGraph command"""
        (graph, _) = self._create_graph_with_node()
        graph.set_disabled(True)
        self.assertTrue(graph.is_disabled())
        og.cmds.EnableGraph(graph=graph)
        self.assertFalse(graph.is_disabled())
        omni.kit.undo.undo()
        self.assertTrue(graph.is_disabled())
        omni.kit.undo.redo()
        self.assertFalse(graph.is_disabled())

        # validate it works pathing a graph path
        graph.set_disabled(True)
        og.cmds.EnableGraph(graph=graph.get_path_to_graph())
        self.assertFalse(graph.is_disabled())

    # -------------------------------------------------------------------------
    async def test_disable_graph_usd_handler_command(self):
        """Test the DisableGraphUsdHandlee OmniGraph command"""
        (graph, _) = self._create_graph_with_node()
        self.assertTrue(graph.usd_notice_handling_enabled())
        og.cmds.DisableGraphUSDHandler(graph=graph)
        self.assertFalse(graph.usd_notice_handling_enabled())
        omni.kit.undo.undo()
        self.assertTrue(graph.usd_notice_handling_enabled())
        omni.kit.undo.redo()
        self.assertFalse(graph.usd_notice_handling_enabled())

    # -------------------------------------------------------------------------
    async def test_enable_graph_usd_handler_command(self):
        """Test the EnableGraph OmniGraph command"""
        (graph, _) = self._create_graph_with_node()
        graph.set_usd_notice_handling_enabled(False)
        self.assertFalse(graph.usd_notice_handling_enabled())
        og.cmds.EnableGraphUSDHandler(graph=graph)
        self.assertTrue(graph.usd_notice_handling_enabled())
        omni.kit.undo.undo()
        self.assertFalse(graph.usd_notice_handling_enabled())
        omni.kit.undo.redo()
        self.assertTrue(graph.usd_notice_handling_enabled())

    # -------------------------------------------------------------------------
    async def test_rename_node_command(self):
        """Test the RenameNode OmniGraph command"""
        (graph, node) = self._create_graph_with_node()
        node_path = node.get_prim_path()

        # Suppress carb logs instead of ogt.ExpectedError because the renaming a node
        # is causing other extensions to load, throwing off the logging.

        # test error handling - invalid path
        with CarbLogSuppressor():
            og.cmds.RenameNode(graph=graph, path=node.get_prim_path(), new_path="An Invalid Path")
            self.assertTrue(node.is_valid())
            self.assertEqual(node.get_prim_path(), node_path)

        # test error handling - existing path
        with CarbLogSuppressor():
            og.cmds.RenameNode(graph=graph, path=node.get_prim_path(), new_path=node.get_prim_path())
            self.assertTrue(node.is_valid())
            self.assertEqual(node.get_prim_path(), node_path)

        new_path = f"{graph.get_path_to_graph()}/new_node"
        og.cmds.RenameNode(graph=graph, path=node.get_prim_path(), new_path=new_path)
        with self.assertRaises(og.OmniGraphError):
            og.Controller.node(node_path)
        self.assertTrue(og.Controller.node(new_path).is_valid())

        omni.kit.undo.undo()
        self.assertTrue(og.Controller.node(node_path).is_valid())
        with self.assertRaises(og.OmniGraphError):
            og.Controller.node(new_path)

        omni.kit.undo.redo()
        with self.assertRaises(og.OmniGraphError):
            og.Controller.node(node_path)
        self.assertTrue(og.Controller.node(new_path).is_valid())

    # -------------------------------------------------------------------------
    async def test_set_attr_command(self):
        """Test the SetAttr Command"""
        (_, node) = self._create_graph_with_node()

        attr = node.get_attribute("inputs:int_input")
        self.assertEqual(og.Controller.get(attr), 0)

        og.cmds.SetAttr(attr=attr, value=1)
        self.assertEqual(og.Controller.get(attr), 1)

        omni.kit.undo.undo()
        self.assertEqual(og.Controller.get(attr), 0)

        omni.kit.undo.redo()
        self.assertEqual(og.Controller.get(attr), 1)

    # -------------------------------------------------------------------------
    async def test_set_attr_data_command(self):
        """Test the SetAttrDataCommand"""
        (_, node) = self._create_graph_with_node()

        attr = node.get_attribute("inputs:int_input")
        attr_data = attr.get_attribute_data()

        self.assertEqual(attr_data.get(), 0)
        og.cmds.SetAttrData(attribute_data=attr_data, value=4)
        self.assertEqual(attr_data.get(), 4)

        omni.kit.undo.undo()
        self.assertEqual(attr_data.get(), 0)

        omni.kit.undo.redo()
        self.assertEqual(attr_data.get(), 4)

        og.cmds.imm.SetAttrData(attribute_data=attr_data, value=5)
        self.assertEqual(attr_data.get(), 5)

        # test with typed data
        with ogt.ExpectedError():
            og.cmds.SetAttrData(
                attribute_data=attr_data, value=og.TypedValue(value=6, type=og.Type(og.BaseDataType.INT))
            )
        self.assertEqual(attr_data.get(), 6)

        with ogt.ExpectedError():
            og.cmds.imm.SetAttrData(
                attribute_data=attr_data, value=og.TypedValue(value=7, type=og.Type(og.BaseDataType.INT))
            )
        self.assertEqual(attr_data.get(), 7)

    # -------------------------------------------------------------------------
    async def test_change_pipeline_stage_command(self):
        """Test changing the pipeline stage command"""
        (graph, _) = self._create_graph_with_node()
        self.assertEqual(graph.get_pipeline_stage(), og.GraphPipelineStage.GRAPH_PIPELINE_STAGE_SIMULATION)

        og.cmds.ChangePipelineStage(graph=graph, new_pipeline_stage=og.GraphPipelineStage.GRAPH_PIPELINE_STAGE_ONDEMAND)
        self.assertEqual(graph.get_pipeline_stage(), og.GraphPipelineStage.GRAPH_PIPELINE_STAGE_ONDEMAND)

        omni.kit.undo.undo()
        self.assertEqual(graph.get_pipeline_stage(), og.GraphPipelineStage.GRAPH_PIPELINE_STAGE_SIMULATION)

        omni.kit.undo.redo()
        self.assertEqual(graph.get_pipeline_stage(), og.GraphPipelineStage.GRAPH_PIPELINE_STAGE_ONDEMAND)

    # -------------------------------------------------------------------------
    async def test_change_set_evaluation_mode_command(self):
        """Test changing the evaluation mode command"""
        (graph, _) = self._create_graph_with_node()
        self.assertEqual(graph.evaluation_mode, og.GraphEvaluationMode.GRAPH_EVALUATION_MODE_AUTOMATIC)

        og.cmds.SetEvaluationMode(
            graph=graph, new_evaluation_mode=og.GraphEvaluationMode.GRAPH_EVALUATION_MODE_STANDALONE
        )
        self.assertEqual(graph.evaluation_mode, og.GraphEvaluationMode.GRAPH_EVALUATION_MODE_STANDALONE)

        omni.kit.undo.undo()
        self.assertEqual(graph.evaluation_mode, og.GraphEvaluationMode.GRAPH_EVALUATION_MODE_AUTOMATIC)

        omni.kit.undo.redo()
        self.assertEqual(graph.evaluation_mode, og.GraphEvaluationMode.GRAPH_EVALUATION_MODE_STANDALONE)

    # -------------------------------------------------------------------------
    async def test_map_attr_command(self):
        """Test the Map Attr command"""
        (_, node) = self._create_graph_with_node()
        int_attr = node.get_attribute("inputs:int_input")

        og.cmds.MapAttr(attr=int_attr, mapping="xformOp:translate")
        self.assertEqual(int_attr.target_mapping, "xformOp:translate")

        omni.kit.undo.undo()
        self.assertEqual(int_attr.target_mapping, None)

        omni.kit.undo.redo()
        self.assertEqual(int_attr.target_mapping, "xformOp:translate")

    # -------------------------------------------------------------------------
    async def test_rename_subgraph_command(self):
        """Test the rename subgraph command"""
        (graph, _) = self._create_graph_with_node()
        sub_graph = graph.create_subgraph(graph.get_path_to_graph() + "/SubGraph", "push")

        sub_graph_path = sub_graph.get_path_to_graph()
        rename_path = graph.get_path_to_graph() + "/NewSubGraph"

        og.cmds.RenameSubgraph(graph=graph, path=sub_graph_path, new_path=rename_path)
        self.assertTrue(og.Controller.graph(rename_path).is_valid())
        self.assertIsNone(og.Controller.graph(sub_graph_path))

        omni.kit.undo.undo()
        self.assertTrue(og.Controller.graph(sub_graph_path).is_valid())
        self.assertIsNone(og.Controller.graph(rename_path))

        omni.kit.undo.redo()
        self.assertTrue(og.Controller.graph(rename_path).is_valid())
        self.assertIsNone(og.Controller.graph(sub_graph_path))

        # error cases
        with CarbLogSuppressor():
            (_, success) = og.cmds.RenameSubgraph(graph=graph, path=rename_path, new_path="An Invalid Prim Path")
            self.assertFalse(success)

        with CarbLogSuppressor():
            (_, success) = og.cmds.RenameSubgraph(graph=graph, path=rename_path, new_path=rename_path)
            self.assertFalse(success)

        with CarbLogSuppressor():
            (_, success) = og.cmds.RenameSubgraph(
                graph=graph, path=rename_path + "_invalid", new_path=rename_path + "_valid"
            )
            self.assertFalse(success)
