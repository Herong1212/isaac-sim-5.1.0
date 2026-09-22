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

import colorsys
import ctypes
import json
import random
import re
import traceback

import carb
import numpy as np
import omni.graph.core as og
import warp as wp
from omni.replicator.core.ogn.OgnSemanticSegmentationDatabase import OgnSemanticSegmentationDatabase
from omni.replicator.core.writers_default.tools import random_colours_id

"""OmniGraph node for semantic segmentation"""


# Expression assumes spaces are allowed in semantic value but not in semantic type
SEMANTIC_SPLIT_REGEX = "\s(?=\w+:)"


@wp.kernel
def get_semantic_from_instance(
    instance_segmentation: wp.array(dtype=wp.uint32),
    semantic_segmentation: wp.array(dtype=wp.uint32),
    instance_ids_gpu: wp.array(dtype=wp.uint32),
    semantic_ids_gpu: wp.array(dtype=wp.uint32),
):
    tid = wp.tid()

    instance = instance_segmentation[tid]
    num_instance_ids = instance_ids_gpu.shape[0]

    # Background is always 0
    if instance == 0:
        semantic_segmentation[tid] = wp.uint32(0)
        return

    # Initialize to 1 (unlabelled)
    semantic_segmentation[tid] = wp.uint32(1)
    i = int(0)
    while i < num_instance_ids:
        if instance_ids_gpu[i] == instance:
            semantic_segmentation[tid] = semantic_ids_gpu[i]
            return
        i += 1


def get_address(attr):
    ptr_type = ctypes.POINTER(ctypes.c_size_t)
    ptr = ctypes.cast(attr.memory, ptr_type)
    return ptr.contents.value


def get_wp_array(ptr, shape, strides, dtype, device):
    return wp.types.array(
        dtype=dtype,
        shape=shape,
        strides=strides,
        ptr=ptr,
        device=device,
        requires_grad=False,
    )


def get_unique_ids(unique_mask, semantic_ids):
    unique_mask_np = unique_mask.numpy().tolist()
    return [semantic_ids[i] for i in range(len(unique_mask_np)) if unique_mask_np[i]]


# ======================================================================
class OgnSemanticSegmentationInternalState:
    def __init__(self):
        self._label_to_id = {}
        self._id_to_label = {}
        self._label_to_color = {}
        self._color_to_label = {}
        self._colorize = False
        self._cached_ids = None
        self._cached_ids_colorized = None
        self._cache_key = None

        self._id_start = 2

        # Step to sample from the hsv space.
        self._color_step = 1
        # Start point to sample from the hsv space.
        self._color_start = 0
        # number of new color added. It will be reset if the hsv space needs to be divided more.
        self._color_count = 0
        # offset that added to self._color_start for everytime it updates.
        self._color_offset = 0

        self.output_array = None
        self.semantic_ids_map_gpu = None

    @property
    def colorize(self):
        return self._colorize

    def get_output_array(self, dtype, shape, device):
        if (
            self.output_array is None
            or dtype != self.output_array.dtype
            or shape != self.output_array.shape
            or device != self.output_array.device
        ):
            self.output_array = wp.empty(
                dtype=dtype,
                shape=tuple(shape),
                device=device,
                requires_grad=False,
            )
        return self.output_array

    @property
    def is_initialized(self):
        return bool(self._label_to_id)

    def _get_random_colors_by_id(self, ids, labels):
        colors = []
        for input_id, label in zip(ids, labels):
            color = self._label_to_color.get(label)
            if color is None:
                color = random_colours_id(input_id)
                self._label_to_color[label] = color
                self._color_to_label[color] = label

                self._color_count += 1

            colors.append(color)

        return colors

    def _get_ids(self, labels):
        ids = []
        for label in labels:
            if label not in self._label_to_id:
                self._label_to_id[label] = self._id_start
                self._id_to_label[self._id_start] = label
                self._id_start += 1

            ids.append(self._label_to_id[label])
        return ids

    def get_ids(self, labels):
        if labels == self._cache_key:
            return self._cached_ids_colorized if self._colorize else self._cached_ids
        if self._colorize:
            ids = self._get_ids(labels)
            colorized_ids = self._get_random_colors_by_id(ids, labels)
            self._cache_key, self._cached_ids, self._cached_ids_colorized = labels, ids, colorized_ids
            return colorized_ids
        else:
            ids = self._get_ids(labels)
            self._cache_key, self._cached_ids = labels, ids
            return ids

    def set_mapping(self, mapping):
        try:
            custom_mapping = json.loads(mapping)
        except json.decoder.JSONDecodeError as e:
            custom_mapping = {}
            carb.log_warn(f"Unable to load custom mapping: {e}")

        # If mapping is provided, it overrides over colorize setting
        if custom_mapping:
            self.set_colorize(isinstance(list(custom_mapping.values())[0], (list, tuple)))

        # Setup predefined labels
        background_key = 0
        unlabelled_key = 1
        background_val = "class:BACKGROUND"
        unlabelled_val = "class:UNLABELLED"
        self._label_to_id = {str(background_val): background_key, str(unlabelled_val): unlabelled_key}
        self._id_to_label = {background_key: background_val, unlabelled_key: unlabelled_val}
        self._label_to_color = {str(background_val): (0, 0, 0, 0), str(unlabelled_val): (0, 0, 0, 255)}
        self._color_to_label = {(0, 0, 0, 0): background_val, (0, 0, 0, 255): unlabelled_val}

        # Validate mapping
        for k, v in custom_mapping.items():
            valid_key_pattern = r"^[^:]+:[^:]+$"
            is_valid_key = re.search(pattern=valid_key_pattern, string=k)
            is_valid_id = isinstance(v, int)
            is_valid_colour = isinstance(v, (list, tuple)) and len(v) == 4 and all(isinstance(e, int) for e in v)
            if not is_valid_key:
                carb.log_warn(f"Skipping entry in custom mapping due to invalid key: `{k}: {v}`")
                continue
            if self._colorize and not is_valid_colour:
                self._custom_mapping = {}
                carb.log_warn(f"Skipping entry in custom mapping due to invalid color: `{k}: {v}`")
                continue
            if not self._colorize and not is_valid_id:
                self._custom_mapping = {}
                carb.log_warn(f"Skipping entry in custom mapping due to invalid ID: `{k}: {v}`")
                continue
            if is_valid_colour:
                v = tuple(v)
                self._label_to_color[k] = v
                self._color_to_label[v] = k
                self._label_to_id[self._id_start] = v
                self._id_start += 1
            else:
                self._label_to_id[k] = v
                self._id_to_label[v] = k

    def set_colorize(self, colorize):
        self._colorize = colorize


def compute(db, target_device: str) -> bool:
    carb.profiler.begin(1, "setup")
    state = db.shared_state
    if not state.is_initialized:
        state.set_colorize(db.inputs.colorize)
        state.set_mapping(db.inputs.mapping)
    height = db.inputs.height
    width = db.inputs.width

    shape = (db.inputs.height, db.inputs.width)
    if shape[0] == 0:
        return True
    instance_seg_strides = db.inputs.instanceSegmentationStrides
    strides = (instance_seg_strides[1], instance_seg_strides[0])
    instance_segmentation_gpu = get_wp_array(
        ptr=db.inputs.instanceSegmentationPtr, shape=shape, strides=strides, dtype=wp.uint32, device=target_device
    ).reshape(-1)

    semantic_segmentation_gpu = state.get_output_array(dtype=wp.uint32, shape=(height, width), device=target_device)

    segmentation_out_shape = (height, width, 4) if state.colorize else (height, width)

    instance_ids = db.inputs.ids

    # Check if instance segmentation node is colorized
    upstream_conns = db.node.get_attribute("inputs:ids").get_upstream_connections()
    if upstream_conns and upstream_conns[0].get_node().get_attribute("inputs:colorize").get():
        # re-interpret input ids as uint32
        instance_ids = instance_ids.reshape(-1, 4).astype(np.uint8).view(np.uint32).reshape(-1)

    if not len(instance_ids):
        # No semantic entity in view. Return empty array
        db.outputs.ids = [0]
        db.outputs.labels = ["class:BACKGROUND"]
        db.outputs.exec = og.ExecutionAttributeState.ENABLED
        db.outputs.bufferSize = db.inputs.bufferSize
        db.outputs.height = db.inputs.height
        db.outputs.width = db.inputs.width

        semantic_segmentation_gpu.zero_()
        db.outputs.dataPtr = semantic_segmentation_gpu.ptr
        db.outputs.dataType = "uint8" if state.colorize else "uint32"
        db.outputs.dataShape = segmentation_out_shape
        db.outputs.strides = semantic_segmentation_gpu.strides[1], semantic_segmentation_gpu.strides[0]
        db.outputs.cudaDeviceIndex = semantic_segmentation_gpu.device.ordinal
        return True

    # new_segmentation_data = np.copy(segmentation_data)
    # mapping from semantic index to its parent semantic index
    carb.profiler.end(1)
    carb.profiler.begin(1, "get ids")

    # Mapping from id to semantic labels of each prim
    semantic_sets = db.inputs.semantics
    semantic_ids_map = state.get_ids(semantic_sets)

    carb.profiler.end(1)
    carb.profiler.begin(1, "allocate gpu data")

    # Check to see if the semantic ids map needs to be re-allocated
    if (
        state.semantic_ids_map_gpu is None
        or state.semantic_ids_map_gpu.shape[0] != len(semantic_ids_map)
        or state.semantic_ids_map_gpu.device != target_device
    ):
        if state.colorize:
            state.semantic_ids_map_gpu = wp.empty(dtype=wp.uint32, shape=(len(semantic_ids_map),), device=target_device)
        else:
            state.semantic_ids_map_gpu = wp.empty(dtype=wp.uint32, shape=(len(semantic_ids_map),), device=target_device)

    if state.colorize:
        wp.copy(
            state.semantic_ids_map_gpu,
            wp.from_numpy(np.array(semantic_ids_map, dtype=np.uint8).view(np.uint32).reshape(-1)),
        )
    else:
        wp.copy(state.semantic_ids_map_gpu, wp.from_numpy(np.array(semantic_ids_map, dtype=np.uint32)))

    instance_ids_gpu = wp.array(instance_ids, dtype=wp.uint32, device=target_device)

    carb.profiler.end(1)
    carb.profiler.begin(1, "map instance2semantic")

    wp.launch(
        kernel=get_semantic_from_instance,
        dim=db.inputs.height * db.inputs.width,
        inputs=[
            instance_segmentation_gpu,
            semantic_segmentation_gpu.reshape(-1),
            instance_ids_gpu,
            state.semantic_ids_map_gpu,
        ],
        device=target_device,
    )
    carb.profiler.end(1)
    carb.profiler.begin(1, "unique ids")

    unique_semantic_ids = sorted(list(set(semantic_ids_map)))
    if state.colorize:
        unique_semantics_sets = [state._color_to_label[usid] for usid in unique_semantic_ids]
    else:
        unique_semantics_sets = [state._id_to_label[usid] for usid in unique_semantic_ids]

    carb.profiler.end(1)
    carb.profiler.begin(1, "set output")

    db.outputs.ids = np.array(unique_semantic_ids).flatten()
    db.outputs.labels = unique_semantics_sets
    db.outputs.exec = og.ExecutionAttributeState.ENABLED
    db.outputs.bufferSize = db.inputs.bufferSize
    db.outputs.height = db.inputs.height
    db.outputs.width = db.inputs.width
    db.outputs.dataPtr = semantic_segmentation_gpu.ptr
    db.outputs.dataType = "uint8" if state.colorize else "uint32"
    db.outputs.dataShape = segmentation_out_shape
    db.outputs.strides = semantic_segmentation_gpu.strides[1], semantic_segmentation_gpu.strides[0]
    db.outputs.cudaDeviceIndex = semantic_segmentation_gpu.device.ordinal
    carb.profiler.end(1)

    return True


class OgnSemanticSegmentation:
    @staticmethod
    def internal_state():
        return OgnSemanticSegmentationInternalState()

    @staticmethod
    def release(node):
        state = OgnSemanticSegmentationDatabase.shared_internal_state(node)
        state.output_array = None

    @staticmethod
    def compute(db) -> bool:
        cuda_ordinal = db.inputs.instanceSegmentationCudaDeviceIndex
        instance_device = f"cuda:{cuda_ordinal}" if cuda_ordinal >= 0 else "cpu"

        try:
            compute(db, instance_device)
        except Exception:
            db.log_error(traceback.format_exc())
            db.internal_state.is_valid = False
            return

        return True
