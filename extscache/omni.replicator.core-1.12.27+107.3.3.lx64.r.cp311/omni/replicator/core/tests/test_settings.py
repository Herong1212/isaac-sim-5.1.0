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

import doctest
import os
import re
import urllib.request
from pathlib import Path

import carb
import omni.kit
import omni.replicator.core as rep
import usdrt
from pxr import PhysxSchema, UsdGeom

TEST_DATA_DIR = Path(os.path.dirname(os.path.realpath(__file__))).joinpath("data")


class TestSettings(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self.golden_dir = os.path.join(TEST_DATA_DIR, "golden")
        await omni.usd.get_context().new_stage_async()
        await omni.kit.app.get_app().next_update_async()

        self._settings = carb.settings.get_settings()

        # Necessary to set attributes correctly
        rep.utils.get_graph()
        await omni.kit.app.get_app().next_update_async()

        rep.set_global_seed(1234)

    async def test_docstrings(self):
        """Test module docstring examples"""
        failures, test_counts = doctest.testmod(rep.settings)
        if failures:
            self.fail(f"Encountered {failures} failures in {test_counts} tests.")

    async def test_set_realtime(self):
        rep.settings.set_render_rtx_realtime(antialiasing="DLSS")

        self.assertEqual(self._settings.get(rep.settings.RENDER_MODE), "RaytracedLighting")
        self.assertEqual(self._settings.get(rep.settings.REALTIME_ANTIALIASING), 3)

    async def test_set_pathtracing(self):
        rep.settings.set_render_pathtraced(samples_per_pixel=124)

        self.assertEqual(self._settings.get(rep.settings.RENDER_MODE), "PathTracing")
        self.assertEqual(self._settings.get(rep.settings.PATHTRACED_TOTAL_SAMPLES_PER_PIXEL), 124)

    async def test_randomize_settings(self):
        rep.settings.carb_settings(
            setting=rep.settings.RENDER_MODE, value=rep.distribution.choice(["RaytracedLighting", "PathTracing"])
        )
        rep.settings.carb_settings(
            setting=rep.settings.PATHTRACED_TOTAL_SAMPLES_PER_PIXEL, value=rep.distribution.uniform(1, 124)
        )
        rep.settings.carb_settings(
            setting="/rtx/sceneDb/ambientLightColor", value=rep.distribution.uniform((0, 0, 0), (1, 1, 1))
        )

        await omni.kit.app.get_app().next_update_async()

        self.assertEqual(self._settings.get(rep.settings.RENDER_MODE), "PathTracing")
        self.assertEqual(self._settings.get(rep.settings.PATHTRACED_TOTAL_SAMPLES_PER_PIXEL), 19)
        self.assertEqual(
            self._settings.get("/rtx/sceneDb/ambientLightColor"),
            [0.838364010947949, 0.511052751597662, 0.987930320162336],
        )

    async def test_carb_settings_docstring_urls(self):
        """Validate that URLs in the `carb_settings` docstring are reachable."""
        doc = rep.settings.carb_settings.__doc__ or ""
        urls = re.findall(r"https?://[^\s)]+", doc)
        urls = [u.rstrip(".,);]") for u in urls]

        self.assertTrue(urls, "No URLs found in carb_settings docstring")

        for url in sorted(set(urls)):
            with self.subTest(url=url):
                try:
                    with urllib.request.urlopen(url, timeout=10) as response:
                        status = getattr(response, "status", response.getcode())
                        self.assertLess(status, 400, f"{url} returned status {status}")
                except Exception as exc:
                    self.fail(f"URL check failed for {url}: {exc}")

    async def test_set_stage_meters_per_unit(self):
        rep.settings.set_stage_meters_per_unit(123)
        stage = omni.usd.get_context().get_stage()
        self.assertTrue(UsdGeom.GetStageMetersPerUnit(stage), 123)

    async def test_set_stage_up_axis(self):
        stage = omni.usd.get_context().get_stage()
        rep.settings.set_stage_up_axis("Z")
        self.assertTrue(UsdGeom.GetStageUpAxis(stage), "Z")

        rep.settings.set_stage_up_axis("Y")
        self.assertTrue(UsdGeom.GetStageUpAxis(stage), "Y")

    async def test_set_physx_delta_time(self):
        physx_delta_time_set = 1.0 / 10.0
        rep.settings.set_physx_timestep(physx_delta_time=physx_delta_time_set)
        stage = omni.usd.get_context().get_stage()

        usdrt_stage = usdrt.Usd.Stage.Attach(omni.usd.get_context().get_stage_id())
        physics_scenes = usdrt_stage.GetPrimsWithTypeName("PhysicsScene")
        self.assertTrue(physics_scenes is not None)

        physx_scene = physics_scenes[0]  # Select the first
        physx_scene = PhysxSchema.PhysxSceneAPI.Apply(stage.GetPrimAtPath(str(physx_scene)))
        physx_delta_time_get = 1.0 / physx_scene.GetTimeStepsPerSecondAttr().Get()

        self.assertEqual(physx_delta_time_get, physx_delta_time_set)
