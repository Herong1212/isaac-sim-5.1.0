// SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#pragma once

#include <omni/core/IObject.h>

namespace omni::sensors::net::utils
{

/**
 * @brief A class that can be used to determine if there are any active omni.bind classes.
 *
 * When a user desires to know if an instance of @ref ImplementsWithTracking is active
 * the user can use @ref anyLiveInstances. Any omni.bind interface that does not use
 * either @ref ImplementsWithTracking or @ref LifeTracking as a base class is
 * not tracked, and it is incumbent on the user to track and ensure the class is disposed of.
 *
 * The user is still required to hook @ref anyLiveInstances into canOnload of each module.
 */
class LifeTracking
{
public:
    LifeTracking()
    {
        s_activeInstances.fetch_add(1, std::memory_order_relaxed);
    }
    ~LifeTracking()
    {
        s_activeInstances.fetch_sub(1, std::memory_order_relaxed);
    }

    static bool anyLiveInstances()
    {
        return s_activeInstances.load(std::memory_order_relaxed) != 0;
    }

private:
    static std::atomic<uint32_t> s_activeInstances;
};

/**
 * @brief Implements one or more omni.bind interfaces with tracking.
 *
 * @tparam omni.bind interfaces that are implemented.
 */
template <typename... Types>
struct ImplementsWithTracking : public LifeTracking, public ::omni::core::Implements<Types...>
{
};

} // namespace omni::sensors::net::utils
