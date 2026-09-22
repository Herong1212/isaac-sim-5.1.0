"""
Contains support for testing the ../generate_node.py script for processing different data types.
Basic testing is in TestNodeGenerator.py.

The framework is set up so that the tests can be run synchronously through main.py, or
asynchronously through the Kit testing framework.
"""

import io
import json
from contextlib import suppress

import omni.graph.tools.ogn as ogn
import omni.kit.test
from omni.graph.tools._impl.node_generator.attributes.AttributeManager import CudaConfiguration
from omni.graph.tools._impl.node_generator.attributes.DoubleAttributeManager import DoubleAttributeManager
from omni.graph.tools._impl.node_generator.attributes.FloatAttributeManager import FloatAttributeManager
from omni.graph.tools._impl.node_generator.attributes.IntAttributeManager import IntAttributeManager
from omni.graph.tools._impl.node_generator.attributes.MatrixAttributeManager import MatrixAttributeManager
from omni.graph.tools._impl.node_generator.attributes.TokenAttributeManager import TokenAttributeManager
from omni.graph.tools._impl.node_generator.utils import IndentedOutput


class TestNodeGeneratorDataTypes(omni.kit.test.AsyncTestCase):
    """Unit test class for this script"""

    attr_index = 0

    # --------------------------------------------------------------------------------------------------------------
    def create_attribute(self, attribute_type: str, attribute_default):
        """
        Create an attribute JSON structure and text with a generic description
        :param attribute_type: Attribute type
        :param attribute_default: Default value of the attribute
        :return: (Attribute Name, Attribute Info as JSON, Attribute as string) output for the attribute definition.
        Both versions are returned as the string attribute omits the enclosing curly braces so that
        attribute definitions can more easily be embedded in the JSON attribute lists
        """
        attribute_name = f"attr{TestNodeGeneratorDataTypes.attr_index}"
        TestNodeGeneratorDataTypes.attr_index += 1
        attribute_as_json = {
            f"{ogn.AttributeKeys.DESCRIPTION}": f"This is attribute {attribute_name}",
            f"{ogn.AttributeKeys.TYPE}": attribute_type,
            f"{ogn.AttributeKeys.DEFAULT}": attribute_default,
        }
        attribute_as_string = f'"{attribute_name}" : {json.dumps(attribute_as_json)}'
        return attribute_name, attribute_as_json, attribute_as_string

    # --------------------------------------------------------------------------------------------------------------
    def validate_node(self, node_wrapper: ogn.NodeInterfaceWrapper, node_name: str):
        """
        Confirms that a named node exists and is a valid node in the interface wrapper.
        :param node_wrapper: ogn.NodeInterfaceWrapper class generated from the node description
        :param node_name: Name of the node to check
        :return: ogn.NodeInterface object for the named node
        """
        self.assertEqual(node_wrapper.node_interface.name, node_name, f"Expected node {node_name} not listed")
        return node_wrapper.node_interface

    # --------------------------------------------------------------------------------------------------------------
    def validate_node_description(self, node_interface: ogn.NodeInterface, expected_description: str):
        """
        Validate that the node interface has parsed a description with the expected name
        :param node_interface: ogn.NodeInterface class of the node being checked
        :param expected_description: Description string the node is expected to have
        """
        self.assertEqual(
            node_interface.description, expected_description, f"Description for node {node_interface.name} not correct"
        )

    # --------------------------------------------------------------------------------------------------------------
    async def test_min_max(self):
        """Test for successful handling of attributes with minimum/maximum values"""
        # Test configurations consist of (attribute type, min value, max value, default value, should succeed?)
        min_max_configurations = [
            ["bool", "true", "false", "true", False],
            ["double", 0.0, 5.0, 3.0, True],
            ["double", 0.0, 5.0, 6.0, False],
            ["float", 0.0, 5.0, 3.0, True],
            ["float", 0.0, 5.0, 6.0, False],
            ["half", 10.0, 1.0, 5.0, False],
            ["half", 1.0, 10.0, 5.0, True],
            ["int", 1, 10, 5, True],
            ["int", 10, 1, 5, False],
            ["int64", 10, 1, 5, False],
            ["int64", 1, 10, 5, True],
            ["uchar", 1, 10, 5, True],
            ["uchar", 10, 1, 5, False],
            ["uint", 1, 10, 5, True],
            ["uint", 10, 1, 5, False],
            ["uint64", 10, 1, 5, False],
            ["uint64", 1, 10, 5, True],
            ["double", '"inf"', None, 5, False],
            ["double", '"inf"', '"inf"', 5, False],
            ["double", '"inf"', '"-inf"', 5, False],
            ["double", '"inf"', '"nan"', 5, False],
            ["double", '"-inf"', '"inf"', 5, True],
            ["double", '"-inf"', '"-inf"', 5, False],
            ["double", '"-inf"', '"nan"', 5, False],
            ["double", '"-inf"', None, 5, True],
            ["double", '"nan"', None, 5, False],
            ["double", '"nan"', '"inf"', 5, False],
            ["double", '"nan"', '"-inf"', 5, False],
            ["double", '"nan"', '"nan"', 5, False],
            ["double", None, None, 5, True],
            ["double", None, '"inf"', 5, True],
            ["double", None, '"-inf"', 5, False],
            ["double", None, '"nan"', 5, False],
            ["double", '"inf"', '"inf"', '"inf"', True],
            ["double", '"-inf"', '"-inf"', '"-inf"', True],
            ["double", '"nan"', '"nan"', '"nan"', True],
            ["double[2]", '["inf", "inf"]', '["inf", "inf"]', '["inf", "inf"]', True],
            ["double[2]", '["-inf", "-inf"]', '["inf", "inf"]', [5, 6], True],
            ["double[2]", '["-inf", "-inf"]', None, [100, 200], True],
            ["double[2]", '["-inf", "-inf"]', ["inf", 6], [10, 10], False],
        ]
        for attribute_type, min_value, max_value, default_value, should_succeed in min_max_configurations:
            min_text = f'"minimum": {min_value},' if min_value is not None else ""
            max_text = f'"maximum": {max_value},' if max_value is not None else ""
            min_max_description = f"""{{
                "MinMaxNode" : {{
                    "{ogn.NodeTypeKeys.DESCRIPTION}" : "This node has attributes with min/max values",
                    "{ogn.NodeTypeKeys.INPUTS}" : {{
                        "a" : {{
                            "description": "This is an a",
                            "type": "{attribute_type}",
                            {min_text}{max_text}
                            "default": {default_value}
                        }}
                    }}
                }}
            }}"""
            if should_succeed:
                min_max_node = ogn.NodeInterfaceWrapper(min_max_description, "test")
                _ = self.validate_node(min_max_node, "test.MinMaxNode")
            else:
                with self.assertRaises(ogn.ParseError, msg=f"Parsing node with min/max values {min_max_description}"):
                    ogn.NodeInterfaceWrapper(min_max_description, "test")

        # Repeat the same tests, reinterpreting the type and values as arrays
        for attribute_type, min_value, max_value, default_value, should_succeed in min_max_configurations:
            min_text = f'"minimum": {min_value},' if min_value is not None else ""
            max_text = f'"maximum": {max_value},' if max_value is not None else ""
            min_max_description = f"""{{
                "MinMaxNode" : {{
                    "{ogn.NodeTypeKeys.DESCRIPTION}" : "This node has attributes with min/max values",
                    "{ogn.NodeTypeKeys.INPUTS}" : {{
                        "a" : {{
                            "description": "This is an a",
                            "type": "{attribute_type}[]",
                            {min_text}{max_text}
                            "default": [{default_value}]
                        }}
                    }}
                }}
            }}"""
            if should_succeed:
                min_max_node = ogn.NodeInterfaceWrapper(min_max_description, "test")
                _ = self.validate_node(min_max_node, "test.MinMaxNode")
            else:
                with self.assertRaises(ogn.ParseError, msg=f"Parsing node with min/max values {min_max_description}"):
                    ogn.NodeInterfaceWrapper(min_max_description, "test")

    # --------------------------------------------------------------------------------------------------------------
    async def test_defaults(self):
        """Test for setting defaults on various types of attributes"""
        # ----------------------------------------
        # Values are [Attribute Type, Default for normal value, Python version of the default]
        defaults = [["bool", "true", True], ["double", 1.4, 1.4], ["float", 1.5, 1.5], ["int", 1, 1]]
        input_name = "input1"
        for attribute_type, default, python_default in defaults:
            array_spec = ["", ', "array": true']  # Test with and without array enabled
            array_info = ["", "array of "]
            array_defaults = [default, [default]]
            array_python_defaults = [python_default, [python_default]]
            for array_type in range(0, 1):
                node_info = f"a legal input default of type {array_info[array_type]}{attribute_type}"
                node_with_defaults_description = f"""{{
                    "NodeWithDefaults" : {{
                        "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is a node with {node_info}",
                        "{ogn.NodeTypeKeys.INPUTS}" : {{
                            "{input_name}": {{
                                "{ogn.AttributeKeys.DESCRIPTION}": "This is the defaulted input",
                                "{ogn.AttributeKeys.TYPE}": "{attribute_type}",
                                "{ogn.AttributeKeys.DEFAULT}": {array_defaults[array_type]}{array_spec[array_type]}
                            }}
                        }}
                    }}
                }}"""
                defaulted_node = ogn.NodeInterfaceWrapper(node_with_defaults_description, "test")
                node_interface = self.validate_node(defaulted_node, "test.NodeWithDefaults")
                (input_attribute, _) = node_interface.attribute_by_name(input_name)
                self.assertEqual(input_attribute.default, array_python_defaults[array_type])

        # ----------------------------------------
        # Values are [Attribute Type, Illegal default for normal value, Illegal default for array value]
        illegal_defaults = [
            ["bool", ["true"], "true"],
            ["double", [1.4], 1.4],
            ["float", [1.5], 1.5],
            ["int", [1], 1],
            ["bool", 1, [1]],
            ["double", "true", ["true"]],
            ["float", '"hello"', ['"world"']],
            ["int", 1.6, [1.6]],
            ["half", 65505.0, [-65505.0]],
            ["int", 3000000000, [-3000000000]],
            ["int64", 10000000000000000000000, [-10000000000000000000000]],
            ["uchar", 257, [-1]],
            ["uint", 3000000000, [-1]],
            ["uint64", 10000000000000000000000, [-1]],
            ["string", 2, [1.2]],
            ["token", 2, [1.2]],
        ]
        for attribute_type, illegal_default, illegal_array_default in illegal_defaults:
            array_spec = ["", '"array": true']  # Test with and without array enabled
            array_info = ["", "array of "]
            array_defaults = [illegal_default, illegal_array_default]
            for array_type in range(0, 1):
                node_info = f"an illegal input default of type {array_info[array_type]}{attribute_type}"
                illegal_default_type_node = f"""{{
                    "IllegalInputType" : {{
                        "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is a node with {node_info}",
                        "{ogn.NodeTypeKeys.INPUTS}" : {{
                            "input1": {{
                                {ogn.AttributeKeys.DESCRIPTION}: "This is the bad input",
                                "{ogn.AttributeKeys.TYPE}": "{attribute_type}",
                                "{ogn.AttributeKeys.DEFAULT}": {array_defaults[array_type]},
                                {array_spec[array_type]}
                            }}
                        }}
                    }}
                }}"""
                with self.assertRaises(ogn.ParseError, msg=f"Parsing interface with {node_info}"):
                    ogn.NodeInterfaceWrapper(illegal_default_type_node, "test")

    # --------------------------------------------------------------------------------------------------------------
    async def test_nan_inf(self):
        """Test for successful handling of attributes with sNan/NaN/Inf/-Inf values"""
        # All of the numeric types that support NaN and Inf values
        allow_nan_inf = [
            "double",
            "double[2]",
            "double[3]",
            "double[4]",
            "double[]",
            "double[2][]",
            "double[3][]",
            "double[4][]",
            "float",
            "float[2]",
            "float[3]",
            "float[4]",
            "float[]",
            "float[2][]",
            "float[3][]",
            "float[4][]",
            "half",
            "half[2]",
            "half[3]",
            "half[4]",
            "half[]",
            "half[2][]",
            "half[3][]",
            "half[4][]",
            "matrixd[2]",
            "matrixd[2][]",
            "matrixd[3]",
            "matrixd[3][]",
            "matrixd[4]",
            "matrixd[4][]",
            "frame[4]",
            "frame[4][]",
            "colord[3]",
            "colord[3][]",
            "colord[4]",
            "colord[4][]",
            "colorf[3]",
            "colorf[3][]",
            "colorf[4]",
            "colorf[4][]",
            "colorh[3]",
            "colorh[3][]",
            "colorh[4]",
            "colorh[4][]",
            "normald[3]",
            "normalf[3]",
            "normalh[3]",
            "normald[3][]",
            "normalf[3][]",
            "normalh[3][]",
            "pointd[3]",
            "pointf[3]",
            "pointh[3]",
            "pointd[3][]",
            "pointf[3][]",
            "pointh[3][]",
            "quatd[4]",
            "quatf[4]",
            "quath[4]",
            "quatd[4][]",
            "quatf[4][]",
            "quath[4][]",
            "texcoordd[2]",
            "texcoordd[3]",
            "texcoordf[2]",
            "texcoordf[3]",
            "texcoordh[2]",
            "texcoordh[3]",
            "texcoordd[2][]",
            "texcoordd[3][]",
            "texcoordf[2][]",
            "texcoordf[3][]",
            "texcoordh[2][]",
            "texcoordh[3][]",
            "timecode",
            "timecode[]",
            "transform[4]",
            "transform[4][]",
            "vectord[3]",
            "vectorf[3]",
            "vectorh[3]",
            "vectord[3][]",
            "vectorf[3][]",
            "vectorh[3][]",
            # These are not numeric types but they do allow the NAN/INF strings since they are string types
            "path",
            "string",
            "token",
            "token[]",
        ]
        # Create nodes with each of the allowed attribute types, ensuring that only those listed above that accept
        # NaN/Inf values correctly parse and the others fail. The variations of the legal names have exactly 4 values
        # so that we know they will be exercised when the 4-tuples are tested. Matrix values are just square arrays of
        # the vectors:  ["INF", "INF"] = double[2], [["INF", "INF"], ["INF", "INF"]] = matrixd[2]
        legal_pos_inf = ['"INF"', '"Inf"', '"inf"', '"+Inf"']
        legal_neg_inf = ['"INF"', '"Inf"', '"inf"', '"-Inf"']
        legal_nan = ['"NAN"', '"NaN"', '"nan"', '"naN"']
        legal_snan = ['"SNAN"', '"sNaN"', '"snan"', '"SnaN"']
        for base_type_name, attribute_manager_type in ogn.ALL_ATTRIBUTE_TYPES.items():
            # These types cannot be instantiated with defaults
            if base_type_name in ["any", "union", "target", "bundle"]:
                continue
            for tuple_count in attribute_manager_type.tuples_supported():
                for array_depth in attribute_manager_type.array_depths_supported():
                    pos_inf_value = ", ".join(legal_pos_inf[i] for i in range(tuple_count))
                    neg_inf_value = ", ".join(legal_neg_inf[i] for i in range(tuple_count))
                    nan_value = ", ".join(legal_nan[i] for i in range(tuple_count))
                    snan_value = ", ".join(legal_snan[i] for i in range(tuple_count))
                    attribute_type_name = base_type_name
                    if tuple_count > 1:
                        attribute_type_name += f"[{tuple_count}]"
                        pos_inf_value = f"[{pos_inf_value}]"
                        neg_inf_value = f"[{neg_inf_value}]"
                        nan_value = f"[{nan_value}]"
                        snan_value = f"[{snan_value}]"
                    if attribute_manager_type.is_matrix_type():
                        pos_inf_value = "[" + ", ".join(f"{pos_inf_value}" for i in range(tuple_count)) + "]"
                        neg_inf_value = "[" + ", ".join(f"{neg_inf_value}" for i in range(tuple_count)) + "]"
                        nan_value = "[" + ", ".join(f"{nan_value}" for i in range(tuple_count)) + "]"
                        snan_value = "[" + ", ".join(f"{snan_value}" for i in range(tuple_count)) + "]"
                    if array_depth > 0:
                        attribute_type_name += "[]"
                        pos_inf_value = f"[{pos_inf_value}, {pos_inf_value}]"
                        neg_inf_value = f"[{neg_inf_value}, {neg_inf_value}]"
                        nan_value = f"[{nan_value}, {nan_value}]"
                        snan_value = f"[{snan_value}, {snan_value}]"
                    inf_nan_description = f"""{{
                        "InfNanNode" : {{
                            "{ogn.NodeTypeKeys.DESCRIPTION}" : "This node has attributes with Inf/Nan values",
                            "{ogn.NodeTypeKeys.INPUTS}" : {{
                                "positiveInf" : {{
                                    "description": "This is an attribute whose default is positive infinity",
                                    "type": "{attribute_type_name}",
                                    "default": {pos_inf_value}
                                }},
                                "negativeInf" : {{
                                    "description": "This is an attribute whose default is negative infinity",
                                    "type": "{attribute_type_name}",
                                    "default": {neg_inf_value}
                                }},
                                "nanValue" : {{
                                    "description": "This is an attribute whose default is NaN",
                                    "type": "{attribute_type_name}",
                                    "default": {nan_value}
                                }},
                                "snanValue" : {{
                                    "description": "This is an attribute whose default is a signaling NaN",
                                    "type": "{attribute_type_name}",
                                    "default": {snan_value}
                                }}
                            }}
                        }}
                    }}"""
                    if attribute_type_name in allow_nan_inf:
                        inf_nan_node = ogn.NodeInterfaceWrapper(inf_nan_description, "test")
                        _ = self.validate_node(inf_nan_node, "test.InfNanNode")
                    else:
                        with self.assertRaises(
                            ogn.ParseError, msg=f"Parsing node with Inf/Nan values {inf_nan_description}"
                        ):
                            ogn.NodeInterfaceWrapper(inf_nan_description, "test")

    # --------------------------------------------------------------------------------------------------------------
    async def test_type_generation(self):
        """Test of code generation using the various type definitions"""
        test_node_type = """
        {
            "TestDataTypes" : {
                "description": "Test node for data type code generation",
                "version": 1,
                "outputs": {
                    "output1" : {
                        "description": "First output",
                        "type": "TYPE"DEFAULT
                    }
                }
            }
        }
        """
        # Set of types tailored to handle specific code paths in the generator
        generation_configurations = [
            ("quatf[4]", "[0.0, 0.0, 0.0, 0.0]"),
            ("quatf[4][]", "[]"),
            ("quatf[4][]", None),
        ]
        for data_type, default_value in generation_configurations:
            definition = test_node_type.replace("TYPE", data_type)
            default_replacement = ""
            if default_value is not None:
                default_replacement = f', "default": {default_value}'
            definition = definition.replace("DEFAULT", f"{default_replacement}")
            _ = ogn.code_generation(definition, "OgnTest", "ogn.test", "ogn.test")

    # --------------------------------------------------------------------------------------------------------------
    async def test_basic_properties(self):
        """Walk the list of all attribute types to get basic properties for each of them and validate them.
        This is done separately from full parsing to keep the test execution time down.
        """

        def _string_or_none(value: str | None):
            self.assertTrue(value is None or isinstance(value, str))

        for base_type_name, attribute_manager_type in ogn.ALL_ATTRIBUTE_TYPES.items():
            args = ["outputs:testAttr", base_type_name]
            if attribute_manager_type.OGN_TYPE == "union":
                args.append({})
            is_extended = base_type_name in ["union", "any"]

            for tuple_count in attribute_manager_type.tuples_supported():
                for array_depth in attribute_manager_type.array_depths_supported():
                    attribute_manager = attribute_manager_type(*args)
                    attribute_manager.tuple_count = tuple_count
                    attribute_manager.array_depth = array_depth

                    # Check that some simple property value requests return something reasonable
                    self.assertTrue(attribute_manager.supports_metadata())
                    _string_or_none(attribute_manager.base_data_type_description())
                    _string_or_none(attribute_manager.data_type_description())
                    _string_or_none(attribute_manager.cpp_base_type_name())
                    _string_or_none(attribute_manager.cpp_role_name())
                    _string_or_none(attribute_manager.cpp_default_initializer())
                    _string_or_none(attribute_manager.fabric_raw_type())
                    _string_or_none(attribute_manager.cuda_base_type_name())
                    _string_or_none(attribute_manager.cuda_role_name())
                    _string_or_none(attribute_manager.cuda_element_type_name())
                    _string_or_none(attribute_manager.cuda_type_name())
                    with suppress(ogn.ParseError):
                        _string_or_none(attribute_manager.usd_type_name())
                    with suppress(ogn.ParseError):
                        _string_or_none(attribute_manager.create_type_name())
                    _string_or_none(attribute_manager.sdf_base_type())
                    _string_or_none(attribute_manager.python_attribute_name())
                    _string_or_none(attribute_manager.python_type_name())
                    _string_or_none(attribute_manager.python_type_annotation())
                    _string_or_none(attribute_manager.python_role_name())
                    _string_or_none(attribute_manager.python_value_as_str("hello"))
                    _string_or_none(attribute_manager.python_value_as_repr("hello"))
                    if is_extended:
                        self.assertTrue(attribute_manager.is_dynamic())
                        self.assertIsNotNone(attribute_manager.python_extended_type()[1])
                        self.assertFalse(attribute_manager.cpp_extended_type().endswith("Regular"))
                        self.assertTrue(len(attribute_manager.usd_type_accepted_description()) > 0)
                    else:
                        self.assertFalse(attribute_manager.is_dynamic())
                        self.assertIsNone(attribute_manager.python_extended_type()[1])
                        self.assertTrue(attribute_manager.cpp_extended_type().endswith("Regular"))

                    self.assertTrue(isinstance(attribute_manager.cuda_configuration(), CudaConfiguration))
                    self.assertTrue(isinstance(attribute_manager.cuda_includes(), list))
                    attribute_manager.add_python_imports()

                    self.assertEqual(2, len(attribute_manager.cpp_initializer()))
                    self.assertTrue(isinstance(attribute_manager.cpp_includes(), list))
                    self.assertTrue(isinstance(attribute_manager.fabric_pointer_exists(), list))
                    self.assertTrue(isinstance(attribute_manager.requires_default(), bool))
                    self.assertTrue(isinstance(attribute_manager.has_can_vectorize(), bool))
                    self.assertTrue(isinstance(attribute_manager.require_precompute_invalidation(), bool))

                    if isinstance(attribute_manager, ogn.NumericAttributeManager):
                        self.assertTrue(
                            attribute_manager.numerical_type()
                            in [
                                ogn.NumericAttributeManager.TYPE_OTHER,
                                ogn.NumericAttributeManager.TYPE_INTEGER,
                                ogn.NumericAttributeManager.TYPE_UNSIGNED_INTEGER,
                                ogn.NumericAttributeManager.TYPE_DECIMAL,
                                ogn.NumericAttributeManager.TYPE_FLOAT,
                                ogn.NumericAttributeManager.TYPE_OBJECT_ID,
                            ]
                        )

                    for memory_type in ogn.MemoryTypeValues.ALL:
                        attribute_manager.memory_type = memory_type

                        self.assertTrue(isinstance(attribute_manager.cpp_typedef_definitions(), list))

                        output = IndentedOutput(io.StringIO())
                        attribute_manager.generate_python_property_code(output)
                        self.assertTrue(len(str(output)) > 0)

                        output = IndentedOutput(io.StringIO())
                        attribute_manager.generate_python_batched_property_code(0, output)
                        self.assertTrue(len(str(output)) > 0)

                        output = IndentedOutput(io.StringIO())
                        attribute_manager.generate_python_validation(output)
                        self.assertTrue(len(str(output)) >= 0)

                        output = IndentedOutput(io.StringIO())
                        if isinstance(attribute_manager, TokenAttributeManager):
                            attribute_manager.default = "red"
                            attribute_manager.cpp_pre_initialization(output)
                            attribute_manager.default = ["red"]

                        attribute_manager.cpp_pre_initialization(output)
                        self.assertTrue(len(str(output)) >= 0)

                        output = IndentedOutput(io.StringIO())
                        attribute_manager.cpp_post_initialization(output)
                        self.assertTrue(len(str(output)) >= 0)

                        output = IndentedOutput(io.StringIO())
                        attribute_manager.emit_usd_declaration(output)
                        self.assertTrue(len(str(output)) > 0)

                        self.assertTrue(isinstance(attribute_manager.cpp_wrapper_class(), tuple))

                    py_values = attribute_manager.sample_values()
                    usd_values = attribute_manager.sample_values(for_usd=True)

                    self.assertEqual(py_values is None, usd_values is None)
                    if py_values is None:
                        continue

                    # The array types will have two copies of the values, tuples have one value per tuple
                    if array_depth > 0:
                        # Each sample will have two distinct values in it
                        self.assertEqual(2, len(py_values))
                        self.assertEqual(2, len(usd_values))

                        for index in range(2):
                            self.assertTrue(1 < len(py_values[index]))
                            self.assertEqual(1, len(usd_values[index]))

    # --------------------------------------------------------------------------------------------------------------
    async def test_edge_cases_matrix(self):
        """Check some of the data type generation code that handles non-standard values"""
        matrix_mgr = MatrixAttributeManager("outputs:mat", "matrixd")
        matrix_mgr.tuple_count = 2
        self.assertEqual(["false", "true"][matrix_mgr.is_required], matrix_mgr.is_required_as_string())
        self.assertEqual(matrix_mgr.tuple_argument(), ", 4")
        identity2 = ((1.0, 0.0), (0.0, 1.0))
        flat_array = (1.0, 0.0, 0.0, 1.0)
        self.assertEqual(matrix_mgr.empty_value(), [list(el) for el in identity2])
        self.assertEqual(list(flat_array), matrix_mgr.python_value(identity2))
        self.assertEqual(identity2, matrix_mgr.usd_value(identity2))

        matrix_mgr.array_depth = 1

        self.assertEqual(matrix_mgr.empty_value(), [])
        self.assertEqual(identity2, matrix_mgr.square_tuple(identity2))
        self.assertEqual(identity2, matrix_mgr.square_tuple(flat_array))
        with self.assertRaises(ogn.ParseError):
            matrix_mgr.square_tuple(((3,), (3,)))
        with self.assertRaises(ogn.ParseError):
            matrix_mgr.square_tuple((3,))
        with self.assertRaises(ogn.ParseError):
            matrix_mgr.validate_value((3,))
        matrix_mgr.minimum = [4.0, 0.0, 0.0, 1.0]
        matrix_mgr.maximum = [0.0, 0.0, 0.0, 1.0]
        with self.assertRaises(ogn.ParseError):
            matrix_mgr.validate_numbers_in_range(flat_array)
        with self.assertRaises(ogn.ParseError):
            matrix_mgr.validate_numbers_in_range(flat_array)

        self.assertEqual("{1.0,0.0,0.0,1.0}", matrix_mgr.cpp_tuple_value(identity2))
        self.assertEqual("{1.0,0.0,0.0,1.0}", matrix_mgr.cpp_tuple_value(flat_array))
        with self.assertRaises(ogn.ParseError):
            matrix_mgr.cpp_tuple_value((3,))
        with self.assertRaises(ogn.ParseError):
            matrix_mgr.cpp_tuple_value(((3,), (3,)))

        self.assertEqual([], matrix_mgr.python_value([]))
        self.assertEqual([list(flat_array)], matrix_mgr.python_value([identity2]))
        self.assertEqual(None, matrix_mgr.usd_value(None))
        self.assertEqual([identity2], matrix_mgr.usd_value([identity2]))
        with self.assertRaises(ogn.ParseError):
            matrix_mgr.usd_value(3)

        self.assertEqual(flat_array, MatrixAttributeManager.flattened_value(flat_array))
        with self.assertRaises(ogn.ParseError):
            MatrixAttributeManager.flattened_value(3)

    # --------------------------------------------------------------------------------------------------------------
    async def test_edge_cases_single(self):
        double2_mgr = DoubleAttributeManager("outputs:dbl2", "double")
        double2_mgr.tuple_count = 2
        self.assertEqual(double2_mgr.tuple_argument(), ", 2")
        with self.assertRaises(ogn.ParseError):
            double2_mgr.cpp_tuple_value(3)
        with self.assertRaises(ogn.ParseError):
            double2_mgr.cpp_tuple_value((1, 2, 3))

        array_mgr = DoubleAttributeManager("outputs:dbl", "double")
        array_mgr.array_depth = 1
        self.assertEqual(array_mgr.tuple_argument(), "")
        array_mgr.override_cpp_configuration("double", [], True)
        array_mgr.override_cuda_configuration("double", [], True)
        self.assertIsNotNone(array_mgr.cpp_configuration())
        self.assertTrue(array_mgr.cpp_element_value("inf").find("infinity") > 0)
        self.assertTrue(array_mgr.cpp_element_value("-inf").find("infinity") > 0)
        self.assertTrue(array_mgr.cpp_element_value("nan").find("NaN") > 0)
        self.assertTrue(array_mgr.cpp_element_value("snan").find("NaN") > 0)

        float_mgr = FloatAttributeManager("outputs:flt", "float")
        self.assertTrue(float_mgr.cpp_element_value("inf").find("infinity") > 0)
        self.assertTrue(float_mgr.cpp_element_value("-inf").find("infinity") > 0)
        self.assertTrue(float_mgr.cpp_element_value("nan").find("NaN") > 0)
        self.assertTrue(float_mgr.cpp_element_value("snan").find("NaN") > 0)

        int_mgr = IntAttributeManager("outputs:int", "int")
        with self.assertRaises(ogn.ParseError):
            int_mgr.validate_value(2147483648)
        self.assertEqual(int_mgr.cpp_element_value(1), "1")

        num_mgr = ogn.NumericAttributeManager("outputs:num", "number")
        self.assertEqual(ogn.NumericAttributeManager.TYPE_OTHER, num_mgr.numerical_type())

        base_mgr = ogn.AttributeManager("outputs:none", "none")
        with self.assertRaises(ogn.ParseError):
            base_mgr.cpp_element_value(2)
        with self.assertRaises(ogn.ParseError):
            base_mgr.cpp_element_value([])
        with self.assertRaises(ogn.ParseError):
            base_mgr.cpp_tuple_value([1, 2])
        with self.assertRaises(TypeError):
            base_mgr.cpp_base_type_name()
        with self.assertRaises(TypeError):
            base_mgr.cpp_role_name()
