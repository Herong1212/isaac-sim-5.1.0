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

#include <carb/Defines.h>

#include <usdrt/gf/half.h>
#include <usdrt/gf/math.h>

#include <cmath>
#include <initializer_list>
#include <stdint.h>
#include <type_traits>

#ifndef __CUDACC__
#    define CUDA_SAFE_ASSERT(cond, ...) CARB_ASSERT(cond, ##__VA_ARGS__)
#    define CUDA_CALLABLE
#else
#    define CUDA_SAFE_ASSERT(cond, ...)
#    define CUDA_CALLABLE __device__ __host__
#endif

namespace omni
{
namespace math
{
namespace linalg
{

// Forward declaration, just for the using statements, below.
class half;

template <typename T, size_t N>
class base_vec
{
public:
    // Some standard types, similar to std::array and std::vector.
    using value_type = T;
    using size_type = size_t;
    using difference_type = ptrdiff_t;
    using reference = value_type&;
    using const_reference = const value_type&;
    using pointer = value_type*;
    using const_pointer = const value_type*;
    using iterator = pointer;
    using const_iterator = const_pointer;

    // static constexpr variable to be able to refer to the tuple size from the type,
    // from outside this class definition.
    static constexpr size_t tuple_size = N;

    using ScalarType = T;
    static const size_t dimension = N;

    base_vec() = default;
    constexpr base_vec(const base_vec<T, N>&) = default;

    constexpr explicit CUDA_CALLABLE base_vec(T value) : v{}
    {
        for (size_t i = 0; i < N; ++i)
        {
            v[i] = value;
        }
    }

    // NOTE: The static_cast is to avoid issues with other not being accepted as being the
    //       base class type, presumably because of the base class type conversion constructor
    //       being marked as explicit.
    template <typename OTHER_T>
    constexpr explicit CUDA_CALLABLE base_vec(const base_vec<OTHER_T, N>& other) : v{}
    {
        for (size_t i = 0; i < N; ++i)
        {
            v[i] = T(other[i]);
        }
    }

    template <typename OTHER_T0, typename OTHER_T1, typename... Args>
    constexpr CUDA_CALLABLE base_vec(OTHER_T0 a, OTHER_T1 b, Args... args) noexcept : v{}
    {
        v[0] = a;
        initHelper<1>(b, args...);
    }

    template <typename OTHER_T>
    CUDA_CALLABLE base_vec(const std::initializer_list<OTHER_T>& other) noexcept : v{}
    {
        CUDA_SAFE_ASSERT(other.size() == N);
        for (size_t i = 0; i < N && i < other.size(); ++i)
        {
            // NOTE: This intentionally doesn't have an explicit cast, so that
            //       the compiler will warn on invalid implicit casts, since this
            //       constructor isn't marked explicit.
            v[i] = other.begin()[i];
        }
    }

    // Access a single component of this base_vec.
    constexpr CUDA_CALLABLE T& operator[](size_t i) noexcept
    {
        // Ensure that this type is a POD type if T is a POD type.
        // This check is unrelated to this operator, but the static_assert
        // must be inside some function that is likely to be called.
        static_assert(std::is_pod<base_vec<T, N>>::value == std::is_pod<T>::value,
                      "base_vec<T,N> should be a POD type iff T is a POD type.");

        CUDA_SAFE_ASSERT(i < N);
        return v[i];
    }
    constexpr CUDA_CALLABLE const T& operator[](size_t i) const noexcept
    {
        CUDA_SAFE_ASSERT(i < N);
        return v[i];
    }

    // Get a pointer to the data of this tuple.
    constexpr CUDA_CALLABLE T* data() noexcept
    {
        return v;
    }
    constexpr CUDA_CALLABLE const T* data() const noexcept
    {
        return v;
    }

    static CUDA_CALLABLE base_vec<T, N> Axis(size_t axis)
    {
        base_vec<T, N> v(T(0));
        if (axis < dimension)
        {
            v[axis] = T(1);
        }
        return v;
    }

    const CUDA_CALLABLE T* GetArray() const
    {
        return data();
    }

    constexpr CUDA_CALLABLE T Dot(const base_vec<T, N>& other) const
    {
        T d = v[0] * other[0];
        for (size_t i = 1; i < N; ++i)
        {
            d += v[i] * other[i];
        }
        return d;
    }

    constexpr CUDA_CALLABLE T GetLengthSq() const
    {
        return this->Dot(*this);
    }

    CUDA_CALLABLE auto GetLength() const
    {
        return std::sqrt(GetLengthSq());
    }

    CUDA_CALLABLE auto Normalize()
    {
        using LengthT = typename std::conditional_t<std::is_same<half, T>::value, float, T>;
        const LengthT length2 = static_cast<LengthT>(GetLengthSq());
        decltype(std::sqrt(length2)) length;
        if (length2 != LengthT(0))
        {
            length = std::sqrt(length2);
            (*this) /= length;
        }
        else
        {
            // If close enough to zero that the length squared is zero,
            // make it exactly zero, for consistency.
            length = 0;
            (*this) *= 0;
        }
        return length;
    }

#ifndef DOXYGEN_BUILD
    CUDA_CALLABLE base_vec<T, N> GetNormalized() const
    {
        base_vec<T, N> copy(*this);
        copy.Normalize();
        return copy;
    }
#endif // DOXYGEN_BUILD

    // NOTE: This is the dot product, NOT the component-wise product!
    constexpr CUDA_CALLABLE T operator*(const base_vec<T, N>& other) const
    {
        return Dot(other);
    }

    constexpr CUDA_CALLABLE base_vec<T, N>& operator+=(const base_vec<T, N>& that) noexcept
    {
        for (size_t i = 0; i < N; ++i)
        {
            v[i] += that[i];
        }
        return *this;
    }

    constexpr CUDA_CALLABLE base_vec<T, N>& operator-=(const base_vec<T, N>& that) noexcept
    {
        for (size_t i = 0; i < N; ++i)
        {
            v[i] -= that[i];
        }
        return *this;
    }

    constexpr CUDA_CALLABLE base_vec<T, N>& operator*=(const T that) noexcept
    {
        for (size_t i = 0; i < N; ++i)
        {
            v[i] *= that;
        }
        return *this;
    }

    constexpr CUDA_CALLABLE base_vec<T, N>& operator/=(const T that) noexcept
    {
        for (size_t i = 0; i < N; ++i)
        {
            v[i] /= that;
        }
        return *this;
    }

#ifndef DOXYGEN_BUILD
    friend CUDA_CALLABLE base_vec<T, N> operator*(const T& multiplier, base_vec<T, N> rhs)
    {
        rhs *= multiplier;
        return rhs;
    }

    friend CUDA_CALLABLE base_vec<T, N> operator*(base_vec<T, N> lhs, const T& multiplier)
    {
        lhs *= multiplier;
        return lhs;
    }

    friend CUDA_CALLABLE base_vec<T, N> operator/(base_vec<T, N> lhs, const T& divisor)
    {
        lhs /= divisor;
        return lhs;
    }

    friend CUDA_CALLABLE base_vec<T, N> operator+(base_vec<T, N> lhs, const base_vec<T, N>& rhs)
    {
        lhs += rhs;
        return lhs;
    }

    friend CUDA_CALLABLE base_vec<T, N> operator-(base_vec<T, N> lhs, const base_vec<T, N>& rhs)
    {
        lhs -= rhs;
        return lhs;
    }
#endif

protected:
    T v[N];

private:
    template <size_t i, typename OTHER_T>
    constexpr CUDA_CALLABLE void initHelper(OTHER_T a)
    {
        static_assert(i == N - 1, "Variadic constructor of base_vec<T, N> requires N arguments");
        v[i] = T(a);
    }
    template <size_t i, typename OTHER_T, typename... Args>
    constexpr CUDA_CALLABLE void initHelper(OTHER_T a, Args... args)
    {
        v[i] = T(a);
        initHelper<i + 1>(args...);
    }
};

#ifndef DOXYGEN_BUILD
template<>
CUDA_CALLABLE inline auto base_vec<half, 2>::GetLength() const
{
    return std::sqrt(static_cast<float>(GetLengthSq()));
}

template<>
CUDA_CALLABLE inline auto base_vec<half, 3>::GetLength() const
{
    return std::sqrt(static_cast<float>(GetLengthSq()));
}

template<>
CUDA_CALLABLE inline auto base_vec<half, 4>::GetLength() const
{
    return std::sqrt(static_cast<float>(GetLengthSq()));
}
#endif // DOXYGEN_BUILD

template <typename T, size_t N>
CUDA_CALLABLE T GfDot(const base_vec<T, N>& a, const base_vec<T, N>& b)
{
    return a.Dot(b);
}

template <typename T, size_t N>
CUDA_CALLABLE auto GfGetLength(const base_vec<T, N>& v)
{
    return v.GetLength();
}

template <typename T, size_t N>
CUDA_CALLABLE auto GfNormalize(base_vec<T, N>* p)
{
    return p->Normalize();
}

template <typename T, size_t N>
CUDA_CALLABLE bool GfIsClose(const base_vec<T, N>& a, const base_vec<T, N>& b, double tolerance)
{
    auto distanceSq = (a - b).GetLengthSq();
    return distanceSq <= tolerance * tolerance;
}

template <typename T>
class vec2 : public base_vec<T, 2>
{
public:
    using base_type = base_vec<T, 2>;
    using this_type = vec2<T>;
    using base_type::operator[];
    using base_type::data;
    using base_type::operator+=;
    using base_type::operator-=;
    using base_type::operator*=;
    using base_type::operator/=;
    using base_type::GetArray;
    using base_type::GetLength;
    using base_type::GetLengthSq;
    using base_type::Normalize;

    using ScalarType = T;
    using base_type::dimension;

    vec2() = default;
    constexpr vec2(const vec2<T>&) = default;

    // Implicit conversion from base class, to avoid issues on that front.
    constexpr CUDA_CALLABLE vec2(const base_type& other) : base_type(other)
    {
    }

    constexpr explicit CUDA_CALLABLE vec2(T value) : base_type(value, value)
    {
    }

    constexpr CUDA_CALLABLE vec2(T v0, T v1) : base_type(v0, v1)
    {
    }

    template <typename OTHER_T>
    constexpr explicit CUDA_CALLABLE vec2(const OTHER_T* p) : base_type(p[0], p[1])
    {
    }

    template <typename OTHER_T>
    explicit CUDA_CALLABLE vec2(const vec2<OTHER_T>& other) : base_type(other)
    {
    }

    template <typename OTHER_T>
    explicit CUDA_CALLABLE vec2(const base_vec<OTHER_T, 2>& other) : base_type(other)
    {
    }

    template <typename OTHER_T>
    CUDA_CALLABLE vec2(const std::initializer_list<OTHER_T>& other) : base_type(other)
    {
    }

    static constexpr CUDA_CALLABLE vec2<T> XAxis()
    {
        return vec2<T>(T(1), T(0));
    }
    static constexpr CUDA_CALLABLE vec2<T> YAxis()
    {
        return vec2<T>(T(0), T(1));
    }

    static CUDA_CALLABLE vec2<T> Axis(size_t axis)
    {
        return base_type::Axis(axis);
    }

    CUDA_CALLABLE this_type& Set(T v0, T v1)
    {
        v[0] = v0;
        v[1] = v1;
        return *this;
    }

    CUDA_CALLABLE this_type& Set(T* p)
    {
        return Set(p[0], p[1]);
    }

    // NOTE: To avoid including Boost unless absolutely necessary, hash_value() is not defined here.

    template <typename OTHER_T>
    CUDA_CALLABLE bool operator==(const vec2<OTHER_T>& other) const
    {
        return (v[0] == other[0]) && (v[1] == other[1]);
    }
    template <typename OTHER_T>
    CUDA_CALLABLE bool operator!=(const vec2<OTHER_T>& other) const
    {
        return !(*this == other);
    }

    // Returns the portion of this that is parallel to unitVector.
    // NOTE: unitVector must have length 1 for this to produce a meaningful result.
    CUDA_CALLABLE this_type GetProjection(const this_type& unitVector) const
    {
        return unitVector * (this->Dot(unitVector));
    }

    // Returns the portion of this that is orthogonal to unitVector.
    // NOTE: unitVector must have length 1 for this to produce a meaningful result.
    CUDA_CALLABLE this_type GetComplement(const this_type& unitVector) const
    {
        return *this - GetProjection(unitVector);
    }

    CUDA_CALLABLE this_type GetNormalized() const
    {
        return base_type::GetNormalized();
    }

private:
    using base_type::v;
};

template <typename T>
CUDA_CALLABLE vec2<T> operator-(const vec2<T>& v)
{
    return vec2<T>(-v[0], -v[1]);
}

template <typename T>
CUDA_CALLABLE vec2<T> GfCompMult(const vec2<T>& a, const vec2<T>& b)
{
    return vec2<T>(a[0] * b[0], a[1] * b[1]);
}

template <typename T>
CUDA_CALLABLE vec2<T> GfCompDiv(const vec2<T>& a, const vec2<T>& b)
{
    return vec2<T>(a[0] / b[0], a[1] / b[1]);
}

template <typename T>
CUDA_CALLABLE vec2<T> GfGetNormalized(const vec2<T>& v)
{
    return v.GetNormalized();
}

template <typename T>
CUDA_CALLABLE vec2<T> GfGetProjection(const vec2<T>& v, const vec2<T>& unitVector)
{
    return v.GetProjection(unitVector);
}

template <typename T>
CUDA_CALLABLE vec2<T> GfGetComplement(const vec2<T>& v, const vec2<T>& unitVector)
{
    return v.GetComplement(unitVector);
}

template <typename T>
class vec3 : public base_vec<T, 3>
{
public:
    using base_type = base_vec<T, 3>;
    using this_type = vec3<T>;
    using base_type::operator[];
    using base_type::data;
    using base_type::operator+=;
    using base_type::operator-=;
    using base_type::operator*=;
    using base_type::operator/=;
    using base_type::GetArray;
    using base_type::GetLength;
    using base_type::GetLengthSq;
    using base_type::Normalize;

    using ScalarType = T;
    using base_type::dimension;

    vec3() = default;
    constexpr vec3(const this_type&) = default;

    // Implicit conversion from base class, to avoid issues on that front.
    constexpr CUDA_CALLABLE vec3(const base_type& other) : base_type(other)
    {
    }

    constexpr explicit CUDA_CALLABLE vec3(T value) : base_type(value, value, value)
    {
    }

    constexpr CUDA_CALLABLE vec3(T v0, T v1, T v2) : base_type(v0, v1, v2)
    {
    }

    template <typename OTHER_T>
    constexpr explicit CUDA_CALLABLE vec3(const OTHER_T* p) : base_type(p[0], p[1], p[2])
    {
    }

    template <typename OTHER_T>
    explicit CUDA_CALLABLE vec3(const vec3<OTHER_T>& other) : base_type(other)
    {
    }

    template <typename OTHER_T>
    explicit CUDA_CALLABLE vec3(const base_vec<OTHER_T, 3>& other) : base_type(other)
    {
    }

    template <typename OTHER_T>
    CUDA_CALLABLE vec3(const std::initializer_list<OTHER_T>& other) : base_type(other)
    {
    }

    static constexpr CUDA_CALLABLE vec3<T> XAxis()
    {
        return vec3<T>(T(1), T(0), T(0));
    }
    static constexpr CUDA_CALLABLE vec3<T> YAxis()
    {
        return vec3<T>(T(0), T(1), T(0));
    }
    static constexpr CUDA_CALLABLE vec3<T> ZAxis()
    {
        return vec3<T>(T(0), T(0), T(1));
    }

    static CUDA_CALLABLE vec3<T> Axis(size_t axis)
    {
        return base_type::Axis(axis);
    }

    CUDA_CALLABLE this_type& Set(T v0, T v1, T v2)
    {
        v[0] = v0;
        v[1] = v1;
        v[2] = v2;
        return *this;
    }

    CUDA_CALLABLE this_type& Set(T* p)
    {
        return Set(p[0], p[1], p[2]);
    }

    // NOTE: To avoid including Boost unless absolutely necessary, hash_value() is not defined here.

    template <typename OTHER_T>
    CUDA_CALLABLE bool operator==(const vec3<OTHER_T>& other) const
    {
        return (v[0] == other[0]) && (v[1] == other[1]) && (v[2] == other[2]);
    }
    template <typename OTHER_T>
    CUDA_CALLABLE bool operator!=(const vec3<OTHER_T>& other) const
    {
        return !(*this == other);
    }

    // Returns the portion of this that is parallel to unitVector.
    // NOTE: unitVector must have length 1 for this to produce a meaningful result.
    CUDA_CALLABLE this_type GetProjection(const this_type& unitVector) const
    {
        return unitVector * (this->Dot(unitVector));
    }

    // Returns the portion of this that is orthogonal to unitVector.
    // NOTE: unitVector must have length 1 for this to produce a meaningful result.
    CUDA_CALLABLE this_type GetComplement(const this_type& unitVector) const
    {
        return *this - GetProjection(unitVector);
    }

    CUDA_CALLABLE this_type GetNormalized() const
    {
        return base_type::GetNormalized();
    }

    static CUDA_CALLABLE bool OrthogonalizeBasis(vec3<T>* pa, vec3<T>* pb, vec3<T>* pc, bool normalize = true);

    CUDA_CALLABLE void BuildOrthonormalFrame(vec3<T>* v1, vec3<T>* v2, float eps = 1e-10) const;

private:
    using base_type::v;
};

template <typename T>
CUDA_CALLABLE vec3<T> operator-(const vec3<T>& v)
{
    return vec3<T>(-v[0], -v[1], -v[2]);
}

template <typename T>
CUDA_CALLABLE vec3<T> GfCompMult(const vec3<T>& a, const vec3<T>& b)
{
    return vec3<T>(a[0] * b[0], a[1] * b[1], a[2] * b[2]);
}

template <typename T>
CUDA_CALLABLE vec3<T> GfCompDiv(const vec3<T>& a, const vec3<T>& b)
{
    return vec3<T>(a[0] / b[0], a[1] / b[1], a[2] / b[2]);
}

template <typename T>
CUDA_CALLABLE vec3<T> GfGetNormalized(const vec3<T>& v)
{
    return v.GetNormalized();
}

template <typename T>
CUDA_CALLABLE vec3<T> GfGetProjection(const vec3<T>& v, const vec3<T>& unitVector)
{
    return v.GetProjection(unitVector);
}

template <typename T>
CUDA_CALLABLE vec3<T> GfGetComplement(const vec3<T>& v, const vec3<T>& unitVector)
{
    return v.GetComplement(unitVector);
}

template <typename T>
CUDA_CALLABLE vec3<T> GfRadiansToDegrees(const vec3<T>& radians)
{
    return radians * T(180.0 / M_PI);
}

template <typename T>
CUDA_CALLABLE vec3<T> GfDegreesToRadians(const vec3<T>& degrees)
{
    return degrees * T(M_PI / 180.0);
}

template <typename T>
CUDA_CALLABLE vec3<T> GfCross(const base_vec<T, 3>& a, const base_vec<T, 3>& b)
{
    return vec3<T>(a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]);
}

// NOTE: This is the cross product, NOT the XOR operator!
template <typename T>
CUDA_CALLABLE vec3<T> operator^(const vec3<T>& a, const vec3<T>& b)
{
    return GfCross(a, b);
}

template <typename T>
class vec4 : public base_vec<T, 4>
{
public:
    using base_type = base_vec<T, 4>;
    using this_type = vec4<T>;
    using base_type::operator[];
    using base_type::data;
    using base_type::operator+=;
    using base_type::operator-=;
    using base_type::operator*=;
    using base_type::operator/=;
    using base_type::GetArray;
    using base_type::GetLength;
    using base_type::GetLengthSq;
    using base_type::Normalize;

    using ScalarType = T;
    using base_type::dimension;

    vec4() = default;
    constexpr vec4(const vec4<T>&) = default;

    // Implicit conversion from base class, to avoid issues on that front.
    constexpr CUDA_CALLABLE vec4(const base_type& other) : base_type(other)
    {
    }

    constexpr explicit CUDA_CALLABLE vec4(T value) : base_type(value, value, value, value)
    {
    }

    constexpr CUDA_CALLABLE vec4(T v0, T v1, T v2, T v3) : base_type(v0, v1, v2, v3)
    {
    }

    template <typename OTHER_T>
    constexpr explicit CUDA_CALLABLE vec4(const OTHER_T* p) : base_type(p[0], p[1], p[2], p[3])
    {
    }

    template <typename OTHER_T>
    explicit CUDA_CALLABLE vec4(const vec4<OTHER_T>& other) : base_type(other)
    {
    }

    template <typename OTHER_T>
    explicit CUDA_CALLABLE vec4(const base_vec<OTHER_T, 4>& other) : base_type(other)
    {
    }

    template <typename OTHER_T>
    CUDA_CALLABLE vec4(const std::initializer_list<OTHER_T>& other) : base_type(other)
    {
    }

    static constexpr CUDA_CALLABLE vec4<T> XAxis()
    {
        return vec4<T>(T(1), T(0), T(0), T(0));
    }
    static constexpr CUDA_CALLABLE vec4<T> YAxis()
    {
        return vec4<T>(T(0), T(1), T(0), T(0));
    }
    static constexpr CUDA_CALLABLE vec4<T> ZAxis()
    {
        return vec4<T>(T(0), T(0), T(1), T(0));
    }
    static constexpr CUDA_CALLABLE vec4<T> WAxis()
    {
        return vec4<T>(T(0), T(0), T(0), T(1));
    }

    static CUDA_CALLABLE vec4<T> Axis(size_t axis)
    {
        return base_type::Axis(axis);
    }

    CUDA_CALLABLE this_type& Set(T v0, T v1, T v2, T v3)
    {
        v[0] = v0;
        v[1] = v1;
        v[2] = v2;
        v[3] = v3;
        return *this;
    }

    CUDA_CALLABLE this_type& Set(T* p)
    {
        return Set(p[0], p[1], p[2], p[3]);
    }

    // NOTE: To avoid including Boost unless absolutely necessary, hash_value() is not defined here.

    template <typename OTHER_T>
    CUDA_CALLABLE bool operator==(const vec4<OTHER_T>& other) const
    {
        return (v[0] == other[0]) && (v[1] == other[1]) && (v[2] == other[2]) && (v[3] == other[3]);
    }
    template <typename OTHER_T>
    CUDA_CALLABLE bool operator!=(const vec4<OTHER_T>& other) const
    {
        return !(*this == other);
    }

    // Returns the portion of this that is parallel to unitVector.
    // NOTE: unitVector must have length 1 for this to produce a meaningful result.
    CUDA_CALLABLE this_type GetProjection(const this_type& unitVector) const
    {
        return unitVector * (this->Dot(unitVector));
    }

    // Returns the portion of this that is orthogonal to unitVector.
    // NOTE: unitVector must have length 1 for this to produce a meaningful result.
    CUDA_CALLABLE this_type GetComplement(const this_type& unitVector) const
    {
        return *this - GetProjection(unitVector);
    }

    CUDA_CALLABLE this_type GetNormalized() const
    {
        return base_type::GetNormalized();
    }

    CUDA_CALLABLE vec3<T> Project() const
    {
        T w = v[3];
        w = (w != T(0)) ? T(1) / w : T(1);
        return w * vec3<T>(v[0], v[1], v[2]);
    }

private:
    using base_type::v;
};

template <typename T>
CUDA_CALLABLE vec4<T> operator-(const vec4<T>& v)
{
    return vec4<T>(-v[0], -v[1], -v[2], -v[3]);
}

template <typename T>
CUDA_CALLABLE vec4<T> GfCompMult(const vec4<T>& a, const vec4<T>& b)
{
    return vec4<T>(a[0] * b[0], a[1] * b[1], a[2] * b[2], a[3] * b[3]);
}

template <typename T>
CUDA_CALLABLE vec4<T> GfCompDiv(const vec4<T>& a, const vec4<T>& b)
{
    return vec4<T>(a[0] / b[0], a[1] / b[1], a[2] / b[2], a[3] / b[3]);
}

template <typename T>
CUDA_CALLABLE vec4<T> GfGetNormalized(const vec4<T>& v)
{
    return v.GetNormalized();
}

template <typename T>
CUDA_CALLABLE vec4<T> GfGetProjection(const vec4<T>& v, const vec4<T>& unitVector)
{
    return v.GetProjection(unitVector);
}

template <typename T>
CUDA_CALLABLE vec4<T> GfGetComplement(const vec4<T>& v, const vec4<T>& unitVector)
{
    return v.GetComplement(unitVector);
}

template <typename T>
CUDA_CALLABLE bool GfOrthogonalizeBasis(vec3<T>* pa, vec3<T>* pb, vec3<T>* pc, bool normalize = true)
{
    // Compute using at least single-precision, to avoid issues with half-precision floating-point values.
    using S = typename std::conditional<std::is_same<T, float>::value || std::is_same<T, double>::value, T, float>::type;
    vec3<S> a(pa->GetNormalized());
    vec3<S> b(pb->GetNormalized());
    vec3<S> c(pc->GetNormalized());

    if (normalize)
    {
        pa->Normalize();
        pb->Normalize();
        pc->Normalize();
    }

    // This is an arbitrary tolerance that's about 8 ulps in single-precision floating-point.
    const double tolerance = 4.8e-7;
    const double toleranceSq = tolerance * tolerance;

    // This max iteration count is also somewhat arbitrary.
    const size_t maxIterations = 32;
    size_t iteration;
    for (iteration = 0; iteration < maxIterations; ++iteration)
    {
        vec3<S> newA(a.GetComplement(b));
        newA = newA.GetComplement(c);
        vec3<S> newB(b.GetComplement(c));
        newB = newB.GetComplement(a);
        vec3<S> newC(c.GetComplement(a));
        newC = newC.GetComplement(b);

        if (iteration == 0)
        {
            // Should only need to check for coplanar vectors on the first iteration.
            auto lengthSqA = newA.GetLengthSq();
            auto lengthSqB = newB.GetLengthSq();
            auto lengthSqC = newC.GetLengthSq();
            // The unusual condition form is to catch NaNs.
            if (!(lengthSqA >= toleranceSq) || !(lengthSqB >= toleranceSq) || !(lengthSqC >= toleranceSq))
            {
                return false;
            }
        }

        // Only move a half-step at a time, to avoid instability and improve convergence.
        newA = S(0.5) * (a + newA);
        newB = S(0.5) * (b + newB);
        newC = S(0.5) * (c + newC);

        if (normalize)
        {
            newA.Normalize();
            newB.Normalize();
            newC.Normalize();
        }

        S changeSq = (newA - a).GetLengthSq() + (newB - b).GetLengthSq() + (newC - c).GetLengthSq();

        if (changeSq < toleranceSq)
        {
            break;
        }

        a = newA;
        b = newB;
        c = newC;

        *pa = vec3<T>(a);
        *pb = vec3<T>(b);
        *pc = vec3<T>(c);

        if (!normalize)
        {
            a.Normalize();
            b.Normalize();
            c.Normalize();
        }
    }

    return iteration < maxIterations;
}

template <typename T>
CUDA_CALLABLE void GfBuildOrthonormalFrame(const vec3<T>& v0, vec3<T>* v1, vec3<T>* v2, float eps)
{
    float length = v0.GetLength();

    if (length == 0)
    {
        *v1 = vec3<T>(0);
        *v2 = vec3<T>(0);
    }
    else
    {
        vec3<T> unitDir = v0 / length;
        *v1 = GfCross(vec3<T>::XAxis(), unitDir);

        if (v1->GetLengthSq() < 1e-8)
        {
            *v1 = GfCross(vec3<T>::YAxis(), unitDir);
        }

        GfNormalize(v1);
        *v2 = GfCross(unitDir, *v1);

        if (length < eps)
        {
            double desiredLen = length / eps;
            *v1 *= desiredLen;
            *v2 *= desiredLen;
        }
    }
}

template <typename T>
CUDA_CALLABLE bool vec3<T>::OrthogonalizeBasis(vec3<T>* pa, vec3<T>* pb, vec3<T>* pc, bool normalize)
{
    return GfOrthogonalizeBasis(pa, pb, pc, normalize);
}

template <typename T>
CUDA_CALLABLE void vec3<T>::BuildOrthonormalFrame(vec3<T>* v1, vec3<T>* v2, float eps) const
{
    return GfBuildOrthonormalFrame(*this, v1, v2, eps);
}

template <typename T, size_t N>
CUDA_CALLABLE base_vec<T, N> GfSlerp(const base_vec<T, N>& a, const base_vec<T, N>& b, double t)
{
    const base_vec<double, N> ad(a);
    base_vec<double, N> bd(b);
    double d = ad.Dot(bd);

    const double arbitraryThreshold = (1.0 - 1e-5);
    if (d < arbitraryThreshold)
    {
        const double angle = t * acos(d);
        base_vec<double, N> complement;
        if (d > -arbitraryThreshold)
        {
            // Common case: large enough angle between a and b for stable angle from acos and stable complement
            complement = bd - d * ad;
        }
        else
        {
            // Angle is almost 180 degrees, so pick an arbitrary vector perpendicular to ad
            size_t minAxis = 0;
            for (size_t axis = 1; axis < N; ++axis)
                minAxis = (abs(ad[axis]) < abs(ad[minAxis])) ? axis : minAxis;
            base_vec<double, N> complement(0.0);
            complement[minAxis] = 1;
            complement -= ad.Dot(complement) * ad;
        }
        complement.Normalize();
        return base_vec<T, N>(cos(angle) * ad + sin(angle) * complement);
    }

    // For small angles, just linearly interpolate.
    return base_vec<T, N>(ad + t * (bd - ad));
}

template <typename T>
CUDA_CALLABLE vec2<T> GfSlerp(const vec2<T>& a, const vec2<T>& b, double t)
{
    return vec2<T>(GfSlerp((const base_vec<T, 2>&)a, (const base_vec<T, 2>&)b, t));
}

template <typename T>
CUDA_CALLABLE vec3<T> GfSlerp(const vec3<T>& a, const vec3<T>& b, double t)
{
    const vec3<double> ad(a);
    vec3<double> bd(b);
    double d = ad.Dot(bd);

    const double arbitraryThreshold = (1.0 - 1e-5);
    if (d < arbitraryThreshold)
    {
        const double angle = t * acos(d);
        vec3<double> complement;
        if (d > -arbitraryThreshold)
        {
            // Common case: large enough angle between a and b for stable angle from acos and stable complement
            complement = bd - d * ad;
        }
        else
        {
            // Angle is almost 180 degrees, so pick an arbitrary vector perpendicular to ad
            vec3<double> ofa(0);
            vec3<double> unit = ad / ad.GetLength();

            vec3<double> xaxis(0);
            xaxis[0] = 1;
            ofa = GfCross(xaxis, unit);
            if (ofa.GetLength() < 1e-8)
            {
                vec3<double> yaxis(0);
                yaxis[1] = 1;
                ofa = GfCross(yaxis, unit);
            }

            ofa.Normalize();

            return vec3<T>(cos(t * M_PI) * ad + sin(t * M_PI) * ofa);
        }
        complement.Normalize();
        return vec3<T>(cos(angle) * ad + sin(angle) * complement);
    }

    // For small angles, just linearly interpolate.
    return vec3<T>(ad + t * (bd - ad));
}

template <typename T>
CUDA_CALLABLE vec4<T> GfSlerp(const vec4<T>& a, const vec4<T>& b, double t)
{
    return vec4<T>(GfSlerp((const base_vec<T, 4>&)a, (const base_vec<T, 4>&)b, t));
}

// Different parameter order, for compatibility.
template <typename VECTOR_T>
CUDA_CALLABLE VECTOR_T GfSlerp(double t, const VECTOR_T& a, const VECTOR_T& b)
{
    return GfSlerp(a, b, t);
}

using vec2h = vec2<half>;
using vec2f = vec2<float>;
using vec2d = vec2<double>;
using vec2i = vec2<int>;

using vec3h = vec3<half>;
using vec3f = vec3<float>;
using vec3d = vec3<double>;
using vec3i = vec3<int>;

using vec4h = vec4<half>;
using vec4f = vec4<float>;
using vec4d = vec4<double>;
using vec4i = vec4<int>;

}
}
}

namespace usdrt
{

using omni::math::linalg::GfBuildOrthonormalFrame;
using omni::math::linalg::GfCompDiv;
using omni::math::linalg::GfCompMult;
using omni::math::linalg::GfCross;
using omni::math::linalg::GfDot;
using omni::math::linalg::GfGetComplement;
using omni::math::linalg::GfGetLength;
using omni::math::linalg::GfGetNormalized;
using omni::math::linalg::GfGetProjection;
using omni::math::linalg::GfIsClose;
using omni::math::linalg::GfNormalize;
using omni::math::linalg::GfOrthogonalizeBasis;
using omni::math::linalg::GfSlerp;

using GfVec2d = omni::math::linalg::vec2<double>;
using GfVec2f = omni::math::linalg::vec2<float>;
using GfVec2h = omni::math::linalg::vec2<omni::math::linalg::half>;
using GfVec2i = omni::math::linalg::vec2<int>;

using GfVec3d = omni::math::linalg::vec3<double>;
using GfVec3f = omni::math::linalg::vec3<float>;
using GfVec3h = omni::math::linalg::vec3<omni::math::linalg::half>;
using GfVec3i = omni::math::linalg::vec3<int>;

using GfVec4d = omni::math::linalg::vec4<double>;
using GfVec4f = omni::math::linalg::vec4<float>;
using GfVec4h = omni::math::linalg::vec4<omni::math::linalg::half>;
using GfVec4i = omni::math::linalg::vec4<int>;

template <>
struct GfIsGfVec<GfVec2d>
{
    static const bool value = true;
};

template <>
struct GfIsGfVec<GfVec2f>
{
    static const bool value = true;
};

template <>
struct GfIsGfVec<GfVec2h>
{
    static const bool value = true;
};

template <>
struct GfIsGfVec<GfVec2i>
{
    static const bool value = true;
};

template <>
struct GfIsGfVec<GfVec3d>
{
    static const bool value = true;
};

template <>
struct GfIsGfVec<GfVec3f>
{
    static const bool value = true;
};

template <>
struct GfIsGfVec<GfVec3h>
{
    static const bool value = true;
};

template <>
struct GfIsGfVec<GfVec3i>
{
    static const bool value = true;
};

template <>
struct GfIsGfVec<GfVec4d>
{
    static const bool value = true;
};

template <>
struct GfIsGfVec<GfVec4f>
{
    static const bool value = true;
};

template <>
struct GfIsGfVec<GfVec4h>
{
    static const bool value = true;
};

template <>
struct GfIsGfVec<GfVec4i>
{
    static const bool value = true;
};

}
