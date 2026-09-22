"""Tests related to type resolution methods"""

from functools import lru_cache

import carb
import omni.graph.core as og
import omni.graph.core.tests as ogts
import omni.graph.core.types as ot

from .test_type_conversions import _test_data

UNKNOWN_TYPE = og.Type(og.BaseDataType.UNKNOWN)
INVALID_RESOLVED_TYPES = [
    og.Type(og.BaseDataType.RELATIONSHIP, 1, 0, og.AttributeRole.BUNDLE),
    og.Type(og.BaseDataType.RELATIONSHIP, 1, 0, og.AttributeRole.TARGET),
    og.Type(og.BaseDataType.UINT, 1, 0, og.AttributeRole.EXECUTION),
]


# ------------------------------------------------------------------------------
@lru_cache(maxsize=1)
def _test_resolvable_types() -> list[list]:
    """
    Helper to return the suite of types for testing that an input or output can be resolved to
    Returns:
        A list of lists of type formats: [OGN, SDF, PYTHON_ANNOTATION, ATTRIBUTE_TYPE]
    """

    def is_resolvable(ogn_type, og_type):
        return ogn_type != "any" and og_type not in INVALID_RESOLVED_TYPES

    return [(a, b, c, d) for (a, b, c, d) in _test_data() if is_resolvable(a, d)]


# =============================================================================
class RegisteredNodeType:
    """Helper RAII class for registering node types"""

    def __init__(self, node_type_class):
        self._node_type_class = node_type_class
        self._node_type_name = node_type_class.get_node_type()
        self.active = False

    def __enter__(self):
        self.active = True
        og.register_node_type(self._node_type_class, 1)

    def __exit__(self, _exit_type, _value, _exit_traceback):
        if self.active:
            og.deregister_node_type(self._node_type_name)
        self.active = False


# =============================================================================
class TestTypeResolutions(ogts.OmniGraphTestCase):
    """Tests for the built-in type resolution methods"""

    # -------------------------------------------------------------------------
    async def setUp(self):
        """Called to intialize a test"""
        self.enable_type_resolution = True
        self._graph_num = 0
        self._node_type_name = None
        self._cache_graph = None
        await super().setUp()
        self._register_node_type()
        self._logging = carb.logging.acquire_logging()
        self._log_was_enabled = self._logging.is_log_enabled()

    # -------------------------------------------------------------------------
    async def tearDown(self):
        """Called to deconstruct a test"""
        self._deregister_node_type()
        self._logging.set_log_enabled(self._log_was_enabled)
        await super().tearDown()

    # -------------------------------------------------------------------------
    def _register_node_type(self):
        """Helper to register, or re-register the preloaded node type"""

        class OgnResolveTypeTest:
            @staticmethod
            def compute(_context: og.GraphContext, _node: og.Node):
                return True

            @staticmethod
            def on_connection_type_resolve(node: og.Node):
                if self.enable_type_resolution:
                    a_attr = node.get_attribute("inputs:a")
                    b_attr = node.get_attribute("inputs:b")
                    c_attr = node.get_attribute("outputs:c")

                    node.resolve_partially_coupled_attributes(
                        attributesArray=[a_attr, b_attr, c_attr],
                        tuplesArray=[None, None, None],
                        arraySizesArray=[None, None, None],
                        rolesArray=[og.AttributeRole.UNKNOWN, og.AttributeRole.UNKNOWN, og.AttributeRole.UNKNOWN],
                    )

            @staticmethod
            def initialize_type(node_type: og.NodeType):
                node_type.add_extended_input("inputs:a", "", True, og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_ANY)
                node_type.add_extended_input("inputs:b", "", True, og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_ANY)
                node_type.add_extended_output("outputs:c", "", True, og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_ANY)

            @staticmethod
            def get_node_type() -> str:
                return "omni.graph.OgnResolveTypeTest"

        self._deregister_node_type()
        og.register_node_type(OgnResolveTypeTest, 1)
        self._node_type_name = OgnResolveTypeTest.get_node_type()

    # -------------------------------------------------------------------------
    def _deregister_node_type(self):
        """Deregister the preloaded node type"""
        if self._node_type_name:
            og.deregister_node_type(self._node_type_name)
        self._node_type_name = None

    # -------------------------------------------------------------------------
    def _create_resolvable_graph(self):
        """Create a resolvable graph, returning the 2 inputs and 1 output attribute"""
        (_, (node,), _, _) = og.Controller.edit(
            f"/World/Graph{self._graph_num}", {og.Controller.Keys.CREATE_NODES: [("ResolveNode", self._node_type_name)]}
        )
        self._graph_num = self._graph_num + 1
        attr_a = node.get_attribute("inputs:a")
        attr_b = node.get_attribute("inputs:b")
        attr_c = node.get_attribute("outputs:c")
        return (attr_a, attr_b, attr_c)

    # -------------------------------------------------------------------------
    def _print_attributes(self, *args):
        """Debugging helper to print the attributes"""
        display = "Attributes: "
        for arg in args:
            display += f" {arg.get_name()}={arg.get_resolved_type()}"
        print(display)

    # -------------------------------------------------------------------------
    async def test_resolve_partially_coupled_same_type(self):
        """
        Simple test that validates setting two inputs to the same type has the
        output resolved to the same type
        """
        for ogn_name, _, _, og_type in _test_resolvable_types():
            (attr_a, attr_b, attr_c) = self._create_resolvable_graph()
            attr_a.set_resolved_type(og_type)
            attr_b.set_resolved_type(og_type)
            resolved_type = attr_c.get_resolved_type()
            self.assertEqual(og_type, resolved_type, f"Expected {ogn_name} to be the same {og_type} {resolved_type}")

    # -------------------------------------------------------------------------
    async def test_resolve_partially_coupled_single_input(self):
        """
        Tests that a partially coupled resolution with only a single input resolved resolves the other input
        and output to the correct types
        """

        for _, _, _, og_type in _test_resolvable_types():
            # Setting only the first input, resolves the second input and the output
            (attr_a, attr_b, attr_c) = self._create_resolvable_graph()
            attr_a.set_resolved_type(og_type)
            self.assertEqual(og_type, attr_b.get_resolved_type())
            self.assertEqual(og_type, attr_c.get_resolved_type())

            (attr_a, attr_b, attr_c) = self._create_resolvable_graph()
            attr_b.set_resolved_type(og_type)
            self.assertEqual(og_type, attr_b.get_resolved_type())
            self.assertEqual(og_type, attr_c.get_resolved_type())

    # -------------------------------------------------------------------------
    async def test_set_resolved_type_on_any(self):
        """Test set_resolved_type with an any attribute type on known any types"""
        self.enable_type_resolution = False
        (attr_a, _, _) = self._create_resolvable_graph()

        type_list = [a[3] for a in _test_resolvable_types()]
        type_list.append(UNKNOWN_TYPE)
        for og_type in type_list:
            attr_a.set_resolved_type(og_type)
            self.assertEqual(attr_a.get_resolved_type(), og_type)

    # -------------------------------------------------------------------------
    async def test_set_resolved_type_on_extended_attr(self):
        """Test set_resolved_type with an extended attribute"""

        valid_types_ogn = og.AttributeType.get_unions()["integral_scalers"]
        valid_types_og = [
            ot.convert_type(x, ot.DataTypeRepresentation.OGN, ot.DataTypeRepresentation.TYPE) for x in valid_types_ogn
        ]
        valid_types_as_str = ",".join(valid_types_ogn)

        # create a node with an extended attribute that takes integer scalar types
        class OgnExtendedTypeTest:
            @staticmethod
            def compute(_context: og.GraphContext, _node: og.Node):
                return True

            @staticmethod
            def initialize_type(node_type: og.NodeType):
                node_type.add_extended_input(
                    "inputs:a", valid_types_as_str, True, og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_UNION
                )

            @staticmethod
            def get_node_type() -> str:
                return "omni.graph.OgnExtendedTypeTest"

        with RegisteredNodeType(OgnExtendedTypeTest):
            controller = og.Controller()
            (graph, (node,), _, _) = controller.edit(
                "/World/Test", {og.Controller.Keys.CREATE_NODES: [("ExtNode", "omni.graph.OgnExtendedTypeTest")]}
            )

            # set to a valid type
            attr = node.get_attribute("inputs:a")
            attr.set_resolved_type(og.Type(og.BaseDataType.INT))
            self.assertEqual(og.Type(og.BaseDataType.INT), attr.get_resolved_type())
            last_valid_type = og.Type(og.BaseDataType.INT)

            # walk through all the types and validate set_resolve_types correct sets
            for _, _, _, og_type in _test_resolvable_types():
                is_valid = og_type in valid_types_og
                if is_valid:
                    attr.set_resolved_type(og_type)
                    self.assertEqual(og_type, attr.get_resolved_type())
                else:
                    with ogts.ExpectedError():
                        attr.set_resolved_type(og_type)
                    self.assertEqual(last_valid_type, attr.get_resolved_type())
                last_valid_type = attr.get_resolved_type()

            # check the node unresolves as expected
            attr.set_resolved_type(UNKNOWN_TYPE)
            self.assertEqual(UNKNOWN_TYPE, attr.get_resolved_type())

            # Connect the node to an integer value and walk through valid types and see
            #  if the attribute can be set. It should only be set if it's compatible
            #  with the existing connection type
            (_, _, _, _) = controller.edit(
                graph,
                {
                    controller.Keys.CREATE_NODES: [("Prefix", self._node_type_name)],
                    controller.Keys.SET_VALUES: [
                        ("Prefix.inputs:a", {"value": 1, "type": og.Type(og.BaseDataType.INT)}),
                        ("Prefix.inputs:b", {"value": 1, "type": og.Type(og.BaseDataType.INT)}),
                    ],
                    controller.Keys.CONNECT: [("Prefix.outputs:c", "ExtNode.inputs:a")],
                },
            )

            self.assertEqual(og.Type(og.BaseDataType.INT), attr.get_resolved_type())

            # int based types that are compatible with it
            int_convertable_types = {
                og.Type(og.BaseDataType.INT),
                og.Type(og.BaseDataType.UINT),
                og.Type(og.BaseDataType.INT64),
            }

            for og_type in valid_types_og:
                is_valid = og_type in int_convertable_types
                # reset to int type. Try changing to convertable type
                attr.set_resolved_type(og.Type(og.BaseDataType.INT))
                if is_valid:
                    attr.set_resolved_type(og_type)
                    self.assertEqual(og_type, attr.get_resolved_type())
                else:
                    with ogts.ExpectedError():
                        attr.set_resolved_type(og_type)
                    self.assertEqual(og.Type(og.BaseDataType.INT), attr.get_resolved_type())

    # --------------------------------------------------------------------------
    async def test_set_resolved_type_with_invalid_types(self):
        """Validates that set resolved type fails when using invalid extended types"""
        for og_type in INVALID_RESOLVED_TYPES:
            # Setting only the first input, resolves the second input and the output
            (attr_a, attr_b, attr_c) = self._create_resolvable_graph()
            with ogts.ExpectedError():
                attr_a.set_resolved_type(og_type)

            # validate no resolution happened on any attribute
            self.assertEqual(UNKNOWN_TYPE, attr_a.get_resolved_type())
            self.assertEqual(UNKNOWN_TYPE, attr_b.get_resolved_type())
            self.assertEqual(UNKNOWN_TYPE, attr_c.get_resolved_type())

    # -------------------------------------------------------------------------
    async def test_setting_resolved_types_independently(self):
        """
        Tests to make sure resolved types can be set independently when no coupling exists
        """
        self.enable_type_resolution = False
        types_to_test = [a[3] for a in _test_resolvable_types()]
        type_len = len(types_to_test)

        for i, type_a in enumerate(types_to_test):
            index = int(i + type_len / 2) % type_len
            type_b = types_to_test[index]
            (attr_a, attr_b, _) = self._create_resolvable_graph()

            # set a
            attr_a.set_resolved_type(type_a)
            self.assertEqual(type_a, attr_a.get_resolved_type())
            self.assertEqual(UNKNOWN_TYPE, attr_b.get_resolved_type())

            # set b
            attr_b.set_resolved_type(type_b)
            self.assertEqual(type_a, attr_a.get_resolved_type())
            self.assertEqual(type_b, attr_b.get_resolved_type())

            # unset a
            attr_a.set_resolved_type(UNKNOWN_TYPE)
            self.assertEqual(UNKNOWN_TYPE, attr_a.get_resolved_type())
            self.assertEqual(type_b, attr_b.get_resolved_type())

            # unset b
            attr_b.set_resolved_type(UNKNOWN_TYPE)
            self.assertEqual(UNKNOWN_TYPE, attr_a.get_resolved_type())
            self.assertEqual(UNKNOWN_TYPE, attr_b.get_resolved_type())

    # -------------------------------------------------------------------------
    async def test_connection_to_any_type(self):
        """
        Tests for which types can be connected to an 'any' input and validate the
        type resolves to expected type
        """
        type_to_create = None

        class OgnConstantOutputType:
            @staticmethod
            def compute(_context: og.GraphContext, _node: og.Node):
                return True

            @staticmethod
            def initialize_type(node_type: og.NodeType):
                node_type.add_output("outputs:value", type_to_create, True)

            @staticmethod
            def get_node_type() -> str:
                return "omni.graph.OgnTestConstantType"

        self.enable_type_resolution = False
        types_to_test = _test_resolvable_types()

        # Create a constant node and connect it. The resolved type of the input should be
        # the same type as the output
        for ogn_type, _, _, test_type in types_to_test:
            type_to_create = ogn_type
            with RegisteredNodeType(OgnConstantOutputType):
                (attr_a, attr_b, _) = self._create_resolvable_graph()

                # attribute a is left as an any type
                # attribute b is pre-resolved
                attr_b.set_resolved_type(test_type)

                graph = attr_a.get_node().get_graph()
                (_, (const,), _, _) = og.Controller().edit(
                    graph, {og.Controller.Keys.CREATE_NODES: [("Constant", OgnConstantOutputType.get_node_type())]}
                )
                og.Controller.connect(const.get_attribute("outputs:value"), attr_a)
                og.Controller.connect(const.get_attribute("outputs:value"), attr_b)

                self.assertEqual(1, attr_a.get_upstream_connection_count())
                self.assertEqual(1, attr_b.get_upstream_connection_count())

                self.assertEqual(test_type, attr_a.get_resolved_type())
                self.assertEqual(test_type, attr_b.get_resolved_type())

                # delete the constant node since the type will go away
                graph.destroy_node(const.get_prim_path(), True)

        # verify the invalid types cannot be connected
        for test_type in INVALID_RESOLVED_TYPES:
            type_to_create = ot.convert_type(test_type, ot.DataTypeRepresentation.TYPE, ot.DataTypeRepresentation.OGN)
            with RegisteredNodeType(OgnConstantOutputType):
                (attr_a, _, _) = self._create_resolvable_graph()
                graph = attr_a.get_node().get_graph()
                (_, (const,), _, _) = og.Controller().edit(
                    graph, {og.Controller.Keys.CREATE_NODES: [("Constant", OgnConstantOutputType.get_node_type())]}
                )
                output_attr = const.get_attribute("outputs:value")
                with ogts.ExpectedError():
                    og.Controller.connect(output_attr, attr_a, undoable=True)
                self.assertEqual(0, output_attr.get_downstream_connection_count())
                self.assertEqual(0, attr_a.get_upstream_connection_count())

    # -------------------------------------------------------------------------
    def _test_connection(self, src_type: str, dst_type: str, expected_result: bool):
        """Helper that tests explicit connections between two different resolved types"""

        src_type = ot.convert_type(src_type, ot.DataTypeRepresentation.OGN, ot.DataTypeRepresentation.TYPE)
        dst_type = ot.convert_type(dst_type, ot.DataTypeRepresentation.OGN, ot.DataTypeRepresentation.TYPE)

        controller = og.Controller()
        (_, (node1, node2), _, _) = controller.edit(
            f"/World/Graph{self._graph_num}",
            {controller.Keys.CREATE_NODES: [("Node1", self._node_type_name), ("Node2", self._node_type_name)]},
        )
        self._graph_num = self._graph_num + 1

        node1.get_attribute("inputs:a").set_resolved_type(src_type)
        node1.get_attribute("inputs:b").set_resolved_type(src_type)
        self.assertEqual(src_type, node1.get_attribute("outputs:c").get_resolved_type())

        node2.get_attribute("inputs:a").set_resolved_type(dst_type)
        self.assertEqual(dst_type, node2.get_attribute("inputs:a").get_resolved_type())

        controller.connect(node1.get_attribute("outputs:c"), node2.get_attribute("inputs:a"))
        expected_count = 1 if expected_result else 0

        self.assertEqual(expected_count, node2.get_attribute("inputs:a").get_upstream_connection_count())
        self.assertEqual(dst_type, node2.get_attribute("inputs:a").get_resolved_type())

    # -------------------------------------------------------------------------
    async def test_resolved_connections(self):
        """Test that explicit resolved types can connect to one another"""

        # turn off carb logging, since this is expected to display warnings
        self._logging.set_log_enabled(False)

        self._test_connection("bool", "bool", True)
        self._test_connection("bool", "bool[]", False)
        self._test_connection("bool", "colord[3]", False)
        self._test_connection("bool", "double", False)
        self._test_connection("bool", "float", False)
        self._test_connection("bool", "half", False)
        self._test_connection("bool", "int", False)
        self._test_connection("bool", "int64", False)
        self._test_connection("bool", "objectId", False)
        self._test_connection("bool", "string", False)
        self._test_connection("bool", "timecode", False)
        self._test_connection("bool", "token", False)
        self._test_connection("bool", "uchar", False)
        self._test_connection("bool", "uint", False)
        self._test_connection("bool", "uint64", False)

        self._test_connection("double", "double", True)
        self._test_connection("double", "timecode", True)
        self._test_connection("double", "float", True)
        self._test_connection("double", "int", True)
        self._test_connection("double", "int64", True)
        self._test_connection("double", "bool", False)
        self._test_connection("double", "bool[]", False)
        self._test_connection("double", "colord[3]", False)
        self._test_connection("double", "half", False)
        self._test_connection("double", "objectId", False)
        self._test_connection("double", "string", False)
        self._test_connection("double", "token", False)
        self._test_connection("double", "uchar", False)
        self._test_connection("double", "uint", False)
        self._test_connection("double", "uint64", False)

        self._test_connection("float", "double", True)
        self._test_connection("float", "float", True)
        self._test_connection("float", "int", True)
        self._test_connection("float", "int64", True)
        self._test_connection("float", "timecode", True)
        self._test_connection("float", "bool", False)
        self._test_connection("float", "bool[]", False)
        self._test_connection("float", "colord[3]", False)
        self._test_connection("float", "half", False)
        self._test_connection("float", "objectId", False)
        self._test_connection("float", "string", False)
        self._test_connection("float", "token", False)
        self._test_connection("float", "uchar", False)
        self._test_connection("float", "uint", False)
        self._test_connection("float", "uint64", False)

        self._test_connection("half", "half", True)
        self._test_connection("half", "bool", False)
        self._test_connection("half", "bool[]", False)
        self._test_connection("half", "colord[3]", False)
        self._test_connection("half", "double", False)
        self._test_connection("half", "float", False)
        self._test_connection("half", "int", False)
        self._test_connection("half", "int64", False)
        self._test_connection("half", "objectId", False)
        self._test_connection("half", "string", False)
        self._test_connection("half", "timecode", False)
        self._test_connection("half", "token", False)
        self._test_connection("half", "uchar", False)
        self._test_connection("half", "uint", False)
        self._test_connection("half", "uint64", False)

        self._test_connection("int", "bool", True)
        self._test_connection("int", "double", True)
        self._test_connection("int", "float", True)
        self._test_connection("int", "int", True)
        self._test_connection("int", "int64", True)
        self._test_connection("int", "uint", True)
        self._test_connection("int", "timecode", True)
        self._test_connection("int", "bool[]", False)
        self._test_connection("int", "colord[3]", False)
        self._test_connection("int", "half", False)
        self._test_connection("int", "objectId", False)
        self._test_connection("int", "string", False)
        self._test_connection("int", "token", False)
        self._test_connection("int", "uchar", False)
        self._test_connection("int", "uint64", False)

        self._test_connection("int64", "bool", True)
        self._test_connection("int64", "double", True)
        self._test_connection("int64", "float", True)
        self._test_connection("int64", "int", True)
        self._test_connection("int64", "int64", True)
        self._test_connection("int64", "uint64", True)
        self._test_connection("int64", "timecode", True)
        self._test_connection("int64", "bool[]", False)
        self._test_connection("int64", "colord[3]", False)
        self._test_connection("int64", "half", False)
        self._test_connection("int64", "objectId", False)
        self._test_connection("int64", "string", False)
        self._test_connection("int64", "token", False)
        self._test_connection("int64", "uchar", False)
        self._test_connection("int64", "uint", False)

        self._test_connection("objectId", "objectId", True)
        self._test_connection("objectId", "bool", False)
        self._test_connection("objectId", "bool[]", False)
        self._test_connection("objectId", "colord[3]", False)
        self._test_connection("objectId", "double", False)
        self._test_connection("objectId", "float", False)
        self._test_connection("objectId", "half", False)
        self._test_connection("objectId", "int", False)
        self._test_connection("objectId", "int64", False)
        self._test_connection("objectId", "string", False)
        self._test_connection("objectId", "timecode", False)
        self._test_connection("objectId", "token", False)
        self._test_connection("objectId", "uchar", False)
        self._test_connection("objectId", "uint", False)
        self._test_connection("objectId", "uint64", False)

        self._test_connection("string", "string", True)
        self._test_connection("string", "bool", False)
        self._test_connection("string", "bool[]", False)
        self._test_connection("string", "colord[3]", False)
        self._test_connection("string", "double", False)
        self._test_connection("string", "float", False)
        self._test_connection("string", "half", False)
        self._test_connection("string", "int", False)
        self._test_connection("string", "int64", False)
        self._test_connection("string", "objectId", False)
        self._test_connection("string", "timecode", False)
        self._test_connection("string", "token", False)
        self._test_connection("string", "uchar", False)
        self._test_connection("string", "uint", False)
        self._test_connection("string", "uint64", False)

        self._test_connection("timecode", "timecode", True)
        self._test_connection("timecode", "double", True)
        self._test_connection("timecode", "float", True)
        self._test_connection("timecode", "int", True)
        self._test_connection("timecode", "int64", True)
        self._test_connection("timecode", "bool", False)
        self._test_connection("timecode", "bool[]", False)
        self._test_connection("timecode", "colord[3]", False)
        self._test_connection("timecode", "half", False)
        self._test_connection("timecode", "objectId", False)
        self._test_connection("timecode", "string", False)
        self._test_connection("timecode", "token", False)
        self._test_connection("timecode", "uchar", False)
        self._test_connection("timecode", "uint", False)
        self._test_connection("timecode", "uint64", False)

        self._test_connection("token", "token", True)
        self._test_connection("token", "bool", False)
        self._test_connection("token", "bool[]", False)
        self._test_connection("token", "colord[3]", False)
        self._test_connection("token", "double", False)
        self._test_connection("token", "float", False)
        self._test_connection("token", "half", False)
        self._test_connection("token", "int", False)
        self._test_connection("token", "int64", False)
        self._test_connection("token", "objectId", False)
        self._test_connection("token", "string", False)
        self._test_connection("token", "timecode", False)
        self._test_connection("token", "uchar", False)
        self._test_connection("token", "uint", False)
        self._test_connection("token", "uint64", False)

        self._test_connection("uchar", "uchar", True)
        self._test_connection("uchar", "bool", False)
        self._test_connection("uchar", "bool[]", False)
        self._test_connection("uchar", "colord[3]", False)
        self._test_connection("uchar", "double", False)
        self._test_connection("uchar", "float", False)
        self._test_connection("uchar", "half", False)
        self._test_connection("uchar", "int", False)
        self._test_connection("uchar", "int64", False)
        self._test_connection("uchar", "objectId", False)
        self._test_connection("uchar", "string", False)
        self._test_connection("uchar", "timecode", False)
        self._test_connection("uchar", "token", False)
        self._test_connection("uchar", "uint", False)
        self._test_connection("uchar", "uint64", False)

        self._test_connection("uint", "bool", True)
        self._test_connection("uint", "double", True)
        self._test_connection("uint", "float", True)
        self._test_connection("uint", "int", True)
        self._test_connection("uint", "int64", True)
        self._test_connection("uint", "uint", True)
        self._test_connection("uint", "uint64", True)
        self._test_connection("uint", "timecode", True)
        self._test_connection("uint", "bool[]", False)
        self._test_connection("uint", "colord[3]", False)
        self._test_connection("uint", "half", False)
        self._test_connection("uint", "objectId", False)
        self._test_connection("uint", "string", False)
        self._test_connection("uint", "token", False)
        self._test_connection("uint", "uchar", False)

        self._test_connection("uint64", "bool", True)
        self._test_connection("uint64", "double", True)
        self._test_connection("uint64", "float", True)
        self._test_connection("uint64", "int", True)
        self._test_connection("uint64", "int64", True)
        self._test_connection("uint64", "uint", True)
        self._test_connection("uint64", "uint64", True)
        self._test_connection("uint64", "timecode", True)
        self._test_connection("uint64", "bool[]", False)
        self._test_connection("uint64", "colord[3]", False)
        self._test_connection("uint64", "half", False)
        self._test_connection("uint64", "objectId", False)
        self._test_connection("uint64", "string", False)
        self._test_connection("uint64", "token", False)
        self._test_connection("uint64", "uchar", False)

    # -------------------------------------------------------------------------
    async def test_resolved_connections_tuple_arrays(self):
        """Test that explicit resolved types can connect to one another with a selection of tuple types and arrays"""

        self._logging.set_log_enabled(False)

        self._test_connection("bool[]", "bool[]", True)
        self._test_connection("bool[]", "bool", False)

        self._test_connection("colord[3]", "colord[3]", True)
        self._test_connection("colord[3]", "double[3]", True)
        self._test_connection("colord[3]", "colord[3][]", False)

        self._test_connection("colord[3][]", "colord[3][]", True)
        self._test_connection("colord[3][]", "double[3][]", True)
        self._test_connection("colord[3][]", "colord[3]", False)

        self._test_connection("colord[4]", "colord[4]", True)
        self._test_connection("colord[4]", "double[4]", True)
        self._test_connection("colord[4]", "colord[4][]", False)

        self._test_connection("colord[4][]", "colord[4][]", True)
        self._test_connection("colord[4][]", "double[4][]", True)
        self._test_connection("colord[4][]", "colord[4]", False)

        self._test_connection("colorf[3]", "colorf[3]", True)
        self._test_connection("colorf[3]", "float[3]", True)
        self._test_connection("colorf[3]", "colorf[3][]", False)

        self._test_connection("colorf[3][]", "colorf[3][]", True)
        self._test_connection("colorf[3][]", "float[3][]", True)
        self._test_connection("colorf[3][]", "colorf[3]", False)

        self._test_connection("colorf[4]", "colorf[4]", True)
        self._test_connection("colorf[4]", "float[4]", True)
        self._test_connection("colorf[4]", "colorf[4][]", False)

        self._test_connection("colorf[4][]", "colorf[4][]", True)
        self._test_connection("colorf[4][]", "float[4][]", True)
        self._test_connection("colorf[4][]", "colorf[4]", False)

        self._test_connection("colorh[3]", "colorh[3]", True)
        self._test_connection("colorh[3]", "half[3]", True)
        self._test_connection("colorh[3]", "colorh[3][]", False)

        self._test_connection("colorh[3][]", "colorh[3][]", True)
        self._test_connection("colorh[3][]", "half[3][]", True)
        self._test_connection("colorh[3][]", "colorh[3]", False)

        self._test_connection("colorh[4]", "colorh[4]", True)
        self._test_connection("colorh[4]", "half[4]", True)
        self._test_connection("colorh[4]", "colorh[4][]", False)

        self._test_connection("colorh[4][]", "colorh[4][]", True)
        self._test_connection("colorh[4][]", "half[4][]", True)
        self._test_connection("colorh[4][]", "colorh[4]", False)

        self._test_connection("double[]", "double[]", True)
        self._test_connection("double[]", "double", False)

        self._test_connection("double[2]", "double[2]", True)
        self._test_connection("double[2]", "double[2][]", False)

        self._test_connection("double[2][]", "double[2][]", True)
        self._test_connection("double[2][]", "double[2]", False)

        self._test_connection("double[3]", "double[3]", True)
        self._test_connection("double[3]", "double[3][]", False)

        self._test_connection("double[3][]", "double[3][]", True)
        self._test_connection("double[3][]", "double[3]", False)

        self._test_connection("double[4]", "double[4]", True)
        self._test_connection("double[4]", "double[4][]", False)

        self._test_connection("double[4][]", "double[4][]", True)
        self._test_connection("double[4][]", "double[4]", False)

        self._test_connection("float[]", "float[]", True)
        self._test_connection("float[]", "float", False)

        self._test_connection("float[2]", "float[2]", True)
        self._test_connection("float[2]", "float[2][]", False)

        self._test_connection("float[2][]", "float[2][]", True)
        self._test_connection("float[2][]", "float[2]", False)

        self._test_connection("float[3]", "float[3]", True)
        self._test_connection("float[3]", "float[3][]", False)

        self._test_connection("float[3][]", "float[3][]", True)
        self._test_connection("float[3][]", "float[3]", False)

        self._test_connection("float[4]", "float[4]", True)
        self._test_connection("float[4]", "float[4][]", False)

        self._test_connection("float[4][]", "float[4][]", True)
        self._test_connection("float[4][]", "float[4]", False)

        self._test_connection("frame[4]", "frame[4]", True)
        self._test_connection("frame[4]", "frame[4][]", False)

        self._test_connection("frame[4][]", "frame[4][]", True)
        self._test_connection("frame[4][]", "frame[4]", False)

        self._test_connection("half[]", "half[]", True)
        self._test_connection("half[]", "half", False)

        self._test_connection("half[2]", "half[2]", True)
        self._test_connection("half[2]", "half[2][]", False)

        self._test_connection("half[2][]", "half[2][]", True)
        self._test_connection("half[2][]", "half[2]", False)

        self._test_connection("half[3]", "half[3]", True)
        self._test_connection("half[3]", "half[3][]", False)

        self._test_connection("half[3][]", "half[3][]", True)
        self._test_connection("half[3][]", "half[3]", False)

        self._test_connection("half[4]", "half[4]", True)
        self._test_connection("half[4]", "half[4][]", False)

        self._test_connection("half[4][]", "half[4][]", True)
        self._test_connection("half[4][]", "half[4]", False)

        self._test_connection("int[]", "int[]", True)
        self._test_connection("int[]", "int", False)

        self._test_connection("int[2]", "int[2]", True)
        self._test_connection("int[2]", "int[2][]", False)

        self._test_connection("int[2][]", "int[2][]", True)
        self._test_connection("int[2][]", "int[2]", False)

        self._test_connection("int[3]", "int[3]", True)
        self._test_connection("int[3]", "int[3][]", False)

        self._test_connection("int[3][]", "int[3][]", True)
        self._test_connection("int[3][]", "int[3]", False)

        self._test_connection("int[4]", "int[4]", True)
        self._test_connection("int[4]", "int[4][]", False)

        self._test_connection("int[4][]", "int[4][]", True)
        self._test_connection("int[4][]", "int[4]", False)

        self._test_connection("int64[]", "int64[]", True)
        self._test_connection("int64[]", "int64", False)

        self._test_connection("matrixd[2]", "double[4]", True)
        self._test_connection("matrixd[2]", "matrixd[2]", True)
        self._test_connection("matrixd[2]", "matrixd[2][]", False)

        self._test_connection("matrixd[2][]", "double[4][]", True)
        self._test_connection("matrixd[2][]", "matrixd[2][]", True)
        self._test_connection("matrixd[2][]", "matrixd[2]", False)

        self._test_connection("matrixd[3]", "matrixd[3]", True)
        self._test_connection("matrixd[3]", "matrixd[3][]", False)

        self._test_connection("matrixd[3][]", "matrixd[3][]", True)
        self._test_connection("matrixd[3][]", "matrixd[3]", False)

        self._test_connection("matrixd[4]", "matrixd[4]", True)
        self._test_connection("matrixd[4]", "matrixd[4][]", False)

        self._test_connection("matrixd[4][]", "matrixd[4][]", True)
        self._test_connection("matrixd[4][]", "matrixd[4]", False)

        self._test_connection("normald[3]", "double[3]", True)
        self._test_connection("normald[3]", "normald[3]", True)
        self._test_connection("normald[3]", "normald[3][]", False)

        self._test_connection("normald[3][]", "double[3][]", True)
        self._test_connection("normald[3][]", "normald[3][]", True)
        self._test_connection("normald[3][]", "normald[3]", False)

        self._test_connection("normalf[3]", "float[3]", True)
        self._test_connection("normalf[3]", "normalf[3]", True)
        self._test_connection("normalf[3]", "normalf[3][]", False)

        self._test_connection("normalf[3][]", "float[3][]", True)
        self._test_connection("normalf[3][]", "normalf[3][]", True)
        self._test_connection("normalf[3][]", "normalf[3]", False)

        self._test_connection("normalh[3]", "half[3]", True)
        self._test_connection("normalh[3]", "normalh[3]", True)
        self._test_connection("normalh[3]", "normalh[3][]", False)

        self._test_connection("normalh[3][]", "half[3][]", True)
        self._test_connection("normalh[3][]", "normalh[3][]", True)
        self._test_connection("normalh[3][]", "normalh[3]", False)

        self._test_connection("objectId[]", "objectId[]", True)
        self._test_connection("objectId[]", "objectId", False)
        self._test_connection("objectId[]", "uint64[]", False)

        self._test_connection("pointd[3]", "double[3]", True)
        self._test_connection("pointd[3]", "pointd[3]", True)
        self._test_connection("pointd[3]", "pointd[3][]", False)

        self._test_connection("pointd[3][]", "double[3][]", True)
        self._test_connection("pointd[3][]", "pointd[3][]", True)
        self._test_connection("pointd[3][]", "pointd[3]", False)

        self._test_connection("pointf[3]", "float[3]", True)
        self._test_connection("pointf[3]", "pointf[3]", True)
        self._test_connection("pointf[3]", "pointf[3][]", False)

        self._test_connection("pointf[3][]", "float[3][]", True)
        self._test_connection("pointf[3][]", "pointf[3][]", True)
        self._test_connection("pointf[3][]", "pointf[3]", False)

        self._test_connection("pointh[3]", "half[3]", True)
        self._test_connection("pointh[3]", "pointh[3]", True)
        self._test_connection("pointh[3]", "pointh[3][]", False)

        self._test_connection("pointh[3][]", "half[3][]", True)
        self._test_connection("pointh[3][]", "pointh[3][]", True)
        self._test_connection("pointh[3][]", "pointh[3]", False)

        self._test_connection("quatd[4]", "double[4]", True)
        self._test_connection("quatd[4]", "quatd[4]", True)
        self._test_connection("quatd[4]", "quatd[4][]", False)

        self._test_connection("quatd[4][]", "double[4][]", True)
        self._test_connection("quatd[4][]", "quatd[4][]", True)
        self._test_connection("quatd[4][]", "quatd[4]", False)

        self._test_connection("quatf[4]", "float[4]", True)
        self._test_connection("quatf[4]", "quatf[4]", True)
        self._test_connection("quatf[4]", "quatf[4][]", False)

        self._test_connection("quatf[4][]", "float[4][]", True)
        self._test_connection("quatf[4][]", "quatf[4][]", True)
        self._test_connection("quatf[4][]", "quatf[4]", False)

        self._test_connection("quath[4]", "half[4]", True)
        self._test_connection("quath[4]", "quath[4]", True)
        self._test_connection("quath[4]", "quath[4][]", False)

        self._test_connection("quath[4][]", "half[4][]", True)
        self._test_connection("quath[4][]", "quath[4][]", True)
        self._test_connection("quath[4][]", "quath[4]", False)

        self._test_connection("texcoordd[2]", "double[2]", True)
        self._test_connection("texcoordd[2]", "texcoordd[2]", True)
        self._test_connection("texcoordd[2]", "texcoordd[2][]", False)

        self._test_connection("texcoordd[2][]", "double[2][]", True)
        self._test_connection("texcoordd[2][]", "texcoordd[2][]", True)
        self._test_connection("texcoordd[2][]", "texcoordd[2]", False)

        self._test_connection("texcoordd[3]", "double[3]", True)
        self._test_connection("texcoordd[3]", "texcoordd[3]", True)
        self._test_connection("texcoordd[3]", "texcoordd[3][]", False)

        self._test_connection("texcoordd[3][]", "double[3][]", True)
        self._test_connection("texcoordd[3][]", "texcoordd[3][]", True)
        self._test_connection("texcoordd[3][]", "texcoordd[3]", False)

        self._test_connection("texcoordf[2]", "float[2]", True)
        self._test_connection("texcoordf[2]", "texcoordf[2]", True)
        self._test_connection("texcoordf[2]", "texcoordf[2][]", False)

        self._test_connection("texcoordf[2][]", "float[2][]", True)
        self._test_connection("texcoordf[2][]", "texcoordf[2][]", True)
        self._test_connection("texcoordf[2][]", "texcoordf[2]", False)

        self._test_connection("texcoordf[3]", "float[3]", True)
        self._test_connection("texcoordf[3]", "texcoordf[3]", True)
        self._test_connection("texcoordf[3]", "texcoordf[3][]", False)

        self._test_connection("texcoordf[3][]", "float[3][]", True)
        self._test_connection("texcoordf[3][]", "texcoordf[3][]", True)
        self._test_connection("texcoordf[3][]", "texcoordf[3]", False)

        self._test_connection("texcoordh[2]", "half[2]", True)
        self._test_connection("texcoordh[2]", "texcoordh[2]", True)
        self._test_connection("texcoordh[2]", "texcoordh[2][]", False)

        self._test_connection("texcoordh[2][]", "half[2][]", True)
        self._test_connection("texcoordh[2][]", "texcoordh[2][]", True)
        self._test_connection("texcoordh[2][]", "texcoordh[2]", False)

        self._test_connection("texcoordh[3]", "half[3]", True)
        self._test_connection("texcoordh[3]", "texcoordh[3]", True)
        self._test_connection("texcoordh[3]", "texcoordh[3][]", False)

        self._test_connection("texcoordh[3][]", "half[3][]", True)
        self._test_connection("texcoordh[3][]", "texcoordh[3][]", True)
        self._test_connection("texcoordh[3][]", "texcoordh[3]", False)

        self._test_connection("timecode[]", "timecode[]", True)
        self._test_connection("timecode[]", "double", False)
        self._test_connection("timecode[]", "timecode", False)

        self._test_connection("token[]", "token[]", True)
        self._test_connection("token[]", "token", False)

        self._test_connection("uchar[]", "uchar[]", True)
        self._test_connection("uchar[]", "uchar", False)

        self._test_connection("uint[]", "uint[]", True)
        self._test_connection("uint[]", "uint", False)

        self._test_connection("uint64[]", "uint64[]", True)
        self._test_connection("uint64[]", "uint64", False)

        self._test_connection("vectord[3]", "double[3]", True)
        self._test_connection("vectord[3]", "vectord[3]", True)
        self._test_connection("vectord[3]", "vectord[3][]", False)

        self._test_connection("vectord[3][]", "double[3][]", True)
        self._test_connection("vectord[3][]", "vectord[3][]", True)
        self._test_connection("vectord[3][]", "vectord[3]", False)

        self._test_connection("vectorf[3]", "float[3]", True)
        self._test_connection("vectorf[3]", "vectorf[3]", True)
        self._test_connection("vectorf[3]", "vectorf[3][]", False)

        self._test_connection("vectorf[3][]", "float[3][]", True)
        self._test_connection("vectorf[3][]", "vectorf[3][]", True)
        self._test_connection("vectorf[3][]", "vectorf[3]", False)

        self._test_connection("vectorh[3]", "half[3]", True)
        self._test_connection("vectorh[3]", "vectorh[3]", True)
        self._test_connection("vectorh[3]", "vectorh[3][]", False)

        self._test_connection("vectorh[3][]", "half[3][]", True)
        self._test_connection("vectorh[3][]", "vectorh[3][]", True)
        self._test_connection("vectorh[3][]", "vectorh[3]", False)
