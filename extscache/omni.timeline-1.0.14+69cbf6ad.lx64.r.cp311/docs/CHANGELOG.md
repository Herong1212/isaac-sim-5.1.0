# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.14] - 2025-03-26
### Added
- Support for unique event Observer names with /app/events/qualifiedNames setting

## [1.0.13] - 2025-03-03
### Changed
- Allow resetting currentTime when setting startTime if timeline is not playing and currentTime < startTime.
- Allow resetting currentTime when setting endTime if timeline is not playing and currentTime > endTime.

## [1.0.12] - 2025-02-25
### Added
- Added correctly named `get_time_codes_per_second` python API.
### Changed
- Increased FPS_TOLERANCE_PERCENT for test.

## [1.0.11] - 2024-10-14
### Added
- Fix current time precision

## [1.0.10] - 2024-04-11
### Added
- Documentation

## [1.0.9] - 2023-06-12
### Added
- Zoom mode

## [1.0.8] - 2023-05-27
### Changed
- Bugfixes in director mode

## [1.0.7] - 2023-03-27
### Changed
- Added director timelines

## [1.0.6] - 2023-03-01
### Changed
- All state changes and corresponding callbacks are applied one frame later
- Timeline was made thread-safe
- Added support for multiple timeline instances
- Made fixed time stepping default
- Fixed time stepping tries to be in sync with clock time

## [1.0.5] - 2022-08-02
### Changed
- play from start time if current time is out of range

## [1.0.4] - 2022-06-29
### Changed
- changed play() to play(start, end, loop).

## [1.0.3] - 2022-06-20
### Added
- Add tentative time.

## [1.0.2] - 2021-04-09
### Added
- Move `app.player.play*` settings from toolbar to timeline extension.

## [1.0.1] - 2021-03-02
### Added
- Started tracking version and changelog. Added tests.
