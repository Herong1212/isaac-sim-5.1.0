// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file EnumBitops.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::EnumBitops.
#pragma once

#include <type_traits>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

//! Enable bitwise operations on enum classes. Templates save on writing boiler plate code to allow this.
template <class T = void>
struct EnumBitops
{
};

#ifndef DOXYGEN_BUILD

template <>
struct EnumBitops<void>
{
    struct _allow_bitops
    {
        static constexpr bool allow_bitops = true;
    };
    using allow_bitops = _allow_bitops;

    template <class T, class R = T>
    using t = typename std::enable_if<std::is_enum<T>::value && EnumBitops<T>::allow_bitops, R>::type;

    template <class T>
    using u = typename std::underlying_type<T>::type;
};

template <class T>
constexpr EnumBitops<>::t<T> operator~(T a)
{
    return static_cast<T>(~static_cast<EnumBitops<>::u<T>>(a));
}
template <class T>
constexpr EnumBitops<>::t<T> operator|(T a, T b)
{
    return static_cast<T>(static_cast<EnumBitops<>::u<T>>(a) | static_cast<EnumBitops<>::u<T>>(b));
}
template <class T>
constexpr EnumBitops<>::t<T> operator&(T a, T b)
{
    return static_cast<T>(static_cast<EnumBitops<>::u<T>>(a) & static_cast<EnumBitops<>::u<T>>(b));
}
template <class T>
constexpr EnumBitops<>::t<T> operator^(T a, T b)
{
    return static_cast<T>(static_cast<EnumBitops<>::u<T>>(a) ^ static_cast<EnumBitops<>::u<T>>(b));
}
template <class T>
constexpr EnumBitops<>::t<T, T&> operator|=(T& a, T b)
{
    a = a | b;
    return a;
}
template <class T>
constexpr EnumBitops<>::t<T, T&> operator&=(T& a, T b)
{
    a = a & b;
    return a;
}
template <class T>
constexpr EnumBitops<>::t<T, T&> operator^=(T& a, T b)
{
    a = a ^ b;
    return a;
}
template <class T, typename = EnumBitops<>::t<T>>
constexpr bool to_bool(T a)
{
    return static_cast<EnumBitops<>::u<T>>(a) != 0;
}

#endif // DOXYGEN_BUILD

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni
