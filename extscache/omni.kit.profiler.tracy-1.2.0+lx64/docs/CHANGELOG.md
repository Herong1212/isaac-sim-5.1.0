# CHANGELOG

This project adheres to `Semantic Versioning <https://semver.org/>`_.

## [1.2.0] - 2024-11-01

- Remove Kit target version lock, so that teams on 106.1+ can use this extension too. If you are on older Kit that is using older Carbonite+Tracy stay on 1.1.6.

## [1.1.7] - 2024-10-16

- Updated to Tracy 0.11.1

## [1.1.6] - 2024-09-10

- Tracy automatic upload to S3

## [1.1.5] - 2024-07-24

- Add automatic Tracy capture controlled via settings

## [1.1.4] - 2023-06-21

- OM-98765: Use build of Tracy that will run on AMD CPUs

## [1.1.3] - 2023-05-15

- Update to newer tracy_bin which uses newer MSVC libs

## [1.1.2] - 2023-05-11

### Changed

- OM-93598: Don't load `carb.profiler-tracy.plugin` until right before we start profiling with tracy.

## [1.1.1] - 2023-05-01

### Changed

- Build against Kit 105.0 instead of 105.1

## [1.1.0] - 2023-04-21

### Added

- Ability to launch Tracy and have it immediately connect to the running Kit process.

### Changed

- Updated Tracy to 0.9.1

## [1.0.5] - 2023-02-20

### Changed

- Fixed extension init on Python 3.10

## [1.0.4] - 2022-09-02

### Changed

- Updated Tracy to 0.8.2

## [1.0.2] - 2022-03-29

### Changed

- trying some other things to see if we can get import-chrome to work on Linux

## [1.0.1] - 2022-03-28

### Added

- Updated popen call so import-chrome works on Linux

## [1.0.0] - 2021-07-02

### Added

- Initial release.
