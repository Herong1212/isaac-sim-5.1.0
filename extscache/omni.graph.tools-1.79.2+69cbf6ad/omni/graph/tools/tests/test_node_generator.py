"""
Contains support for testing the ../generate_node.py script.
Comprehensive data type testing is in TestNodeGeneratorDataTypes.py

The framework is set up so that the tests can be run synchronously through main.py, or
asynchronously through the Kit testing framework.

 TODO: Tests for capabilities to be added
    - Nodes with multiline descriptions
    - Attributes with multiline descriptions
    - Include single or double quotes in descriptions
"""

# pylint: disable=broad-exception-raised
import json
from pathlib import Path

import omni.graph.tools.ogn as ogn
import omni.kit.test
from omni.graph.tools._impl.internal.extension_contents_1_18 import ExtensionContentsV118


class TestNodeGenerator(omni.kit.test.AsyncTestCase):
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
        attribute_name = f"attr{TestNodeGenerator.attr_index}"
        TestNodeGenerator.attr_index += 1
        attribute_as_json = {
            f"{ogn.AttributeKeys.DESCRIPTION}": f"This is attribute {attribute_name}",
            f"{ogn.AttributeKeys.TYPE}": attribute_type,
            f"{ogn.AttributeKeys.DEFAULT}": attribute_default,
        }
        attribute_as_string = f'"{attribute_name}" : {json.dumps(attribute_as_json)}'
        return attribute_name, attribute_as_json, attribute_as_string

    # ======================================================================
    def validate_node(self, node_wrapper: ogn.NodeInterfaceWrapper, node_name: str) -> ogn.NodeInterface:
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
    def test_attribute_defaults(self):
        """Test for successful parsing of defaults values for optional and array attributes"""
        # Test data consisting of values for array, optional, and default values.
        # When a value is "None" the property is omitted. Attribute is assumed to be an integer type.
        array_combinations = [
            [1, True, [1]],
            [1, True, None],
            [1, False, [1]],
            [1, None, [1]],
            [0, True, 1],
            [0, True, None],
            [0, False, 1],
            [0, None, 1],
        ]
        for array_value, optional_value, default_value in array_combinations:
            attr_type = f"int{'[]' * array_value}"
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
                    "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is a node with optional or array types",
                    "{ogn.NodeTypeKeys.INPUTS}" : {{
                        "a": {{
                            "description": "This is an a",
                            {optional_property}
                            {default_property}
                            "type": "{attr_type}"
                        }}
                    }}
                }}
            }}"""
            try:
                arrays = ogn.NodeInterfaceWrapper(arrays_description, "test")
                node_interface = self.validate_node(arrays, "test.Arrays")
                self.validate_node_description(node_interface, "This is a node with optional or array types")
            except Exception as error:  # pylint: disable=broad-except
                raise Exception(f"Failed parsing node description {arrays_description}") from error

    # ======================================================================
    def all_role_tuple_combinations(self):
        """Return a list of all tuple combinations allowed for all of the roles.

        If a role supports an arbitrary list of tuples then choose "2" as a representative example.

        Returns:
            List of (role, tupleList)
                role: Name of the attribute role
                tupleList: List of all tuples the role supports
        """
        all_roles = []
        for attribute_type, attribute_manager in ogn.ALL_ATTRIBUTE_TYPES.items():
            if getattr(attribute_manager, "roles", None) is not None:
                tuples_supported = attribute_manager.tuples_supported()
                if tuples_supported is None:
                    all_roles.append([attribute_type, 2])
                else:
                    for tuple_count in tuples_supported:
                        all_roles.append([attribute_type, tuple_count])
        return all_roles

    # ======================================================================
    def test_minmax_defaults(self):
        """Test the set of minimum and maximum value combinations that are allowed"""
        # Test data consisting of values for attribute type, minimum, maximum, and default values.
        # When a value is "None" the property is omitted.
        minmax_combinations = []

        # Add range tests for every type supporting min/max, arrays of them, and pairs of them
        for type_with_minmax in ["double", "float", "half"]:
            minmax_combinations.append([type_with_minmax, 1.0, 3.0, 2.0])
            minmax_combinations.append([type_with_minmax, 1.0, None, 2.0])
            minmax_combinations.append([type_with_minmax, None, 3.0, 2.0])
            minmax_combinations.append([f"{type_with_minmax}[]", 1.0, 3.0, [2.0, 2.0]])
            minmax_combinations.append([f"{type_with_minmax}[]", 1.0, None, [2.0, 2.0]])
            minmax_combinations.append([f"{type_with_minmax}[]", None, 3.0, [2.0, 2.0]])
            minmax_combinations.append([f"{type_with_minmax}[2]", [1.0, 5.0], [3.0, 7.0], [2.0, 6.0]])
            minmax_combinations.append([f"{type_with_minmax}[2]", [1.0, 5.0], None, [2.0, 6.0]])
            minmax_combinations.append([f"{type_with_minmax}[2]", None, [3.0, 7.0], [2.0, 6.0]])
            minmax_combinations.append([f"{type_with_minmax}[2][]", [1.0, 5.0], [3.0, 7.0], [[2.0, 6.0]]])
            minmax_combinations.append([f"{type_with_minmax}[2][]", [1.0, 5.0], None, [[2.0, 6.0]]])
            minmax_combinations.append([f"{type_with_minmax}[2][]", None, [3.0, 7.0], [[2.0, 6.0]]])
        for type_with_minmax in ["int", "int64"]:
            minmax_combinations.append([type_with_minmax, 1, 3, 2])
            minmax_combinations.append([type_with_minmax, 1, None, 2])
            minmax_combinations.append([type_with_minmax, None, 3, 2])
            minmax_combinations.append([f"{type_with_minmax}[]", 1, 3, [2, 2]])
            minmax_combinations.append([f"{type_with_minmax}[]", 1, None, [2, 2]])
            minmax_combinations.append([f"{type_with_minmax}[]", None, 3, [2, 2]])
            if type_with_minmax == "int":
                minmax_combinations.append([f"{type_with_minmax}[2]", [1, 5], [3, 7], [2, 6]])
                minmax_combinations.append([f"{type_with_minmax}[2]", [1, 5], None, [2, 6]])
                minmax_combinations.append([f"{type_with_minmax}[2]", None, [3, 7], [2, 6]])
                minmax_combinations.append([f"{type_with_minmax}[2][]", [1, 5], [3, 7], [[2, 6]]])
                minmax_combinations.append([f"{type_with_minmax}[2][]", [1, 5], None, [[2, 6]]])
                minmax_combinations.append([f"{type_with_minmax}[2][]", None, [3, 7], [[2, 6]]])
        for role_type, tuple_count in self.all_role_tuple_combinations():
            if role_type == "execution":
                # execution can only take on the values of the enum ExecutionAttributeState
                min_value = 0
                max_value = 2
                actual_value = 1
                minmax_combinations.append([f"{role_type}", min_value, max_value, actual_value])
            else:
                # Matrix types use only one dimension for their tuple count
                if role_type in ["matrixd", "matrixf", "matrixh", "frame", "transform"]:
                    min_value = []
                    max_value = []
                    actual_value = []
                    for _i in range(tuple_count):
                        min_value.append([1] * tuple_count)
                        max_value.append([5] * tuple_count)
                        actual_value.append([3] * tuple_count)
                else:
                    min_value = [1] * tuple_count
                    max_value = [5] * tuple_count
                    actual_value = [3] * tuple_count
                minmax_combinations.append([f"{role_type}[{tuple_count}]", min_value, max_value, actual_value])
                minmax_combinations.append([f"{role_type}[{tuple_count}][]", min_value, max_value, [actual_value]])

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
                    "{ogn.NodeTypeKeys.INPUTS}" : {{
                        "a": {{
                            "description": "This is an a",
                            {minimum_property}
                            {maximum_property}
                            {default_property}
                            "type": "{attribute_type}"
                        }}
                    }}
                }}
            }}"""
            try:
                minmax = ogn.NodeInterfaceWrapper(minmax_description, "test")
                node_interface = self.validate_node(minmax, "test.MinMax")
                self.validate_node_description(node_interface, "This is a node with all valid min/max combinations")
            except Exception as error:  # pylint: disable=broad-except
                raise Exception(minmax_description) from error

    # ======================================================================
    def test_comments(self):
        """Test for successful parsing of a trivial node description with comment fields"""
        comment_string = """
                "$arrayComment": [1, 2, 3],
                "$boolComment": true,
                "$numberComment": 2,
                "$objectComment": { "a" : 1 },
                "$stringComment": "Ignore me"
        """
        comment_node_description = f"""{{
            "CommentNode" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is a commented node",
                {comment_string},
                "{ogn.NodeTypeKeys.INPUTS}" : {{
                    {comment_string}
                }},
                "{ogn.NodeTypeKeys.OUTPUTS}" : {{
                    {comment_string}
                }}
            }},
            {comment_string}
        }}"""
        comment_node = ogn.NodeInterfaceWrapper(comment_node_description, "test")
        node_interface = self.validate_node(comment_node, "test.CommentNode")
        self.validate_node_description(node_interface, "This is a commented node")

    # ======================================================================
    def test_simple_nodes(self):
        """Test for successful parsing of some simple node descriptions"""
        empty_node_description = f"""{{
            "EmptyNode" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is an empty node"
            }}
        }}"""
        empty_node = ogn.NodeInterfaceWrapper(empty_node_description, "test")
        node_interface = self.validate_node(empty_node, "test.EmptyNode")
        self.validate_node_description(node_interface, "This is an empty node")

        # ----------------------------------------
        empty_attributes_description = f"""{{
            "EmptyAttributes" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is a node with no attributes",
                "{ogn.NodeTypeKeys.INPUTS}" : {{}},
                "{ogn.NodeTypeKeys.OUTPUTS}" : {{}}
            }}
        }}"""
        empty_attributes = ogn.NodeInterfaceWrapper(empty_attributes_description, "test")
        node_interface = self.validate_node(empty_attributes, "test.EmptyAttributes")
        self.validate_node_description(node_interface, "This is a node with no attributes")
        self.assertEqual(node_interface.all_input_attributes(), [])
        self.assertEqual(node_interface.all_output_attributes(), [])

    # ======================================================================
    def test_metadata(self):
        """Test for successful parsing of some node type metadata"""
        metadata_node_description = f"""{{
            "MetadataNode" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is node with metadata",
                "{ogn.NodeTypeKeys.METADATA}" : {{ "__testKey__" : "__testValue__", "hidden": true }},
                "{ogn.NodeTypeKeys.UI_NAME}": "Metadata Node",
                "{ogn.NodeTypeKeys.TAGS}": ["first", "second"]
            }}
        }}"""
        metadata_node = ogn.NodeInterfaceWrapper(metadata_node_description, "test")
        node_interface = self.validate_node(metadata_node, "test.MetadataNode")
        self.validate_node_description(node_interface, "This is node with metadata")
        self.assertEqual(node_interface.metadata["__testKey__"], "__testValue__")
        self.assertEqual(node_interface.metadata["hidden"], "True")
        self.assertEqual(node_interface.metadata[ogn.MetadataKeys.UI_NAME], "Metadata Node")
        self.assertEqual(node_interface.metadata[ogn.MetadataKeys.TAGS], "first,second")

    # ======================================================================
    def test_memory_type(self):
        """Test for successful parsing of some node memory type and cuda pointer value"""
        memory_node_description = f"""{{
            "MemoryTypeNode" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is node with CUDA CPU pointer types",
                "{ogn.NodeTypeKeys.MEMORY_TYPE}": "{ogn.MemoryTypeValues.CUDA}",
                "{ogn.NodeTypeKeys.CUDA_POINTERS}": "{ogn.CudaPointerValues.CPU}"
            }}
        }}"""
        metadata_node = ogn.NodeInterfaceWrapper(memory_node_description, "test")
        node_interface = self.validate_node(metadata_node, "test.MemoryTypeNode")
        self.validate_node_description(node_interface, "This is node with CUDA CPU pointer types")

    # ======================================================================
    def test_icon_simple(self):
        """Test for successful parsing of the simplified form of the icon description"""
        simple_icon_node_description = f"""{{
            "SimpleIconNode" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is node with a simplified icon description",
                "{ogn.NodeTypeKeys.VERSION}" : 1,
                "{ogn.NodeTypeKeys.ICON}": "icons/SimpleIcon.svg"
            }}
        }}"""
        metadata_node = ogn.NodeInterfaceWrapper(simple_icon_node_description, "test")
        node_interface = self.validate_node(metadata_node, "test.SimpleIconNode")
        self.validate_node_description(node_interface, "This is node with a simplified icon description")
        self.assertEqual(node_interface.icon_path, "icons/SimpleIcon.svg")
        with self.assertRaises(KeyError):
            _ = node_interface.metadata[ogn.MetadataKeys.ICON_COLOR]
        with self.assertRaises(KeyError):
            _ = node_interface.metadata[ogn.MetadataKeys.ICON_BACKGROUND_COLOR]
        with self.assertRaises(KeyError):
            _ = node_interface.metadata[ogn.MetadataKeys.ICON_BORDER_COLOR]

    # ======================================================================
    def test_icon_detailed(self):
        """Test for successful parsing of the detailed form of the icon description"""
        detailed_icon_node_description = f"""{{
            "DetailedIconNode" : {{
                "{ogn.NodeTypeKeys.DESCRIPTION}" : "This is node with a detailed icon description",
                "{ogn.NodeTypeKeys.VERSION}" : 1,
                "{ogn.NodeTypeKeys.ICON}": {{
                    "{ogn.IconKeys.PATH}": "icons/DetailedIcon.svg",
                    "{ogn.IconKeys.COLOR}": "#FFAABBCC",
                    "{ogn.IconKeys.BACKGROUND_COLOR}": [0, 1, 2, 133],
                    "{ogn.IconKeys.BORDER_COLOR}": "#DDCCBBAA"
                }}
            }}
        }}"""
        metadata_node = ogn.NodeInterfaceWrapper(detailed_icon_node_description, "test")
        node_interface = self.validate_node(metadata_node, "test.DetailedIconNode")
        self.validate_node_description(node_interface, "This is node with a detailed icon description")
        self.assertEqual(node_interface.icon_path, "icons/DetailedIcon.svg")
        self.assertEqual("#FFAABBCC", node_interface.metadata[ogn.MetadataKeys.ICON_COLOR])
        self.assertEqual("#85020100", node_interface.metadata[ogn.MetadataKeys.ICON_BACKGROUND_COLOR])
        self.assertEqual("#DDCCBBAA", node_interface.metadata[ogn.MetadataKeys.ICON_BORDER_COLOR])

    # ======================================================================
    def test_tests(self):
        """Test for successful parsing of combinations of values in the 'tests' property"""
        tests_node_format = """
        {
            "Add" : {
                "description" : "Add the two inputs to create the output",
                "inputs": {
                    "input1" : {
                        "description": "First input",
                        "type": "float",
                        "default": 0.0
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
                        "description": "Sum of the two inputs",
                        "type": "float[]"
                    },
                    "anotherOutput" : {
                        "description": "Dummy output for testing purposes",
                        "type": "int"
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
            '{"inputs:input1": 3.0, "inputs:input2": [1.0, 2.0], "outputs:output": [4.0, 5.0]}',
            '{"inputs:input1": 3.0, "inputs:input2": [1.0, 2.0], "inputs:x2": false, "outputs:output": [4.0, 5.0]}',
            '{"inputs:input1": 3.0, "inputs:input2": [1.0, 2.0], "outputs:output": [4.0, 5.0]},'
            '{"inputs:input1": 3.0, "inputs:input2": [1.0, 2.0], "outputs:output": [4.0, 5.0], "gpu": ["outputs:output"]}',
            '{"description": "More verbose formatting", "inputs": {"input1": 3.0, "input2": [1.0, 2.0]},'
            '"outputs": {"output": [4.0, 5.0]}}',
            '{"file": "MyTestFile.usda", "/PathToNode": {"outputs": {"output": [1.0, 2.0], "anotherOutput": 1}, "state": {"nodeState": 1}}}',
            '{"file": "MyTestFile.usda", "/PathToNode": {"outputs": {"output": [1.0, 2.0], "anotherOutput": 1}, "state_get": {"nodeState": 1}}}',
            '{"file": "MyTestFile.usda", "/PathToNode.outputs": {"output": [1.0, 2.0], "anotherOutput": 1}, "/PathToNode.state": {"nodeState": 1}}',
            '{"file": "MyTestFile.usda", "/PathToNode.outputs": {"output": [1.0, 2.0], "anotherOutput": 1}, "/PathToNode.state_get": {"nodeState": 1, "gpu": ["aa"], "file": ["bb"], "description": "cc"}}',
            '{"file": "MyTestFile.usda", "/PathToNode": {"outputs:output": [1.0, 2.0], "outputs:anotherOutput": 1, "state:nodeState": 1}, "gpu": ["/PathToNode.outputs:output", "/PathToNode.outputs:anotherOutput"]}',
            '{"file": "MyTestFile.usda", "/PathToNode": {"outputs:output": [1.0, 2.0], "outputs:anotherOutput": 1, "state_get:nodeState": 1}}',
            '{"file": "MyTestFile.usda", "/PathToNode.outputs:output": {"type": "float[]", "value": [1.0, 2.0]},'
            '"/PathToNode.outputs:anotherOutput": {"type": "int", "value": 1}, "gpu": ["/PathToNode.outputs:output"]}',
            '{"file": "MyTestFile.usda", "/PathToNode.state:nodeState": {"type": "int", "value": 1.0}}',
            '{"file": "MyTestFile.usda", "/PathToNode.state_get:nodeState": {"type": "int", "value": 1.0}}',
            # Testing that comments work properly in various situations.
            '{"$file": "PathToFile.usda", "setup": {}}',
            '{"$file": "MyTestFile.usda", "inputs:input1": 3.0, "inputs:input1": 1.0, "outputs:output": [4.0, 5.0]}',
            '{"file": "MyTestFile.usda", "/PathToNode": {"$inputs": {"input1": 1.0, "$input2": [1.0, 2.0]}, "outputs": {"output": [4.0, 5.0]}, "$gpu": ["aa"], "$file": ["bb"]}}',
            '{"file": "MyTestFile.usda", "$/PathToNode.inputs": {"input1": 1.0, "input2": [1.0, 2.0]}}',
            '{"file": "MyTestFile.usda", "/PathToNode": {"$inputs:input1": 1.0, "outputs:output": [4.0, 5.0], "$inputs:input2": [1.0, 2.0]}}',
            '{"file": "MyTestFile.usda", "$/PathToNode.inputs:input2": {"type": "float[]", "value": [1.0, 2.0]}}',
            '{"file": "MyTestFile.usda", "/PathToNode": {"$state_set": {"nodeState": 1}}}',
            '{"file": "MyTestFile.usda", "$/PathToNode.state_set": {"nodeState": 1}}',
            '{"file": "MyTestFile.usda", "/PathToNode": {"$state_set:nodeState": 1}}',
            '{"file": "MyTestFile.usda", "$/PathToNode.state_set:nodeState": {"type": "int", "value": 1}}',
        ]
        for test_configuration in test_configurations:
            tests_node_description = tests_node_format + f'"tests": [ {test_configuration}] }} }}'
            test_node = ogn.NodeInterfaceWrapper(tests_node_description, "test")
            _ = self.validate_node(test_node, "test.Add")

    # ======================================================================
    def test_comment_formatting(self):
        """Test for correct operation of the ogn.to_cpp_comments utility"""
        # List of test configuration pairs of [Input, [ExpectedOutputNoIndent, ExpectedOutputIndent4]]
        test_data = [
            ["abc", ["// abc", "    // abc"]],
            ["\nabc\n\n", ["//\n// abc\n//", "    //\n    // abc\n    //"]],
            ["abc\n   def\n   ghi", ["// abc\n//    def\n//    ghi", "    // abc\n    //    def\n    //    ghi"]],
        ]
        for test_input, test_outputs in test_data:
            self.assertEqual(test_outputs[0], ogn.to_cpp_comment(test_input))
            self.assertEqual(test_outputs[1], ogn.to_cpp_comment(test_input, indent_level=1))

        # JSON encodes multiline strings as a list of strings per line. Test that as well.
        # List is pairs of ([InputLines], [ExpectedOutputNoIndent, ExpectedOutputIndent4])
        # The outputs of these tests should match the ones in the list above
        test_list_data = [
            [["abc"], ["// abc", "    // abc"]],
            [["\n", "abc\n", "\n"], ["//\n// abc\n//", "    //\n    // abc\n    //"]],
            [
                ["abc\n", "   def\n", "   ghi\n"],
                ["// abc\n//    def\n//    ghi", "    // abc\n    //    def\n    //    ghi"],
            ],
        ]
        for test_inputs, test_outputs in test_list_data:
            test_input = "".join(test_inputs)
            self.assertEqual(test_outputs[0], ogn.to_cpp_comment(test_input))
            self.assertEqual(test_outputs[1], ogn.to_cpp_comment(test_input, indent_level=1))

    # ======================================================================
    def test_immediate(self):
        """Test for code generation directly from a dictionary to a string"""
        immediate_node_format = """
        {
            "Add" : {
                "description": "Add the two inputs to create the output",
                "version": 1,
                "extras": "python",
                "icon": "///AddIcon.svg",
                "inputs": {
                    "input1" : {
                        "description": "First input",
                        "type": "float",
                        "default": 0.0
                    },
                    "input2" : {
                        "description": "Second input",
                        "type": "float",
                        "default": 0.0
                    }
                },
                "outputs": {
                    "output": {
                        "description": "Sum of the two inputs",
                        "type": "float"
                    }
                },
                "tests": [
                    { "inputs:input1": 1.0, "inputs:input2": 2.0, "outputs:output": 3.0 }
                ]
            }
        }
        """
        # The icon must be an absolute path when generating directly from code as relative paths are assumed to
        # be relative to the location of the .ogn file, which doesn't exist in this case.
        this_dir = Path(__file__).parent
        immediate_node_format = immediate_node_format.replace("//", this_dir.as_posix())
        results = ogn.code_generation(immediate_node_format, "OgnTest", "ogn.test", "ogn.test")
        self.assertCountEqual(
            ["cpp", "docs", "icon", "python", "template", "tests", "usd", "node"], list(results.keys())
        )
        # It would be too tedious to continually adjust this tests every time any tiny little bit of code generation
        # changes so instead just check for some invariants.
        self.assertTrue(results["cpp"].find("class OgnTestDatabase") > 0)
        self.assertTrue(results["docs"].find(":orphan:") > 0)
        self.assertTrue("AddIcon.svg" in results["icon"])
        self.assertTrue(results["python"].find("class OgnTestDatabase(og.Database):") > 0)
        self.assertTrue(results["template"].find("compute(OgnTestDatabase& db)") > 0)
        self.assertTrue(results["tests"].find("async def test_data_access(self):") > 0)
        self.assertTrue(results["usd"].find('def OmniGraphNode "Template_ogn_test_Add"') > 0)

    # ======================================================================
    def test_scheduling(self):
        """Test for legal combinations of scheduling flags"""
        scheduling_format = """
        {{
            "ScheduleMe" : {{
                "description": "Schedule this node as it requests",
                "version": 1,
                "scheduling": {}
            }}
        }}
        """
        for scheduling_configuration, expected in ogn.SchedulingHints.legal_configurations():
            scheduling_description = scheduling_format.format(scheduling_configuration)
            results = ogn.code_generation(scheduling_description, "OgnTest", "ogn.test", "ogn.test")
            difference = expected.compare(results["node"].scheduling_hints)
            self.assertEqual([], difference, f"Error with configuration {scheduling_configuration}")

    # ==============================================================================================================
    def test_directory_scanning(self):
        """Tests the hardcoded assumptions made about how the directory tree is structured"""
        fake_extension = ExtensionContentsV118("not_an_extension", ogn, ogn.__file__)
        self.assertIsNotNone(fake_extension.config_dir)
        self.assertTrue(fake_extension.categories)
