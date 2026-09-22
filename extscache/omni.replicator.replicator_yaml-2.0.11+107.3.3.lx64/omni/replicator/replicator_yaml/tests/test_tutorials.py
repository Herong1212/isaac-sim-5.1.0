# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

import filecmp
import glob
import os
import platform
import shutil
import sys
import unittest
from pathlib import Path

import carb
import numpy as np
import omni.kit
import omni.replicator.core as rep
import omni.usd
from omni.replicator.core.tests.utils import gitlab_output_image_comparison, tc_output_image_comparison
from omni.replicator.replicator_yaml.scripts.replicator_yaml_extension import ReplicatorYAMLExtension
from PIL import Image

TEST_DATA_DIR = Path(os.path.dirname(os.path.realpath(__file__))).joinpath("data")
GOLDEN_DATA_DIR = carb.tokens.get_tokens_interface().resolve(
    "${omni.replicator.extended_tests}/omni/replicator/extended_tests/data"
)


# End-to-end tests for all tutorial scripts
class TestTutorials(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        carb.settings.get_settings().set("/omni/replicator/RTSubframes", 1)
        carb.settings.get_settings().set("/rtx-transient/post/aa/limitedOps", False)
        await omni.usd.get_context().new_stage_async()

        rep.set_global_seed(1234)
        rep.settings.set_render_rtx_realtime(antialiasing="FXAA")

        # Find tutorials
        scripts_dir = os.path.join(TEST_DATA_DIR, "tutorials")
        self.tutorials = []
        for script_dir in os.listdir(scripts_dir):
            for script in os.listdir(os.path.join(scripts_dir, script_dir)):
                if script.startswith("tutorial") and script.endswith(".yaml"):
                    self.tutorials.append(os.path.join(scripts_dir, script_dir, script))

        # self.out_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "_tutorial_out")
        self.out_dir = carb.tokens.get_tokens_interface().resolve("${temp}/tutorial")
        carb.settings.get_settings().set("/omni/replicator/backends/disk/root_dir", self.out_dir)
        self.golden_dir = os.path.join(GOLDEN_DATA_DIR, "golden")

    async def tearDown(self):
        # Delete file created for absolute path write blob test
        shutil.rmtree(self.out_dir, ignore_errors=True)
        carb.settings.get_settings().set("/omni/replicator/RTSubframes", 1)
        carb.settings.get_settings().set("/omni/replicator/replicatorYaml/yamlPath", "")
        carb.settings.get_settings().set("/rtx-transient/post/aa/limitedOps", False)
        await omni.usd.get_context().new_stage_async()

    def _compare_dirs(self, dir_0, dir_1):
        def recursive_check(dcmp):
            if dcmp.left_only or dcmp.right_only:
                return False, dcmp.report()
            for sub_dcmp in dcmp.subdirs.values():
                success, msg = recursive_check(sub_dcmp)
                if not success:
                    return success, msg
            return True, None

        dcmp = filecmp.dircmp(dir_0, dir_1)
        return recursive_check(dcmp)

    def _compare_images(self, image_path_0, image_path_1, threshold=2.5):
        data_0 = np.asarray(Image.open(image_path_0))
        data_1 = np.asarray(Image.open(image_path_1))
        std_dev = np.sqrt(np.square(data_0 - data_1).astype(float).mean())
        image_name = Path(image_path_0).name.split(".")[0]
        out_dir = Path(image_path_0).parent
        tutorial_name = Path(image_path_1).parent.parent.parts[-1]
        if std_dev > threshold:
            if omni.kit.test.utils.is_running_in_teamcity():
                tc_output_image_comparison(image_name, self.golden_dir, out_dir)
            if omni.kit.test.utils.is_running_in_gitlab():
                gitlab_output_image_comparison(f"{tutorial_name}_yaml", image_path_1, image_path_0)
        return std_dev < threshold, f"{std_dev} > {threshold}"

    @unittest.skipIf(platform.machine() == "aarch64", "skipped on ARM, until MR-36549 is merged")
    @unittest.skipIf(os.getenv("ETM_ACTIVE"), "skipped in ETM")
    async def test_tutorials(self):
        failures = []
        for tutorial in self.tutorials:
            # Reset subframes because it is different for different test.
            await omni.usd.get_context().new_stage_async()
            carb.settings.get_settings().set("/omni/replicator/RTSubframes", 1)
            tutorial_name = os.path.splitext(os.path.split(tutorial)[-1])[0]

            print(f"Testing {tutorial_name}...")

            # Skip color tutorial, issue setting FXAA (OMREQ-1364)
            if "color" in tutorial_name:
                continue

            # Clear output directory
            shutil.rmtree(self.out_dir, ignore_errors=True)

            # Skip tests requiring localhost access
            with open(tutorial, "r") as f:
                yaml_file = f.readlines()
            skip_test = False
            for line in yaml_file:
                if "omniverse://localhost" in line:
                    # Test access to server
                    success, _ = omni.client.get_server_info("omniverse://localhost")
                    skip_test = success != omni.client.Result.OK
                    if skip_test:
                        print(f"Skipping {tutorial_name}, it requires access to localhost nucleus server.")
                    break
            if skip_test:
                continue

            carb.settings.get_settings().set("/omni/replicator/replicatorYaml/yamlPath", tutorial)
            await ReplicatorYAMLExtension._autorun(exit_on_complete=False)
            golden_dir = os.path.join(self.golden_dir, "tutorials", tutorial_name)

            # Copy ground truth output for new tests
            if not os.path.exists(golden_dir):
                shutil.copytree(self.out_dir, golden_dir)

            # Compare directory structures
            success, msg = self._compare_dirs(self.out_dir, golden_dir)
            self.assertTrue(success, msg)

            # Compare files (images only for now)
            current_fail = False
            for f in glob.iglob(os.path.join(self.out_dir, "**"), recursive=True):
                if os.path.isdir(f):
                    continue

                rel_path = os.path.relpath(f, self.out_dir)
                golden_path = os.path.join(golden_dir, rel_path)

                ext = os.path.splitext(f)[-1]
                if ext in [".png"]:
                    result, msg = self._compare_images(f, golden_path)
                    try:
                        self.assertTrue(
                            result,
                            f"Tutorial: {tutorial_name} - Image {f} is different from golden {golden_path} {msg}",
                        )
                    except AssertionError as e:
                        failures.append(tutorial_name)
                        current_fail = True
                        print("FAIL!\n")
                        print(e)

            shutil.rmtree(self.out_dir)
            if not current_fail:
                print("OK!\n")

        self.assertFalse(bool(failures), f"One or more tutorial tests has failed! Failing tests: {failures}")
