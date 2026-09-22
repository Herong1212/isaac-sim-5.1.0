import random
import textwrap
from collections import defaultdict


# Function to draw nodes and edges
def draw_scene_graph(image_data, scene_graph, filename=None):
    """
    Draws the scene graph on the image data and saves it to a file.

    image_data (np.ndarray): the image data to draw the scene graph on.
    scene_graph (SceneGraph): the scene graph object.
    filename (str): the file address to save the image to.
    """
    import cv2

    image = cv2.cvtColor(image_data, cv2.COLOR_RGB2BGR)
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    font_thickness = 1
    color = (0, 0, 0)  # Red color for text
    box_color = (255, 255, 255)
    arrow_color = (255, 0, 0)  # Blue color for arrows
    square_size = 30
    wrap_width = 30

    hash_to_id_map = {hashcode: index for index, hashcode in scene_graph.index_map.items()}

    # Draw nodes
    for node_hash, node in scene_graph.nodes.items():

        # skip nodes without edges
        if not node.edges["obj-obj"] and not node.edges["character-obj-spatial"]:
            continue

        bbox = node.bbox_2d
        center_x = int((bbox[0] + bbox[2]) // 2)
        center_y = int((bbox[1] + bbox[3]) // 2)

        # Draw node id at the center of the bounding box
        top_left = (int(center_x - square_size // 2), int(center_y - square_size // 2))
        bottom_right = (int(center_x + square_size // 2), int(center_y + square_size // 2))
        cv2.rectangle(image, top_left, bottom_right, color, -1)
        cv2.putText(
            image,
            f"{hash_to_id_map[node_hash]}",
            (center_x - 8, center_y + 8),
            font,
            0.8,
            (255, 255, 255),
            font_thickness,
            cv2.LINE_AA,
        )

        wrapped_text = textwrap.wrap(node.label, width=wrap_width)  # TODO: change mode.label to caption
        text_height = cv2.getTextSize("Tg", font, font_scale, font_thickness)[0][1]

        # Calculate the box position based on the bounding box location
        box_width = max([cv2.getTextSize(line, font, font_scale, font_thickness)[0][0] for line in wrapped_text]) + 10
        box_height = len(wrapped_text) * (text_height + 5) + 10

        img_height, img_width, _ = image.shape
        if center_x < img_width // 2:  # Bounding box on the left side
            text_x = bbox[0] - box_width - 10 if bbox[0] > box_width + 10 else bbox[2] + 10
        else:  # Bounding box on the right side
            text_x = bbox[2] + 10 if bbox[2] + box_width + 10 < img_width else bbox[0] - box_width - 10

        if bbox[1] > box_height + 10:
            text_y = bbox[1] - box_height - 5
        else:
            text_y = bbox[3] + 5
        text_y += 100

        for i, line in enumerate(wrapped_text):
            cv2.putText(
                image,
                line,
                (int(text_x + 5), int(text_y + (i + 1) * (text_height + 5))),
                font,
                font_scale,
                color,
                font_thickness,
                cv2.LINE_AA,
            )

    # Draw edges
    for node_hash, node in scene_graph.nodes.items():
        # restrict the number of edges to be drawn to 5

        for edge_type in node.edges:
            count = 0
            for neighbor_hash, edge in node.edges[edge_type].items():

                # prune edges by skipping some trivial relations
                relation = edge["relation"]
                if relation == "supported by" or not relation:
                    continue

                source_bbox = node.bbox_2d
                target_bbox = edge["node"].bbox_2d

                source_center = (
                    int((source_bbox[0] + source_bbox[2]) // 2),
                    int((source_bbox[1] + source_bbox[3]) // 2),
                )
                target_center = (
                    int((target_bbox[0] + target_bbox[2]) // 2),
                    int((target_bbox[1] + target_bbox[3]) // 2),
                )

                # Draw arrowed line between the source and target
                cv2.arrowedLine(image, source_center, target_center, arrow_color, 2, tipLength=0.05)

                # Draw relation text near the middle of the line
                mid_point = ((source_center[0] + target_center[0]) // 2, (source_center[1] + target_center[1]) // 2)
                cv2.putText(image, relation, mid_point, font, font_scale, arrow_color, font_thickness, cv2.LINE_AA)
                count += 1

                if count >= 10:
                    break
    if filename:
        cv2.imwrite(filename, image)
        print(f"[IRC] Scene graph saved as {filename}")

    return image


class UnionFind:
    """
    Union-Find data structure with path compression and union by rank. Used for graph prunning.
    """

    def __init__(self, scene_graph):
        self.parent = {}
        self.rank = {}

        for node_hash in scene_graph.nodes:
            self.parent[node_hash] = node_hash
            self.rank[node_hash] = 0

    def find(self, u):
        if self.parent[u] != u:
            self.parent[u] = self.find(self.parent[u])  # Path compression
        return self.parent[u]

    def union(self, u, v):
        root_u = self.find(u)
        root_v = self.find(v)

        if root_u != root_v:
            # Union by rank
            if self.rank[root_u] > self.rank[root_v]:
                self.parent[root_v] = root_u
            elif self.rank[root_u] < self.rank[root_v]:
                self.parent[root_u] = root_v
            else:
                self.parent[root_v] = root_u
                self.rank[root_u] += 1


def kruskal_mst(scene_graph, prob=1, random_seed=0):
    """
    Implementation of Kruskal's algorithm to find the minimum spanning tree of the scene graph.

    scene_graph (SceneGraph): the scene graph object.
    prob (float): the probability of keeping an edge in the MST. Default is 1.
    random_seed (int): the random seed for reproducibility. Default is 0.
    """
    random.seed(random_seed)

    def collect_and_shuffle_edges(scene_graph):
        obj_obj_edges = []
        for node_hash, node in scene_graph.nodes.items():
            for neighbor_hash, edge in node.edges["obj-obj"].items():
                obj_obj_edges.append((node_hash, neighbor_hash, edge["relation"]))

        # shuffle edges
        random.shuffle(obj_obj_edges)
        return obj_obj_edges

    # Step 2: Initialize Union-Find structure
    uf = UnionFind(scene_graph)
    mst = {"obj-obj": defaultdict(list), "character-obj-spatial": defaultdict(list)}  # List to store the MST edges

    # Step 3: Kruskal's algorithm
    shuffled_obj_obj_edges = collect_and_shuffle_edges(scene_graph)
    for edge in shuffled_obj_obj_edges:
        source_node, target_node, relation = edge
        if uf.find(source_node) != uf.find(target_node):
            uf.union(source_node, target_node)
            mst["obj-obj"][source_node].append((target_node, relation))

    for node in scene_graph.feature_map["character"]:
        edges = scene_graph.nodes[node].edges["character-obj-spatial"]
        # only read half of the edges
        select_edges = random.sample(list(edges.items()), len(edges) // 2)
        for neighbor_hash, edge in select_edges:
            if random.random() < 0.5:
                mst["character-obj-spatial"][node].append((neighbor_hash, edge["relation"]))
            else:
                oppo_relation = scene_graph.nodes[neighbor_hash].edges["character-obj-spatial"][node]["relation"]
                mst["character-obj-spatial"][neighbor_hash].append((node, oppo_relation))

    if prob < 1:
        # randomly prune some edges at rate prob
        for edge_type in mst:
            for node_hash, edges in mst[edge_type].items():
                mst[edge_type][node_hash] = [edge for edge in edges if random.random() < prob]

    return mst
