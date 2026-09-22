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
import omni.graph.core as og
import omni.usd
from omni.replicator.core.scripts.functional import get


class OgnGetPrimsInternalState:
    cached_paths = None
    cached_inputs = None


class OgnGetPrims:
    @staticmethod
    def internal_state():
        """Returns an object that will contain per-node state information"""
        return OgnGetPrimsInternalState()

    @staticmethod
    def initialize(graph_context, node):
        node.get_attribute("inputs:pathPattern").register_value_changed_callback(OgnGetPrims.on_value_changed_callback)
        node.get_attribute("inputs:pathMatch").register_value_changed_callback(OgnGetPrims.on_value_changed_callback)
        node.get_attribute("inputs:pathPatternExclusion").register_value_changed_callback(
            OgnGetPrims.on_value_changed_callback
        )
        node.get_attribute("inputs:primTypesExclusion").register_value_changed_callback(
            OgnGetPrims.on_value_changed_callback
        )
        node.get_attribute("inputs:semantics").register_value_changed_callback(OgnGetPrims.on_value_changed_callback)
        node.get_attribute("inputs:semanticsExclusion").register_value_changed_callback(
            OgnGetPrims.on_value_changed_callback
        )
        node.get_attribute("inputs:ignoreCase").register_value_changed_callback(OgnGetPrims.on_value_changed_callback)

    @staticmethod
    def on_value_changed_callback(attr) -> None:
        node = attr.get_node()
        # Gather paths immediately on node creation
        inputs = {
            "path_pattern": node.get_attribute("inputs:pathPattern").get(),
            "path_match": node.get_attribute("inputs:pathMatch").get(),
            "path_pattern_exclusion": node.get_attribute("inputs:pathPatternExclusion").get(),
            "prim_types": [pt.lower() for pt in node.get_attribute("inputs:primTypes").get()],
            "prim_types_exclusion": [pt.lower() for pt in node.get_attribute("inputs:primTypesExclusion").get()],
            "semantics": [tuple(s.split(",")) for s in node.get_attribute("inputs:semantics").get()],
            "semantics_exclusion": [tuple(s.split(",")) for s in node.get_attribute("inputs:semanticsExclusion").get()],
            "ignore_case": node.get_attribute("inputs:ignoreCase").get(),
        }
        stage = omni.usd.get_context().get_stage()
        gathered_prims = get.prims(stage, **inputs)
        gathered_paths = [str(prim.GetPath()) for prim in gathered_prims]
        node.get_attribute("outputs:prims").set(gathered_paths)

    @staticmethod
    def compute(db) -> bool:
        state = db.shared_state

        inputs = {
            "path_pattern": db.inputs.pathPattern,
            "path_match": db.inputs.pathMatch,
            "path_pattern_exclusion": db.inputs.pathPatternExclusion,
            "prim_types": [pt.lower() for pt in db.inputs.primTypes],
            "prim_types_exclusion": [pt.lower() for pt in db.inputs.primTypesExclusion],
            "semantics": [tuple(s.split(",")) for s in db.inputs.semantics],
            "semantics_exclusion": [tuple(s.split(",")) for s in db.inputs.semanticsExclusion],
            "ignore_case": db.inputs.ignoreCase,
        }

        stage = omni.usd.get_context().get_stage()

        is_inputs_unchanged = inputs == state.cached_inputs
        if db.inputs.cachePrims and state.cached_paths is not None and is_inputs_unchanged:
            db.outputs.prims = state.cached_paths
            db.outputs.execOut = og.ExecutionAttributeState.ENABLED
            return True

        gathered_prims = get.prims(stage, **inputs)
        gathered_paths = [str(prim.GetPath()) for prim in gathered_prims]

        if gathered_paths:
            db.outputs.execOut = og.ExecutionAttributeState.ENABLED
            db.outputs.prims = gathered_paths
            if db.inputs.cachePrims:
                state.cached_paths = gathered_paths
            state.cached_inputs = inputs
        else:
            carb.log_warn(f"No prims found with given inputs: {inputs['path_pattern']}")

        return True
