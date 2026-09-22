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
#include "../cpp/Semaphore.h"

namespace carb
{
namespace extras
{

class CARB_DEPRECATED("Deprecated: carb::extras::binary_semaphore has moved to carb::cpp::binary_semaphore") binary_semaphore
    : public carb::cpp::binary_semaphore
{
public:
    constexpr explicit binary_semaphore(ptrdiff_t desired) : carb::cpp::binary_semaphore(desired)
    {
    }
};

template <ptrdiff_t least_max_value = carb::cpp::detail::kSemaphoreValueMax>
class CARB_DEPRECATED("Deprecated: carb::extras::counting_semaphore has moved to carb::cpp::counting_semaphore")
    counting_semaphore : public carb::cpp::counting_semaphore<least_max_value>
{
public:
    constexpr explicit counting_semaphore(ptrdiff_t desired) : carb::cpp::counting_semaphore<least_max_value>(desired)
    {
    }
};

} // namespace extras
} // namespace carb
