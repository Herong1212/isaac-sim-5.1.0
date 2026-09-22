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

import carb
import numpy as np
import omni.kit.test
import omni.replicator.core.functional as F
import omni.usd
import pxr
import usdrt
from omni.replicator.core.scripts.functional import utils as f_utils
from PIL import Image


class TestCreate(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        self._cached_use_fabric_scene_delegate = carb.settings.get_settings().get("/app/useFabricSceneDelegate")

    async def tearDown(self):
        # delete files from temp directory
        temp_dir = carb.tokens.get_tokens_interface().resolve("${temp}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        carb.settings.get_settings().set("/app/useFabricSceneDelegate", self._cached_use_fabric_scene_delegate)

    def create_test_dome_texture(self):
        """Creates a test dome texture and returns the path."""
        # Create dummy texture
        temp_dir = carb.tokens.get_tokens_interface().resolve("${temp}")
        os.makedirs(temp_dir, exist_ok=True)
        texture_path = os.path.join(temp_dir, "test_diffuse_texture.png")
        if not os.path.exists(texture_path):
            # Create a simple test texture (checkerboard pattern)
            texture = np.zeros((256, 256, 3), dtype=np.uint8)
            checker_size = 16  # Size of each checker square

            # Create checkerboard pattern using numpy operations
            x, y = np.indices((256, 256))
            checker_pattern = ((x // checker_size) + (y // checker_size)) % 2

            # Apply colors based on pattern (reshape for broadcasting)
            col1 = np.array([156, 255, 195], dtype=np.uint8)
            col2 = np.array([240, 128, 128], dtype=np.uint8)
            texture[checker_pattern == 0] = col1
            texture[checker_pattern == 1] = col2
            Image.fromarray(texture).save(texture_path)
        return texture_path

    def test_docstrings_functional_create(self):
        """Test module docstring examples"""
        failures, test_counts = doctest.testmod(F.create)
        if failures:
            self.fail(f"Encountered {failures} failures in {test_counts} tests.")

    def create_test_transform_params(self):
        """Creates standard transform test parameters.

        Returns:
            dict: Dictionary containing standard transform test parameters.
        """
        return {
            "basic": {
                "position": (1, 2, 3),
                "rotation": (0, 90, 0),
                "scale": (2, 2, 2),
            },
            "pivot": {
                "position": (1, 2, 3),
                "rotation": (0, 90, 0),
                "pivot": (0.5, 0.5, 0.5),
            },
            "relative": {
                "position": (5, 15, -25),
                "rotation": (0, 0, -90),
            },
            "combined": {
                "position": (15, -5, 25),
                "rotation": (0, 0, 90),
                "pivot": (0.5, 0, 0),
                "expected_position": (0, 0, 0),  # Hard coded, relative and prim position cancel out
                "expected_pivot_position": (
                    25,
                    0,
                    0,
                ),  # Relative & prim position cancel out minus pivot with prim size (100, 100, 100)
                "expected_rotation": (0, 0, 0),  # Hard coded, relative and prim rotation cancel out
            },
        }

    def verify_transform_configurations(self, create_func, prim_type_name=None, test_pivot=True):
        """Tests standard transform configurations for a creation function.

        Args:
            create_func: Function to create the prim (e.g., F.create_batch.xform)
            prim_type_name (str, optional): Expected prim type name to verify
            test_pivot (bool, optional): Whether to test pivot point
        Returns:
            tuple: (basic_prim, pivot_prim, relative_prim, combined_prim)
        """
        params = self.create_test_transform_params()

        # Test basic transform
        basic_params = params["basic"]
        basic_prims = create_func(
            position=basic_params["position"],
            rotation=basic_params["rotation"],
            scale=basic_params["scale"],
            name=f"test_{create_func.__name__.split('.')[-1]}",
        )
        self.assertEqual(len(basic_prims), 1)
        basic_prim = basic_prims[0]
        self.assertTrue(basic_prim.IsValid())
        if prim_type_name:
            self.assertEqual(basic_prim.GetTypeName(), prim_type_name)
        self.verify_transform(
            basic_prim,
            expected_position=basic_params["position"],
            expected_rotation=basic_params["rotation"],
            expected_scale=basic_params["scale"],
        )

        if test_pivot:
            # Test pivot point
            pivot_params = params["pivot"]
            pivot_prim = create_func(
                position=pivot_params["position"],
                rotation=pivot_params["rotation"],
                pivot=pivot_params["pivot"],
                name=f"pivot_{create_func.__name__.split('.')[-1]}",
            )[0]
            bbox = pxr.UsdGeom.Boundable(pivot_prim).ComputeWorldBound(
                pxr.Usd.TimeCode.Default(), purpose1=pxr.UsdGeom.Tokens.default_
            )
            bbox_size = bbox.GetRange().GetSize()
            pivot_coords = bbox_size * 0.25
            translation = pxr.Gf.Vec3f(pivot_params["position"])
            pivot_coords[2] = -pivot_coords[2]  # Due to 90 degree rotation about Z axis
            expected_position = translation - pxr.Gf.Vec3f(pivot_coords)

            self.verify_transform(
                pivot_prim,
                expected_position=expected_position,
                expected_rotation=pivot_params["rotation"],
                message=f"test_pivot: {prim_type_name}",
            )

        # Test relative_to transform
        combined_params = params["combined"]
        relative_params = params["relative"]
        reference_xform = F.create_batch.xform(
            position=relative_params["position"], rotation=relative_params["rotation"], name="reference_xform"
        )[0]

        relative_prim = create_func(
            position=combined_params["position"],
            rotation=combined_params["rotation"],
            relative_to=reference_xform,
            name=f"relative_{create_func.__name__.split('.')[-1]}",
        )[0]

        # Verify prim was created
        self.assertTrue(relative_prim.IsValid())

        # Check final transform
        self.verify_transform(
            relative_prim,
            expected_position=combined_params["expected_position"],
            expected_rotation=combined_params["expected_rotation"],
            rtol=1e-3,
            atol=1e-3,
            message=f"test_relative_to: {prim_type_name}",
        )

        # Test combination of pivot and relative_to
        if test_pivot:
            combined_prim = create_func(
                position=combined_params["position"],
                rotation=combined_params["rotation"],
                pivot=combined_params["pivot"],
                relative_to=reference_xform,
                name=f"combined_{create_func.__name__.split('.')[-1]}",
            )[0]

            # Verify final transform
            expected_position = (-bbox_size[0] * 0.25, 0, 0)
            self.verify_transform(
                combined_prim,
                expected_position=expected_position,
                expected_rotation=combined_params["expected_rotation"],
                rtol=1e-3,
                atol=1e-3,
                message=f"test_combined_pivot: {prim_type_name}",
            )

    async def test_create_reference_with_transforms(self):
        """Tests reference creation with source assets having different transforms.

        Verifies that creating a reference from source assets with various existing
        transforms results in the expected final transform in the target prim. Tests
        all permutations of rotation types (rotate, orientation, quaternion) and
        rotation axes, along with translation and scale.
        """
        stage = omni.usd.get_context().get_stage()

        def create_test_cases():
            """Creates test cases for different transform combinations."""
            # Define target and source transform values
            translation_target = (1, 2, 3)
            scale_target = (2, 2, 2)
            rotation_xyz_target = (10, 20, 30)
            translation_source = (6, 5, 4)
            scale_source = (0.1, 0.2, 0.3)
            rotation_xyz_source = (1, 2, 3)

            # Define rotation values for each axis
            rotations = {
                "x": (45, 0, 0),
                "y": (0, 45, 0),
                "z": (0, 0, 45),
                "xy": (45, 45, 0),
                "xz": (45, 0, 45),
                "yz": (0, 45, 45),
                "xyz": (45, 45, 45),
            }

            # Define orientations (axis-angle) for each axis
            orientations = {
                "x": (1, 0, 0, 0.785),  # 45° around X
                "y": (0, 1, 0, 0.785),  # 45° around Y
                "z": (0, 0, 1, 0.785),  # 45° around Z
                "xy": (0.707, 0.707, 0, 0.785),  # 45° around X+Y
                "xz": (0.707, 0, 0.707, 0.785),  # 45° around X+Z
                "yz": (0, 0.707, 0.707, 0.785),  # 45° around Y+Z
                "xyz": (0.577, 0.577, 0.577, 0.785),  # 45° around X+Y+Z
            }

            # Base test cases
            test_cases = [
                ("source1", None),
                ("source2", {"translate": translation_source}),
                ("source3", {"scale": scale_source}),
            ]

            # Add rotation test cases
            for axis, rot in rotations.items():
                test_cases.extend(
                    [
                        (f"source_rotate_{axis}", {"rotate": rot}),
                        (f"source_rotate_{axis}_trans", {"rotate": rot, "translate": translation_source}),
                        (f"source_rotate_{axis}_scale", {"rotate": rot, "scale": scale_source}),
                        (
                            f"source_rotate_{axis}_full",
                            {"rotate": rot, "translate": translation_source, "scale": scale_source},
                        ),
                    ]
                )

            # Add orientation test cases
            for axis, orient in orientations.items():
                test_cases.extend(
                    [
                        (f"source_orient_{axis}", {"orientation": orient}),
                        (f"source_orient_{axis}_trans", {"orientation": orient, "translate": translation_source}),
                        (f"source_orient_{axis}_scale", {"orientation": orient, "scale": scale_source}),
                        (
                            f"source_orient_{axis}_full",
                            {"orientation": orient, "translate": translation_source, "scale": scale_source},
                        ),
                    ]
                )

            # Add transform test case
            transform = pxr.Gf.Transform()
            transform.SetTranslation(pxr.Gf.Vec3d(*translation_source))
            transform.SetRotation(
                pxr.Gf.Rotation(pxr.Gf.Vec3d(1, 0, 0), rotation_xyz_source[0])
                * pxr.Gf.Rotation(pxr.Gf.Vec3d(0, 1, 0), rotation_xyz_source[1])
                * pxr.Gf.Rotation(pxr.Gf.Vec3d(0, 0, 1), rotation_xyz_source[2])
            )
            transform.SetScale(pxr.Gf.Vec3d(*scale_source))
            test_cases.extend(
                [
                    ("source_transform", {"transform": transform}),
                ]
            )

            return test_cases, translation_target, scale_target, rotation_xyz_target

        def create_source_prim(source_name, source_transform):
            """Creates a source prim with specified transform."""
            source = F.create.xform(name=source_name)
            if source_transform:
                xformable = pxr.UsdGeom.Xformable(source)
                if "translate" in source_transform:
                    xformable.AddTranslateOp().Set(source_transform["translate"])
                if "rotate" in source_transform:
                    xformable.AddRotateXYZOp().Set(source_transform["rotate"])
                if "orientation" in source_transform:
                    xformable.AddOrientOp().Set(pxr.Gf.Quatf(*source_transform["orientation"]))
                if "scale" in source_transform:
                    xformable.AddScaleOp().Set(source_transform["scale"])
                if "transform" in source_transform:
                    xformable.AddTransformOp().Set(source_transform["transform"].GetMatrix())
            return source

        # Get test cases and target transform values
        test_cases, translation_target, scale_target, rotation_xyz_target = create_test_cases()

        # Run tests for each case
        for source_name, source_transform in test_cases:
            # Create source prim with specified transform
            source_prim = create_source_prim(source_name, source_transform)

            # Create target prim and reference
            target_name = f"{source_name}_ref"
            ref = F.create.reference(
                prim_path=source_prim.GetPath(),
                name=target_name,
                position=translation_target,
                scale=scale_target,
                rotation=rotation_xyz_target,
            )

            # Verify the reference was created
            pxr_stage = omni.usd.get_context().get_stage()
            pxr_ref = pxr_stage.GetPrimAtPath(str(ref.GetPrimPath()))
            self.assertTrue(pxr_ref.HasAuthoredReferences())

            # Verify transform components
            self.verify_transform(
                pxr_ref,
                expected_position=translation_target,
                expected_rotation=rotation_xyz_target,
                expected_scale=scale_target,
                message=f"test_create_reference_with_transforms: {source_name}",
            )

    async def test_create_material(self):
        """Tests material creation using both PXR and USDRT paths.

        Verifies that creating materials works correctly with both APIs by:
        1. Creating a sphere to bind the material to
        2. Creating a material with various parameters
        3. Verifying the material is created and bound correctly
        4. Testing both PXR and USDRT code paths
        """
        texture_path = self.create_test_dome_texture()

        # Test both PXR and USDRT paths
        for is_fsd in [False, True]:
            carb.settings.get_settings().set("/app/useFabricSceneDelegate", is_fsd)
            await omni.usd.get_context().new_stage_async()

            # Create a sphere to bind the material to
            sphere = F.create.sphere(position=(0, 0, 0))
            self.assertTrue(sphere)

            # Test OmniPBR.mdl
            omni_pbr_values = {
                "diffuse_color_constant": (0.1, 0.2, 0.3),
                "diffuse_texture": texture_path,
                "albedo_desaturation": 0.5,
                "albedo_add": 0.1,
                "albedo_brightness": 0.9,
                "diffuse_tint": (1, 0.5, 0.2),
                "reflection_roughness_constant": 0.2,
                "reflection_roughness_texture_influence": 0.5,
                "reflectionroughness_texture": texture_path,
                "metallic_constant": 0.8,
                "metallic_texture_influence": 0.5,
                "metallic_texture": texture_path,
                "specular_level": 0.2,
                "enable_ORM_texture": True,
                "ORM_texture": texture_path,
                "ao_to_diffuse": 0.5,
                "ao_texture": texture_path,
                "enable_emission": True,
                "emissive_color": (0, 1, 0),
                "emissive_color_texture": texture_path,
                "emissive_mask_texture": texture_path,
                "emissive_intensity": 1.0,
                "enable_opacity": True,
                "opacity_texture": texture_path,
                "opacity_constant": 0.5,
                "enable_opacity_texture": True,
                "opacity_mode": 1,
                "opacity_threshold": 0.5,
                "geometry_normal_roughness_strength": 0.5,
                "bump_factor": 0.5,
                "normalmap_texture": texture_path,
                "detail_bump_factor": 0.5,
                "detail_normalmap_texture": texture_path,
                "flip_tangent_u": True,
                "flip_tangent_v": True,
                "project_uvw": True,
                "world_or_object": True,
                "uv_space_index": 1,
                "texture_translate": (0.2, 0.5),
                "texture_rotate": 21,
                "texture_scale": (0.1, 0.1),
                "detail_texture_translate": (0.2, 0.5),
                "detail_texture_rotate": 20,
                "detail_texture_scale": (0.1, 0.1),
                "round_edges_radius": 0.5,
                "round_edges_roundness": 0.5,
                "round_edges_across_materials": True,
            }

            # Create a material with variants
            material = F.create.material(
                mdl="OmniPBR.mdl", bind_prims=sphere, name="test_material_variants", **omni_pbr_values
            )

            # Verify material was created
            self.assertTrue(material)

            # Verify material parameters were set correctly
            shader = pxr.UsdShade.Shader(f_utils.get_shader_from_material(material, True))
            for param_name, expected_value in omni_pbr_values.items():
                shader_input = shader.GetInput(param_name)
                self.assertTrue(shader_input)
                set_value = shader_input.Get()
                msg = f"Parameter '{param_name}' mismatch: expected '{expected_value}', got '{set_value}'"
                if isinstance(set_value, pxr.Sdf.AssetPath):
                    self.assertEqual(set_value.path, expected_value, msg=msg)
                else:
                    self.assertAlmostEqual(set_value, expected_value, places=2, msg=msg)

    async def test_create_primitives(self):
        """Tests creation of basic primitive shapes."""
        primitive_types = {
            "cube": F.create_batch.cube,
            "sphere": F.create_batch.sphere,
            "cylinder": F.create_batch.cylinder,
            "cone": F.create_batch.cone,
            "plane": F.create_batch.plane,
        }

        material = F.create.material(mdl="OmniPBR.mdl", name="test_material", diffuse_color_constant=(1, 0, 0))

        for prim_type, prim_func in primitive_types.items():
            # Test standard transform configurations
            self.verify_transform_configurations(prim_func, "Mesh")

            # Test multiple primitives with different positions
            positions = [(x, 0, 0) for x in range(3)]
            multi_prims = prim_func(count=3, position=positions, scale=1.5, material=material)
            self.assertEqual(len(multi_prims), 3)
            for prim, pos in zip(multi_prims, positions):
                self.assertTrue(prim.IsValid())
                self.verify_transform(prim, expected_position=pos, expected_scale=(1.5, 1.5, 1.5))

    async def test_create_reference(self):
        """Tests creation of references with various configurations.

        Tests the following functionality:
        1. Basic reference creation with position, rotation, and scale
        2. Multiple references with different transforms
        3. References with pivot points
        4. References with relative_to transforms
        5. Combination of pivot and relative_to transforms
        """
        # Create source prim
        source = F.create_batch.sphere(name="source")[0]
        source_path = source.GetPath()

        # Define a custom reference creation function that uses the source path
        def create_reference(**kwargs):
            return F.create_batch.reference(prim_path=source_path, **kwargs)

        # Test standard transform configurations
        self.verify_transform_configurations(create_reference)

        # Test multiple references with different transforms
        positions = [(x, 0, 0) for x in range(3)]
        rotations = [(0, y, 0) for y in range(3)]
        multi_refs = F.create_batch.reference(prim_path=source_path, count=3, position=positions, rotation=rotations)
        self.assertEqual(len(multi_refs), 3)
        for ref, pos, rot in zip(multi_refs, positions, rotations):
            self.assertTrue(ref.IsValid())
            self.assertTrue(ref.HasAuthoredReferences())
            self.verify_transform(ref, expected_position=pos, expected_rotation=rot)

    async def test_create_xform(self):
        """Tests creation of xforms"""
        # Test standard transform configurations
        self.verify_transform_configurations(F.create_batch.xform, "Xform", test_pivot=False)

        # Test parent-child relationship
        parent = F.create_batch.xform(name="parent")[0]
        children = F.create_batch.xform(count=3, parent=parent, name="child")
        self.assertEqual(len(children), 3)
        for i, child in enumerate(children):
            self.assertTrue(child.IsValid())
            self.assertEqual(child.GetParent(), parent)
            expected_name = f"child_0{i}" if i > 0 else "child"
            self.assertEqual(child.GetName(), expected_name)

        # Test look_at functionality
        target_pos = (0, 10, 10)
        target = F.create_batch.xform(position=target_pos, name="look_at_target")[0]
        F.create.sphere(parent=target, scale=(0.01))
        look_at_xform = F.create_batch.xform(position=(0, 0, 0), look_at=target.GetPath(), name="looking")[0]
        F.create.camera(parent=look_at_xform)
        self.assertTrue(look_at_xform.IsValid())

        # Verify the xform is oriented towards the target
        xform = pxr.UsdGeom.Xformable(look_at_xform)
        matrix = xform.ComputeLocalToWorldTransform(0.0)
        forward_vector = pxr.Gf.Vec3d(0, 0, 1)
        forward = pxr.Gf.Transform(matrix).GetRotation().TransformDir(forward_vector)
        target_dir = -pxr.Gf.Vec3d(*target_pos).GetNormalized()
        np.testing.assert_allclose(forward, target_dir, atol=1e-6)

    async def test_create_camera(self):
        """Tests camera creation with various parameters."""

        def verify_camera_params(camera, focal_length=None, focus_distance=None, f_stop=None):
            """Helper to verify camera-specific parameters."""
            mod = usdrt if f_utils.get_is_fsd_enabled() else pxr
            camera_schema = mod.UsdGeom.Camera(camera)
            if focal_length is not None:
                self.assertEqual(camera_schema.GetFocalLengthAttr().Get(), focal_length)
            if focus_distance is not None:
                self.assertEqual(camera_schema.GetFocusDistanceAttr().Get(), focus_distance)
            if f_stop is not None:
                self.assertAlmostEqual(camera_schema.GetFStopAttr().Get(), f_stop, places=2)

        # Test basic camera creation with camera-specific parameters
        cameras = F.create_batch.camera(
            position=(1, 2, 3), rotation=(0, 90, 0), focal_length=50, focus_distance=100, f_stop=2.8, name="test_camera"
        )
        self.assertEqual(len(cameras), 1)
        camera = cameras[0]
        self.assertTrue(camera.IsValid())
        self.assertEqual(camera.GetTypeName(), "Camera")

        # Verify camera parameters
        verify_camera_params(camera, 50, 100, 2.8)

        # Test standard transform configurations
        self.verify_transform_configurations(F.create_batch.camera, "Camera", test_pivot=False)

        # Test multiple cameras with different positions and parameters
        positions = [(x, 2, 0) for x in range(3)]
        focal_lengths = [35, 50, 85]
        multi_cameras = F.create_batch.camera(count=3, position=positions, focal_length=focal_lengths)
        self.assertEqual(len(multi_cameras), 3)
        for camera, pos, focal in zip(multi_cameras, positions, focal_lengths):
            self.assertTrue(camera.IsValid())
            self.verify_transform(camera, expected_position=pos)
            verify_camera_params(camera, focal, None, None)

    async def test_create_light(self):
        """Tests creation of different light types with various parameters.

        Tests the following functionality:
        1. Basic light creation with position, rotation, and intensity
        2. Different light types (point, spot, distant)
        3. Light-specific parameters (color, intensity, angle)
        4. Multiple lights with different parameters
        """
        # Create a texture for the dome light
        texture_path = self.create_test_dome_texture()

        light_types = {
            "distant": F.create.distant_light,
            "cylinder": F.create.cylinder_light,
            "sphere": F.create.sphere_light,
            "rect": F.create.rect_light,
            "dome": F.create.dome_light,
            "disk": F.create.disk_light,
        }

        # Additional light parameters
        additional_params = {
            "common": {
                "intensity": 100,
                "color": (0.1, 0.2, 0.7),
                "exposure": 0.7,
                "color_temperature": 5000,
                "enable_color_temperature": True,
                "diffuse": 0.6,
                "specular": 0.4,
            },
            "shaping": {
                "shaping_cone_angle": 120.0,
                "shaping_cone_softness": 0.5,
                "shaping_focus_tint": (0.2, 0.2, 0.2),
            },
            "distant": {
                "angle": 30,
            },
            "rect": {
                "width": 100,
                "height": 100,
            },
            "cylinder": {
                "radius": 100,
                "length": 100,
            },
            "sphere": {
                "radius": 100,
            },
            "disk": {
                "radius": 100,
            },
            "dome": {
                "texture": texture_path,
            },
        }

        usd_name_map = {
            "color_temperature": "colorTemperature",
            "enable_color_temperature": "enableColorTemperature",
            "shaping_cone_angle": "shaping:cone:angle",
            "shaping_cone_softness": "shaping:cone:softness",
            "shaping_focus_tint": "shaping:focusTint",
            "texture": "texture:file",
        }

        mod = usdrt if f_utils.get_is_fsd_enabled() else pxr

        for light_type, light_func in light_types.items():
            # Test point light
            light = light_func(
                position=(1, 2, 3),
                name=light_type,
                **additional_params[light_type],
                **additional_params["common"],
                **(additional_params["shaping"] if light_type != "dome" else {}),
            )
            self.assertTrue(light.IsValid())
            self.assertEqual(light.GetTypeName(), f"{light_type.capitalize()}Light")
            self.verify_transform(light, expected_position=(1, 2, 3))

            # Verify additional parameters
            for param, value in (additional_params[light_type] | additional_params["common"]).items():
                param = f"inputs:{usd_name_map.get(param, param)}"
                msg = f"Parameter '{param}' mismatch: expected '{value}', got '{light.GetAttribute(param).Get()}' for light type '{light_type}'"
                set_value = light.GetAttribute(param).Get()
                if isinstance(set_value, mod.Sdf.AssetPath):
                    self.assertEqual(set_value.path, value, msg=msg)
                else:
                    self.assertAlmostEqual(set_value, value, places=2, msg=msg)

    def verify_transform(
        self,
        prim,
        expected_position=None,
        expected_rotation=None,
        expected_scale=None,
        rtol=1e-3,
        atol=1e-3,
        message: str = None,
    ):
        """Verifies the transform components of a prim.

        Args:
            prim: The USD prim to verify
            expected_position (tuple, optional): Expected (x, y, z) position
            expected_rotation (tuple, optional): Expected (x, y, z) rotation in degrees
            expected_scale (tuple, optional): Expected (x, y, z) scale
            rtol (float): Relative tolerance for numpy.allclose
            atol (float): Absolute tolerance for numpy.allclose
            message (str, optional): Additional message to include in assertion errors
        """
        mod = usdrt if f_utils.get_is_fsd_enabled() else pxr
        if f_utils.get_is_fsd_enabled():
            stage = prim.GetStage()
            stage_id = stage.GetStageIdAsStageId()
            fabric_id = stage.GetFabricId()
            prim_path = prim.GetPrimPath()

            hier = usdrt.hierarchy.IFabricHierarchy().get_fabric_hierarchy(fabric_id, stage_id)
            transform = usdrt.Gf.Transform(hier.get_local_xform(prim_path))
        else:
            xform = pxr.UsdGeom.Xformable(prim)
            matrix = xform.ComputeLocalToWorldTransform(pxr.Usd.TimeCode.Default())
            transform = pxr.Gf.Transform(matrix)

        if expected_position is not None:
            translation = transform.GetTranslation()
            self.assertTrue(
                np.allclose(translation, expected_position, rtol=rtol, atol=atol),
                f"Position mismatch: expected {expected_position}, got {translation}"
                + (f" - {message}" if message else ""),
            )

        if expected_rotation is not None:
            angles = transform.GetRotation().Decompose(mod.Gf.Vec3d.ZAxis(), mod.Gf.Vec3d.YAxis(), mod.Gf.Vec3d.XAxis())
            rotation = mod.Gf.Vec3d(angles[2], angles[1], angles[0])
            self.assertTrue(
                np.allclose(rotation, expected_rotation, rtol=rtol, atol=atol),
                f"Rotation mismatch: expected {expected_rotation}, got {rotation}"
                + (f" - {message}" if message else ""),
            )

        if expected_scale is not None:
            scale = transform.GetScale()
            self.assertTrue(
                np.allclose(scale, expected_scale, rtol=rtol, atol=atol),
                f"Scale mismatch: expected {expected_scale}, got {scale}" + (f" - {message}" if message else ""),
            )
