// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

// CUDA-compatible struct with functions for working with a 3x3 double matrix

#include <float.h>

struct Matrix3d
{
    //! Default constructor. Leaves the matrix component values undefined.
    Matrix3d() = default;

    __device__ explicit Matrix3d(double s)
    {
        SetDiagonal(s);
    }

    __device__ Matrix3d& SetDiagonal(double s);
    __device__ Matrix3d& SetScale(double s);
    __device__ Matrix3d GetInverse() const;

    //! Post-multiplies matrix \e m into this matrix.
    __device__ Matrix3d& operator*=(const Matrix3d& m);

    //! Multiplies matrix \e m1 by \e m2.
    __device__ friend Matrix3d operator*(const Matrix3d& m1, const Matrix3d& m2)
    {
        Matrix3d tmp(m1);
        tmp *= m2;
        return tmp;
    }

    //! Matrix storage, in row-major order.
    double _mtx[3][3];
};

// Leaves the [2][2] element as 1
inline __device__ Matrix3d& Matrix3d::SetScale(double s)
{
    _mtx[0][0] = s;
    _mtx[0][1] = 0.0;
    _mtx[0][2] = 0.0;
    _mtx[1][0] = 0.0;
    _mtx[1][1] = s;
    _mtx[1][2] = 0.0;
    _mtx[2][0] = 0.0;
    _mtx[2][1] = 0.0;
    _mtx[2][2] = s;

    return *this;
}

inline __device__ Matrix3d& Matrix3d::SetDiagonal(double s)
{
    _mtx[0][0] = s;
    _mtx[0][1] = 0.0;
    _mtx[0][2] = 0.0;
    _mtx[1][0] = 0.0;
    _mtx[1][1] = s;
    _mtx[1][2] = 0.0;
    _mtx[2][0] = 0.0;
    _mtx[2][1] = 0.0;
    _mtx[2][2] = s;
    return *this;
}

inline __device__ Matrix3d Matrix3d::GetInverse() const
{
    double x00, x01, x02;
    double x10, x11, x12;
    double x20, x21, x22;

    double det00, det01, det02;
    double det10, det11, det12;
    double det20, det21, det22;

    // Pickle values for computing determinants into registers
    x00 = _mtx[0][0];
    x01 = _mtx[0][1];
    x02 = _mtx[0][2];
    x10 = _mtx[1][0];
    x11 = _mtx[1][1];
    x12 = _mtx[1][2];
    x20 = _mtx[2][0];
    x21 = _mtx[2][1];
    x22 = _mtx[2][2];

    // Compute the determinants of the transposed matrix
    det00 = x11 * x22 - x21 * x12;
    det01 = x02 * x21 - x01 * x22;
    det02 = x01 * x12 - x02 * x11;
    det10 = x12 * x20 - x10 * x22;
    det11 = x00 * x22 - x02 * x20;
    det12 = x10 * x02 - x00 * x12;
    det20 = x10 * x21 - x20 * x11;
    det21 = x20 * x01 - x00 * x21;
    det22 = x00 * x11 - x10 * x01;

    // compute determinant from the first row
    double det = x00 * det00 + x01 * det10 + x02 * det20;

    Matrix3d inverse;

    double eps = 0;
    if (abs(det) > eps)
    {
        double rcp = 1.0 / det;
        // Multiply all 3x3 cofactors by reciprocal & transpose
        inverse._mtx[0][0] = det00 * rcp;
        inverse._mtx[0][1] = det01 * rcp;
        inverse._mtx[1][0] = det10 * rcp;
        inverse._mtx[0][2] = det02 * rcp;
        inverse._mtx[2][0] = det20 * rcp;
        inverse._mtx[1][1] = det11 * rcp;
        inverse._mtx[1][2] = det12 * rcp;
        inverse._mtx[2][1] = det21 * rcp;
        inverse._mtx[2][2] = det22 * rcp;
    }
    else
    {
        inverse.SetScale(FLT_MAX);
    }

    return inverse;
}

inline __device__ Matrix3d& Matrix3d::operator*=(const Matrix3d& m)
{
    // Save current values before they are overwritten
    Matrix3d tmp = *this;

    _mtx[0][0] = tmp._mtx[0][0] * m._mtx[0][0] + tmp._mtx[0][1] * m._mtx[1][0] + tmp._mtx[0][2] * m._mtx[2][0];
    _mtx[0][1] = tmp._mtx[0][0] * m._mtx[0][1] + tmp._mtx[0][1] * m._mtx[1][1] + tmp._mtx[0][2] * m._mtx[2][1];
    _mtx[0][2] = tmp._mtx[0][0] * m._mtx[0][2] + tmp._mtx[0][1] * m._mtx[1][2] + tmp._mtx[0][2] * m._mtx[2][2];

    _mtx[1][0] = tmp._mtx[1][0] * m._mtx[0][0] + tmp._mtx[1][1] * m._mtx[1][0] + tmp._mtx[1][2] * m._mtx[2][0];
    _mtx[1][1] = tmp._mtx[1][0] * m._mtx[0][1] + tmp._mtx[1][1] * m._mtx[1][1] + tmp._mtx[1][2] * m._mtx[2][1];
    _mtx[1][2] = tmp._mtx[1][0] * m._mtx[0][2] + tmp._mtx[1][1] * m._mtx[1][2] + tmp._mtx[1][2] * m._mtx[2][2];

    _mtx[2][0] = tmp._mtx[2][0] * m._mtx[0][0] + tmp._mtx[2][1] * m._mtx[1][0] + tmp._mtx[2][2] * m._mtx[2][0];
    _mtx[2][1] = tmp._mtx[2][0] * m._mtx[0][1] + tmp._mtx[2][1] * m._mtx[1][1] + tmp._mtx[2][2] * m._mtx[2][1];
    _mtx[2][2] = tmp._mtx[2][0] * m._mtx[0][2] + tmp._mtx[2][1] * m._mtx[1][2] + tmp._mtx[2][2] * m._mtx[2][2];

    return *this;
}
