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
 *  @brief Utilities for uploading telemetry events.
 */
#pragma once

#include "IStructuredLogSettings.h"
#include "../extras/UniqueApp.h"
#include "../../carb/launcher/ILauncher.h"
#include "../../carb/launcher/LauncherUtils.h"
#include "../../carb/settings/ISettings.h"

namespace omni
{
namespace telemetry
{

/** Telemetry transmitter app settings.  These control the behavior of the transmitter
 *  app.  They can be specified either on the command line (prefixed by '--'), or in
 *  the transmitter app's config file (`omni.telemetry.transmitter.toml`).
 *  @{
 */
/** This setting will cause the transmitter to stay alive until it is manually killed.
 *  This setting is mostly meant for developer use, but could also be used in server
 *  or farm environments where Omniverse apps are frequently run and exited.  This will
 *  bypass the normal exit condition check of testing whether all apps that tried to
 *  launch the transmitter have exited on their own.  When this option is disabled,
 *  once all apps have exited, the transmitter will exit on its own.  When this option
 *  is enabled, this exit condition will simply be ignored.  This defaults to `false`.
 *
 *  Note that if no schemas are available for the transmitter to process, this option
 *  is ignored.  In that case, the transmitter will simply exit immediately after
 *  trying to download the schemas package.
 *
 *  @note This setting is ignored if @ref kUploadAllAndExitSetting is set to `true`.
 */
constexpr char kStayAliveSetting[] = "/telemetry/stayAlive";

/** When this setting is set to true, it will cause the transmitter to try to
 *  upload all the events that are currently stored and exit once there are no
 *  remaining events.
 *
 *  This is used in tests and use cases where the transmitter is run as a one-shot
 *  operation after a given process has exited.
 *
 *  This defaults to `false`.
 *
 *  @note This setting overrides the behavior of @ref kStayAliveSetting when enabled.
 */
constexpr char kUploadAllAndExitSetting[] = "/telemetry/uploadAllAndExit";

/** The time, in seconds, that the transmitter will wait between polling the log files.
 *  This determines how reactive the transmitter will be to checking for new messages and
 *  how much work it potentially does in the background.  This defaults to 60 seconds.
 */
constexpr char kPollTimeSetting[] = "/telemetry/pollTime";


/** The mode to run the transmitter in.  The value of this setting can be "prod", "dev" or "test".
 *  By default, the transmitter will run in "production" mode.  In "dev" mode, the transmitter
 *  will use the default development schemas URL.  In "test" mode, the default staging endpoint
 *  URL will be used.  The "test" mode is only supported in debug builds.  If "test" is used
 *  in a release build, it will be ignored and the production endpoint will be used instead.
 *
 *  Note that if the schemas package for the requested mode is empty, the transmitter will
 *  just immediately exit since there is nothing for it to process.
 *
 *  This will also apply a "(dev)" or "(test)" tag onto the source of structured log messages when
 *  in "dev" and "test" mode, respectively.
 *
 *  @note This setting is only applied on startup and changing it later into the process will have
 *        no effect. Use @ref structuredlog::IStructuredLogSettings3 to change tagging if needed.
 */
constexpr char kTelemetryModeSetting[] = "/telemetry/mode";

/** This can be used to apply the "(dev)" and "(test)" source tags onto structured log messages
 *  without applying the other behavior of @ref kTelemetryModeSetting.
 *
 *  If @ref kTelemetryModeSetting is set to a valid value, it will take precedence over this setting.
 *
 *  @note This setting is only applied on startup and changing it later into the process will have
 *        no effect. Use @ref structuredlog::IStructuredLogSettings3 for this if needed.
 */
constexpr char kTelemetryTagSetting[] = "/telemetry/modeTag";

/** Setting to enable an anonymous data telemetry mode.  Setting this to `true` has a number of
 *  side effects that would affect the telemetry behavior for the entire process and potentially
 *  even other running Omniverse apps' processes (since all concurrently running apps share a
 *  single telemetry transmitter instance).  The side effects include:
 *    * Clearing out all user and login information that may have been cached from the
 *      `privacy.toml` file.  This includes settings like`/privacy/userId`, `/privacy/idpId`,
 *      `/privacy/idpName`, `/privacy/email`, etc.
 *    * Forcing all consent levels to be enabled.
 *    * Disabling any dev-only output.
 *    * Ensuring production mode will be used for all structured log nessage output and for the
 *      telemetry transmitter.
 *    * Setting the user ID to the same random number that selected on app startup.
 *    * Enabling open-endpoint mode for the telemetry transmitter launch.
 *
 *  All of these settings changes are made both in all internally cached locations for the
 *  information, and in non-persistant parts of the settings registry itself.  This is
 *  done so that any other system that may query those settings would also correctly pick
 *  up on the anonymous data mode change.  This setting defaults to `false`.
 *
 *  @note Since this setting has a potential reach beyond the behavior of just the current
 *        process, care should be taken in using it.  Using this setting is ideal for container
 *        situations where only a single app would be running with a single transmitter working
 *        out of a non-shared log directory.
 *
 *  @note Also note that enabling this setting will result in the setting the user ID with
 *        omni::structuredlog::IStructuredLogSettings::setUserId() being prevented.  This is
 *        to prevent a non-anonymous user ID from being set by another system and incorrectly
 *        or inadvertently introducing PII into what should otherwise be anonymous data.
 */
constexpr char kTelemetryEnableAnonymousDataSetting[] = "/telemetry/enableAnonymousData";

/** Environment variable name that allows the @ref kTelemetryEnableAnonymousDataSetting setting to
 *  be overridden externally.  This is intended to provide way to opt-out of anonymous telemetry
 *  for containerized apps if they are configured to opt-in by default.  This environment variable
 *  is intended to be set inside the container at container launch time.  Setting this to a
 *  boolean convertable value such as '1', 't', 'T', 'y', or 'Y' will override the behavior
 *  of the @ref kTelemetryEnableAnonymousDataSetting setting.  Setting it to any other value will
 *  allow any configured value of the setting to take effect.  Effectively, with the anonymous
 *  data feature overridden with this variable, the telemetry system will fall back to its default
 *  behavior of expecting the privacy consent and user ID settings in the `privacy.toml` file.  If
 *  those are missing (as should be in the containerized case), that will disable transmission of
 *  any locally generated telemetry events.
 */
constexpr char kTelemetryDisableAnonymousDataEnvvar[] = "OMNI_TELEMETRY_DISABLE_ANONYMOUS_DATA";

/** Sets the run environment that determines which flavor of Kit is currently being run.
 *  This should be either `Individual` (for OVI), `Cloud` (for OVC), or `Enterprise` (for
 *  OVE).  This helps to choose the appropriate schema ID when automatically adding the
 *  `schemaid` field to messages being sent to an open endpoint.
 */
constexpr char kTelemetryRunEnvironmentSetting[] = "/telemetry/runEnvironment";

/** This allows the transmitter to run as the root user on Linux.
 *  The root user is disabled by default because it could make some of the transmitter's
 *  files non-writable by regular users.  By default, if the transmitter is launched as
 *  the root user or with `sudo`, it will report an error and exit immediately.  If it is
 *  intended to launch as the root or super user, this option must be explicitly specified
 *  so that there is a clear intention from the user.  The default value is `false`.  This
 *  setting is ignored on Windows.
 */
constexpr char kAllowRootSetting[] = "/telemetry/allowRoot";

/** The list of restricted regions for the transmitter.  If the transmitter is launched
 *  in one of these regions, it will exit immediately on startup.  The entries in this
 *  list are either the country names or the two-letter ISO 3166-1 alpha-2 country code.
 *  Entries in the list are separated by commas (','), bars ('|'), slash ('/'), or whitespace.
 *  Whitespace should not be used when specifying the option on the command line.  It is
 *  typically best to use the two-letter country codes in the list since they are standardized.
 *  This defaults to an empty list.
 */
constexpr char kRestrictedRegionsSetting[] = "/telemetry/restrictedRegions";

/** The assumption of success or failure that should be assumed if the country name and code
 *  could not be retrieved.  Set this to `true` if the transmitter should be allowed to run
 *  if the country code or name could not be retrieved.  Set this to `false` if the transmitter
 *  should not be allowed to run in that error case.  This defaults to `true`.
 */
constexpr char kRestrictedRegionAssumptionSetting[] = "/telemetry/restrictedRegionAssumption";

/** The log file path that will be used for any transmitter processes launched.
 *  If it is not specified, the log path from @ref omni::structuredlog::IStructuredLogSettings::getLogOutputPath()
 *  will be used; If @ref omni::structuredlog::IStructuredLogSettings could not be acquired for
 *  some reason, the CWD will be used.
 */
constexpr char kLogFileSetting[] = "/telemetry/log/file";

/** The log level that will be used for any transmitter process launched.
 *  If this is not specified, the parent process's log level will be used.
 */
constexpr char kLogLevelSetting[] = "/telemetry/log/level";

/** This allows the telemetry transmitter to be launched in an 'open endpoint' mode.  This will
 *  point it to one of the Kratos open endpoint URLs, disable authentication, and set the event
 *  processing protocol to "defaultWithList" (normally set with the `/telemetry/transmitter/0/eventProtocol`
 *  setting).  This mode may only be used when the `/telemetry/extraFields/schemaid` value is
 *  also properly setup and the rest of the app has been properly configured for use with an
 *  open endpoint.  Without a proper configuration, all events will be rejected from the open
 *  endpoint.
 */
constexpr char kUseOpenEndpointSetting[] = "/telemetry/useOpenEndpoint";

/** This allows only a subset of the extra fields specified under `/structuredLog/extraFields/`
 *  to be passed on to the transmitter when it is launched.  By default all extra fields specified
 *  under `/structuredLog/extraFields/` will be passed on to the transmitter to use, but will be
 *  ignored by the transmitter.  If a subset of those extra fields should be automatically added
 *  to each message by the transmitter, they can be added to this setting's value in a single
 *  comma separated list in a string.  Any whitespace in the string will be ignored.  If this
 *  setting is undefined or contains an empty string, no extra fields will be automatically added
 *  to each message.
 */
constexpr char kExtraFieldsToAddSetting[] = "/telemetry/extraFieldsToAdd";

/** This controls whether the extra fields specified in @ref kExtraFieldsToAddSetting will be
 *  replaced in each message if one or more of them already exists or if any fields that already
 *  exist in the event will just be ignored.  When set to `true`, the listed extra fields with
 *  their given values will always overwrite any existing fields with the same name.  When set
 *  to `false`, if a field with the same name as one of the extra fields already exists in a
 *  given event message, it will not be replaced.  The default behavior is to never overwrite
 *  existing fields (ie: set to `false`).
 */
constexpr char kReplaceExtraFieldsSetting[] = "/telemetry/replaceExtraFields";

/** This allows the name of the transmitter launch guard to be changed from its default.  This
 *  launch guard controls whether a new instance of the telemetry transmitter can be launched
 *  at any given time.  Each unique launch guard name allows for an independent unique transmitter
 *  instance to be run even if another instance using a different guard name is already running.
 *  This defaults to "omni.telemetry.transmitter".  This should only be used for testing purposes
 *  and to allow for a different transmitter to run in the system as long as it is not looking at
 *  the same log directory as any other concurrently running instance of the transmitter.
 */
constexpr char kLaunchGuardNameSetting[] = "/telemetry/launchGuardName";


/** This settings key holds an object or an array of objects.
 *  Each object is one transmitter instance.
 *  In the settings JSON, this would look something like:
 *  @code{JSON}
 *  {
 *      "telemetry": {
 *          "transmitter": [
 *              {
 *                  "endpoint": "https://telemetry.not-a-real-url.nvidia.com",
 *              },
 *              {
 *                  "endpoint": "https://metrics.also-not-a-real-url.nvidia.com"
 *              }
 *          ]
 *      }
 *  }
 *  @endcode
 *  You can also specify this on command line like this.
 *  You must ensure that all entries under `/telemetry/transmitter` are contiguous numeric indices
 *  otherwise `/telemetry/transmitter` will be interpreted as a single object.
 *  @code{bash}
 *  "--/telemetry/transmitter/0/endpoint=https://omniverse.kratos-telemetry.nvidia.com" \
 *  "--/telemetry/transmitter/1/endpoint=https://gpuwa.nvidia.com/dataflow/sandbox-jfeather-omniverse/posting"
 *  @endcode
 *  A transmitter instance sends data to a telemetry endpoint with a specific
 *  configuration.
 *  Each instance can be configured to use a different protocol and a different
 *  set of schema URLs, so data sent to each endpoint can be substantially different.
 *  To send data to multiple endpoints, you set up an array of objects under
 *  this settings key.
 *  Note that
 */
constexpr char kTransmitterSetting[] = "/telemetry/transmitter";

/** This setting is an optional member of the @ref kTransmitterSetting object.
 *  If this is set to `true`, the transmitter will ignore the `seek` field in the header
 *  and start parsing from the start of each log again.  This is only intended to be used
 *  for testing purposes.  This defaults to `false`.
 */
constexpr char kResendEventsSettingLeaf[] = "resendEvents";

/** This setting is an optional member of the @ref kTransmitterSetting object.
 *  The maximum number of bytes to send in one transmission to the server.  Event messages
 *  will be sent in batches as large as possible up to this size.  If more message data is
 *  available than this limit, it will be broken up into multiple transmission units.  This
 *  must be less than or equal to the transmission limit of the endpoint the messages are
 *  being sent to.  If this is larger than the server's limit, large message buffers will
 *  simply be rejected and dropped.  This defaults to 5MB.
 */
constexpr char kTransmissionLimitSettingLeaf[] = "transmissionLimit";

/** This setting is an optional member of the @ref kTransmitterSetting object.
 *  This sets the maximum number of messages to process in a single pass on this transmitter.
 *  The transmitter will stop processing log messages and start to upload messages when it
 *  has found, validated, processed, and queued at most this number of messages on any given
 *  transmitter object.  Only validated and queued messages will count toward this limit.
 *  This limit paired with @ref kTransmissionLimitSettingLeaf helps to limit how much of any
 *  log file is processed and transmitted at any given point.  This defaults to 10000 messages.
 */
constexpr char kQueueLimitSettingLeaf[] = "queueLimit";

/** This setting is an optional member of the @ref kTransmitterSetting object.
 *  Sets the URL to send the telemetry events to.  This can be used to send the events to a
 *  custom endpoint.  This will override the default URL inferred by @ref kTelemetryModeSetting.
 *  By default, the @ref kTelemetryModeSetting setting will determine the endpoint URL to use.
 *  You can set this as an array if you want to specify multiple fallback endpoints
 *  to use if the retry limit is exhausted; each endpoint will be tried in order
 *  and will be abandoned if connectivity fails after the retry limit.
 *
 *  This may also be a file URI if the output is to be written to a local log file.  In this case,
 *  this must be a "file:///" style URI since only local files are supported (ie: no server or
 *  host name component).  This file URI may also point to the special paths `/dev/stdout` or
 *  `/dev/stderr` (ie: as "file:///dev/stdout") to output to stdout or stderr respectively
 *  (supported on all platforms).  When a local file or stdout/stderr is used as the destination
 *  endpoint, all newly processed events will simply be appended to the end of the log file.
 *  Exclusive write access to the local log file is expected while the transmitter is running.
 *  The transmitter will lock the file (except stdout and stderr) while writing to it, but will
 *  close the log after each write.  If another process needs to read from it, advisory locking
 *  should be used to guarantee the contents are not in a partial state.  On Windows, this locking
 *  should be done using one of the `LockFile*()` functions.  On Posix platforms that support file
 *  locking, this should be done using either `fcntl(f, F_SETLKW, ...)` for a blocking lock or
 *  `fcntl(f, F_SETLK, ...)` for a non-blocking lock.  Each line in the log file will represent
 *  a single output event.
 *
 *  @note Writing the transmitter output to a log file is only supported with the 'default'
 *        and `defaultWithStringify` output protocols @ref kEventProtocolLeaf.  If another
 *        event protocol is used, it will be reverted to `default` instead.  A warning message
 *        will be output in this case.
 *
 *  @note When outputting data to a file instead of a server URL, authentication will be
 *        implicitly disabled since it is not needed.  If the file URI should ever fail and
 *        be removed from the transmitter (unlikely except in situations where for example the
 *        device is full), the original specified state of the authentication flag will be
 *        restored.  In almost all situations, there is no need to authenticate with anything
 *        when writing a local file.  Leaving authentication enabled (the default behavior) would
 *        just lead to that transmitter object simply sitting idle if the authentication
 *        information could not be downloaded.  The authentication can be disabled using the
 *        @ref kTelemetryAuthenticateSettingLeaf setting.
 */
constexpr char kTelemetryEndpointSettingLeaf[] = "endpoint";

/** This setting is an optional member of the @ref kTransmitterSetting object.
 *  This specifies the URL or URLs to download approved schemas from.  This may be used to
 *  override the default URL and the one specified by @ref kTelemetryModeSetting.  This may
 *  be treated either as a single URL string value or as an array of URL strings.  The usage
 *  depends on how the setting is specified by the user or config.  If an array of URLs is
 *  given, they are assumed to be in priority order starting with the first as the highest
 *  priority URL.  The first one that successfully downloads will be used as the schema
 *  package.  The others are considered to be backup URLs.  This defaults to the Omniverse
 *  production schemas URL.
 *
 *  @note In debug builds, this schemas package URL may also point to a local file.  This
 *        may be specified in both the single string and array forms of this setting.  The
 *        local file URI may be in the `file://` scheme form or as just a local (absolute)
 *        or relative) filename.
 */
constexpr char kTelemetrySchemasUrlSettingLeaf[] = "schemasUrl";

/** This setting is an optional member of the @ref kTransmitterSetting object.
 *  This specifies that authentication should be enabled when sending event messages to the
 *  telemetry endpoint.  When disabled, this will prevent the auth token from being retrieved
 *  from the Omniverse Launcher app.  This should be used in situations where the Omniverse
 *  Launcher app is not running or an endpoint that does not need or expect authorization is
 *  used.  If this is not used and the auth token cannot be retrieved from the Launcher app, the
 *  transmitter will go into an idle mode where nothing is processed or sent.  This mode is
 *  expecting the Launcher app to become available at some future point.  Setting this option
 *  to `false` will disable the authentication checks and just attempt to push the events to
 *  the specified telemetry endpoint URL.  Note that the default endpoint URL will not work
 *  if this option is used since it expected authentication.  The default value is `true`.
 */
constexpr char kTelemetryAuthenticateSettingLeaf[] = "authenticate";

/** This setting is an optional member of the @ref kTransmitterSetting object.
 *  This specifies the URL to download the authentication token from.  This option will be
 *  ignored if @ref kTelemetryAuthenticateSettingLeaf is `false`.  A file will be expected to
 *  be downloaded from this URL.  The downloaded file is expected to be JSON formatted and
 *  is expected to contain the authentication token in the format that the authentication
 *  server expects.  The name of the data property in the file that contains the actual
 *  token to be sent with each message is specified in @ref kTelemetryAuthTokenKeyNameSettingLeaf.
 *  The data property in the file that contains the token's expiry date is specified in
 *  @ref kTelemetryAuthTokenExpiryNameSettingLeaf.  Alternatively, this setting may also point
 *  to a file on disk (either with the 'file://' protocol or by naming the file directly).
 *  If a file on disk is named, it is assumed to either be JSON formatted and also contain
 *  the token data and expiry under the same key names as given with
 *  @ref kTelemetryAuthTokenKeyNameSettingLeaf and @ref kTelemetryAuthTokenExpiryNameSettingLeaf,
 *  or it will be a file whose entire contents will be the token itself.  The latter mode
 *  is only used when the @ref kTelemetryAuthTokenKeyNameSettingLeaf setting is an empty string.
 *  By default, the URL for the Omniverse Launcher's authentication web API will be used.
 */
constexpr char kTelemetryAuthTokenUrlSettingLeaf[] = "authTokenUrl";

/** This setting is an optional member of the @ref kTransmitterSetting object.
 *  This specifies the name of the key in the downloaded authentication token's JSON data
 *  that contains the actual token data to be sent with each set of uploaded messages.
 *  This option will be ignored if @ref kTelemetryAuthenticateSettingLeaf is `false`.
 *  This must be in the format that the authentication server expects.  The token data
 *  itself can be any length, but is expected to be string data in the JSON file.  The
 *  key is looked up in a case sensitive manner.  This defaults to "idToken".
 */
constexpr char kTelemetryAuthTokenKeyNameSettingLeaf[] = "authTokenKeyName";

/** This setting is an optional member of the @ref kTransmitterSetting object.
 *  This specifies the name of the key in the downloaded authentication token's JSON data
 *  that contains the optional expiry date for the token.  This option will be ignored if
 *  @ref kTelemetryAuthenticateSettingLeaf is `false`.If this property exists, it will be used
 *  to predict when the token should be retrieved again.  If this property does not exist,
 *  the token will only be retrieved again if sending a message results in a failure due
 *  to a permission error.  This property is expected to be string data in the JSON
 *  file.  Its contents must be formatted as an RFC3339 date/time string.  This defaults to
 *  "expires".
 */
constexpr char kTelemetryAuthTokenExpiryNameSettingLeaf[] = "authTokenExpiryName";

/** This setting is an optional member of the @ref kTransmitterSetting object.
 *  What serialization protocol is being used by the transmitter.
 *  This can be set to one of three possible (case-insensitive) values:
 *    - "default":  This is the default protocol.  The event will not be modified from its
 *                  original generated format and content.  This includes leaving the `data`
 *                  field as a nested JSON object.  This will send events in batches (as many
 *                  as are available at the time) to the server with each JSON event separated
 *                  by a newline (aka JSON lines format).
 *    - "defaultWithStringify": This sends batches of events at a time to the server with each
 *                  JSON event separated by a newline (aka JSON lines format).  Structuredlog
 *                  event format is largely left as-is; the only change is that the `data`
 *                  field's object is stringified.  This is the only difference between this
 *                  protocol and the `default` protocol above.
 *    - "NVDF":     This is also a batch serialization protocol, except that the event property
 *                  names are modified to follow the expectations of the server.
 *                  This flattens each event's `data` payload into the event base.
 *                  The `time` field is renamed to `ts_created` and its format
 *                  is changed to a *nix epoch time in milliseconds.
 *                  The `id` field is renamed to `_id`.
 *                  All data fields are also prefixed in a Hungarian-notation
 *                  style system.
 */
constexpr char kEventProtocolLeaf[] = "eventProtocol";

/** This setting is an optional member of the @ref kTransmitterSetting object.
 *  The tag name that will be used to record how much of the file was processed.
 *  Unless `kResendEventsSetting` is set to `true`, the seek tags are used to
 *  tell the transmitter how much of the log has been processed so far so that
 *  it won't try to send old events again.
 *  The default value of this is "seek".
 *  You may want to change the seek tag name if you need to send data to multiple
 *  telemetry endpoints with separate transmitter processes.
 *
 *  @note The telemetry log files have a 256 byte header.
 *        Each seek tag will add 13 bytes to the header + the length of the tag
 *        name.
 *        When the log header space is exhausted, the header will not be updated,
 *        which is equivalent to having `kResendEventsSetting` is set to `true`.
 *        Please avoid long tag names to avoid this risk.
 */
constexpr char kSeekTagNameLeaf[] = "seekTagName";

/** This setting is an optional member of the @ref kTransmitterSetting object.
 *  This specifies the expected type of the authentication token.  This can be any of
 *  "auto", "jwt", or "api-key".  By default this is set to "auto" and will attempt to
 *  detect the type of authentication token based on where the @ref kTelemetryAuthTokenUrlSettingLeaf
 *  setting points.  If the value points to a URL, a JWT will be assumed.  If the value points
 *  to a file on disk or directly contains the token itself, a long-lived API key will be assumed.
 *  If an alternate storage method is needed but the assumed type doesn't match the actual
 *  token type, this setting can be used to override the auto detection.  The default value is
 *  "auto".  This setting will be ignored if @ref kTelemetryAuthenticateSettingLeaf is set to false.
 */
constexpr char kTelemetryAuthTokenTypeLeaf[] = "authTokenType";

/** This setting is an optional member of the @ref kTransmitterSetting object.
 *  The number of days before the current time where events in a log start to be considered old.
 *  When set to 0 (and this setting isn't overridden on a per-schema or per-event level), all
 *  events are processed as normal and no events are considered old.  When set to a non-zero
 *  value, any events that are found to be older than this number of days will be processed
 *  differently depending on the flags specified globally (@ref kIgnoreOldEventsSettingLeaf and
 *  @ref kPseudonymizeOldEventsSettingLeaf), at the schema level (``fSchemaFlagIgnoreOldEvents``
 *  and ``fSchemaFlagPseudonymizeOldEvents``), and at the event level (``fEventFlagIgnoreOldEvents``
 *  and ``fEventFlagPseudonymizeOldEvents``).  If no special flags are given, the default
 *  behavior is to anonymize old events before transmitting them.  This will only override the
 *  old events threshold given at the schema (``#/oldEventsThreshold``) or event
 *  (``#/events/<eventName>/oldEventsThreshold``) if it is a smaller non-zero value than the
 *  values given at the lower levels.  This defaults to 0 days (ie: disables checking for 'old'
 *  events).
 */
constexpr char kOldEventThresholdSettingLeaf[] = "oldEventThreshold";

/** This setting is an optional member of the @ref kTransmitterSetting object.
 *  Flag to indicate that when an old event is detected, it should simply be discarded instead
 *  of being anonymized or pseudonymized before transmission.  This is useful if processing
 *  old events is not interesting for analysis or if transmitting an old event will violate a
 *  data retention policy.  An event is considered old if it is beyond the 'old events threshold'
 *  (see @ref kOldEventThresholdSettingLeaf).  By default, old events will be anonymized before being
 *  transmitted.  If this flag is set here at the global level, it will override any old event
 *  settings from the schema and event levels.
 */
constexpr char kIgnoreOldEventsSettingLeaf[] = "ignoreOldEvents";

/** This setting is an optional member of the @ref kTransmitterSetting object.
 *  Flag to indicate that when an old event is detected, it should be pseudonymized instead of
 *  anonymized before transmission.  This setting is ignored for any given event if the
 *  @ref kIgnoreOldEventsSettingLeaf setting, ``fSchemaFlagIgnoreOldEvents`` flag, or
 *  ``fEventFlagIgnoreOldEvents`` flag is used for that event.  When not specified, the default
 *  behavior is to anonymize old events before transmission.
 */
constexpr char kPseudonymizeOldEventsSettingLeaf[] = "pseudonymizeOldEvents";

/** This setting is an optional member of the @ref kTransmitterSetting object.
 *  The number of attempts to transmit data that will be made before giving up.
 *  This can be set to -1 to retry forever.  If sending events to the current
 *  endpoint for this transmitter object fails, it will be retried up to this
 *  many times.  If a send completes successfully, the retry counter will be
 *  reset.  If too many retries fail, the current endpoint will be removed from
 *  this transmitter object.  If the last endpoint was removed, the entire
 *  transmitter object will be removed for the remainder of the session.  A
 *  future session that is configured in the same manner will allow the transmissions
 *  to be retried again.  This defaults to 10.
 */
constexpr char kRetryLimitSettingLeaf[] = "retryLimit";

/** This setting is an optional member of the @ref kTransmitterSetting object.
 *  This controls which messages will be considered by the transmitter and
 *  which will be filtered out before validating against a schema.  This is
 *  intended to match each message's transmission mode against the mode that
 *  the transmitter is currently running in.  This value can be one of the
 *  following:
 *   * "all": allow all messages to be validated against schemas.
 *   * "matching": allow messages whose source mode matches the transmitter's
 *          current run mode.
 *   * "matching+": allow messages whose source mode matches the transmitter's
 *          current run mode or higher.
 *   * "test": only consider messages from the 'test' source mode.
 *   * "dev": only consider messages from the 'dev' source mode.
 *   * "prod": only consider messages from the 'prod' source mode.
 *   * "dev,prod" (or other combinations): only consider messages from the listed
 *          source modes.
 *
 *  This defaults to "all".  This setting value may be used either on a
 *  per-transmitter basis when using multiple transmitters, or it may be used in
 *  the legacy setting `/telemetry/messageMatchMode`.  If both the legacy and the
 *  per-transmitter setting are present, the per-transmitter ones will always
 *  override the legacy setting.
 *
 *  @note Setting this to a value other than "all" would result in certain messages
 *        not being transmitted because they were rejected during a previous run and
 *        were skipped over in the log.  It is intended that if this setting is used
 *        for a given transmitter, it is likely to be used with that same matching
 *        mode most often on any given machine.  Note that multiple transmitters with
 *        different matching modes can also be used.
 */
constexpr char kMessageMatchingModeLeaf[] = "messageMatchMode";
/** @} */


/** Create a guard with the standard name and path for the transmitter.
 *  @returns A UniqueApp guard that is used to let the transmitter know when
 *           it should exit on its own.  Telemetry clients should use this to
 *           'connect' to the transmitter (note that this does not require the
 *           transmitter to be running yet). See launchTransmitter() for an
 *           example usage.
 *  @remarks This guard is needed by all telemetry clients to let the transmitter
 *           know when all clients have shut down so it can exit as well.
 */
inline extras::UniqueApp createGuard()
{
    carb::settings::ISettings* settings;
    const char* guardName = "omni.telemetry.transmitter";
    std::string value;
    auto getGuardPath = []() -> std::string {
#if OMNI_PLATFORM_LINUX
        // XDG_RUNTIME_DIR is the standard place for putting runtime IPC objects on Linux
        const char* runDir = getenv("XDG_RUNTIME_DIR");
        if (runDir != nullptr)
        {
            return runDir;
        }
#endif

        core::ObjectPtr<omni::structuredlog::IStructuredLog> strucLog;
        core::ObjectPtr<omni::structuredlog::IStructuredLogSettings> settings;

        strucLog = omni::core::borrow(omniGetStructuredLogWithoutAcquire());
        if (strucLog.get() == nullptr)
        {
            OMNI_LOG_ERROR("failed to get IStructuredLog");
            return "";
        }

        settings = strucLog.as<structuredlog::IStructuredLogSettings>();
        if (settings.get() == nullptr)
        {
            OMNI_LOG_ERROR("failed to get IStructuredLogSettings");
            return "";
        }

        return settings->getLogOutputPath();
    };

    settings = carb::getCachedInterface<carb::settings::ISettings>();

    if (settings != nullptr && settings->isAccessibleAs(carb::dictionary::ItemType::eString, kLaunchGuardNameSetting))
    {
        value = carb::settings::getString(settings, kLaunchGuardNameSetting, guardName);
        guardName = value.c_str();
    }

    return extras::UniqueApp(getGuardPath().c_str(), guardName);
}

/** Determine the directory where the logs of a launched transmitter process should go.
 *  @returns The log output directory.
 */
inline std::string getTransmitterLogPath()
{
    constexpr char kLogFileFallback[] = "./omni.telemetry.transmitter.log";
    carb::settings::ISettings* settings = carb::getFramework()->tryAcquireInterface<carb::settings::ISettings>();
    core::ObjectPtr<omni::structuredlog::IStructuredLog> strucLog =
        omni::core::borrow(omniGetStructuredLogWithoutAcquire());
    core::ObjectPtr<omni::structuredlog::IStructuredLogSettings> strucLogSettings;

    if (settings != nullptr)
    {
        settings->setDefaultString(kLogFileSetting, "");
        carb::cpp::optional<std::string> logFile = carb::settings::getStringOpt(settings, kLogFileSetting);
        if (logFile && !logFile->empty())
            return *logFile;
    }
    else
    {
        CARB_LOG_ERROR("failed to acquire ISettings");
    }

    if (strucLog.get() == nullptr)
    {
        OMNI_LOG_ERROR("failed to get IStructuredLog - using CWD");
        return kLogFileFallback;
    }

    strucLogSettings = strucLog.as<structuredlog::IStructuredLogSettings>();
    if (strucLogSettings.get() == nullptr)
    {
        OMNI_LOG_ERROR("failed to get IStructuredLogSettings - using CWD for the log file");
        return kLogFileFallback;
    }

    return std::string(strucLogSettings->getLogOutputPath()) + "/omni.telemetry.transmitter.log";
}

/** Launch the telemetry transmitter process.
 *  @param[in] transmitterPath The path to the transmitter binary and .py file.
 *  @param[in] extraArgs Extra arguments to pass to the transmitter process.
 *  @returns `true` if the transmitter child process is successfully launched.
 *           Returns `false` otherwise.
 *
 *  @remarks This function will launch an instance of the telemetry transmitter.
 *           Any app using telemetry should launch the transmitter.
 *           The transmitter process will upload telemetry events from the logs
 *           to the Kratos endpoint.
 *           The transmitter is currently dependent on the Omniverse Launcher to
 *           obtain an authentication token to send telemetry.
 *           Only one transmitter process will exist on a system at a time; if
 *           one is launched while another exists, the new instance will exit.
 *           The transmitter process will run until all telemetry client
 *           processes have exited.
 *
 *  @note The `/telemetry/log` tree of settings exists to specify log options for
 *        the transmitter without affecting the parent process.
 *         - `/telemetry/log/file` is passed to the transmitter as `/log/file'.
 *         - `/telemetry/log/level` is passed to the transmitter as `/log/level'.
 *
 *  @note This transmitter process won't log to the standard streams by default.
 *        Logs will go to a standard log file path instead, but `--/log/file` can
 *        be used to override this.
 *        The transmitter process will exit after the host app, so logging to
 *        the standard streams will result in messages being written into terminal
 *        over the user's prompt.
 */
inline bool launchTransmitter(const char* transmitterPath, const std::vector<std::string> extraArgs = {})
{
#if OMNI_PLATFORM_WINDOWS
    const char* ext = ".exe";
#else
    const char* ext = "";
#endif
    carb::launcher::ILauncher* launcher = carb::getFramework()->tryAcquireInterface<carb::launcher::ILauncher>();
    carb::settings::ISettings* settings = carb::getFramework()->tryAcquireInterface<carb::settings::ISettings>();
    extras::UniqueApp guard = createGuard();
    carb::launcher::ArgCollector args;
    carb::launcher::EnvCollector env;
    carb::launcher::LaunchDesc desc = {};
    size_t envCount;

    if (launcher == nullptr)
    {
        OMNI_LOG_ERROR("failed to acquire ILauncher");
        return false;
    }


    guard.connectClientProcess();

    args.format("%s/omni.telemetry.transmitter%s", transmitterPath, ext);

    args.add("/telemetry", "--/", carb::launcher::fSettingsEnumFlagRecursive);
    args.add("/structuredLog/extraFields", "--/", 0);
    args.add("/log", "--/", carb::launcher::fSettingsEnumFlagRecursive, [](const char* path, void* ctx) {
        CARB_UNUSED(ctx);
        return strcmp(path, "/log/enableStandardStreamOutput") != 0 && strcmp(path, "/log/file") != 0 &&
               strcmp(path, "/log/level") != 0;
    });

    // output will not go to the standard streams because it's annoying if
    // output goes to your terminal after your process finishes and there is no
    // way to ensure the transmitter shuts down before your process
    args.add("--/log/enableStandardStreamOutput=false");

    args.format("--/log/file=%s", getTransmitterLogPath().c_str());

    if (settings == nullptr)
    {
        OMNI_LOG_ERROR("failed to acquire ISettings");
    }
    else
    {
        settings->setDefaultString(kLogLevelSetting, "");
        carb::cpp::optional<std::string> logLevel = carb::settings::getStringOpt(settings, kLogLevelSetting);
        if (logLevel && !logLevel->empty())
        {
            args.format("--/log/level=%s", logLevel->c_str());
        }
        else
        {
            logLevel = carb::settings::getStringOpt(settings, "/log/level");
            if (logLevel && !logLevel->empty())
            {
                args.format("--/log/level=%s", logLevel->c_str());
            }
        }
    }

    for (const std::string& arg : extraArgs)
    {
        args.add(arg);
    }

    // add the parent environment but remove the `CARB_APP_PATH` and `CARB_APP_NAME` variables
    // since they will negatively affect the behaviour of the transmitter.  Note that since
    // we're explicitly adding the full parent environment here and just subtracting some
    // variables, we need to also use the `fLaunchFlagNoInheritEnv` flag when launching the
    // child process so that ILauncher doesn't implicitly add them back.
    env.add();
    envCount = env.getCount();
    env.remove("CARB_APP_PATH");
    env.remove("CARB_APP_NAME");

    if (env.getCount() != envCount)
    {
        desc.flags |= carb::launcher::fLaunchFlagAllowBadEnv | carb::launcher::fLaunchFlagNoInheritEnv;
        desc.env = env.getEnv();
        desc.envCount = env.getCount();
    }

    desc.argv = args.getArgs(&desc.argc);
    desc.flags |= carb::launcher::fLaunchFlagNoStdStreams;

    return launcher->launchProcessDetached(desc) != carb::launcher::kBadId;
}


} // namespace telemetry
} // namespace omni
