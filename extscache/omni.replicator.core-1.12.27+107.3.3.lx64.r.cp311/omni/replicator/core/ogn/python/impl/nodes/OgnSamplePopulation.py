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


class OgnSamplePopulation:
    @staticmethod
    def internal_state():
        return rep.randomizer.objects.Population()

    @staticmethod
    def compute(db) -> bool:
        try:
            population = db.shared_state
            population_prim_path = db.inputs.populationPath
            if population_prim_path:
                population.population_prim_path = population_prim_path[0]

            input_path_prims = db.inputs.prims
            input_paths = db.inputs.paths
            prim_paths = []
            if input_path_prims:
                prim_paths += [str(pp) for pp in input_path_prims]
            if input_paths:
                prim_paths += input_paths

            if len(prim_paths) == 0:
                db.outputs.exec = og.ExecutionAttributeState.ENABLED
                return True

            population.usd_paths = prim_paths
            population.mode = db.inputs.mode
            population.set_population_name(db.inputs.populationName)
            population.use_cache = db.inputs.useCache
            population.semantics = [tuple(s.split(",")) for s in db.inputs.semantics]

        except Exception as error:
            db.log_error(f"Population Error: {error}")
            db.outputs.exec = og.ExecutionAttributeState.DISABLED
            return False

        prim_paths = population.populate()

        db.node.get_attribute("inputs:populationPath").set([population.population_prim_path])

        db.outputs.exec = og.ExecutionAttributeState.ENABLED
        db.outputs.prims = [str(pp) for pp in prim_paths]
        return True
