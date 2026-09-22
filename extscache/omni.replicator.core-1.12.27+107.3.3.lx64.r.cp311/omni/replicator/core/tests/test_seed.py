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

import sys
import unittest

import carb
import numpy as np
import omni.graph.core as og
import omni.kit
import omni.replicator.core as rep
from pxr import UsdGeom


class TestSeed(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self._settings = carb.settings.get_settings()
        await omni.usd.get_context().new_stage_async()
        await omni.kit.app.get_app().next_update_async()

        rep.utils.get_graph()
        await omni.kit.app.get_app().next_update_async()  # Currently need to update after graph creation
        carb.settings.get_settings().set("/exts/omni.replicator.core/maxAssetLoadingTime", 0.5)

    async def tearDown(self):
        carb.settings.get_settings().set("/exts/omni.replicator.core/maxAssetLoadingTime", None)

    async def _set_graph(self, seed_a=None, seed_b=None):
        num_frames = 10
        rep.utils.get_graph()
        await omni.kit.app.get_app().next_update_async()  # Currently need to update after graph creation
        with rep.trigger.on_frame(max_execs=num_frames):
            rep.create.cone(count=10, position=rep.distribution.normal((0, 0, 0), (100, 100, 100), seed=seed_a))
            rep.create.cube(count=10, position=rep.distribution.normal((0, 0, 0), (100, 100, 100), seed=seed_b))

    def _get_positions(self):
        stage = omni.usd.get_context().get_stage()
        cones_node = og.Controller().node("/Replicator/SDGPipeline/OgnGroup")
        cubes_node = og.Controller().node("/Replicator/SDGPipeline/OgnGroup_02")
        cone_prims = [stage.GetPrimAtPath(str(p)) for p in cones_node.get_attribute("outputs:prims").get()]
        cube_prims = [stage.GetPrimAtPath(str(p)) for p in cubes_node.get_attribute("outputs:prims").get()]

        cone_positions = [p.GetAttribute("xformOp:translate").Get() for p in cone_prims]
        cube_positions = [p.GetAttribute("xformOp:translate").Get() for p in cube_prims]

        return cone_positions, cube_positions

    async def test_new_scene_repeatability(self):
        rep.set_global_seed(10)

        await omni.usd.get_context().new_stage_async()
        await omni.kit.app.get_app().next_update_async()
        await self._set_graph()

        await rep.orchestrator.run_until_complete_async()

        positions_a, positions_b = self._get_positions()

        # Ensure positions aren't identical
        with np.testing.assert_raises(AssertionError):
            np.testing.assert_array_equal(positions_a, positions_b)

        N = 3
        for i in range(N):
            await omni.usd.get_context().new_stage_async()
            await omni.kit.app.get_app().next_update_async()
            await self._set_graph()

            if i % 2 == 0:
                rep.orchestrator.preview()

            await rep.orchestrator.run_until_complete_async()

            positions_a_2, positions_b_2 = self._get_positions()

            np.testing.assert_allclose(positions_a, positions_a_2)
            np.testing.assert_allclose(positions_b, positions_b_2)

    async def test_restart_repeatability(self):
        rep.set_global_seed(10)

        await omni.usd.get_context().new_stage_async()
        await omni.kit.app.get_app().next_update_async()

        await self._set_graph()

        await rep.orchestrator.run_until_complete_async()

        positions_a, positions_b = self._get_positions()

        N = 2
        for _ in range(N):
            await omni.kit.app.get_app().next_update_async()
            await rep.orchestrator.run_until_complete_async()

            positions_a_2, positions_b_2 = self._get_positions()

            np.testing.assert_allclose(positions_a, positions_a_2)
            np.testing.assert_allclose(positions_b, positions_b_2)

    async def test_seed_change_repeatability(self):
        """Test changing seed between runs.
        A is set to global seed, and should two generate identical sets at the two seeds.
        B is set to a specific seed and should be consistent across global seed changes.
        """
        positions_a = {}
        positions_b = {}
        await omni.usd.get_context().new_stage_async()
        await omni.kit.app.get_app().next_update_async()

        await self._set_graph(seed_b=1410)

        for _ in range(2):
            for seed in [10, 20]:
                rep.set_global_seed(seed)

                await rep.orchestrator.run_until_complete_async()

                a, b = self._get_positions()

                if seed not in positions_a:
                    positions_a[seed] = a
                else:
                    np.testing.assert_allclose(a, positions_a[seed])
                if seed not in positions_b:
                    positions_b[seed] = b
                else:
                    np.testing.assert_allclose(b, positions_b[seed])

        # Ensure positions for A aren't identical when global seed changed
        with np.testing.assert_raises(AssertionError):
            np.testing.assert_array_equal(positions_a[10], positions_a[20])

        # Ensure positions for B are not affected by global seed
        np.testing.assert_array_equal(positions_b[10], positions_b[20])

    async def test_save_open_repeatability(self):
        rep.set_global_seed(10)

        await omni.usd.get_context().new_stage_async()
        await omni.kit.app.get_app().next_update_async()

        await self._set_graph()
        await rep.orchestrator.run_until_complete_async()
        positions_a, positions_b = self._get_positions()
        rep.orchestrator.preview()
        await omni.kit.app.get_app().next_update_async()

        file_path = carb.tokens.get_tokens_interface().resolve("${temp}/test_seed.usd")
        result = await omni.usd.get_context().save_as_stage_async(file_path)
        await omni.usd.get_context().new_stage_async()
        await omni.kit.app.get_app().next_update_async()

        omni.usd.get_context().open_stage(file_path)
        await omni.kit.app.get_app().next_update_async()

        await rep.orchestrator.run_until_complete_async()
        positions_a_2, positions_b_2 = self._get_positions()

        np.testing.assert_allclose(positions_a, positions_a_2)
        np.testing.assert_allclose(positions_b, positions_b_2)

    async def test_seed_order(self):
        """Ensure that parallel randomization maintains order"""
        rep.set_global_seed(1234)
        for _ in range(10):
            await omni.usd.get_context().new_stage_async()
            await omni.kit.app.get_app().next_update_async()

            rep.utils.get_graph()
            await omni.kit.app.get_app().next_update_async()  # Currently need to update after graph creation

            node1 = rep.settings.carb_settings(
                setting=rep.settings.RENDER_MODE, value=rep.distribution.choice(["RaytracedLighting", "PathTracing"])
            )
            node2 = rep.settings.carb_settings(
                setting=rep.settings.PATHTRACED_TOTAL_SAMPLES_PER_PIXEL, value=rep.distribution.uniform(1, 124)
            )
            node3 = rep.settings.carb_settings(
                setting="/rtx/sceneDb/ambientLightColor", value=rep.distribution.uniform((0, 0, 0), (1, 1, 1))
            )

            await omni.kit.app.get_app().next_update_async()

            self.assertEqual(self._settings.get(rep.settings.RENDER_MODE), "PathTracing")
            self.assertEqual(self._settings.get(rep.settings.PATHTRACED_TOTAL_SAMPLES_PER_PIXEL), 19)

            self.assertEqual(
                self._settings.get("/rtx/sceneDb/ambientLightColor"),
                [0.838364010947949, 0.511052751597662, 0.987930320162336],
            )
