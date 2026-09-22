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
// Note: This source derived from bbox3d.h and bbox3d.cpp in USD and modified for this application.
#pragma once

#include <usdrt/gf/math.h>
#include <usdrt/gf/matrix.h>
#include <usdrt/gf/range.h>

#include <iosfwd>

namespace usdrt
{

/// \class GfBBox3d
/// Basic type: arbitrarily oriented 3D bounding box.
///
/// This class represents a three-dimensional bounding box as an
/// axis-aligned box (\c usdrt::usdrt::GfRange3d) and a matrix (\c usdrt::GfMatrix4d) to
/// transform it into the correct space.
///
/// A \c GfBBox3d is more useful than using just \c usdrt::GfRange3d instances
/// (which are always axis-aligned) for these reasons:
///
/// \li When an axis-aligned bounding box is transformed several times,
/// each transformation can result in inordinate growth of the bounding
/// box. By storing the transformation separately, it can be applied once
/// at the end, resulting in a much better fit.  For example, if the
/// bounding box at the leaf of a scene graph is transformed through
/// several levels of the graph hierarchy to the coordinate space at the
/// root, a \c GfBBox3d is generally much smaller than the \c usdrt::GfRange3d
/// computed by transforming the box at each level.
///
/// \li When two or more such bounding boxes are combined, having the
/// transformations stored separately means that there is a better
/// opportunity to choose a better coordinate space in which to combine
/// the boxes.
///
/// \anchor bbox3d_zeroAreaFlag
/// <b> The Zero-area Primitives Flag </b>
///
/// When bounding boxes are used in intersection test culling, it is
/// sometimes useful to extend them a little bit to allow
/// lower-dimensional objects with zero area, such as lines and points,
/// to be intersected. For example, consider a cube constructed of line
/// segments. The bounding box for this shape fits the cube exactly. If
/// an application wants to allow a near-miss of the silhouette edges of
/// the cube to be considered an intersection, it has to loosen the bbox
/// culling test a little bit.
///
/// To distinguish when this loosening is necessary, each \c GfBBox3d
/// instance maintains a flag indicating whether any zero-area primitives
/// are contained within it. The application is responsible for setting
/// this flag correctly by calling \c SetHasZeroAreaPrimitives(). The
/// flag can be accessed during intersection tests by calling \c
/// HasZeroAreaPrimitives(). This flag is set by default in all
/// constructors to \c false.
///
class GfBBox3d
{

public:
    /// The default constructor leaves the box empty, the transformation
    /// matrix identity, and the \ref bbox3d_zeroAreaFlag "zero-area
    /// primitives flag" \c false.
    GfBBox3d()
    {
        _matrix.SetIdentity();
        _inverse.SetIdentity();
        _isDegenerate = false;
        _hasZeroAreaPrimitives = false;
    }

    /// Copy constructor
    GfBBox3d(const GfBBox3d& rhs) : _box(rhs._box)
    {
        _matrix = rhs._matrix;
        _inverse = rhs._inverse;
        _isDegenerate = rhs._isDegenerate;
        _hasZeroAreaPrimitives = rhs._hasZeroAreaPrimitives;
    }

    /// This constructor takes a box and sets the matrix to identity.
    GfBBox3d(const usdrt::GfRange3d& box) : _box(box)
    {
        _matrix.SetIdentity();
        _inverse.SetIdentity();
        _isDegenerate = false;
        _hasZeroAreaPrimitives = false;
    }

    /// This constructor takes a box and a transformation matrix.
    GfBBox3d(const usdrt::GfRange3d& box, const usdrt::GfMatrix4d& matrix)
    {
        Set(box, matrix);
        _hasZeroAreaPrimitives = false;
    }

    /// Sets the axis-aligned box and transformation matrix.
    void Set(const usdrt::GfRange3d& box, const usdrt::GfMatrix4d& matrix)
    {
        _box = box;
        _SetMatrices(matrix);
    }

    /// Sets the transformation matrix only.  The axis-aligned box is not
    /// modified.
    void SetMatrix(const usdrt::GfMatrix4d& matrix)
    {
        _SetMatrices(matrix);
    }

    /// Sets the range of the axis-aligned box only.  The transformation
    /// matrix is not modified.
    void SetRange(const usdrt::GfRange3d& box)
    {
        _box = box;
    }

    /// Returns the range of the axis-aligned untransformed box.
    const usdrt::GfRange3d& GetRange() const
    {
        return _box;
    }

    /// Returns the range of the axis-aligned untransformed box.
    /// This synonym of \c GetRange exists for compatibility purposes.
    const usdrt::GfRange3d& GetBox() const
    {
        return GetRange();
    }

    /// Returns the transformation matrix.
    const usdrt::GfMatrix4d& GetMatrix() const
    {
        return _matrix;
    }

    /// Returns the inverse of the transformation matrix. This will be the
    /// identity matrix if the transformation matrix is not invertible.
    const usdrt::GfMatrix4d& GetInverseMatrix() const
    {
        return _inverse;
    }

    /// Sets the \ref bbox3d_zeroAreaFlag "zero-area primitives flag" to the
    /// given value.
    void SetHasZeroAreaPrimitives(bool hasThem)
    {
        _hasZeroAreaPrimitives = hasThem;
    }

    /// Returns the current state of the \ref bbox3d_zeroAreaFlag "zero-area
    /// primitives flag".
    bool HasZeroAreaPrimitives() const
    {
        return _hasZeroAreaPrimitives;
    }

    /// Returns the volume of the box (0 for an empty box).

    double GetVolume() const;

    /// Transforms the bounding box by the given matrix, which is assumed to
    /// be a global transformation to apply to the box. Therefore, this just
    /// post-multiplies the box's matrix by \p matrix.
    void Transform(const usdrt::GfMatrix4d& matrix)
    {
        _SetMatrices(_matrix * matrix);
    }

    /// Returns the axis-aligned range (as a \c usdrt::GfRange3d) that results from
    /// applying the transformation matrix to the wxis-aligned box and
    /// aligning the result.

    usdrt::GfRange3d ComputeAlignedRange() const;

    /// Returns the axis-aligned range (as a \c usdrt::GfRange3d) that results from
    /// applying the transformation matrix to the axis-aligned box and
    /// aligning the result. This synonym for \c ComputeAlignedRange exists
    /// for compatibility purposes.
    usdrt::GfRange3d ComputeAlignedBox() const
    {
        return ComputeAlignedRange();
    }

    /// Combines two bboxes, returning a new bbox that contains both.  This
    /// uses the coordinate space of one of the two original boxes as the
    /// space of the result; it uses the one that produces whe smaller of the
    /// two resulting boxes.

    static GfBBox3d Combine(const GfBBox3d& b1, const GfBBox3d& b2);

    /// Returns the centroid of the bounding box.
    /// The centroid is computed as the transformed centroid of the range.

    usdrt::GfVec3d ComputeCentroid() const;

    // NOTE: To avoid including Boost unless absolutely necessary, hash_value() is not defined here.

    /// Component-wise equality test. The axis-aligned boxes and
    /// transformation matrices match exactly for bboxes to be considered
    /// equal. (To compare equality of the actual boxes, you can compute both
    /// aligned boxes and test the results for equality.)
    bool operator==(const GfBBox3d& b) const
    {
        return (_box == b._box && _matrix == b._matrix);
    }

    /// Component-wise inequality test. The axis-aligned boxes and
    /// transformation matrices match exactly for bboxes to be considered
    /// equal. (To compare equality of the actual boxes, you can compute both
    /// aligned boxes and test the results for equality.)
    bool operator!=(const GfBBox3d& that) const
    {
        return !(*this == that);
    }

private:
    /// The axis-aligned box.
    usdrt::GfRange3d _box;
    /// Transformation matrix.
    usdrt::GfMatrix4d _matrix;
    /// Inverse of the transformation matrix.
    usdrt::GfMatrix4d _inverse;
    /// Flag indicating whether the matrix is degenerate.
    bool _isDegenerate;
    /// Flag indicating whether the bbox contains zero-area primitives.
    bool _hasZeroAreaPrimitives;

    /// Sets the transformation matrix and the inverse, checking for
    /// degeneracies.

    void _SetMatrices(const usdrt::GfMatrix4d& matrix);

    /// This is used by \c Combine() when it is determined which coordinate
    /// space to use to combine two boxes: \p b2 is transformed into the space
    /// of \p b1 and the results are merged in that space.
    static GfBBox3d _CombineInOrder(const GfBBox3d& b1, const GfBBox3d& b2);
};

inline void GfBBox3d::_SetMatrices(const usdrt::GfMatrix4d& matrix)
{
    const double PRECISION_LIMIT = 1.0e-13;
    double det;

    _isDegenerate = false;
    _matrix = matrix;
    _inverse = matrix.GetInverse(&det, PRECISION_LIMIT);

    // Check for degenerate matrix:
    if (GfAbs(det) <= PRECISION_LIMIT)
    {
        _isDegenerate = true;
        _inverse.SetIdentity();
    }
}

inline double GfBBox3d::GetVolume() const
{
    if (_box.IsEmpty())
        return 0.0;

    // The volume of a transformed box is just its untransformed
    // volume times the determinant of the upper-left 3x3 of the xform
    // matrix. Pretty cool, indeed.
    usdrt::GfVec3d size = _box.GetSize();
    return fabs(_matrix.GetDeterminant3() * size[0] * size[1] * size[2]);
}

inline usdrt::GfRange3d GfBBox3d::ComputeAlignedRange() const
{
    if (_box.IsEmpty())
        return _box;

    // Method: James Arvo, Graphics Gems I, pp 548-550

    // Translate the origin and use the result as the min and max.
    usdrt::GfVec3d trans(_matrix[3][0], _matrix[3][1], _matrix[3][2]);
    usdrt::GfVec3d alignedMin = trans;
    usdrt::GfVec3d alignedMax = trans;

    const usdrt::GfVec3d& min = _box.GetMin();
    const usdrt::GfVec3d& max = _box.GetMax();

    for (int j = 0; j < 3; j++)
    {
        for (int i = 0; i < 3; i++)
        {
            double a = min[i] * _matrix[i][j];
            double b = max[i] * _matrix[i][j];
            if (a < b)
            {
                alignedMin[j] += a;
                alignedMax[j] += b;
            }
            else
            {
                alignedMin[j] += b;
                alignedMax[j] += a;
            }
        }
    }

    return usdrt::GfRange3d(alignedMin, alignedMax);
}

inline GfBBox3d GfBBox3d::Combine(const GfBBox3d& b1, const GfBBox3d& b2)
{
    GfBBox3d result;

    // If either box is empty, use the other as is
    if (b1.GetRange().IsEmpty())
        result = b2;
    else if (b2.GetRange().IsEmpty())
        result = b1;

    // If both boxes are degenerate, combine their projected
    // boxes. Otherwise, transform the degenerate box into the space
    // of the other box and combine the results in that space.
    else if (b1._isDegenerate)
    {
        if (b2._isDegenerate)
            result = GfBBox3d(usdrt::GfRange3d::GetUnion(b1.ComputeAlignedRange(), b2.ComputeAlignedRange()));
        else
            result = _CombineInOrder(b2, b1);
    }
    else if (b2._isDegenerate)
        result = _CombineInOrder(b1, b2);

    // Non-degenerate case: Neither box is empty and they are in
    // different spaces. To get the best results, we'll perform the
    // merge of the two boxes in each of the two spaces. Whichever
    // merge ends up being smaller (by volume) is the one we'll use.
    // Note that we don't use ComputeAlignedRange() as part of the test.
    // This is because projecting almost always adds a little extra
    // space and it gives an unfair advantage to the box that is more
    // closely aligned to the coordinate axes.
    else
    {
        GfBBox3d result1 = _CombineInOrder(b1, b2);
        GfBBox3d result2 = _CombineInOrder(b2, b1);

        // Test within a tolerance (based on volume) to make this
        // reasonably deterministic.
        double v1 = result1.GetVolume();
        double v2 = result2.GetVolume();
        double tolerance = GfMax(1e-10, 1e-6 * GfAbs(GfMax(v1, v2)));

        result = (GfAbs(v1 - v2) <= tolerance ? result1 : (v1 < v2 ? result1 : result2));
    }

    // The _hasZeroAreaPrimitives is set to true if either of the
    // input boxes has it set to true.
    result.SetHasZeroAreaPrimitives(b1.HasZeroAreaPrimitives() || b2.HasZeroAreaPrimitives());

    return result;
}

inline GfBBox3d GfBBox3d::_CombineInOrder(const GfBBox3d& b1, const GfBBox3d& b2)
{
    // Transform b2 into b1's space to get b2t
    GfBBox3d b2t;
    b2t._box = b2._box;
    b2t._matrix = b2._matrix * b1._inverse;
    b2t._inverse = b1._matrix * b2._inverse;

    // Compute the projection of this box into b1's space.
    usdrt::GfRange3d proj = b2t.ComputeAlignedRange();

    // Extend b1 by this box to get the result.
    GfBBox3d result = b1;
    result._box.UnionWith(proj);
    return result;
}

inline usdrt::GfVec3d GfBBox3d::ComputeCentroid() const
{
    usdrt::GfVec3d a = GetRange().GetMax();
    usdrt::GfVec3d b = GetRange().GetMin();

    return GetMatrix().Transform(usdrt::GfVec3d(.5 * (a + b)));
}

} // usdrt namespace close
