// Copyright (c) 2021-2023, NVIDIA CORPORATION. All rights reserved.
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
// Note: This source derived from rotation.h and rotation.cpp in USD and modified for this application.
#pragma once

#include <carb/Defines.h>

#include <usdrt/gf/math.h>
#include <usdrt/gf/matrix.h>
#include <usdrt/gf/quat.h>
#include <usdrt/gf/vec.h>

#include <float.h>

namespace usdrt
{
/// \class GfRotation
///
/// Basic type: 3-space rotation specification.
///
/// This class represents a rotation in 3-space. This stores an axis as a
/// normalized vector of 3 \c doubles and an angle in degrees (as a double).
/// Rotations follow the right-hand rule: a positive rotation about an axis
/// vector appears counter-clockwise when looking from the end of the vector
/// toward the origin.
///
class GfRotation
{

public:
    /// The default constructor leaves the rotation undefined.
    GfRotation() = default;
    GfRotation(const GfRotation&) = default;

    /// This constructor initializes the rotation to be \p angle
    /// degrees about \p axis.
    GfRotation(const usdrt::GfVec3d& axis, double angle)
    {
        SetAxisAngle(axis, angle);
    }

    /// This constructor initializes the rotation from a quaternion.  Note that
    /// this constructor accepts GfQuatf and GfQuath since they implicitly
    /// convert to GfQuatd.
    GfRotation(const usdrt::GfQuatd& quat)
    {
        SetQuat(quat);
    }

    /// This constructor initializes the rotation to one that brings
    /// the \p rotateFrom vector to align with \p rotateTo. The passed
    /// vectors need not be unit length.
    GfRotation(const usdrt::GfVec3d& rotateFrom, const usdrt::GfVec3d& rotateTo)
    {
        SetRotateInto(rotateFrom, rotateTo);
    }

    /// Sets the rotation to be \p angle degrees about \p axis.
    usdrt::GfRotation& SetAxisAngle(const usdrt::GfVec3d& axis, double angle)
    {
        _axis = axis;
        _angle = angle;
        if (!GfIsClose(_axis * _axis, 1.0, 1e-10))
            _axis.Normalize();
        return *this;
    }

    /// Sets the rotation from a quaternion.  Note that this method accepts
    /// GfQuatf and GfQuath since they implicitly convert to GfQuatd.
    usdrt::GfRotation& SetQuat(const usdrt::GfQuatd& quat);

    /// Sets the rotation to one that brings the \p rotateFrom vector
    /// to align with \p rotateTo. The passed vectors need not be unit
    /// length.
    usdrt::GfRotation& SetRotateInto(const usdrt::GfVec3d& rotateFrom, const usdrt::GfVec3d& rotateTo);

    /// Sets the rotation to an identity rotation.
    /// (This is chosen to be 0 degrees around the positive X axis.)
    usdrt::GfRotation& SetIdentity()
    {
        _axis.Set(1.0, 0.0, 0.0);
        _angle = 0.0;
        return *this;
    }

    /// Returns the axis of rotation.
    const usdrt::GfVec3d& GetAxis() const
    {
        return _axis;
    }

    /// Returns the rotation angle in degrees.
    double GetAngle() const
    {
        return _angle;
    }

    /// Returns the rotation expressed as a quaternion.
    usdrt::GfQuatd GetQuat() const;

    /// Returns the inverse of this rotation.
    usdrt::GfRotation GetInverse() const
    {
        return usdrt::GfRotation(_axis, -_angle);
    }

    /// Decompose rotation about 3 orthogonal axes.
    /// If the axes are not orthogonal, warnings will be spewed.
    usdrt::GfVec3d Decompose(const usdrt::GfVec3d& axis0, const usdrt::GfVec3d& axis1, const usdrt::GfVec3d& axis2) const;

    // Full-featured method to  Decompose a rotation matrix into Cardarian
    // angles.
    // Axes have must be normalized. If useHint is specified
    // then the current values stored within thetaTw, thetaFB, thetaLR,
    // and thetaSw will be treated as hint and  used to help choose
    // an equivalent rotation that is as close as possible to the hints.
    //
    // One can use this routine to generate any combination of the three
    // angles by passing in NULL for the angle that is to be omitted.
    //
    // Passing in valid pointers for all four angles will decompose into
    // Tw, FB, and LR but allows Sw to be used for best matching of hint
    // values.  It also allows an swShift value to be passed in as a
    // Sw that is applied after the rotation matrix to get a best fit rotation
    // in four angles.
    //
    // Angles are in radians.
    //
    // Specify \p handedness as -1.0 or 1.0, same as for MultiRotate.
    static void DecomposeRotation(const usdrt::GfMatrix4d& rot,
                                  const usdrt::GfVec3d& TwAxis,
                                  const usdrt::GfVec3d& FBAxis,
                                  const usdrt::GfVec3d& LRAxis,
                                  double handedness,
                                  double* thetaTw,
                                  double* thetaFB,
                                  double* thetaLR,
                                  double* thetaSw = NULL,
                                  bool useHint = false,
                                  const double* swShift = NULL);

    // This function projects the vectors \p v1 and \p v2 onto the plane
    // normal to \p axis, and then returns the rotation about \p axis that
    // brings \p v1 onto \p v2.
    static usdrt::GfRotation RotateOntoProjected(const usdrt::GfVec3d& v1,
                                                 const usdrt::GfVec3d& v2,
                                                 const usdrt::GfVec3d& axis);

    /// Transforms row vector \p vec by the rotation, returning the result.
    usdrt::GfVec3f TransformDir(const usdrt::GfVec3f& vec) const;

    /// \overload
    usdrt::GfVec3d TransformDir(const usdrt::GfVec3d& vec) const;

    // NOTE: To avoid including Boost unless absolutely necessary, hash_value() is not defined here.

    /// Component-wise rotation equality test. The axes and angles must match
    /// exactly for rotations to be considered equal. (To compare equality of
    /// the actual rotations, you can convert both to quaternions and test the
    /// results for equality.)
    bool operator==(const usdrt::GfRotation& r) const
    {
        return (_axis == r._axis && _angle == r._angle);
    }

    /// Component-wise rotation inequality test. The axes and angles must
    /// match exactly for rotations to be considered equal. (To compare
    /// equality of the actual rotations, you can convert both to quaternions
    /// and test the results for equality.)
    bool operator!=(const usdrt::GfRotation& r) const
    {
        return !(*this == r);
    }

    /// Post-multiplies rotation \p r into this rotation.
    usdrt::GfRotation& operator*=(const usdrt::GfRotation& r);

    /// Scales rotation angle by multiplying by \p scale.
    usdrt::GfRotation& operator*=(double scale)
    {
        _angle *= scale;
        return *this;
    }

    /// Scales rotation angle by dividing by \p scale.
    usdrt::GfRotation& operator/=(double scale)
    {
        _angle /= scale;
        return *this;
    }

    /// Returns composite rotation of rotations \p r1 and \p r2.
    friend usdrt::GfRotation operator*(const usdrt::GfRotation& r1, const usdrt::GfRotation& r2)
    {
        usdrt::GfRotation r = r1;
        return r *= r2;
    }

    /// Returns a rotation equivalent to \p r with its angle multiplied
    /// by \p scale.
    friend usdrt::GfRotation operator*(const usdrt::GfRotation& r, double scale)
    {
        usdrt::GfRotation rTmp = r;
        return rTmp *= scale;
    }

    /// Returns a rotation equivalent to \p r with its angle multiplied
    /// by \p scale.
    friend GfRotation operator*(double scale, const usdrt::GfRotation& r)
    {
        return (r * scale);
    }

    /// Returns a rotation equivalent to \p r with its angle divided
    /// by \p scale.
    friend usdrt::GfRotation operator/(const usdrt::GfRotation& r, double scale)
    {
        usdrt::GfRotation rTmp = r;
        return rTmp /= scale;
    }

private:
    /// Axis storage.
    /// This axis is normalized to unit length whenever it is set.
    usdrt::GfVec3d _axis;
    /// Angle storage (represented in degrees).
    double _angle;
};

inline usdrt::GfRotation& GfRotation::SetQuat(const usdrt::GfQuatd& quat)
{
    /// This constant is used to determine whether the length of a vector is too
    /// small to handle accurately.
    const double GfMinVectorLength = 1e-10;

    double len = quat.GetImaginary().GetLength();
    if (len > GfMinVectorLength)
    {
        double x = acos(GfClamp(quat.GetReal(), -1.0, 1.0));
        SetAxisAngle(quat.GetImaginary() / len, 2.0 * GfRadiansToDegrees(x));
    }
    else
        SetIdentity();

    return *this;
}

inline usdrt::GfRotation& GfRotation::SetRotateInto(const usdrt::GfVec3d& rotateFrom, const usdrt::GfVec3d& rotateTo)
{
    usdrt::GfVec3d from = rotateFrom.GetNormalized();
    usdrt::GfVec3d to = rotateTo.GetNormalized();

    double cos = GfDot(from, to);

    if (cos > 0.9999999)
        return SetIdentity();

    if (cos < -0.9999999)
    {
        usdrt::GfVec3d tmp = GfCross(from, usdrt::GfVec3d(1.0, 0.0, 0.0));
        if (tmp.GetLength() < 0.00001)
            tmp = GfCross(from, usdrt::GfVec3d(0.0, 1.0, 0.0));
        return SetAxisAngle(tmp.GetNormalized(), 180.0);
    }

    usdrt::GfVec3d axis = GfCross(rotateFrom, rotateTo).GetNormalized();
    return SetAxisAngle(axis, GfRadiansToDegrees(acos(cos)));
}

inline usdrt::GfQuatd GfRotation::GetQuat() const
{
    double radians = GfDegreesToRadians(_angle) / 2.0;
    double sinR, cosR;
    GfSinCos(radians, &sinR, &cosR);
    usdrt::GfVec3d axis = _axis * sinR;
    return usdrt::GfQuatd(cosR, axis).GetNormalized();
}

inline usdrt::GfVec3d GfRotation::Decompose(const usdrt::GfVec3d& axis0,
                                            const usdrt::GfVec3d& axis1,
                                            const usdrt::GfVec3d& axis2) const
{
    /// This constant is used to determine when a set of basis vectors is close to
    /// orthogonal.
    const double GfMinOrthoTolerance = 1e-6;

    usdrt::GfMatrix4d mat;
    mat.SetRotate(*this);

    usdrt::GfVec3d nAxis0 = axis0.GetNormalized();
    usdrt::GfVec3d nAxis1 = axis1.GetNormalized();
    usdrt::GfVec3d nAxis2 = axis2.GetNormalized();

    if (!(GfIsClose(GfDot(nAxis0, nAxis1), 0, GfMinOrthoTolerance) &&
          GfIsClose(GfDot(nAxis0, nAxis2), 0, GfMinOrthoTolerance) &&
          GfIsClose(GfDot(nAxis1, nAxis2), 0, GfMinOrthoTolerance)))
    {
        // WARN
    }

    usdrt::GfMatrix4d axes(nAxis0[0], nAxis1[0], nAxis2[0], 0, nAxis0[1], nAxis1[1], nAxis2[1], 0, nAxis0[2], nAxis1[2],
                           nAxis2[2], 0, 0, 0, 0, 1);

    usdrt::GfMatrix4d m = axes.GetTranspose() * mat * axes;

    int i = 0, j = 1, k = 2;
    double r0, r1, r2;
    double cy = sqrt(m[i][i] * m[i][i] + m[j][i] * m[j][i]);
    if (cy > 1e-6)
    {
        r0 = atan2(m[k][j], m[k][k]);
        r1 = atan2(-m[k][i], cy);
        r2 = atan2(m[j][i], m[i][i]);
    }
    else
    {
        r0 = atan2(-m[j][k], m[j][j]);
        r1 = atan2(-m[k][i], cy);
        r2 = 0;
    }

    usdrt::GfVec3d axisCross = GfCross(nAxis0, nAxis1);
    double axisHand = GfDot(axisCross, nAxis2);
    if (axisHand >= 0.0)
    {
        r0 = -r0;
        r1 = -r1;
        r2 = -r2;
    }

    return usdrt::GfVec3d(GfRadiansToDegrees(r0), GfRadiansToDegrees(r1), GfRadiansToDegrees(r2));
}

inline usdrt::GfRotation GfRotation::RotateOntoProjected(const usdrt::GfVec3d& v1,
                                                         const usdrt::GfVec3d& v2,
                                                         const usdrt::GfVec3d& axisParam)
{
    usdrt::GfVec3d axis = axisParam.GetNormalized();

    usdrt::GfVec3d v1Proj = v1 - GfDot(v1, axis) * axis;
    usdrt::GfVec3d v2Proj = v2 - GfDot(v2, axis) * axis;
    v1Proj.Normalize();
    v2Proj.Normalize();
    usdrt::GfVec3d crossAxis = GfCross(v1Proj, v2Proj);
    double sinTheta = GfDot(crossAxis, axis);
    double cosTheta = GfDot(v1Proj, v2Proj);
    double theta = 0;
    if (!(fabs(sinTheta) < 1e-6 && fabs(cosTheta) < 1e-6))
        theta = atan2(sinTheta, cosTheta);

    const double toDeg = (180.0) / M_PI;
    return usdrt::GfRotation(axis, theta * toDeg);
}

inline usdrt::GfMatrix4d _RotateOntoProjected(const usdrt::GfVec3d& v1,
                                              const usdrt::GfVec3d& v2,
                                              const usdrt::GfVec3d& axisParam,
                                              double* thetaInRadians)
{
    usdrt::GfMatrix4d mat;
    usdrt::GfRotation r = usdrt::GfRotation::RotateOntoProjected(v1, v2, axisParam);
    mat.SetRotate(r);
    if (thetaInRadians)
    {
        const double toDeg = (180.0) / M_PI;
        *thetaInRadians = r.GetAngle() / toDeg;
    }

    return mat;
}

inline usdrt::GfVec4d _PiShift(const usdrt::GfVec4d& hint, const usdrt::GfVec4d& attempt, double mul = 2 * M_PI)
{
    usdrt::GfVec4d result(attempt);
    for (int i = 0; i < 4; i++)
    {
        double mod1 = fmod(attempt[i], mul);
        double mod2 = fmod(hint[i], mul);
        result[i] = (hint[i] - mod2) + mod1;
        if (fabs(hint[i] - result[i]) > mul / 2.0)
            result[i] += (hint[i] < 0 ? -mul : mul);
    }
    return result;
}

inline void _ShiftGimbalLock(double middleAngle, double* firstAngle, double* lastAngle)
{
    if (fabs(fabs(middleAngle) - M_PI) < 1e-6)
    {
        double diff = *lastAngle - *firstAngle;
        *lastAngle = diff / 2;
        *firstAngle = -diff / 2;
    }

    if (fabs(middleAngle) < 1e-6)
    {
        double sum = *lastAngle + *firstAngle;
        *lastAngle = sum / 2;
        *firstAngle = sum / 2;
    }
}

inline void GfRotation::DecomposeRotation(const usdrt::GfMatrix4d& rot,
                                          const usdrt::GfVec3d& TwAxis,
                                          const usdrt::GfVec3d& FBAxis,
                                          const usdrt::GfVec3d& LRAxis,
                                          double handedness,
                                          double* thetaTw,
                                          double* thetaFB,
                                          double* thetaLR,
                                          double* thetaSw,
                                          bool useHint,
                                          const double* swShift)
{
    enum _ZeroAngle
    {
        ZERO_NONE = 0,
        ZERO_TW,
        ZERO_FB,
        ZERO_LR,
        ZERO_SW
    };
    _ZeroAngle zeroAngle = ZERO_NONE;

    double angleStandin = 0.0f, hintTw = 0.0f, hintFB = 0.0f, hintLR = 0.0f, hintSw = 0.0f;
    if (thetaTw == NULL)
    {
        zeroAngle = ZERO_TW;
        thetaTw = &angleStandin;
    }
    if (thetaFB == NULL)
    {
        if (zeroAngle != ZERO_NONE)
        {
            return;
        }
        zeroAngle = ZERO_FB;
        thetaFB = &angleStandin;
    }
    if (thetaLR == NULL)
    {
        if (zeroAngle != ZERO_NONE)
        {
            return;
        }
        zeroAngle = ZERO_LR;
        thetaLR = &angleStandin;
    }
    if (thetaSw == NULL)
    {
        if (zeroAngle != ZERO_NONE)
        {
            return;
        }
        zeroAngle = ZERO_SW;
        thetaSw = &angleStandin;
    }

    if (swShift && zeroAngle != ZERO_NONE)
    {
        // WARN
    }

    if (useHint)
    {
        if (thetaTw)
            hintTw = *thetaTw;
        if (thetaFB)
            hintFB = *thetaFB;
        if (thetaLR)
            hintLR = *thetaLR;
        if (thetaSw)
            hintSw = *thetaSw;
    }

    usdrt::GfVec3d FBAxisR = rot.TransformDir(FBAxis);
    usdrt::GfVec3d TwAxisR = rot.TransformDir(TwAxis);
    usdrt::GfMatrix4d r(1);
    switch (zeroAngle)
    {
    case ZERO_SW:
    case ZERO_NONE:
        r = r * _RotateOntoProjected(r.TransformDir(TwAxisR), TwAxis, LRAxis, thetaLR);
        r = r * _RotateOntoProjected(r.TransformDir(TwAxisR), TwAxis, FBAxis, thetaFB);
        r = r * _RotateOntoProjected(r.TransformDir(FBAxisR), FBAxis, TwAxis, thetaTw);
        *thetaFB *= -handedness;
        *thetaLR *= -handedness;
        *thetaTw *= -handedness;

        *thetaSw = swShift ? *swShift : 0.0;
        break;

    case ZERO_TW:
        r = r * _RotateOntoProjected(r.TransformDir(FBAxisR), FBAxis, TwAxis, thetaSw);
        r = r * _RotateOntoProjected(r.TransformDir(FBAxisR), FBAxis, LRAxis, thetaLR);
        r = r * _RotateOntoProjected(r.TransformDir(TwAxisR), TwAxis, FBAxis, thetaFB);
        *thetaSw *= -handedness;
        *thetaFB *= -handedness;
        *thetaLR *= -handedness;
        break;

    case ZERO_FB:
        r = r * _RotateOntoProjected(r.TransformDir(TwAxisR), FBAxis, TwAxis, thetaSw);
        r = r * _RotateOntoProjected(r.TransformDir(TwAxisR), TwAxis, LRAxis, thetaLR);
        r = r * _RotateOntoProjected(r.TransformDir(FBAxisR), FBAxis, TwAxis, thetaTw);
        *thetaSw *= -handedness;
        *thetaLR *= -handedness;
        *thetaTw *= -handedness;
        break;

    case ZERO_LR:
        r = r * _RotateOntoProjected(r.TransformDir(TwAxisR), LRAxis, TwAxis, thetaSw);
        r = r * _RotateOntoProjected(r.TransformDir(TwAxisR), TwAxis, FBAxis, thetaFB);
        r = r * _RotateOntoProjected(r.TransformDir(FBAxisR), FBAxis, TwAxis, thetaTw);
        *thetaSw *= -handedness;
        *thetaFB *= -handedness;
        *thetaTw *= -handedness;
        break;
    };

    double thetaLRp = *thetaLR + ((*thetaLR > 0) ? -M_PI : M_PI);
    double thetaFBp = *thetaFB + ((*thetaFB > 0) ? -M_PI : M_PI);
    double thetaTwp = *thetaTw + ((*thetaTw > 0) ? -M_PI : M_PI);
    double thetaSwp = *thetaSw + ((*thetaSw > 0) ? -M_PI : M_PI);

    usdrt::GfVec4d vals[4];
    vals[0] = usdrt::GfVec4d(*thetaTw, *thetaFB, *thetaLR, *thetaSw);
    vals[1] = usdrt::GfVec4d(thetaTwp, -thetaFBp, thetaLRp, *thetaSw);
    vals[2] = usdrt::GfVec4d(thetaTwp, -(*thetaFB), -(*thetaLR), thetaSwp);
    vals[3] = usdrt::GfVec4d(*thetaTw, thetaFBp, -thetaLRp, thetaSwp);

    int numVals = zeroAngle == ZERO_NONE ? 4 : 2;
    switch (zeroAngle)
    {
    case ZERO_TW:
        vals[1] = vals[3];
        break;
    case ZERO_FB:
    case ZERO_LR:
        vals[1] = vals[2];
        break;
    default:
        break;
    };

    usdrt::GfVec4d hintAngles(hintTw, hintFB, hintLR, hintSw);

    if (useHint)
    {
        for (size_t i = 0; i < 4; i++)
        {
            vals[i] = _PiShift(hintAngles, vals[i]);
        }
    }

    double min = 0;
    int i, j, mini = -1;

    for (i = 0; i < numVals; i++)
    {
        double sum = 0;
        usdrt::GfVec4d hintDiff = vals[i] - hintAngles;
        for (j = 0; j < 4; j++)
            sum += fabs(hintDiff[j]);
        if ((i == 0) || (sum < min))
        {
            min = sum;
            mini = i;
        }
    }

    *thetaTw = vals[mini][0];
    *thetaFB = vals[mini][1];
    *thetaLR = vals[mini][2];
    *thetaSw = vals[mini][3];

    usdrt::GfMatrix3d basis;
    basis.SetRow(0, TwAxis);
    basis.SetRow(1, FBAxis);
    basis.SetRow(2, LRAxis);
    switch (zeroAngle)
    {
    case ZERO_NONE:
    case ZERO_SW:
        _ShiftGimbalLock(*thetaFB + M_PI / 2 * basis.GetHandedness(), thetaTw, thetaLR);
        break;
    case ZERO_TW:
        _ShiftGimbalLock(*thetaLR + M_PI / 2 * basis.GetHandedness(), thetaFB, thetaSw);
        break;
    case ZERO_FB:
        _ShiftGimbalLock(*thetaLR, thetaTw, thetaSw);
        break;
    case ZERO_LR:
        _ShiftGimbalLock(*thetaFB, thetaTw, thetaSw);
        break;
    };
}

inline usdrt::GfVec3f GfRotation::TransformDir(const usdrt::GfVec3f& vec) const
{
    return usdrt::GfMatrix4d().SetRotate(*this).TransformDir(vec);
}

inline usdrt::GfVec3d GfRotation::TransformDir(const usdrt::GfVec3d& vec) const
{
    return usdrt::GfMatrix4d().SetRotate(*this).TransformDir(vec);
}

inline usdrt::GfRotation& GfRotation::operator*=(const usdrt::GfRotation& r)
{
    /// This constant is used to determine whether the length of a vector is too
    /// small to handle accurately.
    const double GfMinVectorLength = 1e-10;

    usdrt::GfQuatd q = (r.GetQuat() * GetQuat()).GetNormalized();
    double len = q.GetImaginary().GetLength();
    if (len > GfMinVectorLength)
    {
        _axis = q.GetImaginary() / len;
        _angle = 2.0 * GfRadiansToDegrees(acos(q.GetReal()));
    }
    else
    {
        _angle = 0.0;
    }

    return *this;
}

} // namespace close
