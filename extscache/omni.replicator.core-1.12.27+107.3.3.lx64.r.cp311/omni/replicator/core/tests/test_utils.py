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

import omni.kit.test
import omni.replicator.core as rep
from pxr import Usd


class TestUtils(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        await omni.kit.app.get_app().next_update_async()
        self.distribution = rep.distribution.uniform(lower=10, upper=100, num_samples=20)

    async def test_replicatoritem_get_inputs(self):
        # Test can get correct input attributes
        dist_inputs = self.distribution.get_inputs()
        self.assertEqual(list(dist_inputs.keys()), ["lower", "numSamples", "outputType", "seed", "upper"])

    async def test_replicatoritem_get_outputs(self):
        # Test can get correct output attributes
        dist_outputs = self.distribution.get_outputs()
        self.assertEqual(list(dist_outputs.keys()), ["numSamples", "samples"])

    async def test_replicatoritem_get_input(self):
        # Test can get correct input attribute value
        dist_lower = self.distribution.get_input("lower")
        self.assertAlmostEqual(dist_lower, 10, f"Expected lower bound to be 10, got {dist_lower}.")
        dist_upper = self.distribution.get_input("upper")
        self.assertAlmostEqual(dist_upper, 100, f"Expected upper bound to be 100, got {dist_upper}.")
        dist_num_samples = self.distribution.get_input("numSamples")
        self.assertAlmostEqual(dist_num_samples, 20, f"Expected upper bound to be 20, got {dist_num_samples}.")

    async def test_replicatoritem_set_input(self):
        # Test can get correct input attribute value
        self.distribution.set_input("lower", 11)
        dist_lower = self.distribution.get_input("lower")
        self.assertAlmostEqual(dist_lower, 11, f"Expected lower bound to be 11, got {dist_lower}.")
        self.distribution.set_input("upper", 101)
        dist_upper = self.distribution.get_input("upper")
        self.assertAlmostEqual(dist_upper, 101, f"Expected upper bound to be 101, got {dist_upper}.")
        self.distribution.set_input("numSamples", 21)
        dist_num_samples = self.distribution.get_input("numSamples")
        self.assertAlmostEqual(dist_num_samples, 21, f"Expected upper bound to be 21, got {dist_num_samples}.")

    async def test_replicatoritem_invalid(self):
        with self.assertRaises(ValueError):
            self.distribution.get_input("invalid_name")
        with self.assertRaises(ValueError):
            self.distribution.set_input("invalid_name", 11)
        with self.assertRaises(ValueError):
            self.distribution.get_output("invalid_name")
        with self.assertRaises(TypeError):
            self.distribution.set_input("upper", "invalid_value")
        with self.assertRaises(NotImplementedError):
            self.distribution.set_input("upper", rep.distribution.uniform(0, 10))

    async def test_replicatoritem_get_prims(self):
        cubes = rep.create.cube(count=3, position=rep.distribution.uniform((-100, -100, -100), (100, 100, 100)))
        stage = omni.usd.get_context().get_stage()
        cubes_gt = [
            stage.GetPrimAtPath(p)
            for p in ["/Replicator/Cube_Xform", "/Replicator/Cube_Xform_01", "/Replicator/Cube_Xform_02"]
        ]
        self.assertEqual(cubes.get_output_prims()["prims"], cubes_gt)
        plane = rep.create.plane(scale=10)

        with cubes:
            scatter_node = rep.randomizer.scatter_2d(plane)

        get = rep.get.xform("/Replicator/Cube*")

        await rep.orchestrator.step_async()

        self.assertEqual(scatter_node.get_input_prims()["prims"], cubes_gt)
        self.assertEqual(
            scatter_node.get_input_prims()["surfacePrims"], [stage.GetPrimAtPath("/Replicator/Plane_Xform")]
        )

        # Test get_output_prims
        self.assertEqual(get.get_output_prims()["prims"], cubes_gt)

    async def test_decal_transform_from_normalized_bounds(self):
        """Test that normalized bounds return correct transform values for decal use"""
        await omni.usd.get_context().new_stage_async()
        rep.create.cube(scale=(2.5, 1, 0.75))
        await omni.kit.app.get_app().next_update_async()

        input_norm_vector = (0.5, 0.5, 2)
        additional_rotation = (0, 0, 90)
        scale = (0.2, 0.2, 0.2)
        offset = 0.05

        pos, rot, scl = rep.utils.get_decal_bounds_transform_from_normalized(
            "/Replicator/Cube_Xform", input_norm_vector, offset, additional_rotation, scale
        )

        self.assertEqual(pos, (62.5, 25, 42.5), "Translation not correct!")
        self.assertEqual(rot, (0, 0, 90), "Rotation not correct!")
        self.assertEqual(scl, (0.5, 0.2, 0.15), "Scale not correct!")
