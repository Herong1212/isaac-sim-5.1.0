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

#include <usdrt/gf/defines.h>
#include <usdrt/gf/math.h>
#include <usdrt/gf/traits.h>
#include <usdrt/gf/vec.h>

#include <initializer_list>

namespace omni
{
namespace math
{
namespace linalg
{

// Forward declaration, just for the using statement, below.
class half;

template <typename T>
class quat : private base_vec<T, 4>
{
public:
    using base_type = base_vec<T, 4>;
    // usdrt edit
    using typename base_type::const_iterator;
    using typename base_type::const_pointer;
    using typename base_type::const_reference;
    using typename base_type::difference_type;
    using typename base_type::iterator;
    using typename base_type::pointer;
    using typename base_type::reference;
    using typename base_type::size_type;
    using typename base_type::value_type;
    // end usdrt edit

    using ScalarType = T;
    using ImaginaryType = vec3<T>;
#ifndef DOXYGEN_BUILD
    constexpr static size_t dimension = 4;
    constexpr static size_t real_index = 3;
    constexpr static size_t imaginary_index = 0;
#endif // DOXYGEN_BUILD

    quat() = default;
    constexpr quat(const quat<T>&) = default;

    // Explicit conversion from base class, to avoid issues on that front.
    constexpr explicit CUDA_CALLABLE quat(const base_type& other) : base_type(other)
    {
    }

    // NOTE: This usually only makes sense for real being -1, 0, or 1.
    constexpr explicit CUDA_CALLABLE quat(T real) : base_type(T(0), T(0), T(0), real)
    {
    }

    // NOTE: The order of the arguments is different from the order in memory!
    constexpr CUDA_CALLABLE quat(T real, T i, T j, T k) : base_type(i, j, k, real)
    {
    }

    // NOTE: The order of the arguments is different from the order in memory!
    constexpr CUDA_CALLABLE quat(T real, vec3<T> imaginary) : base_type(imaginary[0], imaginary[1], imaginary[2], real)
    {
    }

    template <typename OTHER_T>
    explicit CUDA_CALLABLE quat(const quat<OTHER_T>& other) : quat(T(other.GetReal()), vec3<T>(other.GetImaginary()))
    {
    }

    // NOTE: The order of the arguments is different from the order in memory,
    //       so we can't delegate directly to the base class constructor.
    template <typename OTHER_T>
    CUDA_CALLABLE quat(const std::initializer_list<OTHER_T>& other) noexcept : base_type(T(0), T(0), T(0), T(0))
    {
        CUDA_SAFE_ASSERT(other.size() == 4);
        if (other.size() != 4)
            return;
        // Order change as above
        base_type::operator[](0) = other.begin()[1];
        base_type::operator[](1) = other.begin()[2];
        base_type::operator[](2) = other.begin()[3];
        base_type::operator[](3) = other.begin()[0];
    }

    static CUDA_CALLABLE quat<T> GetIdentity()
    {
        return quat<T>(T(1));
    }

    CUDA_CALLABLE T GetReal() const
    {
        return base_type::operator[](real_index);
    }
    CUDA_CALLABLE void SetReal(T real)
    {
        base_type::operator[](real_index) = real;
    }

    CUDA_CALLABLE vec3<T> GetImaginary() const
    {
        return vec3<T>(base_type::operator[](imaginary_index), base_type::operator[](imaginary_index + 1),
                       base_type::operator[](imaginary_index + 2));
    }
    CUDA_CALLABLE void SetImaginary(const vec3<T>& imaginary)
    {
        base_type::operator[](imaginary_index) = imaginary[0];
        base_type::operator[](imaginary_index + 1) = imaginary[1];
        base_type::operator[](imaginary_index + 2) = imaginary[2];
    }
    CUDA_CALLABLE void SetImaginary(T i, T j, T k)
    {
        base_type::operator[](imaginary_index) = i;
        base_type::operator[](imaginary_index + 1) = j;
        base_type::operator[](imaginary_index + 2) = k;
    }

    constexpr CUDA_CALLABLE T Dot(const quat<T>& other) const
    {
        return base_type::Dot(other);
        // return GetImaginary().Dot(other.GetImaginary()) + GetReal() * other.GetReal();
    }

    using base_type::data;
    using base_type::GetLength;
    using base_type::GetLengthSq;
    using base_type::Normalize;

#ifndef DOXYGEN_BUILD
    CUDA_CALLABLE quat<T> GetNormalized() const
    {
        return quat<T>(base_type::GetNormalized());
    }
#endif // DOXYGEN_BUILD

    CUDA_CALLABLE quat<T> GetConjugate() const
    {
        return quat<T>(GetReal(), -GetImaginary());
    }

    CUDA_CALLABLE quat<T> GetInverse() const
    {
        return GetConjugate() / GetLengthSq();
    }

    CUDA_CALLABLE vec3<T> Transform(const vec3<T>& point) const
    {
        const auto& cosTheta = GetReal();
        const T cosTheta2 = GetReal() * GetReal();
        const vec3<T> sinThetas = GetImaginary();
        const T sinTheta2 = sinThetas.GetLengthSq();
        const T length2 = cosTheta2 + sinTheta2;
        const T cos2Theta = cosTheta2 - sinTheta2;
        return (cos2Theta * point +
                ((2 * GfDot(sinThetas, point)) * sinThetas + (2 * cosTheta) * GfCross(sinThetas, point))) /
               length2;
    }

    // NOTE: To avoid including Boost unless absolutely necessary, hash_value() is not defined here.

    CUDA_CALLABLE quat<T> operator-() const
    {
        return quat<T>(-GetReal(), -GetImaginary());
    }

    CUDA_CALLABLE bool operator==(const quat<T>& other) const
    {
        return (GetImaginary() == other.GetImaginary()) && (GetReal() == other.GetReal());
    }
    CUDA_CALLABLE bool operator!=(const quat<T>& other) const
    {
        return !(*this == other);
    }

    CUDA_CALLABLE quat<T>& operator*=(const quat<T>& other)
    {
        const T r0 = GetReal();
        const T r1 = other.GetReal();
        const vec3<T> i0 = GetImaginary();
        const vec3<T> i1 = other.GetImaginary();

        // TODO: This isn't the most efficient way to multiply two quaternions.
        SetImaginary(r0 * i1 + r1 * i0 + GfCross(i0, i1));
        SetReal(r0 * r1 - i0.Dot(i1));

        return *this;
    }

    CUDA_CALLABLE quat<T>& operator*=(T scalar)
    {
        base_type::operator*=(scalar);
        return *this;
    }

    CUDA_CALLABLE quat<T>& operator/=(T scalar)
    {
        base_type::operator/=(scalar);
        return *this;
    }

    CUDA_CALLABLE quat<T>& operator+=(const quat<T>& other)
    {
        base_type::operator+=(other);
        return *this;
    }

    CUDA_CALLABLE quat<T>& operator-=(const quat<T>& other)
    {
        base_type::operator-=(other);
        return *this;
    }

#ifndef DOXYGEN_BUILD
    friend CUDA_CALLABLE quat<T> operator+(const quat<T>& a, const quat<T>& b)
    {
        return quat<T>(((const base_type&)a) + ((const base_type&)b));
    }
    friend CUDA_CALLABLE quat<T> operator-(const quat<T>& a, const quat<T>& b)
    {
        return quat<T>(((const base_type&)a) - ((const base_type&)b));
    }
    friend CUDA_CALLABLE quat<T> operator*(const quat<T>& a, const quat<T>& b)
    {
        quat<T> product(a);
        product *= b;
        return product;
    }
    friend CUDA_CALLABLE quat<T> operator*(const quat<T>& q, T scalar)
    {
        return quat<T>(((const base_type&)q) * scalar);
    }
    friend CUDA_CALLABLE quat<T> operator*(T scalar, const quat<T>& q)
    {
        return quat<T>(((const base_type&)q) * scalar);
    }
    friend CUDA_CALLABLE quat<T> operator/(const quat<T>& q, T scalar)
    {
        return quat<T>(((const base_type&)q) / scalar);
    }
#endif
};

template <typename T>
CUDA_CALLABLE T GfDot(const quat<T>& a, const quat<T>& b)
{
    return a.Dot(b);
}

template <typename T>
CUDA_CALLABLE bool GfIsClose(const quat<T>& a, const quat<T>& b, double tolerance)
{
    auto distanceSq = (a - b).GetLengthSq();
    return distanceSq <= tolerance * tolerance;
}


template <typename T>
CUDA_CALLABLE quat<T> GfSlerp(const quat<T>& a, const quat<T>& b, double t)
{
    const quat<double> ad(a);
    quat<double> bd(b);
    double d = ad.Dot(bd);

    // NOTE: Although a proper slerp wouldn't flip b on negative dot, this flips b
    //       for compatibility.  Quaternions cover the space of orientations twice, so this
    //       avoids interpolating between orientations that are more than 180 degrees apart.
    if (d < 0)
    {
        bd = -bd;
        d = -d;
    }

    const double arbitraryThreshold = (1.0 - 1e-5);
    if (d < arbitraryThreshold)
    {
        // Common case: large enough angle between a and b for stable angle from acos and stable complement
        const double angle = t * std::acos(d);
        quat<double> complement = bd - d * ad;
        complement.Normalize();
        return quat<T>(std::cos(angle) * ad + std::sin(angle) * complement);
    }

    // For small angles, just linearly interpolate.
    return quat<T>(ad + t * (bd - ad));
}

using quath = quat<half>;
using quatf = quat<float>;
using quatd = quat<double>;

// Alphabetical order (same order as pxr::UsdGeomXformCommonAPI::RotationOrder)
enum class EulerRotationOrder
{
    XYZ,
    XZY,
    YXZ,
    YZX,
    ZXY,
    ZYX
};

static constexpr size_t s_eulerRotationOrderAxes[6][3] = {
    { 0, 1, 2 }, // XYZ
    { 0, 2, 1 }, // XZY
    { 1, 0, 2 }, // YXZ
    { 1, 2, 0 }, // YZX
    { 2, 0, 1 }, // ZXY
    { 2, 1, 0 } // ZYX
};

// eulerAngles is in radians.  You can use GfDegreesToRadians to convert.
template <typename T>
CUDA_CALLABLE quatd eulerAnglesToQuaternion(const vec3<T>& eulerAngles, EulerRotationOrder order)
{
    // There's almost certainly a more efficient way to do this, but this should work,
    // (unless the quaternion order is backward from what's needed, but then
    // choosing the reverse rotation order should address that.)

    // Quaternions are applied "on both sides", so each contains half the rotation,
    // or at least that's a mnemonic to remember to half it.
    const vec3d halfAngles = 0.5 * vec3d(eulerAngles);

    const double cx = std::cos(halfAngles[0]);
    const double sx = std::sin(halfAngles[0]);
    const double cy = std::cos(halfAngles[1]);
    const double sy = std::sin(halfAngles[1]);
    const double cz = std::cos(halfAngles[2]);
    const double sz = std::sin(halfAngles[2]);

    const quatd qs[3] = { quatd(cx, vec3d(sx, 0, 0)), quatd(cy, vec3d(0, sy, 0)), quatd(cz, vec3d(0, 0, sz)) };

    // Apply the quaternions in the specified order
    // NOTE: Even though USD matrix transformations are applied to row vectors from left to right,
    //       quaternions are still applied from right to left, like standard quaternions.
    const size_t* const orderAxes = s_eulerRotationOrderAxes[size_t(order)];
    const quatd q = qs[orderAxes[2]] * qs[orderAxes[1]] * qs[orderAxes[0]];

    return q;
}

}
}
}

namespace usdrt
{

using omni::math::linalg::GfDot;
using omni::math::linalg::GfIsClose;
using omni::math::linalg::GfSlerp;

using GfQuatd = omni::math::linalg::quat<double>;
using GfQuatf = omni::math::linalg::quat<float>;
using GfQuath = omni::math::linalg::quat<omni::math::linalg::half>;


template <>
struct GfIsGfQuat<GfQuatd>
{
    static const bool value = true;
};

template <>
struct GfIsGfQuat<GfQuatf>
{
    static const bool value = true;
};

template <>
struct GfIsGfQuat<GfQuath>
{
    static const bool value = true;
};

}
