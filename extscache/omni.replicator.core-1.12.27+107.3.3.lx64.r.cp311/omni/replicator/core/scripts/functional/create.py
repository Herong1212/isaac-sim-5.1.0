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

from typing import Dict, List, Optional, Tuple, Union

import pxr
import usdrt

from . import create_batch


def scope(
    name: str = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
) -> pxr.Usd.Prim:
    """Create a Scope

    Args:
        name: Name of the object.
        parent: Optional parent prim path. The scope will be created as a child of this prim.

    Example:
        >>> import omni.replicator.core as rep
        >>> scope = rep.functional.create.scope()
    """
    return create_batch.scope(
        name=name,
        parent=parent,
        count=1,
    )[0]


def clone(
    path: Union[str, pxr.Sdf.Path, usdrt.Sdf.Path],
    position: Union[float, Tuple[float]] = None,
    scale: Union[float, Tuple[float]] = None,
    rotation: Union[float, Tuple[float]] = None,
    look_at: Union[
        str,
        pxr.Sdf.Path,
        usdrt.Sdf.Path,
        Tuple[float, float, float],
        List[Union[str, pxr.Sdf.Path, usdrt.Sdf.Path]],
    ] = None,
    look_at_up_axis: Union[Tuple[float]] = None,
    pivot: Union[Tuple[float, float, float], List[Tuple[float, float, float]], pxr.Gf.Vec3d] = None,
    relative_to: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    name: str = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
) -> List[pxr.Usd.Prim]:
    """Create a Clone

    Args:
        path: Path to the prim to clone.
        position: XYZ coordinates in world space. If a single value is provided, all axes will be set to that value.
        scale: Scaling factors for XYZ axes. If a single value is provided, all axes will be set to that value.
        rotation: Euler angles in degrees in XYZ order. If a single value is provided, all axes will be set to that
            value.
        look_at: Look-at target, specified either as a ``ReplicatorItem``, a prim path, or world coordinates.
                If multiple prims are set, the target point will be the mean of their positions.
        look_at_up_axis: Look-at up axis of the created prim.
        pivot: Pivot point of the created prim normalized in the range [-1, 1] for each axis.
        relative_to: If provided, position will be relative to this prim instead of world space.
        name: Name of the object.
        parent: Optional parent prim path. The clone will be created as a child of this prim.


    Example:
        >>> import omni.replicator.core as rep
        >>> original = rep.functional.create.sphere()
        >>> clone = rep.functional.create.clone(
        ...     path="/Sphere",
        ... )
    """
    return create_batch.clone(
        path=path,
        position=position,
        scale=scale,
        rotation=rotation,
        look_at=look_at,
        look_at_up_axis=look_at_up_axis,
        pivot=pivot,
        relative_to=relative_to,
        name=name,
        parent=parent,
    )[0]


def xform(
    position: Union[float, Tuple[float]] = None,
    scale: Union[float, Tuple[float]] = None,
    rotation: Union[float, Tuple[float]] = None,
    look_at: Union[
        str,
        pxr.Sdf.Path,
        usdrt.Sdf.Path,
        Tuple[float, float, float],
        List[Union[str, pxr.Sdf.Path, usdrt.Sdf.Path]],
    ] = None,
    look_at_up_axis: Union[Tuple[float]] = None,
    pivot: Union[Tuple[float, float, float], List[Tuple[float, float, float]], pxr.Gf.Vec3d] = None,
    relative_to: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    semantics: Union[Dict[str, Union[List, str]], List[Tuple[str, str]]] = None,
    visible: bool = True,
    name: str = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    material: Union[pxr.Usd.Prim, usdrt.Usd.Prim] = None,
) -> List[pxr.Usd.Prim]:
    """Create a Xform

    Args:
        position: XYZ coordinates in world space. If a single value is provided, all axes will be set to that value.
        scale: Scaling factors for XYZ axes. If a single value is provided, all axes will be set to that value.
        rotation: Euler angles in degrees in XYZ order. If a single value is provided, all axes will be set to that
            value.
        look_at: Look-at target, specified either as a ``ReplicatorItem``, a prim path, or world coordinates.
                If multiple prims are set, the target point will be the mean of their positions.
        look_at_up_axis: Look-at up axis of the created prim.
        pivot: Pivot point of the created prim normalized in the range [-1, 1] for each axis.
        relative_to: If provided, position will be relative to this prim instead of world space.
        semantics: Dictionary specifying semantic type and values. Legacy lists of tuples are also accepted but will be converted to dictionaries.
        visible: If ``False``, the prim will be invisible. This is often useful when creating prims to use as bounds
            with other randomizers.
        name: Name of the object.
        parent: Optional parent prim path. The xform will be created as a child of this prim.
        material: Material to bind to the created prim.

    Example:
        >>> import omni.replicator.core as rep
        >>> rng = rep.rng.ReplicatorRNG()
        >>> xform = rep.functional.create.xform(
        ...     position=rng.generator.uniform((0,0,0), (100, 100, 100)),
        ...     semantics={"class": "thing"},
        ... )
    """
    return create_batch.xform(
        name=name,
        parent=parent,
        position=position,
        rotation=rotation,
        scale=scale,
        look_at=look_at,
        look_at_up_axis=look_at_up_axis,
        pivot=pivot,
        relative_to=relative_to,
        semantics=semantics,
        visible=visible,
        material=material,
        count=1,
    )[0]


def camera(
    position: Union[float, Tuple[float]] = None,
    scale: Union[float, Tuple[float]] = None,
    rotation: Union[float, Tuple[float]] = None,
    look_at: Union[
        str,
        pxr.Sdf.Path,
        usdrt.Sdf.Path,
        Tuple[float, float, float],
        List[Union[str, pxr.Sdf.Path, usdrt.Sdf.Path]],
    ] = None,
    look_at_up_axis: Union[Tuple[float]] = None,
    relative_to: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    focal_length: float = 24.0,
    focus_distance: float = 400.0,
    f_stop: float = 0.0,
    horizontal_aperture: float = 20.955,
    horizontal_aperture_offset: float = 0.0,
    vertical_aperture_offset: float = 0.0,
    clipping_range: Tuple[float, float] = (1.0, 1000000.0),
    projection_type: str = "pinhole",
    fisheye_nominal_width: float = 1936.0,
    fisheye_nominal_height: float = 1216.0,
    fisheye_optical_centre_x: float = 970.94244,
    fisheye_optical_centre_y: float = 600.37482,
    openCV_focal_x: float = 731.78788,
    openCV_focal_y: float = 731.78789,
    fisheye_max_fov: float = 200.0,
    fisheye_polynomial_a: float = 0.0,
    fisheye_polynomial_b: float = 0.00245,
    fisheye_polynomial_c: float = 0.0,
    fisheye_polynomial_d: float = 0.0,
    fisheye_polynomial_e: float = 0.0,
    fisheye_polynomial_f: float = 0.0,
    fisheye_p0: float = -0.00037,
    fisheye_p1: float = -0.00074,
    fisheye_s0: float = -0.00058,
    fisheye_s1: float = -0.00022,
    fisheye_s2: float = 0.00019,
    fisheye_s3: float = -0.0002,
    cross_camera_reference_name: str = None,
    name: str = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
) -> pxr.Usd.Prim:
    """Create a Camera

    Args:
        position: XYZ coordinates in world space. If a single value is provided, all axes will be set to that value.
        scale: Scaling factors for XYZ axes. If a single value is provided, all axes will be set to that value.
        rotation: Euler angles in degrees in XYZ order. If a single value is provided, all axes will be set to that
            value.
        look_at: Look-at target, specified either as a ``ReplicatorItem``, a prim path, or world coordinates.
                If multiple prims are set, the target point will be the mean of their positions.
        look_at_up_axis: Look-at up axis of the created prim.
        relative_to: If provided, position will be relative to this prim instead of world space.
        focal_length: Focal length of the camera.
        focus_distance: Distance to the focus plane.
        f_stop: F-stop of the camera.
        horizontal_aperture: Horizontal aperture of the camera.
        horizontal_aperture_offset: Horizontal aperture offset of the camera.
        vertical_aperture_offset: Vertical aperture offset of the camera.
        clipping_range: Clipping range of the camera.
        projection_type: Projection type of the camera.
        fisheye_nominal_width: Nominal width of the fisheye camera.
        fisheye_nominal_height: Nominal height of the fisheye camera.
        fisheye_optical_centre_x: Optical centre x of the fisheye camera.
        fisheye_optical_centre_y: Optical centre y of the fisheye camera.
        openCV_focal_x: Focal x of the openCV camera.
        openCV_focal_y: Focal y of the openCV camera.
        fisheye_max_fov: Maximum field of view of the fisheye camera.
        fisheye_polynomial_a: Polynomial coefficient a of the fisheye camera.
        fisheye_polynomial_b: Polynomial coefficient b of the fisheye camera.
        fisheye_polynomial_c: Polynomial coefficient c of the fisheye camera.
        fisheye_polynomial_d: Polynomial coefficient d of the fisheye camera.
        fisheye_polynomial_e: Polynomial coefficient e of the fisheye camera.
        fisheye_polynomial_f: Polynomial coefficient f of the fisheye camera.
        fisheye_p0: Polynomial coefficient p0 of the fisheye camera.
        fisheye_p1: Polynomial coefficient p1 of the fisheye camera.
        fisheye_s0: Polynomial coefficient s0 of the fisheye camera.
        fisheye_s1: Polynomial coefficient s1 of the fisheye camera.
        fisheye_s2: Polynomial coefficient s2 of the fisheye camera.
        fisheye_s3: Polynomial coefficient s3 of the fisheye camera.
        cross_camera_reference_name: Name of the cross camera reference.
        name: Name of the object.
        parent: Optional parent prim path. The camera will be created as a child of this prim.


    Example:
        >>> import omni.replicator.core as rep
        >>> rng = rep.rng.ReplicatorRNG()
        >>> camera = rep.functional.create.camera(
        ...     position=rng.generator.uniform((0,0,0), (100, 100, 100)),
        ... )
    """
    return create_batch.camera(
        name=name,
        parent=parent,
        position=position,
        rotation=rotation,
        scale=scale,
        look_at=look_at,
        look_at_up_axis=look_at_up_axis,
        relative_to=relative_to,
        focal_length=focal_length,
        focus_distance=focus_distance,
        f_stop=f_stop,
        horizontal_aperture=horizontal_aperture,
        horizontal_aperture_offset=horizontal_aperture_offset,
        vertical_aperture_offset=vertical_aperture_offset,
        clipping_range=clipping_range,
        projection_type=projection_type,
        fisheye_nominal_width=fisheye_nominal_width,
        fisheye_nominal_height=fisheye_nominal_height,
        fisheye_optical_centre_x=fisheye_optical_centre_x,
        fisheye_optical_centre_y=fisheye_optical_centre_y,
        openCV_focal_x=openCV_focal_x,
        openCV_focal_y=openCV_focal_y,
        fisheye_max_fov=fisheye_max_fov,
        fisheye_polynomial_a=fisheye_polynomial_a,
        fisheye_polynomial_b=fisheye_polynomial_b,
        fisheye_polynomial_c=fisheye_polynomial_c,
        fisheye_polynomial_d=fisheye_polynomial_d,
        fisheye_polynomial_e=fisheye_polynomial_e,
        fisheye_polynomial_f=fisheye_polynomial_f,
        fisheye_p0=fisheye_p0,
        fisheye_p1=fisheye_p1,
        fisheye_s0=fisheye_s0,
        fisheye_s1=fisheye_s1,
        fisheye_s2=fisheye_s2,
        fisheye_s3=fisheye_s3,
        cross_camera_reference_name=cross_camera_reference_name,
    )[0]


def reference(
    usd_path: Union[str, List[str]] = None,
    prim_path: Union[str, List[str]] = None,
    position: Union[float, Tuple[float]] = None,
    scale: Union[float, Tuple[float]] = None,
    rotation: Union[float, Tuple[float]] = None,
    look_at: Union[
        str,
        pxr.Sdf.Path,
        usdrt.Sdf.Path,
        Tuple[float, float, float],
        List[Union[str, pxr.Sdf.Path, usdrt.Sdf.Path]],
    ] = None,
    look_at_up_axis: Union[Tuple[float]] = None,
    pivot: Union[Tuple[float, float, float], List[Tuple[float, float, float]], pxr.Gf.Vec3d] = None,
    relative_to: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    semantics: Union[Dict[str, Union[List, str]], List[Tuple[str, str]]] = None,
    visible: bool = True,
    name: str = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
) -> pxr.Usd.Prim:
    """Create a Reference

    Args:
        usd_path: USD path of the prim to reference.
        prim_path: Prim path of the prim to reference.
        position: XYZ coordinates in world space. If a single value is provided, all axes will be set to that value.
        scale: Scaling factors for XYZ axes. If a single value is provided, all axes will be set to that value.
        rotation: Euler angles in degrees in XYZ order. If a single value is provided, all axes will be set to that
            value.
        look_at: Look-at target, specified either as a ``ReplicatorItem``, a prim path, or world coordinates.
                If multiple prims are set, the target point will be the mean of their positions.
        look_at_up_axis: Look-at up axis of the created prim.
        pivot: Pivot point of the created prim normalized in the range [-1, 1] for each axis.
        relative_to: If provided, position will be relative to this prim instead of world space.
        semantics: Dictionary specifying semantic type and values. Legacy lists of tuples are also accepted but will be converted to dictionaries.
        visible: If ``False``, the prim will be invisible. This is often useful when creating prims to use as bounds
            with other randomizers.
        name: Name of the object.
        parent: Optional parent prim path. The reference will be created as a child of this prim.


    Example:
        >>> import omni.replicator.core as rep
        >>> rng = rep.rng.ReplicatorRNG()
        >>> reference_internal = rep.functional.create.reference(
        ...     prim_path="/World/Looks/Red",
        ...     position=rng.generator.uniform((0,0,0), (100, 100, 100)),
        ...     semantics={"class": "internal_reference"},
        ... )
        >>> reference_external = rep.functional.create.reference(
        ...     usd_path="/path/to/external/file.usd",
        ...     position=rng.generator.uniform((0,0,0), (100, 100, 100)),
        ...     semantics={"class": "external_reference"},
        ... )
    """
    return create_batch.reference(
        name=name,
        parent=parent,
        usd_path=usd_path,
        prim_path=prim_path,
        position=position,
        rotation=rotation,
        scale=scale,
        look_at=look_at,
        look_at_up_axis=look_at_up_axis,
        pivot=pivot,
        relative_to=relative_to,
        semantics=semantics,
        visible=visible,
        count=1,
    )[0]


def plane(
    position: Union[float, Tuple[float]] = None,
    scale: Union[float, Tuple[float]] = None,
    rotation: Union[float, Tuple[float]] = None,
    look_at: Union[
        str,
        pxr.Sdf.Path,
        usdrt.Sdf.Path,
        Tuple[float, float, float],
        List[Union[str, pxr.Sdf.Path, usdrt.Sdf.Path]],
    ] = None,
    look_at_up_axis: Union[Tuple[float]] = None,
    pivot: Union[Tuple[float, float, float], List[Tuple[float, float, float]], pxr.Gf.Vec3d] = None,
    relative_to: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    semantics: Union[Dict[str, Union[List, str]], List[Tuple[str, str]]] = None,
    visible: bool = True,
    name: str = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    material: Union[pxr.Usd.Prim, usdrt.Usd.Prim] = None,
) -> pxr.Usd.Prim:
    """Create a Plane

    Args:
        position: XYZ coordinates in world space. If a single value is provided, all axes will be set to that value.
        scale: Scaling factors for XYZ axes. If a single value is provided, all axes will be set to that value.
        rotation: Euler angles in degrees in XYZ order. If a single value is provided, all axes will be set to that
            value.
        look_at: Look-at target, specified either as a ``ReplicatorItem``, a prim path, or world coordinates.
                If multiple prims are set, the target point will be the mean of their positions.
        look_at_up_axis: Look-at up axis of the created prim.
        pivot: Pivot point of the created prim normalized in the range [-1, 1] for each axis.
        relative_to: If provided, position will be relative to this prim instead of world space.
        semantics: Dictionary specifying semantic type and values. Legacy lists of tuples are also accepted but will be converted to dictionaries.
        visible: If ``False``, the prim will be invisible. This is often useful when creating prims to use as bounds
            with other randomizers.
        name: Name of the object.
        parent: Optional parent prim path. The plane will be created as a child of this prim.
        material: Material to bind to the created prim.

    Example:
        >>> import omni.replicator.core as rep
        >>> rng = rep.rng.ReplicatorRNG()
        >>> plane = rep.functional.create.plane(
        ...     position=rng.generator.uniform((0,0,0), (100, 100, 100)),
        ...     semantics={"class": "plane"},
        ... )
    """
    return create_batch.plane(
        name=name,
        parent=parent,
        position=position,
        rotation=rotation,
        scale=scale,
        look_at=look_at,
        look_at_up_axis=look_at_up_axis,
        pivot=pivot,
        relative_to=relative_to,
        semantics=semantics,
        visible=visible,
        material=material,
        count=1,
    )[0]


def sphere(
    position: Union[float, Tuple[float]] = None,
    scale: Union[float, Tuple[float]] = None,
    rotation: Union[float, Tuple[float]] = None,
    look_at: Union[
        str,
        pxr.Sdf.Path,
        usdrt.Sdf.Path,
        Tuple[float, float, float],
        List[Union[str, pxr.Sdf.Path, usdrt.Sdf.Path]],
    ] = None,
    look_at_up_axis: Union[Tuple[float]] = None,
    pivot: Union[Tuple[float, float, float], List[Tuple[float, float, float]], pxr.Gf.Vec3d] = None,
    relative_to: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    semantics: Union[Dict[str, Union[List, str]], List[Tuple[str, str]]] = None,
    visible: bool = True,
    as_mesh: bool = True,
    name: str = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    material: Union[pxr.Usd.Prim, usdrt.Usd.Prim] = None,
) -> pxr.Usd.Prim:
    """Create a Sphere

    Args:
        position: XYZ coordinates in world space. If a single value is provided, all axes will be set to that value.
        scale: Scaling factors for XYZ axes. If a single value is provided, all axes will be set to that value.
        rotation: Euler angles in degrees in XYZ order. If a single value is provided, all axes will be set to that
            value.
        look_at: Look-at target, specified either as a ``ReplicatorItem``, a prim path, or world coordinates.
                If multiple prims are set, the target point will be the mean of their positions.
        look_at_up_axis: Look-at up axis of the created prim.
        pivot: Pivot point of the created prim normalized in the range [-1, 1] for each axis.
        relative_to: If provided, position will be relative to this prim instead of world space.
        semantics: Dictionary specifying semantic type and values. Legacy lists of tuples are also accepted but will be converted to dictionaries.
        visible: If ``False``, the prim will be invisible. This is often useful when creating prims to use as bounds
            with other randomizers.
        as_mesh: If True, creates a mesh sphere. If False, creates a native USD sphere
        name: Name of the object.
        parent: Optional parent prim path. The sphere will be created as a child of this prim.
        material: Material to bind to the created prim.

    Example:
        >>> import omni.replicator.core as rep
        >>> rng = rep.rng.ReplicatorRNG()
        >>> sphere = rep.functional.create.sphere(
        ...     position=rng.generator.uniform((0,0,0), (100, 100, 100)),
        ...     semantics={"class": "sphere"},
        ... )
    """
    return create_batch.sphere(
        name=name,
        parent=parent,
        position=position,
        rotation=rotation,
        scale=scale,
        look_at=look_at,
        look_at_up_axis=look_at_up_axis,
        pivot=pivot,
        relative_to=relative_to,
        semantics=semantics,
        visible=visible,
        as_mesh=as_mesh,
        material=material,
        count=1,
    )[0]


def cube(
    position: Union[float, Tuple[float]] = None,
    scale: Union[float, Tuple[float]] = None,
    rotation: Union[float, Tuple[float]] = None,
    look_at: Union[
        str,
        pxr.Sdf.Path,
        usdrt.Sdf.Path,
        Tuple[float, float, float],
        List[Union[str, pxr.Sdf.Path, usdrt.Sdf.Path]],
    ] = None,
    look_at_up_axis: Union[Tuple[float]] = None,
    pivot: Union[Tuple[float, float, float], List[Tuple[float, float, float]], pxr.Gf.Vec3d] = None,
    relative_to: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    semantics: Union[Dict[str, Union[List, str]], List[Tuple[str, str]]] = None,
    visible: bool = True,
    as_mesh: bool = True,
    name: str = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    material: Union[pxr.Usd.Prim, usdrt.Usd.Prim] = None,
) -> pxr.Usd.Prim:
    """Create a Cube

    Args:
        position: XYZ coordinates in world space. If a single value is provided, all axes will be set to that value.
        scale: Scaling factors for XYZ axes. If a single value is provided, all axes will be set to that value.
        rotation: Euler angles in degrees in XYZ order. If a single value is provided, all axes will be set to that
            value.
        look_at: Look-at target, specified either as a ``ReplicatorItem``, a prim path, or world coordinates.
                If multiple prims are set, the target point will be the mean of their positions.
        look_at_up_axis: Look-at up axis of the created prim.
        pivot: Pivot point of the created prim normalized in the range [-1, 1] for each axis.
        relative_to: If provided, position will be relative to this prim instead of world space.
        semantics: Dictionary specifying semantic type and values. Legacy lists of tuples are also accepted but will be converted to dictionaries.
        visible: If ``False``, the prim will be invisible. This is often useful when creating prims to use as bounds
            with other randomizers.
        as_mesh: If True, creates a mesh cube. If False, creates a native USD cube
        name: Name of the object.
        parent: Optional parent prim path. The cube will be created as a child of this prim.
        material: Material to bind to the created prim.

    Example:
        >>> import omni.replicator.core as rep
        >>> rng = rep.rng.ReplicatorRNG()
        >>> cube = rep.functional.create.cube(
        ...     position=rng.generator.uniform((0,0,0), (100, 100, 100)),
        ...     semantics={"class": "cube"},
        ... )
    """
    return create_batch.cube(
        name=name,
        parent=parent,
        position=position,
        rotation=rotation,
        scale=scale,
        look_at=look_at,
        look_at_up_axis=look_at_up_axis,
        pivot=pivot,
        relative_to=relative_to,
        semantics=semantics,
        visible=visible,
        as_mesh=as_mesh,
        material=material,
        count=1,
    )[0]


def disk(
    position: Union[float, Tuple[float]] = None,
    scale: Union[float, Tuple[float]] = None,
    rotation: Union[float, Tuple[float]] = None,
    look_at: Union[
        str,
        pxr.Sdf.Path,
        usdrt.Sdf.Path,
        Tuple[float, float, float],
        List[Union[str, pxr.Sdf.Path, usdrt.Sdf.Path]],
    ] = None,
    look_at_up_axis: Union[Tuple[float]] = None,
    pivot: Union[Tuple[float, float, float], List[Tuple[float, float, float]], pxr.Gf.Vec3d] = None,
    relative_to: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    semantics: Union[Dict[str, Union[List, str]], List[Tuple[str, str]]] = None,
    visible: bool = True,
    name: str = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    material: Union[pxr.Usd.Prim, usdrt.Usd.Prim] = None,
) -> pxr.Usd.Prim:
    """Create a Disk

    Args:
        position: XYZ coordinates in world space. If a single value is provided, all axes will be set to that value.
        scale: Scaling factors for XYZ axes. If a single value is provided, all axes will be set to that value.
        rotation: Euler angles in degrees in XYZ order. If a single value is provided, all axes will be set to that
            value.
        look_at: Look-at target, specified either as a ``ReplicatorItem``, a prim path, or world coordinates.
                If multiple prims are set, the target point will be the mean of their positions.
        look_at_up_axis: Look-at up axis of the created prim.
        pivot: Pivot point of the created prim normalized in the range [-1, 1] for each axis.
        relative_to: If provided, position will be relative to this prim instead of world space.
        semantics: Dictionary specifying semantic type and values. Legacy lists of tuples are also accepted but will be converted to dictionaries.
        visible: If ``False``, the prim will be invisible. This is often useful when creating prims to use as bounds
            with other randomizers.
        name: Name of the object.
        parent: Optional parent prim path. The disk will be created as a child of this prim.
        material: Material to bind to the created prim.

    Example:
        >>> import omni.replicator.core as rep
        >>> rng = rep.rng.ReplicatorRNG()
        >>> disk = rep.functional.create.disk(
        ...     position=rng.generator.uniform((0,0,0), (100, 100, 100)),
        ...     semantics={"class": "disk"},
        ... )
    """
    return create_batch.disk(
        name=name,
        parent=parent,
        position=position,
        rotation=rotation,
        scale=scale,
        look_at=look_at,
        look_at_up_axis=look_at_up_axis,
        pivot=pivot,
        relative_to=relative_to,
        semantics=semantics,
        visible=visible,
        material=material,
        count=1,
    )[0]


def torus(
    position: Union[float, Tuple[float]] = None,
    scale: Union[float, Tuple[float]] = None,
    rotation: Union[float, Tuple[float]] = None,
    look_at: Union[
        str,
        pxr.Sdf.Path,
        usdrt.Sdf.Path,
        Tuple[float, float, float],
        List[Union[str, pxr.Sdf.Path, usdrt.Sdf.Path]],
    ] = None,
    look_at_up_axis: Union[Tuple[float]] = None,
    pivot: Union[Tuple[float, float, float], List[Tuple[float, float, float]], pxr.Gf.Vec3d] = None,
    relative_to: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    semantics: Union[Dict[str, Union[List, str]], List[Tuple[str, str]]] = None,
    visible: bool = True,
    name: str = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    material: Union[pxr.Usd.Prim, usdrt.Usd.Prim] = None,
) -> pxr.Usd.Prim:
    """Create a Torus

    Args:
        position: XYZ coordinates in world space. If a single value is provided, all axes will be set to that value.
        scale: Scaling factors for XYZ axes. If a single value is provided, all axes will be set to that value.
        rotation: Euler angles in degrees in XYZ order. If a single value is provided, all axes will be set to that
            value.
        look_at: Look-at target, specified either as a ``ReplicatorItem``, a prim path, or world coordinates.
                If multiple prims are set, the target point will be the mean of their positions.
        look_at_up_axis: Look-at up axis of the created prim.
        pivot: Pivot point of the created prim normalized in the range [-1, 1] for each axis.
        relative_to: If provided, position will be relative to this prim instead of world space.
        semantics: Dictionary specifying semantic type and values. Legacy lists of tuples are also accepted but will be converted to dictionaries.
        visible: If ``False``, the prim will be invisible. This is often useful when creating prims to use as bounds
            with other randomizers.
        name: Name of the object.
        parent: Optional parent prim path. The torus will be created as a child of this prim.
        material: Material to bind to the created prim.

    Example:
        >>> import omni.replicator.core as rep
        >>> rng = rep.rng.ReplicatorRNG()
        >>> torus = rep.functional.create.torus(
        ...     position=rng.generator.uniform((0,0,0), (100, 100, 100)),
        ...     semantics={"class": "torus"},
        ... )
    """
    return create_batch.torus(
        name=name,
        parent=parent,
        position=position,
        rotation=rotation,
        scale=scale,
        look_at=look_at,
        look_at_up_axis=look_at_up_axis,
        pivot=pivot,
        relative_to=relative_to,
        semantics=semantics,
        visible=visible,
        material=material,
        count=1,
    )[0]


def cylinder(
    position: Union[float, Tuple[float]] = None,
    scale: Union[float, Tuple[float]] = None,
    rotation: Union[float, Tuple[float]] = None,
    look_at: Union[
        str,
        pxr.Sdf.Path,
        usdrt.Sdf.Path,
        Tuple[float, float, float],
        List[Union[str, pxr.Sdf.Path, usdrt.Sdf.Path]],
    ] = None,
    look_at_up_axis: Union[Tuple[float]] = None,
    pivot: Union[Tuple[float, float, float], List[Tuple[float, float, float]], pxr.Gf.Vec3d] = None,
    relative_to: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    semantics: Union[Dict[str, Union[List, str]], List[Tuple[str, str]]] = None,
    as_mesh: bool = True,
    visible: bool = True,
    name: str = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    material: Union[pxr.Usd.Prim, usdrt.Usd.Prim] = None,
) -> pxr.Usd.Prim:
    """Create a Cylinder

    Args:
        position: XYZ coordinates in world space. If a single value is provided, all axes will be set to that value.
        scale: Scaling factors for XYZ axes. If a single value is provided, all axes will be set to that value.
        rotation: Euler angles in degrees in XYZ order. If a single value is provided, all axes will be set to that
            value.
        look_at: Look-at target, specified either as a ``ReplicatorItem``, a prim path, or world coordinates.
                If multiple prims are set, the target point will be the mean of their positions.
        look_at_up_axis: Look-at up axis of the created prim.
        pivot: Pivot point of the created prim normalized in the range [-1, 1] for each axis.
        relative_to: If provided, position will be relative to this prim instead of world space.
        semantics: Dictionary specifying semantic type and values. Legacy lists of tuples are also accepted but will be converted to dictionaries.
        as_mesh: If True, creates a mesh cylinder. If False, creates a native USD cylinder.
        visible: If ``False``, the prim will be invisible. This is often useful when creating prims to use as bounds
            with other randomizers.
        name: Name of the object.
        parent: Optional parent prim path. The cylinder will be created as a child of this prim.
        material: Material to bind to the created prim.

    Example:
        >>> import omni.replicator.core as rep
        >>> rng = rep.rng.ReplicatorRNG()
        >>> cylinder = rep.functional.create.cylinder(
        ...     position=rng.generator.uniform((0,0,0), (100, 100, 100)),
        ...     semantics={"class": "cylinder"},
        ... )
    """
    return create_batch.cylinder(
        name=name,
        parent=parent,
        position=position,
        rotation=rotation,
        scale=scale,
        look_at=look_at,
        look_at_up_axis=look_at_up_axis,
        pivot=pivot,
        relative_to=relative_to,
        semantics=semantics,
        visible=visible,
        as_mesh=as_mesh,
        material=material,
        count=1,
    )[0]


def cone(
    position: Union[float, Tuple[float]] = None,
    scale: Union[float, Tuple[float]] = None,
    rotation: Union[float, Tuple[float]] = None,
    look_at: Union[
        str,
        pxr.Sdf.Path,
        usdrt.Sdf.Path,
        Tuple[float, float, float],
        List[Union[str, pxr.Sdf.Path, usdrt.Sdf.Path]],
    ] = None,
    look_at_up_axis: Union[Tuple[float]] = None,
    pivot: Union[Tuple[float, float, float], List[Tuple[float, float, float]], pxr.Gf.Vec3d] = None,
    relative_to: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    semantics: Union[Dict[str, Union[List, str]], List[Tuple[str, str]]] = None,
    visible: bool = True,
    as_mesh: bool = True,
    name: str = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    material: Union[pxr.Usd.Prim, usdrt.Usd.Prim] = None,
) -> pxr.Usd.Prim:
    """Create a Cone

    Args:
        position: XYZ coordinates in world space. If a single value is provided, all axes will be set to that value.
        scale: Scaling factors for XYZ axes. If a single value is provided, all axes will be set to that value.
        rotation: Euler angles in degrees in XYZ order. If a single value is provided, all axes will be set to that
            value.
        look_at: Look-at target, specified either as a ``ReplicatorItem``, a prim path, or world coordinates.
                If multiple prims are set, the target point will be the mean of their positions.
        look_at_up_axis: Look-at up axis of the created prim.
        pivot: Pivot point of the created prim normalized in the range [-1, 1] for each axis.
        relative_to: If provided, position will be relative to this prim instead of world space.
        semantics: Dictionary specifying semantic type and values. Legacy lists of tuples are also accepted but will be converted to dictionaries.
        visible: If ``False``, the prim will be invisible. This is often useful when creating prims to use as bounds
            with other randomizers.
        as_mesh: If True, creates a mesh cone. If False, creates a native USD cone.
        name: Name of the object.
        parent: Optional parent prim path. The cone will be created as a child of this prim.
        material: Material to bind to the created prim.

    Example:
        >>> import omni.replicator.core as rep
        >>> rng = rep.rng.ReplicatorRNG()
        >>> cone = rep.functional.create.cone(
        ...     position=rng.generator.uniform((0,0,0), (100, 100, 100)),
        ...     semantics={"class": "cone"},
        ... )
    """
    return create_batch.cone(
        name=name,
        parent=parent,
        position=position,
        rotation=rotation,
        scale=scale,
        look_at=look_at,
        look_at_up_axis=look_at_up_axis,
        pivot=pivot,
        relative_to=relative_to,
        semantics=semantics,
        visible=visible,
        as_mesh=as_mesh,
        material=material,
        count=1,
    )[0]


def sphere_light(
    position: Union[float, Tuple[float]] = None,
    scale: Union[float, Tuple[float]] = None,
    rotation: Union[float, Tuple[float]] = None,
    look_at: Union[
        str,
        pxr.Sdf.Path,
        usdrt.Sdf.Path,
        Tuple[float, float, float],
        List[Union[str, pxr.Sdf.Path, usdrt.Sdf.Path]],
    ] = None,
    look_at_up_axis: Union[Tuple[float]] = None,
    pivot: Union[Tuple[float, float, float], List[Tuple[float, float, float]], pxr.Gf.Vec3d] = None,
    relative_to: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    semantics: Union[Dict[str, Union[List, str]], List[Tuple[str, str]]] = None,
    visible: bool = True,
    color: Union[Tuple[float, float, float]] = (1.0, 1.0, 1.0),
    intensity: Union[float] = 30000.0,
    exposure: Union[float] = None,
    color_temperature: Union[float] = 6500,
    enable_color_temperature: bool = False,
    diffuse: float = 1.0,
    specular: float = 1.0,
    shaping_cone_angle: float = 180.0,
    shaping_cone_softness: float = 0.0,
    shaping_focus_tint: float = (1.0, 1.0, 1.0),
    radius: float = 1.0,
    name: str = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
) -> pxr.Usd.Prim:
    """Create a sphere light

    Args:
        position: XYZ coordinates in world space. If a single value is provided, all axes will be set to that value.
        scale: Scaling factors for XYZ axes. If a single value is provided, all axes will be set to that value.
        rotation: Euler angles in degrees in XYZ order. If a single value is provided, all axes will be set to that
            value.
        look_at: Look-at target, specified either as a ``ReplicatorItem``, a prim path, or world coordinates.
                If multiple prims are set, the target point will be the mean of their positions.
        look_at_up_axis: Look-at up axis of the created prim.
        pivot: Pivot point of the created prim normalized in the range [-1, 1] for each axis.
        relative_to: If provided, position will be relative to this prim instead of world space.
        semantics: Dictionary specifying semantic type and values. Legacy lists of tuples are also accepted but will be converted to dictionaries.
        visible: If ``False``, the prim will be invisible. This is often useful when creating prims to use as bounds
            with other randomizers.
        color: Color of the light.
        intensity: Intensity of the light.
        exposure: Exposure of the light.
        color_temperature: Color temperature of the light.
        enable_color_temperature: If ``True``, the light will use a color temperature.
        diffuse: Diffuse of the light.
        specular: Specular of the light.
        shaping_cone_angle: Shaping cone angle of the light.
        shaping_cone_softness: Softness of the light cone.
        shaping_focus_tint: Shaping focus tint of the light.
        radius: Radius of the light.
        name: Name of the object.
        parent: Optional parent prim path. The xform will be created as a child of this prim.

    Example:
        >>> import omni.replicator.core as rep
        >>> rng = rep.rng.ReplicatorRNG()
        >>> sphere_light = rep.functional.create.sphere_light(
        ...     position=rng.generator.uniform((0,0,0), (100, 100, 100)),
        ... )
    """

    return create_batch.sphere_light(
        name=name,
        parent=parent,
        position=position,
        rotation=rotation,
        scale=scale,
        look_at=look_at,
        look_at_up_axis=look_at_up_axis,
        pivot=pivot,
        relative_to=relative_to,
        semantics=semantics,
        visible=visible,
        color=color,
        intensity=intensity,
        exposure=exposure,
        color_temperature=color_temperature,
        enable_color_temperature=enable_color_temperature,
        diffuse=diffuse,
        specular=specular,
        shaping_cone_angle=shaping_cone_angle,
        shaping_cone_softness=shaping_cone_softness,
        shaping_focus_tint=shaping_focus_tint,
        radius=radius,
        count=1,
    )[0]


def disk_light(
    position: Union[float, Tuple[float]] = None,
    scale: Union[float, Tuple[float]] = None,
    rotation: Union[float, Tuple[float]] = None,
    look_at: Union[
        str,
        pxr.Sdf.Path,
        usdrt.Sdf.Path,
        Tuple[float, float, float],
        List[Union[str, pxr.Sdf.Path, usdrt.Sdf.Path]],
    ] = None,
    look_at_up_axis: Union[Tuple[float]] = None,
    pivot: Union[Tuple[float, float, float], List[Tuple[float, float, float]], pxr.Gf.Vec3d] = None,
    relative_to: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    semantics: Union[Dict[str, Union[List, str]], List[Tuple[str, str]]] = None,
    visible: bool = True,
    color: Union[Tuple[float, float, float]] = (1.0, 1.0, 1.0),
    intensity: Union[float] = 30000.0,
    exposure: Union[float] = None,
    color_temperature: Union[float] = 6500,
    enable_color_temperature: bool = False,
    diffuse: float = 1.0,
    specular: float = 1.0,
    shaping_cone_angle: float = 180.0,
    shaping_cone_softness: float = 0.0,
    shaping_focus_tint: float = (1.0, 1.0, 1.0),
    radius: float = 1.0,
    name: str = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
) -> pxr.Usd.Prim:
    """Create a disk light.

    Args:
        position: XYZ coordinates in world space. If a single value is provided, all axes are set to that value.
        scale: Scaling factors for XYZ axes. If a single value is provided, all axes are set to that value.
        rotation: Euler angles in degrees in XYZ order. If a single value is provided, all axes are set to that value.
        look_at: Look-at target as a prim path or world coordinates. For multiple prims, their mean is used.
        look_at_up_axis: Look-at up axis of the created prim.
        pivot: Pivot point normalized to [-1, 1] for each axis.
        relative_to: If provided, position will be relative to this prim instead of world space.
        semantics: Dictionary of semantic type and values (legacy list of tuples also accepted).
        visible: Whether the prim is visible.
        color: RGB color of the light.
        intensity: Light intensity in lumens.
        exposure: Light exposure value.
        color_temperature: Color temperature in Kelvin.
        enable_color_temperature: Whether to use color temperature.
        diffuse: Diffuse contribution multiplier.
        specular: Specular contribution multiplier.
        shaping_cone_angle: Angle of the light cone in degrees.
        shaping_cone_softness: Softness of the light cone.
        shaping_focus_tint: RGB tint color for focused area.
        radius: Radius of the disk light.
        name: Name of the object.
        parent: Optional parent prim path.

    Example:
        >>> import omni.replicator.core as rep
        >>> rng = rep.rng.ReplicatorRNG()
        >>> disk_light = rep.functional.create.disk_light(
        ...     position=rng.generator.uniform((0,0,0), (100, 100, 100)),
        ... )
    """

    return create_batch.disk_light(
        name=name,
        parent=parent,
        position=position,
        rotation=rotation,
        scale=scale,
        look_at=look_at,
        look_at_up_axis=look_at_up_axis,
        pivot=pivot,
        relative_to=relative_to,
        semantics=semantics,
        visible=visible,
        color=color,
        intensity=intensity,
        exposure=exposure,
        color_temperature=color_temperature,
        enable_color_temperature=enable_color_temperature,
        diffuse=diffuse,
        specular=specular,
        shaping_cone_angle=shaping_cone_angle,
        shaping_cone_softness=shaping_cone_softness,
        shaping_focus_tint=shaping_focus_tint,
        radius=radius,
        count=1,
    )[0]


def rect_light(
    position: Union[float, Tuple[float]] = None,
    scale: Union[float, Tuple[float]] = None,
    rotation: Union[float, Tuple[float]] = None,
    look_at: Union[
        str,
        pxr.Sdf.Path,
        usdrt.Sdf.Path,
        Tuple[float, float, float],
        List[Union[str, pxr.Sdf.Path, usdrt.Sdf.Path]],
    ] = None,
    look_at_up_axis: Union[Tuple[float]] = None,
    pivot: Union[Tuple[float, float, float], List[Tuple[float, float, float]], pxr.Gf.Vec3d] = None,
    relative_to: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    semantics: Union[Dict[str, Union[List, str]], List[Tuple[str, str]]] = None,
    visible: bool = True,
    color: Union[Tuple[float, float, float]] = (1.0, 1.0, 1.0),
    intensity: Union[float] = 30000.0,
    exposure: Union[float] = None,
    color_temperature: Union[float] = 6500,
    enable_color_temperature: bool = False,
    diffuse: float = 1.0,
    specular: float = 1.0,
    shaping_cone_angle: float = 180.0,
    shaping_cone_softness: float = 0.0,
    shaping_focus_tint: float = (1.0, 1.0, 1.0),
    height: float = 1.0,
    width: float = 1.0,
    name: str = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
) -> pxr.Usd.Prim:
    """Create a rectangle light.

    Args:
        position: XYZ coordinates in world space. If a single value is provided, all axes are set to that value.
        scale: Scaling factors for XYZ axes. If a single value is provided, all axes are set to that value.
        rotation: Euler angles in degrees in XYZ order. If a single value is provided, all axes are set to that value.
        look_at: Look-at target as a prim path or world coordinates. For multiple prims, their mean is used.
        look_at_up_axis: Look-at up axis of the created prim.
        pivot: Pivot point normalized to [-1, 1] for each axis.
        relative_to: If provided, position will be relative to this prim instead of world space.
        semantics: Dictionary of semantic type and values (legacy list of tuples also accepted).
        visible: Whether the prim is visible.
        color: RGB color of the light.
        intensity: Light intensity in lumens.
        exposure: Light exposure value.
        color_temperature: Color temperature in Kelvin.
        enable_color_temperature: Whether to use color temperature.
        diffuse: Diffuse contribution multiplier.
        specular: Specular contribution multiplier.
        shaping_cone_angle: Angle of the light cone in degrees.
        shaping_cone_softness: Softness of the light cone.
        shaping_focus_tint: RGB tint color for focused area.
        height: Height of the rectangle light.
        width: Width of the rectangle light.
        name: Name of the object.
        parent: Optional parent prim path.

    Example:
        >>> import omni.replicator.core as rep
        >>> rng = rep.rng.ReplicatorRNG()
        >>> rect_light = rep.functional.create.rect_light(
        ...     position=rng.generator.uniform((0,0,0), (100, 100, 100)),
        ... )
    """

    return create_batch.rect_light(
        name=name,
        parent=parent,
        position=position,
        rotation=rotation,
        scale=scale,
        look_at=look_at,
        look_at_up_axis=look_at_up_axis,
        pivot=pivot,
        relative_to=relative_to,
        semantics=semantics,
        visible=visible,
        color=color,
        intensity=intensity,
        exposure=exposure,
        color_temperature=color_temperature,
        enable_color_temperature=enable_color_temperature,
        diffuse=diffuse,
        specular=specular,
        shaping_cone_angle=shaping_cone_angle,
        shaping_cone_softness=shaping_cone_softness,
        shaping_focus_tint=shaping_focus_tint,
        height=height,
        width=width,
        count=1,
    )[0]


def cylinder_light(
    position: Union[float, Tuple[float]] = None,
    scale: Union[float, Tuple[float]] = None,
    rotation: Union[float, Tuple[float]] = None,
    look_at: Union[
        str,
        pxr.Sdf.Path,
        usdrt.Sdf.Path,
        Tuple[float, float, float],
        List[Union[str, pxr.Sdf.Path, usdrt.Sdf.Path]],
    ] = None,
    look_at_up_axis: Union[Tuple[float]] = None,
    pivot: Union[Tuple[float, float, float], List[Tuple[float, float, float]], pxr.Gf.Vec3d] = None,
    relative_to: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    semantics: Union[Dict[str, Union[List, str]], List[Tuple[str, str]]] = None,
    visible: bool = True,
    color: Union[Tuple[float, float, float]] = (1.0, 1.0, 1.0),
    intensity: Union[float] = 30000.0,
    exposure: Union[float] = None,
    color_temperature: Union[float] = 6500,
    enable_color_temperature: bool = False,
    diffuse: float = 1.0,
    specular: float = 1.0,
    shaping_cone_angle: float = 180.0,
    shaping_cone_softness: float = 0.0,
    shaping_focus_tint: float = (1.0, 1.0, 1.0),
    radius: float = 1.0,
    length: float = 1.0,
    name: str = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
) -> pxr.Usd.Prim:
    """Create a cylinder light.

    Args:
        position: XYZ coordinates in world space. If a single value is provided, all axes are set to that value.
        scale: Scaling factors for XYZ axes. If a single value is provided, all axes are set to that value.
        rotation: Euler angles in degrees in XYZ order. If a single value is provided, all axes are set to that value.
        look_at: Look-at target as a prim path or world coordinates. For multiple prims, their mean is used.
        look_at_up_axis: Look-at up axis of the created prim.
        pivot: Pivot point normalized to [-1, 1] for each axis.
        relative_to: If provided, position will be relative to this prim instead of world space.
        semantics: Dictionary of semantic type and values (legacy list of tuples also accepted).
        visible: Whether the prim is visible.
        color: RGB color of the light.
        intensity: Light intensity in lumens.
        exposure: Light exposure value.
        color_temperature: Color temperature in Kelvin.
        enable_color_temperature: Whether to use color temperature.
        diffuse: Diffuse contribution multiplier.
        specular: Specular contribution multiplier.
        shaping_cone_angle: Angle of the light cone in degrees.
        shaping_cone_softness: Softness of the light cone.
        shaping_focus_tint: RGB tint color for focused area.
        radius: Radius of the cylinder light.
        length: Length of the cylinder light.
        name: Name of the object.
        parent: Optional parent prim path.

    Example:
        >>> import omni.replicator.core as rep
        >>> rng = rep.rng.ReplicatorRNG()
        >>> cylinder_light = rep.functional.create.cylinder_light(
        ...     position=rng.generator.uniform((0,0,0), (100, 100, 100)),
        ... )
    """

    return create_batch.cylinder_light(
        name=name,
        parent=parent,
        position=position,
        rotation=rotation,
        scale=scale,
        look_at=look_at,
        look_at_up_axis=look_at_up_axis,
        pivot=pivot,
        relative_to=relative_to,
        semantics=semantics,
        visible=visible,
        color=color,
        intensity=intensity,
        exposure=exposure,
        color_temperature=color_temperature,
        enable_color_temperature=enable_color_temperature,
        diffuse=diffuse,
        specular=specular,
        shaping_cone_angle=shaping_cone_angle,
        shaping_cone_softness=shaping_cone_softness,
        shaping_focus_tint=shaping_focus_tint,
        radius=radius,
        length=length,
        count=1,
    )[0]


def distant_light(
    position: Union[float, Tuple[float]] = None,
    scale: Union[float, Tuple[float]] = None,
    rotation: Union[float, Tuple[float]] = None,
    look_at: Union[
        str,
        pxr.Sdf.Path,
        usdrt.Sdf.Path,
        Tuple[float, float, float],
        List[Union[str, pxr.Sdf.Path, usdrt.Sdf.Path]],
    ] = None,
    look_at_up_axis: Union[Tuple[float]] = None,
    pivot: Union[Tuple[float, float, float], List[Tuple[float, float, float]], pxr.Gf.Vec3d] = None,
    relative_to: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    semantics: Union[Dict[str, Union[List, str]], List[Tuple[str, str]]] = None,
    visible: bool = True,
    color: Union[Tuple[float, float, float]] = (1.0, 1.0, 1.0),
    intensity: Union[float] = 30000.0,
    exposure: Union[float] = None,
    color_temperature: Union[float] = 6500,
    enable_color_temperature: bool = False,
    diffuse: float = 1.0,
    specular: float = 1.0,
    shaping_cone_angle: float = 180.0,
    shaping_cone_softness: float = 0.0,
    shaping_focus_tint: float = (1.0, 1.0, 1.0),
    angle: float = 1.0,
    name: str = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
) -> pxr.Usd.Prim:
    """Create a distant light.

    Args:
        position: XYZ coordinates in world space. If a single value is provided, all axes are set to that value.
        scale: Scaling factors for XYZ axes. If a single value is provided, all axes are set to that value.
        rotation: Euler angles in degrees in XYZ order. If a single value is provided, all axes are set to that value.
        look_at: Look-at target as a prim path or world coordinates. For multiple prims, their mean is used.
        look_at_up_axis: Look-at up axis of the created prim.
        pivot: Pivot point normalized to [-1, 1] for each axis.
        relative_to: If provided, position will be relative to this prim instead of world space.
        semantics: Dictionary of semantic type and values (legacy list of tuples also accepted).
        visible: Whether the prim is visible.
        color: RGB color of the light.
        intensity: Light intensity in lumens.
        exposure: Light exposure value.
        color_temperature: Color temperature in Kelvin.
        enable_color_temperature: Whether to use color temperature.
        diffuse: Diffuse contribution multiplier.
        specular: Specular contribution multiplier.
        shaping_cone_angle: Angle of the light cone in degrees.
        shaping_cone_softness: Softness of the light cone.
        shaping_focus_tint: RGB tint color for focused area.
        angle: Angle of the distant light cone in degrees.
        name: Name of the object.
        parent: Optional parent prim path.

    Returns:
        The created distant light prim.
    """

    return create_batch.distant_light(
        name=name,
        parent=parent,
        position=position,
        rotation=rotation,
        scale=scale,
        look_at=look_at,
        look_at_up_axis=look_at_up_axis,
        pivot=pivot,
        relative_to=relative_to,
        semantics=semantics,
        visible=visible,
        color=color,
        intensity=intensity,
        exposure=exposure,
        color_temperature=color_temperature,
        enable_color_temperature=enable_color_temperature,
        diffuse=diffuse,
        specular=specular,
        shaping_cone_angle=shaping_cone_angle,
        shaping_cone_softness=shaping_cone_softness,
        shaping_focus_tint=shaping_focus_tint,
        angle=angle,
        count=1,
    )[0]


def dome_light(
    color: Tuple[float] = (1.0, 1.0, 1.0),
    texture: str = None,
    texture_format: str = "latlong",
    intensity: float = 1000.0,
    exposure: float = 1.0,
    diffuse: float = 1.0,
    specular: float = 1.0,
    color_temperature: Union[float] = 6500,
    enable_color_temperature: bool = False,
    position: Union[float, Tuple[float]] = None,
    scale: Union[float, Tuple[float]] = None,
    rotation: Union[float, Tuple[float]] = None,
    look_at: Union[
        str,
        pxr.Sdf.Path,
        usdrt.Sdf.Path,
        Tuple[float, float, float],
        List[Union[str, pxr.Sdf.Path, usdrt.Sdf.Path]],
    ] = None,
    look_at_up_axis: Union[Tuple[float]] = None,
    name: str = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
) -> pxr.Usd.Prim:
    """Create a Dome Light

    Args:
        color: Color of the light.
        texture: Path to the texture file for the dome light.
        texture_format: Format of the texture. Default is "latlong".
        intensity: Intensity of the light.
        exposure: Exposure multiplier.
        diffuse: Diffuse component of the light.
        specular: Specular component of the light.
        color_temperature: Color temperature of the light.
        enable_color_temperature: If ``True``, the light will use a color temperature.
        position: XYZ coordinates in world space. If a single value is provided, all axes will be set to that value.
        scale: Scaling factors for XYZ axes. If a single value is provided, all axes will be set to that value.
        rotation: Euler angles in degrees in XYZ order. If a single value is provided, all axes will be set to that
            value.
        look_at: Look-at target, specified either as a ``ReplicatorItem``, a prim path, or world coordinates.
                If multiple prims are set, the target point will be the mean of their positions.
        look_at_up_axis: Look-at up axis of the created prim.
        name: Name of the object.
        parent: Optional parent prim path. The dome light will be created as a child of this prim.

    Example:
        >>> import omni.replicator.core as rep
        >>> rng = rep.rng.ReplicatorRNG()
        >>> dome_light = rep.functional.create.dome_light(
        ...     intensity=rng.generator.uniform(1000.0, 2000.0),
        ...     color=(0.8, 0.8, 1.0),
        ... )
    """
    return create_batch.dome_light(
        name=name,
        parent=parent,
        position=position,
        rotation=rotation,
        scale=scale,
        look_at=look_at,
        look_at_up_axis=look_at_up_axis,
        color=color,
        texture=texture,
        texture_format=texture_format,
        intensity=intensity,
        exposure=exposure,
        diffuse=diffuse,
        specular=specular,
        color_temperature=color_temperature,
        enable_color_temperature=enable_color_temperature,
        count=1,
    )[0]


def material(
    mdl: str,
    bind_prims: Optional[pxr.Usd.Prim] = None,
    name: str = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    **kwargs,
):
    """Create a material

    Args:
        mdl: Path to the material definition.
        bind_prims: List of prims to bind the material to.
        name: Name of the material.
        parent: Optional parent prim path. The material will be created as a child of this prim.

    Example:
        >>> import omni.replicator.core as rep
        >>> rng = rep.rng.ReplicatorRNG()
        >>> material = rep.functional.create.material(
        ...     mdl="OmniPBR.mdl",
        ...     diffuse_color_constant=rng.generator.uniform((0.1, 0.1, 1.0), (0.8, 0.8, 1.0)),
        ... )
    """
    return create_batch.material(
        mdl=mdl,
        bind_prims=[bind_prims],
        name=name,
        parent=parent,
        count=1,
        **kwargs,
    )[0]


def omni_lidar(
    position: Union[float, Tuple[float]] = None,
    rotation: Union[float, Tuple[float]] = None,
    name: Optional[str] = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    **kwargs,
) -> List[Union[pxr.Usd.Prim, usdrt.Usd.Prim]]:
    """Create a LiDAR sensor.

    Args:
        position: XYZ coordinates in world space. If a single value is provided, all axes will be set to that value.
        rotation: Euler angles in degrees in XYZ order. If a single value is provided, all axes will be set to that
            value.
        name: Name for the LiDAR sensor
        parent: Parent prim path to create LiDAR under
        **kwargs: Additional attributes to be added to the LiDAR sensor

    Example:
        >>> import omni.replicator.core as rep
        >>> # Create LiDAR sensor
        >>> lidar = rep.functional.create.omni_lidar(
        ...     position=(100, 100, 100),
        ...     rotation=(45, 45, 0),
        ... )
    """
    # Create the LiDAR sensor
    return create_batch.omni_lidar(
        position=position,
        rotation=rotation,
        count=1,
        name=name,
        parent=parent,
        **kwargs,
    )[0]


def omni_radar(
    position: Union[float, Tuple[float]] = None,
    rotation: Union[float, Tuple[float]] = None,
    name: Optional[str] = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    **kwargs,
) -> List[Union[pxr.Usd.Prim, usdrt.Usd.Prim]]:
    """Create a Radar sensor.

    Args:
        position: XYZ coordinates in world space. If a single value is provided, all axes will be set to that value.
        rotation: Euler angles in degrees in XYZ order. If a single value is provided, all axes will be set to that
            value.
        name: Name for the Radar sensor
        parent: Parent prim path to create Radar under
        **kwargs: Additional attributes to be added to the Radar sensor

    Example:
        >>> import omni.replicator.core as rep
        >>> # Create Radar sensor
        >>> radar = rep.functional.create.omni_radar(
        ...     position=(100, 100, 100),
        ...     rotation=(45, 45, 0),
        ... )
    """

    # Create the Radar sensor
    return create_batch.omni_radar(
        position=position,
        rotation=rotation,
        count=1,
        name=name,
        parent=parent,
        **kwargs,
    )[0]
