// Copyright (c) 2021-2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
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
// Note: This source derived from transform.h and transform.cpp in USD and modified for this application.
#pragma once

#include <usdrt/gf/matrix.h>
#include <usdrt/gf/rotation.h>
#include <usdrt/gf/vec.h>

namespace usdrt
{
/// Basic type: Compound linear transformation.
///
/// This class represents a linear transformation specified as a series of
/// individual components: a \em translation, a \em rotation, a \em scale, a
/// \em pivotPosition, and a \em pivotOrientation.  When applied to a point,
/// the point will be transformed as follows (in order):
///
/// \li Scaled by the \em scale with respect to \em pivotPosition and the
/// orientation specified by the \em pivotOrientation.
/// \li Rotated by the \em rotation about \em pivotPosition.
/// \li Translated by \em Translation
///
/// That is, the cumulative matrix that this represents looks like this.
///
/// \code
/// M = -P * -O * S * O * R * P * T
/// \endcode
///
/// where
/// \li \em T is the \em translation matrix
/// \li \em P is the matrix that translates by \em pivotPosition
/// \li \em R is the \em rotation matrix
/// \li \em O is the matrix that rotates to \em pivotOrientation
/// \li \em S is the \em scale matrix
///
class GfTransform
{

public:
    /// The default constructor sets the component values to the
    /// identity transformation.
    GfTransform()
    {
        SetIdentity();
    }

    /// This constructor initializes the transformation from all
    /// component values.
    /// Nv note: pixar module includes a depricated Set function with the a different argument order. Omitting.
    GfTransform(const usdrt::GfVec3d& translation,
                const usdrt::GfRotation& rotation,
                const usdrt::GfVec3d& scale,
                const usdrt::GfVec3d& pivotPosition,
                const usdrt::GfRotation& pivotOrientation)
    {
        Set(translation, rotation, scale, pivotPosition, pivotOrientation);
    }

    /// This constructor initializes the transformation with a matrix.  See
    /// SetMatrix() for more information.
    GfTransform(const usdrt::GfMatrix4d& m)
    {
        SetIdentity();
        SetMatrix(m);
    }

    /// Sets the transformation from all component values.
    usdrt::GfTransform& Set(const usdrt::GfVec3d& translation,
                            const usdrt::GfRotation& rotation,
                            const usdrt::GfVec3d& scale,
                            const usdrt::GfVec3d& pivotPosition,
                            const usdrt::GfRotation& pivotOrientation);

    /// Sets the transform components to implement the transformation
    /// represented by matrix \p m , ignoring any projection. This tries to
    /// leave the current center unchanged.
    usdrt::GfTransform& SetMatrix(const usdrt::GfMatrix4d& m);

    /// Sets the transformation to the identity transformation.
    usdrt::GfTransform& SetIdentity();

    /// Sets the scale component, leaving all others untouched.
    void SetScale(const usdrt::GfVec3d& scale)
    {
        _scale = scale;
    }

    /// Sets the pivot orientation component, leaving all others untouched.
    void SetPivotOrientation(const usdrt::GfRotation& pivotOrient)
    {
        _pivotOrientation = pivotOrient;
    }

    /// Sets the pivot orientation component, leaving all others untouched.
    void SetScaleOrientation(const usdrt::GfRotation& pivotOrient)
    {
        SetPivotOrientation(pivotOrient);
    }

    /// Sets the rotation component, leaving all others untouched.
    void SetRotation(const usdrt::GfRotation& rotation)
    {
        _rotation = rotation;
    }

    /// Sets the pivot position component, leaving all others untouched.
    void SetPivotPosition(const usdrt::GfVec3d& pivPos)
    {
        _pivotPosition = pivPos;
    }

    /// Sets the pivot position component, leaving all others untouched.
    void SetCenter(const usdrt::GfVec3d& pivPos)
    {
        SetPivotPosition(pivPos);
    }

    /// Sets the translation component, leaving all others untouched.
    void SetTranslation(const usdrt::GfVec3d& translation)
    {
        _translation = translation;
    }

    /// Returns the scale component.
    const usdrt::GfVec3d& GetScale() const
    {
        return _scale;
    }

    /// Returns the pivot orientation component.
    const usdrt::GfRotation& GetPivotOrientation() const
    {
        return _pivotOrientation;
    }

    /// Returns the scale orientation component.
    const usdrt::GfRotation& GetScaleOrientation() const
    {
        return GetPivotOrientation();
    }

    /// Returns the rotation component.
    const usdrt::GfRotation& GetRotation() const
    {
        return _rotation;
    }

    /// Returns the pivot position component.
    const usdrt::GfVec3d& GetPivotPosition() const
    {
        return _pivotPosition;
    }

    /// Returns the pivot position component.
    const usdrt::GfVec3d& GetCenter() const
    {
        return GetPivotPosition();
    }

    /// Returns the translation component.
    const usdrt::GfVec3d& GetTranslation() const
    {
        return _translation;
    }

    /// Returns a \c GfMatrix4d that implements the cumulative transformation.
    usdrt::GfMatrix4d GetMatrix() const;

    /// Component-wise transform equality test. All components must match
    /// exactly for transforms to be considered equal.
    bool operator==(const usdrt::GfTransform& xf) const;

    /// Component-wise transform inequality test. All components must match
    /// exactly for transforms to be considered equal.
    bool operator!=(const usdrt::GfTransform& xf) const
    {
        return !(*this == xf);
    }

    /// Post-multiplies transform \p xf into this transform.
    usdrt::GfTransform& operator*=(const usdrt::GfTransform& xf);

    /// Returns the product of transforms \p xf1 and \p xf2.
    friend usdrt::GfTransform operator*(const usdrt::GfTransform& xf1, const usdrt::GfTransform& xf2)
    {
        usdrt::GfTransform xf = xf1;
        return xf *= xf2;
    }

private:
    /// translation
    usdrt::GfVec3d _translation;
    /// rotation
    usdrt::GfRotation _rotation;
    /// scale factors
    usdrt::GfVec3d _scale;
    /// orientation used for scaling and rotation
    usdrt::GfRotation _pivotOrientation;
    /// center of rotation and scaling
    usdrt::GfVec3d _pivotPosition;
};

inline usdrt::GfTransform& GfTransform::Set(const usdrt::GfVec3d& translation,
                                            const usdrt::GfRotation& rotation,
                                            const usdrt::GfVec3d& scale,
                                            const usdrt::GfVec3d& pivotPosition,
                                            const usdrt::GfRotation& pivotOrientation)
{
    _scale = scale;
    _pivotOrientation = pivotOrientation;
    _rotation = rotation;
    _pivotPosition = pivotPosition;
    _translation = translation;

    return *this;
}

inline usdrt::GfTransform& GfTransform::SetMatrix(const usdrt::GfMatrix4d& m)
{

    // Factor the matrix into the components, while trying to leave
    // the pivotPosition field unchanged.

    // Create a matrix, [mNoPivot], given by:
    //          [pivotPositionInverse][mNoPivot][pivotPosition] = [m]
    //
    // So, [mNoPivot] = [pivotPosition][m][pivotPositionInverse]
    usdrt::GfMatrix4d mPivotPos, mPivotPosInv;
    mPivotPos.SetTranslate(_pivotPosition);
    mPivotPosInv.SetTranslate(-_pivotPosition);
    usdrt::GfMatrix4d mNoPivot = mPivotPos * m * mPivotPosInv;

    // Factor mNoPivot into the other components
    usdrt::GfMatrix4d shearRotMat, rotMat, projMat;

    // Factor returns false if the given matrix is singular,
    // but produces a result anyway.  We use that result regardless,
    // because singular matrices (such as zero scales) are still
    // valid for constructing Transforms.
    mNoPivot.Factor(&shearRotMat, &_scale, &rotMat, &_translation, &projMat);

    _rotation = rotMat.ExtractRotation();

    // Don't set the scale orientation if the scale is unity
    if (_scale != usdrt::GfVec3d(1.0, 1.0, 1.0))
        _pivotOrientation = shearRotMat.GetTranspose().ExtractRotation();
    else
        _pivotOrientation.SetIdentity();

    return *this;
}

inline usdrt::GfTransform& GfTransform::SetIdentity()
{
    _scale.Set(1.0, 1.0, 1.0);
    _pivotOrientation.SetIdentity();
    _rotation.SetIdentity();
    _pivotPosition = usdrt::GfVec3d(0);
    _translation = usdrt::GfVec3d(0);

    return *this;
}

inline usdrt::GfMatrix4d GfTransform::GetMatrix() const
{
    bool doPivot = (_pivotPosition != usdrt::GfVec3d(0));
    bool doScale = (_scale != usdrt::GfVec3d(1.0, 1.0, 1.0));
    bool doScaleOrient = (_pivotOrientation.GetAngle() != 0.0);
    bool doRotation = (_rotation.GetAngle() != 0.0);
    bool doTranslation = (_translation != usdrt::GfVec3d(0));
    bool anySet = false;
    usdrt::GfMatrix4d mtx;

    //
    // When multiplying matrices A*B, the effects of A are more local
    // than the effects of B (A's operation takes place before
    // B's). So we use post-multiplication of matrices (with the '*='
    // operator), in the order we want the operations to be applied.
    //

#define _GF_ACCUM(mtxOp)                                                                                               \
    {                                                                                                                  \
        if (anySet)                                                                                                    \
        {                                                                                                              \
            usdrt::GfMatrix4d tmp;                                                                                     \
            tmp.mtxOp;                                                                                                 \
            mtx *= tmp;                                                                                                \
        }                                                                                                              \
        else                                                                                                           \
        {                                                                                                              \
            mtx.mtxOp;                                                                                                 \
            anySet = true;                                                                                             \
        }                                                                                                              \
    }

    if (doPivot)
        _GF_ACCUM(SetTranslate(-_pivotPosition));

    if (doScale)
    {
        if (doScaleOrient)
            _GF_ACCUM(SetRotate(_pivotOrientation.GetInverse()));

        _GF_ACCUM(SetScale(_scale));

        if (doScaleOrient)
            _GF_ACCUM(SetRotate(_pivotOrientation));
    }

    if (doRotation)
        _GF_ACCUM(SetRotate(_rotation));

    if (doPivot)
        _GF_ACCUM(SetTranslate(_pivotPosition));

    if (doTranslation)
        _GF_ACCUM(SetTranslate(_translation));

#undef _GF_ACCUM

    if (!anySet)
        mtx.SetIdentity();

    return mtx;
}

inline bool GfTransform::operator==(const usdrt::GfTransform& xf) const
{
    return (GetScale() == xf.GetScale() && GetPivotOrientation() == xf.GetPivotOrientation() &&
            GetRotation() == xf.GetRotation() && GetPivotPosition() == xf.GetPivotPosition() &&
            GetTranslation() == xf.GetTranslation());
}

inline usdrt::GfTransform& GfTransform::operator*=(const usdrt::GfTransform& xf)
{
    return SetMatrix(GetMatrix() * xf.GetMatrix());
}

} // namespace usdrt
