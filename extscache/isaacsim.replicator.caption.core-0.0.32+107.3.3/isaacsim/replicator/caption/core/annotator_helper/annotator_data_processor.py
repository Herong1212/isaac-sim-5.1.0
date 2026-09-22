from __future__ import annotations

import os
from collections import Counter
from pathlib import Path
from typing import Any

import carb
import numpy as np
import omni
import omni.replicator.core as rep
import omni.usd
from omni.replicator.core.scripts.writers_default.tools import *
from omni.syntheticdata.scripts import helpers
from PIL import Image

from ..settings import ReplicatorCaptionSettings
from ..utils import Utils


class ObjectAnnotatorInfo:
    """Store raw information related to target object"""

    def __init__(self, label: str = "", prim_path: str = "", annotators: dict[str, Any] | None = None):
        self.label: str = label  # object's semantic label
        self.prim_path: str = prim_path  # object's prim path
        if annotators is None:
            self.annotator_data = {}
        else:
            self.annotator_data = annotators

    def get_label(self) -> str:
        return self.label

    def get_prim_path(self) -> str:
        return self.prim_path

    def update_annotator_data(self, annotator_name, data):
        """store annotator info base on annotator's name"""
        self.annotator_data[annotator_name] = data
        pass

    def get_annotator_info(self, annotator_name: str):
        if annotator_name not in self.annotator_data:
            carb.log_info(
                " Warning as message:: Object Detection class: {class_name} does not handle: {annotator_name} annotator".format(
                    class_name=type(self).__name__, annotator_name=annotator_name
                )
            )
            return None
        else:
            return self.annotator_data[annotator_name]


class AnnotatorDataProcessor:
    """collect, store and process scene information base on different requirements"""

    __instance: AnnotatorDataProcessor = None

    def __init__(self):
        if self.__instance is not None:
            raise RuntimeError("Only one instance of AnnotatorDataProcessor is allowed")

        # template object info dict used to store all annotator information for each object
        self.object_info_dict: dict[str, ObjectAnnotatorInfo] = {}

        AnnotatorDataProcessor.__instance = self

    def destroy(self):
        """destroy function that would be triggered when destroy the Annotator Data Processor"""
        # clean all object info stored in the object info dict
        self.object_info_dict.clear()
        AnnotatorDataProcessor.__instance = None

    def __del__(self):
        self.destroy()

    @classmethod
    def get_instance(cls) -> AnnotatorDataProcessor:
        if cls.__instance is None:
            AnnotatorDataProcessor()
        return cls.__instance

    @classmethod
    async def get_replicator_annotators(cls, annotator_name_list: list[str], render_product_size: tuple = (1920, 1080)):
        """get specific annotator from target camera view"""
        target_camera_path = ReplicatorCaptionSettings.get_target_camera_prim_path()
        rp = rep.create.render_product(target_camera_path, render_product_size)
        annotator_dict = {}
        for annotator_name in annotator_name_list:
            target_annotator = rep.AnnotatorRegistry.get_annotator(annotator_name)
            # attach the render product to the annotator.
            target_annotator.attach(rp)
            annotator_dict[str(annotator_name)] = target_annotator
        return annotator_dict

    @classmethod
    def calculate_box_2d_area(cls, bbox):
        """calculate the area of 2d tight bounding box"""
        x_min, y_min, x_max, y_max = int(bbox["x_min"]), int(bbox["y_min"]), int(bbox["x_max"]), int(bbox["y_max"])
        area = (x_max - x_min) * (y_max - y_min)
        bbox = [x_min, y_min, x_max, y_max]
        return area

    @classmethod
    async def save_renderproduct(cls, render_product_data: Any):
        """save render product to the cache folder"""
        # get output folder path
        camera_path = ReplicatorCaptionSettings.get_target_camera_prim_path()
        camera_id = Utils.camera_path_to_id(camera_path)
        output_folder_path = ReplicatorCaptionSettings.get_image_folder_path(camera_id)
        # check whether the output folder exist:
        Utils.check_folder_exist(folder_path=output_folder_path, create_one=True)
        # if so, get the file name and assemble file path
        camera_view_image_name = "{camera_id}.png".format(camera_id=camera_id)
        camera_view_image_path = os.path.join(output_folder_path, camera_view_image_name)
        # save the camera view image
        rgb = Image.fromarray(render_product_data, "RGBA").convert("RGB")
        rgb.save(camera_view_image_path, quality=90)
        # output the logging info:
        carb.log_info(
            "camera view image has been stored in the {target_path}".format(target_path=camera_view_image_path)
        )

    @classmethod
    def reformat_camera_params(cls, camera_params: Any):
        """helper method to reformat the camera params array"""

        projection_type = camera_params["cameraModel"]
        view_to_world = np.linalg.inv(np.reshape(camera_params["cameraViewTransform"], (4, 4)))
        world_to_view = np.reshape(camera_params["cameraViewTransform"], (4, 4))
        width, height = camera_params["renderProductResolution"][0], camera_params["renderProductResolution"][1]
        if projection_type == "fisheyePolynomial":
            ftheta = {
                "width": camera_params["cameraFisheyeNominalWidth"],
                "height": camera_params["cameraFisheyeNominalHeight"],
                "cx": camera_params["cameraFisheyeOpticalCentre"][0],
                "cy": camera_params["cameraFisheyeOpticalCentre"][1],
                "poly_a": camera_params["cameraFisheyePolynomial"][0],
                "poly_b": camera_params["cameraFisheyePolynomial"][1],
                "poly_c": camera_params["cameraFisheyePolynomial"][2],
                "poly_d": camera_params["cameraFisheyePolynomial"][3],
                "poly_e": camera_params["cameraFisheyePolynomial"][4],
                "poly_f": camera_params["cameraFisheyePolynomial"][5],
                "max_fov": camera_params["cameraFisheyeMaxFOV"],
            }
            ftheta["edge_fov"] = helpers.ftheta_distortion(ftheta, ftheta["width"] / 2)
            ftheta["c_ndc"] = np.array(
                [
                    (ftheta["cx"] - ftheta["width"] / 2) / ftheta["width"],
                    (ftheta["height"] / 2 - ftheta["cy"]) / ftheta["width"],
                ]
            )
        else:
            ftheta = None

        view_params = {
            "view_to_world": np.array(view_to_world),
            "world_to_view": np.array(world_to_view),
            "projection_type": projection_type,
            "ftheta": ftheta,
            "width": width,
            "height": height,
            "aspect_ratio": width / height,
            "clipping_range": camera_params["cameraNearFar"],
            "horizontal_aperture": camera_params["cameraAperture"][0],
            "focal_length": camera_params["cameraFocalLength"],
        }
        return view_params

    async def capture_camera_view_information(self, save_image: bool = True, annotator_list: list[str] = []):
        """get object's annotator data from specific camera view in the stage"""
        self.object_info_dict.clear()
        # if the input does not specify the annotator list, use the default annotator list
        if not annotator_list:
            annotator_list = ReplicatorCaptionSettings.DEFAULT_ANNOTATOR_LIST
        target_camera_path = ReplicatorCaptionSettings.get_target_camera_prim_path()
        carb.log_info(
            "camera path in capture camera view information {target_camera_path}".format(
                target_camera_path=target_camera_path
            )
        )

        camera_params = None
        # attach the render product to target annotators
        annotator_dict = await AnnotatorDataProcessor.get_replicator_annotators(annotator_name_list=annotator_list)
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        # update the simulation with one async step.
        await rep.orchestrator.step_async()
        await rep.orchestrator.step_async()
        # add two frame's update to buffer the cache
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        # fetch current annotator's information :
        if "rgb" in annotator_dict:
            rgb_data = annotator_dict["rgb"].get_data()
            if save_image:
                # save camera view as image
                await AnnotatorDataProcessor.save_renderproduct(rgb_data)

        if "camera_params" in annotator_dict:
            camera_params = annotator_dict["camera_params"].get_data()

        # validate and record object data
        await self.validate_and_process_object_info(annotator_dict)
        await omni.kit.app.get_app().next_update_async()
        # post process the object information
        await self.post_process_object_info()
        target_object_key = self.object_info_dict.keys()
        # clean and release the storage.
        return target_object_key, camera_params, rgb_data

    async def validate_and_process_object_info(self, all_annotator_dict: dict):
        """save 2d bbox information to the target data folder"""

        # get captioned object list:
        # currently does not determined whether the caption information would be stored in the object directly.
        # If so, we could change this method to a better solution.
        # captioned_usd_list = Utils.get_captioned_props_list()

        # get current stage:
        stage = omni.usd.get_context().get_stage()
        target_annotator = ["bounding_box_2d_tight_fast", "bounding_box_2d_loose_fast"]  # skeleton_data
        unnecessary_type_list = ReplicatorCaptionSettings.UNNECESSARY_TYPE_LIST
        annotator_dict = Utils.filter_dict_by_keys(all_annotator_dict, target_annotator)

        for annotator_name, annotator_object in annotator_dict.items():
            annotator = annotator_object.get_data()
            object_prim_paths = annotator["info"]["primPaths"]
            id_to_label = annotator["info"]["idToLabels"]
            id_to_data = annotator["data"]
            for idx, prim_path in enumerate(object_prim_paths):
                # get object's semantic label
                semantic_id = id_to_data[idx]["semanticId"]
                label = id_to_label[semantic_id]
                object_data = id_to_data[idx]
                # check whether object need to be ignore
                if str(label).lower() in unnecessary_type_list:
                    continue

                # NOTE::
                # following function check whether the object is in the captioned asset folder,
                # please feel free to change this:
                # current_object_path = str(Utils.get_object_reference(prim_path=prim_path, stage=stage))
                # # if the object has not been captioned.
                # if not current_object_path in captioned_usd_list:
                #     continue

                if prim_path not in self.object_info_dict:
                    self.object_info_dict[prim_path] = ObjectAnnotatorInfo(label=label, prim_path=prim_path)
                # Update the info dictionary with the annotator data
                self.object_info_dict[prim_path].update_annotator_data(annotator_name, object_data)

    async def post_process_object_info(self):
        """post process the object info, get object 2d bounding box and get the info"""
        elements = []
        for prim_path, object_info in self.object_info_dict.items():
            # get object bbox tight
            bbox_2d_tight = object_info.get_annotator_info("bounding_box_2d_tight_fast")
            if not bbox_2d_tight:
                continue
            # get bbox loose
            bbox_2d_loose = object_info.get_annotator_info("bounding_box_2d_loose_fast")
            if not bbox_2d_loose:
                continue
            area = self.calculate_box_2d_area(bbox_2d_tight)
            prim_path = object_info.get_prim_path()
            elements.append((prim_path, area))

        # sort the 2d bounding box size
        elements.sort(key=lambda x: x[1], reverse=True)

        threshold_num = ReplicatorCaptionSettings.get_object_number_threshold()
        # the element with largest bounding box
        top_elements = elements[:threshold_num]
        target_object_list = [prim_path for prim_path, area in top_elements]
        # only preserve the top {n} elemnt, for n defined in object number threshold.
        self.object_info_dict = Utils.filter_dict_by_keys(self.object_info_dict, target_object_list)
