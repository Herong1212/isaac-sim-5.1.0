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
This is the implementation of the OGN node defined in OgnDecal.ogn
"""

# Array or tuple values are accessed as numpy arrays so you probably need this import
import math

import numpy as np
import omni.graph.core as og
import omni.timeline
import omni.warp
import warp as wp
import warp.sim
from pxr import Gf, Sdf, Usd, UsdGeom

# wp.config.mode = "debug"
# wp.config.verify_cuda = True


def read_transform_bundle(bundle):
    timeline = omni.timeline.get_timeline_interface()
    time = timeline.get_current_time() * timeline.get_time_codes_per_seconds()

    stage = omni.usd.get_context().get_stage()
    prim = UsdGeom.Xformable(stage.GetPrimAtPath(bundle.attribute_by_name("sourcePrimPath").value))
    return prim.ComputeLocalToWorldTransform(time)


def read_bounds_bundle(bundle):
    timeline = omni.timeline.get_timeline_interface()
    time = timeline.get_current_time() * timeline.get_time_codes_per_seconds()

    stage = omni.usd.get_context().get_stage()
    prim = UsdGeom.Xformable(stage.GetPrimAtPath(bundle.attribute_by_name("sourcePrimPath").value))

    bounds = prim.ComputeWorldBound(time, purpose1="default")
    return bounds


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


def add_bundle_float_data(bundle, name, data, type):

    attr = bundle.attribute_by_name(name)
    if attr is None:
        attr = bundle.insert((type, name))

    attr.size = len(data)
    attr.cpu_value = data.astype(np.float32)


def add_bundle_int_data(bundle, name, data, type):

    attr = bundle.attribute_by_name(name)
    if attr is None:
        attr = bundle.insert((type, name))

    attr.size = len(data)
    attr.cpu_value = data.astype(np.int32)


def add_bundle_attr(
    bundle: og.BundleContents,
    name: str,
    type: og.Type,
) -> og.RuntimeAttribute:
    attr = bundle.attribute_by_name(name)
    if attr is None:
        attr = bundle.insert((type, name))

    return attr


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


class OgnDecalState:
    def __init__(self):

        self.initialized = False


class OgnDecal:
    @staticmethod
    def internal_state():

        return OgnDecalState()

    """
    """

    @staticmethod
    def compute(db) -> bool:
        """Run simulation"""

        state = db.internal_state
        mesh = db.inputs.mesh

        with wp.ScopedDevice("cuda:0"):
            stage = omni.usd.get_context().get_stage()
            mesh = stage.GetPrimAtPath("/World/Target/case_a05_inst/Case_A05_01/M_Case_A1_Body")
            mesh = stage.GetPrimAtPath("/World/Torus")

            if mesh and (state.initialized == False and db.inputs.execIn):

                with wp.ScopedTimer("Init"):
                    mesh_points = mesh.GetPrim().GetAttribute("points").Get()
                    mesh_indices = mesh.GetPrim().GetAttribute("faceVertexIndices").Get()
                    mesh_counts = mesh.GetPrim().GetAttribute("faceVertexCounts").Get()
                    # mesh_xform = read_transform_bundle(mesh)

                    num_points = len(mesh_points)

                    if num_points:

                        # allow each tri to be cut once
                        expand = 2

                        state.max_points = len(mesh_indices) * expand
                        state.max_tris = len(mesh_indices) * expand

                        state.mesh_points = wp.array(mesh_points, dtype=wp.vec3)
                        state.mesh_tris = wp.array(triangulate(mesh_counts, mesh_indices), dtype=int)

                        state.clip_points0 = wp.zeros(state.max_points, dtype=wp.vec3)
                        state.clip_points1 = wp.zeros(state.max_points, dtype=wp.vec3)

                        state.clip_normals0 = wp.zeros(state.max_points, dtype=wp.vec3)
                        state.clip_normals1 = wp.zeros(state.max_points, dtype=wp.vec3)

                        state.clip_tris0 = wp.zeros(state.max_tris, dtype=int)
                        state.clip_tris1 = wp.zeros(state.max_tris, dtype=int)

                        state.clip_tris_count = wp.array([len(state.mesh_tris)], dtype=int)
                        state.clip_points_count = wp.array([len(state.mesh_points)], dtype=int)

                        state.clip_uvs = wp.zeros(state.max_points * 2, dtype=float)

                        state.initialized = True

            with wp.ScopedTimer("Clipping"):

                # assign initial state to clipping output
                state.clip_points0.assign(state.mesh_points)
                state.clip_tris0.assign(state.mesh_tris)

                # compute normals
                state.clip_normals0.zero_()

                wp.launch(
                    compute_normals,
                    dim=int(len(state.mesh_tris) / 3),
                    inputs=[state.clip_points0, state.clip_normals0, state.clip_tris0],
                )
                wp.launch(normalize_normals, dim=len(state.mesh_points), inputs=[state.clip_normals0])

                state.clip_tris_count.assign([len(state.mesh_tris)])
                state.clip_points_count.assign([len(state.mesh_points)])

                planes = [
                    Gf.Plane(Gf.Vec3d(0.0, 0.0, -1.0), 0.0),
                    Gf.Plane(Gf.Vec3d(0.0, 0.0, 1.0), -db.inputs.clip_depth),
                    Gf.Plane(Gf.Vec3d(1.0, 0.0, 0.0), -db.inputs.clip_width),
                    Gf.Plane(Gf.Vec3d(-1.0, 0.0, 0.0), -db.inputs.clip_width),
                    Gf.Plane(Gf.Vec3d(0.0, 1.0, 0.0), -db.inputs.clip_height),
                    Gf.Plane(Gf.Vec3d(0.0, -1.0, 0.0), -db.inputs.clip_height),
                ]

                # transform planes from xform space to mesh local space
                for i, p in enumerate(planes):
                    plane_world = p.Transform(Gf.Matrix4d(db.inputs.clip_xform.reshape((4, 4))))
                    plane_local = plane_world.Transform(
                        UsdGeom.Xformable(mesh).ComputeLocalToWorldTransform(0.0).GetInverse()
                    )

                    planes[i] = wp.vec4(
                        plane_local.GetNormal()[0],
                        plane_local.GetNormal()[1],
                        plane_local.GetNormal()[2],
                        -plane_local.GetDistanceFromOrigin(),
                    )

                # clip against planes
                for plane in planes:

                    num_points = int(state.clip_points_count.numpy()[0])
                    num_tris = int(state.clip_tris_count.numpy()[0])

                    state.clip_points_count.zero_()
                    state.clip_tris_count.zero_()

                    wp.launch(
                        kernel=clip_mesh,
                        dim=int(num_tris / 3),
                        inputs=[
                            state.clip_points0,
                            state.clip_points1,
                            state.clip_normals0,
                            state.clip_normals1,
                            state.clip_points_count,
                            state.clip_tris0,
                            state.clip_tris1,
                            state.clip_tris_count,
                            plane,
                            state.max_points,
                            state.max_tris,
                        ],
                    )

                    # print(f"{num_points}, {num_tris}")

                    state.clip_points0, state.clip_points1 = state.clip_points1, state.clip_points0
                    state.clip_normals0, state.clip_normals1 = state.clip_normals1, state.clip_normals0
                    state.clip_tris0, state.clip_tris1 = state.clip_tris1, state.clip_tris0

            with wp.ScopedTimer("Compute UVs"):

                # state.clip_points0, state.clip_points1 = state.clip_points1, state.clip_points0
                # state.clip_tris0, state.clip_tris1 = state.clip_tris1, state.clip_tris0

                clip_to_world = Gf.Matrix4d(db.inputs.clip_xform.reshape((4, 4)))
                mesh_to_world = UsdGeom.Xformable(mesh).ComputeLocalToWorldTransform(0.0)

                mesh_to_clip = mesh_to_world * clip_to_world.GetInverse()

                scale_u = clip_to_world.TransformDir(Gf.Vec3d(1.0, 0.0, 0.0)).GetLength()
                scale_v = clip_to_world.TransformDir(Gf.Vec3d(0.0, 1.0, 0.0)).GetLength()

                plane_u = Gf.Plane(Gf.Vec3d(1.0, 0.0, 0.0), db.inputs.clip_width)
                plane_v = Gf.Plane(Gf.Vec3d(0.0, 1.0, 0.0), db.inputs.clip_height)

                plane_u = wp.vec4(
                    plane_u.GetNormal()[0],
                    plane_u.GetNormal()[1],
                    plane_u.GetNormal()[2],
                    plane_u.GetDistanceFromOrigin(),
                )

                plane_v = wp.vec4(
                    plane_v.GetNormal()[0],
                    plane_v.GetNormal()[1],
                    plane_v.GetNormal()[2],
                    plane_v.GetDistanceFromOrigin(),
                )

                num_points = int(state.clip_points_count.numpy()[0])
                num_tris = int(state.clip_tris_count.numpy()[0])

                # print("----")
                # print(f"{num_points}, {num_tris}")

                # tex_coords = wp.zeros(n=(num_points*2), dtype=float)

                wp.launch(
                    compute_uvs,
                    dim=num_points,
                    inputs=[
                        state.clip_points0,
                        state.clip_uvs,
                        plane_u,
                        plane_v,
                        mesh_to_clip,
                        db.inputs.clip_width,
                        db.inputs.clip_height,
                    ],
                )

                vertices_offset = wp.clone(state.clip_points0)
                wp.launch(
                    offset_mesh,
                    dim=num_points,
                    inputs=[state.clip_points0, state.clip_normals0, vertices_offset, db.inputs.offset_normal],
                )

            # output mesh
            with wp.ScopedTimer("Output"):

                add_bundle_float_data(
                    db.outputs.mesh,
                    "points",
                    data=vertices_offset.numpy()[0:num_points],
                    type=og.Type(og.BaseDataType.FLOAT, tuple_count=3, array_depth=1),
                )
                add_bundle_float_data(
                    db.outputs.mesh,
                    "normals",
                    data=state.clip_normals0.numpy()[0:num_points],
                    type=og.Type(og.BaseDataType.FLOAT, tuple_count=3, array_depth=1),
                )
                add_bundle_float_data(
                    db.outputs.mesh,
                    "primvars:st",
                    data=state.clip_uvs.numpy().reshape((-1, 2))[0:num_points],
                    type=og.Type(og.BaseDataType.FLOAT, tuple_count=2, array_depth=1),
                )
                add_bundle_int_data(
                    db.outputs.mesh,
                    "faceVertexIndices",
                    data=state.clip_tris0.numpy()[0:num_tris],
                    type=og.Type(og.BaseDataType.INT, tuple_count=1, array_depth=1),
                )
                add_bundle_int_data(
                    db.outputs.mesh,
                    "faceVertexCounts",
                    data=np.array([3] * int(num_tris / 3)),
                    type=og.Type(og.BaseDataType.INT, tuple_count=1, array_depth=1),
                )

                source_prim_path_attr = add_bundle_attr(
                    db.outputs.mesh,
                    "sourcePrimPath",
                    og.Type(
                        og.BaseDataType.TOKEN,
                        tuple_count=1,
                        array_depth=0,
                        role=og.AttributeRole.NONE,
                    ),
                )
                source_prim_path_attr.cpu_value = "/World/Decal"

                source_prim_type_attr = add_bundle_attr(
                    db.outputs.mesh,
                    "sourcePrimType",
                    og.Type(
                        og.BaseDataType.TOKEN,
                        tuple_count=1,
                        array_depth=0,
                        role=og.AttributeRole.NONE,
                    ),
                )
                source_prim_type_attr.cpu_value = "Mesh"

                db.outputs.execOut = db.inputs.execIn

        return True
