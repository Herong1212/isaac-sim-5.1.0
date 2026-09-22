# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""This module provides utilities for manipulating and transforming primitives in 3D space, including functions to flatten matrices, compose transformation matrices from translation, rotation, and scale, generate compatible euler angles, find the best euler angles for a given transformation, and construct transformation matrices from separate components."""


import math
from typing import List

import carb
import carb.profiler
import carb.settings
import usdrt.Gf
from pxr import Gf, Usd, UsdGeom


@carb.profiler.profile
def flatten(transform):
    """Convert array[4][4] to array[16]"""

    # flatten the matrix by hand
    # USING LIST COMPREHENSION IS VERY SLOW (e.g. return [item for sublist in transform for item in sublist]), which takes around 10ms.
    m0, m1, m2, m3 = transform[0], transform[1], transform[2], transform[3]
    return [
        m0[0],
        m0[1],
        m0[2],
        m0[3],
        m1[0],
        m1[1],
        m1[2],
        m1[3],
        m2[0],
        m2[1],
        m2[2],
        m2[3],
        m3[0],
        m3[1],
        m3[2],
        m3[3],
    ]


# @carb.profiler.profile
# def get_local_transform_pivot_inv(prim: Usd.Prim, time: Usd.TimeCode = Usd.TimeCode):
#     xform = UsdGeom.Xformable(prim)
#     xform_ops = xform.GetOrderedXformOps()
#     if len(xform_ops):
#         pivot_op_inv = xform_ops[-1]
#         if (
#             pivot_op_inv.GetOpType() == UsdGeom.XformOp.TypeTranslate
#             and pivot_op_inv.IsInverseOp()
#             and pivot_op_inv.GetName().endswith("pivot")
#         ):
#             return pivot_op_inv.GetOpTransform(time)
#     return Gf.Matrix4d(1.0)


def compose_transform_ops_to_matrix(
    translation: usdrt.Gf.Vec3d | usdrt.Gf.Vec3f | usdrt.Gf.Vec3h,
    rotation: usdrt.Gf.Vec3d | usdrt.Gf.Vec3f | usdrt.Gf.Vec3h,
    rotation_order: usdrt.Gf.Vec3i,
    scale: usdrt.Gf.Vec3d | usdrt.Gf.Vec3f | usdrt.Gf.Vec3h,
) -> usdrt.Gf.Matrix4d:
    """Composes a transformation matrix from translation, rotation, rotation order, and scale vectors.

    Args:
        translation (Union[:obj:`usdrt.Gf.Vec3d`, :obj:`usdrt.Gf.Vec3f`, :obj:`usdrt.Gf.Vec3h`]): The translation vector specifying the translation part of the transform.
        rotation (Union[:obj:`usdrt.Gf.Vec3d`, :obj:`usdrt.Gf.Vec3f`, :obj:`usdrt.Gf.Vec3h`]): The rotation vector specifying the rotation part of the transform in degrees.
        rotation_order (:obj:`usdrt.Gf.Vec3i`): The order of axes for the rotation specified as integers. Each element corresponds to an axis (0 for x, 1 for y, 2 for z).
        scale (Union[:obj:`usdrt.Gf.Vec3d`, :obj:`usdrt.Gf.Vec3f`, :obj:`usdrt.Gf.Vec3h`]): The scale vector specifying the scale part of the transform.

    Returns:
        :obj:`usdrt.Gf.Matrix4d`: The composed transformation matrix as a 4x4 matrix."""
    axes = [usdrt.Gf.Vec3d.XAxis(), usdrt.Gf.Vec3d.YAxis(), usdrt.Gf.Vec3d.ZAxis()]
    rot = []
    for i in range(3):
        axis_idx = rotation_order[i]
        rot.append(usdrt.Gf.Rotation(axes[axis_idx], rotation[axis_idx]))
    rotation_mtx = usdrt.Gf.Matrix4d(1.0)
    rotation_mtx.SetRotate(rot[0] * rot[1] * rot[2])
    valid_scale = usdrt.Gf.Vec3d(0.0)
    for i in range(3):
        if abs(scale[i]) == 0:
            valid_scale[i] = 0.001
        else:
            valid_scale[i] = scale[i]
    scale_mtx = usdrt.Gf.Matrix4d(1.0)
    scale_mtx.SetScale(valid_scale)
    translate_mtx = usdrt.Gf.Matrix4d(1.0)
    translate_mtx.SetTranslate(usdrt.Gf.Vec3d(translation[0], translation[1], translation[2]))
    return scale_mtx * rotation_mtx * translate_mtx


def generate_compatible_euler_angles(euler: usdrt.Gf.Vec3d, rotation_order: usdrt.Gf.Vec3i) -> List[usdrt.Gf.Vec3d]:
    """Generates a list of euler angles that are compatible with the provided euler angles and rotation order.

    Args:
        euler (:obj:`usdrt.Gf.Vec3d`): The original euler angles to find compatible angles for.
        rotation_order (:obj:`usdrt.Gf.Vec3i`): The order of rotation axes.

    Returns:
        List[:obj:`usdrt.Gf.Vec3d`]: A list of euler angles compatible with the given euler angles and rotation order.
    """
    equal_eulers = [euler]
    mid_order = rotation_order[1]
    equal = usdrt.Gf.Vec3d()
    for i in range(3):
        if i == mid_order:
            equal[i] = 180 - euler[i]
        else:
            equal[i] = euler[i] + 180
    equal_eulers.append(equal)
    for i in range(3):
        equal[i] -= 360
    equal_eulers.append(equal)
    return equal_eulers


def find_best_euler_angles(
    old_rot_vec: usdrt.Gf.Vec3d, new_rot_vec: usdrt.Gf.Vec3d, rotation_order: usdrt.Gf.Vec3i
) -> usdrt.Gf.Vec3d:
    """Finds the closest euler angles to the old rotation vector that correspond to the new rotation vector.

    Args:
        old_rot_vec (:obj:`usdrt.Gf.Vec3d`): The original rotation vector that the new euler angles should be close to.
        new_rot_vec (:obj:`usdrt.Gf.Vec3d`): The target rotation vector to find the closest euler angles for.
        rotation_order (:obj:`usdrt.Gf.Vec3i`): The order of rotations to be considered when generating euler angles.

    Returns:
        :obj:`usdrt.Gf.Vec3d`: The euler angles that are closest to the original rotation vector."""
    equal_eulers = generate_compatible_euler_angles(new_rot_vec, rotation_order)
    nearest_euler = None
    for euler in equal_eulers:
        for i in range(3):
            euler[i] = repeat(euler[i] - old_rot_vec[i] + 180.0, 360.0) + old_rot_vec[i] - 180.0
        if nearest_euler is None:
            nearest_euler = euler
        else:
            distance_1 = (nearest_euler - old_rot_vec).GetLength()
            distance_2 = (euler - old_rot_vec).GetLength()

            if distance_2 < distance_1:
                nearest_euler = euler
    return nearest_euler


def repeat(t: float, length: float) -> float:
    """Args:
        t (float): The value to be repeated within the range.
        length (float): The range length within which the value 't' is to be repeated.

    Returns:
        float: The repeated value of 't' within the range of 'length'."""
    return t - (math.floor(t / length) * length)


def construct_transform_matrix_from_SRT(
    t: usdrt.Gf.Vec3d,
    rot_euler: usdrt.Gf.Vec3d,
    rot_order: usdrt.Gf.Vec3i,
    scale: usdrt.Gf.Vec3d,
    pivot_inv: usdrt.Gf.Matrix4d,
) -> usdrt.Gf.Matrix4d:
    """Constructs a transformation matrix from separate components of scale, rotation, and translation.

    Args:
        t (usdrt.Gf.Vec3d): The translation vector.
        rot_euler (usdrt.Gf.Vec3d): The rotation vector in Euler angles.
        rot_order (usdrt.Gf.Vec3i): The order of rotations to apply.
        scale (usdrt.Gf.Vec3d): The scaling vector.
        pivot_inv (usdrt.Gf.Matrix4d): The inverse of the pivot matrix.

    Returns:
        usdrt.Gf.Matrix4d: The constructed transform matrix as a 4x4 matrix."""
    trans_mtx = usdrt.Gf.Matrix4d()
    rot_mtx = usdrt.Gf.Matrix4d()
    scale_mtx = usdrt.Gf.Matrix4d()
    trans_mtx.SetTranslate(usdrt.Gf.Vec3d(t))
    axes = [usdrt.Gf.Vec3d.XAxis(), usdrt.Gf.Vec3d.YAxis(), usdrt.Gf.Vec3d.ZAxis()]
    rotation = (
        usdrt.Gf.Rotation(axes[rot_order[0]], rot_euler[rot_order[0]])
        * usdrt.Gf.Rotation(axes[rot_order[1]], rot_euler[rot_order[1]])
        * usdrt.Gf.Rotation(axes[rot_order[2]], rot_euler[rot_order[2]])
    )
    rot_mtx.SetRotate(rotation)
    scale_mtx.SetScale(usdrt.Gf.Vec3d(scale))
    return pivot_inv * scale_mtx * rot_mtx * pivot_inv.GetInverse() * trans_mtx
