"""Tests for nodes with dynamic attributes"""  # noqa: PLC0302

import unittest
from typing import Any, Dict

import omni.graph.core as og
import omni.graph.core.tests as ogts
import omni.usd
import OmniGraphSchemaTools
from omni.graph.core.tests.omnigraph_test_utils import _test_clear_scene, _test_verify_scene, _TestGraphAndNode

DYN_ATTRIBUTE_FORMAT = "inputs:"


# ======================================================================
class TestDynamicNodes(ogts.OmniGraphTestCase):
    """Unit tests for nodes with dynamic attributes"""

    PERSISTENT_SETTINGS_PREFIX = "/persistent"
    TEST_GRAPH_PATH = "/World/TestGraph"

    # This method is copied from the module omnigraph_test_utils and is modified to support the "dynamicInputs" keyword
    # in test data. Once the dynamic inputs can directly be tested in .ogn files, this implementation should be replaced
    # with the standard implementation.
    async def _test_setup_scene(
        tc: unittest.TestCase,  # noqa: N805
        controller: og.Controller,
        test_graph_name: str,
        test_node_name: str,
        test_node_type: str,
        test_run: Dict[str, Any],
        last_test_info: _TestGraphAndNode,
        instance_count=0,
    ) -> _TestGraphAndNode:
        """Setup the scene based on given test run dictionary

        Args:
            tc: Unit test case executing this method. Used to raise errors
            controller: Controller object to use when constructing the scene (e.g. may have undo support disabled)
            test_graph_name: Graph name to use when constructing the scene
            test_node_name: Node name to use when constructing the scene without "setup" explicitly provided in test_run
            test_node_type: Node type to use when constructing the scene without "setup" explicitly provided in test_run
            test_run: Dictionary consisting of a dictionary of dictionaries.
                The key is a path to the node in the test scene (empty if no test scene is
                specified), and the value contains up to the following four sub-lists and
                dictionary:
                - values for input attributes, set before the test starts
                - values for output attributes, checked after the test finishes
                - initial values for state attributes, set before the test starts
                - final values for state attributes, checked after the test finishes
                - setup to be used for populating the scene via controller
                For complete implementation see generate_user_test_data.
            last_test_info: When executing multiple tests cases for the same node, this represents graph and node used in previous run
            instance_count: number of instances to create associated to this graph, in order to test vectorized compute

        Returns:
            Graph and node to use in current execution of the test
        """
        test_info = last_test_info

        setup = test_run.get("setup", None)
        if setup:
            (test_info.graph, test_nodes, _, _) = controller.edit(test_graph_name, setup)
            tc.assertTrue(test_nodes)
            test_info.node = test_nodes[0]
        elif setup is None:
            test_info.graph = controller.create_graph(test_graph_name)
            test_info.graph.set_auto_instancing_allowed(False)
            test_info.node = controller.create_node((test_node_name, test_info.graph), test_node_type)
        else:
            tc.assertTrue(
                test_info.graph is not None and test_info.graph.is_valid(),
                "Test is misconfigured - empty setup cannot be in the first test",
            )
        tc.assertTrue(test_info.graph is not None and test_info.graph.is_valid(), "Test graph invalid")
        tc.assertTrue(test_info.node is not None and test_info.node.is_valid(), "Test node invalid")
        await controller.evaluate(test_info.graph)

        inputs = test_run[""].get("inputs", [])
        state_set = test_run[""].get("state_set", [])

        values_to_set = inputs + state_set
        if values_to_set:
            for attribute_name, attribute_value, _ in values_to_set:
                controller.set(attribute=(attribute_name, test_info.node), value=attribute_value)

        dynamic_inputs = test_run[""].get("dynamicInputs", [])
        if dynamic_inputs:
            for attribute_name, attribute_value, _ in dynamic_inputs:
                controller.create_attribute(
                    test_info.node,
                    attribute_name,
                    attribute_value["type"],
                    og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT,
                    attribute_value["value"],
                )

        # create some instance prims, and apply the graph on it
        if instance_count != 0:
            stage = omni.usd.get_context().get_stage()
            for i in range(instance_count):
                prim_name = f"/World/Test_Instance_Prim_{i}"
                stage.DefinePrim(prim_name)
                OmniGraphSchemaTools.applyOmniGraphAPI(stage, prim_name, test_graph_name)

        return test_info

    async def test_node_is_updated_when_dynamic_attributes_are_added_or_removed(self):
        """Tests that the node database is notified and updated when dynamic attributes are added or removed"""
        # Arrange: create an Add node and add two dynamic attributes on it
        controller = og.Controller()
        keys = og.Controller.Keys

        (
            graph,
            (add_node, _, _),
            _,
            _,
        ) = controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("Add", "omni.graph.nodes.Add"),
                    ("Const1", "omni.graph.nodes.ConstantFloat"),
                    ("Const2", "omni.graph.nodes.ConstantFloat"),
                ],
                keys.CONNECT: [
                    ("Const1.inputs:value", "Add.inputs:a"),
                    ("Const2.inputs:value", "Add.inputs:b"),
                ],
                keys.SET_VALUES: [
                    ("Const1.inputs:value", 2.0),
                    ("Const2.inputs:value", 3.0),
                ],
            },
        )

        # Evaluate the graph once to ensure the node has a Database created
        await controller.evaluate(graph)

        controller.create_attribute(
            add_node,
            "inputs:input0",
            og.Type(og.BaseDataType.FLOAT),
            og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT,
            5,  # the default value will be applied in the computation
        )
        controller.create_attribute(
            add_node,
            "inputs:input1",
            og.Type(og.BaseDataType.FLOAT),
            og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT,
            7,  # the default value will be applied in the computation
        )
        # Act: evaluate the graph
        await controller.evaluate(graph)

        # Assert: read the sum output and test that the dynamic attributes were included in the computation
        sum_attr = controller.attribute("outputs:sum", add_node)
        self.assertEqual(17, controller.get(sum_attr), "The dynamic attributes were not included in the computation")

        # Arrange 2: remove one of the dynamic inputs
        input0_attr = controller.attribute("inputs:input0", add_node)
        controller.remove_attribute(input0_attr)

        # Act 2: evaluate the graph
        await controller.evaluate(graph)

        # Assert 2: assert that only one of the dynamic inputs were used in the computation
        sum_attr = controller.attribute("outputs:sum", add_node)
        self.assertEqual(
            12, og.Controller.get(sum_attr), "The node was not notified of the removal of a dynamic attribute"
        )

    TEST_DATA_ADD = [
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "float[2]", "value": [1.0, 2.0]}, False],
                    ["inputs:b", {"type": "float[2]", "value": [0.5, 1.0]}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "float[2]", "value": [3.0, 4.0]}, False],
                    ["inputs:d", {"type": "float[2]", "value": [0.1, 0.1]}, False],
                ],
                "outputs": [
                    ["outputs:sum", {"type": "float[2]", "value": [4.6, 7.1]}, False],
                ],
            },
        },
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "int64", "value": 10}, False],
                    ["inputs:b", {"type": "int64", "value": 6}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "int64", "value": 4}, False],
                    ["inputs:d", {"type": "int64", "value": 20}, False],
                ],
                "outputs": [
                    ["outputs:sum", {"type": "int64", "value": 40}, False],
                ],
            },
        },
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "double[2][]", "value": [[10, 5], [1, 1]]}, False],
                    ["inputs:b", {"type": "double[2]", "value": [5, 5]}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "double[2]", "value": [5, 5]}, False],
                    ["inputs:d", {"type": "double[2][]", "value": [[10, 5], [1, 1]]}, False],
                ],
                "outputs": [
                    ["outputs:sum", {"type": "double[2][]", "value": [[30, 20], [12, 12]]}, False],
                ],
            },
        },
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "double[2][]", "value": [[10, 5], [1, 1]]}, False],
                    ["inputs:b", {"type": "double", "value": 5}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "double[2]", "value": [5, 5]}, False],
                    ["inputs:d", {"type": "double[2][]", "value": [[10, 5], [1, 1]]}, False],
                ],
                "outputs": [
                    ["outputs:sum", {"type": "double[2][]", "value": [[30, 20], [12, 12]]}, False],
                ],
            },
        },
    ]

    async def test_add(self):
        """Validates the node OgnAdd with dynamic inputs"""
        controller = og.Controller()
        for i, test_run in enumerate(self.TEST_DATA_ADD):
            await _test_clear_scene(self, test_run, reset_stage=False)
            test_info = await self._test_setup_scene(
                controller,
                f"/TestGraph{i}",
                "TestNode_omni_graph_nodes_Add",
                "omni.graph.nodes.Add",
                test_run,
                _TestGraphAndNode(),
            )
            await controller.evaluate(test_info.graph)
            _test_verify_scene(self, controller, test_run, test_info, f"omni.graph.nodes.Add User test case #{i+1}")

    async def test_add_vectorized(self):
        """Validates the node OgnAdd with dynamic inputs - vectorized computation"""
        controller = og.Controller()
        for i, test_run in enumerate(self.TEST_DATA_ADD):
            await _test_clear_scene(self, test_run, reset_stage=False)
            test_info = await self._test_setup_scene(
                controller,
                f"/TestGraph{i}",
                "TestNode_omni_graph_nodes_Add",
                "omni.graph.nodes.Add",
                test_run,
                _TestGraphAndNode(),
                16,
            )
            await controller.evaluate(test_info.graph)
            _test_verify_scene(self, controller, test_run, test_info, f"omni.graph.nodes.Add User test case #{i+1}", 16)

    TEST_DATA_SUBTRACT = [
        {  # 1
            "": {
                "inputs": [
                    ["inputs:a", {"type": "double", "value": 10.0}, False],
                    ["inputs:b", {"type": "double", "value": 0.5}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "double", "value": 1.0}, False],
                    ["inputs:d", {"type": "double", "value": 0.5}, False],
                ],
                "outputs": [
                    ["outputs:difference", {"type": "double", "value": 8}, False],
                ],
            },
        },
        {  # 2
            "": {
                "inputs": [
                    ["inputs:a", {"type": "float", "value": 10.0}, False],
                    ["inputs:b", {"type": "float", "value": 0.5}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "float", "value": 1.0}, False],
                    ["inputs:d", {"type": "float", "value": 0.5}, False],
                ],
                "outputs": [
                    ["outputs:difference", {"type": "float", "value": 8}, False],
                ],
            },
        },
        {  # 3
            "": {
                "inputs": [
                    ["inputs:a", {"type": "half", "value": 10.0}, False],
                    ["inputs:b", {"type": "half", "value": 0.5}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "half", "value": 1.0}, False],
                    ["inputs:d", {"type": "half", "value": 0.5}, False],
                ],
                "outputs": [
                    ["outputs:difference", {"type": "half", "value": 8.0}, False],
                ],
            },
        },
        {  # 4
            "": {
                "inputs": [
                    ["inputs:a", {"type": "int", "value": 10}, False],
                    ["inputs:b", {"type": "int", "value": 6}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "int", "value": 1}, False],
                    ["inputs:d", {"type": "int", "value": 2}, False],
                ],
                "outputs": [
                    ["outputs:difference", {"type": "int", "value": 1}, False],
                ],
            },
        },
        {  # 5
            "": {
                "inputs": [
                    ["inputs:a", {"type": "int64", "value": 10}, False],
                    ["inputs:b", {"type": "int64", "value": 6}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "int64", "value": 1}, False],
                    ["inputs:d", {"type": "int64", "value": 2}, False],
                ],
                "outputs": [
                    ["outputs:difference", {"type": "int64", "value": 1}, False],
                ],
            },
        },
        {  # 6
            "": {
                "inputs": [
                    ["inputs:a", {"type": "uchar", "value": 10}, False],
                    ["inputs:b", {"type": "uchar", "value": 6}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "uchar", "value": 1}, False],
                    ["inputs:d", {"type": "uchar", "value": 2}, False],
                ],
                "outputs": [
                    ["outputs:difference", {"type": "uchar", "value": 1}, False],
                ],
            },
        },
        {  # 7
            "": {
                "inputs": [
                    ["inputs:a", {"type": "uint", "value": 10}, False],
                    ["inputs:b", {"type": "uint", "value": 6}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "uint", "value": 1}, False],
                    ["inputs:d", {"type": "uint", "value": 2}, False],
                ],
                "outputs": [
                    ["outputs:difference", {"type": "uint", "value": 1}, False],
                ],
            },
        },
        {  # 8
            "": {
                "inputs": [
                    ["inputs:a", {"type": "uint64", "value": 10}, False],
                    ["inputs:b", {"type": "uint64", "value": 6}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "uint64", "value": 1}, False],
                    ["inputs:d", {"type": "uint64", "value": 2}, False],
                ],
                "outputs": [
                    ["outputs:difference", {"type": "uint64", "value": 1}, False],
                ],
            },
        },
        {  # 9
            "": {
                "inputs": [
                    ["inputs:a", {"type": "float[2]", "value": [10.0, 20.0]}, False],
                    ["inputs:b", {"type": "float[2]", "value": [0.5, 1.0]}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "float[2]", "value": [1.0, 2.0]}, False],
                    ["inputs:d", {"type": "float[2]", "value": [3.0, 4.0]}, False],
                ],
                "outputs": [
                    ["outputs:difference", {"type": "float[2]", "value": [5.5, 13.0]}, False],
                ],
            },
        },
        {  # 10
            "": {
                "inputs": [
                    ["inputs:a", {"type": "float[3]", "value": [10.0, 20.0, 30.0]}, False],
                    ["inputs:b", {"type": "float[3]", "value": [0.5, 1.0, 1.5]}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "float[3]", "value": [1.0, 2.0, 3.0]}, False],
                    ["inputs:d", {"type": "float[3]", "value": [0.5, 1.0, 1.5]}, False],
                ],
                "outputs": [
                    ["outputs:difference", {"type": "float[3]", "value": [8.0, 16.0, 24.0]}, False],
                ],
            },
        },
        {  # 11
            "": {
                "inputs": [
                    ["inputs:a", {"type": "float[4]", "value": [10.0, 20.0, 30.0, 40.0]}, False],
                    ["inputs:b", {"type": "float[4]", "value": [0.5, 1.0, 1.5, 2.0]}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "float[4]", "value": [1.0, 2.0, 3.0, 4.0]}, False],
                    ["inputs:d", {"type": "float[4]", "value": [0.5, 0.5, 0.5, 0.5]}, False],
                ],
                "outputs": [
                    ["outputs:difference", {"type": "float[4]", "value": [8.0, 16.5, 25.0, 33.5]}, False],
                ],
            },
        },
        {  # 12
            "": {
                "inputs": [
                    ["inputs:a", {"type": "float[2]", "value": [2.0, 3.0]}, False],
                    ["inputs:b", {"type": "float", "value": 1.0}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "float[2]", "value": [0.5, 0.5]}, False],
                    ["inputs:d", {"type": "float", "value": 1.0}, False],
                ],
                "outputs": [
                    ["outputs:difference", {"type": "float[2]", "value": [-0.5, 0.5]}, False],
                ],
            },
        },
        {  # 13
            "": {
                "inputs": [
                    ["inputs:a", {"type": "float", "value": 1.0}, False],
                    ["inputs:b", {"type": "float[2]", "value": [1.0, 2.0]}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "float", "value": 1.0}, False],
                    ["inputs:d", {"type": "float[2]", "value": [1.0, 2.0]}, False],
                ],
                "outputs": [
                    ["outputs:difference", {"type": "float[2]", "value": [-2.0, -4.0]}, False],
                ],
            },
        },
        {  # 14
            "": {
                "inputs": [
                    ["inputs:a", {"type": "float[]", "value": [2.0, 3.0]}, False],
                    ["inputs:b", {"type": "float", "value": 1.0}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "float[]", "value": [2.0, 3.0]}, False],
                    ["inputs:d", {"type": "float", "value": 1.0}, False],
                ],
                "outputs": [
                    ["outputs:difference", {"type": "float[]", "value": [-2.0, -2.0]}, False],
                ],
            },
        },
        {  # 15
            "": {
                "inputs": [
                    ["inputs:a", {"type": "float", "value": 1.0}, False],
                    ["inputs:b", {"type": "float[]", "value": [1.0, 2.0]}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "float", "value": 1.0}, False],
                    ["inputs:d", {"type": "float[]", "value": [1.0, 2.0]}, False],
                ],
                "outputs": [
                    ["outputs:difference", {"type": "float[]", "value": [-2.0, -4.0]}, False],
                ],
            },
        },
        {  # 16
            "": {
                "inputs": [
                    ["inputs:a", {"type": "int64[]", "value": [10]}, False],
                    ["inputs:b", {"type": "int64[]", "value": [5]}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "int64[]", "value": [1]}, False],
                    ["inputs:d", {"type": "int64[]", "value": [2]}, False],
                ],
                "outputs": [
                    ["outputs:difference", {"type": "int64[]", "value": [2]}, False],
                ],
            },
        },
        {  # 17
            "": {
                "inputs": [
                    ["inputs:a", {"type": "int64[]", "value": [10, 20]}, False],
                    ["inputs:b", {"type": "int64[]", "value": [5, 10]}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "int64[]", "value": [1, 2]}, False],
                    ["inputs:d", {"type": "int64[]", "value": [3, 4]}, False],
                ],
                "outputs": [
                    ["outputs:difference", {"type": "int64[]", "value": [1, 4]}, False],
                ],
            },
        },
        {  # 18
            "": {
                "inputs": [
                    ["inputs:a", {"type": "int64[]", "value": [10, 20, 30]}, False],
                    ["inputs:b", {"type": "int64[]", "value": [5, 10, 15]}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "int64[]", "value": [10, 20, 30]}, False],
                    ["inputs:d", {"type": "int64[]", "value": [5, 10, 15]}, False],
                ],
                "outputs": [
                    ["outputs:difference", {"type": "int64[]", "value": [-10, -20, -30]}, False],
                ],
            },
        },
        {  # 19
            "": {
                "inputs": [
                    ["inputs:a", {"type": "int64[]", "value": [10, 20, 30, 40]}, False],
                    ["inputs:b", {"type": "int64[]", "value": [5, 10, 15, 20]}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "int64[]", "value": [10, 20, 30, 40]}, False],
                    ["inputs:d", {"type": "int64[]", "value": [5, 10, 15, 20]}, False],
                ],
                "outputs": [
                    ["outputs:difference", {"type": "int64[]", "value": [-10, -20, -30, -40]}, False],
                ],
            },
        },
        {  # 20
            "": {
                "inputs": [
                    ["inputs:a", {"type": "int[3][]", "value": [[10, 20, 30], [40, 50, 60]]}, False],
                    ["inputs:b", {"type": "int[3]", "value": [5, 10, 15]}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "int[3][]", "value": [[10, 20, 30], [40, 50, 60]]}, False],
                    ["inputs:d", {"type": "int[3]", "value": [5, 10, 15]}, False],
                ],
                "outputs": [
                    [
                        "outputs:difference",
                        {"type": "int[3][]", "value": [[-10, -20, -30], [-10, -20, -30]]},
                        False,
                    ],  # output an array with a single int3 element
                ],
            },
        },
        {  # 21 dynamic arrays mirror the default attributes - should give the same result as previous test
            "": {
                "inputs": [
                    ["inputs:a", {"type": "int[3][]", "value": [[10, 20, 30], [40, 50, 60]]}, False],
                    ["inputs:b", {"type": "int[3]", "value": [5, 10, 15]}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "int[3]", "value": [5, 10, 15]}, False],
                    ["inputs:d", {"type": "int[3][]", "value": [[10, 20, 30], [40, 50, 60]]}, False],
                ],
                "outputs": [
                    ["outputs:difference", {"type": "int[3][]", "value": [[-10, -20, -30], [-10, -20, -30]]}, False],
                ],
            },
        },
        {  # 22
            "": {
                "inputs": [
                    ["inputs:a", {"type": "int[3]", "value": [5, 10, 15]}, False],
                    ["inputs:b", {"type": "int[3][]", "value": [[10, 20, 30], [40, 50, 60]]}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "int[3]", "value": [5, 10, 15]}, False],
                    ["inputs:d", {"type": "int[3][]", "value": [[10, 20, 30], [40, 50, 60]]}, False],
                ],
                "outputs": [
                    ["outputs:difference", {"type": "int[3][]", "value": [[-20, -40, -60], [-80, -100, -120]]}, False],
                ],
            },
        },
        {  # 23
            "": {
                "inputs": [
                    ["inputs:a", {"type": "int[2][]", "value": [[10, 20], [30, 40], [50, 60]]}, False],
                    ["inputs:b", {"type": "int[2]", "value": [5, 10]}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "int[2][]", "value": [[10, 20], [30, 40], [50, 60]]}, False],
                    ["inputs:d", {"type": "int[2]", "value": [5, 10]}, False],
                ],
                "outputs": [
                    ["outputs:difference", {"type": "int[2][]", "value": [[-10, -20], [-10, -20], [-10, -20]]}, False],
                ],
            },
        },
        {  # 24
            "": {
                "inputs": [
                    ["inputs:a", {"type": "int[2]", "value": [5, 10]}, False],
                    ["inputs:b", {"type": "int[2][]", "value": [[10, 20], [30, 40], [50, 60]]}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "int[2]", "value": [5, 10]}, False],
                    ["inputs:d", {"type": "int[2][]", "value": [[10, 20], [30, 40], [50, 60]]}, False],
                ],
                "outputs": [
                    [
                        "outputs:difference",
                        {"type": "int[2][]", "value": [[-20, -40], [-60, -80], [-100, -120]]},
                        False,
                    ],
                ],
            },
        },
    ]

    async def test_subtract(self):
        """Validates the node OgnSubtract with dynamic inputs"""
        controller = og.Controller()
        for i, test_run in enumerate(self.TEST_DATA_SUBTRACT):
            await _test_clear_scene(self, test_run, reset_stage=False)
            test_info = await self._test_setup_scene(
                controller,
                f"/TestGraph{i}",
                "TestNode_omni_graph_nodes_Subtract",
                "omni.graph.nodes.Subtract",
                test_run,
                _TestGraphAndNode(),
            )
            await controller.evaluate(test_info.graph)
            _test_verify_scene(
                self, controller, test_run, test_info, f"omni.graph.nodes.Subtract User test case #{i+1}"
            )

    async def test_subtract_vectorized(self):
        """Validates the node OgnSubtract with dynamic inputs - vectorized computation"""
        controller = og.Controller()
        for i, test_run in enumerate(self.TEST_DATA_SUBTRACT):
            await _test_clear_scene(self, test_run, reset_stage=False)
            test_info = await self._test_setup_scene(
                controller,
                f"/TestGraph{i}",
                "TestNode_omni_graph_nodes_Subtract",
                "omni.graph.nodes.Subtract",
                test_run,
                _TestGraphAndNode(),
                16,
            )
            await controller.evaluate(test_info.graph)
            _test_verify_scene(
                self, controller, test_run, test_info, f"omni.graph.nodes.Subtract User test case #{i+1}", 16
            )

    TEST_DATA_MULTIPLY = [
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "float", "value": 42.0}, False],
                    ["inputs:b", {"type": "float", "value": 2.0}, False],
                ],
                "outputs": [
                    ["outputs:product", {"type": "float", "value": 84.0}, False],
                ],
            },
        },
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "double[2]", "value": [1.0, 42.0]}, False],
                    ["inputs:b", {"type": "double[2]", "value": [2.0, 1.0]}, False],
                ],
                "outputs": [
                    ["outputs:product", {"type": "double[2]", "value": [2.0, 42.0]}, False],
                ],
            },
        },
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "double[]", "value": [1.0, 42.0]}, False],
                    ["inputs:b", {"type": "double", "value": 2.0}, False],
                ],
                "outputs": [
                    ["outputs:product", {"type": "double[]", "value": [2.0, 84.0]}, False],
                ],
            },
        },
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "double[2][]", "value": [[10, 5], [1, 1]]}, False],
                    ["inputs:b", {"type": "double[2]", "value": [5, 5]}, False],
                ],
                "outputs": [
                    ["outputs:product", {"type": "double[2][]", "value": [[50, 25], [5, 5]]}, False],
                ],
            },
        },
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "double[2][]", "value": [[10, 5], [1, 1]]}, False],
                    ["inputs:b", {"type": "double", "value": 2}, False],
                ],
                "outputs": [
                    ["outputs:product", {"type": "double[2][]", "value": [[20, 10], [2, 2]]}, False],
                ],
            },
        },
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "double[2]", "value": [10, 5]}, False],
                    ["inputs:b", {"type": "double", "value": 2}, False],
                ],
                "outputs": [
                    ["outputs:product", {"type": "double[2]", "value": [20, 10]}, False],
                ],
            },
        },
    ]

    async def test_multiply(self):
        controller = og.Controller()
        for i, test_run in enumerate(self.TEST_DATA_MULTIPLY):
            await _test_clear_scene(self, test_run, reset_stage=False)
            test_info = await self._test_setup_scene(
                controller,
                f"/TestGraph{i}",
                "TestNode_omni_graph_nodes_Multiply",
                "omni.graph.nodes.Multiply",
                test_run,
                _TestGraphAndNode(),
            )
            await controller.evaluate(test_info.graph)
            _test_verify_scene(
                self, controller, test_run, test_info, f"omni.graph.nodes.Multiply User test case #{i+1}"
            )

    async def test_multiply_vectorized(self):
        controller = og.Controller()
        for i, test_run in enumerate(self.TEST_DATA_MULTIPLY):
            await _test_clear_scene(self, test_run, reset_stage=False)
            test_info = await self._test_setup_scene(
                controller,
                f"/TestGraph{i}",
                "TestNode_omni_graph_nodes_Multiply",
                "omni.graph.nodes.Multiply",
                test_run,
                _TestGraphAndNode(),
                16,
            )
            await controller.evaluate(test_info.graph)
            _test_verify_scene(
                self, controller, test_run, test_info, f"omni.graph.nodes.Multiply User test case #{i+1}", 16
            )

    TEST_DATA_MINIMUM = [
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "float[2]", "value": [1.0, 2.0]}, False],
                    ["inputs:b", {"type": "float[2]", "value": [0.5, 1.0]}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "float[2]", "value": [3.0, 4.0]}, False],
                    ["inputs:d", {"type": "float[2]", "value": [0.1, 10.0]}, False],
                ],
                "outputs": [
                    ["outputs:minimum", {"type": "float[2]", "value": [0.1, 1.0]}, False],
                ],
            },
        },
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "int64", "value": 10}, False],
                    ["inputs:b", {"type": "int64", "value": 6}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "int64", "value": 4}, False],
                    ["inputs:d", {"type": "int64", "value": 20}, False],
                ],
                "outputs": [
                    ["outputs:minimum", {"type": "int64", "value": 4}, False],
                ],
            },
        },
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "double[2][]", "value": [[10, 5], [1, 1]]}, False],
                    ["inputs:b", {"type": "double[2]", "value": [5, 5]}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "double[2]", "value": [5, 5]}, False],
                    ["inputs:d", {"type": "double[2][]", "value": [[10, 5], [1, 1]]}, False],
                ],
                "outputs": [
                    ["outputs:minimum", {"type": "double[2][]", "value": [[5, 5], [1, 1]]}, False],
                ],
            },
        },
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "double[2][]", "value": [[10, 5], [1, 1]]}, False],
                    ["inputs:b", {"type": "double", "value": 5}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "double[2]", "value": [5, 5]}, False],
                    ["inputs:d", {"type": "double[2][]", "value": [[10, 5], [1, 1]]}, False],
                ],
                "outputs": [
                    ["outputs:minimum", {"type": "double[2][]", "value": [[5, 5], [1, 1]]}, False],
                ],
            },
        },
    ]

    async def test_minimum(self):
        """Validates the node OgnMinimum with dynamic inputs"""
        controller = og.Controller()
        for i, test_run in enumerate(self.TEST_DATA_MINIMUM):
            await _test_clear_scene(self, test_run, reset_stage=False)
            test_info = await self._test_setup_scene(
                controller,
                f"/TestGraph{i}",
                "TestNode_omni_graph_nodes_Minimum",
                "omni.graph.nodes.Minimum",
                test_run,
                _TestGraphAndNode(),
            )
            await controller.evaluate(test_info.graph)
            _test_verify_scene(self, controller, test_run, test_info, f"omni.graph.nodes.Minimum User test case #{i+1}")

    async def test_minimum_vectorized(self):
        """Validates the node OgnMinimum with dynamic inputs - vectorized computation"""
        controller = og.Controller()
        for i, test_run in enumerate(self.TEST_DATA_MINIMUM):
            await _test_clear_scene(self, test_run, reset_stage=False)
            test_info = await self._test_setup_scene(
                controller,
                f"/TestGraph{i}",
                "TestNode_omni_graph_nodes_Minimum",
                "omni.graph.nodes.Minimum",
                test_run,
                _TestGraphAndNode(),
                16,
            )
            await controller.evaluate(test_info.graph)
            _test_verify_scene(
                self, controller, test_run, test_info, f"omni.graph.nodes.Minimum User test case #{i+1}", 16
            )

    TEST_DATA_MAXIMUM = [
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "float[2]", "value": [1.0, 2.0]}, False],
                    ["inputs:b", {"type": "float[2]", "value": [0.5, 1.0]}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "float[2]", "value": [3.0, 4.0]}, False],
                    ["inputs:d", {"type": "float[2]", "value": [0.1, 10.0]}, False],
                ],
                "outputs": [
                    ["outputs:maximum", {"type": "float[2]", "value": [3.0, 10.0]}, False],
                ],
            },
        },
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "int64", "value": 10}, False],
                    ["inputs:b", {"type": "int64", "value": 6}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "int64", "value": 4}, False],
                    ["inputs:d", {"type": "int64", "value": 20}, False],
                ],
                "outputs": [
                    ["outputs:maximum", {"type": "int64", "value": 20}, False],
                ],
            },
        },
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "double[2][]", "value": [[10, 5], [1, 1]]}, False],
                    ["inputs:b", {"type": "double[2]", "value": [5, 5]}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "double[2]", "value": [5, 5]}, False],
                    ["inputs:d", {"type": "double[2][]", "value": [[10, 5], [1, 1]]}, False],
                ],
                "outputs": [
                    ["outputs:maximum", {"type": "double[2][]", "value": [[10, 5], [5, 5]]}, False],
                ],
            },
        },
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "double[2][]", "value": [[10, 5], [1, 1]]}, False],
                    ["inputs:b", {"type": "double", "value": 5}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "double[2]", "value": [5, 5]}, False],
                    ["inputs:d", {"type": "double[2][]", "value": [[10, 5], [1, 1]]}, False],
                ],
                "outputs": [
                    ["outputs:maximum", {"type": "double[2][]", "value": [[10, 5], [5, 5]]}, False],
                ],
            },
        },
    ]

    async def test_maximum(self):
        """Validates the node OgnMaximum with dynamic inputs"""
        controller = og.Controller()
        for i, test_run in enumerate(self.TEST_DATA_MAXIMUM):
            await _test_clear_scene(self, test_run, reset_stage=False)
            test_info = await self._test_setup_scene(
                controller,
                f"/TestGraph{i}",
                "TestNode_omni_graph_nodes_Maximum",
                "omni.graph.nodes.Maximum",
                test_run,
                _TestGraphAndNode(),
            )
            await controller.evaluate(test_info.graph)
            _test_verify_scene(self, controller, test_run, test_info, f"omni.graph.nodes.Maximum User test case #{i+1}")

    async def test_maximum_vectorized(self):
        """Validates the node OgnMaximum with dynamic inputs - vectorized computation"""
        controller = og.Controller()
        for i, test_run in enumerate(self.TEST_DATA_MAXIMUM):
            await _test_clear_scene(self, test_run, reset_stage=False)
            test_info = await self._test_setup_scene(
                controller,
                f"/TestGraph{i}",
                "TestNode_omni_graph_nodes_Maximum",
                "omni.graph.nodes.Maximum",
                test_run,
                _TestGraphAndNode(),
                16,
            )
            await controller.evaluate(test_info.graph)
            _test_verify_scene(
                self, controller, test_run, test_info, f"omni.graph.nodes.Maximum User test case #{i+1}", 16
            )

    TEST_DATA_AND = [
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "bool", "value": False}, False],
                    ["inputs:b", {"type": "bool", "value": True}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "bool", "value": False}, False],
                    ["inputs:d", {"type": "bool", "value": True}, False],
                ],
                "outputs": [
                    ["outputs:result", False, False],
                ],
            },
        },
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "bool", "value": True}, False],
                    ["inputs:b", {"type": "bool", "value": True}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "bool", "value": True}, False],
                    ["inputs:d", {"type": "bool", "value": True}, False],
                ],
                "outputs": [
                    ["outputs:result", True, False],
                ],
            },
        },
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "bool[]", "value": [False, False, True, True]}, False],
                    ["inputs:b", {"type": "bool[]", "value": [False, True, False, True]}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "bool", "value": True}, False],
                    ["inputs:d", {"type": "bool[]", "value": [False, True, False, True]}, False],
                ],
                "outputs": [
                    ["outputs:result", [False, False, False, True], False],
                ],
            },
        },
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "bool", "value": False}, False],
                    ["inputs:b", {"type": "bool[]", "value": [False, True]}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "bool", "value": False}, False],
                    ["inputs:d", {"type": "bool[]", "value": [False, True]}, False],
                ],
                "outputs": [
                    ["outputs:result", [False, False], False],
                ],
            },
        },
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "bool[]", "value": [False, True]}, False],
                    ["inputs:b", {"type": "bool", "value": False}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "bool[]", "value": [False, True]}, False],
                    ["inputs:d", {"type": "bool", "value": False}, False],
                ],
                "outputs": [
                    ["outputs:result", [False, False], False],
                ],
            },
        },
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "bool[]", "value": [False, True]}, False],
                    ["inputs:b", {"type": "bool", "value": True}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "bool[]", "value": [False, True]}, False],
                    ["inputs:d", {"type": "bool", "value": True}, False],
                ],
                "outputs": [
                    ["outputs:result", [False, True], False],
                ],
            },
        },
    ]

    async def test_boolean_and(self):
        controller = og.Controller()
        for i, test_run in enumerate(self.TEST_DATA_AND):
            await _test_clear_scene(self, test_run, reset_stage=False)
            test_info = await self._test_setup_scene(
                controller,
                f"/TestGraph{i}",
                "TestNode_omni_graph_nodes_BooleanAnd",
                "omni.graph.nodes.BooleanAnd",
                test_run,
                _TestGraphAndNode(),
            )
            await controller.evaluate(test_info.graph)
            _test_verify_scene(
                self, controller, test_run, test_info, f"omni.graph.nodes.BooleanAnd User test case #{i+1}"
            )

    async def test_boolean_and_vectorized(self):
        controller = og.Controller()
        for i, test_run in enumerate(self.TEST_DATA_AND):
            await _test_clear_scene(self, test_run, reset_stage=False)
            test_info = await self._test_setup_scene(
                controller,
                f"/TestGraph{i}",
                "TestNode_omni_graph_nodes_BooleanAnd",
                "omni.graph.nodes.BooleanAnd",
                test_run,
                _TestGraphAndNode(),
                16,
            )
            await controller.evaluate(test_info.graph)
            _test_verify_scene(
                self, controller, test_run, test_info, f"omni.graph.nodes.BooleanAnd User test case #{i+1}", 16
            )

    TEST_DATA_OR = [
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "bool", "value": False}, False],
                    ["inputs:b", {"type": "bool", "value": True}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "bool", "value": False}, False],
                    ["inputs:d", {"type": "bool", "value": True}, False],
                ],
                "outputs": [
                    ["outputs:result", True, False],
                ],
            },
        },
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "bool[]", "value": [False, False, True, True]}, False],
                    ["inputs:b", {"type": "bool[]", "value": [False, True, False, True]}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "bool", "value": False}, False],
                    ["inputs:d", {"type": "bool", "value": True}, False],
                ],
                "outputs": [
                    ["outputs:result", {"type": "bool[]", "value": [True, True, True, True]}, False],
                ],
            },
        },
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "bool", "value": False}, False],
                    ["inputs:b", {"type": "bool[]", "value": [False, True]}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "bool", "value": False}, False],
                    ["inputs:d", {"type": "bool", "value": True}, False],
                ],
                "outputs": [
                    ["outputs:result", [True, True], False],
                ],
            },
        },
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "bool[]", "value": [False, True]}, False],
                    ["inputs:b", {"type": "bool", "value": False}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "bool", "value": False}, False],
                    ["inputs:d", {"type": "bool[]", "value": [False, True]}, False],
                ],
                "outputs": [
                    ["outputs:result", [False, True], False],
                ],
            },
        },
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "bool[]", "value": [False, True]}, False],
                    ["inputs:b", {"type": "bool", "value": False}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "bool", "value": False}, False],
                    ["inputs:d", {"type": "bool[]", "value": [False, True]}, False],
                ],
                "outputs": [
                    ["outputs:result", {"type": "bool[]", "value": [False, True]}, False],
                ],
            },
        },
    ]

    async def test_boolean_or(self):
        controller = og.Controller()
        for i, test_run in enumerate(self.TEST_DATA_OR):
            await _test_clear_scene(self, test_run, reset_stage=False)
            test_info = await self._test_setup_scene(
                controller,
                f"/TestGraph{i}",
                "TestNode_omni_graph_nodes_BooleanOr",
                "omni.graph.nodes.BooleanOr",
                test_run,
                _TestGraphAndNode(),
            )
            await controller.evaluate(test_info.graph)
            _test_verify_scene(
                self, controller, test_run, test_info, f"omni.graph.nodes.BooleanOr User test case #{i+1}"
            )

    async def test_boolean_or_vectorized(self):
        controller = og.Controller()
        for i, test_run in enumerate(self.TEST_DATA_OR):
            await _test_clear_scene(self, test_run, reset_stage=False)
            test_info = await self._test_setup_scene(
                controller,
                f"/TestGraph{i}",
                "TestNode_omni_graph_nodes_BooleanOr",
                "omni.graph.nodes.BooleanOr",
                test_run,
                _TestGraphAndNode(),
                16,
            )
            await controller.evaluate(test_info.graph)
            _test_verify_scene(
                self, controller, test_run, test_info, f"omni.graph.nodes.BooleanOr User test case #{i+1}", 16
            )

    TEST_DATA_NAND = [
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "bool", "value": False}, False],
                    ["inputs:b", {"type": "bool", "value": True}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "bool", "value": False}, False],
                    ["inputs:d", {"type": "bool", "value": True}, False],
                ],
                "outputs": [
                    ["outputs:result", True, False],
                ],
            },
        },
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "bool[]", "value": [False, False, True, True]}, False],
                    ["inputs:b", {"type": "bool[]", "value": [False, True, False, True]}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "bool[]", "value": [False, False, True, True]}, False],
                    ["inputs:d", {"type": "bool[]", "value": [False, True, False, True]}, False],
                ],
                "outputs": [
                    ["outputs:result", [True, True, True, False], False],
                ],
            },
        },
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "bool", "value": False}, False],
                    ["inputs:b", {"type": "bool[]", "value": [False, True]}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "bool", "value": False}, False],
                    ["inputs:d", {"type": "bool[]", "value": [False, True]}, False],
                ],
                "outputs": [
                    ["outputs:result", [True, True], False],
                ],
            },
        },
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "bool", "value": False}, False],
                    ["inputs:b", {"type": "bool[]", "value": [False, True]}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "bool[]", "value": [False, True]}, False],
                    ["inputs:d", {"type": "bool", "value": False}, False],
                ],
                "outputs": [
                    ["outputs:result", [True, True], False],
                ],
            },
        },
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "bool[]", "value": [False, True]}, False],
                    ["inputs:b", {"type": "bool", "value": True}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "bool[]", "value": [False, True]}, False],
                    ["inputs:d", {"type": "bool[]", "value": [False, True]}, False],
                ],
                "outputs": [
                    ["outputs:result", [True, False], False],
                ],
            },
        },
    ]

    async def test_boolean_nand(self):
        controller = og.Controller()
        for i, test_run in enumerate(self.TEST_DATA_NAND):
            await _test_clear_scene(self, test_run, reset_stage=False)
            test_info = await self._test_setup_scene(
                controller,
                f"/TestGraph{i}",
                "TestNode_omni_graph_nodes_BooleanNand",
                "omni.graph.nodes.BooleanNand",
                test_run,
                _TestGraphAndNode(),
            )
            await controller.evaluate(test_info.graph)
            _test_verify_scene(
                self, controller, test_run, test_info, f"omni.graph.nodes.BooleanNand User test case #{i+1}"
            )

    async def test_boolean_nand_vectorized(self):
        controller = og.Controller()
        for i, test_run in enumerate(self.TEST_DATA_NAND):
            await _test_clear_scene(self, test_run, reset_stage=False)
            test_info = await self._test_setup_scene(
                controller,
                f"/TestGraph{i}",
                "TestNode_omni_graph_nodes_BooleanNand",
                "omni.graph.nodes.BooleanNand",
                test_run,
                _TestGraphAndNode(),
                16,
            )
            await controller.evaluate(test_info.graph)
            _test_verify_scene(
                self, controller, test_run, test_info, f"omni.graph.nodes.BooleanNand User test case #{i+1}", 16
            )

    TEST_DATA_NOR = [
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "bool", "value": False}, False],
                    ["inputs:b", {"type": "bool", "value": True}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "bool", "value": False}, False],
                    ["inputs:d", {"type": "bool", "value": True}, False],
                ],
                "outputs": [
                    ["outputs:result", False, False],
                ],
            },
        },
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "bool", "value": False}, False],
                    ["inputs:b", {"type": "bool", "value": False}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "bool", "value": False}, False],
                ],
                "outputs": [
                    ["outputs:result", True, False],
                ],
            },
        },
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "bool[]", "value": [False, False, True, True]}, False],
                    ["inputs:b", {"type": "bool[]", "value": [False, True, False, True]}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "bool[]", "value": [False, False, True, True]}, False],
                    ["inputs:d", {"type": "bool[]", "value": [False, True, False, True]}, False],
                ],
                "outputs": [
                    ["outputs:result", [True, False, False, False], False],
                ],
            },
        },
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "bool[]", "value": [False, False, True, True]}, False],
                    ["inputs:b", {"type": "bool[]", "value": [False, True, False, True]}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "bool[]", "value": [False, True, False, True]}, False],
                    ["inputs:d", {"type": "bool[]", "value": [False, False, True, True]}, False],
                ],
                "outputs": [
                    ["outputs:result", [True, False, False, False], False],
                ],
            },
        },
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "bool", "value": False}, False],
                    ["inputs:b", {"type": "bool[]", "value": [False, True]}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "bool", "value": False}, False],
                    ["inputs:d", {"type": "bool[]", "value": [False, True]}, False],
                ],
                "outputs": [
                    ["outputs:result", [True, False], False],
                ],
            },
        },
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "bool[]", "value": [False, True]}, False],
                    ["inputs:b", {"type": "bool", "value": False}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "bool[]", "value": [False, True]}, False],
                    ["inputs:d", {"type": "bool", "value": False}, False],
                ],
                "outputs": [
                    ["outputs:result", [True, False], False],
                ],
            },
        },
    ]

    async def test_boolean_nor(self):
        controller = og.Controller()
        for i, test_run in enumerate(self.TEST_DATA_NOR):
            await _test_clear_scene(self, test_run, reset_stage=False)
            test_info = await self._test_setup_scene(
                controller,
                f"/TestGraph{i}",
                "TestNode_omni_graph_nodes_BooleanNor",
                "omni.graph.nodes.BooleanNor",
                test_run,
                _TestGraphAndNode(),
            )
            await controller.evaluate(test_info.graph)
            _test_verify_scene(
                self, controller, test_run, test_info, f"omni.graph.nodes.BooleanNor User test case #{i+1}"
            )

    async def test_boolean_nor_vectorized(self):
        controller = og.Controller()
        for i, test_run in enumerate(self.TEST_DATA_NOR):
            await _test_clear_scene(self, test_run, reset_stage=False)
            test_info = await self._test_setup_scene(
                controller,
                f"/TestGraph{i}",
                "TestNode_omni_graph_nodes_BooleanNor",
                "omni.graph.nodes.BooleanNor",
                test_run,
                _TestGraphAndNode(),
                16,
            )
            await controller.evaluate(test_info.graph)
            _test_verify_scene(
                self, controller, test_run, test_info, f"omni.graph.nodes.BooleanNor User test case #{i+1}", 16
            )

    TEST_DATA_APPEND_STRING = [
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "token", "value": "/"}, False],
                    ["inputs:b", {"type": "token", "value": "foo"}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "token", "value": "/"}, False],
                    ["inputs:d", {"type": "token", "value": "bar"}, False],
                ],
                "outputs": [
                    ["outputs:value", {"type": "token", "value": "/foo/bar"}, False],
                ],
            },
        },
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "token[]", "value": ["/World", "/World2"]}, False],
                    ["inputs:b", {"type": "token", "value": "/foo"}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "token", "value": "/"}, False],
                    ["inputs:d", {"type": "token", "value": "bar"}, False],
                ],
                "outputs": [
                    ["outputs:value", {"type": "token[]", "value": ["/World/foo/bar", "/World2/foo/bar"]}, False],
                ],
            },
        },
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "token[]", "value": ["/World", "/World2"]}, False],
                    ["inputs:b", {"type": "token[]", "value": ["/foo", "/bar"]}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "token[]", "value": ["/", "baz"]}, False],
                    ["inputs:d", {"type": "token[]", "value": ["/", "biz"]}, False],
                ],
                "outputs": [
                    ["outputs:value", {"type": "token[]", "value": ["/World/foo//", "/World2/barbazbiz"]}, False],
                ],
            },
        },
        {
            "": {
                "inputs": [
                    ["inputs:a", {"type": "string", "value": "/"}, False],
                    ["inputs:b", {"type": "string", "value": "foo"}, False],
                ],
                "dynamicInputs": [
                    ["inputs:c", {"type": "string", "value": "/"}, False],
                    ["inputs:d", {"type": "string", "value": "bar"}, False],
                ],
                "outputs": [
                    ["outputs:value", {"type": "string", "value": "/foo/bar"}, False],
                ],
            },
        },
    ]

    async def test_append_string(self):
        controller = og.Controller()
        for i, test_run in enumerate(self.TEST_DATA_APPEND_STRING):
            await _test_clear_scene(self, test_run, reset_stage=False)
            test_info = await self._test_setup_scene(
                controller,
                f"/TestGraph{i}",
                "AppendString",
                "omni.graph.nodes.BuildString",
                test_run,
                _TestGraphAndNode(),
            )
            await controller.evaluate(test_info.graph)
            _test_verify_scene(
                self, controller, test_run, test_info, f"omni.graph.nodes.BuildString User test case #{i+1}"
            )
