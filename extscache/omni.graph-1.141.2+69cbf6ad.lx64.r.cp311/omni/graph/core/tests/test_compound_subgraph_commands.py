from typing import List

import omni.graph.core as og
import omni.graph.core._unstable as ogu
import omni.graph.core.tests as ogts
import omni.usd
import OmniGraphSchema
from pxr import Sdf

COMPOUND_SUBGRAPH_NODE_TYPE = "omni.graph.nodes.CompoundSubgraph"
DEFAULT_SUBGRAPH_NAME = "Subgraph"

_ADD_NODE = "omni.graph.test.Add"
_CONSTANT_DOUBLE_NODE = "omni.graph.test.ConstantDouble"
_COMPOSE3_NODE = "omni.graph.test.Compose3"


# -------------------------------------------------------------------------
def _register_mock_nodes():
    class OgnMockAdd:
        @staticmethod
        def compute(_context: og.GraphContext, _node: og.Node):
            return True

        @staticmethod
        def initialize_type(node_type: og.NodeType):
            node_type.add_extended_input("inputs:a", "", True, og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_ANY)
            node_type.add_extended_input("inputs:b", "", True, og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_ANY)
            node_type.add_extended_output("outputs:sum", "", True, og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_ANY)

        @staticmethod
        def get_node_type() -> str:
            return _ADD_NODE

    class OgnMockConstantDouble:
        @staticmethod
        def compute(_context: og.GraphContext, _node: og.Node):
            return True

        @staticmethod
        def initialize_type(node_type: og.NodeType):
            node_type.add_input("inputs:value", "double", True)

        @staticmethod
        def get_node_type() -> str:
            return _CONSTANT_DOUBLE_NODE

    class OgnMockCompose3:
        @staticmethod
        def compute(_context: og.GraphContext, _node: og.Node):
            return True

        @staticmethod
        def initialize_type(node_type: og.NodeType):
            node_type.add_input("inputs:x", "double", True)
            node_type.add_input("inputs:y", "double", True)
            node_type.add_input("inputs:z", "double", True)
            node_type.add_output("outputs:double3", "double3", True)

        @staticmethod
        def get_node_type() -> str:
            return _COMPOSE3_NODE

    og.register_node_type(OgnMockAdd, 1)
    og.register_node_type(OgnMockConstantDouble, 1)
    og.register_node_type(OgnMockCompose3, 1)


# -------------------------------------------------------------------------
def _unregister_mock_nodes():
    og.deregister_node_type(_ADD_NODE)
    og.deregister_node_type(_CONSTANT_DOUBLE_NODE)
    og.deregister_node_type(_COMPOSE3_NODE)


# -----------------------------------------------------------------------------
class TestCompoundSubgraphCommands(ogts.OmniGraphTestCase):
    """Tests functionality using subgraph-style compound nodes"""

    _test_graph_path = "/World/TestGraph"

    # -------------------------------------------------------------------------
    async def setUp(self):
        await super().setUp()
        _register_mock_nodes()
        omni.kit.commands.set_logging_enabled(False)

    # -------------------------------------------------------------------------
    async def tearDown(self):
        _unregister_mock_nodes()
        omni.timeline.get_timeline_interface().stop()
        await super().tearDown()
        omni.kit.commands.set_logging_enabled(True)

    # -------------------------------------------------------------------------
    def _get_input_attributes(self, node: og.Node) -> List[og.Attribute]:
        return [
            attr
            for attr in node.get_attributes()
            if attr.get_port_type() == og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT
        ]

    # -------------------------------------------------------------------------
    def _get_output_attributes(self, node: og.Node) -> List[og.Attribute]:
        return [
            attr
            for attr in node.get_attributes()
            if attr.get_port_type() == og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT
        ]

    # ------------------------------------------------------------------------
    async def test_create_compound_subgraph_command(self):
        """Validates the create compound subgraph command, including undo and redo"""
        controller = og.Controller(update_usd=True)
        keys = controller.Keys
        (graph, _, _, _) = controller.edit(self._test_graph_path, {keys.CREATE_NODES: ("Add", _ADD_NODE)})

        # create a compound subgraph with the default name
        stage = omni.usd.get_context().get_stage()

        # validate the node is created
        ogu.cmds.CreateCompoundSubgraph(graph=graph, node_name="Node1", subgraph_name=DEFAULT_SUBGRAPH_NAME)
        node = graph.get_node(f"{self._test_graph_path}/Node1")
        subgraph_path = f"{node.get_prim_path()}/{DEFAULT_SUBGRAPH_NAME}"
        self.assertTrue(node.is_valid())
        self.assertTrue(stage.GetPrimAtPath(subgraph_path).IsValid())

        omni.kit.undo.undo()
        node = graph.get_node(f"{self._test_graph_path}/Node1")
        self.assertFalse(node.is_valid())
        self.assertFalse(stage.GetPrimAtPath(subgraph_path).IsValid())

        omni.kit.undo.redo()
        node = graph.get_node(f"{self._test_graph_path}/Node1")
        self.assertTrue(node.is_valid())
        self.assertTrue(stage.GetPrimAtPath(subgraph_path).IsValid())

        # validate with a different subgraph name
        subgraph2_name = f"{DEFAULT_SUBGRAPH_NAME}_02"
        ogu.cmds.CreateCompoundSubgraph(graph=graph, node_name="Node2", subgraph_name=subgraph2_name)
        node = graph.get_node(f"{self._test_graph_path}/Node2")
        subgraph_path = f"{node.get_prim_path()}/{subgraph2_name}"
        self.assertTrue(node.is_valid())
        self.assertTrue(stage.GetPrimAtPath(subgraph_path).IsValid())

    # ------------------------------------------------------------------------
    async def test_replace_with_compound_subgraph_input_unresolved_types(self):
        """
        Tests the replace with compound subgraph exposes any unresolved types
        """

        # Partially connected graph of add nodes
        # [Add1]->[Add2]->[Add3]
        #  Add1 a,b are left unresolved
        #  Add2 a is connected, b is resolved
        #  Add3 a is connected, b is unresolved
        controller = og.Controller(update_usd=True)
        keys = controller.Keys
        (_, nodes, _, _) = controller.edit(
            self._test_graph_path,
            {
                keys.CREATE_NODES: [
                    ("Add1", _ADD_NODE),
                    ("Add2", _ADD_NODE),
                    ("Add3", _ADD_NODE),
                ],
                keys.CONNECT: [
                    ("Add1.outputs:sum", "Add2.inputs:a"),
                    ("Add2.outputs:sum", "Add3.inputs:a"),
                ],
            },
        )

        # manually resolve
        nodes[1].get_attribute("inputs:b").set_resolved_type(og.Type(og.BaseDataType.DOUBLE))

        # create the subgraph
        (success, node) = ogu.cmds.ReplaceWithCompoundSubgraph(nodes=[node.get_prim_path() for node in nodes])
        self.assertTrue(success)
        self.assertTrue(node.is_valid())

        inputs = self._get_input_attributes(node)
        outputs = self._get_output_attributes(node)
        self.assertEqual(3, len(inputs))
        self.assertEqual(1, len(outputs))

    # ------------------------------------------------------------------------
    async def test_replace_with_compound_subgraph_catches_common_errors(self):
        """
        Validates ReplaceWithCompoundSubgraph handles typical error conditions
        """
        controller = og.Controller(update_usd=True)
        keys = controller.Keys

        (graph1, (add1,), _, _) = controller.edit(self._test_graph_path, {keys.CREATE_NODES: [("Add", _ADD_NODE)]})

        (_, (add2,), _, _) = controller.edit(f"{self._test_graph_path}_2", {keys.CREATE_NODES: [("Add2", _ADD_NODE)]})

        with ogts.ExpectedError():
            # no nodes means no compound is returned
            (success, node) = ogu.cmds.ReplaceWithCompoundSubgraph(nodes=[])
        self.assertFalse(success)
        self.assertIsNone(node)

        # not all nodes from the same graph
        with ogts.ExpectedError():
            (success, node) = ogu.cmds.ReplaceWithCompoundSubgraph(nodes=[add1.get_prim_path(), add2.get_prim_path()])
        self.assertFalse(success)
        self.assertIsNone(node)

        # invalid nodes
        with ogts.ExpectedError():
            (success, node) = ogu.cmds.ReplaceWithCompoundSubgraph(
                nodes=[add1.get_prim_path(), graph1.get_path_to_graph()]
            )
        self.assertFalse(success)
        self.assertIsNone(node)

    # ------------------------------------------------------------------------
    async def test_replace_with_subgraph_in_nested_compounds_types(self):
        """Tests that replace with compound subgraph works with nested compounds"""
        controller = og.Controller(update_usd=True)
        keys = controller.Keys
        (graph, (_,), _, nodes) = controller.edit(
            self._test_graph_path,
            {
                keys.CREATE_NODES: [
                    (
                        "OuterCompound",
                        {
                            keys.CREATE_NODES: [
                                ("Add", _ADD_NODE),
                            ],
                            keys.PROMOTE_ATTRIBUTES: [
                                ("Add.inputs:a", "inputs:a"),
                                ("Add.inputs:b", "inputs:b"),
                                ("Add.outputs:sum", "outputs:sum"),
                            ],
                        },
                    )
                ],
            },
        )

        graph_path = graph.get_path_to_graph()
        (success, c1) = ogu.cmds.ReplaceWithCompoundSubgraph(nodes=[nodes["Add"]])
        self.assertTrue(success)
        self.assertTrue(c1.is_valid())
        compound_graph = c1.get_compound_graph_instance()
        self.assertTrue(compound_graph.is_valid())
        self.assertTrue(compound_graph.get_node(f"{compound_graph.get_path_to_graph()}/Add").is_valid())
        outer_compound = og.Controller.node(f"{graph_path}/OuterCompound")
        self.assertEqual(c1.get_graph().get_owning_compound_node(), outer_compound)

        # create an extra level of compounds by replacing the new compound with a compound
        # [OuterCompound] -> [C1] -> [Add] becomes
        # [OuterCompound] -> [C2] -> [C1] -> [Add]
        (success, c2) = ogu.cmds.ReplaceWithCompoundSubgraph(nodes=[c1])
        self.assertTrue(success)
        self.assertTrue(c2.is_valid())
        outer_compound = og.Controller.node(f"{graph_path}/OuterCompound")
        self.assertEqual(c2.get_graph().get_owning_compound_node(), outer_compound)
        compound_graph = c2.get_compound_graph_instance()
        sub_graph_node = compound_graph.get_nodes()[0]
        self.assertTrue(sub_graph_node.is_compound_node())
        self.assertTrue(sub_graph_node.get_compound_graph_instance().is_valid())
        add_node = sub_graph_node.get_compound_graph_instance().get_nodes()[0]
        self.assertTrue(add_node.is_valid())
        self.assertEqual(Sdf.Path(add_node.get_prim_path()).name, "Add")

    # -----------------------------------------------------------------------------
    async def tests_rename_compound_command(self):
        """Tests the rename compound command"""
        controller = og.Controller(update_usd=True)
        keys = controller.Keys
        (_, _, _, node_map) = controller.edit(
            self._test_graph_path,
            {
                keys.CREATE_NODES: [
                    ("Compound1", {keys.CREATE_NODES: [("Add1", _ADD_NODE)]}),
                    ("Compound2", {keys.CREATE_NODES: [("Add2", _ADD_NODE)]}),
                    ("Compound3", {keys.CREATE_NODES: [("Add3", _ADD_NODE)]}),
                    ("Compound4", {keys.CREATE_NODES: [("Add4", _ADD_NODE)]}),
                    ("Compound5", {keys.CREATE_NODES: [("Add5", _ADD_NODE)]}),
                ]
            },
        )

        graph_paths = [
            og.Controller.prim_path(node_map[f"Compound{idx}"].get_compound_graph_instance()) for idx in range(1, 6)
        ]
        unstable_cmds = og._unstable.cmds  # noqa: PLW0212

        # success case with undo
        unstable_cmds.RenameCompoundSubgraph(subgraph=graph_paths[0], new_path=graph_paths[0] + "_renamed")
        await omni.kit.app.get_app().next_update_async()
        self.assertTrue(og.Controller.graph(graph_paths[0] + "_renamed"))

        omni.kit.undo.undo()
        await omni.kit.app.get_app().next_update_async()
        self.assertTrue(og.Controller.graph(graph_paths[0]))

        omni.kit.undo.redo()
        await omni.kit.app.get_app().next_update_async()
        self.assertTrue(og.Controller.graph(graph_paths[0] + "_renamed"))

        # failure case - bad path
        with ogts.ExpectedError():
            (res, _) = unstable_cmds.RenameCompoundSubgraph(subgraph=graph_paths[1], new_path="This is an invalid path")
            self.assertFalse(res)

        # failure case - rename to an invalid name in immediate mode
        with ogts.ExpectedError():
            self.assertIsNone(
                unstable_cmds.imm.RenameCompoundSubgraph(subgraph=graph_paths[2], new_path="invalid name")
            )

        # pass by graph
        unstable_cmds.RenameCompoundSubgraph(
            subgraph=og.Controller.graph(graph_paths[3]), new_path=graph_paths[3] + "_renamed"
        )
        await omni.kit.app.get_app().next_update_async()
        self.assertTrue(og.Controller.graph(graph_paths[3] + "_renamed"))

        # failure case - path is not a child of the compound node
        with ogts.ExpectedError():
            self.assertIsNone(unstable_cmds.imm.RenameCompoundSubgraph(graph_paths[4], "/World/OtherPath"))

    # -------------------------------------------------------------------------
    async def test_promote_unconnected(self):
        """
        Test promoting all unconnected inputs/outputs on a node in a compound. Ensure that it also creates a unique name
        """
        controller = og.Controller(update_usd=True)
        keys = controller.Keys

        (graph, (_, _compound_node), _, node_map) = controller.edit(
            "/World/TestGraph",
            {
                keys.CREATE_NODES: [
                    ("ConstDouble", _CONSTANT_DOUBLE_NODE),
                    (
                        "Compound",
                        {
                            keys.CREATE_NODES: [
                                ("Add", _ADD_NODE),
                            ],
                            keys.PROMOTE_ATTRIBUTES: [
                                ("Add.inputs:a", "inputs:a"),
                            ],
                        },
                    ),
                ],
                keys.CONNECT: [
                    ("ConstDouble.inputs:value", "Compound.inputs:a"),
                ],
                keys.SET_VALUES: [("ConstDouble.inputs:value", 2.0)],
            },
        )

        await og.Controller.evaluate(graph)
        self.assertTrue(_compound_node.get_attribute("inputs:a").is_valid())
        self.assertFalse(_compound_node.get_attribute_exists("inputs:b"))
        add_node = node_map["Add"]
        (success, ports) = ogu.cmds.PromoteUnconnectedToCompoundSubgraph(node=add_node, inputs=True, outputs=False)
        self.assertTrue(success)
        self.assertEqual(len(ports), 1)
        self.assertTrue(ports[0].is_valid())
        self.assertEqual(ports[0].get_name(), "inputs:b")
        self.assertTrue(_compound_node.get_attribute("inputs:b").is_valid())

        omni.kit.undo.undo()
        self.assertFalse(_compound_node.get_attribute_exists("inputs:b"))

        omni.kit.undo.redo()
        self.assertTrue(_compound_node.get_attribute("inputs:b").is_valid())


# -----------------------------------------------------------------------------
class TestCompoundSubgraphAttributeCommands(ogts.OmniGraphTestCase):
    """Tests related to commands to add, remove and rename attributes from compound nodes
    containing a subgraph
    """

    _test_graph_path = "/World/TestGraph"

    # -------------------------------------------------------------------------
    async def setUp(self):
        await super().setUp()
        _register_mock_nodes()

        # Set up a subgraph node as follows
        #   The composedouble3 node as fixed-type inputs, so they aren't exposed
        #                |-------------------------------------|
        # [Constant] --> | o(a) -->|------|                    |
        #                |         | Add1 |                    |
        # [Constant] --> | o(b) -->|------| --> |------|       |
        #                |                      | Add2 | --> o |-->[Add3]
        #                | o(b_01) -----------> |------|       |
        #                |                                     |
        #                |            |----------------|       |
        #                |            | ComposeDouble3 | --> o |
        #                |            |----------------|       |
        #                |-------------------------------------|
        #
        # The inputs are a, b, b_01
        # The outputs are sum and double3

        controller = og.Controller(update_usd=True)
        keys = controller.Keys

        (
            _,
            (self._constant_node_1, self._constant_node_2, self._compound_node, self._add3_node),
            _,
            mapping,
        ) = controller.edit(
            self._test_graph_path,
            {
                keys.CREATE_NODES: [
                    ("Constant1", _CONSTANT_DOUBLE_NODE),
                    ("Constant2", _CONSTANT_DOUBLE_NODE),
                    (
                        "Compound",
                        {
                            keys.CREATE_NODES: [
                                ("Add1", _ADD_NODE),
                                ("Add2", _ADD_NODE),
                                ("ComposeDouble3", _COMPOSE3_NODE),
                            ],
                            keys.CONNECT: [
                                ("Add1.outputs:sum", "Add2.inputs:a"),
                            ],
                            keys.SET_VALUES: [
                                ("ComposeDouble3.inputs:x", 5.0),
                            ],
                            keys.PROMOTE_ATTRIBUTES: [
                                ("Add1.inputs:a", "a"),
                                ("Add1.inputs:b", "b"),
                                ("Add2.inputs:b", "b_01"),
                                ("Add2.outputs:sum", "sum"),
                                ("ComposeDouble3.outputs:double3", "double3"),
                            ],
                        },
                    ),
                    ("Add3", _ADD_NODE),
                ],
                keys.CONNECT: [
                    ("Constant1.inputs:value", "Compound.inputs:a"),
                    ("Constant2.inputs:value", "Compound.inputs:b"),
                    ("Compound.outputs:sum", "Add3.inputs:a"),
                ],
                keys.SET_VALUES: [
                    ("Constant1.inputs:value", 5.0),
                ],
            },
        )

        self._add1_node = mapping["Add1"]
        self._add2_node = mapping["Add2"]
        self._compose_node = mapping["ComposeDouble3"]

        self._compound_input_1 = og.ObjectLookup.attribute(("inputs:a", self._compound_node))
        self._compound_input_2 = og.ObjectLookup.attribute(("inputs:b", self._compound_node))
        self._compound_input_3 = og.ObjectLookup.attribute(("inputs:b_01", self._compound_node))
        self._compound_output_1 = og.ObjectLookup.attribute(("outputs:sum", self._compound_node))
        self._compound_output_2 = og.ObjectLookup.attribute(("outputs:double3", self._compound_node))
        self._subgraph = og.ObjectLookup.graph(f"{self._compound_node.get_prim_path()}/Subgraph")

        # disable logging of command errors
        omni.kit.commands.set_logging_enabled(False)

    # -------------------------------------------------------------------------
    async def tearDown(self):
        _unregister_mock_nodes()
        await super().tearDown()
        omni.kit.commands.set_logging_enabled(True)

    # -------------------------------------------------------------------------
    async def test_create_input_command(self):
        """Test that input connections can be successfully added and works with undo and redo"""

        connect_to_attr = og.ObjectLookup.attribute(("inputs:x", self._compose_node))
        (success, attr) = ogu.cmds.CreateCompoundSubgraphInput(
            compound_node=self._compound_node, input_name="added_input", connect_to=connect_to_attr
        )

        self.assertTrue(success)
        self.assertTrue(attr.is_valid())
        self.assertTrue(attr.get_downstream_connections()[0], connect_to_attr)
        # validate the value was copied up to the graph
        self.assertEqual(og.Controller.get(attr), 5.0)

        omni.kit.undo.undo()
        self.assertTrue(self._compound_node.is_valid())
        with self.assertRaises(og.OmniGraphError):
            og.ObjectLookup.attribute(("inputs:added_input", self._compound_node))
        self.assertEqual(og.Controller.get(connect_to_attr), 5.0)

        omni.kit.undo.redo()
        self.assertTrue(self._compound_node.is_valid())
        attr = og.ObjectLookup.attribute(("inputs:added_input", self._compound_node))
        self.assertTrue(attr.is_valid())
        self.assertTrue(attr.get_downstream_connections()[0], connect_to_attr)
        self.assertEqual(og.Controller.get(attr), 5.0)

    # ---------------------------------------------------------------------------
    async def test_resolved_attribute_values_are_copied_on_create(self):
        """Tests that resolved attribute values are copied when used with create input"""

        # create a new node in the graph
        new_node = og.GraphController.create_node(
            node_id=("Add4", self._subgraph), node_type_id=_ADD_NODE, update_usd=True
        )

        attr = og.ObjectLookup.attribute(("inputs:a", new_node))
        attr.set_resolved_type(og.Type(og.BaseDataType.DOUBLE))
        og.Controller.set(attr, 10.0, update_usd=True)
        self.assertEqual(og.Controller.get(attr), 10.0)

        (success, compound_attr) = ogu.cmds.CreateCompoundSubgraphInput(
            compound_node=self._compound_node, input_name="added_input", connect_to=attr
        )

        self.assertTrue(success)
        self.assertTrue(compound_attr.is_valid())
        self.assertEqual(10, og.Controller.get(compound_attr))

    # ---------------------------------------------------------------------------
    async def test_create_input_error_cases(self):
        """Validates known failure cases for create input commands"""

        # 1) connecting to an attribute not in the subgraph
        with ogts.ExpectedError():
            (success, attr) = ogu.cmds.CreateCompoundSubgraphInput(
                compound_node=self._compound_node,
                input_name="added_input",
                connect_to=og.ObjectLookup.attribute("inputs:b", self._add3_node),
            )
        self.assertTrue(success)
        self.assertIsNone(attr)

        # 2) connecting to no/invalid attribute
        with self.assertRaises(og.OmniGraphError):
            (success, attr) = ogu.cmds.CreateCompoundSubgraphInput(
                compound_node=self._compound_node, input_name="added_input", connect_to=None
            )
        with ogts.ExpectedError():
            (success, attr) = ogu.cmds.CreateCompoundSubgraphInput(
                compound_node=self._compound_node, input_name="added_input", connect_to="/World/Path.inputs:not_valid"
            )
        self.assertTrue(success)
        self.assertIsNone(attr)

        # 3) connecting to an existing attribute name
        with ogts.ExpectedError():
            connect_to_attr = og.ObjectLookup.attribute(("inputs:x", self._compose_node))
            (success, attr) = ogu.cmds.CreateCompoundSubgraphInput(
                compound_node=self._compound_node, input_name="a", connect_to=connect_to_attr
            )
        self.assertTrue(success)
        self.assertIsNone(attr)

        # 4) connecting to a non-compound node
        with ogts.ExpectedError():
            (success, attr) = ogu.cmds.CreateCompoundSubgraphInput(
                compound_node=self._add3_node, input_name="other", connect_to=connect_to_attr
            )
        self.assertTrue(success)
        self.assertIsNone(attr)

        # 5) connecting to a connected attribute
        with ogts.ExpectedError():
            (success, attr) = ogu.cmds.CreateCompoundSubgraphInput(
                compound_node=self._compound_node,
                input_name="other",
                connect_to=og.ObjectLookup.attribute(("inputs:a", self._add1_node)),
            )
        self.assertTrue(success)
        self.assertIsNone(attr)

        # 6) connecting to output attribute
        with ogts.ExpectedError():
            (success, attr) = ogu.cmds.CreateCompoundSubgraphInput(
                compound_node=self._compound_node,
                input_name="other",
                connect_to=og.ObjectLookup.attribute(("outputs:sum", self._add1_node)),
            )
        self.assertTrue(success)
        self.assertIsNone(attr)

    # -------------------------------------------------------------------------
    def _validate_create_output_command_with_undo_redo(self, connect_from_attr: og.Attribute):
        """Helper to validate create output"""
        (success, attr) = ogu.cmds.CreateCompoundSubgraphOutput(
            compound_node=self._compound_node, output_name="added_output", connect_from=connect_from_attr
        )

        self.assertTrue(success)
        self.assertTrue(attr.is_valid())
        self.assertTrue(attr.get_upstream_connections()[0], connect_from_attr)

        omni.kit.undo.undo()
        self.assertTrue(self._compound_node.is_valid())
        with self.assertRaises(og.OmniGraphError):
            og.ObjectLookup.attribute(("outputs:added_output", self._compound_node))

        omni.kit.undo.redo()
        self.assertTrue(self._compound_node.is_valid())
        attr = og.ObjectLookup.attribute(("outputs:added_output", self._compound_node))
        self.assertTrue(attr.is_valid())
        self.assertTrue(attr.get_upstream_connections()[0], connect_from_attr)

    # -------------------------------------------------------------------------
    async def test_create_output_command(self):
        """Tests that output connections can be successfully added, including undo, redo"""

        # add a node to the subgraph, so there is an unconnected output
        new_node = og.GraphController.create_node(
            node_id=("Add4", self._subgraph),
            node_type_id=_ADD_NODE,
        )
        connect_from_attr = og.ObjectLookup.attribute(("outputs:sum", new_node))
        self._validate_create_output_command_with_undo_redo(connect_from_attr)

    # -------------------------------------------------------------------------
    async def test_create_output_command_multiple_outputs(self):
        """Tests that the output command connects to an already connected output"""
        connect_from_attr = og.ObjectLookup.attribute(("outputs:sum", self._add2_node))
        self._validate_create_output_command_with_undo_redo(connect_from_attr)

    # -------------------------------------------------------------------------
    async def test_create_output_command_error_cases(self):
        """Tests command error cases of output commands"""

        # 1) connecting to an attribute not in the subgraph
        with ogts.ExpectedError():
            (success, attr) = ogu.cmds.CreateCompoundSubgraphOutput(
                compound_node=self._compound_node,
                output_name="added_output",
                connect_from=og.ObjectLookup.attribute("outputs:sum", self._add3_node),
            )
        self.assertTrue(success)
        self.assertIsNone(attr)

        # 2) connecting to no/invalid attribute
        with self.assertRaises(og.OmniGraphError):
            (success, attr) = ogu.cmds.CreateCompoundSubgraphOutput(
                compound_node=self._compound_node, output_name="added_output", connect_from=None
            )
        with ogts.ExpectedError():
            (success, attr) = ogu.cmds.CreateCompoundSubgraphOutput(
                compound_node=self._compound_node,
                output_name="added_output",
                connect_from="/World/Path.outputs:not_valid",
            )
        self.assertTrue(success)
        self.assertIsNone(attr)

        # 3) connecting to an existing attribute name
        with ogts.ExpectedError():
            connect_from_attr = og.ObjectLookup.attribute(("outputs:double3", self._compose_node))
            (success, attr) = ogu.cmds.CreateCompoundSubgraphOutput(
                compound_node=self._compound_node, output_name="sum", connect_from=connect_from_attr
            )
        self.assertTrue(success)
        self.assertIsNone(attr)

        # 4) connecting to a non-compound node
        with ogts.ExpectedError():
            (success, attr) = ogu.cmds.CreateCompoundSubgraphOutput(
                compound_node=self._add3_node, output_name="other", connect_from=connect_from_attr
            )
        self.assertTrue(success)
        self.assertIsNone(attr)

    # -------------------------------------------------------------------------
    async def test_remove_compound_input(self):
        """Tests the remove compound attribute command can remove an input, including undo and redo"""

        self._compound_input_1.set_resolved_type(og.Type(og.BaseDataType.DOUBLE))
        og.Controller.set(self._compound_input_1, 10.0, update_usd=True)

        connected_attr = self._compound_input_1.get_downstream_connections()[0]
        (success, result) = ogu.cmds.RemoveCompoundSubgraphAttribute(attribute=self._compound_input_1)

        self.assertTrue(success)
        self.assertTrue(result)
        self.assertFalse(self._compound_node.get_attribute_exists("inputs:a"))
        self.assertEqual(0, connected_attr.get_upstream_connection_count())

        omni.kit.undo.undo()
        self.assertTrue(self._compound_node.get_attribute_exists("inputs:a"))
        attr = og.ObjectLookup.attribute(("inputs:a", self._compound_node))
        self.assertGreater(attr.get_downstream_connection_count(), 0)
        self.assertEqual(attr.get_downstream_connections()[0], connected_attr)

        omni.kit.undo.redo()
        self.assertFalse(self._compound_node.get_attribute_exists("inputs:a"))
        self.assertEqual(0, connected_attr.get_upstream_connection_count())

    # -------------------------------------------------------------------------
    async def test_remove_compound_inputs_keeps_resolved_values(self):
        """Test the remove compound attribute restores resolved values"""

        # add the connection to the resolved node
        connect_to_attr = og.ObjectLookup.attribute(("inputs:x", self._compose_node))
        (success, attr) = ogu.cmds.CreateCompoundSubgraphInput(
            compound_node=self._compound_node, input_name="added_input", connect_to=connect_to_attr
        )

        self.assertTrue(success)
        self.assertTrue(attr.is_valid())

        (success, result) = ogu.cmds.RemoveCompoundSubgraphAttribute(attribute=attr)

        self.assertTrue(success)
        self.assertTrue(result)

        connect_to_attr = og.ObjectLookup.attribute(("inputs:x", self._compose_node))
        self.assertEqual(5.0, og.Controller.get(connect_to_attr))

    # -------------------------------------------------------------------------
    async def test_remove_compound_output(self):
        """Tests the remove compound attribute command can remove an output, including undo and redo"""
        connected_attr = self._compound_output_1.get_upstream_connections()[0]
        (success, result) = ogu.cmds.RemoveCompoundSubgraphAttribute(attribute=self._compound_output_1)

        self.assertTrue(success)
        self.assertTrue(result)
        self.assertFalse(self._compound_node.get_attribute_exists("outputs:sum"))
        self.assertEqual(0, connected_attr.get_downstream_connection_count())

        omni.kit.undo.undo()
        self.assertTrue(self._compound_node.get_attribute_exists("outputs:sum"))
        attr = og.ObjectLookup.attribute(("outputs:sum", self._compound_node))
        self.assertGreater(attr.get_upstream_connection_count(), 0)
        self.assertEqual(attr.get_upstream_connections()[0], connected_attr)

        omni.kit.undo.redo()
        self.assertFalse(self._compound_node.get_attribute_exists("outputs:sum"))
        self.assertEqual(0, connected_attr.get_downstream_connection_count())

    # -------------------------------------------------------------------------
    async def test_remove_compound_output_error_cases(self):
        """Validates known failure cases for remove attribute commands"""

        # 1) not a compound node
        with ogts.ExpectedError():
            (success, result) = ogu.cmds.RemoveCompoundSubgraphAttribute(
                attribute=og.ObjectLookup.attribute("inputs:b", self._add3_node)
            )
        self.assertTrue(success)
        self.assertFalse(result)

        # 2) not a valid attribute
        with ogts.ExpectedError():
            (success, result) = ogu.cmds.RemoveCompoundSubgraphAttribute(attribute="/World/Path.outputs:invalid_attr")
        self.assertTrue(success)
        self.assertFalse(result)

    # -------------------------------------------------------------------------
    async def test_rename_compound_input_output(self):
        """Tests the rename input/output functionality"""

        # Rename an input attribute
        upstream = self._compound_input_1.get_upstream_connections()
        downstream = self._compound_input_1.get_downstream_connections()
        old_attr_path = self._compound_input_1.get_path()

        (success, new_attr) = ogu.cmds.RenameCompoundSubgraphAttribute(
            attribute=self._compound_input_1, new_name="new_a"
        )

        # Verify that connections are now on new attr and old attr has been removed
        self.assertTrue(success)
        self.assertTrue(new_attr.is_valid())
        self.assertEqual(new_attr.get_upstream_connections(), upstream)
        self.assertEqual(new_attr.get_downstream_connections(), downstream)
        with self.assertRaises(og.OmniGraphError):
            og.ObjectLookup.attribute(old_attr_path)

        new_attr_path = new_attr.get_path()
        omni.kit.undo.undo()

        # Verify undo restores the old attr and connections
        with self.assertRaises(og.OmniGraphError):
            og.ObjectLookup.attribute(new_attr_path)
        attr = og.ObjectLookup.attribute(old_attr_path)
        self.assertEqual(attr.get_upstream_connections(), upstream)
        self.assertEqual(attr.get_downstream_connections(), downstream)

        # Verify redo
        omni.kit.undo.redo()
        attr = og.ObjectLookup.attribute(new_attr_path)
        self.assertEqual(attr.get_upstream_connections(), upstream)
        self.assertEqual(attr.get_downstream_connections(), downstream)
        with self.assertRaises(og.OmniGraphError):
            og.ObjectLookup.attribute(old_attr_path)

        # Rename an output attribute
        upstream = self._compound_output_1.get_upstream_connections()
        downstream = self._compound_output_1.get_downstream_connections()
        old_attr_path = self._compound_output_1.get_path()

        (success, new_attr) = ogu.cmds.RenameCompoundSubgraphAttribute(
            attribute=self._compound_output_1, new_name="new_sum"
        )

        self.assertTrue(success)
        self.assertTrue(new_attr.is_valid())
        self.assertEqual(new_attr.get_upstream_connections(), upstream)
        self.assertEqual(new_attr.get_downstream_connections(), downstream)

        new_attr_path = new_attr.get_path()
        omni.kit.undo.undo()

        with self.assertRaises(og.OmniGraphError):
            og.ObjectLookup.attribute(new_attr_path)
        attr = og.ObjectLookup.attribute(old_attr_path)
        self.assertEqual(attr.get_upstream_connections(), upstream)
        self.assertEqual(attr.get_downstream_connections(), downstream)

        omni.kit.undo.redo()
        attr = og.ObjectLookup.attribute(new_attr_path)
        self.assertEqual(attr.get_upstream_connections(), upstream)
        self.assertEqual(attr.get_downstream_connections(), downstream)

    # -------------------------------------------------------------------------
    async def test_rename_compound_input_output_error_cases(self):
        """Validates known failure cases for remove attribute commands"""
        # attempt to rename to an existing name
        with ogts.ExpectedError():
            (success, new_attr) = ogu.cmds.RenameCompoundSubgraphAttribute(
                attribute=self._compound_input_1, new_name="b"
            )
            self.assertFalse(success)
            self.assertEqual(new_attr, None)


# -------------------------------------------------------------------------
class TestCompoundNodeTypeCommands(ogts.OmniGraphTestCase):
    """Tests base style compound commands"""

    # -------------------------------------------------------------------------
    async def setUp(self):
        await super().setUp()
        _register_mock_nodes()

    # -------------------------------------------------------------------------
    async def tearDown(self):
        _unregister_mock_nodes()
        await super().tearDown()

    # -------------------------------------------------------------------------
    async def test_replace_with_compound_command(self):
        """Test the ReplaceWithCompound command"""
        (graph, nodes, _, _) = og.Controller.edit(
            "/World/MyGraph",
            {
                og.Controller.Keys.CREATE_NODES: [
                    ("Node1", _ADD_NODE),
                    ("Node2", _ADD_NODE),
                    ("Node3", _ADD_NODE),
                ],
                og.Controller.Keys.CONNECT: [
                    ("Node1.outputs:sum", "Node2.inputs:a"),
                    ("Node2.outputs:sum", "Node3.inputs:a"),
                ],
            },
        )

        paths = [Sdf.Path(node.get_prim_path()) for node in nodes]
        og.cmds.ReplaceWithCompound(nodes=paths)
        self.assertEqual(len(graph.get_nodes()), 1)

        omni.kit.undo.undo()
        self.assertEqual(len(graph.get_nodes()), len(nodes))

        omni.kit.undo.redo()
        self.assertEqual(len(graph.get_nodes()), 1)

    # -------------------------------------------------------------------------
    async def test_create_compound_node_type_attributes(self):
        """Test the CreateCompoundNodeType input and output commands"""

        (success, schema_prim) = ogu.cmds.CreateCompoundNodeType()
        self.assertTrue(success)
        self.assertTrue(schema_prim.GetPrim().IsValid())

        # get the graph prim
        graph_prim = og.Controller.prim(schema_prim.GetOmniGraphAssetRel().GetTargets()[0])

        ogu.cmds.CreateCompoundNodeTypeInput(node_type=schema_prim.GetPrim().GetPath(), input_name="in")
        self.assertTrue(graph_prim.HasAPI(OmniGraphSchema.InputDefAPI, "in"))
        omni.kit.undo.undo()
        self.assertFalse(graph_prim.HasAPI(OmniGraphSchema.InputDefAPI, "in"))
        omni.kit.undo.redo()
        self.assertTrue(graph_prim.HasAPI(OmniGraphSchema.InputDefAPI, "in"))

        ogu.cmds.CreateCompoundNodeTypeOutput(node_type=schema_prim.GetPrim().GetPath(), output_name="out")
        self.assertTrue(graph_prim.HasAPI(OmniGraphSchema.OutputDefAPI, "out"))
        omni.kit.undo.undo()
        self.assertFalse(graph_prim.HasAPI(OmniGraphSchema.OutputDefAPI, "out"))
        omni.kit.undo.redo()
        self.assertTrue(graph_prim.HasAPI(OmniGraphSchema.OutputDefAPI, "out"))

    # -------------------------------------------------------------------------
    async def test_remove_compound_node_type_attributes(self):
        """Test the RemoveCompoundNodeType input and output commands"""

        # Set up a compound
        (_, schema_prim) = ogu.cmds.CreateCompoundNodeType()
        graph_prim = og.Controller.prim(schema_prim.GetOmniGraphAssetRel().GetTargets()[0])
        ogu.cmds.CreateCompoundNodeTypeInput(node_type=schema_prim.GetPrim().GetPath(), input_name="in")
        ogu.cmds.CreateCompoundNodeTypeOutput(node_type=schema_prim.GetPrim().GetPath(), output_name="out")
        self.assertTrue(graph_prim.HasAPI(OmniGraphSchema.InputDefAPI, "in"))
        self.assertTrue(graph_prim.HasAPI(OmniGraphSchema.OutputDefAPI, "out"))

        ogu.cmds.RemoveCompoundNodeTypeInput(node_type=schema_prim.GetPrim().GetPath(), input_name="in")
        self.assertFalse(graph_prim.HasAPI(OmniGraphSchema.InputDefAPI, "in"))
        omni.kit.undo.undo()
        self.assertTrue(graph_prim.HasAPI(OmniGraphSchema.InputDefAPI, "in"))
        omni.kit.undo.redo()
        self.assertFalse(graph_prim.HasAPI(OmniGraphSchema.InputDefAPI, "in"))

        ogu.cmds.RemoveCompoundNodeTypeOutput(node_type=schema_prim.GetPrim().GetPath(), output_name="out")
        self.assertFalse(graph_prim.HasAPI(OmniGraphSchema.OutputDefAPI, "out"))
        omni.kit.undo.undo()
        self.assertTrue(graph_prim.HasAPI(OmniGraphSchema.OutputDefAPI, "out"))
        omni.kit.undo.redo()
        self.assertFalse(graph_prim.HasAPI(OmniGraphSchema.OutputDefAPI, "out"))
