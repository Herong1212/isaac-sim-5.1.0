# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.1.0] - 2025-05-01
### Fixed
- Fixed non-functional and missing raycast sequence and sequence array APIs.

## [1.0.6] - 2025-04-07
### Changed
- Updated to use omni.usd via eventdispatcher (Events 2.0) instead of EventStream (Events 1.0)

## [1.0.5] - 2024-04-19
### Changed
- OM-122326: Update docs.

## [1.0.4] - 2024-03-26
### Changed
- Delayed loading of `rtx::raytracing::RaycastQuery` plugin.

## [1.0.3] - 2023-12-04
### Added
- Added utility to raycast from mouse ndc coords.

## [1.0.2] - 2023-11-17
### Added
- Added option to make Ray aware of section plane.

## [1.0.1] - 2023-11-06
### Changed
- Changed `omni.hydra.rtx` to optional dependency so rtx is not forced everywhere. However keep in mind the extension will not be able to return valid raycast result if rtx is missing.

## [1.0.0] - 2023-10-02
### Added
- Initial release.
