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
import functools
from typing import Dict, List, Optional, Tuple, Union

import carb
import omni.client
import pxr
import usdrt
from omni.kit.primitive.mesh import evaluators

from ..utils import utils
from . import modify
from . import utils as f_utils

IGNORE_CREATE_ATTRIBUTES = [
    "CreateColorAttr",  # Function creates a Color3f, Vec3f expected
]


def _get_path(name: str, parent: Union[str, pxr.Sdf.Path, usdrt.Sdf.Path, pxr.Usd.Prim, usdrt.Usd.Prim]):
    """Gets a valid USD path by combining parent path and name.

    Args:
        name: Name for the new prim
        parent: Parent path or prim to create new prim under

    Returns:
        str: Combined valid USD path

    Raises:
        ValueError: If parent path is invalid
    """
    if not pxr.Tf.IsValidIdentifier(name):
        old_name = name
        name = pxr.Tf.MakeValidIdentifier(name)
        carb.log_warn(f"{old_name} is an invalid prim path. Renaming to {name}.")

    if isinstance(parent, (pxr.Usd.Prim, usdrt.Usd.Prim)):
        parent = parent.GetPath()

    if parent is None:
        parent = ""

    if parent and (
        not isinstance(parent, (str, pxr.Sdf.Path, usdrt.Sdf.Path)) or not pxr.Sdf.Path.IsValidPathString(str(parent))
    ):
        raise ValueError(f"Invalid parent prim: '{parent}'")

    return f"{parent}/{name}"


def _get_free_path_suffix(path: Union[str, pxr.Sdf.Path]) -> int:
    """Gets the next available numeric suffix for a path.

    Args:
        path: Base path to check for availability

    Returns:
        int: Next available numeric suffix (0 if base path is available)
    """
    stage = omni.usd.get_context().get_stage()
    suffix = 0
    cur_path = path
    while stage.GetPrimAtPath(cur_path):
        suffix += 1
        cur_path = f"{path}_{suffix:02}"
    return suffix


def _get_free_path_suffix_usdrt(path: Union[str, usdrt.Sdf.Path]) -> int:
    """Gets the next available numeric suffix for a path.

    Args:
        path: Base path to check for availability

    Returns:
        int: Next available numeric suffix (0 if base path is available)
    """
    stage = usdrt.Usd.Stage.Attach(omni.usd.get_context().get_stage_id())
    suffix = 0
    cur_path = path
    while stage.HasPrimAtPath(cur_path):
        suffix += 1
        cur_path = f"{path}_{suffix:02}"
    return suffix


def _get_next_free_path(path: Union[str, pxr.Sdf.Path]) -> pxr.Sdf.Path:
    """Gets the next available path by appending a numeric suffix if needed.

    Args:
        path: Base path to check for availability

    Returns:
        pxr.Sdf.Path: Available path with numeric suffix if needed
    """
    suffix_int = _get_free_path_suffix(path)
    suffix = "" if suffix_int == 0 else f"_{suffix_int:02}"
    return pxr.Sdf.Path(f"{str(path)}{suffix}")


def _get_next_free_path_usdrt(path: Union[str, usdrt.Sdf.Path]) -> usdrt.Sdf.Path:
    """Gets the next available path by appending a numeric suffix if needed.

    Args:
        path: Base path to check for availability

    Returns:
        pxr.Sdf.Path: Available path with numeric suffix if needed
    """
    suffix_int = _get_free_path_suffix_usdrt(path)
    suffix = "" if suffix_int == 0 else f"_{suffix_int:02}"
    return usdrt.Sdf.Path(f"{str(path)}{suffix}")


@functools.lru_cache()
def _get_mesh_data(mesh_type: str, up_axis: str, scale: float):
    """Gets mesh data (points, normals, etc.) for primitive mesh types.

    Args:
        mesh_type: Type of primitive mesh ('sphere', 'cube', etc.)
        up_axis: Axis to use for the up direction ('Y', 'Z', etc.)
        scale: Scale factor for the mesh

    Returns:
        tuple: Mesh data (points, normals, UVs, indices, face counts)

    Raises:
        ValueError: If mesh_type is unknown
    """
    evaluator_name = f"{mesh_type.lower().capitalize()}Evaluator"
    if hasattr(evaluators, evaluator_name):
        evaluator = getattr(evaluators, evaluator_name)({})
    else:
        raise ValueError(f"Unknown mesh type {mesh_type}")

    half_scale = evaluator.get_default_half_scale() * scale

    return evaluator.eval(half_scale=half_scale, up_axis=up_axis)


def _create_mesh(prim: usdrt.Usd.Prim, mesh_type: str, up_axis: str, scale: float):
    """Creates a mesh prim with geometry data.

    Args:
        prim: Prim to create mesh on
        mesh_type: Type of primitive mesh to create
        up_axis: Axis to use for the up direction ('Y', 'Z', etc.)
        scale: Scale factor for the mesh

    Returns:
        usdrt.Usd.Prim: Created mesh prim
    """
    if isinstance(prim, usdrt.Usd.Prim):
        mesh = usdrt.UsdGeom.Mesh(prim)
        mod = usdrt
    else:
        mesh = pxr.UsdGeom.Mesh(prim)
        mod = pxr

    points, normals, sts, point_indices, face_vertex_counts = _get_mesh_data(mesh_type, up_axis, scale)

    mesh.CreatePointsAttr().Set(mod.Vt.Vec3fArray(points))
    mesh.CreateFaceVertexIndicesAttr().Set(point_indices)
    mesh.CreateFaceVertexCountsAttr().Set(face_vertex_counts)

    primvar_api = mod.UsdGeom.PrimvarsAPI(prim)
    normals_primvar = primvar_api.CreatePrimvar("normals", mod.Sdf.ValueTypeNames.Vector3fArray)
    normals_primvar.SetInterpolation("faceVarying")
    normals_primvar.Set(mod.Vt.Vec3fArray(normals))

    sts_primvar = primvar_api.CreatePrimvar("st", mod.Sdf.ValueTypeNames.TexCoord2fArray)
    sts_primvar.SetInterpolation("faceVarying")
    sts_primvar.Set(mod.Vt.Vec2fArray(sts))
    mesh.CreateSubdivisionSchemeAttr().Set("none")

    attr = prim.GetAttribute(mod.UsdGeom.Tokens.extent)
    if attr:
        bounds = mod.UsdGeom.Boundable.ComputeExtentFromPlugins(mod.UsdGeom.Boundable(prim), mod.Usd.TimeCode.Default())
        if bounds:
            attr.Set(bounds)

    return prim


def _create_mdl_material_usdrt(mdl, path):
    stage = usdrt.Usd.Stage.Attach(omni.usd.get_context().get_stage_id())
    mdl_name = mdl.split(".mdl")[0]

    # create material
    mat_prim = stage.DefinePrim(path, "Material")
    mat = usdrt.UsdShade.Material(mat_prim)
    if mat:
        shader_prim = stage.DefinePrim(f"{path}/Shader", "Shader")
        shader = usdrt.UsdShade.Shader(shader_prim)
        if shader:
            shader_out = shader.CreateOutput("out", usdrt.Sdf.ValueTypeNames.Token)
            # shader_out.SetRenderType("material")

            mat.CreateSurfaceOutput("mdl").ConnectToSource(shader_out)
            mat.CreateVolumeOutput("mdl").ConnectToSource(shader_out)
            mat.CreateDisplacementOutput("mdl").ConnectToSource(shader_out)
            shader.CreateImplementationSourceAttr().Set(usdrt.UsdShade.Tokens.sourceAsset)
            shader.SetSourceAsset(usdrt.Sdf.AssetPath(mdl.replace("\\", "/")), "mdl")
            shader.SetSourceAssetSubIdentifier(mdl_name, "mdl")
        else:
            stage.RemovePrim(mat_prim)
            raise ValueError(f"failed to create shader {f'{path}/Shader'}")
    else:
        raise ValueError(f"failed to create prim {path}")

    return mat_prim, shader_prim


def _create_prim_spec(stage: pxr.Usd.Stage, path: str, prim_type: str):
    """Creates a new USD prim of specified type.

    Args:
        path: Path where prim should be created
        prim_type: Type of prim to create

    Returns:
        Union[pxr.Usd.Prim, usdrt.Usd.Prim]: Created prim

    Raises:
        ValueError: If path is invalid
    """
    if not pxr.Sdf.Path.IsValidPathString(str(path)):
        raise ValueError(f"Invalid prim path '{path}'.")

    path = _get_next_free_path(path)

    spec = pxr.Sdf.CreatePrimInLayer(stage.GetRootLayer(), path)
    spec.typeName = prim_type
    spec.specifier = pxr.Sdf.SpecifierDef
    return spec


def _set_transform_to_spec(prim_spec: pxr.Sdf.Spec, transform: pxr.Gf.Transform) -> None:
    """Sets transform attributes on a prim spec, preserving existing transform ops.

    Args:
        prim_spec: The USD prim spec to modify
        transform: Transform object containing translation, rotation and scale
    """
    prim_path = str(prim_spec.path)
    translation = transform.GetTranslation()
    rotation = transform.GetRotation()
    scale = transform.GetScale()

    # Check for existing transform
    transform_spec = prim_spec.GetAttributeAtPath(prim_path + ".xformOp:transform")
    if transform_spec is not None:
        transform_spec.default = transform.GetMatrix()
        return

    # Handle translation
    translate_spec = prim_spec.GetAttributeAtPath(prim_path + ".xformOp:translate")
    if translate_spec is None:
        translate_spec = pxr.Sdf.AttributeSpec(prim_spec, "xformOp:translate", pxr.Sdf.ValueTypeNames.Double3)
    translate_spec.default = translation

    # Check for existing rotation ops in priority order
    rotation_ops = [
        "xformOp:orient",
        "xformOp:rotateXYZ",
        "xformOp:rotateXZY",
        "xformOp:rotateYXZ",
        "xformOp:rotateYZX",
        "xformOp:rotateZXY",
        "xformOp:rotateZYX",
        "xformOp:rotateX",
        "xformOp:rotateY",
        "xformOp:rotateZ",
    ]

    existing_rot_spec = None
    existing_rot_op = None

    for rot_op in rotation_ops:
        spec = prim_spec.GetAttributeAtPath(prim_path + "." + rot_op)
        if spec is not None:
            existing_rot_spec = spec
            existing_rot_op = rot_op
            break

    # Handle rotation based on existing op or create new orient
    default_precision = carb.settings.get_settings().get_as_string("app/primCreation/DefaultXformOpPrecision")
    use_float = len(default_precision) > 0 and default_precision == "Float"

    if existing_rot_spec is not None:
        if existing_rot_op == "xformOp:orient":
            # Use existing orientation
            if use_float or (existing_rot_spec.default is not None and type(existing_rot_spec.default) == pxr.Gf.Quatf):
                existing_rot_spec.default = pxr.Gf.Quatf(rotation)
            else:
                existing_rot_spec.default = pxr.Gf.Quatd(rotation)
        elif existing_rot_op.startswith("xformOp:rotate"):
            # Handle existing rotation
            if len(existing_rot_op) == 14:  # Single axis rotation
                axis = existing_rot_op[-1]
                euler = rotation.Decompose()[0]
                if axis == "X":
                    existing_rot_spec.default = euler[0]
                elif axis == "Y":
                    existing_rot_spec.default = euler[1]
                    existing_rot_spec.default = euler[1]
                elif axis == "Z":
                    existing_rot_spec.default = euler[2]
            else:  # Three axis rotation
                existing_rot_spec.default = rotation.Decompose()[0]
                existing_rot_spec.default = rotation.Decompose()[0]
    else:
        # Create new orientation spec
        if use_float:
            orient_spec = pxr.Sdf.AttributeSpec(prim_spec, "xformOp:orient", pxr.Sdf.ValueTypeNames.Quatf)
            orient_spec.default = pxr.Gf.Quatf(rotation.GetQuat())
        else:
            orient_spec = pxr.Sdf.AttributeSpec(prim_spec, "xformOp:orient", pxr.Sdf.ValueTypeNames.Quatd)
            orient_spec.default = pxr.Gf.Quatd(rotation.GetQuat())
        existing_rot_spec = orient_spec
        existing_rot_op = "xformOp:orient"

    # Handle scale
    scale_spec = prim_spec.GetAttributeAtPath(prim_path + ".xformOp:scale")
    if scale_spec is None:
        scale_spec = pxr.Sdf.AttributeSpec(prim_spec, "xformOp:scale", pxr.Sdf.ValueTypeNames.Double3)
    scale_spec.default = scale

    # Handle transform op order
    op_order_spec = prim_spec.GetAttributeAtPath(prim_path + ".xformOpOrder")
    if op_order_spec is None:
        # Create new op order
        op_order_tokens = []
        if translate_spec:
            op_order_tokens.append("xformOp:translate")
        if existing_rot_spec:
            op_order_tokens.append(existing_rot_op)
        if scale_spec:
            op_order_tokens.append("xformOp:scale")

        op_order_spec = pxr.Sdf.AttributeSpec(
            prim_spec, pxr.UsdGeom.Tokens.xformOpOrder, pxr.Sdf.ValueTypeNames.TokenArray
        )
        op_order_spec.default = pxr.Vt.TokenArray(op_order_tokens)

    # Modify existing op order
    current_ops = list(op_order_spec.default)

    # Remove scale if it exists (will be added back at the end)
    if "xformOp:scale" in current_ops:
        current_ops.remove("xformOp:scale")

    # Add translate if not present
    if translate_spec and "xformOp:translate" not in current_ops:
        current_ops.insert(0, "xformOp:translate")

    # Handle rotation op
    existing_rot_ops = [op for op in current_ops if op.startswith("xformOp:rotate") or op == "xformOp:orient"]
    if existing_rot_spec and existing_rot_op not in current_ops:
        # Remove any existing rotation ops
        for rot_op in existing_rot_ops:
            current_ops.remove(rot_op)
        # Add new rotation op after translate
        translate_idx = current_ops.index("xformOp:translate") if "xformOp:translate" in current_ops else -1
        current_ops.insert(translate_idx + 1, existing_rot_op)

    # Add scale at the end
    if scale_spec:
        current_ops.append("xformOp:scale")

    op_order_spec.default = pxr.Vt.TokenArray(current_ops)


def _create_attributes(
    prim: Union[pxr.Usd.Prim, usdrt.Usd.Prim], attributes: List[Tuple[str, pxr.Sdf.ValueTypeNames, bool]]
):
    """Creates attributes on a prim.

    Args:
        prim: Prim to create attributes on
        attributes: List of (name, type, custom) tuples defining attributes
    """
    for attr_name, attr_type, is_custom in attributes:
        prim.CreateAttribute(attr_name, attr_type, is_custom)


def _check_valid_parent(stage: pxr.Usd.Stage, parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim]):
    """Checks if a parent is valid and raises an error if it is not.

    Args:
        stage: USD stage
        parent: Parent prim path to create under
    """
    if parent is None:
        return

    if isinstance(parent, str):
        parent_prim = stage.GetPrimAtPath(parent)
    elif isinstance(parent, (pxr.Sdf.Path, usdrt.Sdf.Path)):
        parent_prim = stage.GetPrimAtPath(str(parent))
    else:
        parent_prim = parent

    if not parent_prim.IsValid():
        raise ValueError(f"Parent {parent} is not a valid prim")

    if parent_prim.IsA(pxr.UsdGeom.Boundable):
        # https://openusd.org/release/glossary.html#usdglossary-gprim
        raise ValueError(f"Cannot parent to {parent}, as nested gprims are not supported")


def _create_prim_generic(
    prim_type_name: str,
    name: Optional[str] = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    as_mesh: bool = False,
    count: int = 1,
    new_attributes: List[Tuple[str, pxr.Sdf.ValueTypeNames, bool]] = [],
    schemas: List = [],
    **kwargs,
):
    """Generic function for creating USD prims with common functionality.

    Args:
        prim_type_name: Type of prim to create
        name: Name for the prim
        parent: Parent prim path to create under
        as_mesh: If True, creates as mesh version of prim type
        count: Number of prims to create
        new_attributes: List of attributes to create on prim
        schemas: List of schemas to apply to prim
        **kwargs: Additional attributes and properties to set

    Returns:
        List[Union[pxr.Usd.Prim, usdrt.Usd.Prim]]: List of created prims
    """
    if name is None:
        name = prim_type_name

    batched_kwargs = {}
    for k, v in kwargs.items():
        if v is None:
            continue
        batched_kwargs[k.replace("_col_", ":")] = f_utils.get_batched_value(v, count=count)

    prim_type = "Mesh" if as_mesh else prim_type_name
    pxr_stage = omni.usd.get_context().get_stage()
    usdrt_stage = usdrt.Usd.Stage.Attach(omni.usd.get_context().get_stage_id())

    path_templates = []
    if isinstance(parent, list):
        assert len(parent) == count
        for i in range(count):
            _check_valid_parent(pxr_stage, parent[i])
            path_templates.append(_get_path(name, parent[i]))
    else:
        _check_valid_parent(pxr_stage, parent)
        path = _get_path(name, parent)
        starting_suffix = _get_free_path_suffix(path)
        for i in range(starting_suffix, starting_suffix + count):
            cur_path = f"{path}_{i:02}" if i else path
            path_templates.append(cur_path)

    prim_paths = []
    is_fsd_enabled = f_utils.get_is_fsd_enabled()
    if is_fsd_enabled:
        for i in range(count):
            path = _get_next_free_path_usdrt(str(path_templates[i]))
            usdrt_stage.DefinePrim(path, prim_type)
            prim_paths.append(path)
    else:
        with pxr.Sdf.ChangeBlock():
            for i in range(count):
                if "source" in batched_kwargs:
                    prim_spec = pxr.Sdf.CreatePrimInLayer(pxr_stage.GetRootLayer(), path_templates[i])
                    pxr.Sdf.CopySpec(
                        prim_spec.layer,
                        pxr.Sdf.Path(batched_kwargs["source"][i]),
                        prim_spec.layer,
                        pxr.Sdf.Path(path_templates[i]),
                    )
                else:
                    prim_spec = _create_prim_spec(pxr_stage, path_templates[i], prim_type=prim_type)

                f_utils.apply_schemas(prim_spec, schemas)

                prim_paths.append(prim_spec.path)
                if "reference_usd_path" in batched_kwargs or "reference_prim_path" in batched_kwargs:
                    usd_path = (
                        str(batched_kwargs["reference_usd_path"][i]) if "reference_usd_path" in batched_kwargs else ""
                    )
                    prim_path = (
                        str(batched_kwargs["reference_prim_path"][i])
                        if "reference_prim_path" in batched_kwargs
                        else pxr.Sdf.Path()
                    )
                    ref = pxr.Sdf.Reference(assetPath=usd_path, primPath=prim_path)
                    prim_spec.referenceList.Prepend(ref)

    if "reference_usd_path" in batched_kwargs:
        batched_kwargs.pop("reference_usd_path")
    if "reference_prim_path" in batched_kwargs:
        batched_kwargs.pop("reference_prim_path")
    if "source" in batched_kwargs:
        batched_kwargs.pop("source")

    pose_kwargs = ("position", "rotation", "scale", "look_at", "look_at_up_axis", "pivot", "relative_to")

    prims = []
    ctx_mgr = contextlib.nullcontext if is_fsd_enabled else pxr.Sdf.ChangeBlock
    with ctx_mgr():
        for i, prim_path in enumerate(prim_paths):
            if is_fsd_enabled:
                prim = usdrt_stage.GetPrimAtPath(str(prim_path))
                # Add attribute to prims so they can be retrieved with selection API by name
                prim.CreateAttribute(f"tag:replicator:{name}", usdrt.Sdf.ValueTypeNames.Bool, True)
                usdrt.Rt.Xformable(prim).CreateFabricHierarchyLocalMatrixAttr()
                usdrt.Rt.Xformable(prim).CreateFabricHierarchyWorldMatrixAttr()
                usdrt.Rt.Boundable(prim).CreateWorldExtentAttr()
            else:
                prim = pxr_stage.GetPrimAtPath(str(prim_path))
            prims.append(prim)

            _create_attributes(prim, new_attributes)

            if as_mesh:
                _create_mesh(
                    prim,
                    mesh_type=prim_type_name,
                    up_axis=pxr.UsdGeom.GetStageUpAxis(pxr_stage),
                    scale=0.01 / pxr.UsdGeom.GetStageMetersPerUnit(pxr_stage),
                )

            for k, v in batched_kwargs.items():
                if k in pose_kwargs:
                    continue
                elif k == "visible":
                    if not prim.HasAttribute("visibility"):
                        sdf = usdrt.Sdf if is_fsd_enabled else pxr.Sdf
                        prim.CreateAttribute("visibility", sdf.ValueTypeNames.Token, True)
                    modify.attribute(prim, "visibility", "inherited" if v[i] else "invisible")
                elif k == "material":
                    modify.material(prim, v[i])
                elif k == "semantics":
                    modify.semantics(prim, v[i])
                else:
                    modify.attribute(prim, k, v[i])

    if any(k in batched_kwargs for k in pose_kwargs):
        modify.pose(
            prims=prims,
            position_value=batched_kwargs.get("position", None),
            rotation_value=batched_kwargs.get("rotation", None),
            scale_value=batched_kwargs.get("scale", None),
            look_at_value=batched_kwargs.get("look_at", None),
            look_at_up_axis=batched_kwargs.get("look_at_up_axis", None),
            pivot=batched_kwargs.get("pivot", None),
            relative_to=batched_kwargs.get("relative_to", None),
        )
    return prims


def scope(
    count: int = 1,
    name: Optional[str] = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
) -> List[pxr.Usd.Prim]:
    """Creates a scope prim for organizing scene hierarchy.

    Args:
        count: Number of scopes to create
        name: Name for the scope prim
        parent: Parent prim path to create scope under

    Returns:
        List[pxr.Usd.Prim]: List of created scope prims

    Example:
        >>> import omni.replicator.core.functional as F
        >>> scope = F.create_batch.scope(name="MyScope", parent="/World")
    """
    return _create_prim_generic(
        prim_type_name="Scope",
        name=name,
        parent=parent,
        count=count,
    )


def clone(
    path: Union[str, pxr.Sdf.Path, usdrt.Sdf.Path],
    position: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    scale: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    rotation: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    look_at: Union[
        str, pxr.Sdf.Path, usdrt.Sdf.Path, Tuple[float, float, float], List[Union[str, pxr.Sdf.Path, usdrt.Sdf.Path]]
    ] = None,
    look_at_up_axis: Union[Tuple[float]] = None,
    pivot: Union[Tuple[float, float, float], List[Tuple[float, float, float]], pxr.Gf.Vec3d] = None,
    relative_to: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    semantics: Union[Dict[str, Union[List, str]], List[Tuple[str, str]]] = None,
    visible: bool = True,
    count: int = 1,
    name: Optional[str] = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
) -> List[pxr.Usd.Prim]:
    """Creates a clone of a source prim.

    Args:
        source: Source prim to clone
        position: XYZ coordinates in world space. Can be single value (applies to all axes),
                 tuple (applies to XYZ), or list of tuples (one per prim)
        scale: Scaling factors for XYZ axes. Can be single value (applies to all axes),
               tuple (applies to XYZ), or list of tuples (one per prim)
        rotation: Euler angles in degrees (XYZ order). Can be single value (applies to all axes),
                  tuple (applies to XYZ), or list of tuples (one per prim)
        look_at: Target to point transform at (prim path, coordinates, or list of targets)
        look_at_up_axis: Up axis vector for look_at orientation
        pivot: Pivot point specified as a tuple of (x, y, z) normalized to the range [-1, 1] where 0 is the center of the prim
        relative_to: Reference prim for relative positioning. If provided, position will be relative to this prim
        semantics: Dictionary specifying semantic type and values. Legacy lists of tuples are also accepted but will be converted to dictionaries.
        visible: Whether transform should be visible
        count: Number of transforms to create
        name: Name for the transform prim
        parent: Parent prim path to create transform under

    Returns:
        List[pxr.Usd.Prim]: List of created transform prims

    Example:
        >>> import omni.replicator.core.functional as F
        >>> clone = F.create_batch.clone(source="/World/Sphere", position=(1, 2, 3))
    """
    return _create_prim_generic(
        source=path,
        prim_type_name="",
        name=name,
        parent=parent,
        count=count,
        position=position,
        rotation=rotation,
        scale=scale,
        look_at=look_at,
        look_at_up_axis=look_at_up_axis,
        pivot=pivot,
        relative_to=relative_to,
        semantics=semantics,
        visible=visible,
    )


def xform(
    position: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    scale: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    rotation: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    look_at: Union[
        str, pxr.Sdf.Path, usdrt.Sdf.Path, Tuple[float, float, float], List[Union[str, pxr.Sdf.Path, usdrt.Sdf.Path]]
    ] = None,
    look_at_up_axis: Union[Tuple[float]] = None,
    pivot: Union[Tuple[float, float, float], List[Tuple[float, float, float]], pxr.Gf.Vec3d] = None,
    relative_to: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    semantics: Union[Dict[str, Union[List, str]], List[Tuple[str, str]]] = None,
    visible: bool = True,
    count: int = 1,
    name: Optional[str] = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    material: Union[pxr.Usd.Prim, usdrt.Usd.Prim, List[Union[pxr.Usd.Prim, usdrt.Usd.Prim]]] = None,
) -> List[pxr.Usd.Prim]:
    """Creates a transform prim that can be used to group and transform other prims.

    Args:
        position: XYZ coordinates in world space. Can be single value (applies to all axes),
                 tuple (applies to XYZ), or list of tuples (one per prim)
        scale: Scale factors for XYZ axes. Can be single value (applies to all axes),
               tuple (applies to XYZ), or list of tuples (one per prim)
        rotation: Euler angles in degrees (XYZ order). Can be single value (applies to all axes),
                 tuple (applies to XYZ), or list of tuples (one per prim)
        look_at: Target to point transform at (prim path, coordinates, or list of targets)
        look_at_up_axis: Up axis vector for look_at orientation
        pivot: Pivot point specified as a tuple of (x, y, z) normalized to the range [-1, 1] where 0 is the center of the prim
        relative_to: Reference prim for relative positioning. If provided, position will be relative to this prim
        semantics: Dictionary specifying semantic type and values. Legacy lists of tuples are also accepted but will be converted to dictionaries.
        visible: Whether transform should be visible
        count: Number of transforms to create
        name: Name for the transform prim
        parent: Parent prim path to create transform under
        material: Material to bind to the created prim.

    Returns:
        List[pxr.Usd.Prim]: List of created transform prims

    Example:
        >>> import omni.replicator.core.functional as F
        >>> xform = F.create_batch.xform(
        ...     position=(1, 2, 3),
        ...     rotation=(0, 90, 0),
        ...     scale=2.0
        ... )
    """
    return _create_prim_generic(
        prim_type_name="Xform",
        name=name,
        parent=parent,
        count=count,
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
    )


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
    cross_camera_reference_name: Optional[str] = None,
    count: int = 1,
    name: Optional[str] = None,
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
        relative_to: Reference prim for relative positioning. If provided, position will be relative to this prim
        pivot: Pivot point specified as a tuple of (x, y, z) normalized to the range [-1, 1] where 0 is the center of the prim
        focal_length: Focal length of the camera.
        focus_distance: Distance to the focus plane.
        f_stop: F-stop of the camera.
        horizontal_aperture: Horizontal aperture of the camera.
        horizontal_aperture_offset: Horizontal aperture offset of the camera.
        vertical_aperture_offset: Vertical aperture offset of the camera.
        clipping_range: Clipping range of the camera.
        projection_type: Camera projection model. Select from ["pinhole", "pinholeOpenCV", "fisheyePolynomial",
            "fisheyeSpherical","fisheyeKannalaBrandtK3", "fisheyeOpenCV", "fisheyeRadTanThinPrism",
            "omniDirectionalStereo", "generalizedProjection"].
        fisheye_nominal_width: Nominal width of fisheye lens model.
        fisheye_nominal_height: Nominal height of fisheye lens model.
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
        count: Number of cameras to create.
        name: Name of the object.
        parent: Optional parent prim path. The xform will be created as a child of this prim.


    Example:
        >>> import omni.replicator.core as rep
        >>> camera = rep.create.camera(
        ...     position=rep.distribution.uniform((0,0,0), (100, 100, 100)),
        ... )
    """

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

    mod = usdrt if f_utils.get_is_fsd_enabled() else pxr

    new_attributes = [
        ("focalLength", mod.Sdf.ValueTypeNames.Float, False),
        ("focusDistance", mod.Sdf.ValueTypeNames.Float, False),
        ("fStop", mod.Sdf.ValueTypeNames.Float, False),
        ("horizontalAperture", mod.Sdf.ValueTypeNames.Float, False),
        ("horizontalApertureOffset", mod.Sdf.ValueTypeNames.Float, False),
        ("verticalApertureOffset", mod.Sdf.ValueTypeNames.Float, False),
        ("clippingRange", mod.Sdf.ValueTypeNames.Float2, False),
        ("cameraProjectionType", mod.Sdf.ValueTypeNames.Token, False),
        ("fthetaWidth", mod.Sdf.ValueTypeNames.Float, False),
        ("fthetaHeight", mod.Sdf.ValueTypeNames.Float, False),
        ("fthetaCx", mod.Sdf.ValueTypeNames.Float, False),
        ("fthetaCy", mod.Sdf.ValueTypeNames.Float, False),
        ("openCVFx", mod.Sdf.ValueTypeNames.Float, False),
        ("openCVFy", mod.Sdf.ValueTypeNames.Float, False),
        ("fthetaMaxFov", mod.Sdf.ValueTypeNames.Float, False),
        ("fthetaPolyA", mod.Sdf.ValueTypeNames.Float, False),
        ("fthetaPolyB", mod.Sdf.ValueTypeNames.Float, False),
        ("fthetaPolyC", mod.Sdf.ValueTypeNames.Float, False),
        ("fthetaPolyD", mod.Sdf.ValueTypeNames.Float, False),
        ("fthetaPolyE", mod.Sdf.ValueTypeNames.Float, False),
        ("fthetaPolyF", mod.Sdf.ValueTypeNames.Float, False),
        ("p0", mod.Sdf.ValueTypeNames.Float, False),
        ("p1", mod.Sdf.ValueTypeNames.Float, False),
        ("s0", mod.Sdf.ValueTypeNames.Float, False),
        ("s1", mod.Sdf.ValueTypeNames.Float, False),
        ("s2", mod.Sdf.ValueTypeNames.Float, False),
        ("s3", mod.Sdf.ValueTypeNames.Float, False),
        ("crossCameraReferenceName", mod.Sdf.ValueTypeNames.String, False),
    ]

    projection_type_split = projection_type.split("_")
    projection_type = "".join(projection_type_split[:1] + [t.capitalize() for t in projection_type_split[1:]])

    if projection_type not in VALID_PROJECTIONS:
        raise ValueError(f"Invalid projection {projection_type}. Select from {VALID_PROJECTIONS}")

    return _create_prim_generic(
        prim_type_name="Camera",
        new_attributes=new_attributes,
        schemas=["Camera"],
        name=name,
        parent=parent,
        count=count,
        position=position,
        scale=scale,
        rotation=rotation,
        look_at=look_at,
        look_at_up_axis=look_at_up_axis,
        relative_to=relative_to,
        focalLength=focal_length,
        focusDistance=focus_distance,
        fStop=f_stop,
        horizontalAperture=horizontal_aperture,
        horizontalApertureOffset=horizontal_aperture_offset,
        verticalApertureOffset=vertical_aperture_offset,
        clippingRange=clipping_range,
        cameraProjectionType=projection_type,
        fthetaWidth=fisheye_nominal_width,
        fthetaHeight=fisheye_nominal_height,
        fthetaCx=fisheye_optical_centre_x,
        fthetaCy=fisheye_optical_centre_y,
        openCVFx=openCV_focal_x,
        openCVFy=openCV_focal_y,
        fthetaMaxFov=fisheye_max_fov,
        fthetaPolyA=fisheye_polynomial_a,
        fthetaPolyB=fisheye_polynomial_b,
        fthetaPolyC=fisheye_polynomial_c,
        fthetaPolyD=fisheye_polynomial_d,
        fthetaPolyE=fisheye_polynomial_e,
        fthetaPolyF=fisheye_polynomial_f,
        p0=fisheye_p0,
        p1=fisheye_p1,
        s0=fisheye_s0,
        s1=fisheye_s1,
        s2=fisheye_s2,
        s3=fisheye_s3,
        crossCameraReferenceName=cross_camera_reference_name,
        projection="perspective",
        stereoRole="mono",
        shutter_col_open=0.0,
        shutter_col_close=0.0,
        clippingPlanes=[],
        purpose="default",
    )


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
    count: int = 1,
    name: Optional[str] = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
) -> List[pxr.Usd.Prim]:
    """Create a Xform

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
        pivot: Pivot point specified as a tuple of (x, y, z) normalized to the range [-1, 1] where 0 is the center of the prim
        relative_to: Reference prim for relative positioning. If provided, position will be relative to this prim
        semantics: List of semantic type-label pairs.
        visible: If ``False``, the prim will be invisible. This is often useful when creating prims to use as bounds
            with other randomizers.
        count: Number of objects to create.
        name: Name of the object.
        parent: Optional parent prim path. The xform will be created as a child of this prim.


    Example:
        >>> import omni.replicator.core as rep
        >>> xform = rep.create.xform(
        ...     position=rep.distribution.uniform((0,0,0), (100, 100, 100)),
        ...     semantics={"class": "thing"},
        ... )
    """
    if usd_path is None and prim_path is None:
        raise ValueError("Either usd_path or prim_path must be provided")

    return _create_prim_generic(
        prim_type_name="",
        name=name or "Ref",
        parent=parent,
        count=count,
        position=position,
        rotation=rotation,
        scale=scale,
        look_at=look_at,
        look_at_up_axis=look_at_up_axis,
        pivot=pivot,
        relative_to=relative_to,
        semantics=semantics,
        visible=visible,
        reference_usd_path=usd_path,
        reference_prim_path=prim_path,
    )


def plane(
    position: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    scale: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    rotation: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
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
    count: int = 1,
    name: Optional[str] = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    material: Union[pxr.Usd.Prim, usdrt.Usd.Prim, List[Union[pxr.Usd.Prim, usdrt.Usd.Prim]]] = None,
) -> List[pxr.Usd.Prim]:
    """Creates a plane mesh prim.

    Args:
        position: XYZ coordinates in world space. Can be single value (applies to all axes),
                 tuple (applies to XYZ), or list of tuples (one per prim)
        scale: Scale factors for XYZ axes. Can be single value (applies to all axes),
               tuple (applies to XYZ), or list of tuples (one per prim)
        rotation: Euler angles in degrees (XYZ order). Can be single value (applies to all axes),
                 tuple (applies to XYZ), or list of tuples (one per prim)
        look_at: Target to point plane at (prim path, coordinates, or list of targets)
        look_at_up_axis: Up axis vector for look_at orientation
        pivot: Pivot point specified as a tuple of (x, y, z) normalized to the range [-1, 1] where 0 is the center of the prim
        relative_to: Reference prim for relative positioning. If provided, position will be relative to this prim
        semantics: Dictionary specifying semantic type and values. Legacy lists of tuples are also accepted but will be converted to dictionaries.
        visible: Whether plane should be visible
        count: Number of planes to create
        name: Name for the plane prim
        parent: Parent prim path to create plane under
        material: Material to bind to the created prim.

    Returns:
        List[pxr.Usd.Prim]: List of created plane prims

    Example:
        >>> import omni.replicator.core.functional as F
        >>> plane = F.create_batch.plane(
        ...     position=(1, 2, 3),
        ...     scale=(2, 2, 1),
        ...     rotation=(90, 0, 0)
        ... )
    """
    return _create_prim_generic(
        prim_type_name="Plane",
        name=name,
        parent=parent,
        count=count,
        position=position,
        rotation=rotation,
        scale=scale,
        look_at=look_at,
        look_at_up_axis=look_at_up_axis,
        pivot=pivot,
        relative_to=relative_to,
        semantics=semantics,
        visible=visible,
        as_mesh=True,
        material=material,
    )


def sphere(
    position: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    scale: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    rotation: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    look_at: Union[
        str, pxr.Sdf.Path, usdrt.Sdf.Path, Tuple[float, float, float], List[Union[str, pxr.Sdf.Path, usdrt.Sdf.Path]]
    ] = None,
    look_at_up_axis: Union[Tuple[float]] = None,
    pivot: Union[Tuple[float, float, float], List[Tuple[float, float, float]], pxr.Gf.Vec3d] = None,
    relative_to: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    semantics: Union[Dict[str, Union[List, str]], List[Tuple[str, str]]] = None,
    visible: bool = True,
    as_mesh: bool = True,
    count: int = 1,
    name: Optional[str] = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    material: Union[pxr.Usd.Prim, usdrt.Usd.Prim, List[Union[pxr.Usd.Prim, usdrt.Usd.Prim]]] = None,
) -> List[pxr.Usd.Prim]:
    """Creates a sphere prim, either as a mesh or native USD sphere.

    Args:
        position: XYZ coordinates in world space. Can be single value (applies to all axes),
                 tuple (applies to XYZ), or list of tuples (one per prim)
        scale: Scale factors for XYZ axes. Can be single value (applies to all axes),
               tuple (applies to XYZ), or list of tuples (one per prim)
        rotation: Euler angles in degrees (XYZ order). Can be single value (applies to all axes),
                 tuple (applies to XYZ), or list of tuples (one per prim)
        look_at: Target to point sphere at (prim path, coordinates, or list of targets)
        look_at_up_axis: Up axis vector for look_at orientation
        pivot: Pivot point specified as a tuple of (x, y, z) normalized to the range [-1, 1] where 0 is the center of the prim
        relative_to: Reference prim for relative positioning. If provided, position will be relative to this prim
        semantics: Dictionary specifying semantic type and values. Legacy lists of tuples are also accepted but will be converted to dictionaries.
        visible: Whether sphere should be visible
        as_mesh: If True, creates a mesh sphere. If False, creates a native USD sphere
        count: Number of spheres to create
        name: Name for the sphere prim
        parent: Parent prim path to create sphere under
        material: Material to bind to the created prim.

    Returns:
        List[pxr.Usd.Prim]: List of created sphere prims

    Example:
        >>> import omni.replicator.core.functional as F
        >>> sphere = F.create_batch.sphere(
        ...     position=(0, 1, 0),
        ...     scale=0.5,
        ...     as_mesh=True
        ... )
    """
    return _create_prim_generic(
        prim_type_name="Sphere",
        name=name,
        parent=parent,
        count=count,
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
    )


def cube(
    position: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    scale: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    rotation: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    look_at: Union[
        str, pxr.Sdf.Path, usdrt.Sdf.Path, Tuple[float, float, float], List[Union[str, pxr.Sdf.Path, usdrt.Sdf.Path]]
    ] = None,
    look_at_up_axis: Union[Tuple[float]] = None,
    pivot: Union[Tuple[float, float, float], List[Tuple[float, float, float]], pxr.Gf.Vec3d] = None,
    relative_to: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    semantics: Union[Dict[str, Union[List, str]], List[Tuple[str, str]]] = None,
    visible: bool = True,
    as_mesh: bool = True,
    count: int = 1,
    name: Optional[str] = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    material: Union[pxr.Usd.Prim, usdrt.Usd.Prim, List[Union[pxr.Usd.Prim, usdrt.Usd.Prim]]] = None,
) -> List[pxr.Usd.Prim]:
    """Creates a cube prim, either as a mesh or native USD cube.

    Args:
        position: XYZ coordinates in world space. Can be single value (applies to all axes),
                 tuple (applies to XYZ), or list of tuples (one per prim)
        scale: Scale factors for XYZ axes. Can be single value (applies to all axes),
               tuple (applies to XYZ), or list of tuples (one per prim)
        rotation: Euler angles in degrees (XYZ order). Can be single value (applies to all axes),
                 tuple (applies to XYZ), or list of tuples (one per prim)
        look_at: Target to point cube at (prim path, coordinates, or list of targets)
        look_at_up_axis: Up axis vector for look_at orientation
        pivot: Pivot point specified as a tuple of (x, y, z) normalized to the range [-1, 1] where 0 is the center of the prim
        relative_to: Reference prim for relative positioning. If provided, position will be relative to this prim
        semantics: Dictionary specifying semantic type and values. Legacy lists of tuples are also accepted but will be converted to dictionaries.
        visible: Whether cube should be visible
        as_mesh: If True, creates a mesh cube. If False, creates a native USD cube
        count: Number of cubes to create
        name: Name for the cube prim
        parent: Parent prim path to create cube under
        material: Material to bind to the created prim.

    Returns:
        List[pxr.Usd.Prim]: List of created cube prims

    Example:
        >>> import omni.replicator.core.functional as F
        >>> cube = F.create_batch.cube(
        ...     position=(0, 1, 0),
        ...     scale=0.5,
        ...     as_mesh=True
        ... )
    """
    return _create_prim_generic(
        prim_type_name="Cube",
        name=name,
        parent=parent,
        count=count,
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
    )


def disk(
    position: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    scale: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    rotation: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    look_at: Union[
        str, pxr.Sdf.Path, usdrt.Sdf.Path, Tuple[float, float, float], List[Union[str, pxr.Sdf.Path, usdrt.Sdf.Path]]
    ] = None,
    look_at_up_axis: Union[Tuple[float]] = None,
    pivot: Union[Tuple[float, float, float], List[Tuple[float, float, float]], pxr.Gf.Vec3d] = None,
    relative_to: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    semantics: Union[Dict[str, Union[List, str]], List[Tuple[str, str]]] = None,
    visible: bool = True,
    count: int = 1,
    name: Optional[str] = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    material: Union[pxr.Usd.Prim, usdrt.Usd.Prim, List[Union[pxr.Usd.Prim, usdrt.Usd.Prim]]] = None,
) -> List[pxr.Usd.Prim]:
    """Creates a disk mesh prim.

    Args:
        position: XYZ coordinates in world space. Can be single value (applies to all axes),
                 tuple (applies to XYZ), or list of tuples (one per prim)
        scale: Scale factors for XYZ axes. Can be single value (applies to all axes),
               tuple (applies to XYZ), or list of tuples (one per prim)
        rotation: Euler angles in degrees (XYZ order). Can be single value (applies to all axes),
                 tuple (applies to XYZ), or list of tuples (one per prim)
        look_at: Target to point disk at (prim path, coordinates, or list of targets)
        look_at_up_axis: Up axis vector for look_at orientation
        pivot: Pivot point specified as a tuple of (x, y, z) normalized to the range [-1, 1] where 0 is the center of the prim
        relative_to: Reference prim for relative positioning. If provided, position will be relative to this prim
        semantics: Dictionary specifying semantic type and values. Legacy lists of tuples are also accepted but will be converted to dictionaries.
        visible: Whether disk should be visible
        count: Number of disks to create
        name: Name for the disk prim
        parent: Parent prim path to create disk under
        material: Material to bind to the created prim.

    Returns:
        List[pxr.Usd.Prim]: List of created disk prims

    Example:
        >>> import omni.replicator.core.functional as F
        >>> disk = F.create_batch.disk(
        ...     position=(0, 1, 0),
        ...     scale=0.5,
        ... )
    """
    return _create_prim_generic(
        prim_type_name="Disk",
        name=name,
        parent=parent,
        count=count,
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
    )


def torus(
    position: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    scale: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    rotation: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    look_at: Union[
        str, pxr.Sdf.Path, usdrt.Sdf.Path, Tuple[float, float, float], List[Union[str, pxr.Sdf.Path, usdrt.Sdf.Path]]
    ] = None,
    look_at_up_axis: Union[Tuple[float]] = None,
    pivot: Union[Tuple[float, float, float], List[Tuple[float, float, float]], pxr.Gf.Vec3d] = None,
    relative_to: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    semantics: Union[Dict[str, Union[List, str]], List[Tuple[str, str]]] = None,
    visible: bool = True,
    count: int = 1,
    name: Optional[str] = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    material: Union[pxr.Usd.Prim, usdrt.Usd.Prim, List[Union[pxr.Usd.Prim, usdrt.Usd.Prim]]] = None,
) -> List[pxr.Usd.Prim]:
    """Creates a torus mesh prim.

    Args:
        position: XYZ coordinates in world space. Can be single value (applies to all axes),
                 tuple (applies to XYZ), or list of tuples (one per prim)
        scale: Scale factors for XYZ axes. Can be single value (applies to all axes),
               tuple (applies to XYZ), or list of tuples (one per prim)
        rotation: Euler angles in degrees (XYZ order). Can be single value (applies to all axes),
                 tuple (applies to XYZ), or list of tuples (one per prim)
        look_at: Target to point torus at (prim path, coordinates, or list of targets)
        look_at_up_axis: Up axis vector for look_at orientation
        pivot: Pivot point specified as a tuple of (x, y, z) normalized to the range [-1, 1] where 0 is the center of the prim
        relative_to: Reference prim for relative positioning. If provided, position will be relative to this prim
        semantics: Dictionary specifying semantic type and values. Legacy lists of tuples are also accepted but will be converted to dictionaries.
        visible: Whether torus should be visible
        count: Number of toruses to create
        name: Name for the torus prim
        parent: Parent prim path to create torus under
        material: Material to bind to the created prim.

    Returns:
        List[pxr.Usd.Prim]: List of created torus prims

    Example:
        >>> import omni.replicator.core.functional as F
        >>> torus = F.create_batch.torus(
        ...     position=(0, 1, 0),
        ...     scale=0.5,
        ... )
    """
    return _create_prim_generic(
        prim_type_name="Torus",
        name=name,
        parent=parent,
        count=count,
        position=position,
        rotation=rotation,
        scale=scale,
        look_at=look_at,
        look_at_up_axis=look_at_up_axis,
        pivot=pivot,
        as_mesh=True,
        relative_to=relative_to,
        semantics=semantics,
        visible=visible,
        material=material,
    )


def cylinder(
    position: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    scale: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    rotation: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    look_at: Union[
        str, pxr.Sdf.Path, usdrt.Sdf.Path, Tuple[float, float, float], List[Union[str, pxr.Sdf.Path, usdrt.Sdf.Path]]
    ] = None,
    look_at_up_axis: Union[Tuple[float]] = None,
    pivot: Union[Tuple[float, float, float], List[Tuple[float, float, float]], pxr.Gf.Vec3d] = None,
    relative_to: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    semantics: Union[Dict[str, Union[List, str]], List[Tuple[str, str]]] = None,
    as_mesh: bool = True,
    visible: bool = True,
    count: int = 1,
    name: Optional[str] = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    material: Union[pxr.Usd.Prim, usdrt.Usd.Prim, List[Union[pxr.Usd.Prim, usdrt.Usd.Prim]]] = None,
) -> List[pxr.Usd.Prim]:
    """Creates a cylinder prim, either as a mesh or native USD cylinder.

    Args:
        position: XYZ coordinates in world space. Can be single value (applies to all axes),
                 tuple (applies to XYZ), or list of tuples (one per prim)
        scale: Scale factors for XYZ axes. Can be single value (applies to all axes),
               tuple (applies to XYZ), or list of tuples (one per prim)
        rotation: Euler angles in degrees (XYZ order). Can be single value (applies to all axes),
                 tuple (applies to XYZ), or list of tuples (one per prim)
        look_at: Target to point cylinder at (prim path, coordinates, or list of targets)
        look_at_up_axis: Up axis vector for look_at orientation
        pivot: Pivot point specified as a tuple of (x, y, z) normalized to the range [-1, 1] where 0 is the center of the prim
        relative_to: Reference prim for relative positioning. If provided, position will be relative to this prim
        semantics: Dictionary specifying semantic type and values. Legacy lists of tuples are also accepted but will be converted to dictionaries.
        as_mesh: If True, creates a mesh cylinder. If False, creates a native USD cylinder
        visible: Whether cylinder should be visible
        count: Number of cylinders to create
        name: Name for the cylinder prim
        parent: Parent prim path to create cylinder under
        material: Material to bind to the created prim.

    Returns:
        List[pxr.Usd.Prim]: List of created cylinder prims

    Example:
        >>> import omni.replicator.core.functional as F
        >>> cylinder = F.create_batch.cylinder(
        ...     position=(0, 0, 0),
        ...     scale=(0.5, 0.5, 2.0),
        ...     rotation=(0, 0, 90)
        ... )
    """
    return _create_prim_generic(
        prim_type_name="Cylinder",
        name=name,
        parent=parent,
        count=count,
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
    )


def cone(
    position: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    scale: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    rotation: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    look_at: Union[
        str, pxr.Sdf.Path, usdrt.Sdf.Path, Tuple[float, float, float], List[Union[str, pxr.Sdf.Path, usdrt.Sdf.Path]]
    ] = None,
    look_at_up_axis: Union[Tuple[float]] = None,
    pivot: Union[Tuple[float, float, float], List[Tuple[float, float, float]], pxr.Gf.Vec3d] = None,
    relative_to: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    semantics: Union[Dict[str, Union[List, str]], List[Tuple[str, str]]] = None,
    visible: bool = True,
    as_mesh: bool = True,
    count: int = 1,
    name: Optional[str] = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    material: Union[pxr.Usd.Prim, usdrt.Usd.Prim, List[Union[pxr.Usd.Prim, usdrt.Usd.Prim]]] = None,
) -> List[pxr.Usd.Prim]:
    """Creates a cone prim, either as a mesh or native USD cone.

    Args:
        position: XYZ coordinates in world space. Can be single value (applies to all axes),
                 tuple (applies to XYZ), or list of tuples (one per prim)
        scale: Scale factors for XYZ axes. Can be single value (applies to all axes),
               tuple (applies to XYZ), or list of tuples (one per prim)
        rotation: Euler angles in degrees (XYZ order). Can be single value (applies to all axes),
                 tuple (applies to XYZ), or list of tuples (one per prim)
        look_at: Target to point cone at (prim path, coordinates, or list of targets)
        look_at_up_axis: Up axis vector for look_at orientation
        pivot: Pivot point specified as a tuple of (x, y, z) normalized to the range [-1, 1] where 0 is the center of the prim
        relative_to: Reference prim for relative positioning. If provided, position will be relative to this prim
        semantics: Dictionary specifying semantic type and values. Legacy lists of tuples are also accepted but will be converted to dictionaries.
        visible: Whether cone should be visible
        as_mesh: If True, creates a mesh cone. If False, creates a native USD cone
        count: Number of cones to create
        name: Name for the cone prim
        parent: Parent prim path to create cone under
        material: Material to bind to the created prim.

    Returns:
        List[pxr.Usd.Prim]: List of created cone prims

    Example:
        >>> import omni.replicator.core.functional as F
        >>> cone = F.create_batch.cone(
        ...     position=(0, 1, 0),
        ...     scale=(1, 1, 2),
        ...     rotation=(180, 0, 0)
        ... )
    """
    return _create_prim_generic(
        prim_type_name="Cone",
        name=name,
        parent=parent,
        count=count,
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
    )


def sphere_light(
    position: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    scale: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    rotation: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    look_at: Union[
        str, pxr.Sdf.Path, usdrt.Sdf.Path, Tuple[float, float, float], List[Union[str, pxr.Sdf.Path, usdrt.Sdf.Path]]
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
    count: int = 1,
    name: Optional[str] = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
) -> List[pxr.Usd.Prim]:
    """Creates a sphere light prim with configurable lighting properties.

    Args:
        position: XYZ coordinates in world space. Can be single value (applies to all axes),
                 tuple (applies to XYZ), or list of tuples (one per prim)
        scale: Scale factors for XYZ axes. Can be single value (applies to all axes),
               tuple (applies to XYZ), or list of tuples (one per prim)
        rotation: Euler angles in degrees (XYZ order). Can be single value (applies to all axes),
                 tuple (applies to XYZ), or list of tuples (one per prim)
        look_at: Target to point light at (prim path, coordinates, or list of targets)
        look_at_up_axis: Up axis vector for look_at orientation
        pivot: Pivot point specified as a tuple of (x, y, z) normalized to the range [-1, 1] where 0 is the center of the prim
        relative_to: Reference prim for relative positioning. If provided, position will be relative to this prim
        semantics: Dictionary specifying semantic type and values. Legacy lists of tuples are also accepted but will be converted to dictionaries.
        visible: Whether light should be visible
        color: RGB color of the light (0-1 range)
        intensity: Light intensity in lumens
        exposure: Light exposure value
        color_temperature: Color temperature in Kelvin
        enable_color_temperature: Whether to use color temperature
        diffuse: Diffuse contribution multiplier
        specular: Specular contribution multiplier
        shaping_cone_angle: Angle of the light cone in degrees
        shaping_cone_softness: Softness of the light cone
        shaping_focus_tint: RGB tint color for focused area
        radius: Radius of the sphere light
        count: Number of lights to create
        name: Name for the light prim
        parent: Parent prim path to create light under

    Returns:
        List[pxr.Usd.Prim]: List of created sphere light prims

    Example:
        >>> import omni.replicator.core.functional as F
        >>> light = F.create_batch.sphere_light(
        ...     position=(0, 2, 0),
        ...     color=(1, 0.8, 0.6),
        ...     intensity=50000,
        ...     radius=0.5
        ... )
    """
    is_fsd_enabled = f_utils.get_is_fsd_enabled()
    sdf = usdrt.Sdf if is_fsd_enabled else pxr.Sdf
    return _create_prim_generic(
        prim_type_name="SphereLight",
        name=name,
        parent=parent,
        count=count,
        position=position,
        rotation=rotation,
        scale=scale,
        look_at=look_at,
        look_at_up_axis=look_at_up_axis,
        pivot=pivot,
        relative_to=relative_to,
        semantics=semantics,
        visible=visible,
        new_attributes=[
            ("inputs:radius", sdf.ValueTypeNames.Float, False),
            ("inputs:color", sdf.ValueTypeNames.Float3, False),
            ("inputs:shaping:focusTint", sdf.ValueTypeNames.Float3, False),
            ("treatAsPoint", sdf.ValueTypeNames.Bool, False),
            ("visibility", sdf.ValueTypeNames.Token, False),
            ("visibleInPrimaryRay", sdf.ValueTypeNames.Bool, True),
        ],
        inputs_col_radius=radius,
        inputs_col_color=color,
        inputs_col_diffuse=diffuse,
        inputs_col_specular=specular,
        inputs_col_colorTemperature=color_temperature,
        inputs_col_enableColorTemperature=enable_color_temperature,
        inputs_col_exposure=exposure,
        inputs_col_intensity=intensity,
        inputs_col_shaping_col_focusTint=shaping_focus_tint,
        inputs_col_shaping_col_cone_col_angle=shaping_cone_angle,
        inputs_col_shaping_col_cone_col_softness=shaping_cone_softness,
        schemas=["LightAPI", "ShapingAPI", "ShadowAPI"],
    )


def disk_light(
    position: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    scale: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    rotation: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    look_at: Union[
        str, pxr.Sdf.Path, usdrt.Sdf.Path, Tuple[float, float, float], List[Union[str, pxr.Sdf.Path, usdrt.Sdf.Path]]
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
    count: int = 1,
    name: Optional[str] = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
) -> List[pxr.Usd.Prim]:
    """Creates a disk light prim with configurable lighting properties.

    Args:
        position: XYZ coordinates in world space. Can be single value (applies to all axes),
                 tuple (applies to XYZ), or list of tuples (one per prim)
        scale: Scale factors for XYZ axes. Can be single value (applies to all axes),
               tuple (applies to XYZ), or list of tuples (one per prim)
        rotation: Euler angles in degrees (XYZ order). Can be single value (applies to all axes),
                 tuple (applies to XYZ), or list of tuples (one per prim)
        look_at: Target to point light at (prim path, coordinates, or list of targets)
        look_at_up_axis: Up axis vector for look_at orientation
        pivot: Pivot point specified as a tuple of (x, y, z) normalized to the range [-1, 1] where 0 is the center of the prim
        relative_to: Reference prim for relative positioning. If provided, position will be relative to this prim
        semantics: Dictionary specifying semantic type and values. Legacy lists of tuples are also accepted but will be converted to dictionaries.
        visible: Whether light should be visible
        color: RGB color of the light (0-1 range)
        intensity: Light intensity in lumens
        exposure: Light exposure value
        color_temperature: Color temperature in Kelvin
        enable_color_temperature: Whether to use color temperature
        diffuse: Diffuse contribution multiplier
        specular: Specular contribution multiplier
        shaping_cone_angle: Angle of the light cone in degrees
        shaping_cone_softness: Softness of the light cone
        shaping_focus_tint: RGB tint color for focused area
        radius: Radius of the disk light
        count: Number of lights to create
        name: Name for the light prim
        parent: Parent prim path to create light under

    Returns:
        List[pxr.Usd.Prim]: List of created disk light prims

    Example:
        >>> import omni.replicator.core.functional as F
        >>> light = F.create_batch.disk_light(
        ...     position=(0, 2, 0),
        ...     color=(1, 0.8, 0.6),
        ...     intensity=50000,
        ...     radius=0.5
        ... )
    """
    is_fsd_enabled = f_utils.get_is_fsd_enabled()
    sdf = usdrt.Sdf if is_fsd_enabled else pxr.Sdf
    return _create_prim_generic(
        prim_type_name="DiskLight",
        name=name,
        parent=parent,
        count=count,
        position=position,
        rotation=rotation,
        scale=scale,
        look_at=look_at,
        look_at_up_axis=look_at_up_axis,
        pivot=pivot,
        relative_to=relative_to,
        semantics=semantics,
        visible=visible,
        new_attributes=[
            ("inputs:radius", sdf.ValueTypeNames.Float, False),
            ("inputs:color", sdf.ValueTypeNames.Float3, False),
            ("inputs:shaping:focusTint", sdf.ValueTypeNames.Float3, False),
            ("treatAsPoint", sdf.ValueTypeNames.Bool, False),
            ("visibility", sdf.ValueTypeNames.Token, False),
            ("visibleInPrimaryRay", sdf.ValueTypeNames.Bool, True),
        ],
        inputs_col_radius=radius,
        inputs_col_color=color,
        inputs_col_diffuse=diffuse,
        inputs_col_specular=specular,
        inputs_col_colorTemperature=color_temperature,
        inputs_col_enableColorTemperature=enable_color_temperature,
        inputs_col_exposure=exposure,
        inputs_col_intensity=intensity,
        inputs_col_shaping_col_focusTint=shaping_focus_tint,
        inputs_col_shaping_col_cone_col_angle=shaping_cone_angle,
        inputs_col_shaping_col_cone_col_softness=shaping_cone_softness,
        schemas=["LightAPI", "ShapingAPI", "ShadowAPI"],
    )


def rect_light(
    position: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    scale: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    rotation: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    look_at: Union[
        str, pxr.Sdf.Path, usdrt.Sdf.Path, Tuple[float, float, float], List[Union[str, pxr.Sdf.Path, usdrt.Sdf.Path]]
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
    count: int = 1,
    name: Optional[str] = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
) -> List[pxr.Usd.Prim]:
    """Creates a rectangle light prim with configurable lighting properties.

    Args:
        position: XYZ coordinates in world space. Can be single value (applies to all axes),
                 tuple (applies to XYZ), or list of tuples (one per prim)
        scale: Scale factors for XYZ axes. Can be single value (applies to all axes),
               tuple (applies to XYZ), or list of tuples (one per prim)
        rotation: Euler angles in degrees (XYZ order). Can be single value (applies to all axes),
                 tuple (applies to XYZ), or list of tuples (one per prim)
        look_at: Target to point light at (prim path, coordinates, or list of targets)
        look_at_up_axis: Up axis vector for look_at orientation
        pivot: Pivot point specified as a tuple of (x, y, z) normalized to the range [-1, 1] where 0 is the center of the prim
        relative_to: Reference prim for relative positioning. If provided, position will be relative to this prim
        semantics: Dictionary specifying semantic type and values. Legacy lists of tuples are also accepted but will be converted to dictionaries.
        visible: Whether light should be visible
        color: RGB color of the light (0-1 range)
        intensity: Light intensity in lumens
        exposure: Light exposure value
        color_temperature: Color temperature in Kelvin
        enable_color_temperature: Whether to use color temperature
        diffuse: Diffuse contribution multiplier
        specular: Specular contribution multiplier
        shaping_cone_angle: Angle of the light cone in degrees
        shaping_cone_softness: Softness of the light cone
        shaping_focus_tint: RGB tint color for focused area
        height: Height of the rectangle light
        width: Width of the rectangle light
        count: Number of lights to create
        name: Name for the light prim
        parent: Parent prim path to create light under

    Returns:
        List[pxr.Usd.Prim]: List of created rectangle light prims

    Example:
        >>> import omni.replicator.core.functional as F
        >>> light = F.create_batch.rect_light(
        ...     position=(0, 2, 0),
        ...     color=(1, 0.8, 0.6),
        ...     intensity=50000,
        ...     height=0.5,
        ...     width=0.5
        ... )
    """
    is_fsd_enabled = f_utils.get_is_fsd_enabled()
    sdf = usdrt.Sdf if is_fsd_enabled else pxr.Sdf
    return _create_prim_generic(
        prim_type_name="RectLight",
        name=name,
        parent=parent,
        count=count,
        position=position,
        rotation=rotation,
        scale=scale,
        look_at=look_at,
        look_at_up_axis=look_at_up_axis,
        pivot=pivot,
        relative_to=relative_to,
        semantics=semantics,
        visible=visible,
        new_attributes=[
            ("inputs:height", sdf.ValueTypeNames.Float, False),
            ("inputs:width", sdf.ValueTypeNames.Float, False),
            ("inputs:color", sdf.ValueTypeNames.Float3, False),
            ("inputs:shaping:focusTint", sdf.ValueTypeNames.Float3, False),
            ("treatAsPoint", sdf.ValueTypeNames.Bool, False),
            ("visibility", sdf.ValueTypeNames.Token, False),
            ("visibleInPrimaryRay", sdf.ValueTypeNames.Bool, True),
        ],
        inputs_col_height=height,
        inputs_col_width=width,
        inputs_col_color=color,
        inputs_col_diffuse=diffuse,
        inputs_col_specular=specular,
        inputs_col_colorTemperature=color_temperature,
        inputs_col_enableColorTemperature=enable_color_temperature,
        inputs_col_exposure=exposure,
        inputs_col_intensity=intensity,
        inputs_col_shaping_col_focusTint=shaping_focus_tint,
        inputs_col_shaping_col_cone_col_angle=shaping_cone_angle,
        inputs_col_shaping_col_cone_col_softness=shaping_cone_softness,
        schemas=["LightAPI", "ShapingAPI", "ShadowAPI"],
    )


def cylinder_light(
    position: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    scale: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    rotation: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    look_at: Union[
        str, pxr.Sdf.Path, usdrt.Sdf.Path, Tuple[float, float, float], List[Union[str, pxr.Sdf.Path, usdrt.Sdf.Path]]
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
    count: int = 1,
    name: Optional[str] = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
) -> List[pxr.Usd.Prim]:
    """Creates a cylinder light prim with configurable lighting properties.

    Args:
        position: XYZ coordinates in world space. Can be single value (applies to all axes),
                 tuple (applies to XYZ), or list of tuples (one per prim)
        scale: Scale factors for XYZ axes. Can be single value (applies to all axes),
               tuple (applies to XYZ), or list of tuples (one per prim)
        rotation: Euler angles in degrees (XYZ order). Can be single value (applies to all axes),
                 tuple (applies to XYZ), or list of tuples (one per prim)
        look_at: Target to point light at (prim path, coordinates, or list of targets)
        look_at_up_axis: Up axis vector for look_at orientation
        pivot: Pivot point specified as a tuple of (x, y, z) normalized to the range [-1, 1] where 0 is the center of the prim
        relative_to: Reference prim for relative positioning. If provided, position will be relative to this prim
        semantics: Dictionary specifying semantic type and values. Legacy lists of tuples are also accepted but will be converted to dictionaries.
        visible: Whether light should be visible
        color: RGB color of the light (0-1 range)
        intensity: Light intensity in lumens
        exposure: Light exposure value
        color_temperature: Color temperature in Kelvin
        enable_color_temperature: Whether to use color temperature
        diffuse: Diffuse contribution multiplier
        specular: Specular contribution multiplier
        shaping_cone_angle: Angle of the light cone in degrees
        shaping_focus_tint: RGB tint color for focused area
        shaping_cone_softness: Softness of the light cone
        radius: Radius of the cylinder light
        length: Length of the cylinder light
        count: Number of lights to create
        name: Name for the light prim
        parent: Parent prim path to create light under

    Returns:
        List[pxr.Usd.Prim]: List of created cylinder light prims

    Example:
        >>> import omni.replicator.core.functional as F
        >>> light = F.create_batch.cylinder_light(
        ...     position=(0, 2, 0),
        ...     color=(1, 0.8, 0.6),
        ...     intensity=50000,
        ...     radius=0.5,
        ...     length=0.5
        ... )
    """
    is_fsd_enabled = f_utils.get_is_fsd_enabled()
    sdf = usdrt.Sdf if is_fsd_enabled else pxr.Sdf
    return _create_prim_generic(
        prim_type_name="CylinderLight",
        name=name,
        parent=parent,
        count=count,
        position=position,
        rotation=rotation,
        scale=scale,
        look_at=look_at,
        look_at_up_axis=look_at_up_axis,
        pivot=pivot,
        relative_to=relative_to,
        semantics=semantics,
        visible=visible,
        new_attributes=[
            ("inputs:radius", sdf.ValueTypeNames.Float, False),
            ("inputs:length", sdf.ValueTypeNames.Float, False),
            ("inputs:color", sdf.ValueTypeNames.Float3, False),
            ("inputs:shaping:focusTint", sdf.ValueTypeNames.Float3, False),
            ("treatAsPoint", sdf.ValueTypeNames.Bool, False),
            ("visibility", sdf.ValueTypeNames.Token, False),
            ("visibleInPrimaryRay", sdf.ValueTypeNames.Bool, True),
        ],
        inputs_col_radius=radius,
        inputs_col_length=length,
        inputs_col_color=color,
        inputs_col_diffuse=diffuse,
        inputs_col_specular=specular,
        inputs_col_colorTemperature=color_temperature,
        inputs_col_enableColorTemperature=enable_color_temperature,
        inputs_col_exposure=exposure,
        inputs_col_intensity=intensity,
        inputs_col_shaping_col_focusTint=shaping_focus_tint,
        inputs_col_shaping_col_cone_col_angle=shaping_cone_angle,
        inputs_col_shaping_col_cone_col_softness=shaping_cone_softness,
        schemas=["LightAPI", "ShapingAPI", "ShadowAPI"],
    )


def distant_light(
    position: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    scale: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    rotation: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    look_at: Union[
        str, pxr.Sdf.Path, usdrt.Sdf.Path, Tuple[float, float, float], List[Union[str, pxr.Sdf.Path, usdrt.Sdf.Path]]
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
    count: int = 1,
    name: Optional[str] = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
) -> List[pxr.Usd.Prim]:
    """Creates a distant light prim with configurable lighting properties.

    Args:
        position: XYZ coordinates in world space. Can be single value (applies to all axes),
                 tuple (applies to XYZ), or list of tuples (one per prim)
        scale: Scale factors for XYZ axes. Can be single value (applies to all axes),
               tuple (applies to XYZ), or list of tuples (one per prim)
        rotation: Euler angles in degrees (XYZ order). Can be single value (applies to all axes),
                 tuple (applies to XYZ), or list of tuples (one per prim)
        look_at: Target to point light at (prim path, coordinates, or list of targets)
        look_at_up_axis: Up axis vector for look_at orientation
        pivot: Pivot point specified as a tuple of (x, y, z) normalized to the range [-1, 1] where 0 is the center of the prim
        relative_to: Reference prim for relative positioning. If provided, position will be relative to this prim
        semantics: Dictionary specifying semantic type and values. Legacy lists of tuples are also accepted but will be converted to dictionaries.
        visible: Whether light should be visible
        color: RGB color of the light (0-1 range)
        intensity: Light intensity in lumens
        exposure: Light exposure value
        color_temperature: Color temperature in Kelvin
        enable_color_temperature: Whether to use color temperature
        diffuse: Diffuse contribution multiplier
        specular: Specular contribution multiplier
        shaping_cone_angle: Angle of the light cone in degrees
        shaping_cone_softness: Softness of the light cone
        shaping_focus_tint: RGB tint color for focused area
        angle: Angle of the light cone in degrees. For example, the sun has an angle of 0.53 degrees as seen from
            the earth. A higher angle results in softer shadow edges.
        count: Number of lights to create
        name: Name for the light prim
        parent: Parent prim path to create light under

    Returns:
        List[pxr.Usd.Prim]: List of created distant light prims

    Example:
        >>> import omni.replicator.core.functional as F
        >>> light = F.create_batch.distant_light(
        ...     position=(0, 2, 0),
        ...     color=(1, 0.8, 0.6),
        ...     intensity=50000,
        ...     angle=1.0
        ... )
    """
    is_fsd_enabled = f_utils.get_is_fsd_enabled()
    sdf = usdrt.Sdf if is_fsd_enabled else pxr.Sdf
    return _create_prim_generic(
        prim_type_name="DistantLight",
        name=name,
        parent=parent,
        count=count,
        position=position,
        rotation=rotation,
        scale=scale,
        look_at=look_at,
        look_at_up_axis=look_at_up_axis,
        pivot=pivot,
        relative_to=relative_to,
        semantics=semantics,
        visible=visible,
        new_attributes=[
            ("inputs:angle", sdf.ValueTypeNames.Float, False),
            ("inputs:color", sdf.ValueTypeNames.Float3, False),
            ("inputs:shaping:focusTint", sdf.ValueTypeNames.Float3, False),
            ("treatAsPoint", sdf.ValueTypeNames.Bool, False),
            ("visibility", sdf.ValueTypeNames.Token, False),
            ("visibleInPrimaryRay", sdf.ValueTypeNames.Bool, True),
        ],
        inputs_col_angle=angle,
        inputs_col_color=color,
        inputs_col_diffuse=diffuse,
        inputs_col_specular=specular,
        inputs_col_colorTemperature=color_temperature,
        inputs_col_enableColorTemperature=enable_color_temperature,
        inputs_col_exposure=exposure,
        inputs_col_intensity=intensity,
        inputs_col_shaping_col_focusTint=shaping_focus_tint,
        inputs_col_shaping_col_cone_col_angle=shaping_cone_angle,
        inputs_col_shaping_col_cone_col_softness=shaping_cone_softness,
        schemas=["LightAPI", "ShapingAPI", "ShadowAPI"],
    )


def dome_light(
    position: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    scale: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    rotation: Union[float, Tuple[float, float, float], List[Tuple[float, float, float]]] = None,
    look_at: Union[
        str, pxr.Sdf.Path, usdrt.Sdf.Path, Tuple[float, float, float], List[Union[str, pxr.Sdf.Path, usdrt.Sdf.Path]]
    ] = None,
    look_at_up_axis: Union[Tuple[float]] = None,
    color: Tuple[float] = (1.0, 1.0, 1.0),
    texture: str = None,
    texture_format: str = "latlong",
    intensity: float = 1000.0,
    exposure: float = 1.0,
    diffuse: float = 1.0,
    specular: float = 1.0,
    color_temperature: Union[float] = 6500,
    enable_color_temperature: bool = False,
    count: int = 1,
    name: Optional[str] = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
) -> List[pxr.Usd.Prim]:
    """Creates a dome light prim for environment/sky lighting.

    Args:
        position: XYZ coordinates in world space. Can be single value (applies to all axes),
                 tuple (applies to XYZ), or list of tuples (one per prim)
        scale: Scale factors for XYZ axes. Can be single value (applies to all axes),
               tuple (applies to XYZ), or list of tuples (one per prim)
        rotation: Euler angles in degrees (XYZ order). Can be single value (applies to all axes),
                 tuple (applies to XYZ), or list of tuples (one per prim)
        look_at: Target to point light at (prim path, coordinates, or list of targets)
        look_at_up_axis: Up axis vector for look_at orientation
        color: RGB color of the light (0-1 range)
        texture: Path to environment texture map
        texture_format: Format of the texture map ('latlong' or 'mirroredBall')
        intensity: Light intensity in lumens
        exposure: Exposure multiplier
        diffuse: Diffuse contribution multiplier
        specular: Specular contribution multiplier
        color_temperature: Color temperature in Kelvin
        enable_color_temperature: Whether to use color temperature
        count: Number of lights to create
        name: Name for the light prim
        parent: Parent prim path to create light under
        **kwargs: Additional light parameters to set

    Returns:
        List[pxr.Usd.Prim]: List of created dome light prims

    Example:
        >>> import omni.replicator.core.functional as F
        >>> light = F.create_batch.dome_light(
        ...     texture="/path/to/hdri.exr",
        ...     intensity=2000,
        ...     rotation=(0, 45, 0)
        ... )
    """
    is_fsd_enabled = f_utils.get_is_fsd_enabled()

    sdf = usdrt.Sdf if is_fsd_enabled else pxr.Sdf
    return _create_prim_generic(
        prim_type_name="DomeLight",
        name=name,
        parent=parent,
        count=count,
        position=position,
        rotation=rotation,
        scale=scale,
        look_at=look_at,
        look_at_up_axis=look_at_up_axis,
        inputs_col_color=color,
        inputs_col_texture_col_file=texture,
        inputs_col_texture_col_format=texture_format,
        inputs_col_intensity=intensity,
        inputs_col_exposure=exposure,
        inputs_col_diffuse=diffuse,
        inputs_col_specular=specular,
        inputs_col_colorTemperature=color_temperature,
        inputs_col_enableColorTemperature=enable_color_temperature,
        light_col_shaderId="DomeLight",
        guideRadius=100000.0,
        visibility="inherited",
        visibleInPrimaryRay=True,
        new_attributes=[
            ("inputs:color", sdf.ValueTypeNames.Float3, False),
            ("intensity", sdf.ValueTypeNames.Int, False),  # TODO
            ("inputs:texture:file", sdf.ValueTypeNames.Asset, False),
            ("inputs:texture:format", sdf.ValueTypeNames.Token, False),
            ("visibility", sdf.ValueTypeNames.Token, False),
            ("visibleInPrimaryRay", sdf.ValueTypeNames.Bool, True),
            ("light:shaderId", sdf.ValueTypeNames.Token, False),
            ("guideRadius", sdf.ValueTypeNames.Float, False),
        ],
        schemas=["LightAPI", "ShadowAPI"],
    )


def _material_pxr(
    mdl: str,
    bind_prims: Optional[list] = None,
    count: int = 1,
    name: Optional[str] = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    **kwargs,
):
    prims = []
    shaders = []
    parent = f_utils.get_batched_value(parent, count=count)
    stage = omni.usd.get_context().get_stage()
    for i in range(count):
        suffix = f"{i:02}" if i > 0 else ""
        path = _get_next_free_path(_get_path(f"{name}{suffix}", parent[i] if parent else None))
        utils.create_material(mtl_url=mdl, mtl_name="OmniPBR", mtl_path=path)
        prim = stage.GetPrimAtPath(path)
        shaders.append(pxr.UsdShade.Shader(omni.usd.get_shader_from_material(prim, True)))
        prims.append(prim)

    if bind_prims is None:
        bind_prims = [None] * count

    for attr_name, attr_value in kwargs.items():
        kwargs[attr_name] = f_utils.get_batched_value(attr_value, count=count)

    with pxr.Sdf.ChangeBlock():
        for i, (prim, shader, bind_prim) in enumerate(zip(prims, shaders, bind_prims)):
            # Populate material inputs
            f_utils.populate_material_inputs(prim)

            # Set material inputs
            for attr_name, attr_value in kwargs.items():
                attr = shader.GetInput(attr_name)
                if attr and attr_value is not None:
                    python_class = attr.GetAttr().GetTypeName().type.pythonClass  # Might be a better way to do this?
                    if python_class:
                        attr.Set(python_class(attr_value[i]))
                    else:
                        attr.Set(attr_value[i])
                else:
                    raise ValueError(f"Invalid attribute name: {attr_name}")

            if bind_prim is not None:
                if isinstance(bind_prim, usdrt.Usd.Prim):
                    bind_prim = stage.GetPrimAtPath(str(bind_prim.GetPrimPath()))
                elif isinstance(bind_prim, (str, pxr.Sdf.Path, usdrt.Sdf.Path)):
                    bind_prim = stage.GetPrimAtPath(str(bind_prim))
                elif isinstance(bind_prim, pxr.Usd.Prim):
                    pass
                else:
                    raise ValueError(f"Invalid bind prim: {bind_prim} of type {type(bind_prim)}")

                if not bind_prim.IsValid():
                    raise ValueError(f"Invalid bind prim: {bind_prim}")

                pxr.UsdShade.MaterialBindingAPI(bind_prim).Bind(
                    pxr.UsdShade.Material(prim), pxr.UsdShade.Tokens.strongerThanDescendants
                )
    return prims


def _material_usdrt(
    mdl: str,
    bind_prims: Optional[list] = None,
    count: int = 1,
    name: Optional[str] = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    **kwargs,
):
    """Creates material prims using USDRT API.

    Args:
        mdl: Path to MDL material file
        bind_prims: List of prims to bind material to
        count: Number of materials to create
        name: Name for the material prim
        parent: Parent prim path to create under
        **kwargs: Additional material parameters

    Returns:
        List[usdrt.Usd.Prim]: List of created material prims
    """
    prims = []
    for i in range(count):
        suffix = f"{i:02}" if i > 0 else ""
        path = _get_path(f"{name}{suffix}", parent)
        prim, shader_prim = _create_mdl_material_usdrt(mdl, path)
        shader = usdrt.UsdShade.Shader(shader_prim)

        f_utils.populate_material_inputs(prim)

        for attr_name, attr_value in kwargs.items():
            attr = shader.GetInput(attr_name)
            if attr:
                python_class = attr.GetAttr().GetTypeName().type.pythonClass  # Might be a better way to do this?
                if python_class:
                    attr.Set(python_class(attr_value[i]))
                else:
                    attr.Set(attr_value[i])
            else:
                raise ValueError(f"Invalid attribute name: {attr_name}")

        if bind_prims is not None:
            # Ensure bind_prims is a list, material can be bound to a single prim or a list of prims
            if not isinstance(bind_prims[i], list):
                bind_prims[i] = [bind_prims[i]]
            for bp in bind_prims[i]:
                usdrt.UsdShade.MaterialBindingAPI(bp).Bind(
                    usdrt.UsdShade.Material(prim), usdrt.UsdShade.Tokens.strongerThanDescendants
                )
        prims.append(prim)

    return prims


def material(
    mdl: str,
    bind_prims: Optional[list] = None,
    count: int = 1,
    name: Optional[str] = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    **kwargs,
):
    """Creates a material prim with MDL shader and binds it to target prims.

    Args:
        mdl: Path to MDL material file
        bind_prims: List of prims to bind material to
        count: Number of material prims to create
        name: Name for the material prim
        parent: Parent prim path to create material under
        **kwargs: Additional material parameters to set

    Returns:
        List[pxr.Usd.Prim]: List of created material prims

    Example:
        >>> import omni.replicator.core.functional as F
        >>> material = F.create_batch.material(
        ...     mdl="OmniPBR.mdl",
        ...     bind_prims=[sphere_prim],
        ...     diffuse_color=(1, 0, 0)
        ... )
    """
    if name is None:
        name = "Material"

    bind_prims = f_utils.get_batched_value(bind_prims, count=count)

    # Temporarily disabled, USDRT does not support retrieving material inputs
    # if f_utils.get_is_fsd_enabled():
    #     return _material_usdrt(mdl, bind_prims, count, name, parent, **kwargs)

    # Discard pose kwargs
    pose_kwargs = ("position", "rotation", "scale", "look_at", "look_at_up_axis", "pivot", "relative_to")
    for k in pose_kwargs:
        if k in kwargs:
            kwargs.pop(k)

    return _material_pxr(mdl, bind_prims, count, name, parent, **kwargs)


def omni_lidar(
    position: Union[float, Tuple[float]] = None,
    rotation: Union[float, Tuple[float]] = None,
    count: int = 1,
    name: Optional[str] = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    **kwargs,
) -> List[Union[pxr.Usd.Prim, usdrt.Usd.Prim]]:
    """Create a LiDAR sensor.

    Args:
        position: XYZ coordinates in world space. If a single value is provided, all axes will be set to that value.
        rotation: Euler angles in degrees in XYZ order. If a single value is provided, all axes will be set to that
            value.
        count: Number of LiDAR sensors to create
        name: Name for the LiDAR sensor
        parent: Parent prim path to create LiDAR under
        **kwargs: Additional attributes to be added to the LiDAR sensor

    Example:
        >>> import omni.replicator.core as rep
        >>> # Create LiDAR sensor
        >>> lidar = rep.functional.create_batch.omni_lidar(
        ...     position=(100, 100, 100),
        ...     rotation=(45, 45, 0),
        ... )
    """
    schemas = ["OmniSensorGenericLidarCoreAPI"]
    for key in kwargs:
        if key.startswith("omni:sensor:Core:emitterState:"):
            parts = key.split(":")
            instance_name = parts[4]
            new_schema_name = f"OmniSensorGenericLidarCoreEmitterStateAPI:{instance_name}"
            if new_schema_name not in schemas:
                schemas.append(new_schema_name)

    # Create the LiDAR sensor
    return _create_prim_generic(
        prim_type_name="OmniLidar",
        position=position,
        rotation=rotation,
        count=count,
        name=name,
        parent=parent,
        schemas=schemas,
        **kwargs,
    )


def omni_radar(
    position: Union[float, Tuple[float]] = None,
    rotation: Union[float, Tuple[float]] = None,
    count: int = 1,
    name: Optional[str] = None,
    parent: Union[str, pxr.Sdf.Path, pxr.Usd.Prim] = None,
    **kwargs,
) -> List[Union[pxr.Usd.Prim, usdrt.Usd.Prim]]:
    """Create a Radar sensor.

    Args:
        position: XYZ coordinates in world space. If a single value is provided, all axes will be set to that value.
        rotation: Euler angles in degrees in XYZ order. If a single value is provided, all axes will be set to that
            value.
        count: Number of Radar sensors to create
        name: Name for the Radar sensor
        parent: Parent prim path to create Radar under
        **kwargs: Additional attributes to be added to the Radar sensor

    Example:
        >>> import omni.replicator.core as rep
        >>> # Create Radar sensor
        >>> radar = rep.functional.create_batch.omni_radar(
        ...     position=(100, 100, 100),
        ...     rotation=(45, 45, 0),
        ... )
    """
    schemas = ["OmniSensorGenericRadarWpmDmatAPI"]
    for key in kwargs:
        if key.startswith("omni:sensor:WpmDmat:scan:"):
            parts = key.split(":")
            instance_name = parts[4]
            new_schema_name = f"OmniSensorGenericRadarWpmDmatScanCfgAPI:{instance_name}"
            if new_schema_name not in schemas:
                schemas.append(new_schema_name)

    # Create the Radar sensor
    return _create_prim_generic(
        prim_type_name="OmniRadar",
        position=position,
        rotation=rotation,
        count=count,
        name=name,
        parent=parent,
        schemas=schemas,
        **kwargs,
    )
