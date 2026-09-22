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
import math
from typing import List, Tuple, Union

# Array or tuple values are accessed as numpy arrays so you probably need this import
import carb
import numpy as np
import omni.kit.commands
import omni.kit.material.library as mat_lib
import omni.timeline
import Semantics
import warp as wp
from pxr import Gf, Sdf, UsdGeom, UsdShade

# wp.config.mode = "debug"
# wp.config.verify_cuda = True


def triangulate(counts, indices):

    # triangulate
    num_tris = np.sum(np.subtract(counts, 2))
    num_tri_vtx = num_tris * 3
    tri_indices = np.zeros(num_tri_vtx, dtype=int)
    ctr = 0
    wedgeIdx = 0
    for nb in counts:
        for i in range(nb - 2):
            tri_indices[ctr] = indices[wedgeIdx]
            tri_indices[ctr + 1] = indices[wedgeIdx + i + 1]
            tri_indices[ctr + 2] = indices[wedgeIdx + i + 2]
            ctr += 3
        wedgeIdx += nb

    return tri_indices


def _apply_semantics(target_prim, semantics):
    """
    Apply semantics to the shell mesh so the projections have proper segmentation.
    """
    for s in semantics:
        instance_name = f"{s[0]}_{s[1]}"
        sem = Semantics.SemanticsAPI.Apply(target_prim, instance_name)
        sem.CreateSemanticTypeAttr()
        sem.CreateSemanticDataAttr()
        sem.GetSemanticTypeAttr().Set(s[0])
        sem.GetSemanticDataAttr().Set(s[1])


@wp.kernel
def compute_normals(points: wp.array(dtype=wp.vec3), normals: wp.array(dtype=wp.vec3), tris: wp.array(dtype=int)):

    tid = wp.tid()

    i = tris[tid * 3 + 0]
    j = tris[tid * 3 + 1]
    k = tris[tid * 3 + 2]

    p = points[i]
    q = points[j]
    r = points[k]

    n = wp.cross(q - p, r - p)

    wp.atomic_add(normals, i, n)
    wp.atomic_add(normals, j, n)
    wp.atomic_add(normals, k, n)


@wp.kernel
def normalize_normals(normals: wp.array(dtype=wp.vec3)):

    i = wp.tid()

    normals[i] = wp.normalize(normals[i])


@wp.func
def clip_segment(a: wp.vec3, b: wp.vec3, plane: wp.vec4):

    d = b - a
    t = -wp.dot(plane, wp.vec4(a[0], a[1], a[2], 1.0)) / wp.dot(plane, wp.vec4(d[0], d[1], d[2], 0.0))
    return a + wp.clamp(t, 0.0, 1.0) * d


@wp.func
def clip_normal(a: wp.vec3, b: wp.vec3, n0: wp.vec3, n1: wp.vec3, plane: wp.vec4):

    d = b - a
    t = -wp.dot(plane, wp.vec4(a[0], a[1], a[2], 1.0)) / wp.dot(plane, wp.vec4(d[0], d[1], d[2], 0.0))

    return wp.normalize(n0 + wp.clamp(t, 0.0, 1.0) * (n1 - n0))


@wp.kernel
def clip_mesh(
    points_in: wp.array(dtype=wp.vec3),
    points_out: wp.array(dtype=wp.vec3),
    normals_in: wp.array(dtype=wp.vec3),
    normals_out: wp.array(dtype=wp.vec3),
    points_count: wp.array(dtype=int),
    tris_in: wp.array(dtype=int),
    tris_out: wp.array(dtype=int),
    tris_count: wp.array(dtype=int),
    plane: wp.vec4,
    max_points: int,
    max_tris: int,
):

    tid = wp.tid()

    i0 = tris_in[tid * 3 + 0]
    i1 = tris_in[tid * 3 + 1]
    i2 = tris_in[tid * 3 + 2]

    p0 = points_in[i0]
    p1 = points_in[i1]
    p2 = points_in[i2]

    n0 = normals_in[i0]
    n1 = normals_in[i1]
    n2 = normals_in[i2]

    d0 = wp.dot(plane, wp.vec4(p0[0], p0[1], p0[2], 1.0))
    d1 = wp.dot(plane, wp.vec4(p1[0], p1[1], p1[2], 1.0))
    d2 = wp.dot(plane, wp.vec4(p2[0], p2[1], p2[2], 1.0))

    count = 0

    if d0 > 0.0:
        count += 1
    if d1 > 0.0:
        count += 1
    if d2 > 0.0:
        count += 1

    # all verts fail
    if count == 0:
        return

    # clipping case 1
    if count == 1:
        num_points = 3
        num_tris = 1

    # clipping case 2
    if count == 2:
        num_points = 4
        num_tris = 2

    # all verts pass
    if count == 3:
        num_points = 3
        num_tris = 1

    first_point = wp.atomic_add(points_count, 0, num_points)
    if first_point + num_points > max_points:
        return

    first_tri = wp.atomic_add(tris_count, 0, num_tris * 3)
    if first_tri + num_tris * 3 > max_tris:
        return

    out_index = first_point

    # point 0
    if d0 > 0.0:
        points_out[out_index] = p0
        normals_out[out_index] = n0
        out_index += 1

    # edge 0
    if d0 * d1 < 0.0:
        points_out[out_index] = clip_segment(p0, p1, plane)
        normals_out[out_index] = clip_normal(p0, p1, n0, n1, plane)
        out_index += 1

    # point 1
    if d1 > 0.0:
        points_out[out_index] = p1
        normals_out[out_index] = n1
        out_index += 1

    # edge 1
    if d1 * d2 < 0.0:
        points_out[out_index] = clip_segment(p1, p2, plane)
        normals_out[out_index] = clip_normal(p1, p2, n1, n2, plane)
        out_index += 1

    # point 2
    if d2 > 0.0:
        points_out[out_index] = p2
        normals_out[out_index] = n2
        out_index += 1

    # edge 2
    if d2 * d0 < 0.0:
        points_out[out_index] = clip_segment(p2, p0, plane)
        normals_out[out_index] = clip_normal(p2, p0, n2, n0, plane)
        out_index += 1

    # triangulate
    if num_points == 3:
        tris_out[first_tri + 0] = first_point + 0
        tris_out[first_tri + 1] = first_point + 1
        tris_out[first_tri + 2] = first_point + 2

    if num_points == 4:
        tris_out[first_tri + 0] = first_point + 0
        tris_out[first_tri + 1] = first_point + 1
        tris_out[first_tri + 2] = first_point + 3

        tris_out[first_tri + 3] = first_point + 1
        tris_out[first_tri + 4] = first_point + 2
        tris_out[first_tri + 5] = first_point + 3


@wp.kernel
def compute_uvs(
    points: wp.array(dtype=wp.vec3),
    texcoords: wp.array(dtype=float),
    plane_u: wp.vec4,
    plane_v: wp.vec4,
    xform: wp.mat44,
    width: float,
    height: float,
):

    tid = wp.tid()

    p = wp.transform_point(wp.transpose(xform), points[tid])

    u = wp.dot(wp.vec4(p[0], p[1], p[2], 1.0), plane_u)
    v = wp.dot(wp.vec4(p[0], p[1], p[2], 1.0), plane_v)

    texcoords[tid * 2 + 0] = 0.5 * u / width
    texcoords[tid * 2 + 1] = 0.5 * v / height


@wp.kernel
def offset_mesh(
    points_in: wp.array(dtype=wp.vec3),
    normals_in: wp.array(dtype=wp.vec3),
    points_out: wp.array(dtype=wp.vec3),
    offset: float,
):

    tid = wp.tid()

    p = points_in[tid]
    n = normals_in[tid]

    points_out[tid] = p + n * offset


def create_mesh_decal(
    prim_path: Union[str, Sdf.Path],
    decal_path: Union[str, Sdf.Path] = None,
    material_path: Union[str, Sdf.Path] = None,
    texture_group: List[str] = None,
    diffuse: str = None,
    normal: str = None,
    roughness: str = None,
    metallic: str = None,
    opacity: str = None,
    position: Gf.Vec3d = Gf.Vec3d(),
    rotation: Gf.Vec3d = Gf.Vec3d(),
    scale: Gf.Vec3d = Gf.Vec3d(1, 1, 1),
    offset_normal: float = 0.1,
    offset_depth: float = 0.0,
) -> str:
    """Create mesh decal"""
    stage = omni.usd.get_context().get_stage()

    # Assuming this only works on a single mesh at the moment
    if isinstance(prim_path, str) or isinstance(prim_path, Sdf.Path):
        prim = stage.GetPrimAtPath(str(prim_path))
    else:
        prim = prim_path

    # Can't edit instanceable prims
    if prim.IsInstanceable():
        prim.SetInstanceable(False)

    if prim.HasAttribute("replicatorXform"):
        mesh = UsdGeom.Mesh(prim.GetChildren()[0])
    else:
        mesh = UsdGeom.Mesh(prim)

    if not prim.IsValid():
        carb.log_error(f"Target prim is not valid!")
        return prim_path

    if material_path:
        if isinstance(material_path, str) or isinstance(material_path, Sdf.Path):
            material = stage.GetPrimAtPath(material_path)
        else:
            material = material_path
        if not material.IsValid():
            carb.log_error(f"Provided material is not valid!")
            return prim_path
    else:
        material = None

    if decal_path:
        decal_prim = stage.GetPrimAtPath(decal_path)

        if not decal_prim.IsValid() or decal_prim.GetTypeName() != "Mesh":
            carb.log_warn(f"Provided decal prim path not a mesh or valid, creating at {decal_path} instead.")
            decal_name = prim.GetName()
            decal_xform_path = f"{str(decal_path)}/Decal"
            new_decal_path = f"{str(decal_xform_path)}/{decal_name}"
            stage.DefinePrim(decal_xform_path, "Xform")
            _, tmp_prim_path = omni.kit.commands.execute("CreateMeshPrimWithDefaultXformCommand", prim_type="Cube")
            # Move prim
            omni.usd.duplicate_prim(stage, tmp_prim_path, new_decal_path)
            stage.RemovePrim(tmp_prim_path)
            decal_prim = stage.GetPrimAtPath(new_decal_path)

        if not decal_prim.GetAttribute("xformOp:translate"):
            UsdGeom.Xformable(decal_prim).AddTranslateOp()
        decal_prim.GetAttribute("xformOp:translate").Set(prim.GetAttribute("xformOp:translate").Get())
        if not decal_prim.GetAttribute("xformOp:rotateXYZ"):
            UsdGeom.Xformable(decal_prim).AddRotateXYZOp()
        decal_prim.GetAttribute("xformOp:rotateXYZ").Set(prim.GetAttribute("xformOp:rotateXYZ").Get())
        if not decal_prim.GetAttribute("xformOp:scale"):
            UsdGeom.Xformable(decal_prim).AddScaleOp()
        decal_prim.GetAttribute("xformOp:scale").Set(prim.GetAttribute("xformOp:scale").Get())
    else:
        decal_name = prim.GetName()
        if prim.HasAttribute("replicatorXform"):
            decal_xform_path = f"{str(prim.GetChildren()[0].GetPath())}/Decal"
        else:
            decal_xform_path = f"{str(prim.GetPath())}/Decal"
        decal_path = f"{str(decal_xform_path)}/{decal_name}"

        # If the decal prim doesn't exist, create it
        if not stage.GetPrimAtPath(decal_xform_path):
            stage.DefinePrim(decal_xform_path, "Xform")
            _, tmp_prim_path = omni.kit.commands.execute("CreateMeshPrimWithDefaultXformCommand", prim_type="Cube")
            # Move prim
            omni.usd.duplicate_prim(stage, tmp_prim_path, decal_path)
            stage.RemovePrim(tmp_prim_path)
        decal_prim = stage.GetPrimAtPath(decal_path)

    if not UsdGeom.PrimvarsAPI(decal_prim).GetPrimvar("doNotCastShadows"):
        UsdGeom.PrimvarsAPI(decal_prim).CreatePrimvar("doNotCastShadows", Sdf.ValueTypeNames.Bool)
    UsdGeom.PrimvarsAPI(decal_prim).GetPrimvar("doNotCastShadows").Set(True)

    if not decal_prim.GetAttribute("subdivisionScheme").Get():
        decal_prim.CreateAttribute("subdivisionScheme", Sdf.ValueTypeNames.Token)
    decal_prim.GetAttribute("subdivisionScheme").Set("none")

    # Apply material to decal if provided or create default OmniPBR
    if material:
        UsdShade.MaterialBindingAPI(decal_prim).Bind(UsdShade.Material(material), UsdShade.Tokens.weakerThanDescendants)
    else:
        on_mat = lambda mat_prim: UsdShade.MaterialBindingAPI(decal_prim).Bind(
            UsdShade.Material(mat_prim), UsdShade.Tokens.weakerThanDescendants
        )

        # Check that there isn't already a material on the target. Might need a better way to check this.
        if str(UsdShade.MaterialBindingAPI(decal_prim).GetDirectBinding().GetMaterial().GetPath()) == "":
            mat_path = mat_lib.create_mdl_material(stage, "OmniPBR.mdl", "OmniPBR", on_mat)
            material = stage.GetPrimAtPath(mat_path)
        else:
            material = stage.GetPrimAtPath(
                UsdShade.MaterialBindingAPI(decal_prim).GetDirectBinding().GetMaterial().GetPath()
            )
    UsdShade.MaterialBindingAPI.Apply(decal_prim)

    # Set textures from texture_group
    if material and (diffuse or normal or roughness or metallic):
        if texture_group:
            tex_group = json.loads(texture_group[0])
            # Get just the paths, don't care about the prefix
            tex_group = tex_group[next(iter(tex_group))]
        else:
            tex_group = None

        mat_shader = material.GetChild("Shader")
        if diffuse:
            if not mat_shader.GetAttribute("inputs:diffuse_texture").IsValid():
                mat_shader.CreateAttribute("inputs:diffuse_texture", Sdf.ValueTypeNames.Asset, custom=True).Set("")
            if tex_group:
                mat_shader.GetAttribute("inputs:diffuse_texture").Set(str(tex_group[diffuse]))
            else:
                mat_shader.GetAttribute("inputs:diffuse_texture").Set(str(diffuse))
        else:
            if not mat_shader.GetAttribute("inputs:diffuse_texture").IsValid():
                mat_shader.CreateAttribute("inputs:diffuse_texture", Sdf.ValueTypeNames.Asset, custom=True).Set("")
            else:
                mat_shader.GetAttribute("inputs:diffuse_texture").Set("")

        if normal:
            if not mat_shader.GetAttribute("inputs:normalmap_texture").IsValid():
                mat_shader.CreateAttribute("inputs:normalmap_texture", Sdf.ValueTypeNames.Asset, custom=True).Set("")
            if tex_group:
                mat_shader.GetAttribute("inputs:normalmap_texture").Set(str(tex_group[normal]))
            else:
                mat_shader.GetAttribute("inputs:normalmap_texture").Set(str(normal))
        else:
            if not mat_shader.GetAttribute("inputs:normalmap_texture").IsValid():
                mat_shader.CreateAttribute("inputs:normalmap_texture", Sdf.ValueTypeNames.Asset, custom=True).Set("")
            else:
                mat_shader.GetAttribute("inputs:normalmap_texture").Set("")

        if roughness:
            if not mat_shader.GetAttribute("inputs:reflectionroughness_texture").IsValid():
                mat_shader.CreateAttribute(
                    "inputs:reflectionroughness_texture", Sdf.ValueTypeNames.Asset, custom=True
                ).Set("")
            if tex_group:
                mat_shader.GetAttribute("inputs:reflectionroughness_texture").Set(str(tex_group[roughness]))
            else:
                mat_shader.GetAttribute("inputs:reflectionroughness_texture").Set(str(roughness))
        else:
            if not mat_shader.GetAttribute("inputs:reflectionroughness_texture").IsValid():
                mat_shader.CreateAttribute(
                    "inputs:reflectionroughness_texture", Sdf.ValueTypeNames.Asset, custom=True
                ).Set("")
            else:
                mat_shader.GetAttribute("inputs:reflectionroughness_texture").Set("")

        if metallic:
            if not mat_shader.GetAttribute("inputs:metallic_texture").IsValid():
                mat_shader.CreateAttribute("inputs:metallic_texture", Sdf.ValueTypeNames.Asset, custom=True).Set("")
            if tex_group:
                mat_shader.GetAttribute("inputs:metallic_texture").Set(str(tex_group[metallic]))
            else:
                mat_shader.GetAttribute("inputs:metallic_texture").Set(str(metallic))
        else:
            if not mat_shader.GetAttribute("inputs:metallic_texture").IsValid():
                mat_shader.CreateAttribute("inputs:metallic_texture", Sdf.ValueTypeNames.Asset, custom=True).Set("")
            else:
                mat_shader.GetAttribute("inputs:metallic_texture").Set("")

        if opacity:
            if not mat_shader.GetAttribute("inputs:opacity_texture").IsValid():
                mat_shader.CreateAttribute("inputs:opacity_texture", Sdf.ValueTypeNames.Asset, custom=True).Set("")
            if tex_group:
                mat_shader.GetAttribute("inputs:opacity_texture").Set(str(tex_group[opacity]))
            else:
                mat_shader.GetAttribute("inputs:opacity_texture").Set(str(opacity))

            if not mat_shader.GetAttribute("inputs:enable_opacity").IsValid():
                mat_shader.CreateAttribute("inputs:enable_opacity", Sdf.ValueTypeNames.Bool, custom=True).Set(True)
            mat_shader.GetAttribute("inputs:enable_opacity").Set(True)
            if not mat_shader.GetAttribute("inputs:enable_opacity_texture").IsValid():
                mat_shader.CreateAttribute("inputs:enable_opacity_texture", Sdf.ValueTypeNames.Bool, custom=True).Set(
                    True
                )
            mat_shader.GetAttribute("inputs:enable_opacity_texture").Set(True)
        else:
            if not mat_shader.GetAttribute("inputs:opacity_texture").IsValid():
                mat_shader.CreateAttribute("inputs:opacity_texture", Sdf.ValueTypeNames.Asset, custom=True).Set("")
            else:
                mat_shader.GetAttribute("inputs:opacity_texture").Set("")

    with wp.ScopedDevice("cuda:0"):
        if mesh:
            # Create Transform from translate, rotation and scale inputs
            # Rotation
            x_axis = Gf.Rotation(Gf.Vec3d.XAxis(), rotation[0])
            y_axis = Gf.Rotation(Gf.Vec3d.YAxis(), rotation[1])
            z_axis = Gf.Rotation(Gf.Vec3d.ZAxis(), rotation[2])
            rotation = x_axis * y_axis * z_axis

            # Scale
            m_scale = Gf.Matrix4d().SetScale(scale)

            clip_xform = m_scale * Gf.Matrix4d(rotation, position)

            # The projection happens from the origin to the edge of the default cube length
            clip_width = clip_height = clip_depth = 0.5 / UsdGeom.GetStageMetersPerUnit(stage)

            # DEBUG
            # print("Clip depth: " + str(clip_depth))
            # print("Clip height: " + str(clip_height))
            # print("Clip width: " + str(clip_width))
            # print("Clip xform: " + str(clip_xform))

            # Initialization
            mesh_points = mesh.GetPointsAttr().Get()
            mesh_indices = mesh.GetFaceVertexIndicesAttr().Get()
            mesh_counts = mesh.GetFaceVertexCountsAttr().Get()
            mesh_xform = UsdGeom.Xformable(mesh).ComputeLocalToWorldTransform(0.0)

            num_points = len(mesh_points)

            if num_points:

                # allow each tri to be cut once
                expand = 2

                max_points = len(mesh_indices) * expand
                max_tris = len(mesh_indices) * expand

                mesh_points = wp.array(mesh_points, dtype=wp.vec3)
                mesh_tris = wp.array(triangulate(mesh_counts, mesh_indices), dtype=int)

                clip_points0 = wp.zeros(max_points, dtype=wp.vec3)
                clip_points1 = wp.zeros(max_points, dtype=wp.vec3)

                clip_normals0 = wp.zeros(max_points, dtype=wp.vec3)
                clip_normals1 = wp.zeros(max_points, dtype=wp.vec3)

                clip_tris0 = wp.zeros(max_tris, dtype=int)
                clip_tris1 = wp.zeros(max_tris, dtype=int)

                clip_tris_count = wp.array([len(mesh_tris)], dtype=int)
                clip_points_count = wp.array([len(mesh_points)], dtype=int)

                clip_uvs = wp.zeros(max_points * 2, dtype=float)

        # Clipping
        # assign initial state to clipping output
        clip_points0.assign(mesh_points)
        clip_tris0.assign(mesh_tris)

        # compute normals
        clip_normals0.zero_()

        wp.launch(compute_normals, dim=int(len(mesh_tris) / 3), inputs=[clip_points0, clip_normals0, clip_tris0])
        wp.launch(normalize_normals, dim=len(mesh_points), inputs=[clip_normals0])

        clip_tris_count.assign([len(mesh_tris)])
        clip_points_count.assign([len(mesh_points)])

        planes = [
            Gf.Plane(Gf.Vec3d(0.0, 0.0, -1.0), 0.0),
            Gf.Plane(Gf.Vec3d(0.0, 0.0, 1.0), -clip_depth),
            Gf.Plane(Gf.Vec3d(1.0, 0.0, 0.0), -clip_width),
            Gf.Plane(Gf.Vec3d(-1.0, 0.0, 0.0), -clip_width),
            Gf.Plane(Gf.Vec3d(0.0, 1.0, 0.0), -clip_height),
            Gf.Plane(Gf.Vec3d(0.0, -1.0, 0.0), -clip_height),
        ]

        # transform planes from xform space to mesh local space
        for i, p in enumerate(planes):

            plane_world = p.Transform(clip_xform)
            plane_local = plane_world.Transform(mesh_xform.GetInverse())

            planes[i] = wp.vec4(
                plane_local.GetNormal()[0],
                plane_local.GetNormal()[1],
                plane_local.GetNormal()[2],
                -plane_local.GetDistanceFromOrigin(),
            )

        # clip against planes
        for plane in planes:

            num_points = int(clip_points_count.numpy()[0])
            num_tris = int(clip_tris_count.numpy()[0])

            clip_points_count.zero_()
            clip_tris_count.zero_()

            wp.launch(
                kernel=clip_mesh,
                dim=int(num_tris / 3),
                inputs=[
                    clip_points0,
                    clip_points1,
                    clip_normals0,
                    clip_normals1,
                    clip_points_count,
                    clip_tris0,
                    clip_tris1,
                    clip_tris_count,
                    plane,
                    max_points,
                    max_tris,
                ],
            )

            clip_points0, clip_points1 = clip_points1, clip_points0
            clip_normals0, clip_normals1 = clip_normals1, clip_normals0
            clip_tris0, clip_tris1 = clip_tris1, clip_tris0

        # Compute UVs
        clip_to_world = clip_xform
        mesh_to_world = mesh_xform

        mesh_to_clip = mesh_to_world * clip_to_world.GetInverse()

        scale_u = clip_to_world.TransformDir(Gf.Vec3d(1.0, 0.0, 0.0)).GetLength()
        scale_v = clip_to_world.TransformDir(Gf.Vec3d(0.0, 1.0, 0.0)).GetLength()

        plane_u = wp.vec4(1.0, 0.0, 0.0, clip_width)
        plane_v = wp.vec4(0.0, 1.0, 0.0, clip_height)

        num_points = int(clip_points_count.numpy()[0])
        num_tris = int(clip_tris_count.numpy()[0])

        wp.launch(
            compute_uvs,
            dim=num_points,
            inputs=[clip_points0, clip_uvs, plane_u, plane_v, mesh_to_clip, clip_width, clip_height],
        )

        vertices_offset = wp.clone(clip_points0)
        wp.launch(offset_mesh, dim=num_points, inputs=[clip_points0, clip_normals0, vertices_offset, offset_normal])

        # Set decal values
        UsdGeom.PrimvarsAPI(decal_prim).GetPrimvar("st").SetInterpolation("vertex")
        UsdGeom.Mesh(decal_prim).GetPointsAttr().Set(vertices_offset.numpy()[0:num_points])
        UsdGeom.Mesh(decal_prim).GetNormalsAttr().Set(clip_normals0.numpy()[0:num_points])
        if not decal_prim.GetAttribute("primvars:st").IsValid():
            decal_prim.CreateAttribute("primvars:st", Sdf.ValueTypeNames.TexCoord2fArray, custom=True).Set(
                clip_uvs.numpy().reshape((-1, 2))[0:num_points]
            )
        else:
            decal_prim.GetAttribute("primvars:st").Set(clip_uvs.numpy().reshape((-1, 2))[0:num_points])
        UsdGeom.Mesh(decal_prim).GetFaceVertexIndicesAttr().Set(clip_tris0.numpy()[0:num_tris])
        UsdGeom.Mesh(decal_prim).GetFaceVertexCountsAttr().Set(np.array([3] * int(num_tris / 3)))

    return decal_path
