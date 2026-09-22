"""Partition pass example unit tests for OG"""

import carb
import omni.graph.core as og
import omni.graph.core.tests as ogts


# ======================================================================
class SimpleGraphScene:
    def __init__(self):
        self.graph = None
        self.nodes = None


# ======================================================================
def create_scriptnode_graph():
    """Create a scene containing a PushGraph with a specific ScriptNode that is compatible with
    the corresponding partition pass."""

    scene = SimpleGraphScene()
    (scene.graph, scene.nodes, _, _) = og.Controller.edit(
        "/World/PushGraph",
        {og.Controller.Keys.CREATE_NODES: [("ScriptNode", "omni.graph.scriptnode.ScriptNode")]},
    )

    return scene


# ======================================================================
def create_lazy_foreach_graph():
    """Create a simple LazyGraph with a ForEach node to test that dirty_push evaluation
    is still respected after a partition pass is run."""

    scene = SimpleGraphScene()
    (scene.graph, scene.nodes, _, _) = og.Controller.edit(
        {"graph_path": "/World/TestGraph", "evaluator_name": "dirty_push"},
        {
            og.Controller.Keys.CREATE_NODES: [
                ("Val0", "omni.graph.nodes.ConstantInt"),
                ("Val1", "omni.graph.nodes.ConstantInt"),
                ("Val2", "omni.graph.nodes.ConstantInt"),
                ("Array", "omni.graph.nodes.ConstructArray"),
                ("ForEach", "omni.graph.action.ForEach"),
                ("Counter", "omni.graph.action.Counter"),
            ],
            og.Controller.Keys.CREATE_ATTRIBUTES: [
                ("Array.inputs:input1", "int"),
                ("Array.inputs:input2", "int"),
            ],
            og.Controller.Keys.SET_VALUES: [
                ("Val0.inputs:value", 0),
                ("Val1.inputs:value", 1),
                ("Val2.inputs:value", 2),
                ("Array.inputs:arraySize", 3),
            ],
            og.Controller.Keys.CONNECT: [
                ("Val0.inputs:value", "Array.inputs:input0"),
                ("Val1.inputs:value", "Array.inputs:input1"),
                ("Val2.inputs:value", "Array.inputs:input2"),
                ("ForEach.outputs:finished", "Counter.inputs:execIn"),
            ],
        },
    )

    return scene


# ======================================================================
class TestOmniGraphPartitionPasses(ogts.OmniGraphTestCase):
    """OmniGraph Partition Pass Unit Tests"""

    async def test_override_foreachnode_pass(self):
        """Exercise the ForEach Node Pattern Partition Pass"""

        # Wrapper method for loading and initializing the test scene.
        async def setup_and_check(self, enable_pass: bool, expected_result):
            """Wrapper method for convenient test setup and execution"""
            # Set the partition pass setting.
            carb.settings.get_settings().set("/app/omni.graph.examples/enableForEachPass", enable_pass)

            # Load the test scene.
            (result, error) = await ogts.load_test_file("ForEachInPushGraph.usda", use_caller_subdirectory=True)
            self.assertTrue(result, error)

            # Read the scene graph.
            graph = og.get_graph_by_path("/World/DrawLine")
            graph_context = graph.get_default_graph_context()
            variable = graph.find_variable("Points")

            # Check that the necessary conditions are met.
            for i in range(20):
                await og.Controller.evaluate(graph)
                value = variable.get_array(graph_context, False, 0)
                for j in range(3):
                    for k in range(3):
                        self.assertAlmostEqual(
                            value[j][k], expected_result[i % len(expected_result)][j][k], places=4  # noqa: S001
                        )

        # Note that we wrap the driver test code in a try-finally block to ensure
        # that the enableForEachPass setting gets reset to False if an exception
        # occurs (thus ensuring that it won't stick around and potentially pollute
        # downstream tests).
        try:
            # ForEach partition pass disabled. When the partition pass is disabled in this test,
            # only the first point gets computed because the ForEach node detects the execIn activation
            # as being a reset of the state of the loop.
            expected_result_disabled = [
                [[-300, 0, 0], [0, 0, 0], [0, 0, 0]] * 4,
            ]

            await setup_and_check(self, False, expected_result_disabled)

            # ForEach partition pass enabled. When the partition pass is enabled in this test,
            # each of the 3 individual point values get computed and written out to the Points
            # variable in a single graph tick. As a result, the Points variable will not have
            # any zero points, and the array will contain the same values each tick.
            expected_result_enabled = [
                [
                    [-300, 0, 0],
                    [7.75462661, -1.13686838e-13, 1.54487908e2],
                    [2.83183032e2, -3.41060513e-13, -1.50866692e2],
                ],
            ]
            await setup_and_check(self, True, expected_result_enabled)

        finally:
            carb.settings.get_settings().set("/app/omni.graph.examples/enableForEachPass", False)

    async def test_override_scriptnode_pass(self):
        """Exercise the Script Node Partition Pass"""
        scene = create_scriptnode_graph()

        # Add the necessary inputs and outputs to the script node so
        # that the partition pass recognizes it.
        og.Controller.create_attribute(
            scene.nodes[0],
            "inputs:my_input_attribute",
            og.Type(og.BaseDataType.INT, 1, 0, og.AttributeRole.NONE),
            og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT,
        )
        og.Controller.create_attribute(
            scene.nodes[0],
            "outputs:my_output_attribute",
            og.Type(og.BaseDataType.INT, 1, 0, og.AttributeRole.NONE),
            og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT,
        )

        # Add an internal state variable to the script node that gets ticked
        # for every evaluation. We'll use this counter to determine whether the
        # node computed or simply passed its cached output value downstream
        # (without a nodal compute being invoked).
        og.Controller.create_attribute(
            scene.nodes[0],
            "state:my_internal_state",
            og.Type(og.BaseDataType.INT, 1, 0, og.AttributeRole.NONE),
            og.AttributePortType.ATTRIBUTE_PORT_TYPE_STATE,
        )

        # Set the script node's internal script to compute the nth Fibonacci
        # Fibonacci in an iterative fashion (where n is the given integer via
        # "inputs:my_input_attribute").
        script_string = "def fib(count):\n"
        script_string += "    if count == 0:\n"
        script_string += "        return 0\n"
        script_string += "    if count == 1:\n"
        script_string += "        return 1\n"
        script_string += "\n"
        script_string += "    num1 = 0\n"
        script_string += "    num2 = 1\n"
        script_string += "\n"
        script_string += "    for i in range(count):\n"
        script_string += "        numth = num1 + num2\n"
        script_string += "        num1 = num2\n"
        script_string += "        num2 = numth\n"
        script_string += "    return num1\n"
        script_string += "\n"
        script_string += "def compute(db):\n"
        script_string += "    count = db.inputs.my_input_attribute\n"
        script_string += "    db.outputs.my_output_attribute = fib(count)\n"
        script_string += "    if db.state.my_internal_state < 10000:\n"
        script_string += "        db.state.my_internal_state += 1\n"
        script_string += "    else:\n"
        script_string += "        db.state.my_internal_state = 0\n"

        scene.nodes[0].get_attribute("inputs:script").set(script_string)

        my_input_attr = scene.nodes[0].get_attribute("inputs:my_input_attribute")
        my_internal_state = scene.nodes[0].get_attribute("state:my_internal_state")
        my_output_attr = scene.nodes[0].get_attribute("outputs:my_output_attribute")

        # Set the input and try computing multiple times. Only the first
        # call to evaluate the graph should have triggered a script node
        # evaluation (per the partition pass that's being tested here).
        # Note that we *temporarily* enable the script node partition
        # during this test *only* in order to not potentially impact any
        # other downstream tests.
        with og.Settings.temporary("/app/omni.graph.examples/enableScriptNodePass", True):
            my_input_attr.set(10)
            for _ in range(4):
                await og.Controller.evaluate(scene.graph)
                self.assertEqual(my_output_attr.get(), 55)
                self.assertEqual(my_internal_state.get(), 1)
            my_input_attr.set(15)
            for _ in range(4):
                await og.Controller.evaluate(scene.graph)
                self.assertEqual(my_output_attr.get(), 610)
                self.assertEqual(my_internal_state.get(), 2)
            my_input_attr.set(10)
            for _ in range(4):
                await og.Controller.evaluate(scene.graph)
                self.assertEqual(my_output_attr.get(), 55)
                self.assertEqual(my_internal_state.get(), 3)

    async def test_lazy_foreach_graph_with_partition_pass(self):
        """Check that dirty_push evaluation graphs work correctly after
        partition passes are run on said graphs (OM-93668)"""
        scene = create_lazy_foreach_graph()

        try:
            # Enable the ForEach partition pass.
            carb.settings.get_settings().set("/app/omni.graph.examples/enableForEachPass", True)

            # Get some necessary node attributes for the test.
            const_int_node_0 = scene.nodes[0]
            in_value_attr = const_int_node_0.get_attribute("inputs:value")
            make_array_node = scene.nodes[3]
            in_inputsa_attr = make_array_node.get_attribute("inputs:input0")
            counter_node = scene.nodes[5]
            out_count_attr = counter_node.get_attribute("outputs:count")

            # If nothing changes in the graph, no nodes should be evaluated after
            # the initial computation (i.e. immediately after creating the graph)
            # => the counter node's output value should be one. Prior to OM-93668
            # being addressed the counter node would instead get ticked/incremented
            # each compute., so out_count_attr.get() would equal 3.
            await og.Controller.evaluate(scene.graph)
            await og.Controller.evaluate(scene.graph)
            await og.Controller.evaluate(scene.graph)
            self.assertEqual(out_count_attr.get(), 1)

            # The counter node should only be triggered to evaluate when downstream
            # changes are made. Prior to OM-93668 the counter node would instead get
            # ticked/incremented each compute, so out_count_attr.get() would equal 6.
            og.Controller.disconnect(in_value_attr, in_inputsa_attr)
            await og.Controller.evaluate(scene.graph)
            await og.Controller.evaluate(scene.graph)
            await og.Controller.evaluate(scene.graph)
            self.assertEqual(out_count_attr.get(), 2)

        finally:
            # Disable the ForEach partition pass.
            carb.settings.get_settings().set("/app/omni.graph.examples/enableForEachPass", False)
