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

import carb
import omni.graph.core as og
from omni.replicator.core import utils
from pxr import Gf


class OgnMeshBoundsDecalPlacement:
    @staticmethod
    def compute(db) -> bool:
        prim_paths = db.inputs.prims
        in_vector = db.inputs.boundsVector if not None else Gf.Vec3d(0, 0, 1)
        in_offset = db.inputs.offset if not None else 0.01
        in_rotation = db.inputs.rotation if not None else Gf.Vec3d()
        in_scale = db.inputs.scale if not None else Gf.Vec3d(1, 1, 1)

        if len(prim_paths) == 0:
            return False

        if len(prim_paths) != 1:
            carb.log_error(f"Can only normalize on a single target mesh.")
            db.outputs.execOut = og.ExecutionAttributeState.DISABLED
            return False
        else:
            prim_path = prim_paths[0]

        try:
            translate, rotateXYZ, scale = utils.get_decal_transform_from_normalized_bounds(
                prim_path, in_vector, in_offset, in_rotation, in_scale
            )
        except Exception as e:
            db.outputs.execOut = og.ExecutionAttributeState.DISABLED
            return False

        db.outputs.execOut = og.ExecutionAttributeState.ENABLED
        db.outputs.translation = translate
        db.outputs.rotation = rotateXYZ
        db.outputs.scale = scale

        return True
