# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
import shutil
import unittest

import carb
import omni.client
import omni.kit
import yaml
from omni.replicator.replicator_yaml import ParserError, parse


class TestErrorHandling(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        # Create a new stage
        await omni.usd.get_context().new_stage_async()

        # self.out_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "_out")
        self.out_dir = carb.tokens.get_tokens_interface().resolve("${temp}/test_error_handling")
        self.yaml_dir = os.path.join(self.out_dir, "yaml_dir")
        os.makedirs(self.yaml_dir, exist_ok=True)

        await omni.kit.app.get_app().next_update_async()

    async def tearDown(self):
        shutil.rmtree(self.out_dir)

    async def test_wrong_arg(self):
        """Test when wrong arg name is provided."""

        data = {
            "file_root_dir": os.path.dirname(__file__),
            "test_scene": {
                "create.from_usd": {"usd_path": {"value": "data/objects/rocket.usd", "property": "file_path"}}
            },
        }

        yaml_file_path = os.path.join(self.yaml_dir, "test_data.yaml")
        self._write_yaml(data, yaml_file_path)

        with self.assertRaises(ParserError) as context:
            parse(yaml_path=yaml_file_path)

        self.assertTrue(
            f"Error parsing {yaml_file_path}, line 4: \n\t> 4\nomni.replicator.core.scripts.create.from_usd got an unexpected keyword argument usd_path."
            == str(context.exception)
        )

    async def test_missing_arg(self):
        """Test when required arg name is missing."""

        data = {
            "file_root_dir": os.path.dirname(__file__),
            "test_scene": {"create.from_usd": {"semantics": [["class", "scene"]]}},
        }

        yaml_file_path = os.path.join(self.yaml_dir, "test_data.yaml")
        self._write_yaml(data, yaml_file_path)

        with self.assertRaises(ParserError) as context:
            parse(yaml_path=yaml_file_path)

        self.assertTrue(
            f"Error parsing {yaml_file_path}, line 3: \n\t> 3\nArg usd of function omni.replicator.core.scripts.create.from_usd is not an optional arg but no value is provided."
            == str(context.exception)
        )

    def _write_yaml(self, data, file_path):
        with open(file_path, "w") as file:
            yaml.dump(data, file, default_flow_style=False)
