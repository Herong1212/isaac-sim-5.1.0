# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

import asyncio
import os
import shutil
import unittest

import carb
import omni.kit
import omni.replicator.core as rep
import yaml
from omni.replicator.replicator_yaml import parse


class TestLightParameters(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        # Create a new stage
        await omni.usd.get_context().new_stage_async()

        # self.out_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "_out")
        self.out_dir = carb.tokens.get_tokens_interface().resolve("${temp}/test_object_parameters")
        self.yaml_dir = os.path.join(self.out_dir, "yaml_dir")
        os.makedirs(self.yaml_dir, exist_ok=True)

        await omni.kit.app.get_app().next_update_async()

    async def test_light_temp(self):
        """Test modifying light temp argument."""
        data = {
            "lights": {
                "create.light": {
                    "light_type": "sphere",
                    "count": 2,
                    "temperature": {"distribution.uniform": {"lower": 1000, "upper": 2000}},
                }
            }
        }

        yaml_file_path = os.path.join(self.yaml_dir, "test_data.yaml")
        self._write_yaml(data, yaml_file_path)

        parse(yaml_path=yaml_file_path)

        await omni.kit.app.get_app().next_update_async()

        stage = omni.usd.get_context().get_stage()

        light_1 = stage.GetPrimAtPath("/Replicator/SphereLight_Xform/SphereLight")
        light_2 = stage.GetPrimAtPath("/Replicator/SphereLight_Xform_01/SphereLight")

        light_1_color_temp = light_1.GetAttribute("inputs:colorTemperature").Get()
        light_2_color_temp = light_2.GetAttribute("inputs:colorTemperature").Get()

        self.assertTrue(light_1_color_temp >= 1000 and light_1_color_temp <= 2000)
        self.assertTrue(light_2_color_temp >= 1000 and light_2_color_temp <= 2000)

    def _write_yaml(self, data, file_path):
        with open(file_path, "w") as file:
            yaml.dump(data, file, default_flow_style=False)
