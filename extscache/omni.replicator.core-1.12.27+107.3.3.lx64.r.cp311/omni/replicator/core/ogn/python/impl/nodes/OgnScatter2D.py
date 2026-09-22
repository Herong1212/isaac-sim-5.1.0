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
from omni.replicator.core.functional.randomizer import scatter_2d


class OgnScatter2DInternalState:
    def __init__(self):
        self.rng = rep.rng.ReplicatorRNG()


class OgnScatter2D:
    @staticmethod
    def internal_state():
        return OgnScatter2DInternalState()

    @staticmethod
    def release(node):
        rep.rng.release(node.get_prim_path())

    @staticmethod
    def compute(db) -> bool:
        state = db.shared_state

        stage = omni.usd.get_context().get_stage()
        surface_prim_paths = utils.get_non_xform_prims(db.inputs.surfacePrims)
        surface_prims = [stage.GetPrimAtPath(str(p)) for p in surface_prim_paths]
        nocoll_prim_paths = utils.get_non_xform_prims(db.inputs.noCollPrims)
        no_collision_prims = [stage.GetPrimAtPath(str(p)) for p in nocoll_prim_paths]
        sample_prim_paths = db.inputs.prims
        sample_prims = [stage.GetPrimAtPath(str(p)) for p in sample_prim_paths]
        min_samp = db.inputs.minSamp
        max_samp = db.inputs.maxSamp
        offset = db.inputs.normalOffset

        if len(surface_prim_paths) == 0 or len(sample_prim_paths) == 0:
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

        scatter_2d(
            prims=sample_prims,
            surface_prims=surface_prims,
            no_collision_prims=no_collision_prims,
            extents=(min_samp, max_samp),
            offset=offset,
            check_for_collisions=db.inputs.checkForCollisions,
            rng=state.rng,
        )

        db.outputs.execOut = og.ExecutionAttributeState.ENABLED
        return True
