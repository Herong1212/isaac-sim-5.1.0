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

from lib2to3.pgen2 import token

import omni.graph.core as og
import omni.kit
import omni.replicator.core as rep
import omni.usd
from pxr import Gf, UsdShade


class TestOgnSampleOmniPBR(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()

        rep.set_global_seed(1234)

        self._stage = omni.usd.get_context().get_stage()
        self._controller = og.Controller()
        self._graph = self._controller.create_graph("/World/PushGraph")

        await omni.kit.app.get_app().next_update_async()

        self._material_node = self._controller.create_node(
            ("mat_rand", self._graph), "omni.replicator.core.OgnSampleOmniPBR"
        )

        self._material_node_prim = self._stage.GetPrimAtPath(self._material_node.get_prim_path())

    async def tearDown(self):
        await omni.usd.get_context().new_stage_async()

    def _setup(self, num_samples, num_instances, num_prototypes, num_mesh_children, mode):
        targets = []
        num_total = num_instances + num_prototypes
        if mode == "meshes":
            num_total *= 2

        def create_mesh_group(path, num_children):
            self._stage.DefinePrim(path, "Xform")
            for i in range(num_children):
                self._stage.DefinePrim(f"{path}/mesh{i}", "Mesh")

        # Add meshes
        for i in range(num_samples):
            path = f"/prim_{i}"
            create_mesh_group(path, num_mesh_children)
            targets.append(path)

        # Add point instancer
        pi = self._stage.DefinePrim("/PI", "PointInstancer")
        for i in range(num_prototypes):
            path = f"/PI/proto_{i}"
            create_mesh_group(path, num_mesh_children)
            targets.append(path)
            pi.GetRelationship("prototypes").SetTargets([path])
            pi.GetAttribute("protoIndices").Set([0] * num_instances)
            pi.GetAttribute("positions").Set([[0, 0, 0]] * num_instances)

        # Setup relationships
        rep.utils.set_target_prims(self._material_node, "inputs:prims", targets)

        # Set resolved type to token array
        token_array_type = og.Type(og.BaseDataType.TOKEN, 1, 1)
        numerial_type = og.Type(og.BaseDataType.DOUBLE, 1, 1)

        # Set the resolved type of each of the attribute of OgnSampleOmniPBR node.
        self._material_node.get_attribute("inputs:diffuseTexture").set_resolved_type(token_array_type)
        self._material_node.get_attribute("inputs:diffuse").set_resolved_type(numerial_type)
        self._material_node.get_attribute("inputs:metallicTexture").set_resolved_type(token_array_type)
        self._material_node.get_attribute("inputs:metallic").set_resolved_type(numerial_type)
        self._material_node.get_attribute("inputs:roughnessTexture").set_resolved_type(token_array_type)
        self._material_node.get_attribute("inputs:roughness").set_resolved_type(numerial_type)

        # Create distribution
        diffuse_node = self._controller.create_node(
            ("diffuse_uniform", self._graph), "omni.replicator.core.OgnSampleUniform"
        )
        diffuse_node.get_attribute("inputs:numSamples").set(num_total)
        diffuse_node.get_attribute("inputs:lower").set([0.0, 0.0, 0.0])
        diffuse_node.get_attribute("inputs:upper").set([1.0, 1.0, 1.0])
        diffuse_node.get_attribute("outputs:samples").set_resolved_type(numerial_type)

        metallic_node = self._controller.create_node(
            ("metallic_uniform", self._graph), "omni.replicator.core.OgnSampleUniform"
        )
        metallic_node.get_attribute("inputs:numSamples").set(num_total)
        metallic_node.get_attribute("inputs:lower").set(0.0)
        metallic_node.get_attribute("inputs:upper").set(1.0)
        metallic_node.get_attribute("outputs:samples").set_resolved_type(numerial_type)

        roughness_node = self._controller.create_node(
            ("roughness_uniform", self._graph), "omni.replicator.core.OgnSampleUniform"
        )
        roughness_node.get_attribute("inputs:numSamples").set(num_total)
        roughness_node.get_attribute("inputs:lower").set(0.0)
        roughness_node.get_attribute("inputs:upper").set(1.0)
        roughness_node.get_attribute("outputs:samples").set_resolved_type(numerial_type)

        diffuse_texture_node = self._controller.create_node(
            ("diffuse_texture_choice", self._graph), "omni.replicator.core.OgnSampleChoice"
        )
        diffuse_texture_node.get_attribute("inputs:numSamples").set(num_total)
        diffuse_texture_node.get_attribute("inputs:choices").set_resolved_type(token_array_type)
        diffuse_texture_node.get_attribute("inputs:choices").set(rep.example.TEXTURES)
        diffuse_texture_node.get_attribute("outputs:samples").set_resolved_type(token_array_type)

        metallic_texture_node = self._controller.create_node(
            ("metallic_texture_choice", self._graph), "omni.replicator.core.OgnSampleChoice"
        )
        metallic_texture_node.get_attribute("inputs:numSamples").set(num_total)
        metallic_texture_node.get_attribute("inputs:choices").set_resolved_type(token_array_type)
        metallic_texture_node.get_attribute("inputs:choices").set(rep.example.TEXTURES)
        metallic_texture_node.get_attribute("outputs:samples").set_resolved_type(token_array_type)

        roughness_texture_node = self._controller.create_node(
            ("roughness_texture_choice", self._graph), "omni.replicator.core.OgnSampleChoice"
        )
        roughness_texture_node.get_attribute("inputs:numSamples").set(num_total)
        roughness_texture_node.get_attribute("inputs:choices").set_resolved_type(token_array_type)
        roughness_texture_node.get_attribute("inputs:choices").set(rep.example.TEXTURES)
        roughness_texture_node.get_attribute("outputs:samples").set_resolved_type(token_array_type)

        # Connect nodes
        diffuse_node.get_attribute("outputs:samples").connect(self._material_node.get_attribute("inputs:diffuse"), True)
        metallic_node.get_attribute("outputs:samples").connect(
            self._material_node.get_attribute("inputs:metallic"), True
        )
        roughness_node.get_attribute("outputs:samples").connect(
            self._material_node.get_attribute("inputs:roughness"), True
        )
        diffuse_texture_node.get_attribute("outputs:samples").connect(
            self._material_node.get_attribute("inputs:diffuseTexture"), True
        )
        metallic_texture_node.get_attribute("outputs:samples").connect(
            self._material_node.get_attribute("inputs:metallicTexture"), True
        )
        roughness_texture_node.get_attribute("outputs:samples").connect(
            self._material_node.get_attribute("inputs:roughnessTexture"), True
        )

        return targets

    async def test_sample_omnipbr_prims(self):
        """Test sampling material values for meshes."""
        num_samples = 10
        num_prototypes = 5
        num_instances = 100
        num_mesh_children = 2

        targets = self._setup(num_samples, num_instances, num_prototypes, num_mesh_children, mode="prims")
        await omni.kit.app.get_app().next_update_async()

        await self._controller.evaluate(self._graph)

        # VALIDATION
        bound_materials = set()
        queue = list(targets)
        while queue:
            path = queue.pop()
            prim = self._stage.GetPrimAtPath(path)
            material, _ = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()
            shader = UsdShade.Shader(omni.usd.get_shader_from_material(material.GetPrim(), True))
            if material:
                bound_materials.add(str(material.GetPath()))
            children = prim.GetChildren()
            if children:
                queue.extend([str(c.GetPath()) for c in children])

            # FIXME: Requires access to bundle data to compare to actual sampled values
            self.assertNotEqual(shader.GetInput("diffuse_color_constant").Get(), Gf.Vec3f((0.2, 0.2, 0.2)))
            self.assertNotEqual(shader.GetInput("reflection_roughness_constant").Get(), 0.5)
            self.assertNotEqual(shader.GetInput("metallic_constant").Get(), 0.0)

        self.assertEqual(len(bound_materials), num_samples + num_prototypes)

    async def test_sample_omnipbr_meshes(self):
        """Test sampling diffuse color values for meshes."""
        num_samples = 10
        num_prototypes = 5
        num_instances = 100
        num_mesh_children = 2

        self._material_node.get_attribute("inputs:mode").set("meshes")

        prims = self._setup(num_samples, num_instances, num_prototypes, num_mesh_children, mode="meshes")
        target_prims = rep.utils.find_prims(prims, mode="meshes")

        await self._controller.evaluate(self._graph)

        # VALIDATION
        bound_materials = set()
        for prim in target_prims:
            material, _ = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()
            shader = UsdShade.Shader(omni.usd.get_shader_from_material(material.GetPrim(), True))
            if material:
                bound_materials.add(str(material.GetPath()))

            # FIXME: Requires access to bundle data to compare to actual sampled values
            self.assertNotEqual(shader.GetInput("diffuse_color_constant").Get(), Gf.Vec3f((0.2, 0.2, 0.2)))
            self.assertNotEqual(shader.GetInput("reflection_roughness_constant").Get(), 0.5)
            self.assertNotEqual(shader.GetInput("metallic_constant").Get(), 0.0)

        self.assertEqual(len(bound_materials), num_samples * num_mesh_children + num_prototypes * num_mesh_children)
