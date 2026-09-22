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

from typing import List, Tuple, Union

import numpy as np
import omni.replicator.core as rep
import omni.replicator.core.functional as F
import omni.usd
import pxr
import usdrt
from omni.replicator.core.utils import mesh_voxel_utils as mvu


def _scatter_no_collision_check(prims, num_samples, rng_generator, reject_cls, collision_spec: mvu.CollisionCheckSpec):

    if collision_spec.scatter_type == "2d":
        sampled_points = mvu.MeshUtils().sample_points_meshsurface(
            num_samples,
            collision_spec.surface_meshes,
            collision_spec.extents,
            rng_generator,
            collision_spec.offset,
            [reject_cls._delete_outside_minmax],
        )
    elif collision_spec.scatter_type == "3d":

        voxel_p = mvu.VoxelUtils().get_voxel_data(collision_spec)
        sampled_points = mvu.VoxelUtils().sample_points_voxelgrid(
            num_samples,
            voxel_p,
            rng_generator,
            [reject_cls._delete_outside_minmax],
        )
    else:
        raise RuntimeError("must choose valid scatter_type of 2d or 3d")
    F.modify.pose(prims, position_value=sampled_points)


def _scatter_with_collision_check(
    prims, nocoll_prims, check_for_collisions, rng_generator, reject_cls, collision_spec: mvu.CollisionCheckSpec
):
    sampled_points = []
    paths_check = []
    paths_check_extra = []
    pi_paths_check = []
    pi_c_to_desc = {}
    sample_prims_cl = []  # collision loop prims list
    collision_checker = mvu.CollisionUtilities()

    def populate_meshes(recur_prim, child, check_for_collisions=True):
        if str(recur_prim.GetTypeName()) in ["Mesh", "Shape"]:
            pi_c_to_desc[str(child.GetPath())].append(str(recur_prim.GetPath()))
            if check_for_collisions:
                pi_paths_check.append(str(recur_prim.GetPath()))
        for sub_recur_prim in recur_prim.GetChildren():
            populate_meshes(sub_recur_prim, child, check_for_collisions)

    for prim in prims:
        if prim.GetTypeName() == "PointInstancer":
            proto_indices = prim.GetAttribute("protoIndices").Get()
            for proto_idx in proto_indices:
                sample_prims_cl.append(prim.GetChildren()[proto_idx])
            for child in prim.GetChildren():
                pi_c_to_desc[str(child.GetPath())] = []
                populate_meshes(child, child, check_for_collisions)
        else:
            sample_prims_cl.append(prim)

    for nocoll_prim in nocoll_prims:
        if nocoll_prim.GetTypeName() == "PointInstancer":
            for child in nocoll_prim.GetChildren():
                pi_c_to_desc[str(child.GetPath())] = []
                populate_meshes(child, child, True)
        else:
            if str(nocoll_prim.GetPath()) not in paths_check_extra:
                paths_check_extra.append(str(nocoll_prim.GetPath()))

    if collision_spec.scatter_type == "3d":
        voxel_p = mvu.VoxelUtils().get_voxel_data(collision_spec)

    for prim_cl in sample_prims_cl:
        prim_type_name = str(prim_cl.GetTypeName())
        is_point_instancer = prim_cl.GetParent().GetTypeName() == "PointInstancer"

        # Get all mesh descendants
        sample_paths_mesh_curr = []
        sample_paths_mesh_curr_types = []
        sample_paths_type_primpos = []
        if not is_point_instancer:
            if prim_type_name in ["Mesh", "Shape"]:
                sample_paths_mesh_curr.append(str(prim_cl.GetPath()))
                sample_paths_mesh_curr_types.append(prim_cl.GetTypeName())
                sample_paths_type_primpos.append(prim_cl.GetTypeName())
            else:
                for child in prim_cl.GetChildren():
                    if "xformOpOrder" in child.GetPropertyNames() or (
                        "points" in child.GetPropertyNames() and "xformOp:translate" in child.GetPropertyNames()
                    ):
                        sample_paths_mesh_curr.append(str(child.GetPath()))
                        sample_paths_mesh_curr_types.append(child.GetTypeName())
                        sample_paths_type_primpos.append(prim_cl.GetTypeName())

        # Skip if no valid mesh found
        if not is_point_instancer and len(sample_paths_mesh_curr) == 0:
            continue

        path_cl = str(prim_cl.GetPath())
        count = 0
        intersecting = True

        while intersecting:
            if collision_spec.scatter_type == "2d":
                sample = (
                    mvu.MeshUtils()
                    .sample_points_meshsurface(
                        1,
                        collision_spec.surface_meshes,
                        collision_spec.extents,
                        rng_generator,
                        collision_spec.offset,
                        [reject_cls._delete_outside_minmax],
                    )
                    .tolist()[0]
                )
            elif collision_spec.scatter_type == "3d":
                sample = (
                    mvu.VoxelUtils()
                    .sample_points_voxelgrid(
                        1,
                        voxel_p,
                        rng_generator,
                        [reject_cls._delete_outside_minmax],
                    )
                    .tolist()[0]
                )

            if is_point_instancer:
                path_list = [path_cl]
                # loop through all collision meshes within the instance we are setting position of
                for pi_path in pi_c_to_desc[path_cl]:
                    intersecting = collision_checker.check_m_collision(
                        paths_check_extra, pi_paths_check, pi_path, True, sample, True
                    )
                    if intersecting:
                        break
            else:
                if prim_type_name not in ["Mesh", "GeomSubset"] and len(prim_cl.GetChildren()) > 0:
                    for prim_g_child in prim_cl.GetChildren():
                        # if the child is not a mesh maybe the gchildren will be meshes. better to apply collision APIs to those to avoid crashes like OM100140
                        if prim_g_child.GetTypeName() in ["Mesh", "GeomSubset"]:
                            # TODO: This will only store one mesh
                            path_cl = str(prim_g_child.GetPath())

                path_list = []
                # loop through all collision meshes within the xform we are setting position of
                for path_m, path_m_type, path_m_primpos_type in zip(
                    sample_paths_mesh_curr, sample_paths_mesh_curr_types, sample_paths_type_primpos
                ):
                    if path_m_type == "Camera":
                        continue

                    # if we're altering the parent xform of a mesh, KEEP the mesh offset if its there
                    if path_m_primpos_type == "Xform":
                        reset_mesh_offset_pos = False
                    # otherwise if we're directly altering the mesh position, RESET it with the sampled one
                    else:
                        reset_mesh_offset_pos = True

                    path_list.append(path_m)

                    if check_for_collisions:
                        intersecting = collision_checker.check_m_collision(
                            paths_check_extra + paths_check,
                            pi_paths_check,
                            path_m,
                            False,
                            sample,
                            reset_mesh_offset_pos,
                        )
                    else:
                        intersecting = collision_checker.check_m_collision(
                            paths_check_extra, pi_paths_check, path_m, False, sample, reset_mesh_offset_pos
                        )
                    if intersecting:
                        break

            count += 1
            if intersecting and count >= 10000:
                raise ValueError(
                    "Randomization timed out while scattering, cannot find a configuration to randomize prim locations and prevent collisions."
                )

        paths_check += path_list
        sampled_points.append(sample)

    collision_checker.update_collision_cache(paths_check_extra + paths_check)
    collision_checker.clear_actors()

    F.modify.pose(prims, position_value=sampled_points)


def scatter_2d(
    prims: Union[pxr.Usd.Prim, usdrt.Usd.Prim, List[Union[pxr.Usd.Prim, usdrt.Usd.Prim]]],
    surface_prims: Union[pxr.Usd.Prim, usdrt.Usd.Prim, List[Union[pxr.Usd.Prim, usdrt.Usd.Prim]]],
    no_collision_prims: Union[pxr.Usd.Prim, usdrt.Usd.Prim, List[Union[pxr.Usd.Prim, usdrt.Usd.Prim]]] = None,
    extents: Tuple[Tuple[float, float, float], Tuple[float, float, float]] = None,
    offset: float = 0.0,
    check_for_collisions: bool = False,
    rng: np.random.Generator = None,
) -> None:
    """Scatter the prims in 2D space.

    Args:
        prims: The prims to scatter.
        surface_prims: The surface prims to sample points from.
        no_collision_prims: Existing prim(s) to prevent collisions with - if any prims are passed they will be checked for
            collisions which may slow down compute, regardless if ``check_for_collisions`` is ``True`` or ``False``.
        extents: The 3D extents of the sampling volume.
        offset: The distance the prims should be offset along the normal of the surface of the mesh.
        check_for_collisions: Whether the scatter operation should ensure that objects are not intersecting
        rng: The random number generator to use. If `None`, a new generator will be created using
            `np.random.default_rng()`.

    Example:
        >>> import omni.replicator.core.functional as F
        >>> import omni.replicator.core as rep
        >>> rng = rep.rng.ReplicatorRNG()
        >>> surface_prim = F.create.plane(name="surface_prim", position=(0, 0, 0), scale=(10, 1, 10))
        >>> prims = F.create_batch.cube(count=10, position=(0, 0, 0), scale=(1, 1, 1))
        >>> F.randomizer.scatter_2d(prims, surface_prim, rng=rng)
    """
    if not surface_prims:
        raise ValueError("Invalid surface prims")

    if not prims:
        raise ValueError("Invalid prims")

    if rng is None:
        rng_generator = np.random.default_rng()
    elif isinstance(rng, rep.rng.ReplicatorRNG):
        rng_generator = rng.generator
    elif isinstance(rng, np.random.Generator):
        rng_generator = rng
    else:
        raise NotImplementedError(
            f"Unsupported RNG type: {type(rng)}. Only `rep.rng.ReplicatorRNG` and `np.random.Generator` are supported."
        )

    if isinstance(prims, (pxr.Usd.Prim, usdrt.Usd.Prim)):
        prims = [prims]

    if isinstance(surface_prims, (pxr.Usd.Prim, usdrt.Usd.Prim)):
        surface_prims = [surface_prims]

    if no_collision_prims is None:
        no_collision_prims = []

    surface_prim_paths = [p.GetPath() for p in surface_prims]
    no_collision_prim_paths = [p.GetPath() for p in no_collision_prims]

    if extents is None:
        extents = ([-3.4028235e38, -3.4028235e38, -3.4028235e38]), ([3.4028235e38, 3.4028235e38, 3.4028235e38])

    # set up the sample pruning class
    reject_cls = mvu.RejectPoints()
    reject_cls._set_minmax(*extents)

    # validate input
    stage = omni.usd.get_context().get_stage()

    # TODO: Allow sampling from primitive shapes (i.e. cube, sphere, cone, capsule), not just meshes!
    surface_meshes, _ = mvu.MeshUtils._check_get_meshes(stage, surface_prim_paths, ["Mesh", "GeomSubset"])
    nocoll_meshes, _ = mvu.MeshUtils._check_get_meshes(
        stage, no_collision_prim_paths, ["Mesh", "GeomSubset", "PointInstancer", "Xform"]
    )

    num_samples = 0
    for prim in prims:
        if not prim.IsA(pxr.UsdGeom.Xformable):
            raise ValueError(
                f"Expected prim at {prim.GetPath()} to be an Xformable prim but got type {prim.GetTypeName()}"
            )
        elif not prim.HasAttribute("xformOp:translate"):
            pxr.UsdGeom.Xformable(prim).AddTranslateOp()
        if prim.IsA(pxr.UsdGeom.PointInstancer):
            num_samples += len(prim.GetAttribute("protoIndices").Get())
        else:
            num_samples += 1

    collision_spec = mvu.CollisionCheckSpec("2d")
    collision_spec.set_2d_spec(surface_meshes, offset, extents)
    if not check_for_collisions and len(no_collision_prims) == 0:
        _scatter_no_collision_check(prims, num_samples, rng_generator, reject_cls, collision_spec)
    else:
        _scatter_with_collision_check(
            prims, nocoll_meshes, check_for_collisions, rng_generator, reject_cls, collision_spec
        )


def scatter_3d(
    prims: Union[pxr.Usd.Prim, usdrt.Usd.Prim, List[Union[pxr.Usd.Prim, usdrt.Usd.Prim]]],
    volume_prims: Union[pxr.Usd.Prim, usdrt.Usd.Prim, List[Union[pxr.Usd.Prim, usdrt.Usd.Prim]]] = None,
    no_collision_prims: Union[pxr.Usd.Prim, usdrt.Usd.Prim, List[Union[pxr.Usd.Prim, usdrt.Usd.Prim]]] = None,
    volume_excl_prims: Union[pxr.Usd.Prim, usdrt.Usd.Prim, List[Union[pxr.Usd.Prim, usdrt.Usd.Prim]]] = None,
    extents: Tuple[Tuple[float, float, float], Tuple[float, float, float]] = None,
    check_for_collisions: bool = False,
    prevent_vol_overlap: bool = True,
    viz_sampled_voxels: bool = False,
    resolution_scaling: float = 1.0,
    input_voxel_size: float = 0.0,
    rng: np.random.Generator = None,
) -> None:
    """Scatter the prims in 3D space.

    Args:
        prims: The prims to scatter.
        volume_prims: The volume prims to sample points from.
        no_collision_prims: Existing prim(s) to prevent collisions with - if any prims are passed they will be checked for
            collisions using rejection sampling. This may slow down compute, regardless if check_for_collisions is
            True/False.
        volume_excl_prims: Prim(s) from which to exclude from sampling. Must have watertight meshes. Similar effect to
            ``no_coll_prims``, but more efficient and less accurate. Rather than performing rejection sampling based on
            collision with the provided volume (as ``no_coll_prims`` does), this prunes off the voxelized sampling space
            enclosed by ``volume_excl_prims`` so the rejection rate is 0 because it never tires to sample in the
            excluded space. However, some objects may get sampled very close to the edge of a mesh in
            ``volume_excl_prims``, where the sampled root point is outside ``volume_excl_prims`` but parts of the mesh
            extend to overlap the space. To get the best of both worlds, you can pass the same volume prim to both
            ``no_coll_prims`` and to ``volume_excl_prims``, providing a high accuracy and a low rejection rate.
        extents: The extents of the sampling volume.
        check_for_collisions: Whether the scatter operation should ensure that sampled objects are not intersecting.
        prevent_vol_overlap: If ``True``, prevents double sampling even when multiple enclosing volumes overlap, so that
            the entire enclosed volume is sampled uniformly. If ``False``, it allows overlapped sampling with higher
            density in overlapping areas.
        viz_sampled_voxels: If ``True``, creates semi-transparent green cubes in all voxels in the scene that the input
            prim positions are sampled from.
        resolution_scaling: Amount the default voxel resolution used in sampling should be scaled. More complex meshes
            may require higher resolution. Default voxel resolution is 30 for the longest side of the mean sized
            volumePrim mesh provided. Higher values will ensure more fine-grained voxels, but will come at the cost of
            performance.
        input_voxel_size: Voxel size used to compute the resolution. If this is provided, then resolution_scaling is ignored,
            otherwise (if it is ``0`` by default) resolution_scaling is used.
        rng: The random number generator to use. If `None`, a new generator will be created using
            `np.random.default_rng()`.

    Example:
        >>> import omni.replicator.core.functional as F
        >>> import omni.replicator.core as rep
        >>> rng = rep.rng.ReplicatorRNG()
        >>> volume_prim = F.create.torus(name="volume_prim", position=(0, 0, 0), scale=(10, 10, 10), visible=False)
        >>> prims = F.create_batch.cube(count=500, position=(0, 0, 0), scale=(1, 1, 1))
        >>> F.randomizer.scatter_3d(prims, volume_prim, rng=rng)
    """

    if not prims:
        raise ValueError("Invalid prims")

    if rng is None:
        rng_generator = np.random.default_rng()
    elif isinstance(rng, rep.rng.ReplicatorRNG):
        rng_generator = rng.generator
    elif isinstance(rng, np.random.Generator):
        rng_generator = rng
    else:
        raise NotImplementedError(
            f"Unsupported RNG type: {type(rng)}. Only `rep.rng.ReplicatorRNG` and `np.random.Generator` are supported."
        )

    if isinstance(prims, (pxr.Usd.Prim, usdrt.Usd.Prim)):
        prims = [prims]

    if isinstance(volume_prims, (pxr.Usd.Prim, usdrt.Usd.Prim)):
        volume_prims = [volume_prims]

    if isinstance(volume_excl_prims, (pxr.Usd.Prim, usdrt.Usd.Prim)):
        volume_excl_prims = [volume_excl_prims]

    if no_collision_prims is None:
        no_collision_prims = []

    if volume_excl_prims is None:
        volume_excl_prims = []

    prim_paths = [p.GetPath() for p in prims]
    volume_prim_paths = (
        [p.GetPath() for p in volume_prims] if volume_prims else []
    )  # Can be empty if extents are specified
    no_collision_prim_paths = [p.GetPath() for p in no_collision_prims]
    volume_excl_prim_paths = [p.GetPath() for p in volume_excl_prims]

    if extents is None:
        if volume_prims is None:
            raise ValueError("No enclosing volume provided and no extents specified.")
        extents = ([-3.4028235e38, -3.4028235e38, -3.4028235e38]), ([3.4028235e38, 3.4028235e38, 3.4028235e38])
    else:
        # Validate extents
        assert (
            len(extents) == 2
        ), "Extents must be a tuple of two tuples in the form ((min_x, min_y, min_z), (max_x, max_y, max_z))"
        assert len(extents[0]) == 3, "Extents must be in the form ((min_x, min_y, min_z), (max_x, max_y, max_z))"
        assert len(extents[1]) == 3, "Extents must be in the form ((min_x, min_y, min_z), (max_x, max_y, max_z))"

        # Ensure min extents are less than max extents
        if any(extents[0][i] > extents[1][i] for i in range(3)):
            raise ValueError(
                f"The min {extents[0]} and max {extents[1]} sampling bounds are not valid. The min extents must be less than the max extents."
            )

    # set up the sample pruning class
    reject_cls = mvu.RejectPoints()
    reject_cls._set_minmax(*extents)

    # validate input
    stage = omni.usd.get_context().get_stage()

    # if there is no input enclosing volume we need to create it based on the min/max sampling bounds
    if len(volume_prim_paths) == 0:
        if any(bound < -3.402823e38 for bound in extents[0]) or any(bound > 3.402823e38 for bound in extents[1]):
            raise ValueError(
                f"No enclosing volume provided and the min {extents[0]} and max {extents[1]} sampling bounds are very large. Exiting node."
            )

        # Create a cube volume based on supplied extents
        vol_encl_prim_new = F.create.cube(
            name="CubeVolEncl",
            position=tuple(np.mean((extents[0], extents[1]), axis=0)),
            scale=tuple((np.subtract(extents[1], extents[0]) / 100.0)),
            visible=False,
        )
        volume_prim_paths = [str(vol_encl_prim_new.GetPath())]

    num_samples = 0
    for prim in prims:
        if not prim.IsA(pxr.UsdGeom.Xformable):
            raise ValueError(
                f"Expected prim at {prim.GetPath()} to be an Xformable prim but got type {prim.GetTypeName()}"
            )
        elif not prim.HasAttribute("xformOp:translate"):
            pxr.UsdGeom.Xformable(prim).AddTranslateOp()
        if prim.IsA(pxr.UsdGeom.PointInstancer):
            num_samples += len(prim.GetAttribute("protoIndices").Get())
        else:
            num_samples += 1

    # TODO: Allow sampling from primitive shapes (i.e. cube, sphere, cone, capsule), not just meshes!
    volume_prims, volume_prim_paths = mvu.MeshUtils._check_get_meshes(stage, volume_prim_paths)
    no_collision_prims, no_collision_prim_paths = mvu.MeshUtils._check_get_meshes(
        stage, no_collision_prim_paths, ["Mesh", "GeomSubset", "PointInstancer", "Xform"]
    )
    volume_excl_prims, volume_excl_prim_paths = mvu.MeshUtils._check_get_meshes(stage, volume_excl_prim_paths)

    collision_spec = mvu.CollisionCheckSpec("3d")
    collision_spec.set_3d_spec(
        (prims, prim_paths),
        (volume_prims, volume_prim_paths),
        (no_collision_prims, no_collision_prim_paths),
        (volume_excl_prims, volume_excl_prim_paths),
        extents,
        prevent_vol_overlap,
        viz_sampled_voxels,
        resolution_scaling,
        input_voxel_size,
    )

    if not check_for_collisions and len(no_collision_prims) == 0:
        _scatter_no_collision_check(prims, num_samples, rng_generator, reject_cls, collision_spec)
    else:
        _scatter_with_collision_check(
            prims, no_collision_prims, check_for_collisions, rng_generator, reject_cls, collision_spec
        )
