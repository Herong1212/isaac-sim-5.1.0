// Copyright (c) 2023-2024, NVIDIA CORPORATION. All rights reserved.
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
// Note: This source derived from frustum.h and frustum.cpp in USD and modified for this application.
#pragma once

#include <usdrt/gf/bbox3d.h>
#include <usdrt/gf/math.h>
#include <usdrt/gf/matrix.h>
#include <usdrt/gf/plane.h>
#include <usdrt/gf/range.h>
#include <usdrt/gf/ray.h>
#include <usdrt/gf/rotation.h>
#include <usdrt/gf/vec.h>

#include <algorithm>
#include <iosfwd>
#include <vector>

using namespace std;

namespace usdrt
{

/// \class GfFrustum
///
/// Basic type: View frustum.
///
/// This class represents a viewing frustum in three dimensional eye space. It
/// may represent either a parallel (orthographic) or perspective projection.
/// One can think of the frustum as being defined by 6 boundary planes.
///
/// The frustum is specified using these parameters:
///  \li The \em position of the viewpoint.
///  \li The \em rotation applied to the default view frame, which is
///      looking along the -z axis with the +y axis as the "up"
///      direction.
///  \li The 2D \em window on the reference plane that defines the left,
///      right, top, and bottom planes of the viewing frustum, as
///      described below.
///  \li The distances to the \em near and \em far planes.
///  \li The \em projection \em type
///  \li The view distance.
///
/// The window and near/far parameters combine to define the view frustum as
/// follows. Transform the -z axis and the +y axis by the frustum rotation to
/// get the world-space \em view \em direction and \em up \em direction. Now
/// consider the \em reference \em plane that is perpendicular to the view
/// direction, a distance of referencePlaneDepth from the viewpoint, and whose
/// y axis corresponds to the up direction.  The window rectangle is specified
/// in a 2D coordinate system embedded in this plane. The origin of the
/// coordinate system is the point at which the view direction vector
/// intersects the plane. Therefore, the point (0,1) in this plane is found by
/// moving 1 unit along the up direction vector in this plane. The vector from
/// the viewpoint to the resulting point will form a 45-degree angle with the
/// view direction.
///
/// The view distance is only useful for interactive applications. It can be
/// used to compute a look at point which is useful when rotating around an
/// object of interest.
///
class GfFrustum
{
public:
    /// This enum is used to determine the type of projection represented by a
    /// frustum.
    enum ProjectionType
    {
        Orthographic, ///< Orthographic projection
        Perspective, ///< Perspective projection
    };

    /// This constructor creates an instance with default viewing parameters:
    /// \li The position is the origin.
    /// \li The rotation is the identity rotation. (The view is along
    ///     the -z axis, with the +y axis as "up").
    /// \li The window is -1 to +1 in both dimensions.
    /// \li The near/far interval is (1, 10).
    /// \li The view distance is 5.0.
    /// \li The projection type is \c GfFrustum::Perspective.
    GfFrustum();

    /// This constructor creates an instance with the given viewing
    /// parameters.
    GfFrustum(const usdrt::GfVec3d& position,
              const usdrt::GfRotation& rotation,
              const usdrt::GfRange2d& window,
              const usdrt::GfRange1d& nearFar,
              GfFrustum::ProjectionType projectionType,
              double viewDistance = 5.0);

    /// This constructor creates an instance from a camera matrix (always of a
    /// y-Up camera, also see SetPositionAndRotationFromMatrix) and the given
    /// viewing parameters.
    GfFrustum(const usdrt::GfMatrix4d& camToWorldXf,
              const usdrt::GfRange2d& window,
              const usdrt::GfRange1d& nearFar,
              GfFrustum::ProjectionType projectionType,
              double viewDistance = 5.0);


    // NOTE: To avoid including Boost unless absolutely necessary, hash_value() is not defined here.

    // Equality operator. true iff all parts match.
    bool operator==(const GfFrustum& f) const
    {
        if (_position != f._position)
            return false;
        if (_rotation != f._rotation)
            return false;
        if (_window != f._window)
            return false;
        if (_nearFar != f._nearFar)
            return false;
        if (_viewDistance != f._viewDistance)
            return false;
        if (_projectionType != f._projectionType)
            return false;

        return true;
    }

    // Inequality operator. true iff not equality.
    bool operator!=(const GfFrustum& f) const
    {
        return !(*this == f);
    }

    /// Destructor.
    ~GfFrustum();

    /// \name Value setting and access
    /// The methods in this group set and access the values that are used to
    /// define a frustum.

    /// Sets the position of the frustum in world space.
    void SetPosition(const usdrt::GfVec3d& position)
    {
        _position = position;
        _DirtyFrustumPlanes();
    }

    /// Returns the position of the frustum in world space.
    const usdrt::GfVec3d& GetPosition() const
    {
        return _position;
    }

    /// Sets the orientation of the frustum in world space as a rotation to
    /// apply to the default frame: looking along the -z axis with the +y axis
    /// as "up".
    void SetRotation(const usdrt::GfRotation& rotation)
    {
        _rotation = rotation;
        _DirtyFrustumPlanes();
    }

    /// Returns the orientation of the frustum in world space as a rotation to
    /// apply to the -z axis.
    const usdrt::GfRotation& GetRotation() const
    {
        return _rotation;
    }

    /// Sets the position and rotation of the frustum from a camera matrix
    /// (always from a y-Up camera). The resulting frustum's transform will
    /// always represent a right-handed and orthonormal coordinate sytem
    /// (scale, shear, and projection are removed from the given \p
    /// camToWorldXf).
    void SetPositionAndRotationFromMatrix(const usdrt::GfMatrix4d& camToWorldXf);

    /// Sets the window rectangle in the reference plane that defines the
    /// left, right, top, and bottom planes of the frustum.
    void SetWindow(const usdrt::GfRange2d& window)
    {
        _window = window;
        _DirtyFrustumPlanes();
    }

    /// Returns the window rectangle in the reference plane.
    const usdrt::GfRange2d& GetWindow() const
    {
        return _window;
    }

    /// Returns the depth of the reference plane.
    static double GetReferencePlaneDepth()
    {
        return 1.0;
    }

    /// Sets the near/far interval.
    void SetNearFar(const usdrt::GfRange1d& nearFar)
    {
        _nearFar = nearFar;
        _DirtyFrustumPlanes();
    }

    /// Returns the near/far interval.
    const usdrt::GfRange1d& GetNearFar() const
    {
        return _nearFar;
    }

    /// Sets the view distance.
    void SetViewDistance(double viewDistance)
    {
        _viewDistance = viewDistance;
    }

    /// Returns the view distance.
    double GetViewDistance() const
    {
        return _viewDistance;
    }

    /// Sets the projection type.
    void SetProjectionType(GfFrustum::ProjectionType projectionType)
    {
        _projectionType = projectionType;
        _DirtyFrustumPlanes();
    }

    /// Returns the projection type.
    GfFrustum::ProjectionType GetProjectionType() const
    {
        return _projectionType;
    }

    /// \name Convenience methods
    ///
    /// The methods in this group allow the frustum's data to be accessed and
    /// modified in terms of different representations that may be more
    /// convenient for certain applications.
    ///

    /// Sets up the frustum in a manner similar to \c gluPerspective().
    ///
    /// It sets the projection type to \c GfFrustum::Perspective and sets the
    /// window specification so that the resulting symmetric frustum encloses
    /// an angle of \p fieldOfViewHeight degrees in the vertical direction,
    /// with \p aspectRatio used to figure the angle in the horizontal
    /// direction. The near and far distances are specified as well. The
    /// window coordinates are computed as:
    /// \code
    ///     top    = tan(fieldOfViewHeight / 2)
    ///     bottom = -top
    ///     right  = top * aspectRatio
    ///     left   = -right
    ///     near   = nearDistance
    ///     far    = farDistance
    /// \endcode
    ///
    void SetPerspective(double fieldOfViewHeight, double aspectRatio, double nearDistance, double farDistance);

    /// Sets up the frustum in a manner similar to gluPerspective().
    ///
    /// It sets the projection type to \c GfFrustum::Perspective and
    /// sets the window specification so that:
    ///
    /// If \a isFovVertical is true, the resulting symmetric frustum encloses
    /// an angle of \p fieldOfView degrees in the vertical direction, with \p
    /// aspectRatio used to figure the angle in the horizontal direction.
    ///
    /// If \a isFovVertical is false, the resulting symmetric frustum encloses
    /// an angle of \p fieldOfView degrees in the horizontal direction, with
    /// \p aspectRatio used to figure the angle in the vertical direction.
    ///
    /// The near and far distances are specified as well. The window
    /// coordinates are computed as follows:
    ///
    /// \li if isFovVertical:
    ///     \li top    = tan(fieldOfView / 2)
    ///     \li right  = top * aspectRatio
    /// \li if NOT isFovVertical:
    ///     \li right    = tan(fieldOfView / 2)
    ///     \li top  = right / aspectRation
    /// \li bottom = -top
    /// \li left   = -right
    /// \li near   = nearDistance
    /// \li far    = farDistance
    ///
    void SetPerspective(double fieldOfView, bool isFovVertical, double aspectRatio, double nearDistance, double farDistance);

    /// Returns the current frustum in the format used by \c SetPerspective().
    /// If the current frustum is not a perspective projection, this returns
    /// \c false and leaves the parameters untouched.
    bool GetPerspective(double* fieldOfViewHeight, double* aspectRatio, double* nearDistance, double* farDistance) const;

    /// Returns the current frustum in the format used by \c SetPerspective().
    /// If the current frustum is not a perspective projection, this returns
    /// \c false and leaves the parameters untouched.
    bool GetPerspective(
        bool isFovVertical, double* fieldOfView, double* aspectRatio, double* nearDistance, double* farDistance) const;

    /// Returns the horizontal or vertical fov of the frustum. The fov of the
    /// frustum is not necessarily the same value as displayed in the viewer.
    /// The displayed fov is a function of the focal length or FOV avar. The
    /// frustum's fov may be different due to things like lens breathing.
    ///
    /// If the frustum is not of type \c GfFrustum::Perspective, the returned
    /// FOV will be 0.0.
    ///
    /// \note The default value for \c isFovVertical is false so calling \c
    /// GetFOV without an argument will return the horizontal field of view
    /// which is compatible with menv2x's old GfFrustum::GetFOV routine.
    double GetFOV(bool isFovVertical = false);

    /// Sets up the frustum in a manner similar to \c glOrtho().
    ///
    /// Sets the projection to \c GfFrustum::Orthographic and sets the window
    /// and near/far specifications based on the given values.

    void SetOrthographic(double left, double right, double bottom, double top, double nearPlane, double farPlane);

    /// Returns the current frustum in the format used by \c
    /// SetOrthographic(). If the current frustum is not an orthographic
    /// projection, this returns \c false and leaves the parameters untouched.
    bool GetOrthographic(double* left, double* right, double* bottom, double* top, double* nearPlane, double* farPlane) const;

    /// Modifies the frustum to tightly enclose a sphere with the given center
    /// and radius, using the current view direction. The planes of the
    /// frustum are adjusted as necessary. The given amount of slack is added
    /// to the sphere's radius is used around the sphere to avoid boundary
    /// problems.
    void FitToSphere(const usdrt::GfVec3d& center, double radius, double slack = 0.0);

    /// Transforms the frustum by the given matrix.
    ///
    /// The transformation matrix is applied as follows: the position and the
    /// direction vector are transformed with the given matrix. Then the
    /// length of the new direction vector is used to rescale the near and far
    /// plane and the view distance. Finally, the points that define the
    /// reference plane are transformed by the matrix. This method assures
    /// that the frustum will not be sheared or perspective-projected.
    ///
    /// \note Note that this definition means that the transformed frustum
    /// does not preserve scales very well. Do \em not use this function to
    /// transform a frustum that is to be used for precise operations such as
    /// intersection testing.
    GfFrustum& Transform(const usdrt::GfMatrix4d& matrix);

    /// Returns the normalized world-space view direction vector, which is
    /// computed by rotating the -z axis by the frustum's rotation.
    usdrt::GfVec3d ComputeViewDirection() const;

    /// Returns the normalized world-space up vector, which is computed by
    /// rotating the y axis by the frustum's rotation.
    usdrt::GfVec3d ComputeUpVector() const;

    /// Computes the view frame defined by this frustum. The frame consists of
    /// the view direction, up vector and side vector, as shown in this
    /// diagram.
    ///
    /// \code
    ///            up
    ///            ^   ^
    ///            |  /
    ///            | / view
    ///            |/
    ///            +- - - - > side
    /// \endcode
    ///
    void ComputeViewFrame(usdrt::GfVec3d* side, usdrt::GfVec3d* up, usdrt::GfVec3d* view) const;

    /// Computes and returns the world-space look-at point from the eye point
    /// (position), view direction (rotation), and view distance.
    usdrt::GfVec3d ComputeLookAtPoint() const;

    /// Returns a matrix that represents the viewing transformation for this
    /// frustum.  That is, it returns the matrix that converts points from
    /// world space to eye (frustum) space.
    usdrt::GfMatrix4d ComputeViewMatrix() const;

    /// Returns a matrix that represents the inverse viewing transformation
    /// for this frustum.  That is, it returns the matrix that converts points
    /// from eye (frustum) space to world space.
    usdrt::GfMatrix4d ComputeViewInverse() const;

    /// Returns a GL-style projection matrix corresponding to the frustum's
    /// projection.
    usdrt::GfMatrix4d ComputeProjectionMatrix() const;

    /// Returns the aspect ratio of the frustum, defined as the width of the
    /// window divided by the height. If the height is zero or negative, this
    /// returns 0.
    double ComputeAspectRatio() const;

    /// Returns the world-space corners of the frustum as a vector of 8
    /// points, ordered as:
    /// \li Left bottom near
    /// \li Right bottom near
    /// \li Left top near
    /// \li Right top near
    /// \li Left bottom far
    /// \li Right bottom far
    /// \li Left top far
    /// \li Right top far

    std::vector<usdrt::GfVec3d> ComputeCorners() const;

    /// Returns the world-space corners of the intersection of the frustum
    /// with a plane parallel to the near/far plane at distance d from the
    /// apex, ordered as:
    /// \li Left bottom
    /// \li Right bottom
    /// \li Left top
    /// \li Right top
    /// In particular, it gives the partial result of ComputeCorners when given
    /// near or far distance.

    std::vector<usdrt::GfVec3d> ComputeCornersAtDistance(double d) const;

    /// Returns a frustum that is a narrowed-down version of this frustum,
    /// such that the frustum rectangle on the near plane encloses \p point
    /// with at most \p halfSize[0] distance on the left and right and at most
    /// \p halfSize[1] distance on the top and bottom. (If \p point is closer
    /// than the half size to a side of the frustum, that side is left alone.
    /// The point and sizes are in normalized 2D coordinates; they range from
    /// (-1, -1) at the lower left corner of the near-plane window rectangle
    /// to (1,1) at the upper right corner.
    ///
    /// \p point is a 2d point expressed as a normalized window position.
    ///
    /// This method is useful for computing a volume to use for interactive
    /// picking.
    GfFrustum ComputeNarrowedFrustum(const usdrt::GfVec2d& point, const usdrt::GfVec2d& halfSize) const;

    /// Returns a frustum that is a narrowed-down version of this frustum,
    /// such that the frustum rectangle on the near plane encloses \p point
    /// with at most \p halfSize[0] distance on the left and right and at most
    /// \p halfSize[1] distance on the top and bottom. (If \p point is closer
    /// than the half size to a side of the frustum, that side is left alone.
    /// The point and sizes are in normalized 2D coordinates; they range from
    /// (-1, -1) at the lower left corner of the near-plane window rectangle
    /// to (1,1) at the upper right corner.
    ///
    /// \p point is a 3d point expressed in world coordinates
    ///
    /// This method is useful for computing a volume to use for interactive
    /// picking.
    GfFrustum ComputeNarrowedFrustum(const usdrt::GfVec3d& worldPoint, const usdrt::GfVec2d& halfSize) const;

    /// Builds and returns a \c usdrt::GfRay that starts at the viewpoint and extends
    /// through the given \a windowPos given in normalized coords (-1 to +1 in
    /// both dimensions) window position.
    ///
    /// Contrasted with ComputePickRay(), this method returns a ray whose
    /// origin is the eyepoint, while that method returns a ray whose origin
    /// is on the near plane.
    usdrt::GfRay ComputeRay(const usdrt::GfVec2d& windowPos) const;

    /// Builds and returns a \c usdrt::GfRay that connects the viewpoint to the given
    /// 3d point in worldspace.
    ///
    /// Contrasted with ComputePickRay(), this method returns a ray whose
    /// origin is the eyepoint, while that method returns a ray whose origin
    /// is on the near plane.
    usdrt::GfRay ComputeRay(const usdrt::GfVec3d& worldSpacePos) const;

    /// Builds and returns a \c usdrt::GfRay that can be used for picking at the
    /// given normalized (-1 to +1 in both dimensions) window position.
    ///
    /// Contrasted with ComputeRay(), that method returns a ray whose origin
    /// is the eyepoint, while this method returns a ray whose origin is on
    /// the near plane.
    usdrt::GfRay ComputePickRay(const usdrt::GfVec2d& windowPos) const;

    /// Builds and returns a \c usdrt::GfRay that can be used for picking that
    /// connects the viewpoint to the given 3d point in worldspace.
    usdrt::GfRay ComputePickRay(const usdrt::GfVec3d& worldSpacePos) const;


    /// \name Intersection methods
    ///
    /// The methods in this group implement intersection operations
    /// between this frustum and a given primitive.
    ///

    /// Returns true if the given axis-aligned bbox is inside or intersecting
    /// the frustum. Otherwise, it returns false. Useful when doing picking or
    /// frustum culling.
    bool Intersects(const usdrt::GfBBox3d& bbox) const;

    /// Returns true if the given point is inside or intersecting the frustum.
    /// Otherwise, it returns false.
    bool Intersects(const usdrt::GfVec3d& point) const;

    /// Returns \c true if the line segment formed by the given points is
    /// inside or intersecting the frustum.  Otherwise, it returns false.
    bool Intersects(const usdrt::GfVec3d& p0, const usdrt::GfVec3d& p1) const;

    /// Returns \c true if the triangle formed by the given points is inside
    /// or intersecting the frustum.  Otherwise, it returns false.
    bool Intersects(const usdrt::GfVec3d& p0, const usdrt::GfVec3d& p1, const usdrt::GfVec3d& p2) const;

    /// Returns \c true if the bbox volume intersects the view volume given by
    /// the view-projection matrix, erring on the side of false positives for
    /// efficiency.
    ///
    /// This method is intended for cases where a GfFrustum is not available
    /// or when the view-projection matrix yields a view volume that is not
    /// expressable as a GfFrustum.
    ///
    /// Because it errs on the side of false positives, it is suitable for
    /// early-out tests such as draw or intersection culling.
    ///
    static bool IntersectsViewVolume(const usdrt::GfBBox3d& bbox, const usdrt::GfMatrix4d& vpMat);

private:
    // Dirty the result of _CalculateFrustumPlanes.
    void _DirtyFrustumPlanes();

    // Calculates cached frustum planes used for intersection tests.
    void _CalculateFrustumPlanes() const;

    // Builds and returns a \c usdrt::GfRay that can be used for picking. Given an
    // eye position and direction in camera space, offsets the ray to emanate
    // from the near plane, then transforms into worldspace
    usdrt::GfRay _ComputePickRayOffsetToNearPlane(const usdrt::GfVec3d& camSpaceFrom,
                                                  const usdrt::GfVec3d& camSpaceDir) const;

    // Returns a frustum that is a narrowed-down version of this frustum, such
    // that the frustum rectangle on the near plane encloses \p point with at
    // most \p halfSize[0] distance on the left and right and at most \p
    // halfSize[1] distance on the top and bottom. (If \p point is closer than
    // the half size to a side of the frustum, that side is left alone. The
    // point and sizes are in normalized 2D coordinates; they range from (-1,
    // -1) at the lower left corner of the near-plane window rectangle to
    // (1,1) at the upper right corner.
    //
    // \p windowPoint is expressed in window coordinates
    //
    // This method is useful for computing a volume to use for interactive
    // picking.
    GfFrustum _ComputeNarrowedFrustumSub(const usdrt::GfVec2d windowPoint, const usdrt::GfVec2d& halfSize) const;

    bool _SegmentIntersects(usdrt::GfVec3d const& p0, uint32_t p0Mask, usdrt::GfVec3d const& p1, uint32_t p1Mask) const;

    // Position of the frustum in world space.
    usdrt::GfVec3d _position;

    // Orientation of the frustum in world space as a rotation to apply to the
    // -z axis.
    usdrt::GfRotation _rotation;

    // Window rectangle in the image plane.
    usdrt::GfRange2d _window;

    // Near/far interval.
    usdrt::GfRange1d _nearFar;

    // View distance.
    double _viewDistance;

    // Projection type.
    ProjectionType _projectionType;

    // Cached planes.
    // If empty, the planes have not been calculated.
    mutable std::vector<usdrt::GfPlane> _planes;
};

inline GfFrustum::GfFrustum()
    : _position(0),
      _window(usdrt::GfVec2d(-1.0, -1.0), usdrt::GfVec2d(1.0, 1.0)),
      _nearFar(1.0, 10.0),
      _viewDistance(5.0),
      _projectionType(GfFrustum::Perspective)
{
    _rotation.SetIdentity();
}

inline GfFrustum::GfFrustum(const usdrt::GfVec3d& position,
                            const usdrt::GfRotation& rotation,
                            const usdrt::GfRange2d& window,
                            const usdrt::GfRange1d& nearFar,
                            GfFrustum::ProjectionType projectionType,
                            double viewDistance)
    : _position(position),
      _rotation(rotation),
      _window(window),
      _nearFar(nearFar),
      _viewDistance(viewDistance),
      _projectionType(projectionType)
{
}

inline GfFrustum::GfFrustum(const usdrt::GfMatrix4d& camToWorldXf,
                            const usdrt::GfRange2d& window,
                            const usdrt::GfRange1d& nearFar,
                            GfFrustum::ProjectionType projectionType,
                            double viewDistance)
    : _window(window), _nearFar(nearFar), _viewDistance(viewDistance), _projectionType(projectionType)
{
    SetPositionAndRotationFromMatrix(camToWorldXf);
}

inline GfFrustum::~GfFrustum()
{
}

inline void GfFrustum::SetPerspective(double fieldOfViewHeight, double aspectRatio, double nearDistance, double farDistance)
{
    SetPerspective(fieldOfViewHeight, true, aspectRatio, nearDistance, farDistance);
}

inline void GfFrustum::SetPerspective(
    double fieldOfView, bool isFovVertical, double aspectRatio, double nearDistance, double farDistance)
{
    _projectionType = GfFrustum::Perspective;

    double yDist = 1.0;
    double xDist = 1.0;

    // Check for 0, use 1 in that case
    if (aspectRatio == 0.0)
    {
        aspectRatio = 1.0;
    }

    if (isFovVertical)
    {
        // vertical is taken from the given field of view
        yDist = tan(GfDegreesToRadians(fieldOfView / 2.0)) * GetReferencePlaneDepth();
        // horizontal is determined by aspect ratio
        xDist = yDist * aspectRatio;
    }
    else
    {
        // horizontal is taken from the given field of view
        xDist = tan(GfDegreesToRadians(fieldOfView / 2.0)) * GetReferencePlaneDepth();
        // vertical is determined by aspect ratio
        yDist = xDist / aspectRatio;
    }

    _window.SetMin(usdrt::GfVec2d(-xDist, -yDist));
    _window.SetMax(usdrt::GfVec2d(xDist, yDist));
    _nearFar.SetMin(nearDistance);
    _nearFar.SetMax(farDistance);

    _DirtyFrustumPlanes();
}

inline bool GfFrustum::GetPerspective(double* fieldOfViewHeight,
                                      double* aspectRatio,
                                      double* nearDistance,
                                      double* farDistance) const
{
    return GetPerspective(true, fieldOfViewHeight, aspectRatio, nearDistance, farDistance);
}

inline bool GfFrustum::GetPerspective(
    bool isFovVertical, double* fieldOfView, double* aspectRatio, double* nearDistance, double* farDistance) const
{
    if (_projectionType != GfFrustum::Perspective)
        return false;

    usdrt::GfVec2d winSize = _window.GetSize();

    if (isFovVertical)
    {
        *fieldOfView = 2.0 * GfRadiansToDegrees(atan(winSize[1] / (2.0 * GetReferencePlaneDepth())));
    }
    else
    {
        *fieldOfView = 2.0 * GfRadiansToDegrees(atan(winSize[0] / (2.0 * GetReferencePlaneDepth())));
    }
    *aspectRatio = winSize[0] / winSize[1];

    *nearDistance = _nearFar.GetMin();
    *farDistance = _nearFar.GetMax();

    return true;
}

inline double GfFrustum::GetFOV(bool isFovVertical /* = false */)
{
    double result = 0.0;

    if (GetProjectionType() == GfFrustum::Perspective)
    {
        double aspectRatio;
        double nearDistance;
        double farDistance;

        GetPerspective(isFovVertical, &result, &aspectRatio, &nearDistance, &farDistance);
    }

    return result;
}

inline void GfFrustum::SetOrthographic(double left, double right, double bottom, double top, double nearPlane, double farPlane)
{
    _projectionType = GfFrustum::Orthographic;

    _window.SetMin(usdrt::GfVec2d(left, bottom));
    _window.SetMax(usdrt::GfVec2d(right, top));
    _nearFar.SetMin(nearPlane);
    _nearFar.SetMax(farPlane);

    _DirtyFrustumPlanes();
}

inline bool GfFrustum::GetOrthographic(
    double* left, double* right, double* bottom, double* top, double* nearPlane, double* farPlane) const
{
    if (_projectionType != GfFrustum::Orthographic)
        return false;

    *left = _window.GetMin()[0];
    *right = _window.GetMax()[0];
    *bottom = _window.GetMin()[1];
    *top = _window.GetMax()[1];

    *nearPlane = _nearFar.GetMin();
    *farPlane = _nearFar.GetMax();

    return true;
}

inline void GfFrustum::FitToSphere(const usdrt::GfVec3d& center, double radius, double slack)
{
    //
    // The first part of this computes a good value for
    // _viewDistance and modifies the side (left, right, bottom,
    // and top) coordinates of the frustum as necessary.
    //

    if (_projectionType == GfFrustum::Orthographic)
    {
        // Set the distance so the viewpoint is outside the sphere.
        _viewDistance = radius + slack;
        // Set the camera window to enclose the sphere.
        _window = usdrt::GfRange2d(usdrt::GfVec2d(-radius, -radius), usdrt::GfVec2d(radius, radius));
    }
    else
    {
        // Find the plane coordinate to use to compute the view.
        // Assuming symmetry, it should be the half-size of the
        // smaller of the two viewing angles. If asymmetric in a
        // dimension, use the larger size in that dimension.
        size_t whichDim = ComputeAspectRatio() > 1.0 ? 1 : 0;

        double min = _window.GetMin()[whichDim];
        double max = _window.GetMax()[whichDim];
        double halfSize;
        if (min > 0.0)
        {
            halfSize = max;
        }
        else if (max < 0.0)
        {
            halfSize = min;
        }
        else if (-min > max)
        {
            halfSize = min;
        }
        else
        {
            halfSize = max;
        }

        if (halfSize < 0.0)
        {
            halfSize = -halfSize;
        }
        else if (halfSize == 0.0)
        {
            halfSize = 1.0; // Why not?
        }

        // Determine the distance of the viewpoint from the center of
        // the sphere to make the frustum tangent to the sphere. Use
        // similar triangles: the right triangle formed by the
        // viewpoint and the half-size on the plane is similar to the
        // right triangle formed by the viewpoint and the radius of
        // the sphere at the point of tangency.
        _viewDistance = radius * (1.0 / halfSize) * sqrt(GfSqr(halfSize) + GfSqr(_nearFar.GetMin()));

        // XXX.
        // Hmmm. This is not really used anywhere but in tests, so
        // not gonna fix right now but it seems to me the above equation is
        // off.
        // In the diagram below, similar triangles yield the following
        // equal ratios:
        //    halfSize / referencePlaneDepth = radius / tanDist
        // So tanDist = (radius * referencePlaneDepth) / halfSize
        // Then, because it's a right triangle:
        // viewDistance = sqrt( GfSqr(radius) + GfSqr(tanDist))

        /*

          -----    |\                  /
            ^      |  \ ra            /
            |      |    \ di         /
            |      |      \ us      /
            |      |        \      /
            |      |          \   /
            |      |            \/      <---- make believe this is a right angle
            |      |------------/ ------
            |      |           /     ^
            |      |          /      |
      viewDistance |         /       |
            |      |        /        |
            |      |       /t        |
            |      |      /s        referencePlaneDepth
            |      |     /i          |
            |      |    /d           |
            |      |   /n            |
            |      |  /a             |
            |      | /t              v
            v      |/            ------
         ------
                   |            |
                   |<-halfSize->|
                   |            |
                   |            |
        */
    }

    // Adjust the camera so the near plane touches the sphere and the
    // far plane encloses the sphere.
    _nearFar.SetMin(_viewDistance - (radius + slack));
    _nearFar.SetMax(_nearFar.GetMin() + 2.0 * (radius + slack));

    // Set the camera to use the new position. The view direction
    // should not have changed.
    _position = center - _viewDistance * ComputeViewDirection();
}

inline GfFrustum& GfFrustum::Transform(const usdrt::GfMatrix4d& matrix)
{
    // We'll need the old parameters as we build up the new ones, so, work
    // on a newly instantiated frustum. We'll replace the contents of
    // this frustum with it once we are done. Note that _dirty is true
    // by default, so, there is no need to initialize it here.
    GfFrustum frustum;

    // Copy the projection type
    frustum._projectionType = _projectionType;

    // Transform the position of the frustum
    frustum._position = matrix.Transform(_position);

    // Transform the rotation as follows:
    //   1. build view and direction vectors
    //   2. transform them with the given matrix
    //   3. normalize the vectors and cross them to build an orthonormal frame
    //   4. construct a rotation matrix
    //   5. extract the new rotation from the matrix

    // Generate view direction and up vector
    usdrt::GfVec3d viewDir = ComputeViewDirection();
    usdrt::GfVec3d upVec = ComputeUpVector();

    // Transform by matrix
    usdrt::GfVec3d viewDirPrime = matrix.TransformDir(viewDir);
    usdrt::GfVec3d upVecPrime = matrix.TransformDir(upVec);

    // Normalize. Save the vec size since it will be used to scale near/far.
    double scale = viewDirPrime.Normalize();
    upVecPrime.Normalize();

    // Cross them to get the third axis. Voila. We have an orthonormal frame.
    usdrt::GfVec3d viewRightPrime = GfCross(viewDirPrime, upVecPrime);
    viewRightPrime.Normalize();

    // Construct a rotation matrix using the axes.
    //
    //  [ right     0 ]
    //  [ up        1 ]
    //  [ -viewDir  0 ]
    //  [ 0  0   0  1 ]
    usdrt::GfMatrix4d rotMatrix;
    rotMatrix.SetIdentity();
    // first row
    rotMatrix[0][0] = viewRightPrime[0];
    rotMatrix[0][1] = viewRightPrime[1];
    rotMatrix[0][2] = viewRightPrime[2];

    // second row
    rotMatrix[1][0] = upVecPrime[0];
    rotMatrix[1][1] = upVecPrime[1];
    rotMatrix[1][2] = upVecPrime[2];

    // third row
    rotMatrix[2][0] = -viewDirPrime[0];
    rotMatrix[2][1] = -viewDirPrime[1];
    rotMatrix[2][2] = -viewDirPrime[2];

    // Extract rotation
    frustum._rotation = rotMatrix.ExtractRotation();

    // Since we applied the matrix to the direction vector, we can use
    // its length to find out the scaling that needs to applied to the
    // near and far plane.
    frustum._nearFar = _nearFar * scale;

    // Use the same length to scale the view distance
    frustum._viewDistance = _viewDistance * scale;

    // Transform the reference plane as follows:
    //
    //   - construct two 3D points that are on the reference plane
    //     (left/bottom and right/top corner of the reference window)
    //   - transform the points with the given matrix
    //   - move the window back to one unit from the viewpoint and
    //     extract the 2D coordinates that would form the new reference
    //     window
    //
    //     A note on how we do the last "move" of the reference window:
    //     Using similar triangles and the fact that the reference window
    //     is one unit away from the viewpoint, one can show that it's
    //     sufficient to divide the x and y components of the transformed
    //     corners by the length of the transformed direction vector.
    //
    //     A 2D diagram helps:
    //
    //                            |
    //                            |
    //               |            |
    //       * ------+------------+
    //      vp       |y1          |
    //                            |
    //       \--d1--/             |y2
    //
    //       \-------d2----------/
    //
    //     So, y1/y2 = d1/d2 ==> y1 = y2 * d1/d2
    //     Since d1 = 1 ==> y1 = y2 / d2
    //     The same argument applies to the x coordinate.
    //
    // NOTE: In an orthographic projection, the last step (division by
    // the length of the vector) is skipped.
    //
    // XXX NOTE2:  The above derivation relies on the
    // fact that GetReferecePlaneDepth() is 1.0.
    // If we ever allow this to NOT be 1, we'll need to fix this up.

    const usdrt::GfVec2d& min = _window.GetMin();
    const usdrt::GfVec2d& max = _window.GetMax();

    // Construct the corner points in 3D as follows: construct a starting
    // point by using the x and y coordinates of the reference plane and
    // -1 as the z coordinate. Add the position of the frustum to generate
    // the actual points in world-space coordinates.
    usdrt::GfVec3d leftBottom = _position + _rotation.TransformDir(usdrt::GfVec3d(min[0], min[1], -1.0));
    usdrt::GfVec3d rightTop = _position + _rotation.TransformDir(usdrt::GfVec3d(max[0], max[1], -1.0));

    // Now, transform the corner points by the given matrix
    leftBottom = matrix.Transform(leftBottom);
    rightTop = matrix.Transform(rightTop);

    // Subtract the transformed frustum position from the transformed
    // corner points. Then, rotate the points using the rotation that would
    // transform the view direction vector back to (0, 0, -1). This brings
    // the corner points from the woorld coordinate system into the local
    // frustum one.
    leftBottom -= frustum._position;
    rightTop -= frustum._position;
    leftBottom = frustum._rotation.GetInverse().TransformDir(leftBottom);
    rightTop = frustum._rotation.GetInverse().TransformDir(rightTop);

    // Finally, use the similar triangles trick to bring the corner
    // points back at one unit away from the point. These scaled x and
    // y coordinates can be directly used to construct the new
    // transformed reference plane.  Skip the scaling step for an
    // orthographic projection, though.
    if (_projectionType == Perspective)
    {
        leftBottom /= scale;
        rightTop /= scale;
    }

    frustum._window.SetMin(usdrt::GfVec2d(leftBottom[0], leftBottom[1]));
    frustum._window.SetMax(usdrt::GfVec2d(rightTop[0], rightTop[1]));

    // Note that negative scales in the transform have the potential
    // to flip the window.  Fix it if necessary.
    usdrt::GfVec2d wMin = frustum._window.GetMin();
    usdrt::GfVec2d wMax = frustum._window.GetMax();
    // Make sure left < right
    if (wMin[0] > wMax[0])
    {
        std::swap(wMin[0], wMax[0]);
    }
    // Make sure bottom < top
    if (wMin[1] > wMax[1])
    {
        std::swap(wMin[1], wMax[1]);
    }
    frustum._window.SetMin(wMin);
    frustum._window.SetMax(wMax);

    *this = frustum;

    return *this;
}

inline usdrt::GfVec3d GfFrustum::ComputeViewDirection() const
{
    return _rotation.TransformDir(-usdrt::GfVec3d::ZAxis());
}

inline usdrt::GfVec3d GfFrustum::ComputeUpVector() const
{
    return _rotation.TransformDir(usdrt::GfVec3d::YAxis());
}

inline void GfFrustum::ComputeViewFrame(usdrt::GfVec3d* side, usdrt::GfVec3d* up, usdrt::GfVec3d* view) const
{
    *up = ComputeUpVector();
    *view = ComputeViewDirection();
    *side = GfCross(*view, *up);
}

inline usdrt::GfVec3d GfFrustum::ComputeLookAtPoint() const
{
    return _position + _viewDistance * ComputeViewDirection();
}

inline usdrt::GfMatrix4d GfFrustum::ComputeViewMatrix() const
{
    usdrt::GfMatrix4d m;
    m.SetLookAt<GfRotation>(_position, _rotation);
    return m;
}

inline usdrt::GfMatrix4d GfFrustum::ComputeViewInverse() const
{
    return ComputeViewMatrix().GetInverse();
}

inline usdrt::GfMatrix4d GfFrustum::ComputeProjectionMatrix() const
{
    // Build the projection matrix per Section 2.11 of
    // The OpenGL Specification: Coordinate Transforms.
    usdrt::GfMatrix4d matrix;
    matrix.SetIdentity();

    const double l = _window.GetMin()[0];
    const double r = _window.GetMax()[0];
    const double b = _window.GetMin()[1];
    const double t = _window.GetMax()[1];
    const double n = _nearFar.GetMin();
    const double f = _nearFar.GetMax();

    const double rl = r - l;
    const double tb = t - b;
    const double fn = f - n;

    if (_projectionType == GfFrustum::Orthographic)
    {
        matrix[0][0] = 2.0 / rl;
        matrix[1][1] = 2.0 / tb;
        matrix[2][2] = -2.0 / fn;
        matrix[3][0] = -(r + l) / rl;
        matrix[3][1] = -(t + b) / tb;
        matrix[3][2] = -(f + n) / fn;
    }
    else
    {
        // Perspective:
        // The window coordinates are specified with respect to the
        // reference plane (near == 1).
        // XXX Note: If we ever allow reference plane depth to be other
        // than 1.0, we'll need to revisit this.
        matrix[0][0] = 2.0 / rl;
        matrix[1][1] = 2.0 / tb;
        matrix[2][2] = -(f + n) / fn;
        matrix[2][0] = (r + l) / rl;
        matrix[2][1] = (t + b) / tb;
        matrix[3][2] = -2.0 * n * f / fn;
        matrix[2][3] = -1.0;
        matrix[3][3] = 0.0;
    }

    return matrix;
}

inline double GfFrustum::ComputeAspectRatio() const
{
    usdrt::GfVec2d winSize = _window.GetSize();
    double aspectRatio = 0.0;

    if (winSize[1] != 0.0)
        // Negative winsize is used for envcubes, believe it or not.
        aspectRatio = fabs(winSize[0] / winSize[1]);

    return aspectRatio;
}

inline vector<usdrt::GfVec3d> GfFrustum::ComputeCorners() const
{
    const usdrt::GfVec2d& winMin = _window.GetMin();
    const usdrt::GfVec2d& winMax = _window.GetMax();
    double _near = _nearFar.GetMin();
    double _far = _nearFar.GetMax();

    vector<usdrt::GfVec3d> corners;
    corners.reserve(8);

    if (_projectionType == Perspective)
    {
        // Compute the eye-space corners of the near-plane and
        // far-plane frustum rectangles using similar triangles. The
        // reference plane in which the window rectangle is defined is
        // a distance of 1 from the eyepoint. By similar triangles,
        // just multiply the window points by near and far to get the
        // near and far rectangles.
        // XXX Note: If we ever allow reference plane depth to be other
        // than 1.0, we'll need to revisit this.
        corners.push_back(usdrt::GfVec3d(_near * winMin[0], _near * winMin[1], -_near));
        corners.push_back(usdrt::GfVec3d(_near * winMax[0], _near * winMin[1], -_near));
        corners.push_back(usdrt::GfVec3d(_near * winMin[0], _near * winMax[1], -_near));
        corners.push_back(usdrt::GfVec3d(_near * winMax[0], _near * winMax[1], -_near));
        corners.push_back(usdrt::GfVec3d(_far * winMin[0], _far * winMin[1], -_far));
        corners.push_back(usdrt::GfVec3d(_far * winMax[0], _far * winMin[1], -_far));
        corners.push_back(usdrt::GfVec3d(_far * winMin[0], _far * winMax[1], -_far));
        corners.push_back(usdrt::GfVec3d(_far * winMax[0], _far * winMax[1], -_far));
    }
    else
    {
        // Just use the reference plane rectangle as is, translated to
        // the near and far planes.
        corners.push_back(usdrt::GfVec3d(winMin[0], winMin[1], -_near));
        corners.push_back(usdrt::GfVec3d(winMax[0], winMin[1], -_near));
        corners.push_back(usdrt::GfVec3d(winMin[0], winMax[1], -_near));
        corners.push_back(usdrt::GfVec3d(winMax[0], winMax[1], -_near));
        corners.push_back(usdrt::GfVec3d(winMin[0], winMin[1], -_far));
        corners.push_back(usdrt::GfVec3d(winMax[0], winMin[1], -_far));
        corners.push_back(usdrt::GfVec3d(winMin[0], winMax[1], -_far));
        corners.push_back(usdrt::GfVec3d(winMax[0], winMax[1], -_far));
    }

    // Each corner is then transformed into world space by the inverse
    // of the view matrix.
    usdrt::GfMatrix4d m = ComputeViewInverse();
    for (int i = 0; i < 8; i++)
        corners[i] = m.Transform(corners[i]);

    return corners;
}

inline vector<usdrt::GfVec3d> GfFrustum::ComputeCornersAtDistance(double d) const
{
    const usdrt::GfVec2d& winMin = _window.GetMin();
    const usdrt::GfVec2d& winMax = _window.GetMax();

    vector<usdrt::GfVec3d> corners;
    corners.reserve(4);

    if (_projectionType == Perspective)
    {
        // Similar to ComputeCorners
        corners.push_back(usdrt::GfVec3d(d * winMin[0], d * winMin[1], -d));
        corners.push_back(usdrt::GfVec3d(d * winMax[0], d * winMin[1], -d));
        corners.push_back(usdrt::GfVec3d(d * winMin[0], d * winMax[1], -d));
        corners.push_back(usdrt::GfVec3d(d * winMax[0], d * winMax[1], -d));
    }
    else
    {
        corners.push_back(usdrt::GfVec3d(winMin[0], winMin[1], -d));
        corners.push_back(usdrt::GfVec3d(winMax[0], winMin[1], -d));
        corners.push_back(usdrt::GfVec3d(winMin[0], winMax[1], -d));
        corners.push_back(usdrt::GfVec3d(winMax[0], winMax[1], -d));
    }

    // Each corner is then transformed into world space by the inverse
    // of the view matrix.
    const usdrt::GfMatrix4d m = ComputeViewInverse();
    for (int i = 0; i < 4; i++)
        corners[i] = m.Transform(corners[i]);

    return corners;
}

inline GfFrustum GfFrustum::ComputeNarrowedFrustum(const usdrt::GfVec2d& point, const usdrt::GfVec2d& halfSize) const
{
    // Map the point from normalized space (-1 to 1) onto the frustum's
    // window. First, convert the point into the range from 0 to 1,
    // then interpolate in the window rectangle.
    usdrt::GfVec2d scaledPoint = .5 * (usdrt::GfVec2d(1.0, 1.0) + point);
    usdrt::GfVec2d windowPoint = _window.GetMin() + GfCompMult(scaledPoint, _window.GetSize());

    return _ComputeNarrowedFrustumSub(windowPoint, halfSize);
}

inline GfFrustum GfFrustum::ComputeNarrowedFrustum(const usdrt::GfVec3d& worldPoint, const usdrt::GfVec2d& halfSize) const
{
    // Map the point from worldspace onto the frustum's window
    usdrt::GfVec3d lclPt = ComputeViewMatrix().Transform(worldPoint);
    if (lclPt[2] >= 0)
    {
        // error Given worldPoint is behind or at the eye
        // Start with this frustum
        return *this;
    }
    double scaleFactor = _nearFar.GetMin() / -lclPt[2];
    usdrt::GfVec2d windowPoint(lclPt[0] * scaleFactor, lclPt[1] * scaleFactor);

    return _ComputeNarrowedFrustumSub(windowPoint, halfSize);
}

inline GfFrustum GfFrustum::_ComputeNarrowedFrustumSub(const usdrt::GfVec2d windowPoint,
                                                       const usdrt::GfVec2d& halfSize) const
{
    // Start with this frustum
    GfFrustum narrowedFrustum = *this;

    // Also convert the sizes.
    usdrt::GfVec2d halfSizeOnRefPlane = .5 * GfCompMult(halfSize, _window.GetSize());

    // Shrink the narrowed frustum's window to surround the point.
    usdrt::GfVec2d min = windowPoint - halfSizeOnRefPlane;
    usdrt::GfVec2d max = windowPoint + halfSizeOnRefPlane;

    // Make sure the new bounds are within the old window.
    if (min[0] < _window.GetMin()[0])
        min[0] = _window.GetMin()[0];
    if (min[1] < _window.GetMin()[1])
        min[1] = _window.GetMin()[1];
    if (max[0] > _window.GetMax()[0])
        max[0] = _window.GetMax()[0];
    if (max[1] > _window.GetMax()[1])
        max[1] = _window.GetMax()[1];

    // Set the window to the result.
    narrowedFrustum.SetWindow(usdrt::GfRange2d(min, max));

    return narrowedFrustum;
}

// Utility function for mapping an input value from
// one range to another.
inline static double _Rescale(double in, double inA, double inB, double outA, double outB)
{
    double factor = (inA == inB) ? 0.0 : ((inA - in) / (inA - inB));
    return outA + ((outB - outA) * factor);
}

inline static usdrt::GfRay _ComputeUntransformedRay(GfFrustum::ProjectionType projectionType,
                                                    const usdrt::GfRange2d& window,
                                                    const usdrt::GfVec2d& windowPos)
{
    // Compute position on window, from provided normalized
    // (-1 to 1) coordinates.
    double winX = _Rescale(windowPos[0], -1.0, 1.0, window.GetMin()[0], window.GetMax()[0]);
    double winY = _Rescale(windowPos[1], -1.0, 1.0, window.GetMin()[1], window.GetMax()[1]);

    // Compute the camera-space starting point (the viewpoint) and
    // direction (toward the point on the window).
    usdrt::GfVec3d pos;
    usdrt::GfVec3d dir;
    if (projectionType == GfFrustum::Perspective)
    {
        pos = usdrt::GfVec3d(0);
        dir = usdrt::GfVec3d(winX, winY, -1.0).GetNormalized();
    }
    else
    {
        pos.Set(winX, winY, 0.0);
        dir = -usdrt::GfVec3d::ZAxis();
    }

    // Build and return the ray
    return usdrt::GfRay(pos, dir);
}

inline usdrt::GfRay GfFrustum::ComputeRay(const usdrt::GfVec2d& windowPos) const
{
    usdrt::GfRay ray = _ComputeUntransformedRay(_projectionType, _window, windowPos);

    // Transform these by the inverse of the view matrix.
    const usdrt::GfMatrix4d& viewInverse = ComputeViewInverse();
    usdrt::GfVec3d rayFrom = viewInverse.Transform(ray.GetStartPoint());
    usdrt::GfVec3d rayDir = viewInverse.TransformDir(ray.GetDirection());

    // Build and return the ray
    return usdrt::GfRay(rayFrom, rayDir);
}

inline usdrt::GfRay GfFrustum::ComputePickRay(const usdrt::GfVec2d& windowPos) const
{
    usdrt::GfRay ray = _ComputeUntransformedRay(_projectionType, _window, windowPos);
    return _ComputePickRayOffsetToNearPlane(ray.GetStartPoint(), ray.GetDirection());
}

inline usdrt::GfRay GfFrustum::ComputeRay(const usdrt::GfVec3d& worldSpacePos) const
{
    usdrt::GfVec3d camSpaceToPos = ComputeViewMatrix().Transform(worldSpacePos);

    // Compute the camera-space starting point (the viewpoint) and
    // direction (toward the point camSpaceToPos).
    usdrt::GfVec3d pos;
    usdrt::GfVec3d dir;
    if (_projectionType == Perspective)
    {
        pos = usdrt::GfVec3d(0);
        dir = camSpaceToPos.GetNormalized();
    }
    else
    {
        pos.Set(camSpaceToPos[0], camSpaceToPos[1], 0.0);
        dir = -usdrt::GfVec3d::ZAxis();
    }

    // Transform these by the inverse of the view matrix.
    const usdrt::GfMatrix4d& viewInverse = ComputeViewInverse();
    usdrt::GfVec3d rayFrom = viewInverse.Transform(pos);
    usdrt::GfVec3d rayDir = viewInverse.TransformDir(dir);

    // Build and return the ray
    return usdrt::GfRay(rayFrom, rayDir);
}

inline usdrt::GfRay GfFrustum::ComputePickRay(const usdrt::GfVec3d& worldSpacePos) const
{
    usdrt::GfVec3d camSpaceToPos = ComputeViewMatrix().Transform(worldSpacePos);

    // Compute the camera-space starting point (the viewpoint) and
    // direction (toward the point camSpaceToPos).
    usdrt::GfVec3d pos;
    usdrt::GfVec3d dir;
    if (_projectionType == Perspective)
    {
        pos = usdrt::GfVec3d(0);
        dir = camSpaceToPos.GetNormalized();
    }
    else
    {
        pos.Set(camSpaceToPos[0], camSpaceToPos[1], 0.0);
        dir = -usdrt::GfVec3d::ZAxis();
    }

    return _ComputePickRayOffsetToNearPlane(pos, dir);
}

inline usdrt::GfRay GfFrustum::_ComputePickRayOffsetToNearPlane(const usdrt::GfVec3d& camSpaceFrom,
                                                                const usdrt::GfVec3d& camSpaceDir) const
{
    // Move the starting point to the near plane so we don't pick
    // anything that's clipped out of view.
    usdrt::GfVec3d rayFrom = camSpaceFrom + _nearFar.GetMin() * camSpaceDir;

    // Transform these by the inverse of the view matrix.
    const usdrt::GfMatrix4d& viewInverse = ComputeViewInverse();
    rayFrom = viewInverse.Transform(rayFrom);
    usdrt::GfVec3d rayDir = viewInverse.TransformDir(camSpaceDir);

    // Build and return the ray
    return usdrt::GfRay(rayFrom, rayDir);
}

inline bool GfFrustum::Intersects(const usdrt::GfBBox3d& bbox) const
{
    if (bbox.GetBox().IsEmpty())
        return false;

    // Recalculate frustum planes if necessary
    _CalculateFrustumPlanes();

    // Get the bbox in its local space and the matrix that converts
    // world space to that local space.
    const usdrt::GfRange3d& localBBox = bbox.GetRange();
    const usdrt::GfMatrix4d& worldToLocal = bbox.GetInverseMatrix();

    // Test the bbox against each of the frustum planes, transforming
    // the plane by the inverse of the matrix to bring it into the
    // bbox's local space.
    for (size_t i = 0; i < _planes.size(); i++)
    {

        usdrt::GfPlane localPlane = _planes[i];
        localPlane.Transform(worldToLocal);

        if (!localPlane.IntersectsPositiveHalfSpace(localBBox))
            return false;
    }

    return true;
}

inline bool GfFrustum::Intersects(const usdrt::GfVec3d& point) const
{
    // Recalculate frustum planes if necessary
    _CalculateFrustumPlanes();

    // Determine if the point is inside/intersecting the frustum. Quit early
    // if the point is outside of any of the frustum planes.
    for (size_t i = 0; i < _planes.size(); i++)
    {
        if (!_planes[i].IntersectsPositiveHalfSpace(point))
        {
            return false;
        }
    }

    return true;
}

inline static uint32_t _CalcIntersectionBitMask(const std::vector<usdrt::GfPlane>& planes, usdrt::GfVec3d const& p)
{
    return (1 << 0) * planes[0].IntersectsPositiveHalfSpace(p) + (1 << 1) * planes[1].IntersectsPositiveHalfSpace(p) +
           (1 << 2) * planes[2].IntersectsPositiveHalfSpace(p) + (1 << 3) * planes[3].IntersectsPositiveHalfSpace(p) +
           (1 << 4) * planes[4].IntersectsPositiveHalfSpace(p) + (1 << 5) * planes[5].IntersectsPositiveHalfSpace(p);
}

inline bool GfFrustum::_SegmentIntersects(usdrt::GfVec3d const& p0,
                                          uint32_t p0Mask,
                                          usdrt::GfVec3d const& p1,
                                          uint32_t p1Mask) const
{
    // If any of the 6 bits is 0 in both masks, then both points are
    // on the bad side of the corresponding plane. This means that
    // there can't be any intersection.
    if ((p0Mask | p1Mask) != 0x3F)
        return false;

    // If either of the masks has all 6 planes set, the point is
    // inside the frustum, so there's an intersection.
    if ((p0Mask == 0x3F) || (p1Mask == 0x3F))
        return true;

    // If we get here, the 2 points of the segment are both outside
    // the frustum, but not both on the outside of any single plane.

    // Now we can clip the segment against each plane that it
    // straddles to see if the resulting segment has any length.
    // Perform the clipping using parametric coordinates, where t=0
    // represents p0 and t=1 represents p1. Use v = the vector from p0
    // to p1.
    double t0 = 0.0;
    double t1 = 1.0;
    usdrt::GfVec3d v = p1 - p0;

    for (size_t i = 0; i < _planes.size(); ++i)
    {
        const usdrt::GfPlane& plane = _planes[i];
        const uint32_t planeBit = 1 << i;

        uint32_t p0Bit = p0Mask & planeBit;
        uint32_t p1Bit = p1Mask & planeBit;

        // Do this only if the points straddle the plane, meaning they
        // have different values for the bit.
        if (p0Bit == p1Bit)
            continue;

        // To find the parametric distance t at the intersection of a
        // plane and the line defined by (p0 + t * v):
        //
        //   Substitute the intersection point (p0 + t * v) into the
        //   plane equation to get   n . (p0 + t * v) - d = 0
        //
        //   Solve for t:  t = - (n . p0 - d) / (n . v)
        //      But (n . p0 - d) is the distance of p0 from the plane.
        double t = -plane.GetDistance(p0) / (plane.GetNormal() * v);

        // If p0 is inside and p1 is outside, replace t1. Otherwise,
        // replace t0.
        if (p0Bit)
        {
            if (t < t1)
                t1 = t;
        }
        else
        {
            if (t > t0)
                t0 = t;
        }

        // If there is no line segment left, there's no intersection.
        if (t0 > t1)
            return false;
    }

    // If we get here, there's an intersection
    return true;
}

inline bool GfFrustum::Intersects(const usdrt::GfVec3d& p0, const usdrt::GfVec3d& p1) const
{
    // Recalculate frustum planes if necessary
    _CalculateFrustumPlanes();

    // Compute the intersection masks for each point. There is one bit
    // in each mask for each of the 6 planes.
    return _SegmentIntersects(p0, _CalcIntersectionBitMask(_planes, p0), p1, _CalcIntersectionBitMask(_planes, p1));
}

inline bool GfFrustum::Intersects(const usdrt::GfVec3d& p0, const usdrt::GfVec3d& p1, const usdrt::GfVec3d& p2) const
{
    // Recalculate frustum planes if necessary
    _CalculateFrustumPlanes();

    // Compute the intersection masks for each point. There is one bit
    // in each mask for each of the 6 planes.
    uint32_t p0Mask = _CalcIntersectionBitMask(_planes, p0);
    uint32_t p1Mask = _CalcIntersectionBitMask(_planes, p1);
    uint32_t p2Mask = _CalcIntersectionBitMask(_planes, p2);

    // If any of the 6 bits is 0 in all masks, then all 3 points are
    // on the bad side of the corresponding plane. This means that
    // there can't be any intersection.
    if ((p0Mask | p1Mask | p2Mask) != 0x3F)
        return false;

    // If any of the masks has all 6 planes set, the point is inside
    // the frustum, so there's an intersection.
    if ((p0Mask == 0x3F) || (p1Mask == 0x3F) || (p2Mask == 0x3F))
        return true;

    // If we get here, the 3 points of the triangle are all outside
    // the frustum, but not all on the outside of any single plane.
    // There are now 3 remaining possibilities:
    //
    //  (1) At least one edge of the triangle intersects the frustum.
    //  (2) The triangle completely encloses the frustum.
    //  (3) Neither of the above is true, so there is no intersection.

    // Test case (1) by intersecting all three edges with the
    // frustum.
    if (_SegmentIntersects(p0, p0Mask, p1, p1Mask) || _SegmentIntersects(p1, p1Mask, p2, p2Mask) ||
        _SegmentIntersects(p2, p2Mask, p0, p0Mask))
        return true;


    // That leaves cases (2) and (3).

    // Test for case 2 by computing rays from the viewpoint
    // to the far corners, and doing a ray-triangle
    // intersection test.
    // If all 3 points of the triangle lie between the near/far planes,
    // then we only need to test intersection of 1 corner's ray.
    // Otherwise, we test all 4 corners and if any hit, the frustum is inside
    // the triangle.  If all miss, then the frustum is outside.
    // If the points don't lie between near/far, then  we have to test all
    // 4 corners to catch the case when the triangle is being partially
    // clipped by the near/far plane.
    size_t numCornersToCheck = 4;
    // XXX Note: 4 & 5 below are highly dependent on
    // _CalculateFrustumPlanes implementation
    uint32_t nearBit = (1 << 4);
    uint32_t farBit = (1 << 5);
    if ((p0Mask & nearBit) && (p1Mask & nearBit) && (p2Mask & nearBit) && (p0Mask & farBit) && (p1Mask & farBit) &&
        (p2Mask & farBit))
    {
        numCornersToCheck = 1;
    }

    for (size_t i = 0; i < numCornersToCheck; ++i)
    {
        usdrt::GfVec2d pickPoint = (i == 0) ? usdrt::GfVec2d(-1.0, -1.0) :
                                   (i == 1) ? usdrt::GfVec2d(-1.0, 1.0) :
                                   (i == 2) ? usdrt::GfVec2d(1.0, 1.0) :
                                              usdrt::GfVec2d(1.0, -1.0);
        usdrt::GfRay pickRay = ComputePickRay(pickPoint);
        double distance;
        if (pickRay.Intersect(p0, p1, p2, &distance, NULL, NULL))
        {
            return true;
        }
    }


    // Must be case 3.
    return false;
}

inline void GfFrustum::_DirtyFrustumPlanes()
{
    _planes.clear();
}

inline void GfFrustum::_CalculateFrustumPlanes() const
{
    if (!_planes.empty())
        return;

    _planes.reserve(6);

    // These are values we need to construct the planes.
    const usdrt::GfVec2d& winMin = _window.GetMin();
    const usdrt::GfVec2d& winMax = _window.GetMax();
    double _near = _nearFar.GetMin();
    double _far = _nearFar.GetMax();
    usdrt::GfMatrix4d m = ComputeViewInverse();

    // For a perspective frustum, we use the viewpoint and four
    // corners of the near-plane frustum rectangle to define the 4
    // planes forming the left, right, top, and bottom sides of the
    // frustum.
    if (_projectionType == GfFrustum::Perspective)
    {

        //
        // Get the eye-space viewpoint (the origin) and the four corners
        // of the near-plane frustum rectangle using similar triangles.
        //
        // This picture may help:
        //
        //                  top of near plane
        //                  frustum rectangle
        //
        //                  + --
        //                / |  |
        //              /   |  |
        //            /     |  | h
        //          /       |  |
        //        /         |  |
        //   vp +-----------+ --
        //                    center of near plane frustum rectangle
        //      |___________|
        //           near
        //
        // The height (h) of this triangle is found by the following
        // equation, based on the definition of the _window member
        // variable, which is the size of the image rectangle in the
        // reference plane (a distance of 1 from the viewpoint):
        //
        //      h       _window.GetMax()[1]
        //    ------ = --------------------
        //     near             1
        //
        // Solving for h gets the height of the triangle. Doing the
        // similar math for the other 3 sizes of the near-plane
        // rectangle is left as an exercise for the reader.
        //
        // XXX Note: If we ever allow reference plane depth to be other
        // than 1.0, we'll need to revisit this.

        usdrt::GfVec3d vp(0.0, 0.0, 0.0);
        usdrt::GfVec3d lb(_near * winMin[0], _near * winMin[1], -_near);
        usdrt::GfVec3d rb(_near * winMax[0], _near * winMin[1], -_near);
        usdrt::GfVec3d lt(_near * winMin[0], _near * winMax[1], -_near);
        usdrt::GfVec3d rt(_near * winMax[0], _near * winMax[1], -_near);

        // Transform all 5 points into world space by the inverse of the
        // view matrix (which converts from world space to eye space).
        vp = m.Transform(vp);
        lb = m.Transform(lb);
        rb = m.Transform(rb);
        lt = m.Transform(lt);
        rt = m.Transform(rt);

        // Construct the 6 planes. The three points defining each plane
        // should obey the right-hand-rule; they should be in counter-clockwise
        // order on the inside of the frustum. This makes the intersection of
        // the half-spaces defined by the planes the contents of the frustum.
        _planes.push_back(usdrt::GfPlane(vp, lb, lt)); // Left
        _planes.push_back(usdrt::GfPlane(vp, rt, rb)); // Right
        _planes.push_back(usdrt::GfPlane(vp, rb, lb)); // Bottom
        _planes.push_back(usdrt::GfPlane(vp, lt, rt)); // Top
        _planes.push_back(usdrt::GfPlane(rb, lb, lt)); // Near
    }

    // For an orthographic projection, we need only the four corners
    // of the near-plane frustum rectangle and the view direction to
    // define the 4 planes forming the left, right, top, and bottom
    // sides of the frustum.
    else
    {

        //
        // The math here is much easier than in the perspective case,
        // because we have parallel lines instead of triangles. Just
        // use the size of the image rectangle in the reference plane,
        // which is the same in the near plane.
        //
        usdrt::GfVec3d lb(winMin[0], winMin[1], -_near);
        usdrt::GfVec3d rb(winMax[0], winMin[1], -_near);
        usdrt::GfVec3d lt(winMin[0], winMax[1], -_near);
        usdrt::GfVec3d rt(winMax[0], winMax[1], -_near);

        // Transform the 4 points into world space by the inverse of
        // the view matrix (which converts from world space to eye
        // space).
        lb = m.Transform(lb);
        rb = m.Transform(rb);
        lt = m.Transform(lt);
        rt = m.Transform(rt);

        // Transform the canonical view direction (-z axis) into world
        // space.
        usdrt::GfVec3d dir = m.TransformDir(-usdrt::GfVec3d::ZAxis());

        // Construct the 5 planes from these 4 points and the
        // eye-space view direction.
        _planes.push_back(usdrt::GfPlane(lt + dir, lt, lb)); // Left
        _planes.push_back(usdrt::GfPlane(rb + dir, rb, rt)); // Right
        _planes.push_back(usdrt::GfPlane(lb + dir, lb, rb)); // Bottom
        _planes.push_back(usdrt::GfPlane(rt + dir, rt, lt)); // Top
        _planes.push_back(usdrt::GfPlane(rb, lb, lt)); // Near
    }

    // The far plane is the opposite to the near plane. To compute the
    // distance from the origin for the far plane, we take the distance
    // for the near plane, add the difference between the far and the near
    // and then negate that. We do the negation since the far plane
    // faces the opposite direction. A small drawing would help:
    //
    //                               far - near
    //                     /---------------------------\ *
    //
    //        |           |                             |
    //        |           |                             |
    //        |           |                             |
    //   <----|---->      |                             |
    // fnormal|nnormal    |                             |
    //        |           |                             |
    //                near plane                     far plane
    //
    //         \---------/ *
    //          ndistance
    //
    //         \---------------------------------------/ *
    //                         fdistance
    //
    // So, fdistance = - (ndistance + (far - near))
    _planes.push_back(usdrt::GfPlane(-_planes[4].GetNormal(), -(_planes[4].GetDistanceFromOrigin() + (_far - _near))));
}

inline bool GfFrustum::IntersectsViewVolume(const usdrt::GfBBox3d& bbox, const usdrt::GfMatrix4d& viewProjMat)
{
    // This implementation is a standard technique employed in frustum
    // culling during rendering.  It correctly culls the box even from
    // view volumes that are not representable by a GfFrustum because of
    // skewed near/far planes, such as the ones produced by
    // presto shadowmap cameras.
    //
    // Its principle of operation:  If all 8 points of
    // the box, when transformed into clip coordinates,
    // are on one side or the other of each dimension's
    // clipping interval, then the entire
    // box volume must lie outside the view volume.

    // Compute the 8 points of the bbox in
    // bbox local space.
    usdrt::GfVec4d points[8];
    const usdrt::GfVec3d& localMin = bbox.GetRange().GetMin();
    const usdrt::GfVec3d& localMax = bbox.GetRange().GetMax();
    points[0] = usdrt::GfVec4d(localMin[0], localMin[1], localMin[2], 1);
    points[1] = usdrt::GfVec4d(localMin[0], localMin[1], localMax[2], 1);
    points[2] = usdrt::GfVec4d(localMin[0], localMax[1], localMin[2], 1);
    points[3] = usdrt::GfVec4d(localMin[0], localMax[1], localMax[2], 1);
    points[4] = usdrt::GfVec4d(localMax[0], localMin[1], localMin[2], 1);
    points[5] = usdrt::GfVec4d(localMax[0], localMin[1], localMax[2], 1);
    points[6] = usdrt::GfVec4d(localMax[0], localMax[1], localMin[2], 1);
    points[7] = usdrt::GfVec4d(localMax[0], localMax[1], localMax[2], 1);

    // Transform bbox local space points into clip space
    for (int i = 0; i < 8; ++i)
    {
        points[i] = points[i] * bbox.GetMatrix() * viewProjMat;
    }

    // clipFlags is a 6-bit field with one bit per +/- per x,y,z,
    // or one per frustum plane.  If the points overlap the
    // clip volume in any axis, then clipFlags will be 0x3f (0b111111).
    int clipFlags = 0;
    for (int i = 0; i < 8; ++i)
    {
        usdrt::GfVec4d clipPos = points[i];

        // flag is used as a 6-bit shift register, as we append
        // results of plane-side testing.  OR-ing all the flags
        // combines all the records of what plane-side the points
        // have been on.
        int flag = 0;
        for (int j = 0; j < 3; ++j)
        {
            // We use +/-clipPos[3] as the interval bound instead of
            // 1,-1 because these coordinates are not normalized.
            flag = (flag << 1) | (clipPos[j] < clipPos[3]);
            flag = (flag << 1) | (clipPos[j] > -clipPos[3]);
        }
        clipFlags |= flag;
    }

    return clipFlags == 0x3f;
}

inline void GfFrustum::SetPositionAndRotationFromMatrix(const usdrt::GfMatrix4d& camToWorldXf)
{
    // First conform matrix to be...
    usdrt::GfMatrix4d conformedXf = camToWorldXf;
    // ... right handed
    if (!conformedXf.IsRightHanded())
    {
        static usdrt::GfMatrix4d flip(usdrt::GfVec4d(-1.0, 1.0, 1.0, 1.0));
        conformedXf = flip * conformedXf;
    }

    // ... and orthonormal
    conformedXf.Orthonormalize();

    SetRotation(conformedXf.ExtractRotation());
    SetPosition(conformedXf.ExtractTranslation());
}

} // namespace usdrt
