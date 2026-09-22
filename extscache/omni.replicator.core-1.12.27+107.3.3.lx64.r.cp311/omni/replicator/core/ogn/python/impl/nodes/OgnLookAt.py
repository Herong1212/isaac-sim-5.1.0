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

import contextlib

import numpy as np
import omni.graph.core as og
import omni.kit
import omni.timeline
import omni.usd
import pxr
import usdrt
from omni.replicator.core import utils
from omni.replicator.core.functional import utils as f_utils

EPS = 1e-5


class OgnLookAt:
    @staticmethod
    def compute(db) -> bool:
        use_usdrt = f_utils.get_is_fsd_enabled()
        input_prim_paths = db.inputs.prims
        target_prim_paths = db.inputs.targetPrim
        target_coords = db.inputs.target
        leaf_prim_paths = utils.get_non_xform_prims(db.inputs.prims, use_usdrt)
        if len(input_prim_paths) == 0:
            return False

        if use_usdrt:
            mod = usdrt
            stage = usdrt.Usd.Stage.Attach(omni.usd.get_context().get_stage_id())
        else:
            mod = pxr
            stage = omni.usd.get_context().get_stage()
        input_prims = [stage.GetPrimAtPath(str(prim_path)) for prim_path in input_prim_paths]
        leaf_prims = [stage.GetPrimAtPath(str(prim_path)) for prim_path in leaf_prim_paths]

        if target_prim_paths:
            if len(target_prim_paths) == 0:
                return False

            target_prims = [stage.GetPrimAtPath(str(tpp)) for tpp in target_prim_paths]
            target = mod.Gf.Vec3d()
            for target_prim in target_prims:
                target += f_utils.get_world_transform(target_prim).GetTranslation()
            target /= len(target_prims)
        elif len(target_coords) > 0:
            target = target_coords.tolist()
            target = mod.Gf.Vec3d(*target)
        else:
            return False
        try:
            for prim in input_prims:
                if not mod.UsdGeom.Xformable(prim):
                    prim_type = prim.GetTypeName()
                    raise ValueError(
                        f"Expected prim at {prim.GetPath()} to be an Xformable prim but got type {prim_type}"
                    )

        except Exception as error:
            db.outputs.execOut = og.ExecutionAttributeState.DISABLED
            db.log_error(f"LookAt Error: {error}")
            return False

        up_axis = db.inputs.upAxis

        if up_axis is None or np.all(up_axis == 0) or len(up_axis) == 0:
            if mod.UsdGeom.GetStageUpAxis(stage) == "Z":
                up_axis = mod.Gf.Vec3d(0, 0, 1)
            else:
                up_axis = mod.Gf.Vec3d(0, 1, 0)
        else:
            # Normalize up axis
            up_axis = up_axis / np.linalg.norm(up_axis)
            up_axis = mod.Gf.Vec3d(up_axis.tolist())

        output_rotations = []
        stage_up_axis = pxr.UsdGeom.GetStageUpAxis(stage)
        timeline_iface = omni.timeline.get_timeline_interface()
        time = timeline_iface.get_current_time() * timeline_iface.get_time_codes_per_seconds()
        ctx_mgr = contextlib.nullcontext if use_usdrt else pxr.Sdf.ChangeBlock
        with ctx_mgr():
            for xform, leaf in zip(input_prims, leaf_prims):
                is_camera = leaf.GetTypeName() == "Camera"
                world_tf = f_utils.get_world_transform(xform)
                parent_tf = mod.UsdGeom.Xformable(xform).ComputeParentToWorldTransform(time)

                eye = world_tf.GetTranslation()
                rot = utils.look_at(target, up_axis, eye, use_usdrt=use_usdrt, stage_up_axis=stage_up_axis)
                if is_camera and stage_up_axis == "Z":
                    # cam_z_rot is the inverse of the camera (XYZ 90, 0, 90) rotation applied by default when stage is Z-up
                    cam_z_rot = mod.Gf.Rotation(mod.Gf.Vec3d.ZAxis(), -90) * mod.Gf.Rotation(mod.Gf.Vec3d.XAxis(), -90)
                    rot = cam_z_rot * rot

                parent_rot_inv = parent_tf.GetInverse().GetOrthonormalized().ExtractRotation()
                angles = (rot * parent_rot_inv).Decompose(
                    mod.Gf.Vec3d.ZAxis(), mod.Gf.Vec3d.YAxis(), mod.Gf.Vec3d.XAxis()
                )
                x_index, y_index, z_index = 2, 1, 0
                output_rotations.append(mod.Gf.Vec3d(angles[x_index], angles[y_index], angles[z_index]))
        db.outputs.execOut = og.ExecutionAttributeState.ENABLED
        db.outputs.values = output_rotations
        return True
