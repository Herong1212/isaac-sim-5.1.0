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
//! @brief carb.logging StandardLogger2 definitions
#pragma once

#include "LoggingTypes.h"
#include "ILogging.h"

namespace carb
{
namespace logging
{

struct Logger;
struct Logger2;
struct StandardLogger;


#if CARB_VERSION_ATLEAST(carb_logging_ILogging, 1, 2)

/** Base type for the flags that indicate which log destinations are currently active.  Each
 *  destination has its own criteria for when it is considered enabled.  See below for more
 *  information on each destination type.
 */
using LogDestinations = uint32_t;

/** Special value to indicate that no log destinations are currently enabled.  This is to be
 *  compared to a log destinations flag set as a whole instead of just a single flag.
 */
constexpr LogDestinations fLogDestinationNone = 0x00;

/** Flag to indicate that logging to the standard streams (ie: stdout and stderr) is enabled.
 *  This does not mean that all messages _will_ be written to this destination, but rather
 *  that they can be depending on the message's level and the currently configured logging
 *  level.  This flag gets toggled by the StandardLogger2::setStandardStreamOutput() function.
 */
constexpr LogDestinations fLogDestinationStandardStreams = 0x01;

/** Flag to indicate that logging to a file is currently enabled.  This does not mean that all
 *  messages _will_ be written to the file, but rather just that the file is currently open and
 *  will be used as a destination depending on the message's level and currently configured
 *  logging level.  This flag is toggled by functions such as StandardLogger2::setFileOutput()
 *  and StandardLogger2::setFileConfiguration().  Note that this can also be affected by
 *  functions such as StandardLogger2::pauseFileLogging() and StandardLogger2::resumeFileLogging()
 *  since they will close and open the output file.
 */
constexpr LogDestinations fLogDestinationLogFile = 0x02;

/** Flag to indicate that logging to the system specific debug console is enabled.  This is
 *  currently only supported on Windows through destinations such as MSVC's or VSCode's debug
 *  console, tools like 'dbgview' or 'WinDbg', or any other destination that can consume
 *  calls to @a OutputDebugString().  This flag is toggled by functions such as
 *  StandardLogger2::setDebugConsoleOutput().  On Windows, this flag is enabled by default
 *  since this implementation defaults to outputting to the debug console if a debugger is
 *  attached.  This may result in it being seen as an output destination even if no debugger
 *  is currently attached.
 */
constexpr LogDestinations fLogDestinationDebugConsole = 0x04;
#endif

#if CARB_VERSION_ATLEAST(carb_logging_ILogging, 1, 1)

/**
 * A sub-interface of \ref ILogging for \ref StandardLogger instances.
 */
class StandardLogger2
{
    // This class's ABI is versioned by the ILogging version.
public:
    /**
     * Adds a reference to *this.
     */
    virtual void addRef() = 0;

    /**
     * Releases a reference to *this. When the last reference is released, *this is destroyed.
     */
    virtual void release() = 0;

#    if CARB_VERSION_ATLEAST(carb_logging_ILogging, 1, 3)
    //! @private
    CARB_DEPRECATED("Use getLogger() instead") virtual Logger* getLoggerOld() = 0;
#    else
    /**
     * Retrieves access to the underlying \ref Logger for *this.
     * @see ILogging::addLogger() ILogging::removeLogger()
     * @returns the underlying \ref Logger.
     */
    virtual Logger* getLogger() = 0;
#    endif

    /**
     * Includes or excludes the filename of where the log message came from. A new instance
     * will by default exclude this information.
     *
     * @param included Whether the filename information should be included in the log message
     */
    virtual void setFilenameIncluded(bool included) = 0;

    /**
     * Includes or excludes the line number of where the log message came from. A new instance
     * will by default exclude this information.
     *
     * @param included Whether the line number information should be included in the log message
     */
    virtual void setLineNumberIncluded(bool included) = 0;

    /**
     * Includes or excludes the function name of where the log message came from. A new instance
     * will by default exclude this information.
     *
     * @param included Whether the function name information should be included in the log message
     */
    virtual void setFunctionNameIncluded(bool included) = 0;

    /**
     * Includes or excludes the timestamp of when the log message was issued. A new instance
     * will by default exclude this information. The time is in UTC format.
     *
     * @param included Whether the timestamp information should be included in the log message
     */
    virtual void setTimestampIncluded(bool included) = 0;

    /**
     * Includes or excludes the id of a thread from which the log message was issued. A new instance
     * will by default exclude this information.
     *
     * @param included Whether the thread id should be included in the log message
     */
    virtual void setThreadIdIncluded(bool included) = 0;

    /**
     * Includes or excludes the source (module) of where the log message came from. A new instance
     * will by default include this information.
     *
     * @param included Whether the source (module) information should be included in the log message
     */
    virtual void setSourceIncluded(bool included) = 0;

    /**
     * Enables (or disables) standard stream output (stdout and stderr) for the logger. Error messages are written
     * to stderr, all other messages to stdout. A new FrameworkLogger will have this output enabled.
     *
     * @param enabled Whether log output should go to standard streams (stdout and stderr)
     */
    virtual void setStandardStreamOutput(bool enabled) = 0;

    /**
     * (Windows only) Enables (or disables) debug console output for the logger via `OutputDebugStringW()`. By default,
     * debug output is only supplied if a debugger is attached (via `IsDebuggerPresent()`). Calling this with @p enabled
     * as `true` will always produce debug output which is useful for non-debugger tools such as SysInternals DebugView.
     *
     * @param enabled Whether log output should be sent to the debug console.
     */
    virtual void setDebugConsoleOutput(bool enabled) = 0;

    /** sets the path to the log file to open.
     *
     *  @param[in] filePath     the local file path to write the log file to.  This may be a
     *                          relative or absolute path.  Relative paths will be resolved
     *                          relative to the process's current working directory at the time
     *                          of the call.  This may be nullptr to not write to a log file at
     *                          all or to close the current log file.  If a log file was
     *                          previously open during this call, it will be closed first.  If
     *                          nullptr is passed in here, logging to a file will effectively
     *                          be disabled.  This path must be UTF-8 encoded.  See the remarks
     *                          below for more information on formatting of the log file path.
     *  @returns no return value.
     *
     *  @remarks This sets the path to the log file to write to for the given instance of a
     *           standard logger object.  The log file name may contain the string "${pid}" to
     *           have the process ID inserted in its place.  By default, a new standard logger
     *           will disable logging to a file.
     *
     *  @note Setting the log file name with this function will preserve the previous log file
     *        configuration.  If the configuration needs to changes as well (ie: change the
     *        'append' state of the log file), setFileConfiguration() should be used instead.
     */
    virtual void setFileOutput(const char* filePath) = 0;

    /**
     * Enables flushing on every log message to file specified severity or higher.
     * A new instance will have this set to flush starting from kLevelVerbose, so that file logging will be
     * reliable out of the box. The idea is that file logging will be used for debugging purposes by default, with a
     * price of significant performance penalty.
     *
     * @param level The starting log level to flush file log output at.
     */
    virtual void setFileOuputFlushLevel(int32_t level) = 0;

    /**
     * Enables flushing of stdout after each message is printed to it.
     * By default, this option will be disabled.  The default behavior will be to only flush stdout just before
     * writing a message to stderr.
     *
     * @param enabled Set to true to cause stdout to be flushed after each message is written.  Set to false to
     *        use the default behavior of only flushing stdout before writing to stderr.
     */
    virtual void setFlushStandardStreamOutput(bool enabled) = 0;

    /**
     *  Enables a high resolution time index to be printed with each message.
     *  By default, this option is disabled (ie: no time index printed).  When enabled, the current time index
     *  (since the first message was printed) will be printed with each message.  The time index may be in
     *  milliseconds, microseconds, or nanoseconds depending on the string @p units.  The printing of the time
     *  index may be enabled at the same time as the timestamp.
     *
     *  @param[in] units    the units that the time index should be printed in.  This can be one of the following
     *                      supported unit names:
     *      * nullptr, "", or "none": the time index printing is disabled (default state).
     *      * "ms", "milli", or "milliseconds": print the time index in milliseconds.
     *      * "us", "µs", "micro", or "microseconds": print the time index in microseconds.
     *      * "ns", "nano", or "nanoseconds": print the time index in nanoseconds.
     */
    virtual void setElapsedTimeUnits(const char* units) = 0;

    /**
     * Includes or excludes the id of the process from which the log message was issued. A new instance
     * will by default exclude this information.
     *
     * @param enabled Whether the process id should be included in the log message
     */
    virtual void setProcessIdIncluded(bool enabled) = 0;

    /**
     *  sets the process group ID for the logger.  If a non-zero identifier is given, inter-process
     *  locking will be enabled on both the log file and the stdout/stderr streams.  This will prevent
     *  simultaneous messages from multiple processes in the logs from becoming interleaved within
     *  each other.  If a zero identifier is given, inter-process locking will be disabled.
     *
     *  @param[in] id       an arbitrary process group identifier to set.
     */
    virtual void setMultiProcessGroupId(int32_t id) = 0;

    /**
     * Enables (or disables) color codes output for the logger. A new instance will have this output enabled
     * unless the output is piped to a file, in which case this will be disabled.
     *
     * @param enabled Whether log output should include color codes
     */
    virtual void setColorOutputIncluded(bool enabled) = 0;

    /**
     * Specify the output stream that logging should go to.
     * By default, messages are sent to stdout and errors are sent to stderr.
     *
     *  @param[in] outputStream The output stream setting to use.
     *                          If this is OutputStream::eStderr, all logging
     *                          output will be sent to stderr.
     *                          If this is OutputStream::eDefault, the default
     *                          logging behavior will be used.
     */
    virtual void setOutputStream(OutputStream outputStream) = 0;

    /**
     * Sets the log level threshold for the messages going to the standard stream. Messages below this threshold will be
     * dropped.
     *
     * @param level The log level to set.
     */
    virtual void setStandardStreamOutputLevelThreshold(int32_t level) = 0;

    /**
     * Sets the log level threshold for the messages going to the debug console output. Messages below this threshold
     * will be dropped.
     *
     * @param level The log level to set.
     */
    virtual void setDebugConsoleOutputLevelThreshold(int32_t level) = 0;

    /**
     * Sets the log level threshold for the messages going to the file output. Messages below this threshold
     * will be dropped.
     *
     * @param level The log level to set.
     */
    virtual void setFileOutputLevelThreshold(int32_t level) = 0;

    /**
     * Sets the file path and configuration for file logging. If nullptr is provided the file logging is disabled. A new
     * instance will by default disable file output.
     *
     * @param filePath The local file path to write to or nullptr, if you want to disable logging to file.
     *  Parameter is encoded as UTF8 character string with forward slashes as path separator. The path
     *  should include the extension .log but this is not a requirement. If a relative path is provided
     *  it is interpreted to be relative to the current working directory for the application. Can be kKeepSameFile to
     *  keep logging to the same file but set a new LogFileConfiguration.
     * @param config The LogFileConfiguration structure with parameters to use for the file configuration. Required.
     */
    virtual void setFileConfiguration(const char* filePath, const LogFileConfiguration* config) = 0;

    /**
     * Returns the file path (in buffer) and configuration for file logging.
     *
     * @param buffer The buffer that will receive the UTF-8 file name that is being logged to. May be nullptr.
     * @param bufferSize The maximum number of bytes available in \p buffer.
     * @param config The LogFileConfiguration to receive the current configuration. May be nullptr.
     * @returns If successful, the number of non-NUL bytes written to \p buffer. If not successful, contains the
     * required size of a buffer to receive the filename (not including the NUL terminator).
     */
    virtual size_t getFileConfiguration(char* buffer, size_t bufferSize, LogFileConfiguration* config) = 0;

    /**
     * Pauses file logging (and closes the file) until resumeFileLogging() is called.
     *
     * @note This is a counted call. Each call to pauseFileLogging() must have a matching call to resumeFileLogging()
     *
     */
    virtual void pauseFileLogging() = 0;

    /**
     * Resumes file logging (potentially reopening the file)
     *
     * @note This is a counted call. Each call to pauseFileLogging() must have a matching call to resumeFileLogging()
     *
     */
    virtual void resumeFileLogging() = 0;

    /**
     * Forces the logger to use ANSI escape code's to annotate the log with color.
     *
     * By default, on Windows ANSI escape codes will never be used, rather the Console API will be used to place
     * colors in a console. Linux uses the isatty() to determine if the terminal supports ANSI escape codes. However,
     * the isatty check doesn't work in all cases. One notable case where this doesn't work is running a process in a
     * CI/CD that returns false from isatty() yet still supports ANSI escape codes.
     *
     * See: https://en.wikipedia.org/wiki/ANSI_escape_code for more information about ANSI escape codes.
     *
     * @param forceAnsiColor if true forces terminal to use ANSI escape codes for color
     */
    virtual void setForceAnsiColor(bool forceAnsiColor) = 0;

    /**
     * Overrides the current log level, for the given stream, only for the calling thread.
     *
     * Call \ref clearLevelThresholdThreadOverride() to clear the override.
     * @param type The \ref OutputType to override.
     * @param level The \ref loglevel to use for override.
     */
    virtual void setLevelThresholdThreadOverride(OutputType type, int32_t level) = 0;

    /**
     * Clears any override for the given stream, only for the calling thread.
     *
     * The override was previously set with \ref setLevelThresholdThreadOverride().
     * @param type The \ref OutputType to override.
     */
    virtual void clearLevelThresholdThreadOverride(OutputType type) = 0;

#    if CARB_VERSION_ATLEAST(carb_logging_ILogging, 1, 2)
    /**
     * Retrieves the current set of log destinations for this logger.
     *
     * @param[in] level The logging level to check each destination against.  This can be one of
     *                  the standard `kLevel*` values.  Each log destination that is currently
     *                  enabled will only set its corresponding flag if the given log level is
     *                  at or above the currently configured level for the same destination on
     *                  the calling thread.
     *
     * @returns A set of flags indicating which log destinations are currently enabled for the
     *          given log level.  Note that each destination can be affected by the configured
     *          logging level for the calling module and thread.  Also note that since this
     *          check is performed separately from emitting any particular log message, there
     *          is a potential race between outputting a message then checking the destinations
     *          versus another thread changing the logger's configuration.  The returned values
     *          are more for informational purposes as a result.
     */
    virtual LogDestinations getConfiguredLogDestinationsForLevel(int32_t level) = 0;
#    endif

#    if CARB_VERSION_ATLEAST(carb_logging_ILogging, 1, 3)
    /**
     * Sets whether the emitting thread's current traceparent ID will also be included in logs.
     *
     *  @param[in] state    The new state of whether the traceparent ID should be included in
     *                      each new log message.  If `true`, the traceparent ID (if any) will
     *                      be included with each message.  If no traceparent ID is currently
     *                      set, no extra value will be emitted.  If `false`, no extra value
     *                      will be emitted even if a traceparent ID is active on the calling
     *                      thread.
     */
    virtual void setTraceIdIncluded(bool state) = 0;

    /**
     * Retrieves access to the underlying \ref Logger2 for *this.
     * @see ILogging::addLogger() ILogging::removeLogger()
     * @returns the underlying \ref Logger2.
     */
    virtual Logger2* getLogger() = 0;
    // FIXME!! should we also be exposing 'get' functions for each of the various logger settings?
#    endif

#    if CARB_VERSION_ATLEAST(carb_logging_ILogging, 1, 5)
    /**
     * Sets whether timestamps in log messages should be in UTC or local time.
     *
     * @param[in] utc  If `true`, timestamps will be in UTC time. If `false`, timestamps
     *                 will be in the local system time zone.
     */
    virtual void setUtcTimestamps(bool utc) = 0;

    /**
     * Sets whether timestamps in log messages should include microsecond precision.
     *
     * @param[in] enabled  If `true`, timestamps will include microsecond precision. If `false`, timestamps
     *                     will only include millisecond precision.
     */
    virtual void setMicrosecondTimestamp(bool enabled) = 0;
#    endif


    // Functions may be added to this class as long as it is not inherited from (as an interface) and ILogging's minor
    // version is incremented.
};

#endif

} // namespace logging
} // namespace carb
