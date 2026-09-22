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
 *  @brief The structured log control interface.
 */
#pragma once

#include "StructuredLogCommon.h"
#include "IStructuredLogControl.h"

#include "../core/IObject.h"


namespace omni
{
namespace structuredlog
{

class IStructuredLogControl2;

// ****************************** IStructuredLogControl2 interface ********************************
/** Interface for the second version of the IStructuredLogControl interface.  This interface
 *  exposes more functions to control the behavior of the structured logging system.  This
 *  object can be retrieved directly or by casting the main IStructuredLog interface to this
 *  type using `omni::core::ObjectPtr::as<>()`.
 */
class IStructuredLogControl2_abi : public omni::core::Inherits<omni::structuredlog::IStructuredLogControl_abi,
                                                               OMNI_TYPE_ID("omni.structuredlog.IStructuredLogControl2")>
{
protected:
    /** Immediately emits the process lifetime exit event for the process.
     *
     *  @param[in] reason   The reason why the exit event is being emitted.  This can be any text
     *                      that gives and indication for why an exit is occurring.  This may not
     *                      be `nullptr` and should not be an empty string.
     *
     *  @returns No return value.
     *
     *  @remarks This forces the process lifetime exit event to be emitted early for the process.
     *           If this is called, it will pre-empt the normal attempt to emit it automatically
     *           when `omni.structuredlog.plugin` unloads.  This can be used to provide a
     *           different reason message for the exit event or to explicitly emit the event in
     *           situations where `omni.structuredlog.plugin` cannot be properly unloaded (ie:
     *           another system leaks or hangs onto a reference to one of the objects from the
     *           library).
     *
     *  @note This should only ever be called when a process shutdown is iminent and cannot be
     *        cancelled or avoided.  If this is emitted earlier in the process than exit time,
     *        the analysis of the process' duration could be incorrect.
     *
     *  @note Calling this will flush the structuredlog queue to ensure the event is flushed to disk
     *        before the process exits.
     */
    virtual void emitProcessLifetimeExitEvent_abi(OMNI_ATTR("c_str, in, not_null") const char* reason) noexcept = 0;
};

} // namespace structuredlog
} // namespace omni

#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include "IStructuredLogControl2.gen.h"

/** @copydoc omni::structuredlog::IStructuredLogControl2_abi */
class omni::structuredlog::IStructuredLogControl2
    : public omni::core::Generated<omni::structuredlog::IStructuredLogControl2_abi>
{
};

#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include "IStructuredLogControl2.gen.h"
