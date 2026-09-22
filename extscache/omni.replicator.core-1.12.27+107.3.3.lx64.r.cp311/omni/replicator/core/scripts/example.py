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

import glob
import os

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(CUR_DIR, "data", "assets")
TEXTURES_DIR = os.path.join(CUR_DIR, "data", "textures")
UV_TEXTURES_DIR = os.path.join(CUR_DIR, "data", "uv_textures")
MATERIALS_DIR = os.path.join(CUR_DIR, "data", "materials")
ASSETS = glob.glob(os.path.join(ASSETS_DIR, "*"))
TEXTURES = glob.glob(os.path.join(TEXTURES_DIR, "*"))
MATERIALS = glob.glob(os.path.join(MATERIALS_DIR, "*.mdl"))
MDL_JSON_EXAMPLE = {
    "name": "RepMaterialTest",
    "nodes": {
        "material": {"type": "material"},
        "a": {"type": "diffuse", "name": "base", "out_type": "Token"},
        "b": {"type": "diffuse", "name": "base", "out_type": "Token"},
        "blend": {"type": "surface_falloff", "name": "blend", "out_type": "Token"},
    },
    "edges": {
        "1": {"output": {"node": "a", "pin": "out"}, "input": {"node": "blend", "pin": "base"}},
        "2": {"output": {"node": "b", "pin": "out"}, "input": {"node": "blend", "pin": "blend"}},
        "3": {"input": {"node": "a", "values": {"diffuse_color": [0.0, 0.0, 1.0]}}},
        "4": {"input": {"node": "b", "values": {"diffuse_color": [1.0, 0.0, 0.0]}}},
        "5": {"output": {"node": "blend", "pin": "out"}, "input": {"node": "material", "pin": "surface"}},
        "6": {"input": {"node": "blend", "values": {"facing_weight": 0.5}}},
    },
}
