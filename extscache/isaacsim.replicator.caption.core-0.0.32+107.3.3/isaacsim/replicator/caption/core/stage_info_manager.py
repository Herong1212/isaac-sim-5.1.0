from __future__ import annotations

import asyncio
import os

import carb
import omni.usd
from pxr import Usd

from .annotator_helper.annotator_data_processor import AnnotatorDataProcessor
from .object_info import NodeInfo
from .settings import ReplicatorCaptionSettings
from .stage_data_process.data_postprocess import DataPostProcessor
from .three_dim_scene_graph.scene_graph import SceneGraph
from .three_dim_scene_graph.scene_node import ObjectInfoDictReader, attach_label_to_usd_func
from .sft_autolabeling.scene_graph_sft import GenSceneCap
from .utils import Utils, check_prim_character, ConfigFileReader


class StageInfoManager:
    """collect, store and process scene information base on different requirements.

    Attributes:
        object_info_dict (dict): stores annotator information of target objects.
        view_params (dict): stores camera information.
        configs (dict): stores caption configurations from config file.
    """

    __instance: StageInfoManager = None

    def __init__(self):
        if self.__instance is not None:
            raise RuntimeError("Only one instance of StageInfoManager is allowed")
        self.object_info_dict: dict[str, NodeInfo] = {}
        self.view_params = None
        StageInfoManager.__instance = self
        self.configs = None
        self.caption_results = None
        self.url = None
        self.name = None
        self.key = None
        self.collection = None

    def destroy(self):
        self.object_info_dict.clear()
        self.view_params = None
        StageInfoManager.__instance = None

    def __del__(self):
        self.destroy()

    def set_model_params(self, url, name, key):
        self.url = url
        self.name = name
        self.key = key

    def set_db(self, db):
        self.db = db

    def refresh_configs(self):
        """
        Refreshs the configs at runtime.
        """
        config_file_reader = ConfigFileReader()
        self.configs = config_file_reader.get_configs()

        # update output path
        output_path = self.get_config_valid_value("output_path")
        if not output_path:
            output_path = carb.settings.get_settings().get(ReplicatorCaptionSettings.CACHE_DATA_FOLDER)
        ReplicatorCaptionSettings.set_output_folder_path(output_path)

    def refresh_camera_path(self):
        """
        Updates camera path from UI or config file at runtime.
        """

        # check if camera path is passed from UI
        # if not, use the one from config file
        camera_path = carb.settings.get_settings().get(
            ReplicatorCaptionSettings.TARGET_CAMERA_PRIM_PATH
        )  # passed from UI
        if not camera_path:
            camera_path = self.get_config_valid_value("camera_prim_path")
            ReplicatorCaptionSettings.set_target_camera_prim_path(camera_path)
        self.configs["isaacsim.replicator.caption.core"]["camera_prim_path"] = camera_path

    @classmethod
    def get_instance(cls) -> StageInfoManager:
        if cls.__instance is None:
            StageInfoManager()
        return cls.__instance

    def get_config_valid_value(self, key):
        """
        A fast way to get configs from config file.
        """
        if not self.configs:
            self.configs = self.refresh_configs()
        config_content = self.configs["isaacsim.replicator.caption.core"]
        return config_content.get(key)

    def get_caption_configs_valid_value(self, key):
        """
        A fast way to get caption configs from config file.
        """
        if not self.configs:
            self.configs = self.refresh_configs()
        config_content = self.configs["isaacsim.replicator.caption.core"]["caption_configs"]
        return config_content.get(key)

    def get_cameras_prim_paths(self):
        """
        Get all camera prim paths from the stage.
        Only returns cameras under /World/Cameras.
        """
        stage = omni.usd.get_context().get_stage()
        return [
            str(prim.GetPath())
            for prim in stage.Traverse()
            if prim.GetTypeName() == "Camera" and prim.GetPath().GetParentPath() == "/World/Cameras"
        ]

    def load_stage_from_path(self, stage_path: str):
        """
        Load stage from path.
        """
        try:
            omni.kit.window.file.open_stage(stage_path, omni.usd.UsdContextInitialLoadSet.LOAD_ALL)
        except Exception as e:
            # Release event handle and do not procceed loading assets
            carb.log_error("Load scene ({0}) fails. No assets will be loaded.".format(stage_path))
            self._load_stage_handle = None

    def load_scene_from_config(self):
        """
        Load scene by config file and triggers load assets when scene is loaded.
        Code refer to isaacsim.replicator.agent.core.simulation SimulationManager
        """
        import omni.kit.window.file

        scene_path = self.get_config_valid_value("scene_path")
        if not scene_path:
            carb.log_error("Unable to load scene due to missing scene path in config file.")
            return
        if scene_path != omni.usd.get_context().get_stage_url():

            def open_stage(usd_path: str, ignore_unsave=True):
                carb.log_info("Opening stage: {0}".format(usd_path))
                if not Usd.Stage.IsSupportedFile(usd_path):
                    raise ValueError("Only USD files can be loaded")

                IGNORE_UNSAVED_CONFIG_KEY = "/app/file/ignoreUnsavedStage"
                old_val = carb.settings.get_settings().get(IGNORE_UNSAVED_CONFIG_KEY)
                carb.settings.get_settings().set(IGNORE_UNSAVED_CONFIG_KEY, ignore_unsave)
                omni.kit.window.file.open_stage(usd_path, omni.usd.UsdContextInitialLoadSet.LOAD_ALL)
                carb.settings.get_settings().set(IGNORE_UNSAVED_CONFIG_KEY, old_val)

            try:
                open_stage(scene_path)
            except Exception as e:
                # Release event handle and do not procceed loading assets
                carb.log_error("Load scene ({0}) fails. No assets will be loaded.".format(scene_path))
                self._load_stage_handle = None

        else:
            # Skip loading stage. Load assets other than scene
            carb.log_info("The current scene matches the scene path in config file. Scene loading is skipped.")

    # NOTE:: currently this method is a place holder:>
    # It only call data fetching method to store information in to a json file format:
    # Please inject the function that build scene graph from object data information:
    async def async_gather_node_info_from_camera_view(self):
        """get node information from target view"""
        # check whether current camrea path is valid:StageInfoManager
        self.object_info_dict.clear()
        self.view_params = None
        stage = omni.usd.get_context().get_stage()
        target_camera_path = ReplicatorCaptionSettings.get_target_camera_prim_path()
        if not Utils.is_valid_camera_path(target_camera_path):
            carb.log_warn(
                "Error as warning: {camera_path} is not a valid camera path.".format(camera_path=target_camera_path)
            )
            return

        annotator_processor = AnnotatorDataProcessor.get_instance()
        target_prim_path_list, camera_params, _ = await annotator_processor.capture_camera_view_information()
        # if camera_params is not None, re-format the camera parameter's format:
        if camera_params:
            self.view_params = AnnotatorDataProcessor.reformat_camera_params(camera_params)

        for prim_path in target_prim_path_list:
            # for prim in stage.Traverse():
            prim = stage.GetPrimAtPath(prim_path)
            class_name = Utils.get_prim_semantic_label(
                target_prim=prim
            )  # get the class name of the prim from manual labels temporarily
            if not class_name:
                continue
            self.register_object_information(target_prim_path=prim_path, stage=stage, view_params=self.view_params)

            # add 2d information to the object information
            if prim_path in annotator_processor.object_info_dict:
                bbox_2d_tight = annotator_processor.object_info_dict[prim_path].get_annotator_info(
                    "bounding_box_2d_tight_fast"
                )
                self.object_info_dict[prim_path].update_annotator_data("2d_bbox_info", bbox_2d_tight.tolist()[1:5])
            else:
                carb.log_warn("Error as warning: {prim_path} is not visible.".format(prim_path=prim_path))
                del self.object_info_dict[prim_path]
                continue

        self.output_object_data(sub_dir=Utils.camera_path_to_id(target_camera_path))

    async def async_generate_camera_scene_graph_stage(self):
        """get node information from target view"""
        # check whether current camrea path is valid:StageInfoManager
        self.object_info_dict.clear()
        self.view_params = None
        stage = omni.usd.get_context().get_stage()
        target_camera_path = ReplicatorCaptionSettings.get_target_camera_prim_path()
        if not Utils.is_valid_camera_path(target_camera_path):
            carb.log_warn(
                "Error as warning: {camera_path} is not a valid camera path.".format(camera_path=target_camera_path)
            )
            return

        annotator_processor = AnnotatorDataProcessor.get_instance()
        target_prim_path_list, camera_params, rgb_data = await annotator_processor.capture_camera_view_information()
        if len(target_prim_path_list) == 0:
            attach_label_to_usd_func()
            target_prim_path_list, camera_params, rgb_data = await annotator_processor.capture_camera_view_information()
        # if camera_params is not None, re-format the camera parameter's format:
        if camera_params:
            self.view_params = AnnotatorDataProcessor.reformat_camera_params(camera_params)

        # for prim_path in target_prim_path_list:
        final_prim_path_set = set()
        # for prim in stage.Traverse():
        for prim_path in target_prim_path_list:
            prim = stage.GetPrimAtPath(prim_path)
            class_name = Utils.get_prim_semantic_label(
                target_prim=prim
            )  # get the class name of the prim from manual labels temporarily
            if not class_name:
                continue
            # prim_path = str(prim.GetPrimPath())
            final_prim_path, usd_path = Utils.capture_usd_info(prim_path, stage, verbose=True)
            if final_prim_path in final_prim_path_set:
                """skip the duplicated prim"""
                continue
            final_prim_path_set.add(final_prim_path)
            if usd_path is None:
                print(f"Warning: {prim_path} has no usd path.".format(prim_path=prim_path))
                usd_path = "None"

            self.register_object_information(target_prim_path=prim_path, stage=stage, view_params=self.view_params)
            try:
                # add 2d information to the object information
                bbox_2d_tight = annotator_processor.object_info_dict[prim_path].get_annotator_info(
                    "bounding_box_2d_tight_fast"
                )
            except KeyError:
                carb.log_warn("Error as warning: {prim_path} is not visible.".format(prim_path=prim_path))
                del self.object_info_dict[prim_path]
                continue

            self.object_info_dict[prim_path].update_annotator_data("usd_path", usd_path)
            self.object_info_dict[prim_path].update_annotator_data("2d_bbox_info", bbox_2d_tight.tolist()[1:5])
            is_character = check_prim_character(prim)
            self.object_info_dict[prim_path].update_annotator_data("is_character", is_character)
            self.object_info_dict[prim_path].update_annotator_data("caption", Utils.get_prim_attribute(prim, "caption"))

        caption_configs = self.get_config_valid_value("caption_configs")
        scene_graph = SceneGraph(caption_configs=caption_configs)
        node_reader = ObjectInfoDictReader(world=False)
        node_reader.get_nodes(
            self.object_info_dict,
            caption_only=self.get_config_valid_value("caption_only"),
            use_ai_label=self.get_caption_configs_valid_value("use_ai_label"),
            threshold_num=self.get_caption_configs_valid_value("max_object_capacity"),
        )
        for node in node_reader.nodes:
            scene_graph.add_node(node)

        camera_folder = Utils.camera_path_to_id(target_camera_path)
        save_dir = ReplicatorCaptionSettings.get_scene_graph_folder_path(sub_dir_name=camera_folder)

        scene_graph.build_graph()

        full_graph = await self.save_full_scene_graph(scene_graph, save_dir)
        pruned_graph = await self.save_pruned_scene_graph(scene_graph, save_dir)
        await self.save_visualized_scene_graph(scene_graph, rgb_data, save_dir)
        await self.save_scene_cap(full_graph, pruned_graph, save_dir)

        return scene_graph

    async def save_scene_cap(self, full_scene_graph_dict, pruned_scene_graph_dict, save_dir):
        """
        Saves scene graph caption to a json file.

        full_scene_graph_dict (dict): full scene graph dictionary exported from SceneGraph object.
        pruned_scene_graph_dict (dict): pruned scene graph dictionary exported from SceneGraph object.
        save_dir (str): the directory to save the scene graph caption.
        """
        if pruned_scene_graph_dict is None:
            carb.log_warn("No pruned scene graph is generated.")
            return
        generate_caption_flag = (
            self.get_caption_configs_valid_value("global_caption")
            or self.get_caption_configs_valid_value("qa_caption")
            or self.get_caption_configs_valid_value("brief_caption")
        )
        if not generate_caption_flag:
            return
        print("Generating scene graph caption... This may take a while.")
        gen_scene_cap = GenSceneCap(pruned_scene_graph_dict, url=self.url, name=self.name, key=self.key)
        global_cap = None
        brief_cap = None
        sft_qa = None
        if self.get_caption_configs_valid_value("global_caption"):
            global_cap = await gen_scene_cap.prompt_global_caption()
        if self.get_caption_configs_valid_value("brief_caption"):
            brief_cap = await gen_scene_cap.prompt_brief_caption()
        if self.get_caption_configs_valid_value("qa_caption"):
            # use full graph to generate accurate QA caption
            if full_scene_graph_dict is None:
                raise Exception("Need full scene graph to generate QA caption.")
            gen_scene_cap_full = GenSceneCap(full_scene_graph_dict, url=self.url, name=self.name, key=self.key)
            sft_qa = await gen_scene_cap_full.prompt_sft_qa()

        self.caption_results = gen_scene_cap.scene_graph

        self.caption_results["global_caption"] = global_cap
        self.caption_results["sft_qa"] = sft_qa
        self.caption_results["brief_caption"] = brief_cap
        cap_file_output = os.path.join(save_dir, "scene_graph_caption.json")
        Utils.store_as_json_file(cap_file_output, self.caption_results)

    async def save_full_scene_graph(self, scene_graph, save_dir):
        """
        Saves full scene graph to a json file.

        scene_graph (SceneGraph): the scene graph object.
        save_dir (str): the directory to save the full scene graph dictionary.
        """
        if self.get_caption_configs_valid_value("save_full_scene_graph"):
            graph = await scene_graph.export_graph()
            full_graph = graph.copy()
            output_file = os.path.join(save_dir, "full_scene_graph.json")
            Utils.store_as_json_file(output_file, full_graph)

            return full_graph

        return None

    async def save_pruned_scene_graph(self, scene_graph: SceneGraph, save_dir):
        """
        Saves pruned scene graph to a json file. It only works when edges are available in the scene graph.
        """
        export_edges = self.get_caption_configs_valid_value("export_edges")
        if export_edges and self.get_caption_configs_valid_value("save_pruned_scene_graph"):
            scene_graph.prune()
            pruned_graph = await scene_graph.export_graph()
            save_file_name = os.path.join(save_dir, "pruned_scene_graph.json")
            Utils.store_as_json_file(save_file_name, pruned_graph)

            return pruned_graph

        return None

    async def save_visualized_scene_graph(self, scene_graph, rgb_data, save_dir):
        """
        Saves visualized scene graph to a jpg file.

        scene_graph (SceneGraph): the scene graph object.
        rgb_data (numpy.ndarray): the rgb data of the camera view.
        save_dir (str): the directory to save the visualized scene graph jpg file
        """
        if self.get_caption_configs_valid_value("visualize_caption"):
            # draw scene graph on output image
            file_name = os.path.join(save_dir, "viz_camera_scene_graph.jpg")
            scene_graph.draw_graph(rgb_data, file_name)

    def gather_store_object_info_form_view(self):
        """store target object information"""
        asyncio.ensure_future(self.async_gather_node_info_from_camera_view())
        asyncio.ensure_future(self.async_generate_camera_scene_graph_stage())

    def register_object_information(self, target_prim_path: str, stage=None, view_params=None):
        """get object information from annotators and save them into object_info_dict.

        target_prim_path (str): the target prim path to get information.
        stage (Usd.Stage): the stage to get the target prim.
        view_params (dict): the camera information for prim information processing.
        """

        if stage is None:
            return
        target_prim = stage.GetPrimAtPath(target_prim_path)
        semantic_label = Utils.get_prim_semantic_label(target_prim=target_prim)
        # NOTE:: should we still save the object information if it is not labeled?
        object_reference_url = Utils.get_object_reference(prim_path=target_prim_path, stage=stage)
        if target_prim_path not in self.object_info_dict:
            self.object_info_dict[target_prim_path] = NodeInfo(label=semantic_label, prim_path=target_prim_path)

        target_object_info = self.object_info_dict[target_prim_path]
        target_object_info.update_annotator_data("reference url", object_reference_url)
        bbox_info = DataPostProcessor.get_bbox_3d_data(prim=target_prim, view_params=view_params)
        world_bbox_info = DataPostProcessor.get_bbox_3d_data(prim=target_prim, view_params=None)
        target_object_info.update_annotator_data("bbox_info", bbox_info)
        target_object_info.update_annotator_data("world_bbox_info", world_bbox_info)

        is_character = check_prim_character(target_prim)
        target_object_info.update_annotator_data("is_character", is_character)

    def output_object_data(self, sub_dir):
        """output prim information into a json file.

        sub_dir (str): the sub directory to store the json file.
        """
        info_dict = {"object": {}, "camera": {}}
        # collect camera information
        for prim_path, agent_info in self.object_info_dict.items():
            # check whether agent is valid
            info_dict["object"][prim_path] = agent_info.get_all_info()
        # then load current camera info
        info_dict["camera"] = self.view_params
        file_folder_path = ReplicatorCaptionSettings.get_data_folder_path(sub_dir_name=sub_dir)
        target_file_name = ReplicatorCaptionSettings.DATA_FILE_NAME
        file_path = os.path.join(file_folder_path, target_file_name)
        # store the data as a json file
        Utils.store_as_json_file(file_path=file_path, info_data=info_dict)
