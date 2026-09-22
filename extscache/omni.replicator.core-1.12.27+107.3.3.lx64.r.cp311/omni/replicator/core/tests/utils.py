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
import shutil
import unittest
from pathlib import Path

import omni.kit.test
from PIL import Image

TEST_OUTPUT_DIR = Path(omni.kit.test.utils.get_test_output_path())


def save_image(data, path):
    Image.fromarray(data).save(path)


def tc_output_image_comparison(name, golden_dir, out_dir, image_data=None):
    """
    Have TC disaply both the golden and test result image inline with test output. Save the image if
    it is passed in as an array.
    """
    if image_data.any():
        result_path = os.path.join(out_dir, f"{name}_result.png")
        save_image(image_data, result_path)
    else:
        result_path = os.path.join(out_dir, f"{name}.png")
    print(f"##teamcity[publishArtifacts '{golden_dir} => golden']\n")
    print(f"##teamcity[publishArtifacts '{result_path} => results']\n")
    print(f"##teamcity[testMetadata type='image' name='{name} Reference' value='golden/{name}.png']\n")
    print(f"##teamcity[testMetadata type='image' name='{name} Generated' value='results/{name}_result.png']\n")


def gitlab_output_image_comparison(name, golden_image_filepath, result_image_filepath=None, image_data=None):
    """Write the image comparisons to a folder in _testoutput. Used for tests on gitlab-ci."""
    results_path = Path(TEST_OUTPUT_DIR).joinpath(name)
    results_path.mkdir(exist_ok=True)

    if image_data is None and result_image_filepath is None:
        print("Neither result image or result image data provided!")
        return

    # If the result image array is provided, save that to the results folder, otherwise copy the result image
    if image_data is not None and image_data.any():
        save_image(image_data, Path(results_path).joinpath(f"result.png"))
    else:
        shutil.copy(result_image_filepath, results_path)
        copied_file = Path(results_path).joinpath(Path(result_image_filepath).name)
        copied_file.rename(Path(copied_file.parent).joinpath(f"{copied_file.stem}_result{copied_file.suffix}"))

    # Copy the golden image
    shutil.copyfile(golden_image_filepath, Path(results_path).joinpath(f"golden{Path(golden_image_filepath).suffix}"))
