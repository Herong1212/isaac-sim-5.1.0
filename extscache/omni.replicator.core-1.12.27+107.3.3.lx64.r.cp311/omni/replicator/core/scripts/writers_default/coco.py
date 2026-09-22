# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

import os
import random
import string
from datetime import datetime
from pathlib import Path
from typing import List

import numpy as np

from ...bindings._omni_replicator_core import Schema_omni_replicator_extinfo_1_0
from .. import functional as F
from ..annotators import AnnotatorRegistry
from ..backends import BackendDispatch
from ..utils import rng
from ..writers import Writer

__version__ = "0.0.1"


class CocoWriter(Writer):
    """Writer outputting data in the Coco annotation format:
    https://cocodataset.org/#format-data

    .. note::
        Development work to provide full-support is ongoing.

        - Supported: Object Detection, Stuff Segmentation, Panoptic Segmentation
        - Unsupported: Keypoints, Image Captioning, DensePose

        https://github.com/cocodataset/panopticapi

    Supported Annotations:
        - RGB
        - Object Detection
        - Semantic Segmentation

    Args:
        output_dir: Output directory to which Coco annotations will be saved.
        semantic_types: List of semantic types to consider.
            If ``None``, only consider semantic types ``['class', 'coco', 'stuff', 'thing']``.
        coco_categories: Dictionary of COCO compatible labels. Required keys: ``name``, ``id``.
            If ``None``, will use the built-in COCO labels from https://cocodataset.org
            ex: ``{"semantic_name": 'name': 'semantic_name', 'id': 1234, 'supercategory': 'super_name', 'color': (03, 23, 15), 'isthing': 1}``
        s3_bucket:
            The S3 Bucket name to write to. If not provided, disk backend will be used instead. Default: ``None``.
            This backend requires that AWS credentials are set up in ``~/.aws/credentials``.
            See https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration
        s3_region:
            If provided, this is the region the S3 bucket will be set to. Default: ``us-east-1``
        s3_endpoint:
            If provided, this endpoint URL will be used instead of the default.
        dataset_id:
            An identifier to be added to the output file names.  If None, will use a random string
        image_output_format:
            Image filetype to write to disk, default is PNG
        coco_license_info:
            Dictionary of license information to add. ``[{"id": int, "name": str, "url": str,},]``.
            See: https://cocodataset.org/#format-data
    """

    def __init__(
        self,
        output_dir: str,
        semantic_types: List[str] = None,
        coco_categories: dict = None,
        s3_bucket: str = None,
        s3_region: str = None,
        s3_endpoint: str = None,
        dataset_id: str = None,
        frame_padding: int = 4,
        image_output_format: str = "png",
        coco_license_info: List[dict] = None,
        **kwargs,
    ):
        self.__dict__.update(locals())
        self.__dict__.update(kwargs)
        self.version = __version__
        self._telemetry = Schema_omni_replicator_extinfo_1_0()
        self._frame_id = 0
        self._sequence_id = 0
        self._image_output_format = image_output_format
        self._frame_padding = frame_padding
        self._num_annotations = 0
        self._used_categories = {}

        self.output_dir = output_dir
        self.data_structure = "renderProduct"
        if coco_categories is None:
            self.label_dict = COCO_LABELS
        else:
            self.label_dict = coco_categories
            if "other" not in self.label_dict:
                self.label_dict["other"] = COCO_LABELS["other"]
            if "unlabelled" not in self.label_dict:
                self.label_dict["unlabelled"] = COCO_LABELS["unlabelled"]
            if "background" not in self.label_dict:
                self.label_dict["background"] = COCO_LABELS["background"]

        if s3_bucket:
            # Create S3 Backend
            self.backend = BackendDispatch(
                output_dir=output_dir,  # Maintains previous behaviour
                key_prefix=output_dir,
                bucket=s3_bucket,
                region=s3_region,
                endpoint_url=s3_endpoint,
                overwrite=False,
            )
        else:
            self.backend = BackendDispatch(output_dir=output_dir, overwrite=False)

        self._date = datetime.now(datetime.now().astimezone().tzinfo)
        self.year = self._date.year

        if semantic_types is None:
            self.semantic_types = ["class", "coco", "stuff", "thing"]
        else:
            self.semantic_types = semantic_types
        if dataset_id is None:
            # Using global seed will also use the same output filename
            random.seed(rng.get_global_seed())
            # Will generate random string of characters
            self.dataset_id = "".join(random.choices(string.ascii_lowercase, k=8))

        # Annotators #
        self.annotators.append(AnnotatorRegistry.get_annotator("rgb"))
        self.annotators.append(
            AnnotatorRegistry.get_annotator(
                "bounding_box_2d_tight_fast", init_params={"semanticTypes": self.semantic_types}
            )
        )
        self.annotators.append(
            AnnotatorRegistry.get_annotator("semantic_segmentation", init_params={"semanticTypes": self.semantic_types})
        )

        # COCO Annotation JSON file
        self.coco_annotation_dict = {}
        self._init_coco_annotation()
        if coco_license_info is None:
            self.coco_annotation_dict["licenses"] = []
        else:
            self.coco_annotation_dict["licenses"] = coco_license_info
        # Write initial annotation JSON (in case job doesn't complete)
        self._write_coco_annotation_file()

    def _init_coco_annotation(self):
        self.coco_annotation_dict["info"] = {
            "description": "COCO dataset created with Omniverse Replicator",
            "url": "https://cocodataset.org",
            "version": f"{self.version}",
            "year": self.year,
            "date_created": self._date.isoformat(),
            "contributor": "",  # TODO: pass-parameter for this?
        }
        self.coco_annotation_dict["images"] = []
        self.coco_annotation_dict["annotations"] = []
        self.coco_annotation_dict["categories"] = []
        self.coco_annotation_output_path = os.path.join(f"coco_annotations_{self.dataset_id}.json")

    def _write_coco_annotation_file(self):
        # write only the labels actually used in the dataset to disk (saves on space)
        self.coco_annotation_dict["categories"] = list(self._used_categories.values())

        annotations = {str(k): v for k, v in self.coco_annotation_dict.items()}
        self.backend.schedule(
            F.write_json, self.coco_annotation_output_path, annotations, indent=2, check_circular=False
        )

    def on_final_frame(self):
        self._write_coco_annotation_file()

    def write(self, data: dict):
        """Write function called from the OgnWriter node on every frame to process annotator output.

        Args:
            data: A dictionary containing the annotator data for the current frame.
        """
        # Check for on_time triggers
        # For each on_time trigger, prefix the output frame number with the trigger counts
        sequence_id = ""
        for trigger_name, call_count in data["trigger_outputs"].items():
            if "on_time" in trigger_name:
                sequence_id = f"{call_count}_{sequence_id}_"
        if sequence_id != self._sequence_id:
            self._frame_id = 0
            self._sequence_id = sequence_id

        # Loop through all annotators and render products
        for render_product_name, rp_data_dict in data["renderProducts"].items():

            camera_name = rp_data_dict["camera"][1:].replace("Replicator/", "").replace("/", "-").replace("_", "-")
            rgb_path = self._write_rgb(render_product_name, camera_name, rp_data_dict["rgb"])
            image_id = len(self.coco_annotation_dict["images"])
            image_dict = {
                "file_name": Path(rgb_path).as_posix(),
                "id": image_id,
                "height": int(rp_data_dict["resolution"][1]),
                "width": int(rp_data_dict["resolution"][0]),
                "license": 0,
                "date_captured": self._date.isoformat(),
                "flicker_url": "",
            }
            self.coco_annotation_dict["images"].append(image_dict)
            self._write_annotation_segments(rp_data_dict["bounding_box_2d_tight_fast"], image_id)
            seg_path = self._write_segmentation_image(
                render_product_name, camera_name, rp_data_dict["semantic_segmentation"]
            )

        self._frame_id += 1
        if self._frame_id % 25 == 0:
            # periodically write the annotation file to avoid data loss
            self._write_coco_annotation_file()

    def _write_rgb(self, render_product, camera_name, annotator_dict: dict):
        output_path = render_product + os.path.sep
        file_path = f"{output_path}rgb_{camera_name}_{self.dataset_id}.{self._sequence_id}{self._frame_id:0{self._frame_padding}}.{self._image_output_format}"
        self.backend.schedule(F.write_image, data=annotator_dict["data"], path=file_path)
        return file_path

    def _write_annotation_segments(self, annotator_dict, image_id):
        bbox_data = annotator_dict["data"]
        bbox_id2labels = annotator_dict["idToLabels"]

        image_bboxes = []

        for cur_bbox in bbox_data:
            semantic_id = cur_bbox["semanticId"]
            x_min = int(cur_bbox["x_min"])
            x_max = int(cur_bbox["x_max"])
            y_min = int(cur_bbox["y_min"])
            y_max = int(cur_bbox["y_max"])

            # [ x, y, width, height]
            coco_bbox = [x_min, y_min, x_max - x_min, y_max - y_min]
            bbox_semantic_dict = bbox_id2labels.get(semantic_id)

            category_id = None
            for label in list(bbox_semantic_dict.values()):
                # Skipping bbox labels that don't have categories
                if label not in self.label_dict:
                    continue
                category_id = self.label_dict[label]["id"]
                self._used_categories.setdefault(label, self.label_dict[label])
            if category_id is None:
                category_id = self.label_dict["other"]["id"]
                self._used_categories.setdefault("other", self.label_dict["other"])
            annotation_entry = {
                "id": self._num_annotations,
                "image_id": image_id,
                "bbox": coco_bbox,
                "area": float((x_max - x_min) * (y_max - y_min)),
                "bbox_mode": 1,
                "category_id": int(category_id),
                "iscrowd": 0,  # TODO: Support cluster of objects
                "segmentation": [],  # TODO: Supports RLE and list of vertices segmentation
            }
            image_bboxes.append(annotation_entry)
            self._num_annotations += 1

        self.coco_annotation_dict["annotations"] += image_bboxes

    def _write_segmentation_image(self, render_product, camera_name, annotator_dict: dict):
        output_path = render_product + os.path.sep
        img_file_path = f"{output_path}panoptic_{camera_name}_{self.dataset_id}.{self._sequence_id}{self._frame_id:0{self._frame_padding}}.{self._image_output_format}"
        id_to_labels = annotator_dict["idToLabels"]  # Labels from renderer : '0': {'class': 'background'}

        # Create blank image
        colored_segmentation = np.zeros(
            (annotator_dict["data"].shape[0], annotator_dict["data"].shape[1], 3), dtype=np.uint8
        )

        for render_id, semantic_pair in id_to_labels.items():
            # '(0, 0, 0, 0)': {'class': 'background'}.
            for sem_label in semantic_pair.values():
                try:
                    label_info = self.label_dict[sem_label]
                except KeyError:
                    label_info = self.label_dict["other"]

                colored_segmentation[annotator_dict["data"] == int(render_id)] = label_info["color"]

        # Write colorized image to disk
        self.backend.schedule(F.write_image, data=colored_segmentation, path=img_file_path)

        return img_file_path


# TODO
def colorize_coco(data_dict, coco_categories):
    return


"""
https://cocodataset.org/#stuff-eval
https://cocodataset.org/#panoptic-eval
https://raw.githubusercontent.com/cocodataset/panopticapi/master/panoptic_coco_categories.json

1-91 thing categories (80 total)
92-182 original stuff categories (36 total)
183-200 merged stuff categories (17 total)

The following new stuff categories were created by merging old stuff categories:
tree-merged: branch, tree, bush, leaves
fence-merged: cage, fence, railing
ceiling-merged: ceiling-tile, ceiling-other
sky-other-merged: clouds, sky-other, fog
cabinet-merged: cupboard, cabinet
table-merged: desk-stuff, table
floor-other-merged: floor-marble, floor-other, floor-tile
pavement-merged: floor-stone, pavement
mountain-merged: hill, mountain
grass-merged: moss, grass, straw
dirt-merged: mud, dirt
paper-merged: napkin, paper
food-other-merged: salad, vegetable, food-other
building-other-merged: skyscraper, building-other
rock-merged: stone, rock
wall-other-merged: wall-other, wall-concrete, wall-panel
rug-merged: mat, rug, carpet

The following stuff categories were removed (their pixels are set to void):
furniture-other, metal, plastic, solid-other, structural-other, waterdrops, textile-other, cloth, clothes, plant-other, wood, ground-other
Note that when you load the PNG as an RGB image, you will need to compute the ids via ids=R+G*256+B*256^2.
"""
# fmt: off
COCO_LABELS = {
    'unlabelled': {'name': 'unlabelled', 'id': 0, 'supercategory': 'unlabelled', 'color': (0, 0, 0), 'isthing': 0},
    'person': {'name': 'person', 'id': 1, 'supercategory': 'person', 'color': (220, 20, 60), 'isthing': 1},
    'bicycle': {'name': 'bicycle', 'id': 2, 'supercategory': 'vehicle', 'color': (119, 11, 32), 'isthing': 1},
    'car': {'name': 'car', 'id': 3, 'supercategory': 'vehicle', 'color': (0, 0, 142), 'isthing': 1},
    'motorcycle': {'name': 'motorcycle', 'id': 4, 'supercategory': 'vehicle', 'color': (0, 0, 230), 'isthing': 1},
    'airplane': {'name': 'airplane', 'id': 5, 'supercategory': 'vehicle', 'color': (106, 0, 228), 'isthing': 1},
    'bus': {'name': 'bus', 'id': 6, 'supercategory': 'vehicle', 'color': (0, 60, 100), 'isthing': 1},
    'train': {'name': 'train', 'id': 7, 'supercategory': 'vehicle', 'color': (0, 80, 100), 'isthing': 1},
    'truck': {'name': 'truck', 'id': 8, 'supercategory': 'vehicle', 'color': (0, 0, 70), 'isthing': 1},
    'boat': {'name': 'boat', 'id': 9, 'supercategory': 'vehicle', 'color': (0, 0, 192), 'isthing': 1},
    'traffic light': {'name': 'traffic light', 'id': 10, 'supercategory': 'outdoor', 'color': (250, 170, 30), 'isthing': 1},
    'fire hydrant': {'name': 'fire hydrant', 'id': 11, 'supercategory': 'outdoor', 'color': (100, 170, 30), 'isthing': 1},
    'street sign': {'name': 'street sign', 'id': 12, 'supercategory': 'outdoor', 'color': (0, 0, 0), 'isthing': 1},
    'stop sign': {'name': 'stop sign', 'id': 13, 'supercategory': 'outdoor', 'color': (220, 220, 0), 'isthing': 1},
    'parking meter': {'name': 'parking meter', 'id': 14, 'supercategory': 'outdoor', 'color': (175, 116, 175), 'isthing': 1},
    'bench': {'name': 'bench', 'id': 15, 'supercategory': 'outdoor', 'color': (250, 0, 30), 'isthing': 1},
    'bird': {'name': 'bird', 'id': 16, 'supercategory': 'animal', 'color': (165, 42, 42), 'isthing': 1},
    'cat': {'name': 'cat', 'id': 17, 'supercategory': 'animal', 'color': (255, 77, 255), 'isthing': 1},
    'dog': {'name': 'dog', 'id': 18, 'supercategory': 'animal', 'color': (0, 226, 252), 'isthing': 1},
    'horse': {'name': 'horse', 'id': 19, 'supercategory': 'animal', 'color': (182, 182, 255), 'isthing': 1},
    'sheep': {'name': 'sheep', 'id': 20, 'supercategory': 'animal', 'color': (0, 82, 0), 'isthing': 1},
    'cow': {'name': 'cow', 'id': 21, 'supercategory': 'animal', 'color': (120, 166, 157), 'isthing': 1},
    'elephant': {'name': 'elephant', 'id': 22, 'supercategory': 'animal', 'color': (110, 76, 0), 'isthing': 1},
    'bear': {'name': 'bear', 'id': 23, 'supercategory': 'animal', 'color': (174, 57, 255), 'isthing': 1},
    'zebra': {'name': 'zebra', 'id': 24, 'supercategory': 'animal', 'color': (199, 100, 0), 'isthing': 1},
    'giraffe': {'name': 'giraffe', 'id': 25, 'supercategory': 'animal', 'color': (72, 0, 118), 'isthing': 1},
    'hat': {'name': 'hat', 'id': 26, 'supercategory': 'accessory', 'color': (0, 0, 0), 'isthing': 1},
    'backpack': {'name': 'backpack', 'id': 27, 'supercategory': 'accessory', 'color': (255, 179, 240), 'isthing': 1},
    'umbrella': {'name': 'umbrella', 'id': 28, 'supercategory': 'accessory', 'color': (0, 125, 92), 'isthing': 1},
    'shoe': {'name': 'shoe', 'id': 29, 'supercategory': 'accessory', 'color': (0, 0, 0), 'isthing': 1},
    'eye glasses': {'name': 'eye glasses', 'id': 30, 'supercategory': 'accessory', 'color': (0, 0, 0), 'isthing': 1},
    'handbag': {'name': 'handbag', 'id': 31, 'supercategory': 'accessory', 'color': (209, 0, 151), 'isthing': 1},
    'tie': {'name': 'tie', 'id': 32, 'supercategory': 'accessory', 'color': (188, 208, 182), 'isthing': 1},
    'suitcase': {'name': 'suitcase', 'id': 33, 'supercategory': 'accessory', 'color': (0, 220, 176), 'isthing': 1},
    'frisbee': {'name': 'frisbee', 'id': 34, 'supercategory': 'sports', 'color': (255, 99, 164), 'isthing': 1},
    'skis': {'name': 'skis', 'id': 35, 'supercategory': 'sports', 'color': (92, 0, 73), 'isthing': 1},
    'snowboard': {'name': 'snowboard', 'id': 36, 'supercategory': 'sports', 'color': (133, 129, 255), 'isthing': 1},
    'sports ball': {'name': 'sports ball', 'id': 37, 'supercategory': 'sports', 'color': (78, 180, 255), 'isthing': 1},
    'kite': {'name': 'kite', 'id': 38, 'supercategory': 'sports', 'color': (0, 228, 0), 'isthing': 1},
    'baseball bat': {'name': 'baseball bat', 'id': 39, 'supercategory': 'sports', 'color': (174, 255, 243), 'isthing': 1},
    'baseball glove': {'name': 'baseball glove', 'id': 40, 'supercategory': 'sports', 'color': (45, 89, 255), 'isthing': 1},
    'skateboard': {'name': 'skateboard', 'id': 41, 'supercategory': 'sports', 'color': (134, 134, 103), 'isthing': 1},
    'surfboard': {'name': 'surfboard', 'id': 42, 'supercategory': 'sports', 'color': (145, 148, 174), 'isthing': 1},
    'tennis racket': {'name': 'tennis racket', 'id': 43, 'supercategory': 'sports', 'color': (255, 208, 186), 'isthing': 1},
    'bottle': {'name': 'bottle', 'id': 44, 'supercategory': 'kitchen', 'color': (197, 226, 255), 'isthing': 1},
    'plate': {'name': 'plate', 'id': 45, 'supercategory': 'kitchen', 'color': (0, 0, 0), 'isthing': 1},
    'wine glass': {'name': 'wine glass', 'id': 46, 'supercategory': 'kitchen', 'color': (171, 134, 1), 'isthing': 1},
    'cup': {'name': 'cup', 'id': 47, 'supercategory': 'kitchen', 'color': (109, 63, 54), 'isthing': 1},
    'fork': {'name': 'fork', 'id': 48, 'supercategory': 'kitchen', 'color': (207, 138, 255), 'isthing': 1},
    'knife': {'name': 'knife', 'id': 49, 'supercategory': 'kitchen', 'color': (151, 0, 95), 'isthing': 1},
    'spoon': {'name': 'spoon', 'id': 50, 'supercategory': 'kitchen', 'color': (9, 80, 61), 'isthing': 1},
    'bowl': {'name': 'bowl', 'id': 51, 'supercategory': 'kitchen', 'color': (84, 105, 51), 'isthing': 1},
    'banana': {'name': 'banana', 'id': 52, 'supercategory': 'food', 'color': (74, 65, 105), 'isthing': 1},
    'apple': {'name': 'apple', 'id': 53, 'supercategory': 'food', 'color': (166, 196, 102), 'isthing': 1},
    'sandwich': {'name': 'sandwich', 'id': 54, 'supercategory': 'food', 'color': (208, 195, 210), 'isthing': 1},
    'orange': {'name': 'orange', 'id': 55, 'supercategory': 'food', 'color': (255, 109, 65), 'isthing': 1},
    'broccoli': {'name': 'broccoli', 'id': 56, 'supercategory': 'food', 'color': (0, 143, 149), 'isthing': 1},
    'carrot': {'name': 'carrot', 'id': 57, 'supercategory': 'food', 'color': (179, 0, 194), 'isthing': 1},
    'hot dog': {'name': 'hot dog', 'id': 58, 'supercategory': 'food', 'color': (209, 99, 106), 'isthing': 1},
    'pizza': {'name': 'pizza', 'id': 59, 'supercategory': 'food', 'color': (5, 121, 0), 'isthing': 1},
    'donut': {'name': 'donut', 'id': 60, 'supercategory': 'food', 'color': (227, 255, 205), 'isthing': 1},
    'cake': {'name': 'cake', 'id': 61, 'supercategory': 'food', 'color': (147, 186, 208), 'isthing': 1},
    'chair': {'name': 'chair', 'id': 62, 'supercategory': 'furniture', 'color': (153, 69, 1), 'isthing': 1},
    'couch': {'name': 'couch', 'id': 63, 'supercategory': 'furniture', 'color': (3, 95, 161), 'isthing': 1},
    'potted plant': {'name': 'potted plant', 'id': 64, 'supercategory': 'furniture', 'color': (163, 255, 0), 'isthing': 1},
    'bed': {'name': 'bed', 'id': 65, 'supercategory': 'furniture', 'color': (119, 0, 170), 'isthing': 1},
    'mirror': {'name': 'mirror', 'id': 133, 'supercategory': 'furniture-stuff', 'color': (154, 208, 0), 'isthing': 0},
    'dining table': {'name': 'dining table', 'id': 67, 'supercategory': 'furniture', 'color': (0, 182, 199), 'isthing': 1},
    'window': {'name': 'window', 'id': 68, 'supercategory': 'window', 'color': (255, 73, 97), 'isthing': 1},
    'desk': {'name': 'desk', 'id': 110, 'supercategory': 'furniture-stuff', 'color': (209, 226, 140), 'isthing': 0},
    'toilet': {'name': 'toilet', 'id': 70, 'supercategory': 'furniture', 'color': (0, 165, 120), 'isthing': 1},
    'door': {'name': 'door', 'id': 71, 'supercategory': 'furniture-stuff', 'color': (0, 0, 0), 'isthing': 1},
    'tv': {'name': 'tv', 'id': 72, 'supercategory': 'electronic', 'color': (183, 130, 88), 'isthing': 1},
    'laptop': {'name': 'laptop', 'id': 73, 'supercategory': 'electronic', 'color': (95, 32, 0), 'isthing': 1},
    'mouse': {'name': 'mouse', 'id': 74, 'supercategory': 'electronic', 'color': (130, 114, 135), 'isthing': 1},
    'remote': {'name': 'remote', 'id': 75, 'supercategory': 'electronic', 'color': (110, 129, 133), 'isthing': 1},
    'keyboard': {'name': 'keyboard', 'id': 76, 'supercategory': 'electronic', 'color': (166, 74, 118), 'isthing': 1},
    'cell phone': {'name': 'cell phone', 'id': 77, 'supercategory': 'electronic', 'color': (219, 142, 185), 'isthing': 1},
    'microwave': {'name': 'microwave', 'id': 78, 'supercategory': 'appliance', 'color': (79, 210, 114), 'isthing': 1},
    'oven': {'name': 'oven', 'id': 79, 'supercategory': 'appliance', 'color': (178, 90, 62), 'isthing': 1},
    'toaster': {'name': 'toaster', 'id': 80, 'supercategory': 'appliance', 'color': (65, 70, 15), 'isthing': 1},
    'sink': {'name': 'sink', 'id': 81, 'supercategory': 'appliance', 'color': (127, 167, 115), 'isthing': 1},
    'refrigerator': {'name': 'refrigerator', 'id': 82, 'supercategory': 'appliance', 'color': (59, 105, 106), 'isthing': 1},
    'blender': {'name': 'blender', 'id': 83, 'supercategory': 'appliance', 'color': (0, 0, 0), 'isthing': 1},
    'book': {'name': 'book', 'id': 84, 'supercategory': 'indoor', 'color': (142, 108, 45), 'isthing': 1},
    'clock': {'name': 'clock', 'id': 85, 'supercategory': 'indoor', 'color': (196, 172, 0), 'isthing': 1},
    'vase': {'name': 'vase', 'id': 86, 'supercategory': 'indoor', 'color': (95, 54, 80), 'isthing': 1},
    'scissors': {'name': 'scissors', 'id': 87, 'supercategory': 'indoor', 'color': (128, 76, 255), 'isthing': 1},
    'teddy bear': {'name': 'teddy bear', 'id': 88, 'supercategory': 'indoor', 'color': (201, 57, 1), 'isthing': 1},
    'hair drier': {'name': 'hair drier', 'id': 89, 'supercategory': 'indoor', 'color': (246, 0, 122), 'isthing': 1},
    'toothbrush': {'name': 'toothbrush', 'id': 90, 'supercategory': 'indoor', 'color': (191, 162, 208), 'isthing': 1},
    'hair brush': {'name': 'hair brush', 'id': 91, 'supercategory': 'indoor', 'color': (0, 0, 0), 'isthing': 1},
    'banner': {'name': 'banner', 'id': 92, 'supercategory': 'textile', 'color': (255, 255, 128), 'isthing': 0},
    'blanket': {'name': 'blanket', 'id': 93, 'supercategory': 'textile', 'color': (147, 211, 203), 'isthing': 0},
    'branch': {'name': 'branch', 'id': 94, 'supercategory': 'plant', 'color': (0, 0, 0), 'isthing': 0},
    'bridge': {'name': 'bridge', 'id': 95, 'supercategory': 'building', 'color': (150, 100, 100), 'isthing': 0},
    'building-other': {'name': 'building-other', 'id': 96, 'supercategory': 'building', 'color': (116, 112, 0), 'isthing': 0},
    'bush': {'name': 'bush', 'id': 97, 'supercategory': 'plant', 'color': (0, 0, 0), 'isthing': 0},
    'cabinet': {'name': 'cabinet', 'id': 98, 'supercategory': 'furniture-stuff', 'color': (134, 199, 156), 'isthing': 0},
    'cage': {'name': 'cage', 'id': 99, 'supercategory': 'plant', 'color': (0, 0, 0), 'isthing': 0},
    'cardboard': {'name': 'cardboard', 'id': 100, 'supercategory': 'raw-material', 'color': (168, 171, 172), 'isthing': 0},
    'carpet': {'name': 'carpet', 'id': 101, 'supercategory': 'floor', 'color': (96, 36, 108), 'isthing': 0},
    'ceiling-other': {'name': 'ceiling-other', 'id': 102, 'supercategory': 'ceiling', 'color': (146, 139, 141), 'isthing': 0},
    'ceiling-tile': {'name': 'ceiling-tile', 'id': 103, 'supercategory': 'ceiling', 'color': (146, 139, 141), 'isthing': 0},
    'cloth': {'name': 'cloth', 'id': 104, 'supercategory': 'textile', 'color': (0, 0, 0), 'isthing': 0},
    'clothes': {'name': 'clothes', 'id': 105, 'supercategory': 'textile', 'color': (0, 0, 0), 'isthing': 0},
    'clouds': {'name': 'clouds', 'id': 106, 'supercategory': 'sky', 'color': (70, 130, 180), 'isthing': 0},
    'counter': {'name': 'counter', 'id': 107, 'supercategory': 'furniture-stuff', 'color': (146, 112, 198), 'isthing': 0},
    'cupboard': {'name': 'cupboard', 'id': 108, 'supercategory': 'furniture-stuff', 'color': (0, 0, 0), 'isthing': 0},
    'curtain': {'name': 'curtain', 'id': 109, 'supercategory': 'textile', 'color': (210, 170, 100), 'isthing': 0},
    'dirt': {'name': 'dirt', 'id': 111, 'supercategory': 'ground', 'color': (208, 229, 228), 'isthing': 0},
    'door-stuff': {'name': 'door-stuff', 'id': 112, 'supercategory': 'furniture-stuff', 'color': (92, 136, 89), 'isthing': 0},
    'fence': {'name': 'fence', 'id': 113, 'supercategory': 'structural', 'color': (190, 153, 153), 'isthing': 0},
    'floor-marble': {'name': 'floor-marble', 'id': 114, 'supercategory': 'floor', 'color': (96, 36, 108), 'isthing': 0},
    'floor-other': {'name': 'floor-other', 'id': 115, 'supercategory': 'floor', 'color': (96, 36, 108), 'isthing': 0},
    'floor-stone': {'name': 'floor-stone', 'id': 116, 'supercategory': 'floor', 'color': (96, 36, 108), 'isthing': 0},
    'floor-tile': {'name': 'floor-tile', 'id': 117, 'supercategory': 'floor', 'color': (96, 36, 108), 'isthing': 0},
    'floor-wood': {'name': 'floor-wood', 'id': 118, 'supercategory': 'floor', 'color': (218, 88, 184), 'isthing': 0},
    'flower': {'name': 'flower', 'id': 119, 'supercategory': 'plant', 'color': (241, 129, 0), 'isthing': 0},
    'fog': {'name': 'fog', 'id': 120, 'supercategory': 'water', 'color': (0, 0, 0), 'isthing': 0},
    'food-other': {'name': 'food-other', 'id': 121, 'supercategory': 'food-stuff', 'color': (152, 161, 64), 'isthing': 0},
    'fruit': {'name': 'fruit', 'id': 122, 'supercategory': 'food-stuff', 'color': (217, 17, 255), 'isthing': 0},
    'furniture-other': {'name': 'furniture-other', 'id': 123, 'supercategory': 'furniture-stuff', 'color': (104, 84, 109), 'isthing': 0},
    'grass': {'name': 'grass', 'id': 124, 'supercategory': 'plant', 'color': (152, 251, 152), 'isthing': 0},
    'gravel': {'name': 'gravel', 'id': 125, 'supercategory': 'ground', 'color': (124, 74, 181), 'isthing': 0},
    'ground-other': {'name': 'ground-other', 'id': 126, 'supercategory': 'ground', 'color': (0, 0, 0), 'isthing': 0},
    'hill': {'name': 'hill', 'id': 127, 'supercategory': 'solid', 'color': (0, 0, 0), 'isthing': 0},
    'house': {'name': 'house', 'id': 128, 'supercategory': 'building', 'color': (70, 70, 70), 'isthing': 0},
    'leaves': {'name': 'leaves', 'id': 129, 'supercategory': 'plant', 'color': (0, 0, 0), 'isthing': 0},
    'light': {'name': 'light', 'id': 130, 'supercategory': 'furniture-stuff', 'color': (255, 228, 255), 'isthing': 0},
    'mat': {'name': 'mat', 'id': 131, 'supercategory': 'textile', 'color': (0, 0, 0), 'isthing': 0},
    'metal': {'name': 'metal', 'id': 132, 'supercategory': 'raw-material', 'color': (0, 0, 0), 'isthing': 0},
    'moss': {'name': 'moss', 'id': 134, 'supercategory': 'plant', 'color': (0, 0, 0), 'isthing': 0},
    'mountain': {'name': 'mountain', 'id': 135, 'supercategory': 'solid', 'color': (0, 0, 0), 'isthing': 0},
    'mud': {'name': 'mud', 'id': 136, 'supercategory': 'ground', 'color': (0, 0, 0), 'isthing': 0},
    'napkin': {'name': 'napkin', 'id': 137, 'supercategory': 'textile', 'color': (0, 0, 0), 'isthing': 0},
    'net': {'name': 'net', 'id': 138, 'supercategory': 'structural', 'color': (193, 0, 92), 'isthing': 0},
    'paper': {'name': 'paper', 'id': 139, 'supercategory': 'raw-material', 'color': (0, 0, 0), 'isthing': 0},
    'pavement': {'name': 'pavement', 'id': 140, 'supercategory': 'ground', 'color': (0, 0, 0), 'isthing': 0},
    'pillow': {'name': 'pillow', 'id': 141, 'supercategory': 'textile', 'color': (76, 91, 113), 'isthing': 0},
    'plant-other': {'name': 'plant-other', 'id': 142, 'supercategory': 'plant', 'color': (0, 0, 0), 'isthing': 0},
    'plastic': {'name': 'plastic', 'id': 143, 'supercategory': 'raw-material', 'color': (0, 0, 0), 'isthing': 0},
    'platform': {'name': 'platform', 'id': 144, 'supercategory': 'ground', 'color': (255, 180, 195), 'isthing': 0},
    'playingfield': {'name': 'playingfield', 'id': 145, 'supercategory': 'ground', 'color': (106, 154, 176), 'isthing': 0},
    'railing': {'name': 'railing', 'id': 146, 'supercategory': 'plant', 'color': (0, 0, 0), 'isthing': 0},
    'railroad': {'name': 'railroad', 'id': 147, 'supercategory': 'ground', 'color': (230, 150, 140), 'isthing': 0},
    'river': {'name': 'river', 'id': 148, 'supercategory': 'water', 'color': (60, 143, 255), 'isthing': 0},
    'road': {'name': 'road', 'id': 149, 'supercategory': 'ground', 'color': (128, 64, 128), 'isthing': 0},
    'rock': {'name': 'rock', 'id': 150, 'supercategory': 'solid', 'color': (0, 114, 143), 'isthing': 0},
    'roof': {'name': 'roof', 'id': 151, 'supercategory': 'building', 'color': (92, 82, 55), 'isthing': 0},
    'rug': {'name': 'rug', 'id': 152, 'supercategory': 'textile', 'color': (250, 141, 255), 'isthing': 0},
    'salad': {'name': 'salad', 'id': 153, 'supercategory': 'food-stuff', 'color': (0, 0, 0), 'isthing': 0},
    'sand': {'name': 'sand', 'id': 154, 'supercategory': 'ground', 'color': (254, 212, 124), 'isthing': 0},
    'sea': {'name': 'sea', 'id': 155, 'supercategory': 'water', 'color': (73, 77, 174), 'isthing': 0},
    'shelf': {'name': 'shelf', 'id': 156, 'supercategory': 'furniture-stuff', 'color': (255, 160, 98), 'isthing': 0},
    'sky-other': {'name': 'sky-other', 'id': 157, 'supercategory': 'sky', 'color': (70, 130, 180), 'isthing': 0},
    'skyscraper': {'name': 'skyscraper', 'id': 158, 'supercategory': 'building', 'color': (0, 0, 0), 'isthing': 0},
    'snow': {'name': 'snow', 'id': 159, 'supercategory': 'ground', 'color': (255, 255, 255), 'isthing': 0},
    'solid-other': {'name': 'solid-other', 'id': 160, 'supercategory': 'solid', 'color': (0, 0, 0), 'isthing': 0},
    'stairs': {'name': 'stairs', 'id': 161, 'supercategory': 'furniture-stuff', 'color': (104, 84, 109), 'isthing': 0},
    'stone': {'name': 'stone', 'id': 162, 'supercategory': 'solid', 'color': (0, 0, 0), 'isthing': 0},
    'straw': {'name': 'straw', 'id': 163, 'supercategory': 'plant', 'color': (0, 0, 0), 'isthing': 0},
    'structural-other': {'name': 'structural-other', 'id': 164, 'supercategory': 'plant', 'color': (0, 0, 0), 'isthing': 0},
    'table': {'name': 'table', 'id': 165, 'supercategory': 'furniture-stuff', 'color': (209, 226, 140), 'isthing': 0},
    'tent': {'name': 'tent', 'id': 166, 'supercategory': 'building', 'color': (169, 164, 131), 'isthing': 0},
    'textile-other': {'name': 'textile-other', 'id': 167, 'supercategory': 'textile', 'color': (0, 0, 0), 'isthing': 0},
    'towel': {'name': 'towel', 'id': 168, 'supercategory': 'textile', 'color': (225, 199, 255), 'isthing': 0},
    'tree': {'name': 'tree', 'id': 169, 'supercategory': 'plant', 'color': (107, 142, 35), 'isthing': 0},
    'vegetable': {'name': 'vegetable', 'id': 170, 'supercategory': 'food-stuff', 'color': (0, 0, 0), 'isthing': 0},
    'wall-brick': {'name': 'wall-brick', 'id': 171, 'supercategory': 'wall', 'color': (137, 54, 74), 'isthing': 0},
    'wall-concrete': {'name': 'wall-concrete', 'id': 172, 'supercategory': 'wall', 'color': (102, 102, 156), 'isthing': 0},
    'wall-other': {'name': 'wall-other', 'id': 173, 'supercategory': 'wall', 'color': (102, 102, 156), 'isthing': 0},
    'wall-panel': {'name': 'wall-panel', 'id': 174, 'supercategory': 'wall', 'color': (102, 102, 156), 'isthing': 0},
    'wall-stone': {'name': 'wall-stone', 'id': 175, 'supercategory': 'wall', 'color': (135, 158, 223), 'isthing': 0},
    'wall-tile': {'name': 'wall-tile', 'id': 176, 'supercategory': 'wall', 'color': (7, 246, 231), 'isthing': 0},
    'wall-wood': {'name': 'wall-wood', 'id': 177, 'supercategory': 'wall', 'color': (107, 255, 200), 'isthing': 0},
    'water-other': {'name': 'water-other', 'id': 178, 'supercategory': 'water', 'color': (58, 41, 149), 'isthing': 0},
    'waterdrops': {'name': 'waterdrops', 'id': 179, 'supercategory': 'water', 'color': (0, 0, 0), 'isthing': 0},
    'window-blind': {'name': 'window-blind', 'id': 180, 'supercategory': 'window', 'color': (183, 121, 142), 'isthing': 0},
    'window-other': {'name': 'window-other', 'id': 181, 'supercategory': 'window', 'color': (255, 73, 97), 'isthing': 0},
    'wood': {'name': 'wood', 'id': 182, 'supercategory': 'solid', 'color': (0, 0, 0), 'isthing': 0},
    'other': {'name': 'other', 'id': 183, 'supercategory': 'other', 'color': (0, 0, 0), 'isthing': 0},
    'tree-merged': {'name': 'tree-merged', 'id': 184, 'supercategory': 'plant', 'color': (107, 142, 35), 'isthing': 0},
    'fence-merged': {'name': 'fence-merged', 'id': 185, 'supercategory': 'structural', 'color': (190, 153, 153), 'isthing': 0},
    'ceiling-merged': {'name': 'ceiling-merged', 'id': 186, 'supercategory': 'ceiling', 'color': (146, 139, 141), 'isthing': 0},
    'sky-other-merged': {'name': 'sky-other-merged', 'id': 187, 'supercategory': 'sky', 'color': (70, 130, 180), 'isthing': 0},
    'cabinet-merged': {'name': 'cabinet-merged', 'id': 188, 'supercategory': 'furniture-stuff', 'color': (134, 199, 156), 'isthing': 0},
    'table-merged': {'name': 'table-merged', 'id': 189, 'supercategory': 'furniture-stuff', 'color': (209, 226, 140), 'isthing': 0},
    'floor-other-merged': {'name': 'floor-other-merged', 'id': 190, 'supercategory': 'floor', 'color': (96, 36, 108), 'isthing': 0},
    'pavement-merged': {'name': 'pavement-merged', 'id': 191, 'supercategory': 'ground', 'color': (96, 96, 96), 'isthing': 0},
    'mountain-merged': {'name': 'mountain-merged', 'id': 192, 'supercategory': 'solid', 'color': (64, 170, 64), 'isthing': 0},
    'grass-merged': {'name': 'grass-merged', 'id': 193, 'supercategory': 'plant', 'color': (152, 251, 152), 'isthing': 0},
    'dirt-merged': {'name': 'dirt-merged', 'id': 194, 'supercategory': 'ground', 'color': (208, 229, 228), 'isthing': 0},
    'paper-merged': {'name': 'paper-merged', 'id': 195, 'supercategory': 'raw-material', 'color': (206, 186, 171), 'isthing': 0},
    'food-other-merged': {'name': 'food-other-merged', 'id': 196, 'supercategory': 'food-stuff', 'color': (152, 161, 64), 'isthing': 0},
    'building-other-merged': {'name': 'building-other-merged', 'id': 197, 'supercategory': 'building', 'color': (116, 112, 0), 'isthing': 0},
    'rock-merged': {'name': 'rock-merged', 'id': 198, 'supercategory': 'solid', 'color': (0, 114, 143), 'isthing': 0},
    'wall-other-merged': {'name': 'wall-other-merged', 'id': 199, 'supercategory': 'wall', 'color': (102, 102, 156), 'isthing': 0},
    'rug-merged': {'name': 'rug-merged', 'id': 200, 'supercategory': 'textile', 'color': (250, 141, 255), 'isthing': 0},
    'other': {'name': 'other', 'id': 201, 'supercategory': 'other', 'color': (0, 0, 0), 'isthing': 0},  # TODO: Choose right id and color for other
    'background': {'name': 'background', 'id': 202, 'supercategory': 'background', 'color': (0, 0, 0), 'isthing': 0}, # TODO: Choose right id and color for background
}
