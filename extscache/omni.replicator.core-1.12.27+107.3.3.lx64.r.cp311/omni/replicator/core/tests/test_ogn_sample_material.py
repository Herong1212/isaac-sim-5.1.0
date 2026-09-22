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

import numpy as np
import omni.graph.core as og
import omni.kit
import omni.replicator.core as rep
import omni.usd
from pxr import UsdGeom


class TestOgnSampleMaterial(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        rep.set_global_seed(1234)

        self._stage = omni.usd.get_context().get_stage()
        self._controller = og.Controller()
        self._graph = self._controller.create_graph("/World/PushGraph")

        self._material_node = self._controller.create_node(
            ("mat_rand", self._graph), "omni.replicator.core.OgnSampleMaterial"
        )
        self._material_node.get_attribute("inputs:useMaterialPrim").set(True)
        self._material_node_prim = self._stage.GetPrimAtPath(self._material_node.get_prim_path())

    async def tearDown(self):
        await omni.usd.get_context().new_stage_async()

    async def test_1_geom_1_material(self):
        """Test sampling one material for one mesh."""

        mtl_name = "OmniGlass"
        omni.kit.commands.execute("CreateAndBindMdlMaterialFromLibrary", mdl_name=f"{mtl_name}.mdl", mtl_name=mtl_name)
        material_path = f"/Looks/{mtl_name}"
        material = self._stage.GetPrimAtPath(material_path)

        _, sample_prim_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Sphere")
        sample_prim = self._stage.GetPrimAtPath(sample_prim_path)

        # Setup relationships
        for target in [sample_prim_path]:
            omni.kit.commands.execute(
                "AddRelationshipTarget",
                relationship=self._material_node_prim.GetAttribute("inputs:prims"),
                target=target,
            )
        for target in [material_path]:
            omni.kit.commands.execute(
                "AddRelationshipTarget",
                relationship=self._material_node_prim.GetAttribute("inputs:materialPrim"),
                target=target,
            )

        await self._controller.evaluate(self._graph)

        self.assertTrue(sample_prim.GetRelationship("material:binding").GetTargets()[0] == material_path)

    async def test_1_geom_2_material(self):
        """Test sampling two materials for one mesh."""

        mtl_name_1 = "OmniGlass"
        omni.kit.commands.execute(
            "CreateAndBindMdlMaterialFromLibrary", mdl_name=f"{mtl_name_1}.mdl", mtl_name=mtl_name_1
        )
        material_path_1 = f"/Looks/{mtl_name_1}"
        material_1 = self._stage.GetPrimAtPath(material_path_1)
        mtl_name_2 = "OmniPBR"
        omni.kit.commands.execute(
            "CreateAndBindMdlMaterialFromLibrary", mdl_name=f"{mtl_name_2}.mdl", mtl_name=mtl_name_2
        )
        material_path_2 = f"/Looks/{mtl_name_2}"
        material_2 = self._stage.GetPrimAtPath(material_path_2)

        _, sample_prim_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Sphere")
        sample_prim = self._stage.GetPrimAtPath(sample_prim_path)

        # Setup relationships
        for target in [sample_prim_path]:
            omni.kit.commands.execute(
                "AddRelationshipTarget",
                relationship=self._material_node_prim.GetAttribute("inputs:prims"),
                target=target,
            )
        for target in [material_path_1, material_path_2]:
            omni.kit.commands.execute(
                "AddRelationshipTarget",
                relationship=self._material_node_prim.GetAttribute("inputs:materialPrim"),
                target=target,
            )

        self._material_node.get_attribute("inputs:seed").set(1410)
        await self._controller.evaluate(self._graph)

        has_material = (
            sample_prim.GetRelationship("material:binding").GetTargets()[0] == material_path_1
            or sample_prim.GetRelationship("material:binding").GetTargets()[0] == material_path_2
        )

        self.assertTrue(has_material)

    async def test_2_geom_1_material(self):
        """Test sampling one material for two meshes."""

        mtl_name = "OmniGlass"
        omni.kit.commands.execute("CreateAndBindMdlMaterialFromLibrary", mdl_name=f"{mtl_name}.mdl", mtl_name=mtl_name)
        material_path = f"/Looks/{mtl_name}"
        material = self._stage.GetPrimAtPath(material_path)

        _, sample_prim_path_1 = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Sphere")
        sample_prim_1 = self._stage.GetPrimAtPath(sample_prim_path_1)
        _, sample_prim_path_2 = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Sphere")
        sample_prim_2 = self._stage.GetPrimAtPath(sample_prim_path_2)

        # Setup relationships
        for target in [sample_prim_path_1, sample_prim_path_2]:
            omni.kit.commands.execute(
                "AddRelationshipTarget",
                relationship=self._material_node_prim.GetAttribute("inputs:prims"),
                target=target,
            )
        for target in [material_path]:
            omni.kit.commands.execute(
                "AddRelationshipTarget",
                relationship=self._material_node_prim.GetAttribute("inputs:materialPrim"),
                target=target,
            )

        self._material_node.get_attribute("inputs:seed").set(1410)
        await self._controller.evaluate(self._graph)

        has_material = (
            sample_prim_1.GetRelationship("material:binding").GetTargets()[0] == material_path
            and sample_prim_2.GetRelationship("material:binding").GetTargets()[0] == material_path
        )

        self.assertTrue(has_material)

    async def test_2_geom_2_material(self):
        """Test sampling two materials for two meshes."""

        mtl_name_1 = "OmniGlass"
        omni.kit.commands.execute(
            "CreateAndBindMdlMaterialFromLibrary", mdl_name=f"{mtl_name_1}.mdl", mtl_name=mtl_name_1
        )
        material_path_1 = f"/Looks/{mtl_name_1}"
        material_1 = self._stage.GetPrimAtPath(material_path_1)
        mtl_name_2 = "OmniPBR"
        omni.kit.commands.execute(
            "CreateAndBindMdlMaterialFromLibrary", mdl_name=f"{mtl_name_2}.mdl", mtl_name=mtl_name_2
        )
        material_path_2 = f"/Looks/{mtl_name_2}"
        material_2 = self._stage.GetPrimAtPath(material_path_2)

        _, sample_prim_path_1 = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Sphere")
        sample_prim_1 = self._stage.GetPrimAtPath(sample_prim_path_1)
        _, sample_prim_path_2 = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Sphere")
        sample_prim_2 = self._stage.GetPrimAtPath(sample_prim_path_2)

        # Setup relationships
        for target in [sample_prim_path_1, sample_prim_path_2]:
            omni.kit.commands.execute(
                "AddRelationshipTarget",
                relationship=self._material_node_prim.GetAttribute("inputs:prims"),
                target=target,
            )
        for target in [material_path_1, material_path_2]:
            omni.kit.commands.execute(
                "AddRelationshipTarget",
                relationship=self._material_node_prim.GetAttribute("inputs:materialPrim"),
                target=target,
            )

        self._material_node.get_attribute("inputs:seed").set(1410)
        await self._controller.evaluate(self._graph)

        prim_1_has_mat_1 = sample_prim_1.GetRelationship("material:binding").GetTargets()[0] == material_path_1
        prim_1_has_mat_2 = sample_prim_1.GetRelationship("material:binding").GetTargets()[0] == material_path_2
        prim_2_has_mat_1 = sample_prim_2.GetRelationship("material:binding").GetTargets()[0] == material_path_1
        prim_2_has_mat_2 = sample_prim_2.GetRelationship("material:binding").GetTargets()[0] == material_path_2

        has_material = (prim_1_has_mat_1 or prim_1_has_mat_2) and (prim_2_has_mat_1 or prim_2_has_mat_2)

        self.assertTrue(has_material)

    async def test_point_instancer(self):
        """Testing sampling point instancers."""
        N = 100
        pi = self._stage.DefinePrim("/PI", "PointInstancer")
        _, proto1_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        _, proto2_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Sphere")
        UsdGeom.PointInstancer(pi).CreatePrototypesRel().SetTargets([proto1_path, proto2_path])
        pi.GetAttribute("protoIndices").Set([0] * N + [1] * N)

        _, sample_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cone")
        sample_prim = self._stage.GetPrimAtPath(sample_path)

        mtl_name = "OmniGlass"
        omni.kit.commands.execute("CreateAndBindMdlMaterialFromLibrary", mdl_name=f"{mtl_name}.mdl", mtl_name=mtl_name)
        material_path = f"/Looks/{mtl_name}"
        material = self._stage.GetPrimAtPath(material_path)

        # Setup relationships
        for target in [pi.GetPath(), sample_path]:
            omni.kit.commands.execute(
                "AddRelationshipTarget",
                relationship=self._material_node_prim.GetAttribute("inputs:prims"),
                target=target,
            )
        for target in [material_path]:
            omni.kit.commands.execute(
                "AddRelationshipTarget",
                relationship=self._material_node_prim.GetAttribute("inputs:materialPrim"),
                target=target,
            )

        self._material_node.get_attribute("inputs:seed").set(1410)
        await self._controller.evaluate(self._graph)

        material_on_cone = sample_prim.GetRelationship("material:binding").GetTargets()[0] == material_path

        material_on_protos = True
        for proto in pi.GetRelationship("prototypes").GetTargets():
            prim = self._stage.GetPrimAtPath(proto)
            material_on_protos = material_on_protos and (
                prim.GetRelationship("material:binding").GetTargets()[0] == material_path
            )

        self.assertTrue(material_on_cone and material_on_protos)

    async def test_material_coverage(self):
        """Test uniform distribution of samples."""

        num_materials = 10
        material_paths = list()
        for i in range(num_materials):
            name = f"material_{i}"
            omni.kit.commands.execute("CreateAndBindMdlMaterialFromLibrary", mdl_name="OmniPBR.mdl", mtl_name=name)
            material_paths.append(f"/Looks/{name}")

        num_samples = 20
        sample_prim_paths = list()
        sample_prims = list()
        for i in range(num_samples):
            _, sample_prim_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
            sample_prim = self._stage.GetPrimAtPath(sample_prim_path)
            sample_prims.append(sample_prim)
            sample_prim_paths.append(sample_prim_path)

        # Setup relationships
        for target in sample_prim_paths:
            omni.kit.commands.execute(
                "AddRelationshipTarget",
                relationship=self._material_node_prim.GetAttribute("inputs:prims"),
                target=target,
            )
        for target in material_paths:
            omni.kit.commands.execute(
                "AddRelationshipTarget",
                relationship=self._material_node_prim.GetAttribute("inputs:materialPrim"),
                target=target,
            )

        self._material_node.get_attribute("inputs:seed").set(1410)
        await self._controller.evaluate(self._graph)

        material_counts = [0] * num_materials

        for prim in sample_prims:
            material_path = prim.GetRelationship("material:binding").GetTargets()[0]
            material_counts[material_paths.index(material_path)] += 1

        std = np.sqrt(num_samples * (num_materials - 1) / (num_materials**2))
        is_distributed = (np.min(material_counts) >= num_samples / num_materials - 2 * std) and (
            np.max(material_counts) <= num_samples / num_materials + 2 * std
        )

        self.assertTrue(is_distributed)
