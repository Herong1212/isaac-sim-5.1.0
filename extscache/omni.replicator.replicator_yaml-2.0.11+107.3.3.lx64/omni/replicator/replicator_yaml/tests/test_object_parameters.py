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

import os
import shutil
import unittest

import carb
import omni.client
import omni.kit
import yaml
from omni.replicator.replicator_yaml import ParserError, parse


class TestObjectParameters(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        # Create a new stage
        await omni.usd.get_context().new_stage_async()

        # self.out_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "_out")
        self.out_dir = carb.tokens.get_tokens_interface().resolve("${temp}/test_object_parameters")
        self.yaml_dir = os.path.join(self.out_dir, "yaml_dir")
        os.makedirs(self.yaml_dir, exist_ok=True)

        await omni.kit.app.get_app().next_update_async()

    async def tearDown(self):
        shutil.rmtree(self.out_dir)

    # FIXME Find an alternative way to test
    @unittest.skipIf(
        omni.client.get_server_info("omniverse://localhost")[0] != omni.client.Result.OK,
        "Unable to reach OV-Content",
    )
    async def test_asset_nucleus(self):
        """Test to load a object from nucleus server."""

        data = {
            "nucleus_server": "omniverse://localhost/",
            "test_scene": {
                "create.from_usd": {
                    "usd": {
                        "value": "NVIDIA/Samples/Marbles/assets/standalone/A_bumper/A_bumper.usd",
                        "property": "nucleus_path",
                    }
                }
            },
        }

        yaml_file_path = os.path.join(self.yaml_dir, "test_data.yaml")
        self._write_yaml(data, yaml_file_path)

        parse(yaml_path=yaml_file_path)

        await omni.kit.app.get_app().next_update_async()

        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath("/Replicator/Ref_Xform/Ref")

        asset_path = "omniverse://localhost/NVIDIA/Samples/Marbles/assets/standalone/A_bumper/A_bumper.usd"
        self.assertTrue(prim.GetMetadata("references").GetAddedOrExplicitItems()[0].assetPath == asset_path)

    async def test_asset_local(self):
        """Test to load a object locally."""

        data = {
            "file_root_dir": os.path.dirname(__file__),
            "test_scene": {"create.from_usd": {"usd": {"value": "data/objects/rocket.usd", "property": "file_path"}}},
        }

        yaml_file_path = os.path.join(self.yaml_dir, "test_data.yaml")
        self._write_yaml(data, yaml_file_path)

        parse(yaml_path=yaml_file_path)

        await omni.kit.app.get_app().next_update_async()

        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath("/Replicator/Ref_Xform/Ref")

        asset_path = os.path.join(os.path.dirname(__file__), "data/objects/rocket.usd")
        self.assertTrue(prim.GetMetadata("references").GetAddedOrExplicitItems()[0].assetPath == asset_path)

    def _write_yaml(self, data, file_path):
        with open(file_path, "w") as file:
            yaml.dump(data, file, default_flow_style=False)
