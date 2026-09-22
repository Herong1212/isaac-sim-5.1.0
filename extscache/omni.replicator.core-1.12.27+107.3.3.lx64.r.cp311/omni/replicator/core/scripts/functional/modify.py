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

import contextlib
from typing import Any, Dict, List, Optional, Tuple, Union

import carb
import numpy as np
import omni.usd
import pxr
import usdrt
import warp as wp

from ...bindings._omni_replicator_core import apply_pxr_transforms
from .. import utils
from . import utils as f_utils

PERSISTENT_SETTINGS_PREFIX = "/persistent"
ROTATION_ORDER_MAP = {
    "pxr": {
        "X": pxr.Gf.Vec3d.XAxis(),
        "Y": pxr.Gf.Vec3d.YAxis(),
        "Z": pxr.Gf.Vec3d.ZAxis(),
    },
    "usdrt": {
        "X": usdrt.Gf.Vec3d.XAxis(),
        "Y": usdrt.Gf.Vec3d.YAxis(),
        "Z": usdrt.Gf.Vec3d.ZAxis(),
    },
}
VALID_ROTATION_ORDERS = ("XYZ", "XZY", "YXZ", "YZX", "ZXY", "ZYX")


def _get_xform_defaults():
    settings = carb.settings.get_settings()
    defaultXformOpType = settings.get(PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/DefaultXformOpType")
    defaultRotationOrder = settings.get(PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/DefaultRotationOrder")
    defaultXformPrecision = settings.get(PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/DefaultXformOpPrecision")
    return defaultXformOpType, defaultRotationOrder, defaultXformPrecision


@wp.kernel(enable_backward=False)
def move_prims(pos: wp.fabricarray(dtype=wp.mat44d), new_positions: wp.array(dtype=wp.vec3d)):
    i = wp.tid()
    m = pos[i]
    m[3, 0] = new_positions[i][0]
    m[3, 1] = new_positions[i][1]
    m[3, 2] = new_positions[i][2]
    pos[i] = m


def _get_relative_transform(relative_to):
    """Gets the world transform matrix for the relative_to reference.

    Args:
        relative_to (Union[str, pxr.Sdf.Path, usdrt.Sdf.Path, pxr.Usd.Prim, usdrt.Usd.Prim]):
            Reference to get transform from.

    Returns:
        pxr.Gf.Matrix4d: World transform matrix of the reference.

    Raises:
        ValueError: If relative_to is invalid or prim cannot be found.
    """
    if isinstance(relative_to, (pxr.Usd.Prim, usdrt.Usd.Prim)):
        prim = relative_to
    else:
        # Convert string or path to prim
        if isinstance(relative_to, (str, pxr.Sdf.Path, usdrt.Sdf.Path)):
            relative_to = pxr.Sdf.Path(relative_to)
        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath(str(relative_to))
        if not prim:
            raise ValueError(f"Could not find prim at path: {relative_to}")

    # Get world transform of reference prim
    if f_utils.get_is_fsd_enabled():
        stage = prim.GetStage()
        stage_id = stage.GetStageIdAsStageId()
        fabric_id = stage.GetFabricId()
        prim_path = prim.GetPrimPath()

        hier = usdrt.hierarchy.IFabricHierarchy().get_fabric_hierarchy(fabric_id, stage_id)
        return usdrt.Gf.Transform(hier.get_local_xform(prim_path))
    else:
        xformable = pxr.UsdGeom.Xformable(prim)
        return pxr.Gf.Transform(xformable.ComputeLocalToWorldTransform(pxr.Usd.TimeCode.Default()))


def pose(
    prims: Union[pxr.Usd.Prim, usdrt.Usd.Prim, List[Union[pxr.Usd.Prim, usdrt.Usd.Prim]]],
    position_value=None,
    rotation_value=None,
    rotation_order: Optional[str] = None,
    scale_value=None,
    relative_to: Union[str, pxr.Sdf.Path, usdrt.Sdf.Path, pxr.Usd.Prim, usdrt.Usd.Prim] = None,
    look_at_value: Union[
        pxr.Usd.Prim,
        usdrt.Usd.Prim,
        List[Union[pxr.Usd.Prim, usdrt.Usd.Prim, Tuple[float, float, float], pxr.Gf.Vec3d]],
        Tuple[float, float, float],
        pxr.Gf.Vec3d,
    ] = None,
    look_at_up_axis: Union[Tuple[float, float, float], List[float], pxr.Gf.Vec3d] = (0, 1, 0),
    pivot: Union[Tuple[float, float, float], List[Tuple[float, float, float]], pxr.Gf.Vec3d] = None,
):
    """Modify the pose of prims by setting position, rotation, scale and look-at parameters.

    Args:
        prims: Single prim or list of prims to modify
        position_value: World space position(s) as (x,y,z) tuples
        rotation_value: Rotation value(s) as Euler angles, quaternions or Gf.Rotation
        rotation_order: Rotation order for Euler angles. If ``None``, the default rotation order specified by the
            ``/app/primCreation/DefaultRotationOrder`` setting will be used.
        scale_value: Scale value(s) as single float or (x,y,z) tuples
        relative_to: Reference prim to apply transforms relative to
        look_at_value: Target(s) to orient prims towards (mutually exclusive with rotation_value)
        look_at_up_axis: Up vector for look-at calculations
        pivot: Local pivot point(s) for transforms, normalized to [-1,1] range

    Raises:
        ValueError: If invalid inputs are provided or operations fail
    """
    # Early exit if no transforms specified
    if all(v is None for v in (position_value, rotation_value, scale_value, look_at_value, pivot)):
        return

    # Normalize inputs
    prims = [prims] if isinstance(prims, (pxr.Usd.Prim, usdrt.Usd.Prim)) else prims
    num_prims = prims.GetCount() if isinstance(prims, usdrt.Rt.RtPrimSelection) else len(prims)

    # Batch values to match prim count
    position_value = f_utils.get_batched_value(position_value, prims)
    rotation_value = f_utils.get_batched_value(rotation_value, prims)
    scale_value = f_utils.get_batched_value(scale_value, prims)
    pivot = f_utils.get_batched_value(pivot, prims)
    relative_to = f_utils.get_batched_value(relative_to, prims)

    # Special case: RtPrimSelection
    if isinstance(prims, usdrt.Rt.RtPrimSelection):
        _apply_rt_prim_transforms(
            prims, position_value, rotation_value, scale_value, look_at_value, look_at_up_axis, pivot
        )
        return

    # Process look-at targets
    if look_at_value is not None:
        look_at_value = _normalize_look_at_targets(look_at_value, num_prims)

    # Apply transforms to each prim
    if f_utils.get_is_fsd_enabled():
        mod = usdrt
        stage = usdrt.Usd.Stage.Attach(omni.usd.get_context().get_stage_id())
        ctx_mgr = contextlib.nullcontext
    else:
        mod = pxr
        ctx_mgr = pxr.Sdf.ChangeBlock
        stage = omni.usd.get_context().get_stage()
    with ctx_mgr():
        for idx, prim in enumerate(prims):
            # Handle point instancers separately
            if prim.GetTypeName() == "PointInstancer":
                pos_subset = position_value[idx:] if position_value is not None else None
                rot_subset = rotation_value[idx:] if rotation_value is not None else None
                scale_subset = scale_value[idx:] if scale_value is not None else None
                pivot_subset = pivot[idx:] if pivot is not None else None

                # TODO handle like the rest with transforms
                if pos_subset:
                    _modify_point_instancer_positions(prim, pos_subset, pivot_subset)
                if rot_subset or (look_at_value is not None):
                    look_at_subset = look_at_value[idx:] if look_at_value is not None else None
                    _modify_point_instancer_rotations(prim, rot_subset, look_at_subset, look_at_up_axis, pivot_subset)
                if scale_subset:
                    _modify_point_instancer_scales(prim, scale_subset)
                idx += len(prim.GetAttribute("protoIndices").Get())
                continue

            # Get reference transform if specified
            ref_transform = None
            if relative_to is not None and relative_to[idx] is not None:
                ref_transform = f_utils.get_world_transform(relative_to[idx])

            # Create a transform object to accumulate all modifications
            transform = f_utils.get_local_transform(prim)

            # Set pivot if specified
            if pivot is not None and pivot[idx] is not None:
                # Get prim's bounding box
                # TODO: For USDRT need to get the bound a different way
                stage_pxr = omni.usd.get_context().get_stage()
                prim_pxr = stage_pxr.GetPrimAtPath(str(prim.GetPath()))
                bbox = pxr.UsdGeom.Boundable(prim_pxr).ComputeWorldBound(
                    mod.Usd.TimeCode.Default(), purpose1=mod.UsdGeom.Tokens.default_
                )
                bbox_range = bbox.GetRange()

                # Convert normalized pivot to world space
                pivot_point = mod.Gf.Vec3d(
                    bbox_range.GetMin()[0] + (bbox_range.GetSize()[0] * (pivot[idx][0] + 1) * 0.5),
                    bbox_range.GetMin()[1] + (bbox_range.GetSize()[1] * (pivot[idx][1] + 1) * 0.5),
                    bbox_range.GetMin()[2] + (bbox_range.GetSize()[2] * (pivot[idx][2] + 1) * 0.5),
                )
                transform.SetPivotPosition(pivot_point)

            if rotation_value is not None:
                rot = rotation_value[idx]
                # Euler Angles
                if isinstance(rot, (tuple, list, mod.Gf.Vec3f, mod.Gf.Vec3d)) and len(rot) == 3:
                    if rotation_order is None:
                        rotation_order = (
                            carb.settings.get_settings().get_as_string("/app/primCreation/DefaultRotationOrder")
                            or "XYZ"
                        )
                    elif rotation_order not in VALID_ROTATION_ORDERS:
                        raise ValueError(
                            f"Invalid rotation order: {rotation_order}, must be one of {VALID_ROTATION_ORDERS}"
                        )
                    # Convert Euler angles to rotation
                    mod_str = "pxr" if mod == pxr else "usdrt"
                    rot = (
                        mod.Gf.Rotation(ROTATION_ORDER_MAP[mod_str][rotation_order[0].upper()], rot[0])
                        * mod.Gf.Rotation(ROTATION_ORDER_MAP[mod_str][rotation_order[1].upper()], rot[1])
                        * mod.Gf.Rotation(ROTATION_ORDER_MAP[mod_str][rotation_order[2].upper()], rot[2])
                    )
                # Quaternions
                elif isinstance(rot, (tuple, list, mod.Gf.Vec4f, mod.Gf.Vec4d)) and len(rot) == 4:
                    # Convert quaternion to rotation
                    rot = mod.Gf.Rotation(mod.Gf.Quatd(rot))
                elif isinstance(rot, (mod.Gf.Quatf, mod.Gf.Quatd)):
                    rot = mod.Gf.Rotation(rot)
                elif not isinstance(rot, (mod.Gf.Rotation, usdrt.Gf.Rotation)):
                    raise ValueError(f"Invalid rotation value: {rot} of type {type(rot)}")

                transform.SetRotation(rot)

            # Apply position
            if position_value is not None:
                pos = position_value[idx]
                if isinstance(pos, (tuple, list)) and len(pos) == 3:
                    pos = mod.Gf.Vec3d(*pos)
                elif isinstance(pos, (mod.Gf.Vec3f, mod.Gf.Vec3d)):
                    pos = list(pos)

                transform.SetTranslation(pos)

            # Apply scale
            if scale_value is not None:
                scale_val = scale_value[idx]
                if isinstance(scale_val, (int, float)):
                    scale_val = mod.Gf.Vec3d(scale_val, scale_val, scale_val)
                elif isinstance(scale_val, (tuple, list)) and len(scale_val) == 3:
                    scale_val = mod.Gf.Vec3d(*scale_val)

                transform.SetScale(scale_val)

            pivot_matrix_inv = mod.Gf.Transform(translation=-transform.GetPivotPosition())
            transform = mod.Gf.Transform(transform.GetMatrix() * pivot_matrix_inv.GetMatrix())
            if ref_transform is not None:
                transform = mod.Gf.Transform(transform.GetMatrix() * ref_transform.GetMatrix())

            # Lookat applied after all other transforms
            # Apply rotation (either direct or look-at)
            if look_at_value is not None:
                target = look_at_value[idx]
                if isinstance(target, (str, pxr.Sdf.Path, usdrt.Sdf.Path)):
                    target = stage.GetPrimAtPath(str(target))
                if isinstance(target, (mod.Usd.Prim, mod.Usd.Prim)):
                    # Get prim position for look_at target
                    target_pos = f_utils.get_world_transform(target).GetTranslation()
                elif isinstance(target, (tuple, list, mod.Gf.Vec3d)):
                    target_pos = target
                else:
                    raise ValueError(f"Unsupported look_at target type: {type(target)}")

                # Get current prim position as eye position
                stage_up_axis = pxr.UsdGeom.GetStageUpAxis(omni.usd.get_context().get_stage())
                eye_pos = transform.GetTranslation()
                if look_at_up_axis is None:
                    look_at_up_axis = mod.Gf.Vec3d.ZAxis() if stage_up_axis == "Z" else mod.Gf.Vec3d.YAxis()
                rot = utils.look_at(
                    target_pos,
                    look_at_up_axis,
                    eye_pos,
                    stage_up_axis=stage_up_axis,
                    use_usdrt=f_utils.get_is_fsd_enabled(),
                )

                # For replicator cameras xform, apply additional replication when stage is Z-up to account for camera y-up orientation
                mod_str = "pxr" if mod == pxr else "usdrt"
                if prim.HasAttribute("replicatorCameraXform") and stage_up_axis == "Z":
                    # cam_z_rot is the inverse of the camera (XYZ 90, 0, 90) rotation applied by default when stage is Z-up
                    cam_z_rot = mod.Gf.Rotation(mod.Gf.Vec3d.ZAxis(), -90) * mod.Gf.Rotation(mod.Gf.Vec3d.XAxis(), -90)
                    rot = cam_z_rot * rot

                # Remove parent rotation
                parent_tf = f_utils.get_world_transform(prim.GetParent())
                parent_rot_inv = parent_tf.GetMatrix().GetInverse().GetOrthonormalized().ExtractRotation()
                rot = rot * parent_rot_inv

                transform.SetRotation(rot)

            # Apply the final transform to the prim
            if isinstance(prim, usdrt.Usd.Prim):
                _apply_usdrt_transforms(prim, transform)
            else:
                # Call C++ binding with prim path and 16-element matrix list to avoid Boost.Python/pybind interop
                mat = transform.GetMatrix()
                mat16 = [
                    mat[0][0],
                    mat[0][1],
                    mat[0][2],
                    mat[0][3],
                    mat[1][0],
                    mat[1][1],
                    mat[1][2],
                    mat[1][3],
                    mat[2][0],
                    mat[2][1],
                    mat[2][2],
                    mat[2][3],
                    mat[3][0],
                    mat[3][1],
                    mat[3][2],
                    mat[3][3],
                ]
                apply_pxr_transforms(str(prim.GetPath()), mat16)
            idx += 1


def _transform_to_relative_space(relative_to, positions, rotations):
    """Transform position and rotation values to be relative to reference."""
    ref_matrix = f_utils.get_world_transform(relative_to)

    if positions is not None:
        positions = [(ref_matrix * pxr.Gf.Matrix4d().SetTranslate(pos)).ExtractTranslation() for pos in positions]

    if rotations is not None:
        ref_rotation = pxr.Gf.Rotation(ref_matrix.ExtractRotation())
        rotations = [
            ref_rotation * (pxr.Gf.Rotation(pxr.Gf.Vec3d(*rot)) if isinstance(rot, (tuple, list)) else rot)
            for rot in rotations
        ]
    return positions, rotations


def _normalize_look_at_targets(look_at, num_prims):
    """Normalize look-at targets to a list matching number of prims."""
    if not isinstance(look_at, list):
        look_at = [look_at] * num_prims
    elif len(look_at) == 1:
        look_at = look_at * num_prims
    elif len(look_at) != num_prims:
        raise ValueError(f"Length of look_at targets ({len(look_at)}) must match number of prims ({num_prims})")
    return look_at


def _apply_usdrt_transforms(prim, transform: usdrt.Gf.Transform):
    stage = prim.GetStage()
    stage_id = stage.GetStageIdAsStageId()
    fabric_id = stage.GetFabricId()
    prim_path = prim.GetPrimPath()
    if isinstance(prim_path, pxr.Sdf.Path):
        prim_path = usdrt.Sdf.Path(str(prim_path))

    if isinstance(transform, pxr.Gf.Transform):
        transform = usdrt.Gf.Transform(usdrt.Gf.Matrix4d(transform.GetMatrix()))

    hier = usdrt.hierarchy.IFabricHierarchy().get_fabric_hierarchy(fabric_id, stage_id)
    hier.set_local_xform(prim_path, transform.GetMatrix())
    # hier.update_world_xforms()


def _apply_rt_prim_transforms(
    prims, position_value, rotation_value=None, scale_value=None, look_at=None, look_at_up_axis=None, pivot=None
):
    """Apply transforms to RtPrimSelection.

    Args:
        prims: The RtPrimSelection to transform
        position_value: Position value to apply
        rotation_value: Optional rotation value to apply
        scale_value: Optional scale value to apply
        look_at: Optional look_at target
        look_at_up_axis: Optional up axis for look_at
        pivot: Optional pivot point for transforms
    """
    # Currently only handles position transforms
    positions = wp.fabricarray(prims, "omni:fabric:localMatrix")
    device = positions.device
    new_positions = wp.array(position_value, dtype=wp.vec3d, device=device)
    assert new_positions.size == len(prims)
    wp.launch(move_prims, dim=positions.size, inputs=[positions, new_positions], device=device)


def position(
    prims: Union[pxr.Usd.Prim, usdrt.Usd.Prim, List[Union[pxr.Usd.Prim, usdrt.Usd.Prim]]],
    value: Union[Tuple[float, float, float], List[Tuple[float, float, float]], pxr.Gf.Vec3d],
    relative_to: Union[str, pxr.Sdf.Path, usdrt.Sdf.Path, pxr.Usd.Prim, usdrt.Usd.Prim] = None,
    pivot: Union[Tuple[float, float, float], List[Tuple[float, float, float]], pxr.Gf.Vec3d] = None,
):
    return pose(prims, position_value=value, relative_to=relative_to, pivot=pivot)


def look_at(
    prims: Union[pxr.Usd.Prim, usdrt.Usd.Prim, List[Union[pxr.Usd.Prim, usdrt.Usd.Prim]]],
    value: Union[Tuple[float, float, float], List[Tuple[float, float, float]], pxr.Gf.Vec3d],
    look_at_up_axis: Union[Tuple[float, float, float], List[float], pxr.Gf.Vec3d] = (0, 1, 0),
):
    """Modify the look_at of USD prims.

    Args:
        prims: Single prim or list of prims to look_at.
        value: Look_at target(s) specified as either:
            - USD prim
            - Point in space as (x,y,z)
        look_at_up_axis: Up vector for look_at calculations. Defaults to (0,1,0).
    """
    return pose(prims, look_at_value=value, look_at_up_axis=look_at_up_axis)


def rotation(
    prims: Union[pxr.Usd.Prim, usdrt.Usd.Prim, List[Union[pxr.Usd.Prim, usdrt.Usd.Prim]]],
    value: Union[Tuple[float, float, float], List[Tuple[float, float, float]], pxr.Gf.Vec3d],
    value_rotation_order: str = "XYZ",
    relative_to: Union[str, pxr.Sdf.Path, usdrt.Sdf.Path, pxr.Usd.Prim, usdrt.Usd.Prim] = None,
    pivot: Union[Tuple[float, float, float], List[Tuple[float, float, float]], pxr.Gf.Vec3d] = None,
):
    """Modify the rotation of USD prims.

    Target rotation will follow existing prim rotation operation when present. Otherwise, a "rotateXYZ" operation will be
    applied.

    Args:
        prims: Single prim or list of prims to rotate.
        value: Rotation value(s) specified as either:
            - Euler angles in degrees. Rotation order can be specified using the value_rotation_order parameter.
            - Quaternion (x,y,z,w)
            - pxr.Gf.Rotation object.
        value_rotation_order: Rotation operation of the provided value. Defaults to "XYZ".
        relative_to: Reference to apply rotation relative to. Can be:
            - Path string
            - USD prim
            - pxr.Sdf.Path
        pivot: Local pivot point(s) for rotation, normalized to [-1,1] range.
            Origin is at center of prim's bounding box.

    Raises:
        ValueError: If both value and look_at are specified, or if invalid rotation values
            or look_at targets are provided.
    """
    return pose(
        prims=prims,
        rotation_value=value,
        rotation_order=value_rotation_order,
        relative_to=relative_to,
        pivot=pivot,
    )


def scale(
    prims: Union[pxr.Usd.Prim, usdrt.Usd.Prim, List[Union[pxr.Usd.Prim, usdrt.Usd.Prim]]],
    value: Union[Tuple[float, float, float], List[Tuple[float, float, float]], pxr.Gf.Vec3d],
    relative_to: Union[str, pxr.Sdf.Path, usdrt.Sdf.Path, pxr.Usd.Prim, usdrt.Usd.Prim] = None,
):
    """Modify the scale of USD prims.

    Args:
        prims: Single prim or list of prims to scale.
        value: Scale value(s) specified as either:
            - Tuple of (x,y,z) scale factors
            - List of (x,y,z) scale factors
            - pxr.Gf.Vec3d object
        relative_to: Reference to apply scale relative to. Can be:
            - Path string
            - USD prim
            - pxr.Sdf.Path
    """
    return pose(prims, scale_value=value, relative_to=relative_to)


def _material_attribute(prim: pxr.Usd.Prim, attribute_name: str, value: Any):
    """Modify an attribute of a material prim.

    Args:
        prim: The material prim to modify
        attribute_name: The name of the attribute to modify
        value: The value to set the attribute to
    """
    if isinstance(prim, (pxr.Usd.Prim, usdrt.Usd.Prim)):
        prim = [prim]
        value = [value]

    value = f_utils.get_batched_value(value, prim)

    with pxr.Sdf.ChangeBlock():
        for p, v in zip(prim, value):
            f_utils.populate_material_inputs(p)
            if p.GetTypeName() == "Shader":
                shader = pxr.UsdShade.Shader(p)
            elif p.GetTypeName() == "Material":
                shader = pxr.UsdShade.Shader(omni.usd.get_shader_from_material(p, True))
            else:
                raise ValueError(f"Invalid prim type: {p.GetTypeName()}, expected Shader or Material")
            attr = shader.GetInput(attribute_name.replace("inputs:", ""))
            if attr and v is not None:
                python_class = attr.GetAttr().GetTypeName().type.pythonClass  # Might be a better way to do this?
                if isinstance(v, str) and attr.GetTypeName() == usdrt.Sdf.ValueTypeNames.Asset:
                    v = usdrt.Sdf.AssetPath(v, v)
                elif python_class:
                    attr.Set(python_class(v))
                else:
                    attr.Set(v)
            else:
                raise ValueError(f"No attribute '{attribute_name}' exists for prim '{p}'.")


def attribute(
    prims: Union[pxr.Usd.Prim, usdrt.Usd.Prim, List[Union[pxr.Usd.Prim, usdrt.Usd.Prim]]],
    attribute_name: str,
    value: Any,
):
    """Modify an attribute of a prim.

    Args:
        prims: The prims to modify
        attribute_name: The name of the attribute to modify
        value: The value to set the attribute to
    """
    if isinstance(prims, (pxr.Usd.Prim, usdrt.Usd.Prim)):
        prims = [prims]
        value = [value]

    value = f_utils.get_batched_value(value, prims)

    def set_attributes(prims, attribute, values):
        for p, v in zip(prims, values):
            # Try to get attribute
            if p.HasAttribute(attribute):
                attr = p.GetAttribute(attribute)
            # For materials/shaders, try populating inputs and check again
            elif p.GetTypeName() in ["Material", "Shader"]:
                f_utils.populate_material_inputs(p)
                if p.HasAttribute(attribute):
                    attr = p.GetAttribute(attribute)
                else:
                    raise ValueError(
                        f"No attribute '{attribute}' exists for prim '{p}' even after populating material inputs."
                    )
            else:
                raise ValueError(f"No attribute '{attribute}' exists for prim '{p}'.")

            if isinstance(v, str) and attr.GetTypeName() == usdrt.Sdf.ValueTypeNames.Asset:
                v = usdrt.Sdf.AssetPath(v, v)
            type_name = attr.GetTypeName()
            if hasattr(type_name, "type"):
                python_class = type_name.type.pythonClass  # Might be a better way to do this?
            else:
                python_class = None
            if isinstance(v, str) and attr.GetTypeName() == usdrt.Sdf.ValueTypeNames.Asset:
                v = usdrt.Sdf.AssetPath(v, v)
            elif python_class:
                attr.Set(python_class(v))
            else:
                attr.Set(v)

    # Specify context based on pxr or USDRT prim, checking the first prim
    is_usdrt_prim = isinstance(prims[0], usdrt.Usd.Prim)
    ctx_mgr = contextlib.nullcontext if is_usdrt_prim else pxr.Sdf.ChangeBlock
    with ctx_mgr():
        if all(p.GetTypeName() in ["Material", "Shader"] for p in prims):
            _material_attribute(prims, attribute_name, value)
        else:
            set_attributes(prims, attribute_name, value)


def semantics(
    prims: Union[pxr.Usd.Prim, usdrt.Usd.Prim, List[Union[pxr.Usd.Prim, usdrt.Usd.Prim]]],
    value: Optional[
        Union[List[Tuple[str, str]], Dict[str, Union[str, List[str]]], List[Dict[str, Union[str, List[str]]]]]
    ] = None,
    mode: str = "add",
) -> None:
    """Modify semantics of one or more prims.

    Modify the semantics of one or more prims. Semantics use the OpenUSD SemanticsLabelsAPI schema
    (https://openusd.org/dev/api/usd_semantics_overview.html). If a prim used the older SemanticsAPI schema,
    it will be automatically converted to the new SemanticsLabelsAPI schema.

    Args:
        prims: The prims to modify
        value: Dictionary or List of dictionaries representing semantic type and values
        mode: The mode to use for modifying semantics. Can be "add", "replace", or "clear".
            - "add": Add new semantics. If a semantic type already exists, it will be extended.
            - "replace": Replace existing semantics. If a semantic type already exists, it will be replaced with the new value.
            - "clear": Clear all existing semantics before applying new values.
    """
    VALID_MODES = ["add", "replace", "clear"]
    if mode.lower() not in VALID_MODES:
        raise ValueError(f"Invalid mode {mode}. Must be one of {VALID_MODES}.")

    if value is None:
        value = {}

    # Normalize inputs
    if isinstance(prims, (pxr.Usd.Prim, usdrt.Usd.Prim)):
        prims = [prims]

    # Validate and normalize value input
    normalized_values = []
    # Handle legacy format: single (type, value) tuple
    if isinstance(value, (tuple, list)) and len(value) == 2 and all((isinstance(i, str) for i in value)):
        normalized_values.append(utils.legacy_semantics_arg_to_new([tuple(value)]))
    elif isinstance(value, list) and all(
        isinstance(item, (tuple, list)) and len(item) == 2 and isinstance(item[1], str) for item in value
    ):
        normalized_values = utils.legacy_semantics_arg_to_new(value)
    elif isinstance(value, list):
        for i, v in enumerate(value):
            # Handle legacy format: single (type, value) tuple
            if isinstance(v, (tuple, list)) and len(v) == 2 and all((isinstance(i, str) for i in v)):
                normalized_values.append(utils.legacy_semantics_arg_to_new([tuple(v)]))
            # Handle legacy format: list of (type, value) tuples
            elif isinstance(v, list) and all(isinstance(item, (tuple, list)) and len(item) == 2 for item in v):
                normalized_values.append(utils.legacy_semantics_arg_to_new(v))
            # Handle legacy format: list of lists of (type, value) tuples
            elif isinstance(v, list) and all(
                isinstance(sublist, list) and all(isinstance(item, tuple) and len(item) == 2 for item in sublist)
                for sublist in v
            ):
                normalized_values.append(utils.legacy_semantics_arg_to_new(v))
            # Handle dictionary format
            elif isinstance(v, dict):
                normalized_values.append(v)
            else:
                raise ValueError(
                    f"Invalid semantics value format: {v}. Expected dictionary or list of (type, value) tuples."
                )
    elif isinstance(value, dict):
        normalized_values.append(value)
    else:
        raise ValueError(
            f"Invalid semantics value format: {value}. Expected dictionary, list of dictionaries, or list of (type, value) tuples."
        )
    normalized_values = f_utils.get_batched_value(normalized_values, prims)
    stage = omni.usd.get_context().get_stage()

    def add_semantics(prim, semantic_type, semantic_value, mode: str):
        schemas = [s.split(":")[1] for s in prim.GetAppliedSchemas() if "SemanticsLabelsAPI" in s]

        # Ensure proper path
        if isinstance(prim, str):
            prim_path = pxr.Sdf.Path(prim)

        # Get the SdfPrimSpec for this prim
        layer = stage.GetEditTarget().GetLayer()
        prim_spec = layer.GetPrimAtPath(str(prim.GetPath()))
        if prim_spec is None:
            # Prim doesn't exist; create it as a Def
            prim_spec = pxr.Sdf.CreatePrimInLayer(layer, str(prim.GetPath()))
            prim_spec.specifier = pxr.Sdf.SpecifierDef

        api_schema_token = f"SemanticsLabelsAPI:{semantic_type}"

        f_utils.apply_schemas(prim_spec, [api_schema_token])

        attr_name = f"semantics:labels:{semantic_type}"

        # Set semantic value
        # semantic_value should be a list of strings here
        if isinstance(semantic_value, str):
            semantic_value = [semantic_value]

        # Add attribute if it doesn't exist
        if attr_name not in prim_spec.attributes:
            pxr.Sdf.AttributeSpec(
                prim_spec,
                attr_name,
                pxr.Sdf.ValueTypeNames.StringArray,
            )

        labels_attr = prim_spec.attributes[attr_name]
        if mode in ["replace", "clear"]:
            labels_attr.default = semantic_value
        else:
            labels_attr.default = [*labels_attr.default, *semantic_value]

    def clear_semantics(prim):
        """Clear all semantics labels and applied API tokens from a prim.

        Args:
            prim (pxr.Usd.Prim | usdrt.Usd.Prim): Prim whose semantics will be cleared.

        Notes:
            Performs a single-pass removal by:
            - Deleting all attributes with names starting with ``semantics:labels:``
            - Filtering out any ``SemanticsLabelsAPI:<inst>`` tokens from the
              ``apiSchemas`` list-op without converting it to an explicit list
        """

        # Ensure we operate on a PXR prim for Sdf editing
        if isinstance(prim, usdrt.Usd.Prim):
            prim = omni.usd.get_context().get_stage().GetPrimAtPath(str(prim.GetPath()))

        prim_spec: pxr.Sdf.PrimSpec = prim.GetPrimStack()[0]

        # Remove all semantics:labels:* attributes in one pass
        attr_names_to_delete = [
            name for name in list(prim_spec.attributes.keys()) if name.startswith("semantics:labels:")
        ]
        for attr_name in attr_names_to_delete:
            attr_spec = prim_spec.attributes[attr_name]
            del attr_spec.owner.properties[attr_name]

        # Filter SemanticsLabelsAPI:* tokens from apiSchemas in one pass
        existing_apis = prim_spec.GetInfo("apiSchemas") or pxr.Sdf.TokenListOp()
        if existing_apis:
            modified = False
            if getattr(existing_apis, "explicitItems", None) is not None:
                new_list = [s for s in (existing_apis.explicitItems or []) if not s.startswith("SemanticsLabelsAPI:")]
                if new_list != (existing_apis.explicitItems or []):
                    existing_apis.explicitItems = new_list
                    modified = True
            if getattr(existing_apis, "prependedItems", None) is not None:
                new_list = [s for s in (existing_apis.prependedItems or []) if not s.startswith("SemanticsLabelsAPI:")]
                if new_list != (existing_apis.prependedItems or []):
                    existing_apis.prependedItems = new_list
                    modified = True
            if getattr(existing_apis, "appendedItems", None) is not None:
                new_list = [s for s in (existing_apis.appendedItems or []) if not s.startswith("SemanticsLabelsAPI:")]
                if new_list != (existing_apis.appendedItems or []):
                    existing_apis.appendedItems = new_list
                    modified = True

            if modified:
                is_empty = not (
                    (existing_apis.explicitItems or [])
                    or (getattr(existing_apis, "prependedItems", None) or [])
                    or (getattr(existing_apis, "appendedItems", None) or [])
                )
                if is_empty:
                    prim_spec.ClearInfo("apiSchemas")
                else:
                    prim_spec.SetInfo("apiSchemas", existing_apis)

    def clear_semantics_legacy(prim):
        # Remove all applied schemas from legacy semantics API
        if prim.HasAPI(pxr.Semantics.SemanticsAPI):
            for schema in prim.GetAppliedSchemas():
                if schema.startswith("SemanticsAPI"):
                    prim.RemoveAppliedSchema(schema)

    with pxr.Sdf.ChangeBlock():
        for prim, sems in zip(prims, normalized_values):
            if isinstance(prim, usdrt.Usd.Prim):
                prim = stage.GetPrimAtPath(str(prim.GetPath()))
            elif not isinstance(prim, pxr.Usd.Prim):
                raise ValueError(f"Invalid prim type: {type(prim)}, expected `pxr.Usd.Prim` or `usdrt.Usd.Prim`")

            legacy_semantics = {}
            if prim.HasAPI(pxr.Semantics.SemanticsAPI):
                if mode.lower() != "clear":
                    legacy_semantics = utils.legacy_semantics_arg_to_new(utils.parse_semantics(prim))
                clear_semantics_legacy(prim)
            if mode.lower() == "clear":
                clear_semantics(prim)
            if isinstance(prim, usdrt.Usd.Prim):
                prim = stage.GetPrimAtPath(str(prim.GetPath()))
            for semantic_type, semantic_value in sems.items():
                if isinstance(semantic_value, str):
                    semantic_value = [semantic_value]
                if legacy_semantics and semantic_type in legacy_semantics:
                    semantic_value = legacy_semantics[semantic_type] + semantic_value
                add_semantics(prim, semantic_type, semantic_value, mode.lower())


def _modify_point_instancer_positions(
    prim: pxr.Usd.Prim, value: Union[List[Tuple[float, float, float]], np.ndarray], pivot=None
):
    """Modify positions of a point instancer prim.

    Args:
        prim: The point instancer prim to modify
        value: List of position values
        pivot: Optional pivot points for transforms

    Returns:
        int: Number of instances processed (to update offset)
    """
    proto_indices = prim.GetAttribute("protoIndices").Get()
    if proto_indices is None:
        return 0

    positions = []
    num_instances = len(proto_indices)

    if isinstance(value, np.ndarray) and len(value.shape) == 1:
        value = value.reshape(-1, 3).tolist()
    elif not isinstance(value[0], (tuple, list)):
        value = np.array(value).reshape(-1, 3).tolist()

    # Get positions for each instance
    for i in range(num_instances):
        curr_pos = value[i]

        # Handle pivot transformation for each instance if specified
        if pivot is not None and pivot[i] is not None:
            # Get prototype prim's bounding box
            proto_path = prim.GetAttribute("prototypes").Get()[proto_indices[i]]
            proto_prim = prim.GetStage().GetPrimAtPath(proto_path)
            bbox = pxr.UsdGeom.Boundable(proto_prim).ComputeWorldBound(
                pxr.Usd.TimeCode.Default(), purpose1=pxr.UsdGeom.Tokens.default_
            )
            bbox_range = bbox.GetRange()

            # Convert normalized pivot to world space
            pivot_point = -pxr.Gf.Vec3d(
                bbox_range.GetMin()[0] + (bbox_range.GetSize()[0] * (pivot[i][0] + 1) * 0.5),
                bbox_range.GetMin()[1] + (bbox_range.GetSize()[1] * (pivot[i][1] + 1) * 0.5),
                bbox_range.GetMin()[2] + (bbox_range.GetSize()[2] * (pivot[i][2] + 1) * 0.5),
            )

            # Apply pivot transformation
            pivot_transform = pxr.Gf.Matrix4d()
            pivot_transform.SetTranslate(pivot_point)
            curr_pos = pivot_transform.Transform(pxr.Gf.Vec3d(*curr_pos))

        positions.append(curr_pos)

    # Set positions attribute for all instances
    positions_attr = prim.GetAttribute("positions")
    if not positions_attr:
        positions_attr = prim.CreateAttribute("positions", pxr.Sdf.ValueTypeNames.Point3fArray, False)
    positions_attr.Set(positions)

    return num_instances


def _modify_point_instancer_rotations(prim, value, look_at=None, look_at_up_axis=(0, 1, 0), pivot=None):
    """Modify rotations of a point instancer prim.

    Args:
        prim (pxr.Usd.Prim): The point instancer prim to modify
        value (List[Union[Tuple[float, float, float], pxr.Gf.Rotation]]): List of rotation values
        look_at (Optional[List[Union[pxr.Usd.Prim, Tuple[float, float, float]]]]): Optional look-at targets
        look_at_up_axis (Tuple[float, float, float]): Up vector for look-at calculations
        pivot (Optional[List[Tuple[float, float, float]]]): Optional pivot points for transforms

    Returns:
        int: Number of instances processed (to update offset)
    """
    proto_indices = prim.GetAttribute("protoIndices").Get()
    if proto_indices is None:
        return 0

    rotations = []
    num_instances = len(proto_indices)

    stage_up_axis = pxr.UsdGeom.GetStageUpAxis(omni.usd.get_context().get_stage())

    # Get positions for look-at calculations if needed
    positions = None
    if look_at is not None:
        positions = prim.GetAttribute("positions").Get()

    if isinstance(value, np.ndarray) and len(value.shape) == 1:
        value = value.reshape(-1, 3).tolist()

    # Process each instance
    for i in range(num_instances):
        if look_at is not None:
            # Handle look-at rotation
            target = look_at[i] if isinstance(look_at, list) else look_at
            if isinstance(target, (pxr.Usd.Prim, usdrt.Usd.Prim)):
                xform_target = pxr.UsdGeom.Xformable(target).ComputeLocalToWorldTransform(pxr.Usd.TimeCode.Default())
                target_pos = xform_target.ExtractTranslation()
            else:
                target_pos = target

            eye_pos = positions[i] if positions is not None else pxr.Gf.Vec3d(0, 0, 0)
            rot = utils.look_at(target_pos, look_at_up_axis, eye_pos, stage_up_axis=stage_up_axis)
        else:
            # Handle direct rotation value
            rot = value[i]
            if isinstance(rot, (tuple, list, np.ndarray)) and len(rot) == 3:
                # Convert Euler angles to quaternion
                rot = (
                    pxr.Gf.Rotation(pxr.Gf.Vec3d.XAxis(), rot[0])
                    * pxr.Gf.Rotation(pxr.Gf.Vec3d.YAxis(), rot[1])
                    * pxr.Gf.Rotation(pxr.Gf.Vec3d.ZAxis(), rot[2])
                )
            elif isinstance(rot, (tuple, list, np.ndarray)) and len(rot) == 4:
                rot = pxr.Gf.Rotation(pxr.Gf.Quatd(*rot))
            else:
                raise ValueError(
                    f"Invalid rotation value: {rot} of type {type(rot)}. Expected tuple, list, or numpy array."
                )

        # Handle pivot transformation
        if pivot is not None and pivot[i] is not None:
            # Get prototype prim's bounding box
            proto_path = prim.GetAttribute("prototypes").Get()[proto_indices[i]]
            proto_prim = prim.GetStage().GetPrimAtPath(proto_path)
            bbox = pxr.UsdGeom.Boundable(proto_prim).ComputeWorldBound(
                pxr.Usd.TimeCode.Default(), purpose1=pxr.UsdGeom.Tokens.default_
            )
            bbox_range = bbox.GetRange()

            # Convert normalized pivot to world space
            pivot_point = pxr.Gf.Vec3d(
                bbox_range.GetMin()[0] + (bbox_range.GetSize()[0] * (pivot[i][0] + 1) * 0.5),
                bbox_range.GetMin()[1] + (bbox_range.GetSize()[1] * (pivot[i][1] + 1) * 0.5),
                bbox_range.GetMin()[2] + (bbox_range.GetSize()[2] * (pivot[i][2] + 1) * 0.5),
            )

            # Create pivot transform matrices
            pivot_transform = pxr.Gf.Matrix4d()
            pivot_transform.SetTranslate(pivot_point)
            inv_pivot_transform = pivot_transform.GetInverse()

            # Apply rotation around pivot
            rot_matrix = pxr.Gf.Matrix4d()
            rot_matrix.SetRotate(rot)
            final_matrix = pivot_transform * rot_matrix * inv_pivot_transform
            rot = pxr.Gf.Rotation(final_matrix.ExtractRotation())

        # Convert rotation to quaternion for point instancer
        rotations.append(pxr.Gf.Quath(rot.GetQuat()))

    # Set orientations attribute for all instances
    orientations_attr = prim.GetAttribute("orientations")
    if not orientations_attr:
        orientations_attr = prim.CreateAttribute("orientations", pxr.Sdf.ValueTypeNames.QuatfArray, False)
    orientations_attr.Set(rotations)

    return num_instances


def _modify_point_instancer_scales(prim, value):
    """Modify scales of a point instancer prim.

    Args:
        prim (pxr.Usd.Prim): The point instancer prim to modify
        value (List[Union[float, Tuple[float, float, float]]]): List of scale values

    Returns:
        int: Number of instances processed (to update offset)
    """
    proto_indices = prim.GetAttribute("protoIndices").Get()
    if proto_indices is None:
        return 0

    scales = []
    num_instances = len(proto_indices)

    # Process each instance
    for i in range(num_instances):
        scale_val = value[i]
        if isinstance(scale_val, (int, float)):
            scale_val = (scale_val, scale_val, scale_val)
        scales.append(scale_val)

    # Set scales attribute for all instances
    scales_attr = prim.GetAttribute("scales")
    if not scales_attr:
        scales_attr = prim.CreateAttribute("scales", pxr.Sdf.ValueTypeNames.Float3Array, False)
    scales_attr.Set(scales)

    return num_instances


def visibility(
    prims: Union[pxr.Usd.Prim, usdrt.Usd.Prim, List[Union[pxr.Usd.Prim, usdrt.Usd.Prim]]],
    value: Union[bool, List[bool]],
) -> None:
    """
    Sets the visibility attribute for one or more USD prims.

    Args:
        prims: A single prim or a list of prims (pxr.Usd.Prim or usdrt.Usd.Prim) whose visibility will be set.
        value: A boolean or list of booleans indicating visibility for each prim.
            True sets visibility to "inherited" (visible), False sets to "invisible".

    Raises:
        ValueError: If any value in `value` is not a boolean.
    """
    # Normalize prims to a list
    if isinstance(prims, (pxr.Usd.Prim, usdrt.Usd.Prim)):
        prims = [prims]

    # Normalize and validate value to a list of booleans
    if isinstance(value, bool):
        value = [value]

    if not all(isinstance(v, bool) for v in value):
        raise ValueError("Visibility value must be a boolean or list of booleans")

    # Batch values to match prim count
    value = f_utils.get_batched_value(value, prims)

    with pxr.Sdf.ChangeBlock():
        for idx, mesh in enumerate(prims):
            if mesh.HasAttribute("visibility"):
                mesh.GetAttribute("visibility").Set("inherited" if value[idx] else "invisible")
            else:
                carb.log_warn(f"{mesh} has no visibility attribute. Skipping...")


def material(
    prims: Union[pxr.Usd.Prim, usdrt.Usd.Prim, List[Union[pxr.Usd.Prim, usdrt.Usd.Prim]]],
    material_prim: Union[pxr.Usd.Prim, usdrt.Usd.Prim, List[Union[pxr.Usd.Prim, usdrt.Usd.Prim]]],
) -> None:
    """Modify the bound material of the prims specified in ``prims``.

    Args:
        prims (Union[pxr.Usd.Prim, usdrt.Usd.Prim, List[Union[pxr.Usd.Prim, usdrt.Usd.Prim]]]): A single prim or a list
            of prims to bind the material to.
        material_prim (Union[pxr.Usd.Prim, usdrt.Usd.Prim, List[Union[pxr.Usd.Prim, usdrt.Usd.Prim]]]): The material to
            bind to the prims. If multiple materials are provided, the number of materials must match the number of
            prims.
    """
    if prims is None or material_prim is None:
        raise ValueError("prims and material_prim cannot be None")

    if isinstance(prims, (pxr.Usd.Prim, usdrt.Usd.Prim)):
        prims = [prims]
    if isinstance(material_prim, (pxr.Usd.Prim, usdrt.Usd.Prim)):
        material_prim = [material_prim]

    material_prim = f_utils.get_batched_value(material_prim, prims)

    with pxr.Sdf.ChangeBlock():
        for prim, mat in zip(prims, material_prim):
            if mat.GetTypeName() != "Material":
                raise ValueError(f"`material_prim` {mat} is not a material type, got {mat.GetTypeName()}")

            mat = pxr.UsdShade.Material(mat)
            pxr.UsdShade.MaterialBindingAPI(prim).Bind(mat)
            pxr.UsdShade.MaterialBindingAPI.Apply(prim)
