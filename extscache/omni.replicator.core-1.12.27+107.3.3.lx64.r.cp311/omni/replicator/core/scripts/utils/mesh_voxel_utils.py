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

from typing import List, Tuple

import carb
import carb.settings
import numpy as np
import omni.kit.usd
import omni.usd
from pxr import Gf, Sdf, Tf, Usd, UsdGeom, UsdShade

from ...bindings._omni_replicator_core import CollisionUtilities as CollisionUtilitiesCPP
from . import utils

DEFAULT_VOXEL_RESOLUTION = 30


class CollisionCheckSpec:
    def __init__(self, scatter_type):
        self.scatter_type = scatter_type

    def set_2d_spec(self, surface_meshes, offset, extents):
        self.surface_meshes = surface_meshes
        self.offset = offset
        self.extents = extents

    def set_3d_spec(
        self,
        prims_t,
        volume_prims_t,
        no_collision_prims_t,
        volume_excl_prims_t,
        extents,
        prevent_vol_overlap,
        viz_sampled_voxels,
        resolution_scaling,
        input_voxel_size,
    ):

        self.prims, self.prim_paths = prims_t[0], prims_t[1]
        self.volume_prims, self.volume_prim_paths = volume_prims_t[0], volume_prims_t[1]
        self.no_collision_prims, self.no_collision_prim_paths = no_collision_prims_t[0], no_collision_prims_t[1]
        self.volume_excl_prims, self.volume_excl_prim_paths = volume_excl_prims_t[0], volume_excl_prims_t[1]
        self.extents = extents
        self.prevent_vol_overlap = prevent_vol_overlap
        self.viz_sampled_voxels = viz_sampled_voxels
        self.resolution_scaling = resolution_scaling
        self.input_voxel_size = input_voxel_size


class RejectPoints:
    # class with various point sampling rejection functions
    def __init__(self):
        self.pl_above_p = dict()
        self.not_pl_above_p = dict()

    def _set_minmax(self, min_samp, max_samp):
        self.min_samp = min_samp
        self.max_samp = max_samp

    def _delete_outside_minmax(self, sampled_points):
        # make sure the samples aren't outside sampling bounds. reject stuff outside and resample
        sampled_points = np.delete(
            sampled_points,
            np.where(
                (sampled_points[:, 0] < self.min_samp[0])
                | (sampled_points[:, 0] > self.max_samp[0])
                | (sampled_points[:, 1] < self.min_samp[1])
                | (sampled_points[:, 1] > self.max_samp[1])
                | (sampled_points[:, 2] < self.min_samp[2])
                | (sampled_points[:, 2] > self.max_samp[2])
            )[0],
            axis=0,
        )
        return sampled_points


@utils.singleton
class CollisionUtilities:
    # Class wraps CPP class so it is only initialized once
    def __init__(self):
        self._collision_utils = None
        self._stage_event_listener = carb.eventdispatcher.get_eventdispatcher().observe_event(
            event_name=omni.usd.get_context().stage_event_name(omni.usd.StageEventType.CLOSED),
            on_event=self._on_stage_closed,
            observer_name="replicator.utils.mesh_voxel_utils:stage_closed",
        )

    def _on_stage_closed(self, e):
        self.release()

    def __del__(self):
        self._stage_event_listener.reset()

    def _initialize_collision_utils(self):
        if self._collision_utils is None:
            self._collision_utils = CollisionUtilitiesCPP()

    def check_m_collision(self, *args, **kwargs):
        self._initialize_collision_utils()
        return self._collision_utils.check_m_collision(*args, **kwargs)

    def check_m_collision_usd(self, *args, **kwargs):
        self._initialize_collision_utils()
        return self._collision_utils.check_m_collision_usd(*args, **kwargs)

    def check_collision(self, *args, **kwargs):
        self._initialize_collision_utils()
        return self._collision_utils.check_collision(*args, **kwargs)

    def update_collision_cache(self, *args, **kwargs):
        self._initialize_collision_utils()
        return self._collision_utils.update_collision_cache(*args, **kwargs)

    def clear_actors(self) -> None:
        if self._collision_utils is None:
            return
        return self._collision_utils.clear_actors()

    def release(self) -> None:
        if self._collision_utils is None:
            return
        self.clear()
        self._collision_utils = None

    def clear(self) -> None:
        if self._collision_utils is None:
            return
        return self._collision_utils.clear_actors() and self._collision_utils.clear_collision_cache()


@utils.singleton
class MeshUtils:
    _watched_prim_paths = set()
    _cache = {}
    _prim_change_listener = None
    _stage_event_listener = None

    def __del__(self):
        self._stage_event_listener.reset()

    @classmethod
    def _on_stage_closed(cls, e):
        cls._watched_prim_paths.clear()
        cls._cache.clear()
        cls._prim_change_listener = None

    @classmethod
    def _on_prim_change(cls, notice, _):
        changes = set(c.GetPrimPath() for c in notice.GetChangedInfoOnlyPaths())

        intersection = cls._watched_prim_paths.intersection(changes)

        if intersection:
            cls._watched_prim_paths.clear()  # Force prim paths to be re-processed
            cls._cache.clear()

    @staticmethod
    def _convert_poly_to_tri(
        vertices: np.ndarray, faces_indices: np.ndarray, face_vertex_counts: np.ndarray
    ) -> np.ndarray:
        """Converts the input mesh into a triangle mesh.

        Args:
            vertices: A 2D array of shape (V, 3) containing the vertices that define the mesh.
            faces_indices: A 1D array representing the indices of the vertices for the corresponding faces.
            face_vertex_counts: A 1D array containing the number of vertices defined for each face.

        Returns:
            An array containing the faces of the triangle mesh.
        """
        mask = face_vertex_counts > 3
        faces = np.empty(
            (face_vertex_counts.shape[0] + np.sum(face_vertex_counts[np.nonzero(mask)]) - 3 * np.sum(mask), 3),
            dtype=np.int64,
        )
        faces_idx = 0
        poly_faces_idx = 0

        for vertex_count in face_vertex_counts:
            if vertex_count == 3:
                faces[faces_idx, :] = faces_indices[poly_faces_idx : poly_faces_idx + 3]
            else:  # if face is not a triangle, then break it up into multiple triangles
                faces[faces_idx : faces_idx + vertex_count - 2, 0] = faces_indices[poly_faces_idx]
                # sub-divide the polygon into several triangles by creating lines from the first vertex
                for i in range(poly_faces_idx, poly_faces_idx + vertex_count - 2):
                    faces[faces_idx + i - poly_faces_idx, 1:] = faces_indices[i + 1 : i + 3]
            faces_idx += vertex_count - 2
            poly_faces_idx += vertex_count

        return faces

    @staticmethod
    def _subdivide_vertices(vertices: np.ndarray, faces: np.ndarray, resolution: int) -> np.ndarray:
        """Upsamples the mesh by subdividing the triangle mesh's vertices.

        Ensures that every existing edge's length is <= (resolution-1) / resolution^2
        NOTE: This is a NumPy implementation of the function,
        "kaolin.ops.mesh.trianglemesh._unbatched_subdivide_vertices()", in the Kaolin library .
        Original source code here: https://github.com/NVIDIAGameWorks/kaolin

        Args:
            vertices: A 2D array of shape (V, 3) containing the vertices that define the mesh.
            faces: A 2D array of shape (F, 3) containing the indices of the vertices that define each face.
            resolution: An integer > 1 which specifies how much to subdivide the mesh's vertices.

        Returns:
            An array containing the upsampled vertices.
        """
        assert resolution > 1
        min_edge_length = ((resolution - 1) / (resolution**2)) ** 2
        v1 = np.take(vertices, faces[:, 0], axis=0)
        v2 = np.take(vertices, faces[:, 1], axis=0)
        v3 = np.take(vertices, faces[:, 2], axis=0)

        while True:
            edge1_length = np.sum((v1 - v2) ** 2, axis=1)[:, None]
            edge2_length = np.sum((v2 - v3) ** 2, axis=1)[:, None]
            edge3_length = np.sum((v3 - v1) ** 2, axis=1)[:, None]
            total_edges_length = np.concatenate((edge1_length, edge2_length, edge3_length), axis=1)
            max_edges_length = np.max(total_edges_length, axis=1)

            keep = max_edges_length > min_edge_length

            K = np.sum(keep)
            if K == 0:
                break
            V = vertices.shape[0]
            v1 = v1[keep]  # shape of (K, 3), where K is number of edges that has been kept
            v2 = v2[keep]
            v3 = v3[keep]

            v4 = (v1 + v3) / 2
            v5 = (v1 + v2) / 2
            v6 = (v2 + v3) / 2

            vertices = np.concatenate((vertices, v4, v5, v6))
            vertices, _ = np.unique(vertices, return_inverse=True, axis=0)
            v1 = np.concatenate((v1, v2, v4, v3))
            v2 = np.concatenate((v4, v5, v5, v4))
            v3 = np.concatenate((v5, v6, v6, v6))
        return vertices

    @staticmethod
    def _filter_faces(
        face_indices: np.ndarray, face_vertex_counts: np.ndarray, select_indices: list
    ) -> Tuple[np.ndarray]:
        """Computes the faces specified by `select_indices`.

        Args:
            faces_indices: A 1D array representing the indices of the vertices for the corresponding faces.
            face_vertex_counts: A 1D array containing the number of vertices defined for each face.
            select_indices: A 1D array containing

        Returns:
            A Tuple containing the selected faces and the number of vertices per face.
        """

        faces = list()
        new_faces_count = list()
        faces_idx = 0
        for idx, vertex_count in enumerate(face_vertex_counts):
            if idx in select_indices:
                faces.extend(face_indices[faces_idx : faces_idx + vertex_count])
                new_faces_count.append(vertex_count)
            faces_idx += vertex_count

        return np.array(faces), np.array(new_faces_count)

    @staticmethod
    def _prune_samp_bounds(
        vertices: np.ndarray, tris: np.ndarray, min_samp: np.ndarray, max_samp: np.ndarray
    ) -> np.ndarray:
        """Returns a pruned list of vertex indices based on the min/max sampling bounds.
            Makes sure that for all 3 verts in each triangle, the same coordinate (x,y,or z)
            is outside sampling bounds for all 3 verts.
            It's not safe to just check if at least one coordinate is outside for all verts.
            Why? because if its x on one, y on another, and z on the last,
            you may have a case where the middle of the plane created by
            the 3 verts is penetrated by the part of the allowable volume.
            So this pruning is relatively conservative

        Args:
            vertices: A 2D array of shape (V, 3) containing the vertices that define the mesh.
            tris: A 2D array representing the indices (I, 3) of the vertices for the corresponding faces.
            min_samp: A tuple of minimum global sampling bounds
            max_samp: A tuple of maximum global sampling bounds

        Returns:
            An array with pruned vertex indices
        """

        vt = vertices[tris]
        min_b = np.min((np.max(vt, axis=1) - min_samp), axis=1)
        max_b = np.max((np.min(vt, axis=1) - max_samp), axis=1)
        prune = np.logical_and(min_b >= 0, max_b <= 0)
        tris = tris[prune]
        return tris

    @staticmethod
    def _set_newmesh(
        stage,
        xform_path,
        prim,
        prim_type,
        position=(0, 0, 0),
        rotateXYZ=(0, 0, 0),
        scale=(0, 0, 0),
        xform_meshparent=True,
        visibility=True,
    ):
        """Creates new prim if provided prim is None and sets position, rotate, and scale of its parent xform. If the
            prim is not None, it gets parent and sets the position, rotate, and scale of it. Returns the prim
            along with the prim path.

        Args:
            stage: The USD stage
            xform_path: The desired xform prim path on the stage
            prim: The prim, will create a new one if this is None
            prim_type: the mesh type you want to create, e.g. "Cube", "Torus", "Cylinder".
            position: The desired xyz translation of the xform
            rotateXYZ: The desired xyz rotation of the xform
            scale: The desired xyz scale of the xform
            xform_meshparent: apply the position/rotation/scale to the xform parent of the mesh if ``True``, otherwise
                apply the position/rotation/scale to the mesh prim
            visibility: Whether the new mesh is visible on the stage

        Returns:
            The xform prim along with the volume prim path for the mesh inside the xform.

        """
        if prim is None:
            encl_ct = ""
            # if there is a valid mesh prim we should not overwrite it - so instead append numbers on its parent xform
            while stage.GetPrimAtPath(xform_path + str(encl_ct) + "/" + prim_type).IsValid():
                if len(str(encl_ct)) == 0:
                    encl_ct = 0
                encl_ct = int(encl_ct) + 1
                encl_ct = "{:02d}".format(encl_ct)

            if len(str(encl_ct)) != 0:
                xform_path += str(encl_ct)

            mesh_prim_path = xform_path + "/" + prim_type
            if not stage.GetPrimAtPath(mesh_prim_path).IsValid():
                xform_prim = stage.DefinePrim(xform_path, "Xform")
                _, tmp_prim_path = omni.kit.commands.execute(
                    "CreateMeshPrimWithDefaultXformCommand", prim_type=prim_type
                )
                # Move prim
                omni.usd.duplicate_prim(stage, tmp_prim_path, mesh_prim_path)
                stage.RemovePrim(tmp_prim_path)

                prim = stage.GetPrimAtPath(mesh_prim_path)
                if xform_meshparent:
                    prim.GetAttribute("xformOp:translate").Set((0, 0, 0))
                    prim.GetAttribute("xformOp:rotateXYZ").Set((0, 0, 0))
                    prim.GetAttribute("xformOp:scale").Set((1, 1, 1))
                    UsdGeom.Xformable(xform_prim).AddTranslateOp().Set(position)
                    UsdGeom.Xformable(xform_prim).AddRotateXYZOp().Set(rotateXYZ)
                    UsdGeom.Xformable(xform_prim).AddScaleOp().Set(scale)
                else:
                    prim.GetAttribute("xformOp:translate").Set(position)
                    prim.GetAttribute("xformOp:rotateXYZ").Set(rotateXYZ)
                    prim.GetAttribute("xformOp:scale").Set(scale)
                    if not xform_prim.HasAttribute("xformOp:translate"):
                        UsdGeom.Xformable(xform_prim).AddTranslateOp().Set((0, 0, 0))
                    else:
                        xform_prim.GetAttribute("xformOp:translate").Set((0, 0, 0))
                    if not xform_prim.HasAttribute("xformOp:rotateXYZ"):
                        UsdGeom.Xformable(xform_prim).AddRotateXYZOp().Set((0, 0, 0))
                    else:
                        xform_prim.GetAttribute("xformOp:rotateXYZ").Set((0, 0, 0))
                    if not xform_prim.HasAttribute("xformOp:scale"):
                        UsdGeom.Xformable(xform_prim).AddScaleOp().Set((1, 1, 1))
                    else:
                        xform_prim.GetAttribute("xformOp:scale").Set((1, 1, 1))
            else:
                _, tmp_prim_path = omni.kit.commands.execute(
                    "CreateMeshPrimWithDefaultXformCommand", prim_type=prim_type
                )
                # Move prim
                omni.usd.duplicate_prim(stage, tmp_prim_path, mesh_prim_path)
                stage.RemovePrim(tmp_prim_path)

                prim = stage.GetPrimAtPath(mesh_prim_path)
                if xform_meshparent:
                    prim.GetAttribute("xformOp:translate").Set((0, 0, 0))
                    prim.GetAttribute("xformOp:rotateXYZ").Set((0, 0, 0))
                    prim.GetAttribute("xformOp:scale").Set((1, 1, 1))
                    prim.GetParent().GetAttribute("xformOp:translate").Set(position)
                    prim.GetParent().GetAttribute("xformOp:rotateXYZ").Set(rotateXYZ)
                    prim.GetParent().GetAttribute("xformOp:scale").Set(scale)
                else:
                    prim.GetAttribute("xformOp:translate").Set(position)
                    prim.GetAttribute("xformOp:rotateXYZ").Set(rotateXYZ)
                    prim.GetAttribute("xformOp:scale").Set(scale)

        else:
            if xform_meshparent:
                prim.GetParent().GetAttribute("xformOp:translate").Set(position)
                prim.GetParent().GetAttribute("xformOp:rotateXYZ").Set(rotateXYZ)
                prim.GetParent().GetAttribute("xformOp:scale").Set(scale)
            else:
                prim.GetAttribute("xformOp:translate").Set(position)
                prim.GetAttribute("xformOp:rotateXYZ").Set(rotateXYZ)
                prim.GetAttribute("xformOp:scale").Set(scale)

        if prim.HasAttribute("visibility"):
            if visibility:
                prim.GetAttribute("visibility").Set("inherited")
            else:
                prim.GetAttribute("visibility").Set("invisible")

        return prim

    @staticmethod
    def _get_all_meshes(
        stage,
        do_not_add_paths: list,
    ):
        """Takes a stage and traverses it, adding all meshes on the stage, except those specified in do not add list

        Args:
            stage: The USD stage
            do_not_add_paths: A list of prim paths we should not add to the list

        Returns:
            A list of prims of type mesh

        """

        # TODO: convert to usdrt:
        # usdrt_stage = usdrt.Usd.Stage.Attach(omni.usd.get_context().get_stage_id())
        # prims = usdrt_stage.GetPrimsWithTypeName("Mesh")

        prim_paths_m = list()
        for prim in Usd.PrimRange(stage.GetPrimAtPath("/Replicator")):
            if prim.GetTypeName() == "Mesh":
                ok_to_add = True
                for dne_path in do_not_add_paths:
                    dne_path_str = str(dne_path)
                    prim_path_str = str(prim.GetPath())
                    if dne_path_str in prim_path_str or prim_path_str in dne_path_str:
                        ok_to_add = False
                if ok_to_add:
                    prim_paths_m.append(prim.GetPath())
        return prim_paths_m

    @staticmethod
    def _check_get_meshes(stage, prim_paths: list, allowable_types: list = ["Mesh"]):
        """Takes a list of prim paths and checks if they are of type Mesh. If they are not of type mesh, checks
             descendants to see if any are meshes. If so replaces the prim path with all descendent meshes. If prim path
             is not of type Mesh and has no children of type mesh, throws an error.

        Args:
            stage: The USD stage
            prim_paths: The input prim paths
            allowable_types: List of strings specifying the allowable prim types

        Returns:
            A list of prims of type mesh, as well as corresponding list of prim paths of type mesh

        """

        prims_m = list()
        prim_paths_m = list()

        for prim_path in prim_paths:
            prim = stage.GetPrimAtPath(str(prim_path))
            prim_type = prim.GetTypeName()
            if prim_type in allowable_types:
                prims_m.append(prim)
                prim_paths_m.append(str(prim_path))
            else:
                curr_prims_m = []
                for descendant in Usd.PrimRange(prim):
                    if descendant.GetTypeName() in allowable_types:
                        curr_prims_m.append(descendant)
                        prims_m.append(descendant)
                        prim_paths_m.append(str(descendant.GetPath()))
                if len(curr_prims_m) == 0:
                    raise ValueError(
                        f"Expected prim at {prim.GetPath()} to be of type {allowable_types} or have a descendant of type {allowable_types} but got type {prim_type} and contains no meshes"
                    )
        return prims_m, prim_paths_m

    @classmethod
    def _get_weighted_mesh_data(cls, prim, extents, cache: bool = False):
        if cls._prim_change_listener is None or cls._stage_event_listener is None:
            cls._prim_change_listener = Tf.Notice.Register(
                Usd.Notice.ObjectsChanged, cls._on_prim_change, omni.usd.get_context().get_stage()
            )
            cls._stage_event_listener = carb.eventdispatcher.get_eventdispatcher().observe_event(
                event_name=omni.usd.get_context().stage_event_name(omni.usd.StageEventType.CLOSED),
                on_event=cls._on_stage_closed,
                observer_name="replicator.utils.mesh_voxel_utils:stage_closed",
            )

        cached_data = cls._cache.get(str(prim.GetPath()))
        if cached_data is not None:
            return cached_data
        if prim.GetTypeName() == "GeomSubset":
            mesh_prim = prim.GetParent()
            vertices = np.array(mesh_prim.GetAttribute("points").Get())
            faces_indices = np.array(mesh_prim.GetAttribute("faceVertexIndices").Get())
            face_vertex_counts = np.array(mesh_prim.GetAttribute("faceVertexCounts").Get())
            selected_indices = list(prim.GetAttribute("indices").Get())
            faces_indices, face_vertex_counts = cls._filter_faces(faces_indices, face_vertex_counts, selected_indices)
        elif prim.GetTypeName() == "Mesh":
            mesh_prim = prim
            vertices = np.array(prim.GetAttribute("points").Get())
            faces_indices = np.array(prim.GetAttribute("faceVertexIndices").Get())
            face_vertex_counts = np.array(prim.GetAttribute("faceVertexCounts").Get())
        else:
            raise ValueError(f"Invalid mesh at {str(prim.GetPath())}")

        triangles = cls._convert_poly_to_tri(vertices, faces_indices, face_vertex_counts)  # (N, 3)

        # apply global transform
        global_transform = np.array(utils.read_prim_transform(mesh_prim))
        transformed_vertices = (np.hstack((vertices, np.ones((vertices.shape[0], 1)))) @ global_transform)[:, :3]

        # prune the triangles based on sampling bounds
        triangles = cls._prune_samp_bounds(transformed_vertices, triangles, *extents)

        # get normals
        v1 = transformed_vertices[triangles[:, 0]] - transformed_vertices[triangles[:, 1]]
        v2 = transformed_vertices[triangles[:, 0]] - transformed_vertices[triangles[:, 2]]
        surface_normals = np.cross(v1, v2)
        areas = 0.5 * np.linalg.norm(np.cross(v1, v2), axis=-1)
        surface_normals /= 2 * areas[:, None]

        mesh_data = {
            "weights": areas.astype(np.float64),
            "triangles": triangles,
            "transformed_vertices": transformed_vertices,
            "normals": surface_normals,
            "prim_indices": vertices.shape[0],
        }
        cls._cache[str(prim.GetPath())] = mesh_data

        cur_prim_path = prim.GetPath()
        prims_to_watch = set()
        while not cur_prim_path.IsRootPrimPath():
            prims_to_watch.add(cur_prim_path)
            cur_prim_path = cur_prim_path.GetParentPath()
        prims_to_watch.add(cur_prim_path)

        cls._watched_prim_paths.update(prims_to_watch)
        return mesh_data

    @classmethod
    def sample_points_meshsurface(
        cls,
        num_samples: int,
        mesh_prims: List[Usd.Prim],
        extents: Tuple[Tuple[float, float, float], Tuple[float, float, float]],
        rng_generator: np.random.Generator,
        offset: float,
        prune_func_list: list,
    ):
        """Computes array of points sampled on the voxelgrid that are within the provide min and max sampling bounds

        Args:
            num_samples: The number of points you wish to sample
            mesh_prims: The meshes from which to sample from
            rng_generator: random number generator
            offset: The distance from the mesh that you wish to sample the points on
            prune_func_list: A list of pruning functions used for rejection sampling of sampled points

        Returns:
            A (num_samples x 3) array of sampled points

        """

        N_left_to_sample = num_samples
        N_loop = 0
        sampled_points = None

        transformed_vertices, normals, triangles, weights = [], [], [], []
        num_vertices = 0

        combined_data = cls._cache.get(tuple(set(mesh_prims)))
        if combined_data is None:
            for mesh_prim in mesh_prims:
                mesh_data = cls._get_weighted_mesh_data(mesh_prim, extents)

                transformed_vertices.append(mesh_data["transformed_vertices"])
                triangles.append(mesh_data["triangles"] + num_vertices)
                normals.append(mesh_data["normals"])
                weights.append(mesh_data["weights"])
                num_vertices += mesh_data["transformed_vertices"].shape[0]

            # Concatenate arrays
            combined_data = {
                "transformed_vertices": np.concatenate(transformed_vertices),
                "triangles": np.concatenate(triangles),
                "normals": np.concatenate(normals),
                "weights": np.concatenate(weights),
                "normalization_constant": np.sum(np.concatenate(weights)),
            }
            cls._cache[tuple(set(mesh_prims))] = combined_data

        transformed_vertices = combined_data["transformed_vertices"]
        triangles = combined_data["triangles"]
        normals = combined_data["normals"]
        weights = combined_data["weights"]
        normalization_constant = combined_data["normalization_constant"]

        # sample tris
        triangle_indices = np.arange(triangles.shape[0])

        # loop until we have enough sampled coordinates within min_samp and max_samp
        while sampled_points is None or sampled_points.shape[0] < num_samples:
            sampled_tris = rng_generator.multinomial(N_left_to_sample, weights / normalization_constant)
            sampled_indices = np.repeat(triangle_indices, sampled_tris)
            rng_generator.shuffle(sampled_indices)
            r1 = np.sqrt(rng_generator.random((N_left_to_sample, 1)))
            r2 = rng_generator.random((N_left_to_sample, 1))
            sampled_points_new = (
                (1 - r1) * transformed_vertices[triangles[sampled_indices, 0]]
                + (r1 * (1 - r2)) * transformed_vertices[triangles[sampled_indices, 1]]
                + (r1 * r2) * transformed_vertices[triangles[sampled_indices, 2]]
            )
            sampled_points_new += normals[sampled_indices] * offset

            for prune_func in prune_func_list:
                sampled_points_new = prune_func(sampled_points_new)

            if sampled_points is None:
                sampled_points = sampled_points_new
            elif sampled_points is not None and len(sampled_points_new.shape) > 0:
                sampled_points = np.concatenate((sampled_points, sampled_points_new), axis=0)

            if sampled_points is not None:
                N_left_to_sample = num_samples - sampled_points.shape[0]

            N_loop += 1

            if N_loop >= 900:
                raise ValueError(
                    "Randomization timed out, cannot find a set of samples within the global sampling bounds provided."
                )

        return sampled_points

    @staticmethod
    def _add_height(sample_arr: np.ndarray, rng_generator: np.random.Generator, height_range: Tuple[float, float]):
        """Samples height above surface and adds it to the gravity normal direction of the sampled points

        Args:
            sample_arr: An Nx3 array of N sampled points on the surface(s)
            rng_generator: random noise generator
            height_range: A two-tuple with min and max height above the surface mesh

        Returns:
            Sampled array with added random height

        """

        height_added = rng_generator.uniform(low=height_range[0], high=height_range[1], size=sample_arr.shape[0])
        sample_arr[:, 1] += height_added
        return sample_arr


class VoxelGridProperties:
    def __init__(
        self,
        voxels=None,
        voxel_size=None,
        voxel_vol=None,
        voxel_extents=None,
        mesh_scale=None,
        mesh_scale_multiplier=None,
    ):
        self.voxels = voxels
        self.voxel_size = voxel_size
        self.voxel_vol = voxel_vol
        self.voxel_extents = voxel_extents
        self.mesh_scale = mesh_scale
        self.mesh_scale_multiplier = mesh_scale_multiplier
        if voxels is not None:
            self.weights = float(voxels.shape[0])
        else:
            self.weights = None


@utils.singleton
class VoxelUtils:
    _watched_prim_paths = set()
    _voxel_p = {}
    _resolution = None
    _prim_change_listener = None
    _stage_event_listener = None

    def __del__(self):
        self._stage_event_listener.reset()

    @classmethod
    def _on_stage_closed(cls, e):
        cls._watched_prim_paths.clear()
        cls._voxel_p.clear()
        cls._prim_change_listener = None

    @classmethod
    def _on_prim_change(cls, notice, _):
        changes = set(c.GetPrimPath() for c in notice.GetChangedInfoOnlyPaths())

        intersection = cls._watched_prim_paths.intersection(changes)

        if intersection:
            cls._watched_prim_paths.clear()  # Force prim paths to be re-processed
            cls._voxel_p.clear()

    @staticmethod
    def _base_points_to_voxelgrids(points: np.ndarray, vg_size: tuple) -> np.ndarray:
        """Converts points to voxelgrids. Only points within range [0, 1] are used for voxelization.

        .. warning:
            Causes issues when points outside of the range are provided.

        .. note::
            This is a NumPy implementation of the function,
            "kaolin.ops.conversions.pointcloud_base_points_to_voxelgrids()", in the Kaolin library.
            Original source code here: https://github.com/NVIDIAGameWorks/kaolin

        Args:
            points: A 2D array of size (P, 3) containing the scaled points.
            vg_size: A tuple of integers > 1 which specifies how much to subdivide the mesh's vertices.

        Returns:
            An array representing the surface voxelgrid
        """
        # TODO: causes issues when points outside of the range are provided.
        dtype = points.dtype
        resolution = max(vg_size)
        pc_index = (points) * (resolution - 1)
        pc_index = np.round(pc_index)
        pc_index = np.unique(pc_index.astype(np.int_), axis=0)

        # needed in the event points are a bit outside the extents (e.g. input points < 0 or > 1)
        pc_index = np.delete(pc_index, np.where((pc_index < 0) | ((pc_index - vg_size) >= 0))[0], axis=0)
        vg = np.zeros(shape=vg_size, dtype=dtype)
        vg[tuple(pc_index.transpose())] = 1
        return vg

    @staticmethod
    def _trianglemesh_to_voxelgrid(vertices: np.ndarray, faces: np.ndarray, voxel_size: float) -> np.ndarray:
        """Converts a triangle mesh into a voxelgrid of size (resolution, resolution, resolution)

        .. note::
            This is a NumPy implementation of the function,
            "kaolin.ops.conversions.trianglemesh.trianglemeshes_to_voxelgrids()", in the Kaolin library.
            Original source code here: https://github.com/NVIDIAGameWorks/kaolin

        Args:
            vertices: A 2D array of shape (V, 3) containing the vertices that define the mesh.
            faces: A 2D array of shape (F, 3) containing the indices of the vertices that define each face.
            resolution: An integer > 1 which specifies how much to subdivide the mesh's vertices.
            mesh_voxel_map: A dictionary where voxel parameters will be saved.

        Returns:
            An array representing the surface voxelgrid.

        Raises:
            ValueError: If voxel_size is not valid.
        """
        extents_xyz = None
        extents_xyz = np.array([np.min(vertices, axis=0), np.max(vertices, axis=0)])

        # get the divisible voxels just below and above the min and max extents, respectively
        extents_sign = np.sign(extents_xyz)
        extents_mask_neg = np.array(extents_sign)
        extents_mask_neg[extents_mask_neg == -1] = 0
        extents_mask_pos = -np.array(extents_sign)
        extents_mask_pos[extents_mask_pos == -1] = 0
        extents_voxel_xyz = (
            np.stack(
                [
                    (np.abs(extents_xyz[0]) / voxel_size + 0.0).astype(int) * extents_sign[0] * voxel_size,
                    (np.abs(extents_xyz[1]) / voxel_size + 1.0).astype(int) * extents_sign[1] * voxel_size,
                ]
            )
            * extents_mask_neg
            + np.stack(
                [
                    (np.abs(extents_xyz[0]) / voxel_size + 1.0).astype(int) * extents_sign[0] * voxel_size,
                    (np.abs(extents_xyz[1]) / voxel_size + 0.0).astype(int) * extents_sign[1] * voxel_size,
                ]
            )
            * extents_mask_pos
        )
        # make sure that the extents are separated by a non-zero amount. If they are not (which
        # can happen when all the vertices lie in a plane orthogonal to x, y, or z), then we
        # should add the voxel_size to the upper bound.
        for i in range(3):
            if extents_voxel_xyz[1, i] - extents_voxel_xyz[0, i] == 0:
                extents_voxel_xyz[1, i] += voxel_size

        # compute the scale from the voxel extents
        scale = np.abs(extents_voxel_xyz[1, :] - extents_voxel_xyz[0, :])
        resolution_3D = scale / voxel_size

        if np.sum(resolution_3D - (resolution_3D + 0.0000001).astype(int)) > 0.0001:
            raise ValueError(
                "Global scale should be an int or very close to is since this is the number of voxels the grid will have"
            )
        else:
            resolution_3D = (resolution_3D + 0.0000001).astype(int)

        resolution = np.max(resolution_3D)

        scaled_points = ((vertices[:, :3] - extents_voxel_xyz[0, :]) / np.max(scale).reshape(-1, 1, 1)).astype(
            np.float32
        )

        # make smaller by half a voxel so it doesn't go outside the bounds
        scaled_points[0] = scaled_points[0] * (scale - voxel_size / 2) / scale

        if resolution > 1:
            points = MeshUtils._subdivide_vertices(scaled_points[0], faces, resolution)

        voxelgrid = VoxelUtils._base_points_to_voxelgrids(points, resolution_3D)

        return voxelgrid, extents_voxel_xyz

    @staticmethod
    def _fill(voxelgrid: np.ndarray) -> np.ndarray:
        """Fills in the volume of a voxel grid.

        Args:
            voxelgrid: The voxelgrid that defines the surface of the mesh.

        Returns:
            An array containing the voxelgrid with its volume filled in.
        """
        # Import only when required to decrease startup time (ndimage adds ~100 ms)
        from scipy.ndimage import binary_fill_holes

        dtype = voxelgrid.dtype
        return np.array(binary_fill_holes(voxelgrid), dtype=dtype)

    @staticmethod
    def _rm_overlap_direct(
        voxel_vol: np.ndarray, extents_voxel_xyz: np.ndarray, voxel_size: float, rm_overlap_voxel_p: dict
    ) -> np.ndarray:
        """Returns a voxel grid where voxels in the global space that are overlapping those in the provided
            rm_overlap_voxel_p dict are zeroed out

        Args:
            voxel_vol: A 3D voxel grid containing the a binary mask over enclosed spaces.
            extents_voxel_xyz: A 2D array representing the indices (I, 3) of the vertices for the corresponding faces.
            voxel_size: The size of each voxel (applies to x,y,z) in cm
            rm_overlap_voxel_p: dict containing keys referencing voxelized volumetric prims that point to
                values containing a sub dict of voxel properties

        Returns:
            An voxel grid array with zeroed out voxels based on previously accounted for space
        """

        # make sure that the extents provided are [[minx,miny,minz], [maxx,maxy,maxz]]
        if np.min(extents_voxel_xyz[1] - extents_voxel_xyz[0]) <= 0:
            raise ValueError("Extents do not represent a min and max in the global coordinate frame")

        for prim_key in rm_overlap_voxel_p:

            # make sure that the extents provided are [[minx,miny,minz], [maxx,maxy,maxz]]
            if (
                np.min(rm_overlap_voxel_p[prim_key].voxel_extents[1] - rm_overlap_voxel_p[prim_key].voxel_extents[0])
                <= 0
            ):
                raise ValueError("Extents do not represent a min and max in the global coordinate frame")

            # if any of the low extents are higher than their corresponding previous high extent
            # OR any of the high extents are lower than their corresponding previous low extent
            # then skip
            if np.max(extents_voxel_xyz[0] - rm_overlap_voxel_p[prim_key].voxel_extents[1]) > 0 or np.min(
                extents_voxel_xyz[1] - rm_overlap_voxel_p[prim_key].voxel_extents[0] < 0
            ):
                continue

            extents_voxel_coords_p0 = ((extents_voxel_xyz - extents_voxel_xyz[0]) / voxel_size + 0.0001).astype(int)
            extents_voxel_coords_state_p0 = (
                (rm_overlap_voxel_p[prim_key].voxel_extents - extents_voxel_xyz[0]) / voxel_size + 0.0001
            ).astype(int)
            extents_rm_p0 = np.stack(
                [
                    np.max(np.stack([extents_voxel_coords_p0[0], extents_voxel_coords_state_p0[0]]), axis=0),
                    np.min(np.stack([extents_voxel_coords_p0[1], extents_voxel_coords_state_p0[1]]), axis=0),
                ]
            )
            if np.min(extents_rm_p0) < 0:
                raise ValueError("Extents are out of range -- below min of voxel grid")
            elif np.max(extents_rm_p0 - extents_voxel_coords_p0[1]) > 0:
                continue
                # raise ValueError("Extents are out of range -- above max of voxel grid")

            extents_voxel_coords_p1 = (
                (extents_voxel_xyz - rm_overlap_voxel_p[prim_key].voxel_extents[0]) / voxel_size + 0.0001
            ).astype(int)
            extents_voxel_coords_state_p1 = (
                (rm_overlap_voxel_p[prim_key].voxel_extents - rm_overlap_voxel_p[prim_key].voxel_extents[0])
                / voxel_size
                + 0.0001
            ).astype(int)
            extents_rm_p1 = np.stack(
                [
                    np.max(np.stack([extents_voxel_coords_p1[0], extents_voxel_coords_state_p1[0]]), axis=0),
                    np.min(np.stack([extents_voxel_coords_p1[1], extents_voxel_coords_state_p1[1]]), axis=0),
                ]
            )
            if np.min(extents_rm_p1) < 0:
                raise ValueError("Extents are out of range -- below min of voxel grid")
            elif np.max(extents_rm_p1 - extents_voxel_coords_p1[1]) > 0:
                raise ValueError("Extents are out of range -- above max of voxel grid")

            # Subtract overlapping voxels from existing volume. Guard against
            # degenerate (zero-sized) intersections that would raise broadcasting
            # errors by skipping the subtraction in that case.

            # Determine the size of the intersection region for both volumes.
            region_shape_new = extents_rm_p0[1] - extents_rm_p0[0]  # shape (3,)
            region_shape_old = extents_rm_p1[1] - extents_rm_p1[0]

            # If any dimension is zero, there is nothing to subtract.
            if np.any(region_shape_new <= 0) or np.any(region_shape_old <= 0):
                continue

            try:
                voxel_vol[
                    extents_rm_p0[0][0] : extents_rm_p0[1][0],
                    extents_rm_p0[0][1] : extents_rm_p0[1][1],
                    extents_rm_p0[0][2] : extents_rm_p0[1][2],
                ] -= rm_overlap_voxel_p[prim_key].voxel_vol[
                    extents_rm_p1[0][0] : extents_rm_p1[1][0],
                    extents_rm_p1[0][1] : extents_rm_p1[1][1],
                    extents_rm_p1[0][2] : extents_rm_p1[1][2],
                ]
            except ValueError:
                # Shapes did not match due to unexpected edge cases – skip this prim.
                continue

            voxel_vol[voxel_vol < 0] = 0

        return voxel_vol

    @staticmethod
    def _get_voxel_pl_above(
        voxel_vol: np.ndarray,
        voxel_vol_pl_above: np.ndarray,
        extents_voxel_xyz: np.ndarray,
        voxel_size: float,
        above_surf_voxel_p: dict,
    ) -> np.ndarray:
        """Returns a voxel grid where voxels in the global space that are overlapping those in the provided
            ``rm_overlap_voxel_p`` dict are zeroed out

        Args:
            voxel_vol: A 3D voxel grid containing the a binary mask over enclosed spaces.
            voxel_vol_pl_above: A 3D voxel grid in the same global location as ``voxel_vol`` that is modified in place to
                fill in areas above the pl_above object surfaces.
            extents_voxel_xyz: A 2D array representing the indices (I, 3) of the vertices for the corresponding faces.
            voxel_size: The size of each voxel (applies to x,y,z) in cm
            above_surf_voxel_p: dict containing keys referencing voxelized volumetric prims that point to
                values containing a sub dict of voxel properties

        Returns:
            An voxel grid array with 1s only above the top surface of the place above voxel grid surface, otherwise 0
        """

        # make sure that the extents provided are [[minx,miny,minz], [maxx,maxy,maxz]]
        if np.min(extents_voxel_xyz[1] - extents_voxel_xyz[0]) <= 0:
            raise ValueError("Extents do not represent a min and max in the global coordinate frame")

        for prim_key in above_surf_voxel_p:

            # make sure that the extents provided are [[minx,miny,minz], [maxx,maxy,maxz]]
            if (
                np.min(above_surf_voxel_p[prim_key].voxel_extents[1] - above_surf_voxel_p[prim_key].voxel_extents[0])
                <= 0
            ):
                raise ValueError("Extents do not represent a min and max in the global coordinate frame")

            # if any of the low extents are higher than their corresponding previous high extent
            # OR any of the high extents are lower than their corresponding previous low extent
            # then skip UNLESS the object is underneath normal to gravity, which we still want to consider
            # and "place above"
            if np.max(extents_voxel_xyz[0] - above_surf_voxel_p[prim_key].voxel_extents[1]) > 0 or np.min(
                extents_voxel_xyz[1] - above_surf_voxel_p[prim_key].voxel_extents[0] < 0
            ):

                # if the y is underneath the enclosure, still consider it for placing above
                if above_surf_voxel_p[prim_key].voxel_extents[1][1] <= extents_voxel_xyz[0][1]:

                    # if the x and z are out of range, skip
                    if (
                        above_surf_voxel_p[prim_key].voxel_extents[0][0] > extents_voxel_xyz[1][0]
                        or above_surf_voxel_p[prim_key].voxel_extents[1][0] < extents_voxel_xyz[0][0]
                        or above_surf_voxel_p[prim_key].voxel_extents[0][2] > extents_voxel_xyz[1][2]
                        or above_surf_voxel_p[prim_key].voxel_extents[1][2] < extents_voxel_xyz[0][2]
                    ):
                        continue
                else:
                    # if the y is above the enclosure, skip
                    continue

            extents_voxel_coords_p0 = ((extents_voxel_xyz - extents_voxel_xyz[0]) / voxel_size + 0.0001).astype(int)
            extents_voxel_coords_state_p0 = (
                (above_surf_voxel_p[prim_key].voxel_extents - extents_voxel_xyz[0]) / voxel_size + 0.0001
            ).astype(int)
            extents_rm_p0 = np.stack(
                [
                    np.max(np.stack([extents_voxel_coords_p0[0], extents_voxel_coords_state_p0[0]]), axis=0),
                    np.min(np.stack([extents_voxel_coords_p0[1], extents_voxel_coords_state_p0[1]]), axis=0),
                ]
            )
            underneath = False
            if (
                np.any(
                    [
                        extents_rm_p0[0][0],
                        extents_rm_p0[0][1],
                        extents_rm_p0[0][2],
                        extents_rm_p0[1][0],
                        extents_rm_p0[1][2],
                    ]
                )
                < 0
            ):
                raise ValueError("Extents are out of range -- below min of voxel grid")
            elif extents_rm_p0[1][1] < 0:
                underneath = True
            elif np.max(extents_rm_p0 - extents_voxel_coords_p0[1]) > 0:
                continue
                # raise ValueError("Extents are out of range -- above max of voxel grid")

            extents_voxel_coords_p1 = (
                (extents_voxel_xyz - above_surf_voxel_p[prim_key].voxel_extents[0]) / voxel_size + 0.0001
            ).astype(int)
            extents_voxel_coords_state_p1 = (
                (above_surf_voxel_p[prim_key].voxel_extents - above_surf_voxel_p[prim_key].voxel_extents[0])
                / voxel_size
                + 0.0001
            ).astype(int)
            extents_rm_p1 = np.stack(
                [
                    np.max(np.stack([extents_voxel_coords_p1[0], extents_voxel_coords_state_p1[0]]), axis=0),
                    np.min(np.stack([extents_voxel_coords_p1[1], extents_voxel_coords_state_p1[1]]), axis=0),
                ]
            )
            if np.min(extents_rm_p1) < 0:
                raise ValueError("Extents are out of range -- below min of voxel grid")
            elif np.max(extents_rm_p1 - extents_voxel_coords_p1[1]) > 0:
                raise ValueError("Extents are out of range -- above max of voxel grid")

            if not underneath:
                # here we need to add in the voxels for the top surface
                voxel_vol_pl_above[
                    extents_rm_p0[0][0] : extents_rm_p0[1][0],
                    extents_rm_p0[0][1] : extents_rm_p0[1][1],
                    extents_rm_p0[0][2] : extents_rm_p0[1][2],
                ] += above_surf_voxel_p[prim_key].voxel_vol[
                    extents_rm_p1[0][0] : extents_rm_p1[1][0],
                    extents_rm_p1[0][1] : extents_rm_p1[1][1],
                    extents_rm_p1[0][2] : extents_rm_p1[1][2],
                ]

            # if anything in the y direction of the above surf voxel grid is below but 1, make sure the bottom layer
            # of voxels in voxel_vol_pl_above is set to 1
            if extents_rm_p1[0][1] > 0:
                voxel_vol_pl_above[
                    extents_rm_p0[0][0] : extents_rm_p0[1][0], 0, extents_rm_p0[0][2] : extents_rm_p0[1][2]
                ] += np.max(
                    above_surf_voxel_p[prim_key].voxel_vol[
                        extents_rm_p1[0][0] : extents_rm_p1[1][0],
                        0 : extents_rm_p1[0][1],
                        extents_rm_p1[0][2] : extents_rm_p1[1][2],
                    ],
                    axis=1,
                )

        voxel_vol_pl_above[voxel_vol_pl_above > 0] = 1

        # cut out anything that's not a 1 in the main volume
        voxel_vol_pl_above = voxel_vol * voxel_vol_pl_above

        return voxel_vol_pl_above

    @staticmethod
    def _rm_excl_objs(
        voxel_vol: np.ndarray,
        extents_voxel_xyz: np.ndarray,
        voxel_size: float,
        vol_excl_prims: list,
        vol_excl_prim_paths: List[str],
    ) -> np.ndarray:
        """Returns a voxel grid where voxels overlapping with the exclusion prim voxel space are zeroed out

        Args:
            voxel_vol: A 3D voxel grid containing the a binary mask over enclosed spaces.
            extents_voxel_xyz: A 2D array representing the indices (I, 3) of the vertices for the corresponding faces.
            voxel_size: The size of each voxel (applies to x,y,z) in cm
            vol_excl_prims: A list of prim(s) from which to exclude from sampling. similar effect to no_coll_prims, but
                more efficient and less accurate
            vol_excl_prim_paths: A list of paths corresponding to vol_excl_prims

        Returns:
            An voxel grid array with zeroed out voxels based on previously accounted for space
        """

        for _, (prim, prim_path) in enumerate(zip(vol_excl_prims, vol_excl_prim_paths)):

            vertices = np.array(prim.GetAttribute("points").Get())  # translation in cm
            faces_indices = np.array(prim.GetAttribute("faceVertexIndices").Get())
            face_vertex_counts = np.array(prim.GetAttribute("faceVertexCounts").Get())

            # convert prim mesh to a triangle mesh
            faces = MeshUtils._convert_poly_to_tri(vertices, faces_indices, face_vertex_counts)

            # generate voxel grid
            global_transform = np.array(
                utils.read_prim_transform(prim)
            )  # translation in cm. this includes the scaling.
            verts_global = (np.hstack((vertices, np.ones((vertices.shape[0], 1)))) @ global_transform)[:, :3]
            voxel_surface_excl, extents_voxel_xyz_excl = VoxelUtils._trianglemesh_to_voxelgrid(
                verts_global, faces, voxel_size
            )

            # fill voxel volume
            voxel_vol_excl = VoxelUtils._fill(voxel_surface_excl)

            # here remove it from the provided shape
            properties = {
                prim_path: VoxelGridProperties(voxel_vol=voxel_vol_excl, voxel_extents=extents_voxel_xyz_excl)
            }
            voxel_vol = VoxelUtils._rm_overlap_direct(voxel_vol, extents_voxel_xyz, voxel_size, properties)

        return voxel_vol

    @staticmethod
    def _prune_place_above(
        voxel_vol: np.ndarray,
        extents_voxel_xyz: np.ndarray,
        voxel_size: float,
        pl_above_prims: list,
        pl_above_prim_paths: List[str],
    ) -> np.ndarray:
        """Returns a voxel grid where voxels everything not over the top of pl_above_prims is zeroed out

        Args:
            voxel_vol: A 3D voxel grid containing the a binary mask over enclosed spaces.
            extents_voxel_xyz: A 2D array representing the indices (I, 3) of the vertices for the corresponding faces.
            voxel_size: The size of each voxel (applies to x,y,z) in cm
            pl_above_prims: A list of prim(s) representing the objects we want to only place things above
            pl_above_prim_paths: A list of paths corresponding to pl_above_prims

        Returns:
            A pruned voxel grid where 1's are set to 0 unless they are over the place above objects
        """
        voxel_vol_pl_above = np.zeros_like(voxel_vol)

        for _, (prim, prim_path) in enumerate(zip(pl_above_prims, pl_above_prim_paths)):

            vertices = np.array(prim.GetAttribute("points").Get())  # translation in cm
            faces_indices = np.array(prim.GetAttribute("faceVertexIndices").Get())
            face_vertex_counts = np.array(prim.GetAttribute("faceVertexCounts").Get())

            # convert prim mesh to a triangle mesh
            faces = MeshUtils._convert_poly_to_tri(vertices, faces_indices, face_vertex_counts)

            # generate voxel grid
            global_transform = np.array(
                utils.read_prim_transform(prim)
            )  # translation in cm. this includes the scaling.
            verts_global = (np.hstack((vertices, np.ones((vertices.shape[0], 1)))) @ global_transform)[:, :3]
            voxel_surface_pl_above, extents_voxel_xyz_pl_above = VoxelUtils._trianglemesh_to_voxelgrid(
                verts_global, faces, voxel_size
            )

            # here add on the voxels above the prim
            properties = {
                prim_path: VoxelGridProperties(
                    voxel_vol=voxel_surface_pl_above, voxel_extents=extents_voxel_xyz_pl_above
                )
            }
            voxel_vol_pl_above = VoxelUtils._get_voxel_pl_above(
                voxel_vol, voxel_vol_pl_above, extents_voxel_xyz, voxel_size, properties
            )

        encl_ct = np.zeros((voxel_vol.shape[0], voxel_vol.shape[2]))

        # go through voxel_vol and voxel_vol_pl_above and modify voxel_vol_pl_above in place
        for j in range(voxel_vol.shape[1]):

            # if the first level of voxel_vol is 1 then toggle first enclosure
            if j == 0:
                encl_ct += voxel_vol[:, 0, :]

            else:
                # if we switch from a open space to closed space we trigger first enclosure
                # if voxel_vol[j]==1 and voxel_vol[j-1]==0, toggleunder+=1
                encl_ct += voxel_vol[:, j, :] * (1 - voxel_vol[:, j - 1, :])

                # if we switch from a closed encl to an open space we trigger second enclosure
                # if voxel_vol[j]==0 and voxel_vol[j-1]==1, toggleunder+=1
                encl_ct += (1 - voxel_vol[:, j, :]) * voxel_vol[:, j - 1, :]

                toggle_encl = 2 - encl_ct
                toggle_encl[toggle_encl > 1] = 1
                toggle_encl[toggle_encl < 0] = 0

                # which enclosure we are in does not matter if voxel_vol and its previous are 1 ... carry up if the last one was 1
                # if j and voxel_vol_pl_above[j]==0 and voxel_vol_pl_above[j-1]==1 and voxel_vol[j]==1 and voxel_vol[j-1]==1, voxel_vol_pl_above[j]=1
                voxel_vol_pl_above[:, j, :] += (
                    voxel_vol_pl_above[:, j - 1, :] * voxel_vol[:, j, :] * voxel_vol[:, j - 1, :]
                )

                # if j and voxel_vol_pl_above[j]==0 and voxel_vol_pl_above[j-1]==1 and voxel_vol[j]==1 and voxel_vol[j-1]==0 and toggleunder < 2, voxel_vol_pl_above[j]=1
                voxel_vol_pl_above[:, j, :] += (
                    voxel_vol_pl_above[:, j - 1, :] * voxel_vol[:, j, :] * (1 - voxel_vol[:, j - 1, :]) * toggle_encl
                )

                # on or below the first enclosure and voxel_vol is 0, still carry up if the last one was 1
                # if j and voxel_vol_pl_above[j]==0 and voxel_vol_pl_above[j-1]==1 and voxel_vol[j]==0 and toggleunder < 2, voxel_vol_pl_above[j]=1
                voxel_vol_pl_above[:, j, :] += voxel_vol_pl_above[:, j - 1, :] * (1 - voxel_vol[:, j, :]) * toggle_encl

        voxel_vol_pl_above[voxel_vol_pl_above > 1] = 1

        return voxel_vol_pl_above

    @staticmethod
    def _prune_height_range(
        voxel_vol: np.ndarray,
        voxel_size: float,
        height_range: tuple,
    ) -> np.ndarray:
        """Computes a pruned voxel grid based on the height range specified. drop a trace down each voxel direction
            normal to gravity and set the "floor" that height is measured based on when a voxel changes from "1" to
            "0" or "1" to "out of bounds". I.e. from above, the location that is occluded after a series of open
            sampling space.
                *Measure continuously from the midpoint of every voxel based gravity normal vector. If the mid point of
                a given voxel is less than the low height range, zero it. If the mid point of a given voxel is higher
                than the high height range, zero it.

        Args:
            voxel_vol: A 3D voxel grid containing the a binary mask over enclosed spaces.
            voxel_size: The size of each voxel (applies to x,y,z) in cm
            height_range: A tuple specifying the min and max height above the surface to sample on

        Returns:
            A pruned voxel grid array with zeroed out voxels outside of the height range
        """
        # create a voxel grid with 1's where the floor is
        floor_vol = np.array(voxel_vol)
        floor_vol[:, 1:, :] = voxel_vol[:, 1:, :] - voxel_vol[:, :-1, :]
        floor_vol[floor_vol < 0] = 0

        # make another voxel grid with 1's at a range above the floor
        height_range_vol = np.zeros_like(floor_vol)
        for height_step in range(
            max(0, int(height_range[0] / float(voxel_size) + 0.5)),
            min(voxel_vol.shape[1], int(height_range[1] / float(voxel_size) + 0.5)),
        ):
            if height_step == 0:
                height_range_vol += floor_vol
            else:
                height_range_vol[:, height_step:, :] += floor_vol[:, :-height_step, :]
        height_range_vol[height_range_vol > 1] = 1

        # knock out everything that was not in the original voxel volume
        height_range_vol = height_range_vol * voxel_vol

        # if the height range was out of bounds of the voxel space, just return the original voxel vol so
        # we don't run into errors later.
        if np.sum(height_range_vol) == 0:
            return voxel_vol

        return height_range_vol

    @staticmethod
    def _create_from_height_upperbound(voxel_vol, extents_voxel_xyz, voxel_size, height_range_max):
        """Computes a new voxel grid that is larger in the y direction that the original one, to reflect voxel
            sampling space above the surface, where the new voxel is created based on the height range max. Input voxels
            only represent where the surface cuts through the voxel space, so they are initially set to zero unless
            the minimum height range is very small.

        Args:
            voxel_vol: A 3D voxel grid containing the a binary mask over enclosed spaces.
            extents_voxel_xyz: A 2D array representing the indices (I, 3) of the vertices for the corresponding faces.
            voxel_size: The size of each voxel (applies to x,y,z) in cm
            height_range: A tuple specifying the min and max height above the surface to sample on

        Returns:
            A new (and likely enlarged) voxel volume reflecting the height max where sampling is desired, as well as
            the modified voxel extents.
        """

        height_range_max_voxel = int(height_range_max / voxel_size + 0.5)
        voxel_vol_addon = np.zeros((voxel_vol.shape[0], height_range_max_voxel, voxel_vol.shape[2]))
        extents_voxel_xyz[1, 1] += height_range_max_voxel * voxel_size
        voxel_vol = np.concatenate((voxel_vol, voxel_vol_addon), axis=1)

        voxel_vol_new = np.zeros_like(voxel_vol)
        for i in range(0, voxel_vol.shape[0]):
            for height_step in range(i, i + height_range_max_voxel):
                if height_step > voxel_vol.shape[1] - 1:
                    continue
                voxel_vol_new[:, height_step, :] += voxel_vol[:, i, :]

        voxel_vol_new[voxel_vol_new > 1] = 1

        return voxel_vol_new, extents_voxel_xyz

    @staticmethod
    def _compute_voxel_size(
        default_voxel_size: float,
        resolution: float,
        volume_prims: list,
        volume_prim_paths: list,
        voxel_p: dict,
    ) -> float:
        """Computes a voxel size based on the default voxel size and resolution specified. Also returns a dict with
            current voxel properties so we don't have to read USD prims a second time.

        Args:
            default_voxel_size: The size of each voxel (applies to x,y,z) in cm
            resolution: user defined length of the longest side
            volume_prims: list of enclosing volume prims
            volume_prim_paths: list of enclosing volume prim paths
            voxel_p: voxel properties dict containing at least the mesh scale for each enclosing volume prim

        Returns:
            The voxel size
        """

        if not isinstance(default_voxel_size, float) or default_voxel_size <= 0.0:
            # here we need to set the voxel size based on the average size of each of the vol prims.
            # Compute the longest side length of each vol_prim and then
            voxel_size_all = []
            for idx, (prim, prim_path) in enumerate(zip(volume_prims, volume_prim_paths)):
                vertices = np.array(prim.GetAttribute("points").Get())  # translation in cm
                extents_xyz = (np.max(vertices, axis=0) - np.min(vertices, axis=0)) * voxel_p[prim_path].mesh_scale
                curr_voxel_size = np.max(extents_xyz) / resolution
                voxel_size_all.append(curr_voxel_size)
            voxel_size = np.mean(voxel_size_all)  # (cm / voxel)

        else:
            voxel_size = default_voxel_size  # (cm / voxel)

        return voxel_size

    @staticmethod
    def _prune_samp_bounds(
        voxel_vol: np.ndarray,
        extents_voxel_xyz: np.ndarray,
        voxel_size: float,
        min_samp: np.ndarray,
        max_samp: np.ndarray,
    ) -> np.ndarray:
        """Computes a pruned voxel grid where locations beyond the min/max sampling bounds are zeroed out.

        Args:
            voxel_vol: A 3D voxel grid containing the a binary mask over enclosed spaces.
            extents_voxel_xyz: A 2D array representing the indices (I, 3) of the vertices for the corresponding faces.
            voxel_size: The size of each voxel (applies to x,y,z) in cm
            min_samp: A tuple of minimum global sampling bounds
            max_samp: A tuple of maximum global sampling bounds

        Returns:
            A pruned voxel grid array with zeroed out voxels beyond bounds
        """

        min_act = np.max((extents_voxel_xyz[0], min_samp), axis=0)
        max_act = np.min((extents_voxel_xyz[1], max_samp), axis=0)

        prune_min = np.floor((min_act - extents_voxel_xyz[0]) / voxel_size).astype(int)
        prune_max = np.ceil(voxel_vol.shape - (extents_voxel_xyz[1] - max_act) / voxel_size).astype(int)

        voxel_vol[: prune_min[0], :, :] = 0
        voxel_vol[:, : prune_min[1], :] = 0
        voxel_vol[:, :, : prune_min[2]] = 0
        voxel_vol[prune_max[0] :, :, :] = 0
        voxel_vol[:, prune_max[1] :, :] = 0
        voxel_vol[:, :, prune_max[2] :] = 0

        return voxel_vol

    @classmethod
    def get_voxel_data(cls, collision_spec):
        if cls._prim_change_listener is None or cls._stage_event_listener is None:
            cls._prim_change_listener = Tf.Notice.Register(
                Usd.Notice.ObjectsChanged, cls._on_prim_change, omni.usd.get_context().get_stage()
            )
            cls._stage_event_listener = carb.eventdispatcher.get_eventdispatcher().observe_event(
                event_name=omni.usd.get_context().stage_event_name(omni.usd.StageEventType.CLOSED),
                on_event=cls._on_stage_closed,
                observer_name="replicator.utils.mesh_voxel_utils:stage_closed",
            )

        # Validate input
        try:

            # ensure that all sample prims are xformable
            for prim in collision_spec.prims:
                if not UsdGeom.Xformable(prim):
                    prim_type = prim.GetTypeName()
                    raise ValueError(
                        f"Expected prim at {prim.GetPath()} to be an Xformable prim but got type {prim_type}"
                    )
                elif prim.GetAttribute("xformOp:translate") is None:
                    UsdGeom.Xformable(prim).AddTranslateOp()
            resolution = int(np.round(DEFAULT_VOXEL_RESOLUTION * collision_spec.resolution_scaling))

            if resolution < 1:
                raise ValueError(
                    f"Expected inputs:resolutionScaling to be at least {1/30} but got value {collision_spec.resolution_scaling}"
                )
        except Exception as error:
            raise RuntimeError(f"Scatter3D Error: {error}")

        if cls._resolution == -1:
            cls._resolution = resolution
        # if we change the resolution, we need to re-voxelize every mesh and reset the state
        elif cls._resolution != resolution:
            cls._voxel_p = {}
            cls._resolution = resolution

        voxel_p_curr_update = dict()
        for idx, (prim, prim_path) in enumerate(zip(collision_spec.volume_prims, collision_spec.volume_prim_paths)):
            scale_3D = np.linalg.norm(utils.read_prim_transform(prim), axis=-1)
            voxel_p_curr_update[prim_path] = VoxelGridProperties(mesh_scale=scale_3D[:3])

        voxel_size = VoxelUtils._compute_voxel_size(
            default_voxel_size=collision_spec.input_voxel_size,
            resolution=resolution,
            volume_prims=collision_spec.volume_prims,
            volume_prim_paths=collision_spec.volume_prim_paths,
            voxel_p=voxel_p_curr_update,
        )
        voxel_p_out = {}

        for idx, (prim, prim_path) in enumerate(zip(collision_spec.volume_prims, collision_spec.volume_prim_paths)):
            # TODO: Allow sampling from primitive shapes (i.e. cube, sphere, cone, capsule)
            scale_multiplier = np.prod(voxel_p_curr_update[prim_path].mesh_scale)

            # voxelize meshes if necessary
            if prim_path not in cls._voxel_p or not np.array_equal(
                cls._voxel_p[prim_path].mesh_scale_multiplier, scale_multiplier
            ):

                if prim_path in cls._voxel_p:
                    del cls._voxel_p[prim_path]

                vertices = np.array(prim.GetAttribute("points").Get())  # translation in cm
                faces_indices = np.array(prim.GetAttribute("faceVertexIndices").Get())
                face_vertex_counts = np.array(prim.GetAttribute("faceVertexCounts").Get())

                # convert prim mesh to a triangle mesh
                faces = MeshUtils._convert_poly_to_tri(vertices, faces_indices, face_vertex_counts)

                # generate voxel grid
                global_transform = np.array(
                    utils.read_prim_transform(prim)
                )  # translation in cm. this includes the scaling.
                verts_global = (np.hstack((vertices, np.ones((vertices.shape[0], 1)))) @ global_transform)[:, :3]
                voxel_surface, extents_voxel_xyz = VoxelUtils._trianglemesh_to_voxelgrid(
                    verts_global, faces, voxel_size
                )
                # fill voxel volume
                voxel_vol = VoxelUtils._fill(voxel_surface)

                if np.sum(voxel_surface) == np.sum(voxel_vol) and np.sum(voxel_vol) > 8:
                    carb.log_warn(
                        f"Unable to fill voxel volume of {prim.GetPath()}. Cause may include that the voxel size is relatively large, the mesh is very thin, or the surface is not watertight. Suggest inspecting the mesh and/or increasing the voxel size."
                    )

                if collision_spec.prevent_vol_overlap:
                    # remove overlap from previous included prims
                    voxel_vol = VoxelUtils._rm_overlap_direct(voxel_vol, extents_voxel_xyz, voxel_size, cls._voxel_p)

                # remove overlap from ALL exclusion prims
                voxel_vol = VoxelUtils._rm_excl_objs(
                    voxel_vol,
                    extents_voxel_xyz,
                    voxel_size,
                    collision_spec.volume_excl_prims,
                    collision_spec.volume_excl_prim_paths,
                )

                # prune the voxel volume based on the user provided global min and max, this increases sample efficiency
                voxel_vol = VoxelUtils._prune_samp_bounds(
                    voxel_vol, extents_voxel_xyz, voxel_size, collision_spec.extents[0], collision_spec.extents[1]
                )

                # visualize the voxels used for sampling
                if collision_spec.viz_sampled_voxels:
                    VoxelUtils._viz_create_voxelcubes(prim_path, voxel_vol, extents_voxel_xyz, voxel_size)

                voxels = np.array(np.nonzero(voxel_vol)).transpose()

                # set properties of voxels
                cls._voxel_p[prim_path] = VoxelGridProperties(
                    voxels=voxels,
                    voxel_size=voxel_size,
                    voxel_vol=voxel_vol,
                    voxel_extents=extents_voxel_xyz,
                    mesh_scale_multiplier=scale_multiplier,
                )

                # cls._cache[str(prim.GetPath())] = mesh_data

                cur_prim_path = prim.GetPath()
                prims_to_watch = set()
                while not cur_prim_path.IsRootPrimPath():
                    prims_to_watch.add(cur_prim_path)
                    cur_prim_path = cur_prim_path.GetParentPath()
                prims_to_watch.add(cur_prim_path)

                cls._watched_prim_paths.update(prims_to_watch)

            voxel_p_out[prim_path] = cls._voxel_p[prim_path]

        return voxel_p_out

    @classmethod
    def sample_points_voxelgrid(
        cls, num_samples: int, voxel_p: dict, rng_generator: np.random.Generator, prune_func_list: list
    ):
        """Computes array of points sampled on the voxelgrid that are within the provide min and max sampling bounds

        Args:
            num_samples: The number of points you wish to sample
            voxel_p: voxel properties, containing voxel grid and associated properties
            rng_generator: random noise generator
            prune_func_list: A list of pruning functions used for rejection sampling of sampled points

        Returns:
            A (num_samples x 3) array of sampled points

        """

        N_left_to_sample = num_samples
        N_loop = 0
        sampled_points = None
        normalization_constant = np.sum([voxel_p[prim_path].weights for prim_path in voxel_p])

        # loop until we have enough sampled coordinates within min_samp and max_samp
        while sampled_points is None or sampled_points.shape[0] < num_samples:

            weight_arr = [voxel_p[prim_path].weights for prim_path in voxel_p]

            # rng_generator.multinomial requires float64 datatypes for the weighting
            sampled_meshes = rng_generator.multinomial(
                N_left_to_sample, np.array(weight_arr).astype(np.float64) / normalization_constant
            )

            sampled_points_new = list()
            for idx, prim_path in enumerate(voxel_p):  # go through the index and keys of prim paths dict
                num_in_mesh = sampled_meshes[idx]
                sampled_indices = rng_generator.choice(voxel_p[prim_path].voxels.shape[0], num_in_mesh)
                sampled_voxels = voxel_p[prim_path].voxels[sampled_indices]

                # generate a random point within the voxel in the voxel's local coordinate
                noise_matrix = rng_generator.random((num_in_mesh, 3))
                norm_sampled_points = sampled_voxels + noise_matrix

                # convert to mesh coordinate frame
                mesh_coords = norm_sampled_points * voxel_p[prim_path].voxel_size + voxel_p[prim_path].voxel_extents[0]
                sampled_points_new.append(mesh_coords)

            sampled_points_new = np.concatenate(sampled_points_new)
            rng_generator.shuffle(sampled_points_new)

            for prune_func in prune_func_list:
                sampled_points_new = prune_func(sampled_points_new)

            if sampled_points is None:
                sampled_points = sampled_points_new
            elif sampled_points is not None and len(sampled_points_new.shape) > 0:
                sampled_points = np.concatenate((sampled_points, sampled_points_new), axis=0)

            if sampled_points is not None:
                N_left_to_sample = num_samples - sampled_points.shape[0]

            N_loop += 1

            if N_loop >= 900:
                raise ValueError(
                    "Randomization timed out, cannot find a set of samples within the global sampling bounds provided."
                )

        return sampled_points

    @staticmethod
    def _viz_create_voxelcubes(prim_path, voxel_vol, extents_voxel_xyz, voxel_size):
        """Visualizes the sampling space by creating point instances of semi-transparent green cubes where the sampled
        voxels are.

        Args:
            prim_path: The input prim path for a voxelized mesh
            voxel_vol: A 3D voxel grid containing the a binary mask over enclosed spaces.
            extents_voxel_xyz: A 2D array representing the indices (I, 3) of the vertices for the corresponding faces.
            voxel_size: The size of each voxel (applies to x,y,z) in cm

        """

        stage = omni.usd.get_context().get_stage()
        num_cubes = int(np.sum(voxel_vol))
        geomPointInstancerPath = "/Replicator/" + "_".join(prim_path.split("/")[2:]) + "_PI"
        boxActorPath = geomPointInstancerPath + "/boxActor"
        pi_prim = stage.GetPrimAtPath(geomPointInstancerPath)

        if not pi_prim:
            # Box instanced
            cubeGeom = UsdGeom.Cube.Define(stage, boxActorPath)
            cubeGeom.CreateSizeAttr(voxel_size / 1.1)

            # Create point instancer
            shapeList = UsdGeom.PointInstancer.Define(stage, Sdf.Path(geomPointInstancerPath))
            meshList = shapeList.GetPrototypesRel()

            # add mesh reference to point instancer
            meshList.AddTarget(Sdf.Path(boxActorPath))
            recently_defined = True
        else:
            shapeList = UsdGeom.PointInstancer(pi_prim)
            recently_defined = False

        # indices
        meshIndices = [0] * num_cubes
        positions = []

        for i in range(voxel_vol.shape[0]):
            for j in range(voxel_vol.shape[1]):
                for k in range(voxel_vol.shape[2]):
                    if voxel_vol[i, j, k] == 1:
                        position = (
                            extents_voxel_xyz[0][0] + (i + 0.5) * voxel_size,
                            extents_voxel_xyz[0][1] + (j + 0.5) * voxel_size,
                            extents_voxel_xyz[0][2] + (k + 0.5) * voxel_size,
                        )
                        positions.append(Gf.Vec3f(position[0], position[1], position[2]))

        shapeList.GetProtoIndicesAttr().Set(meshIndices)
        shapeList.GetPositionsAttr().Set(positions)

        geomMaterialPath = "/Replicator/Looks/OmniPBR_PI"
        pi_mtl_prim = stage.GetPrimAtPath(geomMaterialPath)

        if not pi_mtl_prim:
            _settings = carb.settings.get_settings()
            _settings.set_bool("/rtx/raytracing/fractionalCutoutOpacity", True)

            # create material prim and bind
            materialScopePath = "/Replicator/Looks"
            if not stage.GetPrimAtPath(materialScopePath):
                UsdGeom.Scope.Define(stage, materialScopePath)

            material = UsdShade.Material.Define(stage, geomMaterialPath)
            shader = UsdShade.Shader.Define(stage, Sdf.Path(geomMaterialPath).AppendPath("Shader"))
            shader.CreateImplementationSourceAttr(UsdShade.Tokens.sourceAsset)

            usdPreviewSurfaceShaderOutput = shader.CreateOutput("out", Sdf.ValueTypeNames.Token)
            usdPreviewSurfaceShaderOutput.SetRenderType("material")

            shader.GetPrim().CreateAttribute("inputs:diffuse_tint", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(0, 1, 0))
            shader.GetPrim().CreateAttribute("inputs:enable_opacity", Sdf.ValueTypeNames.Bool).Set(True)
            shader.GetPrim().CreateAttribute("inputs:opacity_constant", Sdf.ValueTypeNames.Float).Set(0.27)

            # MDL shaders should use "mdl" sourceType
            shader.SetSourceAsset("OmniPBR.mdl", "mdl")
            shader.SetSourceAssetSubIdentifier("OmniPBR", "mdl")
            # MDL materials should use "mdl" renderContext
            material.CreateSurfaceOutput("mdl").ConnectToSource(shader.ConnectableAPI(), "out")
            material.CreateDisplacementOutput("mdl").ConnectToSource(shader.ConnectableAPI(), "out")
            material.CreateVolumeOutput("mdl").ConnectToSource(shader.ConnectableAPI(), "out")

            cubePrim = stage.GetPrimAtPath(boxActorPath)
            cubePrim.ApplyAPI(UsdShade.MaterialBindingAPI)
            UsdShade.MaterialBindingAPI(cubePrim).Bind(material, UsdShade.Tokens.weakerThanDescendants)

        elif recently_defined:
            # The point instancer is newly defined and needs to be bound to the material
            material = UsdShade.Material(stage.GetPrimAtPath(geomMaterialPath))

            cubePrim = stage.GetPrimAtPath(boxActorPath)
            cubePrim.ApplyAPI(UsdShade.MaterialBindingAPI)
            UsdShade.MaterialBindingAPI(cubePrim).Bind(material, UsdShade.Tokens.weakerThanDescendants)
