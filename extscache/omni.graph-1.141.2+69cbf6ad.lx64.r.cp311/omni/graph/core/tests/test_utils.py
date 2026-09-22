"""Unit tests for random omni.graph utilities"""

import omni.graph.core as og
import omni.graph.core.tests as ogt
import omni.graph.tools.ogn as ogn
import omni.usd
from pxr import Gf, Sdf

from .._impl.helpers import graph_iterator

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
            node_type.set_metadata(ogn.MetadataKeys.EXTENSION, "omni.graph")
            node_type.set_metadata(ogn.MetadataKeys.DESCRIPTION, "A description")
            node_type.set_metadata(ogn.MetadataKeys.LANGUAGE, "Python")
            node_type.set_metadata(ogn.MetadataKeys.UI_NAME, "Test Node")
            node_type.set_metadata(ogn.MetadataKeys.TAGS, "tag")

            node_type.set_metadata(ogn.MetadataKeys.ICON_BACKGROUND_COLOR, "[0, 0, 0, 0]")
            node_type.set_metadata(ogn.MetadataKeys.ICON_BORDER_COLOR, "[1, 0, 1, 0]")
            node_type.set_metadata(ogn.MetadataKeys.ICON_COLOR, "[0, 0, 0, 1]")
            node_type.set_metadata(ogn.MetadataKeys.ICON_PATH, "/a_path")

            node_type.set_metadata("Custom metadata", "custom")

            node_type.add_extended_input("inputs:input", "", True, og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_ANY)
            node_type.add_extended_input(
                "inputs:extended", "int,float", True, og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_UNION
            )
            node_type.add_input("inputs:input_float", "float", True)
            node_type.add_input("inputs:input_rel", "target", True)
            node_type.add_extended_output("outputs:output", "", True, og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_ANY)
            node_type.add_state("state:state", "int", 0)

            scheduling_hints = node_type.get_scheduling_hints()
            scheduling_hints.set_data_access(og.eAccessLocation.E_GLOBAL, og.eAccessType.E_WRITE)
            scheduling_hints.set_data_access(og.eAccessLocation.E_STATIC, og.eAccessType.E_NONE)
            scheduling_hints.set_data_access(og.eAccessLocation.E_TOPOLOGY, og.eAccessType.E_READ_WRITE)
            scheduling_hints.set_data_access(og.eAccessLocation.E_USD, og.eAccessType.E_READ)
            scheduling_hints.compute_rule = og.eComputeRule.E_DEFAULT

            node_type.set_scheduling_hints(scheduling_hints)

        @staticmethod
        def get_node_type() -> str:
            return _MOCK_NODE_TYPE

    og.register_node_type(OgnSimpleNode, 1)


# -------------------------------------------------------------------------
def _deregister_node_type():
    """Deregister the preloaded node type"""
    og.deregister_node_type(_MOCK_NODE_TYPE)


# -------------------------------------------------------------------------
class TestUtils(ogt.OmniGraphTestCase):
    """Tests for helper utility methdos inside omni.graph"""

    # ---------------------------------------------------------------------
    async def test_generate_ogn_from_node(self):
        """Test the generate ogn from node utility function"""
        try:
            _register_node_type()

            (graph, (node,), _, _) = og.Controller(update_usd=True).edit(
                "/World/TestGraph",
                {
                    og.Controller.Keys.CREATE_NODES: [("Node", _MOCK_NODE_TYPE)],
                },
            )
            await og.Controller.evaluate(graph)

            ogn_dict = og.generate_ogn_from_node(node)[_MOCK_NODE_TYPE]
            icon_dict = ogn_dict[ogn.NodeTypeKeys.ICON]
            meta_dict = ogn_dict[ogn.NodeTypeKeys.METADATA]

            self.assertEqual(ogn_dict[ogn.NodeTypeKeys.DESCRIPTION], ["A description"])
            self.assertEqual(ogn_dict[ogn.NodeTypeKeys.LANGUAGE], "Python")
            self.assertEqual(ogn_dict[ogn.NodeTypeKeys.UI_NAME], "Test Node")
            self.assertEqual(set(ogn_dict[ogn.NodeTypeKeys.SCHEDULING]), {"global-write", "topology", "usd-read"})

            self.assertEqual(icon_dict[ogn.IconKeys.BACKGROUND_COLOR], "[0, 0, 0, 0]")
            self.assertEqual(icon_dict[ogn.IconKeys.BORDER_COLOR], "[1, 0, 1, 0]")
            self.assertEqual(icon_dict[ogn.IconKeys.COLOR], "[0, 0, 0, 1]")
            self.assertEqual(icon_dict[ogn.IconKeys.PATH], "a_path")

            self.assertEqual(meta_dict["Custom metadata"], "custom")

            self.assertIn("inputs", ogn_dict)
            self.assertIn("outputs", ogn_dict)
            self.assertIn("state", ogn_dict)

            inputs_dict = ogn_dict["inputs"]
            any_input = inputs_dict["input"]
            ext_input = inputs_dict["extended"]
            type_input = inputs_dict["input_float"]

            self.assertEqual(any_input["type"], "any")
            self.assertEqual(ext_input["type"], ["int", "float"])
            self.assertEqual(type_input["type"], "float")

        finally:
            _deregister_node_type()

    # ---------------------------------------------------------------------
    async def test_load_example_file(self):
        """Test for og.load_example_file"""
        with ogt.ExpectedError():  # warning for the noop node type
            (result, _) = await og.load_example_file("ExampleCube.usda")
        self.assertTrue(result)
        cube = omni.usd.get_context().get_stage().GetPrimAtPath("/World/Cube")
        self.assertTrue(cube.IsValid())

    # ---------------------------------------------------------------------
    async def test_attribute_value_as_usd(self):
        """Tests for og.attribute_valud_as_usd"""

        # scalar
        self.assertEqual(og.attribute_value_as_usd(og.Type(og.BaseDataType.INT), 1), 1)
        self.assertEqual(og.attribute_value_as_usd(og.Type(og.BaseDataType.FLOAT), 1), 1.0)
        self.assertEqual(og.attribute_value_as_usd(og.Type(og.BaseDataType.DOUBLE), 1), 1.0)
        self.assertEqual(og.attribute_value_as_usd(og.Type(og.BaseDataType.BOOL), True), True)
        self.assertEqual(og.attribute_value_as_usd(og.Type(og.BaseDataType.HALF), 1), 1.0)
        self.assertEqual(og.attribute_value_as_usd(og.Type(og.BaseDataType.INT64), 1), 1)
        self.assertEqual(og.attribute_value_as_usd(og.Type(og.BaseDataType.TOKEN), "One"), "One")
        self.assertEqual(og.attribute_value_as_usd(og.Type(og.BaseDataType.UCHAR), "a"), "a")
        self.assertEqual(og.attribute_value_as_usd(og.Type(og.BaseDataType.UINT64), 1), 1)

        # array
        self.assertEqual(og.attribute_value_as_usd(og.Type(og.BaseDataType.INT, 1), [1, 1]), [1, 1])
        self.assertEqual(og.attribute_value_as_usd(og.Type(og.BaseDataType.FLOAT, 1), [1.0, 1.0]), [1.0, 1.0])
        self.assertEqual(og.attribute_value_as_usd(og.Type(og.BaseDataType.DOUBLE, 1), [1.0, 1.0]), [1.0, 1.0])
        self.assertEqual(og.attribute_value_as_usd(og.Type(og.BaseDataType.BOOL, 1), True), True)
        self.assertEqual(og.attribute_value_as_usd(og.Type(og.BaseDataType.HALF, 1), [1.0, 1.0]), [1.0, 1.0])
        self.assertEqual(og.attribute_value_as_usd(og.Type(og.BaseDataType.INT64, 1), [1, 1]), [1, 1])
        self.assertEqual(og.attribute_value_as_usd(og.Type(og.BaseDataType.TOKEN, 1), ["One", "Two"]), ["One", "Two"])
        self.assertEqual(og.attribute_value_as_usd(og.Type(og.BaseDataType.UINT64, 1), [1, 1]), [1, 1])
        self.assertEqual(
            og.attribute_value_as_usd(og.Type(og.BaseDataType.UINT64, 1, 0, og.AttributeRole.TEXT), "Text"), "Text"
        )

        # tuples
        self.assertEqual(
            og.attribute_value_as_usd(og.Type(og.BaseDataType.DOUBLE, 1, 0, og.AttributeRole.TIMECODE), 1),
            Sdf.TimeCode(1),
        )
        self.assertEqual(
            og.attribute_value_as_usd(og.Type(og.BaseDataType.DOUBLE, 3, 0, og.AttributeRole.COLOR), [1, 0, 1]),
            Gf.Vec3d(1, 0, 1),
        )
        self.assertEqual(
            og.attribute_value_as_usd(og.Type(og.BaseDataType.FLOAT, 3, 0, og.AttributeRole.COLOR), [1, 0, 1]),
            Gf.Vec3f(1, 0, 1),
        )
        self.assertEqual(
            og.attribute_value_as_usd(og.Type(og.BaseDataType.HALF, 3, 0, og.AttributeRole.COLOR), [1, 0, 1]),
            Gf.Vec3h(1, 0, 1),
        )
        self.assertEqual(
            og.attribute_value_as_usd(
                og.Type(og.BaseDataType.DOUBLE, 4, 0, og.AttributeRole.MATRIX), [[1.0, 0.0], [1.0, 0.0]]
            ),
            Gf.Matrix2d(1, 0, 1, 0),
        )
        self.assertEqual(
            og.attribute_value_as_usd(
                og.Type(og.BaseDataType.DOUBLE, 9, 0, og.AttributeRole.MATRIX),
                [[1.0, 0.0, 1.0], [1.0, 0.0, 1.0], [1.0, 0.0, 1.0]],
            ),
            Gf.Matrix3d(1, 0, 1, 1, 0, 1, 1, 0, 1),
        )
        self.assertEqual(
            og.attribute_value_as_usd(
                og.Type(og.BaseDataType.DOUBLE, 16, 0, og.AttributeRole.MATRIX),
                [[1.0, 0.0, 1.0, 0.0], [1.0, 0.0, 1.0, 0.0], [1.0, 0.0, 1.0, 0.0], [1.0, 0.0, 1.0, 0.0]],
            ),
            Gf.Matrix4d(1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0),
        )
        self.assertEqual(
            og.attribute_value_as_usd(og.Type(og.BaseDataType.DOUBLE, 3, 0, og.AttributeRole.NORMAL), [1, 0, 0]),
            Gf.Vec3d(1, 0, 0),
        )
        self.assertEqual(
            og.attribute_value_as_usd(og.Type(og.BaseDataType.FLOAT, 3, 0, og.AttributeRole.NORMAL), [1, 0, 0]),
            Gf.Vec3f(1, 0, 0),
        )
        self.assertEqual(
            og.attribute_value_as_usd(og.Type(og.BaseDataType.HALF, 3, 0, og.AttributeRole.NORMAL), [1, 0, 0]),
            Gf.Vec3h(1, 0, 0),
        )
        self.assertEqual(
            og.attribute_value_as_usd(og.Type(og.BaseDataType.DOUBLE, 3, 0, og.AttributeRole.POSITION), [1, 0, 0]),
            Gf.Vec3d(1, 0, 0),
        )
        self.assertEqual(
            og.attribute_value_as_usd(og.Type(og.BaseDataType.FLOAT, 3, 0, og.AttributeRole.POSITION), [1, 0, 0]),
            Gf.Vec3f(1, 0, 0),
        )
        self.assertEqual(
            og.attribute_value_as_usd(og.Type(og.BaseDataType.HALF, 3, 0, og.AttributeRole.POSITION), [1, 0, 0]),
            Gf.Vec3h(1, 0, 0),
        )
        self.assertEqual(
            og.attribute_value_as_usd(og.Type(og.BaseDataType.DOUBLE, 3, 0, og.AttributeRole.QUATERNION), [1, 0, 0, 0]),
            Gf.Quatd(0, 1, 0, 0),
        )
        self.assertEqual(
            og.attribute_value_as_usd(og.Type(og.BaseDataType.FLOAT, 3, 0, og.AttributeRole.QUATERNION), [1, 0, 0, 0]),
            Gf.Quatf(0, 1, 0, 0),
        )
        self.assertEqual(
            og.attribute_value_as_usd(og.Type(og.BaseDataType.HALF, 3, 0, og.AttributeRole.QUATERNION), [1, 0, 0, 0]),
            Gf.Quath(0, 1, 0, 0),
        )
        self.assertEqual(
            og.attribute_value_as_usd(og.Type(og.BaseDataType.DOUBLE, 3, 0, og.AttributeRole.TEXCOORD), [1, 0, 0]),
            Gf.Vec3d(1, 0, 0),
        )
        self.assertEqual(
            og.attribute_value_as_usd(og.Type(og.BaseDataType.FLOAT, 3, 0, og.AttributeRole.TEXCOORD), [1, 0, 0]),
            Gf.Vec3f(1, 0, 0),
        )
        self.assertEqual(
            og.attribute_value_as_usd(og.Type(og.BaseDataType.HALF, 3, 0, og.AttributeRole.TEXCOORD), [1, 0, 0]),
            Gf.Vec3h(1, 0, 0),
        )
        self.assertEqual(
            og.attribute_value_as_usd(og.Type(og.BaseDataType.DOUBLE, 3, 0, og.AttributeRole.VECTOR), [1, 0, 0]),
            Gf.Vec3d(1, 0, 0),
        )
        self.assertEqual(
            og.attribute_value_as_usd(og.Type(og.BaseDataType.FLOAT, 3, 0, og.AttributeRole.VECTOR), [1, 0, 0]),
            Gf.Vec3f(1, 0, 0),
        )
        self.assertEqual(
            og.attribute_value_as_usd(og.Type(og.BaseDataType.HALF, 3, 0, og.AttributeRole.VECTOR), [1, 0, 0]),
            Gf.Vec3h(1, 0, 0),
        )

        # array tuples
        self.assertEqual(
            og.attribute_value_as_usd(og.Type(og.BaseDataType.DOUBLE, 1, 1, og.AttributeRole.TIMECODE), [1]),
            [Sdf.TimeCode(1)],
        )
        self.assertEqual(
            og.attribute_value_as_usd(og.Type(og.BaseDataType.DOUBLE, 3, 1, og.AttributeRole.COLOR), [[1, 0, 1]]),
            [Gf.Vec3d(1, 0, 1)],
        )
        self.assertEqual(
            og.attribute_value_as_usd(og.Type(og.BaseDataType.FLOAT, 3, 1, og.AttributeRole.COLOR), [[1, 0, 1]]),
            [Gf.Vec3f(1, 0, 1)],
        )
        self.assertEqual(
            og.attribute_value_as_usd(og.Type(og.BaseDataType.HALF, 3, 1, og.AttributeRole.COLOR), [[1, 0, 1]]),
            [Gf.Vec3h(1, 0, 1)],
        )
        self.assertEqual(
            og.attribute_value_as_usd(
                og.Type(og.BaseDataType.DOUBLE, 4, 1, og.AttributeRole.MATRIX), [[[1.0, 0.0], [1.0, 0.0]]]
            ),
            [Gf.Matrix2d(1, 0, 1, 0)],
        )
        self.assertEqual(
            og.attribute_value_as_usd(
                og.Type(og.BaseDataType.DOUBLE, 9, 1, og.AttributeRole.MATRIX),
                [[[1.0, 0.0, 1.0], [1.0, 0.0, 1.0], [1.0, 0.0, 1.0]]],
            ),
            [Gf.Matrix3d(1, 0, 1, 1, 0, 1, 1, 0, 1)],
        )
        self.assertEqual(
            og.attribute_value_as_usd(
                og.Type(og.BaseDataType.DOUBLE, 16, 1, og.AttributeRole.MATRIX),
                [[[1.0, 0.0, 1.0, 0.0], [1.0, 0.0, 1.0, 0.0], [1.0, 0.0, 1.0, 0.0], [1.0, 0.0, 1.0, 0.0]]],
            ),
            [Gf.Matrix4d(1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0)],
        )
        self.assertEqual(
            og.attribute_value_as_usd(og.Type(og.BaseDataType.DOUBLE, 3, 1, og.AttributeRole.NORMAL), [[1, 0, 0]]),
            [Gf.Vec3d(1, 0, 0)],
        )
        self.assertEqual(
            og.attribute_value_as_usd(og.Type(og.BaseDataType.FLOAT, 3, 1, og.AttributeRole.NORMAL), [[1, 0, 0]]),
            [Gf.Vec3f(1, 0, 0)],
        )
        self.assertEqual(
            og.attribute_value_as_usd(og.Type(og.BaseDataType.HALF, 3, 1, og.AttributeRole.NORMAL), [[1, 0, 0]]),
            [Gf.Vec3h(1, 0, 0)],
        )
        self.assertEqual(
            og.attribute_value_as_usd(og.Type(og.BaseDataType.DOUBLE, 3, 1, og.AttributeRole.POSITION), [[1, 0, 0]]),
            [Gf.Vec3d(1, 0, 0)],
        )
        self.assertEqual(
            og.attribute_value_as_usd(og.Type(og.BaseDataType.FLOAT, 3, 1, og.AttributeRole.POSITION), [[1, 0, 0]]),
            [Gf.Vec3f(1, 0, 0)],
        )
        self.assertEqual(
            og.attribute_value_as_usd(og.Type(og.BaseDataType.HALF, 3, 1, og.AttributeRole.POSITION), [[1, 0, 0]]),
            [Gf.Vec3h(1, 0, 0)],
        )
        self.assertEqual(
            og.attribute_value_as_usd(
                og.Type(og.BaseDataType.DOUBLE, 3, 1, og.AttributeRole.QUATERNION), [[1, 0, 0, 0]]
            ),
            [Gf.Quatd(0, 1, 0, 0)],
        )
        self.assertEqual(
            og.attribute_value_as_usd(
                og.Type(og.BaseDataType.FLOAT, 3, 1, og.AttributeRole.QUATERNION), [[1, 0, 0, 0]]
            ),
            [Gf.Quatf(0, 1, 0, 0)],
        )
        self.assertEqual(
            og.attribute_value_as_usd(og.Type(og.BaseDataType.HALF, 3, 1, og.AttributeRole.QUATERNION), [[1, 0, 0, 0]]),
            [Gf.Quath(0, 1, 0, 0)],
        )
        self.assertEqual(
            og.attribute_value_as_usd(og.Type(og.BaseDataType.DOUBLE, 3, 1, og.AttributeRole.TEXCOORD), [[1, 0, 0]]),
            [Gf.Vec3d(1, 0, 0)],
        )
        self.assertEqual(
            og.attribute_value_as_usd(og.Type(og.BaseDataType.FLOAT, 3, 1, og.AttributeRole.TEXCOORD), [[1, 0, 0]]),
            [Gf.Vec3f(1, 0, 0)],
        )
        self.assertEqual(
            og.attribute_value_as_usd(og.Type(og.BaseDataType.HALF, 3, 1, og.AttributeRole.TEXCOORD), [[1, 0, 0]]),
            [Gf.Vec3h(1, 0, 0)],
        )
        self.assertEqual(
            og.attribute_value_as_usd(og.Type(og.BaseDataType.DOUBLE, 3, 1, og.AttributeRole.VECTOR), [[1, 0, 0]]),
            [Gf.Vec3d(1, 0, 0)],
        )
        self.assertEqual(
            og.attribute_value_as_usd(og.Type(og.BaseDataType.FLOAT, 3, 1, og.AttributeRole.VECTOR), [[1, 0, 0]]),
            [Gf.Vec3f(1, 0, 0)],
        )
        self.assertEqual(
            og.attribute_value_as_usd(og.Type(og.BaseDataType.HALF, 3, 1, og.AttributeRole.VECTOR), [[1, 0, 0]]),
            [Gf.Vec3h(1, 0, 0)],
        )

    # ---------------------------------------------------------------------
    async def test_python_value_as_usd(self):
        """Test the python value as usd method"""

        # scalar
        self.assertEqual(og.python_value_as_usd(og.Type(og.BaseDataType.INT), 1), 1)
        self.assertEqual(og.python_value_as_usd(og.Type(og.BaseDataType.FLOAT), 1), 1.0)
        self.assertEqual(og.python_value_as_usd(og.Type(og.BaseDataType.DOUBLE), 1), 1.0)
        self.assertEqual(og.python_value_as_usd(og.Type(og.BaseDataType.BOOL), True), True)
        self.assertEqual(og.python_value_as_usd(og.Type(og.BaseDataType.HALF), 1), 1.0)
        self.assertEqual(og.python_value_as_usd(og.Type(og.BaseDataType.INT64), 1), 1)
        self.assertEqual(og.python_value_as_usd(og.Type(og.BaseDataType.TOKEN), "One"), "One")
        self.assertEqual(og.python_value_as_usd(og.Type(og.BaseDataType.UCHAR), "a"), "a")
        self.assertEqual(og.python_value_as_usd(og.Type(og.BaseDataType.UINT64), 1), 1)

        # array
        self.assertEqual(og.python_value_as_usd(og.Type(og.BaseDataType.INT, 1), [1, 1]), [1, 1])
        self.assertEqual(og.python_value_as_usd(og.Type(og.BaseDataType.FLOAT, 1), [1.0, 1.0]), [1.0, 1.0])
        self.assertEqual(og.python_value_as_usd(og.Type(og.BaseDataType.DOUBLE, 1), [1.0, 1.0]), [1.0, 1.0])
        self.assertEqual(og.python_value_as_usd(og.Type(og.BaseDataType.BOOL, 1), True), True)
        self.assertEqual(og.python_value_as_usd(og.Type(og.BaseDataType.HALF, 1), [1.0, 1.0]), [1.0, 1.0])
        self.assertEqual(og.python_value_as_usd(og.Type(og.BaseDataType.INT64, 1), [1, 1]), [1, 1])
        self.assertEqual(og.python_value_as_usd(og.Type(og.BaseDataType.TOKEN, 1), ["One", "Two"]), ["One", "Two"])
        self.assertEqual(og.python_value_as_usd(og.Type(og.BaseDataType.UINT64, 1), [1, 1]), [1, 1])
        self.assertEqual(
            og.python_value_as_usd(og.Type(og.BaseDataType.UINT64, 1, 0, og.AttributeRole.TEXT), "Text"), "Text"
        )

        # tuples
        self.assertEqual(
            og.python_value_as_usd(og.Type(og.BaseDataType.DOUBLE, 1, 0, og.AttributeRole.TIMECODE), 1), Sdf.TimeCode(1)
        )
        self.assertEqual(
            og.python_value_as_usd(og.Type(og.BaseDataType.DOUBLE, 3, 0, og.AttributeRole.COLOR), [1, 0, 1]),
            Gf.Vec3d(1, 0, 1),
        )
        self.assertEqual(
            og.python_value_as_usd(og.Type(og.BaseDataType.FLOAT, 3, 0, og.AttributeRole.COLOR), [1, 0, 1]),
            Gf.Vec3f(1, 0, 1),
        )
        self.assertEqual(
            og.python_value_as_usd(og.Type(og.BaseDataType.HALF, 3, 0, og.AttributeRole.COLOR), [1, 0, 1]),
            Gf.Vec3h(1, 0, 1),
        )
        self.assertEqual(
            og.python_value_as_usd(
                og.Type(og.BaseDataType.DOUBLE, 4, 0, og.AttributeRole.MATRIX), [[1.0, 0.0], [1.0, 0.0]]
            ),
            Gf.Matrix2d(1, 0, 1, 0),
        )
        self.assertEqual(
            og.python_value_as_usd(
                og.Type(og.BaseDataType.DOUBLE, 9, 0, og.AttributeRole.MATRIX),
                [[1.0, 0.0, 1.0], [1.0, 0.0, 1.0], [1.0, 0.0, 1.0]],
            ),
            Gf.Matrix3d(1, 0, 1, 1, 0, 1, 1, 0, 1),
        )
        self.assertEqual(
            og.python_value_as_usd(
                og.Type(og.BaseDataType.DOUBLE, 16, 0, og.AttributeRole.MATRIX),
                [[1.0, 0.0, 1.0, 0.0], [1.0, 0.0, 1.0, 0.0], [1.0, 0.0, 1.0, 0.0], [1.0, 0.0, 1.0, 0.0]],
            ),
            Gf.Matrix4d(1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0),
        )
        self.assertEqual(
            og.python_value_as_usd(og.Type(og.BaseDataType.DOUBLE, 3, 0, og.AttributeRole.NORMAL), [1, 0, 0]),
            Gf.Vec3d(1, 0, 0),
        )
        self.assertEqual(
            og.python_value_as_usd(og.Type(og.BaseDataType.FLOAT, 3, 0, og.AttributeRole.NORMAL), [1, 0, 0]),
            Gf.Vec3f(1, 0, 0),
        )
        self.assertEqual(
            og.python_value_as_usd(og.Type(og.BaseDataType.HALF, 3, 0, og.AttributeRole.NORMAL), [1, 0, 0]),
            Gf.Vec3h(1, 0, 0),
        )
        self.assertEqual(
            og.python_value_as_usd(og.Type(og.BaseDataType.DOUBLE, 3, 0, og.AttributeRole.POSITION), [1, 0, 0]),
            Gf.Vec3d(1, 0, 0),
        )
        self.assertEqual(
            og.python_value_as_usd(og.Type(og.BaseDataType.FLOAT, 3, 0, og.AttributeRole.POSITION), [1, 0, 0]),
            Gf.Vec3f(1, 0, 0),
        )
        self.assertEqual(
            og.python_value_as_usd(og.Type(og.BaseDataType.HALF, 3, 0, og.AttributeRole.POSITION), [1, 0, 0]),
            Gf.Vec3h(1, 0, 0),
        )
        self.assertEqual(
            og.python_value_as_usd(og.Type(og.BaseDataType.DOUBLE, 3, 0, og.AttributeRole.QUATERNION), [1, 0, 0, 0]),
            Gf.Quatd(0, 1, 0, 0),
        )
        self.assertEqual(
            og.python_value_as_usd(og.Type(og.BaseDataType.FLOAT, 3, 0, og.AttributeRole.QUATERNION), [1, 0, 0, 0]),
            Gf.Quatf(0, 1, 0, 0),
        )
        self.assertEqual(
            og.python_value_as_usd(og.Type(og.BaseDataType.HALF, 3, 0, og.AttributeRole.QUATERNION), [1, 0, 0, 0]),
            Gf.Quath(0, 1, 0, 0),
        )
        self.assertEqual(
            og.python_value_as_usd(og.Type(og.BaseDataType.DOUBLE, 3, 0, og.AttributeRole.TEXCOORD), [1, 0, 0]),
            Gf.Vec3d(1, 0, 0),
        )
        self.assertEqual(
            og.python_value_as_usd(og.Type(og.BaseDataType.FLOAT, 3, 0, og.AttributeRole.TEXCOORD), [1, 0, 0]),
            Gf.Vec3f(1, 0, 0),
        )
        self.assertEqual(
            og.python_value_as_usd(og.Type(og.BaseDataType.HALF, 3, 0, og.AttributeRole.TEXCOORD), [1, 0, 0]),
            Gf.Vec3h(1, 0, 0),
        )
        self.assertEqual(
            og.python_value_as_usd(og.Type(og.BaseDataType.DOUBLE, 3, 0, og.AttributeRole.VECTOR), [1, 0, 0]),
            Gf.Vec3d(1, 0, 0),
        )
        self.assertEqual(
            og.python_value_as_usd(og.Type(og.BaseDataType.FLOAT, 3, 0, og.AttributeRole.VECTOR), [1, 0, 0]),
            Gf.Vec3f(1, 0, 0),
        )
        self.assertEqual(
            og.python_value_as_usd(og.Type(og.BaseDataType.HALF, 3, 0, og.AttributeRole.VECTOR), [1, 0, 0]),
            Gf.Vec3h(1, 0, 0),
        )

        # array tuples
        self.assertEqual(
            og.python_value_as_usd(og.Type(og.BaseDataType.DOUBLE, 1, 1, og.AttributeRole.TIMECODE), [1]),
            [Sdf.TimeCode(1)],
        )
        self.assertEqual(
            og.python_value_as_usd(og.Type(og.BaseDataType.DOUBLE, 3, 1, og.AttributeRole.COLOR), [[1, 0, 1]]),
            [Gf.Vec3d(1, 0, 1)],
        )
        self.assertEqual(
            og.python_value_as_usd(og.Type(og.BaseDataType.FLOAT, 3, 1, og.AttributeRole.COLOR), [[1, 0, 1]]),
            [Gf.Vec3f(1, 0, 1)],
        )
        self.assertEqual(
            og.python_value_as_usd(og.Type(og.BaseDataType.HALF, 3, 1, og.AttributeRole.COLOR), [[1, 0, 1]]),
            [Gf.Vec3h(1, 0, 1)],
        )
        self.assertEqual(
            og.python_value_as_usd(
                og.Type(og.BaseDataType.DOUBLE, 4, 1, og.AttributeRole.MATRIX), [[[1.0, 0.0], [1.0, 0.0]]]
            ),
            [Gf.Matrix2d(1, 0, 1, 0)],
        )
        self.assertEqual(
            og.python_value_as_usd(
                og.Type(og.BaseDataType.DOUBLE, 9, 1, og.AttributeRole.MATRIX),
                [[[1.0, 0.0, 1.0], [1.0, 0.0, 1.0], [1.0, 0.0, 1.0]]],
            ),
            [Gf.Matrix3d(1, 0, 1, 1, 0, 1, 1, 0, 1)],
        )
        self.assertEqual(
            og.python_value_as_usd(
                og.Type(og.BaseDataType.DOUBLE, 16, 1, og.AttributeRole.MATRIX),
                [[[1.0, 0.0, 1.0, 0.0], [1.0, 0.0, 1.0, 0.0], [1.0, 0.0, 1.0, 0.0], [1.0, 0.0, 1.0, 0.0]]],
            ),
            [Gf.Matrix4d(1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0)],
        )
        self.assertEqual(
            og.python_value_as_usd(og.Type(og.BaseDataType.DOUBLE, 3, 1, og.AttributeRole.NORMAL), [[1, 0, 0]]),
            [Gf.Vec3d(1, 0, 0)],
        )
        self.assertEqual(
            og.python_value_as_usd(og.Type(og.BaseDataType.FLOAT, 3, 1, og.AttributeRole.NORMAL), [[1, 0, 0]]),
            [Gf.Vec3f(1, 0, 0)],
        )
        self.assertEqual(
            og.python_value_as_usd(og.Type(og.BaseDataType.HALF, 3, 1, og.AttributeRole.NORMAL), [[1, 0, 0]]),
            [Gf.Vec3h(1, 0, 0)],
        )
        self.assertEqual(
            og.python_value_as_usd(og.Type(og.BaseDataType.DOUBLE, 3, 1, og.AttributeRole.POSITION), [[1, 0, 0]]),
            [Gf.Vec3d(1, 0, 0)],
        )
        self.assertEqual(
            og.python_value_as_usd(og.Type(og.BaseDataType.FLOAT, 3, 1, og.AttributeRole.POSITION), [[1, 0, 0]]),
            [Gf.Vec3f(1, 0, 0)],
        )
        self.assertEqual(
            og.python_value_as_usd(og.Type(og.BaseDataType.HALF, 3, 1, og.AttributeRole.POSITION), [[1, 0, 0]]),
            [Gf.Vec3h(1, 0, 0)],
        )
        self.assertEqual(
            og.python_value_as_usd(og.Type(og.BaseDataType.DOUBLE, 3, 1, og.AttributeRole.QUATERNION), [[1, 0, 0, 0]]),
            [Gf.Quatd(0, 1, 0, 0)],
        )
        self.assertEqual(
            og.python_value_as_usd(og.Type(og.BaseDataType.FLOAT, 3, 1, og.AttributeRole.QUATERNION), [[1, 0, 0, 0]]),
            [Gf.Quatf(0, 1, 0, 0)],
        )
        self.assertEqual(
            og.python_value_as_usd(og.Type(og.BaseDataType.HALF, 3, 1, og.AttributeRole.QUATERNION), [[1, 0, 0, 0]]),
            [Gf.Quath(0, 1, 0, 0)],
        )
        self.assertEqual(
            og.python_value_as_usd(og.Type(og.BaseDataType.DOUBLE, 3, 1, og.AttributeRole.TEXCOORD), [[1, 0, 0]]),
            [Gf.Vec3d(1, 0, 0)],
        )
        self.assertEqual(
            og.python_value_as_usd(og.Type(og.BaseDataType.FLOAT, 3, 1, og.AttributeRole.TEXCOORD), [[1, 0, 0]]),
            [Gf.Vec3f(1, 0, 0)],
        )
        self.assertEqual(
            og.python_value_as_usd(og.Type(og.BaseDataType.HALF, 3, 1, og.AttributeRole.TEXCOORD), [[1, 0, 0]]),
            [Gf.Vec3h(1, 0, 0)],
        )
        self.assertEqual(
            og.python_value_as_usd(og.Type(og.BaseDataType.DOUBLE, 3, 1, og.AttributeRole.VECTOR), [[1, 0, 0]]),
            [Gf.Vec3d(1, 0, 0)],
        )
        self.assertEqual(
            og.python_value_as_usd(og.Type(og.BaseDataType.FLOAT, 3, 1, og.AttributeRole.VECTOR), [[1, 0, 0]]),
            [Gf.Vec3f(1, 0, 0)],
        )
        self.assertEqual(
            og.python_value_as_usd(og.Type(og.BaseDataType.HALF, 3, 1, og.AttributeRole.VECTOR), [[1, 0, 0]]),
            [Gf.Vec3h(1, 0, 0)],
        )

    # ---------------------------------------------------------------------
    async def test_data_shape_from_type(self):
        """Tests for og.test_data_shape_from_type"""
        types = [
            # scalar
            og.Type(og.BaseDataType.INT),
            og.Type(og.BaseDataType.FLOAT),
            og.Type(og.BaseDataType.DOUBLE),
            og.Type(og.BaseDataType.BOOL),
            og.Type(og.BaseDataType.HALF),
            og.Type(og.BaseDataType.INT64),
            og.Type(og.BaseDataType.TOKEN),
            og.Type(og.BaseDataType.UCHAR),
            og.Type(og.BaseDataType.UINT64),
            # array
            og.Type(og.BaseDataType.INT, 1),
            og.Type(og.BaseDataType.FLOAT, 1),
            og.Type(og.BaseDataType.DOUBLE, 1),
            og.Type(og.BaseDataType.BOOL, 1),
            og.Type(og.BaseDataType.HALF, 1),
            og.Type(og.BaseDataType.INT64, 1),
            og.Type(og.BaseDataType.TOKEN, 1),
            og.Type(og.BaseDataType.UINT64, 1),
            # tuples
            og.Type(og.BaseDataType.DOUBLE, 1, 0, og.AttributeRole.TIMECODE),
            og.Type(og.BaseDataType.DOUBLE, 3, 0, og.AttributeRole.COLOR),
            og.Type(og.BaseDataType.FLOAT, 3, 0, og.AttributeRole.COLOR),
            og.Type(og.BaseDataType.HALF, 3, 0, og.AttributeRole.COLOR),
            og.Type(og.BaseDataType.DOUBLE, 4, 0, og.AttributeRole.MATRIX),
            og.Type(og.BaseDataType.DOUBLE, 9, 0, og.AttributeRole.MATRIX),
            og.Type(og.BaseDataType.DOUBLE, 16, 0, og.AttributeRole.MATRIX),
            og.Type(og.BaseDataType.DOUBLE, 3, 0, og.AttributeRole.NORMAL),
            og.Type(og.BaseDataType.FLOAT, 3, 0, og.AttributeRole.NORMAL),
            og.Type(og.BaseDataType.HALF, 3, 0, og.AttributeRole.NORMAL),
            og.Type(og.BaseDataType.DOUBLE, 3, 0, og.AttributeRole.POSITION),
            og.Type(og.BaseDataType.FLOAT, 3, 0, og.AttributeRole.POSITION),
            og.Type(og.BaseDataType.HALF, 3, 0, og.AttributeRole.POSITION),
            og.Type(og.BaseDataType.DOUBLE, 3, 0, og.AttributeRole.QUATERNION),
            og.Type(og.BaseDataType.FLOAT, 3, 0, og.AttributeRole.QUATERNION),
            og.Type(og.BaseDataType.HALF, 3, 0, og.AttributeRole.QUATERNION),
            og.Type(og.BaseDataType.DOUBLE, 3, 0, og.AttributeRole.TEXCOORD),
            og.Type(og.BaseDataType.FLOAT, 3, 0, og.AttributeRole.TEXCOORD),
            og.Type(og.BaseDataType.HALF, 3, 0, og.AttributeRole.TEXCOORD),
            og.Type(og.BaseDataType.DOUBLE, 3, 0, og.AttributeRole.VECTOR),
            og.Type(og.BaseDataType.FLOAT, 3, 0, og.AttributeRole.VECTOR),
            og.Type(og.BaseDataType.HALF, 3, 0, og.AttributeRole.VECTOR),
            # array tuples
            og.Type(og.BaseDataType.DOUBLE, 1, 1, og.AttributeRole.TIMECODE),
            og.Type(og.BaseDataType.DOUBLE, 3, 1, og.AttributeRole.COLOR),
            og.Type(og.BaseDataType.FLOAT, 3, 1, og.AttributeRole.COLOR),
            og.Type(og.BaseDataType.HALF, 3, 1, og.AttributeRole.COLOR),
            og.Type(og.BaseDataType.DOUBLE, 4, 1, og.AttributeRole.MATRIX),
            og.Type(og.BaseDataType.DOUBLE, 9, 1, og.AttributeRole.MATRIX),
            og.Type(og.BaseDataType.DOUBLE, 16, 1, og.AttributeRole.MATRIX),
            og.Type(og.BaseDataType.DOUBLE, 3, 1, og.AttributeRole.NORMAL),
            og.Type(og.BaseDataType.FLOAT, 3, 1, og.AttributeRole.NORMAL),
            og.Type(og.BaseDataType.HALF, 3, 1, og.AttributeRole.NORMAL),
            og.Type(og.BaseDataType.DOUBLE, 3, 1, og.AttributeRole.POSITION),
            og.Type(og.BaseDataType.FLOAT, 3, 1, og.AttributeRole.POSITION),
            og.Type(og.BaseDataType.HALF, 3, 1, og.AttributeRole.POSITION),
            og.Type(og.BaseDataType.DOUBLE, 3, 1, og.AttributeRole.QUATERNION),
            og.Type(og.BaseDataType.FLOAT, 3, 1, og.AttributeRole.QUATERNION),
            og.Type(og.BaseDataType.HALF, 3, 1, og.AttributeRole.QUATERNION),
            og.Type(og.BaseDataType.DOUBLE, 3, 1, og.AttributeRole.TEXCOORD),
            og.Type(og.BaseDataType.FLOAT, 3, 1, og.AttributeRole.TEXCOORD),
            og.Type(og.BaseDataType.HALF, 3, 1, og.AttributeRole.TEXCOORD),
            og.Type(og.BaseDataType.DOUBLE, 3, 1, og.AttributeRole.VECTOR),
            og.Type(og.BaseDataType.FLOAT, 3, 1, og.AttributeRole.VECTOR),
            og.Type(og.BaseDataType.HALF, 3, 1, og.AttributeRole.VECTOR),
        ]

        for t in types:
            (d_type, d_shape) = og.data_shape_from_type(t)
            self.assertEqual(t.base_type, d_type.base_type)
            self.assertEqual(t.tuple_count, d_type.tuple_count)
            self.assertEqual(t.role == og.AttributeRole.MATRIX, d_type.is_matrix_type())

            # validate the return values work in the data wrapper class
            data_wrapper = og.DataWrapper(0, d_type, d_shape, og.Device("cpu"), og.PtrToPtrKind.CPU)
            self.assertEqual(data_wrapper.is_array(), t.array_depth > 0)
            self.assertTrue(str(data_wrapper).startswith("CPU"))

    # ---------------------------------------------------------------------
    async def test_graph_iterator(self):
        """Tests the graph iterator helper utility"""
        try:
            _register_node_type()

            (graph, (_, compound), _, _) = og.Controller(update_usd=True).edit(
                "/World/TestGraph",
                {
                    og.Controller.Keys.CREATE_NODES: [
                        ("Node", _MOCK_NODE_TYPE),
                        ("Compound", {og.Controller.Keys.CREATE_NODES: [("SubNode", _MOCK_NODE_TYPE)]}),
                    ],
                },
            )

            graphs = list(graph_iterator())
            self.assertIn(graph, graphs)
            self.assertIn(compound.get_compound_graph_instance(), graphs)

        finally:
            _deregister_node_type()

    # ---------------------------------------------------------------------
    async def test_graph_settings(self):
        """Tests the graph settings utility"""
        try:
            _register_node_type()
            (graph, _, _, _) = og.Controller(update_usd=True).edit(
                "/World/TestGraph",
                {
                    og.Controller.Keys.CREATE_NODES: [("Node", _MOCK_NODE_TYPE)],
                },
            )

            settings = og.get_graph_settings(graph)
            self.assertEqual(settings.evaluator_type, "push")
            self.assertEqual(settings.fabric_backing, "StageWithoutHistory")
            self.assertEqual(settings.pipeline_stage, "pipelineStageSimulation")
            self.assertEqual(settings.evaluation_mode, "Automatic")

        finally:
            _deregister_node_type()

    # ---------------------------------------------------------------------
    async def test_remove_attribute_if(self):
        """Test the remove_attribute_if method"""
        try:
            _register_node_type()
            (_, (node,), _, _) = og.Controller(update_usd=True).edit(
                "/World/TestGraph",
                {
                    og.Controller.Keys.CREATE_NODES: [("Node", _MOCK_NODE_TYPE)],
                },
            )

            def filter_func(attr: og.Attribute) -> bool:
                return attr.get_resolved_type() == og.Type(og.BaseDataType.FLOAT)

            count = len(node.get_attributes())
            self.assertTrue(node.get_attribute_exists("inputs:input_float"))
            self.assertGreater(og.remove_attributes_if(node, filter_func), 0)
            self.assertGreater(count, len(node.get_attributes()))
            self.assertFalse(node.get_attribute_exists("inputs:input_float"))

        finally:
            _deregister_node_type()

    # ---------------------------------------------------------------------
    async def test_is_attribute_plain_data(self):
        """Test the is_attribute_plain_data method"""
        try:
            _register_node_type()
            (_, (node,), _, _) = og.Controller(update_usd=True).edit(
                "/World/TestGraph",
                {
                    og.Controller.Keys.CREATE_NODES: [("Node", _MOCK_NODE_TYPE)],
                },
            )

            self.assertTrue(og.is_attribute_plain_data(node.get_attribute("inputs:input_float")))
            self.assertFalse(og.is_attribute_plain_data(node.get_attribute("inputs:input")))  # any
            self.assertFalse(og.is_attribute_plain_data(node.get_attribute("inputs:input_rel")))  # relationship
            self.assertFalse(og.is_attribute_plain_data(node.get_attribute("node:type")))  # special

        finally:
            _deregister_node_type()

    # ---------------------------------------------------------------------
    async def test_get_current_file_format_version_property(self):
        """Simple test that validates the og.Graph.CURRENT_FILE_FORMAT_VERSION constant"""

        version = og.Graph.CURRENT_FILE_FORMAT_VERSION
        # make sure the version is equal or greater than 1,9
        self.assertTrue(version >= og.FileFormatVersion(1, 9))

    # ---------------------------------------------------------------------
    async def test_file_format_version_object(self):
        """Unit tests for og.FileFormatVersion"""

        # test the > operator
        self.assertTrue(og.FileFormatVersion(1, 0) > og.FileFormatVersion(0, 0))
        self.assertTrue(og.FileFormatVersion(1, 1) > og.FileFormatVersion(1, 0))
        self.assertFalse(og.FileFormatVersion(1, 0) > og.FileFormatVersion(2, 0))
        self.assertFalse(og.FileFormatVersion(1, 0) > og.FileFormatVersion(1, 0))
        self.assertFalse(og.FileFormatVersion(1, 0) > og.FileFormatVersion(1, 1))

        # test the >= operator
        self.assertTrue(og.FileFormatVersion(1, 0) >= og.FileFormatVersion(0, 0))
        self.assertTrue(og.FileFormatVersion(1, 1) >= og.FileFormatVersion(1, 0))
        self.assertTrue(og.FileFormatVersion(1, 0) >= og.FileFormatVersion(1, 0))
        self.assertFalse(og.FileFormatVersion(1, 0) >= og.FileFormatVersion(2, 0))
        self.assertFalse(og.FileFormatVersion(1, 0) >= og.FileFormatVersion(1, 1))

        # test the == operator
        self.assertTrue(og.FileFormatVersion(1, 0) == og.FileFormatVersion(1, 0))
        self.assertFalse(og.FileFormatVersion(1, 1) == og.FileFormatVersion(1, 0))
        self.assertFalse(og.FileFormatVersion(1, 0) == og.FileFormatVersion(0, 0))

        # test the != operator
        self.assertTrue(og.FileFormatVersion(1, 0) != og.FileFormatVersion(0, 0))
        self.assertTrue(og.FileFormatVersion(1, 1) != og.FileFormatVersion(1, 0))
        self.assertFalse(og.FileFormatVersion(1, 0) != og.FileFormatVersion(1, 0))

        # test the <= operator
        self.assertTrue(og.FileFormatVersion(1, 0) <= og.FileFormatVersion(1, 0))
        self.assertTrue(og.FileFormatVersion(1, 0) <= og.FileFormatVersion(2, 0))
        self.assertTrue(og.FileFormatVersion(1, 0) <= og.FileFormatVersion(1, 1))
        self.assertFalse(og.FileFormatVersion(1, 1) <= og.FileFormatVersion(1, 0))
        self.assertFalse(og.FileFormatVersion(2, 0) <= og.FileFormatVersion(1, 0))

        # test the < operator
        self.assertTrue(og.FileFormatVersion(1, 0) < og.FileFormatVersion(2, 0))
        self.assertTrue(og.FileFormatVersion(1, 0) < og.FileFormatVersion(1, 1))
        self.assertFalse(og.FileFormatVersion(1, 1) < og.FileFormatVersion(1, 0))
        self.assertFalse(og.FileFormatVersion(2, 0) < og.FileFormatVersion(1, 0))
        self.assertFalse(og.FileFormatVersion(1, 0) < og.FileFormatVersion(1, 0))
