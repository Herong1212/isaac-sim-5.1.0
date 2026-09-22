# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""An utility module which provides APIs to interact with Fabric stage and prim for fabric commands."""

import carb
import re
from typing import Union
import usdrt.Usd
import usdrt.Sdf
import usdrt.Rt
import usdrt.Vt
import usdrt.Gf

from pxr import Sdf, Gf


def get_stage_next_free_path(stage: usdrt.Usd.Stage, path: Union[str, usdrt.Sdf.Path], prepend_default_prim: bool):
    """Generates a unique path for a new prim on the given stage by incrementing a numerical suffix until a free path is found.

    Args:
        stage (usdrt.Usd.Stage): The Fabric stage where the new prim path will be created.
        path (Union[str, usdrt.Sdf.Path]): The initial path for the new prim. If it's a string, it should be a valid Fabric path.
        prepend_default_prim (bool): If True, the default prim's path will be prepended to the generated path if the provided path is not already under the default prim.

    Returns:
        str: A unique string path that does not correspond to an existing prim on the stage.

    Raises:
        ValueError: If the provided path is not a valid Fabric path string."""
    if isinstance(path, usdrt.Sdf.Path):
        path = path.pathString

    if isinstance(path, str) and not Sdf.Path.IsValidPathString(path):
        raise ValueError(f"{path} is not a valid path")

    # TODO: remove pxr Sdf dependency here when OM-101632 is ready
    path = Sdf.Path(path)
    # If path is missing leading slash, it's still ValidPathString but may crash in other USD api. Correct it here and issue a warning.
    corrected_path = path.MakeAbsolutePath(Sdf.Path.absoluteRootPath)
    if path != corrected_path:
        carb.log_warn(f"Path {path} is auto-corrected to {corrected_path}. Please verify your path format.")
        path = corrected_path

    path = usdrt.Sdf.Path(path.pathString)
    if prepend_default_prim and stage.GetDefaultPrim().IsValid():
        defaultPrim = stage.GetDefaultPrim()
        if defaultPrim and not (path.HasPrefix(defaultPrim.GetPath()) and path != defaultPrim.GetPath()):
            path = path.ReplacePrefix(usdrt.Sdf.Path.absoluteRootPath, defaultPrim.GetPath())

    def increment_path(path):
        """Increments the numerical suffix of a given Fabric path until a unique path is found that does not exist on the stage.

        Args:
            path (str): The initial Fabric path to be incremented.

        Returns:
            str: A unique Fabric path with an incremented numerical suffix."""
        match = re.search(r"_(\d+)$", path)
        if match:
            new_num = int(match.group(1)) + 1
            ret = re.sub(r"_(\d+)$", str.format("_{:02d}", new_num), path)
        else:
            ret = path + "_01"
        return ret

    path_string = path.GetString()
    while stage.GetPrimAtPath(path_string):
        path_string = increment_path(path_string)

    return path_string


def is_ancestor_prim_type(stage: usdrt.Usd.Stage, prim_path: usdrt.Sdf.Path, prim_type: usdrt.Usd.SchemaBase):
    """Checks if any ancestor prims of the given prim at the provided path are of the specified prim type.

    Args:
        stage (usdrt.Usd.Stage): The stage in which to search for ancestor prims.
        prim_path (usdrt.Sdf.Path): The path to the starting prim to check its ancestors.
        prim_type (usdrt.Usd.SchemaBase): The type of the prim to check for among the ancestors.

    Returns:
        bool: True if any ancestor prims are of the specified prim type, False otherwise."""
    # are any parent prims in prim_path type prim_type?
    parent_path = prim_path.GetParentPath()
    while parent_path and parent_path != usdrt.Sdf.Path.absoluteRootPath:
        parent_prim = stage.GetPrimAtPath(parent_path)
        if parent_prim and parent_prim.IsA(prim_type):
            return True

        parent_path = parent_path.GetParentPath()

    return False


def can_prim_have_children(stage: usdrt.Usd.Stage, new_path: usdrt.Sdf.Path, prim: usdrt.Usd.Prim):
    """Determines if a given Fabric prim can have children based on its type and the types of its ancestors.

    Args:
        stage (usdrt.Usd.Stage): The stage containing the Fabric prims to evaluate.
        new_path (usdrt.Sdf.Path): The path to the prim being evaluated.
        prim (usdrt.Usd.Prim): The prim to evaluate.

    Returns:
        bool: False if the prim is of type usdrt.UsdGeom.Gprim and any of its ancestors are also of type usdrt.UsdGeom.Gprim, True otherwise.
    """
    # if prim is usdrt.UsdGeom.Gprim and any parent prims are also usdrt.UsdGeom.Gprim then return False
    if isinstance(prim, usdrt.Usd.Prim):
        is_gprim = prim.IsA(usdrt.UsdGeom.Gprim)
    else:
        schema_registy = usdrt.Usd.SchemaRegistry.GetInstance()
        is_gprim = schema_registy.IsA(prim, usdrt.UsdGeom.Gprim)

    if is_gprim and is_ancestor_prim_type(stage, new_path, usdrt.UsdGeom.Gprim):
        return False

    return True


def compute_visibility(prim):
    """Computes the visibility state of a given Fabric prim.

    This function checks the visibility attribute of the given prim and its ancestors
    in the USD scene hierarchy. If any ancestor's visibility is set to invisible,
    the function will return 'invisible'. Otherwise, it will return 'inherited'.

    Args:
        prim (usdrt.Usd.Prim): The prim to compute visibility for.

    Returns:
        str: The visibility state of the prim, either 'invisible' or 'inherited'."""
    imageable = usdrt.UsdGeom.Imageable(prim)
    if imageable:
        visibility_attr = imageable.GetVisibilityAttr()
        if visibility_attr.IsValid():
            if visibility_attr.Get() == usdrt.UsdGeom.Tokens.invisible:
                return usdrt.UsdGeom.Tokens.invisible

    parent = prim.GetParent()
    if parent:
        # Check parent visibility
        return compute_visibility(prim.GetParent())

    return usdrt.UsdGeom.Tokens.inherited


def has_prefix(path: usdrt.Sdf.Path, prefix: usdrt.Sdf.Path):
    """Checks if the given Fabric path has the specified prefix.

    Args:
        path (usdrt.Sdf.Path): The Fabric path to check for the prefix.
        prefix (usdrt.Sdf.Path): The prefix path to check against the given path.

    Returns:
        bool: True if the path has the specified prefix, False otherwise."""
    path_prefixes = path.GetPrefixes()
    if prefix in path_prefixes or prefix == usdrt.Sdf.Path("/"):
        return True

    return False


def remove_descendent_paths(paths: list[usdrt.Sdf.Path]):
    """Removes descendant paths from a sorted list of Fabric paths, effectively deduplicating the list by retaining only the highest ancestor paths.

    Args:
        paths (list[usdrt.Sdf.Path]): A list of Fabric paths to filter.

    Returns:
        list[usdrt.Sdf.Path]: A list containing the original paths without any descendants."""
    # sort paths first
    paths.sort()

    unique_paths = []
    if paths:
        unique_paths = [paths[0]]
        path_to_compare = paths[0]
        for path in paths[1:]:
            # TODO: replace with usdrt.Sdf.Path.HasPrefix when OM-101039 is fixed
            if not has_prefix(path, path_to_compare):
                unique_paths.append(path)
                path_to_compare = path

    return unique_paths


def get_rotation_from_order(order: str, angles: list[float]):
    """Composes a rotation based on a given order and corresponding angles.

    Args:
        order (str): A string specifying the order of axes (e.g., 'XYZ') for which to apply the rotations.
        angles (list[float]): A list of three float values specifying the rotation in degrees around the X, Y, and Z axes, respectively.

    Returns:
        usdrt.Gf.Rotation: The final rotation composed of the specified order and angles."""
    # Compose rotation from rotation orders
    # args: order: e.g. XYZ, angles are degrees, angle is always in XYZ order e.g [10,30,40]
    final_rotation = None
    for i in range(len(order)):
        axis_name = order[i]
        match axis_name:
            case "X":
                axis = usdrt.Gf.Vec3d.XAxis()
                angle = angles[0]
            case "Y":
                axis = usdrt.Gf.Vec3d.YAxis()
                angle = angles[1]
            case "Z":
                axis = usdrt.Gf.Vec3d.ZAxis()
                angle = angles[2]
            case _:
                continue

        rotation = usdrt.Gf.Rotation(axis, angle)
        if final_rotation is None:
            final_rotation = rotation
        else:
            final_rotation *= rotation

    return final_rotation


def get_local_transform_matrix_from_xform_attrs(
    prim: usdrt.Usd.Prim, time_code: usdrt.Usd.TimeCode = usdrt.Usd.TimeCode.Default()
) -> usdrt.Gf.Matrix4d:
    """Computes the local transformation matrix for a given Fabric prim at a specific time.

    This function extracts the transformation attributes (translate, scale, rotate, and transform) based on the xform op order
    and composes them into a single transformation matrix that represents the local transformation of the prim.

    Args:
        prim (usdrt.Usd.Prim): The Fabric prim to compute the local transform for.
        time_code (usdrt.Usd.TimeCode, optional): The time at which to compute the transformation. Defaults to usdrt.Usd.TimeCode.Default().

    Returns:
        usdrt.Gf.Matrix4d: The computed local transformation matrix representing the prim's transform at the specified time.
    """
    # get local transform from xform attributes
    xformable = usdrt.UsdGeom.Xformable(prim)
    xform_op_order_attr = xformable.GetXformOpOrderAttr()

    xform_mtx = usdrt.Gf.Matrix4d()

    if xform_op_order_attr:
        xform_op_order = xform_op_order_attr.Get()
        xform_iter = iter(reversed(range(len(xform_op_order))))
        # iterate in reverse order!
        for op_order_index in xform_iter:
            op_order_name = xform_op_order[op_order_index]

            # Skip the current xformOp and the next one if they're inverses of each other.
            if op_order_index - 1 >= 0:
                next_op_order_name = xform_op_order[op_order_index - 1]
                if "!invert!" + op_order_name == next_op_order_name or "!invert!" + next_op_order_name == op_order_name:
                    next(xform_iter)
                    continue

            if op_order_name.startswith("!resetXformStack!"):
                break

            op_name_extracted = ":".join(op_order_name.split(":")[1:])
            # op_order_name may not be the attribute name
            op_attr_name = "xformOp:" + op_name_extracted
            xform_op_attr = prim.GetAttribute(op_attr_name)
            if not xform_op_attr:
                continue

            xform_op_attr_value = xform_op_attr.Get(time_code)

            def check_value_type(value):
                """Ensures that the provided value has the expected type, converting it if necessary.

                Args:
                    value: The value to check and possibly convert.

                Returns:
                    The value converted to the expected type if it was not already of that type; otherwise, the original value.
                """
                if not isinstance(value, usdrt.Gf.Vec3d):
                    return usdrt.Gf.Vec3d(value)
                return value

            op_mtx = usdrt.Gf.Matrix4d()

            if "translate" in op_name_extracted:
                op_mtx.SetTranslate(check_value_type(xform_op_attr_value))

            elif "scale" in op_name_extracted:
                op_mtx.SetScale(check_value_type(xform_op_attr_value))

            elif "rotate" in op_name_extracted:
                op_name = op_name_extracted.split(":")[0]
                rotation_order = op_name.split("rotate")[-1]
                rotation = get_rotation_from_order(rotation_order, check_value_type(xform_op_attr_value))
                op_mtx.SetRotate(rotation)

            elif "transform" in op_name_extracted:
                if not isinstance(xform_op_attr_value, usdrt.Gf.Matrix4d):
                    xform_op_attr_value = convert_matrix4_type(xform_op_attr_value, usdrt.Gf.Matrix4d)
                op_mtx = xform_op_attr_value

            elif "orient" in op_name_extracted:
                if not isinstance(xform_op_attr_value, usdrt.Gf.Quatd):
                    real_part = xform_op_attr_value.GetReal()
                    imaginary_part = xform_op_attr_value.GetImaginary()
                    xform_op_attr_value = usdrt.Gf.Quatd(real_part, imaginary_part)
                op_mtx.SetRotate(xform_op_attr_value)

            else:
                continue

            if op_order_name.startswith("!invert!"):
                # invert matrix
                op_mtx = op_mtx.GetInverse()

            if op_mtx != usdrt.Gf.Matrix4d():
                xform_mtx *= op_mtx

    return xform_mtx


def convert_matrix4_type(matrix, to_matrix_type: Union[usdrt.Gf.Matrix4d, Gf.Matrix4d]):
    """Converts a matrix to the specified matrix type.

    Args:
        matrix: The matrix to convert.
        to_matrix_type (Union[usdrt.Gf.Matrix4d, Gf.Matrix4d]): The type of matrix to convert to, either usdrt.Gf.Matrix4d or Gf.Matrix4d.

    Returns:
        The converted matrix as the specified matrix type."""
    # convert between pxr matrix and usdrt matrix
    return to_matrix_type(
        matrix[0][0],
        matrix[0][1],
        matrix[0][2],
        matrix[0][3],
        matrix[1][0],
        matrix[1][1],
        matrix[1][2],
        matrix[1][3],
        matrix[2][0],
        matrix[2][1],
        matrix[2][2],
        matrix[2][3],
        matrix[3][0],
        matrix[3][1],
        matrix[3][2],
        matrix[3][3],
    )


def compute_extent_from_points(prim: usdrt.Usd.Prim, time_code: usdrt.Usd.TimeCode = usdrt.Usd.TimeCode.Default()):
    """Computes the axis-aligned bounding box (extent) of a given Fabric prim based on its 'points' attribute at a specific time.

    Args:
        prim (usdrt.Usd.Prim): The Fabric prim to compute the extent for.
        time_code (usdrt.Usd.TimeCode, optional): The time at which to evaluate the 'points' attribute. Defaults to usdrt.Usd.TimeCode.Default().

    Returns:
        usdrt.Gf.Range3d: The computed bounding box range representing the extent of the prim."""
    points_attr = prim.GetAttribute("points")

    bbox_range = usdrt.Gf.Range3d()
    if points_attr:
        for point in points_attr.Get():
            bbox_range.UnionWith(usdrt.Gf.Vec3d(point))

    return bbox_range
