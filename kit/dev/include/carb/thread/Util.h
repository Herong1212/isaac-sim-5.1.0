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
//! @brief Carbonite thread utilities.
#pragma once

#include "../Defines.h"

#include "Types.h"

#include "../extras/ScopeExit.h"
#include "../math/Util.h"
#include "../process/Util.h"
#include "../profiler/IProfiler.h"

#include "../cpp/Thread.h"

#if CARB_PLATFORM_WINDOWS
#    include "../CarbWindows.h"
#    include "../extras/Unicode.h"
#elif CARB_POSIX
#    include "../../omni/extras/ContainerHelper.h"
#    include <sys/syscall.h>

#    include <pthread.h>
#    include <sched.h>
#    include <unistd.h>
#else
CARB_UNSUPPORTED_PLATFORM();
#endif


#include <atomic>
#include <string>
#include <thread>

namespace carb
{
namespace thread
{

/** The number of CPUs represented by an individual cpu mask. */
constexpr uint64_t kCpusPerMask = std::numeric_limits<CpuMaskVector::value_type>::digits;

#if CARB_PLATFORM_WINDOWS
#    ifndef DOXYGEN_SHOULD_SKIP_THIS
namespace detail
{
const DWORD MS_VC_EXCEPTION = 0x406D1388;
#        pragma pack(push, 8)
typedef struct tagTHREADNAME_INFO
{
    DWORD dwType;
    LPCSTR szName;
    DWORD dwThreadID;
    DWORD dwFlags;
} THREADNAME_INFO;
#        pragma pack(pop)

inline void setDebuggerThreadName(DWORD threadId, LPCSTR name)
{
    // Do it the old way, which is only really useful if the debugger is running
    if (::IsDebuggerPresent())
    {
        detail::THREADNAME_INFO info;
        info.dwType = 0x1000;
        info.szName = name;
        info.dwThreadID = threadId;
        info.dwFlags = 0;
#        pragma warning(push)
#        pragma warning(disable : 6320 6322)
        __try
        {
            ::RaiseException(detail::MS_VC_EXCEPTION, 0, sizeof(info) / sizeof(ULONG_PTR), (ULONG_PTR*)&info);
        }
        __except (CARBWIN_EXCEPTION_EXECUTE_HANDLER)
        {
        }
#        pragma warning(pop)
    }
}

} // namespace detail
#    endif
#endif

/**
 * Sets the name of the given thread.
 *
 * @note The length of the name is limited by the system.
 *
 * @param h The native handle to the thread.
 * @param name The desired name for the thread.
 */
inline void setName(NativeHandleType h, const char* name)
{
#if CARB_PLATFORM_WINDOWS
    // Emulate CARB_NAME_THREAD but don't include Profile.h which would create a circular dependency.
    if (auto profiler = g_carbProfiler.load(std::memory_order_acquire))
        profiler->nameThreadDynamic(::GetThreadId(h), "%s", name);
    // SetThreadDescription is only available starting with Windows 10 1607
    using PSetThreadDescription = HRESULT(CARBWIN_WINAPI*)(HANDLE, PCWSTR);
    static PSetThreadDescription SetThreadDescription =
        (PSetThreadDescription)::GetProcAddress(::GetModuleHandleW(L"kernel32.dll"), "SetThreadDescription");
    if (SetThreadDescription)
    {
        bool b = CARBWIN_SUCCEEDED(SetThreadDescription(h, extras::convertUtf8ToWide(name).c_str()));
        CARB_UNUSED(b);
        CARB_ASSERT(b);
    }
    else
    {
        detail::setDebuggerThreadName(::GetThreadId(h), name);
    }
#elif CARB_PLATFORM_LINUX
    if (h == pthread_self())
    {
        // Emulate CARB_NAME_THREAD but don't include Profile.h which would create a circular dependency.
        if (auto prof = g_carbProfiler.load(std::memory_order_acquire))
            prof->nameThreadDynamic(0, "%s", name);
    }
    if (pthread_setname_np(h, name) != 0)
    {
        // This is limited to 16 characters including NUL according to the man page.
        constexpr static size_t kMaxLen = 15;
        char buffer[kMaxLen + 1 /* 1 for null terminator */];
        strncpy(buffer, name, kMaxLen);
        buffer[kMaxLen] = '\0';
        pthread_setname_np(h, buffer);
    }
#else
    CARB_UNSUPPORTED_PLATFORM();
#endif
}

/**
 * Retrieves the name of the thread previously set with setName().
 *
 * @note The length of the name is limited by the system.
 *
 * @param h The native handle to the thread.
 * @return The name of the thread.
 */
inline std::string getName(NativeHandleType h)
{
#if CARB_PLATFORM_WINDOWS
    // GetThreadDescription is only available starting with Windows 10 1607
    using PGetThreadDescription = HRESULT(CARBWIN_WINAPI*)(HANDLE, PWSTR*);
    static PGetThreadDescription GetThreadDescription =
        (PGetThreadDescription)::GetProcAddress(::GetModuleHandleW(L"kernel32.dll"), "GetThreadDescription");
    if (GetThreadDescription)
    {
        PWSTR threadName;
        if (CARBWIN_SUCCEEDED(GetThreadDescription(h, &threadName)))
        {
            std::string s = extras::convertWideToUtf8(threadName);
            ::LocalFree(threadName);
            return s;
        }
    }
    return std::string();
#elif CARB_PLATFORM_LINUX
    char buffer[64];
    if (pthread_getname_np(h, buffer, CARB_COUNTOF(buffer)) == 0)
    {
        return std::string(buffer);
    }
    return std::string();
#else
    CARB_UNSUPPORTED_PLATFORM();
#endif
}

/**
 * Sets the CPU affinity for the given thread handle
 *
 * Each bit represents a logical CPU; bit 0 for CPU 0, bit 1 for CPU 1, etc.
 *
 * @param h The native handle to the thread
 * @param mask The bitmask representing the desired CPU affinity. Zero (no bits set) is ignored.
 */
inline void setAffinity(NativeHandleType h, size_t mask)
{
#if CARB_PLATFORM_WINDOWS
    ::SetThreadAffinityMask(h, mask);
#elif CARB_PLATFORM_LINUX
    // From the man page: The cpu_set_t data type is implemented as a bit mask. However, the data structure should be
    // treated as opaque: all manipulation of the CPU sets should be done via the macros described in this page.
    if (!mask)
        return;

    cpu_set_t cpuSet;
    CPU_ZERO(&cpuSet);
    static_assert(sizeof(cpuSet) >= sizeof(mask), "Invalid assumption: use CPU_ALLOC");

    do
    {
        int bit = __builtin_ctzll(mask);
        CPU_SET(bit, &cpuSet);
        mask &= ~(size_t(1) << bit);
    } while (mask != 0);

    pthread_setaffinity_np(h, sizeof(cpu_set_t), &cpuSet);
#else
    CARB_UNSUPPORTED_PLATFORM();
#endif
}

/**
 * Sets the CPU Affinity for the thread.
 *
 * On Windows each entry in the CpuMaskVector represents a Processor Group. Each thread can only belong to a single
 * Processor Group, so this function will only set the CPU Affinity to the first non-zero entry in the provided
 * CpuMaskVector. That is to say, if both \c masks[0] and \c masks[1] both have bits sets, only the CPUs in \c masks[0]
 * will be set for the affinity.
 *
 * On Linux, the CpuMaskVector is analogous to a cpu_set_t. There are no restrictions on the number of CPUs that the
 * affinity mask can contain.
 *
 * @param h The thread to set CPU Affinity for.
 * @param masks Affinity masks to set.
 *
 * @return True if the function succeeded, false otherwise. If \c masks is empty, or has no bits set, false will be
 * returned. If the underlying function for setting affinity failed, then \c errno or \c last-error will be set.
 */
inline bool setAffinity(NativeHandleType h, const CpuMaskVector& masks)
{
    if (masks.empty())
    {
        return false;
    }
#if CARB_PLATFORM_WINDOWS
    // Find the lowest mask with a value set. That is the CPU Group that we'll set the affinity for.
    for (uint64_t i = 0; i < masks.size(); ++i)
    {
        if (masks[i])
        {
            CARBWIN_GROUP_AFFINITY affinity{};
            affinity.Group = (WORD)i;
            affinity.Mask = masks[i];

            return ::SetThreadGroupAffinity(h, (const GROUP_AFFINITY*)&affinity, nullptr);
        }
    }

    // Would only reach here if no affinity mask had a cpu set.
    return false;
#elif CARB_PLATFORM_LINUX
    uint64_t numCpus = kCpusPerMask * masks.size();

    cpu_set_t* cpuSet = CPU_ALLOC(numCpus);
    if (!cpuSet)
    {
        return false;
    }

    CARB_SCOPE_EXIT
    {
        CPU_FREE(cpuSet);
    };

    CPU_ZERO_S(CPU_ALLOC_SIZE(numCpus), cpuSet);

    for (uint64_t i = 0; i < masks.size(); ++i)
    {
        CpuMaskVector::value_type mask = masks[i];
        while (mask != 0)
        {
            auto bit = (unsigned long)cpp::countr_zero(mask);
            CPU_SET(bit + (i * kCpusPerMask), cpuSet);
            mask &= ~(CpuMaskVector::value_type(1) << bit);
        }
    }

    if (pthread_setaffinity_np(h, CPU_ALLOC_SIZE(numCpus), cpuSet) != 0)
    {
        return false;
    }
    else
    {
        return true;
    }
#else
    CARB_UNSUPPORTED_PLATFORM();
#endif
}

/**
 * Gets the current CPU Affinity for the thread.
 *
 * On Windows each entry in the CpuMaskVector represents a Processor Group.
 * On Linux, the CpuMaskVector is analogous to a cpu_set_t.
 *
 * @param h The thread to get CPU Affinity for.
 *
 * @return A CpuMaskVector containing the cpu affinities for the thread. If the underlying functions to get thread
 * affinity return an error, the returned CpuMaskVector will be empty and \c errno or \c last-error will be set.
 */
inline CpuMaskVector getAffinity(NativeHandleType h)
{
    CpuMaskVector results;
#if CARB_PLATFORM_WINDOWS
    CARBWIN_GROUP_AFFINITY affinity;
    if (!::GetThreadGroupAffinity(h, (PGROUP_AFFINITY)&affinity))
    {
        return results;
    }

    results.resize(affinity.Group + 1, 0);
    results.back() = affinity.Mask;

    return results;
#elif CARB_PLATFORM_LINUX
    // Get the current affinity
    cpu_set_t cpuSet;
    CPU_ZERO(&cpuSet);
    if (pthread_getaffinity_np(h, sizeof(cpu_set_t), &cpuSet) != 0)
    {
        return results;
    }

    // Convert the cpu_set_t to a CpuMaskVector
    results.reserve(sizeof(cpu_set_t) / sizeof(CpuMaskVector::value_type));
    CpuMaskVector::value_type* ptr = reinterpret_cast<CpuMaskVector::value_type*>(&cpuSet);
    for (uint64_t i = 0; i < (sizeof(cpu_set_t) / sizeof(CpuMaskVector::value_type)); i++)
    {
        results.push_back(ptr[i]);
    }

    return results;
#else
    CARB_UNSUPPORTED_PLATFORM();
#endif
}

/**
 * A utility class for providing a growing number of pause instructions, followed by yielding.
 *
 * The pause instruction is effectively \ref CARB_HARDWARE_PAUSE().
 *
 * Very fast to construct, often used in a loop such as:
 * ```cpp
 * for (AtomicBackoff<> b;; b.pause())
 *     if (condition())
 *         break;
 * ```
 * @tparam PausesBeforeYield the number of pauses that will occur before yielding begins. See
 * \ref AtomicBackoff::pause().
 */
template <size_t PausesBeforeYield = 16>
class AtomicBackoff
{
public:
    //! The number of pauses that should be executed before yielding the thread.
    static constexpr size_t kPausesBeforeYield = PausesBeforeYield;
    static_assert(carb::cpp::has_single_bit(kPausesBeforeYield), "Must be a power of 2");

    //! Constructor.
    constexpr AtomicBackoff() noexcept = default;

    CARB_PREVENT_COPY_AND_MOVE(AtomicBackoff);

    /**
     * A helper function for executing the CPU pause instruction `count` times.
     * @param count The number of times to execute \ref CARB_HARDWARE_PAUSE().
     */
    static void pauseLoop(size_t count) noexcept
    {
        while (count-- > 0)
            CARB_HARDWARE_PAUSE();
    }

    /**
     * Resets `*this`.
     */
    void reset() noexcept
    {
        m_growth = 1;
    }

    /**
     * Every time called, will pause for exponentially longer, and after a certain amount will instead yield.
     *
     * Pause is as via \ref CARB_HARDWARE_PAUSE. Yield is as via `std::this_thread::yield()`.
     * The pause count starts at 1 when \ref reset() or newly constructed. Each time this function is called, the CPU
     * pause instruction is executed `count` times and `count` is doubled. If called when `count` exceeds
     * \ref kPausesBeforeYield, a yield occurs instead. Calling \ref reset() resets the `count` to 1.
     */
    void pause() noexcept
    {
        if (m_growth <= kPausesBeforeYield)
        {
            // Execute pauses
            pauseLoop(m_growth);
            // Pause twice as many times next time
            m_growth *= 2;
        }
        else
        {
            // Too much contention; just yield to the OS
            std::this_thread::yield();
        }
    }

    /**
     * Similar to \ref pause() but if would yield, instead returns false.
     * @returns true if the internal `count` is less than \ref kPausesBeforeYield; `false` otherwise.
     */
    bool pauseWithoutYield() noexcept
    {
        pauseLoop(m_growth);
        if (m_growth >= kPausesBeforeYield)
            return false;
        // Pause twice as many times next time
        m_growth *= 2;
        return true;
    }

private:
    size_t m_growth{ 1 };
};

/**
 *  Similar to `std::thread::hardware_concurrency()`, but pays attention to docker cgroup config
 *  and CPU limits.
 *
 *  Docker allows a container's CPU usage to be limited in two ways - CPU quotas and CPU sets.  A
 *  CPU quota provides a ratio of core usage time versus the scheduling period.  A CPU set
 *  explicitly lists which host CPU cores the container's processes are allowed to run on.  Both
 *  types of limits work together to provide an effective overall CPU usage limit.
 *
 *  When launching a container, Docker will respect the cgroup version that the host system is
 *  using.  Currently cgroups have version 1 and 2, both effectively providing the same info for
 *  CPU usage limits, but specified in different ways.  The cgroups are controlled through a
 *  mounted filesystem directory structure.  There is always a root cgroup defined for the entire
 *  system located at `/sys/fs/cgroup/`.  Other child cgroups an also be defined to further limit
 *  the resources available to specific processes.  The main difference between the two versions
 *  is that the cgroup v1 interface is a hierarchical directory structure whereas v2 uses a
 *  simpler flat directory.  Each version also has different filenames for some of the resource
 *  interface files.
 *
 *  For cgroup v1, the CPU set is defined in the following files:
 *   * `/sys/fs/cgroup/cpuset/cpuset.cpus`
 *   * `/sys/fs/cgroup/cpuset/cpuset.effective_cpus`
 *
 *  For cgroup v2, the CPU set is defined in the following files:
 *   * `/sys/fs/cgroup/cpuset.cpus`
 *   * `/sys/fs/cgroup/cpuset.cpus.effective`
 *
 *  For cgroup v1, the CPU quota is defined in the following files:
 *   * `/sys/fs/cgroup/cpu/cpu.cfs_quota_us` (CPU quota time in microseconds).
 *   * `/sys/fs/cgroup/cpu/cpu.cfs_period_us` (CPU scheduling period time in microseconds).
 *
 *  For cgroup v2, the CPU quota is defined in the following file (both the quota and period time
 *  values are specified in the same file with 'quota' being first and 'period' second.  The
 *  'quota' value may be `max` to indicate that there is no limiting):
 *   * `/sys/fs/cgroup/cpu.max`
 *
 *  When launching a container, docker allows both a CPU quota and a CPU set to be defined.  Both
 *  are valid together or may be used separately to limit total CPU usage inside the container.
 *  The CPU set is defined using the `--cpuset-cpus` command line option and the CPU quota is
 *  defined using the `--cpus` command line option.  Fractional CPU quotas are allowed and will
 *  be rounded up or down as needed here.  A quota of a half or larger will round up to a full CPU
 *  core. It is possible to have an odd number reported by this function when a CPU quota is used.
 *
 *  Examples:
 *   * Docker `--cpus="3.75"` will produce `4` (rounds fractional up)
 *   * Docker `--cpus="3.50"` will produce `4` (rounds fractional up)
 *   * Docker `--cpus="3.25"` will produce `3` (rounds fractional down)
 *   * Docker `--cpus="0.25"` will produce `1` (minimum of 1)
 *   * Docker `--cpuset-cpus="0-1,3"` will produce `3` (cores 0, 1, and 3 are available).
 *   * Docker `--cpuset-cpus="0-3"` will produce `4` (cores 0, 1, 2, and 3 are available).
 *   * Docker `--cpuset-cpus="0,5,7,9,15"` will produce `5` (cores 0, 5, 7, 9, and 15).
 *   * Docker `--cpuset-cpus="1"` will produce `1` (only core 1 is available).
 *   * Docker `--cpuset-cpus="0-3" --cpus="2.75"` will produce `3` (the quota limits here)
 *   * Docker `--cpuset-cpus="0-3" --cpus="4.75"` will produce `4` (the CPU set limits here)
 *
 *  @returns The number of CPUs available on the current system or within the current container,
 *           if applicable.
 */
inline unsigned hardware_concurrency() noexcept
{
#if CARB_PLATFORM_LINUX
    static auto dockerLimit = omni::extras::getDockerCpuLimit();
    if (dockerLimit > 0)
    {
        return unsigned(dockerLimit);
    }
#endif
    return std::thread::hardware_concurrency();
}

} // namespace thread

/**
 * Namespace for utilities that operate on the current thread specifically.
 */
namespace this_thread
{

/**
 * A simple sleep for the current thread that does not include the overhead of `std::chrono`.
 *
 * @note The \ref carb::cpp::this_thread::sleep_for and \ref carb::cpp::this_thread::sleep_until functions make strong
 *  guarantees that they sleep *at least* as long as requested. This function directly calls the underlying kernel sleep
 *  function (`Sleep` or `NtDelayExecution` on Windows and `nanosleep` on POSIX) and only provides the guarantees of the
 *  kernel functions.
 * @param microseconds The number of microseconds to sleep for.
 */
inline void sleepForUs(uint32_t microseconds) noexcept
{
    carb::cpp::detail::sleepUs(std::chrono::microseconds(microseconds));
}

#ifndef DOXYGEN_SHOULD_SKIP_THIS
namespace detail
{

inline unsigned contentionSpins()
{
    // These must be power-of-two-minus-one so that they function as bitmasks
    constexpr static unsigned kSpinsMax = 128 - 1;
    constexpr static unsigned kSpinsMin = 32 - 1;

    // Use randomness to prevent threads from resonating at the same frequency and permanently contending. Use a
    // simple LCG for randomness.
    static std::atomic_uint _seed; // Use random initialization value as the starting seed
    unsigned int next = _seed.load(std::memory_order_relaxed);
    _seed.store(next * 1103515245 + 12345, std::memory_order_relaxed);
    return ((next >> 24) & kSpinsMax) | kSpinsMin;
}

// This function name breaks naming paradigms so that it shows up prominently in stack traces. As the name implies, this
// function waits until f() returns true.
template <class Func>
void __CONTENDED_WAIT__(Func&& f) noexcept(noexcept(f()))
{
    thread::AtomicBackoff<> backoff;
    while (CARB_UNLIKELY(!f()))
        backoff.pause();
}

#    if CARB_PLATFORM_LINUX
using TidReaderFunc = thread::ThreadId (*)(void);

inline thread::ThreadId staticOffsetTidReader()
{
    constexpr static size_t kOffset = 180; // offsetof(struct pthread, tid) / sizeof(uint32_t)

    // Should correspond to struct pthread's tid member. See nptl/descr.h in GLIBC source
    return reinterpret_cast<const uint32_t*>(pthread_self())[kOffset];
}

inline thread::ThreadId syscallTidReader()
{
    return (thread::ThreadId)(pid_t)syscall(SYS_gettid);
}

inline TidReaderFunc determineTidReader() noexcept
{
    // The thread ID is stored internally within the pthread_t, but this is opaque and there is no public API for
    // retrieving it. There is however a syscall for retrieving it, but this takes on average 700 ns per call on an
    // Intel Core i9-7900X running kernel 5.15.0-92. Its offset however hasn't changed in over a decade between glibc
    // versions 2.17 and 2.35, so we can read it with some caution. The memory backing the pthread_t is mmap'd and
    // initialized to zeros, so it is highly improbable that we read a value that happens to be at the same location
    // that randomly matches our thread ID.

    // macOS has pthread_gettid_np(), and efforts to add it to glibc can be tracked here:
    // https://sourceware.org/bugzilla/show_bug.cgi?id=27880

    // Sanity-check the static TID reader, and if it matches, return it.
    if (staticOffsetTidReader() == syscallTidReader())
        return &staticOffsetTidReader;

    // NOTE: We could dynamically try to find the TID within the pthread_t block, but this is problematic especially
    // when running in docker containers where TID is usually a very small number.
    return &syscallTidReader;
}
#    endif

} // namespace detail
#endif

/**
 * Returns the native handle for the current thread.
 *
 * @note Windows: This handle is not unique to the thread but instead is a pseudo-handle representing "current thread".
 * To obtain a unique handle to the current thread, use the Windows API function `DuplicateHandle()`.
 *
 * @return The native handle for the current thread.
 */
inline thread::NativeHandleType get()
{
#if CARB_PLATFORM_WINDOWS
    return ::GetCurrentThread();
#elif CARB_POSIX
    return pthread_self();
#else
    CARB_UNSUPPORTED_PLATFORM();
#endif
}


/**
 * Returns the ID of the currently executing process.
 * @returns The current ID of the process.
 */
CARB_DEPRECATED("Use this_process::getId() instead") static inline thread::ProcessId getProcessId()
{
    return this_process::getId();
}

/**
 * Get the ID of the currently executing process.
 * @note Linux: This value is cached, so this can be unsafe if you are using fork() or clone() without calling exec()
 * after. This should be safe if you're only using @ref carb::launcher::ILauncher to launch processes.
 * @returns The current ID of the process.
 */
CARB_DEPRECATED("Use this_process::getIdCached() instead") static inline thread::ProcessId getProcessIdCached()
{
    return this_process::getIdCached();
}

/**
 * Retrieve the thread ID for the current thread.
 *
 * @note (Linux) This function returns the *thread ID* which is different than `pthread_self()`. This thread ID can be
 *   found with `syscall(SYS_gettid)`, but this can be very slow as it is a syscall. To be more performant, Carbonite
 *   attempts to read the value from within the opaque `pthread_t`, but there is no guarantee that GLIBC will keep this
 *   value in the same location permanently. If the value cannot be read from `pthread_t`, it will fall back to using
 *   the slower syscall. This value is not stored in a `thread_local` because older versions of GLIBC (such as 2.17
 *   which is used by Centos7) require a lock that is also required for loading shared libraries, which can cause a
 *   deadlock.
 * @return The thread ID for the current thread.
 */
inline thread::ThreadId getId()
{
#if CARB_PLATFORM_WINDOWS
    return thread::ThreadId(::GetCurrentThreadId());
#elif CARB_PLATFORM_LINUX
    // Determine the best way to read the thread ID and use that.
    // NOTE: We do not store this in a thread_local because on older versions of glibc (especially 2.17, which is what
    // Centos7 uses), this will require a lock that is also shared with loading shared libraries, which can cause a
    // deadlock.
    static detail::TidReaderFunc reader = detail::determineTidReader();
    return reader();
#else
    CARB_UNSUPPORTED_PLATFORM();
#endif
}

/**
 * Sets the name for the current thread.
 *
 * @note The length of the name is limited by the system and may be truncated.
 *
 * @param name The desired name for the current thread.
 */
inline void setName(const char* name)
{
    thread::setName(get(), name);
}

/**
 * Retrieves the name of the current thread.
 *
 * @return The name of the current thread.
 */
inline std::string getName()
{
    return thread::getName(get());
}

/**
 * Sets the affinity of the current thread.
 *
 * Each bit represents a logical CPU; bit 0 for CPU 0, bit 1 for CPU 1, etc.
 *
 * @note This function is limited to the first 64 CPUs in a system.
 *
 * @param mask The bitmask representing the desired CPU affinity. Zero (no bits set) is ignored.
 */
inline void setAffinity(size_t mask)
{
    thread::setAffinity(get(), mask);
}

/**
 * Sets the CPU Affinity for the current thread.
 *
 * On Windows each entry in the CpuMaskVector represents a Processor Group. Each thread can only belong to a single
 * Processor Group, so this function will only set the CPU Affinity to the first non-zero entry in the provided
 * CpuMaskVector. That is to say, if both \c masks[0] and \c masks[1] have bits sets, only the CPUs in \c masks[0]
 * will be set for the affinity.
 *
 * On Linux, the CpuMaskVector is analogous to a cpu_set_t. There are no restrictions on the number of CPUs that the
 * affinity mask can contain.
 *
 * @param masks Affinity masks to set.
 *
 * @return True if the function succeeded, false otherwise. If \c masks is empty, or has no bits set, false will be
 * returned. If the underlying function for setting affinity failed, then \c errno or \c last-error will be set.
 */
inline bool setAffinity(const thread::CpuMaskVector& masks)
{
    return thread::setAffinity(get(), masks);
}

/**
 * Gets the current CPU Affinity for the current thread.
 *
 * On Windows each entry in the CpuMaskVector represents a Processor Group.
 * On Linux, the CpuMaskVector is analogous to a cpu_set_t.
 *
 * @return A CpuMaskVector containing the cpu affinities for the thread. If the underlying functions to get thread
 * affinity return an error, the returned CpuMaskVector will be empty and \c errno or \c last-error will be set.
 */
inline thread::CpuMaskVector getAffinity()
{
    return thread::getAffinity(get());
}

/**
 * Calls a predicate repeatedly until it returns \c true.
 *
 * This function is recommended only for situations where exactly one thread is waiting on another thread. For multiple
 * threads waiting on a predicate, use \ref spinWaitWithBackoff().
 *
 * @note This function **does not return** until @p f has returned `true` for the calling thread. For a version of this
 *   function that will give up, use \ref spinTryWait().
 *
 * @note This function **does not** enter the kernel to wait.
 *
 * @param f The predicate to call repeatedly until it returns `true`.
 */
template <class Func>
void spinWait(Func&& f) noexcept(noexcept(f()))
{
    while (!CARB_LIKELY(f()))
    {
        CARB_HARDWARE_PAUSE();
    }
}

/**
 * Calls a predicate until it returns true with progressively increasing delays between calls.
 *
 * This function is a low-level utility for high-contention cases where multiple threads will be calling @p f
 * simultaneously, @p f needs to succeed (return `true`) before continuing, but @p f will only succeed for one thread at
 * a time. This function does not return until @p f returns `true`, at which point this function returns immediately.
 * High contention is assumed when @p f returns `false` for several calls, at which point the calling thread will invoke
 * `std::this_thread::yield()` between calls to @p f. This is a back-off mechanism to allow one thread to move forward
 * while other competing threads wait their turn.
 *
 * @note This function **does not return** until @p f has returned `true` for the calling thread. For a version of this
 *   function that will give up, use \ref spinTryWaitWithBackoff().
 *
 * @note This function **may** enter the kernel to wait.
 *
 * @param f The predicate to call repeatedly until it returns `true`.
 */
template <class Func>
void spinWaitWithBackoff(Func&& f) noexcept(noexcept(f()))
{
    if (CARB_UNLIKELY(!f()))
    {
        detail::__CONTENDED_WAIT__(std::forward<Func>(f));
    }
}

/**
 * Calls a predicate until it returns true or a number of attempts have elapsed.
 *
 * This function is recommended only for situations where exactly one thread is waiting on another thread. For multiple
 * threads waiting on a predicate, use \ref spinTryWaitWithBackoff().
 *
 * This function will call @p f interspersed with increasing invocations of \ref CARB_HARDWARE_PAUSE. After a certain
 * number of attempts, the function gives up and returns `false`. If @p f returns `true`, spinTryWait() immediately
 * returns `true`.
 *
 * @note This function **does not** enter the kernel to wait.
 *
 * @param f The predicate to call repeatedly until it returns `true`.
 * @returns `true` immediately when @p f returns `true`. If a number of attempts to call @p f all return `false` then
 * the function gives up and `false` is returned.
 */
template <class Func>
bool spinTryWait(Func&& f) noexcept(noexcept(f()))
{
    thread::AtomicBackoff<> backoff;
    while (CARB_UNLIKELY(!f()))
        if (!backoff.pauseWithoutYield()) // not really much of a backoff
            return false;
    return true;
}

/**
 * Calls a predicate until it returns true or a number of attempts have elapsed, backing off as time passes.
 *
 * This function is a low-level utility for high-contention cases where multiple threads will be calling @p f
 * simultaneously, and @p f needs to succeed (return `true`) before continuing, but @p f will only succeed for one
 * thread at a time. This function will call @p f interspersed with increasing invocations of \ref CARB_HARDWARE_PAUSE.
 * However, unlike \ref spinTryWait(), this function will then proceed to `std::this_thread::yield()` calls which will
 * typically enter the kernel to wait. After a certain number of attempts, the function gives up and returns `false`.
 * If @p f returns `true`, spinTryWait() immediately returns `true`.
 *
 * @note This function **may** enter the kernel to wait.
 *
 * @param f The predicate to call repeatedly until it returns `true`.
 * @returns `true` immediately when @p f returns `true`. If a number of attempts to call @p f all return `false` then
 * the function gives up and `false` is returned.
 */
template <class Func>
bool spinTryWaitWithBackoff(Func&& f) noexcept(noexcept(f()))
{
    if (CARB_LIKELY(f()))
        return true;

    size_t count = 1;
    for (; count < 32; count *= 2)
    {
        // Do a bunch of pause instructions
        thread::AtomicBackoff<>::pauseLoop(count);
        if (CARB_LIKELY(f()))
            return true;
    }
    for (; count < 64; ++count)
    {
        // Do some yielding
        std::this_thread::yield();
        if (CARB_LIKELY(f()))
            return true;
    }
    return false;
}

/**
 * A replacement function for `std::atomic_thread_fence(std::memory_order_seq_cst)` that performs better on some older
 * compilers.
 */
inline void atomic_fence_seq_cst() noexcept
{
#if CARB_X86_64 && CARB_COMPILER_GNUC && __GNUC__ < 11 && !CARB_TSAN_ENABLED
    // On x86_64 CPUs we can use any lock-prefixed instruction as a StoreLoad operation to achieve sequential
    // consistency (see https://shipilev.net/blog/2014/on-the-fence-with-dependencies/). The 'notb' instruction here has
    // the added benefit of not affecting flags or other registers (see https://www.felixcloutier.com/x86/not).
    // It is also likely that our 'unused' variable at the top of the stack is in L1 cache.
    unsigned char unused{};
    __asm__ __volatile__("lock; notb %0" : "+m"(unused)::"memory");
#else
    std::atomic_thread_fence(std::memory_order_seq_cst);
#endif
}

//! @copydoc carb::cpp::this_thread::sleep_for
template <class Rep, class Period>
void sleep_for(const std::chrono::duration<Rep, Period>& delay)
{
    cpp::this_thread::sleep_for(delay);
}

//! @copydoc carb::cpp::this_thread::sleep_until
template <class Clock, class Duration>
void sleep_until(const std::chrono::time_point<Clock, Duration>& when)
{
    cpp::this_thread::sleep_until(when);
}

} // namespace this_thread
} // namespace carb
