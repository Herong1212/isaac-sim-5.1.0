"""Support for generating simple regression test code for OmniGraph Nodes.

The tests do three things:
    1. Do a test "import" of the Python interface to the node
    2. Do a test load of the USDA template interface for the node
    3. Run all of the "tests" cases specified in the node's .ogn file

Exports:
    generate_tests: Create a TestNODE.py file containing standard unit tests of the node operation
"""

import shutil
from pathlib import Path
from typing import Any, List, Optional

from .attributes.management import list_without_runtime_attributes
from .generate_test_imports import ensure_test_is_imported
from .keys import MemoryTypeValues, TestKeys
from .nodes import NodeInterfaceGenerator
from .utils import GeneratorConfiguration, ParseError, ensure_writable_directory, logger

__all__ = ["generate_tests"]


class NodeTestGenerator(NodeInterfaceGenerator):
    """Manage the functions required to generate basic test scripts for a node"""

    def __init__(self, configuration: GeneratorConfiguration):  # noqa: PLW0246
        """Set up the generator and output the test scripts for the node

        Just passes the initialization on to the parent class. See the argument and
        exception descriptions there.
        """
        super().__init__(configuration)
        self.tests_data_directory: Path = None

    # ----------------------------------------------------------------------
    def interface_file_name(self) -> str:
        """Return the path to the name of the Python test file"""
        return self.test_class_name() + ".py"

    # ----------------------------------------------------------------------
    def test_class_name(self) -> str:
        """Returns the name to use for the test class and base name for the test file"""
        return f"Test{self.base_name}"

    # ----------------------------------------------------------------------
    def __find_and_copy_test_file(self, file_path: Path) -> Path:
        """Helper method that locates .ogn test files and copies them into the
        $BUILD/exts/omni.graph.myext/omni/graph/myext/ogn/tests/data/MyNodeBaseName
        directory. These can either be absolute paths or paths relative to the .ogn
        source file.

        Returns:
            Absolute path to the copied test file.

        Raises:
            ParseError: If the file path could not be recognized, or it did not reference an existing file
        """
        # Find the absolute location of the test file for copying.
        potential_path = file_path
        if not potential_path.is_absolute():
            if self.node_file_path is None:
                raise ParseError(f'Specified relative test file path "{potential_path}" but there is no .ogn path.')
            potential_path = Path(self.node_file_path).parent / potential_path
        if not potential_path.is_file():
            raise ParseError(f"Test file path {potential_path} does not exist.")

        # Non-usd/usda files should not be copied.
        if potential_path.suffix not in [".usd", ".usda"]:
            raise ParseError(f'Test file path must be a USD or USDA file. "{potential_path}" not allowed.')

        # Copy the test file into the shared tests data directory located at
        # $BUILD/exts/omni.graph.myext/omni/graph/myext/ogn/tests/data/MyNodeBaseName.
        # Note that each node's test scenes get grouped into separate folders to prevent
        # potential duplicate-naming collisions (e.g. if two different nodes use two
        # different test scenes that happen to share the same name and type).
        try:
            self.tests_data_directory = Path(self.output_path).parent / "data" / self.base_name
            ensure_writable_directory(self.tests_data_directory)
            shutil.copy(potential_path, self.tests_data_directory)
            return self.tests_data_directory / potential_path.name
        except Exception as error:
            raise ParseError("Failed to create tests data directory") from error

    # ----------------------------------------------------------------------
    def __generate_user_input_test_data(self, test_run: dict[str, any], node_path: str, node_test_data: dict):
        """Helper method for generating input user test data."""
        input_data = []
        for attribute, attribute_value in node_test_data.input_values.items():
            if isinstance(attribute, str):
                on_gpu = False
            else:
                on_gpu = attribute.memory_type != MemoryTypeValues.CPU
            input_data.append([attribute, attribute_value, on_gpu])
        test_run[node_path][TestKeys.INPUTS] = input_data

    # ----------------------------------------------------------------------
    def __generate_user_output_test_data(
        self, test_run: dict[str, any], node_path: str, node_test_data: dict, gpu_outputs: list[str]
    ):
        """Helper method for generating output user test data."""
        output_data = []
        for attribute, attribute_value in node_test_data.expected_outputs.items():
            if isinstance(attribute, str):
                on_gpu = attribute in gpu_outputs or (node_path + "." + attribute) in gpu_outputs
            else:
                if attribute.memory_type == MemoryTypeValues.ANY:
                    on_gpu = attribute.name in gpu_outputs or (node_path + "." + attribute.name) in gpu_outputs
                else:
                    on_gpu = attribute.memory_type != MemoryTypeValues.CPU
            output_data.append([attribute, attribute_value, on_gpu])
        test_run[node_path][TestKeys.OUTPUTS] = output_data

    # ----------------------------------------------------------------------
    def __generate_user_initial_state_test_data(self, test_run: dict[str, any], node_path: str, node_test_data: dict):
        """Helper method for generating initial state user test data."""
        state_data = []
        for attribute, attribute_value in node_test_data.state_initial_values.items():
            if isinstance(attribute, str):
                on_gpu = False
            else:
                on_gpu = attribute.memory_type != MemoryTypeValues.CPU
            state_data.append([attribute, attribute_value, on_gpu])
        test_run[node_path][TestKeys.STATE_SET] = state_data

    # ----------------------------------------------------------------------
    def __generate_user_final_state_test_data(self, test_run: dict[str, any], node_path: str, node_test_data: dict):
        """Helper method for generating final state user test data."""
        state_data = []
        for attribute, attribute_value in node_test_data.state_final_values.items():
            if isinstance(attribute, str):
                on_gpu = False
            else:
                on_gpu = attribute.memory_type != MemoryTypeValues.CPU
            state_data.append([attribute, attribute_value, on_gpu])
        test_run[node_path][TestKeys.STATE_GET] = state_data

    # ----------------------------------------------------------------------
    def generate_user_test_data(self, all_tests: List) -> list[dict[str, Any]]:
        """Generate the section of the user test that creates the test data to be iterated over.

        The variable "test_data" is set up to be a list of test data, whose elements consist of a dictionary
        whose key-value pairs are either ("file", file_path) or (node_path, dic[]), where the latter dictionary
        consists of up to four sub-lists:
            - values for input attributes, set before the test starts (empty for tests with specified test scenes).
            - values for output attributes, checked after the test finishes.
            - initial values for state attributes, set before the test starts (empty for tests with specified test scenes).
            - final values for state attributes, checked after the test finishes.
        Each of the data elements consist of a 3-tuple of the name of the attribute, the value for it, and whether the
        attribute's data should be manipulated on the GPU.

        Here's a simple example of two tests. In the first, two inputs are set, one output is checked, one state
        attribute has an initial value set and a final value checked, and a node of type "MyNodeType" is created
        before the test runs; note that no explicit scene is specified in the 1st test, hence why the node_path variable
        is blank. In the second example, we specify some test scene to use, and have a series of attributes that need
        to be checked on multiple different nodes (not just the node corresponding directly to the one defined in the
        .ogn file):
            TEST_DATA = [
                {
                    "": {
                        "inputs": [
                            ["inputs:attr", INPUT_VALUE, False],
                            ["inputs:attr2", INPUT_VALUE2, False],
                        ],
                        "outputs": [
                            ["outputs:attr", OUTPUT_VALUE, False],
                        ],
                        "state_set": [
                            ["state:attr", INITIAL_VALUE, False],
                        ],
                        "state_get": [
                            ["state:attr", FINAL_VALUE, False],
                        ]
                    },
                    "setup": {
                        "create_nodes": [["MyNode", "MyNodeType"]]
                    }
                },
                {
                    "file": "C:/Absolute/Path/To/TestFileForMyNode.usda",
                    "/MyGraph/MyNode": {
                        "outputs": [
                            ["outputs:attr0", OUTPUT_VALUE_0, False],
                            ["outputs:attr1", OUTPUT_VALUE_1, False],
                        ],
                        "state_get": [
                            ["state:attr", FINAL_VALUE, False],
                        }
                    ],
                    "/MyGraph/AnotherNode": {
                        "outputs:attr", ANOTHER_OUTPUT_VALUE, False],
                    }
                }
            ]

        Args:
            all_tests (list[dict[str, Any]]): List of test dictionaries with the test information to be consolidated

        Returns:
            list[dict[str, Any]]: List of tests found, where each test is a dictonary of node_path:attribute:value
        """

        all_tests_data = []
        for test_data in all_tests:

            test_run = {}

            if test_data.file_path:
                # While we are here, check if the test file path (relative to the
                # source .ogn file) actually exists. If it does, copy it into the
                # $BUILD/exts/omni.graph.myext/omni/graph/myext/ogn/tests/data/MyNodeBaseName
                # directory.
                abs_file_path = self.__find_and_copy_test_file(Path(test_data.file_path))
                rel_path = abs_file_path.relative_to(Path(self.interface_directory).absolute().resolve().as_posix())

                # Save the absolute copied file path as a string.
                test_run[TestKeys.FILE] = str(rel_path)

            for node_path, node_test_data in test_data.node_test_data.items():
                if node_path and node_path in TestKeys.FILE:
                    continue

                test_run[node_path] = {}

                # The outputs who decide on being on the GPU at runtime have to be marked as such in the test data.
                # That way the test knows where to look for the results.
                gpu_outputs = node_test_data.gpu_outputs

                # Do all inputs first, for clarity
                if node_test_data.input_values:
                    self.__generate_user_input_test_data(test_run, node_path, node_test_data)
                # ...then all outputs
                if node_test_data.expected_outputs:
                    self.__generate_user_output_test_data(test_run, node_path, node_test_data, gpu_outputs)
                # ...then all state initial values
                if node_test_data.state_initial_values:
                    self.__generate_user_initial_state_test_data(test_run, node_path, node_test_data)
                # ... all state final values
                if node_test_data.state_final_values:
                    self.__generate_user_final_state_test_data(test_run, node_path, node_test_data)

            # ... and graph setup (where None has a different meaning than the empty list)
            if test_data.graph_setup is not None:
                test_run[TestKeys.SETUP] = test_data.graph_setup

            all_tests_data.append(test_run)

        return all_tests_data

    # ----------------------------------------------------------------------
    def generate_user_test_run(self, has_test_file: bool):
        """Generate the section of the user test that iterates test runs over the test data"""
        node_type_name = self.node_interface.name
        if self.out.indent("for i, test_run in enumerate(self.TEST_DATA):"):
            self.out.write("# Skip test runs that specified a test scene.")
            if has_test_file and self.out.indent(f'if "{TestKeys.FILE}" in test_run:'):
                self.out.write("continue")
                self.out.exdent()
            self.out.write("controller = og.Controller()")
            self.out.write("await _test_clear_scene(self, test_run, reset_stage=False)")
            self.out.write(
                f'test_info = await _test_setup_scene(self, controller, f"/TestGraph{{i}}", "TestNode_{self.safe_name()}",'
                f' "{node_type_name}", test_run, _TestGraphAndNode())'
            )
            self.out.write("await controller.evaluate(test_info.graph)")
            self.out.write(
                "_test_verify_scene(self, controller, test_run, test_info,"
                f' f"{node_type_name} User test case #{{i+1}}")'
            )
            self.out.exdent()

    # ----------------------------------------------------------------------
    def generate_user_vectorized_test_run(self, has_test_file: bool):
        """Generate the section of the user test that iterates test runs over a repeated set of test data"""
        number_of_instances = 16
        node_type_name = self.node_interface.name
        if self.out.indent("for i, test_run in enumerate(self.TEST_DATA):"):
            self.out.write("# Skip test runs that specified a test scene.")
            if has_test_file and self.out.indent(f'if "{TestKeys.FILE}" in test_run:'):
                self.out.write("continue")
                self.out.exdent()
            self.out.write("controller = og.Controller()")
            self.out.write("await _test_clear_scene(self, test_run, reset_stage=False)")
            self.out.write(
                f'test_info = await _test_setup_scene(self, controller, f"/TestGraph{{i}}", "TestNode_{self.safe_name()}",'
                f'"{node_type_name}", test_run, _TestGraphAndNode(), {number_of_instances})'
            )
            self.out.write("await controller.evaluate(test_info.graph)")
            self.out.write(
                f"_test_verify_scene(self, controller, test_run, test_info,"
                f' f"{node_type_name} User test case #{{i+1}}", {number_of_instances})'
            )
            self.out.exdent()

    # ----------------------------------------------------------------------
    def generate_threadsafety_test_run(self, has_test_file: bool):
        """Generate the section of the user test that iterates test runs over the test data,
        specifically to look for threadsafety issues."""
        node_type_name = self.node_interface.name
        self.out.write("import omni.kit")
        self.out.write("# Generate multiple instances of the test setup to run them concurrently")
        self.out.write("instance_setup = dict()")
        if self.out.indent("for n in range(24):"):
            self.out.write('instance_setup[f"/TestGraph_{n}"] = _TestGraphAndNode()')
            self.out.exdent()

        # if there is test file, it may need to be filtered out
        self.out.write("")
        if has_test_file:
            self.out.write("# Reduce the list of test runs to only valid ones for thread tests")
            self.out.write("valid_test_runs=[]")
            if self.out.indent("for test_run in self.TEST_DATA:"):
                if self.out.indent(f'if "{TestKeys.FILE}" in test_run:'):
                    self.out.write("continue")
                    self.out.exdent()
                self.out.write("valid_test_runs.append(test_run)")
                self.out.exdent()
            if self.out.indent("if not valid_test_runs:  # pragma: no cover"):
                self.out.write("return")
                self.out.exdent()
        else:
            self.out.write("valid_test_runs = self.TEST_DATA")

        self.out.write("")
        self.out.write("# Build a map of test graph to setup data")
        self.out.write("test_data_setup = {}")
        self.out.write("idx = 0")
        if self.out.indent("for n in range(24):"):
            self.out.write('test_data_setup[f"/TestGraph_{n}"] = valid_test_runs[idx]')
            self.out.write("idx = (idx + 1) % len(valid_test_runs)")
            self.out.exdent()

        self.out.write("")
        self.out.write("await omni.usd.get_context().new_stage_async()")
        if self.out.indent("for (key, test_info) in instance_setup.copy().items():"):
            self.out.write(
                "instance_setup[key] = await _test_setup_scene(self, og.Controller(allow_exists_prim=True), key,"
                f' "TestNode_{self.safe_name()}", "{node_type_name}", test_data_setup[key], test_info)'
            )
            self.out.exdent()
        self.out.write("self.assertEqual(len(og.get_all_graphs()), 24)")

        self.out.write("")
        self.out.write("# We want to evaluate all graphs concurrently. Kick them all.")
        self.out.write("# Evaluate multiple times to skip 2 serial frames and increase chances for a race condition.")
        if self.out.indent("for _ in range(10):"):
            self.out.write("await omni.kit.app.get_app().next_update_async()")
            self.out.exdent()

        self.out.write("")
        if self.out.indent("for (key, test_info) in instance_setup.items():"):
            self.out.write(
                "_test_verify_scene(self, og.Controller(), test_data_setup[key], test_info, "
                f'f"{node_type_name} User test case instance{{key}}")'
            )
            self.out.exdent()

    # ----------------------------------------------------------------------
    def generate_test_with_scene(self):
        """Generate the section of the user test that runs any specified test scenes"""
        self.out.write("from pathlib import Path")
        if self.out.indent("for i, test_run in enumerate(self.TEST_DATA):"):
            self.out.write("# Skip test runs that do not have a specified test scene.")
            self.out.write("# Otherwise attempt to open the file.")
            if self.out.indent(f'if "{TestKeys.FILE}" not in test_run:'):
                self.out.write("continue")
                self.out.exdent()
            self.out.write(f'test_file_path = Path(__file__).parent / test_run["{TestKeys.FILE}"]')
            self.out.write("(result, error) = await ogts.load_test_file(str(test_file_path))")
            self.out.write('self.assertTrue(result, f"{error} on {test_file_path}")')
            self.out.write("")
            self.out.write("# Run the test scene once.")
            self.out.write("await omni.kit.app.get_app().next_update_async()")
            self.out.write("")
            self.out.write("# Loop through all relevant node data for verification.")
            if self.out.indent("for node_path, _ in test_run.items():"):
                if self.out.indent(f'if node_path == "{TestKeys.FILE}":'):
                    self.out.write("continue")
                    self.out.exdent()
                self.out.write(
                    "_test_verify_scene(self, og.Controller(), test_run, None, "
                    'f"{node_path} User test case #{i+1}", 0, node_path)'
                )
                self.out.exdent()
            self.out.exdent()

    # ----------------------------------------------------------------------
    def _generate_user_tests(self) -> bool:
        """Generate the test method that exercises the tests specified in the .ogn file.
        Returns True if the test was created.
        """
        all_tests = self.node_interface.all_tests()
        # If the user did not specify any tests then do not generate this test function
        if not all_tests:
            return False

        self.out.write("")

        test_data = self.generate_user_test_data(all_tests)

        # While it would be nice to just convert the dictionary as a string directly, the fact that some numeric values
        # like 'inf' and 'nan' do not render in a way that allows assignment means that we have to instead convert it
        # incrementally. The test_data structure is a list of dictionaries where the dictionary entries are node path
        # keys with another dictionary as a value. This nested dictionary has "input", "output", and "state" keys with
        # values equal to a tuple of (AttributeName, AttributeValue, OnGpu)
        # [{'/MyGraph/MyNode': {'inputs': [['inputs:a_double_inf', "float('Inf')", False], ['inputs:a_double_ninf', "float('-Inf')", False]]}}
        has_test_file = False
        t = "    "
        tests_as_str = "[\n"
        for test_definition in test_data:  # noqa: PLR1702
            tests_as_str += f"{t}{t}{{\n"
            for key, value in test_definition.items():
                if key == TestKeys.FILE:
                    has_test_file = True
                    tests_as_str += f"{t}{t}{t}'{key}': R\"{value}\",\n"
                    continue
                if not isinstance(value, dict):
                    raise ValueError(f"{key}'s value is not a dictionary.")

                tests_as_str += f"{t}{t}{t}'{key}': {{\n"
                for attribute_port, attribute_values in value.items():
                    if attribute_port not in [
                        TestKeys.INPUTS,
                        TestKeys.OUTPUTS,
                        TestKeys.STATE_GET,
                        TestKeys.STATE_SET,
                        TestKeys.STATE,
                    ]:
                        tests_as_str += f"{t}{t}{t}{t}'{attribute_port}': {attribute_values},\n"
                        continue
                    tests_as_str += f"{t}{t}{t}{t}'{attribute_port}': [\n"
                    try:
                        for attribute, attribute_value, on_gpu in attribute_values:
                            if isinstance(attribute, str) and TestKeys.FILE in test_definition:
                                if attribute_value is None:
                                    attribute_value = "None"
                                tests_as_str += f"{t}{t}{t}{t}{t}['{attribute}', {attribute_value}, {on_gpu}],\n"
                            else:
                                value_as_str = attribute.python_value_as_str(attribute_value)
                                if value_as_str is None:
                                    value_as_str = "None"
                                tests_as_str += f"{t}{t}{t}{t}{t}['{attribute.name}', {value_as_str}, {on_gpu}],\n"
                    except ValueError as error:
                        raise ValueError(f"Failed test data generation with {attribute_values}") from error
                    tests_as_str += f"{t}{t}{t}{t}],\n"
                tests_as_str += f"{t}{t}{t}}},\n"
            tests_as_str += f"{t}{t}}},\n"
        tests_as_str += f"{t}]"

        self.out.write(f"TEST_DATA = {tests_as_str}")

        self.out.write("")
        self.out.write('test_cap = os.getenv("OGN_GENERATED_TEST_LIMIT")')
        if self.out.indent("if test_cap is not None:  # pragma: no cover"):
            self.out.write("TEST_DATA = TEST_DATA[0: int(test_cap)]")
            self.out.exdent()

        self.out.write("")
        if self.out.indent("async def test_generated(self):"):
            self.generate_user_test_run(has_test_file)
            self.out.exdent()

        self.out.write("")
        if self.out.indent("async def test_vectorized_generated(self):"):
            self.generate_user_vectorized_test_run(has_test_file)
            self.out.exdent()

        if self.node_interface.scheduling_hints is not None:
            self.out.write("")
            if self.out.indent("async def test_thread_safety(self):"):
                self.generate_threadsafety_test_run(has_test_file)
                self.out.exdent()

        # Don't generate tests with external scenes if the user did not
        # specify any external scenes to use in their tests.
        if has_test_file:
            self.out.write("")
            if self.out.indent("async def test_with_scene(self):"):
                self.generate_test_with_scene()
                self.out.exdent()

        return True

    # ----------------------------------------------------------------------
    def _generate_data_access_test(self) -> bool:
        """Generate the test method for loading the generated USD file.
        Returns True if any test was generated.
        """
        check_usd = self.node_interface.can_generate("usd")
        check_python = self.node_interface.can_generate("python")
        # There is not enough information to test data access if there's no Python database and no USD file
        if not check_usd and not check_python:
            return False

        node_type_name = self.node_interface.name
        node_name = f"Template_{self.safe_name()}"

        # The node may have generated a .usda file with default values on it. If so then load it in and confirm
        # that the node exists after load and the inputs have the defaults.
        self.out.write("")
        self.out.write("async def test_data_access(self):")
        if self.out.indent():
            if check_python:
                db_name = f"{self.base_name}Database"
                self.out.write(f"from {self.module}.ogn.{db_name} import {db_name}")
            # If USD testing is turned on then use that as a source of the test node
            if check_usd:
                self.out.write(f'test_file_name = "{self.base_name}Template.usda"')
                # The file is found in the usd/ subdirectory of this script's test directory.
                self.out.write('usd_path = os.path.join(os.path.dirname(__file__), "usd", test_file_name)')
                if self.out.indent("if not os.path.exists(usd_path):  # pragma: no cover"):
                    self.out.write('self.assertTrue(False, f"{usd_path} not found for loading test")')
                    self.out.exdent()
                self.out.write("(result, error) = await ogts.load_test_file(usd_path)")
                self.out.write("self.assertTrue(result, f'{error} on {usd_path}')")
                # This node name is hardcoded into the USD generation
                self.out.write(f'test_node = og.Controller.node("/TestGraph/{node_name}")')
            # otherwise create the node directly
            else:
                self.out.write('(_, (test_node,), _, _) = og.Controller.edit("/TestGraph", {')
                self.out.write(f'    og.Controller.Keys.CREATE_NODES: ("{node_name}", "{node_type_name}")')
                self.out.write("})")

            if check_python:
                self.out.write(f"database = {db_name}(test_node)")
            self.out.write("self.assertTrue(test_node.is_valid())")

            # Checking the version instead of the name allows for node type name aliases
            self.out.write("node_type_name = test_node.get_type_name()")
            version = self.node_interface.version
            self.out.write(f"self.assertEqual(og.GraphRegistry().get_node_type_version(node_type_name), {version})")
            self.out.write("")
            if self.out.indent("def _attr_error(attribute: og.Attribute, usd_test: bool) -> str:  # pragma no cover"):
                self.out.write('test_type = "USD Load" if usd_test else "Database Access"')
                self.out.write('return f"{node_type_name} {test_type} Test - {attribute.get_name()} value error"')
                self.out.exdent()
            self.out.write("")

            # Emit code to read the inputs and compare against the default values
            write_fail_tests = []
            for attribute in list_without_runtime_attributes(self.node_interface.all_attributes()):
                # Optional attributes are not written to the template file
                if not attribute.is_required:
                    continue
                name_to_check = attribute.usd_name()
                self.out.write("")
                self.out.write(f'self.assertTrue(test_node.get_attribute_exists("{name_to_check}"))')

                # Always get the value, so that the code is exercised
                self.out.write(f'attribute = test_node.get_attribute("{name_to_check}")')
                self.out.write("self.assertTrue(attribute.is_valid())")
                # Values aren't available for testing if the memory type is purely CUDA
                if check_python and attribute.memory_type != MemoryTypeValues.CUDA:
                    attribute_accessor = f"{attribute.namespace}.{attribute.python_property_name()}"
                    # If memory type is determined at runtime the property is an accessor, not a value
                    if attribute.memory_type == MemoryTypeValues.ANY and not attribute.cpp_accessor_on_cpu():
                        attribute_accessor += ".cpu"
                    self.out.write(f"db_value = database.{attribute_accessor}")
                    # Set inputs with concrete values equal to themselves to test the setters
                    if self.node_interface.is_batched_attribute(attribute):
                        self.out.write(f"database.{attribute_accessor} = db_value")
                        if attribute.array_depth > 0:
                            write_fail_tests.append(attribute_accessor)

                # Only check input numbers since they should be well-defined as the defaults for all nodes
                if not attribute.is_read_only():
                    continue

                if attribute.default is not None:
                    expected_value = attribute.python_value_as_repr(attribute.default)
                    self.out.write(f"expected_value = {expected_value}")
                    if check_usd:
                        self.out.write("actual_value = og.Controller.get(attribute)")
                        self.out.write("ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))")
                    if check_python and attribute.memory_type != MemoryTypeValues.CUDA:
                        self.out.write("ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))")

            if check_python:
                self.out.write("temp_setting = database.inputs._setting_locked")
                # Get and set a value that's part of the local data, and a brand new one, to cover the overridden
                # __getattr__ and __setattr__ implementations.
                (input_batch, output_batch, state_batch) = self.node_interface.has_batched_attributes()
                if input_batch:
                    self.out.write("database.inputs._testing_sample_value = True")
                if output_batch:
                    self.out.write("database.outputs._testing_sample_value = True")
                if state_batch:
                    self.out.write("database.state._testing_sample_value = True")
                if write_fail_tests:
                    # If there are any values that can fail to set due to being read-only, lock and check that failure
                    self.out.write("database.inputs._setting_locked = True")
                    for attribute_accessor in write_fail_tests:
                        if self.out.indent("with self.assertRaises(og.ReadOnlyError):"):
                            self.out.write(f"database.{attribute_accessor} = []")
                            self.out.exdent()
                self.out.write("database.inputs._setting_locked = temp_setting")
                if input_batch:
                    self.out.write("self.assertTrue(database.inputs._testing_sample_value)")
                if output_batch:
                    self.out.write("self.assertTrue(database.outputs._testing_sample_value)")
                if state_batch:
                    self.out.write("self.assertTrue(database.state._testing_sample_value)")

            self.out.exdent()

        return True

    # ----------------------------------------------------------------------
    def generate_node_interface(self):
        """Generate the test method for the named node"""
        has_tests = self._generate_user_tests()
        has_tests = self._generate_data_access_test() or has_tests
        # If no tests were written then the test class will be empty so add a pass to avoid a syntax error
        if not has_tests:
            self.out.write("pass")
        if self.interface_directory is not None:
            ensure_test_is_imported(self.test_class_name(), Path(self.interface_directory))

    # ----------------------------------------------------------------------
    def pre_interface_generation(self):
        """Create the imports and common test framework used by tests for all nodes"""
        self.out.write("import os")
        self.out.write("import omni.kit.test")
        self.out.write("import omni.graph.core as og")
        self.out.write("import omni.graph.core.tests as ogts")
        self.out.write("from omni.graph.core.tests.omnigraph_test_utils import _TestGraphAndNode")
        self.out.write("from omni.graph.core.tests.omnigraph_test_utils import _test_clear_scene")
        self.out.write("from omni.graph.core.tests.omnigraph_test_utils import _test_setup_scene")
        self.out.write("from omni.graph.core.tests.omnigraph_test_utils import _test_verify_scene")
        self.out.write("")
        self.out.write("")
        self.out.write("class TestOgn(ogts.OmniGraphTestCase):")
        self.out.indent()


# ======================================================================
def generate_tests(configuration: GeneratorConfiguration) -> Optional[str]:
    """Create support files for the tests on the node

    Args:
        configuration: Information defining how and where the test files will be generated

    Returns:
        String containing the generated test script code or None if its generation was not enabled

    Raises:
        NodeGenerationError: When there is a failure in the generation of the tests
    """
    if not configuration.node_interface.can_generate("tests"):
        return None

    logger.info("Generating Node Type Tests")
    generator = NodeTestGenerator(configuration)
    generator.generate_interface()
    return str(generator.out)
