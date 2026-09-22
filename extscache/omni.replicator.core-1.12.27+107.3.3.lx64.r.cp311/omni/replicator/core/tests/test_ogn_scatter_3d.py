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
from scipy import ndimage


class TestOgnScatter3D(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        rep.set_global_seed(1234)

        self._stage = omni.usd.get_context().get_stage()
        self._controller = og.Controller()
        self._graph = self._controller.create_graph("/World/PushGraph")

        self._scatter_node = self._controller.create_node(("scatter", self._graph), "omni.replicator.core.OgnScatter3D")
        self._scatter_node_prim = self._stage.GetPrimAtPath(self._scatter_node.get_prim_path())

    async def tearDown(self):
        await omni.usd.get_context().new_stage_async()

    @unittest.skip("Enable when able to retrieve logged messages")
    async def test_invalid_volume(self):
        """Test raises error from invalid volume prim"""

        invalid_volume = self._stage.DefinePrim("/invalid", "Xform")
        _, sample_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")

        # Setup relationships
        self._add_relationship_target("inputs:prims", [sample_path])
        self._add_relationship_target("inputs:volumePrims", [invalid_volume.GetPath()])

        await self._controller.evaluate(self._graph)
        # error_messages = self._scatter_node.get_compute_messages(omni.graph.core.Severity.ERROR)
        # self.assertFalse(success)
        # TODO when able to retrieve logged messages

    @unittest.skip("Enable when able to retrieve logged messages")
    async def test_invalid_sample(self):
        """Test raises error from invalid sample prim"""

        _, volume_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        invalid_sample = self._stage.DefinePrim("/invalid", "Scope")

        # Setup relationships
        self._add_relationship_target("inputs:prims", [invalid_sample.GetPath()])
        self._add_relationship_target("inputs:volumePrims", [volume_path])

        await self._controller.evaluate(self._graph)
        # error_messages = self._scatter_node.get_compute_messages(omni.graph.core.Severity.ERROR)
        # self.assertFalse(success)
        # TODO when able to retrieve logged messages

    async def test_1_volume_1_sample(self):
        """Test sampling one mesh from one volume."""

        _, sample_prim_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Sphere")
        sample_prim = self._stage.GetPrimAtPath(sample_prim_path)
        sample_prim.GetAttribute("xformOp:translate").Set((-1000, -1000, -1000))
        _, volume_prim_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Torus")
        volume_prim = self._stage.GetPrimAtPath(volume_prim_path)
        # generate voxelgrid
        mesh_properties = dict()
        voxel_size = 3.0
        vertices = np.array(volume_prim.GetAttribute("points").Get())
        faces_indices = np.array(volume_prim.GetAttribute("faceVertexIndices").Get())
        face_vertex_counts = np.array(volume_prim.GetAttribute("faceVertexCounts").Get())
        faces = _convert_poly_to_tri(vertices, faces_indices, face_vertex_counts)
        voxel_surface = _trianglemesh_to_voxelgrid(vertices, faces, voxel_size, mesh_properties)
        voxel_volume = _fill(voxel_surface)
        voxels = np.array(np.nonzero(voxel_volume)).transpose()
        # voxel coordinates of bottom left corner
        origin = mesh_properties["origin"]
        voxel_coords = voxels * voxel_size + origin

        # Setup relationships
        self._add_relationship_target("inputs:prims", [sample_prim_path])
        self._add_relationship_target("inputs:volumePrims", [volume_prim_path])

        # Get sample with global seed of 1234
        await self._controller.evaluate(self._graph)
        sampled_point_seed_1234 = np.array(sample_prim.GetAttribute("xformOp:translate").Get())

        rep.set_global_seed(0)

        await self._controller.evaluate(self._graph)
        sampled_point = np.array(sample_prim.GetAttribute("xformOp:translate").Get())
        x = sampled_point[0]
        y = sampled_point[1]
        z = sampled_point[2]

        # Assert that the two sampled points are not close to each other
        with self.assertRaises(AssertionError):
            np.testing.assert_allclose(sampled_point_seed_1234, sampled_point)

        is_in_mesh = False
        # check to make sure that the point lies in a voxel coordinate
        for coord in voxel_coords:
            if (
                x >= coord[0]
                and y >= coord[1]
                and z >= coord[2]
                and x <= coord[0] + voxel_size
                and y <= coord[1] + voxel_size
                and z <= coord[2] + voxel_size
            ):
                is_in_mesh = True
                break
        print("1 VOLUME 1 SAMPLE TEST CASE PASS:", is_in_mesh)
        print(volume_prim.GetAttribute("xformOp:scale").Get())
        self.assertTrue(is_in_mesh)

    async def test_1_volume_2_sample(self):
        """Test sampling two meshes from one volume."""

        _, sample_prim_path_1 = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        sample_prim_1 = self._stage.GetPrimAtPath(sample_prim_path_1)
        sample_prim_1.GetAttribute("xformOp:translate").Set((-1000, -1000, -1000))
        _, sample_prim_path_2 = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        sample_prim_2 = self._stage.GetPrimAtPath(sample_prim_path_2)
        sample_prim_2.GetAttribute("xformOp:translate").Set((-1000, -1000, -1000))

        _, volume_prim_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        volume_prim = self._stage.GetPrimAtPath(volume_prim_path)
        volume_offset = (0, 0, 500)
        volume_prim.GetAttribute("xformOp:translate").Set(volume_offset)

        # Setup relationships
        self._add_relationship_target("inputs:prims", [sample_prim_path_1, sample_prim_path_2])
        self._add_relationship_target("inputs:volumePrims", [volume_prim_path])

        self._scatter_node.get_attribute("inputs:seed").set(1410)
        await self._controller.evaluate(self._graph)

        sampled_point_1 = np.array(sample_prim_1.GetAttribute("xformOp:translate").Get())
        sampled_point_2 = np.array(sample_prim_2.GetAttribute("xformOp:translate").Get())
        is_in_cube_1 = np.linalg.norm(sampled_point_1 - np.array(volume_offset)) ** 2 <= 100 * 100 * 100
        is_in_cube_2 = np.linalg.norm(sampled_point_2 - np.array(volume_offset)) ** 2 <= 100 * 100 * 100
        is_in_mesh = is_in_cube_1 and is_in_cube_2
        print("1 VOLUME 2 SAMPLE TEST CASE PASS:", is_in_mesh)
        self.assertTrue(is_in_mesh)

    async def test_2_volume_1_sample(self):
        """Test sampling one mesh from two volumes."""

        _, sample_prim_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        sample_prim = self._stage.GetPrimAtPath(sample_prim_path)
        sample_prim.GetAttribute("xformOp:translate").Set((-1000, -1000, -1000))
        _, volume_prim_path_1 = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        volume_prim_1 = self._stage.GetPrimAtPath(volume_prim_path_1)
        volume_offset_1 = (0, 0, 500)
        volume_prim_1.GetAttribute("xformOp:translate").Set(volume_offset_1)
        _, volume_prim_path_2 = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        volume_prim_2 = self._stage.GetPrimAtPath(volume_prim_path_2)
        volume_offset_2 = (0, 0, -500)
        volume_prim_2.GetAttribute("xformOp:translate").Set(volume_offset_2)

        # Setup relationships
        self._add_relationship_target("inputs:prims", [sample_prim_path])
        self._add_relationship_target("inputs:volumePrims", [volume_prim_path_1, volume_prim_path_2])

        self._scatter_node.get_attribute("inputs:seed").set(1410)
        await self._controller.evaluate(self._graph)

        sampled_point = np.array(sample_prim.GetAttribute("xformOp:translate").Get())
        is_in_cube_1 = np.linalg.norm(sampled_point - np.array(volume_offset_1)) ** 2 <= 100 * 100 * 100
        is_in_cube_2 = np.linalg.norm(sampled_point - np.array(volume_offset_2)) ** 2 <= 100 * 100 * 100
        is_in_mesh = is_in_cube_1 or is_in_cube_2
        print("2 VOLUME 1 SAMPLE TEST CASE PASS:", is_in_mesh)
        self.assertTrue(is_in_mesh)

    async def test_2_volume_2_sample(self):
        """Test sampling two meshes from two volumes."""

        _, sample_prim_path_1 = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        sample_prim_1 = self._stage.GetPrimAtPath(sample_prim_path_1)
        sample_prim_1.GetAttribute("xformOp:translate").Set((-10000, -1000, -1000))
        _, sample_prim_path_2 = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        sample_prim_2 = self._stage.GetPrimAtPath(sample_prim_path_2)
        sample_prim_2.GetAttribute("xformOp:translate").Set((-1000, -10000, -1000))

        _, volume_prim_path_1 = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        volume_prim_1 = self._stage.GetPrimAtPath(volume_prim_path_1)
        volume_offset_1 = (0, 0, 500)
        volume_prim_1.GetAttribute("xformOp:translate").Set(volume_offset_1)
        _, volume_prim_path_2 = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        volume_prim_2 = self._stage.GetPrimAtPath(volume_prim_path_2)
        volume_offset_2 = (0, 0, -500)
        volume_prim_2.GetAttribute("xformOp:translate").Set(volume_offset_2)

        # Setup relationships
        self._add_relationship_target("inputs:prims", [sample_prim_path_1, sample_prim_path_2])
        self._add_relationship_target("inputs:volumePrims", [volume_prim_path_1, volume_prim_path_2])

        self._scatter_node.get_attribute("inputs:seed").set(1410)
        await self._controller.evaluate(self._graph)

        sampled_point_1 = np.array(sample_prim_1.GetAttribute("xformOp:translate").Get())
        sampled_point_2 = np.array(sample_prim_2.GetAttribute("xformOp:translate").Get())
        is_1_in_cube_1 = np.linalg.norm(sampled_point_1 - np.array(volume_offset_1)) ** 2 <= 100 * 100 * 100
        is_1_in_cube_2 = np.linalg.norm(sampled_point_1 - np.array(volume_offset_2)) ** 2 <= 100 * 100 * 100
        is_2_in_cube_1 = np.linalg.norm(sampled_point_2 - np.array(volume_offset_1)) ** 2 <= 100 * 100 * 100
        is_2_in_cube_2 = np.linalg.norm(sampled_point_2 - np.array(volume_offset_2)) ** 2 <= 100 * 100 * 100
        is_in_mesh = (is_1_in_cube_1 or is_1_in_cube_2) and (is_2_in_cube_1 or is_2_in_cube_2)
        print("2 VOLUME 2 SAMPLE TEST CASE PASS:", is_in_mesh)
        self.assertTrue(is_in_mesh)

    async def test_coverage(self):
        """Test uniform distribution of samples."""

        sample_prims = list()
        sample_prim_paths = list()
        num_samples = 100

        for i in range(num_samples):
            _, sample_prim_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
            sample_prim = self._stage.GetPrimAtPath(sample_prim_path)
            sample_prim.GetAttribute("xformOp:translate").Set((-1000, -1000, -1000))
            sample_prims.append(sample_prim)
            sample_prim_paths.append(sample_prim_path)

        _, volume_prim_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        volume_prim = self._stage.GetPrimAtPath(volume_prim_path)
        volume_offset = (0, 0, 0)
        volume_prim.GetAttribute("xformOp:translate").Set(volume_offset)

        # Setup relationships
        self._add_relationship_target("inputs:prims", sample_prim_paths)
        self._add_relationship_target("inputs:volumePrims", [volume_prim_path])

        self._scatter_node.get_attribute("inputs:seed").set(1410)
        await self._controller.evaluate(self._graph)

        sampled_point = np.concatenate(
            [np.array(prim.GetAttribute("xformOp:translate").Get()).reshape(1, 3) for prim in sample_prims]
        )

        num_per_octant = list()
        octant_signs = [
            (1, 1, 1),
            (1, 1, -1),
            (1, -1, 1),
            (1, -1, -1),
            (-1, 1, 1),
            (-1, 1, -1),
            (-1, -1, 1),
            (-1, -1, -1),
        ]
        for sign in octant_signs:
            points = np.array(sign).reshape(1, 3) * sampled_point
            num_per_octant.append(np.all(np.logical_and(points >= 0, points <= 50), axis=-1).sum())

        std = np.sqrt(num_samples * 7 / 64)

        is_distributed = (np.min(num_per_octant) >= num_samples / 8 - 3 * std) and (
            np.max(num_per_octant) <= num_samples / 8 + 3 * std
        )

        print("POINTS COVERAGE TEST CASE PASS:", is_distributed)
        self.assertTrue(is_distributed)

    async def test_point_instancer_sample(self):
        """Test sampling a point instancer."""
        N = 100  # point samples per prototype
        pi = self._stage.DefinePrim("/PI", "PointInstancer")
        _, proto1_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        _, proto2_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Sphere")
        UsdGeom.PointInstancer(pi).CreatePrototypesRel().SetTargets([proto1_path, proto2_path])
        pi.GetAttribute("protoIndices").Set([0] * N + [1] * N)
        pi.GetAttribute("positions").Set([[0, 0, 0]])

        _, mesh_volume_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Torus")
        _, mesh_sample_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cone")

        # Setup relationships
        self._add_relationship_target("inputs:prims", [pi.GetPath(), mesh_sample_path])
        self._add_relationship_target("inputs:volumePrims", [mesh_volume_path])

        self._scatter_node.get_attribute("inputs:seed").set(1410)
        await self._controller.evaluate(self._graph)

        pi_has_positions = len(pi.GetAttribute("positions").Get()) == len(pi.GetAttribute("protoIndices").Get())
        self.assertTrue(pi_has_positions)

    async def test_coverage_scaled_mesh(self):
        """Test that a scaled mesh is sampled uniformly."""
        N = 1000  # point samples per prototype
        pi = self._stage.DefinePrim("/PI", "PointInstancer")
        _, proto1_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        UsdGeom.PointInstancer(pi).CreatePrototypesRel().SetTargets([proto1_path])
        pi.GetAttribute("protoIndices").Set([0] * N)
        pi.GetAttribute("positions").Set([[0, 0, 0]])

        _, volume_prim_path_1 = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        volume_prim_1 = self._stage.GetPrimAtPath(volume_prim_path_1)
        volume_prim_1.GetAttribute("xformOp:translate").Set((10000, 10000, 10000))
        volume_prim_1.GetAttribute("xformOp:scale").Set((0.1, 0.1, 0.1))
        _, volume_prim_path_2 = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        volume_prim_2 = self._stage.GetPrimAtPath(volume_prim_path_2)
        volume_prim_2.GetAttribute("xformOp:scale").Set((1, 1, 1))

        # Setup relationships
        self._add_relationship_target("inputs:prims", [pi.GetPath()])
        self._add_relationship_target("inputs:volumePrims", [volume_prim_path_1, volume_prim_path_2])

        self._scatter_node.get_attribute("inputs:seed").set(1410)

        small_cube_ratio = await self._compute_small_cube_ratios(pi, [9995, 10005], [-50, 50])
        self.assertTrue(abs(0.001 - small_cube_ratio) < 0.0005)

    async def test_noise_matrix_scaling(self):
        """Test that the noise matrix is being scaled appropriately."""
        N = 1000  # point samples per prototype
        pi = self._stage.DefinePrim("/PI", "PointInstancer")
        _, proto1_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        UsdGeom.PointInstancer(pi).CreatePrototypesRel().SetTargets([proto1_path])
        pi.GetAttribute("protoIndices").Set([0] * N)
        pi.GetAttribute("positions").Set([[0, 0, 0]])

        _, volume_prim_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        self._stage.GetPrimAtPath(volume_prim_path)

        # Setup relationships
        self._add_relationship_target("inputs:prims", [pi.GetPath()])
        self._add_relationship_target("inputs:volumePrims", [volume_prim_path])

        self._scatter_node_prim.GetAttribute("inputs:resolutionScaling").Set(1 / 15)

        self._scatter_node.get_attribute("inputs:seed").set(1410)

        octant_signs = [
            (1, 1, 1),
            (1, 1, -1),
            (1, -1, 1),
            (1, -1, -1),
            (-1, 1, 1),
            (-1, 1, -1),
            (-1, -1, 1),
            (-1, -1, -1),
        ]

        # Take 100 samples
        num_per_octant_average = []
        for _ in range(100):
            await self._controller.evaluate(self._graph)
            sampled_points = np.array(pi.GetAttribute("positions").Get())
            # Assert within bounds of volumes
            in_bounds = np.logical_and(np.all(sampled_points <= 50, axis=1), np.all(sampled_points >= -50, axis=1))

            self.assertTrue(np.all(in_bounds))
            num_per_octant = list()
            for sign in octant_signs:
                points = np.array(sign).reshape(1, 3) * sampled_points
                num_per_octant.append(np.all(np.logical_and(points >= 0, points <= 50), axis=-1).sum())
            num_per_octant_average.append(np.mean(num_per_octant))

        std = np.sqrt(N * 7 / 64)
        average_distribution = np.mean(num_per_octant)

        is_distributed = average_distribution <= N / 8 + std and average_distribution >= N / 8 - std
        print("TEST NOISE MATRIX SCALING PASS:", is_distributed)
        self.assertTrue(is_distributed)

    async def test_change_scale(self):
        """Test that when the scale changes, the distribution of prims changes accordingly."""
        N = 10  # point samples per prototype
        pi = self._stage.DefinePrim("/PI", "PointInstancer")
        _, proto1_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        UsdGeom.PointInstancer(pi).CreatePrototypesRel().SetTargets([proto1_path])
        pi.GetAttribute("protoIndices").Set([0] * N)
        pi.GetAttribute("positions").Set([[0, 0, 0]])

        _, volume_prim_path_1 = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        volume_prim_1 = self._stage.GetPrimAtPath(volume_prim_path_1)
        volume_prim_1.GetAttribute("xformOp:translate").Set((10000, 10000, 10000))
        volume_prim_1.GetAttribute("xformOp:scale").Set((0.1, 0.1, 0.1))
        _, volume_prim_path_2 = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        volume_prim_2 = self._stage.GetPrimAtPath(volume_prim_path_2)
        volume_prim_2.GetAttribute("xformOp:scale").Set((1, 1, 1))

        # Setup relationships
        self._add_relationship_target("inputs:prims", [pi.GetPath()])
        self._add_relationship_target("inputs:volumePrims", [volume_prim_path_1, volume_prim_path_2])

        vs = 5.0  # mm
        self._scatter_node.get_attribute("inputs:voxelSize").set(
            vs
        )  # we need this to pass the test for the new scatter node
        self._scatter_node.get_attribute("inputs:seed").set(1410)

        small_cube_ratio_1 = await self._compute_small_cube_ratios(pi, [9995 - vs, 10005 + vs], [-50 - vs, 50 + vs])
        volume_prim_1.GetAttribute("xformOp:scale").Set((1, 1, 1))
        volume_prim_2.GetAttribute("xformOp:scale").Set((0.1, 0.1, 0.1))
        small_cube_ratio_2 = await self._compute_small_cube_ratios(pi, [-5 - vs, 5 + vs], [9950 - vs, 10050 + vs])

        np.testing.assert_allclose([small_cube_ratio_1, small_cube_ratio_2], [0.001, 0.001], atol=0.0005)

    async def test_scatter_moving_volume(self):
        cubes = rep.create.cube()
        sphere = rep.create.sphere(scale=0.01)

        positions = [(-100, 0, 100), (100, 0, -100)]

        with rep.trigger.on_frame():
            with sphere:
                rep.modify.pose(position=rep.distribution.sequence(positions))
            with cubes:
                rep.randomizer.scatter_3d(volume_prims=sphere)

        await rep.orchestrator.step_async()
        cube_pose = cubes.get_output_prims()["prims"][0].GetAttribute("xformOp:translate").Get()
        np.testing.assert_allclose(cube_pose, np.array(positions[0]), atol=1.0)
        await rep.orchestrator.step_async()
        cube_pose = cubes.get_output_prims()["prims"][0].GetAttribute("xformOp:translate").Get()
        np.testing.assert_allclose(cube_pose, np.array(positions[1]), atol=1.0)

    def _add_relationship_target(self, attribute, prim_paths):
        for target in prim_paths:
            omni.kit.commands.execute(
                "AddRelationshipTarget", relationship=self._scatter_node_prim.GetAttribute(attribute), target=target
            )

    async def _compute_small_cube_ratios(self, pi, small_cube_bound, large_cube_bound, num_iterations=1000):
        small_cube_ratios = list()
        for _ in range(num_iterations):
            await self._controller.evaluate(self._graph)
            sampled_points = np.array(pi.GetAttribute("positions").Get())
            # Assert within bounds of volumes
            in_small_bounds = np.logical_and(
                np.all(sampled_points <= small_cube_bound[1], axis=1),
                np.all(sampled_points >= small_cube_bound[0], axis=1),
            )
            in_large_bounds = np.logical_and(
                np.all(sampled_points <= large_cube_bound[1], axis=1),
                np.all(sampled_points >= large_cube_bound[0], axis=1),
            )
            self.assertTrue(np.all(np.logical_or(in_small_bounds, in_large_bounds)))

            num_within_small_cube = np.sum(in_small_bounds)
            small_cube_ratios.append(num_within_small_cube / len(sampled_points))

        return sum(small_cube_ratios) / len(small_cube_ratios)


def _convert_poly_to_tri(vertices: np.ndarray, faces_indices: np.ndarray, face_vertex_counts: np.ndarray) -> np.ndarray:
    """
    Converts the input mesh into a triangle mesh.

    Args:
        vertices: A 2D array of shape (V, 3) containing the vertices that define the mesh.
        faces_indices: A 1D array representing the indices of the vertices for the corresponding faces.
        face_vertex_counts: A 1D array containing the number of vertices defined for each face.
    """
    mask = face_vertex_counts > 3
    faces = np.empty(
        (face_vertex_counts.shape[0] + np.sum(face_vertex_counts[np.nonzero(mask)]) - 3 * np.sum(mask), 3),
        dtype=np.int64,
    )
    faces_idx = 0
    poly_faces_idx = 0

    for vertex_count in face_vertex_counts:
        if vertex_count == 3:
            faces[faces_idx, :] = faces_indices[poly_faces_idx : poly_faces_idx + 3]
        else:  # if face is not a triangle, then break it up into multiple triangles
            faces[faces_idx : faces_idx + vertex_count - 2, 0] = faces_indices[poly_faces_idx]
            # sub-divide the polygon into several triangles by creating lines from the first vertex
            for i in range(poly_faces_idx, poly_faces_idx + vertex_count - 2):
                faces[faces_idx + i - poly_faces_idx, 1:] = faces_indices[i + 1 : i + 3]
        faces_idx += vertex_count - 2
        poly_faces_idx += vertex_count

    return faces


def _subdivide_vertices(vertices: np.ndarray, faces: np.ndarray, resolution: int) -> np.ndarray:
    """
    Upsamples the mesh by subdividing the triangle mesh's vertices.
    Ensures that every existig edge's length is <= (resolution-1) / resolution^2
    NOTE: This is a NumPy implementation of the function,
    "kaolin.ops.mesh.trianglemesh._unbatched_subdivide_vertices()", in the Kaolin library .
    Original source code here: https://github.com/NVIDIAGameWorks/kaolin

    Args:
        vertices: A 2D array of shape (V, 3) containing the vertices that define the mesh.
        faces: A 2D array of shape (F, 3) containing the indices of the vertices that define each face.
        resolution: An integer > 1 which specifies how much to subdivide the mesh's vertices.
    """
    assert resolution > 1
    min_edge_length = ((resolution - 1) / (resolution**2)) ** 2
    v1 = np.take(vertices, faces[:, 0], axis=0)
    v2 = np.take(vertices, faces[:, 1], axis=0)
    v3 = np.take(vertices, faces[:, 2], axis=0)

    while True:
        edge1_length = np.sum((v1 - v2) ** 2, axis=1)[:, None]
        edge2_length = np.sum((v2 - v3) ** 2, axis=1)[:, None]
        edge3_length = np.sum((v3 - v1) ** 2, axis=1)[:, None]
        total_edges_length = np.concatenate((edge1_length, edge2_length, edge3_length), axis=1)
        max_edges_length = np.max(total_edges_length, axis=1)
        # Choose the edges that is greater than the min_edge_length
        keep = max_edges_length > min_edge_length
        # if all the edges are smaller than the min_edge_length, stop upsampling
        K = np.sum(keep)
        if K == 0:
            break
        v1 = v1[keep]  # shape of (K, 3), where K is number of edges that has been kept
        v2 = v2[keep]
        v3 = v3[keep]
        # New vertices are placed at the middle of the edge
        v4 = (v1 + v3) / 2  # shape of (K, 3), where K is number of edges that has been kept
        v5 = (v1 + v2) / 2
        v6 = (v2 + v3) / 2
        # update vertices
        vertices = np.concatenate((vertices, v4, v5, v6))
        # Get rid of repeated vertices
        vertices, unique_indices = np.unique(vertices, return_inverse=True, axis=0)
        # Update v1, v2, v3
        v1 = np.concatenate((v1, v2, v4, v3))
        v2 = np.concatenate((v4, v5, v5, v4))
        v3 = np.concatenate((v5, v6, v6, v6))
    return vertices


def _base_points_to_voxelgrids(points: np.ndarray, resolution: int) -> np.ndarray:
    """
    Converts points to voxelgrids. Only points within range [0, 1] are used for voxelization.
    NOTE: This is a NumPy implementation of the function,
    "kaolin.ops.conversions.pointcloud_base_points_to_voxelgrids()", in the Kaolin library.
    Original source code here: https://github.com/NVIDIAGameWorks/kaolin

    Args:
        points: A 2D array of size (P, 3) containing the scaled points.
        resolution: An integer > 1 which specifies how much to subdivide the mesh's vertices.
    """
    # num_p = points.shape[0]
    dtype = points.dtype

    vg_size = (resolution, resolution, resolution)

    # mult = np.ones(1, dtype=dtype) * (resolution - 1)
    pc_index = np.unique(np.round(((points) * (resolution - 1))).astype(np.int_), axis=0)

    vg = np.zeros(shape=vg_size, dtype=dtype)
    vg[tuple(pc_index.transpose())] = 1
    return vg


def _trianglemesh_to_voxelgrid(
    vertices: np.ndarray, faces: np.ndarray, voxel_size: float, mesh_voxel_map: dict
) -> np.ndarray:
    """
    Converts a triangle mesh into a voxelgrid of size (resolution, resolution, resolution)
    NOTE: This is a NumPy implementation of the function,
    "kaolin.ops.conversions.trianglemesh.trianglemeshes_to_voxelgrids()", in the Kaolin library.
    Original source code here: https://github.com/NVIDIAGameWorks/kaolin

    Args:
        vertices: A 2D array of shape (V, 3) containing the vertices that define the mesh.
        faces: A 2D array of shape (F, 3) containing the indices of the vertices that define each face.
        resolution: An integer > 1 which specifies how much to subdivide the mesh's vertices.
        mesh_voxel_map: A dictionary where voxel parameters will be saved.
    """
    if voxel_size <= 0:
        raise ValueError(f"Expected positive voxel_size, instead got {voxel_size}")

    origin = np.min(vertices, axis=0)
    scale = np.max(np.max(vertices, axis=0) - origin, axis=0)
    resolution = int(scale / voxel_size)
    mesh_voxel_map["resolution"] = resolution
    mesh_voxel_map["origin"] = origin
    mesh_voxel_map["scale"] = scale
    scaled_points = (vertices - origin) / scale.reshape(-1, 1, 1)

    points = _subdivide_vertices(scaled_points[0], faces, resolution)
    voxelgrid = _base_points_to_voxelgrids(points, resolution)

    return voxelgrid


def _fill(voxelgrid: np.ndarray) -> np.ndarray:
    """
    Fills in the volume of a voxel grid.
    NOTE: This is a NumPy implementation of the function
    "kaolin.ops.voxelgrid.fill()" in the Kaolin library.
    Original source code here: https://github.com/NVIDIAGameWorks/kaolin

    Args:
        voxelgrid: The voxelgrid that defines the surface of the mesh.
    """
    dtype = voxelgrid.dtype
    return np.array(ndimage.binary_fill_holes(voxelgrid), dtype=dtype)
