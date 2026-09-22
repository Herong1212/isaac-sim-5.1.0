// SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
/** @file
 *  @brief An interface for redirecting @ref omni::log::ILog messages to structured logging.
 */
#pragma once

#include <omni/structuredlog/IStructuredLog.h>
#include <omni/structuredlog/IStructuredLogFromILog.h>

namespace omni
{
namespace structuredlog
{

class IStructuredLogFromILog2;


// ****************************** IStructuredLogFromILog2 interface *******************************
/** This extends the functionality of the @ref omni::structuredlog::IStructuredLogFromILog
 *  interface.  This allows for the event flags of the log consumer event to be modified.  This
 *  is an internal interface however and is not intended to be used externally.
 */
class IStructuredLogFromILog2_abi
    : public omni::core::Inherits<omni::structuredlog::IStructuredLogFromILog_abi,
                                  OMNI_TYPE_ID("omni.structuredlog.IStructuredLogFromILog2")>
{
protected:
    /** Modifies the flags for the log consumer event.
     *
     *  @param[in] setFlags     The set of flags to add to the log consumer event.
     *
     *  @param[in] clearFlags   The set of flags to remove from the log consumer event.  These
     *                          flags will be cleared before the flags from @p setFlags are
     *                          added.
     *
     *  @returns `true` if the log consumer event's flags were successfully modified.  Returns
     *           `false` if the log consumer event or schema is not present or did not get loaded.
     */
    virtual bool setLoggingEventFlags_abi(EventFlags setFlags, EventFlags clearFlags) noexcept = 0;

    /** Retrieves the current log filtering level.
     *
     *  @returns The current log filtering level for the log consumer.  This defaults to 'verbose'
     *           level log messages and therefore allows through all messages that make it to the
     *           log consumer.  This can be changed to further filter log messages based on level
     *           using omni::structuredlog::IStructuredLogFromILog2::setLogLevel().
     */
    virtual int32_t getLogLevel_abi() noexcept = 0;

    /** Sets the current log filtering level.
     *
     *  @param[in] level    The new logging level to filter at.  Any log messages that arrive at
     *                      or above this level will be allowed through.  Any log messages below
     *                      this level will be filtered out.
     *  @returns No return value.
     *
     *  @remarks This sets the new log filtering level.  This can be used to have an additional
     *           control over filtering which log messages get through from the log consumer.
     *           This defaults to 'verbose' level log messages and allows all messages through
     *           the filter.  This is useful for example if the main logger should allow 'info'
     *           level messages through to the log file, but should only allow 'warn' level
     *           messages through to stdout.
     */
    virtual void setLogLevel_abi(int32_t level) noexcept = 0;
};

} // namespace structuredlog
} // namespace omni

#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include "IStructuredLogFromILog2.gen.h"

/** @copydoc omni::structuredlog::IStructuredLogFromILog2_abi */
class omni::structuredlog::IStructuredLogFromILog2
    : public omni::core::Generated<omni::structuredlog::IStructuredLogFromILog2_abi>
{
};

#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include "IStructuredLogFromILog2.gen.h"
