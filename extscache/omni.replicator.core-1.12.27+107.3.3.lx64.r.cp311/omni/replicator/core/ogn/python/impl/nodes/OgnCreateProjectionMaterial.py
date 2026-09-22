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

from ast import literal_eval
from pathlib import Path
from typing import List, Union

import numpy as np
import omni.graph.core as og
import omni.kit.material.library as mat_lib
import omni.timeline
import omni.usd
import Semantics
from omni.replicator.core import functional as F
from omni.replicator.core.ogn.OgnCreateProjectionMaterialDatabase import OgnCreateProjectionMaterialDatabase
from pxr import Gf, Sdf, Tf, Usd, UsdGeom, UsdShade

manager = omni.kit.app.get_app().get_extension_manager()
ext_id = manager.get_enabled_extension_id("omni.replicator.core")
ext_path = manager.get_extension_path(ext_id)
MDL_FOLDER = Path(ext_path).joinpath("mdl").as_posix()


class VertexOffsetError(Exception):
    """Base exception for errors raised by the offsetting verticies"""

    def __init__(self, msg=None):
        if msg is None:
            msg = "An error was encountered offsetting verticies of the target prim."
        super().__init__(msg)


def _create_mesh_shell(target_prim, path):
    """Create a mesh shell from input mesh(es)

    Concatenate points, polygons and normals and create a new mesh at the specified path.
    """
    stage = omni.usd.get_context().get_stage()
    projection_prim = stage.DefinePrim(path, "Mesh")
    vert_combined = []
    face_vert_counts_combined = []
    face_vert_idx_combined = []
    normals_combined = []
    cur_time = 0.0
    target_prim_to_world = UsdGeom.Xformable(target_prim).ComputeLocalToWorldTransform(cur_time)
    vert_idx_offset = 0
    descendants = [target_prim]
    prototype_tfs = {}
    while descendants:
        cur_prim = descendants.pop()
        if cur_prim.HasAttribute("replicatorProjection"):
            continue
        if cur_prim.IsInstanceable():
            prototype_tfs[cur_prim.GetPrototype().GetName()] = UsdGeom.Xformable(cur_prim).ComputeLocalToWorldTransform(
                cur_time
            )
            descendants.append(cur_prim.GetPrototype())
        elif cur_prim.GetTypeName() != "Mesh":
            descendants.extend(cur_prim.GetChildren())
        else:
            mesh_to_world = UsdGeom.Xformable(cur_prim).ComputeLocalToWorldTransform(cur_time)
            root_path = str(cur_prim.GetPrimPath()).split("/", 2)[1]
            if cur_prim.IsInPrototype() and root_path in prototype_tfs:
                mesh_to_world = mesh_to_world * prototype_tfs.get(root_path)
            mesh_to_target = mesh_to_world * target_prim_to_world.GetInverse()
            points_raw = np.array(cur_prim.GetAttribute("points").Get())
            points_transformed = (np.pad(points_raw, ((0, 0), (0, 1)), constant_values=1) @ mesh_to_target)[..., :3]
            vert_combined.append(points_transformed)
            face_vert_counts_combined.extend(cur_prim.GetAttribute("faceVertexCounts").Get())
            face_vert_idx_raw = np.array(cur_prim.GetAttribute("faceVertexIndices").Get())
            face_vert_idx = face_vert_idx_raw + vert_idx_offset
            face_vert_idx_combined.append(face_vert_idx)
            if cur_prim.HasAttribute("primvars:normals"):
                normals_combined.extend(cur_prim.GetAttribute("primvars:normals").Get())
            elif cur_prim.HasAttribute("normals"):
                normals_combined.extend(cur_prim.GetAttribute("normals").Get())
            vert_idx_offset += len(points_transformed)

    projection_prim.GetAttribute("points").Set(np.vstack(vert_combined))
    projection_prim.GetAttribute("faceVertexCounts").Set(np.array(face_vert_counts_combined))
    projection_prim.GetAttribute("faceVertexIndices").Set(np.hstack(face_vert_idx_combined))
    projection_prim.GetAttribute("normals").Set(np.array(normals_combined))
    return projection_prim


def _apply_primvars(target_prim):
    """
    Create quat, position and scale primvars on the shell mesh. These values will be used by the projection
    material in order to move the projection on the surface of the target prim.
    """
    stage = omni.usd.get_context().get_stage()

    if not target_prim.GetAttribute("primvars:projection_quat").IsValid():
        target_prim.CreateAttribute("primvars:projection_quat", Sdf.ValueTypeNames.Float4, custom=True).Set(
            (0, 0, 0, 0)
        )

    if not target_prim.GetAttribute("primvars:projection_position").IsValid():
        target_prim.CreateAttribute("primvars:projection_position", Sdf.ValueTypeNames.Float3, custom=True).Set(
            (0, 0, 0)
        )

    if not target_prim.GetAttribute("primvars:projection_scale").IsValid():
        target_prim.CreateAttribute("primvars:projection_scale", Sdf.ValueTypeNames.Float3, custom=True).Set((0, 0, 0))

    if not target_prim.GetAttribute("primvars:projection_unitscale").IsValid():
        target_prim.CreateAttribute("primvars:projection_unitscale", Sdf.ValueTypeNames.Float, custom=True).Set(
            UsdGeom.GetStageMetersPerUnit(stage)
        )


def _apply_projection_mdl(target_prim, material_prim=None):
    """
    Apply the projection material which reads the quat, position, and scale primvars to move the projection
    on the surface of the target prim.
    """
    stage = omni.usd.get_context().get_stage()
    projection_mdl = str(Path(MDL_FOLDER).joinpath("project_pbr_material.mdl").as_posix())

    if material_prim:
        # Duplicate the target material and apply
        duplicate_mat_path = str(material_prim.GetPath())
        duplicate_mat_path = omni.usd.get_stage_next_free_path(stage, duplicate_mat_path, False)
        omni.usd.duplicate_prim(stage, str(material_prim.GetPath()), duplicate_mat_path)
        UsdShade.MaterialBindingAPI(target_prim).Bind(
            UsdShade.Material(stage.GetPrimAtPath(duplicate_mat_path)), UsdShade.Tokens.weakerThanDescendants
        )
    else:
        on_mat = lambda mat_prim: UsdShade.MaterialBindingAPI(target_prim).Bind(
            UsdShade.Material(mat_prim), UsdShade.Tokens.weakerThanDescendants
        )

        # Check that there isn't already a projection material on the target. Might need a better way to check this.
        if "ProjectPBRMaterial" not in str(
            UsdShade.MaterialBindingAPI(target_prim).GetDirectBinding().GetMaterial().GetPath()
        ):
            mat_lib.create_mdl_material(stage, projection_mdl, "ProjectPBRMaterial", on_mat)
    UsdShade.MaterialBindingAPI.Apply(target_prim)


def _apply_vertex_offsets(projection_prim, scale=None):
    """
    Create a shell around target to apply projection material to.
    This is a workaround for a decal system at the moment.
    """
    count = 0
    if scale:
        scale_value = scale
    else:
        scale_value = 0.01

    face_vertex_indices = []
    face_vertex_counts = []
    vertex_normals = []
    vertex_normals_divcount = []

    # Get attributes
    if projection_prim.GetAttribute("points").IsValid():
        points = projection_prim.GetAttribute("points").Get()
    else:
        raise VertexOffsetError(f'Target prim {projection_prim.GetPath()} doesn\'t have a "points" attribute.')

    if projection_prim.GetAttribute("normals").IsValid():
        normals = projection_prim.GetAttribute("normals").Get()
    else:
        raise VertexOffsetError(f'Target prim v doesn\'t have a "normals" attribute.')

    if projection_prim.GetAttribute("faceVertexCounts").IsValid():
        face_vertex_counts = projection_prim.GetAttribute("faceVertexCounts").Get()
    else:
        raise VertexOffsetError(
            f'Target prim {projection_prim.GetPath()} doesn\'t have a "faceVertexCounts" attribute.'
        )

    if projection_prim.GetAttribute("faceVertexIndices").IsValid():
        face_vertex_indices = projection_prim.GetAttribute("faceVertexIndices").Get()
    else:
        raise VertexOffsetError(
            f'Target prim {projection_prim.GetPath()} doesn\'t have a "faceVertexIndices" attribute.'
        )

    # Init vertex normals
    for i in range(len(points)):
        vertex_normals.append(Gf.Vec3f(0.0, 0.0, 0.0))
        vertex_normals_divcount.append(0.0)

    # Iterate through the faces, getting the vert indicies, and adding the face normals for those verts to a list
    for faceVertCount in face_vertex_counts:
        for x in range(faceVertCount):
            if (x + count) < len(face_vertex_indices):
                vertex_index = face_vertex_indices[x + count]
                if vertex_index < len(vertex_normals) and (x + count) < len(normals):
                    vertex_normals[vertex_index] += normals[x + count]
                    vertex_normals_divcount[vertex_index] += 1
        count += faceVertCount

    # Divide the normals by how many were added
    for i in range(len(vertex_normals)):
        if vertex_normals_divcount[i] > 0:
            vertex_normals[i] = vertex_normals[i] / vertex_normals_divcount[i]
    for i in range(len(points)):
        points[i] = points[i] + vertex_normals[i] * scale_value

    # Get and set the target cube's points
    projection_prim.GetAttribute("points").Set(points)


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


def _duplicate_target(target_prim, dest_path):
    """
    Duplicate the target prim provided it is a mesh or a Replicator Xform with a mesh child.
    """
    stage = omni.usd.get_context().get_stage()
    stage.DefinePrim("/Projection", "Xform")
    dest_path = omni.usd.get_stage_next_free_path(stage, dest_path, False)
    omni.usd.duplicate_prim(stage, target_prim.GetPath(), dest_path)
    projection_prim = stage.GetPrimAtPath(dest_path)

    # Remove children from the duplicate prim
    for child_prim in projection_prim.GetChildren():
        stage.RemovePrim(child_prim.GetPath())

    # Reset projection prim transform, will inherit parent's transform
    projection_prim.GetAttribute("xformOp:translate").Set(Gf.Vec3d(0, 0, 0))
    projection_prim.GetAttribute("xformOp:rotateXYZ").Set(Gf.Vec3d(0, 0, 0))
    projection_prim.GetAttribute("xformOp:scale").Set(Gf.Vec3d(1, 1, 1))

    return projection_prim


class ProjectionMaterialState:
    def __init__(self):
        self._proxy_prim_paths = set()
        self._proxy_prims = []
        self._listener = None

    def setup_listener(self, proxy_prim_paths: List[Union[str, Sdf.Path]]) -> None:
        if not proxy_prim_paths:
            return
        stage_pxr = omni.usd.get_context().get_stage()
        self._proxy_prim_paths = set(proxy_prim_paths)
        self._proxy_prims = [stage_pxr.GetPrimAtPath(str(ppp)) for ppp in proxy_prim_paths]
        self._listener = Tf.Notice.Register(
            Usd.Notice.ObjectsChanged, self._on_usd_changed, omni.usd.get_context().get_stage()
        )

    def __del__(self):
        self.release()

    def release(self):
        if self._listener:
            self._listener.Revoke()

    def has_proxy_moved(self, notice) -> bool:
        changes = set(notice.GetChangedInfoOnlyPaths())
        return bool(changes.union(self._proxy_prim_paths))

    def _on_usd_changed(self, notice, _):
        stage = omni.usd.get_context().get_stage()
        if stage.GetEditTarget().GetLayer() == stage.GetSessionLayer():
            return

        if not self.has_proxy_moved(notice):
            return

        for prim in self._proxy_prims:
            tf = Gf.Transform(UsdGeom.Xformable(prim).ComputeLocalToWorldTransform(Usd.TimeCode.Default()))
            prim_position = tf.GetTranslation()
            prim_orientation = tf.GetRotation().GetQuaternion()
            prim_scale = tf.GetScale()
            target_path_attr = prim.GetAttribute("primvars:projection_prim")
            if not target_path_attr or not stage.GetPrimAtPath(str(target_path_attr.Get())):
                continue
            target_prim = stage.GetPrimAtPath(target_path_attr.Get())
            target_prim.GetAttribute("primvars:projection_position").Set(prim_position)
            target_prim.GetAttribute("primvars:projection_quat").Set(
                (*[prim_orientation.imaginary[i] for i in range(3)], prim_orientation.real)
            )
            target_prim.GetAttribute("primvars:projection_scale").Set(prim_scale)


class OgnCreateProjectionMaterial:
    @staticmethod
    def internal_state():
        return ProjectionMaterialState()

    @staticmethod
    def release(node):
        state = OgnCreateProjectionMaterialDatabase.shared_internal_state(node)
        state.release()

    @staticmethod
    def initialize(_, node):
        state = OgnCreateProjectionMaterialDatabase.shared_internal_state(node)
        proxy_prim_paths = node.get_attribute("inputs:proxyPrim").get()
        state.setup_listener(proxy_prim_paths)

    @staticmethod
    def compute(db) -> bool:
        target_prim_paths = db.inputs.prims
        proxy_prim_paths = db.inputs.proxyPrim
        semantics = db.inputs.semantics
        if semantics:
            semantics = literal_eval(semantics)
        else:
            semantics = {}
        material_prim_paths = db.inputs.materialPrim
        offset_scale = db.inputs.offsetScale
        state = db.shared_state

        # Validate input
        if not target_prim_paths:
            db.outputs.execOut = og.ExecutionAttributeState.DISABLED
            return False

        if not proxy_prim_paths:
            db.outputs.execOut = og.ExecutionAttributeState.DISABLED
            return False

        stage = omni.usd.get_context().get_stage()

        target_prims = [stage.GetPrimAtPath(str(tp)) for tp in target_prim_paths]
        proxy_prims = [stage.GetPrimAtPath(str(pp)) for pp in proxy_prim_paths]
        if material_prim_paths:
            material_prims = [stage.GetPrimAtPath(str(mpp)) for mpp in material_prim_paths]
        else:
            material_prims = [None]

        if len(proxy_prims) < len(target_prims) or len(proxy_prims) % len(target_prims) > 0:
            db.log_error("Obtained invalid number of proxy prims for the number of targets supplied.")
        else:
            multiple = len(proxy_prims) // len(target_prims)
            target_prims = target_prims * multiple

        if len(material_prims) == 1:
            material_prims = material_prims * len(target_prims)

        # Validate prims
        for target_prim in target_prims:
            if not target_prim.IsValid():
                db.log_error(f"Encountered invalid target prim {target_prim.GetPath()}")
                db.outputs.execOut = og.ExecutionAttributeState.DISABLED
                return False

        for proxy_prim in proxy_prims:
            if not proxy_prim.IsValid():
                db.log_error(f"Encountered invalid proxy prim {target_prim.GetPath()}")
                db.outputs.execOut = og.ExecutionAttributeState.DISABLED
                return False

        # HACK Check that the projection doesn't already exist
        projection_prims = []
        for proxy_prim in proxy_prims:
            if proxy_prim.GetAttribute("primvars:projection_prim").IsValid():
                prim_path = proxy_prim.GetAttribute("primvars:projection_prim").Get()
                if not stage.GetPrimAtPath(prim_path):
                    continue
                projection_prims.append(prim_path)

        if projection_prims:
            db.outputs.prims = projection_prims
            db.outputs.execOut = og.ExecutionAttributeState.ENABLED
            return True

        # Extract meshes from target prims
        projection_paths = []
        shell_cache = {}
        for target_prim, material_prim, proxy_prim in zip(target_prims, material_prims, proxy_prims):
            projection_name = proxy_prim.GetName()
            projection_xform = stage.DefinePrim(f"{str(target_prim.GetPath())}/Projection", "Xform")
            projection_xform.CreateAttribute("replicatorProjection", Sdf.ValueTypeNames.Bool).Set(True)
            projection_path = f"{str(projection_xform.GetPath())}/{projection_name}"

            # Duplicate the target prim by concatenating meshes
            if str(target_prim.GetPath()) in shell_cache:
                omni.usd.duplicate_prim(stage, shell_cache[str(target_prim.GetPath())], projection_path)
                projection_prim = stage.GetPrimAtPath(projection_path)
            else:
                projection_prim = _create_mesh_shell(target_prim, projection_path)
                shell_cache[str(target_prim.GetPath())] = projection_path

            # Apply primvars to duplicate
            _apply_primvars(projection_prim)

            # Apply MDL Material to duplicate
            _apply_projection_mdl(projection_prim, material_prim)

            # Apply vertex offsets to duplicate
            _apply_vertex_offsets(projection_prim, offset_scale)

            # Apply semantic label to duplicate
            if semantics:
                F.modify.semantics(projection_prim, semantics)

            # Ensure castShadows is off on duplicate prim
            if not UsdGeom.PrimvarsAPI(projection_prim).GetPrimvar("doNotCastShadows"):
                UsdGeom.PrimvarsAPI(projection_prim).CreatePrimvar("doNotCastShadows", Sdf.ValueTypeNames.Bool)
            UsdGeom.PrimvarsAPI(projection_prim).GetPrimvar("doNotCastShadows").Set(True)

            # Record the corresponding proxy prim to the projection prim to make modification easier
            if not projection_prim.GetAttribute("primvars:proxy_prim").IsValid():
                projection_prim.CreateAttribute("primvars:proxy_prim", Sdf.ValueTypeNames.Token, custom=True).Set(
                    proxy_prim.GetPath().pathString
                )

            # Record the corresponding projection prim to the proxy to link them and not recreate the projection
            if not proxy_prim.GetAttribute("primvars:projection_prim").IsValid():
                proxy_prim.CreateAttribute("primvars:projection_prim", Sdf.ValueTypeNames.Token, custom=True).Set(
                    str(projection_path)
                )
            projection_paths.append(projection_path)

        if proxy_prim_paths != state._proxy_prim_paths:
            state.setup_listener(proxy_prim_paths)

        db.outputs.prims = projection_paths
        db.outputs.execOut = og.ExecutionAttributeState.ENABLED

        return True
