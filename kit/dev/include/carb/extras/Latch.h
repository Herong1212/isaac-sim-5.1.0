// SPDX-FileCopyrightText: Copyright (c) 2019-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#pragma once
#include "../cpp/Latch.h"

namespace carb
{
namespace extras
{

class CARB_DEPRECATED("Deprecated: carb::extras::latch has moved to carb::cpp::latch") latch : public carb::cpp::latch
{
public:
    constexpr explicit latch(ptrdiff_t expected) : carb::cpp::latch(expected)
    {
    }
};

} // namespace extras
} // namespace carb
