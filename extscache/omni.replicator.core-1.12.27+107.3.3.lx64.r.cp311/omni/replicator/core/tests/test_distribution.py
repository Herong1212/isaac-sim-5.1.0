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
import sys
import unittest

import carb
import numpy as np
import omni.kit
import omni.kit.test
import omni.replicator.core as rep
import omni.usd


class TestDistribution(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        if os.getenv("ETM_ACTIVE"):
            self.skipTest("skip in ETM to keep tests lean")

        await omni.usd.get_context().new_stage_async()
        await omni.kit.app.get_app().next_update_async()

    async def tearDown(self):
        await rep.orchestrator.stop_async()
        await omni.usd.get_context().new_stage_async()

    async def test_choice_tuple(self):
        with rep.create.cube():
            rep.modify.pose(position=rep.distribution.choice([(10.0, 20.0, 30.0), (40.0, 50.0, 60.0)], seed=10))

        await omni.kit.app.get_app().next_update_async()

        stage = omni.usd.get_context().get_stage()
        cube_xform = stage.GetPrimAtPath("/Replicator/Cube_Xform")
        cube_position = np.array(cube_xform.GetAttribute("xformOp:translate").Get())

        np.testing.assert_allclose(cube_position, np.array((40.0, 50.0, 60.0)), atol=1e-3)

    async def test_choice_tuple_int(self):
        with rep.create.cube():
            rep.modify.pose(position=rep.distribution.choice([(10, 20, 30), (40, 50, 60)], seed=10))

        await omni.kit.app.get_app().next_update_async()

        stage = omni.usd.get_context().get_stage()
        cube_xform = stage.GetPrimAtPath("/Replicator/Cube_Xform")
        cube_position = np.array(cube_xform.GetAttribute("xformOp:translate").Get())

        np.testing.assert_allclose(cube_position, np.array((40.0, 50.0, 60.0)), atol=1e-3)

    async def test_choice_single_float(self):
        seq = [15.0, 5.0]
        with rep.trigger.on_frame(max_execs=5):
            rep.modify.time(rep.distribution.choice(seq, name="value"))

        for i in range(5):
            await rep.orchestrator.step_async()
            self.assertTrue(omni.timeline.get_timeline_interface().get_current_time() in seq)

    async def test_choice_sdf_path(self):
        cube = rep.create.cube(position=(0, 0, 1000))
        sphere = rep.create.sphere(position=(1000, 0, 0))
        prim_sdf_paths = [p.GetPath() for p in cube.get_output_prims()["prims"]] + [
            p.GetPath() for p in sphere.get_output_prims()["prims"]
        ]

        with rep.trigger.on_frame():
            random_prim = rep.distribution.choice(prim_sdf_paths, seed=10)
            camera = rep.create.camera(look_at=random_prim)

        self.assertEqual(random_prim.node.get_type_name(), "omni.replicator.core.OgnSampleChoicePrim")

        await rep.orchestrator.step_async()

        camera_xform = camera.get_output_prims()["prims"][0]
        camera_rotation = np.array(camera_xform.GetAttribute("xformOp:rotateXYZ").Get())

        np.testing.assert_allclose(camera_rotation, np.array((0.0, -90.0, -0.0)), atol=1e-3)

    async def test_choice_string_path(self):
        cube = rep.create.cube(position=(0, 0, 1000))
        sphere = rep.create.sphere(position=(1000, 0, 0))

        prim_sdf_paths = [p.GetPath() for p in cube.get_output_prims()["prims"]] + [
            p.GetPath() for p in sphere.get_output_prims()["prims"]
        ]
        prim_string_paths = [str(p) for p in prim_sdf_paths]

        with rep.trigger.on_frame():
            random_prim = rep.distribution.choice(prim_string_paths, seed=10)
            camera = rep.create.camera(look_at=random_prim)

        self.assertEqual(random_prim.node.get_type_name(), "omni.replicator.core.OgnSampleChoicePrim")

        await rep.orchestrator.step_async()

        camera_xform = camera.get_output_prims()["prims"][0]
        camera_rotation = np.array(camera_xform.GetAttribute("xformOp:rotateXYZ").Get())

        np.testing.assert_allclose(camera_rotation, np.array((0.0, -90.0, -0.0)), atol=1e-3)

    async def test_choice_strings(self):
        string_paths = ["NVIDIA", "RTX", "Omniverse"]

        with rep.trigger.on_frame():
            random_prim = rep.distribution.choice(string_paths, seed=10)

        await rep.orchestrator.step_async()
        self.assertEqual(random_prim.node.get_type_name(), "omni.replicator.core.OgnSampleChoice")
        self.assertEqual(random_prim.get_inputs()["choices"], string_paths)

    async def test_choice_mixed_types(self):
        # Test to make sure assertion is raised on mixed list types
        items = ["NVIDIA", "RTX", "Omniverse", 1080, 10.2]
        with self.assertRaises(ValueError):
            with rep.trigger.on_frame():
                random_prim = rep.distribution.choice(items, seed=10)

    async def test_choice_prims(self):
        cube = rep.create.cube(position=(0, 0, 1000))
        sphere = rep.create.sphere(position=(1000, 0, 0))

        prims = cube.get_output_prims()["prims"] + sphere.get_output_prims()["prims"]

        with rep.trigger.on_frame():
            random_prim = rep.distribution.choice(prims, seed=10)
            camera = rep.create.camera(look_at=random_prim)

        self.assertEqual(random_prim.node.get_type_name(), "omni.replicator.core.OgnSampleChoicePrim")

        await rep.orchestrator.step_async()

        camera_xform = camera.get_output_prims()["prims"][0]
        camera_rotation = np.array(camera_xform.GetAttribute("xformOp:rotateXYZ").Get())

        np.testing.assert_allclose(camera_rotation, np.array((0.0, -90.0, -0.0)), atol=1e-3)

    async def test_choice_prims_replicatoritem(self):
        rep.create.cube(scale=50, position=(0, 0, 1000), as_mesh=False)
        rep.create.sphere(scale=50, position=(1000, 0, 0), as_mesh=False)
        shapes = rep.get.prims(prim_types=["Sphere", "Cube"])
        with rep.trigger.on_frame():
            random_prim = rep.distribution.choice(shapes, seed=10)
            camera = rep.create.camera(look_at=random_prim)

        self.assertEqual(random_prim.node.get_type_name(), "omni.replicator.core.OgnSampleChoicePrim")

        await rep.orchestrator.step_async()

        camera_xform = camera.get_output_prims()["prims"][0]
        camera_rotation = np.array(camera_xform.GetAttribute("xformOp:rotateXYZ").Get())

        np.testing.assert_allclose(camera_rotation, np.array((0.0, -90.0, -0.0)), atol=1e-3)

    async def test_choice_prims_downstream(self):
        """Test that choice prim is connected to a downstream node that modifies the prim"""
        plane = rep.create.plane(visible=False, scale=20)

        cube = rep.create.cube(semantics=[("class", "distractor")])
        sphere = rep.create.sphere(semantics=[("class", "distractor")])
        cone = rep.create.cone(semantics=[("class", "distractor")])

        distractors = rep.get.prims(semantics=[("class", "distractor")])

        with rep.trigger.on_frame(max_execs=10):
            subset = rep.distribution.choice(distractors, num_samples=1, with_replacements=False, seed=10)

            rep.randomizer.scatter_2d(surface_prims=plane, check_for_collisions=True, input_prims=subset, seed=0)

        self.assertEqual(subset.node.get_type_name(), "omni.replicator.core.OgnSampleChoicePrim")

        await rep.orchestrator.step_async()

        cube_xform = cube.get_output_prims()["prims"][0]
        cube_translate = np.array(cube_xform.GetAttribute("xformOp:translate").Get())

        sphere_xform = sphere.get_output_prims()["prims"][0]
        sphere_translate = np.array(sphere_xform.GetAttribute("xformOp:translate").Get())

        cone_xform = cone.get_output_prims()["prims"][0]
        cone_translate = np.array(cone_xform.GetAttribute("xformOp:translate").Get())

        np.testing.assert_allclose(cube_translate, np.array((0.0, 0.0, 0.0)), atol=1e-3)
        np.testing.assert_allclose(sphere_translate, np.array((0.0, 0.0, 0.0)), atol=1e-3)
        np.testing.assert_allclose(cone_translate, np.array((-957.435887, 0.0, 38.819934)), atol=1e-3)

    async def test_choice_prims_invalid_path(self):
        # Confirm invalid paths get converted to strings
        random_prim = rep.distribution.choice(["/INVALID"])
        self.assertEqual(random_prim.node.get_type_name(), "omni.replicator.core.OgnSampleChoice")

    async def test_choice_prims_paths_mix(self):
        cube = rep.create.cube(position=(-500, -500, 0))
        sphere = rep.create.sphere(position=(1000, 0, 0))
        rep.create.cone(scale=50, position=(500, 500, 0), as_mesh=False)
        cones = rep.get.prims(prim_types=["Cone"])

        # Pass in a Usd.Prim, Sdf.Paths and a ReplicatorItem
        prims = cube.get_output_prims()["prims"] + [p.GetPath() for p in sphere.get_output_prims()["prims"]] + [cones]

        with rep.trigger.on_frame():
            random_prim = rep.distribution.choice(prims, seed=1)
            camera = rep.create.camera(look_at=random_prim)

        self.assertEqual(random_prim.node.get_type_name(), "omni.replicator.core.OgnSampleChoicePrim")

        for i in range(6):
            await rep.orchestrator.step_async()

            camera_xform = camera.get_output_prims()["prims"][0]
            camera_rotation = np.array(camera_xform.GetAttribute("xformOp:rotateXYZ").Get())

            # Note: Order is just luck of the seed
            if i < 2:
                # Sphere
                np.testing.assert_allclose(camera_rotation, np.array((0.0, -90.0, -0.0)), atol=1e-3)
            elif i < 4:
                # Cone
                np.testing.assert_allclose(camera_rotation, np.array((0.0, -90.0, 45.0)), atol=1e-3)
            else:
                # Cube
                np.testing.assert_allclose(camera_rotation, np.array((0.0, 90.0, 45.0)), atol=1e-3)

    async def test_sequence_sdf_path(self):
        cube = rep.create.cube(position=(0, 0, 1000))
        sphere = rep.create.sphere(position=(1000, 0, 0))
        prim_sdf_paths = [p.GetPath() for p in cube.get_output_prims()["prims"]] + [
            p.GetPath() for p in sphere.get_output_prims()["prims"]
        ]

        with rep.trigger.on_frame():
            random_prim = rep.distribution.sequence(prim_sdf_paths, seed=10)
            camera = rep.create.camera(look_at=random_prim)

        self.assertEqual(random_prim.node.get_type_name(), "omni.replicator.core.OgnSampleSequencePrim")

        await rep.orchestrator.step_async()
        await rep.orchestrator.step_async()

        camera_xform = camera.get_output_prims()["prims"][0]
        camera_rotation = np.array(camera_xform.GetAttribute("xformOp:rotateXYZ").Get())

        np.testing.assert_allclose(camera_rotation, np.array((0.0, -90.0, -0.0)), atol=1e-3)

    async def test_sequence_string_path(self):
        cube = rep.create.cube(position=(0, 0, 1000))
        sphere = rep.create.sphere(position=(1000, 0, 0))

        prim_sdf_paths = [p.GetPath() for p in cube.get_output_prims()["prims"]] + [
            p.GetPath() for p in sphere.get_output_prims()["prims"]
        ]
        prim_string_paths = [str(p) for p in prim_sdf_paths]

        with rep.trigger.on_frame():
            random_prim = rep.distribution.sequence(prim_string_paths, seed=10)
            camera = rep.create.camera(look_at=random_prim)

        self.assertEqual(random_prim.node.get_type_name(), "omni.replicator.core.OgnSampleSequencePrim")

        await rep.orchestrator.step_async()
        await rep.orchestrator.step_async()

        camera_xform = camera.get_output_prims()["prims"][0]
        camera_rotation = np.array(camera_xform.GetAttribute("xformOp:rotateXYZ").Get())

        np.testing.assert_allclose(camera_rotation, np.array((0.0, -90.0, -0.0)), atol=1e-3)

    async def test_sequence_prims(self):
        cube = rep.create.cube(position=(0, 0, 1000))
        sphere = rep.create.sphere(position=(1000, 0, 0))

        prims = cube.get_output_prims()["prims"] + sphere.get_output_prims()["prims"]

        with rep.trigger.on_frame():
            random_prim = rep.distribution.sequence(prims, seed=10)
            camera = rep.create.camera(look_at=random_prim)

        self.assertEqual(random_prim.node.get_type_name(), "omni.replicator.core.OgnSampleSequencePrim")

        await rep.orchestrator.step_async()
        await rep.orchestrator.step_async()

        camera_xform = camera.get_output_prims()["prims"][0]
        camera_rotation = np.array(camera_xform.GetAttribute("xformOp:rotateXYZ").Get())

        np.testing.assert_allclose(camera_rotation, np.array((0.0, -90.0, -0.0)), atol=1e-3)

    async def test_sequence_prims_paths_mix(self):
        cube = rep.create.cube(position=(0, 0, 1000))
        sphere = rep.create.sphere(position=(1000, 0, 0))

        prims = cube.get_output_prims()["prims"] + [p.GetPath() for p in sphere.get_output_prims()["prims"]]

        with rep.trigger.on_frame():
            random_prim = rep.distribution.sequence(prims, seed=10)
            camera = rep.create.camera(look_at=random_prim)

        self.assertEqual(random_prim.node.get_type_name(), "omni.replicator.core.OgnSampleSequencePrim")

        await rep.orchestrator.step_async()
        await rep.orchestrator.step_async()

        camera_xform = camera.get_output_prims()["prims"][0]
        camera_rotation = np.array(camera_xform.GetAttribute("xformOp:rotateXYZ").Get())

        np.testing.assert_allclose(camera_rotation, np.array((0.0, -90.0, -0.0)), atol=1e-3)

    async def test_sequence_prims_replicator_item(self):
        cube = rep.create.cube(position=(0, 0, 1000))
        sphere = rep.create.sphere(position=(1000, 0, 0))

        prim_sdf_paths = [p.GetPath() for p in cube.get_output_prims()["prims"]] + [
            p.GetPath() for p in sphere.get_output_prims()["prims"]
        ]
        prims = rep.create.group(prim_sdf_paths)

        with rep.trigger.on_frame():
            random_prim = rep.distribution.sequence(prims, seed=10)
            camera = rep.create.camera(look_at=random_prim)

        self.assertEqual(random_prim.node.get_type_name(), "omni.replicator.core.OgnSampleSequencePrim")

        await rep.orchestrator.step_async()
        await rep.orchestrator.step_async()

        camera_xform = camera.get_output_prims()["prims"][0]
        camera_rotation = np.array(camera_xform.GetAttribute("xformOp:rotateXYZ").Get())

        np.testing.assert_allclose(camera_rotation, np.array((0.0, -90.0, -0.0)), atol=1e-3)

    async def test_sequence_unordered(self):
        cube = rep.create.cube()

        sequence_positions = [
            (0, 0, 0),
            (10, 10, 10),
            (20, 20, 20),
            (30, 30, 30),
            (40, 40, 40),
            (50, 50, 50),
            (60, 60, 60),
            (70, 70, 70),
            (80, 80, 80),
            (90, 90, 90),
        ]

        with rep.trigger.on_frame(max_execs=20):
            with cube:
                rep.modify.pose(position=rep.distribution.sequence(sequence_positions, ordered=False))

        await omni.kit.app.get_app().next_update_async()

        stage = omni.usd.get_context().get_stage()
        cube_xform = stage.GetPrimAtPath("/Replicator/Cube_Xform")

        # Test for the first 5 iterations, the order of the positions is not the same as origin one.
        unordered_positions = []
        for i in range(10):
            await rep.orchestrator.step_async()
            unordered_positions.append(np.array(cube_xform.GetAttribute("xformOp:translate").Get()))

        assert not np.allclose(np.array(sequence_positions), np.array(unordered_positions))

        # Test for the next 5 iterations, it will re-sample again
        unordered_positions_1 = []
        for i in range(10):
            await rep.orchestrator.step_async()
            unordered_positions_1.append(np.array(cube_xform.GetAttribute("xformOp:translate").Get()))

        assert not np.allclose(np.array(sequence_positions), np.array(unordered_positions_1))
        assert not np.allclose(np.array(unordered_positions), np.array(unordered_positions_1))

    async def test_sequence_ordered(self):
        cube = rep.create.cube()

        sequence_positions = [(0, 0, 0), (10, 10, 10), (20, 20, 20), (30, 30, 30), (40, 40, 40)]

        with rep.trigger.on_frame(max_execs=10):
            with cube:
                rep.modify.pose(position=rep.distribution.sequence(sequence_positions, ordered=True))

        await omni.kit.app.get_app().next_update_async()

        stage = omni.usd.get_context().get_stage()
        cube_xform = stage.GetPrimAtPath("/Replicator/Cube_Xform")

        # Test for the first 5 iterations
        ordered_positions = []
        for i in range(5):
            await rep.orchestrator.step_async()
            ordered_positions.append(np.array(cube_xform.GetAttribute("xformOp:translate").Get()))

        np.testing.assert_allclose(np.array(sequence_positions), np.array(ordered_positions))

        # Test for the next 5 iterations, it will re-sample again
        ordered_positions_1 = []
        for i in range(5):
            await rep.orchestrator.step_async()
            ordered_positions_1.append(np.array(cube_xform.GetAttribute("xformOp:translate").Get()))

        np.testing.assert_allclose(np.array(sequence_positions), np.array(ordered_positions))

    async def test_uniform_save_open_repeatability(self):
        cube = rep.create.cube()

        with rep.trigger.on_frame(max_execs=5):
            with cube:
                rep.modify.attribute(
                    "xformOp:translate", rep.distribution.uniform((0, 0, 0), (100, 100, 100), seed=10), "double3"
                )

        await omni.kit.app.get_app().next_update_async()

        file_path = carb.tokens.get_tokens_interface().resolve("${temp}/test_uniform_save_open.usd")
        result = await omni.usd.get_context().save_as_stage_async(file_path)

        await omni.usd.get_context().new_stage_async()
        await omni.kit.app.get_app().next_update_async()

        omni.usd.get_context().open_stage(file_path)
        await omni.kit.app.get_app().next_update_async()

        await rep.orchestrator.step_async()
        await rep.orchestrator.step_async()

        stage = omni.usd.get_context().get_stage()
        cube_xform = stage.GetPrimAtPath("/Replicator/Cube_Xform")
        cube_position = np.array(cube_xform.GetAttribute("xformOp:translate").Get())

        np.testing.assert_allclose(cube_position, np.array([14.928212, 51.280462, 13.59196]), atol=1e-3)

    async def test_normal_save_open_repeatability(self):
        cube = rep.create.cube()

        with rep.trigger.on_frame(max_execs=5):
            with cube:
                rep.modify.attribute(
                    "xformOp:rotateXYZ", rep.distribution.normal(mean=(90, 90, 90), std=(1, 1, 1), seed=10), "double3"
                )

        await omni.kit.app.get_app().next_update_async()

        file_path = carb.tokens.get_tokens_interface().resolve("${temp}/test_normal_save_open.usd")
        result = await omni.usd.get_context().save_as_stage_async(file_path)

        await omni.usd.get_context().new_stage_async()
        await omni.kit.app.get_app().next_update_async()

        omni.usd.get_context().open_stage(file_path)
        await omni.kit.app.get_app().next_update_async()

        await rep.orchestrator.step_async()
        await rep.orchestrator.step_async()

        stage = omni.usd.get_context().get_stage()
        cube_xform = stage.GetPrimAtPath("/Replicator/Cube_Xform")
        cube_rotation = np.array(cube_xform.GetAttribute("xformOp:rotateXYZ").Get())

        np.testing.assert_allclose(cube_rotation, np.array([90.266975, 89.75142, 90.12648]), atol=1e-3)

    async def test_log_uniform_save_open_repeatability(self):
        cube = rep.create.cube()

        with rep.trigger.on_frame(max_execs=5):
            with cube:
                rep.modify.attribute(
                    "xformOp:translate", rep.distribution.log_uniform((1, 1, 1), (100, 100, 100), seed=10), "double3"
                )

        await omni.kit.app.get_app().next_update_async()

        file_path = carb.tokens.get_tokens_interface().resolve("${temp}/test_log_uniform_save_open.usd")
        result = await omni.usd.get_context().save_as_stage_async(file_path)

        await omni.usd.get_context().new_stage_async()
        await omni.kit.app.get_app().next_update_async()

        omni.usd.get_context().open_stage(file_path)
        await omni.kit.app.get_app().next_update_async()

        await rep.orchestrator.step_async()
        await rep.orchestrator.step_async()

        stage = omni.usd.get_context().get_stage()
        cube_xform = stage.GetPrimAtPath("/Replicator/Cube_Xform")
        cube_position = np.array(cube_xform.GetAttribute("xformOp:translate").Get())

        np.testing.assert_allclose(cube_position, np.array([1.988677, 10.60740735, 1.86998969]), atol=1e-3)

    async def test_sequence_reset(self):
        sequence = [[float(i)] * 3 for i in range(10)]

        cube = rep.create.cube()
        with rep.trigger.on_frame():
            with cube:
                rep.modify.pose(position=rep.distribution.sequence(sequence))

        cube_xform = cube.get_output_prims()["prims"][0]

        async def test_steps():
            steps = 2
            for step in range(steps):
                await rep.orchestrator.step_async()

            cube_position = np.array(cube_xform.GetAttribute("xformOp:translate").Get())
            np.testing.assert_allclose(cube_position, sequence[step])

        await test_steps()
        await rep.orchestrator.stop_async()
        await test_steps()

    async def test_uniform_reuse(self):
        """Verify that the uniform distribution samples are reused when the same distribution is used multiple times."""
        cones = rep.create.cone(count=10)
        cubes = rep.create.cube(count=10)

        with rep.trigger.on_frame():
            position_y = rep.distribution.uniform(0, 1000)
            with cones:
                rep.modify.pose(position_y=position_y)
            with cubes:
                rep.modify.pose(position_y=position_y)

        for _ in range(2):
            await rep.orchestrator.step_async()
            # Check that the samples are only in the top half of the sphere
            pos_y = position_y.get_output("samples")
            for i, s in enumerate(cones.get_output_prims()["prims"]):
                world_position = rep.functional.utils.get_world_transform(s).GetTranslation()
                self.assertAlmostEqual(world_position[1], pos_y[i])
            for i, s in enumerate(cubes.get_output_prims()["prims"]):
                world_position = rep.functional.utils.get_world_transform(s).GetTranslation()
                self.assertAlmostEqual(world_position[1], pos_y[i])

    async def test_choice_distribution_replicatoritem(self):
        """Test that the choice of distribution replicator item is working."""
        rep.set_global_seed(12)

        cube = rep.create.cube(count=5)
        cones = rep.create.cone(count=5)

        # For testing a large number of inputs
        distributions_cubes = [rep.distribution.uniform((i * 100, 0, 0), ((i + 1) * 100, 0, 0)) for i in range(11)]
        distributions_cones = [
            rep.distribution.uniform((0, 0, 0), (100, 0, 0)),
            rep.distribution.uniform((400, 0, 0), (500, 0, 0)),
        ]
        with rep.trigger.on_frame():
            with cube:
                rep.modify.pose(position=rep.distribution.sequence(distributions_cubes))
            with cones:
                rep.modify.pose(position=rep.distribution.choice(distributions_cones))

        for i in range(3):  #  only test 3 steps to keep test fast
            await rep.orchestrator.step_async()

            cube_prims = cube.get_output_prims()["prims"]
            cone_prims = cones.get_output_prims()["prims"]
            for cube_prim in cube_prims:
                translation = cube_prim.GetAttribute("xformOp:translate").Get()
                translation_x = translation[0]
                expected_range = (i * 100, (i + 1) * 100)
                self.assertGreaterEqual(translation_x, expected_range[0])
                self.assertGreater(expected_range[1], translation_x)

            for cone_prim in cone_prims:
                translation = cone_prim.GetAttribute("xformOp:translate").Get()
                translation_x = translation[0]
                self.assertTrue(0 < translation_x < 100 or 400 < translation_x < 500)

    async def test_sequence_stride(self):
        visibility_sequence = [(True, False, False), (False, True, False), (False, False, True)]
        torus = rep.create.torus(position=(200, 0, 200))
        sphere = rep.create.sphere(position=(0, 0, 200))
        cylinder = rep.create.cylinder(position=(-200, 50, -200))
        group = rep.create.group([torus, sphere, cylinder])

        await omni.kit.app.get_app().next_update_async()
        with rep.trigger.on_frame(max_execs=3):
            with group:
                rep.modify.visibility(rep.distribution.sequence(visibility_sequence))
        await omni.kit.app.get_app().next_update_async()

        # First frame
        await rep.orchestrator.step_async()
        for i, prim in enumerate(group.get_output_prims()["prims"]):
            visib = "invisible"
            if visibility_sequence[0][i] is True:
                visib = "inherited"
            prim_visib = prim.GetAttribute("visibility").Get()
            self.assertEqual(prim_visib, visib)

        # Second frame
        await rep.orchestrator.step_async()
        for i, prim in enumerate(group.get_output_prims()["prims"]):
            visib = "invisible"
            if visibility_sequence[1][i] is True:
                visib = "inherited"
            prim_visib = prim.GetAttribute("visibility").Get()
            self.assertEqual(prim_visib, visib)

        # Third frame
        await rep.orchestrator.step_async()
        for i, prim in enumerate(group.get_output_prims()["prims"]):
            visib = "invisible"
            if visibility_sequence[2][i] is True:
                visib = "inherited"
            prim_visib = prim.GetAttribute("visibility").Get()
            self.assertEqual(prim_visib, visib)
