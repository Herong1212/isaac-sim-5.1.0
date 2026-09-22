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

import numpy as np
import omni.graph.core as og
import omni.replicator.core as rep
import omni.timeline
import omni.usd
from pxr import Gf, Sdf


class OgnSampleLightInternalState:
    def __init__(self):
        self.rng = rep.rng.ReplicatorRNG()


class OgnSampleLight:
    @staticmethod
    def internal_state():
        return OgnSampleLightInternalState()

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

        # WAR to see if connected to prims output
        if len(sample_prim_paths) == 1 and stage.GetPrimAtPath(str(sample_prim_paths[0])).GetTypeName() == "Output":
            output_prim = stage.GetPrimAtPath(str(sample_prim_paths[0]))
            sample_prim_paths = output_prim.GetRelationship("prims").GetTargets()

        sample_prims = [stage.GetPrimAtPath(str(prim_path)) for prim_path in sample_prim_paths]

        color_min = np.array(db.inputs.colorMin)
        color_max = np.array(db.inputs.colorMax)
        intensity_range = np.array(db.inputs.intensityRange)
        temperature_range = np.array(db.inputs.temperatureRange)
        enable_temperature = db.inputs.enableTemperature

        # validate input
        try:
            for prim in sample_prims:
                prim_type = str(prim.GetTypeName())
                if "Light" not in prim_type:
                    raise ValueError(f"Expected prim at {prim.GetPath()} to be a light but got type {prim_type}")
            if np.any(np.logical_or(color_min < 0, color_min > 1)):
                raise ValueError(
                    f"Expected all values of inputs:colorMin to be within [0, 1] but instead received {color_min}"
                )
            if np.any(np.logical_and(color_max < 0, color_max > 1)):
                raise ValueError(
                    f"Expected all values of inputs:colorMax to be within [0, 1] but instead received {color_max}"
                )
            if np.any(color_min > color_max):
                raise ValueError(
                    "Expected values in inputs:colorMin to be less than or equal to values in inputs:colorMax, "
                    + f"but instead received {color_min} for inputs:colorMin and {color_max} for inputs:colorMax"
                )
            if np.any(intensity_range < 0):
                raise ValueError(
                    f"Expected both values in inputs:intensityRange to be greater than zero, but received {intensity_range}"
                )
            if intensity_range[0] > intensity_range[1]:
                raise ValueError(
                    f"Expected first value of inputs:intensityRange to be less than or equal to second value, but instead received {intensity_range}"
                )
            if enable_temperature:
                if np.any(np.logical_or(temperature_range < 1000, temperature_range > 10000)):
                    raise ValueError(
                        f"Expected both values in inputs:temperatureRange to be within [1000, 10000], but received {temperature_range}"
                    )
                if temperature_range[0] > temperature_range[1]:
                    raise ValueError(
                        f"Expected first value of inputs:temperatureRange to be less than or equal to second value, but instead received {temperature_range}"
                    )

        except Exception as error:
            db.log_error(f"SampleLight Error: {error}")
            db.outputs.execOut = og.ExecutionAttributeState.DISABLED
            return False

        num_samples = len(sample_prim_paths)

        is_seed_valid = db.inputs.seed is not None
        is_seed_changed = state.rng is None or db.inputs.seed != state.rng.seed
        if is_seed_valid and is_seed_changed:
            node_id = db.inputs.nodeId if db.node.get_attribute_exists("inputs:nodeId") else 0
            state.rng.initialize(db.inputs.seed, db.node, node_id)

        sampled_colors = state.rng.generator.uniform(color_min, color_max, size=(num_samples, 3))
        sampled_intensities = state.rng.generator.uniform(intensity_range[0], intensity_range[1], size=(num_samples,))
        if enable_temperature:
            sampled_temperatures = state.rng.generator.uniform(
                temperature_range[0], temperature_range[1], size=(num_samples,)
            )

        with Sdf.ChangeBlock():
            idx = 0
            for prim in sample_prims:
                prim.GetAttribute("inputs:color").Set(Gf.Vec3f(*sampled_colors[idx]))
                prim.GetAttribute("inputs:intensity").Set(sampled_intensities[idx])
                if enable_temperature:
                    prim.GetAttribute("inputs:enableColorTemperature").Set(True)
                    prim.GetAttribute("inputs:colorTemperature").Set(sampled_temperatures[idx])
                idx += 1

        db.outputs.execOut = og.ExecutionAttributeState.ENABLED
        return True
