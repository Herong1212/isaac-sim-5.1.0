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

import json
from pathlib import Path
from typing import List

import carb
import omni.graph.core as og
import omni.timeline
import omni.usd
from pxr import Gf, Sdf, UsdShade

manager = omni.kit.app.get_app().get_extension_manager()
ext_id = manager.get_enabled_extension_id("omni.replicator.core")
ext_path = manager.get_extension_path(ext_id)
MDL_FOLDER = Path(ext_path).joinpath("mdl").as_posix()


class OgnModifyProjectionMaterial:
    @staticmethod
    def compute(db) -> bool:
        projection_prim_paths = db.inputs.prims
        in_positions = db.inputs.position if db.inputs.position is not None else None
        in_rotations = db.inputs.rotation if db.inputs.rotation is not None else None
        in_scales = db.inputs.scale if db.inputs.scale is not None else None
        in_diffuse = db.inputs.diffuse if db.inputs.diffuse is not None else None
        in_normal = db.inputs.normal if db.inputs.normal is not None else None
        in_roughness = db.inputs.roughness if db.inputs.roughness is not None else None
        in_metallic = db.inputs.metallic if db.inputs.metallic is not None else None
        in_texture_group = db.inputs.textureGroup if db.inputs.textureGroup is not None else None

        # Validate input
        if not projection_prim_paths:
            db.outputs.execOut = og.ExecutionAttributeState.DISABLED
            return False

        stage = omni.usd.get_context().get_stage()
        projection_prims = [stage.GetPrimAtPath(str(pp)) for pp in projection_prim_paths]
        num_prims = len(projection_prims)

        if len(in_positions) > 0 and len(in_positions) != num_prims:
            if len(in_positions) == 1:
                in_positions = in_positions * num_prims
            else:
                db.log_error(f"Expected {num_prims} position inputs, got {len(in_positions)}")
                db.outputs.execOut = og.ExecutionAttributeState.DISABLED
                return False
        if len(in_rotations) > 0 and len(in_rotations) != num_prims:
            if len(in_rotations) == 1:
                in_rotations = in_rotations * num_prims
            else:
                db.log_error(f"Expected {num_prims} rotation inputs, got {len(in_rotations)}")
                db.outputs.execOut = og.ExecutionAttributeState.DISABLED
                return False
        if len(in_scales) > 0 and len(in_scales) != num_prims:
            if len(in_scales) == 1:
                in_scales = in_scales * num_prims
            else:
                db.log_error(f"Expected {num_prims} scale inputs, got {len(in_scales)}")
                db.outputs.execOut = og.ExecutionAttributeState.DISABLED
                return False
        # Use inputs as suffix keys for texture group if there is one
        if in_texture_group:
            if isinstance(in_diffuse, List) and len(in_diffuse) != 0:
                in_diffuse = in_diffuse[0]
            if isinstance(in_normal, List) and len(in_normal) != 0:
                in_normal = in_normal[0]
            if isinstance(in_roughness, List) and len(in_roughness) != 0:
                in_roughness = in_roughness[0]
            if isinstance(in_metallic, List) and len(in_metallic) != 0:
                in_metallic = in_metallic[0]
            if len(in_texture_group) > 1:
                db.log_error("Expected one texure group, got multiple.")
                db.outputs.execOut = og.ExecutionAttributeState.DISABLED
                return False
        else:
            if len(in_diffuse) > 0 and len(in_diffuse) != num_prims:
                if len(in_diffuse) == 1:
                    in_diffuse = in_diffuse * num_prims
                else:
                    db.log_error(f"Expected {num_prims} diffuse inputs, got {len(in_diffuse)}")
                    db.outputs.execOut = og.ExecutionAttributeState.DISABLED
                    return False
            if len(in_normal) > 0 and len(in_normal) != num_prims:
                if len(in_normal) == 1:
                    in_normal = in_normal * num_prims
                else:
                    db.log_error(f"Expected {num_prims} normal inputs, got {len(in_normal)}")
                    db.outputs.execOut = og.ExecutionAttributeState.DISABLED
                    return False
            if len(in_roughness) > 0 and len(in_roughness) != num_prims:
                if len(in_roughness) == 1:
                    in_roughness = in_roughness * num_prims
                else:
                    db.log_error(f"Expected {num_prims} roughness inputs, got {len(in_roughness)}")
                    db.outputs.execOut = og.ExecutionAttributeState.DISABLED
                    return False
            if len(in_metallic) > 0 and len(in_metallic) != num_prims:
                if len(in_metallic) == 1:
                    in_metallic = in_metallic * num_prims
                else:
                    db.log_error(f"Expected {num_prims} metallic inputs, got {len(in_metallic)}")
                    db.outputs.execOut = og.ExecutionAttributeState.DISABLED
                    return False

        for idx, projection_prim in enumerate(projection_prims):
            # Update primvar values
            try:
                if not projection_prim.GetAttribute("primvars:projection_prim").IsValid():
                    projection_proxy_prim = stage.GetPrimAtPath(
                        projection_prim.GetAttribute("primvars:proxy_prim").Get()
                    )
                else:
                    carb.log_error(
                        "Projection does not have an associated proxy prim! Create first with rep.create.projection_material."
                    )
                    db.outputs.execOut = og.ExecutionAttributeState.DISABLED
                    return False

                # Get Prim Direction Vectors
                proxy_world_trans = omni.usd.get_world_transform_matrix(projection_proxy_prim)

                # Set the rotation quat manually, might be a bug when setting scale?
                if in_rotations.any():
                    rotation = Gf.Vec3d(in_rotations[idx].tolist())
                else:
                    rotation = projection_proxy_prim.GetAttribute("xformOp:rotateXYZ").Get()
                x_axis = Gf.Rotation(Gf.Vec3d.XAxis(), rotation[0])
                y_axis = Gf.Rotation(Gf.Vec3d.YAxis(), rotation[1])
                z_axis = Gf.Rotation(Gf.Vec3d.ZAxis(), rotation[2])
                full_rotation = x_axis * y_axis * z_axis
                proxy_world_trans.SetRotate(full_rotation)

                rotation_quat = proxy_world_trans.ExtractRotationQuat()
                projection_quat = (
                    rotation_quat.imaginary[0],
                    rotation_quat.imaginary[1],
                    rotation_quat.imaginary[2],
                    rotation_quat.real,
                )

                # Get Prim Position and Scale
                if in_positions.any():
                    position = Gf.Vec3d(in_positions[idx].tolist())
                else:
                    position = projection_proxy_prim.GetAttribute("xformOp:translate").Get()

                if in_scales.any():
                    scale = Gf.Vec3d(in_scales[idx].tolist())
                else:
                    scale = projection_proxy_prim.GetAttribute("xformOp:scale").Get()
                scale = (scale[0], scale[1], scale[2])

                # Set transform attributes to Target Prim
                projection_prim.GetAttribute("primvars:projection_quat").Set(projection_quat)
                projection_prim.GetAttribute("primvars:projection_position").Set(position)
                projection_prim.GetAttribute("primvars:projection_scale").Set(scale)

                # Update material properties if provided
                material = UsdShade.MaterialBindingAPI(projection_prim).GetDirectBinding().GetMaterial()
                rel = UsdShade.MaterialBindingAPI(projection_prim).GetDirectBinding().GetBindingRel()
                UsdShade.MaterialBindingAPI(projection_prim).SetMaterialBindingStrength(
                    rel, UsdShade.Tokens.weakerThanDescendants
                )
                projection_mat_prim = material.GetPrim().GetChild("Shader")

                if projection_mat_prim.IsValid():
                    if in_texture_group:
                        texture_group = json.loads(in_texture_group[0])
                        # Get just the paths, don't care about the prefix
                        texture_group = texture_group[next(iter(texture_group))]
                    else:
                        texture_group = None
                    if in_diffuse:
                        if not projection_mat_prim.GetAttribute("inputs:diffuse_texture").IsValid():
                            projection_mat_prim.CreateAttribute(
                                "inputs:diffuse_texture", Sdf.ValueTypeNames.Asset, custom=True
                            ).Set("")
                        if texture_group:
                            projection_mat_prim.GetAttribute("inputs:diffuse_texture").Set(
                                str(texture_group[in_diffuse])
                            )
                        else:
                            projection_mat_prim.GetAttribute("inputs:diffuse_texture").Set(str(in_diffuse[idx]))

                    if in_normal:
                        if not projection_mat_prim.GetAttribute("inputs:normalmap_texture").IsValid():
                            projection_mat_prim.CreateAttribute(
                                "inputs:normalmap_texture", Sdf.ValueTypeNames.Asset, custom=True
                            ).Set("")
                        if texture_group:
                            projection_mat_prim.GetAttribute("inputs:normalmap_texture").Set(
                                str(texture_group[in_normal])
                            )
                        else:
                            projection_mat_prim.GetAttribute("inputs:normalmap_texture").Set(str(in_normal[idx]))

                    if in_roughness:
                        if not projection_mat_prim.GetAttribute("inputs:reflectionroughness_texture").IsValid():
                            projection_mat_prim.CreateAttribute(
                                "inputs:reflectionroughness_texture", Sdf.ValueTypeNames.Asset, custom=True
                            ).Set("")
                        if texture_group:
                            projection_mat_prim.GetAttribute("inputs:reflectionroughness_texture").Set(
                                str(texture_group[in_roughness])
                            )
                        else:
                            projection_mat_prim.GetAttribute("inputs:reflectionroughness_texture").Set(
                                str(in_roughness[idx])
                            )
                    if in_metallic:
                        if not projection_mat_prim.GetAttribute("inputs:metallic_texture").IsValid():
                            projection_mat_prim.CreateAttribute(
                                "inputs:metallic_texture", Sdf.ValueTypeNames.Asset, custom=True
                            ).Set("")
                        if texture_group:
                            projection_mat_prim.GetAttribute("inputs:metallic_texture").Set(
                                str(texture_group[in_metallic])
                            )
                        else:
                            projection_mat_prim.GetAttribute("inputs:metallic_texture").Set(str(in_metallic[idx]))

            except Exception as error:
                # If anything causes compute to fail report the error and return False
                db.outputs.execOut = og.ExecutionAttributeState.DISABLED
                db.log_error(str(error))
                return False

        db.outputs.execOut = og.ExecutionAttributeState.ENABLED

        return True
