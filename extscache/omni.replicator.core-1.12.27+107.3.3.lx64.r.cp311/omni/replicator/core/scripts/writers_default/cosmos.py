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

import json
from typing import Optional

import omni.timeline
from video_encoding import get_video_encoding_interface

from .. import functional as F
from ..annotators import AnnotatorRegistry
from ..backends import DiskBackend, io_queue
from ..writers import Writer

__version__ = "0.0.2"


class CosmosWriter(Writer):
    """Writer class for generating input to Cosmos Transfer1.

    This writer generates videos for various modalities that can be used as input to Cosmos Transfer1. The included
    modalities are:
    - RGB
    - Shaded Segmentation
    - Segmentation
    - Distance to camera (Depth)
    - Edges

    If using a ``trigger.on_time`` node, the writer will automatically increment the clip index when the trigger fires.
    Otherwise, the clip index can be incremented manually by calling the ``next_clip`` method.

    Args:
        backend: The backend to use for writing the video.
        output_dir: Output directory string that indicates the directory to save the results. This parameter is ignored
            if backend is set.
        video_filepath: Path where the output video will be saved (e.g. "/home/user/Videos/my_video.mp4").
        segmentation_mapping: An optional dictionary mapping semantic labels to specific colors. If set,
            `use_instance_id` is ignored and the segmentation used will be based on semantic segmentation.
        use_instance_id: Whether to use instance id segmentation instead of instance segmentation. Instance ID
            segmentation does not require assets be semantically annotated. If `segmentation_mapping` is set,
            this parameter is ignored.
        canny_threshold_low: The lower threshold for the Canny edge detector.
        canny_threshold_high: The higher threshold for the Canny edge detector.
    """

    def __init__(
        self,
        backend=None,
        output_dir: str = None,
        segmentation_mapping: Optional[dict] = None,
        use_instance_id: bool = True,
        canny_threshold_low: int = 10,
        canny_threshold_high: int = 100,
    ):
        self._backend = backend
        if output_dir and not self._backend:
            self._backend = DiskBackend(output_dir=output_dir)
        elif not self._backend:
            raise ValueError("No `backend` or `output_dir` parameter specified, unable to initialize writer.")

        self.version = __version__

        semantic_params = {"colorize": True}
        shade_seg_params = {}
        if segmentation_mapping:
            semantic_params["mapping"] = self._get_anno_semantic_mapping(segmentation_mapping)
            self._shaded_segmentation_annotator = "shaded_semantic_segmentation"
            self._segmentation_annotator = "semantic_segmentation"
            shade_seg_params["useCandyColours"] = False
        elif use_instance_id:
            self._shaded_segmentation_annotator = "shaded_instance_id_segmentation"
            self._segmentation_annotator = "instance_id_segmentation_fast"
        else:
            self._shaded_segmentation_annotator = "shaded_instance_segmentation"
            self._segmentation_annotator = "instance_segmentation"

        self.annotators = [
            AnnotatorRegistry.get_annotator(self._shaded_segmentation_annotator, device="cuda").augment(
                "Canny", thresholdLow=canny_threshold_low, thresholdHigh=canny_threshold_high, name="edges"
            ),
            AnnotatorRegistry.get_annotator(
                self._shaded_segmentation_annotator, device="cuda", init_params=shade_seg_params
            ),
            AnnotatorRegistry.get_annotator(self._segmentation_annotator, init_params=semantic_params, device="cuda"),
            AnnotatorRegistry.get_annotator("distance_to_camera").augment("ColorizeDepth", name="depth"),
            "rgb",
        ]
        self._frame_id = 0
        self._clip_idx = 0
        self._frame_rate = None
        self._light_source = None

    def _get_anno_semantic_mapping(self, mapping_dict):
        anno_semantic_mapping = {}
        for k, v in mapping_dict.items():
            is_valid_id = isinstance(v, int)
            is_valid_colour = isinstance(v, (list, tuple)) and len(v) == 4 and all(isinstance(e, int) for e in v)
            if not is_valid_id and not is_valid_colour:
                raise ValueError(
                    f"Provided mapping maps to invalid values. All target values must be an integer ID or integer RGBA values"
                )
            if ":" in k:
                anno_semantic_mapping[k] = v
            else:
                # fallback on `class` semantic type
                anno_semantic_mapping[f"class:{k}"] = v
        return json.dumps(anno_semantic_mapping)

    def write(self, data):
        """Write video data optimized for Cosmos Transfer1.

        Args:
            data: Dictionary containing frame data with keys:
                - rgb: RGB image array (H,W,3)
                - segmentation: Segmentation image array (H,W,C)
                - shaded_seg: Shaded segmentation image array (H,W,C)
                - depth: Depth image array (H,W,1)
                - edges: Edge image array (H,W,1)
        """
        sequence_id = None
        for trigger_name, call_count in data["trigger_outputs"].items():
            if "on_time" in trigger_name:
                sequence_id = call_count
                # Only use the first on_time trigger to determine the sequence id
                break
        if sequence_id is not None and sequence_id != self._clip_idx:
            self.next_clip()
            self._clip_idx = sequence_id

        if self._frame_rate is None:
            timeline_iface = omni.timeline.get_timeline_interface()
            self._frame_rate = timeline_iface.get_time_codes_per_seconds()
        edges = data["edges"]
        instance_segmentation = data[self._segmentation_annotator]["data"]
        shaded_seg = data[self._shaded_segmentation_annotator]
        depth = data["depth"]
        rgb = data["rgb"]

        self._backend.schedule(
            F.write_image, data=rgb, path=f"clip_{self._clip_idx:04}/rgb/rgb_{self._frame_id:04}.png"
        )
        self._backend.schedule(
            F.write_image,
            data=shaded_seg,
            path=f"clip_{self._clip_idx:04}/shaded_seg/shaded_seg_{self._frame_id:04}.png",
        )
        self._backend.schedule(
            F.write_image,
            data=instance_segmentation,
            path=f"clip_{self._clip_idx:04}/segmentation/segmentation_{self._frame_id:04}.png",
        )
        self._backend.schedule(
            F.write_image, data=depth, path=f"clip_{self._clip_idx:04}/depth/depth_{self._frame_id:04}.png"
        )
        self._backend.schedule(
            F.write_image, data=edges, path=f"clip_{self._clip_idx:04}/edges/edges_{self._frame_id:04}.png"
        )
        self._frame_id += 1

    def on_final_frame(self):
        if self._frame_id == 0:
            return

        io_queue.wait_until_done()

        for key in ["rgb", "segmentation", "edges", "depth", "shaded_seg"]:
            video_encoding = get_video_encoding_interface()
            video_encoding.start_encoding(
                video_filename=f"{self._backend.output_dir}/clip_{self._clip_idx:04}/{key}.mp4",
                framerate=self._frame_rate,
                nframes=self._frame_id,
                overwrite_video=True,
            )
            for i in range(self._frame_id):
                path = f"{self._backend.output_dir}/clip_{self._clip_idx:04}/{key}/{key}_{i:04}.png"
                video_encoding.encode_next_frame_from_file(path)
            video_encoding.finalize_encoding()

        self._frame_id = 0

    def next_clip(self):
        """Finalize current clip and update parameters for the next one.

        - Combines generated frames into videos
        - Resets frame counter
        - Increments output directory
        """
        self.on_final_frame()
        self._clip_idx += 1
