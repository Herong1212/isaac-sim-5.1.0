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
This is the implementation of the OGN node defined in OgnMeshDecal.ogn
"""

from ast import literal_eval

# Array or tuple values are accessed as numpy arrays so you probably need this import
import carb
import numpy as np
import omni.graph.core as og
import omni.replicator.core as rep
import omni.replicator.core.functional as F
import omni.usd
from pxr import Gf


class OgnMeshDecal:
    @staticmethod
    def compute(db) -> bool:
        """Create decal"""
        prims = db.inputs.prims
        decal_prims = db.inputs.decalPrim
        materials = db.inputs.materialPrim
        in_diffuse = db.inputs.diffuse if db.inputs.diffuse is not None else None
        in_normal = db.inputs.normal if db.inputs.normal is not None else None
        in_roughness = db.inputs.roughness if db.inputs.roughness is not None else None
        in_metallic = db.inputs.metallic if db.inputs.metallic is not None else None
        in_opacity = db.inputs.opacity if db.inputs.opacity is not None else None
        in_texture_group = db.inputs.textureGroup if db.inputs.textureGroup is not None else None
        in_semantics = db.inputs.semantics
        if in_semantics:
            in_semantics = literal_eval(in_semantics)
        else:
            in_semantics = {}
        in_position = db.inputs.position if db.inputs.position is not None else None
        in_rotation = db.inputs.rotation if db.inputs.rotation is not None else None
        in_scale = db.inputs.scale if db.inputs.scale is not None else None

        if len(prims) == 0:
            return False

        # This only works on a single mesh at the moment
        if len(prims) != 1:
            carb.log_error(f"Mesh decal is limited to a single target mesh.")
            db.outputs.execOut = og.ExecutionAttributeState.DISABLED
            return False

        if decal_prims:
            if len(decal_prims) != 1:
                carb.log_error(f"Only a single decal prim can be modified.")
                db.outputs.execOut = og.ExecutionAttributeState.DISABLED
                return False
            else:
                in_decal = str(decal_prims[0])
        else:
            in_decal = None

        if materials:
            if len(materials) != 1:
                carb.log_error(f"Mesh decal is limited to a single material.")
                db.outputs.execOut = og.ExecutionAttributeState.DISABLED
                return False
            else:
                in_material = str(materials[0])
        else:
            in_material = None

        try:
            decal_prim_path = rep.create_mesh_decal(
                prim_path=str(prims[0]),
                decal_path=in_decal,
                material_path=in_material,
                texture_group=in_texture_group,
                diffuse=in_diffuse,
                normal=in_normal,
                roughness=in_roughness,
                metallic=in_metallic,
                opacity=in_opacity,
                position=Gf.Vec3d(in_position.tolist()),
                rotation=Gf.Vec3d(in_rotation.tolist()),
                scale=Gf.Vec3d(in_scale.tolist()),
                offset_normal=db.inputs.offsetNormal,
                offset_depth=db.inputs.offsetDepth,
            )
            if decal_prim_path:
                stage = omni.usd.get_context().get_stage()
                decal_prim = stage.GetPrimAtPath(decal_prim_path)
                F.modify.semantics(decal_prim, in_semantics)

        except Exception as error:
            db.log_error(f"OgnMeshDecal Error: {error}")
            db.outputs.exec = og.ExecutionAttributeState.DISABLED
            return False

        db.outputs.execOut = db.inputs.execIn
        return True
