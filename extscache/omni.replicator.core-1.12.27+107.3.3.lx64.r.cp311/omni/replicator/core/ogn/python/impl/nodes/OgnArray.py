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

"""
This is the implementation of the OGN node defined in OgnOnNewFrame.ogn
"""
import omni.graph.core as og
import omni.usd
from omni.replicator.core import utils


def get_type(name):
    if "matrix" not in name:
        if "4d" in name or "double4" in name:
            return og.Type(og.BaseDataType.DOUBLE, 4, 1)
        elif "4f" in name or "float4" in name:
            return og.Type(og.BaseDataType.FLOAT, 4, 1)
        elif "3d" in name or "double3" in name:
            return og.Type(og.BaseDataType.DOUBLE, 3, 1)
        elif "3f" in name or "float3" in name:
            return og.Type(og.BaseDataType.FLOAT, 3, 1)
        elif "2d" in name or "double2" in name:
            return og.Type(og.BaseDataType.DOUBLE, 2, 1)
        elif "2f" in name or "float2" in name:
            return og.Type(og.BaseDataType.FLOAT, 2, 1)
        elif name == "int4":
            return og.Type(og.BaseDataType.INT, 4, 1)
        elif name == "int3":
            return og.Type(og.BaseDataType.INT, 3, 1)
        elif name == "int2":
            return og.Type(og.BaseDataType.INT, 2, 1)
        elif name == "float":
            return og.Type(og.BaseDataType.FLOAT, 1, 1)
        elif name == "double":
            return og.Type(og.BaseDataType.DOUBLE, 1, 1)
        elif name == "int":
            return og.Type(og.BaseDataType.INT, 1, 1)
        elif name == "asset":
            return og.Type(og.BaseDataType.TOKEN, 1, 1)
        elif name == "token":
            return og.Type(og.BaseDataType.TOKEN, 1, 1)
        elif name == "bool":
            return og.Type(og.BaseDataType.BOOL, 1, 1)
    else:
        if name == "matrix4d":
            return og.Type(og.BaseDataType.DOUBLE, 16, 1)
        elif name == "matrix4f":
            return og.Type(og.BaseDataType.FLOAT, 16, 1)
        elif name == "matrix3d":
            return og.Type(og.BaseDataType.DOUBLE, 9, 1)
        elif name == "matrix3f":
            return og.Type(og.BaseDataType.FLOAT, 9, 1)
        elif name == "matrix2d":
            return og.Type(og.BaseDataType.DOUBLE, 4, 1)
        elif name == "matrix2f":
            return og.Type(og.BaseDataType.FLOAT, 4, 1)
    return None


class OgnArray:
    @staticmethod
    def compute(db) -> bool:
        return True

    @staticmethod
    def initialize(graph_context, node):
        function_callback = OgnArray.on_value_changed_callback
        node.get_attribute("inputs:arrayType").register_value_changed_callback(function_callback)

    @staticmethod
    def on_value_changed_callback(attr) -> None:
        node = attr.get_node()
        specified_type = attr.get_array(False, False, 0)
        array = node.get_attribute("inputs:array")
        if array.get_resolved_type().base_type == og.BaseDataType.UNKNOWN:
            array_type = get_type(specified_type)
            if array_type is None:
                raise ValueError(f"Unable to parse type {specified_type}")
            array.set_resolved_type(array_type)
