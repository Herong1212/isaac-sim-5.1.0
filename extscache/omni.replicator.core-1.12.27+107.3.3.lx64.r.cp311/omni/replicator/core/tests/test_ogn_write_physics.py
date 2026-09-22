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
import omni.graph.core as og
import omni.kit
import omni.replicator.core as rep
import omni.usd
from pxr import Gf, PhysxSchema, UsdPhysics, UsdShade


class TestOgnWritePhysics(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        rep.set_global_seed(1234)

        self._stage = omni.usd.get_context().get_stage()
        self._controller = og.Controller()
        self._graph = self._controller.create_graph("/World/PushGraph")

        self._uniform_node = self._controller.create_node(
            ("uniform", self._graph), "omni.replicator.core.OgnSampleUniform"
        )
        self._choice_node = self._controller.create_node(
            ("choice", self._graph), "omni.replicator.core.OgnSampleChoice"
        )
        self._assign_node = self._controller.create_node(
            ("assign", self._graph), "omni.replicator.core.OgnWritePhysics"
        )
        self._assign_node_prim = self._stage.GetPrimAtPath(self._assign_node.get_prim_path())

    async def tearDown(self):
        await omni.usd.get_context().new_stage_async()

    async def test_rigid_body_attributes(self):
        """Test assigning rigid body attributes such as linear and angular velocity."""
        await self._test_attribute(
            attribute_names=["physics:velocity", "physics:angularVelocity"], attribute_sizes=[3, 3]
        )

    async def test_mass_attributes(self):
        """Test assigning mass attributes."""
        attribute_names = [
            "physics:mass",
            "physics:density",
            "physics:centerOfMass",
            "physics:centerOfMass",
            "physics:diagonalInertia",
        ]

        await self._test_attribute(attribute_names=attribute_names, attribute_sizes=[1, 1, 3, 3, 3])

    async def test_drive_attributes(self):
        """Test assigning drive attributes."""
        omni.kit.commands.execute("CreatePrimCommand", prim_path="/sample1", prim_type="Cube")
        omni.kit.commands.execute("CreatePrimCommand", prim_path="/sample2", prim_type="Cube")
        omni.kit.commands.execute("CreatePrimCommand", prim_path="/sample3", prim_type="Cube")
        omni.kit.commands.execute("CreatePrimCommand", prim_path="/sample4", prim_type="Cube")

        prim_paths = ["/sample1/joint", "/sample2/joint", "/sample3/joint", "/sample4/joint"]
        joint_types = ["Revolute", "Revolute", "Prismatic", "Prismatic"]
        for idx, (path, joint_type) in enumerate(zip(prim_paths, joint_types)):
            eval(f"UsdPhysics.{joint_type}Joint.Define(self._stage, '{path}')")
            prim = self._stage.GetPrimAtPath(path)
            if idx % 2 == 0:
                drive_type = UsdPhysics.Tokens.angular if "Revolute" in joint_type else UsdPhysics.Tokens.linear
                UsdPhysics.DriveAPI.Apply(prim, drive_type)

        await self._test_attribute(
            attribute_names=["rep:physics:resolveStiffness", "rep:physics:resolveDamping"],
            attribute_sizes=[1, 1],
            prim_paths=prim_paths,
        )

    @unittest.skip("AddRigidBodyMaterialCommand is no longer available")
    async def test_physics_material_attributes(self):
        """Test assigning physics material attributes."""

        # Test cases:
        # 1) non physics material prim
        # 2) physics material prim
        # 3) prim with no physics material
        # 4) prim with physics material
        # 5) prim with non physics material

        # create materials
        material_paths = ["/mat1", "/mat2", "/mat3", "/mat4"]
        material_prims = list()
        for path in material_paths:
            omni.kit.commands.execute("AddRigidBodyMaterialCommand", stage=self._stage, path=path)
            material_prims.append(self._stage.GetPrimAtPath(path))
        # create 2 non-physics materials
        material_prims[0].RemoveAPI(UsdPhysics.MaterialAPI)
        material_prims[2].RemoveAPI(UsdPhysics.MaterialAPI)
        # create prims
        prim_paths = ["/sample1", "/sample2", "/sample3"]
        prims = list()
        for path in prim_paths:
            omni.kit.commands.execute("CreatePrimCommand", prim_path=path, prim_type="Cube")

        omni.kit.commands.execute(
            "BindMaterialCommand",
            prim_path=prim_paths[1],
            material_path=material_paths[0],
            strength=UsdShade.Tokens.weakerThanDescendants,
        )
        omni.kit.commands.execute(
            "BindMaterialCommand",
            prim_path=prim_paths[2],
            material_path=material_paths[1],
            strength=UsdShade.Tokens.weakerThanDescendants,
        )

        attribute_names = ["physics:dynamicFriction", "physics:staticFriction", "physics:density"]

        await self._test_attribute(
            attribute_names=attribute_names,
            attribute_sizes=[1, 1, 1],
            prim_paths=prim_paths + material_paths[2:],
            attribute_min=0.0,
            attribute_max=1.0,
            check_material=True,
        )

    async def test_physics_collider(self):
        prims = list()
        prim_paths = ["/sample1", "/sample2"]

        for path in prim_paths:
            omni.kit.commands.execute("CreatePrimCommand", prim_path=path, prim_type="Cube")
            prims.append(self._stage.GetPrimAtPath(path))

        # apply collision API to first prim
        collision_api = UsdPhysics.CollisionAPI.Apply(prims[0])
        physx_collision_api = PhysxSchema.PhysxCollisionAPI.Apply(prims[0])
        mesh_collision_api = UsdPhysics.MeshCollisionAPI.Apply(prims[0])
        mesh_collision_api.GetApproximationAttr().Set("convexHull")

        self._choice_node.get_attribute("inputs:seed").set(42)
        self._choice_node.get_attribute("inputs:numSamples").set(len(prims))
        choices_type = og.Type(og.BaseDataType.TOKEN, 1, 1)
        self._choice_node.get_attribute("inputs:choices").set_resolved_type(choices_type)
        self._choice_node.get_attribute("inputs:choices").set(["meshSimplification"])
        self._choice_node.get_attribute("inputs:weights").set([1])

        self._add_relationship_target("inputs:prims", prim_paths)

        self._controller.connect(
            self._choice_node.get_attribute("outputs:samples"), self._assign_node.get_attribute("inputs:values")
        )

        self._assign_node.get_attribute("inputs:attribute").set("physics:approximation")
        await self._controller.evaluate(self._graph)

        prim_1_type = str(prims[0].GetAttribute("physics:approximation").Get())
        prim_2_type = str(prims[1].GetAttribute("physics:approximation").Get())

        self.assertTrue(prim_1_type == "meshSimplification")
        self.assertTrue(prim_2_type == "meshSimplification")

    async def _test_attribute(
        self,
        attribute_names,
        attribute_sizes,
        prim_paths=None,
        attribute_min=100.0,
        attribute_max=1000.0,
        check_material=False,
    ):
        prims = list()
        if prim_paths is None:
            prim_paths = ["/sample1", "/sample2"]

            for path in prim_paths:
                omni.kit.commands.execute("CreatePrimCommand", prim_path=path, prim_type="Cube")

        for path in prim_paths:
            prims.append(self._stage.GetPrimAtPath(path))

        for name, size in zip(attribute_names, attribute_sizes):
            lower = np.array([attribute_min] * size)
            upper = np.array([attribute_max] * size)

            self._uniform_node.get_attribute("inputs:seed").set(42)
            self._uniform_node.get_attribute("inputs:numSamples").set(len(prims))
            self._uniform_node.get_attribute("inputs:lower").set(lower)
            self._uniform_node.get_attribute("inputs:upper").set(upper)

            self._add_relationship_target("inputs:prims", prim_paths)

            self._controller.connect(
                self._uniform_node.get_attribute("outputs:samples"), self._assign_node.get_attribute("inputs:values")
            )
            self._assign_node.get_attribute("inputs:attribute").set(name)
            await self._controller.evaluate(self._graph)
            if "resolve" in name:
                attribute_vals = list()
                for prim in prims:
                    if "prismatic" in prim.GetTypeName().lower():
                        stiffness_name = "drive:linear:physics:stiffness"
                        damping_name = "drive:linear:physics:damping"
                    elif "revolute" in prim.GetTypeName().lower():
                        stiffness_name = "drive:angular:physics:stiffness"
                        damping_name = "drive:angular:physics:damping"
                    if "stiffness" in name.lower():
                        attribute_vals.append(np.array(prim.GetAttribute(stiffness_name).Get()).reshape(-1))
                    else:
                        attribute_vals.append(np.array(prim.GetAttribute(damping_name).Get()).reshape(-1))
            elif check_material:
                attribute_vals = list()
                for prim in prims:
                    if prim.GetTypeName() == "Material":
                        attribute_vals.append(np.array(prim.GetAttribute(name).Get()).reshape(-1))
                    else:
                        material_path = prim.GetRelationship("material:binding").GetTargets()[0]
                        material = self._stage.GetPrimAtPath(material_path)
                        attribute_vals.append(np.array(material.GetAttribute(name).Get()).reshape(-1))
            else:
                attribute_vals = [np.array(prim.GetAttribute(name).Get()).reshape(-1) for prim in prims]
            self.assertTrue(np.all(np.logical_and(attribute_vals >= lower, attribute_vals <= upper)))

    def _add_relationship_target(self, attribute, prim_paths):
        for target in prim_paths:
            omni.kit.commands.execute(
                "AddRelationshipTarget", relationship=self._assign_node_prim.GetAttribute(attribute), target=target
            )
