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
import re

import numpy as np
import omni.graph.core as og
import warp as wp

"""OmniGraph node to Bounding box annotator"""

SEMANTIC_SPLIT_REGEX = "\s(?=\w+:)"


def get_wp_array(ptr, shape, strides, dtype, device):
    wp_arr = wp.types.array(
        dtype=dtype,
        shape=shape,
        strides=strides,
        ptr=ptr,
        device=device,
        requires_grad=False,
    )
    if not device:
        wp_arr = wp_arr.numpy()
    return wp_arr


class OgnInstanceSegmentationLegacy:
    @staticmethod
    def compute(db) -> bool:
        colorize = db.inputs.colorize
        ids = db.inputs.ids
        labels = db.inputs.labels
        semantics = db.inputs.semantics
        semantic_str = []

        device = f"cuda:{db.inputs.cudaDeviceIndex}" if db.inputs.cudaDeviceIndex >= 0 else "cpu"

        output_shape = (db.inputs.height, db.inputs.width)
        output_strides = (db.inputs.strides[1], db.inputs.strides[0])
        output_dtype = wp.uint8 if colorize else wp.uint32
        if colorize:
            ids = ids.reshape((-1, 4))
            output_shape = (db.inputs.height, db.inputs.width, 4)
            output_strides = (db.inputs.strides[1], db.inputs.strides[0], wp.types.type_size_in_bytes(wp.uint8))

        ids = ids.tolist()

        for semantic in semantics:
            semantic_str.append(
                {lab.split(":")[0]: lab.split(":")[1] for lab in re.split(SEMANTIC_SPLIT_REGEX, semantic)}
            )

        if len(ids) > 0:
            if colorize:
                id_to_semantics = {str(tuple(_id)): label for _id, label in zip(ids, semantic_str)}
                id_to_labels = {str(tuple(_id)): label for _id, label in zip(ids, labels)}
            else:
                id_to_semantics = {_id: label for _id, label in zip(ids, semantic_str)}
                id_to_labels = {_id: label for _id, label in zip(ids, labels)}
            serialized_index_to_semantics = json.dumps(id_to_semantics)
            serialized_index_to_labels = json.dumps(id_to_labels)
        else:
            serialized_index_to_labels = "{}"
            serialized_index_to_semantics = "{}"

        instance_seg_data = wp.array(
            dtype=output_dtype,
            shape=output_shape,
            strides=output_strides,
            ptr=db.inputs.dataPtr,
            device=device,
            requires_grad=False,
        ).numpy()

        if colorize:
            db.outputs.data = instance_seg_data.reshape(db.inputs.height * db.inputs.width, 4).view(np.uint8)
        else:
            db.outputs.data = instance_seg_data.reshape(
                db.inputs.height * db.inputs.width,
            ).view(np.uint8)
        db.outputs.dataType = db.inputs.dataType
        db.outputs.dataShape = output_shape
        db.outputs.idToLabels = serialized_index_to_labels
        db.outputs.idToSemantics = serialized_index_to_semantics
        db.outputs.exec = og.ExecutionAttributeState.ENABLED
        db.outputs.bufferSize = db.inputs.bufferSize
        db.outputs.height = db.inputs.height
        db.outputs.width = db.inputs.width

        return True
