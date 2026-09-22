// SPDX-FileCopyrightText: Copyright (c) 2018-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
//! @brief carb.profiler macros and helpers
#pragma once

#include "../Defines.h"

#include "../Framework.h"
#include "IProfiler.h"

#include <atomic>
#include <utility>

#include "ProfilerUtils.h"

/**
 * Declares a channel that can be used with the profiler.
 *
 * Channels can be used in place of a mask for macros such as \ref CARB_PROFILE_ZONE. Channels allow enabling and
 * disabling at runtime, or based on a settings configuration.
 *
 * Channels must have static storage and module lifetime, therefore this macro should be used at file-level, class-level
 * or namespace-level scope only. Any other use is undefined behavior.
 *
 * Channels must be declared in exactly one compilation unit for a given module. References to the channel can be
 * accomplished with \ref CARB_PROFILE_EXTERN_CHANNEL for other compilation units that desire to reference the channel.
 *
 * Channel settings are located under `/profiler/channels/<name>` and may have the following values:
 *   - `enabled` - (bool) whether this channel is enabled (reports to the profiler) or not
 *   - `mask` - (uint64_t) the mask used with the profiler
 *
 * @param name_ A string name for this channel. This is used to look up settings keys for this channel.
 * @param defaultMask_ The profiler works with the concept of masks. The profiler must have the capture mask enabled for
 *      this channel to report to the profiler. A typical value for this could be
 *      \ref carb::profiler::kCaptureMaskDefault.
 * @param defaultEnabled_ Whether this channel is enabled to report to the profiler by default.
 * @param symbol_ The symbol name that code would refer to this channel by.
 */
#define CARB_PROFILE_DECLARE_CHANNEL(name_, defaultMask_, defaultEnabled_, symbol_)                                    \
    ::carb::profiler::Channel symbol_((defaultMask_), (defaultEnabled_), "" name_)

/**
 * References a channel declared in another compilation unit.
 *
 * @param symbol_ The symbol name given to the \ref CARB_PROFILE_DECLARE_CHANNEL
 */
#define CARB_PROFILE_EXTERN_CHANNEL(symbol_) extern ::carb::profiler::Channel symbol_

#if CARB_PROFILING || defined(DOXYGEN_BUILD)

/**
 * @defgroup Profiler Helper Macros
 *
 * All of the following macros do nothing if @ref g_carbProfiler is `nullptr` (i.e.
 * carb::profiler::registerProfilerForClient() has not been called).
 * @{
 */

#    ifndef DOXYGEN_BUILD
// The following are helper macros for the profiler.
#        define CARB_PROFILE_IF(cond, true_case, false_case) CARB_PROFILE_IF_HELPER(cond, true_case, false_case)

// Note: CARB_PROFILE_HAS_VARARGS only supports up to 10 args now. If more are desired, increase the sequences below
// and add test cases to TestProfiler.cpp
// This trick is from https://stackoverflow.com/a/36015150/1450686
#        if CARB_COMPILER_MSC
#            define CARB_PROFILE_HAS_VARARGS(x, ...) CARB_PROFILE_EXPAND_ARGS(CARB_PROFILE_AUGMENT_ARGS(__VA_ARGS__))
#        elif CARB_COMPILER_GNUC
#            define CARB_PROFILE_HAS_VARARGS(...)                                                                      \
                CARB_PROFILE_ARGCHK_PRIVATE2(0, ##__VA_ARGS__, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0)
#        else
#            error Unsupported Compiler!
#        endif

// The following are implementation helpers not intended to be used
#        define CARB_PROFILE_IF_HELPER(cond, true_case, false_case)                                                    \
            CARB_JOIN(CARB_PROFILE_IF_HELPER_, cond)(true_case, false_case)
#        define CARB_PROFILE_IF_HELPER_0(true_case, false_case) false_case
#        define CARB_PROFILE_IF_HELPER_1(true_case, false_case) true_case

#        define CARB_PROFILE_AUGMENT_ARGS(...) unused, __VA_ARGS__
#        define CARB_PROFILE_EXPAND_ARGS(...)                                                                          \
            CARB_PROFILE_EXPAND(CARB_PROFILE_ARGCHK_PRIVATE(__VA_ARGS__, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0))
#        define CARB_PROFILE_EXPAND(x) x
#        define CARB_PROFILE_ARGCHK_PRIVATE(_1, _2, _3, _4, _5, _6, _7, _8, _9, _10, count, ...) count
#        define CARB_PROFILE_ARGCHK_PRIVATE2(_0, _1, _2, _3, _4, _5, _6, _7, _8, _9, _10, count, ...) count

#        define CARB_PROFILE_UFUNCFILE(prof, func)                                                                     \
            [p = (prof), f = (func)] {                                                                                 \
                static auto tup = ::carb::profiler::detail::makeString2(                                               \
                    p->registerStaticString(f), p->registerStaticString(__FILE__));                                    \
                return tup;                                                                                            \
            }()

#        define CARB_PROFILE_UFUNCFILESTR(prof, func, str)                                                             \
            [p = (prof), f = (func), s = (str)] {                                                                      \
                static auto tup = ::carb::profiler::detail::makeString3(                                               \
                    p->registerStaticString(f), p->registerStaticString(__FILE__), p->registerStaticString(s));        \
                return tup;                                                                                            \
            }()

#        define CARB_PROFILE_FUNCFILE(func)                                                                            \
            [f = (func)] {                                                                                             \
                if (auto prof = ::g_carbProfiler.load(std::memory_order_acquire))                                      \
                {                                                                                                      \
                    static auto tup = ::carb::profiler::detail::makeString2(                                           \
                        prof->registerStaticString(f), prof->registerStaticString(__FILE__));                          \
                    return tup;                                                                                        \
                }                                                                                                      \
                return ::carb::profiler::detail::emptyTuple2();                                                        \
            }()

#        define CARB_PROFILE_FUNCFILESTR(func, str)                                                                    \
            [f = (func), s = (str)] {                                                                                  \
                if (auto prof = ::g_carbProfiler.load(std::memory_order_acquire))                                      \
                {                                                                                                      \
                    static auto tup = ::carb::profiler::detail::makeString3(prof->registerStaticString(f),             \
                                                                            prof->registerStaticString(__FILE__),      \
                                                                            prof->registerStaticString(s));            \
                    return tup;                                                                                        \
                }                                                                                                      \
                return ::carb::profiler::detail::emptyTuple3();                                                        \
            }()

#        define CARB_PROFILE_CHECKMASK(mask)                                                                           \
            (((mask) ? (mask) : carb::profiler::kCaptureMaskDefault) &                                                 \
             g_carbProfilerMask.load(std::memory_order_acquire))

namespace carb
{
namespace profiler
{
namespace detail
{

// Helper functions for begin that take the tuples created by CARB_PROFILE_UFUNCFILE and CARB_PROFILE_UFUNCFILESTR
template <class... Args>
carb::profiler::ZoneId beginDynamicHelper(::carb::profiler::IProfiler* prof,
                                          const uint64_t mask,
                                          const ::carb::profiler::detail::String2& tup,
                                          int line,
                                          const char* fmt,
                                          Args&&... args)
{
    if (!CARB_PROFILE_CHECKMASK(mask))
        return kNoZoneId;
    return prof->beginDynamic(mask, tup.first, tup.second, line, fmt, std::forward<Args>(args)...);
}
template <class... Args>
carb::profiler::ZoneId beginDynamicHelper(::carb::profiler::IProfiler* prof,
                                          const carb::profiler::Channel& channel,
                                          const ::carb::profiler::detail::String2& tup,
                                          int line,
                                          const char* fmt,
                                          Args&&... args)
{
    if (!channel.isEnabled())
        return kNoZoneId;
    return prof->beginDynamic(channel.getMask(), tup.first, tup.second, line, fmt, std::forward<Args>(args)...);
}
inline carb::profiler::ZoneId beginStaticHelper(::carb::profiler::IProfiler* prof,
                                                const uint64_t mask,
                                                const ::carb::profiler::detail::String3& tup,
                                                int line)
{
    if (!CARB_PROFILE_CHECKMASK(mask))
        return kNoZoneId;
    return prof->beginStatic(mask, tup.first, tup.second, line, tup.third);
}
inline carb::profiler::ZoneId beginStaticHelper(::carb::profiler::IProfiler* prof,
                                                const carb::profiler::Channel& channel,
                                                const ::carb::profiler::detail::String3& tup,
                                                int line)
{
    if (!channel.isEnabled())
        return kNoZoneId;
    return prof->beginStatic(channel.getMask(), tup.first, tup.second, line, tup.third);
}
inline void endHelper(const uint64_t mask, ::carb::profiler::ZoneId id = ::carb::profiler::kUnknownZoneId)
{
    auto prof = ::g_carbProfiler.load(std::memory_order_acquire);
    if (prof && id != ::carb::profiler::kNoZoneId && CARB_PROFILE_CHECKMASK(mask))
        prof->endEx(mask, id);
}
inline void endHelper(const carb::profiler::Channel& channel,
                      ::carb::profiler::ZoneId id = ::carb::profiler::kUnknownZoneId)
{
    auto prof = ::g_carbProfiler.load(std::memory_order_acquire);
    if (prof && id != ::carb::profiler::kNoZoneId && channel.isEnabled())
        prof->endEx(channel.getMask(), id);
}
inline uint64_t maskHelper(uint64_t mask)
{
    return mask;
}
inline uint64_t maskHelper(const carb::profiler::Channel& channel)
{
    return channel.getMask();
}
inline bool enabled(uint64_t mask)
{
    return CARB_PROFILE_CHECKMASK(mask);
}
inline bool enabled(const carb::profiler::Channel& channel)
{
    return channel.isEnabled();
}

inline const ::carb::profiler::detail::String2& emptyTuple2()
{
    static constexpr auto tup = ::carb::profiler::detail::makeString2(kInvalidStaticString, kInvalidStaticString);
    return tup;
}

inline const ::carb::profiler::detail::String3& emptyTuple3()
{
    static constexpr auto tup =
        ::carb::profiler::detail::makeString3(kInvalidStaticString, kInvalidStaticString, kInvalidStaticString);
    return tup;
}

} // namespace detail
} // namespace profiler
} // namespace carb

#    endif

/**
 * Starts the profiler that has been registered with carb::profiler::registerProfilerForClient().
 *
 * When finished with the profiler it should be stopped with CARB_PROFILE_SHUTDOWN().
 *
 * @note This is typically done immediately after carb::profiler::registerProfilerForClient().
 */
#    define CARB_PROFILE_STARTUP()                                                                                     \
        [] {                                                                                                           \
            if (auto prof = ::g_carbProfiler.load(std::memory_order_acquire))                                          \
            {                                                                                                          \
                prof->startup();                                                                                       \
            }                                                                                                          \
        }()

/**
 * Shuts down the profiler that has been registered with carb::profiler::registerProfilerForClient() and previously
 * started with CARB_PROFILE_STARTUP().
 *
 * @note This is typically done immediately before carb::profiler::deregisterProfilerForClient().
 */
#    define CARB_PROFILE_SHUTDOWN()                                                                                    \
        [] {                                                                                                           \
            if (auto prof = ::g_carbProfiler.load(std::memory_order_acquire))                                          \
            {                                                                                                          \
                prof->shutdown();                                                                                      \
            }                                                                                                          \
        }()

/**
 * Registers a static string for use with the profiler.
 *
 * The profiler works by capturing events very quickly in the thread of execution that they happen in, and then
 * processing them later in a background thread. Since static/literal strings are contained in memory that may be
 * invalid once the module unloads, these static/literal strings are registered and copied by the profiler and this
 * macro returns a handle to the string that can be passed to the "static" function such as
 * @ref carb::profiler::IProfiler::beginStatic().
 *
 * @note This macro is used by other helper macros and is typically not used by applications.
 *
 * @warning Undefined behavior occurs if the given string is not a literal or static string.
 *
 * @returns A handle to the static string registered with the profiler. There is no need to unregister this string.
 */
#    define CARB_PROFILE_REGISTER_STRING(str)                                                                          \
        [&] {                                                                                                          \
            if (auto __prof = ::g_carbProfiler.load(std::memory_order_acquire))                                        \
            {                                                                                                          \
                static auto __p = __prof->registerStaticString(str);                                                   \
                return __p;                                                                                            \
            }                                                                                                          \
            return ::carb::profiler::kInvalidStaticString;                                                             \
        }()

/**
 * A helper to set the capture mask.
 *
 * The capture mask is a set of 64 bits. Each profiling zone is *bitwise-and*'d with the capture mask. If the operation
 * matches the profiling zone mask then the event is included in the profiling output. Otherwise, the event is ignored.
 *
 * The default capture mask is profiler-specific, but typically has all bits set (i.e. includes everything).
 * @see carb::profiler::IProfiler::setCaptureMask()
 *
 * @warning Changing the capture mask after the profiler has been started causes undefined behavior.
 */
#    define CARB_PROFILE_SET_CAPTURE_MASK(mask)                                                                        \
        [&] {                                                                                                          \
            if (auto __prof = ::g_carbProfiler.load(std::memory_order_acquire))                                        \
            {                                                                                                          \
                __prof->setCaptureMask(mask);                                                                          \
            }                                                                                                          \
        }()

/**
 * Marks the beginning of a profiling zone.
 *
 * To end the profiling zone, use CARB_PROFILE_END().
 *
 * @warning Consider using CARB_PROFILE_ZONE() to automatically profile a scope. Manual begin and end sections can cause
 * programming errors and confuse the profiler if an end is skipped.
 *
 * @param maskOrChannel The event mask (see carb::profiler::setCaptureMask()) or a channel symbol name.
 * @param eventName The name of the profiling zone. This must be either a literal string or a printf-style format
 * string. Literal strings are far more efficient.
 * @param ... Optional printf-style variadic arguments corresponding to format specifiers in @p eventName.
 * @returns A carb::profiler::ZoneId that is unique to this zone and should be passed to CARB_PROFILE_END().
 */
#    define CARB_PROFILE_BEGIN(maskOrChannel, eventName, ...)                                                          \
        [&, __prof = g_carbProfiler.load(std::memory_order_acquire), __func = __func__] {                              \
            return __prof ? CARB_PROFILE_IF(CARB_PROFILE_HAS_VARARGS((eventName), ##__VA_ARGS__),                      \
                                            ::carb::profiler::detail::beginDynamicHelper(                              \
                                                __prof, (maskOrChannel), CARB_PROFILE_UFUNCFILE(__prof, __func),       \
                                                __LINE__, (eventName), ##__VA_ARGS__),                                 \
                                            ::carb::profiler::detail::beginStaticHelper(                               \
                                                __prof, (maskOrChannel),                                               \
                                                CARB_PROFILE_UFUNCFILESTR(__prof, __func, (eventName)), __LINE__)) :   \
                            (0 ? /*compiler validate*/ printf((eventName), ##__VA_ARGS__) : 0);                        \
        }()

/**
 * Marks the end of a profiling zone previously started with CARB_PROFILE_BEGIN().
 *
 * @warning Consider using CARB_PROFILE_ZONE() to automatically profile a scope. Manual begin and end sections can cause
 * programming errors and confuse the profiler if an end is skipped.
 *
 * @param maskOrChannel The event mask or a channel symbol. This should match the value passed to CARB_PROFILE_BEGIN().
 * @param ... The carb::profiler::ZoneId returned from CARB_PROFILE_BEGIN(), if known. This will help the profiler to
 *    validate that the proper zone was ended.
 */
#    define CARB_PROFILE_END(maskOrChannel, ...) ::carb::profiler::detail::endHelper((maskOrChannel), ##__VA_ARGS__)

/**
 * Inserts a frame marker for the calling thread in the profiling output, for profilers that support frame markers.
 *
 * @note The name provided below must be the same for each set of frames, and called each time from the same thread.
 * For example you might have main thread frames that all are named "frame" and GPU frames that are named "GPU
 * frame". Some profilers (i.e. profiler-cpu to Tracy conversion) require that the name contain the word "frame."
 *
 * @param maskOrChannel Deprecated and ignored for frame events.
 * @param frameName A name for the frame. This must either be a literal string or a printf-style format string. Literal
 *    strings are far more efficient. See the note above about frame names.
 * @param ... Optional printf-style variadic arguments corresponding to format specifiers in @p frameName.
 */
#    define CARB_PROFILE_FRAME(maskOrChannel, frameName, ...)                                                          \
        [&] {                                                                                                          \
            /* Use printf to validate the format string */                                                             \
            if (0)                                                                                                     \
            {                                                                                                          \
                printf((frameName), ##__VA_ARGS__);                                                                    \
            }                                                                                                          \
            if (auto __prof = ::g_carbProfiler.load(std::memory_order_acquire))                                        \
            {                                                                                                          \
                CARB_PROFILE_IF(                                                                                       \
                    CARB_PROFILE_HAS_VARARGS((frameName), ##__VA_ARGS__),                                              \
                    __prof->frameDynamic(0, (frameName), ##__VA_ARGS__), __prof->frameStatic(0, [__prof]() {           \
                        static ::carb::profiler::StaticStringType p = __prof->registerStaticString("" frameName);      \
                        return p;                                                                                      \
                    }()));                                                                                             \
            }                                                                                                          \
        }()

/**
 * Creates a profiling zone over a scope.
 *
 * This macro creates a temporary object on the stack that automatically begins a profiling zone at the point where this
 * macro is used, and automatically ends the profiling zone when it goes out of scope.
 *
 * @param maskOrChannel The event mask (see carb::profiler::setCaptureMask()) or a channel symbol.
 * @param zoneName The name of the profiling zone. This must be either a literal string or a printf-style format string.
 * Literal strings are far more efficient.
 * @param ... Optional printf-style variadic arguments corresponding to format specifiers in @p zoneName.
 */
#    define CARB_PROFILE_ZONE(maskOrChannel, zoneName, ...)                                                            \
        CARB_PROFILE_IF(CARB_PROFILE_HAS_VARARGS((zoneName), ##__VA_ARGS__),                                           \
                        ::carb::profiler::ProfileZoneDynamic CARB_JOIN(_carbZone, __LINE__)(                           \
                            (maskOrChannel), CARB_PROFILE_FUNCFILE(__func__), __LINE__, (zoneName), ##__VA_ARGS__),    \
                        ::carb::profiler::ProfileZoneStatic CARB_JOIN(_carbZone, __LINE__)(                            \
                            (maskOrChannel), CARB_PROFILE_FUNCFILESTR(__func__, (zoneName)), __LINE__))

/**
 * A helper for CARB_PROFILE_ZONE() that automatically uses the function name as from `CARB_PRETTY_FUNCTION`.
 *
 * Equivalent, but faster than: `CARB_PROFILE_ZONE(mask, "%s", CARB_PRETTY_FUNCTION)`.
 *
 * @param maskOrChannel The event mask (see carb::profiler::setCaptureMask()) or a profiling channel.
 */
#    define CARB_PROFILE_FUNCTION(maskOrChannel)                                                                       \
        ::carb::profiler::ProfileZoneStatic CARB_JOIN(_carbZoneFunction, __LINE__)(                                    \
            (maskOrChannel), CARB_PROFILE_FUNCFILESTR(__func__, CARB_PRETTY_FUNCTION), __LINE__)

/**
 * Writes a named numeric value to the profiling output for profilers that support them.
 *
 * @note Supported types for @p value are `float`, `uint32_t` and `int32_t`.
 *
 * @param value The value to record.
 * @param maskOrChannel The event mask (see carb::profiler::setCaptureMask()) or a profiling channel.
 * @param valueName The name of the value. This must be either a literal string or a printf-style format string. Literal
 *    strings are far more efficient.
 * @param ... Optional printf-style variadic arguments corresponding to format specifiers in @p valueName.
 */
#    define CARB_PROFILE_VALUE(value, maskOrChannel, valueName, ...)                                                   \
        [&, __prof = ::g_carbProfiler.load(std::memory_order_acquire)] {                                               \
            /* Use printf to validate the format string */                                                             \
            if (0)                                                                                                     \
            {                                                                                                          \
                printf((valueName), ##__VA_ARGS__);                                                                    \
            }                                                                                                          \
            auto&& __moc = (maskOrChannel);                                                                            \
            if (__prof && ::carb::profiler::detail::enabled(__moc))                                                    \
            {                                                                                                          \
                CARB_PROFILE_IF(CARB_PROFILE_HAS_VARARGS((valueName), ##__VA_ARGS__),                                  \
                                __prof->valueDynamic(                                                                  \
                                    ::carb::profiler::detail::maskHelper(__moc), (value), (valueName), ##__VA_ARGS__), \
                                __prof->valueStatic(::carb::profiler::detail::maskHelper(__moc), (value), [__prof]() { \
                                    static ::carb::profiler::StaticStringType p =                                      \
                                        __prof->registerStaticString("" valueName);                                    \
                                    return p;                                                                          \
                                }()));                                                                                 \
            }                                                                                                          \
        }()

/**
 * Records an allocation event for a named memory pool for profilers that support them.
 *
 * @param maskOrChannel The event mask (see carb::profiler::setCaptureMask()) or a profiling channel.
 * @param ptr The memory address that was allocated.
 * @param size The size of the memory region beginning at @p ptr.
 * @param poolName The name of the memory pool. This must be either a literal string or a printf-style format string.
 * Literal strings are far more efficient.
 * @param ... Optional printf-style variadic arguments corresponding to format specifiers in @p poolName.
 */
#    define CARB_PROFILE_ALLOC_NAMED(maskOrChannel, ptr, size, poolName, ...)                                          \
        [&, __prof = ::g_carbProfiler.load(std::memory_order_acquire)] {                                               \
            /* Use printf to validate the format string */                                                             \
            if (0)                                                                                                     \
            {                                                                                                          \
                printf((poolName), ##__VA_ARGS__);                                                                     \
            }                                                                                                          \
            auto&& __moc = (maskOrChannel);                                                                            \
            if (__prof && ::carb::profiler::detail::enabled(__moc))                                                    \
            {                                                                                                          \
                CARB_PROFILE_IF(                                                                                       \
                    CARB_PROFILE_HAS_VARARGS((poolName), ##__VA_ARGS__),                                               \
                    __prof->allocNamedDynamic(                                                                         \
                        ::carb::profiler::detail::maskHelper(__moc), (ptr), (size), (poolName), ##__VA_ARGS__),        \
                    __prof->allocNamedStatic(::carb::profiler::detail::maskHelper(__moc), (ptr), (size), [__prof]() {  \
                        static ::carb::profiler::StaticStringType p = __prof->registerStaticString("" poolName);       \
                        return p;                                                                                      \
                    }()));                                                                                             \
            }                                                                                                          \
        }()

/**
 * Records a free event for a named memory pool for profilers that support them.
 *
 * @param maskOrChannel The event mask (see carb::profiler::setCaptureMask()) or a profiling channel. This should match
 *      the value passed to CARB_PROFILE_ALLOC_NAMED() for the same allocation.
 * @param ptr The memory address that was freed.
 * @param poolName The name of the memory pool. This must be either a literal string or a printf-style format string.
 * Literal strings are far more efficient.
 * @param ... Optional printf-style variadic arguments corresponding to format specifiers in @p poolName.
 */
#    define CARB_PROFILE_FREE_NAMED(maskOrChannel, ptr, poolName, ...)                                                 \
        [&, __prof = ::g_carbProfiler.load(std::memory_order_acquire)] {                                               \
            /* Use printf to validate the format string */                                                             \
            if (0)                                                                                                     \
            {                                                                                                          \
                printf((poolName), ##__VA_ARGS__);                                                                     \
            }                                                                                                          \
            auto&& __moc = (maskOrChannel);                                                                            \
            if (__prof && ::carb::profiler::detail::enabled(__moc))                                                    \
            {                                                                                                          \
                CARB_PROFILE_IF(                                                                                       \
                    CARB_PROFILE_HAS_VARARGS((poolName), ##__VA_ARGS__),                                               \
                    __prof->freeNamedDynamic(                                                                          \
                        ::carb::profiler::detail::maskHelper(__moc), (ptr), (poolName), ##__VA_ARGS__),                \
                    __prof->freeNamedStatic(::carb::profiler::detail::maskHelper(__moc), (ptr), [__prof]() {           \
                        static ::carb::profiler::StaticStringType p = __prof->registerStaticString("" poolName);       \
                        return p;                                                                                      \
                    }()));                                                                                             \
            }                                                                                                          \
        }()

/**
 * Records an allocation event for profilers that support them.
 *
 * @param maskOrChannel The event mask (see carb::profiler::setCaptureMask()) or a profiling channel.
 * @param ptr The memory address that was allocated.
 * @param size The size of the memory region beginning at @p ptr.
 */
#    define CARB_PROFILE_ALLOC(maskOrChannel, ptr, size)                                                               \
        [&, __prof = ::g_carbProfiler.load(std::memory_order_acquire)] {                                               \
            auto&& __moc = (maskOrChannel);                                                                            \
            if (__prof && ::carb::profiler::detail::enabled(__moc))                                                    \
            {                                                                                                          \
                __prof->allocStatic(::carb::profiler::detail::maskHelper(__moc), (ptr), (size));                       \
            }                                                                                                          \
        }()

/**
 * Records a free event for profilers that support them.
 *
 * @param maskOrChannel The event mask (see carb::profiler::setCaptureMask()) or a profiling channel.
 * @param ptr The memory address that was freed.
 */
#    define CARB_PROFILE_FREE(maskOrChannel, ptr)                                                                      \
        [&, __prof = ::g_carbProfiler.load(std::memory_order_acquire)] {                                               \
            auto&& __moc = (maskOrChannel);                                                                            \
            if (__prof && ::carb::profiler::detail::enabled(__moc))                                                    \
            {                                                                                                          \
                __prof->freeStatic(::carb::profiler::detail::maskHelper(__moc), (ptr));                                \
            }                                                                                                          \
        }()

/**
 * Records the name of a thread.
 *
 * @param tidOrZero The thread ID that is being named. A value of `0` indicates the current thread. Not all profilers
 * support values other than `0`.
 * @param threadName The name of the thread. This must be either a literal string or a printf-style format string.
 * Literal strings are far more efficient.
 * @param ... Optional printf-style variadic arguments corresponding to format specifiers in @p threadName.
 */
#    define CARB_NAME_THREAD(tidOrZero, threadName, ...)                                                               \
        [&] {                                                                                                          \
            /* Use printf to validate the format string */                                                             \
            if (0)                                                                                                     \
            {                                                                                                          \
                printf((threadName), ##__VA_ARGS__);                                                                   \
            }                                                                                                          \
            if (auto __prof = ::g_carbProfiler.load(std::memory_order_acquire))                                        \
            {                                                                                                          \
                CARB_PROFILE_IF(CARB_PROFILE_HAS_VARARGS((threadName), ##__VA_ARGS__),                                 \
                                __prof->nameThreadDynamic((tidOrZero), (threadName), ##__VA_ARGS__),                   \
                                __prof->nameThreadStatic((tidOrZero), [__prof]() {                                     \
                                    static ::carb::profiler::StaticStringType p =                                      \
                                        __prof->registerStaticString("" threadName);                                   \
                                    return p;                                                                          \
                                }()));                                                                                 \
            }                                                                                                          \
        }()

/**
 * Records an instant event on a thread's timeline at the current time.
 *
 * @param maskOrChannel The event mask (see carb::profiler::setCaptureMask()) or a profiling channel.
 * @param type The type of the instant event that will be passed to carb::profiler::emitInstantStatic() or
 *   carb::profiler::emitInstantDynamic().
 * @param name The name of the event. This must either be a literal string or a printf-style format string with variadic
 *   arguments. Literal strings are far more efficient.
 * @param ... Optional printf-style variadic arguments corresponding to format specifiers in @p name.
 */
#    define CARB_PROFILE_EVENT(maskOrChannel, type, name, ...)                                                         \
        [&, __prof = ::g_carbProfiler.load(std::memory_order_acquire), __func = CARB_PRETTY_FUNCTION] {                \
            if (0)                                                                                                     \
                printf((name), ##__VA_ARGS__);                                                                         \
            auto&& __moc = (maskOrChannel);                                                                            \
            if (__prof && ::carb::profiler::detail::enabled(__moc))                                                    \
            {                                                                                                          \
                CARB_PROFILE_IF(CARB_PROFILE_HAS_VARARGS((name), ##__VA_ARGS__),                                       \
                                static auto __tup = ::carb::profiler::detail::makeString2(                             \
                                    __prof->registerStaticString(__func), __prof->registerStaticString(__FILE__));     \
                                __prof->emitInstantDynamic(::carb::profiler::detail::maskHelper(__moc), __tup.first,   \
                                                           __tup.second, __LINE__, (type), (name), ##__VA_ARGS__),     \
                                static auto __tup = ::carb::profiler::detail::makeString3(                             \
                                    __prof->registerStaticString(__func), __prof->registerStaticString(__FILE__),      \
                                    __prof->registerStaticString(name));                                               \
                                __prof->emitInstantStatic(::carb::profiler::detail::maskHelper(__moc), __tup.first,    \
                                                          __tup.second, __LINE__, (type), __tup.third));               \
            }                                                                                                          \
        }()

/**
 * Records the beginning of a flow event on the timeline at the current time for the current thread.
 *
 * Flow events draw an arrow from one point (the `BEGIN` location) to another point (the `END` location).
 * These two points can be in different threads but must have a matching @p id field. The @p id field is meant to be
 * unique across profiler runs, but may be reused as long as the @p name field matches across all `BEGIN` events and
 * events occur on the global timeline as `BEGIN` followed by `END`.
 *
 * This macro will automatically insert an instant event on the current thread's timeline.
 *
 * @param maskOrChannel The event mask (see carb::profiler::setCaptureMask()) or a profiling channel.
 * @param id A unique identifier that must also be passed to CARB_PROFILE_FLOW_END().
 * @param name The name of the event. This must either be a literal string or a printf-style format string with variadic
 *   arguments. Literal strings are far more efficient.
 * @param ... Optional printf-style variadic arguments corresponding to format specifiers in @p name.
 */
#    define CARB_PROFILE_FLOW_BEGIN(maskOrChannel, id, name, ...)                                                      \
        [&, __prof = ::g_carbProfiler.load(std::memory_order_acquire), __func = CARB_PRETTY_FUNCTION] {                \
            if (0)                                                                                                     \
                printf((name), ##__VA_ARGS__);                                                                         \
            auto&& __moc = (maskOrChannel);                                                                            \
            if (__prof && ::carb::profiler::detail::enabled(__moc))                                                    \
            {                                                                                                          \
                CARB_PROFILE_IF(                                                                                       \
                    CARB_PROFILE_HAS_VARARGS(name, ##__VA_ARGS__),                                                     \
                    static auto __tup = ::carb::profiler::detail::makeString2(                                         \
                        __prof->registerStaticString(__func), __prof->registerStaticString(__FILE__));                 \
                    __prof->emitFlowDynamic(::carb::profiler::detail::maskHelper(__moc), __tup.first, __tup.second,    \
                                            __LINE__, ::carb::profiler::FlowType::Begin, (id), (name), ##__VA_ARGS__), \
                    static auto __tup = ::carb::profiler::detail::makeString3(__prof->registerStaticString(__func),    \
                                                                              __prof->registerStaticString(__FILE__),  \
                                                                              __prof->registerStaticString("" name));  \
                    __prof->emitFlowStatic(::carb::profiler::detail::maskHelper(__moc), __tup.first, __tup.second,     \
                                           __LINE__, ::carb::profiler::FlowType::Begin, (id), __tup.third));           \
            }                                                                                                          \
        }()

/**
 * Records the end of a flow event on the timeline at the current time for the current thread.
 *
 * @see CARB_PROFILE_FLOW_BEGIN()
 *
 * @param maskOrChannel The event mask or profiling channel. Must match the value given to CARB_PROFILE_FLOW_BEGIN().
 * @param id Th unique identifier passed to CARB_PROFILE_FLOW_BEGIN().
 */
#    define CARB_PROFILE_FLOW_END(maskOrChannel, id)                                                                     \
        [&, __prof = ::g_carbProfiler.load(std::memory_order_acquire), __func = CARB_PRETTY_FUNCTION] {                  \
            auto&& __moc = (maskOrChannel);                                                                              \
            if (__prof && ::carb::profiler::detail::enabled(__moc))                                                      \
            {                                                                                                            \
                static auto __tup = ::carb::profiler::detail::makeString2(                                               \
                    __prof->registerStaticString(__func), __prof->registerStaticString(__FILE__));                       \
                __prof->emitFlowStatic(::carb::profiler::detail::maskHelper(__moc), __tup.first, __tup.second, __LINE__, \
                                       ::carb::profiler::FlowType::End, (id), ::carb::profiler::kInvalidStaticString);   \
            }                                                                                                            \
        }()


/**
 * Create a new GPU profiling context that allows injecting timestamps coming from a GPU in a deferred manner
 *
 * @param name name of the context
 * @param correlatedCpuTimestampNs correlated GPU clock timestamp (in nanoseconds)
 * @param correlatedGpuTimestamp correlated GPU clock timestamp (raw value)
 * @param gpuTimestampPeriodNs is the number of nanoseconds required for a GPU timestamp query to be incremented
 * by 1.
 * @param graphicsApi string of graphic API used ['vulkan'/'d3d12']
 * @returns a valid ID or kInvalidGpuContextId if creation fails
 */
#    define CARB_PROFILE_CREATE_GPU_CONTEXT(                                                                           \
        name, correlatedCpuTimestampNs, correlatedGpuTimestamp, gpuTimestampPeriodNs, graphicsApi)                     \
        [&, __prof = ::g_carbProfiler.load(std::memory_order_acquire)]() {                                             \
            return __prof ? __prof->createGpuContext((name), (correlatedCpuTimestampNs), (correlatedGpuTimestamp),     \
                                                     (gpuTimestampPeriodNs), (graphicsApi)) :                          \
                            ::carb::profiler::kInvalidGpuContextId;                                                    \
        }()

/**
 * Destroy a previously created GPU Context
 *
 * @param contextId ID of the context, returned by createGpuContext
 */
#    define CARB_PROFILE_DESTROY_GPU_CONTEXT(contextId)                                                                \
        [&] {                                                                                                          \
            if (auto __prof = ::g_carbProfiler.load(std::memory_order_acquire))                                        \
            {                                                                                                          \
                __prof->destroyGpuContext(contextId);                                                                  \
            }                                                                                                          \
        }()

/**
 * Submit context calibration information that allows correlating CPU and GPU clocks
 *
 * @param contextId ID of the context, returned by @ref carb::profiler::IProfiler::createGpuContext()
 * @param correlatedCpuTimestampNs The new CPU timestamp at the time of correlation (in nanoseconds)
 * @param previousCorrelatedCpuTimestampNs The CPU timestamp at the time of previous correlation (in nanoseconds)
 * @param correlatedGpuTimestamp The new raw GPU timestamp at the time of correlation
 */
#    define CARB_PROFILE_CALIBRATE_GPU_CONTEXT(                                                                         \
        contextId, correlatedCpuTimestampNs, previousCorrelatedCpuTimestampNs, correlatedGpuTimestamp)                  \
        [&, __prof = ::g_carbProfiler.load(std::memory_order_acquire)]() {                                              \
            return __prof ? __prof->calibrateGpuContext((contextId), (correlatedCpuTimestampNs),                        \
                                                        (previousCorrelatedCpuTimestampNs), (correlatedGpuTimestamp)) : \
                            false;                                                                                      \
        }()


/**
 * Record the beginning of a new GPU timestamp query
 *
 * @param maskOrChannel Event capture mask or profiling channel.
 * @param contextId The id of the context as returned by @ref carb::profiler::IProfiler::createGpuContext()
 * @param queryId Unique query id (for identification when passing to @ref
 *   carb::profiler::IProfiler::setGpuQueryValue())
 * @param eventName The name for the event.
 */
#    define CARB_PROFILE_GPU_QUERY_BEGIN(maskOrChannel, contextId, queryId, eventName, ...)                              \
        [&, __prof = ::g_carbProfiler.load(std::memory_order_acquire), __func = CARB_PRETTY_FUNCTION] {                  \
            if (0)                                                                                                       \
                printf((eventName), ##__VA_ARGS__);                                                                      \
            auto&& __moc = (maskOrChannel);                                                                              \
            if (__prof && ::carb::profiler::detail::enabled(__moc))                                                      \
            {                                                                                                            \
                CARB_PROFILE_IF(                                                                                         \
                    CARB_PROFILE_HAS_VARARGS((eventName), ##__VA_ARGS__),                                                \
                    static auto __tup = ::carb::profiler::detail::makeString2(                                           \
                        __prof->registerStaticString(__func), __prof->registerStaticString(__FILE__));                   \
                    __prof->beginGpuQueryDynamic(::carb::profiler::detail::maskHelper(__moc), __tup.first, __tup.second, \
                                                 __LINE__, (contextId), (queryId), (eventName), ##__VA_ARGS__),          \
                    static auto __tup = ::carb::profiler::detail::makeString3(                                           \
                        __prof->registerStaticString(__func), __prof->registerStaticString(__FILE__),                    \
                        __prof->registerStaticString("" eventName));                                                     \
                    __prof->beginGpuQueryStatic(::carb::profiler::detail::maskHelper(__moc), __tup.first,                \
                                                __tup.second, __LINE__, (contextId), (queryId), __tup.third));           \
            }                                                                                                            \
        }()

/**
 * Record the end of a new GPU timestamp query
 *
 * @param maskOrChannel Event capture mask or profiling channel.
 * @param contextId The id of the context as returned by @ref carb::profiler::IProfiler::createGpuContext()
 * @param queryId Unique query id (for identification when passing to @ref
 *   carb::profiler::IProfiler::setGpuQueryValue())
 */
#    define CARB_PROFILE_GPU_QUERY_END(maskOrChannel, contextId, queryId)                                              \
        [&, __prof = ::g_carbProfiler.load(std::memory_order_acquire)] {                                               \
            auto&& __moc = (maskOrChannel);                                                                            \
            if (__prof && ::carb::profiler::detail::enabled(__moc))                                                    \
            {                                                                                                          \
                __prof->endGpuQuery(::carb::profiler::detail::maskHelper(__moc), (contextId), (queryId));              \
            }                                                                                                          \
        }()


/**
 * Set the value we've received from the GPU for a query (begin or end) we've issued in the past
 *
 * @param maskOrChannel Event capture mask or profiling channel
 * @param contextId The id of the context as returned by @ref carb::profiler::IProfiler::createGpuContext()
 * @param queryId Unique query id specified at begin/end time
 * @param gpuTimestamp Raw GPU timestamp value
 */
#    define CARB_PROFILE_GPU_SET_QUERY_VALUE(maskOrChannel, contextId, queryId, gpuTimestamp)                          \
        [&, __prof = ::g_carbProfiler.load(std::memory_order_acquire)] {                                               \
            auto&& __moc = (maskOrChannel);                                                                            \
            if (__prof && ::carb::profiler::detail::enabled(__moc))                                                    \
            {                                                                                                          \
                __prof->setGpuQueryValue(                                                                              \
                    ::carb::profiler::detail::maskHelper(__moc), (contextId), (queryId), (gpuTimestamp));              \
            }                                                                                                          \
        }()


/**
 *  Create a lockable context which we can use to tag lock operation
 * @note Do not use this macro directly. Use \ref carb::profiler::ProfiledMutex or
 * \ref carb::profiler::ProfiledSharedMutex instead.
 * @param maskOrChannel Event capture mask or profiling channel
 * @param isSharedLock If this shared for a shared lock
 * @param name The lockable context name
 */
#    define CARB_PROFILE_LOCKABLE_CREATE(maskOrChannel, isSharedLock, name)                                            \
        [&, __prof = ::g_carbProfiler.load(std::memory_order_acquire), __func = CARB_PRETTY_FUNCTION] {                \
            auto&& __moc = (maskOrChannel);                                                                            \
            if (__prof && ::carb::profiler::detail::enabled(__moc))                                                    \
            {                                                                                                          \
                static auto __tup = ::carb::profiler::detail::makeString2(                                             \
                    __prof->registerStaticString(__func), __prof->registerStaticString(__FILE__));                     \
                return __prof->createLockable(::carb::profiler::detail::maskHelper(__moc), (name), (isSharedLock),     \
                                              __tup.first, __tup.second, __LINE__);                                    \
            }                                                                                                          \
            return ::carb::profiler::kInvalidLockableId;                                                               \
        }()


/**
 * Destroy a lockable context
 * @note Do not use this macro directly. Use \ref carb::profiler::ProfiledMutex or
 * \ref carb::profiler::ProfiledSharedMutex instead.
 * @param lockableId the id of the lockable as returned by @ref carb::profiler::IProfiler::createLockable()
 */
#    define CARB_PROFILE_LOCKABLE_DESTROY(lockableId)                                                                  \
        [&, __prof = ::g_carbProfiler.load(std::memory_order_acquire)] {                                               \
            auto&& __id = (lockableId);                                                                                \
            if (__prof && __id != carb::profiler::kInvalidLockableId)                                                  \
            {                                                                                                          \
                __prof->destroyLockable(__id);                                                                         \
            }                                                                                                          \
        }()

/**
 * Records a lockable operation on a thread's timeline at the current time.
 * @note Do not use this macro directly. Use \ref carb::profiler::ProfiledMutex or
 * \ref carb::profiler::ProfiledSharedMutex instead.
 * @param lockableId the id of the lockable as returned by @ref carb::profiler::IProfiler::createLockable()
 * @param operation which lock operation to tag
 */
#    define CARB_PROFILE_LOCKABLE_OPERATION(lockableId, operation)                                                     \
        [&, __prof = ::g_carbProfiler.load(std::memory_order_acquire)] {                                               \
            auto&& __id = (lockableId);                                                                                \
            if (__prof && __id != carb::profiler::kInvalidLockableId)                                                  \
            {                                                                                                          \
                __prof->lockableOperation(__id, (operation));                                                          \
            }                                                                                                          \
        }()


/**
 * Inserts an anonymous frame marker along with an RGBA image (for profilers that support it).
 *
 * @param maskOrChannel Deprecated and ignored for frame events.
 * @param rgbaImageData pointer to the start of the image data (pixels must be in RGBA order)
 * @param imageDataSizeInBytes total size in bytes of the image data
 * @param width in pixels of the image data (must be a multiple of 4)
 * @param height in pixels of the image data (must be a multiple of 4)
 */
#    define CARB_PROFILE_FRAME_WITH_IMAGE(maskOrChannel, rgbaImageData, imageDataSizeInBytes, width, height)           \
        [&, __prof = ::g_carbProfiler.load(std::memory_order_acquire)] {                                               \
            auto&& __moc = (maskOrChannel);                                                                            \
            if (__prof && ::carb::profiler::detail::enabled(__moc))                                                    \
            {                                                                                                          \
                return __prof->frameWithImage(::carb::profiler::detail::maskHelper(__moc), (rgbaImageData),            \
                                              (imageDataSizeInBytes), (width), (height));                              \
            }                                                                                                          \
        }()

/// @}
#else

#    define CARB_PROFILE_STARTUP() (void(0))
#    define CARB_PROFILE_SHUTDOWN() (void(0))
#    define CARB_PROFILE_REGISTER_STRING(str) (CARB_UNUSED(str), ::carb::profiler::kInvalidStaticString)
#    define CARB_PROFILE_SET_CAPTURE_MASK(mask) CARB_UNUSED(mask)
#    define CARB_PROFILE_BEGIN(maskOrChannel, eventName, ...)                                                          \
        (CARB_UNUSED((maskOrChannel), (eventName), ##__VA_ARGS__), ::carb::profiler::kNoZoneId)
#    define CARB_PROFILE_END(maskOrChannel, ...) CARB_UNUSED((maskOrChannel), ##__VA_ARGS__)
#    define CARB_PROFILE_FRAME(mask, frameName, ...) CARB_UNUSED((mask), (frameName), ##__VA_ARGS__)
#    define CARB_PROFILE_ZONE(maskOrChannel, zoneName, ...) CARB_UNUSED((maskOrChannel), (zoneName), ##__VA_ARGS__)
#    define CARB_PROFILE_FUNCTION(maskOrChannel) CARB_UNUSED(maskOrChannel)
#    define CARB_PROFILE_VALUE(value, maskOrChannel, valueName, ...)                                                   \
        CARB_UNUSED((value), (maskOrChannel), (valueName), ##__VA_ARGS__)
#    define CARB_PROFILE_ALLOC_NAMED(maskOrChannel, ptr, size, poolName, ...)                                          \
        CARB_UNUSED((maskOrChannel), (ptr), (size), (poolName), ##__VA_ARGS__)
#    define CARB_PROFILE_FREE_NAMED(maskOrChannel, ptr, poolName, ...)                                                 \
        CARB_UNUSED((maskOrChannel), (ptr), (poolName), ##__VA_ARGS__)
#    define CARB_PROFILE_ALLOC(maskOrChannel, ptr, size) CARB_UNUSED((maskOrChannel), (ptr), (size))
#    define CARB_PROFILE_FREE(maskOrChannel, ptr) CARB_UNUSED((maskOrChannel), (ptr))
#    define CARB_NAME_THREAD(tidOrZero, threadName, ...) CARB_UNUSED((tidOrZero), (threadName), ##__VA_ARGS__)
#    define CARB_PROFILE_EVENT(maskOrChannel, type, name, ...)                                                         \
        CARB_UNUSED((maskOrChannel), (type), (name), ##__VA_ARGS__)
#    define CARB_PROFILE_FLOW_BEGIN(maskOrChannel, id, name, ...)                                                      \
        CARB_UNUSED((maskOrChannel), (id), (name), ##__VA_ARGS__)
#    define CARB_PROFILE_FLOW_END(maskOrChannel, id) CARB_UNUSED((maskOrChannel), (id))
#    define CARB_PROFILE_CREATE_GPU_CONTEXT(                                                                           \
        name, correlatedCpuTimestampNs, correlatedGpuTimestamp, gpuTimestampPeriodNs, graphicApi)                      \
        (CARB_UNUSED(                                                                                                  \
             (name), (correlatedCpuTimestampNs), (correlatedGpuTimestamp), (gpuTimestampPeriodNs), (graphicsApi)),     \
         carb::profiler::kInvalidGpuContextId)
#    define CARB_PROFILE_DESTROY_GPU_CONTEXT(contextId) CARB_UNUSED(contextId)
#    define CARB_PROFILE_CALIBRATE_GPU_CONTEXT(                                                                        \
        contextId, correlatedCpuTimestampNs, previousCorrelatedCpuTimestampNs, correlatedGpuTimestamp)                 \
        CARB_UNUSED(                                                                                                   \
            (contextId), (correlatedCpuTimestampNs), (previousCorrelatedCpuTimestampNs), (correlatedGpuTimestamp))
#    define CARB_PROFILE_GPU_QUERY_BEGIN(maskOrChannel, contextId, queryId, eventName, ...)                            \
        CARB_UNUSED((maskOrChannel), (contextId), (queryId), (eventName), ##__VA_ARGS__)
#    define CARB_PROFILE_GPU_QUERY_END(maskOrChannel, contextId, queryId)                                              \
        (CARB_UNUSED((maskOrChannel), (contextId), (queryId)))
#    define CARB_PROFILE_GPU_SET_QUERY_VALUE(maskOrChannel, contextId, queryId, gpuTimestamp)                          \
        CARB_UNUSED((maskOrChannel), (contextId), (queryId), (gpuTimestamp))
#    define CARB_PROFILE_LOCKABLE_CREATE(maskOrChannel, isSharedLock, name)                                            \
        (CARB_UNUSED((maskOrChannel), (isSharedLock), (name)), ::carb::profiler::kInvalidLockableId)
#    define CARB_PROFILE_LOCKABLE_DESTROY(lockableId) CARB_UNUSED(lockableId)
#    define CARB_PROFILE_LOCKABLE_OPERATION(lockableId, operation) CARB_UNUSED((lockableId), (operation))
#    define CARB_PROFILE_FRAME_WITH_IMAGE(maskOrChannel, imageData, sizeInBytes, width, height)                        \
        CARB_UNUSED((maskOrChannel), (imageData), (sizeInBytes), (width), (height))
#endif

/**
 * Placeholder macro for any work that needs to be done at the global scope for the profiler.
 * @note This is typically not used as it is included in the @ref CARB_GLOBALS_EX macro.
 */
#define CARB_PROFILER_GLOBALS()

namespace carb
{
namespace profiler
{

/**
 * Wrapper to add automatic profiling to a mutex
 */
template <class Mutex>
class ProfiledMutex
{
public:
    /**
     * Constructor.
     * @param profileMask The mask used to determine if events from this mutex are captured.
     * @param name The name of the mutex
     */
    ProfiledMutex(const uint64_t profileMask, const char* name) : ProfiledMutex(profileMask, false, name)
    {
    }

    /**
     * Constructor.
     * @param channel The profiling channel used to determine if events from this mutex are captured.
     * @param name The name of the mutex
     */
    ProfiledMutex(const carb::profiler::Channel& channel, const char* name) : ProfiledMutex(channel, false, name)
    {
    }

    /**
     * Destructor.
     */
    ~ProfiledMutex()
    {
        CARB_PROFILE_LOCKABLE_DESTROY(m_lockableId);
    }

    /**
     * Locks the underlying mutex and reports the event to the profiler.
     */
    void lock()
    {
        CARB_PROFILE_LOCKABLE_OPERATION(m_lockableId, LockableOperationType::BeforeLock);
        m_mutex.lock();
        CARB_PROFILE_LOCKABLE_OPERATION(m_lockableId, LockableOperationType::AfterLock);
    }

    /**
     * Attempts a lock on the underlying mutex and reports the event to the profiler if successful.
     * @returns \c true if successfully locked; \c false otherwise.
     */
    bool try_lock()
    {
        bool acquired = m_mutex.try_lock();
        if (acquired)
        {
            CARB_PROFILE_LOCKABLE_OPERATION(m_lockableId, LockableOperationType::AfterSuccessfulTryLock);
        }
        return acquired;
    }

    /**
     * Unlocks the underlying mutex and reports the event to the profiler.
     */
    void unlock()
    {
        m_mutex.unlock();
        CARB_PROFILE_LOCKABLE_OPERATION(m_lockableId, LockableOperationType::AfterUnlock);
    }

    /**
     * Returns a reference to the underlying mutex.
     * @returns a reference to the underlying mutex.
     */
    Mutex& getMutex()
    {
        return m_mutex;
    }

    /**
     * Returns a reference to the underlying mutex.
     * @returns a reference to the underlying mutex.
     */
    const Mutex& getMutex() const
    {
        return m_mutex;
    }

protected:
    /**
     * Protected Constructor.
     * @param profileMask The mask used to determine if events from this mutex are captured.
     * @param isSharedMutex A boolean representing whether `*this` represents a shared mutex.
     * @param name The name of the mutex
     */
    ProfiledMutex(const uint64_t profileMask, bool isSharedMutex, const char* name)
    {
        m_lockableId = CARB_PROFILE_LOCKABLE_CREATE(profileMask, isSharedMutex, name);
    }
    /**
     * Protected Constructor.
     * @param channel The channel used to determine if events from this mutex are captured.
     * @param isSharedMutex A boolean representing whether `*this` represents a shared mutex.
     * @param name The name of the mutex
     */
    ProfiledMutex(const carb::profiler::Channel& channel, bool isSharedMutex, const char* name)
    {
        m_lockableId = CARB_PROFILE_LOCKABLE_CREATE(channel, isSharedMutex, name);
    }

    //! The underlying mutex instance
    Mutex m_mutex;
    //! The lockable ID as returned by \ref carb::profiler::IProfiler::createLockable()
    LockableId m_lockableId;
};

/**
 * Wrapper to add automatic profiling to a shared mutex
 */
template <class Mutex>
class ProfiledSharedMutex : public ProfiledMutex<Mutex>
{
    using Base = ProfiledMutex<Mutex>;

public:
    /**
     * Constructor.
     * @param profileMask The mask used to determine if events from this mutex are captured.
     * @param name The name of the mutex
     */
    ProfiledSharedMutex(const uint64_t profileMask, const char* name) : Base(profileMask, true, name)
    {
    }

    /**
     * Constructor.
     * @param channel The profiling channel used to determine if events from this mutex are captured.
     * @param name The name of the mutex
     */
    ProfiledSharedMutex(const carb::profiler::Channel& channel, const char* name) : Base(channel, true, name)
    {
    }

    /**
     * Destructor.
     */
    ~ProfiledSharedMutex()
    {
    }

    /**
     * Locks the underlying mutex (shared) and reports the event to the profiler.
     */
    void lock_shared()
    {
        CARB_PROFILE_LOCKABLE_OPERATION(this->m_lockableId, LockableOperationType::BeforeLockShared);
        this->m_mutex.lock_shared();
        CARB_PROFILE_LOCKABLE_OPERATION(this->m_lockableId, LockableOperationType::AfterLockShared);
    }

    /**
     * Attempts a shared lock on the underlying mutex and reports the event to the profiler if successful.
     * @returns \c true if successfully locked; \c false otherwise.
     */
    bool try_lock_shared()
    {
        bool acquired = this->m_mutex.try_lock_shared();
        if (acquired)
        {
            CARB_PROFILE_LOCKABLE_OPERATION(this->m_lockableId, LockableOperationType::AfterSuccessfulTryLockShared);
        }
        return acquired;
    }

    /**
     * Unlocks (shared) the underlying mutex and reports the event to the profiler.
     */
    void unlock_shared()
    {
        this->m_mutex.unlock_shared();
        CARB_PROFILE_LOCKABLE_OPERATION(this->m_lockableId, LockableOperationType::AfterUnlockShared);
    }
};


void deregisterProfilerForClient() noexcept;

#ifndef DOXYGEN_SHOULD_SKIP_THIS
namespace detail
{

inline void updateMask(uint64_t mask)
{
    g_carbProfilerMask.store(mask, std::memory_order_release);
}

inline void releaseHook(void* iface, void*)
{
    g_carbProfiler.store(nullptr, std::memory_order_seq_cst);
    getFramework()->removeReleaseHook(iface, &releaseHook, nullptr);
}

inline void frameworkReleaseHook(void*, void*)
{
    // Framework is going away, so make sure we get fully deregistered.
    deregisterProfilerForClient();
}

inline void loadHook(const PluginDesc&, void*)
{
    if (!g_carbProfiler)
    {
        IProfiler* profiler = getFramework()->tryAcquireInterface<IProfiler>();
        if (profiler)
        {
            if (profiler->setMaskCallback)
            {
                // Relaxed semantics since we will shortly be synchronizing on g_carbProfiler.
                g_carbProfilerMask.store(profiler->setMaskCallback(updateMask, true), std::memory_order_relaxed);
            }
            else
            {
                g_carbProfilerMask.store(uint64_t(-1), std::memory_order_relaxed); // not supported; let everything
                                                                                   // through
            }
            getFramework()->addReleaseHook(profiler, &detail::releaseHook, nullptr);
            g_carbProfiler.store(profiler, std::memory_order_seq_cst); // sequentially consistent
        }
    }
}

inline bool& registered()
{
    static bool r{ false };
    return r;
}

inline LoadHookHandle& loadHookHandle()
{
    static carb::LoadHookHandle handle{};
    return handle;
}

} // namespace detail
#endif

/**
 * Allows access to the @ref g_carbProfiler global variable previously registered with @ref registerProfilerForClient().
 * @returns The value of @ref g_carbProfiler.
 */
inline IProfiler* getProfiler(std::memory_order order = std::memory_order_seq_cst)
{
    return g_carbProfiler.load(order);
}

/**
 * Clears the @ref g_carbProfiler global variable and unregisters load and release hooks with the \ref Framework.
 */
inline void deregisterProfilerForClient() noexcept
{
    if (std::exchange(detail::registered(), false))
    {
        auto fw = getFramework();
        auto handle = std::exchange(detail::loadHookHandle(), kInvalidLoadHook);
        IProfiler* profiler = g_carbProfiler.exchange(nullptr, std::memory_order_seq_cst);
        if (fw)
        {
            if (profiler && fw->verifyInterface(profiler) && profiler->setMaskCallback)
            {
                profiler->setMaskCallback(detail::updateMask, false);
            }
            if (handle)
            {
                fw->removeLoadHook(handle);
            }
            fw->removeReleaseHook(nullptr, &detail::frameworkReleaseHook, nullptr);
            if (profiler)
            {
                fw->removeReleaseHook(profiler, &detail::releaseHook, nullptr);
            }

            // Unregister channels
            Channel::onProfilerUnregistered();
        }
    }
}

/**
 * Acquires the default IProfiler interface and assigns it to the @ref g_carbProfiler global variable.
 *
 * If a profiler is not yet loaded, a load hook is registered with the \ref Framework and when the profiler is loaded,
 * \ref g_carbProfiler will be automatically set for this module. If the profiler is unloaded, \ref g_carbProfiler will
 * be automatically set to `nullptr`.
 */
inline void registerProfilerForClient() noexcept
{
    if (!std::exchange(detail::registered(), true))
    {
        auto fw = getFramework();
        fw->addReleaseHook(nullptr, &detail::frameworkReleaseHook, nullptr);
        IProfiler* profiler = fw->tryAcquireInterface<IProfiler>();
        if (profiler)
        {
            if (profiler->setMaskCallback)
            {
                // Relaxed semantics since we will shortly be synchronizing on g_carbProfiler.
                g_carbProfilerMask.store(profiler->setMaskCallback(detail::updateMask, true), std::memory_order_relaxed);
            }
            else
            {
                g_carbProfilerMask.store(uint64_t(-1), std::memory_order_relaxed); // let everything through
            }
            bool b = fw->addReleaseHook(profiler, &detail::releaseHook, nullptr);
            CARB_ASSERT(b);
            CARB_UNUSED(b);
        }
        g_carbProfiler.store(profiler, std::memory_order_seq_cst); // sequentially consistent
        detail::loadHookHandle() = fw->addLoadHook<IProfiler>(nullptr, &detail::loadHook, nullptr);

        // Register channels
        Channel::onProfilerRegistered();

        // Make sure this only happens once even if re-registered.
        static bool ensureDeregister = (atexit(&deregisterProfilerForClient), true);
        CARB_UNUSED(ensureDeregister);
    }
}

} // namespace profiler
} // namespace carb
