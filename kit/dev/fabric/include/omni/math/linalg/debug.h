// Copyright (c) 2022, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "half.h"
#include "matrix.h"
#include "quat.h"
#include "vec.h"

#include <iomanip>
#include <iostream>

namespace omni
{
namespace math
{
namespace linalg
{

// =================================================================================
// Debug output operators for linalg types

std::ostream& operator<<(std::ostream& out, half const& v)
{
    return out << (float)v;
}

template <typename T, size_t precision = 4>
struct NumericFormatter
{
    explicit NumericFormatter(T d)
    {
        m_val = d;
    }
    static constexpr size_t s_precision = precision;
    static constexpr size_t s_width = 14;
    T m_val;
};

template <typename T>
std::ostream& operator<<(std::ostream& out, NumericFormatter<T> const& f)
{
    return out << std::setprecision(NumericFormatter<T>::s_precision) << std::fixed << std::left
               << std::setw(NumericFormatter<T>::s_width) << std::setfill(' ') << f.m_val;
}

template <typename T, size_t N>
std::ostream& operator<<(std::ostream& out, base_matrix<T, N> const& m)
{
    using Fmt = NumericFormatter<T>;
    for (size_t i = 0; i < (N - 1); ++i)
    {
        out << '|';
        for (size_t j = 0; j < (N - 1); ++j)
            out << Fmt(m[i][j]);
        out << Fmt(m[i][N - 1]) << '|';
        if (i < (N - 1))
            out << '\n';
    }
    return out;
}

template<typename T, size_t N>
std::ostream& operator<<(std::ostream& out, base_vec<T, N> const& v)
{
    using Fmt = NumericFormatter<T>;
    out << '(';
    for (size_t i = 0; i < (N - 1); ++i)
        out << Fmt(v[0]);
    return out << Fmt(v[N - 1]) << ')';
}

template <typename T>
std::ostream& operator<<(std::ostream& out, quat<T> const& q)
{
    auto i = q.GetImaginary();
    auto real = q.GetReal();
    return out << vec4<T>{ real, i[0], i[1], i[2] };
}


} // linalg
} // math
} // omni
