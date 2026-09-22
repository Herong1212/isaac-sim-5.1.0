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

from functools import lru_cache

import numpy as np
import omni.graph.core as og
import omni.usd
import usdrt
from omni.replicator.core import functional as F
from omni.replicator.core import utils
from pxr import Usd, UsdGeom

EPS = 1e-5


class InitBoundsCache:
    def __init__(self):
        self.init_sizes = None
        self._prim_paths = None

    def get_init_sizes(self, prim_paths):
        if prim_paths != self._prim_paths:
            self._prim_paths = prim_paths
            if F.utils.get_is_fsd_enabled():
                raise NotImplementedError("FSD is not supported yet")
                self._set_init_sizes_usdrt(prim_paths)
            else:
                self._set_init_sizes_pxr(prim_paths)
        return self.init_sizes

    def _set_init_sizes_usdrt(self, prim_paths):
        self.init_sizes = []
        stage = usdrt.Usd.Stage.Attach(omni.usd.get_context().get_stage_id())
        sample_prims = [stage.GetPrimAtPath(str(prim_path)) for prim_path in prim_paths]

        for prim in sample_prims:
            bounds = prim.GetAttribute("_worldExtent").Get()

    def _set_init_sizes_pxr(self, prim_paths):
        self.init_sizes = []
        stage = omni.usd.get_context().get_stage()
        sample_prims = [stage.GetPrimAtPath(str(prim_path)) for prim_path in prim_paths]

        for prim in sample_prims:
            timeline = omni.timeline.get_timeline_interface()
            time = timeline.get_current_time() * timeline.get_time_codes_per_seconds()

            cache = UsdGeom.BBoxCache(time=time, includedPurposes=[UsdGeom.Tokens.default_], useExtentsHint=True)
            bounds = utils.compute_aabb(cache, prim)
            min_bound = bounds[:3]
            max_bound = bounds[3:]
            self.init_sizes.append(max_bound - min_bound)

        self.init_sizes = np.array(self.init_sizes)


class OgnSizeToScale:
    @staticmethod
    def internal_state():
        return InitBoundsCache()

    @staticmethod
    def compute(db) -> bool:
        sample_prim_paths = db.inputs.prims

        if len(sample_prim_paths) == 0:
            db.outputs.execOut = og.ExecutionAttributeState.DISABLED
            return False

        state = db.shared_state
        init_sizes = state.get_init_sizes(sample_prim_paths)

        size = db.inputs.size

        # Compute the bounding box to get the size of the prim.
        all_scales = size / (init_sizes + EPS)

        if db.inputs.maintainAspectRatio:
            all_scales = np.repeat(np.min(all_scales, axis=1, keepdims=True), 3, axis=1)

        # Set the number of samples to be the same as number of prims
        db.outputs.numSamples = len(sample_prim_paths)
        db.outputs.samples = all_scales

        db.outputs.execOut = og.ExecutionAttributeState.ENABLED

        return True
