import omni.graph.core as og
import omni.graph.core.tests as ogt
import omni.graph.tools.ogn as ogn

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
            node_type.add_extended_output("outputs:output", "", True, og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_ANY)
            node_type.add_state("state:state", "int", True)

        @staticmethod
        def get_node_type() -> str:
            return _MOCK_NODE_TYPE

    og.register_node_type(OgnSimpleNode, 1)


# -------------------------------------------------------------------------
def _deregister_node_type():
    """Deregister the preloaded node type"""
    og.deregister_node_type(_MOCK_NODE_TYPE)


# -------------------------------------------------------------------------
class OgnSimpleNodePyDatabase(og.Database):
    """Database implementation for the mock node type"""

    INTERFACE = og.Database._get_interface(  # noqa PLW0212
        [
            ("inputs:input", "any", 2, None, "Input a", {}, True, None, False, ""),
            ("outputs:output", "any", 2, None, "The result of a - b", {}, True, None, False, ""),
            (
                "state:state",
                "int",
                0,
                None,
                "The current state of the node",
                {ogn.MetadataKeys.DEFAULT: "1"},
                True,
                1,
                False,
                "",
            ),
        ]
    )


# -------------------------------------------------------------------------
class TestDatabaseAPI(ogt.OmniGraphTestCase):
    """Tests for the database API"""

    # -------------------------------------------------------------------------
    async def setUp(self):
        await super().setUp()
        _register_node_type()

    # -------------------------------------------------------------------------
    async def tearDown(self):
        _deregister_node_type()
        await super().tearDown()

    # -------------------------------------------------------------------------
    def _create_graph_and_node(self, graph_name="/World/TestGraph"):
        (graph, (node,), _, _) = og.Controller.edit(
            graph_name,
            {
                og.Controller.Keys.CREATE_NODES: [
                    ("Node1", _MOCK_NODE_TYPE),
                ]
            },
        )
        return (graph, node)

    # -------------------------------------------------------------------------
    async def test_database_api(self):
        """Test accessor on the ogn database for a node"""
        (graph, node) = self._create_graph_and_node()

        db = OgnSimpleNodePyDatabase(node)

        # access the metadata
        self.assertIsNone(db.get_metadata("InvalidMetadata"))
        self.assertIsNone(db.get_metadata("InvalidAttrMetadata"), node.get_attribute("inputs:input"))

        # test the accessors
        self.assertEqual(db.abi_node, node)
        self.assertEqual(db.abi_context, graph.get_default_graph_context())

        # test the ability to add errors and warnings
        with ogt.ExpectedError():
            db.log_error("This is an error")
        self.assertEqual(len(node.get_compute_messages(og.Severity.ERROR)), 1)
        with ogt.ExpectedError():
            db.log_warn("This is a warning")
        with ogt.ExpectedError():
            db.log_warning("This is another warning")
        self.assertEqual(len(node.get_compute_messages(og.Severity.WARNING)), 2)
        db.log_info("this is info")
        self.assertEqual(len(node.get_compute_messages(og.Severity.INFO)), 1)

        # internal state
        self.assertIsNone(db.per_instance_internal_state(node))
        self.assertIsNone(db.shared_internal_state(node))
        self.assertIsNone(db.shared_state)
        self.assertIsNone(db.per_instance_state)

        # node errors
        self.assertEqual(OgnSimpleNodePyDatabase.per_node_errors(node), [])

        # variables
        graph.create_variable("var", og.Type(og.BaseDataType.INT))
        graph.create_variable("var_array", og.Type(og.BaseDataType.INT, 1, 1))
        self.assertEqual(db.get_variable("var"), 0)
        db.set_variable("var", 1)
        db.set_variable("var_array", [1])
        self.assertEqual(db.get_variable("var"), 1)
        self.assertEqual(db.get_variable("var_array"), [1])
        self.assertIsNone(db.get_variable("invalid"))
        with self.assertRaises(og.OmniGraphError):
            db.set_variable("invalid", 1)

        # dynamic attributes
        node.create_attribute("inputs:dyn", og.Type(og.BaseDataType.INT))
        node.create_attribute("outputs:dyn_out", og.Type(og.BaseDataType.INT))
        node.create_attribute("state:dyn_state", og.Type(og.BaseDataType.INT))

        dynamic_attributes = db.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT)
        self.assertTrue(dynamic_attributes.has_attribute("dyn"))
        dynamic_attributes.set("dyn", False, 1)
        self.assertEqual(dynamic_attributes.get("dyn"), 1)
        access = og.DynamicAttributeAccess(
            graph.get_default_graph_context(), node, [node.get_attribute("inputs:dyn")], dynamic_attributes
        )
        self.assertEqual("[]", str(access))
        self.assertEqual(dynamic_attributes, access.get_dynamic_attributes())

        dynamic_attributes = db.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT)
        self.assertFalse(dynamic_attributes.has_attribute("dyn"))

        dynamic_attributes = db.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_STATE)
        self.assertFalse(dynamic_attributes.has_attribute("dyn"))
