# SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

import io
import json
import os
from typing import List

import numpy as np
from omni.replicator.core import AnnotatorRegistry, Writer, WriterRegistry, backends
from omni.replicator.core import functional as F

__version__ = "0.0.1"


class VisualizerWriter(Writer):
    def __init__(self, output_dir: str, asset_paths: list, overwrite: bool = True, image_output_format: str = "png"):
        self._output_dir = output_dir
        self._asset_paths = asset_paths
        self.overwrite = overwrite
        self._backend = backends.get("DiskBackend")
        self._backend.initialize(output_dir=output_dir)
        self.backend = self._backend
        self._frame_id = 0
        self._sequence_id = 0
        self._image_output_format = image_output_format
        self._output_data_format = {}
        self.annotators = []
        self.version = __version__

        self.annotators.append(AnnotatorRegistry.get_annotator("rgb"))

        self._one_asset_data = []

    def write(self, data: dict):
        data_dir = os.path.join(self._output_dir, "visualize_models")
        os.makedirs(data_dir, exist_ok=True)

        for annotator in data.keys():
            if annotator.startswith("rgb"):
                rgb_data = data[annotator]

        self._one_asset_data.append(rgb_data)

        if self._frame_id % 4 == 3:
            combined_asset_data = np.concatenate(self._one_asset_data, axis=1)

            asset_name = self._asset_paths[self._frame_id // 4].split("/")[-1].split(".")[0]
            file_path = f"{asset_name}.{self._image_output_format}"

            self._backend.schedule(F.write_image, data=combined_asset_data, path=os.path.join(data_dir, file_path))

            self._one_asset_data = []

        self._frame_id += 1


WriterRegistry.register(VisualizerWriter)
