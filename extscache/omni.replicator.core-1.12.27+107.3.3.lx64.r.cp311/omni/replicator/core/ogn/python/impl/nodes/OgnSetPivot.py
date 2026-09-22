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

import numpy as np
import omni.graph.core as og
import omni.usd
from omni.replicator.core import utils
from pxr import Gf, Sdf, Usd, UsdGeom


class OgnSetPivot:
    @staticmethod
    def compute(db) -> bool:
        stage = omni.usd.get_context().get_stage()
        sample_prim_paths = db.inputs.prims
        sample_prims = [stage.GetPrimAtPath(str(prim_path)) for prim_path in sample_prim_paths]

        pivot_vals = db.inputs.pivot
        if len(pivot_vals.shape) == 0:
            raise ValueError("Attribute 'pivot' is empty.")

        pivot_vals = pivot_vals.reshape((len(sample_prims), 3))

        for idx, prim in enumerate(sample_prims):
            # Only works for xform prim.
            prim_type = prim.GetTypeName()
            if prim_type != "Xform":
                db.log_error(f"The pivot can only be set to a xform prim, but got {prim_type}")
                db.outputs.execOut = og.ExecutionAttributeState.DISABLED
                return False

            # Convert the relative range to the absolute range.
            cache = UsdGeom.BBoxCache(
                time=Usd.TimeCode.Default(), includedPurposes=[UsdGeom.Tokens.default_], useExtentsHint=True
            )
            bound = utils.compute_aabb(cache, prim)

            min_bound = bound[:3]
            max_bound = bound[3:]

            size = max_bound - min_bound

            timeline_iface = omni.timeline.get_timeline_interface()
            time = timeline_iface.get_current_time() * timeline_iface.get_time_codes_per_seconds()

            parent_tf = UsdGeom.Xformable(prim).ComputeParentToWorldTransform(time)
            prim_local_tf = UsdGeom.Xformable(prim).GetLocalTransformation()

            # Calculate the centre of the
            centroid_location = np.array(parent_tf.ExtractTranslation() + prim_local_tf.ExtractTranslation())

            pivot_val = pivot_vals[idx]
            actual_pivot = min_bound + size * (pivot_val + 1) / 2

            pivot_offset = centroid_location - actual_pivot

            # First, offset all the children
            for child_prim in prim.GetChildren():

                # Offset the child prim in the opposite direction
                if not child_prim.GetAttribute("xformOp:translate"):
                    UsdGeom.Xformable(child_prim).AddTranslateOp(precision=UsdGeom.XformOp.PrecisionDouble)

                child_prim_translation = UsdGeom.Xformable(child_prim).GetLocalTransformation().ExtractTranslation()
                child_prim.GetAttribute("xformOp:translate").Set(
                    Gf.Vec3d(*(pivot_offset + child_prim_translation).tolist())
                )

        db.outputs.execOut = og.ExecutionAttributeState.ENABLED
        return True
