# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from pathlib import Path

import carb.settings
import omni.anim.curve.core
import omni.graph.core as og
import omni.kit.app
import omni.kit.commands
import omni.kit.test
import omni.kit.ui_test as ui_test
import omni.usd
from carb.input import KeyboardInput as key


class TestTimelineNode(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        extension_root_folder = Path(
            omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
        )
        self._test_files = extension_root_folder.joinpath("data/tests/usd")
        self._settings = carb.settings.get_settings()

    async def tearDown(self):
        await omni.usd.get_context().close_stage_async()

    async def test_timeline_node(self):
        await self._test_timeline_node_impl()

    async def _load_stage(self):
        usd_context = omni.usd.get_context()
        self._app = omni.kit.app.get_app()

        filename = "timeline_node_test.usda"
        test_file_path = self._test_files.joinpath(filename).absolute()
        await usd_context.open_stage_async(str(test_file_path))

        for i in range(10):
            await self._app.next_update_async()

        self._stage = usd_context.get_stage()

    async def _test_timeline_node_impl(self):
        await self._load_stage()

        graph = self._stage.GetPrimAtPath("/World/ActionGraph")
        self.assertEqual(graph.GetTypeName(), "OmniGraph")

        test_graph = og.get_graph_by_path(graph.GetPrimPath().pathString)

        # Test play from start
        await self._test_node_outputs(test_graph, key.J, [0.1, 1, 2])

        # Test play from start with a Delay node (latent state) connected in between (OM-96686)
        await self._test_node_outputs(test_graph, key.Y, [1.1, 2, 3], offset=1)

        # Test play from end
        await self._test_node_outputs(test_graph, key.K, [0.1, 1, 2], reverse=True)

        # Test play
        await self._test_node_outputs(test_graph, key.M, [0.1, 1, 2])

        # Test reverse
        await self._test_node_outputs(test_graph, key.N, [0.1, 1, 2], reverse=True)

        # Test stop
        await self._test_node_outputs(test_graph, key.J, [0.1, 1])

        curr_value = self._get_node_output()
        # stop execution, value should not keep going
        await self._test_node_outputs(test_graph, key.O, [1, 2], override_expected_value=curr_value)

        # Test set time
        await ui_test.emulate_keyboard_press(key.J)
        await og.Controller.evaluate(graph)
        # fast-forward time to 1
        await self._test_node_outputs(test_graph, key.L, [0.1, 1], offset=-1)

    async def _test_node_outputs(
        self,
        graph,
        keypress: key | None,
        times: list[float],
        offset: float = 0,
        reverse: bool = False,
        override_expected_value: float | None = None,
    ):
        start_time = self._app.get_time_since_start_s()

        if keypress is not None:
            await ui_test.emulate_keyboard_press(keypress, human_delay_speed=1)

        for time in times:
            if time > 0:
                while True:
                    curr_time = self._app.get_time_since_start_s()
                    if curr_time - start_time >= time:
                        break
                    await og.Controller.evaluate(graph)

            self._test_y_within_range(time, offset, reverse, override_expected_value)

    def _test_y_within_range(
        self,
        time: float,
        offset: float,
        reverse: bool,
        override_expected_value: float | None = None,
    ):
        node_time = time - offset
        if reverse:
            node_time = 2 - node_time
        expected_output = (
            override_expected_value if override_expected_value is not None else self._evaluate_curve_at_time(node_time)
        )
        actual_output = self._get_node_output()
        self.assertAlmostEqual(
            actual_output, expected_output, msg=f"{actual_output} is not close to {expected_output} at {time}", delta=10
        )

    def _evaluate_curve_at_time(self, time: float):
        curve_plugin = omni.anim.curve.core.acquire_interface()
        return curve_plugin.evaluate("/World/ActionGraph/timeline.outputs:output:x", time)

    def _get_node_output(self):
        attribute = og.ObjectLookup.attribute("/World/ActionGraph/timeline.outputs:output")
        return og.Controller.get(attribute=attribute)
