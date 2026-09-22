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
 *  @brief Interface to querying and adjusting structured logging settings.
 */
#pragma once

#include "StructuredLogCommon.h"
#include "IStructuredLogSettings2.h"

#include "../core/IObject.h"


namespace omni
{
namespace structuredlog
{

class IStructuredLogSettings3;

/** The tag that is applied to structuredlog messages. */
enum class TelemetryMode
{
    /** Production mode. No tag is added to messages. */
    eProduction,

    /** Developer mode. A `(dev)` tag is added to the source of messages. */
    eDev,

    /** Test mode. A `(test)` tag is added to the source of messages. */
    eTest,
};

// ****************************** IStructuredLogSettings3 interface *******************************
/** Interface for the third version of the IStructuredLogSettings interface.  This interface
 *  exposes more settings to control the behaviour of the structured logging system.  This
 *  object can be retrieved directly or by casting the main IStructuredLog interface to this
 *  type using `omni::core::ObjectPtr::as<>()`.
 */
class IStructuredLogSettings3_abi
    : public omni::core::Inherits<omni::structuredlog::IStructuredLogSettings2_abi,
                                  OMNI_TYPE_ID("omni.structuredlog.IStructuredLogSettings3")>
{
protected:
    /** This function specifies which tag is added to the source of structured log messages.
     *  @param mode The tagging mode to apply to telemetry messages.
     *
     *  @remarks This behaves the same as @ref telemetry::kTelemetryModeSetting and @ref
     *           telemetry::kTelemetryTagSetting with respect to the message source tagging.
     *           This does not apply any of the other behaviors of @ref telemetry::kTelemetryModeSetting.
     */
    virtual void setMessageSourceTag_abi(TelemetryMode mode) noexcept = 0;

    /** This function informs the structured log system that the settings registry is fully loaded.
     *
     *  @remarks Because omni.structuredlog loads very early in the process, it is typically loaded
     *           before `ISettings`, so it needs to be explicitly told when it's safe to start
     *           reading from the settings registry.
     *           This function will flag this internally and may also read some settings from the
     *           registry.
     */
    virtual void settingsLoadComplete_abi() noexcept = 0;
};

} // namespace structuredlog
} // namespace omni

#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include "IStructuredLogSettings3.gen.h"

// insert custom API functions here.
/** @copydoc omni::structuredlog::IStructuredLogSettings3_abi */
class omni::structuredlog::IStructuredLogSettings3
    : public omni::core::Generated<omni::structuredlog::IStructuredLogSettings3_abi>
{
};

#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include "IStructuredLogSettings3.gen.h"
