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

import sys
from typing import Callable, List, Optional, Tuple, Union

import omni.graph.core as og
import usdrt
from pxr import Sdf, Usd

from . import distribution, objects  # noqa: F401
from .utils.utils import (
    ReplicatorItem,
    ReplicatorWrapper,
    _connect_prims,
    _setup_random_attribute,
    _validate_paths,
    create_node,
    set_target_prims,
)


def register(  # pylint: disable=invalid-name
    fn: Callable[..., Union[ReplicatorItem, og.Node]], override: bool = True, fn_name: str = None
) -> None:
    """Register a new function under ``omni.replicator.core.randomizer``.
    Extend the default capabilities of ``omni.replicator.core.randomizer`` by registering new functionality. New
    functions must return a ``ReplicatorItem`` or an ``OmniGraph`` node.

    Args:
        fn: A function that returns a ``ReplicatorItem`` or an ``OmniGraph`` node.
        override: If ``True``, will override existing functions of the same name. If ``False``, an error is raised.
        fn_name: Optional arg that let user choose the function name when registering it in replicator. If not
        specified, the function name is used. ``fn_name`` must follow valid [Python identifier rules]
        (https://docs.python.org/3.10/reference/lexical_analysis.html#identifiers)

    Example:
        >>> import omni.replicator.core as rep
        >>> def scatter_points(points):
        ...     return rep.modify.pose(position=rep.distribution.choice(points))
        >>> rep.randomizer.register(scatter_points)
        >>> with rep.create.cone():
        ...     rep.randomizer.scatter_points([(0, 0, 0), (0, 0, 100), (0, 0, 200)])
        omni.replicator.core.randomizer.scatter_points
    """
    if fn_name is None:
        fn_name = fn.__name__

    if not fn_name.isidentifier():
        raise ValueError(
            f"The function name {fn_name} is not a valid Python identifier. fn_name must only contains alphanumeric "
            "letters (a-z), numbers (0-9) or underscores (_) and cannot start with a number or contain any spaces."
        )

    module = sys.modules[__name__]
    if fn_name in dir(module):
        if override:
            print(f"Overriding function {{{fn_name}}} for replicator.randomizer.")
        else:
            raise ValueError()

    wrapped_fn = ReplicatorWrapper(fn)
    setattr(sys.modules[__name__], fn_name, wrapped_fn)


@ReplicatorWrapper
def scatter_2d(
    surface_prims: Union[ReplicatorItem, List[str]],
    no_coll_prims: Union[ReplicatorItem, List[str]] = None,
    min_samp: Tuple[float, float, float] = (None, None, None),
    max_samp: Tuple[float, float, float] = (None, None, None),
    seed: int = None,
    offset: int = 0,
    check_for_collisions: bool = False,
    input_prims: Union[ReplicatorItem, List[str]] = None,
    name: Optional[str] = None,
) -> ReplicatorItem:
    """Scatter input prims across the surface of the specified surface prims.

    Args:
        surface_prims: The prims across which to scatter the input prims. These can be meshes or GeomSubsets which
            specify a subset of a mesh's polygons on which to scatter.
        no_coll_prims: Existing prim(s) to prevent collisions with - if any prims are passed they will be checked for
            collisions which may slow down compute, regardless if ``check_for_collisions`` is ``True`` or ``False``.
        min_samp: The minimum position in global space to sample from.
        max_samp: The maximum position in global space to sample from.
        seed: Seed to use as initialization for the pseudo-random number generator. If not specified, the global seed
            will be used.
        offset: The distance the prims should be offset along the normal of the surface of the mesh.
        check_for_collisions: Whether the scatter operation should ensure that objects are not intersecting.

                - ``0``: No collision checking (fastest)
                - ``1``: Check for collisions among the sampled input prims,
                - ``2``: No collision checking among sampled input prims, but compute collision convex meshes for all
                  the prims on the stage by recursively traversing the stage, and make sure the sampled prims do not
                  collide with any of them.
                - ``3``: Make sure the sampled prims don't collide with anything (slowest)

        input_prims: The prims to be modified. If using ``with`` syntax, this argument can be omitted.
        name (optional): A name for the graph node.

    Example:
        >>> import omni.replicator.core as rep
        >>> spheres = rep.create.sphere(count=100)
        >>> surface_prim = rep.create.torus(scale=20, visible=False)
        >>> with spheres:
        ...     rep.randomizer.scatter_2d(surface_prim)
        omni.replicator.core.randomizer.scatter_2d
    """

    min_samp_t = tuple(-3.4028235e38 if v is None else v for v in min_samp)
    max_samp_t = tuple(3.4028235e38 if v is None else v for v in max_samp)

    node = create_node(
        "omni.replicator.core.OgnScatter2D",
        seed=seed,
        normalOffset=offset,
        checkForCollisions=check_for_collisions,
        minSamp=min_samp_t,
        maxSamp=max_samp_t,
        node_name=name,
    )

    # WAR for multiple prims limitations
    if input_prims:
        set_target_prims(node, "inputs:prims", input_prims)
    if surface_prims:
        if isinstance(surface_prims, ReplicatorItem):
            _connect_prims(node, "inputs:surfacePrims", surface_prims)
        else:
            set_target_prims(node, "inputs:surfacePrims", surface_prims)
    if no_coll_prims:
        if isinstance(no_coll_prims, ReplicatorItem):
            _connect_prims(node, "inputs:noCollPrims", no_coll_prims)
        else:
            # no_coll_prims_group = create_group(no_coll_prims) #TODO this does not work yet
            set_target_prims(node, "inputs:noCollPrims", no_coll_prims)
    return node


@ReplicatorWrapper
def scatter_3d(
    volume_prims: Union[ReplicatorItem, List[str]] = None,
    no_coll_prims: Union[ReplicatorItem, List[str]] = None,
    volume_excl_prims: Union[ReplicatorItem, List[str]] = None,
    min_samp: Tuple[float, float, float] = (None, None, None),
    max_samp: Tuple[float, float, float] = (None, None, None),
    resolution_scaling: float = 1.0,
    voxel_size: float = 0.0,
    check_for_collisions: bool = False,
    prevent_vol_overlap: bool = True,
    viz_sampled_voxels: bool = False,
    seed: int = None,
    input_prims: Union[ReplicatorItem, List[str]] = None,
    name: Optional[str] = None,
) -> ReplicatorItem:
    """Scatter input prims within the bounds of the specified volume prims.

    Args:
        volume_prims: The prims within which to scatter the input prims. Currently, only meshes are supported, and
            they must be watertight. If no prims are provided, you must specify min_samp and max_samp bounds.
        no_coll_prims: Existing prim(s) to prevent collisions with - if any prims are passed they will be checked for
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
        min_samp: The minimum position in global space to sample from.
        max_samp: The maximum position in global space to sample from.
        resolution_scaling: Amount the default voxel resolution used in sampling should be scaled. More complex meshes
            may require higher resolution. Default voxel resolution is 30 for the longest side of the mean sized
            volumePrim mesh provided. Higher values will ensure more fine-grained voxels, but will come at the cost of
            performance.
        voxel_size: Voxel size used to compute the resolution. If this is provided, then resolution_scaling is ignored,
            otherwise (if it is ``0`` by default) resolution_scaling is used.
        check_for_collisions: Whether the scatter operation should ensure that sampled objects are not intersecting.
        prevent_vol_overlap: If ``True``, prevents double sampling even when multiple enclosing volumes overlap, so that
            the entire enclosed volume is sampled uniformly. If ``False``, it allows overlapped sampling with higher
            density in overlapping areas.
        viz_sampled_voxels: If ``True``, creates semi-transparent green cubes in all voxels in the scene that the input
            prim positions are sampled from.
        seed: Seed to use as initialization for the pseudo-random number generator. If not specified, the global seed
            will be used.
        input_prims: The prims to be modified. If using ``with`` syntax, this argument can be omitted.
        name (optional): A name for the graph node.

    Example:
        >>> import omni.replicator.core as rep
        >>> spheres = rep.create.sphere(count=100)
        >>> volume_prim = rep.create.torus(scale=20, visible=False)
        >>> with spheres:
        ...     rep.randomizer.scatter_3d(volume_prim)
        omni.replicator.core.randomizer.scatter_3d
    """

    # If the volume prims are empty then we must fully define the min and max sampling extents
    if volume_prims is None and (
        not all(isinstance(bound, (float, int)) for bound in min_samp)
        or not all(isinstance(bound, (float, int)) for bound in max_samp)
    ):
        raise ValueError("Sampling volume is not fully defined")

    min_samp_t = tuple(-3.4028235e38 if v is None else v for v in min_samp)
    max_samp_t = tuple(3.4028235e38 if v is None else v for v in max_samp)

    node = create_node(
        "omni.replicator.core.OgnScatter3D",
        resolutionScaling=resolution_scaling,
        voxelSize=voxel_size,
        seed=seed,
        checkForCollisions=check_for_collisions,
        preventVolOverlap=prevent_vol_overlap,
        vizSampledVoxels=viz_sampled_voxels,
        minSamp=min_samp_t,
        maxSamp=max_samp_t,
        node_name=name,
    )

    # WAR for multiple prims limitations
    if input_prims:
        set_target_prims(node, "inputs:prims", input_prims)
    if volume_prims:
        if isinstance(volume_prims, ReplicatorItem):
            _connect_prims(node, "inputs:volumePrims", volume_prims)
        else:
            set_target_prims(node, "inputs:volumePrims", volume_prims)
    if no_coll_prims:
        if isinstance(no_coll_prims, ReplicatorItem):
            _connect_prims(node, "inputs:noCollPrims", no_coll_prims)
        else:
            set_target_prims(node, "inputs:noCollPrims", no_coll_prims)
    if volume_excl_prims:
        if isinstance(volume_excl_prims, ReplicatorItem):
            _connect_prims(node, "inputs:volumeExclPrims", volume_excl_prims)
        else:
            set_target_prims(node, "inputs:volumeExclPrims", volume_excl_prims)
    return node


@ReplicatorWrapper
def materials(  # pylint: disable=redefined-outer-name
    materials: Union[ReplicatorItem, List[str]],
    seed: int = None,
    max_cached_materials: int = 0,
    input_prims=None,
    name: Optional[str] = None,
) -> ReplicatorItem:
    """Sample materials from provided materials and bind to the input_prims.

    Note that binding materials is a relatively expensive operation. It is generally more efficient to modify
    materials already bound to prims.

    Args:
        materials: The list of materials to sample from and bind to the input prims. The materials can be prim paths,
            MDL paths or a ``ReplicatorItem``.
        seed: Seed to use as initialization for the pseudo-random number generator. If not specified, the global seed
            will be used.
        max_cached_materials: Maximum number of materials allowed to remain in the scene when not attached to a prim.
            A larger value allows more materials to remain in the scene, reducing the number of materials that need to
            be re-created each call at the expense of memory usage. Only applies to materials created from MDL paths
            specified in `materials`. The default value of 0 removes all cached materials at the end of each call.
        input_prims: The prims to be modified. If using ``with`` syntax, this argument can be omitted.
        name (optional): A name for the graph node.

    Example:
        >>> import omni.replicator.core as rep
        >>> mats = rep.create.material_omnipbr(diffuse=rep.distribution.uniform((0,0,0), (1,1,1)), count=100)
        >>> spheres = rep.create.sphere(
        ...     scale=0.2,
        ...     position=rep.distribution.uniform((-100,-100,-100), (100,100,100)),
        ...     count=100
        ... )
        >>> with spheres:
        ...     rep.randomizer.materials(mats)
        omni.replicator.core.randomizer.materials
    """
    node = create_node(
        "omni.replicator.core.OgnSampleMaterial", maxCachedMaterials=max_cached_materials, seed=seed, node_name=name
    )

    # WAR for multiple prims limitations
    if input_prims:
        set_target_prims(node, "inputs:prims", input_prims)
    if materials:
        if isinstance(materials, ReplicatorItem):
            # Check if valid distribution
            if materials.node.get_attribute_exists("outputs:samples"):
                if materials.node.get_attribute("outputs:samples").get_type_name() == "targets":
                    input_name = "materialPrim"
                    og.AttributeValueHelper(node.get_attribute("inputs:useMaterialPrim")).set(True, update_usd=True)
                else:
                    input_name = "materialPaths"
                _setup_random_attribute(
                    write_node=node, attribute_value=materials, prim_path=input_prims, input_name=input_name
                )
            else:
                og.AttributeValueHelper(node.get_attribute("inputs:useMaterialPrim")).set(True, update_usd=True)
                _connect_prims(node, "inputs:materialPrim", materials)
        elif isinstance(materials, List) and all(isinstance(m, ReplicatorItem) for m in materials):
            # Get paths from ReplicatorItem materials
            mat_paths = []
            for mat in materials:
                if mat.node.get_attribute_exists("outputs:prims"):
                    mat_paths.extend(mat.node.get_attribute("outputs:prims").get())

            materials = distribution.choice(mat_paths)
            _setup_random_attribute(
                write_node=node, attribute_value=materials, prim_path=input_prims, input_name="materialPrim"
            )
            og.AttributeValueHelper(node.get_attribute("inputs:useMaterialPrim")).set(True, update_usd=True)
        else:
            og.AttributeValueHelper(node.get_attribute("inputs:materialPaths")).set(materials, update_usd=True)

    return node


@ReplicatorWrapper
def instantiate(
    paths: Union[ReplicatorItem, List[Union[str, Sdf.Path, usdrt.Sdf.Path, Usd.Prim, ReplicatorItem]]],
    size: Union[ReplicatorItem, int],
    weights: List[float] = None,
    mode: str = "scene_instance",
    with_replacements=True,
    seed: int = None,
    name: str = None,
    use_cache: bool = True,
    semantics: List[Tuple[str, str]] = None,
) -> ReplicatorItem:
    """Sample ``size`` number of prims from the paths provided.

    Args:
        paths: The list of USD paths pointing to the assets to sample from.
        size: The number of samples to sample. NOTE: if the paths is a ``ReplicatorItem``, size will be ignored.
        weights: The weights to use for sampling. If provided, the length of ``weights`` must match the length of
            ``paths``. If omitted, uniform sampling will be used. NOTE: if the paths is a ``ReplicatorItem``, weights
            will be ignored.
        mode: The instantiation mode. Choose from [scene_instance, point_instance, reference]. Defaults to
            scene_instance. Scene Instance creates a prototype in the cache, and new instances reference the prototype.
            Point Instancesare best suited for situations requiring a very large number of samples, but only pose
            attributes can be modified per instance. Reference mode is used for asset references that need to be
            modified (WARNING: this mode has known material loading issue.)
        with_replacements: When ``False``, avoids duplicates when sampling. Default ``True``. NOTE: if the paths is a
            ReplicatorItem, with_replacements will be ignored.
        seed: Seed to use as initialization for the pseudo-random number generator. If not specified, the global seed
            will be used. NOTE: if the paths is a ``ReplicatorItem``, seed will be ignored.
        name: Optionally prepend a name to the population.
        use_cache: If ``True``, cache the assets in ``paths`` to speed up randomization. Set to False
            if the size of the population is too large to be cached. Default: True.
        semantics: List of semantic type-label pairs.

    Example:
        >>> import omni.replicator.core as rep
        >>> usds = rep.utils.get_usd_files(rep.example.ASSETS_DIR)
        >>> with rep.randomizer.instantiate(usds, size=100):
        ...     rep.modify.pose(position=rep.distribution.uniform((-50,-50,-50),(50,50,50)))
        omni.replicator.core.modify.pose
    """
    node = create_node(
        "omni.replicator.core.OgnSamplePopulation",
        mode=mode,
        populationName=name,
        useCache=use_cache,
        node_name=name,
        semantics=[",".join(s) for s in semantics] if semantics else [],
    )
    if isinstance(paths, str):
        paths = [paths]

    if isinstance(paths, list) and len(paths) == 0:
        raise ValueError(f"No valid usd files provided: {paths}")

    if not isinstance(paths, ReplicatorItem) or (
        isinstance(paths, ReplicatorItem) and paths.node.get_attribute_exists("outputs:prims")
    ):
        paths = distribution.choice(
            choices=paths, num_samples=size, weights=weights, seed=seed, with_replacements=with_replacements
        )

    if isinstance(paths, ReplicatorItem) and paths.node.get_attribute_exists("outputs:samples"):
        if paths.node.get_attribute("outputs:samples").get_resolved_type().get_role_name() == "target":
            paths.node.get_attribute("outputs:samples").connect(node.get_attribute("inputs:prims"), True)
        else:
            paths.node.get_attribute("outputs:samples").connect(node.get_attribute("inputs:paths"), True)
    else:
        raise ValueError(
            "Received invalid value for `paths`. Expected a list of paths or a ReplicatorItem with prims or samples "
            "output."
        )

    return node


@ReplicatorWrapper
def rotation(
    min_angle: Tuple[float, float, float] = (-180.0, -180.0, -180.0),
    max_angle: Tuple[float, float, float] = (180.0, 180.0, 180.0),
    seed: int = None,
    input_prims: Union[ReplicatorItem, List[str]] = None,
) -> ReplicatorItem:
    """Randomize the rotation of the input prims

    This randomizer produces a truly uniformly distributed rotations to the input prims. In contrast, rotations are not
    truly uniformly distributed when simply sampling uniformly for each rotation axis.

    Args:
        min_angle: Minimum value for Euler angles in XYZ form (degrees)
        max_angle: Maximum value for Euler angles in XYZ form (degrees)
        seed: Seed to use as initialization for the pseudo-random number generator. If not specified, the global seed
            will be used.
        input_prims: The prims to be modified. If using ``with`` syntax, this argument can be omitted.

    Example:
        >>> import omni.replicator.core as rep
        >>> cubes = rep.create.cube(position=rep.distribution.uniform((-100,-100,-100),(100,100,100)), count=100)
        >>> with cubes:
        ...     rep.randomizer.rotation()
        omni.replicator.core.randomizer.rotation
    """
    node = create_node("omni.replicator.core.OgnSampleRotation", minAngle=min_angle, maxAngle=max_angle, seed=seed)

    # WAR for multiple prims limitations
    if input_prims:
        set_target_prims(node, "inputs:prims", input_prims)
    return node


@ReplicatorWrapper
def texture(
    textures: Union[ReplicatorItem, List[str]],
    texture_scale: Union[ReplicatorItem, List[Tuple[float, float]]] = None,
    texture_rotate: Union[ReplicatorItem, List[int]] = None,
    per_sub_mesh: bool = False,
    project_uvw: bool = False,
    seed: int = None,
    input_prims: Union[ReplicatorItem, List[str]] = None,
) -> ReplicatorItem:
    """Randomize texture
    Creates and binds an OmniPBR material to each prim in input_prims and modifies textures.

    Args:
        textures: List of texture paths, or a ``ReplicatorItem`` that outputs a list of texture paths. If a list of
            texture paths is provided, they will be sampled uniformly using the global seed.
        texture_scale: List of texture scales in (X, Y) represented by positive floats. Larger values will make the
            texture appear smaller on the asset.
        texture_rotate: Rotation in degrees of the texture.
        per_sub_mesh: If ``True``, bind a material to each mesh and geom_subset. If ``False``, a material is bound only
            to the specified prim.
        project_uvw: When ``True``, UV coordinates will be generated by projecting them from a coordinate system.
        seed: Seed to use as initialization for the pseudo-random number generator. If not specified, the global seed
            will be used.
        input_prims: List of input_prims. If constructing using ``with`` structure, set to None to bind input_prims
            to the current context.

    Example:
        >>> import omni.replicator.core as rep
        >>> with rep.create.cone(position=rep.distribution.uniform((-100,-100,-100),(100,100,100)), count=100):
        ...     rep.randomizer.texture(textures=rep.example.TEXTURES, texture_scale=[(0.5, 0.5)], texture_rotate=[45])
        omni.replicator.core.randomizer.texture
    """
    mode = "meshes" if per_sub_mesh else "prims"
    node = create_node("omni.replicator.core.OgnSampleOmniPBR", mode=mode, projectUVW=project_uvw, seed=seed)

    if not isinstance(textures, ReplicatorItem):
        _validate_paths(textures)
        textures = distribution.choice(textures)

    _setup_random_attribute(write_node=node, attribute_value=textures, prim_path=input_prims, mode=mode)
    textures.node.get_attribute("outputs:samples").connect(node.get_attribute("inputs:diffuseTexture"), True)

    if texture_scale:
        if not isinstance(texture_scale, ReplicatorItem):
            texture_scale = distribution.uniform(texture_scale, texture_scale)
        _setup_random_attribute(
            write_node=node, attribute_value=texture_scale, prim_path=input_prims, input_name="textureScale"
        )
        # texture_scale.node.get_attribute("outputs:samples").connect(node.get_attribute("inputs:textureScale"), True)

    if texture_rotate:
        if not isinstance(texture_rotate, ReplicatorItem):
            texture_rotate = distribution.uniform(texture_rotate, texture_rotate)
        _setup_random_attribute(
            write_node=node, attribute_value=texture_rotate, prim_path=input_prims, input_name="textureRotate"
        )
        # texture_rotate.node.get_attribute("outputs:samples").connect(node.get_attribute("inputs:textureRotate"), True)

    # WAR for multiple prims limitations
    if input_prims:
        set_target_prims(node, "inputs:prims", input_prims)
    return node


@ReplicatorWrapper
def color(
    colors: Union[ReplicatorItem, List[Tuple[float]]],
    per_sub_mesh: bool = False,
    seed: int = None,
    input_prims: Union[ReplicatorItem, List[str]] = None,
) -> ReplicatorItem:
    """Randomize colors
    Creates and binds an OmniPBR material to each prim in input_prims and randomizes colors.

    Args:
        colors: List of colors, or a ``ReplicatorItem`` that outputs a list of colors. If supplied as a list, a `choice`
            sampler is automatically created to sample from the supplied color list.
        per_sub_mesh: If ``True``, bind a color to each mesh and geom_subset. If ``False``, a color is bound only to the
            specified prim.
        seed: If colors is specified as a list, optionally provide seed for color sampler. Unused if colors is a
            ``ReplicatorItem``.
        input_prims: List of input_prims. If constructing using ``with`` structure, set to None to bind ``input_prims``
            to the current context.

    Example:
        >>> import omni.replicator.core as rep
        >>> cones = rep.create.cone(position=rep.distribution.uniform((-100,-100,-100),(100,100,100)), count=100)
        >>> with cones:
        ...     rep.randomizer.color(colors=rep.distribution.uniform((0, 0, 0), (1, 1, 1)))
        omni.replicator.core.randomizer.color
    """
    mode = "meshes" if per_sub_mesh else "prims"
    node = create_node("omni.replicator.core.OgnSampleOmniPBR", mode=mode)

    if isinstance(colors, (list, tuple)):
        colors = distribution.choice(colors, seed=seed)

    if isinstance(colors, ReplicatorItem):
        _setup_random_attribute(write_node=node, attribute_value=colors, prim_path=input_prims)
        colors.node.get_attribute("outputs:samples").connect(node.get_attribute("inputs:diffuse"), True)

    # WAR for multiple prims limitations
    if input_prims:
        set_target_prims(node, "inputs:prims", input_prims)
    return node
