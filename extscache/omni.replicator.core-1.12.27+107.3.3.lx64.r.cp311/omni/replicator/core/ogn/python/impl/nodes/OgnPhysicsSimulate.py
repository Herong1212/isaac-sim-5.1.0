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

import omni.graph.core as og
import omni.physx
import pxr
from omni.replicator.core.functional import physics


class OgnPhysicsSimulate:
    @staticmethod
    def compute(db) -> bool:
        sim_time = db.inputs.simulationTime
        step_dt = db.inputs.stepDt
        physics_scene_inputs = db.inputs.physicsScene

        if sim_time <= 0:
            db.log_error(f"Invalid value for 'time'. Expected a positive float value > 0, got '{time}'")
            return False
        if step_dt <= 0:
            db.log_error(f"Invalid value for 'stepDt'. Expected a positive float value > 0, got '{step_dt}'")
            return False
        if sim_time < step_dt:
            db.log_error(f"Invalid value for 'time'. Time value must be larger than 'stepDt: {step_dt}'")
            return False

        # Validate Physics scenes
        stage = omni.usd.get_context().get_stage()
        physics_scenes = []
        for ps in physics_scene_inputs:
            physics_scene = str(ps)
            if not pxr.Sdf.Path.IsValidPathString(physics_scene) or not stage.GetPrimAtPath(physics_scene).IsValid():
                db.log_error(f"Skipping physics scene '{physics_scene}, prim path is invalid.")
                db.outputs.execOut = og.ExecutionAttributeState.DISABLED
                return False
            physics_scene_type = stage.GetPrimAtPath(physics_scene).GetTypeName()
            if physics_scene_type != "PhysicsScene":
                db.log_error(
                    f"Skipping physics scene '{physics_scene}', got type '{physics_scene_type}' instead of 'PhysicsScene'."
                )
                db.outputs.execOut = og.ExecutionAttributeState.DISABLED
                return False
            physics_scenes.append(physics_scene)

        if physics_scenes:
            for physics_scene in physics_scenes:
                physics.simulate(sim_time, step_dt, physics_scene)
        else:
            physics.simulate(sim_time, step_dt)

        db.outputs.execOut = og.ExecutionAttributeState.ENABLED
        return True
