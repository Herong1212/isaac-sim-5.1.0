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

"""
This is the implementation of the OGN node defined in OgnOnNewFrame.ogn
"""

import carb
import omni.graph.core as og
from omni.replicator.core import utils
from omni.replicator.core.scripts.functional.modify import visibility
from pxr import Sdf


class OgnSetVisibility:
    @staticmethod
    def compute(db) -> bool:
        targets = db.inputs.prims
        values = db.inputs.values

        samples = values.tolist()
        prims = utils.find_prims(targets, "prims")

        visibility(prims, samples)

        db.outputs.execOut = og.ExecutionAttributeState.ENABLED
        return True
