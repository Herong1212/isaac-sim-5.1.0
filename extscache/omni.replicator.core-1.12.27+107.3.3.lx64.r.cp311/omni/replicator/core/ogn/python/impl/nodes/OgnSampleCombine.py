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

import warnings
from ast import literal_eval

import numpy as np
import omni.graph.core as og


class OgnSampleCombine:
    @staticmethod
    def compute(db) -> bool:
        num_nodes = db.inputs.numInputNodes
        num_samples = db.inputs.numSamples

        if num_samples < 1:
            warnings.warn(f"Expected inputs:num_samples to be greater than 0 but instead received {num_samples}")
            return False

        samples = []

        for i in range(num_nodes):
            attribute_name = f"sample_{i}"
            # Get value out of a bundle
            value = getattr(db.inputs, attribute_name)

            if not isinstance(value, np.ndarray):
                # Repeat the value to num_samples
                if isinstance(value, (list, tuple)):
                    if len(value) == num_samples:
                        value = np.array(value).reshape(num_samples, -1)
                    else:
                        value = np.repeat(np.array(value), num_samples).reshape(num_samples, -1)
                else:
                    value = np.tile(value, (num_samples, 1))
            else:
                if len(value) == 1:
                    value = np.repeat(value, num_samples).reshape(num_samples, -1)
                else:
                    value = value.reshape((num_samples, -1))
                # If the number of samples is different in different distributions, raise an error.
                if value.shape[0] != num_samples:
                    raise ValueError(
                        f"Number of samples should be {num_samples} in every distributions, but got {value.shape[0]}"
                    )
            samples.append(value)

        samples = np.concatenate(samples, axis=1)

        if "str" in samples.dtype.name or "bool" in samples.dtype.name:
            samples = samples.flatten().tolist()

        db.outputs.samples = samples
        return True

    # @staticmethod
    # def initialize(graph_context, node):
    #     function_callback = OgnSampleCombine.on_value_changed_callback
    #     node.get_attribute("inputs:numSamples").register_value_changed_callback(function_callback)

    @staticmethod
    def on_connection_type_resolve(node) -> None:
        output_attr = node.get_attribute("outputs:samples")
        output_type = output_attr.get_resolved_type().base_type

        attributes_to_couple = []

        for attr in node.get_attributes():
            is_input = attr.get_port_type() == og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT
            is_unknown = attr.get_resolved_type().base_type != og.BaseDataType.UNKNOWN
            is_sample = "sample_" in attr.get_name()
            if is_input and is_sample:
                # attributes_to_couple.append(attributes_to_couple)
                attr.set_resolved_type(og.Type(output_type, 1, 1))

    # @staticmethod
    # def on_value_changed_callback(attr):
    #     node = attr.get_node()
    #     num_samples = attr.get()

    #     num_nodes = node.get_attribute("inputs:numInputNodes").get()

    #     for i in range(num_nodes):
    #         input_dist_attr = node.get_attribute(f"inputs:sample_{i}")

    #         if input_dist_attr.is_valid():
    #             upstream_connections = input_dist_attr.get_upstream_connections()

    #             for connection in upstream_connections:
    #                 upstream_node = connection.get_node()
    #                 upstream_num_samples = upstream_node.get_attribute("inputs:numSamples")

    #                 if upstream_num_samples.is_valid() and upstream_num_samples.get() != num_samples:
    #                     upstream_num_samples.set(num_samples)

    # if array.get_resolved_type().base_type == og.BaseDataType.UNKNOWN:
    #     array_type = get_type(specified_type)
    #     if array_type is None:
    #         raise ValueError(f"Unable to parse type {specified_type}")
    #     array.set_resolved_type(array_type)
