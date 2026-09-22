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
//! \brief Carbonite C++14-compatible Chrono library overrides
#pragma once

#include "../Defines.h"

#include <chrono>
#include <type_traits>

namespace carb
{
namespace cpp
{
namespace chrono
{

//! A **monotonic** high-resolution clock.
//!
//! @note The standard allows `std::chrono::high_resolution_clock` to alias either `system_clock` (non-monotonic) or
//! the monotonic `steady_clock` (or be a distinct clock). Since we always desire for this to be a monotonic clock, this
//! aliases `std::chrono::high_resolution_clock` only if it is steady, otherwise it aliases `std::chrono::steady_clock`.
//! @see https://en.cppreference.com/w/cpp/chrono/high_resolution_clock
using high_resolution_clock =
    std::conditional_t<std::chrono::high_resolution_clock::is_steady, std::chrono::high_resolution_clock, std::chrono::steady_clock>;

} // namespace chrono
} // namespace cpp
namespace chrono = cpp::chrono;
} // namespace carb
