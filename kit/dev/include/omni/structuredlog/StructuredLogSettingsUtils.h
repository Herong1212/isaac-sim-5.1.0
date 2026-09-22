// SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
/** @file
 *  @brief Utilities for the carb::settings::ISettings settings for structured logging.
 */
#pragma once

#include "IStructuredLog.h"
#include "IStructuredLogExtraFields.h"
#include "IStructuredLogSettings.h"
#include "IStructuredLogSettings2.h"
#include "IStructuredLogSettings3.h"
#include "IStructuredLogFromILog.h"
#include "IStructuredLogFromILog2.h"

#include "../../carb/extras/StringSafe.h"
#include "../../carb/settings/ISettings.h"
#include "../../carb/settings/SettingsUtils.h"
#include "../core/Omni.h"
#include "../extras/PrivacySettings.h"
#include "../extras/OmniConfig.h"
#include "../log/ILog.h"
#include "../platforminfo/IOsInfo2.h"


namespace omni
{
namespace structuredlog
{

/** Constants for default and minimum values for various settings.
 *  @{
 */

/** The default value for the log size limit in bytes.
 *  See IStructuredLogSettings::setLogSizeLimit() for details.
 */
constexpr int64_t kDefaultLogSizeLimit = 50ll * 1024ll * 1024ll;

/** The minimum value that can be set for the log size limit in bytes.
 *  See IStructuredLogSettings::setLogSizeLimit() for details.
 */
constexpr int64_t kMinLogSizeLimit = 256ll * 1024ll;

/** The default log retention setting.
 *  See IStructuredLogSettings::setLogRetentionCount() for details.
 */
constexpr size_t kDefaultLogRetentionCount = 3;

/** The minimum allowed log retention setting.
 *  See IStructuredLogSettings::setLogRetentionCount() for details.
 */
constexpr size_t kMinLogRetentionCount = 1;

/** The default value for the event queue size in bytes.
 *  See IStructuredLogSettings::setEventQueueSize() for details.
 */
constexpr size_t kDefaultEventQueueSize = 2 * 1024 * 1024;

/** The minimum allowed event queue size in bytes.
 *  See IStructuredLogSettings::setEventQueueSize() for details.
 */
constexpr size_t kMinEventQueueSize = 512 * 1024;

/** The maximum allowed event queue size in bytes.
 *  See IStructuredLogSettings::setEventQueueSize() for details.
 */
constexpr size_t kMaxEventQueueSize = 1024 * 1024 * 1024;

/** The recommended size for the event queue when log redirection is enabled.  See
 *  IStructuredLogSettings::setEventQueueSize() for details.  See @ref kEnableLogConsumerSetting
 *  and IStructuredLogFromILog::enableLogging() for more information on log redirection.
 */
constexpr size_t kRecommendedLoggingEventQueueSize = 32 * 1024 * 1024;

/** The default mode for generating event IDs.
 *  See IStructuredLogSettings::setEventIdMode() for details.
 */
constexpr IdMode kDefaultIdMode = IdMode::eFastSequential;

/** The default type of event ID to generate.
 *  See IStructuredLogSettings::setEventIdMode() for details.
 */
constexpr IdType kDefaultIdType = IdType::eUuid;

/** Special value to indicate that the heartbeat event should be disabled.  Any other value
 *  will indicate that the heartbeat events will be generated.
 */
constexpr uint64_t kHeartbeatDisabled = 0;

/** The default minimum time between heartbeat events in seconds.  This can be
 *  @ref kHeartbeatDisabled to indicate that the heartbeat events are disabled.  For more
 *  details, please see IStructuredLogSettings2::setHeartbeatPeriod().
 */
constexpr uint64_t kDefaultHeartbeatPeriod = kHeartbeatDisabled;

/** The default state for whether headers will be added to each written log file.  For
 *  more details, please see IStructuredLogSettings2::setNeedsLogHeaders().
 */
constexpr bool kDefaultNeedLogHeaders = true;

/** The default state for whether the CloudEvents wrapper will be output with each message.
 *  By default, all messages will be emitted as CloudEvents 1.0 compliant messages.  The
 *  omni::structuredlog::IStructuredLogSettings2::setOutputFlags() function or the
 *  @ref kEmitPayloadOnlySettings setting can be used to change this setting.
 */
constexpr bool kDefaultEmitPayloadOnlySettings = false;

/** The default state for whether the cloud heartbeat events will be emitted.  For these
 *  events to be emitted, the normal heartbeat event must also be enabled with
 *  @ref kHeartbeatPeriodSetting.  These cloud heartbeat events are effectively duplicate
 *  data and are not strictly necessary.
 */
constexpr bool kDefaultEmitCloudHeartbeat = false;

/** The default mode for how a random user ID is chosen.  This is the same default behavior that
 *  `omni.structuredlog.plugin` itself exhibits when no user ID is given.
 */
constexpr char kDefaultAnonymousUserIdMode[] = "random";

/** The default enable mode for the 'JSON on stdout' feature.  This functionality should only
 *  be enabled if absolutely needed since it will affect multiple other settings across the
 *  structured logging system and the standard logger.  Note that this will also default to
 *  `true` if `/app/coreapi/alpha/enabled` is also enabled.  This will effectively enable
 *  this feature by default for CoreAPI services.
 */
constexpr bool kDefaultEnableJsonStdout = false;

/** The default high water mark for the queue.
 */
constexpr int64_t kDefaultQueueHighWaterMark = 80;
/** @} */

/** Names for various settings that can be used to override some of the default settings.  Note
 *  that these will not override any values that are explicitly set by the host app itself.
 *  @{
 */
/** Global enable/disable for structured logging.  When set to `false`, the structured log system
 *  will be disabled.  This will prevent any event messages from being written out unless the
 *  host app explicitly wants them to.  When set to `true`, the structured log system will be
 *  enabled and event messages will be emitted normally.  This defaults to `false`.
 */
constexpr char kGlobalEnableSetting[] = "/structuredLog/enable";

/** Specifies the directory that log files should be written to.  This is also the directory that
 *  the telemetry transmitter app will check for when enumerating and consuming logs.  This must
 *  always be a local path and may be either absolute or relative.  The default location is
 *  `$HOME/.nvidia-omniverse/logs/` (where ``$HOME`` is ``%USERPROFILE%`` on Windows and the usual
 *  meaning on POSIX platforms).  This setting is mainly intended for testing and the default
 *  directory should be used whenever possible.  If this setting is used in a Kit launch (either
 *  on command line or in a config file), it will be passed on to the telemetry transmitter app
 *  when it gets launched.
 */
constexpr char kLogDirectory[] = "/structuredLog/logDirectory";

/** The default log name to use.  If a default log name is set, all events that do not use the
 *  @ref fEventFlagUseLocalLog flag will write their messages to this log file.  Events that
 *  do use the @ref fEventFlagUseLocalLog flag will write only to their schema's log file.  This
 *  value must be only the log file's name, not including its path.  The logs will always be
 *  created in the structured logging system's current log output path.  As a special case, this
 *  may also be set to either "/dev/stdout" or "/dev/stderr" (on all platforms) to output all
 *  events directly to stdout or stderr respectively.  When one of these log names are used, all
 *  events will be unconditionally written to stdout/stderr regardless of their event or schema
 *  flags.  There will also be no log header written out when events are being sent to stdout or
 *  stderr.  This defaults to an empty string.
 */
constexpr char kDefaultLogNameSetting[] = "/structuredLog/defaultLogName";

/** The setting path for the privacy settings file to load.  This allows the default location of
 *  the privacy settings file to be overridden.  The default location for the privacy settings
 *  file is `$HOME/.nvidia-omniverse/config/privacy.toml` on all platforms, where `$HOME` on
 *  Windows is `%USERPROFILE%).  Note that even if this setting is used and it points to a valid
 *  file, the settings from the default `privacy.toml` file will still be loaded first if it
 *  is present.  The settings in the file specified here will simply override any settings given
 *  in the default file.  This allows any missing settings in the new file to still be provided
 *  by what was present in the default file's location.
 */
constexpr char kPrivacyFileSetting[] = "/structuredLog/privacySettingsFile";

/** The setting path for the log retention count.  This controls how many log files will be
 *  left in the log directory when a log rotation occurs.  When a log file reaches its size
 *  limit, it is renamed and a new empty log with the original name is created.  A rolling
 *  history of the few most recent logs is maintained after a rotation.  This setting controls
 *  exactly how many of each log will be retained after a rotation.  This defaults to 3.
 */
constexpr char kLogRetentionCountSetting[] = "/structuredLog/logRetentionCount";

/** The setting path for the log size limit in megabytes.  When a log file reaches this size,
 *  it is rotated out by renaming it and creating a new log file with the original name.  If
 *  too many logs exist after this rotation, the oldest one is deleted.  This defaults to 50MB.
 */
constexpr char kLogSizeLimitSetting[] = "/structuredLog/logSizeLimit";

/** The setting path for the size of the event queue buffer in kilobytes.  The size of the
 *  event queue controls how many messages can be queued in the message processing queue before
 *  events start to get dropped (or a stall potentially occurs).  The event queue can fill up
 *  if the app is emitting messages from multiple threads at a rate that is higher than they
 *  can be processed or written to disk.  In general, there should not be a situation where
 *  the app is emitting messages at a rate that causes the queue to fill up.  However, this
 *  may be beyond the app's control if (for example) the drive the log is being written to
 *  is particularly slow or extremely busy.  This defaults to 2048KB.
 */
constexpr char kEventQueueSizeSetting[] = "/structuredLog/eventQueueSize";

/** The setting path for the event identifier mode.  This controls how event identifiers are
 *  generated.  Valid values are 'fast-sequential', `sequential`, and `random`.  Each has its
 *  own benefits and drawbacks:
 *    * `sequential` ensures that all generated event IDs are in sequential order.  When the
 *      event ID type is set to `UUID`, this will ensure that each generated event ID can be
 *      easily sorted after the previous one.  With a UUID type ID, this mode can be expensive
 *      to generate.  With a `uint64` ID, this is the most performant to generate.
 *    * `fast-sequential` is only effective when the event ID type is set to 'UUID'.  In this
 *      mode, the UUIDs that are generated are sequential, but in memory order, not lexicographical
 *      order.  It takes some extra effort to sort these events on the data analysis side, but
 *      they are generated very quickly.  When the event ID type is not 'UUID', this mode behaves
 *      in the same way as `sequential`.
 *    * `random` generates a random event ID for each new event.  This does not preserve any
 *      kind of order of events.  If the app does not require sequential events, this can be
 *      more performant to generate especially for UUIDs.
 *
 *  This defaults to 'fast-sequential.  This setting is not case sensitive.
 */
constexpr char kEventIdModeSetting[] = "/structuredLog/eventIdMode";

/** The setting path for the event identifier data type.  This determines what kind of event
 *  ID will be generated for each new event and how it will be printed out with each message.
 *  The following types are supported:
 *    * `UUID` generates a 128 bit universally unique identifier.  The event ID mode determines
 *      how one event ID will be related to the next.  This is printed into each event message
 *      in the standard UUID format ("00000000-0000-0000-0000-000000000000").  This type provides
 *      the most uniqueness and room for scaling in large data sets.
 *    * `uint64` generates a 64 bit integer identifier.  The event ID mode determines how one
 *      event ID will be related to the next.  This is printed into each event message as a
 *      simple decimal integer value.
 *
 *  This defaults to 'UUID'.  This setting is not case sensitive.
 */
constexpr char kEventIdTypeSetting[] = "/structuredLog/eventIdType";

/** The setting path for the log consumer toggle.  This enables or disables the redirection
 *  of normal Carbonite (ie: `CARB_LOG_*()`) and Omni (ie: `OMNI_LOG_*()`) messages as structured
 *  log events as well.  The log messages will still go to their original destination (stdout,
 *  stderr, log file, MSVC output window, etc) as well.  This defaults to `false`.
 */
constexpr char kEnableLogConsumerSetting[] = "/structuredLog/enableLogConsumer";

/** The setting path that will contain zero or more keys that will be used to disable schemas
 *  when they are first registered.  Each key under this setting will have a name that matches
 *  zero or schema names.  From a .schema file, this would match the "name" property.  From a
 *  JSON schema file, this would match the @a `#/schemaMeta/clientName` property.  The key's
 *  value is expected to be a boolean that indicates whether it is enabled upon registration.
 *
 *  The names of the keys under this path may either be a schema's full name or a wildcard
 *  string that matches to zero or more schema names.  In either version, the case of the
 *  non-wildcard portions of the key name is important.  The wildcard characters '*' (match
 *  to zero or more characters) and '?' (match to exactly one character) may be used.  This
 *  is only meant to be a simple wildcard filter, not a full regular expression.
 *
 *  For example, in a TOML file, these settings may be used to disable or enable multiple
 *  schemas:
 *  @rst
    .. code-block:: toml

        [structuredLog.state.schemas]
        "omni.test_schema" = false  # disable 'omni.test_schema' on registration.
        "omni.other_schema" = true  # enable 'omni.other_schema' on registration.
        "carb.*" = false            # disable all schemas starting with 'carb.'.

    @endrst
 *
 *  @note The keys in this setting path are inherently unordered.  If a set of dependent
 *  enable/disable settings is needed, the @ref kSchemasStateArraySetting setting path
 *  should be used instead.  This other setting allows an array to be specified that
 *  preserves the order of keys.  This is useful for doing things like disabling all
 *  schemas then only enabling a select few.
 */
constexpr char kSchemasStateListSetting[] = "/structuredLog/state/schemas";

/** The setting path that will contain zero or more keys that will be used to disable events
 *  when they are first registered.  Each key under this setting will have a name that matches
 *  zero or event names.  From a .schema file, this would match the "namespace" property plus
 *  one of the properties under @a `#/events/`.  From a JSON schema file, this would match one
 *  of the event properties under @a `#/definitions/events/`.  The key's value is expected to
 *  be a boolean that indicates whether it is enabled upon registration.
 *
 *  The names of the keys under this path may either be an event's full name or a wildcard
 *  string that matches to zero or more event names.  In either version, the case of the
 *  non-wildcard portions of the key name is important.  The wildcard characters '*' (match
 *  to zero or more characters) and '?' (match to exactly one character) may be used.  This
 *  is only meant to be a simple wildcard filter, not a full regular expression.
 *
 *  For example, in a TOML file, these settings may be used to disable or enable multiple
 *  events:
 *  @rst
    .. code-block:: toml

        [structuredLog.state.events]
        "com.nvidia.omniverse.fancy_event" = false
        "com.nvidia.carbonite.*" = false            # disable all 'com.nvidia.carbonite' events.

    @endrst
 *
 *  @note The keys in this setting path are inherently unordered.  If a set of dependent
 *  enable/disable settings is needed, the @ref kEventsStateArraySetting setting path
 *  should be used instead.  This other setting allows an array to be specified that
 *  preserves the order of keys.  This is useful for doing things like disabling all
 *  events then only enabling a select few.
 */
constexpr char kEventsStateListSetting[] = "/structuredLog/state/events";

/** The setting path to an array that will contain zero or more values that will be used to
 *  disable or enable schemas when they are first registered.  Each value in this array will
 *  have a name that matches zero or more schema names.  From a .schema file, this would match the
 *  "name" property.  From a JSON schema file, this would match the @a `#/schemaMeta/clientName`
 *  property.  The schema name may be optionally prefixed by either '+' or '-' to enable or
 *  disable (respectively) matching schemas.  Alternatively, the schema's name may be assigned
 *  a boolean value to indicate whether it is enabled or not.  If neither a '+'/'-' prefix nor
 *  a boolean assignment suffix is specified, 'enabled' is assumed.
 *
 *  The names in this array either be a schema's full name or a wildcard string that matches
 *  to zero or more schema names.  In either version, the case of the non-wildcard portions
 *  of the key name is important.  The wildcard characters '*' (match to zero or more characters)
 *  and '?' (match to exactly one character) may be used.  This is only meant to be a simple
 *  wildcard filter, not a full regular expression.
 *
 *  For example, in a TOML file, these settings may be used to disable or enable multiple
 *  schemas:
 *  @rst
    .. code-block:: toml

        structuredLog.schemaStates = [
            "-omni.test_schema",        # disable 'omni.test_schema' on registration.
            "omni.other_schema = true", # enable 'omni.other_schema' on registration.
            "-carb.*"                   # disable all schemas starting with 'carb.'.
        ]

    @endrst
 *
 *  @note TOML does not allow static arrays such as above to be appended to with later lines.
 *  Attempting to do so will result in a parsing error.
 */
constexpr char kSchemasStateArraySetting[] = "/structuredLog/schemaStates";

/** The setting path to an array that will contain zero or more values that will be used to
 *  disable or enable events when they are first registered.  Each value in this array will
 *  have a name that matches zero or more event names.  From a .schema file, this would match one
 *  of the property names under `#/events/`.  From a JSON schema file, this would match one
 *  of the event object names in @a `#/definitions/events/`.  The event name may be optionally
 *  prefixed by either '+' or '-' to enable or disable (respectively) matching event(s).
 *  Alternatively, the event's name may be assigned a boolean value to indicate whether it is
 *  enabled or not.  If neither a '+'/'-' prefix nor a boolean assignment suffix is specified,
 *  'enabled' is assumed.
 *
 *  The names in this array either be an event's full name or a wildcard string that matches
 *  to zero or more event names.  In either version, the case of the non-wildcard portions
 *  of the array entry name is important.  The wildcard characters '*' (match to zero or more characters)
 *  and '?' (match to exactly one character) may be used.  This is only meant to be a simple
 *  wildcard filter, not a full regular expression.
 *
 *  For example, in a TOML file, these settings may be used to disable or enable multiple
 *  schemas:
 *  @rst
    .. code-block:: toml

        structuredLog.schemaStates = [
            "-com.nvidia.omniverse.fancy_event",
            "com.nvidia.carbonite.* = false"            # disable all 'com.nvidia.carbonite' events.
        ]

    @endrst
 *
 *  @note that TOML does not allow static arrays such as above to be appended to with later lines.
 *  Attempting to do so will result in a parsing error.
 */
constexpr char kEventsStateArraySetting[] = "/structuredLog/eventStates";

/** The setting path that will contain the minimum number of seconds between heartbeat events
 *  A heartbeat event is one that is sent periodically to help calculate session lengths even
 *  if the expected 'exit' or 'crash' process lifetime events are missing.  These events can
 *  be missing in such unavoidable cases as a power loss, the user killing the process, a blue
 *  screen of death or kernel panic, etc.  These situations cannot be assumed as either crashes
 *  or normal exits, but at least these events can help indicate how long the actual session was.
 *  This can be set to 0 to disable the heartbeat messages.  By default the heartbeat events are
 *  disabled (ie: set to @ref kHeartbeatDisabled).
 */
constexpr char kHeartbeatPeriodSetting[] = "/structuredLog/heartbeatPeriod";

/** The setting path that will indicate whether headers will be added to each log file that is
 *  written to disk.  Each log file will have one header on the first line that is a JSON object
 *  that indicates the origin of the log and the version of the `omni.structuredlog.plugin`
 *  plugin that created it.  This header object is followed by whitespace to allow it to be
 *  modified later as needed without having to rewrite the entire file.  The telemetry transmitter
 *  consumes this header object and modifies it to indicate its processing progress.  Without
 *  this header, the telemetry transmitter will ignore the log file.  This setting defaults to
 *  `true`.
 */
constexpr char kNeedLogHeadersSetting[] = "/structuredLog/needLogHeaders";

/** The setting path that will indicate whether the CloudEvents wrapper should be added to the
 *  payload of each emitted event.  By default, each event will be emitted as a CloudEvent
 *  compliant JSON object.  If this setting is enabled, the CloudEvent wrapper will be skipped
 *  and only the schema's defined payload for the event will be emitted.  The main payload will
 *  be emitted as the top level object in the JSON output when this setting is enabled.
 *
 *  Note that when this setting is used, the output will be incompatible with the telemetry
 *  transmitter and the rest of the Omniverse telemetry toolchain.  If a host app decides to
 *  use this feature, they will be responsible for including all the relevant information that
 *  would normally be part of the CloudEvents header.  This includes fields such as the user
 *  ID, event type, event schema, event ID, etc.  This setting defaults to `false`.
 */
constexpr char kEmitPayloadOnlySettings[] = "/structuredLog/emitPayloadOnly";

/** The setting path that will indicate whether the cloud heartbeat events will be enabled.
 *  These will only be emitted if the normal heartbeat events are also enabled
 *  (with @ref kHeartbeatPeriodSetting).  These events are effectively duplicate data and
 *  are not strictly necessary.  This defaults to `false`.
 */
constexpr char kEmitCloudHeartbeatSetting[] = "/structuredLog/emitCloudHeartbeat";

/** The settings branch that will be expected to contain zero or more key/value pairs for extra
 *  fields to be added to each output message.  This branch will only be parsed once on startup.
 *  Any extra dynamic fields that need to be added at runtime need to be added or removed
 *  programmatically using the `omni::structuredlog::IStructuredLogExtraFields` interface.
 *  Only string values will be accepted under this branch.  By default this settings branch
 *  is expected to be empty and no extra fields will be added.
 *
 *  Note that the number of extra fields added should be kept to a minimum required count and
 *  size since they can affect both output and transmission performance.
 */
constexpr char kExtraFieldsSettingBranch[] = "/structuredLog/extraFields";

/** The setting path that will indicate which type of anonymous user ID will be used in cases
 *  where no user ID is provided in the `privacy.toml` file or the `privacy.toml` file is missing.
 *  This may be either "random" or "machine".  If it is "random", a completely random user ID will
 *  be chosen.  In this case the user will appear as though it had only ever run a single session
 *  in telemetry data.  If it is "machine", the user ID will be set to an identity derived from
 *  the calling machine's hardware and OS information.  In this case it would be possible to
 *  identify multiple sessions coming from the same user (though no identifying information of
 *  any kind would be present).  The machine ID would be a one-way hash of a large amount of
 *  information about the system the session is run on.  As long as the user runs again on that
 *  same machine it would give the same anonymous user ID.  This setting defaults to "random".
 *
 *  Note that `omni.platforminfo.plugin` must be available in order to generate the machine ID.
 *  If that plugin is not available, the "random" mode will be used instead.  Any value other
 *  than the ones listed above will also fall back to using "random" mode.
 */
constexpr char kAnonymousUserIdModeSetting[] = "/structuredLog/anonymousUserIdMode";

/** The setting path that indicates whether the 'JSON on stdout' functionality is enabled or not.
 *  When enabled, this will disable the standard logger's output to stdout/stderr, enable the log
 *  consumer for `omni.structuredlog.plugin`, and set the structured logging queue size to 32MB.
 *  This should only be enabled when absolutely needed since it can affect how standard log
 *  messages appear on the console/terminal and how they are consumed.  This defaults to false
 *  when not running under a CoreAPI service.  This defaults to true under a CoreAPI service.
 */
constexpr char kEnableJsonStdoutSetting[] = "/structuredLog/enableJsonStdout";

/** This sets the point where omni.structuredlog will decide that the queue is overfilled and will
 *  automatically increase the queue size.
 *  This is represented as a percent of the queue that's full, so a setting of 70 will cause the
 *  queue to resize when it's more than 70% full.
 *  By default, this is 80.
 *  This can be set to 0 or a negative number to disable this feature.
 */
constexpr char kQueueHighWaterMark[] = "/structuredLog/queueHighWaterMark";

/** This is the path for settings tree that contains the set of schemas or wildcards to set the
 *  maximum allowable throughput measured in bytes per second.
 *  If no throughput limit is set, the maximum throughput is unlimited.
 *
 *  The throughput limit works by totalling up the number of bytes emitted within the current time
 *  period. Once the next message will exceed the throughput limit within a given period, that
 *  message is discarded. Messages can be sent again once the period is over.
 *
 *
 *  @rst
    .. code-block:: toml

        structuredLog.limits.throughput = [
            "omni.other_schema = 65536", # limit omni.other_schema to 64KB / second
            "carb.* = 1048576"           # limit carb schemas to 1MB / second
        ]

    @endrst
 *
 */
constexpr char kSchemasThroughputLimitsSetting[] = "/structuredLog/limits/throughput";

/** This is the path for settings tree that contains the set of schemas or wildcards to set the
 *  time period (in milliseconds) for the throughput limits defined by @ref kSchemasThroughputLimitsSetting.
 *
 *  Rate limiting is done where the sum of one second worth of time windows cannot exceed the rate
 *  limit. For example, assuming the throughput limit is 64KiB bytes and the period is 1000ms, if
 *  64KiB is sent in the first 100ms, all messages will be discarded for the next 900ms. If the
 *  period was instead 250ms, messages would be discarded for the next 150ms, then each 250ms
 *  window would allow an additional 16KiB to be sent. This allows the throughput over 1 second to
 *  exceed the limit (up to 2x in the most extreme case), but the average over a long period of
 *  time will be below the limit.
 *
 *  Because structuredlog flushes messages asynchronously, setting a very small period may not have
 *  an effect. By default structuredlog flushes messages every 100ms unless the queue is heavily
 *  loaded, so window sizes below 100ms may effectively act as 100ms windows.
 *
 *  This must be between 1ms and 1000ms.
 *  The default value is 100ms.
 *
 *  @rst
    .. code-block:: toml

        structuredLog.limits.period = [
            "omni.other_schema = 200", # set omni.other_schema to use a 200ms period.
            "carb.* = 500"             # set carb schemas to a 500ms period.
        ]

    @endrst
 *
 */
constexpr char kSchemasThroughputPeriodSetting[] = "/structuredLog/limits/throughputPeriod";
/** @} */


/** Enables or disables the structured logging log message redirection.
 *
 *  @param[in] enabled  Set to ``true`` to enable structured logging log message redirection.
 *                      Set to ``false`` to disable structured logging log message redirection.
 *  @returns ``true`` if logging redirection was successfully enabled.  Returns ``false``
 *           otherwise
 *
 *  This enables or disables structured logging log message redirection.  This system
 *  will monitor log messages and emit them as structured log messages.
 */
inline bool setStructuredLogLoggingEnabled(bool enabled = true)
{
    omni::core::ObjectPtr<IStructuredLog> strucLog;
    omni::core::ObjectPtr<IStructuredLogFromILog> log;


    strucLog = omni::core::borrow(omniGetStructuredLogWithoutAcquire());

    if (strucLog.get() == nullptr)
        return false;

    log = strucLog.as<IStructuredLogFromILog>();

    if (log.get() == nullptr)
        return false;

    if (enabled)
        log->enableLogging();

    else
        log->disableLogging();

    return true;
}

/** Checks the settings registry for structured log settings and makes them active.
 *
 *  @param[in] settings     The settings interface to use to retrieve configuration values.
 *                          This may not be `nullptr`.
 *  @returns No return value.
 *
 *  @remarks This sets appropriate default values for all the structured log related settings then
 *           attempts to retrieve their current values and set them as active.  This assumes
 *           that the settings hive has already been loaded from disk and made active in the
 *           main settings registry.
 *
 *  @thread_safety This call is thread safe.
 */
inline void configureStructuredLogging(carb::settings::ISettings* settings)
{
    omni::core::ObjectPtr<IStructuredLog> strucLog;
    omni::core::ObjectPtr<IStructuredLogSettings> ts;
    omni::core::ObjectPtr<IStructuredLogSettings2> ts2;
    omni::core::ObjectPtr<IStructuredLogSettings3> ts3;
    omni::core::ObjectPtr<IStructuredLogFromILog> log;
    omni::core::ObjectPtr<IStructuredLogExtraFields> extraFields;
    carb::cpp::optional<std::string> value;
    int64_t count;
    size_t queueSize;
    IdMode idMode = kDefaultIdMode;
    IdType idType = kDefaultIdType;


    if (settings == nullptr)
        return;

    // ****** set appropriate defaults for each setting ******
    settings->setDefaultBool(kGlobalEnableSetting, false);
    settings->setDefaultString(kLogDirectory, "");
    settings->setDefaultString(kDefaultLogNameSetting, "");
    settings->setDefaultInt64(kLogRetentionCountSetting, kDefaultLogRetentionCount);
    settings->setDefaultInt64(kLogSizeLimitSetting, kDefaultLogSizeLimit / 1048576);
    settings->setDefaultInt64(kEventQueueSizeSetting, kDefaultEventQueueSize / 1024);
    settings->setDefaultString(kEventIdModeSetting, "fast-sequential");
    settings->setDefaultString(kEventIdTypeSetting, "UUID");
    settings->setDefaultBool(kEnableLogConsumerSetting, false);
    settings->setDefaultInt64(kHeartbeatPeriodSetting, kDefaultHeartbeatPeriod);
    settings->setDefaultBool(kNeedLogHeadersSetting, kDefaultNeedLogHeaders);
    settings->setDefaultBool(kEmitPayloadOnlySettings, kDefaultEmitPayloadOnlySettings);
    settings->setDefaultBool(kEmitCloudHeartbeatSetting, kDefaultEmitCloudHeartbeat);
    settings->setDefaultString(kAnonymousUserIdModeSetting, kDefaultAnonymousUserIdMode);

    if (settings->getAsBool("/app/coreapi/alpha/enabled"))
        settings->setDefaultBool(kEnableJsonStdoutSetting, true);

    else
        settings->setDefaultBool(kEnableJsonStdoutSetting, kDefaultEnableJsonStdout);


    // ****** grab the structured log settings object so the config can be set ******
    strucLog = omni::core::borrow(omniGetStructuredLogWithoutAcquire());

    if (strucLog.get() == nullptr)
        return;

    ts = strucLog.as<IStructuredLogSettings>();

    if (ts.get() == nullptr)
        return;


    // ****** retrieve the settings and make them active ******
    strucLog->setEnabled(omni::structuredlog::kBadEventId, omni::structuredlog::fEnableFlagAll,
                         settings->getAsBool(kGlobalEnableSetting));

    // set the default log name.
    value = carb::settings::getStringOpt(settings, kDefaultLogNameSetting);

    if (value && !value->empty())
        ts->setLogDefaultName(value->c_str());

    value = carb::settings::getStringOpt(settings, kLogDirectory);

    if (value && !value->empty())
    {
        ts->setLogOutputPath(value->c_str());
    }
    else
    {
        // This setting needs to be reloaded after ISerializer has been loaded, since it can read
        // omniverse.toml now in case there are overrides there.
        extras::OmniConfig config;
        ts->setLogOutputPath(config.getBaseLogsPath().c_str());
    }

    // set the log retention count.
    count = settings->getAsInt64(kLogRetentionCountSetting);
    ts->setLogRetentionCount((size_t)count);

    // set the log size limit.
    count = settings->getAsInt64(kLogSizeLimitSetting);
    ts->setLogSizeLimit(count * 1048576);

    // set the event queue size (given in KB in the setting).
    queueSize = (size_t)settings->getAsInt64(kEventQueueSizeSetting);
    ts->setEventQueueSize(queueSize * 1024);

    // set the event ID mode.
    value = carb::settings::getStringOpt(settings, kEventIdModeSetting);

    if (carb::extras::compareStringsNoCase(value->c_str(), "fast-sequential") == 0)
        idMode = IdMode::eFastSequential;

    else if (carb::extras::compareStringsNoCase(value->c_str(), "sequential") == 0)
        idMode = IdMode::eSequential;

    else if (carb::extras::compareStringsNoCase(value->c_str(), "random") == 0)
        idMode = IdMode::eRandom;

    else
        OMNI_LOG_WARN("unknown event ID mode '%s'.  Assuming 'fast-sequential'.", value->c_str());

    // set the event ID type.
    value = carb::settings::getStringOpt(settings, kEventIdTypeSetting);

    if (carb::extras::compareStringsNoCase(value->c_str(), "UUID") == 0)
        idType = IdType::eUuid;

    else if (carb::extras::compareStringsNoCase(value->c_str(), "uint64") == 0)
        idType = IdType::eUint64;

    else
        OMNI_LOG_WARN("unknown event ID type '%s'.  Assuming 'UUID'.", value->c_str());

    ts->setEventIdMode(idMode, idType);

    // load the privacy settings and set the user ID from it.
    ts->loadPrivacySettings();

    // load the enable states for each schema and event.
    ts->enableSchemasFromSettings();

    // retrieve and set the user ID if present.
    std::string uid = omni::extras::PrivacySettings::getUserIdString();

    if (!uid.empty())
        ts->setUserId(uid.c_str());

    else
    {
        carb::cpp::optional<std::string> mode = carb::settings::getStringOpt(settings, kAnonymousUserIdModeSetting);

        if (mode && carb::extras::compareStringsNoCase(mode->c_str(), "machine") == 0)
        {
            auto os2 = omni::core::createType<omni::platforminfo::IOsInfo2>();

            if (os2 != nullptr)
            {
                uint64_t id = os2->getMachineId();

                if (id != 0)
                {
                    ts->setUserId(std::to_string(id).c_str());
                }
            }
        }
    }

    // setup the structured log logger.  Note that if this is enabled on the command line
    // this will also implicitly increase the event queue's buffer size.
    log = strucLog.as<IStructuredLogFromILog>();

    if (log.get() == nullptr)
        return;

    if (settings->getAsBool(kEnableLogConsumerSetting))
    {
        log->enableLogging();
        ts->setEventQueueSize(CARB_MAX(kRecommendedLoggingEventQueueSize, queueSize * 1024));
    }

    // setup the default heartbeat event period.
    ts2 = strucLog.as<IStructuredLogSettings2>();

    if (ts2 != nullptr)
    {
        OutputFlags flags = fOutputFlagNone;

        count = settings->getAsInt64(kHeartbeatPeriodSetting);
        ts2->setHeartbeatPeriod((size_t)count);

        if (!settings->getAsBool(kNeedLogHeadersSetting))
            flags |= fOutputFlagSkipLogHeaders;

        if (settings->getAsBool(kEmitPayloadOnlySettings))
            flags |= fOutputFlagPayloadOnly;

        if (settings->getAsBool(kEmitCloudHeartbeatSetting))
            flags |= fOutputFlagEmitCloudHeartbeat;

        ts2->setOutputFlags(flags, 0);
    }

    extraFields = strucLog.as<IStructuredLogExtraFields>();

    if (extraFields != nullptr)
    {
        // walk through the extra fields branch of the settings registry and add an extra field
        // for each key/value pair in there.  In general we don't expect there to be more than
        // a couple extra fields present.
        carb::settings::ScopedRead readLock;
        if (settings->isAccessibleAs(carb::dictionary::ItemType::eDictionary, kExtraFieldsSettingBranch))
        {
            carb::dictionary::IDictionary* dictionary = carb::getCachedInterface<carb::dictionary::IDictionary>();
            const carb::dictionary::Item* branch = settings->getSettingsDictionary(kExtraFieldsSettingBranch);
            size_t childCount = dictionary->getItemChildCount(branch);

            for (size_t i = 0; i < childCount; i++)
            {
                const carb::dictionary::Item* item = dictionary->getItemChildByIndex(branch, i);

                if (item == nullptr)
                    continue;

                const char* key = dictionary->getItemName(item);
                const char* val = dictionary->getStringBuffer(item);

                if (key != nullptr && val != nullptr)
                {
                    extraFields->setValue(key, val, omni::structuredlog::fExtraFieldFlagNone);
                }
            }
        }
    }

    // settings requested that 'JSON logging' be used => enable the various settings related
    //   to setting this mode.  JSON logging mode outputs all log messages to stdout (unbuffered)
    //   formatted as JSON events.  It also silences the stdout/stderr output of the standard
    //   logger so that log messages are not doubled up in different formats on stdout.  Each
    //   log message will still be output to all other destinations (ie: debug console, log
    //   file(s), etc).
    if (log != nullptr && ts != nullptr && settings->getAsBool(kEnableJsonStdoutSetting))
    {
        auto log2 = strucLog.as<IStructuredLogFromILog2>();

        if (log2 != nullptr)
        {
            auto logging = carb::getFramework()->tryAcquireInterface<carb::logging::ILogging>();

            if (logging != nullptr)
            {
                auto standardLogger = logging->getDefaultLogger();

                if (standardLogger != nullptr)
                {
                    standardLogger->setStandardStreamOutput(false);
                }
            }

            // enable structured logging for at least the log consumer event since it is now
            // needed in order for log messages to be output.  The structured logging system
            // also needs to be globally enabled for this to take effect.
            strucLog->setEnabled(omni::structuredlog::kBadEventId, omni::structuredlog::fEnableFlagAll, true);
            strucLog->setEnabled(log->getLoggingEventId(), omni::structuredlog::fEnableFlagWholeSchema, true);
            settings->setBool(kGlobalEnableSetting, true);

            // enable the log consumer and set its destination to only stdout.
            log->enableLogging();
            log2->setLoggingEventFlags(
                omni::structuredlog::fEventFlagOutputToStdout | omni::structuredlog::fEventFlagSkipLog, 0);

            // make sure the log consumer respects the standard output stream log level.  This
            // log level further filters log messages that make it through to consumers but don't
            // then make it to the standard streams under the standard logger.
            log2->setLogLevel(
                carb::logging::stringToLevel(carb::settings::getString(settings, "/log/outputStreamLevel").c_str()));

            // increase the queue size.  If we're going to be serving all log messages through the
            // structured log queue, the queue's buffer needs to be large enough to ensure a
            // potentially large amount of concurrent message traffic can safely go through it.
            // With each message being anywhere from 200 bytes to upwards of 3KB (depending on
            // content), not that many messages will fit in the default buffer size of 2MB.
            // If a lot of message traffic suddenly occurs very quickly, the queue's buffer
            // could fill up and start either dropping messages or blocking threads until
            // space is available.
            size_t userSize = queueSize;

            userSize = CARB_MAX(userSize, omni::structuredlog::kRecommendedLoggingEventQueueSize);
            ts->setEventQueueSize(userSize);
        }
    }

    ts3 = strucLog.as<IStructuredLogSettings3>();

    if (ts3 != nullptr)
    {
        ts3->settingsLoadComplete();
    }

    strucLog.release();
}

} // namespace structuredlog
} // namespace omni
