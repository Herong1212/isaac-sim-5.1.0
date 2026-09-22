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
import numpy as np
import omni.graph.core as og
import omni.replicator.core as rep
import omni.timeline
import omni.usd
from omni.replicator.core import utils
from pxr import Gf, Sdf, UsdGeom
from scipy.spatial.transform import Rotation as R


class OgnSampleRotationInternalState:
    def __init__(self):
        self.rng = rep.rng.ReplicatorRNG()


class OgnSampleRotation:
    @staticmethod
    def internal_state():
        return OgnSampleRotationInternalState()

    @staticmethod
    def release(node):
        rep.rng.release(node.get_prim_path())

    @staticmethod
    def compute(db) -> bool:
        state = db.shared_state

        stage = omni.usd.get_context().get_stage()
        sample_prim_paths = db.inputs.prims

        if len(sample_prim_paths) == 0:
            db.outputs.execOut = og.ExecutionAttributeState.DISABLED
            return False

        sample_prims = [stage.GetPrimAtPath(str(prim_path)) for prim_path in sample_prim_paths]

        lower = db.inputs.minAngle
        upper = db.inputs.maxAngle
        selected_rotation_ops = []

        # ensure that all sample prims are xformable
        for prim in sample_prims:
            if not UsdGeom.Xformable(prim):
                prim_type = prim.GetTypeName()
                raise carb.log_error(
                    f"Expected prim at {prim.GetPath()} to be an Xformable prim but got type {prim_type}"
                )
                continue

            selected_rotation_ops.append(utils.select_rotation_op(prim))

        if np.any(lower > upper) or np.any(np.isclose(lower, upper)):
            raise ValueError(
                f"Received value of inputs:lower to be: {lower} and value of inputs:upper to be {upper}"
                + "All angles in inputs:lower are expected to be strictly less than inputs:upper."
            )

        # count samples
        num_samples = 0
        for prim in sample_prims:
            prim_type = prim.GetTypeName()
            if prim_type == "PointInstancer":
                num_samples += len(prim.GetAttribute("protoIndices").Get())
            else:
                num_samples += 1

        # sampling seed
        is_seed_valid = db.inputs.seed is not None
        is_seed_changed = state.rng is None or db.inputs.seed != state.rng.seed
        if is_seed_valid and is_seed_changed:
            node_id = db.inputs.nodeId if db.node.get_attribute_exists("inputs:nodeId") else 0
            state.rng.initialize(db.inputs.seed, db.node, node_id)

        # sample rotations within constraint
        samples = list()
        num_valid = 0
        while num_valid < num_samples:
            num_to_sample = 2 * num_samples  # sample twice as many, as a heuristic
            rots = R.random(num_to_sample, random_state=state.rng.generator).as_euler("XYZ", degrees=True)
            rots = (rots + 180.0) / 360.0 * (upper - lower) + lower
            is_in_range = np.logical_and(rots >= lower, rots <= upper)
            valid_samples = rots[np.where(np.logical_and.reduce(is_in_range.T))]
            samples.append(valid_samples)
            num_valid += valid_samples.shape[0]

        sampled_rotations = np.concatenate(samples)[0:num_samples, :]

        with Sdf.ChangeBlock():
            idx = 0
            for prim, rotation_op in zip(sample_prims, selected_rotation_ops):
                if prim.GetTypeName() == "PointInstancer":
                    num_samples_pi = len(prim.GetAttribute("protoIndices").Get())
                    quats = R.from_euler(
                        "XYZ", angles=sampled_rotations[idx : idx + num_samples_pi], degrees=True
                    ).as_quat()
                    prim.GetAttribute("orientations").Set([Gf.Quath(*angles) for angles in quats])
                    idx += num_samples_pi
                else:
                    rotaton_angles_xyz = sampled_rotations[idx]
                    rotation = (
                        Gf.Rotation(Gf.Vec3d.XAxis(), rotaton_angles_xyz[0])
                        * Gf.Rotation(Gf.Vec3d.YAxis(), rotaton_angles_xyz[1])
                        * Gf.Rotation(Gf.Vec3d.ZAxis(), rotaton_angles_xyz[2])
                    )
                    utils.set_rotation_by_op(prim, rotation_op, rotation)

                    idx += 1

        db.outputs.execOut = og.ExecutionAttributeState.ENABLED
        return True
