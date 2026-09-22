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
//! @brief omni.kit.app utilities
#pragma once

#include "../../carb/InterfaceUtils.h"
#include "../../carb/cpp/StringView.h"
#include "../../carb/eventdispatcher/IEventDispatcher.h"
#include "../../carb/eventdispatcher/IMessageQueue.h"

#include "IApp.h"

namespace omni::kit
{

/**
 * Immediately dispatches an Event and then queues it to the given RunLoop.
 *
 * @param deferredEventName The event name to defer. This is the "normal" event name.
 * @param immediateEventName The event name to dispatch immediately. This is typically \p deferredEventName with a
 *   string suffix `:immediate`.
 * @param runloopName The name of the \ref RunLoop to queue the deferred event to. If empty, \ref kRunLoopDefault is
 *   inferred.
 * @param payload Zero or more key/value `std::pair` objects of type `std::pair<carb::RStringKey, T>` where the first
 *   parameter is the key and the second is the value. The value must be of a type understood by a
 *   \ref carb::variant::Translator specialization.
 * @returns `true` if the message was both dispatched immediately and deferred; `false` if an error occurred.
 */
template <class... Args>
bool queueEventToRunLoop(carb::RString deferredEventName,
                         carb::RString immediateEventName,
                         const carb::cpp::string_view runloopName,
                         Args&&... payload)
{
    using namespace carb;
    auto ed = getCachedInterface<eventdispatcher::IEventDispatcher>();
    auto mqf = getCachedInterface<eventdispatcher::IMessageQueueFactory>();
    if (!ed || !mqf)
        return false;

    std::array<eventdispatcher::NamedVariant, sizeof...(payload)> variants{ eventdispatcher::detail::translate(
        std::forward<Args>(payload))... };
    if constexpr (sizeof...(payload) != 0)
    {
        std::sort(variants.begin(), variants.end(), eventdispatcher::detail::NamedVariantLess{});
        CARB_ASSERT(std::adjacent_find(variants.begin(), variants.end(), eventdispatcher::detail::NamedVariantEqual{}) ==
                        variants.end(),
                    "Event has duplicate keys");
    }

    eventdispatcher::EventData event = { immediateEventName, variants.size(), variants.data() };
    ed->internalDispatch(event);

    RStringKey mqName;

    if (runloopName.empty() || runloopName == cpp::string_view(kRunLoopDefault))
    {
        mqName = kGlobalMessageBus;
    }
    else
    {
        omni::string scratch;
        constexpr static cpp::string_view kPrefix("runloop:");
        constexpr static cpp::string_view kSuffix(":messageBus");
        scratch.reserve(kPrefix.size() + kSuffix.size() + runloopName.size());
        scratch.append(kPrefix);
        scratch.append(runloopName);
        scratch.append(kSuffix);

        mqName = RStringKey(scratch.c_str(), scratch.length());
    }

    auto mq = mqf->getMessageQueue(mqName);

    CARB_UNLIKELY_IF(!mq)
    {
        if (auto app = carb::getCachedInterface<IApp>())
        {
            app->ensureRunLoop(runloopName.empty() ? kRunLoopDefault : omni::string(runloopName).c_str());
        }
        // Try again after ensuring the runloop
        mq = mqf->getMessageQueue(mqName);
        if (!mq)
            return false;
    }

    eventdispatcher::IMessageQueue::ExpectedType expect;
    event.eventName = deferredEventName;
    mq->internalPush(expect, event, false, nullptr, nullptr);
    return expect.has_value();
}

/**
 * Immediately dispatches an Event and then queues it to the *main* RunLoop.
 *
 * @param deferredEventName The event name to defer. This is the "normal" event name.
 * @param immediateEventName The event name to dispatch immediately. This is typically \p deferredEventName with a
 *   string suffix `:immediate`.
 * @param payload Zero or more key/value `std::pair` objects of type `std::pair<carb::RStringKey, T>` where the first
 *   parameter is the key and the second is the value. The value must be of a type understood by a
 *   \ref carb::variant::Translator specialization.
 * @returns `true` if the message was both dispatched immediately and deferred; `false` if an error occurred.
 */
template <class... Args>
bool queueEvent(carb::RString deferredEventName, carb::RString immediateEventName, Args&&... payload)
{
    return queueEventToRunLoop(deferredEventName, immediateEventName, kRunLoopDefault, std::forward<Args>(payload)...);
}

} // namespace omni::kit
