# Changelog

## [2.4.5] - 2025-05-01
### Changed
- Prepare for Python-3.12

## [2.4.4] - 2025-03-10
### Fixed
- OMPE-36842: Make error of access denied or path not found more clear to user.

## [2.4.3] - 2025-04-26
### Changed
- OMPE-39146: Remove hard code for "omniverse".

## [2.4.2] - 2025-04-22
### Fixed
- OMPE-41571: Fix mdl package path convert when contain special characters.

## [2.4.1] - 2025-04-14
### Fixed
- OMPE-40611: Match and replace texture paths in .mdl files in a less greedy way.

## [2.4.0] - 2025-02-28
### Fixed
- OMPE-38777: Fix path calculation for paths with spaces.

## [2.3.1] - 2024-12-20
### Changed
- OMPE-31903: Use omni.usd.make_valid_identifier instead of Tf.MakeValidIdentifier to support unicode characters.

## [2.3.0] - 2024-09-20
### Changed
- Fixes for Python-3.11
### Removed
- Export of wrap function

## [2.2.22] - 2024-09-20
### Changed
- OMPE-15324: Fix issue when collecting referenced assets with USD only modifies the original asset.

## [2.2.21] - 2024-04-01
### Added
- Add docs for omni.kit.usd.collect module.

## [2.2.20] - 2024-03-01
### Added
- Improve collect tool so that all absolute URLs are converted.

## [2.2.19] - 2024-02-27
### Added
- Don't remove non-default prims if layer has no default prim set.

## [2.2.18] - 2024-02-07
### Added
- Fix MDL collect issue about bsdf_measurements.
- Fix test of collect with cache.

## [2.2.17] - 2024-01-31
### Added
- Improve public APIs of collector.
- Improve collector to support caching history records to speed up re-collect.

## [2.2.16] - 2024-01-23
### Added
- Improve collector to support time based collection.

## [2.2.15] - 2024-01-19
### Added
- More support to convert usda to usdc format by considering underlying fileFormat of layer.

## [2.2.14] - 2024-01-12
### Added
- Fix collecting default prim only issue when root prims are over 2.

## [2.2.13] - 2024-01-08
### Added
- Fix collect issue if stage includes references from a different local drive.

## [2.2.12] - 2024-01-05
### Added
- Add option to support converting usda to usdc format for ascii USD files.

## [2.2.11] - 2024-01-03
### Added
- Improve collector's performance by speeding up regex match for resolving material dependencies.
- Add return value for collect() function for status check.
- Add support to specify option for collecting default prim only.

## [2.2.10] - 2023-12-19
### Added
- Improve collector to support collecting opended stage with anonymous root.
- Increase code coverage.

## [2.2.9] - 2023-08-22
### Added
- Fix collection issue when layer is opened in memory with new changes.

## [2.2.8] - 2023-08-16
### Added
- OM-102672: Support to collect texture in mtlx(MterialX) file.

## [2.2.7] - 2023-08-01
### Added
- OM-103573: Add default prim only options.

## [2.2.6] - 2023-07-28
### Changed
- Re-pathing locked states inside customLayerData.

## [2.2.5] - 2023-07-26
### Changed
- Fix collecting UDIM textures in MDL.

## [2.2.4] - 2023-07-12
### Changed
- Fix flat collection issue, which maps wrong paths for MDLs.

## [2.2.3] - 2023-06-09
### Changed
- Use sync save for layer instead of async one to avoid hang.

## [2.2.2] - 2023-05-24
### Changed
- Fix possible hang caused by calling pybind11 bindings from USD boost bindings in mutil-threads.

## [2.2.1] - 2023-05-09
### Changed
- Improve collect tool to report progress of collecting dependencies also.

## [2.2.0] - 2023-03-24
### Changed
- Extracted the core collector backend from omni.kit.tool.collect.  No functional changes.
