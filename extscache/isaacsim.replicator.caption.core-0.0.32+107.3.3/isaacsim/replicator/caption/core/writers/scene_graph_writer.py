import os
import asyncio
import random

import cv2
import numpy as np
import omni.usd

from omni.replicator.core import WriterRegistry
from omni.replicator.core.scripts import functional as F
from omni.replicator.core.scripts.writers_default.tools import *

from .annotator_data_processor import AnnotatorDataProcessor

from .ira_basic_writer import IRABasicWriter
from .writer_utils import WriterUtils
from .object_info_manager import ObjectInfo
from ..three_dim_scene_graph.scene_graph import SceneGraph
from ..three_dim_scene_graph.scene_node import IRAWriterInfoDictReader, attach_label_to_usd_func
from ..utils import Utils
from ..sft_autolabeling.scene_graph_sft import GenSceneCap
from ..settings import ReplicatorCaptionSettings


__copyright__ = "Copyright (c) 2021, NVIDIA CORPORATION. All rights reserved."
__license__ = """
NVIDIA CORPORATION and its licensors retain all intellectual property
and proprietary rights in and to this software, related documentation
and any modifications thereto. Any use, reproduction, disclosure or
distribution of this software and related documentation without an express
license agreement from NVIDIA CORPORATION is strictly prohibited.
"""

# Generate scene graph based on annotator captured information. The algorithm is
# a modified version of https://arxiv.org/pdf/2406.01584

random.seed(0)

DEFAULT_CAPTION_CONFIG = {
    "save_full_scene_graph": True,
    "save_pruned_scene_graph": True,
    "attach_label_to_usd": False,
    "use_ai_label": False,
    "visualize_caption": True,
    "max_object_capacity": 100,
    "export_edges": True,
    "global_caption": False,
    "qa_caption": False,
    "brief_caption": False,
    "pruning_ratio": 1.0,
    "verbose": True,
    "random_seed": 0,
    "caption_only": True,
    "export_world": True,
}


class SceneGraphWriter(IRABasicWriter):
    """Writer outputting data in the Json format
        Development work to provide full support is ongoing.

    PostProcessed Annotations:
        bounding_box_2d_tight, bounding_box_3d, centroids 3d, scene graph

    Notes:
        Scene Graph:
            Nodes represent prim objects; edges represent spatial relationship

    Attributes:
        caption_interval (int): the interval of generating caption. Default is 1000.
        caption_config (dict): the configuration of caption generation. Default is None.
        scene_graph_interval (int): the interval of generating scene graph. Default is 1.
        export_point_cloud (bool): whether to export point cloud. Default is False.
        export_depth (bool): whether to export depth. Default is False.
        skip_frames (int): the number of frames to skip. Default is 0.
        writer_interval (int): the interval of writing the images and annotations. Default is 1.
        output_dir (str): the output directory. Default is the cache folder path.
    """

    def __init__(
        self,
        caption_interval: int = 1000,
        scene_graph_interval: int = 1,
        caption_config: dict = DEFAULT_CAPTION_CONFIG,
        export_point_cloud: bool = False,
        export_depth: bool = False,
        skip_frames: int = 0,
        writer_interval: int = 1,
        output_dir: str = ReplicatorCaptionSettings.get_cache_folder_path(),
        *args,  # Additional positional arguments for the parent class
        **kwargs,  # Additional keyword arguments for the parent class
    ):
        """Create a Scene Graph Writer"""

        # Call the parent constructor to handle parent class parameters
        filtered_kwargs = kwargs

        # if user want to output object's bounding box information
        # template parameters to test object info output

        # overwrite some of the default settings
        read_configs = DEFAULT_CAPTION_CONFIG
        read_configs.update(caption_config)

        filtered_kwargs["pointcloud"] = export_point_cloud
        filtered_kwargs["distance_to_image_plane"] = export_depth
        filtered_kwargs["object_info_centroids_3d"] = True
        filtered_kwargs["output_dir"] = output_dir

        filtered_kwargs["semantic_filter_predicate"] = None  # suppress the semantic filter
        filtered_kwargs["camera_params"] = True
        filtered_kwargs["rgb"] = True
        filtered_kwargs["object_info_bounding_box_2d_tight"] = True
        filtered_kwargs["object_info_bounding_box_3d"] = True

        super().__init__(*args, **kwargs)

        # # skip first several frame
        # self.skip_frames = carb.settings.get_settings().get(
        #     "/persistent/exts/isaacsim.replicator.agent/skip_starting_frames"
        # )
        # # frame interval of writing new annotators.
        # self.writer_interval = carb.settings.get_settings().get(
        #     "/persistent/exts/isaacsim.replicator.agent/frame_write_interval"
        # )
        self.skip_frames = skip_frames
        self.writer_interval = writer_interval

        # Track numbering of the next frame to be written.
        self._frame_counter = 0
        self.output_objects = True
        self.caption_interval = caption_interval
        self.scene_graph_interval = scene_graph_interval
        self.caption_config = read_configs

        self.export_depth = export_depth
        self.export_point_cloud = export_point_cloud

        self.attach_label_to_usd = self.caption_config["attach_label_to_usd"]

        if self.attach_label_to_usd:
            attach_label_to_usd_func()

    @classmethod
    def params_values(cls):
        param_value_dict = {}
        # Gather child class parameters
        if cls != SceneGraphWriter:
            param_value_dict.update(WriterUtils.inspect_writer_init(cls))
        # Gather self parameters
        param_value_dict.update(WriterUtils.inspect_writer_init(SceneGraphWriter))
        # Gather BasicWriter parameters
        param_value_dict.update(IRABasicWriter.basic_params_values())
        return param_value_dict

    @classmethod
    def params_labels(cls):
        # Params to be display in the UI and their display labels
        return {
            "output_dir": "output_dir",
            "caption_interval": "caption_interval",
            "scene_graph_interval": "scene_graph_interval",
            "caption_config": "caption_config",
            "export_point_cloud": "export_point_cloud",
            "export_depth": "export_depth",
            "skip_frames": "skip_frames",
            "writer_interval": "writer_interval",
        }

    @classmethod
    def tooltip(cls):
        return f"""
            SceneGraphWriter
            - Generates captions of rgb images, scene graph and visualized scene graphs from cameras.
        """

    def object_detection_enabled(self):
        """check whether user want to output object detection data"""
        return True  # TODO: add a switch based on some settings

    def _write_sensor_data(self, annotator_dict: dict):
        """write annotator data related to single sensor"""
        camera_path = annotator_dict["camera"]
        # get current activated annotator list:
        all_annotators = annotator_dict.keys()
        # get all customized annotator list:
        customized_annotator_set = self.get_customized_annotators()
        # get default annotators:
        default_annotators = [
            item
            for item in all_annotators
            if not any(str(item).startswith(prefix) for prefix in customized_annotator_set)
        ]

        camera_id = str(camera_path).replace("/", "_")

        for annotator_name in default_annotators:

            output_path = os.path.join(camera_id, annotator_name) + os.path.sep
            annotator_data = annotator_dict[annotator_name]

            for annotator_type, output_function_name in self.annotator_to_function_dict.items():
                if str(annotator_name).startswith(annotator_type):
                    # check whether the output function has been implemented
                    if hasattr(self, output_function_name):
                        default_output_function = getattr(self, output_function_name)
                        default_output_function(annotator_data, output_path)

                    break
        # whether user want to write object detection
        if self.object_detection_enabled():
            # collected all information included by this camera into a json file.
            self.write_object_detection(
                camera_path=camera_path, sub_dir=camera_id, rgb_data=annotator_dict["rgb"]
            )  # add rgb data to the output

            # add pointcloud and depth data to the output

        self.customized_post_process(annotator_dict=annotator_dict, sub_dir=camera_id)

    def write_object_detection(self, camera_path: str, sub_dir: str, rgb_data: np.ndarray):
        """Add filters to check agent info's visibility

        camera_path (str): the camera prim path
        sub_dir (str): the sub directory to save the output
        rgb_data (np.ndarray): the rgb data captured by the camera
        """
        info_dict = {"agents": [], "objects": []}
        # fetch object detection info base on
        object_detection_info = self.object_info_manager.get_camera_view_info(camera_path)

        if object_detection_info:
            # Collect agent information if available:
            agent_info_dict = object_detection_info.get_agent_info_dict()
            # collect camera information
            camera_params = object_detection_info.get_camera_params()
            stage = omni.usd.get_context().get_stage()
            if agent_info_dict:
                for prim_path, agent_info in agent_info_dict.items():
                    # check whether agent is valid
                    if not self.is_valid_info(agent_info, camera_params):
                        continue
                    self.postprocess_object_detection_annotator(object_info=agent_info, camera_params=camera_params)
                    sub_dict = agent_info.get_all_info()
                    sub_dict["prim_path"] = prim_path
                    _, sub_dict["usd_path"] = Utils.capture_usd_info(prim_path=prim_path, stage=stage, verbose=True)
                    info_dict["agents"].append(sub_dict)

            if self.output_objects:
                object_info_dict = object_detection_info.get_object_info_dict()
                for prim_path, object_info in object_info_dict.items():
                    # check whether object is valid
                    if not self.is_valid_info(object_info, camera_params):
                        continue
                    self.postprocess_object_detection_annotator(object_info=object_info, camera_params=camera_params)
                    sub_dict = object_info.get_all_info()
                    sub_dict["prim_path"] = prim_path
                    _, sub_dict["usd_path"] = Utils.capture_usd_info(prim_path=prim_path, stage=stage, verbose=True)
                    prim = stage.GetPrimAtPath(prim_path)
                    sub_dict["caption"] = Utils.get_prim_attribute(prim, "caption")
                    info_dict["objects"].append(sub_dict)  # TODO: decide whether to output object info

        # Construct the output file path
        output_filepath = os.path.join(
            sub_dir,
            "object_detection",
            f"object_detection_{self._sequence_id}{self._frame_id:0{self._frame_padding}}.json",
        )

        # Schedule the backend write operation, helper method "numpy encoder" is imported to let
        self._backend.schedule(
            F.write_json, data=info_dict, path=output_filepath, indent=4, default=WriterUtils.numpy_encoder
        )

        # ================= scene graph files =================
        if self._frame_counter % self.scene_graph_interval == 0:
            nodes_reader = IRAWriterInfoDictReader(world=False)
            nodes_reader.get_nodes(
                info_dict,
                caption_only=self.caption_config["caption_only"],
                use_ai_label=self.caption_config["use_ai_label"],
                threshold_num=self.caption_config["max_object_capacity"],
            )

            scene_graph = SceneGraph(self.caption_config)
            for node in nodes_reader.nodes:
                scene_graph.add_node(node)

            scene_graph.build_graph()

            full_graph, pruned_graph = self.scene_graph_export(scene_graph, sub_dir)

            # only when edges are generated can we visualize the scene graph
            if self.caption_config["visualize_caption"]:
                self.scene_graph_caption(full_graph, pruned_graph, sub_dir)
                self.scene_graph_visualize(scene_graph, sub_dir, rgb_data)

    def scene_graph_export(self, scene_graph: SceneGraph, sub_dir: str):
        """
        Export scene graph to json file

        scene_graph (SceneGraph): the scene graph object
        sub_dir (str): the sub directory to save the output
        """
        graph = asyncio.run(scene_graph.export_graph())

        full_graph = graph.copy()

        # ================= save scene graph JSON ===================
        # only when edges are exported can we prune the graph
        pruned_graph = None
        if self.caption_config["export_edges"]:
            scene_graph.prune()
            pruned_graph = asyncio.run(scene_graph.export_graph())

        if self._frame_counter % self.scene_graph_interval == 0:

            # Schedule the backend write operation, helper method "numpy encoder" is imported to let
            if self.caption_config["save_full_scene_graph"]:
                # Construct the output file path
                output_filepath_full = os.path.join(
                    sub_dir,
                    "caption_full_json",
                    f"scene_graph_full_{self._sequence_id}{self._frame_id:0{self._frame_padding}}.json",
                )

                self._backend.schedule(
                    F.write_json,
                    data=full_graph,
                    path=output_filepath_full,
                    indent=4,
                    default=WriterUtils.numpy_encoder,
                )
                print(f"[INFO] Full scene graph saved to {output_filepath_full}")
            if self.caption_config["save_pruned_scene_graph"] and self.caption_config["export_edges"]:

                output_filepath_pruned = os.path.join(
                    sub_dir,
                    "caption_pruned_json",
                    f"scene_graph_pruned_{self._sequence_id}{self._frame_id:0{self._frame_padding}}.json",
                )

                self._backend.schedule(
                    F.write_json,
                    data=pruned_graph,
                    path=output_filepath_pruned,
                    indent=4,
                    default=WriterUtils.numpy_encoder,
                )
                print(f"[INFO] Pruned scene graph saved to {output_filepath_pruned}")

        return full_graph, pruned_graph

    def scene_graph_caption(self, full_graph: dict, pruned_graph: dict, sub_dir: str):
        """
        Generate caption for the scene graph and save to json file.

        full_graph (dict): the full scene graph dictionary
        pruned_graph (dict): the pruned scene graph dictionary
        sub_dir (str): the sub directory to save the output
        """
        # ================= get caption dict ===================
        if self._frame_counter % self.caption_interval == 0 and (
            self.caption_config["global_caption"]
            or self.caption_config["brief_caption"]
            or self.caption_config["qa_caption"]
        ):  # get scene caption and qa for the first frame
            if not self.caption_config["export_edges"]:
                print("[Warning] No edges are exported, cannot generate caption. Skip")
                return
            print("[Warning] The frame for caption can be slow.")
            gen_scene_cap = GenSceneCap(pruned_graph)

            output_dict = gen_scene_cap.scene_graph

            if self.caption_config["global_caption"]:
                output_dict["global_caption"] = asyncio.run(gen_scene_cap.prompt_global_caption())
            if self.caption_config["brief_caption"]:
                output_dict["brief_caption"] = asyncio.run(gen_scene_cap.prompt_brief_caption())

            if self.caption_config["qa_caption"]:
                full_gen_scene_cap = GenSceneCap(full_graph)
                output_dict["sft_qa"] = asyncio.run(full_gen_scene_cap.prompt_sft_qa())

            # TODO: add custom caption API

            cap_output_filepath = os.path.join(
                sub_dir,
                "caption",
                f"caption_{self._sequence_id}{self._frame_id:0{self._frame_padding}}.json",
            )

            self._backend.schedule(
                F.write_json, data=output_dict, path=cap_output_filepath, indent=4, default=WriterUtils.numpy_encoder
            )
            print(f"[INFO] Caption saved to {cap_output_filepath}")

    def scene_graph_visualize(self, scene_graph: SceneGraph, sub_dir: str, rgb_data: np.ndarray):
        """
        Visualize pruned scene graph.

        scene_graph (SceneGraph): the scene graph object
        sub_dir (str): the sub directory to save the output
        rgb_data (np.ndarray): the rgb data captured by camera
        """
        if self.caption_config["visualize_caption"] and self._frame_counter % self.scene_graph_interval == 0:

            # ================= save last frame rgb image =================
            if scene_graph.get_edges_number() > 40:
                # only draw character and object interaction in dense scene
                for node_hash in scene_graph.nodes:
                    node = scene_graph.nodes[node_hash]
                    if node.category == "object":
                        node.edges["obj-obj"] = {}

            draw_graph_on_image = scene_graph.draw_graph(image=rgb_data["data"])

            # convert to RGB from BGR
            draw_graph_on_image = cv2.cvtColor(draw_graph_on_image, cv2.COLOR_BGR2RGB)

            rgb_output_filepath = os.path.join(
                sub_dir,
                "caption_rgb",
                f"rgb_{self._sequence_id}{self._frame_id:0{self._frame_padding}}.png",
            )

            self._backend.schedule(F.write_image, data=draw_graph_on_image, path=rgb_output_filepath)
            print(f"[INFO] Visualized scene graph saved to {rgb_output_filepath}")

    def postprocess_object_detection_annotator(self, object_info, camera_params):
        """post process the annotator_data to refine the format"""

        # for all objects, add camera view data
        if isinstance(object_info, ObjectInfo):
            bbox_3d_annotator = object_info.get_annotator_info("bounding_box_3d_fast")

            if bbox_3d_annotator:
                # convert the world transform to object's view space transforma
                bbox_3d_transform = bbox_3d_annotator["transform"]
                camera_view_matrix = np.reshape(camera_params["cameraViewTransform"], (4, 4))
                bbox_3d_annotator["camera_view_transform"] = AnnotatorDataProcessor.convert_to_camera_space(
                    world_transform=bbox_3d_transform, camera_view_matrix=camera_view_matrix
                )
                translations_3d = bbox_3d_annotator["vertex"]["translations_3d"]
                # add 1 to the last column to make it transform from 1x8x3 to a 1x8x4 matrix
                translations_3d = np.concatenate([translations_3d, np.ones((1, 8, 1))], axis=-1)
                camera_view_translations_3d = AnnotatorDataProcessor.convert_to_camera_space(
                    world_transform=translations_3d, camera_view_matrix=camera_view_matrix
                )

                # remove 1 in the last column to make it a 8x3 matrix
                bbox_3d_annotator["vertex"]["camera_view_translations_3d"] = camera_view_translations_3d[:, :, :-1]

    def is_valid_info(self, object_info, camera_params):
        """check whether object info is valid

        object_info (ObjectInfo): the object info to check
        camera_params (dict): the camera parameters
        """

        # if the object is an object info
        if isinstance(object_info, ObjectInfo):
            # check whether the object's 3d bounding box is validate
            return AnnotatorDataProcessor.validate_and_process_bbox_3d_data(
                object_info=object_info, camera_params=camera_params
            )
        return False


# always register the writer to make it available to IRA
WriterRegistry.register(SceneGraphWriter)
