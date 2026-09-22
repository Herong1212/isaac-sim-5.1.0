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
from pxr import Gf, UsdGeom
from scipy.spatial.transform import Rotation as R


class TestOgnLookAt(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        rep.set_global_seed(1234)

        self._stage = omni.usd.get_context().get_stage()
        self._controller = og.Controller()
        self._graph = self._controller.create_graph("/World/PushGraph")

        self._look_at_node = self._controller.create_node(("look_at", self._graph), "omni.replicator.core.OgnLookAt")
        self._look_at_node_prim = self._stage.GetPrimAtPath(self._look_at_node.get_prim_path())

        # reslove the dtype of up axis.
        self._look_at_node.get_attribute("inputs:upAxis").set_resolved_type(og.Type(og.BaseDataType.FLOAT, 1, 1))

        await omni.kit.app.get_app().next_update_async()

    async def tearDown(self):
        await omni.usd.get_context().new_stage_async()

    async def test_look_at_coord(self):
        """Test look at with a target 3D coordinate"""
        _, cube_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        cube = self._stage.GetPrimAtPath(cube_path)

        self._look_at_node_prim.GetRelationship("inputs:prims").SetTargets([cube_path])

        test1 = (Gf.Vec3f(0, 0, 1), np.array([180.0, 0.0, 180.0]))
        test2 = (Gf.Vec3f(1, 0, 0), np.array([0.0, -90.0, 0.0]))
        test3 = (Gf.Vec3f(0, 1, 0), np.array([90, 0.0, 0.0]))
        test4 = (Gf.Vec3f(1, 1, 0), np.array([45.0, -90.0, 0.0]))

        for target, expected in [test1, test2, test3, test4]:
            self._look_at_node.get_attribute("inputs:target").set(target)
            await self._controller.evaluate(self._graph)
            rotation = self._look_at_node.get_attribute("outputs:values").get_array(False, False, 0).reshape(3)
            # convert intrinsic euler angles to quaternion so that we can compare unique representations
            np.testing.assert_allclose(
                R.from_euler("xyz", expected, degrees=True).as_quat(),
                R.from_euler("xyz", rotation, degrees=True).as_quat(),
                atol=1e-5,
            )

    async def test_look_at_prim(self):
        """Test look at with a target prim"""
        _, cube_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        cube = self._stage.GetPrimAtPath(cube_path)

        _, target_sphere_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Sphere")
        target_sphere = self._stage.GetPrimAtPath(target_sphere_path)

        self._look_at_node_prim.GetRelationship("inputs:prims").SetTargets([cube_path])
        self._look_at_node_prim.GetRelationship("inputs:targetPrim").SetTargets([target_sphere_path])

        test1 = (Gf.Vec3f(0, 0, 1), np.array([180.0, 0.0, 180.0]))
        test2 = (Gf.Vec3f(1, 0, 0), np.array([0.0, -90.0, 0.0]))
        test3 = (Gf.Vec3f(0, 1, 0), np.array([90.0, 0.0, 0.0]))
        test4 = (Gf.Vec3f(1, 1, 0), np.array([45.0, -90.0, 0.0]))

        for target, expected in [test1, test2, test3, test4]:
            target_sphere.GetAttribute("xformOp:translate").Set(target)
            await self._controller.evaluate(self._graph)
            rotation = self._look_at_node.get_attribute("outputs:values").get_array(False, False, 0).reshape(3)
            # convert intrinsic euler angles to quaternion so that we can compare unique representations
            np.testing.assert_allclose(
                R.from_euler("xyz", expected, degrees=True).as_quat(),
                R.from_euler("xyz", rotation, degrees=True).as_quat(),
                atol=1e-5,
            )

    async def test_parent_translation(self):
        """Test look at with prim whose parent has a translation applied"""
        parent_path = "/parent"
        omni.kit.commands.execute("CreatePrimCommand", prim_type="Xform", prim_path=parent_path)
        parent = self._stage.GetPrimAtPath(parent_path)
        if "xformOp:translate" not in parent.GetPropertyNames():
            UsdGeom.Xformable(parent).AddTranslateOp()
        parent.GetAttribute("xformOp:translate").Set((1000, 2000, 3000))
        _, cube_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        omni.kit.commands.create(
            "MovePrim", path_from=cube_path, path_to=f"{parent_path}/Cube_Xform"
        ).do()  # executing command without undo to avoid bug https://jirasw.nvidia.com/browse/OMPE-14264
        cube = parent.GetAllChildren()[0]
        self._look_at_node_prim.GetRelationship("inputs:prims").SetTargets([cube.GetPath()])
        cube.GetAttribute("xformOp:translate").Set((0, 0, 0))

        test1 = (Gf.Vec3f(1000, 2000, 3001), np.array([180.0, 0.0, 180.0]))
        test2 = (Gf.Vec3f(1001, 2000, 3000), np.array([0.0, -90.0, 0.0]))
        test3 = (Gf.Vec3f(1000, 2001, 3000), np.array([90, 0.0, 0.0]))
        test4 = (Gf.Vec3f(1001, 2001, 3000), np.array([45.0, -90.0, 0.0]))

        for target, expected in [test1, test2, test3, test4]:
            self._look_at_node.get_attribute("inputs:target").set(target)
            await self._controller.evaluate(self._graph)
            rotation = self._look_at_node.get_attribute("outputs:values").get_array(False, False, 0).reshape(3)
            # convert intrinsic euler angles to quaternion so that we can compare unique representations
            np.testing.assert_allclose(
                R.from_euler("xyz", expected, degrees=True).as_quat(),
                R.from_euler("xyz", rotation, degrees=True).as_quat(),
                atol=1e-5,
            )

    async def test_parent_rotation(self):
        """Test look at with prim whose parent has a rotation applied
        Parent's rotation should not affect children's rotation.
        """
        parent_path = "/parent"
        omni.kit.commands.execute("CreatePrimCommand", prim_type="Xform", prim_path=parent_path)
        parent = self._stage.GetPrimAtPath(parent_path)
        if "xformOp:rotateXYZ" not in parent.GetPropertyNames():
            UsdGeom.Xformable(parent).AddRotateXYZOp()
        parent.GetAttribute("xformOp:rotateXYZ").Set((30, 60, 90))
        _, cube_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        omni.kit.commands.create(
            "MovePrim", path_from=cube_path, path_to=f"{parent_path}/Cube_Xform"
        ).do()  # executing command without undo to avoid bug https://jirasw.nvidia.com/browse/OMPE-14264
        cube = parent.GetAllChildren()[0]
        self._look_at_node_prim.GetRelationship("inputs:prims").SetTargets([cube.GetPath()])
        cube.GetAttribute("xformOp:rotateXYZ").Set((0, 0, 0))

        test1 = (Gf.Vec3f(0, 0, 1), np.array([180.0, 0.0, 180.0]))
        # test2 = (Gf.Vec3f(1, 0, 0), np.array([0.0, 270.0, 0.0]))  TODO: Needs investigation where when computing quaternion, linux and windows results differ.
        test2 = (Gf.Vec3f(1, 0, 1), np.array([0.0, 225.0, 0.0]))
        test3 = (Gf.Vec3f(0, 1, 0), np.array([90, 0.0, 0.0]))
        test4 = (Gf.Vec3f(1, 1, 0), np.array([45.0, -90.0, 0.0]))

        # Set up a writer node to write the attribute to the prim.
        writer_node = self._controller.create_node(
            ("write_attribute", self._graph), "omni.replicator.core.OgnWritePrimAttribute"
        )
        writer_node_prim = self._stage.GetPrimAtPath(writer_node.get_prim_path())
        writer_node_prim.GetRelationship("inputs:prims").SetTargets([cube.GetPath()])
        og.AttributeValueHelper(writer_node.get_attribute("inputs:attribute")).set("xformOp:rotateXYZ", update_usd=True)
        og.AttributeValueHelper(writer_node.get_attribute("inputs:attributeType")).set("double3", update_usd=True)

        for target, expected in [test1, test2, test3, test4]:
            self._look_at_node.get_attribute("inputs:target").set(target)

            self._look_at_node.get_attribute("outputs:values").connect(writer_node.get_attribute("inputs:values"), True)

            await self._controller.evaluate(self._graph)
            timeline_iface = omni.timeline.get_timeline_interface()
            time = timeline_iface.get_current_time() * timeline_iface.get_time_codes_per_seconds()
            xform = UsdGeom.Xformable(cube)

            # get global rotation
            rot = xform.ComputeLocalToWorldTransform(time).ExtractRotation().GetQuaternion()
            rotation = np.array([*np.array(rot.GetImaginary()), np.array(rot.GetReal())])

            np.testing.assert_allclose(R.from_euler("xyz", expected, degrees=True).as_quat(), rotation, atol=0.0001)

    async def test_z_up_axis(self):
        # set up Z up axis
        """Test look at with Z-Up"""
        UsdGeom.SetStageUpAxis(self._stage, "Z")
        _, cone_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cone")
        cone = self._stage.GetPrimAtPath(cone_path)

        self._look_at_node_prim.GetRelationship("inputs:prims").SetTargets([cone_path])
        test1 = (Gf.Vec3f(0, 0, 1), np.array([180, 0.0, 90]))
        test2 = (Gf.Vec3f(1, 0, 0), np.array([90.0, 0.0, -90.0]))
        test3 = (Gf.Vec3f(0, 1, 0), np.array([90, 0.0, 0.0]))
        test4 = (Gf.Vec3f(1, 1, 0), np.array([90.0, 0.0, -45.0]))

        for target, expected in [test1, test2, test3, test4]:
            self._look_at_node.get_attribute("inputs:target").set(target)
            await self._controller.evaluate(self._graph)
            rotation = self._look_at_node.get_attribute("outputs:values").get_array(False, False, 0).reshape(3)
            rep.functional.create.sphere(target * 50, scale=0.1)
            # convert intrinsic euler angles to quaternion so that we can compare unique representations
            np.testing.assert_allclose(
                R.from_euler("xyz", expected, degrees=True).as_quat(),
                R.from_euler("xyz", rotation, degrees=True).as_quat(),
                atol=1e-5,
            )

    async def test_up_axis(self):
        """Test user-define up axis for look at"""
        _, cube_path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        cube = self._stage.GetPrimAtPath(cube_path)

        cube.GetAttribute("xformOp:translate").Set((0, 0, 500))
        self._look_at_node_prim.GetRelationship("inputs:prims").SetTargets([cube_path])

        test1 = ((1, 0, 0), np.array([0.0, 0.0, -90.0]))
        test2 = ((0, 1, 0), np.array([0.0, 0, 0.0]))
        test3 = ((0, 0, 1), np.array([0.0, 0.0, 0.0]))
        test4 = ((-1, -1, -1), np.array([0.0, 0.0, 135.0]))
        test5 = ((1, 0, 1), np.array([0.0, 0.0, -90.0]))
        test6 = ((1, 1, 1), np.array([0.0, 0.0, -45.0]))

        for up_axis, expected in [test1, test2, test3, test4, test5, test6]:
            self._look_at_node.get_attribute("inputs:target").set(Gf.Vec3f(0, 0, 0))
            self._look_at_node.get_attribute("inputs:upAxis").set(up_axis)

            await self._controller.evaluate(self._graph)

            rotation = self._look_at_node.get_attribute("outputs:values").get_array(False, False, 0).reshape(3)
            # convert intrinsic euler angles to quaternion so that we can compare unique representations
            np.testing.assert_allclose(
                R.from_euler("xyz", expected, degrees=True).as_quat(),
                R.from_euler("xyz", rotation, degrees=True).as_quat(),
                atol=1e-16,
            )

    async def test_timeseries(self):
        """Test look at with prim that has timeseries transforms applied"""
        prim = self._stage.DefinePrim("/prim", "Cube")
        target = self._stage.DefinePrim("/target", "Sphere")
        self._look_at_node_prim.GetRelationship("inputs:prims").SetTargets([str(prim.GetPath())])
        self._look_at_node_prim.GetRelationship("inputs:targetPrim").SetTargets([target.GetPath()])

        UsdGeom.Xformable(prim).AddTranslateOp()
        UsdGeom.Xformable(prim).AddRotateXYZOp()
        UsdGeom.Xformable(target).AddTranslateOp()

        timeline_iface = omni.timeline.get_timeline_interface()
        time_codes_per_sec = timeline_iface.get_time_codes_per_seconds()
        timeline_iface.set_end_time(1000.0)

        # Set timeseries translations on target
        for i, coord in enumerate([(0, 0, 1), (1, 0, 0), (0, 1, 0), (1, 1, 0)]):
            target.GetAttribute("xformOp:translate").Set(coord, time=(i / time_codes_per_sec))

        for i, gt in enumerate([(180.0, 0.0, 180.0), (0.0, -90.0, 0.0), (90, 0.0, 0.0), (45.0, -90.0, 0.0)]):
            timeline_iface.set_current_time(i / time_codes_per_sec)
            await omni.kit.app.get_app().next_update_async()
            rotation = self._look_at_node.get_attribute("outputs:values").get_array(False, False, 0).reshape(3)
            np.testing.assert_allclose(
                R.from_euler("xyz", rotation, degrees=True).as_quat(),
                R.from_euler("xyz", np.array(gt), degrees=True).as_quat(),
                atol=1e-5,
            )

        # Add timeseries translations on prim
        for i, coord in enumerate([(0, 0, -1), (-1, 0, 0), (0, -1, 0), (-1, -1, 0)]):
            prim.GetAttribute("xformOp:translate").Set(coord, time=(i / time_codes_per_sec))

        for i, gt in enumerate([(180.0, 0.0, 180.0), (0.0, -90.0, 0.0), (90, 0.0, 0.0), (0.0, -90.0, 45.0)]):
            timeline_iface.set_current_time(i / time_codes_per_sec)
            await omni.kit.app.get_app().next_update_async()
            rotation = self._look_at_node.get_attribute("outputs:values").get_array(False, False, 0).reshape(3)
            np.testing.assert_allclose(
                R.from_euler("xyz", rotation, degrees=True).as_quat(),
                R.from_euler("xyz", np.array(gt), degrees=True).as_quat(),
                atol=1e-5,
            )

    async def test_look_at_api(self):
        cube = rep.create.cube(position=(500, 0, 0))
        camera = rep.create.camera(look_at=cube)
        await omni.kit.app.get_app().next_update_async()
        rep.orchestrator.preview()

        camera_prim = camera.get_output_prims()["prims"][0]
        camera_rot = UsdGeom.Xformable(camera_prim).ComputeLocalToWorldTransform(0).ExtractRotation()

        camera_rot = np.array(camera_rot.Decompose(Gf.Vec3d.ZAxis(), Gf.Vec3d.YAxis(), Gf.Vec3d.XAxis()))
        np.testing.assert_allclose(camera_rot, np.array((0, -90, 0)))

    async def test_look_at_api_sequence(self):
        camera = rep.create.camera()
        render_product = rep.create.render_product(camera, (1024, 1024))
        bbox = rep.AnnotatorRegistry.get_annotator("bounding_box_2d_tight")
        bbox.attach(render_product)
        bounds = rep.create.sphere(visible=False, scale=20)
        usd_files = rep.example.ASSETS

        with rep.trigger.on_frame(max_execs=10):
            with rep.randomizer.instantiate(rep.distribution.sequence(usd_files), size=1):
                rep.modify.semantics([("class", "semantic")])
            with camera:
                rep.randomizer.scatter_2d(surface_prims=bounds)
                rep.modify.pose(look_at=(0, 0, 0))

        for _ in range(10):
            await rep.orchestrator.step_async()
            self.assertGreater(len(bbox.get_data()["data"]), 0)
