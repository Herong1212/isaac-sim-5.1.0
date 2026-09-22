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


class TestOgnScatter2D(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()

        rep.set_global_seed(1234)

        self._stage = omni.usd.get_context().get_stage()
        self._controller = og.Controller()
        self._graph = self._controller.create_graph("/World/PushGraph")

        self._scatter_node = self._controller.create_node(("scatter", self._graph), "omni.replicator.core.OgnScatter2D")
        self._scatter_node_prim = self._stage.GetPrimAtPath(self._scatter_node.get_prim_path())

    async def tearDown(self):
        await omni.usd.get_context().new_stage_async()

    async def test_1_surface_1_sample(self):
        """Test sampling one mesh from one surface."""
        _, sample_prim_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Sphere")
        sample_prim = self._stage.GetPrimAtPath(sample_prim_path)
        sample_prim.GetAttribute("xformOp:translate").Set((-1000, -1000, -1000))
        _, surface_prim_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cone")
        surface_prim = self._stage.GetPrimAtPath(surface_prim_path)

        vertices = np.array(surface_prim.GetAttribute("points").Get())
        faces_indices = np.array(surface_prim.GetAttribute("faceVertexIndices").Get())
        face_vertex_counts = np.array(surface_prim.GetAttribute("faceVertexCounts").Get())
        faces = convert_poly_to_tri(vertices, faces_indices, face_vertex_counts)

        # Setup relationships
        for target in [sample_prim_path]:
            omni.kit.commands.execute(
                "AddRelationshipTarget",
                relationship=self._scatter_node_prim.GetAttribute("inputs:prims"),
                target=target,
            )
        for target in [surface_prim_path]:
            omni.kit.commands.execute(
                "AddRelationshipTarget",
                relationship=self._scatter_node_prim.GetAttribute("inputs:surfacePrims"),
                target=target,
            )

        await self._controller.evaluate(self._graph)
        # Get sample with global seed of 1234
        sampled_point_seed_1234 = np.array(sample_prim.GetAttribute("xformOp:translate").Get())

        rep.set_global_seed(1410)
        await self._controller.evaluate(self._graph)
        sampled_point = np.array(sample_prim.GetAttribute("xformOp:translate").Get())

        # Assert that the two sampled points are not close to each other
        with self.assertRaises(AssertionError):
            np.testing.assert_allclose(sampled_point_seed_1234, sampled_point)

        is_on_mesh = False
        # check to make sure that point is on surface of mesh by checking if any tetrahedron has zero volume
        for face in faces:
            v1 = vertices[face[0]]
            v2 = vertices[face[1]]
            v3 = vertices[face[2]]

            mat = np.hstack((np.vstack((v1, v2, v3, sampled_point)), np.ones((4, 1))))
            det = np.linalg.det(mat)
            if np.isclose(det, 0.0):
                is_on_mesh = True
                break

        self.assertTrue(is_on_mesh)

    async def test_1_surface_2_sample(self):
        """Test sampling two meshes from one surface."""

        _, sample_prim_path_1 = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        sample_prim_1 = self._stage.GetPrimAtPath(sample_prim_path_1)
        sample_prim_1.GetAttribute("xformOp:translate").Set((-1000, -1000, -1000))
        _, sample_prim_path_2 = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        sample_prim_2 = self._stage.GetPrimAtPath(sample_prim_path_2)
        sample_prim_2.GetAttribute("xformOp:translate").Set((-1000, -1000, -1000))

        _, surface_prim_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        surface_prim = self._stage.GetPrimAtPath(surface_prim_path)
        surface_offset = (0, 0, 500)
        surface_prim.GetAttribute("xformOp:translate").Set(surface_offset)

        # Setup relationships
        for target in [sample_prim_path_1, sample_prim_path_2]:
            omni.kit.commands.execute(
                "AddRelationshipTarget",
                relationship=self._scatter_node_prim.GetAttribute("inputs:prims"),
                target=target,
            )
        for target in [surface_prim_path]:
            omni.kit.commands.execute(
                "AddRelationshipTarget",
                relationship=self._scatter_node_prim.GetAttribute("inputs:surfacePrims"),
                target=target,
            )

        self._scatter_node.get_attribute("inputs:seed").set(1410)
        await self._controller.evaluate(self._graph)

        sampled_point_1 = np.array(sample_prim_1.GetAttribute("xformOp:translate").Get())
        sampled_point_2 = np.array(sample_prim_2.GetAttribute("xformOp:translate").Get())
        is_on_cube_1 = on_cube(sampled_point_1 - np.array(surface_offset))
        is_on_cube_2 = on_cube(sampled_point_2 - np.array(surface_offset))
        is_on_mesh = is_on_cube_1 and is_on_cube_2
        self.assertTrue(is_on_mesh)

    async def test_2_surface_1_sample(self):
        """Test sampling one mesh from two surfaces."""

        _, sample_prim_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        sample_prim = self._stage.GetPrimAtPath(sample_prim_path)
        sample_prim.GetAttribute("xformOp:translate").Set((-1000, -1000, -1000))
        _, surface_prim_path_1 = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        surface_prim_1 = self._stage.GetPrimAtPath(surface_prim_path_1)
        surface_offset_1 = (0, 0, 500)
        surface_prim_1.GetAttribute("xformOp:translate").Set(surface_offset_1)
        _, surface_prim_path_2 = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        surface_prim_2 = self._stage.GetPrimAtPath(surface_prim_path_2)
        surface_offset_2 = (0, 0, -500)
        surface_prim_2.GetAttribute("xformOp:translate").Set(surface_offset_2)

        # Setup relationships
        for target in [sample_prim_path]:
            omni.kit.commands.execute(
                "AddRelationshipTarget",
                relationship=self._scatter_node_prim.GetAttribute("inputs:prims"),
                target=target,
            )
        for target in [surface_prim_path_1, surface_prim_path_2]:
            omni.kit.commands.execute(
                "AddRelationshipTarget",
                relationship=self._scatter_node_prim.GetAttribute("inputs:surfacePrims"),
                target=target,
            )

        self._scatter_node.get_attribute("inputs:seed").set(1410)
        await self._controller.evaluate(self._graph)

        sampled_point = np.array(sample_prim.GetAttribute("xformOp:translate").Get())
        is_on_cube_1 = on_cube(sampled_point - np.array(surface_offset_1))
        is_on_cube_2 = on_cube(sampled_point - np.array(surface_offset_2))
        is_on_mesh = is_on_cube_1 or is_on_cube_2
        self.assertTrue(is_on_mesh)

    async def test_2_surface_2_sample(self):
        """Test sampling two meshes from two surfaces."""
        _, sample_prim_path_1 = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        sample_prim_1 = self._stage.GetPrimAtPath(sample_prim_path_1)
        sample_prim_1.GetAttribute("xformOp:translate").Set((-1000, -1000, -1000))
        _, sample_prim_path_2 = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        sample_prim_2 = self._stage.GetPrimAtPath(sample_prim_path_2)
        sample_prim_2.GetAttribute("xformOp:translate").Set((-1000, -1000, -1000))

        _, surface_prim_path_1 = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        surface_prim_1 = self._stage.GetPrimAtPath(surface_prim_path_1)
        surface_offset_1 = (0, 0, 500)
        surface_prim_1.GetAttribute("xformOp:translate").Set(surface_offset_1)
        _, surface_prim_path_2 = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        surface_prim_2 = self._stage.GetPrimAtPath(surface_prim_path_2)
        surface_offset_2 = (0, 0, -500)
        surface_prim_2.GetAttribute("xformOp:translate").Set(surface_offset_2)

        # Setup relationships
        for target in [sample_prim_path_1, sample_prim_path_2]:
            omni.kit.commands.execute(
                "AddRelationshipTarget",
                relationship=self._scatter_node_prim.GetAttribute("inputs:prims"),
                target=target,
            )
        for target in [surface_prim_path_1, surface_prim_path_2]:
            omni.kit.commands.execute(
                "AddRelationshipTarget",
                relationship=self._scatter_node_prim.GetAttribute("inputs:surfacePrims"),
                target=target,
            )

        self._scatter_node.get_attribute("inputs:seed").set(1410)
        await self._controller.evaluate(self._graph)

        sampled_point_1 = np.array(sample_prim_1.GetAttribute("xformOp:translate").Get())
        sampled_point_2 = np.array(sample_prim_2.GetAttribute("xformOp:translate").Get())
        is_1_on_cube_1 = on_cube(sampled_point_1 - np.array(surface_offset_1))
        is_1_on_cube_2 = on_cube(sampled_point_1 - np.array(surface_offset_2))
        is_2_on_cube_1 = on_cube(sampled_point_2 - np.array(surface_offset_1))
        is_2_on_cube_2 = on_cube(sampled_point_2 - np.array(surface_offset_2))
        is_on_mesh = (is_1_on_cube_1 or is_1_on_cube_2) and (is_2_on_cube_1 or is_2_on_cube_2)
        self.assertTrue(is_on_mesh)

    async def test_point_instancer_sample(self):
        N = 100  # point samples per prototype
        pi = self._stage.DefinePrim("/PI", "PointInstancer")
        _, proto1_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        _, proto2_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Sphere")
        pi.GetAttribute("protoIndices").Set([0] * N + [1] * N)

        _, mesh_surface_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Torus")
        _, mesh_sample_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cone")

        # Setup relationships
        for target in [pi.GetPath(), mesh_sample_path]:
            omni.kit.commands.execute(
                "AddRelationshipTarget",
                relationship=self._scatter_node_prim.GetAttribute("inputs:prims"),
                target=target,
            )
        for target in [mesh_surface_path]:
            omni.kit.commands.execute(
                "AddRelationshipTarget",
                relationship=self._scatter_node_prim.GetAttribute("inputs:surfacePrims"),
                target=target,
            )

        self._scatter_node.get_attribute("inputs:seed").set(1410)
        await self._controller.evaluate(self._graph)

        pi_has_positions = len(pi.GetAttribute("positions").Get()) == len(pi.GetAttribute("protoIndices").Get())
        self.assertTrue(pi_has_positions)

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

        _, surface_prim_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        surface_prim = self._stage.GetPrimAtPath(surface_prim_path)
        surface_offset = (0, 0, 0)
        surface_prim.GetAttribute("xformOp:translate").Set(surface_offset)

        # Setup relationships
        for target in sample_prim_paths:
            omni.kit.commands.execute(
                "AddRelationshipTarget",
                relationship=self._scatter_node_prim.GetAttribute("inputs:prims"),
                target=target,
            )
        for target in [surface_prim_path]:
            omni.kit.commands.execute(
                "AddRelationshipTarget",
                relationship=self._scatter_node_prim.GetAttribute("inputs:surfacePrims"),
                target=target,
            )

        self._scatter_node.get_attribute("inputs:seed").set(1410)
        await self._controller.evaluate(self._graph)

        sampled_points = np.concatenate(
            [np.array(prim.GetAttribute("xformOp:translate").Get()).reshape(1, 3) for prim in sample_prims]
        )

        num_per_side = [0] * 6
        num_per_side[0] += (np.isclose(sampled_points[:, 0], 50.0)).sum()
        num_per_side[1] += (np.isclose(sampled_points[:, 0], -50.0)).sum()
        num_per_side[2] += (np.isclose(sampled_points[:, 1], 50.0)).sum()
        num_per_side[3] += (np.isclose(sampled_points[:, 1], -50.0)).sum()
        num_per_side[4] += (np.isclose(sampled_points[:, 2], 50.0)).sum()
        num_per_side[5] += (np.isclose(sampled_points[:, 2], -50.0)).sum()

        std = np.sqrt(num_samples * 5 / 36)

        is_distributed = (np.min(num_per_side) >= num_samples / 6 - 2 * std) and (
            np.max(num_per_side) <= num_samples / 6 + 2 * std
        )

        self.assertTrue(is_distributed)

    async def test_geomsubset(self):
        "Test sampling from GeomSubset."
        N = 1000  # point samples per prototype
        pi = self._stage.DefinePrim("/PI", "PointInstancer")
        _, proto1_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        UsdGeom.PointInstancer(pi).CreatePrototypesRel().SetTargets([proto1_path])
        pi.GetAttribute("protoIndices").Set([0] * N)
        pi.GetAttribute("positions").Set([[0, 0, 0]])

        _, surface_prim_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        surface_prim = self._stage.GetPrimAtPath(surface_prim_path)
        surface_offset = (0, 0, 0)
        subset = self._stage.DefinePrim(f"{surface_prim_path}/sub", "GeomSubset")
        subset.GetAttribute("indices").Set(
            [0]
        )  # this corresponds to +Z side of the cube - index prior to Kit 104.2+release.30.e51bf939 was index 3
        subset_path = subset.GetPath()

        # Setup relationships
        omni.kit.commands.execute(
            "AddRelationshipTarget",
            relationship=self._scatter_node_prim.GetAttribute("inputs:prims"),
            target=pi.GetPath(),
        )

        for target in [subset_path]:
            omni.kit.commands.execute(
                "AddRelationshipTarget",
                relationship=self._scatter_node_prim.GetAttribute("inputs:surfacePrims"),
                target=target,
            )

        self._scatter_node.get_attribute("inputs:seed").set(1410)
        await self._controller.evaluate(self._graph)
        sampled_points = np.array(pi.GetAttribute("positions").Get())

        is_on_face = (
            np.all(np.logical_and(sampled_points[:, 0] >= -50, sampled_points[:, 0] <= 50))
            and np.all(np.logical_and(sampled_points[:, 1] >= -50, sampled_points[:, 1] <= 50))
            and np.all(np.isclose(sampled_points[:, 2], 50.0))
        )
        self.assertTrue(is_on_face)

    async def test_coverage_scaled_meshes(self):
        """Test that the polygons on a scaled mesh are sampled uniformly."""
        N = 100  # point samples per prototype
        pi = self._stage.DefinePrim("/PI", "PointInstancer")
        _, proto1_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        UsdGeom.PointInstancer(pi).CreatePrototypesRel().SetTargets([proto1_path])
        pi.GetAttribute("protoIndices").Set([0] * N)
        pi.GetAttribute("positions").Set([[0, 0, 0]])

        _, surface_prim_path_1 = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        surface_prim_1 = self._stage.GetPrimAtPath(surface_prim_path_1)
        # surface_prim_1_offset = (10000, 10000, 10000)
        surface_prim_1.GetAttribute("xformOp:translate").Set((10000, 10000, 10000))
        surface_prim_1.GetAttribute("xformOp:scale").Set((0.01, 0.01, 0.01))
        _, surface_prim_path_2 = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        surface_prim_2 = self._stage.GetPrimAtPath(surface_prim_path_2)
        surface_prim_2.GetAttribute("xformOp:scale").Set((1, 1, 1))

        # Setup relationships
        omni.kit.commands.execute(
            "AddRelationshipTarget",
            relationship=self._scatter_node_prim.GetAttribute("inputs:prims"),
            target=pi.GetPath(),
        )
        for target in [surface_prim_path_1, surface_prim_path_2]:
            omni.kit.commands.execute(
                "AddRelationshipTarget",
                relationship=self._scatter_node_prim.GetAttribute("inputs:surfacePrims"),
                target=target,
            )

        self._scatter_node.get_attribute("inputs:seed").set(1410 + 122)

        # Take 100 samples
        small_cube_ratios = []
        for _ in range(100):
            await self._controller.evaluate(self._graph)
            sampled_points = np.array(pi.GetAttribute("positions").Get())
            # Assert points on surface
            on_small_cube = num_on_cube(sampled_points - np.array((10000, 10000, 10000)), scale=0.01)
            on_large_cube = num_on_cube(sampled_points)
            self.assertTrue(on_small_cube + on_large_cube == N)

            small_cube_ratios.append(on_small_cube / N)

        small_cube_ratio_mean = np.mean(small_cube_ratios)
        np.testing.assert_allclose(small_cube_ratio_mean, 0.0, atol=0.01)

    async def test_normal_offset(self):
        """Test that samples are being offset correctly."""
        N = 1000  # point samples per prototype
        pi = self._stage.DefinePrim("/PI", "PointInstancer")
        _, proto1_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        UsdGeom.PointInstancer(pi).CreatePrototypesRel().SetTargets([proto1_path])
        pi.GetAttribute("protoIndices").Set([0] * N)
        pi.GetAttribute("positions").Set([[0, 0, 0]])

        _, surface_prim_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        surface_prim = self._stage.GetPrimAtPath(surface_prim_path)
        # Setup relationships
        omni.kit.commands.execute(
            "AddRelationshipTarget",
            relationship=self._scatter_node_prim.GetAttribute("inputs:prims"),
            target=pi.GetPath(),
        )
        omni.kit.commands.execute(
            "AddRelationshipTarget",
            relationship=self._scatter_node_prim.GetAttribute("inputs:surfacePrims"),
            target=surface_prim_path,
        )

        self._scatter_node.get_attribute("inputs:seed").set(42)
        self._scatter_node.get_attribute("inputs:normalOffset").set(100)
        await self._controller.evaluate(self._graph)

        sampled_points = np.array(pi.GetAttribute("positions").Get())
        # with an offset of 100, should be on a cube that is 300x300x300
        num_valid = num_on_cube(sampled_points, scale=3)
        self.assertTrue(num_valid == N)

    async def test_scatter_moving_surface(self):
        cubes = rep.create.cube()
        plane = rep.create.plane(scale=0.01)

        positions = [(-100, 0, 100), (100, 0, -100)]

        with rep.trigger.on_frame():
            with plane:
                rep.modify.pose(position=rep.distribution.sequence(positions))
            with cubes:
                rep.randomizer.scatter_2d(surface_prims=plane)

        await rep.orchestrator.step_async()
        cube_pose = cubes.get_output_prims()["prims"][0].GetAttribute("xformOp:translate").Get()
        np.testing.assert_allclose(cube_pose, np.array(positions[0]), atol=1.0)
        await rep.orchestrator.step_async()
        cube_pose = cubes.get_output_prims()["prims"][0].GetAttribute("xformOp:translate").Get()
        np.testing.assert_allclose(cube_pose, np.array(positions[1]), atol=1.0)

    async def test_scatter_2d_double_no_col(self):
        plane = rep.create.plane(scale=10)
        cube = rep.create.cube()
        sphere = rep.create.sphere()
        torus = rep.create.torus()
        with rep.trigger.on_time(interval=1):
            traversable_plane = rep.get.prim_at_path(plane.get_output("prims")[0])
            get_cube = rep.get.prim_at_path(cube.get_output("prims")[0])
            get_sphere = rep.get.prim_at_path(sphere.get_output("prims")[0])
            get_torus = rep.get.prim_at_path(torus.get_output("prims")[0])

            with get_cube:
                scatter = rep.randomizer.scatter_2d(
                    traversable_plane, no_coll_prims=[get_sphere, get_torus], check_for_collisions=True
                )

        await rep.orchestrator.step_async()

        self.assertEqual(len(scatter.get_input("noCollPrims")), 2)
        upstream_exec_node = scatter.node.get_attribute("inputs:execIn").get_upstream_connections()[0].get_node()
        self.assertEqual(upstream_exec_node.get_type_name(), "omni.graph.action.RationalTimeSyncGate")
        self.assertEqual(upstream_exec_node.get_attribute("inputs:execIn").get_upstream_connection_count(), 4)


def on_cube(point: np.ndarray) -> bool:
    """
    Returns whether a point is on the surface of a cube, centered at origin, with sidelength of 100 units
    """

    on_x_side = (
        (np.isclose(point[0], 50.0) or np.isclose(point[0], -50.0))
        and (-50.0 <= point[1] <= 50.0)
        and (-50.0 <= point[2] <= 50.0)
    )
    on_y_side = (
        (np.isclose(point[1], 50.0) or np.isclose(point[1], -50.0))
        and (-50.0 <= point[0] <= 50.0)
        and (-50.0 <= point[2] <= 50.0)
    )
    on_z_side = (
        (np.isclose(point[2], 50.0) or np.isclose(point[2], -50.0))
        and (-50.0 <= point[1] <= 50.0)
        and (-50.0 <= point[0] <= 50.0)
    )

    return on_x_side or on_y_side or on_z_side


def num_on_cube(points: np.ndarray, scale=1) -> bool:
    """
    Returns the number of points in a batch which are on the surface of a cube
    """
    edge = 100.0 * scale / 2
    on_x = np.logical_and.reduce(
        (
            np.logical_and(points[:, 1] >= -edge, points[:, 1] <= edge),
            np.logical_and(points[:, 2] >= -edge, points[:, 2] <= edge),
            np.logical_or(np.isclose(points[:, 0], edge), np.isclose(points[:, 0], -edge)),
        )
    )
    on_y = np.logical_and.reduce(
        (
            np.logical_and(points[:, 0] >= -edge, points[:, 0] <= edge),
            np.logical_and(points[:, 2] >= -edge, points[:, 2] <= edge),
            np.logical_or(np.isclose(points[:, 1], edge), np.isclose(points[:, 1], -edge)),
        )
    )
    on_z = np.logical_and.reduce(
        (
            np.logical_and(points[:, 0] >= -edge, points[:, 0] <= edge),
            np.logical_and(points[:, 1] >= -edge, points[:, 1] <= edge),
            np.logical_or(np.isclose(points[:, 2], edge), np.isclose(points[:, 2], -edge)),
        )
    )

    return np.sum(np.logical_or.reduce((on_x, on_y, on_z)))


def convert_poly_to_tri(vertices: np.ndarray, faces_indices: np.ndarray, face_vertex_counts: np.ndarray) -> np.ndarray:
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
