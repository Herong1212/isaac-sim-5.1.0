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

from typing import List

import omni.graph.core as og
import omni.timeline
import omni.usd
from omni.replicator.core import utils
from omni.replicator.core.scripts.functional import modify


class OgnBindMaterial:
    @staticmethod
    def compute(db) -> bool:
        prim_paths = db.inputs.prims
        material_paths = db.inputs.materialPaths
        material_prims = db.inputs.materialPrims

        stage = omni.usd.get_context().get_stage()

        # Validate input
        if len(prim_paths) == 0 or material_paths is None and material_prims is None:
            db.outputs.exec = og.ExecutionAttributeState.DISABLED
            return False

        prims = [stage.GetPrimAtPath(str(prim_path)) for prim_path in prim_paths]
        material_prims = [stage.GetPrimAtPath(str(material_path)) for material_path in material_paths] + [
            stage.GetPrimAtPath(str(material_prim)) for material_prim in material_prims
        ]

        modify.material(prims=prims, material_prim=material_prims)

        db.outputs.exec = og.ExecutionAttributeState.ENABLED
        return True
