// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

// CUDA-compatible struct with functions for working with a 4x4 double matrix

#include <float.h>

struct Matrix4d
{
    //! Default constructor. Leaves the matrix component values undefined.
    Matrix4d() = default;

    __device__ explicit Matrix4d(double s)
    {
        SetDiagonal(s);
    }

    __device__ Matrix4d& SetDiagonal(double s);
    __device__ Matrix4d& SetScale(double s);
    __device__ Matrix4d GetInverse() const;

    //! Post-multiplies matrix \e m into this matrix.
    __device__ Matrix4d& operator*=(const Matrix4d& m);

    //! Multiplies matrix \e m1 by \e m2.
    __device__ friend Matrix4d operator*(const Matrix4d& m1, const Matrix4d& m2)
    {
        Matrix4d tmp(m1);
        tmp *= m2;
        return tmp;
    }

    //! Matrix storage, in row-major order.
    double _mtx[4][4];
};

// Leaves the [3][3] element as 1
inline __device__ Matrix4d& Matrix4d::SetScale(double s)
{
    _mtx[0][0] = s;
    _mtx[0][1] = 0.0;
    _mtx[0][2] = 0.0;
    _mtx[0][3] = 0.0;
    _mtx[1][0] = 0.0;
    _mtx[1][1] = s;
    _mtx[1][2] = 0.0;
    _mtx[1][3] = 0.0;
    _mtx[2][0] = 0.0;
    _mtx[2][1] = 0.0;
    _mtx[2][2] = s;
    _mtx[2][3] = 0.0;
    _mtx[3][0] = 0.0;
    _mtx[3][1] = 0.0;
    _mtx[3][2] = 0.0;
    _mtx[3][3] = 1.0;

    return *this;
}

inline __device__ Matrix4d& Matrix4d::SetDiagonal(double s)
{
    _mtx[0][0] = s;
    _mtx[0][1] = 0.0;
    _mtx[0][2] = 0.0;
    _mtx[0][3] = 0.0;
    _mtx[1][0] = 0.0;
    _mtx[1][1] = s;
    _mtx[1][2] = 0.0;
    _mtx[1][3] = 0.0;
    _mtx[2][0] = 0.0;
    _mtx[2][1] = 0.0;
    _mtx[2][2] = s;
    _mtx[2][3] = 0.0;
    _mtx[3][0] = 0.0;
    _mtx[3][1] = 0.0;
    _mtx[3][2] = 0.0;
    _mtx[3][3] = s;
    return *this;
}

inline __device__ Matrix4d Matrix4d::GetInverse() const
{
    double x00, x01, x02, x03;
    double x10, x11, x12, x13;
    double x20, x21, x22, x23;
    double x30, x31, x32, x33;
    double y01, y02, y03, y12, y13, y23;
    double z00, z10, z20, z30;
    double z01, z11, z21, z31;
    double z02, z03, z12, z13, z22, z23, z32, z33;

    // Pickle 1st two columns of matrix into registers
    x00 = _mtx[0][0];
    x01 = _mtx[0][1];
    x10 = _mtx[1][0];
    x11 = _mtx[1][1];
    x20 = _mtx[2][0];
    x21 = _mtx[2][1];
    x30 = _mtx[3][0];
    x31 = _mtx[3][1];

    // Compute all six 2x2 determinants of 1st two columns
    y01 = x00 * x11 - x10 * x01;
    y02 = x00 * x21 - x20 * x01;
    y03 = x00 * x31 - x30 * x01;
    y12 = x10 * x21 - x20 * x11;
    y13 = x10 * x31 - x30 * x11;
    y23 = x20 * x31 - x30 * x21;

    // Pickle last two columns of matrix into registers
    x02 = _mtx[0][2];
    x03 = _mtx[0][3];
    x12 = _mtx[1][2];
    x13 = _mtx[1][3];
    x22 = _mtx[2][2];
    x23 = _mtx[2][3];
    x32 = _mtx[3][2];
    x33 = _mtx[3][3];

    // Compute all 3x3 cofactors for 2nd two columns */
    z33 = x02 * y12 - x12 * y02 + x22 * y01;
    z23 = x12 * y03 - x32 * y01 - x02 * y13;
    z13 = x02 * y23 - x22 * y03 + x32 * y02;
    z03 = x22 * y13 - x32 * y12 - x12 * y23;
    z32 = x13 * y02 - x23 * y01 - x03 * y12;
    z22 = x03 * y13 - x13 * y03 + x33 * y01;
    z12 = x23 * y03 - x33 * y02 - x03 * y23;
    z02 = x13 * y23 - x23 * y13 + x33 * y12;

    // Compute all six 2x2 determinants of 2nd two columns
    y01 = x02 * x13 - x12 * x03;
    y02 = x02 * x23 - x22 * x03;
    y03 = x02 * x33 - x32 * x03;
    y12 = x12 * x23 - x22 * x13;
    y13 = x12 * x33 - x32 * x13;
    y23 = x22 * x33 - x32 * x23;

    // Compute all 3x3 cofactors for 1st two columns
    z30 = x11 * y02 - x21 * y01 - x01 * y12;
    z20 = x01 * y13 - x11 * y03 + x31 * y01;
    z10 = x21 * y03 - x31 * y02 - x01 * y23;
    z00 = x11 * y23 - x21 * y13 + x31 * y12;
    z31 = x00 * y12 - x10 * y02 + x20 * y01;
    z21 = x10 * y03 - x30 * y01 - x00 * y13;
    z11 = x00 * y23 - x20 * y03 + x30 * y02;
    z01 = x20 * y13 - x30 * y12 - x10 * y23;

    // compute 4x4 determinant & its reciprocal
    double det = x30 * z30 + x20 * z20 + x10 * z10 + x00 * z00;

    Matrix4d inverse;

    double eps = 0;
    if (abs(det) > eps)
    {

        double rcp = 1.0 / det;
        // Multiply all 3x3 cofactors by reciprocal & transpose
        inverse._mtx[0][0] = z00 * rcp;
        inverse._mtx[0][1] = z10 * rcp;
        inverse._mtx[1][0] = z01 * rcp;
        inverse._mtx[0][2] = z20 * rcp;
        inverse._mtx[2][0] = z02 * rcp;
        inverse._mtx[0][3] = z30 * rcp;
        inverse._mtx[3][0] = z03 * rcp;
        inverse._mtx[1][1] = z11 * rcp;
        inverse._mtx[1][2] = z21 * rcp;
        inverse._mtx[2][1] = z12 * rcp;
        inverse._mtx[1][3] = z31 * rcp;
        inverse._mtx[3][1] = z13 * rcp;
        inverse._mtx[2][2] = z22 * rcp;
        inverse._mtx[2][3] = z32 * rcp;
        inverse._mtx[3][2] = z23 * rcp;
        inverse._mtx[3][3] = z33 * rcp;
    }
    else
    {
        inverse.SetScale(FLT_MAX);
    }

    return inverse;
}

inline __device__ Matrix4d& Matrix4d::operator*=(const Matrix4d& m)
{
    // Save current values before they are overwritten
    Matrix4d tmp = *this;

    _mtx[0][0] = tmp._mtx[0][0] * m._mtx[0][0] + tmp._mtx[0][1] * m._mtx[1][0] + tmp._mtx[0][2] * m._mtx[2][0] +
                 tmp._mtx[0][3] * m._mtx[3][0];

    _mtx[0][1] = tmp._mtx[0][0] * m._mtx[0][1] + tmp._mtx[0][1] * m._mtx[1][1] + tmp._mtx[0][2] * m._mtx[2][1] +
                 tmp._mtx[0][3] * m._mtx[3][1];

    _mtx[0][2] = tmp._mtx[0][0] * m._mtx[0][2] + tmp._mtx[0][1] * m._mtx[1][2] + tmp._mtx[0][2] * m._mtx[2][2] +
                 tmp._mtx[0][3] * m._mtx[3][2];

    _mtx[0][3] = tmp._mtx[0][0] * m._mtx[0][3] + tmp._mtx[0][1] * m._mtx[1][3] + tmp._mtx[0][2] * m._mtx[2][3] +
                 tmp._mtx[0][3] * m._mtx[3][3];

    _mtx[1][0] = tmp._mtx[1][0] * m._mtx[0][0] + tmp._mtx[1][1] * m._mtx[1][0] + tmp._mtx[1][2] * m._mtx[2][0] +
                 tmp._mtx[1][3] * m._mtx[3][0];

    _mtx[1][1] = tmp._mtx[1][0] * m._mtx[0][1] + tmp._mtx[1][1] * m._mtx[1][1] + tmp._mtx[1][2] * m._mtx[2][1] +
                 tmp._mtx[1][3] * m._mtx[3][1];

    _mtx[1][2] = tmp._mtx[1][0] * m._mtx[0][2] + tmp._mtx[1][1] * m._mtx[1][2] + tmp._mtx[1][2] * m._mtx[2][2] +
                 tmp._mtx[1][3] * m._mtx[3][2];

    _mtx[1][3] = tmp._mtx[1][0] * m._mtx[0][3] + tmp._mtx[1][1] * m._mtx[1][3] + tmp._mtx[1][2] * m._mtx[2][3] +
                 tmp._mtx[1][3] * m._mtx[3][3];

    _mtx[2][0] = tmp._mtx[2][0] * m._mtx[0][0] + tmp._mtx[2][1] * m._mtx[1][0] + tmp._mtx[2][2] * m._mtx[2][0] +
                 tmp._mtx[2][3] * m._mtx[3][0];

    _mtx[2][1] = tmp._mtx[2][0] * m._mtx[0][1] + tmp._mtx[2][1] * m._mtx[1][1] + tmp._mtx[2][2] * m._mtx[2][1] +
                 tmp._mtx[2][3] * m._mtx[3][1];

    _mtx[2][2] = tmp._mtx[2][0] * m._mtx[0][2] + tmp._mtx[2][1] * m._mtx[1][2] + tmp._mtx[2][2] * m._mtx[2][2] +
                 tmp._mtx[2][3] * m._mtx[3][2];

    _mtx[2][3] = tmp._mtx[2][0] * m._mtx[0][3] + tmp._mtx[2][1] * m._mtx[1][3] + tmp._mtx[2][2] * m._mtx[2][3] +
                 tmp._mtx[2][3] * m._mtx[3][3];

    _mtx[3][0] = tmp._mtx[3][0] * m._mtx[0][0] + tmp._mtx[3][1] * m._mtx[1][0] + tmp._mtx[3][2] * m._mtx[2][0] +
                 tmp._mtx[3][3] * m._mtx[3][0];

    _mtx[3][1] = tmp._mtx[3][0] * m._mtx[0][1] + tmp._mtx[3][1] * m._mtx[1][1] + tmp._mtx[3][2] * m._mtx[2][1] +
                 tmp._mtx[3][3] * m._mtx[3][1];

    _mtx[3][2] = tmp._mtx[3][0] * m._mtx[0][2] + tmp._mtx[3][1] * m._mtx[1][2] + tmp._mtx[3][2] * m._mtx[2][2] +
                 tmp._mtx[3][3] * m._mtx[3][2];

    _mtx[3][3] = tmp._mtx[3][0] * m._mtx[0][3] + tmp._mtx[3][1] * m._mtx[1][3] + tmp._mtx[3][2] * m._mtx[2][3] +
                 tmp._mtx[3][3] * m._mtx[3][3];

    return *this;
}

inline __device__ static float3 getTranslation(const Matrix4d& src)
{
    return float3{ float(src._mtx[3][0]), float(src._mtx[3][1]), float(src._mtx[3][2]) };
}

inline __device__ static float4 getRotation(const Matrix4d& src)
{
    // if (!removeScale(src))
    //{
    //    return carb::Float4{0.0f, 0.0f, 0.0f, 1.0f};
    //}

    float tr = float(src._mtx[0][0] + src._mtx[1][1] + src._mtx[2][2]);
    if (tr >= 0.0)
    {
        float s = sqrtf(tr + 1.0f); // better use invsqrt, but didn't find the fast API....
        float4 result;
        result.w = 0.5f * s;
        s = 0.5f / s;
        result.x = float(src._mtx[1][2] - src._mtx[2][1]) * s;
        result.y = float(src._mtx[2][0] - src._mtx[0][2]) * s;
        result.z = float(src._mtx[0][1] - src._mtx[1][0]) * s;
        return result;
    }
    else
    {
        int i = 0;
        if (src._mtx[1][1] > src._mtx[0][0])
            i = 1;
        if (src._mtx[2][2] > src._mtx[i][i])
            i = 2;

        static constexpr int next[3] = { 1, 2, 0 };
        int j = next[i];
        int k = next[j];

        float s = float(sqrt(src._mtx[i][i] - src._mtx[j][j] - src._mtx[k][k] + 1.0f));
        float quat[4];
        quat[i] = 0.5f * s;
        s = 0.5f / s;
        quat[j] = float(src._mtx[i][j] + src._mtx[j][i]) * s;
        quat[k] = float(src._mtx[k][i] + src._mtx[i][k]) * s;
        quat[3] = float(src._mtx[j][k] - src._mtx[k][j]) * s;
        return float4{ quat[0], quat[1], quat[2], quat[3] };
    }
}

inline __device__ static float4 quatMultiply(const float4& q0, const float4& q1)
{
    float4 result;
    result.x = q0.w * q1.x + q0.x * q1.w + q0.y * q1.z - q0.z * q1.y;
    result.y = q0.w * q1.y - q0.x * q1.z + q0.y * q1.w + q0.z * q1.x;
    result.z = q0.w * q1.z + q0.x * q1.y - q0.y * q1.x + q0.z * q1.w;
    result.w = q0.w * q1.w - q0.x * q1.x - q0.y * q1.y - q0.z * q1.z;

    return result;
}

inline __device__ static void matrixToDualQuat(float* dst, const Matrix4d& src)
{
    float3 trans = getTranslation(src);
    float4 quat = getRotation(src);

    float invQuatLength = 1 / sqrt(quat.x * quat.x + quat.y * quat.y + quat.z * quat.z + quat.w * quat.w);

    dst[0] = quat.x * invQuatLength;
    dst[1] = quat.y * invQuatLength;
    dst[2] = quat.z * invQuatLength;
    dst[3] = quat.w * invQuatLength;

    float4 quat2{ trans.x, trans.y, trans.z, 0.0f };
    float4 dual = quatMultiply(quat2, float4{ dst[0], dst[1], dst[2], dst[3] });
    dst[4] = dual.x * 0.5f;
    dst[5] = dual.y * 0.5f;
    dst[6] = dual.z * 0.5f;
    dst[7] = dual.w * 0.5f;
}
