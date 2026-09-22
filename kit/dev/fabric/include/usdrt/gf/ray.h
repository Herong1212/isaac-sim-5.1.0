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
// Note: This source derived from ray.h and ray.cpp in USD and modified for this application.
#pragma once

#include <usdrt/gf/bbox3d.h>
#include <usdrt/gf/line.h>
#include <usdrt/gf/lineSeg.h>
#include <usdrt/gf/math.h>
#include <usdrt/gf/matrix.h>
#include <usdrt/gf/plane.h>
#include <usdrt/gf/range.h>
#include <usdrt/gf/vec.h>

namespace usdrt
{

/// \class GfRay
///
/// Basic type: Ray used for intersection testing
///
/// This class represents a three-dimensional ray in space, typically
/// used for intersection testing. It consists of an origin and a
/// direction.
///
/// Note that by default a \c GfRay does not normalize its direction
/// vector to unit length.
///
/// Note for ray intersections, the start point is included in the computations,
/// i.e., a distance of zero is defined to be intersecting.
///
class GfRay
{

public:
    /// The default constructor leaves the ray parameters undefined.
    GfRay()
    {
    }

    /// This constructor takes a starting point and a direction.
    GfRay(const usdrt::GfVec3d& startPoint, const usdrt::GfVec3d& direction)
    {
        SetPointAndDirection(startPoint, direction);
    }

    /// Sets the ray by specifying a starting point and a direction.

    void SetPointAndDirection(const usdrt::GfVec3d& startPoint, const usdrt::GfVec3d& direction);

    /// Sets the ray by specifying a starting point and an ending point.

    void SetEnds(const usdrt::GfVec3d& startPoint, const usdrt::GfVec3d& endPoint);

    /// Returns the starting point of the segment.
    const usdrt::GfVec3d& GetStartPoint() const
    {
        return _startPoint;
    }

    /// Returns the direction vector of the segment. This is not guaranteed to
    /// be unit length.
    const usdrt::GfVec3d& GetDirection() const
    {
        return _direction;
    }

    /// Returns the point that is \p distance units from the starting point
    /// along the direction vector, expressed in parametic distance.
    usdrt::GfVec3d GetPoint(double distance) const
    {
        return _startPoint + distance * _direction;
    }

    /// Transforms the ray by the given matrix.

    GfRay& Transform(const usdrt::GfMatrix4d& matrix);

    /// Returns the point on the ray that is closest to \p point. If \p
    /// rayDistance is not \c NULL, it will be set to the parametric distance
    /// along the ray of the closest point.

    usdrt::GfVec3d FindClosestPoint(const usdrt::GfVec3d& point, double* rayDistance = NULL) const;

    /// Component-wise equality test. The starting points, directions, and
    /// lengths must match exactly for rays to be considered equal.
    bool operator==(const GfRay& r) const
    {
        return (_startPoint == r._startPoint && _direction == r._direction);
    }

    /// Component-wise inequality test. The starting points, directions, and
    /// lengths must match exactly for rays to be considered equal.
    bool operator!=(const GfRay& r) const
    {
        return !(*this == r);
    }

    /// \name Intersection methods.
    ///
    /// The methods in this group intersect the ray with a geometric entity.

    /// Intersects the ray with the triangle formed by points \p p0, \p p1,
    /// and \p p2, returning \c true if it hits. If there is an intersection,
    /// it also returns the parametric distance to the intersection point in
    /// \p distance, the barycentric coordinates of the intersection point in
    /// \p barycentricCoords and the front-facing flag in \p frontFacing. The
    /// barycentric coordinates are defined with respect to the three vertices
    /// taken in order.  The front-facing flag is \c true if the intersection
    /// hit the side of the triangle that is formed when the vertices are
    /// ordered counter-clockwise (right-hand rule). If any of the return
    /// pointers are \c NULL, the corresponding values are not returned.
    ///
    /// If the distance to the intersection is greater than \p maxDist, then
    /// the method will return false.
    ///
    /// Barycentric coordinates are defined to sum to 1 and satisfy this
    /// relationsip:
    /// \code
    ///     intersectionPoint = (barycentricCoords[0] * p0 +
    ///                          barycentricCoords[1] * p1 +
    ///                          barycentricCoords[2] * p2);
    /// \endcode

    bool Intersect(const usdrt::GfVec3d& p0,
                   const usdrt::GfVec3d& p1,
                   const usdrt::GfVec3d& p2,
                   double* distance = NULL,
                   usdrt::GfVec3d* barycentricCoords = NULL,
                   bool* frontFacing = NULL,
                   double maxDist = std::numeric_limits<double>::infinity()) const;

    /// Intersects the ray with a plane, returning \c true if the ray is not
    /// parallel to the plane and the intersection is within the ray bounds.
    /// If there is an intersection, it also returns the parametric distance
    /// to the intersection point in \p distance and the front-facing flag in
    /// \p frontFacing, if they are not \c NULL. The front-facing flag is \c
    /// true if the intersection is on the side of the plane in which its
    /// normal points.

    bool Intersect(const usdrt::GfPlane& plane, double* distance = NULL, bool* frontFacing = NULL) const;

    /// Intersects the ray with an axis-aligned box, returning \c true if the
    /// ray intersects it at all within bounds. If there is an intersection,
    /// this also returns the parametric distances to the two intersection
    /// points in \p enterDistance and \p exitDistance.

    bool Intersect(const usdrt::GfRange3d& box, double* enterDistance = NULL, double* exitDistance = NULL) const;

    /// Intersects the ray with an oriented box, returning \c true if the
    /// ray intersects it at all within bounds. If there is an intersection,
    /// this also returns the parametric distances to the two intersection
    /// points in \p enterDistance and \p exitDistance.

    bool Intersect(const usdrt::GfBBox3d& box, double* enterDistance = NULL, double* exitDistance = NULL) const;

    /// Intersects the ray with a sphere, returning \c true if the ray
    /// intersects it at all within bounds.  If there is an intersection,
    /// returns the parametric distance to the two intersection points in \p
    /// enterDistance and \p exitDistance.

    bool Intersect(const usdrt::GfVec3d& center,
                   double radius,
                   double* enterDistance = NULL,
                   double* exitDistance = NULL) const;

    /// Intersects the ray with an infinite cylinder, with axis \p axis,
    /// centered at the \p origin, with radius \p radius.
    ///
    /// Returns \c true if the ray intersects it at all within bounds. If
    /// there is an intersection, returns the parametric distance to the two
    /// intersection points in \p enterDistance and \p exitDistance.
    ///
    /// Note this method does not validate whether the radius is valid.

    bool Intersect(const usdrt::GfVec3d& origin,
                   const usdrt::GfVec3d& axis,
                   const double radius,
                   double* enterDistance = NULL,
                   double* exitDistance = NULL) const;

    /// Intersects the ray with an infinite non-double cone, centered at \p
    /// origin, with axis \p axis, radius \p radius and apex at \p height.
    ///
    /// Returns \c true if the ray intersects it at all within bounds. If
    /// there is an intersection, returns the parametric distance to the two
    /// intersection points in \p enterDistance and \p exitDistance.
    ///
    /// Note this method does not validate whether the radius are height are
    /// valid.
    bool Intersect(const usdrt::GfVec3d& origin,
                   const usdrt::GfVec3d& axis,
                   const double radius,
                   const double height,
                   double* enterDistance = NULL,
                   double* exitDistance = NULL) const;


private:
    friend bool GfFindClosestPoints(const GfRay&, const usdrt::GfLine&, usdrt::GfVec3d*, usdrt::GfVec3d*, double*, double*);

    friend bool GfFindClosestPoints(
        const GfRay&, const usdrt::GfLineSeg&, usdrt::GfVec3d*, usdrt::GfVec3d*, double*, double*);

    /// Solves the quadratic equation returning the solutions, if defined, in
    /// \p enterDistance and \p exitDistance, where \p enterDistance is less
    /// than or equal to \p exitDistance.
    bool _SolveQuadratic(
        const double a, const double b, const double c, double* enterDistance = NULL, double* exitDistance = NULL) const;

    /// The starting point of the ray.
    usdrt::GfVec3d _startPoint;
    /// The direction vector.
    usdrt::GfVec3d _direction;
};

/// Computes the closest points between a ray and a line. The two points are
/// returned in \p rayPoint and \p linePoint.  The parametric distance of each
/// point on the lines is returned in \p rayDistance and \p lineDistance.
///
/// This returns \c false if the lines were close enough to parallel that no
/// points could be computed; in this case, the other return values are
/// undefined.
bool GfFindClosestPoints(const GfRay& ray,
                         const usdrt::GfLine& line,
                         usdrt::GfVec3d* rayPoint = nullptr,
                         usdrt::GfVec3d* linePoint = nullptr,
                         double* rayDistance = nullptr,
                         double* lineDistance = nullptr);

/// Computes the closest points between a ray and a line segment. The two
/// points are returned in \p rayPoint and \p segPoint.  The parametric
/// distance of each point is returned in \p rayDistance and \p segDistance.
///
/// This returns \c false if the lines were close enough to parallel that no
/// points could be computed; in this case, the other return values are
/// undefined.
bool GfFindClosestPoints(const GfRay& ray,
                         const usdrt::GfLineSeg& seg,
                         usdrt::GfVec3d* rayPoint = nullptr,
                         usdrt::GfVec3d* segPoint = nullptr,
                         double* rayDistance = nullptr,
                         double* segDistance = nullptr);

// Menv 2x uses SetDirection, but it looks like it is only in
// sgu/rayIntersectAction.cpp so I'm just going to change the name
// and let the compiler complain about any problems.
void GfRay::SetPointAndDirection(const usdrt::GfVec3d& startPoint, const usdrt::GfVec3d& direction)
{
    _startPoint = startPoint;
    _direction = direction;
}

void GfRay::SetEnds(const usdrt::GfVec3d& startPoint, const usdrt::GfVec3d& endPoint)
{
    _startPoint = startPoint;
    _direction = endPoint - startPoint;
}

GfRay& GfRay::Transform(const usdrt::GfMatrix4d& matrix)
{
    _startPoint = matrix.Transform(_startPoint);
    _direction = matrix.TransformDir(_direction);

    return *this;
}

usdrt::GfVec3d GfRay::FindClosestPoint(const usdrt::GfVec3d& point, double* rayDistance) const
{
    usdrt::GfLine l;
    double len = l.Set(_startPoint, _direction);
    double lrd;
    (void)l.FindClosestPoint(point, &lrd);

    if (lrd < 0.0)
        lrd = 0.0;

    if (rayDistance)
        *rayDistance = lrd / len;

    return l.GetPoint(lrd);
}

bool GfFindClosestPoints(const GfRay& ray,
                         const usdrt::GfLine& line,
                         usdrt::GfVec3d* rayPoint,
                         usdrt::GfVec3d* linePoint,
                         double* rayDistance,
                         double* lineDistance)
{
    usdrt::GfLine l;
    double len = l.Set(ray._startPoint, ray._direction);

    usdrt::GfVec3d rp, lp;
    double rd, ld;

    if (!GfFindClosestPoints(l, line, &rp, &lp, &rd, &ld))
        return false;

    if (rd < 0.0)
        rd = 0.0;

    if (rayPoint)
        *rayPoint = l.GetPoint(rd);

    if (linePoint)
        *linePoint = lp;

    if (rayDistance)
        *rayDistance = rd / len;

    if (lineDistance)
        *lineDistance = ld;

    return true;
}

bool GfFindClosestPoints(const GfRay& ray,
                         const usdrt::GfLineSeg& seg,
                         usdrt::GfVec3d* rayPoint,
                         usdrt::GfVec3d* segPoint,
                         double* rayDistance,
                         double* segDistance)
{
    usdrt::GfLine l;
    double len = l.Set(ray._startPoint, ray._direction);

    usdrt::GfVec3d rp, sp;
    double rd, sd;

    if (!GfFindClosestPoints(l, seg, &rp, &sp, &rd, &sd))
        return false;

    if (rd < 0.0)
        rd = 0.0;

    if (rayPoint)
        *rayPoint = l.GetPoint(rd);

    if (segPoint)
        *segPoint = sp;

    if (rayDistance)
        *rayDistance = rd / len;

    if (segDistance)
        *segDistance = sd;

    return true;
}

inline bool GfRay::Intersect(const usdrt::GfVec3d& p0,
                             const usdrt::GfVec3d& p1,
                             const usdrt::GfVec3d& p2,
                             double* distance,
                             usdrt::GfVec3d* barycentricCoords,
                             bool* frontFacing,
                             double maxDist) const
{
    // from limits.h
    double minVectorLength = 1e-10;

    // Intersect the ray with the plane containing the three points.
    usdrt::GfPlane plane(p0, p1, p2);
    double intersectionDist;
    if (!Intersect(plane, &intersectionDist, frontFacing))
        return false;

    if (intersectionDist > maxDist)
        return false;

    // Find the largest component of the plane normal. The other two
    // dimensions are the axes of the aligned plane we will use to
    // project the triangle.
    double xAbs = GfAbs(plane.GetNormal()[0]);
    double yAbs = GfAbs(plane.GetNormal()[1]);
    double zAbs = GfAbs(plane.GetNormal()[2]);
    unsigned int axis0, axis1;
    if (xAbs > yAbs && xAbs > zAbs)
    {
        axis0 = 1;
        axis1 = 2;
    }
    else if (yAbs > zAbs)
    {
        axis0 = 2;
        axis1 = 0;
    }
    else
    {
        axis0 = 0;
        axis1 = 1;
    }

    // Determine if the projected intersection (of the ray's line and
    // the triangle's plane) lies within the projected triangle.
    // Since we deal with only 2 components, we can avoid the third
    // computation.
    double inter0 = _startPoint[axis0] + intersectionDist * _direction[axis0];
    double inter1 = _startPoint[axis1] + intersectionDist * _direction[axis1];
    usdrt::GfVec2d d0(inter0 - p0[axis0], inter1 - p0[axis1]);
    usdrt::GfVec2d d1(p1[axis0] - p0[axis0], p1[axis1] - p0[axis1]);
    usdrt::GfVec2d d2(p2[axis0] - p0[axis0], p2[axis1] - p0[axis1]);

    // XXX This code can miss some intersections on very tiny tris.
    double alpha;
    double beta = ((d0[1] * d1[0] - d0[0] * d1[1]) / (d2[1] * d1[0] - d2[0] * d1[1]));
    // clamp beta to 0 if it is only very slightly less than 0
    if (beta < 0 && beta > -minVectorLength)
    {
        // CODE_COVERAGE_OFF_NO_REPORT - architecture dependent numerics
        beta = 0;
        // CODE_COVERAGE_ON_NO_REPORT
    }
    if (beta < 0.0 || beta > 1.0)
    {
        return false;
    }
    alpha = -1.0;
    if (d1[1] < -minVectorLength || d1[1] > minVectorLength)
        alpha = (d0[1] - beta * d2[1]) / d1[1];
    else
        alpha = (d0[0] - beta * d2[0]) / d1[0];

    // clamp alpha to 0 if it is only very slightly less than 0
    if (alpha < 0 && alpha > -minVectorLength)
    {
        // CODE_COVERAGE_OFF_NO_REPORT - architecture dependent numerics
        alpha = 0;
        // CODE_COVERAGE_ON_NO_REPORT
    }

    // clamp gamma to 0 if it is only very slightly less than 0
    float gamma = 1.0 - (alpha + beta);
    if (gamma < 0 && gamma > -minVectorLength)
    {
        // CODE_COVERAGE_OFF_NO_REPORT - architecture dependent numerics
        gamma = 0;
        // CODE_COVERAGE_ON_NO_REPORT
    }
    if (alpha < 0.0 || gamma < 0.0)
        return false;

    if (distance)
        *distance = intersectionDist;
    if (barycentricCoords)
        barycentricCoords->Set(gamma, alpha, beta);

    return true;
}

inline bool GfRay::Intersect(const usdrt::GfPlane& plane, double* distance, bool* frontFacing) const
{
    // from limits.h
    double minVectorLength = 1e-10;

    // The dot product of the ray direction and the plane normal
    // indicates the angle between them. Reject glancing
    // intersections. Note: this also rejects ill-formed planes with
    // zero normals.
    double d = GfDot(_direction, plane.GetNormal());
    if (d < minVectorLength && d > -minVectorLength)
        return false;

    // Get a point on the plane.
    usdrt::GfVec3d planePoint = plane.GetDistanceFromOrigin() * plane.GetNormal();

    // Compute the parametric distance t to the plane. Reject
    // intersections outside the ray bounds.
    double t = GfDot(planePoint - _startPoint, plane.GetNormal()) / d;
    if (t < 0.0)
        return false;

    if (distance)
        *distance = t;
    if (frontFacing)
        *frontFacing = (d < 0.0);

    return true;
}

inline bool GfRay::Intersect(const usdrt::GfRange3d& box, double* enterDistance, double* exitDistance) const
{
    // from limits.h
    double minVectorLength = 1e-10;

    if (box.IsEmpty())
        return false;

    // Compute the intersection distance of all 6 planes of the
    // box. Save the largest near-plane intersection and the smallest
    // far-plane intersection.
    double maxNearest = -DBL_MAX, minFarthest = DBL_MAX;
    for (size_t i = 0; i < 3; i++)
    {

        // Skip dimensions almost parallel to the ray.
        double d = GetDirection()[i];
        if (GfAbs(d) < minVectorLength)
        {
            // ray is parallel to this set of planes.
            // If origin is not between them, no intersection.
            if (GetStartPoint()[i] < box.GetMin()[i] || GetStartPoint()[i] > box.GetMax()[i])
            {
                return false;
            }
            else
            {
                continue;
            }
        }

        d = 1.0 / d;
        double t1 = d * (box.GetMin()[i] - GetStartPoint()[i]);
        double t2 = d * (box.GetMax()[i] - GetStartPoint()[i]);

        // Make sure t1 is the nearer one
        if (t1 > t2)
        {
            double tmp = t1;
            t1 = t2;
            t2 = tmp;
        }

        // Update the min and max
        if (t1 > maxNearest)
            maxNearest = t1;
        if (t2 < minFarthest)
            minFarthest = t2;
    }

    // If the largest near-plane intersection is after the smallest
    // far-plane intersection, the ray's line misses the box. Also
    // check if both intersections are completely outside the near/far
    // bounds.
    if (maxNearest > minFarthest || minFarthest < 0.0)
        return false;

    if (enterDistance)
        *enterDistance = maxNearest;
    if (exitDistance)
        *exitDistance = minFarthest;
    return true;
}

inline bool GfRay::Intersect(const usdrt::GfBBox3d& box, double* enterDistance, double* exitDistance) const
{
    // Transform the ray to the local space of the bbox.
    GfRay localRay(*this);
    localRay.Transform(box.GetInverseMatrix());

    // We take advantage of the fact that the time of intersection is
    // invariant before/after transformation to just return the results of
    // the intersection in local space.
    return localRay.Intersect(box.GetRange(), enterDistance, exitDistance);
}

inline bool GfRay::Intersect(const usdrt::GfVec3d& center, double radius, double* enterDistance, double* exitDistance) const
{

    usdrt::GfVec3d p1 = _startPoint;
    usdrt::GfVec3d p2 = p1 + _direction;

    // Intersection pt: p = p1 + u (p2 -p1)
    // we are solving for u.
    // where p1 = [x1 y1 z1],  p2 = [x2 y2 z2]
    //
    double A, B, C;
    double x1, x2, x3, y1, y2, y3, z1, z2, z3;
    x1 = p1[0];
    y1 = p1[1];
    z1 = p1[2];
    x2 = p2[0];
    y2 = p2[1];
    z2 = p2[2];
    x3 = center[0];
    y3 = center[1];
    z3 = center[2];

    A = (x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1) + (z2 - z1) * (z2 - z1);
    B = 2 * ((x2 - x1) * (x1 - x3) + (y2 - y1) * (y1 - y3) + (z2 - z1) * (z1 - z3));
    C = x3 * x3 + y3 * y3 + z3 * z3 + x1 * x1 + y1 * y1 + z1 * z1 - 2 * (x3 * x1 + y3 * y1 + z3 * z1) - radius * radius;

    return _SolveQuadratic(A, B, C, enterDistance, exitDistance);
}

inline bool GfRay::Intersect(const usdrt::GfVec3d& origin,
                             const usdrt::GfVec3d& axis,
                             const double radius,
                             double* enterDistance,
                             double* exitDistance) const
{
    usdrt::GfVec3d unitAxis = axis.GetNormalized();

    usdrt::GfVec3d delta = _startPoint - origin;
    usdrt::GfVec3d u = _direction - GfDot(_direction, unitAxis) * unitAxis;
    usdrt::GfVec3d v = delta - GfDot(delta, unitAxis) * unitAxis;

    // Quadratic equation for implicit infinite cylinder
    double a = GfDot(u, u);
    double b = 2.0 * GfDot(u, v);
    double c = GfDot(v, v) - GfSqr(radius);

    return _SolveQuadratic(a, b, c, enterDistance, exitDistance);
}

inline bool GfRay::Intersect(const usdrt::GfVec3d& origin,
                             const usdrt::GfVec3d& axis,
                             const double radius,
                             const double height,
                             double* enterDistance,
                             double* exitDistance) const
{
    usdrt::GfVec3d unitAxis = axis.GetNormalized();

    // Apex of cone
    usdrt::GfVec3d apex = origin + height * unitAxis;

    usdrt::GfVec3d delta = _startPoint - apex;
    usdrt::GfVec3d u = _direction - GfDot(_direction, unitAxis) * unitAxis;
    usdrt::GfVec3d v = delta - GfDot(delta, unitAxis) * unitAxis;

    double p = GfDot(_direction, unitAxis);
    double q = GfDot(delta, unitAxis);

    double cos2 = GfSqr(height) / (GfSqr(height) + GfSqr(radius));
    double sin2 = 1 - cos2;

    double a = cos2 * GfDot(u, u) - sin2 * GfSqr(p);
    double b = 2.0 * (cos2 * GfDot(u, v) - sin2 * p * q);
    double c = cos2 * GfDot(v, v) - sin2 * GfSqr(q);

    if (!_SolveQuadratic(a, b, c, enterDistance, exitDistance))
    {
        return false;
    }

    // Eliminate any solutions on the double cone
    bool enterValid = GfDot(unitAxis, GetPoint(*enterDistance) - apex) <= 0.0;
    bool exitValid = GfDot(unitAxis, GetPoint(*exitDistance) - apex) <= 0.0;

    if ((!enterValid) && (!exitValid))
    {

        // Solutions lie only on double cone
        return false;
    }

    if (!enterValid)
    {
        *enterDistance = *exitDistance;
    }
    else if (!exitValid)
    {
        *exitDistance = *enterDistance;
    }

    return true;
}

inline bool GfRay::_SolveQuadratic(
    const double a, const double b, const double c, double* enterDistance, double* exitDistance) const
{
    const double tolerance = 1e-6;
    if (GfIsClose(a, 0.0, tolerance))
    {
        if (GfIsClose(b, 0.0, tolerance))
        {

            // Degenerate solution
            return false;
        }

        double t = -c / b;

        if (t < 0.0)
        {
            return false;
        }

        if (enterDistance)
        {
            *enterDistance = t;
        }

        if (exitDistance)
        {
            *exitDistance = t;
        }

        return true;
    }

    // Discriminant
    double disc = GfSqr(b) - 4.0 * a * c;

    if (GfIsClose(disc, 0.0, tolerance))
    {

        // Tangent
        double t = -b / (2.0 * a);

        if (t < 0.0)
        {
            return false;
        }

        if (enterDistance)
        {
            *enterDistance = t;
        }

        if (exitDistance)
        {
            *exitDistance = t;
        }

        return true;
    }

    if (disc < 0.0)
    {

        // No intersection
        return false;
    }

    // Two intersection points
    double q = -0.5 * (b + copysign(1.0, b) * GfSqrt(disc));
    double t0 = q / a;
    double t1 = c / q;

    if (t0 > t1)
    {
        std::swap(t0, t1);
    }

    if (t1 >= 0)
    {

        if (enterDistance)
        {
            *enterDistance = t0;
        }

        if (exitDistance)
        {
            *exitDistance = t1;
        }

        return true;
    }

    return false;
}

} // usdrt namespace close
