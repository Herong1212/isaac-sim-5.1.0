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

import omni.graph.core as og
import omni.replicator.core as rep
import omni.usd
from omni.replicator.core import utils
from omni.replicator.core.functional.randomizer import scatter_3d


class OgnScatter3DInternalState:
    def __init__(self):
        self.rng = rep.rng.ReplicatorRNG()


class OgnScatter3D:
    @staticmethod
    def internal_state():
        return OgnScatter3DInternalState()

    @staticmethod
    def release(node):
        rep.rng.release(node.get_prim_path())

    @staticmethod
    def compute(db) -> bool:
        state = db.shared_state
        stage = omni.usd.get_context().get_stage()

        volume_prim_paths = [str(p) for p in utils.get_non_xform_prims(db.inputs.volumePrims)]
        volume_prims = [stage.GetPrimAtPath(str(p)) for p in volume_prim_paths]

        nocoll_prim_paths = [str(p) for p in utils.get_non_xform_prims(db.inputs.noCollPrims)]
        no_collision_prims = [stage.GetPrimAtPath(str(p)) for p in nocoll_prim_paths]

        volume_excl_prim_paths = [str(p) for p in utils.get_non_xform_prims(db.inputs.volumeExclPrims)]
        volume_excl_prims = [stage.GetPrimAtPath(str(p)) for p in volume_excl_prim_paths]

        sample_prim_paths = db.inputs.prims
        sample_prims = [stage.GetPrimAtPath(str(p)) for p in sample_prim_paths]

        if len(sample_prim_paths) == 0 or len(volume_prims) == 0:
            db.outputs.execOut = og.ExecutionAttributeState.DISABLED
            return False

        # sampling seed
        is_seed_valid = db.inputs.seed is not None
        is_seed_changed = state.rng is None or db.inputs.seed != state.rng.seed
        if is_seed_valid and is_seed_changed:
            node_id = db.inputs.nodeId if db.node.get_attribute_exists("inputs:nodeId") else 0
            state.rng.initialize(db.inputs.seed, db.node, node_id)

        for prim in sample_prim_paths:
            if utils.is_camera_prim(prim):
                rep.functional.physics.create_camera_collision_prims(prim)

        try:
            scatter_3d(
                prims=sample_prims,
                volume_prims=volume_prims,
                no_collision_prims=no_collision_prims,
                volume_excl_prims=volume_excl_prims,
                extents=(db.inputs.minSamp, db.inputs.maxSamp),
                check_for_collisions=db.inputs.checkForCollisions,
                prevent_vol_overlap=db.inputs.preventVolOverlap,
                viz_sampled_voxels=db.inputs.vizSampledVoxels,
                resolution_scaling=db.inputs.resolutionScaling,
                input_voxel_size=db.inputs.voxelSize,
                rng=state.rng,
            )
        except Exception as error:
            db.log_error(error)
            db.outputs.execOut = og.ExecutionAttributeState.DISABLED
            return False

        db.outputs.execOut = og.ExecutionAttributeState.ENABLED

        return True
