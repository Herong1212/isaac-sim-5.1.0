import omni.graph.core as og
import omni.graph.core.tests as ogt
from pxr import Sdf, Usd

_MOCK_NODE_TYPE = "omni.graph.test.mock"


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
            node_type.add_input("inputs:fixed_type", "float", True)
            node_type.add_input("inputs:target", "target", True)

        @staticmethod
        def get_node_type() -> str:
            return _MOCK_NODE_TYPE

    og.register_node_type(OgnSimpleNode, 1)


# -------------------------------------------------------------------------
def _deregister_node_type():
    """Deregister the preloaded node type"""
    og.deregister_node_type(_MOCK_NODE_TYPE)


# -------------------------------------------------------------------------
class TestControllers(ogt.OmniGraphTestCase):
    """Additional tests for og.Controller related classes

    Note: omni.graph.test contain more comprehensive tests for og.Controller related classes
    Tests here focus mostly on edge cases and errors
    """

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
    def test_graph_controller_api(self):
        """Tests for the og.GraphController API"""
        (graph, node) = self._create_graph_and_node()
        graph_controller = og.GraphController()

        # Create graph tests
        with self.assertRaises(og.OmniGraphError):  # no graph id
            og.GraphController.create_graph({"no_graph_id": "no_graph_id"})
        with self.assertRaises(og.OmniGraphError):  # invalid graph id
            og.GraphController.create_graph(graph)
        valid_not_undoable = og.GraphController.create_graph("/World/NoUndoGraph", undoable=False)
        self.assertTrue(valid_not_undoable.is_valid())
        valid_from_dict = og.GraphController.create_graph({"graph_path": "/World/GraphFromDict"})
        self.assertTrue(valid_from_dict)

        # create node tests
        with self.assertRaises(og.OmniGraphError):  # version id supplied
            og.GraphController.create_node(node.get_prim_path() + "2", _MOCK_NODE_TYPE, version=1)
        with self.assertRaises(og.OmniGraphError):  # bad graph, node pair
            og.GraphController.create_node((node.get_prim_path() + "3", "/NotValidGraph"), _MOCK_NODE_TYPE)
        with self.assertRaises(og.OmniGraphError):  # bad graph, node pair
            og.GraphController.create_node((node, graph.get_path_to_graph()), _MOCK_NODE_TYPE)
        with self.assertRaises(og.OmniGraphError):  # bad node path
            og.GraphController.create_node("/NotValidGraph/Node", _MOCK_NODE_TYPE)
        with self.assertRaises(og.OmniGraphError):  # existing node
            og.GraphController.create_node(node.get_prim_path(), _MOCK_NODE_TYPE)
        not_undoable_node = og.GraphController.create_node(
            f"{graph.get_path_to_graph()}/NewNode", _MOCK_NODE_TYPE, undoable=False
        )
        self.assertTrue(not_undoable_node.is_valid())
        self.assertEqual(og.GraphController.create_node(node.get_prim_path(), _MOCK_NODE_TYPE, allow_exists=True), node)
        from_obj_node = graph_controller.create_node(node.get_prim_path() + "_obj", _MOCK_NODE_TYPE)
        self.assertTrue(from_obj_node.is_valid())

        # delete node
        self.assertTrue(og.GraphController.delete_node([]))
        with self.assertRaises(og.OmniGraphError):
            og.GraphController.delete_node([("/InvalidPair", "Node")])
        with self.assertRaises(og.OmniGraphError):
            og.GraphController.delete_node("/InvalidNode")
        og.GraphController.delete_node(not_undoable_node)
        self.assertFalse(not_undoable_node.is_valid())
        graph_controller.delete_node(from_obj_node, undoable=False)
        self.assertFalse(from_obj_node.is_valid())

        # create prim
        with self.assertRaises(og.OmniGraphError):  # bad prim paths
            og.GraphController.create_prim(graph.get_path_to_graph() + "/Prim")
        with self.assertRaises(og.OmniGraphError):  # invalid attributes
            og.GraphController.create_prim("/World/Prim", attribute_values=["A", "List"])
        prim = og.GraphController.create_prim("/World/Prim")
        self.assertTrue(prim.IsValid())
        with self.assertRaises(og.OmniGraphError):
            og.GraphController.create_prim("/World/Prim")
        self.assertEqual(og.GraphController.create_prim("/World/Prim", allow_exists=True), prim)
        self.assertTrue(og.GraphController.create_prim("/World/PrimNoUndo", undoable=False).IsValid())
        prim_with_values = og.GraphController.create_prim(
            prim_path="/World/PrimPlusValues",
            attribute_values={
                "someFloat": ("float", 3.0),
                "inputs:float3": (og.Type(og.BaseDataType.FLOAT, 3), [1.0, 2.0, 3.0]),
                "someFloat3": ("float[3]", [4.0, 5.0, 6.0]),
                "someColor": ("color3d", [0.5, 0.6, 0.2]),
            },
        )
        self.assertTrue(prim_with_values.IsValid())
        with self.assertRaises(og.OmniGraphError):
            og.GraphController.create_prim(
                prim_path="/World/PrimPlusBadTypes",
                attribute_values={
                    "someFloat": ("not_a_type", 3.0),
                },
            )
        self.assertTrue(graph_controller.create_prim("/FromObjPrim").IsValid())

        # create_variable
        valid_var = og.GraphController.create_variable(graph, "valid_var", "int")
        self.assertTrue(bool(valid_var))
        with ogt.ExpectedError():
            with self.assertRaises(og.OmniGraphError):
                og.GraphController.create_variable(graph, "next_var", "not_a_valid_type")
        self.assertTrue(og.GraphController.create_variable(graph, "valid_og_var", og.Type(og.BaseDataType.FLOAT)))
        self.assertTrue(
            og.GraphController.create_variable(graph, "valid_no_undo", og.Type(og.BaseDataType.FLOAT), undoable=False)
        )
        og.GraphController.set_variable_default_value(valid_var, 2)
        self.assertEqual(2, og.GraphController.get_variable_default_value(valid_var))
        self.assertTrue(graph_controller.create_variable(graph, "another_var", "float"))

        # connect / disconnect api
        other_node = og.GraphController.create_node(node.get_prim_path() + "_2", _MOCK_NODE_TYPE)
        input_attr = node.get_attribute("inputs:input")
        output_attr = other_node.get_attribute("outputs:output")
        with self.assertRaises(og.OmniGraphError):
            og.GraphController.connect(src_spec="/Invalid.output_attr", dst_spec="/Invalid.input_attr")
        og.GraphController.connect(src_spec=output_attr, dst_spec=input_attr)
        self.assertEqual(output_attr.get_downstream_connection_count(), 1)
        self.assertEqual(input_attr.get_upstream_connection_count(), 1)
        og.GraphController.disconnect(src_spec=output_attr, dst_spec=input_attr)
        self.assertEqual(output_attr.get_downstream_connection_count(), 0)
        self.assertEqual(input_attr.get_upstream_connection_count(), 0)

        graph_controller.connect(src_spec=output_attr, dst_spec=("inputs:input", node), undoable=False)
        self.assertEqual(output_attr.get_downstream_connection_count(), 1)
        self.assertEqual(input_attr.get_upstream_connection_count(), 1)

        graph_controller.disconnect_all(output_attr, undoable=False)
        self.assertEqual(output_attr.get_downstream_connection_count(), 0)
        self.assertEqual(input_attr.get_upstream_connection_count(), 0)

        og.GraphController.connect(src_spec=output_attr, dst_spec=input_attr)
        og.GraphController.disconnect_all(input_attr)
        self.assertEqual(output_attr.get_downstream_connection_count(), 0)
        self.assertEqual(input_attr.get_upstream_connection_count(), 0)

    # -------------------------------------------------------------------------
    async def test_controller_api(self):
        """Tests for the og.Controller api"""
        (graph, _) = self._create_graph_and_node()
        no_undo_controller = og.Controller(undoable=False)

        # invalid graphs for manual eval
        prerender = no_undo_controller.create_graph(
            {"graph_path": "/World/PreRender", "pipeline_stage": og.GraphPipelineStage.GRAPH_PIPELINE_STAGE_PRERENDER}
        )
        postrender = no_undo_controller.create_graph(
            {"graph_path": "/World/PostRender", "pipeline_stage": og.GraphPipelineStage.GRAPH_PIPELINE_STAGE_POSTRENDER}
        )

        # evaluate - check for error cases
        # invalid graph
        with self.assertRaises(og.OmniGraphError):
            await og.Controller.evaluate(graph_id="/InvalidGraphId")
        with self.assertRaises(og.OmniGraphError):
            await og.Controller.evaluate(prerender)
        with self.assertRaises(og.OmniGraphError):
            await no_undo_controller.evaluate(postrender)

        # evaluate_sync
        with self.assertRaises(og.OmniGraphError):
            og.Controller.evaluate_sync(graph_id="/InvalidGraphId")
        with self.assertRaises(og.OmniGraphError):
            og.Controller.evaluate_sync(prerender)
        with self.assertRaises(og.OmniGraphError):
            no_undo_controller.evaluate_sync(postrender)

        # edit errors and edge cases
        with self.assertRaises(og.OmniGraphError):
            og.Controller.edit(graph, {"InvalidKey": []})
        # empty edit is valid
        og.Controller.edit(graph, None)

        (new_graph, (node1, node2), _, _) = no_undo_controller.edit(
            "/World/NewGraph",
            {
                og.Controller.Keys.CREATE_NODES: [("Node1", _MOCK_NODE_TYPE), ("Node2", _MOCK_NODE_TYPE)],
                og.Controller.Keys.CREATE_PRIMS: [
                    ("/World/Cube1", "Cube"),
                    ("/World/Cube2", {"someFloat": ("float", 3.0)}, "Cube"),
                ],
            },
        )
        self.assertTrue(new_graph.is_valid())
        no_undo_controller.edit(new_graph, {og.Controller.Keys.DELETE_NODES: ["Node1"]})
        self.assertFalse(node1.is_valid())
        with self.assertRaises(og.OmniGraphError):
            og.Controller.edit(
                graph, {og.Controller.Keys.SET_VALUES: (("inputs:input", "Node1", "too", "many"), "args")}
            )
        with self.assertRaises(og.OmniGraphError):
            og.Controller.edit(graph, {og.Controller.Keys.SET_VALUES: ("Node1.too_many_._separators", "args")})
        no_undo_controller.edit(  # validate create attributes
            new_graph,
            {
                og.Controller.Keys.CREATE_ATTRIBUTES: [
                    ("Node2.inputs:new_any", "any"),
                    ("Node2.inputs:new_union", ["float", "double"]),
                    ("Node2.outputs:new_output", og.Type(og.BaseDataType.FLOAT, 3)),
                ]
            },
        )
        self.assertTrue(og.Controller.attribute(("inputs:new_any", node2)).is_valid())
        self.assertTrue(og.Controller.attribute(("inputs:new_union", node2)).is_valid())
        self.assertTrue(og.Controller.attribute(("outputs:new_output", node2)).is_valid())

    # -------------------------------------------------------------------------
    async def test_object_lookup_api(self):
        """Tests for the object lookup api"""

        (graph, node) = self._create_graph_and_node()
        graph_path = graph.get_path_to_graph()
        # .graph method
        self.assertEqual(None, og.ObjectLookup.graph(None))
        self.assertEqual(None, og.ObjectLookup.graph("/InvalidGraphPath"))
        self.assertEqual(graph, og.ObjectLookup.graph(graph))
        self.assertEqual(graph, og.ObjectLookup.graph(graph_path))
        self.assertEqual(graph, og.ObjectLookup.graph(Sdf.Path(graph_path)))
        self.assertEqual(graph, og.ObjectLookup.graph(og.ObjectLookup.prim(graph_path)))
        self.assertEqual([graph, graph], og.ObjectLookup.graph([graph, graph_path]))

        # .node method
        node_path = node.get_prim_path()
        node_name = Sdf.Path(node_path).name
        with self.assertRaises(og.OmniGraphError):
            og.ObjectLookup.node(None)
        with self.assertRaises(og.OmniGraphError):
            og.ObjectLookup.node("/InvalidNodePath")
        self.assertEqual(node, og.ObjectLookup.node(node))
        self.assertEqual(node, og.ObjectLookup.node(node_path))
        self.assertEqual(node, og.ObjectLookup.node(Sdf.Path(node_path)))
        self.assertEqual(node, og.ObjectLookup.node(og.ObjectLookup.prim(node_path)))
        self.assertEqual([node, node], og.ObjectLookup.node([node, node_path]))

        # .node_path method
        with self.assertRaises(og.OmniGraphError):
            og.ObjectLookup.node_path(None)
        self.assertEqual(node_path, og.ObjectLookup.node_path(node))
        self.assertEqual(node_path, og.ObjectLookup.node_path(node_path))
        self.assertEqual(node_path, og.ObjectLookup.node_path(Sdf.Path(node_path)))
        self.assertEqual(node_path, og.ObjectLookup.node_path(og.ObjectLookup.prim(node)))
        self.assertEqual(node_path, og.ObjectLookup.node_path((node_name, graph.get_path_to_graph())))
        self.assertEqual(node_path, og.ObjectLookup.node_path((node_name, Sdf.Path(graph.get_path_to_graph()))))
        self.assertEqual(node_path, og.ObjectLookup.node_path((node_name, graph)))

        # prim_path method
        with self.assertRaises(og.OmniGraphError):
            og.ObjectLookup.prim_path(None)
        with self.assertRaises(og.OmniGraphError):
            og.ObjectLookup.prim_path(Usd.Prim())
        with self.assertRaises(og.OmniGraphError):
            og.ObjectLookup.prim_path(node.get_compound_graph_instance())
        self.assertEqual(node_path, og.ObjectLookup.prim_path(node_path))
        self.assertEqual(node_path, og.ObjectLookup.prim_path(node))
        self.assertEqual(graph_path, og.ObjectLookup.prim_path(graph_path))
        self.assertEqual(graph_path, og.ObjectLookup.prim_path(graph))
        self.assertEqual([node_path, graph_path], og.ObjectLookup.prim_path([node, graph]))

        # attribute
        attr = node.get_attribute("inputs:fixed_type")
        attr_path = attr.get_path()
        attr_prop = og.ObjectLookup.usd_property(attr_path)
        with self.assertRaises(og.OmniGraphError):
            og.ObjectLookup.attribute((attr_path, node_path, graph_path))
        self.assertEqual(attr, og.ObjectLookup.attribute(attr))
        self.assertEqual(attr, og.ObjectLookup.attribute(attr_path))
        self.assertEqual(attr, og.ObjectLookup.attribute(Sdf.Path(attr_path)))
        self.assertEqual(attr, og.ObjectLookup.attribute(attr_prop))
        self.assertEqual([attr, attr, attr], og.ObjectLookup.attribute([attr, attr_path, attr_prop]))

        # attribute path
        with self.assertRaises(og.OmniGraphError):
            og.ObjectLookup.attribute_path(None)
        self.assertEqual(attr_path, og.ObjectLookup.attribute_path(attr))
        self.assertEqual(attr_path, og.ObjectLookup.attribute_path(attr_path))
        self.assertEqual(attr_path, og.ObjectLookup.attribute_path(Sdf.Path(attr_path)))
        self.assertEqual(attr_path, og.ObjectLookup.attribute_path(attr_prop))

        # attribute_type
        attr_type = attr.get_resolved_type()
        with self.assertRaises(og.OmniGraphError):
            og.ObjectLookup.attribute_type(None)
        self.assertEqual(attr_type, og.ObjectLookup.attribute_type(attr))
        self.assertEqual(attr_type, og.ObjectLookup.attribute_type(attr_type))

        # node_type
        node_type = node.get_node_type()
        node_type_str = node_type.get_node_type()
        with self.assertRaises(og.OmniGraphError):
            og.ObjectLookup.node_type("not.a.node.type")
        self.assertEqual(node_type, og.ObjectLookup.node_type(node_type))
        self.assertEqual(node_type, og.ObjectLookup.node_type(node_type_str))
        self.assertEqual(node_type, og.ObjectLookup.node_type(node))
        self.assertEqual([node_type, node_type], og.ObjectLookup.node_type([node_type, node]))

        # prim
        graph_prim = og.ObjectLookup.prim(graph_path)
        node_prim = og.ObjectLookup.prim(node_path)
        self.assertEqual(graph_prim.GetPath(), Sdf.Path(graph_path))
        self.assertEqual(node_prim.GetPath(), Sdf.Path(node_path))
        with self.assertRaises(og.OmniGraphError):
            og.ObjectLookup.prim(None)
        self.assertEqual(graph_prim, og.ObjectLookup.prim(graph))
        self.assertEqual(node_prim, og.ObjectLookup.prim(node))
        self.assertEqual(graph_prim, og.ObjectLookup.prim(graph_prim))
        self.assertEqual(graph_prim, og.ObjectLookup.prim(Sdf.Path(graph_path)))
        self.assertEqual(node_prim, og.ObjectLookup.prim((node_name, graph_path)))
        self.assertEqual([graph_prim, node_prim], og.ObjectLookup.prim([graph_path, node_path]))

        # usd_attribute
        with self.assertRaises(og.OmniGraphError):
            og.ObjectLookup.usd_attribute("Not a valid usd attribute")
        self.assertEqual(attr_prop, og.ObjectLookup.usd_attribute(attr))
        self.assertEqual([attr_prop, attr_prop], og.ObjectLookup.usd_attribute([attr, attr_path]))

        # usd_property
        with self.assertRaises(og.OmniGraphError):
            og.ObjectLookup.usd_property("Not a valid usd attribute")
        self.assertEqual(attr_prop, og.ObjectLookup.usd_property(attr))
        self.assertEqual([attr_prop, attr_prop], og.ObjectLookup.usd_property([attr, attr_path]))

        # usd_relationship
        rel_attr = node.get_attribute("inputs:target")
        rel_path = rel_attr.get_path()
        rel = og.ObjectLookup.usd_relationship(rel_path)
        self.assertEqual(rel.GetPath(), Sdf.Path(rel_path))
        with self.assertRaises(og.OmniGraphError):
            og.ObjectLookup.usd_relationship("Invalid relationship")
        self.assertEqual(rel, og.ObjectLookup.usd_relationship(Sdf.Path(rel_path)))
        self.assertEqual(rel, og.ObjectLookup.usd_relationship(rel))
        self.assertEqual(rel, og.ObjectLookup.usd_relationship(rel_attr))
        self.assertEqual([rel, rel], og.ObjectLookup.usd_relationship([rel_path, rel_attr]))

    # -------------------------------------------------------------------------
    def _create_graph_and_node_with_compound(self, graph_name="/World/CompoundTestGraph"):

        (graph, (node, compound_node), _, _) = og.Controller.edit(
            graph_name,
            {
                og.Controller.Keys.CREATE_NODES: [
                    ("Node1", _MOCK_NODE_TYPE),
                    ("CompoundNode1", {og.Controller.Keys.CREATE_NODES: [("NodeL2", _MOCK_NODE_TYPE)]}),
                ]
            },
        )
        return (graph, node, compound_node)

    # -------------------------------------------------------------------------
    async def test_object_lookup_api_for_compounds(self):
        """Tests for the og.ObjectLookup API compound node related commands"""
        (graph, node, compound_node) = self._create_graph_and_node_with_compound()

        # grab the graph and nested node
        sub_graph = compound_node.get_compound_graph_instance()
        sub_node = sub_graph.get_nodes()[0]
        self.assertTrue(sub_graph.is_valid())
        self.assertTrue(sub_node.is_valid())

        # og.ObjectLookup.compound_graph
        self.assertEqual(og.ObjectLookup.compound_graph(compound_node), sub_graph)
        self.assertEqual(og.ObjectLookup.compound_graph(compound_node.get_prim_path()), sub_graph)
        self.assertEqual(og.ObjectLookup.compound_graph(Sdf.Path(compound_node.get_prim_path())), sub_graph)
        self.assertIsNone(og.ObjectLookup.compound_graph(node))
        self.assertIsNone(og.ObjectLookup.compound_graph(node.get_prim_path()))
        self.assertIsNone(og.ObjectLookup.compound_graph(Sdf.Path(node.get_prim_path())))
        with self.assertRaises(og.OmniGraphError):
            og.ObjectLookup.compound_graph("not a node")
        with self.assertRaises(og.OmniGraphError):
            og.ObjectLookup.compound_graph([compound_node, "invalid node"])
        self.assertEqual(
            og.ObjectLookup.compound_graph([compound_node, compound_node.get_prim_path(), node, node.get_prim_path()]),
            [sub_graph, sub_graph, None, None],
        )
        self.assertEqual(og.ObjectLookup.compound_graph([]), [])

        # og.ObjectLookup.compound_node
        self.assertEqual(og.ObjectLookup.compound_node(graph), None)
        self.assertEqual(og.ObjectLookup.compound_node(graph.get_path_to_graph()), None)
        self.assertEqual(og.ObjectLookup.compound_node(node), None)
        self.assertEqual(og.ObjectLookup.compound_node(node.get_prim_path()), None)
        self.assertEqual(og.ObjectLookup.compound_node(compound_node), None)
        self.assertEqual(og.ObjectLookup.compound_node(sub_graph), compound_node)
        self.assertEqual(og.ObjectLookup.compound_node(sub_graph.get_path_to_graph()), compound_node)
        self.assertEqual(og.ObjectLookup.compound_node(Sdf.Path(sub_graph.get_path_to_graph())), compound_node)
        self.assertEqual(og.ObjectLookup.compound_node(sub_node), compound_node)
        self.assertEqual(og.ObjectLookup.compound_node(sub_node.get_prim_path()), compound_node)
        self.assertEqual(og.ObjectLookup.compound_node(Sdf.Path(sub_node.get_prim_path())), compound_node)
        with self.assertRaises(og.OmniGraphError):
            og.ObjectLookup.compound_node(None)
        with self.assertRaises(og.OmniGraphError):
            og.ObjectLookup.compound_node("Invalid node")
        self.assertEqual(og.ObjectLookup.compound_node([]), [])
        self.assertEqual(
            og.ObjectLookup.compound_node(
                [graph, node, compound_node.get_prim_path(), sub_graph, sub_graph.get_path_to_graph(), sub_node]
            ),
            [None, None, None, compound_node, compound_node, compound_node],
        )
