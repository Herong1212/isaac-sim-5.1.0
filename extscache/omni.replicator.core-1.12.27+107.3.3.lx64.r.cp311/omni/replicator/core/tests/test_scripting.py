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
import re
import shutil
import sys
import unittest

import carb
import omni.kit
import omni.replicator.core as rep


class TestScripting(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        await omni.kit.app.get_app().next_update_async()

        self.out_dir = carb.tokens.get_tokens_interface().resolve("${temp}/test_scripting")

    async def tearDown(self):
        shutil.rmtree(self.out_dir)
        await omni.usd.get_context().new_stage_async()

    async def _run_script(self):
        with rep.new_layer():
            camera = rep.create.camera()
            rp = rep.create.render_product(camera, (1024, 1024))

            writer = rep.WriterRegistry.get("BasicWriter")
            writer.initialize(output_dir=self.out_dir, rgb=True)
            writer.attach(rp)

            sphere = rep.create.sphere()
            with rep.trigger.on_frame(max_execs=10):
                with sphere:
                    rep.modify.pose(position=rep.distribution.uniform((0, 0, 0), (10, 10, 10)))

        await rep.orchestrator.run_until_complete_async()

    async def test_run_script_twice(self):
        # Run once
        await self._run_script()
        rgb = [f for f in os.listdir(self.out_dir) if re.search("rgb", f)]
        self.assertEqual(len(rgb), 10)

        # Remove files
        shutil.rmtree(self.out_dir)
        self.assertFalse(os.path.exists(self.out_dir))

        # Run again
        await self._run_script()
        rgb = [f for f in os.listdir(self.out_dir) if re.search("rgb", f)]
        self.assertEqual(len(rgb), 10)
