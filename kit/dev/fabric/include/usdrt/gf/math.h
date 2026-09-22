// Copyright (c) 2021-2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

//! @file
//!
//! @brief TODO

#ifdef _MSC_VER
// This is for M_PI
#    define _USE_MATH_DEFINES
#    include <math.h>
#endif

#include <usdrt/gf/defines.h>

#include <cmath>

namespace omni
{
namespace math
{
namespace linalg
{

// WARNING: Non-standard parameter order, for compatibility!
template <typename VALUE_T>
CUDA_CALLABLE VALUE_T GfLerp(double t, const VALUE_T& a, const VALUE_T& b)
{
    // Always use the difference, so that if a==b, a value equal to both
    // will be returned, instead of one that might have roundoff error.
    return a + t * (b - a);
}

template <typename VALUE_T>
CUDA_CALLABLE VALUE_T GfRadiansToDegrees(VALUE_T radians)
{
    return radians * VALUE_T(180.0 / M_PI);
}

template <typename VALUE_T>
CUDA_CALLABLE VALUE_T GfDegreesToRadians(VALUE_T degrees)
{
    return degrees * VALUE_T(M_PI / 180.0);
}

CUDA_CALLABLE inline bool GfIsClose(double a, double b, double epsilon)
{
    return fabs(a - b) < epsilon;
}

template <typename VALUE_T>
CUDA_CALLABLE VALUE_T GfMin(VALUE_T a1, VALUE_T a2)
{
    return (a1 < a2 ? a1 : a2);
}

template <typename VALUE_T>
CUDA_CALLABLE VALUE_T GfMin(VALUE_T a1, VALUE_T a2, VALUE_T a3)
{
    return GfMin(GfMin(a1, a2), a3);
}

template <typename VALUE_T>
CUDA_CALLABLE VALUE_T GfMin(VALUE_T a1, VALUE_T a2, VALUE_T a3, VALUE_T a4)
{
    return GfMin(GfMin(a1, a2, a3), a4);
}

template <typename VALUE_T>
CUDA_CALLABLE VALUE_T GfMin(VALUE_T a1, VALUE_T a2, VALUE_T a3, VALUE_T a4, VALUE_T a5)
{
    return GfMin(GfMin(a1, a2, a3, a4), a5);
}

template <typename VALUE_T>
CUDA_CALLABLE VALUE_T GfMax(VALUE_T a1, VALUE_T a2)
{
    return (a1 < a2 ? a2 : a1);
}

template <typename VALUE_T>
CUDA_CALLABLE VALUE_T GfMax(VALUE_T a1, VALUE_T a2, VALUE_T a3)
{
    return GfMax(GfMax(a1, a2), a3);
}

template <typename VALUE_T>
CUDA_CALLABLE VALUE_T GfMax(VALUE_T a1, VALUE_T a2, VALUE_T a3, VALUE_T a4)
{
    return GfMax(GfMax(a1, a2, a3), a4);
}

template <typename VALUE_T>
CUDA_CALLABLE VALUE_T GfMax(VALUE_T a1, VALUE_T a2, VALUE_T a3, VALUE_T a4, VALUE_T a5)
{
    return GfMax(GfMax(a1, a2, a3, a4), a5);
}

template <class VALUE_T>
inline double GfSqr(const VALUE_T& x)
{
    return x * x;
}

template <class VALUE_T>
inline VALUE_T GfClamp(const VALUE_T x, const VALUE_T min, VALUE_T max)
{
    if (x < min)
        return min;
    if (x > max)
        return max;
    return x;
}

template <class VALUE_T>
inline void GfSinCos(const VALUE_T v, VALUE_T* s, VALUE_T* c)
{
    *s = std::sin(v);
    *c = std::cos(v);
}

template <class VALUE_T>
inline VALUE_T GfAbs(VALUE_T f)
{
    return std::fabs(f);
}

template <class VALUE_T>
inline VALUE_T GfSqrt(VALUE_T f)
{
    return std::sqrt(f);
}
}
}
}

namespace usdrt
{

using omni::math::linalg::GfAbs;
using omni::math::linalg::GfClamp;
using omni::math::linalg::GfDegreesToRadians;
using omni::math::linalg::GfIsClose;
using omni::math::linalg::GfLerp;
using omni::math::linalg::GfMax;
using omni::math::linalg::GfMin;
using omni::math::linalg::GfRadiansToDegrees;
using omni::math::linalg::GfSinCos;
using omni::math::linalg::GfSqr;
using omni::math::linalg::GfSqrt;

}
