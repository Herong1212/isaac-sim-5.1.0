# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [7.5.0] - 2025-02-05
### Changed
- Update to build with the latest Kit 107.0 and ABI=1

## [7.2.0] - 2025-01-21
### Changed
- Update to build with the latest Kit 107.0

## [7.1.0] - 2024-12-09
### Changed
- Update to build with the latest Kit 107.0

## [7.0.0] - 2024-11-14
### Changed
- Update to build with Kit 107.0

## [6.1.0] - 2024-10-23
### Added
- Support for setting private shared port received from streaming/creds endpoint.

### Changed
- Update to use a newer version of streamsdk (35031330.0_gs_04_69).

## [6.0.0] - 2024-09-25
### Changed
- Update to build with Kit 106.2

## [5.1.0] - 2024-09-24
### Changed
- Update to build with Kit 106.1

## [5.0.8] - 2024-05-20
### Added
- API to set STUN credentials.

## [5.0.7] - 2024-05-03
### Changed
- Allow viewport streams to be enabled/disabled dynamically, not just at startup.

## [5.0.6] - 2024-04-30
### Changed
- Remove dependency on `omni.kit.renderer.cuda_interop`.

## [5.0.5] - 2024-03-05
### Changed
- Fixed asyncCopy path to parallelize copies for multiple streams.

## [5.0.4] - 2024-03-05
### Changed
- Added support for overriding the timestamp with the frame number.

## [5.0.3] - 2024-02-29
### Added
- Support for audio streaming.

## [5.0.2] - 2024-02-26
### Added
- Ability to stream aovs other than ldr color ones.

### Changed
- Default value of the new /app/livestream/asyncCopy setting to true.

## [5.0.1] - 2024-02-12
### Added
- New /app/livestream/asyncCopy setting to copy render products asynchronously.

## [5.0.0] - 2024-02-12
### Changed
- Updated to build with Kit 107.0

## [4.2.1] - 2024-02-08
### Changed
- Change to support encoding a viewport stream on the same device as it is rendered.

## [4.2.0] - 2024-02-08
### Changed
- Update to use a newer version of streamsdk (33859876.0_gs_04_63).

## [4.1.2] - 2024-02-06
### Added
- Option to stream multiple viewports over separate connections.

## [4.1.1] - 2024-01-31
### Fixed
- Extension load order issue.

## [4.1.0] - 2024-01-25
### Added
- Option to stream just the viewport instead of the whole app.

## [4.0.0] - 2024-01-02
### Changed
- Updated to build with Kit 106.0

## [3.2.0] - 2023-09-28
### Changed
- Remove some unused settings and dependencies.
- Updated to build with the latest repo_* packages.

## [3.1.0] - 2023-09-18
### Changed
- Updated to build with a newer version of Kit 105.2

## [3.0.0] - 2023-07-25
### Changed
- Updated to build with Kit 105.2

## [2.2.0] - 2023-07-24
### Changed
- Updated to build with a newer version of Kit 105.1

## [2.1.0] - 2023-07-03
### Changed
- Updated to build with a newer version of Kit 105.1

## [2.0.2] - 2023-05-23
### Changed
- Exposed qosStatusCallback to Python.

## [2.0.1] - 2023-05-15
### Changed
- Pull in some changes that were made to the original extensions that are still present in kit.

## [2.0.0] - 2023-05-12
### Changed
- Updated to build with Kit 105.1

## [1.0.1] - 2023-05-11
### Fixed
- OM-93598: Judder when livestreaming Composer 2023.1

## [1.0.0] - 2023-05-05
### Added
- Moved from kit into kit-livestream
