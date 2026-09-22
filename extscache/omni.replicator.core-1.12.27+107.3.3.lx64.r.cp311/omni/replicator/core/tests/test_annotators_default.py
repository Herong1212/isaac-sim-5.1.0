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

import os
import sys
import unittest

import carb
import imageio
import numpy as np
import omni.kit
import omni.replicator.core as rep
import warp as wp
from omni.hydra.engine.stats import get_device_info
from omni.replicator.core.modify import semantics
from PIL import Image
from pxr import Gf, Sdf

TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")
AOVS_RT = [
    "LdrColor",
    "HdrColor",
    "SmoothNormal",
    # "BumpNormal",
    "AmbientOcclusion",
    "Motion2d",
    # "DiffuseAlbedo",
    # "SpecularAlbedo",
    "Roughness",
    # "DirectDiffuse",
    # "DirectSpecular",
    # "Reflections",    # FIXME: Fails when testing
    # "IndirectDiffuse",    # FIXME: Fails when testing
    "DepthLinearized",
    # "EmissionAndForegroundMask",
]
AOVS_PT = [
    "PtDirectIllumation",
    "PtGlobalIllumination",
    "PtReflections",
    "PtRefractions",
    "PtSelfIllumination",
    "PtBackground",
    "PtWorldNormal",
    "PtWorldPos",
    "PtZDepth",
    "PtVolumes",
    "PtDiffuseFilter",
    "PtReflectionFilter",
    "PtRefractionFilter",
]  # , "PtMultiMatte0", "PtMultiMatte1", "PtMultiMatte2",
# 		           "PtMultiMatte3", "PtMultiMatte4", "PtMultiMatte5", "PtMultiMatte6"]


def create_test_scene():
    red_diffuse = rep.create.material_omnipbr(diffuse=(1, 0, 0.2), roughness=1.0)
    metallic_reflective = rep.create.material_omnipbr(roughness=0.01, metallic=1.0)
    glow = rep.create.material_omnipbr(emissive_color=(1.0, 0.5, 0.4), emissive_intensity=100000.0)
    rep.create.cone(material=metallic_reflective)
    rep.create.cube(position=(100, 50, -100), material=red_diffuse)
    rep.create.sphere(position=(-100, 50, 100), material=glow)
    rep.create.plane(scale=(100, 1, 100), position=(0, -50, 0))


class TestAnnotatorsDefault(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        await omni.kit.app.get_app().next_update_async()
        self.render_product = rep.create.render_product("/OmniverseKit_Persp", (512, 256))

    async def tearDown(self):
        # Disable reading and writing render settings to USD and Fabric (enabling results in some tests crashing)
        carb.settings.get_settings().set("/app/hydra/renderSettings/useUsdAttributes", False)
        carb.settings.get_settings().set("/app/hydra/renderSettings/useFabricAttributes", False)
        await omni.usd.get_context().new_stage_async()

    def _disable_render_settings_rtx_extension(self):
        ext_manager = omni.kit.app.get_app().get_extension_manager()
        ext_manager.set_extension_enabled("omni.usd.schema.render_settings.rtx", False)

    async def test_aovs_rt_cuda(self):
        DEVICE = "cuda:0"

        create_test_scene()

        rep.settings.set_render_rtx_realtime(antialiasing="DLAA")
        rep.settings.carb_settings("/rtx/indirectDiffuse/enabled", True)
        rep.settings.carb_settings("/rtx/sceneDb/ambientLightIntensity", 0.0)
        rep.settings.carb_settings("/rtx-transient/post/aa/limitedOps", False)

        annos = {}
        for aov in AOVS_RT:
            anno = rep.annotators.get(aov, device=DEVICE)
            anno.attach(self.render_product)
            annos[aov] = anno

        await rep.orchestrator.step_async(rt_subframes=10)

        golden_data_dir = os.path.join(TEST_DATA_DIR, "aovs")
        golden_filepath = os.path.join(golden_data_dir, "golden_rt_aovs.npz")
        golden_rt_aovs = np.load(golden_filepath)

        for aov, anno in annos.items():
            print("AOV", aov)
            data = anno.get_data()
            if data.shape[0] == 0:
                continue
            if not aov in golden_rt_aovs:
                golden_rt_aovs[aov] = data.numpy()
            golden_data = golden_rt_aovs[aov]
            rep.functional.io_functions.write_exr(os.path.join(golden_data_dir, f"COINCOIN_{aov}_rt_cuda.exr"), data)
            std_dev = np.sqrt(np.square(data.numpy().squeeze() - golden_data).astype(float).mean())
            if std_dev > 20:
                rep.functional.io_functions.write_exr(os.path.join(golden_data_dir, f"FAIL_{aov}_rt_cuda.exr"), data)
                rep.functional.io_functions.write_exr(
                    os.path.join(golden_data_dir, f"FAILDIFF_{aov}_rt_cuda.exr"), data - golden_data
                )
            self.assertLess(std_dev, 20, f"AOV {aov} on device {DEVICE} does not match golden file")

        # Uncomment to update goldens
        # np.savez(golden_filepath, **golden_rt_aovs)

    # @unittest.skipIf(len(get_device_info()) > 0, "Test is flaky on MGPU systems")
    async def test_aovs_pt_cuda(self):
        DEVICE = "cuda:0"

        create_test_scene()

        rep.settings.set_render_pathtraced()

        annos = {}
        for aov in AOVS_PT:
            anno = rep.annotators.get(aov, device=DEVICE)
            anno.attach(self.render_product)
            annos[aov] = anno

        await rep.orchestrator.step_async()

        golden_data_dir = os.path.join(TEST_DATA_DIR, "aovs")
        golden_filepath = os.path.join(golden_data_dir, "golden_pt_aovs.npz")
        golden_pt_aovs = np.load(golden_filepath)

        for aov, anno in annos.items():
            print("AOV", aov)
            data = anno.get_data()
            if data.shape[0] == 0:
                continue
            if not aov in golden_pt_aovs:
                golden_pt_aovs[aov] = data.numpy()
            golden_data = golden_pt_aovs[aov]
            std_dev = np.sqrt(np.square(data.numpy() - golden_data).astype(float).mean())
            if std_dev > 20:
                rep.functional.io_functions.write_exr(os.path.join(golden_data_dir, f"FAIL_{aov}_pt_cuda.exr"), data)
                rep.functional.io_functions.write_exr(
                    os.path.join(golden_data_dir, f"FAILDIFF_{aov}_pt_cuda.exr"), data - golden_data
                )
            self.assertLess(std_dev, 20, f"AOV {aov} on device {DEVICE} does not match golden file")

        # Uncomment to update goldens
        # np.savez(golden_filepath, **golden_pt_aovs)

    async def test_aovs_rt_cpu(self):
        DEVICE = "cpu"

        create_test_scene()

        rep.settings.set_render_rtx_realtime(antialiasing="DLAA")
        rep.settings.carb_settings("/rtx/indirectDiffuse/enabled", True)
        rep.settings.carb_settings("/rtx/sceneDb/ambientLightIntensity", 0.0)
        rep.settings.carb_settings("/rtx-transient/post/aa/limitedOps", False)

        annos = {}
        for aov in AOVS_RT:
            anno = rep.annotators.get(aov, device=DEVICE)
            anno.attach(self.render_product)
            annos[aov] = anno

        await rep.orchestrator.step_async(rt_subframes=10)

        golden_data_dir = os.path.join(TEST_DATA_DIR, "aovs")
        golden_filepath = os.path.join(golden_data_dir, "golden_rt_aovs.npz")
        golden_rt_aovs = np.load(golden_filepath)

        for aov, anno in annos.items():
            print("AOV", aov)
            data = anno.get_data()
            data = np.nan_to_num(data, 0.0)
            self.assertTrue(data is not None or data.shape[0] == 0, f"Data for aov {aov} is invalid")
            if not aov in golden_rt_aovs:
                golden_rt_aovs[aov] = data.numpy()
            golden_data = golden_rt_aovs[aov]
            std_dev = np.sqrt(np.square(data - golden_data).astype(float).mean())
            if std_dev > 20:
                rep.functional.io_functions.write_exr(os.path.join(golden_data_dir, f"FAIL_{aov}_rt_cpu.exr"), data)
                rep.functional.io_functions.write_exr(
                    os.path.join(golden_data_dir, f"FAILDIFF_{aov}_rt_cpu.exr"), data - golden_data
                )
            self.assertLess(std_dev, 20, f"AOV {aov} on device {DEVICE} does not match golden file")

        # Uncomment to update goldens
        # np.savez(golden_filepath, **golden_rt_aovs)

    async def test_aovs_pt_cpu(self):
        DEVICE = "cpu"

        create_test_scene()

        rep.settings.set_render_pathtraced()

        annos = {}
        for aov in AOVS_PT:
            anno = rep.annotators.get(aov, device=DEVICE)
            anno.attach(self.render_product)
            annos[aov] = anno

        await rep.orchestrator.step_async()

        golden_data_dir = os.path.join(TEST_DATA_DIR, "aovs")
        golden_filepath = os.path.join(golden_data_dir, "golden_pt_aovs.npz")
        golden_pt_aovs = np.load(golden_filepath)

        for aov, anno in annos.items():
            print("AOV", aov)
            data = anno.get_data()
            data = np.nan_to_num(data, 0.0)
            self.assertTrue(data is not None or data.shape[0] == 0, f"Data for aov {aov} is invalid")
            if not aov in golden_pt_aovs:
                golden_pt_aovs[aov] = data.numpy()
            golden_data = golden_pt_aovs[aov]
            std_dev = np.sqrt(np.square(data - golden_data).astype(float).mean())
            if std_dev > 20:
                rep.functional.io_functions.write_exr(os.path.join(golden_data_dir, f"FAIL_{aov}_pt_cpu.exr"), data)
                rep.functional.io_functions.write_exr(
                    os.path.join(golden_data_dir, f"FAILDIFF_{aov}_pt_cpu.exr"), data - golden_data
                )
            self.assertLess(std_dev, 20, f"AOV {aov} on device {DEVICE} does not match golden file")

        # Uncomment to update goldens
        # np.savez(golden_filepath, **golden_pt_aovs)

    async def test_bbox_occlusion_two_children(self):
        cube = rep.create.cube(position=(0, 50, 100))
        sphere = rep.create.sphere(position=(-100, 50, 100))

        stage = omni.usd.get_context().get_stage()
        parent = stage.DefinePrim("/Parent", "Xform")
        rep.functional.modify.semantics(parent, [("class", "parent_class")])

        # Create hierarchical semantics
        omni.kit.commands.create(
            "MovePrim", path_from="/Replicator/Cube_Xform", path_to="/Parent/Cube_Xform"
        ).do()  # executing command without undo to avoid bug https://jirasw.nvidia.com/browse/OMPE-14264
        cube.set_input("primsIn", ["/Parent/Cube_Xform"])
        omni.kit.commands.create(
            "MovePrim", path_from="/Replicator/Sphere_Xform", path_to="/Parent/Sphere_Xform"
        ).do()  # executing command without undo to avoid bug https://jirasw.nvidia.com/browse/OMPE-14264
        sphere.set_input("primsIn", ["/Parent/Sphere_Xform"])

        render_product = rep.create.render_product("/OmniverseKit_Persp", (512, 256))

        bbox_3d_anno = rep.annotators.get("bounding_box_3d")
        bbox_3d_anno.attach(render_product)

        await rep.orchestrator.step_async()

        bbox_data = bbox_3d_anno.get_data()
        occlusion = {
            path: bbox_data["data"][i]["occlusionRatio"] for i, path in enumerate(bbox_data["info"]["primPaths"])
        }

        self.assertEqual(bbox_data["info"]["primPaths"], ["/Parent"], "Occlusion should only contains /Parent.")
        np.testing.assert_allclose(
            occlusion["/Parent"], -1.0, err_msg=f"Occlusion ratio of parent should be -1.0, got {occlusion}."
        )

    async def test_bbox_occlusion_one_child(self):
        cube = rep.create.cube(position=(0, 50, 100))

        stage = omni.usd.get_context().get_stage()
        parent = stage.DefinePrim("/Parent", "Xform")
        rep.functional.modify.semantics(parent, [("class", "parent_class")])

        # Create hierarchical semantics
        omni.kit.commands.create(
            "MovePrim", path_from="/Replicator/Cube_Xform", path_to="/Parent/Cube_Xform"
        ).do()  # executing command without undo to avoid bug https://jirasw.nvidia.com/browse/OMPE-14264
        cube.set_input("primsIn", ["/Parent/Cube_Xform"])

        render_product = rep.create.render_product("/OmniverseKit_Persp", (512, 256))

        bbox_3d_anno = rep.annotators.get("bounding_box_3d")
        bbox_3d_anno.attach(render_product)

        await rep.orchestrator.step_async()

        bbox_data = bbox_3d_anno.get_data()
        occlusion = {
            path: bbox_data["data"][i]["occlusionRatio"] for i, path in enumerate(bbox_data["info"]["primPaths"])
        }

        self.assertEqual(bbox_data["info"]["primPaths"], ["/Parent"], f"Occluion should only contains /Parent.")
        np.testing.assert_allclose(
            occlusion["/Parent"], 0.0, err_msg=f"Occlusion ratio of parent should be 0.0, got {occlusion}."
        )

    async def test_bbox_occlusion_one_child_semantic(self):
        rep.create.cube(position=(0, 50, 100))
        sphere = rep.create.sphere(position=(-100, 50, 100), semantics=[("class", "sphere")])

        stage = omni.usd.get_context().get_stage()
        parent = stage.DefinePrim("/Parent", "Xform")
        rep.functional.modify.semantics(parent, [("class", "parent_class")])

        # Create hierarchical semantics
        omni.kit.commands.create(
            "MovePrim", path_from="/Replicator/Sphere_Xform", path_to="/Parent/Sphere_Xform"
        ).do()  # executing command without undo to avoid bug https://jirasw.nvidia.com/browse/OMPE-14264
        sphere.set_input("primsIn", ["/Parent/Sphere_Xform"])

        render_product = rep.create.render_product("/OmniverseKit_Persp", (512, 256))

        bbox_3d_anno = rep.annotators.get("bounding_box_3d")
        bbox_3d_anno.attach(render_product)

        render_product = rep.create.render_product("/OmniverseKit_Persp", (512, 256))

        bbox_3d_anno = rep.annotators.get("bounding_box_3d")
        bbox_3d_anno.attach(render_product)

        await rep.orchestrator.step_async()

        bbox_data = bbox_3d_anno.get_data()
        occlusion = {
            path: bbox_data["data"][i]["occlusionRatio"] for i, path in enumerate(bbox_data["info"]["primPaths"])
        }

        self.assertEqual(
            bbox_data["info"]["primPaths"],
            ["/Parent", "/Parent/Sphere_Xform"],
            f"Occluion should contains /Parent and /Parent/Sphere_Xform.",
        )

        parent_occlusion_ratio = occlusion["/Parent"]
        np.testing.assert_allclose(
            parent_occlusion_ratio,
            0.47759998,
            err_msg=f"Occlusion ratio of parent should be 0.47759998,, got {parent_occlusion_ratio}.",
        )

        sphere_occlusion_ratio = occlusion["/Parent/Sphere_Xform"]
        np.testing.assert_allclose(
            occlusion["/Parent/Sphere_Xform"],
            0.47759998,
            err_msg=f"Occlusion ratio of sphere should be 0.47759998, got {sphere_occlusion_ratio}.",
        )

    async def test_reference_time(self):
        anno = rep.annotators.get("ReferenceTime")
        anno.attach(self.render_product)

        await rep.orchestrator.step_async()

        reference_time = anno.get_data()
        self.assertNotEqual(reference_time["referenceTimeDenominator"], 0.0, "Reference time denominator value was 0.0")
        self.assertNotEqual(reference_time["referenceTimeNumerator"], 0.0, "Reference time numerator value was 0.0")
        self.assertNotEqual(
            reference_time["referenceTimeNumerator"],
            reference_time["referenceTimeDenominator"],
            f"Reference time denominator has the same value as numerator ({reference_time['referenceTimeDenominator']}, {reference_time['referenceTimeNumerator']})",
        )

    @unittest.skipIf(os.getenv("ETM_ACTIVE"), "Test produces a warp on Windows when running on CI")
    async def test_pointcloud_segmentation_dtype(self):
        # Create more than 255 prims/semantics
        cubes = rep.create.cube(
            count=300,
            position=rep.distribution.uniform((-200, 0, -500), (200, 200, 200)),
            scale=0.1,
        )
        cube_prims = cubes.get_output_prims()["prims"]
        for i in range(300):
            cube_prim = cube_prims[i]
            rep.functional.modify.semantics(cube_prim, [("class", f"cube{i}")])

        rp = rep.create.render_product("/OmniverseKit_Persp", (1024, 1024))
        pc_anno = rep.annotators.get("pointcloud")
        pc_anno.attach(rp)

        await rep.orchestrator.step_async()

        data = pc_anno.get_data()["info"]

        self.assertGreater(data["pointSemantic"].max(), 255)
        self.assertEqual(data["pointSemantic"].dtype, np.uint32)

        self.assertGreater(data["pointInstance"].max(), 255)
        self.assertEqual(data["pointInstance"].dtype, np.uint32)

    @unittest.skipIf(not sys.platform.startswith("win"), "Test only applies to direct x")
    async def test_pointcloud_win_valid(self):
        # Check against buffersize issue that occurs on windows
        cubes = rep.create.cube(
            scale=1000,
        )
        cube_prim = cubes.get_output_prims()["prims"]

        rp = rep.create.render_product("/OmniverseKit_Persp", (10, 10))
        pc_anno = rep.annotators.get("pointcloud", init_params={"includeUnlabelled": True})
        pc_anno.attach(rp)

        await rep.orchestrator.step_async()

        data = pc_anno.get_data()

        self.assertEqual(data["data"].shape, (10 * 10, 3))
        self.assertEqual(data["info"]["pointSemantic"].dtype, np.uint32)
        self.assertEqual(data["info"]["pointInstance"].dtype, np.uint32)

    async def test_fabric_reader_display_color(self):
        cube1 = rep.create.cube()
        cube2 = rep.create.cube()

        stage = omni.usd.get_context().get_stage()

        cube_prim_path = "/Replicator/Cube_Xform/Cube"
        stage.GetPrimAtPath(cube_prim_path).GetAttribute("primvars:displayColor").Set([(0, 0, 255)])

        cube_prim_path_2 = "/Replicator/Cube_Xform_01/Cube"
        stage.GetPrimAtPath(cube_prim_path_2).GetAttribute("primvars:displayColor").Set([(255, 0, 0)])

        await omni.kit.app.get_app().next_update_async()

        rp = rep.create.render_product("/OmniverseKit_Persp", (1024, 1024))
        fabric_reader_anno = rep.annotators.get(
            "Attribute",
            init_params={
                "prims": ["/Replicator/Cube_Xform/Cube", "/Replicator/Cube_Xform_01/Cube"],
                "attribute": "primvars:displayColor",
            },
        )

        fabric_reader_anno.attach(rp)
        await rep.orchestrator.step_async()
        sensor_data = fabric_reader_anno.get_data()

        np.testing.assert_array_almost_equal(sensor_data, np.array([0.0, 0.0, 255.0, 255.0, 0, 0]))

    @unittest.skipIf(os.getenv("ETM_ACTIVE"), "skipped in ETM, test takes too long on Windows CI")
    async def test_fabric_reader_size(self):
        cube1 = rep.create.cube(as_mesh=False)
        cube2 = rep.create.cube(as_mesh=False)

        stage = omni.usd.get_context().get_stage()

        cube_prim_path = "/Replicator/Cube_Xform/Cube"
        cube_prim = stage.GetPrimAtPath(cube_prim_path)

        cube_prim.GetAttribute("size").Set(1000)

        cube_prim_path_2 = "/Replicator/Cube_Xform_01/Cube"
        cube_prim_2 = stage.GetPrimAtPath(cube_prim_path_2)

        cube_prim_2.GetAttribute("size").Set(50)

        await omni.kit.app.get_app().next_update_async()

        rp = rep.create.render_product("/OmniverseKit_Persp", (1024, 1024))
        fabric_reader_anno = rep.annotators.get(
            "Attribute",
            init_params={
                "prims": [cube_prim_path, cube_prim_path_2],
                "attribute": "size",
            },
        )

        fabric_reader_anno.attach(rp)
        await rep.orchestrator.step_async()
        sensor_data = fabric_reader_anno.get_data()

        np.testing.assert_array_almost_equal(sensor_data, np.array([1000.0, 50.0]))

    async def test_fabric_reader_int(self):
        """Test int, int[], int2, int2[], int3, int3[]"""

        cube1 = rep.create.cube(as_mesh=False)
        cube2 = rep.create.cube(as_mesh=False)
        cube_prim_path = "/Replicator/Cube_Xform/Cube"
        cube_prim_path_2 = "/Replicator/Cube_Xform_01/Cube"

        values = {
            "int": (Sdf.ValueTypeNames.Int, 12),
            "intArr": (Sdf.ValueTypeNames.IntArray, [12, 56, 50, 390, -31]),
            "int2": (Sdf.ValueTypeNames.Int2, Gf.Vec2i(12, 56)),
            "int2Arr": (Sdf.ValueTypeNames.Int2Array, [Gf.Vec2i(12, 56), Gf.Vec2i(56, 12)]),
            "int3": (Sdf.ValueTypeNames.Int3, Gf.Vec3i(12, 56, 90)),
            "int3Arr": (Sdf.ValueTypeNames.Int3Array, [Gf.Vec3i(12, 56, 90), Gf.Vec3i(90, 56, 12)]),
        }

        for path in [cube_prim_path, cube_prim_path_2]:
            stage = omni.usd.get_context().get_stage()
            cube_prim = stage.GetPrimAtPath(path)
            for name, (dtype, value) in values.items():
                cube_prim.CreateAttribute(name, dtype).Set(value)

        await omni.kit.app.get_app().next_update_async()

        rp = rep.create.render_product("/OmniverseKit_Persp", (1024, 1024))

        expected_values = {
            "int": [12, 12],
            "intArr": [12, 56, 50, 390, -31] * 2,
            "int2": [12, 56] * 2,
            "int2Arr": [12, 56, 56, 12] * 2,
            "int3": [12, 56, 90] * 2,
            "int3Arr": [12, 56, 90, 90, 56, 12] * 2,
        }

        fabric_reader_annos = []
        for name in values:
            fabric_reader_anno = rep.annotators.get(
                "Attribute",
                init_params={
                    "prims": [cube_prim_path, cube_prim_path_2],
                    "attribute": name,
                },
            )
            fabric_reader_anno.attach(rp)
            fabric_reader_annos.append(fabric_reader_anno)

        await rep.orchestrator.step_async()

        for name, fabric_reader_anno in zip(expected_values, fabric_reader_annos):
            sensor_data = fabric_reader_anno.get_data()
            np.testing.assert_array_almost_equal(sensor_data, expected_values[name], decimal=3)

    async def test_fabric_reader_float(self):
        """Test float, float[], float2, float2[], float3, float3[]"""

        cube1 = rep.create.cube(as_mesh=False)
        cube2 = rep.create.cube(as_mesh=False)
        cube_prim_path = "/Replicator/Cube_Xform/Cube"
        cube_prim_path_2 = "/Replicator/Cube_Xform_01/Cube"

        values = {
            "float": (Sdf.ValueTypeNames.Float, 12.34),
            "floatArr": (Sdf.ValueTypeNames.FloatArray, [12.34, 56.78, 50.13, 390.1, -31.2]),
            "float2": (Sdf.ValueTypeNames.Float2, (12.34, 56.78)),
            "float2Arr": (Sdf.ValueTypeNames.Float2Array, [(12.34, 56.78), (56.78, 12.34)]),
            "float3": (Sdf.ValueTypeNames.Float3, (12.34, 56.78, 90.12)),
            "float3Arr": (Sdf.ValueTypeNames.Float3Array, [(12.34, 56.78, 90.12), (90.12, 56.78, 12.34)]),
        }

        for path in [cube_prim_path, cube_prim_path_2]:
            stage = omni.usd.get_context().get_stage()
            cube_prim = stage.GetPrimAtPath(path)
            for name, (dtype, value) in values.items():
                cube_prim.CreateAttribute(name, dtype).Set(value)

        await omni.kit.app.get_app().next_update_async()

        rp = rep.create.render_product("/OmniverseKit_Persp", (1024, 1024))

        expected_values = {
            "float": [12.34, 12.34],
            "floatArr": [12.34, 56.78, 50.13, 390.1, -31.2] * 2,
            "float2": [12.34, 56.78] * 2,
            "float2Arr": [12.34, 56.78, 56.78, 12.34] * 2,
            "float3": [12.34, 56.78, 90.12] * 2,
            "float3Arr": [12.34, 56.78, 90.12, 90.12, 56.78, 12.34] * 2,
        }

        fabric_reader_annos = []
        for name in values:
            fabric_reader_anno = rep.annotators.get(
                "Attribute",
                init_params={
                    "prims": [cube_prim_path, cube_prim_path_2],
                    "attribute": name,
                },
            )
            fabric_reader_anno.attach(rp)
            fabric_reader_annos.append(fabric_reader_anno)

        await rep.orchestrator.step_async()

        for name, fabric_reader_anno in zip(expected_values, fabric_reader_annos):
            sensor_data = fabric_reader_anno.get_data()
            np.testing.assert_array_almost_equal(sensor_data, expected_values[name], decimal=3)

    async def test_fabric_reader_double(self):
        """Test double, double[], double2, double2[], double3, double3[]"""

        cube1 = rep.create.cube(as_mesh=False)
        cube2 = rep.create.cube(as_mesh=False)
        cube_prim_path = "/Replicator/Cube_Xform/Cube"
        cube_prim_path_2 = "/Replicator/Cube_Xform_01/Cube"

        values = {
            "double": (Sdf.ValueTypeNames.Double, 12.34),
            "doubleArr": (Sdf.ValueTypeNames.DoubleArray, [12.34, 56.78, 50.13, 390.1, -31.2]),
            "double2": (Sdf.ValueTypeNames.Double2, (12.34, 56.78)),
            "double2Arr": (Sdf.ValueTypeNames.Double2Array, [(12.34, 56.78), (56.78, 12.34)]),
            "double3": (Sdf.ValueTypeNames.Double3, (12.34, 56.78, 90.12)),
            "double3Arr": (Sdf.ValueTypeNames.Double3Array, [(12.34, 56.78, 90.12), (90.12, 56.78, 12.34)]),
        }

        for path in [cube_prim_path, cube_prim_path_2]:
            stage = omni.usd.get_context().get_stage()
            cube_prim = stage.GetPrimAtPath(path)
            for name, (dtype, value) in values.items():
                cube_prim.CreateAttribute(name, dtype).Set(value)

        await omni.kit.app.get_app().next_update_async()

        rp = rep.create.render_product("/OmniverseKit_Persp", (1024, 1024))

        expected_values = {
            "double": [12.34, 12.34],
            "doubleArr": [12.34, 56.78, 50.13, 390.1, -31.2] * 2,
            "double2": [12.34, 56.78] * 2,
            "double2Arr": [12.34, 56.78, 56.78, 12.34] * 2,
            "double3": [12.34, 56.78, 90.12] * 2,
            "double3Arr": [12.34, 56.78, 90.12, 90.12, 56.78, 12.34] * 2,
        }

        fabric_reader_annos = []
        for name in values:
            fabric_reader_anno = rep.annotators.get(
                "Attribute",
                init_params={
                    "prims": [cube_prim_path, cube_prim_path_2],
                    "attribute": name,
                },
            )
            fabric_reader_anno.attach(rp)
            fabric_reader_annos.append(fabric_reader_anno)

        await rep.orchestrator.step_async()

        for name, fabric_reader_anno in zip(expected_values, fabric_reader_annos):
            sensor_data = fabric_reader_anno.get_data()
            np.testing.assert_array_almost_equal(sensor_data, expected_values[name], decimal=3)

    async def test_fabric_reader_multiple_attrs(self):
        """Test the creation of multiple fabric reader annotators that read different attributes."""

        cube1 = rep.create.cube(as_mesh=False)
        cube2 = rep.create.cube(as_mesh=False)
        cube_prim_path = "/Replicator/Cube_Xform/Cube"
        cube_prim_path_2 = "/Replicator/Cube_Xform_01/Cube"

        values = {
            "float": (Sdf.ValueTypeNames.Float, 12.34),
            "floatArr": (Sdf.ValueTypeNames.FloatArray, [12.34, 56.78, 50.13, 390.1, -31.2]),
        }

        for path in [cube_prim_path, cube_prim_path_2]:
            stage = omni.usd.get_context().get_stage()
            cube_prim = stage.GetPrimAtPath(path)
            for name, (dtype, value) in values.items():
                cube_prim.CreateAttribute(name, dtype).Set(value)

        await omni.kit.app.get_app().next_update_async()

        rp = rep.create.render_product("/OmniverseKit_Persp", (1024, 1024))

        expected_values = {
            "float": [12.34, 12.34],
            "floatArr": [12.34, 56.78, 50.13, 390.1, -31.2] * 2,
        }

        fabric_reader_anno_float = rep.annotators.get(
            "Attribute",
            init_params={
                "prims": [cube_prim_path, cube_prim_path_2],
                "attribute": "float",
            },
        )
        fabric_reader_anno_float.attach(rp)

        fabric_reader_anno_float_arr = rep.annotators.get(
            "Attribute",
            init_params={
                "prims": [cube_prim_path, cube_prim_path_2],
                "attribute": "floatArr",
            },
        )
        fabric_reader_anno_float_arr.attach(rp)

        await rep.orchestrator.step_async()
        sensor_data_float = fabric_reader_anno_float.get_data()
        sensor_data_float_arr = fabric_reader_anno_float_arr.get_data()

        np.testing.assert_array_almost_equal(sensor_data_float, expected_values["float"], decimal=3)
        np.testing.assert_array_almost_equal(sensor_data_float_arr, expected_values["floatArr"], decimal=3)

    async def test_semantic_segmentation_annotator(self):
        MAX_DEPTH = 10
        rep.create.cone(semantics=[("class", "cone")], scale=0.1, position=(-100, 0, 100))
        rep.create.cone(semantics=[("class", "cone")], scale=0.1, position=(-90, 0, 90))
        rep.create.cone(semantics=[("class", "cone")], scale=0.1, position=(-80, 0, 80))
        rep.create.cube(scale=0.1, position=(-50, 0, 50))  # unlabelled
        rep.create.sphere(semantics=[("class", "sphere")], scale=0.1, position=(0, -10000, 0))  # out of view

        gt = [{"class": "BACKGROUND"}, {"class": "UNLABELLED"}, {"class": "cone"}]

        # Test hierarchy
        for depth in range(1, MAX_DEPTH):
            xform = rep.create.xform(semantics=[("class", "level0")], position=(depth * 10, 0, depth * -10))
            for d in range(1, depth):
                xform = rep.create.xform(semantics=[("class", f"level{d}")], parent=xform)
            rep.create.cone(semantics=[("class", "cone")], scale=0.1, parent=xform)
            hierarchy = ",".join([f"level{d}" for d in range(depth)])
            gt.append({"class": f"cone,{hierarchy}"})

        anno = rep.annotators.get("semantic_segmentation")
        anno.attach(self.render_product)

        await rep.orchestrator.step_async()

        self.assertGreater(len(anno.get_data()["info"]["idToLabels"]), 0)

        for _, value in anno.get_data()["info"]["idToLabels"].items():
            self.assertTrue(value in gt, f"Unexpected value {value} found. Expected one of {gt}")
            idx = gt.index(value)
            gt.pop(idx)

        self.assertEqual(len(gt), 0, f"One or more GT labels were not found in the annotator output: {gt}")

    async def test_semantic_segmentation_annotator_coloured_instance(self):
        MAX_DEPTH = 10
        rep.create.cone(semantics=[("class", "cone")], scale=0.1, position=(-100, 0, 100))
        rep.create.cone(semantics=[("class", "cone")], scale=0.1, position=(-90, 0, 90))
        rep.create.cone(semantics=[("class", "cone")], scale=0.1, position=(-80, 0, 80))
        rep.create.cube(scale=0.1, position=(-50, 0, 50))  # unlabelled
        rep.create.sphere(semantics=[("class", "sphere")], scale=0.1, position=(0, -10000, 0))  # out of view

        gt = [{"class": "BACKGROUND"}, {"class": "UNLABELLED"}, {"class": "cone"}]

        # Test hierarchy
        for depth in range(1, MAX_DEPTH):
            xform = rep.create.xform(semantics=[("class", "level0")], position=(depth * 10, 0, depth * -10))
            for d in range(1, depth):
                xform = rep.create.xform(semantics=[("class", f"level{d}")], parent=xform)
            rep.create.cone(semantics=[("class", "cone")], scale=0.1, parent=xform)
            hierarchy = ",".join([f"level{d}" for d in range(depth)])
            gt.append({"class": f"cone,{hierarchy}"})

        anno = rep.annotators.get("semantic_segmentation", init_params={"colorize": True})
        anno.attach(self.render_product)

        coloured_instance = rep.annotators.get("instance_segmentation_fast", init_params={"colorize": True})
        coloured_instance.attach(self.render_product)

        await rep.orchestrator.step_async()

        self.assertGreater(len(anno.get_data()["info"]["idToLabels"]), 0)

        for _, value in anno.get_data()["info"]["idToLabels"].items():
            self.assertTrue(value in gt, f"Unexpected value {value} found. Expected one of {gt}")
            idx = gt.index(value)
            gt.pop(idx)

        self.assertEqual(len(gt), 0, f"One or more GT labels were not found in the annotator output: {gt}")

        data = coloured_instance.get_data()["data"]
        semantic_data = anno.get_data()["data"]

    async def test_DepthSensorDistance_annotator(self):
        rep.create.cube(scale=0.1, position=(0, 0, 0))
        rep.create.cone(scale=0.1, position=(0, 0, 10))

        depth_sensor = rep.annotators.get("DepthSensorDistance")
        depth_sensor.attach(self.render_product)

        await rep.orchestrator.step_async()

        data = depth_sensor.get_data()
        self.assertEqual(data.shape, (256, 512))

    async def test_DepthSensorPointCloudPosition_annotator(self):
        rep.create.cube(scale=0.1, position=(0, 0, 0))
        rep.create.cone(scale=0.1, position=(0, 0, 10))

        depth_sensor = rep.annotators.get("DepthSensorPointCloudPosition")
        depth_sensor.attach(self.render_product)

        await rep.orchestrator.step_async()

        data = depth_sensor.get_data()
        self.assertEqual(data.shape, (256, 512, 4))

    async def test_DepthSensorPointCloudColor_annotator(self):
        rep.create.cube(scale=0.1, position=(0, 0, 0))
        rep.create.cone(scale=0.1, position=(0, 0, 10))

        depth_sensor = rep.annotators.get("DepthSensorPointCloudColor")
        depth_sensor.attach(self.render_product)

        await rep.orchestrator.step_async()

        data = depth_sensor.get_data()
        self.assertEqual(data.shape, (256, 512, 4))

    async def test_DepthSensorImager_annotator(self):
        rep.create.cube(scale=0.1, position=(0, 0, 0))
        rep.create.cone(scale=0.1, position=(0, 0, 10))

        depth_sensor = rep.annotators.get("DepthSensorImager")
        depth_sensor.attach(self.render_product)

        await rep.orchestrator.step_async()

        data = depth_sensor.get_data()
        self.assertEqual(data.shape, (256, 512))

    async def test_stableIdMap(self):
        rep.create.cube(semantics={"foo": "bar"})

        def decode_mapping(data: bytes):
            num_entries = int.from_bytes(data[-4:], byteorder="little")
            output_data_type = np.dtype([("stable_id", "<u4", (4)), ("label_length", "<u4"), ("label_offset", "<u4")])
            entry_data_length = num_entries * output_data_type.itemsize
            entries = np.frombuffer(data[:entry_data_length], "<u4").reshape(-1, 6)

            mapping = {}
            for entry in entries:
                entry_id = int.from_bytes(entry[:4].tobytes(), byteorder="little")
                mapping[entry_id] = data[entry[5] : entry[5] + entry[4]].decode("utf8").rstrip()
            return mapping

        rp = rep.create.render_product("/OmniverseKit_Persp", (1024, 1024))
        anno = rep.annotators.get("StableIdMap")
        anno.attach(rp)

        await rep.orchestrator.step_async()
        stable_id_map = decode_mapping(anno.get_data().tobytes())

        self.assertEqual(len(stable_id_map), 2)
        self.assertEqual(set(stable_id_map.values()), {"/Replicator/Cube_Xform", "/Replicator/Cube_Xform/Cube"})

    async def test_srtx_aov_annotators(self):
        # Basic test to ensure that the srtx aov annotators are registered correctly and returns non-empty data
        rep.create.cube(semantics={"foo": "bar"})

        rp = rep.create.render_product("/OmniverseKit_Persp", (1024, 1024))

        srtx_aov_anno_names = [
            "StableIdMap",
            "StableIdSegmentation",
            "SemanticBoundingBox3D",
            "SemanticBoundingBox2DTight",
            "SemanticBoundingBox2DLoose",
            "SemanticSegmentation",
            "SemanticIdMap",
            "StableIdSemanticIdMap",
            "StableIdMapDeltas",
            # "SemanticIdMapDeltas", TODO: Not cherry-picked into 107.3
            "SemanticInstanceSegmentation",
            "StableIdSegmentation",
        ]

        srtx_aov_annotators = []
        for anno_name in srtx_aov_anno_names:
            anno = rep.annotators.get(anno_name)
            anno.attach(rp)
            srtx_aov_annotators.append(anno)

        await rep.orchestrator.step_async()

        for anno in srtx_aov_annotators:
            data = anno.get_data()
            self.assertGreater(len(data), 0)

    async def test_annotator_overscan(self):
        # Test the output of annotator has correct size when overscan is set
        async def run_example_async(with_overscan: bool, fit_output_to_data_window: bool = None):
            await omni.usd.get_context().new_stage_async()
            rep.functional.create.dome_light(intensity=500)
            rep.functional.create.sphere_light(position=(90, 90, 300), color=(0.2, 0.4, 0.2), intensity=90000)
            rep.functional.create.sphere(position=(0, 75, 0), scale=0.8, semantics={"class": "sphere"})
            rep.functional.create.torus(position=(0, 0, 0), scale=0.5, semantics={"class": "torus"})
            rep.functional.create.cone(position=(0, -100, 0), semantics={"class": "cone"})

            camera = rep.functional.create.camera(position=(0, 0, 0), name="RepCamera")
            rp = rep.create.render_product(camera, (1000, 1000), name="RepCameraRP")

            if with_overscan and fit_output_to_data_window is not None:
                settings = carb.settings.get_settings()
                overscan_amout = 0.2
                settings.set("/rtx/dataWindowNDC/0", -overscan_amout)
                settings.set("/rtx/dataWindowNDC/1", -overscan_amout)
                settings.set("/rtx/dataWindowNDC/2", 1.0 + overscan_amout)
                settings.set("/rtx/dataWindowNDC/3", 1.0 + overscan_amout)
                settings.set("/rtx/dataWindow/fitOutputToDataWindow", fit_output_to_data_window)

            anno_names = [
                "rgb",
                "normals",
                "distance_to_camera",
                "distance_to_image_plane",
                "semantic_segmentation",
                "instance_segmentation_fast",
                "instance_id_segmentation_fast",
                "motion_vectors",
            ]
            annotators = []
            for anno_name in anno_names:
                anno = rep.annotators.get(anno_name)
                anno.attach(rp)
                annotators.append(anno)

            for _ in range(10):
                await omni.kit.app.get_app().next_update_async()
            await rep.orchestrator.step_async()

            anno_data_list = [anno.get_data() for anno in annotators]

            anno_data_list = [
                anno_data["data"] if isinstance(anno_data, dict) else anno_data for anno_data in anno_data_list
            ]

            for anno_data in anno_data_list:
                if with_overscan and fit_output_to_data_window:
                    if len(anno_data.shape) == 3:
                        self.assertEqual(anno_data.shape, (1400, 1400, 4))
                    else:
                        self.assertEqual(anno_data.shape, (1400, 1400))
                else:
                    if len(anno_data.shape) == 3:
                        self.assertEqual(anno_data.shape, (1000, 1000, 4))
                    else:
                        self.assertEqual(anno_data.shape, (1000, 1000))

        await run_example_async(with_overscan=False)
        await run_example_async(with_overscan=True, fit_output_to_data_window=False)
        await run_example_async(with_overscan=True, fit_output_to_data_window=True)

    async def test_opencv_camera_params(self):
        camera = rep.create.camera(position=(100, 0, 0), projection_type="fisheyeOpenCV")

        camera_2 = rep.create.camera(
            position=(100, 0, 0), projection_type="fisheyeOpenCV", openCV_focal_x=700, openCV_focal_y=800
        )
        camera_3 = rep.create.camera(
            position=(100, 0, 0), projection_type="pinholeOpenCV", openCV_focal_x=600, openCV_focal_y=900
        )

        pinhole_camera = rep.create.camera(position=(100, 0, 0), projection_type="pinhole")

        render_product = rep.create.render_product(camera, (1200, 1000))
        render_product_2 = rep.create.render_product(camera_2, (800, 600))
        render_product_3 = rep.create.render_product(camera_3, (1200, 1000))
        render_product_4 = rep.create.render_product(pinhole_camera, (1200, 1000))

        anno = rep.annotators.get("CameraParams").attach(render_product)
        anno_2 = rep.annotators.get("CameraParams").attach(render_product_2)
        anno_3 = rep.annotators.get("CameraParams").attach(render_product_3)

        pinhole_anno = rep.annotators.get("CameraParams").attach(render_product_4)

        await rep.orchestrator.step_async()

        self.assertEqual(anno.get_data()["cameraModel"], "fisheyeOpenCV")
        self.assertAlmostEqual(anno.get_data()["cameraOpenCVFx"], 731.7879028320312, places=3)  # Default value
        self.assertAlmostEqual(anno.get_data()["cameraOpenCVFy"], 731.7879028320312, places=3)  # Default value

        self.assertEqual(anno_2.get_data()["cameraModel"], "fisheyeOpenCV")
        self.assertAlmostEqual(anno_2.get_data()["cameraOpenCVFx"], 700)  # Custom value
        self.assertAlmostEqual(anno_2.get_data()["cameraOpenCVFy"], 800)

        for key in anno_3.get_data():
            if key == "cameraOpenCVFx":
                self.assertAlmostEqual(anno_3.get_data()[key], 600)  # Custom value
            elif key == "cameraOpenCVFy":
                self.assertAlmostEqual(anno_3.get_data()[key], 900)
            elif key == "cameraModel":
                self.assertEqual(anno_3.get_data()[key], "pinholeOpenCV")
            else:
                # other value should be the same for pinhole and pinholeOpenCV
                pinhole_opencv_data = anno_3.get_data()[key]
                pinhole_data = pinhole_anno.get_data()[key]
                if isinstance(pinhole_opencv_data, np.ndarray):
                    np.testing.assert_array_almost_equal(pinhole_opencv_data, pinhole_data, decimal=3)
                else:
                    self.assertAlmostEqual(pinhole_opencv_data, pinhole_data, places=3)

    async def test_semantic_segmentation_annotator_coloured_instance(self):
        with rep.trigger.on_frame():
            cone = rep.create.cone(
                semantics={"class": "cone"},
                position=(460, 450, 420),
            )
            cube = rep.create.cube(
                semantics={"class": "cube"},
                position=(400, 450, 450),
            )
            with rep.create.group([cone, cube]):
                rep.modify.visibility(rep.distribution.choice([True, False]))

        anno = rep.annotators.get("semantic_segmentation", init_params={"colorize": True})
        anno.attach(self.render_product)

        CONE_PIXEL = (128, 502)
        CUBE_PIXEL = (128, 10)

        for _ in range(3):
            await rep.orchestrator.step_async()
            data = anno.get_data()
            seg = data["data"]
            semantic_map = data["info"]["idToLabels"]

            # Check cone pixel is always the same
            cone_pixel_rgba = str(tuple(seg[CONE_PIXEL]))
            cone_pixel_semantic = semantic_map.get(cone_pixel_rgba, {})
            if cone_pixel_semantic != {"class": "BACKGROUND"}:
                self.assertEqual(cone_pixel_semantic, {"class": "cone"}, "Cone semantic missing or incorrect")

            # Check cube pixel is always the same
            cube_pixel_rgba = str(tuple(seg[CUBE_PIXEL]))
            cube_pixel_semantic = semantic_map.get(cube_pixel_rgba, {})
            if cube_pixel_semantic != {"class": "BACKGROUND"}:
                self.assertEqual(cube_pixel_semantic, {"class": "cube"}, "Cube semantic missing or incorrect")
