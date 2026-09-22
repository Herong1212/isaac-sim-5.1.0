import os, asyncio

import numpy as np
from omni.syntheticdata.scripts import helpers
from pymongo import MongoClient
import omni.usd
import carb

from ..annotator_helper.annotator_data_processor import AnnotatorDataProcessor
from ..db.db import DB, MongoDB
from ..stage_data_process.data_postprocess import DataPostProcessor
from ..utils import Utils, get_annotate_semantic_label
from .spatial_compute import infer_spatial_relations
from ..object_caption.generate_object_caption import DB_NAME, COLLECTION_NAME, get_file_unique_identifier_async


OBJECTS_TO_SKIP = [
    "wall",
    "bracket",
    "pillar",
    "floor",
    "floor_decal",
    "ceiling",
    "sign",
    "barcode",
    "beam",
    "collision",
]


class PrimNode:
    """
    Each PrimNode represents a node in the scene graph. It contains information about the each prim.

    Attributes:
        caption (str): the caption of the object, usually a sentence describing the object.
        label (str): the semantic label of the object, usually 1-2 words categorizing the object.
        edges (dict): a dictionary of edges connecting this node to other nodes.
        prim_path (str): the path to the prim in the USD file.
        bbox_3d (Tuple): the 3D bounding box of the object at the local coordinate system, based on camera view.
        world_bbox_3d (Tuple): the 3D bounding box of the object in world space.
        centroid_3d (Tuple): the 3D centroid of the object.
        bbox_2d (Tuple): the 2D bounding box of the object.
        is_world (bool): whether the object is in world space.
        action (str): the action the object is performing.
        category (str): the category of the object. Options: "object", "character".
        children (List): a list of child nodes. The children means the nodes that are supported by this node.
        parent (PrimNode): the parent node. The parent means the node that supports this node.

    """

    def __init__(self, prim_path, category="object"):
        self.caption = None
        self.label = None
        self.edges = {"obj-obj": {}, "character-obj-spatial": {}}
        self.prim_path = prim_path
        self.label = None
        self.caption = None
        self.bbox_3d = None  # make it a Tuple
        self.world_bbox_3d = None
        self.centroid_3d = None  # make it a Tuple
        self.bbox_2d = None  # make it a Tuple
        self.is_world = False
        self.action = None

        self.category = category  # ["object", "character"]
        self.children = []  # for building a SupportTree
        self.parent = None

    def add_edge(self, neighbor, edge_type="obj-obj", relation=None):  # neighbor is a usd node
        """
        neighbor (PrimNode): the node to connect to this node.
        edge_type (str): the type of edge to add. options: "obj-obj", "character-obj"
        relation (str): the spatial relation between the two nodes. options: "left",
            "right", "front", "back", "above", "below", "inside", "outside", "touching", "far", "near"
        """
        if not self.centroid_3d or not neighbor.centroid_3d:
            raise ValueError("Node must have 3D centroid to create edge.")
        if hash(neighbor) not in self.edges[edge_type]:
            if not relation:
                relation = infer_spatial_relations(self, neighbor)
            self.edges[edge_type][hash(neighbor)] = {
                "node": neighbor,
                "relation": relation,
            }

    def add_child(self, child):
        """
        This is used for building a SupportTree

        child (PrimNode): child node
        """
        self.children.append(child)
        child.parent = self  # set parent node of the child

    def reset(self):
        """
        Removes edges and children from the node
        """
        self.edges = {"obj-obj": {}, "character-obj-spatial": {}}
        self.children = []

    def __repr__(self):
        return f"PrimNode(label={self.label}, caption={self.caption})"

    def __hash__(self):
        return hash(self.prim_path)


class ObjectInfoDictReader:
    """
    Dump object info dict to PrimNode

    Attributes:
        nodes (List): a list of PrimNode objects.
        world (bool): whether the objects are in world space.
        log_missing_object (str): the path to the log file for usd files missing object captions.
    """

    def __init__(self, world=False, log_missing_object=None):
        self.nodes = []
        self.world = world
        self.log_missing_object = log_missing_object
        self.db = None
        if os.getenv("MONGODB_URI") is None:
            raise Exception("MONGODB_URI is not set")
        try:
            # Connect to MongoDB
            mongodb_uri = os.getenv("MONGODB_URI")
            self.db: DB = MongoDB(mongodb_uri)
        except Exception as e:
            raise Exception(f"Error connecting to MongoDB: {e}")

    def get_nodes(self, obj_info_dict, caption_only=False, use_ai_label=False, threshold_num=50):
        """
        obj_info_dict (dict): a map storing object basic and spatial information.
        caption_only (bool): whether to skip nodes without caption stored in MongoDB.
        use_ai_label (bool): whether to use AI label instead of the label automatically generated by prim path basename.
        threshold_num (int): the number of nodes to keep based on the size of 2D bounding box (in reverse order).
        """
        results = []
        for prim_path, node_info in obj_info_dict.items():
            node = PrimNode(prim_path, category="object")
            usd_path = node_info.get_property_info_with_key("usd_path")
            query_caption, query_label = asyncio.run(
                self.get_object_caption_async(
                    usd_path,
                    prim_path,
                    node_info.get_property_info_with_key("caption"),
                )
            )
            node.caption = query_caption
            if node.caption is None and caption_only:  # skip nodes without caption
                continue
            node.label = node_info.label

            # skip some prefiltered objects
            if any(substring in node.label for substring in OBJECTS_TO_SKIP):
                continue
            if use_ai_label:
                node.label = query_label

            node.is_world = self.world

            if self.world:
                node.centroid_3d = tuple(
                    node_info.get_property_info_with_key("bbox_info")["transform"][-1][:3].tolist()
                )
                node.bbox_3d = node.world_bbox_3d
                node.world_bbox_3d = tuple(
                    node_info.get_property_info_with_key("bbox_info")["vertex"]["translations_3d"].tolist()
                )
            else:
                node.bbox_2d = node_info.get_property_info_with_key("2d_bbox_info")
                bbox_3d_info = tuple(
                    node_info.get_property_info_with_key("bbox_info")["vertex"]["view_translations_3d"]
                )
                centroid_3d_info = node_info.get_property_info_with_key("bbox_info")["view_transform"][-1][:3]
                node.centroid_3d = (-centroid_3d_info[1], centroid_3d_info[0], centroid_3d_info[2])

                # switch (x,y,z) to (-y,x,z) for 3D bbox
                node.bbox_3d = tuple([[-coord[1], coord[0], coord[2]] for coord in bbox_3d_info])
                node.world_bbox_3d = tuple(
                    node_info.get_property_info_with_key("world_bbox_info")["vertex"]["translations_3d"].tolist()
                )
                # node.world_bbox_3d = [[coord[2], coord[0], coord[1]] for coord in node.world_bbox_3d]  # only uncomment when testing IRO scene

            is_character = node_info.get_property_info_with_key("is_character")
            if is_character:
                node.category = "character"
            else:
                node.category = "object"

            results.append(node)

        self.nodes.extend(results)

        asyncio.run(self.post_process_object_info_async(threshold_num))

    async def get_object_caption_async(self, usd_path, prim_path, caption=None):
        """
        Get object caption from MongoDB.

        usd_path (str): the path to the USD file.
        """
        # first query by usd name
        # if return None, decide whether to generate caption for the missing one
        # if return one result, return the caption
        # if return multiple results, further query by the usd file hash id
        if usd_path is None or usd_path == "None":
            print("[Warning] No USD path provided. Skipping upload to database.")
            return None, None

        # Get the prim from the stage
        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath(prim_path)
        if not prim:
            carb.log_info(f"Caption not found for {usd_path}")
            return None, None

        semantic_label = Utils.get_prim_semantic_label(prim)
        if os.getenv("MONGODB_URI") == "placeholder":
            if caption is None or semantic_label is None:
                usd_name = os.path.basename(usd_path)
                usd_name_lower = usd_name.lower()
                if not any(substring in usd_name_lower for substring in OBJECTS_TO_SKIP):
                    print(f"[Warning] Object caption for {usd_path} not found in MongoDB.")
                    # temporarily shut down printout warnings
                    if self.log_missing_object:
                        with open(self.log_missing_object, "a") as f:
                            f.write(f"{usd_path}\n")
                return None, None
            else:
                return caption, semantic_label

        usd_name = os.path.basename(usd_path)
        query = {"usd_name": usd_name}
        result = list(self.db.find(query))

        if len(result) == 1:
            return result[0]["caption"], result[0]["semantic_label"]

        elif len(result) == 0 or len(result) > 1:
            sha256_hash = await get_file_unique_identifier_async(usd_path)
            no_caption = False
            if sha256_hash:
                query = {"usd_sha256": sha256_hash}
                hash_result = list(self.db.find(query))
                if len(hash_result) == 0:
                    no_caption = True
            else:
                no_caption = True

            if no_caption:
                usd_name_lower = usd_name.lower()
                if not any(substring in usd_name_lower for substring in OBJECTS_TO_SKIP):
                    print(f"[Warning] Object caption for {usd_path} not found in MongoDB.")
                    # temporarily shut down printout warnings
                    if self.log_missing_object:
                        with open(self.log_missing_object, "a") as f:
                            f.write(f"{usd_path}\n")
                return None, None
            elif len(hash_result) == 1:
                return hash_result[0]["caption"], hash_result[0]["semantic_label"]
            else:
                raise ValueError(f"Multiple captions found for {usd_path}.")

    async def post_process_object_info_async(self, threshold_num=50):
        """Filter nodes by the size of 2D bounding box

        threshold_num (int): the number of nodes to keep based on the size of 2D bounding box (in reverse order).
        """
        elements = []

        # iterate through nodes and get the object with largest bounding box
        for idx, node in enumerate(self.nodes):
            bbox_2d = node.bbox_2d

            if bbox_2d is None:
                bbox_3d = node.world_bbox_3d
                area_or_volume = self.__calculate_box_3d_volume(bbox_3d)
            else:
                area_or_volume = self.__calculate_box_2d_area(bbox_2d)
            elements.append((idx, area_or_volume))

        # sort the 2d bounding box size
        elements.sort(key=lambda x: x[1], reverse=True)
        filtered_nodes = []
        for idx, _ in elements[:threshold_num]:
            filtered_nodes.append(self.nodes[idx])

        self.nodes = filtered_nodes

    def __calculate_box_2d_area(self, bbox_2d):
        return (bbox_2d[2] - bbox_2d[0]) * (bbox_2d[3] - bbox_2d[1])

    def __calculate_box_3d_volume(self, bbox_3d):
        i_coord = []
        for index in range(3):
            i_coord.append(min([point[index] for point in bbox_3d]))
            i_coord.append(max([point[index] for point in bbox_3d]))

        x_min, x_max, y_min, y_max, z_min, z_max = i_coord
        volume = (x_max - x_min) * (y_max - y_min) * (z_max - z_min)
        return volume


class IRAWriterInfoDictReader(ObjectInfoDictReader):
    """
    Dump Isaacsim.replicator.agent.core object info dict to PrimNode.
    """

    def __init__(self, world=False, log_missing_object=None):
        super().__init__(world, log_missing_object)

    def get_nodes(self, obj_info_dict, caption_only=False, use_ai_label=False, threshold_num=100):
        """
        Get nodes from Isaacsim.replicator.agent.core info dict.

        obj_info_dict (dict): a map storing object basic and spatial information.
        caption_only (bool): whether to skip nodes without caption stored in MongoDB.
        use_ai_label (bool): whether to use AI label instead of the label automatically generated by prim path basename.
        threshold_num (int): the number of nodes to keep based on the size of 2D bounding box (in reverse order).
        """
        results = []
        for cat in ["agents", "objects"]:
            for dict_info in obj_info_dict[cat]:
                if cat == "agents":
                    category = "character"
                elif cat == "objects":
                    category = "object"
                node = PrimNode(dict_info["prim_path"], category=category)

                node.label = dict_info["label"]["class"]
                node.category = category

                # skip some prefiltered objects
                if node.label in OBJECTS_TO_SKIP:
                    continue
                query_caption, query_label = asyncio.run(self.get_object_caption_async(dict_info["usd_path"], dict_info["prim_path"]))
                node.caption = query_caption
                if node.caption is None and caption_only:  # skip nodes without caption
                    continue
                if use_ai_label:
                    node.label = query_label

                bbox_3d_info = dict_info["annotators"]["bounding_box_3d_fast"]["vertex"]["translations_3d"].tolist()[
                    0
                ]  # TODO: check if this is correct
                node.world_bbox_3d = tuple([coord for coord in bbox_3d_info])

                local_bbox_3d = dict_info["annotators"]["bounding_box_3d_fast"]["vertex"][
                    "camera_view_translations_3d"
                ].tolist()[0]
                local_bbox_3d = [[-coord[1], coord[0], coord[2]] for coord in local_bbox_3d]
                node.bbox_3d = tuple([coord for coord in local_bbox_3d])

                centroid_3d_info = dict_info["annotators"]["bounding_box_3d_fast"]["camera_view_transform"][-1].tolist()
                node.centroid_3d = (
                    -centroid_3d_info[1],
                    centroid_3d_info[0],
                    centroid_3d_info[2],
                )  # TODO: check if this is correct

                try:
                    bounding_box_2d_tight = dict_info["annotators"]["bounding_box_2d_tight_fast"]
                except KeyError:
                    # no 2d bounding box detected
                    continue
                node.bbox_2d = [
                    bounding_box_2d_tight["x_min"],
                    bounding_box_2d_tight["y_min"],
                    bounding_box_2d_tight["x_max"],
                    bounding_box_2d_tight["y_max"],
                ]
                node.is_world = self.world
                results.append(node)

        self.nodes.extend(results)

        asyncio.run(self.post_process_object_info_async(threshold_num))


class IROWriterInfoDictReader(ObjectInfoDictReader):
    """
    Dump Isaacsim.replicator.object info dict to Node/
    """

    def __init__(self, world=False, log_missing_object=None):
        """
        obj_info_dict (dict): IRO exported info.
        {
            "bbox_2d_unfiltered": bounding_box_2d_tight_fast,
            "bbox_3d_unfiltered": bounding_box_3d_fast,
        }
        Direct output from Annotator
        """
        super().__init__(world, log_missing_object)

    def get_nodes(self, obj_info_dict, caption_only=False, use_ai_label=False, threshold_num=100):
        """
        Get nodes from Isaacsim.replicator.object info dict.

        obj_info_dict (dict): a map storing object basic and spatial information.
        caption_only (bool): whether to skip nodes without caption stored in MongoDB.
        use_ai_label (bool): whether to use AI label instead of the label automatically generated by prim path basename.
        threshold_num (int): the number of nodes to keep based on the size of 2D bounding box (in reverse order).
        """
        bbox_2d = obj_info_dict["bbox_2d_unfiltered"]
        bbox_3d = obj_info_dict["bbox_3d_unfiltered"]
        view_params = AnnotatorDataProcessor.reformat_camera_params(obj_info_dict["camera_params"])
        usd_paths = obj_info_dict["usd_paths"]  # TODO: add usd path to obj_info_dict in ORO

        for i, prim_path in enumerate(bbox_2d["info"]["primPaths"]):
            data = bbox_2d["data"][i]
            sem_label_dict = bbox_2d["info"]["idToLabels"][data["semanticId"]]
            label = get_annotate_semantic_label(sem_label_dict)
            if label in OBJECTS_TO_SKIP:
                continue
            usd_path = usd_paths[i]
            query_caption, query_label = asyncio.run(self.get_object_caption_async(usd_path, prim_path))
            if query_caption is None and caption_only:  # skip nodes without caption
                continue
            node = PrimNode(prim_path, category="object")
            node.caption = query_caption
            node.label = label
            if use_ai_label:
                node.label = query_label
            node.bbox_2d = [int(data["x_min"]), int(data["y_min"]), int(data["x_max"]), int(data["y_max"])]
            box_id = bbox_2d["info"]["bboxIds"][i]
            # find index of the same box_id in bbox_3d
            index = np.where(bbox_3d["info"]["bboxIds"] == box_id)[0]
            if len(index) == 0:
                # no 3d bbox found
                continue
            else:
                index = index.tolist()[0]
            data_3d = bbox_3d["data"][index]
            res = self._process_camera_params_3d(data_3d, view_params)
            node.bbox_3d = res["bbox_3d"]
            node.centroid_3d = res["centroid_3d"]

            node.world_bbox_3d = res["world_bbox_3d"]
            node.is_world = self.world

            self.nodes.append(node)
            asyncio.run(self.post_process_object_info_async(threshold_num))

    def _process_camera_params_3d(self, bbox_3d_data, view_params):
        res = {}

        corners = helpers.get_bbox_3d_corners(Utils.extent_dimension(bbox_3d_data))

        if corners.shape[1] != 8:
            # carb.log_info("corner vertex is not 8. discard the info")
            return False

        translations_2d = DataPostProcessor.world_to_image_helper(corners.reshape(-1, 3), view_params)
        res["translations_2d"] = translations_2d[:, :2].tolist()
        # update to (z, x, y) format - dropped after code migration
        res["world_bbox_3d"] = corners.tolist()[0]
        res["world_bbox_3d"] = [[coord[2], coord[0], coord[1]] for coord in res["world_bbox_3d"]]

        camera_view_matrix = view_params["world_to_view"]
        view_transform = Utils.convert_to_camera_space(bbox_3d_data["transform"], camera_view_matrix)
        translations_3d = np.concatenate([corners, np.ones((1, 8, 1))], axis=-1)
        camera_view_translations_3d = Utils.convert_to_camera_space(
            world_transform=translations_3d, camera_view_matrix=camera_view_matrix
        )
        bbox_3d = camera_view_translations_3d[:, :, :-1].tolist()[0]
        res["bbox_3d"] = [[-coord[1], coord[0], coord[2]] for coord in bbox_3d]  # not affecting other parts of the code
        centroid_3d = view_transform[-1, :3].tolist()
        res["centroid_3d"] = (-centroid_3d[1], centroid_3d[0], centroid_3d[2])

        return res


def attach_label_to_usd_func():
    """
    Attach semantic label to usd file with usd paths
    """
    stage = omni.usd.get_context().get_stage()
    print("Attaching semantic labels to USD file...")
    for prim in stage.Traverse():
        if prim.GetTypeName() != "Xform":
            continue
        prim_path = str(prim.GetPrimPath())

        usd_path = Utils.get_object_reference(prim_path, stage)
        if usd_path and usd_path.endswith(".usd"):
            usd_name = os.path.basename(usd_path).lower()
            if not any([obj in usd_name for obj in OBJECTS_TO_SKIP]):

                label_name = os.path.basename(usd_path).replace(".usd", "")
                Utils.enable_semantics(prim, label_name)
