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
import omni.usd
from omni.replicator.core import utils


# ======================================================================
class OgnPerAxisPose:
    @staticmethod
    def compute(db) -> bool:
        prim_paths = db.inputs.prims
        num_samples = db.inputs.numSamples

        fullValues = db.inputs.fullValues
        x_values = db.inputs.xValue
        y_values = db.inputs.yValue
        z_values = db.inputs.zValue

        if len(fullValues) != 0 and (len(x_values) != 0 or len(y_values) != 0 or len(z_values)):
            carb.log_warn(
                "Both full 3D value and per axis value is specified, the full value will overwrite per axis value."
            )

        if len(fullValues) != 0:
            if len(fullValues) == 1 and num_samples > 1:
                # Repeat value if single value supplied for multiple samples
                db.outputs.samples = fullValues.tolist() * num_samples
            else:
                db.outputs.samples = fullValues.tolist()
            db.outputs.exec = og.ExecutionAttributeState.ENABLED
            return True

        mode = db.inputs.mode

        stage = omni.usd.get_context().get_stage()

        base_value = [[0, 0, 0] for _ in range(len(prim_paths))]

        if num_samples > 1:
            if len(x_values) == 1:
                x_values = x_values.tolist() * num_samples
            if len(y_values) == 1:
                y_values = y_values.tolist() * num_samples
            if len(z_values) == 1:
                z_values = z_values.tolist() * num_samples

        if len(x_values) != 0 and len(x_values) != len(prim_paths):
            db.log_error(f"Could not create a pose for {len(prim_paths)} prim paths given {len(x_values)} x values.")
            return False
        if len(y_values) != 0 and len(y_values) != len(prim_paths):
            db.log_error(f"Could not create a pose for {len(prim_paths)} prim paths given {len(y_values)} x values.")
            return False
        if len(z_values) != 0 and len(z_values) != len(prim_paths):
            db.log_error(f"Could not create a pose for {len(prim_paths)} prim paths given {len(z_values)} x values.")
            return False

        for i, prim_path in enumerate(prim_paths):
            prim = stage.GetPrimAtPath(str(prim_path))

            original_value = None
            # Determine attribute name to extract the original values of each prim.
            if mode == "position":
                original_value = prim.GetAttribute("xformOp:translate").Get()
            elif mode == "rotation":
                for attr_name in prim.GetAttribute("xformOpOrder").Get():
                    if "rotate" in attr_name:
                        original_value = prim.GetAttribute(attr_name).Get()
            else:
                raise NotImplementedError(f"The attribute {mode} is not supported for per axis pose yet.")

            if len(x_values) != 0:
                base_value[i][0] = x_values[i]
            elif original_value is not None:
                base_value[i][0] = original_value[0]

            if len(y_values) != 0:
                base_value[i][1] = y_values[i]
            elif original_value is not None:
                base_value[i][1] = original_value[1]

            if len(z_values) != 0:
                base_value[i][2] = z_values[i]
            elif original_value is not None:
                base_value[i][2] = original_value[2]

        db.outputs.samples = base_value
        db.outputs.exec = og.ExecutionAttributeState.ENABLED

        return True
