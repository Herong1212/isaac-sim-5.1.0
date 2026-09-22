// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

// Copyright 2016 Pixar
//
// Licensed under the Apache License, Version 2.0 (the "Apache License")
// with the following modification; you may not use this file except in
// compliance with the Apache License and the following modification to it:
// Section 6. Trademarks. is deleted and replaced with:
//
// 6. Trademarks. This License does not grant permission to use the trade
//    names, trademarks, service marks, or product names of the Licensor
//    and its affiliates, except as required to comply with Section 4(c) of
//    the License and to reproduce the content of the NOTICE file.
//
// You may obtain a copy of the Apache License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the Apache License with the above modification is
// distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
// KIND, either express or implied. See the Apache License for the specific
// language governing permissions and limitations under the Apache License.
//
// Note: This source derived from lineSeg.h and lineSeg.cpp in USD and modified for this application.
#pragma once

#include <usdrt/gf/line.h>
#include <usdrt/gf/math.h>
#include <usdrt/gf/vec.h>

namespace usdrt
{

/// \class GfLineSeg
///
/// Basic type: 3D line segment
///
/// This class represents a three-dimensional line segment in space.
///
class GfLineSeg
{

public:
    /// The default constructor leaves line parameters undefined.
    GfLineSeg()
    {
    }

    /// Construct a line segment that spans two points.
    GfLineSeg(const usdrt::GfVec3d& p0, const usdrt::GfVec3d& p1)
    {
        _length = _line.Set(p0, p1 - p0);
    }

    /// Return the point on the segment specified by the parameter t.
    /// p = p0 + t * (p1 - p0)
    usdrt::GfVec3d GetPoint(double t) const
    {
        return _line.GetPoint(t * _length);
    }

    /// Return the normalized direction of the line.
    const usdrt::GfVec3d& GetDirection() const
    {
        return _line.GetDirection();
    }

    /// Return the length of the line
    double GetLength() const
    {
        return _length;
    }

    /// Returns the point on the line that is closest to \p point. If
    /// \p t is not \c NULL, it will be set to the parametric
    /// distance along the line of the closest point.

    usdrt::GfVec3d FindClosestPoint(const usdrt::GfVec3d& point, double* t = NULL) const;

    /// Component-wise equality test. The starting points and directions,
    /// must match exactly for lines to be considered equal.
    bool operator==(const GfLineSeg& l) const
    {
        return (_line == l._line && _length == l._length);
    }

    /// Component-wise inequality test. The starting points,
    /// and directions must match exactly for lines to be
    /// considered equal.
    bool operator!=(const GfLineSeg& r) const
    {
        return !(*this == r);
    }

private:
    friend bool GfFindClosestPoints(
        const usdrt::GfLine&, const GfLineSeg&, usdrt::GfVec3d*, usdrt::GfVec3d*, double*, double*);

    friend bool GfFindClosestPoints(const GfLineSeg&, const GfLineSeg&, usdrt::GfVec3d*, usdrt::GfVec3d*, double*, double*);

    usdrt::GfLine _line;
    double _length; // distance from p0 to p1
};

/// Computes the closets points on \p line and \p seg.
///
/// The two points are returned in \p p1 and \p p2. The parametric distances
/// of \p p1 and \p p2 along the line and segment are returned in \p t1 and \p
/// t2.
///
/// This returns \c false if the lines were close enough to parallel that no
/// points could be computed; in this case, the other return values are
/// undefined.
bool GfFindClosestPoints(const usdrt::GfLine& line,
                         const GfLineSeg& seg,
                         usdrt::GfVec3d* p1 = nullptr,
                         usdrt::GfVec3d* p2 = nullptr,
                         double* t1 = nullptr,
                         double* t2 = nullptr);

/// Computes the closets points on two line segments, \p seg1 and \p seg2. The
/// two points are returned in \p p1 and \p p2. The parametric distances of \p
/// p1 and \p p2 along the segments are returned in \p t1 and \p t2.
///
/// This returns \c false if the lines were close enough to parallel that no
/// points could be computed; in this case, the other return values are
/// undefined.
bool GfFindClosestPoints(const GfLineSeg& seg1,
                         const GfLineSeg& seg2,
                         usdrt::GfVec3d* p1 = nullptr,
                         usdrt::GfVec3d* p2 = nullptr,
                         double* t1 = nullptr,
                         double* t2 = nullptr);

inline usdrt::GfVec3d GfLineSeg::FindClosestPoint(const usdrt::GfVec3d& point, double* t) const
{
    // Find the parametric distance, lt, of the closest point on the line
    // and then clamp lt to be on the line segment.

    double lt;
    if (_length == 0.0)
    {
        lt = 0.0;
    }
    else
    {
        _line.FindClosestPoint(point, &lt);

        lt = GfClamp(lt / _length, 0., 1.);
    }

    if (t)
        *t = lt;

    return GetPoint(lt);
}

inline bool GfFindClosestPoints(
    const usdrt::GfLine& line, const GfLineSeg& seg, usdrt::GfVec3d* p1, usdrt::GfVec3d* p2, double* t1, double* t2)
{
    usdrt::GfVec3d cp1, cp2;
    double lt1, lt2;
    if (!GfFindClosestPoints(line, seg._line, &cp1, &cp2, &lt1, &lt2))
        return false;

    lt2 = GfClamp(lt2 / seg._length, 0., 1.);
    cp2 = seg.GetPoint(lt2);

    // If we clamp the line segment, change the rayPoint to be
    // the closest point on the ray to the clamped point.
    if (lt2 <= 0 || lt2 >= 1)
    {
        cp1 = line.FindClosestPoint(cp2, &lt1);
    }

    if (p1)
        *p1 = cp1;

    if (p2)
        *p2 = cp2;

    if (t1)
        *t1 = lt1;

    if (t2)
        *t2 = lt2;

    return true;
}


inline bool GfFindClosestPoints(
    const GfLineSeg& seg1, const GfLineSeg& seg2, usdrt::GfVec3d* p1, usdrt::GfVec3d* p2, double* t1, double* t2)
{
    usdrt::GfVec3d cp1, cp2;
    double lt1, lt2;
    if (!GfFindClosestPoints(seg1._line, seg2._line, &cp1, &cp2, &lt1, &lt2))
        return false;

    lt1 = GfClamp(lt1 / seg1._length, 0., 1.);

    lt2 = GfClamp(lt2 / seg2._length, 0., 1.);

    if (p1)
        *p1 = seg1.GetPoint(lt1);

    if (p2)
        *p2 = seg2.GetPoint(lt2);

    if (t1)
        *t1 = lt1;

    if (t2)
        *t2 = lt2;

    return true;
}

} // usdrt namespace close
