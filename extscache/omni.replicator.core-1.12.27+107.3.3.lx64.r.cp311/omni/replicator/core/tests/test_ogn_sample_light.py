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


class TestOgnSampleLight(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        rep.set_global_seed(1234)

        self._stage = omni.usd.get_context().get_stage()
        self._controller = og.Controller()
        self._graph = self._controller.create_graph("/World/PushGraph")

        self._sample_node = self._controller.create_node(("sample", self._graph), "omni.replicator.core.OgnSampleLight")
        self._sample_node_prim = self._stage.GetPrimAtPath(self._sample_node.get_prim_path())

    async def tearDown(self):
        await omni.usd.get_context().new_stage_async()

    @unittest.skipIf(os.getenv("ETM_ACTIVE"), "skipped in ETM, test takes too long on Windows CI")
    async def test_light_distribution(self):
        """Test sampling attributes of light."""
        sample_prims = list()
        sample_prim_paths = list()
        num_samples = 1000
        light_prim_types = ["DistantLight", "SphereLight", "RectLight", "DiskLight", "CylinderLight", "DomeLight"]
        # create a bunch of samples from different types of lights
        for i in range(num_samples):
            prim_path = f"/sample{i+1}"
            omni.kit.commands.execute(
                "CreatePrimCommand", prim_path=prim_path, prim_type=light_prim_types[i % len(light_prim_types)]
            )
            sample_prim = self._stage.GetPrimAtPath(prim_path)
            sample_prim_paths.append(prim_path)
            sample_prims.append(sample_prim)

        # setup relationships
        self._add_relationship_target("inputs:prims", sample_prim_paths)
        self._sample_node.get_attribute("inputs:seed").set(1410)

        color_min = np.array([0.5, 0.5, 0.5])
        color_max = np.array([0.75, 0.75, 0.75])
        color_mean = (color_max + color_min) / 2
        color_std = (color_max - color_min) / np.sqrt(12)
        intensity_range = np.array([1000, 50000])
        intensity_mean = np.mean(intensity_range)
        intensity_std = (intensity_range[1] - intensity_range[0]) / np.sqrt(12)
        temperature_range = np.array([2000, 6000])
        temperature_mean = np.mean(temperature_range)
        temperature_std = (temperature_range[1] - temperature_range[0]) / np.sqrt(12)

        self._sample_node.get_attribute("inputs:colorMin").set(color_min)
        self._sample_node.get_attribute("inputs:colorMax").set(color_max)
        self._sample_node.get_attribute("inputs:intensityRange").set(intensity_range)
        self._sample_node.get_attribute("inputs:enableTemperature").set(False)
        await self._controller.evaluate(self._graph)
        # test that enableTemperature=False doesn't change temperature
        temperatures = [prim.GetAttribute("inputs:colorTemperature").Get() for prim in sample_prims]
        self.assertTrue(np.all(np.isclose(temperatures, 6500.0)))

        self._sample_node.get_attribute("inputs:enableTemperature").set(True)
        self._sample_node.get_attribute("inputs:temperatureRange").set(temperature_range)
        await self._controller.evaluate(self._graph)
        # test that all attributes are properly randomized
        colors = np.array([np.array(prim.GetAttribute("inputs:color").Get()) for prim in sample_prims])
        intensities = np.array([prim.GetAttribute("inputs:intensity").Get() for prim in sample_prims])
        temperatures = np.array([prim.GetAttribute("inputs:colorTemperature").Get() for prim in sample_prims])

        self.assertTrue(np.all(np.logical_and(color_min <= colors, colors <= color_max)))
        self.assertTrue(np.all(np.isclose(np.mean(colors, axis=0), color_mean, atol=0.05)))
        self.assertTrue(np.all(np.isclose(np.std(colors, axis=0), color_std, atol=0.01)))

        self.assertTrue(np.all(np.logical_and(intensity_range[0] <= intensities, intensities <= intensity_range[1])))
        self.assertTrue(np.all(np.isclose(np.mean(intensities), intensity_mean, atol=0.05 * intensity_mean)))
        self.assertTrue(np.all(np.isclose(np.std(intensities), intensity_std, atol=0.05 * intensity_std)))

        self.assertTrue(
            np.all(np.logical_and(temperature_range[0] <= temperatures, temperatures <= temperature_range[1]))
        )
        self.assertTrue(np.all(np.isclose(np.mean(temperatures), temperature_mean, atol=0.05 * temperature_mean)))
        self.assertTrue(np.all(np.isclose(np.std(temperatures), temperature_std, atol=0.05 * temperature_std)))

    def _add_relationship_target(self, attribute, prim_paths):
        for target in prim_paths:
            omni.kit.commands.execute(
                "AddRelationshipTarget", relationship=self._sample_node_prim.GetAttribute(attribute), target=target
            )
