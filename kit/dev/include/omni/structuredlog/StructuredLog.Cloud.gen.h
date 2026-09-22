// SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

// DO NOT MODIFY THIS FILE. This is a generated file.
// This file was generated from: StructuredLog.Cloud.schema

//
#pragma once

#include <omni/log/ILog.h>
#include <omni/structuredlog/IStructuredLog.h>
#include <omni/structuredlog/JsonTree.h>
#include <omni/structuredlog/BinarySerializer.h>
#include <omni/structuredlog/StringView.h>

#include <memory>

namespace omni
{
namespace telemetry
{

/** helper macro to send the 'startup' event.
 *
 *  @param[in] cloud_link_id_ Parameter from schema at path '/cloud_link_id'.
 *             The UUID of the cloud session that is currently running Kit or
 *             NVStreamer.  This is used to link together events across multiple
 *             sessions or instances that are running under the same cloud
 *             session.
 *  @param[in] ident_ Parameter from schema at path '/ident'.
 *             The information of where this pod is running.
 *  @param[in] application_ Parameter from schema at path '/application'.
 *             The information about which app is being run.  This is duplicated
 *             information and should be removed eventually.
 *  @returns no return value.
 *
 *  @remarks This event notes which Kit or NVStreamer based app was launched,
 *           its version, the user, node, and cluster information, and the
 *           cloud session ID that needs to be linked to this telemetry session
 *           ID.
 *
 *  @sa @ref Schema_omni_carb_cloud_1_0::startup_sendEvent().
 *  @sa @ref Schema_omni_carb_cloud_1_0::startup_isEnabled().
 */
#define OMNI_OMNI_CARB_CLOUD_1_0_STARTUP(cloud_link_id_, ident_, application_)                                         \
    OMNI_STRUCTURED_LOG(omni::telemetry::Schema_omni_carb_cloud_1_0::startup, cloud_link_id_, ident_, application_)

/** helper macro to send the 'heartbeat' event.
 *
 *  @param[in] cloud_link_id_ Parameter from schema at path '/cloud_link_id'.
 *             The UUID of the cloud session that is currently running Kit or
 *             NVStreamer.  This is used to link together events across multiple
 *             sessions or instances that are running under the same cloud
 *             session.
 *  @returns no return value.
 *
 *  @remarks This event notes that the app is still running.  The intention is
 *           that this event should be emitted periodically to provide a way to
 *           estimate session lengths even in cases where the exit event is not
 *           present (ie: unexpected exit, power loss, process killed by the
 *           user, etc).
 *
 *  @sa @ref Schema_omni_carb_cloud_1_0::heartbeat_sendEvent().
 *  @sa @ref Schema_omni_carb_cloud_1_0::heartbeat_isEnabled().
 */
#define OMNI_OMNI_CARB_CLOUD_1_0_HEARTBEAT(cloud_link_id_)                                                             \
    OMNI_STRUCTURED_LOG(omni::telemetry::Schema_omni_carb_cloud_1_0::heartbeat, cloud_link_id_)

/** helper macro to send the 'exit' event.
 *
 *  @param[in] cloud_link_id_ Parameter from schema at path '/cloud_link_id'.
 *             The UUID of the cloud session that is currently running Kit or
 *             NVStreamer.  This is used to link together events across multiple
 *             sessions or instances that are running under the same cloud
 *             session.
 *  @param[in] application_ Parameter from schema at path '/application'.
 *             The information about which app is being run.  This is duplicated
 *             information and should be removed eventually.
 *  @param[in] exit_abnormally_ Parameter from schema at path '/exit_abnormally'.
 *             A flag indicating whether a crash occurred (true) or if a normal
 *             exit was used (false).
 *  @returns no return value.
 *
 *  @remarks This event notes which Kit or NVStreamer based app was exited, its
 *           version, whether the exit was clean or not, and the cloud session
 *           ID that needs to be linked to this telemetry session ID.
 *
 *  @sa @ref Schema_omni_carb_cloud_1_0::exit_sendEvent().
 *  @sa @ref Schema_omni_carb_cloud_1_0::exit_isEnabled().
 */
#define OMNI_OMNI_CARB_CLOUD_1_0_EXIT(cloud_link_id_, application_, exit_abnormally_)                                  \
    OMNI_STRUCTURED_LOG(                                                                                               \
        omni::telemetry::Schema_omni_carb_cloud_1_0::exit, cloud_link_id_, application_, exit_abnormally_)

class Schema_omni_carb_cloud_1_0
{
public:
    /** struct definition for parameter ident of event com.nvidia.omni.carb.cloud.startup. */
    struct Struct_startup_ident
    {
        /** The identifier of the cluster this pod is running on. */
        omni::structuredlog::StringView cluster;

        /** The identifier of the node this pod is running on.  This will be
         *  either a hostname or the IPv4/IPv6 address of the node.
         */
        omni::structuredlog::StringView node;

        /** Default constructor for @ref Struct_startup_ident. */
        Struct_startup_ident() = default;

        /** Basic constructor for @ref Struct_startup_ident. */
        Struct_startup_ident(omni::structuredlog::StringView cluster_, omni::structuredlog::StringView node_)
        {
            cluster = cluster_;
            node = node_;
        }

        /** Basic assignment operator for @ref Struct_startup_ident. */
        Struct_startup_ident& operator=(const Struct_startup_ident& other)
        {
            cluster = other.cluster;
            node = other.node;
            return *this;
        }

        /** Basic copy constructor for @ref Struct_startup_ident. */
        Struct_startup_ident(const Struct_startup_ident& other)
        {
            *this = other;
        }
    };

    /** struct definition for parameter application of event com.nvidia.omni.carb.cloud.startup. */
    struct Struct_startup_application
    {
        /** The name of the app that is starting up. */
        omni::structuredlog::StringView name;

        /** The version of the app that is starting up. */
        omni::structuredlog::StringView version;

        /** Default constructor for @ref Struct_startup_application. */
        Struct_startup_application() = default;

        /** Basic constructor for @ref Struct_startup_application. */
        Struct_startup_application(omni::structuredlog::StringView name_, omni::structuredlog::StringView version_)
        {
            name = name_;
            version = version_;
        }

        /** Basic assignment operator for @ref Struct_startup_application. */
        Struct_startup_application& operator=(const Struct_startup_application& other)
        {
            name = other.name;
            version = other.version;
            return *this;
        }

        /** Basic copy constructor for @ref Struct_startup_application. */
        Struct_startup_application(const Struct_startup_application& other)
        {
            *this = other;
        }
    };

    /** struct definition for parameter application of event com.nvidia.omni.carb.cloud.exit. */
    struct Struct_exit_application
    {
        /** The name of the app that is starting up. */
        omni::structuredlog::StringView name;

        /** The version of the app that is starting up. */
        omni::structuredlog::StringView version;

        /** Default constructor for @ref Struct_exit_application. */
        Struct_exit_application() = default;

        /** Basic constructor for @ref Struct_exit_application. */
        Struct_exit_application(omni::structuredlog::StringView name_, omni::structuredlog::StringView version_)
        {
            name = name_;
            version = version_;
        }

        /** Basic assignment operator for @ref Struct_exit_application. */
        Struct_exit_application& operator=(const Struct_exit_application& other)
        {
            name = other.name;
            version = other.version;
            return *this;
        }

        /** Basic copy constructor for @ref Struct_exit_application. */
        Struct_exit_application(const Struct_exit_application& other)
        {
            *this = other;
        }
    };

    /** the event ID names used to send the events in this schema.  These IDs
     *  are used when the schema is first registered, and are passed to the
     *  allocEvent() function when sending the event.
     */
    enum : uint64_t
    {
        kStartupEventId =
            OMNI_STRUCTURED_LOG_EVENT_ID("omni.carb.cloud", "com.nvidia.omni.carb.cloud.startup", "1.0", "0"),
        kHeartbeatEventId =
            OMNI_STRUCTURED_LOG_EVENT_ID("omni.carb.cloud", "com.nvidia.omni.carb.cloud.heartbeat", "1.0", "0"),
        kExitEventId = OMNI_STRUCTURED_LOG_EVENT_ID("omni.carb.cloud", "com.nvidia.omni.carb.cloud.exit", "1.0", "0"),
    };

    Schema_omni_carb_cloud_1_0() = default;

    /** Register this class with the @ref omni::structuredlog::IStructuredLog interface.
     *  @param[in] flags The flags to pass into @ref omni::structuredlog::IStructuredLog::allocSchema()
     *                   This may be zero or more of the @ref omni::structuredlog::SchemaFlags flags.
     *  @returns `true` if the operation succeeded.
     *  @returns `false` if @ref omni::structuredlog::IStructuredLog couldn't be loaded.
     *  @returns `false` if a memory allocation failed.
     */
    static bool registerSchema(omni::structuredlog::IStructuredLog* strucLog) noexcept
    {
        return _registerSchema(strucLog);
    }

    /** Check whether this structured log schema is enabled.
     *  @param[in] eventId     the ID of the event to check the enable state for.
     *                         This must be one of the @a k*EventId symbols
     *                         defined above.
     *  @returns Whether this client is enabled.
     */
    static bool isEnabled(omni::structuredlog::EventId eventId) noexcept
    {
        return _isEnabled(eventId);
    }

    /** Enable/disable an event in this schema.
     *  @param[in] eventId     the ID of the event to enable or disable.
     *                         This must be one of the @a k*EventId symbols
     *                         defined above.
     *  @param[in] enabled     Whether is enabled or disabled.
     */
    static void setEnabled(omni::structuredlog::EventId eventId, bool enabled) noexcept
    {
        _setEnabled(eventId, enabled);
    }

    /** Enable/disable this schema.
     *  @param[in] enabled     Whether is enabled or disabled.
     */
    static void setEnabled(bool enabled) noexcept
    {
        _setEnabled(enabled);
    }

    /** event enable check helper functions.
     *
     *  @param[in] strucLog   The structured log object to use to send this event.  This
     *                        must not be nullptr.  It is the caller's responsibility
     *                        to ensure that a valid object is passed in.
     *  @returns `true` if the specific event and this schema are both enabled.
     *  @returns `false` if either the specific event or this schema is disabled.
     *
     *  @remarks These check if an event corresponding to the function name is currently
     *           enabled.  These are useful to avoid parameter evaluation before calling
     *           into one of the event emitter functions.  These will be called from the
     *           OMNI_STRUCTURED_LOG() macro.  These may also be called directly if an event
     *           needs to be emitted manually, but the only effect would be the potential
     *           to avoid parameter evaluation in the *_sendEvent() function.  Each
     *           *_sendEvent() function itself will also internally check if the event
     *           is enabled before sending it.
     *  @{
     */
    static bool startup_isEnabled(omni::structuredlog::IStructuredLog* strucLog) noexcept
    {
        return strucLog->isEnabled(kStartupEventId);
    }

    static bool heartbeat_isEnabled(omni::structuredlog::IStructuredLog* strucLog) noexcept
    {
        return strucLog->isEnabled(kHeartbeatEventId);
    }

    static bool exit_isEnabled(omni::structuredlog::IStructuredLog* strucLog) noexcept
    {
        return strucLog->isEnabled(kExitEventId);
    }
    /** @} */

    /** Send the event 'com.nvidia.omni.carb.cloud.startup'
     *
     *  @param[in] strucLog The global structured log object to use to send
     *             this event.  This must not be nullptr.  It is the caller's
     *             responsibility to ensure a valid object is passed in.
     *  @param[in] cloud_link_id Parameter from schema at path '/cloud_link_id'.
     *             The UUID of the cloud session that is currently running Kit or
     *             NVStreamer.  This is used to link together events across multiple
     *             sessions or instances that are running under the same cloud
     *             session.
     *  @param[in] ident Parameter from schema at path '/ident'.
     *             The information of where this pod is running.
     *  @param[in] application Parameter from schema at path '/application'.
     *             The information about which app is being run.  This is duplicated
     *             information and should be removed eventually.
     *  @returns no return value.
     *
     *  @remarks This event notes which Kit or NVStreamer based app was launched,
     *           its version, the user, node, and cluster information, and the
     *           cloud session ID that needs to be linked to this telemetry session
     *           ID.
     */
    static void startup_sendEvent(omni::structuredlog::IStructuredLog* strucLog,
                                  const omni::structuredlog::StringView& cloud_link_id,
                                  const Struct_startup_ident& ident,
                                  const Struct_startup_application& application) noexcept
    {
        _startup_sendEvent(strucLog, cloud_link_id, ident, application);
    }

    /** Send the event 'com.nvidia.omni.carb.cloud.heartbeat'
     *
     *  @param[in] strucLog The global structured log object to use to send
     *             this event.  This must not be nullptr.  It is the caller's
     *             responsibility to ensure a valid object is passed in.
     *  @param[in] cloud_link_id Parameter from schema at path '/cloud_link_id'.
     *             The UUID of the cloud session that is currently running Kit or
     *             NVStreamer.  This is used to link together events across multiple
     *             sessions or instances that are running under the same cloud
     *             session.
     *  @returns no return value.
     *
     *  @remarks This event notes that the app is still running.  The intention is
     *           that this event should be emitted periodically to provide a way to
     *           estimate session lengths even in cases where the exit event is not
     *           present (ie: unexpected exit, power loss, process killed by the
     *           user, etc).
     */
    static void heartbeat_sendEvent(omni::structuredlog::IStructuredLog* strucLog,
                                    const omni::structuredlog::StringView& cloud_link_id) noexcept
    {
        _heartbeat_sendEvent(strucLog, cloud_link_id);
    }

    /** Send the event 'com.nvidia.omni.carb.cloud.exit'
     *
     *  @param[in] strucLog The global structured log object to use to send
     *             this event.  This must not be nullptr.  It is the caller's
     *             responsibility to ensure a valid object is passed in.
     *  @param[in] cloud_link_id Parameter from schema at path '/cloud_link_id'.
     *             The UUID of the cloud session that is currently running Kit or
     *             NVStreamer.  This is used to link together events across multiple
     *             sessions or instances that are running under the same cloud
     *             session.
     *  @param[in] application Parameter from schema at path '/application'.
     *             The information about which app is being run.  This is duplicated
     *             information and should be removed eventually.
     *  @param[in] exit_abnormally Parameter from schema at path '/exit_abnormally'.
     *             A flag indicating whether a crash occurred (true) or if a normal
     *             exit was used (false).
     *  @returns no return value.
     *
     *  @remarks This event notes which Kit or NVStreamer based app was exited, its
     *           version, whether the exit was clean or not, and the cloud session
     *           ID that needs to be linked to this telemetry session ID.
     */
    static void exit_sendEvent(omni::structuredlog::IStructuredLog* strucLog,
                               const omni::structuredlog::StringView& cloud_link_id,
                               const Struct_exit_application& application,
                               bool exit_abnormally) noexcept
    {
        _exit_sendEvent(strucLog, cloud_link_id, application, exit_abnormally);
    }

private:
    /** This will allow us to disable array length checks in release builds,
     *  since they would have a negative performance impact and only be hit
     *  in unusual circumstances.
     */
    static constexpr bool kValidateLength = CARB_DEBUG;

    /** body for the registerSchema() public function. */
    static bool _registerSchema(omni::structuredlog::IStructuredLog* strucLog)
    {
        omni::structuredlog::AllocHandle handle = {};
        omni::structuredlog::SchemaResult result;
        uint8_t* buffer;
        omni::structuredlog::EventInfo events[3] = {};
        size_t bufferSize = 0;
        size_t total = 0;
        omni::structuredlog::SchemaFlags flags = 0;

        if (strucLog == nullptr)
        {
            OMNI_LOG_WARN(
                "no structured log object!  The schema "
                "'Schema_omni_carb_cloud_1_0' "
                "will be disabled.");
            return false;
        }

        // calculate the tree sizes
        size_t startup_size = _startup_calculateTreeSize();
        size_t heartbeat_size = _heartbeat_calculateTreeSize();
        size_t exit_size = _exit_calculateTreeSize();

        // calculate the event buffer size
        bufferSize += startup_size;
        bufferSize += heartbeat_size;
        bufferSize += exit_size;

        // begin schema creation
        buffer = strucLog->allocSchema("omni.carb.cloud", "1.0", flags, bufferSize, &handle);
        if (buffer == nullptr)
        {
            OMNI_LOG_ERROR("allocSchema failed (size = %zu bytes)", bufferSize);
            return false;
        }

        // register all the events
        events[0].schema = _startup_buildJsonTree(startup_size, buffer + total);
        events[0].eventName = "com.nvidia.omni.carb.cloud.startup";
        events[0].parserVersion = 0;
        events[0].eventId = kStartupEventId;
        total += startup_size;
        events[1].schema = _heartbeat_buildJsonTree(heartbeat_size, buffer + total);
        events[1].eventName = "com.nvidia.omni.carb.cloud.heartbeat";
        events[1].parserVersion = 0;
        events[1].eventId = kHeartbeatEventId;
        total += heartbeat_size;
        events[2].schema = _exit_buildJsonTree(exit_size, buffer + total);
        events[2].eventName = "com.nvidia.omni.carb.cloud.exit";
        events[2].parserVersion = 0;
        events[2].eventId = kExitEventId;
        total += exit_size;

        result = strucLog->commitSchema(handle, events, CARB_COUNTOF(events));
        if (result != omni::structuredlog::SchemaResult::eSuccess &&
            result != omni::structuredlog::SchemaResult::eAlreadyExists)
        {
            OMNI_LOG_ERROR(
                "failed to register structured log events "
                "{result = %s (%zu)}",
                getSchemaResultName(result), size_t(result));
            return false;
        }

        return true;
    }

    /** body for the isEnabled() public function. */
    static bool _isEnabled(omni::structuredlog::EventId eventId)
    {
        omni::structuredlog::IStructuredLog* strucLog = omniGetStructuredLogWithoutAcquire();
        return strucLog != nullptr && strucLog->isEnabled(eventId);
    }

    /** body for the setEnabled() public function. */
    static void _setEnabled(omni::structuredlog::EventId eventId, bool enabled)
    {
        omni::structuredlog::IStructuredLog* strucLog = omniGetStructuredLogWithoutAcquire();
        if (strucLog == nullptr)
            return;

        strucLog->setEnabled(eventId, 0, enabled);
    }

    /** body for the setEnabled() public function. */
    static void _setEnabled(bool enabled)
    {
        omni::structuredlog::IStructuredLog* strucLog = omniGetStructuredLogWithoutAcquire();
        if (strucLog == nullptr)
            return;

        strucLog->setEnabled(kStartupEventId, omni::structuredlog::fEnableFlagWholeSchema, enabled);
    }

#if OMNI_PLATFORM_WINDOWS
#    pragma warning(push)
#    pragma warning(disable : 4127) // warning C4127: conditional expression is constant.
#endif

    /** body for the startup_sendEvent() function. */
    static void _startup_sendEvent(omni::structuredlog::IStructuredLog* strucLog,
                                   const omni::structuredlog::StringView& cloud_link_id,
                                   const Struct_startup_ident& ident,
                                   const Struct_startup_application& application) noexcept
    {
        omni::structuredlog::AllocHandle handle = {};

        // calculate the required buffer size for the event
        omni::structuredlog::BinaryBlobSizeCalculator calc;
        {
            if (kValidateLength && cloud_link_id.length() + 1 > UINT16_MAX)
            {
                OMNI_LOG_ERROR(
                    "length of parameter 'cloud_link_id' exceeds max value 65535 - "
                    "it will be truncated (size was %zu)",
                    cloud_link_id.length() + 1);
            }

            // property cloud_link_id
            calc.track(cloud_link_id);

            // property ident
            {
                if (kValidateLength && ident.cluster.length() + 1 > UINT16_MAX)
                {
                    OMNI_LOG_ERROR(
                        "length of parameter 'ident.cluster' exceeds max value 65535 - "
                        "it will be truncated (size was %zu)",
                        ident.cluster.length() + 1);
                }

                // property ident.cluster
                calc.track(ident.cluster);

                if (kValidateLength && ident.node.length() + 1 > UINT16_MAX)
                {
                    OMNI_LOG_ERROR(
                        "length of parameter 'ident.node' exceeds max value 65535 - "
                        "it will be truncated (size was %zu)",
                        ident.node.length() + 1);
                }

                // property ident.node
                calc.track(ident.node);
            }

            // property application
            {
                if (kValidateLength && application.name.length() + 1 > UINT16_MAX)
                {
                    OMNI_LOG_ERROR(
                        "length of parameter 'application.name' exceeds max value 65535 - "
                        "it will be truncated (size was %zu)",
                        application.name.length() + 1);
                }

                // property application.name
                calc.track(application.name);

                if (kValidateLength && application.version.length() + 1 > UINT16_MAX)
                {
                    OMNI_LOG_ERROR(
                        "length of parameter 'application.version' exceeds max value 65535 - "
                        "it will be truncated (size was %zu)",
                        application.version.length() + 1);
                }

                // property application.version
                calc.track(application.version);
            }
        }

        // write out the event into the buffer
        void* buffer = strucLog->allocEvent(0, kStartupEventId, 0, calc.getSize(), &handle);
        if (buffer == nullptr)
        {
            OMNI_LOG_ERROR(
                "failed to allocate a %zu byte buffer for structured log event "
                "'com.nvidia.omni.carb.cloud.startup'",
                calc.getSize());
            return;
        }

        omni::structuredlog::BlobWriter<CARB_DEBUG, _onStructuredLogValidationError> writer(buffer, calc.getSize());
        {
            // property cloud_link_id
            writer.copy(cloud_link_id);

            // property ident
            {
                // property ident.cluster
                writer.copy(ident.cluster);

                // property ident.node
                writer.copy(ident.node);
            }

            // property application
            {
                // property application.name
                writer.copy(application.name);

                // property application.version
                writer.copy(application.version);
            }
        }

        strucLog->commitEvent(handle);
    }

    /** body for the heartbeat_sendEvent() function. */
    static void _heartbeat_sendEvent(omni::structuredlog::IStructuredLog* strucLog,
                                     const omni::structuredlog::StringView& cloud_link_id) noexcept
    {
        omni::structuredlog::AllocHandle handle = {};

        // calculate the required buffer size for the event
        omni::structuredlog::BinaryBlobSizeCalculator calc;
        {
            if (kValidateLength && cloud_link_id.length() + 1 > UINT16_MAX)
            {
                OMNI_LOG_ERROR(
                    "length of parameter 'cloud_link_id' exceeds max value 65535 - "
                    "it will be truncated (size was %zu)",
                    cloud_link_id.length() + 1);
            }

            // property cloud_link_id
            calc.track(cloud_link_id);
        }

        // write out the event into the buffer
        void* buffer = strucLog->allocEvent(0, kHeartbeatEventId, 0, calc.getSize(), &handle);
        if (buffer == nullptr)
        {
            OMNI_LOG_ERROR(
                "failed to allocate a %zu byte buffer for structured log event "
                "'com.nvidia.omni.carb.cloud.heartbeat'",
                calc.getSize());
            return;
        }

        omni::structuredlog::BlobWriter<CARB_DEBUG, _onStructuredLogValidationError> writer(buffer, calc.getSize());
        {
            // property cloud_link_id
            writer.copy(cloud_link_id);
        }

        strucLog->commitEvent(handle);
    }

    /** body for the exit_sendEvent() function. */
    static void _exit_sendEvent(omni::structuredlog::IStructuredLog* strucLog,
                                const omni::structuredlog::StringView& cloud_link_id,
                                const Struct_exit_application& application,
                                bool exit_abnormally) noexcept
    {
        omni::structuredlog::AllocHandle handle = {};

        // calculate the required buffer size for the event
        omni::structuredlog::BinaryBlobSizeCalculator calc;
        {
            if (kValidateLength && cloud_link_id.length() + 1 > UINT16_MAX)
            {
                OMNI_LOG_ERROR(
                    "length of parameter 'cloud_link_id' exceeds max value 65535 - "
                    "it will be truncated (size was %zu)",
                    cloud_link_id.length() + 1);
            }

            // property cloud_link_id
            calc.track(cloud_link_id);

            // property application
            {
                if (kValidateLength && application.name.length() + 1 > UINT16_MAX)
                {
                    OMNI_LOG_ERROR(
                        "length of parameter 'application.name' exceeds max value 65535 - "
                        "it will be truncated (size was %zu)",
                        application.name.length() + 1);
                }

                // property application.name
                calc.track(application.name);

                if (kValidateLength && application.version.length() + 1 > UINT16_MAX)
                {
                    OMNI_LOG_ERROR(
                        "length of parameter 'application.version' exceeds max value 65535 - "
                        "it will be truncated (size was %zu)",
                        application.version.length() + 1);
                }

                // property application.version
                calc.track(application.version);
            }

            // property exit_abnormally
            calc.track(exit_abnormally);
        }

        // write out the event into the buffer
        void* buffer = strucLog->allocEvent(0, kExitEventId, 0, calc.getSize(), &handle);
        if (buffer == nullptr)
        {
            OMNI_LOG_ERROR(
                "failed to allocate a %zu byte buffer for structured log event "
                "'com.nvidia.omni.carb.cloud.exit'",
                calc.getSize());
            return;
        }

        omni::structuredlog::BlobWriter<CARB_DEBUG, _onStructuredLogValidationError> writer(buffer, calc.getSize());
        {
            // property cloud_link_id
            writer.copy(cloud_link_id);

            // property application
            {
                // property application.name
                writer.copy(application.name);

                // property application.version
                writer.copy(application.version);
            }

            // property exit_abnormally
            writer.copy(exit_abnormally);
        }

        strucLog->commitEvent(handle);
    }
#if OMNI_PLATFORM_WINDOWS
#    pragma warning(pop)
#endif

    /** Calculate JSON tree size for structured log event: com.nvidia.omni.carb.cloud.startup.
     *  @returns The JSON tree size in bytes for this event.
     */
    static size_t _startup_calculateTreeSize()
    {
        // calculate the buffer size for the tree
        omni::structuredlog::JsonTreeSizeCalculator calc;
        calc.trackRoot();
        calc.trackObject(5); // object has 5 properties
        {
            // property cloud_link_id
            calc.trackName("cloud_link_id");
            calc.track(static_cast<const char*>(nullptr));

            // property ident
            calc.trackName("ident");
            calc.trackObject(2); // object has 2 properties
            {
                // property cluster
                calc.trackName("cluster");
                calc.track(static_cast<const char*>(nullptr));

                // property node
                calc.trackName("node");
                calc.track(static_cast<const char*>(nullptr));
            }

            // property application
            calc.trackName("application");
            calc.trackObject(2); // object has 2 properties
            {
                // property name
                calc.trackName("name");
                calc.track(static_cast<const char*>(nullptr));

                // property version
                calc.trackName("version");
                calc.track(static_cast<const char*>(nullptr));
            }

            // property version
            calc.trackName("version");
            calc.track("1", sizeof("1"));

            // property event
            calc.trackName("event");
            calc.track("cloud-startup", sizeof("cloud-startup"));
        }
        return calc.getSize();
    }

    /** Generate the JSON tree for structured log event: com.nvidia.omni.carb.cloud.startup.
     *  @param[in]    bufferSize The length of @p buffer in bytes.
     *  @param[inout] buffer     The buffer to write the tree into.
     *  @returns The JSON tree for this event.
     *  @returns nullptr if a logic error occurred or @p bufferSize was too small.
     */
    static omni::structuredlog::JsonNode* _startup_buildJsonTree(size_t bufferSize, uint8_t* buffer)
    {
        CARB_MAYBE_UNUSED bool result;
        omni::structuredlog::BlockAllocator alloc(buffer, bufferSize);
        omni::structuredlog::JsonBuilder builder(&alloc);
        omni::structuredlog::JsonNode* base = static_cast<omni::structuredlog::JsonNode*>(alloc.alloc(sizeof(*base)));
        if (base == nullptr)
        {
            OMNI_LOG_ERROR(
                "failed to allocate the base node for event "
                "'com.nvidia.omni.carb.cloud.startup' "
                "{alloc size = %zu, buffer size = %zu}",
                sizeof(*base), bufferSize);
            return nullptr;
        }
        *base = {};

        // build the tree
        result = builder.createObject(base, 5); // object has 5 properties
        if (!result)
        {
            OMNI_LOG_ERROR("failed to create an object node (bad size calculation?)");
            return nullptr;
        }
        {
            // property cloud_link_id
            result = builder.setName(&base->data.objVal[0], "cloud_link_id");
            if (!result)
            {
                OMNI_LOG_ERROR("failed to set the object name (bad size calculation?)");
                return nullptr;
            }
            result = builder.setNode(&base->data.objVal[0], static_cast<const char*>(nullptr));
            if (!result)
            {
                OMNI_LOG_ERROR("failed to set type 'const char*' (shouldn't be possible)");
                return nullptr;
            }

            // property ident
            result = builder.setName(&base->data.objVal[1], "ident");
            if (!result)
            {
                OMNI_LOG_ERROR("failed to set the object name (bad size calculation?)");
                return nullptr;
            }
            result = builder.createObject(&base->data.objVal[1], 2); // object has 2 properties
            if (!result)
            {
                OMNI_LOG_ERROR("failed to create a new object node (bad size calculation?)");
                return nullptr;
            }
            {
                // property cluster
                result = builder.setName(&base->data.objVal[1].data.objVal[0], "cluster");
                if (!result)
                {
                    OMNI_LOG_ERROR("failed to set the object name (bad size calculation?)");
                    return nullptr;
                }
                result = builder.setNode(&base->data.objVal[1].data.objVal[0], static_cast<const char*>(nullptr));
                if (!result)
                {
                    OMNI_LOG_ERROR("failed to set type 'const char*' (shouldn't be possible)");
                    return nullptr;
                }

                // property node
                result = builder.setName(&base->data.objVal[1].data.objVal[1], "node");
                if (!result)
                {
                    OMNI_LOG_ERROR("failed to set the object name (bad size calculation?)");
                    return nullptr;
                }
                result = builder.setNode(&base->data.objVal[1].data.objVal[1], static_cast<const char*>(nullptr));
                if (!result)
                {
                    OMNI_LOG_ERROR("failed to set type 'const char*' (shouldn't be possible)");
                    return nullptr;
                }
            }

            // property application
            result = builder.setName(&base->data.objVal[2], "application");
            if (!result)
            {
                OMNI_LOG_ERROR("failed to set the object name (bad size calculation?)");
                return nullptr;
            }
            result = builder.createObject(&base->data.objVal[2], 2); // object has 2 properties
            if (!result)
            {
                OMNI_LOG_ERROR("failed to create a new object node (bad size calculation?)");
                return nullptr;
            }
            {
                // property name
                result = builder.setName(&base->data.objVal[2].data.objVal[0], "name");
                if (!result)
                {
                    OMNI_LOG_ERROR("failed to set the object name (bad size calculation?)");
                    return nullptr;
                }
                result = builder.setNode(&base->data.objVal[2].data.objVal[0], static_cast<const char*>(nullptr));
                if (!result)
                {
                    OMNI_LOG_ERROR("failed to set type 'const char*' (shouldn't be possible)");
                    return nullptr;
                }

                // property version
                result = builder.setName(&base->data.objVal[2].data.objVal[1], "version");
                if (!result)
                {
                    OMNI_LOG_ERROR("failed to set the object name (bad size calculation?)");
                    return nullptr;
                }
                result = builder.setNode(&base->data.objVal[2].data.objVal[1], static_cast<const char*>(nullptr));
                if (!result)
                {
                    OMNI_LOG_ERROR("failed to set type 'const char*' (shouldn't be possible)");
                    return nullptr;
                }
            }

            // property version
            result = builder.setName(&base->data.objVal[3], "version");
            if (!result)
            {
                OMNI_LOG_ERROR("failed to set the object name (bad size calculation?)");
                return nullptr;
            }
            result = builder.setNode(&base->data.objVal[3], "1", sizeof("1"));
            if (!result)
            {
                OMNI_LOG_ERROR("failed to copy string '1' (bad size calculation?)");
                return nullptr;
            }
            result = omni::structuredlog::JsonBuilder::setFlags(
                &base->data.objVal[3], omni::structuredlog::JsonNode::fFlagConst);
            if (!result)
            {
                OMNI_LOG_ERROR("failed to set flag 'omni::structuredlog::JsonNode::fFlagConst'");
                return nullptr;
            }

            // property event
            result = builder.setName(&base->data.objVal[4], "event");
            if (!result)
            {
                OMNI_LOG_ERROR("failed to set the object name (bad size calculation?)");
                return nullptr;
            }
            result = builder.setNode(&base->data.objVal[4], "cloud-startup", sizeof("cloud-startup"));
            if (!result)
            {
                OMNI_LOG_ERROR("failed to copy string 'cloud-startup' (bad size calculation?)");
                return nullptr;
            }
            result = omni::structuredlog::JsonBuilder::setFlags(
                &base->data.objVal[4], omni::structuredlog::JsonNode::fFlagConst);
            if (!result)
            {
                OMNI_LOG_ERROR("failed to set flag 'omni::structuredlog::JsonNode::fFlagConst'");
                return nullptr;
            }
        }

        return base;
    }

    /** Calculate JSON tree size for structured log event: com.nvidia.omni.carb.cloud.heartbeat.
     *  @returns The JSON tree size in bytes for this event.
     */
    static size_t _heartbeat_calculateTreeSize()
    {
        // calculate the buffer size for the tree
        omni::structuredlog::JsonTreeSizeCalculator calc;
        calc.trackRoot();
        calc.trackObject(2); // object has 2 properties
        {
            // property cloud_link_id
            calc.trackName("cloud_link_id");
            calc.track(static_cast<const char*>(nullptr));

            // property event
            calc.trackName("event");
            calc.track("cloud-heartbeat", sizeof("cloud-heartbeat"));
        }
        return calc.getSize();
    }

    /** Generate the JSON tree for structured log event: com.nvidia.omni.carb.cloud.heartbeat.
     *  @param[in]    bufferSize The length of @p buffer in bytes.
     *  @param[inout] buffer     The buffer to write the tree into.
     *  @returns The JSON tree for this event.
     *  @returns nullptr if a logic error occurred or @p bufferSize was too small.
     */
    static omni::structuredlog::JsonNode* _heartbeat_buildJsonTree(size_t bufferSize, uint8_t* buffer)
    {
        CARB_MAYBE_UNUSED bool result;
        omni::structuredlog::BlockAllocator alloc(buffer, bufferSize);
        omni::structuredlog::JsonBuilder builder(&alloc);
        omni::structuredlog::JsonNode* base = static_cast<omni::structuredlog::JsonNode*>(alloc.alloc(sizeof(*base)));
        if (base == nullptr)
        {
            OMNI_LOG_ERROR(
                "failed to allocate the base node for event "
                "'com.nvidia.omni.carb.cloud.heartbeat' "
                "{alloc size = %zu, buffer size = %zu}",
                sizeof(*base), bufferSize);
            return nullptr;
        }
        *base = {};

        // build the tree
        result = builder.createObject(base, 2); // object has 2 properties
        if (!result)
        {
            OMNI_LOG_ERROR("failed to create an object node (bad size calculation?)");
            return nullptr;
        }
        {
            // property cloud_link_id
            result = builder.setName(&base->data.objVal[0], "cloud_link_id");
            if (!result)
            {
                OMNI_LOG_ERROR("failed to set the object name (bad size calculation?)");
                return nullptr;
            }
            result = builder.setNode(&base->data.objVal[0], static_cast<const char*>(nullptr));
            if (!result)
            {
                OMNI_LOG_ERROR("failed to set type 'const char*' (shouldn't be possible)");
                return nullptr;
            }

            // property event
            result = builder.setName(&base->data.objVal[1], "event");
            if (!result)
            {
                OMNI_LOG_ERROR("failed to set the object name (bad size calculation?)");
                return nullptr;
            }
            result = builder.setNode(&base->data.objVal[1], "cloud-heartbeat", sizeof("cloud-heartbeat"));
            if (!result)
            {
                OMNI_LOG_ERROR("failed to copy string 'cloud-heartbeat' (bad size calculation?)");
                return nullptr;
            }
            result = omni::structuredlog::JsonBuilder::setFlags(
                &base->data.objVal[1], omni::structuredlog::JsonNode::fFlagConst);
            if (!result)
            {
                OMNI_LOG_ERROR("failed to set flag 'omni::structuredlog::JsonNode::fFlagConst'");
                return nullptr;
            }
        }

        return base;
    }

    /** Calculate JSON tree size for structured log event: com.nvidia.omni.carb.cloud.exit.
     *  @returns The JSON tree size in bytes for this event.
     */
    static size_t _exit_calculateTreeSize()
    {
        // calculate the buffer size for the tree
        omni::structuredlog::JsonTreeSizeCalculator calc;
        calc.trackRoot();
        calc.trackObject(4); // object has 4 properties
        {
            // property cloud_link_id
            calc.trackName("cloud_link_id");
            calc.track(static_cast<const char*>(nullptr));

            // property application
            calc.trackName("application");
            calc.trackObject(2); // object has 2 properties
            {
                // property name
                calc.trackName("name");
                calc.track(static_cast<const char*>(nullptr));

                // property version
                calc.trackName("version");
                calc.track(static_cast<const char*>(nullptr));
            }

            // property exit_abnormally
            calc.trackName("exit_abnormally");
            calc.track(bool(false));

            // property event
            calc.trackName("event");
            calc.track("cloud-exit", sizeof("cloud-exit"));
        }
        return calc.getSize();
    }

    /** Generate the JSON tree for structured log event: com.nvidia.omni.carb.cloud.exit.
     *  @param[in]    bufferSize The length of @p buffer in bytes.
     *  @param[inout] buffer     The buffer to write the tree into.
     *  @returns The JSON tree for this event.
     *  @returns nullptr if a logic error occurred or @p bufferSize was too small.
     */
    static omni::structuredlog::JsonNode* _exit_buildJsonTree(size_t bufferSize, uint8_t* buffer)
    {
        CARB_MAYBE_UNUSED bool result;
        omni::structuredlog::BlockAllocator alloc(buffer, bufferSize);
        omni::structuredlog::JsonBuilder builder(&alloc);
        omni::structuredlog::JsonNode* base = static_cast<omni::structuredlog::JsonNode*>(alloc.alloc(sizeof(*base)));
        if (base == nullptr)
        {
            OMNI_LOG_ERROR(
                "failed to allocate the base node for event "
                "'com.nvidia.omni.carb.cloud.exit' "
                "{alloc size = %zu, buffer size = %zu}",
                sizeof(*base), bufferSize);
            return nullptr;
        }
        *base = {};

        // build the tree
        result = builder.createObject(base, 4); // object has 4 properties
        if (!result)
        {
            OMNI_LOG_ERROR("failed to create an object node (bad size calculation?)");
            return nullptr;
        }
        {
            // property cloud_link_id
            result = builder.setName(&base->data.objVal[0], "cloud_link_id");
            if (!result)
            {
                OMNI_LOG_ERROR("failed to set the object name (bad size calculation?)");
                return nullptr;
            }
            result = builder.setNode(&base->data.objVal[0], static_cast<const char*>(nullptr));
            if (!result)
            {
                OMNI_LOG_ERROR("failed to set type 'const char*' (shouldn't be possible)");
                return nullptr;
            }

            // property application
            result = builder.setName(&base->data.objVal[1], "application");
            if (!result)
            {
                OMNI_LOG_ERROR("failed to set the object name (bad size calculation?)");
                return nullptr;
            }
            result = builder.createObject(&base->data.objVal[1], 2); // object has 2 properties
            if (!result)
            {
                OMNI_LOG_ERROR("failed to create a new object node (bad size calculation?)");
                return nullptr;
            }
            {
                // property name
                result = builder.setName(&base->data.objVal[1].data.objVal[0], "name");
                if (!result)
                {
                    OMNI_LOG_ERROR("failed to set the object name (bad size calculation?)");
                    return nullptr;
                }
                result = builder.setNode(&base->data.objVal[1].data.objVal[0], static_cast<const char*>(nullptr));
                if (!result)
                {
                    OMNI_LOG_ERROR("failed to set type 'const char*' (shouldn't be possible)");
                    return nullptr;
                }

                // property version
                result = builder.setName(&base->data.objVal[1].data.objVal[1], "version");
                if (!result)
                {
                    OMNI_LOG_ERROR("failed to set the object name (bad size calculation?)");
                    return nullptr;
                }
                result = builder.setNode(&base->data.objVal[1].data.objVal[1], static_cast<const char*>(nullptr));
                if (!result)
                {
                    OMNI_LOG_ERROR("failed to set type 'const char*' (shouldn't be possible)");
                    return nullptr;
                }
            }

            // property exit_abnormally
            result = builder.setName(&base->data.objVal[2], "exit_abnormally");
            if (!result)
            {
                OMNI_LOG_ERROR("failed to set the object name (bad size calculation?)");
                return nullptr;
            }
            result = builder.setNode(&base->data.objVal[2], bool(false));
            if (!result)
            {
                OMNI_LOG_ERROR("failed to set type 'bool' (shouldn't be possible)");
                return nullptr;
            }

            // property event
            result = builder.setName(&base->data.objVal[3], "event");
            if (!result)
            {
                OMNI_LOG_ERROR("failed to set the object name (bad size calculation?)");
                return nullptr;
            }
            result = builder.setNode(&base->data.objVal[3], "cloud-exit", sizeof("cloud-exit"));
            if (!result)
            {
                OMNI_LOG_ERROR("failed to copy string 'cloud-exit' (bad size calculation?)");
                return nullptr;
            }
            result = omni::structuredlog::JsonBuilder::setFlags(
                &base->data.objVal[3], omni::structuredlog::JsonNode::fFlagConst);
            if (!result)
            {
                OMNI_LOG_ERROR("failed to set flag 'omni::structuredlog::JsonNode::fFlagConst'");
                return nullptr;
            }
        }

        return base;
    }

    /** The callback that is used to report validation errors.
     *  @param[in] s The validation error message.
     */
    static void _onStructuredLogValidationError(const char* s)
    {
        OMNI_LOG_ERROR("error sending a structured log event: %s", s);
    }
};

// asserts to ensure that no one's modified our dependencies
static_assert(omni::structuredlog::BlobWriter<>::kVersion == 0, "BlobWriter version changed");
static_assert(omni::structuredlog::JsonNode::kVersion == 0, "JsonNode version changed");
static_assert(sizeof(omni::structuredlog::JsonNode) == 24, "unexpected size");
static_assert(std::is_standard_layout<omni::structuredlog::JsonNode>::value, "this type needs to be ABI safe");
static_assert(offsetof(omni::structuredlog::JsonNode, type) == 0, "struct layout changed");
static_assert(offsetof(omni::structuredlog::JsonNode, flags) == 1, "struct layout changed");
static_assert(offsetof(omni::structuredlog::JsonNode, len) == 2, "struct layout changed");
static_assert(offsetof(omni::structuredlog::JsonNode, nameLen) == 4, "struct layout changed");
static_assert(offsetof(omni::structuredlog::JsonNode, name) == 8, "struct layout changed");
static_assert(offsetof(omni::structuredlog::JsonNode, data) == 16, "struct layout changed");

} // namespace telemetry
} // namespace omni

OMNI_STRUCTURED_LOG_ADD_SCHEMA(omni::telemetry::Schema_omni_carb_cloud_1_0, omni_carb_cloud, 1_0, 0);
