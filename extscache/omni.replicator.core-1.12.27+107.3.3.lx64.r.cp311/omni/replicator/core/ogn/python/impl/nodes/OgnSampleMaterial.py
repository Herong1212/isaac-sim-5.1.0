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

import os
import re

import carb
import numpy as np
import omni.graph.core as og
import omni.replicator.core as rep
import omni.timeline
import omni.usd
from omni.replicator.core import utils
from omni.replicator.core.create import REPLICATOR_SCOPE
from omni.replicator.core.ogn.OgnSampleMaterialDatabase import OgnSampleMaterialDatabase
from pxr import Sdf, UsdShade

LOOKS_PATH = f"{REPLICATOR_SCOPE}/Looks"


class OgnSampleMaterialInternalState:
    def __init__(self):
        self.material_paths = []
        self.mdl_mapping = {}
        self._mdl_cached = {}
        self.rng = rep.rng.ReplicatorRNG()
        self.max_cached_materials = 0

    def set_mdl_mapping(self, mdls):
        # Set all mdls to unused
        for mdl in self._mdl_cached:
            self._mdl_cached[mdl] = True

        stage = omni.usd.get_context().get_stage()
        if not stage.GetPrimAtPath(LOOKS_PATH):
            stage.DefinePrim(LOOKS_PATH, "Scope")
        for mdl in mdls:
            if mdl not in self.mdl_mapping:
                mtl_name, _ = os.path.splitext(os.path.split(mdl)[-1])
                self.mdl_mapping[mdl] = omni.usd.get_stage_next_free_path(stage, f"{LOOKS_PATH}/{mtl_name}", False)

    def remove_mdl_material(self, mdl):
        if mdl not in self.mdl_mapping:
            return

        path = self.mdl_mapping.get(mdl)
        stage = omni.usd.get_context().get_stage()
        if path and stage.GetPrimAtPath(path):
            stage.RemovePrim(path)

        # Remove from list of cached mdls
        if mdl in self._mdl_cached:
            self._mdl_cached.pop(mdl)

    def clear_mdl_materials(self):
        # Remove all mdl materials in stage and clear mdl mapping
        for mdl in self.mdl_mapping:
            self.remove_mdl_material(mdl)
        self.mdl_mapping.clear()

    def get_material_prim(self, prim_path):
        if prim_path in self.mdl_mapping:
            mdl = prim_path
            prim_path = self.mdl_mapping[mdl]
            self._mdl_cached[mdl] = False
        stage = omni.usd.get_context().get_stage()
        if not stage.GetPrimAtPath(str(prim_path)) and re.fullmatch("^.*\.mdl$", mdl):
            mtl_name, _ = os.path.splitext(os.path.split(mdl)[-1])
            utils.create_material(mtl_url=mdl, mtl_name=mtl_name, mtl_path=prim_path)

        return stage.GetPrimAtPath(str(prim_path))

    def clean_mdl_cached(self):
        """Remove cached materials if exceeding max cache size"""
        cached_mdls = [mdl for mdl in self._mdl_cached if self._mdl_cached[mdl]]
        while cached_mdls and sum(self._mdl_cached.values()) > self.max_cached_materials:
            self.remove_mdl_material(cached_mdls.pop())


class OgnSampleMaterial:
    @staticmethod
    def internal_state():
        return OgnSampleMaterialInternalState()

    @staticmethod
    def release(node):
        # clear created mdls
        state = OgnSampleMaterialDatabase.shared_internal_state(node)
        state.clear_mdl_materials()
        rep.rng.release(node.get_prim_path())

    @staticmethod
    def compute(db) -> bool:
        state = db.shared_state
        use_material_prims = db.inputs.useMaterialPrim

        state.max_cached_materials = db.inputs.maxCachedMaterials

        stage = omni.usd.get_context().get_stage()
        sample_prim_paths = db.inputs.prims

        mdls = []
        if use_material_prims:
            material_prim_paths = db.inputs.materialPrim
        else:
            materials = db.inputs.materialPaths
            mdls = [m for m in materials if re.fullmatch("^.*\.mdl$", m)]
            remaining_materials = [m for m in materials if m not in mdls]
            valid_material_prims = [m for m in remaining_materials if stage.GetPrimAtPath(m)]

            state.set_mdl_mapping(mdls)
            material_prim_paths = valid_material_prims

        if len(sample_prim_paths) == 0 or len(material_prim_paths) + len(mdls) == 0:
            db.outputs.execOut = og.ExecutionAttributeState.ENABLED
            return True

        sample_prims = [stage.GetPrimAtPath(str(prim_path)) for prim_path in sample_prim_paths]
        material_prims = [stage.GetPrimAtPath(str(prim_path)) for prim_path in material_prim_paths]

        # going through all of the prims/prototypes of point instancers
        prims_and_protos = list()
        for prim in sample_prims:
            if prim.GetTypeName() == "PointInstancer":
                protos = prim.GetRelationship("prototypes").GetTargets()
                prims_and_protos.extend([stage.GetPrimAtPath(str(path)) for path in protos])
            else:
                prims_and_protos.append(prim)

        try:
            for prim in material_prims:
                prim_type = prim.GetTypeName()
                if prim_type != "Material":
                    raise ValueError(
                        f"Expected prim at {prim.GetPath()} to be of type UsdShade.Material but got type {prim_type}"
                    )
        except Exception as error:
            db.log_error(f"SampleMaterial Error: {error}")
            db.outputs.execOut = og.ExecutionAttributeState.DISABLED
            return False

        for material in material_prim_paths + mdls:
            if material not in state.material_paths:
                state.material_paths.append(material)

        num_samples = len(prims_and_protos)

        is_seed_valid = db.inputs.seed is not None
        is_seed_changed = state.rng is None or db.inputs.seed != state.rng.seed
        if is_seed_valid and is_seed_changed:
            node_id = db.inputs.nodeId if db.node.get_attribute_exists("inputs:nodeId") else 0
            state.rng.initialize(db.inputs.seed, db.node, node_id)

        # FIXME: If the upstream node is a choice node, there is double sampling.
        sampled_indices = state.rng.generator.integers(len(state.material_paths), size=num_samples)
        for idx, sample_prim in enumerate(prims_and_protos):
            material = UsdShade.Material(state.get_material_prim(state.material_paths[sampled_indices[idx]]))
            UsdShade.MaterialBindingAPI(sample_prim).Bind(material)
            UsdShade.MaterialBindingAPI.Apply(sample_prim)

        # Clear unused materials beyond specified max to avoid over-accumulating materials in scene
        state.clean_mdl_cached()

        db.outputs.execOut = og.ExecutionAttributeState.ENABLED
        return True
