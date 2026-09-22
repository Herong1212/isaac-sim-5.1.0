# SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

import numpy as np
import omni.graph.core as og
import omni.replicator.core as rep
import omni.usd
from pxr import Gf, UsdGeom


class OgnCameraPositionLookAtPrim:
    @staticmethod
    def compute(db):
        # Get all input attributes
        target_prim_paths = db.inputs.targetPrim
        if len(target_prim_paths) == 0:
            db.outputs.execOut = og.ExecutionAttributeState.DISABLED
            return False

        # Only one target camera supported
        target_prim_path = target_prim_paths[0]

        scale = db.inputs.scale
        axis = db.inputs.axes[0]

        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath(str(target_prim_path))

        centre = Gf.Vec3d(0, 0, 0)

        timeline = omni.timeline.get_timeline_interface()
        time = timeline.get_current_time() * timeline.get_time_codes_per_seconds()

        cache = UsdGeom.BBoxCache(time=time, includedPurposes=[UsdGeom.Tokens.default_], useExtentsHint=True)
        bounds_world = cache.ComputeWorldBound(prim)

        asset_range = bounds_world.GetRange()

        centre += asset_range.GetMidpoint()

        # Calculate distance to move camera from asset
        distance = np.linalg.norm(np.array(asset_range.GetSize()))
        distance *= scale  # Scale factor of distance from object centroid to camera

        normalized_axis = np.array(axis) / np.linalg.norm(np.array(axis))
        translate_distance = distance * normalized_axis
        translation = [(centre + translate_distance).tolist()]

        db.outputs.samples = translation
        db.outputs.execOut = og.ExecutionAttributeState.ENABLED

        return True
