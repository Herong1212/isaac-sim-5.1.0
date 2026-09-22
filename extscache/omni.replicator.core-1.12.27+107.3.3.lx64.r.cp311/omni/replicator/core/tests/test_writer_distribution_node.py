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
import omni.kit
import omni.replicator.core as rep
from omni.replicator.core import AnnotatorRegistry, BackendDispatch, Writer


class TestWriterDistributionNode(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        await omni.kit.app.get_app().next_update_async()

    async def tearDown(self):
        await omni.usd.get_context().new_stage_async()

    async def test_distribution_results(self):
        cube = rep.create.cube(semantics=[("class", "cube")])
        sphere = rep.create.cube(semantics=[("class", "sphere")])
        cylinder = rep.create.cube(semantics=[("class", "cylinder")])

        camera = rep.create.camera()

        distribution_names = ["test_log_uniform", "test_uniform", "test_normal"]

        with rep.trigger.on_frame(max_execs=10):
            with cube:
                rep.modify.pose(
                    position=rep.distribution.log_uniform((0.1, 0.1, 0.1), (1, 1, 1), name=distribution_names[0])
                )
            with sphere:
                rep.modify.pose(
                    position=rep.distribution.uniform((0.1, 0.1, 0.1), (1, 1, 1), name=distribution_names[1])
                )
            with cylinder:
                rep.modify.pose(
                    position=rep.distribution.normal((0.1, 0.1, 0.1), (1, 1, 1), name=distribution_names[2])
                )

        render_product = rep.create.render_product(camera, resolution=(640, 480))

        class CustomWriter(Writer):
            def __init__(self, output_dir):
                self._output_dir = output_dir
                self._backend = BackendDispatch(output_dir=output_dir)

                self.annotators.append(AnnotatorRegistry.get_annotator("bounding_box_3d"))

            def write(self, data):
                distribution_outputs = data["distribution_outputs"]
                transforms = data["bounding_box_3d"]["data"]["transform"]

                for i in range(len(transforms)):
                    distribution_name = distribution_names[i]
                    distribution_output = distribution_outputs[distribution_name]
                    tf = transforms[i]
                    translate = tf[-1, :3]

                    np.testing.assert_allclose(distribution_output[0], translate)

        rep.WriterRegistry.register(CustomWriter)
        writer = rep.WriterRegistry.get("CustomWriter")

        writer.initialize(output_dir="./")

        writer.attach([render_product])

        await rep.orchestrator.run_until_complete_async()
