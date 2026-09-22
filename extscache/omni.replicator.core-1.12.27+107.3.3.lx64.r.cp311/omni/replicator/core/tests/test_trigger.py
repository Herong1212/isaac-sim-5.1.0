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

import doctest
import os
from functools import partial
from pathlib import Path

import numpy as np
import omni.graph.core as og
import omni.kit
import omni.replicator.core as rep
import omni.usd
from omni.replicator.core.create import render_product

TEST_DATA_DIR = Path(os.path.dirname(os.path.realpath(__file__))).joinpath("data")


class TestTriggers(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self.golden_dir = os.path.join(TEST_DATA_DIR, "golden")
        await omni.usd.get_context().new_stage_async()

        # Setting time to zero necessary, new stage does not always reset timeline
        omni.timeline.get_timeline_interface().set_current_time(0.0)

        self._stage = omni.usd.get_context().get_stage()

    async def tearDown(self):
        await omni.usd.get_context().new_stage_async()
        rep.orchestrator.stop()

    def test_docstrings(self):
        """Test module docstring examples"""
        failures, test_counts = doctest.testmod(rep.trigger)
        if failures:
            self.fail(f"Encountered {failures} failures in {test_counts} tests.")

    async def test_on_condition_partial(self):
        def condition_fn(prim_paths, threshold=0.0):
            import omni.usd
            from pxr import UsdGeom

            stage = omni.usd.get_context().get_stage()
            up_axis = UsdGeom.GetStageUpAxis(stage)
            op = "xformOp:translate"
            idx = 1 if up_axis == "Y" else 2
            for prim_path in prim_paths:
                prim = stage.GetPrimAtPath(str(prim_path))
                if prim.HasAttribute(op) and prim.GetAttribute(op).Get()[idx] < threshold:
                    return True
            return False

        sphere = rep.create.sphere(position=(100.0, 100.0, 100.0))

        # Multi trigger not yet suppported
        # with rep.trigger.on_frame(max_execs=5):
        #     with sphere:
        #         rep.modify.pose(scale=rep.distribution.uniform(0.2, 2.0))

        with rep.trigger.on_condition(partial(condition_fn, prim_paths=sphere.get_output("prims")), max_execs=5):
            with sphere:
                rep.modify.pose(position=(0.0, 50.0, 0.0))

        sphere_prim = sphere.get_output_prims()["prims"][0]

        await rep.orchestrator.step_async()
        self.assertEqual(sphere_prim.GetAttribute("xformOp:translate").Get()[1], 100.0)

        # Now set sphere under threshold to trigger condition
        sphere_prim.GetAttribute("xformOp:translate").Set((100.0, -100.0, 100.0))

        await rep.orchestrator.step_async()
        self.assertEqual(sphere_prim.GetAttribute("xformOp:translate").Get()[1], 50.0)

    async def test_on_condition_callable(self):
        def condition_fn(threshold=0.0):
            import omni.usd
            from pxr import UsdGeom

            stage = omni.usd.get_context().get_stage()
            prim_paths = []
            for prim in stage.Traverse():
                if "Sphere_Xform" in prim.GetName():
                    prim_paths.append(prim.GetPath())
            up_axis = UsdGeom.GetStageUpAxis(stage)
            op = "xformOp:translate"
            idx = 1 if up_axis == "Y" else 2
            for prim_path in prim_paths:
                prim = stage.GetPrimAtPath(str(prim_path))
                if prim.HasAttribute(op) and prim.GetAttribute(op).Get()[idx] < threshold:
                    return True
            return False

        sphere = rep.create.sphere(position=(100.0, 100.0, 100.0))

        # Multi trigger not yet suppported
        # with rep.trigger.on_frame(max_execs=5):
        #     with sphere:
        #         rep.modify.pose(scale=rep.distribution.uniform(0.2, 2.0))

        with rep.trigger.on_condition(condition_fn, max_execs=5):
            with sphere:
                rep.modify.pose(position=(0.0, 50.0, 0.0))

        sphere_prim = sphere.get_output_prims()["prims"][0]

        await rep.orchestrator.step_async()
        self.assertEqual(sphere_prim.GetAttribute("xformOp:translate").Get()[1], 100.0)

        # Now set sphere under threshold to trigger condition
        sphere_prim.GetAttribute("xformOp:translate").Set((100.0, -100.0, 100.0))

        await rep.orchestrator.step_async()
        self.assertEqual(sphere_prim.GetAttribute("xformOp:translate").Get()[1], 50.0)

    async def test_multiple_triggers(self):
        """Test scheduling execs if the node is dependend on two different triggers."""
        camera = rep.create.camera()

        rp = rep.create.render_product(camera=camera, resolution=(512, 512))

        cube = rep.create.cube()
        # sphere = rep.create.sphere()

        with rep.trigger.on_frame(num_frames=10):
            with cube:
                rep.modify.pose(rotation=(0, 90, 0))
                rep.modify.pose_camera_relative(distance=10, camera=camera, render_product=rp)

            # with sphere:
            #     rep.modify.pose(rotation=(0, 90, 0))
            #     rep.modify.pose_camera_relative(distance=20, camera=camera, render_product=rp)

        await rep.orchestrator.step_async()

        write_prim_attr_node = og.Controller().node("/Replicator/SDGPipeline/OgnWritePrimAttribute")
        upstream_node = write_prim_attr_node.get_attribute("inputs:execIn").get_upstream_connections()[0].get_node()

        self.assertEqual(
            upstream_node.get_type_name(),
            "omni.graph.action.RationalTimeSyncGate",
            "Sync gate for write prim attribute's upstream atrributes is not created.",
        )

    async def test_on_time_writer_trigger(self):
        """OnTime trigger should trigger on last frame when attached to an annotator/writer"""
        camera = rep.create.camera(position=(0, 1000, 0), look_at=(0, 0, 0))
        rp = rep.create.render_product(camera=camera, resolution=(512, 512))
        cube = rep.create.cube(pivot=(0, 1, 0), position=(0, 900, 0))
        with cube:
            rep.physics.rigid_body()
        ground = rep.create.plane(position=(0, -200, 0))
        with ground:
            rep.physics.collider()

        rep.modify.timeline(1000.0, modify_type="end_time")

        class DistanceWriter(rep.Writer):
            def __init__(self):
                self.annotators = ["distance_to_image_plane"]
                self.observations = []

            def write(self, data):
                self.observations.append(data["distance_to_image_plane"][256, 256])

        writer = DistanceWriter()
        writer.attach(rp, trigger=rep.trigger.on_time_end(max_execs=4, interval=0.25, rt_subframes=1))

        with rep.trigger.on_time(max_execs=2, interval=0.5, rt_subframes=1):
            with cube:
                rep.modify.pose(position=(0, 900, 0))
                rep.physics.rigid_body(velocity=(0, 0, 0))

        await rep.orchestrator.run_until_complete_async()

        np.testing.assert_allclose(np.array(writer.observations), np.array([1.271, 2.155, 1.271, 2.155]), atol=1e-3)

    async def test_on_custom_event_writer_trigger(self):
        cube = rep.create.cube(rotation=(0.0, 45, 0.0))
        cube_prim = cube.get_output_prims()["prims"][0]

        sequence = [(-10.0, -10.0, -10.0), (1.0, 1.0, 1.0), (2.0, 2.0, 2.0), (3.0, 3.0, 3.0)]

        with rep.trigger.on_custom_event("move_cube"):
            with cube:
                rep.modify.pose(position=rep.distribution.sequence(sequence))

        await rep.orchestrator._orchestrator.start_async()
        await omni.kit.app.get_app().next_update_async()

        # Confirm no trigger activation
        for _ in range(2):
            await omni.kit.app.get_app().next_update_async()
            self.assertEqual(cube_prim.GetAttribute("xformOp:translate").Get()[0], 0.0)

        # Confirm trigger activation
        for i in range(6):
            seq_idx = (i // 2) % len(sequence)
            if i % 2 == 0:
                rep.utils.send_og_event("move_cube")
            await omni.kit.app.get_app().next_update_async()
            self.assertEqual(cube_prim.GetAttribute("xformOp:translate").Get()[0], sequence[seq_idx][0])
