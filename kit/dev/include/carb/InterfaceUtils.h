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
//! @brief Utilities for Carbonite Interface management.
#pragma once

#include "Framework.h"
#include "PluginInitializers.h"
#include "cpp/Atomic.h"

namespace carb
{

#ifndef DOXYGEN_BUILD
namespace detail
{
template <typename InterfaceT, const char* PluginName>
class CachedInterface : public ::carb::detail::Deinit
{
public:
    constexpr CachedInterface() = default;
    ~CachedInterface()
    {
        reset();
    }

    InterfaceT* get(const InterfaceDesc& desc)
    {
        auto iface = m_cachedInterface.load(std::memory_order_acquire);
        CARB_LIKELY_IF(iface)
        {
            CARB_FATAL_UNLESS(
                desc.version == m_cachedVersion,
                "Modules using multiple versions of an interface are not allowed! Ensure that the module's premake "
                "defines <version_macro>=<version_macro_latest> so that the entire module is built with the same "
                "interface version (%s: existing: %d.%d, requested: %d.%d)",
                desc.name, m_cachedVersion.major, m_cachedVersion.minor, desc.version.major, desc.version.minor);
            return iface;
        }
        return getInternal(desc);
    }

    void reset()
    {
        ::carb::Framework* framework = ::carb::getFramework();
        if (!framework)
        {
            // Framework no longer valid or already unloaded.
            return;
        }

        auto iface = m_cachedInterface.exchange(nullptr, std::memory_order_relaxed);
        if (iface)
        {
            framework->removeReleaseHook(iface, sReleaseHook, this);
        }
        framework->removeReleaseHook(nullptr, sFrameworkReleased, this);
        m_reqState.store(NotRequested, std::memory_order_release);
        m_reqState.notify_all();
    }

    [[nodiscard]] bool check() const noexcept
    {
        return m_cachedInterface.load(std::memory_order_relaxed) != nullptr;
    }

private:
    enum RequestState
    {
        NotRequested,
        Requesting,
        Finished,
    };
    std::atomic<InterfaceT*> m_cachedInterface{ nullptr };
    carb::Version m_cachedVersion{};
    carb::cpp::atomic<RequestState> m_reqState{ NotRequested };

    static void sReleaseHook(void* iface, void* this_)
    {
        static_cast<CachedInterface*>(this_)->releaseHook(iface);
    }
    static void sFrameworkReleased(void*, void* this_)
    {
        // The Framework is fully released. Reset our request state.
        static_cast<CachedInterface*>(this_)->reset();
    }
    void releaseHook(void* iface)
    {
        // Clear the cached interface pointer, but don't fully reset. Further attempts to get() will proceed to
        // getInternal(), but will not attempt to acquire the interface again.
        CARB_ASSERT(iface == m_cachedInterface);
        CARB_UNUSED(iface);
        m_cachedInterface.store(nullptr, std::memory_order_relaxed);
    }

    void deinit() override
    {
        reset();
    }

    CARB_NOINLINE InterfaceT* getInternal(const InterfaceDesc& desc)
    {
        ::carb::Framework* framework = ::carb::getFramework();
        if (!framework)
        {
            return nullptr;
        }

        RequestState state = m_reqState.load(std::memory_order_acquire);
        while (state != Finished)
        {
            if (state == NotRequested && m_reqState.compare_exchange_weak(
                                             state, Requesting, std::memory_order_relaxed, std::memory_order_relaxed))
            {
                InterfaceT* iface = framework->tryAcquireInterface<InterfaceT>(PluginName);
                if (!iface)
                {
                    // Failed to acquire. Reset to initial state
                    m_reqState.store(NotRequested, std::memory_order_release);
                    m_reqState.notify_all();
                    return nullptr;
                }
                CARB_UNLIKELY_IF(!framework->addReleaseHook(iface, sReleaseHook, this))
                {
                    // This could only happen if something released the interface between us acquiring it and adding
                    // the release hook. Repeat the process again.
                    state = NotRequested;
                    m_reqState.store(state, std::memory_order_release);
                    m_reqState.notify_all();
                    continue;
                }
                bool b = framework->addReleaseHook(nullptr, sFrameworkReleased, this);
                CARB_UNUSED(b);
                CARB_ASSERT(b);
                m_cachedVersion = desc.version;
                m_cachedInterface.store(iface, std::memory_order_release);
                m_reqState.store(Finished, std::memory_order_release);
                m_reqState.notify_all();
                return iface;
            }
            else if (state == Requesting)
            {
                m_reqState.wait(state, std::memory_order_relaxed);
                state = m_reqState.load(std::memory_order_acquire);
            }
        }
        return m_cachedInterface.load(std::memory_order_relaxed);
    }
};

template <class T, const char* PluginName>
CachedInterface<T, PluginName>& cachedInterface()
{
    static CachedInterface<T, PluginName> cached;
    return cached;
}
} // namespace detail
#endif

/**
 * Retrieves the specified interface as if from Framework::tryAcquireInterface() and caches it for fast retrieval.
 *
 * If the interface is fully released by all clients calling \ref Framework::releaseInterface() (or by calling
 * \ref Framework::unloadAllPlugins), the cached interface will be automatically cleared. For cached interfaces exported
 * by the same client (i.e. plugin) the cache is cleared \a after \ref carbOnPluginShutdown is called. Otherwise the
 * cached interface is cleared \a before \ref carbOnPluginShutdown is called. Calls to getCachedInterface() after this
 * point will return `nullptr`. In order for getCachedInterface() to call \ref Framework::tryAcquireInterface() again,
 * first call \ref resetCachedInterface().
 *
 * Releasing the Carbonite Framework with \ref carb::releaseFramework() automatically resets all cached interfaces as if
 * by calling \ref resetCachedInterface().
 *
 * @thread_safety This function is safe to call simultaneously by multiple threads.
 * @tparam InterfaceT The interface class to retrieve.
 * @tparam PluginName The name of a specific plugin to keep cached. Note: this must be a global char array or `nullptr`.
 * @returns The loaded and acquired interface class if successfully acquired through Framework::tryAcquireInterface(),
 * or a previously cached value. If the interface could not be found, or has been released with releaseFramework(),
 * `nullptr` is returned.
 */
template <typename InterfaceT, const char* PluginName = nullptr>
[[nodiscard]] inline InterfaceT* getCachedInterface()
{
    return ::carb::detail::cachedInterface<InterfaceT, PluginName>().get(InterfaceT::getInterfaceDesc());
}

/**
 * Resets any previously-cached interface of the given type and allows it to be acquired again.
 *
 * @note This does NOT *release* the interface as if Framework::releaseInterface() were called. It merely resets the
 * cached state so that getCachedInterface() will call Framework::tryAcquireInterface() again.
 *
 * @tparam InterfaceT The type of interface class to evict from cache.
 * @tparam PluginName The name of a specific plugin that is cached. Note: this must be a global char array or `nullptr`.
 */
template <typename InterfaceT, const char* PluginName = nullptr>
inline void resetCachedInterface()
{
    ::carb::detail::cachedInterface<InterfaceT, PluginName>().reset();
}

} // namespace carb
