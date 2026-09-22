import json
import random

from .graph_utils import draw_scene_graph, kruskal_mst
from .scene_node import PrimNode
from .spatial_compute import (
    create_edge_same_hierarchy,
    get_node_coord,
    get_opposite_spatial_relations,
    vertical_i_supports_j_node,
)


class SceneGraph:
    """
    An undirected graph representation of a scene. Each node in the graph is a PrimNode object. The graph edges
    represent spatial relationships between nodes.

    Attributes:
        nodes (Dict[int, PrimNode]): A map of nodes in the graph. The key is the hash value of the node.
        directed (bool): A flag indicating whether the graph is directed or not.
        index_count (int): The number of nodes in the graph.
        index_map (Dict[int, int]): A map of node indices to node hashes.
        feature_map (Dict[str, List[int]]): A map of node features to node hashes.
        support_tree (SupportTree): A support tree for the objects in the scene.
        caption_configs (Dict): A dictionary of caption configurations.

    """

    def __init__(self, caption_configs=None):
        self.nodes = {}
        self.directed = False
        self.index_count = 0
        self.index_map = {}
        self.feature_map = {"character": [], "object": []}
        self.support_tree = None
        self.caption_configs = caption_configs

    def add_node(self, usd_node):
        """Add a node to the graph"""
        node_hash = hash(usd_node)

        if node_hash not in self.nodes:
            self.nodes[node_hash] = usd_node
            self.index_map[self.index_count] = node_hash
            self.index_count += 1
            feature = usd_node.category
            self.feature_map[feature].append(node_hash)

    def create_edge(self, usd_node1, usd_node2, edge_type="obj-obj", relation=None):
        """Add an edge between two nodes"""
        if hash(usd_node1) == hash(usd_node2):
            if self.caption_configs["verbose"]:
                print("Cannot add an edge to the same node. Skipped.")
        elif hash(usd_node1) in self.nodes and hash(usd_node2) in self.nodes:
            if hash(usd_node2) not in self.nodes[hash(usd_node1)].edges:
                self.nodes[hash(usd_node1)].add_edge(usd_node2, edge_type, relation)
                if not self.directed:
                    # If the graph is undirected, add the reverse edge
                    new_relation = get_opposite_spatial_relations(relation) if relation else None
                    self.nodes[hash(usd_node2)].add_edge(usd_node1, edge_type, new_relation)
        else:
            if self.caption_configs["verbose"]:
                print(f"One or both nodes {usd_node1}, {usd_node2} do not exist.")

    def _build_support_tree(self):
        """
        Build a support tree for the objects in the scene.
        """
        # Create a support tree with the floor as the root node

        # find if floor exists
        object_list = []
        floor_node = None
        for node_hash in self.feature_map["object"]:
            if "floor" not in self.nodes[node_hash].label:
                object_list.append(self.nodes[node_hash])
            else:
                floor_node = self.nodes[node_hash]
        if floor_node:
            support_tree = SupportTree(floor_node)
        else:
            support_tree = SupportTree()

        support_tree.build_tree(object_list)
        if self.caption_configs["verbose"]:
            support_tree.display()
        return support_tree

    def _build_object_edges(self):
        """
        Build edges between object nodes.
        """
        support_tree = self._build_support_tree()
        level_one_nodes = support_tree.get_nodes_at_level(1)
        self.support_tree = support_tree

        # randomly sample no more than 30 level one nodes:
        if len(level_one_nodes) > 30:
            level_one_nodes = random.sample(level_one_nodes, 30)

        # build children edges for the whole tree, starting from level one
        def build_support_edges(node):
            for child in node.children:
                self.create_edge(node, child, "obj-obj", "supports")
                build_support_edges(child)

        for node in level_one_nodes:
            build_support_edges(node)

        # build edges for nodes at level 1
        for i, node1 in enumerate(level_one_nodes):
            for node2 in level_one_nodes[i + 1 :]:
                if node1 != node2:
                    i_coord, j_coord = get_node_coord(node1, world=False), get_node_coord(node2, world=False)
                    i_centroid, j_centroid = node1.centroid_3d, node2.centroid_3d
                    relations = create_edge_same_hierarchy(i_coord, j_coord, i_centroid, j_centroid)
                    if relations:
                        relation = ",".join(relations)
                        self.create_edge(node1, node2, "obj-obj", relation)
                    # else:
                    #     print(f"No relation between {node1} and {node2}")

        return level_one_nodes

    def _build_obj_char_edges(self, level_one_nodes):
        # Assumes that characters are standing on the floor
        for char_hash in self.feature_map["character"]:
            char = self.nodes[char_hash]
            for obj in level_one_nodes:
                i_coord, j_coord = get_node_coord(char, world=False), get_node_coord(obj, world=False)
                i_centroid, j_centroid = char.centroid_3d, obj.centroid_3d
                relations = create_edge_same_hierarchy(i_coord, j_coord, i_centroid, j_centroid)
                if relations:
                    relation = ",".join(relations)
                    self.create_edge(char, obj, "character-obj-spatial", relation)
                # else:
                #     print(f"No relation between {char} and {obj}")

    def build_graph(self):
        """
        Build the graph by adding edges between nodes.
        """
        # build graph layer by layer

        level_one_objects = self._build_object_edges()
        self._build_obj_char_edges(level_one_objects)

        # total number of edges:
        total_edges = self.get_edges_number()
        if self.caption_configs["verbose"]:
            print(f"[IRC] Graph built with {len(self.nodes)} nodes and {total_edges} edges")

    def get_edges_number(self):
        total_edges = 0

        for node in self.nodes:
            for edge_type in self.nodes[node].edges:
                total_edges += len(self.nodes[node].edges[edge_type])

        return total_edges

    async def export_graph(self, filename=None):
        """
        Converts the graph to a dictionary and saves it as a JSON file.
        """
        graph = {"obj": {}, "character": {}, "edges": {"obj-obj": [], "character-obj-spatial": []}}
        export_edges = self.caption_configs["export_edges"]

        # assign id to each node, starting from 0
        node_id = 0
        for node_hash in self.feature_map["object"]:
            node = self.nodes[node_hash]
            node_dict = {
                "class": node.label,
                "3d_bbox": node.bbox_3d,
                "2d_bbox": node.bbox_2d,
                "3d_centroid": node.centroid_3d,
                "caption": node.caption,
                "id": node_id,
            }
            if export_edges:
                node_dict["world_3d_bbox"] = node.world_bbox_3d
            graph["obj"][node.prim_path] = node_dict
            node_id += 1

        for node_hash in self.feature_map["character"]:
            node = self.nodes[node_hash]
            node_dict = {
                "label": node.label,
                "caption": node.caption,
                "location": node.centroid_3d,
                "3d_bbox": node.bbox_3d,
                "2d_bbox": node.bbox_2d,
                "id": node_id,
            }
            if self.caption_configs["export_world"]:
                node_dict["world_3d_bbox"] = node.world_bbox_3d
            graph["character"][node.prim_path] = node_dict
            node_id += 1

        if export_edges:
            for node_hash in self.nodes:
                for edge_type in self.nodes[node_hash].edges:
                    for neighbor_hash, edge in self.nodes[node_hash].edges[edge_type].items():
                        node_prim = self.nodes[node_hash].prim_path
                        neighbor_prim = self.nodes[neighbor_hash].prim_path
                        edge_dict = {
                            "source": node_prim,
                            "source_name": self.nodes[node_hash].label,
                            "target": neighbor_prim,
                            "target_name": self.nodes[neighbor_hash].label,
                            "relation": edge["relation"],
                        }
                        graph["edges"][edge_type].append(edge_dict)

        if filename:
            with open(filename, "w") as f:
                json.dump(graph, f, indent=4)
            if self.caption_configs["verbose"]:
                print(f"[IRC] Scene graph has been successfully saved to {filename}")

        return graph

    def prune(self):
        """
        Reduces the number of edges in the graph but keeps the nodes.
        """
        prob = self.caption_configs["pruning_ratio"]
        mst = kruskal_mst(self, prob, random_seed=self.caption_configs["random_seed"])
        for node_hash, node in self.nodes.items():
            for edge_type in node.edges:
                node.edges[edge_type] = {}
                if node_hash in mst[edge_type]:
                    for neighbor_hash, relation in mst[edge_type][node_hash]:
                        node.edges[edge_type][neighbor_hash] = {"node": self.nodes[neighbor_hash], "relation": relation}
        if self.caption_configs["verbose"]:
            print("Graph pruned")
            print(f"Number of nodes: {len(self.nodes)}, number of edges: {self.get_edges_number()}")

    def draw_graph(self, image, filename=None):
        """Draw the scene graph on an image. The image must match the scene graph.

        image(np.array): The image to draw the scene graph on.
        filename(str): The address of the output image file.
        """
        image = draw_scene_graph(image, self, filename)
        # Save or display the output image (for visualization purposes)

        return image

    def clear(self):
        """
        Clears the graph.
        """
        self.nodes = {}
        self.index_count = 0
        self.index_map = {}
        self.feature_map = {"character": [], "object": []}
        print("Graph cleared")

    def __len__(self):
        """
        Returns the number of nodes and edges in the graph.
        """
        return len(self.nodes), self.get_edges_number()

    def __repr__(self):
        """
        Returns a string representation of the graph.
        """
        rstring = ""
        hash_to_index = {v: k for k, v in self.index_map.items()}
        for node in self.nodes:
            edges = self.nodes[node].edges
            feature = self.nodes[node].category
            rstring += f"{self.nodes[node]}: ID: {hash_to_index[node]}, feature: {feature}\n"
            for edge_type in edges:
                rstring += f"  {edge_type}: {[(self.nodes[neighbor], edges[edge_type][neighbor]['relation']) for neighbor in edges[edge_type]]}\n"

        return rstring[:-1]


class SupportTree:
    def __init__(self, root_node=None):
        #
        """
        Initialize the tree with the root node (floor). If floor is one of the node, pick it out.
        Otherwise, create a new node for the floor.

        root_node (PrimNode): The root node of the tree.
        """
        if not root_node:
            root_node = PrimNode("/floor", category="object")
            root_node.label = "floor"
        self.root = root_node

    def build_tree(self, objects):
        """
        Iterate through the objects and build the tree using is_vertical_func.
        The root node is the floor.

        objects (List[PrimNode]): List of PrimNode objects in the room.
        """
        # Skip the root node (floor) since it doesn't need to be supported

        # Continue building the tree by checking each pair of objects.
        for obj_a in objects:
            for obj_b in objects:
                if obj_a != obj_b and vertical_i_supports_j_node(obj_a, obj_b):
                    # avoid the situation that obj_a is supported by obj_b and obj_b is supported by obj_a
                    if not vertical_i_supports_j_node(obj_b, obj_a):
                        obj_a.add_child(obj_b)

        # connect the root node to the objects
        for obj in objects:
            if obj.parent is None:
                self.root.add_child(obj)

    def display(self, node=None, level=0):
        """
        Displays the SupportTree tree structure.

        node(PrimNode): The current node being processed (defaults to root).
        level(int): The current depth in the recursive traversal.
        """
        # Recursively display the tree structure
        if node is None:
            node = self.root
        print(" " * (level * 4) + node.label)
        for child in node.children:
            self.display(child, level + 1)

    def get_nodes_at_level(self, level, node=None, current_level=0):
        """
        Returns a list of all nodes at the specified level.

        level(int): The depth level at which to gather nodes.
        node(PrimNode): The current node being processed (defaults to root).
        current_level(int): The current depth in the recursive traversal.

        Returns:
        List[PrimNode]: A list of nodes at the specified level.
        """
        if node is None:
            node = self.root

        # If the current level matches the target level, return the node's name
        if current_level == level:
            return [node]

        # Otherwise, keep traversing to find nodes at the target level
        nodes_at_level = []
        for child in node.children:
            nodes_at_level.extend(self.get_nodes_at_level(level, child, current_level + 1))

        return nodes_at_level
