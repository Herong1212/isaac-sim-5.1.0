# Copyright (c) 2018-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""This module provides classes for caching and indexing graph nodes, ports, and connections to improve model access efficiency."""


__all__ = ["GraphNodeIndex"]

from .graph_model import GraphModel
from collections import defaultdict
from typing import Any, Set, Tuple
from typing import Dict
from typing import List
from typing import Optional
from typing import Union
import itertools
import weakref


class CachePort:
    """
    The structure to keep in the ports and their properties and don't
    access the model many times.
    """

    def __init__(
        self,
        port: Any,
        name: str,
        state: Optional[GraphModel.ExpansionState],
        child_count: int,
        level: int,
        relative_position: int,
        parent_child_count: int,
        siblings_below,
        parent_cached_port: Optional[weakref.ProxyType] = None,
    ):
        # Port from the model
        self.port: Any = port
        # The user displayed name of the port
        self.name: str = str(name)
        # Expansion state if it's a groop
        self.state: Optional[GraphModel.ExpansionState] = state
        # Number of children
        self.child_count: int = child_count
        # The level in the tree structure
        self.level: int = level
        # Position number in the parent list
        self.relative_position = relative_position
        # Number of children of the parent
        self.parent_child_count = parent_child_count
        # Siblings below flags for all levels "above"
        self.siblings_below = siblings_below
        # The visibility after collapsing
        self.visibile: bool = True
        # Inputs from the model
        self.inputs: Optional[List[Any]] = None
        # Outputs from the model
        self.outputs: Optional[List[Any]] = None

        self.parent_cached_node: Optional[weakref.ProxyType] = None
        self.parent_cached_port: Optional[weakref.ProxyType] = parent_cached_port

    def __repr__(self):
        return f"<CachePort {self.port}>"

    def __hash__(self):
        if self.inputs:
            inputs_hash = hash(tuple(hash(i) for i in self.inputs))
        else:
            inputs_hash = 0

        if self.outputs:
            outputs_hash = hash(tuple(hash(i) for i in self.outputs))
        else:
            outputs_hash = 0

        return hash(
            (
                CachePort,
                self.port,
                self.name,
                self.state and self.state.value,
                self.visibile,
                inputs_hash,
                outputs_hash,
            )
        )

    def __eq__(self, other):
        return hash(self) == hash(other)


class CacheNode:
    """The structure to keep in the cache and don't access the model many times"""

    def __init__(
        self,
        node: Any,
        state: Optional[GraphModel.ExpansionState],
        cached_ports: List[CachePort],
        stacking_order: int,
        icon: str,
        additional_hash=0,
    ):
        # Node from the model
        self.node: Any = node
        # Expansion state if it's a group
        self.state: Optional[GraphModel.ExpansionState] = state
        # Ports from the model
        self.cached_ports: List[CachePort] = cached_ports
        # Level represents the distance of the current node from the root
        self.level = None
        self.stacking_order: int = stacking_order
        # The icon path of the node
        self.icon = icon
        # The nodes dependent from the current node. If the nodes connected like this A.out -> B.in,
        # then A.dependent = [B]
        self.dependent = []
        # Hash
        self._additional_hash = additional_hash

        self.inputs = []
        self.outputs = []

        # Add connection to the parent node
        selfproxy = weakref.proxy(self)
        for port in self.cached_ports:
            port.parent_cached_node = selfproxy

    def __repr__(self):
        return f"<CacheNode {self.node}>"

    def __hash__(self):
        cached_ports_hash = hash(tuple(hash(p) for p in self.cached_ports))
        return hash(
            (CacheNode, self.node, self.state and self.state.value, self.icon, cached_ports_hash, self._additional_hash)
        )

    def __eq__(self, other):
        return hash(self) == hash(other)


class CacheConnection:
    """The structure to keep connections in the cache and don't access the model many times"""

    def __init__(
        self,
        source_cached_port: CachePort,
        target_cached_port: CachePort,
    ):
        self.source_port: Any = source_cached_port.port
        self.target_port: Any = target_cached_port.port
        self.__hash = hash(
            (
                CacheConnection,
                source_cached_port,
                target_cached_port,
                source_cached_port.parent_cached_node.__hash__(),
                target_cached_port.parent_cached_node.__hash__(),
            )
        )

    @property
    def pair(self):
        return (self.source_port, self.target_port)

    def __repr__(self):
        return f"<CacheConnection {self.pair}>"

    def __hash__(self):
        return self.__hash

    def __eq__(self, other):
        return hash(self) == hash(other)


class GraphNodeDiff:
    """
    The object that keeps the difference that is the list of nodes and
    connections to add and delete.
    """

    def __init__(
        self,
        nodes_to_add: List[CacheNode] = None,
        nodes_to_del: List[CacheNode] = None,
        connections_to_add: List[CacheConnection] = None,
        connections_to_del: List[CacheConnection] = None,
    ):
        self.nodes_to_add = nodes_to_add
        self.nodes_to_del = nodes_to_del
        self.connections_to_add = connections_to_add
        self.connections_to_del = connections_to_del

    @property
    def valid(self):
        return (
            self.nodes_to_add is not None
            and self.nodes_to_del is not None
            and self.connections_to_add is not None
            and self.connections_to_del is not None
        )

    def __repr__(self):
        return (
            "<GraphNodeDiff\n"
            f" Add: {self.nodes_to_add} {self.connections_to_add}\n"
            f" Del: {self.nodes_to_del} {self.connections_to_del}\n"
            ">"
        )


class GraphNodeIndex:
    """A class for caching and indexing graph nodes, ports, and connections to improve access efficiency in a model.

    This class provides methods for quickly accessing and modifying nodes and connections within a graph model based on a hierarchical index. It's designed to optimize read and write operations by maintaining an internal cache of graph elements.

    Args:
        model (Optional[GraphModel]): The graph model to index.
        port_grouping (bool): Flag indicating whether to group ports.

    Note:
        The initialization of this class involves building caches and indices for nodes, ports, and connections, and may have performance implications on large graphs.
    """

    def __init__(self, model: Optional[GraphModel], port_grouping: bool):
        """Initializes a new instance of the GraphNodeIndex class."""
        # List of all the nodes from the model
        self.cached_nodes: List[Optional[CacheNode]] = []
        # List of all the connections from the model
        self.cached_connections: List[Optional[CacheConnection]] = []
        # Dictionary that has a node from the model as a key and the
        # index of this node in all_cached_nodes.
        self.node_to_id: Dict[Any, int] = {}
        # Dictionary that has a port from the model as a key and the
        # index of the parent node in self.cached_nodes.
        self.port_to_id: Dict[Any, int] = {}
        # Dictionary that has a port from the model as a key and the
        # index of the port in cached_node.cached_ports.
        port_to_port_id: Dict[Any, int] = {}
        # Connection hash to ID in self.cached_connections.
        self.connection_to_id: Dict[Tuple[Any, Any], int] = {}
        # Set with all the ports from the model if this port is output. We need
        # it to detect the flow direction.
        self.ports_used_as_output = set()
        # All the connections.
        self.source_to_target = defaultdict(set)
        # Dict[child port: parent port]
        self.port_child_to_parent: Dict[Any, Any] = {}

        if not model:
            return

        # Preparing the cache and indices.
        for node in model.nodes or []:
            # Caching ports

            def recurse_ports(port_list, level, parent_siblings_below, cached_parent_port=None):
                cache_ports: List[CachePort] = []
                port_count = len(port_list)
                for id, port in enumerate(port_list):
                    if port_grouping:
                        sub_ports = model[port].ports
                        is_group = sub_ports is not None
                    else:
                        sub_ports = None
                        is_group = False

                    name = model[port].name
                    state = model[port].expansion_state
                    siblings_below = parent_siblings_below + [id == (port_count - 1)]

                    cached_port = CachePort(
                        port,
                        name,
                        state,
                        len(sub_ports) if is_group else 0,
                        level,
                        id,
                        port_count,
                        siblings_below,
                        cached_parent_port,
                    )
                    cache_ports.append(cached_port)
                    if is_group:
                        cached_port_proxy = weakref.proxy(cached_port)
                        cache_ports += recurse_ports(sub_ports, level + 1, siblings_below, cached_port_proxy)

                return cache_ports

            root_ports = model[node].ports or []
            cached_ports: List[CachePort] = recurse_ports(root_ports, 0, [], None)

            # The ID of the current cached node in the cache
            cached_node_id = len(self.cached_nodes)

            # The global index
            self.node_to_id[node] = cached_node_id

            state = model[node].expansion_state

            # Allows to draw backdrops in background
            stacking_order = model[node].stacking_order

            # Hash name, description and color, so the node is autogenerated when it's changed.
            additional_hash = hash(
                (model[node].name, model[node].description, model[node].display_color, model[node].size)
            )

            # The global cache
            self.cached_nodes.append(
                CacheNode(node, state, cached_ports, stacking_order, model[node].icon, additional_hash)
            )

        # Cache connections
        for cached_node_id, cached_node in enumerate(self.cached_nodes):
            cached_ports = cached_node.cached_ports

            # True if node has output node
            node_has_outputs = False

            # Parent port to put the connections to
            cached_port_parent: Optional[CachePort] = None
            # How many ports already hidden
            hidden_port_counter = 0
            # How many ports we need to hide
            hidden_port_number = 0

            # for port, port_state, port_child_count in zip(ports, port_states, port_child_counts):
            for cached_port_id, cached_port in enumerate(cached_ports):
                port = cached_port.port

                port_inputs = model[port].inputs
                port_outputs = model[port].outputs
                # Copy to detach from the model
                port_inputs = port_inputs[:] if port_inputs is not None else None
                port_outputs = port_outputs[:] if port_outputs is not None else None

                cached_port.visibile = not cached_port_parent

                if cached_port_parent:
                    # Put inputs/outputs to the parent
                    if port_inputs is not None:
                        cached_port_parent.inputs = cached_port_parent.inputs or []
                        cached_port_parent.inputs += port_inputs
                    if port_outputs is not None:
                        cached_port_parent.outputs = cached_port_parent.outputs or []
                        cached_port_parent.outputs += port_outputs
                else:
                    # Put inputs/outputs to the port
                    cached_port.inputs = port_inputs
                    cached_port.outputs = port_outputs

                if cached_port_parent:
                    connection_port = cached_port_parent.port
                    # Dict[child: parent]
                    self.port_child_to_parent[cached_port.port] = cached_port_parent.port
                else:
                    connection_port = cached_port.port

                if port_inputs:
                    for source in port_inputs:
                        # |--------|      |-----------------|
                        # | source | ---> | connection_port |
                        # |--------|      |-----------------|
                        # Ex:
                        # source is Usd.Prim(</World/Looks/OmniGlass/Shader>).GetAttribute('outputs:out')
                        # connection_port is Usd.Prim(</World/Looks/OmniGlass>).GetAttribute('outputs:mdl:displacement')
                        self.source_to_target[source].add(connection_port)

                if port_outputs:
                    for source in port_outputs:
                        self.source_to_target[source].add(connection_port)

                if port_outputs is not None:
                    node_has_outputs = True

                self.port_to_id[port] = cached_node_id
                port_to_port_id[port] = cached_port_id

                # Check if the port is hidden and hide it. It happens
                # when the port is collapsed.
                if cached_port_parent:
                    hidden_port_counter += 1
                    hidden_port_number += cached_port.child_count

                    if hidden_port_counter == hidden_port_number:
                        # We hide enough
                        cached_port_parent = None

                    continue

                if cached_port.child_count > 0 and cached_port.state == GraphModel.ExpansionState.CLOSED:
                    # The next one should be hidden
                    cached_port_parent = cached_port
                    hidden_port_counter = 0
                    hidden_port_number = cached_port.child_count

            for cached_port in cached_ports:
                # If the node don't have any output (in OmniGraph inputs and outputs are equal) we consider that all
                # the input attributes are used as outputs.
                if not node_has_outputs or cached_port.outputs is not None:
                    self.ports_used_as_output.add(cached_port.port)

            # chain.from_iterable(['ABC', 'DEF']) --> A B C D E F
            cached_node.inputs = list(itertools.chain.from_iterable([p.inputs for p in cached_ports if p.inputs]))
            cached_node.outputs = list(itertools.chain.from_iterable([p.outputs for p in cached_ports if p.outputs]))

        # Replace input/output of cached ports to point to the parents of the collapsed ports
        for cached_node in self.cached_nodes:
            for cached_port in cached_node.cached_ports:
                if cached_port.inputs:
                    inputs = []
                    for i in cached_port.inputs:
                        parent = self.port_child_to_parent.get(i, None)
                        if parent:
                            inputs.append(parent)
                        else:
                            inputs.append(i)
                    cached_port.inputs = inputs

                if cached_port.outputs:
                    outputs = []
                    for i in cached_port.outputs:
                        parent = self.port_child_to_parent.get(i, None)
                        if parent:
                            outputs.append(parent)
                        else:
                            outputs.append(i)
                    cached_port.outputs = outputs

        # Remove the collapsed ports from source_to_target and move the removed content to the port parents.
        source_to_target_filtered = defaultdict(set)
        for source, target in self.source_to_target.items():
            if source in self.port_child_to_parent:
                source_to_target_filtered[self.port_child_to_parent[source]].update(target)
            else:
                source_to_target_filtered[source].update(target)

        self.source_to_target = source_to_target_filtered

        # Save connections
        for source, targets in self.source_to_target.items():
            source_node_id = self.port_to_id[source]
            source_port_id = port_to_port_id[source]
            source_cached_port = self.cached_nodes[source_node_id].cached_ports[source_port_id]
            for target in targets:
                target_node_id = self.port_to_id[target]
                target_port_id = port_to_port_id[target]
                target_cached_port = self.cached_nodes[target_node_id].cached_ports[target_port_id]

                connection = CacheConnection(source_cached_port, target_cached_port)

                self.connection_to_id[connection.pair] = len(self.cached_connections)
                self.cached_connections.append(connection)

    def get_diff(self, other: "GraphNodeIndex"):
        """Generates the difference object: the list of nodes and connections to add and delete.

        Args:
            other (GraphNodeIndex): The GraphNodeIndex to compare with the current GraphNodeIndex.

        Returns:
            GraphNodeDiff: An object representing the difference between this GraphNodeIndex and another."""
        # Nodes diff
        self_nodes = set(self.cached_nodes[i] for _, i in self.node_to_id.items())
        other_nodes = set(other.cached_nodes[i] for _, i in other.node_to_id.items())
        nodes_to_add = list(other_nodes - self_nodes)
        nodes_to_del = list(self_nodes - other_nodes)

        if len(self.node_to_id) == len(nodes_to_del):
            # If we need to remove all nodes, it's better to create a new graph node index
            return GraphNodeDiff()

        # Holding on to this in case we need something related for the backdrops zstack
        # max_level = max(self.cached_nodes[i].stacking_order for _, i in self.node_to_id.items())
        # for node in nodes_to_add:
        #     if node.stacking_order is not None and node.stacking_order < max_level:
        #         # We can't put the node under others. Only to top.
        #         return GraphNodeDiff()

        # Connections diff
        self_connections = set(self.cached_connections[i] for _, i in self.connection_to_id.items())
        other_connections = set(other.cached_connections[i] for _, i in other.connection_to_id.items())
        connections_to_add = list(other_connections - self_connections)
        connections_to_del = list(self_connections - other_connections)

        return GraphNodeDiff(nodes_to_add, nodes_to_del, connections_to_add, connections_to_del)

    def mutate(self, diff: Union["GraphNodeIndex", GraphNodeDiff]) -> Tuple[Set]:
        """Apply the difference to the cache index.

        Args:
            diff (Union["GraphNodeIndex", GraphNodeDiff]): The difference to apply to the current GraphNodeIndex.

        Returns:
            Tuple[Set]: A tuple containing sets of added nodes, deleted nodes, added connections, and deleted connections.
        """

        if isinstance(diff, GraphNodeIndex):
            diff = self.get_diff(diff)

        node_add = set()
        node_del = set()
        connection_add = set()
        connection_del = set()

        # Remove nodes from index
        for cached_node in diff.nodes_to_del:
            node = cached_node.node
            node_id = self.node_to_id[node]
            self.cached_nodes[node_id] = None

            for cached_port in cached_node.cached_ports:
                port = cached_port.port

                self.port_to_id.pop(port, None)
                if port in self.ports_used_as_output:
                    self.ports_used_as_output.remove(port)

                self.port_child_to_parent.pop(port, None)

            node_del.add(node)
            self.node_to_id.pop(node)

        # Remove connections from index
        for cached_connection in diff.connections_to_del:
            connection_id = self.connection_to_id[cached_connection.pair]
            self.cached_connections[connection_id] = None

            source_port = cached_connection.source_port
            target_port = cached_connection.target_port

            targets = self.source_to_target[source_port]
            targets.remove(target_port)
            if len(targets) == 0:
                self.source_to_target.pop(source_port)

            connection_del.add(cached_connection)
            self.connection_to_id.pop(cached_connection.pair)

        # Add nodes to index
        for cached_node in diff.nodes_to_add:
            node = cached_node.node
            node_id = len(self.cached_nodes)

            self.cached_nodes.append(cached_node)
            self.node_to_id[node] = node_id
            node_add.add(node)

            cached_ports = cached_node.cached_ports

            # True if node has output node
            node_has_outputs = False

            for cached_port in cached_ports:
                port = cached_port.port
                self.port_to_id[port] = node_id

                self.ports_used_as_output

                if cached_port.outputs is not None:
                    node_has_outputs = True

                cached_port_parent = cached_port.parent_cached_port
                if cached_port_parent:
                    self.port_child_to_parent[cached_port.port] = cached_port_parent.port

            for cached_port in cached_ports:
                # If the node don't have any output (in OmniGraph inputs and
                # outputs are equal) we consider that all the input attributes
                # are used as outputs.
                if not node_has_outputs or cached_port.outputs is not None:
                    self.ports_used_as_output.add(cached_port.port)

        # Add connections to index
        for cached_connection in diff.connections_to_add:
            connection_id = len(self.cached_connections)

            self.cached_connections.append(cached_connection)
            self.connection_to_id[cached_connection.pair] = connection_id
            connection_add.add(cached_connection)

            source_port = cached_connection.source_port
            target_port = cached_connection.target_port

            self.source_to_target[source_port].add(target_port)

        return node_add, node_del, connection_add, connection_del
