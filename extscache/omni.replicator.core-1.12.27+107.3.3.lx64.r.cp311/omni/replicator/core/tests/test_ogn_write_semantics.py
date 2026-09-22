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

import omni.graph.core as og
import omni.kit
import omni.replicator.core as rep
import omni.usd


class TestOgnWritePrimAttribute(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        rep.set_global_seed(1234)

        self._stage = omni.usd.get_context().get_stage()
        self._controller = og.Controller()
        self._graph = self._controller.create_graph("/World/PushGraph")

        self._semantics_node = self._controller.create_node(
            ("semantics", self._graph), "omni.replicator.core.OgnWriteSemantics"
        )
        self._semantics_node_prim = self._stage.GetPrimAtPath(self._semantics_node.get_prim_path())

    async def tearDown(self):
        await omni.usd.get_context().new_stage_async()

    async def test_write_semantics(self):
        """Test assigning semantics."""
        cones = [self._stage.DefinePrim(f"/World/Cone_{i}", "Cone") for i in range(10)]

        for target in [c.GetPath() for c in cones]:
            omni.kit.commands.execute(
                "AddRelationshipTarget",
                relationship=self._semantics_node_prim.GetAttribute("inputs:prims"),
                target=target,
            )
        self._semantics_node.get_attribute("inputs:semantics").set(["class:sphere", "material:rubber"])

        await self._controller.evaluate(self._graph)

        for cone in cones:
            semantics = rep.utils.parse_semantics(cone)
            self.assertEqual(set([("class", "sphere"), ("material", "rubber")]), set(semantics))
