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
//! @brief Futex implementation details.
#pragma once

#include "../../Defines.h"
#include "../../thread/Util.h"

#include <atomic>

#if CARB_PLATFORM_WINDOWS
#    pragma comment(lib, "synchronization.lib") // must link with synchronization.lib
#    include "../../CarbWindows.h"
#elif CARB_PLATFORM_LINUX
#    include <linux/futex.h>
#    include <sys/syscall.h>
#    include <sys/time.h>

#    include <unistd.h>
#else
CARB_UNSUPPORTED_PLATFORM();
#endif

//! \cond DEV
namespace carb
{
namespace thread
{
namespace detail
{

template <class T, size_t S = sizeof(T)>
struct to_integral
{
};

template <class T>
struct to_integral<T, 1>
{
    using type = int8_t;
};

template <class T>
struct to_integral<T, 2>
{
    using type = int16_t;
};

template <class T>
struct to_integral<T, 4>
{
    using type = int32_t;
};

template <class T>
struct to_integral<T, 8>
{
    using type = int64_t;
};

template <class T>
using to_integral_t = typename to_integral<T>::type;

template <class As, class T>
[[nodiscard]] std::enable_if_t<std::is_integral<T>::value && sizeof(As) == sizeof(T), As> reinterpret_as(const T& in) noexcept
{
    static_assert(std::is_integral<As>::value, "Must be integral type");
    return static_cast<As>(in);
}

template <class As, class T>
[[nodiscard]] std::enable_if_t<std::is_pointer<T>::value && sizeof(As) == sizeof(T), As> reinterpret_as(const T& in) noexcept
{
    static_assert(std::is_integral<As>::value, "Must be integral type");
    return reinterpret_cast<As>(in);
}

template <class As, class T>
[[nodiscard]] std::enable_if_t<(!std::is_pointer<T>::value && !std::is_integral<T>::value) || sizeof(As) != sizeof(T), As> reinterpret_as(
    const T& in) noexcept
{
    static_assert(std::is_integral<As>::value, "Must be integral type");
    As out{}; // Init to zero
    memcpy(&out, std::addressof(in), sizeof(in));
    return out;
}

template <class T>
bool futex_compare(const std::atomic<T>& val, T compare, std::memory_order order = std::memory_order_seq_cst) noexcept
{
    using I = to_integral_t<T>;
    return reinterpret_as<I>(val.load(order)) == reinterpret_as<I>(compare);
}

#if CARB_PLATFORM_WINDOWS
using hundrednanos = std::chrono::duration<int64_t, std::ratio<1, 10'000'000>>;

using RtlWaitOnAddressFn = NTSTATUS(__stdcall*)(volatile const void*, const void*, size_t, int64_t*);
CARB_WEAKLINK auto RtlWaitOnAddress =
    (RtlWaitOnAddressFn)GetProcAddress(GetModuleHandleW(L"ntdll.dll"), "RtlWaitOnAddress");

inline bool WaitOnAddress(volatile const void* val, const void* compare, size_t size, int64_t* timeout) noexcept
{
    // Use the NTDLL version of this function since we can give it relative or absolute times in 100ns units
    switch (NTSTATUS ret = RtlWaitOnAddress(val, compare, size, timeout))
    {
        case CARBWIN_STATUS_SUCCESS:
            return true;

        default:
            CARB_FATAL_UNLESS(
                0, "Unexpected result from RtlWaitOnAddress: 0x%lx, GetLastError=%" PRIdword, ret, ::GetLastError());
            [[fallthrough]]; // (not really, but the compiler doesn't know that CARB_FATAL_UNLESS doesn't return)
        case CARBWIN_STATUS_TIMEOUT:
            return false;
    }
}

template <class T>
inline bool WaitOnAddress(const std::atomic<T>& val, T compare, int64_t* timeout) noexcept
{
    static_assert(sizeof(val) == sizeof(compare), "Invalid assumption about atomic");
    return WaitOnAddress(std::addressof(val), std::addressof(compare), sizeof(T), timeout);
}

// Use undocumented API unlikely to change since so many things are based on it.
// https://ntdoc.m417z.com/ntwaitforalertbythreadid
// https://dennisbabkin.com/blog/?t=how-to-put-thread-into-kernel-wait-and-to-wake-it-by-thread-id
using NtWaitForAlertByThreadIdFn = NTSTATUS(__stdcall*)(const void*, int64_t*);
CARB_WEAKLINK auto NtWaitForAlertByThreadId =
    (NtWaitForAlertByThreadIdFn)GetProcAddress(GetModuleHandleW(L"ntdll.dll"), "NtWaitForAlertByThreadId");
using NtAlertThreadByThreadIdFn = NTSTATUS(__stdcall*)(HANDLE); // HANDLE?
CARB_WEAKLINK auto NtAlertThreadByThreadId =
    (NtAlertThreadByThreadIdFn)GetProcAddress(GetModuleHandleW(L"ntdll.dll"), "NtAlertThreadByThreadId");

inline bool WaitForAlertByThreadId(const void* addr, int64_t* timeout) noexcept
{
    // OVCC-1549: Do not use thread-safe static initialization for looking up NtWaitForAlertByThreadId! See Jira/MR for
    // more info.
    switch (NTSTATUS ret = NtWaitForAlertByThreadId(addr, timeout))
    {
        case CARBWIN_STATUS_SUCCESS: // not received in practice
        case CARBWIN_STATUS_ALERTED:
            return true;

        default:
            CARB_FATAL_UNLESS(0, "Unexpected result from NtWaitForAlertByThreadId: 0x%lx, GetLastError=%" PRIdword, ret,
                              ::GetLastError());
            [[fallthrough]]; // (not really, but the compiler doesn't know that CARB_FATAL_UNLESS doesn't return)
        case CARBWIN_STATUS_TIMEOUT:
            return false;
    }
}

inline void AlertThreadByThreadId(ThreadId threadId) noexcept
{
    // OVCC-1549: Do not use thread-safe static initialization for looking up NtAlertThreadByThreadId! See Jira/MR for
    // more info.
    NTSTATUS ret = NtAlertThreadByThreadId((HANDLE)(UINT_PTR)threadId);
    // Win32 APIs typically ignore this return value
    CARB_ASSERT(ret == CARBWIN_STATUS_SUCCESS, "NtAlertThreadByThreadId gave unexpected result: %lx", ret);
    CARB_UNUSED(ret);
}

template <class T>
inline void threadId_wait(const std::atomic<T>& val) noexcept
{
    WaitForAlertByThreadId(std::addressof(val), nullptr);
}

template <class T, class Clock, class Duration>
inline bool threadId_wait_until(const std::atomic<T>& val, std::chrono::time_point<Clock, Duration> time_point)
{
    // We want to use monotonic clocks instead of the system clock which is subject to time correction and can jump
    // backwards or forwards. Positive absolute time for WaitForAlertByThreadId is based on the system clock, so always
    // use the relative version.
    auto const steadyClockTarget = cpp::detail::convertToClock<std::chrono::steady_clock>(time_point);

    // Compute updated relative timeout and wait
    auto now = std::chrono::steady_clock::now();
    do
    {
        // Compute relative time (passed as a negative number to WaitForAlertByThreadId). WaitForAlertByThreadId must be
        // called at least once.
        int64_t relTime =
            -std::chrono::duration_cast<detail::hundrednanos>(cpp::detail::clampDuration(steadyClockTarget - now)).count();
        if (WaitForAlertByThreadId(std::addressof(val), &relTime))
            return true;
        now = std::chrono::steady_clock::now();
    } while (now <= steadyClockTarget);

    return false;
}

template <class T, class Rep, class Period>
inline bool threadId_wait_for(const std::atomic<T>& val, std::chrono::duration<Rep, Period> duration)
{
    // WaitForAlertByThreadId with relative time is not accurate and will often wait less than the requested time.
    // Compute an absolute timeout value based on a monotonic clock.
    return threadId_wait_until(val, cpp::detail::absTime<std::chrono::steady_clock>(duration));
}

inline void threadId_wake(ThreadId id) noexcept
{
    AlertThreadByThreadId(id);
}

template <class T>
inline void futex_wait(const std::atomic<T>& val, T compare) noexcept
{
    WaitOnAddress(val, compare, nullptr);
}

template <class T, class Clock, class Duration>
inline bool futex_wait_until(const std::atomic<T>& val, T compare, std::chrono::time_point<Clock, Duration> time_point)
{
    // We want to use monotonic clocks instead of the system clock which is subject to time correction and can jump
    // backwards or forwards. Positive absolute time for WaitForAlertByThreadId is based on the system clock, so always
    // use the relative version.
    auto const steadyClockTarget = cpp::detail::convertToClock<std::chrono::steady_clock>(time_point);
    for (;;)
    {
        const auto now = std::chrono::steady_clock::now();
        if (steadyClockTarget <= now)
        {
            // Timeout expired, do immediate check and return. WaitOnAddress is quite slow if the timeout is zero.
            return !futex_compare(val, compare);
        }

        int64_t relTime =
            -std::chrono::duration_cast<detail::hundrednanos>(cpp::detail::clampDuration(steadyClockTarget - now)).count();
        CARB_ASSERT(relTime < 0);
        if (detail::WaitOnAddress(val, compare, &relTime))
            return true;
    }
}

template <class T, class Rep, class Period>
inline bool futex_wait_for(const std::atomic<T>& val, T compare, std::chrono::duration<Rep, Period> duration)
{
    return duration.count() > 0 ?
               futex_wait_until(val, compare, cpp::detail::absTime<std::chrono::steady_clock>(duration)) :
               !futex_compare(val, compare);
}

template <class T>
inline void futex_wake_one(std::atomic<T>& val) noexcept
{
    WakeByAddressSingle(std::addressof(val));
}

template <class T>
inline void futex_wake_n(std::atomic<T>& val, size_t n) noexcept
{
    while (n--)
        futex_wake_one(val);
}

template <class T>
inline void futex_wake_all(std::atomic<T>& val) noexcept
{
    WakeByAddressAll(std::addressof(val));
}

// Windows-specific futex
template <class T, size_t S = sizeof(T)>
class WindowsFutex
{
    static_assert(S == 1 || S == 2 || S == 4 || S == 8, "Unsupported size");

public:
    using AtomicType = typename std::atomic<T>;
    using Type = T;
    static inline void wait(const AtomicType& val, Type compare) noexcept
    {
        futex_wait(val, compare);
    }
    template <class Rep, class Period>
    static inline bool wait_for(const AtomicType& val, Type compare, std::chrono::duration<Rep, Period> duration)
    {
        return futex_wait_for(val, compare, duration);
    }
    template <class Clock, class Duration>
    static inline bool wait_until(const AtomicType& val, Type compare, std::chrono::time_point<Clock, Duration> time_point)
    {
        return futex_wait_until(val, compare, time_point);
    }
    static inline void notify_one(AtomicType& a) noexcept
    {
        futex_wake_one(a);
    }
    static inline void notify_n(AtomicType& a, size_t n) noexcept
    {
        futex_wake_n(a, n);
    }
    static inline void notify_all(AtomicType& a) noexcept
    {
        futex_wake_all(a);
    }
};
#elif CARB_PLATFORM_LINUX
constexpr int64_t kNsPerSec = 1'000'000'000;

inline int futex(const std::atomic_uint32_t& aval,
                 int futex_op,
                 uint32_t val,
                 const struct timespec* timeout,
                 uint32_t* uaddr2,
                 unsigned int val3) noexcept
{
    static_assert(sizeof(aval) == sizeof(uint32_t), "Invalid assumption about atomic");
    auto ret = syscall(SYS_futex, std::addressof(aval), futex_op, val, timeout, uaddr2, val3);
    return ret >= 0 ? int(ret) : -errno;
}

inline void futex_wait(const std::atomic_uint32_t& val, uint32_t compare) noexcept
{
    for (;;)
    {
        int ret = futex(val, FUTEX_WAIT_BITSET_PRIVATE, compare, nullptr, nullptr, FUTEX_BITSET_MATCH_ANY);
        switch (ret)
        {
            case 0:
            case -EAGAIN: // Valid or spurious wakeup
                return;

            case -ETIMEDOUT:
                // Apparently on Windows Subsystem for Linux, calls to the kernel can timeout even when a timeout value
                // was not specified. Fall through.
            case -EINTR: // Interrupted by signal; loop again
                break;

            default:
                CARB_FATAL_UNLESS(0, "Unexpected result from futex(): %d/%s", -ret, strerror(-ret));
        }
    }
}

template <class Rep, class Period>
inline bool futex_wait_for(const std::atomic_uint32_t& val, uint32_t compare, std::chrono::duration<Rep, Period> duration)
{
    // Relative time
    int64_t ns = std::chrono::duration_cast<std::chrono::nanoseconds>(cpp::detail::clampDuration(duration)).count();
    if (ns <= 0)
    {
        return false;
    }

    struct timespec ts;
    ts.tv_sec = time_t(ns / detail::kNsPerSec);
    ts.tv_nsec = long(ns % detail::kNsPerSec);

    // Since we're using relative time here, we can use FUTEX_WAIT_PRIVATE (see futex() man page)
    int ret = futex(val, FUTEX_WAIT_PRIVATE, compare, &ts, nullptr, 0);
    switch (ret)
    {
        case 0: // Valid wakeup
        case -EAGAIN: // Valid or spurious wakeup
        case -EINTR: // Interrupted by signal; treat as a spurious wakeup
            return true;

        default:
            CARB_FATAL_UNLESS(0, "Unexpected result from futex(): %d/%s", -ret, strerror(-ret));
            [[fallthrough]]; // (not really but the compiler doesn't know that the above won't return)
        case -ETIMEDOUT:
            return false;
    }
}

template <class Clock, class Duration>
inline bool futex_wait_until(const std::atomic_uint32_t& val,
                             uint32_t compare,
                             const std::chrono::time_point<Clock, Duration>& time_point)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);

    auto const duration = time_point - Clock::now();

    // Get the number of nanoseconds to go (constrained)
    int64_t ns = std::chrono::duration_cast<std::chrono::nanoseconds>(cpp::detail::clampDuration(duration)).count();

    if (ns <= 0)
    {
        return false;
    }

    ts.tv_sec += time_t(ns / kNsPerSec);
    ts.tv_nsec += long(ns % kNsPerSec);

    // Handle rollover
    if (ts.tv_nsec >= kNsPerSec)
    {
        ++ts.tv_sec;
        ts.tv_nsec -= kNsPerSec;
    }

    for (;;)
    {
        // Since we're using absolute monotonic time, we use FUTEX_WAIT_BITSET_PRIVATE. See the man page for futex for
        // more info.
        int ret = futex(val, FUTEX_WAIT_BITSET_PRIVATE, compare, &ts, nullptr, FUTEX_BITSET_MATCH_ANY);
        switch (ret)
        {
            case 0: // Valid wakeup
            case -EAGAIN: // Valid or spurious wakeup
                return true;

            case -EINTR: // Interrupted by signal; loop again
                break;

            default:
                CARB_FATAL_UNLESS(0, "Unexpected result from futex(): %d/%s", -ret, strerror(-ret));
                [[fallthrough]]; // (not really but the compiler doesn't know that the above won't return)
            case -ETIMEDOUT:
                return false;
        }
    }
}

inline void futex_wake_n(std::atomic_uint32_t& val, unsigned count) noexcept
{
    int ret = futex(val, FUTEX_WAKE_BITSET_PRIVATE, count, nullptr, nullptr, FUTEX_BITSET_MATCH_ANY);
    CARB_ASSERT(ret >= 0, "futex(FUTEX_WAKE) failed with errno=%d/%s", -ret, strerror(-ret));
    CARB_UNUSED(ret);
}

inline void futex_wake_one(std::atomic_uint32_t& val) noexcept
{
    futex_wake_n(val, 1);
}

inline void futex_wake_all(std::atomic_uint32_t& val) noexcept
{
    futex_wake_n(val, INT_MAX);
}
#endif

class NativeFutex
{
public:
    using AtomicType = std::atomic_uint32_t;
    using Type = uint32_t;
    static inline void wait(const AtomicType& val, Type compare) noexcept
    {
        futex_wait(val, compare);
    }
    template <class Rep, class Period>
    static inline bool wait_for(const AtomicType& val, Type compare, std::chrono::duration<Rep, Period> duration)
    {
        return futex_wait_for(val, compare, duration);
    }
    template <class Clock, class Duration>
    static inline bool wait_until(const AtomicType& val, Type compare, std::chrono::time_point<Clock, Duration> time_point)
    {
        return futex_wait_until(val, compare, time_point);
    }
    static inline void notify_one(AtomicType& a) noexcept
    {
        futex_wake_one(a);
    }
    static inline void notify_n(AtomicType& a, size_t n) noexcept
    {
        futex_wake_n(a, unsigned(carb_min<size_t>(UINT_MAX, n)));
    }
    static inline void notify_all(AtomicType& a) noexcept
    {
        futex_wake_all(a);
    }
};

} // namespace detail
} // namespace thread
} // namespace carb
//! \endcond
