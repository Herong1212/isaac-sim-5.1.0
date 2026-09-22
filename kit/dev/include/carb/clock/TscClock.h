// SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file
//! @brief Implementation of a clock based on the CPU time-stamp counter
#pragma once

#include "../Defines.h"

#include "../cpp/Thread.h"
#include "../math/MulDiv.h"
#include "../Strong.h"

#include <atomic>
#include <thread>

#if CARB_COMPILER_GNUC || CARB_TOOLCHAIN_CLANG || defined(DOXYGEN_BUILD)
//! Macro to creaete a memory barrier in an operation.
#    define CARBLOCAL_COMPILER_BARRIER __asm__ volatile("" ::: "memory")
#elif CARB_COMPILER_MSC
extern "C"
{
    void _ReadWriteBarrier(void);
#    pragma intrinsic(_ReadWriteBarrier)
#    define CARBLOCAL_COMPILER_BARRIER _ReadWriteBarrier()
#    if CARB_X86_64
    unsigned __int64 rdtsc(void);
    unsigned __int64 rdtscp(unsigned int*);
#        pragma intrinsic(__rdtsc)
#        pragma intrinsic(__rdtscp)
#    elif CARB_AARCH64
// Adapted from https://github.com/llvm-mirror/clang/blob/master/test/CodeGen/arm64-microsoft-status-reg.cpp
#        define CARBLOCAL_AARCH64_SYSREG(op0, op1, crn, crm, op2)                                                      \
            (((op0 & 1) << 14) | ((op1 & 7) << 11) | ((crn & 15) << 7) | ((crm & 15) << 3) | ((op2 & 7) << 0))
#        define CARBLOCAL_AARCH64_CNTVCT CARBLOCAL_AARCH64_SYSREG(3, 3, 14, 0, 2) // Generic Timer counter register
    __int64 _ReadStatusReg(int);
#        pragma intrinsic(_ReadStatusReg)
#    else
    CARB_UNSUPPORTED_ARCHITECTURE();
#    endif
}
#else
CARB_UNSUPPORTED_COMPILER(); // For brevity, every compiler ifdef block below does not have this check
#endif

#if CARB_PLATFORM_WINDOWS
#    include "../CarbWindows.h"
#elif CARB_POSIX
#    include <time.h>
#else
CARB_UNSUPPORTED_PLATFORM();
#endif

namespace carb
{
//! Namespace for clock utilities
namespace clock
{

//! \cond DEV
namespace detail
{

// non pipeline-flushing
inline uint64_t readTsc(void) noexcept
{
#if CARB_X86_64
#    if CARB_COMPILER_GNUC || CARB_TOOLCHAIN_CLANG
    return __builtin_ia32_rdtsc();
#    elif CARB_COMPILER_MSC
    return __rdtsc();
#    endif
#elif CARB_AARCH64
#    if CARB_COMPILER_GNUC || CARB_TOOLCHAIN_CLANG
    // From: https://github.com/google/benchmark/blob/master/src/cycleclock.h
    // System timer of ARMv8 runs at a different frequency than the CPU's.
    // The frequency is fixed, typically in the range 1-50MHz. It can be
    // read at CNTFRQ special register. We assume the OS has set up
    // the virtual timer properly.
    uint64_t virtualTimer;
    asm volatile("mrs %0, cntvct_el0" : "=r"(virtualTimer));
    return virtualTimer;
#    elif CARB_COMPILER_MSC
    return _ReadStatusReg(CARBLOCAL_AARCH64_CNTVCT);
#    endif
#else
    CARB_UNSUPPORTED_ARCHITECTURE();
#endif
}

// flushes pipeline
inline uint64_t readTscp(void) noexcept
{
#if CARB_X86_64
#    if CARB_COMPILER_GNUC || CARB_TOOLCHAIN_CLANG
    unsigned int cpu;
    CARBLOCAL_COMPILER_BARRIER;
    auto val = __builtin_ia32_rdtscp(&cpu);
    CARBLOCAL_COMPILER_BARRIER;
    return val;
#    elif CARB_COMPILER_MSC
    unsigned int cpu;
    // Use compiler barriers to ensure that the timer read location is sequentially consisted wrt the surrounding code.
    CARBLOCAL_COMPILER_BARRIER;
    auto val = __rdtscp(&cpu);
    CARBLOCAL_COMPILER_BARRIER;
    return val;
#    endif
#elif CARB_AARCH64
    CARBLOCAL_COMPILER_BARRIER;
    auto val = readTsc();
    CARBLOCAL_COMPILER_BARRIER;
    return val;
#else
    CARB_UNSUPPORTED_ARCHITECTURE();
#endif
}

inline uint64_t readMonotonic(void) noexcept
{
#if CARB_PLATFORM_WINDOWS
    CARBWIN_LARGE_INTEGER li;
    BOOL b = QueryPerformanceCounter((LARGE_INTEGER*)&li);
    CARB_ASSERT(b);
    CARB_UNUSED(b);
    return li.QuadPart;
#elif CARB_POSIX
    struct timespec tp;
    clock_gettime(CLOCK_MONOTONIC, &tp);
    return ((uint64_t)tp.tv_sec * 1'000'000'000) + (uint64_t)tp.tv_nsec; // nanosecond resolution
#else
    CARB_UNSUPPORTED_PLATFORM();
#endif
}

inline uint64_t readMonotonicFreq(void) noexcept
{
#if CARB_PLATFORM_WINDOWS
    CARBWIN_LARGE_INTEGER li;
    BOOL b = QueryPerformanceFrequency((LARGE_INTEGER*)&li);
    CARB_ASSERT(b);
    CARB_UNUSED(b);
    return li.QuadPart;
#elif CARB_POSIX
    return 1'000'000'000; // nanosecond resolution
#else
    CARB_UNSUPPORTED_PLATFORM();
#endif
}

inline void sampleClocks(uint64_t& tsc, uint64_t& monotonic) noexcept
{
    // Attempt to take a TSC stamp and monotonic stamp as closely together as possible. In order to do this, we will
    // interleave several timestamps in the pattern: TSC, mono, TSC, mono, ..., TSC
    // Essentially this measures how long each monotonic timestamp takes in terms of the much faster TSC. We can then
    // take the fastest monotonic timestamp and calculate an equivalent TSC timestamp from the midpoint.

    static constexpr int kIterations = 100;
    uint64_t stamps[kIterations * 2 + 1];
    uint64_t* stamp = stamps;
    uint64_t* const end = stamp + (kIterations * 2);

    // Sleep so that we hopefully start with a full quanta and are less likely to context switch during this function.
    cpp::this_thread::sleep_for(std::chrono::milliseconds(1));

    // Interleave sampling the TSC and monotonic clocks ending on a TSC
    while (stamp != end)
    {
        // Unroll the loop slightly
        *(stamp++) = readTscp();
        *(stamp++) = readMonotonic();
        *(stamp++) = readTscp();
        *(stamp++) = readMonotonic();
        *(stamp++) = readTscp();
        *(stamp++) = readMonotonic();
        *(stamp++) = readTscp();
        *(stamp++) = readMonotonic();
        CARB_ASSERT(stamp <= end);
    }
    *(stamp++) = readTscp();

    // Start with the first as a baseline
    uint64_t best = stamps[2] - stamps[0];
    tsc = stamps[0] + ((stamps[2] - stamps[0]) / 2);
    monotonic = stamps[1];

    // Find the best sample
    for (int i = 0; i != kIterations; ++i)
    {
        uint64_t tscDiff = stamps[2 * (i + 1)] - stamps[2 * i];
        if (tscDiff < best)
        {
            best = tscDiff;
            // Use a tsc sample midway between two samples
            tsc = stamps[2 * i] + (tscDiff / 2);
            monotonic = stamps[2 * i + 1];
        }
    }
}

inline uint64_t computeTscFrequency() noexcept
{
    // We have two clocks in two different domains. The CPU-specific TSC and the monotonic clock. We need to compute the
    // frequency of the TSC since it is not presented in any way.
    uint64_t tsc[2];
    uint64_t monotonic[2];

    // Sample our clocks and wait briefly then sample again
    sampleClocks(tsc[0], monotonic[0]);
    cpp::this_thread::sleep_for(std::chrono::milliseconds(10));
    sampleClocks(tsc[1], monotonic[1]);

    // This shouldn't happen, given the delay
    CARB_ASSERT(monotonic[1] != monotonic[0]);
    return math::mulDiv(math::round_nearest_neighbor, tsc[1] - tsc[0], readMonotonicFreq(), monotonic[1] - monotonic[0])
        .value();
}

} // namespace detail
//! \endcond

//! Static class for a CPU time-stamp clock
//!
//! The functions and types within this class are used for sampling the CPU's time-stamp counter--typically a clock-
//! cycle resolution clock directly within the CPU hardware.
class tsc_clock
{
public:
    //! Type definition of a sample from the CPU time-stamp counter.
    //!
    //! The time units of this are unspecified. Use \ref Freq to determine the frequency of the time-stamp counter.
    CARB_STRONGTYPE(Sample, uint64_t);

    //! The frequency of the timestamp counter, that is, the number of Samples per second.
    CARB_STRONGTYPE(Freq, uint64_t);

    //! Read a sample from the CPU time-stamp clock.
    //!
    //! Note that this operation is intended to be as fast as possible to maintain accuracy.
    //! @returns a time-stamp \ref Sample at the time the function is called.
    static Sample sample() noexcept
    {
        return Sample(detail::readTscp());
    }

    //! Computes the frequency of the CPU time-stamp clock.
    //!
    //! The first call to this function can take longer as the CPU time-stamp clock is calibrated.
    //! @note This implementation assumes that the frequency never changes. Please verify with your CPU architecture
    //! that this assumption is correct.
    //! @returns the computed \ref Freq of the CPU time-stamp clock.
    static Freq frequency() noexcept
    {
        static std::atomic_uint64_t freq{ 0 };
        uint64_t f = freq.load(std::memory_order_relaxed);
        CARB_UNLIKELY_IF(f == 0)
        {
            f = detail::computeTscFrequency();
            freq.store(f, std::memory_order_relaxed);
        }
        return Freq(f);
    }

    //! Computes the difference of two samples as a std::chrono::duration
    //!
    //! @tparam Duration a `std::chrono::duration` template to convert to.
    //! @param older The older (starting) sample
    //! @param newer The newer (ending) sample
    //! @returns The difference in timestamps as the requested `Duration` representation
    template <class Duration>
    static Duration duration(Sample older, Sample newer) noexcept
    {
        using DurationRep = typename Duration::rep;
        using Rep = std::conditional_t<std::is_floating_point<DurationRep>::value, double,
                                       std::conditional_t<std::is_signed<DurationRep>::value, int64_t, uint64_t>>;
        using Period = typename Duration::period;
        int64_t const diff = int64_t(newer.get()) - int64_t(older.get());
        int64_t const freq = int64_t(frequency().get());
        CARB_ASSERT(freq > 0);

        // diff * period::den / (freq * period::num)
        auto duration = math::mulDiv(Rep(diff), Rep(Period::den), Rep(freq * Period::num));
        return Duration(DurationRep(duration.value_or(Rep{})));
    }
};
} // namespace clock
} // namespace carb

#undef CARBLOCAL_AARCH64_SYSREG
#undef CARBLOCAL_AARCH64_CNTVCT
#undef CARBLOCAL_COMPILER_BARRIER
