import omni.graph.core as og
import omni.graph.core.tests as ogt
import omni.kit.undo

_MOCK_NODE_TYPE = "omni.graph.test.mocknode"


# -------------------------------------------------------------------------
def _register_node_type():
    """Helper to register, a preloaded node type with a couple of inputs"""

    class OgnSimpleNode:
        @staticmethod
        def compute(_context: og.GraphContext, _node: og.Node):
            return True

        @staticmethod
        def initialize_type(node_type: og.NodeType):
            node_type.add_extended_input("inputs:input", "", True, og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_ANY)
            node_type.add_extended_input("inputs:input2", "", True, og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_ANY)
            node_type.add_input("inputs:bundle", "bundle", True)
            node_type.add_extended_output("outputs:output", "", True, og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_ANY)
            node_type.add_output("outputs_bundle", "bundle", True)

        @staticmethod
        def get_node_type() -> str:
            return _MOCK_NODE_TYPE

    og.register_node_type(OgnSimpleNode, 1)


# -------------------------------------------------------------------------
def _deregister_node_type():
    """Deregister the preloaded node type"""
    og.deregister_node_type(_MOCK_NODE_TYPE)


# -------------------------------------------------------------------------
class TestTopologyCommands(ogt.OmniGraphTestCase):
    """Unit tests for topology-related OmniGraph commands"""

    # -------------------------------------------------------------------------
    async def setUp(self):
        await super().setUp()
        _register_node_type()

    # -------------------------------------------------------------------------
    async def tearDown(self):
        _deregister_node_type()
        await super().tearDown()

    # -------------------------------------------------------------------------
    def _create_graph_and_nodes(self, graph_name="/World/TestGraph"):
        (graph, (node1, node2), _, _) = og.Controller.edit(
            graph_name, {og.Controller.Keys.CREATE_NODES: [("Node1", _MOCK_NODE_TYPE), ("Node2", _MOCK_NODE_TYPE)]}
        )
        return (graph, node1, node2)

    # -------------------------------------------------------------------------
    async def test_connect_prim_command(self):
        """Test the Connect Prim command"""
        (_, node1, node2) = self._create_graph_and_nodes()
        attr = node2.get_attribute("inputs:bundle")
        bundle_path = node1.get_prim_path() + "/outputs_bundle"

        (_, success) = og.cmds.ConnectPrim(attr=attr, prim_path=bundle_path, is_bundle_connection=True)
        self.assertTrue(success)
        self.assertEqual(attr.get_upstream_connection_count(), 1)

        omni.kit.undo.undo()
        self.assertEqual(attr.get_upstream_connection_count(), 0)

        omni.kit.undo.redo()
        self.assertEqual(attr.get_upstream_connection_count(), 1)

    # -------------------------------------------------------------------------
    async def test_disconnect_prim_command(self):
        """Test the disconnect prim command"""
        (_, node1, node2) = self._create_graph_and_nodes()
        attr = node2.get_attribute("inputs:bundle")
        bundle_path = node1.get_prim_path() + "/outputs_bundle"

        og.cmds.ConnectPrim(attr=attr, prim_path=bundle_path, is_bundle_connection=True)
        self.assertEqual(attr.get_upstream_connection_count(), 1)

        og.cmds.DisconnectPrim(attr=attr, prim_path=bundle_path, is_bundle_connection=True)
        self.assertEqual(attr.get_upstream_connection_count(), 0)

        omni.kit.undo.undo()
        self.assertEqual(attr.get_upstream_connection_count(), 1)

        omni.kit.undo.redo()
        self.assertEqual(attr.get_upstream_connection_count(), 0)

    # -------------------------------------------------------------------------
    async def test_connect_attrs_command(self):
        """Test the ConnectAttr Command"""
        (_, node1, node2) = self._create_graph_and_nodes()
        out_attr = node1.get_attribute("outputs:output")
        in_attr = node2.get_attribute("inputs:input")

        og.cmds.ConnectAttrs(src_attr=out_attr, dest_attr=in_attr, modify_usd=True)
        self.assertEqual(out_attr.get_downstream_connection_count(), 1)
        self.assertEqual(in_attr.get_upstream_connection_count(), 1)
        self.assertEqual(out_attr.get_downstream_connections()[0], in_attr)
        self.assertEqual(out_attr, in_attr.get_upstream_connections()[0])

        omni.kit.undo.undo()
        self.assertEqual(out_attr.get_downstream_connection_count(), 0)
        self.assertEqual(in_attr.get_upstream_connection_count(), 0)

        omni.kit.undo.redo()
        self.assertEqual(out_attr.get_downstream_connection_count(), 1)
        self.assertEqual(in_attr.get_upstream_connection_count(), 1)
        self.assertEqual(out_attr.get_downstream_connections()[0], in_attr)
        self.assertEqual(out_attr, in_attr.get_upstream_connections()[0])

    # -------------------------------------------------------------------------
    async def test_disconnect_all_command(self):
        """Test the Disconnect All Command"""
        (_, node1, node2) = self._create_graph_and_nodes()
        out_attr = node1.get_attribute("outputs:output")
        in_attr = node2.get_attribute("inputs:input")

        og.cmds.ConnectAttrs(src_attr=out_attr, dest_attr=in_attr, modify_usd=True)
        self.assertEqual(out_attr.get_downstream_connection_count(), 1)
        self.assertEqual(in_attr.get_upstream_connection_count(), 1)
        self.assertEqual(out_attr.get_downstream_connections()[0], in_attr)
        self.assertEqual(out_attr, in_attr.get_upstream_connections()[0])

        og.cmds.DisconnectAllAttrs(attr=out_attr, modify_usd=True)
        self.assertEqual(out_attr.get_downstream_connection_count(), 0)
        self.assertEqual(in_attr.get_upstream_connection_count(), 0)

        omni.kit.undo.undo()
        self.assertEqual(out_attr.get_downstream_connection_count(), 1)
        self.assertEqual(in_attr.get_upstream_connection_count(), 1)
        self.assertEqual(out_attr.get_downstream_connections()[0], in_attr)
        self.assertEqual(out_attr, in_attr.get_upstream_connections()[0])

        omni.kit.undo.redo()
        self.assertEqual(out_attr.get_downstream_connection_count(), 0)
        self.assertEqual(in_attr.get_upstream_connection_count(), 0)

        # test the immediate command
        og.cmds.ConnectAttrs(src_attr=out_attr, dest_attr=in_attr, modify_usd=True)
        self.assertEqual(in_attr.get_upstream_connection_count(), 1)
        og.cmds.imm.DisconnectAllAttrs(attr=in_attr, modify_usd=True)
        self.assertEqual(in_attr.get_upstream_connection_count(), 0)

    # -------------------------------------------------------------------------
    async def test_disconnect_attr_command(self):
        """Test the Disconnect Attrs Command"""
        (_, node1, node2) = self._create_graph_and_nodes()
        out_attr = node1.get_attribute("outputs:output")
        in_attr = node2.get_attribute("inputs:input")
        in_attr2 = node2.get_attribute("inputs:input2")

        og.cmds.ConnectAttrs(src_attr=out_attr, dest_attr=in_attr, modify_usd=True)
        og.cmds.ConnectAttrs(src_attr=out_attr, dest_attr=in_attr2, modify_usd=True)
        self.assertEqual(out_attr.get_downstream_connection_count(), 2)
        self.assertEqual(in_attr.get_upstream_connection_count(), 1)
        self.assertEqual(in_attr2.get_upstream_connection_count(), 1)

        og.cmds.DisconnectAttrs(src_attr=out_attr, dest_attr=in_attr, modify_usd=True)
        self.assertEqual(out_attr.get_downstream_connection_count(), 1)
        self.assertEqual(in_attr.get_upstream_connection_count(), 0)
        self.assertEqual(in_attr2.get_upstream_connection_count(), 1)

        omni.kit.undo.undo()
        self.assertEqual(out_attr.get_downstream_connection_count(), 2)
        self.assertEqual(in_attr.get_upstream_connection_count(), 1)
        self.assertEqual(in_attr2.get_upstream_connection_count(), 1)

        omni.kit.undo.redo()
        self.assertEqual(out_attr.get_downstream_connection_count(), 1)
        self.assertEqual(in_attr.get_upstream_connection_count(), 0)
        self.assertEqual(in_attr2.get_upstream_connection_count(), 1)

    # -------------------------------------------------------------------------
    async def test_create_attr_command(self):
        """Test the Create Attr command"""
        (_, node, _) = self._create_graph_and_nodes()
        attr_name = "inputs:new_attr"

        og.cmds.CreateAttr(node=node, attr_name=attr_name, attr_type="int")
        self.assertTrue(node.get_attribute(attr_name).is_valid())

        omni.kit.undo.undo()
        with ogt.ExpectedError():
            self.assertFalse(node.get_attribute(attr_name).is_valid())

        omni.kit.undo.redo()
        self.assertTrue(node.get_attribute(attr_name).is_valid())

        # test immediate mode
        attr_name = "inputs:another"
        og.cmds.imm.CreateAttr(node=node, attr_name=attr_name, attr_type="int")
        self.assertTrue(node.get_attribute(attr_name).is_valid())

    # -------------------------------------------------------------------------
    async def test_remove_attr_command(self):
        """Test the Remove Attr command"""
        (_, node, _) = self._create_graph_and_nodes()
        attr_name = "inputs:input"
        self.assertTrue(node.get_attribute(attr_name).is_valid())

        og.cmds.RemoveAttr(attribute=node.get_attribute(attr_name))
        with ogt.ExpectedError():
            self.assertFalse(node.get_attribute(attr_name).is_valid())

        omni.kit.undo.undo()
        self.assertTrue(node.get_attribute(attr_name).is_valid())

        omni.kit.undo.redo()
        with ogt.ExpectedError():
            self.assertFalse(node.get_attribute(attr_name).is_valid())

    # -------------------------------------------------------------------------
    async def test_create_node_command(self):
        """Test the Create Node command"""
        (graph, _, _) = self._create_graph_and_nodes()

        node_path = f"{graph.get_path_to_graph()}/NewNode"

        og.cmds.CreateNode(graph=graph, node_path=node_path, node_type=_MOCK_NODE_TYPE, create_usd=True)
        self.assertTrue(og.Controller.node(node_path).is_valid())

        omni.kit.undo.undo()
        with self.assertRaises(og.OmniGraphError):
            og.Controller.node(node_path)

        omni.kit.undo.redo()
        self.assertTrue(og.Controller.node(node_path).is_valid())

        # create an invalid node
        with ogt.ExpectedError():
            (_, node) = og.cmds.CreateNode(
                graph=graph, node_path=node_path + "2", node_type="omni.no.node.type", create_usd=True
            )
            self.assertFalse(node.is_valid())

    # -------------------------------------------------------------------------
    async def test_create_graph_as_node_command(self):
        """Test the Create Graph As Node command"""
        path = "/World/Graph"
        orchestration_graphs = og.get_global_orchestration_graphs_in_pipeline_stage(
            og.GraphPipelineStage.GRAPH_PIPELINE_STAGE_ONDEMAND
        )
        (result, _) = og.cmds.CreateGraphAsNode(
            graph=orchestration_graphs[0],
            node_name="WrappedNode",
            graph_path="/World/Graph",
            evaluator_name="push",
            is_global_graph=True,
            backed_by_usd=True,
            fc_backing_type=og.GraphBackingType.GRAPH_BACKING_TYPE_FABRIC_SHARED,
            pipeline_stage=og.GraphPipelineStage.GRAPH_PIPELINE_STAGE_ONDEMAND,
        )
        self.assertTrue(result)

        omni.kit.undo.undo()
        with ogt.ExpectedError():
            self.assertIsNone(og.Controller.graph(path))

        omni.kit.undo.redo()
        self.assertTrue(og.Controller.graph(path).is_valid())

    # -------------------------------------------------------------------------
    async def test_create_subgraph_command(self):
        """Test the Create Subgraph command"""
        (graph, _, _) = self._create_graph_and_nodes()
        subgraph_path = f"{graph.get_path_to_graph()}/SubGraph"

        og.cmds.CreateSubgraph(graph=graph, subgraph_path=subgraph_path, evaluator="push")
        self.assertTrue(graph.get_subgraph(subgraph_path).is_valid())

        omni.kit.undo.undo()
        self.assertFalse(graph.get_subgraph(subgraph_path).is_valid())

        omni.kit.undo.redo()
        self.assertTrue(graph.get_subgraph(subgraph_path).is_valid())

    # -------------------------------------------------------------------------
    async def test_delete_node_command(self):
        """Test the Delete Node command"""
        (graph, node, _) = self._create_graph_and_nodes()

        node_path = node.get_prim_path()
        og.cmds.DeleteNode(graph=graph, node_path=node_path, modify_usd=True)
        self.assertFalse(graph.get_node(node_path).is_valid())

        omni.kit.undo.undo()
        self.assertTrue(graph.get_node(node_path).is_valid())

        omni.kit.undo.redo()
        self.assertFalse(graph.get_node(node_path).is_valid())

    # -------------------------------------------------------------------------
    async def test_create_variable_command(self):
        """Test the Create Variable Command"""
        (graph, _, _) = self._create_graph_and_nodes()
        variable_name = "myvar"

        og.cmds.CreateVariable(graph=graph, variable_name=variable_name, variable_type=og.Type(og.BaseDataType.INT))
        self.assertTrue(bool(graph.find_variable(variable_name)))

        omni.kit.undo.undo()
        self.assertFalse(bool(graph.find_variable(variable_name)))

        omni.kit.undo.redo()
        self.assertTrue(bool(graph.find_variable(variable_name)))

    # -------------------------------------------------------------------------
    async def test_remove_variable_command(self):
        """Test the Remove Variable Command"""
        (graph, _, _) = self._create_graph_and_nodes()
        variable_name = "myvar"

        og.cmds.CreateVariable(graph=graph, variable_name=variable_name, variable_type=og.Type(og.BaseDataType.INT))
        var = graph.find_variable(variable_name)
        self.assertTrue(bool(var))

        og.cmds.RemoveVariable(graph=graph, variable=var)
        self.assertFalse(bool(graph.find_variable(variable_name)))

        omni.kit.undo.undo()
        self.assertTrue(bool(graph.find_variable(variable_name)))

        omni.kit.undo.redo()
        self.assertFalse(bool(graph.find_variable(variable_name)))

    # -------------------------------------------------------------------------
    async def test_change_variable_type_command(self):
        """Test the Change Variable Type command"""
        (graph, _, _) = self._create_graph_and_nodes()
        variable_name = "myvar"

        og.cmds.CreateVariable(graph=graph, variable_name=variable_name, variable_type=og.Type(og.BaseDataType.INT))
        var = graph.find_variable(variable_name)
        self.assertEqual(var.type, og.Type(og.BaseDataType.INT))

        og.cmds.ChangeVariableType(variable=var, variable_type=og.Type(og.BaseDataType.FLOAT))
        self.assertEqual(var.type, og.Type(og.BaseDataType.FLOAT))

        omni.kit.undo.undo()
        self.assertEqual(var.type, og.Type(og.BaseDataType.INT))

        omni.kit.undo.redo()
        self.assertEqual(var.type, og.Type(og.BaseDataType.FLOAT))

    # -------------------------------------------------------------------------
    async def test_resolve_attr_type_command(self):
        """Test the Resolve Attr Type command"""
        (_, node, _) = self._create_graph_and_nodes()
        attr = node.get_attribute("inputs:input")

        og.cmds.ResolveAttrType(attr=attr, type_id="int")
        self.assertEqual(attr.get_resolved_type(), og.Type(og.BaseDataType.INT))

        omni.kit.undo.undo()
        self.assertEqual(attr.get_resolved_type(), og.Type(og.BaseDataType.UNKNOWN))

        omni.kit.undo.redo()
        self.assertEqual(attr.get_resolved_type(), og.Type(og.BaseDataType.INT))
