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

import carb
import numpy as np
import omni.replicator.core.functional as F
import omni.usd


class TestIO(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        self._tmp_dir = carb.tokens.get_tokens_interface().resolve("${temp}/test_io")

    def test_read_write_exr(self):
        compressions = ["ZIP", "PIZ", "PXR24", "B44", "LC"]
        array_shapes = [(100, 100), (100, 100, 1), (100, 100, 2), (100, 100, 3), (100, 100, 4)]
        dtypes = [np.float32, np.float16, np.uint8, np.int32]

        def check_exr_file(file_path, gt_data):
            # Check if the file was created
            self.assertTrue(os.path.exists(file_path))

            # Check if the file is not empty
            self.assertTrue(os.path.getsize(file_path) > 0)

            # Check if the file correct
            data = F.io_functions.read_exr(file_path)
            # The loader always yields float32; cast to the original dtype so
            # that the comparison doesn't fail solely due to dtype mismatch.
            np.testing.assert_allclose(data.astype(gt_data.dtype).squeeze(), gt_data.squeeze())

        for array_shape in array_shapes:
            for dtype in dtypes:
                for compression in compressions:
                    data = np.random.rand(*array_shape).astype(dtype)
                    path = f"{self._tmp_dir}/test_{array_shape}_{data.dtype.name}_{compression}.exr"
                    F.io_functions.write_exr(path, data, compression=compression)
                    check_exr_file(path, data)
