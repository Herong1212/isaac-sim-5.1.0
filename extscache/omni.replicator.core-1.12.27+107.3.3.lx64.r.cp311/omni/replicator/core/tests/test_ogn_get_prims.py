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

import omni.graph.core as og
import omni.kit.test
import omni.replicator.core as rep
import omni.usd
from pxr import Sdf


class TestGetPrims(omni.kit.test.AsyncTestCase):
    # Before running each test
    async def setUp(self) -> None:
        await omni.usd.get_context().new_stage_async()
        rep.set_global_seed(1234)

        self._stage = omni.usd.get_context().get_stage()
        self._controller = og.Controller()
        self._graph = self._controller.create_graph("/World/PushGraph")

        self.getprims_node = self._controller.create_node(
            ("get_prims", self._graph), "omni.replicator.core.OgnGetPrims"
        )

        # Create a few prims
        # FIXME material raises some node related error messages only during tests
        # dog_mat = rep.create.material_omnipbr(semantics=[("dog", "woof"), ("duck", "quack")])
        rep.create.cube(semantics=[("duck", "quack")])
        rep.create.cone(semantics=[("duck", "quack"), ("cat", "meow")], as_mesh=False)
        rep.create.cylinder(semantics=[("cat", "purrrrr")])
        # rep.create.sphere(material=dog_mat) # FIXME (see fixme above)
        rep.create.sphere(semantics=[("dog", "woof"), ("duck", "quack")], as_mesh=False)  # FIXME (see fixme above)
        rep.create.torus(semantics=[("dog", "woof")])

    async def test_get_prims_by_path(self):
        expected_result = set(
            [
                Sdf.Path("/Replicator/Cube_Xform"),
                Sdf.Path("/Replicator/Cube_Xform/Cube"),
                Sdf.Path("/Replicator/Cone_Xform"),
                Sdf.Path("/Replicator/Cone_Xform/Cone"),
                Sdf.Path("/Replicator/Cylinder_Xform"),
                Sdf.Path("/Replicator/Cylinder_Xform/Cylinder"),
            ]
        )

        regex = r"/Replicator/C"
        self.getprims_node.get_attribute("inputs:pathPattern").set(regex)

        await self._controller.evaluate(self._graph)

        gathered_prims = [Sdf.Path(str(p)) for p in self.getprims_node.get_attribute("outputs:prims").get()]
        self.assertEqual(expected_result, set(gathered_prims))

        regex = r"/Con"
        expected_result.remove(Sdf.Path("/Replicator/Cone_Xform"))
        expected_result.remove(Sdf.Path("/Replicator/Cone_Xform/Cone"))
        self.getprims_node.get_attribute("inputs:pathPatternExclusion").set(regex)

        await self._controller.evaluate(self._graph)

        gathered_prims = [Sdf.Path(str(p)) for p in self.getprims_node.get_attribute("outputs:prims").get()]
        self.assertEqual(expected_result, set(gathered_prims))

    async def test_get_prims_by_type(self):
        expected_result = set(
            [
                Sdf.Path("/Replicator/Cube_Xform/Cube"),
                Sdf.Path("/Replicator/Sphere_Xform/Sphere"),
                Sdf.Path("/Replicator/Cylinder_Xform/Cylinder"),
                Sdf.Path("/Replicator/Torus_Xform/Torus"),
            ]
        )

        prim_types = ["Sphere", "mesh"]
        self.getprims_node.get_attribute("inputs:primTypes").set(prim_types)

        await self._controller.evaluate(self._graph)

        gathered_prims = [Sdf.Path(str(p)) for p in self.getprims_node.get_attribute("outputs:prims").get()]
        self.assertEqual(expected_result, set(gathered_prims))

        prim_types_exclusion = ["Sphere"]
        expected_result.remove(Sdf.Path("/Replicator/Sphere_Xform/Sphere"))
        self.getprims_node.get_attribute("inputs:primTypesExclusion").set(prim_types_exclusion)

        await self._controller.evaluate(self._graph)

        gathered_prims = [Sdf.Path(str(p)) for p in self.getprims_node.get_attribute("outputs:prims").get()]
        self.assertEqual(expected_result, set(gathered_prims))

    async def test_get_prims_by_semantics(self):
        expected_result = set(
            [
                Sdf.Path("/Replicator/Cone_Xform"),
                Sdf.Path("/Replicator/Sphere_Xform"),
                Sdf.Path("/Replicator/Torus_Xform"),
                # Sdf.Path("/Replicator/Looks/OmniPBR"),
            ]
        )

        semantics = [("cat", "meow"), ("dog", "woof")]
        self.getprims_node.get_attribute("inputs:semantics").set([",".join(s) for s in semantics])

        await self._controller.evaluate(self._graph)

        gathered_prims = [Sdf.Path(str(p)) for p in self.getprims_node.get_attribute("outputs:prims").get()]
        self.assertEqual(expected_result, set(gathered_prims))

        semantics_exclusion = [("cat", "meow")]
        expected_result.remove(Sdf.Path("/Replicator/Cone_Xform"))
        # expected_result.remove(Sdf.Path("/Replicator/Looks/OmniPBR"))
        self.getprims_node.get_attribute("inputs:semanticsExclusion").set([",".join(s) for s in semantics_exclusion])

        await self._controller.evaluate(self._graph)

        gathered_prims = [Sdf.Path(str(p)) for p in self.getprims_node.get_attribute("outputs:prims").get()]
        self.assertEqual(expected_result, set(gathered_prims))
