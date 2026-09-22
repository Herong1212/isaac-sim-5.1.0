# in-contact vertical: supported by; embedded into, placed in, inside
# non-contact vertical: hanging on, affixed on, mounted on, above, higher than, below, lower than
# horizontal: near (far) to the left (right) of, is behind, is in front of, close to, adjacent to, besides, next to
# multi-object: aligned, between
# Only part of the spatial relationships are implemented.
# Please refer to Scene Verse (https://arxiv.org/pdf/2401.09340) A.2. 3D Scene Graph Construction for more details.
def less_than_with_margin(a, b, margin):
    """
    Whether a is less than b with a small margin
    """
    return a <= b + margin


# i supported by j: abs(i_zmin - j_zmax) < 0.05, and i is within j on x and y axis with a small margin
def vertical_support(i_coord, j_coord):
    """
    Whether i is supported by j

    i_coord (list): [i_xmin, i_xmax, i_ymin, i_ymax, i_zmin, i_zmax]
    j_coord (list): [j_xmin, j_xmax, j_ymin, j_ymax, j_zmin, j_zmax]
    """
    i_xmin, i_xmax, i_ymin, i_ymax, i_zmin, i_zmax = i_coord
    j_xmin, j_xmax, j_ymin, j_ymax, j_zmin, j_zmax = j_coord
    i_margin = 0.05 * max((i_xmax - i_xmin), (j_xmax - j_xmin))
    j_margin = 0.05 * max((i_ymax - i_ymin), (j_ymax - j_ymin))
    scale1 = i_zmax - i_zmin
    scale2 = j_zmax - j_zmin
    margin1 = 0.05 * scale1
    margin2 = 0.05 * scale2
    max_margin = max(margin1, margin2)
    abs_z_diff = abs(i_zmin - j_zmax)
    range_flag1 = (
        less_than_with_margin(j_xmin, i_xmin, i_margin)
        and less_than_with_margin(i_xmax, j_xmax, i_margin)
        and less_than_with_margin(j_ymin, i_ymin, i_margin)
        and less_than_with_margin(i_ymax, j_ymax, i_margin)
    )

    range_flag2 = (
        less_than_with_margin(j_xmin, i_xmin, j_margin)
        and less_than_with_margin(i_xmax, j_xmax, j_margin)
        and less_than_with_margin(j_ymin, i_ymin, j_margin)
        and less_than_with_margin(i_ymax, j_ymax, j_margin)
    )

    range_flag = range_flag1 or range_flag2

    if (
        abs_z_diff / max(scale1, scale2) < 0.05 and range_flag
    ):  # improve tolerance to resolve object contactness issue temporarily
        return True

    # another situation: i is inside j
    # method: check all 8 corners of i, if all corners are inside j, then i is inside j
    # for example: boxes on a large shelf can be seen as the shelf supports the boxes
    inside_flag = (
        less_than_with_margin(j_xmin, i_xmin, max_margin)
        and less_than_with_margin(i_xmax, j_xmax, max_margin)
        and less_than_with_margin(j_ymin, i_ymin, max_margin)
        and less_than_with_margin(i_ymax, j_ymax, max_margin)
        and less_than_with_margin(j_zmin, i_zmin, max_margin)
        and less_than_with_margin(i_zmax, j_zmax, max_margin)
    )

    if inside_flag:
        return True

    return False


def vertical_i_supports_j_node(i_node, j_node):
    """
    Whether i supports j

    i_node (PrimNode): a node in the scene graph
    j_node (PrimNode): a node different from i_node in the scene graph
    """
    i_coord = get_node_coord(i_node, world=True)
    j_coord = get_node_coord(j_node, world=True)
    return vertical_support(j_coord, i_coord)


def horizontal_relations(i_coord, j_coord):
    """
    Get the spatial relationship description between two nodes on the same hierarchy on SupportTree.

    i_coord (list): The 3d bounding box of node i. [i_xmin, i_xmax, i_ymin, i_ymax, i_zmin, i_zmax]
    j_coord (list): The 3d bounding box of node j. [j_xmin, j_xmax, j_ymin, j_ymax, j_zmin, j_zmax]
    """
    i_xmin, i_xmax, i_ymin, i_ymax, i_zmin, i_zmax = i_coord
    j_xmin, j_xmax, j_ymin, j_ymax, j_zmin, j_zmax = j_coord
    relations = []
    if less_than_with_margin(i_ymax, j_ymin, 0.05):
        relations.append("left")
    if less_than_with_margin(j_ymax, i_ymin, 0.05):
        relations.append("right")
    if less_than_with_margin(i_xmax, j_xmin, 0.05):
        relations.append("behind")
    if less_than_with_margin(j_xmax, i_xmin, 0.05):
        relations.append("front")
    return relations


def horizontal_distance_relative(i_centroid, j_centroid, scale):
    """
    Get the relative distance between two nodes on the same hierarchy on SupportTree.

    i_centroid (list): The centroid coordinate of node i. [i_x, i_y, i_z]
    j_centroid (list): The centroid coordinate of node j. [j_x, j_y, j_z]
    scale (float): the scale of the scene
    """
    i_x, i_y, i_z = i_centroid
    j_x, j_y, j_z = j_centroid
    distance = ((i_x - j_x) ** 2 + (i_y - j_y) ** 2) ** 0.5
    relative_distance = distance / scale
    return relative_distance


def create_edge_same_hierarchy(i_coord, j_coord, i_centroid, j_centroid, near_thread=1, far_thread=4):
    """
    Get the spatial relationship description between two nodes on the same hierarchy on SupportTree.

    i_coord (list): The 3d bounding box of node i. [i_xmin, i_xmax, i_ymin, i_ymax, i_zmin, i_zmax]
    j_coord (list): The 3d bounding box of node j. [j_xmin, j_xmax, j_ymin, j_ymax, j_zmin, j_zmax]
    i_centroid (list): The centroid coordinate of node i. [i_x, i_y, i_z]
    j_centroid (list): The centroid coordinate of node j. [j_x, j_y, j_z]
    near_thread (float): the threshold of near distance
    far_thread (float): the threshold of far distance
    """
    relations = horizontal_relations(i_coord, j_coord)
    scale_i = ((i_coord[1] - i_coord[0]) ** 2 + (i_coord[3] - i_coord[2]) ** 2 + (i_coord[5] - i_coord[4]) ** 2) ** 0.5
    scale_j = ((j_coord[1] - j_coord[0]) ** 2 + (j_coord[3] - j_coord[2]) ** 2 + (j_coord[5] - j_coord[4]) ** 2) ** 0.5
    scale = max(scale_i, scale_j)
    distance = horizontal_distance_relative(i_centroid, j_centroid, scale)
    if distance < near_thread:
        relations.append("near")
    elif distance > far_thread:
        relations.append("far")
    return relations


def get_node_coord(node, world=True):
    """
    node(PrimNode): a node in the scene graph.
    world(bool): whether to use world_bbox_3d or bbox_3d to get the coordinate of the node. Default is True.
    """
    i_coord = []
    for index in range(3):
        if world:
            i_coord.append(min([point[index] for point in node.world_bbox_3d]))
            i_coord.append(max([point[index] for point in node.world_bbox_3d]))
        else:
            i_coord.append(min([point[index] for point in node.bbox_3d]))
            i_coord.append(max([point[index] for point in node.bbox_3d]))
    return i_coord


def infer_spatial_relations(node1, node2):
    """
    Get spatial relationship description between two nodes

    node1 (PrimNode): a node in the scene graph
    node2 (PrimNode): a node different from node1 in the scene graph
    """
    i_coord = get_node_coord(node1)
    j_coord = get_node_coord(node2)
    if vertical_support(i_coord, j_coord):
        return "supported by"
    else:
        i_centroid = node1.centroid_3d
        j_centroid = node2.centroid_3d
        relations = create_edge_same_hierarchy(i_coord, j_coord, i_centroid, j_centroid)
        return ",".join(relations)


def get_opposite_spatial_relations(relation):
    """
    Get the opposite spatial relationship description.

    relation (str): a spatial relationship description by a string, separated by comma, e.g., "left,behind"
    """
    relations = relation.split(",")

    def get_opposite_spatial_word(relation):
        if relation == "left":
            return "right"
        elif relation == "right":
            return "left"
        elif relation == "behind":
            return "front"
        elif relation == "front":
            return "behind"
        elif relation == "near":
            return "near"
        elif relation == "far":
            return "far"
        elif relation == "supported by":
            return "supports"
        elif relation == "supports":
            return "supported by"
        else:
            return None

    for i in range(len(relations)):
        relations[i] = get_opposite_spatial_word(relations[i])

    return ",".join(relations)
