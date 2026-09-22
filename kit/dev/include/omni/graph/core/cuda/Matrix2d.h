// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

// CUDA-compatible struct with functions for working with a 2x2 double matrix

#include <float.h>

struct Matrix2d
{
    //! Default constructor. Leaves the matrix component values undefined.
    Matrix2d() = default;

    __device__ explicit Matrix2d(double s)
    {
        SetDiagonal(s);
    }

    __device__ Matrix2d& SetDiagonal(double s);
    __device__ Matrix2d& SetScale(double s);
    __device__ Matrix2d GetInverse() const;

    //! Post-multiplies matrix \e m into this matrix.
    __device__ Matrix2d& operator*=(const Matrix2d& m);

    //! Multiplies matrix \e m1 by \e m2.
    __device__ friend Matrix2d operator*(const Matrix2d& m1, const Matrix2d& m2)
    {
        Matrix2d tmp(m1);
        tmp *= m2;
        return tmp;
    }

    //! Matrix storage, in row-major order.
    double _mtx[2][2];
};

// Leaves the [2][2] element as 1
inline __device__ Matrix2d& Matrix2d::SetScale(double s)
{
    _mtx[0][0] = s;
    _mtx[0][1] = 0.0;
    _mtx[1][0] = 0.0;
    _mtx[1][1] = s;

    return *this;
}

inline __device__ Matrix2d& Matrix2d::SetDiagonal(double s)
{
    _mtx[0][0] = s;
    _mtx[0][1] = 0.0;
    _mtx[1][0] = 0.0;
    _mtx[1][1] = s;
    return *this;
}

inline __device__ Matrix2d Matrix2d::GetInverse() const
{
    double x00, x01;
    double x10, x11;

    // Pickle values for computing determinants into registers
    x00 = _mtx[0][0];
    x01 = _mtx[0][1];
    x10 = _mtx[1][0];
    x11 = _mtx[1][1];

    // Compute the determinant
    double det = x00 * x11 - x01 * x10;

    Matrix2d inverse;

    double eps = 0;
    if (abs(det) > eps)
    {
        double rcp = 1.0 / det;
        // Multiply all 3x3 cofactors by reciprocal & transpose
        inverse._mtx[0][0] = x11 * rcp;
        inverse._mtx[0][1] = -x01 * rcp;
        inverse._mtx[1][0] = -x10 * rcp;
        inverse._mtx[1][1] = x00 * rcp;
    }
    else
    {
        inverse.SetScale(FLT_MAX);
    }

    return inverse;
}

inline __device__ Matrix2d& Matrix2d::operator*=(const Matrix2d& m)
{
    // Save current values before they are overwritten
    Matrix2d tmp = *this;

    _mtx[0][0] = tmp._mtx[0][0] * m._mtx[0][0] + tmp._mtx[0][1] * m._mtx[1][0];
    _mtx[0][1] = tmp._mtx[0][0] * m._mtx[0][1] + tmp._mtx[0][1] * m._mtx[1][1];

    _mtx[1][0] = tmp._mtx[1][0] * m._mtx[0][0] + tmp._mtx[1][1] * m._mtx[1][0];
    _mtx[1][1] = tmp._mtx[1][0] * m._mtx[0][1] + tmp._mtx[1][1] * m._mtx[1][1];

    return *this;
}
