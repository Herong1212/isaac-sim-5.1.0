// SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! \file
//! \brief C++14-compatible implementation of select functionality from C++ `<cstddef>` library.
#pragma once

#include <type_traits>

namespace carb
{
namespace cpp
{

//! A byte is a distinct type that implements the concept of byte as specified in the C++ language definition.
//! Like `char` and `unsigned char`, it can be used to access raw memory occupied by other objects, but unlike those
//! types it is not a character type and is not an arithmetic type. A byte is only a collection of bits, and only
//! bitwise operators are defined for it.
enum class byte : unsigned char
{
};

#ifndef DOXYGEN_BUILD
template <class IntegerType, std::enable_if_t<std::is_integral<IntegerType>::value, bool> = false>
constexpr IntegerType to_integer(byte b) noexcept
{
    return static_cast<IntegerType>(b);
}

constexpr byte operator|(byte l, byte r) noexcept
{
    return byte(static_cast<unsigned char>(l) | static_cast<unsigned char>(r));
}

constexpr byte operator&(byte l, byte r) noexcept
{
    return byte(static_cast<unsigned char>(l) & static_cast<unsigned char>(r));
}

constexpr byte operator^(byte l, byte r) noexcept
{
    return byte(static_cast<unsigned char>(l) ^ static_cast<unsigned char>(r));
}

constexpr byte operator~(byte b) noexcept
{
    return byte(~static_cast<unsigned char>(b));
}

template <class IntegerType, std::enable_if_t<std::is_integral<IntegerType>::value, bool> = false>
constexpr byte operator<<(byte b, IntegerType shift) noexcept
{
    return byte(static_cast<unsigned char>(b) << shift);
}

template <class IntegerType, std::enable_if_t<std::is_integral<IntegerType>::value, bool> = false>
constexpr byte operator>>(byte b, IntegerType shift) noexcept
{
    return byte(static_cast<unsigned char>(b) >> shift);
}

template <class IntegerType, std::enable_if_t<std::is_integral<IntegerType>::value, bool> = false>
constexpr byte& operator<<=(byte& b, IntegerType shift) noexcept
{
    b = b << shift;
    return b;
}

template <class IntegerType, std::enable_if_t<std::is_integral<IntegerType>::value, bool> = false>
constexpr byte& operator>>=(byte& b, IntegerType shift) noexcept
{
    b = b >> shift;
    return b;
}

constexpr byte& operator|=(byte& l, byte r) noexcept
{
    l = l | r;
    return l;
}

constexpr byte& operator&=(byte& l, byte r) noexcept
{
    l = l & r;
    return l;
}

constexpr byte& operator^=(byte& l, byte r) noexcept
{
    l = l ^ r;
    return l;
}

#endif

} // namespace cpp
} // namespace carb
