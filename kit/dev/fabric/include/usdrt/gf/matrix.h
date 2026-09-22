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

#include <usdrt/gf/defines.h>
#include <usdrt/gf/quat.h>
#include <usdrt/gf/vec.h>

#include <initializer_list>

namespace usdrt
{
class GfRotation;
}

namespace omni
{
namespace math
{
namespace linalg
{

template <typename T, size_t N>
class base_matrix
{
public:
    using ScalarType = T;
    static const size_t numRows = N;
    static const size_t numColumns = N;

    base_matrix() = default;
    constexpr base_matrix(const base_matrix<T, N>&) = default;
    constexpr base_matrix<T, N>& operator=(const base_matrix<T, N>&) = default;

    // NOTE: Hopefully the compiler can identify that the initializer for v is redundant,
    //       since this constructor is quite useful for constexpr cases.
    explicit constexpr CUDA_CALLABLE base_matrix(const T m[N][N]) : v{}
    {
        for (size_t i = 0; i < N; ++i)
        {
            for (size_t j = 0; j < N; ++j)
            {
                v[i][j] = m[i][j];
            }
        }
    }

    explicit CUDA_CALLABLE base_matrix(T scalar)
    {
        SetDiagonal(scalar);
    }
    explicit CUDA_CALLABLE base_matrix(const base_vec<T, N>& diagonal)
    {
        SetDiagonal(diagonal);
    }

    template <typename OTHER_T>
    explicit CUDA_CALLABLE base_matrix(const base_matrix<OTHER_T, N>& other)
    {
        for (size_t i = 0; i < N; ++i)
        {
            for (size_t j = 0; j < N; ++j)
            {
                v[i][j] = T(other[i][j]);
            }
        }
    }

    template <typename OTHER_T>
    CUDA_CALLABLE base_matrix(const std::initializer_list<std::initializer_list<OTHER_T>>& other) : v{}
    {
        CUDA_SAFE_ASSERT(other.size() == N);
        for (size_t i = 0; i < N && i < other.size(); ++i)
        {
            CUDA_SAFE_ASSERT(other.begin()[i].size() == N);
            for (size_t j = 0; j < N && j < other.begin()[i].size(); ++j)
            {
                // NOTE: This intentionally doesn't have an explicit cast, so that
                //       the compiler will warn on invalid implicit casts, since this
                //       constructor isn't marked explicit.
                v[i][j] = other.begin()[i].begin()[j];
            }
        }
    }

    CUDA_CALLABLE void SetRow(size_t rowIndex, const base_vec<T, N>& rowValues)
    {
        for (size_t col = 0; col < N; ++col)
        {
            v[rowIndex][col] = rowValues[col];
        }
    }

    CUDA_CALLABLE void SetColumn(size_t colIndex, const base_vec<T, N>& colValues)
    {
        for (size_t row = 0; row < N; ++row)
        {
            v[row][colIndex] = colValues[row];
        }
    }

    CUDA_CALLABLE base_vec<T, N> GetRow(size_t rowIndex) const
    {
        base_vec<T, N> rowValues;
        for (size_t col = 0; col < N; ++col)
        {
            rowValues[col] = v[rowIndex][col];
        }
        return rowValues;
    }

    CUDA_CALLABLE base_vec<T, N> GetColumn(size_t colIndex) const
    {
        base_vec<T, N> colValues;
        for (size_t row = 0; row < N; ++row)
        {
            colValues[row] = v[row][colIndex];
        }
        return colValues;
    }

    CUDA_CALLABLE base_matrix<T, N>& Set(const T m[N][N])
    {
        for (size_t i = 0; i < N; ++i)
        {
            for (size_t j = 0; j < N; ++j)
            {
                v[i][j] = m[i][j];
            }
        }
        return *this;
    }

    CUDA_CALLABLE base_matrix<T, N>& SetIdentity()
    {
        return SetDiagonal(T(1));
    }

    CUDA_CALLABLE base_matrix<T, N>& SetZero()
    {
        return SetDiagonal(T(0));
    }

    CUDA_CALLABLE base_matrix<T, N>& SetDiagonal(T scalar)
    {
        for (size_t i = 0; i < N; ++i)
        {
            for (size_t j = 0; j < N; ++j)
            {
                v[i][j] = (i == j) ? scalar : T(0);
            }
        }
        return *this;
    }

    CUDA_CALLABLE base_matrix<T, N>& SetDiagonal(const base_vec<T, N>& diagonal)
    {
        for (size_t i = 0; i < N; ++i)
        {
            for (size_t j = 0; j < N; ++j)
            {
                v[i][j] = (i == j) ? diagonal[i] : T(0);
            }
        }
        return *this;
    }

    CUDA_CALLABLE T* Get(T m[N][N]) const
    {
        for (size_t i = 0; i < N; ++i)
        {
            for (size_t j = 0; j < N; ++j)
            {
                m[i][j] = v[i][j];
            }
        }
        return &m[0][0];
    }

    CUDA_CALLABLE T* data()
    {
        return &v[0][0];
    }

    CUDA_CALLABLE const T* data() const
    {
        return &v[0][0];
    }

    CUDA_CALLABLE T* GetArray()
    {
        return &v[0][0];
    }
    CUDA_CALLABLE const T* GetArray() const
    {
        return &v[0][0];
    }

    CUDA_CALLABLE T* operator[](size_t row)
    {
        return v[row];
    }
    CUDA_CALLABLE const T* operator[](size_t row) const
    {
        return v[row];
    }

    // NOTE: To avoid including Boost unless absolutely necessary, hash_value() is not defined here.

    CUDA_CALLABLE bool operator==(const base_matrix<T, N>& other) const
    {
        for (size_t i = 0; i < N; ++i)
        {
            for (size_t j = 0; j < N; ++j)
            {
                if (v[i][j] != other[i][j])
                {
                    return false;
                }
            }
        }
        return true;
    }
    CUDA_CALLABLE bool operator!=(const base_matrix<T, N>& other) const
    {
        return !(*this == other);
    }

    template <typename OTHER_T>
    CUDA_CALLABLE bool operator==(const base_matrix<OTHER_T, N>& other) const
    {
        for (size_t i = 0; i < N; ++i)
        {
            for (size_t j = 0; j < N; ++j)
            {
                if (v[i][j] != other[i][j])
                {
                    return false;
                }
            }
        }
        return true;
    }
    template <typename OTHER_T>
    CUDA_CALLABLE bool operator!=(const base_matrix<OTHER_T, N>& other) const
    {
        return !(*this == other);
    }

#ifndef DOXYGEN_BUILD
    CUDA_CALLABLE base_matrix<T, N> GetTranspose() const
    {
        base_matrix<T, N> result;
        for (size_t i = 0; i < N; ++i)
        {
            for (size_t j = 0; j < N; ++j)
            {
                result[i][j] = v[j][i];
            }
        }
        return result;
    }
#endif // DOXYGEN_BUILD

    CUDA_CALLABLE base_matrix<T, N>& operator*=(const base_matrix<T, N>& other)
    {
        T result[N][N];
        for (size_t row = 0; row < N; ++row)
        {
            for (size_t col = 0; col < N; ++col)
            {
                T sum = v[row][0] * other[0][col];
                for (size_t i = 1; i < N; ++i)
                {
                    sum += v[row][i] * other[i][col];
                }
                result[row][col] = sum;
            }
        }
        Set(result);
        return *this;
    }

    CUDA_CALLABLE base_matrix<T, N>& operator*=(T scalar)
    {
        for (size_t row = 0; row < N; ++row)
        {
            for (size_t col = 0; col < N; ++col)
            {
                v[row][col] *= scalar;
            }
        }
        return *this;
    }

#ifndef DOXYGEN_BUILD
    friend CUDA_CALLABLE base_matrix<T, N> operator*(const base_matrix<T, N>& matrix, T scalar)
    {
        base_matrix<T, N> result;
        for (size_t row = 0; row < N; ++row)
        {
            for (size_t col = 0; col < N; ++col)
            {
                result[row][col] = matrix[row][col] * scalar;
            }
        }
        return result;
    }

    friend CUDA_CALLABLE base_matrix<T, N> operator*(T scalar, const base_matrix<T, N>& matrix)
    {
        return matrix * scalar;
    }
#endif

    CUDA_CALLABLE base_matrix<T, N>& operator+=(const base_matrix<T, N>& other)
    {
        for (size_t row = 0; row < N; ++row)
        {
            for (size_t col = 0; col < N; ++col)
            {
                v[row][col] += other[row][col];
            }
        }
        return *this;
    }

    CUDA_CALLABLE base_matrix<T, N>& operator-=(const base_matrix<T, N>& other)
    {
        for (size_t row = 0; row < N; ++row)
        {
            for (size_t col = 0; col < N; ++col)
            {
                v[row][col] -= other[row][col];
            }
        }
        return *this;
    }

#ifndef DOXYGEN_BUILD
    CUDA_CALLABLE base_matrix<T, N> operator-() const
    {
        base_matrix<T, N> result;
        for (size_t row = 0; row < N; ++row)
        {
            for (size_t col = 0; col < N; ++col)
            {
                result[row][col] = -v[row][col];
            }
        }
        return result;
    }
#endif // DOXYGEN_BUILD

#ifndef DOXYGEN_BUILD
    friend CUDA_CALLABLE base_matrix<T, N> operator+(const base_matrix<T, N>& a, const base_matrix<T, N>& b)
    {
        base_matrix<T, N> result;
        for (size_t row = 0; row < N; ++row)
        {
            for (size_t col = 0; col < N; ++col)
            {
                result[row][col] = a[row][col] + b[row][col];
            }
        }
        return result;
    }

    friend CUDA_CALLABLE base_matrix<T, N> operator-(const base_matrix<T, N>& a, const base_matrix<T, N>& b)
    {
        base_matrix<T, N> result;
        for (size_t row = 0; row < N; ++row)
        {
            for (size_t col = 0; col < N; ++col)
            {
                result[row][col] = a[row][col] - b[row][col];
            }
        }
        return result;
    }

    friend CUDA_CALLABLE base_matrix<T, N> operator*(const base_matrix<T, N>& a, const base_matrix<T, N>& b)
    {
        base_matrix<T, N> result(a);
        result *= b;
        return result;
    }

    // Matrix times column vector
    friend CUDA_CALLABLE base_vec<T, N> operator*(const base_matrix<T, N>& matrix, const base_vec<T, N>& vec)
    {
        base_vec<T, N> result;
        for (size_t row = 0; row < N; ++row)
        {
            T sum = matrix[row][0] * vec[0];
            for (size_t col = 1; col < N; ++col)
            {
                sum += matrix[row][col] * vec[col];
            }
            result[row] = sum;
        }
        return result;
    }

    // Row vector times matrix
    friend CUDA_CALLABLE base_vec<T, N> operator*(const base_vec<T, N>& vec, const base_matrix<T, N>& matrix)
    {
        base_vec<T, N> result;
        T scale = vec[0];
        for (size_t col = 0; col < N; ++col)
        {
            result[col] = matrix[0][col] * scale;
        }
        for (size_t row = 1; row < N; ++row)
        {
            T scale = vec[row];
            for (size_t col = 0; col < N; ++col)
            {
                result[col] += matrix[row][col] * scale;
            }
        }
        return result;
    }

    // Matrix times column vector
    template <typename OTHER_T>
    friend CUDA_CALLABLE base_vec<OTHER_T, N> operator*(const base_matrix<T, N>& matrix, const base_vec<OTHER_T, N>& vec)
    {
        base_vec<OTHER_T, N> result;
        for (size_t row = 0; row < N; ++row)
        {
            OTHER_T sum = matrix[row][0] * vec[0];
            for (size_t col = 1; col < N; ++col)
            {
                sum += matrix[row][col] * vec[col];
            }
            result[row] = sum;
        }
        return result;
    }

    // Row vector times matrix
    template <typename OTHER_T>
    friend CUDA_CALLABLE base_vec<OTHER_T, N> operator*(const base_vec<OTHER_T, N>& vec, const base_matrix<T, N>& matrix)
    {
        base_vec<OTHER_T, N> result;
        OTHER_T scale = vec[0];
        for (size_t col = 0; col < N; ++col)
        {
            result[col] = matrix[0][col] * scale;
        }
        for (size_t row = 1; row < N; ++row)
        {
            OTHER_T scale = vec[row];
            for (size_t col = 0; col < N; ++col)
            {
                result[col] += matrix[row][col] * scale;
            }
        }
        return result;
    }
#endif

protected:
    T v[N][N];
};

template <typename T, size_t N>
CUDA_CALLABLE bool GfIsClose(const base_matrix<T, N>& a, const base_matrix<T, N>& b, double tolerance)
{
    for (size_t row = 0; row < N; ++row)
    {
        for (size_t col = 0; col < N; ++col)
        {
            const T diff = a[row][col] - b[row][col];
            const T absDiff = (diff < T(0)) ? -diff : diff;
            // NOTE: This condition looks weird, but it's so that NaN values in
            //       either matrix will yield false.
            if (!(absDiff <= tolerance))
            {
                return false;
            }
        }
    }
    return true;
}

template <typename T>
class matrix2 : public base_matrix<T, 2>
{
public:
    using base_type = base_matrix<T, 2>;
    using this_type = matrix2<T>;
    using base_matrix<T, 2>::base_matrix;
    using base_type::operator[];
    using base_type::operator==;
    using base_type::operator!=;
    using base_type::data;
    using base_type::Get;
    using base_type::GetArray;
    using base_type::SetColumn;
    using base_type::SetRow;

    using ScalarType = T;
    using base_type::numColumns;
    using base_type::numRows;

    matrix2() = default;
    constexpr matrix2(const this_type&) = default;
    constexpr this_type& operator=(const this_type&) = default;

    // Implicit conversion from base_type
    CUDA_CALLABLE matrix2(const base_type& other) : base_type(other)
    {
    }

    template <typename OTHER_T>
    explicit CUDA_CALLABLE matrix2(const matrix2<OTHER_T>& other)
        : base_type(static_cast<const base_matrix<OTHER_T, numRows>&>(other))
    {
    }

    CUDA_CALLABLE matrix2(T v00, T v01, T v10, T v11)
    {
        Set(v00, v01, v10, v11);
    }

    CUDA_CALLABLE this_type& Set(const T m[numRows][numColumns])
    {
        base_type::Set(m);
        return *this;
    }

    CUDA_CALLABLE this_type& Set(T v00, T v01, T v10, T v11)
    {
        T v[2][2] = { { v00, v01 }, { v10, v11 } };
        return Set(v);
    }

    CUDA_CALLABLE this_type& SetIdentity()
    {
        base_type::SetIdentity();
        return *this;
    }

    CUDA_CALLABLE this_type& SetZero()
    {
        base_type::SetZero();
        return *this;
    }

    CUDA_CALLABLE this_type& SetDiagonal(T scalar)
    {
        base_type::SetDiagonal(scalar);
        return *this;
    }

    CUDA_CALLABLE this_type& SetDiagonal(const base_vec<T, numRows>& diagonal)
    {
        base_type::SetDiagonal(diagonal);
        return *this;
    }

    CUDA_CALLABLE this_type GetTranspose() const
    {
        return this_type(base_type::GetTranspose());
    }

    CUDA_CALLABLE this_type GetInverse(T* det = nullptr, T epsilon = T(0)) const
    {
        T determinant = GetDeterminant();
        if (det != nullptr)
        {
            *det = determinant;
        }

        T absDeterminant = (determinant < 0) ? -determinant : determinant;
        // This unusual writing of the condition should catch NaNs.
        if (!(absDeterminant > epsilon))
        {
            // Return the zero matrix, instead of a huge matrix,
            // so that multiplying by this is less likely to be catastrophic.
            return this_type(T(0));
        }

        T inverse[2][2] = { { v[1][1] / determinant, -v[0][1] / determinant },
                            { -v[1][0] / determinant, v[0][0] / determinant } };
        return this_type(inverse);
    }

    CUDA_CALLABLE T GetDeterminant() const
    {
        return v[0][0] * v[1][1] - v[0][1] * v[1][0];
    }

    CUDA_CALLABLE this_type& operator*=(const base_type& other)
    {
        base_type::operator*=(other);
        return *this;
    }

    CUDA_CALLABLE this_type& operator*=(T scalar)
    {
        base_type::operator*=(scalar);
        return *this;
    }

    CUDA_CALLABLE this_type& operator+=(const base_type& other)
    {
        base_type::operator+=(other);
        return *this;
    }

    CUDA_CALLABLE this_type& operator-=(const base_type& other)
    {
        base_type::operator-=(other);
        return *this;
    }

    CUDA_CALLABLE this_type operator-() const
    {
        return this_type(base_type::operator-());
    }

#ifndef DOXYGEN_BUILD
    friend CUDA_CALLABLE this_type operator/(const this_type& a, const this_type& b)
    {
        return a * b.GetInverse();
    }
#endif // DOXYGEN_BUILD

private:
    using base_type::v;
};

template <typename T>
class matrix3 : public base_matrix<T, 3>
{
public:
    using base_type = base_matrix<T, 3>;
    using this_type = matrix3<T>;
    using base_matrix<T, 3>::base_matrix;
    using base_type::operator[];
    using base_type::operator==;
    using base_type::operator!=;
    using base_type::data;
    using base_type::Get;
    using base_type::GetArray;
    using base_type::SetColumn;
    using base_type::SetRow;

    using ScalarType = T;
    using base_type::numColumns;
    using base_type::numRows;

    matrix3() = default;
    constexpr matrix3(const this_type&) = default;
    constexpr this_type& operator=(const this_type&) = default;

    // Implicit conversion from base_type
    CUDA_CALLABLE matrix3(const base_type& other) : base_type(other)
    {
    }

    template <typename OTHER_T>
    explicit CUDA_CALLABLE matrix3(const matrix3<OTHER_T>& other)
        : base_type(static_cast<const base_matrix<OTHER_T, numRows>&>(other))
    {
    }

    CUDA_CALLABLE matrix3(T v00, T v01, T v02, T v10, T v11, T v12, T v20, T v21, T v22)
    {
        Set(v00, v01, v02, v10, v11, v12, v20, v21, v22);
    }

    matrix3(const usdrt::GfRotation& rot)
    {
        SetGfRotation(rot);
    }

    CUDA_CALLABLE matrix3(const quat<double>& rotation)
    {
        SetRotate(rotation);
    }


    CUDA_CALLABLE this_type& Set(const T m[numRows][numColumns])
    {
        base_type::Set(m);
        return *this;
    }

    CUDA_CALLABLE this_type& Set(T v00, T v01, T v02, T v10, T v11, T v12, T v20, T v21, T v22)
    {
        T v[3][3] = { { v00, v01, v02 }, { v10, v11, v12 }, { v20, v21, v22 } };
        return Set(v);
    }

    CUDA_CALLABLE this_type& SetIdentity()
    {
        base_type::SetIdentity();
        return *this;
    }

    CUDA_CALLABLE this_type& SetZero()
    {
        base_type::SetZero();
        return *this;
    }

    CUDA_CALLABLE this_type& SetDiagonal(T scalar)
    {
        base_type::SetDiagonal(scalar);
        return *this;
    }

    CUDA_CALLABLE this_type& SetDiagonal(const base_vec<T, numRows>& diagonal)
    {
        base_type::SetDiagonal(diagonal);
        return *this;
    }

    CUDA_CALLABLE this_type GetTranspose() const
    {
        return this_type(base_type::GetTranspose());
    }

    CUDA_CALLABLE this_type GetInverse(T* det = nullptr, T epsilon = T(0)) const
    {
        T determinant = GetDeterminant();
        if (det != nullptr)
        {
            *det = determinant;
        }

        T absDeterminant = (determinant < 0) ? -determinant : determinant;
        // This unusual writing of the condition should catch NaNs.
        if (!(absDeterminant > epsilon))
        {
            // Return the zero matrix, instead of a huge matrix,
            // so that multiplying by this is less likely to be catastrophic.
            return this_type(T(0));
        }

        // TODO: If compilers have difficulty optimizing this, inline the calculations.
        const vec3<T> row0 = GfCross(vec3<T>(v[1]), vec3<T>(v[2]));
        const vec3<T> row1 = GfCross(vec3<T>(v[2]), vec3<T>(v[0]));
        const vec3<T> row2 = GfCross(vec3<T>(v[0]), vec3<T>(v[1]));
        const T recip = T(1) / determinant;

        return this_type(row0[0], row0[1], row0[2], row1[0], row1[1], row1[2], row2[0], row2[1], row2[2]) * recip;
    }

    CUDA_CALLABLE T GetDeterminant() const
    {
        // Scalar triple product
        // TODO: If compilers have difficulty optimizing this, inline the calculations.
        return vec3<T>(v[0]).Dot(GfCross(vec3<T>(v[1]), vec3<T>(v[2])));
    }

    CUDA_CALLABLE bool Orthonormalize()
    {
        vec3<T> rows[3] = { vec3<T>(v[0]), vec3<T>(v[1]), vec3<T>(v[2]) };
        bool success = GfOrthogonalizeBasis(&rows[0], &rows[1], &rows[2]);
        if (success)
        {
            // TODO: Should this check for a negative determinant and flip 1 or all 3 axes,
            //       to force this to be a rotation matrix?
            for (size_t i = 0; i < 3; ++i)
            {
                for (size_t j = 0; j < 3; ++j)
                {
                    v[i][j] = rows[i][j];
                }
            }
        }
        return success;
    }

    CUDA_CALLABLE this_type GetOrthonormalized() const
    {
        this_type result(*this);
        result.Orthonormalize();
        return result;
    }

    CUDA_CALLABLE int GetHandedness() const
    {
        T det = GetDeterminant();
        return (det < T(0)) ? -1 : ((det > T(0)) ? 1 : 0);
    }

    CUDA_CALLABLE bool IsRightHanded() const
    {
        return GetHandedness() == 1;
    }
    CUDA_CALLABLE bool IsLeftHanded() const
    {
        return GetHandedness() == -1;
    }

    CUDA_CALLABLE this_type& operator*=(const base_type& other)
    {
        base_type::operator*=(other);
        return *this;
    }

    CUDA_CALLABLE this_type& operator*=(T scalar)
    {
        base_type::operator*=(scalar);
        return *this;
    }

    CUDA_CALLABLE this_type& operator+=(const base_type& other)
    {
        base_type::operator+=(other);
        return *this;
    }

    CUDA_CALLABLE this_type& operator-=(const base_type& other)
    {
        base_type::operator-=(other);
        return *this;
    }

    CUDA_CALLABLE this_type operator-() const
    {
        return this_type(base_type::operator-());
    }

#ifndef DOXYGEN_BUILD
    friend CUDA_CALLABLE this_type operator/(const this_type& a, const this_type& b)
    {
        return a * b.GetInverse();
    }
#endif // DOXYGEN_BUILD

    CUDA_CALLABLE this_type& SetScale(T scale)
    {
        return SetDiagonal(scale);
    }

    CUDA_CALLABLE this_type& SetScale(const vec3<T>& scales)
    {
        return SetDiagonal(scales);
    }
    // Note: This breaks pin compatibility with USD, but is necessary
    // to avoid a circular dependency with matrix and GfRotation
    template <typename R>
    this_type& SetGfRotation(const R& rot)
    {
        return SetRotate(rot.GetQuat());
    }

    // NOTE: The input quaternion must be normalized (length 1).
    // NOTE: This may or may not represent the rotation matrix for the opposite rotation,
    //       due to interpretations of left-to-right vs. right-to-left multiplication.
    CUDA_CALLABLE this_type& SetRotate(const quat<double>& rotation)
    {
        const double w = rotation.GetReal();
        const vec3<double> xyz = rotation.GetImaginary();
        const double x = xyz[0];
        const double y = xyz[1];
        const double z = xyz[2];
        const double x2 = x * x;
        const double y2 = y * y;
        const double z2 = z * z;
        const double xy = x * y;
        const double xz = x * z;
        const double yz = y * z;
        const double xw = x * w;
        const double yw = y * w;
        const double zw = z * w;

        const T m[3][3] = { { T(1 - 2 * (y2 + z2)), 2 * T(xy + zw), 2 * T(xz - yw) },
                            { 2 * T(xy - zw), T(1 - 2 * (x2 + z2)), 2 * T(yz + xw) },
                            { 2 * T(xz + yw), 2 * T(yz - xw), T(1 - 2 * (x2 + y2)) } };
        return Set(m);
    }

    // Note: This breaks pin compatibility with USD, but is necessary
    // to avoid a circular dependency with matrix and GfRotation
    template <typename R>
    R ExtractGfRotation() const
    {
        return R(ExtractRotation());
    }

    CUDA_CALLABLE quat<double> ExtractRotation() const
    {
        int i;
        if (v[0][0] > v[1][1])
            i = (v[0][0] > v[2][2] ? 0 : 2);
        else
            i = (v[1][1] > v[2][2] ? 1 : 2);

        vec3<double> im;
        double r;

        if (v[0][0] + v[1][1] + v[2][2] > v[i][i])
        {
            r = 0.5 * sqrt(v[0][0] + v[1][1] + v[2][2] + 1);
            im.Set((v[1][2] - v[2][1]) / (4.0 * r), (v[2][0] - v[0][2]) / (4.0 * r), (v[0][1] - v[1][0]) / (4.0 * r));
        }
        else
        {
            int j = (i + 1) % 3;
            int k = (i + 2) % 3;
            double q = 0.5 * sqrt(v[i][i] - v[j][j] - v[k][k] + 1);

            im[i] = q;
            im[j] = (v[i][j] + v[j][i]) / (4 * q);
            im[k] = (v[k][i] + v[i][k]) / (4 * q);
            r = (v[j][k] - v[k][j]) / (4 * q);
        }
        return quat<double>(GfClamp(r, -1.0, 1.0), im);
    }

    // Note: This breaks pin compatibility with USD, but is necessary
    // to avoid a circular dependency with matrix and GfRotation
    template <typename R>
    vec3<T> DecomposeRotation(const vec3<T>& axis0, const vec3<T>& axis1, const vec3<T>& axis2) const
    {
        return vec3<T>(ExtractGfRotation<R>().Decompose(vec3<double>(axis0), vec3<double>(axis1), vec3<double>(axis2)));
    }

private:
    using base_type::v;
};

template <typename T>
class matrix4 : public base_matrix<T, 4>
{
public:
    using base_type = base_matrix<T, 4>;
    using this_type = matrix4<T>;
    using base_matrix<T, 4>::base_matrix;
    using base_type::operator[];
    using base_type::operator==;
    using base_type::operator!=;
    using base_type::data;
    using base_type::Get;
    using base_type::GetArray;
    using base_type::SetColumn;
    using base_type::SetRow;

    using ScalarType = T;
    using base_type::numColumns;
    using base_type::numRows;

    matrix4() = default;
    constexpr matrix4(const this_type&) = default;
    constexpr this_type& operator=(const this_type&) = default;

    // Implicit conversion from base_type
    CUDA_CALLABLE matrix4(const base_type& other) : base_type(other)
    {
    }

    template <typename OTHER_T>
    explicit CUDA_CALLABLE matrix4(const matrix4<OTHER_T>& other)
        : base_type(static_cast<const base_matrix<OTHER_T, numRows>&>(other))
    {
    }

    CUDA_CALLABLE matrix4(
        T v00, T v01, T v02, T v03, T v10, T v11, T v12, T v13, T v20, T v21, T v22, T v23, T v30, T v31, T v32, T v33)
    {
        Set(v00, v01, v02, v03, v10, v11, v12, v13, v20, v21, v22, v23, v30, v31, v32, v33);
    }

    matrix4(const usdrt::GfRotation& rotate, const vec3<T>& translate)
    {

        SetTransform(rotate, translate);
    }

    CUDA_CALLABLE matrix4(const matrix3<T>& rotmx, const vec3<T>& translate)
    {

        SetTransform(rotmx, translate);
    }

    CUDA_CALLABLE this_type& Set(const T m[numRows][numColumns])
    {
        base_type::Set(m);
        return *this;
    }

    CUDA_CALLABLE this_type& Set(
        T v00, T v01, T v02, T v03, T v10, T v11, T v12, T v13, T v20, T v21, T v22, T v23, T v30, T v31, T v32, T v33)
    {
        T v[4][4] = { { v00, v01, v02, v03 }, { v10, v11, v12, v13 }, { v20, v21, v22, v23 }, { v30, v31, v32, v33 } };

        return Set(v);
    }

    CUDA_CALLABLE this_type& SetIdentity()
    {
        base_type::SetIdentity();
        return *this;
    }

    CUDA_CALLABLE this_type& SetZero()
    {
        base_type::SetZero();
        return *this;
    }

    CUDA_CALLABLE this_type& SetDiagonal(T scalar)
    {
        base_type::SetDiagonal(scalar);
        return *this;
    }

    CUDA_CALLABLE this_type& SetDiagonal(const base_vec<T, numRows>& diagonal)
    {
        base_type::SetDiagonal(diagonal);
        return *this;
    }

    CUDA_CALLABLE this_type GetTranspose() const
    {
        return this_type(base_type::GetTranspose());
    }

    // TODO: Optimize this.  The implementation is not as efficient as it could be.
    //       For example, it computes the 4x4 determinant separately from the rest.
    CUDA_CALLABLE this_type GetInverse(T* det = nullptr, T epsilon = T(0)) const
    {
        T determinant = GetDeterminant();
        if (det != nullptr)
        {
            *det = determinant;
        }

        T absDeterminant = (determinant < 0) ? -determinant : determinant;
        // This unusual writing of the condition should catch NaNs.
        if (!(absDeterminant > epsilon))
        {
            // Return the zero matrix, instead of a huge matrix,
            // so that multiplying by this is less likely to be catastrophic.
            return this_type(T(0));
        }

        // Compute all 2x2 determinants.
        // There are only actually 6x6 of them: (0,1), (0,2), (0,3), (1,2), (1,3), (2,3) for row pairs and col pairs.
        constexpr size_t pairIndices[6][2] = { { 0, 1 }, { 0, 2 }, { 0, 3 }, { 1, 2 }, { 1, 3 }, { 2, 3 } };
        T det2x2[6][6];
        // NOTE: The first 3 row pairs are never used, below, so we can skip computing them.
        for (size_t rowpair = 3; rowpair < 6; ++rowpair)
        {
            const size_t row0 = pairIndices[rowpair][0];
            const size_t row1 = pairIndices[rowpair][1];
            for (size_t colpair = 0; colpair < 6; ++colpair)
            {
                const size_t col0 = pairIndices[colpair][0];
                const size_t col1 = pairIndices[colpair][1];
                det2x2[rowpair][colpair] = v[row0][col0] * v[row1][col1] - v[row0][col1] * v[row1][col0];
            }
        }

        // Compute all 3x3 determinants.
        // There is one for every row-col pair.
        constexpr size_t oneIndexRemoved4[4][3] = { { 1, 2, 3 }, { 0, 2, 3 }, { 0, 1, 3 }, { 0, 1, 2 } };
        constexpr size_t twoIndicesRemovedToPair[4][3] = { { 5, 4, 3 }, { 5, 2, 1 }, { 4, 2, 0 }, { 3, 1, 0 } };
        T adjugate[4][4];
        for (size_t omittedRow = 0; omittedRow < 4; ++omittedRow)
        {
            for (size_t omittedCol = 0; omittedCol < 4; ++omittedCol)
            {
                size_t iterationRow = oneIndexRemoved4[omittedRow][0];
                // The first entry in each subarray of twoIndicesRemovedToPair is 3, 4, or 5,
                // regardless of omittedRow, which is why we didn't need to compute det2x2 for
                // any rowpair less than 3, above.
                size_t rowpair = twoIndicesRemovedToPair[omittedRow][0];
                T sum = T(0);
                for (size_t subCol = 0; subCol < 3; ++subCol)
                {
                    size_t iterationCol = oneIndexRemoved4[omittedCol][subCol];
                    size_t colpair = twoIndicesRemovedToPair[omittedCol][subCol];
                    const T& factor = v[iterationRow][iterationCol];
                    T value = factor * det2x2[rowpair][colpair];
                    sum += (subCol & 1) ? -value : value;
                }
                // The adjugate matrix is the transpose of the cofactor matrix, so row and col are swapped here.
                adjugate[omittedCol][omittedRow] = ((omittedRow ^ omittedCol) & 1) ? -sum : sum;
            }
        }

        // Divide by the 4x4 determinant.
        for (size_t row = 0; row < 4; ++row)
        {
            for (size_t col = 0; col < 4; ++col)
            {
                adjugate[row][col] /= determinant;
            }
        }

        return this_type(adjugate);
    }

    CUDA_CALLABLE T GetDeterminant() const
    {
        T sum = 0;
        // It's *very* common that the first 3 components of the last column are all zero,
        // so skip over them.
        if (v[0][3] != 0)
        {
            sum -= v[0][3] * vec3<T>(v[1]).Dot(GfCross(vec3<T>(v[2]), vec3<T>(v[3])));
        }
        if (v[1][3] != 0)
        {
            sum += v[1][3] * vec3<T>(v[0]).Dot(GfCross(vec3<T>(v[2]), vec3<T>(v[3])));
        }
        if (v[2][3] != 0)
        {
            sum -= v[2][3] * vec3<T>(v[0]).Dot(GfCross(vec3<T>(v[1]), vec3<T>(v[3])));
        }
        if (v[3][3] != 0)
        {
            sum += v[3][3] * vec3<T>(v[0]).Dot(GfCross(vec3<T>(v[1]), vec3<T>(v[2])));
        }
        return sum;
    }

    CUDA_CALLABLE T GetDeterminant3() const
    {
        // Scalar triple product
        return vec3<T>(v[0]).Dot(GfCross(vec3<T>(v[1]), vec3<T>(v[2])));
    }

    CUDA_CALLABLE int GetHandedness() const
    {
        T det = GetDeterminant3();
        return (det < T(0)) ? -1 : ((det > T(0)) ? 1 : 0);
    }

    CUDA_CALLABLE bool IsRightHanded() const
    {
        return GetHandedness() == 1;
    }
    CUDA_CALLABLE bool IsLeftHanded() const
    {
        return GetHandedness() == -1;
    }

    CUDA_CALLABLE bool Orthonormalize()
    {
        vec3<T> rows[3] = { vec3<T>(v[0][0], v[0][1], v[0][2]), vec3<T>(v[1][0], v[1][1], v[1][2]),
                            vec3<T>(v[2][0], v[2][1], v[2][2]) };
        bool success = GfOrthogonalizeBasis(&rows[0], &rows[1], &rows[2]);
        // TODO: Should this check for a negative determinant and flip 1 or all 3 axes,
        //       to force this to be a rotation matrix?
        for (size_t i = 0; i < 3; ++i)
        {
            for (size_t j = 0; j < 3; ++j)
            {
                v[i][j] = rows[i][j];
            }
        }

        const double minVectorLength = 1e-10;

        if (v[3][3] != 1.0 && !GfIsClose(v[3][3], 0.0, minVectorLength))
        {
            v[3][0] /= v[3][3];
            v[3][1] /= v[3][3];
            v[3][2] /= v[3][3];
            v[3][3] = 1.0;
        }

        return success;
    }

    CUDA_CALLABLE this_type GetOrthonormalized() const
    {
        this_type result(*this);
        result.Orthonormalize();
        return result;
    }

    CUDA_CALLABLE this_type& operator*=(const base_type& other)
    {
        base_type::operator*=(other);
        return *this;
    }

    CUDA_CALLABLE this_type& operator*=(T scalar)
    {
        base_type::operator*=(scalar);
        return *this;
    }

    CUDA_CALLABLE this_type& operator+=(const base_type& other)
    {
        base_type::operator+=(other);
        return *this;
    }

    CUDA_CALLABLE this_type& operator-=(const base_type& other)
    {
        base_type::operator-=(other);
        return *this;
    }

    CUDA_CALLABLE this_type operator-() const
    {
        return this_type(base_type::operator-());
    }

#ifndef DOXYGEN_BUILD
    friend CUDA_CALLABLE this_type operator/(const this_type& a, const this_type& b)
    {
        return a * b.GetInverse();
    }
#endif // DOXYGEN_BUILD

    CUDA_CALLABLE this_type& SetScale(T scale)
    {
        return SetDiagonal(vec4<T>(scale, scale, scale, T(1)));
    }

    CUDA_CALLABLE this_type& SetScale(const vec3<T>& scales)
    {
        return SetDiagonal(vec4<T>(scales[0], scales[1], scales[2], T(1)));
    }

    this_type& SetTransform(const usdrt::GfRotation& rot, const vec3<T>& translate)
    {
        SetRotate(rot);
        return SetTranslateOnly(translate);
    }

    CUDA_CALLABLE this_type& SetTransform(const matrix3<T>& rot, const vec3<T>& translate)
    {
        SetRotate(rot);
        return SetTranslateOnly(translate);
    }

    CUDA_CALLABLE this_type RemoveScaleShear() const
    {
        vec3<T> rows[3] = { vec3<T>(v[0]), vec3<T>(v[1]), vec3<T>(v[2]) };
        bool success = GfOrthogonalizeBasis(&rows[0], &rows[1], &rows[2]);
        if (!success)
        {
            return *this;
        }
        // Scalar triple product is determinant of 3x3 matrix, (which should be about -1 or 1
        // after orthonormalizing the vectors.)
        if (rows[0].Dot(GfCross(rows[1], rows[2])) < 0)
        {
            // Negative determinant, so invert one of the axes.
            // TODO: Is it better to invert all 3 axes?
            rows[2] = -rows[2];
        }
        return matrix4<T>(rows[0][0], rows[0][1], rows[0][2], 0.0f, rows[1][0], rows[1][1], rows[1][2], 0.0f,
                          rows[2][0], rows[2][1], rows[2][2], 0.0f, v[3][0], v[3][1], v[3][2], 1.0f);
    }

    this_type& SetRotate(const usdrt::GfRotation& rotation)
    {
        matrix3<T> m3;
        m3.SetGfRotation(rotation);
        return SetRotate(m3);
    }


    this_type& SetRotateOnly(const usdrt::GfRotation& rotation)
    {
        matrix3<T> m3;
        m3.SetGfRotation(rotation);
        return SetRotateOnly(m3);
    }

    CUDA_CALLABLE this_type& SetRotate(const quat<double>& rotation)
    {
        matrix3<T> m3;
        m3.SetRotate(rotation);
        return SetRotate(m3);
    }


    CUDA_CALLABLE this_type& SetRotateOnly(const quat<double>& rotation)
    {
        matrix3<T> m3;
        m3.SetRotate(rotation);
        return SetRotateOnly(m3);
    }

    // NOTE: Contrary to the name, this sets the full 3x3 portion of the matrix,
    //       i.e. it also sets scales and shears.
    // NOTE: This clears any translations.
    CUDA_CALLABLE this_type& SetRotate(const matrix3<T>& m3)
    {
        for (size_t i = 0; i < 3; ++i)
        {
            for (size_t j = 0; j < 3; ++j)
            {
                v[i][j] = m3[i][j];
            }
            v[i][3] = T(0);
        }
        v[3][0] = T(0);
        v[3][1] = T(0);
        v[3][2] = T(0);
        v[3][3] = T(1);

        return *this;
    }

    // NOTE: Contrary to the name, this sets the full 3x3 portion of the matrix,
    //       i.e. it also sets scales and shears.
    // NOTE: This does NOT clear any translations.
    CUDA_CALLABLE this_type& SetRotateOnly(const matrix3<T>& m3)
    {
        for (size_t i = 0; i < 3; ++i)
        {
            for (size_t j = 0; j < 3; ++j)
            {
                v[i][j] = m3[i][j];
            }
        }

        return *this;
    }

    CUDA_CALLABLE this_type& SetTranslate(const vec3<T>& translation)
    {
        for (size_t i = 0; i < 3; ++i)
        {
            for (size_t j = 0; j < 4; ++j)
            {
                v[i][j] = (i == j) ? T(1) : T(0);
            }
        }
        v[3][0] = translation[0];
        v[3][1] = translation[1];
        v[3][2] = translation[2];
        v[3][3] = T(1);

        return *this;
    }

    CUDA_CALLABLE this_type& SetTranslateOnly(const vec3<T>& translation)
    {
        v[3][0] = translation[0];
        v[3][1] = translation[1];
        v[3][2] = translation[2];
        v[3][3] = T(1);

        return *this;
    }

    CUDA_CALLABLE void SetRow3(size_t rowIndex, const vec3<T>& rowValues)
    {
        v[rowIndex][0] = rowValues[0];
        v[rowIndex][1] = rowValues[1];
        v[rowIndex][2] = rowValues[2];
    }

    CUDA_CALLABLE vec3<T> GetRow3(size_t rowIndex) const
    {
        return vec3<T>(v[rowIndex][0], v[rowIndex][1], v[rowIndex][2]);
    }

    CUDA_CALLABLE this_type& SetLookAt(const vec3<T>& cameraPosition,
                                       const vec3<T>& focusPosition,
                                       const vec3<T>& upDirection)
    {
        // NOTE: forward is the negative z direction.
        vec3<T> forward = (focusPosition - cameraPosition).GetNormalized();
        // Force up direction to be orthogonal to forward.
        // NOTE: up is the positive y direction.
        vec3<T> up = upDirection.GetComplement(forward).GetNormalized();
        // NOTE: right is the positive x direction.
        vec3<T> right = GfCross(forward, up);

        // Pre-translation by -cameraPosition
        vec3<T> translation(-right.Dot(cameraPosition), -up.Dot(cameraPosition), forward.Dot(cameraPosition));

        T m[4][4] = { { right[0], up[0], -forward[0], T(0) },
                      { right[1], up[1], -forward[1], T(0) },
                      { right[2], up[2], -forward[2], T(0) },
                      { translation[0], translation[1], translation[2], T(1) } };

        return Set(m);
    }

    CUDA_CALLABLE this_type& SetLookAt(const vec3<T>& cameraPosition, const quat<double>& orientation)
    {
        matrix4<T> translation;
        translation.SetTranslate(-cameraPosition);
        matrix4<T> rotation;
        rotation.SetRotate(orientation.GetInverse());
        *this = translation * rotation;
        return *this;
    }


    // Note: This breaks pin compatibility with USD, but is necessary
    // to avoid a circular dependency with matrix and GfRotation
    template <typename R>
    this_type& SetLookAt(const vec3<T>& cameraPosition, const R& orientation)
    {
        matrix4<T> translation;
        translation.SetTranslate(-cameraPosition);
        matrix4<T> rotation;
        rotation.SetRotate(orientation.GetInverse());
        *this = translation * rotation;
        return *this;
    }

    bool Factor(this_type* r, vec3<T>* s, this_type* u, vec3<T>* t, this_type* p, float eps = 1e-10) const;

    CUDA_CALLABLE vec3<T> ExtractTranslation() const
    {
        return vec3<T>(v[3][0], v[3][1], v[3][2]);
    }

    CUDA_CALLABLE quat<double> ExtractRotation() const
    {
        return ExtractRotationMatrix().ExtractRotation();
    }

    // Note: This breaks pin compatibility with USD, but is necessary
    // to avoid a circular dependency with matrix and GfRotation
    template <typename R>
    R ExtractGfRotation() const
    {
        return R(ExtractRotation());
    }

    // Note: This breaks pin compatibility with USD, but is necessary
    // to avoid a circular dependency with matrix and GfRotation
    template <typename R>
    vec3<T> DecomposeRotation(const vec3<T>& axis0, const vec3<T>& axis1, const vec3<T>& axis2) const
    {
        return vec3<T>(ExtractGfRotation<R>().Decompose(vec3<double>(axis0), vec3<double>(axis1), vec3<double>(axis2)));
    }

    // NOTE: Contrary to the name, this extracts the full 3x3 portion of the matrix,
    //       i.e. it also includes scales and shears.
    CUDA_CALLABLE matrix3<T> ExtractRotationMatrix() const
    {
        return matrix3<T>(v[0][0], v[0][1], v[0][2], v[1][0], v[1][1], v[1][2], v[2][0], v[2][1], v[2][2]);
    }

    template <typename OTHER_T>
    CUDA_CALLABLE vec3<OTHER_T> Transform(const vec3<OTHER_T>& u) const
    {
        return vec3<OTHER_T>(vec4<T>(u[0] * v[0][0] + u[1] * v[1][0] + u[2] * v[2][0] + v[3][0],
                                     u[0] * v[0][1] + u[1] * v[1][1] + u[2] * v[2][1] + v[3][1],
                                     u[0] * v[0][2] + u[1] * v[1][2] + u[2] * v[2][2] + v[3][2],
                                     u[0] * v[0][3] + u[1] * v[1][3] + u[2] * v[2][3] + v[3][3])
                                 .Project());
    }

    template <typename OTHER_T>
    CUDA_CALLABLE vec3<OTHER_T> TransformDir(const vec3<OTHER_T>& u) const
    {
        return vec3<OTHER_T>(OTHER_T(u[0] * v[0][0] + u[1] * v[1][0] + u[2] * v[2][0]),
                             OTHER_T(u[0] * v[0][1] + u[1] * v[1][1] + u[2] * v[2][1]),
                             OTHER_T(u[0] * v[0][2] + u[1] * v[1][2] + u[2] * v[2][2]));
    }

    template <typename OTHER_T>
    CUDA_CALLABLE vec3<OTHER_T> TransformAffine(const vec3<OTHER_T>& u) const
    {
        return vec3<OTHER_T>(OTHER_T(u[0] * v[0][0] + u[1] * v[1][0] + u[2] * v[2][0] + v[3][0]),
                             OTHER_T(u[0] * v[0][1] + u[1] * v[1][1] + u[2] * v[2][1] + v[3][1]),
                             OTHER_T(u[0] * v[0][2] + u[1] * v[1][2] + u[2] * v[2][2] + v[3][2]));
    }


private:
    void _Jacobi3(vec3<T>* eigenvalues, vec3<T> eigenvectors[3]) const;
    friend class matrix4<double>;
    friend class matrix4<float>;
    using base_type::v;
};

using matrix2f = matrix2<float>;
using matrix2d = matrix2<double>;

using matrix3f = matrix3<float>;
using matrix3d = matrix3<double>;

using matrix4f = matrix4<float>;
using matrix4d = matrix4<double>;

}
}
}

namespace usdrt
{

using omni::math::linalg::GfIsClose;

using GfMatrix2d = omni::math::linalg::matrix2<double>;
using GfMatrix2f = omni::math::linalg::matrix2<float>;
using GfMatrix3d = omni::math::linalg::matrix3<double>;
using GfMatrix3f = omni::math::linalg::matrix3<float>;
using GfMatrix4d = omni::math::linalg::matrix4<double>;
using GfMatrix4f = omni::math::linalg::matrix4<float>;

template <>
struct GfIsGfMatrix<GfMatrix2d>
{
    static const bool value = true;
};

template <>
struct GfIsGfMatrix<GfMatrix2f>
{
    static const bool value = true;
};

template <>
struct GfIsGfMatrix<GfMatrix3d>
{
    static const bool value = true;
};

template <>
struct GfIsGfMatrix<GfMatrix3f>
{
    static const bool value = true;
};

template <>
struct GfIsGfMatrix<GfMatrix4d>
{
    static const bool value = true;
};

template <>
struct GfIsGfMatrix<GfMatrix4f>
{
    static const bool value = true;
};

}


#include <usdrt/gf/factor.inl>
