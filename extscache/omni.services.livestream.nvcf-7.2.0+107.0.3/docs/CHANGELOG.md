# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [7.2.0] - 2024-12-19
### Added
- New `/app/livestream/nvcf/quitOnSessionEnded` setting (defaults to true).
- New `/app/livestream/nvcf/sessionResumeTimeoutSeconds` setting (defaults to 0).
- New `/app/livestream/nvcf/waitForCustomReadyEvent` setting (defaults to false).
- New `omni.services.livestream.nvcf.session_ended` event that is sent when a streaming session ends (if `quitOnSessionEnded` is false).
- New `omni.services.livestream.nvcf.custom_ready` event that must be sent by the application when it is ready to be streamed
  (if `waitForCustomReadyEvent` is true), both at startup and after receiving an `omni.services.livestream.nvcf.session_ended` event.

### Removed
- The `/app/livestream/nvcf/allowSessionResume` setting.

## [7.1.1] - 2024-12-17
### Fixed
- Ensure the `/v1/streaming/endsession` endpoint returns a result before the app quits.

## [7.1.0] - 2024-11-26
### Added
- New `/v1/streaming/endsession` endpoint required for NVCF session resume.
- New `/app/livestream/nvcf/allowSessionResume` setting.

## [7.0.0] - 2024-11-14
### Changed
- Update to build with Kit 107.0

## [6.1.1] - 2024-10-25
### Fixed
- Bug where new private shared port field was not optional.

## [6.1.0] - 2024-10-23
### Added
- Support for setting private shared port received from streaming/creds endpoint.

### Changed
- Update to use a newer version of streamsdk (35031330.0_gs_04_69).

## [6.0.0] - 2024-09-25
### Changed
- Update to build with Kit 106.2

## [5.0.0] - 2024-09-24
### Changed
- Update to build with Kit 106.1

## [3.0.0] - 2024-07-16
### Added
- New `/v1/streaming/ready` endpoint

## [1.0.0] - 2024-05-16
### Changed
- Initial version.
