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
//!
//! @brief Helper utilities for carb.events.
#pragma once

#include "../Defines.h"
#include "../InterfaceUtils.h"
#include "../ObjectUtils.h"
#include "IEvents.h"

#include <functional>
#include <utility>

namespace carb
{
namespace events
{

/**
 * Helper for carb::getCachedInterface<IEvents>().
 * @returns The cached carb::events::IEvents interface.
 */
inline IEvents* getCachedEventsInterface()
{
    return getCachedInterface<IEvents>();
}

/**
 * A helper to use a `std::function` as an carb::events::IEventListener.
 */
class LambdaEventListener : public IEventListener
{
public:
    /**
     * Constructor.
     * @param fn The `std::function` to call when onEvent() is called.
     */
    LambdaEventListener(std::function<void(IEvent*)> fn) : m_fn(std::move(fn))
    {
    }

    /**
     * Passes the event to the `std::function` given to the constructor.
     * @param e The carb::events::IEvent to process.
     */
    void onEvent(IEvent* e) override
    {
        if (m_fn)
            m_fn(e);
    }

private:
    std::function<void(IEvent*)> m_fn;

    CARB_IOBJECT_IMPL
};

/**
 * A helper for IEvents::createSubscriptionToPop() that creates a @ref LambdaEventListener.
 * @param stream The @ref IEventStream to use.
 * @param onEventFn A handler that will be invoked for each carb::events::IEvent that is popped.
 * @param order An optional value used to specify the order tier. Lower order tiers will be notified first.
 *   Multiple IEventListener objects at the same order tier are notified in an undefined order.
 * @param subscriptionName An optional name for the subscription. Names do not need to be unique.
 * @returns A ISubscription pointer. The subscription is valid as long as the ISubscription pointer is referenced.
 *   Alternately, the IEventListener can be unsubscribed by calling ISubscription::unsubscribe().
 */
[[nodiscard]] inline ObjectPtr<ISubscription> createSubscriptionToPop(IEventStream* stream,
                                                                      std::function<void(IEvent*)> onEventFn,
                                                                      Order order = kDefaultOrder,
                                                                      const char* subscriptionName = nullptr)
{
    return stream->createSubscriptionToPop(
        carb::stealObject(new LambdaEventListener(std::move(onEventFn))).get(), order, subscriptionName);
}

/// @copydoc createSubscriptionToPop
/// @param eventType A specific event to listen for.
[[nodiscard]] inline ObjectPtr<ISubscription> createSubscriptionToPopByType(IEventStream* stream,
                                                                            EventType eventType,
                                                                            std::function<void(IEvent*)> onEventFn,
                                                                            Order order = kDefaultOrder,
                                                                            const char* subscriptionName = nullptr)
{
    return stream->createSubscriptionToPopByType(
        eventType, carb::stealObject(new LambdaEventListener(std::move(onEventFn))).get(), order, subscriptionName);
}

/**
 * A helper for IEvents::createSubscriptionToPush() that creates a @ref LambdaEventListener.
 * @param stream The @ref IEventStream to use.
 * @param onEventFn A handler that will be invoked for each carb::events::IEvent that is pushed.
 * @param order An optional value used to specify the order tier. Lower order tiers will be notified first.
 *   Multiple IEventListener objects at the same order tier are notified in an undefined order.
 * @param subscriptionName An optional name for the subscription. Names do not need to be unique.
 * @returns A ISubscription pointer. The subscription is valid as long as the ISubscription pointer is referenced.
 *   Alternately, the IEventListener can be unsubscribed by calling ISubscription::unsubscribe().
 */
[[nodiscard]] inline ObjectPtr<ISubscription> createSubscriptionToPush(IEventStream* stream,
                                                                       std::function<void(IEvent*)> onEventFn,
                                                                       Order order = kDefaultOrder,
                                                                       const char* subscriptionName = nullptr)
{
    return stream->createSubscriptionToPush(
        carb::stealObject(new LambdaEventListener(std::move(onEventFn))).get(), order, subscriptionName);
}

/// @copydoc createSubscriptionToPush
/// @param eventType A specific event to listen for.
[[nodiscard]] inline ObjectPtr<ISubscription> createSubscriptionToPushByType(IEventStream* stream,
                                                                             EventType eventType,
                                                                             std::function<void(IEvent*)> onEventFn,
                                                                             Order order = kDefaultOrder,
                                                                             const char* subscriptionName = nullptr)
{
    return stream->createSubscriptionToPushByType(
        eventType, carb::stealObject(new LambdaEventListener(std::move(onEventFn))).get(), order, subscriptionName);
}

/**
 * A helper for \ref IEventStream::walkSubscriptionsToPop() that gathers the subscriptions into a vector.  The order is
 * unspecified.
 * @param stream The \ref IEventStream to use.
 * @returns A vector of ISubscription pointers.
 */
[[nodiscard]] inline std::vector<ObjectPtr<ISubscription>> getSubscriptionsToPop(IEventStream* stream)
{
    std::vector<ObjectPtr<ISubscription>> subscriptions;
    subscriptions.reserve(stream->getSubscriptionToPopCount());
    stream->walkSubscriptionsToPop(
        [](ISubscription* s, void* userData) {
            auto& subs = *static_cast<decltype(subscriptions)*>(userData);
            subs.emplace_back(carb::borrowObject(s));
            return true;
        },
        &subscriptions);
    return subscriptions;
}

/**
 * A helper for \ref IEventStream::walkSubscriptionsToPush() that gathers the subscriptions into a vector. The order is
 * unspecified.
 * @param stream The \ref IEventStream to use.
 * @returns A vector of ISubscription pointers.
 */
[[nodiscard]] inline std::vector<ObjectPtr<ISubscription>> getSubscriptionsToPush(IEventStream* stream)
{
    std::vector<ObjectPtr<ISubscription>> subscriptions;
    subscriptions.reserve(stream->getSubscriptionToPushCount());
    stream->walkSubscriptionsToPush(
        [](ISubscription* s, void* userData) {
            auto& subs = *static_cast<decltype(subscriptions)*>(userData);
            subs.emplace_back(carb::borrowObject(s));
            return true;
        },
        &subscriptions);
    return subscriptions;
}

} // namespace events
} // namespace carb
