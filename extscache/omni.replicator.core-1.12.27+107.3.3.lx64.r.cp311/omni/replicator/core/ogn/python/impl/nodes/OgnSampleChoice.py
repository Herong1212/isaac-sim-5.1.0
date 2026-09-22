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

import omni.graph.core as og
import omni.replicator.core as rep


class OgnSampleChoiceInternalState:
    def __init__(self):
        self.rng = rep.rng.ReplicatorRNG()


class OgnSampleChoice:
    @staticmethod
    def internal_state():
        return OgnSampleChoiceInternalState()

    @staticmethod
    def release(node):
        rep.rng.release(node.get_prim_path())

    @staticmethod
    def compute(db) -> bool:
        state = db.shared_state
        choices = db.inputs.choices.array_value()
        weights = db.inputs.weights
        num_samples = db.inputs.numSamples
        with_replacements = db.inputs.withReplacements

        if len(choices) == 0 or num_samples == 0:
            return False

        # validate input
        try:
            if len(weights) != 0:
                if len(weights) != len(choices):
                    raise ValueError(f"Number of choices `{len(choices)}` and weights `{len(weights)}` do not match.")
                weights_sum = sum(weights)
                weights_norm = [w / weights_sum for w in weights]
            else:
                weights_norm = None

            if num_samples < 1:
                warnings.warn(f"Expected inputs:num_samples to be greater than 0 but instead received {num_samples}")
                return False

        except Exception as error:
            db.log_error(f"SampleChoice Error: {error}")
            return False

        is_seed_valid = db.inputs.seed is not None
        is_seed_changed = state.rng is None or db.inputs.seed != state.rng.seed
        if is_seed_valid and is_seed_changed:
            node_id = db.inputs.nodeId if db.node.get_attribute_exists("inputs:nodeId") else 0
            state.rng.initialize(db.inputs.seed, db.node, node_id)

        # samples = np.random.choice(a=choices, size=num_samples, p=weights_norm)
        samples = state.rng.generator.choice(
            choices, axis=0, size=num_samples, p=weights_norm, replace=with_replacements
        )

        db.outputs.samples = samples
        db.outputs.numSamples = db.inputs.numSamples
        return True

    @staticmethod
    def initialize(graph_context, node):
        connected_function_callback = OgnSampleChoice.on_connected_callback
        node.register_on_connected_callback(connected_function_callback)

    @staticmethod
    def on_connected_callback(upstream_attr, downstream_attr):
        if downstream_attr.get_name() == "inputs:choices":
            if downstream_attr.get_resolved_type().base_type == og.BaseDataType.UNKNOWN:
                upstream_resolved_type = upstream_attr.get_resolved_type()
                if upstream_resolved_type.base_type != og.BaseDataType.UNKNOWN:
                    downstream_attr.set_resolved_type(upstream_resolved_type)

        # Resolve output attr based on the downstream attr
        if upstream_attr.get_name() == "outputs:samples":
            if upstream_attr.get_resolved_type().base_type == og.BaseDataType.UNKNOWN:
                if downstream_attr.get_resolved_type().base_type != og.BaseDataType.UNKNOWN:
                    og.AttributeValueHelper(upstream_attr).resolve_type(downstream_attr.get_resolved_type())
                else:
                    node = upstream_attr.get_node()
                    choices_attr_type = node.get_attribute("inputs:choices").get_resolved_type()
                    og.AttributeValueHelper(upstream_attr).resolve_type(choices_attr_type)
