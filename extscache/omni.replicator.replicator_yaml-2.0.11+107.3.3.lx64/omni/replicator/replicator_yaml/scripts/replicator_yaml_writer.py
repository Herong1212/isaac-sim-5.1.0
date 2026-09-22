# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import io
import json
import os
from typing import List

import numpy as np
from omni.replicator.core import AnnotatorRegistry, Writer, WriterRegistry, backends
from omni.replicator.core import functional as F
from omni.syntheticdata.scripts.SyntheticData import SyntheticData

__version__ = "0.0.1"


class ReplicatorYAMLWriterError(Exception):
    """Base exception for errors raised by parser"""

    def __init__(self, msg=None):
        if msg is None:
            msg = "A replicator YAML Writer error was encountered."
        super().__init__(msg)


def colorize_normals(data):
    """Convert normals data into colored image.

    Args:
        data (numpy.ndarray): data returned by the annotator.

    Return:
        (np.array): Data converted to uint8 RGB image.
    """

    colored_data = ((data * 0.5 + 0.5) * 255).astype(np.uint8)
    return colored_data


class ReplicatorYAMLWriter(Writer):
    """Replicator YAML writer capable of writing built-in annotator groundtruth.

    Attributes:
        output_dir:
            Output directory string that indicates the directory to save the results.
        overwrite:
            Whether to overwrite the saved file or not.
        semantic_types:
            List of semantic types to consider when filtering annotator data. Default: ["class"]
        rgb:
            Boolean value that indicates whether the rgb annotator will be activated
            and the data will be written or not. Default: False.
        bounding_box_2d_tight:
            Boolean value that indicates whether the bounding_box_2d_tight annotator will be activated
            and the data will be written or not. Default: False.
        bounding_box_2d_loose:
            Boolean value that indicates whether the bounding_box_2d_loose annotator will be activated
            and the data will be written or not. Default: False.
        semantic_segmentation:
            Boolean value that indicates whether the semantic_segmentation annotator will be activated
            and the data will be written or not. Default: False.
        instance_id_segmentation:
            Boolean value that indicates whether the instance_id_segmentation annotator will be activated
            and the data will be written or not. Default: False.
        instance_segmentation:
            Boolean value that indicates whether the instance_segmentation annotator will be activated
            and the data will be written or not. Default: False.
        distance_to_camera:
            Boolean value that indicates whether the distance_to_camera annotator will be activated
            and the data will be written or not. Default: False.
        distance_to_image_plane:
            Boolean value that indicates whether the distance_to_image_plane annotator will be activated
            and the data will be written or not. Default: False.
        bounding_box_3d:
            Boolean value that indicates whether the bounding_box_3d annotator will be activated
            and the data will be written or not. Default: False.
        occlusion:
            Boolean value that indicates whether the occlusion annotator will be activated
            and the data will be written or not. Default: False.
        normals:
            Boolean value that indicates whether the normals annotator will be activated
            and the data will be written or not. Default: False.
        motion_vectors:
            Boolean value that indicates whether the motion_vectors annotator will be activated
            and the data will be written or not. Default: False.
        camera_params:
            Boolean value that indicates whether the camera_params annotator will be activated
            and the data will be written or not. Default: False.
        pointcloud:
            Boolean value that indicates whether the pointcloud annotator will be activated
            and the data will be written or not. Default: False.
        image_output_format:
            String that indicates the format of saved RGB images. Default: "png"
        colorize_semantic_segmentation:
            If ``True``, semantic segmentation is converted to an image where semantic IDs are mapped to colors
            and saved as a uint8 4 channel PNG image. If ``False``, the output is saved as a uint32 PNG image.
            Defaults to ``True``.
        colorize_instance_id_segmentation:
            If ``True``, instance id segmentation is converted to an image where instance IDs are mapped to colors.
            and saved as a uint8 4 channel PNG image. If ``False``, the output is saved as a uint32 PNG image.
            Defaults to ``True``.
        colorize_instance_segmentation:
            If ``True``, instance segmentation is converted to an image where instance are mapped to colors.
            and saved as a uint8 4 channel PNG image. If ``False``, the output is saved as a uint32 PNG image.
            Defaults to ``True``.
        semantic_filter_predicate:
            A string specifying a semantic filter predicate as a disjunctive normal form of semantic type, labels.
            Examples :
                "typeA : labelA & !labelB | labelC , typeB: labelA ; typeC: labelD"
                "typeA : * ; * : labelA"

    Example:
        >>> import omni.replicator.core as rep
        >>> camera = rep.create.camera()
        >>> render_product = rep.create.render_product(camera, (1024, 1024))
        >>> writer = rep.WriterRegistry.get("ReplicatorYAMLWriter")
        >>> import carb
        >>> tmp_dir = carb.tokens.get_tokens_interface().resolve("${temp}/rgb")
        >>> writer.initialize(output_dir=tmp_dir, rgb=True)
        >>> writer.attach([render_product])
        >>> rep.orchestrator.run()
    """

    def __init__(
        self,
        output_dir: str,
        overwrite: bool = True,
        semantic_types: List[str] = None,
        rgb: bool = False,
        bounding_box_2d_tight: bool = False,
        bounding_box_2d_loose: bool = False,
        semantic_segmentation: bool = False,
        instance_id_segmentation: bool = False,
        instance_segmentation: bool = False,
        # background_rand: bool = False,
        distance_to_camera: bool = False,
        distance_to_image_plane: bool = False,
        bounding_box_3d: bool = False,
        occlusion: bool = False,
        normals: bool = False,
        motion_vectors: bool = False,
        camera_params: bool = False,
        pointcloud: bool = False,
        image_output_format: str = "png",
        colorize_semantic_segmentation: bool = True,
        colorize_instance_id_segmentation: bool = True,
        colorize_instance_segmentation: bool = True,
        skeleton_data: bool = False,
        semantic_filter_predicate: str = None,
    ):
        self._output_dir = output_dir
        self.overwrite = overwrite
        self._backend = backends.get("DiskBackend")
        self._backend.initialize(output_dir=output_dir)
        self.backend = self._backend
        self._frame_id = 0
        self._sequence_id = 0
        self._image_output_format = image_output_format
        self._output_data_format = {}
        self.annotators = []
        self.version = __version__

        self.colorize_semantic_segmentation = colorize_semantic_segmentation
        self.colorize_instance_id_segmentation = colorize_instance_id_segmentation
        self.colorize_instance_segmentation = colorize_instance_segmentation

        # Set the global semantic filter predicate
        if semantic_filter_predicate is not None:
            SyntheticData.Get().set_instance_mapping_semantic_filter(semantic_filter_predicate)

        # Specify the semantic types that will be included in output
        if semantic_types is not None:
            if semantic_filter_predicate is None:
                semantic_filter_predicate = ":*; ".join(semantic_types) + ":*"
            else:
                raise ValueError(
                    "`semantic_types` and `semantic_filter_predicate` are mutually exclusive. Please choose only one."
                )
        elif semantic_filter_predicate is None:
            semantic_filter_predicate = "class:*"

        # Set the global semantic filter predicate
        if semantic_filter_predicate is not None:
            SyntheticData.Get().set_instance_mapping_semantic_filter(semantic_filter_predicate)

        # RGB
        if rgb:
            self.annotators.append(AnnotatorRegistry.get_annotator("rgb"))

        # Bounding Box 2D
        if bounding_box_2d_tight:
            self.annotators.append("bounding_box_2d_tight_fast")

        if bounding_box_2d_loose:
            self.annotators.append("bounding_box_2d_loose_fast")

        # Semantic Segmentation
        if semantic_segmentation:
            self.annotators.append(
                AnnotatorRegistry.get_annotator(
                    "semantic_segmentation", init_params={"colorize": colorize_semantic_segmentation}
                )
            )

        # Instance Segmentation
        if instance_id_segmentation:
            self.annotators.append(
                AnnotatorRegistry.get_annotator(
                    "instance_id_segmentation_fast", init_params={"colorize": colorize_instance_id_segmentation}
                )
            )

        # Instance Segmentation
        if instance_segmentation:
            self.annotators.append(
                AnnotatorRegistry.get_annotator(
                    "instance_segmentation_fast", init_params={"colorize": colorize_instance_segmentation}
                )
            )
        # # Background Rand
        # if background_rand:
        #     self.annotators.append(AnnotatorRegistry.get_annotator("background_rand", init_params={"colorize": True}))

        # Depth
        if distance_to_camera:
            self.annotators.append(AnnotatorRegistry.get_annotator("distance_to_camera"))

        if distance_to_image_plane:
            self.annotators.append(AnnotatorRegistry.get_annotator("distance_to_image_plane"))

        # Bounding Box 3D
        if bounding_box_3d:
            self.annotators.append("bounding_box_3d_fast")

        # Motion Vectors
        if motion_vectors:
            self.annotators.append(AnnotatorRegistry.get_annotator("motion_vectors"))

        # Occlusion
        if occlusion:
            self.annotators.append(AnnotatorRegistry.get_annotator("occlusion"))

        # Normals
        if normals:
            self.annotators.append(AnnotatorRegistry.get_annotator("normals"))

        # Camera Params
        if camera_params:
            self.annotators.append(AnnotatorRegistry.get_annotator("camera_params"))

        # Pointcloud
        if pointcloud:
            self.annotators.append(AnnotatorRegistry.get_annotator("pointcloud"))

        # Skeleton Data
        if skeleton_data:
            self.annotators.append(AnnotatorRegistry.get_annotator("skeleton_data"))

        # Variable to record the existing max index in the directory if overwrite is True
        self.rgb_max_idx = None
        self.bounding_box_2d_tight_max_idx = None
        self.bounding_box_2d_loose_max_idx = None
        self.semantic_segmentation_max_idx = None
        self.instance_id_segmentation_max_idx = None
        self.instance_segmentation_max_idx = None
        self.distance_to_camera_max_idx = None
        self.distance_to_image_plane_max_idx = None
        self.bounding_box_3d_max_idx = None
        self.motion_vectors_max_idx = None
        self.occlusion_max_idx = None
        self.normals_max_idx = None
        self.camera_params_max_idx = None
        self.pointcloud_max_idx = None
        self.seketon_data_max_idx = None

    def write(self, data: dict):
        """Write function called from the OgnWriter node on every frame to process annotator output.

        Args:
            data: A dictionary containing the annotator data for the current frame.
        """
        # Check for on_time triggers
        # For each on_time trigger, prefix the output frame number with the trigger counts
        sequence_id = None

        self.is_sequential = False
        for trigger_name, call_count in data["trigger_outputs"].items():
            if "on_time" in trigger_name:
                sequence_id = call_count
                self.is_sequential = True

        if sequence_id != self._sequence_id:
            self._frame_id = 0
            self._sequence_id = sequence_id

        data_dir = os.path.join(self._output_dir, "data")
        os.makedirs(data_dir, exist_ok=True)

        for annotator in data.keys():
            annotator_split = annotator.split("-")
            stereo_cameras = False
            render_product_path = ""

            # multiple render_products for stereo camera.
            if len(annotator_split) == 2:
                stereo_cameras = True
                if annotator.endswith("_R"):
                    render_product_path = "right"
                elif annotator.endswith("_L"):
                    render_product_path = "left"
                else:
                    raise ReplicatorYAMLWriterError(
                        f"{len(annotator_split)} render products provided. Replicator YAML Writer only supports single or stereo camera."
                    )

            if annotator.startswith("rgb"):
                if stereo_cameras:
                    actual_dir = os.path.join(data_dir, render_product_path, "rgb")
                else:
                    actual_dir = os.path.join(data_dir, "rgb")
                self._write_rgb(data, actual_dir, annotator)

            if annotator.startswith("normals"):
                if stereo_cameras:
                    actual_dir = os.path.join(data_dir, render_product_path, "normals")
                else:
                    actual_dir = os.path.join(data_dir, "normals")
                self._write_normals(data, actual_dir, annotator)

            if annotator.startswith("distance_to_camera"):
                if stereo_cameras:
                    actual_dir = os.path.join(data_dir, render_product_path, "distance_to_camera")
                else:
                    actual_dir = os.path.join(data_dir, "distance_to_camera")
                self._write_distance_to_camera(data, actual_dir, annotator)

            if annotator.startswith("distance_to_image_plane"):
                if stereo_cameras:
                    actual_dir = os.path.join(data_dir, render_product_path, "distance_to_image_plane")
                else:
                    actual_dir = os.path.join(data_dir, "distance_to_image_plane")
                self._write_distance_to_image_plane(data, actual_dir, annotator)

            if annotator.startswith("semantic_segmentation"):
                if stereo_cameras:
                    actual_dir = os.path.join(data_dir, render_product_path, "semantic_segmentation")
                else:
                    actual_dir = os.path.join(data_dir, "semantic_segmentation")
                self._write_semantic_segmentation(data, actual_dir, annotator)

            if annotator.startswith("instance_id_segmentation"):
                if stereo_cameras:
                    actual_dir = os.path.join(data_dir, render_product_path, "instance_id_segmentation")
                else:
                    actual_dir = os.path.join(data_dir, "instance_id_segmentation")
                self._write_instance_id_segmentation(data, actual_dir, annotator)

            if annotator.startswith("instance_segmentation"):
                if stereo_cameras:
                    actual_dir = os.path.join(data_dir, render_product_path, "instance_segmentation")
                else:
                    actual_dir = os.path.join(data_dir, "instance_segmentation")
                self._write_instance_segmentation(data, actual_dir, annotator)

            if annotator.startswith("motion_vectors"):
                if stereo_cameras:
                    actual_dir = os.path.join(data_dir, render_product_path, "motion_vectors")
                else:
                    actual_dir = os.path.join(data_dir, "motion_vectors")
                self._write_motion_vectors(data, actual_dir, annotator)

            if annotator.startswith("occlusion"):
                if stereo_cameras:
                    actual_dir = os.path.join(data_dir, render_product_path, "occlusion")
                else:
                    actual_dir = os.path.join(data_dir, "occlusion")
                self._write_occlusion(data, actual_dir, annotator)

            if annotator.startswith("bounding_box_3d"):
                if stereo_cameras:
                    actual_dir = os.path.join(data_dir, render_product_path, "bounding_box_3d")
                else:
                    actual_dir = os.path.join(data_dir, "bounding_box_3d")
                self._write_bounding_box_data(data, "3d", actual_dir, annotator)

            if annotator.startswith("bounding_box_2d_loose"):
                if stereo_cameras:
                    actual_dir = os.path.join(data_dir, render_product_path, "bounding_box_2d_loose")
                else:
                    actual_dir = os.path.join(data_dir, "bounding_box_2d_loose")
                self._write_bounding_box_data(data, "2d_loose", actual_dir, annotator)

            if annotator.startswith("bounding_box_2d_tight"):
                if stereo_cameras:
                    actual_dir = os.path.join(data_dir, render_product_path, "bounding_box_2d_tight")
                else:
                    actual_dir = os.path.join(data_dir, "bounding_box_2d_tight")
                self._write_bounding_box_data(data, "2d_tight", actual_dir, annotator)

            if annotator.startswith("camera_params"):
                if stereo_cameras:
                    actual_dir = os.path.join(data_dir, render_product_path, "camera_params")
                else:
                    actual_dir = os.path.join(data_dir, "camera_params")
                self._write_camera_params(data, actual_dir, annotator)

            if annotator.startswith("pointcloud"):
                if stereo_cameras:
                    actual_dir = os.path.join(data_dir, render_product_path, "pointcloud")
                else:
                    actual_dir = os.path.join(data_dir, "pointcloud")
                self._write_pointcloud(data, actual_dir, annotator)

            if annotator.startswith("skeleton_data"):
                if stereo_cameras:
                    actual_dir = os.path.join(data_dir, render_product_path, "skeleton_data")
                else:
                    actual_dir = os.path.join(data_dir, "skeleton_data")
                self._write_skeleton(data, actual_dir, annotator)

        self._frame_id += 1

    def _write_rgb(self, data: dict, render_product_path: str, annotator: str):
        if self.rgb_max_idx is None:
            if self.overwrite:
                self.rgb_max_idx = 0
            else:
                self.rgb_max_idx = self._find_largest_index(render_product_path, "rgb", [self._image_output_format])

        if self.is_sequential:
            file_path_suffix = f"{self._sequence_id + self.rgb_max_idx}_{self._frame_id}"
        else:
            file_path_suffix = f"{self._frame_id + self.rgb_max_idx}"

        file_path = f"{render_product_path}/rgb_{file_path_suffix}.{self._image_output_format}"
        self._backend.schedule(F.write_image, data=data[annotator], path=file_path)

    def _write_normals(self, data: dict, render_product_path: str, annotator: str):
        if self.normals_max_idx is None:
            if self.overwrite:
                self.normals_max_idx = 0
            else:
                self.normals_max_idx = self._find_largest_index(
                    render_product_path, "normals", [self._image_output_format]
                )

        normals_data = data[annotator]

        if self.is_sequential:
            file_path_suffix = f"{self._sequence_id + self.normals_max_idx}_{self._frame_id}"
        else:
            file_path_suffix = f"{self._frame_id + self.normals_max_idx}"

        file_path = f"{render_product_path}/normals_{file_path_suffix}.{self._image_output_format}"

        self._backend.schedule(F.write_image, data=data[annotator], path=file_path)

        colorized_normals_data = colorize_normals(normals_data)
        self._backend.schedule(F.write_image, data=colorized_normals_data, path=file_path)

    def _write_distance_to_camera(self, data: dict, render_product_path: str, annotator: str):
        if self.distance_to_camera_max_idx is None:
            if self.overwrite:
                self.distance_to_camera_max_idx = 0
            else:
                self.distance_to_camera_max_idx = self._find_largest_index(
                    render_product_path, "distance_to_camera", ["npy"]
                )

        dist_to_cam_data = data[annotator]

        if self.is_sequential:
            file_path_suffix = f"{self._sequence_id + self.distance_to_camera_max_idx}_{self._frame_id}"
        else:
            file_path_suffix = f"{self._frame_id + self.distance_to_camera_max_idx}"

        file_path = f"{render_product_path}/distance_to_camera_{file_path_suffix}.npy"

        self._backend.schedule(F.write_np, data=dist_to_cam_data, path=file_path)

    def _write_distance_to_image_plane(self, data: dict, render_product_path: str, annotator: str):
        if self.distance_to_image_plane_max_idx is None:
            if self.overwrite:
                self.distance_to_image_plane_max_idx = 0
            else:
                self.distance_to_image_plane_max_idx = self._find_largest_index(
                    render_product_path, "distance_to_image_plane", ["npy"]
                )

        dis_to_img_plane_data = data[annotator]

        if self.is_sequential:
            file_path_suffix = f"{self._sequence_id + self.distance_to_image_plane_max_idx}_{self._frame_id}"
        else:
            file_path_suffix = f"{self._frame_id + self.distance_to_image_plane_max_idx}"

        file_path = f"{render_product_path}/distance_to_image_plane_{file_path_suffix}.npy"

        self._backend.schedule(F.write_np, data=dis_to_img_plane_data, path=file_path)

    def _write_semantic_segmentation(self, data: dict, render_product_path: str, annotator: str):
        if self.semantic_segmentation_max_idx is None:
            if self.overwrite:
                self.semantic_segmentation_max_idx = 0
            else:
                self.semantic_segmentation_max_idx = self._find_largest_index(
                    render_product_path, "semantic_segmentation", ["png", "json"]
                )

        semantic_seg_data = data[annotator]["data"]
        height, width = semantic_seg_data.shape[:2]

        if self.is_sequential:
            file_path_suffix = f"{self._sequence_id + self.semantic_segmentation_max_idx}_{self._frame_id}"
        else:
            file_path_suffix = f"{self._frame_id + self.semantic_segmentation_max_idx}"

        file_path = f"{render_product_path}/semantic_segmentation_{file_path_suffix}.png"

        if self.colorize_semantic_segmentation:
            semantic_seg_data = semantic_seg_data.view(np.uint8).reshape(height, width, -1)
            self._backend.schedule(F.write_image, data=semantic_seg_data, path=file_path)
        else:
            semantic_seg_data = semantic_seg_data.view(np.uint32).reshape(height, width)
            self._backend.schedule(F.write_image, data=semantic_seg_data, path=file_path)

        id_to_labels = data[annotator]["info"]["idToLabels"]

        file_path = f"{render_product_path}/semantic_segmentation_labels_{file_path_suffix}.json"

        self._backend.schedule(F.write_json, data={str(k): v for k, v in id_to_labels.items()}, path=file_path)

    def _write_instance_id_segmentation(self, data: dict, render_product_path: str, annotator: str):
        if self.instance_id_segmentation_max_idx is None:
            if self.overwrite:
                self.instance_id_segmentation_max_idx = 0
            else:
                self.instance_id_segmentation_max_idx = self._find_largest_index(
                    render_product_path, "instance_id_segmentation", ["png", "json"]
                )

        instance_seg_data = data[annotator]["data"]
        height, width = instance_seg_data.shape[:2]

        if self.is_sequential:
            file_path_suffix = f"{self._sequence_id + self.instance_id_segmentation_max_idx}_{self._frame_id}"
        else:
            file_path_suffix = f"{self._frame_id + self.instance_id_segmentation_max_idx}"

        file_path = f"{render_product_path}/instance_id_segmentation_{file_path_suffix}.png"

        if self.colorize_instance_id_segmentation:
            instance_seg_data = instance_seg_data.view(np.uint8).reshape(height, width, -1)
            self._backend.schedule(F.write_image, data=instance_seg_data, path=file_path)
        else:
            instance_seg_data = instance_seg_data.view(np.uint32).reshape(height, width)
            self._backend.schedule(F.write_image, data=instance_seg_data, path=file_path)

        id_to_labels = data[annotator]["info"]["idToLabels"]

        file_path = f"{render_product_path}/instance_id_segmentation_mapping_{file_path_suffix}.json"

        self._backend.schedule(F.write_json, data={str(k): v for k, v in id_to_labels.items()}, path=file_path)

    def _write_instance_segmentation(self, data: dict, render_product_path: str, annotator: str):
        if self.instance_segmentation_max_idx is None:
            if self.overwrite:
                self.instance_segmentation_max_idx = 0
            else:
                self.instance_segmentation_max_idx = self._find_largest_index(
                    render_product_path, "instance_segmentation", ["png", "json"]
                )

        instance_seg_data = data[annotator]["data"]
        height, width = instance_seg_data.shape[:2]

        if self.is_sequential:
            file_path_suffix = f"{self._sequence_id + self.instance_segmentation_max_idx}_{self._frame_id}"
        else:
            file_path_suffix = f"{self._frame_id + self.instance_segmentation_max_idx}"

        file_path = f"{render_product_path}/instance_segmentation_{file_path_suffix}.png"

        if self.colorize_instance_segmentation:
            instance_seg_data = instance_seg_data.view(np.uint8).reshape(height, width, -1)
            self._backend.schedule(F.write_image, data=instance_seg_data, path=file_path)
        else:
            instance_seg_data = instance_seg_data.view(np.uint32).reshape(height, width)
            self._backend.schedule(F.write_image, data=instance_seg_data, path=file_path)

        id_to_labels = data[annotator]["info"]["idToLabels"]

        file_path = f"{render_product_path}/instance_segmentation_mapping_{file_path_suffix}.json"

        self._backend.schedule(F.write_json, data={str(k): v for k, v in id_to_labels.items()}, path=file_path)

        id_to_semantics = data[annotator]["info"]["idToSemantics"]

        file_path = f"{render_product_path}/instance_segmentation_semantics_mapping_{file_path_suffix}.json"

        self._backend.schedule(F.write_json, data={str(k): v for k, v in id_to_semantics.items()}, path=file_path)

    def _write_motion_vectors(self, data: dict, render_product_path: str, annotator: str):
        if self.motion_vectors_max_idx is None:
            if self.overwrite:
                self.motion_vectors_max_idx = 0
            else:
                self.motion_vectors_max_idx = self._find_largest_index(render_product_path, "motion_vectors", ["npy"])

        motion_vec_data = data[annotator]

        if self.is_sequential:
            file_path_suffix = f"{self._sequence_id + self.motion_vectors_max_idx}_{self._frame_id}"
        else:
            file_path_suffix = f"{self._frame_id + self.motion_vectors_max_idx}"

        file_path = f"{render_product_path}/motion_vectors_{file_path_suffix}.npy"

        self._backend.schedule(F.write_np, data=motion_vec_data, path=file_path)

    def _write_occlusion(self, data: dict, render_product_path: str, annotator: str):
        if self.occlusion_max_idx is None:
            if self.overwrite:
                self.occlusion_max_idx = 0
            else:
                self.occlusion_max_idx = self._find_largest_index(render_product_path, "occlusion", ["npy"])

        occlusion_data = data[annotator]

        if self.is_sequential:
            file_path_suffix = f"{self._sequence_id + self.occlusion_max_idx}_{self._frame_id}"
        else:
            file_path_suffix = f"{self._frame_id + self.occlusion_max_idx}"

        file_path = f"{render_product_path}/occlusion_{file_path_suffix}.npy"

        self._backend.schedule(F.write_np, data=occlusion_data, path=file_path)

    def _write_bounding_box_data(self, data: dict, bbox_type: str, render_product_path: str, annotator: str):
        curr_bbox_max_idx = None
        if bbox_type == "2d_tight":
            if self.bounding_box_2d_tight_max_idx is None:
                if self.overwrite:
                    self.bounding_box_2d_tight_max_idx = 0
                else:
                    self.bounding_box_2d_tight_max_idx = self._find_largest_index(
                        render_product_path, "bounding_box_2d_tight", ["npy", "json"]
                    )
            curr_bbox_max_idx = self.bounding_box_2d_tight_max_idx
        elif bbox_type == "2d_loose":
            if self.bounding_box_2d_loose_max_idx is None:
                if self.overwrite:
                    self.bounding_box_2d_loose_max_idx = 0
                else:
                    self.bounding_box_2d_loose_max_idx = self._find_largest_index(
                        render_product_path, "bounding_box_2d_loose", ["npy", "json"]
                    )
            curr_bbox_max_idx = self.bounding_box_2d_loose_max_idx
        elif bbox_type == "3d":
            if self.bounding_box_3d_max_idx is None:
                if self.overwrite:
                    self.bounding_box_3d_max_idx = 0
                else:
                    self.bounding_box_3d_max_idx = self._find_largest_index(
                        render_product_path, "bounding_box_3d", ["npy", "json"]
                    )
            curr_bbox_max_idx = self.bounding_box_3d_max_idx

        bbox_data = data[annotator]["data"]
        id_to_labels = data[annotator]["info"]["idToLabels"]

        if self.is_sequential:
            file_path_suffix = f"{self._sequence_id + curr_bbox_max_idx}_{self._frame_id}"
        else:
            file_path_suffix = f"{self._frame_id + curr_bbox_max_idx}"

        file_path = f"{render_product_path}/bounding_box_{bbox_type}_{file_path_suffix}.npy"

        self._backend.schedule(F.write_np, data=bbox_data, path=file_path)

        labels_file_path = f"{render_product_path}/bounding_box_{bbox_type}_labels_{file_path_suffix}.json"

        self._backend.schedule(F.write_json, data=id_to_labels, path=labels_file_path)

    def _write_camera_params(self, data: dict, render_product_path: str, annotator: str):
        if self.camera_params_max_idx is None:
            if self.overwrite:
                self.camera_params_max_idx = 0
            else:
                self.camera_params_max_idx = self._find_largest_index(render_product_path, "camera_params", ["json"])

        camera_data = data[annotator]
        serializable_data = {}

        for key, val in camera_data.items():
            if isinstance(val, np.ndarray):
                serializable_data[key] = val.tolist()
            else:
                serializable_data[key] = val

        if self.is_sequential:
            file_path_suffix = f"{self._sequence_id + self.camera_params_max_idx}_{self._frame_id}"
        else:
            file_path_suffix = f"{self._frame_id + self.camera_params_max_idx}"

        file_path = f"{render_product_path}/camera_params_{file_path_suffix}.json"

        self._backend.schedule(F.write_json, data=serializable_data, path=file_path)

    def _write_pointcloud(self, data: dict, render_product_path: str, annotator: str):
        if self.pointcloud_max_idx is None:
            if self.overwrite:
                self.pointcloud_max_idx = 0
            else:
                self.pointcloud_max_idx = self._find_largest_index(render_product_path, "pointcloud", ["npy"])

        pointcloud_data = data[annotator]["data"]
        pointcloud_rgb = data[annotator]["info"]["pointRgb"].reshape(-1, 4)
        pointcloud_normals = data[annotator]["info"]["pointNormals"].reshape(-1, 4)
        pointcloud_semantic = data[annotator]["info"]["pointSemantic"]
        pointcloud_instance = data[annotator]["info"]["pointInstance"]

        if self.is_sequential:
            file_path_suffix = f"{self._sequence_id + self.pointcloud_max_idx}_{self._frame_id}"
        else:
            file_path_suffix = f"{self._frame_id + self.pointcloud_max_idx}"

        file_path = f"{render_product_path}/pointcloud_{file_path_suffix}.npy"

        self._backend.schedule(F.write_np, data=pointcloud_data, path=file_path)

        rgb_file_path = f"{render_product_path}/pointcloud_rgb_{file_path_suffix}.npy"

        self._backend.schedule(F.write_np, data=pointcloud_rgb, path=rgb_file_path)

        normals_file_path = f"{render_product_path}/pointcloud_normals_{file_path_suffix}.npy"

        self._backend.schedule(F.write_np, data=pointcloud_normals, path=normals_file_path)

        semantic_file_path = f"{render_product_path}/pointcloud_semantic_{file_path}.npy"

        self._backend.schedule(F.write_np, data=pointcloud_semantic, path=semantic_file_path)

        instance_file_path = f"{render_product_path}/pointcloud_instance_{file_path}.npy"
        self._backend.schedule(F.write_np, data=pointcloud_instance, path=instance_file_path)

    def _write_skeleton(self, data: dict, render_product_path: str, annotator: str):
        if self.skeleton_data_max_idx is None:
            if self.overwrite:
                self.skeleton_data_max_idx = 0
            else:
                self.skeleton_data_max_idx = self._find_largest_index(render_product_path, "skeleton_data", ["json"])

        skeleton = json.loads(data[annotator]["skeletonData"])

        if self.is_sequential:
            file_path_suffix = f"{self._sequence_id + self.skeleton_data_max_idx}_{self._frame_id}"
        else:
            file_path_suffix = f"{self._frame_id + self.skeleton_data_max_idx}"

        file_path = f"{render_product_path}/skeleton_{file_path_suffix}.json"

        serializable_data = {f"skeleton_{idx}": skel for idx, skel in enumerate(skeleton)}

        self._backend.schedule(F.write_json, data=serializable_data, path=file_path)

    def _find_largest_index(self, curr_dir, annotator_name, suffixes):
        """Helper function to find the next free index of largest existing file in a directory."""
        # if the directory doesn't exist, directly return 0.
        if not os.path.exists(curr_dir):
            return 0

        max_index = 0
        for file in os.listdir(curr_dir):
            for suffix in suffixes:
                if file.endswith(suffix) and annotator_name in file:
                    if self.is_sequential:
                        max_index = max(max_index, int(file.split(".")[0].split("_")[-2]))
                    else:
                        max_index = max(max_index, int(file.split(".")[0].split("_")[-1]))

        if max_index == 0:
            return 0
        else:
            return max_index + 1


WriterRegistry.register(ReplicatorYAMLWriter)
