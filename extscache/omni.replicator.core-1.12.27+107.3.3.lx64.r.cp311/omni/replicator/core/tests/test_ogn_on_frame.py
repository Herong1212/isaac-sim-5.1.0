# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import unittest
from pathlib import Path

import carb.events
import carb.settings
import numpy as np
import omni.graph.core as og
import omni.kit
import omni.replicator.core as rep
import omni.usd
from PIL import Image

TEST_DATA_DIR = Path(os.path.dirname(os.path.realpath(__file__))).joinpath("data")


class TestOgnOnFrame(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self.golden_dir = os.path.join(TEST_DATA_DIR, "golden")
        await omni.usd.get_context().new_stage_async()
        rep.set_global_seed(1234)

        self._stage = omni.usd.get_context().get_stage()
        self._controller = og.Controller()

        self._on_frame_node = rep.utils.create_node("omni.replicator.core.OgnOnFrame")
        self._on_frame_node_prim = self._stage.GetPrimAtPath(self._on_frame_node.get_prim_path())

        self._counter = rep.utils.create_node("omni.graph.action.Counter")
        self._on_frame_node.get_attribute("outputs:execOut").connect(self._counter.get_attribute("inputs:execIn"), True)
        await omni.kit.app.get_app().next_update_async()

    async def tearDown(self):
        carb.settings.get_settings().set("/exts/omni.replicator.core/Orchestrator/enableEvalTriggers", False)
        rep.orchestrator.stop()
        await omni.usd.get_context().new_stage_async()

    async def test_start_stop(self):
        """Test that start and stop events enable/disable the node execution"""
        self._on_frame_node.get_attribute("inputs:maxExecs").set(10)

        await rep.orchestrator._orchestrator.start_async()
        for frame_num in range(10):
            await omni.kit.app.get_app().next_update_async()
            exec_count = self._on_frame_node.get_attribute("outputs:execCounts").get()
            self.assertEqual(exec_count, frame_num, f"Expected execution {frame_num}, got {exec_count}")
        frame_num = self._on_frame_node.get_attribute("outputs:execCounts").get()
        rep.orchestrator.stop()
        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(frame_num, self._on_frame_node.get_attribute("outputs:execCounts").get())

    async def test_start_stop_secondary_graph(self):
        """Test that start and stop events enable/disable the node execution"""
        self._on_frame_node.get_attribute("inputs:maxExecs").set(10)

        # Enable eval all
        rep.settings.carb_settings("/exts/omni.replicator.core/Orchestrator/enableEvalTriggers", True)

        # Create secondary graph and node
        graph_sec = og.Controller().create_graph(
            {
                "graph_path": "/My/Graph",
                "evaluator_name": "execution",
                "pipeline_stage": og.GraphPipelineStage.GRAPH_PIPELINE_STAGE_SIMULATION,
            }
        )
        on_frame_node_sec = rep.utils.create_node("omni.replicator.core.OgnOnFrame", graph=graph_sec)

        counter_sec = rep.utils.create_node("omni.graph.action.Counter", graph=graph_sec)
        on_frame_node_sec.get_attribute("outputs:execOut").connect(self._counter.get_attribute("inputs:execIn"), True)
        await omni.kit.app.get_app().next_update_async()

        await rep.orchestrator._orchestrator.start_async()
        for frame_num in range(10):
            await omni.kit.app.get_app().next_update_async()
            exec_count = self._on_frame_node.get_attribute("outputs:execCounts").get()
            self.assertEqual(
                exec_count, frame_num, f"Failed on primary graph, expected execution {frame_num}, got {exec_count}"
            )
            exec_count_sec = on_frame_node_sec.get_attribute("outputs:execCounts").get()
            self.assertEqual(
                exec_count_sec,
                frame_num,
                f"Failed on secondary graph, expected execution {frame_num}, got {exec_count_sec}",
            )
        frame_num = self._on_frame_node.get_attribute("outputs:execCounts").get()
        rep.orchestrator.stop()
        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(frame_num, self._on_frame_node.get_attribute("outputs:execCounts").get())
        self.assertEqual(frame_num, on_frame_node_sec.get_attribute("outputs:execCounts").get())

    async def test_preview(self):
        """Test that preview generates a single impulse"""
        self.assertEqual(self._counter.get_attribute("outputs:count").get(), 0)
        rep.orchestrator.preview()
        self.assertEqual(self._counter.get_attribute("outputs:count").get(), 1)
        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(self._counter.get_attribute("outputs:count").get(), 1)
        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(self._counter.get_attribute("outputs:count").get(), 1)

    async def test_preview_async(self):
        """Test that preview generates a single impulse"""
        self.assertEqual(self._counter.get_attribute("outputs:count").get(), 0)
        await rep.orchestrator.preview_async()
        self.assertEqual(self._counter.get_attribute("outputs:count").get(), 1)
        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(self._counter.get_attribute("outputs:count").get(), 1)
        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(self._counter.get_attribute("outputs:count").get(), 1)

    async def test_interval(self):
        """Test that interval works as expected"""
        interval = 10
        self._on_frame_node.get_attribute("inputs:maxExecs").set(10)
        self._on_frame_node.get_attribute("inputs:interval").set(interval)
        for f in range(2):
            for _ in range(interval):
                await rep.orchestrator.step_async()
                num_execs = self._on_frame_node.get_attribute("outputs:execCounts").get()
                self.assertEqual(num_execs, f, f"Expected {f} execs, got {num_execs}")
