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
import omni.kit
import omni.replicator.core as rep
from omni.replicator.core.ogn.OgnSampleSequencePrimDatabase import OgnSampleSequencePrimDatabase


class OgnSampleSequencePrimInternalState:
    def __init__(self):
        self.rng = rep.rng.ReplicatorRNG()

        self.current_index = 0
        self.num_items = 0

        # unordered variables
        self.unselected_indices = []

        self.sub_orchestrator = None

    def get_index_ordered(self):
        pre_increment = self.current_index
        self.current_index = (self.current_index + 1) % self.num_items
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
                observer_name="OgnSampleSequencePrim",
                event_name=rep.orchestrator.ORCHESTRATOR_EVENT,
                on_event=self.on_orchestrator,
            )
            self.node_path = node.get_prim_path()
            self.graph = node.get_graph()
            exit_val = True

        return exit_val


class OgnSampleSequencePrim:
    @staticmethod
    def internal_state():
        return OgnSampleSequencePrimInternalState()

    @staticmethod
    def release(node):
        rep.rng.release(node.get_prim_path())
        state = OgnSampleSequencePrimDatabase.shared_internal_state(node)
        if state.sub_orchestrator is not None:
            state.sub_orchestrator.reset()
        rep.orchestrator._release_trigger(node.get_prim_path())

    @staticmethod
    def compute(db) -> bool:
        state = db.shared_state
        ordered = db.inputs.ordered

        items = db.inputs.items

        if len(items) == 0:
            return False

        is_seed_valid = db.inputs.seed is not None
        is_seed_changed = state.rng is None or db.inputs.seed != state.rng.seed
        if is_seed_valid and is_seed_changed:
            node_id = db.inputs.nodeId if db.node.get_attribute_exists("inputs:nodeId") else 0
            state.rng.initialize(db.inputs.seed, db.node, node_id)

        state.num_items = len(items)

        if ordered:
            db.outputs.samples = [items[state.get_index_ordered()]]
        else:
            db.outputs.samples = [items[state.get_index_unordered()]]

        return True
