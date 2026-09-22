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

# pylint: disable=too-many-lines,broad-except,redefined-outer-name,protected-access

import json
import math
import sys
from collections import namedtuple
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple, Union

import carb.settings
import omni.client
import omni.graph.core as og
import omni.kit.async_engine
import omni.kit.commands
import omni.usd
import pxr
import usdrt
from omni.replicator.core.bindings._omni_replicator_core import Schema_omni_replicator_extinfo_1_0
from pxr import Gf, Sdf, Tf, Usd, UsdGeom

from . import functional as F  # noqa: N812  # ignore uppercase import linting error
from . import modify
from .distribution import choice
from .utils import (
    ReplicatorItem,
    ReplicatorWrapper,
    create_node,
    get_non_xform_prims,
    get_usd_files,
    utils,
    viewport_manager,
)
from .utils.mdl_graph_gen import MaterialGraphGenerator

REPLICATOR_SCOPE = "/Replicator"
LOOKS_PATH = "/Replicator/Looks"

POSE_ATTRIBUTES = ["position", "rotation", "scale", "look_at", "look_at_up_axis"]
XFORM_ATTRIBUTES = ["semantics", "visible"] + POSE_ATTRIBUTES
VALID_PROJECTIONS = [
    "pinhole",
    "pinholeOpenCV",
    "fisheyePolynomial",
    "fisheyeSpherical",
    "fisheyeKannalaBrandtK3",
    "fisheyeOpenCV",
    "fisheyeRadTanThinPrism",
    "omniDirectionalStereo",
    "generalizedProjection",
]

UsdAttrMapping = namedtuple("UsdAttrMapping", ["usd_attr", "value"])


def _set_targets(node, relationship, targets):
    stage = omni.usd.get_context().get_stage()
    node_prim = stage.GetPrimAtPath(node.get_prim_path())
    node_prim.GetRelationship(relationship).SetTargets([str(t) for t in targets])


# TODO Refactor this function (too-complex), or move to C++ if performance is an issue
def _create_prim(  # noqa: C901  # ignore complexity linting error
    prim_type: str,
    material=None,
    count=1,
    parent=None,
    name=None,
    prim_create_fn=None,
    **kwargs,
):
    # Create xform parent
    # Replicator nests prims under Xforms to enable intuitive pivoting and transform GT reporting
    if parent is None:
        parent = "/Replicator"
        stage = omni.usd.get_context().get_stage()
        if not stage.GetPrimAtPath(parent).IsValid():
            stage.DefinePrim(parent, "Scope")
    elif isinstance(parent, ReplicatorItem):
        parent = parent.node.get_attribute("outputs:prims").get()

    # Create xform
    suffix = "" if prim_type == "Xform" else "_Xform"
    if name is None:
        xform_name = f"{prim_type}{suffix}"
    else:
        xform_name = f"{Tf.MakeValidIdentifier(name)}{suffix}"

    # Handle both static and dynamic (ReplicatorItem) attributes
    attributes = {
        "xform": {"defined": {"position": (0, 0, 0), "scale": (1, 1, 1)}, "dynamic": {}},
        "prim": {"defined": {"position": (0, 0, 0), "scale": (1, 1, 1)}, "dynamic": {}},
    }
    if "look_at" not in kwargs:
        # If look_at is not specified, set default rotation
        attributes["xform"]["defined"]["rotation"] = (0, 0, 0)
        attributes["prim"]["defined"]["rotation"] = (0, 0, 0)

    for attr, value in kwargs.items():
        if isinstance(value, UsdAttrMapping):
            attr = value.usd_attr if isinstance(value.value, ReplicatorItem) else attr
            value = value.value

        if value is None:
            continue

        attr_prim = "xform" if attr in XFORM_ATTRIBUTES else "prim"
        attr_type = "dynamic" if isinstance(value, ReplicatorItem) else "defined"
        attributes[attr_prim][attr_type][attr] = value

        if attr == "look_at" and "look_at_up_axis" in kwargs:
            attributes[attr_prim][attr_type]["look_at_up_axis"] = kwargs["look_at_up_axis"]

        if attr == "pivot":
            attributes["prim"]["defined"]["position"] = (0, 0, 0)

    mod = usdrt if F.utils.get_is_fsd_enabled() else pxr
    new_attributes = [("replicatorXform", mod.Sdf.ValueTypeNames.Bool, False)]
    if prim_type == "Camera":
        new_attributes.append(("replicatorCameraXform", mod.Sdf.ValueTypeNames.Bool, False))

    # Create xforms for all prims except materials
    if prim_type != "Material":
        xforms = F.create_batch._create_prim_generic(
            prim_type_name="Xform",
            name=xform_name,
            parent=parent,
            count=count,
            new_attributes=new_attributes,
            replicatorXform=True,
            **attributes["xform"]["defined"],
        )
        prims_parent = xforms
        xform_group = group([str(xf.GetPrimPath()) for xf in xforms])
    else:
        xforms = None
        looks = stage.GetPrimAtPath(f"{REPLICATOR_SCOPE}/Looks")
        if looks.IsValid():
            prims_parent = looks
        else:
            prims_parent = F.create.scope(name="Looks", parent=parent)
        xform_group = None

    if prim_type != "Xform":
        # Create prim
        if name is None:
            prim_name = prim_type
        else:
            prim_name = Tf.MakeValidIdentifier(name)

        if prim_create_fn is None:
            prim_create_fn = getattr(F.create_batch, prim_type.replace("Light", "_light").lower())

        prims = prim_create_fn(
            name=prim_name,
            parent=prims_parent,
            count=count,
            **attributes["prim"]["defined"],
        )

        # Rotate cameras 90 degrees if up axis is Z
        prim_type = prims[0].GetTypeName()
        up_axis = pxr.UsdGeom.GetStageUpAxis(omni.usd.get_context().get_stage())
        if prim_type.lower() == "camera" and up_axis == "Z":
            F.modify.rotation(prims, [(90, 0, 90)])

        # Apply ReplicatorItem attribute values
        prim_group = group([str(p.GetPrimPath()) for p in prims])
        with prim_group:
            for attr, item in attributes["prim"]["dynamic"].items():
                modify.attribute(attr, item)
            if material:
                modify.material(material)

    if xforms is None:
        xform_group = prim_group

    with xform_group:
        if any(k in attributes["xform"]["dynamic"] for k in POSE_ATTRIBUTES):
            modify.pose(
                position=attributes["xform"]["dynamic"].get("position", None),
                rotation=attributes["xform"]["dynamic"].get("rotation", None),
                scale=attributes["xform"]["dynamic"].get("scale", None),
                look_at=attributes["xform"]["dynamic"].get("look_at", None),
                look_at_up_axis=attributes["xform"]["dynamic"].get("look_at_up_axis", None),
                pivot=attributes["xform"]["dynamic"].get("pivot", None),
            )
        if "semantics" in attributes["xform"]["dynamic"]:
            modify.semantics(attributes["xform"]["dynamic"]["semantics"])
        if "visible" in attributes["xform"]["dynamic"]:
            modify.visibility(attributes["xform"]["dynamic"]["visible"])

    return xform_group


def register(  # pylint: disable=invalid-name
    fn: Callable[..., Union[ReplicatorItem, og.Node]], override: bool = True, fn_name: Optional[str] = None
) -> None:
    """Register a new function under ``omni.replicator.core.create``.
    Extend the default capabilities of ``omni.replicator.core.create`` by registering new functionality. New functions
    must return a ``ReplicatorItem`` or an ``OmniGraph`` node.

    Args:
        fn: A function that returns a ``ReplicatorItem`` or an ``OmniGraph`` node.
        override: If ``True``, will override existing functions of the same name. If ``False``, an error is raised.
        fn_name: Optional arg that let user choose the function name when registering it in replicator. If not
            specified, the function name is used. ``fn_name`` must follow valid [Python identifier rules]
            (https://docs.python.org/3.10/reference/lexical_analysis.html#identifiers)


    Example:
        >>> import omni.replicator.core as rep
        >>> def light_cluster(num_lights: int = 10):
        ...     lights = rep.create.light(
        ...         light_type="sphere",
        ...         count=num_lights,
        ...         position=rep.distribution.uniform((-500, -500, -500), (500, 500, 500)),
        ...         intensity=rep.distribution.uniform(10000, 20000),
        ...         temperature=rep.distribution.uniform(1000, 10000),
        ...     )
        ...     return lights
        >>> rep.create.register(light_cluster)
        >>> lights = rep.create.light_cluster(50)

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
            carb.log_info(f"Overriding function {{{fn_name}}} for replicator.create.")
        else:
            raise ValueError()

    wrapped_fn = ReplicatorWrapper(fn)
    setattr(sys.modules[__name__], fn_name, wrapped_fn)


@ReplicatorWrapper
def xform(
    position: Union[ReplicatorItem, float, Tuple[float]] = None,
    scale: Union[ReplicatorItem, float, Tuple[float]] = None,
    rotation: Union[ReplicatorItem, float, Tuple[float]] = None,
    look_at: Union[
        ReplicatorItem,
        str,
        Sdf.Path,
        usdrt.Sdf.Path,
        Tuple[float, float, float],
        List[Union[str, Sdf.Path, usdrt.Sdf.Path]],
    ] = None,
    look_at_up_axis: Union[ReplicatorItem, Tuple[float]] = None,
    semantics: Union[Dict[str, Union[List, str]], List[Tuple[str, str]]] = None,
    visible: bool = True,
    count: int = 1,
    name: Optional[str] = None,
    parent: Union[ReplicatorItem, str, Sdf.Path, Usd.Prim] = None,
) -> ReplicatorItem:
    """Create a Xform

    Args:
        position: XYZ coordinates in world space. If a single value is provided, all axes will be set to that value.
        scale: Scaling factors for XYZ axes. If a single value is provided, all axes will be set to that value.
        rotation: Euler angles in degrees in XYZ order. If a single value is provided, all axes will be set to that
            value.
        look_at: Look-at target, specified either as a ``ReplicatorItem``, a prim path, or world coordinates.
                If multiple prims are set, the target point will be the mean of their positions.
        look_at_up_axis: Look-at up axis of the created prim.
        semantics: Dictionary specifying semantic type and values. Legacy lists of tuples are also accepted but will be
            converted to dictionaries.
        visible: If ``False``, the prim will be invisible. This is often useful when creating prims to use as bounds
            with other randomizers.
        count: Number of objects to create.
        name: Name of the object.
        parent: Optional parent prim path. The xform will be created as a child of this prim.


    Example:
        >>> import omni.replicator.core as rep
        >>> xform = rep.create.xform(
        ...     position=rep.distribution.uniform((0,0,0), (100, 100, 100)),
        ...     semantics={"class": ["thing"]},
        ... )
    """
    if count < 1:
        raise ValueError(f"Count must be higher than 0, recieved {count}.")
    return _create_prim(
        prim_type="Xform",
        position=position,
        scale=scale,
        rotation=rotation,
        look_at=look_at,
        look_at_up_axis=look_at_up_axis,
        semantics=semantics,
        visible=visible,
        count=count,
        name=name,
        parent=parent,
    )


@ReplicatorWrapper
def sphere(
    position: Union[ReplicatorItem, float, Tuple[float]] = None,
    scale: Union[ReplicatorItem, float, Tuple[float]] = None,
    pivot: Union[ReplicatorItem, Tuple[float]] = None,
    rotation: Union[ReplicatorItem, float, Tuple[float]] = None,
    look_at: Union[
        ReplicatorItem,
        str,
        Sdf.Path,
        usdrt.Sdf.Path,
        Tuple[float, float, float],
        List[Union[str, Sdf.Path, usdrt.Sdf.Path]],
    ] = None,
    look_at_up_axis: Union[ReplicatorItem, Tuple[float]] = None,
    semantics: Union[Dict[str, Union[List, str]], List[Tuple[str, str]]] = None,
    material: Union[ReplicatorItem, Usd.Prim] = None,
    visible: bool = True,
    as_mesh: bool = True,
    count: int = 1,
    name: Optional[str] = None,
    parent: Union[ReplicatorItem, str, Sdf.Path, Usd.Prim] = None,
) -> ReplicatorItem:
    """Create a sphere

    Args:
        position: XYZ coordinates in world space. If a single value is provided, all axes will be set to that value.
        scale: Scaling factors for XYZ axes. If a single value is provided, all axes will be set to that value.
        pivot: Pivot that sets the center point of translate and rotate operation. Pivot values are normalized between
            ``[-1, 1]`` for each axis based on the  prim's axis aligned extents.
        rotation: Euler angles in degrees in XYZ order. If a single value is provided, all axes will be set to that
            value.
        look_at: Look-at target, specified either as a ``ReplicatorItem``, a prim path, or world coordinates.
                If multiple prims are set, the target point will be the mean of their positions.
        look_at_up_axis: Look-at up axis of the created prim.
        semantics: Dictionary specifying semantic type and values. Legacy lists of tuples are also accepted but will be
            converted to dictionaries.
        material: Material to attach to the sphere.
        visible: If ``False``, the prim will be invisible. This is often useful when creating prims to use as bounds
            with other randomizers.
        as_mesh: If ``False``, create a ``Usd.Sphere`` prim. If ``True``, create a mesh.
        count: Number of objects to create.
        name: Name of the object.
        parent: Optional parent prim path. The object will be created as a child of this prim.

    Example:
        >>> import omni.replicator.core as rep
        >>> sphere = rep.create.sphere(
        ...     position=rep.distribution.uniform((0,0,0), (100, 100, 100)),
        ...     scale=2,
        ...     rotation=(45, 45, 0),
        ...     semantics={"class": ["sphere"]},
        ... )
    """
    if count < 1:
        raise ValueError(f"Count must be higher than 0, recieved {count}.")
    return _create_prim(
        prim_type="Sphere",
        position=position,
        scale=scale,
        pivot=pivot,
        rotation=rotation,
        look_at=look_at,
        look_at_up_axis=look_at_up_axis,
        semantics=semantics,
        material=material,
        visible=visible,
        as_mesh=as_mesh,
        count=count,
        name=name,
        parent=parent,
    )


@ReplicatorWrapper
def torus(
    position: Union[ReplicatorItem, float, Tuple[float]] = None,
    scale: Union[ReplicatorItem, float, Tuple[float]] = None,
    pivot: Union[ReplicatorItem, Tuple[float]] = None,
    rotation: Union[ReplicatorItem, float, Tuple[float]] = None,
    look_at: Union[
        ReplicatorItem,
        str,
        Sdf.Path,
        usdrt.Sdf.Path,
        Tuple[float, float, float],
        List[Union[str, Sdf.Path, usdrt.Sdf.Path]],
    ] = None,
    look_at_up_axis: Union[ReplicatorItem, Tuple[float]] = None,
    semantics: Union[Dict[str, Union[List, str]], List[Tuple[str, str]]] = None,
    material: Union[ReplicatorItem, Usd.Prim] = None,
    visible: bool = True,
    count: int = 1,
    name: Optional[str] = None,
    parent: Union[ReplicatorItem, str, Sdf.Path, Usd.Prim] = None,
) -> ReplicatorItem:
    """Create a torus

    Args:
        position: XYZ coordinates in world space. If a single value is provided, all axes will be set to that value.
        scale: Scaling factors for XYZ axes. If a single value is provided, all axes will be set to that value.
        pivot: Pivot that sets the center point of translate and rotate operation. Pivot values are normalized between
            ``[-1, 1]`` for each axis based on the  prim's axis aligned extents.
        rotation: Euler angles in degrees in XYZ order. If a single value is provided, all axes will be set to that
            value.
        look_at: Look-at target, specified either as a ``ReplicatorItem``, a prim path, or world coordinates.
                If multiple prims are set, the target point will be the mean of their positions.
        look_at_up_axis: Look-at up axis of the created prim.
        semantics: Dictionary specifying semantic type and values. Legacy lists of tuples are also accepted but will be
            converted to dictionaries.
        material: Material to attach to the torus.
        visible: If ``False``, the prim will be invisible. This is often useful when creating prims to use as bounds
            with other randomizers.
        count: Number of objects to create.
        name: Name of the object
        parent: Optional parent prim path. The object will be created as a child of this prim.

    Example:
        >>> import omni.replicator.core as rep
        >>> torus = rep.create.torus(
        ...     position=rep.distribution.uniform((0,0,0), (100, 100, 100)),
        ...     scale=2,
        ...     rotation=(45, 45, 0),
        ...     semantics={"class": ["torus"]},
        ... )
    """
    return _create_prim(
        prim_type="Torus",
        position=position,
        pivot=pivot,
        scale=scale,
        rotation=rotation,
        look_at=look_at,
        look_at_up_axis=look_at_up_axis,
        semantics=semantics,
        material=material,
        visible=visible,
        count=count,
        name=name,
        parent=parent,
    )


@ReplicatorWrapper
def disk(
    position: Union[ReplicatorItem, float, Tuple[float]] = None,
    scale: Union[ReplicatorItem, float, Tuple[float]] = None,
    pivot: Union[ReplicatorItem, Tuple[float]] = None,
    rotation: Union[ReplicatorItem, float, Tuple[float]] = None,
    look_at: Union[
        ReplicatorItem,
        str,
        Sdf.Path,
        usdrt.Sdf.Path,
        Tuple[float, float, float],
        List[Union[str, Sdf.Path, usdrt.Sdf.Path]],
    ] = None,
    look_at_up_axis: Union[ReplicatorItem, Tuple[float]] = None,
    semantics: Union[Dict[str, Union[List, str]], List[Tuple[str, str]]] = None,
    material: Union[ReplicatorItem, Usd.Prim] = None,
    visible: bool = True,
    count: int = 1,
    name: Optional[str] = None,
    parent: Union[ReplicatorItem, str, Sdf.Path, Usd.Prim] = None,
) -> ReplicatorItem:
    """Create a disk

    Args:
        position: XYZ coordinates in world space. If a single value is provided, all axes will be set to that value.
        scale: Scaling factors for XYZ axes. If a single value is provided, all axes will be set to that value.
        pivot: Pivot that sets the center point of translate and rotate operation. Pivot values are normalized between
            ``[-1, 1]`` for each axis based on the  prim's axis aligned extents.
        rotation: Euler angles in degrees in XYZ order. If a single value is provided, all axes will be set to that
            value.
        look_at: Look-at target, specified either as a ``ReplicatorItem``, a prim path, or world coordinates.
                If multiple prims are set, the target point will be the mean of their positions.
        look_at_up_axis: Look-at up axis of the created prim.
        semantics: Dictionary specifying semantic type and values. Legacy lists of tuples are also accepted but will be
            converted to dictionaries.
        material: Material to attach to the disk.
        visible: If ``False``, the prim will be invisible. This is often useful when creating prims to use as bounds
            with other randomizers.
        count: Number of objects to create.
        name: Name of the object.
        parent: Optional parent prim path. The object will be created as a child of this prim.

    Example:
        >>> import omni.replicator.core as rep
        >>> disk = rep.create.disk(
        ...     position=rep.distribution.uniform((0,0,0), (100, 100, 100)),
        ...     scale=2,
        ...     rotation=(45, 45, 0),
        ...     semantics={"class": ["disk"]},
        ... )
    """

    return _create_prim(
        prim_type="Disk",
        position=position,
        pivot=pivot,
        scale=scale,
        rotation=rotation,
        look_at=look_at,
        look_at_up_axis=look_at_up_axis,
        semantics=semantics,
        material=material,
        visible=visible,
        count=count,
        name=name,
        parent=parent,
    )


@ReplicatorWrapper
def plane(
    position: Union[ReplicatorItem, float, Tuple[float]] = None,
    scale: Union[ReplicatorItem, float, Tuple[float]] = None,
    pivot: Union[ReplicatorItem, Tuple[float]] = None,
    rotation: Union[ReplicatorItem, float, Tuple[float]] = None,
    look_at: Union[
        ReplicatorItem,
        str,
        Sdf.Path,
        usdrt.Sdf.Path,
        Tuple[float, float, float],
        List[Union[str, Sdf.Path, usdrt.Sdf.Path]],
    ] = None,
    look_at_up_axis: Union[ReplicatorItem, Tuple[float]] = None,
    semantics: Union[Dict[str, Union[List, str]], List[Tuple[str, str]]] = None,
    material: Union[ReplicatorItem, Usd.Prim] = None,
    visible: bool = True,
    count: int = 1,
    name: Optional[str] = None,
    parent: Union[ReplicatorItem, str, Sdf.Path, Usd.Prim] = None,
) -> ReplicatorItem:
    """Create a plane

    Args:
        position: XYZ coordinates in world space. If a single value is provided, all axes will be set to that value.
        scale: Scaling factors for XYZ axes. If a single value is provided, all axes will be set to that value.
        pivot: Pivot that sets the center point of translate and rotate operation. Pivot values are normalized between
            ``[-1, 1]`` for each axis based on the  prim's axis aligned extents.
        rotation: Euler angles in degrees in XYZ order. If a single value is provided, all axes will be set to that
            value.
        look_at: Look-at target, specified either as a ``ReplicatorItem``, a prim path, or world coordinates.
                If multiple prims are set, the target point will be the mean of their positions.
        look_at_up_axis: Look-at up axis of the created prim.
        semantics: Dictionary specifying semantic type and values. Legacy lists of tuples are also accepted but will be
            converted to dictionaries.
        material: Material to attach to the plane.
        visible: If ``False``, the prim will be invisible. This is often useful when creating prims to use as bounds
            with other randomizers.
        count: Number of objects to create.
        name: Name of the object
        parent: Optional parent prim path. The object will be created as a child of this prim.

    Example:
        >>> import omni.replicator.core as rep
        >>> plane = rep.create.plane(
        ...     position=rep.distribution.uniform((0,0,0), (100, 100, 100)),
        ...     scale=2,
        ...     rotation=(45, 45, 0),
        ...     semantics={"class": "plane"},
        ... )
    """
    return _create_prim(
        prim_type="Plane",
        position=position,
        scale=scale,
        pivot=pivot,
        rotation=rotation,
        look_at=look_at,
        look_at_up_axis=look_at_up_axis,
        semantics=semantics,
        material=material,
        visible=visible,
        count=count,
        name=name,
        parent=parent,
    )


@ReplicatorWrapper
def cube(
    position: Union[ReplicatorItem, float, Tuple[float]] = None,
    scale: Union[ReplicatorItem, float, Tuple[float]] = None,
    pivot: Union[ReplicatorItem, Tuple[float]] = None,
    rotation: Union[ReplicatorItem, float, Tuple[float]] = None,
    look_at: Union[
        ReplicatorItem,
        str,
        Sdf.Path,
        usdrt.Sdf.Path,
        Tuple[float, float, float],
        List[Union[str, Sdf.Path, usdrt.Sdf.Path]],
    ] = None,
    look_at_up_axis: Union[ReplicatorItem, Tuple[float]] = None,
    semantics: Union[Dict[str, Union[List, str]], List[Tuple[str, str]]] = None,
    material: Union[ReplicatorItem, Usd.Prim] = None,
    visible: bool = True,
    as_mesh: bool = True,
    count: int = 1,
    name: Optional[str] = None,
    parent: Union[ReplicatorItem, str, Sdf.Path, Usd.Prim] = None,
) -> ReplicatorItem:
    """Create a cube

    Args:
        position: XYZ coordinates in world space. If a single value is provided, all axes will be set to that value.
        scale: Scaling factors for XYZ axes. If a single value is provided, all axes will be set to that value.
        pivot: Pivot that sets the center point of translate and rotate operation. Pivot values are normalized between
            ``[-1, 1]`` for each axis based on the  prim's axis aligned extents.
        rotation: Euler angles in degrees in XYZ order. If a single value is provided, all axes will be set to that
            value.
        look_at: Look-at target, specified either as a ``ReplicatorItem``, a prim path, or world coordinates.
                If multiple prims are set, the target point will be the mean of their positions.
        look_at_up_axis: Look-at up axis of the created prim.
        semantics: Dictionary specifying semantic type and values. Legacy lists of tuples are also accepted but will be
            converted to dictionaries.
        material: Material to attach to the cube.
        visible: If ``False``, the prim will be invisible. This is often useful when creating prims to use as bounds
            with other randomizers.
        as_mesh: If ``False``, create a ``Usd.Cube`` prim. If ``True``, create a mesh.
        count: Number of objects to create.
        name: Name of the object
        parent: Optional parent prim path. The object will be created as a child of this prim.

    Example:
        >>> import omni.replicator.core as rep
        >>> cube = rep.create.cube(
        ...     position=rep.distribution.uniform((0,0,0), (100, 100, 100)),
        ...     scale=2,
        ...     rotation=(45, 45, 0),
        ...     semantics={"class": "cube"},
        ... )
    """
    return _create_prim(
        prim_type="Cube",
        position=position,
        scale=scale,
        pivot=pivot,
        rotation=rotation,
        look_at=look_at,
        look_at_up_axis=look_at_up_axis,
        semantics=semantics,
        material=material,
        visible=visible,
        as_mesh=as_mesh,
        count=count,
        name=name,
        parent=parent,
    )


@ReplicatorWrapper
def cylinder(
    position: Union[ReplicatorItem, float, Tuple[float]] = None,
    scale: Union[ReplicatorItem, float, Tuple[float]] = None,
    pivot: Union[ReplicatorItem, Tuple[float]] = None,
    rotation: Union[ReplicatorItem, float, Tuple[float]] = None,
    look_at: Union[
        ReplicatorItem,
        str,
        Sdf.Path,
        usdrt.Sdf.Path,
        Tuple[float, float, float],
        List[Union[str, Sdf.Path, usdrt.Sdf.Path]],
    ] = None,
    look_at_up_axis: Union[ReplicatorItem, Tuple[float]] = None,
    semantics: Union[Dict[str, Union[List, str]], List[Tuple[str, str]]] = None,
    material: Union[ReplicatorItem, Usd.Prim] = None,
    visible: bool = True,
    as_mesh: bool = True,
    count: int = 1,
    name: Optional[str] = None,
    parent: Union[ReplicatorItem, str, Sdf.Path, Usd.Prim] = None,
) -> ReplicatorItem:
    """Create a cylinder

    Args:
        position: XYZ coordinates in world space. If a single value is provided, all axes will be set to that value.
        scale: Scaling factors for XYZ axes. If a single value is provided, all axes will be set to that value.
        pivot: Pivot that sets the center point of translate and rotate operation. Pivot values are normalized between
            ``[-1, 1]`` for each axis based on the  prim's axis aligned extents.
        rotation: Euler angles in degrees in XYZ order. If a single value is provided, all axes will be set to that
            value.
        look_at: Look-at target, specified either as a ``ReplicatorItem``, a prim path, or world coordinates.
                If multiple prims are set, the target point will be the mean of their positions.
        look_at_up_axis: Look-at up axis of the created prim.
        semantics: Dictionary specifying semantic type and values. Legacy lists of tuples are also accepted but will be
            converted to dictionaries.
        material: Material to attach to the cylinder.
        visible: If ``False``, the prim will be invisible. This is often useful when creating prims to use as bounds
            with other randomizers.
        as_mesh: If ``False``, create a Usd.Cylinder prim. If ``True``, create a mesh.
        count: Number of objects to create.
        name: Name of the object
        parent: Optional parent prim path. The object will be created as a child of this prim.

    Example:
        >>> import omni.replicator.core as rep
        >>> cylinder = rep.create.cylinder(
        ...     position=rep.distribution.uniform((0,0,0), (100, 100, 100)),
        ...     scale=2,
        ...     rotation=(45, 45, 0),
        ...     semantics={"class": "cylinder"},
        ... )
    """
    return _create_prim(
        prim_type="Cylinder",
        position=position,
        scale=scale,
        pivot=pivot,
        rotation=rotation,
        look_at=look_at,
        look_at_up_axis=look_at_up_axis,
        semantics=semantics,
        material=material,
        visible=visible,
        as_mesh=as_mesh,
        count=count,
        name=name,
        parent=parent,
    )


@ReplicatorWrapper
def cone(
    position: Union[ReplicatorItem, float, Tuple[float]] = None,
    scale: Union[ReplicatorItem, float, Tuple[float]] = None,
    pivot: Union[ReplicatorItem, Tuple[float]] = None,
    rotation: Union[ReplicatorItem, float, Tuple[float]] = None,
    look_at: Union[
        ReplicatorItem,
        str,
        Sdf.Path,
        usdrt.Sdf.Path,
        Tuple[float, float, float],
        List[Union[str, Sdf.Path, usdrt.Sdf.Path]],
    ] = None,
    look_at_up_axis: Union[ReplicatorItem, Tuple[float]] = None,
    semantics: Union[Dict[str, Union[List, str]], List[Tuple[str, str]]] = None,
    material: Union[ReplicatorItem, Usd.Prim] = None,
    visible: bool = True,
    as_mesh: bool = True,
    count: int = 1,
    name: Optional[str] = None,
    parent: Union[ReplicatorItem, str, Sdf.Path, Usd.Prim] = None,
) -> ReplicatorItem:
    """Create a cone

    Args:
        position: XYZ coordinates in world space. If a single value is provided, all axes will be set to that value.
        scale: Scaling factors for XYZ axes. If a single value is provided, all axes will be set to that value.
        pivot: Pivot that sets the center point of translate and rotate operation. Pivot values are normalized between
            ``[-1, 1]`` for each axis based on the  prim's axis aligned extents.
        rotation: Euler angles in degrees in XYZ order. If a single value is provided, all axes will be set to that
            value.
        look_at: Look-at target, specified either as a ``ReplicatorItem``, a prim path, or world coordinates.
                If multiple prims are set, the target point will be the mean of their positions.
        look_at_up_axis: Look-at up axis of the created prim.
        semantics: Dictionary specifying semantic type and values. Legacy lists of tuples are also accepted but will be
            converted to dictionaries.
        material: Material to attach to the cone.
        visible: If ``False``, the prim will be invisible. This is often useful when creating prims to use as bounds
            with other randomizers.
        as_mesh: If ``False``, create a ``Usd.Cone`` prim. If ``True``, create a mesh.
        count: Number of objects to create.
        name: Name of the object.
        parent: Optional parent prim path. The object will be created as a child of this prim.

    Example:
        >>> import omni.replicator.core as rep
        >>> cone = rep.create.cone(
        ...     position=rep.distribution.uniform((0,0,0), (100, 100, 100)),
        ...     scale=2,
        ...     rotation=(45, 45, 0),
        ...     semantics={"class": "cone"},
        ... )
    """
    return _create_prim(
        prim_type="Cone",
        position=position,
        scale=scale,
        pivot=pivot,
        rotation=rotation,
        look_at=look_at,
        look_at_up_axis=look_at_up_axis,
        semantics=semantics,
        material=material,
        visible=visible,
        as_mesh=as_mesh,
        count=count,
        name=name,
        parent=parent,
    )


@ReplicatorWrapper
def camera(
    position: Union[ReplicatorItem, float, Tuple[float]] = None,
    rotation: Union[ReplicatorItem, float, Tuple[float]] = None,
    look_at: Union[
        ReplicatorItem,
        str,
        Sdf.Path,
        usdrt.Sdf.Path,
        Tuple[float, float, float],
        List[Union[str, Sdf.Path, usdrt.Sdf.Path]],
    ] = None,
    look_at_up_axis: Union[ReplicatorItem, Tuple[float]] = None,
    focal_length: Union[ReplicatorItem, float] = 24.0,
    focus_distance: Union[ReplicatorItem, float] = 400.0,
    f_stop: Union[ReplicatorItem, float] = 0.0,
    horizontal_aperture: Union[ReplicatorItem, float] = 20.955,
    horizontal_aperture_offset: Union[ReplicatorItem, float] = 0.0,
    vertical_aperture_offset: Union[ReplicatorItem, float] = 0.0,
    clipping_range: Union[ReplicatorItem, Tuple[float, float]] = (1.0, 1000000.0),
    projection_type: Union[ReplicatorItem, str] = "pinhole",
    fisheye_nominal_width: Union[ReplicatorItem, float] = 1936.0,
    fisheye_nominal_height: Union[ReplicatorItem, float] = 1216.0,
    fisheye_optical_centre_x: Union[ReplicatorItem, float] = 970.94244,
    fisheye_optical_centre_y: Union[ReplicatorItem, float] = 600.37482,
    openCV_focal_x: Union[ReplicatorItem, float] = 731.78788,
    openCV_focal_y: Union[ReplicatorItem, float] = 731.78789,
    fisheye_max_fov: Union[ReplicatorItem, float] = 200.0,
    fisheye_polynomial_a: Union[ReplicatorItem, float] = 0.0,
    fisheye_polynomial_b: Union[ReplicatorItem, float] = 0.00245,
    fisheye_polynomial_c: Union[ReplicatorItem, float] = 0.0,
    fisheye_polynomial_d: Union[ReplicatorItem, float] = 0.0,
    fisheye_polynomial_e: Union[ReplicatorItem, float] = 0.0,
    fisheye_polynomial_f: Union[ReplicatorItem, float] = 0.0,
    fisheye_p0: Union[ReplicatorItem, float] = -0.00037,
    fisheye_p1: Union[ReplicatorItem, float] = -0.00074,
    fisheye_s0: Union[ReplicatorItem, float] = -0.00058,
    fisheye_s1: Union[ReplicatorItem, float] = -0.00022,
    fisheye_s2: Union[ReplicatorItem, float] = 0.00019,
    fisheye_s3: Union[ReplicatorItem, float] = -0.0002,
    cross_camera_reference_name: Optional[str] = None,
    count: int = 1,
    parent: Union[ReplicatorItem, str, Sdf.Path, Usd.Prim] = None,
    name: Optional[str] = None,
) -> ReplicatorItem:
    """Create a camera

    Args:
        position: XYZ coordinates in world space. If a single value is provided, all axes will be set to that value.
        rotation: Euler angles in degrees in XYZ order. If a single value is provided, all axes will be set to that
            value.
        look_at: Look-at target, specified either as a ``ReplicatorItem``, a prim path, or world coordinates.
                If multiple prims are set, the target point will be the mean of their positions.
        look_at_up_axis: Look-at up axis of the created prim.
        focal_length: Physical focal length of the camera in units equal to ``0.1 * world units``.
        focus_distance: Distance from the camera to the focus plane in world units.
        f_stop: Lens aperture. Default ``0.0`` turns off focusing.
        horizontal_aperture: Horizontal aperture in units equal to ``0.1 * world units``. Default simulates a 35mm
            spherical projection aperture.
        horizontal_aperture_offset: Horizontal aperture offset in units equal to ``0.1 * world units``.
        vertical_aperture_offset: Vertical aperture offset in units equal to ``0.1 * world units``.
        clipping_range: (Near, Far) clipping distances of the camera in world units.
        projection_type: Camera projection model. Select from ["pinhole", "pinholeOpenCV", "fisheye_polynomial",
            "fisheyeSpherical", "fisheyeKannalaBrandtK3", "fisheyeRadTanThinPrism", "fisheyeOpenCV",
            "omniDirectionalStereo", "generalizedProjection"].
        fisheye_nominal_width: Nominal width of fisheye lens model.
        fisheye_nominal_height: Nominal height of fisheye lens model.
        fisheye_optical_centre_x: Horizontal optical centre position of fisheye lens model.
        fisheye_optical_centre_y: Vertical optical centre position of fisheye lens model.
        openCV_focal_x: Focal x of the openCV camera.
        openCV_focal_y: Focal y of the openCV camera.
        fisheye_max_fov: Maximum field of view of fisheye lens model.
        fisheye_polynomial_a: First polynomial coefficient of fisheye camera.
        fisheye_polynomial_b: Second polynomial coefficient of fisheye camera.
        fisheye_polynomial_c: Third polynomial coefficient of fisheye camera.
        fisheye_polynomial_d: Fourth polynomial coefficient of fisheye camera.
        fisheye_polynomial_e: Fifth polynomial coefficient of fisheye camera.
        fisheye_polynomial_f: Sixth polynomial coefficient of fisheye camera.
        fisheye_p0: Distortion coefficient to calculate tangential distortion for rad tan thin prism camera.
        fisheye_p1: Distortion coefficient to calculate tangential distortion for rad tan thin prism camera.
        fisheye_s0: Distortion coefficient to calculate thin prism distortion for rad tan thin prism camera.
        fisheye_s1: Distortion coefficient to calculate thin prism distortion for rad tan thin prism camera.
        fisheye_s2: Distortion coefficient to calculate thin prism distortion for rad tan thin prism camera.
        fisheye_s3: Distortion coefficient to calculate thin prism distortion for rad tan thin prism camera.,
        count: Number of objects to create.
        parent: Optional parent prim path. The camera will be created as a child of this prim.
        name: Name of the camera

    Example:
        >>> import omni.replicator.core as rep
        >>> # Create camera
        >>> camera = rep.create.camera(
        ...     position=rep.distribution.uniform((0,0,0), (100, 100, 100)),
        ...     rotation=(45, 45, 0),
        ...     focus_distance=rep.distribution.normal(400.0, 100),
        ...     f_stop=1.8,
        ... )
        >>> # Attach camera to render product
        >>> render_product = rep.create.render_product(camera, resolution=(1024, 1024))
    """

    projection_type_split = projection_type.split("_")
    projection_type = "".join(projection_type_split[:1] + [t.capitalize() for t in projection_type_split[1:]])

    if projection_type not in VALID_PROJECTIONS:
        raise ValueError(f"Invalid projection {projection_type}. Select from {VALID_PROJECTIONS}")

    return _create_prim(
        prim_type="Camera",
        position=position,
        rotation=rotation,
        look_at=look_at,
        look_at_up_axis=look_at_up_axis,
        focal_length=UsdAttrMapping("focalLength", focal_length),
        focus_distance=UsdAttrMapping("focusDistance", focus_distance),
        f_stop=UsdAttrMapping("fStop", f_stop),
        horizontal_aperture=UsdAttrMapping("horizontalAperture", horizontal_aperture),
        horizontal_aperture_offset=UsdAttrMapping("horizontalApertureOffset", horizontal_aperture_offset),
        vertical_aperture_offset=UsdAttrMapping("verticalApertureOffset", vertical_aperture_offset),
        clipping_range=UsdAttrMapping("clippingRange", clipping_range),
        projection_type=UsdAttrMapping("cameraProjectionType", projection_type),
        fisheye_nominal_width=UsdAttrMapping("fthetaWidth", fisheye_nominal_width),
        fisheye_nominal_height=UsdAttrMapping("fthetaHeight", fisheye_nominal_height),
        fisheye_optical_centre_x=UsdAttrMapping("fthetaCx", fisheye_optical_centre_x),
        fisheye_optical_centre_y=UsdAttrMapping("fthetaCy", fisheye_optical_centre_y),
        openCV_focal_x=UsdAttrMapping("openCVFx", openCV_focal_x),
        openCV_focal_y=UsdAttrMapping("openCVFy", openCV_focal_y),
        fisheye_max_fov=UsdAttrMapping("fthetaMaxFov", fisheye_max_fov),
        fisheye_polynomial_a=UsdAttrMapping("fthetaPolyA", fisheye_polynomial_a),
        fisheye_polynomial_b=UsdAttrMapping("fthetaPolyB", fisheye_polynomial_b),
        fisheye_polynomial_c=UsdAttrMapping("fthetaPolyC", fisheye_polynomial_c),
        fisheye_polynomial_d=UsdAttrMapping("fthetaPolyD", fisheye_polynomial_d),
        fisheye_polynomial_e=UsdAttrMapping("fthetaPolyE", fisheye_polynomial_e),
        fisheye_polynomial_f=UsdAttrMapping("fthetaPolyF", fisheye_polynomial_f),
        fisheye_p0=UsdAttrMapping("p0", fisheye_p0),
        fisheye_p1=UsdAttrMapping("p1", fisheye_p1),
        fisheye_s0=UsdAttrMapping("s0", fisheye_s0),
        fisheye_s1=UsdAttrMapping("s1", fisheye_s1),
        fisheye_s2=UsdAttrMapping("s2", fisheye_s2),
        fisheye_s3=UsdAttrMapping("s3", fisheye_s3),
        cross_camera_reference_name=UsdAttrMapping("crossCameraReferenceName", cross_camera_reference_name),
        count=count,
        parent=parent,
        name=name,
    )


@ReplicatorWrapper
def tiled_sensor(
    cameras: List[Union[str, ReplicatorItem]],
    camera_resolution: Tuple[int, int],
    tiled_resolution: Tuple[int, int],
    output_types: Optional[List[str]] = None,
    name: Optional[str] = None,
    parent: Union[ReplicatorItem, str, Sdf.Path, Usd.Prim] = None,
):
    """[DEPRECATED] Creates a tiled sensor that takes in a list of camera and outputs a tiled buffer with the output of
    all the cameras.


    Args:
        cameras: List of cameras.
        camera_resolution: Resolution of each sensor (Width, Height)
        tiled_resolution: Total tiled resolution of the output. Must be divisible by the camera_resolution both in x and
            y axes.
        output_types: Output type of the tiled sensor. Currently it supports ["rgb", "depth"]. Default: ["rgb"]
        name: Name of the tiled sensor.
        parent: Optional parent prim path. The sensor will be created as a child of this prim.

    Example:
        >>> import omni.replicator.core as rep
        >>> # Create tiled sensor
        >>> cams = [rep.create.camera() for _ in range(4)]
        >>> sensor = rep.create.tiled_sensor(
        ...     cameras=cams, camera_resolution=(128, 128), tiled_resolution=(256, 256), output_types=["rgb"]
        ... )
        >>> # Attach camera to render product
        >>> render_product = rep.create.render_product(camera=sensor, resolution=(256, 256))  # doctest: +SKIP
    """
    carb.log_warn(
        "RTX Sensor based tiled rendering has been deprecated. For tiled rendering, use "
        "`rep.create.render_product_tiled`."
    )

    if output_types is None:
        output_types = ["rgb"]

    # Check to see if required extension is enabled
    ext_manager = omni.kit.app.get_app_interface().get_extension_manager()
    if ext_manager.is_extension_enabled("omni.sensors.tiled"):
        carb.log_warn("The `tiled_sensor` function requires the `omni.sensors.tiled` extension to function.")

    if tiled_resolution[0] % camera_resolution[0] != 0:
        raise ValueError(
            f"Tiled Resolution {tiled_resolution[0]} in X axis is not divisible by camera resolution "
            f"{camera_resolution[0]} in X axis."
        )

    if tiled_resolution[1] % camera_resolution[1] != 0:
        raise ValueError(
            f"Tiled Resolution {tiled_resolution[1]} in Y axis is not divisible by camera resolution "
            f"{camera_resolution[1]} in Y axis."
        )

    # Sensor is just like a normal camera with different attributes.
    if name:
        sensor = camera(name=name, parent=parent)
    else:
        sensor = camera(name="tiled_sensor", parent=parent)

    sensor_xform_prim = sensor.get_output_prims()["prims"][0]
    sensor_prim = sensor_xform_prim.GetChildren()[0]

    # Create a bridge prim that contains a list of cameras
    # Bridge prim is needed because config and signal strings may not be connected through stage with history/fabric.
    bridge_prim = xform().get_output_prims()["prims"][0]

    sensor_prim.CreateAttribute("sensorModelConfig", Sdf.ValueTypeNames.String).Set(str(bridge_prim.GetPath()))
    sensor_prim.CreateAttribute("sensorModelPluginName", Sdf.ValueTypeNames.String).Set("omni.sensors.tiled.plugin")
    sensor_prim.CreateAttribute("cameraSensorType", Sdf.ValueTypeNames.Token).Set("rtxsensor")

    # Writes camera path to the bridge prim.
    bridge_cam_rel = bridge_prim.CreateRelationship("camPrims")
    bridge_prim.CreateAttribute("cameraResolution", Sdf.ValueTypeNames.Int2).Set(
        Gf.Vec2i(camera_resolution[0], camera_resolution[1])
    )
    bridge_prim.CreateAttribute("tiledResolution", Sdf.ValueTypeNames.Int2).Set(
        Gf.Vec2i(tiled_resolution[0], tiled_resolution[1])
    )

    if not output_types:
        raise ValueError("output_types of tiled sensor cannot be empty or None.")

    allowed_output_types = ["rgb", "depth"]
    for output_type in output_types:
        if output_type not in allowed_output_types:
            raise ValueError(
                f"{output_type} is not supported for tiled sensor. Only {allowed_output_types} are supported."
            )

    bridge_prim.CreateAttribute("outputType", Sdf.ValueTypeNames.StringArray).Set(output_types)

    camera_paths = []
    for cam in cameras:
        if isinstance(cam, (str, Sdf.Path, usdrt.Sdf.Path)) and Sdf.Path.IsValidPathString(str(cam)):
            camera_paths.append(Sdf.Path(str(cam)))
        elif isinstance(cam, ReplicatorItem) and cam.get_output_prims().get("prims"):
            camera_paths.append(cam.get_output_prims()["prims"][0].GetChildren()[0].GetPath())
        elif isinstance(cam, Usd.Prim):
            camera_paths.append(cam.GetPath())
        else:
            raise ValueError(f"Expect cameras to be either ReplicatorItem, str or valid Sdf.Path, but got {type(cam)}.")

    bridge_cam_rel.SetTargets(camera_paths)

    return sensor


def render_product_tiled(
    cameras: List[Union[str, ReplicatorItem]],
    tile_resolution: Tuple[int, int],
    force_new: bool = False,
    name: Optional[str] = None,
) -> viewport_manager.HydraTexture:
    """Creates a single render product to render multiple sensor tiles.

    Creates a render product attached to a list of sensors and outputs a tiled buffer with the output of all attached
    sensors. Tiled rendering is most performant when rendering a large number of sensors at low resolution. Returns a
    ``HydraTexture`` object with resolution equal ``tile_resolution[0] * ceil(sqrt(len(cameras))),
    tile_resolution[1] * ceil(sqrt(len(cameras))``.

    Note: Only a single tiled resolution is allowed per session. Creating more render products with different tiled
    resolution will cause the previous tiled render products to render incorrectly.

    Args:
        cameras: List of cameras to attach to the render product.
        tile_resolution: Resolution of each sensor (Width, Height)
        force_new: If ``True``, force creation of a new render product. If ``False``, existing render products will
            be re-used if currently assigned to same camera and of the same resolution. Is overriden to ``True`` if a
            ``name`` is provided.
        name: Name of the tiled sensor.


    Example:
        >>> import omni.replicator.core as rep
        >>> # Create tiled sensor
        >>> cams = [rep.create.camera() for _ in range(4)]
        >>> tiled_rp = rep.create.render_product_tiled(cameras=cams, tile_resolution=(128, 128))
        >>> # Attach annotators
        >>> anno = rep.annotators.get("distance_to_camera").attach(tiled_rp)
    """
    camera_paths = []
    for cam in cameras:
        if isinstance(cam, ReplicatorItem):
            camera_paths.extend(get_non_xform_prims(cam.get_output("prims")))
        elif isinstance(cam, (str, Sdf.Path, usdrt.Sdf.Path)):
            camera_paths.append(str(cam))
        else:
            raise ValueError(f"Invalid camera `{cam}` found in cameras list: `{cameras}`")

    num_cameras = len(camera_paths)
    carb_settings = carb.settings.get_settings()
    view_tile_limit = carb_settings.get_as_int("/rtx/viewTile/limit")
    if view_tile_limit and view_tile_limit < num_cameras:
        raise ValueError(
            f"Unable to create render product with {num_cameras} tiles due to limit of {view_tile_limit}. "
            "Increase limit specified in carb setting '/rtx/viewTile/limit' or reduce the number of cameras"
        )

    num_tiles_per_side = math.ceil(math.sqrt(num_cameras))

    kit_version, _ = omni.kit.app.get_app().get_kit_version().split("+")
    major, minor, _ = kit_version.split(".")

    if int(major) == 106 and int(minor) < 5:
        full_resolution = (num_tiles_per_side * tile_resolution[0], num_tiles_per_side * tile_resolution[1])
        # Check if tiled settings were previously set
        existing_tile_width = carb_settings.get("/rtx/viewTile/resolution/0") or carb_settings.get(
            "/rtx/viewTile/width"
        )
        existing_tile_height = carb_settings.get("/rtx/viewTile/resolution/1") or carb_settings.get(
            "/rtx/viewTile/height"
        )

        if existing_tile_width and existing_tile_width != tile_resolution[0]:
            setting = (
                "/rtx/viewTile/width" if carb_settings.get("/rtx/viewTile/width") else "/rtx/viewTile/resolution/0"
            )
            carb.log_warn(
                f"Changing `{setting}` from {existing_tile_width} to {tile_resolution[0]} may cause any previously "
                "created tiled render product to render incorrectly"
            )
        if existing_tile_height and existing_tile_height != tile_resolution[1]:
            setting = (
                "/rtx/viewTile/height" if carb_settings.get("/rtx/viewTile/height") else "/rtx/viewTile/resolution/1"
            )
            carb.log_warn(
                f"Changing `{setting}` from {existing_tile_height} to {tile_resolution[1]} may cause any previously "
                "created tiled render product to render incorrectly"
            )

        # Set carb settings
        # Support 106.1
        carb_settings.set("/rtx/viewTile/resolution/0", tile_resolution[0])  # width
        carb_settings.set("/rtx/viewTile/resolution/1", tile_resolution[1])  # height

        # Support 106.2+
        carb_settings.set("/rtx/viewTile/width", tile_resolution[0])  # width
        carb_settings.set("/rtx/viewTile/height", tile_resolution[1])  # height

    elif (int(major) >= 106 and int(minor) >= 5) or int(major) >= 107:
        # NOTE: This MUST match what kit's rendering/source/sharedlibs/rtx.hydra/RtxHydraEngine.cpp  does
        # Use auto tile sizing by setting tile resolution to (0, 0)
        carb_settings.set("/rtx/viewTile/resolution/0", 0)  # width
        carb_settings.set("/rtx/viewTile/resolution/1", 0)  # height

        x_coord = math.floor(tile_resolution[0] * max(1, num_tiles_per_side))
        factor = math.ceil(max(1, num_cameras / max(1, (x_coord / tile_resolution[0]))))
        y_coord = math.floor(tile_resolution[1] * factor)

        # Handle numerical errors resulting in Kit's CEIL increasing tile resolution by 1
        if math.ceil(y_coord / factor) > tile_resolution[1]:
            y_coord -= 1
        full_resolution = (x_coord, y_coord)
    else:
        raise NotImplementedError(f"Tiled rendering is not supported in Kit version '{kit_version}'")

    # Create render product (attach first camera)
    created_rp = render_product(cameras[0], full_resolution, force_new=force_new, name=name)

    # Attach all cameras
    stage = omni.usd.get_context().get_stage()
    rp_prim = stage.GetPrimAtPath(created_rp.path)
    with Usd.EditContext(stage, stage.GetSessionLayer()):
        rp_prim.GetRelationship("camera").SetTargets(camera_paths)

    return created_rp


def stereo_camera(
    stereo_baseline: Union[ReplicatorItem, float],
    position: Union[ReplicatorItem, float, Tuple[float]] = None,
    rotation: Union[ReplicatorItem, float, Tuple[float]] = None,
    look_at: Union[
        ReplicatorItem,
        str,
        Sdf.Path,
        usdrt.Sdf.Path,
        Tuple[float, float, float],
        List[Union[str, Sdf.Path, usdrt.Sdf.Path]],
    ] = None,
    look_at_up_axis: Union[ReplicatorItem, Tuple[float]] = None,
    focal_length: Union[ReplicatorItem, float] = 24.0,
    focus_distance: Union[ReplicatorItem, float] = 400.0,
    f_stop: Union[ReplicatorItem, float] = 0.0,
    horizontal_aperture: Union[ReplicatorItem, float] = 20.955,
    horizontal_aperture_offset: Union[ReplicatorItem, float] = 0.0,
    vertical_aperture_offset: Union[ReplicatorItem, float] = 0.0,
    clipping_range: Union[ReplicatorItem, Tuple[float, float]] = (1.0, 1000000.0),
    projection_type: Union[ReplicatorItem, str] = "pinhole",
    fisheye_nominal_width: Union[ReplicatorItem, float] = 1936.0,
    fisheye_nominal_height: Union[ReplicatorItem, float] = 1216.0,
    fisheye_optical_centre_x: Union[ReplicatorItem, float] = 970.94244,
    fisheye_optical_centre_y: Union[ReplicatorItem, float] = 600.37482,
    fisheye_max_fov: Union[ReplicatorItem, float] = 200.0,
    fisheye_polynomial_a: Union[ReplicatorItem, float] = 0.0,
    fisheye_polynomial_b: Union[ReplicatorItem, float] = 0.00245,
    fisheye_polynomial_c: Union[ReplicatorItem, float] = 0.0,
    fisheye_polynomial_d: Union[ReplicatorItem, float] = 0.0,
    fisheye_polynomial_e: Union[ReplicatorItem, float] = 0.0,
    fisheye_polynomial_f: Union[ReplicatorItem, float] = 0.0,
    fisheye_p0: Union[ReplicatorItem, float] = -0.00037,
    fisheye_p1: Union[ReplicatorItem, float] = -0.00074,
    fisheye_s0: Union[ReplicatorItem, float] = -0.00058,
    fisheye_s1: Union[ReplicatorItem, float] = -0.00022,
    fisheye_s2: Union[ReplicatorItem, float] = 0.00019,
    fisheye_s3: Union[ReplicatorItem, float] = -0.0002,
    count: int = 1,
    name: Optional[str] = None,
    parent: Union[ReplicatorItem, str, Sdf.Path, Usd.Prim] = None,
) -> ReplicatorItem:
    """Create a stereo camera pair.

    Args:
        stereo_baseline: Distance between stereo camera pairs.
        position: XYZ coordinates in world space. If a single value is provided, all axes will be set to that value.
        rotation: Euler angles in degrees in XYZ order. If a single value is provided, all axes will be set to that
            value.
        look_at: Look-at target, specified either as a ``ReplicatorItem``, a prim path or as coordinates.
            If multiple prims are set, the target point will be the mean of their positions.
        look_at_up_axis: Look-at up axis of the created prim.
        focal_length: Physical focal length of the camera in units equal to ``0.1 * world units``.
        focus_distance: Distance from the camera to the focus plane in world units.
        f_stop: Lens aperture. Default ``0.0`` turns off focusing.
        horizontal_aperture: Horizontal aperture in units equal to ``0.1 * world units``. Default simulates a 35mm
            spherical projection aperture.
        horizontal_aperture_offset: Horizontal aperture offset in units equal to ``0.1 * world units``.
        vertical_aperture_offset: Vertical aperture offset in units equal to ``0.1 * world units``.
        clipping_range: (Near, Far) clipping distances of the camera in world units.
        projection_type: Camera projection model. Select from ["pinhole", "fisheye_polynomial","fisheyeSpherical",
            fisheyeKannalaBrandtK3", "fisheyeRadTanThinPrism", "fisheyeOpenCV", "generalizedProjection"].
        fisheye_nominal_width: Nominal width of fisheye lens model.
        fisheye_nominal_height: Nominal height of fisheye lens model.
        fisheye_optical_centre_x: Horizontal optical centre position of fisheye lens model.
        fisheye_optical_centre_y: Vertical optical centre position of fisheye lens model.
        fisheye_max_fov: Maximum field of view of fisheye lens model.
        fisheye_polynomial_a: 1st component of fisheye polynomial (only valid for fisheye_polynomial projection type).
        fisheye_polynomial_b: 2nd component of fisheye polynomial (only valid for fisheye_polynomial projection type).
        fisheye_polynomial_c: 3rd component of fisheye polynomial (only valid for fisheye_polynomial projection type).
        fisheye_polynomial_d: 4th component of fisheye polynomial (only valid for fisheye_polynomial projection type).
        fisheye_polynomial_e: 5th component of fisheye polynomial (only valid for fisheye_polynomial projection type).
        count: Number of objects to create.
        name: Name of the cameras. ``_L`` and ``_R`` will be appended for Left and Right cameras, respectively.
        parent: Optional parent prim path. The cameras will be created as a child of this prim.

    Example:
        >>> import omni.replicator.core as rep
        >>> # Create stereo camera
        >>> stereo_camera_pair = rep.create.stereo_camera(
        ...     stereo_baseline=10,
        ...     position=(10, 10, 10),
        ...     rotation=(45, 45, 0),
        ...     focus_distance=rep.distribution.normal(400.0, 100),
        ...     f_stop=1.8,
        ... )
        >>> # Attach camera to render product
        >>> render_product = rep.create.render_product(stereo_camera_pair, resolution=(1024, 1024))
    """
    if name is None:
        name = "StereoCam"
    parent_xforms = xform(
        position=position,
        rotation=rotation,
        count=count,
        name=name,
        parent=parent,
    )
    parent_xform_paths = parent_xforms.node.get_attribute("outputs:prims").get()
    stage = omni.usd.get_context().get_stage()
    up_axis = UsdGeom.GetStageUpAxis(stage)

    if up_axis.lower() == "y":
        left_position = (-stereo_baseline / 2, 0.0, 0.0)
        right_position = (stereo_baseline / 2, 0.0, 0.0)
    else:
        left_position = (0.0, -stereo_baseline / 2, 0.0)
        right_position = (0.0, stereo_baseline / 2, 0.0)

    # Cross correspondence only available for fisheye polynomial projection
    do_cross_corr = projection_type == "fisheye_polynomial"

    for parent_path in parent_xform_paths:
        # Left camera
        _ = camera(
            position=left_position,
            parent=parent_path,
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
            cross_camera_reference_name=f"{name}_R" if do_cross_corr else None,
            name=f"{name}_L" if name else None,
        )

        # Right camera
        _ = camera(
            parent=parent_path,
            position=right_position,
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
            cross_camera_reference_name=f"{name}_L" if do_cross_corr else None,
            name=f"{name}_R" if name else None,
        )
    # Do this after camera creation so camera rotation with Z axis up can be taken into account
    with parent_xforms:
        modify.pose(look_at=look_at, look_at_up_axis=look_at_up_axis)
    return parent_xforms


@ReplicatorWrapper
def light(
    position: Union[ReplicatorItem, float, Tuple[float]] = None,
    scale: Union[ReplicatorItem, float, Tuple[float]] = None,
    rotation: Union[ReplicatorItem, float, Tuple[float]] = None,
    look_at: Union[
        ReplicatorItem,
        str,
        Sdf.Path,
        usdrt.Sdf.Path,
        Tuple[float, float, float],
        List[Union[str, Sdf.Path, usdrt.Sdf.Path]],
    ] = None,
    look_at_up_axis: Union[ReplicatorItem, Tuple[float]] = None,
    light_type: str = "Distant",
    color: Union[ReplicatorItem, Tuple[float, float, float]] = (1.0, 1.0, 1.0),
    intensity: Union[ReplicatorItem, float] = 1000.0,
    exposure: Union[ReplicatorItem, float] = None,
    temperature: Union[ReplicatorItem, float] = 6500,
    texture: Union[ReplicatorItem, str] = None,
    count: int = 1,
    name: Optional[str] = None,
    parent: Union[ReplicatorItem, str, Sdf.Path, Usd.Prim] = None,
) -> ReplicatorItem:
    """Create a light

    Args:
        position: XYZ coordinates in world space. If a single value is provided, all axes will be set to that value.
            Ignored for dome and distant light types.
        scale: Scaling factors for XYZ axes. If a single value is provided, all axes will be set to that value.
            Ignored for dome and distant light types.
        rotation: Euler angles in degrees in XYZ order. If a single value is provided, all axes will be set to that
            value.
        look_at: Look-at target, specified either as a ``ReplicatorItem``, a prim path, or world coordinates.
            If multiple prims are set, the target point will be the mean of their positions.
        look_at_up_axis: Look-at up axis of the created prim.
        light_type: Light type. Select from ["cylinder", "disk", "distant", "dome", "rect", "sphere"]
        color: Light color in (R,G,B). Float values from ``[0.0-1.0]``
        intensity: Light intensity. Scales the power of the light linearly.
        exposure: Scales the power of the light exponentially as a power of 2. The result is multiplied with
            ``intensity``.
        temperature: Color temperature in degrees Kelvin indicating the white point. Lower values are warmer,
            higher values are cooler. Valid range ``[1000-10000]``.
        texture: Image texture to use for dome light such as an HDR (High Dynamic Range) intended for IBL (Image Based
            Lighting). Ignored for other light types.
        count: Number of objects to create.
        name: Name of the light.
        parent: Optional parent prim path. The object will be created as a child of this prim.

    Examples:
        >>> import omni.replicator.core as rep
        >>> distance_light = rep.create.light(
        ...     rotation=rep.distribution.uniform((0,-180,-180), (0,180,180)),
        ...     intensity=rep.distribution.normal(10000, 1000),
        ...     temperature=rep.distribution.normal(6500, 1000),
        ...     light_type="distant"
        ... )
        >>> dome_light = rep.create.light(
        ...     rotation=rep.distribution.uniform((0,-180,-180), (0,180,180)),
        ...     texture=rep.distribution.choice(rep.example.TEXTURES),
        ...     light_type="dome"
        ... )
    """
    assert light_type.lower() in ["cylinder", "disk", "distant", "dome", "rect", "sphere"]

    if isinstance(color, list):
        color = tuple(color)

    enable_temperature = temperature is not None

    if texture is not None:
        # If in RaytracedLighting, minimum RTSubframes=3 is required
        render_mode = carb.settings.get_settings().get("/rtx/rendermode")
        rt_subframes = carb.settings.get_settings().get("/omni/replicator/RTSubframes")
        if render_mode == "RaytracedLighting" and (rt_subframes is None or rt_subframes < 3):
            carb.log_warn(
                "`/omni/replicator/RTSubframes` must be > 3 to avoid blank textures while randomizing dome "
                f"light texture. RTSubframes has been automatically increased from {rt_subframes} to 3"
            )
            carb.settings.get_settings().set("/omni/replicator/RTSubframes", 3)

    return _create_prim(
        prim_type=f"{light_type.capitalize()}Light",
        position=position,
        scale=scale,
        rotation=rotation,
        look_at=look_at,
        semantics=None,
        look_at_up_axis=look_at_up_axis,
        color=color,
        intensity=intensity,
        exposure=exposure,
        texture=UsdAttrMapping("texture:file", texture),
        color_temperature=UsdAttrMapping("colorTemperature", temperature),
        enable_color_temperature=UsdAttrMapping("enableColorTemperature", enable_temperature),
        count=count,
        name=name,
        parent=parent,
    )


# TODO Refactor this function (too-complex), or move to C++ if performance is an issue
def render_product(  # noqa: C901  # ignore complexity linting error
    camera: Union[ReplicatorItem, str, List[str], Sdf.Path, List[Sdf.Path], usdrt.Usd.Prim, List[usdrt.Usd.Prim]],
    resolution: Tuple[int, int],
    force_new: bool = False,
    name: Union[str, List[str]] = None,
    render_vars: List[str] = None,
) -> Union[str, List]:
    """Create a render product
    A RenderProduct describes images or other file-like artifacts produced by a render, such as rgb (``LdrColor``),
    normals, depth, etc. If an existing render product exists that have the same resolution and camera attached, it is
    returned. If no matching render product is found or if ``force_new`` is set to `True`, a new render product is
    created.

    By default, the following render variables are automatically created for each render product:
    - LdrColor (RGB): The final rendered image
    - Depth: Linear depth from camera
    - InstanceSegmentation: Instance segmentation mask
    - SemanticSegmentation: Semantic segmentation mask
    - WorldPosition: World space position of each pixel
    - WorldNormals: World space normals
    - MotionVectors: Motion vectors for temporal effects

    Note: When using Viewport 2.0, viewports are not generated to draw the render product on screen.
    Note: Render products can utilize a large amount of VRAM. Render Products no longer in use should be destroyed.

    Args:
        camera: The camera prim (pxr.Usd.Camera) or OmniSensor to attach to the render product. If a list of cameras is
            provided, a list of render products is created.
        resolution: (width, height) resolution of the render product
        force_new: If ``True``, force creation of a new render product. If ``False``, existing render products will
            be re-used if currently assigned to same camera and of the same resolution. Is overriden to ``True`` if a
            ``name`` is provided.
        name: Optionally specify the name(s) of the render product(s). Name must produce a valid USD path. If no
            ``name`` is provided, defaults to ``Replicator``. The render product will be created at the following path
            within the Session Layer: ``/Render/<render product prefix><name>`` where ``<render product prefix>`` is
            ``HydraTextures/`` by default. If multiple cameras are provided or if a render product of the specified
            ``name`` already exists, a ``_<num>`` suffix is added starting at ``_01``. If specifying unique names for
            multiple cameras, ``name`` can be supplied as a list of strings of the same length as ``camera``.
        render_vars: List of custom render variables to create. Valid options include:
            ["GenericModelOutput", "RtxSensorCpu", "RtxSensorGpu", "RtxSensorMetadata"].
            If None, default render variables are created.
    Example:
        >>> import omni.replicator.core as rep
        >>> render_product = rep.create.render_product(
        ...     rep.create.camera(), resolution=(1024, 1024), name="MyRenderProduct"
        ... )
        >>> # Create render product with custom render variables
        >>> render_product = rep.create.render_product(
        ...     rep.create.camera(), resolution=(1024, 1024),
        ...     render_vars=["GenericModelOutput", "RtxSensorMetadata"]
        ... )
    """
    _telemetry = Schema_omni_replicator_extinfo_1_0()
    if not isinstance(resolution, (tuple, list)) or len(resolution) != 2:
        raise TypeError(f"Type {type(resolution)} is invalid. Specify resolution in format `(width: int, height: int)`")

    if not isinstance(camera, list):
        camera = [camera]

    if name is not None:
        force_new = True
        if not Tf.IsValidIdentifier(name):
            old_name = name
            name = Tf.MakeValidIdentifier(name)
            carb.log_warn(f"{{{old_name}}} is an invalid name.  Renaming to {{{name}}}.")

    resolution = (int(resolution[0]), int(resolution[1]))

    # Ensure render_vars is always a list when provided.
    if render_vars is not None and not isinstance(render_vars, list):
        render_vars = [render_vars]

    def attach_render_products(sensor_paths, names):
        sensor_paths = get_non_xform_prims(sensor_paths)
        if not sensor_paths:
            raise ValueError("No valid sensor paths provided")

        if not isinstance(names, list):
            names = [names] * len(sensor_paths)

        if len(names) != len(sensor_paths):
            raise ValueError(
                f"Got {len(sensor_paths)} sensors and {len(names)} names. Please ensure same number of sensors and "
                "names are provided."
            )

        if all(n is None for n in names) and len(sensor_paths) == 2 and all("StereoCam" in c for c in sensor_paths):
            names = []
            for sensor_path in sensor_paths:
                stereo_pos = sensor_path.split("_")[-1]
                names.append(f"Replicator_{stereo_pos}")

        render_products = []
        for name, sensor_path in zip(names, sensor_paths):
            sensor_path = str(sensor_path)  # Convert usdrt.UdsPath objects to str
            stage = omni.usd.get_context().get_stage()
            sensor_prim = stage.GetPrimAtPath(sensor_path)
            if not sensor_prim.IsValid():
                raise ValueError(f"Sensor prim {sensor_path} is not valid")

            render_prod = viewport_manager.get_render_product(sensor_path, resolution, force_new, name)

            # Create render variables if specified
            with Usd.EditContext(stage, stage.GetSessionLayer()):
                if render_vars is not None:
                    render_vars_path = "/Render/Vars"

                    # Ensure the Render/Vars path exists
                    if not stage.GetPrimAtPath(render_vars_path):
                        stage.DefinePrim(render_vars_path, "Scope")

                    # Create render variables for each AOV
                    for aov in render_vars:
                        render_var_path = f"{render_vars_path}/{aov}"
                        if not stage.GetPrimAtPath(render_var_path).IsValid():
                            render_var = stage.DefinePrim(render_var_path, "RenderVar")
                            render_var.CreateAttribute("sourceName", Sdf.ValueTypeNames.String).Set(aov)

                        rp_prim = stage.GetPrimAtPath(render_prod.path)
                        ordered_vars = rp_prim.GetRelationship("orderedVars")
                        ordered_vars.AddTarget(render_var_path)

                # If this is an OmniSensor and no render vars specified, set up a GenericModelOutput AOV by default
                elif render_vars is None and sensor_prim.IsA("OmniSensor"):
                    render_var_path = "/Render/Vars/GenericModelOutput"
                    if not stage.GetPrimAtPath(render_var_path).IsValid():
                        stage.DefinePrim(render_var_path, "RenderVar")
                        render_var = stage.DefinePrim(render_var_path, "RenderVar")
                        render_var.CreateAttribute("sourceName", Sdf.ValueTypeNames.String).Set("GenericModelOutput")
                    rp_prim = stage.GetPrimAtPath(render_prod.path)
                    ordered_vars = rp_prim.GetRelationship("orderedVars")
                    ordered_vars.ClearTargets(True)
                    ordered_vars.SetTargets([render_var_path])

            render_products.append(render_prod)
            _telemetry.renderproduct_sendEvent(int(resolution[0]), int(resolution[1]))
        if len(render_products) == 1:
            return render_products[0]

        return render_products

    async def get_sensor_paths_async(sensors, names):
        sensor_paths = []
        for sensor in sensors:
            while not sensor.get_outputs().get("prims") and sensor.node.get_compute_count() == 0:
                await omni.kit.app.get_app().next_update_async()

            paths = [str(p) for p in sensor.get_output("prims")]
            if not paths:
                raise ValueError(f"Unable to get sensor path from {sensor}")
            sensor_paths.extend(paths)

        return attach_render_products(sensor_paths, names)

    # Set the omni/replicator/totalRenderProductPixels variable
    # TODO this is not value for multiple render products
    carb.settings.get_settings().set_int(
        "omni/replicator/totalRenderProductPixels", min(100000000, resolution[0] * resolution[1])
    )

    if all(isinstance(cam, ReplicatorItem) for cam in camera):
        if all(cam.get_outputs().get("prims") for cam in camera):
            sensor_paths = []
            for cam in camera:
                sensor_paths.extend(cam.get_output("prims"))
            return attach_render_products(sensor_paths, name)

        return omni.kit.async_engine.run_coroutine(get_sensor_paths_async(camera, name))

    sensor_paths = []
    for sensor in camera:
        if isinstance(sensor, (str, Sdf.Path, usdrt.Sdf.Path)):
            sensor_paths.append(str(sensor))
        elif isinstance(sensor, (usdrt.Usd.Prim, pxr.Usd.Prim)):
            sensor_paths.append(str(sensor.GetPath()))
        else:
            raise ValueError(f"Unable to get sensor path from {sensor}")

    return attach_render_products(sensor_paths, name)


@ReplicatorWrapper
def from_usd(
    usd: str,
    position: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    scale: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    rotation: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    look_at: Union[
        str,
        Sdf.Path,
        Usd.Prim,
        Tuple[float, float, float],
        List[Union[str, Sdf.Path, Usd.Prim, Tuple[float, float, float]]],
    ] = None,
    look_at_up_axis: Union[Tuple[float]] = None,
    semantics: Union[Dict[str, Union[List, str]], List[Tuple[str, str]]] = None,
    count: int = 1,
    name: Optional[str] = None,
    parent: Union[str, Sdf.Path, Usd.Prim] = None,
) -> ReplicatorItem:
    r"""Reference a USD into the current USD stage.

    Args:
        usd: Path to a usd file (``\*.usd``, ``\*.usdc``, ``\*.usda``)
        semantics: Dictionary specifying semantic type and values. Legacy lists of tuples are also accepted but will be
            converted to dictionaries.

    Example:
        >>> import omni.replicator.core as rep
        >>> usd_path = rep.example.ASSETS[0]
        >>> asset = rep.create.from_usd(usd_path, semantics={"class": "example"})
    """
    return _create_prim(
        prim_type="Reference",
        usd_path=usd,
        semantics=semantics,
        count=count,
        name=name or "Ref",
        parent=parent,
        position=position,
        scale=scale,
        rotation=rotation,
        look_at=look_at,
        look_at_up_axis=look_at_up_axis,
    )


@ReplicatorWrapper
def group(
    items: List[Union[ReplicatorItem, str, Sdf.Path]],
    semantics: Union[Dict[str, Union[List, str]], List[Tuple[str, str]]] = None,
    name=None,
) -> ReplicatorItem:
    """Group assets into a common node.
    Grouping assets makes it easier and faster to apply randomizations to multiple assets simultaneously.

    Args:
        items: Assets to be grouped together.
        semantics: Dictionary specifying semantic type and values. Legacy lists of tuples are also accepted but will be
            converted to dictionaries.
        name (optional): A name for the given group node

    Example:
        >>> import omni.replicator.core as rep
        >>> cones = [rep.create.cone() for _ in range(100)]
        >>> group = rep.create.group(cones, semantics={"class": "cone"})
    """
    # TODO handle all arguments
    prim_paths = []
    prim_nodes = []
    for item in items:
        if isinstance(item, (str, Sdf.Path)):
            prim_paths.append(item)
        elif isinstance(item, ReplicatorItem):
            if "prims" in item.outputs and all(
                item.node.get_attribute(f"inputs:{item_in}").get_upstream_connection_count() == 0
                for item_in in item.inputs
            ):
                # If node has no upstream exec, assume static inputs, get paths directly for better perf
                prim_paths.extend(item.get_output("prims"))
            else:
                prim_nodes.append(item.node)
        else:
            raise ValueError(f"Item of type {type(item)} must be ReplicatorItem or string.")
    node = create_node("omni.replicator.core.OgnGroup", node_name=name)
    # Use enumerate to avoid manual index manipulation and comply with linting rule SIM113.
    start_idx = 0
    if prim_paths:
        og.AttributeValueHelper(node.get_attribute("inputs:primsIn")).set(prim_paths, update_usd=True)
        start_idx = 1
    for idx, prim_node in enumerate(prim_nodes, start=start_idx):
        suffix = "" if idx == 0 else idx
        prim_node.get_attribute("outputs:prims").connect(node.get_attribute(f"inputs:primsIn{suffix}"), True)
    if semantics:
        stage = omni.usd.get_context().get_stage()
        prims = [stage.GetPrimAtPath(str(p)) for p in node.get_attribute("outputs:prims").get()]
        F.modify.semantics(prims, semantics)
    return node


def from_dir(
    dir_path: str,
    recursive: bool = False,
    path_filter: str = None,
    semantics: Union[Dict[str, Union[List, str]], List[Tuple[str, str]]] = None,
) -> ReplicatorItem:
    """Create a group of assets from the USD files found in `dir_path`

    Args:
        dir_path: The root path to search from.
        recursive: If ``True``, search through sub-folders.
        path_filter: A Regular Expression (RegEx) string to filter paths with.
        semantics: Dictionary specifying semantic type and values. Legacy lists of tuples are also accepted but will be
            converted to dictionaries.

    Example:
        >>> import omni.replicator.core as rep
        >>> asset_path = rep.example.ASSETS_DIR
        >>> asset = rep.create.from_dir(asset_path, path_filter="rocket")
    """
    usd_paths = get_usd_files(dir_path, recursive=recursive, path_filter=path_filter)
    if len(usd_paths) == 0:
        raise ValueError(f"No valid usd files found at: {dir_path}")
    stage = omni.usd.get_context().get_stage()
    xform_paths = []
    for usd_path in usd_paths:
        xform_path = omni.usd.get_stage_next_free_path(stage, f"{REPLICATOR_SCOPE}/Ref_Xform", False)
        xform = stage.DefinePrim(xform_path, "Xform")
        UsdGeom.Xformable(xform).AddTranslateOp()
        UsdGeom.Xformable(xform).AddRotateXYZOp()
        UsdGeom.Xformable(xform).AddScaleOp()
        prim_path = f"{xform_path}/Ref"
        ref = stage.DefinePrim(prim_path)
        ref.GetReferences().AddReference(usd_path)
        if semantics:
            F.modify.semantics(ref, semantics)
        xform_paths.append(xform_path)
    return group(xform_paths)


@ReplicatorWrapper
def material_omnipbr(
    diffuse: Tuple[float] = None,
    diffuse_texture: str = None,
    roughness: float = None,
    roughness_texture: str = None,
    metallic: float = None,
    metallic_texture: str = None,
    specular: float = None,
    emissive_color: Tuple[float] = None,
    emissive_texture: str = None,
    emissive_intensity: float = 0.0,
    project_uvw: bool = False,
    semantics: Union[Dict[str, Union[List, str]], List[Tuple[str, str]]] = None,
    count: int = 1,
) -> ReplicatorItem:
    """Create an OmniPBR Material

    Args:
        diffuse: Diffuse/albedo color in RGB colorspace
        diffuse_texture: Path to diffuse texture
        roughness: Material roughness in the range ``[0, 1]``
        roughness_texture: Path to roughness texture
        metallic: Material metallic value in the range ``[0, 1]``. Typically, metallic is assigned either ``0.0`` or
            ``1.0``
        metallic_texture: Path to metallic texture
        specular: Intensity of specular reflections in the range ``[0, 1]``
        emissive_color: Color of emissive light emanating from material in RGB colorspace
        emissive_texture: Path to emissive texture
        emissive_intensity: Emissive intensity of the material. Setting to ``0.0`` (default) disables emission.
        project_uvw: When ``True``, UV coordinates will be generated by projecting them from a coordinate system.
        semantics: Assign semantics to material
        count: Number of objects to create.

    Example:
        >>> import omni.replicator.core as rep
        >>> mat1 = rep.create.material_omnipbr(
        ...    diffuse=rep.distribution.uniform((0, 0, 0), (1, 1, 1)),
        ...    roughness=rep.distribution.uniform(0, 1),
        ...    metallic=rep.distribution.choice([0, 1]),
        ...    emissive_color=rep.distribution.uniform((0, 0, 0.5), (0, 0, 1)),
        ...    emissive_intensity=rep.distribution.uniform(0, 1000),
        ... )
        >>> mat2 = rep.create.material_omnipbr(
        ...    diffuse_texture=rep.distribution.choice(rep.example.TEXTURES),
        ...    roughness_texture=rep.distribution.choice(rep.example.TEXTURES),
        ...    metallic_texture=rep.distribution.choice(rep.example.TEXTURES),
        ...    emissive_texture=rep.distribution.choice(rep.example.TEXTURES),
        ...    emissive_intensity=rep.distribution.uniform(0, 1000),
        ... )
        >>> cone = rep.create.cone(material=mat1)
        >>> torus = rep.create.torus(material=mat2)
    """
    return _create_prim(
        prim_type="Material",
        mdl="OmniPBR.mdl",
        name="OmniPBR",
        diffuse_color_constant=diffuse,
        diffuse_texture=diffuse_texture,
        reflection_roughness_constant=roughness,
        reflectionroughness_texture=roughness_texture,
        metallic_constant=metallic,
        metallic_texture=metallic_texture,
        specular_level=specular,
        enable_emission=any(e is not None for e in [emissive_color, emissive_texture, emissive_intensity]),
        emissive_color=emissive_color,
        emissive_color_texture=emissive_texture,
        emissive_intensity=emissive_intensity,
        project_uvw=project_uvw,
        semantics=semantics,
        count=count,
    )


@ReplicatorWrapper
def mdl_from_json(material_def: Dict = None, material_def_path: str = None) -> ReplicatorItem:
    """Create a MDL ShaderGraph material defined in a json dictionary.

    Args:
        material_def: A dictionary object defining the MDL material graph.
        material_def_path: A path to a json file to decode and generate an MDL material graph from.

    Example:
        >>> import omni.replicator.core as rep
        >>> gen_mat = rep.create.mdl_from_json(material_def=rep.example.MDL_JSON_EXAMPLE)
        >>> cube = rep.create.cube(material=gen_mat)
    """

    if material_def is None and material_def_path is None:
        raise ValueError("Must provide a material definition dictionary or path to a material definition dictionary!")

    if material_def_path and not material_def and Path(material_def_path).exists():
        try:
            with open(material_def_path, encoding="utf-8") as file:
                material_def = json.load(file)
        except json.decoder.JSONDecodeError as err:
            raise ValueError(f"Failed to decode provided material definition json! \n {err}") from err
    elif material_def_path and not material_def:
        raise ValueError(f"{material_def_path} does not exist!")

    mat_gen = MaterialGraphGenerator(material_def)
    gen_mat_path = mat_gen.create_graph()
    material_group = group([gen_mat_path])
    return material_group.node


@ReplicatorWrapper
def projection_material(
    proxy_prim: Union[ReplicatorItem, str, Sdf.Path],
    semantics: Union[Dict[str, Union[List, str]], List[Tuple[str, str]]] = None,
    material: Union[ReplicatorItem, str, Sdf.Path] = None,
    offset_scale: float = 0.01,
    input_prims: Union[ReplicatorItem, List[str]] = None,
    name: Optional[str] = None,
) -> ReplicatorItem:
    """Project a texture onto a target prim.

    ``ProjectPBRMaterial`` is used to facilitate these projections. The proxy prim is a prim used to control the
    position, rotation and scale of the projection. There can only be one proxy/projection pair, so a proxy prim can
    only modify a single projection.
    The projection will happen in the direction of the negative x-axis. This node only sets up the
    projection material, the ``rep.modify.projection_material`` node should be used to update the projection itself.

    Args:
        proxy_prim: The prims which will be used to manipulate the projection.
        material: Projection material to apply to the projection. If not provided, use 'ProjectPBRMaterial'.
        semantics: Semantics to apply to the defect.
        offset_scale: Scale factor when extruding ``target_prim`` points.
        input_prims: The prim which will be projected on to. If using ``with`` syntax, this argument can be omitted.
        name (optional): A name for the given projection node.

    Example:
        >>> import omni.replicator.core as rep
        >>> torus = rep.create.torus()
        >>> cube = rep.create.cube(position=(50, 100, 0), rotation=(0, 0, 90), scale=(0.2, 0.2, 0.2))
        >>> sem = [('class', 'shape')]
        >>> with torus:
        ...     rep.create.projection_material(cube, sem)
        omni.replicator.core.create.projection_material
    """
    if isinstance(semantics, list):
        semantics = utils.legacy_semantics_arg_to_new(semantics)
    node = create_node(
        "omni.replicator.core.OgnCreateProjectionMaterial",
        semantics=str(semantics),
        offsetScale=offset_scale,
        node_name=name,
    )

    if isinstance(proxy_prim, ReplicatorItem):
        if proxy_prim.node.get_attribute_exists("outputs:prims"):
            utils._connect_prims(node, "inputs:proxyPrim", proxy_prim)
    elif isinstance(proxy_prim, (str, Sdf.Path, usdrt.Sdf.Path)) and Sdf.IsValidPathString(str(proxy_prim)):
        proxy_prim = Sdf.Path(proxy_prim)
        node.get_attribute("inputs:proxyPrim").set(str(proxy_prim))
    else:
        raise ValueError(f"Invalid `proxy_prim` provided: {proxy_prim}")

    if material:
        if isinstance(material, ReplicatorItem):
            if material.node.get_attribute_exists("outputs:prims"):
                utils._connect_prims(node, "inputs:materialPrim", material)
        elif isinstance(material, (str, Sdf.Path, usdrt.Sdf.Path)) and Sdf.IsValidPathString(str(material)):
            material = Sdf.Path(material)
            node.get_attribute("inputs:materialPrim").set(str(material))
        else:
            raise ValueError(f"Invalid `material` provided: {material}")

    if input_prims:
        node.get_attribute("inputs:prims").set([str(ip) for ip in input_prims])

    return node


@ReplicatorWrapper
def mesh_decal(  # noqa: C901  # ignore complexity linting error
    decal: Union[ReplicatorItem, str, Sdf.Path] = None,
    material: Union[ReplicatorItem, str, Sdf.Path] = None,
    texture_group: Union[ReplicatorItem, List[str]] = None,
    diffuse: Union[ReplicatorItem, str] = None,
    normal: Union[ReplicatorItem, str] = None,
    roughness: Union[ReplicatorItem, str] = None,
    metallic: Union[ReplicatorItem, str] = None,
    opacity: Union[ReplicatorItem, str] = None,
    semantics: Union[Dict[str, Union[List, str]], List[Tuple[str, str]]] = None,
    position: Union[ReplicatorItem, Gf.Vec3d, str] = (0, 0, 0),
    rotation: Union[ReplicatorItem, Gf.Vec3d, str] = (0, 0, 0),
    scale: Union[ReplicatorItem, Gf.Vec3d, str] = (1, 1, 1),
    offset_normal: float = 0.1,
    offset_depth: float = 0.0,
    input_prims: Union[ReplicatorItem, List[str]] = None,
    name: Optional[str] = None,
) -> ReplicatorItem:
    """Create a mesh decal target prim. The decal mesh is projected on to the target mesh in the -Z direction.

    Args:
        decal (optional): Decal mesh to modify can be provided, otherwise a new decal mesh will be created and modified
            as a child of the target prim.
        material (optional): Apply this custom material to the decal, otherwise an OmniPBR will be created.
        texture_group (optional): Set the diffuse, normal, roughness, and/or metallic texture simultaniously. Use where
            there are diffuse, normal, roughness, and/or metallic textures in a set. If using this arg, the diffuse,
            normal, roughness and/or metallic args should be set to the suffix used to denote each type.
        diffuse: Set the diffuse texture used on the mesh decal material. If using with texture_group, set to suffix
            used.
        normal: Set the normal texture used on the mesh decal material. If using with texture_group, set to suffix used.
        roughness: Set the roughness texture used on the mesh decal material. If using with texture_group, set to suffix
            used.
        metallic: Set the metallic texture used on the mesh decal material. If using with texture_group, set to suffix
            used.
        opacity: Set the opacity texture used on the mesh decal material. If using with texture_group, set to suffix
            used.
        semantics (optional): Semantics to apply to the defect.
        position: Manually update the position of the decal.
        rotation: Manually update the rotation of the decal.
        scale: Manually update the scale of the decal.
        offset_normal: Offset along the normal of the decal.
        offset_depth: Offset depth of the decal.
        input_prims: The prim which will have the decal. If using `with` syntax, this argument can be omitted.
        name (optional): A name for the given node.

    Example:
        >>> import omni.replicator.core as rep
        >>> torus = rep.create.torus()
        >>> sem = {"class": "decal"}
        >>> with torus:
        ...     rep.create.mesh_decal(
        ...         semantics=sem,
        ...         texture_group=rep.utils.get_files_group(rep.example.UV_TEXTURES_DIR, ['_D', '_O']),
        ...         position=(50, 30, 25),
        ...         rotation=(-90, 0, 0),
        ...         scale=(0.2, 0.2, 0.5),
        ...         diffuse="_D",
        ...         opacity="_O"
        ...     )
        omni.replicator.core.create.mesh_decal
    """
    if isinstance(semantics, list):
        semantics = utils.legacy_semantics_arg_to_new(semantics)
    node = create_node(
        "omni.replicator.core.OgnMeshDecal",
        semantics=str(semantics),
        offsetNormal=offset_normal,
        offsetDepth=offset_depth,
        node_name=name,
    )

    if decal:
        if isinstance(decal, ReplicatorItem):
            if decal.node.get_attribute_exists("outputs:prims"):
                utils._connect_prims(node, "inputs:decalPrim", decal)
        elif isinstance(decal, (str, Sdf.Path, usdrt.Sdf.Path)) and Sdf.IsValidPathString(str(decal)):
            decal = Sdf.Path(decal)
            node.get_attribute("inputs:decalPrim").set(str(decal))
        else:
            raise ValueError(f"Invalid `decal` provided: {decal}")

    if material:
        if isinstance(material, ReplicatorItem):
            if material.node.get_attribute_exists("outputs:prims"):
                utils._connect_prims(node, "inputs:materialPrim", material)
        elif isinstance(material, (str, Sdf.Path, usdrt.Sdf.Path)) and Sdf.IsValidPathString(str(material)):
            material = Sdf.Path(material)
            node.get_attribute("inputs:materialPrim").set(str(material))
        else:
            raise ValueError(f"Invalid `material` provided: {material}")

    if texture_group:
        if not isinstance(texture_group, ReplicatorItem):
            texture_group = choice(texture_group)
        texture_group.node.get_attribute("outputs:samples").connect(node.get_attribute("inputs:textureGroup"), True)

    if diffuse:
        node.get_attribute("inputs:diffuse").set(diffuse)

    if normal:
        node.get_attribute("inputs:normal").set(normal)

    if roughness:
        node.get_attribute("inputs:roughness").set(roughness)

    if metallic:
        node.get_attribute("inputs:metallic").set(metallic)

    if opacity:
        node.get_attribute("inputs:opacity").set(opacity)

    if position:
        if not isinstance(position, ReplicatorItem):
            node.get_attribute("inputs:position").set(position)
        else:
            # Check that there is a position output from upstream node first, i.e. OgnMeshBoundsDecalPlacement
            if position.node.get_attribute_exists("outputs:position"):
                position.node.get_attribute("outputs:position").connect(node.get_attribute("inputs:position"), True)
            else:
                position.node.get_attribute("outputs:samples").connect(node.get_attribute("inputs:position"), True)

    if rotation:
        if not isinstance(rotation, ReplicatorItem):
            node.get_attribute("inputs:rotation").set(rotation)
        else:
            # Check that there is a rotation output from upstream node first, i.e. OgnMeshBoundsDecalPlacement
            if rotation.node.get_attribute_exists("outputs:rotation"):
                rotation.node.get_attribute("outputs:rotation").connect(node.get_attribute("inputs:rotation"), True)
            else:
                rotation.node.get_attribute("outputs:samples").connect(node.get_attribute("inputs:rotation"), True)

    if scale:
        if not isinstance(scale, ReplicatorItem):
            node.get_attribute("inputs:scale").set(scale)
        else:
            # Check that there is a scale output from upstream node first, i.e. OgnMeshBoundsDecalPlacement
            if scale.node.get_attribute_exists("outputs:scale"):
                scale.node.get_attribute("outputs:scale").connect(node.get_attribute("inputs:scale"), True)
            else:
                scale.node.get_attribute("outputs:samples").connect(node.get_attribute("inputs:scale"), True)

    if input_prims:
        utils.set_target_prims(node, "inputs:prims", input_prims)

    return node


@ReplicatorWrapper
def omni_lidar(
    position: Union[ReplicatorItem, float, Tuple[float]] = None,
    rotation: Union[ReplicatorItem, float, Tuple[float]] = None,
    count: int = 1,
    name: str = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    **kwargs,
) -> ReplicatorItem:
    """Create a LiDAR sensor.

    Args:
        position: XYZ coordinates in world space. If a single value is provided, all axes will be set to that value.
        rotation: Euler angles in degrees in XYZ order. If a single value is provided, all axes will be set to that
            value.
        count: Number of LiDAR sensors to create.
        name: Name of the LiDAR sensor.
        parent: Parent prim for the LiDAR sensor.
        **kwargs: Additional attributes to be added to the LiDAR sensor

    Example:
        >>> import omni.replicator.core as rep
        >>> # Create LiDAR sensor
        >>> lidar = rep.create.omni_lidar(
        ...     position=rep.distribution.uniform((0,0,0), (100, 100, 100)),
        ...     rotation=(45, 45, 0),
        ... )
        >>> # Attach LiDAR to render product
        >>> render_product = rep.create.render_product(lidar, resolution=(1024, 1024))  # doctest: +SKIP
    """
    # Create the LiDAR sensor
    return _create_prim(
        prim_type="OmniLidar",
        position=position,
        rotation=rotation,
        count=count,
        name=name,
        parent=parent,
        prim_create_fn=F.create_batch.omni_lidar,
        **kwargs,
    )


@ReplicatorWrapper
def omni_radar(
    position: Union[ReplicatorItem, float, Tuple[float]] = None,
    rotation: Union[ReplicatorItem, float, Tuple[float]] = None,
    count: int = 1,
    name: str = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    **kwargs,
) -> ReplicatorItem:
    """Create a Radar sensor.

    Args:
        position: XYZ coordinates in world space. If a single value is provided, all axes will be set to that value.
        rotation: Euler angles in degrees in XYZ order. If a single value is provided, all axes will be set to that
            value.
        count: Number of Radar sensors to create.
        name: Name of the Radar sensor.
        parent: Parent prim for the Radar sensor.
        **kwargs: Additional attributes to be added to the Radar sensor

    Example:
        >>> import omni.replicator.core as rep
        >>> # Create Radar sensor
        >>> radar = rep.create.omni_radar(
        ...     position=rep.distribution.uniform((0,0,0), (100, 100, 100)),
        ...     rotation=(45, 45, 0),
        ... )
        >>> # Attach Radar to render product
        >>> render_product = rep.create.render_product(radar, resolution=(1024, 1024))  # doctest: +SKIP
    """
    # Create the Radar sensor
    return _create_prim(
        prim_type="OmniRadar",
        position=position,
        rotation=rotation,
        count=count,
        name=name,
        parent=parent,
        prim_create_fn=F.create_batch.omni_radar,
        **kwargs,
    )
