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
import subprocess
import sys
import unittest
from pathlib import Path

import carb.settings
import numpy as np
import omni.kit
import omni.kit.test
import omni.replicator.core as rep
import omni.usd
import omni.usd.schema.omni_sensors
from omni.replicator.core.utils.mdl_graph_gen import MaterialGraphGenerator, MaterialGraphGeneratorError
from omni.replicator.core.utils.viewport_manager import LEGACY_RP_PREFIX, RP_PREFIX_SETTING
from PIL import Image
from pxr import Sdf, UsdGeom, UsdSemantics, UsdShade

TEST_DATA_DIR = Path(os.path.dirname(os.path.realpath(__file__))).joinpath("data")


def save_image(data, path):
    Image.fromarray(data).save(path)


def tc_show_image(name, golden_file_path, out_dir, image):
    result_path = os.path.join(out_dir, f"{name}_result.png")
    save_image(image.numpy(), result_path)
    print(f"##teamcity[publishArtifacts '{golden_file_path} => golden']\n")
    print(f"##teamcity[publishArtifacts '{result_path} => results']\n")
    print(f"##teamcity[testMetadata type='image' name='{name} Reference' value='golden/{name}.png']\n")
    print(f"##teamcity[testMetadata type='image' name='{name} Generated' value='results/{name}_result.png']\n")


def _get_used_gpu_memory():
    """Return used GPU memory in MB"""
    mem_used = 0

    command = "nvidia-smi"
    arg_query = "--query-gpu=memory.used"
    arg_format = "--format=csv,noheader,nounits"

    try:
        p = subprocess.Popen([command, arg_query, arg_format], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = p.communicate()
        mem_used = sum([int(m) for m in output.decode("ascii").split("\n") if m])
    except (OSError, ValueError, FileNotFoundError) as e:
        print("Error trying to run nvidia-smi")
        print(e)

    return mem_used


class TestCreate(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        if os.getenv("ETM_ACTIVE") and sys.platform.startswith("win"):
            self.skipTest("skip in ETM, windows tests take longer")

        await omni.usd.get_context().new_stage_async()
        await omni.kit.app.get_app().next_update_async()
        rep.set_global_seed(1)

    async def tearDown(self):
        carb.settings.get_settings().set("/omni/replicator/RTSubframes", 1)
        await omni.usd.get_context().new_stage_async()

    async def test_docstrings(self):
        """Test module docstring examples"""
        failures, test_counts = doctest.testmod(rep.create)
        if failures:
            self.fail(f"Encountered {failures} failures in {test_counts} tests.")

    async def test_create_camera(self):
        rep.create.camera(
            None,
            None,
            None,
            focal_length=35.0,
            focus_distance=200.0,
            f_stop=1.0,
            horizontal_aperture=30,
            horizontal_aperture_offset=1.0,
            vertical_aperture_offset=2.0,
            clipping_range=(2.0, 3.0),
            projection_type="fisheyePolynomial",
            fisheye_nominal_width=1800,
            fisheye_nominal_height=1000,
            fisheye_optical_centre_x=900,
            fisheye_optical_centre_y=500,
            fisheye_max_fov=300.0,
            fisheye_polynomial_a=1.0,
            fisheye_polynomial_b=2.0,
            fisheye_polynomial_c=3.0,
            fisheye_polynomial_d=4.0,
            fisheye_polynomial_e=5.0,
            fisheye_polynomial_f=6.0,
        )

        stage = omni.usd.get_context().get_stage()
        cam_xform = stage.GetPrimAtPath("/Replicator/Camera_Xform")
        cam = cam_xform.GetChild("Camera")

        self.assertTrue(cam.GetAttribute("focalLength").Get(), 35.0)
        self.assertTrue(cam.GetAttribute("focusDistance").Get(), 200.0)
        self.assertTrue(cam.GetAttribute("fStop").Get(), 1.0)
        self.assertTrue(cam.GetAttribute("horizontalAperture").Get(), 30)
        self.assertTrue(cam.GetAttribute("horizontalApertureOffset").Get(), 1.0)
        self.assertTrue(cam.GetAttribute("verticalApertureOffset").Get(), 2.0)
        self.assertTrue(cam.GetAttribute("clippingRange").Get(), (2.0, 3.0))
        self.assertTrue(cam.GetAttribute("cameraProjectionType").Get(), "fisheyePolynomial")
        self.assertTrue(cam.GetAttribute("fthetaWidth").Get(), 1800)
        self.assertTrue(cam.GetAttribute("fthetaHeight").Get(), 1000)
        self.assertTrue(cam.GetAttribute("fthetaCx").Get(), 900)
        self.assertTrue(cam.GetAttribute("fthetaCy").Get(), 500)
        self.assertTrue(cam.GetAttribute("fthetaMaxFov").Get(), 300.0)
        self.assertTrue(cam.GetAttribute("fthetaPolyA").Get(), 1.0)
        self.assertTrue(cam.GetAttribute("fthetaPolyB").Get(), 2.0)
        self.assertTrue(cam.GetAttribute("fthetaPolyC").Get(), 3.0)
        self.assertTrue(cam.GetAttribute("fthetaPolyD").Get(), 4.0)
        self.assertTrue(cam.GetAttribute("fthetaPolyE").Get(), 5.0)
        self.assertTrue(cam.GetAttribute("fthetaPolyF").Get(), 6.0)

    async def test_create_camera_kannala(self):
        rep.create.camera(
            None,
            None,
            None,
            focal_length=35.0,
            focus_distance=200.0,
            f_stop=1.0,
            horizontal_aperture=30,
            horizontal_aperture_offset=1.0,
            vertical_aperture_offset=2.0,
            clipping_range=(2.0, 3.0),
            projection_type="fisheyeKannalaBrandtK3",
            fisheye_nominal_width=1800,
            fisheye_nominal_height=1000,
            fisheye_optical_centre_x=900,
            fisheye_optical_centre_y=500,
            fisheye_max_fov=300.0,
            fisheye_polynomial_a=1.0,
            fisheye_polynomial_b=2.0,
            fisheye_polynomial_c=3.0,
            fisheye_polynomial_d=4.0,
            fisheye_polynomial_e=5.0,
            fisheye_polynomial_f=6.0,
        )

        stage = omni.usd.get_context().get_stage()
        cam_xform = stage.GetPrimAtPath("/Replicator/Camera_Xform")
        cam = cam_xform.GetChild("Camera")

        self.assertTrue(cam.GetAttribute("focalLength").Get(), 35.0)
        self.assertTrue(cam.GetAttribute("focusDistance").Get(), 200.0)
        self.assertTrue(cam.GetAttribute("fStop").Get(), 1.0)
        self.assertTrue(cam.GetAttribute("horizontalAperture").Get(), 30)
        self.assertTrue(cam.GetAttribute("horizontalApertureOffset").Get(), 1.0)
        self.assertTrue(cam.GetAttribute("verticalApertureOffset").Get(), 2.0)
        self.assertTrue(cam.GetAttribute("clippingRange").Get(), (2.0, 3.0))
        self.assertTrue(cam.GetAttribute("cameraProjectionType").Get(), "fisheyeKannalaBrandtK3")
        self.assertTrue(cam.GetAttribute("fthetaWidth").Get(), 1800)
        self.assertTrue(cam.GetAttribute("fthetaHeight").Get(), 1000)
        self.assertTrue(cam.GetAttribute("fthetaCx").Get(), 900)
        self.assertTrue(cam.GetAttribute("fthetaCy").Get(), 500)
        self.assertTrue(cam.GetAttribute("fthetaMaxFov").Get(), 300.0)
        self.assertTrue(cam.GetAttribute("fthetaPolyA").Get(), 1.0)
        self.assertTrue(cam.GetAttribute("fthetaPolyB").Get(), 2.0)
        self.assertTrue(cam.GetAttribute("fthetaPolyC").Get(), 3.0)
        self.assertTrue(cam.GetAttribute("fthetaPolyD").Get(), 4.0)
        self.assertTrue(cam.GetAttribute("fthetaPolyE").Get(), 5.0)
        self.assertTrue(cam.GetAttribute("fthetaPolyF").Get(), 6.0)

    async def test_create_camera_rad_tan_thin_prism(self):
        rep.create.camera(
            None,
            None,
            None,
            focal_length=35.0,
            focus_distance=200.0,
            f_stop=1.0,
            horizontal_aperture=30,
            horizontal_aperture_offset=1.0,
            vertical_aperture_offset=2.0,
            clipping_range=(2.0, 3.0),
            projection_type="fisheyeRadTanThinPrism",
            fisheye_nominal_width=1800,
            fisheye_nominal_height=1000,
            fisheye_optical_centre_x=900,
            fisheye_optical_centre_y=500,
            fisheye_max_fov=300.0,
            fisheye_polynomial_a=1.0,
            fisheye_polynomial_b=2.0,
            fisheye_polynomial_c=3.0,
            fisheye_polynomial_d=4.0,
            fisheye_polynomial_e=5.0,
            fisheye_polynomial_f=6.0,
            fisheye_p0=0.1,
            fisheye_p1=0.2,
            fisheye_s0=0.1,
            fisheye_s1=0.2,
            fisheye_s2=0.3,
            fisheye_s3=0.4,
        )

        stage = omni.usd.get_context().get_stage()
        cam_xform = stage.GetPrimAtPath("/Replicator/Camera_Xform")
        cam = cam_xform.GetChild("Camera")

        self.assertTrue(cam.GetAttribute("focalLength").Get(), 35.0)
        self.assertTrue(cam.GetAttribute("focusDistance").Get(), 200.0)
        self.assertTrue(cam.GetAttribute("fStop").Get(), 1.0)
        self.assertTrue(cam.GetAttribute("horizontalAperture").Get(), 30)
        self.assertTrue(cam.GetAttribute("horizontalApertureOffset").Get(), 1.0)
        self.assertTrue(cam.GetAttribute("verticalApertureOffset").Get(), 2.0)
        self.assertTrue(cam.GetAttribute("clippingRange").Get(), (2.0, 3.0))
        self.assertTrue(cam.GetAttribute("cameraProjectionType").Get(), "fisheyeRadTanThinPrism")
        self.assertTrue(cam.GetAttribute("fthetaWidth").Get(), 1800)
        self.assertTrue(cam.GetAttribute("fthetaHeight").Get(), 1000)
        self.assertTrue(cam.GetAttribute("fthetaCx").Get(), 900)
        self.assertTrue(cam.GetAttribute("fthetaCy").Get(), 500)
        self.assertTrue(cam.GetAttribute("fthetaMaxFov").Get(), 300.0)
        self.assertTrue(cam.GetAttribute("fthetaPolyA").Get(), 1.0)
        self.assertTrue(cam.GetAttribute("fthetaPolyB").Get(), 2.0)
        self.assertTrue(cam.GetAttribute("fthetaPolyC").Get(), 3.0)
        self.assertTrue(cam.GetAttribute("fthetaPolyD").Get(), 4.0)
        self.assertTrue(cam.GetAttribute("fthetaPolyE").Get(), 5.0)
        self.assertTrue(cam.GetAttribute("fthetaPolyF").Get(), 6.0)
        self.assertTrue(cam.GetAttribute("p0").Get(), 0.1)
        self.assertTrue(cam.GetAttribute("p1").Get(), 0.2)
        self.assertTrue(cam.GetAttribute("s0").Get(), 0.1)
        self.assertTrue(cam.GetAttribute("s1").Get(), 0.2)
        self.assertTrue(cam.GetAttribute("s2").Get(), 0.3)
        self.assertTrue(cam.GetAttribute("s3").Get(), 0.4)

    async def test_create_camera(self):
        rep.create.camera(
            None,
            None,
            None,
            focal_length=35.0,
            focus_distance=200.0,
            f_stop=1.0,
            horizontal_aperture=30,
            horizontal_aperture_offset=1.0,
            vertical_aperture_offset=2.0,
            clipping_range=(2.0, 3.0),
            projection_type="fisheyePolynomial",
            fisheye_nominal_width=1800,
            fisheye_nominal_height=1000,
            fisheye_optical_centre_x=900,
            fisheye_optical_centre_y=500,
            fisheye_max_fov=300.0,
            fisheye_polynomial_a=1.0,
            fisheye_polynomial_b=2.0,
            fisheye_polynomial_c=3.0,
            fisheye_polynomial_d=4.0,
            fisheye_polynomial_e=5.0,
            fisheye_polynomial_f=6.0,
        )

        stage = omni.usd.get_context().get_stage()
        cam_xform = stage.GetPrimAtPath("/Replicator/Camera_Xform")
        cam = cam_xform.GetChild("Camera")

        self.assertTrue(cam.GetAttribute("focalLength").Get(), 35.0)
        self.assertTrue(cam.GetAttribute("focusDistance").Get(), 200.0)
        self.assertTrue(cam.GetAttribute("fStop").Get(), 1.0)
        self.assertTrue(cam.GetAttribute("horizontalAperture").Get(), 30)
        self.assertTrue(cam.GetAttribute("horizontalApertureOffset").Get(), 1.0)
        self.assertTrue(cam.GetAttribute("verticalApertureOffset").Get(), 2.0)
        self.assertTrue(cam.GetAttribute("clippingRange").Get(), (2.0, 3.0))
        self.assertTrue(cam.GetAttribute("cameraProjectionType").Get(), "fisheyePolynomial")
        self.assertTrue(cam.GetAttribute("fthetaWidth").Get(), 1800)
        self.assertTrue(cam.GetAttribute("fthetaHeight").Get(), 1000)
        self.assertTrue(cam.GetAttribute("fthetaCx").Get(), 900)
        self.assertTrue(cam.GetAttribute("fthetaCy").Get(), 500)
        self.assertTrue(cam.GetAttribute("fthetaMaxFov").Get(), 300.0)
        self.assertTrue(cam.GetAttribute("fthetaPolyA").Get(), 1.0)
        self.assertTrue(cam.GetAttribute("fthetaPolyB").Get(), 2.0)
        self.assertTrue(cam.GetAttribute("fthetaPolyC").Get(), 3.0)
        self.assertTrue(cam.GetAttribute("fthetaPolyD").Get(), 4.0)
        self.assertTrue(cam.GetAttribute("fthetaPolyE").Get(), 5.0)
        self.assertTrue(cam.GetAttribute("fthetaPolyF").Get(), 6.0)

    async def test_create_named_objects(self):
        rep.create.camera(name="test_camera")
        stage = omni.usd.get_context().get_stage()
        cam_xform = stage.GetPrimAtPath("/Replicator/test_camera_Xform")
        cam = cam_xform.GetChild("test_camera")
        self.assertTrue(cam_xform.IsValid())
        self.assertTrue(cam.IsValid())
        cubes = rep.create.cube(name="test_cubes", count=3)
        cube_xform = stage.GetPrimAtPath("/Replicator/test_cubes_Xform_01")
        cube = cube_xform.GetChild("test_cubes")
        self.assertTrue(cube_xform.IsValid())
        self.assertTrue(cube.IsValid())

    async def test_create_xform(self):
        stage = omni.usd.get_context().get_stage()
        rep.create._create_prim("Xform")
        xform = stage.GetPrimAtPath("/Replicator/Xform")
        self.assertTrue(xform.IsValid())
        rep.create.xform(name="xform_test", position=(10, 10, 10))
        xform = stage.GetPrimAtPath("/Replicator/xform_test")
        self.assertTrue(xform.IsValid())
        await omni.kit.app.get_app().next_update_async()
        position = np.array(xform.GetAttribute("xformOp:translate").Get())
        np.testing.assert_allclose(position, np.array((10.0, 10.0, 10.0)), atol=1e-3)

    async def test_create_multiple_camera(self):
        rep.create.camera(
            None,
            None,
            None,
            focal_length=35.0,
            focus_distance=200.0,
            f_stop=1.0,
            horizontal_aperture=30,
            horizontal_aperture_offset=1.0,
            vertical_aperture_offset=2.0,
            clipping_range=(2.0, 3.0),
            projection_type="fisheyePolynomial",
            fisheye_nominal_width=1800,
            fisheye_nominal_height=1000,
            fisheye_optical_centre_x=900,
            fisheye_optical_centre_y=500,
            fisheye_max_fov=300.0,
            fisheye_polynomial_a=1.0,
            fisheye_polynomial_b=2.0,
            fisheye_polynomial_c=3.0,
            fisheye_polynomial_d=4.0,
            fisheye_polynomial_e=5.0,
            fisheye_polynomial_f=6.0,
            count=5,
        )

        stage = omni.usd.get_context().get_stage()

        for i in range(5):
            if i == 0:
                cam_xform = stage.GetPrimAtPath("/Replicator/Camera_Xform")
            else:
                cam_xform = stage.GetPrimAtPath(f"/Replicator/Camera_Xform_0{i}")
            cam = cam_xform.GetChild("Camera")

            self.assertTrue(cam.GetAttribute("focalLength").Get(), 35.0)
            self.assertTrue(cam.GetAttribute("focusDistance").Get(), 200.0)
            self.assertTrue(cam.GetAttribute("fStop").Get(), 1.0)
            self.assertTrue(cam.GetAttribute("horizontalAperture").Get(), 30)
            self.assertTrue(cam.GetAttribute("horizontalApertureOffset").Get(), 1.0)
            self.assertTrue(cam.GetAttribute("verticalApertureOffset").Get(), 2.0)
            self.assertTrue(cam.GetAttribute("clippingRange").Get(), (2.0, 3.0))
            self.assertTrue(cam.GetAttribute("cameraProjectionType").Get(), "fisheyePolynomial")
            self.assertTrue(cam.GetAttribute("fthetaWidth").Get(), 1800)
            self.assertTrue(cam.GetAttribute("fthetaHeight").Get(), 1000)
            self.assertTrue(cam.GetAttribute("fthetaCx").Get(), 900)
            self.assertTrue(cam.GetAttribute("fthetaCy").Get(), 500)
            self.assertTrue(cam.GetAttribute("fthetaMaxFov").Get(), 300.0)
            self.assertTrue(cam.GetAttribute("fthetaPolyA").Get(), 1.0)
            self.assertTrue(cam.GetAttribute("fthetaPolyB").Get(), 2.0)
            self.assertTrue(cam.GetAttribute("fthetaPolyC").Get(), 3.0)
            self.assertTrue(cam.GetAttribute("fthetaPolyD").Get(), 4.0)
            self.assertTrue(cam.GetAttribute("fthetaPolyE").Get(), 5.0)
            self.assertTrue(cam.GetAttribute("fthetaPolyF").Get(), 6.0)

    async def test_create_stereo_camera(self):
        sphere = rep.create.sphere()
        stereo_camera_pair = rep.create.stereo_camera(
            stereo_baseline=10,
            position=rep.distribution.uniform((0, 100, 100), (0, 200, 200)),
            rotation=None,
            look_at=sphere,
            focal_length=35.0,
            focus_distance=200.0,
            f_stop=1.0,
            horizontal_aperture=30,
            horizontal_aperture_offset=1.0,
            vertical_aperture_offset=2.0,
            clipping_range=(2.0, 3.0),
            projection_type="fisheyePolynomial",
            fisheye_nominal_width=1800,
            fisheye_nominal_height=1000,
            fisheye_optical_centre_x=900,
            fisheye_optical_centre_y=500,
            fisheye_max_fov=300.0,
            fisheye_polynomial_a=1.0,
            fisheye_polynomial_b=2.0,
            fisheye_polynomial_c=3.0,
            fisheye_polynomial_d=4.0,
            fisheye_polynomial_e=5.0,
            fisheye_polynomial_f=6.0,
        )

        await omni.kit.app.get_app().next_update_async()

        stage = omni.usd.get_context().get_stage()

        left_cam = stage.GetPrimAtPath("/Replicator/StereoCam/StereoCam_L_Xform/StereoCam_L")
        right_cam = stage.GetPrimAtPath("/Replicator/StereoCam/StereoCam_R_Xform/StereoCam_R")

        left_cam_xform = stage.GetPrimAtPath("/Replicator/StereoCam/StereoCam_L_Xform")
        right_cam_xform = stage.GetPrimAtPath("/Replicator/StereoCam/StereoCam_R_Xform")

        self.assertTrue(left_cam.IsValid())
        self.assertTrue(right_cam.IsValid())
        self.assertTrue(left_cam_xform.IsValid())
        self.assertTrue(right_cam_xform.IsValid())

        # Test intrinsics (left)
        self.assertTrue(left_cam.GetAttribute("focalLength").Get(), 35.0)
        self.assertTrue(left_cam.GetAttribute("focusDistance").Get(), 200.0)
        self.assertTrue(left_cam.GetAttribute("fStop").Get(), 1.0)
        self.assertTrue(left_cam.GetAttribute("horizontalAperture").Get(), 30)
        self.assertTrue(left_cam.GetAttribute("horizontalApertureOffset").Get(), 1.0)
        self.assertTrue(left_cam.GetAttribute("verticalApertureOffset").Get(), 2.0)
        self.assertTrue(left_cam.GetAttribute("clippingRange").Get(), (2.0, 3.0))
        self.assertTrue(left_cam.GetAttribute("cameraProjectionType").Get(), "fisheyePolynomial")
        self.assertTrue(left_cam.GetAttribute("fthetaWidth").Get(), 1800)
        self.assertTrue(left_cam.GetAttribute("fthetaHeight").Get(), 1000)
        self.assertTrue(left_cam.GetAttribute("fthetaCx").Get(), 900)
        self.assertTrue(left_cam.GetAttribute("fthetaCy").Get(), 500)
        self.assertTrue(left_cam.GetAttribute("fthetaMaxFov").Get(), 300.0)
        self.assertTrue(left_cam.GetAttribute("fthetaPolyA").Get(), 1.0)
        self.assertTrue(left_cam.GetAttribute("fthetaPolyB").Get(), 2.0)
        self.assertTrue(left_cam.GetAttribute("fthetaPolyC").Get(), 3.0)
        self.assertTrue(left_cam.GetAttribute("fthetaPolyD").Get(), 4.0)
        self.assertTrue(left_cam.GetAttribute("fthetaPolyE").Get(), 5.0)
        self.assertTrue(left_cam.GetAttribute("fthetaPolyF").Get(), 6.0)

        # Test intrinsics (right)
        self.assertTrue(right_cam.GetAttribute("focalLength").Get(), 35.0)
        self.assertTrue(right_cam.GetAttribute("focusDistance").Get(), 200.0)
        self.assertTrue(right_cam.GetAttribute("fStop").Get(), 1.0)
        self.assertTrue(right_cam.GetAttribute("horizontalAperture").Get(), 30)
        self.assertTrue(right_cam.GetAttribute("horizontalApertureOffset").Get(), 1.0)
        self.assertTrue(right_cam.GetAttribute("verticalApertureOffset").Get(), 2.0)
        self.assertTrue(right_cam.GetAttribute("clippingRange").Get(), (2.0, 3.0))
        self.assertTrue(right_cam.GetAttribute("cameraProjectionType").Get(), "fisheyePolynomial")
        self.assertTrue(right_cam.GetAttribute("fthetaWidth").Get(), 1800)
        self.assertTrue(right_cam.GetAttribute("fthetaHeight").Get(), 1000)
        self.assertTrue(right_cam.GetAttribute("fthetaCx").Get(), 900)
        self.assertTrue(right_cam.GetAttribute("fthetaCy").Get(), 500)
        self.assertTrue(right_cam.GetAttribute("fthetaMaxFov").Get(), 300.0)
        self.assertTrue(right_cam.GetAttribute("fthetaPolyA").Get(), 1.0)
        self.assertTrue(right_cam.GetAttribute("fthetaPolyB").Get(), 2.0)
        self.assertTrue(right_cam.GetAttribute("fthetaPolyC").Get(), 3.0)
        self.assertTrue(right_cam.GetAttribute("fthetaPolyD").Get(), 4.0)
        self.assertTrue(right_cam.GetAttribute("fthetaPolyE").Get(), 5.0)
        self.assertTrue(right_cam.GetAttribute("fthetaPolyF").Get(), 6.0)

        # Test local position
        left_local_position = np.array(left_cam_xform.GetAttribute("xformOp:translate").Get())
        right_local_position = np.array(right_cam_xform.GetAttribute("xformOp:translate").Get())
        np.testing.assert_allclose(left_local_position, np.array((-5, 0.0, 0.0)), atol=1e-3)
        np.testing.assert_allclose(right_local_position, np.array((5, 0.0, 0.0)), atol=1e-3)

        left_tf = UsdGeom.Xformable(left_cam_xform).ComputeLocalToWorldTransform(0.0)
        right_tf = UsdGeom.Xformable(right_cam_xform).ComputeLocalToWorldTransform(0.0)

        # Test world position
        left_position = np.array(left_tf.ExtractTranslation())
        right_position = np.array(right_tf.ExtractTranslation())
        np.testing.assert_allclose(left_position, np.array((-5, 195.04637, 114.415961)), atol=1e-3)
        np.testing.assert_allclose(right_position, np.array((5, 195.04637, 114.415961)), atol=1e-3)

        # Test rotation
        left_rotation = left_tf.ExtractRotation()
        right_rotation = right_tf.ExtractRotation()
        self.assertAlmostEqual(left_rotation.angle, right_rotation.angle)
        np.testing.assert_allclose(np.array(left_rotation.axis), np.array(right_rotation.axis))

    async def test_create_stereo_camera_up_z(self):
        rep.settings.set_stage_up_axis("Z")
        sphere = rep.create.sphere()
        stereo_camera_pair = rep.create.stereo_camera(
            stereo_baseline=10,
            position=rep.distribution.uniform((0, 100, 100), (0, 200, 200)),
            rotation=None,
            look_at=sphere,
            focal_length=35.0,
            focus_distance=200.0,
            f_stop=1.0,
            horizontal_aperture=30,
            horizontal_aperture_offset=1.0,
            vertical_aperture_offset=2.0,
            clipping_range=(2.0, 3.0),
            projection_type="fisheyePolynomial",
            fisheye_nominal_width=1800,
            fisheye_nominal_height=1000,
            fisheye_optical_centre_x=900,
            fisheye_optical_centre_y=500,
            fisheye_max_fov=300.0,
            fisheye_polynomial_a=1.0,
            fisheye_polynomial_b=2.0,
            fisheye_polynomial_c=3.0,
            fisheye_polynomial_d=4.0,
            fisheye_polynomial_e=5.0,
            fisheye_polynomial_f=6.0,
        )

        await omni.kit.app.get_app().next_update_async()

        stage = omni.usd.get_context().get_stage()

        left_cam = stage.GetPrimAtPath("/Replicator/StereoCam/StereoCam_L_Xform/StereoCam_L")
        right_cam = stage.GetPrimAtPath("/Replicator/StereoCam/StereoCam_R_Xform/StereoCam_R")

        left_cam_xform = stage.GetPrimAtPath("/Replicator/StereoCam/StereoCam_L_Xform")
        right_cam_xform = stage.GetPrimAtPath("/Replicator/StereoCam/StereoCam_R_Xform")

        self.assertTrue(left_cam.IsValid())
        self.assertTrue(right_cam.IsValid())
        self.assertTrue(left_cam_xform.IsValid())
        self.assertTrue(right_cam_xform.IsValid())
        self.assertTrue(left_cam.GetAttribute("focalLength").Get(), 35.0)
        self.assertTrue(left_cam.GetAttribute("focusDistance").Get(), 200.0)
        self.assertTrue(left_cam.GetAttribute("fStop").Get(), 1.0)
        self.assertTrue(left_cam.GetAttribute("horizontalAperture").Get(), 30)
        self.assertTrue(left_cam.GetAttribute("horizontalApertureOffset").Get(), 1.0)
        self.assertTrue(left_cam.GetAttribute("verticalApertureOffset").Get(), 2.0)
        self.assertTrue(left_cam.GetAttribute("clippingRange").Get(), (2.0, 3.0))
        self.assertTrue(left_cam.GetAttribute("cameraProjectionType").Get(), "fisheyePolynomial")
        self.assertTrue(left_cam.GetAttribute("fthetaWidth").Get(), 1800)
        self.assertTrue(left_cam.GetAttribute("fthetaHeight").Get(), 1000)
        self.assertTrue(left_cam.GetAttribute("fthetaCx").Get(), 900)
        self.assertTrue(left_cam.GetAttribute("fthetaCy").Get(), 500)
        self.assertTrue(left_cam.GetAttribute("fthetaMaxFov").Get(), 300.0)
        self.assertTrue(left_cam.GetAttribute("fthetaPolyA").Get(), 1.0)
        self.assertTrue(left_cam.GetAttribute("fthetaPolyB").Get(), 2.0)
        self.assertTrue(left_cam.GetAttribute("fthetaPolyC").Get(), 3.0)
        self.assertTrue(left_cam.GetAttribute("fthetaPolyD").Get(), 4.0)
        self.assertTrue(left_cam.GetAttribute("fthetaPolyE").Get(), 5.0)
        self.assertTrue(left_cam.GetAttribute("fthetaPolyF").Get(), 6.0)

        self.assertTrue(right_cam.GetAttribute("focalLength").Get(), 35.0)
        self.assertTrue(right_cam.GetAttribute("focusDistance").Get(), 200.0)
        self.assertTrue(right_cam.GetAttribute("fStop").Get(), 1.0)
        self.assertTrue(right_cam.GetAttribute("horizontalAperture").Get(), 30)
        self.assertTrue(right_cam.GetAttribute("horizontalApertureOffset").Get(), 1.0)
        self.assertTrue(right_cam.GetAttribute("verticalApertureOffset").Get(), 2.0)
        self.assertTrue(right_cam.GetAttribute("clippingRange").Get(), (2.0, 3.0))
        self.assertTrue(right_cam.GetAttribute("cameraProjectionType").Get(), "fisheyePolynomial")
        self.assertTrue(right_cam.GetAttribute("fthetaWidth").Get(), 1800)
        self.assertTrue(right_cam.GetAttribute("fthetaHeight").Get(), 1000)
        self.assertTrue(right_cam.GetAttribute("fthetaCx").Get(), 900)
        self.assertTrue(right_cam.GetAttribute("fthetaCy").Get(), 500)
        self.assertTrue(right_cam.GetAttribute("fthetaMaxFov").Get(), 300.0)
        self.assertTrue(right_cam.GetAttribute("fthetaPolyA").Get(), 1.0)
        self.assertTrue(right_cam.GetAttribute("fthetaPolyB").Get(), 2.0)
        self.assertTrue(right_cam.GetAttribute("fthetaPolyC").Get(), 3.0)
        self.assertTrue(right_cam.GetAttribute("fthetaPolyD").Get(), 4.0)
        self.assertTrue(right_cam.GetAttribute("fthetaPolyE").Get(), 5.0)
        self.assertTrue(right_cam.GetAttribute("fthetaPolyF").Get(), 6.0)

        left_local_position = np.array(left_cam_xform.GetAttribute("xformOp:translate").Get())
        right_local_position = np.array(right_cam_xform.GetAttribute("xformOp:translate").Get())

        np.testing.assert_allclose(left_local_position, np.array((0.0, -5, 0.0)), atol=1e-3)
        np.testing.assert_allclose(right_local_position, np.array((0.0, 5, 0.0)), atol=1e-3)

        left_position = np.array(UsdGeom.Xformable(left_cam_xform).ComputeLocalToWorldTransform(0.0))[3, :3]
        right_position = np.array(UsdGeom.Xformable(right_cam_xform).ComputeLocalToWorldTransform(0.0))[3, :3]

        np.testing.assert_allclose(left_position, np.array((5, 195.046371, 114.415961)), atol=1e-3)
        np.testing.assert_allclose(right_position, np.array((-5, 195.04637, 114.415961)), atol=1e-3)

    async def test_create_render_product_multi_cams(self):
        """Test to create render product for multiple cameras."""
        stereo_camera_pair = rep.create.stereo_camera(stereo_baseline=10)
        render_products = rep.create.render_product(stereo_camera_pair, (1024, 512))
        await omni.kit.app.get_app().next_update_async()

        self.assertTrue(isinstance(render_products, list))
        self.assertEqual(len(render_products), 2)

    @unittest.skipIf(
        omni.kit.test.utils.is_running_in_teamcity() or omni.kit.test.utils.is_running_in_gitlab(),
        "Need a better way to test, used mem varies widely on TC",
    )
    async def test_create_render_product_create_destroy(self):
        """Verify render product created and destroyed releases resources."""
        NUM_WAIT_FRAMES = 50
        RESOLUTION = (2048, 2048)
        MIN_GPU_MEM = 500
        MAX_GPU_MEM = 4000

        for _ in range(NUM_WAIT_FRAMES):
            await omni.kit.app.get_app().next_update_async()
        init_gpu_mem = _get_used_gpu_memory()

        rp = rep.create.render_product("/OmniverseKit_Persp", RESOLUTION)
        for _ in range(NUM_WAIT_FRAMES):
            await omni.kit.app.get_app().next_update_async()
        cur_gpu_mem = _get_used_gpu_memory()
        self.assertTrue(
            MIN_GPU_MEM
            <= cur_gpu_mem - init_gpu_mem
            <= MAX_GPU_MEM,  # Large threshold needed on CI machines, locally seems to be 1000
            f"Expected render product to use > {MIN_GPU_MEM} MB and < {MAX_GPU_MEM} MB but used {cur_gpu_mem - init_gpu_mem} MB (init: {init_gpu_mem}, cur: {cur_gpu_mem})",
        )

        rp.destroy()
        # await omni.usd.get_context().new_stage_async()
        for _ in range(NUM_WAIT_FRAMES):
            await omni.kit.app.get_app().next_update_async()
        cur_gpu_mem = _get_used_gpu_memory()
        self.assertLess(
            cur_gpu_mem - init_gpu_mem,
            MAX_GPU_MEM,  # Large threshold needed on CI machines
            f"Expected < {MIN_GPU_MEM} MB difference after creating+destroying render product but used MB {cur_gpu_mem - init_gpu_mem} (init: {init_gpu_mem}, cur: {cur_gpu_mem})",
        )

        # Recreate render product to ensure that a new one can be created without errors
        rp = rep.create.render_product("/OmniverseKit_Persp", RESOLUTION)
        for _ in range(NUM_WAIT_FRAMES):
            await omni.kit.app.get_app().next_update_async()
        cur_gpu_mem = _get_used_gpu_memory()
        self.assertTrue(
            MIN_GPU_MEM
            <= cur_gpu_mem - init_gpu_mem
            <= MAX_GPU_MEM,  # Large threshold needed on CI machines, locally seems to be 1000
            f"Expected render product to use > {MIN_GPU_MEM} MB and < {MAX_GPU_MEM} MB but used {cur_gpu_mem - init_gpu_mem} MB (init: {init_gpu_mem}, cur: {cur_gpu_mem})",
        )

    async def test_create_render_product_destroy_attached(self):
        """Test destruction of attached render product"""
        # Ensure no errors raised
        anno = rep.annotators.get("LdrColor")
        rp = rep.create.render_product(rep.create.camera(), (1024, 1024))
        anno.attach(rp)

        await rep.orchestrator.step_async()

        rp.destroy()

        await rep.orchestrator.step_async()

    async def test_create_render_product_from_default(self):
        init_rp = rep.create.render_product("/OmniverseKit_Persp", (1024, 256))
        init_rp_path = init_rp.path
        rp = rep.create.render_product(rep.create.camera(), (1024, 256))

        path_prefix = carb.settings.get_settings().get_as_string(RP_PREFIX_SETTING) or LEGACY_RP_PREFIX
        self.assertEqual(init_rp_path, f"/Render/{path_prefix}Replicator", "Default render product naming has changed")
        self.assertEqual(rp.path, f"/Render/{path_prefix}Replicator_01", "Numbering of render products has changed")

    async def test_create_render_product(self):
        """Test to create render product."""
        camera = rep.create.camera(position=(500, 500, 500), look_at=(0, 0, 0))
        render_product = rep.create.render_product(camera, (1024, 512))
        await omni.kit.app.get_app().next_update_async()
        render_product = rep.create.render_product(camera, resolution=(1024.0, 512.0))
        await omni.kit.app.get_app().next_update_async()
        render_product = rep.create.render_product(camera, resolution=("1024", "512"))
        await omni.kit.app.get_app().next_update_async()
        with self.assertRaises(ValueError):
            not_a_camera = 1234
            rep.create.render_product(not_a_camera, (32, 32))
            await omni.kit.app.get_app().next_update_async()
        with self.assertRaises(TypeError):
            rep.create.render_product(camera, resolution="1024x512")
            await omni.kit.app.get_app().next_update_async()

    async def test_create_render_product_named(self):
        """Test to create render product with a name."""
        camera = rep.create.camera(position=(500, 500, 500), look_at=(0, 0, 0))
        camera2 = rep.create.camera(position=(500, 500, 500), look_at=(0, 0, 0))
        rep.create.render_product(camera, (1024, 512))  # Replicator
        rep.create.render_product(camera, (1024, 512), name="Testing")  # Testing
        rep.create.render_product(camera, (1024, 512), name="Testing", force_new=True)  # Testing_01
        rep.create.render_product(camera2, (1024, 512), name="Testing")  # Testing_02
        # Should re-use RP for camera, and make a new RP for camera2 (Replicator, Replicator_01)
        reuse = rep.create.render_product([camera, camera2], (1024, 512))
        # Should make 2 new render products (TestingMulti, TestingMulti_01)
        rep.create.render_product([camera, camera2], (320, 240), name="TestingMulti")

        await omni.kit.app.get_app().next_update_async()

        stage = omni.usd.get_context().get_stage()
        reuse_paths = [rp.path for rp in reuse]
        prefix = carb.settings.get_settings().get_as_string(RP_PREFIX_SETTING) or LEGACY_RP_PREFIX
        self.assertTrue(stage.GetPrimAtPath(f"/Render/{prefix}Testing"))
        self.assertTrue(stage.GetPrimAtPath(f"/Render/{prefix}Testing_01"))
        self.assertTrue(stage.GetPrimAtPath(f"/Render/{prefix}Testing_02"))
        self.assertTrue(stage.GetPrimAtPath(f"/Render/{prefix}TestingMulti"))
        self.assertTrue(stage.GetPrimAtPath(f"/Render/{prefix}TestingMulti_01"))
        self.assertTrue(len(reuse_paths) == 2)
        self.assertTrue(f"/Render/{prefix}Testing_02" in reuse_paths)
        self.assertTrue(f"/Render/{prefix}Replicator" in reuse_paths)

    async def test_create_dome_light_with_texture(self):
        """Test to create domelight with texture."""
        # TODO: implement this once test golden hdr is found.
        dome_light = rep.create.light(
            light_type="Dome", texture=os.path.join(TEST_DATA_DIR, "objects", "textures", "checkerboard_texture.png")
        )

        await omni.kit.app.get_app().next_update_async()

        stage = omni.usd.get_context().get_stage()

        dome_light_prim = stage.GetPrimAtPath("/Replicator/DomeLight_Xform/DomeLight")

        dome_light_texture = dome_light_prim.GetAttribute("inputs:texture:file").Get()

        self.assertTrue(
            dome_light_texture, os.path.join(TEST_DATA_DIR, "objects", "textures", "checkerboard_texture.png")
        )

    async def test_create_look_at_up_axis(self):
        """Test the up axis is created correctly in create."""
        # Create a shape to look_at.
        cube = rep.create.cube(semantics=[("class", "cube")], position=(0, 0, 0))

        camera = rep.create.camera(
            position=(0, 0, 500),
            look_at=cube,
            look_at_up_axis=rep.distribution.uniform((0, 0, 0), (100, 100, 100), seed=10),
        )

        await omni.kit.app.get_app().next_update_async()

        camera_prim_path = camera.node.get_attribute("outputs:prims").get()[0]

        stage = omni.usd.get_context().get_stage()
        camera_prim = stage.GetPrimAtPath(str(camera_prim_path))

        camera_rotation = np.array(camera_prim.GetAttribute("xformOp:rotateXYZ").Get())

        np.testing.assert_allclose(camera_rotation, np.array((0, 0, -77.74351)))

    async def test_create_render_product_reuse(self):
        cam = rep.create.camera()
        with rep.new_layer():
            rep.create.render_product(cam, (512, 512))

        stage = omni.usd.get_context().get_stage()
        cur_renders_num = len(stage.GetPrimAtPath("/Render").GetChildren())

        await omni.kit.app.get_app().next_update_async()
        with rep.new_layer():
            cam = rep.create.camera()
            rep.create.render_product(cam, (512, 512))

        new_renders_num = len(stage.GetPrimAtPath("/Render").GetChildren())

        self.assertEqual(
            cur_renders_num,
            new_renders_num,
            f"Unexpected new `/Render` entry detected. Expected {cur_renders_num}, got {new_renders_num}",
        )

    async def test_create_render_product_force_new(self):
        rep.create.render_product("/OmniverseKit_Persp", (512, 512))

        stage = omni.usd.get_context().get_stage()
        path_prefix = carb.settings.get_settings().get_as_string(RP_PREFIX_SETTING) or LEGACY_RP_PREFIX
        rp_parent = f"/Render/{path_prefix}".rsplit("/", maxsplit=1)[0]
        cur_renders_num = len(stage.GetPrimAtPath(rp_parent).GetChildren())

        await omni.kit.app.get_app().next_update_async()
        rep.create.render_product("/OmniverseKit_Persp", (512, 512), force_new=True)

        render_children = stage.GetPrimAtPath(rp_parent).GetChildren()
        new_renders_num = len(render_children)

        self.assertLess(
            cur_renders_num,
            new_renders_num,
            f"Unexpected number of `{rp_parent}` entry detected. Expected < {new_renders_num}, got {cur_renders_num}: {render_children}",
        )

    async def test_create_render_product_new_layer(self):
        cam = rep.create.camera()
        rep.create.render_product(cam, (512, 512))
        path_prefix = carb.settings.get_settings().get_as_string(RP_PREFIX_SETTING) or LEGACY_RP_PREFIX
        rp_parent = f"/Render/{path_prefix}".rsplit("/", maxsplit=1)[0]

        stage = omni.usd.get_context().get_stage()
        cur_renders_num = len(stage.GetPrimAtPath(rp_parent).GetChildren())

        await omni.kit.app.get_app().next_update_async()
        with rep.new_layer():
            cam = rep.create.camera()
            rep.create.render_product(cam, (512, 512))
        new_renders_num = len(stage.GetPrimAtPath(rp_parent).GetChildren())

        self.assertEqual(cur_renders_num + 1, new_renders_num, f"Unexpected number of `{rp_parent}` entry detected")

        await omni.kit.app.get_app().next_update_async()
        with rep.new_layer():
            cam = rep.create.camera()
            rep.create.render_product(cam, (512, 512))
        new_renders_num = len(stage.GetPrimAtPath(rp_parent).GetChildren())

        self.assertEqual(cur_renders_num + 1, new_renders_num, f"Unexpected number of `{rp_parent}` entry detected")

    async def test_create_mdl_material_graph_from_json(self):
        gen_mat = rep.create.mdl_from_json(material_def_path=os.path.join(TEST_DATA_DIR, "test_mdl_graph.json"))
        cube = rep.create.cube(material=gen_mat)

        # It takes a few frames for the rest of the MDL graph to populate
        for _ in range(6):
            await omni.kit.app.get_app().next_update_async()

        stage = omni.usd.get_context().get_stage()
        mat_path = "/Replicator/Looks/RepMaterialTest"
        base_path = mat_path + "/base"
        layer1_path = mat_path + "/layer1"
        blend_path = mat_path + "/blend"
        noise_path = mat_path + "/perlin_noise_texture"
        cube_prim = stage.GetPrimAtPath("/Replicator/Cube_Xform/Cube")

        self.assertTrue(stage.GetPrimAtPath(mat_path).IsValid(), "Generated material is not valid!")
        self.assertTrue(stage.GetPrimAtPath(base_path).IsValid(), "Base shader is not valid!")
        self.assertTrue(stage.GetPrimAtPath(layer1_path).IsValid(), "Layer1 shader is not valid!")
        self.assertTrue(stage.GetPrimAtPath(blend_path).IsValid(), "Blend shadder is not valid!")
        self.assertTrue(stage.GetPrimAtPath(noise_path).IsValid(), "Noise node graph is not valid!")

        self.assertEqual(
            UsdShade.MaterialBindingAPI(cube_prim).GetDirectBinding().GetMaterial().GetPath(),
            mat_path,
            "Bound material is not correct!",
        )

    async def test_create_mdl_material_graph_from_json_check_render(self):
        gen_mat = rep.create.mdl_from_json(material_def=rep.example.MDL_JSON_EXAMPLE)
        cube = rep.create.cube(material=gen_mat)

        anno = rep.annotators.get("LdrColor")
        rp = rep.create.render_product("/OmniverseKit_Persp", (1024, 1024))
        anno.attach(rp)

        await rep.orchestrator.step_async(rt_subframes=10)

        data = anno.get_data()

        golden_dir = os.path.join(TEST_DATA_DIR, "golden")
        golden_file = os.path.join(golden_dir, "mdl_from_json_example.png")
        golden_data = np.array(Image.open(golden_file))

        std_dev = np.sqrt(np.square(data - golden_data).astype(float).mean())
        if std_dev > 2:
            tc_show_image("mdl_from_json_example", golden_dir, golden_dir, data)
        self.assertLess(std_dev, 2)

    async def test_create_mdl_material_graph_from_json_errors(self):
        # Test invalid input attribute name
        test_case_1 = {
            "name": "RepMaterialTest",
            "nodes": {
                "material": {"type": "material"},
                "a": {"type": "diffuse", "name": "base", "out_type": "Token"},
                "blend": {"type": "surface_falloff", "name": "blend", "out_type": "Token"},
            },
            "edges": {
                "1": {"output": {"node": "a", "pin": "out"}, "input": {"node": "blend", "pin": "base"}},
                "3": {"input": {"node": "a", "values": {"diffuse_color": [0.0, 0.0, 1.0]}}},
                "6": {"input": {"node": "blend", "values": {"INVALID": 0.5}}},  # INVALID ATTRIBUTE
            },
        }
        with self.assertRaises(MaterialGraphGeneratorError) as context:
            MaterialGraphGenerator(test_case_1).create_graph()

        # Test invalid connection input attribute name
        test_case_2 = {
            "name": "RepMaterialTest",
            "nodes": {
                "material": {"type": "material"},
                "a": {"type": "diffuse", "name": "base", "out_type": "Token"},
                "blend": {"type": "surface_falloff", "name": "blend", "out_type": "Token"},
            },
            "edges": {
                "1": {
                    "output": {"node": "a", "pin": "out"},
                    "input": {"node": "blend", "pin": "INVALID"},
                },  # INVALID ATTRIBUTE
                "3": {"input": {"node": "a", "values": {"diffuse_color": [0.0, 0.0, 1.0]}}},
                "6": {"input": {"node": "blend", "values": {"facing_weight": 0.5}}},
            },
        }
        with self.assertRaises(MaterialGraphGeneratorError) as context:
            MaterialGraphGenerator(test_case_2).create_graph()

        # Test invalid connection output attribute name
        test_case_3 = {
            "name": "RepMaterialTest",
            "nodes": {
                "material": {"type": "material"},
                "a": {"type": "diffuse", "name": "base", "out_type": "Token"},
                "blend": {"type": "surface_falloff", "name": "blend", "out_type": "Token"},
            },
            "edges": {
                "1": {
                    "output": {"node": "a", "pin": "INVALID"},
                    "input": {"node": "blend", "pin": "base"},
                },  # INVALID ATTRIBUTE
                "3": {"input": {"node": "a", "values": {"diffuse_color": [0.0, 0.0, 1.0]}}},
                "6": {"input": {"node": "blend", "values": {"facing_weight": 0.5}}},
            },
        }
        with self.assertRaises(MaterialGraphGeneratorError) as context:
            MaterialGraphGenerator(test_case_3).create_graph()

        # Test missing type key
        test_case_4 = {
            "name": "RepMaterialTest",
            "nodes": {
                "material": {},  # No type!
                "a": {"type": "diffuse", "name": "base", "out_type": "Token"},
                "blend": {"type": "surface_falloff", "name": "blend", "out_type": "Token"},
            },
            "edges": {
                "1": {"output": {"node": "a", "pin": "out"}, "input": {"node": "blend", "pin": "base"}},
                "3": {"input": {"node": "a", "values": {"diffuse_color": [0.0, 0.0, 1.0]}}},
                "6": {"input": {"node": "blend", "values": {"facing_weight": 0.5}}},
            },
        }
        with self.assertRaises(MaterialGraphGeneratorError) as context:
            MaterialGraphGenerator(test_case_4).create_graph()

        # Test invalid definition data type
        test_case_5 = {"INVALID"}  # Invalid type
        with self.assertRaises(MaterialGraphGeneratorError) as context:
            MaterialGraphGenerator(test_case_5).create_graph()

        # Test invalid definition path
        test_case_6 = "/invalid/path.json"  # Invalid path
        with self.assertRaises(ValueError) as context:
            rep.create.mdl_from_json(material_def_path=test_case_6)

    async def test_create_single_projection(self):
        """Test to see if the projection prim is created and setup properly"""

        await omni.usd.get_context().new_stage_async()

        torus = rep.create.torus()
        cube = rep.create.cube(position=(50, 100, 0), rotation=(0, 0, 90), scale=(0.2, 0.2, 0.2))

        sem = [("class", "smile")]

        with torus:
            rep.create.projection_material(cube, sem)

        await omni.kit.app.get_app().next_update_async()

        stage = omni.usd.get_context().get_stage()

        # Check structure
        self.assertTrue(stage.GetPrimAtPath("/Replicator/Torus_Xform/Projection/Cube_Xform").IsValid())

        projection_prim = stage.GetPrimAtPath("/Replicator/Torus_Xform/Projection/Cube_Xform")

        # Check materials
        self.assertEquals(
            str(UsdShade.MaterialBindingAPI(projection_prim).GetDirectBinding().GetMaterial().GetPath()),
            "/Looks/ProjectPBRMaterial",
        )

        # Check that primvars exist
        self.assertTrue(projection_prim.GetAttribute("primvars:projection_quat").IsValid())
        self.assertTrue(projection_prim.GetAttribute("primvars:projection_position").IsValid())
        self.assertTrue(projection_prim.GetAttribute("primvars:projection_scale").IsValid())
        self.assertTrue(projection_prim.GetAttribute("primvars:doNotCastShadows").IsValid())

    async def test_create_multiple_projections(self):
        """Test to see if the projection prim is created and setup properly"""

        await omni.usd.get_context().new_stage_async()

        torus = rep.create.torus()
        cube_01 = rep.create.cube(position=(50, 100, 0), rotation=(0, 0, 90), scale=(0.2, 0.2, 0.2))
        cube_02 = rep.create.cube(position=(-50, 100, 0), rotation=(0, 0, 90), scale=(0.2, 0.2, 0.2))

        sem = [("class", "smile")]

        with torus:
            rep.create.projection_material(cube_01, sem)
            rep.create.projection_material(cube_02, sem)

        await omni.kit.app.get_app().next_update_async()

        stage = omni.usd.get_context().get_stage()

        # Check structure
        self.assertTrue(stage.GetPrimAtPath("/Replicator/Torus_Xform/Projection/Cube_Xform").IsValid())
        self.assertTrue(stage.GetPrimAtPath("/Replicator/Torus_Xform/Projection/Cube_Xform_01").IsValid())

        projection_prim_01 = stage.GetPrimAtPath("/Replicator/Torus_Xform/Projection/Cube_Xform")
        projection_prim_02 = stage.GetPrimAtPath("/Replicator/Torus_Xform/Projection/Cube_Xform_01")

        # Check materials
        self.assertEqual(
            str(UsdShade.MaterialBindingAPI(projection_prim_01).GetDirectBinding().GetMaterial().GetPath()),
            "/Looks/ProjectPBRMaterial",
        )
        self.assertEqual(
            str(UsdShade.MaterialBindingAPI(projection_prim_02).GetDirectBinding().GetMaterial().GetPath()),
            "/Looks/ProjectPBRMaterial_01",
        )

        # Check that primvars exist
        self.assertTrue(projection_prim_01.GetAttribute("primvars:projection_quat").IsValid())
        self.assertTrue(projection_prim_01.GetAttribute("primvars:projection_position").IsValid())
        self.assertTrue(projection_prim_01.GetAttribute("primvars:projection_scale").IsValid())
        self.assertTrue(projection_prim_01.GetAttribute("primvars:doNotCastShadows").IsValid())
        self.assertTrue(projection_prim_02.GetAttribute("primvars:projection_quat").IsValid())
        self.assertTrue(projection_prim_02.GetAttribute("primvars:projection_position").IsValid())
        self.assertTrue(projection_prim_02.GetAttribute("primvars:projection_scale").IsValid())
        self.assertTrue(projection_prim_02.GetAttribute("primvars:doNotCastShadows").IsValid())

    async def test_create_parenting(self):
        """Test to see if replicator parenting works properly"""
        stage = omni.usd.get_context().get_stage()
        if stage.HasDefaultPrim():
            root_path = stage.GetDefaultPrim().GetPath()
        else:
            root_path = Sdf.Path.absoluteRootPath
        # Create cube
        omni.kit.commands.execute("CreatePrim", prim_type="Cube")
        cube_path = root_path.AppendChild("Cube")
        cube = stage.GetPrimAtPath(cube_path)
        self.assertTrue(cube)

        await omni.kit.app.get_app().next_update_async()
        sphere = rep.create.sphere()
        cone = rep.create.cone(parent=sphere)
        torus = rep.create.torus(parent=cone)
        rep.create.disk(parent=cone)
        rep.create.light(parent=torus)
        rep.create.stereo_camera(stereo_baseline=1.0, parent=torus)

        # Cannot parent to gprims
        with self.assertRaises(ValueError):
            rep.create.sphere(parent=cube)

        # Check parenting structure
        self.assertTrue(stage.GetPrimAtPath("/Replicator/Sphere_Xform/Cone_Xform/Cone").IsValid())
        self.assertTrue(stage.GetPrimAtPath("/Replicator/Sphere_Xform/Cone_Xform/Torus_Xform/Torus").IsValid())
        self.assertTrue(
            stage.GetPrimAtPath(
                "/Replicator/Sphere_Xform/Cone_Xform/Torus_Xform/DistantLight_Xform/DistantLight"
            ).IsValid()
        )
        self.assertTrue(stage.GetPrimAtPath("/Replicator/Sphere_Xform/Cone_Xform/Disk_Xform/Disk").IsValid())
        self.assertTrue(
            stage.GetPrimAtPath(
                "/Replicator/Sphere_Xform/Cone_Xform/Torus_Xform/StereoCam/StereoCam_L_Xform/StereoCam_L"
            ).IsValid()
        )
        self.assertTrue(
            stage.GetPrimAtPath(
                "/Replicator/Sphere_Xform/Cone_Xform/Torus_Xform/StereoCam/StereoCam_R_Xform/StereoCam_R"
            ).IsValid()
        )

    async def test_create_invalid_prim_names(self):
        """
        An identifier is valid if it follows the C/Python identifier convention;
        that is, it must be at least one character long, must start with a letter or underscore,
        and must contain only letters, underscores, and numerals.
        """
        # https://openusd.org/release/api/group__group__tf___string.html#gaa129b294af3f68d01477d430b70d40c8
        stage = omni.usd.get_context().get_stage()

        # Test invalid prim names
        rep.create.sphere(name="invalid-sphere-prim-name")
        self.assertTrue(
            stage.GetPrimAtPath("/Replicator/invalid_sphere_prim_name_Xform/invalid_sphere_prim_name").IsValid()
        )
        rep.create.cube(name="")
        self.assertTrue(stage.GetPrimAtPath("/Replicator/__Xform/_").IsValid())
        rep.create.cone(name="123xyx")
        self.assertTrue(stage.GetPrimAtPath("/Replicator/_23xyx_Xform/_23xyx").IsValid())
        rp = rep.create.render_product("/OmniverseKit_Persp", (128, 128), name="my-dash-separated-name-01")

    async def test_create_tiled_render_product_square(self):
        async def test_tiles(num_cameras, tile_resolution):
            await omni.usd.get_context().new_stage_async()

            cams = []
            for i in range(num_cameras):
                rep.create.cube(position=(i * 2000, 0, 0), pivot=(0, 0, 1))
                cams.append(rep.create.camera(position=(i * 2000, 0, i * 100 + 100)))

            rp_tiled = rep.create.render_product_tiled(cameras=cams, tile_resolution=tile_resolution, force_new=True)

            anno = rep.annotators.get("distance_to_camera", device="cuda")
            anno.attach(rp_tiled)

            await rep.orchestrator.step_async()
            data = anno.get_data()

            # Uncomment for debugging
            # from omni.replicator.core.writers_default.tools import colorize_distance
            # from PIL import Image
            # Image.fromarray(colorize_distance(data)).save(f"tiled_square_{num_cameras}.png")

            for i in range(num_cameras):
                expected_depth = i + 1
                y_min, y_max = tile_resolution[1] * (i // 4), (tile_resolution[1] * (i // 4) + tile_resolution[1])
                x_min, x_max = tile_resolution[0] * (i % 4), (tile_resolution[0] * (i % 4) + tile_resolution[0])
                tile = data[y_min:y_max, x_min:x_max]
                # Uncomment for debugging
                # Image.fromarray(colorize_distance(tile)).save(f"implicit_{i}.png")
                observed_depth = tile.numpy()[tile_resolution[1] // 2, tile_resolution[0] // 2]
                self.assertAlmostEqual(observed_depth, expected_depth, places=1)

        tile_resolution = (60, 60)

        await test_tiles(10, tile_resolution)

    async def test_create_tiled_render_product_rect(self):
        # Create multiple tiled render products at rectangular resolution
        tile_resolutions = [(64, 32), (19, 69)]
        annos = []
        for rp_idx, tile_resolution in enumerate(tile_resolutions):
            num_cameras = 6 + rp_idx
            cubes = []
            cams = []
            for i in range(num_cameras):
                cubes.append(rep.create.cube(position=(i * 2000, 0, 0), pivot=(0, 0, 1)))
                cams.append(rep.create.camera(position=(i * 2000, 0, i * 100 + 100 + rp_idx * 100)))
            rp = rep.create.render_product_tiled(cameras=cams, tile_resolution=tile_resolution)

            anno = rep.annotators.get("distance_to_camera", device="cuda")
            anno.attach(rp)
            annos.append(anno)

        await rep.orchestrator.step_async()

        for rp_idx, tile_resolution in enumerate(tile_resolutions):
            num_cameras = 6 + rp_idx
            data = annos[rp_idx].get_data()

            # Uncomment for debugging
            # from omni.replicator.core.writers_default.tools import colorize_distance
            # from PIL import Image
            # Image.fromarray(colorize_distance(data)).save(f"tiled_rect_{rp_idx}.png")

            for i in range(num_cameras):
                expected_depth = i + 1 + rp_idx
                y_min, y_max = tile_resolution[1] * (i // 3), (tile_resolution[1] * (i // 3) + tile_resolution[1])
                x_min, x_max = tile_resolution[0] * (i % 3), (tile_resolution[0] * (i % 3) + tile_resolution[0])
                tile = data[y_min:y_max, x_min:x_max]
                # Uncomment for debugging
                # Image.fromarray(colorize_distance(tile)).save(f"implicit_{i}_{rp_idx}.png")
                observed_depth = tile.numpy()[tile_resolution[1] // 2, tile_resolution[0] // 2]
                self.assertAlmostEqual(observed_depth, expected_depth, places=1)

    # TODO: Add test back when the tiled bbox 2d bug is fixed.
    @unittest.skip("Skip, revert the tiled bbox 2d change because of bug. NV Bug: 5294174")
    async def test_create_tiled_render_product_bboxes(self):
        """Test to see if creating a tiled render product has a 2d bbox for each tile"""
        await omni.usd.get_context().new_stage_async()

        # Create a cube that will be visible in all tiles
        cube = rep.create.cube(position=(0, 0, 0), scale=(0.1, 0.1, 0.1), semantics=[("class", "cube")])

        # Create multiple cameras in a grid pattern
        num_cameras = 4
        cameras = []
        for i in range(num_cameras):
            # Position cameras in a 2x2 grid
            x = (i % 2) * 20 - 10  # -10, 10
            y = (i // 2) * 20 - 10  # -10, 10
            cameras.append(rep.create.camera(position=(x, y, 20), look_at=(0, 0, 0)))

        # Create tiled render product
        tile_resolution = (256, 256)
        rp = rep.create.render_product_tiled(cameras=cameras, tile_resolution=tile_resolution)

        # Verify all cameras are attached to the render product
        stage = omni.usd.get_context().get_stage()
        rp_prim = stage.GetPrimAtPath(rp.path)
        self.assertTrue(rp_prim.IsValid(), "Render product prim not found")

        # Get the camera targets from the render product
        camera_targets = rp_prim.GetRelationship("camera").GetTargets()
        self.assertEqual(
            len(camera_targets),
            num_cameras,
            f"Expected {num_cameras} cameras attached to render product, got {len(camera_targets)}",
        )

        # Get bounding box annotator
        bbox_anno = rep.annotators.get("bounding_box_2d_tight_fast")
        rgb_anno = rep.annotators.get("rgb")
        bbox_anno.attach(rp)
        rgb_anno.attach(rp)

        await rep.orchestrator.step_async()

        Image.fromarray(rgb_anno.get_data()).save("rgb.png")
        Image.fromarray(
            rep.writers_default.tools.colorize_bbox_2d(rgb_anno.get_data(), bbox_anno.get_data()["data"])
        ).save("rgb_bbox.png")

        # Get bounding box data
        bbox_data = bbox_anno.get_data()["data"]
        bbox_ids = bbox_anno.get_data()["info"]["bboxIds"]

        # Verify we have the correct number of bounding boxes (one per tile)
        self.assertEqual(len(bbox_data), num_cameras, f"Expected {num_cameras} bounding boxes, got {len(bbox_data)}")

        # Verify each bounding box is in the correct tile
        for i, bbox in enumerate(bbox_data):
            # Calculate expected tile coordinates
            tile_x = (i % 2) * tile_resolution[0]
            tile_y = (i // 2) * tile_resolution[1]

            bbox_id = bbox_ids[i]
            # Bounding box should be within its tile
            self.assertTrue(
                tile_x <= bbox[1] <= tile_x + tile_resolution[0],
                f"Bounding box {bbox_id} x_min coordinate {bbox[1]} not in tile x range [{tile_x}, {tile_x + tile_resolution[0]}]",
            )

            self.assertTrue(
                tile_y <= bbox[2] <= tile_y + tile_resolution[1],
                f"Bounding box {bbox_id} y_min coordinate {bbox[2]} not in tile y range [{tile_y}, {tile_y + tile_resolution[1]}]",
            )

            self.assertTrue(
                tile_x <= bbox[3] <= tile_x + tile_resolution[0],
                f"Bounding box {bbox_id} x_max coordinate {bbox[3]} not in tile x range [{tile_x}, {tile_x + tile_resolution[0]}]",
            )

            self.assertTrue(
                tile_y <= bbox[4] <= tile_y + tile_resolution[1],
                f"Bounding box {bbox_id} y_max coordinate {bbox[4]} not in tile y range [{tile_y}, {tile_y + tile_resolution[1]}]",
            )

        # Verify bounding boxes are not identical (they should be slightly different due to perspective)
        for i in range(len(bbox_data)):
            for j in range(i + 1, len(bbox_data)):
                self.assertFalse(
                    np.array_equal(bbox_data[i], bbox_data[j]),
                    f"Bounding boxes {i} and {j} are identical, but should be different due to perspective",
                )

    async def test_create_single_mesh_decal(self):
        """Test to see if the mesh decal is created and setup properly"""
        diffuse_uv_texture = Path(TEST_DATA_DIR).joinpath("objects", "textures", "nv_uv_grid_D.png").as_posix()
        opactiy_uv_texture = Path(TEST_DATA_DIR).joinpath("objects", "textures", "nv_uv_grid_O.png").as_posix()

        await omni.usd.get_context().new_stage_async()

        stage = omni.usd.get_context().get_stage()

        torus = rep.create.torus()
        sem = [("class", "shape")]
        with torus:
            rep.create.mesh_decal(
                semantics=sem,
                diffuse=diffuse_uv_texture,
                opacity=opactiy_uv_texture,
                position=(50, 30, 25),
                rotation=(-90, 0, 0),
                scale=(0.2, 0.2, 0.2),
            )

        for _ in range(2):
            await rep.orchestrator.step_async()

        # Check structure
        self.assertTrue(
            stage.GetPrimAtPath("/Replicator/Torus_Xform/Torus/Decal/Torus_Xform").IsValid(), "Decal path not correct!"
        )

        decal = stage.GetPrimAtPath("/Replicator/Torus_Xform/Torus/Decal/Torus_Xform")
        self.assertTrue(decal.HasAPI(UsdSemantics.LabelsAPI))

        p_sem = UsdSemantics.LabelsAPI.Get(decal, "class")
        self.assertEquals(p_sem.GetLabelsAttr().Get(), ["shape"])

        # Check material
        self.assertEquals(
            str(UsdShade.MaterialBindingAPI(decal).GetDirectBinding().GetMaterial().GetPath()),
            "/Looks/OmniPBR",
            "Material not created!",
        )

        material_shader = (
            UsdShade.MaterialBindingAPI(decal).GetDirectBinding().GetMaterial().GetPrim().GetChild("Shader")
        )

        self.assertEqual(
            material_shader.GetAttribute("inputs:diffuse_texture").Get().path,
            diffuse_uv_texture,
            "Diffuse texture not correct!",
        )
        self.assertEqual(
            material_shader.GetAttribute("inputs:opacity_texture").Get().path,
            opactiy_uv_texture,
            "Opacity texture not correct!",
        )
        self.assertEqual(material_shader.GetAttribute("inputs:enable_opacity").Get(), True, "Opacity not enabled!")
        self.assertEqual(
            material_shader.GetAttribute("inputs:enable_opacity_texture").Get(), True, "Opacity texture not enabled!"
        )

    async def test_create_single_mesh_decal_image(self):
        """Create the mesh decal and check that it matches a golden image."""
        diffuse_uv_texture = Path(TEST_DATA_DIR).joinpath("objects", "textures", "nv_uv_grid_D.png").as_posix()
        opactiy_uv_texture = Path(TEST_DATA_DIR).joinpath("objects", "textures", "nv_uv_grid_O.png").as_posix()

        await omni.usd.get_context().new_stage_async()

        stage = omni.usd.get_context().get_stage()

        torus = rep.create.torus(position=(370, 375, 370))
        sem = [("class", "shape")]
        with torus:
            rep.create.mesh_decal(
                semantics=sem,
                diffuse=diffuse_uv_texture,
                opacity=opactiy_uv_texture,
                position=(420, 405, 395),
                rotation=(-90, 0, 0),
                scale=(0.2, 0.2, 0.5),
                offset_normal=0.01,
            )

        rgb = rep.annotators.get("rgb")
        render_product = rep.create.render_product("/OmniverseKit_Persp", (1024, 512))
        rgb.attach(render_product)

        for _ in range(2):
            await rep.orchestrator.step_async()

        test_rgb_data = rgb.get_data()

        golden_dir = Path(TEST_DATA_DIR).joinpath("golden").as_posix()
        golden_file_path = Path(golden_dir).joinpath("mesh_decal.png").as_posix()
        golden_image = np.asarray(Image.open(golden_file_path))

        std_dev = np.sqrt(np.square(test_rgb_data - golden_image).astype(float).mean())
        if std_dev > 2:
            tc_show_image("mesh_decal", golden_dir, golden_dir, test_rgb_data)
        self.assertLess(std_dev, 2)

    async def test_create_normalized_mesh_decal(self):
        """Test to see if the mesh decal is created and setup properly using the OgnMeshBoundsDecalPlacement node"""
        # TODO: Implement test
        pass

    async def test_instantiate_with_semantics_scene_instance(self):
        """Instantiate a scene instanced population of cubes with semantics"""
        await omni.usd.get_context().new_stage_async()

        # Setup test
        cube = rep.create.cube(visible=False)

        def rand_props(size):
            instances = rep.randomizer.instantiate(
                cube, size=size, name="scene_inst_sem", mode="scene_instance", semantics=[("class", "cube")]
            )
            with instances:
                rep.modify.pose(
                    position=rep.distribution.uniform((-500, 0, -500), (500, 0, 500)),
                )
            return instances

        rep.randomizer.register(rand_props)

        with rep.trigger.on_frame(max_execs=5):
            rep.randomizer.rand_props(5)

        # Step randomization
        await rep.orchestrator.step_async()

        # Check that population's children has the semantic applied
        stage = omni.usd.get_context().get_stage()

        self.assertTrue(stage.GetPrimAtPath("/Replicator/SampledAssets").IsValid(), "Population was not created!")
        population = stage.GetPrimAtPath("/Replicator/SampledAssets").GetChildren()[0]

        refs = population.GetChildren()

        for r in refs:
            self.assertTrue(r.HasAPI(UsdSemantics.LabelsAPI), f"Prim {r} does not have semantics applied!")
            self.assertEqual(UsdSemantics.LabelsAPI.Get(r, "class").GetLabelsAttr().Get(), ["cube"])

    async def test_instantiate_with_semantics_point_instance(self):
        """Instantiate a point instanced population of cubes with semantics"""
        await omni.usd.get_context().new_stage_async()

        # Setup test
        CUBE = rep.create.cube(visible=False)

        def rand_props(size):
            instances = rep.randomizer.instantiate(
                CUBE, size=size, name="point_inst_sem", mode="point_instance", semantics=[("class", "cube")]
            )
            with instances:
                rep.modify.pose(
                    position=rep.distribution.uniform((-500, 0, -500), (500, 0, 500)),
                )
            return instances.node

        rep.randomizer.register(rand_props)

        with rep.trigger.on_frame(max_execs=5):
            rep.randomizer.rand_props(5)

        # Step randomization
        await rep.orchestrator.step_async()

        # Check that population has the semantic applied
        stage = omni.usd.get_context().get_stage()

        self.assertTrue(stage.GetPrimAtPath("/Replicator/SampledAssets").IsValid(), "Population was not created!")
        population = stage.GetPrimAtPath("/Replicator/SampledAssets").GetChildren()[0]

        refs = population.GetChildren()

        for r in refs:
            self.assertTrue(r.HasAPI(UsdSemantics.LabelsAPI), f"Prim {r} does not have semantics applied!")
            self.assertEqual(UsdSemantics.LabelsAPI.Get(r, "class").GetLabelsAttr().Get(), ["cube"])

    async def test_create_from_replicatoritems(self):
        rep.create.sphere(as_mesh=False)
        rep.create.cube(as_mesh=False)

        with rep.trigger.on_frame():
            sphere = rep.get.prims(prim_types=["Sphere"], cache_result=False)
            cube = rep.get.prims(prim_types=["Cube"], cache_result=False)
            group = rep.create.group([sphere, cube])
            with group:
                rep.modify.pose(position=0)

        await rep.orchestrator.step_async()
        rep.create.sphere(as_mesh=False)
        rep.create.cube(as_mesh=False, count=2)
        await rep.orchestrator.step_async()

        # Assert group was updated to new prim
        self.assertEqual(len(group.get_output("prims")), 5)

    async def test_create_list_attr(self):
        # Test for an attribute set as a list instead of a tuple
        rep.create.camera(
            None,
            None,
            None,
            clipping_range=[2.0, 3.0],
        )

        stage = omni.usd.get_context().get_stage()
        cam_xform = stage.GetPrimAtPath("/Replicator/Camera_Xform")
        cam = cam_xform.GetChild("Camera")
        self.assertTrue(cam.GetAttribute("clippingRange").Get(), (2.0, 3.0))

    @unittest.skipIf(
        omni.kit.test.utils.is_running_in_teamcity() or omni.kit.test.utils.is_running_in_gitlab(),
        "localhost not available on CI",
    )
    async def test_create_from_usd(self):
        # await omni.kit.app.get_app().next_update_async()
        with self.assertRaises(FileNotFoundError):
            rep.create.from_usd("omniverse://localhost/this_file/does_not_exist.usd")

        with self.assertRaises(ValueError):
            rep.create.from_usd("omniverse://localhost/not_a_usd_extension.obj")

        rep.create.from_usd(Path(TEST_DATA_DIR).joinpath("objects/rocket.usd").as_posix())
        stage = omni.usd.get_context().get_stage()
        self.assertTrue(
            stage.GetPrimAtPath("/Replicator/Ref_Xform/Ref/Sphere_000_Sphere_003/Sphere_000_Sphere_003").IsValid()
        )

    async def test_create_omni_lidar(self):
        """Test creating an omni lidar with various parameters"""
        # Test with default parameters
        rep.create.omni_lidar(
            position=(0, 0, 0),
            rotation=(0, 0, 0),
        )

        stage = omni.usd.get_context().get_stage()
        lidar_xform = stage.GetPrimAtPath("/Replicator/OmniLidar_Xform")
        lidar = lidar_xform.GetChild("OmniLidar")

        # Verify the LiDAR prim was created
        self.assertTrue(lidar.IsValid(), "LiDAR prim was not created")

        # Verify the core API is applied
        self.assertTrue(lidar.HasAPI("OmniSensorGenericLidarCoreAPI"), "Core API was not applied to LiDAR")

        # Test with multiple parameters
        rep.create.omni_lidar(
            position=(10, 20, 30),
            rotation=(45, 0, 0),
        )

        await omni.kit.app.get_app().next_update_async()
        stage = omni.usd.get_context().get_stage()

        # Verify position and rotation were set correctly
        lidar_xform = stage.GetPrimAtPath("/Replicator/OmniLidar_Xform_01")
        self.assertTrue(lidar_xform.IsValid(), "Second LiDAR prim was not created")

        lidar = lidar_xform.GetChild("OmniLidar")
        self.assertTrue(
            lidar.HasAPI("OmniSensorGenericLidarCoreAPI"), "OmniSensor Lidar API was not applied to second LiDAR"
        )

        # Verify the position and rotation were set correctly
        position = np.array(lidar_xform.GetAttribute("xformOp:translate").Get())
        np.testing.assert_allclose(
            position, np.array((10.0, 20.0, 30.0)), atol=1e-3, err_msg="LiDAR position was not set correctly"
        )

        rotation = np.array(lidar_xform.GetAttribute("xformOp:rotateXYZ").Get())
        np.testing.assert_allclose(
            rotation, np.array((45.0, 0.0, 0.0)), atol=1e-3, err_msg="LiDAR rotation was not set correctly"
        )

        # Test with emitter states
        states = {
            "omni:sensor:Core:emitterState:s001:azimuthDeg": [-1.0, 2.0],
            "omni:sensor:Core:emitterState:s002:focalSlope": [-1.0, 2.0],
            "omni:sensor:Core:auxOutputType": "PointCloud",
        }
        rep.create.omni_lidar(
            position=(0, 0, 0),
            rotation=(0, 0, 0),
            **states,
        )

        await omni.kit.app.get_app().next_update_async()
        stage = omni.usd.get_context().get_stage()

        lidar_xform = stage.GetPrimAtPath("/Replicator/OmniLidar_Xform_02")
        lidar = lidar_xform.GetChild("OmniLidar")

        # Verify the core API and emitter state APIs are applied
        self.assertTrue(
            lidar.HasAPI("OmniSensorGenericLidarCoreAPI"), "Core API was not applied to LiDAR with emitter states"
        )
        self.assertTrue(
            "OmniSensorGenericLidarCoreEmitterStateAPI:s002" in lidar.GetAppliedSchemas(),
            "Emitter state schema s002 was not applied",
        )

        for k, v in states.items():
            self.assertEqual(lidar.GetAttribute(k).Get(), v)

    async def test_create_omni_radar(self):
        """Test creating an omni radar with various parameters"""
        # Test with default parameters
        rep.create.omni_radar(
            position=(0, 0, 0),
            rotation=(0, 0, 0),
        )

        stage = omni.usd.get_context().get_stage()
        radar_xform = stage.GetPrimAtPath("/Replicator/OmniRadar_Xform")
        radar = radar_xform.GetChild("OmniRadar")

        # Verify the Radar prim was created
        self.assertTrue(radar.IsValid(), "Radar prim was not created")

        # Verify the core API is applied
        self.assertTrue(
            radar.HasAPI("OmniSensorGenericRadarWpmDmatAPI"), "OmniSensor Radar API was not applied to Radar"
        )

        # Test with multiple parameters
        radar_item = rep.create.omni_radar(
            position=(10, 20, 30),
            rotation=(45, 0, 0),
        )

        await omni.kit.app.get_app().next_update_async()
        stage = omni.usd.get_context().get_stage()

        # Verify position and rotation were set correctly
        radar_xform = stage.GetPrimAtPath("/Replicator/OmniRadar_Xform_01")
        self.assertTrue(radar_xform.IsValid(), "Second Radar prim was not created")

        radar = radar_xform.GetChild("OmniRadar")
        self.assertTrue(radar.HasAPI("OmniSensorGenericRadarWpmDmatAPI"), "Core API was not applied to second Radar")

        # Verify the position and rotation were set correctly
        position = np.array(radar_xform.GetAttribute("xformOp:translate").Get())
        np.testing.assert_allclose(
            position, np.array((10.0, 20.0, 30.0)), atol=1e-3, err_msg="Radar position was not set correctly"
        )

        rotation = np.array(radar_xform.GetAttribute("xformOp:rotateXYZ").Get())
        np.testing.assert_allclose(
            rotation, np.array((45.0, 0.0, 0.0)), atol=1e-3, err_msg="Radar rotation was not set correctly"
        )

        # Test with emitter states
        states = {
            "omni:sensor:WpmDmat:auxOutputType": "PointCloud",
            "omni:sensor:WpmDmat:scan:s001:rBins": 10,
            "omni:sensor:WpmDmat:scan:s002:raysPerDeg": 10,
        }
        rep.create.omni_radar(
            position=(0, 0, 0),
            rotation=(0, 0, 0),
            **states,
        )

        await omni.kit.app.get_app().next_update_async()
        stage = omni.usd.get_context().get_stage()

        radar_xform = stage.GetPrimAtPath("/Replicator/OmniRadar_Xform_02")
        radar = radar_xform.GetChild("OmniRadar")

        # Verify the core API and emitter state APIs are applied
        self.assertTrue(
            radar.HasAPI("OmniSensorGenericRadarWpmDmatAPI"), "Core API was not applied to Radar with emitter states"
        )
        self.assertTrue(
            "OmniSensorGenericRadarWpmDmatScanCfgAPI:s002" in radar.GetAppliedSchemas(),
            f"Emitter state schema s002 was not applied, {radar.GetAppliedSchemas()}",
        )

        for k, v in states.items():
            self.assertEqual(radar.GetAttribute(k).Get(), v)

    async def test_create_render_product_with_render_vars(self):
        """Test creating a render product with custom render variables"""
        custom_render_vars = ["HdrColor", "Normal"]

        # Create a camera
        camera = rep.create.camera(position=(0, 0, 0), rotation=(0, 0, 0))

        # Create a render product with custom render variables
        rp = rep.create.render_product(camera=camera, resolution=(1024, 1024), render_vars=custom_render_vars)

        await omni.kit.app.get_app().next_update_async()
        stage = omni.usd.get_context().get_stage()

        # Verify the render variables were created
        render_vars_path = "/Render/Vars"
        self.assertTrue(stage.GetPrimAtPath(render_vars_path).IsValid(), "Render/Vars path was not created")

        # Check render vars were created
        for render_var in custom_render_vars:
            render_var_path = Sdf.Path(f"{render_vars_path}/{render_var}")
            self.assertTrue(stage.GetPrimAtPath(render_var_path).IsValid(), f"{render_var} render var was not created")

            # Verify the render var attributes
            render_var_prim = stage.GetPrimAtPath(render_var_path)
            self.assertEqual(
                render_var_prim.GetAttribute("sourceName").Get(),
                render_var,
                "Render var sourceName is not set correctly",
            )

            # Verify rendervar is attached to the render product
            rp_prim = stage.GetPrimAtPath(rp.path)
            rp_render_vars = rp_prim.GetRelationship("orderedVars").GetTargets()
            self.assertTrue(
                render_var_path in rp_render_vars,
                f"{render_var_path} was not attached to the render product with targets: {rp_render_vars}",
            )

        # TODO: Add back in once renderer can return a list of valid render vars
        # Test with invalid render var
        # with self.assertRaises(ValueError):
        #     rep.create.render_product(camera=camera, resolution=(1024, 1024), render_vars=["InvalidRenderVar"])

    @unittest.skip("Skip Omni Sensors, failing to find plugin")
    async def test_create_render_product_with_omni_sensor(self):
        # Test OmniLidar with no render_vars (should create GenericModelOutput by default)
        await omni.usd.get_context().new_stage_async()
        lidar = rep.create.omni_lidar(position=(0, 0, 0), rotation=(0, 0, 0))
        render_product = rep.create.render_product(lidar, resolution=(1024, 1024))

        await omni.kit.app.get_app().next_update_async()
        stage = omni.usd.get_context().get_stage()

        # Verify GenericModelOutput was created by default
        render_vars_path = "/Render/Vars"
        generic_model_output_path = f"{render_vars_path}/GenericModelOutput"
        self.assertTrue(
            stage.GetPrimAtPath(generic_model_output_path).IsValid(),
            "GenericModelOutput render var was not created for OmniLidar by default",
        )

        # Test OmniRadar with no render_vars (should create GenericModelOutput by default)
        await omni.usd.get_context().new_stage_async()
        radar = rep.create.omni_radar(position=(0, 0, 0), rotation=(0, 0, 0))
        render_product = rep.create.render_product(radar, resolution=(1024, 1024))

        await omni.kit.app.get_app().next_update_async()
        stage = omni.usd.get_context().get_stage()

        # Verify GenericModelOutput was created by default
        generic_model_output_path = f"{render_vars_path}/GenericModelOutput"
        self.assertTrue(
            stage.GetPrimAtPath(generic_model_output_path).IsValid(),
            "GenericModelOutput render var was not created for OmniRadar by default",
        )

        # Test with only RtxSensorMetadata render var
        await omni.usd.get_context().new_stage_async()
        lidar = rep.create.omni_lidar(position=(0, 0, 0), rotation=(0, 0, 0))
        render_product = rep.create.render_product(lidar, resolution=(1024, 1024), render_vars=["RtxSensorMetadata"])

        await omni.kit.app.get_app().next_update_async()
        stage = omni.usd.get_context().get_stage()

        # Verify only RtxSensorMetadata was created
        metadata_path = f"{render_vars_path}/RtxSensorMetadata"
        self.assertTrue(
            stage.GetPrimAtPath(metadata_path).IsValid(), "RtxSensorMetadata render var was not created when specified"
        )
        self.assertFalse(
            stage.GetPrimAtPath(f"{render_vars_path}/GenericModelOutput").IsValid(),
            "GenericModelOutput should not be created when only RtxSensorMetadata is specified",
        )
