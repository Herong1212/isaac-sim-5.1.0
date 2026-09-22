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
//! @brief carb.logging utilities
#pragma once

#include "../Framework.h"
#include "ILogging.h"

#include "../../omni/log/ILog.h"
#include "../cpp/Optional.h"

#include <cctype>
#include <cstdint>
#include <cstdio>

// example-begin Log levels
namespace carb
{
namespace logging
{

//! \defgroup loglevel Log Levels
//! @{

/**
 * Verbose level, this is for detailed diagnostics messages. Expect to see some verbose messages on every frame under
 * certain conditions.
 */
const int32_t kLevelVerbose = -2;
/**
 * Info level, this is for informational messages. They are usually triggered on state changes and typically we should
 * not see the same message on every frame.
 */
const int32_t kLevelInfo = -1;
/**
 * Warning level, this is for warning messages. Something could be wrong but not necessarily an error. Therefore
 * anything that could be a problem but cannot be determined to be an error should fall into this category. This is the
 * default log level threshold, if nothing else was specified via configuration or startup arguments. This is also the
 * reason why it has a value of 0 (default as zero).
 */
const int32_t kLevelWarn = 0;
/**
 * Error level, this is for error messages. An error has occurred but the program can continue.
 */
const int32_t kLevelError = 1;
/**
 * Fatal level, this is for messages on unrecoverable errors. An error has occurred and the program cannot continue.
 * After logging such a message the caller should take immediate action to exit the program or unload the module.
 */
const int32_t kLevelFatal = 2;

//! @}

} // namespace logging
} // namespace carb
// example-end

//! A global weak variable representing the current log level.
//! @note This variable is registered by \ref carb::logging::registerLoggingForClient() and is updated whenever the
//!   logging level changes.
//! @warning If \ref carb::logging::deregisterLoggingForClient() is not called before a module is unloaded, changing the
//!   log level can result in a crash since \ref carb::logging::ILogging retains a pointer to this variable.
CARB_WEAKLINK int32_t g_carbLogLevel = carb::logging::kLevelWarn;
//! A global weak variable cache of the logging function.
//!
//! This variable is initialized by \ref carb::logging::registerLoggingForClient() and stores a pointer to
//!   \ref carb::logging::ILogging::log() for performance, so that the interface does not have to constantly be acquired
//!   (even via \ref carb::getCachedInterface()).
CARB_WEAKLINK carb::logging::LogFn g_carbLogFn CARB_PRINTF_FUNCTION(6, 7);
//! A global weak variable cache of the logging interface.
//!
//! This variable is initialized by \ref carb::logging::registerLoggingForClient(). As \ref carb::logging::ILogging is a
//! built-in interface from the Carbonite Framework, this variable can be safely cached without
//! \ref carb::getCachedInterface().
CARB_WEAKLINK carb::logging::ILogging* g_carbLogging;

#if CARB_COMPILER_GNUC || defined(DOXYGEN_BUILD)
/**
 * A printf that will never be executed but allows the compiler to test if there are format errors.
 *
 * This is a no-op on GCC and Clang because they support `__attribute__((format))`.
 * @param fmt The printf format specifier
 * @param ... Optional arguments
 */
#    define CARB_FAKE_PRINTF(fmt, ...)                                                                                 \
        do                                                                                                             \
        {                                                                                                              \
        } while (0)
#else
#    define CARB_FAKE_PRINTF(fmt, ...)                                                                                 \
        do                                                                                                             \
        {                                                                                                              \
            if (false)                                                                                                 \
                ::printf(fmt, ##__VA_ARGS__);                                                                          \
        } while (0)
#endif

//! \defgroup logmacros Logging Macros
//! @{

//! Logging macro if the level is dynamic.
//!
//! Prefer using @ref CARB_LOG_VERBOSE, @ref CARB_LOG_INFO, etc. if the level is static.
//! @param level The \ref loglevel
//! @param fmt The printf format specifier string
//! @param ... Optional arguments
#define CARB_LOG(level, fmt, ...)                                                                                      \
    do                                                                                                                 \
    {                                                                                                                  \
        auto lvl = (level);                                                                                            \
        if (g_carbLogFn && g_carbLogLevel <= lvl)                                                                      \
        {                                                                                                              \
            CARB_FAKE_PRINTF(fmt, ##__VA_ARGS__);                                                                      \
            g_carbLogFn(g_carbClientName, lvl, __FILE__, __func__, __LINE__, fmt, ##__VA_ARGS__);                      \
        }                                                                                                              \
    } while (0)

//! Logging macro for static log level.
//! @param fmt The printf format specifier string
//! @param ... Optional arguments
#define CARB_LOG_VERBOSE(fmt, ...) CARB_LOG(carb::logging::kLevelVerbose, fmt, ##__VA_ARGS__)
//! @copydoc CARB_LOG_VERBOSE
#define CARB_LOG_INFO(fmt, ...) CARB_LOG(carb::logging::kLevelInfo, fmt, ##__VA_ARGS__)
//! @copydoc CARB_LOG_VERBOSE
#define CARB_LOG_WARN(fmt, ...) CARB_LOG(carb::logging::kLevelWarn, fmt, ##__VA_ARGS__)
//! @copydoc CARB_LOG_VERBOSE
#define CARB_LOG_ERROR(fmt, ...) CARB_LOG(carb::logging::kLevelError, fmt, ##__VA_ARGS__)
//! @copydoc CARB_LOG_VERBOSE
#define CARB_LOG_FATAL(fmt, ...) CARB_LOG(carb::logging::kLevelFatal, fmt, ##__VA_ARGS__)

//! Single-time logging macro if the level is dynamic.
//!
//! Prefer using @ref CARB_LOG_VERBOSE_ONCE, @ref CARB_LOG_INFO_ONCE, etc. if the level is static.
//! @note This logs a single time by using `static` initialization.
//! @param level The \ref loglevel
//! @param fmt The print format specifier string
//! @param ... Optional arguments
#define CARB_LOG_ONCE(level, fmt, ...)                                                                                   \
    do                                                                                                                   \
    {                                                                                                                    \
        static bool CARB_JOIN(logged_, __LINE__) =                                                                       \
            (g_carbLogFn && g_carbLogLevel <= (level)) ?                                                                 \
                (false ?                                                                                                 \
                     (::printf(fmt, ##__VA_ARGS__), true) :                                                              \
                     (g_carbLogFn(g_carbClientName, (level), __FILE__, __func__, __LINE__, fmt, ##__VA_ARGS__), true)) : \
                false;                                                                                                   \
        CARB_UNUSED(CARB_JOIN(logged_, __LINE__));                                                                       \
    } while (0)

//! Single-time logging macro for static log level.
//! @note This logs a single time by using `static` initialization.
//! @param fmt The print format specifier string
//! @param ... Optional arguments
#define CARB_LOG_VERBOSE_ONCE(fmt, ...) CARB_LOG_ONCE(carb::logging::kLevelVerbose, fmt, ##__VA_ARGS__)
//! @copydoc CARB_LOG_VERBOSE_ONCE
#define CARB_LOG_INFO_ONCE(fmt, ...) CARB_LOG_ONCE(carb::logging::kLevelInfo, fmt, ##__VA_ARGS__)
//! @copydoc CARB_LOG_VERBOSE_ONCE
#define CARB_LOG_WARN_ONCE(fmt, ...) CARB_LOG_ONCE(carb::logging::kLevelWarn, fmt, ##__VA_ARGS__)
//! @copydoc CARB_LOG_VERBOSE_ONCE
#define CARB_LOG_ERROR_ONCE(fmt, ...) CARB_LOG_ONCE(carb::logging::kLevelError, fmt, ##__VA_ARGS__)
//! @copydoc CARB_LOG_VERBOSE_ONCE
#define CARB_LOG_FATAL_ONCE(fmt, ...) CARB_LOG_ONCE(carb::logging::kLevelFatal, fmt, ##__VA_ARGS__)

//! @}

//! Placeholder macro for any globals that must be declared for the logging system.
//! @note This is typically not used as it is included in the @ref CARB_GLOBALS_EX macro.
#define CARB_LOG_GLOBALS()

namespace carb
{
namespace logging
{

//! Accessor for logging interface.
//! @returns \ref ILogging interface as read from \ref g_carbLogging
inline ILogging* getLogging()
{
    return g_carbLogging;
}

//! Acquires the default ILogging interface and registers log channels.
//!
//! This acquires the \ref ILogging interface and assigns it to a special \ref g_carbLogging variable. The
//! \ref g_carbLogLevel variable is registered with \ref ILogging so that it is kept up to date when log level changes.
//! The \ref g_carbLogFn variable is also initialized. Finally \ref omni::log::addModulesChannels() is called to
//! register log channels.
//! @note It is typically not necessary to call this function. It is automatically called for plugins by
//!   \ref carb::pluginInitialize() (in turn called by \ref CARB_PLUGIN_IMPL). For script bindings it is called by
//!   \ref carb::acquireFrameworkForBindings(). For applications it is called by
//!   \ref carb::acquireFrameworkAndRegisterBuiltins() (typically called by \ref OMNI_CORE_INIT).
//! @see deregisterLoggingForClient()
inline void registerLoggingForClient() noexcept
{
    g_carbLogging = getFramework()->tryAcquireInterface<ILogging>();
    if (g_carbLogging)
    {
        g_carbLogging->registerSource(g_carbClientName, [](int32_t logLevel) { g_carbLogLevel = logLevel; });
        g_carbLogFn = g_carbLogging->log;
    }

    omni::log::addModulesChannels();
}

//! Unregisters the log channels and the logger interface.
//!
//! @note It is typically not necessary to call this function as it is automatically called in similar situations to
//!   those described in @ref registerLoggingForClient().
inline void deregisterLoggingForClient() noexcept
{
    omni::log::removeModulesChannels();

    if (g_carbLogging)
    {
        g_carbLogFn = nullptr;
        if (getFramework() && getFramework()->verifyInterface<ILogging>(g_carbLogging))
        {
            g_carbLogging->unregisterSource(g_carbClientName);
        }
        g_carbLogging = nullptr;
    }
}

//! A struct that describes level name to integer value
struct StringToLogLevelMapping
{
    const char* name; //!< Log level name
    int32_t level; //!< Log level integer value (see \ref loglevel)
};

//! A mapping of log level names to integer value
//! @see loglevel
const StringToLogLevelMapping kStringToLevelMappings[] = { { "verbose", kLevelVerbose },
                                                           { "info", kLevelInfo },
                                                           { "warning", kLevelWarn },
                                                           { "error", kLevelError },
                                                           { "fatal", kLevelFatal } };

//! The number of items in \ref kStringToLevelMappings.
const size_t kStringToLevelMappingsCount = CARB_COUNTOF(kStringToLevelMappings);

/**
 * Convert a given string to a log level.
 *
 * Compares the given \p levelString against \ref kStringToLevelMappings to find a match. Only the first character is
 * checked in a case insensitive manner.
 * @param levelString A string representing the name of a log level. `nullptr` is interpreted as \ref kLevelFatal. Only
 *   the first character of the string is checked in a case insensitive manner.
 * @returns The integer \ref loglevel determined from \p levelString. If a level could not be determined,
 *   \ref kLevelFatal is returned after an error log is issued.
 */
inline int32_t stringToLevel(const char* levelString)
{
    const int32_t kFallbackLevel = kLevelFatal;
    if (!levelString)
        return kFallbackLevel;

    // Since our log level identifiers start with different characters, we're allowed to just compare the first one.
    // However, whether the need arises, it is worth making a score-based system, where full match will win over
    // partial match, if there are similarly starting log levels.
    int lcLevelChar = tolower((unsigned char)levelString[0]);
    for (size_t lm = 0; lm < kStringToLevelMappingsCount; ++lm)
    {
        int lcMappingChar = tolower((unsigned char)kStringToLevelMappings[lm].name[0]);
        if (lcLevelChar == lcMappingChar)
            return kStringToLevelMappings[lm].level;
    }

    // Ideally, this should never happen if level string is valid.
    CARB_ASSERT(false);
    CARB_LOG_ERROR("Unknown log level string: %s", levelString);
    return kFallbackLevel;
}

/** @copydoc stringToLevel(const char*) */
inline int32_t stringToLevel(carb::cpp::optional<std::string> levelString)
{
    return stringToLevel(levelString ? levelString->c_str() : nullptr);
}


} // namespace logging
} // namespace carb
