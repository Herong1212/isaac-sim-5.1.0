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

import numpy as np
import omni.graph.core as og
import omni.replicator.core as rep
from omni.replicator.core import utils


class OgnSampleUniformInternalState:
    def __init__(self):
        self.rng = rep.rng.ReplicatorRNG()


class OgnSampleUniform:
    @staticmethod
    def internal_state():
        return OgnSampleUniformInternalState()

    @staticmethod
    def release(node):
        rep.rng.release(node.get_prim_path())

    @staticmethod
    def compute(db) -> bool:
        state = db.shared_state

        lower = db.inputs.lower
        upper = db.inputs.upper
        num_samples = db.inputs.numSamples

        if len(lower) == 0 or len(upper) == 0:
            return False

        # validate input
        try:
            if len(lower) != len(upper):
                raise ValueError(
                    "For uniform distribution, the lengths of inputs:lower and inputs:upper must be equal, "
                    + f" but instead received lengths {len(lower)} and {len(upper)}, {lower, upper}"
                )
            if np.any(lower > upper):
                raise ValueError(
                    "For uniform distribution, all values in inputs:lower are expected to be "
                    + f"smaller or equal than all values in inputs:upper, but instead received {lower}"
                    + f"for inputs:lower and {upper} for inputs:upper."
                )
            if num_samples < 1:
                warnings.warn(f"Expected inputs:num_samples to be greater than 0 but instead received {num_samples}")
                return False

            sample_size = len(lower)

        except Exception as error:
            db.log_error(f"SampleUniform Error: {error}")
            return False

        is_seed_valid = db.inputs.seed is not None
        is_seed_changed = state.rng is None or db.inputs.seed != state.rng.seed
        if is_seed_valid and is_seed_changed:
            node_id = db.inputs.nodeId if db.node.get_attribute_exists("inputs:nodeId") else 0
            state.rng.initialize(db.inputs.seed, db.node, node_id)

        samples = state.rng.generator.uniform(lower, upper, size=(num_samples, sample_size))

        # Repeat along dimension if required
        tuple_count = db.outputs.samples.type.tuple_count
        if tuple_count > samples.shape[1]:
            samples = samples.repeat(tuple_count, 1)

        db.outputs.samples = samples
        db.outputs.numSamples = db.inputs.numSamples
        return True

    @staticmethod
    def initialize(graph_context, node):
        connected_function_callback = OgnSampleUniform.on_connected_callback
        node.register_on_connected_callback(connected_function_callback)

        function_callback = OgnSampleUniform.on_value_changed_callback
        node.get_attribute("inputs:outputType").register_value_changed_callback(function_callback)

        # Have to resolve the output type here because save and reload only calls initialize
        output_type = node.get_attribute("inputs:outputType").get()
        output_attr = node.get_attribute("outputs:samples")

        if output_type != "":
            output_attr.set_resolved_type(og.Controller.attribute_type(output_type))

    @staticmethod
    def on_connected_callback(upstream_attr, downstream_attr):
        if upstream_attr.get_name() != "outputs:samples":
            return

        node = upstream_attr.get_node()
        downstream_node = downstream_attr.get_node()

        if downstream_node.get_attribute_exists("inputs:attributeType"):
            downstream_attr_type = downstream_node.get_attribute("inputs:attributeType").get()
        else:
            downstream_attr_type = None

        output_type_attr = node.get_attribute("inputs:outputType")
        # Set the resolved type to be the downstream if it is resolved
        if upstream_attr.get_resolved_type().base_type == og.BaseDataType.UNKNOWN:
            downstream_resolved_type = downstream_attr.get_resolved_type()
            if downstream_resolved_type.base_type != og.BaseDataType.UNKNOWN:
                specified_type = downstream_resolved_type
            elif downstream_attr_type:
                downstream_attr_type = downstream_node.get_attribute("inputs:attributeType").get()
                specified_type = og.Controller.attribute_type(f"{downstream_attr_type}[]")
            else:
                specified_type = node.get_attribute("inputs:lower").get_resolved_type()
            # Get rid of role_name
            specified_type = og.Type(specified_type.base_type, specified_type.tuple_count, specified_type.array_depth)
            og.AttributeValueHelper(output_type_attr).set(str(specified_type), update_usd=True)

    @staticmethod
    def on_value_changed_callback(attr) -> None:
        node = attr.get_node()
        output_type = attr.get()
        output_attr = node.get_attribute("outputs:samples")
        if output_attr.get_resolved_type().base_type == og.BaseDataType.UNKNOWN and output_type != "":
            if output_type is None:
                raise ValueError(f"Unable to parse type {output_type}")
            output_attr.set_resolved_type(og.Controller.attribute_type(output_type))
