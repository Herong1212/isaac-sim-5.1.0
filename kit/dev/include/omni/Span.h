// SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file
//! @brief Implementation of \ref omni::span
#pragma once

#include "../carb/cpp/Span.h"

namespace omni
{

//! @copydoc carb::cpp::dynamic_extent
constexpr auto dynamic_extent = carb::cpp::dynamic_extent;

//! @copydoc carb::cpp::span
template <class T, size_t Extent = dynamic_extent>
using span = carb::cpp::span<T, Extent>;

// Deduction guides are missing here because alias templates are not deduced. C++20 adds some support for them with
// class template argument deduction (CTAD).

} // namespace omni
