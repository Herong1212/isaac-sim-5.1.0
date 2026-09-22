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

import numpy as np
import omni.graph.core as og
import omni.kit
import omni.replicator.core as rep
import omni.usd
from pxr import UsdGeom
from scipy.spatial.transform import Rotation as R


class TestOgnSampleRotation(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()

        rep.set_global_seed(1234)

        self._stage = omni.usd.get_context().get_stage()
        self._controller = og.Controller()
        self._graph = self._controller.create_graph("/World/PushGraph")

        self._sample_node = self._controller.create_node(
            ("sample", self._graph), "omni.replicator.core.OgnSampleRotation"
        )
        self._sample_node_prim = self._stage.GetPrimAtPath(self._sample_node.get_prim_path())

    async def tearDown(self):
        await omni.usd.get_context().new_stage_async()

    async def test_1_sample(self):
        """Test sampling rotation of one prims."""

        _, sample_prim_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        sample_prim = self._stage.GetPrimAtPath(sample_prim_path)

        self._sample_node.get_attribute("inputs:prims").set([sample_prim_path])
        self._sample_node.get_attribute("inputs:seed").set(1410)
        await self._controller.evaluate(self._graph)

        sampled_rot = np.array(sample_prim.GetAttribute("xformOp:rotateXYZ").Get())

        self.assertTrue(sampled_rot is not None)

    async def test_multiple_samples_constrained(self):
        """Test sampling constrained rotations of multiple prims."""

        sample_prims = list()
        num_samples = 100

        for i in range(num_samples):
            _, sample_prim_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
            sample_prim = self._stage.GetPrimAtPath(sample_prim_path)
            sample_prims.append(sample_prim)
            omni.kit.commands.execute(
                "AddRelationshipTarget",
                relationship=self._sample_node_prim.GetAttribute("inputs:prims"),
                target=sample_prim_path,
            )

        min_angle = np.array([30, 40, 50])
        max_angle = np.array([60, 70, 80])

        self._sample_node.get_attribute("inputs:minAngle").set(min_angle)
        self._sample_node.get_attribute("inputs:maxAngle").set(max_angle)

        self._sample_node.get_attribute("inputs:seed").set(1410)
        await self._controller.evaluate(self._graph)

        for prim in sample_prims:
            sampled_rot = np.array(prim.GetAttribute("xformOp:rotateXYZ").Get())
            in_limits = np.all(np.logical_and(sampled_rot >= min_angle, sampled_rot <= max_angle))
            self.assertTrue(in_limits)

    async def test_point_instancer(self):
        """Test sampling a point instancer."""

        N = 100
        pi = self._stage.DefinePrim("/PI", "PointInstancer")
        _, proto1_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        _, proto2_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Sphere")
        UsdGeom.PointInstancer(pi).CreatePrototypesRel().SetTargets([proto1_path, proto2_path])
        pi.GetAttribute("protoIndices").Set([0] * N + [1] * N)

        _, mesh_sample_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cone")

        # setup relationships
        for target in [pi.GetPath(), mesh_sample_path]:
            omni.kit.commands.execute(
                "AddRelationshipTarget", relationship=self._sample_node_prim.GetAttribute("inputs:prims"), target=target
            )

        self._sample_node.get_attribute("inputs:seed").set(1410)
        await self._controller.evaluate(self._graph)

        pi_has_orientations = len(pi.GetAttribute("orientations").Get()) == len(pi.GetAttribute("protoIndices").Get())
        self.assertTrue(pi_has_orientations)

    async def test_uniform_rotation(self):
        """Test that the rotation sampling procedure is uniform."""

        N = 10000
        pi = self._stage.DefinePrim("/PI", "PointInstancer")
        _, proto_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        UsdGeom.PointInstancer(pi).CreatePrototypesRel().SetTargets([proto_path])
        pi.GetAttribute("protoIndices").Set([0] * N)

        # setup relationships
        for target in [pi.GetPath()]:
            omni.kit.commands.execute(
                "AddRelationshipTarget", relationship=self._sample_node_prim.GetAttribute("inputs:prims"), target=target
            )
        self._sample_node.get_attribute("inputs:seed").set(1410)
        await self._controller.evaluate(self._graph)

        orientations = pi.GetAttribute("orientations").Get()
        quats = np.array([[*rot.GetImaginary()] + [rot.GetReal()] for rot in orientations])

        rot_vecs = R.from_quat(quats).as_rotvec()
        angles = np.linalg.norm(rot_vecs, axis=-1)
        vecs = rot_vecs / angles[:, None]

        mean_angle = np.mean(angles)
        mean_vec_norm = np.linalg.norm(np.mean(vecs, axis=0))

        np.testing.assert_allclose(mean_angle, 2.20741609916, atol=0.005)
        np.testing.assert_allclose(mean_vec_norm, 0.02, atol=0.005)
