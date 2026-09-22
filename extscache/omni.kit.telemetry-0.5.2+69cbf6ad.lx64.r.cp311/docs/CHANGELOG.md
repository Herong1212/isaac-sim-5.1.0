# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.5.2] - 2025-05-01
### Changed
- Prepare for Python-3.12

## [0.5.1] - 2024-09-27

### Changed
-
- Changed the way that user PII is hidden by using a UUID instead of a session ID.

## [0.5.0] - 2024-04-15

### Added

- Added the setting `/telemetry/enableAnonymousData` to enable a mode where anonymous data will be produced and transmitted
  to the NV open teleemtry endpoint.  When enabled, all user information in the settings registry and cached in the process
  will be cleared out and replaced by a randomly generated user ID.  The `/telemetry/useOpenEndpoint` setting will also
  be enabled and the `/telemetry/mode` setting will be cleared so that only production mode is used.  This mode guarantees
  that no information about a real user or their location will be emitted as telemetry.

## [0.5.0] - 2023-09-29

### Added

-   Added setting `removePIISentry` which defaults to `False`, when enabled we replace absolute paths with the last part
    of the path for every string we find. We also remove the userId or replace it with the sessionId which is simply an
    unique integer per session

## [0.5.0] - 2023-10-06
### Changed

- Added support for detecting OVI vs OVE vs OVC and configuring the telemetry system
  to use an open endpoint for OVE run environments.

## [0.4.0] - 2023-05-25

### Changed

-   Move DSN get setting into the extension startup

## [0.3.0] - 2023-05-24

### Changed

-   Send Kit version with the tag `app.kit_version`
-   Set the release using the app name + app version

## [0.2.0] - 2023-05-22

### Changed

-   Set DSN as a setting
