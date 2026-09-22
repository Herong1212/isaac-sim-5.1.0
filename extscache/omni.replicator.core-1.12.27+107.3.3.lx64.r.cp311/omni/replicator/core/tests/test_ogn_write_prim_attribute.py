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

import unittest
from typing import List

import numpy as np
import omni.graph.core as og
import omni.kit
import omni.replicator.core as rep
import omni.usd
from pxr import Gf, Sdf, UsdGeom, Vt
from scipy.spatial.transform import Rotation as R


class TestOgnWritePrimAttribute(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        rep.set_global_seed(1234)

        self._stage = omni.usd.get_context().get_stage()
        self._controller = og.Controller()
        self._graph = self._controller.create_graph("/World/PushGraph")

        self._uniform_node = self._controller.create_node(
            ("uniform", self._graph), "omni.replicator.core.OgnSampleUniform"
        )
        self._assign_node = self._controller.create_node(
            ("assign", self._graph), "omni.replicator.core.OgnWritePrimAttribute"
        )
        self._assign_node_prim = self._stage.GetPrimAtPath(self._assign_node.get_prim_path())
        self._assign_node.get_attribute("inputs:attributeType").set("double")

    async def tearDown(self):
        await omni.usd.get_context().new_stage_async()

    async def test_1d_types(self):
        """Test assigning 1D attributes."""

        await self._test_types([Sdf.ValueTypeNames.Float, Sdf.ValueTypeNames.Double], [float, float], 1)

    async def test_2d_types(self):
        """Test assigning 2D attributes."""

        await self._test_types([Sdf.ValueTypeNames.Float2, Sdf.ValueTypeNames.Double2], [Gf.Vec2f, Gf.Vec2d], 2)

    async def test_3d_types(self):
        """Test assigning 3D attributes."""

        await self._test_types([Sdf.ValueTypeNames.Float3, Sdf.ValueTypeNames.Double3], [Gf.Vec3f, Gf.Vec3d], 3)

    async def test_4d_types(self):
        """Test assigning 4D attributes."""

        await self._test_types([Sdf.ValueTypeNames.Float4, Sdf.ValueTypeNames.Double4], [Gf.Vec4f, Gf.Vec4d], 4)

    async def test_2d_matrix_types(self):
        """Test assigning to 2D matrices."""

        await self._test_types([Sdf.ValueTypeNames.Matrix2d], [Gf.Matrix2d], 4)

    async def test_3d_matrix_types(self):
        """Test assigning to 3D matrices."""

        await self._test_types([Sdf.ValueTypeNames.Matrix3d], [Gf.Matrix3d], 9)

    async def test_4d_matrix_types(self):
        """Test assigning to 4D matrices."""

        await self._test_types([Sdf.ValueTypeNames.Matrix4d], [Gf.Matrix4d], 16)

    async def test_token_type(self):
        """Test assigning 1D attribute with token."""
        prims = list()
        prim_paths = list()
        num_samples = 10

        attribute_name = "testAttribute"

        initial_val = ["initialVal"]

        token_assign_node = self._controller.create_node(
            ("token_assign", self._graph), "omni.replicator.core.OgnWritePrimAttribute"
        )
        token_assign_node.get_attribute("inputs:attributeType").set("token")
        token_assign_node_prim = self._stage.GetPrimAtPath(token_assign_node.get_prim_path())

        for i in range(num_samples):
            prim_path = f"/sample{i+1}"
            omni.kit.commands.execute("CreatePrimCommand", prim_path=prim_path, prim_type="Cube")
            prim = self._stage.GetPrimAtPath(prim_path)

            prim.CreateAttribute(attribute_name, Sdf.ValueTypeNames.Token, False).Set(Vt.Token(*initial_val))
            prim_paths.append(prim_path)
            prims.append(prim)

        for target in prim_paths:
            omni.kit.commands.execute(
                "AddRelationshipTarget", relationship=token_assign_node_prim.GetAttribute("inputs:prims"), target=target
            )

        assigned_val = ["assignedVal"] * num_samples

        token_assign_node.get_attribute("inputs:values").set(assigned_val)
        token_assign_node.get_attribute("inputs:attribute").set(attribute_name)

        await self._controller.evaluate(self._graph)
        attribute_vals = [prim.GetAttribute(attribute_name).Get() for prim in prims]

        self.assertFalse(attribute_vals == initial_val * num_samples)
        self.assertTrue(attribute_vals == assigned_val)

    async def test_asset_type(self):
        """Test assigning 1D attribute with asset."""
        prims = list()
        prim_paths = list()
        num_samples = 10

        attribute_name = "testAttribute"

        initial_val = ["initialVal"]

        asset_assign_node = self._controller.create_node(
            ("asset_assign", self._graph), "omni.replicator.core.OgnWritePrimAttribute"
        )
        asset_assign_node.get_attribute("inputs:attributeType").set("asset")
        asset_assign_node_prim = self._stage.GetPrimAtPath(asset_assign_node.get_prim_path())

        for i in range(num_samples):
            prim_path = f"/sample{i+1}"
            omni.kit.commands.execute("CreatePrimCommand", prim_path=prim_path, prim_type="Cube")
            prim = self._stage.GetPrimAtPath(prim_path)

            prim.CreateAttribute(attribute_name, Sdf.ValueTypeNames.Token, False).Set(Vt.Token(*initial_val))
            prim_paths.append(prim_path)
            prims.append(prim)

        for target in prim_paths:
            omni.kit.commands.execute(
                "AddRelationshipTarget", relationship=asset_assign_node_prim.GetAttribute("inputs:prims"), target=target
            )

        assigned_val = ["assignedVal"] * num_samples

        asset_assign_node.get_attribute("inputs:values").set(assigned_val)
        asset_assign_node.get_attribute("inputs:attribute").set(attribute_name)

        await self._controller.evaluate(self._graph)
        attribute_vals = [prim.GetAttribute(attribute_name).Get() for prim in prims]

        self.assertFalse(attribute_vals == initial_val * num_samples)
        self.assertTrue(attribute_vals == assigned_val)

    async def test_point_instancer_attribute_rotate(self):
        """Test assigning rotation attributes to point instancers."""
        lower = np.array([-60] * 3)
        upper = np.array([60] * 3)

        orientations = await self._get_point_instancer_results("xformOp:rotateXYZ", lower, upper, "orientations")
        attribute_vals = np.array([[*q.GetImaginary(), q.GetReal()] for q in orientations])
        vals = R.from_quat(attribute_vals).as_euler("xyz", degrees=True)

        self.assertTrue(np.all(np.logical_and(vals >= lower, vals <= upper)))

    async def test_point_instancer_attribute_translate(self):
        """Test assigning translation attributes to point instancers."""
        lower = np.array([100] * 3)
        upper = np.array([1000] * 3)

        positions = await self._get_point_instancer_results("xformOp:translate", lower, upper, "positions")
        self.assertTrue(np.all(np.logical_and(positions >= lower, positions <= upper)))

    async def test_point_instancer_attribute_scale(self):
        """Test assigning scaling attributes to point instancers."""
        lower = np.array([100] * 3)
        upper = np.array([1000] * 3)

        positions = await self._get_point_instancer_results("xformOp:scale", lower, upper, "scales")

        self.assertTrue(np.all(np.logical_and(positions >= lower, positions <= upper)))

    async def _get_point_instancer_results(self, attribute_name, lower, upper, pi_attribute_name):
        N = 100
        pi = self._stage.DefinePrim("/PI", "PointInstancer")
        _, proto1_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        _, proto2_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Sphere")
        UsdGeom.PointInstancer(pi).CreatePrototypesRel().SetTargets([proto1_path, proto2_path])
        pi.GetAttribute("protoIndices").Set([0] * N + [1] * N)

        self._uniform_node.get_attribute("inputs:seed").set(42)
        self._uniform_node.get_attribute("inputs:numSamples").set(2 * N)
        self._uniform_node.get_attribute("inputs:lower").set(lower)
        self._uniform_node.get_attribute("inputs:upper").set(upper)

        self._add_relationship_target("inputs:prims", [pi.GetPath()])

        self._controller.connect(
            self._uniform_node.get_attribute("outputs:samples"), self._assign_node.get_attribute("inputs:values")
        )
        self._assign_node.get_attribute("inputs:attribute").set(attribute_name)
        await self._controller.evaluate(self._graph)

        return pi.GetAttribute(pi_attribute_name).Get()

    async def _test_types(self, types: List[Sdf.ValueTypeName], containers: List, size: int):
        prims = list()
        prim_paths = list()
        num_samples = 10

        attribute_names = [f"testAttribute{i}" for i in range(len(types))]

        attribute_val = [-1] * size

        for i in range(num_samples):
            prim_path = f"/sample{i+1}"
            omni.kit.commands.execute("CreatePrimCommand", prim_path=prim_path, prim_type="Cube")
            prim = self._stage.GetPrimAtPath(prim_path)
            for idx, name in enumerate(attribute_names):
                container = containers[idx]
                prim.CreateAttribute(name, types[idx], False).Set(container(*attribute_val))
            prim_paths.append(prim_path)
            prims.append(prim)

        lower = np.array([100.0] * size)
        upper = np.array([1000.0] * size)

        self._uniform_node.get_attribute("inputs:seed").set(42)
        self._uniform_node.get_attribute("inputs:numSamples").set(num_samples)
        self._uniform_node.get_attribute("inputs:lower").set(lower)
        self._uniform_node.get_attribute("inputs:upper").set(upper)

        self._add_relationship_target("inputs:prims", prim_paths)

        self._controller.connect(
            self._uniform_node.get_attribute("outputs:samples"), self._assign_node.get_attribute("inputs:values")
        )

        for name in attribute_names:
            self._assign_node.get_attribute("inputs:attribute").set(name)
            await self._controller.evaluate(self._graph)
            attribute_vals = [np.array(prim.GetAttribute(name).Get()).reshape(-1) for prim in prims]
            self.assertTrue(
                np.all(np.logical_and(attribute_vals >= lower, attribute_vals <= upper)),
                f"Attribute {name}: expected values between {lower} and {upper}, got {attribute_vals}",
            )

    def _add_relationship_target(self, attribute, prim_paths):
        for target in prim_paths:
            omni.kit.commands.execute(
                "AddRelationshipTarget", relationship=self._assign_node_prim.GetAttribute(attribute), target=target
            )
