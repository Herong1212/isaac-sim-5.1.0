# Changelog

## [1.3.1]
### Changed
- Update to support Arm

## [1.3.0]
### Changed
- Upgrade Kit SDK to 107

## [1.2.0]
### Changed
- Upgrade Kit SDK to 106.4

## [1.1.14]
### Changed
- Remove AnimationSchemaTools deprecation warning.

## [1.1.13]
### Changed
- Add support level to package.

## [1.1.12]
### Changed
- Reformat all source with repo format.

## [1.1.11]
### Added
- Added omni.usd.schema.anim to dependencies.

## [1.1.10]
### Added
- Added more unit tests
### Changed
- Ignored some unused code from the test coverage

## [1.1.9]
### Added
- Add more unit tests

## [1.1.8]
### Fixed
- [OM-119133] Curve simplification results in the appearance of new curves that are empty
- [OM-119135] Simplifying prims without translate, rotate, and scale attributes lead to errors
- [OM-119134] USD timesample to curve conversion doesn’t work on xformOp:transform

## [1.1.7]
### Fixed
- [OMPRW-638]Fixed a bug that sometimes graph nodes can't be deleted.

## [1.1.6]
### Changed
- Disable the threadSafe flag to avoid the crashes

## [1.1.5]
### Changed
- Updated kit-sdk version

## [1.1.4] - 2023-11-27
### Changed
- Updated kit-sdk version

## [1.1.3] - 2023-09-21
### Fixed
- Fixed OM-107210 that context menu entries are enabled for attributes that are not supported.

## [1.1.2] - 2023-09-12
### Fixed
- Fixed the bug that a curve is not deleted when the last key is deleted.

## [1.1.1] - 2023-09-06
### Changed
- Added a setting to control whether a curve is deleted when the last key is deleted.

## [1.1.0] - 2023-09-01
### Changed
- Use new curve node type name.

## [1.0.1] - 2023-08-30
### Changed
- Removed "clear_dense_data" option from the conversion command.

## [1.0.0] - 2023-08-24
### Changed
- Renamed from omni.anim.curve to omn.anim.curve.core.
