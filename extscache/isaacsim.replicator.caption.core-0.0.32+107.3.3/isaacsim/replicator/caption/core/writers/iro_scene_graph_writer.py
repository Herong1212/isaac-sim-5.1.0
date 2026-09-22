"""
This writer only works for IsaacSim.replicator.object. The writer class is inherited from the WorkerWriter class in the replicator core.
"""

import logging, os, asyncio

import cv2

import omni.kit
import omni.usd
from omni.replicator.core import AnnotatorRegistry, BackendDispatch
import numpy as np

from isaacsim.replicator.object.mutables.camera import Camera_DEV
from isaacsim.replicator.object.utility.misc import tentative_retrieve, P, write_yaml, VERSION
from isaacsim.replicator.object.simple_writer import WorkerWriter

from omni.replicator.core.scripts import functional as F
from omni.replicator.core import WriterRegistry

from ..sft_autolabeling.scene_graph_sft import GenSceneCap
from ..three_dim_scene_graph.scene_graph import SceneGraph
from ..three_dim_scene_graph.scene_node import IROWriterInfoDictReader
from .writer_utils import WriterUtils
from ..utils import Utils

class IROSceneGraphWriter(WorkerWriter):
    """
    A writer class for Isaacsim.replicator.object extension. This writer is responsible for generating scene graph
    and captioning the scene graph from IRO simulation. The scene graph is generated from the bounding box
    annotations and camera parameters.

    Attributes:
        caption_configs (dict): The configuration for generating caption.
        scene (Scene): The scene object.
        annotators (list): The list of annotators to use for generating caption.
        oro_metadata (dict): The metadata for the current frame.
        oro_index (int): The index of the current frame.
        global_metadata (dict): The global metadata.
        is_multi_camera (bool): Whether the scene has multiple cameras.
        camera_name_to_rp_name (dict): The mapping from camera name to replicator product name
    """

    def __init__(self, caption_configs, scene):
        """
        caption_configs (dict): The configuration for generating caption.
        scene (Scene): The scene object.
        """
        self._backend = BackendDispatch({"paths": {"out_dir": scene.output_path}})
        self.caption_configs = caption_configs
        self.scene = scene
        self.annotators = [
            AnnotatorRegistry.get_annotator("rgb"),
            AnnotatorRegistry.get_annotator(
                "bounding_box_2d_tight_fast",
            ),
            AnnotatorRegistry.get_annotator(
                "bounding_box_3d_fast",
            ),
            AnnotatorRegistry.get_annotator("camera_params"),
        ]

        # Create all necessary output directories
        os.makedirs(f"{self.scene.output_path}/caption", exist_ok=True)
        os.makedirs(f"{self.scene.output_path}/caption/caption_full_json", exist_ok=True)
        os.makedirs(f"{self.scene.output_path}/caption/caption_pruned_json", exist_ok=True)
        os.makedirs(f"{self.scene.output_path}/caption/caption_dict", exist_ok=True)
        os.makedirs(f"{self.scene.output_path}/caption/caption_rgb", exist_ok=True)

        if self.caption_configs["export_depth"]:
            self.annotators.append(AnnotatorRegistry.get_annotator("distance_to_image_plane"))
            os.makedirs(f"{self.scene.output_path}/caption/depth", exist_ok=True)

        if self.caption_configs["export_point_cloud"]:
            self.annotators.append(AnnotatorRegistry.get_annotator("pointcloud"))
            os.makedirs(f"{self.scene.output_path}/caption/pointcloud", exist_ok=True)

        self.oro_metadata = None
        self.oro_index = None

        self._frame_id = 0
        self.global_metadata = {}
        self.is_multi_camera = False
        self.camera_name_to_rp_name = None

    def __add_usd_paths_to_caption_dict(self, caption_dict):
        # add usd path to caption_dict, save it to bbox_2d_unfiltered
        usd_paths = []
        stage = omni.usd.get_context().get_stage()
        for prim_path in caption_dict["bbox_2d_unfiltered"]["info"]["primPaths"]:
            _, usd_path = Utils.capture_usd_info(prim_path, stage=stage, verbose=True)
            usd_paths.append(usd_path)
        caption_dict["usd_paths"] = usd_paths

    def write(self, data):
        """
        Writes the scene graph and caption to the output directory.

        data (dict): The collected writer data for the current frame.
            More details see https://docs.omniverse.nvidia.com/extensions/latest/ext_replicator/custom_writer.html.
        """
        self.oro_metadata = self.global_metadata.pop(self._frame_id)
        self.oro_index = self._frame_id

        # in multi-camera case, match rp names with camera names
        if self.is_multi_camera and self.camera_name_to_rp_name is None:
            self.camera_name_to_rp_name = {}
            for key in data:
                if key.startswith("rp_Replicator"):
                    rp_name = key[3:]
                    replicator_camera_path = data[key]["camera"]
                    camera_name = replicator_camera_path[
                        len("/Replicator/Camera_") : replicator_camera_path.find("_Xform/Camera_")
                    ]
                    self.camera_name_to_rp_name[camera_name] = rp_name

        with P(f"write {self.oro_index}"):

            at_least_one_visible_tracked_mutable = False
            for mutable in self.scene.mutables.values():
                if isinstance(mutable, Camera_DEV):
                    if self.is_multi_camera:
                        mutable.rp_name = self.camera_name_to_rp_name[mutable.name]
                    output_name = tentative_retrieve(
                        "output_name", self.oro_metadata, str, f'{self.oro_metadata["seed"]}_{mutable.name}'
                    )
                    output_name = output_name.replace("$(camera_name)", mutable.name).replace(
                        "$(camera_index)", str(mutable.ref_index)
                    )
                    image = self.save_caption_results(mutable, data, output_name)
                    if self.scene.output_switches["images"]:
                        output_path = f"{self.scene.output_path}/images/{output_name}.jpg"
                        message = f"[METROPERF]: frame saved at {output_path}, [{self.oro_index + 1}/{self.scene.num_frames}]"
                        logging.info(message)
                        print(message)
                        self._backend.write_image(f"{output_path}", image)

                    if self.scene.progress_bar is not None:
                        self.scene.progress_bar.model.set_value((self.oro_index + 1) / self.scene.num_frames)

            # if nothing is tracked, don't write  xxx
            if tentative_retrieve("skip_frames_with_no_visible_tracked_mutables", self.oro_metadata, bool, False):
                if not at_least_one_visible_tracked_mutable:
                    self._frame_id += 1
                    return

            output_name_global = tentative_retrieve(
                "output_name", self.oro_metadata, str, f'{self.oro_metadata["seed"]}'
            )
            output_name_global = output_name_global.replace("$(camera_name)", "GLOBAL").replace(
                "$(camera_index)", "GLOBAL"
            )

            metadata_with_header = {
                "isaacsim.replicator.object": {
                    "version": VERSION,
                }
            }

            metadata_with_header["isaacsim.replicator.object"].update(self.oro_metadata)
            if self.scene.output_switches["descriptions"]:
                metadata_with_header["isaacsim.replicator.object"][
                    "output_path"
                ] += "__NEXT"  # convenience for restoration
                write_yaml(metadata_with_header, f"{self.scene.output_path}/descriptions/{output_name_global}.yaml")

        self._frame_id += 1

    def save_caption_results(self, mutable, data, output_name):
        image, depth, pointcloud, caption_dict = mutable.capture_caption(self.caption_configs, data)

        self.__add_usd_paths_to_caption_dict(caption_dict)

        caption_dir = f"{self.scene.output_path}/caption"
        self.process_scene_graph(caption_dict, image, caption_dir, output_name)

        if self.caption_configs["export_depth"] and depth is not None:
            output_filepath = f"{caption_dir}/depth/{output_name}.npy"
            logging.debug(f"depth path: {output_filepath}")
            self._backend.schedule(F.write_np, data=depth, path=output_filepath)

            message = f"[METROPERF]: depth map saved at {caption_dir}/{output_name}.npy"
            logging.info(message)
            print(message)

        if self.caption_configs["export_point_cloud"] and pointcloud is not None:
            output_filepath = f"{caption_dir}/pointcloud/{output_name}.npy"
            self._backend.schedule(F.write_np, data=pointcloud, path=output_filepath)

            message = f"[METROPERF]: point cloud saved at {caption_dir}/{output_name}.npy"
            logging.info(message)
            print(message)

        return image

    def process_scene_graph(self, obj_info_dict, rgb_data, sub_dir, output_name):
        """
        Prepares SceneGraph object based on collected IRO prim information and camera captured rgb data.

        obj_info_dict (dict): The object information dictionary.
            {
                "bbox_2d_unfiltered": bounding_box_2d_tight_fast,
                "bbox_3d_unfiltered": bounding_box_3d_fast,
            }
            Direct output from Annotator
        rgb_data (np.ndarray): The RGB image data captured by the camera.
        sub_dir (str): The sub directory to save the scene graph files.
        output_name (str): The output name of the scene graph files.
        """
        iro_reader = IROWriterInfoDictReader(world=False)
        iro_reader.get_nodes(
            obj_info_dict,
            caption_only=self.caption_configs["caption_only"],
            use_ai_label=self.caption_configs["use_ai_label"],
            threshold_num=self.caption_configs["max_object_capacity"],
        )
        scene_graph = SceneGraph(self.caption_configs)
        for node in iro_reader.nodes:
            scene_graph.add_node(node)

        export_edges = self.caption_configs["export_edges"]

        if export_edges:
            # add edges to the scene graph
            scene_graph.build_graph()

        full_graph, pruned_graph = self.scene_graph_export(scene_graph, sub_dir, output_name)

        # only when edges are generated can we visualize the scene graph
        if export_edges:
            self.scene_graph_caption(full_graph, pruned_graph, sub_dir, output_name)
            if self.caption_configs["visualize_caption"]:
                self.scene_graph_visualize(scene_graph, sub_dir, output_name, rgb_data)

    def scene_graph_export(self, scene_graph: SceneGraph, sub_dir: str, output_name: str):
        """
        Exports the scene graph, including full and pruned graphs, to JSON.

        scene_graph (SceneGraph): The scene graph object.
        sub_dir (str): The sub directory to save the scene graph files.
        output_name (str): The output name of the scene graph files.
        """

        graph = asyncio.run(scene_graph.export_graph())

        full_graph = graph.copy()

        # ================= save scene graph JSON ===================
        # only when edges are exported can we prune the graph
        pruned_graph = None
        export_edges = self.caption_configs["export_edges"]

        if export_edges:
            scene_graph.prune()
            pruned_graph = asyncio.run(scene_graph.export_graph())

        # Schedule the backend write operation, helper method "numpy encoder" is imported to let
        if self.caption_configs["save_full_scene_graph"]:
            # Construct the output file path
            output_filepath_full = os.path.join(
                sub_dir,
                "caption_full_json",
                f"{output_name}.json",
            )

            self._backend.schedule(
                F.write_json,
                data=full_graph,
                path=output_filepath_full,
                indent=4,
                default=WriterUtils.numpy_encoder,
            )

            message = f"[METROPERF]: full scene graph saved at {output_filepath_full}"
            logging.info(message)
            print(message)

        if self.caption_configs["save_pruned_scene_graph"] and export_edges:

            output_filepath_pruned = os.path.join(
                sub_dir,
                "caption_pruned_json",
                f"{output_name}.json",
            )

            self._backend.schedule(
                F.write_json,
                data=pruned_graph,
                path=output_filepath_pruned,
                indent=4,
                default=WriterUtils.numpy_encoder,
            )

            message = f"[METROPERF]: pruned scene graph saved at {output_filepath_pruned}"
            logging.info(message)
            print(message)

        return full_graph, pruned_graph

    def scene_graph_caption(self, full_graph: dict, pruned_graph: dict, sub_dir: str, output_name: str):
        """
        Generates caption for the scene graph.

        full_graph (dict): The full scene graph dictionary exported from SceneGraph object.
        pruned_graph (dict): The pruned scene graph dictionary exported from SceneGraph object.
        sub_dir (str): The sub directory to save the caption files.
        output_name (str): The output name of the caption files.
        """

        # ================= get caption dict ===================
        global_caption_switch = self.caption_configs["global_caption"]
        brief_caption_switch = self.caption_configs["brief_caption"]
        qa_caption_switch = self.caption_configs["qa_caption"]

        if global_caption_switch or brief_caption_switch or qa_caption_switch:
            if not self.caption_configs["export_edges"]:
                print("[Warning] No edges are exported, cannot generate caption. Skip")
                return
            print("[Warning] The frame for caption can be slow.")
            gen_scene_cap = GenSceneCap(pruned_graph)

            output_dict = gen_scene_cap.scene_graph

            if global_caption_switch:
                output_dict["global_caption"] = asyncio.run(gen_scene_cap.prompt_global_caption())
            if brief_caption_switch:
                output_dict["brief_caption"] = asyncio.run(gen_scene_cap.prompt_brief_caption())

            if qa_caption_switch:
                full_gen_scene_cap = GenSceneCap(full_graph)
                output_dict["sft_qa"] = asyncio.run(full_gen_scene_cap.prompt_sft_qa())

            # TODO: add custom caption API
            cap_output_filepath = os.path.join(
                sub_dir,
                "caption_dict",
                f"{output_name}.json",
            )

            self._backend.schedule(
                F.write_json,
                data=output_dict,
                path=cap_output_filepath,
                indent=4,
                default=WriterUtils.numpy_encoder,
            )

            message = f"[METROPERF]: caption saved at {cap_output_filepath}"
            logging.info(message)
            print(message)

    def scene_graph_visualize(self, scene_graph: SceneGraph, sub_dir: str, output_name: str, rgb_data: np.ndarray):
        """
        Visualize pruned scene graph on images.

        scene_graph (SceneGraph): The scene graph object.
        sub_dir (str): The sub directory to save the visualization files.
        output_name (str): The output name of the visualization files.
        rgb_data (np.ndarray): The RGB image data captured by the camera.
        """
        # ================= save last frame rgb image =================
        if scene_graph.get_edges_number() > 40:
            # only draw character and object interaction in dense scene
            for node_hash in scene_graph.nodes:
                node = scene_graph.nodes[node_hash]
                if node.category == "object":
                    node.edges["obj-obj"] = {}

        draw_graph_on_image = scene_graph.draw_graph(image=np.array(rgb_data))

        # convert to RGB from BGR
        draw_graph_on_image = cv2.cvtColor(draw_graph_on_image, cv2.COLOR_BGR2RGB)

        rgb_output_filepath = os.path.join(
            sub_dir,
            "caption_rgb",
            f"{output_name}.png",
        )

        self._backend.schedule(F.write_image, data=draw_graph_on_image, path=rgb_output_filepath)

        message = f"[METROPERF]: visualized caption saved at {rgb_output_filepath}"
        logging.info(message)
        print(message)

print("[INFO] Register IROSceneGraphWriter to the WriterRegistry")
# registry
WriterRegistry.register(IROSceneGraphWriter)
