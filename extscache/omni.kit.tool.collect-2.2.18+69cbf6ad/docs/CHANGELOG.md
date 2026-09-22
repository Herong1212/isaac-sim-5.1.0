# Changelog

## [2.2.18] - 2025-04-26
### Changed
- OMPE-39146: Remove hard code for "omnverse".

## [2.2.17] - 2025-02-28
### Fixed
- OMPE-38777: Fix collect folder default with spaces in path.

## [2.2.16] - 2024-10-22
### Changed
- OMPE-22583: Update public API.

## [2.2.15] - 2024-08-13
### Changed
- OMPE-8922: Update icon of menu item in Content context menu

## [2.2.14] - 2024-06-19
### Changed
- OMPE-8340: Updated documentation.

## [2.2.13] - 2024-06-14
### Changed
- OMPE-8340: Updated documentation with AI agent for omni.kit.tool.collect.

## [2.2.12] - 2024-04-03
### Changed
- OM-122597: Always show full path in file select frame.

## [2.2.11] - 2024-03-20
### Added
- DHS-971: Add collect folder's file interface.

## [2.2.10] - 2024-02-27
### Added
- Fix UX issue that widgets layout is overflow out of the window.

## [2.2.9] - 2024-01-19
### Added
- Add option to convert usda to usdc during collection.

## [2.2.8] - 2024-01-04
### Added
- Add option to specify option for collecting default prim only.

## [2.2.7] - 2023-12-19
### Added
- Improve collect tool to support collect multiple files in content context menu.

## [2.2.6] - 2023-12-19
### Added
- Improve collect tool to support collecting opened stage with anonymous root.

## [2.2.5] - 2023-08-22
### Added
- Add context menu to support collecting checkpoints.

## [2.2.4] - 2023-08-22
### Added
- Fix "Collect As" under File menu and improve tests to cover it.

## [2.2.3] - 2023-08-01
### Added
- OM-103573: Add default prim only options.

## [2.2.2] - 2023-05-23
### Added
- OM-88159: Add new collect all interface to support collect multi files at once.

## [2.2.1] - 2023-05-09
### Changed
- Improve collect tool to report progress of collecting dependencies.

## [2.2.0] - 2023-03-24
### Changed
- Separate this UI from the core collector model which is moved to omni.kit.usd.collect.

## [2.1.27] - 2023-03-07
### Changed
- Update the way to locate file picker cancel button in ui collect test.

## [2.1.26] - 2023-02-07
### Changed
- Fix issue that references non-existed variable.

## [2.1.25] - 2023-02-03
### Changed
- Supports to define exclusion rules to skip collecting URLs with specific patterns.

## [2.1.24] - 2023-01-18
### Changed
- Fixed 2 tests to be able to be run in random order.

## [2.1.23] - 2022-11-07
### Changed
- Reduce size of test data.
- Improve UI.
- Make omni.kit.window.content_browser as optional.
- Fix MDL parser that cannot handle spaces in texture define.

## [2.1.22] - 2022-10-28
### Added
- Clean up dependencies and de-register menu item after extension is shutdown.

## [2.1.21] - 2022-10-14
### Added
- Better wording for selecting collect folder.

## [2.1.20] - 2022-10-09
### Added
- Add option to force all collected files to be writable.

## [2.1.19] - 2022-09-06
### Added
- Add texture grouping options for flat collection mode, textures can be grouped by MDL, USD or flat.

## [2.1.18] - 2022-09-05
### Changed
- Fix issue that won't hide progress bar.

## [2.1.17] - 2022-08-27
### Changed
- Move collect tool into Kit core.
- More improvement to perf.
- Hook collect tool to file menu.

## [2.1.16] - 2022-08-26
### Changed
- Fix file naming conflicts for flat collection.
- More improvement about logging and perf.

## [2.1.15] - 2022-08-23
### Changed
- More test coverage.

## [2.1.14] - 2022-08-18
### Changed
- Fix refactoring issues.

## [2.1.13] - 2022-08-12
### Changed
- Refactoring collect tool to improve perf.
- Fix tags collecting.

## [2.1.12] - 2022-07-28
### Changed
- Fix issues to collect read-only USD files.

## [2.1.11] - 2022-05-26
### Changed
- Workaround to solve usda collect issue by renaming extension to match its content format.

## [2.1.10] - 2022-05-20
### Added
- Fix collect issue that will miss tags for USD files.

## [2.1.9] - 2022-05-12
### Added
- add flag to elide copy if files that already in destination location.

## [2.1.8] - 2022-04-28
### Changed
- Revert maximum tasks to 8 to avoid influence interaction of UI.

## [2.1.7] - 2022-04-28
### Changed
- Add error options to customize error reporting.

## [2.1.6] - 2022-04-06
### Changed
- Match MDL resolve rule as new-MDL-Schema in USD.

## [2.1.5] - 2022-03-07
### Changed
- Fix missing changes from Kit release/103.1.

## [2.1.4] - 2022-03-07
### Changed
- Catch possible exceptions threw by UsdUtils.ExtractExternalReferences and UsdUtils.ModifyAssetPaths.

## [2.1.3] - 2022-02-21
### Changed
- Move collect tool to kit-tools repo.

## [2.1.2] - 2022-02-09
### Changed
- Fix an issue that UDIM textures are missing to be collected.

## [2.1.1] - 2022-01-12
### Changed
- Fix path decode issue for collecting projects from ov to ov.

## [2.1.0] - 2021-12-16
### Changed
- Fix path resolve that's with/without relative path prefix, like './' or '../'

## [2.0.8] - 2021-09-27
### Changed
- Fix texture collecting for cube/ptex textures
- Fix mdl module replace.

## [2.0.7] - 2021-09-16
### Changed
- Improve UX of file picker to show folder name for folder picker.

## [2.0.6] - 2021-09-10
### Fixes
- Improve flat collect to resolve material dependencies.

## [2.0.5] - 2021-09-09
### Added
- Add API to collect.

## [2.0.4] - 2021-08-25
### Fixes
- Fix UDIM textures collect.

## [2.0.3] - 2021-07-28
### Changed
- More tests.

## [2.0.2] - 2021-07-21
### Fixed
- Fix collection to assets from http source.

## [2.0.1] - 2021-02-06
### Changed
- Initialize change log.
- Remove old editor and content window dependencies.
