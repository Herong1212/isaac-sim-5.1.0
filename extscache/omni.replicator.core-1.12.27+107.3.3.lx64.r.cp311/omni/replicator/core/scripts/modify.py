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

# pylint: disable=too-many-lines,protected-access

import sys
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import carb
import numpy as np
import omni.graph.core as og
import omni.usd
import usdrt
from omni.usd._impl.utils import get_prim_at_path
from pxr import Sdf, UsdGeom

from .distribution import choice, uniform
from .utils import ReplicatorItem, ReplicatorWrapper, create_node, sequential, set_target_prims, utils
from .utils.viewport_manager import HydraTexture


def register(  # pylint: disable=invalid-name
    fn: Callable[..., Union[ReplicatorItem, og.Node]], override: bool = True, fn_name: str = None
) -> None:
    """Register a new function under ``omni.replicator.core.modify``.
    Extend the default capabilities of ``omni.replicator.core.modify`` by registering new functionality. New functions
    must return a ``ReplicatorItem`` or an ``OmniGraph`` node.

    Args:
        fn: A function that returns a ``ReplicatorItem`` or an ``OmniGraph`` node.
        override: If ``True``, will override existing functions of the same name. If ``False``, an error is raised.
        fn_name: Optional arg that let user choose the function name when registering it in replicator. If not
            specified, the function name is used. ``fn_name`` must follow valid [Python identifier rules]
            (https://docs.python.org/3.10/reference/lexical_analysis.html#identifiers)
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
            print(f"Overriding function {{{fn_name}}} for replicator.modify.")
        else:
            raise ValueError()

    wrapped_fn = ReplicatorWrapper(fn)
    setattr(sys.modules[__name__], fn_name, wrapped_fn)


@ReplicatorWrapper
def semantics(  # pylint: disable=redefined-outer-name
    semantics: Optional[Union[Dict[str, str], List[Tuple[str, str]]]] = None,
    input_prims: Union[ReplicatorItem, List[str]] = None,
    mode: str = "add",
) -> ReplicatorItem:
    """Add semantics to the target prims

    Args:
        semantics: ``TYPE,VALUE`` pairs of semantic labels to include on the prim. (Ex: ('class', 'sphere'))
        input_prims: The prims to be modified. If using ``with`` syntax, this argument can be omitted.
        mode: Semantics modification mode. Select from [``add``, ``replace``, ``clear``].
            In ``add`` mode, semantic labels are added to the prim, labels with the same ``TYPE:VALUE`` will be skipped.
            (eg. ``class:car, class:sedan`` -> ``class:car, class:sedan, class:automobile``).
            In ``replace`` mode, the semantics ``VALUE`` specified will replace any existing value of the same semantic
            ``TYPE`` (eg. ``class:car, class:sedan, subclass:emergency`` -> ``class:automobile, subclass:emergency``).
            In ``clear`` mode, **ALL** existing semantics are cleared before adding the specified semantics.
            (eg. ``class:car, subclass:emergency, region:usa`` -> ``class:automobile``).

    Example:
        >>> import omni.replicator.core as rep
        >>> with rep.create.sphere():
        ...     rep.modify.semantics([("class", "sphere")])
        omni.replicator.core.modify.semantics
    """
    valid_modes = ["add", "replace", "clear"]
    if mode.lower() not in valid_modes:
        raise ValueError(f"Invalid mode `{mode}`. Select from {valid_modes}")

    # Normalize the semantics input into a dictionary format
    if isinstance(semantics, str):
        semantics = dict([s.split(":") for s in semantics.split(";")])  # Legacy semantics format
    elif isinstance(semantics, tuple):
        semantics = {semantics[0]: semantics[1]}
    if isinstance(semantics, list):
        semantics = utils.legacy_semantics_arg_to_new(semantics)

    if isinstance(semantics, dict):
        node = create_node("omni.replicator.core.OgnWriteSemantics", semantics_values=str(semantics), mode=mode.lower())
    elif isinstance(semantics, ReplicatorItem):
        node = create_node("omni.replicator.core.OgnWriteSemantics", mode=mode.lower())
        utils._setup_random_attribute(node, input_name="semantics", attribute_value=semantics, prim_path=None)
    elif semantics is None:
        node = create_node("omni.replicator.core.OgnWriteSemantics", mode=mode.lower())
    else:
        raise ValueError(
            f"Invalid semantics format `{semantics}`. Semantics should be specified as a dictionary "
            "in the form `{<type>: [<value0>, <value1>]}`"
        )

    if input_prims:
        set_target_prims(node, "inputs:prims", input_prims)
    return node


@ReplicatorWrapper
def pose(
    position: Union[ReplicatorItem, float, Tuple[float]] = None,
    position_x: Union[ReplicatorItem, float] = None,
    position_y: Union[ReplicatorItem, float] = None,
    position_z: Union[ReplicatorItem, float] = None,
    rotation: Union[ReplicatorItem, float, Tuple[float]] = None,
    rotation_x: Union[ReplicatorItem, float] = None,
    rotation_y: Union[ReplicatorItem, float] = None,
    rotation_z: Union[ReplicatorItem, float] = None,
    rotation_order: str = "XYZ",
    scale: Union[ReplicatorItem, float, Tuple[float]] = None,
    size: Union[ReplicatorItem, float, Tuple[float]] = None,
    pivot: Union[ReplicatorItem, Tuple[float]] = None,
    look_at: Union[
        ReplicatorItem,
        str,
        Sdf.Path,
        usdrt.Sdf.Path,
        Tuple[float, float, float],
        List[Union[str, Sdf.Path, usdrt.Sdf.Path]],
    ] = None,
    look_at_up_axis: Union[str, Tuple[float, float, float]] = None,
    input_prims: Union[ReplicatorItem, List[str]] = None,
    name: Optional[str] = None,
) -> ReplicatorItem:
    """Modify the position, rotation, scale, and/or look-at target of the prims specified in ``input_prims``.

    Args:
        position: XYZ coordinates in world space.
        position_x: coordinates value along the x axis.
        position_y: coordinates value along the y axis.
        position_z: coordinates value along the z axis.
        rotation: Rotation in degrees for the axes specified in ``rotation_order``.
        rotation_x: Rotation in degrees for the X axis.
        rotation_y: Rotation in degrees for the Y axis.
        rotation_z: Rotation in degrees for the Z axis.
        rotation_order: Order of rotation. Select from [XYZ, XZY, YXZ, YZX, ZXY, ZYX]
        scale: Scale factor for each of XYZ axes.
        size: Desired size of the input prims. Each input prim is scaled to match the specified ``size`` extents in
            each of the XYZ axes.
        pivot: Pivot that sets the center point of translate and rotate operation.
        look_at: The look at target to orient towards specified as either a ``ReplicatorItem``, a prim path, or world
            coordinates. If multiple prims are set, the target point will be the mean of their positions.
        look_at_up_axis: The up axis used in look_at function
        input_prims: The prims to be modified. If using ``with`` syntax, this argument can be omitted.
        name (optional): A name for the graph node.

    .. note::
        * ``position`` and  any of (``position_x``, ``position_y``, and ``position_z``) cannot both be specified.
        * ``rotation`` and ``look_at`` cannot both be specified.
        * ``size`` and ``scale`` cannot both be specified.
        * ``size`` is converted to scale based on the prim's current axis-aligned bounding box size. If a scale is
          already applied, it might not be able to reflect the true size of the prim.

    Example:
        >>> import omni.replicator.core as rep
        >>> with rep.create.cube():
        ...     rep.modify.pose(position=rep.distribution.uniform((0, 0, 0), (100, 100, 100)),
        ...                     scale=rep.distribution.uniform(0.1, 10),
        ...                     look_at=(0, 0, 0))
        omni.replicator.core.modify.pose
    """
    with sequential():
        if position is not None:
            if position_x is not None or position_y is not None or position_z is not None:
                raise ValueError(
                    "Position and any of position_x, position_y and position_z cannot be specified at the same time. "
                    "Please choose one."
                )
            position = _per_axis_pose(
                attribute="position", full_value=position, input_prims=input_prims, node_name=name
            )
            _position(position, input_prims)

        if position_x is not None or position_y is not None or position_z is not None:
            position = _per_axis_pose(
                attribute="position", x=position_x, y=position_y, z=position_z, input_prims=input_prims, node_name=name
            )
            _position(position, input_prims)

        if pivot is not None:
            _pivot(pivot, input_prims)

        if rotation is not None:
            if rotation_x is not None or rotation_y is not None or rotation_z is not None:
                raise ValueError(
                    "Rotation and any of rotation_x, rotation_y and rotation_z cannot be specified at the same time. "
                    "Please choose one."
                )
            rotation = _per_axis_pose(attribute="rotation", full_value=rotation, input_prims=input_prims)
            _rotation(rotation, rotation_order, input_prims)

        if rotation_x is not None or rotation_y is not None or rotation_z is not None:
            rotation = _per_axis_pose(
                attribute="rotation", x=rotation_x, y=rotation_y, z=rotation_z, input_prims=input_prims
            )
            _rotation(rotation, rotation_order, input_prims)

        if scale is not None:
            if size is not None:
                raise ValueError("Scale and size cannot be specified at the same time. Please choose one.")
            _scale(scale, input_prims)

        if size is not None:
            scale = _size_to_scale(size, input_prims)
            _scale(scale, input_prims)

        if look_at is not None:
            if rotation is not None:
                raise ValueError("Rotation of prim was set to be randomized but look_at_target was also specified.")
            look_at_node = _look_at(look_at, look_at_up_axis, input_prims)
            _rotation(look_at_node, "XYZ", input_prims)


@ReplicatorWrapper
def _per_axis_pose(  # pylint: disable=invalid-name,redefined-outer-name
    attribute: str,
    full_value: Union[ReplicatorItem, float] = None,
    x: Union[ReplicatorItem, float] = None,
    y: Union[ReplicatorItem, float] = None,
    z: Union[ReplicatorItem, float] = None,
    input_prims: Union[ReplicatorItem, List[str]] = None,
    node_name: Optional[str] = None,
) -> ReplicatorItem:
    """Modify the value on single axis.

    Args:
        attribute: attribute name that is being modified.
        full_value: Full values on all axes. Cannot co-exist with any of the per axis value.
        x: Value on the x axis. Defaults to None.
        y: Value on the x axis. Defaults to None.
        z: Value on the x axis. Defaults to None.
        input_prims: The prims to be modified. If using ``with`` syntax, this argument can be omitted.
    """
    node = create_node("omni.replicator.core.OgnPerAxisPose", mode=attribute, node_name=f"{node_name or ''}PerAxisPose")

    if full_value is not None:
        if not isinstance(full_value, ReplicatorItem):
            full_value = uniform(full_value, full_value)
        utils._setup_random_attribute(
            write_node=node, attribute_value=full_value, prim_path=input_prims, input_name="fullValues"
        )

    if x is not None:
        if not isinstance(x, ReplicatorItem):
            x = uniform(x, x)
        utils._setup_random_attribute(write_node=node, attribute_value=x, prim_path=input_prims, input_name="xValue")

    if y is not None:
        if not isinstance(y, ReplicatorItem):
            y = uniform(y, y)
        utils._setup_random_attribute(write_node=node, attribute_value=y, prim_path=input_prims, input_name="yValue")

    if z is not None:
        if not isinstance(z, ReplicatorItem):
            z = uniform(z, z)
        utils._setup_random_attribute(write_node=node, attribute_value=z, prim_path=input_prims, input_name="zValue")

    if input_prims:
        set_target_prims(node, "inputs:prims", input_prims)

    return node


@ReplicatorWrapper
def pose_camera_relative(
    camera: Union[ReplicatorItem, List[str]],
    render_product: ReplicatorItem,
    distance: float,
    horizontal_location: float = 0,
    vertical_location: float = 0,
    input_prims=None,
) -> ReplicatorItem:
    """Modify the positions of the prim relative to a camera.

    Args:
        camera: Camera that the prim is relative to.
        horizontal_location: Horizontal location in the camera space, which is in the range ``[-1, 1]``.
        vertical_location: Vertical location in the camera space, which is in the range ``[-1, 1]``.
        distance: Distance from the prim to the camera.
        input_prims: The prims to be modified. If using ``with`` syntax, this argument can be omitted.

    Example:
        >>> import omni.replicator.core as rep
        >>> camera = rep.create.camera()
        >>> render_product = rep.create.render_product(camera, (1024, 512))
        >>> with rep.create.cube():
        ...     rep.modify.pose_camera_relative(
        ...         camera, render_product, distance=500, horizontal_location=0, vertical_location=0
        ...     )
        omni.replicator.core.modify.pose_camera_relative
    """
    with sequential():
        # Wrap the node with ReplicatorItem
        obj_position = _camera_relative_position(
            camera, render_product, horizontal_location, vertical_location, distance, input_prims
        )

        # Modify the position
        _position(obj_position, input_prims)


@ReplicatorWrapper
def _camera_relative_position(
    camera: Union[ReplicatorItem, str],
    render_product: Union[ReplicatorItem, str, HydraTexture],
    horizontal_location: Union[ReplicatorItem, float],
    vertical_location: Union[ReplicatorItem, float],
    distance: Union[ReplicatorItem, float],
    input_prims=None,
) -> ReplicatorItem:
    """Convert the camera relative position to world coordinates.

    Args:
        camera: Camera that the prim is relative to.
        horizontal_location: Horizontal location in the camera space, which is in the range ``[-1, 1]``.
        vertical_location: Vertical location in the camera space, which is in the range ``[-1, 1]``.
        distance: Distance from the prim to the camera.
        input_prims: The prims to be modified. If using ``with`` syntax, this argument can be omitted.

    Return:
        (og.Node): Node containing the value of world coordinates.
    """
    if isinstance(render_product, list):
        carb.log_warn(
            "Multiple render products provided. The camera relative position will be calculated based on the first "
            "render product."
        )
        render_product = render_product[0]
        carb.log_warn(
            "camera_relative_position takes in a single render product but received multiple."
            f"Using the first render product {render_product}"
        )

    if isinstance(render_product, (str, Sdf.Path, usdrt.Sdf.Path)):
        if not Sdf.Path.IsValidPathString(str(render_product)):
            raise ValueError(f"Received Invalid render product path `{render_product}`")
    elif not isinstance(render_product, HydraTexture):
        raise ValueError(f"Received Invalid render product `{render_product}` of type {type(render_product)}")

    if isinstance(render_product, HydraTexture):
        render_product = render_product.path

    render_product = get_prim_at_path(Sdf.Path(render_product))

    width, height = render_product.GetAttribute("resolution").Get()

    node = create_node("omni.replicator.core.OgnCameraRelativePosition", width=width, height=height, numSamples=1)

    if not isinstance(horizontal_location, ReplicatorItem):
        horizontal_location = uniform(horizontal_location, horizontal_location)

    if not isinstance(vertical_location, ReplicatorItem):
        vertical_location = uniform(vertical_location, vertical_location)

    if not isinstance(distance, ReplicatorItem):
        distance = uniform(distance, distance)

    utils._setup_random_attribute(
        write_node=node, attribute_value=horizontal_location, prim_path=input_prims, input_name="horizontalLocation"
    )
    utils._setup_random_attribute(
        write_node=node, attribute_value=vertical_location, prim_path=input_prims, input_name="verticalLocation"
    )
    utils._setup_random_attribute(
        write_node=node, attribute_value=distance, prim_path=input_prims, input_name="distance"
    )

    if isinstance(camera, (str, Sdf.Path, usdrt.Sdf.Path)):
        camera_prim_path = str(camera)
    elif isinstance(camera, ReplicatorItem):
        camera_prim_path = str(camera.get_output("prims")[0])
    else:
        raise ValueError(f"camera expects a string, Sdf.Path or ReplicatorItem, got {type(camera)}")

    # Special case if the camera is a stereo camera pair.
    if camera_prim_path.rsplit("/", maxsplit=1)[-1].startswith("Stereo"):
        # By default, set relative to left_camera
        set_target_prims(node, "inputs:cameraPrim", str(camera_prim_path) + "/StereoCam_L_Xform")
    else:
        set_target_prims(node, "inputs:cameraPrim", camera)

    return node


# TODO Refactor this function (too-complex), or move to C++ if performance is an issue
@ReplicatorWrapper
def _look_at(  # noqa: C901  # ignore complexity linting error
    target: Union[
        ReplicatorItem,
        str,
        Sdf.Path,
        usdrt.Sdf.Path,
        Tuple[float, float, float],
        List[Union[str, Sdf.Path, usdrt.Sdf.Path]],
    ],
    up_axis: Union[ReplicatorItem, str, Tuple[float, float, float]] = None,
    input_prims: Union[ReplicatorItem, List[str]] = None,
) -> ReplicatorItem:
    """Modify the orientation of the prims specified in ``input_prims`` to look at the specified target.
       NOTE: When the look_at vector is align with the up_axis, a small offset need to be applied to
       the position of the prims in order to get the correct value of the rotation. If Y is the stage's up axis, the
       new eye will be `eye + (0, 0, EPS)`. If Z is the stage's up axis, the new eye will be `eye + (EPS, 0, 0)`, where
       eye is the position of the input prims

    Args:
        target: The target to orient towards. If multiple prims are set, the target point will be the mean of their
            positions.
        up_axis: The up axis of the input prims. If it is ``None``, the stage's up axis will be used.
        input_prims: The prims to be modified. If using ``with`` syntax, this argument can be omitted.

    Example:
        >>> import omni.replicator.core as rep
        >>> target = rep.create.sphere(position=(10, 0, 0))
        >>> with rep.create.camera():
        ...     rep.modify._look_at(
        ...         target=target,
        ... )
        omni.replicator.core.modify._look_at
    """
    look_at_node = create_node("omni.replicator.core.OgnLookAt")

    if isinstance(up_axis, ReplicatorItem):
        if up_axis.node.get_attribute_exists("inputs:numSamples"):
            og.AttributeValueHelper(up_axis.node.get_attribute("inputs:numSamples")).set(1, update_usd=True)
        utils.auto_connect(up_axis.node, look_at_node, mapping=[utils.AttrMap("outputs:samples", "inputs:upAxis")])
    else:
        if isinstance(up_axis, str):
            up_axis_lower = up_axis.lower()
            if up_axis_lower == "x":
                up_axis = (1, 0, 0)
            elif up_axis_lower == "y":
                up_axis = (0, 1, 0)
            elif up_axis_lower == "z":
                up_axis = (0, 0, 1)
            else:
                raise ValueError(f"The up axis can either be X, Y or Z, but got {up_axis}")
        elif isinstance(up_axis, (tuple, list)):
            if len(up_axis) != 3:
                raise ValueError(f"The up axis must be length of 3, but got {len(up_axis)}.")
        elif up_axis is None:
            stage = omni.usd.get_context().get_stage()
            if UsdGeom.GetStageUpAxis(stage) == "Z":
                up_axis = (0, 0, 1)
            else:
                up_axis = (0, 1, 0)
        else:
            raise ValueError(f"The type of up axis must be either str or tuple, but got {type(up_axis)}.")

        og.AttributeValueHelper(look_at_node.get_attribute("inputs:upAxis")).set(up_axis, update_usd=True)

    if isinstance(target, ReplicatorItem):
        if (
            target.node.get_attribute_exists("outputs:prims")
            or target.node.get_attribute_exists("outputs_prims")
            or target.node.get_attribute_exists("outputs_primsBundle")
        ):
            utils._connect_prims(look_at_node, "inputs:targetPrim", target)
        # Choice and sequence node
        elif target.node.get_attribute_exists("inputs:choices") or target.node.get_attribute_exists("inputs:items"):
            # If target output, tie up with targetPrim
            if target.node.get_attribute("outputs:samples").get_resolved_type().get_ogn_type_name() == "target":
                utils.auto_connect(
                    target.node, look_at_node, mapping=[utils.AttrMap("outputs:samples", "inputs:targetPrim")]
                )
            # Otherwise, output must be coordinates
            else:
                utils.auto_connect(
                    target.node, look_at_node, mapping=[utils.AttrMap("outputs:samples", "inputs:target")]
                )
        else:
            if target.node.get_attribute_exists("inputs:numSamples"):
                og.AttributeValueHelper(target.node.get_attribute("inputs:numSamples")).set(1, update_usd=True)
            utils.auto_connect(target.node, look_at_node, mapping=[utils.AttrMap("outputs:samples", "inputs:target")])

    elif hasattr(target, "__iter__"):
        if isinstance(target, str) or isinstance(target[0], (Sdf.Path, str, usdrt.Sdf.Path, ReplicatorItem)):
            set_target_prims(look_at_node, "inputs:targetPrim", target)
        else:
            og.AttributeValueHelper(look_at_node.get_attribute("inputs:target")).set(target, update_usd=True)
    else:
        raise ValueError(f"Unable to get coordinates from target of type {type(target)}")

    # WAR for multiple prims limitations
    if input_prims:
        set_target_prims(look_at_node, "inputs:prims", input_prims)

    return look_at_node


@ReplicatorWrapper
def _position(position: ReplicatorItem, input_prims: Union[ReplicatorItem, List[str]] = None) -> ReplicatorItem:
    """Modify the position of the prims specified in ``input_prims``.

    Args:
        position: XYZ coordinates in world space.
        input_prims: The prims to be modified. If using ``with`` syntax, this argument can be omitted.

    Example:
        >>> import omni.replicator.core as rep
        >>> cube = rep.create.cube()
        >>> with cube:
        ...     rep.modify._position(rep.distribution.uniform((0, 0, 0), (100, 100, 100)))
        omni.replicator.core.modify._position
    """
    if isinstance(position, ReplicatorItem):
        node = create_node(
            "omni.replicator.core.OgnWritePrimAttribute", attribute="xformOp:translate", attributeType="double3"
        )
        utils._setup_random_attribute(write_node=node, attribute_value=position, prim_path=input_prims)
    else:
        # Still creating a distr node because we don't want to dynamically set the resolved type.
        distr_node = uniform(position, position)
        node = create_node(
            "omni.replicator.core.OgnWritePrimAttribute", attribute="xformOp:translate", attributeType="double3"
        )
        utils._setup_random_attribute(write_node=node, attribute_value=distr_node, prim_path=input_prims)
    if input_prims:
        set_target_prims(node, "inputs:prims", input_prims)

    return node


@ReplicatorWrapper
def _pivot(pivot: ReplicatorItem, input_prims: Union[ReplicatorItem, List[str]] = None) -> ReplicatorItem:
    """Modify the pivot point of the prims specified in ``input_prims``.
       NOTE: Setting pivot only works on xform prim.

    Args:
        pivot: Pivot that sets the center point of translate and rotate operation. Pivot values are normalized between
            ``[-1, 1]`` for each axis based on the  prim's axis aligned extents. When it's in the range of (-1, 1),
            it means the pivot point is inside the bounding box of the object.
        input_prims: The prims to be modified. If using ``with`` syntax, this argument can be omitted.

    Example:
        >>> import omni.replicator.core as rep
        >>> cube = rep.create.cube()
        >>> with cube:
        ...     rep.modify._pivot(rep.distribution.uniform((-1, -1, -1), (1, 1, 1)))
        omni.replicator.core.modify._pivot
    """
    if isinstance(pivot, ReplicatorItem):
        node = create_node("omni.replicator.core.OgnSetPivot")
        utils._setup_random_attribute(write_node=node, attribute_value=pivot, prim_path=input_prims, input_name="pivot")
    else:
        distr_node = uniform(pivot, pivot)
        node = create_node("omni.replicator.core.OgnSetPivot")
        utils._setup_random_attribute(
            write_node=node, attribute_value=distr_node, prim_path=input_prims, input_name="pivot"
        )
    if input_prims:
        set_target_prims(node, "inputs:prims", input_prims)
    return node


@ReplicatorWrapper
def _scale(scale: ReplicatorItem, input_prims: Union[ReplicatorItem, List[str]] = None) -> ReplicatorItem:
    """Modify the scale of the prims specified in ``input_prims``.

    Args:
        scale: Scale factor for each of XYZ axes.
        input_prims: The prims to be modified. If using ``with`` syntax, this argument can be omitted.

    Example:
        >>> import omni.replicator.core as rep
        >>> cube = rep.create.cube()
        >>> with cube:
        ...     rep.modify._scale(rep.distribution.uniform(1, 5))
        omni.replicator.core.modify._scale
    """
    if isinstance(scale, ReplicatorItem):
        node = create_node(
            "omni.replicator.core.OgnWritePrimAttribute", attribute="xformOp:scale", attributeType="double3"
        )
        utils._setup_random_attribute(write_node=node, attribute_value=scale, prim_path=input_prims)
    else:
        # Still creating a distr node because we don't want to dynamically set the resolved type.
        distr_node = uniform(scale, scale)
        node = create_node(
            "omni.replicator.core.OgnWritePrimAttribute", attribute="xformOp:scale", attributeType="double3"
        )
        utils._setup_random_attribute(write_node=node, attribute_value=distr_node, prim_path=input_prims)
    if input_prims:
        set_target_prims(node, "inputs:prims", input_prims)
    return node


@ReplicatorWrapper
def _size_to_scale(size: ReplicatorItem, input_prims: Union[ReplicatorItem, List[str]] = None) -> ReplicatorItem:
    """Convert the size to scale for ``input_prims``.

    Args:
        size: Desired size of the input prims. Each input prim is scaled to match the specified ``size`` extents in
            each of the XYZ axes.
        input_prims: The prims to be modified. If using ``with`` syntax, this argument can be omitted.

    Return:
        (og.Node): Node containing the desired scale, given the size.
    """
    if not isinstance(size, ReplicatorItem):
        size = uniform(size, size)

    node = create_node("omni.replicator.core.OgnSizeToScale", numSamples=1)
    utils._setup_random_attribute(write_node=node, attribute_value=size, prim_path=input_prims, input_name="size")

    if input_prims:
        set_target_prims(node, "inputs:prims", input_prims)

    return node


@ReplicatorWrapper
def _rotation(
    rotation: ReplicatorItem, rotation_order: str = "XYZ", input_prims: Union[ReplicatorItem, List[str]] = None
) -> ReplicatorItem:
    """Modify the rotation of the prims specified in ``input_prims``.

    Args:
        rotation: Rotation in degrees for the axes specified in `rotation_order`
        rotation_order: Order of rotation. Select from [XYZ, XZY, YXZ, YZX, ZXY, ZYX]
        input_prims: The prims to be modified. If using ``with`` syntax, this argument can be omitted.

    Example:
        >>> import omni.replicator.core as rep
        >>> cube = rep.create.cube()
        >>> with cube:
        ...     rep.modify._rotation(rep.distribution.uniform((-180, -180, -180), (180, 180, 180)), "ZYX")
        omni.replicator.core.modify._rotation
    """
    if set(rotation_order.upper()) != set("XYZ"):
        raise ValueError(
            f"Invalid rotation order {rotation_order}. Rotation order must be specified as a permutation of 'X', 'Y', "
            "'Z'"
        )
    if isinstance(rotation, ReplicatorItem):
        node = create_node(
            "omni.replicator.core.OgnWritePrimAttribute",
            attribute=f"xformOp:rotate{rotation_order.upper()}",
            attributeType="double3",
        )
        utils._setup_random_attribute(write_node=node, attribute_value=rotation, prim_path=input_prims)
    else:
        # Still creating a distr node because we don't want to dynamically set the resolved type
        distr_node = uniform(rotation, rotation)
        node = create_node(
            "omni.replicator.core.OgnWritePrimAttribute",
            attribute=f"xformOp:rotate{rotation_order.upper()}",
            attributeType="double3",
        )
        utils._setup_random_attribute(write_node=node, attribute_value=distr_node, prim_path=input_prims)
    if input_prims:
        set_target_prims(node, "inputs:prims", input_prims)
    return node


@ReplicatorWrapper
def attribute(
    name: str,
    value: Union[Any, ReplicatorItem],
    attribute_type: str = None,
    input_prims: Union[ReplicatorItem, List[str]] = None,
) -> ReplicatorItem:
    """Modify the attribute of the prims specified in ``input_prims``.

    Args:
        name: The name of the attribute to modify.
        value: The value to set the attribute to.
        attribute_type: The data type of the attribute. This parameter is required if the attribute specified does not
            already exist and must be created.
        input_prims: The prims to be modified. If using ``with`` syntax, this argument can be omitted.

    Example:
        >>> import omni.replicator.core as rep
        >>> sphere = rep.create.sphere(as_mesh=False)
        >>> with sphere:
        ...     rep.modify.attribute("radius", rep.distribution.uniform(1, 5))
        omni.replicator.core.modify.attribute
    """
    node = create_node(
        "omni.replicator.core.OgnWritePrimAttribute",
        attribute=name,
        attributeType=attribute_type,
        node_name=f"WritePrimAttribute_{name}",
    )
    if not isinstance(value, ReplicatorItem):
        value = choice([value])
    utils._setup_random_attribute(write_node=node, attribute_value=value, prim_path=input_prims)

    return node


@ReplicatorWrapper
def visibility(
    value: Union[ReplicatorItem, List[bool], bool] = None,
    input_prims: Union[ReplicatorItem, List[str]] = None,
    name: Optional[str] = None,
) -> ReplicatorItem:
    """Modify the visibility of prims.

    Args:
        value: True, False. Or a list of ``bools`` for each prim to be modified, or a Replicator Distribution.
        input_prims: The prims to be modified. If using ``with`` syntax, this argument can be omitted.
        name (optional): A name for the graph node.

    Example:
        >>> import omni.replicator.core as rep
        >>> sphere = rep.create.sphere(position=(100, 0, 100))
        >>> with sphere:
        ...     rep.modify.visibility(False)
        omni.replicator.core.modify.visibility
        >>> with rep.trigger.on_frame(max_execs=10):
        ...    with sphere:
        ...        rep.modify.visibility(rep.distribution.sequence([True, False]))
        omni.replicator.core.modify.visibility

    """
    if value is None:
        value = choice([True, False], with_replacements=True)
    node = create_node("omni.replicator.core.OgnSetVisibility", node_name=name)
    if isinstance(value, ReplicatorItem):
        utils._setup_random_attribute(write_node=node, attribute_value=value, prim_path=input_prims)
    elif isinstance(value, bool):
        og.AttributeValueHelper(node.get_attribute("inputs:values")).set([value], update_usd=True)
    elif isinstance(value, List):
        og.AttributeValueHelper(node.get_attribute("inputs:values")).set(value, update_usd=True)
    else:
        raise ValueError(f"Unrecognized input type {type(value)} for modify.visibility")

    if input_prims:
        set_target_prims(node, "inputs:prims", input_prims)

    return node


@ReplicatorWrapper
def variant(
    name: str,
    value: Union[List[str], ReplicatorItem],
    input_prims: Union[ReplicatorItem, List[str]] = None,
) -> ReplicatorItem:
    """Modify the variant of the prims specified in ``input_prims``.

    Args:
        name: The name of the variant set to modify.
        value: The value to set the variant to.
        input_prims: The prims to be modified. If using ``with`` syntax, this argument can be omitted.

    Example:
        >>> import os
        >>> import omni.replicator.core as rep
        >>> sphere = rep.create.from_usd(os.path.join(rep.example.ASSETS_DIR, "variant.usd"))
        >>> with rep.trigger.on_frame(max_execs=10):
        ...     with sphere:
        ...         rep.modify.variant("colorVariant", rep.distribution.choice(["red", "green", "blue"]))
        omni.replicator.core.modify.variant
    """
    if not name:
        carb.log_error("Variant set name must be provided!")
        raise ValueError("Variant set name must be provided!")

    node = create_node("omni.replicator.core.OgnSetVariant", variant=name, node_name=f"SetVariant_{name}")
    if not isinstance(value, ReplicatorItem):
        if not isinstance(value, List):
            value = [value]
        value = choice(value)
    utils._setup_random_attribute(node, input_name="values", attribute_value=value, prim_path=None)

    if input_prims:
        set_target_prims(node, "inputs:prims", input_prims)

    return node


@ReplicatorWrapper
def material(
    value: Union[ReplicatorItem, List[str]] = None,
    input_prims: Union[ReplicatorItem, List[str]] = None,
    name: Optional[str] = None,
) -> ReplicatorItem:
    """Modify the bound material of the prims specified in ``input_prims``.

    Args:
        value: The material to bind to the prims. If multiple materials provided, a random one will be chosen.
        input_prims: The prims to be modified. If using ``with`` syntax, this argument can be omitted.
        name (optional): A name for the graph node.

    Example:
        >>> import omni.replicator.core as rep
        >>> mat = rep.create.material_omnipbr()
        >>> sphere = rep.create.sphere(as_mesh=False)
        >>> with sphere:
        ...     rep.modify.material(["/Replicator/Looks/OmniPBR"])
        omni.replicator.core.modify.material
    """
    node = create_node("omni.replicator.core.OgnBindMaterial", node_name=name)

    if isinstance(value, list):
        # If it's a list, wrap it in a choice node
        value = choice(value)
        value.node.get_attribute("outputs:samples").connect(node.get_attribute("inputs:materialPrims"), True)
    elif isinstance(value, ReplicatorItem) and value.node.get_attribute_exists("outputs_prims"):
        # ReplicatorItem is an omnipbr_material
        value.node.get_attribute("outputs_prims").connect(node.get_attribute("inputs:materialPrims"), True)
    elif isinstance(value, ReplicatorItem) and value.node.get_attribute_exists("outputs:prims"):
        value.node.get_attribute("outputs:prims").connect(node.get_attribute("inputs:materialPrims"), True)
    elif isinstance(value, ReplicatorItem) and value.node.get_attribute_exists("outputs_primsBundle"):
        # ReplicatorItem is an omnipbr_material
        value.node.get_attribute("outputs_primsBundle").connect(node.get_attribute("inputs:materialPrims"), True)
        # set_target_prims(node, "inputs:values", value)
    elif isinstance(value, ReplicatorItem) and value.node.get_attribute_exists("outputs:samples"):
        # ReplicatorItem is a type of distribution
        if value.node.get_attribute("outputs:samples").get_type_name() == "target":
            # value.node.get_attribute("outputs:samples").connect(node.get_attribute("inputs:materialPrims"), True)
            utils._setup_random_attribute(
                write_node=node, attribute_value=value.node, input_name="inputs:materialPrims"
            )
        else:
            value.node.get_attribute("outputs:samples").connect(node.get_attribute("inputs:materialPaths"), True)
    else:
        carb.log_error("Could not connect values!")

    if input_prims:
        set_target_prims(node, "inputs:prims", input_prims)

    return node


@ReplicatorWrapper
def timeline(value: Union[float, ReplicatorItem], modify_type: str = None) -> ReplicatorItem:
    """Modify the timeline by frame number or time value (in seconds).

    Args:
        value: The value to set the frame number or time to.
        modify_type: The method with which to modify the timeline by. Valid types are
            [time, start_time, end_time, frame, start_frame, end_frame]

    Example:
        >>> import omni.replicator.core as rep
        >>> with rep.trigger.on_frame(max_execs=10):
        ...     rep.modify.timeline(rep.distribution.uniform(0, 500), "frame")
        omni.replicator.core.modify.timeline
    """
    if modify_type.lower() not in ["time", "start_time", "end_time", "frame", "start_frame", "end_frame"]:
        raise ValueError(
            f"Invalid modify_type `{modify_type}`. Select from [time, start_time, end_time, frame, start_frame, "
            "end_frame]"
        )
    if isinstance(value, (int, float)):
        node = create_node("omni.replicator.core.OgnSetTimeline", modifyType=modify_type, value=value)
    elif isinstance(value, ReplicatorItem):
        node = create_node("omni.replicator.core.OgnSetTimeline", modifyType=modify_type)
        value.node.get_attribute("outputs:samples").connect(node.get_attribute("inputs:value"), True)
    else:
        carb.log_error("Value must be int, float, or ReplicatorItem")
        return None

    return node


@ReplicatorWrapper
def time(value: Union[float, ReplicatorItem]) -> ReplicatorItem:
    """Set the timeline time value (in seconds).

    Args:
        value: The value to set the time to.

    Example:
        >>> import omni.replicator.core as rep
        >>> with rep.trigger.on_frame(max_execs=10):
        ...     rep.modify.time(rep.distribution.uniform(0, 500))
        omni.replicator.core.modify.time
    """
    return timeline(value, "time")


@ReplicatorWrapper
def frame(value: Union[float, ReplicatorItem]) -> ReplicatorItem:
    """Set the timeline frame value (in frames).

    Args:
        value: The value to set the time to.

    Example:
        >>> import omni.replicator.core as rep
        >>> with rep.trigger.on_frame(max_execs=10):
        ...     rep.modify.frame(rep.distribution.uniform(0, 500))
        omni.replicator.core.modify.frame
    """
    return timeline(value, "frame")


@ReplicatorWrapper
def animation(
    values: Union[ReplicatorItem, List[str], List[Sdf.Path], List[usdrt.Sdf.Path]],
    reset_timeline: bool = False,
    input_prims: Union[ReplicatorItem, List[str]] = None,
) -> ReplicatorItem:
    """Modify the bound animation on a skeleton. This does not do any retargetting.

    Args:
        values: The animation to set to the skeleton. If a list of values is provided, one will be chosen at random.
        reset_timeline: Reset the timeline after changing the animation.
        input_prims: The skeleton to modify. If using ``with`` syntax, this argument can be omitted.

    Example:
        >>> import omni.replicator.core as rep
        >>> from pxr import Sdf
        >>> person = rep.get.skeleton('/World/Worker/Worker')
        >>> new_anim = Sdf.Path('/World/other_anim')
        >>> with person:
        ...    rep.modify.animation([new_anim])
        omni.replicator.core.modify.animation
    """
    if not isinstance(values, ReplicatorItem):
        values = choice(values)

    node = create_node("omni.replicator.core.OgnModifyAnimationTarget", reset_timeline=reset_timeline)
    values.node.get_attribute("outputs:samples").connect(node.get_attribute("inputs:values"), True)

    if input_prims:
        set_target_prims(node, "inputs:prims", input_prims)

    return node


# TODO Refactor this function (too-complex), or move to C++ if performance is an issue
@ReplicatorWrapper
def projection_material(  # noqa: C901  # ignore complexity linting error
    position: Union[ReplicatorItem, List[str]] = None,
    rotation: Union[ReplicatorItem, List[str]] = None,
    scale: Union[ReplicatorItem, List[str]] = None,
    texture_group: Union[ReplicatorItem, List[str]] = None,
    diffuse: Union[ReplicatorItem, List[str]] = None,
    normal: Union[ReplicatorItem, List[str]] = None,
    roughness: Union[ReplicatorItem, List[str]] = None,
    metallic: Union[ReplicatorItem, List[str]] = None,
    input_prims: Union[ReplicatorItem, List[str]] = None,
    name: Optional[str] = None,
) -> og.Node:
    """Modify values on a projection and update the transform via updates to the proxy prim.

    The proxy prims' transforms can be modified outside this function and then this function can be used to update the
    projection position, scale, and rotation if not manually provided.

    Args:
        position: Manually update the position of the projection, this will override the position from the proxy.
        rotation: Manually update the rotation of the projection, this will override the rotation from the proxy.
        scale: Manually update the scale of the projection, this will override the scale from the proxy.
        texture_group: Update the diffuse, normal, roughness, and/or metallic texture simultaniously. Use where there
            are diffuse, normal, roughness, and/or metallic textures in a set. If using this arg, the diffuse, normal,
            roughness and/or metallic args should be set to the suffix used to denote each type.
        diffuse: Update the diffuse texture used on the projection material. Will not change if not provided.
        normal: Update the normal texture used on the projection material. Will not change if not provided.
        roughness: Update the roughness texture used on the projection material. Will not change if not provided.
        metallic: Update the metallic texture used on the projection material. Will not change if not provided.
        input_prims: The projection prim to modify. If using ``with`` syntax, this argument can be omitted.
        name (optional): A name for the graph node.

    Example:
        >>> import omni.replicator.core as rep
        >>> import os
        >>> torus = rep.create.torus()
        >>> cube = rep.create.cube(position=(50, 100, 0), rotation=(0, 0, 90), scale=(0.2, 0.2, 0.2))
        >>> sem = [('class', 'shape')]
        >>> with torus:
        ...     projection = rep.create.projection_material(cube, sem)
        >>> with projection:
        ...     rep.modify.projection_material(diffuse=os.path.join(rep.example.TEXTURES_DIR, "smiley_albedo.png"))
        omni.replicator.core.modify.projection_material
    """
    node = create_node("omni.replicator.core.OgnModifyProjectionMaterial", node_name=name)

    if position:
        if not isinstance(position, ReplicatorItem):
            position = uniform(position)
        position.node.get_attribute("outputs:samples").connect(node.get_attribute("inputs:position"), True)

    if rotation:
        if not isinstance(rotation, ReplicatorItem):
            rotation = uniform(rotation)
        rotation.node.get_attribute("outputs:samples").connect(node.get_attribute("inputs:rotation"), True)

    if scale:
        if not isinstance(scale, ReplicatorItem):
            scale = uniform(scale)
        scale.node.get_attribute("outputs:samples").connect(node.get_attribute("inputs:scale"), True)

    if texture_group:
        if not isinstance(texture_group, ReplicatorItem):
            texture_group = choice(texture_group)

        texture_group.node.get_attribute("outputs:samples").connect(node.get_attribute("inputs:textureGroup"), True)

    if diffuse:
        if texture_group and isinstance(diffuse, str):
            node.get_attribute("inputs:diffuse").set([diffuse])
        else:
            if not isinstance(diffuse, ReplicatorItem):
                if not isinstance(diffuse, List):
                    diffuse = [diffuse]
                diffuse = choice(diffuse)
            diffuse.node.get_attribute("outputs:samples").connect(node.get_attribute("inputs:diffuse"), True)

    if normal:
        if texture_group and isinstance(normal, str):
            node.get_attribute("inputs:normal").set([normal])
        else:
            if not isinstance(normal, ReplicatorItem):
                if not isinstance(normal, List):
                    normal = [normal]
                normal = choice(normal)
            normal.node.get_attribute("outputs:samples").connect(node.get_attribute("inputs:normal"), True)

    if roughness:
        if texture_group and isinstance(roughness, str):
            node.get_attribute("inputs:roughness").set([roughness])
        else:
            if not isinstance(roughness, ReplicatorItem):
                if not isinstance(roughness, List):
                    roughness = [roughness]
                roughness = choice(roughness)
            roughness.node.get_attribute("outputs:samples").connect(node.get_attribute("inputs:roughness"), True)

    if metallic:
        if texture_group and isinstance(metallic, str):
            node.get_attribute("inputs:metallic").set([metallic])
        else:
            if not isinstance(metallic, ReplicatorItem):
                if not isinstance(metallic, List):
                    metallic = [metallic]
                metallic = choice(metallic)
            metallic.node.get_attribute("outputs:samples").connect(node.get_attribute("inputs:metallic"), True)

    if input_prims:
        set_target_prims(node, "inputs:prims", input_prims)

    return node


def pose_orbit(
    barycentre: Union[ReplicatorItem, Tuple[float, float, float], str],
    distance: Union[ReplicatorItem, float],
    azimuth: Union[ReplicatorItem, float],
    elevation: Union[ReplicatorItem, float],
    look_at_barycentre: bool = True,
    input_prims: Union[ReplicatorItem, List[str]] = None,
) -> og.Node:
    """Position the ``input_prims`` in an orbit around a point.

    Args:
        barycentre: The point around which to position the input prims. The barycentre can be specified
            as either coordinates or as prim paths. If more than one prim path is provided, the barycentre will
            be set to the mean of the prim centres.
        distance: Distance from barycentre
        azimuth: Horizontal angle (in degrees).
        elevation: Vertical angle  (in degrees).
        look_at_centre: If ``True``, orient the ``input_prims`` towards the barycentre. Default ``True``.
        input_prims: The prims to be modified. If using ``with`` syntax, this argument can be omitted.

    Example:
        >>> import omni.replicator.core as rep
        >>> cube = rep.create.cube()
        >>> camera = rep.create.camera()
        >>> with camera:
        ...     rep.modify.pose_orbit(
        ...         barycentre=cube,
        ...         distance=rep.distribution.uniform(400, 500),
        ...         azimuth=45,
        ...         elevation=rep.distribution.uniform(-180, 180),
        ...     )
        omni.replicator.core.modify._pose_orbit
    """
    with sequential():
        orbit_node = _pose_orbit(barycentre, distance, azimuth, elevation, input_prims)
        _position(orbit_node, input_prims=input_prims)
        if look_at_barycentre:
            look_at_node = _look_at(barycentre, input_prims=input_prims)
            _rotation(look_at_node, "XYZ", input_prims)

    return orbit_node


@ReplicatorWrapper
def _pose_orbit(
    barycentre: Union[ReplicatorItem, Tuple[float, float, float], str],
    distance: Union[ReplicatorItem, float],
    azimuth: Union[ReplicatorItem, float],
    elevation: Union[ReplicatorItem, float],
    input_prims: Union[ReplicatorItem, List[str]] = None,
) -> og.Node:
    if isinstance(barycentre, (tuple, list)) and len(barycentre) != 3:
        raise ValueError(
            f"Coordinates `{barycentre}` supplied are invalid. Please provide coordinates " "in the form of (x, y z)"
        )

    orbit_node = create_node("omni.replicator.core.OgnOrbit")

    if isinstance(barycentre, (ReplicatorItem, str, Sdf.Path, usdrt.Sdf.Path)):
        if isinstance(barycentre, ReplicatorItem) and barycentre.node.get_attribute_exists("outputs:samples"):
            utils._setup_random_attribute(
                write_node=orbit_node, attribute_value=barycentre, input_name="inputs:barycentrePrim"
            )
        else:
            set_target_prims(orbit_node, "inputs:barycentrePrim", barycentre)
        orbit_node.get_attribute("inputs:barycentreMode").set("Prim")
    elif isinstance(barycentre, (tuple, list, np.ndarray)):
        orbit_node.get_attribute("inputs:barycentreCoordinates").set(barycentre)
        orbit_node.get_attribute("inputs:barycentreMode").set("Coordinates")
    else:
        raise ValueError(f"Invalid type {type(barycentre)} supplied for `barycentre`")

    utils._setup_random_attribute(
        write_node=orbit_node, attribute_value=distance, prim_path=input_prims, input_name="distance"
    )
    utils._setup_random_attribute(
        write_node=orbit_node, attribute_value=azimuth, prim_path=input_prims, input_name="azimuth"
    )
    utils._setup_random_attribute(
        write_node=orbit_node, attribute_value=elevation, prim_path=input_prims, input_name="elevation"
    )

    return orbit_node
