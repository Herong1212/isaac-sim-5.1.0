"""Tests for the runtime AutoNode functionality"""

import logging
import sys

import carb
import numpy as np
import omni.graph.core as og
import omni.graph.core._impl.autonode_examples as examples
import omni.graph.core.tests as ogts
import omni.graph.core.types as ot

# Test-specific imports that aren't generally used. Remove the underscore to keep lint happy.
from omni.graph.core._impl.autonode import _generate_node_type as generate_node_type
from omni.graph.core._impl.unstable.attribute_spec import AttributeSpec
from omni.graph.core._impl.unstable.runtime_node_types import RUNTIME_MODULE_NAME

# This odd looking thing ensures that the AutoNode definition does not inherit the omni.graph.core namespace since
# it knows the extension belongs to the template. The test relies on it being unattached to any extension.
_ext_path = carb.tokens.get_tokens_interface().resolve("${omni.graph}") + "/docs"
sys.path.append(_ext_path)
from autonode_helper import run_test  # noqa: E402

sys.path.pop()


# ==============================================================================================================
class TestAutoNodeRuntime(ogts.OmniGraphTestCase):
    # --------------------------------------------------------------------------------------------------------------
    async def test_invalid_runtime_definitions(self):
        """Test that the _AutoNodePopulator construction correctly catches poorly configured definitions"""

        def test_function() -> None:
            """This is test_function"""

        class CallableWithoutName:
            def __call__(self):
                pass

        def test_with_execute(execute: ot.execution):
            pass

        # Arguments to the populator to be tested:
        #   compute_function: callable,
        #   unique_name: str = None,
        #   ui_name: str = None,
        #   add_execution_pins: bool = False,
        #   metadata: dict[str, str] = None,

        error_test_parameters = [
            (3, {}),
            (CallableWithoutName(), {}),
            (test_with_execute, {"add_execution_pins": True}),
            (test_function, {"unique_name": ["Not a name"]}),
            (test_function, {"ui_name": 42}),
            (test_function, {"add_execution_pins": "Not a boolean"}),
            (test_function, {"metadata": 42}),
            (test_function, {"metadata": {42: "key not a string"}}),
            (test_function, {"metadata": [42, 42]}),
        ]
        for func, kwargs in error_test_parameters:
            with self.assertRaises(og.NodeTypeConstructionError, msg=f"Testing {func=} {kwargs=}"):
                generate_node_type(func, **kwargs)

    # --------------------------------------------------------------------------------------------------------------
    async def test_generate_node_type(self):
        """Test the functionality of the _generate_node_type function without actually creating any node types"""

        def test_function() -> None:
            """This is test_function"""

        class CallableWithName:
            """This is CallableWithName"""

            def __init__(self):
                self.__name__ = "callable_with_name"

            def __call__(self):
                pass

        named_callable = CallableWithName()
        default_names = {test_function: "omni.graph.test_function", named_callable: "omni.graph.callable_with_name"}
        default_ui_names = {test_function: "Test Function (AutoNode)", named_callable: "Callable With Name (AutoNode)"}
        expected_descriptions = {test_function: "This is test_function", named_callable: "This is CallableWithName"}

        # Set of valid parameters that can be passed to the populator. For simplicity the kwargs are flattened into
        # an ordered list of (callable, unique_name, ui_name, add_execution_pins, metadata). Every parameter uses
        # "None" to mean "use the default".
        test_parameters = [
            (test_function, None, None, None, {}),
            (named_callable, None, None, None, {}),
            (test_function, "HanShotFirst", None, None, {}),
            (test_function, None, "GreedoShotFirst", None, {}),
            (test_function, None, None, True, {}),
            (test_function, None, None, None, {"Han": "pilot"}),
            (test_function, None, None, None, {"Pilots": ["Han", "Poe"], "Rebels": ["Han", "Luke", "Leia"]}),
            (test_function, "Han", "Leia", True, {"Emperor": "Palpatine"}),
        ]

        for compute, unique_name, ui_name, add_execution_pins, metadata in test_parameters:
            metadata[RUNTIME_MODULE_NAME] = True
            results = generate_node_type(
                compute,
                module_name=None,
                unique_name=unique_name,
                ui_name=ui_name,
                add_execution_pins=add_execution_pins,
                metadata=metadata,
            )

        expected_unique_name = default_names[compute] if unique_name is None else unique_name
        expected_ui_name = default_ui_names[compute] if ui_name is None else ui_name
        expected_description = expected_descriptions[compute]
        expected_metadata = {key: str(value) for key, value in (metadata or {}).items() if key != RUNTIME_MODULE_NAME}
        if add_execution_pins:
            expected_inputs = [
                AttributeSpec(name="execute", port_type=og.AttributePortType.INPUT, type_name="execution")
            ]
            expected_outputs = [
                AttributeSpec(name="execute", port_type=og.AttributePortType.OUTPUT, type_name="execution")
            ]
        else:
            expected_inputs = []
            expected_outputs = []
        expected_methods = {"compute": compute}

        self.assertEqual(expected_unique_name, results["unique_name"])
        self.assertEqual(compute.__name__, results["name"])
        self.assertEqual(expected_ui_name, results["ui_name"])
        self.assertEqual("omni.graph.core.tests.test_autonode", results["module_name"])
        self.assertEqual("omni.graph", results["extension"])
        self.assertEqual(expected_description, results["description"])
        self.assertEqual(expected_metadata, results["metadata"])
        self.assertCountEqual(expected_inputs, results["inputs"])
        self.assertCountEqual(expected_outputs, results["outputs"])
        self.assertCountEqual(expected_methods, results["method_overrides"])

    # --------------------------------------------------------------------------------------------------------------
    async def test_generate_node_type_with_inputs(self):
        """Test the functionality of the _generate_node_type function for parsing input attributes"""

        a_attr_structure = AttributeSpec(name="a", port_type=og.AttributePortType.INPUT, type_name="int")
        b_attr_structure = AttributeSpec(name="b", port_type=og.AttributePortType.INPUT, type_name="float")

        def test_function(a: ot.int, b: ot.float) -> None:
            """This is test_function"""

        default_metadata = {RUNTIME_MODULE_NAME: True}
        results = generate_node_type(test_function, metadata=default_metadata)

        self.assertEqual("test_function", results["name"])
        self.assertEqual("omni.graph.test_function", results["unique_name"])
        self.assertEqual("Test Function (AutoNode)", results["ui_name"])
        self.assertEqual("This is test_function", results["description"])
        self.assertCountEqual([a_attr_structure, b_attr_structure], results["inputs"])
        self.assertEqual([], results["outputs"])

        # Make sure that explicit inputs and outputs interleave with implicit execution pins
        def test_function2(a: ot.int, b: ot.float) -> ot.float:
            """This is test_function2"""

        results = generate_node_type(test_function2, add_execution_pins=True, metadata=default_metadata)

        in_exec = AttributeSpec(name="execute", port_type=og.AttributePortType.INPUT, type_name="execution")
        out_exec = AttributeSpec(name="execute", port_type=og.AttributePortType.OUTPUT, type_name="execution")
        out_attr_structure = AttributeSpec(name="out_0", port_type=og.AttributePortType.OUTPUT, type_name="float")
        self.assertEqual("test_function2", results["name"])
        self.assertEqual("omni.graph.test_function2", results["unique_name"])
        self.assertEqual("Test Function2 (AutoNode)", results["ui_name"])
        self.assertEqual("This is test_function2", results["description"])
        self.assertCountEqual([a_attr_structure, b_attr_structure, in_exec], results["inputs"])
        self.assertCountEqual([out_attr_structure, out_exec], results["outputs"])

    # --------------------------------------------------------------------------------------------------------------
    async def test_autonode_examples(self):
        """Test that the examples created to exercise all AutoNode types, also used for documentation, function
        correctly. The return value from each of the functions is a 2-tuple of node type name and test data as a
        2-tuple of input values and output values as dictionaries by name. For example the boolean test node type
        will return ("omni.graph.autonode_bool", ({"first_value": True, "second_value": True}, {"out_0": True})) which
        is interpreted as the following test sequence:
            - Instantiate a node of type "omni.graph.autonode_bool"
            - Set the node's input attribute "inputs:first_value" to the value True
            - Set the node's input attribute "inputs:second_value" to the value True
            - Run the graph evaluation
            - Read the value of the node's output attribute "outputs:out_0" and confirm that it equals True
        If the tests returned are "None" that indicates the tests should be done manually so the node types are
        left to be tested manually.
        """
        logger = logging.getLogger("AutoNode")
        # The way the graph is constructed it will reuse the same graph for each test, speeding it up a bit
        controller = og.Controller()
        (graph, _, _, _) = controller.edit("/TestGraph", {})
        for function_name in [name for name in dir(examples) if name.startswith("construct_")]:
            logger.info("Running automatic test from the function '%s'", function_name)
            (node_type_name, test_data) = getattr(examples, function_name)()
            logger.debug("... current registration list is %s", og.get_registered_nodes())
            logger.debug("... test data is %s", test_data)
            self.assertTrue(node_type_name in og.get_registered_nodes())

            # When test_data is None the tests must be done manually. Assert here to verify that everything is flagged.
            if test_data is None:
                logger.debug("... must be tested manually")
                self.assertTrue(function_name in examples.TEST_MANUALLY, f"No manual test for {function_name}")
                continue

            # Empty test data means that no testing is required for whatever reason (e.g. no attributes exist)
            if not test_data:
                logger.debug("... no testing required")
                continue

            # Allow for just one or a list of tests
            test_data = test_data if isinstance(test_data, list) else [test_data]
            node = controller.create_node(("TestNode", graph), node_type_name)
            for inputs, outputs in test_data:
                logger.debug("... setting inputs %s", inputs)
                for input_name, input_value in inputs.items():
                    controller.set(controller.attribute(f"inputs:{input_name}", node), input_value)
                await controller.evaluate()
                logger.debug("... confirming outputs %s", outputs)
                for output_name, expected_value in outputs.items():
                    actual_value = controller.get(controller.attribute(f"outputs:{output_name}", node))
                    logger.debug("... actual output was %s", actual_value)
                    if isinstance(expected_value, np.ndarray):
                        if expected_value.dtype in [np.float16, np.float32, np.float64]:
                            equal = np.allclose(np.array(actual_value).flatten(), np.array(expected_value).flatten())
                        else:
                            equal = np.array(actual_value).flatten() == np.array(expected_value).flatten()
                        if isinstance(equal, np.ndarray):
                            equal = equal.all()
                    else:
                        equal = actual_value == expected_value
                    self.assertTrue(
                        equal,
                        f"Output value from TestNode.outputs:{output_name} of type {node_type_name}"
                        f" was {actual_value} instead of {expected_value}",
                    )
            # Get rid of the node so that evaluates do not get progressively slower as we walk through the list
            controller.delete_node(node)
            og.deregister_node_type(node_type_name)

    # --------------------------------------------------------------------------------------------------------------
    async def _test_construct_autonode_execution(self) -> bool:
        """Test the construct_autonode_execution AutoNode definition with a manually constructed graph.
        Returns True if the test succeeded.
        """

        # As the usual node type definitions are in omni.graph.action_nodes use AutoNode to construct one here for
        # testing. It will add a little bit more to the test coverage.
        @og.create_node_type
        def triggered_add(trigger: ot.execution, first_value: ot.int, second_value: ot.int) -> ot.int:
            """Set the output to the sum of the two input integer values when the trigger is enabled"""
            if trigger == og.ExecutionAttributeState.ENABLED:
                return first_value + second_value
            return 0

        result_node_type_name = "omni.graph.triggered_add"

        controller = og.Controller()
        (node_type_name, _) = examples.construct_autonode_execution()
        (_, (test_node, result_node), _, _) = controller.edit(
            "/TestGraph",
            {
                controller.Keys.CREATE_NODES: [
                    ("TestNode", node_type_name),
                    ("ResultNode", result_node_type_name),
                ],
                controller.Keys.CONNECT: ("TestNode.outputs:out_0", "ResultNode.inputs:trigger"),
            },
        )
        await controller.evaluate()
        output_attr = controller.attribute("outputs:out_0", result_node)
        first_input_attr = controller.attribute("inputs:first_value", result_node)
        second_input_attr = controller.attribute("inputs:second_value", result_node)
        trigger_1_attr = controller.attribute("inputs:first_trigger", test_node)
        trigger_2_attr = controller.attribute("inputs:second_trigger", test_node)
        self.assertEqual(0, og.Controller.get(output_attr))

        first_input_attr.set(5)
        second_input_attr.set(10)
        await controller.evaluate()
        # Nothing should evaluate until the input execution pins are enabled
        self.assertEqual(0, og.Controller.get(output_attr))

        trigger_1_attr.set(og.ExecutionAttributeState.ENABLED)
        await controller.evaluate()
        # Only one is enabled, no evaluation yet
        self.assertEqual(0, og.Controller.get(output_attr))

        trigger_2_attr.set(og.ExecutionAttributeState.ENABLED)
        await controller.evaluate()
        self.assertEqual(15, og.Controller.get(output_attr))

        # Second evaluation sequence. Cannot explicitly test the Action Graph sequence here where the input pins
        # are automatically disabled since that graph type is not available in the core, so just check that the
        # values continue to be computed after being changed.
        first_input_attr.set(42)
        second_input_attr.set(420)
        await controller.evaluate()
        self.assertEqual(462, og.Controller.get(output_attr))

        controller.delete_node([test_node, result_node])
        og.deregister_node_type(node_type_name)
        og.deregister_node_type(result_node_type_name)

        return True

    # --------------------------------------------------------------------------------------------------------------
    async def _test_construct_autonode_bundle(self) -> bool:
        """Test the construct_autonode_bundle AutoNode definition with a manually constructed graph.
        As the node type compute is set up to just add attributes to a bundle the test will be to chain
        three nodes together where the attribute addition numbers are 0, 1, and 2. The 0 ensures the first bundle
        starts empty and the 1 and 2 add a total of 3 attributes to the bundle. Then the specialty node created
        for the test is used to report the results in a verifiable way since currently bundle data cannot be
        read directly from an attribute.
        Returns True if the test succeeded.
        """

        @og.create_node_type
        def bundle_member_count(bundle: ot.bundle) -> ot.int:
            """Set the output to the number of attributes in the bundle"""
            return bundle.size

        report_node_type_name = "omni.graph.bundle_member_count"

        controller = og.Controller()
        (node_type_name, _) = examples.construct_autonode_bundle()
        (_, (test_node_1, test_node_2, test_node_3, report_node), _, _) = controller.edit(
            "/TestGraph",
            {
                controller.Keys.CREATE_NODES: [
                    ("TestNode1", node_type_name),
                    ("TestNode2", node_type_name),
                    ("TestNode3", node_type_name),
                    ("ReportNode", report_node_type_name),
                ],
                controller.Keys.CONNECT: [
                    ("TestNode1.outputs_out_0", "TestNode2.inputs:bundle"),
                    ("TestNode2.outputs_out_0", "TestNode3.inputs:bundle"),
                    ("TestNode3.outputs_out_0", "ReportNode.inputs:bundle"),
                ],
                controller.Keys.SET_VALUES: [
                    ("TestNode1.inputs:added", 0),
                    ("TestNode2.inputs:added", 1),
                    ("TestNode3.inputs:added", 2),
                ],
            },
        )
        await controller.evaluate()
        result = og.Controller.get(controller.attribute("outputs:out_0", report_node))
        self.assertEqual(result, 3, "Correctly built a bundle along a chain with all 3 new attributes")

        controller.delete_node([test_node_1, test_node_2, test_node_3, report_node])
        og.deregister_node_type(node_type_name)
        og.deregister_node_type(report_node_type_name)

        return True

    # --------------------------------------------------------------------------------------------------------------
    async def _test_construct_autonode_output_bundles(self) -> bool:
        """Test the construct_autonode_output_bundles AutoNode definition with a manually constructed graph.
        As the node type compute is set up to just create a bundle from scratch it can be created by itself. However,
        a specialty node created for the test is needed to report the results in a verifiable way since currently
        bundle data cannot be read directly from an attribute.
        Returns True if the test succeeded.
        """

        @og.create_node_type
        def bundle_member_name(bundle: ot.bundle) -> ot.string:
            """Set the output to the name of the first attribute found in the bundle"""
            return bundle.attributes[0].name

        report_node_type_name = "omni.graph.bundle_member_name"

        controller = og.Controller()
        (node_type_name, _) = examples.construct_autonode_output_bundles()
        (_, (test_node, report_node), _, _) = controller.edit(
            "/TestGraph",
            {
                controller.Keys.CREATE_NODES: [
                    ("TestNode", node_type_name),
                    ("ReportNode", report_node_type_name),
                ],
                controller.Keys.CONNECT: [
                    ("TestNode.outputs_out_0", "ReportNode.inputs:bundle"),
                ],
            },
        )
        await controller.evaluate()
        result = og.Controller.get(controller.attribute("outputs:out_0", report_node))
        self.assertEqual(result, "fizzbin", "Correctly built a bundle from scratch with one attribute")

        controller.delete_node([test_node, report_node])
        og.deregister_node_type(node_type_name)
        og.deregister_node_type(report_node_type_name)

        return True

    # --------------------------------------------------------------------------------------------------------------
    async def test_autonode_manual_examples(self):
        """Test that the examples created to exercise all AutoNode types as above that use"""
        manual_tests_done = {function_name: False for function_name in examples.TEST_MANUALLY}

        for function_name in manual_tests_done:
            test_function = getattr(self, f"_test_{function_name}", None)
            if test_function is not None:
                manual_tests_done[function_name] = await test_function()

        # Now that the tests are done confirm that we have not forgotten any
        self.assertTrue(
            all(complete for complete in manual_tests_done.values()),
            f"No manual tests for {[test_name for test_name, done in manual_tests_done.items() if not done]}",
        )

    # --------------------------------------------------------------------------------------------------------------
    async def test_autonode_raise_exception(self):
        """Test that when an AutoNode function raises an exception it is correctly reported and caught"""
        error_message = "Indeterminate result from dividing 0 by 0"

        @og.create_node_type
        def raise_exception() -> None:
            raise og.OmniGraphError(error_message)

        controller = og.Controller()
        (_, (test_node,), _, _) = controller.edit(
            "/TestGraph",
            {
                controller.Keys.CREATE_NODES: [
                    ("ReportNode", "omni.graph.raise_exception"),
                ],
            },
        )
        with ogts.ExpectedError():
            await controller.evaluate()

        messages = test_node.get_compute_messages(og.Severity.ERROR)
        self.assertTrue(any(message.find(error_message) >= 0 for message in messages))

    # --------------------------------------------------------------------------------------------------------------
    async def test_helper(self):
        """Run the test imported from the helper file, which is used to make sure doc code samples are functional"""
        self.assertTrue(run_test())
