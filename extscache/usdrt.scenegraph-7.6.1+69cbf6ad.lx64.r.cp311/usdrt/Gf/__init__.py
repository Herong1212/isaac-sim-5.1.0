# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

import pxr as _pxr

from ._Gf import *


def convertToUsdrt(obj):
    """
    Convenience helper to convert from pxr.Gf to usdrt.Gf types.
    """
    # Vec2
    if isinstance(obj, _pxr.Gf.Vec2d):
        return _Gf.Vec2d(obj)
    if isinstance(obj, _pxr.Gf.Vec2f):
        return _Gf.Vec2f(obj)
    if isinstance(obj, _pxr.Gf.Vec2h):
        return _Gf.Vec2h(obj)
    if isinstance(obj, _pxr.Gf.Vec2i):
        return _Gf.Vec2i(obj)

    # Vec3
    elif isinstance(obj, _pxr.Gf.Vec3d):
        return _Gf.Vec3d(obj)
    elif isinstance(obj, _pxr.Gf.Vec3f):
        return _Gf.Vec3f(obj)
    elif isinstance(obj, _pxr.Gf.Vec3h):
        return _Gf.Vec3h(obj)
    elif isinstance(obj, _pxr.Gf.Vec3i):
        return _Gf.Vec3i(obj)

    # Vec4
    elif isinstance(obj, _pxr.Gf.Vec4d):
        return _Gf.Vec4d(obj)
    elif isinstance(obj, _pxr.Gf.Vec4f):
        return _Gf.Vec4f(obj)
    elif isinstance(obj, _pxr.Gf.Vec4h):
        return _Gf.Vec4h(obj)
    elif isinstance(obj, _pxr.Gf.Vec4i):
        return _Gf.Vec4i(obj)

    # Matrix
    elif isinstance(obj, _pxr.Gf.Matrix2d):
        return _Gf.Matrix2d(obj)
    elif isinstance(obj, _pxr.Gf.Matrix2f):
        return _Gf.Matrix2f(obj)
    elif isinstance(obj, _pxr.Gf.Matrix3d):
        return _Gf.Matrix3d(obj)
    elif isinstance(obj, _pxr.Gf.Matrix3f):
        return _Gf.Matrix3f(obj)
    elif isinstance(obj, _pxr.Gf.Matrix4d):
        return _Gf.Matrix4d(obj)
    elif isinstance(obj, _pxr.Gf.Matrix4f):
        return _Gf.Matrix4f(obj)

    # Range
    elif isinstance(obj, _pxr.Gf.Range1d):
        return _Gf.Range1d(convertToUsdrt(obj.min), convertToUsdrt(obj.max))
    elif isinstance(obj, _pxr.Gf.Range1f):
        return _Gf.Range1f(convertToUsdrt(obj.min), convertToUsdrt(obj.max))
    elif isinstance(obj, _pxr.Gf.Range2d):
        return _Gf.Range2d(convertToUsdrt(obj.min), convertToUsdrt(obj.max))
    elif isinstance(obj, _pxr.Gf.Range2f):
        return _Gf.Range2f(convertToUsdrt(obj.min), convertToUsdrt(obj.max))
    elif isinstance(obj, _pxr.Gf.Range3d):
        return _Gf.Range3d(convertToUsdrt(obj.min), convertToUsdrt(obj.max))
    elif isinstance(obj, _pxr.Gf.Range3f):
        return _Gf.Range3f(convertToUsdrt(obj.min), convertToUsdrt(obj.max))

    # Quat
    elif isinstance(obj, _pxr.Gf.Quatd):
        return _Gf.Quatd(convertToUsdrt(obj.real), convertToUsdrt(obj.imaginary))
    elif isinstance(obj, _pxr.Gf.Quatf):
        return _Gf.Quatf(convertToUsdrt(obj.real), convertToUsdrt(obj.imaginary))
    elif isinstance(obj, _pxr.Gf.Quath):
        return _Gf.Quath(convertToUsdrt(obj.real), convertToUsdrt(obj.imaginary))

    # Rect
    elif isinstance(obj, _pxr.Gf.Rect2i):
        return _Gf.Rect2i(convertToUsdrt(obj.min), convertToUsdrt(obj.max))

    # Rotation
    elif isinstance(obj, _pxr.Gf.Rotation):
        return _Gf.Rotation(convertToUsdrt(obj.axis), convertToUsdrt(obj.angle))

    # Transform
    elif isinstance(obj, _pxr.Gf.Transform):
        return _Gf.Transform(
            convertToUsdrt(obj.translation),
            convertToUsdrt(obj.rotation),
            convertToUsdrt(obj.scale),
            convertToUsdrt(obj.pivotPosition),
            convertToUsdrt(obj.pivotOrientation),
        )

    # Ray
    elif isinstance(obj, _pxr.Gf.Ray):
        return _Gf.Ray(convertToUsdrt(obj.startPoint), convertToUsdrt(obj.direction))

    # Frustum
    elif isinstance(obj, _pxr.Gf.Frustum):
        return _Gf.Frustum(
            convertToUsdrt(obj.position),
            convertToUsdrt(obj.rotation),
            convertToUsdrt(obj.window),
            convertToUsdrt(obj.nearFar),
            convertToUsdrt(obj.projectionType),
            convertToUsdrt(obj.viewDistance),
        )

    elif isinstance(obj, _pxr.Gf.Frustum.ProjectionType):
        if obj is _pxr.Gf.Frustum.Orthographic:
            return _Gf.Frustum.Orthographic
        else:
            return _Gf.Frustum.Perspective

    # BBox3d
    elif isinstance(obj, _pxr.Gf.BBox3d):
        return _Gf.BBox3d(convertToUsdrt(obj.box), convertToUsdrt(obj.matrix))

    # Line
    elif isinstance(obj, _pxr.Gf.Line):
        return _Gf.Line(convertToUsdrt(obj.GetPoint(0)), convertToUsdrt(obj.direction))

    # LineSeg
    elif isinstance(obj, _pxr.Gf.LineSeg):
        return _Gf.LineSeg(convertToUsdrt(obj.GetPoint(0)), convertToUsdrt(obj.GetPoint(1)))

    # Plane
    elif isinstance(obj, _pxr.Gf.Plane):
        return _Gf.Plane(convertToUsdrt(obj.normal), convertToUsdrt(obj.distanceFromOrigin))

    return obj


def convertToPxr(obj):
    """
    Convenience helper to convertToPxr from _pxr.Gf to pxr.Gf types.
    """
    # Vec2
    if isinstance(obj, _Gf.Vec2d):
        return _pxr.Gf.Vec2d(obj[0], obj[1])
    if isinstance(obj, _Gf.Vec2f):
        return _pxr.Gf.Vec2f(obj[0], obj[1])
    if isinstance(obj, _Gf.Vec2h):
        return _pxr.Gf.Vec2h(obj[0], obj[1])
    if isinstance(obj, _Gf.Vec2i):
        return _pxr.Gf.Vec2i(obj[0], obj[1])

    # Vec3
    elif isinstance(obj, _Gf.Vec3d):
        return _pxr.Gf.Vec3d(obj[0], obj[1], obj[2])
    elif isinstance(obj, _Gf.Vec3f):
        return _pxr.Gf.Vec3f(obj[0], obj[1], obj[2])
    elif isinstance(obj, _Gf.Vec3h):
        return _pxr.Gf.Vec3h(obj[0], obj[1], obj[2])
    elif isinstance(obj, _Gf.Vec3i):
        return _pxr.Gf.Vec3i(obj[0], obj[1], obj[2])

    # Vec4
    elif isinstance(obj, _Gf.Vec4d):
        return _pxr.Gf.Vec4d(obj[0], obj[1], obj[2], obj[3])
    elif isinstance(obj, _Gf.Vec4f):
        return _pxr.Gf.Vec4f(obj[0], obj[1], obj[2], obj[3])
    elif isinstance(obj, _Gf.Vec4h):
        return _pxr.Gf.Vec4h(obj[0], obj[1], obj[2], obj[3])
    elif isinstance(obj, _Gf.Vec4i):
        return _pxr.Gf.Vec4i(obj[0], obj[1], obj[2], obj[3])

    # Matrix
    elif isinstance(obj, _Gf.Matrix2d):
        return _pxr.Gf.Matrix2d(obj)
    elif isinstance(obj, _Gf.Matrix2f):
        return _pxr.Gf.Matrix2f(obj)
    elif isinstance(obj, _Gf.Matrix3d):
        return _pxr.Gf.Matrix3d(obj)
    elif isinstance(obj, _Gf.Matrix3f):
        return _pxr.Gf.Matrix3f(obj)
    elif isinstance(obj, _Gf.Matrix4d):
        return _pxr.Gf.Matrix4d(obj)
    elif isinstance(obj, _Gf.Matrix4f):
        return _pxr.Gf.Matrix4f(obj)

    # Range
    elif isinstance(obj, _Gf.Range1d):
        return _pxr.Gf.Range1d(convertToPxr(obj.min), convertToPxr(obj.max))
    elif isinstance(obj, _Gf.Range1f):
        return _pxr.Gf.Range1f(convertToPxr(obj.min), convertToPxr(obj.max))
    elif isinstance(obj, _Gf.Range2d):
        return _pxr.Gf.Range2d(convertToPxr(obj.min), convertToPxr(obj.max))
    elif isinstance(obj, _Gf.Range2f):
        return _pxr.Gf.Range2f(convertToPxr(obj.min), convertToPxr(obj.max))
    elif isinstance(obj, _Gf.Range3d):
        return _pxr.Gf.Range3d(convertToPxr(obj.min), convertToPxr(obj.max))
    elif isinstance(obj, _Gf.Range3f):
        return _pxr.Gf.Range3f(convertToPxr(obj.min), convertToPxr(obj.max))

    # Quat
    elif isinstance(obj, _Gf.Quatd):
        return _pxr.Gf.Quatd(convertToPxr(obj.real), convertToPxr(obj.imaginary))
    elif isinstance(obj, _Gf.Quatf):
        return _pxr.Gf.Quatf(convertToPxr(obj.real), convertToPxr(obj.imaginary))
    elif isinstance(obj, _Gf.Quath):
        return _pxr.Gf.Quath(convertToPxr(obj.real), convertToPxr(obj.imaginary))

    # Rect
    elif isinstance(obj, _Gf.Rect2i):
        return _pxr.Gf.Rect2i(convertToPxr(obj.min), convertToPxr(obj.max))

    # Rotation
    elif isinstance(obj, _Gf.Rotation):
        return _pxr.Gf.Rotation(convertToPxr(obj.axis), convertToPxr(obj.angle))

    # Transform
    elif isinstance(obj, _Gf.Transform):
        return _pxr.Gf.Transform(
            convertToPxr(obj.translation),
            convertToPxr(obj.rotation),
            convertToPxr(obj.scale),
            convertToPxr(obj.pivotPosition),
            convertToPxr(obj.pivotOrientation),
        )

    # Ray
    elif isinstance(obj, _Gf.Ray):
        return _pxr.Gf.Ray(convertToPxr(obj.startPoint), convertToPxr(obj.direction))

    # Frustum
    elif isinstance(obj, _Gf.Frustum):
        return _pxr.Gf.Frustum(
            convertToPxr(obj.position),
            convertToPxr(obj.rotation),
            convertToPxr(obj.window),
            convertToPxr(obj.nearFar),
            convertToPxr(obj.projectionType),
            convertToPxr(obj.viewDistance),
        )

    elif isinstance(obj, _Gf.Frustum.ProjectionType):
        if obj is _Gf.Frustum.Orthographic:
            return _pxr.Gf.Frustum.Orthographic
        else:
            return _pxr.Gf.Frustum.Perspective

    # BBox3d
    elif isinstance(obj, _Gf.BBox3d):
        return _pxr.Gf.BBox3d(convertToPxr(obj.box), convertToPxr(obj.matrix))

    # Line
    elif isinstance(obj, _Gf.Line):
        return _pxr.Gf.Line(convertToPxr(obj.GetPoint(0)), convertToPxr(obj.direction))

    # LineSeg
    elif isinstance(obj, _Gf.LineSeg):
        return _pxr.Gf.LineSeg(convertToPxr(obj.GetPoint(0)), convertToPxr(obj.GetPoint(1)))

    # Plane
    elif isinstance(obj, _Gf.Plane):
        return _pxr.Gf.Plane(convertToPxr(obj.normal), convertToPxr(obj.distanceFromOrigin))

    return obj
