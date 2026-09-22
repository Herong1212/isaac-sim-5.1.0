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

from typing import Tuple

import omni.graph.core as og

NODE_VALUES_CACHE_SIZE = 5


class NamedNodes:
    """Class collecting attributes from named nodes

    Temporary solution to collect attributes from nodes indexed by simulation time.
    """

    # TODO: replace this functionality with Fabric

    _named_nodes = {}
    _named_node_values = {}
    _trigger_values = {}
    _distribution_values = {}

    @classmethod
    def reset(cls):
        cls._named_nodes = {}
        cls._named_node_values = {}
        cls._trigger_values = {}
        cls._distribution_values = {}

    @classmethod
    def add(cls, name: str, node: og.Node):
        cls._named_nodes[name] = node

    @classmethod
    def _get_named_node_values(cls, reference_time: Tuple[int, int]):
        return cls._named_node_values.get(reference_time, {})

    @classmethod
    def _get_distribution_values(cls, reference_time: Tuple[int, int]):
        return cls._distribution_values.get(reference_time, {})

    @classmethod
    def _get_trigger_values(cls, reference_time: Tuple[int, int]):
        return cls._trigger_values.get(reference_time, {})

    @classmethod
    def collect_data(cls, reference_time: Tuple[int, int]):
        named_nodes_dict = {}
        distribution_values_dict = {}
        trigger_values_dict = {}
        for name in list(cls._named_nodes.keys()):
            node = cls._named_nodes[name]
            if not node.is_valid():
                del cls._named_nodes[name]
                continue
            for attr in node.get_attributes():
                if not attr:
                    # Invalid attribute handler
                    continue
                if attr.get_port_type() != og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT:
                    continue
                if attr.get_resolved_type().get_role_name() in ["execution", "bundle"]:
                    continue
                data_type = attr.get_resolved_type()
                if data_type.array_depth == 0:
                    value = attr.get()
                else:
                    value = attr.get_array(False, False, 0)
                attr_name = attr.get_name().split(":")[-1]
                named_nodes_dict.setdefault(name, {})[attr_name] = value

                # TO BE DEPRECATED
                is_trigger_node = node.get_type_name() in [
                    f"omni.replicator.core.{n}" for n in ["OgnOnFrame", "OgnOnTime"]
                ]
                if is_trigger_node and attr.get_name() == "outputs:execCounts":
                    # is trigger node
                    trigger_values_dict[name] = value
                elif attr.get_name() == "outputs:samples":
                    # is distribution node
                    distribution_values_dict[name] = value

        if len(distribution_values_dict) > 0:
            cls._distribution_values[reference_time] = distribution_values_dict

        if len(cls._distribution_values) > NODE_VALUES_CACHE_SIZE:
            cls._distribution_values.pop(next(iter(cls._distribution_values.keys())))

        if len(trigger_values_dict) > 0:
            cls._trigger_values[reference_time] = trigger_values_dict

        if len(cls._trigger_values) > NODE_VALUES_CACHE_SIZE:
            cls._trigger_values.pop(next(iter(cls._trigger_values.keys())))

        if len(named_nodes_dict) > 0:
            cls._named_node_values[reference_time] = named_nodes_dict

        if len(cls._named_node_values) > NODE_VALUES_CACHE_SIZE:
            cls._named_node_values.pop(min(cls._named_node_values.keys()))


def _add_named_node(name: str, node: og.Node):
    NamedNodes.add(name, node)
