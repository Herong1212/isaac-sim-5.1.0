// SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! \file
//! \brief C++14-compatible implementation of select functionality from C++ `<thread>` library.
#pragma once

#include "../CarbWindows.h"

#if CARB_POSIX
#    include <time.h>
#endif

#include <thread>

namespace carb
{
namespace cpp
{
//! \cond DEV
namespace detail
{

template <class Duration>
[[nodiscard]] Duration clampDuration(Duration offset)
{
    // NOTE: This function may not use any thread-safe statics (OVCC-1549)
    using namespace std::chrono;
    constexpr Duration Max = duration_cast<Duration>(milliseconds(0x7fffffff));
    return ::carb_max(Duration(0), ::carb_min(Max, offset));
}

template <class Clock, class Rep, class Period>
[[nodiscard]] auto absTime(const std::chrono::duration<Rep, Period>& delay,
                           typename Clock::time_point const now = Clock::now()) noexcept
{
    // NOTE: This function may not use any thread-safe statics (OVCC-1549)
    using namespace std::chrono;
    constexpr auto kZero = duration<Rep, Period>::zero();
    decltype(now + delay) absTime = now;
    if (delay > kZero)
    {
#pragma push_macro("max")
#undef max
        constexpr auto kMax = Clock::time_point::max();
#pragma pop_macro("max")

        if (absTime < kMax - delay)
            absTime += delay;
        else
            absTime = kMax;
    }
    return absTime;
}

template <class Clock, class Duration>
auto convertToClock(const std::chrono::time_point<Clock, Duration>& tp, std::true_type)
{
    // NOTE: This function may not use any thread-safe statics (OVCC-1549)

    // Already in terms of desired clock
    return tp;
}

template <class ToClock, class FromClock, class Duration>
auto convertToClock(const std::chrono::time_point<FromClock, Duration>& tp, std::false_type)
{
    // NOTE: This function may not use any thread-safe statics (OVCC-1549)

    // Convert to desired clock
    return absTime<ToClock>(tp - FromClock::now());
}

template <class ToClock, class FromClock, class Duration>
auto convertToClock(const std::chrono::time_point<FromClock, Duration>& tp)
{
    return convertToClock<ToClock>(tp, std::is_same<ToClock, FromClock>{});
}

#if CARB_PLATFORM_WINDOWS
// https://undocumented.ntinternals.net/index.html?page=UserMode%2FUndocumented%20Functions%2FNT%20Objects%2FThread%2FNtDelayExecution.html
using NtDelayExecutionFn = NTSTATUS(__stdcall*)(BOOL, int64_t*);
CARB_WEAKLINK auto NtDelayExecution =
    (NtDelayExecutionFn)GetProcAddress(GetModuleHandleW(L"ntdll.dll"), "NtDelayExecution");
#endif

inline void sleepUs(std::chrono::microseconds usec) noexcept
{
#if CARB_PLATFORM_WINDOWS
    if (NtDelayExecution)
    {
        // NtDelayExecution takes relative 100ns time units as a negative number.
        int64_t delay100ns = -(int64_t(carb_max<int64_t>(0, carb_min(usec.count(), int64_t(INT64_MAX) / 10))) * 10);
        NtDelayExecution(false, &delay100ns);
    }
    else
    {
        // Sleep only has millisecond resolution, so fall back to it only if NtDelayExecution isn't available.
        ::Sleep(DWORD(uint64_t(carb_max<int64_t>(0, carb_min(usec.count() / 1000, int64_t(UINT32_MAX) * 1000)))));
    }
#elif CARB_POSIX
    int64_t nanos = carb_max<int64_t>(0, carb_min(usec.count(), int64_t(INT64_MAX / 1'000))) * 1'000;
    struct timespec rem, req{ time_t(nanos / 1'000'000'000), long(nanos % 1'000'000'000) };
    while (nanosleep(&req, &rem) != 0 && errno == EINTR)
        req = rem; // Complete remaining sleep
#else
    CARB_PLATFORM_UNSUPPORTED();
#endif
}

} // namespace detail
//! \endcond DEV

namespace this_thread
{

/**
 * Blocks the execution of the current thread until *at least* the specified time.
 *
 * This function may block for longer than @p when due to scheduling or resource contention delays.
 * Uses a monotonic clock to measure duration.
 * @warning MSVC versions prior to 2022 17.9 <a
 * href="https://developercommunity.visualstudio.com/t/Modifying-the-system-time-to-the-past-s/10476559">have a bug</a>
 *  where the system clock is used instead of a monotonic clock. This function does not have the issue as long as the
 *  @p when parameter is in terms of a monotonic clock. If a wall-clock time is used, it is converted to a monotonic
 *  clock, but the conversion is subject to system clock adjustments.
 * @param when The time point to wait until.
 */
template <class Clock, class Duration>
void sleep_until(const std::chrono::time_point<Clock, Duration>& when)
{
#if CARB_PLATFORM_WINDOWS && defined(_MSC_VER) && _MSC_VER < 1939
    // OVCC-1610: MSVC prior to 2022 update 17.9 has a bug where sleep_for and sleep_until are not monotonic and are
    // affected by changes to the system clock that result in hangs.
    // https://developercommunity.visualstudio.com/t/Modifying-the-system-time-to-the-past-s/10476559
    auto const steadyClockTarget = cpp::detail::convertToClock<std::chrono::steady_clock>(when);
    for (;;)
    {
        auto const now = std::chrono::steady_clock::now();
        if (steadyClockTarget <= now)
            break;
        cpp::detail::sleepUs(
            std::chrono::duration_cast<std::chrono::microseconds>(cpp::detail::clampDuration(steadyClockTarget - now)));
    }
#else
    std::this_thread::sleep_until(when);
#endif
}

/**
 * Blocks the execution of the current thread for *at least* the specified duration.
 *
 * This function may block for longer than @p delay due to scheduling or resource contention delays.
 * Uses a monotonic clock to measure duration.
 * @warning MSVC versions prior to 2022 17.9 <a
 * href="https://developercommunity.visualstudio.com/t/Modifying-the-system-time-to-the-past-s/10476559">have a bug</a>
 *  where the system clock is used instead of a monotonic clock. This function does not have the issue.
 * @param delay The time duration to sleep for.
 */
template <class Rep, class Period>
void sleep_for(const std::chrono::duration<Rep, Period>& delay)
{
#if CARB_PLATFORM_WINDOWS && defined(_MSC_VER) && _MSC_VER < 1939
    // OVCC-1610: MSVC prior to 2022 update 17.9 has a bug where sleep_for and sleep_until are not monotonic and are
    // affected by changes to the system clock that result in hangs.
    // https://developercommunity.visualstudio.com/t/Modifying-the-system-time-to-the-past-s/10476559
    sleep_until(cpp::detail::absTime<std::chrono::steady_clock>(delay));
#else
    std::this_thread::sleep_for(delay);
#endif
}

} // namespace this_thread

} // namespace cpp
} // namespace carb
