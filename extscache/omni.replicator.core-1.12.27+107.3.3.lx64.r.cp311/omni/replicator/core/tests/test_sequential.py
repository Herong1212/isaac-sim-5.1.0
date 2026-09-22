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
import platform
import tempfile
from pathlib import Path

import numpy as np
import omni.kit
import omni.replicator.core as rep
import omni.replicator.core.functional as F
from omni.replicator.core import backends
from PIL import Image


class TestSequential(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self.absolute_path = (Path(tempfile.mkdtemp()) / "rep_test_absolute_path").as_posix()
        await omni.usd.get_context().new_stage_async()

    def test_docstrings(self):
        """Test module docstring examples"""
        failures, test_counts = doctest.testmod(rep.backends.sequential)
        if failures:
            self.fail(f"Encountered {failures} failures in {test_counts} tests.")

    async def test_sequential_modify_path(self):
        backend_abs = backends.BackendDispatch(output_dir=self.absolute_path)
        exr_data = np.zeros((10, 10), dtype=np.float32)
        abs_test_data_path = "exr_data.exr"
        expected_output_abs_test_data_path = "exr_data_1_2.exr"
        add_suffix_lambda = lambda image_name, suffix="_1": (
            f"{image_name.rsplit('.', 1)[0]}{suffix}.{image_name.rsplit('.', 1)[1]}"
            if "." in image_name
            else image_name
        )

        class add_suffix_class:
            def __init__(self, suffix="_2"):
                self.suffix = suffix

            def __call__(self, input_string):
                input_string_parts = input_string.split(".")
                if len(input_string_parts) >= 2:
                    extension = input_string_parts[-1]
                    base_name = "".join(input_string_parts[:-1])
                    new_image_name = f"{base_name}{self.suffix}.{extension}"
                    return new_image_name

        sequence = backends.Sequential(
            add_suffix_lambda,
            add_suffix_class("_2"),
        )

        backend_abs.schedule(F.write_image, path=sequence(abs_test_data_path), data=exr_data)

        backend_abs.wait_until_done()
        self.assertTrue(os.path.exists(os.path.join(self.absolute_path, expected_output_abs_test_data_path)))

    async def test_sequential_modify_data(self):
        backend_abs = backends.BackendDispatch(output_dir=self.absolute_path)
        abs_test_data_path = "random_data.png"

        def add_black_mask(array):
            return np.zeros_like(array)

        sequence = backends.Sequential(
            add_black_mask,
        )

        random_data = np.random.randint(0, 256, size=(5, 5, 3), dtype=np.uint8)
        backend_abs.schedule(F.write_image, path=abs_test_data_path, data=sequence(random_data))

        backend_abs.wait_until_done()
        self.assertTrue(os.path.exists(os.path.join(self.absolute_path, abs_test_data_path)))

        print(platform.machine())
        if platform.machine() != "AMD64" or platform.machine() != "x86_64":
            image = Image.open(os.path.join(self.absolute_path, abs_test_data_path), formats=["PNG"])
        else:
            image = Image.open(os.path.join(self.absolute_path, abs_test_data_path))
        image_array = np.array(image)

        reference_zero_array = np.zeros((5, 5, 3), dtype=np.uint8)
        self.assertTrue(np.array_equal(image_array, reference_zero_array))

    async def test_setting_float(self):
        seq = [1.0, 2.0, 3.0, 4.0, 5.0]
        with rep.trigger.on_frame(max_execs=5):
            rep.modify.time(rep.distribution.sequence(seq, name="value"))

        for i in range(5):
            await rep.orchestrator.step_async()
            self.assertEqual(omni.timeline.get_timeline_interface().get_current_time(), seq[i])
