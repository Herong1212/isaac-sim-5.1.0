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

import json
import os
import unittest
from pathlib import Path

import carb
import numpy as np
import omni.kit
import omni.replicator.core as rep
import omni.timeline
import omni.usd
from PIL import Image, ImageDraw

TEST_DATA_DIR = Path(os.path.dirname(os.path.realpath(__file__))).joinpath("data")


class TestSkeletonAnnotator(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        # Setup file directory for loading scene
        self.TEST_DIR = os.path.join(TEST_DATA_DIR, "objects")
        self.GOLDEN_DIR = os.path.join(TEST_DATA_DIR, "golden", "skeleton_tests")
        self.out_dir = carb.tokens.get_tokens_interface().resolve("${temp}/test_skeleton_annotator")
        os.makedirs(self.out_dir, exist_ok=True)

    async def _setup_stage(self, map_path, rest, timestamp=0):
        # Open stage via USD File
        (result, err) = await omni.usd.get_context().open_stage_async(
            map_path, omni.usd.UsdContextInitialLoadSet.LOAD_ALL
        )

        # Importantly. this sets `omni.timeline.set_play_every_frame(True)` which guarantees the graph is executed every frame
        rep.orchestrator._orchestrator._set_capture_settings()

        await omni.kit.app.get_app().next_update_async()

        # Setup stage components and viewport
        self._stage = omni.usd.get_context().get_stage()
        self.camera_width, self.camera_height = 1024, 512
        camera_path = "/World/Camera"
        self._rp = rep.create.render_product(camera_path, (self.camera_width, self.camera_height))

        # Create the annotator
        skel_annotator = rep.annotators.get("skeleton_data")
        self._annotator = skel_annotator.attach(self._rp)

        # Get random time frame in stage
        self._timeline_iface = omni.timeline.get_timeline_interface()
        if rest:
            self._timeline_iface.set_current_time(0)
        elif timestamp > 0:
            self._timeline_iface.set_current_time(timestamp)
        else:
            self._timeline_iface.set_current_time(np.random.uniform(1.0, 30.0))
        self._timeline_iface.commit_silently()

        await rep.orchestrator.step_async()

    async def _get_skeletons_data_from_stage(self):
        skel_data = self._annotator.get_data()["skeletonData"]
        output_data = json.loads(skel_data)
        return output_data

    async def _write_skeleton_data(self, skels_data):
        # Create directory to output image
        output_subdir = os.path.join(self.out_dir, "annotated_skeleton")
        os.makedirs(output_subdir, exist_ok=True)

        # Setup image parameters for PIL
        img = Image.new("RGB", (self.camera_width, self.camera_height), (0, 0, 0))
        img_draw = ImageDraw.Draw(img)

        for skel_data in skels_data:
            # Retrieve 2d point translations and their parents for drawing on image
            parents = np.array(skel_data["skeleton_parents"])
            pose_2d_translations = np.array(skel_data["translations_2d"])

            # Iterate through and plot all joints and draw all skeleton lines
            for i, pos in enumerate(pose_2d_translations):
                if i > 0:
                    # Plot bones
                    x1 = pos[0]
                    y1 = pos[1]
                    x2 = pose_2d_translations[parents[i].item()][0]
                    y2 = pose_2d_translations[parents[i].item()][1]
                    img_draw.line([(int(x1), int(y1)), (int(x2), int(y2))], fill=(255, 0, 0, 255), width=1)

                    # Plot joints
                    radius = 4
                    ul_point = (int(x1) - radius, int(y1) - radius)
                    lr_point = (int(x1) + radius, int(y1) + radius)
                    img_draw.arc([ul_point, lr_point], start=0, end=360, fill="blue")

        json_fpath = os.path.join(output_subdir, "2d_annotated_skeletons.json")
        json.dump(skels_data, open(json_fpath, "w"))

        # Save image to specified file and directory
        fpath = os.path.join(output_subdir, "2d_annotated_skeletons.png")
        img.save(fpath)

    async def test_single_nonanimated_skeleton_annotations(self):
        map_path = os.path.join(self.TEST_DIR, "anim_skel_test_scene.usd")
        await self._setup_stage(map_path, True)
        skels_data = await self._get_skeletons_data_from_stage()
        await self._write_skeleton_data(skels_data)

        # Check that file was written
        self.assertTrue(os.path.isfile(os.path.join(self.out_dir, "annotated_skeleton/2d_annotated_skeletons.png")))

        # Compare output images
        test_file_path = os.path.join(self.out_dir, "annotated_skeleton/2d_annotated_skeletons.png")
        test_data = np.array(Image.open(test_file_path))

        golden_file_path = os.path.join(self.GOLDEN_DIR, "test_single_nonanimated_skeleton_annotations.png")
        golden_data = np.array(Image.open(golden_file_path))

        std_dev = np.sqrt(np.square(test_data - golden_data).astype(float).mean())

        self.assertLess(std_dev, 2)

        # Compare output json data
        test_file_path = os.path.join(self.out_dir, "annotated_skeleton/2d_annotated_skeletons.json")
        test_data = json.load(open(test_file_path, "r"))

        golden_file_path = os.path.join(self.GOLDEN_DIR, "test_single_nonanimated_skeleton_annotations.json")
        golden_data = json.load(open(golden_file_path, "r"))

        for key, val in test_data[0].items():
            if key in ["joint_occlusions", "occlusion_types"]:
                continue
            if isinstance(val, list) and not isinstance(val[0], str):
                np.testing.assert_allclose(np.array(val), np.array(golden_data[0][key]), atol=1e-3)
            else:
                self.assertEqual(val, golden_data[0][key], f"Values in {key} are different!")

    async def test_skeleton_in_view(self):
        person_src = os.path.join(self.TEST_DIR, "Worker/Worker.usd")
        with rep.new_layer():
            person = rep.create.from_usd(person_src, semantics=[("class", "person")])

            # Create camera and position it so that the person is partially outside the view
            camera = rep.create.camera(position=(8, -220.0, 240.0), rotation=(77.0, 0.0, 3.5))

            skel_anno = rep.annotators.get("skeleton_data")
            render_product = rep.create.render_product(camera, (1024, 1024))
            skel_anno.attach(render_product)

            await rep.orchestrator.step_async()

            data = skel_anno.get_data()

            # Check that the person is not in view
            self.assertTrue(data["inView"][0] == False)

    @unittest.skip("FIXME - causes Kit to hang")
    async def test_partially_occluded_skeleton_joint_annotations(self):
        person_src = os.path.join(self.TEST_DIR, "Worker/Worker.usd")
        with rep.new_layer():
            person = rep.create.from_usd(person_src, semantics=[("class", "person")])
            area = rep.create.cube(scale=2, position=(0.0, 0.0, 100.0), visible=False)  # Area to scatter spheres in

            camera = rep.create.camera(
                position=(8, -100.0, 100.0), rotation=(77.0, 0.0, 3.5), projection_type="fisheyePolynomial"
            )
            render_product = rep.create.render_product(camera, (1024, 1024))

            def randomize_spheres():
                spheres = rep.create.sphere(scale=0.1, count=100)
                with spheres:
                    rep.randomizer.scatter_3d(area)
                return spheres.node

            rep.randomizer.register(randomize_spheres)

            with rep.trigger.on_frame(max_execs=1):
                rep.randomizer.randomize_spheres()

            # Initialize and attach writer
            writer = rep.WriterRegistry.get("BasicWriter")
            writer.initialize(output_dir=self.out_dir, rgb=True, skeleton_data=True)
            writer.attach([render_product])

        timeline = omni.timeline.get_timeline_interface()
        timeline.set_end_time(100.0)
        await omni.kit.app.get_app().next_update_async()
        timeline.play()
        await rep.orchestrator.step_async()  # Golden is captured at frame=1
        await rep.orchestrator.stop_async()

        # Check that file was written
        self.assertTrue(os.path.isfile(os.path.join(self.out_dir, "rgb_0000.png")), "Unable to find rgb file")

        # Compare output images
        test_file_path = os.path.join(self.out_dir, "rgb_0000.png")
        test_data = np.array(Image.open(test_file_path))

        golden_file_path = os.path.join(self.GOLDEN_DIR, "test_partially_occluded_skeleton_annotations.png")
        golden_data = np.array(Image.open(golden_file_path))

        std_dev = np.sqrt(np.square(test_data - golden_data).astype(float).mean())

        self.assertLess(std_dev, 2, "Test image differs from golden")

        # Compare output json data
        test_file_path = os.path.join(self.out_dir, "skeleton_0000.json")
        test_data = json.load(open(test_file_path, "r"))

        golden_file_path = os.path.join(self.GOLDEN_DIR, "test_partially_occluded_skeleton_annotations.json")
        golden_data = json.load(open(golden_file_path, "r"))

        for key, val in test_data["skeleton_0"].items():
            if isinstance(val, list) and not isinstance(val[0], str):
                np.testing.assert_allclose(np.array(val), np.array(golden_data["skeleton_0"][key]), atol=1e-3)
            else:
                self.assertEqual(val, golden_data["skeleton_0"][key], f"Values in {key} are different!")

    async def test_single_animated_skeleton_annotations(self):
        map_path = os.path.join(self.TEST_DIR, "anim_skel_test_scene.usd")
        await self._setup_stage(map_path, False)
        skels_data = await self._get_skeletons_data_from_stage()
        await self._write_skeleton_data(skels_data)

        # Check that file was written
        self.assertTrue(os.path.isfile(os.path.join(self.out_dir, "annotated_skeleton/2d_annotated_skeletons.png")))

        # Compare output images
        test_file_path = os.path.join(self.out_dir, "annotated_skeleton/2d_annotated_skeletons.png")
        test_data = np.array(Image.open(test_file_path))

        golden_file_path = os.path.join(self.GOLDEN_DIR, "test_single_animated_skeleton_annotations.png")
        golden_data = np.array(Image.open(golden_file_path))

        std_dev = np.sqrt(np.square(test_data - golden_data).astype(float).mean())

        self.assertLess(std_dev, 2)

        # Compare output json data
        test_file_path = os.path.join(self.out_dir, "annotated_skeleton/2d_annotated_skeletons.json")
        test_data = json.load(open(test_file_path, "r"))

        golden_file_path = os.path.join(self.GOLDEN_DIR, "test_single_animated_skeleton_annotations.json")
        golden_data = json.load(open(golden_file_path, "r"))

        for key, val in test_data[0].items():
            if key in ["joint_occlusions", "occlusion_types"]:
                continue
            if isinstance(val, list) and not isinstance(val[0], str):
                np.testing.assert_allclose(np.array(val), np.array(golden_data[0][key]), atol=1e-3)
            else:
                self.assertEqual(val, golden_data[0][key], f"Values in {key} are different!")

    async def test_multiple_animated_skeleton_annotations(self):
        map_path = os.path.join(self.TEST_DIR, "multiple_anim_skel_test_scene.usd")
        await self._setup_stage(map_path, False)
        skels_data = await self._get_skeletons_data_from_stage()
        await self._write_skeleton_data(skels_data)

        # Check that file was written
        self.assertTrue(os.path.isfile(os.path.join(self.out_dir, "annotated_skeleton/2d_annotated_skeletons.png")))

        # Compare output images
        test_file_path = os.path.join(self.out_dir, "annotated_skeleton/2d_annotated_skeletons.png")
        test_data = np.array(Image.open(test_file_path))

        golden_file_path = os.path.join(self.GOLDEN_DIR, "test_multiple_animated_skeleton_annotations.png")
        golden_data = np.array(Image.open(golden_file_path))

        std_dev = np.sqrt(np.square(test_data - golden_data).astype(float).mean())

        self.assertLess(std_dev, 2)

        # Compare output json data
        test_file_path = os.path.join(self.out_dir, "annotated_skeleton/2d_annotated_skeletons.json")
        test_data = json.load(open(test_file_path, "r"))

        golden_file_path = os.path.join(self.GOLDEN_DIR, "test_multiple_animated_skeleton_annotations.json")
        golden_data = json.load(open(golden_file_path, "r"))

        for idx, item in enumerate(golden_data):
            for key, val in test_data[idx].items():
                if key in ["joint_occlusions", "occlusion_types"]:
                    continue
                if isinstance(val, list) and not isinstance(val[0], str):
                    np.testing.assert_allclose(np.array(val), np.array(golden_data[idx][key]), atol=1e-3)
                else:
                    self.assertEqual(val, golden_data[idx][key], f"Values in {key} are different!")

    async def test_clipped_skeleton_annotations(self):
        map_path = os.path.join(self.TEST_DIR, "nonanim_clipped_skel_test_scene.usd")
        await self._setup_stage(map_path, True)
        skels_data = await self._get_skeletons_data_from_stage()
        await self._write_skeleton_data(skels_data)

        # Check that file was written
        self.assertTrue(os.path.isfile(os.path.join(self.out_dir, "annotated_skeleton/2d_annotated_skeletons.png")))

        # Compare output images
        test_file_path = os.path.join(self.out_dir, "annotated_skeleton/2d_annotated_skeletons.png")
        test_data = np.array(Image.open(test_file_path))

        golden_file_path = os.path.join(self.GOLDEN_DIR, "test_clipped_skeleton_annotations.png")
        golden_data = np.array(Image.open(golden_file_path))

        std_dev = np.sqrt(np.square(test_data - golden_data).astype(float).mean())

        self.assertLess(std_dev, 2)

        # Compare output json data
        test_file_path = os.path.join(self.out_dir, "annotated_skeleton/2d_annotated_skeletons.json")
        test_data = json.load(open(test_file_path, "r"))

        golden_file_path = os.path.join(self.GOLDEN_DIR, "test_clipped_skeleton_annotations.json")
        golden_data = json.load(open(golden_file_path, "r"))

        for key, val in test_data[0].items():
            if key in ["joint_occlusions", "occlusion_types"]:
                continue
            if isinstance(val, list) and not isinstance(val[0], str):
                np.testing.assert_allclose(np.array(val), np.array(golden_data[0][key]), atol=1e-3)
            else:
                self.assertEqual(val, golden_data[0][key], f"Values in {key} are different!")

    @unittest.skip("omni.anim.skelJoint causing crashes. Disable for now.")  # FIXME: ecameracci to investigate
    async def test_single_animated_skeleton_annotations_skeljoint(self):
        map_path = os.path.join(self.TEST_DIR, "anim_skel_test_scene.usd")
        await self._setup_stage(map_path, False)

        # Specific to using skelJoint
        self._data_node.get_attribute("inputs:useSkelJoints").set(True)
        omni.usd.get_context().get_selection().select_all_prims("OmniJoint")
        for _ in range(4):
            await omni.kit.app.get_app().next_update_async()

        skels_data = await self._get_skeletons_data_from_stage()
        await self._write_skeleton_data(skels_data)

        # Check that file was written
        self.assertTrue(os.path.isfile(os.path.join(self.out_dir, "annotated_skeleton/2d_annotated_skeletons.png")))

        # Compare output images
        test_file_path = os.path.join(self.out_dir, "annotated_skeleton/2d_annotated_skeletons.png")
        test_data = np.array(Image.open(test_file_path))

        golden_file_path = os.path.join(self.GOLDEN_DIR, "test_single_animated_skeleton_annotations.png")
        golden_data = np.array(Image.open(golden_file_path))

        std_dev = np.sqrt(np.square(test_data - golden_data).astype(float).mean())

        self.assertLess(std_dev, 2)

        # Compare output json data
        test_file_path = os.path.join(self.out_dir, "annotated_skeleton/2d_annotated_skeletons.json")
        test_data = json.load(open(test_file_path, "r"))

        golden_file_path = os.path.join(self.GOLDEN_DIR, "test_single_animated_skeleton_annotations.json")
        golden_data = json.load(open(golden_file_path, "r"))

        for key, val in test_data[0].items():
            if key in ["joint_occlusions", "occlusion_types"]:
                continue
            if isinstance(val, list) and not isinstance(val[0], str):
                np.testing.assert_allclose(np.array(val), np.array(golden_data[0][key]), atol=1e-3)
            else:
                self.assertEqual(val, golden_data[0][key], f"Values in {key} are different!")
