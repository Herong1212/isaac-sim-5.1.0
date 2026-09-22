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
import omni.kit
import omni.replicator.core as rep


class TestReplicatorYAMLWriter(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        # Create a new stage
        await omni.usd.get_context().new_stage_async()

        torus = rep.create.torus(semantics=[("class", "torus"), ("alias", "donut")])
        sphere = rep.create.sphere(semantics=[("class", "sphere"), ("alias", "ball")])
        cube = rep.create.cube(semantics=[("class", "cube")])

        camera = rep.create.camera(position=(0, 0, 1000))
        self.render_product = rep.create.render_product(camera, (1024, 512))

        # fix seed for consistent result
        test_seed = 1234
        with rep.trigger.on_frame(max_execs=10):
            with rep.create.group([torus, sphere, cube]):
                rep.modify.pose(
                    position=rep.distribution.uniform((-100, -100, -100), (200, 200, 200), seed=test_seed),
                    scale=rep.distribution.uniform(0.1, 2, seed=test_seed),
                )
                rep.randomizer.rotation(seed=test_seed)

        # self.out_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "_out")
        self.out_dir = carb.tokens.get_tokens_interface().resolve("${temp}/test_replicator_yaml_writer")
        os.makedirs(self.out_dir, exist_ok=True)

        await omni.kit.app.get_app().next_update_async()

    async def tearDown(self):
        shutil.rmtree(self.out_dir)

    async def test_overwrite_false_empty_dir(self):
        """Writer will write to disk if overwrite is set to False and dir is empty"""
        writer = rep.WriterRegistry.get("ReplicatorYAMLWriter")
        out_dir = os.path.join(self.out_dir, "overwrite_empty")
        os.makedirs(out_dir, exist_ok=True)
        writer.initialize(output_dir=out_dir, rgb=True, overwrite=False)
        writer.attach([self.render_product])

        await rep.orchestrator.run_until_complete_async()

        for i in range(10):
            image_file_name = f"rgb_{i}.png"

            self.assertTrue(os.path.isfile(os.path.join(out_dir, "data", "rgb", image_file_name)))
