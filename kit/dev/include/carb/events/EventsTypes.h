// SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file
//! @brief carb.events type declarations
#pragma once

#include "../IObject.h"

namespace carb::events
{

// Forward declarations
class ISubscription;
class IEvent;


/**
 * Event type is 64-bit number. To use strings as event types hash function can be used. @see CARB_EVENTS_TYPE_FROM_STR
 */
using EventType = uint64_t;

/**
 * Event sender identifier. It is useful in some cases to differentiate who send an event. E.g. to know that is was you.
 */
using SenderId = uint32_t;

/**
 * Default sender id to use if you don't want it to be unique
 */
constexpr SenderId kGlobalSenderId = 0;


/**
 * Event notification order.
 */
using Order = int32_t;

/**
 * Default order value. This is a signed value, so negative order values will be called before the default order.
 */
constexpr Order kDefaultOrder = 0;

/**
 * Callback function called by \ref IEventStream::walkSubscriptionsToPush and \ref IEventStream::walkSubscriptionsToPop.
 * @param subscription The subscription.
 * @param userData The userdata passed to the \ref IEventStream function.
 * @returns `true` to continue iterating through the subscriptions, `false` to stop iterating.
 */
using SubscriptionCallback = bool (*)(ISubscription* subscription, void* userData);

/**
 * Interface to implement for event listener.
 */
class IEventListener : public IObject
{
public:
    /**
     * Function to be implemented that will handle an event.
     * @param e The event to process. To stop further propagation of the event, call IEvent::consume().
     */
    virtual void onEvent(IEvent* e) = 0;
};

/// Helper definition for IEventListener smart pointer.
using IEventListenerPtr = ObjectPtr<IEventListener>;

/**
 * Compile-time conversion of string to carb::events::EventType.
 * @param STR The string to convert.
 * @returns The EventType corresponding to the given string.
 */
#define CARB_EVENTS_TYPE_FROM_STR(STR) CARB_HASH_STRING(STR)

/**
 * Run-time conversion of string to carb::events::EventType.
 * @param str The string to convert.
 * @returns The EventType corresponding to the given string.
 */
inline EventType typeFromString(const char* str)
{
    return carb::hashString(str);
}


} // namespace carb::events
