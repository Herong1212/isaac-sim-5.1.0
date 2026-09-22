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

import numpy as np
import omni.kit.test
import omni.replicator.core as rep
import omni.usd
from omni.replicator.core import utils


def get_prim_at_path(path: str):
    stage = omni.usd.get_context().get_stage()
    return stage.GetPrimAtPath(str(path))


class TestGet(omni.kit.test.AsyncTestCaseFailOnLogError):
    async def setUp(self):

        await omni.usd.get_context().new_stage_async()

    async def test_get_prim_at_path(self):
        cube = rep.create.cube()
        sphere = rep.create.sphere()

        cube_xform = rep.get.prim_at_path("/Replicator/Cube_Xform")

        with cube_xform:
            rep.modify.pose(position=(100, 0, 0))

        await omni.kit.app.get_app().next_update_async()

        cube_prim = get_prim_at_path(cube.node.get_attribute("outputs:prims").get()[0])
        cube_position = np.array(cube_prim.GetAttribute("xformOp:translate").Get())
        np.testing.assert_allclose(cube_position, np.array([100, 0, 0]))

        self.assertTrue(len(cube_xform.node.get_attribute("outputs:prims").get()) == 1)

    async def test_get_prim_at_path_list(self):
        cube = rep.create.cube()
        sphere = rep.create.sphere()
        cone = rep.create.cone()

        cube_cone_xform = rep.get.prim_at_path(["/Replicator/Cube_Xform", "/Replicator/Cone_Xform"])

        with cube_cone_xform:
            rep.modify.pose(position=(100, 0, 0))

        await omni.kit.app.get_app().next_update_async()

        cube_prim = cube.get_output_prims()["prims"][0]
        cube_position = np.array(cube_prim.GetAttribute("xformOp:translate").Get())
        np.testing.assert_allclose(cube_position, np.array([100, 0, 0]))

        cone_prim = cone.get_output_prims()["prims"][0]
        cone_position = np.array(cone_prim.GetAttribute("xformOp:translate").Get())
        np.testing.assert_allclose(cone_position, np.array([100, 0, 0]))

        self.assertTrue(len(cube_cone_xform.get_output_prims()["prims"]) == 2)

    async def test_get_prims(self):
        cube = rep.create.cube()
        sphere = rep.create.sphere()

        cube_xform = rep.get.prims("^\/Replicator\/Cube_Xform$")

        with cube_xform:
            rep.modify.pose(position=(100, 0, 0))

        await omni.kit.app.get_app().next_update_async()

        cube_prim = cube.get_output_prims()["prims"][0]
        cube_position = np.array(cube_prim.GetAttribute("xformOp:translate").Get())

        np.testing.assert_allclose(cube_position, np.array([100, 0, 0]))

    async def test_get_prims_immediate(self):
        # Verify prims output is immediately available after node creation
        cube = rep.create.cube()
        sphere = rep.create.sphere()

        get = rep.get.prims(prim_types=["Mesh"])
        get_output = set([str(p) for p in get.get_output("prims")])

        gt = set(["/Replicator/Cube_Xform/Cube", "/Replicator/Sphere_Xform/Sphere"])

        self.assertEqual(get_output, gt, f"Expected {gt}, got {get_output}")

    async def test_get_prims_at_paths_immediate(self):
        # Verify prims output is immediately available after node creation
        cube = rep.create.cube()
        sphere = rep.create.sphere()

        get = rep.get.prim_at_path(["/Replicator/Cube_Xform"])
        get_output = get.get_output("prims")

        gt = ["/Replicator/Cube_Xform"]

        self.assertEqual(get_output, gt, f"Expected {gt}, got {get_output}")
