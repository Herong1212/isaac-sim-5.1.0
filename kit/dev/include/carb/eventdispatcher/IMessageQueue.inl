// SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#ifdef __INTELLISENSE__
#    include "IMessageQueue.h"
#endif

#include "../variant/IVariant.h"
#include "../variant/VariantUtils.h"
#include "../tasking/TaskingHelpers.h"

namespace carb
{
namespace eventdispatcher
{

///////////////////////////////////////////////////////////////////////////////
// IMessageQueueFactory
inline omni::expected<std::pair<IMessageQueuePtr, bool>, omni::core::Result> IMessageQueueFactory::createMessageQueue(
    RStringKey name, const MessageQueueParams& params)
{
    bool existing;
    omni::core::Result result;
    auto p = internalCreateMessageQueue(name, params, result, existing);
    if (p)
    {
        IMessageQueuePtr ptr(p, IMessageQueuePtr::InitPolicy::eSteal);
        return omni::expected<std::pair<IMessageQueuePtr, bool>, omni::core::Result>(
            std::make_pair(std::move(ptr), !existing));
    }

    return omni::unexpected<omni::core::Result>(result);
}

inline IMessageQueuePtr IMessageQueueFactory::getMessageQueue(RStringKey name)
{
    return IMessageQueuePtr(internalGetMessageQueue(name), IMessageQueuePtr::InitPolicy::eSteal);
}

///////////////////////////////////////////////////////////////////////////////
// IMessageQueue

template <class Func>
inline auto IMessageQueue::peek(Func&& func) const -> ExpectedType
{
    using Func_t = std::decay_t<Func>;
    ExpectedType result;
    internalPeek(result, +[](const Event& evt, void* ud) { (*static_cast<Func_t*>(ud))(evt); }, &func);
    return result;
}

template <class Func>
inline auto IMessageQueue::pop(Func&& func) -> ExpectedType
{
    using Func_t = std::decay_t<Func>;
    ExpectedType result;
    internalPop(result, +[](const Event& evt, void* ud) { (*static_cast<Func_t*>(ud))(evt); }, &func);
    return result;
}

inline auto IMessageQueue::awaitMessage() const -> ExpectedType
{
    omni::expected<void, omni::core::Result> result;
    internalAwaitMessage(result, carb::tasking::kInfinite, nullptr, nullptr);
    return result;
}

template <class Rep, class Period>
auto IMessageQueue::awaitMessageFor(const std::chrono::duration<Rep, Period>& duration) const -> ExpectedType
{
    omni::expected<void, omni::core::Result> result;
    internalAwaitMessage(result, tasking::detail::convertDuration(duration), nullptr, nullptr);
    return result;
}

template <class Clock, class Duration>
auto IMessageQueue::awaitMessageUntil(const std::chrono::time_point<Clock, Duration>& when) const -> ExpectedType
{
    omni::expected<void, omni::core::Result> result;
    internalAwaitMessage(result, tasking::detail::convertAbsTime(when), nullptr, nullptr);
    return result;
}

inline auto IMessageQueue::stop() -> ExpectedType
{
    ExpectedType result;
    internalStop(result);
    return result;
}

template <class... Args>
auto IMessageQueue::pushAsync(RString eventName, Args&&... payload) -> ExpectedType
{
    std::array<NamedVariant, sizeof...(payload)> variants{ detail::translate(std::forward<Args>(payload))... };
    std::sort(variants.begin(), variants.end(), detail::NamedVariantLess{});
    CARB_ASSERT(std::adjacent_find(variants.begin(), variants.end(), detail::NamedVariantEqual{}) == variants.end(),
                "Message has duplicate keys");
    EventData data{ eventName, variants.size(), variants.data() };
    ExpectedType result;
    internalPush(result, data, false, nullptr, nullptr);
    return result;
}

template <class InIter>
auto IMessageQueue::pushAsyncIter(RString eventName, InIter begin, InIter end) -> ExpectedType
{
    std::vector<NamedVariant> variants;
    while (begin != end)
        variants.emplace_back(detail::translate(*(begin++)));
    std::sort(variants.begin(), variants.end(), detail::NamedVariantLess{});
    CARB_ASSERT(std::adjacent_find(variants.begin(), variants.end(), detail::NamedVariantEqual{}) == variants.end(),
                "Message has duplicate keys");
    EventData data{ eventName, variants.size(), variants.data() };
    ExpectedType result;
    internalPush(result, data, false, nullptr, nullptr);
    return result;
}

template <class... Args>
auto IMessageQueue::pushAndWait(RString eventName, Args&&... payload) -> ExpectedType
{
    std::array<NamedVariant, sizeof...(payload)> variants{ detail::translate(std::forward<Args>(payload))... };
    std::sort(variants.begin(), variants.end(), detail::NamedVariantLess{});
    CARB_ASSERT(std::adjacent_find(variants.begin(), variants.end(), detail::NamedVariantEqual{}) == variants.end(),
                "Message has duplicate keys");
    EventData data{ eventName, variants.size(), variants.data() };
    ExpectedType result;
    internalPush(result, data, true, nullptr, nullptr);
    return result;
}

template <class InIter>
auto IMessageQueue::pushAndWaitIter(RString eventName, InIter begin, InIter end) -> ExpectedType
{
    std::vector<NamedVariant> variants;
    while (begin != end)
        variants.emplace_back(detail::translate(*(begin++)));
    std::sort(variants.begin(), variants.end(), detail::NamedVariantLess{});
    CARB_ASSERT(std::adjacent_find(variants.begin(), variants.end(), detail::NamedVariantEqual{}) == variants.end(),
                "Message has duplicate keys");
    EventData data{ eventName, variants.size(), variants.data() };
    ExpectedType result;
    internalPush(result, data, true, nullptr, nullptr);
    return result;
}

} // namespace eventdispatcher
} // namespace carb
