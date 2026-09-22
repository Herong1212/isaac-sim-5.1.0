// Copyright (c) 2023-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#include <carb/extras/Debugging.h>
#include <carb/crashreporter/CrashReporterUtils.h>

// CARB_FAIL_UNLESS is similar to CARB_FATAL_UNLESS in syntax, but it doesn't terminate on cond=false
// but instead just logs an error that will fail tests or breaks into the debugger if one is attached.
// It should only be used for non-recoverable coding errors. Non-recoverable NOT in the sense of a guaranteed
// crash, but rather in the sense of an unexpected logic error (NOT data error) that will not be handled or repaired.
// When the breakpoint is hit in the debugger use s_ignore = true in watch window to ignore future failures

#ifndef CARB_ENABLE_FAIL
#   ifdef CARB_SHIPPING
#       define CARB_ENABLE_FAIL 0
#   else // CARB_SHIPPING
#       define CARB_ENABLE_FAIL 1
#   endif
#endif

#define CARB_BREAK_POINT_IF_DEBUGGER_ATTACHED() do {                   \
    if (carb::extras::isDebuggerAttached())                            \
        CARB_BREAK_POINT();                                            \
} while (false)

#if CARB_ENABLE_FAIL

#   define CARB_FAIL_UNLESS_IMPL(cond, onlyOnce, fmt, ...)             \
        if(CARB_UNLIKELY(!(cond)))                                     \
        {                                                              \
            static bool s_ignore = false;                              \
            if (!s_ignore)                                             \
            {                                                          \
                s_ignore = onlyOnce;                                   \
                CARB_LOG_ERROR(fmt, ##__VA_ARGS__);                    \
                carb::crashreporter::addCrashMetadata("carbFailure", 1); \
                carb::crashreporter::addCrashMetadata("carbFailureMessage", fmt); \
                CARB_BREAK_POINT_IF_DEBUGGER_ATTACHED();               \
            }                                                          \
        }                                                                                                              

#   define CARB_FAIL_UNLESS(cond, fmt, ...)                            \
        CARB_FAIL_UNLESS_IMPL(cond, false, fmt, ##__VA_ARGS__)

#   define CARB_FAIL_ONCE_UNLESS(cond, fmt, ...)                       \
        CARB_FAIL_UNLESS_IMPL(cond, true, fmt, ##__VA_ARGS__)

#else  // #if CARB_ENABLE_FAIL

    #define CARB_FAIL_UNLESS(cond, fmt, ...)
    #define CARB_FAIL_ONCE_UNLESS(cond, fmt, ...)

#endif // #if !CARB_ENABLE_FAIL
