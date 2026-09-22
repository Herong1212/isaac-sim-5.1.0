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
import omni.graph.core as og
import omni.usd
from omni.replicator.core import utils


class OgnGetPrimAtPath:
    @staticmethod
    def initialize(graph_context, node):
        node.get_attribute("inputs:paths").register_value_changed_callback(OgnGetPrimAtPath.on_value_changed_callback)

    @staticmethod
    def on_value_changed_callback(attr) -> None:
        # Gather paths immediately on node creation
        stage = omni.usd.get_context().get_stage()
        node = attr.get_node()
        paths = attr.get()
        valid_paths = []
        for path in paths:
            if not stage.GetPrimAtPath(str(path)).IsValid():
                carb.log_warn(f"Cannot find prim {path} in the stage.")
            else:
                valid_paths.append(str(path))

        node.get_attribute("outputs:prims").set(valid_paths)

    @staticmethod
    def compute(db) -> bool:
        if db.inputs.paths is None or len(db.inputs.paths) == 0:
            carb.log_warn("Path value is empty.")
            db.outputs.execOut = og.ExecutionAttributeState.DISABLED
            return False

        paths = db.inputs.paths

        stage = omni.usd.get_context().get_stage()

        for path in paths:
            if not stage.GetPrimAtPath(str(path)).IsValid():
                carb.log_warn(f"Cannot find prim {path} in the stage.")
                db.outputs.execOut = og.ExecutionAttributeState.DISABLED
                return False

        db.outputs.execOut = og.ExecutionAttributeState.ENABLED
        db.outputs.prims = [str(p) for p in paths]
        return True
