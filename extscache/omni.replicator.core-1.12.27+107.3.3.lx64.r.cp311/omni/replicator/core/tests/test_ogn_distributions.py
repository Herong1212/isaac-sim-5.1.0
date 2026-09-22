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

import numpy as np
import omni.graph.core as og
import omni.kit
import omni.kit.commands
import omni.replicator.core as rep
import omni.usd
from omni.replicator.core import utils
from omni.usd._impl.utils import get_prim_at_path
from pxr import Gf, Sdf


class TestOgnDistribution(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        rep.set_global_seed(1234)

        self._stage = omni.usd.get_context().get_stage()
        self._controller = og.Controller()
        self._graph = self._controller.create_graph("/World/PushGraph")

        # Define node dtype
        base_type = og.BaseDataType.DOUBLE
        sample_type = og.Type(base_type, 1, 1)

        self._uniform_node = self._controller.create_node(
            ("uniform", self._graph), "omni.replicator.core.OgnSampleUniform"
        )
        self._normal_node = self._controller.create_node(
            ("normal", self._graph), "omni.replicator.core.OgnSampleNormal"
        )
        self._choice_node = self._controller.create_node(
            ("choice", self._graph), "omni.replicator.core.OgnSampleChoice"
        )
        self._sequence_node = self._controller.create_node(
            ("sequence", self._graph), "omni.replicator.core.OgnSampleSequence"
        )
        self._assign_node = self._controller.create_node(
            ("assign", self._graph), "omni.replicator.core.OgnWritePrimAttribute"
        )
        self._log_uniform_node = self._controller.create_node(
            ("log_uniform", self._graph), "omni.replicator.core.OgnSampleLogUniform"
        )
        self._assign_node.get_attribute("inputs:attributeType").set("float")
        self._assign_node_prim = self._stage.GetPrimAtPath(self._assign_node.get_prim_path())

    async def tearDown(self):
        await omni.usd.get_context().new_stage_async()

    async def test_uniform_distribution(self):
        """Test that values are distributed uniformly."""
        prims = list()
        prim_paths = list()
        num_samples = 500

        for i in range(num_samples):
            prim_path = f"/sample{i+1}"
            omni.kit.commands.execute("CreatePrimCommand", prim_path=prim_path, prim_type="Cube")
            prim = self._stage.GetPrimAtPath(prim_path)
            prim.CreateAttribute("testAttribute", Sdf.ValueTypeNames.Float, False).Set(-1)
            prim_paths.append(prim_path)
            prims.append(prim)

        lower = np.array([100.0])
        upper = np.array([1000.0])
        mean = (upper + lower) / 2
        std = (upper - lower) / np.sqrt(12)

        self._uniform_node.get_attribute("inputs:seed").set(42)
        self._uniform_node.get_attribute("inputs:numSamples").set(num_samples)
        self._uniform_node.get_attribute("inputs:lower").set(lower)
        self._uniform_node.get_attribute("inputs:upper").set(upper)

        self._add_relationship_target("inputs:prims", prim_paths)

        self._controller.connect(
            self._uniform_node.get_attribute("outputs:samples"), self._assign_node.get_attribute("inputs:values")
        )

        self._assign_node.get_attribute("inputs:attribute").set("testAttribute")
        await self._controller.evaluate(self._graph)

        attribute_vals = np.array([np.array(prim.GetAttribute("testAttribute").Get()).reshape(-1) for prim in prims])

        self.assertTrue(np.all(np.logical_and(attribute_vals >= lower, attribute_vals <= upper)))
        self.assertTrue(np.all(np.isclose(np.mean(attribute_vals), mean, rtol=0.02)))
        self.assertTrue(np.all(np.isclose(np.std(attribute_vals), std, rtol=0.05)))

    async def test_normal_distribution(self):
        """Test that values are distributed normally."""
        prims = list()
        prim_paths = list()
        num_samples = 500

        for i in range(num_samples):
            prim_path = f"/sample{i+1}"
            omni.kit.commands.execute("CreatePrimCommand", prim_path=prim_path, prim_type="Cube")
            prim = self._stage.GetPrimAtPath(prim_path)
            prim.CreateAttribute("testAttribute", Sdf.ValueTypeNames.Float, False).Set(-1)
            prim_paths.append(prim_path)
            prims.append(prim)

        mean = np.array([500.0])
        std = np.array([10.0])

        self._normal_node.get_attribute("inputs:seed").set(42)
        self._normal_node.get_attribute("inputs:numSamples").set(num_samples)
        self._normal_node.get_attribute("inputs:mean").set(mean)
        self._normal_node.get_attribute("inputs:std").set(std)

        self._add_relationship_target("inputs:prims", prim_paths)

        self._controller.connect(
            self._normal_node.get_attribute("outputs:samples"), self._assign_node.get_attribute("inputs:values")
        )

        self._assign_node.get_attribute("inputs:attribute").set("testAttribute")
        await self._controller.evaluate(self._graph)

        attribute_vals = np.array([np.array(prim.GetAttribute("testAttribute").Get()).reshape(-1) for prim in prims])

        np.testing.assert_allclose(np.mean(attribute_vals), mean, rtol=0.01)
        np.testing.assert_allclose(np.std(attribute_vals), std, rtol=0.1)

    async def test_sequential_sampling(self):
        """Test that values are sampled sequentially"""
        prim_path = "/World/Cube"
        material_path = "/World/mtl_Cube"
        material_shader_path = "/World/mtl_Cube/Shader"

        stage = omni.usd.get_context().get_stage()

        omni.kit.commands.execute("CreatePrim", prim_path=prim_path, prim_type="Cube")
        omni.kit.commands.execute("CreatePreviewSurfaceMaterialPrim", mtl_path=material_path)
        omni.kit.commands.execute("BindMaterial", prim_path=prim_path, material_path=material_path)

        prim = stage.GetPrimAtPath(material_shader_path)
        prim.CreateAttribute(
            "inputs:diffuseColor", Sdf.ValueTypeNames.Color3f, False
        )  # Diffuse color attribute no longer created in Kit 107
        created_color = prim.GetAttribute("inputs:diffuseColor").Get()

        # Setup the graph
        color_sequence = [(2.0, 0.0, 0.0), (2.0, 2.0, 0.0), (0.0, 0.0, 2.0)]  # Red, Yellow, Blue

        self._sequence_node.get_attribute("inputs:items").set_resolved_type(og.Type(og.BaseDataType.FLOAT, 3, 1))
        self._sequence_node.get_attribute("inputs:items").set(color_sequence)

        self._add_relationship_target("inputs:prims", [material_shader_path])

        self._controller.connect(
            self._sequence_node.get_attribute("outputs:samples"), self._assign_node.get_attribute("inputs:values")
        )
        self._assign_node.get_attribute("inputs:attribute").set("inputs:diffuseColor")

        await self._controller.evaluate(self._graph)

        # Assert values are correct after each evaluation
        new_color = stage.GetPrimAtPath(material_shader_path).GetAttribute("inputs:diffuseColor").Get()
        self.assertNotEqual(created_color, new_color)
        self.assertEqual(new_color, color_sequence[0])

        await self._controller.evaluate(self._graph)

        new_color = stage.GetPrimAtPath(material_shader_path).GetAttribute("inputs:diffuseColor").Get()
        self.assertNotEqual(created_color, new_color)
        self.assertEqual(new_color, color_sequence[1])

        await self._controller.evaluate(self._graph)

        new_color = stage.GetPrimAtPath(material_shader_path).GetAttribute("inputs:diffuseColor").Get()
        self.assertNotEqual(created_color, new_color)
        self.assertEqual(new_color, color_sequence[2])

        # Assert that the sample loops back to the first value
        await self._controller.evaluate(self._graph)

        new_color = stage.GetPrimAtPath(material_shader_path).GetAttribute("inputs:diffuseColor").Get()
        self.assertNotEqual(created_color, new_color)
        self.assertEqual(new_color, color_sequence[0])

    async def test_sequence_float3(self):
        rep.set_global_seed(1234)
        sequence = [(3.4, 3.4, 3.4), (10.3, 10.3, 10.3), (23.2, 23.2, 23.2)]
        with rep.trigger.on_frame():
            rep.create.sphere(position=rep.distribution.sequence(sequence))

        await omni.kit.app.get_app().next_update_async()

        for i in range(len(sequence)):
            rep.orchestrator.preview()
            await omni.kit.app.get_app().next_update_async()

            sphere_prim = self._stage.GetPrimAtPath("/Replicator/Sphere_Xform")
            translation = sphere_prim.GetAttribute("xformOp:translate").Get()

            # Lost some precision after passing through more nodes.
            np.testing.assert_allclose(np.array(translation), np.array(sequence[i]))

    def _add_relationship_target(self, attribute, prim_paths):
        for target in prim_paths:
            omni.kit.commands.execute(
                "AddRelationshipTarget", relationship=self._assign_node_prim.GetAttribute(attribute), target=target
            )

    async def test_choice_distribution(self):
        """Test the choice distribution."""
        prims = list()
        prim_paths = list()
        num_samples = 500

        for i in range(num_samples):
            prim_path = f"/sample{i+1}"
            omni.kit.commands.execute("CreatePrimCommand", prim_path=prim_path, prim_type="Cube")
            prim = self._stage.GetPrimAtPath(prim_path)
            prim.CreateAttribute("testAttribute", Sdf.ValueTypeNames.Float, False).Set(-1)
            prim_paths.append(prim_path)
            prims.append(prim)

        choices = np.random.uniform(0, 100, size=1000)
        weights = np.ones(1000)

        choice_array_node = self._controller.create_node(("choice_arr", self._graph), "omni.replicator.core.OgnArray")
        choice_array_node.get_attribute("inputs:arrayType").set("float")

        self._choice_node.get_attribute("inputs:seed").set(42)
        self._choice_node.get_attribute("inputs:numSamples").set(num_samples)
        self._controller.connect(
            choice_array_node.get_attribute("inputs:array"), self._choice_node.get_attribute("inputs:choices")
        )
        choice_array_node.get_attribute("inputs:array").set(choices)

        self._choice_node.get_attribute("inputs:weights").set(weights)

        self._add_relationship_target("inputs:prims", prim_paths)

        self._controller.connect(
            self._choice_node.get_attribute("outputs:samples"), self._assign_node.get_attribute("inputs:values")
        )

        self._assign_node.get_attribute("inputs:attribute").set("testAttribute")
        await self._controller.evaluate(self._graph)

        attribute_vals = np.array([np.array(prim.GetAttribute("testAttribute").Get()).reshape(-1) for prim in prims])

        self.assertTrue(np.all(np.logical_and(attribute_vals >= 0, attribute_vals <= 100)))

    async def test_choice_api_float3(self):
        rep.set_global_seed(1234)
        choices = [(3.4, 3.4, 3.4), (10.3, 10.3, 10.3), (23.2, 23.2, 23.2)]
        rep.create.sphere(position=rep.distribution.choice(choices))
        await omni.kit.app.get_app().next_update_async()

        sphere_prim = self._stage.GetPrimAtPath("/Replicator/Sphere_Xform")
        translation = sphere_prim.GetAttribute("xformOp:translate").Get()

        # Lost some precision after passing through more nodes.
        np.testing.assert_allclose(np.array(translation), np.array(choices[2]))

    async def test_choice_api_str(self):
        # Test makes sure no errors are generated
        # TODO improve this test case
        rep.set_global_seed(1234)
        choices = ["Item1", "Item2", "Item3"]
        rep.distribution.choice(choices)

    async def test_choice_api_bool(self):
        # Test makes sure no errors are generated
        # TODO improve this test case
        rep.set_global_seed(1234)
        choices = [True, True, False]
        rep.distribution.choice(choices)

    async def test_choice_api_int(self):
        # Test makes sure no errors are generated
        # TODO improve this test case
        rep.set_global_seed(1234)
        choices = [1, 2, 3]
        rep.distribution.choice(choices)

    async def test_distribution_combine(self):
        position = rep.distribution.combine([rep.distribution.uniform((0, 0), (100, 100), seed=10), 50.0])

        rotation = rep.distribution.combine(
            [rep.distribution.normal(mean=90, std=1, seed=10), rep.distribution.uniform((0), (90), seed=10), 45.0]
        )

        scale = 10

        cube = rep.create.cube(position=position, rotation=rotation, scale=scale)

        await omni.kit.app.get_app().next_update_async()

        cube_prim = cube.get_output_prims()["prims"][0]
        cube_position = np.array(cube_prim.GetAttribute("xformOp:translate").Get())

        np.testing.assert_allclose(cube_position, np.array([95.60017096, 20.76818101, 50.0]))

        cube_rotation = np.array(cube_prim.GetAttribute("xformOp:rotateXYZ").Get())
        np.testing.assert_allclose(cube_rotation, np.array([88.896, 86.040, 45.0]), rtol=1e-5)

        cube_scale = np.array(cube_prim.GetAttribute("xformOp:scale").Get())

        np.testing.assert_allclose(cube_scale, np.array([10, 10, 10]))

    async def test_distribution_combine_int(self):
        """Test if the numerical value is a int."""
        position = rep.distribution.combine([rep.distribution.uniform((0, 0), (100, 100), seed=10), 131])

        rotation = rep.distribution.combine(
            [rep.distribution.normal(mean=90, std=1, seed=10), rep.distribution.uniform((0), (90), seed=10), 44]
        )

        scale = 10

        cube = rep.create.cube(position=position, rotation=rotation, scale=scale)

        await omni.kit.app.get_app().next_update_async()

        cube_prim = cube.get_output_prims()["prims"][0]
        cube_position = np.array(cube_prim.GetAttribute("xformOp:translate").Get())

        np.testing.assert_allclose(cube_position, np.array([95.60017096, 20.76818101, 131.0]))

        cube_rotation = np.array(cube_prim.GetAttribute("xformOp:rotateXYZ").Get())
        np.testing.assert_allclose(cube_rotation, np.array([88.896, 86.040, 44.0]), rtol=1e-5)

        cube_scale = np.array(cube_prim.GetAttribute("xformOp:scale").Get())

        np.testing.assert_allclose(cube_scale, np.array([10, 10, 10]))

    async def test_log_uniform_distribution(self):
        """Test that values are distributed log uniformly."""

        prims = list()
        prim_paths = list()
        num_samples = 500

        for i in range(num_samples):
            prim_path = f"/sample{i+1}"
            omni.kit.commands.execute("CreatePrimCommand", prim_path=prim_path, prim_type="Cube")
            prim = self._stage.GetPrimAtPath(prim_path)
            prim.CreateAttribute("testAttribute", Sdf.ValueTypeNames.Float, False).Set(-1)
            prim_paths.append(prim_path)
            prims.append(prim)

        lower = np.array([100.0])
        upper = np.array([1000.0])

        log_frac = np.log(upper / lower)
        mean = (upper - lower) / log_frac
        variance = (upper**2 - lower**2) / (2 * log_frac) - ((upper - lower) / log_frac) ** 2
        std = np.sqrt(variance)

        self._log_uniform_node.get_attribute("inputs:seed").set(42)
        self._log_uniform_node.get_attribute("inputs:numSamples").set(num_samples)
        self._log_uniform_node.get_attribute("inputs:lower").set(lower)
        self._log_uniform_node.get_attribute("inputs:upper").set(upper)

        self._add_relationship_target("inputs:prims", prim_paths)

        self._controller.connect(
            self._log_uniform_node.get_attribute("outputs:samples"), self._assign_node.get_attribute("inputs:values")
        )

        self._assign_node.get_attribute("inputs:attribute").set("testAttribute")
        await self._controller.evaluate(self._graph)

        attribute_vals = np.array([np.array(prim.GetAttribute("testAttribute").Get()).reshape(-1) for prim in prims])

        self.assertTrue(np.all(np.logical_and(attribute_vals >= lower, attribute_vals <= upper)))
        self.assertTrue(np.all(np.isclose(np.mean(attribute_vals), mean, rtol=0.02)))
        self.assertTrue(np.all(np.isclose(np.std(attribute_vals), std, rtol=0.05)))
