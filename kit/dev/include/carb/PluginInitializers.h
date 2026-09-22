// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
//! @brief Utilities to ease the creation of Carbonite plugins.
#pragma once

#include "Defines.h"

#include <atomic>

namespace carb
{
#ifndef DOXYGEN_BUILD
void pluginDeinitialize();

namespace detail
{

inline bool& initialized() noexcept
{
    static bool init = false;
    return init;
}

class Deinit
{
private:
    friend void ::carb::pluginDeinitialize();

    static std::atomic<Deinit*>& chain() noexcept
    {
        static std::atomic<Deinit*> s_chain{ nullptr };
        return s_chain;
    }
    static void call() noexcept
    {
        auto p = chain().load(std::memory_order_relaxed);
        for (decltype(p) next; p; p = next)
        {
            next = p->m_next;
#    if CARB_EXCEPTIONS_ENABLED
            try
            {
                p->deinit();
            }
            catch (...)
            {
            }
#    else
            p->deinit();
#    endif
        }
    }

    Deinit* m_next{ nullptr };

protected:
    virtual void deinit() = 0;

    Deinit() : m_next(chain().load(std::memory_order_relaxed))
    {
        while (!chain().compare_exchange_strong(m_next, this))
        {
        }
    }
};

} // namespace detail
#endif
struct Framework;
namespace logging
{
void registerLoggingForClient() noexcept;
void deregisterLoggingForClient() noexcept;
} // namespace logging
namespace profiler
{
void registerProfilerForClient() noexcept;
void deregisterProfilerForClient() noexcept;
} // namespace profiler
namespace assert
{
void registerAssertForClient() noexcept;
void deregisterAssertForClient() noexcept;
} // namespace assert
namespace l10n
{
void registerLocalizationForClient() noexcept;
void deregisterLocalizationForClient() noexcept;
} // namespace l10n

/**
 * Function called automatically at plugin startup to initialize utilities within each plugin.
 */
inline void pluginInitialize()
{
    if (detail::initialized())
        return;
    carb::detail::initialized() = true;

    logging::registerLoggingForClient();
    profiler::registerProfilerForClient();
    assert::registerAssertForClient();
    l10n::registerLocalizationForClient();
}

/**
 * Function called automatically at plugin shutdown to de-initialize utilities within each plugin.
 */
inline void pluginDeinitialize()
{
    if (!detail::initialized())
        return;
    carb::detail::initialized() = false;

    // Execute the deinit chain
    detail::Deinit::call();

    assert::deregisterAssertForClient();
    profiler::deregisterProfilerForClient();
    logging::deregisterLoggingForClient();
    l10n::deregisterLocalizationForClient();
}

} // namespace carb
