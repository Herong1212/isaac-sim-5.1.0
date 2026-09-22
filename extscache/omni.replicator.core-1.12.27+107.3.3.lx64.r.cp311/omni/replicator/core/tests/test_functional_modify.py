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

import numpy as np
import omni.replicator.core.functional as F
import omni.usd
import pxr
from omni.replicator.core import utils as rep_utils
from omni.replicator.core.functional import modify


class TestModify(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()

    def test_docstrings_functional_modify(self):
        """Test module docstring examples"""
        failures, test_counts = doctest.testmod(modify)
        if failures:
            self.fail(f"Encountered {failures} failures in {test_counts} tests.")

    # Convert both Euler angles to quaternions
    @staticmethod
    # Verify prim modifications
    def verify_prim_modifications(prim, new_position, new_rotation, new_scale):
        # Extract transform from prim
        xform = pxr.Gf.Transform(pxr.UsdGeom.Xformable(prim).ComputeLocalToWorldTransform(pxr.Usd.TimeCode.Default()))

        # Check position
        position = xform.GetTranslation()
        np.testing.assert_array_almost_equal(
            position, new_position, decimal=5, err_msg=f"Position mismatch for {prim.GetPath()}"
        )

        def euler_to_quat(angles_deg):
            # Create rotation and get quaternion
            rotation = (
                pxr.Gf.Rotation(pxr.Gf.Vec3d.XAxis(), angles_deg[0])
                * pxr.Gf.Rotation(pxr.Gf.Vec3d.YAxis(), angles_deg[1])
                * pxr.Gf.Rotation(pxr.Gf.Vec3d.ZAxis(), angles_deg[2])
            )
            return rotation.GetQuat()

        # Check rotation
        quat_from_xform = xform.GetRotation().GetQuat()
        quat_from_new = euler_to_quat(new_rotation)

        # Note: need to check both q and -q since they represent the same rotation
        # np.testing.assert_array_almost_equal(quat_from_attr.GetImaginary(), quat_from_new.GetImaginary())
        np.testing.assert_array_almost_equal(
            np.array([*quat_from_xform.GetImaginary(), quat_from_xform.GetReal()]),
            np.array([*quat_from_new.GetImaginary(), quat_from_new.GetReal()]),
            err_msg=f"Rotation mismatch for {prim.GetPath()}",
        )

        # Check scale
        scale = xform.GetScale()
        np.testing.assert_array_almost_equal(
            scale, new_scale, decimal=5, err_msg=f"Scale mismatch for {prim.GetPath()}"
        )

    @staticmethod
    def verify_point_instancer_instances(instancer, new_positions, new_rotations, new_scales):
        # Get positions attribute
        positions_attr = instancer.GetAttribute("positions")
        positions = positions_attr.Get()

        # Get orientations attribute
        orientations_attr = instancer.GetAttribute("orientations")
        orientations = orientations_attr.Get()

        # Get scales attribute
        scales_attr = instancer.GetAttribute("scales")
        scales = scales_attr.Get()

        # Verify positions
        np.testing.assert_array_almost_equal(
            positions, new_positions, decimal=3, err_msg="Point instancer positions mismatch"
        )

        # Verify orientations
        # Convert XYZ euler angles to quaternions for comparison
        new_positions_quats = pxr.Vt.QuatdArray(
            [
                (
                    pxr.Gf.Rotation(pxr.Gf.Vec3d.XAxis(), angles_deg[0])
                    * pxr.Gf.Rotation(pxr.Gf.Vec3d.YAxis(), angles_deg[1])
                    * pxr.Gf.Rotation(pxr.Gf.Vec3d.ZAxis(), angles_deg[2])
                ).GetQuat()
                for angles_deg in new_rotations
            ]
        )

        np.testing.assert_array_almost_equal(
            orientations, new_positions_quats, decimal=3, err_msg="Point instancer rotations mismatch"
        )

        # Verify scales
        np.testing.assert_array_almost_equal(scales, new_scales, decimal=3, err_msg="Point instancer scales mismatch")

    def test_modify_transforms_with_point_instancer(self):
        """Tests modification of position, rotation and scale for multiple prims and point instancer instances.

        Tests:
            - Creating basic prims and a point instancer with 10 prototypes
            - Modifying position, rotation, and scale for each prim and instance
            - Verifying transform changes are applied correctly
        """

        rng = np.random.default_rng(42)

        # Create test stage and basic prims
        stage = omni.usd.get_context().get_stage()
        cube = stage.DefinePrim("/World/cube", "Cube")
        sphere = stage.DefinePrim("/World/sphere", "Sphere")
        cylinder = stage.DefinePrim("/World/cylinder", "Cylinder")

        # Number of instances in the point instancer
        num_instances = 10

        # Create point instancer with some prototypes
        instancer = stage.DefinePrim("/World/instancer", "PointInstancer")
        proto0 = stage.DefinePrim(f"/World/instancer/proto0", "Sphere")
        proto1 = stage.DefinePrim(f"/World/instancer/proto1", "Cube")
        prototypes = [proto0, proto1]

        # Set up prototypes relationship for point instancer
        instancer.GetRelationship("prototypes").SetTargets([str(p.GetPath()) for p in prototypes])

        # Set up indices for the point instancer
        indices_attr = instancer.GetAttribute("protoIndices")
        indices_attr.Set([i % len(prototypes) for i in range(num_instances)])

        # Create list of prims to modify
        prims_to_modify = [cube, sphere, cylinder, instancer]

        # Generate random transformations for all prims and instances
        total_count = len(prims_to_modify) - 1 + num_instances

        # Test position modification
        new_positions = rng.uniform(-5.0, 5.0, size=(total_count, 3))

        # Test rotation modification (in degrees)
        new_rotations = rng.uniform(-45.0, 45.0, size=(total_count, 3))

        # Test scale modification
        new_scales = rng.uniform(0.5, 3.0, size=(total_count, 3))

        # Apply modifications
        modify.pose(
            prims_to_modify,
            position_value=new_positions,
            rotation_value=new_rotations,
            scale_value=new_scales,
        )

        # Verify prim modifications
        for i, prim in enumerate(prims_to_modify):
            if prim.GetTypeName() == "PointInstancer":
                self.verify_point_instancer_instances(prim, new_positions[i:], new_rotations[i:], new_scales[i:])
            else:
                self.verify_prim_modifications(prim, new_positions[i], new_rotations[i], new_scales[i])

    async def test_modify_semantics(self):
        """Test modifying semantics."""
        cones = F.create_batch.cone(count=10)

        # Apply a non-semantic schema. This schema should not be affected by the semantics API
        F.physics.apply_rigid_body(cones)

        for cone in cones:
            rep_utils._set_semantics_legacy(cone, [("class", "legacy")])

        per_object_semantics = [{"class": ["sphere", "ball"], "material": f"rubber{i}"} for i in range(len(cones))]

        # Apply with a list, multiple objects
        F.modify.semantics(cones, per_object_semantics)

        per_object_gt = [
            {k: [v] if isinstance(v, str) else v for k, v in per_object_semantics[i].items()} for i in range(len(cones))
        ]

        # Add legacy semantics
        for d in per_object_gt:
            d["class"] = ["legacy", *d["class"]]

        # Verify that the semantics are applied to the cones
        for i, cone in enumerate(cones):
            semantics = rep_utils.legacy_semantics_arg_to_new(rep_utils.parse_semantics(cone))
            self.assertEqual(per_object_gt[i], semantics)

        # Apply more semantics
        per_object_semantics2 = {"class": "3d sphere", "material": ["vulcanized rubber"]}
        F.modify.semantics(cones, per_object_semantics2)

        # Verify that the semantics are applied to the cones
        for i, cone in enumerate(cones):
            semantics = rep_utils.legacy_semantics_arg_to_new(rep_utils.parse_semantics(cone))
            for k, v in per_object_semantics2.items():
                if isinstance(v, str):
                    v = [v]
                per_object_gt[i][k] = per_object_gt[i].get(k, []) + v
            self.assertEqual(per_object_gt[i], semantics)

        # Test replace semantics
        per_object_semantics3 = {"class": ["ceci n'est pas une balle"]}
        F.modify.semantics(cones, per_object_semantics3, mode="replace")

        # Verify that the semantics are applied to the cones
        for i, cone in enumerate(cones):
            per_object_gt[i].update(per_object_semantics3)
            semantics = rep_utils.legacy_semantics_arg_to_new(rep_utils.parse_semantics(cone))
            self.assertEqual(per_object_gt[i], semantics)

        # Test clear semantics
        per_object_semantics4 = {"action": ["rolling"]}
        F.modify.semantics(cones, per_object_semantics4, mode="clear")

        # Verify that the semantics are applied to the cones
        for i, cone in enumerate(cones):
            semantics = rep_utils.legacy_semantics_arg_to_new(rep_utils.parse_semantics(cone))
            self.assertEqual(per_object_semantics4, semantics)

        # Test full clear
        F.modify.semantics(cones, mode="clear")

        # Verify that the semantics are applied to the cones
        for i, cone in enumerate(cones):
            semantics = rep_utils.legacy_semantics_arg_to_new(rep_utils.parse_semantics(cone))
            self.assertEqual({}, semantics)

        # Verify that semantics work on a separate layer
        # Create an anonymous layer and set it as the current edit target
        stage = omni.usd.get_context().get_stage()
        anon_layer = pxr.Sdf.Layer.CreateAnonymous()
        stage.GetRootLayer().subLayerPaths.append(anon_layer.identifier)
        stage.SetEditTarget(anon_layer)

        # Add semantic to prim in new layer
        F.modify.semantics(cones, mode="clear", value={"layerSemantics": "layerSemantics"})

        # Verify that the semantics are applied to the cones in that layer
        # Check that the semantics are applied only in the anonymous layer
        layer_schema_name = "SemanticsLabelsAPI:layerSemantics"
        for cone in cones:
            # Get the prim in the context of the anonymous layer
            prim_in_anon = anon_layer.GetPrimAtPath(cone.GetPath())
            print(
                prim_in_anon.GetInfo("apiSchemas").explicitItems,
                prim_in_anon.GetInfo("apiSchemas").appendedItems,
                prim_in_anon.GetInfo("apiSchemas").prependedItems,
            )
            self.assertEqual(prim_in_anon.GetInfo("apiSchemas").appendedItems, [layer_schema_name])

            # Switch back to the root layer and check that semantics are not present there
            prim_in_root = stage.GetRootLayer().GetPrimAtPath(cone.GetPath())
            self.assertFalse(layer_schema_name in prim_in_root.GetInfo("apiSchemas").explicitItems)

        # Verify that the non-semantic schema is not affected
        for cone in cones:
            prim_in_root = stage.GetRootLayer().GetPrimAtPath(cone.GetPath())
            prepended_schemas = prim_in_root.GetInfo("apiSchemas").prependedItems
            self.assertTrue(
                "PhysxRigidBodyAPI" in prepended_schemas, f"PhysxRigidBodyAPI should be present in {cone.GetPath()}"
            )

    async def test_modify_semantics_supported_formats(self):
        def get_semantics(prim):
            return rep_utils.legacy_semantics_arg_to_new(rep_utils.parse_semantics(prim))

        # Test legacy format
        cube = F.create.cube()
        F.modify.semantics(prims=cube, value=[("class", "cube")])
        self.assertEqual(get_semantics(cube), {"class": ["cube"]})

        # Test legacy format with list of tuples
        cube = F.create.cube()
        F.modify.semantics(prims=cube, value=[("class", "cube"), ("class", "cube2")])
        self.assertEqual(get_semantics(cube), {"class": ["cube", "cube2"]})

        # Test legacy format with list of tuples when using 2 prims
        cubes = F.create_batch.cube(count=2)
        F.modify.semantics(prims=cubes, value=[("class", "cube"), ("class", "cube2")])
        for prim in cubes:
            self.assertEqual(get_semantics(prim), {"class": ["cube", "cube2"]})

        # Test legacy format with list of tuples when using 2 prims and two different semantics
        cubes = F.create_batch.cube(count=2)
        F.modify.semantics(
            prims=cubes, value=[[("class", "cube"), ("class", "cube2")], [("class", "cube3"), ("class", "cube4")]]
        )
        self.assertEqual(get_semantics(cubes[0]), {"class": ["cube", "cube2"]})
        self.assertEqual(get_semantics(cubes[1]), {"class": ["cube3", "cube4"]})

        # Test new format
        cube = F.create.cube()
        F.modify.semantics(prims=cube, value={"class": "cube"})

        # Test new format with list of tuples
        cube = F.create.cube()
        F.modify.semantics(prims=cube, value=[{"class": ["cube", "cube2"]}])

        # Test new format with list of tuples when using 2 prims
        cubes = F.create_batch.cube(count=2)
        F.modify.semantics(prims=cubes, value=[{"class": ["cube", "cube2"]}])
        for prim in cubes:
            self.assertEqual(get_semantics(prim), {"class": ["cube", "cube2"]})

        # Test new format with list of tuples when using 2 prims and two different semantics
        cubes = F.create_batch.cube(count=2)
        F.modify.semantics(prims=cubes, value=[{"class": ["cube", "cube2"]}, {"class": ["cube3", "cube4"]}])
        self.assertEqual(get_semantics(cubes[0]), {"class": ["cube", "cube2"]})
        self.assertEqual(get_semantics(cubes[1]), {"class": ["cube3", "cube4"]})
