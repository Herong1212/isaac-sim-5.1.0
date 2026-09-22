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
from dataclasses import dataclass
from typing import Tuple

import carb
import omni.graph.core as og
import omni.timeline
import omni.usd
from omni.replicator.core import utils
from pxr import Gf, Sdf, Usd, UsdShade

MDL = "OmniPBR.mdl"
LOOKS_PATH = "/Replicator/Looks"


@dataclass
class OmniPBR_Params:
    diffuse: Tuple[float] = None
    diffuse_texture: str = None
    texture_scale: Tuple[float] = None
    texture_rotate: Tuple[float] = None
    roughness: float = None
    roughness_texture: str = None
    metallic: float = None
    metallic_texture: str = None
    project_uvw: bool = False


class OgnSampleOmniPBRInternalState:
    def __init__(self):
        stage = omni.usd.get_context().get_stage()
        if not stage.GetPrimAtPath(LOOKS_PATH):
            stage.DefinePrim(LOOKS_PATH, "Scope")
        self.material_cache = []
        self.last_index = 0
        self.disabled_instancing_cache = set()

    def disable_scene_instancing(self, prim):
        """Disable scene instancing for the specified prim and its descendants

        Args:
            prim: Prim for which to disable scene instancing
        """
        prim_path = str(prim.GetPath())
        if prim_path in self.disabled_instancing_cache:
            return
        for p in Usd.PrimRange(prim):
            if p.IsInstanceable():
                carb.log_info(f"SampleOmniPBR has disabled scene instancing on prim at {prim_path}")
                p.SetInstanceable(False)
        self.disabled_instancing_cache.add(prim_path)

    def modify_material(self, prim, params):
        material, _ = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()
        shader = UsdShade.Shader(omni.usd.get_shader_from_material(material.GetPrim(), True))

        # Set value inputs
        if params.diffuse:
            shader.GetInput("diffuse_color_constant").Set(params.diffuse)
        if params.roughness:
            shader.GetInput("reflection_roughness_constant").Set(params.roughness)
        if params.metallic:
            shader.GetInput("metallic_constant").Set(params.metallic)

        # Set texture inputs
        if params.diffuse_texture:
            shader.GetInput("diffuse_texture").Set(params.diffuse_texture)
        if params.roughness_texture:
            shader.GetInput("reflectionroughness_texture").Set(params.roughness_texture)
        if params.metallic_texture:
            shader.GetInput("metallic_texture").Set(params.metallic_texture)
        if params.texture_scale:
            shader.GetInput("texture_scale").Set(Gf.Vec2f(params.texture_scale))
        if params.texture_rotate:
            shader.GetInput("texture_rotate").Set(params.texture_rotate)
        # Set other attributes
        shader.GetInput("project_uvw").Set(params.project_uvw)

    def add_material(self):
        stage = omni.usd.get_context().get_stage()
        mtl_name, _ = os.path.splitext(MDL)
        prim_path = omni.usd.get_stage_next_free_path(stage, f"{LOOKS_PATH}/{MDL.split('.')[0]}", False)
        utils.create_material(mtl_url=MDL, mtl_name=mtl_name, mtl_path=prim_path)
        material_prim = stage.GetPrimAtPath(prim_path)
        shader = UsdShade.Shader(omni.usd.get_shader_from_material(material_prim, True))

        # Add value inputs]
        shader.CreateInput("diffuse_color_constant", Sdf.ValueTypeNames.Color3f)
        shader.CreateInput("reflection_roughness_constant", Sdf.ValueTypeNames.Float)
        shader.CreateInput("metallic_constant", Sdf.ValueTypeNames.Float)

        # Add texture inputs
        shader.CreateInput("diffuse_texture", Sdf.ValueTypeNames.Asset)
        shader.CreateInput("reflectionroughness_texture", Sdf.ValueTypeNames.Asset)
        shader.CreateInput("metallic_texture", Sdf.ValueTypeNames.Asset)

        # Add other attributes
        shader.CreateInput("project_uvw", Sdf.ValueTypeNames.Bool)

        # Add texture scale and rotate
        shader.CreateInput("texture_scale", Sdf.ValueTypeNames.Float2)
        shader.CreateInput("texture_rotate", Sdf.ValueTypeNames.Float)

        material = UsdShade.Material(material_prim)
        self.material_cache.append(str(material.GetPath()))
        return material

    def initialize_materials(self, prims):
        for prim in prims:
            cur_material, _ = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()
            if str(cur_material.GetPath()) not in self.material_cache:
                material = self.add_material()
                UsdShade.MaterialBindingAPI(prim).Bind(material, UsdShade.Tokens.strongerThanDescendants)
                UsdShade.MaterialBindingAPI.Apply(prim)

    def clear(self):
        stage = omni.usd.get_context().get_stage()
        for _, prim in self.material_cache:
            stage.RemovePrim(prim)
        self.material_cache = []


class OgnSampleOmniPBR:
    @staticmethod
    def internal_state():
        return OgnSampleOmniPBRInternalState()

    @staticmethod
    def compute(db) -> bool:
        state = db.shared_state

        sample_prim_paths = db.inputs.prims

        sample_prim_paths = utils.get_non_xform_prims(sample_prim_paths)
        prims = utils.find_prims(sample_prim_paths, db.inputs.mode)

        # Exclude projection prims
        prims = [p for p in prims if not p.HasAttribute("replicatorProjection")]

        nones = [None] * len(prims)
        diffuse_samples = db.inputs.diffuse.tolist()
        diffuse_texture_samples = db.inputs.diffuseTexture
        roughness_samples = db.inputs.roughness.tolist()
        roughness_texture_samples = db.inputs.roughnessTexture
        metallic_samples = db.inputs.metallic.tolist()
        metallic_texture_samples = db.inputs.metallicTexture
        texture_scale = db.inputs.textureScale.tolist()
        texture_rotate = db.inputs.textureRotate.tolist()

        for material_attr in [
            diffuse_samples,
            diffuse_texture_samples,
            roughness_samples,
            roughness_texture_samples,
            metallic_samples,
            metallic_texture_samples,
        ]:
            if len(material_attr) == 0:
                material_attr = nones

        # This has to happen outside of change block
        state.initialize_materials(prims)

        # Binding materials is expensive, prefer modifying bound materials
        with Sdf.ChangeBlock():
            for idx, prim in enumerate(prims):
                state.disable_scene_instancing(prim)
                mat_params = OmniPBR_Params()
                if diffuse_samples:
                    mat_params.diffuse = tuple(diffuse_samples[idx])
                if diffuse_texture_samples:
                    mat_params.diffuse_texture = "".join(diffuse_texture_samples[idx])
                if roughness_samples:
                    mat_params.roughness = roughness_samples[idx]
                if roughness_texture_samples:
                    mat_params.roughness_texture = "".join(roughness_texture_samples[idx])
                if metallic_samples:
                    mat_params.metallic = metallic_samples[idx]
                if metallic_texture_samples:
                    mat_params.metallic_texture = "".join(metallic_texture_samples[idx])
                if texture_scale:
                    mat_params.texture_scale = texture_scale[idx]
                if texture_rotate:
                    mat_params.texture_rotate = texture_rotate[idx]
                mat_params.project_uvw = db.inputs.projectUVW
                state.modify_material(prim, mat_params)

        db.outputs.execOut = og.ExecutionAttributeState.ENABLED
        return True
