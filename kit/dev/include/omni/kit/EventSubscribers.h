// SPDX-FileCopyrightText: Copyright (c) 2019-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file
//! @brief Utilities for managing EventSubscribers for omni.kit.app
#pragma once

#include "../../carb/Defines.h"

#include <vector>

namespace carb
{

/**
 * A class that manages subscribers
 *
 * @thread_safety This class is **not** thread safe. Consider using \ref carb::delegate::Delegate which is thread-safe.
 * @warning This class does not conform to Basic Callback Hygiene as described in the @rstdoc{../../../../CODING}. It's
 *   use should be avoided. Instead use \ref carb::delegate::Delegate. This class is also not thread-safe.
 * @tparam FuncT The function pointer type to manage
 * @tparam SubIdT A type that is used as the subscriber type
 */
template <class FuncT, typename SubIdT>
class EventSubscribers
{
public:
    /**
     * Create a subscription, returning a handle to reference it.
     * @warning This class does not conform to Basic Callback Hygiene as described in the @rstdoc{../../../../CODING}.
     *   It's use should be avoided. Instead use \ref carb::delegate::Delegate. This class is also not thread-safe.
     * @param fn The function pointer to register
     * @param userData The user data that should be passed to \p fn when called
     * @returns a `SubIdT` to reference the registered function. There is no invalid value, so `0` may be returned.
     *   Subscription IDs may also be reused as soon as they are unsubscribed. Call \ref unsubscribe() when finished
     *   with the subscription.
     */
    SubIdT subscribe(FuncT fn, void* userData)
    {
        // Search for free slot
        size_t index;
        bool found = false;
        for (size_t i = 0; i < m_subscribers.size(); i++)
        {
            if (!m_subscribers[i].fn)
            {
                index = i;
                found = true;
                break;
            }
        }

        // Add new slot if haven't found a free one
        if (!found)
        {
            m_subscribers.push_back({});
            index = m_subscribers.size() - 1;
        }

        m_subscribers[index] = { fn, userData };
        return (SubIdT)index;
    }

    /**
     * Removes a subscriber previously subscribed with @ref subscribe().
     * @warning This class does not conform to Basic Callback Hygiene as described in the @rstdoc{../../../../CODING}.
     *   It's use should be avoided. Instead use \ref carb::delegate::Delegate. This class is also not thread-safe.
     * @warning Calling this function with an invalid Subscription ID will cause undefined behavior.
     * @param id The subscriber ID previously passed to \ref subscribe().
     */
    void unsubscribe(SubIdT id)
    {
        CARB_ASSERT(id < m_subscribers.size());
        m_subscribers[id] = {};
    }

    /**
     * Calls all subscribers.
     * @warning This class does not conform to Basic Callback Hygiene as described in the @rstdoc{../../../../CODING}.
     *   It's use should be avoided. Instead use \ref carb::delegate::Delegate. This class is also not thread-safe.
     * @param args Arguments passed to the subscribed `FuncT` functions. These arguments are passed by value prior to
     *   the `userData` parameter that was registered with \ref subscribe().
     */
    template <typename... Ts>
    void send(Ts... args)
    {
        // Iterate by index because subscribers can actually change during iteration (vector can grow)
        const size_t kCount = m_subscribers.size();
        for (size_t i = 0; i < kCount; i++)
        {
            auto& subsribers = m_subscribers[i];
            if (subsribers.fn)
                subsribers.fn(args..., subsribers.userData);
        }
    }

    /**
     * Calls a single subscriber.
     * @warning This class does not conform to Basic Callback Hygiene as described in the @rstdoc{../../../../CODING}.
     *   It's use should be avoided. Instead use \ref carb::delegate::Delegate. This class is also not thread-safe.
     * @warning Calling this function with an invalid Subscription ID will cause undefined behavior.
     * @param id The subscriber ID previously passed to \ref subscribe().
     * @param args Arguments passed to the subscribed `FuncT` functions. These arguments are passed by value prior to
     *   the `userData` parameter that was registered with \ref subscribe().
     */
    template <typename... Ts>
    void sendForId(uint64_t id, Ts... args)
    {
        CARB_ASSERT(id < m_subscribers.size());
        if (m_subscribers[id].fn)
            m_subscribers[id].fn(args..., m_subscribers[id].userData);
    }

private:
    struct EventData
    {
        FuncT fn;
        void* userData;
    };
    std::vector<EventData> m_subscribers;
};

} // namespace carb
