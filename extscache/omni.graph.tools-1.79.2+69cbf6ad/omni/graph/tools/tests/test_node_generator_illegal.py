"""
Contains support for testing the ../generate_node.py script for illegal syntax or flag combinations.

The framework is set up so that the tests can be run synchronously through main.py, or
asynchronously through the Kit testing framework.
"""

import json
import os

import omni.graph.tools.ogn as ogn
import omni.kit.test
from omni.graph.tools._impl.node_generator.attributes.naming import CPP_KEYWORDS, PYTHON_KEYWORDS, SAFE_CPP_KEYWORDS


# --------------------------------------------------------------------------------------------------------------
class _ExpectedError:
    """
    Helper class used to prefix any pending error messages with [Expected Error]
    stdoutFailPatterns.exclude (defined in extension.toml) will cause these errors
    to be ignored when running tests.

    Note that it will prepend only the first error.

    Usage:
        with _ExpectedError():
            function_that_produced_error_output()

    """

    def __enter__(self):
        print("", flush=True)  # preflush any output, otherwise it may be appended to the next statement
        print("[Ignore this error/warning] ", end="", flush=True)

    def __exit__(self, exit_type, value, traceback):
        print("", flush=True)  # print a newline, to avoid actual errors being ignored


class TestNodeGeneratorIllegal(omni.kit.test.AsyncTestCase):
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
        attribute_name = f"attr{TestNodeGeneratorIllegal.attr_index}"
        TestNodeGeneratorIllegal.attr_index += 1
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
    def illegal_when_debugging(self, node_description: str, msg: str):
        """Run a parse that is only illegal when in debugging mode, otherwise it just generates warnings"""
        if os.getenv("OGN_STRICT_DEBUG"):
            with self.assertRaises(ogn.ParseError, msg=f"Parsing interface with {msg}\n{node_description}"):
                ogn.NodeInterfaceWrapper(node_description, "test")
        else:
            ogn.NodeInterfaceWrapper(node_description, "test")

    # ======================================================================
    async def test_illegal_arrays(self):
        """Test the set of array flag combinations that are not allowed"""
        # Test data consisting of values for array, optional, and default values.
        # When a value is "None" the property is omitted. Attribute is assumed to be an integer type.
        # Missing default values are permitted so only illegal values are tested.
        array_combinations = [
            [1, True, 1],
            [1, False, 1],
            [1, False, ["hello"]],
            [1, None, 1],
            [1, None, ["hello"]],
            [0, True, [1]],
            [0, False, [1]],
            [0, False, ["hello"]],
            [0, None, [1]],
            [0, None, ["hello"]],
            [2, True, [1]],
            [2, False, [1]],
            [2, False, ["hello"]],
            [2, None, [1]],
            [2, None, ["hello"]],
        ]
        for array_value, optional_value, default_value in array_combinations:
            attribute_type = f"int{'[]' * array_value}"
            if optional_value is None:
                optional_property = ""
            elif optional_value:
                optional_property = '"optional": true,'
            else:
                optional_property = '"optional": false,'
            if default_value is None:
                default_property = ""
            else:
                default_property = f'"default": {default_value},'
            arrays_description = f"""{{
                "Arrays" : {{
                    "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is a node with all valid array combinations",
                    "{ogn.NodeTypeKeys.VERSION}": 1,
                    "{ogn.NodeTypeKeys.INPUTS}" : {{
                        "a": {{
                            "{ogn.AttributeKeys.DESCRIPTION}": "This is an a",
                            {optional_property}
                            {default_property}
                            "{ogn.AttributeKeys.TYPE}": "{attribute_type}"
                        }}
                    }}
                }}
            }}"""
            with self.assertRaises(
                ogn.ParseError, msg=f"Parsing interface with illegal array parameter combinations {arrays_description}"
            ):
                ogn.NodeInterfaceWrapper(arrays_description, "test")

    # ======================================================================
    async def test_illegal_minmax(self):
        """Test the set of minimum and maximum value combinations that are not allowed"""
        # Test data consisting of values for attribute type, minimum, maximum, and default value
        # When a value is "None" the property is omitted.
        minmax_combinations = [["int", 1.0, None, 1], ["float", None, "hello", 1.0]]
        # Add range tests for every type supporting min/max, arrays of them, and pairs of them
        for type_with_minmax in [
            "double",
            "float",
            "colord",
            "colorf",
            "colorh",
            "normald",
            "normalf",
            "normalh",
            "pointd",
            "pointf",
            "pointh",
            "texcoordd",
            "texcoordf",
            "texcoordh",
            "vectord",
            "vectorf",
            "vectorh",
            "xform",
        ]:
            minmax_combinations.append([type_with_minmax, 1.0, 3.0, 0.0])  # Default < min
            minmax_combinations.append([type_with_minmax, 1.0, 3.0, 4.0])  # Default > max
            minmax_combinations.append([type_with_minmax, 3.0, 1.0, 2.0])  # max < min
            minmax_combinations.append([f"{type_with_minmax}[]", 1.0, 3.0, [0.0, 2.0]])
            minmax_combinations.append([f"{type_with_minmax}[]", 1.0, 3.0, [2.0, 4.0]])
            minmax_combinations.append([f"{type_with_minmax}[]", 3.0, 1.0, [2.0, 2.0]])
            minmax_combinations.append([f"{type_with_minmax}[2]", [1.0, 5.0], [3.0, 7.0], [0.0, 6.0]])
            minmax_combinations.append([f"{type_with_minmax}[2]", [1.0, 5.0], [3.0, 7.0], [2.0, 8.0]])
            minmax_combinations.append([f"{type_with_minmax}[2]", [3.0, 7.0], [1.0, 5.0], [2.0, 6.0]])
            minmax_combinations.append([f"{type_with_minmax}[2][]", [1.0, 5.0], [3.0, 7.0], [[0.0, 6.0]]])
            minmax_combinations.append([f"{type_with_minmax}[2][]", [1.0, 5.0], [3.0, 7.0], [[2.0, 8.0]]])
            minmax_combinations.append([f"{type_with_minmax}[2][]", [3.0, 7.0], [1.0, 5.0], [[2.0, 6.0]]])
        for type_with_minmax in ["half", "int", "int64", "uchar", "uint", "uint64"]:
            minmax_combinations.append([type_with_minmax, 1, 3, 0])  # Default < min
            minmax_combinations.append([type_with_minmax, 1, 3, 4])  # Default > max
            minmax_combinations.append([type_with_minmax, 3, 1, 2])  # max < min
            minmax_combinations.append([f"{type_with_minmax}[]", 1, 3, [0, 2]])
            minmax_combinations.append([f"{type_with_minmax}[]", 1, 3, [2, 4]])
            minmax_combinations.append([f"{type_with_minmax}[]", 3, 1, [2, 2]])
            minmax_combinations.append([f"{type_with_minmax}[2]", [1, 5], [3, 7], [0, 6]])
            minmax_combinations.append([f"{type_with_minmax}[2]", [1, 5], [3, 7], [2, 8]])
            minmax_combinations.append([f"{type_with_minmax}[2]", [3, 7], [1, 5], [2, 6]])
            minmax_combinations.append([f"{type_with_minmax}[2][]", [1, 5], [3, 7], [[0, 6]]])
            minmax_combinations.append([f"{type_with_minmax}[2][]", [1, 5], [3, 7], [[2, 8]]])
            minmax_combinations.append([f"{type_with_minmax}[2][]", [3, 7], [1, 5], [[2, 6]]])
        # Add one test for every type that does not support min/max values
        for type_without_minmax in ["bool", "string", "token"]:
            minmax_combinations.append([type_without_minmax, 1, None, 2])
            minmax_combinations.append([type_without_minmax, None, 3, 2])
        for attribute_type, minimum_value, maximum_value, default_value in minmax_combinations:
            if minimum_value is None:
                minimum_property = ""
            else:
                minimum_property = f'"minimum": {minimum_value},'
            if maximum_value is None:
                maximum_property = ""
            else:
                maximum_property = f'"maximum": {maximum_value},'
            if default_value is None:
                default_property = ""
            else:
                default_property = f'"default": {default_value},'
            minmax_description = f"""{{
                "MinMax" : {{
                    "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is a node with all valid min/max combinations",
                    "{ogn.NodeTypeKeys.VERSION}": 1,
                    "{ogn.NodeTypeKeys.INPUTS}" : {{
                        "a": {{
                            "description": "This is an a",
                            {minimum_property}
                            {maximum_property}
                            {default_property}
                            "{ogn.AttributeKeys.TYPE}": "{attribute_type}"
                        }}
                    }}
                }}
            }}"""
            with self.assertRaises(
                ogn.ParseError,
                msg=f"Parsing interface with illegal min/max parameter combinations {minmax_description}",
            ):
                ogn.NodeInterfaceWrapper(minmax_description, "test")

    # ======================================================================
    async def test_illegal_nodes(self):
        """Test for correctly failed parsing of some illegal node descriptions"""
        empty_json = "{}"
        with self.assertRaises(ogn.ParseError, msg="Parsing interface with no nodes"):
            ogn.NodeInterfaceWrapper(empty_json, "test")

        # ----------------------------------------
        illegal_json = f'"{ogn.NodeTypeKeys.DESCRIPTION}" : "This is a node"'
        with self.assertRaises(ogn.ParseError, msg="Parsing illegal json"):
            ogn.NodeInterfaceWrapper(illegal_json, "test")

        # ----------------------------------------
        illegal_node = f'{{ "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is a node" }}'
        with self.assertRaises(ogn.ParseError, msg="Parsing illegal node"):
            ogn.NodeInterfaceWrapper(illegal_node, "test")

        # ----------------------------------------
        invalid_node = f'{{ "123Node" : {{ "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is an illegally named node" }} }}'
        with self.assertRaises(ogn.ParseError, msg="Parsing interface with illegal node name"):
            ogn.NodeInterfaceWrapper(invalid_node, "test")

        # ----------------------------------------
        illegal_multiple_nodes = f"""{{
            "LegalFirstNode" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : "This empty node is legal"
            }},
            "IllegalSecondNode" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : "This second node is legal"
            }}
        }}"""
        with self.assertRaises(ogn.ParseError, msg="Parsing interface with illegal multiple nodes"):
            ogn.NodeInterfaceWrapper(illegal_multiple_nodes, "test")

        # ----------------------------------------
        illegal_memory_type = f"""{{
            "IllegalMemoryType" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is a node with an illegal memory type",
                "{ogn.NodeTypeKeys.MEMORY_TYPE}" : "foo"
            }}
        }}"""
        with self.assertRaises(ogn.ParseError, msg="Parsing interface with illegal memory type"):
            ogn.NodeInterfaceWrapper(illegal_memory_type, "test")

        # ----------------------------------------
        illegal_description_empty = f"""{{
            "IllegalDescriptionEmpty" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : [""]
            }}
        }}"""
        self.illegal_when_debugging(illegal_description_empty, "illegal empty description")

        # ----------------------------------------
        illegal_description_null = f"""{{
            "IllegalDescriptionNull" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : ""
            }}
        }}"""
        self.illegal_when_debugging(illegal_description_null, "illegal null description")

        # ----------------------------------------
        illegal_description_empty_list = f"""{{
            "IllegalDescriptionEmptyList" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : []
            }}
        }}"""
        self.illegal_when_debugging(illegal_description_empty_list, "illegal empty list description")

        # ----------------------------------------
        illegal_attribute_memory_type = f"""{{
            "IllegalAttributeMemoryType" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is a node with an illegal attribute memory type",
                "{ogn.NodeTypeKeys.VERSION}": 1,
                "{ogn.NodeTypeKeys.INPUTS}" : {{
                    "input1": {{
                        "{ogn.AttributeKeys.DESCRIPTION}": "This is the first input",
                        "{ogn.AttributeKeys.TYPE}": "float",
                        "{ogn.AttributeKeys.DEFAULT}": 1.0,
                        "{ogn.AttributeKeys.MEMORY_TYPE}": "foo"
                    }}
                }}
            }}
        }}"""
        with self.assertRaises(ogn.ParseError, msg="Parsing interface with illegal attribute memory type"):
            ogn.NodeInterfaceWrapper(illegal_attribute_memory_type, "test")

        # ----------------------------------------
        illegal_metadata = f"""{{
            "illegal_metadata" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is a node with an illegal metadata",
                "{ogn.NodeTypeKeys.VERSION}": 1,
                "{ogn.NodeTypeKeys.METADATA}" : "must be a dictionary"
            }}
        }}"""
        with self.assertRaises(ogn.ParseError, msg="Parsing interface with illegal metadata"):
            ogn.NodeInterfaceWrapper(illegal_metadata, "test")

        # ----------------------------------------
        illegal_ui_name_metadata = f"""{{
            "illegal_ui_name_metadata" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is a node with an illegal uiName metadata",
                "{ogn.NodeTypeKeys.VERSION}": 1,
                "{ogn.NodeTypeKeys.UI_NAME}" : ["must be a string"]
            }}
        }}"""
        with self.assertRaises(ogn.ParseError, msg="Parsing interface with illegal uiName metadata"):
            ogn.NodeInterfaceWrapper(illegal_ui_name_metadata, "test")

        # ----------------------------------------
        illegal_simple_icon = f"""{{
            "illegal_simple_icon" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is a node with an illegal simple icon path description",
                "{ogn.NodeTypeKeys.VERSION}": 1,
                "{ogn.NodeTypeKeys.ICON}" : ["icon cannot be a list"]
            }}
        }}"""
        with self.assertRaises(ogn.ParseError, msg="Parsing interface with illegal simplified icon path"):
            ogn.NodeInterfaceWrapper(illegal_simple_icon, "test")

        # ----------------------------------------
        illegal_detailed_icon = f"""{{
            "illegal_detailed_icon" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is a node with an illegal detailed icon path description",
                "{ogn.NodeTypeKeys.VERSION}": 1,
                "{ogn.NodeTypeKeys.ICON}" : {{ "illegal": "Illegal keyword" }}
            }}
        }}"""
        with self.assertRaises(ogn.ParseError, msg="Parsing interface with illegal detailed icon information"):
            ogn.NodeInterfaceWrapper(illegal_detailed_icon, "test")

        # ----------------------------------------
        illegal_colors = [
            "#FFGGFF99",
            123,
            "FF112233",
            "#11223344",
            {"red": 45},
            [1, 2, 3, 4, 5],
            [-1, 2, 3, 4],
            [256, 2, 3, 4],
        ]
        for illegal_color in illegal_colors:
            illegal_icon_color = f"""{{
                "illegal_icon_color" : {{
                    "{ogn.NodeTypeKeys.DESCRIPTION}" :
                        "This is a node with an illegal icon color definition {illegal_color}",
                    "{ogn.NodeTypeKeys.VERSION}" : 1,
                    "{ogn.NodeTypeKeys.ICON}" : {{ "color": "#FFGGFF99" }}
                }}
            }}"""
            with self.assertRaises(
                ogn.ParseError, msg=f"Parsing interface with illegal icon color definition {illegal_color}"
            ):
                ogn.NodeInterfaceWrapper(illegal_icon_color, "test")

        # ----------------------------------------
        illegal_tags_metadata = f"""{{
            "illegal_tags_metadata" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is a node with an illegal tags metadata",
                "{ogn.NodeTypeKeys.VERSION}": 1,
                "{ogn.NodeTypeKeys.TAGS}" : {{"help": "cannot be a dictionary"}}
            }}
        }}"""
        with self.assertRaises(ogn.ParseError, msg="Parsing interface with illegal tags metadata"):
            ogn.NodeInterfaceWrapper(illegal_tags_metadata, "test")

        # ----------------------------------------
        illegal_memory_type = f"""{{
            "illegal_memory_type" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is a node with an illegal memory type",
                "{ogn.NodeTypeKeys.VERSION}": 1,
                "{ogn.NodeTypeKeys.MEMORY_TYPE}" : "gpu"
            }}
        }}"""
        with self.assertRaises(ogn.ParseError, msg="Parsing interface with illegal memory type"):
            ogn.NodeInterfaceWrapper(illegal_memory_type, "test")

        # ----------------------------------------
        illegal_cuda_pointers = f"""{{
            "illegal_cuda_pointers" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is a node with an illegal CUDA pointer type",
                "{ogn.NodeTypeKeys.VERSION}": 1,
                "{ogn.NodeTypeKeys.CUDA_POINTERS}" : "gpu"
            }}
        }}"""
        with self.assertRaises(ogn.ParseError, msg="Parsing interface with illegal CUDA pointer type"):
            ogn.NodeInterfaceWrapper(illegal_cuda_pointers, "test")

        # ----------------------------------------
        illegal_language = f"""{{
            "IllegalLanguage" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is a node with an illegal language",
                "{ogn.NodeTypeKeys.VERSION}": 1,
                "{ogn.NodeTypeKeys.LANGUAGE}" : "pascal"
            }}
        }}"""
        with self.assertRaises(ogn.ParseError, msg="Parsing interface with illegal language type"):
            ogn.NodeInterfaceWrapper(illegal_language, "test")

        # ----------------------------------------
        illegal_comments = [
            '"!comment": [1,2,3]',
            '"!comment": true',
            '"!comment": 2',
            '"!comment": { "a": 1 }',
            '"!comment": "Ignore me"',
        ]
        for illegal_comment in illegal_comments:
            for comment_location in range(0, 4):
                comment_strings = ["", "", "", ""]
                comment_strings[comment_location] = illegal_comment
                illegal_comment_node_description = f"""{{
                    "CommentNode" : {{
                        "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is a commented node",
                        "{ogn.NodeTypeKeys.VERSION}": 1,
                        {comment_strings[0]}
                        "{ogn.NodeTypeKeys.INPUTS}" : {{
                            {comment_strings[1]}
                        }},
                        "{ogn.NodeTypeKeys.OUTPUTS}" : {{
                            "{ogn.AttributeKeys.DESCRIPTION}": "This is a commented attribute",
                            {comment_strings[2]}
                        }}
                    }},
                    {comment_strings[3]}
                }}"""
                with self.assertRaises(
                    ogn.ParseError, msg=f"Parsing illegal comment {illegal_comment} in position {comment_location}"
                ):
                    ogn.NodeInterfaceWrapper(illegal_comment_node_description, "test")

    # ======================================================================
    async def test_illegal_attributes(self):
        """Test for correctly failed parsing of some illegal attribute descriptions"""
        # ----------------------------------------
        illegal_input_name = f"""{{
            "IllegalInputName" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is a node with an illegal input name",
                "{ogn.NodeTypeKeys.VERSION}": 1,
                "{ogn.NodeTypeKeys.INPUTS}" : {{
                    "1input1": {{
                        "{ogn.AttributeKeys.DESCRIPTION}": "This is the first input",
                        "{ogn.AttributeKeys.TYPE}": "float"
                    }}
                }}
            }}
        }}"""
        with self.assertRaises(ogn.ParseError, msg="Parsing interface with illegal input attribute name"):
            ogn.NodeInterfaceWrapper(illegal_input_name, "test")

        # ----------------------------------------
        illegal_duplicate_name = f"""{{
            "IllegalDuplicateName" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is a node with an illegal repeated name",
                "{ogn.NodeTypeKeys.VERSION}": 1,
                "{ogn.NodeTypeKeys.INPUTS}" : {{
                    "input1": {{
                        "{ogn.AttributeKeys.DESCRIPTION}": "This is the first input",
                        "{ogn.AttributeKeys.TYPE}": "float"
                    }},
                    "inputs:input1": {{
                        "{ogn.AttributeKeys.DESCRIPTION}": "This is also the first input",
                        "{ogn.AttributeKeys.TYPE}": "float"
                    }}
                }}
            }}
        }}"""
        with self.assertRaises(ogn.ParseError, msg="Parsing interface with illegal repeated attribute name"):
            ogn.NodeInterfaceWrapper(illegal_duplicate_name, "test")

        # ----------------------------------------
        illegal_output_name = f"""{{
            "IllegalOutputName" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is a node with an illegal output name",
                "{ogn.NodeTypeKeys.VERSION}": 1,
                "{ogn.NodeTypeKeys.OUTPUTS}" : {{
                    "output1(a)": {{
                        "{ogn.AttributeKeys.DESCRIPTION}": "This is the output",
                        "{ogn.AttributeKeys.TYPE}": "float"
                    }}
                }}
            }}
        }}"""
        with self.assertRaises(ogn.ParseError, msg="Parsing interface with illegal output attribute name"):
            ogn.NodeInterfaceWrapper(illegal_output_name, "test")

        # ----------------------------------------
        illegal_input_type = f"""{{
            "IllegalInputType" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is a node with an illegal input type",
                "{ogn.NodeTypeKeys.VERSION}": 1,
                "{ogn.NodeTypeKeys.INPUTS}" : {{
                    "input1": {{
                        "{ogn.AttributeKeys.DESCRIPTION}": "This is the first input",
                        "{ogn.AttributeKeys.TYPE}": "YogiBear"
                    }}
                }}
            }}
        }}"""
        with self.assertRaises(ogn.ParseError, msg="Parsing interface with illegal input attribute type"):
            ogn.NodeInterfaceWrapper(illegal_input_type, "test")

        # ----------------------------------------
        illegal_input_metadata = f"""{{
            "IllegalInputMetadata" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is a node with an illegal input metadata",
                "{ogn.NodeTypeKeys.VERSION}": 1,
                "{ogn.NodeTypeKeys.INPUTS}" : {{
                    "input1": {{
                        "{ogn.AttributeKeys.DESCRIPTION}": "This is the first input",
                        "{ogn.AttributeKeys.TYPE}": "int",
                        "{ogn.AttributeKeys.METADATA}": 3
                    }}
                }}
            }}
        }}"""
        with self.assertRaises(ogn.ParseError, msg="Parsing interface with illegal input attribute metadata"):
            ogn.NodeInterfaceWrapper(illegal_input_metadata, "test")

        # ----------------------------------------
        illegal_output_description = f"""{{
            "IllegalOutputDescription" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is a node with a missing attribute description",
                "{ogn.NodeTypeKeys.VERSION}": 1,
                "{ogn.NodeTypeKeys.OUTPUTS}" : {{
                    "output1(a)": {{
                        "{ogn.AttributeKeys.DESCRIPTION}": "This is the first output",
                        "{ogn.AttributeKeys.TYPE}": "float"
                    }}
                }}
            }}
        }}"""
        with self.assertRaises(ogn.ParseError, msg="Parsing interface with missing output attribute description"):
            ogn.NodeInterfaceWrapper(illegal_output_description, "test")

        # ----------------------------------------
        no_default_description = f"""{{
            "NoDefaultDescription" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is a node with a missing attribute default",
                "{ogn.NodeTypeKeys.VERSION}": 1,
                "{ogn.NodeTypeKeys.OUTPUTS}" : {{
                    "output1": {{
                        {ogn.AttributeKeys.DESCRIPTION}: "This is the output with no default",
                        "{ogn.AttributeKeys.TYPE}": "float"
                    }}
                }}
            }}
        }}"""
        with self.assertRaises(ogn.ParseError, msg="Parsing interface with missing output attribute default"):
            ogn.NodeInterfaceWrapper(no_default_description, "test")

        # ----------------------------------------
        attribute_description = f"""
                    "input1": {{
                        {ogn.AttributeKeys.DESCRIPTION}: "This is the first input",
                        "{ogn.AttributeKeys.TYPE}": "int"
                    }}
        """
        # Test configurations are a list of [input_attributes, output_attributes], each containing a duplicate
        duplicate_attribute_tests = [
            [[attribute_description, attribute_description], []],
            [[], [attribute_description, attribute_description]],
            [[attribute_description], [attribute_description]],
        ]
        for duplicate_attribute_test in duplicate_attribute_tests:
            inputs = ""
            if duplicate_attribute_test[0]:
                attribute_list = ",".join(duplicate_attribute_test[0])
                inputs = f'"{ogn.NodeTypeKeys.INPUTS}" : {{ {attribute_list} }},'
            outputs = ""
            if duplicate_attribute_test[1]:
                attribute_list = ",".join(duplicate_attribute_test[1])
                outputs = f'"{ogn.NodeTypeKeys.INPUTS}" : {{ {attribute_list} }},'
            duplicated_attributes_description = f"""{{
                "DuplicatedAttributes" : {{
                    "{ogn.NodeTypeKeys.VERSION}": 1,
                    {inputs}
                    {outputs}
                    "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is a node with duplicate attributes"
                }}
            }}"""
            with self.assertRaises(
                ogn.ParseError, msg=f"Parsing duplicate attributes {duplicated_attributes_description}"
            ):
                ogn.NodeInterfaceWrapper(duplicated_attributes_description, "test")

        # Test for attributes with existing but empty descriptions
        for attribute_type in [ogn.NodeTypeKeys.INPUTS, ogn.NodeTypeKeys.OUTPUTS]:
            for description_string in ['[""]', '""', "[]"]:
                illegal_empty_description = f"""{{
                    "IllegalEmptyDescription" : {{
                        "{ogn.NodeTypeKeys.DESCRIPTION}" : ["Node with empty attribute description"],
                        "{ogn.NodeTypeKeys.VERSION}": 1,
                        "{attribute_type}": {{
                            "attribute": {{
                                "{ogn.AttributeKeys.TYPE}": "float",
                                "{ogn.AttributeKeys.DEFAULT}": 0.0,
                                "{ogn.AttributeKeys.DESCRIPTION}": {description_string}
                            }}
                        }}
                    }}
                }}"""
                self.illegal_when_debugging(illegal_empty_description, "illegal empty attribute description")

    # ======================================================================
    async def test_illegal_tests(self):
        """Test for correct rejection of illegal combinations of values in the 'tests' property"""
        tests_node_format = """
        {
            "Add" : {
                "description": "Add the two inputs to create the output",
                "version": 1,
                "inputs": {
                    "input1" : {
                        "description": "Multiplier",
                        "type": "float",
                        "default": 0.0,
                        "minimum": 0.0,
                        "maximum": 1.0
                    },
                    "input2" : {
                        "description": "Second input",
                        "type": "float[]",
                        "default": [0.0]
                    },
                    "x2": {
                        "description": "Double the first input",
                        "type": "bool",
                        "optional": true
                    }
                },
                "outputs": {
                    "output": {
                        "description": "Element-wise product of the two inputs",
                        "type": "float[]",
                        "default": [0.0]
                    }
                },
                "state":{
                    "nodeState": {
                        "description": "Dummy node state",
                        "type": "int"
                    }
                },
        """
        test_configurations = [
            # Attribute not recognized
            '{"inputs:nobody": 1.0}',
            # Bad attribute data type
            '{"inputs:input1": true, "inputs:input2": [1.0, 2.0], "outputs:output": [4.0, 5.0]}',
            # Attribute value out of range
            '{"inputs:input1": 2.0, "inputs:input2": [1.0, 2.0], "outputs:output": [4.0, 5.0]}',
            # Bad optional attribute
            '{"inputs:input1": 1.0, "inputs:input2": [1.0, 2.0], "inputs:x2": 3, "outputs:output": [4.0, 5.0]}',
            # Bad optional attribute
            '{"inputs:input1": 1.0, "inputs:input2": [1.0, 2.0], "inputs:foo": 3, "outputs:output": [4.0, 5.0]}',
            # Bad gpu_outputs information
            '{"inputs:input1": true, "gpu": ["inputs:input1"]}',
            '{"inputs:input1": true, "gpu": ["blah"]}',
            '{"inputs:input1": true, "gpu": ["outputs:output", "inputs:input1"]}',
            '{"inputs:input1": true, "gpu": ["outputs:output", "state:state"]}',
            '{"inputs:input1": true, "gpu": ["outputs:output", "state_get:state_get"]}',
            '{"inputs:input1": true, "gpu": ["outputs:output", "state_set:state_set"]}',
            # Bad file name
            '{"file": 5.0}',
            # Illegal use of the 'setup' keyword in a test utilizing an external scene
            '{"file": "PathToFile.usda", "setup": {}}',
            # Illegal use of the 'inputs' keyword in tests utilizing an external scene
            '{"file": "MyTestFile.usda", "/PathToNode": {"inputs": {"input1": 1.0, "input2": [1.0, 2.0]}, "outputs": {"output": [4.0, 5.0]}}}',
            '{"file": "MyTestFile.usda", "/PathToNode.inputs": {"input1": 1.0, "input2": [1.0, 2.0]}}',
            '{"file": "MyTestFile.usda", "/PathToNode": {"inputs:input1": 1.0, "outputs:output": [4.0, 5.0], "inputs:input2": [1.0, 2.0]}}',
            '{"file": "MyTestFile.usda", "/PathToNode.inputs:input2": {"type": "float[]", "value": [1.0, 2.0]}}',
            # Illegal use of the 'state_set" keyword in tests utilizing an external scene
            '{"file": "MyTestFile.usda", "/PathToNode": {"state_set": {"nodeState": 1}}}',
            '{"file": "MyTestFile.usda", "/PathToNode.state_set": {"nodeState": 1}}',
            '{"file": "MyTestFile.usda", "/PathToNode": {"state_set:nodeState": 1}}',
            '{"file": "MyTestFile.usda", "/PathToNode.state_set:nodeState": {"type": "int", "value": 1}}',
            # Missing colon
            '{"file": "MyTestFile.usda", "/PathToNode": {"outputs:output": [1.0, 2.0], "outputsanotherOutput": 1, "state:nodeState": 1}}',
            # Bad gpu_outputs information
            '{"file": "MyTestFile.usda", "gpu": ["/PathToNode.inputs:input"]}',
            '{"file": "MyTestFile.usda", "gpu": ["/PathToNode.state:state"]}',
            '{"file": "MyTestFile.usda", "gpu": ["/PathToNode.state_get:state_get"]}',
            '{"file": "MyTestFile.usda", "gpu": ["/PathToNode.state_set:state_set"]}',
            '{"file": "MyTestFile.usda", "gpu": ["blah"]}',
            '{"file": "MyTestFile.usda", "gpu": ["outputs:myOutput"]}',
            '{"file": "MyTestFile.usda", "gpu": [".outputs:myOutput"]}',
            '{"file": "MyTestFile.usda", "/PathToNode": {"outputs:output": [1.0, 2.0], "gpu": ["outputs:myOutput"], "outputs:anotherOutput": 1, "state_get:nodeState": 1}}',
            '{"file": "MyTestFile.usda", "/PathToNode": {"outputs:output": [1.0, 2.0], "file": ["aFile"], "outputs:anotherOutput": 1, "state_get:nodeState": 1}}',
        ]
        for test_configuration in test_configurations:
            tests_node_description = (
                tests_node_format
                + f"""
                "tests": [ {test_configuration}]
            }}
        }}"""
            )
            with self.assertRaises(ogn.ParseError, msg=f"Parsing illegal test configuration {tests_node_description}"):
                ogn.NodeInterfaceWrapper(tests_node_description, "test")

    # ======================================================================
    async def test_illegal_scheduling(self):
        """Test for correct rejection of illegal combinations of scheduling flags"""
        scheduling_format = """
        {{
            "ScheduleMe" : {{
                "description": "Schedule this node as it requests",
                "version": 1,
                "scheduling": {}
            }}
        }}
        """
        for scheduling_configuration in ogn.SchedulingHints.illegal_configurations():
            scheduling_description = scheduling_format.format(scheduling_configuration)
            with self.assertRaises(ogn.ParseError, msg=f"Parsing illegal scheduling flags {scheduling_description}"):
                ogn.NodeInterfaceWrapper(scheduling_description, "test")

    # ======================================================================
    async def test_tokens_with_illegal_characters(self):
        """Test for successful parsing of attribute metadata"""
        node_name = "NodeWithSpecialTokenCharacters"
        node_with_illegal_tokens = json.loads(
            f"""{{
            "{node_name}" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is a node with special characters in the tokens",
                "{ogn.NodeTypeKeys.VERSION}": 1
            }}
        }}"""
        )
        illegal_tokens = [
            ["foo < bar", "foo != bar"],
            {"foo < bar": "fooLtBar"},
        ]
        for token_data in illegal_tokens:
            node_with_illegal_tokens[node_name][ogn.NodeTypeKeys.TOKENS] = token_data
            with self.assertRaises(ogn.ParseError, msg=f"Parsing illegal token names {node_with_illegal_tokens}"):
                ogn.NodeInterfaceWrapper(node_with_illegal_tokens, "test")

    # ======================================================================
    async def test_allowed_tokens_with_illegal_characters(self):
        """Test for successful parsing of attribute metadata"""
        node_name = "AttributeWithSpecialTokenCharacters"
        attr_with_illegal_tokens = json.loads(
            f"""{{
            "{node_name}" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is a node with special characters in the tokens",
                "{ogn.NodeTypeKeys.VERSION}": 1,
                "{ogn.NodeTypeKeys.INPUTS}" : {{
                    "inputTokens": {{
                        "description": ["This is an input with metadata"],
                        "type": "token",
                        "default": "foo",
                        "metadata": {{
                        }}
                    }}
                }}
            }}
        }}"""
        )
        illegal_tokens = [
            ["foo < bar", "foo != bar"],
            {"foo < bar": "fooLtBar"},
        ]
        for token_data in illegal_tokens:
            attr_with_illegal_tokens[node_name][ogn.NodeTypeKeys.INPUTS]["inputTokens"]["metadata"][
                ogn.MetadataKeys.ALLOWED_TOKENS
            ] = token_data
            with self.assertRaises(
                ogn.ParseError, msg=f"Parsing illegal allowedToken names {attr_with_illegal_tokens}"
            ):
                ogn.NodeInterfaceWrapper(attr_with_illegal_tokens, "test")

    # ======================================================================
    async def test_illegal_token_default(self):
        """Test for failure when specifying a default token that is not in the allowed list"""
        node_name = "NodeWithSpecialTokenCharacters"
        node_with_illegal_default = json.loads(
            f"""{{
            "{node_name}" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is a node with attributes with an illegal default token",
                "{ogn.NodeTypeKeys.VERSION}": 1,
                "{ogn.NodeTypeKeys.INPUTS}" : {{
                    "XXX": {{
                        "{ogn.AttributeKeys.DESCRIPTION}": "This is the token input",
                        "{ogn.AttributeKeys.TYPE}": "token",
                        "{ogn.AttributeKeys.DEFAULT}": "X",
                        "{ogn.AttributeKeys.ALLOWED_TOKENS}": "X"
                    }}
                }}
            }}
        }}"""
        )
        illegal_combinations = [
            ["foo", {"fooLtBar": "foo < bar", "fooEqBar": "foo == bar"}],
            ["foo", ["fooLtBar", "fooEqBar"]],
            ["foo", "bar"],
        ]
        for default_value, allowed_tokens in illegal_combinations:
            attr_definition = node_with_illegal_default[node_name][ogn.NodeTypeKeys.INPUTS]["XXX"]
            attr_definition[ogn.AttributeKeys.DEFAULT] = default_value
            attr_definition[ogn.AttributeKeys.ALLOWED_TOKENS] = allowed_tokens
            with self.assertRaises(ogn.ParseError, msg=f"Parsing illegal token defaults {node_with_illegal_default}"):
                ogn.NodeInterfaceWrapper(node_with_illegal_default, "test")

    # ======================================================================
    async def test_keyword_attributes(self):
        """Test for correctly failed parsing of attributes named after keywords"""
        python_keyword_attribute = f"""{{
            "PythonKeywordAttribute" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is a node with an illegal input name",
                "{ogn.NodeTypeKeys.VERSION}": 1,
                "{ogn.NodeTypeKeys.LANGUAGE}": "Python",
                "{ogn.NodeTypeKeys.INPUTS}" : {{
                    "beetleJuice": {{
                        "{ogn.AttributeKeys.DESCRIPTION}": "This is the first input",
                        "{ogn.AttributeKeys.TYPE}": "float"
                    }}
                }}
            }}
        }}"""
        for python_key in PYTHON_KEYWORDS:
            description = python_keyword_attribute.replace("beetleJuice", python_key)
            with self.assertRaises(ogn.ParseError, msg="Parsing interface with python keyword attribute name"):
                with _ExpectedError():
                    ogn.NodeInterfaceWrapper(description, "test")

        # --------------------------------------------------------------------------------------------------------------

        cpp_keyword_attribute = f"""{{
            "CppKeywordAttribute" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is a node with an illegal input name",
                "{ogn.NodeTypeKeys.VERSION}": 1,
                "{ogn.NodeTypeKeys.INPUTS}" : {{
                    "XXX": {{
                        "{ogn.AttributeKeys.DESCRIPTION}": "This is the first input",
                        "{ogn.AttributeKeys.TYPE}": "float"
                    }}
                }}
            }}
        }}"""
        for cpp_key in CPP_KEYWORDS:
            description = cpp_keyword_attribute.replace("XXX", cpp_key)
            if cpp_key in SAFE_CPP_KEYWORDS:
                self.assertIsNotNone(ogn.NodeInterfaceWrapper(description, "test"))
            else:
                with self.assertRaises(ogn.ParseError, msg="Parsing interface with C++ keyword attribute name"):
                    with _ExpectedError():
                        ogn.NodeInterfaceWrapper(description, "test")
