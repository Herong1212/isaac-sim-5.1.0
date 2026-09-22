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
import subprocess
import time
import unittest
from pathlib import Path
from sys import platform

import carb
import carb.settings
import numpy as np
import omni.kit
import omni.kit.app
import omni.replicator.core as rep
import omni.usd
import psutil
from omni.usd._impl.utils import get_prim_at_path
from omni.usd.commands import DeletePrimsCommand
from pxr import Sdf


class TestExtension(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        if os.getenv("ETM_ACTIVE"):
            self.skipTest("skip in ETM to keep tests lean")

        await omni.usd.get_context().new_stage_async()
        await omni.kit.app.get_app().next_update_async()
        self.out_dir = carb.tokens.get_tokens_interface().resolve("${temp}/test_extension")

        rep.utils.get_graph()
        await omni.kit.app.get_app().next_update_async()
        rep.BackendDispatch.set_max_queue_size(10)

        manager = omni.kit.app.get_app().get_extension_manager()
        ext_id = manager.get_extension_id_by_module("omni.replicator.core")
        ext_path = manager.get_extension_path(ext_id)

        # Find snippets
        snippets_dir = str(Path(ext_path).joinpath("snippets").as_posix())
        self.snippets = []
        for snippet in os.listdir(Path(snippets_dir).as_posix()):
            if snippet.startswith("snippet") and snippet.endswith(".py"):
                self.snippets.append(Path(snippets_dir).joinpath(snippet).as_posix())

    async def tearDown(self):
        await rep.orchestrator.stop_async()
        rep.BackendDispatch.set_max_queue_size(1000)
        shutil.rmtree(self.out_dir, True)
        await omni.usd.get_context().new_stage_async()

    async def run_until_stop(self):
        await rep.orchestrator.run_until_complete_async()
        rep.BackendDispatch.wait_until_done()

    async def test_replicator_item_reuse(self):
        sphere_ = rep.create.sphere(as_mesh=False)
        cube_ = rep.create.cube(as_mesh=False)

        sphere = rep.get.xform("Sphere")
        cube = rep.get.xform("Cube")

        with sphere:
            rep.modify.attribute("radius", rep.distribution.uniform(1, 10, seed=1234), attribute_type="double")

        with rep.trigger.on_frame():
            with cube:
                rep.modify.pose(position=rep.distribution.uniform((0, 0, 0), (10, 10, 10), seed=1234))
            with cube:
                rep.modify.attribute("size", rep.distribution.uniform(1, 10, seed=1234), attribute_type="double")
            with sphere:
                rep.modify.pose(position=rep.distribution.uniform((0, 0, 0), (10, 10, 10), seed=1234))

        sphere_prim = sphere_.get_output_prims()["prims"][0].GetChildren()[0]
        np.set_printoptions(2, suppress=True)

        for _ in range(4):
            await rep.orchestrator.step_async()

        sphere_radius = np.array(sphere_prim.GetAttribute("radius").Get())

        np.testing.assert_allclose(sphere_radius, np.array([9.7902975]))
        sphere_position = np.array(sphere_prim.GetParent().GetAttribute("xformOp:translate").Get())
        np.testing.assert_allclose(sphere_position, np.array([2.636498, 4.410061, 6.098708]))

        cube_prim = cube_.get_output_prims()["prims"][0].GetChildren()[0]

        cube_size = np.array(cube_prim.GetAttribute("size").Get())
        np.testing.assert_allclose(cube_size, np.array([3.355232]))
        cube_position = np.array(cube_prim.GetParent().GetAttribute("xformOp:translate").Get())
        np.testing.assert_allclose(cube_position, np.array([2.636498, 4.410061, 6.098708]))

    async def test_snippets(self):
        for snippet in self.snippets:
            snippet_name = os.path.splitext(os.path.split(snippet)[-1])[0]

            await omni.usd.get_context().new_stage_async()

            print(f"Testing {snippet_name}...")

            # Clear output directory
            shutil.rmtree(self.out_dir, ignore_errors=True)

            # Run snippet
            self.assertTrue(
                omni.kit.app.get_app().get_python_scripting().execute_file(snippet, []),
                f"{snippet_name} did not execute successfully.",
            )
            await omni.kit.app.get_app().next_update_async()
