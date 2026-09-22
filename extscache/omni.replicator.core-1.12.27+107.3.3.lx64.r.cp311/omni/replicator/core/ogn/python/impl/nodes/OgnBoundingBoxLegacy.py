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

import omni.graph.core as og

"""OmniGraph node to Bounding box annotator"""


class OgnBoundingBoxLegacy:
    @staticmethod
    def compute(db) -> bool:
        ids = db.inputs.ids
        labels = db.inputs.labels
        labels_str = []

        for label in labels:
            labels_str.append({lab.split(":")[0]: lab.split(":")[1] for lab in label.split(" ")})

        if len(ids) > 0:
            id_to_labels = {_id: label for _id, label in zip(ids.tolist(), labels_str)}
            serialized_index_to_labels = json.dumps(id_to_labels)
        else:
            serialized_index_to_labels = "{}"

        db.outputs.data = db.inputs.data
        db.outputs.idToLabels = serialized_index_to_labels
        db.outputs.primPaths = db.inputs.primPaths
        db.outputs.bboxIds = db.inputs.bboxIds
        db.outputs.exec = og.ExecutionAttributeState.ENABLED
        db.outputs.bufferSize = db.inputs.bufferSize
        db.outputs.height = db.inputs.height
        db.outputs.width = db.inputs.width

        return True
