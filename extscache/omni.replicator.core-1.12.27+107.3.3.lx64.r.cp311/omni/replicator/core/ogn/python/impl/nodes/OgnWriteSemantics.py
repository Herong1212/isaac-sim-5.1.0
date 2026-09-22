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

from ast import literal_eval

import omni.graph.core as og
import omni.replicator.core as rep
import omni.timeline
import omni.usd


class OgnWriteSemantics:
    @staticmethod
    def compute(db) -> bool:
        stage = omni.usd.get_context().get_stage()
        sample_prim_paths = db.inputs.prims
        mode = db.inputs.mode
        semantics_legacy = db.inputs.semantics
        semantics_values = db.inputs.semantics_values

        semantics = {}

        if (
            semantics_values
            and len(semantics_values) > 1
            and semantics_values[0] == "{"
            and semantics_values[-1] == "}"
        ):
            # New semantics
            semantics.update(literal_eval(semantics_values))
        if semantics_legacy:
            # Legacy semantics
            semantics_legacy = [tuple(v.split(":")) for v in db.inputs.semantics]
            semantics.update(rep.utils.legacy_semantics_arg_to_new(semantics_legacy))

        prims = [stage.GetPrimAtPath(str(p)) for p in sample_prim_paths]
        rep.functional.modify.semantics(prims, semantics, mode=mode)

        db.outputs.execOut = og.ExecutionAttributeState.ENABLED
        return True
