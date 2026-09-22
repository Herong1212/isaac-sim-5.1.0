# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""This module provides the SugiyamaLayout class for computing coordinates to draw directed graphs using Sugiyama's method."""


__all__ = ["SugiyamaLayout"]

from collections import defaultdict
from bisect import bisect


class SugiyamaLayout:
    """Compute the coordinates for drawing directed graphs following the method
    developed by Sugiyama.

    This method consists of four phases:
    1. Cycle Removal
    2. Layer Assignment
    3. Crossing Reduction
    4. Coordinate Assignment

    As input it takes the list of edges in the following format:
    [(vertex1, vertex2), (vertex3, vertex4), ... ]

    Once the object is created, it's possible to get the node layer number
    immediately.

    To get the node positions, it's necessary to set each node's size and
    call `update_positions`.

    Follows closely to the following papers:
    [1] "An Efficient Implementation of Sugiyama's Algorithm for Layered Graph Drawing"
    Eiglsperger Siebenhaller Kaufmann
    [2] "Sugiyama Algorithm"
    Nikolov
    [3] "Graph Drawing Algorithms in Information Visualization"
    Frishman

    Args:
        edges (list): List of edges in the graph.
        vertical_distance (float): The vertical distance between layers.
        horizontal_distance (float): The horizontal distance between nodes within a layer.

    Attributes:
        Node (class): Temporary node that caches all the intermediate compute data."""

    class Node:
        """Temporary node that caches all the intermediate compute data"""

        def __init__(self, id):
            self.id = id

            # Upstream and downstream nodes
            self.upstream = []
            self.downstream = []

            # For iteration
            self.is_currently_iterating = False
            self.highest_iteration_index = 0
            self.lowest_iteration_index = 0

            # Layer and position
            self.layer = None
            self.is_dummy = False
            # Barycenter is the position in the layer in [0..1] interval
            self.barycenter = None
            self.index_in_layer = None

            # The final geometry
            self.width = None
            self.height = None
            self.final_position = None

            self.root = None
            self.horizontal_aligned_to = None
            self.vertical_aligned_to = None
            self.offset = None
            self.max_y = None
            self.bound = [0.0, 0.0, 0.0, 0.0]

        def add_upstream(self, node):
            """Add the upstream node. It will add current node to downstream as well."""
            if node.id not in self.upstream:
                self.upstream.append(node.id)

            if self.id not in node.downstream:
                node.downstream.append(self.id)

        def __repr__(self):
            result = f"<Node {self.id}: up"
            for n in self.upstream:
                result += f" {n}"
            result += "; down"
            for n in self.downstream:
                result += f" {n}"
            result += f"; layer_id{self.layer}>"
            return result

    def __init__(self, edges=[], vertical_distance=10.0, horizontal_distance=10.0):
        """Initialize the SugiyamaLayout with optional edges, vertical and horizontal distances."""
        # Minimal space between items
        self.vertical_distance = vertical_distance
        self.horizontal_distance = horizontal_distance

        # Current alignment direction. It will call property setter.
        self._alignment_direction = 0

        # Counter for creating dummy nodes. Dummy nodes are negative ID.
        self._dummy_counter = -1
        self._edges = set(edges)

        # All the nodes
        self._nodes = {}
        # Connected graphs
        self._graphs = []
        #
        self._dummies = {}
        # All the layers it's a dict with list of vertices id
        self._layers = defaultdict(list)

        # The action
        self._split_to_graphs()
        self._layout()

    @property
    def _alignment_direction(self):
        return self.__alignment_direction

    @property
    def _alignment_direction_horizontal(self):
        return self.__alignment_direction_horizontal

    @property
    def _alignment_direction_vertical(self):
        return self.__alignment_direction_vertical

    @_alignment_direction.setter
    def _alignment_direction(self, alignment_direction):
        """
        Alignment policy:
        _alignment_direction=0 -> vertical=1, horizontal=-1
        _alignment_direction=1 -> vertical=-1, horizontal=-1
        _alignment_direction=2 -> vertical=1, horizontal=1
        _alignment_direction=3 -> vertical=-1, horizontal=1
        """
        self.__alignment_direction = alignment_direction
        self.__alignment_direction_vertical, self.__alignment_direction_horizontal = {
            0: (1, -1),
            1: (-1, -1),
            2: (1, 1),
            3: (-1, 1),
        }[alignment_direction]

    @_alignment_direction_horizontal.setter
    def _alignment_direction_horizontal(self, _alignment_direction_horizontal):
        _alignment_direction = (_alignment_direction_horizontal + 1) + (1 - self.__alignment_direction_vertical) // 2
        self._alignment_direction = _alignment_direction

    @_alignment_direction_vertical.setter
    def _alignment_direction_vertical(self, _alignment_direction_vertical):
        _alignment_direction = (self.__alignment_direction_horizontal + 1) + (1 - _alignment_direction_vertical) // 2
        self._alignment_direction = _alignment_direction

    def _get_roots(self, graph):
        # Nodes that doesn't have anything downstream
        current_roots = []
        for edge in graph:
            vertex = edge[0]
            if not self._nodes[vertex].downstream:
                current_roots.append(self._nodes[vertex])

        return current_roots

    def __get_connected_dummy(self, node):
        dummy_id = node.dummy_nodes.get(node.layer - 1, None)
        return [dummy_id] if dummy_id is not None else []

    def __is_between_dummies(self, node):
        return any([x.is_dummy for x in self.__get_connected_dummy(node)])

    def __iterate_node_edges(self, node, counter, visited, reversed_edges):
        counter[0] += 1
        node.highest_iteration_index = counter[0]
        node.lowest_iteration_index = counter[0]
        visited.append(node)

        node.is_currently_iterating = True

        for vertex in node.upstream:
            upstream = self._nodes[vertex]
            if upstream.highest_iteration_index == 0:
                self.__iterate_node_edges(upstream, counter, visited, reversed_edges)
                node.lowest_iteration_index = min(node.lowest_iteration_index, upstream.lowest_iteration_index)
            elif upstream.is_currently_iterating:
                # It's a loop. We need to invert this connection.
                reversed_edges.append((node.id, upstream.id))
            if upstream in visited:
                node.lowest_iteration_index = min(node.lowest_iteration_index, upstream.highest_iteration_index)

        if node.lowest_iteration_index == node.highest_iteration_index:
            backtracing = [visited.pop()]
            while backtracing[-1] != node:
                backtracing.append(visited.pop())

        node.is_currently_iterating = False

    def _get_reversed_edges(self, graph, roots):
        counter = [0]
        visited = []
        reversed_edges = []

        for vertex, node in self._nodes.items():
            node.highest_iteration_index = 0

        # Start from roots
        for root in roots:
            self.__iterate_node_edges(root, counter, visited, reversed_edges)

        # Iterate rest
        for edge in graph:
            for vertex in edge:
                node = self._nodes[vertex]
                if node.highest_iteration_index == 0:
                    self.__iterate_node_edges(node, counter, visited, reversed_edges)

        return reversed_edges

    def _invert_edge(self, edge):
        """Invert the flow direction of the given edge"""
        v1 = edge[0]
        v2 = edge[1]
        node1 = self._nodes[v1]
        node1.upstream.remove(v2)
        node2 = self._nodes[v2]
        node2.downstream.remove(v1)
        node2.add_upstream(node1)

    def _set_layer(self, node):
        """Set the layer id of the node"""
        current_layer = node.layer
        # Layers start from 1
        new_layer = max([self._nodes[x].layer for x in node.downstream] + [0]) + 1

        if current_layer == new_layer:
            # Nothing changed
            return

        if current_layer is not None:
            self._layers[current_layer].remove(node.id)

        node.layer = new_layer
        self._layers[node.layer].append(node.id)

    def _iterate_layer(self, roots):
        scaned_edges = {}
        # Roots are in the first layer
        current_layer = roots
        while len(current_layer) > 0:
            next_layer = []
            for node in current_layer:
                self._set_layer(node)
                # Mark out-edges has scanned.
                for vertex in node.upstream:
                    edge = (node.id, vertex)
                    scaned_edges[edge] = True
                # Check if out-vertices are rank-able.
                for x in node.upstream:
                    upstream = self._nodes[x]
                    if not (
                        False in [scaned_edges.get((vertex, upstream.id), False) for vertex in upstream.downstream]
                    ):
                        if x not in next_layer:
                            next_layer.append(self._nodes[x])
            current_layer = next_layer

    def _create_dummy(self, layer, dummy_nodes):
        """Create a dummy node and put it to the layer."""
        # Setup a new node
        dummy_node = self._nodes[self._dummy_counter] = self.Node(self._dummy_counter)
        self._dummy_counter -= 1
        dummy_node.is_dummy = True
        dummy_node.layer = layer
        dummy_node.width = 0.0
        dummy_node.height = 0.0

        self._layers[layer].append(dummy_node.id)
        dummy_node.dummy_nodes = dummy_nodes
        dummy_nodes[layer] = dummy_node
        return dummy_node

    def _create_dummies(self, edge):
        """Create and all dummy nodes for the given edge."""
        v1, v2 = edge
        layer1, layer2 = self._nodes[v1].layer, self._nodes[v2].layer
        if layer1 > layer2:
            v1, v2 = v2, v1
            layer1, layer2 = layer2, layer1
        if (layer2 - layer1) > 1:
            # "dummy vertices" are stored in the dict, keyed by their layer.
            dummy_nodes = self._dummies[edge] = {}
            node1 = self._nodes[v1]
            node2 = self._nodes[v2]
            dummy_nodes[layer1] = node1
            dummy_nodes[layer2] = node2

            # Disconnect the nodes
            node1.upstream.remove(v2)
            node2.downstream.remove(v1)

            # Insert dummies between nodes
            prev_dummy = node1
            for layer_id in range(layer1 + 1, layer2):
                dummy = self._create_dummy(layer_id, dummy_nodes)
                prev_dummy.add_upstream(dummy)
                prev_dummy = dummy

            prev_dummy.add_upstream(node2)

    def _get_cross_count(self, layer_id):
        """Number of crosses in the layer"""
        neighbor_indices = []
        layer = self._layers[layer_id]
        for vertex in layer:
            node = self._nodes[vertex]
            neighbor_indices.extend(
                sorted([self._nodes[neighbor].index_in_layer for neighbor in self._get_neighbors(node)])
            )

        s = []
        count = 0
        for i, neighbor_index in enumerate(neighbor_indices):
            j = bisect(s, neighbor_index)
            if j < i:
                count += i - j
            s.insert(j, neighbor_index)
        return count

    def _get_next_layer_id(self, layer_id):
        """The layer that is the next according to the current slignment direction"""
        layer_id += 1 if self._alignment_direction_horizontal == -1 else -1
        return layer_id

    def _get_prev_layer_id(self, layer_id):
        """The layer that is the previous according to the current slignment direction"""
        layer_id += 1 if self._alignment_direction_horizontal == 1 else -1
        return layer_id

    def _get_mean_value_position(self, node):
        """
        Compute the position of the node according to the position of
        neighbors in the previous layer. It's the mean value of adjacent
        positions of neighbors.
        """
        layer_id = node.layer
        prev_layer = self._get_prev_layer_id(layer_id)
        if prev_layer not in self._layers:
            return node.barycenter
        bars = [self._nodes[vertex].barycenter for vertex in self._get_neighbors(node)]
        return node.barycenter if len(bars) == 0 else float(sum(bars)) / len(bars)

    def _reduce_crossings(self, layer_id):
        """
        Reorder the nodes in the layer to reduce the number of crossings in the layer.

        Return the new number of crossing.
        """
        layer = self._layers[layer_id]
        num_nodes = len(layer)
        total_crossings = 0
        for i, j in zip(range(num_nodes - 1), range(1, num_nodes)):
            vertex_i = layer[i]
            vertex_j = layer[j]
            barycenters_neighbors_i = [
                self._nodes[vertex].barycenter for vertex in self._get_neighbors(self._nodes[vertex_i])
            ]
            barycenters_neighbors_j = [
                self._nodes[vertex].barycenter for vertex in self._get_neighbors(self._nodes[vertex_j])
            ]
            crossings_ij = crossings_ji = 0
            for neightbor_j in barycenters_neighbors_j:
                crossings = len([neighbor_i for neighbor_i in barycenters_neighbors_i if neighbor_i > neightbor_j])
                # Crossings we have now
                crossings_ij += crossings
                # Crossings we would have if swap verices
                crossings_ji += len(barycenters_neighbors_i) - crossings
            if crossings_ji < crossings_ij:
                # Swap vertices
                layer[i] = vertex_j
                layer[j] = vertex_i
                total_crossings += crossings_ji
            else:
                total_crossings += crossings_ij
        return total_crossings

    def _reorder(self, layer_id):
        """
        Reorder the nodes within the layer to reduce the number of crossings in the layer.

        Return the number of crossing.
        """
        # TODO: Use code from _reduce_crossings to find the initial number of
        # crossings.
        c = self._get_cross_count(layer_id)
        layer = self._layers[layer_id]
        barycenter_height = 1.0 / (len(layer) - 1) if len(layer) > 1 else 1.0
        if c > 0:
            for vertex in layer:
                node = self._nodes[vertex]
                node.barycenter = self._get_mean_value_position(node)
            # Reorder layers according to barycenter.
            layer.sort(key=lambda x: self._nodes[x].barycenter)
            c = self._reduce_crossings(layer_id)
            # Re assign new position since it was reordered
            for i, vertex in enumerate(layer):
                self._nodes[vertex].index_in_layer = i
                self._nodes[vertex].barycenter = i * barycenter_height
        return c

    def _ordering_pass(self, direction=-1):
        """
        Ordering of the vertices such that the number of edge crossings is reduced.
        """
        crossings = 0

        self._alignment_direction_horizontal = direction
        for layer_id in sorted(self._layers.keys())[::-direction]:
            crossings += self._reorder(layer_id)

        return crossings

    def _get_neighbors(self, node):
        """
        Neighbors are to left/right adjacent nodes. Node.upstream/downstream
        have connections from all the layers. This returns from neighbour
        layers according to the current alignment direction.
        """
        alignment_direction_horizontal = self._alignment_direction_horizontal
        # TODO: It's called very often. We need to cache it.
        node.neighbors_at_direction = {-1: list(node.downstream), 1: list(node.upstream)}
        if node.is_dummy:
            return node.neighbors_at_direction[alignment_direction_horizontal]
        for direction in (-1, 1):
            tr = node.layer + direction
            for i, x in enumerate(node.neighbors_at_direction[direction]):
                if self._nodes[x].layer == tr:
                    continue
                # TODO: check if we need this code. upstream/downstream has dummies.
                edge = (node.id, x)
                if edge not in self._dummies:
                    edge = (x, node.id)
                dum = self._dummies[edge][tr]
                node.neighbors_at_direction[direction][i] = dum.id
        return node.neighbors_at_direction[alignment_direction_horizontal]

    def _get_median_index(self, node):
        """
        Find the position of node according to neigbor positions in neigbor layer.
        """
        neighbors = self._get_neighbors(node)
        index_in_layer = [self._nodes[x].index_in_layer for x in neighbors]
        neighbors_size = len(index_in_layer)
        if neighbors_size == 0:
            return []
        index_in_layer.sort()
        index_in_layer = index_in_layer[:: self._alignment_direction_vertical]
        i, j = divmod(neighbors_size - 1, 2)
        return [index_in_layer[i]] if j == 0 else [index_in_layer[i], index_in_layer[i + j]]

    def _horizontal_alignment(self):
        """
        Horizontal alignment according to current alignment direction.
        """
        alignment_direction_vertical, alignment_direction_horizontal = (
            self._alignment_direction_vertical,
            self._alignment_direction_horizontal,
        )
        for layer_id in sorted(self._layers.keys())[::-alignment_direction_horizontal]:
            prev_layer_id = self._get_prev_layer_id(layer_id)
            if prev_layer_id not in self._layers:
                continue

            current_vertex_index = None
            layer = self._layers[layer_id]
            prev_layer = self._layers[prev_layer_id]
            for vertex in layer[::alignment_direction_vertical]:
                node = self._nodes[vertex]
                for median_vertex_index in self._get_median_index(node):
                    median_vertex = prev_layer[median_vertex_index]
                    if self._nodes[vertex].horizontal_aligned_to is vertex:
                        if alignment_direction_horizontal == 1:
                            edge = (vertex, median_vertex)
                        else:
                            edge = (median_vertex, vertex)

                        if edge in self._dummy_intersections:
                            continue

                        if (current_vertex_index is None) or (
                            alignment_direction_vertical * current_vertex_index
                            < alignment_direction_vertical * median_vertex_index
                        ):
                            # Align median
                            self._nodes[median_vertex].horizontal_aligned_to = vertex

                            # Align the given one
                            median_root = self._nodes[median_vertex].root
                            self._nodes[vertex].horizontal_aligned_to = median_root
                            self._nodes[vertex].root = median_root

                            current_vertex_index = median_vertex_index

    def _align_subnetwork(self, vertex):
        """
        Vertical alignment according to current alignment direction.
        """
        if self._nodes[vertex].max_y is not None:
            return

        self._nodes[vertex].max_y = 0.0
        vertex_to_align = vertex
        while True:
            prev_index_in_layer = self._nodes[vertex_to_align].index_in_layer - self._alignment_direction_vertical
            layer_id = self._nodes[vertex_to_align].layer

            if 0 <= prev_index_in_layer < len(self._layers[layer_id]):
                prev_vertex_id = self._layers[layer_id][prev_index_in_layer]
                vertical_distance = (
                    self.vertical_distance
                    + self._nodes[prev_vertex_id].height * 0.5
                    + self._nodes[vertex_to_align].height * 0.5
                )

                # Recursively place subnetwork
                root_vertex_id = self._nodes[prev_vertex_id].root
                self._align_subnetwork(root_vertex_id)

                # Adjust node position
                if self._nodes[vertex].vertical_aligned_to is vertex:
                    self._nodes[vertex].vertical_aligned_to = self._nodes[root_vertex_id].vertical_aligned_to

                if self._nodes[vertex].vertical_aligned_to == self._nodes[root_vertex_id].vertical_aligned_to:
                    self._nodes[vertex].max_y = max(
                        self._nodes[vertex].max_y, self._nodes[root_vertex_id].max_y + vertical_distance
                    )
                else:
                    aligned_vertex = self._nodes[root_vertex_id].vertical_aligned_to
                    offset = self._nodes[vertex].max_y - self._nodes[root_vertex_id].max_y + vertical_distance
                    if self._nodes[aligned_vertex].offset is None:
                        self._nodes[aligned_vertex].offset = offset
                    else:
                        self._nodes[aligned_vertex].offset = min(self._nodes[aligned_vertex].offset, offset)

            vertex_to_align = self._nodes[vertex_to_align].horizontal_aligned_to
            if vertex_to_align is vertex:
                # Already aligned
                break

    def _vertical_alignment(self):
        """
        Vertical alignment according to current alignment direction.
        """
        _alignment_direction_vertical, _alignment_direction_horizontal = (
            self._alignment_direction_vertical,
            self._alignment_direction_horizontal,
        )
        layer_ids = sorted(self._layers.keys())[::-_alignment_direction_horizontal]

        for layer_id in layer_ids:
            for vertex in self._layers[layer_id][::_alignment_direction_vertical]:
                if self._nodes[vertex].root is vertex:
                    self._align_subnetwork(vertex)

        # Mirror nodes when the alignment is bottom.
        if _alignment_direction_vertical == -1:
            for layer_id in layer_ids:
                for vertex in self._layers[layer_id]:
                    y = self._nodes[vertex].max_y
                    if y:
                        self._nodes[vertex].max_y = -y

        # Assign bound
        bound = None
        for layer_id in layer_ids:
            for vertex in self._layers[layer_id][::_alignment_direction_vertical]:
                self._nodes[vertex].bound[self._alignment_direction] = self._nodes[self._nodes[vertex].root].max_y
                aligned_vertex = self._nodes[self._nodes[vertex].root].vertical_aligned_to
                offset = self._nodes[aligned_vertex].offset
                if offset is not None:
                    self._nodes[vertex].bound[self._alignment_direction] += _alignment_direction_vertical * offset
                if bound is None:
                    bound = self._nodes[vertex].bound[self._alignment_direction]
                else:
                    bound = min(bound, self._nodes[vertex].bound[self._alignment_direction])

        # Initialize
        for layer_id, layer in self._layers.items():
            for vertex in layer:
                self._nodes[vertex].root = vertex
                self._nodes[vertex].horizontal_aligned_to = vertex
                self._nodes[vertex].vertical_aligned_to = vertex
                self._nodes[vertex].offset = None
                self._nodes[vertex].max_y = None

    def _split_to_graphs(self):
        """Split edges to multiple connected graphs. Result is self._graphs."""
        # All vertices
        vertices = set()

        # Dict where key is vertex, value is all the connected vertices
        dependencies = defaultdict(set)

        for v1, v2 in self._edges:
            vertices.add(v1)
            vertices.add(v2)

            dependencies[v1].add(v2)
            dependencies[v2].add(v1)

            if v1 in self._nodes:
                n1 = self._nodes[v1]
            else:
                n1 = self.Node(v1)
                self._nodes[v1] = n1

            if v2 in self._nodes:
                n2 = self._nodes[v2]
            else:
                n2 = self.Node(v2)
                self._nodes[v2] = n2

            n1.add_upstream(n2)

        while vertices:
            # Start with any vertex
            current_vertices = [vertices.pop()]
            # For each vertex, remove all connected from `vertices` and add it to current graph
            for vertex in current_vertices:
                for dependent in dependencies.get(vertex, []):
                    if dependent in vertices:
                        vertices.remove(dependent)
                        current_vertices.append(dependent)

            # Here `current_vertices` has all the vertices that are conneted to a single graph
            current_edges = set()
            for vertex in current_vertices:
                for edge in self._edges:
                    if edge[0] in current_vertices or edge[1] in current_vertices:
                        current_edges.add(edge)

            self._graphs.append(current_edges)

    def _find_dummy_intersections(self):
        """
        Detect crossings in dummy nodes.
        """
        self._dummy_intersections = []
        for layer_id, layer_vertices in self._layers.items():
            prev_layer_id = layer_id - 1
            if prev_layer_id not in self._layers:
                continue

            first_vertex = 0
            vertices_count = len(layer_vertices) - 1
            prev_layer_vertices_count = len(self._layers[prev_layer_id]) - 1
            vertex_range_from = 0
            for i, current_vertex_id in enumerate(layer_vertices):
                node = self._nodes[current_vertex_id]
                if not node.is_dummy:
                    continue

                if i == vertices_count or self.__is_between_dummies(node):
                    connected_dummy_index = prev_layer_vertices_count
                    if self.__is_between_dummies(node):
                        connected_dummy_index = self.__get_connected_dummy(node)[-1].index_in_layer
                    for vertex_in_this_layer in layer_vertices[vertex_range_from : i + 1]:
                        for neighbor in self._get_neighbors(self._nodes[vertex_in_this_layer]):
                            neighbor_index = self._nodes[neighbor].index_in_layer
                            if neighbor_index < first_vertex or neighbor_index > connected_dummy_index:
                                # Intersection found
                                self._dummy_intersections.append((neighbor, vertex_in_this_layer))

                    vertex_range_from = i + 1
                    first_vertex = connected_dummy_index

    def _layout(self):
        """Perform first three steps of Sugiyama layouting"""
        for graph in self._graphs:
            # 1. Cycle Removal
            roots = self._get_roots(graph)
            reversed_edges = self._get_reversed_edges(graph, roots)

            # Make the graph acyclic by reversing appropriate edges.
            for edge in reversed_edges:
                self._invert_edge(edge)

            # Get roots one more time
            roots += [node for node in self._get_roots(graph) if node not in roots]

            # 2. Layer Assignment
            self._iterate_layer(roots)

            # TODO: Optimize layers. Root nodes could potentially go to other
            # layers if it could minimize crossings

            # Add dummies
            for edge in graph:
                self._create_dummies(edge)

        # Pre-setup of some indices
        for _, layer in self._layers.items():
            # Barycenter is the position in the layer in [0..1] interval
            barycenter_height = 1.0 / (len(layer) - 1) if len(layer) > 1 else 1.0
            for i, vertex in enumerate(layer):
                node = self._nodes[vertex]
                node.index_in_layer = i
                node.barycenter = i * barycenter_height

        # 3. Crossing Reduction, 2 passes in both direction for optimal ordering
        for i in range(2):
            # Ordering pass for layers from 0 to end
            crossings = self._ordering_pass()
            if crossings > 0:
                # Second pass in reverse direction
                self._ordering_pass(direction=1)

        self._ordering_pass()

        # 3a. Crossing Reduction in dummy nodes
        self._find_dummy_intersections()

    def update_positions(self):
        """4. Coordinate Assignment"""
        # Initialize node attributes.
        # TODO: Put it to init
        for _, layer in self._layers.items():
            for vertex in layer:
                node = self._nodes[vertex]
                node.root = vertex
                node.horizontal_aligned_to = vertex
                node.vertical_aligned_to = vertex
                node.offset = None
                node.max_y = None
                node.bound = [0.0, 0.0, 0.0, 0.0]

        for _alignment_direction in range(4):
            self._alignment_direction = _alignment_direction
            self._horizontal_alignment()
            self._vertical_alignment()

        # Final coordinate assigment of all nodes:
        x_counter = 0
        for _, layer in self._layers.items():
            if not layer:
                continue

            max_width = max([self._nodes[vertex].width / 2.0 for vertex in layer])

            y_counter = None
            for vertex in layer:
                y = sorted(self._nodes[vertex].bound)
                # Average of computed bound
                average_y = (y[1] + y[2]) / 2.0

                # Prevent node intersections
                if y_counter is None:
                    y_counter = average_y
                y_counter = max(y_counter, average_y)

                # Final xy-coordinates. Negative X because we go from right to left.
                self._nodes[vertex].final_position = (-x_counter - max_width, y_counter)

                y_counter += self._nodes[vertex].height + self.vertical_distance

            x_counter += 2 * max_width + self.horizontal_distance

    def set_size(self, vertex, width, height):
        """Sets the size of the node.

        Args:
            vertex: The identifier of the node.
            width: The width of the node.
            height: The height of the node."""
        node = self._nodes.get(vertex, None)
        if not node:
            # The node not in the list because the node is not connected to anythig.
            # Since the graph layers start from 1, we put those non-graph
            # vertices to the layer 0 and they will stay in a separate column.
            layer_id = 0
            node = self.Node(vertex)
            node.layer = layer_id
            node.index_in_layer = len(self._layers[layer_id])

            self._nodes[node.id] = node
            self._layers[layer_id].append(node.id)

        node.width = width
        node.height = height

    def get_position(self, vertex):
        """Returns the position of the specified node.

        Args:
            vertex: The identifier of the node.

        Returns:
            The position of the node if the node exists."""
        node = self._nodes.get(vertex, None)
        if node:
            return node.final_position

    def get_layer(self, vertex):
        """Returns the layer id of the specified node.

        Args:
            vertex: The identifier of the node.

        Returns:
            The layer id of the node if the node exists."""
        node = self._nodes.get(vertex, None)
        if node:
            return node.layer
