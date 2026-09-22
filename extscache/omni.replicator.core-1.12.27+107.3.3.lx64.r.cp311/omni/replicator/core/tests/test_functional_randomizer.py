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

import random

import numpy as np
import omni.kit
import omni.replicator.core as rep
import omni.replicator.core.functional.randomizer as frand
import omni.usd
from omni.kit.test import AsyncTestCase


class TestScatterFunctions(AsyncTestCase):
    """Tests for :pyfunc:`scatter_2d` and :pyfunc:`scatter_3d` in ``functional.randomizer``.

    The goal is to exercise every branch in these two helpers so that they reach
    100 percent line coverage.  All tests run inside the OmniKit event-loop and
    therefore need to be asynchronous.
    """

    async def setUp(self):
        """Create a fresh USD stage for every test."""
        await omni.usd.get_context().new_stage_async()
        self._stage = omni.usd.get_context().get_stage()

    async def tearDown(self):
        """Reset the stage so tests stay fully isolated."""
        await omni.usd.get_context().new_stage_async()

    # ---------------------------------------------------------------------
    # scatter_2d
    # ---------------------------------------------------------------------
    async def test_scatter_2d_errors(self):
        """Verify the early error branches in ``scatter_2d``."""
        _, cube_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        cube_prim = self._stage.GetPrimAtPath(cube_path)

        # 1) Missing surface prims.
        with self.assertRaises(ValueError):
            frand.scatter_2d(prims=cube_prim, surface_prims=None)

        # 2) Missing prims.
        with self.assertRaises(ValueError):
            frand.scatter_2d(prims=None, surface_prims=cube_prim)

        # 3) Unsupported RNG type → NotImplementedError.
        with self.assertRaises(NotImplementedError):
            frand.scatter_2d(prims=cube_prim, surface_prims=cube_prim, rng=random.Random())

    async def test_scatter_2d_success_paths(self):
        """Exercise both execution branches for ``scatter_2d`` (with and without collision checking)."""
        rng_rep = rep.rng.ReplicatorRNG()
        rng_np = np.random.default_rng(seed=123)

        # Dummy prim to be scattered.
        _, sample_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Sphere")
        sample_prim = self._stage.GetPrimAtPath(sample_path)

        # Surface mesh on which to scatter.
        _, surface_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        surface_prim = self._stage.GetPrimAtPath(surface_path)

        # Path 1: No-collision branch with no explicit RNG.
        frand.scatter_2d(prims=sample_prim, surface_prims=surface_prim, check_for_collisions=False)

        # Path 2: Collision-checking branch, with explicit replicator RNG.
        _, no_coll_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cone")
        no_coll_prim = self._stage.GetPrimAtPath(no_coll_path)
        frand.scatter_2d(
            prims=[sample_prim],  # list input exercises list-conversion branch
            surface_prims=[surface_prim],
            no_collision_prims=[no_coll_prim],
            check_for_collisions=True,
            rng=rng_rep,  # explicit replicator RNG path
        )

        # Path 3: Collision-checking branch, with explicit numpy RNG.
        _, no_coll_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cone")
        no_coll_prim = self._stage.GetPrimAtPath(no_coll_path)
        frand.scatter_2d(
            prims=[sample_prim],  # list input exercises list-conversion branch
            surface_prims=[surface_prim],
            no_collision_prims=[no_coll_prim],
            check_for_collisions=True,
            rng=rng_np,  # explicit replicator RNG path
        )

    # ---------------------------------------------------------------------
    # scatter_3d
    # ---------------------------------------------------------------------
    async def test_scatter_3d_errors(self):
        """Cover error branches of ``scatter_3d``."""
        # Create a prim so that *prims* argument is valid.
        _, sample_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Sphere")
        sample_prim = self._stage.GetPrimAtPath(sample_path)

        # 1) No volume prims + unbounded extents – should raise ValueError.
        with self.assertRaises(ValueError):
            frand.scatter_3d(prims=sample_prim)

        # 2) Unsupported RNG type.
        _, volume_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        volume_prim = self._stage.GetPrimAtPath(volume_path)
        with self.assertRaises(NotImplementedError):
            frand.scatter_3d(prims=sample_prim, volume_prims=volume_prim, rng=random.Random())

    async def test_scatter_3d_success_paths(self):
        """Exercise all non-error branches of ``scatter_3d``."""

        rng_rep = rep.rng.ReplicatorRNG()
        rng_np = np.random.default_rng(seed=123)

        # Prim to scatter.
        _, sample_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Sphere")
        sample_prim = self._stage.GetPrimAtPath(sample_path)

        # Volume shell.
        _, volume_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        volume_prim = self._stage.GetPrimAtPath(volume_path)

        # Path 1: No-collision branch with no explicit RNG.
        frand.scatter_3d(prims=sample_prim, volume_prims=volume_prim)

        # Path 2: Collision-checking branch, with explicit replicator RNG.
        _, no_coll_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cone")
        no_coll_prim = self._stage.GetPrimAtPath(no_coll_path)
        frand.scatter_3d(
            prims=[sample_prim],
            volume_prims=[volume_prim],
            no_collision_prims=[no_coll_prim],
            check_for_collisions=True,
            rng=rng_rep,
        )

        # -------------------------------------------------------------
        # Path 3: Auto-generated enclosing volume (volume_prims=None) with explicit numpy RNG.
        # -------------------------------------------------------------
        # The voxel-overlap cache maintained in ``VoxelUtils`` can retain
        # state across multiple scatter_3d invocations on the same stage.
        # To keep the test isolated—and avoid edge-cases inside
        # ``_rm_overlap_direct``—we create a fresh stage before triggering
        # the *extents-only* code-path.

        bounded_extents = ((-10.0, -10.0, -10.0), (10.0, 10.0, 10.0))
        frand.scatter_3d(
            prims=sample_prim,
            volume_prims=None,
            extents=bounded_extents,
            prevent_vol_overlap=True,  # test overlap pruning works without errors
            rng=rng_np,
        )

    async def test_scatter_2d_heterogeneous_surfaces(self):
        """Test that scatter_2d works with heterogeneous surfaces.

        The surfaces have different numbers of polygons
        """
        spheres = rep.functional.create_batch.sphere(count=10)
        surfaces = [
            rep.functional.create.plane(position=(0, -100, 0), scale=(2, 1, 2)),
            rep.functional.create.torus(position=(0, 100, 0)),
        ]
        # Make sure no errors
        rng = rep.rng.ReplicatorRNG()
        rep.functional.randomizer.scatter_2d(prims=spheres, surface_prims=surfaces, rng=rng)

        # Ensure that the spheres are scattered on both surfaces
        sphere_positions = []
        for sphere in spheres:
            sphere_positions.append(rep.functional.utils.get_world_transform(sphere).GetTranslation())
        sphere_positions_np = np.array(sphere_positions)

        num_on_plane = np.sum(sphere_positions_np[:, 1] == -100)
        self.assertGreater(num_on_plane, 0)  # at least one sphere on plane
        self.assertGreater((10 - num_on_plane), 0)  # at least one sphere on torus
