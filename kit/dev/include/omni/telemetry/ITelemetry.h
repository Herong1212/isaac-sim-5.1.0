// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
/// @file
/// @brief Provides a helper interface to allow access to some common telemetry operations.
#pragma once

#include <omni/core/Omni.h>
#include <omni/core/OmniAttr.h>
#include <omni/core/IObject.h>


namespace omni
{
/** Namespace for telemetry related interfaces and functionality. */
namespace telemetry
{

/** Forward declaration of the ITelemetry interface implementation class. */
class ITelemetry;

/** Interface to handle performing telemetry related tasks.
 *
 *  This provides an abstraction over the lower level telemetry and structured logging systems
 *  and allows control over some common features of it.
 */
class ITelemetry_abi : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("omni.kit.telemetry.ITelemetry")>
{
protected:
    /** Sends a generic structured log event with caller specified data.
     *
     *  @param[in] eventType    A string describing the event that occurred.  There is no
     *                          restriction on the content or formatting of this value.
     *                          This should neither be `nullptr` nor an empty string.
     *  @param[in] duration     A generic duration value that can be optionally included
     *                          with the event.  It is the caller's respsonsibility to
     *                          decide on the usage and semantics of this value depending
     *                          on the @p eventType value.  This may be 0.0 if no duration
     *                          value is needed for the event.
     *  @param[in] data1        A string data value to be sent with the event.  The contents
     *                          and interpretation of this string depend on the @p eventTyoe
     *                          value.
     *  @param[in] data2        A string data value to be sent with the event.  The contents
     *                          and interpretation of this string depend on the @p eventTyoe
     *                          value.
     *  @param[in] value1       A floating point value to be sent with the event.  This value
     *                          will be interpreted according to the @p eventType value.
     *  @param[in] value2       A floating point value to be sent with the event.  This value
     *                          will be interpreted according to the @p eventType value.
     *
     *  @returns No return value.
     *
     *  @remarks This sends a generic event to the structured logging log file.  The contents,
     *           semantics, and interpretation of this event are left entirely up to the caller.
     *           This will be a no-op if telemetry is disabled (ie: the telemetry module either
     *           intentionally was not loaded or failed to load).
     */
    virtual void sendGenericEvent_abi(OMNI_ATTR("c_str, in") const char* eventType, double duration, OMNI_ATTR("c_str, in") const char* data1, OMNI_ATTR("c_str, in") const char* data2, double value1, double value2) noexcept = 0;
};

} // namespace telemetry
} // namespace omni

#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include "ITelemetry.gen.h"

/** @copydoc omni::telemetry::ITelemetry_abi */
class omni::telemetry::ITelemetry
    : public omni::core::Generated<omni::telemetry::ITelemetry_abi>
{
public:
    static void sendCustomEvent(const char* eventType, double duration = 0.0, const char* data1 = nullptr, const char* data2 = nullptr, double value1 = 0.0, double value2 = 0.0)
    {
        omni::core::ObjectPtr<omni::telemetry::ITelemetry> ptr = omni::core::createType<omni::telemetry::ITelemetry>();

        if (ptr.get() == nullptr)
            return;

        ptr->sendGenericEvent(eventType, duration, data1, data2, value1, value2);
    }
};

#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include "ITelemetry.gen.h"
