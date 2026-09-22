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
import io
import json
import os
import platform
import shutil
import sys
import unittest
from pathlib import Path

import carb
import imageio
import numpy as np
import omni.graph.core as og
import omni.kit
import omni.replicator.core as rep
import omni.syntheticdata as sd
import warp as wp
from omni.hydra.engine.stats import get_device_info
from omni.replicator.core.functional import io_functions
from omni.replicator.core.utils import annotator_utils
from PIL import Image
from pxr import Usd

TEST_DATA_DIR = Path(os.path.dirname(os.path.realpath(__file__))).joinpath("data")


@wp.kernel
def rgba_to_rgb_warp(data_in: wp.array3d(dtype=wp.uint8), data_out: wp.array3d(dtype=wp.uint8)):
    i, j = wp.tid()
    data_out[i, j, 0] = data_in[i, j, 0]
    data_out[i, j, 1] = data_in[i, j, 1]
    data_out[i, j, 2] = data_in[i, j, 2]


@wp.kernel
def hdr_rgba_to_rgb_warp(data_in: wp.array3d(dtype=wp.float16), data_out: wp.array3d(dtype=wp.float16)):
    i, j = wp.tid()
    data_out[i, j, 0] = data_in[i, j, 0]
    data_out[i, j, 1] = data_in[i, j, 1]
    data_out[i, j, 2] = data_in[i, j, 2]


def rgba_to_rgb_np(data_in):
    return data_in[..., :3]


@wp.kernel
def image_gaussian_noise_warp(
    data_in: wp.array3d(dtype=wp.uint8), data_out: wp.array3d(dtype=wp.uint8), seed: int, sigma: float = 0.5
):
    i, j = wp.tid()
    dim_i = data_out.shape[0]
    dim_j = data_out.shape[1]
    pixel_id = i * dim_i + j
    state_r = wp.rand_init(seed, pixel_id + (dim_i * dim_j * 0))
    state_g = wp.rand_init(seed, pixel_id + (dim_i * dim_j * 1))
    state_b = wp.rand_init(seed, pixel_id + (dim_i * dim_j * 2))

    data_out[i, j, 0] = wp.uint8(float(data_in[i, j, 0]) + (255.0 * sigma * wp.randn(state_r)))
    data_out[i, j, 1] = wp.uint8(float(data_in[i, j, 1]) + (255.0 * sigma * wp.randn(state_g)))
    data_out[i, j, 2] = wp.uint8(float(data_in[i, j, 2]) + (255.0 * sigma * wp.randn(state_b)))
    data_out[i, j, 3] = wp.uint8(255)


def image_gaussian_noise_np(data_in, seed: int, sigma: float = 0.5):
    np.random.seed(seed)
    data_out = np.empty_like(data_in)
    data_out[..., :3] = np.clip(
        data_in[..., :3] + 255.0 * sigma * np.random.randn(*data_in.shape[:-1], 3), 0, 255
    ).astype(data_in.dtype)
    data_out[..., 3] = 255
    return data_out


class TestAnnotatorRegistry(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self.annotators_to_unregister = []
        self.augmentations_to_unregister = []

        # Create a new stage
        await omni.usd.get_context().new_stage_async()
        await omni.kit.app.get_app().next_update_async()

        self.out_dir = carb.tokens.get_tokens_interface().resolve("${temp}/test_annotator_registry")
        self.golden_dir = Path(TEST_DATA_DIR).joinpath("golden")

    async def tearDown(self):
        sd.SyntheticData.Get().set_instance_mapping_semantic_filter("*:*")
        rep.orchestrator.stop()
        for annotator in self.annotators_to_unregister:
            rep.annotators.unregister(annotator)
        for augmentation in self.augmentations_to_unregister:
            rep.annotators.unregister_augmentation(augmentation)
        shutil.rmtree(self.out_dir, ignore_errors=True)
        await omni.usd.get_context().new_stage_async()

    async def _scene_setup(self):
        self.camera = rep.create.camera(position=(0, 0, 1000))
        self.render_product = rep.create.render_product(self.camera, (1024, 512))
        # Create colour
        red = rep.create.material_omnipbr(diffuse=(255, 0, 0))

        # Create some shapes to randomize
        stage = omni.usd.get_context().get_stage()
        parent = stage.DefinePrim("/Parent", "Xform")
        rep.functional.modify.semantics(parent, [("class", "parent_semantic")])

        torus = rep.create.torus(semantics=[("class", "torus"), ("alias", "donut")])
        sphere = rep.create.sphere(semantics=[("class", "sphere"), ("alias", "ball")], material=red)
        cube = rep.create.cube(semantics=[("class", "cube")])

        # Create hierarchical semantics
        omni.kit.commands.create(
            "MovePrim", path_from="/Replicator/Cube_Xform", path_to="/Parent/Cube_Xform"
        ).do()  # executing command without undo to avoid bug https://jirasw.nvidia.com/browse/OMPE-14264

        # fix seed for consistent result
        test_seed = 1234
        self.trigger = rep.trigger.on_frame(max_execs=10, rt_subframes=2)
        with self.trigger:
            with rep.create.group([torus, sphere, cube]):
                rep.modify.pose(
                    position=rep.distribution.uniform((-100, -100, -100), (200, 200, 200), seed=test_seed),
                    scale=rep.distribution.uniform(0.1, 2, seed=test_seed),
                )
                rep.randomizer.rotation(seed=test_seed)

        self._backend = rep.BackendDispatch(output_dir=self.out_dir, overwrite=True)
        self.backend = self._backend
        await omni.kit.app.get_app().next_update_async()

    @unittest.skipIf(os.getenv("ETM_ACTIVE"), "skipped in ETM to keep tests lean")
    async def test_docstrings(self):
        """Test module docstring examples"""
        failures, test_counts = doctest.testmod(rep.annotators)
        if failures:
            self.fail(f"Encountered {failures} failures in {test_counts} tests.")
        else:
            print(f"Passed {test_counts} docstring tests")

    async def test_get_registered_annotators(self):
        annotators = rep.annotators.get_registered_annotators()
        DEFAULT_ANNOS = [
            "camera_params",
            "rgb",
            "normals",
            "motion_vectors",
            "cross_correspondence",
            "occlusion",
            "distance_to_image_plane",
            "distance_to_camera",
            "LdrColor",
            "HdrColor",
            "SmoothNormal",
            "BumpNormal",
            "AmbientOcclusion",
            "Motion2d",
            "DiffuseAlbedo",
            "SpecularAlbedo",
            "Roughness",
            "DirectDiffuse",
            "DirectSpecular",
            "Reflections",
            "IndirectDiffuse",
            "DepthLinearized",
            "EmissionAndForegroundMask",
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
            "PtMultiMatte0",
            "PtMultiMatte1",
            "PtMultiMatte2",
            "PtMultiMatte3",
            "PtMultiMatte4",
            "PtMultiMatte5",
            "PtMultiMatte6",
            "PtMultiMatte7",
            "primPaths",
            "bounding_box_2d_tight_fast",
            "bounding_box_2d_tight",
            "bounding_box_2d_loose_fast",
            "bounding_box_2d_loose",
            "bounding_box_3d_360",
            "bounding_box_3d_fast",
            "bounding_box_3d",
            "semantic_segmentation",
            "instance_segmentation_fast",
            "instance_segmentation",
            "CameraParams",
            "skeleton_data",
            "pointcloud",
        ]
        for anno in DEFAULT_ANNOS:
            self.assertTrue(anno in annotators, f"Missing annotator {anno} from {annotators}")

    def _validate_bbox_2d(self, frame_id):
        npy_file_name = f"bounding_box_2d_loose_{frame_id}.npy"
        self.assertTrue(os.path.isfile(os.path.join(self.out_dir, npy_file_name)))

        data = np.load(os.path.join(self.out_dir, npy_file_name))

        golden_file_path = os.path.join(self.golden_dir, "basic_writer_bounding_box_2d_loose.npy")
        golden_data = np.load(golden_file_path)

        # Allow bounds to vary by 1 pixel
        np.testing.assert_allclose(np.unique(data["x_min"]), np.unique(golden_data["x_min"]), atol=1)
        np.testing.assert_allclose(np.unique(data["y_min"]), np.unique(golden_data["y_min"]), atol=1)
        np.testing.assert_allclose(np.unique(data["x_max"]), np.unique(golden_data["x_max"]), atol=1)
        np.testing.assert_allclose(np.unique(data["y_max"]), np.unique(golden_data["y_max"]), atol=1)

        # Check for labels
        labels_file_name = f"bounding_box_2d_loose_labels_{frame_id}.json"
        with open(os.path.join(self.out_dir, labels_file_name), "r") as json_data:
            id_to_labels = json.load(json_data)

        self.assertEqual(id_to_labels["0"], {"class": "torus", "alias": "donut"})
        self.assertEqual(id_to_labels["1"], {"class": "sphere", "alias": "ball"})
        self.assertEqual(id_to_labels["2"], {"class": "cube,parent_semantic", "alias": "box"})
        self.assertEqual(id_to_labels["3"], {"alias": "box", "class": "parent_semantic"})

        np.testing.assert_allclose(data["semanticId"], np.array([0, 1, 1, 2, 3]))

    def _validate_rgb(self, frame_id, default_std_dev=2):
        image_file_name = f"image_{frame_id}.png"
        image_path = os.path.join(self.out_dir, image_file_name)
        self.assertTrue(os.path.isfile(image_path), f"Could not find image file at path {image_path}")

        data = np.asarray(Image.open(image_path))

        golden_file_path = os.path.join(self.golden_dir, "basic_writer_rgb.png")
        golden_image = np.asarray(Image.open(golden_file_path))

        std_dev = np.sqrt(np.square(data - golden_image).astype(float).mean())
        self.assertLess(std_dev, default_std_dev)

    def _write_image(self, data, frame_id):
        # Save image
        file_path = f"image_{frame_id}.png"
        self._backend.schedule(io_functions.write_image, data=data, path=file_path)

    def _write_bbox2d(self, data, frame_id):
        # Save BBOX 2D
        bbox_2d_tight_data = data["data"]

        id_to_labels = data["info"]["idToLabels"]

        file_path = f"bounding_box_2d_tight_{frame_id}.npy"
        self._backend.schedule(io_functions.write_np, data=bbox_2d_tight_data, path=file_path)

        labels_file_path = f"bounding_box_2d_tight_labels_{frame_id}.json"
        self._backend.schedule(io_functions.write_json, data=id_to_labels, path=labels_file_path)

    async def test_get_data_odd_resolution(self):
        # Catches certain issues when running on DirectX with
        # non-power-of-2 resolutions
        rp = rep.create.render_product(rep.create.camera(), (5, 5))
        anno = rep.annotators.get("distance_to_image_plane")
        anno.attach(rp)

        await rep.orchestrator.step_async()

        data = anno.get_data()
        self.assertEqual(data.shape, (5, 5))

    async def test_get_data(self):
        await self._scene_setup()

        rgb = rep.annotators.get("rgb")
        bbox2d = rep.annotators.get("bounding_box_2d_loose")

        rgb.attach(self.render_product)
        bbox2d.attach(self.render_product)

        for frame_id in range(10):
            await rep.orchestrator.step_async()

            rgb_data = rgb.get_data()
            bbox2d_data = bbox2d.get_data()
            self._write_image(rgb_data, frame_id)
            self._write_bbox2d(bbox2d_data, frame_id)

        self._backend.wait_until_done()

        # FIXME jlafleche test against all frame IDs produced
        for frame_id in range(1):
            self._validate_rgb(frame_id, 3)
            self._validate_bbox_2d

    async def test_get_data_on_open(self):
        """Test get_data on a just-opened scene

        This test is to catch an issue where the render graph was
        not executed on the first frame when attaching an annotator
        to a render product by string.
        """
        scene = os.path.join(self.golden_dir, os.path.pardir, "objects", "semantic_car_scene.usd")
        await omni.usd.get_context().open_stage_async(scene)

        while omni.usd.get_context().get_stage() is None:
            await omni.kit.app.get_app().next_update_async()

        self.render_product = rep.create.render_product("/World/Camera", (1024, 512))

        bbox2d = rep.annotators.get("bounding_box_2d_tight")
        bbox2d.attach(self.render_product)

        await rep.orchestrator.step_async()

        bbox2d_data = bbox2d.get_data()
        self.assertGreater(len(bbox2d_data["data"]), 0)

    async def test_get_data_on_play(self):
        """Test get_data when using capture on play

        This test is to catch an issue where the render graph was
        not executed on the first frame when attaching an annotator
        and running the timeline with capture on play on
        """
        await self._scene_setup()
        rep.orchestrator.set_capture_on_play(True)

        bbox2d = rep.annotators.get("pointcloud")
        bbox2d.attach(self.render_product)

        await rep.orchestrator._orchestrator._initialize_async()

        timeline = omni.timeline.get_timeline_interface()
        timeline.play()
        timeline.commit_silently()

        # Loop through multiple frames to ensure no error trying to get data when first frame is not yet rendered
        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()
            bbox2d_data = bbox2d.get_data()
        self.assertGreater(len(bbox2d_data["data"]), 0)

    async def test_get_data_device(self):
        await self._scene_setup()
        rgb_cpu = rep.annotators.get("rgb")
        rgb_gpu = rep.annotators.get("rgb", device="cuda")

        rgb_cpu.attach(self.render_product)
        rgb_gpu.attach(self.render_product)

        await rep.orchestrator.step_async()

        # Test that defaults are correct
        self.assertTrue(
            isinstance(rgb_cpu.get_data(), np.ndarray),
            f"Default CPU RGB not returning default numpy array: {type(rgb_cpu.get_data())}.",
        )
        self.assertTrue(
            isinstance(rgb_gpu.get_data(), wp.array),
            f"Default GPU RGB not returning default warp array: {type(rgb_gpu.get_data())}.",
        )

        # Test that data is set to correct device
        self.assertTrue(
            isinstance(rgb_cpu.get_data(device="cuda"), wp.array),
            f"Default CPU RGB not returning requested warp array: {type(rgb_cpu.get_data())}.",
        )
        self.assertTrue(
            isinstance(rgb_gpu.get_data(device="cpu"), np.ndarray),
            f"Default GPU RGB not returning requested numpy array: {type(rgb_gpu.get_data())}.",
        )

    @unittest.skipIf(os.getenv("ETM_ACTIVE"), "skipped in ETM to keep tests lean")
    async def test_augmentation_noise_warp(self):
        await self._scene_setup()
        aug = rep.annotators.augment("rgb", image_gaussian_noise_warp, sigma=0.1, seed=1234)
        aug.attach(self.render_product)

        for frame_id in range(10):
            await rep.orchestrator.step_async()
        augmented_data = aug.get_data()

        golden_file_path = os.path.join(self.golden_dir, "augmentation_gaussian_noise_warp_9.png")
        golden_image = np.asarray(Image.open(golden_file_path))

        std_dev = np.sqrt(np.square(augmented_data.numpy() - golden_image).astype(float).mean())
        self.assertLess(std_dev, 2, "Augmentation result exceeds deviation threshold")

    @unittest.skipIf(os.getenv("ETM_ACTIVE"), "skipped in ETM to keep tests lean")
    async def test_augmentation_noise_np(self):
        await self._scene_setup()
        aug = rep.annotators.get("rgb").augment(image_gaussian_noise_np, sigma=0.1, seed=1234)
        aug.attach(self.render_product)

        for frame_id in range(10):
            await rep.orchestrator.step_async()
        augmented_data = aug.get_data()

        golden_file_path = os.path.join(self.golden_dir, "augmentation_gaussian_noise_np_9.png")
        golden_image = np.asarray(Image.open(golden_file_path))

        std_dev = np.sqrt(np.square(augmented_data - golden_image).astype(float).mean())
        self.assertLess(std_dev, 2, "Augmentation result exceeds deviation threshold")

    @unittest.skipIf(os.getenv("ETM_ACTIVE"), "skipped in ETM to keep tests lean")
    async def test_augmentation_rgb_warp(self):
        await self._scene_setup()
        aug = rep.annotators.augment("rgb", rgba_to_rgb_warp, data_out_shape=(-1, -1, 3))
        aug.attach(self.render_product)

        for frame_id in range(10):
            await rep.orchestrator.step_async()
            augmented_data = aug.get_data()
            self.assertEqual(augmented_data.shape[-1], 3)

        golden_file_path = os.path.join(self.golden_dir, "augmentation_rgb_9.png")
        golden_image = np.asarray(Image.open(golden_file_path))

        std_dev = np.sqrt(np.square(augmented_data.numpy() - golden_image).astype(float).mean())
        self.assertLess(std_dev, 2, "Annotation result exceeds deviation threshold")

    @unittest.skipIf(os.getenv("ETM_ACTIVE"), "skipped in ETM to keep tests lean")
    async def test_augmentation_hdr_rgb_warp(self):
        """Test that augmentation works on alternate data types"""
        # https://github.com/opencv/opencv/issues/21326 when running on ARM
        if platform.machine() == "aarch64":
            carb.log_warn("Setting OPENCV_IO_ENABLE_OPENEXR to 1 for ARM")
            os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"

        await self._scene_setup()
        aug = rep.annotators.augment("HdrColor", hdr_rgba_to_rgb_warp, data_out_shape=(-1, -1, 3))
        aug.attach(self.render_product)

        for frame_id in range(10):
            await rep.orchestrator.step_async()
            augmented_data = aug.get_data()
            self.assertEqual(augmented_data.shape[-1], 3)

        # backend = rep.BackendDispatch({"paths": {"out_dir": "_outoutout"}})
        # backend.write_exr("foo.exr", augmented_data.numpy().astype(np.float32))
        imageio.plugins.freeimage.download()
        golden_file_path = os.path.join(self.golden_dir, "augmentation_rgb_9.exr")
        golden_image = imageio.imopen(golden_file_path, io_mode="r").read()

        std_dev = np.sqrt(np.square(augmented_data.numpy().astype(np.float32) - golden_image).astype(float).mean())
        self.assertLess(std_dev, 2, "Annotation result exceeds deviation threshold")

    @unittest.skipIf(os.getenv("ETM_ACTIVE"), "skipped in ETM to keep tests lean")
    async def test_augmentation_hdr_rgb_np(self):
        # https://github.com/opencv/opencv/issues/21326 when running on ARM
        if platform.machine() == "aarch64":
            carb.log_warn("Setting OPENCV_IO_ENABLE_OPENEXR to 1 for ARM")
            os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"

        await self._scene_setup()
        aug = rep.annotators.get("HdrColor").augment(rgba_to_rgb_np)
        aug.attach(self.render_product)

        for frame_id in range(10):
            await rep.orchestrator.step_async()
            augmented_data = aug.get_data()
            self.assertEqual(augmented_data.shape[-1], 3)

        imageio.plugins.freeimage.download()
        golden_file_path = os.path.join(self.golden_dir, "augmentation_rgb_9.exr")
        golden_image = imageio.imopen(golden_file_path, io_mode="r").read()

        std_dev = np.sqrt(np.square(augmented_data.astype(np.float32) - golden_image).astype(float).mean())
        self.assertLess(std_dev, 2, "Annotation result exceeds deviation threshold")

    @unittest.skipIf(os.getenv("ETM_ACTIVE"), "skipped in ETM to keep tests lean")
    async def test_augmentation_rgb_np(self):
        await self._scene_setup()
        aug = rep.annotators.get("rgb").augment(rgba_to_rgb_np)
        aug.attach(self.render_product)

        for frame_id in range(10):
            await rep.orchestrator.step_async()
            augmented_data = aug.get_data()
            self.assertEqual(augmented_data.shape[-1], 3)

        golden_file_path = os.path.join(self.golden_dir, "augmentation_rgb_9.png")
        golden_image = np.asarray(Image.open(golden_file_path))

        std_dev = np.sqrt(np.square(augmented_data - golden_image).astype(float).mean())
        self.assertLess(std_dev, 2, "Annotation result exceeds deviation threshold")

    async def test_augmentation_chain_warp(self):
        await self._scene_setup()
        rep.annotators.register(
            "registered_augmentation_warp_test",
            rep.annotators.augment_compose(
                source_annotator=rep.annotators.get("rgb", device="cuda"),
                augmentations=[
                    rep.annotators.Augmentation.from_function(image_gaussian_noise_warp, sigma=0.1, seed=1234),
                    rep.annotators.Augmentation.from_function(rgba_to_rgb_warp, data_out_shape=(-1, -1, 3)),
                ],
            ),
        )
        aug = rep.annotators.get("registered_augmentation_warp_test")
        aug.attach(self.render_product)

        for frame_id in range(10):
            await rep.orchestrator.step_async()
        augmented_data = aug.get_data(device="cpu")

        golden_file_path = os.path.join(self.golden_dir, "augmentation_gaussian_noise_warp_9.png")
        golden_image = np.asarray(Image.open(golden_file_path))[..., :3]

        std_dev = np.sqrt(np.square(augmented_data - golden_image).astype(float).mean())
        self.assertLess(std_dev, 2, "Augmentation result exceeds deviation threshold")

    async def test_augmentation_chain_np(self):
        await self._scene_setup()
        aug = rep.annotators.augment_compose(
            source_annotator="rgb",
            augmentations=[
                rep.annotators.Augmentation.from_function(image_gaussian_noise_np, sigma=0.1, seed=1234),
                rep.annotators.Augmentation.from_function(rgba_to_rgb_np),
            ],
        )
        aug.attach(self.render_product)

        for frame_id in range(10):
            await rep.orchestrator.step_async()
        augmented_data = aug.get_data()

        golden_file_path = os.path.join(self.golden_dir, "augmentation_gaussian_noise_np_9.png")
        golden_image = np.asarray(Image.open(golden_file_path))[..., :3]

        std_dev = np.sqrt(np.square(augmented_data - golden_image).astype(float).mean())
        self.assertLess(std_dev, 2, "Augmentation result exceeds deviation threshold")

    @unittest.skipIf(os.getenv("ETM_ACTIVE"), "skipped in ETM to keep tests lean")
    async def test_register_augmentation(self):
        rep.annotators.register_augmentation(
            "rgb_no_alpha_test", rep.annotators.Augmentation.from_function(rgba_to_rgb_warp)
        )
        self.augmentations_to_unregister.append("rgb_no_alpha_test")
        rep.annotators.get_augmentation("rgb_no_alpha_test")

        # test register with new name
        rep.annotators.register_augmentation("rgb_no_alpha_test2", "rgb_no_alpha_test")
        self.augmentations_to_unregister.append("rgb_no_alpha_test2")
        rep.annotators.get_augmentation("rgb_no_alpha_test2")

    @unittest.skipIf(os.getenv("ETM_ACTIVE"), "skipped in ETM to keep tests lean")
    async def test_augment_compose(self):
        await self._scene_setup()

        def rgb_to_greyscale(data_in):
            r, g, b = data_in[..., 0], data_in[..., 1], data_in[..., 2]
            return (0.299 * r + 0.587 * g + 0.114 * b).astype(np.uint8)

        greyscale_anno = rep.annotators.augment_compose(
            source_annotator="rgb",
            augmentations=["RgbaToRgb", rep.annotators.Augmentation.from_function(rgb_to_greyscale)],
        )

        greyscale_anno.attach(self.render_product)

        for frame_id in range(10):
            await rep.orchestrator.step_async()

        augmented_data = greyscale_anno.get_data(device="cpu")

        golden_file_path = os.path.join(self.golden_dir, "augmentation_compose_9.png")
        golden_image = np.asarray(Image.open(golden_file_path))

        std_dev = np.sqrt(np.square(augmented_data - golden_image).astype(float).mean())
        self.assertLess(std_dev, 3, "Augmentation result exceeds deviation threshold")

    @unittest.skipIf(os.getenv("ETM_ACTIVE"), "skipped in ETM to keep tests lean")
    async def test_augmentation_missing_arg(self):
        await self._scene_setup()

        def aug_fail_test(data_in, seed, a_required_arg):
            return data_in

        with self.assertRaises(rep.annotators.AugmentationError) as context:
            rep.annotators.get("rgb").augment(aug_fail_test)

        self.assertTrue("Augmentation is missing required arguments: ['a_required_arg']" in str(context.exception))

    async def test_augmentation_global_seed(self):
        await self._scene_setup()
        rep.set_global_seed(123)

        def aug_global_seed_np(data_in, seed):
            return data_in * 0 + seed

        @wp.kernel
        def aug_global_seed_warp(data_in: wp.array3d(dtype=wp.uint8), data_out: wp.array3d(dtype=wp.uint8), seed: int):
            i, j = wp.tid()
            data_out[i, j, 0] = wp.uint8(seed)
            data_out[i, j, 1] = wp.uint8(seed)
            data_out[i, j, 2] = wp.uint8(seed)
            data_out[i, j, 3] = wp.uint8(seed)

        anno1 = rep.annotators.get("rgb").augment(aug_global_seed_np)
        anno1.attach(self.render_product)
        anno2 = rep.annotators.get("rgb").augment(aug_global_seed_np)
        anno2.attach(self.render_product)
        anno3 = rep.annotators.get("rgb").augment(aug_global_seed_warp)
        anno3.attach(self.render_product)
        anno4 = rep.annotators.get("rgb").augment(aug_global_seed_warp)
        anno4.attach(self.render_product)

        await rep.orchestrator.step_async()

        anno_data1 = anno1.get_data()
        anno_data2 = anno2.get_data()
        anno_data3 = anno3.get_data().numpy()
        anno_data4 = anno4.get_data().numpy()

        self.assertEqual(anno_data1[0, 0, 0], 33158374, "Got unexpected seeded value based on provided global seed")
        self.assertEqual(anno_data2[0, 0, 0], 1432268922, "Got unexpected seeded value based on provided global seed")
        self.assertEqual(anno_data3[0, 0, 0], 56, "Got unexpected seeded value based on provided global seed")
        self.assertEqual(anno_data4[0, 0, 0], 253, "Got unexpected seeded value based on provided global seed")

    @unittest.skipIf(os.getenv("ETM_ACTIVE"), "skipped in ETM to keep tests lean")
    async def test_node_augmentation(self):
        await self._scene_setup()
        anno = rep.annotators.get("PostProcessRenderProductCamera").augment("omni.replicator.core.CameraParams")
        anno.attach(self.render_product)

        await rep.orchestrator.step_async()

        anno_data = anno.get_data()

        self.assertTrue("cameraFisheyeMaxFOV" in anno_data, "Expected parameter missing from augmented node.")
        self.assertEqual(anno_data["cameraModel"], "pinhole", "Incorrect camera model in augmented node.")

    @unittest.skipIf(os.getenv("ETM_ACTIVE"), "skipped in ETM to keep tests lean")
    async def test_node_augmentation_from_node(self):
        await self._scene_setup()
        augmentation = rep.annotators.Augmentation.from_node("omni.replicator.core.CameraParams")
        anno = rep.annotators.get("PostProcessRenderProductCamera").augment(augmentation)
        anno.attach(self.render_product)

        await rep.orchestrator.step_async()

        anno_data = anno.get_data()

        self.assertTrue("cameraFisheyeMaxFOV" in anno_data, "Expected parameter missing from augmented node.")
        self.assertEqual(anno_data["cameraModel"], "pinhole", "Incorrect camera model in augmented node.")

    @unittest.skipIf(os.getenv("ETM_ACTIVE"), "skipped in ETM to keep tests lean")
    async def test_node_augmentation_register(self):
        await self._scene_setup()
        rep.annotators.register_augmentation("cam_params_test", "omni.replicator.core.CameraParams")
        self.augmentations_to_unregister.append("cam_params_test")

        anno = rep.annotators.get("PostProcessRenderProductCamera").augment("cam_params_test")
        anno.attach(self.render_product)

        await rep.orchestrator.step_async()

        anno_data = anno.get_data()

        self.assertTrue("cameraFisheyeMaxFOV" in anno_data, "Expected parameter missing from augmented node.")
        self.assertEqual(anno_data["cameraModel"], "pinhole", "Incorrect camera model in augmented node.")

    @unittest.skip("Need test annotator node with an execOut")
    async def test_augmentation_auto_connect(self):
        await self._scene_setup()
        NodeConnectionTemplate = sd.SyntheticData.NodeConnectionTemplate
        rep.AnnotatorRegistry.register_annotator_from_node(
            "SyncGateTest",
            input_rendervars=[
                NodeConnectionTemplate("PostProcessDispatcher", attributes_mapping={"outputs:exec": "inputs:execIn"})
            ],
            node_type_id="omni.graph.action.RationalTimeSyncGate",
        )

        anno = rep.annotators.get("SyncGateTest").augment("rgba_to_rgb")
        anno.attach(self.render_product)

        # Find node
        root_path = "/Render/PostProcess/SDGPipeline"

        node_prim = None
        stage = omni.usd.get_context().get_stage()
        for child in stage.GetPrimAtPath(root_path).GetChildren():
            if "Rgba" in child.GetPrimPath().pathString:
                node_prim = child
                break

        self.assertTrue(node_prim is not None, "Unable to find augmentation node")
        node = og.Controller().node(node_prim)
        exec_in = node.get_attribute("inputs:exec")
        self.assertEqual(exec_in.get_upstream_connection_count(), 1, "Incorrect number of connections to exec in")

    async def test_ldr_color_cpu(self):
        await self._scene_setup()
        anno = rep.annotators.get("LdrColor")
        anno.attach(self.render_product)
        for frame_id in range(10):
            await rep.orchestrator.step_async()
        anno_data = anno.get_data()

        golden_file_path = os.path.join(self.golden_dir, "augmentation_rgb_9.png")
        golden_image = np.asarray(Image.open(golden_file_path))

        std_dev = np.sqrt(np.square(anno_data[..., :3] - golden_image).astype(float).mean())
        self.assertLess(std_dev, 2, "Augmentation result exceeds deviation threshold")

    async def test_rgb_gpu(self):
        await self._scene_setup()
        anno = rep.annotators.get("LdrColor", device="cuda:0")
        anno.attach(self.render_product)
        for frame_id in range(10):
            await rep.orchestrator.step_async()
        anno_data = anno.get_data()

        self.assertTrue(anno_data.device.is_cuda, f"Expected cuda device, got {anno_data.device.alias}")

        golden_file_path = os.path.join(self.golden_dir, "augmentation_rgb_9.png")
        golden_image = np.asarray(Image.open(golden_file_path))

        std_dev = np.sqrt(np.square(anno_data.numpy()[..., :3] - golden_image).astype(float).mean())
        self.assertLess(std_dev, 2, "Augmentation result exceeds deviation threshold")

    async def test_depth_pixel_cpu(self):
        """Test single value output"""
        await self._scene_setup()
        anno = rep.annotators.get("DepthLinearized")
        anno.attach(rep.create.render_product(self.camera, (1, 1)))
        for _ in range(2):
            await rep.orchestrator.step_async()
        anno_data = anno.get_data()
        self.assertEqual(anno_data.shape, ())

        self.assertTrue(isinstance(anno_data, np.ndarray), f"Expected numpy array, got {type(anno_data)}")

    async def test_depth_pixel_gpu(self):
        """Test single value output"""
        await self._scene_setup()
        anno = rep.annotators.get("DepthLinearized", device="cuda:0")
        anno.attach(rep.create.render_product(self.camera, (1, 1)))
        for _ in range(2):
            await rep.orchestrator.step_async()
        anno_data = anno.get_data()
        self.assertEqual(anno_data.shape, (1,))

        self.assertTrue(anno_data.device.is_cuda, f"Expected cuda device, got {anno_data.device.alias}")

    async def test_ldr_color_gpu(self):
        await self._scene_setup()
        anno = rep.annotators.get("LdrColor", device="cuda:0")
        anno.attach(self.render_product)
        for frame_id in range(10):
            await rep.orchestrator.step_async()
        anno_data = anno.get_data()

        self.assertTrue(anno_data.device.is_cuda, f"Expected cuda device, got {anno_data.device.alias}")

        golden_file_path = os.path.join(self.golden_dir, "augmentation_rgb_9.png")
        golden_image = np.asarray(Image.open(golden_file_path))

        std_dev = np.sqrt(np.square(anno_data.numpy()[..., :3] - golden_image).astype(float).mean())
        self.assertLess(std_dev, 2, "Annotation result exceeds deviation threshold")

    @unittest.skipIf(len(get_device_info()) < 2, "MGPU test unable to run on single GPU machine.")
    async def test_ldr_color_mgpu(self):
        await self._scene_setup()
        anno = rep.annotators.get("LdrColor", device="cuda:1")
        anno.attach(self.render_product)
        for frame_id in range(10):
            await rep.orchestrator.step_async()
        anno_data = anno.get_data()

        self.assertEqual(anno_data.device.ordinal, 1, f"Expected cuda device `1`, got `{anno_data.device.ordinal}`")
        self.assertTrue(anno_data.device.is_cuda, f"Expected cuda device, got {anno_data.device.alias}")

        golden_file_path = os.path.join(self.golden_dir, "augmentation_rgb_9.png")
        golden_image = np.asarray(Image.open(golden_file_path))

        std_dev = np.sqrt(np.square(anno_data.numpy()[..., :3] - golden_image).astype(float).mean())
        self.assertLess(std_dev, 2, "Annotation result exceeds deviation threshold")

    async def test_bbox3d_gpu_unsupported(self):
        with self.assertRaises(rep.annotators.AnnotatorRegistryError) as context:
            anno = rep.annotators.get("bounding_box_3d", device="cuda")

    async def test_auto_sync_gate_recur(self):
        """Test if the _auto_sync_gate function will create sync gates recursively."""

        # Using pointcloud annotator because it has semantic_segmentation as upstream node.add()
        await self._scene_setup()

        pointcloud = rep.annotators.get("pointcloud")

        pointcloud.attach(self.render_product)

        for frame_id in range(10):
            await rep.orchestrator.step_async()
            pointcloud_data = pointcloud.get_data()

        self._backend.wait_until_done()

        pointcloud_sync_node = (
            pointcloud.get_node().get_attribute("inputs:exec").get_upstream_connections()[0].get_node()
        )

        self.assertEqual(
            pointcloud_sync_node.get_prim_path(),
            "/Render/PostProcess/SDGPipeline/Replicator_pointcloud_Sync",
        )
        self.assertEqual(pointcloud_sync_node.get_type_name(), "omni.graph.action.RationalTimeSyncGate")

        sync_node_up_conns = pointcloud_sync_node.get_attribute("inputs:execIn").get_upstream_connections()
        # Should be 5 nodes connect to the sync gate: rgb, normal, camera_params, camera_3d_position and semantic_segmentation
        self.assertEqual(len(sync_node_up_conns), 6)

        # There should also be a sync gate for instance segmentation

        semantic_seg_node = None
        for conn in sync_node_up_conns:
            if "semantic_segmentation" in conn.get_node().get_prim_path():
                semantic_seg_node = conn.get_node()
                break

        self.assertTrue(semantic_seg_node is not None)

        instance_node = semantic_seg_node.get_attribute("inputs:exec").get_upstream_connections()[0].get_node()
        instance_sync_node = instance_node.get_attribute("inputs:exec").get_upstream_connections()[0].get_node()

        self.assertEqual(
            instance_sync_node.get_prim_path(),
            "/Render/PostProcess/SDGPipeline/Replicator_instance_segmentation_fast_Sync",
        )
        self.assertEqual(instance_sync_node.get_type_name(), "omni.graph.action.RationalTimeSyncGate")

        instance_sync_node_up_conns = instance_sync_node.get_attribute("inputs:execIn").get_upstream_connections()

        # Should be 3 nodes connect to the sync gate: "InstanceSegmentationSDExportRawArray", "InstanceMappingPtr", "InstanceMapping"
        self.assertEqual(len(instance_sync_node_up_conns), 3)

    @unittest.skip("Enable once OMREQ-1176 addressed")
    async def test_residual_overs(self):
        await self._scene_setup()
        anno = rep.annotators.get("LdrColor", device="cuda")
        anno.attach(self.render_product)
        await rep.orchestrator.step_async()
        fpath = os.path.join(self.out_dir, "test_overs.usda")

        # Remove replicator prim to avoid errors in test
        stage = omni.usd.get_context().get_stage()
        stage.RemovePrim("/Replicator")

        # Save stage
        await omni.usd.get_context().save_as_stage_async(fpath)

        with open(fpath, "r") as f:
            for line in f.readlines():
                self.assertNotIn("over", line, f"Caught override in saved usda on line: `{line}`")

    async def test_attach_annotator_capture_on_play_playing(self):
        """Test whether annotator is capturing data when attached on playing scene with capture on play enabled."""
        await omni.usd.get_context().new_stage_async()  # FIXME Required due to OM-98674 after hitting timeline play
        rep.orchestrator.set_capture_on_play(True)
        await omni.kit.app.get_app().next_update_async()
        rep.orchestrator._orchestrator._timeline.play()
        rep.orchestrator._orchestrator._timeline.commit_silently()  # Needed in Kit 107

        cam = rep.create.camera(position=(1, 2, 3))
        rp = rep.create.render_product(cam, (512, 512))

        cube = rep.create.cube(rotation=(0.0, 45, 0.0))
        cube_prim = cube.get_output_prims()["prims"][0]

        with rep.trigger.on_frame():
            with cube:
                rep.modify.pose(
                    position=rep.distribution.sequence(
                        [(0.0, -10.0, 0.0), (1.0, 1.0, 1.0), (2.0, 2.0, 2.0), (3.0, 3.0, 3.0)]
                    )
                )

        anno = rep.annotators.get("rgb")
        anno.attach(rp)

        await rep.orchestrator._orchestrator.start_async()

        for _ in range(4):
            await omni.kit.app.get_app().next_update_async()

        anno_data = anno.get_data()

        self.assertTrue(anno_data is not None, "Annotator data is empty, expected data received")
        self.assertEqual(anno_data.shape, (512, 512, 4))
        self.assertEqual(cube_prim.GetAttribute("xformOp:translate").Get()[0], 3)

    async def test_attach_detach(self):
        await self._scene_setup()
        rgb_anno = rep.annotators.get("rgb")
        rgb_anno.attach(self.render_product)
        await rep.orchestrator.step_async()
        rgb_anno.detach()

        self.assertTrue(
            rgb_anno._render_products is None,
            f"Expected detached annotator to have no render products, got {rgb_anno._render_products}",
        )
        with self.assertRaises(rep.annotators.AnnotatorError):
            rgb_anno.detach()

    async def test_simtime(self):
        await self._scene_setup()
        sim_time_anno = rep.annotators.get("ReferenceTime")
        sim_time_anno.attach(self.render_product)

        await rep.orchestrator.step_async()

        sim_time = sim_time_anno.get_data()
        self.assertTrue(sim_time["referenceTimeDenominator"] != 0, "Sim time denominator not set")
        self.assertTrue(sim_time["referenceTimeNumerator"] != 0, "Sim time numerator not set")

    async def test_get_data_do_copy(self):
        await self._scene_setup()
        # TODO jlafleche Revise test to better catch malfunctions
        anno = rep.annotators.get("LdrColor", device="cuda")
        anno.attach(self.render_product)

        await rep.orchestrator.step_async()
        data = anno.get_data()
        data_id_0 = id(data)

        # Default does not do a copy
        await rep.orchestrator.step_async()
        data = anno.get_data()
        data_id_1 = id(data)
        self.assertNotEqual(data_id_0, data_id_1)

        # Explicitly copy
        await rep.orchestrator.step_async()
        data0 = anno.get_data(do_array_copy=True)
        await rep.orchestrator.step_async()
        data1 = anno.get_data(do_array_copy=True)
        data_id_1 = id(data1)
        self.assertNotEqual(data_id_0, data_id_1)

        # Change annotator default do_copy setting
        anno.detach()
        await rep.orchestrator.step_async()
        anno = rep.annotators.get("LdrColor", device="cuda", do_array_copy=True)
        anno.attach(self.render_product)

        # Annotator default now does a copy
        await rep.orchestrator.step_async()
        data = anno.get_data()
        data_id_1 = id(data)
        self.assertNotEqual(data_id_0, data_id_1)

    async def test_get_data_buffer(self):
        await self._scene_setup()
        anno = rep.annotators.get("LdrColor", device="cuda", do_array_copy=True)
        anno.attach(self.render_product)

        await rep.orchestrator.step_async()
        data = anno.get_data()
        data_id_0 = id(data)

        # Expect a new buffer since `data`` object is still alive
        await rep.orchestrator.step_async()
        data = anno.get_data()
        data_id_1 = id(data)
        self.assertNotEqual(data_id_0, data_id_1)

        # Delete data object so buffer can be reused
        del data
        await rep.orchestrator.step_async()
        data = anno.get_data()
        data_id_1 = id(data)
        self.assertEqual(data_id_0, data_id_1)

    async def test_multiple_data_arrays(self):
        """Test that an annotator with more than one array output correctly returns data payload"""
        await self._scene_setup()
        rep.annotators.AnnotatorRegistry.register_annotator_from_node(
            name="MultiData",
            input_rendervars=[
                rep.NodeConnectionTemplate(
                    "LdrColorSDhostPtr",
                    attributes_mapping={
                        "outputs:exec": "inputs:execIn",
                    },
                ),
            ],
            node_type_id="omni.graph.scriptnode.ScriptNode",
            output_data_type=np.uint8,
            output_is_2d=True,
            output_channels=4,
            is_gpu_enabled=True,
            hidden=True,
        )
        anno = rep.annotators.get("MultiData")
        anno.attach(self.render_product)

        anno_node = anno.get_node()
        upstream_node = anno_node.get_attribute("inputs:execIn").get_upstream_connections()[0].get_node()
        for attr in ["dataPtr", "bufferSize", "strides", "cudaDeviceIndex", "height", "width"]:
            upstream_attr = upstream_node.get_attribute(f"outputs:{attr}")
            downstream_attr = og.Controller().create_attribute(
                anno_node, f"inputs:{attr}", upstream_attr.get_resolved_type()
            )
            upstream_attr.connect(downstream_attr, True)
            og.Controller().create_attribute(
                anno_node,
                f"outputs:{attr}",
                upstream_attr.get_resolved_type(),
                og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT,
            )
            if attr == "dataPtr":
                attr = "Ptr"
            og.Controller().create_attribute(
                anno_node,
                f"outputs:ldr0{attr[0].upper()}{attr[1:]}",
                upstream_attr.get_resolved_type(),
                og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT,
            )
            if attr == "strides":
                continue
            og.Controller().create_attribute(
                anno_node,
                f"outputs:ldr1{attr[0].upper()}{attr[1:]}",
                upstream_attr.get_resolved_type(),
                og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT,
            )

        # Add type attribute to test
        og.Controller().create_attribute(
            anno_node,
            "outputs:ldr1DataType",
            og.Type(og.BaseDataType.TOKEN, 1, 1),
            og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT,
        )
        anno_node.get_attribute("outputs:ldr1DataType").set("float32")

        # Add dummy data suffixed attribute to make sure it gets captured correctly
        og.Controller().create_attribute(
            anno_node,
            "outputs:dummyData",
            og.Type(og.BaseDataType.FLOAT, 1, 1),
            og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT,
        )

        # Add Type suffixed attribute to make sure it gets captured correctly
        og.Controller().create_attribute(
            anno_node,
            "outputs:dummyType",
            og.Type(og.BaseDataType.FLOAT, 1, 1),
            og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT,
        )

        input_script = """def compute(db):
            db.outputs.dataPtr = db.inputs.dataPtr
            db.outputs.bufferSize = db.inputs.bufferSize
            db.outputs.strides = db.inputs.strides
            db.outputs.cudaDeviceIndex = db.inputs.cudaDeviceIndex
            db.outputs.height = db.inputs.height
            db.outputs.width = db.inputs.width

            db.outputs.ldr0Ptr = db.inputs.dataPtr
            db.outputs.ldr0BufferSize = db.inputs.bufferSize
            db.outputs.ldr0Strides = db.inputs.strides
            db.outputs.ldr0CudaDeviceIndex = db.inputs.cudaDeviceIndex
            db.outputs.ldr0Height = db.inputs.height
            db.outputs.ldr0Width = db.inputs.width

            db.outputs.ldr1Ptr = db.inputs.dataPtr
            db.outputs.ldr1BufferSize = db.inputs.bufferSize
            db.outputs.ldr1Strides = db.inputs.strides
            db.outputs.ldr1CudaDeviceIndex = db.inputs.cudaDeviceIndex
            db.outputs.ldr1Height = db.inputs.height // 2
            db.outputs.ldr1Width = db.inputs.width // 2
        """
        anno_node.get_attribute("inputs:script").set(input_script)

        await rep.orchestrator.step_async()

        data = anno.get_data()

        self.assertTrue("ldr0" in data, f"Could not find `ldr0` key in data. Found {data.keys()}")
        self.assertTrue("ldr1" in data, f"Could not find `ldr1` key in data. Found {data.keys()}")

        self.assertEqual(data["ldr0"].shape, (512, 1024, 4))
        self.assertEqual(data["ldr1"].shape, (256, 512, 4))

        self.assertEqual(data["ldr0"].dtype, np.uint8)
        self.assertEqual(data["ldr1"].dtype, np.float32)

        # Ensure `Data` suffixed attribute is correctly captured
        self.assertTrue("dummyData" in data["info"], f"`dummyData` attribute missing from annotator output: {data}")
        self.assertTrue("dummyType" in data["info"], f"`dummyType` attribute missing from annotator output: {data}")

    async def test_height_1_float3_array_anno(self):
        # Test for OM-116189
        # Not a perfect, test, anno in ticket has no format specified
        rp = rep.create.render_product(rep.create.camera(), (256, 1))
        anno = rep.annotators.get("LdrColor")
        anno.attach(rp)

        await rep.orchestrator.step_async()

        data = anno.get_data()

        self.assertEqual(data.shape, (256, 4))

    async def test_resolution_change(self):
        rp = rep.create.render_product(rep.create.camera(), (256, 256))
        anno = rep.annotators.get("LdrColor")
        anno.attach(rp)

        await rep.orchestrator.step_async()

        self.assertEqual(anno.get_data().shape[:2], (256, 256))

        # Detach
        anno.detach()

        # Change resolution
        rp.hydra_texture.set_width(1024)
        rp.hydra_texture.set_height(1024)

        # Re-attach
        anno.attach(rp)

        await rep.orchestrator.step_async()

        self.assertEqual(anno.get_data().shape[:2], (1024, 1024))

        # Test without detaching

        # Change resolution
        rp.hydra_texture.set_width(512)
        rp.hydra_texture.set_height(512)

        await rep.orchestrator.step_async()

        self.assertEqual(anno.get_data().shape[:2], (512, 512))

    async def test_invalid_device(self):
        await self._scene_setup()
        anno = rep.annotators.get("pointcloud", device="cpu")
        anno2 = rep.annotators.get("instance_segmentation_fast", device="cpu")
        anno.attach(self.render_product)
        anno2.attach(self.render_product)

        await rep.orchestrator.step_async()

        with self.assertRaises(ValueError):
            anno.get_data(device="invalid")

        # Simulate a graph reset removing __device node attribute
        stage = omni.usd.get_context().get_stage()
        with Usd.EditContext(stage, stage.GetSessionLayer()):
            anno.get_node().get_attribute("outputs:__device").set("")

        await rep.orchestrator.step_async()

        self.assertEqual(type(anno.get_data(device=None)["data"]), np.ndarray)

        # Replicate what OgnWriter does
        annotator_params = rep.AnnotatorRegistry._annotators.get(anno.name)
        annotator_id = str(anno.get_node().get_prim_path())
        data = annotator_utils.get_annotator_data(
            anno.get_node(), annotator_params, device=None, annotator_id=annotator_id
        )
        self.assertEqual(type(data["data"]), np.ndarray)

        # Cause a graph reset (caused by OM-99906)
        # Disabled as graph resets can cause a segfault
        # annotator_id = str(anno2.get_node().get_prim_path())    # Capture id because the node reference will be lost
        # annotator_params = rep.AnnotatorRegistry._annotators.get(anno2.name)
        # timeline = omni.timeline.get_timeline_interface()
        # timeline.set_time_codes_per_second(31)
        # timeline.commit()

        # await rep.orchestrator.step_async()

        # node = og.Controller().node(annotator_id)
        # data = annotator_utils.get_annotator_data(node, annotator_params, device=None, annotator_id=annotator_id)
        # self.assertEqual(type(data["data"]), np.ndarray)

    async def test_attach_annotators_invalid(self):
        anno = rep.annotators.get("LdrColor")
        rp = rep.create.render_product("/OmniverseKit_Persp", (512, 512))
        with self.assertRaises(ValueError):
            anno.attach([])
        with self.assertRaises(NotImplementedError):
            anno.attach([rp, rp])
        with self.assertRaises(NotImplementedError):
            anno.attach([rp, rp], [0, 1])

    async def test_bbox_semantic_types(self):
        await self._scene_setup()
        self.trigger.node.set_disabled(True)
        anno = rep.annotators.get(f"bounding_box_2d_tight")
        anno2 = rep.annotators.get(f"bounding_box_2d_loose", init_params={"semanticTypes": ["dummy"]})
        anno3 = rep.annotators.get(f"bounding_box_3d", init_params={"semanticFilter": "alias:*"})

        anno.attach(self.render_product)
        await rep.orchestrator.step_async()

        self.assertEqual(len(anno.get_data()["data"]), 3)

        anno2.attach(self.render_product)
        await rep.orchestrator.step_async()
        self.assertEqual(len(anno.get_data()["data"]), 3)
        self.assertEqual(len(anno2.get_data()["data"]), 0)

        anno3.attach(self.render_product)
        await rep.orchestrator.step_async()

        self.assertEqual(len(anno.get_data()["data"]), 3)
        self.assertEqual(len(anno2.get_data()["data"]), 0)
        self.assertEqual(len(anno3.get_data()["data"]), 2)

        anno2.detach()

        await rep.orchestrator.step_async()
        self.assertEqual(len(anno.get_data()["data"]), 3)
        self.assertEqual(len(anno3.get_data()["data"]), 2)

    async def test_bbox_fast_semantic_types(self):
        await self._scene_setup()
        self.trigger.node.set_disabled(True)
        anno = rep.annotators.get(f"bounding_box_2d_tight_fast")
        anno2 = rep.annotators.get(f"bounding_box_2d_loose_fast", init_params={"semanticTypes": ["dummy"]})
        anno3 = rep.annotators.get(f"bounding_box_3d_fast", init_params={"semanticFilter": "alias:*"})

        anno.attach(self.render_product)
        await rep.orchestrator.step_async()

        self.assertEqual(len(anno.get_data()["data"]), 3)

        anno2.attach(self.render_product)
        await rep.orchestrator.step_async()
        self.assertEqual(len(anno.get_data()["data"]), 3)
        self.assertEqual(len(anno2.get_data()["data"]), 0)

        anno3.attach(self.render_product)
        await rep.orchestrator.step_async()

        self.assertEqual(len(anno.get_data()["data"]), 3)
        self.assertEqual(len(anno2.get_data()["data"]), 0)
        self.assertEqual(len(anno3.get_data()["data"]), 2)

        anno2.detach()

        await rep.orchestrator.step_async()
        self.assertEqual(len(anno.get_data()["data"]), 3)
        self.assertEqual(len(anno3.get_data()["data"]), 2)

    async def test_detaching_interdependent_annotators(self):
        """Test that detaching an annotator also detaches any other annotators that depend on it

        Also ensure that shared annotators are not deactivated when only one annotator is detached.
        """
        rp = rep.create.render_product(rep.create.camera(), (512, 512))
        camera_params_anno = rep.annotators.get("camera_params")
        pointcloud_anno = rep.annotators.get("pointcloud")

        camera_params_anno.attach(rp)
        pointcloud_anno.attach(rp)

        camera_params_anno_path = str(camera_params_anno.get_node().get_prim_path())
        pointcloud_anno_path = str(pointcloud_anno.get_node().get_prim_path())

        # Test 1: Detach camera params annotator but keep pointcloud annotator active
        # Since camera params is shared, it should remain active
        camera_params_anno.detach()
        stage = omni.usd.get_context().get_stage()
        with Usd.EditContext(stage, stage.GetSessionLayer()):
            self.assertTrue(
                stage.GetPrimAtPath(camera_params_anno_path).IsValid(), "Camera params annotator should remain active"
            )
            self.assertTrue(
                stage.GetPrimAtPath(pointcloud_anno_path).IsValid(), "Pointcloud annotator should remain active"
            )

        # Test 2: Detach both pointcloud annotator - no annotators should be active
        pointcloud_anno.detach()
        with Usd.EditContext(stage, stage.GetSessionLayer()):
            self.assertFalse(
                stage.GetPrimAtPath(camera_params_anno_path).IsValid(), "Camera params annotator should not be active"
            )
            self.assertFalse(
                stage.GetPrimAtPath(pointcloud_anno_path).IsValid(), "Pointcloud annotator should not be active"
            )

        # Re-attach both annotators
        camera_params_anno.attach(rp)
        pointcloud_anno.attach(rp)

        # Test 3: Detach pointcloud annotator. It should be deactivated but camera params should remain active
        pointcloud_anno.detach()
        with Usd.EditContext(stage, stage.GetSessionLayer()):
            self.assertTrue(
                stage.GetPrimAtPath(camera_params_anno_path).IsValid(), "Camera params annotator should remain active"
            )
            self.assertFalse(
                stage.GetPrimAtPath(pointcloud_anno_path).IsValid(), "Pointcloud annotator should not be active"
            )

    async def test_instance_segmentation_fast_semantic_types(self):
        await self._scene_setup()
        anno = rep.annotators.get(f"instance_segmentation_fast", init_params={"semanticTypes": ["alias"]})

        anno.attach(self.render_product)
        for _ in range(10):
            await rep.orchestrator.step_async()

        self.assertEqual(len(anno.get_data()["info"]["idToLabels"]), 4)
        self.assertEqual(len(np.unique(anno.get_data()["data"])), 3)  # background, donut, ball, torus

        for id, semantic in anno.get_data()["info"]["idToSemantics"].items():
            if id != 0 and id != 1:
                self.assertTrue("alias" in semantic)
                self.assertFalse("class" in semantic)

    async def test_instance_segmentation_semantic_types(self):
        await self._scene_setup()
        anno = rep.annotators.get(f"instance_segmentation", init_params={"semanticTypes": ["alias"]})

        anno.attach(self.render_product)
        for _ in range(10):
            await rep.orchestrator.step_async()

        self.assertEqual(len(anno.get_data()["info"]["idToLabels"]), 4)
        self.assertEqual(len(np.unique(anno.get_data()["data"])), 3)  # background, donut, ball, torus

        for id, semantic in anno.get_data()["info"]["idToSemantics"].items():
            if id != "0" and id != "1":
                self.assertTrue("alias" in semantic)
                self.assertFalse("class" in semantic)

    async def test_semantic_segmentation_semantic_filter(self):
        await self._scene_setup()
        anno = rep.annotators.get(f"semantic_segmentation", init_params={"semanticFilter": "alias:*"})

        anno.attach(self.render_product)
        for _ in range(10):
            await rep.orchestrator.step_async()

        self.assertEqual(
            len(anno.get_data()["info"]["idToLabels"]),
            4,
            f"Expected 4 labels, got {anno.get_data()['info']['idToLabels']}",
        )
        self.assertEqual(
            len(np.unique(anno.get_data()["data"])),
            3,
            f"Expected 3 unique values, got {np.unique(anno.get_data()['data'])}",
        )  # background, donut, ball, torus

        for id, label in anno.get_data()["info"]["idToLabels"].items():
            if id != "0" and id != "1":
                self.assertTrue("alias" in label)
                self.assertFalse("class" in label)
