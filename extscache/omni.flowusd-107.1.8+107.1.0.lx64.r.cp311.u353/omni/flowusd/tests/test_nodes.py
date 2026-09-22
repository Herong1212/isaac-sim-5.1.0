# Copyright (c) 2021-2023, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto. Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.graph.core as og
import omni.graph.core.tests as ogts


class TestFlowUsdNodes(ogts.OmniGraphTestCase):
    """Tests for various flowusd nodes"""

    async def setUp(self):
        await super().setUp()

    async def tearDown(self):
        await super().tearDown()

    # Regression test to fix OM-74947
    async def test_prim_path_changed(self):
        """Test ReadUSDAttributeRange node value changes if input prim is changing"""

        controller = og.Controller()

        TEST_GRAPH_PATH = "/World/Graph"

        (result, error) = await ogts.load_test_file("TestRangeNodePrimPath.usda", use_caller_subdirectory=True)
        self.assertTrue(result, error)
        graph = controller.graph(TEST_GRAPH_PATH)
        self.assertTrue(graph)

        range_node = controller.node(f"{TEST_GRAPH_PATH}/read_usd_attribute_range")

        await controller.evaluate(graph)

        value_first = controller.get(controller.attribute("outputs:value", range_node))
        value_first_str = str(value_first)

        await controller.evaluate(graph)

        value_second = controller.get(controller.attribute("outputs:value", range_node))
        value_second_str = str(value_second)

        self.assertNotEqual(value_first_str, value_second_str)
