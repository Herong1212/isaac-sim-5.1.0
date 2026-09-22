// SPDX-FileCopyrightText: Copyright (c) 2019-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
/** @file
 *  @brief Provides some helper functions that check the state of debuggers for the calling
 *         process.
 */
#pragma once

#include "../detail/PushBadMacros.h"

#include "../Defines.h"

#if CARB_PLATFORM_WINDOWS
#    include "../CarbWindows.h"
extern "C"
{
    // Forge doesn't define these functions, and it can be included before CarbWindows.h in some cases
    // So ensure that they're defined here.
    __declspec(dllimport) BOOL __stdcall IsDebuggerPresent(void);
    __declspec(dllimport) void __stdcall DebugBreak(void);

    // Undocumented function from ntdll.dll, only present in ntifs.h from the Driver Development Kit
    __declspec(dllimport) unsigned short __stdcall RtlCaptureStackBackTrace(unsigned long,
                                                                            unsigned long,
                                                                            void**,
                                                                            unsigned long*);
}
#elif CARB_POSIX
#    include <chrono>
#    include <cctype>
#    include <execinfo.h>
#    include <signal.h>
#    include <stdint.h>
#    include <string.h>
#    include <fcntl.h>
#    include <sys/types.h>
#    include <unistd.h>
#else
CARB_UNSUPPORTED_PLATFORM();
#endif

#include <cstdio>

/** Namespace for all low level Carbonite functionality. */
namespace carb
{
/** Common namespace for extra helper functions and classes. */
namespace extras
{

#ifndef DOXYGEN_SHOULD_SKIP_THIS
#endif

/**
 *  Checks if a debugger is attached to the calling process.
 *
 *  @returns `true` if a user-mode debugger is currently attached to the calling process.
 *  @returns `false` if the calling process does not have a debugger attached.
 *
 *  @remarks This checks if a debugger is currently attached to the calling process.  This will
 *           query the current state of the debugger so that a process can disable some debug-
 *           only checks at runtime if the debugger is ever detached.  If a debugger is attached
 *           to a running process, this will start returning `true` again.
 *
 *  @note    On Linux and related platforms, the debugger check is a relatively expensive
 *           operation.  To avoid unnecessary overhead explicitly checking this state each time,
 *           the last successfully queried state will be cached for a short period.  Future calls
 *           within this period will simply return the cached state instead of querying again.
 */
inline bool isDebuggerAttached(void)
{
#if CARB_PLATFORM_WINDOWS
    return IsDebuggerPresent();
#elif CARB_PLATFORM_LINUX
    // the maximum amount of time in milliseconds that the cached debugger state is valid for.
    // If multiple calls to isDebuggerAttached() are made within this period, a cached state
    // will be returned instead of re-querying.  Outside of this period however, a new call
    // to check the debugger state with isDebuggerAttached() will cause the state to be
    // refreshed.
    using namespace std::chrono;
    static constexpr auto kDebugUtilsDebuggerCheckPeriod = milliseconds(500);
    static bool queried = false;
    static bool state = false;
    auto now = steady_clock::now();
    static auto lastCheckTime = now;
    auto elapsedTime = now - lastCheckTime;


    if (!queried || elapsedTime > kDebugUtilsDebuggerCheckPeriod)
    {
        // on Android and Linux we can check the '/proc/self/status' file for the line
        // "TracerPid:" to check if the associated value is *not* 0.  Note that this is
        // not a cheap check so we'll cache its result and only re-query once every few
        // seconds.

        // fopen() and fgets() can use the heap, and we may be called from the crashreporter, so avoid using those
        // functions to avoid heap usage.
        int fd = open("/proc/self/status", O_RDONLY);
        if (fd < 0)
            return false;

        lastCheckTime = now;
        queried = true;
        char data[256];
        constexpr static char TracerPid[] = "TracerPid:";
        for (;;)
        {
            // Read some bytes from the file
            ssize_t bytes = CARB_RETRY_EINTR(read(fd, data, CARB_COUNTOF(data) - 1));
            if (bytes <= 0)
            {
                // Reached the end without finding the line, shouldn't happen
                CARB_ASSERT(0);
                close(fd);
                state = false;
                break;
            }
            data[bytes] = '\0';

            // Look for the 'T' in "TracerPid"
            auto p = strchr(data, 'T');
            if (!p)
                continue;

            // Can we see the whole line?
            auto cr = strchr(p, '\n');
            if (!cr)
            {
                if (p == data)
                    // This line is too long; skip the 'T' and try again
                    lseek(fd, -off_t(bytes - 1), SEEK_CUR);
                else
                    // Cannot see the whole line. Back up to where we found the 'T'
                    lseek(fd, -off_t(data + bytes - p), SEEK_CUR);
                continue;
            }

            // Back up to the next line for the next read
            lseek(fd, -off_t(data + bytes - (cr + 1)), SEEK_CUR);

            // TracerPid line?
            if (strncmp(p, TracerPid, CARB_COUNTOF(TracerPid) - 1) != 0)
                // Nope, on to the next line
                continue;

            // Yep, get the result.
            p += (CARB_COUNTOF(TracerPid) - 1);
            while (p != cr && (*p == '0' || isspace(*p)))
                ++p;

            // If we find any characters other than space or zero, we have a tracer
            state = p != cr;
            close(fd);
            break;
        }
    }

    return state;
#else
    CARB_UNSUPPORTED_PLATFORM();
#endif
}

/**
 *  Performs a software breakpoint if a debugger is currently attached to this process.
 *
 *  @returns No return value.
 *
 *  @remarks This performs a software breakpoint.  If a debugger is attached, this will cause the
 *           breakpoint to be caught and the debugger will take over the process' state.  If no
 *           debugger is attached, this will be ignored.  This can be thought of as a more dynamic
 *           version of CARB_ASSERT(0) where the existence of a debugger is explicitly checked
 *           at runtime instead of at compile time.
 *
 *  @note    This should really only be used for local debugging purposes.  The debugger check
 *           that is used in here (isDebuggerAttached()) could potentially be expensive on some
 *           platforms, so this should only be called when it is well known that a problem that
 *           needs immediate debugging attention has already occurred.
 */
inline void debuggerBreak(void)
{
    if (!isDebuggerAttached())
        return;

#if CARB_PLATFORM_WINDOWS
    DebugBreak();
#elif CARB_POSIX
    // NOTE: the __builtin_trap() call is the more 'correct and portable' way to do this.  However
    //       that unfortunately raises a SIGILL signal which is not continuable (at least not in
    //       MSVC Android or GDB) so its usefulness in a debugger is limited.  Directly raising a
    //       SIGTRAP signal instead still gives the desired behavior and is also continuable.
    raise(SIGTRAP);
#else
    CARB_UNSUPPORTED_PLATFORM();
#endif
}

/**
 * Attempts to capture the callstack for the current thread.
 *
 * @note Non-debug code and lack of symbols can cause this function to be unable to capture stack frames. Function
 * inlining and tail-calls may result in functions being absent from the backtrace.
 *
 * @param skipFrames The number of callstack frames to skip from the start (current call point) of the backtrace.
 * @param array The array of pointers that is populated with the backtrace. The caller allocates this array.
 * @param count The number of pointers that @p array can hold; the maximum size of the captured backtrace.
 *
 * @return The number of backtrace frames captured in @p array
 */
inline size_t debugBacktrace(size_t skipFrames, void** array, size_t count) noexcept
{
#if CARB_PLATFORM_WINDOWS
    // Apparently RtlCaptureStackBackTrace() can "fail" (i.e. not write anything and return 0) without setting any
    // error for GetLastError(). Try a few times in a loop.
    constexpr static int kRetries = 3;
    for (int i = 0; i != kRetries; ++i)
    {
        unsigned short frames =
            ::RtlCaptureStackBackTrace((unsigned long)skipFrames, (unsigned long)count, array, nullptr);
        if (frames)
            return frames;
    }
    // Failed
    return 0;
#elif CARB_PLATFORM_LINUX
    void** target = array;
    if (skipFrames)
    {
        target = CARB_STACK_ALLOC(void*, count + skipFrames);
    }
    size_t captured = (size_t)::backtrace(target, int(count + skipFrames));
    if (captured <= skipFrames)
        return 0;

    if (skipFrames)
    {
        captured -= skipFrames;
        memcpy(array, target + skipFrames, sizeof(void*) * captured);
    }
    return captured;
#else
    CARB_UNSUPPORTED_PLATFORM();
#endif
}

/**
 * Prints a formatted string to debug output. On Windows this means, OutputDebugString; on Linux, this just prints to
 * the console.
 *
 * @note This should never be used in production code!
 *
 * On Windows, the Sysinternals DebugView utility can be used to view the debug strings outside of a debugger.
 * @param fmt The printf-style format string
 */
void debugPrint(const char* fmt, ...) CARB_PRINTF_FUNCTION(1, 2);
inline void debugPrint(const char* fmt, ...)
{
#if CARB_PLATFORM_WINDOWS
    va_list va, va2;
    va_start(va, fmt);

    va_copy(va2, va);
    int count = vsnprintf(nullptr, 0, fmt, va2);
    va_end(va2);
    if (count > 0)
    {
        char* buffer = CARB_STACK_ALLOC(char, size_t(count) + 1);
        vsnprintf(buffer, size_t(count + 1), fmt, va);
        ::OutputDebugStringA(buffer);
    }
    va_end(va);
#else
    va_list va;
    va_start(va, fmt);
    vfprintf(stdout, fmt, va);
    va_end(va);
#endif
}

} // namespace extras
} // namespace carb

#include "../detail/PopBadMacros.h"
