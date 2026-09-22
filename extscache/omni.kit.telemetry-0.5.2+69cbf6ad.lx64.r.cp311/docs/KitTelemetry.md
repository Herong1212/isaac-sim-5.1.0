# Configuring the `omni.kit.telemetry` Extension

## Overview

The `omni.kit.telemetry` extension is responsible for a few major tasks.  These largely occur in the background
and require no direct interaction from the rest of the app.  All of this behavior occurs during the startup of
the extension automatically.  The major tasks that occur during extension startup are:

* Launch the telemetry transmitter app.  This app is shipped with the extension and is responsible for parsing,
  validating, and transmitting all structured log messages produced by the app.  Only the specific messages that
  have been approved and validated will be transmitted.  More on this below.
* Collect system information and emit structured log messages and crash reporter metadata values for it.  The
  collected system information includes CPU, memory, OS, GPU, and display information.  Only information about
  the capabilities of the system is collected, never any user specific information.
* Emit various startup events.  This includes events that identify the run environment being used (ie:
  cloud/enterprise/individual, cloud node/cluster name, etc), the name and version of the app, the various
  session IDs (ie: telemetry, launcher, cloud, etc), and the point at which the app is ready for the user to
  interact with it.
* Provide interfaces that allow some limited access to information about the session.  The `omni::telemetry::ITelemetry`
  and `omni::telemetry::ITelemetry2` interfaces can be used to access this information.  These interfaces are
  read-only for the most part.

Once the extension has successfully started up, it is generally not interacted with again for the duration of the
app's session.


## The Telemetry Transmitter

The telemetry transmitter is a separate app that is bundled with the `omni.kit.telemetry` extension.  It is
launched during the extension's startup.  For the most part the configuration of the transmitter is automatic.
However, its configuration can be affected by passing specific settings to the Kit based app itself.  In general,
any settings under the `/telemetry/` settings branch will be passed directly on to the transmitter when it is
launched.  There are some settings that may be slightly adjusted or added to however depending on the launch mode.
The transmitter process will also inherit any settings under the `/log/` (with a few exceptions) and
`/structuredLog/extraFields/` settings branches.

In almost all cases, the transmitter process will be unique in the system.  At any given time, only a single
instance of the transmitter process will be running.  If another instance of the transmitter is launched while
another one is running, the new instance will immediately exit.  This single instance of the transmitter will
however handle events produced by all Kit based apps, even if multiple apps are running simultaneously.  This
limitation can be overcome by specifying a new launch guard name with the `/telemetry/launchGuardName` setting,
but is not recommended without also including additional configuration changes for the transmitter such as the
log folder to be scanned.  Having multiple transmitters running simultaneously could result in duplicate messages
being sent and more contention on accessing log files.

When the transmitter is successfully launched, it will keep track of how many Kit based apps have attempted to
launch it.  The transmitter will continue to run until all Kit based apps that tried to launch it have exited.
This is true regardless of how each Kit based app exits - whether through a normal exit, crashing, or being
terminated by the user.  The only cases where the transmitter will exit early will be if it detects that
another instance is already running, and if it detects that the user has not given any consent to transmit
any data.  In the latter case, the transmitter exits because it has no job to perform without user consent.

When the transmitter is run with authentication enabled (ie: the `/telemetry/transmitter/0/authenticate=true`
or `/telemetry/authenticate=true` settings), it requires a way to deliver the authentication token to it.
This is usually provided by downloading a JSON file from a certain configurable URL.  The authentication token
may arrive with an expiry time.  The transmitter will request a renewed authentication token only once the
expiry time has passed.  The authentication token is never stored locally in a file by the transmitter.
If the transmitter is unable to acquire an authentication token for any reason (ie: URL not available,
attempt to download the token failed or was rejected, etc), that endpoint in the transmitter will simply pause
its event processing queue until a valid authentication token can be acquired.

When the transmitter starts up, it performs the following checks:

* Reads the current privacy consent settings for the user.  These settings are found in the `privacy.toml`
  file that the Kit based app loaded on startup.  By default this file is located in `~/.nvidia-omniverse/config/privacy.toml`
  but can be relocated for a session using the `/structuredLog/privacySettingsFile` setting.
* Loads its configuration settings and builds all the requested transmission profiles.  The same set of parsed,
  validated events can be sent to multiple endpoints if the transmitter is configured to do so.
* Downloads the appropriate approved schemas package for the current telemetry mode.  Each schema in the package
  is then loaded and validated.  Information about each event in each schema is then stored internally.
* Parses out the extra fields passed to it.  Each of the named extra fields will be added to each validated
  message before it is transmitted.
* In newer versions of the transmitter (v0.5.0 and later), the list of current schema IDs is downloaded and
  parsed if running in 'open endpoint' mode (ie: authentication is off and the `schemaid` extra field is
  passed on to it).  This is used to set the latest value for the `schemaid` field.
* Outputs its startup settings to its log file.  Depending on how the Kit based app is launched, this log file
  defaults to either `${kit}/logs/` or `~/.nvidia-omniverse/logs/`.  The default name for the log file is
  `omni.telemetry.transmitter.log`.

While the transmitter is running, it repeatedly performs the following operations:

* Scans the log directory for new structured log messages.  If no new messages are found, the transmitter will
  sleep for one minute (by default) before trying again.
* All new messages that are found are then validated against the set of loaded events.  Any message that fails
  validation (ie: not formatted correctly or its event type isn't present in the approved events list) will
  simply be dropped and not transmitted.
* Send the set of new approved, validated events to each of the requested endpoints.  The transmitter will
  remove any endpoint that repeatedly fails to be contacted but continue doing its job for all other endpoints.
  If all endpoints are removed, the transmitter will simply exit.
* Update the progress tags for each endpoint in each log file to indicate how far into the log file it has
  successfully processed and transmitted.  If the transmitter exits and the log files persist, the next run
  will simply pick off where it left off.
* Check whether the transmitter should exit.  This can occur if all of the launching Kit based apps have exited
  or if all endpoints have been removed due to them being unreachable.


## Anonymous Data Mode

An anonymous data mode is also supported for Omniverse telemetry.  This guarantees that all user information
is cleared out, if loaded, very early on startup.  Enabling this also enables open endpoint usage, and sets
the transmitter to 'production' mode.  All consent levels will also be enabled once a random user ID is
chosen for the session.  This mode is enabled using the `/telemetry/enableAnonymousData` setting (boolean).

For more information, please see the [Anonymous Data Mode documentation](http://omniverse-docs.s3-website-us-east-1.amazonaws.com/carbonite/168.0-pre/docs/structuredlog/OmniTelemetry.html#anonymous-data-mode).


## Configuration Options Available to the `omni.kit.telemetry` Extension

The `omni.kit.telemetry` will do its best to automatically detect the mode that it should run in.  However,
sometimes an app can be run in a setting where the correct mode cannot be accurately detected.  In these cases
the extension will just fall back to its default mode.  The current mode can be explicitly chosen using the
`/telemetry/mode` setting.  However, some choices of mode (ie: 'test') may not function properly without
the correct build of the extension and transmitter.  The extension can run in the following modes:

* `Production`: Only transmits events that are approved for public users.  Internal-only events will only
  be emitted to local log files and will not be transmitted anywhere.  The default transmission endpoint
  is Kratos (public).  This is the default mode.
* `Developer`: Transmits events that are approved for both public users and internal users.  The default
  transmission endpoints are Kratos (public) and NVDF (internal only).
* `Test`: Send only locally defined test events.  This mode is typically only used for early iterative
  testing purposes during development.  This mode in the transmitter allows locally defined schemas to be
  provided.  The default transmission endpoints are Kratos (public) and NVDF (internal only).

The extension also detects the 'run environment' it is in as best it can.  This detection cannot be
overridden by a setting.  The current run environment can be retrieved with the
`omni::telemetry::ITelemetry2::getRunEnvironment()` function (C++) or the
`omni.telemetry.ITelemetry2().run_environment` property (python).  The following run environments are
detected and supported:

* `Individual`: This is the default mode.  This launches the transmitter in its default mode as well
  (ie: `production` unless otherwise specified).  If consent is given, all generated and approved
  telemetry events will be sent to both Kratos (public) and NVDF (internal only).  This mode requires
  that the user be logged into the Omniverse Launcher app since it provides the authentication
  information that the public data endpoint requires.  If the Omniverse Launcher is not running,
  data transmission will just be paused until the Launcher app is running.  This mode is chosen only
  if no others are detected.  This run environment is typically picked for individual users who
  install their Omniverse apps through the desktop Omniverse Launcher app.  This run environment is
  referred to as "OVI".
* `Cloud`: This launches the transmitter in 'cloud' mode.  In this mode the final output from the
  transmitter is not sent anywhere, but rather written to a local file on disk.  The intent is that
  another log consumer service will monitor for changes on this log file and consume events as they
  become available.  This allows more control over which data is ingested and how that data is
  ingested.  This run environment is typically launched through the Omniverse Cloud cockpit web
  portal and is referred to as "OVC".
* `Enterprise`: This launches the transmitter in 'enterprise' mode.  In this mode, data is sent
  to an open endpoint data collector.  No authentication is needed in this mode.  The data coming
  in does however get validated before storing.  This run environment is typically detected
  when using the Omniverse Enterprise Launcher app to install or launch the Kit based app.  This
  run environment is referred to as "OVE".


Many of the [structured logging and telemetry settings](http://omniverse-docs.s3-website-us-east-1.amazonaws.com/carbonite/167.0/docs/structuredlog/OmniTelemetry.html#configuration-options>)
that come from the Carbonite components of the telemetry system also affect how the `omni.kit.telemetry`
extension starts up.  Some of the more useful settings that affect this are listed below.  Other
settings listed in the above Carbonite documentation can be referred to for additional information.

The following settings can control the startup behavior of the `omni.kit.telemetry` extension,
the transmitter launch, and structured logging for the app:

* Settings used for configuring the transmitter to use an open endpoint:

  * `/structuredLog/privacySettingsFile`: Sets the location of the privacy settings TOML file.
    This setting should only be used when configuring an app in a container to use a special
    privacy settings file instead of the default one.  The default location and name for this
    file is `~/.nvidia-omniverse/config/privacy.toml`.  This setting is undefined by default.
  * `/telemetry/openTestEndpointUrl`: Sets the URL to use as the test mode open endpoint URL
    for the transmitter.  This value is specified in the extension's configuration files and
    may override anything given on the command line or other global config files.
  * `/telemetry/openEndpointUrl`: Sets the URL to use as the dev or production mode open
    endpoint URL for the transmitter.  This value is specified in the extension's configuration
    files and may override anything given on the command line or other global config files.
  * `/telemetry/enterpriseOpenTestEndpointUrl`: Sets the URL to use as the test mode open
    endpoint URL for OVE for the transmitter.  This value is specified in the extension's
    configuration files and may override anything given on the command line or other global
    config files.
  * `/telemetry/enterpriseOpenEndpointUrl`: Sets the URL to use as the dev or production mode
    open endpoint URL for OVE for the transmitter.  This value is specified in the extension's
    configuration files and may override anything given on the command line or other global
    config files.
  * `/telemetry/useOpenEndpoint`: Boolean value to explicitly launch the transmitter in
    'open endpoint' mode.  This will configure the transmitter to set its endpoint to the
    Kratos open endpoint URL for the current telemetry mode and run environment.  In most
    cases this setting and ensuring that the privacy settings are provided by the user are
    enough to successfully launch the transmitter in open endpoint mode.  This defaults to
    `false`.
  * `/telemetry/enableAnonymousData`: Boolean value to override several other telemetry, privacy,
    and endpoint settings.  This will clear out all user information settings (both in the
    settings registry and cached in the running process), choose a random user ID for the session,
    enable all consent levels, enable `/telemetry/useOpenEndpoint`, and clear out `/telemetry/mode`
    so that only production mode events can be used.  This also affects how the telemetry
    transmitter is launched when the `omni.kit.telemetry` extension starts up.

* Settings to help control logging (structured or otherwise) in the transmitter:

  * `/telemetry/log/level`: Sets the logging level that will be passed on to the transmitter.
    This allows the transmitter to be given a different logging level than the Kit based app
    was launched with.  This defaults to `warning`.  This is useful for debugging telemetry
    transmitter issues without having to also increase the default logging level in the
    rest of the Kit based app.
  * `/telemetry/log/file`: Sets the logging output filename that will be passed on to the
    transmitter.  This allows the transmitter to be given a different log output file than
    was requested for the Kit based app.  This defaults to `omni.telemetry.transmitter.log`
    in the structured log system's log directory (defaults to `~/.nvidia-omniverse/logs/`)
    but can be overridden to point to the `${kit}/logs/` directory when the app is run in
    'portable' mode or from a local developer build.
  * Any other `/log/` settings passed to the Kit based app with the exception of
    `/log/enableStandardStreamOutput`, `/log/file`, and `/log/level` will be inherited
    by the transmitter when it is launched.
  * Any settings under the `/structuredLog/extraFields/` branch will be passed along to
    the transmitter unmodified.
  * Any settings under the `/telemetry/` branch will be passed along to the transmitter
    unmodified.
  * The `/structuredLog/privacySettingsFile` setting will be passed along to the
    transmitter if it is specified for the Kit based app.  If not, the various privacy
    consent settings will be passed on individually.  Note that the transmitter may
    still override these privacy settings if it detects a `privacy.toml` file in the
    expected location.
  * The `/structuredLog/logDirectory` setting will be passed on to the transmitter if
    explicitly given to the Kit based app.
  * `/telemetry/testLogFile`: Specifies the path to the special log file to use to
    output some additional information from the transmitter.  This log file does not
    get created by the Carbonite logging system nor does it use its settings.  This
    file provides some extra diagnostic information from the transmitter unaffected by
    the normal logging system.  This defaults to disabling the test log.

* Settings that control telemetry destination behavior:

  * `/telemetry/enableNVDF`: For OVI run environments, this boolean setting controls
    whether the NVDF (internal only) endpoint will be added to the transmitter during
    its launch.  For other run environments or for OVI run environments using the open
    endpoint, this is ignored.  This is enabled by default.
  * `/telemetry/nvdfTestEndpoint`: A boolean setting used to specify whether the
    'test' or 'production' NVDF (internal only) endpoint should be used.  This setting
    is only used if `/telemetry/enableNVDF` is also enabled and being used in the OVI
    run environment.  This defaults to `false`.
  * `/telemetry/endpoint`: Overrides the default public endpoint to use in the
    transmitter.  This setting is ignored in the OVE run environment and when using
    an open endpoint.  This defaults to an empty string.
  * `/telemetry/cloudLogEndpoint`: Allows the default endpoint to use for OVC to be
    overridden.  This is expected to be a local file URI the points to the file that
    the transmitter's final output will be written to.  This setting is ignored unless
    the current run environment is OVC.  This defaults to `file:///${omni_logs}/kit.transmitter.out.log`.
    Note that this file URI must either set the server name to `localhost` or leave
    it blank (implying `localhost`).  A common point of confusion with local file
    URIs is in the number of slashes after the `file://` tag.  In general, a file URI
    is of the form `file://<host>/<local_path>` where `<host>` is the server name
    (ie: must be `localhost` or nothing in this case), and `<local_path>` is the
    absolute file path on the given host system.  On Windows this ends up being
    something similar to `file:///c:/path/to/file.txt`.  On POSIX systems however,
    since absolute paths always start with a slash ('/'), this ends up being something
    similar to `file:////path/to/file.txt`.

* Settings to control the extension's startup behavior:

  * `/exts/omni.kit.telemetry/skipDeferredStartup`: Boolean setting to allow
    the extension's various startup tasks to be run serially instead of in
    parallel.  This is often needed for unit test purposes to guarantee that
    all of the startup tasks have completed before the extension's tests start
    to run.  If enabled, this will cause the extension to take slightly longer
    to startup (should still be less than 2s in almost all cases).  This defaults
    to `false`.

* Settings specific to the OVC run environment:

  * `/cloud/cluster`: String setting that specifies the name of the cluster the
    session will run on.  This is expected to be provided by the OVC app launch
    system.  This defaults to an empty string.
  * `/cloud/node`: String setting that specifies the name of the node that the
    session will run on.  This is expected to be provided by the OVC app launch
    system.  This defaults to an empty string.
  * `/telemetry/extraFieldsToAdd`: String setting that specifies which of the extra fields
    under `/structuredLog/extraFields/` that are inherited by the telemetry transmitter on
    launch should be automatically added to each message by the transmitter.  This is expected
    to be a comma separated list of key names in the `/structuredLog/extraFields/` settings
    branch.  Note that there should not be any whitespace in this setting's value otherwise
    some platforms such as Windows could parse it incorrectly.  Any keys names in this list
    that do not exist as extra fields passed to the transmitter will simply be ignored.  This
    defaults to an empty string.

    Note that if this setting is present and contains the `schemaid` field name, the transmitter
    will automatically retrieve and add the correct schema ID value to each message that is
    sent.  This automatic behavior also requires the `/telemetry/runEnvironment` setting
    however to correctly determine which schema ID to use.
  * `/telemetry/runEnvironment`: String setting that specifies the run environment that the
    `omni.kit.telemetry` extension has detected.  This is automatically passed on to the
    telemetry transmitter when running in open-endpoint mode.


## Crash Reporter Metadata

The `omni.kit.telemetry` extension will set or modify several crash reporter metadata values
during its startup.  Unless otherwise noted, each of these metadata values will be created by
the extension.  The following metadata values are managed by this extension:

* `environmentName`: This metadata value is originally set by Kit-kernel, but can be modified
  by `omni.kit.telemetry` if it is left at the value `default`.  In this case, its value
  will be replaced by the current detected run environment - one of `Individual`, `Enterprise`,
  or `Cloud`.
* `runEnvironment`: Contains the current detected run environment - one of `Individual`,
  `Enterprise`, or `Cloud`.  This value is added to explicitly include the run environment
  name even in cases where `environmentName` is set to something else by Kit-kernel.
* `externalBuild`: Set to `true` if the current Kit app is being run by an external (ie: public)
  user or has not been detected as an internal-only session.  Set to `false` if an internal
  user or session has been detected.
* `launcherSessionId`: If the OVI launcher app is currently running in the system, this value is
  set to the session ID for the launcher.
* `cloudPodSessionId`: If in the OVC run environment, this will contain the cloud session ID.
* `cpuName`: The friendly name of the system's main CPU.
* `cpuId`: The internal ID of the system's main CPU.
* `cpuVendor`: The name of the system's main CPU vendor.
* `osName`: The friendly name of the operating system.
* `osDistro`: The distribution name of the operating system.
* `osVersion`: The detailed version number or code of the operating system.
* `primaryDisplayRes`: The resolution of the system's primary display (if any).
* `desktopSize`: The size of the entire system desktop for the current user.
* `desktopOrigin`: The top-left origin point of the desktop window.  On some systems this may just
  be (0, 0), but others such as Windows allow for negative origin points.
* `displayCount`: The number of attached displays (if any).
* `displayRes_<n>`: The current resolution in pixels of the n-th display.
* `gpu_<n>`: The name of the n-th GPU attached to the system.
* `gpuVRAM_<n>`: The amount of video memory the n-th GPU attached to the system has.
* `gpuDriver_<n>`: The active driver version for the n-th GPU attached to the system.
