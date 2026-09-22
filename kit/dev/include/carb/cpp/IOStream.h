// SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! \file
//! \brief I/O stream operations for C++ types
#pragma once

#include <string_view>
#include <iostream>

namespace carb::cpp
{
// Forward declarations
template <class CharT, class Traits>
class basic_string_view;

template <class CharT, class Traits>
class basic_zstring_view;

//! Stream operator for carb::cpp::basic_string_view
template <class CharT, class Traits>
std::basic_ostream<CharT, Traits>& operator<<(std::basic_ostream<CharT, Traits>& os,
                                              const basic_string_view<CharT, Traits>& sv)
{
    return os << ::std::basic_string_view<CharT, Traits>(sv);
}

//! Stream operator for carb::cpp::basic_zstring_view
template <class CharT, class Traits>
std::basic_ostream<CharT, Traits>& operator<<(std::basic_ostream<CharT, Traits>& os,
                                              const basic_zstring_view<CharT, Traits>& sv)
{
    return os << ::std::basic_string_view<CharT, Traits>(sv);
}
} // namespace carb::cpp
