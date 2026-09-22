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

import doctest
import os
import shutil
import unittest
from pathlib import Path

import carb
import numpy as np
import omni.kit
import omni.replicator.core as rep
import omni.replicator.core.functional as F
import pxr
import usdrt
from omni.replicator.core import utils
from omni.replicator.core.distribution import choice
from pxr import Gf, Usd, UsdGeom, UsdSemantics, UsdShade

manager = omni.kit.app.get_app().get_extension_manager()
ext_id = manager.get_enabled_extension_id("omni.replicator.core")
ext_path = manager.get_extension_path(ext_id)
MDL_FOLDER = Path(ext_path).joinpath("mdl").as_posix()
TEST_DATA_DIR = Path(os.path.dirname(os.path.realpath(__file__))).joinpath("data")


def get_prim_at_path(path: str):
    stage = omni.usd.get_context().get_stage()
    return stage.GetPrimAtPath(str(path))


def get_rot(replicator_item):
    if F.utils.get_is_fsd_enabled():
        mod = usdrt
        usdrt_stage = usdrt.Usd.Stage.Attach(omni.usd.get_context().get_stage_id())
        stage_id = usdrt_stage.GetStageIdAsStageId()
        fabric_id = usdrt_stage.GetFabricId()
        hier = usdrt.hierarchy.IFabricHierarchy().get_fabric_hierarchy(fabric_id, stage_id)
        print(usdrt_stage.GetPrimAtPath(replicator_item.get_output("prims")[0]).GetChildren())
        prim = usdrt_stage.GetPrimAtPath(replicator_item.get_output("prims")[0]).GetChildren()[0]
        camera_xform = hier.get_world_xform(prim.GetPath())
        rot = camera_xform.ExtractRotation()
    else:
        mod = pxr
        camera_prim = replicator_item.get_output_prims()["prims"][0].GetChildren()[0]
        rot = UsdGeom.Xformable(camera_prim).ComputeLocalToWorldTransform(0).ExtractRotation()
    rotation_decomp = np.array(rot.Decompose(mod.Gf.Vec3d.ZAxis(), mod.Gf.Vec3d.YAxis(), mod.Gf.Vec3d.XAxis()))
    return (rotation_decomp[2], rotation_decomp[1], rotation_decomp[0])


class TestOgnModify(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        rep.set_global_seed(1234)

    async def tearDown(self):
        temp_dir = carb.tokens.get_tokens_interface().resolve("${temp}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        await omni.usd.get_context().new_stage_async()

    def test_docstrings(self):
        """Test module docstring examples"""
        failures, test_counts = doctest.testmod(rep.modify)
        if failures:
            self.fail(f"Encountered {failures} failures in {test_counts} tests.")

    async def test_modify_pose(self):
        position = rep.distribution.uniform((0, 50, 100), (0, 50, 100))
        rotation = rep.distribution.sequence([(0, 45, 90)])
        scale = rep.distribution.uniform((1, 2, 3), (1, 2, 3))

        cube = rep.create.cube(count=2)
        with cube:
            rep.modify.pose(position=position, rotation=rotation, scale=scale)

        await omni.kit.app.get_app().next_update_async()

        cube_prim = cube.get_output_prims()["prims"][0]
        cube_position = np.array(cube_prim.GetAttribute("xformOp:translate").Get())

        np.testing.assert_allclose(cube_position, np.array([0, 50, 100]))

        cube_rotation = np.array(cube_prim.GetAttribute("xformOp:rotateXYZ").Get())
        np.testing.assert_allclose(cube_rotation, np.array([0, 45, 90]), atol=1e-14)

        cube_scale = np.array(cube_prim.GetAttribute("xformOp:scale").Get())
        np.testing.assert_allclose(cube_scale, np.array([1, 2, 3]))

    async def test_modify_pose_axes_position(self):
        x_positions = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
        position_x = rep.distribution.sequence(x_positions)
        position_y = None
        position_z = rep.distribution.uniform(-50, 50, seed=10)

        cube = rep.create.cube(position=(0, 100, 0), count=10)
        with cube:
            rep.modify.pose(position_x=position_x, position_y=position_y, position_z=position_z)

        await omni.kit.app.get_app().next_update_async()

        cube_prim_paths = cube.get_output("prims")

        for i in range(10):
            cube_prim = get_prim_at_path(cube_prim_paths[i])
            cube_position = np.array(cube_prim.GetAttribute("xformOp:translate").Get())
            self.assertAlmostEqual(cube_position[0], x_positions[0])
            self.assertEqual(cube_position[1], 100)
            self.assertLess(cube_position[2], 50)
            self.assertGreater(cube_position[2], -50)

    async def test_modify_pose_axes_rotation(self):
        x_rotations = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
        rotation_x = rep.distribution.sequence(x_rotations)
        rotation_y = None
        rotation_z = rep.distribution.uniform(-90, 90, seed=10)

        cube = rep.create.cube(rotation=(0, 77, 0), count=10)
        with cube:
            rep.modify.pose(rotation_x=rotation_x, rotation_y=rotation_y, rotation_z=rotation_z)

        await omni.kit.app.get_app().next_update_async()

        cube_prim_paths = cube.get_output("prims")

        for i in range(10):
            cube_prim = get_prim_at_path(cube_prim_paths[i])
            cube_rotation = np.array(cube_prim.GetAttribute("xformOp:rotateXYZ").Get())
            self.assertAlmostEqual(cube_rotation[0], x_rotations[0])
            self.assertEqual(cube_rotation[1], 77)
            self.assertLess(cube_rotation[2], 90)
            self.assertGreater(cube_rotation[2], -90)

    async def test_modify_pose_single_axis(self):
        cube = rep.create.cube(position=(0, 100, 0), count=10)
        with cube:
            rep.modify.pose(position_y=rep.distribution.uniform(-300, 300))

        await omni.kit.app.get_app().next_update_async()

        cube_prim_paths = cube.get_output("prims")

        prev_cube_pos_y = None
        for i in range(10):
            cube_prim = get_prim_at_path(cube_prim_paths[i])
            cube_position = np.array(cube_prim.GetAttribute("xformOp:translate").Get())
            self.assertEqual(cube_position[0], 0)
            self.assertEqual(cube_position[2], 0)

            if prev_cube_pos_y:
                self.assertNotEqual(cube_position[1], prev_cube_pos_y)

            prev_cube_pos_y = cube_position[1]

    async def test_modify_pose_input_prims(self):
        position = rep.distribution.uniform((0, 50, 100), (0, 50, 100))
        rotation = rep.distribution.uniform((0, 45, 90), (0, 45, 90))
        scale = rep.distribution.uniform((1, 2, 3), (1, 2, 3))

        cube = rep.create.cube()
        rep.modify.pose(position=position, rotation=rotation, scale=scale, input_prims=cube)

        await omni.kit.app.get_app().next_update_async()

        cube_prim = cube.get_output_prims()["prims"][0]
        cube_position = np.array(cube_prim.GetAttribute("xformOp:translate").Get())

        np.testing.assert_allclose(cube_position, np.array([0, 50, 100]))

        cube_rotation = np.array(cube_prim.GetAttribute("xformOp:rotateXYZ").Get())
        np.testing.assert_allclose(cube_rotation, np.array([0, 45, 90]), atol=1e-14)

        cube_scale = np.array(cube_prim.GetAttribute("xformOp:scale").Get())
        np.testing.assert_allclose(cube_scale, np.array([1, 2, 3]))

    async def test_size_to_scale(self):
        """Test converting the size to scale functionality."""
        cube = rep.create.cube()
        torus = rep.create.torus()

        with cube:
            rep.modify.pose(size=(1000, 500, 200))

        with torus:
            rep.modify.pose(size=300)

        await omni.kit.app.get_app().next_update_async()

        cube_prim = cube.get_output_prims()["prims"][0]
        cube_scale = np.array(cube_prim.GetAttribute("xformOp:scale").Get())
        np.testing.assert_allclose(cube_scale, np.array([2.0, 2.0, 2.0]), atol=1e-6)

        torus_prim = torus.get_output_prims()["prims"][0]
        torus_scale = np.array(torus_prim.GetAttribute("xformOp:scale").Get())
        np.testing.assert_allclose(torus_scale, np.array([2.0, 2.0, 2.0]), atol=1e-6)

    async def test_size_to_scale_replicator_item(self):
        """Test converting the size to scale functionality."""

        cube = rep.create.cube()
        torus = rep.create.torus()

        with cube:
            rep.modify.pose(size=rep.distribution.uniform((1, 1, 1), (1000, 1000, 1000), seed=10))

        with torus:
            rep.modify.pose(size=rep.distribution.uniform(10, 200, seed=10))

        await omni.kit.app.get_app().next_update_async()

        cube_prim = cube.get_output_prims()["prims"][0]
        cube_scale = np.array(cube_prim.GetAttribute("xformOp:scale").Get())
        np.testing.assert_allclose(cube_scale, np.array([2.084741, 2.084741, 2.084741]), atol=1e-6)

        torus_prim = torus.get_output_prims()["prims"][0]
        torus_scale = np.array(torus_prim.GetAttribute("xformOp:scale").Get())
        np.testing.assert_allclose(torus_scale, np.array([1.277602, 1.277602, 1.277602]), atol=1e-6)

    async def test_size_to_scale_replicator_item_input_prims(self):
        """Test converting the size to scale functionality."""

        cube = rep.create.cube()
        torus = rep.create.torus()

        rep.modify.pose(size=rep.distribution.uniform((1, 1, 1), (1000, 1000, 1000), seed=10), input_prims=cube)
        rep.modify.pose(size=rep.distribution.uniform(10, 200, seed=10), input_prims=torus)

        await omni.kit.app.get_app().next_update_async()

        cube_prim = cube.get_output_prims()["prims"][0]
        cube_scale = np.array(cube_prim.GetAttribute("xformOp:scale").Get())
        np.testing.assert_allclose(cube_scale, np.array([2.084741, 2.084741, 2.084741]), atol=1e-6)

        torus_prim = torus.get_output_prims()["prims"][0]
        torus_scale = np.array(torus_prim.GetAttribute("xformOp:scale").Get())
        np.testing.assert_allclose(torus_scale, np.array([1.277602, 1.277602, 1.277602]), atol=1e-6)

    async def test_modify_pivot(self):
        """Test modifying the prim's pivot point."""
        cubes = rep.create.cube(semantics=[("class", "cube")], count=1)

        with cubes:
            rep.modify.pose(scale=(10, 10, 10), pivot=(0, 0, -1))  # Centre of the x-y plane

        await omni.kit.app.get_app().next_update_async()

        cube_xform_prim_paths = cubes.get_output("prims")

        for cube_xform_prim_path in cube_xform_prim_paths:
            cube_xform_prim = get_prim_at_path(cube_xform_prim_path)
            cube_prim = cube_xform_prim.GetChild("Cube")

            cube_pivot = np.array(cube_xform_prim.GetAttribute("xformOp:translate").Get())

            np.testing.assert_allclose(cube_pivot, np.array([0, 0, 0]))

            # The actual prim is being offset to the opposite of pivot position.
            cube_translation = np.array(cube_prim.GetAttribute("xformOp:translate").Get())

            np.testing.assert_allclose(cube_translation, np.array([0, 0, 50]))

            await omni.kit.app.get_app().next_update_async()

            cache = UsdGeom.BBoxCache(
                time=Usd.TimeCode.Default(), includedPurposes=[UsdGeom.Tokens.default_], useExtentsHint=True
            )
            bound = utils.compute_aabb(cache, cube_prim)

            # Rotation is around the pivot point.
            np.testing.assert_allclose(bound, np.array([-500, -500, 0, 500, 500, 1000]))

    async def test_modify_pivot_input_prims(self):
        """Test modifying the prim's pivot point."""
        cubes = rep.create.cube(semantics=[("class", "cube")], count=1)

        rep.modify.pose(scale=(10, 10, 10), pivot=(0, 0, -1), input_prims=cubes)  # Centre of the x-y plane

        await omni.kit.app.get_app().next_update_async()

        cube_xform_prim_paths = cubes.get_output("prims")

        for cube_xform_prim_path in cube_xform_prim_paths:
            cube_xform_prim = get_prim_at_path(cube_xform_prim_path)
            cube_prim = cube_xform_prim.GetChild("Cube")

            cube_pivot = np.array(cube_xform_prim.GetAttribute("xformOp:translate").Get())

            np.testing.assert_allclose(cube_pivot, np.array([0, 0, 0]))

            # The actual prim is being offset to the opposite of pivot position.
            cube_translation = np.array(cube_prim.GetAttribute("xformOp:translate").Get())

            np.testing.assert_allclose(cube_translation, np.array([0, 0, 50]))

            await omni.kit.app.get_app().next_update_async()

            cache = UsdGeom.BBoxCache(
                time=Usd.TimeCode.Default(), includedPurposes=[UsdGeom.Tokens.default_], useExtentsHint=True
            )
            bound = utils.compute_aabb(cache, cube_prim)

            # Rotation is around the pivot point.
            np.testing.assert_allclose(bound, np.array([-500, -500, 0, 500, 500, 1000]))

    async def test_modify_pivot_frame_trigger(self):
        """Test modifying the prim's pivot point under a on_frame trigger."""
        cubes = rep.create.cube(semantics=[("class", "cube")], count=1)

        with rep.trigger.on_frame(max_execs=10):
            with cubes:
                rep.modify.pose(scale=(10, 10, 10), pivot=(0, 0, -1))  # Centre of the x-y plane

        await omni.kit.app.get_app().next_update_async()

        for i in range(10):
            await rep.orchestrator.step_async()

            cube_xform_prim_paths = cubes.get_output("prims")

            for cube_xform_prim_path in cube_xform_prim_paths:
                cube_xform_prim = get_prim_at_path(cube_xform_prim_path)
                cube_prim = cube_xform_prim.GetChild("Cube")

                cube_pivot = np.array(cube_xform_prim.GetAttribute("xformOp:translate").Get())

                np.testing.assert_allclose(cube_pivot, np.array([0, 0, 0]))

                # The actual prim is being offset to the opposite of pivot position.
                cube_translation = np.array(cube_prim.GetAttribute("xformOp:translate").Get())

                np.testing.assert_allclose(cube_translation, np.array([0, 0, 50]))

    async def test_modify_pivot_non_centre(self):
        """Test modifying the prim's pivot for a non-centred prim."""
        rocket_prim_path = os.path.join(TEST_DATA_DIR, "objects", "rocket.usd")

        rocket = rep.randomizer.instantiate([rocket_prim_path], size=1)

        with rocket:
            rep.modify.pose(pivot=(0, 0, -1))  # Centre of the x-y plane

        await omni.kit.app.get_app().next_update_async()

        await rep.orchestrator.step_async()

        rocket_xform_prim = get_prim_at_path("/Replicator/SampledAssets").GetChildren()[0].GetChildren()[0]

        rocket_prim = rocket_xform_prim.GetChildren()[0]

        # The actual prim is being offset to the opposite of pivot position.
        rocket_translation = np.array(rocket_prim.GetAttribute("xformOp:translate").Get())

        np.testing.assert_allclose(rocket_translation, np.array([0.0062705, -0.46456649, 0.28908101]), atol=1e-3)

    async def _run_until_stopped(self):
        await rep.orchestrator.run_until_complete_async()

    async def test_camera_relative(self):
        """Test modify object location in camera space."""

        # TODO jiehanw: Expand tests:
        # - Add fisheye
        # - Check prims are distributed
        out_dir = carb.tokens.get_tokens_interface().resolve("${temp}/test_cam_rel")

        camera = rep.create.camera()
        render_product = rep.create.render_product(camera, (1024, 512))
        writer = rep.WriterRegistry.get("BasicWriter")
        writer.initialize(output_dir=out_dir, bounding_box_2d_loose=True, frame_padding=0)
        writer.attach(render_product)

        # FIXME The get_data path crashes on Windows TC
        # bbox = rep.AnnotatorRegistry.get_annotator("bounding_box_2d_loose")
        # bbox.attach(render_product)

        spheres = rep.create.sphere(semantics=[("class", "sphere")], count=10)
        cubes = rep.create.cube(semantics=[("class", "cube")], count=10)

        with rep.trigger.on_frame(max_execs=1):
            with camera:
                rep.modify.pose(
                    position=rep.distribution.uniform((-1000, -1000, -1000), (1000, 1000, 1000)),
                    look_at=rep.distribution.uniform((-1000, -1000, -1000), (1000, 1000, 1000)),
                )
            with spheres:
                rep.modify.pose_camera_relative(
                    camera,
                    render_product,
                    rep.distribution.uniform(900, 1200, seed=123),
                    rep.distribution.uniform(-1, 1),
                    0,
                )
            with cubes:
                rep.modify.pose_camera_relative(
                    camera,
                    render_product,
                    rep.distribution.uniform(1200, 1400, seed=123),
                    0,
                    rep.distribution.uniform(-1, 1),
                )

        await rep.orchestrator.run_until_complete_async()

        camera_prim = camera.get_output_prims()["prims"][0].GetChildren()[0]
        camera_tf = UsdGeom.Xformable(camera_prim).ComputeLocalToWorldTransform(0).GetInverse()

        npy_file_name = "bounding_box_2d_loose_0.npy"
        bbox_data = np.load(os.path.join(out_dir, npy_file_name))

        # FIXME The get_data path crashes on Windows TC
        # bbox_data = bbox.get_data()["data"]

        # SPHERES
        sphere_prims = spheres.get_output_prims()["prims"]
        sphere_positions = np.array([s.GetAttribute("xformOp:translate").Get() for s in sphere_prims])
        sphere_positions_cam = np.pad(sphere_positions, ((0, 0), (0, 1)), constant_values=1) @ camera_tf
        sphere_distances = np.linalg.norm(sphere_positions_cam[:3], axis=1)

        # Test Distance
        np.testing.assert_array_less(900, sphere_distances)
        np.testing.assert_array_less(sphere_distances, 1200)

        # Test vertical close to zero
        np.testing.assert_allclose(sphere_positions_cam[:, 1], np.zeros_like(sphere_positions_cam[:, 1]), atol=1e-10)

        # Test all prims in field of view
        self.assertEqual(len(bbox_data[bbox_data["semanticId"] == 0]), 10)

        # CUBES
        cube_prims = cubes.get_output_prims()["prims"]
        cube_positions = np.array([s.GetAttribute("xformOp:translate").Get() for s in cube_prims])
        cube_positions_cam = np.pad(cube_positions, ((0, 0), (0, 1)), constant_values=1) @ camera_tf
        cube_distances = np.linalg.norm(cube_positions_cam[:3], axis=1)

        # Test Distance
        np.testing.assert_array_less(1200, cube_distances)
        np.testing.assert_array_less(cube_distances, 1400)

        # Test vertical close to zero
        np.testing.assert_allclose(cube_positions_cam[:, 0], np.zeros_like(cube_positions_cam[:, 0]), atol=1e-10)

        # Test all prims in field of view
        # FIXME test fails only on TC
        # self.assertEqual(len(bbox_data[bbox_data["semanticId"] == 1]), 10)

    async def test_modify_visibility(self):
        """Test modifying the visibility of the prim."""

        cubes = rep.create.cube(semantics=[("class", "cube")], count=10)

        with cubes:
            rep.modify.visibility(choice([True, False], seed=10))

        await omni.kit.app.get_app().next_update_async()

        cube_xform_prim_paths = cubes.get_output("prims")

        expected_visibility = [
            "invisible",
            "invisible",
            "inherited",
            "inherited",
            "invisible",
            "invisible",
            "invisible",
            "inherited",
            "invisible",
            "invisible",
        ]
        cube_visibility = [
            mesh.GetAttribute("visibility").Get() for mesh in utils.find_prims(cube_xform_prim_paths, "prims")
        ]

        assert expected_visibility == cube_visibility

    async def test_modify_visibility_group_single_value(self):
        sphere = rep.create.sphere(position=(100, 0, 100))
        cylinder = rep.create.cylinder(position=(-100, 0, -100))
        group = rep.create.group([cylinder, sphere])
        with group:
            rep.modify.visibility(False)

        await omni.kit.app.get_app().next_update_async()
        for prim in group.get_output_prims()["prims"]:
            self.assertEqual(prim.GetAttribute("visibility").Get(), "invisible")

        with group:
            rep.modify.visibility([True])

        await omni.kit.app.get_app().next_update_async()
        for prim in group.get_output_prims()["prims"]:
            self.assertEqual(prim.GetAttribute("visibility").Get(), "inherited")

        await omni.kit.app.get_app().next_update_async()
        with rep.trigger.on_frame(max_execs=2):
            with group:
                rep.modify.visibility(rep.distribution.sequence([True, False]))

        await rep.orchestrator.step_async()
        for prim in group.get_output_prims()["prims"]:
            self.assertEqual(prim.GetAttribute("visibility").Get(), "inherited")

        await rep.orchestrator.step_async()
        for prim in group.get_output_prims()["prims"]:
            self.assertEqual(prim.GetAttribute("visibility").Get(), "invisible")

    async def test_modify_visibility_input_prims(self):
        """Test modifying the visibility of the prim."""

        cubes = rep.create.cube(semantics=[("class", "cube")], count=10)

        rep.modify.visibility(choice([True, False], seed=10), input_prims=cubes)

        await omni.kit.app.get_app().next_update_async()

        cube_xform_prim_paths = cubes.get_output("prims")

        expected_visibility = [
            "invisible",
            "invisible",
            "inherited",
            "inherited",
            "invisible",
            "invisible",
            "invisible",
            "inherited",
            "invisible",
            "invisible",
        ]
        cube_visibility = [
            mesh.GetAttribute("visibility").Get() for mesh in utils.find_prims(cube_xform_prim_paths, "prims")
        ]

        assert expected_visibility == cube_visibility

    async def test_modify_visibility_list_value(self):
        """Test modifying the visibility of the prim, which the input is a list of values."""

        cubes = rep.create.cube(semantics=[("class", "cube")], count=10)

        with cubes:
            rep.modify.visibility([False, False, True, True, False, False, False, True, False, False])

        await omni.kit.app.get_app().next_update_async()

        cube_xform_prim_paths = cubes.get_output("prims")

        expected_visibility = [
            "invisible",
            "invisible",
            "inherited",
            "inherited",
            "invisible",
            "invisible",
            "invisible",
            "inherited",
            "invisible",
            "invisible",
        ]
        cube_visibility = [
            mesh.GetAttribute("visibility").Get() for mesh in utils.find_prims(cube_xform_prim_paths, "prims")
        ]

        assert expected_visibility == cube_visibility

    async def test_modify_look_at(self):
        # Create a shape to look_at.
        cube = rep.create.cone(semantics=[("class", "cube")], position=(0, 0, 0))

        camera = rep.create.camera(position=(0, 0, 500))
        with camera:
            rep.modify.pose(look_at=cube, look_at_up_axis="X")

        await omni.kit.app.get_app().next_update_async()

        camera_rotation = get_rot(camera)

        np.testing.assert_allclose(camera_rotation, np.array((0, 0, -90)))

    async def test_modify_look_at_input_prims(self):
        # Create a shape to look_at.
        cube = rep.create.cone(semantics=[("class", "cube")], position=(0, 0, 0))

        camera = rep.create.camera(position=(0, 0, 500))
        rep.modify.pose(look_at=cube, look_at_up_axis="X", input_prims=camera)

        await omni.kit.app.get_app().next_update_async()

        camera_rotation = get_rot(camera)

        np.testing.assert_allclose(camera_rotation, np.array((0, 0, -90)))

    async def test_modify_look_at_replicator_item_prim(self):
        """Test that the up axis is a replicator item."""
        # Create a shape to look_at.
        cube = rep.create.cone(semantics=[("class", "cube")], position=(0, 0, 0))
        camera = rep.create.camera(position=(0, 0, 500))

        with camera:
            rep.modify.pose(look_at=cube, look_at_up_axis=rep.distribution.uniform((0, 0, 0), (100, 100, 100), seed=10))

        await omni.kit.app.get_app().next_update_async()

        camera_rotation = get_rot(camera)

        np.testing.assert_allclose(camera_rotation, np.array((0, 0, -77.74351)))

    async def test_modify_look_at_replicator_item_coords(self):
        """Test that the up axis is a replicator item."""
        camera = rep.create.camera(position=(0, 0, 500))
        coords = [(500, 0, 0), (2, 2, 2)]

        with camera:
            rep.modify.pose(
                look_at=rep.distribution.sequence(coords),
            )

        await omni.kit.app.get_app().next_update_async()

        camera_rotation = get_rot(camera)

        np.testing.assert_allclose(camera_rotation, np.array((0.0, -45.0, 0.0)))

    async def test_modify_look_at_replicator_item_targets(self):
        """Test that the up axis is a replicator item."""
        camera = rep.create.camera(position=(0, 0, 500))
        cone = rep.create.cone(semantics=[("class", "cone")], position=(500, 0, 0))
        cube = rep.create.cube(semantics=[("class", "cube")], position=(0, 500, 0))

        with camera:
            rep.modify.pose(
                look_at=rep.distribution.sequence(rep.create.group([cone, cube])),
            )

        await omni.kit.app.get_app().next_update_async()

        camera_rotation = get_rot(camera)

        np.testing.assert_allclose(camera_rotation, np.array((0.0, -45.0, 0.0)))

    async def test_modify_look_at_target_distribution(self):
        """Test that the look at target is a distribution node."""
        rep.set_global_seed(12)  # set seed to 12 to maintain old sample choice

        cube = rep.create.cube(position=(1000, 0, 0))
        sphere = rep.create.sphere(position=(0, 1000, 0))
        cone = rep.create.cone(position=(0, 0, 1000))

        camera = rep.create.camera(position=(2000, 0, 0))

        prim_paths = ["/Replicator/Cube_Xform", "/Replicator/Sphere_Xform", "/Replicator/Cone_Xform"]

        with camera:
            rep.modify.pose(look_at=rep.distribution.choice(prim_paths))

        await omni.kit.app.get_app().next_update_async()

        camera_rotation = get_rot(camera)

        # Look at sphere
        np.testing.assert_allclose(camera_rotation, np.array((0, 90, -26.565052)))

    async def test_stereo_camera_relative(self):
        """Test the camera relative positioning of a item for stereo camera."""

        stereo_camera_pair = rep.create.stereo_camera(stereo_baseline=0.2)
        # stereo_camera_pair = rep.create.camera()
        render_products = rep.create.render_product(stereo_camera_pair, (1024, 512))

        if not isinstance(render_products, list):
            render_products = [render_products]
        cube = rep.create.cube()

        with cube:
            rep.modify.pose_camera_relative(
                stereo_camera_pair, render_products[0], distance=100, horizontal_location=0, vertical_location=0
            )

        await omni.kit.app.get_app().next_update_async()

        cube_xform_prim = cube.get_output_prims()["prims"][0]
        cube_position = np.array(cube_xform_prim.GetAttribute("xformOp:translate").Get())

        np.testing.assert_allclose(cube_position, np.array((-0.1, 0, -100)))

    async def test_stereo_camera_relative_input_prims(self):
        """Test the camera relative positioning of a item for stereo camera."""

        stereo_camera_pair = rep.create.stereo_camera(stereo_baseline=0.2)
        # stereo_camera_pair = rep.create.camera()
        render_products = rep.create.render_product(stereo_camera_pair, (1024, 512))

        if not isinstance(render_products, list):
            render_products = [render_products]
        cube = rep.create.cube()

        rep.modify.pose_camera_relative(
            stereo_camera_pair,
            render_products[0],
            distance=100,
            horizontal_location=0,
            vertical_location=0,
            input_prims=cube,
        )

        await omni.kit.app.get_app().next_update_async()

        cube_xform_prim = cube.get_output_prims()["prims"][0]
        cube_position = np.array(cube_xform_prim.GetAttribute("xformOp:translate").Get())

        np.testing.assert_allclose(cube_position, np.array((-0.1, 0, -100)))

    async def test_modify_attribute_static(self):
        stage = omni.usd.get_context().get_stage()

        spheres = rep.create.sphere(count=5, as_mesh=False)
        sphere_prim_paths = rep.utils.get_node_targets(spheres.node, "outputs:prims", replicatorXform=False)

        for sphere_prim_path in sphere_prim_paths:
            prim = get_prim_at_path(sphere_prim_path)
            self.assertEqual(prim.GetAttribute("radius").Get(), 1.0)

        with spheres:
            rep.modify.attribute("radius", 123.4, attribute_type="double")

        await rep.orchestrator.step_async()

        for sphere_prim_path in sphere_prim_paths:
            prim = get_prim_at_path(sphere_prim_path)
            self.assertEqual(prim.GetAttribute("radius").Get(), 123.4)

    async def test_modify_attribute_static_input_prims(self):
        stage = omni.usd.get_context().get_stage()

        spheres = rep.create.sphere(count=5, as_mesh=False)
        sphere_prim_paths = rep.utils.get_node_targets(spheres.node, "outputs:prims", replicatorXform=False)

        for sphere_prim_path in sphere_prim_paths:
            prim = get_prim_at_path(sphere_prim_path)
            self.assertEqual(prim.GetAttribute("radius").Get(), 1.0)

        rep.modify.attribute("radius", 123.4, attribute_type="double", input_prims=spheres)

        await rep.orchestrator.step_async()

        for sphere_prim_path in sphere_prim_paths:
            prim = get_prim_at_path(sphere_prim_path)
            self.assertEqual(prim.GetAttribute("radius").Get(), 123.4)

    async def test_camera_look_at_y_up(self):
        stage = omni.usd.get_context().get_stage()
        UsdGeom.SetStageUpAxis(stage, "Y")

        target = rep.create.cone(position=(500, 500, 0))
        camera = rep.create.camera(look_at=target)
        await omni.kit.app.get_app().next_update_async()

        camera_rot = get_rot(camera)

        np.testing.assert_allclose(camera_rot, np.array((0, -90, 45)))

    async def test_camera_look_at_z_up(self):
        stage = omni.usd.get_context().get_stage()
        UsdGeom.SetStageUpAxis(stage, "Z")

        target = rep.create.cone(position=(350, 850, 850))
        camera = rep.create.camera(position=(350, 350, 350), look_at=target)
        await omni.kit.app.get_app().next_update_async()

        camera_rot = get_rot(camera)

        np.testing.assert_allclose(camera_rot, np.array((135, 0, 0)), atol=1e-8)

        rep.create.cone(position=(0, 100, 0))
        rp = rep.create.render_product("/OmniverseKit_Persp", (100, 100))
        depth_anno = rep.annotators.get("distance_to_camera")
        depth_anno.attach(rp)
        rgb_anno = rep.annotators.get("rgb")
        rgb_anno.attach(rp)
        for pos in [
            (500, 0, 0),
            (0, 500, 0),
            (0, 0, 500),
            (500, 500, 500),
            (500, 500, 0),
            (500, 0, 500),
            (0, 500, 500),
        ]:
            cam = rep.create.camera(position=pos, look_at=(0, 100, 0))
            # stage_usdrt = usdrt.Usd.Stage.Attach(omni.usd.get_context().get_stage_id())
            # stage_usdrt.WriteToStage()
            cam_path = f"{cam.get_output('prims')[0]}/Camera"
            rp.hydra_texture.set_camera_path(str(cam_path))
            await rep.orchestrator.step_async()
            self.assertLess(depth_anno.get_data()[50, 50], 100)

    async def test_camera_rot_y_up(self):
        stage = omni.usd.get_context().get_stage()
        UsdGeom.SetStageUpAxis(stage, "Y")

        target = rep.create.cone(position=(500, 0, 0))
        camera = rep.create.camera(rotation=(0, -90, 0))
        await omni.kit.app.get_app().next_update_async()

        camera_rot = get_rot(camera)

        np.testing.assert_allclose(camera_rot, np.array((0, -90, 0)))

    async def test_camera_rot_z_up(self):
        stage = omni.usd.get_context().get_stage()
        UsdGeom.SetStageUpAxis(stage, "Z")

        target = rep.create.cone(position=(0, 500, 0))
        camera = rep.create.camera(rotation=(0, 0, -90))
        await omni.kit.app.get_app().next_update_async()

        camera_rot = get_rot(camera)
        np.testing.assert_allclose(camera_rot, np.array((90, 0, 0)), atol=1e-12)

    async def test_camera_look_at_y_align(self):
        """Test if the look at direction is aligned with Y up axis"""
        stage = omni.usd.get_context().get_stage()
        UsdGeom.SetStageUpAxis(stage, "Y")

        target = rep.create.cone(position=(0, 100, 0))
        camera = rep.create.camera(position=(0, 500, 0), look_at=target)
        await omni.kit.app.get_app().next_update_async()

        camera_rot = get_rot(camera)
        np.testing.assert_allclose(camera_rot, np.array((-90, 0, 0)))

    async def test_camera_look_at_z_align(self):
        """Test if the look at direction is aligned with Z up axis"""
        stage = omni.usd.get_context().get_stage()
        UsdGeom.SetStageUpAxis(stage, "Z")

        target = rep.create.cone(position=(0, 0, 100))
        camera = rep.create.camera(position=(0, 0, 500), look_at=target)
        await omni.kit.app.get_app().next_update_async()

        camera_rot = get_rot(camera)
        np.testing.assert_allclose(camera_rot, np.array((0, 0, 90)), atol=1e-5)

    async def test_camera_look_at_custom_align(self):
        """Test if the look at direction is aligned with custom look-up axis"""
        stage = omni.usd.get_context().get_stage()
        UsdGeom.SetStageUpAxis(stage, "Z")

        target = rep.create.cone(position=(0, 0, 0))
        camera = rep.create.camera(position=(0, 500, 500), look_at=target, look_at_up_axis=(0, 1, 1))
        await omni.kit.app.get_app().next_update_async()

        camera_rot = get_rot(camera)
        np.testing.assert_allclose(camera_rot, np.array((0, 45, 90)), atol=1e-5)

    async def test_set_time(self):
        """Test that the timeline is being set to the passed in time"""
        await omni.usd.get_context().new_stage_async()
        timeline_iface = omni.timeline.acquire_timeline_interface()
        timeline_iface.set_current_time(0)

        start_time = timeline_iface.get_current_time()

        with rep.trigger.on_frame(max_execs=1):
            rep.modify.time(250)

        # await omni.kit.app.get_app().next_update_async()
        await rep.orchestrator.step_async()

        new_time = timeline_iface.get_current_time()

        self.assertEqual(start_time, 0.0, msg="Start time is not 0.0s")
        self.assertEqual(new_time, 250.0, msg="Set time is not 250.0s")

    async def test_set_time_random(self):
        """Test that the timeline is being set to the passed in time"""
        await omni.usd.get_context().new_stage_async()
        timeline_iface = omni.timeline.acquire_timeline_interface()
        timeline_iface.set_current_time(0)

        start_time = timeline_iface.get_current_time()

        with rep.trigger.on_frame(max_execs=1):
            rep.modify.frame(rep.distribution.uniform(0, 500))

        # await omni.kit.app.get_app().next_update_async()
        await rep.orchestrator.step_async()

        new_time = timeline_iface.get_current_time()

        self.assertEqual(start_time, 0.0, msg="Start time is not 0.0s")
        self.assertNotEqual(start_time, new_time, msg="New time was not randomized.")

    async def test_set_frame(self):
        """Test that the timeline is being set to the passed in frame"""
        await omni.usd.get_context().new_stage_async()
        timeline_iface = omni.timeline.acquire_timeline_interface()
        timeline_iface.set_current_time(0)

        fps = float(timeline_iface.get_time_codes_per_seconds())
        start_time = timeline_iface.get_current_time()

        with rep.trigger.on_frame(max_execs=1):
            rep.modify.frame(250)

        # await omni.kit.app.get_app().next_update_async()
        await rep.orchestrator.step_async()

        new_time = timeline_iface.get_current_time()

        self.assertEqual(start_time, 0.0, msg="Start time is not 0.0s")
        self.assertEqual(new_time, (250 / fps), msg=f"New time is not 250 / {fps}")

    async def test_exec_dependent_on_population(self):
        asset_paths = rep.example.ASSETS

        camera = rep.create.camera(position=(0, 0, 1000))

        with rep.trigger.on_frame():
            instance = rep.randomizer.instantiate(paths=rep.distribution.sequence(asset_paths), size=1)

            with instance:
                rep.modify.pose(position=rep.distribution.uniform((-500, -500, 0), (500, 500, 0)))

            with camera:
                rep.modify.pose(look_at=instance)

        await rep.orchestrator.step_async()

        camera_rot = get_rot(camera)
        self.assertNotEqual(camera_rot[0], 0.0)
        self.assertNotEqual(camera_rot[1], 0.0)

    async def test_exec_dependent_on_get_prims(self):
        cube1 = rep.create.cube(semantics=[("class", "cube")])
        cube2 = rep.create.cube(semantics=[("class", "cube")])

        camera = rep.create.camera(position=(0, 0, 1000))

        cubes = rep.get.prims(semantics=[("class", "cube")])

        with rep.trigger.on_frame():
            with cubes:
                rep.modify.pose(position=rep.distribution.uniform((-500, -500, 0), (500, 500, 0)))

            with camera:
                rep.modify.pose(look_at=cubes)

        await rep.orchestrator.step_async()

        camera_rot = get_rot(camera)
        self.assertNotEqual(camera_rot[0], 0.0)
        self.assertNotEqual(camera_rot[1], 0.0)

    async def test_exec_dependent_on_get_prim_at_path(self):
        cube1 = rep.create.cube(semantics=[("class", "cube")])

        camera = rep.create.camera(position=(0, 0, 1000))

        cube = rep.get.prim_at_path("/Replicator/Cube_Xform")

        with rep.trigger.on_frame():
            with cube:
                rep.modify.pose(position=rep.distribution.uniform((-500, -500, 0), (500, 500, 0)))

            with camera:
                rep.modify.pose(look_at=cube)

        await rep.orchestrator.step_async()

        camera_rot = get_rot(camera)
        self.assertNotEqual(camera_rot[0], 0.0)
        self.assertNotEqual(camera_rot[1], 0.0)

    async def test_modify_material_prims(self):
        """Tests if the OmniPBR created by the create node is bound to the prim"""
        await omni.usd.get_context().new_stage_async()

        mat_path = "/Replicator/Looks/OmniPBR"

        # Create cubes
        cubes = rep.create.cube(count=5)
        cube_prims = cubes.get_output_prims()["prims"]
        cube_paths = cubes.get_output("prims")

        mats = rep.create.material_omnipbr(count=25)
        choice = rep.distribution.choice(mats)

        with cubes:
            rep.modify.material(choice)

        await omni.kit.app.get_app().next_update_async()

        for prim, mat in zip(cube_prims, choice.get_output("samples")):
            self.assertTrue(prim.IsValid(), "Cube prim created not valid!")
            self.assertEqual(
                str(UsdShade.MaterialBindingAPI(prim).GetDirectBinding().GetMaterial().GetPath()),
                str(mat),
                "Bound material is not correct!",
            )

    async def test_modify_material_paths(self):
        """Tests if the material at a path is bound to the prim"""
        await omni.usd.get_context().new_stage_async()

        mat_path1 = "/World/Looks/Test_Material1"
        mat_path2 = "/World/Looks/Test_Material2"

        cube_path = "/World/Cube"

        # Create a cube
        omni.kit.commands.execute("CreatePrim", prim_path=cube_path, prim_type="Cube")
        # Create materials
        omni.kit.commands.execute("CreatePreviewSurfaceMaterialPrimCommand", mtl_path=mat_path1)
        omni.kit.commands.execute("CreatePreviewSurfaceMaterialPrimCommand", mtl_path=mat_path2)

        cube = rep.get.prims(cube_path)

        with cube:
            rep.modify.material([mat_path1, mat_path2])

        await omni.kit.app.get_app().next_update_async()
        stage = omni.usd.get_context().get_stage()

        prim = get_prim_at_path(cube_path)
        self.assertTrue(prim.IsValid(), "Cube prim created not valid!")

        self.assertTrue(
            UsdShade.MaterialBindingAPI(prim).GetDirectBinding().GetMaterial().GetPath() == mat_path1
            or UsdShade.MaterialBindingAPI(prim).GetDirectBinding().GetMaterial().GetPath() == mat_path2,
            "Neither test material was bound to the cube!",
        )

    async def test_modify_projection(self):
        """Test to see if the projection material is updated"""
        smile_diffuse = os.path.join(TEST_DATA_DIR, "objects", "textures", "smiley_albedo.png")
        smile_normal = os.path.join(TEST_DATA_DIR, "objects", "textures", "smiley_normal.png")
        smile_roughness = os.path.join(TEST_DATA_DIR, "objects", "textures", "smiley_rough.png")

        await omni.usd.get_context().new_stage_async()

        torus = rep.create.torus()
        proxy = rep.create.cube(position=(50, 100, 0), rotation=(0, 0, 90), scale=(0.2, 0.2, 0.2))

        sem = [("class", "smile")]

        with torus:
            projection = rep.create.projection_material(proxy, sem)

        with projection:
            rep.modify.projection_material(diffuse=smile_diffuse, normal=smile_normal, roughness=smile_roughness)

        await omni.kit.app.get_app().next_update_async()

        # Check structure
        self.assertTrue(get_prim_at_path("/Replicator/Torus_Xform/Projection/Cube_Xform").IsValid())

        projection_prim = get_prim_at_path("/Replicator/Torus_Xform/Projection/Cube_Xform")

        # Check materials
        self.assertEqual(
            str(UsdShade.MaterialBindingAPI(projection_prim).GetDirectBinding().GetMaterial().GetPath()),
            "/Looks/ProjectPBRMaterial",
        )

        projection_mat = (
            UsdShade.MaterialBindingAPI(projection_prim).GetDirectBinding().GetMaterial().GetPrim().GetChild("Shader")
        )

        self.assertEqual(
            str(projection_mat.GetAttribute("inputs:diffuse_texture").Get()).replace("@", ""), smile_diffuse
        )
        self.assertEqual(
            str(projection_mat.GetAttribute("inputs:normalmap_texture").Get()).replace("@", ""), smile_normal
        )
        self.assertEqual(
            str(projection_mat.GetAttribute("inputs:reflectionroughness_texture").Get()).replace("@", ""),
            smile_roughness,
        )

        # Check that primvars exist
        self.assertTrue(projection_prim.GetAttribute("primvars:projection_quat").IsValid())
        self.assertTrue(projection_prim.GetAttribute("primvars:projection_position").IsValid())
        self.assertTrue(projection_prim.GetAttribute("primvars:projection_scale").IsValid())
        self.assertTrue(projection_prim.GetAttribute("primvars:doNotCastShadows").IsValid())

        # Check that primvars are updated
        self.assertEqual(projection_prim.GetAttribute("primvars:projection_quat").Get(), (0, 0, 0.70710677, 0.70710677))
        self.assertEqual(projection_prim.GetAttribute("primvars:projection_position").Get(), (50.0, 100.0, 0.0))
        self.assertEqual(projection_prim.GetAttribute("primvars:projection_scale").Get(), (0.2, 0.2, 0.2))
        self.assertEqual(projection_prim.GetAttribute("primvars:doNotCastShadows").Get(), True)

        # Check semantics
        p_sem = UsdSemantics.LabelsAPI(projection_prim, "class")

        self.assertEquals(p_sem.GetLabelsAttr().Get(), ["smile"])

        # Check that changing proxy pose updates primvars
        proxy_prim = proxy.get_output_prims()["prims"][0]
        proxy_prim.GetAttribute("xformOp:translate").Set((60, 100, -50))
        proxy_prim.GetAttribute("xformOp:rotateXYZ").Set((-160, 20, 90))
        proxy_prim.GetAttribute("xformOp:scale").Set((0.4, 0.4, 0.4))

        await omni.kit.app.get_app().next_update_async()

        self.assertEqual(projection_prim.GetAttribute("primvars:projection_position").Get(), (60.0, 100.0, -50.0))
        self.assertEqual(projection_prim.GetAttribute("primvars:projection_scale").Get(), (0.4, 0.4, 0.4))
        self.assertEqual(projection_prim.GetAttribute("primvars:doNotCastShadows").Get(), True)

    async def test_modify_projection_attributes_with_distributions(self):
        """Test to see if the projection material is updated"""
        smile_diffuse = os.path.join(TEST_DATA_DIR, "objects", "textures", "smiley_albedo.png")
        smile_normal = os.path.join(TEST_DATA_DIR, "objects", "textures", "smiley_normal.png")
        smile_roughness = os.path.join(TEST_DATA_DIR, "objects", "textures", "smiley_rough.png")

        await omni.usd.get_context().new_stage_async()

        torus = rep.create.torus()
        cube = rep.create.cube(position=(50, 100, 0), rotation=(0, 0, 90), scale=(0.2, 0.2, 0.2))

        sem = [("class", "smile")]

        with torus:
            projection = rep.create.projection_material(cube, sem)

        await omni.kit.app.get_app().next_update_async()

        projection_prim = get_prim_at_path("/Replicator/Torus_Xform/Projection/Cube_Xform")
        projection_mat = (
            UsdShade.MaterialBindingAPI(projection_prim).GetDirectBinding().GetMaterial().GetPrim().GetChild("Shader")
        )

        # Get starting vars
        start_quat = projection_prim.GetAttribute("primvars:projection_quat").Get()
        start_position = projection_prim.GetAttribute("primvars:projection_position").Get()
        start_scale = projection_prim.GetAttribute("primvars:projection_scale").Get()
        start_diffuse = projection_mat.GetAttribute("inputs:diffuse_texture").Get()
        start_normal = projection_mat.GetAttribute("inputs:normalmap_texture").Get()
        start_roughness = projection_mat.GetAttribute("inputs:reflectionroughness_texture").Get()

        with rep.trigger.on_frame():
            with projection:
                rep.modify.projection_material(
                    position=rep.distribution.uniform((-300, -300, -300), (300, 300, 300), seed=10),
                    rotation=rep.distribution.uniform((-300, -300, -300), (300, 300, 300), seed=10),
                    scale=rep.distribution.uniform((-300, -300, -300), (300, 300, 300), seed=10),
                    diffuse=rep.distribution.choice([smile_diffuse, smile_normal, smile_roughness], seed=10),
                    normal=rep.distribution.choice([smile_diffuse, smile_normal, smile_roughness], seed=10),
                    roughness=rep.distribution.choice([smile_diffuse, smile_normal, smile_roughness], seed=10),
                )

        await rep.orchestrator.step_async()
        await omni.kit.app.get_app().next_update_async()

        projection_prim = get_prim_at_path("/Replicator/Torus_Xform/Projection/Cube_Xform")
        projection_mat = (
            UsdShade.MaterialBindingAPI(projection_prim).GetDirectBinding().GetMaterial().GetPrim().GetChild("Shader")
        )

        # Get updated vars
        updated_quat = projection_prim.GetAttribute("primvars:projection_quat").Get()
        updated_position = projection_prim.GetAttribute("primvars:projection_position").Get()
        updated_scale = projection_prim.GetAttribute("primvars:projection_scale").Get()
        updated_diffuse = projection_mat.GetAttribute("inputs:diffuse_texture").Get()
        updated_normal = projection_mat.GetAttribute("inputs:normalmap_texture").Get()
        updated_roughness = projection_mat.GetAttribute("inputs:reflectionroughness_texture").Get()

        # Make sure they are not the same
        self.assertNotEqual(start_quat, updated_quat)
        self.assertNotEqual(start_position, updated_position)
        self.assertNotEqual(start_scale, updated_scale)
        self.assertNotEqual(start_diffuse, updated_diffuse)
        self.assertNotEqual(start_normal, updated_normal)
        self.assertNotEqual(start_roughness, updated_roughness)

    async def test_modify_projections_custom_material(self):
        """Test to see if the custom materials will be applied to projections"""
        smile_diffuse = os.path.join(TEST_DATA_DIR, "objects", "textures", "smiley_albedo.png")

        await omni.usd.get_context().new_stage_async()

        stage = omni.usd.get_context().get_stage()

        # Stage setup
        projection_mdl = str(Path(MDL_FOLDER).joinpath("project_pbr_material.mdl").as_posix())

        omni.kit.commands.execute(
            "CreateMdlMaterialPrim",
            mtl_url=projection_mdl,
            mtl_name="ProjectPBRMaterial",
            mtl_path="/World/Looks/MyCustomProjectionMaterial",
            select_new_prim=False,
        )

        plane_prim = F.create.plane(position=(50.0, 100.0, 0.0), rotation=(0.0, 45.0, 10.0), parent="/World")

        await omni.kit.app.get_app().next_update_async()

        # Replicator setup
        plane = rep.get.prims(path_pattern="/World/Plane")
        cube01 = rep.create.cube(
            visible=False,
            semantics=[("class", "cube")],
            position=(50, 100, 0),
            rotation=(0, 0, 90),
            scale=(0.2, 0.2, 0.2),
        )
        cube02 = rep.create.cube(
            visible=False,
            semantics=[("class", "cube")],
            position=(-50, 100, 0),
            rotation=(0, 0, 90),
            scale=(0.2, 0.2, 0.2),
        )
        sem = [("class", "shape")]

        mat = rep.get.prims(path_pattern="/World/Looks/MyCustomProjectionMaterial")

        # Randomizer for scattering
        def get_shapes():
            shapes = rep.get.prims(semantics=[("class", "cube")])
            with shapes:
                rep.randomizer.scatter_2d(plane, seed=10)
            return shapes.node

        rep.randomizer.register(get_shapes)

        # Create the projection with the plane as the target
        with plane:
            proj01 = rep.create.projection_material(cube01, sem, mat)
            proj02 = rep.create.projection_material(cube02, sem, mat)

        # Modify the cube position, and update the projection
        with rep.trigger.on_frame(max_execs=1):
            rep.randomizer.get_shapes()
            with proj01:
                rep.modify.projection_material(diffuse=smile_diffuse)
            with proj02:
                rep.modify.projection_material(diffuse=smile_diffuse)

        await rep.orchestrator.step_async()
        await omni.kit.app.get_app().next_update_async()

        projection_prim_01 = get_prim_at_path("/World/Plane/Projection/Cube_Xform")
        projection_mat_01 = (
            UsdShade.MaterialBindingAPI(projection_prim_01).GetDirectBinding().GetMaterial().GetPath().pathString
        )
        projection_prim_02 = get_prim_at_path("/World/Plane/Projection/Cube_Xform_01")
        projection_mat_02 = (
            UsdShade.MaterialBindingAPI(projection_prim_02).GetDirectBinding().GetMaterial().GetPath().pathString
        )

        # Check that material applied is custom material
        materials = ["/World/Looks/MyCustomProjectionMaterial_01", "/World/Looks/MyCustomProjectionMaterial_02"]
        self.assertTrue(projection_mat_01 in materials, "Custom material not being used!")
        materials.remove(projection_mat_01)
        self.assertEquals(projection_mat_02, materials[0], "Custom material not being used!")

    async def test_semantics(self):
        """Test assigning semantics."""
        cones = rep.create.cone(count=10)
        # Apply with a list, multiple objects
        with cones:
            rep.modify.semantics(["class:sphere", "material:rubber"])

        # Apply semantics at creation
        cube = rep.create.cube(semantics=[("shape", "cube")])
        sphere = rep.create.sphere()
        # Apply single tuple
        with sphere:
            rep.modify.semantics(semantics=("shape", "sphere"))

        await omni.kit.app.get_app().next_update_async()

        for cone in cones.get_output_prims()["prims"]:
            semantics = rep.utils.parse_semantics(cone)
            self.assertEqual(set([("class", "sphere"), ("material", "rubber")]), set(semantics))

        cube_semantics = rep.utils.parse_semantics(cube.get_output_prims()["prims"][0])
        sphere_semantics = rep.utils.parse_semantics(sphere.get_output_prims()["prims"][0])
        self.assertEqual([("shape", "cube")], cube_semantics)
        self.assertEqual([("shape", "sphere")], sphere_semantics)

    async def test_semantics_add(self):
        """Test adding semantics."""
        cones = rep.create.cone(count=10, semantics=[("class", "remain"), ("shape", "cone")])

        with cones:
            rep.modify.semantics(["class:sphere", "material:rubber"], mode="add")

        await omni.kit.app.get_app().next_update_async()

        for cone in cones.get_output_prims()["prims"]:
            semantics = rep.utils.parse_semantics(cone)
            self.assertEqual(
                set([("class", "sphere"), ("class", "remain"), ("material", "rubber"), ("shape", "cone")]),
                set(semantics),
            )

    async def test_semantics_replace(self):
        """Test adding semantics."""
        cones = rep.create.cone(count=10, semantics=[("class", "replace"), ("shape", "cone"), ("material", "old")])

        with cones:
            rep.modify.semantics(["class:sphere", "material:rubber"], mode="replace")

        await omni.kit.app.get_app().next_update_async()

        for cone in cones.get_output_prims()["prims"]:
            semantics = rep.utils.parse_semantics(cone)
            self.assertEqual(set([("class", "sphere"), ("material", "rubber"), ("shape", "cone")]), set(semantics))

    async def test_semantics_replace_rep_item(self):
        """Test adding semantics."""
        cones = rep.create.cone(count=10, semantics=[("class", "replace"), ("shape", "cone")])

        with cones:
            rep.modify.semantics(rep.distribution.choice(["class:sphere"]), mode="replace")

        await omni.kit.app.get_app().next_update_async()

        for cone in cones.get_output_prims()["prims"]:
            semantics = rep.utils.parse_semantics(cone)
            self.assertEqual(set([("class", "sphere"), ("shape", "cone")]), set(semantics))

    async def test_semantics_clear(self):
        """Test adding semantics."""
        cones = rep.create.cone(count=10, semantics=[("class", "remain"), ("shape", "cone")])

        with cones:
            rep.modify.semantics(["class:sphere", "material:rubber"], mode="clear")

        await omni.kit.app.get_app().next_update_async()

        for cone in cones.get_output_prims()["prims"]:
            semantics = rep.utils.parse_semantics(cone)
            self.assertEqual(set([("class", "sphere"), ("material", "rubber")]), set(semantics))

    async def test_modify_variant(self):
        """Test modifying a variant on a prim."""
        variant_example = os.path.join(TEST_DATA_DIR, "objects", "test_variant.usd")

        await omni.usd.get_context().open_stage_async(variant_example)

        sphere = rep.get.prims("/World/Sphere$")

        with rep.trigger.on_frame(max_execs=10):
            with sphere:
                rep.modify.variant("colorVariant", rep.distribution.choice(["red", "green", "blue"]))

        await rep.orchestrator.step_async()
        stage = omni.usd.get_context().get_stage()

        selection = stage.GetPrimAtPath("/World/Sphere").GetVariantSet("colorVariant").GetVariantSelection()
        self.assertEqual(selection, "blue")
        color = stage.GetPrimAtPath("/World/Sphere/OmniPBR/Shader").GetAttribute("inputs:diffuse_color_constant").Get()
        self.assertEqual(color, Gf.Vec3f(0.0, 0.0, 1.0))

        # Step 3 times to get variant to change with seed
        for _ in range(3):
            await rep.orchestrator.step_async()
        stage = omni.usd.get_context().get_stage()

        selection = stage.GetPrimAtPath("/World/Sphere").GetVariantSet("colorVariant").GetVariantSelection()
        self.assertEqual(selection, "green")
        color = stage.GetPrimAtPath("/World/Sphere/OmniPBR/Shader").GetAttribute("inputs:diffuse_color_constant").Get()
        self.assertEqual(color, Gf.Vec3f(0.0, 1.0, 0.0))

    async def test_pose_orbit_prim(self):
        stage = omni.usd.get_context().get_stage()
        UsdGeom.SetStageUpAxis(stage, "Y")
        barycentre_position = np.array([1000, 1000, 1000])
        barycentre = rep.create.sphere(semantics=[("class", "sphere")], scale=0.2)
        camera = rep.create.camera()

        rp = rep.create.render_product(camera, (100, 100))
        anno = rep.annotators.get("bounding_box_2d_tight")
        anno.attach(rp)

        with rep.trigger.on_frame():
            # Test that orbit will be sequenced after the sphere is moved
            with barycentre:
                rep.modify.pose(position=barycentre_position)
            with camera:
                rep.modify.pose_orbit(
                    barycentre=barycentre,
                    distance=rep.distribution.uniform(800, 1000),
                    azimuth=rep.distribution.uniform(-90, 90),
                    elevation=45,
                )

        camera_prim = camera.get_output_prims()["prims"][0]

        for _ in range(5):
            await rep.orchestrator.step_async()

            camera_trans = camera_prim.GetAttribute("xformOp:translate").Get()

            distance_computed = np.linalg.norm(np.array(camera_trans) - barycentre_position)
            bbox = anno.get_data()["data"][0]
            bbox_centre = np.mean(np.array([bbox["x_min"], bbox["y_min"], bbox["x_max"], bbox["y_max"]]))
            self.assertAlmostEqual(bbox_centre, 50.0, places=0)
            distance_computed = np.linalg.norm(np.array(camera_trans) - barycentre_position)
            self.assertGreater(distance_computed, 800.0)
            self.assertGreater(1000.0, distance_computed)

    # TODO jlafleche Enable once samplers are execution nodes
    @unittest.skip("Test requires change to exec samplers")
    async def test_pose_orbit_path_choice(self):
        stage = omni.usd.get_context().get_stage()
        UsdGeom.SetStageUpAxis(stage, "Y")
        barycentre_position1 = np.array([1000, 10000, 1000])
        barycentre_position2 = np.array([-1000, -10000, -1000])
        sphere = rep.create.sphere(semantics=[("class", "sphere")], scale=0.3)
        cube = rep.create.cube(semantics=[("class", "cube")], scale=0.3)
        camera = rep.create.camera()

        rp = rep.create.render_product(camera, (100, 100))
        anno = rep.annotators.get("bounding_box_2d_tight")
        anno.attach(rp)
        rgb = rep.annotators.get("rgb")
        rgb.attach(rp)

        with rep.trigger.on_frame():
            # Test that orbit will be sequenced after the sphere is moved
            barycentre = rep.distribution.choice(["/Replicator/Sphere_Xform", "/Replicator/Cube_Xform"])

            # with utils.sequential():
            with sphere:
                rep.modify.pose(position=barycentre_position1)
            with cube:
                rep.modify.pose(position=barycentre_position2)
            with camera:
                rep.modify.pose_orbit(
                    barycentre=barycentre,
                    distance=rep.distribution.uniform(800, 1000),
                    azimuth=rep.distribution.uniform(-90, 90),
                    elevation=45,
                )

        camera_prim = camera.get_output_prims()["prims"][0]
        rep.orchestrator.preview()
        rep.create.light(light_type="distant")

        for _ in range(5):
            await rep.orchestrator.step_async()

            camera_trans = camera_prim.GetAttribute("xformOp:translate").Get()

            bbox_data = anno.get_data()

            bbox = bbox_data["data"][0]
            bbox_centre = np.mean(np.array([bbox["x_min"], bbox["y_min"], bbox["x_max"], bbox["y_max"]]))
            semantic = bbox_data["info"]["idToLabels"][str(bbox["semanticId"])]["class"]

            barycentre_position = barycentre_position1 if semantic == "sphere" else barycentre_position2

            distance_computed = np.linalg.norm(np.array(camera_trans) - barycentre_position)
            self.assertAlmostEqual(bbox_centre, 50.0, places=0)
            distance_computed = np.linalg.norm(np.array(camera_trans) - barycentre_position)
            self.assertGreater(distance_computed, 800.0)
            self.assertGreater(1000.0, distance_computed)

    async def test_pose_orbit_path(self):
        stage = omni.usd.get_context().get_stage()
        UsdGeom.SetStageUpAxis(stage, "Y")

        barycentre_position = np.array([1000, 1000, 1000])
        barycentre = rep.create.sphere(semantics=[("class", "sphere")], scale=0.2)
        camera = rep.create.camera()

        rp = rep.create.render_product(camera, (100, 100))
        anno = rep.annotators.get("bounding_box_2d_tight")
        anno.attach(rp)

        with rep.trigger.on_frame():
            # Test that orbit will be sequenced after the sphere is moved
            with barycentre:
                rep.modify.pose(position=barycentre_position)
            with camera:
                rep.modify.pose_orbit(
                    barycentre="/Replicator/Sphere_Xform",
                    distance=rep.distribution.uniform(800, 1000),
                    azimuth=rep.distribution.uniform(-90, 90),
                    elevation=45,
                )

        camera_prim = camera.get_output_prims()["prims"][0]

        for _ in range(5):
            await rep.orchestrator.step_async()

            camera_trans = camera_prim.GetAttribute("xformOp:translate").Get()

            distance_computed = np.linalg.norm(np.array(camera_trans) - barycentre_position)
            bbox = anno.get_data()["data"][0]
            bbox_centre = np.mean(np.array([bbox["x_min"], bbox["y_min"], bbox["x_max"], bbox["y_max"]]))
            self.assertAlmostEqual(bbox_centre, 50.0, places=0)
            self.assertGreater(distance_computed, 800.0)
            self.assertGreater(1000.0, distance_computed)

    async def test_pose_orbit_coord(self):
        stage = omni.usd.get_context().get_stage()
        UsdGeom.SetStageUpAxis(stage, "Z")

        barycentre_position = np.array([1000, 1000, 1000])
        barycentre = rep.create.sphere(semantics=[("class", "sphere")], scale=0.2)
        camera = rep.create.camera()

        rp = rep.create.render_product(camera, (100, 100))
        anno = rep.annotators.get("bounding_box_2d_loose")
        anno.attach(rp)

        with rep.trigger.on_frame():
            # Test that orbit will be sequenced after the sphere is moved
            with barycentre:
                rep.modify.pose(position=barycentre_position)
            with camera:
                rep.modify.pose_orbit(
                    barycentre=barycentre_position,
                    distance=rep.distribution.uniform(800, 1000),
                    azimuth=rep.distribution.uniform(-90, 90),
                    elevation=45,
                )

        camera_prim = camera.get_output_prims()["prims"][0]

        for _ in range(5):
            await rep.orchestrator.step_async()

            camera_trans = camera_prim.GetAttribute("xformOp:translate").Get()

            distance_computed = np.linalg.norm(np.array(camera_trans) - barycentre_position)
            bbox = anno.get_data()["data"][0]
            bbox_centre = np.mean(np.array([bbox["x_min"], bbox["y_min"], bbox["x_max"], bbox["y_max"]]))
            self.assertAlmostEqual(bbox_centre, 50.0, places=0)
            distance_computed = np.linalg.norm(np.array(camera_trans) - barycentre_position)
            self.assertGreater(distance_computed, 800.0)
            self.assertGreater(1000.0, distance_computed)

    async def test_modify_arbitrary_material_attribute(self):
        material = rep.create.material_omnipbr()

        with material:
            rep.modify.attribute("some_cool_property", 5.5, "float")

        await rep.orchestrator.step_async()

        material_prim = material.get_output_prims()["prims"][0]
        shader_prim = material_prim.GetChildren()[0]
        self.assertTrue(shader_prim.HasAttribute("inputs:some_cool_property"))
        self.assertEqual(shader_prim.GetAttribute("inputs:some_cool_property").Get(), 5.5)

    async def test_modify_semantics(self):
        """Test modifying semantics."""
        cones = [rep.create.cone() for _ in range(10)]
        per_object_semantics = [[("class", "sphere"), ("class", "ball"), ("material", f"rubber{i}")] for i in range(10)]

        # Apply with a list, multiple objects
        for i, cone in enumerate(cones):
            with cone:
                rep.modify.semantics(per_object_semantics[i])

        per_object_gt = per_object_semantics

        await omni.kit.app.get_app().next_update_async()

        # Verify that the semantics are applied to the cones
        for i, cone in enumerate(cones):
            semantics = rep.utils.parse_semantics(cone.get_output_prims()["prims"][0])
            self.assertEqual(set(per_object_gt[i]), set(semantics))

        # Apply more semantics
        per_object_semantics2 = [("class", "3d_sphere"), ("material", "vulcanized_rubber")]
        cones_group = rep.create.group([str(c.get_output("prims")[0]) for c in cones])
        with cones_group:
            rep.modify.semantics(per_object_semantics2)

        await omni.kit.app.get_app().next_update_async()

        # Verify that the semantics are applied to the cones
        for i, cone in enumerate(cones):
            semantics = rep.utils.parse_semantics(cone.get_output_prims()["prims"][0])
            per_object_gt[i].extend(per_object_semantics2)
            self.assertEqual(set(per_object_gt[i]), set(semantics))

        # Test replace semantics
        per_object_semantics3 = [("class", "ceci_nest_pas_une_balle")]

        with cones_group:
            rep.modify.semantics(per_object_semantics3, mode="replace")

        await omni.kit.app.get_app().next_update_async()

        # Verify that the semantics are applied to the cones
        for i, cone in enumerate(cones):
            per_object_gt[i] = [v for v in per_object_gt[i] if v[0] != "class"]
            per_object_gt[i].extend(per_object_semantics3)
            semantics = rep.utils.parse_semantics(cone.get_output_prims()["prims"][0])
            self.assertEqual(set(per_object_gt[i]), set(semantics))

        # Test clear semantics
        per_object_semantics4 = [("action", "rolling")]
        with cones_group:
            rep.modify.semantics(per_object_semantics4, mode="clear")

        await omni.kit.app.get_app().next_update_async()

        # Verify that the semantics are applied to the cones
        for i, cone in enumerate(cones):
            semantics = rep.utils.parse_semantics(cone.get_output_prims()["prims"][0])
            self.assertEqual(set(per_object_semantics4), set(semantics))

        # Test full clear
        with cones_group:
            rep.modify.semantics(mode="clear")

        await omni.kit.app.get_app().next_update_async()

        # Verify that the semantics are applied to the cones
        for i, cone in enumerate(cones):
            semantics = rep.utils.parse_semantics(cone.get_output_prims()["prims"][0])
            self.assertEqual([], semantics)

    async def test_modify_xform_attribute(self):
        """Test modifying an Xform attribute."""
        xform = rep.create.xform()
        xform_prim = xform.get_output_prims()["prims"][0]

        # Create a dummy attribute
        xform_prim.CreateAttribute("dummy", pxr.Sdf.ValueTypeNames.Bool).Set(False)

        with xform:
            rep.modify.attribute("dummy", True)

        await rep.orchestrator.step_async()

        self.assertTrue(xform_prim.GetAttribute("dummy").Get())

    async def test_modify_attribute_vec2(self):
        """Test modifying a Vec2 (float2) attribute on a material."""
        material = rep.create.material_omnipbr()

        # Modify an existing Vec2 input on the shader (texture_scale)
        with material:
            rep.modify.attribute(
                "inputs:texture_scale",
                (20.0, 30.0),
                attribute_type="float2",
            )

        # Execute the graph so the modify node runs
        await rep.orchestrator.step_async()

        # Retrieve the shader prim and validate the attribute value
        material_prim = material.get_output_prims()["prims"][0]
        shader_prim = material_prim.GetChildren()[0]

        self.assertTrue(
            shader_prim.HasAttribute("inputs:texture_scale"),
            "Shader is missing the expected 'inputs:texture_scale' attribute",
        )

        texture_scale = np.array(shader_prim.GetAttribute("inputs:texture_scale").Get())
        np.testing.assert_allclose(texture_scale, np.array((20.0, 30.0)))

    async def test_modify_attribute_vec4(self):
        """Test modifying Vec4 (float4 and double4) attributes on a material."""
        material = rep.create.material_omnipbr()

        vec4f_value = (1.1, 2.2, 3.3, 4.4)
        vec4d_value = (10.1, 11.2, 12.3, 13.4)

        # Apply both float4 and double4 modifications
        with material:
            rep.modify.attribute("inputs:vec4f_test", vec4f_value, attribute_type="float4")
            rep.modify.attribute("inputs:vec4d_test", vec4d_value, attribute_type="double4")

        # Execute graph so the modifications propagate
        await rep.orchestrator.step_async()

        # Validate results
        material_prim = material.get_output_prims()["prims"][0]
        shader_prim = material_prim.GetChildren()[0]

        # Float4 check
        self.assertTrue(shader_prim.HasAttribute("inputs:vec4f_test"))
        fetched_vec4f = np.array(shader_prim.GetAttribute("inputs:vec4f_test").Get())
        np.testing.assert_allclose(fetched_vec4f, np.array(vec4f_value))

        # Double4 check
        self.assertTrue(shader_prim.HasAttribute("inputs:vec4d_test"))
        fetched_vec4d = np.array(shader_prim.GetAttribute("inputs:vec4d_test").Get())
        np.testing.assert_allclose(fetched_vec4d, np.array(vec4d_value))

    async def test_modify_semantics_with_existing_schema(self):
        # Create a cube and apply a rigid body schema
        cube = rep.create.cube()
        with cube:
            rep.physics.rigid_body()

        # Apply semantics with instance "class" and label "cube" using add (append)
        with cube:
            rep.modify.semantics(["class:cube"], mode="add")

        await omni.kit.app.get_app().next_update_async()

        # Fetch the created prim
        cube_prim = cube.get_output_prims()["prims"][0]

        # Verify rigid body schemas are still applied
        self.assertTrue(cube_prim.HasAPI(pxr.UsdPhysics.RigidBodyAPI))
        self.assertTrue(cube_prim.HasAPI(pxr.PhysxSchema.PhysxRigidBodyAPI))

        # Verify semantic label was applied correctly
        semantics = rep.utils.parse_semantics(cube_prim)
        self.assertEqual(set([("class", "cube")]), set(semantics))
