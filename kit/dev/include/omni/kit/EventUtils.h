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
//! @brief omni.kit.app event utilities
#pragma once

#include <carb/InterfaceUtils.h>
#include <carb/eventdispatcher/IEventDispatcher.h>
#include <carb/eventdispatcher/IMessageQueue.h>

namespace omni::kit
{

/**
 * Immediately dispatches an Event and then queues it to the given message queue.
 *
 * @param eventName The event name to defer. This is the "normal" event name.
 * @param immediateEventName The event name to dispatch immediately. This is typically \p eventName with a
 *   string suffix `:immediate`.
 * @param mq A reference to the message queue that the event should be queued to.
 * @param args Zero or more key/value `std::pair` objects of type `std::pair<carb::RStringKey, T>` where the first
 *   parameter is the key and the second is the value. The value must be of a type understood by a
 *   `carb::variant::Translator` specialization.
 * @returns `true` if the event was both dispatched immediately and deferred; `false` if an error occurred.
 */
template<class... Args>
bool pushEventToQueue(carb::RString eventName, carb::RString immediateEventName, carb::eventdispatcher::IMessageQueue& mq, Args&&... args) noexcept
{
    using namespace carb;

    auto ed = getCachedInterface<eventdispatcher::IEventDispatcher>();
    CARB_UNLIKELY_IF(!ed)
    {
        return false;
    }
    
    std::array<eventdispatcher::NamedVariant, sizeof...(args)> variants{ eventdispatcher::detail::translate(
        std::forward<Args>(args))... };
    if constexpr (sizeof...(args) != 0)
    {
        std::sort(variants.begin(), variants.end(), eventdispatcher::detail::NamedVariantLess{});
        CARB_ASSERT(std::adjacent_find(variants.begin(), variants.end(), eventdispatcher::detail::NamedVariantEqual{}) ==
                        variants.end(),
                    "Event has duplicate keys");
    }

    eventdispatcher::EventData event = { immediateEventName, variants.size(), variants.data() };
    ed->internalDispatch(event);

    eventdispatcher::IMessageQueue::ExpectedType expect;
    event.eventName = eventName;
    mq.internalPush(expect, event, false, nullptr, nullptr);
    return expect.has_value();
}

/**
 * Pops all entries from a message queue and dispatches them.
 * @param mq A reference to the `carb::eventdispatcher::IMessageQueue` to pop until empty.
 * @retval true All events were popped from the message queue and dispatched.
 * @retval false An error occurred.
 */
inline bool pumpQueue(carb::eventdispatcher::IMessageQueue& mq) noexcept
{
    using namespace carb::eventdispatcher;

    // It shouldn't be possible for `ed` to be `nullptr` because we have a valid `mq`.
    auto ed = carb::getCachedInterface<IEventDispatcher>();

    IMessageQueue::ExpectedType expect;
    do
    {
        expect = mq.pop([&](const Event& e) { ed->internalDispatch(e); });
    } while (expect.has_value());

    return expect.has_value();
}

}
