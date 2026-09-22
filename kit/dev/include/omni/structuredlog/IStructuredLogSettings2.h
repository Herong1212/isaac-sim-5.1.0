// SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
/** @file
 *  @brief Interface to querying and adjusting structured logging settings.
 */
#pragma once

#include "StructuredLogCommon.h"
#include "IStructuredLogSettings.h"

#include "../core/IObject.h"


namespace omni
{
namespace structuredlog
{

class IStructuredLogSettings2;

/** Base type for the ouptut flags for the structured logging system.  These flags are used
 *  in the omni::structuredlog::IStructuredLogSettings2::getOutputFlags() and
 *  omni::structuredlog::IStructuredLogSEttings2::setOutputFlags() functions.
 */
using OutputFlags = uint32_t;

/** Special flag value to indicate that no output flags are being specified. */
constexpr OutputFlags fOutputFlagNone = 0;

/** Flag to indicate that only emit the payload portion of each message as the full output instead
 *  of including the CloudEvents wrapper as well.  In this case, it is expected to be the host
 *  app's responsibility to ensure all the useful or required information is included in the
 *  payload itself (ie: timestamps, user information, etc).  Also, when this flag is used, log
 *  files created containing these messages cannot be consumed by the telemetry transmitter.
 *  This flag should only be used when the host app wants to use structured logging messages
 *  but does not want to use them as part of the telemetry toolchain.  This flag is off by
 *  default.  Adding this flag will take effect the next time a message is emitted.
 */
constexpr OutputFlags fOutputFlagPayloadOnly = 0x00000001;

/** Flag to indicate that no header should be written out to log files created by the structured
 *  logging system.  The header is consumed and modified by the telemetry transmitter app to allow
 *  it to store its progress in processing each log file.  If the header is missing, the
 *  transmitter app will simply ignore the log file.  Omitting the headers in log files allows the
 *  log output to purely just be the structured log event messages so they can be more easily
 *  consumed wholesale by external apps.  Note that when this flag is used, the structured log
 *  files created by the host app will be incompatible with the rest of the telemetry toolchain
 *  in Omniverse.  This flag is off by default.  Adding this flag will take effect the next time
 *  a new log file is created.
 */
constexpr OutputFlags fOutputFlagSkipLogHeaders = 0x00000002;

/** Flag to indicate that the cloud heartbeat events should be emitted as well as the normal
 *  heartbeat events.  This cloud heartbeat event is effectively duplciate data and will only
 *  be emitted when this flag is used and the normal heartbeat events are also enabled.  This
 *  defaults to off.
 */
constexpr OutputFlags fOutputFlagEmitCloudHeartbeat = 0x00000004;


// ****************************** IStructuredLogSettings2 interface *******************************
/** Interface for the second version of the IStructuredLogSettings interface.  This interface
 *  exposes more settings to control the behaviour of the structured logging system.  This
 *  object can be retrieved directly or by casting the main IStructuredLog interface to this
 *  type using `omni::core::ObjectPtr::as<>()`.
 */
class IStructuredLogSettings2_abi
    : public omni::core::Inherits<omni::structuredlog::IStructuredLogSettings_abi,
                                  OMNI_TYPE_ID("omni.structuredlog.IStructuredLogSettings2")>
{
protected:
    /** Retrieves the current heartbeat message period in seconds.
     *
     *  @returns The minimum time in seconds between heartbeat events.  This will be
     *           @ref omni::structuredlog::kHeartbeatDisabled if the heartbeat events are
     *           disabled.  When enabled, the heartbeat events will be generated within
     *           ~100ms of this scheduled time.  In general, it is expected that the heartbeat
     *           period be on the scale of one minute or more to reduce the overall amount of
     *           event traffic.
     */
    virtual uint64_t getHeartbeatPeriod_abi() noexcept = 0;

    /** Sets the new heartbeat event period in seconds.
     *
     *  @param[in] period   The minimum time in seconds between generated heartbeat events.
     *                      This may be @ref omni::structuredlog::kHeartbeatDisabled to disable
     *                      the heartbeat events.
     *  @returns No return value.
     *
     *  @remarks The heartbeat events can be used to get an estimate of a session's length even if
     *           the 'exit' or 'crash' process lifetime events are missing (ie: power loss, user
     *           kills the process, blue screen of death or kernel panic, etc).  The session can
     *           neither be assumed to have exited normally nor crashed with only these heartbeat
     *           events present however.
     */
    virtual void setHeartbeatPeriod_abi(uint64_t period) noexcept = 0;

    /** Retrieves whether header objects will be added to each newly written log file.
     *
     *  @returns `true` if headers will be written to each new log file.  Returns `false` if
     *           header objects will be omitted from new log files.
     */
    virtual bool getNeedLogHeaders_abi() noexcept = 0;

    /** Sets whether headers will be added to each newly written log file.
     *
     *  @param[in] needHeaders  Set to `true` to indicate that headers should be added to each
     *                          newly written log file.  Set to `false` to indicate that the
     *                          header should be omitted.
     *  @returns No return value.
     *
     *  @remarks This sets whether log headers will be written out to each new log file.  The
     *           header is consumed and modified by the telemetry transmitter app to allow it
     *           to store its progress in processing each log file.  If the header is missing,
     *           the transmitter app will simply ignore the log file.  Omitting the headers
     *           in log files allows the log output to purely just be the structured log event
     *           messages so they can be more easily consumed wholesale by external apps.
     *
     *  @note Changing this setting will only take effect the next time a new log file is written
     *        out to disk.  Disabling this will not remove the header object from an existing log
     *        file.
     */
    virtual void setNeedLogHeaders_abi(bool needHeaders) noexcept = 0;

    /** Retrieves the current set of output flags for structured logging.
     *
     *  @returns The current output flags for the structured logging system.  These indicate how
     *           various aspects of the logging system will function.  Note that some flags may
     *           affect whether the produced messages are compatible with the remainder of the
     *           telemetry toolchain in Omniverse apps.  By default, all output flags are off.
     */
    virtual OutputFlags getOutputFlags_abi() noexcept = 0;

    /** Sets or clears one or more output flags for structured logging.
     *
     *  @param[in] flagsToAdd       A set of zero or more flag bits to set.  These must be either
     *                              @ref omni::structuredlog::fOutputFlagNone or one or more of
     *                              the @ref omni::structuredlog::OutputFlags flags.
     *
     *  @param[in] flagsToRemove    A set of zero or more flag bits to cleared.  These must be
     *                              either @ref omni::structuredlog::fOutputFlagNone or one or
     *                              more of the @ref omni::structuredlog::OutputFlags flags.
     *
     *  @returns No return value.
     *
     *  @remarks This sets or clears flags that affect the output from the structured logging
     *           system.  These flags are all disabled by default.  These flags will take effect
     *           the next time a message is emitted.
     */
    virtual void setOutputFlags_abi(OutputFlags flagsToAdd, OutputFlags flagsToRemove) noexcept = 0;
};

} // namespace structuredlog
} // namespace omni

#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include "IStructuredLogSettings2.gen.h"

// insert custom API functions here.
/** @copydoc omni::structuredlog::IStructuredLogSettings2_abi */
class omni::structuredlog::IStructuredLogSettings2
    : public omni::core::Generated<omni::structuredlog::IStructuredLogSettings2_abi>
{
};

#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include "IStructuredLogSettings2.gen.h"
