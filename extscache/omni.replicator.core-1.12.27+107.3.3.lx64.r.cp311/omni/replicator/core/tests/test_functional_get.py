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

import omni.kit.test
import omni.replicator.core.functional as F
import omni.usd


class TestFunctionalGet(omni.kit.test.AsyncTestCaseFailOnLogError):
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        self.stage = omni.usd.get_context().get_stage()

    async def test_prim_at_paths(self):
        # Create a mesh prim
        prim_paths = ["/World/Mesh1"]
        self.stage.DefinePrim(prim_paths[0], "Mesh")

        # Get the prim at path
        prims_at_paths = F.get.prim_at_paths(self.stage, "/World/Mesh1")
        self.assertEqual(len(prims_at_paths), 1)
        self.assertEqual([str(prim.GetPath()) for prim in prims_at_paths], prim_paths)

        # Create a second prim
        prim_paths.append("/World/Cube")
        self.stage.DefinePrim(prim_paths[1], "Cube")
        prims_at_paths2 = F.get.prim_at_paths(self.stage, prim_paths)
        self.assertEqual(len(prims_at_paths2), 2)

        self.assertEqual([str(prim.GetPath()) for prim in prims_at_paths2], prim_paths)
