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
 *  @brief Interface to manage extra CloudEvent fields in all structured log messages.
 */
#pragma once

#include "StructuredLogCommon.h"

#include "../core/IObject.h"

#include <omni/String.h>


namespace omni
{
namespace structuredlog
{

class IStructuredLogExtraFields;

/** Base type for flags that control how extra field flags are specified or retrieved in
 *  omni::structuredlog::IStructuredLogExtraFields::getExtraCloudEventField() and
 *  omni::structuredlog::IStructuredLogExtraFields::setExtraCloudEventField().
 */
using ExtraFieldFlags = uint32_t;

/** Value to indicate that no special flags are being specified. */
constexpr ExtraFieldFlags fExtraFieldFlagNone = 0;


// ***************************** IStructuredLogExtraFields interface ******************************
/** Interface to manage extra CloudEvent fields to be included in each emitted message.  This
 *  allows for fields to be added and removed as needed.  It also allows existing registered
 *  fields to be enumerated at any given time.  An extra field is a key/value pair that is
 *  included at the top level of the JSON object for each message that follows.  Only string
 *  values are allowed for each key.
 */
class IStructuredLogExtraFields_abi
    : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("omni.structuredlog.IStructuredLogExtraFields")>
{
protected:
    /** Adds, modifies, or removes an extra field key/value pair.
     *
     *  @param[in] fieldName    The name of the field to add, modify or remove.  This may not be
     *                          `nullptr` or and empty string.  The field name must only contain
     *                          alphabetic, numeric, or underscore ASCII characters.  Any
     *                          characters outside these will cause the field to not be updated.
     *                          Further, this may not be one of the reserved CloudEvent field
     *                          names such as "specversion", "data", "time", "source", "session",
     *                          "dataschema", "type", or "subject".
     *  @param[in] value        The new value to set for the requested extra field.  This may be
     *                          `nullptr` to indicate that the named field should be removed.
     *                          The value string may include any characters, but should be limited
     *                          to a small number of characters (ideally less than 64 characters).
     *  @param[in] flags        Flags to control how the new value is added, modified, or removed.
     *                          Currently no flags are defined.  This must be set to
     *                          @ref omni::structuredlog::fExtraFieldFlagNone.
     *  @returns `true` if the requested extra field is successfully added, modified, or removed.
     *           Returns `false` if an invalid field name is given, or the operation could not
     *           be completed for any reason.
     *
     *  @remarks This adds, modifies, or removes a registered extra field and value.  Any extra
     *           fields that are registered at the time a message is emitted will be added to the
     *           message on output.  At least for the first version of this interface it is
     *           expected that extra fields be largely static.
     *
     *  @thread_safety This call is thread safe.
     */
    virtual bool setValue_abi(OMNI_ATTR("c_str, in, not_null") const char* fieldName,
                              OMNI_ATTR("c_str, in, not_null") const char* value,
                              ExtraFieldFlags flags) noexcept = 0;
};

} // namespace structuredlog
} // namespace omni

#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include "IStructuredLogExtraFields.gen.h"

// insert custom API functions here.
/** @copydoc omni::structuredlog::IStructuredLogExtraFields_abi */
class omni::structuredlog::IStructuredLogExtraFields
    : public omni::core::Generated<omni::structuredlog::IStructuredLogExtraFields_abi>
{
};

#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include "IStructuredLogExtraFields.gen.h"
