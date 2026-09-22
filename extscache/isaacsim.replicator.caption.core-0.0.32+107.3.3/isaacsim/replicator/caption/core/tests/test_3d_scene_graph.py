import ast
import json
import os

import numpy as np
import omni.kit.test
from isaacsim.replicator.caption.core.three_dim_scene_graph.scene_graph import SceneGraph
from isaacsim.replicator.caption.core.three_dim_scene_graph.scene_node import PrimNode, ObjectInfoDictReader

# parent of current directory
parent_dir = os.path.dirname(os.path.abspath(__file__))


def read_list_from_file(file_path):

    # Read the content of the file
    with open(file_path, "r") as file:
        content = file.read()

    # Parse the content as a Python list
    try:
        data_list = ast.literal_eval(content)
    except (ValueError, SyntaxError):
        print("Error: The file does not contain a valid list.")

    # Now `data_list` holds the parsed list
    return data_list


class JsonObjectReader(ObjectInfoDictReader):
    """
    Read through objects in a stage
    """

    def __init__(self, world=False, log_missing_object=None):
        super().__init__(world, log_missing_object)

    async def get_nodes(self, stage_folder):
        stage_2d_folder = os.path.join(stage_folder, "bounding_box_2d_loose")
        stage_3d_folder = os.path.join(stage_folder, "bounding_box_3d")
        # read information from metadata and stage files
        coord_2d_loose = np.load(os.path.join(stage_2d_folder, "bounding_box_2d_loose_0003.npy"))
        # coord_3d_loose = np.load(os.path.join(self.stage_3d_folder, 'bounding_box_3d_loose_0003.npy'))
        coord_3d_loose = json.load(open(f"{parent_dir}/test_data/World_Cameras_Camera_04.json"))

        with open(os.path.join(stage_2d_folder, f"bounding_box_2d_loose_labels_0003.json")) as f:
            label_info_2d = json.load(f)
        with open(os.path.join(stage_3d_folder, f"bounding_box_3d_labels_0003.json")) as f:
            label_info_3d = json.load(f)

        assets_info_2d = read_list_from_file(
            os.path.join(stage_2d_folder, f"bounding_box_2d_loose_prim_paths_0003.json")
        )
        assets_info_3d = read_list_from_file(os.path.join(stage_3d_folder, f"bounding_box_3d_prim_paths_0003.json"))

        for i, asset in enumerate(assets_info_2d):
            node = PrimNode(asset)
            node.label = label_info_2d[str(i)]["class"]
            node.bbox_2d = coord_2d_loose[i].tolist()[1:5]
            node.bbox_3d = tuple([box[:3] for box in coord_3d_loose[i]["bounding_box_metadata"]["keypoints_3d"][1:]])
            node.world_bbox_3d = tuple(
                [box[:3] for box in coord_3d_loose[i]["bounding_box_metadata"]["keypoints_3d"][1:]]
            )
            node.centroid_3d = tuple(coord_3d_loose[i]["bounding_box_metadata"]["position"][:3])
            node.is_world = self.world
            # node.caption = await self.get_object_caption_async(asset)

            self.nodes.append(node)


class JsonCharacterReader(JsonObjectReader):
    def __init__(self, world=False):
        super().__init__(world)

        self.nodes = []
        self.world = world

    async def get_nodes(self, stage_folder):
        # read information from metadata and stage files

        info = json.load(open(os.path.join(stage_folder, "object_detection/1038.json")))

        for asset in info["characters"]:
            usd_path = None
            node = PrimNode(usd_path, category="character")
            node.label = asset["label"]
            bbox_2d = asset["2d_bounding_box"]
            node.bbox_2d = [bbox_2d[1], bbox_2d[3], bbox_2d[0], bbox_2d[2]]
            node.bbox_3d = tuple([box[:3] for box in asset["3d_bounding_box"]["3d_vertex"][1:]])
            node.world_bbox_3d = node.bbox_3d
            node.centroid_3d = tuple(asset["3d_bounding_box"]["location"][:3])
            node.is_world = self.world
            node.action = asset["action_tag"]
            node.prim_path = asset["label"]  # no prim path, use label as prim path
            # node.caption = await self.get_object_caption_async("random_name")

            self.nodes.append(node)


class TestPrimNode(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    # Actual test, notice it is "async" function, so "await" can be used if needed
    async def test_node_format(self):
        # Read the objects in the stage
        stage_folder = f"{parent_dir}/test_data/Test_Scene_Data_Camera_00"
        object_json_reader = JsonObjectReader()
        await object_json_reader.get_nodes(stage_folder)
        nodes = object_json_reader.nodes
        assert len(nodes) == 10

        # check node attributes
        node = nodes[0]
        assert node.category == "object"

        assert len(node.bbox_2d) == 4
        assert len(node.bbox_3d) == 8
        assert len(node.centroid_3d) == 3
        assert node.caption is None

    async def test_character_format(self):
        character_stage_folder = f"{parent_dir}/test_data/Test_Hospital_Human_World_Camera_00"
        character_json_reader = JsonCharacterReader()
        await character_json_reader.get_nodes(character_stage_folder)
        nodes = character_json_reader.nodes
        assert len(nodes) == 2
        node = nodes[0]
        assert node.category == "character"
        assert len(node.bbox_2d) == 4
        assert len(node.bbox_3d) == 8
        assert len(node.centroid_3d) == 3
        assert node.caption is None


class TestSceneGraph(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        caption_configs = {
            "verbose": True,
            "export_edges": True,
            "export_world": True,
            "pruning_ratio": 1.0,
            "random_seed": 0,
        }
        scene_graph = SceneGraph(caption_configs)

        character_stage_folder = f"{parent_dir}/test_data/Test_Hospital_Human_World_Camera_00"
        character_json_reader = JsonCharacterReader()

        stage_folder = f"{parent_dir}/test_data/Test_Scene_Data_Camera_00"
        object_json_reader = JsonObjectReader()

        await object_json_reader.get_nodes(stage_folder)
        await character_json_reader.get_nodes(character_stage_folder)

        self.object_json_reader = object_json_reader
        self.character_json_reader = character_json_reader

        self.scene_graph = scene_graph

    async def tearDown(self):
        pass

    # Actual test, notice it is "async" function, so "await" can be used if needed
    async def test_scene_graph_build(self):

        scene_graph = self.scene_graph
        for node in self.object_json_reader.nodes:
            scene_graph.add_node(node)
        for node in self.character_json_reader.nodes:
            scene_graph.add_node(node)

        assert len(scene_graph.feature_map["object"]) == 10
        assert len(scene_graph.feature_map["character"]) == 2
        assert scene_graph.index_count == 12

        scene_graph.build_graph()
        assert len(scene_graph.nodes) == 12
        assert scene_graph.get_edges_number() == 48

        for character in scene_graph.feature_map["character"]:
            node = scene_graph.nodes[character]
            if node.label == "doctor":
                assert len(node.edges["character-obj-spatial"]) == 5
            elif node.label == "patient":
                assert len(node.edges["character-obj-spatial"]) == 5

        scene_graph.prune()
        assert len(scene_graph.nodes) == 12
        assert scene_graph.get_edges_number() < 13

    async def test_support_tree(self):
        self.scene_graph.clear()
        scene_graph = self.scene_graph
        for node in self.object_json_reader.nodes:
            scene_graph.add_node(node)

        # build graph tree
        support_tree = scene_graph._build_support_tree()

        assert len(support_tree.get_nodes_at_level(0)) == 1
        assert len(support_tree.get_nodes_at_level(1)) == 5
        assert len(support_tree.get_nodes_at_level(2)) == 4

    async def test_export_scene_graph(self):
        self.scene_graph.clear()
        scene_graph = self.scene_graph
        for node in self.object_json_reader.nodes:
            scene_graph.add_node(node)
        for node in self.character_json_reader.nodes:
            scene_graph.add_node(node)

        scene_graph.build_graph()

        export_dict = await scene_graph.export_graph()

        assert len(export_dict["obj"]) == 10
        assert len(export_dict["character"]) == 2
        assert len(export_dict["edges"]) == 2
        assert len(export_dict["edges"]["character-obj-spatial"]) == 20  # (5+5) * 2
        assert len(export_dict["edges"]["obj-obj"]) == 28  # 5 * 4 + 4 * 2 (supports)

    async def test_spatial_relation(self):

        self.scene_graph.clear()
        scene_graph = self.scene_graph
        for node in self.object_json_reader.nodes:
            scene_graph.add_node(node)

        scene_graph.build_graph()

        # randomly check several spatial relations
        for node_hash in scene_graph.nodes:
            node = scene_graph.nodes[node_hash]
            if node.label == "hospital_chair":
                for edge in node.edges["obj-obj"]:
                    neighbor = scene_graph.nodes[edge]
                    if neighbor.label == "hospital_bed":
                        assert "left" in node.edges["obj-obj"][edge]["relation"]

                    elif neighbor.label == "hospital_table":
                        assert "behind" in node.edges["obj-obj"][edge]["relation"]

            if node.label == "hospital_desk":
                for edge in node.edges["obj-obj"]:
                    neighbor = scene_graph.nodes[edge]
                    if neighbor.label == "bookset":
                        assert node.edges["obj-obj"][edge]["relation"] == "supports"
                    if neighbor.label == "hospital_chair":
                        assert "right" in node.edges["obj-obj"][edge]["relation"]
                        assert "front" in node.edges["obj-obj"][edge]["relation"]
