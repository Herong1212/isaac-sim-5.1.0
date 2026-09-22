"""
Contains support for testing the ../generate_node.py script for attribute manager behaviour.

The framework is set up so that the tests can be run synchronously through main.py, or
asynchronously through the Kit testing framework.
"""

import json

import omni.graph.tools.ogn as ogn
import omni.kit.test
from omni.graph.tools._impl.node_generator.utils import ParseError


class TestNodeGeneratorAttributes(omni.kit.test.AsyncTestCase):
    """Unit test class for this script"""

    attr_index = 0

    # ======================================================================
    def create_attribute(self, attribute_type: str, attribute_default):
        """
        Create an attribute JSON structure and text with a generic description
        :param attribute_type: Attribute type
        :param attribute_default: Default value of the attribute
        :return: (Attribute Name, Attribute Info as JSON, Attribute as string) output for the attribute definition.
        Both versions are returned as the string attribute omits the enclosing curly braces so that
        attribute definitions can more easily be embedded in the JSON attribute lists
        """
        attribute_name = f"attr{TestNodeGeneratorAttributes.attr_index}"
        TestNodeGeneratorAttributes.attr_index += 1
        attribute_as_json = {
            f"{ogn.AttributeKeys.DESCRIPTION}": f"This is attribute {attribute_name}",
            f"{ogn.AttributeKeys.TYPE}": attribute_type,
            f"{ogn.AttributeKeys.DEFAULT}": attribute_default,
        }
        attribute_as_string = f'"{attribute_name}" : {json.dumps(attribute_as_json)}'
        return attribute_name, attribute_as_json, attribute_as_string

    # ======================================================================
    def validate_node(self, node_wrapper: ogn.NodeInterfaceWrapper, node_name: str):
        """
        Confirms that a named node exists and is a valid node in the interface wrapper.
        :param node_wrapper: ogn.NodeInterfaceWrapper class generated from the node description
        :param node_name: Name of the node to check
        :return: ogn.NodeInterface object for the named node
        """
        self.assertEqual(node_wrapper.node_interface.name, node_name, f"Expected node {node_name} not listed")
        return node_wrapper.node_interface

    # ======================================================================
    def validate_node_description(self, node_interface: ogn.NodeInterface, expected_description: str):
        """
        Validate that the node interface has parsed a description with the expected name
        :param node_interface: ogn.NodeInterface class of the node being checked
        :param expected_description: Description string the node is expected to have
        """
        self.assertEqual(
            node_interface.description, expected_description, f"Description for node {node_interface.name} not correct"
        )

    # ======================================================================
    def test_attribute_types(self):
        """Test for extracting the correct attribute manager from a type description"""
        import omni.graph.tools._impl.node_generator.attributes.management as management_module

        description = {"type": None, "optional": True, "description": "No description"}
        # KEY: attribute type name, VALUE: name of attribute manager for that type
        test_data = {
            "bool": "BoolAttributeManager",
            "double": "DoubleAttributeManager",
            "float": "FloatAttributeManager",
            "half": "HalfAttributeManager",
            "int": "IntAttributeManager",
            "int64": "Int64AttributeManager",
            "string": "StringAttributeManager",
            "token": "TokenAttributeManager",
            "colord": "ColorAttributeManager",
            "colorf": "ColorAttributeManager",
            "colorh": "ColorAttributeManager",
            "execution": "ExecutionAttributeManager",
            "frame": "FrameAttributeManager",
            "matrixd": "MatrixAttributeManager",
            "normald": "NormalAttributeManager",
            "normalf": "NormalAttributeManager",
            "normalh": "NormalAttributeManager",
            "pointd": "PointAttributeManager",
            "pointf": "PointAttributeManager",
            "pointh": "PointAttributeManager",
            "texcoordd": "TexCoordAttributeManager",
            "texcoordf": "TexCoordAttributeManager",
            "texcoordh": "TexCoordAttributeManager",
            "timecode": "TimeCodeAttributeManager",
            "transform": "FrameAttributeManager",
            "uchar": "UCharAttributeManager",
            "uint": "UIntAttributeManager",
            "uint64": "UInt64AttributeManager",
            "vectord": "VectorAttributeManager",
            "vectorf": "VectorAttributeManager",
            "vectorh": "VectorAttributeManager",
        }
        for attribute_type, manager_name in test_data.items():
            expected_manager = getattr(management_module, manager_name)
            # Check tuple and array combinations
            for tuple_count in expected_manager.tuples_supported():
                for array_depth in expected_manager.array_depths_supported():
                    suffix = "" if tuple_count < 2 else f"[{tuple_count}]"
                    suffix += "" if array_depth == 0 else "[]"
                    description["type"] = f"{attribute_type}{suffix}"
                    manager = ogn.get_attribute_manager(f"{ogn.OUTPUT_NS}:attribute", attribute_data=description)
                    self.assertEqual(manager.__class__.__name__, manager_name)

    # ======================================================================
    def test_split_attributes(self):
        """Test for successful parsing of attribute union groups"""
        # Try each group by itself
        for group_name, literal_types in ogn.ATTRIBUTE_UNION_GROUPS.items():
            type_name, _, _, extra_info = ogn.split_attribute_type_name([group_name])
            self.assertEqual(type_name, "union")
            for literal_type in literal_types:
                self.assertTrue(literal_type in extra_info)

        # Test a combination of groups
        combo_groups = [["integral_scalers", "decimal_scalers"], ["arrays", "integral_arrays"]]
        for combo in combo_groups:
            type_name, _, _, extra_info = ogn.split_attribute_type_name(combo)
            self.assertEqual(type_name, "union")
            combo_expanded = ogn.expand_attribute_union_groups(combo)
            for literal_type in (name for name in (group for group in combo_expanded)):
                self.assertTrue(literal_type in extra_info)

    # ======================================================================
    def test_attributes(self):
        """Test for successful parsing of attributes within nodes"""
        input_name, input_json, input_description = self.create_attribute("float", 0.0)
        output_name, output_json, output_description = self.create_attribute("double", 0.0)
        state_name, state_json, state_description = self.create_attribute("double", 0.0)
        node_description = "This is a node with one of each type of attribute"
        one_attribute_node_description = f"""{{
            "EmptyAttributes" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : "{node_description}",
                "{ogn.NodeTypeKeys.INPUTS}" : {{
                    {input_description}
                }},
                "{ogn.NodeTypeKeys.OUTPUTS}" : {{
                    {output_description}
                }},
                "{ogn.NodeTypeKeys.STATE}" : {{
                    {state_description}
                }}
            }}
        }}"""
        one_attribute_node = ogn.NodeInterfaceWrapper(one_attribute_node_description, "test")
        node_interface = self.validate_node(one_attribute_node, "test.EmptyAttributes")
        self.validate_node_description(node_interface, node_description)
        self.assertEqual(1, len(node_interface.all_input_attributes()))
        self.assertEqual(1, len(node_interface.all_output_attributes()))
        self.assertEqual(1, len(node_interface.all_state_attributes()))
        (input1, attribute_group) = node_interface.attribute_by_name(input_name)
        self.assertTrue(
            input1 is not None and attribute_group == ogn.INPUT_GROUP, f"Input attributes should contain {input_name}"
        )
        self.assertEqual(
            input1.description, input_json[ogn.AttributeKeys.DESCRIPTION], "Description of input attribute"
        )
        self.assertEqual(input1.type, input_json[ogn.AttributeKeys.TYPE], "Type of input attribute")
        self.assertEqual(input1.default, input_json[ogn.AttributeKeys.DEFAULT], "Default value of input attribute")
        (output1, attribute_group) = node_interface.attribute_by_name(output_name)
        self.assertTrue(
            output1 is not None and attribute_group == ogn.OUTPUT_GROUP,
            f"Output attributes should contain {output_name}",
        )
        self.assertEqual(
            output1.description, output_json[ogn.AttributeKeys.DESCRIPTION], "Description of output attribute"
        )
        self.assertEqual(output1.type, output_json[ogn.AttributeKeys.TYPE], "Type of output attribute")
        self.assertEqual(output1.default, output_json[ogn.AttributeKeys.DEFAULT], "Default value of output attribute")
        (state1, attribute_group) = node_interface.attribute_by_name(state_name)
        self.assertTrue(
            state1 is not None and attribute_group == ogn.STATE_GROUP, f"State attributes should contain {state_name}"
        )
        self.assertEqual(
            state1.description, state_json[ogn.AttributeKeys.DESCRIPTION], "Description of state attribute"
        )
        self.assertEqual(state1.type, state_json[ogn.AttributeKeys.TYPE], "Type of state attribute")
        self.assertEqual(state1.default, state_json[ogn.AttributeKeys.DEFAULT], "Default value of state attribute")

    # ======================================================================
    def test_attribute_deprecation(self):
        """Test for successful parsing of deprecated attributes"""
        node_with_deprecated_attrs = f"""{{
            "DeprecatedAttrsNode" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is a node with several deprecated attributes.",
                "{ogn.NodeTypeKeys.INPUTS}" : {{
                    "specialCharsMsg": {{
                        "{ogn.AttributeKeys.DESCRIPTION}":
                            ["Deprecation msg has special chars that need to be properly escaped."],
                        "{ogn.AttributeKeys.TYPE}": "double",
                        "{ogn.AttributeKeys.DEPRECATED}":
                            "This message has a backslash \\\\, newline \\n, return \\r, and quotes \\\" '"
                    }},
                    "notDeprecated": {{
                        "{ogn.AttributeKeys.DESCRIPTION}": ["This attribute is not deprecated."],
                        "{ogn.AttributeKeys.TYPE}": "double"
                    }}
                }},
                "{ogn.NodeTypeKeys.OUTPUTS}" : {{
                    "arrayMsg": {{
                        "{ogn.AttributeKeys.DESCRIPTION}": ["Deprecation msg is an array of strings."],
                        "{ogn.AttributeKeys.TYPE}": "int",
                        "{ogn.AttributeKeys.DEPRECATED}": [
                            "This message is",
                            "spread across multiple",
                            "array elements."
                        ]
                    }}
                }},
                "{ogn.NodeTypeKeys.STATE}" : {{
                    "emptyMsg": {{
                        "{ogn.AttributeKeys.DESCRIPTION}": ["Deprecation msg is empty."],
                        "{ogn.AttributeKeys.TYPE}": "int",
                        "{ogn.AttributeKeys.DEPRECATED}": ""
                    }}
                }}
            }}
        }}"""
        node = ogn.NodeInterfaceWrapper(node_with_deprecated_attrs, "test")
        node_interface = self.validate_node(node, "test.DeprecatedAttrsNode")

        (attr, _is_output) = node_interface.attribute_by_name("specialCharsMsg")
        self.assertTrue(attr.is_deprecated, "Deprecated input attribute")
        self.assertEqual(
            attr.deprecation_msg,
            "This message has a backslash \\, newline \n, return \r, and quotes \" '",
            "Deprecation msg with special chars.",
        )

        (attr, _is_output) = node_interface.attribute_by_name("notDeprecated")
        self.assertFalse(attr.is_deprecated, "Non-deprecated input attribute")
        self.assertEqual(attr.deprecation_msg, "", "Deprecation msg should be empty.")

        (attr, _is_output) = node_interface.attribute_by_name("arrayMsg")
        self.assertTrue(attr.is_deprecated, "Deprecated output attribute")
        self.assertEqual(
            attr.deprecation_msg,
            "This message is spread across multiple array elements.",
            "Deprecation msg is an array of strings.",
        )

        (attr, _is_output) = node_interface.attribute_by_name("emptyMsg")
        self.assertTrue(attr.is_deprecated, "Deprecated state attribute")
        self.assertEqual(attr.deprecation_msg, "", "Deprecation msg is empty.")

    # ======================================================================
    def test_attribute_memory_type(self):
        """Test for successful parsing of attribute memory type"""
        cpu_cuda_node = f"""{{
            "CpuCudaNode" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is a node with one CUDA input and one CPU output",
                "{ogn.NodeTypeKeys.VERSION}": 1,
                "{ogn.NodeTypeKeys.MEMORY_TYPE}": "{ogn.MemoryTypeValues.CUDA}",
                "{ogn.NodeTypeKeys.INPUTS}" : {{
                    "inputCUDA": {{
                        "description": ["This is a CUDA input"],
                        "type": "double",
                        "default": 0.0
                    }}
                }},
                "{ogn.NodeTypeKeys.OUTPUTS}" : {{
                    "outputCPU": {{
                        "description": ["This is a CPU output"],
                        "type": "double",
                        "memoryType": "{ogn.MemoryTypeValues.CPU}"
                    }},
                    "outputAny": {{
                        "description": ["This is a runtime determined output"],
                        "type": "double",
                        "memoryType": "{ogn.MemoryTypeValues.ANY}"
                    }}
                }}
            }}
        }}"""
        cpu_cuda_node = ogn.NodeInterfaceWrapper(cpu_cuda_node, "test")
        node_interface = self.validate_node(cpu_cuda_node, "test.CpuCudaNode")
        (input1, _) = node_interface.attribute_by_name("inputCUDA")
        self.assertEqual(input1.memory_type, ogn.MemoryTypeValues.CUDA, "Input inheriting CUDA type from node")
        (output1, _) = node_interface.attribute_by_name("outputCPU")
        self.assertEqual(output1.memory_type, ogn.MemoryTypeValues.CPU, "Output overriding CUDA type from node")

    # ======================================================================
    def test_attribute_metadata(self):
        """Test for successful parsing of attribute metadata"""
        node_with_attr_metadata = f"""{{
            "NodeWithAttributeMetadata" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is a node with metadata on an attribute",
                "{ogn.NodeTypeKeys.VERSION}": 1,
                "{ogn.NodeTypeKeys.TOKENS}": ["foo", "bar"],
                "{ogn.NodeTypeKeys.INPUTS}" : {{
                    "inputMeta": {{
                        "description": ["This is an input with metadata"],
                        "type": "token",
                        "default": "foo",
                        "metadata": {{
                            "{ogn.MetadataKeys.HIDDEN}": "True",
                            "keyable": "True",
                            "{ogn.MetadataKeys.ALLOWED_TOKENS}": ["foo", "B"]
                        }}
                    }}
                }}
            }}
        }}"""
        node_with_attr_metadata = ogn.NodeInterfaceWrapper(node_with_attr_metadata, "test")
        node_interface = self.validate_node(node_with_attr_metadata, "test.NodeWithAttributeMetadata")
        (input1, _) = node_interface.attribute_by_name("inputMeta")
        expected_metadata = {
            ogn.MetadataKeys.HIDDEN: "True",
            "keyable": "True",
            ogn.MetadataKeys.ALLOWED_TOKENS: "foo,B",
            ogn.MetadataKeys.ALLOWED_TOKENS_RAW: '["foo", "B"]',
            ogn.MetadataKeys.DESCRIPTION: "This is an input with metadata",
            ogn.MetadataKeys.DEFAULT: '"foo"',
        }
        self.assertEqual(input1.metadata, expected_metadata, "Input attribute with metadata")
        # Check that node tokens and allowedTokens are consolidated
        expected_tokens = {"foo": "foo", "bar": "bar", "B": "B"}
        self.assertEqual(node_interface.tokens, expected_tokens)

    # ======================================================================
    def test_tokens_with_special_characters(self):
        """Test for successful parsing of attribute token metadata"""
        node_with_attr_metadata = f"""{{
            "NodeWithSpecialTokenCharacters" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is a node with special characters in the tokens",
                "{ogn.NodeTypeKeys.VERSION}": 1,
                "{ogn.NodeTypeKeys.TOKENS}": {{"fooLtBar": "foo < bar", "fooNeBar": "foo != bar"}},
                "{ogn.NodeTypeKeys.INPUTS}" : {{
                    "inputTokens": {{
                        "description": ["This is an input with metadata"],
                        "type": "token",
                        "default": "fooEqBar",
                        "metadata": {{
                            "{ogn.MetadataKeys.HIDDEN}": "True",
                            "keyable": "True",
                            "{ogn.MetadataKeys.ALLOWED_TOKENS}": {{"fooLtBar": "foo < bar", "fooEqBar": "foo == bar"}}
                        }}
                    }}
                }}
            }}
        }}"""
        node_with_attr_metadata = ogn.NodeInterfaceWrapper(node_with_attr_metadata, "test")
        node_interface = self.validate_node(node_with_attr_metadata, "test.NodeWithSpecialTokenCharacters")
        (input1, _) = node_interface.attribute_by_name("inputTokens")
        expected_metadata = {
            ogn.MetadataKeys.HIDDEN: "True",
            "keyable": "True",
            ogn.MetadataKeys.ALLOWED_TOKENS_RAW: '{"fooLtBar": "foo < bar", "fooEqBar": "foo == bar"}',
            ogn.MetadataKeys.ALLOWED_TOKENS: "foo < bar,foo == bar",
            ogn.MetadataKeys.DESCRIPTION: "This is an input with metadata",
            ogn.MetadataKeys.DEFAULT: '"foo == bar"',
        }
        self.assertEqual(input1.metadata, expected_metadata, "Input attribute with metadata")
        expected_tokens = {"fooLtBar": "foo < bar", "fooNeBar": "foo != bar", "fooEqBar": "foo == bar"}
        self.assertEqual(node_interface.tokens, expected_tokens)

    # ======================================================================
    def test_alternative_token_specification(self):
        """Test for successful use of allowed tokens as first order data with name-based default value"""
        node_with_alt_tokens = f"""{{
            "NodeWithAlternativeAllowedTokens" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is a node that sets token defaults by name",
                "{ogn.NodeTypeKeys.VERSION}": 1,
                "{ogn.NodeTypeKeys.INPUTS}" : {{
                    "inputTokens": {{
                        "description": ["This is an input with metadata"],
                        "type": "token",
                        "default": "fooLtBar",
                        "{ogn.MetadataKeys.ALLOWED_TOKENS}": {{"fooLtBar": "foo < bar", "fooEqBar": "foo == bar"}}
                    }}
                }}
            }}
        }}"""
        node_with_alt_tokens = ogn.NodeInterfaceWrapper(node_with_alt_tokens, "test")
        node_interface = self.validate_node(node_with_alt_tokens, "test.NodeWithAlternativeAllowedTokens")
        (input1, _) = node_interface.attribute_by_name("inputTokens")
        self.assertEqual(input1.metadata[ogn.MetadataKeys.DEFAULT], '"foo < bar"')

    # ======================================================================
    def test_attribute_with_invalid_extended_types(self):
        """Test for invalid extended types failing to parse"""
        node_with_invalid_type = f"""{{
            "NodeWithInvalidExtendedTypes" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is a node that uses an invalid extended type",
                "{ogn.NodeTypeKeys.VERSION}": 1,
                "{ogn.NodeTypeKeys.INPUTS}" : {{
                    "invalidExtendedType": {{
                        "description": ["This is an extended input"],
                        "type": ["bundle", "execution", "target"]
                    }}
                }}
            }}
        }}"""
        with self.assertRaises(ParseError):
            ogn.NodeInterfaceWrapper(node_with_invalid_type, "test")
