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
//! @brief Implementation of a clock based on the CPU time-stamp counter
#pragma once

#include "../clock/TscClock.h"

namespace carb
{
namespace time
{
//! Deprecated name for carb::clock::tsc_clock;
using carb::clock::tsc_clock;
//! \cond DEV
namespace detail
{
using namespace carb::clock::detail;
}
//! \endcond
} // namespace time
} // namespace carb
