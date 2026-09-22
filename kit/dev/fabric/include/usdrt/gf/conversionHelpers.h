// Copyright (c) 2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <pxr/base/gf/matrix2d.h>
#include <pxr/base/gf/matrix2f.h>
#include <pxr/base/gf/matrix3d.h>
#include <pxr/base/gf/matrix3f.h>
#include <pxr/base/gf/matrix4d.h>
#include <pxr/base/gf/matrix4f.h>
#include <pxr/base/gf/vec2d.h>
#include <pxr/base/gf/vec2f.h>
#include <pxr/base/gf/vec2h.h>
#include <pxr/base/gf/vec2i.h>
#include <pxr/base/gf/range1d.h>
#include <pxr/base/gf/range1f.h>
#include <pxr/base/gf/range2d.h>
#include <pxr/base/gf/range2f.h>
#include <pxr/base/gf/range3d.h>
#include <pxr/base/gf/range3f.h>
#include <pxr/base/gf/rect2i.h>
#include <pxr/base/gf/rotation.h>
#include <pxr/base/gf/transform.h>
#include <pxr/base/gf/ray.h>
#include <pxr/base/gf/frustum.h>
#include <pxr/base/gf/line.h>
#include <pxr/base/gf/lineSeg.h>
#include <pxr/base/gf/plane.h>

#include <usdrt/gf/matrix.h>
#include <usdrt/gf/range.h>
#include <usdrt/gf/vec.h>
#include <usdrt/gf/rect.h>
#include <usdrt/gf/rotation.h>
#include <usdrt/gf/transform.h>
#include <usdrt/gf/ray.h>
#include <usdrt/gf/frustum.h>
#include <usdrt/gf/line.h>
#include <usdrt/gf/lineSeg.h>
#include <usdrt/gf/plane.h>

namespace usdrt
{
//-----------------------------------------------------------------------------
// convert to usdrt
//-----------------------------------------------------------------------------

template <typename R, typename P>
inline const R& toUsdrt(const P& pxrObj)
{
    return reinterpret_cast<const R&>(pxrObj);
}

// GfHalf
inline GfHalf toUsdrt(pxr::GfHalf v)
{
    return toUsdrt<GfHalf, pxr::GfHalf>(v);
}

// Vec2
inline GfVec2d toUsdrt(pxr::GfVec2d v)
{
    return toUsdrt<GfVec2d, pxr::GfVec2d>(v);
}
inline GfVec2f toUsdrt(pxr::GfVec2f v)
{
    return toUsdrt<GfVec2f, pxr::GfVec2f>(v);
}
inline GfVec2h toUsdrt(pxr::GfVec2h v)
{
    return toUsdrt<GfVec2h, pxr::GfVec2h>(v);
}
inline GfVec2i toUsdrt(pxr::GfVec2i v)
{
    return toUsdrt<GfVec2i, pxr::GfVec2i>(v);
}

// Vec3
inline GfVec3d toUsdrt(pxr::GfVec3d v)
{
    return toUsdrt<GfVec3d, pxr::GfVec3d>(v);
}
inline GfVec3f toUsdrt(pxr::GfVec3f v)
{
    return toUsdrt<GfVec3f, pxr::GfVec3f>(v);
}
inline GfVec3h toUsdrt(pxr::GfVec3h v)
{
    return toUsdrt<GfVec3h, pxr::GfVec3h>(v);
}
inline GfVec3i toUsdrt(pxr::GfVec3i v)
{
    return toUsdrt<GfVec3i, pxr::GfVec3i>(v);
}

// Vec4
inline GfVec4d toUsdrt(pxr::GfVec4d v)
{
    return toUsdrt<GfVec4d, pxr::GfVec4d>(v);
}
inline GfVec4f toUsdrt(pxr::GfVec4f v)
{
    return toUsdrt<GfVec4f, pxr::GfVec4f>(v);
}
inline GfVec4h toUsdrt(pxr::GfVec4h v)
{
    return toUsdrt<GfVec4h, pxr::GfVec4h>(v);
}
inline GfVec4i toUsdrt(pxr::GfVec4i v)
{
    return toUsdrt<GfVec4i, pxr::GfVec4i>(v);
}

// Matrix
inline GfMatrix2d toUsdrt(pxr::GfMatrix2d v)
{
    return toUsdrt<GfMatrix2d, pxr::GfMatrix2d>(v);
}
inline GfMatrix2f toUsdrt(pxr::GfMatrix2f v)
{
    return toUsdrt<GfMatrix2f, pxr::GfMatrix2f>(v);
}
inline GfMatrix3d toUsdrt(pxr::GfMatrix3d v)
{
    return toUsdrt<GfMatrix3d, pxr::GfMatrix3d>(v);
}
inline GfMatrix3f toUsdrt(pxr::GfMatrix3f v)
{
    return toUsdrt<GfMatrix3f, pxr::GfMatrix3f>(v);
}
inline GfMatrix4d toUsdrt(pxr::GfMatrix4d v)
{
    return toUsdrt<GfMatrix4d, pxr::GfMatrix4d>(v);
}
inline GfMatrix4f toUsdrt(pxr::GfMatrix4f v)
{
    return toUsdrt<GfMatrix4f, pxr::GfMatrix4f>(v);
}

// Range
inline GfRange1d toUsdrt(pxr::GfRange1d v)
{
    return GfRange1d(v.GetMin(), v.GetMax());
}

inline GfRange1f toUsdrt(pxr::GfRange1f v)
{
    return GfRange1f(v.GetMin(), v.GetMax());
}

inline GfRange2d toUsdrt(pxr::GfRange2d v)
{
    return GfRange2d(toUsdrt(v.GetMin()), toUsdrt(v.GetMax()));
}
inline GfRange2f toUsdrt(pxr::GfRange2f v)
{
    return GfRange2f(toUsdrt(v.GetMin()), toUsdrt(v.GetMax()));
}
inline GfRange3d toUsdrt(pxr::GfRange3d v)
{
    return GfRange3d(toUsdrt(v.GetMin()), toUsdrt(v.GetMax()));
}
inline GfRange3f toUsdrt(pxr::GfRange3f v)
{
    return GfRange3f(toUsdrt(v.GetMin()), toUsdrt(v.GetMax()));
}

// Quat
inline GfQuatd toUsdrt(pxr::GfQuatd v)
{
    return GfQuatd(v.GetReal(), toUsdrt(v.GetImaginary()));
}
inline GfQuatf toUsdrt(pxr::GfQuatf v)
{
    return GfQuatf(v.GetReal(), toUsdrt(v.GetImaginary()));
}
inline GfQuath toUsdrt(pxr::GfQuath v)
{
    return GfQuath(toUsdrt(v.GetReal()), toUsdrt(v.GetImaginary()));
}

// Rect
inline GfRect2i toUsdrt(pxr::GfRect2i v)
{
    return GfRect2i(toUsdrt(v.GetMin()), toUsdrt(v.GetMax()));
}

// Rotation
inline GfRotation toUsdrt(pxr::GfRotation v)
{
    return GfRotation(toUsdrt(v.GetAxis()), v.GetAngle());
}

// Transform
inline GfTransform toUsdrt(pxr::GfTransform v)
{
    return GfTransform(toUsdrt(v.GetTranslation()), toUsdrt(v.GetRotation()), toUsdrt(v.GetScale()),
                       toUsdrt(v.GetPivotPosition()), toUsdrt(v.GetPivotOrientation()));
}

// Ray
inline GfRay toUsdrt(pxr::GfRay v)
{
    return GfRay(toUsdrt(v.GetStartPoint()), toUsdrt(v.GetDirection()));
}

// Frustum
inline GfFrustum::ProjectionType toUsdrt(pxr::GfFrustum::ProjectionType v)
{
    return GfFrustum::ProjectionType(int(v));
}

inline GfFrustum toUsdrt(pxr::GfFrustum v)
{
    return GfFrustum(toUsdrt(v.GetPosition()), toUsdrt(v.GetRotation()), toUsdrt(v.GetWindow()),
                     toUsdrt(v.GetNearFar()), toUsdrt(v.GetProjectionType()), v.GetViewDistance());
}

// BBox3d
inline GfBBox3d toUsdrt(pxr::GfBBox3d v)
{
    return GfBBox3d(toUsdrt(v.GetBox()), toUsdrt(v.GetMatrix()));
}

// Line
inline GfLine toUsdrt(pxr::GfLine v)
{
    return GfLine(toUsdrt(v.GetPoint(0)), toUsdrt(v.GetDirection()));
}

// LineSeg
inline GfLineSeg toUsdrt(pxr::GfLineSeg v)
{
    return GfLineSeg(toUsdrt(v.GetPoint(0)), toUsdrt(v.GetPoint(1)));
}

// Plane
inline GfPlane toUsdrt(pxr::GfPlane p)
{
    return GfPlane(toUsdrt(p.GetNormal()), p.GetDistanceFromOrigin());
}

//-----------------------------------------------------------------------------
// convert to pxr
//-----------------------------------------------------------------------------

template <typename R, typename P>
inline const R& toPxr(const P& usdrtObj)
{
    return reinterpret_cast<const R&>(usdrtObj);
}

// pxr::GfHalf
inline pxr::GfHalf toPxr(GfHalf v)
{
    return toPxr<pxr::GfHalf, GfHalf>(v);
}

// Vec2
inline pxr::GfVec2d toPxr(GfVec2d v)
{
    return toPxr<pxr::GfVec2d, GfVec2d>(v);
}
inline pxr::GfVec2f toPxr(GfVec2f v)
{
    return toPxr<pxr::GfVec2f, GfVec2f>(v);
}
inline pxr::GfVec2h toPxr(GfVec2h v)
{
    return toPxr<pxr::GfVec2h, GfVec2h>(v);
}
inline pxr::GfVec2i toPxr(GfVec2i v)
{
    return toPxr<pxr::GfVec2i, GfVec2i>(v);
}

// Vec3
inline pxr::GfVec3d toPxr(GfVec3d v)
{
    return toPxr<pxr::GfVec3d, GfVec3d>(v);
}
inline pxr::GfVec3f toPxr(GfVec3f v)
{
    return toPxr<pxr::GfVec3f, GfVec3f>(v);
}
inline pxr::GfVec3h toPxr(GfVec3h v)
{
    return toPxr<pxr::GfVec3h, GfVec3h>(v);
}
inline pxr::GfVec3i toPxr(GfVec3i v)
{
    return toPxr<pxr::GfVec3i, GfVec3i>(v);
}

// Vec4
inline pxr::GfVec4d toPxr(GfVec4d v)
{
    return toPxr<pxr::GfVec4d, GfVec4d>(v);
}
inline pxr::GfVec4f toPxr(GfVec4f v)
{
    return toPxr<pxr::GfVec4f, GfVec4f>(v);
}
inline pxr::GfVec4h toPxr(GfVec4h v)
{
    return toPxr<pxr::GfVec4h, GfVec4h>(v);
}
inline pxr::GfVec4i toPxr(GfVec4i v)
{
    return toPxr<pxr::GfVec4i, GfVec4i>(v);
}

// Matrix
inline pxr::GfMatrix2d toPxr(GfMatrix2d v)
{
    return toPxr<pxr::GfMatrix2d, GfMatrix2d>(v);
}
inline pxr::GfMatrix2f toPxr(GfMatrix2f v)
{
    return toPxr<pxr::GfMatrix2f, GfMatrix2f>(v);
}
inline pxr::GfMatrix3d toPxr(GfMatrix3d v)
{
    return toPxr<pxr::GfMatrix3d, GfMatrix3d>(v);
}
inline pxr::GfMatrix3f toPxr(GfMatrix3f v)
{
    return toPxr<pxr::GfMatrix3f, GfMatrix3f>(v);
}
inline pxr::GfMatrix4d toPxr(GfMatrix4d v)
{
    return toPxr<pxr::GfMatrix4d, GfMatrix4d>(v);
}
inline pxr::GfMatrix4f toPxr(GfMatrix4f v)
{
    return toPxr<pxr::GfMatrix4f, GfMatrix4f>(v);
}

// Range
inline pxr::GfRange1d toPxr(GfRange1d v)
{
    return pxr::GfRange1d(v.GetMin(), v.GetMax());
}

inline pxr::GfRange1f toPxr(GfRange1f v)
{
    return pxr::GfRange1f(v.GetMin(), v.GetMax());
}

inline pxr::GfRange2d toPxr(GfRange2d v)
{
    return pxr::GfRange2d(toPxr(v.GetMin()), toPxr(v.GetMax()));
}
inline pxr::GfRange2f toPxr(GfRange2f v)
{
    return pxr::GfRange2f(toPxr(v.GetMin()), toPxr(v.GetMax()));
}
inline pxr::GfRange3d toPxr(GfRange3d v)
{
    return pxr::GfRange3d(toPxr(v.GetMin()), toPxr(v.GetMax()));
}
inline pxr::GfRange3f toPxr(GfRange3f v)
{
    return pxr::GfRange3f(toPxr(v.GetMin()), toPxr(v.GetMax()));
}

// Quat
inline pxr::GfQuatd toPxr(GfQuatd v)
{
    return pxr::GfQuatd(v.GetReal(), toPxr(v.GetImaginary()));
}
inline pxr::GfQuatf toPxr(GfQuatf v)
{
    return pxr::GfQuatf(v.GetReal(), toPxr(v.GetImaginary()));
}
inline pxr::GfQuath toPxr(GfQuath v)
{
    return pxr::GfQuath(toPxr(v.GetReal()), toPxr(v.GetImaginary()));
}

// Rect
inline pxr::GfRect2i toPxr(GfRect2i v)
{
    return pxr::GfRect2i(toPxr(v.GetMin()), toPxr(v.GetMax()));
}

// Rotation
inline pxr::GfRotation toPxr(GfRotation v)
{
    return pxr::GfRotation(toPxr(v.GetAxis()), v.GetAngle());
}

// Transform
inline pxr::GfTransform toPxr(GfTransform v)
{
    return pxr::GfTransform(toPxr(v.GetTranslation()), toPxr(v.GetRotation()), toPxr(v.GetScale()),
                            toPxr(v.GetPivotPosition()), toPxr(v.GetPivotOrientation()));
}

// Ray
inline pxr::GfRay toPxr(GfRay v)
{
    return pxr::GfRay(toPxr(v.GetStartPoint()), toPxr(v.GetDirection()));
}

// Frustum
inline pxr::GfFrustum::ProjectionType toPxr(GfFrustum::ProjectionType v)
{
    return pxr::GfFrustum::ProjectionType(int(v));
}

inline pxr::GfFrustum toPxr(GfFrustum v)
{
    return pxr::GfFrustum(toPxr(v.GetPosition()), toPxr(v.GetRotation()), toPxr(v.GetWindow()), toPxr(v.GetNearFar()),
                          toPxr(v.GetProjectionType()), v.GetViewDistance());
}

// BBox3d
inline pxr::GfBBox3d toPxr(GfBBox3d v)
{
    return pxr::GfBBox3d(toPxr(v.GetBox()), toPxr(v.GetMatrix()));
}

// Line
inline pxr::GfLine toPxr(GfLine v)
{
    return pxr::GfLine(toPxr(v.GetPoint(0)), toPxr(v.GetDirection()));
}

// LineSeg
inline pxr::GfLineSeg toPxr(GfLineSeg v)
{
    return pxr::GfLineSeg(toPxr(v.GetPoint(0)), toPxr(v.GetPoint(1)));
}

// Plane
inline pxr::GfPlane toPxr(GfPlane p)
{
    return pxr::GfPlane(toPxr(p.GetNormal()), p.GetDistanceFromOrigin());
}

} // namespace usdrt
