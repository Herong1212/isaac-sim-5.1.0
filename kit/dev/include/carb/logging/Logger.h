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
//! @brief carb.logging Logger definition
#pragma once

#include "../Defines.h"

#include "ILogging.h"
#include "../thread/Types.h"

#include <cstdint>

namespace carb
{
//! Namespace for logging interfaces and utilities
namespace logging
{

#if CARB_VERSION_ATLEAST(carb_logging_ILogging, 1, 3) || defined(OMNI_BIND)
/**
 * A structure defining a log message as passed to Logger2::handleMessage().
 *
 * @see Logger2::handleMessage
 */
struct LogMessage
{
    //! The size of the `LogMessage` structure, used as a version.
    //!
    //! To verify if a desired field is included, do this check:
    //! `msg.sizeOf >= (offsetof(LogMessage, <field>) + sizeof(LogMessage::<field>))`
    //! @warning Only access fields that fit fully within the `sizeOf`! Fields up to and including `message` are always
    //!   valid.
    size_t sizeOf{ sizeof(LogMessage) };

    //! The source of the log message in UTF-8 encoding. Commonly this is the plugin name that generated the message,
    //! or the channel name. Will not be NULL.
    const char* source;

    //! The source code file name that generated the log message. May be NULL if not available.
    const char* fileName;

    //! The line number in `fileName` where the log message was generated from. Will be 0 if not available.
    int lineNumber;

    //! The log severity level of the message.
    //! @see loglevel
    int32_t level;

    //! The name of the module which generated the log message. May be NULL if not available.
    const char* moduleName;

    //! The name of the function which generated the log message. May be NULL if not available.
    const char* functionName;

    //! The process ID that generated the log message.
    process::ProcessId processId;

    //! The thread ID that generated the log message.
    thread::ThreadId threadId;

    //! The current traceparent ID for the thread that generated the message, or an empty string if no trace is active
    //! on the calling thread or \a OmniTrace is not enabled. Will not be NULL.
    const char* traceParentId;

    //! The log timestamp in nanoseconds based on std::chrono::steady_clock.
    uint64_t timestampNs;

    //! The log message in UTF-8 encoding. Will not be NULL.
    const char* message;

    //! A string containing the current global extra fields for this log message.  This may be
    //! an empty string if no extra fields have been specified.
    //!
    //! @warning This field must be checked if it is safe to access in the passed version of a
    //!          log message struct using a call to
    //!          `CARB_INCLUDES_MEMBER(msg.sizeOf, carb::logging::LogMessage::globalExtraFields)`
    //!          before attempting to access this member.
    const char* globalExtraFields;

    //! A string containing the current thread extra fields for this log message.  This may be
    //! an empty string if no thread specific extra fields have been specified.
    //!
    //! @warning This field must be checked if it is safe to access in the passed version of a
    //!          log message struct using a call to
    //!          `CARB_INCLUDES_MEMBER(msg.sizeOf, carb::logging::LogMessage::threadExtraFields)`
    //!          before attempting to access this member.
    const char* threadExtraFields;

    // Additional fields must be added here; no fields may be removed!
};
// These ABI parameters are guaranteed
static_assert(sizeof(LogMessage) >= 80 && alignof(LogMessage) == sizeof(size_t));
static_assert(offsetof(LogMessage, sizeOf) == 0);
static_assert(offsetof(LogMessage, source) == 8);
static_assert(offsetof(LogMessage, fileName) == 16);
static_assert(offsetof(LogMessage, lineNumber) == 24);
static_assert(offsetof(LogMessage, level) == 28);
static_assert(offsetof(LogMessage, moduleName) == 32);
static_assert(offsetof(LogMessage, functionName) == 40);
static_assert(offsetof(LogMessage, processId) == 48);
static_assert(offsetof(LogMessage, threadId) == 52);
static_assert(offsetof(LogMessage, traceParentId) == 56);
static_assert(offsetof(LogMessage, timestampNs) == 64);
static_assert(offsetof(LogMessage, message) == 72);
static_assert(offsetof(LogMessage, globalExtraFields) == 80);
static_assert(offsetof(LogMessage, threadExtraFields) == 88);

/**
 * Defines a registerable callback interface to receive notification of every log message.
 * @see ILogging::addLogger ILogging::removeLogger
 */
struct Logger2
{
    /**
     * Called to notify of a log message.
     *
     * This function is called by @ref ILogging if `*this` has been registered via @ref ILogging::addLogger(), the log
     * level passes the threshold (for module or globally if not set for modules), and logging is enabled (for module or
     * globally if not set for module).
     *
     * @note The framework protects against recursively calling `*this` in the event that `handleMessage` causes a log
     * message to be recursively emitted. In these situations, `*this` will not receive the recursive log message, but
     * other `Logger2` instances will receive it.
     *
     * @note In some cases such as internal locks being held, log messages are deferred by the Framework in order to
     * prevent `Logger2` instances from calling back into the Framework when unsafe operations could be performed.
     *
     * @warning The \p message has a `sizeOf` parameter that must be checked to ensure safe access to fields.
     * @thread_safety this function can be called simultaneously by multiple threads. The thread that calls this
     *   function is not necessarily the thread that emitted the log message, such as when asynchronous logging is
     *   enabled.
     * @param message The \ref LogMessage structure containing information about the emitted log.
     */
    virtual void handleMessage(const LogMessage& message) = 0;
};
#else // Leave these types opaque
struct LogMessage;
struct Logger2;
#endif

//! @private
struct Logger
{
    //! @private
    void(CARB_ABI* handleMessage)(Logger* logger,
                                  const char* source,
                                  int32_t level,
                                  const char* fileName,
                                  const char* functionName,
                                  int lineNumber,
                                  const char* message);

    // NOTE: This interface, because it is inherited from, is CLOSED and may not have any additional functions added
    // without an ILogging major version increase.
};

} // namespace logging
} // namespace carb
