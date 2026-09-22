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
//! @brief carb.logging interface definition
#pragma once

#include "../Interface.h"
#include "../IObject.h"

#include <string>

//! Latest version for carb::logging::ILogging
#define carb_logging_ILogging_latest CARB_HEXVERSION(1, 5)
#ifndef carb_logging_ILogging
//! The default current version for carb::logging::ILogging
#    define carb_logging_ILogging CARB_HEXVERSION(1, 1)
#endif

#include "StandardLogger2.h"

namespace carb
{
namespace logging
{


struct StandardLogger;
class StandardLogger2;
struct Logger;
struct Logger2;

/**
 * Defines a callback type for setting log level for every source.
 */
typedef void(CARB_ABI* SetLogLevelFn)(int32_t logLevel);

/** Base type for the flags that control how extra fields on log messages are managed.
 *  These flags are used in functions like ILogging::modifyExtraFieldValue(),
 *  ILogging::addExtraField(), ILogging::removeExtraField(), etc.
 */
using ExtraFieldFlags = uint32_t;

/** No special behavior will be used when only this flag is specified.  This will assume the
 *  default behavior of either adding or removing the specified extra field in the global
 *  list.  The field will be removed if the given value string is `nullptr`.
 */
constexpr ExtraFieldFlags fExtraFieldFlagNone = 0x00;

/** The new extra field value will be treated as global on all threads for this process.  This
 *  flag will take precedence over the @ref fExtraFieldFlagThread flag if both are present.
 *  If neither this flag nor @ref fExtraFieldFlagThread are specified, a global extra field
 *  is assumed.
 */
constexpr ExtraFieldFlags fExtraFieldFlagGlobal = 0x00;

/** The new extra field value will only be added for or modified in the calling thread.  If the
 *  global list contains an extra field with the same key name, both extra fields will be included
 *  with each log message on the calling thread.  This flag will be superceded by
 *  @ref fExtraFieldFlagGlobal if both are present.
 */
constexpr ExtraFieldFlags fExtraFieldFlagThread = 0x01;

/**
 * Defines a log setting behavior.
 */
enum class LogSettingBehavior
{
    eInherit,
    eOverride
};

/**
 * Function pointer typedef for a logging function
 *
 * @note Typically this is not used directly. It exists solely for \ref g_carbLogFn and represents the type of
 *   \ref carb::logging::ILogging::log().
 * @param source The log source (typically client or plugin)
 * @param level The log level, such as \ref kLevelInfo
 * @param fileName The name of the source file that generated the log message (typically from `__FILE__`)
 * @param functionName The name of the source function that generated the log message (such as via
 *   \ref CARB_PRETTY_FUNCTION)
 * @param lineNumber The line number of \p filename that generated the log message (typically from `__LINE__`)
 * @param fmt A printf format string
 * @param ... varargs for \p fmt
 */
typedef void (*LogFn)(const char* source,
                      int32_t level,
                      const char* fileName,
                      const char* functionName,
                      int lineNumber,
                      const char* fmt,
                      ...);

namespace detail
{

/** @private */
enum class ExtraFieldOperation
{
    eCreateOrModify,
    eDelete,
    eExists,
};

} // namespace detail

// 'destroyStandardLoggerOld' is deprecated: Use StandardLogger2::release() instead
CARB_IGNOREWARNING_CLANG_WITH_PUSH("-Wdeprecated-declarations")

/**
 * Defines the log system that is associated with the Framework.
 *
 * This interface defines the log system, which is a singleton object. It can be used at any moment, including
 * before the startup of the Framework and after the Framework was shutdown. It allows a user to setup the logging
 * behavior in advance and allows the Framework to log during its initialization.
 *
 * Logger - is an interface for logging backend. ILogging can contain multiple Loggers and every message will be passed
 * to every logger. There is one implementation of a Logger provided - StandardLogger. It can log into file, console and
 * debug window. ILogging starts up with one instance of \ref StandardLogger2, which can be retrieved by calling
 * getDefaultLogger(). It is added by default, but can be removed with
 * `getLogging()->removeLogger(getLogging()->getDefaultLogger()->getLogger())`.
 *
 * ILogging supports multiple sources of log messages. Source is just a name to differentiate the origins of a message.
 * Every plugin, application and Framework itself are different sources. However user can add more custom sources if
 * needed.
 *
 * Use the logging macros from Log.h for all logging in applications and plugins.
 *
 * There are 2 log settings: log level (to control log severity threshold) and log enabled (to toggle whole logging).
 * Both of them can be set globally and per source.
 */
struct ILogging
{
    CARB_PLUGIN_INTERFACE_EX("carb::logging::ILogging", carb_logging_ILogging_latest, carb_logging_ILogging)

    /**
     * Logs a formatted message to the specified log source and log level.
     *
     * This API is used primarily by the CARB_LOG_XXXX macros.
     *
     * @param source The log source to log the message to.
     * @param level The level to log the message at.
     * @param fileName The file name to log to.
     * @param functionName The name of the function where the message originated from.
     * @param lineNumber The line number
     * @param fmt The print formatted message.
     * @param ... The variable arguments for the formatted message variables.
     */
    void(CARB_ABI* log)(const char* source,
                        int32_t level,
                        const char* fileName,
                        const char* functionName,
                        int lineNumber,
                        const char* fmt,
                        ...) CARB_PRINTF_FUNCTION(6, 7);

    /**
     * Sets global log level threshold. Messages below this threshold will be dropped.
     *
     * @param level The log level to set.
     */
    void(CARB_ABI* setLevelThreshold)(int32_t level);

    /**
     * Gets global log level threshold. Messages below this threshold will be dropped.
     *
     * @return Global log level.
     */
    int32_t(CARB_ABI* getLevelThreshold)();

    /**
     * Sets global log enabled setting.
     *
     * @param enabled Global log enabled setting.
     */
    void(CARB_ABI* setLogEnabled)(bool enabled);

    /**
     * If global log is enabled.
     *
     * @return Global log enabled.
     */
    bool(CARB_ABI* isLogEnabled)();

    /**
     * Sets log level threshold for the specified source. Messages below this threshold will be dropped.
     * Per source log settings can either inherit global or override it, it is configured with
     * LogSettingBehavior::eInherit and LogSettingBehavior::eOverride accordingly.
     *
     * @param source The source to set log level setting for. Must not be nullptr.
     * @param behavior The log setting behavior for the source.
     * @param level The log level to set. This param is ignored if behavior is set to LogSettingBehavior::eInherit.
     */
    void(CARB_ABI* setLevelThresholdForSource)(const char* source, LogSettingBehavior behavior, int32_t level);

    /**
     * Sets log enabled setting for the specified source.
     * Per source log settings can either inherit global or override it, it is configured with
     * LogSettingBehavior::eInherit and LogSettingBehavior::eOverride accordingly.
     *
     * @param source The source to set log enabled setting for. Must not be nullptr.
     * @param behavior The log setting behavior for the source.
     * @param enabled The log enabled setting. This param is ignored if behavior is set to LogSettingBehavior::eInherit.
     */
    void(CARB_ABI* setLogEnabledForSource)(const char* source, LogSettingBehavior behavior, bool enabled);

    /**
     * Reset all log settings set both globally and per source.
     * Log system resets to the defaults: log is enabled and log level is 'warn'.
     */
    void(CARB_ABI* reset)();

#if CARB_VERSION_ATLEAST(carb_logging_ILogging, 1, 3)
    static_assert(carb_logging_ILogging < CARB_HEXVERSION(2, 0), "Remove this function on major version change");
    //! @private
    CARB_DEPRECATED("Use addLogger() instead.") void(CARB_ABI* addLoggerOld)(Logger* logger);

    //! @private
    CARB_DEPRECATED("Use removeLogger() instead") void(CARB_ABI* removeLoggerOld)(Logger* logger);
#else
    /**
     * Adds a logger to the ILogging.
     * @see StandardLogger2::getLogger()
     * @param logger The logger to be added.
     */
    void(CARB_ABI* addLogger)(Logger* logger);

    /**
     * Removes the logger from the ILogging.
     * @see StandardLogger2::getLogger()
     * @param logger The logger to be removed.
     */
    void(CARB_ABI* removeLogger)(Logger* logger);
#endif

#if CARB_VERSION_ATLEAST(carb_logging_ILogging, 1, 1)
    /**
     * Accesses the default logger.
     *
     * This logger can be disabled by passing it to \ref removeLogger(). This logger is owned by the logging system and
     * cannot be destroyed by passing it to \ref destroyStandardLoggerOld().
     *
     * @rst
     * .. deprecated:: 156.0
     *     Use getDefaultLogger() instead
     * @endrst
     *
     * @returns the default logger.
     */
    CARB_DEPRECATED("Use getDefaultLogger() instead") StandardLogger*(CARB_ABI* getDefaultLoggerOld)();

    /**
     * Creates a new \ref StandardLogger instance.
     *
     * Use this method to create additional \ref StandardLogger instances. This can be useful when you want to log
     * to multiple output destinations but want different configuration for each. Use \ref addLogger() to make it
     * active. When finished with the \ref StandardLogger pass it to \ref destroyStandardLoggerOld().
     *
     * @rst
     * .. deprecated:: 156.0
     *     Use createStandardLogger() instead
     * @endrst
     *
     * @returns A new \ref StandardLogger.
     */
    CARB_DEPRECATED("Use createStandardLogger() instead") StandardLogger*(CARB_ABI* createStandardLoggerOld)();

    /**
     * Use this method to destroy a \ref StandardLogger that was created via \ref createStandardLoggerOld().
     *
     * @rst
     * .. deprecated:: 156.0
     *     The ``StandardLogger2`` that replaces ``StandardLogger`` can be destroyed by calling ``release()``.
     * @endrst
     *
     * @param logger The logger to be destroyed.
     */
    CARB_DEPRECATED("Use StandardLogger2::release() instead")
    void(CARB_ABI* destroyStandardLoggerOld)(StandardLogger* logger);
#else
    /**
     * Accesses the default logger.
     *
     * This logger can be disabled by passing it to \ref removeLogger(). This logger is owned by the logging system and
     * cannot be destroyed by passing it to \ref destroyStandardLogger().
     *
     * @returns the default logger.
     */
    StandardLogger*(CARB_ABI* getDefaultLogger)();

    /**
     * Creates a new \ref StandardLogger instance.
     *
     * Use this method to create additional \ref StandardLogger instances. This can be useful when you want to log
     * to multiple output destinations but want different configuration for each. Use \ref addLogger() to make it
     * active. When finished with the \ref StandardLogger pass it to \ref destroyStandardLogger().
     *
     * @returns A new \ref StandardLogger.
     */
    StandardLogger*(CARB_ABI* createStandardLogger)();

    /**
     * Use this method to destroy a \ref StandardLogger that was created via \ref createStandardLogger().
     *
     * @param logger The logger to be destroyed.
     */
    void(CARB_ABI* destroyStandardLogger)(StandardLogger* logger);
#endif

    /**
     * Register new logging source.
     * This function is mainly automatically used by plugins, application and the Framework itself to create
     * their own logging sources.
     *
     * Custom logging source can also be created if needed. It is the user's responsibility to call
     * ILogging::unregisterSource in that case.
     *
     * It is the source responsibility to track its log level. The reason is that it allows to filter out
     * logging before calling into the logging system, thus making the performance cost for the disabled logging
     * negligible. It is done by providing a callback `setLevelThreshold` to be called by ILogging when any setting
     * which influences this source is changed.
     *
     * @param source The source name. Must not be nullptr.
     * @param setLevelThreshold The callback to be called to update log level. ILogging::unregisterSource must be called
     * when the callback is no longer valid.
     */
    void(CARB_ABI* registerSource)(const char* source, SetLogLevelFn setLevelThreshold);

    /**
     * Unregister logging source.
     *
     * @param source The source name. Must not be nullptr.
     */
    void(CARB_ABI* unregisterSource)(const char* source);

    /**
     * Instructs the logging system to deliver all log messages to the Logger backends asynchronously. Async logging is
     * OFF by default.
     *
     * This causes log() calls to be buffered so that log() may return as quickly as possible. A background thread then
     * issues these buffered log messages to the registered Logger backend objects.
     *
     * @param logAsync True to use async logging; false to disable async logging.
     * @return true if was previously using async logging; false if was previously using synchronous logging.
     */
    bool(CARB_ABI* setLogAsync)(bool logAsync);

    /**
     * Returns whether the ILogging system is using async logging.
     * @return true if currently using async logging; false if currently using synchronous logging
     */
    bool(CARB_ABI* getLogAsync)();

    /**
     * When ILogging is in async mode, wait until all log messages have flushed out to the various loggers.
     */
    void(CARB_ABI* flushLogs)();

#if CARB_VERSION_ATLEAST(carb_logging_ILogging, 1, 1)
    /**
     * Retrieves the extended StandardLogger2 interface from an old \ref StandardLogger instance.
     * @param logger The logger to retrieve the instance from. If `nullptr` then `nullptr` will be returned.
     * @returns The \ref StandardLogger2 interface for \p logger, or `nullptr`.
     */
    StandardLogger2*(CARB_ABI* getStandardLogger2)(StandardLogger* logger);

    /**
     * Accesses the default logger.
     *
     * This logger can be disabled by passing the underlying logger (from \ref StandardLogger2::getLogger()) to
     * \ref removeLogger(). This logger is owned by the logging system and calling \ref StandardLogger2::release() has
     * no effect.
     *
     * @returns the default \ref StandardLogger2.
     */
    StandardLogger2*(CARB_ABI* getDefaultLogger)();

    //! @private
    StandardLogger2*(CARB_ABI* createStandardLoggerInternal)();

    /**
     * Creates a new \ref StandardLogger2 instance.
     *
     * Use this method to create additional \ref StandardLogger2 instances. This can be useful when you want to log
     * to multiple output destinations but want different configuration for each. Pass the value from
     * \ref StandardLogger2::getLogger() to \ref addLogger() to make it active. When finished with the
     * \ref StandardLogger2 call \ref StandardLogger2::release().
     *
     * @returns A new \ref StandardLogger2.
     */
    ObjectPtr<StandardLogger2> createStandardLogger()
    {
        using Ptr = ObjectPtr<StandardLogger2>;
        return Ptr(createStandardLoggerInternal(), Ptr::InitPolicy::eSteal);
    }
#endif

#if CARB_VERSION_ATLEAST(carb_logging_ILogging, 1, 3)
    /**
     * Adds a logger to the ILogging.
     * @see StandardLogger2::getLogger()
     * @param logger The logger to be added.
     */
    void(CARB_ABI* addLogger)(Logger2* logger);

    /**
     * Removes the logger from the ILogging.
     * @see StandardLogger2::getLogger()
     * @param logger The logger to be removed.
     * @returns true if the logger was found and removed; false if an error occurs.
     */
    bool(CARB_ABI* removeLogger)(Logger2* logger);
#endif

#if CARB_VERSION_ATLEAST(carb_logging_ILogging, 1, 4)
    /** @private */
    bool(CARB_ABI* internalModifyExtraFieldValue)(const char* key,
                                                  const char* value,
                                                  detail::ExtraFieldOperation op,
                                                  ExtraFieldFlags flags);

    /** Adds, removes, or modifies a specific extra field for logs.
     *
     *  @param[in] key      The key name of the extra field to operate on.  The specific operation
     *                      depends on the value in @p flags and @p value.  This may not be an
     *                      empty string or `nullptr`.  This key name should only contain
     *                      alphanumeric printable characters and should be as short as possible
     *                      while still being uniquely identifying.
     *  @param[in] value    The new value to set for the given extra field.  This may be `nullptr`
     *                      to remove the extra field with the given key name.
     *  @param[in] flags    Flags to control how this operation will proceed.  This may be any
     *                      combination of the @ref ExtraFieldFlags flags.
     *
     *  @returns `true` if the requested extra field is added or modified successfully.  Returns
     *           Returns `false` if adding or modifying the value of the extra field fails for
     *           any reason (ie: memory allocation, etc).
     *
     *  @remarks This allows an extra field to be added or modified.  Any time a log message
     *           is emitted, all of the extra fields that exist at the time for the emitting
     *           thread (global fields list plus the list for the calling thread).  The standard
     *           logger will add the extra field strings at the start of the log message text
     *           itself.  It will be passed to all log loggers (ie: `carb::logging::Logger2`)
     *           and log consumers (ie: `omni::log::ILogMessageConsumer2`).  Each global extra
     *           field will be surrounded by square brackets (ie: '[]'), with the format
     *           "[<key>:<value>]".  Thread specific extra fields will follow the same format
     *           except they will be surrounded with round brackets (ie: '()').  The ordering
     *           of the extra fields in the log output will be undefined, but the order will
     *           remain stable as long as no change to the extra fields list is made.
     *
     *  @note The thread-specific extra fields are not fiber aware and will therefore emit the
     *        extra fields belonging to the thread the fiber is running on instead of the fields
     *        added by the fiber itself.  This includes the fibers used for `carb.tasking` tasks
     *        and `omni.job` jobs.  If extra fields are needed from a task or job, they should be
     *        added inside the tasks function then removed before the task switches away or
     *        unschedules itself.
     */
    template <typename T>
    bool modifyExtraFieldValue(const char* key, T value, ExtraFieldFlags flags = fExtraFieldFlagNone)
    {
        return internalModifyExtraFieldValue(
            key, std::to_string(value).c_str(), detail::ExtraFieldOperation::eCreateOrModify, flags);
    }

    /** Adds an extra field key/value pair.
     *
     *  @param[in] key      The key name of the extra field to add.  The @p flags parameter
     *                      controls which list (global or per-thread) this new extra field is
     *                      is added to.  This may not be an empty string or `nullptr`.  This
     *                      key name should only contain alphanumeric printable characters and
     *                      should be as short as possible while still being uniquely identifying.
     *  @param[in] value    The new value to set for the given extra field.  This may not be
     *                      `nullptr`.
     *  @param[in] flags    Flags to control which extra fields list will be added to.  This may
     *                      be either @ref fExtraFieldFlagGlobal or @ref fExtraFieldFlagThread.
     *  @returns `true` if the new value is sucessfully added.  Returns `false` otherwise.
     */
    template <typename T>
    bool addExtraField(const char* key, T value, ExtraFieldFlags flags = fExtraFieldFlagNone)
    {
        return modifyExtraFieldValue(key, value, flags);
    }

    /** Removes an extra field based on its key name.
     *
     *  @param[in] key      The key name of the extra field to remove.  The @p flags parameter
     *                      controls which list (global or per-thread) this extra field will be
     *                      removed from.  This may not be an empty string or `nullptr`.  This
     *                      key name should only contain alphanumeric printable characters and
     *                      should be as short as possible while still being uniquely identifying.
     *  @param[in] flags    Flags to control which extra fields list this key should be removed
     *                      from.  This may be either @ref fExtraFieldFlagGlobal or
     *                      @ref fExtraFieldFlagThread.
     *  @returns `true` if the specified key/value pair was successfully removed from the
     *           requested list.  Returns `false` if the key was not found in the specified list.
     */
    bool removeExtraField(const char* key, ExtraFieldFlags flags = fExtraFieldFlagNone)
    {
        return internalModifyExtraFieldValue(key, nullptr, detail::ExtraFieldOperation::eDelete, flags);
    }

    /** Tests whether a given extra field exists.
     *
     *  @param[in] key      The key name of the extra field to check if it exists in the given
     *                      list.  This may not be an empty string or `nullptr`.
     *  @param[in] flags    Flags specifying which list the named extra field is expected to be
     *                      tested as being in.  This should be either @ref fExtraFieldFlagGlobal
     *                      or @ref fExtraFieldFlagThread.
     *  @returns `true` if the named extra field currently exists in the requested list.  Returns
     *           `false` if the named extra field does not exist yet.
     */
    bool hasExtraField(const char* key, ExtraFieldFlags flags = fExtraFieldFlagNone)
    {
        return internalModifyExtraFieldValue(key, nullptr, detail::ExtraFieldOperation::eExists, flags);
    }
#endif
};

#if CARB_VERSION_ATLEAST(carb_logging_ILogging, 1, 4)
/** @copydoc ILogging::modifyExtraFieldValue */
template <>
inline bool ILogging::modifyExtraFieldValue(const char* key, const char* value, ExtraFieldFlags flags)
{
    return internalModifyExtraFieldValue(key, value, detail::ExtraFieldOperation::eCreateOrModify, flags);
}

/** @copydoc ILogging::modifyExtraFieldValue */
template <>
inline bool ILogging::modifyExtraFieldValue(const char* key, std::nullptr_t value, ExtraFieldFlags flags)
{
    return internalModifyExtraFieldValue(key, value, detail::ExtraFieldOperation::eCreateOrModify, flags);
}

/** @copydoc ILogging::addExtraField */
template <>
inline bool ILogging::addExtraField(const char* key, const char* value, ExtraFieldFlags flags)
{
    CARB_ASSERT(value != nullptr);
    return internalModifyExtraFieldValue(key, value, detail::ExtraFieldOperation::eCreateOrModify, flags);
}
#endif

CARB_IGNOREWARNING_CLANG_POP
} // namespace logging
} // namespace carb
