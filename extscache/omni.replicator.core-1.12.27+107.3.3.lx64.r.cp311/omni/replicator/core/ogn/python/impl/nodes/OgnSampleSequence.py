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

import carb.events
import omni.graph.core as og
import omni.replicator.core as rep
from omni.replicator.core.ogn.OgnSampleSequenceDatabase import OgnSampleSequenceDatabase


class OgnSampleSequenceInternalState:
    def __init__(self):
        self.rng = rep.rng.ReplicatorRNG()

        self.current_index = 0
        self.num_items = 0
        self.stride_len = 1

        # unordered variables
        self.unselected_indices = []

        self.sub_orchestrator = None

    def get_index_ordered(self):
        pre_increment = self.current_index
        self.current_index = (self.current_index + self.stride_len) % self.num_items
        return pre_increment

    def get_index_unordered(self):
        if len(self.unselected_indices) == 0:
            self.unselected_indices = list(range(self.num_items))

        select_index = self.rng.generator.choice(self.unselected_indices, axis=0, size=1, replace=False)[0]

        self.unselected_indices.remove(select_index)

        return select_index

    def reset_current_index(self):
        self.current_index = 0

    def on_orchestrator(self, event):
        if event is None:
            return

        if event.has_key("command") and event.get("command") == "initialize":
            self.reset_current_index()

    def first_time_subscribe(self, node: og.Node) -> bool:
        """Checked call to set up carb subscription
        Args:
            node: The node instance
            viewport_handle: The handle for the viewport to watch
        Returns:
            True if we subscribed, False if we are already subscribed
        """
        exit_val = False

        if self.sub_orchestrator is None:
            # Add a subscription for the given event name. This is a pop subscription, so we expect a 1-frame
            # lag between send and receive
            self.sub_orchestrator = carb.eventdispatcher.get_eventdispatcher().observe_event(
                observer_name="OgnSampleSequence",
                event_name=rep.orchestrator.ORCHESTRATOR_EVENT,
                on_event=self.on_orchestrator,
            )
            self.node_path = node.get_prim_path()
            self.graph = node.get_graph()
            exit_val = True

        return exit_val


class OgnSampleSequence:
    @staticmethod
    def internal_state():
        return OgnSampleSequenceInternalState()

    @staticmethod
    def release(node):
        rep.rng.release(node.get_prim_path())
        state = OgnSampleSequenceDatabase.shared_internal_state(node)
        if state.sub_orchestrator is not None:
            state.sub_orchestrator.reset()
        rep.orchestrator._release_trigger(node.get_prim_path())

    @staticmethod
    def compute(db) -> bool:
        state = db.shared_state
        ordered = db.inputs.ordered

        items = db.inputs.items.array_value()
        stride_len = db.inputs.stride

        if len(items) == 0:
            return False

        is_seed_valid = db.inputs.seed is not None
        is_seed_changed = state.rng is None or db.inputs.seed != state.rng.seed
        if is_seed_valid and is_seed_changed:
            node_id = db.inputs.nodeId if db.node.get_attribute_exists("inputs:nodeId") else 0
            state.rng.initialize(db.inputs.seed, db.node, node_id)

        state.num_items = len(items)
        state.stride_len = stride_len

        if ordered:
            index = state.get_index_ordered()
            if stride_len == 1:
                samples = items[index]
                # If the output is an array, we need to wrap the sample in a list
                if db.outputs.samples.type.array_depth > 0:
                    samples = [samples]
                db.outputs.samples = samples
            else:
                stride = index + stride_len
                db.outputs.samples = [items[index:stride]]
        else:
            index = state.get_index_unordered()
            if stride_len == 1:
                db.outputs.samples = [items[index]]
            else:
                stride = index + stride_len
                db.outputs.samples = [items[index:stride]]

        return True

    @staticmethod
    def initialize(graph_context, node):
        state = OgnSampleSequenceDatabase.shared_internal_state(node)
        state.first_time_subscribe(node)
        connected_function_callback = OgnSampleSequence.on_connected_callback
        node.register_on_connected_callback(connected_function_callback)

    @staticmethod
    def on_connected_callback(upstream_attr, downstream_attr):
        if downstream_attr.get_name() == "inputs:items":
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
                    items_attr = node.get_attribute("inputs:items")
                    og.AttributeValueHelper(upstream_attr).resolve_type(items_attr.get_resolved_type())
