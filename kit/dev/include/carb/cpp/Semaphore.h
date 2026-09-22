// SPDX-FileCopyrightText: Copyright (c) 2019-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! \file
//! \brief C++14-compatible implementation of select functionality from C++ `<semaphore>` library.
#pragma once

#include "Atomic.h"
#include "../thread/Futex.h"

#include <atomic>
#include <chrono>

namespace carb
{
namespace cpp
{
#ifndef DOXYGEN_SHOULD_SKIP_THIS
namespace detail
{

#    if CARB_PLATFORM_WINDOWS
constexpr ptrdiff_t kSemaphoreValueMax = LONG_MAX;
#    else
constexpr ptrdiff_t kSemaphoreValueMax = INT_MAX;
#    endif

} // namespace detail
#endif

// Handle case where Windows.h may have defined 'max'
#pragma push_macro("max")
#undef max

/**
 * C++20-compatible counting semaphore class.
 *
 * A counting_semaphore is a lightweight synchronization primitive that can control access to a shared resource. Unlike
 * a mutex, a counting_semaphore allows more than one concurrent access to the same resource, for at least
 * `least_max_value` concurrent accessors. The program is ill-formed if `least_max_value` is negative.
 *
 * This is a C++14-compatible implementation of std::counting_semaphore from C++20 draft spec dated 11/13/2019.
 *
 * @note `sizeof(counting_semaphore)` is 8 bytes for `least_max_value > 1`. A specialization exists for
 *      `least_max_value == 1` where the size is only 1 byte, also known as @ref binary_semaphore.
 *
 * @tparam least_max_value      The maximum count value that this semaphore can reach. This
 *                              indicates the number of threads or callers that can simultaneously
 *                              successfully acquire this semaphore. May not be less than zero.
 *
 * @thread_safety This class is thread-safe. However, attempting to destruct before all threads have returned from any
 *     function (especially the wait functions) is malformed and will lead to undefined behavior.
 */
template <ptrdiff_t least_max_value = detail::kSemaphoreValueMax>
class CARB_VIZ counting_semaphore
{
    CARB_PREVENT_COPY_AND_MOVE(counting_semaphore);

public:
    /** Constructor: initializes a new semaphore object with a given count.
     *
     *  @param[in] desired  The initial count value for the semaphore.  This must be a positive
     *                      value or zero.  If set to zero, the semaphore will be 'unowned' on
     *                      creation.  If set to any other value, the semaphore will only be able
     *                      to be acquired by at most @a least_max_value minus @p desired other
     *                      threads or callers until it is released @p desired times.
     */
    constexpr explicit counting_semaphore(ptrdiff_t desired) noexcept
        : m_data((uint64_t)::carb_min(::carb_max(ptrdiff_t(0), desired), least_max_value))
    {
        CARB_ASSERT(desired >= 0 && desired <= least_max_value, "Precondition violation: N4950 [thread.sema.cnt]/5");
        static_assert(least_max_value >= 0, "semaphore with negative count is ill-formed");
        static_assert(least_max_value <= detail::kSemaphoreValueMax,
                      "semaphore count too high (must not exceed detail::kSemaphoreValueMax)");
    }

    /**
     * Destructor
     *
     * On Linux, performs a `CARB_CHECK` to verify that no waiters are present when `*this` is destroyed.
     *
     * @note On Windows, `ExitProcess()` (or returning from `main()`) causes all threads to be terminated before
     * `atexit()` registered functions are called (and static objects are cleaned up). This has the unpleasant side
     * effect of potentially terminating threads that are waiting on a semaphore and will never get the chance to clean
     * up their waiting count. Therefore, this check is linux only.
     */
    ~counting_semaphore() noexcept
    {
#if CARB_PLATFORM_LINUX
        // Make sure we don't have any waiters when we are destroyed
        CARB_CHECK((m_data.load(std::memory_order_acquire) >> kWaitersShift) == 0, "Semaphore destroyed with waiters");
#endif
    }

    /** Retrieves the maximum count value this semaphore can reach.
     *
     *  @returns The maximum count value for this semaphore.  This will never be zero.
     *
     *  @thread_safety This call is thread safe.
     */
    static constexpr ptrdiff_t max() noexcept
    {
        return least_max_value;
    }

    /** Releases references on this semaphore and potentially wakes another waiting thread.
     *
     *  @param[in] update   The number of references to atomically increment this semaphore's
     *                      counter by.  This number of waiting threads will be woken as a
     *                      result. This value must be not less than zero and must not exceed
     *                      \ref max().
     *  @return No return value.
     *
     *  @remarks This releases zero or more references on this semaphore.  If a reference is
     *           released, another waiting thread could potentially be woken and acquire this
     *           semaphore again.
     *
     *  @note While std::counting_semaphore::release() allows this function to throw, this
     *        implementation will not. Similar to the MS STL counting_semaphore, this
     *        function will `std::terminate` on precondition violation (that is, if the resulting
     *        semaphore count is less than zero or exceeds \ref max()).
     *
     *  @thread_safety This call is thread safe.
     */
    void release(ptrdiff_t update = 1) noexcept
    {
        CARB_FATAL_UNLESS(update >= 0 && update <= least_max_value, "Precondition violation: N4950 [thread.sema.cnt]/5");

        uint64_t d = m_data.fetch_add(update, std::memory_order_release);
        const ptrdiff_t value(int32_t(d & kValueMask));
        CARB_FATAL_UNLESS(value >= 0 && update <= (least_max_value - value),
                          "Precondition violation: update <= max() - counter (N4950 [thread.sema.cnt]/5)");

        // At this point, the Semaphore could be destroyed by another thread. Therefore, we shouldn't access any other
        // members (taking the reference of m_data below is okay because that would not actually read any memory that
        // may be destroyed)

        // Always issue a wake if there are waiters
        uint64_t const waiters = d >> kWaitersShift;
        if (waiters == 0)
        {
            // nothing to wake
        }
        else if (waiters <= size_t(update))
        {
            m_data.notify_all();
        }
        else
        {
            // Wake at most `update`. Since cpp::atomic does not have a way to notify `n`, we use futex directly.
            thread::futex::notify(m_data, unsigned(size_t(update)));
        }
    }

    /** Acquires a reference to this semaphore.
     *
     *  @returns No return value.
     *
     *  @remarks This blocks until a reference to this semaphore can be successfully acquired.
     *           This is done by atomically decrementing the semaphore's counter if it is greater
     *           than zero.  If the counter is zero, this will block until the counter is greater
     *           than zero.  The counter is incremented by calling release().
     *
     *  @thread_safety This call is thread safe.
     */
    void acquire() noexcept
    {
        CARB_LIKELY_IF(fast_acquire(false))
        {
            return;
        }

        // Register as a waiter
        uint64_t d = m_data.fetch_add(kOneWaiter, std::memory_order_relaxed) + kOneWaiter;
        for (;;)
        {
            if ((d & kValueMask) != 0)
            {
                // Try to unregister as a waiter and grab a token at the same time
                CARB_LIKELY_IF(m_data.compare_exchange_weak(
                    d, d - 1 - kOneWaiter, std::memory_order_acquire, std::memory_order_relaxed))
                {
                    return;
                }
            }
            else
            {
                // Need to wait
                m_data.wait(d, std::memory_order_relaxed);

                // Reload
                d = m_data.load(std::memory_order_relaxed);
            }
        }
    }

    /** Attempts to acquire a reference to this semaphore.
     *
     *  @returns `true` if the semaphore's counter was greater than zero and it was successfully
     *           atomically decremented.  Returns `false` if the counter was zero and the
     *           semaphore could not be acquired.  This will never block even if the semaphore
     *           could not be acquired.
     *
     *  @thread_safety This call is thread safe.
     */
    bool try_acquire() noexcept
    {
        return fast_acquire(true);
    }

    /** Attempts to acquire a reference to this semaphore for a specified relative time.
     *
     *  @tparam Rep     The representation primitive type for the duration value.
     *  @tparam Period  The duration's time scale value (ie: milliseconds, seconds, etc).
     *  @param[in] duration The amount of time to try to acquire this semaphore for.  This is
     *                      specified as a duration relative to the call time.
     *  @returns `true` if the semaphore's counter was greater than zero and it was successfully
     *           atomically decremented within the specified time limit.  Returns `false` if the
     *           counter was zero and the semaphore could not be acquired within the time limit.
     *           This will only block for up to approximately the specified time limit.
     *
     *  @thread_safety This call is thread safe.
     */
    template <class Rep, class Period>
    bool try_acquire_for(const std::chrono::duration<Rep, Period>& duration) noexcept
    {
        if (duration.count() <= 0)
            return try_acquire();

        CARB_LIKELY_IF(fast_acquire(false))
        {
            return true;
        }

        // Register as a waiter
        uint64_t d = m_data.fetch_add(kOneWaiter, std::memory_order_relaxed) + kOneWaiter;
        while ((d & kValueMask) != 0)
        {
            // Try to unregister as a waiter and grab a token at the same time
            CARB_LIKELY_IF(m_data.compare_exchange_weak(
                d, d - 1 - kOneWaiter, std::memory_order_acquire, std::memory_order_relaxed))
            {
                return true;
            }
        }

        // Now we need to wait, but do it with absolute time so that we properly handle spurious futex wakeups
        auto const deadline = cpp::detail::absTime<std::chrono::steady_clock>(duration);
        for (;;)
        {
            if ((d & kValueMask) != 0)
            {
                // Try to unreference as a waiter and grab a token at the same time
                CARB_LIKELY_IF(m_data.compare_exchange_weak(
                    d, d - 1 - kOneWaiter, std::memory_order_acquire, std::memory_order_relaxed))
                {
                    return true;
                }
            }
            else
            {
                // Need to wait
                CARB_UNLIKELY_IF(!m_data.wait_until(d, deadline, std::memory_order_relaxed))
                {
                    // Timed out. Unregister as a waiter
                    m_data.fetch_sub(kOneWaiter, std::memory_order_relaxed);
                    return false;
                }

                // Reload after wait
                d = m_data.load(std::memory_order_relaxed);
            }
        }
    }

    /** Attempts to acquire a reference to this semaphore until a specified absolute time.
     *
     *  @tparam Clock       The clock to use as a time source to compare the time limit to.
     *  @tparam Duration    The duration type associated with the specified clock.
     *  @param[in] time_point   The absolute time to try to acquire this semaphore for.  This is
     *                          specified as a time point from the given clock @a Clock.
     *  @returns `true` if the semaphore's counter was greater than zero and it was successfully
     *           atomically decremented before the specified time limit.  Returns `false` if the
     *           counter was zero and the semaphore could not be acquired before the time limit.
     *           This will only block up until approximately the specified time limit.
     *
     *  @thread_safety This call is thread safe.
     */
    template <class Clock, class Duration>
    bool try_acquire_until(const std::chrono::time_point<Clock, Duration>& time_point) noexcept
    {
        CARB_LIKELY_IF(fast_acquire(false))
        {
            return true;
        }

        // Register as a waiter
        uint64_t d = m_data.fetch_add(kOneWaiter, std::memory_order_relaxed) + kOneWaiter;
        for (;;)
        {
            if ((d & kValueMask) != 0)
            {
                // Try to unregister as a waiter and grab a token at the same time
                CARB_LIKELY_IF(m_data.compare_exchange_weak(
                    d, d - 1 - kOneWaiter, std::memory_order_acquire, std::memory_order_relaxed))
                {
                    return true;
                }
            }
            else
            {
                // Need to wait
                CARB_UNLIKELY_IF(!m_data.wait_until(d, time_point, std::memory_order_relaxed))
                {
                    // Timed out. Unregister as a waiter
                    m_data.fetch_sub(kOneWaiter, std::memory_order_relaxed);
                    return false;
                }

                // Reload after wait
                d = m_data.load(std::memory_order_relaxed);
            }
        }
    }

private:
    // The 32 most significant bits are the waiters; the lower 32 bits is the value of the semaphore
    CARB_VIZ cpp::atomic_uint64_t m_data;
    constexpr static int kWaitersShift = 32;
    constexpr static uint64_t kOneWaiter = uint64_t(1) << kWaitersShift;
    constexpr static unsigned kValueMask = 0xffffffff;

    CARB_ALWAYS_INLINE bool fast_acquire(bool needResolution) noexcept
    {
        // According to the standard, release() strongly happens before invocations of try_acquire that observe the
        // result of the effects, so synchronize-with release() with memory_order_acquire here.
        uint64_t d = m_data.load(needResolution ? std::memory_order_acquire : std::memory_order_relaxed);
        for (;;)
        {
            if (!(d & kValueMask))
                return false;

            CARB_LIKELY_IF(m_data.compare_exchange_weak(d, d - 1, std::memory_order_acquire, std::memory_order_relaxed))
            {
                return true;
            }

            if (!needResolution)
                return false;
        }
    }
};

#ifndef DOXYGEN_SHOULD_SKIP_THIS
/** Specialization for the case of a semaphore with a maximum count of 1.  This is treated as
 *  a binary semaphore - it can only be acquired by one caller at a time.
 */
template <>
class CARB_VIZ counting_semaphore<1>
{
    CARB_PREVENT_COPY_AND_MOVE(counting_semaphore);

public:
    static constexpr ptrdiff_t max() noexcept
    {
        return 1;
    }

    constexpr explicit counting_semaphore(ptrdiff_t desired) noexcept
        : m_val(uint8_t(size_t(::carb_min(::carb_max(ptrdiff_t(0), desired), max()))))
    {
        CARB_ASSERT(
            desired == 0 || desired == 1, "Precondition violation: desired must be 0 or 1 (N4950 [thread.sema.cnt]/5)");
    }

    void release(ptrdiff_t update = 1) noexcept
    {
        if (update == 0)
            return;

        CARB_FATAL_UNLESS(update == 1, "Precondition violation: update must be 0 or 1 (N4950 [thread.sema.cnt]/5)");

        // Our notify_one() is very fast if nothing is actually waiting. Therefore, don't bother with a slower
        // exchange() here, just store and notify.
        m_val.store(1, std::memory_order_release);
        m_val.notify_one();
    }

    void acquire() noexcept
    {
        while (!try_acquire())
        {
            m_val.wait(0, std::memory_order_relaxed);
        }
    }

    bool try_acquire() noexcept
    {
        uint8_t old = m_val.exchange(0, std::memory_order_acquire);
        CARB_ASSERT(old <= 1); // m_val can only be 0 or 1 (possible precondition violation)
        return old == 1;
    }

    template <class Rep, class Period>
    bool try_acquire_for(const std::chrono::duration<Rep, Period>& duration) noexcept
    {
        // Attempt to acquire before we do the deadline calculations
        CARB_LIKELY_IF(try_acquire())
        {
            return true;
        }

        auto deadline = cpp::detail::absTime<std::chrono::steady_clock>(duration);
        do
        {
            CARB_UNLIKELY_IF(!m_val.wait_until(0, deadline, std::memory_order_relaxed))
            {
                return false;
            }
        } while (!try_acquire());

        return true;
    }

    template <class Clock, class Duration>
    bool try_acquire_until(const std::chrono::time_point<Clock, Duration>& time_point) noexcept
    {
        while (!try_acquire())
        {
            CARB_UNLIKELY_IF(!m_val.wait_until(0, time_point, std::memory_order_relaxed))
            {
                return false;
            }
        }

        return true;
    }

private:
    CARB_VIZ cpp::atomic_uint8_t m_val;
};
#endif

/** Alias for a counting semaphore that can only be acquired by one caller at a time. */
using binary_semaphore = counting_semaphore<1>;

#pragma pop_macro("max")

} // namespace cpp
} // namespace carb
