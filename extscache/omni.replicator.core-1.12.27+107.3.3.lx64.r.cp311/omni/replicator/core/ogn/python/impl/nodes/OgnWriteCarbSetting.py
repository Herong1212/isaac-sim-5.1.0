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

import carb
import numpy as np
import omni.graph.core as og


def get_type(cur_val):
    if isinstance(cur_val, (list, tuple)):
        el_len = len(cur_val)
        el_type = type(cur_val[0])
    else:
        el_len = 1
        el_type = type(cur_val)

    if el_type == int:
        base_type = og.BaseDataType.INT
    elif el_type == float:
        base_type = og.BaseDataType.DOUBLE
    elif el_type == bool:
        base_type = og.BaseDataType.BOOL
    elif el_type == str:
        base_type = og.BaseDataType.TOKEN
    else:
        raise ValueError(
            f"Base type {el_type} is not supported. Only elements of type float, bool, int and float are supported."
        )
    return og.Type(base_type, el_len, 1)


class OgnWriteCarbSetting:
    @staticmethod
    def compute(db) -> bool:
        setting_name = db.inputs.setting
        values = db.inputs.values
        if setting_name == "" or values is None:
            db.outputs.execOut = og.ExecutionAttributeState.DISABLED
            return False
        # TODO: Change this when choice's type is resolved inside the node.
        sample = values.array_value()
        if isinstance(sample, np.ndarray):
            sample = sample.tolist()

        if isinstance(sample, (list, tuple)):
            sample = sample[0]
        carb_value = carb.settings.get_settings().get(setting_name)
        dtype = type(carb_value)

        carb.settings.get_settings().set(setting_name, dtype(sample))

        db.outputs.execOut = og.ExecutionAttributeState.ENABLED
        return True

    @staticmethod
    def initialize(graph_context, node):
        function_callback = OgnWriteCarbSetting.on_value_changed_callback
        node.get_attribute("inputs:setting").register_value_changed_callback(function_callback)

    @staticmethod
    def on_value_changed_callback(attr) -> None:
        node = attr.get_node()
        setting = attr.get_array(False, False, 0)
        setting_type = get_type(carb.settings.get_settings().get(setting))
        values = node.get_attribute("inputs:values")
        if values.get_resolved_type().base_type == og.BaseDataType.UNKNOWN:
            values.set_resolved_type(setting_type)
