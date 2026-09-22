// SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#pragma once

//! @file
//! @brief Carbonite declarations of functions for TSAN (thread sanitizer) support

#include "../Defines.h"

#include <atomic>

#if defined DOXYGEN_BUILD || CARB_TSAN_ENABLED
//! Macro declaring code that should be instantiated if TSan is enabled.
#    define CARB_IF_TSAN(...) __VA_ARGS__
//! Macro declaring code that should be instantiated if TSan is NOT enabled.
#    define CARB_IF_NOT_TSAN(...)

namespace carb
{
//! A helper type that is `T` if TSan is not enabled, or `std::atomic<T>` if TSan is enabled. Generally used for working
//! around TSan false positives or warnings with complicated (but correct) logic.
template <class T>
using AtomicIfTSan = std::atomic<T>;
} // namespace carb
#else
#    define CARB_IF_TSAN(...)
#    define CARB_IF_NOT_TSAN(...) __VA_ARGS__
namespace carb
{
template <class T>
using AtomicIfTSan = T;
}
#endif

#if CARB_TSAN_ENABLED && defined __has_include && __has_include(<sanitizer/tsan_interface.h>)
// Include the official header
#    include <sanitizer/tsan_interface.h>
#elif !defined SANITIZER_TSAN_INTERFACE_H // from sanitizer/tsan_interface.h (already included)

// Definitions must match sanitizer/tsan_interface.h

#    ifndef DOXYGEN_BUILD
// Mutex has static storage duration and no-op constructor and destructor.
// This effectively makes tsan ignore destroy annotation.
constexpr unsigned __tsan_mutex_linker_init = 1 << 0;
// Mutex is write reentrant.
constexpr unsigned __tsan_mutex_write_reentrant = 1 << 1;
// Mutex is read reentrant.
constexpr unsigned __tsan_mutex_read_reentrant = 1 << 2;
// Mutex does not have static storage duration, and must not be used after
// its destructor runs.  The opposite of __tsan_mutex_linker_init.
// If this flag is passed to __tsan_mutex_destroy, then the destruction
// is ignored unless this flag was previously set on the mutex.
constexpr unsigned __tsan_mutex_not_static = 1 << 8;
// Mutex operation flags:
// Denotes read lock operation.
constexpr unsigned __tsan_mutex_read_lock = 1 << 3;
// Denotes try lock operation.
constexpr unsigned __tsan_mutex_try_lock = 1 << 4;
// Denotes that a try lock operation has failed to acquire the mutex.
constexpr unsigned __tsan_mutex_try_lock_failed = 1 << 5;
// Denotes that the lock operation acquires multiple recursion levels.
// Number of levels is passed in recursion parameter.
// This is useful for annotation of e.g. Java builtin monitors,
// for which wait operation releases all recursive acquisitions of the mutex.
constexpr unsigned __tsan_mutex_recursive_lock = 1 << 6;
// Denotes that the unlock operation releases all recursion levels.
// Number of released levels is returned and later must be passed to
// the corresponding __tsan_mutex_post_lock annotation.
constexpr unsigned __tsan_mutex_recursive_unlock = 1 << 7;

// Flags for __tsan_switch_to_fiber:
// Do not establish a happens-before relation between fibers
constexpr unsigned __tsan_switch_to_fiber_no_sync = 1 << 0;

extern "C"
{
#        if CARB_TSAN_ENABLED
    // __tsan_release establishes a happens-before relation with a preceding
    // __tsan_acquire on the same address.
    void __tsan_acquire(void* addr);
    void __tsan_release(void* addr);

    // Annotate creation of a mutex.
    // Supported flags: mutex creation flags.
    void __tsan_mutex_create(void* addr, unsigned flags);

    // Annotate destruction of a mutex.
    // Supported flags:
    //   - __tsan_mutex_linker_init
    //   - __tsan_mutex_not_static
    void __tsan_mutex_destroy(void* addr, unsigned flags);

    // Annotate start of lock operation.
    // Supported flags:
    //   - __tsan_mutex_read_lock
    //   - __tsan_mutex_try_lock
    //   - all mutex creation flags
    void __tsan_mutex_pre_lock(void* addr, unsigned flags);

    // Annotate end of lock operation.
    // Supported flags:
    //   - __tsan_mutex_read_lock (must match __tsan_mutex_pre_lock)
    //   - __tsan_mutex_try_lock (must match __tsan_mutex_pre_lock)
    //   - __tsan_mutex_try_lock_failed
    //   - __tsan_mutex_recursive_lock
    //   - all mutex creation flags
    void __tsan_mutex_post_lock(void* addr, unsigned flags, int recursion);

    // Annotate start of unlock operation.
    // Supported flags:
    //   - __tsan_mutex_read_lock
    //   - __tsan_mutex_recursive_unlock
    int __tsan_mutex_pre_unlock(void* addr, unsigned flags);

    // Annotate end of unlock operation.
    // Supported flags:
    //   - __tsan_mutex_read_lock (must match __tsan_mutex_pre_unlock)
    void __tsan_mutex_post_unlock(void* addr, unsigned flags);

    // Annotate start/end of notify/signal/broadcast operation.
    // Supported flags: none.
    void __tsan_mutex_pre_signal(void* addr, unsigned flags);
    void __tsan_mutex_post_signal(void* addr, unsigned flags);

    // Annotate start/end of a region of code where lock/unlock/signal operation
    // diverts to do something else unrelated to the mutex. This can be used to
    // annotate, for example, calls into cooperative scheduler or contention
    // profiling code.
    // These annotations must be called only from within
    // __tsan_mutex_pre/post_lock, __tsan_mutex_pre/post_unlock,
    // __tsan_mutex_pre/post_signal regions.
    // Supported flags: none.
    void __tsan_mutex_pre_divert(void* addr, unsigned flags);
    void __tsan_mutex_post_divert(void* addr, unsigned flags);

    // Fiber switching API.
    //   - TSAN context for fiber can be created by __tsan_create_fiber
    //     and freed by __tsan_destroy_fiber.
    //   - TSAN context of current fiber or thread can be obtained
    //     by calling __tsan_get_current_fiber.
    //   - __tsan_switch_to_fiber should be called immediatly before switch
    //     to fiber, such as call of swapcontext.
    //   - Fiber name can be set by __tsan_set_fiber_name.
    void* __tsan_get_current_fiber(void);
    void* __tsan_create_fiber(unsigned flags);
    void __tsan_destroy_fiber(void* fiber);
    void __tsan_switch_to_fiber(void* fiber, unsigned flags);
    void __tsan_set_fiber_name(void* fiber, const char* name);
#        else
    // clang-format off
    inline constexpr void __tsan_acquire(void *) {}
    inline constexpr void __tsan_release(void *) {}
    inline constexpr void __tsan_mutex_create(void *, unsigned) noexcept {}
    inline constexpr void __tsan_mutex_destroy(void *, unsigned) noexcept {}
    inline constexpr void __tsan_mutex_pre_lock(void *, unsigned) noexcept {}
    inline constexpr void __tsan_mutex_post_lock(void *, unsigned, int) noexcept {}
    inline constexpr int __tsan_mutex_pre_unlock(void *, unsigned) noexcept { return 0; }
    inline constexpr void __tsan_mutex_post_unlock(void *, unsigned) noexcept {}
    inline constexpr void __tsan_mutex_pre_signal(void *, unsigned) noexcept {}
    inline constexpr void __tsan_mutex_post_signal(void *, unsigned) noexcept {}
    inline constexpr void __tsan_mutex_pre_divert(void *, unsigned) noexcept {}
    inline constexpr void __tsan_mutex_post_divert(void *, unsigned) noexcept {}
    inline void *__tsan_get_current_fiber(void) noexcept { return nullptr; }
    inline void *__tsan_create_fiber(unsigned) noexcept { return nullptr; }
    inline constexpr void __tsan_destroy_fiber(void *) noexcept {}
    inline constexpr void __tsan_switch_to_fiber(void *, unsigned) noexcept {}
    inline constexpr void __tsan_set_fiber_name(void *, const char *) noexcept {}
// clang-format on
#        endif
}
#    endif
#endif
