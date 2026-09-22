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
from omni.replicator.core.ogn.OgnGroupDatabase import OgnGroupDatabase
from omni.replicator.core.utils.utils import _get_node_attributes


class GroupState:
    def __init__(self):
        self.do_evaluate_paths = True


class OgnGroup:
    @staticmethod
    def internal_state():
        return GroupState()

    @staticmethod
    def compute(db) -> bool:
        state = db.shared_internal_state(db.node)
        if state.do_evaluate_paths:
            OgnGroup.evaluate_paths(db.node)

        return True

    @staticmethod
    def evaluate_paths(node):
        collected_prims = []
        do_evaluate_paths = False
        for a in node.get_attributes():
            if a.get_port_type() != og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT:
                continue
            if a.get_resolved_type().role != og.AttributeRole.TARGET:
                continue
            collected_prims += a.get()
            # If there's a connection, inputs may change, need to evaluate paths on compute
            if not do_evaluate_paths and a.get_upstream_connection_count() > 0:
                do_evaluate_paths = True
        node.get_attribute("outputs:prims").set(collected_prims)
        state = OgnGroupDatabase.shared_internal_state(node)
        state.do_evaluate_paths = do_evaluate_paths
        OgnGroup.check_and_add_inputs(node)

    @staticmethod
    def initialize(graph_context, node):
        prims_in = node.get_attribute("inputs:primsIn")
        node.get_attribute("outputs:prims").set(prims_in.get())
        prims_in.register_value_changed_callback(OgnGroup.on_value_changed_callback)
        node.register_on_connected_callback(OgnGroup.on_connected_callback)

        OgnGroup.evaluate_paths(node)

    @staticmethod
    def on_value_changed_callback(attr) -> None:
        OgnGroup.evaluate_paths(attr.get_node())

    @staticmethod
    def check_and_add_inputs(node):
        node_inputs = _get_node_attributes(node, on_input=True, on_output=False)
        if all(
            node.get_attribute(f"inputs:{i}").get_upstream_connection_count() or node.get_attribute(f"inputs:{i}").get()
            for i in node_inputs
        ):
            # all inputs full, create a new one
            node.create_attribute(
                f"inputs:primsIn{len(node_inputs)}",
                og.Type(og.BaseDataType.RELATIONSHIP, role=og.AttributeRole.TARGET),
            )
            new_attr = node.get_attribute(f"inputs:primsIn{len(node_inputs)}")
            new_attr.register_value_changed_callback(OgnGroup.on_value_changed_callback)

    @staticmethod
    def on_connected_callback(upstream_attr, downstream_attr):
        # if downstream node is group node and all inputs full, create a new one
        downstream_node = downstream_attr.get_node()
        if not downstream_node.get_type_name() == "omni.replicator.core.OgnGroup":
            return

        # If there's a connection, inputs may change, need to evaluate paths on compute
        state = OgnGroupDatabase.shared_internal_state(downstream_node)
        state.do_evaluate_paths = True

        OgnGroup.check_and_add_inputs(downstream_node)
        OgnGroup.evaluate_paths(downstream_node)
