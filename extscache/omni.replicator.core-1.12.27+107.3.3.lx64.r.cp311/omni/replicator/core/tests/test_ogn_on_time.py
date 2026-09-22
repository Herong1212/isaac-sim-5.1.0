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
import time
import unittest
from pathlib import Path

import carb
import numpy as np
import omni.graph.core as og
import omni.kit
import omni.replicator.core as rep
import omni.usd

TEST_DATA_DIR = Path(os.path.dirname(os.path.realpath(__file__))).joinpath("data")


class Counter(rep.Writer):
    def __init__(self):
        self.annotators = ["LdrColor"]  # Remove annotator when can run without any
        self.count = 0

    def write(self, data):
        self.count += 1


class TestOgnOnTime(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self.golden_dir = os.path.join(TEST_DATA_DIR, "golden")
        carb.settings.get_settings().set("/omni/replicator/RTSubframes", 1)
        await omni.usd.get_context().new_stage_async()
        timeline = omni.timeline.get_timeline_interface()
        timeline.set_time_codes_per_second(24)
        timeline.set_looping(True)
        await omni.kit.app.get_app().next_update_async()
        rep.set_global_seed(1234)

        self._stage = omni.usd.get_context().get_stage()
        self._controller = og.Controller()

        self._on_time_node = rep.utils.create_node("omni.replicator.core.OgnOnTime")
        self._on_time_node_prim = self._stage.GetPrimAtPath(self._on_time_node.get_prim_path())

        self._counter = rep.utils.create_node("omni.graph.action.Counter")
        self._on_time_node.get_attribute("outputs:execOut").connect(self._counter.get_attribute("inputs:execIn"), True)
        rep.orchestrator._orchestrator._reset_sim_times_to_write()
        rep.orchestrator.set_capture_on_play(True)
        await omni.kit.app.get_app().next_update_async()

    async def tearDown(self):
        carb.settings.get_settings().set("/omni/replicator/RTSubframes", 1)
        rep.orchestrator.set_capture_on_play(False)
        await rep.orchestrator.stop_async()
        # await omni.usd.get_context().new_stage_async()
        rep.orchestrator._orchestrator._reset_sim_times_to_write()

    async def test_start_stop(self):
        """Test that start and stop events enable/disable the node execution"""
        timeline_iface = omni.timeline.get_timeline_interface()
        start_time = timeline_iface.get_current_time()
        self._on_time_node.get_attribute("inputs:maxExecs").set(10)
        self._on_time_node.get_attribute("inputs:interval").set(0.5)
        await rep.orchestrator.step_async()

        rep.orchestrator.resume()

        # Start waits to frames to disable asyncRendering
        for _ in range(20):
            await omni.kit.app.get_app().next_update_async()
        cur_count = self._counter.get_attribute("outputs:count").get()
        rep.orchestrator.stop()

        for _ in range(20):
            await omni.kit.app.get_app().next_update_async()
        self.assertGreater(cur_count, 0)
        self.assertEqual(cur_count, self._counter.get_attribute("outputs:count").get())

    async def test_preview(self):
        """Test that preview generates a single impulse"""
        self.assertEqual(self._counter.get_attribute("outputs:count").get(), 0)
        rep.orchestrator.preview()
        self.assertEqual(self._counter.get_attribute("outputs:count").get(), 1)
        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(self._counter.get_attribute("outputs:count").get(), 1)
        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(self._counter.get_attribute("outputs:count").get(), 1)

    async def test_interval(self):
        """Test that interval works as expected"""
        # Add visual cue
        with rep.create.sphere(position=(0, 300, 0), scale=0.5):
            rep.physics.rigid_body()

        class Counter(rep.Writer):
            def __init__(self):
                self.annotators = ["LdrColor"]  # Remove annotator when can run without any
                self.count = 0

            def write(self, data):
                self.count += 1

        rp = rep.create.render_product("/OmniverseKit_Persp", (128, 128))
        counter_writer = Counter()
        counter_writer.attach(rp)

        timeline_iface = omni.timeline.get_timeline_interface()
        timeline_iface.set_current_time(0.0)
        timeline_iface.set_end_time(10.0)
        interval = 0.25
        num = 5
        fps = timeline_iface.get_time_codes_per_seconds()
        self._on_time_node.get_attribute("inputs:maxExecs").set(num)
        self._on_time_node.get_attribute("inputs:interval").set(interval)
        self._on_time_node.get_attribute("inputs:resetPhysics").set(False)
        await omni.kit.app.get_app().next_update_async()

        await rep.orchestrator.run_until_complete_async()

        # Check that trigger executed `num` times
        ontime_node_counts = self._on_time_node.get_attribute("outputs:execCounts").get()
        counter_node_counts = self._counter.get_attribute("outputs:count").get()
        self.assertEqual(ontime_node_counts, num, f"OnTime node registered {ontime_node_counts}, expected {num}")
        self.assertEqual(
            counter_node_counts, num + 1, f"Counter node registered {counter_node_counts}, expected {num + 1}"
        )  # +1 to account for first frame

        # Check that orchestrator scheduled exactly `fps * interval * num` frames
        num_frames = int(fps * interval * num)  # 24 * 0.25 * 5 = 30 frames
        self.assertEqual(
            counter_writer.count,
            num_frames,
            f"Counter writer registered {counter_writer.count} frames, expected {num_frames}",
        )

        # Check that trigger reset timeline to 0.0
        self.assertAlmostEqual(timeline_iface.get_current_time(), 0.0)

    async def test_interval_short_end_time(self):
        # Add visual cue
        with rep.create.sphere(position=(0, 300, 0), scale=0.5):
            rep.physics.rigid_body()

        rp = rep.create.render_product("/OmniverseKit_Persp", (128, 128))
        counter_writer = Counter()
        counter_writer.attach(rp)

        timeline_iface = omni.timeline.get_timeline_interface()
        fps = timeline_iface.get_time_codes_per_seconds()
        timeline_iface.set_current_time(0.0)
        timeline_iface.set_end_time(0.2)
        interval = 1.0 / 6.0
        num = 5

        self._on_time_node.get_attribute("inputs:maxExecs").set(num)
        self._on_time_node.get_attribute("inputs:interval").set(interval)
        self._on_time_node.get_attribute("inputs:resetPhysics").set(False)
        await omni.kit.app.get_app().next_update_async()

        await rep.orchestrator.run_until_complete_async()

        # Check that trigger executed `num` times
        ontime_node_counts = self._on_time_node.get_attribute("outputs:execCounts").get()
        counter_node_counts = self._counter.get_attribute("outputs:count").get()
        self.assertEqual(ontime_node_counts, num, f"OnTime node registered {ontime_node_counts}, expected {num}")
        self.assertEqual(
            counter_node_counts, num + 1, f"Counter node registered {counter_node_counts}, expected {num + 1}"
        )  # +1 to account for first frame

        # Check that orchestrator scheduled exactly `fps * interval * (num + 1)` frames
        # (num + 1) accounts for frame at 0.0 s
        # Update subscription appears to force timeline to loop to 0.0 more reliably than without (ie. async)
        num_frames = int(fps * interval * (num + 1))  # 24 * 0.167 * 5 = 24 frames
        self.assertEqual(
            counter_writer.count,
            num_frames,
            f"Counter writer registered {counter_writer.count} frames, expected {num_frames}",
        )

        # Check that trigger reset timeline to 0.0
        self.assertAlmostEqual(timeline_iface.get_current_time(), 0.0)

    async def test_on_time_subframes(self):
        """Ensure correct frames scheduled when subframes are used

        Ensure consistent number of frames generated per trigger execution and that frame 0.0 is generated
        """
        max_execs = 2
        carb.settings.get_settings().set("/omni/replicator/RTSubframes", 3)
        # trigger = rep.trigger.on_time(max_execs=max_execs, interval=0.125)
        self._on_time_node.get_attribute("inputs:maxExecs").set(2)
        self._on_time_node.get_attribute("inputs:interval").set(0.125)

        camera = rep.create.camera(position=(0, 0, 100))
        rp = rep.create.render_product(camera=camera, resolution=(512, 512))

        counter_writer = Counter()
        counter_writer.attach(rp)

        await rep.orchestrator.run_until_complete_async()

        self.assertEqual(
            counter_writer.count,
            3 * max_execs,
            f"Counter writer registered {counter_writer.count} frames, expected {7 * max_execs}",
        )
        self.assertEqual(self._on_time_node.get_attribute("outputs:execCounts").get(), max_execs)
