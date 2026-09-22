// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include "../variant/IVariant.h"
#include "../variant/VariantUtils.h"
#include "../InterfaceUtils.h"


#include <algorithm>
#include <array>
#include <functional>
#include <utility>
#include <vector>

namespace carb
{
namespace eventdispatcher
{


inline constexpr ObserverGuard::ObserverGuard() noexcept : m_o(kInvalidObserver)
{
}

inline constexpr ObserverGuard::ObserverGuard(Observer o) noexcept : m_o(o)
{
}

inline constexpr ObserverGuard::ObserverGuard(std::nullptr_t) noexcept : m_o(kInvalidObserver)
{
}

inline ObserverGuard::ObserverGuard(ObserverGuard&& other) noexcept : m_o(std::exchange(other.m_o, kInvalidObserver))
{
}

inline ObserverGuard::~ObserverGuard() noexcept
{
    reset();
}

inline ObserverGuard& ObserverGuard::operator=(ObserverGuard&& other) noexcept
{
    swap(other);
    return *this;
}

inline ObserverGuard& ObserverGuard::operator=(std::nullptr_t) noexcept
{
    reset();
    return *this;
}

inline Observer ObserverGuard::release() noexcept
{
    return std::exchange(m_o, kInvalidObserver);
}

inline void ObserverGuard::reset(Observer o) noexcept
{
    if (m_o != kInvalidObserver)
    {
        auto iface = carb::getCachedInterface<IEventDispatcher>();

        // this interface can fail to be acquired on shutdown when kit is launched as part of
        // a Python script => just allow the object to leak in that case.
        if (CARB_LIKELY(iface != nullptr))
            iface->stopObserving(m_o);
    }
    m_o = o;
}

inline void ObserverGuard::swap(ObserverGuard& o) noexcept
{
    std::swap(m_o, o.m_o);
}

constexpr inline Observer ObserverGuard::get() const noexcept
{
    return m_o;
}

inline ObserverGuard::operator bool() const noexcept
{
    return m_o != kInvalidObserver;
}

inline bool operator==(const ObserverGuard& lhs, const ObserverGuard& rhs)
{
    return lhs.get() == rhs.get();
}

inline bool operator!=(const ObserverGuard& lhs, const ObserverGuard& rhs)
{
    return lhs.get() != rhs.get();
}

inline bool operator<(const ObserverGuard& lhs, const ObserverGuard& rhs)
{
    return lhs.get() < rhs.get();
}

inline void swap(ObserverGuard& lhs, ObserverGuard& rhs) noexcept
{
    lhs.swap(rhs);
}

#if CARB_VERSION_ATLEAST(carb_eventdispatcher_IEventDispatcher, 1, 1)
template <class Invocable, class... Args>
[[nodiscard]] ObserverGuard IEventDispatcher::observeEvent(
    RStringKey observerName, Order order, RString eventName, Invocable&& invocable, Args&&... filterArgs)
{
    using FunctionType = std::function<void(const Event&)>;
    auto pFunc = new FunctionType{ std::forward<Invocable>(invocable) };
    std::array<NamedVariant, sizeof...(filterArgs)> variants{ detail::translate(std::forward<Args>(filterArgs))... };
    std::sort(variants.begin(), variants.end(), detail::NamedVariantLess{});
    return ObserverGuard(
        internalObserveEvent2({ sizeof(ObserveEventDesc), observerName, order, eventName, variants,
                                [](const Event& event, void* ud) { (*static_cast<FunctionType*>(ud))(event); },
                                [](void* ud) { delete static_cast<FunctionType*>(ud); }, pFunc }));
}

template <class Invocable, class InIter>
[[nodiscard]] ObserverGuard IEventDispatcher::observeEventIter(
    RStringKey observerName, Order order, RString eventName, Invocable&& invocable, InIter begin, InIter end)
{
    using FunctionType = std::function<void(const Event&)>;
    auto pFunc = new FunctionType{ std::forward<Invocable>(invocable) };
    std::vector<NamedVariant> variants;
    while (begin != end)
        variants.emplace_back(detail::translate(*(begin++)));
    std::sort(variants.begin(), variants.end(), detail::NamedVariantLess{});
    return ObserverGuard(
        internalObserveEvent2({ sizeof(ObserveEventDesc), observerName, order, eventName, variants,
                                [](const Event& event, void* ud) { (*static_cast<FunctionType*>(ud))(event); },
                                [](void* ud) { delete static_cast<FunctionType*>(ud); }, pFunc }));
}
#else
template <class Invocable, class... Args>
[[nodiscard]] ObserverGuard IEventDispatcher::observeEvent(Order order,
                                                           RString eventName,
                                                           Invocable&& invocable,
                                                           Args&&... filterArgs)
{
    using FunctionType = std::function<void(const Event&)>;
    auto pFunc = new FunctionType{ std::forward<Invocable>(invocable) };
    std::array<NamedVariant, sizeof...(filterArgs)> variants{ detail::translate(std::forward<Args>(filterArgs))... };
    std::sort(variants.begin(), variants.end(), detail::NamedVariantLess{});
    return ObserverGuard(
        internalObserveEvent(order, eventName, variants.size(), variants.data(),
                             [](const Event& event, void* ud) { (*static_cast<FunctionType*>(ud))(event); },
                             [](void* ud) { delete static_cast<FunctionType*>(ud); }, pFunc));
}

template <class Invocable, class InIter>
[[nodiscard]] ObserverGuard IEventDispatcher::observeEventIter(
    Order order, RString eventName, Invocable&& invocable, InIter begin, InIter end)
{
    using FunctionType = std::function<void(const Event&)>;
    auto pFunc = new FunctionType{ std::forward<Invocable>(invocable) };
    std::vector<NamedVariant> variants;
    while (begin != end)
        variants.emplace_back(detail::translate(*(begin++)));
    std::sort(variants.begin(), variants.end(), detail::NamedVariantLess{});
    return ObserverGuard(
        internalObserveEvent(order, eventName, variants.size(), variants.data(),
                             [](const Event& event, void* ud) { (*static_cast<FunctionType*>(ud))(event); },
                             [](void* ud) { delete static_cast<FunctionType*>(ud); }, pFunc));
}
#endif

template <class... Args>
bool IEventDispatcher::hasObservers(RString eventName, Args&&... filterArgs)
{
    std::array<NamedVariant, sizeof...(filterArgs)> variants{ detail::translate(std::forward<Args>(filterArgs))... };
    std::sort(variants.begin(), variants.end(), detail::NamedVariantLess{});
    CARB_ASSERT(std::adjacent_find(variants.begin(), variants.end(), detail::NamedVariantEqual{}) == variants.end(),
                "At least one non-unique key specified");
    return internalHasObservers(eventName, variants.size(), variants.data());
}

template <class InIter>
bool IEventDispatcher::hasObserversIter(RString eventName, InIter begin, InIter end)
{
    std::vector<NamedVariant> variants;
    while (begin != end)
        variants.emplace_back(detail::translate(*(begin++)));
    std::sort(variants.begin(), variants.end(), detail::NamedVariantLess{});
    CARB_ASSERT(std::adjacent_find(variants.begin(), variants.end(), detail::NamedVariantEqual{}) == variants.end(),
                "At least one non-unique key specified");
    return internalHasObservers(eventName, variants.size(), variants.data());
}

inline size_t IEventDispatcher::dispatchEvent(const Event& event, RString* newEventName)
{
    return internalDispatch({ newEventName ? *newEventName : event.eventName, event.numVariants, event.variants });
}

template <class... Args>
size_t IEventDispatcher::dispatchEvent(RString eventName, Args&&... payload)
{
    std::array<NamedVariant, sizeof...(payload)> variants{ detail::translate(std::forward<Args>(payload))... };
    std::sort(variants.begin(), variants.end(), detail::NamedVariantLess{});
    CARB_ASSERT(std::adjacent_find(variants.begin(), variants.end(), detail::NamedVariantEqual{}) == variants.end(),
                "Event has duplicate keys");
    return internalDispatch({ eventName, variants.size(), variants.data() });
}

template <class InIter>
size_t IEventDispatcher::dispatchEventIter(RString eventName, InIter begin, InIter end)
{
    std::vector<NamedVariant> variants;
    while (begin != end)
        variants.emplace_back(detail::translate(*(begin++)));
    std::sort(variants.begin(), variants.end(), detail::NamedVariantLess{});
    CARB_ASSERT(std::adjacent_find(variants.begin(), variants.end(), detail::NamedVariantEqual{}) == variants.end(),
                "Event has duplicate keys");
    return internalDispatch({ eventName, variants.size(), variants.data() });
}

#if CARB_VERSION_ATLEAST(carb_eventdispatcher_IEventDispatcher, 1, 4)

template <class... Args>
void IEventDispatcher::iterateObservers(RString eventName, const omni::function<void(Observer)>& fn, Args&&... filterArgs)
{
    std::array<NamedVariant, sizeof...(filterArgs)> variants{ detail::translate(std::forward<Args>(filterArgs))... };
    std::sort(variants.begin(), variants.end(), detail::NamedVariantLess{});
    CARB_ASSERT(std::adjacent_find(variants.begin(), variants.end(), detail::NamedVariantEqual{}) == variants.end(),
                "At least one non-unique key specified");
    return internalIterateObservers(eventName, fn, variants.size(), variants.data());
}

#endif


} // namespace eventdispatcher
} // namespace carb

// Specialization for std::hash
template <>
struct std::hash<::carb::eventdispatcher::ObserverGuard>
{
    size_t operator()(const ::carb::eventdispatcher::ObserverGuard& g) const noexcept
    {
        return std::hash<carb::eventdispatcher::Observer>{}(g.get());
    }
};
