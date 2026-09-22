// SPDX-FileCopyrightText: Copyright (c) 2020-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
//! @brief Carbonite Futex implementation.
#pragma once

#include "detail/FutexImpl.h"

#include <atomic>

namespace carb
{
namespace thread
{

/**
 * Futex namespace.
 *
 * @warning Futex is a very low-level system; generally its use should be avoided. There are plenty of higher level
 * synchronization primitives built on top of Futex that should be used instead, such as `carb::cpp::atomic`.
 *
 * FUTEX stands for Fast Userspace muTEX. Put simply, it's a way of efficiently blocking threads by waiting on an
 * address as long as the value at that address matches the expected value. Atomically the value at the address is
 * checked and if it matches the expected value, the thread enters a wait-state (until notified). If the value does not
 * match expectation, the thread does not enter a wait-state. This low-level system is the foundation for many
 * synchronization primitives.
 *
 * On Windows, this functionality is achieved through APIs `WaitOnAddress`, `WakeByAddressSingle` and
 * `WakeByAddressAll` and support values of 1, 2, 4 or 8 bytes. Much of the functionality is implemented without
 * requiring system calls, so attempting to wait when the value is different, or notifying without any waiting threads
 * are very efficient--only a few nanoseconds each. Calls which wait or notify waiting threads will enter the kernel and
 * be on the order of microseconds.
 *
 * The Linux kernel provides a `futex` syscall for this functionality, with two downsides. First, a `futex` can be only
 * four bytes (32-bit), and second due to being a syscall even calls with no work can take nearly a microsecond. macOS
 * has a similar feature in the undocumented `__ulock_wait` and `__ulock_wake` calls.
 *
 * For Linux and macOS, the Carbonite futex system has a user-space layer called `ParkingLot` that supports values of 1,
 * 2, 4 or 8 bytes and eliminates most syscalls unless work must actually be done. This causes no-op work to be on the
 * order of just a few nanoseconds with worst-case timing being comparable to syscall times.
 *
 * Linux information: http://man7.org/linux/man-pages/man2/futex.2.html
 *
 * Windows information: https://docs.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-waitonaddress
 */
struct futex
{

    /**
     * Waits on a value until woken.
     *
     * The value at @p val is atomically compared with @p compare. If the values are not equal, this function returns
     * immediately. Otherwise, if the values are equal, this function sleeps the current thread. Waking is not automatic
     * when the value changes. The thread that changes the value must then call wake() to wake the waiting threads.
     *
     * @note Futexes are prone to spurious wakeups. It is the responsibility of the caller to determine whether a return
     * from wait() is spurious or valid.
     *
     * @param val The value that is read atomically. If this matches @p compare, the thread sleeps.
     * @param compare The expected value.
     */
    template <class T>
    inline static void wait(const std::atomic<T>& val, T compare) noexcept
    {
        detail::Futex<T>::wait(val, compare);
    }

    /**
     * Waits on a value until woken or timed out.
     *
     * The value at @p val is atomically compared with @p compare. If the values are not equal, this function returns
     * immediately. Otherwise, if the values are equal, this function sleeps the current thread. Waking is not automatic
     * when the value changes. The thread that changes the value must then call wake() to wake the waiting threads.
     *
     * @note Futexes are prone to spurious wakeups. It is the responsibility of the caller to determine whether a return
     * from wait() is spurious or valid.
     *
     * @note On Linux, interruptions by signals are treated as spurious wakeups.
     *
     * @param val The value that is read atomically. If this matches @p compare, the thread sleeps.
     * @param compare The expected value.
     * @param duration The relative time to wait.
     * @return `true` if woken legitimately or spuriously; `false` if timed out.
     */
    template <class T, class Rep, class Period>
    inline static bool wait_for(const std::atomic<T>& val, T compare, std::chrono::duration<Rep, Period> duration)
    {
        return detail::Futex<T>::wait_for(val, compare, duration);
    }

    /**
     * Waits on a value until woken or timed out.
     *
     * The value at @p val is atomically compared with @p compare. If the values are not equal, this function returns
     * immediately. Otherwise, if the values are equal, this function sleeps the current thread. Waking is not automatic
     * when the value changes. The thread that changes the value must then call wake() to wake the waiting threads.
     *
     * @note Futexes are prone to spurious wakeups. It is the responsibility of the caller to determine whether a return
     * from wait() is spurious or valid.
     *
     * @param val The value that is read atomically. If this matches @p compare, the thread sleeps.
     * @param compare The expected value.
     * @param time_point The absolute time point to wait until.
     * @return `true` if woken legitimately or spuriously; `false` if timed out.
     */
    template <class T, class Clock, class Duration>
    inline static bool wait_until(const std::atomic<T>& val, T compare, std::chrono::time_point<Clock, Duration> time_point)
    {
        return detail::Futex<T>::wait_until(val, compare, time_point);
    }

    /**
     * Wakes threads that are waiting in one of the @p futex wait functions.
     *
     * @note To wake all threads waiting on @p val, use wake_all().
     *
     * @param val The same value that was passed to wait(), wait_for() or wait_until().
     * @param count The number of threads to wake. To wake all threads, use wake_all().
     * @param maxCount An optimization for Windows that specifies the total number of threads that are waiting on @p
     * addr. If @p count is greater-than-or-equal-to @p maxCount then a specific API call that wakes all threads is
     * used. Ignored on Linux.
     */
    template <class T>
    inline static void notify(std::atomic<T>& val, unsigned count, unsigned maxCount = unsigned(INT_MAX)) noexcept
    {
        if (count != 1 && count >= maxCount)
            detail::Futex<T>::notify_all(val);
        else
            detail::Futex<T>::notify_n(val, count);
    }

    /**
     * Wakes threads that are waiting in one of the @p futex wait functions.
     *
     * @note To wake all threads waiting on @p val, use wake_all().
     *
     * @param val The same value that was passed to wait(), wait_for() or wait_until().
     * @param count The number of threads to wake. To wake all threads, use wake_all().
     */
    template <class T>
    inline static void notify_n(std::atomic<T>& val, unsigned count) noexcept
    {
        detail::Futex<T>::notify_n(val, count);
    }

    //! @copydoc notify()
    template <class T>
    CARB_DEPRECATED("use notify() instead")
    inline static void wake(std::atomic<T>& val, unsigned count, unsigned maxCount = unsigned(INT_MAX)) noexcept
    {
        notify(val, count, maxCount);
    }

    /**
     * Wakes one thread that is waiting in one of the @p futex wait functions.
     *
     * @param val The same value that was passed to wait(), wait_for() or wait_until().
     */
    template <class T>
    inline static void notify_one(std::atomic<T>& val) noexcept
    {
        detail::Futex<T>::notify_one(val);
    }

    //! @copydoc notify_one()
    template <class T>
    CARB_DEPRECATED("use notify_one() instead")
    inline static void wake_one(std::atomic<T>& val) noexcept
    {
        notify_one(val);
    }

    /**
     * Wakes all threads that are waiting in one of the @p futex wait functions
     *
     * @param val The same value that was passed to wait(), wait_for() or wait_until().
     */
    template <class T>
    inline static void notify_all(std::atomic<T>& val) noexcept
    {
        detail::Futex<T>::notify_all(val);
    }

    //! @copydoc notify_all()
    template <class T>
    CARB_DEPRECATED("Use notify_all() instead")
    inline static void wake_all(std::atomic<T>& val) noexcept
    {
        notify_all(val);
    }


}; // struct futex
} // namespace thread
} // namespace carb
